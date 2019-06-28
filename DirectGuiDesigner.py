#!/usr/bin/env python
# -*- coding: utf-8 -*-

from direct.showbase.ShowBase import ShowBase

from panda3d.core import Point3, Vec3, loadPrcFileData, WindowProperties

from direct.gui import DirectGuiGlobals as DGG

from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectScrolledFrame import DirectScrolledFrame
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
    #show-frame-rate-meter #t
    window-title DirectGUI Designer
    """)

class DirectGuiDesigner(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        wp = WindowProperties()
        wp.setIconFilename("icons/DirectGuiDesigner.ico")
        base.win.requestProperties(wp)

        self.selectedElement = None
        # dict of all elements in the visual editor
        # Key = guiID; Value = [element, properties]
        self.elementDict = {}

        self.dlgHelp = None
        self.dlgQuit = None

        # Delay initial setup by 0.5s to let the window set it's final
        # size and we'll be able to use the screen corner/edge variables
        taskMgr.doMethodLater(0.5, self.setupGui, "delayed setup", extraArgs = [])

    def setupGui(self):
        self.screenWidth = abs(base.a2dRight) + abs(base.a2dLeft)
        self.leftEdge = -(self.screenWidth * (2.0 / 3.0))
        self.rightEdge = self.screenWidth * (1.0 / 3.0)

        self.tt = Tooltip()

        # 3/4 wide editor content frame
        color = (
            (0.8, 0.8, 0.8, 1), # Normal
            (0.9, 0.9, 1, 1), # Click
            (0.8, 0.8, 1, 1), # Hover
            (0.5, 0.5, 0.5, 1)) # Disabled
        self.visualEditor = DirectScrolledFrame(
            frameColor=(0, 0, 0, 0),
            frameSize=(0,self.screenWidth*(0.75),
                base.a2dBottom,base.a2dTop-0.1),
            pos=(self.screenWidth*(0.25), 0, 0),
            canvasSize=(-2, 2, -2, 2),
            scrollBarWidth=0.04,
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
            frameSize=(-self.screenWidth/8, self.screenWidth/8, base.a2dBottom, base.a2dTop),
            pos=(self.screenWidth/8,0,0))
        self.toolsFrame.reparentTo(base.a2dLeftCenter)

        self.toolFrameHeight = (abs(base.a2dBottom) + abs(base.a2dTop)) / 3

        self.nextToolFrameY = base.a2dTop

        self.toolboxFrame = DirectGuiDesignerToolbox(self.toolsFrame, self.nextToolFrameY, self.toolFrameHeight)
        self.nextToolFrameY -= self.toolFrameHeight-0.02

        self.propertiesFrame = DirectGuiDesignerProperties(self.toolsFrame, self.nextToolFrameY, self.toolFrameHeight, self.visualEditor)
        self.propertiesEditor(self.visualEditorInfo)
        self.nextToolFrameY -= self.toolFrameHeight-0.02

        self.structureFrame = DirectGuiDesignerStructure(self.toolsFrame, self.nextToolFrameY, self.toolFrameHeight, self.visualEditor, self.elementDict, self.selectedElement)

        self.elementHandler = DirectGuiDesignerElementHandler(self.propertiesFrame, self.visualEditor)

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
        self.accept("control-delete", self.removeElement)
        self.accept("control-g", self.menuBar.cb_grid.commandFunc, extraArgs=[None])
        self.accept("control-h", self.toggleElementVisibility)
        self.accept("f1", self.showHelp)

        self.accept("arrow-left", print, extraArgs=["Test"])

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

        #base.exitFunc = self.quitApp
        """

        #TODO: Why does this break scaling of everything in the window if the size changes?
        self.accept('window-event', self.windowEventHandler)

    def windowEventHandler( self, window=None ):
        if window is not None: # window is none if panda3d is not started
            wp=window.getProperties()
            newsize=[wp.getXSize(),wp.getYSize()]
            print(newsize)"""

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
        if elementInfo is None:
            print("Element can't be selected")
            return
        self.refreshProperties(elementInfo)
        if elementInfo.element is self.visualEditor:
            # we don't need to select the editor itself
            self.selectedElement = None
            base.messenger.send("refreshStructureTree")
            return
        if elementInfo.element is None:
            return
        self.selectedElement = elementInfo
        elementInfo.element.setColorScale(1,1,0,1)
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

    def dragTask(self, t):
        mwn = base.mouseWatcherNode
        if mwn.hasMouse():
            vMouse2render2d = Point3(mwn.getMouse()[0], 0, mwn.getMouse()[1])
            newPos = vMouse2render2d + t.editVec
            t.elementInfo.element.setPos(render2d, newPos)

            if self.snapToGrid:
                newPos = t.elementInfo.element.getPos()
                newPos.set(
                    ROUND_TO(newPos[0], self.gridSpacing),
                    ROUND_TO(newPos[1], self.gridSpacing),
                    ROUND_TO(newPos[2], self.gridSpacing))
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
        self.refreshProperties(t.elementInfo)

    def removeElement(self, element=None):
        #TODO: If element was added to a scrolledList this scrolled list needs to remove the element with removeItem prior to deletion
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
        DirectGuiDesignerExporterProject(self.elementDict, self.visualEditor)

    def export(self):
        DirectGuiDesignerExporterPy(self.elementDict, self.visualEditor)

    def load(self):
        projectLoader = DirectGuiDesignerLoaderProject(self.visualEditorInfo, self.elementHandler)
        self.elementDict = projectLoader.get()

    def hideHelp(self, args):
        self.dlgHelp.destroy()
        self.dlgHelpShadow.destroy()
        self.dlgHelp = None

    def __quit(self, selection):
        if selection == 1:
            quit()
        else:
            self.dlgQuit.destroy()
            self.dlgQuitShadow.destroy()
            self.dlgQuit = None

    def quitApp(self):
        if self.dlgQuit is not None: return
        self.dlgQuit = OkCancelDialog(
            text="Really Quit?",
            state=DGG.NORMAL,
            relief=DGG.RIDGE,
            frameColor=(1,1,1,1),
            sortOrder=1,
            button_relief=DGG.FLAT,
            button_frameColor=(0.8, 0.8, 0.8, 1),
            command=self.__quit)
        self.dlgQuitShadow = DirectFrame(
            pos=(0.025, 0, -0.025),
            sortOrder=0,
            frameColor=(0,0,0,0.5),
            frameSize=self.dlgQuit.bounds)

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

F1 - Show this help Dialog


LMB = Left Mouse Button | RMB = Right Mouse Button | MMB = Middle Mouse Button
"""
        self.dlgHelp = OkDialog(
            text=text,
            state=DGG.NORMAL,
            relief=DGG.RIDGE,
            frameColor=(1,1,1,1),
            sortOrder=1,
            button_relief=DGG.FLAT,
            button_frameColor=(0.8, 0.8, 0.8, 1),
            command=self.hideHelp)
        self.dlgHelpShadow = DirectFrame(
            pos=(0.025, 0, -0.025),
            sortOrder=0,
            frameColor=(0,0,0,0.5),
            frameSize=self.dlgHelp.bounds)

designer=DirectGuiDesigner()
designer.run()
