#!/usr/bin/env python
"""In case somebody wants to use the color picker on linux."""

import sys

import pygtk
import gtk


pygtk.require('2.0')


COLOR_SEL = gtk.ColorSelectionDialog("Sublime Color Picker")

if len(sys.argv) > 1:
    if gtk.gdk.Color(sys.argv[1]):
        COLOR_SEL.colorsel.set_current_color(gtk.gdk.Color(sys.argv[1]))

if COLOR_SEL.run() == gtk.RESPONSE_OK:
    COLOR = COLOR_SEL.colorsel.get_current_color()
    # Convert to 8bit channels
    RED = COLOR.red / 256
    GREEN = COLOR.green / 256
    BLUE = COLOR.blue / 256
    # Convert to hexa strings
    RED = str(hex(RED))[2:]
    GREEN = str(hex(GREEN))[2:]
    BLUE = str(hex(BLUE))[2:]
    # Format
    if len(RED) == 1:
        RED = "0%s" % RED
    if len(GREEN) == 1:
        GREEN = "0%s" % GREEN
    if len(BLUE) == 1:
        BLUE = "0%s" % BLUE

    FINAL_COLOR = RED + GREEN + BLUE
    print(FINAL_COLOR.upper())

COLOR_SEL.destroy()
