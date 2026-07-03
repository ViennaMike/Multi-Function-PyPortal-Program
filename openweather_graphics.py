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

cwd = ("/" + __file__).rsplit("/", 1)[0]

def wx_graphics(medium_font, large_font, small_font, weather):
    """Build and return a display Group from a parsed OpenWeatherMap JSON dict.

    Args:
        weather: dict already parsed from the OpenWeatherMap API response.
    Returns:
        (displayio.Group, background_file_path)
    """
    text_group = displayio.Group()

    time_text = Label(medium_font)
    time_text.x = 200
    time_text.y = 25
    time_text.color = 0xFFFFFF
    text_group.append(time_text)

    temp_text = Label(large_font)
    temp_text.x = 200
    temp_text.y = 195
    temp_text.color = 0xFFFFFF
    text_group.append(temp_text)

    main_text = Label(large_font)
    main_text.x = 10
    main_text.y = 195
    main_text.color = 0xFFFFFF
    text_group.append(main_text)

    description_text = Label(small_font)
    description_text.x = 10
    description_text.y = 225
    description_text.color = 0xFFFFFF
    text_group.append(description_text)

    background_file = "/icons/" + weather["icon"] + ".bmp"

    city_text = Label(medium_font, text=weather["name"])
    city_text.x = 10
    city_text.y = 25
    city_text.color = 0xFFFFFF
    text_group.append(city_text)
    print(weather["name"])

    now_cast_time = time.localtime(weather["dt"] + weather["timezone"])
    hour   = now_cast_time[3]
    minute = now_cast_time[4]
    fmt = "%d:%02d"
    if hour >= 12:
        hour -= 12
        fmt += " PM"
    else:
        fmt += " AM"
    if hour == 0:
        hour = 12
    time_text.text = "(" + fmt % (hour, minute) + ")"

    print(weather["main_wx"])
    main_text.text = weather["main_wx"]

    temperature = weather["temp"] - 273.15  # Kelvin → Celsius → Fahrenheit
    print(temperature)
    temp_text.text = "%d °F" % ((temperature * 9 / 5) + 32)

    description = weather["description"]
    description = description[0].upper() + description[1:]
    print(description)
    description_text.text = description

    return (text_group, background_file)
