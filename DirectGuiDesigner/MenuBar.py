from panda3d.core import TransparencyAttrib, ConfigVariableBool

from direct.showbase.DirectObject import DirectObject

from direct.gui import DirectGuiGlobals as DGG
DGG.BELOW = "below"

from direct.gui.DirectButton import DirectButton
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectCheckBox import DirectCheckBox
from DirectGuiExtension.DirectMenuItem import DirectMenuItem, DirectMenuItemEntry, DirectMenuItemSubMenu
from DirectGuiExtension.DirectBoxSizer import DirectBoxSizer

class MenuBar(DirectObject):
    def __init__(self, grid):
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
            pos=(0, 0, 0),
            itemMargin=(2,2,2,2),
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

        viewEntries = [
            DirectMenuItemEntry("Toggle Grid", base.messenger.send, ["toggleGrid", [not self.grid.isHidden()]]),
            DirectMenuItemEntry("Toggle Scale", base.messenger.send, ["toggleVisualEditorParent"])
        ]
        self.view = DirectMenuItem(
            text="View",
            text_fg=(1,1,1,1),
            text_scale=0.8,
            items=viewEntries,
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
            DirectMenuItemEntry("Undo", base.messenger.send, ["undo"]),
            DirectMenuItemEntry("Redo", base.messenger.send, ["redo"]),
            DirectMenuItemEntry("Cycle redos", base.messenger.send, ["cycleRedo"]),
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
