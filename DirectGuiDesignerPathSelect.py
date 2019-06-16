#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file was created using the DirectGUI Designer

from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectEntry import DirectEntry
from direct.gui.DirectButton import DirectButton
from panda3d.core import (
    LPoint3f,
    LVecBase3f
)

class DirectGuiDesignerPathSelect:
    def __init__(self, command, headerText, actionText, affirmText, filePath):
        self.darkenFrame = DirectFrame(
            relief=1,
            frameSize=(base.a2dLeft,base.a2dRight,base.a2dTop,base.a2dBottom),
            frameColor=(0, 0, 0, 0.45),
            pos=LPoint3f(0, 0, 0),
            state=DGG.NORMAL
        )
        self.mainFrame = DirectFrame(
            relief=1,
            frameSize=(-0.75,0.75,-0.4,0.4),
            frameColor=(1, 1, 1, 1),
            pos=LPoint3f(0, 0, 0),
        )
        self.pathEntry = DirectEntry(
            parent=self.mainFrame,
            borderWidth=(0.1, 0.1),
            frameColor=(0.8, 0.8, 0.8, 1),
            pad=(0.2, 0.2),
            pos=LPoint3f(-0.7, 0, 0.02),
            scale=0.05,
            width=28,
            overflow=True,
            command=command,
            extraArgs=[1],
            initialText=filePath
        )
        DirectButton(
            parent=self.mainFrame,
            relief=1,
            frameColor=(0.8, 0.8, 0.8, 1),
            pos=LPoint3f(0.575, 0, -0.35),
            scale=LVecBase3f(0.1, 0.1, 0.1),
            text = "Cancel",
            text_scale=0.75,
            command=command,
            extraArgs=[0]
        )
        headerFrame = DirectFrame(
            parent=self.mainFrame,
            relief=1,
            frameSize=(-0.75,0.75,-0.05,0.05),
            frameColor=(0.25, 0.25, 0.25, 1.0),
            pos=LPoint3f(0, 0, 0.35),
            scale=LVecBase3f(1, 0.1, 1),
        )
        DirectLabel(
            parent=headerFrame,
            frameColor=(0.8, 0.8, 0.8, 0.0),
            pos=LPoint3f(-0.7, 0, -0.02),
            scale=LVecBase3f(0.07, 0.1, 0.07),
            text = headerText,
            text_align=0,
            text_fg=(1,1,1,1),
            text_scale=0.75,
        )
        DirectButton(
            parent=self.mainFrame,
            relief=1,
            frameColor=(0.8, 0.8, 0.8, 1),
            pos=LPoint3f(0.325, 0, -0.35),
            scale=LVecBase3f(0.1, 0.1, 0.1),
            text = affirmText,
            text_scale=0.75,
            command=command,
            extraArgs=[1],
        )
        DirectLabel(
            parent=self.mainFrame,
            frameColor=(0.8, 0.8, 0.8, 0.0),
            pos=LPoint3f(-0.71, 0, 0.11),
            scale=LVecBase3f(0.1, 0.1, 0.1),
            text_scale=0.5,
            text = actionText,
            text_align=0,
        )

    def destroy(self):
        self.darkenFrame.destroy()
        self.mainFrame.destroy()

    def getPath(self):
        return self.pathEntry.get()
