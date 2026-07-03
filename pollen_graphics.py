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

import displayio

VALUE_GRAPHICS = {
    "N/A": "/icons/NotAvailable.bmp",
    0:     "/icons/None.bmp",
    1:     "/icons/VeryLow.bmp",
    2:     "/icons/Low.bmp",
    3:     "/icons/Moderate.bmp",
    4:     "/icons/High.bmp",
    5:     "/icons/VeryHigh.bmp",
}

def pollen_graphics(tree, weed, grass):
    """Build and return a display Group for tree, weed, and grass pollen levels.

    Args:
        tree:  tree pollen index value (int 0-5 or "N/A")
        weed:  weed pollen index value (int 0-5 or "N/A")
        grass: grass pollen index value (int 0-5 or "N/A")
    Returns:
        (displayio.Group, background_file_path)
    """
    tree_graphic  = VALUE_GRAPHICS.get(tree,  VALUE_GRAPHICS["N/A"])
    weed_graphic  = VALUE_GRAPHICS.get(weed,  VALUE_GRAPHICS["N/A"])
    grass_graphic = VALUE_GRAPHICS.get(grass, VALUE_GRAPHICS["N/A"])

    print("Pollen graphics:", tree_graphic, weed_graphic, grass_graphic)

    pollen_group = displayio.Group()

    # CircuitPython 9.2+ accepts a path string directly — no manual open() needed,
    # which prevents file-handle accumulation across display cycles.
    for path, x_pos, y_pos in [
        (tree_graphic,  80,  55),
        (weed_graphic,  80, 115),
        (grass_graphic, 80, 175),
    ]:
        bitmap    = displayio.OnDiskBitmap(path)
        tile_grid = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)
        tile_grid.x = x_pos
        tile_grid.y = y_pos
        pollen_group.append(tile_grid)

    return (pollen_group, "/icons/pollen_background.bmp")
