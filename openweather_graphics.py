
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

cwd = ("/"+__file__).rsplit('/', 1)[0] # the current working directory (where this file is)
def wx_graphics(medium_font, large_font, small_font, weather):
    """Take input JSON pulled from the openweather API, extract the relevent data,
    and format for display. Inputs are medium, large, and small fonts and the JSON input from
    the API
    """
    text_group = displayio.Group(max_size = 5)
    weather = json.loads(weather)

    time_text = Label(medium_font, max_glyphs=11)
    time_text.x = 200
    time_text.y = 25 # default was 12
    time_text.color = 0xFFFFFF
    text_group.append(time_text)

    temp_text = Label(large_font, max_glyphs=6)
    temp_text.x = 200
    temp_text.y = 195
    temp_text.color = 0xFFFFFF
    text_group.append(temp_text)

    main_text = Label(large_font, max_glyphs=20)
    main_text.x = 10
    main_text.y = 195
    main_text.color = 0xFFFFFF
    text_group.append(main_text)

    description_text = Label(small_font, max_glyphs=60)
    description_text.x = 10
    description_text.y = 225
    description_text.color = 0xFFFFFF
    text_group.append(description_text)

    # set the background based on the weather
    weather_icon = weather['weather'][0]['icon']
    background_file = "/icons/"+weather_icon+".bmp"

    # city_name =  weather['name'] + ", " + weather['sys']['country']
    city_name =  weather['name']
    print(city_name)
    city_text = Label(medium_font, text=city_name)
    city_text.x = 10
    city_text.y = 25 # default was 12
    city_text.color = 0xFFFFFF
    text_group.append(city_text)

    now_cast_time = time.localtime(weather['dt']+weather['timezone'])
    hour = now_cast_time[3]
    minute = now_cast_time[4]
    format_str = "%d:%02d"
    if hour >= 12:
        hour -= 12
        format_str = format_str+" PM"
    else:
        format_str = format_str+" AM"
    if hour == 0:
        hour = 12
    time_str = "("+format_str % (hour, minute)+")"
    time_text.text = time_str

    main_wx = weather['weather'][0]['main']
    print(main_wx)
    main_text.text = main_wx

    temperature = weather['main']['temp'] - 273.15 # its...in kelvin
    print(temperature)
    temp_text.text = "%d °F" % ((temperature * 9 / 5) + 32)

    description = weather['weather'][0]['description']
    description = description[0].upper() + description[1:]
    print(description)
    description_text.text = description
    # example: "thunderstorm with heavy drizzle"
    return (text_group, background_file)