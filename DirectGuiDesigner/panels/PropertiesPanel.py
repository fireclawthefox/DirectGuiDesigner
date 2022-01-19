#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

#TODO: Remove startpos and replace by boxsizer placements
#    Some functions return the element, some places them directly, handle accordingly
#    remove unused functions
#    cleanup

import logging, sys, copy

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
from direct.showbase.DirectObject import DirectObject

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
from DirectGuiExtension.DirectCollapsibleFrame import DirectCollapsibleFrame

from DirectGuiDesigner.core import WidgetDefinition

class PropertyInfo:
    def __init__(self, displayName, propertyName, propertyType, customCommandName, customSelectionDict):
        self.displayName = displayName
        self.propertyName = propertyName
        self.propertyType = propertyType
        self.customCommandName = customCommandName
        self.customSelectionDict = customSelectionDict

SCROLLBARWIDTH = 20

class PropertiesPanel(DirectObject):
    scrollSpeedUp = -0.001
    scrollSpeedDown = 0.001

    def __init__(self, parent, getEditorRootCanvas, getEditorPlacer, tooltip):
        height = DGH.getRealHeight(parent)
        # A list containing the prooperty information
        self.tooltip = tooltip
        self.parent = parent
        self.customWidgetDefinitions = {}

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
            text_fg=(1,1,1,1),
            frameColor=VBase4(0, 0, 0, 0),
            )
        self.box.addItem(self.lblHeader, skipRefresh=True)

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
        self.propertiesFrame.verticalScroll.scrollStep(scrollStep)

    def resizeFrame(self):
        """Refreshes the sizer and recalculates the framesize to fit the parents
        frame size"""
        self.sizer.refresh()
        self.propertiesFrame["frameSize"] = (
                self.parent["frameSize"][0], self.parent["frameSize"][1],
                self.parent["frameSize"][2]+DGH.getRealHeight(self.lblHeader), self.parent["frameSize"][3])

    def setupProperties(self, headerText, elementInfo, elementDict):
        """Creates the set of editable properties for the given element"""
        self.ignoreAll()
        self.headerText = headerText
        self.elementInfo = elementInfo
        self.elementDict = elementDict
        # create the frame that will hold all our properties
        self.mainBoxFrame = DirectBoxSizer(
            orientation=DGG.VERTICAL,
            itemAlign=DirectBoxSizer.A_Left,
            frameColor=VBase4(0,0,0,0),
            parent=self.propertiesFrame.getCanvas(),
            suppressMouse=True,
            state=DGG.NORMAL)
        self.mainBoxFrame.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        self.mainBoxFrame.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])

        # Create the header for the properties
        l = DirectLabel(
            text=headerText,
            text_scale=18,
            text_pos=(-10, 0),
            text_align=TextNode.ACenter,
            frameSize=VBase4(
                -self.propertiesFrame["frameSize"][1],
                self.propertiesFrame["frameSize"][1]-SCROLLBARWIDTH,
                -10,
                20),
            frameColor=VBase4(0.7,0.7,0.7,1),
            state=DGG.NORMAL)
        l.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        l.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        self.mainBoxFrame.addItem(l)

        # Set up all the properties
        try:

            allDefinitions = {**WidgetDefinition.DEFINITIONS, **self.customWidgetDefinitions}

            # check if we have a definition for this specific GUI element
            if elementInfo.type in allDefinitions:
                # create the main set of properties to edit
                wd = allDefinitions[elementInfo.type]
                # create a header for this type of element
                self.__createInbetweenHeader(elementInfo.type)

                section = self.createSection()

                # Designer specific entries
                self.__createNameProperty(elementInfo)

                self.__createRootReParent(elementInfo)

                # create the set of properties to edit on the main component
                for definition in wd:
                    self.createProperty(definition, elementInfo)

                self.updateSection(section)
                section.toggleCollapsed()
                section.toggleCollapsed()

                # create the sub component set of properties to edit
                groups = {}
                for componentName, componentDefinition in elementInfo.element._DirectGuiBase__componentInfo.items():
                    widget = componentDefinition[0]
                    wConfigure = componentDefinition[1]
                    wType = componentDefinition[2]
                    wGet = componentDefinition[3]
                    group = componentDefinition[4]

                    # store the sub widget as an element info object
                    subWidgetElementInfo = copy.copy(elementInfo)
                    subWidgetElementInfo.element = widget

                    headerName = componentName
                    if group is not None:
                        headerName = f"{wType} - [{widget}]"

                    # check if this component has definitions
                    if wType in allDefinitions:
                        # write the header for this component
                        self.__createInbetweenHeader(headerName)
                        subsection = self.createSection()
                        subWd = allDefinitions[wType]
                        for definition in subWd:
                            # create the property for all the defined
                            self.createProperty(definition, subWidgetElementInfo)

                        self.updateSection(subsection)
                        subsection.toggleCollapsed()
                        subsection.toggleCollapsed()

        except:
            e = sys.exc_info()[1]
            base.messenger.send("showWarning", [str(e)])
            logging.exception("Error while loading properties panel")

        #
        # Reset property Frame framesize
        #
        self.updateCanvasSize()

    def updateCanvasSize(self):
        self.mainBoxFrame.refresh()

        self.propertiesFrame["canvasSize"] = (
            0,
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
            frameColor=(1,1,1,1),
            headerheight=24,
            frameSize=(
                -self.propertiesFrame["frameSize"][1],
                self.propertiesFrame["frameSize"][1]-SCROLLBARWIDTH,
                0, 20))

        self.accept(section.getCollapsedEvent(), self.sectionCollapsed, extraArgs=[section])
        self.accept(section.getExtendedEvent(), self.updateCanvasSize)

        section.toggleCollapseButton["text_scale"] = 12
        section.toggleCollapseButton["text_pos"] = (0, -12)

        section.toggleCollapseButton.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        section.toggleCollapseButton.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        section.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        section.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])

        self.mainBoxFrame.addItem(section)
        self.boxFrame = DirectBoxSizer(
            pos=(0,0,-section["headerheight"]),#DGH.getRealLeft(section)
            frameSize=(
                -self.propertiesFrame["frameSize"][1],
                self.propertiesFrame["frameSize"][1]-SCROLLBARWIDTH,
                0, 0),
            orientation=DGG.VERTICAL,
            itemAlign=DirectBoxSizer.A_Left,
            frameColor=VBase4(0,0,0,0),
            parent=section,
            suppressMouse=True,
            state=DGG.NORMAL)
        self.boxFrame.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        self.boxFrame.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        return section

    def sectionCollapsed(self, section):
        self.updateCanvasSize()

    def updateSection(self, section):
        self.boxFrame.refresh()
        fs = self.boxFrame["frameSize"]
        section["frameSize"] = (fs[0], fs[1], fs[2]-section["headerheight"], fs[3])
        section.updateFrameSize()

    def createProperty(self, definition, elementInfo):
        if definition.editType == WidgetDefinition.PropertyEditTypes.integer:
            logging.debug("create integer property")
            self.__createNumberInput(definition, elementInfo, int)
        elif definition.editType == WidgetDefinition.PropertyEditTypes.float:
            logging.debug("create float property")
            self.__createNumberInput(definition, elementInfo, float)
        elif definition.editType == WidgetDefinition.PropertyEditTypes.bool:
            logging.debug("create bool property")
            self.__createBoolProperty(definition, elementInfo)
        elif definition.editType == WidgetDefinition.PropertyEditTypes.text:
            #logging.debug("create text property")
            self.__createTextProperty(definition, elementInfo)
        elif definition.editType == WidgetDefinition.PropertyEditTypes.base2:
            #logging.debug("create base2 property")
            self.__createBaseNInput(definition, elementInfo, 2)
        elif definition.editType == WidgetDefinition.PropertyEditTypes.base3:
            #logging.debug("create base3 property")
            self.__createBaseNInput(definition, elementInfo, 3)
        elif definition.editType == WidgetDefinition.PropertyEditTypes.base4:
            #logging.debug("create base4 property")
            self.__createBaseNInput(definition, elementInfo, 4)
        elif definition.editType == WidgetDefinition.PropertyEditTypes.command:
            #logging.debug("create command property")
            self.__createCustomCommand(definition, elementInfo)
        elif definition.editType == WidgetDefinition.PropertyEditTypes.path:
            #logging.debug("create path property")
            self.__createPathProperty(definition, elementInfo)
        elif definition.editType == WidgetDefinition.PropertyEditTypes.optionMenu:
            #logging.debug("create option menu property")
            self.__createOptionMenuProperty(definition, elementInfo)
        elif definition.editType == WidgetDefinition.PropertyEditTypes.list:
            #logging.debug("create list property")
            self.__createListProperty(definition, elementInfo)
        elif definition.editType == WidgetDefinition.PropertyEditTypes.tuple:
            #logging.debug("create tuple property")
            self.__createTupleProperty(definition, elementInfo)
        elif definition.editType == WidgetDefinition.PropertyEditTypes.fitToChildren:
            #logging.debug("create fit to children property")
            self.__createFitToChildren(definition, elementInfo)
        else:
            logging.error(f"Edit type {definition.editType} not in Edit type definitions")

    def clear(self):
        if self.mainBoxFrame is not None:
            self.mainBoxFrame.destroy()

    def __createInbetweenHeader(self, description):
        l = DirectLabel(
            text=description,
            text_scale=16,
            text_pos=(-10, 0),
            text_align=TextNode.ACenter,
            frameSize=VBase4(self.propertiesFrame["frameSize"][0], self.propertiesFrame["frameSize"][1], -10, 20),
            frameColor=VBase4(0.85,0.85,0.85,1),
            state=DGG.NORMAL)
        l.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        l.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        self.mainBoxFrame.addItem(l, skipRefresh=True)

    def __createPropertyHeader(self, description):
        l = DirectLabel(
            text=description,
            text_scale=12,
            text_pos=(self.propertiesFrame["frameSize"][0], 0),
            text_align=TextNode.ALeft,
            frameSize=VBase4(self.propertiesFrame["frameSize"][0], self.propertiesFrame["frameSize"][1], -10, 20),
            frameColor=VBase4(0.85,0.85,0.85,1),
            state=DGG.NORMAL)
        l.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        l.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        self.boxFrame.addItem(l, skipRefresh=True)

    def __getFormated(self, value, isInt=False):
        if type(value) is int or isInt:
            return "{}".format(int(value))
        elif type(value) is not str:
            return "{:0.3f}".format(value)
        else:
            return value

    def __getPropertyName(self, definition):
        propName = definition.internalName
        if definition.elementGroup != "":
            # prepent the group
            propName = f"{definition.elementGroup}_{propName}"
        return propName

    def __getValues(self, definition, elementInfo):
        propName = self.__getPropertyName(definition)
        if propName in elementInfo.extraOptions:
            value = elementInfo.extraOptions[propName]
            logging.debug(f"Get property from extra options. {propName}={value}")
            return value
        elif not definition.canGetValueFromElement:
            # this has to come from the extra options, otherwise we just return
            # an empty string
            logging.debug(f"Can't get value of property {propName} from the element")
            return ""
        elif definition.getFunctionName:
            try:
                if type(definition.getFunctionName) == str:
                    value = getattr(elementInfo.element, definition.getFunctionName)()
                    #logging.debug(f"Try get property by function name. {definition.getFunctionName}={value}")
                    return value
                else:
                    #logging.debug(f"Try get property by function pointer. {definition.getFunctionName}")
                    return definition.getFunctionName()
            except:
                logging.exception(f"couldn't get value of {propName} by function {definition.getFunctionName}")
        else:
            value = None
            try:
                value = elementInfo.element[propName]
                #logging.debug(f"Try get property by direkt key access. {propName}={value}")
            except:
                component = elementInfo.element
                prop = propName
                if propName == "text_align":
                    return elementInfo.element.component("text0").align
                if "_" in propName:
                    #subElements = split(propName, "_")
                    #for subElement in subElements:
                    component = elementInfo.element.component(propName)
                    prop = propName.split("_")[-1]
                if hasattr(component, prop):
                    value = getattr(component, prop)
                    #logging.debug(f"Try get property by sub-component. {prop}={value}")
                else:
                    logging.debug(f"Couldn't get value for {propName}")
                    raise
            return value

    def __setValue(self, definition, elementInfo, value, valueAsString=""):
        propName = self.__getPropertyName(definition)
        if definition.isInitOption:
            # This is an initialization option, so we just store it as extra options
            if valueAsString != "":
                logging.debug(f"Store value as string in extra options. {propName}={valueAsString}")
                # if the value as string is set, this is probably the one we
                # want to store (e.g. paths to models, fonts, etc)
                elementInfo.extraOptions[propName] = valueAsString
            else:
                # if no string value is given, store the real value
                logging.debug(f"Store value as extra options. {propName}={value}")
                elementInfo.extraOptions[propName] = value
        elif definition.setFunctionName:
            try:
                if type(definition.setFunctionName) == str:
                    logging.debug(f"Try set value via function name. func: {definition.setFunctionName} value: {value}")
                    getattr(elementInfo.element, definition.setFunctionName)(value)
                else:
                    logging.debug(f"Try set value via function pointer. ptr: {definition.setFunctionName} value: {value}")
                    definition.setFunctionName(value)
                if definition.addToExtraOptions:
                    # check if we want to store it as a string or the real value
                    if valueAsString != "":
                        logging.debug(f"Additionally store value as string in extra options. {propName}={valueAsString}")
                        elementInfo.extraOptions[propName] = valueAsString
                    else:
                        logging.debug(f"Additionally store value as extra options. {propName}={value}")
                        elementInfo.extraOptions[propName] = value
            except:
                # setting the element failed, revert to old value in case it was
                # partly set
                logging.exception(f"couldn't set value of {propName} to value {value}")
                elementInfo.element[propName] = oldValue
        else:
            # get the old value of the property
            oldValue = self.__getValues(definition, elementInfo)
            try:
                logging.debug(f"Try set value by direct key access. {propName}={value}")
                # try to set the new value on the property
                elementInfo.element[propName] = value

                # in addition, if this should be stored in extra options
                # (e.g. if we can't get the property value from the element
                # itself in other ways)
                if definition.addToExtraOptions:
                    # check if we want to store it as a string or the real value
                    if valueAsString != "":
                        logging.debug(f"Additionally store value as string in extra options. {propName}={valueAsString}")
                        elementInfo.extraOptions[propName] = valueAsString
                    else:
                        logging.debug(f"Additionally store value as extra options. {propName}={value}")
                        elementInfo.extraOptions[propName] = value
            except:
                # setting the element failed, revert to old value in case it was
                # partly set
                logging.exception(f"couldn't set value of {propName} to value {value}")
                elementInfo.element[propName] = oldValue

        if definition.postProcessFunctionName is not None:
            if type(definition.postProcessFunctionName) == str:
                logging.debug(f"Run postprocess command by name. {definition.postProcessFunctionName}")
                getattr(elementInfo.element, definition.postProcessFunctionName)()
            else:
                logging.debug(f"Run postprocess command by pointer. {definition.postProcessFunctionName}")
                definition.postProcessFunctionName()

    def __addToKillRing(self, elementInfo, definition, oldValue, newValue):
        base.messenger.send("addToKillRing",
            [elementInfo, "set", definition.internalName, oldValue, newValue])

    def __createTextEntry(self, text, width, command, commandArgs=[]):
        def focusOut():
            messenger.send("reregisterKeyboardEvents")
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
                except:
                    if value.get(True) == "":
                        values.append(None)
                    else:
                        logging.exception("ERROR: NAN", value.get(True))
                        values.append(numberType(0))
            try:
                oldValue = self.__getValues(definition, elementInfo)
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
                if value is None: allValuesSet = False
                if value is not None: allValuesNone = False
            if allValuesNone:
                values = None
            elif allValuesSet:
                values = tuple(values)
            if allValuesNone or allValuesSet:
                self.__setValue(definition, elementInfo, values)
        self.__createPropertyHeader(definition.visiblename)
        values = self.__getValues(definition, elementInfo)
        if type(values) is int or type(values) is float:
            values = [values] * n
        if definition.nullable:
            if values is None:
                values = [""] * n
        width = (DGH.getRealWidth(self.boxFrame) - 2*SCROLLBARWIDTH) / n
        entryBox = DirectBoxSizer()
        for i in range(n):
            value = self.__getFormated(values[i])
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
            except:
                if text == "" and definition.nullable:
                    value = None
                else:
                    logging.exception("ERROR: NAN", value)
                    value = numberType(0)
            try:
                oldValue = self.__getValues(definition, elementInfo)
                self.__addToKillRing(elementInfo, definition, oldValue, value)
            except:
                logging.exception(f"{definition.internalName} not supported by undo/redo yet")
            self.__setValue(definition, elementInfo, value)
        self.__createPropertyHeader(definition.visiblename)
        valueA = self.__getValues(definition, elementInfo)
        if valueA is None and not definition.nullable:
            logging.error(f"Got None value for not nullable element {definition.internalName}")
        if valueA is not None:
            valueA = self.__getFormated(valueA, numberType is int)
        width = DGH.getRealWidth(self.boxFrame)
        entry = self.__createTextEntry(str(valueA), width, update, [elementInfo])
        self.boxFrame.addItem(entry, skipRefresh=True)

    def __createTextProperty(self, definition, elementInfo):
        def update(text, elementInfo):
            base.messenger.send("setDirtyFlag")
            try:
                oldValue = self.__getValues(definition, elementInfo)
                self.__addToKillRing(elementInfo.element, definition.internalName, oldValue, text)
            except:
                logging.exception(f"{definition.internalName} not supported by undo/redo yet")

            self.__setValue(definition, elementInfo, text)
        self.__createPropertyHeader(definition.visiblename)
        text = self.__getValues(definition, elementInfo)
        width = DGH.getRealWidth(self.boxFrame)
        entry = self.__createTextEntry(text, width, update, [elementInfo])
        self.boxFrame.addItem(entry, skipRefresh=True)

    def __createBoolProperty(self, definition, elementInfo):
        def update(value):
            base.messenger.send("setDirtyFlag")
            try:
                oldValue = self.__getValues(definition, elementInfo)
                self.__addToKillRing(elementInfo, definition, oldValue, value)
            except:
                logging.exception(f"{definition.internalName} not supported by undo/redo yet")
            self.__setValue(definition, elementInfo, value)
        self.__createPropertyHeader(definition.visiblename)
        valueA = self.__getValues(definition, elementInfo)
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
                if entry.get() != "":
                    value.append(entry.get())

            try:
                oldValue = self.__getValues(definition, elementInfo)
                self.__addToKillRing(elementInfo, definition, oldValue, value)
            except:
                logging.exception(f"{definition.internalName} not supported by undo/redo yet")

            self.__setValue(definition, elementInfo, value)

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
                self.boxFrame.refresh()
                self.resizeFrame()

        self.__createPropertyHeader(definition.visiblename)
        listItems = self.__getValues(definition, elementInfo)

        # make sure we have a list
        if listItems is None or isinstance(listItems, str):
            listItems = [listItems]

        width = DGH.getRealWidth(self.boxFrame)
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

    def __createTupleProperty(self, definition, elementInfo):
        def update(text, elementInfo, entries):
            base.messenger.send("setDirtyFlag")
            value = []

            for entry in entries:
                if entry.get() != "":
                    value.append(entry.get())

            value = tuple(value)

            try:
                oldValue = self.__getValues(definition, elementInfo)
                self.__addToKillRing(elementInfo, definition, oldValue, value)
            except:
                logging.exception(f"{definition.internalName} not supported by undo/redo yet")

            self.__setValue(definition, elementInfo, value)

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
                self.boxFrame.refresh()
                self.resizeFrame()

        self.__createPropertyHeader(definition.visiblename)
        listItems = self.__getValues(definition, elementInfo)
        width = DGH.getRealWidth(self.boxFrame)
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
                except:
                    logging.debug(f"command evaluation not supported: {text}")
                    logging.debug("set command without evalution")
                    command = text

            try:
                base.messenger.send("addToKillRing",
                    [updateElement, "set", updateAttribute, curCommand, text])
            except:
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
        width = (DGH.getRealWidth(parent)-10)
        entryWidth = width / 13
        entry = self.__createTextEntry(curCommand, entryWidth, update, [elementInfo])
        self.boxFrame.addItem(entry, skipRefresh=True)

    def __createPathProperty(self, definition, elementInfo):
        def update(text):
            value = text
            if text == "" and definition.nullable:
                value = None
            elif definition.loaderFunc is not None:
                try:
                    if type(definition.loaderFunc) is str:
                        value = eval(definition.loaderFunc)
                    else:
                        value = definition.loaderFunc(value)
                except:
                    logging.exception("Couldn't load path with loader function")
                    value = text
            base.messenger.send("setDirtyFlag")
            try:
                self.__setValue(definition, elementInfo, value, text)
            except:
                logging.exception("Couldn't load font: {}".format(text))
                updateElement[updateAttribute] = None
        def setPath(path):
            update(path)

            # make sure to take the actual value to write it to the textbox in
            # case something hapened while updating the value
            v = self.__getValues(definition, elementInfo)
            if v is None:
                v = ""
            entry.set(v)
        def selectPath(confirm):
            if confirm:
                setPath(self.browser.get())
            self.browser.hide()
        def showBrowser():
            self.browser = DirectFolderBrowser(
                selectPath,
                True,
                ConfigVariableString("work-dir-path", "~").getValue(),
                "",
                tooltip=self.tooltip)
            self.browser.show()
        self.__createPropertyHeader(definition.visiblename)
        path = self.__getValues(definition, elementInfo)
        if type(path) is not str:
            path = ""
        width = DGH.getRealWidth(self.boxFrame)
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
            oldValue = self.__getValues(definition, elementInfo)
            value = definition.valueOptions[selection]
            # Undo/Redo setup
            try:
                if oldValue != value:
                    self.__addToKillRing(elementInfo, definition, oldValue, value)
            except Exception as e:
                logging.exception(f"{definition.internalName} not supported by undo/redo yet")

            # actually set the value on the element
            self.__setValue(definition, elementInfo, value)

        self.__createPropertyHeader(definition.visiblename)
        if definition.valueOptions is None:
            return
        value = self.__getValues(definition, elementInfo)
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
        self.__createPropertyHeader(definition.visiblename)
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
            if l is None or r is None or b is None or t is None: return
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
        width = DGH.getRealWidth(self.boxFrame)
        entry = self.__createTextEntry(text, width, update)
        self.boxFrame.addItem(entry, skipRefresh=True)

    def __createRootReParent(self, elementInfo):
        def update(name):
            base.messenger.send("setDirtyFlag")
            parent = self.getEditorPlacer(name)
            elementInfo.element.reparentTo(parent)
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


    #
    # OLD...
    #

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

