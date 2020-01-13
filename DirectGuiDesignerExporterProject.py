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

from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectDialog import YesNoDialog

from DirectGuiDesignerPathSelect import DirectGuiDesignerPathSelect
from DirectGuiDesignerJSONTools import DirectGuiDesignerJSONTools

class DirectGuiDesignerExporterProject:
    def __init__(self, fileName, guiElementsDict, getEditorFrame, usePixel2D, exceptionSave=False, tooltip=None):
        self.guiElementsDict = guiElementsDict
        self.getEditorFrame = getEditorFrame
        self.usePixel2D = usePixel2D

        if exceptionSave:
            self.excSave()
            return

        self.dlgPathSelect = DirectGuiDesignerPathSelect(
            self.save, "Save Project File", "Save file path", "Save", fileName, tooltip)

    def excSave(self):
        self.dlgOverwrite = None
        self.dlgOverwriteShadow = None

        tmpPath = os.path.join(tempfile.gettempdir(), "DGDExceptionSave.json")
        self.__executeSave(True, tmpPath)
        logging.info("Wrote crash session file to {}".format(tmpPath))

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
                    extraArgs=[path],
                    scale=300,
                    pos=(base.getSize()[0]/2, 0, -base.getSize()[1]/2),
                    parent=base.pixel2d)
                self.dlgOverwriteShadow = DirectFrame(
                    pos=(base.getSize()[0]/2 + 10, 0, -base.getSize()[1]/2 - 10),
                    sortOrder=0,
                    frameColor=(0,0,0,0.5),
                    frameSize=self.dlgOverwrite.bounds,
                    scale=300,
                    parent=base.pixel2d)
            else:
                self.__executeSave(True, path)
            base.messenger.send("setLastPath", [path])
        self.dlgPathSelect.destroy()
        del self.dlgPathSelect

    def __executeSave(self, overwrite, path):
        if self.dlgOverwrite is not None: self.dlgOverwrite.destroy()
        if self.dlgOverwriteShadow is not None: self.dlgOverwriteShadow.destroy()
        if not overwrite: return

        jsonTools = DirectGuiDesignerJSONTools()
        jsonElements = jsonTools.getProjectJSON(self.guiElementsDict, self.getEditorFrame, self.usePixel2D)
        with open(path, 'w') as outfile:
            json.dump(jsonElements, outfile, indent=2)

        base.messenger.send("clearDirtyFlag")

