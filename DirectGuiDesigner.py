#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import platform
import logging
from logging.handlers import TimedRotatingFileHandler
import tempfile

from direct.showbase.ShowBase import ShowBase

from panda3d.core import (
    Point3,
    Vec3,
    Filename,
    loadPrcFile,
    loadPrcFileData,
    WindowProperties,
    ConfigVariableBool,
    ConfigVariableString,
    ConfigVariableSearchPath,
    TextNode,
    TextProperties,
    TextPropertiesManager
)

from direct.gui import DirectGuiGlobals as DGG

from direct.gui.DirectFrame import DirectFrame
#from direct.gui.DirectScrolledFrame import DirectScrolledFrame
from directGuiOverrides.DirectScrolledFrame import DirectScrolledFrame
from direct.gui.DirectDialog import OkDialog
from direct.gui.DirectDialog import OkCancelDialog

from direct.directtools.DirectGrid import DirectGrid
from direct.directtools.DirectUtil import ROUND_TO

from DirectGuiDesignerEditorCanvas import DirectGuiDesignerEditorCanvas
from DirectGuiDesignerElementHandler import DirectGuiDesignerElementHandler
from DirectGuiDesignerElementHandler import ElementInfo
from DirectGuiDesignerMenuBar import DirectGuiDesignerMenuBar
from DirectGuiDesignerToolbox import DirectGuiDesignerToolbox
from DirectGuiDesignerProperties import DirectGuiDesignerProperties
from DirectGuiDesignerStructure import DirectGuiDesignerStructure
from DirectGuiDesignerExporterPy import DirectGuiDesignerExporterPy
from DirectGuiDesignerExporterProject import DirectGuiDesignerExporterProject
from DirectGuiDesignerLoaderProject import DirectGuiDesignerLoaderProject
from DirectGuiDesignerLoaderPy import DirectGuiDesignerLoaderPy
from DirectGuiDesignerSettings import GUI as DirectGuiDesignerSettings
from DirectGuiDesignerCustomWidgets import DirectGuiDesignerCustomWidgets

from DirectFolderBrowser.DirectFolderBrowser import DirectFolderBrowser

from DirectGuiDesignerTooltip import Tooltip


loadPrcFileData(
    "",
    """
    textures-power-2 none
    window-title DirectGUI Designer
    #show-frame-rate-meter #t
    #want-pstats #t
    maximized #t
    """)

# check if we have a config file
home = os.path.expanduser("~")
basePath = os.path.join(home, ".DirectGuiDesigner")
if not os.path.exists(basePath):
    os.makedirs(basePath)
logPath = os.path.join(basePath, "logs")
if not os.path.exists(logPath):
    os.makedirs(logPath)


# START Move old config and log files to the new folders
# NOTE: This should be removed in a later version
import shutil
oldConfig = os.path.join(home, ".DirectGuiDesigner.prc")
if os.path.exists(oldConfig):
    shutil.move(oldConfig, os.path.join(basePath, ".DirectGuiDesigner.prc"))
logfiles = []
for f in os.listdir(home):
    if os.path.isfile(os.path.join(home, f)) and f.startswith("DirectGuiDesigner.log"):
        logfiles.append(f)
for f in logfiles:
    shutil.move(os.path.join(home, f), os.path.join(logPath, f))
# END Move old files


logfile = os.path.join(logPath, "DirectGuiDesigner.log")
handler = TimedRotatingFileHandler(logfile)
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[handler])
prcFileName = os.path.join(basePath, ".DirectGuiDesigner.prc")
if os.path.exists(prcFileName):
    loadPrcFile(Filename.fromOsSpecific(prcFileName))

    # make sure to load our custom paths
    pathsConfig = ConfigVariableSearchPath("custom-model-path", "").getValue()
    for path in pathsConfig.getDirectories():
        line = "model-path {}".format(str(path))
        print(str(path))
        loadPrcFileData("", line)
else:
    with open(prcFileName, "w") as prcFile:
        prcFile.write("skip-ask-for-quit #f\n")
        prcFile.write("create-executable-scripts #f\n")
        prcFile.write("show-toolbar #t\n")

    #if platform.system() == "Windows":
    #    from ctypes import WinDLL
    #    from stat import FILE_ATTRIBUTE_HIDDEN
    #    from os import stat

    #    # Change the current files attributes to contain the "hidden" attribute
    #    kernel32 = WinDLL("kernel32")
    #    attrs = stat(prcFileName).st_file_attributes
    #    attrs = attrs | FILE_ATTRIBUTE_HIDDEN
    #    kernel32.SetFileAttributesW(prcFileName, attrs)


class DirectGuiDesigner(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        logging.debug("Start Designer")

        self.dirty = False

        self.lastDirPath = ConfigVariableString("work-dir-path", "~").getValue()
        self.lastFileNameWOExtension = "export"

        wp = WindowProperties()
        if platform.system() == "Windows":
            wp.setIconFilename("icons/DirectGuiDesigner.ico")
        else:
            wp.setIconFilename("icons/DirectGuiDesigner64.png")
        base.win.requestProperties(wp)

        self.selectedElement = None
        # dict of all elements in the visual editor
        # Key = guiID; Value = elementInfo
        self.elementDict = {}

        map = base.win.get_keyboard_map()

        self.is_down = base.mouseWatcherNode.is_button_down
        self.key_lcontrol = map.get_mapped_button("lcontrol")
        self.key_rcontrol = map.get_mapped_button("rcontrol")
        self.key_lshift = map.get_mapped_button("lshift")
        self.key_rshift = map.get_mapped_button("rshift")

        self.dlgHelp = None
        self.dlgHelpShadow = None

        self.dlgSettings = None
        self.dlgSettingsShadow = None

        self.dlgQuit = None
        self.dlgQuitShadow = None

        self.dlgWarning = None
        self.dlgWarningShadow = None

        self.dlgInfo = None
        self.dlgInfoShadow = None

        self.dlgNewProject = None
        self.dlgNewProjectShadow = None

        self.openDialogCloseFunctions = []

        self.copyOptionsElement = None

        # Delay initial setup by 0.5s to let the window set it's final
        # size and we'll be able to use the screen corner/edge variables
        taskMgr.doMethodLater(0.5, self.setupGui, "delayed setup", extraArgs = [])

    def setupGui(self):
        logging.debug("Setup GUI")
        self.screenWidth = abs(base.a2dRight) + abs(base.a2dLeft)
        self.screenWidthPx = base.getSize()[0]
        self.screenHeightPx = base.getSize()[1]
        self.leftEdge = -(self.screenWidth * (2.0 / 3.0))
        self.rightEdge = self.screenWidth * (1.0 / 3.0)

        self.tt = Tooltip()

        # 3/4 wide editor content frame
        self.editorFrame = DirectGuiDesignerEditorCanvas()
        self.visualEditorInfo = ElementInfo(self.editorFrame.visualEditor, "Editor")

        self.menuBar = DirectGuiDesignerMenuBar(self.tt, self.editorFrame.grid)
        self.toolbarHeight = 24

        # 1/4 wide toolbox, properties and structure frame
        self.toolsFrame = DirectFrame(
            frameColor=(0.25, 0.25, 0.25, 1),
            frameSize=(0, self.screenWidthPx/4, -self.screenHeightPx, -self.toolbarHeight),
            pos=(self.screenWidth/8,0,0),
            parent=base.pixel2d)

        self.toolFrameHeight = -self.screenHeightPx / 3 + (self.toolbarHeight/3)

        self.nextToolFrameY = -self.toolbarHeight

        self.toolboxFrame = DirectGuiDesignerToolbox(self.toolsFrame, self.nextToolFrameY, self.toolFrameHeight)
        self.nextToolFrameY += self.toolFrameHeight

        self.propertiesFrame = DirectGuiDesignerProperties(self.toolsFrame, self.nextToolFrameY, self.toolFrameHeight, self.getEditorRootCanvas, self.getEditorPlacer, self.tt)
        self.propertiesEditor(self.visualEditorInfo)
        self.nextToolFrameY += self.toolFrameHeight

        self.structureFrame = DirectGuiDesignerStructure(self.toolsFrame, self.nextToolFrameY, self.toolFrameHeight, self.getEditorRootCanvas, self.elementDict, self.selectedElement)

        self.elementHandler = DirectGuiDesignerElementHandler(self.propertiesFrame, self.getEditorRootCanvas)
        self.editorFrame.setElementHandler(self.elementHandler)

        self.customWidgetsHandler = DirectGuiDesignerCustomWidgets(self.toolboxFrame, self.elementHandler)

        self.registerKeyboardEvents()
        self.accept("unregisterKeyboardEvents", self.ignoreKeyboardEvents)
        self.accept("reregisterKeyboardEvents", self.registerKeyboardEvents)

        self.accept("createControl", self.__createControl)
        self.accept("newProject", self.new)
        self.accept("saveProject", self.save)
        self.accept("exportProject", self.export)
        self.accept("loadProject", self.load)
        self.accept("updateElementDict-afterLoad", self.updateElementDict)
        self.accept("refreshStructureTree", self.__refreshStructureTree)
        self.accept("selectElement", self.selectElement)
        self.accept("removeElement", self.removeElement)
        self.accept("copyOptions", self.copyOptions)
        self.accept("pasteOptions", self.pasteOptions)
        self.accept("copyElement", self.copyElement)
        self.accept("pasteElement", self.pasteElement)
        self.accept("toggleElementVisibility", self.toggleElementVisibility)
        self.accept("setParentOfElement", self.setParentOfElement)
        self.accept("toggleGrid", self.editorFrame.toggleGrid)
        self.accept("toggleVisualEditorParent", self.editorFrame.toggleVisualEditorParent)
        self.accept("setVisualEditorParent", self.editorFrame.setVisualEditorParent)
        self.accept("setVisualEditorCanvasSize", self.editorFrame.setVisualEditorCanvasSize)
        self.accept("showHelp", self.showHelp)
        self.accept("quitApp", self.quitApp)
        self.accept("showSettings", self.showSettings)
        self.accept("Settings_OK", self.hideSettings, [True])
        self.accept("Settings_CANCEL", self.hideSettings, [False])

        self.accept("setDirtyFlag", self.setDirty)
        self.accept("clearDirtyFlag", self.setClean)

        self.accept("setName", self.setName)
        self.accept("setCommand", self.setCommand)
        self.accept("setExtraArgs", self.setExtraArgs)

        self.accept("dragStart", self.dragStart)
        self.accept("dragStop", self.dragStop)

        self.accept("showWarning", self.showWarning)
        self.accept("showInfo", self.showInfo)

        self.screenSize = base.getSize()
        self.accept("window-event", self.windowEventHandler)

        self.accept("setLastPath", self.setLastPath)

        sys.excepthook = self.excHandler

        self.win.setCloseRequestEvent("quitApp")

        # Load user custom widgets
        self.customWidgetsHandler.loadCustomWidgets()

        tmpPath = os.path.join(tempfile.gettempdir(), "DGDExceptionSave.json")
        if os.path.exists(tmpPath):
            logging.info("Loading crash session file {}".format(tmpPath))
            projectLoader = DirectGuiDesignerLoaderProject(tmpPath, self.visualEditorInfo, self.elementHandler, self.customWidgetsHandler, self.getEditorPlacer, True)
            self.elementDict = projectLoader.get()
            base.messenger.send("refreshStructureTree")
            base.messenger.send("setDirtyFlag")
            base.messenger.send("showInfo", ["Loaded previously crashed session!"])
            os.remove(tmpPath)
            logging.info("Removed crash session file")
        logging.debug("Startup complete")

    def setDirty(self):
        wp = WindowProperties()
        wp.setTitle("*DirectGUI Designer")
        base.win.requestProperties(wp)

        self.dirty = True

    def setClean(self):
        wp = WindowProperties()
        wp.setTitle("DirectGUI Designer")
        base.win.requestProperties(wp)

        self.dirty = False

    def setLastPath(self, path):
        self.lastDirPath = os.path.dirname(path)
        fn = os.path.splitext(os.path.basename(path))[0]
        if fn != "":
            self.lastFileNameWOExtension = os.path.splitext(os.path.basename(path))[0]

    def getEditorRootCanvas(self):
        return self.editorFrame.visualEditor.getCanvas()

    def getEditorPlacer(self, placerName):
        return self.editorFrame.getEditorPlacer(placerName)

    def getEditorFrame(self):
        return self.editorFrame.visualEditor

    def excHandler(self, ex_type, ex_value, ex_traceback):
        logging.error("Unhandled exception", exc_info=(ex_type, ex_value, ex_traceback))
        print("Try to save file after unhandled exception. Please restart the app to automatically load the exception save file!")

        DirectGuiDesignerExporterProject("", self.elementDict, self.getEditorFrame, not self.editorFrame.visEditorInAspect2D, exceptionSave=True)

    def inteligentEscape(self):
        dlgList = [self.dlgHelp, self.dlgSettings, self.dlgQuit, self.dlgWarning, self.dlgInfo, self.dlgNewProject]
        if not all(dlg is None for dlg in dlgList):
            self.openDialogCloseFunctions[-1](None)
        else:
            self.selectElement(self.visualEditorInfo, None)

    def registerKeyboardEvents(self):
        self.accept("escape", self.inteligentEscape)
        self.accept("mouse3", self.selectElement, extraArgs=[self.visualEditorInfo, None])
        self.accept("mouse2", self.editorFrame.dragEditorFrame, extraArgs=[True])
        self.accept("mouse2-up", self.editorFrame.dragEditorFrame, extraArgs=[False])
        self.accept("wheel_up", self.editorFrame.zoom, extraArgs=[.1])
        self.accept("wheel_down", self.editorFrame.zoom, extraArgs=[-.1])

        self.accept("control-n", self.new)
        self.accept("control-s", self.save)
        self.accept("control-e", self.export)
        self.accept("control-o", self.load)
        self.accept("control-q", self.quitApp)
        self.accept("control-c", self.copyElement)
        self.accept("control-v", self.pasteElement)
        self.accept("shift-control-c", self.copyOptions)
        self.accept("shift-control-v", self.pasteOptions)
        self.accept("delete", self.removeElement)
        self.accept("control-g", self.menuBar.cb_grid.commandFunc, extraArgs=[None])
        self.accept("control-h", self.toggleElementVisibility)
        self.accept("f1", self.showHelp)

        self.accept("arrow_left", self.moveElement, extraArgs=["left"])
        self.accept("arrow_right", self.moveElement, extraArgs=["right"])
        self.accept("arrow_up", self.moveElement, extraArgs=["up"])
        self.accept("arrow_down", self.moveElement, extraArgs=["down"])

        self.accept("arrow_left-repeat", self.moveElement, extraArgs=["left"])
        self.accept("arrow_right-repeat", self.moveElement, extraArgs=["right"])
        self.accept("arrow_up-repeat", self.moveElement, extraArgs=["up"])
        self.accept("arrow_down-repeat", self.moveElement, extraArgs=["down"])

        speedUp = 5
        self.accept("shift-arrow_left", self.moveElement, extraArgs=["left", speedUp])
        self.accept("shift-arrow_right", self.moveElement, extraArgs=["right", speedUp])
        self.accept("shift-arrow_up", self.moveElement, extraArgs=["up", speedUp])
        self.accept("shift-arrow_down", self.moveElement, extraArgs=["down", speedUp])

        self.accept("shift-arrow_left-repeat", self.moveElement, extraArgs=["left", speedUp])
        self.accept("shift-arrow_right-repeat", self.moveElement, extraArgs=["right", speedUp])
        self.accept("shift-arrow_up-repeat", self.moveElement, extraArgs=["up", speedUp])
        self.accept("shift-arrow_down-repeat", self.moveElement, extraArgs=["down", speedUp])

        speedDown = 0.5
        self.accept("control-arrow_left", self.moveElement, extraArgs=["left", speedDown])
        self.accept("control-arrow_right", self.moveElement, extraArgs=["right", speedDown])
        self.accept("control-arrow_up", self.moveElement, extraArgs=["up", speedDown])
        self.accept("control-arrow_down", self.moveElement, extraArgs=["down", speedDown])

        self.accept("control-arrow_left-repeat", self.moveElement, extraArgs=["left", speedDown])
        self.accept("control-arrow_right-repeat", self.moveElement, extraArgs=["right", speedDown])
        self.accept("control-arrow_up-repeat", self.moveElement, extraArgs=["up", speedDown])
        self.accept("control-arrow_down-repeat", self.moveElement, extraArgs=["down", speedDown])

    def ignoreKeyboardEvents(self):
        self.ignore("control-n")
        self.ignore("control-s")
        self.ignore("control-e")
        self.ignore("control-o")
        self.ignore("control-q")
        self.ignore("control-c")
        self.ignore("control-v")
        self.ignore("shift-control-c")
        self.ignore("shift-control-v")
        self.ignore("delete")
        self.ignore("control-g")
        self.ignore("control-h")
        self.ignore("f1")

        self.ignore("arrow_left")
        self.ignore("arrow_right")
        self.ignore("arrow_up")
        self.ignore("arrow_down")

        self.ignore("arrow_left-repeat")
        self.ignore("arrow_right-repeat")
        self.ignore("arrow_up-repeat")
        self.ignore("arrow_down-repeat")

        self.ignore("shift-arrow_left")
        self.ignore("shift-arrow_right")
        self.ignore("shift-arrow_up")
        self.ignore("shift-arrow_down")

        self.ignore("shift-arrow_left-repeat")
        self.ignore("shift-arrow_right-repeat")
        self.ignore("shift-arrow_up-repeat")
        self.ignore("shift-arrow_down-repeat")

        self.ignore("control-arrow_left")
        self.ignore("control-arrow_right")
        self.ignore("control-arrow_up")
        self.ignore("control-arrow_down")

        self.ignore("control-arrow_left-repeat")
        self.ignore("control-arrow_right-repeat")
        self.ignore("control-arrow_up-repeat")
        self.ignore("control-arrow_down-repeat")

    def windowEventHandler(self, window=None):
        # call showBase windowEvent which would otherwise get overridden and breaking the app
        self.windowEvent(window)

        if window != self.win:
            # This event isn't about our window.
            return

        if window is not None: # window is none if panda3d is not started
            if self.screenSize == base.getSize():
                return
            self.screenSize = base.getSize()
            self.screenWidth = abs(base.a2dRight) + abs(base.a2dLeft)
            self.screenWidthPx = base.getSize()[0]
            self.screenHeightPx = base.getSize()[1]
            self.toolsFrame["frameSize"] = (0, self.screenWidthPx/4, -self.screenHeightPx, -self.toolbarHeight)

            # Resize all editor frames
            self.editorFrame.resizeFrame()
            self.menuBar.resizeFrame()
            self.toolFrameHeight = -self.screenHeightPx / 3 + (self.toolbarHeight / 3)
            self.nextToolFrameY = -self.toolbarHeight
            self.toolboxFrame.resizeFrame(self.nextToolFrameY, self.toolFrameHeight)
            self.nextToolFrameY += self.toolFrameHeight
            self.propertiesFrame.resizeFrame(self.nextToolFrameY, self.toolFrameHeight)
            self.nextToolFrameY += self.toolFrameHeight
            self.structureFrame.resizeFrame(self.nextToolFrameY, self.toolFrameHeight)

            # Reposition dialogs and resize thier shadows
            for dialog in [self.dlgHelp, self.dlgSettings, self.dlgQuit, self.dlgWarning, self.dlgInfo, self.dlgNewProject]:
                if dialog is not None:
                    dialog.setPos(base.getSize()[0]//2, 0, -base.getSize()[1]//2)

            for shadow in [self.dlgHelpShadow, self.dlgSettingsShadow, self.dlgQuitShadow, self.dlgWarningShadow, self.dlgInfoShadow, self.dlgNewProjectShadow]:
                if shadow is not None:
                    shadow["frameSize"] = (0, base.getSize()[0], -base.getSize()[1], 0)

    def propertiesEditor(self, elementInfo):
        self.propertiesFrame.clearPropertySelection()
        self.propertiesFrame.propertyList["frameColor"] = True
        self.propertiesFrame.propertyList["canvasSize"] = True
        self.propertiesFrame.setupProperties("Editor Properties", elementInfo, self.elementDict)

    def __refreshStructureTree(self):
        self.structureFrame.refreshStructureTree(self.elementDict, self.selectedElement)

    def __createControl(self, element):
        funcName = "create{}".format(element)
        parent = None
        elementInfo = None
        widget = self.customWidgetsHandler.getWidget(element)
        if self.selectedElement is not None:
            parent = self.selectedElement.element
        if hasattr(self.elementHandler, funcName):
            if widget is None:
                elementInfo = getattr(self.elementHandler, funcName)(parent)
            else:
                elementInfo = getattr(self.elementHandler, funcName)(widget, parent)
        else:
            logging.error("Undefined control: {}".format(element))
            return

        if elementInfo is None: return
        if type(elementInfo) is tuple:
            if self.selectedElement is not None and self.selectedElement.type == "DirectScrolledList":
                self.selectedElement.element.addItem(elementInfo[0].element)
            elif self.selectedElement is not None:
                widget = self.customWidgetsHandler.getWidget(self.selectedElement.type)
                if widget is not None:
                    if widget.addItemFunction is not None:
                        # call custom widget add function
                        getattr(self.selectedElement.element, widget.addItemFunction)(elementInfo[0].element)
            for entry in elementInfo:
                if self.selectedElement is not None and entry.parent is None:
                    entry.parent = self.selectedElement
                self.elementDict[entry.element.guiId] = entry
        else:
            if self.selectedElement is not None:
                elementInfo.parent = self.selectedElement
                if self.selectedElement.type == "DirectScrolledList":
                    self.selectedElement.element.addItem(elementInfo.element)
                widget = self.customWidgetsHandler.getWidget(self.selectedElement.type)
                if widget is not None:
                    if widget.addItemFunction is not None:
                        # call custom widget add function
                        getattr(self.selectedElement.element, widget.addItemFunction)(elementInfo.element)
            self.elementDict[elementInfo.element.guiId] = elementInfo
        base.messenger.send("refreshStructureTree")
        base.messenger.send("setDirtyFlag")

        return elementInfo

    def selectElement(self, elementInfo, args=None):
        if self.selectedElement is not None:
            self.selectedElement.element.clearColorScale()
            self.ignoreKeyboardEvents()
            self.registerKeyboardEvents()
        if elementInfo is None:
            base.messenger.send("showWarning", ["Element can't be selected"])
            return
        if elementInfo.element is self.editorFrame.visualEditor:
            # we don't need to select the editor itself
            self.selectedElement = None
            self.refreshProperties(elementInfo)
            base.messenger.send("refreshStructureTree")
            return
        if elementInfo.element is None:
            return
        self.selectedElement = elementInfo
        elementInfo.element.setColorScale(1,1,0,1)
        self.refreshProperties(elementInfo)
        base.messenger.send("refreshStructureTree")

    def refreshProperties(self, elementInfo):
        self.propertiesFrame.clear()
        propFuncName = "properties{}".format(elementInfo.type)
        try:
            widget = self.customWidgetsHandler.getWidget(elementInfo.type)
            if elementInfo.type == "Editor":
                getattr(self, propFuncName)(elementInfo)
            if hasattr(self.elementHandler, propFuncName):
                if widget is None:
                    getattr(self.elementHandler, propFuncName)(elementInfo, self.elementDict)
                else:
                    getattr(self.elementHandler, propFuncName)(elementInfo, self.elementDict, widget)
        except:
            e = sys.exc_info()[1]
            base.messenger.send("showWarning", [str(e)])
            logging.exception("Error while loading properties panel")

    def dragStart(self, elementInfo, event):
        self.selectElement(elementInfo, event)
        element = elementInfo.element
        taskMgr.remove("dragDropTask")
        parent = element.getParent()
        pos = element.getPos(parent)
        element.setPos(pos)
        vWidget2render2d = element.getPos(render2d)
        vMouse2render2d = Point3(event.getMouse()[0], 0, event.getMouse()[1])
        editVec = Vec3(vWidget2render2d - vMouse2render2d)
        t = taskMgr.add(self.dragTask, "dragDropTask")
        t.elementInfo = elementInfo
        t.editVec = editVec
        t.mouseVec = vMouse2render2d

    def dragTask(self, t):
        mwn = base.mouseWatcherNode
        if mwn.hasMouse():
            vMouse2render2d = Point3(mwn.getMouse()[0], 0, mwn.getMouse()[1])
            newPos = vMouse2render2d + t.editVec

            if self.editorFrame.snapToGrid and (t.mouseVec - vMouse2render2d).length() < 0.01:
                return t.cont

            oldPos = t.elementInfo.element.getPos()
            t.elementInfo.element.setPos(render2d, newPos)

            if self.editorFrame.snapToGrid:

                newPos = t.elementInfo.element.getPos()
                modifier = 0.5
                if self.is_down(self.key_lcontrol) or self.is_down(self.key_rcontrol):
                    modifier = 0.25
                if self.is_down(self.key_lshift) or self.is_down(self.key_rshift):
                    modifier = 1
                newPos.set(
                    ROUND_TO(newPos[0], self.editorFrame.grid.getGridSpacing()*modifier),
                    ROUND_TO(newPos[1], self.editorFrame.grid.getGridSpacing()*modifier),
                    ROUND_TO(newPos[2], self.editorFrame.grid.getGridSpacing()*modifier))
                t.elementInfo.element.setPos(newPos)

            # check if the item has actually moved
            if not self.dirty and oldPos != t.elementInfo.element.getPos():
                base.messenger.send("setDirtyFlag")

        return t.cont

    def dragStop(self, event):
        t = taskMgr.getTasksNamed("dragDropTask")[0]
        parent = t.elementInfo.element.getParent()
        pos = t.elementInfo.element.getPos(self.editorFrame.visualEditor.getCanvas())
        if pos.x < self.editorFrame.visualEditor["canvasSize"][0]:
            t.elementInfo.element.setX(self.editorFrame.visualEditor.getCanvas(), self.editorFrame.visualEditor["canvasSize"][0])
        if pos.x > self.editorFrame.visualEditor["canvasSize"][1]:
            t.elementInfo.element.setX(self.editorFrame.visualEditor.getCanvas(), self.editorFrame.visualEditor["canvasSize"][1])
        if pos.z < self.editorFrame.visualEditor["canvasSize"][2]:
            t.elementInfo.element.setZ(self.editorFrame.visualEditor.getCanvas(), self.editorFrame.visualEditor["canvasSize"][2])
        if pos.z > self.editorFrame.visualEditor["canvasSize"][3]:
            t.elementInfo.element.setZ(self.editorFrame.visualEditor.getCanvas(), self.editorFrame.visualEditor["canvasSize"][3])
        self.refreshProperties(t.elementInfo)
        taskMgr.remove("dragDropTask")

    def moveElement(self, direction, speedMult=1):
        if self.selectedElement is None: return
        workOn = self.selectedElement.element

        # Make sure elements always move the same amount no matter their scale
        # The parents scale will be ignored, elements will move
        # respective to their parents scale not the visual editor frame
        scale = workOn.getScale()
        moverScaleX = 1 / scale.getX()
        moverScaleZ = 1 / scale.getZ()

        speed = 0.01
        if not self.editorFrame.visEditorInAspect2D:
            speed = 5

        if direction == "left":
            workOn.setX(workOn, -speed*moverScaleX*speedMult)
        elif direction == "right":
            workOn.setX(workOn, speed*moverScaleX*speedMult)
        elif direction == "up":
            workOn.setZ(workOn, speed*moverScaleZ*speedMult)
        elif direction == "down":
            workOn.setZ(workOn, -speed*moverScaleZ*speedMult)
        self.refreshProperties(self.selectedElement)
        base.messenger.send("setDirtyFlag")

    def removeElement(self, element=None):
        workOn = None
        selectEditor = False
        if element is not None:
            workOn = element
            if self.selectedElement is not None and element == self.selectedElement.element:
                selectEditor = True
                self.selectedElement = None
        elif self.selectedElement is not None:
            taskMgr.remove("dragDropTask")
            selectEditor = True
            workOn = self.selectedElement.element
            self.selectedElement = None
        else:
            return

        if not workOn.isEmpty():
            self.canvasParents = [
                "canvasTopCenter","canvasBottomCenter","canvasLeftCenter","canvasRightCenter",
                "canvasTopLeft","canvasTopRight","canvasBottomLeft","canvasBottomRight"]
            name = workOn.getName()
            if name.split("-")[1] in self.elementDict.keys():
                name = name.split("-")[1]
            if name in self.elementDict.keys():
                if self.elementDict[name].parent is not None \
                and (self.elementDict[name].parent.getName() if hasattr(self.elementDict[name].parent, "getName") else self.elementDict[name].parent.name) not in self.canvasParents \
                and self.elementDict[name].parent.type == "DirectScrolledList":
                    self.elementDict[name].parent.element.removeItem(workOn)

                # Check if our parent is a custom widget
                if self.elementDict[name].parent is not None \
                and self.customWidgetsHandler.getWidget(self.elementDict[name].parent.type) is not None:
                    widget = self.customWidgetsHandler.getWidget(self.elementDict[name].parent.type)
                    if widget.removeItemFunction is not None:
                        # call custom widget remove function
                        getattr(self.elementDict[name].parent.element, widget.removeItemFunction)(workOn)
                del self.elementDict[name]
        workOn.destroy()

        # cleanup
        for key, value in self.elementDict.copy().items():
            if value is None or value.element.isEmpty():
                del self.elementDict[key]

        if selectEditor:
            self.selectElement(self.visualEditorInfo)
        base.messenger.send("refreshStructureTree")
        base.messenger.send("setDirtyFlag")

    def toggleElementVisibility(self, element=None):
        workOn = None
        if element is not None:
            workOn = element
        elif self.selectedElement is not None:
            workOn = self.selectedElement.element
        else:
            return

        if workOn.isHidden():
            workOn.show()
        else:
            workOn.hide()
        base.messenger.send("refreshStructureTree")

    def __findFirstGUIElement(self, root):
        if hasattr(root, "getParent"):
            if not root.getParent().isEmpty():
                name = root.getParent().getName()
                if len(root.getName().split("-")) > 1:
                    name = root.getName().split("-")[1]
                if name in self.elementDict:
                    return self.elementDict[name]
                return self.__findFirstGUIElement(root.getParent())
            else:
                return None
        return None

    def setName(self, elementInfo, name):
        guiId = elementInfo.element.guiId
        e = self.elementDict[guiId]
        e.name = name
        if e.type == "DirectEntry":
            if (e.parent is not None
            and e.parent.type == "DirectEntryScroll"):
                parentID = e.parent.element.guiId
                self.elementDict[parentID].extraOptions["entry"] = name
        base.messenger.send("refreshStructureTree")

    def setCommand(self, elementInfo, command):
        self.elementDict[elementInfo.element.guiId].command = command

    def setExtraArgs(self, elementInfo, extraArgs):
        self.elementDict[elementInfo.element.guiId].extraArgs = extraArgs

    def setParentOfElement(self, element, parent):
        self.canvasParents = [
            "canvasTopCenter","canvasBottomCenter","canvasLeftCenter","canvasRightCenter",
            "canvasTopLeft","canvasTopRight","canvasBottomLeft","canvasBottomRight"]

        if parent is self.getEditorRootCanvas():
            self.elementDict[element.guiId].parent = None
        else:
            parentElement = None
            if parent.getName() in self.elementDict.keys():
                parentElement = self.elementDict[parent.getName()]
            elif len(parent.getName().split("-")) > 1 and parent.getName().split("-")[1] in self.elementDict.keys():
                parentElement = self.elementDict[parent.getName().split("-")[1]]
            elif parent.getName() in self.canvasParents:
                parentElement = parent
            else:
                # check if we can find an element as parent of the current NP
                # This happens for elements that have a canvas or other sub NPs
                parentElement = self.__findFirstGUIElement(parent)
            self.elementDict[element.guiId].parent = parentElement

    def copyElement(self):
        if self.selectedElement is None: return
        self.copiedElement = self.selectedElement

    def pasteElement(self):
        if self.copiedElement is None: return
        self.copyCreatedElementIds = []
        self.__copyBranch(self.copiedElement, self.selectedElement)

    def __copyBranch(self, startObject, parent=None):
        if startObject == parent: return
        for elementName, elementInfo in self.elementDict.copy().items():
            if elementInfo.element.guiId in self.copyCreatedElementIds: continue
            if elementInfo.parent == startObject or elementInfo == startObject:
                newElement = self.__createControl(elementInfo.type)
                if type(newElement) is tuple:
                    newElement = newElement[0]
                self.copyCreatedElementIds.append(elementInfo.element.guiId)
                if parent is not None:
                    newParent = None
                    if type(parent) is ElementInfo:
                        newParent = self.getEditorRootCanvas().find("**/{}".format(parent.element.getName()))
                    else:
                        newParent = self.getEditorRootCanvas().find("**/{}".format(parent.getName()))
                    self.setParentOfElement(newElement.element, newParent)
                    newElement.element.reparentTo(newParent)
                self.__copyOptions(elementInfo.element, newElement.element, parent is not None)

                self.__copyBranch(elementInfo, newElement.element)

    def copyOptions(self):
        if self.selectedElement is None: return
        self.copyOptionsElement = self.selectedElement.element
        print(self.copyOptionsElement)

    def pasteOptions(self):
        if self.copyOptionsElement is None: return
        self.__copyOptions(self.copyOptionsElement, self.selectedElement.element)

    def __copyOptions(self, elementFrom, elementTo, copyPosition=False):
        if elementFrom is None or elementTo is None: return
        try:
            text = elementTo["text"]
            text_fg = None
            for compName in elementFrom.components():
                comp = elementFrom.component(compName)
                if hasattr(comp, "fg"):
                    text_fg = comp.fg
                    break

            hpr = elementFrom.getHpr()
            scale = elementFrom.getScale()
            if copyPosition:
                pos = elementFrom.getPos()
            elementTo.copyOptions(elementFrom)
            elementTo["text"] = text
            if text_fg is not None:
                elementTo["text_fg"] = text_fg
            elementTo.setHpr(hpr)
            elementTo.setScale(scale)
            if copyPosition:
                elementTo.setPos(pos)
        except Exception as e:
            logging.error("Couldn't copy element options")
            logging.exception(e)
            base.messenger.send("showWarning", ["Couldn't copy element options"])

    def new(self):
        if self.dirty:
            self.dlgNewProject = OkCancelDialog(
                text="You have unsaved changes!\nReally create new project?",
                relief=DGG.RIDGE,
                frameColor=(1,1,1,1),
                frameSize=(-0.5,0.5,-0.3,0.2),
                sortOrder=1,
                button_relief=DGG.FLAT,
                button_frameColor=(0.8, 0.8, 0.8, 1),
                command=self.__newProject,
                scale=300,
                pos=(base.getSize()[0]/2, 0, -base.getSize()[1]/2),
                parent=base.pixel2d)
            self.dlgNewProjectShadow = DirectFrame(
                pos=(base.getSize()[0]/2 + 10, 0, -base.getSize()[1]/2 - 10),
                sortOrder=0,
                frameColor=(0,0,0,0.5),
                frameSize=self.dlgNewProject.bounds,
                scale=300,
                parent=base.pixel2d)
            return False
        else:
            self.__newProject(1)
            return True

    def __newProject(self, selection):
        if selection == 1:
            for name, elementInfo in list(self.elementDict.items()):
                self.removeElement(elementInfo.element)
            self.selectedElement = None
            self.elementDict = {}
            base.messenger.send("clearDirtyFlag")
        if self.dlgNewProject is not None:
            self.dlgNewProject.destroy()
            self.dlgNewProjectShadow.destroy()
            self.dlgNewProject = None
            self.dlgNewProjectShadow = None

    def save(self):
        self.selectElement(self.visualEditorInfo)
        DirectGuiDesignerExporterProject(os.path.join(self.lastDirPath, self.lastFileNameWOExtension + ".json"), self.elementDict, self.getEditorFrame, not self.editorFrame.visEditorInAspect2D, tooltip=self.tt)

    def export(self):
        self.selectElement(self.visualEditorInfo)
        DirectGuiDesignerExporterPy(os.path.join(self.lastDirPath, self.lastFileNameWOExtension + ".py"), self.elementDict, self.customWidgetsHandler, self.getEditorFrame, self.tt, not self.editorFrame.visEditorInAspect2D)

    def load(self):
        self.selectElement(self.visualEditorInfo)
        projectLoader = DirectGuiDesignerLoaderProject(os.path.join(self.lastDirPath, self.lastFileNameWOExtension + ".json"), self.visualEditorInfo, self.elementHandler, self.customWidgetsHandler, self.getEditorPlacer, False, self.tt, self.new)

    def updateElementDict(self, newDict):
        self.elementDict.update(newDict)
        base.messenger.send("refreshStructureTree")

    def __quit(self, selection):
        if selection == 1:
            self.userExit()
        else:
            self.dlgQuit.destroy()
            self.dlgQuitShadow.destroy()
            self.dlgQuit = None
            self.dlgQuitShadow = None
            del self.openDialogCloseFunctions[-1]

    def quitApp(self):
        if self.dlgQuit is not None: return
        if ConfigVariableBool("skip-ask-for-quit", False).getValue() or self.dirty == False:
            self.__quit(1)
            return

        self.dlgQuit = OkCancelDialog(
            text="You have unsaved changes!\nReally Quit?",
            state=DGG.NORMAL,
            relief=DGG.RIDGE,
            frameColor=(1,1,1,1),
            scale=300,
            pos=(base.getSize()[0]/2, 0, -base.getSize()[1]/2),
            sortOrder=1,
            button_relief=DGG.FLAT,
            button_frameColor=(0.8, 0.8, 0.8, 1),
            command=self.__quit,
            parent=base.pixel2d)
        self.dlgQuitShadow = DirectFrame(
            state=DGG.NORMAL,
            sortOrder=0,
            frameColor=(0,0,0,0.5),
            frameSize=(0, base.getSize()[0], -base.getSize()[1], 0),
            parent=base.pixel2d)
        self.openDialogCloseFunctions.append(self.__quit)

    def showSettings(self):
        if self.dlgSettings is not None:
            return

        base.messenger.send("unregisterKeyboardEvents")
        self.dlgSettingsShadow = DirectFrame(
            state=DGG.NORMAL,
            sortOrder=0,
            frameColor=(0,0,0,0.5),
            frameSize=(0, base.getSize()[0], -base.getSize()[1], 0),
            parent=base.pixel2d)

        self.dlgSettings = DirectGuiDesignerSettings(base.pixel2d)

        self.dlgSettings.lblSearchPath["state"] = DGG.NORMAL
        self.dlgSettings.lblSearchPath.bind(DGG.ENTER, self.tt.show, ["A colon separated list of paths to search for models, images and other assets"])
        self.dlgSettings.lblSearchPath.bind(DGG.EXIT, self.tt.hide)
        self.dlgSettings.txtSearchPaths.bind(DGG.ENTER, self.tt.show, ["A colon separated list of paths to search for models, images and other assets"])
        self.dlgSettings.txtSearchPaths.bind(DGG.EXIT, self.tt.hide)

        self.dlgSettings.setPos = self.dlgSettings.frmMain.setPos
        self.dlgSettings.setPos(self.screenWidthPx//2, 0, -self.screenHeightPx//2)
        self.dlgSettings.cbAskForQuit["indicatorValue"] = not ConfigVariableBool("skip-ask-for-quit", False).getValue()
        self.dlgSettings.cbExecutableScripts["indicatorValue"] = ConfigVariableBool("create-executable-scripts", False).getValue()
        self.dlgSettings.cbShowToolbar["indicatorValue"] = ConfigVariableBool("show-toolbar", True).getValue()
        self.dlgSettings.txtCustomWidgetsPath.enterText(ConfigVariableString("custom-widgets-path", "").getValue())
        self.dlgSettings.txtWorkDir.enterText(ConfigVariableString("work-dir-path", "").getValue())

        paths = ""
        pathsConfig = ConfigVariableSearchPath("custom-model-path", "").getValue()
        for path in pathsConfig.getDirectories():
            if paths != "":
                paths = "{}:{}".format(paths, path)
            else:
                print(path)
                paths = str(path)
        self.dlgSettings.txtSearchPaths.enterText(paths)

        def selectWidgetsPath(confirm):
            if confirm:
                self.dlgSettings.txtCustomWidgetsPath.enterText(self.browser.get())
            self.browser.hide()
            self.browser = None
        def showWidgetsBrowser():
            self.browser = DirectFolderBrowser(selectWidgetsPath, False, ConfigVariableString("custom-widgets-path", "").getValue(), os.path.split(ConfigVariableString("custom-widgets-path", "").getValue())[1], tooltip=self.tt)
            self.browser.show()
        self.dlgSettings.btnBrowseWidgetPath["command"] = showWidgetsBrowser

        def addSearchPath(confirm):
            if confirm:
                prevPaths = self.dlgSettings.txtSearchPaths.get()
                self.dlgSettings.txtSearchPaths.enterText("{}:{}".format(prevPaths, self.browser.get()))
            self.browser.hide()
            self.browser = None
        def showSearchPathBrowser():
            self.browser = DirectFolderBrowser(addSearchPath, False, tooltip=self.tt)
            self.browser.show()
        self.dlgSettings.btnBrowseSearchPaths["command"] = showSearchPathBrowser

        def selectWorkDirPath(confirm):
            if confirm:
                self.dlgSettings.txtWorkDir.enterText(self.browser.get())
            self.browser.hide()
            self.browser = None
        def showWorkDirBrowser():
            self.browser = DirectFolderBrowser(selectWorkDirPath, False, ConfigVariableString("work-dir-path", "").getValue(), os.path.split(ConfigVariableString("work-dir-path", "").getValue())[1], tooltip=self.tt)
            self.browser.show()
        self.dlgSettings.btnBrowseWorkDir["command"] = showWorkDirBrowser

        self.openDialogCloseFunctions.append(self.hideSettings)

    def hideSettings(self, accept):
        base.messenger.send("reregisterKeyboardEvents")
        if accept:
            with open(prcFileName, "w") as prcFile:
                line = "skip-ask-for-quit {}\n".format("#t" if self.dlgSettings.cbAskForQuit["indicatorValue"] == 0 else "#f")
                prcFile.write(line)
                loadPrcFileData("", line)

                line = "create-executable-scripts {}\n".format("#f" if self.dlgSettings.cbExecutableScripts["indicatorValue"] == 0 else "#t")
                prcFile.write(line)
                loadPrcFileData("", line)

                line = "show-toolbar {}\n".format("#f" if self.dlgSettings.cbShowToolbar["indicatorValue"] == 0 else "#t")
                prcFile.write(line)
                loadPrcFileData("", line)

                prcFile.write("custom-widgets-path {}\n".format(self.dlgSettings.txtCustomWidgetsPath.get()))
                for path in self.dlgSettings.txtSearchPaths.get().split(":"):
                    line = "custom-model-path {}\n".format(path)
                    prcFile.write(line)
                    line = "model-path {}\n".format(path)
                    loadPrcFileData("", line)

                prcFile.write("work-dir-path {}\n".format(self.dlgSettings.txtWorkDir.get()))

            # This somehow results in files that can't be changed by the code above anymore
            # So... no hidden config files for windows.
            #if platform.system() == "Windows":
            #    from ctypes import WinDLL
            #    from stat import FILE_ATTRIBUTE_HIDDEN
            #    from os import stat

            #    # Change the current files attributes to contain the "hidden" attribute
            #    kernel32 = WinDLL("kernel32")
            #    attrs = stat(prcFileName).st_file_attributes
            #    attrs = attrs | FILE_ATTRIBUTE_HIDDEN
            #    kernel32.SetFileAttributesW(prcFileName, attrs)


        self.dlgSettings.frmMain.hide()
        del self.dlgSettings
        self.dlgSettings = None

        self.dlgSettingsShadow.destroy()
        self.dlgSettingsShadow = None
        del self.openDialogCloseFunctions[-1]

    def showHelp(self):
        if self.dlgHelp is not None:
            self.hideHelp(None)
            return


        tpMgr = TextPropertiesManager.getGlobalPtr()

        tpHeader = TextProperties()
        tpHeader.setTextScale(1.5)
        tpHeader.setUnderscore(True)
        tpHeader.setGlyphShift(1)
        font = loader.loadFont("fonts/DejaVuSansMono-Bold.ttf")
        tpHeader.setFont(font)
        tpMgr.setProperties("header", tpHeader)

        tpSmall = TextProperties()
        tpSmall.setTextScale(0.75)
        tpMgr.setProperties("small", tpSmall)

        tpBold = TextProperties()
        font = loader.loadFont("fonts/DejaVuSansMono-Bold.ttf")
        tpBold.setFont(font)
        tpMgr.setProperties("bold", tpBold)

        text="""\1header\1~~~Direct GUI Visual Editor Help~~~\2

\1bold\1LMB\2 - Select an element / Press and drag to move element around
\1bold\1Esc\2 - Deselect currently selected Element
\1bold\1RMB\2 - Deselect currently selected Element
\1bold\1MMB\2 - Move Editor Area

\1bold\1Mouse Wheel\2 - Zoom

\1bold\1Ctrl-N  \2 - Create New GUI
\1bold\1Ctrl-S  \2 - Save as Project File
\1bold\1Ctrl-E  \2 - Export as Python File
\1bold\1Ctrl-O  \2 - Load Project File
\1bold\1Ctrl-Q  \2 - Quit Application
\1bold\1Ctrl-C  \2 - Copy selected Element
\1bold\1Ctrl-V  \2 - Paste copied Element
\1bold\1Ctrl-Shift-C\2 - Copy selected Elements settings
\1bold\1Ctrl-Shift-V\2 - Paste copied Element settings to selected element
\1bold\1Ctrl-Del\2 - Delete selected Element
\1bold\1Ctrl-H  \2 - Toggle selected Element visibility
\1bold\1Ctrl-G  \2 - Toggle grid and snap to grid

\1bold\1Arrow Keys\2 - Move the selected Element (use Shift and Ctrl to change distance)

\1bold\1F1\2 - Show this help Dialog

Note: If the grid is shown elements will automatically snap to it when moved

Log messages are written to:

\1small\1{}\2


\1small\1LMB = Left Mouse Button | RMB = Right Mouse Button | MMB = Middle Mouse Button\2
""".format(logfile)
        self.dlgHelp = OkDialog(
            text=text,
            state=DGG.NORMAL,
            relief=DGG.RIDGE,
            frameColor=(1,1,1,1),
            sortOrder=1,
            scale=300,
            pos=(base.getSize()[0]/2, 0, -base.getSize()[1]/2),
            button_relief=DGG.FLAT,
            button_frameColor=(0.8, 0.8, 0.8, 1),
            command=self.hideHelp,
            parent=base.pixel2d)
        self.dlgHelpShadow = DirectFrame(
            state=DGG.NORMAL,
            sortOrder=0,
            frameColor=(0,0,0,0.5),
            frameSize=(0, base.getSize()[0], -base.getSize()[1], 0),
            parent=base.pixel2d)
        self.openDialogCloseFunctions.append(self.hideHelp)

    def hideHelp(self, args):
        self.dlgHelp.destroy()
        self.dlgHelpShadow.destroy()
        self.dlgHelp = None
        self.dlgHelpShadow = None
        del self.openDialogCloseFunctions[-1]

    def showWarning(self, text):
        if self.dlgWarning is not None: return
        text = "WARNING!\n\n" + text
        self.dlgWarning = OkDialog(
            text=text,
            state=DGG.NORMAL,
            relief=DGG.RIDGE,
            frameColor=(1,1,1,1),
            sortOrder=1,
            scale=300,
            pos=(base.getSize()[0]/2, 0, -base.getSize()[1]/2),
            button_relief=DGG.FLAT,
            button_frameColor=(0.8, 0.8, 0.8, 1),
            command=self.hideWarning,
            parent=base.pixel2d)
        self.dlgWarningShadow = DirectFrame(
            state=DGG.NORMAL,
            sortOrder=0,
            frameColor=(0.25,0,0,0.5),
            frameSize=(0, base.getSize()[0], -base.getSize()[1], 0),
            parent=base.pixel2d)
        self.openDialogCloseFunctions.append(self.hideWarning)

    def hideWarning(self, args):
        self.dlgWarning.destroy()
        self.dlgWarningShadow.destroy()
        self.dlgWarning = None
        self.dlgWarningShadow = None
        del self.openDialogCloseFunctions[-1]

    def showInfo(self, text):
        if self.dlgInfo is not None: return
        text = "INFO:\n\n" + text
        self.dlgInfo = OkDialog(
            text=text,
            state=DGG.NORMAL,
            relief=DGG.RIDGE,
            frameColor=(1,1,1,1),
            sortOrder=1,
            scale=300,
            pos=(base.getSize()[0]/2, 0, -base.getSize()[1]/2),
            button_relief=DGG.FLAT,
            button_frameColor=(0.8, 0.8, 0.8, 1),
            command=self.hideInfo,
            parent=base.pixel2d)
        self.dlgInfoShadow = DirectFrame(
            state=DGG.NORMAL,
            sortOrder=0,
            frameColor=(0.15,0.15,0.25,0.5),
            frameSize=(0, base.getSize()[0], -base.getSize()[1], 0),
            parent=base.pixel2d)
        self.openDialogCloseFunctions.append(self.hideInfo)

    def hideInfo(self, args):
        self.dlgInfo.destroy()
        self.dlgInfoShadow.destroy()
        self.dlgInfo = None
        self.dlgInfoShadow = None
        del self.openDialogCloseFunctions[-1]

designer=DirectGuiDesigner()
designer.run()
