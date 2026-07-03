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

# Version 1.3 3/18/2024 Covid removed awhile ago. This update adds pollen
#     levels from the Google Maps Platform API.
# Version 1.2 5/21/2020 Restructured and added control over ordering, so, for example,
#     can interleave apps, such as time, weather, time, shower thoughts, time, S&P
# Version 1.1 5/20/2020. Replaced Alpha Vantage as source for S&P 500 Data with
# Finnhub, since AV stopped providing S&P index via their free API.

"""
This is the main program for a multi-function Portal app.
It includes current weather, day, date, time, S&P 500, pollen levels,
and Shower Thoughts subreddit.
"""
import sys
import time
import microcontroller
import board
import supervisor
import json
from adafruit_pyportal import PyPortal
from adafruit_bitmap_font import bitmap_font
import adafruit_requests as requests

cwd = ("/"+__file__).rsplit('/', 1)[0]  # the current working directory (where this file is)
sys.path.append(cwd)

import day_graphics          # pylint: disable=wrong-import-position
import openweather_graphics  # pylint: disable=wrong-import-position
import st_graphics           # pylint: disable=wrong-import-position
import market_graphics       # pylint: disable=wrong-import-position
import pollen_graphics       # pylint: disable=wrong-import-position

linger = 5  # number of seconds to stay on each app
long_linger = 10  # For apps with more text, like shower thoughts

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# Initiate the pyportal
DATA_LOCATION = []
pyportal = PyPortal(json_path=DATA_LOCATION,
                    status_neopixel=board.NEOPIXEL,
                    default_bg=0x000000)

# Get the fonts for all apps
small_font = cwd+"/fonts/Arial-12.bdf"
medium_font = cwd+"/fonts/Arial-16.bdf"
large_font = cwd+"/fonts/Arial-Bold-24.bdf"
small_font = bitmap_font.load_font(small_font)
medium_font = bitmap_font.load_font(medium_font)
large_font = bitmap_font.load_font(large_font)
glyphs = b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-,.: '
small_font.load_glyphs(glyphs)
medium_font.load_glyphs(glyphs)
large_font.load_glyphs(glyphs)
large_font.load_glyphs(('°',))  # a non-ascii character we need for sure

# Weather info
# Use cityname, country code where countrycode is ISO3166 format.
# E.g. "New York, US" or "London, GB" OR use Location Code
LOCATION = "4791160"  # Vienna, VA
# Set up where we'll be fetching data from
# You'll need to get a token from openweather.org, looks like 'b6907d289e10d714a6e88b30761fae22'
WX_DATA_SOURCE = "https://api.openweathermap.org/data/2.5/weather?id="+LOCATION
WX_DATA_SOURCE += "&appid="+secrets['openweather_token']

# S&P 500 ("Market Data") info
MARKET_DATA_SOURCE = "https://query2.finance.yahoo.com/v8/finance/chart/%5EGSPC"
market_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
# PRICE_DATA_SOURCE = 'https://twelve-data1.p.rapidapi.com/price?symbol=GSPC'
# CLOSE_DATA_SOURCE = 'https://twelve-data1.p.rapidapi.com/time_series?symbol=GSPC&interval=1day&outputsize=2'

# Shower thoughts info
ST_DATA_SOURCE = "https://www.reddit.com/r/Showerthoughts/new.json?sort=new&limit=1"

# Pollen count info
# pollen_key = secrets['google_key']
pollen_key = secrets['google_key']
POLLEN_DATA_SOURCE = "https://pollen.googleapis.com/v1/forecast:lookup" + '?key=' + pollen_key
POLLEN_LOCATION_DATA = 'location.longitude=-77.23&location.latitude=38.91&days=1&plantsDescription=False'

# Create exception for when Google doesn't return pollen response code (value not = 200)
class InvalidPollenResponseCode(Exception):
    pass

def iso(a_time):
    local_time = time.localtime(a_time)
    year = str(local_time[0])
    month = str(local_time[1])
    if len(month) == 1:
        month = '0'+month
    day_of_month = str(local_time[2])
    if len(day_of_month) == 1:
        day_of_month = '0'+day_of_month
    day_iso = year+'-'+month+'-'+day_of_month+'T00:00:00.000'
    return day_iso

def local(a_time):
    local_time = time.localtime(a_time)
    year = str(local_time[0])
    month = str(local_time[1])
    day_of_month = str(local_time[2])
    day_local = month+'/'+day_of_month+'/'+year
    return day_local

# Loop through all the applications
localtime_refresh = 0
weather_refresh = 0
st_refresh = 0
market_refresh = 0
pollen_refresh = 0

# Set up an ordering list, so it's easy to add new apps (memory permitting) or change their order, or
# repeat an app in the order
order = [0, 1, 4, 0, 2, 0, 3]
index = 0
"""
Occassionally, seemingly at randome, get errors like:
"unable to get time from the internet -  Failed to request hostname"
So put in an error counter, if happens 5 times, reset the device.
"""
error_counter = 0
while True:
    try:
        print('index = ',index, 'order[index] = ',order[index])
        if order[index] == 0:
            # Day, date, and time. Only query the online time once per hour (and on first run).
            pyportal.set_background(cwd+"/day_bitmap.bmp")
            if (localtime_refresh == 0) or (time.monotonic() - localtime_refresh) > 3600:
                print("Getting time from internet!")
                try:
                    pyportal.get_local_time()
                    localtime_refresh = time.monotonic()
                    error_counter=0
                except RuntimeError as e:
                    print("unable to get time from the internet - ", e)
                    localtime_refresh = 0
                    error_counter+=1
                    if error_counter >= 3:
                        print("failed 3 times in a row, doing hardware reset")
                        microcontroller.reset()
            text_group = day_graphics.day_graphics(medium_font = medium_font, large_font = large_font)
            pyportal.splash.append(text_group)
            # Display for linger seconds, then empty the pyportal.splash group so it can be loaded with new display info
            time.sleep(linger)
        elif order[index] == 1:
            # Display weather: only query the weather every 10 minutes (and on first run)."""
            pyportal.set_background(cwd+"/wx_bitmap.bmp")
            time.sleep(1)
            if (weather_refresh == 0) or (time.monotonic() - weather_refresh) > 600:
                weather_refresh = time.monotonic()
                try:
                    wx = pyportal.fetch(WX_DATA_SOURCE)
                except RuntimeError as e:
                    if e == "Failed to request hostname":
                        print("Error: ", e, "doing hardware reset")
                        microcontroller.reset()
                print("Response is", wx)
            text_group, background_file = openweather_graphics.wx_graphics(medium_font = medium_font,
                                large_font = large_font, small_font = small_font, weather = wx)
            pyportal.set_background(cwd+background_file)
            pyportal.splash.append(text_group)
            # Display for linger seconds
            time.sleep(linger)
        elif order[index] == 2:
            # Display Reddit Shower Thoughts. Only query shower thoughts every 5 minutes (and on first run)."""
            pyportal.set_background(cwd+"/st_bitmap.bmp")
            time.sleep(1)
            if (st_refresh == 0) or (time.monotonic() - st_refresh) > 300:
                st_refresh = time.monotonic()
                print("Getting shower thought from internet!")
                try:
                    st = pyportal.fetch(ST_DATA_SOURCE)
                except RuntimeError as e:
                    if e == "Failed to request hostname":
                        print("Error: ", e, "Doing hardware reset")
                        microcontroller.reset()
                print("Response is", st)
            # If shower thought longer than 140 characters, skip update, use old shower thought
            st_json = json.loads(st)
            thought = st_json['data']['children'][0]['data']['title']
            print("shower thought: ", thought)
            print("length: ", len(thought))
            text_group = st_graphics.st_graphics(medium_font = medium_font, large_font = large_font,
                        small_font = small_font, st = st)
            pyportal.splash.append(text_group)
            # Display for long_linger seconds
            time.sleep(long_linger)
        elif order[index] == 3:
            """Display S&P 500. Only query the S&P every 15 minutes (and on first run)."""
            pyportal.set_background(cwd+"/market_bitmap.bmp")
            time.sleep(1)
            if (market_refresh == 0) or (time.monotonic() - market_refresh) > 900:
                market_refresh = time.monotonic()
                print("Getting S&P 500 from internet!")
                try:
                    market = requests.get(MARKET_DATA_SOURCE, headers=market_headers)
                    # print(stock_response.headers)
                    market_data = market.json()
                    market_meta = market_data["chart"]["result"][0]["meta"]
                    prev_close = market_meta["previousClose"]
                    current_price = market_meta["regularMarketPrice"]
                    print(prev_close)
                    print(current_price)
                except RuntimeError as e:
                    if e == "Failed to request hostname":
                        print("Error: ", e, "doing hardware reset")
                        microcontroller.reset()
                if current_price == '' or prev_close == '':
                    raise ValueError('empty string returned')
            text_group, background_file = market_graphics.market_graphics(medium_font = medium_font, large_font = large_font,
                                    market = current_price, market2 = prev_close)
            pyportal.set_background(cwd+background_file)
            pyportal.splash.append(text_group)
            # Display for linger seconds, then empty the pyportal.splash group so it can be loaded with new display info
            time.sleep(linger)
        elif order[index] == 4:
            """Display Universal Pollen Index for trees, grass, and weeds, if available."""
            pyportal.set_background(cwd+"/pollen_cover.bmp")
            time.sleep(1)
            if ((time.monotonic() - pollen_refresh) > 14400) or (pollen_refresh == 0):
                pollen_refresh = time.monotonic()
                print("Getting Pollen Data from internet!")
                try:
                    POLLEN_DATA_SOURCE = POLLEN_DATA_SOURCE + '&'+POLLEN_LOCATION_DATA
                    print("pollen data source: ", POLLEN_DATA_SOURCE)
                    pollen_response = requests.get(POLLEN_DATA_SOURCE)
                    print ("pollen status code: ", pollen_response.status_code)
                    print("pollen response header: ", pollen_response.headers)
                    print("pollen json body: ", pollen_response.json())
                    if pollen_response.status_code != 200:
                        pollen_refresh = 14340
                        bad_pollen_data = True
                        raise ValueError("bad http status code returned")
                except RuntimeError as e:
                    if e == "Failed to request hostname":
                        print("Error: ", e, "doing hardware reset")
                        microcontroller.reset()
            pollen_data = pollen_response.json()['dailyInfo'][0]['pollenTypeInfo']
            text_group, background_file = pollen_graphics.pollen_graphics(pollen_data)
            print('pollen text_group: ', text_group)
            pyportal.set_background(cwd+background_file)
            pyportal.splash.append(text_group)
            # Display for long_linger seconds
            time.sleep(long_linger)
        else:
            raise ValueError("app index set to invalid value")
        # Empty the pyportal.splash group so it can be loaded with new display info
        pyportal.splash.pop()
        index = (index+1)%(len(order))
    except Exception as e:
        print("Some error occured,  skipping this iteration! -", e)
        index = (index+1)%(len(order))
        continue
