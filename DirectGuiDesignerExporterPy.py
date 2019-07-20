#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

import os
import logging
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectDialog import YesNoDialog

from DirectGuiDesignerPathSelect import DirectGuiDesignerPathSelect

class DirectGuiDesignerExporterPy:
    functionMapping = {
        "base":{"initialText":"get"},
        "text":{"align":"align", "scale":"scale", "pos":"pos", "fg":"fg", "bg":"bg"}}

    ignoreRepr = ["command"]

    # list of control names starting with the following will be ignored
    ignoreControls = ["indicator", "item", "cancelframe", "popupMarker", "popupMenu"]
    # list of control names staritng with the following will always be included
    explIncludeControls = ["itemFrame"]

    explIncludeOptions = ["forceHeight", "numItemsVisible"]

    def __init__(self, guiElementsDict, visualEditor, tooltip):
        self.guiElementsDict = guiElementsDict

        self.createdParents = ["root"]
        self.postponedElements = {}
        self.visualEditor = visualEditor
        self.preSetupCalling = []
        self.radiobuttonDict = {}

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
            if elementInfo.type not in usedImports:
                self.content = "{}\n{}".format(self.content, importStatements[elementInfo.type])
                usedImports.append(elementInfo.type)
        self.content = """
{}
from panda3d.core import (
    LPoint3f,
    LVecBase3f,
    LVecBase4f
)

# Uncomment this line and the lines at the bottom to run this file directly
from direct.showbase.ShowBase import ShowBase

class GUI:
    def __init__(self, rootParent=None):
        """.format(self.content)

        self.__createStructuredElements("root", visualEditor.getCanvas())

        self.content += "\n"
        for line in self.preSetupCalling:
            self.content += line + "\n"

        for radioButton, others in self.radiobuttonDict.items():
            self.content += " "*8 + "{}.setOthers([".format(radioButton)
            for other in others:
                self.content += other + ","
            self.content += "])\n"
        self.content += """
# Uncomment these lines and the showbase import line at the top to run this file directly
app = ShowBase()
GUI()
app.run()"""

        self.dlgPathSelect = DirectGuiDesignerPathSelect(
            self.save, "Save Python File", "Save file path", "Save", "~/export.py", tooltip)

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
        self.dlgPathSelect.destroy()
        del self.dlgPathSelect

    def __executeSave(self, overwrite, path):
        if self.dlgOverwrite is not None: self.dlgOverwrite.destroy()
        if self.dlgOverwriteShadow is not None: self.dlgOverwriteShadow.destroy()
        if not overwrite: return
        with open(path, 'w') as outfile:
            outfile.write(self.content)

    def __createStructuredElements(self, rootName, root, ignoreChildren=False):
        elementInfo = None
        if root != self.visualEditor.getCanvas():
            name = ""
            if rootName in self.guiElementsDict.keys():
                elementInfo = self.guiElementsDict[rootName]
                name = rootName
            elif len(rootName.split("-")) > 1 and rootName.split("-")[1] in self.guiElementsDict.keys():
                elementInfo = self.guiElementsDict[rootName.split("-")[1]]
                name = rootName.split("-")[1]
            if elementInfo is not None:
                postponed = False
                if len(elementInfo.createAfter) > 0:
                    for afterElementInfo in elementInfo.createAfter:
                        if afterElementInfo.name not in self.createdParents:
                            self.postponedElements[elementInfo.name] = elementInfo
                            postponed = True
                if not postponed:
                    self.content += self.__createElement(elementInfo)
                    self.createdParents.append(elementInfo.name)

        if hasattr(root, "getChildren") and not ignoreChildren:
            for child in root.getChildren():
                self.__createStructuredElements(child.getName(), child)

        if elementInfo is not None and elementInfo.name in self.postponedElements.keys():
            del self.postponedElements[elementInfo.name]

        # check if we can create postponed elements
        for postponedElementInfoName, postponedElementInfo in self.postponedElements.copy().items():
            if postponedElementInfoName in self.createdParents: continue

            hasAll = True
            if len(postponedElementInfo.createAfter) > 0:
                for afterElementInfo in postponedElementInfo.createAfter:
                    if afterElementInfo.name not in self.createdParents:
                        hasAll = False

            if hasAll:
                self.__createStructuredElements(postponedElementInfo.element.getName(), postponedElementInfo.element, True)

    def __createElement(self, elementInfo):
        extraOptions = ""
        for optionName, optionValue in elementInfo.extraOptions.items():
            extraOptions += " "*12 + "{}={},\n".format(optionName, optionValue)
        elementCode = """
        self.{} = {}(
{}{}{}{}        )\n""".format(
            elementInfo.name,
            elementInfo.type,
            self.__writeElementOptions(elementInfo),
            " "*12 + "command={},\n".format(elementInfo.command) if elementInfo.command is not None else "",
            " "*12 + "extraArgs=[{}],\n".format(elementInfo.extraArgs) if elementInfo.extraArgs is not None else "",
            extraOptions,
            )

        if elementInfo.type == "DirectScrolledListItem":
            self.preSetupCalling.append(" "*8 + "self.{}.addItem(self.{})".format(elementInfo.parent.name ,elementInfo.name))

        return elementCode

    def __getAllSubcomponents(self, componentName, component, componentPath):
        add = False
        for incl in self.explIncludeControls:
            if componentName.startswith(incl): add = True
        if not add:
            for item in self.ignoreControls:
                if componentName.startswith(item): return
        if componentPath == "":
            componentPath = componentName
        else:
            componentPath += "_" + componentName
        self.componentsList[component] = componentPath
        if not hasattr(component, "components"): return
        for subcomponentName in component.components():
            self.__getAllSubcomponents(subcomponentName, component.component(subcomponentName), componentPath)

    def __writeElementOptions(self, elementInfo):
        element = elementInfo.element
        elementOptions = ""
        indent = " "*12

        self.componentsList = {element:""}
        for subcomponentName in element.components():
            self.__getAllSubcomponents(subcomponentName, element.component(subcomponentName), "")

        if elementInfo.type == "DirectOptionMenu":
            elementOptions += indent + "items=['item1'],\n"

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
                            elementOptions += indent + name + option + "=" + reprFunc(getattr(element, value)()) + ",\n"
                        else:
                            elementOptions += indent + name + option + "=" + reprFunc(getattr(element, value)) + ",\n"

            if not hasattr(element, "options"): continue

            for option in element.options():
                if option[DGG._OPT_DEFAULT] == "parent":
                    continue

                if option[DGG._OPT_DEFAULT] == "others":
                    elementNameDict = {}
                    others = []
                    for key, value in self.guiElementsDict.items():
                        elementNameDict[value.element] = value.name
                    for otherElement in option[DGG._OPT_VALUE]:
                        if otherElement in elementNameDict:
                            others.append("self.{}".format(elementNameDict[otherElement]))
                    self.radiobuttonDict["self.{}".format(elementInfo.name)] = others
                    continue

                elif not option[DGG._OPT_FUNCTION]:
                    if option[DGG._OPT_VALUE] != element[option[DGG._OPT_DEFAULT]] or option[DGG._OPT_DEFAULT] in self.explIncludeOptions:
                        elementOptions += indent + name + option[DGG._OPT_DEFAULT] + "=" + reprFunc(element[option[DGG._OPT_DEFAULT]]) + ",\n"
                else:
                    funcName = "get{}{}".format(option[DGG._OPT_DEFAULT][0].upper(), option[DGG._OPT_DEFAULT][1:])
                    propName = "{}".format(option[DGG._OPT_DEFAULT])
                    if hasattr(element, funcName):
                        if funcName == "getColor":
                            # Savety check. I currently only know of this function that isn't set by default
                            if not element.hasColor(): continue
                        value = getattr(element, funcName)()
                        if option[DGG._OPT_VALUE] != value:
                            elementOptions += indent + name + option[0] + "=" + reprFunc(value) + ",\n"
                    elif hasattr(element, propName):
                        if not callable(type(getattr(element, propName))):
                            # TODO: Check if we ever get here at al
                            value = getattr(element, propName)
                            if option[DGG._OPT_VALUE] != value:
                                elementOptions += indent + name + option[0] + "=" + reprFunc(value) + ",\n"
                    elif option[DGG._OPT_DEFAULT] in self.functionMapping["base"]:
                        funcName = self.functionMapping["base"][option[DGG._OPT_DEFAULT]]
                        if hasattr(element, funcName):
                            value = getattr(element, funcName)()
                            if option[DGG._OPT_VALUE] != value:
                                elementOptions += indent + name + option[0] + "=" + reprFunc(value) + ",\n"
                        else:
                            logging.error("Can't call: " + option[DGG._OPT_DEFAULT])
                    else:
                        try:
                            if option[DGG._OPT_VALUE] != element[option[DGG._OPT_DEFAULT]]:
                                elementOptions += indent + name + option[DGG._OPT_DEFAULT] + "=" + reprFunc(element[option[DGG._OPT_VALUE]]) + ",\n"
                        except:
                            logging.error("Can't write: " + option[DGG._OPT_DEFAULT])

            if elementInfo.parent is not None and name == "":
                if elementInfo.parent.type == "DirectScrollFrame":
                    # use the canvas as parent
                    elementOptions += indent + "parent=self." + elementInfo.parent.name + ".getCanvas(),\n"
                else:
                    elementOptions += indent + "parent=self." + elementInfo.parent.name + ",\n"
            elif name == "":
                # use the parent passed to the class
                elementOptions += indent + "parent=rootParent,\n"

        return elementOptions
