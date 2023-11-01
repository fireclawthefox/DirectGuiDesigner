#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

import logging

from direct.gui import DirectGuiGlobals as DGG
from panda3d.core import NodePath
from DirectGuiDesigner.core.PropertyHelper import PropertyHelper
from DirectGuiDesigner.core.ElementInfo import ElementInfo
from DirectGuiDesigner.core.WidgetDefinition import PropertyEditTypes

class JSONTools:
    functionMapping = {
        "base":{"initialText":"get"},
        #"text":{"align":"align", "scale":"scale", "pos":"pos", "fg":"fg", "bg":"bg", "wordwrap":"wordwrap"}
        }

    subOptionMapping = {
        "image":{"scale":"scale", "pos":"pos"}}

    specialPropMapping = {
        "align":{
            "0":"TextNode.A_left",
            "1":"TextNode.A_right",
            "2":"TextNode.A_center",
            "3":"TextNode.A_boxed_left",
            "4":"TextNode.A_boxed_right",
            "5":"TextNode.A_boxed_center"
        }
    }

    ignoreMapping = {
        "DirectCheckButton":["indicator_text"],
        "DirectRadioButton":["indicator_text"],
    }
    ignoreFunction = ["state", "width"]
    ignoreOptions = ["guiId", "enableEdit"]
    ignoreOptionsWithSub = ["item_", "item0_"]
    keepExactIgnoreOptionsWithSub = ["item_text"]
    ignoreRepr = ["command"]

    explIncludeOptions = ["forceHeight", "numItemsVisible", "pos", "hpr", "scrollBarWidth", "initialText"]

    def getProjectJSON(
            self,
            guiElementsDict,
            getEditorFrame,
            getEditorRootCanvas,
            getAllEditorPlacers,
            allWidgetDefinitions,
            usePixel2D):
        self.guiElementsDict = guiElementsDict
        self.allWidgetDefinitions = allWidgetDefinitions
        self.getEditorFrame = getEditorFrame
        jsonElements = {}
        jsonElements["ProjectVersion"] = "0.2a"
        jsonElements["EditorConfig"] = {}
        jsonElements["EditorConfig"]["usePixel2D"] = usePixel2D
        jsonElements["EditorConfig"]["canvasSize"] = repr(getEditorFrame()["canvasSize"])
        jsonElements["ComponentList"] = {}

        self.writtenRoots = []

        self.getEditorRootCanvas = getEditorRootCanvas
        self.getAllEditorPlacers = getAllEditorPlacers

        roots = [None] + getAllEditorPlacers()

        for root in roots:
            self.writeSortedContent(root, jsonElements)
            for name, elementInfo in self.guiElementsDict.items():
                if elementInfo.parent not in self.writtenRoots:
                    self.writeSortedContent(elementInfo.parent, jsonElements)

        return jsonElements

    def writeSortedContent(self, root, jsonElements):
        """To have everything in the right order, we're going to go through all
        elements here and add them from top to bottom, first the parents, then
        respectively their children."""
        for name, elementInfo in self.guiElementsDict.items():
            if elementInfo.parent == root:
                if root not in self.writtenRoots: self.writtenRoots.append(root)
                try:
                    jsonElements["ComponentList"][elementInfo.name] = self.__createJSONEntry(elementInfo)
                except Exception as e:
                    logging.exception("error while writing {}:".format(elementInfo.name))
                    base.messenger.send("showWarning", ["error while writing {}:".format(elementInfo.name)])
                self.writeSortedContent(elementInfo, jsonElements)

    def __createJSONEntry(self, elementInfo):
        from DirectGuiDesigner.DirectGuiDesigner import DirectGuiDesigner
        addItemExtraArgs = []
        for arg in elementInfo.addItemExtraArgs:
            if isinstance(arg, NodePath):
                name = DirectGuiDesigner.elementDict[arg.guiId].name
                addItemExtraArgs.append(name)
            else:
                addItemExtraArgs.append(arg)

        return {
            "element": self.__writeElement(elementInfo),
            "type": elementInfo.type,
            "parent": self.__writeParent(elementInfo.parent),
            "command": elementInfo.command,
            "extraArgs": elementInfo.extraArgs,
            "extraOptions": elementInfo.extraOptions,
            "addItemExtraArgs": addItemExtraArgs,
            "addItemNode": elementInfo.addItemNode
        }

    def __writeParent(self, parent):
        if parent is None or parent == self.getEditorRootCanvas():
            return "root"
        canvasParents = self.getAllEditorPlacers()
        if type(parent) == type(NodePath()):
            if parent in canvasParents:
                return parent.getName().replace("canvas", "a2d")
            else:
                return parent.getName()
        if parent.element.guiId in self.guiElementsDict.keys():
            return self.guiElementsDict[parent.element.guiId].name
        return parent.element.guiId

    def __getAllSubcomponents(self, componentName, component, componentPath):
        if componentPath == "":
            componentPath = componentName
        else:
            componentPath += "_" + componentName

        self.componentsList[component] = componentPath
        if not hasattr(component, "components"): return
        for subcomponentName in component.components():
            self.__getAllSubcomponents(subcomponentName, component.component(subcomponentName), componentPath)

    def __writeElement(self, elementInfo):
        element = elementInfo.element
        elementJson = {}

        self.componentsList = {element:""}
        # Check if the component has any sub-components assigned, e.g.
        # component0_subcomp0_subsubcomp0
        # we want    ^   and  ^
        for subcomponentName in element.components():
            self.__getAllSubcomponents(subcomponentName, element.component(subcomponentName), "")

        hasError = False

        for element, name in self.componentsList.items():
            if elementInfo.type in self.ignoreMapping:
                if name in self.ignoreMapping[elementInfo.type]:
                    continue
            if name in self.ignoreRepr:
                reprFunc = lambda x: x
            else:
                reprFunc = repr
            if name != "":
                name += "_"

            for key in self.functionMapping.keys():
                if key in name:
                    for option, value in self.functionMapping[key].items():
                        if name + option not in elementInfo.valueHasChanged \
                        or not elementInfo.valueHasChanged[name + option]:
                            # skip unchanged values
                            continue

                        if callable(getattr(element, value)):
                            optionValue = reprFunc(getattr(element, value)())
                        else:
                            optionValue = reprFunc(getattr(element, value))

                        if option in self.specialPropMapping.keys():
                            optionValue = self.specialPropMapping[option][optionValue]
                        elementJson[name + option] = optionValue
            for key in self.subOptionMapping.keys():
                if key in name:
                    for option, value in self.subOptionMapping[key].items():
                        if name + option not in elementInfo.valueHasChanged \
                        or not elementInfo.valueHasChanged[name + option]:
                            # skip unchanged values
                            continue
                        optionValue = reprFunc(element[value])
                        elementJson[name + option] = optionValue

            if type(element).__name__ in self.allWidgetDefinitions:
                wdList = self.allWidgetDefinitions[type(element).__name__]
                for wd in wdList:
                    if wd.internalName == "" \
                    or wd.editType == PropertyEditTypes.command:
                        continue
                    subElementInfo = ElementInfo(
                        element,
                        elementInfo.type,
                        elementInfo.name,
                        elementInfo.parent,
                        elementInfo.extraOptions,
                        elementInfo.createAfter,
                        elementInfo.customImportPath)
                    #subElementInfo.element = element

                    value = PropertyHelper.getValues(wd, subElementInfo)
                    if hasattr(element, "options"):
                        for option in element.options():
                            if option[DGG._OPT_DEFAULT] == wd.internalName \
                            and option[DGG._OPT_VALUE] == value:
                                hasChanged = False
                                break

                            n = name + option[DGG._OPT_DEFAULT]
                            notInValueHasChanged = (
                                n not in elementInfo.valueHasChanged \
                                or not elementInfo.valueHasChanged[n])

                            hasChanged = True
                            if option[DGG._OPT_DEFAULT] == wd.internalName \
                            and notInValueHasChanged:
                                hasChanged = False
                                break
                    else:
                        newWidget = type(element)()
                        needCheck = True
                        n = name + wd.internalName
                        skipCheck = False
                        if n in elementInfo.valueHasChanged \
                        and elementInfo.valueHasChanged[n]:
                            hasChanged = True
                            skipCheck = True

                        if not skipCheck:
                            if wd.getFunctionName is not None:
                                if type(wd.getFunctionName) == str:
                                    try:
                                        origWidgetValue = getattr(
                                            newWidget,
                                            wd.getFunctionName)()
                                    except Exception:
                                        # this may happen if something hasn't
                                        # been set in the vanilla widget. E.g.
                                        # the geom of an OnscreenGeom. So there
                                        # must have been changes in the widget
                                        needCheck = False
                                else:
                                    origWidgetValue = wd.getFunctionName()
                            else:
                                origWidgetValue = getattr(
                                    newWidget,
                                    wd.internalName)

                            if needCheck and value == origWidgetValue:
                                hasChanged = False

                    if hasChanged:
                        if isinstance(value, str):
                            new_value = value
                        else:
                            new_value = reprFunc(value)
                        elementJson[name + wd.internalName] = new_value

            if not hasattr(element, "options"): continue

            for option in element.options():
                if option[DGG._OPT_DEFAULT] in self.ignoreOptions: continue
                if name + option[DGG._OPT_DEFAULT] not in elementInfo.valueHasChanged \
                or not elementInfo.valueHasChanged[name + option[DGG._OPT_DEFAULT]]:
                    # skip unchanged values
                    continue

                containsIgnore = False
                for ignoreOption in self.ignoreOptionsWithSub:
                    if option[DGG._OPT_DEFAULT] in self.keepExactIgnoreOptionsWithSub:
                        continue
                    if option[DGG._OPT_DEFAULT].startswith(ignoreOption):
                        containsIgnore
                        break
                if containsIgnore: continue

                if elementInfo.type in self.ignoreMapping:
                    if name + option[DGG._OPT_DEFAULT] in self.ignoreMapping[elementInfo.type]:
                        continue

                value = None

                funcName = "get{}{}".format(option[DGG._OPT_DEFAULT][0].upper(), option[DGG._OPT_DEFAULT][1:])
                propName = "{}".format(option[DGG._OPT_DEFAULT])
                if hasattr(element, funcName) and not option[DGG._OPT_DEFAULT] in self.ignoreFunction:
                    if funcName == "getColor":
                        # Savety check. I currently only know of this function that isn't set by default
                        if not element.hasColor(): continue
                    value = getattr(element, funcName)()
                elif hasattr(element, propName):
                    if callable(getattr(element, propName)):
                        value = getattr(element, propName)()
                    else:
                        value = getattr(element, propName)
                elif option[DGG._OPT_DEFAULT] in self.functionMapping["base"]:
                    funcName = self.functionMapping["base"][option[DGG._OPT_DEFAULT]]
                    if hasattr(element, funcName):
                        value = getattr(element, funcName)()
                    else:
                        hasError = True
                        logging.warning("Can't call: {}".format(option[DGG._OPT_DEFAULT]))
                else:
                    try:
                        value = element[option[DGG._OPT_DEFAULT]]
                    except Exception as e:
                        hasError = True
                        logging.warning("Can't write: {}".format(option[DGG._OPT_DEFAULT]))

                if (option[DGG._OPT_VALUE] != element[option[DGG._OPT_DEFAULT]] \
                or option[DGG._OPT_DEFAULT] in self.explIncludeOptions) \
                and not hasError:
                    if option[DGG._OPT_DEFAULT] in self.specialPropMapping:
                        value = self.specialPropMapping[option[DGG._OPT_DEFAULT]][reprFunc(value)]

                    if not (isinstance(value, type) and reprFunc(value).startswith("<class")):
                        elementJson[name + option[DGG._OPT_DEFAULT]] = reprFunc(value)

            # special options for specific elements
            if elementInfo.type == "DirectRadioButton":
                elementNameDict = {}
                others = []
                for key, value in self.guiElementsDict.items():
                    elementNameDict[value.element] = value.name
                for otherElement in elementInfo.element["others"]:
                    if otherElement in elementNameDict:
                        others.append("{}".format(elementNameDict[otherElement]))
                elementJson["others"] = others

        # transparency attribute
        elementJson["transparency"] = reprFunc(elementInfo.element.getTransparency())

        if hasError:
            base.messenger.send("showWarning", ["Saved Project with errors! See log for more information"])
        return elementJson
