"""
Gallery to show one picture per day and special files on selected dates.

Images need to be 800 x 480 pixels and jpeg format, file extention jpg or jpeg
Images they must be the screen dimensions (or smaller) and saved as *non-progressive* jpgs.

Copy images to the root of your SD card by plugging it into a computer.
Remember to eject the file before removing it from the computer

To display a specific file on a specific day prefix it with
DateDDMM
e.g.
Date1703-Andy.jpg
"""

import os
import gc
import random
import inky_frame
import jpegdec
import sdcard
import time
import inky_helper as ih
import network
from machine import Pin, I2C, RTC
import pcf85063a

from machine import SPI, Pin

from picographics import DISPLAY_INKY_FRAME_SPECTRA_7 as DISPLAY  # 7.3" Spectra
from picographics import PicoGraphics

print("Dad's Photoframe")

# how often to change image (in minutes)
UPDATE_INTERVAL = 24 * 60

# set up the display
graphics = PicoGraphics(DISPLAY)

# Create a new JPEG decoder for our PicoGraphics
j = jpegdec.JPEG(graphics)

# Set tz_offset to be the number of hours off of UTC for your local zone.
# Examples:  tz_offset = -7 # Pacific time (PST)
#            tz_offset =  1 # CEST (Paris)
tz_offset = 0
tz_seconds = tz_offset * 3600

def getDate():
    # Read clock and on fail assume it's Christmas
    # Sync the Inky (always on) RTC to the Pico W so that "time.localtime()" works.
    inky_frame.pcf_to_pico_rtc()

    year, month, day, hour, minute, second, dow, _ = time.localtime(time.time() + tz_seconds)

    # Connect to the network and get the time if it's not set
    if year < 2023:
        # Connect to WiFi and set the time
        try:
            from secrets import WIFI_PASSWORD, WIFI_SSID
            ih.network_connect(WIFI_SSID, WIFI_PASSWORD)
            inky_frame.set_time()
            year, month, day, hour, minute, second, dow, _ = time.localtime(time.time() + tz_seconds)     
        except:
            print("Add your WiFi credentials to secrets.py")
            # Set the RTC to an approx time.
            year = 2025
            month = 12
            day = 25
            i2c = I2C(0)
            rtc = pcf85063a.PCF85063A(i2c)
            rtc.datetime((year, month, day, hour, minute, second, dow))
            inky_frame.pcf_to_pico_rtc()

    return year, month, day, hour, minute, second, dow

try:
    print("Reading SDCard")

    # set up the SD card
    sd_spi = SPI(0, sck=Pin(18, Pin.OUT), mosi=Pin(19, Pin.OUT), miso=Pin(16, Pin.OUT))
    sd = sdcard.SDCard(sd_spi, Pin(22))
    os.mount(sd, "/sd")
except Exception as error:
    print("No SDCard found", error)
    graphics.set_font("bitmap8")
    graphics.set_pen(1)
    graphics.clear()
    graphics.set_pen(0) # Black
    graphics.set_thickness(4)
    graphics.text("No SDCard found", 5, 5, scale=8)
    graphics.update()
    time.sleep(10)
    inky_frame.sleep_for(1) # Time for the display to redraw
    inky_frame.turn_off     # Stop or if on power will reboot

def shuffle_inplace(seq):
    """Shuffle list seq in-place using Fisher–Yates (uniform)."""
    for i in range(len(seq) - 1, 0, -1):
        j = random.randrange(i + 1)  # 0 <= j <= i
        seq[i], seq[j] = seq[j], seq[i]

def display_image(filename):
    # Open the JPEG file
    j.open_file(filename)

    # Decode the JPEG
    j.decode(0, 0, jpegdec.JPEG_SCALE_FULL)

    # Display the result
    graphics.update()

def find_first_date_file(datefiles, day, month):
    prefix = f"date{int(day):02d}{int(month):02d}"

    for f in datefiles:
        if (f.lower().startswith(prefix)):
            return f
    return None

# Main code

# Get a list of files that are in the directory
files = os.listdir("/sd")
# remove files from the list that aren't .jpgs or .jpegs
files = [f for f in files if f.lower().endswith((".jpg", ".jpeg"))]

shuffle_inplace(files)

# Split these
date_files = [f for f in files if f.lower().startswith("date")]
files = [f for f in files if not f.lower().startswith("date")]

print("Running")

while True:
    for file in files:
        # Check for special date file-> "Date1703-Andy.jpg"
        year, month, day, hour, minute, second, dow = getDate()
        date_time = f"{year:04}/{month:02}/{day:02} {hour:02}:{minute:02}:{second:02}"
        print(date_time)

        specialDay = find_first_date_file(date_files, day, month)
        print("Special day",specialDay)  
        if (specialDay != None):
            file = specialDay
        
        print(f"Displaying /sd/{file}")
        display_image("/sd/" + file)

        print(f"Sleeping for {UPDATE_INTERVAL} minutes")
        time.sleep(10)
        inky_frame.sleep_for(UPDATE_INTERVAL)

    gc.collect() # Garbage collect each time we've done a full pass of the files.
