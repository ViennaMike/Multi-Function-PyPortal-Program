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

# Version 2.0 5/22/2026
#   Updated for CircuitPython 10.x: migrated secrets to settings.toml,
#   replaced pyportal.fetch() with direct requests via pyportal.network.
#   Fixed bugs: daily reset variable typo, RuntimeError string comparisons,
#   uninitialized variables on first fetch failure, pollen bitmap file handle
#   leak (now fixed in pollen_graphics.py). Removed dead code.

"""
Main program for a multi-function PyPortal app.
Cycles through: day/date/time, weather, pollen, shower thoughts, S&P 500.
"""

import os
import sys
import time
import gc
import microcontroller
import board

from adafruit_pyportal import PyPortal
from adafruit_bitmap_font import bitmap_font

cwd = ("/" + __file__).rsplit("/", 1)[0]
sys.path.append(cwd)

import day_graphics
import openweather_graphics
import st_graphics
import market_graphics
import pollen_graphics

linger = 5       # seconds to display most apps
long_linger = 10 # seconds for text-heavy apps (shower thoughts, pollen)

# API endpoints — credentials read from settings.toml
LOCATION = "4791160"  # Vienna, VA (OpenWeatherMap city ID)
WX_DATA_SOURCE = (
    "https://api.openweathermap.org/data/2.5/weather?id=" + LOCATION
    + "&appid=" + os.getenv("OPENWEATHER_TOKEN")
)
MARKET_DATA_SOURCE = "https://query2.finance.yahoo.com/v8/finance/chart/%5EGSPC?range=1d&interval=1d"
MARKET_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/111.0.0.0 Safari/537.36"
}
ST_DATA_SOURCE = "https://api.adviceslip.com/advice"
POLLEN_DATA_SOURCE = (
    "https://pollen.googleapis.com/v1/forecast:lookup?key="
    + os.getenv("GOOGLE_KEY")
    + "&location.longitude=-77.23&location.latitude=38.91&days=1&plantsDescription=False"
)

# Initialise PyPortal — WiFi credentials come from settings.toml automatically
pyportal = PyPortal(status_neopixel=board.NEOPIXEL, default_bg=0x000000)
pyportal.network.connect()
requests = pyportal.network.requests

# Record how many groups the library owns in root_group (e.g. _bg_group).
# The exception handler uses this as a floor so it never pops library-owned
# groups — specifically _bg_group, which set_background() updates in-place
# but never re-inserts if removed.
BASE_GROUP_LEN = len(pyportal.root_group)

# Load fonts once; pass references to each graphics module
small_font  = bitmap_font.load_font(cwd + "/fonts/Arial-12.bdf")
medium_font = bitmap_font.load_font(cwd + "/fonts/Arial-16.bdf")
large_font  = bitmap_font.load_font(cwd + "/fonts/Arial-Bold-24.bdf")
glyphs = b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-,.: '
small_font.load_glyphs(glyphs)
medium_font.load_glyphs(glyphs)
large_font.load_glyphs(glyphs)
large_font.load_glyphs(("°",))

# Display order: 0=time, 1=weather, 2=shower thoughts, 3=market, 4=pollen
# Repeat index 0 to interleave time between other apps.
order = [0, 1, 4, 0, 2, 0, 3]
index = 0

# Timestamps for rate-limiting each data source
localtime_refresh = 0
weather_refresh   = 0
st_refresh        = 0
market_refresh    = 0
pollen_refresh    = 0

last_reset_day = None  # tracks which calendar day the daily reset last fired
error_counter  = 0     # consecutive time-sync failures; 3 in a row triggers reset

# Cached data — initialised to None so first-cycle fetch failures are handled
# gracefully (app is skipped rather than crashing with NameError)
wx            = None
thought       = None
current_price = None
prev_close    = None
pollen_data   = None

while True:
    try:
        now = time.localtime()
        if now[3] == 2 and now[4] == 13 and last_reset_day != now[2]:
            print("Scheduled daily reset at 2:13 AM")
            last_reset_day = now[2]
            microcontroller.reset()

        print("index =", index, "  app =", order[index])

        # ------------------------------------------------------------------
        # App 0 — Day / Date / Time
        # ------------------------------------------------------------------
        if order[index] == 0:
            gc.collect()
            pyportal.set_background(cwd + "/day_bitmap.bmp")
            if localtime_refresh == 0 or (time.monotonic() - localtime_refresh) > 3600:
                print("Getting time from internet")
                try:
                    pyportal.get_local_time()
                    localtime_refresh = time.monotonic()
                    error_counter = 0
                except Exception as e:
                    print("Time sync failed:", type(e).__name__, e)
                    localtime_refresh = 0
                    error_counter += 1
                    if error_counter >= 3:
                        print("Time sync failed 3 times — resetting")
                        microcontroller.reset()
            text_group = day_graphics.day_graphics(
                medium_font=medium_font, large_font=large_font)
            pyportal.root_group.append(text_group)
            time.sleep(linger)
            pyportal.root_group.pop()
            text_group = None

        # ------------------------------------------------------------------
        # App 1 — Weather (OpenWeatherMap, refreshes every 10 min)
        # ------------------------------------------------------------------
        elif order[index] == 1:
            gc.collect()
            pyportal.set_background(cwd + "/wx_bitmap.bmp")
            time.sleep(1)
            if weather_refresh == 0 or (time.monotonic() - weather_refresh) > 600:
                print("Getting weather from internet")
                try:
                    response = requests.get(WX_DATA_SOURCE)
                    raw = response.json()
                    response.close()
                    del response
                    # Extract only the fields we need, then free the full dict
                    wx = {
                        "icon":        raw["weather"][0]["icon"],
                        "name":        raw["name"],
                        "dt":          raw["dt"],
                        "timezone":    raw["timezone"],
                        "main_wx":     raw["weather"][0]["main"],
                        "temp":        raw["main"]["temp"],
                        "description": raw["weather"][0]["description"],
                    }
                    del raw
                    gc.collect()
                    weather_refresh = time.monotonic()
                except Exception as e:
                    if "Failed to request hostname" in str(e):
                        print("Network error — resetting:", e)
                        microcontroller.reset()
                    print("Weather fetch error:", type(e).__name__, e)
            if wx is not None:
                text_group, background_file = openweather_graphics.wx_graphics(
                    medium_font=medium_font, large_font=large_font,
                    small_font=small_font, weather=wx)
                gc.collect()
                pyportal.set_background(cwd + background_file)
                pyportal.root_group.append(text_group)
                time.sleep(linger)
                pyportal.root_group.pop()
                text_group = None
            else:
                time.sleep(linger)

        # ------------------------------------------------------------------
        # App 2 — Advice slips (refreshes every 2 hours)
        # ------------------------------------------------------------------
        elif order[index] == 2:
            gc.collect()
            pyportal.set_background(cwd + "/st_bitmap.bmp")
            time.sleep(1)
            if st_refresh == 0 or (time.monotonic() - st_refresh) > 7200:
                print("Getting advice slip quote from internet")
                try:
                    response = requests.get(ST_DATA_SOURCE)
                    print("Status:", response.status_code)
                    st_json = response.json()
                    response.close()
                    del response
                    st_refresh = time.monotonic()
                    new_thought = st_json["slip"]["advice"]
                    print("new thought: ", new_thought)
                    del st_json
                    if len(new_thought) <= 140:
                        thought = new_thought
                    elif thought is None:
                        # First run and entry is too long — use fallback
                        thought = "Brevity is the soul of wit. (William Shakespeare)"
                    # else: keep the previously cached thought
                except Exception as e:
                    print("advice slip fetch error:", type(e).__name__, e)
                    st_refresh = 0  # Force retry next cycle
                    # Don't reset — let the main loop's error handler deal with it
            if thought is not None:
                print("advice slip:", thought)
                text_group = st_graphics.st_graphics(
                    medium_font=medium_font, large_font=large_font,
                    small_font=small_font, thought=thought)
                pyportal.root_group.append(text_group)
                time.sleep(long_linger)
                pyportal.root_group.pop()
                text_group = None
            else:
                time.sleep(long_linger)

        # ------------------------------------------------------------------
        # App 3 — S&P 500 (Yahoo Finance, refreshes every 15 min)
        # ------------------------------------------------------------------
        elif order[index] == 3:
            gc.collect()
            pyportal.set_background(cwd + "/market_bitmap.bmp")
            time.sleep(1)
            if market_refresh == 0 or (time.monotonic() - market_refresh) > 900:
                print("Getting S&P 500 from internet")
                try:
                    response = requests.get(MARKET_DATA_SOURCE, headers=MARKET_HEADERS)
                    market_data = response.json()
                    response.close()
                    del response
                    market_refresh = time.monotonic()
                    meta = market_data["chart"]["result"][0]["meta"]
                    current_price = meta["regularMarketPrice"]
                    prev_close    = meta["chartPreviousClose"]
                    del market_data, meta
                    print("S&P price:", current_price, " prev close:", prev_close)
                except Exception as e:
                    if "Failed to request hostname" in str(e):
                        print("Network error — resetting:", e)
                        microcontroller.reset()
                    print("Market fetch error:", type(e).__name__, e)
            if current_price is not None and prev_close is not None:
                text_group, background_file = market_graphics.market_graphics(
                    medium_font=medium_font, large_font=large_font,
                    market=current_price, market2=prev_close)
                gc.collect()
                pyportal.set_background(cwd + background_file)
                pyportal.root_group.append(text_group)
                time.sleep(linger)
                pyportal.root_group.pop()
                text_group = None
            else:
                time.sleep(linger)

        # ------------------------------------------------------------------
        # App 4 — Pollen (Google Maps Pollen API, refreshes every 4 hr)
        # ------------------------------------------------------------------
        elif order[index] == 4:
            gc.collect()
            pyportal.set_background(cwd + "/pollen_cover.bmp")
            time.sleep(1)
            if pollen_refresh == 0 or (time.monotonic() - pollen_refresh) > 14400:
                print("Getting pollen data from internet")
                try:
                    response = requests.get(POLLEN_DATA_SOURCE)
                    if response.status_code != 200:
                        print("Bad pollen HTTP status:", response.status_code)
                        response.close()
                        del response
                        pollen_refresh = 0
                    else:
                        pollen_json = response.json()
                        response.close()
                        del response
                        pollen_refresh = time.monotonic()
                        # Extract only the 3 index values, then free the full dict
                        tree_val = weed_val = grass_val = "N/A"
                        for item in pollen_json["dailyInfo"][0]["pollenTypeInfo"]:
                            name = item["displayName"]
                            val = item["indexInfo"]["value"] if "indexInfo" in item else "N/A"
                            if name == "Tree":
                                tree_val = val
                            elif name == "Weed":
                                weed_val = val
                            elif name == "Grass":
                                grass_val = val
                        pollen_data = {"tree": tree_val, "weed": weed_val, "grass": grass_val}
                        del pollen_json, tree_val, weed_val, grass_val
                        gc.collect()
                except Exception as e:
                    if "Failed to request hostname" in str(e):
                        print("Network error — resetting:", e)
                        microcontroller.reset()
                    print("Pollen fetch error:", type(e).__name__, e)
            if pollen_data is not None:
                text_group, background_file = pollen_graphics.pollen_graphics(
                    pollen_data["tree"], pollen_data["weed"], pollen_data["grass"])
                gc.collect()
                pyportal.set_background(cwd + background_file)
                pyportal.root_group.append(text_group)
                time.sleep(long_linger)
                pyportal.root_group.pop()
                text_group = None
            else:
                time.sleep(long_linger)

        else:
            raise ValueError("app index set to invalid value")

        index = (index + 1) % len(order)

    except Exception as e:
        print("Error in main loop — skipping iteration:", e)
        while len(pyportal.root_group) > BASE_GROUP_LEN:
            pyportal.root_group.pop()
        index = (index + 1) % len(order)

    gc.collect()
    print("Free memory:", gc.mem_free())
