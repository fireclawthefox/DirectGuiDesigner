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
    TextNode,
    Point3,
    TextProperties,
    TransparencyAttrib,
    PGButton,
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

from DirectGuiDesignerFileBrowser import DirectGuiDesignerFileBrowser

class PropertyInfo:
    def __init__(self, displayName, propertyName, propertyType, customCommandName):
        self.displayName = displayName
        self.propertyName = propertyName
        self.propertyType = propertyType
        self.customCommandName = customCommandName

class DirectGuiDesignerProperties():

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
        "text_pos":False, # base3
        "text_fg":False, # base4
        "text_bg":False, # base4
        "image":False, # text
        "image_scale":False, # base3
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
        "decButton_pos":False,
        "decButton_hpr":False,
        "decButton_scale":False,
        "decButton_frameColor":False,
        "decButton_frameSize":False,
        "thumb_pos":False,
        "thumb_hpr":False,
        "thumb_scale":False,
        "thumb_frameColor":False,
        "thumb_frameSize":False,

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
        "frameSize":"getBounds",

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

    def __init__(self, parent, posZ, height, getEditorRootCanvas, getEditorPlacer, tooltip):
        # A list containing the prooperty information
        self.customProperties = []
        self.tooltip = tooltip
        self.parent = parent
        self.maxElementWidth = 0
        self.lblHeader = DirectLabel(
            text="Properties",
            text_scale=16,
            text_pos=(parent["frameSize"][0], 0),
            text_align=TextNode.ALeft,
            text_fg=(1,1,1,1),
            frameSize=VBase4(parent["frameSize"][0], parent["frameSize"][1], -10, 20),
            frameColor=VBase4(0, 0, 0, 0),
            pos=(0,0,posZ-20),
            parent=parent,)
        posZ -= 30
        color = (
            (0.8, 0.8, 0.8, 1), # Normal
            (0.9, 0.9, 1, 1), # Click
            (0.8, 0.8, 1, 1), # Hover
            (0.5, 0.5, 0.5, 1)) # Disabled
        self.propertiesFrame = DirectScrolledFrame(
            # make the frame fit into our background frame
            frameSize=VBase4(parent["frameSize"][0], parent["frameSize"][1], height+30, 0),
            # make the canvas as big as the frame
            canvasSize=VBase4(parent["frameSize"][0], parent["frameSize"][1]-20, height+30, 0),
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
            pos=(0,0,posZ),
            state=DGG.NORMAL,
            parent=parent,)
        self.propertiesFrame.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        self.propertiesFrame.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])

        self.getEditorRootCanvas = getEditorRootCanvas
        self.getEditorPlacer = getEditorPlacer

    def scroll(self, scrollStep, event):
        self.propertiesFrame.verticalScroll.scrollStep(scrollStep)

    def resizeFrame(self, posZ, height):
        self.lblHeader["frameSize"] = (self.parent["frameSize"][0], self.parent["frameSize"][1], -10, 20)
        self.lblHeader["text_pos"] = (self.parent["frameSize"][0], 0)
        self.lblHeader.setPos(0,0,posZ-20)
        posZ -= 30
        self.propertiesFrame["frameSize"] = (self.parent["frameSize"][0], self.parent["frameSize"][1], height+30, 0)
        self.propertiesFrame.setPos(0,0,posZ)

        # refresh properties
        self.clear()
        self.setupProperties(self.headerText, self.elementInfo, self.elementDict)

    def defaultPropertySelection(self):
        self.clearPropertySelection()
        trueValues = ["name", "parent", "relief", "borderWidth", "frameSize",
            "frameColor", "pad", "pos", "hpr", "scale", "sortOrder",
            "enableTransparency", "state", "image", "image_scale"]
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
            text_pos=(0, 0),
            text_align=TextNode.ACenter,
            frameSize=VBase4(-self.propertiesFrame["frameSize"][1]/2, self.propertiesFrame["frameSize"][1]/2, -10, 20),
            frameColor=VBase4(0.7,0.7,0.7,1),
            pos=(self.propertiesFrame["frameSize"][1]/2,0,-20),
            parent=propFrame)
        self.startPos = Point3(self.propertiesFrame["frameSize"][0], 0, -30)
        self.frameSize = 30

        element = elementInfo.element

        try:
            #
            # General Properties
            #
            self.__createInbetweenHeader("General Properties", self.startPos, propFrame)
            self.frameSize += 30
            if self.propertyList["name"]:
                self.__createNameProperty(self.startPos, propFrame, elementInfo)
                self.moveNext()
            if self.propertyList["parent"]:
                self.__createParentProperty(self.startPos, propFrame, elementInfo)
                self.moveNext()
            if self.propertyList["text"]:
                self.__createTextProperty("Text", self.startPos, propFrame, element, "text")
                self.moveNext()
            if self.propertyList["text_align"]:
                self.__createTextAlignProperty(self.startPos, propFrame, element)
                self.moveNext()
            if self.propertyList["text_scale"]:
                self.__createBase2Input("Text Scale", self.startPos, propFrame, element, "text_scale")
                self.moveNext()
            if self.propertyList["text_fg"]:
                self.__createBase4Input("Text Color (r/g/b/a)", self.startPos, propFrame, element, "text_fg")
                self.moveNext()
            if self.propertyList["text_bg"]:
                self.__createBase4Input("Text Background Color (r/g/b/a)", self.startPos, propFrame, element, "text_bg")
                self.moveNext()
            if self.propertyList["text_pos"]:
                self.__createBase2Input("Text Position (X/Y)", self.startPos, propFrame, element, "text_pos")
                self.moveNext()
            if self.propertyList["relief"]:
                self.__createReliefProperty("Relief", self.startPos, propFrame, element)
                self.moveNext()
            if self.propertyList["borderWidth"]:
                self.__createBase2Input("Border Width", self.startPos, propFrame, element, "borderWidth")
                self.moveNext()
            if self.propertyList["frameSize"]:
                self.__createBase4Input("Frame Size (L/R/B/T)", self.startPos, propFrame, element, "frameSize")
                self.moveNext()
                self.__createResetFramesize(self.startPos, propFrame, element)
                self.startPos.setZ(self.startPos.getZ() - 30)
                self.frameSize += 30
            if self.propertyList["frameColor"]:
                self.__createBase4Input("Background Color (r/g/b/a)", self.startPos, propFrame, element, "frameColor")
                self.moveNext()
            if self.propertyList["enableTransparency"]:
                self.__createTransparencyProperty(self.startPos, propFrame, element)
                self.moveNext()
            if self.propertyList["pad"]:
                self.__createBase2Input("Padding", self.startPos, propFrame, element, "pad")
                self.moveNext()
            if self.propertyList["pos"]:
                self.__createBase3Input("Position (X/Y/Z)", self.startPos, propFrame, element, "pos")
                self.moveNext()
            if self.propertyList["hpr"]:
                self.__createBase3Input("Rotation (H/P/R)", self.startPos, propFrame, element, "hpr")
                self.moveNext()
            if self.propertyList["scale"]:
                self.__createBase3Input("Scale", self.startPos, propFrame, element, "scale")
                self.moveNext()
            if self.propertyList["color"]:
                self.__createBase4Input("Color (r/g/b/a)", self.startPos, propFrame, element, "color")
                self.moveNext()
            if self.propertyList["image"]:
                self.__createImageProperty("Image", self.startPos, propFrame, element)
                self.moveNext()
            if self.propertyList["image_scale"]:
                self.__createBase3Input("Image Scale", self.startPos, propFrame, element, "image_scale")
                self.moveNext()
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
            for prop in ["pressEffect"]:
                if self.propertyList[prop]:
                    self.__createInbetweenHeader("Button Properties", self.startPos, propFrame)
                    break
            if self.propertyList["pressEffect"]:
                #TODO: The pressEffect is currently not changeable after initialization!
                self.__createPressEffectProperty("Show press effect", self.startPos, propFrame, elementInfo)
                self.moveNext()

            #
            # Entry specific
            #
            for prop in ["initialText", "width", "numLines", "overflow", "obscured"]:
                if self.propertyList[prop]:
                    self.__createInbetweenHeader("Entry Properties", self.startPos, propFrame)
                    break
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
            for prop in ["canvasSize", "scrollBarWidth"]:
                if self.propertyList[prop]:
                    self.__createInbetweenHeader("Scrolled Frame Properties", self.startPos, propFrame)
                    break
            if self.propertyList["canvasSize"]:
                self.__createBase4Input("Canvas Space (L/R/B/T)", self.startPos, propFrame, element, "canvasSize")
                self.moveNext()
            if self.propertyList["scrollBarWidth"]:
                self.__createFloatInput("Scroll Bar Width", self.startPos, propFrame, element, "scrollBarWidth", True)
                self.moveNext()

            #
            # Scrolled Entry specific
            #
            for prop in ["clipSize"]:
                if self.propertyList[prop]:
                    self.__createInbetweenHeader("Scrolled Entry Properties", self.startPos, propFrame)
                    break
            if self.propertyList["clipSize"]:
                self.__createBase4Input("Clip Size (L/R/B/T)", self.startPos, propFrame, element, "clipSize")
                self.moveNext()

            #
            # Checkbox specific
            #
            for prop in ["uncheckedImage","checkedImage","isChecked"]:
                if self.propertyList[prop]:
                    self.__createInbetweenHeader("Scrolled Entry Properties", self.startPos, propFrame)
                    break
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
                self.__createBase3Input("incButton Position (X/Y/Z)", self.startPos, propFrame, element, "incButton_pos")
                self.moveNext()
            if self.propertyList["incButton_hpr"]:
                self.__createBase3Input("incButton Rotation (H/P/R)", self.startPos, propFrame, element, "incButton_hpr")
                self.moveNext()
            if self.propertyList["incButton_scale"]:
                self.__createBase3Input("incButton Scale", self.startPos, propFrame, element, "incButton_scale")
                self.moveNext()
            if self.propertyList["incButton_frameColor"]:
                self.__createBase4Input("incButton Background Color (r/g/b/a)", self.startPos, propFrame, element, "incButton_frameColor")
                self.moveNext()
            if self.propertyList["incButton_frameSize"]:
                self.__createBase4Input("incButton Frame Size (L/R/B/T)", self.startPos, propFrame, element, "incButton_frameSize")
                self.moveNext()
                incBtn = element.incButton
                self.__createResetFramesize(self.startPos, propFrame, incBtn)
                self.startPos.setZ(self.startPos.getZ() - 30)
                self.frameSize += 30

            for key in self.propertyList.keys():
                if key.startswith("decButton") and self.propertyList[key]:
                    self.__createInbetweenHeader("Dec Button Properties", self.startPos, propFrame)
                    break
            if self.propertyList["decButton_pos"]:
                self.__createBase3Input("decButton Position (X/Y/Z)", self.startPos, propFrame, element, "decButton_pos")
                self.moveNext()
            if self.propertyList["decButton_hpr"]:
                self.__createBase3Input("decButton Rotation (H/P/R)", self.startPos, propFrame, element, "decButton_hpr")
                self.moveNext()
            if self.propertyList["decButton_scale"]:
                self.__createBase3Input("decButton Scale", self.startPos, propFrame, element, "decButton_scale")
                self.moveNext()
            if self.propertyList["decButton_frameColor"]:
                self.__createBase4Input("decButton Background Color (r/g/b/a)", self.startPos, propFrame, element, "decButton_frameColor")
                self.moveNext()
            if self.propertyList["decButton_frameSize"]:
                self.__createBase4Input("decButton Frame Size (L/R/B/T)", self.startPos, propFrame, element, "decButton_frameSize")
                self.moveNext()
                decBtn = element.decButton
                self.__createResetFramesize(self.startPos, propFrame, decBtn)
                self.startPos.setZ(self.startPos.getZ() - 30)
                self.frameSize += 30

            for key in self.propertyList.keys():
                if key.startswith("thumb") and self.propertyList[key]:
                    self.__createInbetweenHeader("Thumb Properties", self.startPos, propFrame)
                    break
            if self.propertyList["thumb_pos"]:
                self.__createBase3Input("thumb Position (X/Y/Z)", self.startPos, propFrame, element, "thumb_pos")
                self.moveNext()
            if self.propertyList["thumb_hpr"]:
                self.__createBase3Input("thumb Rotation (H/P/R)", self.startPos, propFrame, element, "thumb_hpr")
                self.moveNext()
            if self.propertyList["thumb_scale"]:
                self.__createBase3Input("thumb Scale", self.startPos, propFrame, element, "thumb_scale")
                self.moveNext()
            if self.propertyList["thumb_frameColor"]:
                self.__createBase4Input("thumb Background Color (r/g/b/a)", self.startPos, propFrame, element, "thumb_frameColor")
                self.moveNext()
            if self.propertyList["thumb_frameSize"]:
                self.__createBase4Input("thumb Frame Size (L/R/B/T)", self.startPos, propFrame, element, "thumb_frameSize")
                self.moveNext()
                decBtn = element.thumb
                self.__createResetFramesize(self.startPos, propFrame, decBtn)
                self.startPos.setZ(self.startPos.getZ() - 30)
                self.frameSize += 30

            #
            # CheckButton specific
            #
            for prop in ["boxBorder","boxPlacement","boxImage","boxImageScale","boxImageColor","boxRelief", "indicator_text_scale", "indicator_text_pos", "indicator_borderWidth"]:
                if self.propertyList[prop]:
                    self.__createInbetweenHeader("Check Button Properties", self.startPos, propFrame)
                    break
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
                self.__createBase4Input("Box Image Color (r/g/b/a)", self.startPos, propFrame, element, "boxImageColor")
                self.moveNext()
            if self.propertyList["boxRelief"]:
                self.__createReliefProperty("Box Relief", self.startPos, propFrame, element, "boxRelief")
                self.moveNext()
            if self.propertyList["indicator_text_scale"]:
                self.__createBase2Input("Indicator Text Scale", self.startPos, propFrame, element, "indicator_text_scale")
                self.moveNext()
            if self.propertyList["indicator_text_pos"]:
                self.__createBase2Input("Indicator Text Position (X/Y)", self.startPos, propFrame, element, "indicator_text_pos")
                self.moveNext()
            if self.propertyList["indicator_borderWidth"]:
                self.__createBase2Input("Indicator Border Width", self.startPos, propFrame, element, "indicator_borderWidth")
                self.moveNext()

            #
            # RadioButton specific
            #
            for prop in ["others", "indicatorValue"]:
                if self.propertyList[prop]:
                    self.__createInbetweenHeader("Radio Button Properties", self.startPos, propFrame)
                    break
            if self.propertyList["others"]:
                self.__createOthersSelectorProperty(self.startPos, propFrame, element)
            if self.propertyList["indicatorValue"]:
                self.__createBoolProperty("Is selected", self.startPos, propFrame, element, "indicatorValue")
                self.moveNext()

            #
            # OptionMenu specific
            #
            for prop in ["popupMarkerBorder","popupMarker_pos","popupMenuLocation","highlightColor","highlightScale"]:
                if self.propertyList[prop]:
                    self.__createInbetweenHeader("Check Button Properties", self.startPos, propFrame)
                    break
            if self.propertyList["popupMarkerBorder"]:
                self.__createBase2Input("Popup Marker Border", self.startPos, propFrame, element, "popupMarkerBorder")
                self.moveNext()
            if self.propertyList["popupMarker_pos"]:
                self.__createBase3Input("Popup Marker Position (X/Y/Z)", self.startPos, propFrame, element, "popupMarker_pos")
                self.moveNext()
            if self.propertyList["popupMenuLocation"]:
                self.__createPlacementProperty("Popup Menu Location", self.startPos, propFrame, element, "popupMenuLocation")
                self.moveNext()
            if self.propertyList["highlightColor"]:
                self.__createBase4Input("Highlight Color", self.startPos, propFrame, element, "highlightColor")
                self.moveNext()
            if self.propertyList["highlightScale"]:
                self.__createBase2Input("Highlight Scale", self.startPos, propFrame, element, "highlightScale")
                self.moveNext()

            #
            # ScrollBar/Silder specific
            #
            for prop in ["SB-range","scrollSize","pageSize","orientation","manageButtons", "resizeThumb"]:
                if self.propertyList[prop]:
                    self.__createInbetweenHeader("ScrollBar/Slider Properties", self.startPos, propFrame)
                    break
            if self.propertyList["SB-range"]:
                self.__createBase2Input("Bar Range", self.startPos, propFrame, element, "range")
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
            for prop in ["range","barBorderWidth","barColor","barTexture", "barRelief"]:
                if self.propertyList[prop]:
                    self.__createInbetweenHeader("WaitBar Properties", self.startPos, propFrame)
                    break
            if self.propertyList["range"]:
                self.__createFloatInput("Bar Range", self.startPos, propFrame, element, "range")
                self.moveNext()
            if self.propertyList["barBorderWidth"]:
                self.__createBase2Input("Bar Border Width", self.startPos, propFrame, element, "barBorderWidth")
                self.moveNext()
            if self.propertyList["barColor"]:
                self.__createBase4Input("Bar Color", self.startPos, propFrame, element, "barColor")
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
                    self.__createBase2Input(prop.displayName, self.startPos, propFrame, element, prop.propertyName)
                    self.moveNext()
                elif prop.propertyType.lower() == "vbase3":
                    self.__createBase3Input(prop.displayName, self.startPos, propFrame, element, prop.propertyName)
                    self.moveNext()
                elif prop.propertyType.lower() == "vbase4":
                    self.__createBase4Input(prop.displayName, self.startPos, propFrame, element, prop.propertyName)
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

        self.curPropFrame = propFrame

    def clear(self):
        if self.curPropFrame is not None:
            self.curPropFrame.destroy()

    def __createInbetweenHeader(self, description, startPos, parent):
        x = startPos.getX()
        z = startPos.getZ()
        DirectLabel(
            text=description,
            text_scale=16,
            text_pos=(0, 0),
            text_align=TextNode.ACenter,
            frameSize=VBase4(-self.propertiesFrame["frameSize"][1]/2, self.propertiesFrame["frameSize"][1]/2, -10, 20),
            frameColor=VBase4(0.85,0.85,0.85,1),
            pos=(self.propertiesFrame["frameSize"][1]/2,0,z-20),
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

    def __createBase4Input(self, description, startPos, parent, updateElement, updateAttribute):
        def update(text):
            base.messenger.send("setDirtyFlag")
            valueA = 0.0
            try:
                valueA = float(a.get(True))
            except:
                logging.exception("ERROR: NAN", valueA)
            valueB = 0.0
            try:
                valueB = float(b.get(True))
            except:
                logging.exception("ERROR: NAN", valueB)
            valueC = 0.0
            try:
                valueC = float(c.get(True))
            except:
                logging.exception("ERROR: NAN", valueC)
            valueD = 0.0
            try:
                valueD = float(d.get(True))
            except:
                logging.exception("ERROR: NAN", valueD)
            if updateAttribute in self.initOpDict:
                if hasattr(updateElement, self.initOpDict[updateAttribute]):
                    getattr(updateElement, self.initOpDict[updateAttribute])(
                        valueA,
                        valueB,
                        valueC,
                        valueD)
            elif updateAttribute in self.subControlInitOpDict:
                if hasattr(updateElement, self.subControlInitOpDict[updateAttribute][0]):
                    control = getattr(updateElement, self.subControlInitOpDict[updateAttribute][0])
                    if hasattr(control, self.subControlInitOpDict[updateAttribute][1]):
                        getattr(control, self.subControlInitOpDict[updateAttribute][1])(
                            valueA,
                            valueB,
                            valueC,
                            valueD)
            else:
                updateElement[updateAttribute] = (
                    valueA,
                    valueB,
                    valueC,
                    valueD)
        x = startPos.getX()
        z = startPos.getZ()
        self.__createPropertyHeader(description, z, parent)
        z = startPos.getZ()
        valueA = valueB = valueC = valueD = 0
        if updateAttribute in self.initOpGetDict or updateAttribute in self.subControlInitOpGetDict or updateAttribute in self.getAsPropDict:
            v = self.__getValues(updateElement, updateAttribute)
            if v is not None:
                valueA, valueB, valueC, valueD = v
        elif "image_" in updateAttribute:
            parts = updateAttribute.split("_")
            if updateElement[parts[0]] is not None:
                valueA = updateElement[updateAttribute][0]
                valueB = updateElement[updateAttribute][1]
                valueC = updateElement[updateAttribute][2]
                valueD = updateElement[updateAttribute][3]
        elif updateElement[updateAttribute] is not None:
            valueA = updateElement[updateAttribute][0]
            valueB = updateElement[updateAttribute][1]
            valueC = updateElement[updateAttribute][2]
            valueD = updateElement[updateAttribute][3]

        valueA = self.__getFormated(valueA)
        valueB = self.__getFormated(valueB)
        valueC = self.__getFormated(valueC)
        valueD = self.__getFormated(valueD)
        width = (parent.bounds[1]-10) / 4
        entryWidth = width / 13
        a = self.__createTextEntry(str(valueA), x, z, entryWidth, update, parent)
        x += width
        b = self.__createTextEntry(str(valueB), x, z, entryWidth, update, parent)
        x += width
        c = self.__createTextEntry(str(valueC), x, z, entryWidth, update, parent)
        x += width
        d = self.__createTextEntry(str(valueD), x, z, entryWidth, update, parent)

    def __createBase3Input(self, description, startPos, parent, updateElement, updateAttribute):
        def update(text):
            base.messenger.send("setDirtyFlag")
            valueA = 0.0
            try:
                valueA = float(a.get(True))
            except:
                logging.exception("ERROR: NAN", valueA)
            valueB = 0.0
            try:
                valueB = float(b.get(True))
            except:
                logging.exception("ERROR: NAN", valueB)
            valueC = 0.0
            try:
                valueC = float(c.get(True))
            except:
                logging.exception("ERROR: NAN", valueC)
            if updateAttribute in self.initOpDict:
                if hasattr(updateElement, self.initOpDict[updateAttribute]):
                    getattr(updateElement, self.initOpDict[updateAttribute])(
                        valueA,
                        valueB,
                        valueC)
            elif updateAttribute in self.subControlInitOpDict:
                if hasattr(updateElement, self.subControlInitOpDict[updateAttribute][0]):
                    control = getattr(updateElement, self.subControlInitOpDict[updateAttribute][0])
                    if hasattr(control, self.subControlInitOpDict[updateAttribute][1]):
                        getattr(control, self.subControlInitOpDict[updateAttribute][1])(
                            valueA,
                            valueB,
                            valueC)
            else:
                updateElement[updateAttribute] = (
                    valueA,
                    valueB,
                    valueC)
        x = startPos.getX()
        z = startPos.getZ()
        self.__createPropertyHeader(description, z, parent)
        z = startPos.getZ()
        valueA = valueB = valueC = 0

        if updateAttribute in self.initOpGetDict or updateAttribute in self.subControlInitOpGetDict or updateAttribute in self.getAsPropDict:
            v = self.__getValues(updateElement, updateAttribute)
            if v is not None:
                valueA, valueB, valueC = v
        elif "image_" in updateAttribute:
            parts = updateAttribute.split("_")
            if updateElement[parts[0]] is not None:
                valueA = updateElement[updateAttribute][0]
                valueB = updateElement[updateAttribute][1]
                valueC = updateElement[updateAttribute][2]
        elif updateElement[updateAttribute] is not None:
            valueA = updateElement[updateAttribute][0]
            valueB = updateElement[updateAttribute][1]
            valueC = updateElement[updateAttribute][2]

        valueA = self.__getFormated(valueA)
        valueB = self.__getFormated(valueB)
        valueC = self.__getFormated(valueC)
        width = (parent.bounds[1]-10) / 3
        entryWidth = width / 13
        a = self.__createTextEntry(str(valueA), x, z, entryWidth, update, parent)
        x += width
        b = self.__createTextEntry(str(valueB), x, z, entryWidth, update, parent)
        x += width
        c = self.__createTextEntry(str(valueC), x, z, entryWidth, update, parent)

    def __createBase2Input(self, description, startPos, parent, updateElement, updateAttribute):
        def update(text):
            base.messenger.send("setDirtyFlag")
            valueA = 0.0
            try:
                valueA = float(a.get(True))
            except:
                logging.exception("ERROR: NAN", valueA)
            valueB = 0.0
            try:
                valueB = float(b.get(True))
            except:
                logging.exception("ERROR: NAN", valueB)
            if updateAttribute in self.initOpDict:
                if hasattr(updateElement, self.initOpDict[updateAttribute]):
                    getattr(updateElement, self.initOpDict[updateAttribute])(
                        valueA,
                        valueB)
            elif updateAttribute in self.subControlInitOpDict:
                if hasattr(updateElement, self.subControlInitOpDict[updateAttribute][0]):
                    control = getattr(updateElement, self.subControlInitOpDict[updateAttribute][0])
                    if hasattr(control, self.subControlInitOpDict[updateAttribute][1]):
                        getattr(control, self.subControlInitOpDict[updateAttribute][1])(
                            valueA,
                            valueB)
            else:
                updateElement[updateAttribute] = (
                    valueA,
                    valueB)
        x = startPos.getX()
        z = startPos.getZ()
        self.__createPropertyHeader(description, z, parent)
        z = startPos.getZ()
        valueA = valueB = 0
        if updateAttribute in self.initOpGetDict or updateAttribute in self.subControlInitOpGetDict or updateAttribute in self.getAsPropDict:
            v = self.__getValues(updateElement, updateAttribute)
            if v is not None:
                valueA, valueB = v
        elif "image_" in updateAttribute:
            parts = updateAttribute.split("_")
            if updateElement[parts[0]] is not None:
                valueA = updateElement[updateAttribute][0]
                valueB = updateElement[updateAttribute][1]
        elif updateElement[updateAttribute] is not None:
            valueA = updateElement[updateAttribute][0]
            valueB = updateElement[updateAttribute][1]

        valueA = self.__getFormated(valueA)
        valueB = self.__getFormated(valueB)
        width = (parent.bounds[1]-10) / 2
        entryWidth = width / 13
        a = self.__createTextEntry(str(valueA), x, z, entryWidth, update, parent)
        x += width
        b = self.__createTextEntry(str(valueB), x, z, entryWidth, update, parent)

    def __createFloatInput(self, description, startPos, parent, updateElement, updateAttribute, resetFrameSize=False):
        def update(text):
            base.messenger.send("setDirtyFlag")
            value = 0.0
            try:
                value = float(text)
            except:
                logging.exception("ERROR: NAN", value)
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

    def __createBoolProperty(self, description, startPos, parent, updateElement, updateAttribute):
        def update(value):
            base.messenger.send("setDirtyFlag")
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
            self.browser = DirectGuiDesignerFileBrowser(selectPath, True, ConfigVariableString("work-dir-path", "~").getValue(), "", self.tooltip)
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

    def __createReliefProperty(self, description, startPos, parent, updateElement, updateAttribute="relief"):
        def update(selection):
            base.messenger.send("setDirtyFlag")
            updateElement[updateAttribute] = DGG.FrameStyleDict[selection]
        selectedElement = None
        for key, value in DGG.FrameStyleDict.items():
            if value == updateElement[updateAttribute]:
                selectedElement = key
                break
        self.__createOptionMenuProperty(
            description, startPos, parent, updateElement,
            list(DGG.FrameStyleDict.keys()), selectedElement, update)

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
            pos=(self.parent.getWidth() / 2, 0, z-3),
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

    def __createOptionMenuProperty(self, description, startPos, parent, updateElement, items, selectedElement, command):
        x = startPos.getX()
        z = startPos.getZ()
        self.__createPropertyHeader(description, z, parent)
        z = startPos.getZ()
        menu = DirectOptionMenu(
            items=items,
            pos=(x+10, 0, z+0.0125),
            scale=12,
            popupMenuLocation=DGG.BELOW,
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
        x = startPos.getX()
        z = startPos.getZ()
        btn = DirectButton(
            text="Update Frame Size",
            pad=(0.25,0.25),
            pos=(self.parent.getWidth() / 2, 0, z-15),
            scale=12,
            parent=parent,
            command=updateElement.resetFrameSize
            )
        btn.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        btn.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
