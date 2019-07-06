

from panda3d.core import VBase4, TextNode

from direct.gui import DirectGuiGlobals as DGG

from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectScrolledFrame import DirectScrolledFrame

class DirectGuiDesignerToolbox:
    def __init__(self, parent, posZ, height):
        self.parent = parent
        self.toolsFrame = parent
        self.lblHeader = DirectLabel(
            text="Toolbox",
            text_scale=0.05,
            text_pos=(parent["frameSize"][0], -0.015),
            text_align=TextNode.ALeft,
            text_fg=(1,1,1,1),
            frameSize=VBase4(parent["frameSize"][0], parent["frameSize"][1], 0.03, -0.03),
            frameColor=VBase4(0, 0, 0, 0),
            pos=(0,0,posZ-0.03),
            parent=parent,)
        posZ -= 0.06
        color = (
            (0.8, 0.8, 0.8, 1), # Normal
            (0.9, 0.9, 1, 1), # Click
            (0.8, 0.8, 1, 1), # Hover
            (0.5, 0.5, 0.5, 1)) # Disabled
        self.toolboxFrame = DirectScrolledFrame(
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
        self.toolboxFrame.reparentTo(parent)
        self.toolboxEntries = [
            ["~Interactive Elements~"],
            ["Button", "DirectButton"],
            ["Entry", "DirectEntry"],
            ["Scrolled Entry", "DirectEntryScroll"],
            ["Check Box", "DirectCheckBox"],
            ["Check Button", "DirectCheckButton"],
            ["Option Menu", "DirectOptionMenu"],
            ["Radio Button", "DirectRadioButton"],
            ["Slider", "DirectSlider"],
            ["Scroll Bar", "DirectScrollBar"],
            ["Scrolled List Item", "DirectScrolledListItem"],

            ["~Display Elements~"],
            ["Label", "DirectLabel"],
            ["Wait Bar", "DirectWaitBar"],

            ["~Container~"],
            ["Frame", "DirectFrame"],
            ["Scrolled Frame", "DirectScrolledFrame"],
            ["Scrolled List", "DirectScrolledList"],

            ["~Dialogs~"],
            ["OK Dialog", "OkDialog"],
            ["OK Cancel Dialog", "OkCancelDialog"],
            ["Yes No Dialog", "YesNoDialog"],
            ["Yes No Cancel Dialog", "YesNoCancelDialog"],
            ["Retry Cancel Dialog", "RetryCancelDialog"],
        ]
        idx = 1
        for entry in self.toolboxEntries:
            if len(entry) == 2:
                item = self.__makeToolboxListItem(entry[0], entry[1], idx)
                item.reparentTo(self.toolboxFrame.getCanvas())
            else:
                item = self.__makeToolboxCenteredListItem(entry[0], idx)
                item.reparentTo(self.toolboxFrame.getCanvas())
            idx += 1
        self.toolboxFrame["canvasSize"] = (
            parent["frameSize"][0], parent["frameSize"][1]-0.04,
            -(len(self.toolboxEntries)*0.08), 0)
        self.toolboxFrame.setCanvasSize()

    def resizeFrame(self, posZ, height):
        self.lblHeader["frameSize"] = (self.parent["frameSize"][0], self.parent["frameSize"][1], 0.03, -0.03)
        self.lblHeader["text_pos"] = (self.parent["frameSize"][0], -0.015)
        self.lblHeader.setPos(0,0,posZ-0.03)
        posZ -= 0.06
        self.toolboxFrame["frameSize"] = (self.parent["frameSize"][0], self.parent["frameSize"][1], -(height-0.08), 0)
        self.toolboxFrame.setPos(0,0,posZ)

    def __createControl(self, name):
        base.messenger.send("createControl", [name])

    def __makeToolboxListItem(self, displayName, name, index):
        item = DirectButton(
            text=displayName,
            frameSize=VBase4(self.toolsFrame["frameSize"][0], self.toolsFrame["frameSize"][1]-0.04, -0.04, 0.04),
            frameColor=(VBase4(1,1,1,1), #normal
                VBase4(0.9,0.9,0.9,1), #click
                VBase4(0.8,0.8,0.8,1), #hover
                VBase4(0.5,0.5,0.5,1)), #disabled
            text_align=TextNode.ALeft,
            text_scale=0.05,
            text_pos=(self.toolsFrame["frameSize"][0], -0.015),
            pos=(0, 0, -(0.08 * index)+0.04),
            relief=DGG.FLAT,
            command=self.__createControl,
            extraArgs=[name])
        return item

    def __makeToolboxCenteredListItem(self, displayName, index):
        item = DirectFrame(
            text=displayName,
            frameSize=VBase4(self.toolsFrame["frameSize"][0]-0.02, self.toolsFrame["frameSize"][1]-0.02, -0.04, 0.04),
            frameColor=VBase4(0.85,0.85,0.85,1),
            text_align=TextNode.ACenter,
            text_scale=0.05,
            text_pos=(0, -0.015),
            pos=(-0.02, 0, -(0.08 * index)+0.04))
        return item
