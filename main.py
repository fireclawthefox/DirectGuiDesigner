#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import platform
import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from logging import StreamHandler
import tempfile

from direct.showbase.ShowBase import ShowBase

from panda3d.core import (
    Point3,
    Vec3,
    Filename,
    loadPrcFile,
    loadPrcFileData,
    WindowProperties,
    ConfigVariableInt,
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

from DirectGuiDesigner.panels.CanvasPanel import CanvasPanel
from DirectGuiDesigner.panels.MenuBar import MenuBar
from DirectGuiDesigner.panels.ToolBar import ToolBar
from DirectGuiDesigner.panels.ToolboxPanel import ToolboxPanel
from DirectGuiDesigner.panels.PropertiesPanel import PropertiesPanel
from DirectGuiDesigner.panels.StructurePanel import StructurePanel

from DirectGuiDesigner.export.ExporterPy import ExporterPy
from DirectGuiDesigner.export.ExporterProject import ExporterProject

from DirectGuiDesigner.loader.Project import ProjectLoader
from DirectGuiDesigner.loader.PyScript import PyScriptLoader

from DirectGuiDesigner.dialogs.SettingsDialog import GUI as SettingsDialog

from DirectGuiDesigner.core.ElementHandler import ElementHandler
from DirectGuiDesigner.core.ElementInfo import ElementInfo
from DirectGuiDesigner.core.CustomWidgets import CustomWidgets
from DirectGuiDesigner.core.KillRing import KillRing

from DirectFolderBrowser.DirectFolderBrowser import DirectFolderBrowser

from DirectGuiExtension import DirectGuiHelper as DGH

from DirectGuiExtension.DirectTooltip import DirectTooltip

from DirectGuiExtension.DirectBoxSizer import DirectBoxSizer
from DirectGuiExtension.DirectAutoSizer import DirectAutoSizer
from DirectGuiExtension.DirectSplitFrame import DirectSplitFrame

from DirectGuiDesigner.core import WidgetDefinition

loadPrcFileData(
    "",
    """
    sync-video #t
    textures-power-2 none
    window-title DirectGUI Designer
    #show-frame-rate-meter #t
    #want-pstats #t
    maximized #t
    model-path $MAIN_DIR/models/
    win-size 1280 720
    ime-aware #t
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

# Remove log files older than 30 days
for f in os.listdir(logPath):
    fParts = f.split(".")
    fDate = datetime.now()
    try:
        fDate = datetime.strptime(fParts[-1], "%Y-%m-%d_%H")
        delta = datetime.now() - fDate
        if delta.days > 30:
            #print(f"remove {os.path.join(logPath, f)}")
            os.remove(os.path.join(logPath, f))
    except Exception:
        # this file does not have a date ending
        pass

logfile = os.path.join(logPath, "DirectGuiDesigner.log")
handler = TimedRotatingFileHandler(logfile)
consoleHandler = StreamHandler()
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[handler])#, consoleHandler])
prcFileName = os.path.join(basePath, ".DirectGuiDesigner.prc")
if os.path.exists(prcFileName):
    loadPrcFile(Filename.fromOsSpecific(prcFileName))

    # make sure to load our custom paths
    pathsConfig = ConfigVariableSearchPath("custom-model-path", "").getValue()
    for path in pathsConfig.getDirectories():
        line = "model-path {}".format(str(path))
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
        self.hasSaved = False
        self.killRing = KillRing()

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

        self.copyOptionsElementInfo = None

        self.copiedElement = None

        self.theCutElement = None

        # Delay initial setup by 0.5s to let the window set it's final
        # size and we'll be able to use the screen corner/edge variables
        taskMgr.doMethodLater(0.5, self.setupGui, "delayed setup", extraArgs = [])


        taskMgr.doMethodLater(ConfigVariableInt("autosave-delay", 60).getValue(), self.autosaveTask, 'autosave task')

    def setupGui(self):
        logging.debug("Setup GUI")
        self.screenWidth = abs(base.a2dRight) + abs(base.a2dLeft)
        self.screenWidthPx = base.getSize()[0]
        self.screenHeightPx = base.getSize()[1]
        self.leftEdge = -(self.screenWidth * (2.0 / 3.0))
        self.rightEdge = self.screenWidth * (1.0 / 3.0)
        splitterWidth = 8

        self.tt = DirectTooltip(
            text = "Tooltip",
            #text_fg = (1,1,1,1),
            pad=(0.2, 0.2),
            scale = 16,
            text_align = TextNode.ALeft,
            frameColor = (1, 1, 0.7, 1),
            parent=base.pixel2d,
            sortOrder=1000)

        #
        # LAYOUT SETUP
        #

        self.mainBox = DirectBoxSizer(
            frameColor=(1,0,0,1),
            orientation=DGG.VERTICAL,
            autoUpdateFrameSize=False)
        self.mainSizer = DirectAutoSizer(
            parent=base.pixel2d,
            child=self.mainBox,
            childUpdateSizeFunc=self.mainBox.refresh
            )

        self.menuBarHeight = 24
        self.toolBarHeight = 48

        self.menuBarSizer = DirectAutoSizer(
            updateOnWindowResize=False,
            parent=self.mainBox,
            minSize=(0,0,-self.menuBarHeight/2, self.menuBarHeight/2),
            extendVertical=False)
        self.toolBarSizer = DirectAutoSizer(
            updateOnWindowResize=False,
            parent=self.mainBox,
            minSize=(0,0,-self.toolBarHeight/2, self.toolBarHeight/2),
            extendVertical=False)
        self.mainBox.addItem(self.menuBarSizer, updateFunc=self.menuBarSizer.refresh, skipRefresh=True)
        self.mainBox.addItem(self.toolBarSizer, updateFunc=self.toolBarSizer.refresh, skipRefresh=True)

        self.mainSplitter = DirectSplitFrame(
            frameSize=self.getMainSplitterSize(),
            firstFrameMinSize=100,
            secondFrameMinSize=100,
            splitterWidth=splitterWidth,
            splitterPos=self.screenWidthPx/3,
            pixel2d=True)
        self.mainSplitter.firstFrame["frameColor"] = (1,1,0,1)
        self.mainSplitter.secondFrame["frameColor"] = (0,1,1,1)

        self.mainSplitter["frameColor"] = (1,0,1,1)
        #self.mainSplitter.firstFrame.hide()
        #self.mainSplitter.secondFrame.hide()

        self.mainSplitSizer = DirectAutoSizer(
            updateOnWindowResize=False,
            parent=self.mainBox,
            child=self.mainSplitter,
            extendVertical=False,
            childUpdateSizeFunc=self.mainSplitter.refresh,
            )
        self.mainBox.addItem(self.mainSplitSizer, updateFunc=self.mainSplitSizer.refresh, skipRefresh=True)
        #self.mainSplitter["splitterPos"] = self.screenWidthPx/3

        self.sidebarSplitterA = DirectSplitFrame(
            frameSize=(0,DGH.getRealWidth(self.mainSplitter.firstFrame),0,DGH.getRealHeight(self.mainSplitter.firstFrame)),
            firstFrameMinSize=40,
            secondFrameMinSize=20,
            splitterWidth=splitterWidth,
            splitterPos=DGH.getRealHeight(self.mainSplitter)/3*2,
            pixel2d=True,
            orientation=DGG.VERTICAL)
        self.sidebarSplitterA.firstFrame["frameColor"] = (1,0,0,1)
        self.sidebarSplitterA.secondFrame["frameColor"] = (1,0,1,1)
        self.sideSplitSizerA = DirectAutoSizer(
            updateOnWindowResize=False,
            parent=self.mainSplitter.firstFrame,
            child=self.sidebarSplitterA,
            childUpdateSizeFunc=self.sidebarSplitterA.refresh
            )
        self.mainSplitter["firstFrameUpdateSizeFunc"] = self.sideSplitSizerA.refresh
        #self.sidebarSplitterA["splitterPos"] = DGH.getRealHeight(self.mainSplitter)/3*2

        self.sidebarSplitterB = DirectSplitFrame(
            frameSize=(0,DGH.getRealWidth(self.sidebarSplitterA.firstFrame),0,DGH.getRealHeight(self.sidebarSplitterA.firstFrame)),
            firstFrameMinSize=20,
            secondFrameMinSize=20,
            splitterWidth=splitterWidth,
            orientation=DGG.VERTICAL)
        self.sidebarSplitterB.firstFrame["frameColor"] = (0,0,1,1)
        self.sidebarSplitterB.secondFrame["frameColor"] = (0,1,0,1)
        self.sideSplitSizerB = DirectAutoSizer(
            updateOnWindowResize=False,
            parent=self.sidebarSplitterA.secondFrame,
            child=self.sidebarSplitterB,
            childUpdateSizeFunc=self.sidebarSplitterB.refresh
            )
        self.sidebarSplitterA["secondFrameUpdateSizeFunc"] = self.sideSplitSizerB.refresh

        #
        # CONTENT SETUP
        #

        self.editorFrame = CanvasPanel(self.mainSplitter.secondFrame)
        self.mainSplitter["secondFrameUpdateSizeFunc"] = self.editorFrame.resizeFrame

        self.visualEditorInfo = ElementInfo(self.editorFrame.visualEditor, "Editor")

        self.menuBar = MenuBar(self.editorFrame.grid)
        self.menuBarSizer.setChild(self.menuBar.menuBar)
        self.menuBarSizer["childUpdateSizeFunc"] = self.menuBar.menuBar.refresh

        self.toolBar = ToolBar(self.tt, self.editorFrame.grid)
        self.toolBarSizer.setChild(self.toolBar.toolBar)
        self.toolBarSizer["childUpdateSizeFunc"] = self.toolBar.toolBar.refresh

        self.mainBox.refresh()

        # TOOLBOX
        self.toolboxFrame = ToolboxPanel(
            self.sidebarSplitterA.firstFrame)
        self.sidebarSplitterA["firstFrameUpdateSizeFunc"]=self.toolboxFrame.resizeFrame

        # PROPERTIES EDITOR
        self.propertiesFrame = PropertiesPanel(
            self.sidebarSplitterB.firstFrame,
            self.getEditorRootCanvas,
            self.getEditorPlacer,
            self.tt)
        self.propertiesEditor(self.visualEditorInfo)
        self.sidebarSplitterB["firstFrameUpdateSizeFunc"]=self.propertiesFrame.resizeFrame

        # STRUCTUR VIEWER
        self.structureFrame = StructurePanel(
            self.sidebarSplitterB.secondFrame,
            self.getEditorRootCanvas,
            self.elementDict,
            self.selectedElement)
        self.sidebarSplitterB["secondFrameUpdateSizeFunc"]=self.structureFrame.resizeFrame

        #
        # ELEMENT HANDLERS
        #
        self.elementHandler = ElementHandler(self.propertiesFrame, self.getEditorRootCanvas)
        self.customWidgetsHandler = CustomWidgets(self.toolboxFrame, self.elementHandler)
        self.propertiesFrame.setCustomWidgetDefinitions(self.customWidgetsHandler.getCustomWidgetDefinitions())

        # connect the handler with the editor frame
        self.editorFrame.setElementHandler(self.elementHandler)

        self.registerKeyboardEvents()

        # these keys will not be ignored until the application is closed
        self.accept("escape", self.inteligentEscape)
        self.accept("mouse3", self.selectElement, extraArgs=[self.visualEditorInfo, None])
        self.accept("mouse2", self.editorFrame.dragEditorFrame, extraArgs=[True])
        self.accept("mouse2-up", self.editorFrame.dragEditorFrame, extraArgs=[False])
        self.accept("wheel_up", self.editorFrame.zoom, extraArgs=[.1])
        self.accept("wheel_down", self.editorFrame.zoom, extraArgs=[-.1])

        # here we have custom events that do not represent a keyboard action
        self.accept("unregisterKeyboardEvents", self.ignoreKeyboardEvents)
        self.accept("reregisterKeyboardEvents", self.registerKeyboardEvents)


        self.accept("quitApp", self.quitApp)

        # TASK AND MENU BAR FEATURES
        self.accept("newProject", self.new)
        self.accept("saveProject", self.save)
        self.accept("exportProject", self.export)
        self.accept("loadProject", self.load)
        self.accept("toggleGrid", self.editorFrame.toggleGrid)
        self.accept("toggleVisualEditorParent", self.editorFrame.toggleVisualEditorParent)
        self.accept("setVisualEditorParent", self.editorFrame.setVisualEditorParent)
        self.accept("setVisualEditorCanvasSize", self.editorFrame.setVisualEditorCanvasSize)

        # DATA
        self.accept("updateElementDict-afterLoad", self.updateElementDict)

        # REFRESH PANELS
        self.accept("refreshStructureTree", self.__refreshStructureTree)
        self.accept("refreshProperties", self.refreshProperties)

        # Element handling
        self.accept("createControl", self.__createControl)
        self.accept("selectElement", self.selectElement)
        self.accept("removeElement", self.removeElement)
        self.accept("copyOptions", self.copyOptions)
        self.accept("pasteOptions", self.pasteOptions)
        self.accept("cutElement", self.cutElement)
        self.accept("copyElement", self.copyElement)
        self.accept("pasteElement", self.pasteElement)
        self.accept("moveElementInStructure", self.moveElementInStructure)
        self.accept("setName", self.setName)

        # DRAG AND DROP
        self.accept("dragStart", self.dragStart)
        self.accept("dragStop", self.dragStop)

        # UNDO/REDO
        self.accept("undo", self.undo)
        self.accept("redo", self.redo)
        self.accept("cycleRedo", self.cycleKillRing)
        self.accept("toggleElementVisibility", self.toggleElementVisibility)
        self.accept("setParentOfElement", self.setParentOfElement)
        self.accept("addToKillRing", self.addToKillRing)

        # HELP DIALOG
        self.accept("showHelp", self.showHelp)

        # SETTINGS
        self.accept("showSettings", self.showSettings)
        self.accept("Settings_OK", self.hideSettings, [True])
        self.accept("Settings_CANCEL", self.hideSettings, [False])

        # ZOOM
        self.accept("setEditorZoom", self.editorFrame.setZoom)
        self.accept("resetZoom", self.editorFrame.resetZoom)
        self.accept("setZoomValeMinMax", self.toolBar.setZoomMinMax)
        self.accept("setZoomValue", self.toolBar.setZoomValue)
        self.accept("zoom-in", self.editorFrame.zoom, extraArgs=[.1])
        self.accept("zoom-out", self.editorFrame.zoom, extraArgs=[-.1])
        self.accept("zoom-reset", self.editorFrame.resetZoom)

        # SAVE INDICATOR
        self.accept("setDirtyFlag", self.setDirty)
        self.accept("clearDirtyFlag", self.setClean)

        # SAVING/LOADING
        self.accept("setLastPath", self.setLastPath)

        # FEEDBACK
        self.accept("showWarning", self.showWarning)
        self.accept("showInfo", self.showInfo)

        # WINDOW HANDLING
        self.screenSize = base.getSize()
        self.accept("window-event", self.windowEventHandler)

        sys.excepthook = self.excHandler

        self.win.setCloseRequestEvent("quitApp")

        # Load user custom widgets
        self.customWidgetsHandler.loadCustomWidgets()

        # Exception save-file-handling
        tmpPath = os.path.join(tempfile.gettempdir(), "DGDExceptionSave.json")
        if os.path.exists(tmpPath):
            logging.info("Loading crash session file {}".format(tmpPath))
            allWidgetDefinitions = {
                **WidgetDefinition.DEFINITIONS,
                **self.customWidgetsHandler.getCustomWidgetDefinitions()}
            projectLoader = ProjectLoader(
                tmpPath,
                self.visualEditorInfo,
                self.elementHandler,
                self.customWidgetsHandler,
                self.getEditorPlacer,
                allWidgetDefinitions,
                True)
            self.elementDict = projectLoader.get()
            base.messenger.send("refreshStructureTree")
            base.messenger.send("setDirtyFlag")
            base.messenger.send("showInfo", ["Loaded previously crashed session!"])
            os.remove(tmpPath)
            logging.info("Removed crash session file")
        logging.debug("Startup complete")

        # refresh the editor area.
        self.editorFrame.setVisualEditorParent(False)

    def getMainSplitterSize(self):
        return (
            -self.screenWidthPx/2,
            self.screenWidthPx/2,
            0,
            self.screenHeightPx - self.menuBarHeight - self.toolBarHeight)

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
        self.hasSaved = True

    def addToKillRing(self, editObject, action, objectType, oldValue, newValue):
        if action == "set" and oldValue == newValue:
            logging.debug(f"action={action}, type={objectType} was not added to killring, reason: old={oldValue} equals new={newValue}")
            return
        logging.debug(f"Add to killring action={action}, type={objectType}, old={oldValue}, new={newValue}")
        self.killRing.push(editObject, action, objectType, oldValue, newValue)

    def undo(self):
        # undo this action
        workOn = self.killRing.pop()

        if workOn is None: return

        if workOn.action == "set":
            if workOn.objectType == "pos":
                logging.debug(f"undo Position to {workOn.oldValue}")
                workOn.editObject.element.setPos(workOn.oldValue)
            elif workOn.objectType == "pressEffect":
                logging.debug(f"try undo press effect to {workOn.oldValue}")
                workOn.editObject.extraOptions["pressEffect"] = workOn.oldValue
            elif workOn.objectType == "transparency":
                workOn.editObject.element.setTransparency(workOn.oldValue)
            else:
                try:
                    logging.debug(f"try undo {workOn.objectType} to {workOn.oldValue}")
                    workOn.editObject.element[workOn.objectType] = workOn.oldValue
                except:
                    logging.exception(f"property {workOn.objectType} currently not supported by undo/redo")

        elif workOn.action == "add" and workOn.objectType == "element":
            logging.debug(f"undo remove added element {workOn.editObject}")
            self.removeElement(workOn.editObject, False)

        elif workOn.action == "kill" and workOn.objectType == "element":
            logging.debug(f"undo last kill {workOn.editObject}")
            workOn.editObject.unstash()
            self.elementDict[workOn.oldValue[0]] = workOn.oldValue[1]
            base.messenger.send("refreshStructureTree")

        elif workOn.action == "copy":
            logging.debug(f"undo last copy {workOn.objectType}")
            if workOn.objectType == "element":
                self.removeElement(workOn.editObject.element, False)
            elif workOn.objectType == "properties":
                for key, value in workOn.oldValue.items():
                    if key == "pos":
                        workOn.editObject.element.setPos(value)
                    elif key == "hpr":
                        workOn.editObject.element.setHpr(value)
                    elif key == "scale":
                        workOn.editObject.element.setScale(value)
                    elif key == "text_fg":
                        workOn.editObject.element["text_fg"] = value
                    else:
                        workOn.editObject.element[key] = value[1]

        if self.selectedElement is not None:
            self.refreshProperties(self.selectedElement)
        base.messenger.send("setDirtyFlag")

    def redo(self):
        # redo this
        workOn = self.killRing.pull()

        if workOn is None:
            logging.debug("nothing to redo")
            return

        if workOn.action == "set":
            if workOn.objectType == "pos":
                if type(workOn.newValue) is list:
                    workOn.editObject.element.setPos(*workOn.newValue)
                else:
                    workOn.editObject.element.setPos(workOn.newValue)
            elif workOn.objectType == "pressEffect":
                workOn.editObject.extraOptions["pressEffect"] = workOn.newValue
            else:
                try:
                    workOn.editObject.element[workOn.objectType] = workOn.newValue
                except:
                    logging.exception(f"property {workOn.objectType} currently not supported by undo/redo")

        elif workOn.action == "add" and workOn.objectType == "element":
            workOn.editObject.unstash()
            self.elementDict[workOn.oldValue[0]] = workOn.oldValue[1]
            base.messenger.send("refreshStructureTree")

        elif workOn.action == "kill" and workOn.objectType == "element":
            self.removeElement(workOn.editObject, False)

        elif workOn.action == "copy":
            if workOn.objectType == "element":
                workOn.editObject.unstash()
                self.elementDict[workOn.oldValue[0]] = workOn.oldValue[1]
                base.messenger.send("refreshStructureTree")
            elif workOn.objectType == "properties":
                for key, value in workOn.newValue.items():
                    if key == "pos":
                        workOn.editObject.element.setPos(value)
                    elif key == "hpr":
                        workOn.editObject.element.setHpr(value)
                    elif key == "scale":
                        workOn.editObject.element.setScale(value)
                    elif key == "text_fg":
                        workOn.editObject.element["text_fg"] = value
                    else:
                        workOn.editObject.element[key] = value[1]

        if self.selectedElement is not None:
            self.refreshProperties(self.selectedElement)
        base.messenger.send("setDirtyFlag")

    def cycleKillRing(self):
        """Cycles through the redo branches at the current depth of the kill ring"""
        self.undo()
        self.killRing.cycleChildren()
        self.redo()

    def setLastPath(self, path):
        self.lastDirPath = os.path.dirname(path)
        fn = os.path.splitext(os.path.basename(path))[0]
        if fn != "":
            self.lastFileNameWOExtension = os.path.splitext(os.path.basename(path))[0]

    def getEditorRootCanvas(self):
        """ returns the canvas element which acts as the root parent for all
        elements in the editors edit area """
        return self.editorFrame.getEditorRootCanvas()

    def getEditorPlacer(self, placerName):
        """Returns the nodepath to a specific placer in the editor. Those
        usually are located at the edges and corners of the editor and resemble
        the a2d* counterparts from the engine"""
        return self.editorFrame.getEditorPlacer(placerName)

    def getAllEditorPlacers(self):
        return self.editorFrame.getAllEditorPlacers()

    def getEditorFrame(self):
        return self.editorFrame.visualEditor

    def excHandler(self, ex_type, ex_value, ex_traceback):
        logging.error("Unhandled exception", exc_info=(ex_type, ex_value, ex_traceback))
        print("Try to save file after unhandled exception. Please restart the app to automatically load the exception save file!")
        allWidgetDefinitions = {
            **WidgetDefinition.DEFINITIONS,
            **self.customWidgetsHandler.getCustomWidgetDefinitions()}
        ExporterProject(
            "",
            self.elementDict,
            self.getEditorFrame,
            self.getAllEditorPlacers,
            allWidgetDefinitions,
            not self.editorFrame.visEditorInAspect2D,
            exceptionSave=True)

    def autosaveTask(self, task):
        task.delayTime = ConfigVariableInt("autosave-delay", 60).getValue()
        try:
            filename = ""
            if self.hasSaved:
                filename = os.path.join(self.lastDirPath, self.lastFileNameWOExtension + ".json~")
            allWidgetDefinitions = {
                **WidgetDefinition.DEFINITIONS,
                **self.customWidgetsHandler.getCustomWidgetDefinitions()}
            ExporterProject(
                filename,
                self.elementDict,
                self.getEditorFrame,
                self.getAllEditorPlacers,
                allWidgetDefinitions,
                not self.editorFrame.visEditorInAspect2D,
                autosave=True)
        except Exception as e:
            logging.error("Autosave failed")
            logging.exception(e)
            print("autosave failed")
        return task.again

    def inteligentEscape(self):
        dlgList = [self.dlgHelp, self.dlgSettings, self.dlgQuit, self.dlgWarning, self.dlgInfo, self.dlgNewProject]
        if not all(dlg is None for dlg in dlgList):
            self.openDialogCloseFunctions[-1](None)
        else:
            self.selectElement(self.visualEditorInfo, None)

    def registerKeyboardEvents(self):
        speedUp = 5
        speedDown = 0.5
        self.keyEvents = {
            "+": [self.editorFrame.zoom, [.1]],
            "-": [self.editorFrame.zoom, [-.1]],
            "control-0": [self.editorFrame.resetZoom],

            "control-n": [self.new],
            "control-s": [self.save],
            "control-e": [self.export],
            "control-o": [self.load],
            "control-q": [self.quitApp],
            "control-c": [self.copyElement],
            "control-x": [self.cutElement],
            "control-v": [self.pasteElement],
            "shift-control-c": [self.copyOptions],
            "shift-control-v": [self.pasteOptions],
            "delete": [self.removeElement],
            "control-g": [self.toolBar.cb_grid.commandFunc, [None]],
            "control-h": [self.toggleElementVisibility],
            "f1": [self.showHelp],
            "control-z": [self.undo],
            "control-y": [self.redo],
            "shift-control-y": [self.cycleKillRing],

            "page_up": [self.moveElementInStructure, [1]],
            "page_down": [self.moveElementInStructure, [-2]],

            "arrow_left": [self.moveElement, ["left"]],
            "arrow_right": [self.moveElement, ["right"]],
            "arrow_up": [self.moveElement, ["up"]],
            "arrow_down": [self.moveElement, ["down"]],

            "arrow_left-repeat": [self.moveElement, ["left"]],
            "arrow_right-repeat": [self.moveElement, ["right"]],
            "arrow_up-repeat": [self.moveElement, ["up"]],
            "arrow_down-repeat": [self.moveElement, ["down"]],

            "shift-arrow_left": [self.moveElement, ["left", speedUp]],
            "shift-arrow_right": [self.moveElement, ["right", speedUp]],
            "shift-arrow_up": [self.moveElement, ["up", speedUp]],
            "shift-arrow_down": [self.moveElement, ["down", speedUp]],

            "shift-arrow_left-repeat": [self.moveElement, ["left", speedUp]],
            "shift-arrow_right-repeat": [self.moveElement, ["right", speedUp]],
            "shift-arrow_up-repeat": [self.moveElement, ["up", speedUp]],
            "shift-arrow_down-repeat": [self.moveElement, ["down", speedUp]]
        }

        for event, actionSet in self.keyEvents.items():
            if len(actionSet) == 2:
                self.accept(event, actionSet[0], extraArgs=actionSet[1])
            else:
                self.accept(event, actionSet[0])

    def ignoreKeyboardEvents(self):
        for event, actionSet in self.keyEvents.items():
            self.ignore(event)

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

            # resize the main splitter to fit the remaining window space
            self.mainSplitter["frameSize"] = self.getMainSplitterSize()

    def propertiesEditor(self, elementInfo):
        self.propertiesFrame.setupProperties("Editor Properties", elementInfo, self.elementDict)

    def __refreshStructureTree(self):
        self.structureFrame.refreshStructureTree(self.elementDict, self.selectedElement)

    def __createControl(self, element):
        funcName = "create{}".format(element)
        parent = None
        elementInfo = None
        widget = self.customWidgetsHandler.getWidget(element)
        if self.selectedElement is not None:
            if self.selectedElement.type == "DirectScrolledFrame":
                parent = self.selectedElement.element.canvas
            else:
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
                sort = self.getMaxSort(entry)
                entry.element.reparentTo(entry.element.getParent(), sort)
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
            sort = self.getMaxSort(elementInfo)
            elementInfo.element.reparentTo(elementInfo.element.getParent(), sort)
            self.elementDict[elementInfo.element.guiId] = elementInfo
        base.messenger.send("refreshStructureTree")
        base.messenger.send("setDirtyFlag")

        if type(elementInfo) is tuple:
            base.messenger.send("addToKillRing",
                [elementInfo[0].element, "add", "element", (elementInfo[0].element.guiId, elementInfo[0]), None])
        else:
            base.messenger.send("addToKillRing",
                [elementInfo.element, "add", "element", (elementInfo.element.guiId, elementInfo), None])

        self.fixElementSortAll()

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
        sp = element.getPos()
        pos = element.getPos(parent)
        element.setPos(pos)
        vWidget2render2d = element.getPos(render2d)
        vMouse2render2d = Point3(event.getMouse()[0], 0, event.getMouse()[1])
        editVec = Vec3(vWidget2render2d - vMouse2render2d)
        t = taskMgr.add(self.dragTask, "dragDropTask")
        t.startPos = sp
        t.elementInfo = elementInfo
        t.editVec = editVec
        t.mouseVec = vMouse2render2d
        t.hasMoved = False

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
            if oldPos != t.elementInfo.element.getPos():
                t.hasMoved = True

        return t.cont

    def dragStop(self, event):
        t = taskMgr.getTasksNamed("dragDropTask")[0]
        #parent = t.elementInfo.element.getParent()
        pos = t.elementInfo.element.getPos()

        if ConfigVariableBool("keep-in-canvas", False).getValue():
            if pos.x < self.editorFrame.getEditorCanvasSize()[0]:
                t.elementInfo.element.setX(self.editorFrame.getEditorCanvasSize()[0])
            if pos.x > self.editorFrame.getEditorCanvasSize()[1]:
                t.elementInfo.element.setX(self.editorFrame.getEditorCanvasSize()[1])
            if pos.z < self.editorFrame.getEditorCanvasSize()[2]:
                t.elementInfo.element.setZ(self.editorFrame.getEditorCanvasSize()[2])
            if pos.z > self.editorFrame.getEditorCanvasSize()[3]:
                t.elementInfo.element.setZ(self.editorFrame.getEditorCanvasSize()[3])
        self.refreshProperties(t.elementInfo)

        if t.hasMoved:
            base.messenger.send("addToKillRing",
                [t.elementInfo, "set", "pos", t.startPos, t.elementInfo.element.getPos()])

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

        startPos = workOn.getPos()

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
        base.messenger.send("addToKillRing",
            [self.selectedElement, "set", "pos", startPos, workOn.getPos()])

    def removeElement(self, element=None, includeWithKillCycle=True):
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

        oldParent = None
        if not workOn.isEmpty() and not workOn.isStashed():
            self.canvasParents = [
                "canvasTopCenter","canvasBottomCenter","canvasLeftCenter","canvasRightCenter",
                "canvasTopLeft","canvasTopRight","canvasBottomLeft","canvasBottomRight"]
            name = workOn.getName()
            if name.split("-")[1] in self.elementDict.keys():
                name = name.split("-")[1]
            if name in self.elementDict.keys():

                if includeWithKillCycle:
                    base.messenger.send("addToKillRing",
                        [workOn, "kill", "element", (name, self.elementDict[name]), None])

                if self.elementDict[name].parent is not None \
                and (self.elementDict[name].parent.getName() if hasattr(self.elementDict[name].parent, "getName") else self.elementDict[name].parent.name) not in self.canvasParents \
                and self.elementDict[name].parent.type == "DirectScrolledList":
                    self.elementDict[name].parent.element.removeItem(workOn)

                # Check if our parent is a custom widget
                if self.elementDict[name].parent is not None \
                and isinstance(self.elementDict[name].parent, ElementInfo) \
                and self.customWidgetsHandler.getWidget(self.elementDict[name].parent.type) is not None:
                    widget = self.customWidgetsHandler.getWidget(self.elementDict[name].parent.type)
                    if widget.removeItemFunction is not None:
                        # call custom widget remove function
                        try:
                            getattr(self.elementDict[name].parent.element, widget.removeItemFunction)(workOn)
                        except:
                            try:
                                getattr(self.elementDict[name].parent.element, widget.removeItemFunction)()
                            except Exception as e:
                                logging.error("Error while calling remove item function {} of item {}".format(widget.removeItemFunction, name))
                                logging.exception(e)
                del self.elementDict[name]
        try:
            workOn.stash()
        except Exception as e:
            print(e)

        #workOn.destroy()

        # cleanup
        for key, value in self.elementDict.copy().items():
            if value is None or value.element.isEmpty() or value.element.isStashed():
                del self.elementDict[key]

        if selectEditor:
            self.selectElement(self.visualEditorInfo)
        self.fixElementSortAll()
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

    def getMaxSort(self, elementInfo):
        """Returns the next sort value of the parent of the given "child" element"""
        children = list(elementInfo.element.getParent().getChildren().getPaths())
        if elementInfo.parent is None:
            children = children[9:]
        return len(children)+1

    def fixElementSortAll(self):
        fixedParents = []
        for name, elementInfo in self.elementDict.items():
            if elementInfo.parent in fixedParents:
                continue
            fixedParents.append(elementInfo.parent)

            children = list(elementInfo.element.getParent().getChildren().getPaths())
            if elementInfo.parent is None:
                children = children[9:]

            #sort = len(children)
            sort = 1
            for child in children:
                child.reparentTo(child.getParent(), sort)
                sort += 1

    def moveElementInStructure(self, direction=1, childElementInfo=None):
        # make sure the sort values of all elements are correct
        self.fixElementSortAll()

        workOn = None
        if childElementInfo is not None:
            workOn = childElementInfo
        elif self.selectedElement is not None:
            workOn = self.selectedElement
        else:
            return

        parent = workOn.element.getParent()
        workOnParent = self.getElementInfo(parent)
        #self.getElementSort(workOn)
        newSort = max(0, workOn.element.getSort()+direction)

        self.reparentElement(workOn, workOnParent, newSort)

        # make sure the sort is correct afterward
        self.fixElementSortAll()


    def reparentElement(self, childElementInfo=None, parentElementInfo=None, sortInParent=0):
        workOn = None
        if childElementInfo is not None:
            workOn = childElementInfo.element
        elif self.selectedElement is not None:
            workOn = self.selectedElement.element
        else:
            return

        workOnParent = None
        if parentElementInfo is not None:
            workOnParent = parentElementInfo.element
        else:
            workOnParent = workOn.getParent()

        workOn.reparentTo(workOnParent, sortInParent)

        base.messenger.send("refreshStructureTree")

        #TODO: Drag and drop in the strucutre view?
        #TODO: Up/Down pgup/gpdown to move selected element up or down in the tree

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

    def getElementInfo(self, nameOrElement):
        """Returns the element info for the given GUI ID or GUI element or
        None if it is not in the dictionary"""
        if nameOrElement in self.elementDict:
            return self.elementDict[nameOrElement]
        elif type(nameOrElement) == str:
            logging.error(f"couldn't find element info for GUI ID {nameOrElement}")
            return None
        else:
            element = self.__findFirstGUIElement(nameOrElement)
            if element is None:
                logging.error(f"couldn't find element info for element {nameOrElement}")
            return element

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

    def cutElement(self):
        if self.selectedElement is None: return
        self.theCutElement = self.selectedElement

    def pasteElement(self):
        # check if we want to have a cut or copy action

        if self.theCutElement is not None:
            # CUT
            # the previous action was a cutting action, so we don't want to copy
            return self.pasteCutElement()

        if self.copiedElement is None: return

        # COPY
        # stores the ids of the source elements that have been copied already
        self.copyCreatedElementIds = []
        self.newElementIds = []
        self.__copyBranch(self.copiedElement, self.selectedElement)

        if self.newElementIds == []:
            return
        e = self.elementDict[self.newElementIds[0]]
        base.messenger.send("addToKillRing",
            [e, "copy", "element", (self.newElementIds[0], e), None])

    def __copyBranch(self, startObject, parent=None):
        if startObject == parent: return
        for elementName, elementInfo in self.elementDict.copy().items():
            if elementInfo.element.guiId in self.copyCreatedElementIds: continue
            if elementInfo.parent == startObject or elementInfo == startObject:
                newElement = self.__createControl(elementInfo.type)
                if type(newElement) is tuple:
                    newElement = newElement[0]
                self.newElementIds.append(newElement.element.guiId)
                self.copyCreatedElementIds.append(elementInfo.element.guiId)
                if parent is not None:
                    newParent = None
                    if type(parent) is ElementInfo:
                        newParent = self.getEditorRootCanvas().find("**/{}".format(parent.element.getName()))
                    else:
                        newParent = self.getEditorRootCanvas().find("**/{}".format(parent.getName()))
                    self.setParentOfElement(newElement.element, newParent)
                    newElement.element.reparentTo(newParent)
                self.__copyOptions(elementInfo, newElement, parent is not None)

                self.__copyBranch(elementInfo, newElement.element)

    def pasteCutElement(self):
        if self.theCutElement is None: return
        if self.theCutElement == self.selectedElement: return

        parent = self.selectedElement
        if self.selectedElement is None:
            parent = editorFrame

        self.theCutElement.element.reparentTo(self.selectedElement.element)

        for elementName, elementInfo in self.elementDict.items():
            if elementInfo == self.theCutElement:
                self.elementDict[elementName].parent = self.selectedElement

        self.theCutElement = None

        base.messenger.send("refreshStructureTree")

    def copyOptions(self):
        if self.selectedElement is None: return
        self.copyOptionsElementInfo = self.selectedElement

    def pasteOptions(self):
        if self.copyOptionsElementInfo is None: return
        self.__copyOptions(self.copyOptionsElementInfo, self.selectedElement)

    def __copyOptions(self, elementInfoFrom, elementInfoTo, copyPosition=False):
        elementFrom = elementInfoFrom.element
        elementTo = elementInfoTo.element
        if elementFrom is None or elementTo is None: return
        try:
            # store for undo
            oldOptions = elementTo._optionInfo.copy()
            oldOptions["hpr"] = elementTo.getHpr()
            oldOptions["scale"] = elementTo.getScale()
            oldOptions["pos"] = elementTo.getPos()
            oldOptions["text_fg"] = None

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

                for compName in elementTo.components():
                    comp = elementTo.component(compName)
                    if hasattr(comp, "fg"):
                        oldOptions["text_fg"] = comp.fg
                        break

                elementTo["text_fg"] = text_fg
            elementTo.setHpr(hpr)
            elementTo.setScale(scale)

            # store for redo
            newOptions = elementTo._optionInfo.copy()
            newOptions["hpr"] = elementTo.getHpr()
            newOptions["scale"] = elementTo.getScale()
            newOptions["pos"] = elementTo.getPos()
            newOptions["text_fg"] = text_fg

            if copyPosition:
                elementTo.setPos(pos)
                newOptions["pos"] = elementTo.getPos()

            # make sure the changed values are set correct
            for key, changed in elementInfoFrom.valueHasChanged.items():
                p = ["pos"] if copyPosition else []
                if key in ["hpr", "scale"] + p:
                    continue
                elementInfoTo.valueHasChanged[key] = changed

            base.messenger.send("addToKillRing",
                [elementTo, "copy", "properties", oldOptions, newOptions])
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
        allWidgetDefinitions = {
            **WidgetDefinition.DEFINITIONS,
            **self.customWidgetsHandler.getCustomWidgetDefinitions()}
        ExporterProject(
            os.path.join(self.lastDirPath, self.lastFileNameWOExtension + ".json"),
            self.elementDict,
            self.getEditorFrame,
            self.getAllEditorPlacers,
            allWidgetDefinitions,
            not self.editorFrame.visEditorInAspect2D,
            tooltip=self.tt)

    def export(self):
        self.selectElement(self.visualEditorInfo)
        allWidgetDefinitions = {
            **WidgetDefinition.DEFINITIONS,
            **self.customWidgetsHandler.getCustomWidgetDefinitions()}
        ExporterPy(
            os.path.join(self.lastDirPath, self.lastFileNameWOExtension + ".py"),
            self.elementDict,
            self.customWidgetsHandler,
            self.getEditorFrame,
            self.getAllEditorPlacers,
            allWidgetDefinitions,
            self.tt,
            not self.editorFrame.visEditorInAspect2D)

    def load(self):
        self.selectElement(self.visualEditorInfo)

        allWidgetDefinitions = {
            **WidgetDefinition.DEFINITIONS,
            **self.customWidgetsHandler.getCustomWidgetDefinitions()}
        projectLoader = ProjectLoader(
            os.path.join(self.lastDirPath, self.lastFileNameWOExtension + ".json"),
            self.visualEditorInfo,
            self.elementHandler,
            self.customWidgetsHandler,
            self.getEditorPlacer,
            allWidgetDefinitions,
            False,
            self.tt,
            self.new)

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

        self.dlgSettings = SettingsDialog(base.pixel2d)

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
        self.dlgSettings.spinAutosaveDealy.setValue(ConfigVariableInt("autosave-delay", 60).getValue())

        paths = ""
        pathsConfig = ConfigVariableSearchPath("custom-model-path", "").getValue()
        for path in pathsConfig.getDirectories():
            if paths != "":
                paths = "{}:{}".format(paths, path)
            else:
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

                line = "autosave-delay {}\n".format(self.dlgSettings.spinAutosaveDealy.get())
                prcFile.write(line)
                loadPrcFileData("", line)

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
\1bold\1Ctrl-Z  \2 - Undo
\1bold\1Ctrl-Y  \2 - Redo
\1bold\1Ctrl-Shift-Y\2 - Cycle through redos

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
