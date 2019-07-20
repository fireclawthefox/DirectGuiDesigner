
#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file was created using the DirectGUI Designer

import os
import math

from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectEntry import DirectEntry
from direct.gui.DirectScrolledFrame import DirectScrolledFrame
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectLabel import DirectLabel
from panda3d.core import (
    LPoint3f,
    LVecBase3f,
    LVecBase4f,
    TransparencyAttrib,
    TextNode
)

class DirectGuiDesignerFileBrowser:
    def __init__(self, command, fileBrowser=False, defaultFilename="export.json", tooltip=None):
        self.tt = tooltip
        self.command = command
        self.showFiles = fileBrowser

        self.currentPath = os.path.expanduser("~")
        self.previousPath = self.currentPath

        self.mainFrame = DirectFrame(
            relief=1,
            frameSize=(-300,300,-200,200),
            frameColor=(1, 1, 1, 1),
            pos=LPoint3f(base.getSize()[0]/2, 0, -base.getSize()[1]/2),
            parent=base.pixel2d,
        )

        self.show = self.mainFrame.show
        self.hide = self.mainFrame.hide
        self.destroy = self.mainFrame.destroy

        self.pathEntry = DirectEntry(
            parent=self.mainFrame,
            relief=DGG.SUNKEN,
            frameColor=(1, 1, 1, 1),
            pad=(0.2, 0.2),
            pos=LPoint3f(-285, 0, 175),
            scale=12,
            width=475/12,
            overflow=True,
            command=self.entryAccept,
            initialText=self.currentPath
        )
        x = 475/2-28
        btn = DirectButton(
            parent=self.mainFrame,
            relief=1,
            frameColor = (
                (0.8, 0.8, 0.8, 1), # Normal
                (0.9, 0.9, 1, 1), # Click
                (0.8, 0.8, 1, 1), # Hover
                (0.5, 0.5, 0.5, 1)), # Disabled
            frameSize=(-14, 14, -10, 18),
            pos=LPoint3f(x, 0, 175),
            text = "( )",
            text_scale=12,
            command=self.folderReload
        )
        btn.bind(DGG.ENTER, self.tt.show, ["Reload Folder"])
        btn.bind(DGG.EXIT, self.tt.hide)
        x += 28
        btn = DirectButton(
            parent=self.mainFrame,
            relief=1,
            frameColor = (
                (0.8, 0.8, 0.8, 1), # Normal
                (0.9, 0.9, 1, 1), # Click
                (0.8, 0.8, 1, 1), # Hover
                (0.5, 0.5, 0.5, 1)), # Disabled
            frameSize=(-14, 14, -10, 18),
            pos=LPoint3f(x, 0, 175),
            text = "^",
            text_scale=12,
            command=self.folderUp
        )
        btn.bind(DGG.ENTER, self.tt.show, ["Move up one level"])
        btn.bind(DGG.EXIT, self.tt.hide)
        x += 28
        btn = DirectButton(
            parent=self.mainFrame,
            relief=1,
            frameColor = (
                (0.8, 0.8, 0.8, 1), # Normal
                (0.9, 0.9, 1, 1), # Click
                (0.8, 0.8, 1, 1), # Hover
                (0.5, 0.5, 0.5, 1)), # Disabled
            frameSize=(-14, 14, -10, 18),
            pos=LPoint3f(x, 0, 175),
            text = "+",
            text_scale=12,
            command=self.folderNew
        )
        btn.bind(DGG.ENTER, self.tt.show, ["Create new folder"])
        btn.bind(DGG.EXIT, self.tt.hide)

        color = (
            (0.8, 0.8, 0.8, 1), # Normal
            (0.9, 0.9, 1, 1), # Click
            (0.8, 0.8, 1, 1), # Hover
            (0.5, 0.5, 0.5, 1)) # Disabled
        self.container = DirectScrolledFrame(
            relief=DGG.SUNKEN,
            frameColor=(1, 1, 1, 1),
            frameSize=(-290, 290, -150, 150),
            canvasSize=(-269, 290, -150, 150),
            pos=LPoint3f(0, 0, 0),
            parent=self.mainFrame,
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
        )

        DirectButton(
            parent=self.mainFrame,
            relief=1,
            frameColor = (
                (0.8, 0.8, 0.8, 1), # Normal
                (0.9, 0.9, 1, 1), # Click
                (0.8, 0.8, 1, 1), # Hover
                (0.5, 0.5, 0.5, 1)), # Disabled
            frameSize=(-45, 45, -6, 14),
            pos=LPoint3f(140, 0, -185),
            text = "ok",
            text_scale=12,
            command=command,
            extraArgs=[1],
        )
        DirectButton(
            parent=self.mainFrame,
            relief=1,
            frameColor = (
                (0.8, 0.8, 0.8, 1), # Normal
                (0.9, 0.9, 1, 1), # Click
                (0.8, 0.8, 1, 1), # Hover
                (0.5, 0.5, 0.5, 1)), # Disabled
            frameSize=(-45, 45, -6, 14),
            pos=LPoint3f(245, 0, -185),
            text = "Cancel",
            text_scale=12,
            command=command,
            extraArgs=[0]
        )

        self.txtFileName = DirectEntry(
            parent=self.mainFrame,
            relief=DGG.SUNKEN,
            frameColor=(1, 1, 1, 1),
            pad=(0.2, 0.2),
            pos=LPoint3f(-275, 0, -185),
            scale=12,
            width=200/12,
            overflow=True,
            command=self.filenameAccept,
            initialText=defaultFilename,
        )

        self.newFolderFrame = DirectFrame(
            parent=self.mainFrame,
            relief=1,
            frameSize=(-290,290,-20,20),
            pos=LPoint3f(0, 0, 145),
            frameColor=(0.5,0.5,0.5,1),
        )
        txtNewFolderName = DirectLabel(
            parent=self.newFolderFrame,
            text="New Folder Name",
            text_scale=12,
            frameColor=(0,0,0,0),
            text_align=TextNode.ALeft,
            pos=(-285, 0, -3),
        )
        self.folderName = DirectEntry(
            parent=self.newFolderFrame,
            relief=DGG.SUNKEN,
            frameColor=(1, 1, 1, 1),
            pad=(0.2, 0.2),
            pos=LPoint3f(-275 + txtNewFolderName.getWidth(), 0, -4),
            scale=12,
            width=(275*2-txtNewFolderName.getWidth() - 100)/12,
            overflow=True,
            command=self.entryAccept,
            initialText="New Folder"
        )
        DirectButton(
            parent=self.newFolderFrame,
            relief=1,
            frameColor = (
                (0.8, 0.8, 0.8, 1), # Normal
                (0.9, 0.9, 1, 1), # Click
                (0.8, 0.8, 1, 1), # Hover
                (0.5, 0.5, 0.5, 1)), # Disabled
            frameSize=(-45, 45, -6, 14),
            pos=LPoint3f(235, 0, -4),
            text = "Create",
            text_scale=12,
            command=self.folderCreate,
            extraArgs=[0]
        )
        self.newFolderFrame.hide()

        self.folderReload()

    def get(self):
        if self.showFiles:
            return os.path.join(self.currentPath, self.txtFileName.get(True))
        return self.currentPath

    def filenameAccept(self, filename):
        self.command(1)

    def entryAccept(self, path):
        self.folderReload()

    def folderReload(self):

        for element in self.container.getCanvas().getChildren():
            element.removeNode()

        path = self.pathEntry.get(True)
        path = os.path.expanduser(path)
        path = os.path.expandvars(path)
        if not os.path.exists(path): return
        self.currentPath = path

        try:
            content = os.scandir(path)
        except PermissionError:
            base.messenger.send("showWarning", ["Access denied!"])
            self.pathEntry.set(self.previousPath)
            self.currentPath = self.previousPath
            self.folderReload()
            return

        xPos = -280 + 50 - 110
        zPos = 140-40
        for entry in content:
            if entry.is_dir() or self.showFiles:
                if xPos + 110 > 290:
                    xPos = -280 + 50 - 110
                    zPos -= 110
                else:
                    xPos += 110

            if entry.is_dir():
                self.__createFolder(entry, xPos, zPos)
            elif entry.is_file() and self.showFiles:
                self.__createFile(entry.name, xPos, zPos)
            elif self.showFiles:
                self.__createUnknown(entry.name, xPos, zPos)

        self.container["canvasSize"] = (-269, 290, zPos-90, 150)
        self.container.setCanvasSize()

    def folderUp(self):
        self.previousPath = self.currentPath
        self.currentPath = os.path.normpath(os.path.join(self.currentPath, ".."))
        self.pathEntry.set(self.currentPath)
        self.folderReload()

    def folderMoveIn(self, path):
        path = os.path.expanduser(path)
        path = os.path.expandvars(path)
        self.previousPath = self.currentPath
        self.currentPath = path
        self.pathEntry.set(path)
        self.folderReload()
        self.container.verticalScroll["value"] = 0

    def folderNew(self):
        if self.newFolderFrame.isHidden():
            self.newFolderFrame.show()
        else:
            self.newFolderFrame.hide()

    def folderCreate(self, path=""):
        try:
            os.makedirs(os.path.join(self.currentPath, self.folderName.get(True)))
        except:
            print("Can't create folder")
        self.newFolderFrame.hide()
        self.folderReload()

    def __createFolder(self, entry, xPos, zPos):
        name = entry.name
        if len(entry.name) > 10:
            name = ""
            for i in range(max(math.ceil(len(entry.name)/10), 4)):
                name += entry.name[i*10:i*10+10]+"\n"
            name = name[:-1]
            if math.ceil(len(entry.name)/10) > 4:
                name += "..."
        btn = DirectButton(
            parent=self.container.getCanvas(),
            image="icons/Folder.png",
            image_scale=35,
            relief=1,
            frameColor = (
                (0.9, 0.9, 0.9, 0), # Normal
                (0.95, 0.95, 1, 1), # Click
                (0.9, 0.9, 1, 1), # Hover
                (0.5, 0.5, 0.5, 1)), # Disabled
            frameSize=(-40, 40, -40, 40),
            pos=LPoint3f(xPos, 0, zPos),
            text = name,
            text_scale=12,
            text_pos=(0,-40),
            command=self.folderMoveIn,
            extraArgs=[entry.path]
        )
        btn.setTransparency(TransparencyAttrib.M_multisample)

    def __createFile(self, filename, xPos, zPos):
        name = filename
        if len(filename) > 10:
            name = ""
            for i in range(min(math.ceil(len(filename)/10), 4)):
                name += filename[i*10:i*10+10]+"\n"
            name = name[:-1]
            if math.ceil(len(filename)/10) > 4:
                name += "..."
        btn = DirectButton(
            parent=self.container.getCanvas(),
            image="icons/File.png",
            image_scale=35,
            relief=1,
            frameColor = (
                (0.9, 0.9, 0.9, 0), # Normal
                (0.95, 0.95, 1, 1), # Click
                (0.9, 0.9, 1, 1), # Hover
                (0.5, 0.5, 0.5, 1)), # Disabled
            frameSize=(-40, 40, -40, 40),
            pos=LPoint3f(xPos, 0, zPos),
            text = name,
            text_scale=12,
            text_pos=(0,-40),
            command=self.txtFileName.set,
            extraArgs=[filename]
        )
        btn.setTransparency(TransparencyAttrib.M_multisample)

    def __createUnknown(self, filename, xPos, zPos):
        name = filename
        if len(filename) > 10:
            name = ""
            for i in range(math.ceil(len(filename)/10)):
                name += filename[i*10:i*10+10]+"\n"
            name = name[:-1]
        lbl = DirectLabel(
            parent=self.container.getCanvas(),
            image="icons/File.png",
            image_scale=35,
            image_color=(0.9,0.5,0.5,1),
            relief=1,
            frameColor = (0.7, 0.7, 0.7, 0),
            frameSize=(-40, 40, -40, 40),
            pos=LPoint3f(xPos, 0, zPos),
            text = name,
            text_scale=12,
            text_pos=(0,-40),
        )
        lbl.setTransparency(TransparencyAttrib.M_multisample)
