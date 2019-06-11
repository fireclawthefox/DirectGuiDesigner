#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

import os
import json
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
            path = self.dlgPathSelect.getPath()
            path = os.path.expanduser(path)
            path = os.path.expandvars(path)
            if os.path.exists(path):
                self.dlgOverwrite = YesNoDialog(
                    text="File already Exist.\nOverwrite?",
                    relief=1,
                    frameSize=(-0.5,0.5,-0.3,0.2),
                    command=self.__executeSave,
                    extraArgs=[path])
            else:
                self.__executeSave(True, path)
        self.dlgPathSelect.destroy()
        del self.dlgPathSelect

    def __executeSave(self, overwrite, path):
        if self.dlgOverwrite is not None: self.dlgOverwrite.destroy()
        if not overwrite: return

        jsonContent = ""

        jsonElements = []
        for name, elementInfo in self.guiElementsDict.items():
            jsonElements.append(self.__createJSONEntry(name, elementInfo))

        with open(path, 'w') as outfile:
            json.dump(jsonElements, outfile, indent=2)

    def __createJSONEntry(self, name, elementInfo):
        json.dumps({
            name: {
                "element":elementInfo.element.guiId,
                "elementType":elementInfo.elementType,
                "parentElement":elementInfo.parentElement,
                "extraDefinitions":elementInfo.extraDefinitions
            }})

