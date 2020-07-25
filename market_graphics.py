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
def market_graphics(medium_font, large_font, market):
    """Take input JSON pulled from the Alpha Vantage API, extract the relevent data,
    and format for display. Inputs are medium and large fonts and the JSON input from
    the API
    """
    text_group = displayio.Group(max_size = 2)
    market = json.loads(market)

    main_text = Label(large_font, max_glyphs=20)
    main_text.x = 40
    main_text.y = 80
    main_text.color = 0xFFFFFF
    text_group.append(main_text)

    sub_text = Label(medium_font, max_glyphs=20)
    sub_text.x = 30
    sub_text.y = 120
    text_group.append(sub_text)

    price = market['c'] * 10 + 7   # Convert SPY ETF to S&P (about 10x)
    prev_close = market['pc'] * 10 + 7  # Convert SPY ETF to S&P (about 10x)
    change = round(price - prev_close, 2)
    percent = round((100 * change / prev_close), 2)
    print(price, change, percent)

    main_text.text = str(price)
    sub_text.text = str(change) + '  (' + str(percent) + '%)'

    # set the background and color of change
    if change >= 0:
        background_file = "/icons/green_up.bmp"
        sub_text.color = 0x00FF00
    else:
        background_file = "/icons/red_down.bmp"
        sub_text.color = 0xFF0000
    return (text_group, background_file)