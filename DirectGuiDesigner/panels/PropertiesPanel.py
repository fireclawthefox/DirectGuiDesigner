#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

import logging
import sys
import copy

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
    ConfigVariableString,
    Filename)
from direct.showbase.DirectObject import DirectObject

from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectScrolledFrame import DirectScrolledFrame
from direct.gui.DirectEntry import DirectEntry
from direct.gui.DirectButton import DirectButton
from DirectGuiDesigner.directGuiOverrides.DirectOptionMenu import DirectOptionMenu
from direct.gui.DirectCheckButton import DirectCheckButton

from DirectFolderBrowser.DirectFolderBrowser import DirectFolderBrowser

from DirectGuiExtension import DirectGuiHelper as DGH
from DirectGuiExtension.DirectBoxSizer import DirectBoxSizer
from DirectGuiExtension.DirectAutoSizer import DirectAutoSizer
from DirectGuiExtension.DirectCollapsibleFrame import DirectCollapsibleFrame

from DirectGuiDesigner.core import WidgetDefinition
from DirectGuiDesigner.core.PropertyHelper import PropertyHelper

DGG.BELOW = "below"
MWUP = PGButton.getPressPrefix() + MouseButton.wheel_up().getName() + '-'
MWDOWN = PGButton.getPressPrefix() + MouseButton.wheel_down().getName() + '-'

SCROLLBARWIDTH = 20


class PropertiesPanel(DirectObject):
    scrollSpeedUp = -0.001
    scrollSpeedDown = 0.001

    def __init__(self, parent, getEditorRootCanvas, getEditorPlacer, tooltip):
        height = DGH.getRealHeight(parent)
        self.tooltip = tooltip
        self.parent = parent
        self.customWidgetDefinitions = {}

        self.setupDone = False

        self.box = DirectBoxSizer(
            frameColor=(0.25, 0.25, 0.25, 1),
            autoUpdateFrameSize=False,
            orientation=DGG.VERTICAL)

        self.sizer = DirectAutoSizer(
            updateOnWindowResize=False,
            parent=parent,
            child=self.box,
            childUpdateSizeFunc=self.box.refresh)

        self.lblHeader = DirectLabel(
            text="Properties",
            text_scale=16,
            text_align=TextNode.ALeft,
            text_fg=(1, 1, 1, 1),
            frameColor=VBase4(0, 0, 0, 0),
            )
        self.box.addItem(self.lblHeader, skipRefresh=True)

        color = (
            (0.8, 0.8, 0.8, 1),  # Normal
            (0.9, 0.9, 1, 1),  # Click
            (0.8, 0.8, 1, 1),  # Hover
            (0.5, 0.5, 0.5, 1))  # Disabled
        self.propertiesFrame = DirectScrolledFrame(
            # make the frame fit into our background frame
            frameSize=VBase4(
                self.parent["frameSize"][0], self.parent["frameSize"][1],
                self.parent["frameSize"][2]+DGH.getRealHeight(self.lblHeader), self.parent["frameSize"][3]),
            # set the frames color to transparent
            frameColor=VBase4(1, 1, 1, 1),
            scrollBarWidth=SCROLLBARWIDTH,
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

    def setCustomWidgetDefinitions(self,customWidgetDefinitions):
        self.customWidgetDefinitions = customWidgetDefinitions

    def scroll(self, scrollStep, event):
        """Scrolls the properties frame vertically with the given step.
        A negative step will scroll down while a positive step value will scroll
        the frame upwards"""
        if self.propertiesFrame.verticalScroll.isHidden():
            return

        self.propertiesFrame.verticalScroll.scrollStep(scrollStep)

    def resizeFrame(self):
        """Refreshes the sizer and recalculates the framesize to fit the parents
        frame size"""
        self.sizer.refresh()
        self.propertiesFrame["frameSize"] = (
                self.parent["frameSize"][0], self.parent["frameSize"][1],
                self.parent["frameSize"][2]+DGH.getRealHeight(self.lblHeader), self.parent["frameSize"][3])

        if self.setupDone and not taskMgr.hasTaskNamed("updatePropPanel"):
            taskMgr.doMethodLater(0.99, self.clear, "clearPropPanel", extraArgs=[])
            taskMgr.doMethodLater(1, self.refreshProperties, "updatePropPanel", extraArgs=[])


    def setupProperties(self, headerText, elementInfo, elementDict):
        """Creates the set of editable properties for the given element"""
        if taskMgr.hasTaskNamed("updatePropPanel"):
            taskMgr.remove("updatePropPanel")
        self.ignoreAll()
        self.headerText = headerText
        self.elementInfo = elementInfo
        self.elementDict = elementDict
        self.refreshProperties()

    def refreshProperties(self):
        # create the frame that will hold all our properties
        self.mainBoxFrame = DirectBoxSizer(
            orientation=DGG.VERTICAL,
            frameColor=VBase4(0, 0, 0, 0),
            parent=self.propertiesFrame.getCanvas(),
            suppressMouse=True,
            state=DGG.NORMAL)
        self.mainBoxFrame.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        self.mainBoxFrame.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])

        # Create the header for the properties
        lbl = DirectLabel(
            text=self.headerText,
            text_scale=18,
            text_pos=(-10, 0),
            text_align=TextNode.ACenter,
            frameSize=VBase4(
                -self.propertiesFrame["frameSize"][1],
                self.propertiesFrame["frameSize"][1],
                -10,
                20),
            frameColor=VBase4(0.7, 0.7, 0.7, 1),
            state=DGG.NORMAL)
        lbl.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        lbl.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        self.mainBoxFrame.addItem(lbl)

        has_error = False
        error_count = 0
        # Set up all the properties
        try:

            allDefinitions = {**WidgetDefinition.DEFINITIONS, **self.customWidgetDefinitions}

            self.boxFrames = {}

            # check if we have a definition for this specific GUI element
            if self.elementInfo.type in allDefinitions:
                # create the main set of properties to edit
                wd = allDefinitions[self.elementInfo.type]
                # create a header for this type of element
                self.__createInbetweenHeader(self.elementInfo.type)

                section = self.createSection()

                # Designer specific entries
                self.__createNameProperty(self.elementInfo)

                self.__createRootReParent(self.elementInfo)

                # create the set of properties to edit on the main component
                for definition in wd:
                    try:
                        self.createProperty(definition, self.elementInfo)
                    except:
                        #e = sys.exc_info()[1]
                        has_error = True
                        error_count += 1
                        logging.exception("Failed to load property for properties panel")

                self.updateSection(section)

                # create the sub component set of properties to edit
                groups = {}
                for componentName, componentDefinition in self.elementInfo.element._DirectGuiBase__componentInfo.items():
                    widget = componentDefinition[0]
                    wConfigure = componentDefinition[1]
                    wType = componentDefinition[2]
                    wGet = componentDefinition[3]
                    group = componentDefinition[4]

                    # store the sub widget as an element info object
                    subWidgetElementInfo = copy.copy(self.elementInfo)
                    subWidgetElementInfo.element = widget
                    subWidgetElementInfo.subComponentName = componentName

                    headerName = componentName
                    if group is not None:
                        widgetNPName = str(widget)
                        if len(widgetNPName) > 35:
                            widgetNPName = widgetNPName[-35:]
                            widgetNPName = "..." + widgetNPName
                        headerName = f"{wType} - [{widgetNPName}]"

                    # check if this component has definitions
                    if wType in allDefinitions:
                        # write the header for this component
                        self.__createInbetweenHeader(headerName)
                        subsection = self.createSection()
                        subWd = allDefinitions[wType]
                        for definition in subWd:
                            # create the property for all definitions of this
                            # sub widget
                            try:
                                self.createProperty(
                                    definition,
                                    subWidgetElementInfo)
                            except:
                                #e = sys.exc_info()[1]
                                has_error = True
                                error_count += 1
                                logging.exception("Failed to load property for properties panel")

                        self.updateSection(subsection)

            self.setupDone = True
        except Exception:
            e = sys.exc_info()[1]
            base.messenger.send("showWarning", [str(e)])
            logging.exception("Error while loading properties panel")

        if has_error:
            base.messenger.send("showWarning", [f"There were {error_count} Errors while loading the properties panel.\nSee log file for more details."])


        #
        # Reset property Frame framesize
        #
        self.updateCanvasSize()

    def updateCanvasSize(self):
        for section, boxFrame in self.boxFrames.items():
            boxFrame.refresh()

        self.mainBoxFrame.refresh()

        self.propertiesFrame["canvasSize"] = (
            self.propertiesFrame["frameSize"][0],
            self.propertiesFrame["frameSize"][1]-SCROLLBARWIDTH,
            self.mainBoxFrame.bounds[2],
            0)
        self.propertiesFrame.setCanvasSize()

        a = self.propertiesFrame["canvasSize"][2]
        b = abs(self.propertiesFrame["frameSize"][2]) + self.propertiesFrame["frameSize"][3]
        scrollDefault = 200
        s = -(scrollDefault / (a / b))

        self.propertiesFrame["verticalScroll_scrollSize"] = s
        self.propertiesFrame["verticalScroll_pageSize"] = s

    def createSection(self):
        section = DirectCollapsibleFrame(
            collapsed=True,
            frameColor=(1, 1, 1, 1),
            headerheight=24,
            frameSize=(
                self.propertiesFrame["frameSize"][0],
                self.propertiesFrame["frameSize"][1],
                0, 20))

        self.accept(section.getCollapsedEvent(), self.sectionCollapsed, extraArgs=[section])
        self.accept(section.getExtendedEvent(), self.updateCanvasSize)

        section.toggleCollapseButton["text_scale"] = 12
        tp = section.toggleCollapseButton["text_pos"]
        section.toggleCollapseButton["text_pos"] = (tp[0] + 5, -12)

        section.toggleCollapseButton.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        section.toggleCollapseButton.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        section.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        section.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])

        self.mainBoxFrame.addItem(section)
        self.boxFrame = DirectBoxSizer(
            pos=(0, 0, -section["headerheight"]),
            frameSize=(
                self.propertiesFrame["frameSize"][0],
                self.propertiesFrame["frameSize"][1]-SCROLLBARWIDTH,
                0, 0),
            orientation=DGG.VERTICAL,
            itemAlign=DirectBoxSizer.A_Left,
            frameColor=VBase4(0, 0, 0, 0),
            parent=section,
            suppressMouse=True,
            state=DGG.NORMAL)
        self.boxFrame.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        self.boxFrame.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])

        self.boxFrames[section] = self.boxFrame

        return section

    def sectionCollapsed(self, section):
        self.updateCanvasSize()

    def updateSection(self, section):
        self.boxFrames[section].refresh()
        fs = self.boxFrames[section]["frameSize"]
        section["frameSize"] = (fs[0], fs[1]-SCROLLBARWIDTH, fs[2]-section["headerheight"], fs[3])
        section.updateFrameSize()
        section.setCollapsed()

    def createProperty(self, definition, elementInfo):
        if definition.editType == WidgetDefinition.PropertyEditTypes.int:
            self.__createNumberInput(definition, elementInfo, int)
        elif definition.editType == WidgetDefinition.PropertyEditTypes.float:
            self.__createNumberInput(definition, elementInfo, float)
        elif definition.editType == WidgetDefinition.PropertyEditTypes.bool:
            self.__createBoolProperty(definition, elementInfo)
        elif definition.editType == WidgetDefinition.PropertyEditTypes.text:
            self.__createTextProperty(definition, elementInfo)
        elif definition.editType == WidgetDefinition.PropertyEditTypes.base2:
            self.__createBaseNInput(definition, elementInfo, 2)
        elif definition.editType == WidgetDefinition.PropertyEditTypes.base3:
            self.__createBaseNInput(definition, elementInfo, 3)
        elif definition.editType == WidgetDefinition.PropertyEditTypes.base4:
            self.__createBaseNInput(definition, elementInfo, 4)
        elif definition.editType == WidgetDefinition.PropertyEditTypes.command:
            self.__createCustomCommand(definition, elementInfo)
        elif definition.editType == WidgetDefinition.PropertyEditTypes.path:
            self.__createPathProperty(definition, elementInfo)
        elif definition.editType == WidgetDefinition.PropertyEditTypes.optionMenu:
            self.__createOptionMenuProperty(definition, elementInfo)
        elif definition.editType == WidgetDefinition.PropertyEditTypes.list:
            self.__createListProperty(definition, elementInfo)
        elif definition.editType == WidgetDefinition.PropertyEditTypes.tuple:
            self.__createTupleProperty(definition, elementInfo)
        elif definition.editType == WidgetDefinition.PropertyEditTypes.fitToChildren:
            self.__createFitToChildren(definition, elementInfo)
        else:
            logging.error(f"Edit type {definition.editType} not in Edit type definitions")

    def clear(self):
        if not hasattr(self, "mainBoxFrame"): return
        if self.mainBoxFrame is not None:
            self.mainBoxFrame.destroy()

    def __createInbetweenHeader(self, description):
        l = DirectLabel(
            text=description,
            text_scale=16,
            text_align=TextNode.ACenter,
            frameSize=VBase4(self.propertiesFrame["frameSize"][0], self.propertiesFrame["frameSize"][1], -10, 20),
            frameColor=VBase4(0.85, 0.85, 0.85, 1),
            state=DGG.NORMAL)
        l.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        l.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        self.mainBoxFrame.addItem(l, skipRefresh=True)

    def __createPropertyHeader(self, description):
        l = DirectLabel(
            text=description,
            text_scale=12,
            text_align=TextNode.ALeft,
            text_pos=(self.propertiesFrame["frameSize"][0] + 5, 0),
            frameSize=VBase4(self.propertiesFrame["frameSize"][0], self.propertiesFrame["frameSize"][1], -10, 20),
            frameColor=VBase4(0.85, 0.85, 0.85, 1),
            state=DGG.NORMAL)
        l.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        l.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        self.boxFrame.addItem(l, skipRefresh=True)

    def __addToKillRing(self, elementInfo, definition, oldValue, newValue):
        base.messenger.send("addToKillRing",
            [elementInfo, "set", definition.internalName, oldValue, newValue])

    def __createTextEntry(self, text, width, command, commandArgs=[]):
        def focusOut():
            base.messenger.send("reregisterKeyboardEvents")
            command(*[entry.get()] + entry["extraArgs"])
        entry = DirectEntry(
            initialText=text,
            relief=DGG.SUNKEN,
            frameColor=(1,1,1,1),
            scale=12,
            width=width/12,
            overflow=True,
            command=command,
            extraArgs=commandArgs,
            focusInCommand=base.messenger.send,
            focusInExtraArgs=["unregisterKeyboardEvents"],
            focusOutCommand=focusOut)
        entry.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        entry.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        return entry

    #
    # General input elements
    #
    def __createBaseNInput(self, definition, elementInfo, n, numberType=float):
        entryList = []

        def update(text, elementInfo):
            base.messenger.send("setDirtyFlag")
            values = []
            for value in entryList:
                try:
                    values.append(numberType(value.get(True)))
                except Exception:
                    if value.get(True) == "":
                        values.append(None)
                    else:
                        logging.exception("ERROR: NAN", value.get(True))
                        values.append(numberType(0))
            try:
                oldValue = PropertyHelper.getValues(definition, elementInfo)
                differ = False
                if oldValue is not None:
                    for i in range(n):
                        if oldValue[i] != values[i]:
                            differ = True
                            break
                elif values is not None and values != []:
                    differ = True
                if differ:
                    self.__addToKillRing(elementInfo, definition, oldValue, values)
            except Exception as e:
                logging.exception(f"{definition.internalName} not supported by undo/redo yet")
            allValuesSet = True
            allValuesNone = True
            for value in values:
                if value is None:
                    allValuesSet = False
                if value is not None:
                    allValuesNone = False
            if allValuesNone:
                values = None
            elif allValuesSet:
                values = tuple(values)
            if allValuesNone or allValuesSet:
                PropertyHelper.setValue(definition, elementInfo, values)
        self.__createPropertyHeader(definition.visibleName)
        values = PropertyHelper.getValues(definition, elementInfo)
        if type(values) is int or type(values) is float:
            values = [values] * n
        if definition.nullable:
            if values is None:
                values = [""] * n
        width = DGH.getRealWidth(self.boxFrame) / n - SCROLLBARWIDTH / n
        entryBox = DirectBoxSizer()
        for i in range(n):
            value = PropertyHelper.getFormated(values[i])
            entry = self.__createTextEntry(str(value), width, update, [elementInfo])
            entryList.append(entry)
            entryBox.addItem(entry)
        self.boxFrame.addItem(entryBox, skipRefresh=True)

    def __createNumberInput(self, definition, elementInfo, numberType):
        def update(text, elementInfo):
            base.messenger.send("setDirtyFlag")
            value = numberType(0)
            try:
                value = numberType(text)
            except Exception:
                if text == "" and definition.nullable:
                    value = None
                else:
                    logging.exception("ERROR: NAN", value)
                    value = numberType(0)
            try:
                oldValue = PropertyHelper.getValues(definition, elementInfo)
                self.__addToKillRing(elementInfo, definition, oldValue, value)
            except Exception:
                logging.exception(f"{definition.internalName} not supported by undo/redo yet")
            PropertyHelper.setValue(definition, elementInfo, value)
        self.__createPropertyHeader(definition.visibleName)
        valueA = PropertyHelper.getValues(definition, elementInfo)
        if valueA is None and not definition.nullable:
            logging.error(f"Got None value for not nullable element {definition.internalName}")
        if valueA is not None:
            valueA = PropertyHelper.getFormated(valueA, numberType is int)
        width = DGH.getRealWidth(self.boxFrame) - SCROLLBARWIDTH
        entry = self.__createTextEntry(str(valueA), width, update, [elementInfo])
        self.boxFrame.addItem(entry, skipRefresh=True)

    def __createTextProperty(self, definition, elementInfo):
        def update(text, elementInfo):
            base.messenger.send("setDirtyFlag")
            try:
                oldValue = PropertyHelper.getValues(definition, elementInfo)
                self.__addToKillRing(elementInfo, definition, oldValue, text)
            except:
                logging.exception(f"{definition.internalName} not supported by undo/redo yet")

            PropertyHelper.setValue(definition, elementInfo, text)
        self.__createPropertyHeader(definition.visibleName)
        text = PropertyHelper.getValues(definition, elementInfo)
        width = DGH.getRealWidth(self.boxFrame) - SCROLLBARWIDTH
        entry = self.__createTextEntry(text, width, update, [elementInfo])
        self.boxFrame.addItem(entry, skipRefresh=True)

    def __createBoolProperty(self, definition, elementInfo):
        def update(value):
            base.messenger.send("setDirtyFlag")
            try:
                oldValue = PropertyHelper.getValues(definition, elementInfo)
                self.__addToKillRing(elementInfo, definition, oldValue, value)
            except:
                logging.exception(f"{definition.internalName} not supported by undo/redo yet")
            PropertyHelper.setValue(definition, elementInfo, value)
        self.__createPropertyHeader(definition.visibleName)
        valueA = PropertyHelper.getValues(definition, elementInfo)
        btn = DirectCheckButton(
            indicatorValue=valueA,
            scale=24,
            frameSize=(-.5,.5,-.5,.5),
            text_align=TextNode.ALeft,
            command=update)
        btn.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        btn.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        self.boxFrame.addItem(btn, skipRefresh=True)

    def __createListProperty(self, definition, elementInfo):
        def update(text, elementInfo, entries):
            base.messenger.send("setDirtyFlag")
            value = []

            for entry in entries:
                #if entry.get() != "":
                value.append(entry.get())

            try:
                oldValue = PropertyHelper.getValues(definition, elementInfo)
                self.__addToKillRing(elementInfo, definition, oldValue, value)
            except Exception:
                logging.exception(f"{definition.internalName} not supported by undo/redo yet")

            PropertyHelper.setValue(definition, elementInfo, value)

        def addEntry(text="", updateEntries=True, updateMainBox=True):
            entry = self.__createTextEntry(str(text), width, update, [elementInfo])
            entriesBox.addItem(entry, skipRefresh=True)
            entries.append(entry)

            if updateEntries:
                for entry in entries:
                    oldArgs = entry["extraArgs"]
                    if len(oldArgs) > 1:
                        oldArgs = oldArgs[:-1]
                    entry["extraArgs"] = oldArgs + [entries]

            if updateMainBox:
                entriesBox.refresh()
                for section, boxFrame in self.boxFrames.items():
                    boxFrame.refresh()
                    self.updateSection(section)

        self.__createPropertyHeader(definition.visibleName)
        listItems = PropertyHelper.getValues(definition, elementInfo)

        # make sure we have a list
        if listItems is None or isinstance(listItems, str):
            listItems = [listItems]

        width = DGH.getRealWidth(self.boxFrame) - SCROLLBARWIDTH
        entriesBox = DirectBoxSizer(
            orientation=DGG.VERTICAL,
            itemAlign=DirectBoxSizer.A_Left,
            frameColor=VBase4(0,0,0,0),
            suppressMouse=True,
            state=DGG.NORMAL)
        entriesBox.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        entriesBox.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        self.boxFrame.addItem(entriesBox, skipRefresh=True)
        entries = []
        for i in range(len(listItems)):
            text = listItems[i]
            addEntry(text, i == len(listItems)-1, i == len(listItems)-1)
        btn = DirectButton(
            text="Add entry",
            pad=(0.25,0.25),
            scale=12,
            command=addEntry
            )
        btn.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        btn.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        self.boxFrame.addItem(btn, skipRefresh=True)

    def __createTupleProperty(self, definition, elementInfo):
        def update(text, elementInfo, entries):
            base.messenger.send("setDirtyFlag")
            value = []

            for entry in entries:
                if entry.get() != "":
                    value.append(entry.get())

            value = tuple(value)

            try:
                oldValue = PropertyHelper.getValues(definition, elementInfo)
                self.__addToKillRing(elementInfo, definition, oldValue, value)
            except Exception:
                logging.exception(f"{definition.internalName} not supported by undo/redo yet")

            PropertyHelper.setValue(definition, elementInfo, value)

        def addEntry(text="", updateEntries=True, updateMainBox=True):
            entry = self.__createTextEntry(text, width, update, [elementInfo])
            entriesBox.addItem(entry, skipRefresh=True)
            entries.append(entry)

            if updateEntries:
                for entry in entries:
                    oldArgs = entry["extraArgs"]
                    if len(oldArgs) > 1:
                        oldArgs = oldArgs[:-1]
                    entry["extraArgs"] = oldArgs + [entries]

            if updateMainBox:
                entriesBox.refresh()
                for section, boxFrame in self.boxFrames.items():
                    boxFrame.refresh()
                    self.updateSection(section)

        self.__createPropertyHeader(definition.visibleName)
        listItems = PropertyHelper.getValues(definition, elementInfo)
        width = DGH.getRealWidth(self.boxFrame) - SCROLLBARWIDTH
        entriesBox = DirectBoxSizer(
            orientation=DGG.VERTICAL,
            itemAlign=DirectBoxSizer.A_Left,
            frameColor=VBase4(0,0,0,0),
            suppressMouse=True,
            state=DGG.NORMAL)
        entriesBox.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        entriesBox.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        self.boxFrame.addItem(entriesBox, skipRefresh=True)
        entries = []
        for i in range(len(listItems)):
            text = listItems[i]
            addEntry(text, i==len(listItems)-1, i==len(listItems)-1)
        btn = DirectButton(
            text="Add entry",
            pad=(0.25,0.25),
            scale=12,
            command=addEntry
            )
        btn.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        btn.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        self.boxFrame.addItem(btn, skipRefresh=True)

    def __createCustomCommandProperty(self, description, updateElement, updateAttribute, elementInfo):
        def update(text, elementInfo):
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
                except Exception:
                    logging.debug(f"command evaluation not supported: {text}")
                    logging.debug("set command without evalution")
                    command = text

            try:
                base.messenger.send("addToKillRing",
                    [updateElement, "set", updateAttribute, curCommand, text])
            except Exception:
                logging.debug(f"{updateAttribute} not supported by undo/redo yet")

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
        self.__createPropertyHeader(description)
        curCommand = ""
        if updateAttribute in elementInfo.extraOptions:
            curCommand = elementInfo.extraOptions[updateAttribute]
        width = (DGH.getRealWidth(parent) - 10) - SCROLLBARWIDTH
        entryWidth = width / 13
        entry = self.__createTextEntry(curCommand, entryWidth, update, [elementInfo])
        self.boxFrame.addItem(entry, skipRefresh=True)

    def __createPathProperty(self, definition, elementInfo):

        def update(text):
            value = text
            if text == "" and definition.nullable:
                value = None
            elif definition.loaderFunc is not None and text != "":
                try:
                    if type(definition.loaderFunc) is str:
                        value = eval(definition.loaderFunc)
                    else:
                        value = definition.loaderFunc(value)
                except Exception:
                    logging.exception("Couldn't load path with loader function")
                    value = text
            base.messenger.send("setDirtyFlag")
            try:
                PropertyHelper.setValue(definition, elementInfo, value, text)
            except Exception:
                base.messenger.send("showWarning", [f"couldn't load file '{text}'"])
                logging.exception("Couldn't load file: {}".format(text))
                elementInfo.element[definition.internalName] = None

        def setPath(path):
            update(path)

            # make sure to take the actual value to write it to the textbox in
            # case something hapened while updating the value
            v = PropertyHelper.getValues(definition, elementInfo)
            if v is None:
                v = ""
            entry.set(v)

        def selectPath(confirm):
            if confirm:
                value = Filename.fromOsSpecific(self.browser.get())
                setPath(str(value))
            self.browser.hide()

        def showBrowser():
            self.browser = DirectFolderBrowser(
                selectPath,
                True,
                ConfigVariableString("work-dir-path", "~").getValue(),
                "",
                tooltip=self.tooltip)
            self.browser.show()
        self.__createPropertyHeader(definition.visibleName)
        path = PropertyHelper.getValues(definition, elementInfo)
        if type(path) is not str:
            path = ""
        width = DGH.getRealWidth(self.boxFrame) - SCROLLBARWIDTH
        entry = self.__createTextEntry(path, width, update)
        self.boxFrame.addItem(entry, skipRefresh=True)

        btn = DirectButton(
            text="Browse",
            text_align=TextNode.ALeft,
            command=showBrowser,
            pad=(0.25,0.25),
            scale=12
            )
        btn.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        btn.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        self.boxFrame.addItem(btn, skipRefresh=True)

    def __createOptionMenuProperty(self, definition, elementInfo):
        def update(selection):
            oldValue = PropertyHelper.getValues(definition, elementInfo)
            value = definition.valueOptions[selection]
            # Undo/Redo setup
            try:
                if oldValue != value:
                    self.__addToKillRing(elementInfo, definition, oldValue, value)
            except Exception as e:
                logging.exception(f"{definition.internalName} not supported by undo/redo yet")

            value_str = ""
            if definition.loaderFunc is not None:
                value_str = value
                try:
                    if type(definition.loaderFunc) is str:
                        value = eval(definition.loaderFunc)
                    else:
                        value = definition.loaderFunc(value)
                except Exception:
                    logging.exception("Couldn't load path with loader function")
                    value = value_str
            # actually set the value on the element
            PropertyHelper.setValue(definition, elementInfo, value, value_str)

        self.__createPropertyHeader(definition.visibleName)
        if definition.valueOptions is None:
            return
        value = PropertyHelper.getValues(definition, elementInfo)
        selectedElement = list(definition.valueOptions.keys())[0]
        for k, v in definition.valueOptions.items():
            if v == value:
                selectedElement = k
                break
        menu = DirectOptionMenu(
            items=list(definition.valueOptions.keys()),
            scale=12,
            popupMenuLocation=DGG.BELOW,
            initialitem=selectedElement,
            command=update)
        menu.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        menu.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        self.boxFrame.addItem(menu, skipRefresh=True)

    def __createCustomCommand(self, definition, elementInfo):
        self.__createPropertyHeader(definition.visibleName)
        btn = DirectButton(
            text="Run Command",
            pad=(0.25,0.25),
            scale=12,
            command=getattr(elementInfo.element, definition.valueOptions)
            )
        btn.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        btn.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        self.boxFrame.addItem(btn, skipRefresh=True)

    def __createFitToChildren(self, definition, elementInfo):
        self.__createPropertyHeader("Fit to children")
        #
        # Fit frame to children
        #
        l, r, b, t = [None,None,None,None]

        def getMaxSize(rootElement, baseElementInfo, l, r, b, t):
            if not hasattr(rootElement, "getChildren"):
                return [l,r,b,t]
            if len(rootElement.getChildren()) <= 0:
                return [l,r,b,t]
            for child in rootElement.getChildren():
                childElementInfo = None
                if child.getName() in self.elementDict.keys():
                    childElementInfo = self.elementDict[child.getName()]
                elif len(child.getName().split("-")) > 1 and child.getName().split("-")[1] in self.elementDict.keys():
                    childElementInfo = self.elementDict[child.getName().split("-")[1]]

                if childElementInfo is None: continue

                element = childElementInfo.element
                el = DGH.getRealLeft(element) + element.getX(baseElementInfo.element)
                er = DGH.getRealRight(element) + element.getX(baseElementInfo.element)
                eb = DGH.getRealBottom(element) + element.getZ(baseElementInfo.element)
                et = DGH.getRealTop(element) + element.getZ(baseElementInfo.element)

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

                l,r,b,t = getMaxSize(child, baseElementInfo, l, r, b, t)
            return [l, r, b, t]

        def fitToChildren(elementInfo, l, r, b, t):
            l, r, b, t = getMaxSize(elementInfo.element, elementInfo, l, r, b, t)
            if l is None or r is None or b is None or t is None:
                return
            elementInfo.element["frameSize"] = [l, r, b, t]

        btn = DirectButton(
            text="Fit to children",
            pad=(0.25,0.25),
            scale=12,
            command=fitToChildren,
            extraArgs=[elementInfo, l, r, b, t]
            )
        btn.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        btn.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        self.boxFrame.addItem(btn, skipRefresh=True)

    #
    # Designer specific input fields
    #
    def __createNameProperty(self, elementInfo):
        def update(text):
            base.messenger.send("setDirtyFlag")
            name = elementInfo.element.guiId.replace("-", "")
            if text != "":
                name = text
            base.messenger.send("setName", [elementInfo, name])
        self.__createPropertyHeader("Name")
        text = elementInfo.name
        width = DGH.getRealWidth(self.boxFrame) - SCROLLBARWIDTH
        entry = self.__createTextEntry(text, width, update)
        self.boxFrame.addItem(entry, skipRefresh=True)

    def __createRootReParent(self, elementInfo):
        def update(name):
            base.messenger.send("setDirtyFlag")
            parent = self.getEditorPlacer(name)
            elementInfo.element.reparentTo(parent)
            if name == "canvasRoot":
                elementInfo.parent = None
            else:
                elementInfo.parent = parent
            base.messenger.send("refreshStructureTree")

        self.__createPropertyHeader("Change Root parent")

        def createReparentButton(txt, arg):
            btn = DirectButton(
                text=txt,
                pad=(0.25,0.25),
                scale=12,
                command=update,
                extraArgs=[arg]
                )
            btn.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
            btn.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
            self.boxFrame.addItem(btn, skipRefresh=True)
        createReparentButton("Root", "canvasRoot")
        createReparentButton("Center Left", "canvasLeftCenter")
        createReparentButton("Center Right", "canvasRightCenter")
        createReparentButton("Top Left", "canvasTopLeft")
        createReparentButton("Top Right", "canvasTopRight")
        createReparentButton("Top Center", "canvasTopCenter")
        createReparentButton("Bottom Left", "canvasBottomLeft")
        createReparentButton("Bottom Right", "canvasBottomRight")
        createReparentButton("Bottom Center", "canvasBottomCenter")
