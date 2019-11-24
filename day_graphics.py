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
#import json
import displayio
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font

# cwd = ("/"+__file__).rsplit('/', 1)[0] # the current working directory (where this file is)

def day_graphics(medium_font, large_font):
    """Format the day, date, and time info from time.localtime() for display.
    Inputs are medium and large fonts.
    """
    text_group = displayio.Group(max_size = 5)

    ur_label = Label(medium_font, max_glyphs=8) #  time text
    ur_label.x = 220
    ur_label.y = 25
    ur_label.color = 0xFFFFFF
    text_group.append(ur_label)

    sub_label = Label(medium_font, max_glyphs=18) # month, date, year text
    sub_label.x = 60
    sub_label.y = 140
    sub_label.color = 0xFFFFFF
    text_group.append(sub_label)

    main_label = Label(large_font, max_glyphs=9) # day of week
    main_label.x = 80
    main_label.y = 100
    main_label.color = 0xFFFFFF
    text_group.append(main_label)

    """Fetch the time.localtime(), parse it out and update the display text"""
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    month_names = ["Unknown", "January", "Febuary", "March", "April", "May", "June", "July",
        "August", "September", "October", "November", "December"]
    now = time.localtime()
    day_str = day_names[now[6]]
    date_str = str(now[2])
    month_str = month_names[now[1]]
    year_str = str(now[0])
    day_date_str = month_str + " " + date_str + ", " + year_str
    sub_label.text = day_date_str
    main_label.text = day_str
    hour = now[3]
    minute = now[4]
    format_str = "%d:%02d"
    if hour >= 12:
        hour -= 12
        format_str = format_str+" PM"
    else:
        format_str = format_str+" AM"
    if hour == 0:
        hour = 12
    time_str = format_str % (hour, minute)
    ur_label.text = time_str
    return(text_group)