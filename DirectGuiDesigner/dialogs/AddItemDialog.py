#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file was created using the DirectGUI Designer

from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectScrolledFrame import DirectScrolledFrame
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectButton import DirectButton
from DirectGuiExtension.DirectBoxSizer import DirectBoxSizer
from direct.gui.DirectEntry import DirectEntry
from panda3d.core import (
    LPoint3f,
    LVecBase3f,
    LVecBase4f,
    TextNode,
    PGButton,
    MouseButton
)

from direct.gui import DirectGuiGlobals as DGG
DGG.MWUP = PGButton.getPressPrefix() + MouseButton.wheel_up().getName() + '-'
DGG.MWDOWN = PGButton.getPressPrefix() + MouseButton.wheel_down().getName() + '-'


class GUI:
    def __init__(self, rootParent=None):
        self.frame = DirectFrame(
            frameSize=(-1, 1, -1, 1),
            frameColor=(1, 1, 1, 1),
            pos=LPoint3f(0, 0, 0),
            scale=LVecBase3f(0.6, 0.6, 0.6),
            parent=rootParent,
        )
        self.frame.setTransparency(0)

        self.argFrame = DirectScrolledFrame(
            state='normal',
            relief=4,
            frameSize=(-0.9, 0.9, -0.7, 0.7),
            frameColor=(1, 1, 1, 1),
            pos=LPoint3f(0, 0, 0),
            canvasSize=(-0.51, 1.0, -2.0, 0.0),
            parent=self.frame,
        )
        self.argFrame.setTransparency(0)

        self.contentBox = DirectBoxSizer(
            orientation='vertical',
            parent=self.argFrame.canvas,
        )
        self.contentBox.setTransparency(0)

        self.headline = DirectLabel(
            pos=LPoint3f(0, 0, 0.83),
            scale=LVecBase3f(0.1, 0.1, 0.1),
            text=['Select Extra Arguments'],
            parent=self.frame,
        )
        self.headline.setTransparency(0)

        self.cancel = DirectButton(
            pad=(0.2, 0.1),
            pos=LPoint3f(0.725, 0, -0.875),
            scale=LVecBase3f(0.1, 0.1, 0.1),
            text=['Cancel'],
            parent=self.frame,
            pressEffect=1,
        )
        self.cancel.setTransparency(0)

        self.ok = DirectButton(
            pad=(0.3, 0.1),
            pos=LPoint3f(0.25, 0, -0.875),
            scale=LVecBase3f(0.1, 0.1, 0.1),
            text=['Ok'],
            parent=self.frame,
            pressEffect=1,
        )
        self.ok.setTransparency(0)

    def show(self):
        self.frame.show()

    def hide(self):
        self.frame.hide()

    def destroy(self):
        self.frame.destroy()


class AddItemDialog(GUI):
    def __init__(self, customWidget, child, childInfo, func, rootParent=None):
        if rootParent is None:
            rootParent = base.pixel2d
        super().__init__(rootParent)
        self.labelList = []
        self.entryList = []

        self.frame.setScale(200)
        self.frame.setPos(base.getSize()[0] // 2, 0, -base.getSize()[1] // 2)

        self.customWidget = customWidget
        self.child = child
        self.childInfo = childInfo
        self.func = func

        self.ok["command"] = self.__callback
        self.cancel["command"] = self.destroy

        self.bindScroll(self.argFrame)
        self.bindScroll(self.argFrame.verticalScroll)
        self.bindScroll(self.argFrame.verticalScroll.thumb)
        self.bindScroll(self.contentBox)

        self.createContent()

    def scrollStep(self, stepCount, *args):
        """Scrolls the indicated number of steps forward.  If
        stepCount is negative, scrolls backward."""
        gui = self.argFrame.verticalScroll
        gui['value'] = gui.guiItem.getValue() + gui.guiItem.getScrollSize() * stepCount

    def bindScroll(self, element):
        element.bind(DGG.MWUP, self.scrollStep, extraArgs=[-20])
        element.bind(DGG.MWDOWN, self.scrollStep, extraArgs=[20])

    def __callback(self, *args):
        extraArgs = self.getValues()
        index = 0
        for definition, value in zip(self.customWidget.addItemExtraArgs.values(), extraArgs):
            valueType = definition["type"]
            defaultValue = definition["defaultValue"]
            converter = str
            if valueType == "int":
                converter = int
            elif valueType == "float":
                converter = float
            elif valueType == "str":
                converter = str

            if value == "":
                extraArgs[index] = defaultValue
            else:
                extraArgs[index] = converter(value)

            index += 1

        self.childInfo.addItemExtraArgs = extraArgs
        self.func(self.child, *extraArgs)

        self.destroy()

    def createContent(self):
        for name, value in self.customWidget.addItemExtraArgs.items():
            defaultValue = str(value["defaultValue"])
            self.addLabel(name)
            self.addEntry(defaultValue)

        self.argFrame["canvasSize"] = self.contentBox["frameSize"]

    def addLabel(self, text):
        newLabel = DirectLabel(
            scale=LVecBase3f(0.1, 0.1, 0.1),
            text=text
        )
        self.contentBox.addItem(newLabel)
        self.labelList.append(newLabel)
        self.bindScroll(newLabel)

    def addEntry(self, text=""):
        newEntry = DirectEntry(
            scale=LVecBase3f(0.1, 0.1, 0.1),
            frameColor=(1, 1, 1, 1),
            initialText=text
        )
        self.contentBox.addItem(newEntry)
        self.entryList.append(newEntry)
        self.bindScroll(newEntry)

    def getValues(self):
        extraArgs = []
        for entry in self.entryList:
            extraArgs.append(entry.get())

        return extraArgs

    def destroy(self):
        super().destroy()
        del self.func
        del self.child
        del self.customWidget
        del self.childInfo

        del self.labelList
        del self.entryList

