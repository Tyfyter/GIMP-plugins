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

def channel_merge(image, drawable, r, g, b) :
	''' Converts a layer to gray scale, without modifying his type (RGB or RGBA).
	Note that this implementation is very inefficient, since it do not make use 
	of tiles or pixel regions. Also, it has a bug which prevents to undo the 
	changes made by this function.
	
	Parameters:
	image : image The current image.
	'''
	# Indicates that the process has started.
	

	# Set up an undo group, so the operation will be undone in one step.
	pdb.gimp_image_undo_group_start(image)
	
	red = pdb.gimp_image_get_layer_by_tattoo(image, r)
	green = pdb.gimp_image_get_layer_by_tattoo(image, g)
	blue = pdb.gimp_image_get_layer_by_tattoo(image, b)
	
	gimp.progress_init("Merging " + red.name + ", " + green.name + ", and " + blue.name + "...")
	
	layer = pdb.gimp_layer_copy(red, false)
	
	newColor = (255,255,255,0)
	
	# Iterate over all the pixels and convert them to gray.
	try:
		for x in range(layer.width):
			# Update the progress bar.
			gimp.progress_update(float(x) / float(layer.width))

			for y in range(layer.height):
				newColor = (red.get_pixel(x,y)[0], green.get_pixel(x,y)[1], blue.get_pixel(x,y)[2], max(red.get_pixel(x,y)[3], green.get_pixel(x,y)[3], blue.get_pixel(x,y)[3]))
				layer.set_pixel(x,y,newColor)
		
		# Update the layer.
		layer.update(0, 0, layer.width, layer.height)
		pdb.gimp_image_insert_layer(image, layer, None, 0)

	except Exception as err:
		exc_type, exc_obj, tb = sys.exc_info()
		line = tb.tb_lineno
		gimp.message("Unexpected error: " + str(err) + " at line " + str(line) + ", last color: " + str(newColor))
	
	# Close the undo group.
	pdb.gimp_image_undo_group_end(image)
	
	# End progress.
	pdb.gimp_progress_end()

def mark_layer(image, drawable, index) :
	pdb.gimp_drawable_set_tattoo(drawable, index)

register(
	"mark_layer",
	"Mark Layer",
	"",
	"",
	"",
	"",
	"<Toolbox>/Xtns/Mark Layer",
	"RGB, RGB*",
	[
	(PF_IMAGE, "img", "RGB Merge", None),
	(PF_DRAWABLE, "drawable", "Input Layer", None),
	(PF_INT, "index", "Index", 0),
	],
	[],
	mark_layer)

register(
	"channel_merge",
	"Channel Merge",
	"",
	"",
	"",
	"",
	"<Toolbox>/Xtns/Channel Merge",
	"RGB, RGB*",
	[
	(PF_IMAGE, "img", "RGB Merge", None),
	(PF_DRAWABLE, "drawable", "Input Layer", None),
	(PF_INT, "r", "Red", 1),
	(PF_INT, "g", "Blue", 2),
	(PF_INT, "b", "Green", 3),
	],
	[],
	channel_merge)

main()
