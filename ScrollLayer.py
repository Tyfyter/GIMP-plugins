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

#sys.stderr = open('GIMPerr.txt', 'a')
#sys.stdout = open('GIMPlog.txt', 'a')

def scroll_up(image, drawable) :
	
	layerCount = len(image.layers)#pdb.gimp_image_get_layers(image)[1]
	current = image.layers.index(image.active_layer)
	target = (layerCount + current - 1) % layerCount
	
	image.active_layer = image.layers[target]
	
	try:
		for i in range(layerCount) :
			image.layers[i].visible = (i == target)

	except Exception as err:
		exc_type, exc_obj, tb = sys.exc_info()
		line = tb.tb_lineno
		gimp.message("Unexpected error: " + str(err) + " at line " + str(line))
	

def scroll_down(image, drawable) :
	
	layerCount = len(image.layers)#pdb.gimp_image_get_layers(image)[1]
	current = image.layers.index(image.active_layer)
	target = (layerCount + current + 1) % layerCount
	
	image.active_layer = image.layers[target]
	
	try:
		for i in range(layerCount) :
			image.layers[i].visible = (i == target)

	except Exception as err:
		exc_type, exc_obj, tb = sys.exc_info()
		line = tb.tb_lineno
		gimp.message("Unexpected error: " + str(err) + " at line " + str(line))
	

try:
	register(
		"layer_scroll_up",
		"Scroll Up",
		"",
		"",
		"",
		"",
		"<Toolbox>/Xtns/Select Last Layer",
		"RGB, RGB*",
		[
		(PF_IMAGE, "img", "Input Image", None),
		(PF_DRAWABLE, "drawable", "Input Layer", None)
		],
		[],
		scroll_up)
	register(
		"layer_scroll_down",
		"Scroll Down",
		"",
		"",
		"",
		"",
		"<Toolbox>/Xtns/Select Next Layer",
		"RGB, RGB*",
		[
		(PF_IMAGE, "img", "Input Image", None),
		(PF_DRAWABLE, "drawable", "Input Layer", None)
		],
		[],
		scroll_down)
except Exception as err:
	exc_type, exc_obj, tb = sys.exc_info()
	line = tb.tb_lineno
	gimp.message("Unexpected error: " + str(err) + " at line " + str(line))

main()
