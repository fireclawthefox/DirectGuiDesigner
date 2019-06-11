#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

import os
from direct.gui.DirectDialog import YesNoDialog

from DirectGuiDesignerPathSelect import DirectGuiDesignerPathSelect

class DirectGuiDesignerExporterPy:
    def __init__(self, guiElementsDict, visualEditor):
        self.guiElementsDict = guiElementsDict
        importStatements = {
            "DirectButton":"from direct.gui.DirectButton import DirectButton",
            "DirectEntry":"from direct.gui.DirectEntry import DirectEntry",
            "DirectEntryScroll":"from direct.gui.DirectEntryScroll import DirectEntryScroll",
            "DirectCheckBox":"from direct.gui.DirectCheckBox import DirectCheckBox",
            "DirectCheckButton":"from direct.gui.DirectCheckButton import DirectCheckButton",
            "DirectOptionMenu":"from direct.gui.DirectOptionMenu import DirectOptionMenu",
            "DirectRadioButton":"from direct.gui.DirectRadioButton import DirectRadioButton",
            "DirectSlider":"from direct.gui.DirectSlider import DirectSlider",
            "DirectScrollBar":"from direct.gui.DirectScrollBar import DirectScrollBar",
            "DirectScrolledList":"from direct.gui.DirectScrolledList import DirectScrolledList",
            "DirectScrolledListItem":"from direct.gui.DirectScrolledList import DirectScrolledListItem",
            "DirectLabel":"from direct.gui.DirectLabel import DirectLabel",
            "DirectWaitBar":"from direct.gui.DirectWaitBar import DirectWaitBar",
            "OkDialog":"from direct.gui.DirectDialog import OkDialog",
            "OkCancelDialog":"from direct.gui.DirectDialog import OkCancelDialog",
            "YesNoDialog":"from direct.gui.DirectDialog import YesNoDialog",
            "YesNoCancelDialog":"from direct.gui.DirectDialog import YesNoCancelDialog",
            "RetryCancelDialog":"from direct.gui.DirectDialog import RetryCancelDialog",
            "DirectFrame":"from direct.gui.DirectFrame import DirectFrame",
            "DirectScrolledFrame":"from direct.gui.DirectScrolledFrame import DirectScrolledFrame",
        }

        self.content="""#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file was created using the DirectGUI Designer
"""
        usedImports = []
        for name, elementInfo in self.guiElementsDict.items():
            if elementInfo.elementType not in usedImports:
                self.content = "{}\n{}".format(self.content, importStatements[elementInfo.elementType])
                usedImports.append(elementInfo.elementType)
        self.content = """
{}
from panda3d.core import (
    LPoint3f,
    LVecBase3f
)
from direct.showbase.ShowBase import ShowBase

class GUI:
    def __init__(self, rootParent=None):
        """.format(self.content)

        self.itemCounter = 0
        self.__createStructuredElements(visualEditor.getCanvas(), 0)

        self.content += """
app = ShowBase()
GUI()
app.run()"""

        self.dlgPathSelect = DirectGuiDesignerPathSelect(
            self.save, "Save Python File", "Save file path", "Save", "~/export.py")

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
        with open(path, 'w') as outfile:
            outfile.write(self.content)

    def __createStructuredElements(self, root, level):
        self.itemCounter += 1
        if level > 0:
            elementInfo = None
            if root.getName() in self.guiElementsDict.keys():
                elementInfo = self.guiElementsDict[elementNP.getName()]
            elif len(root.getName().split("-")) > 1 and root.getName().split("-")[1] in self.guiElementsDict.keys():
                elementInfo = self.guiElementsDict[root.getName().split("-")[1]]
            if elementInfo is not None:
                self.content += self.__createElement(elementInfo)
        if hasattr(root, "getChildren"):
            for child in root.getChildren():
                self.__createStructuredElements(child, level+1)

    def __createElement(self, elementInfo):
        return self.createGuiElement(elementInfo)
        #if hasattr(self, "create{}".format(elementInfo.elementType)):
        #    return getattr(self, "create{}".format(elementInfo.elementType))(elementInfo)
        #else:
        #    print("Unsuported element")

    def __getDefaultProperties(self, elementInfo):
        pText = ""
        if elementInfo.parentElement is not None:
            pText = "            parent=self.{},".format(elementInfo.parentElement.guiId.replace("-",""))
        else:
            pText = "            parent=rootParent,"
        element = elementInfo.element
        return """{}
            relief={},
            borderWidth={},
            frameSize=({},{},{},{}),
            frameColor={},
            pad={},
            pos={},
            hpr={},
            scale={},""".format(
            pText,
            element["relief"],
            element["borderWidth"],
            element.bounds[0],
            element.bounds[1],
            element.bounds[2],
            element.bounds[3],
            element["frameColor"],
            element["pad"],
            element.getPos(),
            element.getHpr(),
            element.getScale()
        )

    def createGuiElement(self, elementInfo):
        elementCode = """
        self.{} = {}(
{}""".format(
            elementInfo.element.guiId.replace("-",""),
            elementInfo.elementType,
            self.__getDefaultProperties(elementInfo))
        for definition in elementInfo.extraDefinitions:
            definitionValue = elementInfo.element[definition]
            if type(definitionValue) is str:
                elementCode = "{}\n            {}=\"{}\",".format(
                    elementCode, definition, definitionValue)
            else:
                elementCode = "{}\n            {}={},".format(
                    elementCode, definition, definitionValue)
        elementCode = "{}\n        )".format(elementCode)
        return elementCode


