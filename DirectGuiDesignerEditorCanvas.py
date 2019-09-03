#!/usr/bin/env python
# -*- coding: utf-8 -*-

from panda3d.core import Point3

from direct.gui import DirectGuiGlobals as DGG

#from direct.gui.DirectScrolledFrame import DirectScrolledFrame
from directGuiOverrides.DirectScrolledFrame import DirectScrolledFrame

from direct.directtools.DirectGrid import DirectGrid

class DirectGuiDesignerEditorCanvas():
    def __init__(self):
        screenHeightPx = base.getSize()[1]
        screenWidth = abs(base.a2dRight) + abs(base.a2dLeft)
        color = (
            (0.8, 0.8, 0.8, 1), # Normal
            (0.9, 0.9, 1, 1), # Click
            (0.8, 0.8, 1, 1), # Hover
            (0.5, 0.5, 0.5, 1)) # Disabled
        # respect menu bar
        self.topMargin=48 / screenHeightPx * 2
        self.visualEditor = DirectScrolledFrame(
            frameColor=(0, 0, 0, 0),
            frameSize=(0,screenWidth*(0.75),
                base.a2dBottom,base.a2dTop-self.topMargin),
            pos=(screenWidth*(0.25), 0, 0),
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
        self.currentVisEditorParent = base.a2dLeftCenter
        self.visEditorInAspect2D = True

        self.grid = DirectGrid(gridSize=50.0, gridSpacing=0.05,parent=self.visualEditor.getCanvas())
        self.grid.setP(90)
        self.grid.snapMarker.hide()

        self.snapToGrid = not self.grid.isHidden()

    def setElementHandler(self, elementHandler):
        self.elementHandler = elementHandler

    def toggleVisualEditorParent(self):
        screenWidthPx = base.getSize()[0]
        screenHeightPx = base.getSize()[1]
        screenWidth = abs(base.a2dRight) + abs(base.a2dLeft)
        if self.currentVisEditorParent == base.a2dLeftCenter:
            # change to pixel2d
            self.visualEditor["frameSize"] = (0,screenWidthPx*0.75,-screenHeightPx,-48)
            self.visualEditor.setPos(screenWidthPx/4, 0, 0)
            self.visualEditor["scrollBarWidth"] = 20
            self.visualEditor["canvasSize"] = (0, 1920, -1080, 0)
            self.visualEditor.reparentTo(pixel2d)
            self.visualEditor.verticalScroll["value"] = 0
            self.visualEditor.horizontalScroll["value"] = 0
            self.currentVisEditorParent = base.pixel2d
            self.grid.setGridSpacing(20)
            self.grid.setGridSize(1920)
            self.visEditorInAspect2D = False
            self.elementHandler.setEditorParentType(self.visEditorInAspect2D)
            self.elementHandler.setEditorCenter((self.visualEditor.getWidth()/2, 0, -self.visualEditor.getHeight()/2))
        else:
            # change to aspect2d
            self.visualEditor["frameSize"] = (0,screenWidth*(0.75), base.a2dBottom,base.a2dTop-self.topMargin)
            self.visualEditor.setPos(screenWidth*(0.25), 0, 0)
            self.visualEditor["scrollBarWidth"] = self.calcScrollBarWidth()
            self.visualEditor["canvasSize"] = (-2, 2, -2, 2)
            self.visualEditor.reparentTo(base.a2dLeftCenter)
            self.visualEditor.verticalScroll["value"] = 0.5
            self.visualEditor.horizontalScroll["value"] = 0.5
            self.currentVisEditorParent = base.a2dLeftCenter
            self.grid.setGridSpacing(0.05)
            self.grid.setGridSize(50)
            self.visEditorInAspect2D = True
            self.elementHandler.setEditorParentType(self.visEditorInAspect2D)
            self.elementHandler.setEditorCenter((0, 0, 0))

    def calcScrollBarWidth(self):
        widthInPx = 20
        screenWidthPx = base.getSize()[0]
        screenWidth = abs(base.a2dRight) + abs(base.a2dLeft)

        return screenWidth / (screenWidthPx / widthInPx)


    def resizeFrame(self):
        screenWidth = abs(base.a2dRight) + abs(base.a2dLeft)
        screenWidthPx = base.getSize()[0]
        screenHeightPx = base.getSize()[1]
        self.topMargin=48 / screenHeightPx * 2
        if self.visEditorInAspect2D:
            self.visualEditor["frameSize"] = (0,screenWidth*(0.75),base.a2dBottom,base.a2dTop-self.topMargin)
            self.visualEditor.setPos(screenWidth*(0.25), 0, 0)
            self.visualEditor["scrollBarWidth"] = self.calcScrollBarWidth()
        else:
            self.visualEditor["frameSize"] = (0,screenWidthPx*0.75,-screenHeightPx,-48)
            self.visualEditor.setPos(screenWidthPx/4, 0, 0)
            self.elementHandler.setEditorCenter((self.visualEditor.getWidth()/2, 0, -self.visualEditor.getHeight()/2))

    def toggleGrid(self, enable):
        if enable:
            self.grid.show()
            self.snapToGrid = True
        else:
            self.grid.hide()
            self.snapToGrid = False

    def zoom(self, direction):
        if direction < 0 and self.visualEditor.getCanvas().getScale() > 0.5:
            self.visualEditor.getCanvas().setScale(self.visualEditor.getCanvas().getScale() + direction)
        elif direction > 0 and self.visualEditor.getCanvas().getScale() < 5.0:
            self.visualEditor.getCanvas().setScale(self.visualEditor.getCanvas().getScale() + direction)

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