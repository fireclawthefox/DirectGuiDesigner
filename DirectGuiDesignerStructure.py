#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

from panda3d.core import VBase4, TextNode, Point3

from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectScrolledFrame import DirectScrolledFrame
from direct.gui.DirectButton import DirectButton

class DirectGuiDesignerStructure():
    def __init__(self, parent, posZ, height, visualEditor, elementDict):
        DirectLabel(
            text="Structure",
            text_scale=0.05,
            text_pos=(parent["frameSize"][0], -0.015),
            text_align=TextNode.ALeft,
            text_fg=(1,1,1,1),
            frameSize=VBase4(parent["frameSize"][0], parent["frameSize"][1], 0.03, -0.03),
            frameColor=VBase4(0, 0, 0, 0),
            pos=(0,0,posZ-0.03),
            parent=parent)
        posZ -= 0.06
        color = (
            (0.8, 0.8, 0.8, 1), # Normal
            (0.9, 0.9, 1, 1), # Click
            (0.8, 0.8, 1, 1), # Hover
            (0.5, 0.5, 0.5, 1)) # Disabled
        self.structureFrame = DirectScrolledFrame(
            # make the frame fit into our background frame
            frameSize=VBase4(parent["frameSize"][0], parent["frameSize"][1], -(height-0.08), 0),
            # make the canvas as big as the frame
            canvasSize=VBase4(parent["frameSize"][0], parent["frameSize"][1]-0.04, -1, 0.0),
            # set the frames color to transparent
            frameColor=VBase4(1, 1, 1, 1),
            scrollBarWidth=0.04,
            verticalScroll_scrollSize=0.04,
            verticalScroll_thumb_relief=DGG.FLAT,
            verticalScroll_incButton_relief=DGG.FLAT,
            verticalScroll_decButton_relief=DGG.FLAT,
            verticalScroll_thumb_frameColor=color,
            verticalScroll_incButton_frameColor=color,
            verticalScroll_decButton_frameColor=color,
            horizontalScroll_thumb_relief=DGG.FLAT,
            horizontalScroll_incButton_relief=DGG.FLAT,
            horizontalScroll_decButton_relief=DGG.FLAT,
            horizontalScroll_thumb_frameColor=color,
            horizontalScroll_incButton_frameColor=color,
            horizontalScroll_decButton_frameColor=color,
            pos=(0,0,posZ),)
        self.maxWidth = parent["frameSize"][1]-0.04
        self.structureFrame.reparentTo(parent)
        self.visualEditor = visualEditor
        self.refreshStructureTree(elementDict)

    def refreshStructureTree(self, elementDict):
        self.elementDict = elementDict
        for element in self.structureFrame.getCanvas().getChildren():
            element.removeNode()

        self.itemCounter = 0
        self.__fillStructureTree(self.visualEditor.getCanvas(), 0, 0)

        self.structureFrame["canvasSize"] = (
            self.structureFrame["frameSize"][0], self.maxWidth,
            -(self.itemCounter*0.052), 0)
        self.structureFrame.setCanvasSize()

    def __fillStructureTree(self, root, level, z):
        if "DirectGrid" in root.getName(): return
        self.itemCounter += 1
        if level > 0:
            self.__makeStructureFrameTreeItem(root, level, z)
        if hasattr(root, "getChildren"):
            for child in root.getChildren():
                z=-0.05*self.itemCounter
                self.__fillStructureTree(child, level+1, z)

    def __makeStructureFrameTreeItem(self, elementNP, parentsLevel, z):
        elementInfo = None
        if elementNP.getName() in self.elementDict.keys():
            elementInfo = self.elementDict[elementNP.getName()]
        elif len(elementNP.getName().split("-")) > 1 and elementNP.getName().split("-")[1] in self.elementDict.keys():
            elementInfo = self.elementDict[elementNP.getName().split("-")[1]]
        else:
            DirectLabel(
                text=elementNP.getName(),
                text_align=TextNode.ALeft,
                relief=DGG.FLAT,
                pos=(self.structureFrame["frameSize"][0] + 0.05*parentsLevel, 0, z),
                scale=0.05,
                parent=self.structureFrame.getCanvas())

        if elementInfo is not None:
            btn = DirectButton(
                text=elementNP.getName(),
                text_align=TextNode.ALeft,
                relief=DGG.FLAT,
                pos=(self.structureFrame["frameSize"][0] + 0.05*parentsLevel, 0, z),
                scale=0.05,
                command=self.__selectElement,
                extraArgs=[elementInfo],
                parent=self.structureFrame.getCanvas())
            btnX = DirectButton(
                text="X",
                text_align=TextNode.ALeft,
                relief=DGG.FLAT,
                pos=(self.structureFrame["frameSize"][0] + 0.05*parentsLevel + btn.bounds[1]*btn.getScale()[0] + 0.01, 0, z),
                scale=0.05,
                command=self.__removeElement,
                extraArgs=[elementInfo],
                parent=self.structureFrame.getCanvas())
            btnV = DirectButton(
                text="V",
                text_align=TextNode.ALeft,
                relief=DGG.FLAT,
                pos=(self.structureFrame["frameSize"][0] + 0.05*parentsLevel + btn.bounds[1]*btn.getScale()[0] + btnX.bounds[1]*btnX.getScale()[0] + 0.02, 0, z),
                scale=0.05,
                command=self.__toggleElementVisibility,
                extraArgs=[elementInfo],
                parent=self.structureFrame.getCanvas())
            #print("W:",self.maxWidth)
            #print("X:",btnV.getX())
            #print("B:",btnV.bounds[1])
            print("size:", (btnV.bounds[1] - btnV.bounds[0])*btnV.getScale().x)
            self.maxWidth = max(self.maxWidth, btnV.getX() + (btnV.bounds[1] - btnV.bounds[0])*btnV.getScale().x + 0.04)

    def __selectElement(self, elementInfo, args=None):
        if elementInfo is not None:
            base.messenger.send("selectElement", [elementInfo, args])

    def __removeElement(self, elementInfo):
        if elementInfo is not None:
            base.messenger.send("removeElement", [elementInfo.element])

    def __toggleElementVisibility(self, elementInfo):
        if elementInfo is not None:
            base.messenger.send("toggleElementVisibility", [elementInfo.element])
