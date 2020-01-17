#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file was created using the DirectGUI Designer

import os

from direct.showbase.DirectObject import DirectObject
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectEntry import DirectEntry
from direct.gui.DirectButton import DirectButton
from panda3d.core import (
    LPoint3f,
    LVecBase3f
)

from DirectGuiDesignerFileBrowser import DirectGuiDesignerFileBrowser

class DirectGuiDesignerPathSelect(DirectObject):
    def __init__(self, command, headerText, actionText, affirmText, filePath, tooltip):
        self.command = command
        self.darkenFrame = DirectFrame(
            relief=1,
            frameSize=(0, base.getSize()[0], -base.getSize()[1], 0),
            frameColor=(0, 0, 0, 0.45),
            state=DGG.NORMAL,
            parent=base.pixel2d,
        )
        self.mainFrame = DirectFrame(
            relief=1,
            frameSize=(-300,300,-150,150),
            frameColor=(1, 1, 1, 1),
            pos=LPoint3f(base.getSize()[0]/2, 0, -base.getSize()[1]/2),
            parent=base.pixel2d,
        )

        # Header
        headerFrame = DirectFrame(
            parent=self.mainFrame,
            relief=1,
            frameSize=(-300,300,-20,20),
            frameColor=(0.25, 0.25, 0.25, 1.0),
            pos=LPoint3f(0, 0, 130),
            scale=LVecBase3f(1, 0.1, 1),
        )
        DirectLabel(
            parent=headerFrame,
            frameColor=(0.8, 0.8, 0.8, 0.0),
            pos=LPoint3f(-295, 0, -5),
            text = headerText,
            text_align=0,
            text_fg=(1,1,1,1),
            scale=16,
        )

        # Entry
        DirectLabel(
            parent=self.mainFrame,
            frameColor=(0.8, 0.8, 0.8, 0.0),
            pos=LPoint3f(-250, 0, 0),
            scale=12,
            text = actionText,
            text_align=0,
        )
        self.pathEntry = DirectEntry(
            parent=self.mainFrame,
            relief=DGG.SUNKEN,
            frameColor=(1, 1, 1, 1),
            pad=(0.2, 0.2),
            pos=LPoint3f(-250, 0, -20),
            scale=12,
            width=(500-90)/12,
            overflow=True,
            command=self.entryCommandHandler,
            initialText=filePath
        )
        DirectButton(
            parent=self.mainFrame,
            relief=1,
            frameColor = (
                (0.8, 0.8, 0.8, 1), # Normal
                (0.9, 0.9, 1, 1), # Click
                (0.8, 0.8, 1, 1), # Hover
                (0.5, 0.5, 0.5, 1)), # Disabled
            frameSize=(-45, 45, -6, 14),
            pos=LPoint3f(235, 0, -20),
            text = "Browse",
            text_scale=12,
            command=self.browse,
        )
        self.browser = DirectGuiDesignerFileBrowser(self.selectPath, True, os.path.dirname(filePath), os.path.split(filePath)[1], tooltip)
        self.browser.hide()

        # Command Buttons
        DirectButton(
            parent=self.mainFrame,
            relief=1,
            frameColor = (
                (0.8, 0.8, 0.8, 1), # Normal
                (0.9, 0.9, 1, 1), # Click
                (0.8, 0.8, 1, 1), # Hover
                (0.5, 0.5, 0.5, 1)), # Disabled
            frameSize=(-45, 45, -6, 14),
            pos=LPoint3f(140, 0, -135),
            text = affirmText,
            text_scale=12,
            command=command,
            extraArgs=[1],
        )
        DirectButton(
            parent=self.mainFrame,
            relief=1,
            frameColor = (
                (0.8, 0.8, 0.8, 1), # Normal
                (0.9, 0.9, 1, 1), # Click
                (0.8, 0.8, 1, 1), # Hover
                (0.5, 0.5, 0.5, 1)), # Disabled
            frameSize=(-45, 45, -6, 14),
            pos=LPoint3f(245, 0, -135),
            text = "Cancel",
            text_scale=12,
            command=command,
            extraArgs=[0]
        )

        # handle window resizing
        self.prevScreenSize = base.getSize()
        self.accept("window-event", self.windowEventHandler)
        self.accept("escape", command, extraArgs=[0])

    def browse(self):
        self.browser.show()

    def selectPath(self, confirm):
        if confirm:
            self.pathEntry.set(self.browser.get())
        self.browser.hide()

    def entryCommandHandler(self, text):
        self.command(1)

    def destroy(self):
        self.ignoreAll()
        self.browser.destroy()
        self.darkenFrame.destroy()
        self.mainFrame.destroy()

    def getPath(self):
        return self.pathEntry.get()

    def windowEventHandler(self, window=None):
        if window != base.win:
            # This event isn't about our window.
            return

        if window is not None: # window is none if panda3d is not started
            if self.prevScreenSize == base.getSize():
                return
            self.prevScreenSize = base.getSize()
            screenWidthPx = base.getSize()[0]
            screenHeightPx = base.getSize()[1]

            self.mainFrame.setPos(screenWidthPx/2, 0, -screenHeightPx/2)
            self.darkenFrame["frameSize"] = (0, screenWidthPx, -screenHeightPx, 0)
