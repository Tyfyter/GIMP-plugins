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

sys.stderr = open('GIMPerr.txt', 'a')
sys.stdout = open('GIMPlog.txt', 'a')

def slice(image, drawable, count) :
	# Indicates that the process has started.
	

	# Set up an undo group, so the operation will be undone in one step.
	pdb.gimp_image_undo_group_start(image)
	
	gimp.progress_init("Slicing")
	
	height = image.height/count

	layers = []
	
	# Iterate over all the pixels and convert them to gray.
	try:
		for i in range(count) :
			layers = layers + [pdb.gimp_layer_copy(drawable, false)]
			pdb.gimp_image_insert_layer(image, layers[i], None, 0)
			pdb.gimp_drawable_offset(layers[i], true, 2, 1, 1)
			pdb.gimp_drawable_offset(layers[i], true, 2, -1, (height*-i)-1)
			layers[i].update(0, 0, layers[i].width, layers[i].height)
		pdb.gimp_image_remove_layer(image, drawable)
		pdb.gimp_crop(image, image.width, height, 0, 0)

	except Exception as err:
		exc_type, exc_obj, tb = sys.exc_info()
		line = tb.tb_lineno
		gimp.message("Unexpected error: " + str(err) + " at line " + str(line))
	
	# Close the undo group.
	pdb.gimp_image_undo_group_end(image)
	
	# End progress.
	pdb.gimp_progress_end()


try:
	register(
		"slice",
		"Slice",
		"",
		"",
		"",
		"",
		"<Toolbox>/Xtns/Slice",
		"RGB, RGB*",
		[
		(PF_IMAGE, "img", "Input Image", None),
		(PF_DRAWABLE, "drawable", "Input Layer", None),
		(PF_INT, "count", "Count", 2),
		],
		[],
		slice)
except Exception as err:
	exc_type, exc_obj, tb = sys.exc_info()
	line = tb.tb_lineno
	gimp.message("Unexpected error: " + str(err) + " at line " + str(line))

main()
