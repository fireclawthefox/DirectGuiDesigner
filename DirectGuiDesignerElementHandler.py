#!/usr/bin/env python
# -*- coding: utf-8 -*-
from direct.gui import DirectGuiGlobals as DGG

from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectScrolledFrame import DirectScrolledFrame
from direct.gui.DirectEntry import DirectEntry
#from direct.gui.DirectEntryScroll import DirectEntryScroll
from DirectEntryScroll import DirectEntryScroll
from direct.gui.DirectCheckBox import DirectCheckBox
from direct.gui.DirectCheckButton import DirectCheckButton
#from direct.gui.DirectOptionMenu import DirectOptionMenu
from DirectOptionMenu import DirectOptionMenu
from direct.gui.DirectRadioButton import DirectRadioButton
from direct.gui.DirectSlider import DirectSlider
from direct.gui.DirectScrollBar import DirectScrollBar
from direct.gui.DirectScrolledList import DirectScrolledList
from direct.gui.DirectScrolledList import DirectScrolledListItem
from direct.gui.DirectWaitBar import DirectWaitBar
from direct.gui.DirectDialog import OkDialog
from direct.gui.DirectDialog import OkCancelDialog
from direct.gui.DirectDialog import YesNoDialog
from direct.gui.DirectDialog import YesNoCancelDialog
from direct.gui.DirectDialog import RetryCancelDialog

from panda3d.core import TextNode

class ElementInfo:
    # The actual GUI element
    element = None
    # Name of the element type
    elementType = None
    # The ElementInfo of the Parent of this element
    parentElement = None
    # The command to be called by the element
    command = None
    extraArgs = None

    def __init__(self, element, elementType, parentElement = None):
        self.element = element
        self.elementType = elementType
        self.parentElement = parentElement

class DirectGuiDesignerElementHandler:
    def __init__(self, propertiesFrame, visualEditor):
        self.propertiesFrame = propertiesFrame
        self.visualEditor = visualEditor

    def dragStart(self, elementInfo, event):
        base.messenger.send("dragStart", [elementInfo, event])

    def dragStop(self, event):
        base.messenger.send("dragStop", [event])

    def setupBind(self, elementInfo, PassedElementInfo=None):
        elementInfo.element.bind(DGG.B1PRESS, self.dragStart, [PassedElementInfo if PassedElementInfo is not None else elementInfo])
        elementInfo.element.bind(DGG.B1RELEASE, self.dragStop)

    def createDirectButton(self, parent=None):
        element = DirectButton(
            text="button",
            parent=parent if parent is not None else self.visualEditor.getCanvas(),
            scale=0.1)
        elementInfo = ElementInfo(element, "DirectButton")
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesDirectButton(self, element, elementDict):
        self.propertiesFrame.defaultPropertySelection()
        self.propertiesFrame.defaultTextPropertySelection()
        self.propertiesFrame.propertyList["command"] = True
        self.propertiesFrame.propertyList["image"] = True
        self.propertiesFrame.setupProperties("Button Properties", element, elementDict)

    def createDirectEntry(self, parent=None):
        element = DirectEntry(
            parent=parent if parent is not None else self.visualEditor.getCanvas(),
            scale=0.1)
        elementInfo = ElementInfo(element, "DirectEntry")
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesDirectEntry(self, element, elementDict):
        self.propertiesFrame.defaultPropertySelection()
        self.propertiesFrame.propertyList["command"] = True
        self.propertiesFrame.propertyList["initialText"] = True
        self.propertiesFrame.propertyList["width"] = True
        self.propertiesFrame.propertyList["numLines"] = True
        self.propertiesFrame.propertyList["overflow"] = True
        self.propertiesFrame.propertyList["obscured"] = True
        self.propertiesFrame.setupProperties("Entry Properties", element, elementDict)

    def createDirectEntryScroll(self, parent=None, createEntry=True):
        if createEntry:
            entry = DirectEntry(
                parent=self.visualEditor.getCanvas())
            element = DirectEntryScroll(
                entry=entry,
                parent=parent if parent is not None else self.visualEditor.getCanvas(),
                scale=0.1)
            elementInfoB = ElementInfo(element, "DirectEntryScroll")
            elementInfoA = ElementInfo(entry, "DirectEntry", elementInfoB)
            self.setupBind(elementInfoA, elementInfoB)
            self.setupBind(elementInfoB)
            return elementInfoA, elementInfoB
        else:
            element = DirectEntryScroll(
                entry=None,
                parent=parent if parent is not None else self.visualEditor.getCanvas(),
                scale=0.1)
            elementInfo = ElementInfo(element, "DirectEntryScroll")
            self.setupBind(elementInfo)
            return elementInfo

    def propertiesDirectEntryScroll(self, element, elementDict):
        self.propertiesFrame.defaultPropertySelection()
        self.propertiesFrame.propertyList["clipSize"] = True
        self.propertiesFrame.setupProperties("Scrolled Entry Properties", element, elementDict)

    def createDirectCheckBox(self, parent=None):
        element = DirectCheckBox(
            #image="icons/minusnode.gif",
            #uncheckedImage="icons/minusnode.gif",
            #checkedImage="icons/plusnode.gif",
            parent=parent if parent is not None else self.visualEditor.getCanvas(),
            scale=0.1)
        elementInfo = ElementInfo(element, "DirectCheckBox")
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesDirectCheckBox(self, element, elementDict):
        self.propertiesFrame.defaultPropertySelection()
        self.propertiesFrame.propertyList["command"] = True
        self.propertiesFrame.propertyList["text"] = True
        self.propertiesFrame.propertyList["text_align"] = True
        self.propertiesFrame.propertyList["image"] = True
        self.propertiesFrame.setupProperties("Checkbox Properties", element, elementDict)

    def createDirectCheckButton(self, parent=None):
        element = DirectCheckButton(
            text="Checkbutton",
            parent=parent if parent is not None else self.visualEditor.getCanvas(),
            scale=0.1)
        elementInfo = ElementInfo(element, "DirectCheckButton")
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesDirectCheckButton(self, element, elementDict):
        self.propertiesFrame.defaultPropertySelection()
        self.propertiesFrame.defaultTextPropertySelection()
        self.propertiesFrame.propertyList["command"] = True
        self.propertiesFrame.propertyList["image"] = True
        self.propertiesFrame.setupProperties("Check Button Properties", element, elementDict)

    def createDirectOptionMenu(self, parent=None):
        element = DirectOptionMenu(
            parent=parent if parent is not None else self.visualEditor.getCanvas(),
            items=["item1"],
            scale=0.1)
        elementInfo = ElementInfo(element, "DirectOptionMenu")
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesDirectOptionMenu(self, element, elementDict):
        self.propertiesFrame.defaultPropertySelection()
        self.propertiesFrame.defaultTextPropertySelection()
        self.propertiesFrame.propertyList["command"] = True
        self.propertiesFrame.propertyList["image"] = True
        self.propertiesFrame.setupProperties("Option Menu Properties", element, elementDict)

    def createDirectRadioButton(self, parent=None):
        element = DirectRadioButton(
            text="Radiobutton",
            parent=parent if parent is not None else self.visualEditor.getCanvas(),
            scale=0.1)
        elementInfo = ElementInfo(element, "DirectRadioButton")
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesDirectRadioButton(self, element, elementDict):
        self.propertiesFrame.defaultPropertySelection()
        self.propertiesFrame.defaultTextPropertySelection()
        self.propertiesFrame.propertyList["command"] = True
        self.propertiesFrame.propertyList["image"] = True
        self.propertiesFrame.setupProperties("Radio Button Properties", element, elementDict)

    def createDirectSlider(self, parent=None):
        element = DirectSlider(
            text="Slider",
            text_scale=0.1,
            parent=self.visualEditor.getCanvas())
        elementInfo = ElementInfo(element, "DirectSlider")
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesDirectSlider(self, element, elementDict):
        self.propertiesFrame.defaultPropertySelection()
        self.propertiesFrame.defaultTextPropertySelection()
        self.propertiesFrame.propertyList["command"] = True
        self.propertiesFrame.propertyList["image"] = True
        self.propertiesFrame.setupProperties("Slider Properties", element, elementDict)

    def createDirectScrollBar(self, parent=None):
        element = DirectScrollBar(
            parent=self.visualEditor.getCanvas())
        elementInfo = ElementInfo(element, "DirectScrollBar")
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesDirectScrollBar(self, element, elementDict):
        self.propertiesFrame.defaultPropertySelection()
        self.propertiesFrame.propertyList["command"] = True
        self.propertiesFrame.propertyList["text"] = True
        self.propertiesFrame.propertyList["text_align"] = True
        self.propertiesFrame.propertyList["image"] = True
        self.propertiesFrame.setupProperties("Scroll Bar Properties", element, elementDict)

    def createDirectScrolledList(self, parent=None):
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

            parent=self.visualEditor.getCanvas())
        elementInfo = ElementInfo(element, "DirectScrolledList")
        element["incButton_pos"] = (-0.35, 0, 0.03)
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesDirectScrolledList(self, element, elementDict):
        self.propertiesFrame.defaultPropertySelection()
        self.propertiesFrame.defaultTextPropertySelection()
        self.propertiesFrame.propertyList["image"] = True
        for key in self.propertiesFrame.propertyList.keys():
            if key.startswith("incButton") or key.startswith("decButton"):
                self.propertiesFrame.propertyList[key] = True
        self.propertiesFrame.setupProperties("Scrolled List Properties", element, elementDict)

    def directScrolledListItemInfoDialog_close(self, args):
        self.directScrolledListItemInfoDialog.destroy()
        directScrolledListItemInfoDialog = None
        self.directScrolledListItemInfoDialogShadow.destroy()
        self.directScrolledListItemInfoDialogShadow = None

    def createDirectScrolledListItem(self, parent=None):
        if parent is None or parent.getName().split("-")[0] != "DirectScrolledList":
            self.directScrolledListItemInfoDialog = OkDialog(
                text="Scrolled List Items must be added to Scrolled Lists.\nPlease select a scrolled list first!",
                state=DGG.NORMAL,
                relief=DGG.FLAT,
                frameColor=(1,1,1,1),
                button_relief=1,
                button_frameColor=(0.8, 0.8, 0.8, 1),
                command=self.directScrolledListItemInfoDialog_close)
            self.directScrolledListItemInfoDialogShadow = DirectFrame(
                pos=(0.025, 0, -0.025),
                sortOrder=0,
                frameColor=(0,0,0,0.5),
                frameSize=self.directScrolledListItemInfoDialog.bounds)
            return None
        element = DirectScrolledListItem(
            text="scrolled list item",
            parent=parent if parent is not None else self.visualEditor.getCanvas(),
            command=base.messenger.send,
            extraArgs=["select_list_item_changed"],
            scale=0.1)
        elementInfo = ElementInfo(element, "DirectScrolledListItem")
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesDirectScrolledListItem(self, element, elementDict):
        self.propertiesFrame.defaultPropertySelection()
        self.propertiesFrame.defaultTextPropertySelection()
        self.propertiesFrame.propertyList["image"] = True
        self.propertiesFrame.setupProperties("Scrolled List Item Properties", element, elementDict)

    def createDirectLabel(self, parent=None):
        element = DirectLabel(
            text = "Label",
            parent=parent if parent is not None else self.visualEditor.getCanvas(),
            state = DGG.NORMAL,
            scale=0.1)
        elementInfo = ElementInfo(element, "DirectLabel")
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesDirectLabel(self, element, elementDict):
        self.propertiesFrame.defaultPropertySelection()
        self.propertiesFrame.defaultTextPropertySelection()
        self.propertiesFrame.propertyList["image"] = True
        self.propertiesFrame.setupProperties("Label Properties", element, elementDict)

    def createDirectWaitBar(self, parent=None):
        element = DirectWaitBar(
            text="0%",
            text_scale=0.1,
            state = DGG.NORMAL,
            parent=self.visualEditor.getCanvas())
        elementInfo = ElementInfo(element, "DirectWaitBar")
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesDirectWaitBar(self, element, elementDict):
        self.propertiesFrame.defaultPropertySelection()
        self.propertiesFrame.defaultTextPropertySelection()
        self.propertiesFrame.propertyList["image"] = True
        self.propertiesFrame.setupProperties("Wait Bar Properties", element, elementDict)

    def createOkDialog(self, parent=None):
        element = OkDialog(
            text="Ok Dialog",
            state = DGG.NORMAL,
            parent=self.visualEditor.getCanvas())
        elementInfo = ElementInfo(element, "OkDialog")
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesOkDialog(self, element, elementDict):
        self.propertiesFrame.defaultPropertySelection()
        self.propertiesFrame.defaultTextPropertySelection()
        self.propertiesFrame.propertyList["command"] = True
        self.propertiesFrame.propertyList["image"] = True
        self.propertiesFrame.setupProperties("Ok Dialog Properties", element, elementDict)

    def createOkCancelDialog(self, parent=None):
        element = OkCancelDialog(
            text="Ok/Cancel Dialog",
            state = DGG.NORMAL,
            parent=self.visualEditor.getCanvas())
        elementInfo = ElementInfo(element, "OkCancelDialog")
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesOkCancelDialog(self, element, elementDict):
        self.propertiesFrame.defaultPropertySelection()
        self.propertiesFrame.defaultTextPropertySelection()
        self.propertiesFrame.propertyList["command"] = True
        self.propertiesFrame.propertyList["image"] = True
        self.propertiesFrame.setupProperties("Ok Cancel Dialog Properties", element, elementDict)

    def createYesNoDialog(self, parent=None):
        element = YesNoDialog(
            text="Yes/No Dialog",
            state = DGG.NORMAL,
            parent=self.visualEditor.getCanvas())
        elementInfo = ElementInfo(element, "YesNoDialog")
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesYesNoDialog(self, element, elementDict):
        self.propertiesFrame.defaultPropertySelection()
        self.propertiesFrame.defaultTextPropertySelection()
        self.propertiesFrame.propertyList["command"] = True
        self.propertiesFrame.propertyList["image"] = True
        self.propertiesFrame.setupProperties("Yes No Dialog Properties", element, elementDict)

    def createYesNoCancelDialog(self, parent=None):
        element = YesNoCancelDialog(
            text="Yes/No/Cancel Dialog",
            state = DGG.NORMAL,
            parent=self.visualEditor.getCanvas())
        elementInfo = ElementInfo(element, "YesNoCancelDialog")
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesYesNoCancelDialog(self, element, elementDict):
        self.propertiesFrame.defaultPropertySelection()
        self.propertiesFrame.defaultTextPropertySelection()
        self.propertiesFrame.propertyList["command"] = True
        self.propertiesFrame.propertyList["image"] = True
        self.propertiesFrame.setupProperties("Yes No Cancel Dialog Properties", element, elementDict)

    def createRetryCancelDialog(self, parent=None):
        element = RetryCancelDialog(
            text="Retry/Cancel Dialog",
            state = DGG.NORMAL,
            parent=self.visualEditor.getCanvas())
        elementInfo = ElementInfo(element, "RetryCancelDialog")
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesRetryCancelDialog(self, element, elementDict):
        self.propertiesFrame.defaultPropertySelection()
        self.propertiesFrame.defaultTextPropertySelection()
        self.propertiesFrame.propertyList["command"] = True
        self.propertiesFrame.propertyList["image"] = True
        self.propertiesFrame.setupProperties("Retry Cancel Dialog Properties", element, elementDict)

    def createDirectFrame(self, parent=None):
        element = DirectFrame(
            frameColor=(1,1,1,1),
            frameSize=(-1,1,-1,1),
            parent=parent if parent is not None else self.visualEditor.getCanvas(),
            state = DGG.NORMAL,
            scale=1)
        elementInfo = ElementInfo(element, "DirectFrame")
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesDirectFrame(self, element, elementDict):
        self.propertiesFrame.defaultPropertySelection()
        self.propertiesFrame.setupProperties("Frame Properties", element, elementDict)

    def createDirectScrolledFrame(self, parent=None):
        element = DirectScrolledFrame(
            frameColor=(1,1,1,1),
            frameSize=(-1,1,-1,1),
            canvasSize=(-2,2,-2,2),
            parent=parent if parent is not None else self.visualEditor.getCanvas(),
            state = DGG.NORMAL,
            scale=0.1)
        elementInfo = ElementInfo(element, "DirectScrolledFrame")
        self.setupBind(elementInfo)
        return elementInfo

    def propertiesDirectScrolledFrame(self, element, elementDict):
        self.propertiesFrame.defaultPropertySelection()
        self.propertiesFrame.propertyList["canvasSize"] = True
        self.propertiesFrame.setupProperties("Scrolled Frame Properties", element, elementDict)
