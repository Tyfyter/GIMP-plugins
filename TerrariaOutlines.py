import sys
from gimpfu import *
#from math import *

def get_alpha(drawable, x, y) :
	if (x < 0 or y < 0 or x > drawable.width or y > drawable.height) :
		return 0
	return drawable.get_pixel(x, y)[3]

def outlines(image, drawable) :
	# Set up an undo group, so the operation will be undone in one step.
	pdb.gimp_image_undo_group_start(image)
	
	gimp.progress_init("Outlining")

	layer = pdb.gimp_layer_copy(drawable, False)
	pdb.gimp_image_insert_layer(image, layer, None, pdb.gimp_image_get_item_position(image,drawable))
	pdb.gimp_drawable_edit_clear(layer)
	
	# Iterate over all the pixels and convert them to gray.
	for x in range(layer.width) :
		for y in range(layer.height) :
			if (get_alpha(drawable, x, y) > 0) :
				c = (get_alpha(drawable, x - 2, y) + get_alpha(drawable, x + 2, y) + get_alpha(drawable, x, y - 2) + get_alpha(drawable, x, y + 2)) / 255
				if (c < 4) :
					layer.set_pixel(x, y, (255, 255, 255, 255))

	
	# Close the undo group.
	pdb.gimp_image_undo_group_end(image)
	
	# End progress.
	pdb.gimp_progress_end()
	layer.update(0, 0, layer.width, layer.height)


# outlinesLog = open(r"%APPDATA%\GIMP\2.10\plug-ins\log.txt", "w+")
# outlinesLog.write("Loading outlines plugin")
#print("Loading outlines plugin")
register(
	"terraria_outlines",
	"Terraria Outlines",
	"",
	"",
	"",
	"",
	"<Toolbox>/Xtns/Terraria Outlines",
	"RGB, RGB*",
	[
	(PF_IMAGE, "img", "RGB Merge", None),
	(PF_DRAWABLE, "drawable", "Input Layer", None),
	],
	[],
	outlines)

# outlinesLog.close()
main()
