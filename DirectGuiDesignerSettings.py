#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file was created using the DirectGUI Designer

from direct.gui import DirectGuiGlobals as DGG

from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectEntry import DirectEntry
from direct.gui.DirectCheckButton import DirectCheckButton
from panda3d.core import (
    LPoint3f,
    LVecBase3f,
    LVecBase4f,
    TextNode
)

class GUI:
    def __init__(self, rootParent=None):

        self.frmMain = DirectFrame(
            borderWidth=(2, 2),
            frameColor=(1, 1, 1, 1),
            frameSize=(-300.0, 300.0, -350.0, 350.0),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(694.875, 0, -488.5),
            parent=rootParent,
        )

        self.btnOk = DirectButton(
            borderWidth=(2, 2),
            frameSize=(-45.0, 45.0, -6.0, 14.0),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(120, 0, -320),
            scale=LVecBase3f(1, 1, 1),
            text='OK',
            text_align=2,
            text_scale=(12.0, 12.0),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            parent=self.frmMain,
            command=base.messenger.send,
            extraArgs=["Settings_OK"],
        )

        self.btnCancel = DirectButton(
            borderWidth=(2, 2),
            frameSize=(-45.0, 45.0, -6.0, 14.0),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(230, 0, -320),
            scale=LVecBase3f(1, 1, 1),
            text='Cancel',
            text_align=2,
            text_scale=(12.0, 12.0),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            parent=self.frmMain,
            command=base.messenger.send,
            extraArgs=["Settings_CANCEL"],
        )

        self.lblCustomWidgets = DirectLabel(
            borderWidth=(2, 2),
            frameColor=(0.8, 0.8, 0.8, 0.0),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(-260, 0, 210),
            scale=LVecBase3f(1, 1, 1),
            text='Custom widgets path:',
            text_align=0,
            text_scale=(12.0, 12.0),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            parent=self.frmMain,
        )

        self.lblHeader = DirectLabel(
            borderWidth=(2, 2),
            frameColor=(0.8, 0.8, 0.8, 0.0),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(0, 0, 300),
            scale=LVecBase3f(1, 1, 1),
            text='Settings',
            text_align=2,
            text_scale=(32.0, 32.0),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            parent=self.frmMain,
        )

        self.txtCustomWidgetsPath = DirectEntry(
            borderWidth=(2, 2),
            hpr=LVecBase3f(0, 0, 0),
            overflow=1,
            pos=LPoint3f(-50, 0, 210),
            scale=LVecBase3f(1, 1, 1),
            width=25.0,
            text_align=0,
            text_scale=(12.0, 12.0),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            parent=self.frmMain,
        )

        self.lblAskForQuit = DirectLabel(
            borderWidth=(2, 2),
            frameColor=(0.8, 0.8, 0.8, 0.0),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(-260, 0, 140),
            scale=LVecBase3f(1, 1, 1),
            text='Ask before quit:',
            text_align=0,
            text_scale=(12.0, 12.0),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            parent=self.frmMain,
        )

        self.cbAskForQuit = DirectCheckButton(
            borderWidth=(2, 2),
            frameColor=(1.0, 1.0, 1.0, 1.0),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(110, 0, 140),
            scale=LVecBase3f(1, 1, 1),
            text='',
            indicator_borderWidth=(2, 2),
            indicator_hpr=LVecBase3f(0, 0, 0),
            indicator_pos=LPoint3f(-11, 0, -7.2),
            indicator_relief='sunken',
            indicator_text_align=2,
            indicator_text_scale=(24, 24),
            indicator_text_pos=(0, -0.2),
            indicator_text_fg=LVecBase4f(0, 0, 0, 1),
            indicator_text_bg=LVecBase4f(0, 0, 0, 0),
            text_align=0,
            text_scale=(12.0, 12.0),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            parent=self.frmMain,
        )

        self.lblExecutableScripts = DirectLabel(
            borderWidth=(2, 2),
            frameColor=(0.8, 0.8, 0.8, 0.0),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(-260, 0, 70),
            scale=LVecBase3f(1, 1, 1),
            text='Create executable Scripts:',
            text_align=0,
            text_scale=(12.0, 12.0),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            parent=self.frmMain,
        )

        self.cbExecutableScripts = DirectCheckButton(
            borderWidth=(2, 2),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(110, 0, 70),
            scale=LVecBase3f(1, 1, 1),
            text='',
            indicator_borderWidth=(2, 2),
            indicator_hpr=LVecBase3f(0, 0, 0),
            indicator_pos=LPoint3f(-11, 0, -7.2),
            indicator_relief='sunken',
            indicator_text_align=2,
            indicator_text_scale=(24, 24),
            indicator_text_pos=(0, -0.2),
            indicator_text_fg=LVecBase4f(0, 0, 0, 1),
            indicator_text_bg=LVecBase4f(0, 0, 0, 0),
            text_align=2,
            text_scale=(12.0, 12.0),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            parent=self.frmMain,
        )

