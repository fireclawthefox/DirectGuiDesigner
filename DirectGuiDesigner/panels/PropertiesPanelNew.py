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

from DirectGuiDesigner.core import WidgetDefinition

class PropertyInfo:
    def __init__(self, displayName, propertyName, propertyType, customCommandName, customSelectionDict):
        self.displayName = displayName
        self.propertyName = propertyName
        self.propertyType = propertyType
        self.customCommandName = customCommandName
        self.customSelectionDict = customSelectionDict

SCROLLBARWIDTH = 20

class PropertiesPanel():
    scrollSpeedUp = -0.001
    scrollSpeedDown = 0.001

    def __init__(self, parent, getEditorRootCanvas, getEditorPlacer, tooltip):
        height = DGH.getRealHeight(parent)
        # A list containing the prooperty information
        self.customProperties = []
        self.tooltip = tooltip
        self.parent = parent

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
        self.headerText = headerText
        self.elementInfo = elementInfo
        self.elementDict = elementDict
        # create the frame that will hold all our properties
        self.boxFrame = DirectBoxSizer(
            orientation=DGG.VERTICAL,
            itemAlign=DirectBoxSizer.A_Left,
            frameColor=VBase4(0,0,0,0),
            parent=self.propertiesFrame.getCanvas(),
            suppressMouse=True,
            state=DGG.NORMAL)
        self.boxFrame.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        self.boxFrame.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])

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
        self.boxFrame.addItem(l)

        #element = elementInfo.element

        # Set up all the properties
        try:
            # check if we have a definition for this specific GUI element
            if elementInfo.type in WidgetDefinition.DEFINITIONS:
                # create the main set of properties to edit
                wd = WidgetDefinition.DEFINITIONS[elementInfo.type]
                # create a header for this type of element
                self.__createInbetweenHeader(elementInfo.type)
                for definition in wd:
                    self.createProperty(definition, elementInfo)

                # create the sub component set of properties to edit
                writtenComponentNames = []
                groups = {}
                for componentName, componentDefinition in elementInfo.element._DirectGuiBase__componentInfo.items():
                    widget = componentDefinition[0]
                    wType = componentDefinition[2]
                    group = componentDefinition[4]

                    # store the sub widget as an element info object
                    subWidgetElementInfo = copy.copy(elementInfo)
                    subWidgetElementInfo.element = widget

                    if group is not None:
                        # check if we haven't done that group before and if it
                        # actually has a definition for the widget
                        if group not in writtenComponentNames:
                            # store this group as written component
                            writtenComponentNames.append(group)

                            # check if this component has definitions
                            if wType in WidgetDefinition.DEFINITIONS:
                                # write the header for this group
                                self.__createInbetweenHeader(group)
                                subWd = WidgetDefinition.DEFINITIONS[wType]
                                for definition in subWd:
                                    # create the property for all the defined
                                    self.createProperty(definition, subWidgetElementInfo)
                    else:
                        # store this group as written component
                        writtenComponentNames.append(componentName)

                        # check if this component has definitions
                        if wType in WidgetDefinition.DEFINITIONS:
                            # write the header for this component
                            self.__createInbetweenHeader(componentName)
                            subWd = WidgetDefinition.DEFINITIONS[wType]
                            for definition in subWd:
                                self.createProperty(definition, subWidgetElementInfo)

                    #if group not in groups and wType in WidgetDefinition.DEFINITIONS:
                    #    print(f"found group: {group} of widget type {wType}")
                    #    groups[group] = WidgetDefinition.DEFINITIONS[wType]


                '''
                # create properties for all sub groups
                for group, definitions in groups.items():
                    for definition in definitions:
                        definition.elementGroup = group
                    self.createProperty(definition, elementInfo)

                print("================ OPTION INFO ================")
                print("_optionInfo")
                print(element._optionInfo)

                print("")
                print("options")
                print(element.options())

                print("")
                # get sub-groups
                groups = []
                for key, value in element._DirectGuiBase__componentInfo.items():
                    group = value[4]
                    if group not in groups:
                        groups.append(group)

                print("================ GROUPS ================")
                print(groups)

                for component in groups:
                    print(component)

                    if component in element._DirectGuiBase__componentInfo:
                        # Call cget on the component.
                        print("component")
                        print(element._DirectGuiBase__componentInfo[component])
                    else:
                        # If this is a group name, call cget for one of
                        # the components in the group.
                        for info in element._DirectGuiBase__componentInfo.values():
                            if info[4] == component:
                                print("sub component")
                                print(info)
                                subWd = WidgetDefinition.DEFINITIONS[info[2]]
                                print(subWd)
                                break
                '''
        except:
            e = sys.exc_info()[1]
            base.messenger.send("showWarning", [str(e)])
            logging.exception("Error while loading properties panel")

        self.boxFrame.refresh()
        #
        # Reset property Frame framesize
        #
        self.propertiesFrame["canvasSize"] = (
            0,
            self.propertiesFrame["frameSize"][1]-SCROLLBARWIDTH,
            self.boxFrame.bounds[2],
            0)
        self.propertiesFrame.setCanvasSize()

        a = self.propertiesFrame["canvasSize"][2]
        b = abs(self.propertiesFrame["frameSize"][2]) + self.propertiesFrame["frameSize"][3]
        scrollDefault = 200
        s = -(scrollDefault / (a / b))

        self.propertiesFrame["verticalScroll_scrollSize"] = s
        self.propertiesFrame["verticalScroll_pageSize"] = s


    def createProperty(self, definition, elementInfo):
        if definition.editType is WidgetDefinition.PropertyEditTypes.integer:
            self.__createNumberInput(definition, elementInfo, int)
        elif definition.editType is WidgetDefinition.PropertyEditTypes.float:
            self.__createNumberInput(definition, elementInfo, float)
        elif definition.editType is WidgetDefinition.PropertyEditTypes.bool:
            self.__createBoolProperty(definition, elementInfo)
        elif definition.editType is WidgetDefinition.PropertyEditTypes.text:
            self.__createTextProperty(definition, elementInfo)
        elif definition.editType is WidgetDefinition.PropertyEditTypes.base2:
            self.__createBaseNInput(definition, elementInfo, 2)
        elif definition.editType is WidgetDefinition.PropertyEditTypes.base3:
            self.__createBaseNInput(definition, elementInfo, 3)
        elif definition.editType is WidgetDefinition.PropertyEditTypes.base4:
            self.__createBaseNInput(definition, elementInfo, 4)
        elif definition.editType is WidgetDefinition.PropertyEditTypes.command:
            self.__createCustomCommand(definition, elementInfo)
        elif definition.editType is WidgetDefinition.PropertyEditTypes.path:
            self.__createPathProperty(definition, elementInfo)
        elif definition.editType is WidgetDefinition.PropertyEditTypes.optionMenu:
            self.__createOptionMenuProperty(definition, elementInfo)
        elif definition.editType is WidgetDefinition.PropertyEditTypes.list:
            pass
        elif definition.editType is WidgetDefinition.PropertyEditTypes.tuple:
            pass
        elif definition.editType is WidgetDefinition.PropertyEditTypes.resetFrameSize:
            pass

    def clear(self):
        if self.boxFrame is not None:
            self.boxFrame.destroy()

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
        self.boxFrame.addItem(l, skipRefresh=True)

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
            return elementInfo.extraOptions[propName]
        elif not definition.canGetValueFromElement:
            # this has to come from the extra options, otherwise we just return
            # an empty string
            return ""
        else:
            value = None
            try:
                value = elementInfo.element[propName]
            except:
                #print(f"CHECKING FOR {propName}")
                component = elementInfo.element
                prop = propName
                if "_" in propName:
                    #subElements = split(propName, "_")
                    #for subElement in subElements:
                    component = elementInfo.element.component(propName)
                    prop = propName.split("_")[-1]
                if hasattr(component, prop):
                    value = getattr(component, prop)
                else:
                    #print("AND IT'S NOT WORKING...'")
                    raise
            return value

    def __setValue(self, definition, elementInfo, value, valueAsString=""):
        propName = self.__getPropertyName(definition)
        if definition.isInitOption:
            # This is an initialization option, so we just store it as extra options
            if valueAsString != "":
                # if the value as string is set, this is probably the one we
                # want to store (e.g. paths to models, fonts, etc)
                elementInfo.extraOptions[propName] = valueAsString
            else:
                # if no string value is given, store the real value
                elementInfo.extraOptions[propName] = value
        else:
            # get the old value of the property
            oldValue = self.__getValues(definition, elementInfo)
            try:
                # try to set the new value on the property
                elementInfo.element[propName] = value

                # in addition, if this should be stored in extra options
                # (e.g. if we can't get the property value from the element
                # itself in other ways)
                if definition.addToExtraOptions:
                    # check if we want to store it as a string or the real value
                    if valueAsString != "":
                        elementInfo.extraOptions[propName] = valueAsString
                    else:
                        elementInfo.extraOptions[propName] = value
            except:
                # setting the element failed, revert to old value in case it was
                # partly set
                logging.exception(f"couldn't set value of {propName} to value {value}")
                elementInfo.element[propName] = oldValue

    def __addToKillRing(self, element, updateProperty, oldValue, newValue):
        base.messenger.send("addToKillRing",
            [elementInfo.element, "set", definition.internalName, oldValue, value])

    def __createTextEntry(self, text, width, command):
        def focusOut():
            messenger.send("reregisterKeyboardEvents")
            command(entry.get())
        entry = DirectEntry(
            initialText=text,
            relief=DGG.SUNKEN,
            frameColor=(1,1,1,1),
            scale=12,
            width=width/12,
            overflow=True,
            command=command,
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
        def update(text):
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
                oldValue = self.__getValues(elementInfo, definition)
                differ = False
                if oldValue is not None:
                    for i in range(n):
                        if oldValue[i] != values[i]:
                            differ = True
                            break
                if differ:
                    self.__addToKillRing(elementInfo.element, definition.internalName, oldValue, values)
            except:
                print(definition.internalName, " not supported by undo/redo yet")
            allValuesSet = True
            allValuesNone = True
            for value in values:
                if value is None: allValuesSet = False
                if value is not None: allValuesNone = False
            if allValuesNone:
                print("ALL VALUES NONE")
                values = None
            elif allValuesSet:
                print("ALL VALUES SET")
                values = tuple(values)
            if allValuesNone or allValuesSet:
                print("UPDATE BASE N PROP")
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
            entry = self.__createTextEntry(str(value), width, update)
            entryList.append(entry)
            entryBox.addItem(entry)
        self.boxFrame.addItem(entryBox, skipRefresh=True)

    def __createNumberInput(self, definition, elementInfo, numberType):
        def update(text):
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
                self.__addToKillRing(elementInfo.element, definition.internalName, oldValue, value)
            except:
                print(definition.internalName, " not supported by undo/redo yet")
            self.__setValue(definition, elementInfo, value)
        self.__createPropertyHeader(definition.visiblename)
        valueA = self.__getValues(definition, elementInfo)
        valueA = self.__getFormated(valueA, numberType is int)
        width = DGH.getRealWidth(self.boxFrame)
        entry = self.__createTextEntry(str(valueA), width, update)
        self.boxFrame.addItem(entry, skipRefresh=True)

    def __createTextProperty(self, definition, elementInfo):
        def update(text):
            base.messenger.send("setDirtyFlag")
            try:
                oldValue = self.__getValues(definition, elementInfo)
                self.__addToKillRing(elementInfo.element, definition.internalName, oldValue, text)
            except:
                print(definition.internalName, " not supported by undo/redo yet")

            self.__setValue(definition, elementInfo, text)
        self.__createPropertyHeader(definition.visiblename)
        text = self.__getValues(definition, elementInfo)
        width = DGH.getRealWidth(self.boxFrame)
        entry = self.__createTextEntry(text, width, update)
        self.boxFrame.addItem(entry, skipRefresh=True)

    def __createBoolProperty(self, definition, elementInfo):
        def update(value):
            base.messenger.send("setDirtyFlag")
            try:
                oldValue = self.__getValues(definition, elementInfo)
                self.__addToKillRing(elementInfo.element, definition.internalName, oldValue, value)
            except:
                print(definition.internalName, " not supported by undo/redo yet")
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

    def __createCustomCommandProperty(self, description, updateElement, updateAttribute, elementInfo):
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
        self.__createPropertyHeader(description)
        curCommand = ""
        if updateAttribute in elementInfo.extraOptions:
            curCommand = elementInfo.extraOptions[updateAttribute]
        width = (DGH.getRealWidth(parent)-10)
        entryWidth = width / 13
        entry = self.__createTextEntry(curCommand, entryWidth, update)
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
            value = definition.valueOptions[selection]
            self.__setValue(definition, elementInfo, value)
        self.__createPropertyHeader(definition.visiblename)
        if definition.valueOptions is None:
            print(f"FAILED TO SET UP OPTION MENU FOR {definition.visiblename}")
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
        width = (DGH.getRealWidth(parent)-10)
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
        width = (DGH.getRealWidth(parent)-10)
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
        width = (DGH.getRealWidth(parent)-10)
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
        box = DirectBoxSizer(parent=parent, pos=startPos)
        box.setX(box.getX() + 10)

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

