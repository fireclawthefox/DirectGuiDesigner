#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

import os
import json
from direct.gui import DirectGuiGlobals as DGG
from DirectGuiDesignerPathSelect import DirectGuiDesignerPathSelect

from panda3d.core import LVecBase2f, LVecBase3f, LVecBase4f, LPoint2f, LPoint3f, LPoint4f
from panda3d.core import LVecBase2, LVecBase3, LVecBase4, LPoint2, LPoint3, LPoint4


import importlib.util



class DirectGuiDesignerLoaderProject:
    funcMap = {"initialText":"set"}
    # This prioList will be walked through if all other options not in
    # this list have already been set
    prioList = ["frameSize"]
    setAsOption = ["frameSize", "barColor", "barRelief", "range", "value"]
    ignoreMap = ["state"]

    def __init__(self, visualEditorInfo, elementHandler):
        self.extraOptions = ["borderWidth", "frameColor", "initialText", "clipSize"]
        self.parentMap = {}
        self.radiobuttonOthersDict = {}
        self.elementDict = {}
        self.elementHandler = elementHandler
        self.visualEditorInfo = visualEditorInfo
        self.visualEditor = visualEditorInfo.element
        self.dlgPathSelect = DirectGuiDesignerPathSelect(
            self.Load, "Load Project File", "Load file path", "Load", "~/export.json")

    def get(self):
        return self.elementDict

    def Load(self, doLoad):
        if doLoad:
            path = self.dlgPathSelect.getPath()
            path = os.path.expanduser(path)
            path = os.path.expandvars(path)

            with open(path, 'r') as infile:
                fileContent = json.load(infile)
            self.createdParents = ["root"]
            self.postponedElements = {}
            for elementName, elementInfo in fileContent.items():
                self.__createElement(elementName, elementInfo)

            for elementInfo, option in self.radiobuttonOthersDict.items():
                elementList = []
                for elementId, info in self.elementDict.items():
                    if info.elementName in option:
                        elementList.append(info.element)
                print(elementList)
                elementInfo.element["others"] = elementList

        self.dlgPathSelect.destroy()
        del self.dlgPathSelect

    def __createElement(self, name, info):
        if info["parentElement"] not in self.createdParents:
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
            if elementInfo["parentElement"] in self.createdParents:
                self.__createElement(elementName, elementInfo)

    def __createControl(self, jsonElementName, jsonElementInfo):
        funcName = "create{}".format(jsonElementInfo["elementType"])
        if hasattr(self.elementHandler, funcName):
            parentName = jsonElementInfo["parentElement"]
            parent = None
            if parentName in self.parentMap.keys():
                parent = self.elementDict[self.parentMap[parentName]]
            if funcName == "createDirectEntryScroll":
                elementInfo = getattr(self.elementHandler, funcName)(parent.element if parent is not None else None, False)
            else:
                elementInfo = getattr(self.elementHandler, funcName)(parent.element if parent is not None else None)

            # load the extra definitions of the element info
            elementInfo.command = jsonElementInfo["command"]
            elementInfo.extraArgs = jsonElementInfo["extraArgs"]
            elementInfo.extraOptions = jsonElementInfo["extraOptions"]
            elementInfo.elementName = jsonElementName

            if elementInfo is None: return
            if type(elementInfo) is tuple:
                if parent is not None and "DirectScrolledList" == parent.elementType:
                    parent.element.addItem(elementInfo[0].element)
                elif parent is not None and "DirectEntryScroll" == parent.elementType:
                    parent.element.setEntry(elementInfo[0].element)
                    parent.extraOptions["entry"] = "self." + elementInfo[0].elementName
                for entry in elementInfo:
                    entry.parentElement = parent
                    # TODO: Check how this works! ESP. Saving TOO
                    self.__setProperties(entry, jsonElementInfo)
                    self.elementDict[entry.element.guiId] = entry
                    self.parentMap[jsonElementName] = entry.element.guiId
            else:
                elementInfo.parentElement = parent
                if parent is not None and "DirectScrolledList" == parent.elementType:
                    parent.element.addItem(elementInfo.element)
                elif parent is not None and "DirectEntryScroll" == parent.elementType:
                    parent.element.setEntry(elementInfo.element)
                    parent.extraOptions["entry"] = "self." + elementInfo.elementName
                self.__setProperties(elementInfo, jsonElementInfo)
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
            print(elementInfo.element.options())
            options = self.extraOptions + elementInfo.element.options()
            if name in self.ignoreMap: return
            if name in options:
                if name in self.funcMap.keys():
                    funcName = self.funcMap[name]
                    if hasattr(elementInfo.element, funcName):
                        getattr(elementInfo.element, funcName)(eval(value))
                elif elementInfo.element.isinitoption(name):
                    funcName = "set{}{}".format(name[0].upper(), name[1:])
                    if hasattr(elementInfo.element, funcName):
                        getattr(elementInfo.element, funcName)(eval(value))
                else:
                    elementInfo.element[name] = eval(value)
            else:
                components = name.split("_")
                if len(components) > 1:
                    component = components[0]
                    elementInfo.element.component(component)[components[1]] = eval(value)
                else:
                    funcName = "set{}{}".format(name[0].upper(), name[1:])
                    if name in self.setAsOption:
                        elementInfo.element[name] = eval(value)
                    elif hasattr(elementInfo.element, funcName):
                        getattr(elementInfo.element, funcName)(eval(value))
                    else:
                        elementInfo.element[name] = eval(value)
        except Exception as e:
            print("Couldn't set Property with Name '{}' to {}".format(name, value))
            print(e)

