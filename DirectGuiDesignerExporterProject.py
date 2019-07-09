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

from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectDialog import YesNoDialog

from DirectGuiDesignerPathSelect import DirectGuiDesignerPathSelect

class DirectGuiDesignerExporterProject:

    functionMapping = {
        "base":{"initialText":"get"},
        "text":{"align":"align", "scale":"scale", "pos":"pos", "fg":"fg", "bg":"bg"}}

    ignoreRepr = ["command"]

    def __init__(self, guiElementsDict, visualEditor):
        self.guiElementsDict = guiElementsDict

        self.dlgPathSelect = DirectGuiDesignerPathSelect(
            self.save, "Save Project File", "Save file path", "Save", "~/export.json")

    def save(self, doSave):
        if doSave:
            self.dlgOverwrite = None
            self.dlgOverwriteShadow = None
            path = self.dlgPathSelect.getPath()
            path = os.path.expanduser(path)
            path = os.path.expandvars(path)
            if os.path.exists(path):
                self.dlgOverwrite = YesNoDialog(
                    text="File already Exist.\nOverwrite?",
                    relief=DGG.RIDGE,
                    frameColor=(1,1,1,1),
                    frameSize=(-0.5,0.5,-0.3,0.2),
                    sortOrder=1,
                    button_relief=DGG.FLAT,
                    button_frameColor=(0.8, 0.8, 0.8, 1),
                    command=self.__executeSave,
                    extraArgs=[path])
                self.dlgOverwriteShadow = DirectFrame(
                    pos=(0.025, 0, -0.025),
                    sortOrder=0,
                    frameColor=(0,0,0,0.5),
                    frameSize=self.dlgOverwrite.bounds)
            else:
                self.__executeSave(True, path)
        self.dlgPathSelect.destroy()
        del self.dlgPathSelect

    def __executeSave(self, overwrite, path):
        if self.dlgOverwrite is not None: self.dlgOverwrite.destroy()
        if self.dlgOverwriteShadow is not None: self.dlgOverwriteShadow.destroy()
        if not overwrite: return

        jsonElements = {}
        for name, elementInfo in self.guiElementsDict.items():
            try:
                jsonElements[name] = self.__createJSONEntry(elementInfo)
            except Exception as e:
                logging.exception("error while writing {}:".format(elementInfo.name))
                base.messenger.send("showWarning", ["error while writing {}:".format(elementInfo.name)])

        with open(path, 'w') as outfile:
            json.dump(jsonElements, outfile, indent=2)

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
        for subcomponentName in element.components():
            self.__getAllSubcomponents(subcomponentName, element.component(subcomponentName), "")

        print(self.componentsList)

        for element, name in self.componentsList.items():
            if name in self.ignoreRepr:
                reprFunc = lambda x: x
            else:
                reprFunc = repr
            if name != "":
                name += "_"
            for key in self.functionMapping.keys():
                if key in name:
                    for option, value in self.functionMapping[key].items():
                        if callable(getattr(element, value)):
                            elementJson[name + option] = reprFunc(getattr(element, value)())
                        else:
                            elementJson[name + option] = reprFunc(getattr(element, value))

            if not hasattr(element, "options"): continue

            for option in element.options():
                print("Storing:", option)
                if not option[DGG._OPT_FUNCTION]:
                    print("NORMAL")
                    print("VALUES:")
                    print(option[DGG._OPT_VALUE])
                    print(element[option[DGG._OPT_DEFAULT]])
                    if option[DGG._OPT_VALUE] != element[option[DGG._OPT_DEFAULT]]:
                        print("DIFFERS")
                        elementJson[name + option[DGG._OPT_DEFAULT]] = reprFunc(element[option[DGG._OPT_DEFAULT]])
                    print("NORMAL END")
                else:
                    print("FUNCTION")
                    funcName = "get{}{}".format(option[DGG._OPT_DEFAULT][0].upper(), option[DGG._OPT_DEFAULT][1:])
                    propName = "{}".format(option[DGG._OPT_DEFAULT])
                    print(funcName)
                    if hasattr(element, funcName):
                        if funcName == "getColor":
                            # Savety check. I currently only know of this function that isn't set by default
                            if not element.hasColor(): continue
                        value = getattr(element, funcName)()
                        print("VALUES:")
                        print(option[DGG._OPT_DEFAULT])
                        print(value)
                        if option[DGG._OPT_VALUE] != value:
                            elementJson[name + option[0]] = reprFunc(value)
                    elif hasattr(element, propName):
                        print("Property:", propName)
                        if not callable(type(getattr(element, propName))):
                            print("GOOD")
                            # TODO: Check if we ever get here at al
                            value = getattr(element, propName)
                            print("VALUES:")
                            print(option[DGG._OPT_DEFAULT])
                            print(value)
                            if option[DGG._OPT_VALUE] != value:
                                elementJson[name + option[0]] = reprFunc(value)
                    elif option[DGG._OPT_DEFAULT] in self.functionMapping["base"]:
                        funcName = self.functionMapping["base"][option[DGG._OPT_DEFAULT]]
                        if hasattr(element, funcName):
                            value = getattr(element, funcName)()
                            print("VALUES:")
                            print(option[DGG._OPT_DEFAULT])
                            print(value)
                            if option[DGG._OPT_VALUE] != value:
                                elementJson[name + option[0]] = reprFunc(value)
                        else:
                            print("Can't call:", option[DGG._OPT_DEFAULT])
                    else:
                        try:
                            if option[DGG._OPT_VALUE] != element[option[DGG._OPT_DEFAULT]]:
                                print("VALUES:")
                                print(option[DGG._OPT_DEFAULT])
                                print(element[option[DGG._OPT_DEFAULT]])
                                elementJson[name + option[DGG._OPT_DEFAULT]] = reprFunc(element[option[DGG._OPT_VALUE]])
                        except:
                            print("Can't write:", option[DGG._OPT_DEFAULT])
                    print("FUNCTION END")

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

        #print(elementJson)
        return elementJson

