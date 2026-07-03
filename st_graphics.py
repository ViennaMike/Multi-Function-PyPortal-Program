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
from adafruit_display_text.label import Label

def st_graphics(medium_font, large_font, small_font, thought):
    """Build and return a display Group that word-wraps an advice slip string.

    Args:
        thought: plain string (already extracted from the API response).
    Returns:
        displayio.Group
    """
    text_group = displayio.Group()

    print("Advice slip:", thought, "  length:", len(thought))

    font = medium_font
    max_chars = 28

    words = thought.split(" ")
    lines = []
    line = ""
    for word in words:
        if len(line + " " + word) <= max_chars:
            line += " " + word
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)

    # Strip the leading space introduced by the " " + word join on the first line
    lines[0] = lines[0].lstrip()

    for idx, line in enumerate(lines):
        label = Label(font, line_spacing=1.2)
        label.x = 15
        label.y = 110 + (idx * 24)
        label.color = 0xFFFFFF
        label.text = line
        text_group.append(label)

    return text_group
