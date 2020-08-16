from panda3d.core import TransparencyAttrib, ConfigVariableBool

from direct.showbase.DirectObject import DirectObject

from direct.gui import DirectGuiGlobals as DGG
DGG.BELOW = "below"

from direct.gui.DirectButton import DirectButton
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectCheckBox import DirectCheckBox
#from direct.gui.DirectOptionMenu import DirectOptionMenu
from directGuiOverrides.DirectOptionMenu import DirectOptionMenu

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
        self.menuBar = DirectFrame(
            frameColor=(0.25, 0.25, 0.25, 1),
            frameSize=(0,screenWidthPx,-12, 12),
            pos=(0, 0, -12),
            parent=base.pixel2d)

        x = 0

        self.file = DirectOptionMenu(
            text_fg=(1,1,1,1),
            text_scale=0.8,
            items=["New", "Save", "Load", "Export", "Quit"],
            pos=(x, 0, -5),
            frameSize=(0,65/21,-7/21,17/21),
            frameColor=color,
            scale=21,
            relief=DGG.FLAT,
            item_text_fg=(1,1,1,1),
            item_text_scale=0.8,
            highlightScale=(0.8,0.8),
            item_relief=DGG.FLAT,
            item_frameColor=color,
            item_pad=(0.2, 0.2),
            highlightColor=color[2],
            popupMenuLocation=DGG.BELOW,
            command=self.toolbarFileCommand,
            parent=self.menuBar)
        self.file["text"] = "File"

        x += 65

        self.view = DirectOptionMenu(
            text_fg=(1,1,1,1),
            text_scale=0.8,
            items=["Toggle Grid", "Toggle Scale"],
            pos=(x, 0, -5),
            frameSize=(0,65/21,-7/21,17/21),
            frameColor=color,
            scale=21,
            relief=DGG.FLAT,
            item_text_fg=(1,1,1,1),
            item_text_scale=0.8,
            highlightScale=(0.8,0.8),
            item_relief=DGG.FLAT,
            item_frameColor=color,
            item_pad=(0.2, 0.2),
            highlightColor=color[2],
            popupMenuLocation=DGG.BELOW,
            command=self.toolbarViewCommand,
            parent=self.menuBar)
        self.view["text"] = "View"

        x += 65

        self.tools = DirectOptionMenu(
            text_fg=(1,1,1,1),
            text_scale=0.8,
            items=["Delete Element", "Copy", "Paste", "Copy options", "Paste options", "Options", "Help"],
            pos=(x, 0, -5),
            frameSize=(0,65/21,-7/21,17/21),
            frameColor=color,
            scale=21,
            relief=DGG.FLAT,
            item_text_fg=(1,1,1,1),
            item_text_scale=0.8,
            highlightScale=(0.8,0.8),
            item_relief=DGG.FLAT,
            item_frameColor=color,
            item_pad=(0.2, 0.2),
            highlightColor=color[2],
            popupMenuLocation=DGG.BELOW,
            command=self.toolbarToolsCommand,
            parent=self.menuBar)
        self.tools["text"] = "Tools"


        #
        # Toolbar
        #
        self.toolBar = DirectFrame(
            frameColor=(0.25, 0.25, 0.25, 1),
            frameSize=(0,barWidth,-24, 24),
            pos=(left, 0, -24-24),
            parent=base.pixel2d)

        x = self.toolBar.bounds[0]
        buttonColor = (
            (0.8, 0.8, 0.8, 1), # Normal
            (0.9, 0.9, 1, 1), # Click
            (0.8, 0.8, 1, 1), # Hover
            (0.5, 0.5, 0.5, 1)) # Disabled
        btn = DirectButton(
            parent=self.toolBar,
            frameSize=(-24,24,-24,24),
            frameColor=buttonColor,
            pos=(x + 24, 0, 0),
            scale=1,
            #text_scale=0.33,
            relief=DGG.FLAT,
            command=base.messenger.send,
            extraArgs=["newProject"],
            image="icons/New.png",
            image_scale=24)
        btn.setTransparency(TransparencyAttrib.M_multisample)
        btn.bind(DGG.ENTER, self.tt.show, ["Create New GUI (Ctrl-N)"])
        btn.bind(DGG.EXIT, self.tt.hide)
        x += 48
        btn = DirectButton(
            parent=self.toolBar,
            frameSize=(-24,24,-24,24),
            frameColor=buttonColor,
            pos=(x + 24, 0, 0),
            scale=1,
            #text_scale=0.33,
            relief=DGG.FLAT,
            command=base.messenger.send,
            extraArgs=["saveProject"],
            image="icons/Save.png",
            image_scale=24)
        btn.setTransparency(TransparencyAttrib.M_multisample)
        btn.bind(DGG.ENTER, self.tt.show, ["Save GUI as gui Project (Ctrl-S)"])
        btn.bind(DGG.EXIT, self.tt.hide)
        x += 48
        btn = DirectButton(
            parent=self.toolBar,
            frameSize=(-24,24,-24,24),
            frameColor=buttonColor,
            pos=(x + 24, 0, 0),
            scale=1,
            text_scale=0.33,
            relief=DGG.FLAT,
            command=base.messenger.send,
            extraArgs=["exportProject"],
            image="icons/Export.png",
            image_scale=24)
        btn.setTransparency(TransparencyAttrib.M_multisample)
        btn.bind(DGG.ENTER, self.tt.show, ["Export GUI as python script (Ctrl-E)"])
        btn.bind(DGG.EXIT, self.tt.hide)
        x += 48
        btn = DirectButton(
            parent=self.toolBar,
            frameSize=(-24,24,-24,24),
            frameColor=buttonColor,
            pos=(x + 24, 0, 0),
            scale=1,
            relief=DGG.FLAT,
            text_scale=0.33,
            command=base.messenger.send,
            extraArgs=["loadProject"],
            image="icons/Load.png",
            image_scale=24)
        btn.setTransparency(TransparencyAttrib.M_multisample)
        btn.bind(DGG.ENTER, self.tt.show, ["Load GUI project (Ctrl-O)"])
        btn.bind(DGG.EXIT, self.tt.hide)
        x += 48 + 12
        btn = DirectButton(
            parent=self.toolBar,
            frameColor=buttonColor,
            pos=(x + 24, 0, 0),
            scale=1,
            relief=DGG.FLAT,
            text_scale=0.33,
            command=base.messenger.send,
            extraArgs=["removeElement"],
            image="icons/Delete.png",
            image_scale=24)
        btn.setTransparency(TransparencyAttrib.M_multisample)
        btn.bind(DGG.ENTER, self.tt.show, ["Delete selected element (Del)"])
        btn.bind(DGG.EXIT, self.tt.hide)
        x += 48
        self.cb_grid = DirectCheckBox(
            parent=self.toolBar,
            frameSize=(-24,24,-24,24),
            frameColor=buttonColor,
            pos=(x + 24, 0, 0),
            scale=1,
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
        x += 48
        self.cb_scale = DirectCheckBox(
            parent=self.toolBar,
            frameSize=(-24,24,-24,24),
            frameColor=buttonColor,
            pos=(x + 24, 0, 0),
            scale=1,
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
        x += 48 + 12
        btn = DirectButton(
            parent=self.toolBar,
            frameSize=(-24,24,-24,24),
            frameColor=buttonColor,
            pos=(x + 24, 0, 0),
            scale=1,
            relief=DGG.FLAT,
            text_scale=0.33,
            command=base.messenger.send,
            extraArgs=["quitApp"],
            image="icons/Quit.png",
            image_scale=24)
        btn.setTransparency(TransparencyAttrib.M_alpha)
        btn.bind(DGG.ENTER, self.tt.show, ["Quit Direct GUI Designer (Ctrl-Q)"])
        btn.bind(DGG.EXIT, self.tt.hide)
        x += 48 + 12
        btn = DirectButton(
            parent=self.toolBar,
            frameSize=(-24,24,-24,24),
            frameColor=buttonColor,
            pos=(x + 24, 0, 0),
            scale=1,
            relief=DGG.FLAT,
            text_scale=0.33,
            command=base.messenger.send,
            extraArgs=["showHelp"],
            image="icons/Help.png",
            image_scale=24)
        btn.setTransparency(TransparencyAttrib.M_multisample)
        btn.bind(DGG.ENTER, self.tt.show, ["Show a help Dialog (F1)"])
        btn.bind(DGG.EXIT, self.tt.hide)
        x += 48 + 12
        btn = DirectButton(
            parent=self.toolBar,
            frameSize=(-24,24,-24,24),
            frameColor=buttonColor,
            pos=(x + 24, 0, 0),
            scale=1,
            relief=DGG.FLAT,
            text_scale=0.33,
            command=base.messenger.send,
            extraArgs=["showSettings"],
            image="icons/Settings.png",
            image_scale=24)
        btn.setTransparency(TransparencyAttrib.M_multisample)
        btn.bind(DGG.ENTER, self.tt.show, ["Show Designer Settings"])
        btn.bind(DGG.EXIT, self.tt.hide)

        if not ConfigVariableBool("show-toolbar", True).getValue():
            self.toolBar.hide()

        self.accept("setVisualEditorParent", self.setVisualEditorParent)

    def toolbarFileCommand(self, selection):
        if selection == "New":
            base.messenger.send("newProject")
        elif selection == "Save":
            base.messenger.send("saveProject")
        elif selection == "Load":
            base.messenger.send("loadProject")
        elif selection == "Export":
            base.messenger.send("exportProject")
        elif selection == "Quit":
            base.messenger.send("quitApp")

        self.file["text"] = "File"

    def toolbarViewCommand(self, selection):
        if selection == "Toggle Grid":
            self.cb_grid.commandFunc(None)
        elif selection == "Toggle Scale":
            self.cb_scale.commandFunc(None)

        self.view["text"] = "View"

    def toolbarToolsCommand(self, selection):
        if selection == "Delete Element":
            base.messenger.send("removeElement")
        elif selection == "Options":
            base.messenger.send("showSettings")
        elif selection == "Copy":
            base.messenger.send("copyElement")
        elif selection == "Paste":
            base.messenger.send("pasteElement")
        elif selection == "Copy options":
            base.messenger.send("copyOptions")
        elif selection == "Paste options":
            base.messenger.send("pasteOptions")
        elif selection == "Help":
            base.messenger.send("showHelp")

        self.tools["text"] = "Tools"

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
