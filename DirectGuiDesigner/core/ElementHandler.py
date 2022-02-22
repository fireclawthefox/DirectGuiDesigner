#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import importlib

from direct.gui import DirectGuiGlobals as DGG

from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectScrolledFrame import DirectScrolledFrame
from direct.gui.DirectEntry import DirectEntry
from directGuiOverrides.DirectEntryScroll import DirectEntryScroll
from direct.gui.DirectCheckBox import DirectCheckBox
from direct.gui.DirectCheckButton import DirectCheckButton
from directGuiOverrides.DirectOptionMenu import DirectOptionMenu
from direct.gui.DirectRadioButton import DirectRadioButton
from directGuiOverrides.DirectSlider import DirectSlider
from directGuiOverrides.DirectScrollBar import DirectScrollBar
from direct.gui.DirectScrolledList import DirectScrolledList
from direct.gui.DirectScrolledList import DirectScrolledListItem
from direct.gui.DirectWaitBar import DirectWaitBar
from direct.gui.DirectDialog import OkDialog
from direct.gui.DirectDialog import OkCancelDialog
from direct.gui.DirectDialog import YesNoDialog
from direct.gui.DirectDialog import YesNoCancelDialog
from direct.gui.DirectDialog import RetryCancelDialog

from panda3d.core import TextNode
from DirectGuiDesigner.core.ElementInfo import ElementInfo

class ElementHandler:
    def __init__(self, propertiesFrame, getEditorRootCanvas):
        self.propertiesFrame = propertiesFrame
        self.getEditorRootCanvas = getEditorRootCanvas
        self.visEditorInAspect2D = True
        self.editorCenter = (0,0,0)

    def setEditorParentType(self, isAspect2D):
        self.visEditorInAspect2D = isAspect2D

    def setEditorCenter(self, center):
        self.editorCenter = center

    def dragStart(self, elementInfo, event):
        base.messenger.send("dragStart", [elementInfo, event])

    def dragStop(self, event):
        base.messenger.send("dragStop", [event])

    def setupBind(self, elementInfo, PassedElementInfo=None):
        elementInfo.element.bind(DGG.B1PRESS, self.dragStart, [PassedElementInfo if PassedElementInfo is not None else elementInfo])
        elementInfo.element.bind(DGG.B1RELEASE, self.dragStop)

    def createMethod(self, widget, parent=None):
        parent = self.getEditorRootCanvas() if parent is None else parent
        pos = self.editorCenter if parent == self.getEditorRootCanvas() else (0,0,0)
        element = getattr(widget.module, widget.className)(
            parent=parent,
            pos=pos)
        elementInfo = ElementInfo(element, widget.className, customImportPath=widget.importPath)
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesMethod(self, element, elementDict, widget):
        self.propertiesFrame.setupProperties("{} Properties".format(widget.displayName), element, elementDict)

    def createCustomWidgetMethods(self, widget):
        setattr(self, widget.getPropFunctionName(), self.propertiesMethod)
        setattr(self, widget.getCreateFunctionName(), self.createMethod)

    def createDirectButton(self, parent=None):
        parent = self.getEditorRootCanvas() if parent is None else parent
        pos = self.editorCenter if parent == self.getEditorRootCanvas() else (0,0,0)
        if self.visEditorInAspect2D:
            element = DirectButton(
                text="button",
                parent=parent,
                scale=0.1)
        else:
            element = DirectButton(
                text="button",
                parent=parent,
                pos=pos,
                text_scale=24,
                borderWidth=(2, 2))
        elementInfo = ElementInfo(element, "DirectButton")
        elementInfo.extraOptions["pressEffect"] = element["pressEffect"]
        if self.visEditorInAspect2D:
            elementInfo.valueHasChanged = {
                "pos": True,
                "text": True,
                "scale": True}
        else:
            elementInfo.valueHasChanged = {
                "text": True,
                "text0_scale": True,
                "text1_scale": True,
                "text2_scale": True,
                "text3_scale": True,
                "pos": True,
                "borderWidth": True}
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesDirectButton(self, element, elementDict):
        self.propertiesFrame.setupProperties("Button Properties", element, elementDict)

    def createDirectEntry(self, parent=None):
        parent = self.getEditorRootCanvas() if parent is None else parent
        pos = self.editorCenter if parent == self.getEditorRootCanvas() else (0,0,0)
        if self.visEditorInAspect2D:
            element = DirectEntry(
                parent=parent,
                scale=0.1)
        else:
            element = DirectEntry(
                pos=pos,
                text_scale=1,
                borderWidth=(2/24, 2/24),
                parent=parent,
                scale=24)
        elementInfo = ElementInfo(element, "DirectEntry")
        if self.visEditorInAspect2D:
            elementInfo.valueHasChanged = {
                "pos": True,
                "scale": True}
        else:
            elementInfo.valueHasChanged = {
                "text0_scale": True,
                "pos": True,
                "borderWidth": True,
                "scale": True}
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesDirectEntry(self, element, elementDict):
        self.propertiesFrame.setupProperties("Entry Properties", element, elementDict)

    def createDirectEntryScroll(self, parent=None, createEntry=True):
        parent = self.getEditorRootCanvas() if parent is None else parent
        pos = self.editorCenter if parent == self.getEditorRootCanvas() else (0,0,0)
        if createEntry:
            if self.visEditorInAspect2D:
                entry = DirectEntry()
                element = DirectEntryScroll(
                    entry=entry,
                    parent=parent,
                    scale=0.1)
            else:
                entry = DirectEntry(
                    text_scale=24,
                    borderWidth=(2, 2))
                element = DirectEntryScroll(
                    entry=entry,
                    pos=pos,
                    borderWidth=(2, 2),
                    parent=parent,
                    clipSize=(-50, 50, -25, 25),
                    scale=1)
            elementInfoA = ElementInfo(entry, "DirectEntry")
            elementInfoB = ElementInfo(element, "DirectEntryScroll", createAfter=[elementInfoA])
            elementInfoB.extraOptions["entry"] = "self." + elementInfoA.name
            elementInfoA.parent = elementInfoB
            self.setupBind(elementInfoA, elementInfoB)
            self.setupBind(elementInfoB)
            return elementInfoA, elementInfoB
        else:
            if self.visEditorInAspect2D:
                element = DirectEntryScroll(
                    entry=None,
                    parent=parent,
                    scale=0.1)
            else:
                element = DirectEntryScroll(
                    entry=None,
                    pos=pos,
                    borderWidth=(2, 2),
                    parent=parent,
                    clipSize=(-50, 50, -25, 25))
            elementInfo = ElementInfo(element, "DirectEntryScroll")
        if self.visEditorInAspect2D:
            elementInfo.valueHasChanged = {
                "pos": True,
                "scale": True}
        else:
            elementInfo.valueHasChanged = {
                "clipSize": True,
                "pos": True,
                "borderWidth": True}
            self.setupBind(elementInfo)
            return elementInfo

    def propertiesDirectEntryScroll(self, element, elementDict):
        self.propertiesFrame.setupProperties("Scrolled Entry Properties", element, elementDict)

    def createDirectCheckBox(self, parent=None):
        parent = self.getEditorRootCanvas() if parent is None else parent
        pos = self.editorCenter if parent == self.getEditorRootCanvas() else (0,0,0)
        if self.visEditorInAspect2D:
            element = DirectCheckBox(
                #image="icons/minusnode.gif",
                #uncheckedImage="icons/minusnode.gif",
                #checkedImage="icons/plusnode.gif",
                parent=parent,
                scale=0.1)
        else:
            element = DirectCheckBox(
                pos=pos,
                borderWidth=(2, 2),
                #image="icons/minusnode.gif",
                #uncheckedImage="icons/minusnode.gif",
                #checkedImage="icons/plusnode.gif",
                parent=parent)
        elementInfo = ElementInfo(element, "DirectCheckBox")
        if self.visEditorInAspect2D:
            elementInfo.valueHasChanged = {
                "pos": True,
                "scale": True}
        else:
            elementInfo.valueHasChanged = {
                "pos": True,
                "borderWidth": True}
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesDirectCheckBox(self, element, elementDict):
        self.propertiesFrame.setupProperties("Checkbox Properties", element, elementDict)

    def createDirectCheckButton(self, parent=None):
        parent = self.getEditorRootCanvas() if parent is None else parent
        pos = self.editorCenter if parent == self.getEditorRootCanvas() else (0,0,0)
        if self.visEditorInAspect2D:
            element = DirectCheckButton(
                text="Checkbutton",
                parent=parent,
                scale=0.1)
        else:
            element = DirectCheckButton(
                pos=pos,
                text_scale=24,
                borderWidth=(2, 2),
                text="Checkbutton",
                indicator_text_scale=24,
                indicator_borderWidth=(2, 2),
                parent=parent)

        elementInfo = ElementInfo(element, "DirectCheckButton")
        if self.visEditorInAspect2D:
            elementInfo.valueHasChanged = {
                "pos": True,
                "text": True,
                "scale": True}
        else:
            elementInfo.valueHasChanged = {
                "text": True,
                "text0_scale": True,
                "text1_scale": True,
                "text2_scale": True,
                "text3_scale": True,
                "pos": True,
                "indicator_text_scale": True,
                "indicator_borderWidth": True,
                "borderWidth": True}
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesDirectCheckButton(self, element, elementDict):
        self.propertiesFrame.setupProperties("Check Button Properties", element, elementDict)

    def createDirectOptionMenu(self, parent=None):
        parent = self.getEditorRootCanvas() if parent is None else parent
        pos = self.editorCenter if parent == self.getEditorRootCanvas() else (0,0,0)
        if self.visEditorInAspect2D:
            element = DirectOptionMenu(
                parent=parent,
                items=["item1"],
                scale=0.1)
        else:
            element = DirectOptionMenu(
                pos=pos,
                borderWidth=(2, 2),
                parent=parent,
                items=["item1"],
                scale=24)
        elementInfo = ElementInfo(element, "DirectOptionMenu")
        if self.visEditorInAspect2D:
            elementInfo.valueHasChanged = {
                "pos": True,
                "items": True,
                "scale": True}
        else:
            elementInfo.valueHasChanged = {
                "pos": True,
                "items": True,
                "borderWidth": True,
                "scale": True}
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesDirectOptionMenu(self, element, elementDict):
        self.propertiesFrame.setupProperties("Option Menu Properties", element, elementDict)

    def createDirectRadioButton(self, parent=None):
        parent = self.getEditorRootCanvas() if parent is None else parent
        pos = self.editorCenter if parent == self.getEditorRootCanvas() else (0,0,0)
        if self.visEditorInAspect2D:
            element = DirectRadioButton(
                text="Radiobutton",
                parent=parent,
                scale=0.1)
        else:
            element = DirectRadioButton(
                text="Radiobutton",
                parent=parent,
                pos=pos,
                text_scale=24,
                borderWidth=(2, 2),
                indicator_text_scale=24,
                indicator_borderWidth=(2, 2))
        elementInfo = ElementInfo(element, "DirectRadioButton")

        elementInfo.extraOptions["variable"] = []
        elementInfo.extraOptions["value"] = []

        if self.visEditorInAspect2D:
            elementInfo.valueHasChanged = {
                "pos": True,
                "text": True,
                "scale": True}
        else:
            elementInfo.valueHasChanged = {
                "text": True,
                "text0_scale": True,
                "text1_scale": True,
                "text2_scale": True,
                "text3_scale": True,
                "indicator_text_scale": True,
                "indicator_borderWidth": True,
                "pos": True,
                "borderWidth": True}

        self.setupBind(elementInfo)
        return elementInfo

    def propertiesDirectRadioButton(self, element, elementDict):
        self.propertiesFrame.setupProperties("Radio Button Properties", element, elementDict)

    def createDirectSlider(self, parent=None):
        parent = self.getEditorRootCanvas() if parent is None else parent
        pos = self.editorCenter if parent == self.getEditorRootCanvas() else (0,0,0)
        if self.visEditorInAspect2D:
            element = DirectSlider(
                text="Slider",
                text_scale=0.1,
                parent=parent)
        else:
            element = DirectSlider(
                text="Slider",
                text_scale=0.1,
                parent=parent,
                pos=pos,
                borderWidth=(2, 2),
                scale=150)
        elementInfo = ElementInfo(element, "DirectSlider")
        if self.visEditorInAspect2D:
            elementInfo.valueHasChanged = {
                "pos": True,
                "text": True,
                "text0_scale": True}
        else:
            elementInfo.valueHasChanged = {
                "text": True,
                "text0_scale": True,
                "scale": True,
                "pos": True,
                "borderWidth": True}
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesDirectSlider(self, element, elementDict):
        self.propertiesFrame.setupProperties("Slider Properties", element, elementDict)

    def createDirectScrollBar(self, parent=None):
        parent = self.getEditorRootCanvas() if parent is None else parent
        pos = self.editorCenter if parent == self.getEditorRootCanvas() else (0,0,0)
        if self.visEditorInAspect2D:
            element = DirectScrollBar(
                parent=parent)
        else:
            element = DirectScrollBar(
                pos=pos,
                borderWidth=(2, 2),
                scale=150,
                parent=parent)
        elementInfo = ElementInfo(element, "DirectScrollBar")
        if self.visEditorInAspect2D:
            elementInfo.valueHasChanged = {
                "pos": True}
        else:
            elementInfo.valueHasChanged = {
                "scale": True,
                "pos": True,
                "borderWidth": True}
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesDirectScrollBar(self, element, elementDict):
        self.propertiesFrame.setupProperties("Scroll Bar Properties", element, elementDict)

    def createDirectScrolledList(self, parent=None):
        parent = self.getEditorRootCanvas() if parent is None else parent
        pos = self.editorCenter if parent == self.getEditorRootCanvas() else (0,0,0)
        if self.visEditorInAspect2D:
            element = DirectScrolledList(
                text="scrolled list",
                text_scale=0.1,
                text_pos=(0,0.015),
                state = DGG.NORMAL,

                decButton_pos= (-0.45, 0, 0.03),
                decButton_text = "Prev",
                decButton_text_scale = 0.05,
                decButton_text_align = TextNode.ALeft,
                decButton_borderWidth = (0.005, 0.005),

                incButton_pos= (0.45, 0, 0.03),
                incButton_text = "Next",
                incButton_text_scale = 0.05,
                incButton_text_align = TextNode.ARight,
                incButton_borderWidth = (0.005, 0.005),

                forceHeight=0.1,

                numItemsVisible=5,
                itemFrame_frameSize=(-0.47, 0.47, -0.5, 0.1),
                itemFrame_frameColor=(1, 1, 1, 1),
                frameSize=(-0.5, 0.5, -0.01, 0.75),
                frameColor=(0.8, 0.8, 0.8, 1),
                itemFrame_pos = (0, 0, 0.6),

                parent=parent)
        else:
            element = DirectScrolledList(
                pos=pos,

                text="scrolled list",
                text_scale=24,
                text_pos=(0,-225),
                borderWidth=(2, 2),
                state = DGG.NORMAL,

                decButton_pos= (-125, 0, -225),
                decButton_text = "Prev",
                decButton_text_scale = 24,
                decButton_text_align = TextNode.ALeft,
                decButton_borderWidth = (2, 2),

                incButton_pos= (125, 0, -225),
                incButton_text = "Next",
                incButton_text_scale = 24,
                incButton_text_align = TextNode.ARight,
                incButton_borderWidth = (2, 2),

                forceHeight=50,

                numItemsVisible=5,
                itemFrame_frameSize=(-125, 125, -250, 50),
                itemFrame_frameColor=(1, 1, 1, 1),
                frameSize=(-150, 150, -250, 125),
                frameColor=(0.8, 0.8, 0.8, 1),
                itemFrame_pos = (0, 0, 50),

                parent=parent)
        elementInfo = ElementInfo(element, "DirectScrolledList")

        if self.visEditorInAspect2D:
            elementInfo.valueHasChanged = {
                "pos": True,
                "text": True,
                "text0_scale": True,
                "text_pos": True,
                "state": True,
                "decButton_pos": True,
                "decButton_text": True,
                "decButton_text0_scale": True,
                "decButton_text1_scale": True,
                "decButton_text2_scale": True,
                "decButton_text3_scale": True,
                "decButton_text0_align": True,
                "decButton_text1_align": True,
                "decButton_text2_align": True,
                "decButton_text3_align": True,
                "decButton_borderWidth": True,
                "incButton_pos": True,
                "incButton_text": True,
                "incButton_text0_scale": True,
                "incButton_text1_scale": True,
                "incButton_text2_scale": True,
                "incButton_text3_scale": True,
                "incButton_text0_align": True,
                "incButton_text1_align": True,
                "incButton_text2_align": True,
                "incButton_text3_align": True,
                "incButton_borderWidth": True,
                "forceHeight": True,
                "numItemsVisible": True,
                "itemFrame_frameSize": True,
                "itemFrame_frameColor": True,
                "frameSize": True,
                "frameColor": True,
                "itemFrame_pos": True}
        else:
            elementInfo.valueHasChanged = {
                "pos": True,
                "text": True,
                "text0_scale": True,
                "text_pos": True,
                "state": True,
                "decButton_pos": True,
                "decButton_text": True,
                "decButton_text0_scale": True,
                "decButton_text1_scale": True,
                "decButton_text2_scale": True,
                "decButton_text3_scale": True,
                "decButton_text0_align": True,
                "decButton_text1_align": True,
                "decButton_text2_align": True,
                "decButton_text3_align": True,
                "decButton_borderWidth": True,
                "incButton_pos": True,
                "incButton_text": True,
                "incButton_text0_scale": True,
                "incButton_text1_scale": True,
                "incButton_text2_scale": True,
                "incButton_text3_scale": True,
                "incButton_text0_align": True,
                "incButton_text1_align": True,
                "incButton_text2_align": True,
                "incButton_text3_align": True,
                "incButton_borderWidth": True,
                "forceHeight": True,
                "numItemsVisible": True,
                "itemFrame_frameSize": True,
                "itemFrame_frameColor": True,
                "frameSize": True,
                "frameColor": True,
                "itemFrame_pos": True}
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesDirectScrolledList(self, element, elementDict):
        self.propertiesFrame.setupProperties("Scrolled List Properties", element, elementDict)

    def createDirectScrolledListItem(self, parent=None):
        if parent is None or parent.getName().split("-")[0] != "DirectScrolledList":
            base.messenger.send("showWarning", ["Scrolled List Items must be added to Scrolled Lists.\nPlease select a scrolled list first!"])
            return None
        if self.visEditorInAspect2D:
            element = DirectScrolledListItem(
                text="scrolled list item",
                parent=parent,
                command=base.messenger.send,
                extraArgs=["select_list_item_changed"],
                scale=0.1)
        else:
            element = DirectScrolledListItem(
                text="scrolled list item",
                text_scale=24,
                borderWidth=(2, 2),
                parent=parent,
                command=base.messenger.send,
                extraArgs=["select_list_item_changed"])
        elementInfo = ElementInfo(element, "DirectScrolledListItem")
        elementInfo.command = "base.messenger.send"
        elementInfo.extraArgs = "'select_list_item_changed'"
        if self.visEditorInAspect2D:
            elementInfo.valueHasChanged = {
                "pos": True,
                "text": True,
                "scale": True}
        else:
            elementInfo.valueHasChanged = {
                "text": True,
                "text0_scale": True,
                "text1_scale": True,
                "text2_scale": True,
                "text3_scale": True,
                "borderWidth": True}
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesDirectScrolledListItem(self, element, elementDict):
        self.propertiesFrame.setupProperties("Scrolled List Item Properties", element, elementDict)

    def createDirectLabel(self, parent=None):
        parent = self.getEditorRootCanvas() if parent is None else parent
        pos = self.editorCenter if parent == self.getEditorRootCanvas() else (0,0,0)
        if self.visEditorInAspect2D:
            element = DirectLabel(
                text = "Label",
                parent=parent,
                state = DGG.NORMAL,
                scale=0.1)
        else:
            element = DirectLabel(
                text = "Label",
                parent=parent,
                state = DGG.NORMAL,
                pos=pos,
                text_scale=24,
                borderWidth=(2, 2))
        elementInfo = ElementInfo(element, "DirectLabel")
        if self.visEditorInAspect2D:
            elementInfo.valueHasChanged = {
                "pos": True,
                "text": True,
                "state": True,
                "scale": True}
        else:
            elementInfo.valueHasChanged = {
                "text": True,
                "text0_scale": True,
                "state": True,
                "pos": True,
                "borderWidth": True}
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesDirectLabel(self, element, elementDict):
        self.propertiesFrame.setupProperties("Label Properties", element, elementDict)

    def createDirectWaitBar(self, parent=None):
        parent = self.getEditorRootCanvas() if parent is None else parent
        pos = self.editorCenter if parent == self.getEditorRootCanvas() else (0,0,0)
        if self.visEditorInAspect2D:
            element = DirectWaitBar(
                text="0%",
                text_scale=0.1,
                state = DGG.NORMAL,
                parent=parent)
        else:
            element = DirectWaitBar(
                text="0%",
                text_scale=0.1,
                scale=150,
                pos=pos,
                borderWidth=(2, 2),
                state = DGG.NORMAL,
                parent=parent)
        elementInfo = ElementInfo(element, "DirectWaitBar")
        if self.visEditorInAspect2D:
            elementInfo.valueHasChanged = {
                "pos": True,
                "text": True,
                "text0_scale": True,
                "state": True}
        else:
            elementInfo.valueHasChanged = {
                "text": True,
                "text0_scale": True,
                "scale": True,
                "state": True,
                "pos": True,
                "borderWidth": True}
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesDirectWaitBar(self, element, elementDict):
        self.propertiesFrame.setupProperties("Wait Bar Properties", element, elementDict)

    def createOkDialog(self, parent=None):
        parent = self.getEditorRootCanvas() if parent is None else parent
        pos = self.editorCenter if parent == self.getEditorRootCanvas() else (0,0,0)
        if self.visEditorInAspect2D:
            element = OkDialog(
                text="Ok Dialog",
                state = DGG.NORMAL,
                parent=parent)
        else:
            element = OkDialog(
                text="Ok Dialog",
                state=DGG.NORMAL,
                scale=300,
                pos=pos,
                parent=parent)
        elementInfo = ElementInfo(element, "OkDialog")
        if self.visEditorInAspect2D:
            elementInfo.valueHasChanged = {
                "pos": True,
                "text": True,
                "state": True}
        else:
            elementInfo.valueHasChanged = {
                "text": True,
                "state": True,
                "scale": True,
                "pos": True}
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesOkDialog(self, element, elementDict):
        self.propertiesFrame.setupProperties("Ok Dialog Properties", element, elementDict)

    def createOkCancelDialog(self, parent=None):
        parent = self.getEditorRootCanvas() if parent is None else parent
        pos = self.editorCenter if parent == self.getEditorRootCanvas() else (0,0,0)
        if self.visEditorInAspect2D:
            element = OkCancelDialog(
                text="Ok/Cancel Dialog",
                state = DGG.NORMAL,
                parent=parent)
        else:
            element = OkCancelDialog(
                text="Ok/Cancel Dialog",
                state=DGG.NORMAL,
                scale=300,
                pos=pos,
                parent=parent)

        elementInfo = ElementInfo(element, "OkCancelDialog")
        if self.visEditorInAspect2D:
            elementInfo.valueHasChanged = {
                "pos": True,
                "text": True,
                "state": True}
        else:
            elementInfo.valueHasChanged = {
                "text": True,
                "state": True,
                "scale": True,
                "pos": True}
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesOkCancelDialog(self, element, elementDict):
        self.propertiesFrame.setupProperties("Ok Cancel Dialog Properties", element, elementDict)

    def createYesNoDialog(self, parent=None):
        parent = self.getEditorRootCanvas() if parent is None else parent
        pos = self.editorCenter if parent == self.getEditorRootCanvas() else (0,0,0)
        if self.visEditorInAspect2D:
            element = YesNoDialog(
                text="Yes/No Dialog",
                state = DGG.NORMAL,
                parent=parent)
        else:
            element = YesNoDialog(
                text="Yes/No Dialog",
                state=DGG.NORMAL,
                scale=300,
                pos=pos,
                parent=parent)
        elementInfo = ElementInfo(element, "YesNoDialog")
        if self.visEditorInAspect2D:
            elementInfo.valueHasChanged = {
                "pos": True,
                "text": True,
                "state": True}
        else:
            elementInfo.valueHasChanged = {
                "text": True,
                "state": True,
                "scale": True,
                "pos": True}
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesYesNoDialog(self, element, elementDict):
        self.propertiesFrame.setupProperties("Yes No Dialog Properties", element, elementDict)

    def createYesNoCancelDialog(self, parent=None):
        if self.visEditorInAspect2D:
            element = YesNoCancelDialog(
                text="Yes/No/Cancel Dialog",
                state = DGG.NORMAL,
                parent=self.getEditorRootCanvas())
        else:
            element = YesNoCancelDialog(
                text="Yes/No/Cancel Dialog",
                state=DGG.NORMAL,
                scale=300,
                pos=self.editorCenter,
                parent=self.getEditorRootCanvas())
        elementInfo = ElementInfo(element, "YesNoCancelDialog")
        if self.visEditorInAspect2D:
            elementInfo.valueHasChanged = {
                "pos": True,
                "text": True,
                "state": True}
        else:
            elementInfo.valueHasChanged = {
                "text": True,
                "state": True,
                "scale": True,
                "pos": True}
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesYesNoCancelDialog(self, element, elementDict):
        self.propertiesFrame.setupProperties("Yes No Cancel Dialog Properties", element, elementDict)

    def createRetryCancelDialog(self, parent=None):
        parent = self.getEditorRootCanvas() if parent is None else parent
        pos = self.editorCenter if parent == self.getEditorRootCanvas() else (0,0,0)
        if self.visEditorInAspect2D:
            element = RetryCancelDialog(
                text="Retry/Cancel Dialog",
                state = DGG.NORMAL,
                parent=parent)
        else:
            element = RetryCancelDialog(
                text="Retry/Cancel Dialog",
                state=DGG.NORMAL,
                scale=300,
                pos=pos,
                parent=parent)
        elementInfo = ElementInfo(element, "RetryCancelDialog")
        if self.visEditorInAspect2D:
            elementInfo.valueHasChanged = {
                "pos": True,
                "text": True,
                "state": True}
        else:
            elementInfo.valueHasChanged = {
                "text": True,
                "state": True,
                "scale": True,
                "pos": True}
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesRetryCancelDialog(self, element, elementDict):
        self.propertiesFrame.setupProperties("Retry Cancel Dialog Properties", element, elementDict)

    def createDirectFrame(self, parent=None):
        parent = self.getEditorRootCanvas() if parent is None else parent
        pos = self.editorCenter if parent == self.getEditorRootCanvas() else (0,0,0)
        if self.visEditorInAspect2D:
            element = DirectFrame(
                frameColor=(1,1,1,1),
                frameSize=(-1,1,-1,1),
                parent=parent,
                state = DGG.NORMAL)
        else:
            element = DirectFrame(
                frameColor=(1,1,1,1),
                text_scale=24,
                frameSize=(-150, 150, -150, 150),
                pos=pos,
                borderWidth=(2, 2),
                parent=parent,
                state = DGG.NORMAL)
        elementInfo = ElementInfo(element, "DirectFrame")
        if self.visEditorInAspect2D:
            elementInfo.valueHasChanged = {
                "pos": True,
                "frameColor": True,
                "frameSize": True,
                "state": True}
        else:
            elementInfo.valueHasChanged = {
                "frameColor": True,
                "text0_scale": True,
                "frameSize": True,
                "state": True,
                "borderWidth": True,
                "pos": True}
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesDirectFrame(self, element, elementDict):
        self.propertiesFrame.setupProperties("Frame Properties", element, elementDict)

    def createDirectScrolledFrame(self, parent=None):
        parent = self.getEditorRootCanvas() if parent is None else parent
        pos = self.editorCenter if parent == self.getEditorRootCanvas() else (0,0,0)
        if self.visEditorInAspect2D:
            element = DirectScrolledFrame(
                frameColor=(1,1,1,1),
                frameSize=(-1,1,-1,1),
                canvasSize=(-2,2,-2,2),
                parent=parent,
                state = DGG.NORMAL)
        else:
            element = DirectScrolledFrame(
                frameColor=(1,1,1,1),
                text_scale=24,
                frameSize=(-150, 150, -150, 150),
                pos=pos,
                borderWidth=(2, 2),
                canvasSize=(-300,300,-300,300),
                scrollBarWidth=20,
                parent=parent,
                state = DGG.NORMAL)
        elementInfo = ElementInfo(element, "DirectScrolledFrame")
        if self.visEditorInAspect2D:
            elementInfo.valueHasChanged = {
                "pos": True,
                "frameColor": True,
                "frameSize": True,
                "canvasSize": True,
                "state": True}
        else:
            elementInfo.valueHasChanged = {
                "frameColor": True,
                "text0_scale": True,
                "canvasSize": True,
                "frameSize": True,
                "scrollBarWidth": True,
                "state": True,
                "borderWidth": True,
                "pos": True}
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesDirectScrolledFrame(self, element, elementDict):
        self.propertiesFrame.setupProperties("Scrolled Frame Properties", element, elementDict)
