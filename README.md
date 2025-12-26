# InkyFrame
Photo Rotation for the 7in InkyFrame

## Details
Writtten in Micropython for the Pimoroni inky-frame, a Pico 2 W powered E Ink®display with Wifi and RTC

## Installation
Copy the .py files to the screen using a tool like Thony.
If you want to sync the time to your wifi network once a day then create a new file secrets.py containing two lines

SSID = “YOUR WI-FI AP NAME”
PASSWORD = “YOUR WI-FI PASSWORD

## Images
Images need to be 800 x 480 pixels and jpeg format, file extention jpg or jpeg
Images they must be the screen dimensions (or smaller) and saved as *non-progressive* jpgs.

Copy images to the root of your SD card by plugging it into a computer.
Remember to eject the file before removing it from the computer

To display a specific file on a specific day prefix it with
DateDDMM
e.g.
Date1703-Andy.jpg

## Reference
* https://github.com/pimoroni/inky-frame
* https://shop.pimoroni.com/products/inky-frame-7-3?variant=40541882056787

