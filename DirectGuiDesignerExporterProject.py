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
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectDialog import YesNoDialog

from DirectGuiDesignerPathSelect import DirectGuiDesignerPathSelect

class DirectGuiDesignerExporterProject:
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
            jsonElements[name] = self.__createJSONEntry(elementInfo)

        with open(path, 'w') as outfile:
            json.dump(jsonElements, outfile, indent=2)

    def __createJSONEntry(self, elementInfo):
        return {
                "element":self.__writeElement(elementInfo),
                "elementType":elementInfo.elementType,
                "parentElement":self.__writeParent(elementInfo.parentElement),
                "extraDefinitions":elementInfo.extraDefinitions,
            }

    def __writeParent(self, parent):
        if parent is None: return "root"
        return parent.element.guiId

    def __writeElement(self, elementInfo):
        element = elementInfo.element
        #print(element.options())
        elementJson = {}
        for option in element.options():
            if not option[DGG._OPT_FUNCTION]:
                if option[DGG._OPT_VALUE] != element[option[DGG._OPT_DEFAULT]]:
                    elementJson[option[DGG._OPT_DEFAULT]] = element[option[DGG._OPT_DEFAULT]]
            else:
                funcName = "get{}{}".format(option[DGG._OPT_DEFAULT][0].upper(), option[DGG._OPT_DEFAULT][1:])
                propName = "{}".format(option[DGG._OPT_DEFAULT])
                print(funcName)
                if hasattr(element, funcName):
                    print("Call:", funcName)
                    value = getattr(element, funcName)()
                    if option[DGG._OPT_VALUE] != value:
                        elementJson[option[0]] = str(value)
                elif hasattr(element, propName):
                    print("Property:", propName)
                    if not callable(type(getattr(element, propName))):
                        print("GOOD")
                        # TODO: Check if we ever get here at al
                        value = getattr(element, propName)
                        if option[DGG._OPT_VALUE] != value:
                            elementJson[option[0]] = str(value)
                else:
                    try:
                        if option[DGG._OPT_VALUE] != element[option[DGG._OPT_DEFAULT]]:
                            elementJson[option[DGG._OPT_DEFAULT]] = element[option[DGG._OPT_DEFAULT]]
                    except:
                        print("Can't write:", option[DGG._OPT_DEFAULT])


        print(elementJson)
        return elementJson

