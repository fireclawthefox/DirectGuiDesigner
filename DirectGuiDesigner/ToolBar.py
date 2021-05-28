from panda3d.core import TransparencyAttrib, ConfigVariableBool

from direct.showbase.DirectObject import DirectObject

from direct.gui import DirectGuiGlobals as DGG
DGG.BELOW = "below"

from direct.gui.DirectButton import DirectButton
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectCheckBox import DirectCheckBox
from DirectGuiExtension.DirectMenuItem import DirectMenuItem, DirectMenuItemEntry, DirectMenuItemSubMenu
from DirectGuiExtension.DirectBoxSizer import DirectBoxSizer

class ToolBar(DirectObject):
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
        # Toolbar
        #
        self.toolBar = DirectBoxSizer(
            frameColor=(0.25, 0.25, 0.25, 1),
            frameSize=(0,barWidth,-24, 24),
            autoUpdateFrameSize=False,
            pos=(0, 0, 0),
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

        placeholder = DirectFrame(
            text="|",
            frameSize=(-1,1,-24,24),
            pad=(4, 0),
            frameColor=(0,0,0,1))
        self.toolBar.addItem(placeholder)

        btn = DirectButton(
            frameSize=(-24,24,-24,24),
            frameColor=buttonColor,
            relief=DGG.FLAT,
            text_scale=0.33,
            command=base.messenger.send,
            extraArgs=["undo"],
            image="icons/Undo.png",
            image_scale=24)
        btn.setTransparency(TransparencyAttrib.M_multisample)
        btn.bind(DGG.ENTER, self.tt.show, ["Undo last action (Ctrl-Z)"])
        btn.bind(DGG.EXIT, self.tt.hide)
        self.toolBar.addItem(btn)

        btn = DirectButton(
            frameSize=(-24,24,-24,24),
            frameColor=buttonColor,
            relief=DGG.FLAT,
            text_scale=0.33,
            command=base.messenger.send,
            extraArgs=["redo"],
            image="icons/Redo.png",
            image_scale=24)
        btn.setTransparency(TransparencyAttrib.M_multisample)
        btn.bind(DGG.ENTER, self.tt.show, ["Redo last action (Ctrl-Y)"])
        btn.bind(DGG.EXIT, self.tt.hide)
        self.toolBar.addItem(btn)

        btn = DirectButton(
            frameSize=(-24,24,-24,24),
            frameColor=buttonColor,
            relief=DGG.FLAT,
            text_scale=0.33,
            command=base.messenger.send,
            extraArgs=["cycleRedo"],
            image="icons/CycleRedo.png",
            image_scale=24)
        btn.setTransparency(TransparencyAttrib.M_multisample)
        btn.bind(DGG.ENTER, self.tt.show, ["Cycle through redo branches (Ctrl-Shift-Y)"])
        btn.bind(DGG.EXIT, self.tt.hide)
        self.toolBar.addItem(btn)

        placeholder = DirectFrame(
            text="|",
            frameSize=(-1,1,-24,24),
            pad=(4, 0),
            frameColor=(0,0,0,1))
        self.toolBar.addItem(placeholder)

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

        placeholder = DirectFrame(
            text="|",
            frameSize=(-1,1,-24,24),
            pad=(4, 0),
            frameColor=(0,0,0,1))
        self.toolBar.addItem(placeholder)

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

        placeholder = DirectFrame(
            text="|",
            frameSize=(-1,1,-24,24),
            pad=(4, 0),
            frameColor=(0,0,0,1))
        self.toolBar.addItem(placeholder)

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

        placeholder = DirectFrame(
            text="|",
            frameSize=(-1,1,-24,24),
            pad=(4, 0),
            frameColor=(0,0,0,1))
        self.toolBar.addItem(placeholder)

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

        self.accept("setVisualEditorParent", self.setVisualEditorParent)
        self.accept("toggleGrid", self.setGrid)
        #self.accept("toggleGrid", self.setVisualEditorParent)

    def toggleGrid(self, selection):
        base.messenger.send("toggleGrid", [selection])

    def setGrid(self, selection):
        self.cb_grid['isChecked'] = selection
        if selection:
            self.cb_grid['image'] = self.cb_grid['checkedImage']
        else:
            self.cb_grid['image'] = self.cb_grid['uncheckedImage']

        self.cb_grid.setImage()

    def toggleVisualEditorParent(self, selection):
        base.messenger.send("toggleVisualEditorParent")

    def setVisualEditorParent(self, toPixel2D):
        self.cb_scale["isChecked"] = not toPixel2D

        if self.cb_scale['isChecked']:
            self.cb_scale['image'] = self.cb_scale['checkedImage']
        else:
            self.cb_scale['image'] = self.cb_scale['uncheckedImage']

        self.cb_scale.setImage()
