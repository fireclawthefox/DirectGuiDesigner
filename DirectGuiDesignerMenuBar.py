from panda3d.core import TransparencyAttrib

from direct.gui import DirectGuiGlobals as DGG

from direct.gui.DirectButton import DirectButton
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectCheckBox import DirectCheckBox

class DirectGuiDesignerMenuBar:
    def __init__(self, tooltip, grid):
        self.tt = tooltip
        self.grid = grid
        screenWidthPx = base.getSize()[0]
        left = screenWidthPx*0.25
        barWidth = screenWidthPx*0.75

        self.menuBar = DirectFrame(
            frameColor=(0.25, 0.25, 0.25, 1),
            frameSize=(0,barWidth,-24, 24),
            pos=(left, 0, -24),
            parent=base.pixel2d)

        x = self.menuBar.bounds[0]
        buttonColor = (
            (0.8, 0.8, 0.8, 1), # Normal
            (0.9, 0.9, 1, 1), # Click
            (0.8, 0.8, 1, 1), # Hover
            (0.5, 0.5, 0.5, 1)) # Disabled
        btn = DirectButton(
            parent=self.menuBar,
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
            parent=self.menuBar,
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
            parent=self.menuBar,
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
            parent=self.menuBar,
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
            parent=self.menuBar,
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
            parent=self.menuBar,
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
            parent=self.menuBar,
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
            parent=self.menuBar,
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
            parent=self.menuBar,
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

    def toggleGrid(self, selection):
        base.messenger.send("toggleGrid", [selection])

    def toggleVisualEditorParent(self, selection):
        base.messenger.send("toggleVisualEditorParent")

    def resizeFrame(self):
        screenWidthPx = base.getSize()[0]
        left = screenWidthPx*0.25
        barWidth = screenWidthPx*0.75
        self.menuBar["frameSize"] = (0,barWidth,-24, 24)
        self.menuBar.setPos(left, 0, -24)
