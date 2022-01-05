#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

import os
import logging
from panda3d.core import ConfigVariableBool
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectDialog import YesNoDialog

from DirectGuiDesigner.dialogs.PathSelect import PathSelect
from DirectGuiDesigner.tools.JSONTools import JSONTools

class ExporterPy:
    functionMapping = {
        "base":{"initialText":"get"},
        "text":{"align":"align", "scale":"scale", "pos":"pos", "fg":"fg", "bg":"bg"}}

    # list of control names starting with the following will be ignored
    ignoreControls = ["item", "cancelframe", "popupMarker", "popupMenu"]
    # list of control names staritng with the following will always be included
    explIncludeControls = ["itemFrame"]

    def __init__(self, saveFile, guiElementsDict, customWidgetHandler, getEditorFrame, getAllEditorPlacers, tooltip, usePixel2D):
        self.guiElementsDict = guiElementsDict
        self.customWidgetHandler = customWidgetHandler

        jsonTools = JSONTools()
        self.jsonFileContent = jsonTools.getProjectJSON(self.guiElementsDict, getEditorFrame, getAllEditorPlacers, usePixel2D)
        self.jsonElements = self.jsonFileContent["ComponentList"]

        self.createdParents = ["root"]
        self.postponedElements = {}
        self.postSetupCalling = []
        self.radiobuttonDict = {}
        self.customWidgetAddDict = {}

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

        self.content = """#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file was created using the DirectGUI Designer

from direct.gui import DirectGuiGlobals as DGG
"""
        usedImports = []
        for name, elementInfo in self.guiElementsDict.items():
            if elementInfo.type not in usedImports:
                if elementInfo.type in importStatements:
                    self.content = "{}\n{}".format(self.content, importStatements[elementInfo.type])
                else:
                    self.content = "{}\n{}".format(self.content, elementInfo.customImportPath)
                usedImports.append(elementInfo.type)
        self.content += """
from panda3d.core import (
    LPoint3f,
    LVecBase3f,
    LVecBase4f,
    TextNode
)"""

        self.content += """

class GUI:
    def __init__(self, rootParent=None):
        """

        #self.__createStructuredElements("root", visualEditor.getCanvas())

        for name, elementInfo in self.jsonElements.items():
            self.content += self.__createElement(name, elementInfo)


        self.content += "\n"
        for line in self.postSetupCalling:
            self.content += line + "\n"

        for radioButton, others in self.radiobuttonDict.items():
            self.content += " "*8 + "{}.setOthers([".format(radioButton)
            for other in others:
                self.content += other + ","
            self.content += "])\n"

        topLevelItems = []
        for name, elementInfo in self.jsonElements.items():
            widget = self.customWidgetHandler.getWidget(elementInfo["type"])
            if widget is not None:
                if name not in self.customWidgetAddDict: continue
                for element in self.customWidgetAddDict[name]:
                    if widget.addItemFunction is not None:
                        self.content += " "*8 + "self.{}.{}({})\n".format(name, widget.addItemFunction, element)

            if elementInfo["parent"] == "root" or elementInfo["parent"].startswith("a2d"):
                topLevelItems.append(name)

        # Create helper functions for toplevel elements
        if len(topLevelItems) > 0:
            self.content += "\n"
            self.content += " "*4 + "def show(self):\n"
            for name in topLevelItems:
                self.content += " "*8 + "self.{}.show()\n".format(name)

            self.content += "\n"
            self.content += " "*4 + "def hide(self):\n"
            for name in topLevelItems:
                self.content += " "*8 + "self.{}.hide()\n".format(name)

            self.content += "\n"
            self.content += " "*4 + "def destroy(self):\n"
            for name in topLevelItems:
                self.content += " "*8 + "self.{}.destroy()\n".format(name)

        # Make script executable if desired
        if ConfigVariableBool("create-executable-scripts", False).getValue():
            self.content += """
# We need a showbase instance to make this script directly runnable
from direct.showbase.ShowBase import ShowBase
app = ShowBase()\n"""
            if usePixel2D:
                self.content += "GUI(app.pixel2d)\n"
            else:
                self.content += "GUI()\n"
            self.content += "app.run()\n"

        self.dlgPathSelect = PathSelect(
            self.save, "Save Python File", "Save file path", "Save", saveFile, tooltip)

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
        with open(path, 'w') as outfile:
            outfile.write(self.content)

    def __createElement(self, name, elementInfo):
        extraOptions = ""
        for optionName, optionValue in elementInfo["extraOptions"].items():
            v = optionValue
            if type(v) is list:
                v = f"[{','.join(map(str, v))}]"
            extraOptions += " "*12 + "{}={},\n".format(optionName, v)
        elementCode = """
        self.{} = {}(
{}{}        )\n""".format(
            name,
            elementInfo["type"],
            self.__writeElementOptions(name, elementInfo),
            #" "*12 + "command={},\n".format(elementInfo["command"]) if elementInfo["command"] is not None else "",
            #"BLUBB",
            #" "*12 + "extraArgs=[{}],\n".format(",".join(map(str, elementInfo["extraArgs"]))) if elementInfo["extraArgs"] is not None else "",
            extraOptions,
            )
        if elementInfo["element"]["transparency"] != "M_none":
            elementCode += " "*8 +"self.{}.setTransparency({})\n"   .format(name, elementInfo["element"]["transparency"])

        if elementInfo["type"] == "DirectScrolledListItem":
            self.postSetupCalling.append(" "*8 + "self.{}.addItem(self.{})".format(elementInfo["parent"], name))

        return elementCode

    def __writeElementOptions(self, name, elementInfo):
        elementOptions = ""
        indent = " "*12

        for optionKey, optionValue in elementInfo["element"].items():
            if optionKey == "others":
                others = []
                for other in optionValue:
                    others.append("self.{}".format(other))
                self.radiobuttonDict["self.{}".format(name)] = others
                continue
            elif optionKey == "transparency":
                continue

            elementOptions += indent + optionKey + "=" + optionValue + ",\n"

        if elementInfo["parent"] != "root":
            self.canvasParents = [
                "a2dTopCenter","a2dBottomCenter","a2dLeftCenter","a2dRightCenter",
                "a2dTopLeft","a2dTopRight","a2dBottomLeft","a2dBottomRight"]

            if elementInfo["parent"] in self.jsonElements and self.jsonElements[elementInfo["parent"]]["type"] == "DirectScrollFrame":
                # use the canvas as parent
                elementOptions += indent + "parent=self." + elementInfo["parent"] + ".getCanvas(),\n"
            elif elementInfo["parent"] in self.jsonElements and self.customWidgetHandler.getWidget(self.jsonElements[elementInfo["parent"]]["type"]) is not None:
                widget = self.customWidgetHandler.getWidget(self.jsonElements[elementInfo["parent"]]["type"])
                if widget.addItemFunction is not None:
                    if elementInfo["parent"] in self.customWidgetAddDict:
                        self.customWidgetAddDict[elementInfo["parent"]].append("self.{}".format(name))
                    else:
                        self.customWidgetAddDict[elementInfo["parent"]] = ["self.{}".format(name)]
            elif elementInfo["parent"] in self.canvasParents:
                elementOptions += indent + "parent=base." + elementInfo["parent"] + ",\n"
            else:
                elementOptions += indent + "parent=self." + elementInfo["parent"] + ",\n"
        else:
            # use the parent passed to the class
            elementOptions += indent + "parent=rootParent,\n"

        return elementOptions
