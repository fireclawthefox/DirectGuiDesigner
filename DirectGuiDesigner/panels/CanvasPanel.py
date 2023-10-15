#!/usr/bin/env python
# -*- coding: utf-8 -*-

from panda3d.core import Point3, ConfigVariableBool, LVecBase3f

from direct.gui import DirectGuiGlobals as DGG

from direct.gui.DirectFrame import DirectFrame
#from direct.gui.DirectScrolledFrame import DirectScrolledFrame
from DirectGuiDesigner.directGuiOverrides.DirectScrolledFrame import DirectScrolledFrame

from direct.directtools.DirectGrid import DirectGrid

from DirectGuiExtension import DirectGuiHelper as DGH
from DirectGuiExtension.DirectAutoSizer import DirectAutoSizer

DEFAULT_MIN_SCALE = 0.2
DEFAULT_MAX_SCALE = 2.0

class CanvasPanel:
    def __init__(self, parent):
        self.parent = parent
        self.elementHandler = None

        color = (
            (0.8, 0.8, 0.8, 1), # Normal
            (0.9, 0.9, 1, 1), # Click
            (0.8, 0.8, 1, 1), # Hover
            (0.5, 0.5, 0.5, 1)) # Disabled


        # we default to a 1920x1080 FHD screen
        self.canvasLeft = -1920/2
        self.canvasRight = 1920/2
        self.canvasTop = 1080/2
        self.canvasBottom = -1080/2

        # use the shorter size (vertical) to calculate a scale of 1
        self.canvasScale = 1080

        self.visualEditor = DirectScrolledFrame(
            frameColor=(0.25, 0.25, 0.25, 1),
            canvasSize=(self.canvasLeft, self.canvasRight, self.canvasBottom, self.canvasTop),
            scrollBarWidth=20,

            # vertical scrollbar
            verticalScroll_value=0.5,
            verticalScroll_thumb_relief=DGG.FLAT,
            verticalScroll_incButton_relief=DGG.FLAT,
            verticalScroll_decButton_relief=DGG.FLAT,
            verticalScroll_thumb_frameColor=color,
            verticalScroll_incButton_frameColor=color,
            verticalScroll_decButton_frameColor=color,

            # horizontal scrollbar
            horizontalScroll_value=0.5,
            horizontalScroll_thumb_relief=DGG.FLAT,
            horizontalScroll_incButton_relief=DGG.FLAT,
            horizontalScroll_decButton_relief=DGG.FLAT,
            horizontalScroll_thumb_frameColor=color,
            horizontalScroll_incButton_frameColor=color,
            horizontalScroll_decButton_frameColor=color,
            )

        self.scaleParent = DirectFrame(
            scale=(1,1,1)
            )

        # store which base parent should be used for the elements
        self.currentVisEditorParent = base.aspect2d
        self.visEditorInAspect2D = True

        # Layouting
        self.sizer = DirectAutoSizer(
            #updateOnWindowResize=False,
            parent=parent,
            child=self.visualEditor,
            )

        # zoom scale
        self.minScale = DEFAULT_MIN_SCALE
        self.maxScale = DEFAULT_MAX_SCALE
        self.zoomInMultiplyer = 1.1
        self.zoomOutMultiplyer = 0.9

        # This frame will be the base parent for the added GUI elements
        self.elementHolder = DirectFrame(
            #frameColor=(0.25, 0.25, 0.25, 1),
            scale=LVecBase3f(self.canvasScale/2,1,self.canvasScale/2),
            parent=self.scaleParent
            )
        self.elementHolder.bind(DGG.B1RELEASE, base.messenger.send, ["mouse3"])
        # Ensure the holder frame will be streched to fill the parent
        self.scaleParentSizer = DirectAutoSizer(
            #updateOnWindowResize=False,
            parent=self.visualEditor.canvas,
            child=self.scaleParent,
            parentGetSizeFunction=self.visualEditor.cget,
            parentGetSizeExtraArgs=["canvasSize"],
            )

        self.elementHolderSizer = DirectAutoSizer(
            #updateOnWindowResize=False,
            parent=self.scaleParent,
            child=self.elementHolder
            )

        # The designers grid
        self.grid = DirectGrid(gridSize=50.0, gridSpacing=0.05,parent=self.elementHolder)
        self.grid.setP(90)
        self.grid.snapMarker.hide()
        self.snapToGrid = not self.grid.isHidden()

        self.canvasTopCenter = self.elementHolder.attachNewNode("canvasTopCenter")
        self.canvasBottomCenter = self.elementHolder.attachNewNode("canvasBottomCenter")
        self.canvasLeftCenter = self.elementHolder.attachNewNode("canvasLeftCenter")
        self.canvasRightCenter = self.elementHolder.attachNewNode("canvasRightCenter")

        self.canvasTopLeft = self.elementHolder.attachNewNode("canvasTopLeft")
        self.canvasTopRight = self.elementHolder.attachNewNode("canvasTopRight")
        self.canvasBottomLeft = self.elementHolder.attachNewNode("canvasBottomLeft")
        self.canvasBottomRight = self.elementHolder.attachNewNode("canvasBottomRight")

        # default to Aspect2D
        self.setVisualEditorParent(False)

        base.taskMgr.add(self.watchCanvasProps, "watch-canvas-properties", sort=50, priority=0)

    def getEditorCanvasSize(self):
        cs = self.elementHolder["frameSize"]

        if self.currentVisEditorParent == base.pixel2d:
            cs = self.visualEditor["canvasSize"]

        return cs

    def getEditorRootCanvas(self):
        return self.elementHolder

    def watchCanvasProps(self, task):
        """Watch for all properties that can be changed on the canvas and won't
        directly propagate down to the actual background, which is the element
        holder."""

        #self.sizer.refresh()

        sizeChanged = False
        cs = self.getEditorCanvasSize()
        if self.canvasLeft != cs[0]:
            sizeChanged = True
        elif self.canvasRight != cs[1]:
            sizeChanged = True
        elif self.canvasBottom != cs[2]:
            sizeChanged = True
        elif self.canvasTop != cs[3]:
            sizeChanged = True

        if sizeChanged:
            width = cs[1] - cs[0]
            height = cs[3] - cs[2]

            self.canvasScale = min(width, height)

            if self.currentVisEditorParent == base.pixel2d:
                if width > height:
                    self.canvasScale *= self.visualEditor.getScale()[2]
                else:
                    self.canvasScale *= self.visualEditor.getScale()[0]
            else:
                if width > height:
                    self.canvasScale *= self.elementHolder.getScale()[2]
                else:
                    self.canvasScale *= self.elementHolder.getScale()[0]

            #TODO: the scale probably needs to be calculated dependent on the users screen size
            self.elementHolder["scale"]= LVecBase3f(self.canvasScale/2,1,self.canvasScale/2),

            self.elementHolderSizer.refresh()
            self.scaleParentSizer.refresh()
            self.setCanvasPlacers()

        if self.visualEditor["frameColor"] != self.elementHolder["frameColor"]:
            fc = self.visualEditor["frameColor"]
            self.elementHolder["frameColor"] = fc
            self.elementHolderSizer["frameColor"] = fc
            self.scaleParentSizer["frameColor"] = fc
            self.scaleParent["frameColor"] = fc
        self.visualEditor

        return task.cont

    def setCanvasPlacers(self):
        cs = self.getEditorCanvasSize()
        self.canvasLeft = cs[0]
        self.canvasRight = cs[1]
        self.canvasBottom = cs[2]
        self.canvasTop = cs[3]

        # Put the nodes in their places
        self.canvasTopCenter.setPos(0, 0, self.canvasTop)
        self.canvasBottomCenter.setPos(0, 0, self.canvasBottom)
        self.canvasLeftCenter.setPos(self.canvasLeft, 0, 0)
        self.canvasRightCenter.setPos(self.canvasRight, 0, 0)

        self.canvasTopLeft.setPos(self.canvasLeft, 0, self.canvasTop)
        self.canvasTopRight.setPos(self.canvasRight, 0, self.canvasTop)
        self.canvasBottomLeft.setPos(self.canvasLeft, 0, self.canvasBottom)
        self.canvasBottomRight.setPos(self.canvasRight, 0, self.canvasBottom)

    def getAllEditorPlacers(self):
        return [
            self.canvasTopCenter,
            self.canvasBottomCenter,
            self.canvasLeftCenter,
            self.canvasRightCenter,
            self.canvasTopLeft,
            self.canvasTopRight,
            self.canvasBottomLeft,
            self.canvasBottomRight]

    def getEditorPlacer(self, placerName):
        placerName = placerName.lower()
        placerName = placerName.replace("a2d", "canvas")
        if placerName == "canvasTopCenter".lower():
            return self.canvasTopCenter
        elif placerName == "canvasBottomCenter".lower():
            return self.canvasBottomCenter
        elif placerName == "canvasLeftCenter".lower():
            return self.canvasLeftCenter
        elif placerName == "canvasRightCenter".lower():
            return self.canvasRightCenter
        elif placerName == "canvasTopLeft".lower():
            return self.canvasTopLeft
        elif placerName == "canvasTopRight".lower():
            return self.canvasTopRight
        elif placerName == "canvasBottomLeft".lower():
            return self.canvasBottomLeft
        elif placerName == "canvasBottomRight".lower():
            return self.canvasBottomRight
        else:
            return self.getEditorRootCanvas()

    def setElementHandler(self, elementHandler):
        self.elementHandler = elementHandler

    def setVisualEditorCanvasSize(self, newCanvasSize):
        self.visualEditor["canvasSize"] = newCanvasSize
        self.elementHolderSizer.refresh()
        self.scaleParentSizer.refresh()
        self.setCanvasPlacers()

    def setVisualEditorParent(self, toPixel2D):
        if toPixel2D:
            # change to pixel2d
            # we default to a 1920x1080 FHD screen
            self.canvasLeft = 0
            self.canvasRight = 1920
            self.canvasBottom = -1080
            self.canvasTop = 0

            self.setVisualEditorCanvasSize((self.canvasLeft, self.canvasRight, self.canvasBottom, self.canvasTop))
            self.currentVisEditorParent = base.pixel2d

            # Speed up the setGridSpacing call by setting the size to 1
            self.grid.setGridSize(1)
            self.grid.setGridSpacing(0.05 * (self.canvasScale / 2))
            self.grid.setGridSize(1920*4)
            self.visEditorInAspect2D = False
            if self.elementHandler is not None:
                self.elementHandler.setEditorParentType(self.visEditorInAspect2D)
                self.elementHandler.setEditorCenter((self.visualEditor.getWidth()/2, 0, -self.visualEditor.getHeight()/2))
        else:
            # change to aspect2d
            # we default to a 1920x1080 FHD screen
            self.canvasLeft = -1920/2
            self.canvasRight = 1920/2
            self.canvasTop = 1080/2
            self.canvasBottom = -1080/2

            self.scaleParent.setScale(1, 1, 1)

            self.setVisualEditorCanvasSize((self.canvasLeft, self.canvasRight, self.canvasBottom, self.canvasTop))
            self.currentVisEditorParent = base.aspect2d

            # Speed up the setGridSpacing call by setting the size to 1
            self.grid.setGridSize(1)
            self.grid.setGridSpacing(0.05)
            self.grid.setGridSize(50)
            self.visEditorInAspect2D = True
            if self.elementHandler is not None:
                self.elementHandler.setEditorParentType(self.visEditorInAspect2D)
                self.elementHandler.setEditorCenter((0, 0, 0))

        # reset the zoom value
        self.resetZoom()

        self.setCanvasPlacers()

    def toggleVisualEditorParent(self):
        if self.currentVisEditorParent == base.aspect2d:
            self.setVisualEditorParent(True)
        elif self.currentVisEditorParent != base.aspect2d:
            self.setVisualEditorParent(False)

    def resizeFrame(self):
        self.sizer.refresh()

    def toggleGrid(self, enable):
        if enable:
            self.grid.show()
            self.snapToGrid = True
        else:
            self.grid.hide()
            self.snapToGrid = False

    def resetZoom(self):
        self.visualEditor["verticalScroll_range"] = (0, 1)
        self.visualEditor["horizontalScroll_range"] = (0, 1)
        if self.currentVisEditorParent != base.aspect2d:
            # we are in pixel2d
            self.getEditorRootCanvas().setScale(1,1,1)
            self.visualEditor.verticalScroll["value"] = 0
            self.visualEditor.horizontalScroll["value"] = 0

            posParentScaleX = DGH.getRealWidth(self.parent)
            self.minScale = DEFAULT_MIN_SCALE
            self.maxScale = DEFAULT_MAX_SCALE
            base.messenger.send("setZoomValeMinMax", [self.minScale, self.maxScale])
            base.messenger.send("setZoomValue", [1])
        else:
            # we are in aspect2d
            self.getEditorRootCanvas().setScale(self.canvasScale/2,1,self.canvasScale/2)
            self.visualEditor.verticalScroll["value"] = 0.5
            self.visualEditor.horizontalScroll["value"] = 0.5

            posParentScaleX = DGH.getRealWidth(self.parent)
            self.minScale = posParentScaleX * DEFAULT_MIN_SCALE
            self.maxScale = posParentScaleX * DEFAULT_MAX_SCALE
            base.messenger.send("setZoomValeMinMax", [self.minScale, self.maxScale])
            base.messenger.send("setZoomValue", [self.canvasScale/2])

    def setZoom(self, zoomValue):
        z = zoomValue
        s = self.getEditorRootCanvas().getScale()

        self.getEditorRootCanvas().setScale(z, s[1], z)

        # update scroll bars
        vr = self.visualEditor["verticalScroll_range"]
        vv = self.visualEditor.verticalScroll["value"]
        hr = self.visualEditor["horizontalScroll_range"]
        hv = self.visualEditor.horizontalScroll["value"]

        vw = vr[1] - vr[0]
        hw = hr[1] - hr[0]

        curPosVer = vv / vw * 100
        curPosHor = hv / hw * 100

        self.visualEditor["verticalScroll_range"] = (vr[0]*(z/s[0]), vr[1]*(z/s[2]))
        self.visualEditor["horizontalScroll_range"] = (hr[0]*(z/s[0]), hr[1]*(z/s[2]))

        vr = self.visualEditor["verticalScroll_range"]
        hr = self.visualEditor["horizontalScroll_range"]

        self.visualEditor.verticalScroll["value"] = (vr[1] - vr[0]) / 100 * curPosVer
        self.visualEditor.horizontalScroll["value"] = (hr[1] - hr[0]) / 100 * curPosHor

        self.elementHolderSizer.refresh()


    def zoom(self, direction):
        z = 1
        s = self.getEditorRootCanvas().getScale()
        if direction < 0 and self.getEditorRootCanvas().getScale()[0] > self.minScale:
            z = self.zoomOutMultiplyer
        elif direction > 0 and self.getEditorRootCanvas().getScale()[0] < self.maxScale:
            z = self.zoomInMultiplyer

        self.getEditorRootCanvas().setScale(s[0]*z, s[1], s[2]*z)

        base.messenger.send("setZoomValue", [self.getEditorRootCanvas().getScale()[0]])

        # update scroll bars
        vr = self.visualEditor["verticalScroll_range"]
        vv = self.visualEditor.verticalScroll["value"]
        hr = self.visualEditor["horizontalScroll_range"]
        hv = self.visualEditor.horizontalScroll["value"]

        vw = vr[1] - vr[0]
        hw = hr[1] - hr[0]

        curPosVer = vv / vw * 100
        curPosHor = hv / hw * 100

        self.visualEditor["verticalScroll_range"] = (vr[0]*z, vr[1]*z)
        self.visualEditor["horizontalScroll_range"] = (hr[0]*z, hr[1]*z)

        vr = self.visualEditor["verticalScroll_range"]
        hr = self.visualEditor["horizontalScroll_range"]

        self.visualEditor.verticalScroll["value"] = (vr[1] - vr[0]) / 100 * curPosVer
        self.visualEditor.horizontalScroll["value"] = (hr[1] - hr[0]) / 100 * curPosHor

        self.elementHolderSizer.refresh()

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
            self.visualEditor["verticalScroll_value"] = newValue

            newValue = self.visualEditor["horizontalScroll_value"] + moveVec.getX()
            self.visualEditor["horizontalScroll_value"] = newValue

        return t.cont
