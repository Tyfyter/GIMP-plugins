#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Fill selection with average color from same

# (c) Ofnuts 2017
#
#   History:
#
#   v0.0: 2017-01-09: Initial version
#   v0.1: 2016-10-30: Sharpen selection before use
#   v0.2: 2016-10-31: Replace color-to-alpha with bucket-fill in color-erase mode
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANDABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import os,sys
from gimpfu import *

def averageFill(image,layer):
    image.undo_group_start()
    try:
        r, _, _, _, _, _ = pdb.gimp_histogram(layer,HISTOGRAM_RED,0,255)
        g, _, _, _, _, _ = pdb.gimp_histogram(layer,HISTOGRAM_GREEN,0,255)
        b, _, _, _, _, _ = pdb.gimp_histogram(layer,HISTOGRAM_BLUE,0,255)
        gimp.context_push()
        gimp.set_foreground((r/255,g/255,b/255))
        pdb.gimp_edit_fill(layer, FOREGROUND_FILL)
        gimp.context_pop()
               
    except Exception as e:
        print e.args[0]
        gimp.message(e.args[0])

    image.undo_group_end()


### Registration
whoiam='\n'+os.path.abspath(sys.argv[0])
author='Ofnuts'
copyrightYear='2017'
desc='Fills selection with average color of selection'
register(
    'ofn-average-fill',
    desc+whoiam,desc,
    author,author,copyrightYear,
    'Fill with average color',
    'RGB*',
    [
        (PF_IMAGE, 'image', 'Input image', None),
        (PF_DRAWABLE, 'drawable', 'Input drawable', None),
    ],
    [],
    averageFill,
    menu='<Image>/Edit'
)

main()