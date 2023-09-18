"""Module for saving a project to a '.gui' file."""

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

from DirectFolderBrowser.DirectFolderBrowser import DirectFolderBrowser

from DirectGuiDesigner.tools.JSONTools import JSONTools


class ExporterProject:
    """Class for saving a project to a '.gui' file."""

    def __init__(
            self,
            fileName,
            guiElementsDict,
            getEditorFrame,
            getEditorRootCanvas,
            getAllEditorPlacers,
            allWidgetDefinitions,
            usePixel2D,
            exceptionSave=False,
            autosave=False,
            tooltip=None):
        self.guiElementsDict = guiElementsDict
        self.getEditorFrame = getEditorFrame
        self.getEditorRootCanvas = getEditorRootCanvas
        self.getAllEditorPlacers = getAllEditorPlacers
        self.usePixel2D = usePixel2D
        self.isAutosave = False
        self.allWidgetDefinitions = allWidgetDefinitions

        if exceptionSave:
            self.excSave()
            return

        if autosave:
            self.isAutosave = True
            self.autoSave(fileName)
            return

        self.browser = DirectFolderBrowser(
            self.save,
            True,
            defaultPath=os.path.dirname(fileName),
            defaultFilename=os.path.split(fileName)[1],
            tooltip=tooltip,
            askForOverwrite=True,
            title="Save GUI")

    def excSave(self):
        """Used when the application crashes to save the current project."""
        tmpPath = os.path.join(tempfile.gettempdir(), "DGDExceptionSave.gui")
        self.__executeSave(tmpPath)
        logging.info("Wrote crash session file to {}".format(tmpPath))

    def autoSave(self, fileName=""):
        """Used to occasionally save the current project."""
        if fileName == "":
            fileName = os.path.join(tempfile.gettempdir(), "DGDAutosave.gui")
        self.__executeSave(fileName)
        logging.info("Wrote autosave file to {}".format(fileName))

    def save(self, doSave):
        """Used when saving manually (via the file browser)."""
        if doSave:
            path = self.browser.get()
            path = os.path.expanduser(path)
            path = os.path.expandvars(path)
            self.__executeSave(path)
            base.messenger.send("setLastPath", [path])
        self.browser.destroy()
        del self.browser

    def __executeSave(self, path):
        """Actually save the project to 'path'."""
        jsonTools = JSONTools()
        jsonElements = jsonTools.getProjectJSON(
            self.guiElementsDict,
            self.getEditorFrame,
            self.getEditorRootCanvas,
            self.getAllEditorPlacers,
            self.allWidgetDefinitions,
            self.usePixel2D)
        with open(path, 'w') as outfile:
            json.dump(jsonElements, outfile, indent=2)

        if not self.isAutosave:
            base.messenger.send("clearDirtyFlag")

