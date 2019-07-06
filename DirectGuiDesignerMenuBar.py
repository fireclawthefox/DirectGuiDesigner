from panda3d.core import TransparencyAttrib

from direct.gui import DirectGuiGlobals as DGG

from direct.gui.DirectButton import DirectButton
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectCheckBox import DirectCheckBox

class DirectGuiDesignerMenuBar:
    def __init__(self, tooltip, grid):
        self.tt = tooltip
        self.grid = grid
        self.screenWidth = abs(base.a2dRight) + abs(base.a2dLeft)

        self.menuBar = DirectFrame(
            frameColor=(0.25, 0.25, 0.25, 1),
            frameSize=(0,self.screenWidth*(0.75),
                -0.05,0.05),
            pos=(self.screenWidth*(0.25), 0, -0.05),
            parent=base.a2dTopLeft)

        x = self.menuBar.bounds[0]+(0.5*0.1)
        buttonColor = (
            (0.8, 0.8, 0.8, 1), # Normal
            (0.9, 0.9, 1, 1), # Click
            (0.8, 0.8, 1, 1), # Hover
            (0.5, 0.5, 0.5, 1)) # Disabled
        btn = DirectButton(
            parent=self.menuBar,
            frameSize=(-0.5,0.5,-0.5,0.5),
            frameColor=buttonColor,
            pos=(x, 0, 0),
            scale=0.1,
            text_scale=0.33,
            relief=DGG.FLAT,
            command=base.messenger.send,
            extraArgs=["newProject"],
            image="icons/New.png",
            image_scale=0.5)
        btn.setTransparency(TransparencyAttrib.M_multisample)
        btn.bind(DGG.ENTER, self.tt.show, ["Create New GUI (Ctrl-N)"])
        btn.bind(DGG.EXIT, self.tt.hide)
        x += 1*0.1
        btn = DirectButton(
            parent=self.menuBar,
            frameSize=(-0.5,0.5,-0.5,0.5),
            frameColor=buttonColor,
            pos=(x, 0, 0),
            scale=0.1,
            text_scale=0.33,
            relief=DGG.FLAT,
            command=base.messenger.send,
            extraArgs=["saveProject"],
            image="icons/Save.png",
            image_scale=0.5)
        btn.setTransparency(TransparencyAttrib.M_multisample)
        btn.bind(DGG.ENTER, self.tt.show, ["Save GUI as gui Project (Ctrl-S)"])
        btn.bind(DGG.EXIT, self.tt.hide)
        x += 1*0.1
        btn = DirectButton(
            parent=self.menuBar,
            frameSize=(-0.5,0.5,-0.5,0.5),
            frameColor=buttonColor,
            pos=(x, 0, 0),
            scale=0.1,
            text_scale=0.33,
            relief=DGG.FLAT,
            command=base.messenger.send,
            extraArgs=["exportProject"],
            image="icons/Export.png",
            image_scale=0.5)
        btn.setTransparency(TransparencyAttrib.M_multisample)
        btn.bind(DGG.ENTER, self.tt.show, ["Export GUI as python script (Ctrl-E)"])
        btn.bind(DGG.EXIT, self.tt.hide)
        x += 1*0.1
        btn = DirectButton(
            parent=self.menuBar,
            frameSize=(-0.5,0.5,-0.5,0.5),
            frameColor=buttonColor,
            pos=(x, 0, 0),
            scale=0.1,
            relief=DGG.FLAT,
            text_scale=0.33,
            command=base.messenger.send,
            extraArgs=["loadProject"],
            image="icons/Load.png",
            image_scale=0.5)
        btn.setTransparency(TransparencyAttrib.M_multisample)
        btn.bind(DGG.ENTER, self.tt.show, ["Load GUI project (Ctrl-O)"])
        btn.bind(DGG.EXIT, self.tt.hide)
        x += 1*0.1 + 0.025
        btn = DirectButton(
            parent=self.menuBar,
            frameSize=(-0.5,0.5,-0.5,0.5),
            frameColor=buttonColor,
            pos=(x, 0, 0),
            scale=0.1,
            relief=DGG.FLAT,
            text_scale=0.33,
            command=base.messenger.send,
            extraArgs=["removeElement"],
            image="icons/Delete.png",
            image_scale=0.5)
        btn.setTransparency(TransparencyAttrib.M_multisample)
        btn.bind(DGG.ENTER, self.tt.show, ["Delete selected element (Ctrl-Del)"])
        btn.bind(DGG.EXIT, self.tt.hide)
        x += 1*0.1
        self.cb_grid = DirectCheckBox(
            parent=self.menuBar,
            frameSize=(-0.5,0.5,-0.5,0.5),
            frameColor=buttonColor,
            pos=(x, 0, 0),
            scale=0.1,
            relief=DGG.FLAT,
            text_scale=0.33,
            image="icons/GridOff.png" if self.grid.isHidden() else "icons/GridOn.png",
            uncheckedImage="icons/GridOff.png",
            checkedImage="icons/GridOn.png",
            image_scale=0.5,
            isChecked=not self.grid.isHidden(),
            command=self.toggleGrid)
        self.cb_grid.setTransparency(TransparencyAttrib.M_multisample)
        self.cb_grid.bind(DGG.ENTER, self.tt.show, ["Toggle Grid (Ctrl-G)"])
        self.cb_grid.bind(DGG.EXIT, self.tt.hide)
        x += 1*0.1 + 0.025
        btn = DirectButton(
            parent=self.menuBar,
            frameSize=(-0.5,0.5,-0.5,0.5),
            frameColor=buttonColor,
            pos=(x, 0, 0),
            scale=0.1,
            relief=DGG.FLAT,
            text_scale=0.33,
            command=base.messenger.send,
            extraArgs=["quitApp"],
            image="icons/Quit.png",
            image_scale=0.5)
        btn.setTransparency(TransparencyAttrib.M_multisample)
        btn.bind(DGG.ENTER, self.tt.show, ["Quit Direct GUI Designer (Ctrl-Q)"])
        btn.bind(DGG.EXIT, self.tt.hide)
        x += 1*0.1 + 0.025
        btn = DirectButton(
            parent=self.menuBar,
            frameSize=(-0.5,0.5,-0.5,0.5),
            frameColor=buttonColor,
            pos=(x, 0, 0),
            scale=0.1,
            relief=DGG.FLAT,
            text_scale=0.33,
            command=base.messenger.send,
            extraArgs=["showHelp"],
            image="icons/Help.png",
            image_scale=0.5)
        btn.setTransparency(TransparencyAttrib.M_multisample)
        btn.bind(DGG.ENTER, self.tt.show, ["Show a help Dialog (F1)"])
        btn.bind(DGG.EXIT, self.tt.hide)

    def toggleGrid(self, selection):
        base.messenger.send("toggleGrid", [selection])

    def resizeFrame(self):
        self.screenWidth = abs(base.a2dRight) + abs(base.a2dLeft)
        self.menuBar["frameSize"] = (0,self.screenWidth*(0.75),-0.05,0.05)
        self.menuBar.setPos(self.screenWidth*(0.25), 0, -0.05)
