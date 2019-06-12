#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

import os
import json
from DirectGuiDesignerPathSelect import DirectGuiDesignerPathSelect


import importlib.util



class DirectGuiDesignerLoaderProject:
    def __init__(self, visualEditorInfo, elementHandler):
        self.elementDict = {}
        self.parentMap = {}
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
            elementInfo = getattr(self.elementHandler, funcName)(parent.element if parent is not None else None)
            if parent is None:
                parent = self.visualEditorInfo
            if elementInfo is None: return
            if type(elementInfo) is tuple:
                if "DirectScrolledList" == parentName.elementType:
                    parent.element.addItem(elementInfo[0].element)
                for entry in elementInfo:
                    entry.parentElement = parent
                    # TODO: Check how this works! ESP. Saving TOO
                    self.__setProperties(entry, jsonElementInfo)
                    self.elementDict[entry.element.guiId] = entry
                    self.parentMap[jsonElementName] = entry.element.guiId
            else:
                elementInfo.parentElement = parent
                if "DirectScrolledList" == parent.elementType:
                    parent.element.addItem(elementInfo.element)
                self.__setProperties(elementInfo, jsonElementInfo)
                self.elementDict[elementInfo.element.guiId] = elementInfo
                self.parentMap[jsonElementName] = elementInfo.element.guiId
            base.messenger.send("refreshStructureTree")

    def __setProperties(self, elementInfo, jsonElementInfo):
        for name, value in jsonElementInfo["element"].items():
            #TODO: Check if INIT OPT
            elementInfo.element[name] = value

