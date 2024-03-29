#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file was created using the DirectGUI Designer

from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectScrolledFrame import DirectScrolledFrame
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectButton import DirectButton
from DirectGuiExtension.DirectBoxSizer import DirectBoxSizer
from direct.gui.DirectEntry import DirectEntry
from direct.gui.DirectRadioButton import DirectRadioButton
from DirectGuiExtension.DirectCollapsibleFrame import DirectCollapsibleFrame
from panda3d.core import (
    LPoint3f,
    LVecBase3f,
    LVecBase4f,
    TextNode,
    PGButton,
    MouseButton
)

from direct.showbase.DirectObject import DirectObject

from direct.gui import DirectGuiGlobals as DGG
DGG.MWUP = PGButton.getPressPrefix() + MouseButton.wheel_up().getName() + '-'
DGG.MWDOWN = PGButton.getPressPrefix() + MouseButton.wheel_down().getName() + '-'


class GUI(DirectObject):
    def __init__(self, rootParent=None):
        super().__init__()
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
            suppressMouse=True,
            state=DGG.NORMAL
        )
        self.contentBox.setTransparency(0)

        self.headline = DirectLabel(
            pos=LPoint3f(0, 0, 0.83),
            scale=LVecBase3f(0.1, 0.1, 0.1),
            text=['Select Extra Arguments'],
            parent=self.frame,
            suppressMouse=True,
            state=DGG.NORMAL
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


class AddByFunction(GUI):
    def __init__(self, customWidget, child, childInfo, func, rootParent=None):
        if rootParent is None:
            rootParent = base.pixel2d
        super().__init__(rootParent)

        self.value = {}  # use name to access the element selection for that parameter
        self.radioList = {}  # dict[name: str, list[radiobutton]]
        self.labelList = []
        self.entryDict = {}

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
            elif valueType == "element":
                def converter(value_):
                    return value_

            if value == "":
                extraArgs[index] = defaultValue
            else:
                try:
                    extraArgs[index] = converter(value)
                except Exception:
                    print("Could not convert value to the specified type")
                    base.messenger.send(
                        "showWarning", [f"The value: '{value}' could not be interpreted as a '{valueType}'."]
                    )
                    return

            index += 1

        self.childInfo.addItemExtraArgs = extraArgs
        try:
            self.func(self.child, *extraArgs)
        except Exception:
            print("Error running addItemFunc")
            base.messenger.send(
                "showWarning", [f"Element could not be added to the parent: {self.customWidget.displayName}"]
            )

        self.destroy()

    def createContent(self):
        for name, value in self.customWidget.addItemExtraArgs.items():
            valueType = value["type"]
            defaultValue = str(value["defaultValue"])
            self.addLabel(name)
            if valueType == "element":
                self.addElementSelection(name)
            else:
                self.addEntry(defaultValue, name)

        self.argFrame["canvasSize"] = self.contentBox["frameSize"]

    def addLabel(self, text):
        newLabel = DirectLabel(
            scale=LVecBase3f(0.1, 0.1, 0.1),
            text=text,
            suppressMouse=True,
            state=DGG.NORMAL
        )
        self.contentBox.addItem(newLabel)
        self.labelList.append(newLabel)
        self.bindScroll(newLabel)

    def addEntry(self, text="", name=""):
        newEntry = DirectEntry(
            scale=LVecBase3f(0.1, 0.1, 0.1),
            frameColor=(1, 1, 1, 1),
            initialText=text
        )
        self.contentBox.addItem(newEntry)
        self.entryDict[name] = newEntry
        self.bindScroll(newEntry)

    def addElementSelection(self, name):
        selection = DirectCollapsibleFrame(
            frameSize=(0, 1, -1, 0.1),
            suppressMouse=True,
            toggleCollapseButton_suppressMouse=True
        )
        self.accept(selection.getExtendedEvent(), self.contentBox.refresh)
        self.accept(selection.getCollapsedEvent(), self.contentBox.refresh)
        self.bindScroll(selection)
        self.bindScroll(selection.toggleCollapseButton)
        self.contentBox.addItem(selection)
        selectionBox = DirectBoxSizer(
            orientation='vertical',
            parent=selection,
            suppressMouse=True
        )
        self.bindScroll(selectionBox)
        i = True
        self.radioList[name] = []
        for key, elementInfo in base.dgd.elementDict.items():
            if i:
                self.value[name] = [elementInfo.element]
                i = False
            newButton = DirectRadioButton(
                scale=LVecBase3f(0.1, 0.1, 0.1),
                text=elementInfo.name,
                variable=self.value[name],
                value=[elementInfo.element],
                suppressMouse=True,
                indicator_suppressMouse=True
            )
            selectionBox.addItem(newButton)
            self.radioList[name].append(newButton)
            self.bindScroll(newButton)

        size = selectionBox["frameSize"]
        selectionBox.setX(-size[0])
        sSize = selection["frameSize"]
        selection["frameSize"] = (sSize[0], sSize[1], size[2], sSize[3])
        selection.updateFrameSize()

        for radioButton in self.radioList[name]:
            radioButton.setOthers(self.radioList[name])

    def getValues(self):
        extraArgs = []
        for name, value in self.customWidget.addItemExtraArgs.items():
            valueType = value["type"]
            if valueType == "element":
                extraArgs.append(self.value[name][0])
            else:
                extraArgs.append(self.entryDict[name].get())

        return extraArgs

    def destroy(self):
        super().destroy()
        del self.func
        del self.child
        del self.customWidget
        del self.childInfo

        del self.labelList
        del self.entryDict


class AddByNode(GUI):
    def __init__(self, customWidget, child, childInfo, parent, rootParent=None):
        if rootParent is None:
            rootParent = base.pixel2d
        super().__init__(rootParent)
        self.radioList = []

        self.value = [customWidget.addItemNode[0]]

        self.frame.setScale(200)
        self.frame.setPos(base.getSize()[0] // 2, 0, -base.getSize()[1] // 2)

        self.customWidget = customWidget
        self.child = child
        self.childInfo = childInfo
        self.parent = parent

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
        try:
            node = getattr(self.parent, self.value[0])
            self.child.reparentTo(node)
        except Exception:
            print(f"Error reparenting element to: {self.value[0]}")
            base.messenger.send(
                "showWarning", [f"Could not reparent {self.child.name} to node: {self.value[0]}"]
            )

        self.childInfo.addItemNode = self.value[0]

        self.destroy()

    def createContent(self):
        for name in self.customWidget.addItemNode:
            self.addRadioButton(name)

        for radioButton in self.radioList:
            radioButton.setOthers(self.radioList)
        self.argFrame["canvasSize"] = self.contentBox["frameSize"]

    def addRadioButton(self, text):
        newButton = DirectRadioButton(
            scale=LVecBase3f(0.1, 0.1, 0.1),
            text=text,
            variable=self.value,
            value=[text]
        )
        self.contentBox.addItem(newButton)
        self.radioList.append(newButton)
        self.bindScroll(newButton)

    def destroy(self):
        super().destroy()
        del self.parent
        del self.child
        del self.childInfo
        del self.customWidget
