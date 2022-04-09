#!/usr/bin/env python
# -*- coding: utf-8 -*-

from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData, WindowProperties
from editorLogHandler import setupLog
from DirectGuiDesigner.DirectGuiDesigner import DirectGuiDesigner

loadPrcFileData(
    "",
    """
    sync-video #t
    textures-power-2 none
    window-title DirectGUI Designer
    maximized #t
    win-size 1280 720
    ime-aware #t
    """)

logfilepath = setupLog("DirectGuiDesigner")

base = ShowBase()

def set_dirty_name():
    wp = WindowProperties()
    wp.setTitle("*DirectGUI Designer")
    base.win.requestProperties(wp)

def set_clean_name():
    wp = WindowProperties()
    wp.setTitle("DirectGUI Designer")
    base.win.requestProperties(wp)

base.accept("request_dirty_name", set_dirty_name)
base.accept("request_clean_name", set_clean_name)

dgd = DirectGuiDesigner(base.pixel2d)
dgd.logfile = logfilepath

base.run()
