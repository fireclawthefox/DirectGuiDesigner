

from panda3d.core import VBase4, TextNode, PGButton, MouseButton

from direct.gui import DirectGuiGlobals as DGG
DGG.MWUP = PGButton.getPressPrefix() + MouseButton.wheel_up().getName() + '-'
DGG.MWDOWN = PGButton.getPressPrefix() + MouseButton.wheel_down().getName() + '-'

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
            text_scale=16,
            text_pos=(parent["frameSize"][0], 0),
            text_align=TextNode.ALeft,
            text_fg=(1,1,1,1),
            frameSize=VBase4(parent["frameSize"][0], parent["frameSize"][1], -10, 20),
            frameColor=VBase4(0, 0, 0, 0),
            pos=(0,0,posZ-20),
            parent=parent,)
        posZ -= 30
        color = (
            (0.8, 0.8, 0.8, 1), # Normal
            (0.9, 0.9, 1, 1), # Click
            (0.8, 0.8, 1, 1), # Hover
            (0.5, 0.5, 0.5, 1)) # Disabled
        self.toolboxFrame = DirectScrolledFrame(
            # make the frame fit into our background frame
            frameSize=VBase4(parent["frameSize"][0], parent["frameSize"][1], height+30, 0),
            # make the canvas as big as the frame
            canvasSize=VBase4(parent["frameSize"][0], parent["frameSize"][1]-20, height+30, 0),
            # set the frames color to transparent
            frameColor=VBase4(1, 1, 1, 1),
            scrollBarWidth=20,
            verticalScroll_scrollSize=20,
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
            pos=(0,0,posZ),
            state=DGG.NORMAL,
            parent=parent)
        self.toolboxFrame.bind(DGG.MWDOWN, self.scroll, [0.01])
        self.toolboxFrame.bind(DGG.MWUP, self.scroll, [-0.01])
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
        self.createEntries()

    def scroll(self, scrollStep, event):
        self.toolboxFrame.verticalScroll.scrollStep(scrollStep)

    def createEntries(self):
        # Empty the toolbox if there were any elements
        for child in self.toolboxFrame.getCanvas().getChildren():
            child.removeNode()
        idx = 1
        for entry in self.toolboxEntries:
            if len(entry) == 2:
                item = self.__makeToolboxListItem(entry[0], entry[1], idx)
                item.reparentTo(self.toolboxFrame.getCanvas())
            else:
                item = self.__makeToolboxCenteredListItem(entry[0], idx)
                item.reparentTo(self.toolboxFrame.getCanvas())
            item.bind(DGG.MWDOWN, self.scroll, [0.01])
            item.bind(DGG.MWUP, self.scroll, [-0.01])
            idx += 1
        self.toolboxFrame["canvasSize"] = (
            self.parent["frameSize"][0], self.parent["frameSize"][1]-20,
            -(len(self.toolboxEntries)*30), 0)
        self.toolboxFrame.setCanvasSize()

    def resizeFrame(self, posZ, height):
        self.lblHeader["frameSize"] = (self.parent["frameSize"][0], self.parent["frameSize"][1], -10, 20)
        self.lblHeader["text_pos"] = (self.parent["frameSize"][0], 0)
        self.lblHeader.setPos(0,0,posZ-20)
        posZ -= 30
        self.toolboxFrame["frameSize"] = (self.parent["frameSize"][0], self.parent["frameSize"][1], height+30, 0)
        self.toolboxFrame.setPos(0,0,posZ)
        self.createEntries()

    def __createControl(self, name):
        base.messenger.send("createControl", [name])

    def __makeToolboxListItem(self, displayName, name, index):
        item = DirectButton(
            text=displayName,
            frameSize=VBase4(self.toolsFrame["frameSize"][0], self.toolsFrame["frameSize"][1]-20, -10, 20),
            frameColor=(VBase4(1,1,1,1), #normal
                VBase4(0.9,0.9,0.9,1), #click
                VBase4(0.8,0.8,0.8,1), #hover
                VBase4(0.5,0.5,0.5,1)), #disabled
            text_align=TextNode.ALeft,
            text_scale=12,
            text_pos=(self.toolsFrame["frameSize"][0], 0),
            pos=(0, 0, -30 * index + 10),
            relief=DGG.FLAT,
            command=self.__createControl,
            extraArgs=[name],
            #suppressMouse=0
            )
        return item

    def __makeToolboxCenteredListItem(self, displayName, index):
        item = DirectFrame(
            text=displayName,
            frameSize=VBase4(-self.toolsFrame["frameSize"][1]/2-10, self.toolsFrame["frameSize"][1]/2-10, -10, 20),
            frameColor=VBase4(0.85,0.85,0.85,1),
            text_align=TextNode.ACenter,
            text_scale=16,
            text_pos=(0, 0),
            pos=(self.toolsFrame["frameSize"][1]/2-10, 0, -30 * index + 10),
            state=DGG.NORMAL,
            #suppressMouse=0
            )
        return item
