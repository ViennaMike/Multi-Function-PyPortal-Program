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

import time
import json
import displayio
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font

# cwd = ("/"+__file__).rsplit('/', 1)[0] # the current working directory (where this file is)

def st_graphics(medium_font, large_font, small_font, st):
    """Take input JSON pulled from the Shower Thoughts subreddit API, extract the title field,
    and format for display. Inputs are medium, large, and small fonts and the JSON input from
    the API
    """
    text_group = displayio.Group(max_size = 6)

    st = json.loads(st)
    thought = st['data']['children'][0]['data']['title']
    print(thought)
    # Split into multiple lines (based on pyportal's wrap_nicely method)
    # Use smaller font if needed to fit
    thought = thought[:170] # max we can fit on display
    if len(thought) > 140:
        max_chars = 38
        font = small_font
        max_glyphs = 38
    else:
        max_chars = 28
        font = medium_font
        max_glyphs = 28
    words = thought.split(' ')
    the_lines = []
    the_line = ""
    for w in words:
        if len(the_line+' '+w) <= max_chars:
            the_line += ' '+w
        else:
            the_lines.append(the_line)
            the_line = ''+w
    if the_line:      # last line remaining
        the_lines.append(the_line)
    # remove first space from first line:
    the_lines[0] = the_lines[0][1:]

    for idx, line in enumerate(the_lines):
        thought_text = Label(font, line_spacing = 1.2, max_glyphs = max_glyphs)
        thought_text.x = 15
        thought_text.y = 110 + (idx * 24)
        thought_text.color = 0xFFFFFF
        thought_text.text = line
        text_group.append(thought_text)
    return(text_group)