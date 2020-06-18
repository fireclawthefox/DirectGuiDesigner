#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file was created using the DirectGUI Designer

from direct.gui import DirectGuiGlobals as DGG

from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectButton import DirectButton
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
            frameSize=(-300.0, 300.0, -250.0, 250.0),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(0, 0, 0),
            parent=rootParent,
        )
        self.frmMain.setTransparency(0)

        self.frmHeader = DirectFrame(
            borderWidth=(2, 2),
            frameColor=(0.25, 0.25, 0.25, 1.0),
            frameSize=(-300.0, 300.0, -20.0, 20.0),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(0, 0, 230),
            parent=self.frmMain,
        )
        self.frmHeader.setTransparency(0)

        self.lblHeader = DirectLabel(
            borderWidth=(2, 2),
            frameColor=(0.8, 0.8, 0.8, 0.0),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(-295, 0, -5),
            scale=LVecBase3f(1, 1, 1),
            text='Settings',
            text_align=TextNode.A_left,
            text_scale=(16.0, 16.0),
            text_pos=(0, 0),
            text_fg=LVecBase4f(1, 1, 1, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            parent=self.frmHeader,
        )
        self.lblHeader.setTransparency(0)

        self.btnOk = DirectButton(
            borderWidth=(2, 2),
            frameSize=(-45.0, 45.0, -6.0, 14.0),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(120, 0, -220),
            relief=1,
            scale=LVecBase3f(1, 1, 1),
            text='OK',
            text_align=TextNode.A_center,
            text_scale=(12.0, 12.0),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            parent=self.frmMain,
            command=messenger.send,
            extraArgs=["Settings_OK"],
        )
        self.btnOk.setTransparency(0)

        self.btnCancel = DirectButton(
            borderWidth=(2, 2),
            frameSize=(-45.0, 45.0, -6.0, 14.0),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(230, 0, -220),
            relief=1,
            scale=LVecBase3f(1, 1, 1),
            text='Cancel',
            text_align=TextNode.A_center,
            text_scale=(12.0, 12.0),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            parent=self.frmMain,
            command=messenger.send,
            extraArgs=["Settings_CANCEL"],
        )
        self.btnCancel.setTransparency(0)

        self.lblCustomWidgets = DirectLabel(
            borderWidth=(2, 2),
            frameColor=(0.8, 0.8, 0.8, 0.0),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(-260, 0, 5),
            scale=LVecBase3f(1, 1, 1),
            text='Custom widgets path:',
            text_align=TextNode.A_left,
            text_scale=(12.0, 12.0),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            parent=self.frmMain,
        )
        self.lblCustomWidgets.setTransparency(0)

        self.txtCustomWidgetsPath = DirectEntry(
            borderWidth=(0.167, 0.167),
            hpr=LVecBase3f(0, 0, 0),
            overflow=1,
            pos=LPoint3f(-50, 0, 5),
            scale=LVecBase3f(12, 1, 12),
            width=18.0,
            text_align=TextNode.A_left,
            text_scale=(1.0, 1.0),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            parent=self.frmMain,
        )
        self.txtCustomWidgetsPath.setTransparency(0)

        self.lblAskForQuit = DirectLabel(
            borderWidth=(2, 2),
            frameColor=(0.8, 0.8, 0.8, 0.0),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(-260, 0, 140),
            scale=LVecBase3f(1, 1, 1),
            text='Ask before quit:',
            text_align=TextNode.A_left,
            text_scale=(12.0, 12.0),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            parent=self.frmMain,
        )
        self.lblAskForQuit.setTransparency(0)

        self.cbAskForQuit = DirectCheckButton(
            borderWidth=(2, 2),
            frameColor=(1.0, 1.0, 1.0, 1.0),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(110, 0, 145),
            scale=LVecBase3f(1, 1, 1),
            text='',
            indicator_borderWidth=(2, 2),
            indicator_hpr=LVecBase3f(0, 0, 0),
            indicator_pos=LPoint3f(-11, 0, -7.2),
            indicator_relief='sunken',
            indicator_text_align=TextNode.A_center,
            indicator_text_scale=(24, 24),
            indicator_text_pos=(0, -0.2),
            indicator_text_fg=LVecBase4f(0, 0, 0, 1),
            indicator_text_bg=LVecBase4f(0, 0, 0, 0),
            text_align=TextNode.A_left,
            text_scale=(12.0, 12.0),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            parent=self.frmMain,
        )
        self.cbAskForQuit.setTransparency(0)

        self.lblExecutableScripts = DirectLabel(
            borderWidth=(2, 2),
            frameColor=(0.8, 0.8, 0.8, 0.0),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(-260, 0, 95),
            scale=LVecBase3f(1, 1, 1),
            text='Create executable Scripts:',
            text_align=TextNode.A_left,
            text_scale=(12.0, 12.0),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            parent=self.frmMain,
        )
        self.lblExecutableScripts.setTransparency(0)

        self.cbExecutableScripts = DirectCheckButton(
            borderWidth=(2, 2),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(110, 0, 100),
            scale=LVecBase3f(1, 1, 1),
            text='',
            indicator_borderWidth=(2, 2),
            indicator_hpr=LVecBase3f(0, 0, 0),
            indicator_pos=LPoint3f(-11, 0, -7.2),
            indicator_relief='sunken',
            indicator_text_align=TextNode.A_center,
            indicator_text_scale=(24, 24),
            indicator_text_pos=(0, -0.2),
            indicator_text_fg=LVecBase4f(0, 0, 0, 1),
            indicator_text_bg=LVecBase4f(0, 0, 0, 0),
            text_align=TextNode.A_center,
            text_scale=(12.0, 12.0),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            parent=self.frmMain,
        )
        self.cbExecutableScripts.setTransparency(0)

        self.btnBrowseWidgetPath = DirectButton(
            borderWidth=(2, 2),
            frameSize=(-45.25, 45.25, -6.0, 14.0),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(230, 0, 5),
            relief=1,
            scale=LVecBase3f(1, 1, 1),
            text='Browse',
            text_align=TextNode.A_center,
            text_scale=(12.0, 12.0),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            parent=self.frmMain,
        )
        self.btnBrowseWidgetPath.setTransparency(0)

        self.lblShowToolbar = DirectLabel(
            borderWidth=(2, 2),
            frameColor=(0.8, 0.8, 0.8, 0.0),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(-260, 0, 50),
            scale=LVecBase3f(1, 1, 1),
            text='Show toolbar',
            text_align=TextNode.A_left,
            text_scale=(12.0, 12.0),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            parent=self.frmMain,
        )
        self.lblShowToolbar.setTransparency(0)

        self.cbShowToolbar = DirectCheckButton(
            borderWidth=(2, 2),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(110, 0, 55),
            scale=LVecBase3f(1, 1, 1),
            text='',
            indicator_borderWidth=(2, 2),
            indicator_hpr=LVecBase3f(0, 0, 0),
            indicator_pos=LPoint3f(-11, 0, -7.2),
            indicator_relief='sunken',
            indicator_text_align=TextNode.A_center,
            indicator_text_scale=(24, 24),
            indicator_text_pos=(0, -0.2),
            indicator_text_fg=LVecBase4f(0, 0, 0, 1),
            indicator_text_bg=LVecBase4f(0, 0, 0, 0),
            text_align=TextNode.A_center,
            text_scale=(12.0, 12.0),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            parent=self.frmMain,
        )
        self.cbShowToolbar.setTransparency(0)

        self.lblSearchPath = DirectLabel(
            borderWidth=(2, 2),
            frameColor=(0.8, 0.8, 0.8, 0.0),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(-260, 0, -40),
            scale=LVecBase3f(1, 1, 1),
            text='Search paths',
            text_align=TextNode.A_left,
            text_scale=(12.0, 12.0),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            parent=self.frmMain,
        )
        self.lblSearchPath.setTransparency(0)

        self.txtSearchPaths = DirectEntry(
            borderWidth=(0.167, 0.167),
            frameSize=(-0.167, 18.167, -0.463, 1.155),
            hpr=LVecBase3f(0, 0, 0),
            overflow=1,
            pos=LPoint3f(-50, 0, -45),
            scale=LVecBase3f(12, 1, 12),
            width=18.0,
            text_align=TextNode.A_left,
            text_scale=(1, 1),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            parent=self.frmMain,
        )
        self.txtSearchPaths.setTransparency(0)

        self.btnBrowseSearchPaths = DirectButton(
            borderWidth=(2, 2),
            frameSize=(-45.25, 45.25, -6.0, 14.0),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(230, 0, -45),
            relief=1,
            scale=LVecBase3f(1, 1, 1),
            text='Browse',
            text_align=TextNode.A_center,
            text_scale=(12.0, 12.0),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            parent=self.frmMain,
        )
        self.btnBrowseSearchPaths.setTransparency(0)


    def show(self):
        self.frmMain.show()

    def hide(self):
        self.frmMain.hide()

    def delete(self):
        self.frmMain.delete()
