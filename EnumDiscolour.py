#!/usr/bin/env python
#
# -------------------------------------------------------------------------------------
#
# Copyright (c) 2013, Jose F. Maldonado
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, 
# are permitted provided that the following conditions are met:
#
#	- Redistributions of source code must retain the above copyright notice, this 
#	list of conditions and the following disclaimer.
#	- Redistributions in binary form must reproduce the above copyright notice, 
#	this list of conditions and the following disclaimer in the documentation and/or 
#	other materials provided with the distribution.
#	- Neither the name of the author nor the names of its contributors may be used 
#	to endorse or promote products derived from this software without specific prior 
#	written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY 
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES 
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT 
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, 
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR 
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN 
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH 
# DAMAGE.
#
# -------------------------------------------------------------------------------------
#
# This file is a basic example of a Python plug-in for GIMP.
#
# It can be executed by selecting the menu option: 'Filters/Test/Discolour layer v1'
# or by writing the following lines in the Python console (that can be opened with the
# menu option 'Filters/Python-Fu/Console'):
# >>> image = gimp.image_list()[0]
# >>> layer = image.layers[0]
# >>> gimp.pdb.python_fu_test_discolour_layer_v1(image, layer)

import math
import sys
from gimpfu import *
#from math import *
false = False
true = True

def enum_discolor(image, drawable, expression, alpha) :
	''' Converts a layer to gray scale, without modifying his type (RGB or RGBA).
	Note that this implementation is very inefficient, since it do not make use 
	of tiles or pixel regions. Also, it has a bug which prevents to undo the 
	changes made by this function.
	
	Parameters:
	image : image The current image.
	drawable : layer The layer of the image that is selected.
	'''
	# Indicates that the process has started.
	gimp.progress_init("Discolouring " + drawable.name + "...")
	

	# Set up an undo group, so the operation will be undone in one step.
	pdb.gimp_image_undo_group_start(image)
	
	layer = pdb.gimp_layer_copy(drawable, false)
	
	newColor = (255,255,255,0)
	# Iterate over all the pixels and convert them to gray.
	try:
		for x in range(layer.width):
			# Update the progress bar.
			gimp.progress_update(float(x) / float(layer.width))

			for y in range(layer.height):
				# Get the pixel and verify that is an RGB value.
				pixel = layer.get_pixel(x,y)
			
				if(len(pixel) >= 3):
					xyz = rgb_to_xyz(pixel)
					LAB = xyz_to_lab(xyz)
					LCh = lab_to_lch(LAB)
					context = {'x': x, 'y': y, 'r': pixel[0], 'g': pixel[1], 'b': pixel[2], 'a': pixel[3], 'X': xyz[0], 'Y': xyz[1], 'Z': xyz[2] , 'L': LAB[0], 'A': LAB[1], 'B': LAB[2], 'C': LCh[1], 'h': LCh[2], 'width': layer.width, 'height': layer.height}
					if(alpha):
						newColor = eval(expression, None, context)
						layer.set_pixel(x,y, truncate_float4(newColor))
					else:
						newColor = eval(expression, None, context) + pixel[3:]
						layer.set_pixel(x,y, truncate_float4(newColor))
		
		# Update the layer.
		layer.update(0, 0, layer.width, layer.height)
		pdb.gimp_image_insert_layer(image, layer, None, pdb.gimp_image_get_item_position(image,drawable))
		pdb.gimp_drawable_edit_clear(drawable)
		pdb.gimp_image_merge_down(image, layer, 0)

	except Exception as err:
		exc_type, exc_obj, tb = sys.exc_info()
		line = tb.tb_lineno
		gimp.message("Unexpected error: " + str(err) + " at line " + str(line) + ", last color: " + str(newColor))
	
	# Close the undo group.
	pdb.gimp_image_undo_group_end(image)
	
	# End progress.
	pdb.gimp_progress_end()

def rgb_to_xyz(rgb) :
	var_R = ( rgb[0] / 255.0 )
	var_G = ( rgb[1] / 255.0 )
	var_B = ( rgb[2] / 255.0 )
    
	if ( var_R > 0.04045 ):
		var_R = ( ( var_R + 0.055 ) / 1.055 ) ** 2.4
	else:
		var_R = var_R / 12.92
	if ( var_G > 0.04045 ):
		var_G = ( ( var_G + 0.055 ) / 1.055 ) ** 2.4
	else:
		var_G = var_G / 12.92
	if ( var_B > 0.04045 ):
		var_B = ( ( var_B + 0.055 ) / 1.055 ) ** 2.4
	else:
		var_B = var_B / 12.92

	var_R = var_R * 100.0
	var_G = var_G * 100.0
	var_B = var_B * 100.0

	X = var_R * 0.4124 + var_G * 0.3576 + var_B * 0.1805
	Y = var_R * 0.2126 + var_G * 0.7152 + var_B * 0.0722
	Z = var_R * 0.0193 + var_G * 0.1192 + var_B * 0.9505
    
	return (X,Y,Z)

def xyz_to_rgb(xyz) :
	var_X = xyz[0] / 100.0
	var_Y = xyz[1] / 100.0
	var_Z = xyz[2] / 100.0

	var_R = var_X *  3.2406 + var_Y * -1.5372 + var_Z * -0.4986
	var_G = var_X * -0.9689 + var_Y *  1.8758 + var_Z *  0.0415
	var_B = var_X *  0.0557 + var_Y * -0.2040 + var_Z *  1.0570

	if ( var_R > 0.0031308 ):
		var_R = 1.055 * ( var_R ** ( 1 / 2.4 ) ) - 0.055
	else:
		var_R = 12.92 * var_R
	if ( var_G > 0.0031308 ):
		var_G = 1.055 * ( var_G ** ( 1 / 2.4 ) ) - 0.055
	else:
		var_G = 12.92 * var_G
	if ( var_B > 0.0031308 ):
		var_B = 1.055 * ( var_B ** ( 1 / 2.4 ) ) - 0.055
	else:
		var_B = 12.92 * var_B

	sR = var_R * 255.0
	sG = var_G * 255.0
	sB = var_B * 255.0
	return (sR,sG,sB)

def xyz_to_lab(xyz) :
	var_X = xyz[0] / 100.0
	var_Y = xyz[1] / 100.0
	var_Z = xyz[2] / 100.0

	if ( var_X > 0.008856 ):
		var_X = var_X ** ( 1/3.0 )
	else:
		var_X = ( 7.787 * var_X ) + ( 16 / 116.0 )
	if ( var_Y > 0.008856 ):
		var_Y = var_Y ** ( 1/3.0 )
	else:
		var_Y = ( 7.787 * var_Y ) + ( 16 / 116.0 )
	if ( var_Z > 0.008856 ):
		var_Z = var_Z ** ( 1/3.0 )
	else:
		var_Z = ( 7.787 * var_Z ) + ( 16 / 116.0 )

	CIE_L = ( 116.0 * var_Y ) - 16
	CIE_a = 500.0 * ( var_X - var_Y )
	CIE_b = 200.0 * ( var_Y - var_Z )
	return (CIE_L,CIE_a,CIE_b)

def lab_to_xyz(lab) :
	var_Y = ( lab[0] + 16 ) / 116
	var_X = lab[1] / 500 + var_Y
	var_Z = var_Y - lab[2] / 200

	if ( var_Y**3  > 0.008856 ):
		var_Y = var_Y**3
	else:
		var_Y = ( var_Y - 16 / 116.0 ) / 7.787
	if ( var_X**3  > 0.008856 ):
		var_X = var_X**3
	else:
		var_X = ( var_X - 16 / 116.0 ) / 7.787
	if ( var_Z**3  > 0.008856 ):
		var_Z = var_Z**3
	else:
		var_Z = ( var_Z - 16 / 116.0 ) / 7.787

	X = var_X * 100.0
	Y = var_Y * 100.0
	Z = var_Z * 100.0
	return (X,Y,Z)
	
def lab_to_lch(lab) :
	var_H = math.atan2( lab[2], lab[1] )

	if ( var_H > 0 ):
		var_H = ( var_H / math.pi ) * 180
	else:
		var_H = 360 - ( abs( var_H ) / math.pi ) * 180

	CIE_C = math.sqrt( lab[1] ** 2 + lab[2] ** 2 )
	return (lab[0],CIE_C,var_H)

def lch_to_lab(lch) :
	CIE_a = math.cos( lch[2] * 0.0174533) * lch[1]
	CIE_b = math.sin( lch[2] * 0.0174533 ) * lch[1]
	return (lch[0],CIE_a,CIE_b)

def lab_to_rgb(lab) :
	return xyz_to_rgb(lab_to_xyz(lab))
	
def rgb_to_lab(rgb) :
	return xyz_to_lab(rgb_to_xyz(rgb))

def lch_to_rgb(lch) :
	return lab_to_rgb(lch_to_lab(lch))
	
def rgb_to_lch(rgb) :
	return lab_to_lch(rgb_to_lab(rgb))

def truncate_float4(rgba) :
	if(len(rgba) > 3) :
		return (int(rgba[0]),int(rgba[1]),int(rgba[2]),int(rgba[3]))
	return (int(rgba[0]),int(rgba[1]),int(rgba[2]))
	
def clamp_rgb(rgba) :
	if(len(rgba) > 3) :
		return (clamp_rgb1(rgba[0]),clamp_rgb1(rgba[1]),clamp_rgb1(rgba[2]),clamp_rgb1(rgba[3]))
	return (clamp_rgb1(rgba[0]),clamp_rgb1(rgba[1]),clamp_rgb1(rgba[2]))
	
def clamp_rgb1(v) :
	return clamp(v,0,255)

def clamp(v,_min,_max) :
	return max(_min,min(v,_max)) 

def abs(v):
	if(v < 0) :
		return -v
	return v
	
def tern(condition, a, b):
	if(condition) :
		return a
	return b

register(
	"enum-discolor",
	"Enum Discolor",
	"",
	"",
	"",
	"",
	"<Toolbox>/Colors/Enum Discolor",
	"RGB, RGB*",
	[
	(PF_IMAGE, "img", "Input Image", None),
	(PF_DRAWABLE, "drawable", "Input Layer", None),
	(PF_STRING, "expression", "Expression", ""),
	(PF_BOOL, "alpha", "Include alpha", false)
	],
	[],
	enum_discolor)
	
register(
	"enum-discolor",
	"Enum Discolor",
	"",
	"",
	"",
	"",
	"<Toolbox>/Xtns/Enum Discolor",
	"RGB, RGB*",
	[
	(PF_IMAGE, "img", "Input Image", None),
	(PF_DRAWABLE, "drawable", "Input Layer", None),
	(PF_STRING, "expression", "Expression", ""),
	(PF_BOOL, "alpha", "Include alpha", false)
	],
	[],
	enum_discolor)

main()
