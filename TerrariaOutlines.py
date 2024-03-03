import sys
from gimpfu import *
#from math import *

def get_alpha(drawable, x, y) :
	if (x < 0 or y < 0 or x >= drawable.width or y >= drawable.height) :
		return 0
	return drawable.get_pixel(x, y)[3] / 255
def get_outness(value, frames, size, offset) : 
	frame_coord = (value - offset) % (size + 2);
	if (frame_coord >= size) :
		if (((value - frame_coord + size + 2) / (size + 2)) % frames == 0) :
			return 2
		return 1
	return 0
def get_surrounding_alpha(drawable, x, y, frames_x, frames_y, size_x, size_y, offset_x, offset_y) :
	x *= 2
	y *= 2
	value = 0
	value += get_alpha(drawable, x + (4 if get_outness(x + 2, frames_x, size_x, offset_x) == 1 else 2), y)
	value += get_alpha(drawable, x - (4 if get_outness(x - 2, frames_x, size_x, offset_x) == 1 else 2), y)
	value += get_alpha(drawable, x, y + (4 if get_outness(y + 2, frames_y, size_y, offset_y) == 1 else 2))
	value += get_alpha(drawable, x, y - (4 if get_outness(y - 2, frames_y, size_y, offset_y) == 1 else 2))
	return value

def outlines(image, drawable, frames_x, frames_y, size_x, size_y, offset_x, offset_y) :
	# Set up an undo group, so the operation will be undone in one step.
	pdb.gimp_image_undo_group_start(image)
	
	gimp.progress_init("Outlining")

	layer = pdb.gimp_layer_copy(drawable, False)
	pdb.gimp_image_insert_layer(image, layer, None, pdb.gimp_image_get_item_position(image,drawable))
	pdb.gimp_drawable_edit_clear(layer)
	
	# Iterate over all the pixels and convert them to gray.
	for x in range(layer.width / 2) :
		if (get_outness(x * 2, frames_x, size_x, offset_x)) :
			continue
		for y in range(layer.height / 2) :
			if (get_outness(y * 2, frames_y, size_y, offset_y)) :
				continue
			if (get_alpha(drawable, x * 2, y * 2) > 0) :
				if (get_surrounding_alpha(drawable, x, y, frames_x, frames_y, size_x, size_y, offset_x, offset_y) < 4) :
					layer.set_pixel(x * 2, y * 2, (255, 255, 255, 255))
					layer.set_pixel(x * 2 + 1, y * 2, (255, 255, 255, 255))
					layer.set_pixel(x * 2, y * 2 + 1, (255, 255, 255, 255))
					layer.set_pixel(x * 2 + 1, y * 2 + 1, (255, 255, 255, 255))

	#for x in range(layer.width) :
	#	for y in range(layer.height) :
	#			layer.set_pixel(x, y, (get_outness(x, frames_x, size_x, offset_x) * 127, get_outness(y, frames_y, size_y, offset_y) * 127, 0, 255))
	
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
	(PF_INT, "frames_x", "Style width", 0),
	(PF_INT, "frames_y", "Style height", 0),
	(PF_INT, "size_x", "Frame size x", 16),
	(PF_INT, "size_y", "Frame size y", 16),
	(PF_INT, "offset_x", "Frame offset x", 0),
	(PF_INT, "offset_y", "Frame offset y", 0),
	],
	[],
	outlines)

# outlinesLog.close()
main()
