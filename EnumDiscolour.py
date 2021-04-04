import math
import sys
from gimpfu import *
#from math import *
false = False
true = True
context = {}

def enum_discolor(image, drawable, expression, alpha, unitcoords, unit) :
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
	pdb.gimp_image_insert_layer(image, layer, None, pdb.gimp_image_get_item_position(image,drawable))
	pdb.gimp_drawable_edit_clear(layer)
	newColor = (255,255,255,0)
	# Iterate over all the pixels
	try:
		for x in range(layer.width):
			gimp.progress_update(float(x) / float(layer.width))

			for y in range(layer.height):
				# Get the pixel and verify that is an RGB value.
				pixel = drawable.get_pixel(x,y)
			
				if(len(pixel) >= 3):
					xyz = rgb_to_xyz(pixel)
					LAB = xyz_to_lab(xyz)
					LCh = lab_to_lch(LAB)
					rgbdiv = (1.0,255.0)[unit]
					percdiv = (1.0,100.0)[unit]
					anglediv = (1.0,360.0)[unit]
					xdiv = (1.0,layer.width*1.0)[unitcoords]
					ydiv = (1.0,layer.height*1.0)[unitcoords]
					global context
					context = {'x': x/xdiv, 'y': y/ydiv, 'r': pixel[0]/rgbdiv, 'g': pixel[1]/rgbdiv, 'b': pixel[2]/rgbdiv, 'a': pixel[3]/rgbdiv, 'X': xyz[0]/percdiv, 'Y': xyz[1]/percdiv, 'Z': xyz[2]/percdiv , 'L': LAB[0]/percdiv, 'A': LAB[1], 'B': LAB[2], 'C': LCh[1]/percdiv, 'h': LCh[2]/anglediv, 'width': layer.width, 'height': layer.height}
					if(alpha):
						newColor = clamp_rgb(eval(expression, None, context), unit)
						layer.set_pixel(x,y, truncate_float4(newColor))
					else:
						newColor = clamp_rgb(eval(expression, None, context), unit) + pixel[3:]
						layer.set_pixel(x,y, truncate_float4(newColor))
		
		# Update the layer.
		layer.update(0, 0, layer.width, layer.height)
		# pdb.gimp_image_insert_layer(image, layer, None, pdb.gimp_image_get_item_position(image,drawable))
		# pdb.gimp_drawable_edit_clear(drawable)
		# pdb.gimp_image_merge_down(image, layer, 0)

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
	
def clamp_rgb(rgba, unit) :
	if(len(rgba) > 3) :
		return (clamp_rgb1(rgba[0],unit),clamp_rgb1(rgba[1],unit),clamp_rgb1(rgba[2],unit),clamp_rgb1(rgba[3],unit))
	return (clamp_rgb1(rgba[0],unit),clamp_rgb1(rgba[1],unit),clamp_rgb1(rgba[2],unit))
	
def clamp_rgb1(v, unit) :
	return clamp(v*((1,255)[unit]),0,255)

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

def stern(condition, a, b):
	if(condition) :
		return eval(str(a), None, context)
	return eval(str(b), None, context)

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
	(PF_BOOL, "alpha", "Include alpha", false),
	(PF_BOOL, "unitcoords", "Unit range coords", false),
	(PF_BOOL, "unit", "Unit range values", false)
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
	(PF_BOOL, "alpha", "Include alpha", false),
	(PF_BOOL, "unitcoords", "Unit range coords", false),
	(PF_BOOL, "unit", "Unit range values", false)
	],
	[],
	enum_discolor)

main()
