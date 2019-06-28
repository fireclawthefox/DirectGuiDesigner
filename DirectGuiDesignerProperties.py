#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

from panda3d.core import VBase4, TextNode, Point3, TextProperties, TransparencyAttrib

from direct.gui import DirectGuiGlobals as DGG
DGG.BELOW = "below"
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectScrolledFrame import DirectScrolledFrame
from direct.gui.DirectEntry import DirectEntry
from direct.gui.DirectButton import DirectButton
#from direct.gui.DirectOptionMenu import DirectOptionMenu
from DirectOptionMenu import DirectOptionMenu
from direct.gui.DirectCheckButton import DirectCheckButton

class DirectGuiDesignerProperties():

    propertyList = {
        "name":False, # text
        "parent":False, # option menu
        "relief":False, # option menu
        "borderWidth":False, # base2
        "frameSize":False, # base4
        "frameColor":False, # base4
        "canvasSize":False, # base4
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
        "sortOrder":False, # int
        "enableTransparency":False, # bool

        "command":False, # text

        # Entry specific
        "initialText":False, # text
        "width":False, # float
        "numLines":False, # int
        "overflow":False, # bool
        "obscured":False, # bool

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
        "text_pos":"pos",
    }
    subControlInitOpGetDict = {
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

    def __init__(self, parent, posZ, height, visualEditor):
        self.maxElementWidth = 0
        DirectLabel(
            text="Properties",
            text_scale=0.05,
            text_pos=(parent["frameSize"][0], -0.015),
            text_align=TextNode.ALeft,
            text_fg=(1,1,1,1),
            frameSize=VBase4(parent["frameSize"][0], parent["frameSize"][1], 0.03, -0.03),
            frameColor=VBase4(0, 0, 0, 0),
            pos=(0,0,posZ-0.03),
            parent=parent)
        posZ -= 0.06
        color = (
            (0.8, 0.8, 0.8, 1), # Normal
            (0.9, 0.9, 1, 1), # Click
            (0.8, 0.8, 1, 1), # Hover
            (0.5, 0.5, 0.5, 1)) # Disabled
        self.propertiesFrame = DirectScrolledFrame(
            # make the frame fit into our background frame
            frameSize=VBase4(parent["frameSize"][0], parent["frameSize"][1], -(height-0.08), 0),
            # make the canvas as big as the frame
            canvasSize=VBase4(parent["frameSize"][0], parent["frameSize"][1]-0.04, -1, 0.0),
            # set the frames color to transparent
            frameColor=VBase4(1, 1, 1, 1),
            scrollBarWidth=0.04,
            verticalScroll_scrollSize=0.04,
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
            pos=(0,0,posZ),)
        self.propertiesFrame.reparentTo(parent)

        self.visualEditor = visualEditor

    def defaultPropertySelection(self):
        self.clearPropertySelection()
        trueValues = ["name", "parent","relief","borderWidth","frameSize","frameColor","pad","pos","hpr","scale", "sortOrder", "enableTransparency"]
        for value in trueValues:
            self.propertyList[value] = True

    def defaultTextPropertySelection(self):
        for key in self.propertyList.keys():
            if key.startswith("text"):
                self.propertyList[key] = True

    def clearPropertySelection(self):
        for key in self.propertyList.keys():
            self.propertyList[key] = False

    def moveNext(self):
        self.startPos.setZ(self.startPos.getZ() - 0.13)
        self.frameSize += 0.13

    def setupProperties(self, headerText, elementInfo, elementDict):
        self.elementDict = elementDict
        propFrame = DirectFrame(
            frameSize=(self.propertiesFrame["frameSize"][0], self.propertiesFrame["frameSize"][1]-0.04, -0.5, 0.0),
            frameColor=VBase4(0,0,0,0),
            parent=self.propertiesFrame.getCanvas())
        DirectLabel(
            text=headerText,
            text_scale=0.05,
            text_pos=(0, -0.015),
            text_align=TextNode.ACenter,
            frameSize=VBase4(self.propertiesFrame["frameSize"][0], self.propertiesFrame["frameSize"][1], 0.03, -0.03),
            frameColor=VBase4(0.7,0.7,0.7,1),
            pos=(0,0,-0.03),
            parent=propFrame)
        self.startPos = Point3(self.propertiesFrame["frameSize"][0], 0, -0.06)
        self.frameSize = 0.06

        element = elementInfo.element

        #
        # General Properties
        #
        self.__createInbetweenHeader("General Properties", self.startPos, propFrame)
        self.frameSize += 0.035
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
            self.__createResetFramesize("Reset Frame Size", self.startPos, propFrame, element)
            self.startPos.setZ(self.startPos.getZ() - 0.065)
            self.frameSize += 0.13
        if self.propertyList["frameColor"]:
            self.__createBase4Input("Background Color (r/g/b/a)", self.startPos, propFrame, element, "frameColor")
            self.moveNext()
        if self.propertyList["enableTransparency"]:
            self.__createTransparencyProperty(self.startPos, propFrame, element)
            self.moveNext()
        if self.propertyList["canvasSize"]:
            self.__createBase4Input("Canvas Space (L/R/B/T)", self.startPos, propFrame, element, "canvasSize")
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
        if self.propertyList["sortOrder"]:
            self.__createIntegerInput("Sort Order", self.startPos, propFrame, element, "sortOrder")
            self.moveNext()
        if self.propertyList["command"]:
            self.__createCommandProperty(self.startPos, propFrame, elementInfo)
            self.moveNext()
            self.__createCommandArgsProperty(self.startPos, propFrame, elementInfo)
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
            self.__createFloatInput("Textfield Width", self.startPos, propFrame, element, "width")
            self.moveNext()
        if self.propertyList["numLines"]:
            self.__createIntegerInput("Number of Lines", self.startPos, propFrame, element, "numLines")
            self.moveNext()
        if self.propertyList["overflow"]:
            self.__createBoolProperty("Enable Overflow", self.startPos, propFrame, element, "overflow")
            self.moveNext()
        if self.propertyList["obscured"]:
            self.__createBoolProperty("Obscured Text", self.startPos, propFrame, element, "obscured")
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
            self.__createResetFramesize("Reset Frame Size", self.startPos, propFrame, incBtn)
            self.startPos.setZ(self.startPos.getZ() - 0.065)
            self.frameSize += 0.13

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
            self.__createResetFramesize("Reset Frame Size", self.startPos, propFrame, decBtn)
            self.startPos.setZ(self.startPos.getZ() - 0.065)
            self.frameSize += 0.13

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
            self.__createResetFramesize("Reset Frame Size", self.startPos, propFrame, decBtn)
            self.startPos.setZ(self.startPos.getZ() - 0.065)
            self.frameSize += 0.13

        #
        # CheckButton specific
        #
        for prop in ["boxBorder","boxPlacement","boxImage","boxImageScale","boxImageColor","boxRelief"]:
            if self.propertyList[prop]:
                self.__createInbetweenHeader("Check Button Properties", self.startPos, propFrame)
                break
        if self.propertyList["boxBorder"]:
            self.__createFloatInput("Box Border Width", self.startPos, propFrame, element, "boxBorder")
            self.moveNext()
        if self.propertyList["boxPlacement"]:
            # boxPlacement maps left, above, right, below
            self.__createBoxPlacementProperty("Box Placement", self.startPos, propFrame, element, "boxPlacement")
            self.moveNext()
        if self.propertyList["boxImage"]:
            self.__createImageProperty("Box Image", self.startPos, propFrame, element, "boxImage")
            self.moveNext()
        if self.propertyList["boxImageScale"]:
            self.__createFloatInput("Box Image scale (X/Y/Z)", self.startPos, propFrame, element, "boxImageScale")
            self.moveNext()
        if self.propertyList["boxImageColor"]:
            self.__createBase4Input("Box Image Color (r/g/b/a)", self.startPos, propFrame, element, "boxImageColor")
            self.moveNext()
        if self.propertyList["boxRelief"]:
            self.__createReliefProperty("Box Relief", self.startPos, propFrame, element, "boxRelief")
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
            self.__createBoxPlacementProperty("Popup Menu Location", self.startPos, propFrame, element, "popupMenuLocation")
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
            self.__createBase2Input("Bar Color", self.startPos, propFrame, element, "range")
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

        propFrame["frameSize"] = (
            self.propertiesFrame["frameSize"][0], self.propertiesFrame["frameSize"][1]-0.04,
            -self.frameSize, 0.0)

        self.propertiesFrame["canvasSize"] = (
            self.propertiesFrame["frameSize"][0], max(self.propertiesFrame["frameSize"][1]-0.04, self.maxElementWidth),
            propFrame.bounds[2]-0.04, 0)
        self.propertiesFrame.setCanvasSize()

        self.curPropFrame = propFrame

    def clear(self):
        if self.curPropFrame is not None:
            self.curPropFrame.destroy()

    def __createInbetweenHeader(self, description, startPos, parent):
        x = startPos.getX()
        z = startPos.getZ()-0.035
        DirectLabel(
            text=description,
            text_scale=0.07,
            #text_pos=(self.propertiesFrame["frameSize"][0], -0.015),
            text_pos=(0, -0.015),
            text_align=TextNode.ACenter,
            frameSize=VBase4(self.propertiesFrame["frameSize"][0], self.propertiesFrame["frameSize"][1], 0.03, -0.03),
            frameColor=VBase4(0.85,0.85,0.85,1),
            pos=(0,0,z),
            parent=parent)
        self.startPos.setZ(self.startPos.getZ() - 0.07)
        self.frameSize += 0.035

    def __createPropertyHeader(self, description, z, parent):
        DirectLabel(
            text=description,
            text_scale=0.05,
            text_pos=(self.propertiesFrame["frameSize"][0], -0.015),
            text_align=TextNode.ALeft,
            frameSize=VBase4(self.propertiesFrame["frameSize"][0], self.propertiesFrame["frameSize"][1], 0.03, -0.03),
            frameColor=VBase4(0.85,0.85,0.85,1),
            pos=(0,0,z),
            parent=parent)

    def __getFormated(self, value):
        if type(value) is int:
            return "{}".format(value)
        else:
            return "{:0.3}".format(value)

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

    def __createBase4Input(self, description, startPos, parent, updateElement, updateAttribute):
        def update(text):
            valueA = 0.0
            try:
                valueA = float(a.get(True))
            except:
                print("ERROR: NAN", valueA)
            valueB = 0.0
            try:
                valueB = float(b.get(True))
            except:
                print("ERROR: NAN", valueB)
            valueC = 0.0
            try:
                valueC = float(c.get(True))
            except:
                print("ERROR: NAN", valueC)
            valueD = 0.0
            try:
                valueD = float(d.get(True))
            except:
                print("ERROR: NAN", valueD)
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
        z = startPos.getZ()-0.03
        self.__createPropertyHeader(description, z, parent)
        valueA = valueB = valueC = valueD = 0
        if updateAttribute in self.initOpGetDict or updateAttribute in self.subControlInitOpGetDict or updateAttribute in self.getAsPropDict:
            valueA, valueB, valueC, valueD = self.__getValues(updateElement, updateAttribute)
        elif updateElement[updateAttribute] is not None:
            valueA = updateElement[updateAttribute][0]
            valueB = updateElement[updateAttribute][1]
            valueC = updateElement[updateAttribute][2]
            valueD = updateElement[updateAttribute][3]

        valueA = self.__getFormated(valueA)
        valueB = self.__getFormated(valueB)
        valueC = self.__getFormated(valueC)
        valueD = self.__getFormated(valueD)
        z -= (0.06+0.025) # 0.025 = half height of the following DirectEntries
        a = DirectEntry(
            initialText=str(valueA),
            pos=(x+0.05, 0, z),
            scale=0.05,
            width=2.5,
            overflow=True,
            command=update,
            parent=parent)
        x += 0.15
        b = DirectEntry(
            initialText=str(valueB),
            pos=(x+0.05, 0, z),
            scale=0.05,
            width=2.5,
            overflow=True,
            command=update,
            parent=parent)
        x += 0.15
        c = DirectEntry(
            initialText=str(valueC),
            pos=(x+0.05, 0, z),
            scale=0.05,
            width=2.5,
            overflow=True,
            command=update,
            parent=parent)
        x += 0.15
        d = DirectEntry(
            initialText=str(valueD),
            pos=(x+0.05, 0, z),
            scale=0.05,
            width=2.5,
            overflow=True,
            command=update,
            parent=parent)

    def __createBase3Input(self, description, startPos, parent, updateElement, updateAttribute):
        def update(text):
            valueA = 0.0
            try:
                valueA = float(a.get(True))
            except:
                print("ERROR: NAN", valueA)
            valueB = 0.0
            try:
                valueB = float(b.get(True))
            except:
                print("ERROR: NAN", valueB)
            valueC = 0.0
            try:
                valueC = float(c.get(True))
            except:
                print("ERROR: NAN", valueC)
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
        z = startPos.getZ()-0.03
        self.__createPropertyHeader(description, z, parent)
        valueA = valueB = valueC = 0
        if updateAttribute in self.initOpGetDict or updateAttribute in self.subControlInitOpGetDict or updateAttribute in self.getAsPropDict:
            valueA, valueB, valueC = self.__getValues(updateElement, updateAttribute)
        elif updateElement[updateAttribute] is not None:
            valueA = updateElement[updateAttribute][0]
            valueB = updateElement[updateAttribute][1]
            valueC = updateElement[updateAttribute][2]

        valueA = self.__getFormated(valueA)
        valueB = self.__getFormated(valueB)
        valueC = self.__getFormated(valueC)
        z -= (0.06+0.025) # 0.025 = half height of the following DirectEntries
        a = DirectEntry(
            initialText=str(valueA),
            pos=(x+0.05, 0, z),
            scale=0.05,
            width=2.5,
            overflow=True,
            command=update,
            parent=parent)
        x += 0.15
        b = DirectEntry(
            initialText=str(valueB),
            pos=(x+0.05, 0, z),
            scale=0.05,
            width=2.5,
            overflow=True,
            command=update,
            parent=parent)
        x += 0.15
        c = DirectEntry(
            initialText=str(valueC),
            pos=(x+0.05, 0, z),
            scale=0.05,
            width=2.5,
            overflow=True,
            command=update,
            parent=parent)

    def __createBase2Input(self, description, startPos, parent, updateElement, updateAttribute):
        def update(text):
            valueA = 0.0
            try:
                valueA = float(a.get(True))
            except:
                print("ERROR: NAN", valueA)
            valueB = 0.0
            try:
                valueB = float(b.get(True))
            except:
                print("ERROR: NAN", valueB)
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
            elif updateAttribute in self.getAsPropDict:
                if hasattr(updateElement, self.getAsPropDict[updateAttribute]):
                    valueA, valueB = getattr(updateElement, self.getAsPropDict[updateAttribute])
                    valueA = self.__getFormated(valueA)
                    valueB = self.__getFormated(valueB)
            else:
                updateElement[updateAttribute] = (
                    valueA,
                    valueB)
        x = startPos.getX()
        z = startPos.getZ()-0.03
        self.__createPropertyHeader(description, z, parent)
        valueA = valueB = 0
        if updateAttribute in self.initOpGetDict or updateAttribute in self.subControlInitOpGetDict or updateAttribute in self.getAsPropDict:
            v = self.__getValues(updateElement, updateAttribute)
            if v is not None:
                valueA, valueB = v
        elif updateElement[updateAttribute] is not None:
            valueA = updateElement[updateAttribute][0]
            valueB = updateElement[updateAttribute][1]

        valueA = self.__getFormated(valueA)
        valueB = self.__getFormated(valueB)
        z -= (0.06+0.025) # 0.025 = half height of the following DirectEntries
        a = DirectEntry(
            initialText=str(valueA),
            pos=(x+0.05, 0, z),
            scale=0.05,
            width=2.5,
            overflow=True,
            command=update,
            parent=parent)
        x += 0.15
        b = DirectEntry(
            initialText=str(valueB),
            pos=(x+0.05, 0, z),
            scale=0.05,
            width=2.5,
            overflow=True,
            command=update,
            parent=parent)

    def __createFloatInput(self, description, startPos, parent, updateElement, updateAttribute):
        def update(text):
            value = 0.0
            try:
                value = float(text)
            except:
                print("ERROR: NAN", value)
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
        z = startPos.getZ()-0.03
        self.__createPropertyHeader(description, z, parent)
        valueA = 0
        if updateAttribute in self.initOpGetDict or updateAttribute in self.subControlInitOpGetDict or updateAttribute in self.getAsPropDict:
            valueA = self.__getValues(updateElement, updateAttribute)
        elif updateElement[updateAttribute] is not None:
            valueA = updateElement[updateAttribute]

        valueA = self.__getFormated(valueA)
        z -= (0.06+0.025) # 0.025 = half height of the following DirectEntries
        DirectEntry(
            initialText=str(valueA),
            pos=(x+0.05, 0, z),
            scale=0.05,
            width=5,
            overflow=True,
            command=update,
            parent=parent)

    def __createIntegerInput(self, description, startPos, parent, updateElement, updateAttribute):
        def update(text):
            value = 0
            try:
                value = int(text)
            except:
                print("ERROR: NAN", value)
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
        x = startPos.getX()
        z = startPos.getZ()-0.03
        self.__createPropertyHeader(description, z, parent)
        valueA = 0
        if updateAttribute in self.initOpGetDict or updateAttribute in self.subControlInitOpGetDict or updateAttribute in self.getAsPropDict:
            valueA = self.__getValues(updateElement, updateAttribute)
        elif updateElement[updateAttribute] is not None:
            valueA = updateElement[updateAttribute]

        valueA = self.__getFormated(valueA)
        z -= (0.06+0.025) # 0.025 = half height of the following DirectEntries
        DirectEntry(
            initialText=str(valueA),
            pos=(x+0.05, 0, z),
            scale=0.05,
            width=5,
            overflow=True,
            command=update,
            parent=parent)

    def __createNameProperty(self, startPos, parent, updateElementInfo):
        def update(text):
            name = updateElementInfo.element.guiId.replace("-", "")
            if text != "":
                name = text
            base.messenger.send("setName", [updateElementInfo, name])
        x = startPos.getX()
        z = startPos.getZ()-0.03
        self.__createPropertyHeader("Name", z, parent)
        z -= (0.06+0.025) # 0.025 = half height of the following DirectEntries
        text = updateElementInfo.elementName
        DirectEntry(
            initialText=text,
            pos=(x+0.05, 0, z),
            scale=0.05,
            width=12,
            overflow=True,
            command=update,
            parent=parent)


    def __createTextProperty(self, description, startPos, parent, updateElement, updateAttribute):
        def update(text):

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
        z = startPos.getZ()-0.03
        self.__createPropertyHeader(description, z, parent)
        z -= (0.06+0.025) # 0.025 = half height of the following DirectEntries
        text = ""
        if updateAttribute in self.initOpGetDict or updateAttribute in self.subControlInitOpGetDict or updateAttribute in self.getAsPropDict:
            text = self.__getValues(updateElement, updateAttribute)
        elif updateElement[updateAttribute] is not None:
            text = updateElement[updateAttribute]
        DirectEntry(
            initialText=text,
            pos=(x+0.05, 0, z),
            scale=0.05,
            width=12,
            overflow=True,
            command=update,
            parent=parent)

    def __createCommandProperty(self, startPos, parent, updateElementInfo):
        def update(text):
            command = None
            if text != "":
                command = text
            base.messenger.send("setCommand", [updateElementInfo, command])
        x = startPos.getX()
        z = startPos.getZ()-0.03
        self.__createPropertyHeader("Command", z, parent)
        z -= (0.06+0.025) # 0.025 = half height of the following DirectEntries
        cmd = "" if updateElementInfo.command is None else updateElementInfo.command
        DirectEntry(
            initialText=cmd,
            pos=(x+0.05, 0, z),
            scale=0.05,
            width=12,
            overflow=True,
            command=update,
            parent=parent)

    def __createCommandArgsProperty(self, startPos, parent, updateElementInfo):
        def update(text):
            extraArgs = None
            if text != "":
                extraArgs = text
            base.messenger.send("setExtraArgs", [updateElementInfo, extraArgs])
        x = startPos.getX()
        z = startPos.getZ()-0.03
        self.__createPropertyHeader("Command Arguments", z, parent)
        z -= (0.06+0.025) # 0.025 = half height of the following DirectEntries
        args = "" if updateElementInfo.extraArgs is None else updateElementInfo.extraArgs
        DirectEntry(
            initialText=args,
            pos=(x+0.05, 0, z),
            scale=0.05,
            width=12,
            overflow=True,
            command=update,
            parent=parent)

    def __createBoolProperty(self, description, startPos, parent, updateElement, updateAttribute):
        def update(value):
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
        z = startPos.getZ()-0.03
        self.__createPropertyHeader(description, z, parent)
        valueA = 0
        if updateAttribute in self.initOpGetDict or updateAttribute in self.subControlInitOpGetDict or updateAttribute in self.getAsPropDict:
            valueA = self.__getValues(updateElement, updateAttribute)
        elif updateElement[updateAttribute] is not None:
            valueA = updateElement[updateAttribute]
        z -= (0.06)
        DirectCheckButton(
            pos=(x+0.05, 0, z),
            indicatorValue=valueA,
            boxPlacement="right",
            scale=0.05,
            text_align=TextNode.ALeft,
            command=update,
            parent=parent)

    def __createOthersSelectorProperty(self, startPos, parent, updateElement):
        def update(selected, selection):
            print(selected, selection)
            if selected:
                updateElement["others"].append(selection.element)
            else:
                updateElement["others"].remove(selection.element)
        x = startPos.getX()
        z = startPos.getZ()-0.03
        self.__createPropertyHeader("Others", z, parent)
        z -= (0.06)

        selectionFrame = DirectScrolledFrame(
            pos=(x,0,z),
            frameColor=(1,1,1,1),
            frameSize=(0,parent["frameSize"][1]*2+0.04,-0.2,0),
            canvasSize=(0,parent["frameSize"][1]*2+0.04,-0.2,0),
            scrollBarWidth=0.04,
            parent=parent,
        )
        innerZ = 0
        nextZ = 0.13
        for keys, radioButton in self.elementDict.items():
            #if radioButton == updateElement: continue
            if radioButton.elementType != "DirectRadioButton": continue
            DirectCheckButton(
                text=radioButton.elementName,
                pos=(0, 0, innerZ-0.035),
                indicatorValue=radioButton.element in updateElement["others"],
                boxPlacement="right",
                scale=0.05,
                text_align=TextNode.ALeft,
                command=update,
                extraArgs=[radioButton],
                parent=selectionFrame.getCanvas())
            innerZ -= 0.07
        selectionFrame["canvasSize"] = (
            0,parent["frameSize"][1]*0.2-0.04,
            innerZ, 0)
        selectionFrame.setCanvasSize()
        self.startPos.setZ(self.startPos.getZ() - 0.3)
        self.frameSize += 0.3

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
            updateElement.setTransparency(getattr(TransparencyAttrib, selection))

        for attrib in transparencyAttribs:
            if getattr(TransparencyAttrib, attrib) == updateElement.getTransparency():
                selectedElement = attrib

        self.__createOptionMenuProperty(
            "Transparency", startPos, parent, updateElement,
            transparencyAttribs, selectedElement, update)

    def __createImageProperty(self, description, startPos, parent, updateElement, updateAttribute="image"):
        def update(text):
            try:
                updateElement[updateAttribute] = text
            except:
                print("Couldn't load image: {}".format(text))
                updateElement[updateAttribute] = None
        x = startPos.getX()
        z = startPos.getZ()-0.03
        self.__createPropertyHeader(description, z, parent)
        z -= (0.06+0.025) # 0.025 = half height of the following DirectEntries
        image = updateElement[updateAttribute]
        DirectEntry(
            initialText=image,
            pos=(x+0.05, 0, z),
            scale=0.05,
            width=12,
            overflow=True,
            command=update,
            parent=parent)

    def __createOptionMenuProperty(self, description, startPos, parent, updateElement, items, selectedElement, command):
        x = startPos.getX()
        z = startPos.getZ()-0.03
        self.__createPropertyHeader(description, z, parent)
        z -= (0.06+0.025) # 0.025 = half height of the following DirectEntries
        menu = DirectOptionMenu(
            items=items,
            pos=(x+0.05, 0, z+0.0125),
            scale=0.05,
            popupMenuLocation=DGG.BELOW,
            initialitem=selectedElement,
            command=command,
            parent=parent)
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
            if root != self.visualEditor.getCanvas():
                path += root.getName() + "/"
            for child in root.getChildren():
                self.__findAllChildren(child, path)

    def __createParentProperty(self, startPos, parent, updateElementInfo):
        updateElement = updateElementInfo.element
        def update(selection):
            if selection == "root":
                newParent = self.visualEditor.getCanvas()
            elif selection.startswith("root/"):
                selection = selection.replace("root/", "**/")
                newParent = self.visualEditor.getCanvas().find(selection)
            else:
                newParent = self.visualEditor.getCanvas().find("**/{}".format(selection))
            base.messenger.send("setParentOfElement", [updateElement, newParent])
            if not newParent.isEmpty():
                try:
                    updateElement.reparentTo(newParent)
                except:
                    print("Failed to reparent {} to {}!\nNOTE: Circular parenting is not allowed!".format(updateElement.getName(), newParent.getName()))
                base.messenger.send("refreshStructureTree")
        self.parentList = ["root"]
        for guiID, elementInfo in self.elementDict.items():
            if elementInfo.element != updateElement:
                if elementInfo.parentElement is not None:
                    if elementInfo.parentElement.element != updateElement:
                        self.parentList.append(elementInfo.element.getName())
                else:
                    self.parentList.append(elementInfo.element.getName())

        self.tmpUpdateElementInfo = updateElementInfo
        self.__findAllChildren(self.visualEditor.getCanvas(), "root/")
        self.updateElementInfo = None

        selectedElement = None
        if updateElement.getParent() == self.visualEditor.getCanvas():
            selectedElement = "root"

        if selectedElement is None:
            if updateElement.getParent().getName() in self.parentList:
                selectedElement = updateElement.getParent().getName()
            else:
                canvas = str(self.visualEditor.getCanvas())
                selectedElement = str(updateElement.getParent()).replace(canvas, "root")

        if selectedElement is None or selectedElement not in self.parentList:
            if updateElementInfo.parentElement is not None:
                if "{}-{}".format(updateElementInfo.elementType, updateElementInfo.parentElement.element.guiId) in self.parentList:
                    selectedElement = "{}-{}".format(updateElementInfo.elementType, updateElementInfo.parentElement.element.guiId)

        self.__createOptionMenuProperty(
            "Parent", startPos, parent, updateElement,
            self.parentList, selectedElement, update)

    def __createReliefProperty(self, description, startPos, parent, updateElement, updateAttribute="relief"):
        def update(selection):
            updateElement[updateAttribute] = DGG.FrameStyleDict[selection]
        selectedElement = None
        for key, value in DGG.FrameStyleDict.items():
            if value == updateElement[updateAttribute]:
                selectedElement = key
                break
        self.__createOptionMenuProperty(
            description, startPos, parent, updateElement,
            list(DGG.FrameStyleDict.keys()), selectedElement, update)

    def __createOrientationProperty(self, description, startPos, parent, updateElement, updateAttribute="relief"):
        orientationDict = {'horizontal': DGG.HORIZONTAL, 'vertical': DGG.VERTICAL, 'vertical_inverted': DGG.VERTICAL_INVERTED}
        def update(selection):
            updateElement[updateAttribute] = orientationDict[selection]
        selectedElement = None
        for key, value in orientationDict.items():
            if value == updateElement[updateAttribute]:
                selectedElement = key
                break
        self.__createOptionMenuProperty(
            description, startPos, parent, updateElement,
            list(orientationDict.keys()), selectedElement, update)

    def __createTextAlignProperty(self, startPos, parent, updateElement):
        alignments = {
            "Left":0,
            "Right":1,
            "Center":2,
            "Boxed Left":3,
            "Boxed Right":4,
            "Boxed Center":5}
        def update(selection):
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

    def __createBoxPlacementProperty(self, description, startPos, parent, updateElement, updateAttribute):
        placements = ["left", "above", "right", "below"]
        def update(selection):
            updateElement[updateAttribute] = selection
        selectedElement = updateElement[updateAttribute]
        self.__createOptionMenuProperty(
            description, startPos, parent, updateElement,
            placements, selectedElement, update)

    def __createResetFramesize(self, description, startPos, parent, updateElement):
        x = startPos.getX()
        z = startPos.getZ()-0.05
        DirectButton(
            text=description,
            text_align=0,
            pos=(x+0.05, 0, z),
            scale=0.05,
            parent=parent,
            command=updateElement.resetFrameSize
            )
