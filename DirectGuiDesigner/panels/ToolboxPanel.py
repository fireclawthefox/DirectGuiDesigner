

from panda3d.core import VBase4, TextNode, PGButton, MouseButton

from direct.gui import DirectGuiGlobals as DGG
DGG.MWUP = PGButton.getPressPrefix() + MouseButton.wheel_up().getName() + '-'
DGG.MWDOWN = PGButton.getPressPrefix() + MouseButton.wheel_down().getName() + '-'

from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectScrolledFrame import DirectScrolledFrame

from DirectGuiExtension import DirectGuiHelper as DGH
from DirectGuiExtension.DirectBoxSizer import DirectBoxSizer
from DirectGuiExtension.DirectAutoSizer import DirectAutoSizer

class ToolboxPanel:
    def __init__(self, parent):
        height = DGH.getRealHeight(parent)
        self.parent = parent

        self.box = DirectBoxSizer(
            frameColor=(0.25, 0.25, 0.25, 1),
            autoUpdateFrameSize=False,
            orientation=DGG.VERTICAL)
        self.sizer = DirectAutoSizer(
            updateOnWindowResize=False,
            parent=parent,
            child=self.box,
            childUpdateSizeFunc=self.box.refresh)

        self.lblHeader = DirectLabel(
            text="Toolbox",
            text_scale=16,
            text_align=TextNode.ALeft,
            text_fg=(1,1,1,1),
            frameColor=VBase4(0, 0, 0, 0),
            )
        self.box.addItem(self.lblHeader)

        color = (
            (0.8, 0.8, 0.8, 1), # Normal
            (0.9, 0.9, 1, 1), # Click
            (0.8, 0.8, 1, 1), # Hover
            (0.5, 0.5, 0.5, 1)) # Disabled
        self.toolboxFrame = DirectScrolledFrame(
            # make the frame fit into our background frame
            frameSize=VBase4(
                self.parent["frameSize"][0], self.parent["frameSize"][1],
                self.parent["frameSize"][2]+DGH.getRealHeight(self.lblHeader), self.parent["frameSize"][3]),
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
            state=DGG.NORMAL)
        self.box.addItem(self.toolboxFrame)
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
        if self.toolboxFrame.verticalScroll.isHidden():
            return

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

        self.recalcScrollSize()


    def recalcScrollSize(self):
        a = self.toolboxFrame["canvasSize"][2]
        b = abs(self.toolboxFrame["frameSize"][2]) + self.toolboxFrame["frameSize"][3]
        scrollDefault = 25
        s = -(scrollDefault / (a / b))

        self.toolboxFrame["verticalScroll_scrollSize"] = s
        self.toolboxFrame["verticalScroll_pageSize"] = s

    def resizeFrame(self):
        preSize = self.sizer["frameSize"]
        self.sizer.refresh()
        postSize = self.sizer["frameSize"]

        if preSize != postSize:
            self.toolboxFrame["frameSize"] = (
                    self.parent["frameSize"][0], self.parent["frameSize"][1],
                    self.parent["frameSize"][2]+DGH.getRealHeight(self.lblHeader), self.parent["frameSize"][3])

            self.createEntries()

    def __createControl(self, name):
        base.messenger.send("createControl", [name])

    def __makeToolboxListItem(self, displayName, name, index):
        item = DirectButton(
            text=displayName,
            frameSize=VBase4(self.parent["frameSize"][0], self.parent["frameSize"][1]-20, -10, 20),
            frameColor=(VBase4(1,1,1,1), #normal
                VBase4(0.9,0.9,0.9,1), #click
                VBase4(0.8,0.8,0.8,1), #hover
                VBase4(0.5,0.5,0.5,1)), #disabled
            text_align=TextNode.ALeft,
            text_scale=12,
            text_pos=(self.parent["frameSize"][0], 0),
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
            frameSize=VBase4(-self.parent["frameSize"][1], self.parent["frameSize"][1], -10, 20),
            frameColor=VBase4(0.85,0.85,0.85,1),
            text_align=TextNode.ACenter,
            text_scale=16,
            text_pos=(-10, 0),
            pos=(0, 0, -30 * index + 10),#self.parent["frameSize"][1]/2-10
            state=DGG.NORMAL,
            #suppressMouse=0
            )
        return item
