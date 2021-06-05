#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

import os
import json
import logging
import tempfile

from direct.showbase.DirectObject import DirectObject
from direct.gui import DirectGuiGlobals as DGG
from DirectGuiDesigner.dialogs.PathSelect import PathSelect

from panda3d.core import TextNode
from panda3d.core import LVecBase2f, LVecBase3f, LVecBase4f, LPoint2f, LPoint3f, LPoint4f
from panda3d.core import LVecBase2, LVecBase3, LVecBase4, LPoint2, LPoint3, LPoint4


import importlib.util



class ProjectLoader(DirectObject):
    funcMap = {"initialText":"set"}
    # This prioList will be walked through if all other options not in
    # this list have already been set
    prioList = ["frameSize"]
    setAsOption = ["frameSize", "canvasSize", "indicatorValue", "frameColor", "barColor", "barRelief", "range", "value", "relief", "borderWidth", "clipSize", "scrollBarWidth", "state"]
    ignoreMap = []#"state"]
    ignoreComponentSplit = ["text", "image"]

    def __init__(self, filePath, visualEditorInfo, elementHandler, customWidgetHandler, getEditorPlacer, exceptionLoading=False, tooltip=None, newProjectCall=None):
        self.newProjectCall = newProjectCall
        self.extraOptions = ["borderWidth", "frameColor", "initialText", "clipSize"]
        self.parentMap = {}
        self.radiobuttonOthersDict = {}
        self.elementDict = {}
        self.elementHandler = elementHandler
        self.customWidgetHandler = customWidgetHandler
        self.visualEditorInfo = visualEditorInfo
        self.visualEditor = visualEditorInfo.element
        self.getEditorPlacer = getEditorPlacer
        self.hasErrors = False
        if exceptionLoading:
            self.excLoad()
        else:
            self.dlgPathSelect = PathSelect(
                self.Load, "Load Project File", "Load file path", "Load", filePath, tooltip)

    def excLoad(self):
        tmpPath = os.path.join(tempfile.gettempdir(), "DGDExceptionSave.json")
        self.__executeLoad(tmpPath)

    def get(self):
        return self.elementDict

    def Load(self, doLoad):
        if doLoad:
            path = self.dlgPathSelect.getPath()
            path = os.path.expanduser(path)
            path = os.path.expandvars(path)

            if not os.path.exists(path):
                base.messenger.send("showWarning", ["File \"{}\" does not exist.".format(path)])
                return

            if self.newProjectCall():
                self.__executeLoad(path)
            else:
                self.accept("clearDirtyFlag", self.__executeLoad, [path])

        self.dlgPathSelect.destroy()
        del self.dlgPathSelect

    def __executeLoad(self, path):
        fileContent = None
        with open(path, 'r') as infile:
            try:
                fileContent = json.load(infile)
            except Exception as e:
                logging.error("Couldn't load project file {}".format(infile))
                logging.exception(e)
                base.messenger.send("showWarning", ["Error while loading Project!\nPlease check output logs for more information."])
                return
        if fileContent is None:
            logging.error("Problems reading Project file: {}".format(infile))
            return

        self.canvasParents = [
            "a2dTopCenter","a2dBottomCenter","a2dLeftCenter","a2dRightCenter",
            "a2dTopLeft","a2dTopRight","a2dBottomLeft","a2dBottomRight"]
        self.createdParents = ["root"] + self.canvasParents
        self.postponedElements = {}
        if fileContent["ProjectVersion"] != "0.2a":
            logging.warning("Unsupported Project Version")
            base.messenger.send("showWarning", ["Unsupported Project Version"])
            return
        base.messenger.send("setVisualEditorParent", [fileContent["EditorConfig"]["usePixel2D"]])
        base.messenger.send("setVisualEditorCanvasSize", [eval(fileContent["EditorConfig"]["canvasSize"])])
        for name, elementInfo in fileContent["ComponentList"].items():
            self.__createElement(name, elementInfo)

        for elementInfo, option in self.radiobuttonOthersDict.items():
            elementList = []
            for elementId, info in self.elementDict.items():
                if info.name in option:
                    elementList.append(info.element)
            elementInfo.element["others"] = elementList

        if self.hasErrors:
            base.messenger.send("showWarning", ["Errors occured while loading the project!\nProject may not be fully loaded\nSee output log for more information."])
            return

        base.messenger.send("setLastPath", [path])
        base.messenger.send("updateElementDict-afterLoad", [self.elementDict])

    def __createElement(self, name, info):
        if info["parent"] not in self.createdParents:
            self.postponedElements[name] = info
            return

        # create the element
        self.__createControl(name, info)
        self.createdParents.append(name)

        if name in self.postponedElements.keys():
            del self.postponedElements[name]

        # check if we can create postponed elements
        for elementName, elementInfo in self.postponedElements.copy().items():
            if elementName in self.createdParents: continue
            if elementInfo["parent"] in self.createdParents:
                self.__createElement(elementName, elementInfo)

    def __createControl(self, jsonElementName, jsonElementInfo):
        funcName = "create{}".format(jsonElementInfo["type"])
        if hasattr(self.elementHandler, funcName):
            parentName = jsonElementInfo["parent"]
            parent = None
            if parentName in self.parentMap.keys():
                parent = self.elementDict[self.parentMap[parentName]]
            widget = self.customWidgetHandler.getWidget(jsonElementInfo["type"])
            if funcName == "createDirectEntryScroll":
                elementInfo = getattr(self.elementHandler, funcName)(parent.element if parent is not None else None, False)
            elif widget is not None:
                # Custom widget add
                elementInfo = getattr(self.elementHandler, funcName)(widget, parent.element if parent is not None else None)
            else:
                elementInfo = getattr(self.elementHandler, funcName)(parent.element if parent is not None else None)

            if elementInfo is None: return

            if parentName in self.canvasParents:
                elementInfo.element.reparentTo(self.getEditorPlacer(parentName))

            # load the extra definitions of the element info
            elementInfo.command = jsonElementInfo["command"]
            elementInfo.extraArgs = jsonElementInfo["extraArgs"]
            elementInfo.extraOptions = jsonElementInfo["extraOptions"]
            elementInfo.name = jsonElementName
            if "transparency" in jsonElementInfo:
                elementInfo.element.setTransparency(eval(jsonElementInfo["transparency"]))

            if type(elementInfo) is tuple:
                if parent is not None and "DirectScrolledList" == parent.type:
                    parent.element.addItem(elementInfo[0].element)
                elif parent is not None and "DirectEntryScroll" == parent.type:
                    parent.element.setEntry(elementInfo[0].element)
                    parent.extraOptions["entry"] = "self." + elementInfo[0].name
                parentWidget = self.customWidgetHandler.getWidget(parent.type if parent is not None else "")
                if parentWidget is not None:
                    if parentWidget.addItemFunction is not None:
                        # call custom widget add function
                        getattr(parent.element, parentWidget.addItemFunction)(elementInfo[0].element)

                for entry in elementInfo:
                    entry.parent = parent
                    # TODO: Check how this works! ESP. Saving TOO
                    self.__setProperties(entry, jsonElementInfo)
                    self.elementDict[entry.element.guiId] = entry
                    self.parentMap[jsonElementName] = entry.element.guiId
            else:
                elementInfo.parent = parent
                if parent is not None and "DirectScrolledList" == parent.type:
                    parent.element.addItem(elementInfo.element)
                elif parent is not None and "DirectEntryScroll" == parent.type:
                    parent.element.setEntry(elementInfo.element)
                    parent.extraOptions["entry"] = "self." + elementInfo.name
                parentWidget = self.customWidgetHandler.getWidget(parent.type if parent is not None else "")
                if parentWidget is not None:
                    if parentWidget.addItemFunction is not None:
                        # call custom widget add function
                        getattr(parent.element, parentWidget.addItemFunction)(elementInfo.element)
                self.__setProperties(elementInfo, jsonElementInfo)
                if elementInfo.type == "DirectScrolledFrame":
                    elementInfo.element.setScrollBarWidth()
                self.elementDict[elementInfo.element.guiId] = elementInfo
                self.parentMap[jsonElementName] = elementInfo.element.guiId
            base.messenger.send("refreshStructureTree")

    def __setProperties(self, elementInfo, jsonElementInfo):
        tempOptionDict = {}
        for name, value in jsonElementInfo["element"].items():
            if name == "others":
                self.radiobuttonOthersDict[elementInfo] = value
                continue
            if name in self.prioList:
                tempOptionDict[name] = value
            else:
                self.__setProp(elementInfo, name, value)

        for name, value in tempOptionDict.items():
            self.__setProp(elementInfo, name, value)

        if "frameSize" not in tempOptionDict.keys():
            elementInfo.element.resetFrameSize()

    def __setProp(self, elementInfo, name, value):
        try:
            options = self.extraOptions + elementInfo.element.options()
            if name in self.ignoreMap: return
            if name in options:
                self.__setPropValue(name, elementInfo.element, value)
            else:
                components = name.split("_")
                found = False
                for comp in components:
                    if comp in self.ignoreComponentSplit:
                        found = True
                if len(components) > 1 and not found:
                    componentName = components[0]
                    if elementInfo.element.hascomponent(componentName):
                        component = elementInfo.element.component(componentName)
                        optionName = components[-1]
                        self.__setPropValue(optionName, component, value)
                    else:
                        try:
                            self.__setPropValue(name, elementInfo.element, value)
                        except Exception as e:
                            logging.exception("Unsupported Property or item {}".format(name))
                else:
                    self.__setPropValue(name, elementInfo.element, value)
        except Exception as e:
            logging.exception("Couldn't set Property with Name '{}' to {}".format(name, value))
            self.hasErrors = True

    def __setPropValue(self, optionName, component, value):
        funcName = "set{}{}".format(optionName[0].upper(), optionName[1:])
        if optionName in self.setAsOption:
            component[optionName] = eval(value)
        elif optionName in self.funcMap.keys():
            funcName = self.funcMap[optionName]
            getattr(component, funcName)(eval(value))
        elif hasattr(component, funcName):
            getattr(component, funcName)(eval(value))
        else:
            component[optionName] = eval(value)
