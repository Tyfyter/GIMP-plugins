import math
import sys
from gimpfu import *
#from math import *
false = False
true = True
context = {}

def graphing_calc(image, expression, step, unitcoords, unit) :
	'''
	Parameters:
	image : image The current image.
	'''
	# Indicates that the process has started.
	gimp.progress_init("Pathing " + expression + "...")
	

	# Set up an undo group, so the operation will be undone in one step.
	pdb.gimp_image_undo_group_start(image)
	
	pdb.gimp_drawable_edit_clear(layer)
	# Iterate over all the pixels
	try:
		path = pdb.gimp_vectors_new(image, expression)
		pdb.gimp_image_add_vectors(image, path, 0)
		xrange = layer.width/step
		for ux in range(xrange):
			x = ux * step
			gimp.progress_update(float(x) / float(layer.width))
			
					xdiv = (1.0,layer.width*1.0)[unitcoords]
					ydiv = (1.0,layer.height*1.0)[unitcoords]
					global context
					context = {'x': x/xdiv}
					pdb.gimp_vectors_bezier_stroke_lineto(path, ux, x, eval(expression, None, context) * ydiv)
		
		# Update the layer.
		# layer.update(0, 0, layer.width, layer.height)
		# pdb.gimp_image_insert_layer(image, layer, None, pdb.gimp_image_get_item_position(image,drawable))
		# pdb.gimp_drawable_edit_clear(drawable)
		# pdb.gimp_image_merge_down(image, layer, 0)

	except Exception as err:
		exc_type, exc_obj, tb = sys.exc_info()
		line = tb.tb_lineno
		gimp.message("Unexpected error: " + str(err) + " at line " + str(line))
	
	# Close the undo group.
	pdb.gimp_image_undo_group_end(image)
	
	# End progress.
	pdb.gimp_progress_end()

register(
	"graphing_calc",
	"graphing calc",
	"",
	"",
	"",
	"",
	"<Toolbox>/Xtns/graphing calc",
	"RGB, RGB*",
	[
	(PF_IMAGE, "img", "Input Image", None),
	(PF_DRAWABLE, "drawable", "Input Layer", None),
	(PF_STRING, "expression", "Expression", ""),
	(PF_FLOAT, "step", "Step size", 1),
	(PF_BOOL, "unitcoords", "Unit range coords", false)
	],
	[],
	graphing_calc)

main()
