import logging

from panda3d.core import NodePath

from direct.showbase.DirectObject import DirectObject

from direct.gui import DirectGuiGlobals as DGG

from DirectGuiExtension import DirectGuiHelper as DGH

from DirectGuiExtension.DirectTooltip import DirectTooltip

from DirectGuiExtension.DirectBoxSizer import DirectBoxSizer
from DirectGuiExtension.DirectAutoSizer import DirectAutoSizer
from DirectGuiExtension.DirectSplitFrame import DirectSplitFrame

from DirectGuiDesigner.panels.CanvasPanel import CanvasPanel
from DirectGuiDesigner.panels.MenuBar import MenuBar
from DirectGuiDesigner.panels.ToolBar import ToolBar
from DirectGuiDesigner.panels.ToolboxPanel import ToolboxPanel
from DirectGuiDesigner.panels.PropertiesPanel import PropertiesPanel
from DirectGuiDesigner.panels.StructurePanel import StructurePanel

class MainView(DirectObject):
    def __init__(self, core, tooltip, parent):
        logging.debug("Setup GUI")

        self.parent = parent

        splitterWidth = 8
        self.menuBarHeight = 24
        self.toolBarHeight = 48

        #self.screenWidth = abs(base.a2dRight) + abs(base.a2dLeft)
        #self.screenWidthPx = base.getSize()[0]
        #self.screenHeightPx = base.getSize()[1]
        #self.leftEdge = -(self.screenWidth * (2.0 / 3.0))
        #self.rightEdge = self.screenWidth * (1.0 / 3.0)

        #self.screenSize = base.getSize()

        #
        # LAYOUT SETUP
        #

        # the box everything get's added to
        self.mainBox = DirectBoxSizer(
            frameColor=(0,0,0,0),
            state=DGG.DISABLED,
            orientation=DGG.VERTICAL,
            autoUpdateFrameSize=False)

        # our root element for the main box
        self.mainSizer = DirectAutoSizer(
            frameColor=(0,0,0,0),
            parent=parent,
            child=self.mainBox,
            childUpdateSizeFunc=self.mainBox.refresh
            )

        # our menu bar
        self.menuBarSizer = DirectAutoSizer(
            updateOnWindowResize=False,
            frameColor=(0,0,0,0),
            parent=self.mainBox,
            extendVertical=False)

        # our tool bar
        self.toolBarSizer = DirectAutoSizer(
            updateOnWindowResize=False,
            frameColor=(0,0,0,0),
            parent=self.mainBox,
            extendVertical=False)

        # the splitter separating the the panels from the main content area
        splitterPos = 0
        if type(self.parent) is NodePath:
            splitterPos = -base.get_size()[0] / 3
        else:
            splitterPos = -parent["frameSize"][1] / 3

        self.mainSplitter = DirectSplitFrame(
            frameSize=self.get_main_splitter_size(),
            firstFrameMinSize=100,
            secondFrameMinSize=100,
            splitterWidth=splitterWidth,
            splitterPos=splitterPos)
        self.mainSplitter["frameColor"] = (0,0,0,0)
        self.mainSplitter.firstFrame["frameColor"] = (0,0,0,0)
        self.mainSplitter.secondFrame["frameColor"] = (0,0,0,0)

        # The sizer which makes sure our splitter is filling up
        self.mainSplitSizer = DirectAutoSizer(
            updateOnWindowResize=False,
            frameColor=(0,0,0,0),
            parent=self.mainBox,
            child=self.mainSplitter,
            parentGetSizeFunction=self.get_main_splitter_size,
            childUpdateSizeFunc=self.mainSplitter.refresh,
            )

        # The first splitter dividing the sidebar on the left
        self.sidebarSplitterA = DirectSplitFrame(
            orientation=DGG.VERTICAL,
            frameSize=(0,DGH.getRealWidth(self.mainSplitter.firstFrame),0,DGH.getRealHeight(self.mainSplitter.firstFrame)),
            firstFrameMinSize=40,
            secondFrameMinSize=20,
            splitterWidth=splitterWidth,
            splitterPos=DGH.getRealHeight(self.mainSplitter) / 3 * 2,
            pixel2d=True)

        # The sizer which makes sure our first part sidebar is filling up
        self.sideSplitSizerA = DirectAutoSizer(
            updateOnWindowResize=False,
            frameColor=(0,0,0,0),
            parent=self.mainSplitter.firstFrame,
            child=self.sidebarSplitterA,
            childUpdateSizeFunc=self.sidebarSplitterA.refresh
            )

        # The second splitter dividing the sidebar on the left
        self.sidebarSplitterB = DirectSplitFrame(
            orientation=DGG.VERTICAL,
            frameSize=(0,DGH.getRealWidth(self.sidebarSplitterA.firstFrame),0,DGH.getRealHeight(self.sidebarSplitterA.firstFrame)),
            firstFrameMinSize=20,
            secondFrameMinSize=20,
            splitterWidth=splitterWidth)

        # The sizer which makes sure our second part sidebar is filling up
        self.sideSplitSizerB = DirectAutoSizer(
            updateOnWindowResize=False,
            frameColor=(0,0,0,0),
            parent=self.sidebarSplitterA.secondFrame,
            child=self.sidebarSplitterB,
            childUpdateSizeFunc=self.sidebarSplitterB.refresh
            )

        self.mainBox.addItem(
            self.menuBarSizer,
            updateFunc=self.menuBarSizer.refresh,
            skipRefresh=True)
        self.mainBox.addItem(
            self.toolBarSizer,
            updateFunc=self.toolBarSizer.refresh,
            skipRefresh=True)
        self.mainBox.addItem(
            self.mainSplitSizer,
            updateFunc=self.mainSplitSizer.refresh,
            skipRefresh=True)

        #
        # CONTENT SETUP
        #
        self.editorFrame = CanvasPanel(self.mainSplitter.secondFrame)

        self.menuBar = MenuBar(self.editorFrame.grid)
        self.menuBarSizer.setChild(self.menuBar.menuBar)
        self.menuBarSizer["childUpdateSizeFunc"] = self.menuBar.menuBar.refresh

        self.toolBar = ToolBar(tooltip, self.editorFrame.grid)
        self.toolBarSizer.setChild(self.toolBar.toolBar)
        self.toolBarSizer["childUpdateSizeFunc"] = self.toolBar.toolBar.refresh

        # TOOLBOX
        self.toolboxFrame = ToolboxPanel(
            self.sidebarSplitterA.firstFrame)
        self.sidebarSplitterA["firstFrameUpdateSizeFunc"]=self.toolboxFrame.resizeFrame

        # update for second part sidebar size
        self.sidebarSplitterA["secondFrameUpdateSizeFunc"] = self.sideSplitSizerB.refresh

        # PROPERTIES EDITOR
        self.propertiesFrame = PropertiesPanel(
            self.sidebarSplitterB.firstFrame,
            self.getEditorRootCanvas,
            self.getEditorPlacer,
            tooltip)
        self.sidebarSplitterB["firstFrameUpdateSizeFunc"]=self.propertiesFrame.resizeFrame

        # STRUCTUR VIEWER
        self.structureFrame = StructurePanel(
            self.sidebarSplitterB.secondFrame,
            self.getEditorRootCanvas,
            core.elementDict,
            core.selectedElement)
        self.sidebarSplitterB["secondFrameUpdateSizeFunc"]=self.structureFrame.resizeFrame

        self.mainSplitter["firstFrameUpdateSizeFunc"] = self.sideSplitSizerA.refresh
        self.mainSplitter["secondFrameUpdateSizeFunc"] = self.editorFrame.resizeFrame

        self.mainBox.refresh()

    def get_main_splitter_size(self):
        size = [0,1,1,0]
        if type(self.parent) is NodePath:
            width = base.get_size()[0]
            height = base.get_size()[1]
        else:
            width = DGH.getRealWidth(self.parent)
            height = DGH.getRealHeight(self.parent)
        return (
            -width/2,
            width/2,
            0,
            height - self.menuBarHeight - self.toolBarHeight)

    def getEditorRootCanvas(self):
        """ returns the canvas element which acts as the root parent for all
        elements in the editors edit area """
        return self.editorFrame.getEditorRootCanvas()

    def getEditorPlacer(self, placerName):
        """Returns the nodepath to a specific placer in the editor. Those
        usually are located at the edges and corners of the editor and resemble
        the a2d* counterparts from the engine"""
        return self.editorFrame.getEditorPlacer(placerName)
