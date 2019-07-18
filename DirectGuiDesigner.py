#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import platform
import logging
import tempfile

from direct.showbase.ShowBase import ShowBase

from panda3d.core import Point3, Vec3, loadPrcFileData, WindowProperties

from direct.gui import DirectGuiGlobals as DGG

from direct.gui.DirectFrame import DirectFrame
#from direct.gui.DirectScrolledFrame import DirectScrolledFrame
from directGuiOverrides.DirectScrolledFrame import DirectScrolledFrame
from direct.gui.DirectDialog import OkDialog
from direct.gui.DirectDialog import OkCancelDialog

from direct.directtools.DirectGrid import DirectGrid
from direct.directtools.DirectUtil import ROUND_TO

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
from DirectGuiDesignerTooltip import Tooltip


loadPrcFileData(
    "",
    """
    win-size 1920 1080
    textures-power-2 none
    fullscreen #f
    window-title DirectGUI Designer
    #show-frame-rate-meter #t
    #want-pstats #t
    """)

class DirectGuiDesigner(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

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

        self.dlgQuit = None
        self.dlgQuitShadow = None

        self.dlgWarning = None
        self.dlgWarningShadow = None

        self.dlgInfo = None
        self.dlgInfoShadow = None

        # Delay initial setup by 0.5s to let the window set it's final
        # size and we'll be able to use the screen corner/edge variables
        taskMgr.doMethodLater(0.5, self.setupGui, "delayed setup", extraArgs = [])

    def setupGui(self):
        self.screenWidth = abs(base.a2dRight) + abs(base.a2dLeft)
        self.screenWidthPx = base.getSize()[0]
        self.screenHeightPx = base.getSize()[1]
        self.leftEdge = -(self.screenWidth * (2.0 / 3.0))
        self.rightEdge = self.screenWidth * (1.0 / 3.0)

        self.tt = Tooltip()

        # 3/4 wide editor content frame
        color = (
            (0.8, 0.8, 0.8, 1), # Normal
            (0.9, 0.9, 1, 1), # Click
            (0.8, 0.8, 1, 1), # Hover
            (0.5, 0.5, 0.5, 1)) # Disabled
        # respect menu bar
        topMargin=48 / self.screenHeightPx * 2
        self.visualEditor = DirectScrolledFrame(
            frameColor=(0, 0, 0, 0),
            frameSize=(0,self.screenWidth*(0.75),
                base.a2dBottom,base.a2dTop-topMargin),
            pos=(self.screenWidth*(0.25), 0, 0),
            canvasSize=(-2, 2, -2, 2),
            scrollBarWidth=self.calcScrollBarWidth(),
            verticalScroll_value=0.5,
            horizontalScroll_value=0.5,
            verticalScroll_thumb_relief=DGG.FLAT,
            verticalScroll_incButton_relief=DGG.FLAT,
            verticalScroll_decButton_relief=DGG.FLAT,
            verticalScroll_thumb_frameColor=color,
            verticalScroll_incButton_frameColor=color,
            verticalScroll_decButton_frameColor=color,
            verticalScroll_resizeThumb=True,
            horizontalScroll_thumb_relief=DGG.FLAT,
            horizontalScroll_incButton_relief=DGG.FLAT,
            horizontalScroll_decButton_relief=DGG.FLAT,
            horizontalScroll_thumb_frameColor=color,
            horizontalScroll_incButton_frameColor=color,
            horizontalScroll_decButton_frameColor=color,
            horizontalScroll_resizeThumb=True,
            parent=base.a2dLeftCenter)

        self.visualEditorInfo = ElementInfo(self.visualEditor, "Editor")

        self.grid = DirectGrid(gridSize=50.0, gridSpacing=0.05,parent=self.visualEditor.getCanvas())
        self.grid.setP(90)
        self.grid.snapMarker.hide()

        self.snapToGrid = not self.grid.isHidden()
        self.gridSpacing = 0.05

        self.menuBar = DirectGuiDesignerMenuBar(self.tt, self.grid)

        # 1/4 wide toolbox, properties and structure frame
        self.toolsFrame = DirectFrame(
            frameColor=(0.25, 0.25, 0.25, 1),
            frameSize=(0, self.screenWidthPx/4, -self.screenHeightPx, 0),
            pos=(self.screenWidth/8,0,0),
            parent=base.pixel2d)

        self.toolFrameHeight = -self.screenHeightPx / 3

        self.nextToolFrameY = 0

        self.toolboxFrame = DirectGuiDesignerToolbox(self.toolsFrame, self.nextToolFrameY, self.toolFrameHeight)
        self.nextToolFrameY += self.toolFrameHeight

        self.propertiesFrame = DirectGuiDesignerProperties(self.toolsFrame, self.nextToolFrameY, self.toolFrameHeight, self.visualEditor)
        self.propertiesEditor(self.visualEditorInfo)
        self.nextToolFrameY += self.toolFrameHeight

        self.structureFrame = DirectGuiDesignerStructure(self.toolsFrame, self.nextToolFrameY, self.toolFrameHeight, self.visualEditor, self.elementDict, self.selectedElement)

        self.elementHandler = DirectGuiDesignerElementHandler(self.propertiesFrame, self.visualEditor)

        self.registerKeyboardEvents()
        self.accept("unregisterKeyboardEvents", self.ignoreKeyboardEvents)
        self.accept("reregisterKeyboardEvents", self.registerKeyboardEvents)

        self.accept("createControl", self.__createControl)
        self.accept("newProject", self.new)
        self.accept("saveProject", self.save)
        self.accept("exportProject", self.export)
        self.accept("loadProject", self.load)
        self.accept("refreshStructureTree", self.__refreshStructureTree)
        self.accept("selectElement", self.selectElement)
        self.accept("removeElement", self.removeElement)
        self.accept("toggleElementVisibility", self.toggleElementVisibility)
        self.accept("setParentOfElement", self.setParentOfElement)
        self.accept("toggleGrid", self.toggleGrid)
        self.accept("showHelp", self.showHelp)
        self.accept("quitApp", self.quitApp)

        self.accept("setName", self.setName)
        self.accept("setCommand", self.setCommand)
        self.accept("setExtraArgs", self.setExtraArgs)

        self.accept("dragStart", self.dragStart)
        self.accept("dragStop", self.dragStop)

        self.accept("showWarning", self.showWarning)
        self.accept("showInfo", self.showInfo)

        self.screenSize = base.getSize()
        self.accept('window-event', self.windowEventHandler)

        sys.excepthook = self.excHandler

        self.win.setCloseRequestEvent("quitApp")

        tmpPath = os.path.join(tempfile.gettempdir(), "DGDExceptionSave.json")
        if os.path.exists(tmpPath):
            logging.info("Loading crash session file {}".format(tmpPath))
            projectLoader = DirectGuiDesignerLoaderProject(self.visualEditorInfo, self.elementHandler, True)
            self.elementDict = projectLoader.get()
            base.messenger.send("refreshStructureTree")
            base.messenger.send("showInfo", ["Loaded previously crashed session!"])
            os.remove(tmpPath)
            logging.info("Removed crash session file")

    def excHandler(self, ex_type, ex_value, ex_traceback):
        logging.error("Unhandled exception", exc_info=(ex_type, ex_value, ex_traceback))

        DirectGuiDesignerExporterProject(self.elementDict)

    def registerKeyboardEvents(self):
        self.accept("escape", self.selectElement, extraArgs=[self.visualEditorInfo, None])
        self.accept("mouse3", self.selectElement, extraArgs=[self.visualEditorInfo, None])
        self.accept("mouse2", self.dragEditorFrame, extraArgs=[True])
        self.accept("mouse2-up", self.dragEditorFrame, extraArgs=[False])
        self.accept("wheel_up", self.zoom, extraArgs=[.1])
        self.accept("wheel_down", self.zoom, extraArgs=[-.1])

        self.accept("control-n", self.new)
        self.accept("control-s", self.save)
        self.accept("control-e", self.export)
        self.accept("control-o", self.load)
        self.accept("control-q", self.quitApp)
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

    def calcScrollBarWidth(self):
        widthInPx = 20
        screenWidthPx = base.getSize()[0]
        screenWidth = abs(base.a2dRight) + abs(base.a2dLeft)

        return screenWidth / (screenWidthPx / widthInPx)

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
            self.toolsFrame["frameSize"] = (0, self.screenWidthPx/4, -self.screenHeightPx, 0)
            self.toolsFrame.setPos(0,0,0)

            topMargin=48 / self.screenHeightPx * 2
            self.visualEditor["frameSize"] = (0,self.screenWidth*(0.75),base.a2dBottom,base.a2dTop-topMargin)
            self.visualEditor.setPos(self.screenWidth*(0.25), 0, 0)
            self.visualEditor["scrollBarWidth"] = self.calcScrollBarWidth()

            self.menuBar.resizeFrame()

            self.toolFrameHeight = -self.screenHeightPx / 3
            self.nextToolFrameY = 0
            self.toolboxFrame.resizeFrame(self.nextToolFrameY, self.toolFrameHeight)
            self.nextToolFrameY += self.toolFrameHeight
            self.propertiesFrame.resizeFrame(self.nextToolFrameY, self.toolFrameHeight)
            self.nextToolFrameY += self.toolFrameHeight
            self.structureFrame.resizeFrame(self.nextToolFrameY, self.toolFrameHeight)

            if self.dlgHelp is not None:
                self.dlgHelp.setPos(base.getSize()[0]/2, 0, -base.getSize()[1]/2)
                self.dlgHelpShadow.setPos(base.getSize()[0]/2 + 10, 0, -base.getSize()[1]/2 - 10)
            if self.dlgQuit is not None:
                self.dlgQuit.setPos(base.getSize()[0]/2, 0, -base.getSize()[1]/2)
                self.dlgQuitShadow["frameSize"] = (0, base.getSize()[0], -base.getSize()[1], 0)

    def propertiesEditor(self, elementInfo):
        self.propertiesFrame.clearPropertySelection()
        self.propertiesFrame.propertyList["frameColor"] = True
        self.propertiesFrame.propertyList["canvasSize"] = True
        self.propertiesFrame.setupProperties("Editor Properties", elementInfo, self.elementDict)

    def __refreshStructureTree(self):
        self.structureFrame.refreshStructureTree(self.elementDict, self.selectedElement)

    def __createControl(self, element):
        funcName = "create{}".format(element)
        if hasattr(self.elementHandler, funcName):
            parent = None
            if self.selectedElement is not None:
                parent = self.selectedElement.element
            elementInfo = getattr(self.elementHandler, funcName)(parent)
            if elementInfo is None: return
            if type(elementInfo) is tuple:
                if self.selectedElement is not None and self.selectedElement.type == "DirectScrolledList":
                    self.selectedElement.element.addItem(elementInfo[0].element)
                for entry in elementInfo:
                    if self.selectedElement is not None and entry.parent is None:
                        entry.parent = self.selectedElement
                    self.elementDict[entry.element.guiId] = entry
            else:
                if self.selectedElement is not None:
                    elementInfo.parent = self.selectedElement
                    if self.selectedElement.type == "DirectScrolledList":
                        self.selectedElement.element.addItem(elementInfo.element)
                self.elementDict[elementInfo.element.guiId] = elementInfo
            base.messenger.send("refreshStructureTree")

    def zoom(self, direction):
        if direction < 0 and self.visualEditor.getCanvas().getScale() > 0.5:
            self.visualEditor.getCanvas().setScale(self.visualEditor.getCanvas().getScale() + direction)
        elif direction > 0 and self.visualEditor.getCanvas().getScale() < 5.0:
            self.visualEditor.getCanvas().setScale(self.visualEditor.getCanvas().getScale() + direction)

    def selectElement(self, elementInfo, args=None):
        if self.selectedElement is not None:
            self.selectedElement.element.clearColorScale()
            self.ignoreKeyboardEvents()
            self.registerKeyboardEvents()
        if elementInfo is None:
            base.messenger.send("showWarning", ["Element can't be selected"])
            return
        if elementInfo.element is self.visualEditor:
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

    def dragEditorFrame(self, dragEnabled):
        taskMgr.remove("dragEditorFrameTask")
        mwn = base.mouseWatcherNode
        if dragEnabled:
            t = taskMgr.add(self.dragEditorFrameTask, "dragEditorFrameTask")
            t.vMouse2render2d = Point3(mwn.getMouse()[0], 0, mwn.getMouse()[1])

    def dragEditorFrameTask(self, t):
        mwn = base.mouseWatcherNode
        if mwn.hasMouse():
            vMouse2render2d = Point3(mwn.getMouse()[0], 0, mwn.getMouse()[1])
            moveVec = t.vMouse2render2d - vMouse2render2d
            t.vMouse2render2d = vMouse2render2d
            newValue = self.visualEditor["verticalScroll_value"] - moveVec.getZ()
            if newValue <= 1 and newValue >= 0:
                self.visualEditor["verticalScroll_value"] = newValue
            newValue = self.visualEditor["horizontalScroll_value"] + moveVec.getX()
            if newValue <= 1 and newValue >= 0:
                self.visualEditor["horizontalScroll_value"] = newValue
        return t.cont

    def refreshProperties(self, elementInfo):
        self.propertiesFrame.clear()
        propFuncName = "properties{}".format(elementInfo.type)
        if elementInfo.type == "Editor":
            getattr(self, propFuncName)(elementInfo)
        if hasattr(self.elementHandler, propFuncName):
            getattr(self.elementHandler, propFuncName)(elementInfo, self.elementDict)

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

            if self.snapToGrid and (t.mouseVec - vMouse2render2d).length() < 0.01:
                return t.cont

            t.elementInfo.element.setPos(render2d, newPos)

            if self.snapToGrid:
                newPos = t.elementInfo.element.getPos()
                modifier = 0.5
                if self.is_down(self.key_lcontrol) or self.is_down(self.key_rcontrol):
                    modifier = 0.25
                if self.is_down(self.key_lshift) or self.is_down(self.key_rshift):
                    modifier = 1
                newPos.set(
                    ROUND_TO(newPos[0], self.gridSpacing*modifier),
                    ROUND_TO(newPos[1], self.gridSpacing*modifier),
                    ROUND_TO(newPos[2], self.gridSpacing*modifier))
                t.elementInfo.element.setPos(newPos)

        return t.cont

    def dragStop(self, event):
        t = taskMgr.getTasksNamed("dragDropTask")[0]
        parent = t.elementInfo.element.getParent()
        pos = t.elementInfo.element.getPos(self.visualEditor.getCanvas())

        if pos.x < self.visualEditor["canvasSize"][0]:
            t.elementInfo.element.setX(self.visualEditor.getCanvas(), self.visualEditor["canvasSize"][0])
        if pos.x > self.visualEditor["canvasSize"][1]:
            t.elementInfo.element.setX(self.visualEditor.getCanvas(), self.visualEditor["canvasSize"][1])
        if pos.z < self.visualEditor["canvasSize"][2]:
            t.elementInfo.element.setZ(self.visualEditor.getCanvas(), self.visualEditor["canvasSize"][2])
        if pos.z > self.visualEditor["canvasSize"][3]:
            t.elementInfo.element.setZ(self.visualEditor.getCanvas(), self.visualEditor["canvasSize"][3])
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

        if direction == "left":
            workOn.setX(workOn, -0.01*moverScaleX*speedMult)
        elif direction == "right":
            workOn.setX(workOn, 0.01*moverScaleX*speedMult)
        elif direction == "up":
            workOn.setZ(workOn, 0.01*moverScaleZ*speedMult)
        elif direction == "down":
            workOn.setZ(workOn, -0.01*moverScaleZ*speedMult)

    def removeElement(self, element=None):
        workOn = None
        selectEditor = False
        if element is not None:
            workOn = element
            if self.selectedElement is not None and element == self.selectedElement.element:
                selectEditor = True
                self.selectedElement = None
        elif self.selectedElement is not None:
            selectEditor = True
            workOn = self.selectedElement.element
            self.selectedElement = None
        else:
            return

        if not workOn.isEmpty():
            name = workOn.getName()
            if name in self.elementDict.keys():
                if self.elementDict[name].parent is not None and self.elementDict[name][0].parent.type == "DirectScrolledList":
                    self.elementDict[name].parent.element.removeItem(workOn)
                del self.elementDict[name]
            elif name.split("-")[1] in self.elementDict.keys():
                if self.elementDict[name.split("-")[1]].parent is not None and self.elementDict[name.split("-")[1]].parent.type == "DirectScrolledList":
                    self.elementDict[name.split("-")[1]].parent.element.removeItem(workOn)
                del self.elementDict[name.split("-")[1]]

        workOn.destroy()

        # cleanup
        for key, value in self.elementDict.copy().items():
            if value is None or value.element.isEmpty():
                del self.elementDict[key]

        if selectEditor:
            self.selectElement(self.visualEditorInfo)
        base.messenger.send("refreshStructureTree")

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
        if parent is self.visualEditor.getCanvas():
            self.elementDict[element.guiId].parent = None
        else:
            parentElement = None
            if parent.getName() in self.elementDict.keys():
                parentElement = self.elementDict[parent.getName()]
            elif len(parent.getName().split("-")) > 1 and parent.getName().split("-")[1] in self.elementDict.keys():
                parentElement = self.elementDict[parent.getName().split("-")[1]]
            else:
                # check if we can find an element as parent of the current NP
                # This happens for elements that have a canvas or other sub NPs
                parentElement = self.__findFirstGUIElement(parent)
            self.elementDict[element.guiId].parent = parentElement

    def toggleGrid(self, enable):
        if enable:
            self.grid.show()
            self.snapToGrid = True
        else:
            self.grid.hide()
            self.snapToGrid = False

    def new(self):
        for name, elementInfo in list(self.elementDict.items()):
            self.removeElement(elementInfo.element)
        self.selectedElement = None
        self.elementDict = {}

    def save(self):
        self.selectElement(self.visualEditorInfo)
        DirectGuiDesignerExporterProject(self.elementDict, self.visualEditor, self.tt)

    def export(self):
        self.selectElement(self.visualEditorInfo)
        DirectGuiDesignerExporterPy(self.elementDict, self.visualEditor, self.tt)

    def load(self):
        self.selectElement(self.visualEditorInfo)
        projectLoader = DirectGuiDesignerLoaderProject(self.visualEditorInfo, self.elementHandler, False, self.tt, self.new)
        self.elementDict = projectLoader.get()

    def __quit(self, selection):
        if selection == 1:
            self.userExit()
        else:
            self.dlgQuit.destroy()
            self.dlgQuitShadow.destroy()
            self.dlgQuit = None
            self.dlgQuitShadow = None

    def quitApp(self):
        if self.dlgQuit is not None: return
        self.dlgQuit = OkCancelDialog(
            text="Really Quit?",
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
            pos=(0.025, 0, -0.025),
            sortOrder=0,
            frameColor=(0,0,0,0.5),
            frameSize=(0, base.getSize()[0], -base.getSize()[1], 0),
            parent=base.pixel2d)

    def showHelp(self):
        if self.dlgHelp is not None: return

        text="""~~~Direct GUI Visual Editor Help~~~

LMB - Select an element / Press and drag to move element around
Esc - Deselect currently selected Element
RMB - Deselect currently selected Element
MMB - Move Editor Area

Mouse Wheel - Zoom

Ctrl-N - Create New GUI
Ctrl-S - Save as Project File
Ctrl-E - Export as Python File
Ctrl-O - Load Project File
Ctrl-Q - Quit Application
Ctrl-Del - Delete selected Element
Ctrl-H - Toggle selected Element visibility
Ctrl-G - Toggle grid and snap to grid

Arrow Keys - Move the selected Element (use Shift and Ctrl to change distance)

F1 - Show this help Dialog


LMB = Left Mouse Button | RMB = Right Mouse Button | MMB = Middle Mouse Button
"""
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
            pos=(base.getSize()[0]/2 + 10, 0, -base.getSize()[1]/2 - 10),
            sortOrder=0,
            frameColor=(0,0,0,0.5),
            frameSize=(self.dlgHelp.bounds[0]*300, self.dlgHelp.bounds[1]*300,
                       self.dlgHelp.bounds[2]*300, self.dlgHelp.bounds[3]*300),
            parent=base.pixel2d)

    def hideHelp(self, args):
        self.dlgHelp.destroy()
        self.dlgHelpShadow.destroy()
        self.dlgHelp = None
        self.dlgHelpShadow = None

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
            pos=(0,0,0),
            sortOrder=0,
            frameColor=(0.25,0,0,0.5),
            frameSize=(0, base.getSize()[0], -base.getSize()[1], 0),
            parent=base.pixel2d)

    def hideWarning(self, args):
        self.dlgWarning.destroy()
        self.dlgWarningShadow.destroy()
        self.dlgWarning = None
        self.dlgWarningShadow = None

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
            pos=(0,0,0),
            sortOrder=0,
            frameColor=(0.15,0.15,0.25,0.5),
            frameSize=(0, base.getSize()[0], -base.getSize()[1], 0),
            parent=base.pixel2d)

    def hideInfo(self, args):
        self.dlgInfo.destroy()
        self.dlgInfoShadow.destroy()
        self.dlgInfo = None
        self.dlgInfoShadow = None

designer=DirectGuiDesigner()
designer.run()
