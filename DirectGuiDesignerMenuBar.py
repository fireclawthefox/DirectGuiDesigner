from panda3d.core import TransparencyAttrib, ConfigVariableBool

from direct.showbase.DirectObject import DirectObject

from direct.gui import DirectGuiGlobals as DGG
DGG.BELOW = "below"

from direct.gui.DirectButton import DirectButton
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectCheckBox import DirectCheckBox
from DirectGuiExtension.DirectMenuItem import DirectMenuItem, DirectMenuItemEntry, DirectMenuItemSubMenu
from DirectGuiExtension.DirectBoxSizer import DirectBoxSizer

class DirectGuiDesignerMenuBar(DirectObject):
    def __init__(self, tooltip, grid):
        self.tt = tooltip
        self.grid = grid
        screenWidthPx = base.getSize()[0]
        left = screenWidthPx*0.25
        barWidth = screenWidthPx*0.75

        color = (
            (0.25, 0.25, 0.25, 1), # Normal
            (0.35, 0.35, 1, 1), # Click
            (0.25, 0.25, 1, 1), # Hover
            (0.1, 0.1, 0.1, 1)) # Disabled

        #
        # Menubar
        #
        self.menuBar = DirectBoxSizer(
            frameColor=(0.25, 0.25, 0.25, 1),
            frameSize=(0,screenWidthPx,-12, 12),
            autoUpdateFrameSize=False,
            pos=(0, 0, -12),
            parent=base.pixel2d)

        fileEntries = [
            DirectMenuItemEntry("New", base.messenger.send, ["newProject"]),
            DirectMenuItemEntry("Save", base.messenger.send, ["saveProject"]),
            DirectMenuItemEntry("Load", base.messenger.send, ["loadProject"]),
            DirectMenuItemEntry("Export", base.messenger.send, ["exportProject"]),
            DirectMenuItemEntry("Quit", base.messenger.send, ["quitApp"]),
            ]
        self.file = DirectMenuItem(
            text="File",
            text_fg=(1,1,1,1),
            text_scale=0.8,
            items=fileEntries,
            frameSize=(0,65/21,-7/21,17/21),
            frameColor=color,
            scale=21,
            relief=DGG.FLAT,
            item_text_fg=(1,1,1,1),
            item_text_scale=0.8,
            item_relief=DGG.FLAT,
            item_pad=(0.2, 0.2),
            itemFrameColor=color,
            popupMenu_itemMargin=(0,0,-.1,-.1),
            popupMenu_frameColor=color,
            highlightColor=color[2])

        # NOTE: view entries defined after toolbar creation
        self.view = DirectMenuItem(
            text="View",
            text_fg=(1,1,1,1),
            text_scale=0.8,
            items=[DirectMenuItemEntry("placeholder", print, ["placeholder"])],
            frameSize=(0,65/21,-7/21,17/21),
            frameColor=color,
            scale=21,
            relief=DGG.FLAT,
            item_text_fg=(1,1,1,1),
            item_text_scale=0.8,
            item_relief=DGG.FLAT,
            item_pad=(0.2, 0.2),
            itemFrameColor=color,
            popupMenu_itemMargin=(0,0,-.1,-.1),
            popupMenu_frameColor=color,
            highlightColor=color[2])

        toolsEntries = [
            DirectMenuItemEntry("Delete Element", base.messenger.send, ["removeElement"]),
            DirectMenuItemEntry("Options", base.messenger.send, ["showSettings"]),
            DirectMenuItemEntry("Copy", base.messenger.send, ["copyElement"]),
            DirectMenuItemEntry("Paste", base.messenger.send, ["pasteElement"]),
            DirectMenuItemEntry("Copy options", base.messenger.send, ["copyOptions"]),
            DirectMenuItemEntry("Paste options", base.messenger.send, ["pasteOptions"]),
            DirectMenuItemEntry("Help", base.messenger.send, ["showHelp"]),
        ]
        self.tools = DirectMenuItem(
            text="Tools",
            text_fg=(1,1,1,1),
            text_scale=0.8,
            items=toolsEntries,
            frameSize=(0,65/21,-7/21,17/21),
            frameColor=color,
            scale=21,
            relief=DGG.FLAT,
            item_text_fg=(1,1,1,1),
            item_text_scale=0.8,
            item_relief=DGG.FLAT,
            item_pad=(0.2, 0.2),
            itemFrameColor=color,
            popupMenu_itemMargin=(0,0,-.1,-.1),
            popupMenu_frameColor=color,
            highlightColor=color[2])

        self.menuBar.addItem(self.file)
        self.menuBar.addItem(self.view)
        self.menuBar.addItem(self.tools)

        #
        # Toolbar
        #
        self.toolBar = DirectBoxSizer(
            frameColor=(0.25, 0.25, 0.25, 1),
            frameSize=(0,barWidth,-24, 24),
            autoUpdateFrameSize=False,
            pos=(left, 0, -24-24),
            parent=base.pixel2d)

        buttonColor = (
            (0.8, 0.8, 0.8, 1), # Normal
            (0.9, 0.9, 1, 1), # Click
            (0.8, 0.8, 1, 1), # Hover
            (0.5, 0.5, 0.5, 1)) # Disabled
        btn = DirectButton(
            frameSize=(-24,24,-24,24),
            frameColor=buttonColor,
            relief=DGG.FLAT,
            command=base.messenger.send,
            extraArgs=["newProject"],
            image="icons/New.png",
            image_scale=24)
        btn.setTransparency(TransparencyAttrib.M_multisample)
        btn.bind(DGG.ENTER, self.tt.show, ["Create New GUI (Ctrl-N)"])
        btn.bind(DGG.EXIT, self.tt.hide)
        self.toolBar.addItem(btn)

        btn = DirectButton(
            frameSize=(-24,24,-24,24),
            frameColor=buttonColor,
            relief=DGG.FLAT,
            command=base.messenger.send,
            extraArgs=["saveProject"],
            image="icons/Save.png",
            image_scale=24)
        btn.setTransparency(TransparencyAttrib.M_multisample)
        btn.bind(DGG.ENTER, self.tt.show, ["Save GUI as gui Project (Ctrl-S)"])
        btn.bind(DGG.EXIT, self.tt.hide)
        self.toolBar.addItem(btn)

        btn = DirectButton(
            frameSize=(-24,24,-24,24),
            frameColor=buttonColor,
            text_scale=0.33,
            relief=DGG.FLAT,
            command=base.messenger.send,
            extraArgs=["exportProject"],
            image="icons/Export.png",
            image_scale=24)
        btn.setTransparency(TransparencyAttrib.M_multisample)
        btn.bind(DGG.ENTER, self.tt.show, ["Export GUI as python script (Ctrl-E)"])
        btn.bind(DGG.EXIT, self.tt.hide)
        self.toolBar.addItem(btn)

        btn = DirectButton(
            frameSize=(-24,24,-24,24),
            frameColor=buttonColor,
            relief=DGG.FLAT,
            text_scale=0.33,
            command=base.messenger.send,
            extraArgs=["loadProject"],
            image="icons/Load.png",
            image_scale=24)
        btn.setTransparency(TransparencyAttrib.M_multisample)
        btn.bind(DGG.ENTER, self.tt.show, ["Load GUI project (Ctrl-O)"])
        btn.bind(DGG.EXIT, self.tt.hide)
        self.toolBar.addItem(btn)

        btn = DirectButton(
            frameSize=(-24,24,-24,24),
            frameColor=buttonColor,
            relief=DGG.FLAT,
            text_scale=0.33,
            command=base.messenger.send,
            extraArgs=["removeElement"],
            image="icons/Delete.png",
            image_scale=24)
        btn.setTransparency(TransparencyAttrib.M_multisample)
        btn.bind(DGG.ENTER, self.tt.show, ["Delete selected element (Del)"])
        btn.bind(DGG.EXIT, self.tt.hide)
        self.toolBar.addItem(btn)

        self.cb_grid = DirectCheckBox(
            frameSize=(-24,24,-24,24),
            frameColor=buttonColor,
            relief=DGG.FLAT,
            text_scale=12,
            image="icons/GridOff.png" if self.grid.isHidden() else "icons/GridOn.png",
            uncheckedImage="icons/GridOff.png",
            checkedImage="icons/GridOn.png",
            image_scale=24,
            isChecked=not self.grid.isHidden(),
            command=self.toggleGrid)
        self.cb_grid.setTransparency(TransparencyAttrib.M_multisample)
        self.cb_grid.bind(DGG.ENTER, self.tt.show, ["Toggle Grid (Ctrl-G)"])
        self.cb_grid.bind(DGG.EXIT, self.tt.hide)
        self.toolBar.addItem(self.cb_grid)

        self.cb_scale = DirectCheckBox(
            frameSize=(-24,24,-24,24),
            frameColor=buttonColor,
            relief=DGG.FLAT,
            text_scale=12,
            image="icons/Scale1.png",
            uncheckedImage="icons/Scale2.png",
            checkedImage="icons/Scale1.png",
            image_scale=24,
            isChecked=True,
            command=self.toggleVisualEditorParent)
        self.cb_scale.setTransparency(TransparencyAttrib.M_alpha)
        self.cb_scale.bind(DGG.ENTER, self.tt.show, ["Toggle editor scale (Aspect/Pixel)"])
        self.cb_scale.bind(DGG.EXIT, self.tt.hide)
        self.toolBar.addItem(self.cb_scale)

        btn = DirectButton(
            frameSize=(-24,24,-24,24),
            frameColor=buttonColor,
            relief=DGG.FLAT,
            text_scale=0.33,
            command=base.messenger.send,
            extraArgs=["quitApp"],
            image="icons/Quit.png",
            image_scale=24)
        btn.setTransparency(TransparencyAttrib.M_alpha)
        btn.bind(DGG.ENTER, self.tt.show, ["Quit Direct GUI Designer (Ctrl-Q)"])
        btn.bind(DGG.EXIT, self.tt.hide)
        self.toolBar.addItem(btn)

        btn = DirectButton(
            frameSize=(-24,24,-24,24),
            frameColor=buttonColor,
            relief=DGG.FLAT,
            text_scale=0.33,
            command=base.messenger.send,
            extraArgs=["showHelp"],
            image="icons/Help.png",
            image_scale=24)
        btn.setTransparency(TransparencyAttrib.M_multisample)
        btn.bind(DGG.ENTER, self.tt.show, ["Show a help Dialog (F1)"])
        btn.bind(DGG.EXIT, self.tt.hide)
        self.toolBar.addItem(btn)

        btn = DirectButton(
            frameSize=(-24,24,-24,24),
            frameColor=buttonColor,
            relief=DGG.FLAT,
            text_scale=0.33,
            command=base.messenger.send,
            extraArgs=["showSettings"],
            image="icons/Settings.png",
            image_scale=24)
        btn.setTransparency(TransparencyAttrib.M_multisample)
        btn.bind(DGG.ENTER, self.tt.show, ["Show Designer Settings"])
        btn.bind(DGG.EXIT, self.tt.hide)
        self.toolBar.addItem(btn)

        if not ConfigVariableBool("show-toolbar", True).getValue():
            self.toolBar.hide()

        viewEntries = [
            DirectMenuItemEntry("Toggle Grid", self.cb_grid.commandFunc, [None]),
            DirectMenuItemEntry("Toggle Scale", self.cb_scale.commandFunc, [None])
        ]

        self.view["items"] = viewEntries
        # HACK: this shouldn't be needed
        '''
        self.view["item_text_fg"]=(1,1,1,1)
        self.view["item_text_scale"]=0.8
        self.view["item_relief"]=DGG.FLAT
        self.view["item_pad"]=(0.2, 0.2)
        self.view["itemFrameColor"]=color
        self.view["popupMenu_itemMargin"]=(0,0,-.1,-.1)
        self.view["popupMenu_frameColor"]=color
        '''
        self.accept("setVisualEditorParent", self.setVisualEditorParent)

    def toggleGrid(self, selection):
        base.messenger.send("toggleGrid", [selection])

    def toggleVisualEditorParent(self, selection):
        base.messenger.send("toggleVisualEditorParent")

    def setVisualEditorParent(self, toPixel2D):
        self.cb_scale["isChecked"] = not toPixel2D

        if self.cb_scale['isChecked']:
            self.cb_scale['image'] = self.cb_scale['checkedImage']
        else:
            self.cb_scale['image'] = self.cb_scale['uncheckedImage']

        self.cb_scale.setImage()

    def resizeFrame(self):
        screenWidthPx = base.getSize()[0]
        left = screenWidthPx*0.25
        barWidth = screenWidthPx*0.75
        self.toolBar["frameSize"] = (0,barWidth,-24, 24)
        self.toolBar.setPos(left, 0, -24-24)

        self.menuBar["frameSize"] = (0,screenWidthPx,-12, 12)
        self.menuBar.setPos(0, 0, -12)

        if not ConfigVariableBool("show-toolbar", True).getValue():
            self.toolBar.hide()
