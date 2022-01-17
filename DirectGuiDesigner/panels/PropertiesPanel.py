#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

import logging, sys

from panda3d.core import (
    VBase4,
    LVecBase4f,
    TextNode,
    Point3,
    TextProperties,
    TransparencyAttrib,
    PGButton,
    PGFrameStyle,
    MouseButton,
    NodePath,
    ConfigVariableString)

from direct.gui import DirectGuiGlobals as DGG
DGG.BELOW = "below"
MWUP = PGButton.getPressPrefix() + MouseButton.wheel_up().getName() + '-'
MWDOWN = PGButton.getPressPrefix() + MouseButton.wheel_down().getName() + '-'
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectScrolledFrame import DirectScrolledFrame
from direct.gui.DirectEntry import DirectEntry
from direct.gui.DirectButton import DirectButton
#from direct.gui.DirectOptionMenu import DirectOptionMenu
from directGuiOverrides.DirectOptionMenu import DirectOptionMenu
from direct.gui.DirectCheckButton import DirectCheckButton

from DirectFolderBrowser.DirectFolderBrowser import DirectFolderBrowser

from DirectGuiExtension import DirectGuiHelper as DGH
from DirectGuiExtension.DirectBoxSizer import DirectBoxSizer
from DirectGuiExtension.DirectAutoSizer import DirectAutoSizer

class PropertyInfo:
    def __init__(self, displayName, propertyName, propertyType, customCommandName, customSelectionDict):
        self.displayName = displayName
        self.propertyName = propertyName
        self.propertyType = propertyType
        self.customCommandName = customCommandName
        self.customSelectionDict = customSelectionDict

class PropertiesPanel():

    propertyList = {
        "name":False, # text
        "parent":False, # option menu
        "relief":False, # option menu
        "borderWidth":False, # base2
        "frameSize":False, # base4
        "frameColor":False, # base4
        "pad":False, # base2
        "pos":False, # base3
        "hpr":False, # base3
        "scale":False, # base4
        "color":False, # base4
        "text":False, # text
        "text_align":False, # option menu
        "text_scale":False, # base4
        "text_font":False, # text
        "text_pos":False, # base3
        "text_fg":False, # base4
        "text_bg":False, # base4
        "text_wordwrap":False, # float
        "image":False, # text
        "image_scale":False, # base3
        "image_pos":False, # base3
        "sortOrder":False, # int
        "enableTransparency":False, # bool
        "state":False, # option menu

        "command":False, # text

        # Button specific
        "pressEffect":False, # bool

        # Entry specific
        "initialText":False, # text
        "width":False, # float
        "numLines":False, # int
        "overflow":False, # bool
        "obscured":False, # bool

        # Scrolled Frame specific
        "canvasSize":False, # base4
        "scrollBarWidth":False, # float

        # Scrolled Entry specific
        "clipSize":False, # base4

        # Checkbox specific
        "uncheckedImage":False, # text
        "checkedImage":False, # text
        "isChecked":False, # bool

        # Sub Control specific
        "incButton_pos":False,
        "incButton_hpr":False,
        "incButton_scale":False,
        "incButton_frameColor":False,
        "incButton_frameSize":False,
        "incButton_image":False,
        "incButton_image_scale":False,
        "decButton_pos":False,
        "decButton_hpr":False,
        "decButton_scale":False,
        "decButton_frameColor":False,
        "decButton_frameSize":False,
        "decButton_image":False,
        "decButton_image_scale":False,
        "thumb_pos":False,
        "thumb_hpr":False,
        "thumb_scale":False,
        "thumb_frameColor":False,
        "thumb_frameSize":False,
        "thumb_image":False,
        "thumb_image_scale":False,

        # CheckButton specific
        "boxBorder":False,
        "boxPlacement":False,
        "boxImage":False,
        "boxImageScale":False,
        "boxImageColor":False,
        "boxRelief":False,
        "indicator_text_scale":False,
        "indicator_text_pos":False,
        "indicator_borderWidth":False,

        # RadioButton specific
        "others":False,
        "indicatorValue":False,

        # OptionMenu specific
        "popupMarkerBorder":False,
        "popupMarker_pos":False,
        "popupMenuLocation":False,
        "highlightColor":False,
        "highlightScale":False,

        # ScrollBar specific
        "SB-range":False,
        "value":False,
        "scrollSize":False,
        "pageSize":False,
        "orientation":False,
        "manageButtons":False,
        "resizeThumb":False,

        # WaitBar specific
        "range":False,
        "value":False,
        "barBorderWidth":False,
        "barColor":False,
        "barTexture":False,
        "barRelief":False,
    }
    initOpDict = {
        "pos":"setPos",
        "hpr":"setHpr",
        "scale":"setScale",
        "color":"setColor",
        "text":"setText",

        # Entry specific
        "initialText":"set",
    }
    initOpGetDict = {
        "pos":"getPos",
        "hpr":"getHpr",
        "scale":"getScale",
        "color":"getColor",
        #"frameSize":"getBounds",

        # Entry specific
        "initialText":"get",
    }
    getAsPropDict = {
        "text_fg":"fg",
        "text_bg":"bg",
    }
    subControlInitOpGetDict = {
        "text_frameSize":["text", "getBounds"],

        "incButton_pos":["incButton", "getPos"],
        "incButton_hpr":["incButton", "getHpr"],
        "incButton_scale":["incButton", "getScale"],
        "incButton_frameSize":["incButton", "getBounds"],

        "decButton_pos":["decButton", "getPos"],
        "decButton_hpr":["decButton", "getHpr"],
        "decButton_scale":["decButton", "getScale"],
        "decButton_frameSize":["decButton", "getBounds"],

        "thumb_pos":["thumb", "getPos"],
        "thumb_hpr":["thumb", "getHpr"],
        "thumb_scale":["thumb", "getScale"],
        "thumb_frameSize":["thumb", "getBounds"],
    }
    subControlInitOpDict = {
        "incButton_pos":["incButton", "setPos"],
        "incButton_hpr":["incButton", "setHpr"],
        "incButton_scale":["incButton", "setScale"],
        "incButton_text":["incButton", "setText"],

        "decButton_pos":["decButton", "setPos"],
        "decButton_hpr":["decButton", "setHpr"],
        "decButton_scale":["decButton", "setScale"],
        "decButton_text":["thumb", "setText"],

        "thumb_pos":["thumb", "setPos"],
        "thumb_hpr":["thumb", "setHpr"],
        "thumb_scale":["thumb", "setScale"],
        "thumb_text":["thumb", "setText"],
    }
    # Call a function instead of directly set the option
    callFunc = {
        "isChecked":["commandFunc",None]
    }

    scrollSpeedUp = -0.001
    scrollSpeedDown = 0.001

    def __init__(self, parent, getEditorRootCanvas, getEditorPlacer, tooltip):
        height = DGH.getRealHeight(parent)
        # A list containing the prooperty information
        self.customProperties = []
        self.tooltip = tooltip
        self.parent = parent
        self.maxElementWidth = 0

        self.box = DirectBoxSizer(
            frameColor=(0.25, 0.25, 0.25, 1),
            autoUpdateFrameSize=False,
            orientation=DGG.VERTICAL)
        self.sizer = DirectAutoSizer(
            parent=parent,
            child=self.box,
            childUpdateSizeFunc=self.box.refresh)

        self.lblHeader = DirectLabel(
            text="Properties",
            text_scale=16,
            text_align=TextNode.ALeft,
            text_fg=(1,1,1,1),
            frameColor=VBase4(0, 0, 0, 0),
            )
        self.box.addItem(self.lblHeader)

        color = (
            (0.8, 0.8, 0.8, 1), # Normal
            (0.9, 0.9, 1, 1), # Click
            (0.8, 0.8, 1, 1), # Hover
            (0.5, 0.5, 0.5, 1)) # Disabled
        self.propertiesFrame = DirectScrolledFrame(
            # make the frame fit into our background frame
            frameSize=VBase4(
                self.parent["frameSize"][0], self.parent["frameSize"][1],
                self.parent["frameSize"][2]+DGH.getRealHeight(self.lblHeader), self.parent["frameSize"][3]),
            # set the frames color to transparent
            frameColor=VBase4(1, 1, 1, 1),
            scrollBarWidth=20,
            verticalScroll_scrollSize=20,
            verticalScroll_thumb_relief=DGG.FLAT,
            verticalScroll_incButton_relief=DGG.FLAT,
            verticalScroll_decButton_relief=DGG.FLAT,
            verticalScroll_thumb_frameColor=color,
            verticalScroll_incButton_frameColor=color,
            verticalScroll_decButton_frameColor=color,
            horizontalScroll_thumb_relief=DGG.FLAT,
            horizontalScroll_incButton_relief=DGG.FLAT,
            horizontalScroll_decButton_relief=DGG.FLAT,
            horizontalScroll_thumb_frameColor=color,
            horizontalScroll_incButton_frameColor=color,
            horizontalScroll_decButton_frameColor=color,
            state=DGG.NORMAL)
        self.box.addItem(self.propertiesFrame)
        self.propertiesFrame.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        self.propertiesFrame.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])

        self.getEditorRootCanvas = getEditorRootCanvas
        self.getEditorPlacer = getEditorPlacer

    def scroll(self, scrollStep, event):
        self.propertiesFrame.verticalScroll.scrollStep(scrollStep)

    def resizeFrame(self):
        self.sizer.refresh()
        self.propertiesFrame["frameSize"] = (
                self.parent["frameSize"][0], self.parent["frameSize"][1],
                self.parent["frameSize"][2]+DGH.getRealHeight(self.lblHeader), self.parent["frameSize"][3])

        # refresh properties
        self.clear()
        self.setupProperties(self.headerText, self.elementInfo, self.elementDict)

    def defaultPropertySelection(self):
        self.clearPropertySelection()
        trueValues = ["name", "parent", "relief", "borderWidth", "frameSize",
            "frameColor", "pad", "pos", "hpr", "scale", "sortOrder",
            "enableTransparency", "state", "image", "image_scale", "image_pos"]
        for value in trueValues:
            self.propertyList[value] = True

    def defaultTextPropertySelection(self):
        for key in self.propertyList.keys():
            if key.startswith("text"):
                self.propertyList[key] = True

    def clearPropertySelection(self):
        for key in self.propertyList.keys():
            self.propertyList[key] = False
        self.customProperties = []

    def moveNext(self):
        self.startPos.setZ(self.startPos.getZ() - 15)
        self.frameSize += 60

    def setupProperties(self, headerText, elementInfo, elementDict):
        self.headerText = headerText
        self.elementInfo = elementInfo
        self.elementDict = elementDict
        propFrame = DirectFrame(
            frameSize=(self.propertiesFrame["frameSize"][0], self.propertiesFrame["frameSize"][1]-20, -50, 0.0),
            frameColor=VBase4(0,0,0,0),
            parent=self.propertiesFrame.getCanvas())
        DirectLabel(
            text=headerText,
            text_scale=18,
            text_pos=(-10, 0),
            text_align=TextNode.ACenter,
            frameSize=VBase4(-self.propertiesFrame["frameSize"][1], self.propertiesFrame["frameSize"][1], -10, 20),
            frameColor=VBase4(0.7,0.7,0.7,1),
            pos=(0,0,-20),
            parent=propFrame)
        self.startPos = Point3(self.propertiesFrame["frameSize"][0], 0, -30)
        self.frameSize = 30

        element = elementInfo.element

        try:
            #
            # General Properties
            #
            self.__createInbetweenHeader(
                "General Properties", self.startPos, propFrame,
                ["name", "parent"])
            self.frameSize += 30
            if self.propertyList["name"]:
                self.__createNameProperty(self.startPos, propFrame, elementInfo)
                self.moveNext()
            if self.propertyList["parent"]:
                self.__createParentProperty(self.startPos, propFrame, elementInfo)
                self.moveNext()
            self.__createInbetweenHeader(
                "Text Properties", self.startPos, propFrame,
                ["text", "text_align", "text_scale", "text_font", "text_fg",
                "text_bg", "text_pos", "text_wordwrap"])
            self.frameSize += 30
            if self.propertyList["text"]:
                self.__createTextProperty("Text", self.startPos, propFrame, element, "text")
                self.moveNext()
            if self.propertyList["text_align"]:
                self.__createTextAlignProperty(self.startPos, propFrame, element)
                self.moveNext()
            if self.propertyList["text_scale"]:
                self.__createBaseNInput("Text Scale", self.startPos, propFrame, element, "text_scale", 2)
                self.moveNext()
            if self.propertyList["text_font"]:
                self.__createFontProperty("Font", self.startPos, propFrame, element)
                self.moveNext()
            if self.propertyList["text_fg"]:
                self.__createBaseNInput("Text Color (r/g/b/a)", self.startPos, propFrame, element, "text_fg", 4)
                self.moveNext()
            if self.propertyList["text_bg"]:
                self.__createBaseNInput("Text Background Color (r/g/b/a)", self.startPos, propFrame, element, "text_bg", 4)
                self.moveNext()
            if self.propertyList["text_pos"]:
                self.__createBaseNInput("Text Position (X/Y)", self.startPos, propFrame, element, "text_pos", 2)
                self.moveNext()
            if self.propertyList["text_wordwrap"]:
                self.__createFloatInput("Word wrap", self.startPos, propFrame, element, "text_wordwrap")
                self.moveNext()
            self.__createInbetweenHeader(
                "Frame Properties", self.startPos, propFrame,
                ["relief", "borderWidth", "frameSize", "frameColor",
                "enableTransparency", "pad"])
            self.frameSize += 30
            if self.propertyList["relief"]:
                self.__createReliefProperty("Relief", self.startPos, propFrame, element)
                self.moveNext()
            if self.propertyList["borderWidth"]:
                self.__createBaseNInput("Border Width", self.startPos, propFrame, element, "borderWidth", 2)
                self.moveNext()
            if self.propertyList["frameSize"]:
                # make sure the frameSize is set correct
                element.frameInitialiseFunc()
                if element["frameSize"] is None:
                    element.setFrameSize(fClearFrame = 1)

                    frameType = element.getFrameType()
                    if ((frameType != PGFrameStyle.TNone) and
                        (frameType != PGFrameStyle.TFlat)):
                        bw = element['borderWidth']
                    else:
                        bw = (0, 0)
                    newFS = LVecBase4f(element.guiItem.getFrame())
                    #newFS[0] += bw[0]
                    #newFS[1] -= bw[0]
                    #newFS[2] += bw[1]
                    #newFS[3] -= bw[1]
                    element["frameSize"] = newFS

                self.__createBaseNInput("Frame Size (L/R/B/T)", self.startPos, propFrame, element, "frameSize", 4)
                self.moveNext()
                self.__createResetFramesize(self.startPos, propFrame, element)
                self.startPos.setZ(self.startPos.getZ() - 30)
                self.frameSize += 30
            if self.propertyList["frameColor"]:
                self.__createBaseNInput("Background Color (r/g/b/a)", self.startPos, propFrame, element, "frameColor", 4)
                self.moveNext()
            if self.propertyList["enableTransparency"]:
                self.__createTransparencyProperty(self.startPos, propFrame, element)
                self.moveNext()
            if self.propertyList["pad"]:
                self.__createBaseNInput("Padding", self.startPos, propFrame, element, "pad", 2)
                self.moveNext()
            self.__createInbetweenHeader(
                "Location Properties", self.startPos, propFrame,
                ["pos", "hpr", "scale"])
            self.frameSize += 30
            if self.propertyList["pos"]:
                self.__createBaseNInput("Position (X/Y/Z)", self.startPos, propFrame, element, "pos", 3)
                self.moveNext()
            if self.propertyList["hpr"]:
                self.__createBaseNInput("Rotation (H/P/R)", self.startPos, propFrame, element, "hpr", 3)
                self.moveNext()
            if self.propertyList["scale"]:
                self.__createBaseNInput("Scale", self.startPos, propFrame, element, "scale", 3)
                self.moveNext()
            self.__createInbetweenHeader(
                "Look Properties", self.startPos, propFrame,
                ["color", "image", "image_scale", "image_pos"])
            self.frameSize += 30
            if self.propertyList["color"]:
                self.__createBaseNInput("Color (r/g/b/a)", self.startPos, propFrame, element, "color", 4)
                self.moveNext()
            if self.propertyList["image"]:
                self.__createImageProperty("Image", self.startPos, propFrame, element)
                self.moveNext()
            if self.propertyList["image_scale"]:
                self.__createBaseNInput("Image Scale", self.startPos, propFrame, element, "image_scale", 3)
                self.moveNext()
            if self.propertyList["image_pos"]:
                self.__createBaseNInput("Image Position (X/Y/Z)", self.startPos, propFrame, element, "image_pos", 3)
                self.moveNext()
            self.__createInbetweenHeader(
                "Other Properties", self.startPos, propFrame,
                ["sortOrder", "command", "state"])
            self.frameSize += 30
            if self.propertyList["sortOrder"]:
                self.__createIntegerInput("Sort Order", self.startPos, propFrame, element, "sortOrder")
                self.moveNext()
            if self.propertyList["command"]:
                self.__createCommandProperty(self.startPos, propFrame, elementInfo)
                self.moveNext()
                self.__createCommandArgsProperty(self.startPos, propFrame, elementInfo)
                self.moveNext()
            if self.propertyList["state"]:
                def update(selection):
                    element["state"] = selection
                self.__createOptionMenuProperty("State", self.startPos, propFrame, elementInfo, [DGG.NORMAL, DGG.DISABLED], element["state"], update)
                self.moveNext()

            #
            # Button specific
            #
            self.__createInbetweenHeader(
                "Button Properties", self.startPos, propFrame, ["pressEffect"])
            if self.propertyList["pressEffect"]:
                #TODO: The pressEffect is currently not changeable after initialization!
                self.__createPressEffectProperty("Show press effect", self.startPos, propFrame, elementInfo)
                self.moveNext()

            #
            # Entry specific
            #
            self.__createInbetweenHeader(
                "Entry Properties", self.startPos, propFrame,
                ["initialText", "width", "numLines", "overflow", "obscured"])
            if self.propertyList["initialText"]:
                self.__createTextProperty("Initial Text", self.startPos, propFrame, element, "initialText")
                self.moveNext()
            if self.propertyList["width"]:
                self.__createFloatInput("Textfield Width", self.startPos, propFrame, element, "width", True)
                self.moveNext()
            if self.propertyList["numLines"]:
                self.__createIntegerInput("Number of Lines", self.startPos, propFrame, element, "numLines", True)
                self.moveNext()
            if self.propertyList["overflow"]:
                self.__createBoolProperty("Enable Overflow", self.startPos, propFrame, element, "overflow")
                self.moveNext()
            if self.propertyList["obscured"]:
                self.__createBoolProperty("Obscured Text", self.startPos, propFrame, element, "obscured")
                self.moveNext()

            #
            # Scrolled Frame specific
            #
            self.__createInbetweenHeader(
                "Scrolled Frame Properties", self.startPos, propFrame,
                ["canvasSize", "scrollBarWidth"])
            if self.propertyList["canvasSize"]:
                self.__createBaseNInput("Canvas Space (L/R/B/T)", self.startPos, propFrame, element, "canvasSize", 4)
                self.moveNext()
            if self.propertyList["scrollBarWidth"]:
                self.__createFloatInput("Scroll Bar Width", self.startPos, propFrame, element, "scrollBarWidth", True)
                self.moveNext()

            #
            # Scrolled Entry specific
            #
            self.__createInbetweenHeader(
                "Scrolled Entry Properties", self.startPos, propFrame,
                ["clipSize"])
            if self.propertyList["clipSize"]:
                self.__createBaseNInput("Clip Size (L/R/B/T)", self.startPos, propFrame, element, "clipSize", 4)
                self.moveNext()

            #
            # Checkbox specific
            #
            self.__createInbetweenHeader(
                "Scrolled Entry Properties", self.startPos, propFrame,
                ["uncheckedImage","checkedImage","isChecked"])
            if self.propertyList["uncheckedImage"]:
                self.__createImageProperty("Unchecked Image", self.startPos, propFrame, element, "uncheckedImage")
                self.moveNext()
            if self.propertyList["checkedImage"]:
                self.__createImageProperty("Checked Image", self.startPos, propFrame, element, "checkedImage")
                self.moveNext()
            if self.propertyList["isChecked"]:
                self.__createBoolProperty("Is checked", self.startPos, propFrame, element, "isChecked")
                self.moveNext()

            #
            # Inc/DecButtons
            #
            for key in self.propertyList.keys():
                if key.startswith("incButton") and self.propertyList[key]:
                    self.__createInbetweenHeader("Inc Button Properties", self.startPos, propFrame)
                    break
            if self.propertyList["incButton_pos"]:
                self.__createBaseNInput("incButton Position (X/Y/Z)", self.startPos, propFrame, element, "incButton_pos", 3)
                self.moveNext()
            if self.propertyList["incButton_hpr"]:
                self.__createBaseNInput("incButton Rotation (H/P/R)", self.startPos, propFrame, element, "incButton_hpr", 3)
                self.moveNext()
            if self.propertyList["incButton_scale"]:
                self.__createBaseNInput("incButton Scale", self.startPos, propFrame, element, "incButton_scale", 3)
                self.moveNext()
            if self.propertyList["incButton_frameColor"]:
                self.__createBaseNInput("incButton Background Color (r/g/b/a)", self.startPos, propFrame, element, "incButton_frameColor", 4)
                self.moveNext()
            if self.propertyList["incButton_frameSize"]:
                self.__createBaseNInput("incButton Frame Size (L/R/B/T)", self.startPos, propFrame, element, "incButton_frameSize", 4)
                self.moveNext()
                incBtn = element.incButton
                self.__createResetFramesize(self.startPos, propFrame, incBtn)
                self.startPos.setZ(self.startPos.getZ() - 30)
                self.frameSize += 30
            if self.propertyList["incButton_image"]:
                self.__createImageProperty("incButton Image", self.startPos, propFrame, element, "incButton_image")
                self.moveNext()
            if self.propertyList["incButton_image_scale"]:
                self.__createBaseNInput("incButton Image Scale (X/Y/Z)", self.startPos, propFrame, element, "incButton_image_scale", 3)
                self.moveNext()

            for key in self.propertyList.keys():
                if key.startswith("decButton") and self.propertyList[key]:
                    self.__createInbetweenHeader("Dec Button Properties", self.startPos, propFrame)
                    break
            if self.propertyList["decButton_pos"]:
                self.__createBaseNInput("decButton Position (X/Y/Z)", self.startPos, propFrame, element, "decButton_pos", 3)
                self.moveNext()
            if self.propertyList["decButton_hpr"]:
                self.__createBaseNInput("decButton Rotation (H/P/R)", self.startPos, propFrame, element, "decButton_hpr", 3)
                self.moveNext()
            if self.propertyList["decButton_scale"]:
                self.__createBaseNInput("decButton Scale", self.startPos, propFrame, element, "decButton_scale", 3)
                self.moveNext()
            if self.propertyList["decButton_frameColor"]:
                self.__createBaseNInput("decButton Background Color (r/g/b/a)", self.startPos, propFrame, element, "decButton_frameColor", 4)
                self.moveNext()
            if self.propertyList["decButton_frameSize"]:
                self.__createBaseNInput("decButton Frame Size (L/R/B/T)", self.startPos, propFrame, element, "decButton_frameSize", 4)
                self.moveNext()
                decBtn = element.decButton
                self.__createResetFramesize(self.startPos, propFrame, decBtn)
                self.startPos.setZ(self.startPos.getZ() - 30)
                self.frameSize += 30
            if self.propertyList["decButton_image"]:
                self.__createImageProperty("decButton Image", self.startPos, propFrame, element, "decButton_image")
                self.moveNext()
            if self.propertyList["decButton_image_scale"]:
                self.__createBaseNInput("decButton Image Scale (X/Y/Z)", self.startPos, propFrame, element, "decButton_image_scale", 3)
                self.moveNext()

            for key in self.propertyList.keys():
                if key.startswith("thumb") and self.propertyList[key]:
                    self.__createInbetweenHeader("Thumb Properties", self.startPos, propFrame)
                    break
            if self.propertyList["thumb_pos"]:
                self.__createBaseNInput("thumb Position (X/Y/Z)", self.startPos, propFrame, element, "thumb_pos", 3)
                self.moveNext()
            if self.propertyList["thumb_hpr"]:
                self.__createBaseNInput("thumb Rotation (H/P/R)", self.startPos, propFrame, element, "thumb_hpr", 3)
                self.moveNext()
            if self.propertyList["thumb_scale"]:
                self.__createBaseNInput("thumb Scale", self.startPos, propFrame, element, "thumb_scale", 3)
                self.moveNext()
            if self.propertyList["thumb_frameColor"]:
                self.__createBaseNInput("thumb Background Color (r/g/b/a)", self.startPos, propFrame, element, "thumb_frameColor", 4)
                self.moveNext()
            if self.propertyList["thumb_frameSize"]:
                self.__createBaseNInput("thumb Frame Size (L/R/B/T)", self.startPos, propFrame, element, "thumb_frameSize", 4)
                self.moveNext()
                decBtn = element.thumb
                self.__createResetFramesize(self.startPos, propFrame, decBtn)
                self.startPos.setZ(self.startPos.getZ() - 30)
                self.frameSize += 30
            if self.propertyList["thumb_image"]:
                self.__createImageProperty("thumb Image", self.startPos, propFrame, element, "thumb_image")
                self.moveNext()
            if self.propertyList["thumb_image_scale"]:
                self.__createBaseNInput("thumb Image Scale (X/Y/Z)", self.startPos, propFrame, element, "thumb_image_scale", 3)
                self.moveNext()

            #
            # CheckButton specific
            #
            self.__createInbetweenHeader(
                "Check Button Properties", self.startPos, propFrame,
                ["boxBorder","boxPlacement","boxImage","boxImageScale",
                "boxImageColor","boxRelief", "indicator_text_scale",
                "indicator_text_pos", "indicator_borderWidth"])
            if self.propertyList["boxBorder"]:
                self.__createFloatInput("Box Border Width", self.startPos, propFrame, element, "boxBorder")
                self.moveNext()
            if self.propertyList["boxPlacement"]:
                # boxPlacement maps left, above, right, below
                self.__createPlacementProperty("Box Placement", self.startPos, propFrame, element, "boxPlacement")
                self.moveNext()
            if self.propertyList["boxImage"]:
                self.__createImageProperty("Box Image", self.startPos, propFrame, element, "boxImage")
                self.moveNext()
            if self.propertyList["boxImageScale"]:
                self.__createFloatInput("Box Image Scale (X/Y/Z)", self.startPos, propFrame, element, "boxImageScale")
                self.moveNext()
            if self.propertyList["boxImageColor"]:
                self.__createBaseNInput("Box Image Color (r/g/b/a)", self.startPos, propFrame, element, "boxImageColor", 4)
                self.moveNext()
            if self.propertyList["boxRelief"]:
                self.__createReliefProperty("Box Relief", self.startPos, propFrame, element, "boxRelief")
                self.moveNext()
            if self.propertyList["indicator_text_scale"]:
                self.__createBaseNInput("Indicator Text Scale", self.startPos, propFrame, element, "indicator_text_scale", 2)
                self.moveNext()
            if self.propertyList["indicator_text_pos"]:
                self.__createBaseNInput("Indicator Text Position (X/Y)", self.startPos, propFrame, element, "indicator_text_pos", 2)
                self.moveNext()
            if self.propertyList["indicator_borderWidth"]:
                self.__createBaseNInput("Indicator Border Width", self.startPos, propFrame, element, "indicator_borderWidth", 2)
                self.moveNext()

            #
            # RadioButton specific
            #
            self.__createInbetweenHeader(
                "Radio Button Properties", self.startPos, propFrame,
                ["others", "indicatorValue"])
            if self.propertyList["others"]:
                self.__createOthersSelectorProperty(self.startPos, propFrame, element)
            if self.propertyList["indicatorValue"]:
                self.__createBoolProperty("Is selected", self.startPos, propFrame, element, "indicatorValue")
                self.moveNext()

            #
            # OptionMenu specific
            #
            self.__createInbetweenHeader(
                "Check Button Properties", self.startPos, propFrame,
                ["popupMarkerBorder","popupMarker_pos","popupMenuLocation",
                "highlightColor","highlightScale"])
            if self.propertyList["popupMarkerBorder"]:
                self.__createBaseNInput("Popup Marker Border", self.startPos, propFrame, element, "popupMarkerBorder", 2)
                self.moveNext()
            if self.propertyList["popupMarker_pos"]:
                self.__createBaseNInput("Popup Marker Position (X/Y/Z)", self.startPos, propFrame, element, "popupMarker_pos", 3)
                self.moveNext()
            if self.propertyList["popupMenuLocation"]:
                self.__createPlacementProperty("Popup Menu Location", self.startPos, propFrame, element, "popupMenuLocation")
                self.moveNext()
            if self.propertyList["highlightColor"]:
                self.__createBaseNInput("Highlight Color", self.startPos, propFrame, element, "highlightColor", 4)
                self.moveNext()
            if self.propertyList["highlightScale"]:
                self.__createBaseNInput("Highlight Scale", self.startPos, propFrame, element, "highlightScale", 2)
                self.moveNext()

            #
            # ScrollBar/Silder specific
            #
            self.__createInbetweenHeader(
                "ScrollBar/Slider Properties", self.startPos, propFrame,
                ["SB-range","scrollSize","pageSize","orientation",
                "manageButtons", "resizeThumb"])
            if self.propertyList["SB-range"]:
                self.__createBaseNInput("Bar Range", self.startPos, propFrame, element, "range", 2)
                self.moveNext()
            if self.propertyList["scrollSize"]:
                self.__createFloatInput("Scroll Size", self.startPos, propFrame, element, "scrollSize")
                self.moveNext()
            if self.propertyList["pageSize"]:
                self.__createFloatInput("Page Size", self.startPos, propFrame, element, "pageSize")
                self.moveNext()
            if self.propertyList["orientation"]:
                self.__createOrientationProperty("Orientation", self.startPos, propFrame, element, "orientation")
                self.moveNext()
            if self.propertyList["manageButtons"]:
                self.__createBoolProperty("Manage Buttons", self.startPos, propFrame, element, "manageButtons")
                self.moveNext()
            if self.propertyList["resizeThumb"]:
                self.__createBoolProperty("Resize Thumb", self.startPos, propFrame, element, "resizeThumb")
                self.moveNext()

            #
            # WaitBar specific
            #
            self.__createInbetweenHeader(
                "WaitBar Properties", self.startPos, propFrame,
                ["range","barBorderWidth","barColor","barTexture", "barRelief"])
            if self.propertyList["range"]:
                self.__createFloatInput("Bar Range", self.startPos, propFrame, element, "range")
                self.moveNext()
            if self.propertyList["barBorderWidth"]:
                self.__createBaseNInput("Bar Border Width", self.startPos, propFrame, element, "barBorderWidth", 2)
                self.moveNext()
            if self.propertyList["barColor"]:
                self.__createBaseNInput("Bar Color", self.startPos, propFrame, element, "barColor", 4)
                self.moveNext()
            if self.propertyList["barTexture"]:
                self.__createImageProperty("Bar Texture", self.startPos, propFrame, element, "barTexture")
                self.moveNext()
            if self.propertyList["barRelief"]:
                self.__createReliefProperty("Bar Relief", self.startPos, propFrame, element, "barRelief")
                self.moveNext()

            #
            # Bar and Slider Generic props
            #
            if self.propertyList["value"]:
                self.__createFloatInput("Value", self.startPos, propFrame, element, "value")
                self.moveNext()

            #
            # Custom properties
            #
            if len(self.customProperties) > 0:
                self.__createInbetweenHeader("Custom Properties", self.startPos, propFrame)
            for prop in self.customProperties:
                if prop.propertyType.lower() == "int":
                    self.__createIntegerInput(prop.displayName, self.startPos, propFrame, element, prop.propertyName)
                    self.moveNext()
                elif prop.propertyType.lower() == "float":
                    self.__createFloatInput(prop.displayName, self.startPos, propFrame, element, prop.propertyName)
                    self.moveNext()
                elif prop.propertyType.lower() == "vbase2":
                    self.__createBaseNInput(prop.displayName, self.startPos, propFrame, element, prop.propertyName, 2)
                    self.moveNext()
                elif prop.propertyType.lower() == "vbase3":
                    self.__createBaseNInput(prop.displayName, self.startPos, propFrame, element, prop.propertyName, 3)
                    self.moveNext()
                elif prop.propertyType.lower() == "vbase4":
                    self.__createBaseNInput(prop.displayName, self.startPos, propFrame, element, prop.propertyName, 4)
                    self.moveNext()
                elif prop.propertyType.lower() == "text":
                    self.__createTextProperty(prop.displayName, self.startPos, propFrame, element, prop.propertyName)
                    self.moveNext()
                elif prop.propertyType.lower() == "image":
                    self.__createImageProperty(prop.displayName, self.startPos, propFrame, element, prop.propertyName)
                    self.moveNext()
                elif prop.propertyType.lower() == "bool":
                    self.__createBoolProperty(prop.displayName, self.startPos, propFrame, element, prop.propertyName)
                    self.moveNext()
                elif prop.propertyType.lower() == "orientation":
                    self.__createOrientationProperty(prop.displayName, self.startPos, propFrame, element, prop.propertyName)
                    self.moveNext()
                elif prop.propertyType.lower() == "relief":
                    self.__createReliefProperty(prop.displayName, self.startPos, propFrame, element, prop.propertyName)
                    self.moveNext()
                elif prop.propertyType.lower() == "placement":
                    self.__createPlacementProperty(prop.displayName, self.startPos, propFrame, element, prop.propertyName)
                    self.moveNext()
                elif prop.propertyType.lower() == "align":
                    self.__createCustomAlignProperty(prop.displayName, self.startPos, propFrame, element, prop.propertyName)
                    self.moveNext()
                elif prop.propertyType.lower() == "selection":
                    self.__createCustomSelectionProperty(prop.displayName, self.startPos, propFrame, element, prop.propertyName, prop.customSelectionDict)
                    self.moveNext()
                elif prop.propertyType.lower() == "commandproperty":
                    self.__createCustomCommandProperty(prop.displayName, self.startPos, propFrame, element, prop.propertyName, elementInfo)
                    self.moveNext()
                #TODO: ADD CUSTOM COMMAND EXTRA ARGUMENTS
                #elif prop.propertyType.lower() == "commandArguments":
                #    self.__createCommandArgsProperty(self.startPos, propFrame, elementInfo)
                #    self.moveNext()
                elif prop.propertyType.lower() == "command":
                    self.__createCustomCommand(prop.displayName, self.startPos, propFrame, element, prop.customCommandName)
                    self.moveNext()
        except:
            e = sys.exc_info()[1]
            base.messenger.send("showWarning", [str(e)])
            logging.exception("Error while loading properties panel")
        #
        # Reset propFrame frame size
        #
        propFrame["frameSize"] = (
            self.propertiesFrame["frameSize"][0], self.propertiesFrame["frameSize"][1]-20,
            -self.frameSize, 0.0)

        self.propertiesFrame["canvasSize"] = (
            self.propertiesFrame["frameSize"][0], max(self.propertiesFrame["frameSize"][1]-20, self.maxElementWidth),
            propFrame.bounds[2]-20, 0)
        self.propertiesFrame.setCanvasSize()

        a = self.propertiesFrame["canvasSize"][2]
        b = abs(self.propertiesFrame["frameSize"][2]) + self.propertiesFrame["frameSize"][3]
        scrollDefault = 200
        s = -(scrollDefault / (a / b))

        self.propertiesFrame["verticalScroll_scrollSize"] = s
        self.propertiesFrame["verticalScroll_pageSize"] = s

        self.curPropFrame = propFrame

    def clear(self):
        if self.curPropFrame is not None:
            self.curPropFrame.destroy()

    def __createInbetweenHeader(self, description, startPos, parent, mustDefinedValues=[]):
        if mustDefinedValues is not []:
            hasDefined = False
            for prop in mustDefinedValues:
                if self.propertyList[prop]:
                    hasDefined = True
                    break
            if not hasDefined: return
        x = startPos.getX()
        z = startPos.getZ()
        DirectLabel(
            text=description,
            text_scale=16,
            text_pos=(-10, 0),
            text_align=TextNode.ACenter,
            frameSize=VBase4(-self.propertiesFrame["frameSize"][1], self.propertiesFrame["frameSize"][1], -10, 20),
            frameColor=VBase4(0.85,0.85,0.85,1),
            pos=(0,0,z-20),
            parent=parent)
        self.startPos.setZ(self.startPos.getZ() - 30)
        self.frameSize += 30

    def __createPropertyHeader(self, description, z, parent):
        DirectLabel(
            text=description,
            text_scale=12,
            text_pos=(self.propertiesFrame["frameSize"][0], 0),
            text_align=TextNode.ALeft,
            frameSize=VBase4(self.propertiesFrame["frameSize"][0], self.propertiesFrame["frameSize"][1], -10, 20),
            frameColor=VBase4(0.85,0.85,0.85,1),
            pos=(0,0,z-20),
            parent=parent)
        self.startPos.setZ(self.startPos.getZ() - 30 - 15)

    def __getFormated(self, value, isInt=False):
        if type(value) is int or isInt:
            return "{}".format(int(value))
        else:
            return "{:0.3f}".format(value)

    def __getValues(self, updateElement, updateAttribute):
        if updateAttribute in self.initOpGetDict:
            if hasattr(updateElement, self.initOpGetDict[updateAttribute]):
                return getattr(updateElement, self.initOpGetDict[updateAttribute])()
        elif updateAttribute in self.subControlInitOpGetDict:
            if hasattr(updateElement, self.subControlInitOpGetDict[updateAttribute][0]):
                control = getattr(updateElement, self.subControlInitOpGetDict[updateAttribute][0])
                if hasattr(control, self.subControlInitOpGetDict[updateAttribute][1]):
                    return getattr(control, self.subControlInitOpGetDict[updateAttribute][1])()
        elif updateAttribute in self.getAsPropDict:
            if hasattr(updateElement, self.getAsPropDict[updateAttribute]):
                return getattr(updateElement, self.getAsPropDict[updateAttribute])
            else:
                for componentName in updateElement.components():
                    comp = updateElement.component(componentName)
                    if hasattr(comp, self.getAsPropDict[updateAttribute]):
                        return getattr(comp, self.getAsPropDict[updateAttribute])

    def __createTextEntry(self, text, x, z, width, command, parent):
        def focusOut():
            messenger.send("reregisterKeyboardEvents")
            command(entry.get())
        entry = DirectEntry(
            initialText=text,
            relief=DGG.SUNKEN,
            frameColor=(1,1,1,1),
            pos=(x+10, 0, z),
            scale=12,
            width=width,
            overflow=True,
            command=command,
            focusInCommand=base.messenger.send,
            focusInExtraArgs=["unregisterKeyboardEvents"],
            focusOutCommand=focusOut,
            parent=parent)
        entry.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        entry.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        return entry

    #
    # General input elements
    #
    def __createBaseNInput(self, description, startPos, parent, updateElement, updateAttribute, n):
        def update(text):
            base.messenger.send("setDirtyFlag")

            values = []
            for value in entryList:
                try:
                    values.append(float(value.get(True)))
                except:
                    logging.exception("ERROR: NAN", value.get(True))

            try:
                if updateAttribute in self.initOpGetDict or updateAttribute in self.subControlInitOpGetDict or updateAttribute in self.getAsPropDict:
                    oldValue = self.__getValues(updateElement, updateAttribute)
                else:
                    oldValue = updateElement[updateAttribute]
                differ = False
                if oldValue is not None:
                    for i in range(n):
                        if oldValue[i] != values[i]:
                            differ = True
                            break
                if differ:
                    base.messenger.send("addToKillRing",
                        [updateElement, "set", updateAttribute, oldValue, values])
            except:
                print(updateAttribute, " not supported by undo/redo yet")

            if updateAttribute in self.initOpGetDict:
                if hasattr(updateElement, self.initOpDict[updateAttribute]):
                    getattr(updateElement, self.initOpDict[updateAttribute])(*values)
            elif updateAttribute in self.subControlInitOpDict:
                if hasattr(updateElement, self.subControlInitOpDict[updateAttribute][0]):
                    control = getattr(updateElement, self.subControlInitOpDict[updateAttribute][0])
                    if hasattr(control, self.subControlInitOpDict[updateAttribute][1]):
                        getattr(control, self.subControlInitOpDict[updateAttribute][1])(*values)
            else:
                updateElement[updateAttribute] = tuple(values)
        x = startPos.getX()
        z = startPos.getZ()
        self.__createPropertyHeader(description, z, parent)
        z = startPos.getZ()
        values = [0] * n
        if updateAttribute in self.initOpGetDict or updateAttribute in self.subControlInitOpGetDict or updateAttribute in self.getAsPropDict:
            v = self.__getValues(updateElement, updateAttribute)
            if v is not None:
                values = v
        elif "image_" in updateAttribute:
            parts = updateAttribute.split("_")
            try:
                idx = 0
                while len(parts) < idx or parts[idx] != "image":
                    idx += 1

                element = updateElement
                for element_index in range(idx):
                    element = element.component(parts[element_index])

                if element["image"] is not None:
                    for i in range(n):
                        values[i] = updateElement[updateAttribute][i]
            except:
                logging.debug("Failed do get image property:", parts)
                return
        elif updateElement[updateAttribute] is not None:
            for i in range(n):
                values[i] = updateElement[updateAttribute][i]

        entryList = []
        width = (DGH.getRealWidth(parent)-10) / n
        entryWidth = width / 13
        for i in range(n):
            value = self.__getFormated(values[i])

            entryList.append(self.__createTextEntry(str(value), x, z, entryWidth, update, parent))
            x += width

    def __createFloatInput(self, description, startPos, parent, updateElement, updateAttribute, resetFrameSize=False):
        def update(text):
            base.messenger.send("setDirtyFlag")
            value = 0.0
            try:
                value = float(text)
            except:
                logging.exception("ERROR: NAN", value)

            try:
                if updateAttribute in self.initOpGetDict or updateAttribute in self.subControlInitOpGetDict or updateAttribute in self.getAsPropDict:
                    oldValue = self.__getValues(updateElement, updateAttribute)
                else:
                    oldValue = updateElement[updateAttribute]
                base.messenger.send("addToKillRing",
                    [updateElement, "set", updateAttribute, oldValue, value])
            except:
                print(updateAttribute, " not supported by undo/redo yet")

            if updateAttribute in self.initOpDict:
                if hasattr(updateElement, self.initOpDict[updateAttribute]):
                    getattr(updateElement, self.initOpDict[updateAttribute])(value)
            elif updateAttribute in self.subControlInitOpDict:
                if hasattr(updateElement, self.subControlInitOpDict[updateAttribute][0]):
                    control = getattr(updateElement, self.subControlInitOpDict[updateAttribute][0])
                    if hasattr(control, self.subControlInitOpDict[updateAttribute][1]):
                        getattr(control, self.subControlInitOpDict[updateAttribute][1])(value)
            else:
                updateElement[updateAttribute] = value
            if resetFrameSize:
                updateElement.resetFrameSize()
        x = startPos.getX()
        z = startPos.getZ()
        self.__createPropertyHeader(description, z, parent)
        z = startPos.getZ()
        valueA = 0
        if updateAttribute in self.initOpGetDict or updateAttribute in self.subControlInitOpGetDict or updateAttribute in self.getAsPropDict:
            v = self.__getValues(updateElement, updateAttribute)
            if v is not None:
                valueA = v
        elif "image_" in updateAttribute:
            parts = updateAttribute.split("_")
            if updateElement[parts[0]] is not None:
                valueA = updateElement[updateAttribute]
        elif updateElement[updateAttribute] is not None:
            valueA = updateElement[updateAttribute]

        valueA = self.__getFormated(valueA)
        width = (parent.bounds[1]-10)
        entryWidth = width / 13
        entry = self.__createTextEntry(str(valueA), x, z, entryWidth, update, parent)

    def __createIntegerInput(self, description, startPos, parent, updateElement, updateAttribute, resetFrameSize=False):
        def update(text):
            base.messenger.send("setDirtyFlag")
            value = 0
            try:
                value = int(text)
            except:
                logging.exception("ERROR: NAN", value)

            try:
                if updateAttribute in self.initOpGetDict or updateAttribute in self.subControlInitOpGetDict or updateAttribute in self.getAsPropDict:
                    oldValue = self.__getValues(updateElement, updateAttribute)
                else:
                    oldValue = updateElement[updateAttribute]
                base.messenger.send("addToKillRing",
                    [updateElement, "set", updateAttribute, oldValue, value])
            except:
                print(updateAttribute, " not supported by undo/redo yet")

            if updateAttribute in self.initOpDict:
                if hasattr(updateElement, self.initOpDict[updateAttribute]):
                    getattr(updateElement, self.initOpDict[updateAttribute])(value)
            elif updateAttribute in self.subControlInitOpDict:
                if hasattr(updateElement, self.subControlInitOpDict[updateAttribute][0]):
                    control = getattr(updateElement, self.subControlInitOpDict[updateAttribute][0])
                    if hasattr(control, self.subControlInitOpDict[updateAttribute][1]):
                        getattr(control, self.subControlInitOpDict[updateAttribute][1])(value)
            else:
                updateElement[updateAttribute] = (value)
            if resetFrameSize:
                updateElement.resetFrameSize()
        x = startPos.getX()
        z = startPos.getZ()
        self.__createPropertyHeader(description, z, parent)
        z = startPos.getZ()
        valueA = 0
        if updateAttribute in self.initOpGetDict or updateAttribute in self.subControlInitOpGetDict or updateAttribute in self.getAsPropDict:
            v = self.__getValues(updateElement, updateAttribute)
            if v is not None:
                valueA = v
        elif "image_" in updateAttribute:
            parts = updateAttribute.split("_")
            if updateElement[parts[0]] is not None:
                valueA = updateElement[updateAttribute]
        elif updateElement[updateAttribute] is not None:
            valueA = updateElement[updateAttribute]

        valueA = self.__getFormated(valueA, True)
        width = (parent.bounds[1]-10)
        entryWidth = width / 13
        entry = self.__createTextEntry(str(valueA), x, z, entryWidth, update, parent)

    def __createTextProperty(self, description, startPos, parent, updateElement, updateAttribute):
        def update(text):
            base.messenger.send("setDirtyFlag")

            try:
                if updateAttribute in self.initOpGetDict or updateAttribute in self.subControlInitOpGetDict or updateAttribute in self.getAsPropDict:
                    oldValue = self.__getValues(updateElement, updateAttribute)
                else:
                    oldValue = updateElement[updateAttribute]
                base.messenger.send("addToKillRing",
                    [updateElement, "set", updateAttribute, oldValue, text])
            except:
                print(updateAttribute, " not supported by undo/redo yet")

            if updateAttribute in self.initOpDict:
                if hasattr(updateElement, self.initOpDict[updateAttribute]):
                    getattr(updateElement, self.initOpDict[updateAttribute])(text)
            elif updateAttribute in self.subControlInitOpDict:
                if hasattr(updateElement, self.subControlInitOpDict[updateAttribute][0]):
                    control = getattr(updateElement, self.subControlInitOpDict[updateAttribute][0])
                    if hasattr(control, self.subControlInitOpDict[updateAttribute][1]):
                        getattr(control, self.subControlInitOpDict[updateAttribute][1])(text)
            else:
                updateElement[updateAttribute] = (text)
        x = startPos.getX()
        z = startPos.getZ()
        self.__createPropertyHeader(description, z, parent)
        z = startPos.getZ()
        text = ""
        if updateAttribute in self.initOpGetDict or updateAttribute in self.subControlInitOpGetDict or updateAttribute in self.getAsPropDict:
            text = self.__getValues(updateElement, updateAttribute)
        elif updateElement[updateAttribute] is not None:
            text = updateElement[updateAttribute]
        width = (parent.bounds[1]-10)
        entryWidth = width / 13
        entry = self.__createTextEntry(text, x, z, entryWidth, update, parent)

    def __createCustomCommandProperty(self, description, startPos, parent, updateElement, updateAttribute, elementInfo):
        def update(text):
            base.messenger.send("setDirtyFlag")
            self.elementInfo.extraOptions[updateAttribute] = text

            for elementId, self.elementInfo in self.elementDict.items():
                if elementId in text:
                    text = text.replace(elementId, "elementDict['{}'].element".format(elementId))
                elif self.elementInfo.name in text:
                    text = text.replace(self.elementInfo.name, "elementDict['{}'].element".format(elementId))

            command = ""
            if text:
                try:
                    command = eval(text)
                except:
                    logging.debug("command evaluation not supported: ", text)
                    logging.debug("set command without evalution")
                    command = text

            try:
                base.messenger.send("addToKillRing",
                    [updateElement, "set", updateAttribute, curCommand, text])
            except:
                print(updateAttribute, " not supported by undo/redo yet")

            if updateAttribute in self.initOpDict:
                if hasattr(updateElement, self.initOpDict[updateAttribute]):
                    getattr(updateElement, self.initOpDict[updateAttribute])(command)
            elif updateAttribute in self.subControlInitOpDict:
                if hasattr(updateElement, self.subControlInitOpDict[updateAttribute][0]):
                    control = getattr(updateElement, self.subControlInitOpDict[updateAttribute][0])
                    if hasattr(control, self.subControlInitOpDict[updateAttribute][1]):
                        getattr(control, self.subControlInitOpDict[updateAttribute][1])(command)
            else:
                updateElement[updateAttribute] = (command)
        x = startPos.getX()
        z = startPos.getZ()
        self.__createPropertyHeader(description, z, parent)
        z = startPos.getZ()
        curCommand = ""
        if updateAttribute in elementInfo.extraOptions:
            curCommand = elementInfo.extraOptions[updateAttribute]
        width = (parent.bounds[1]-10)
        entryWidth = width / 13
        self.__createTextEntry(curCommand, x, z, entryWidth, update, parent)

    def __createBoolProperty(self, description, startPos, parent, updateElement, updateAttribute):
        def update(value):
            base.messenger.send("setDirtyFlag")

            try:
                if updateAttribute in self.initOpGetDict or updateAttribute in self.subControlInitOpGetDict or updateAttribute in self.getAsPropDict:
                    oldValue = self.__getValues(updateElement, updateAttribute)
                else:
                    oldValue = updateElement[updateAttribute]
                base.messenger.send("addToKillRing",
                    [updateElement, "set", updateAttribute, oldValue, value])
            except:
                print(updateAttribute, " not supported by undo/redo yet")


            if updateAttribute in self.callFunc.keys():
                if hasattr(updateElement, self.callFunc[updateAttribute][0]):
                    getattr(updateElement, self.callFunc[updateAttribute][0])(self.callFunc[updateAttribute][1])
                    return
            if updateAttribute in self.initOpDict:
                if hasattr(updateElement, self.initOpDict[updateAttribute]):
                    getattr(updateElement, self.initOpDict[updateAttribute])(value)
            elif updateAttribute in self.subControlInitOpDict:
                if hasattr(updateElement, self.subControlInitOpDict[updateAttribute][0]):
                    control = getattr(updateElement, self.subControlInitOpDict[updateAttribute][0])
                    if hasattr(control, self.subControlInitOpDict[updateAttribute][1]):
                        getattr(control, self.subControlInitOpDict[updateAttribute][1])(value)
            else:
                updateElement[updateAttribute] = value
        x = startPos.getX()
        z = startPos.getZ()
        self.__createPropertyHeader(description, z, parent)
        z = startPos.getZ()
        valueA = 0
        if updateAttribute in self.initOpGetDict or updateAttribute in self.subControlInitOpGetDict or updateAttribute in self.getAsPropDict:
            valueA = self.__getValues(updateElement, updateAttribute)
        elif updateElement[updateAttribute] is not None:
            valueA = updateElement[updateAttribute]
        btn = DirectCheckButton(
            pos=(x+10, 0, z),
            indicatorValue=valueA,
            boxPlacement="right",
            scale=12,
            text_align=TextNode.ALeft,
            command=update,
            parent=parent)
        btn.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        btn.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])

    def __createPressEffectProperty(self, description, startPos, parent, elementInfo):
        def update(value):
            base.messenger.send("setDirtyFlag")
            try:
                oldValue = elementInfo.extraOptions["pressEffect"] if "pressEffect" in elementInfo.extraOptions else 1
                base.messenger.send("addToKillRing",
                    [elementInfo, "set", "pressEffect", oldValue, value])
            except:
                print("pressEffect not supported by undo/redo yet")
            elementInfo.extraOptions["pressEffect"] = value
        x = startPos.getX()
        z = startPos.getZ()
        self.__createPropertyHeader("pressEffect", z, parent)
        z = startPos.getZ()
        value = elementInfo.extraOptions["pressEffect"] if "pressEffect" in elementInfo.extraOptions else 1
        btn = DirectCheckButton(
            pos=(x+10, 0, z),
            indicatorValue=value,
            boxPlacement="right",
            scale=12,
            text_align=TextNode.ALeft,
            command=update,
            parent=parent)
        btn.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        btn.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])

    def __createImageProperty(self, description, startPos, parent, updateElement, updateAttribute="image"):
        def update(text):
            base.messenger.send("setDirtyFlag")
            try:
                updateElement[updateAttribute] = text
            except:
                logging.exception("Couldn't load image: {}".format(text))
                updateElement[updateAttribute] = None
        def setImage(imgUrl):
            entry.set(imgUrl)
            update(imgUrl)

        def selectPath(confirm):
            if confirm:
                setImage(self.browser.get())
            self.browser.hide()
        def showBrowser():
            self.browser = DirectFolderBrowser(selectPath, True, ConfigVariableString("work-dir-path", "~").getValue(), "", tooltip=self.tooltip)
            self.browser.show()
        x = startPos.getX()
        z = startPos.getZ()
        self.__createPropertyHeader(description, z, parent)
        z = startPos.getZ()
        image = updateElement[updateAttribute]
        width = (parent.bounds[1]-10)
        entryWidth = width / 15
        entry = self.__createTextEntry(image, x, z, entryWidth, update, parent)

        btn = DirectButton(
            text="Browse",
            command=showBrowser,
            pad=(0.25,0.25),
            pos=(width - entryWidth, 0, z),
            scale=12,
            parent=parent
            )
        btn.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        btn.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])

    def __createFontProperty(self, description, startPos, parent, updateElement, updateAttribute="text_font"):
        def update(text):
            if text == "": return
            base.messenger.send("setDirtyFlag")
            try:
                self.elementInfo.extraOptions[updateAttribute] = text
                font = loader.loadFont(text)
                updateElement[updateAttribute] = font
            except:
                logging.exception("Couldn't load font: {}".format(text))
                updateElement[updateAttribute] = None
        def setFont(fontUrl):
            entry.set(fontUrl)
            update(fontUrl)

        def selectPath(confirm):
            if confirm:
                setFont(self.browser.get())
            self.browser.hide()
        def showBrowser():
            self.browser = DirectFolderBrowser(selectPath, True, ConfigVariableString("work-dir-path", "~").getValue(), "", tooltip=self.tooltip)
            self.browser.show()
        x = startPos.getX()
        z = startPos.getZ()
        self.__createPropertyHeader(description, z, parent)
        z = startPos.getZ()
        font = ""
        if updateAttribute in self.elementInfo.extraOptions:
            font = self.elementInfo.extraOptions[updateAttribute]
        width = (parent.bounds[1]-10)
        entryWidth = width / 15
        entry = self.__createTextEntry(font, x, z, entryWidth, update, parent)

        btn = DirectButton(
            text="Browse",
            command=showBrowser,
            pad=(0.25,0.25),
            pos=(width - entryWidth, 0, z),
            scale=12,
            parent=parent
            )
        btn.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        btn.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])

    def __createReliefProperty(self, description, startPos, parent, updateElement, updateAttribute="relief"):
        def update(selection):
            base.messenger.send("setDirtyFlag")
            if selection == "None":
                updateElement[updateAttribute] = PGFrameStyle.TNone
            else:
                updateElement[updateAttribute] = DGG.FrameStyleDict[selection]
        selectedElement = "None"
        for key, value in DGG.FrameStyleDict.items():
            if value == updateElement[updateAttribute]:
                selectedElement = key
                break
        self.__createOptionMenuProperty(
            description, startPos, parent, updateElement,
             ["None"] + list(DGG.FrameStyleDict.keys()), selectedElement, update)

    def __createOrientationProperty(self, description, startPos, parent, updateElement, updateAttribute):
        orientationDict = {'horizontal': DGG.HORIZONTAL, 'vertical': DGG.VERTICAL, 'vertical_inverted': DGG.VERTICAL_INVERTED}
        def update(selection):
            base.messenger.send("setDirtyFlag")
            updateElement[updateAttribute] = orientationDict[selection]
        selectedElement = None
        for key, value in orientationDict.items():
            if value == updateElement[updateAttribute]:
                selectedElement = key
                break
        self.__createOptionMenuProperty(
            description, startPos, parent, updateElement,
            list(orientationDict.keys()), selectedElement, update)

    def __createPlacementProperty(self, description, startPos, parent, updateElement, updateAttribute):
        placements = ["left", "above", "right", "below"]
        def update(selection):
            base.messenger.send("setDirtyFlag")
            updateElement[updateAttribute] = selection
        selectedElement = updateElement[updateAttribute]
        self.__createOptionMenuProperty(
            description, startPos, parent, updateElement,
            placements, selectedElement, update)

    def __createCustomCommand(self, description, startPos, parent, updateElement, customCommandName):
        x = startPos.getX()
        z = startPos.getZ()
        self.__createPropertyHeader(description, z, parent)
        z = startPos.getZ()
        btn = DirectButton(
            text=description,
            pad=(0.25,0.25),
            pos=(0, 0, z-3),
            scale=12,
            parent=parent,
            command=getattr(updateElement, customCommandName)
            )
        btn.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        btn.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])

    #
    # Specific input fields
    #

    def __createNameProperty(self, startPos, parent, updateElementInfo):
        def update(text):
            base.messenger.send("setDirtyFlag")
            name = updateElementInfo.element.guiId.replace("-", "")
            if text != "":
                name = text
            base.messenger.send("setName", [updateElementInfo, name])
        x = startPos.getX()
        z = startPos.getZ()
        self.__createPropertyHeader("Name", z, parent)
        z = startPos.getZ()

        text = updateElementInfo.name
        width = (parent.bounds[1]-10)
        entryWidth = width / 13
        entry = self.__createTextEntry(text, x, z, entryWidth, update, parent)

    def __createCommandProperty(self, startPos, parent, updateElementInfo):
        def update(text):
            base.messenger.send("setDirtyFlag")
            command = None
            if text != "":
                command = text
            base.messenger.send("setCommand", [updateElementInfo, command])
        x = startPos.getX()
        z = startPos.getZ()-0.03
        self.__createPropertyHeader("Command", z, parent)
        z = startPos.getZ()
        cmd = "" if updateElementInfo.command is None else updateElementInfo.command
        width = (parent.bounds[1]-10)
        entryWidth = width / 13
        entry = self.__createTextEntry(cmd, x, z, entryWidth, update, parent)

    def __createCommandArgsProperty(self, startPos, parent, updateElementInfo):
        def update(text):
            base.messenger.send("setDirtyFlag")
            extraArgs = None
            if text != "":
                extraArgs = text
            base.messenger.send("setExtraArgs", [updateElementInfo, extraArgs])
        x = startPos.getX()
        z = startPos.getZ()-0.03
        self.__createPropertyHeader("Command Arguments", z, parent)
        z = startPos.getZ()
        args = "" if updateElementInfo.extraArgs is None else updateElementInfo.extraArgs
        width = (parent.bounds[1]-10)
        entryWidth = width / 13
        entry = self.__createTextEntry(args, x, z, entryWidth, update, parent)

    def __createOthersSelectorProperty(self, startPos, parent, updateElement):
        def update(selected, selection):
            base.messenger.send("setDirtyFlag")
            if selected:
                updateElement["others"].append(selection.element)
            else:
                updateElement["others"].remove(selection.element)
        x = startPos.getX()
        z = startPos.getZ()
        self.__createPropertyHeader("Others", z, parent)
        z = startPos.getZ()
        z -= (0.06)

        height = 120

        selectionFrame = DirectScrolledFrame(
            pos=(x,0,z),
            frameColor=(1,1,1,1),
            frameSize=(0,parent["frameSize"][1]-20,-height,0),
            canvasSize=(0,parent["frameSize"][1]-20,-height,0),
            scrollBarWidth=20,
            state=DGG.NORMAL,
            parent=parent,
        )
        selectionFrame.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        selectionFrame.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        innerZ = 0
        nextZ = 30
        for keys, radioButton in self.elementDict.items():
            if radioButton.type != "DirectRadioButton": continue
            cb = DirectCheckButton(
                text=radioButton.name,
                pos=(0, 0, innerZ-12),
                indicatorValue=radioButton.element in updateElement["others"],
                boxPlacement="right",
                scale=12,
                text_align=TextNode.ALeft,
                command=update,
                extraArgs=[radioButton],
                parent=selectionFrame.getCanvas())
            cb.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
            cb.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
            innerZ -= 20
        selectionFrame["canvasSize"] = (
            0,selectionFrame["frameSize"][1]-20,
            innerZ, 0)
        selectionFrame.setCanvasSize()
        self.startPos.setZ(self.startPos.getZ() - height)
        self.frameSize += height

    def __createCustomSelectionProperty(self, description, startPos, parent, updateElement, updateAttribute, menuValues):
        def update(selection):
            base.messenger.send("setDirtyFlag")
            updateElement[updateAttribute] = menuValues[selection]
        selectedElement = ""
        for key, value in menuValues.items():
            if value == updateElement[updateAttribute]:
                selectedElement = key

        self.__createOptionMenuProperty(
            description, startPos, parent, updateElement,
            list(menuValues.keys()), selectedElement, update, DGG.ABOVE)

    def __createOptionMenuProperty(self, description, startPos, parent, updateElement, items, selectedElement, command, popupLocation=DGG.BELOW):
        x = startPos.getX()
        z = startPos.getZ()
        self.__createPropertyHeader(description, z, parent)
        z = startPos.getZ()
        menu = DirectOptionMenu(
            items=items,
            pos=(x+10, 0, z+0.0125),
            scale=12,
            popupMenuLocation=popupLocation,
            initialitem=selectedElement,
            command=command,
            parent=parent)
        menu.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        menu.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        self.maxElementWidth = max(menu.bounds[1]*menu.getScale()[0], self.maxElementWidth)

    def __findAllChildren(self, root, path):
        if "DirectGrid" in root.getName(): return
        if self.tmpUpdateElementInfo.element.getName() in path: return
        if path != "root/":
            name = root.getName()
            if len(name.split("-")) > 1:
                name = name.split("-")[1]
            if name not in self.elementDict.keys():
                self.parentList.append("{}{}".format(path, root.getName()))
        if hasattr(root, "getChildren"):
            if root != self.getEditorRootCanvas():
                path += root.getName() + "/"
            for child in root.getChildren():
                self.__findAllChildren(child, path)

    def __createParentProperty(self, startPos, parent, updateElementInfo):
        updateElement = updateElementInfo.element
        self.canvasParents = [
            "a2dTopCenter","a2dBottomCenter","a2dLeftCenter","a2dRightCenter",
            "a2dTopLeft","a2dTopRight","a2dBottomLeft","a2dBottomRight"]
        def update(selection):
            base.messenger.send("setDirtyFlag")
            if selection == "root":
                newParent = self.getEditorRootCanvas()
            elif selection in self.canvasParents:
                newParent = self.getEditorPlacer(selection)
            elif selection.startswith("root/"):
                selection = selection.replace("root/", "**/")
                newParent = self.getEditorRootCanvas().find(selection)
            else:
                newParent = self.getEditorRootCanvas().find("**/{}".format(selection))
            base.messenger.send("setParentOfElement", [updateElement, newParent])
            if not newParent.isEmpty():
                try:
                    updateElement.reparentTo(newParent)
                except:
                    logging.exception("Failed to reparent {} to {}!\nNOTE: Circular parenting is not allowed!".format(updateElement.getName(), newParent.getName()))
                base.messenger.send("refreshStructureTree")
        self.parentList = ["root"] + self.canvasParents
        for guiID, elementInfo in self.elementDict.items():
            if elementInfo.element != updateElement:
                if elementInfo.parent is not None and type(elementInfo.parent) != type(NodePath()):
                    if elementInfo.parent.element != updateElement:
                        self.parentList.append(elementInfo.element.getName())
                else:
                    self.parentList.append(elementInfo.element.getName())

        self.tmpUpdateElementInfo = updateElementInfo
        self.__findAllChildren(self.getEditorRootCanvas(), "root/")
        self.updateElementInfo = None

        selectedElement = None
        if updateElement.getParent() == self.getEditorRootCanvas():
            selectedElement = "root"
        elif updateElement.getParent().getName().replace("canvas", "a2d") in self.canvasParents:
            selectedElement = updateElement.getParent().name

        if selectedElement is None:
            if updateElement.getParent().getName().replace("canvas", "a2d") in self.parentList:
                selectedElement = updateElement.getParent().getName().replace("canvas", "a2d")
            else:
                canvas = str(self.getEditorRootCanvas())
                selectedElement = str(updateElement.getParent()).replace(canvas, "root")

        if selectedElement is None or selectedElement not in self.parentList:
            if updateElement.getParent().getName().replace("canvas", "a2d") in self.parentList:
                selectedElement = updateElement.getParent().getName().replace("canvas", "a2d")
            elif updateElementInfo.parent is not None:
                if "{}-{}".format(updateElementInfo.type, updateElementInfo.parent.element.guiId) in self.parentList:
                    selectedElement = "{}-{}".format(updateElementInfo.type, updateElementInfo.parent.element.guiId)

        self.__createOptionMenuProperty(
            "Parent", startPos, parent, updateElement,
            self.parentList, selectedElement, update)

    def __createCustomAlignProperty(self, description, startPos, parent, updateElement, updateAttribute):
        alignments = {
            "Left":0,
            "Right":1,
            "Center":2,
            "Boxed Left":3,
            "Boxed Right":4,
            "Boxed Center":5}
        def update(selection):
            base.messenger.send("setDirtyFlag")
            updateElement[updateAttribute] = alignments[selection]
        selectedElement = None

        for componentName in updateElement.components():
            if componentName.startswith("text"):
                currentAlign = updateElement.component(componentName).align
                for aName, aValue in alignments.items():
                    if aValue == currentAlign:
                        selectedElement = aName
                        break
                break
        self.__createOptionMenuProperty(
            description, startPos, parent, updateElement,
            list(alignments.keys()), selectedElement, update, DGG.ABOVE)

    def __createTextAlignProperty(self, startPos, parent, updateElement):
        alignments = {
            "Left":0,
            "Right":1,
            "Center":2,
            "Boxed Left":3,
            "Boxed Right":4,
            "Boxed Center":5}
        def update(selection):
            base.messenger.send("setDirtyFlag")
            updateElement["text_align"] = alignments[selection]
        selectedElement = None

        for componentName in updateElement.components():
            if componentName.startswith("text"):
                currentAlign = updateElement.component(componentName).align
                for aName, aValue in alignments.items():
                    if aValue == currentAlign:
                        selectedElement = aName
                        break
                break
        self.__createOptionMenuProperty(
            "Text Align", startPos, parent, updateElement,
            list(alignments.keys()), selectedElement, update)

    def __createTransparencyProperty(self, startPos, parent, updateElement):
        transparencyAttribs = [
            "M_none",
            "M_alpha",
            "M_premultiplied_alpha",
            "M_multisample",
            "M_multisample_mask",
            "M_binary",
            "M_dual"]

        def update(selection):
            base.messenger.send("setDirtyFlag")
            updateElement.setTransparency(getattr(TransparencyAttrib, selection))

        for attrib in transparencyAttribs:
            if getattr(TransparencyAttrib, attrib) == updateElement.getTransparency():
                selectedElement = attrib

        self.__createOptionMenuProperty(
            "Transparency", startPos, parent, updateElement,
            transparencyAttribs, selectedElement, update)

    def __createResetFramesize(self, startPos, parent, updateElement):
        pos = startPos
        pos.setX(pos.getX() + 10)
        box = DirectBoxSizer(parent=parent, pos=startPos)

        #
        # Update Frame
        #
        btn = DirectButton(
            text="Update",
            pad=(0.25,0.25),
            scale=12,
            parent=parent,
            command=updateElement.resetFrameSize
            )
        btn.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        btn.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])

        box.addItem(btn)

        #
        # Reset Frame
        #
        def recalcFrameGeom(updateElement):
            # remove the frame size as otherwise it won't recalculate
            updateElement["frameSize"] = None
            # now force recalculation of the frame size
            updateElement.setFrameSize(fClearFrame = 1)

        btn = DirectButton(
            text="Reset",
            pad=(0.25,0.25),
            scale=12,
            parent=parent,
            command=recalcFrameGeom,
            extraArgs=[updateElement]
            )
        btn.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        btn.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])

        box.addItem(btn)

        #
        # Fit frame to children
        #
        l, r, b, t = [None,None,None,None]

        def getMaxSize(root, baseElement, l, r, b, t):
            if hasattr(root, "getChildren"):
                if len(root.getChildren()) > 0:
                    for child in root.getChildren():

                        elementInfo = None
                        if child.getName() in self.elementDict.keys():
                            elementInfo = self.elementDict[child.getName()]
                        elif len(child.getName().split("-")) > 1 and child.getName().split("-")[1] in self.elementDict.keys():
                            elementInfo = self.elementDict[child.getName().split("-")[1]]

                        if elementInfo is None: continue

                        element = elementInfo.element
                        el = DGH.getRealLeft(element) + element.getX(baseElement)
                        er = DGH.getRealRight(element) + element.getX(baseElement)
                        eb = DGH.getRealBottom(element) + element.getZ(baseElement)
                        et = DGH.getRealTop(element) + element.getZ(baseElement)

                        if l is None:
                            l = el
                        if r is None:
                            r = er
                        if b is None:
                            b = eb
                        if t is None:
                            t = DGH.getRealTop(element) + element.getZ()

                        l = min(l, el)
                        r = max(r, er)
                        b = min(b, eb)
                        t = max(t, et)

                        l,r,b,t = getMaxSize(child, baseElement, l, r, b, t)
            return [l, r, b, t]

        def fitToChildren(updateElement, l, r, b, t):
            l, r, b, t = getMaxSize(updateElement, updateElement, l, r, b, t)
            if l is None or r is None or b is None or t is None: return
            updateElement["frameSize"] = [l, r, b, t]

        btn = DirectButton(
            text="Fit to children",
            pad=(0.25,0.25),
            scale=12,
            parent=parent,
            command=fitToChildren,
            extraArgs=[updateElement, l, r, b, t]
            )
        btn.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        btn.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])

        box.addItem(btn)
