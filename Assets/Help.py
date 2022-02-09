#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file was created using the DirectGUI Designer

from direct.gui import DirectGuiGlobals as DGG

from direct.gui.DirectFrame import DirectFrame
from DirectGuiExtension.DirectAutoSizer import DirectAutoSizer
from DirectGuiExtension.DirectBoxSizer import DirectBoxSizer
from direct.gui.DirectLabel import DirectLabel
from panda3d.core import (
    LPoint3f,
    LVecBase3f,
    LVecBase4f,
    TextNode
)
# We need showbase to make this script directly runnable
from direct.showbase.ShowBase import ShowBase

class GUI:
    def __init__(self, rootParent=None):

        self.frmMain = DirectFrame(
            borderWidth=(2, 2),
            frameColor=(1, 1, 1, 1),
            frameSize=(0.0, 800.0, -600.0, 0.0),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(0, 0, 0),
            parent=rootParent,
        )
        self.frmMain.setTransparency(0)

        self.boxMain = DirectBoxSizer(
            autoUpdateFrameSize=0,
            frameSize=[0.0, 800.0, -600.0, 0.0],
            hpr=LVecBase3f(0, 0, 0),
            itemAlign=17,
            orientation='vertical',
            pos=LPoint3f(0, 0, 0),
        )
        self.boxMain.setTransparency(0)

        self.autosizerMain = DirectAutoSizer(
            frameSize=[0.0, 800.0, -600.0, 0.0],
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(0, 0, 0),
            parent=self.frmMain,
            childUpdateSizeFunc=self.boxMain.refresh,
        )
        self.autosizerMain.setTransparency(0)

        self.pg15691 = DirectLabel(
            borderWidth=(2, 2),
            frameSize=LVecBase4f(-27.6, 30, -2.7, 17.4),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(0, 0, -17.4),
            scale=LVecBase3f(1, 1, 1),
            text='Label',
            text0_align=TextNode.A_center,
            text0_scale=(24, 24),
            text0_pos=(0, 0),
            text0_fg=LVecBase4f(0, 0, 0, 1),
            text0_bg=LVecBase4f(0, 0, 0, 0),
            text0_wordwrap=None,
        )
        self.pg15691.setTransparency(0)

        self.autosizerMain.setChild(self.boxMain)
        self.boxMain.addItem(self.pg15691)

    def show(self):
        self.frmMain.show()

    def hide(self):
        self.frmMain.hide()

    def destroy(self):
        self.frmMain.destroy()

# Create a ShowBase instance to make this gui directly runnable
app = ShowBase()
GUI(app.pixel2d)
app.run()
