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
import displayio
from adafruit_display_text.label import Label

DAY_NAMES = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday",
]
MONTH_NAMES = [
    "Unknown", "January", "February", "March", "April",
    "May", "June", "July", "August", "September",
    "October", "November", "December",
]

def day_graphics(medium_font, large_font):
    """Build and return a display Group showing current day, date, and time.

    Returns:
        displayio.Group
    """
    text_group = displayio.Group()

    time_label = Label(medium_font)
    time_label.x = 220
    time_label.y = 25
    time_label.color = 0xFFFFFF
    text_group.append(time_label)

    date_label = Label(medium_font)
    date_label.x = 60
    date_label.y = 140
    date_label.color = 0xFFFFFF
    text_group.append(date_label)

    day_label = Label(large_font)
    day_label.x = 80
    day_label.y = 100
    day_label.color = 0xFFFFFF
    text_group.append(day_label)

    now = time.localtime()
    day_label.text  = DAY_NAMES[now[6]]
    date_label.text = MONTH_NAMES[now[1]] + " " + str(now[2]) + ", " + str(now[0])

    hour   = now[3]
    minute = now[4]
    fmt = "%d:%02d"
    if hour >= 12:
        hour -= 12
        fmt += " PM"
    else:
        fmt += " AM"
    if hour == 0:
        hour = 12
    time_label.text = fmt % (hour, minute)

    return text_group
