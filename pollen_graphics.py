# The MIT License (MIT)
#
# Copyright (c) 2019 Michael McGurrin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Version 1.1, 5/21/2020. Revised processing of json to match format of new feed

import time
import json
import displayio
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font

cwd = ("/"+__file__).rsplit('/', 1)[0] # the current working directory (where this file is)
def pollen_graphics(pollen_data):
    """Take input JSON pulled from google map pollen API, extract the relevent data,
    and format for display. Inputs are medium and large fonts and the JSON input from
    the API
    """
    value_graphics = {
        'N/A': "/icons/NotAvailable.bmp",
        1: "/icons/Low.bmp",
        2: "/icons/Moderate.bmp",
        3: "/icons/High.bmp",
        4: "/icons/VeryHigh.bmp",
        5: "/icons/Extreme.bmp",
        }
    # Extract the values from json for trees, weeds, and grasses
    # Set defaults before the loop
    tree_graphic = value_graphics['N/A']
    weed_graphic = value_graphics['N/A']
    grass_graphic = value_graphics['N/A']

    for item in pollen_data:
        print("item displayName:", item['displayName'])
        if item['displayName'] == 'Tree':
            if 'indexInfo' in item:
                tree_graphic = value_graphics[item['indexInfo']['value']]
            else:
                tree_graphic = value_graphics['N/A']
        elif item['displayName'] == 'Weed':
            if 'IndexInfo' in item:
                weed_graphic = value_graphics[item['indexInfo']['value']]
            else:
                weed_graphic = value_graphics['N/A']
        elif item['displayName'] == 'Grass':
            if 'indexInfo' in item:
                grass_graphic = value_graphics[item['indexInfo']['value']]
            else:
                grass_graphic = value_graphics['N/A']
    print("selected graphics: ", tree_graphic, weed_graphic, grass_graphic)
    pollen_group = displayio.Group()
    tree_file = open(tree_graphic, "rb")
    tree_bitmap = displayio.OnDiskBitmap(tree_file)
    tree_tilegrid = displayio.TileGrid(tree_bitmap, pixel_shader=tree_bitmap.pixel_shader)
    tree_tilegrid.x = 80
    tree_tilegrid.y = 55
    pollen_group.append(tree_tilegrid)

    weed_file = open(weed_graphic, "rb")
    weed_bitmap = displayio.OnDiskBitmap(weed_file)
    weed_tilegrid = displayio.TileGrid(weed_bitmap, pixel_shader=weed_bitmap.pixel_shader)
    weed_tilegrid.x = 80
    weed_tilegrid.y = 115
    pollen_group.append(weed_tilegrid)

    grass_file = open(grass_graphic, "rb")
    grass_bitmap = displayio.OnDiskBitmap(grass_file)
    grass_tilegrid = displayio.TileGrid(grass_bitmap, pixel_shader=grass_bitmap.pixel_shader)
    grass_tilegrid.x = 80
    grass_tilegrid.y = 175
    pollen_group.append(grass_tilegrid)

    background_file = "/icons/pollen_background.bmp"
    return (pollen_group, background_file)
