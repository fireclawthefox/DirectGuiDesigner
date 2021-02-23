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

class DirectGuiDesignerJSONTools:
    functionMapping = {
        "base":{"initialText":"get"},
        "text":{"align":"align", "scale":"scale", "pos":"pos", "fg":"fg", "bg":"bg", "wordwrap":"wordwrap"}}

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

    def getProjectJSON(self, guiElementsDict, getEditorFrame, usePixel2D):
        self.guiElementsDict = guiElementsDict
        jsonElements = {}
        jsonElements["ProjectVersion"] = "0.2a"
        jsonElements["EditorConfig"] = {}
        jsonElements["EditorConfig"]["usePixel2D"] = usePixel2D
        jsonElements["EditorConfig"]["canvasSize"] = repr(getEditorFrame()["canvasSize"])
        jsonElements["ComponentList"] = {}

        self.writeSortedContent(None, jsonElements)

        return jsonElements

    def writeSortedContent(self, root, jsonElements):
        """To have everything in the right order, we're going to go through all
        elements here and add them from top to bottom, first the parents, then
        respectively their children."""
        for name, elementInfo in self.guiElementsDict.items():
            if elementInfo.parent == root:
                try:
                    jsonElements["ComponentList"][elementInfo.name] = self.__createJSONEntry(elementInfo)
                except Exception as e:
                    logging.exception("error while writing {}:".format(elementInfo.name))
                    base.messenger.send("showWarning", ["error while writing {}:".format(elementInfo.name)])
                self.writeSortedContent(elementInfo, jsonElements)

    def __createJSONEntry(self, elementInfo):
        return {
                "element":self.__writeElement(elementInfo),
                "type":elementInfo.type,
                "parent":self.__writeParent(elementInfo.parent),
                "command":elementInfo.command,
                "extraArgs":elementInfo.extraArgs,
                "extraOptions":elementInfo.extraOptions,
            }

    def __writeParent(self, parent):
        if parent is None: return "root"
        self.canvasParents = [
            "canvasTopCenter","canvasBottomCenter","canvasLeftCenter","canvasRightCenter",
            "canvasTopLeft","canvasTopRight","canvasBottomLeft","canvasBottomRight"]
        if type(parent) == type(NodePath()):
            if parent.getName() in self.canvasParents:
                return parent.getName().replace("canvas", "a2d")
            else:
                return parent.getName()
        if parent.element.guiId in self.guiElementsDict.keys():
            return self.guiElementsDict[parent.element.guiId].name
        return parent.element.guiId

    def __getAllSubcomponents(self, componentName, component, componentPath):
        # we only respect the first state for now
        if componentName[-1:].isdigit():
            if not componentName[-1:].endswith("0"):
                return

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
            if name[-1:].isdigit():
                if name[-1:].endswith("0"):
                    # first state of this component
                    name = name[:-1]
            if name != "":
                name += "_"
            for key in self.functionMapping.keys():
                if key in name:
                    for option, value in self.functionMapping[key].items():
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
                        optionValue = reprFunc(element[value])
                        elementJson[name + option] = optionValue
            if not hasattr(element, "options"): continue

            for option in element.options():
                if option[DGG._OPT_DEFAULT] in self.ignoreOptions: continue

                containsIgnore = False
                for ignoreOption in self.ignoreOptionsWithSub:
                    if option[DGG._OPT_DEFAULT] in self.keepExactIgnoreOptionsWithSub: continue
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
