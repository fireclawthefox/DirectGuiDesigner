
#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file was created using the DirectGUI Designer

import os
import math

from direct.showbase.DirectObject import DirectObject
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

class DirectGuiDesignerFileBrowser(DirectObject):
    def __init__(self, command, fileBrowser=False, defaultPath="~", defaultFilename="export.json", tooltip=None):
        self.tt = tooltip
        if tooltip is None:
            raise Exception("No Tooltip instance given for File Browser")
        self.command = command
        self.showFiles = fileBrowser

        self.currentPath = os.path.expanduser(defaultPath)
        if not os.path.exists(self.currentPath):
            self.currentPath = os.path.expanduser("~")
        self.previousPath = self.currentPath

        self.screenWidthPx = base.getSize()[0]
        self.screenWidthPxHalf = self.screenWidthPx * 0.5
        self.screenHeightPx = base.getSize()[1]
        self.screenHeightPxHalf = self.screenHeightPx * 0.5

        self.mainFrame = DirectFrame(
            relief=1,
            frameSize=(-self.screenWidthPxHalf,self.screenWidthPxHalf,-self.screenHeightPxHalf,self.screenHeightPxHalf),
            frameColor=(1, 1, 1, 1),
            pos=LPoint3f(base.getSize()[0]/2, 0, -base.getSize()[1]/2),
            parent=base.pixel2d,
        )

        self.pathEntryWidth = self.screenWidthPx - 125

        self.pathEntry = DirectEntry(
            parent=self.mainFrame,
            relief=DGG.SUNKEN,
            frameColor=(1, 1, 1, 1),
            pad=(0.2, 0.2),
            pos=LPoint3f(-self.screenWidthPxHalf + 15, 0, self.screenHeightPxHalf - 25),
            scale=12,
            width=self.pathEntryWidth/12,
            overflow=True,
            command=self.entryAccept,
            initialText=self.currentPath,
            focusInCommand=base.messenger.send,
            focusInExtraArgs=["unregisterKeyboardEvents"],
            focusOutCommand=base.messenger.send,
            focusOutExtraArgs=["reregisterKeyboardEvents"],
        )
        x = self.pathEntryWidth/2-28
        self.btnReload = DirectButton(
            parent=self.mainFrame,
            relief=1,
            frameColor = (
                (0.8, 0.8, 0.8, 1), # Normal
                (0.9, 0.9, 1, 1), # Click
                (0.8, 0.8, 1, 1), # Hover
                (0.5, 0.5, 0.5, 1)), # Disabled
            frameSize=(-14, 14, -10, 18),
            pos=LPoint3f(x, 0, self.screenHeightPxHalf - 25),
            command=self.folderReload,
            image="icons/Reload.png",
            image_scale=14,
            image_pos=(0,0,4),
        )
        self.btnReload.setTransparency(TransparencyAttrib.M_multisample)
        self.btnReload.bind(DGG.ENTER, self.tt.show, ["Reload Folder"])
        self.btnReload.bind(DGG.EXIT, self.tt.hide)
        x += 28
        self.btnFolderUp = DirectButton(
            parent=self.mainFrame,
            relief=1,
            frameColor = (
                (0.8, 0.8, 0.8, 1), # Normal
                (0.9, 0.9, 1, 1), # Click
                (0.8, 0.8, 1, 1), # Hover
                (0.5, 0.5, 0.5, 1)), # Disabled
            frameSize=(-14, 14, -10, 18),
            pos=LPoint3f(x, 0, self.screenHeightPxHalf - 25),
            command=self.folderUp,
            image="icons/FolderUp.png",
            image_scale=14,
            image_pos=(0,0,4),
        )
        self.btnFolderUp.setTransparency(TransparencyAttrib.M_multisample)
        self.btnFolderUp.bind(DGG.ENTER, self.tt.show, ["Move up one level"])
        self.btnFolderUp.bind(DGG.EXIT, self.tt.hide)
        x += 28
        self.btnFolderNew = DirectButton(
            parent=self.mainFrame,
            relief=1,
            frameColor = (
                (0.8, 0.8, 0.8, 1), # Normal
                (0.9, 0.9, 1, 1), # Click
                (0.8, 0.8, 1, 1), # Hover
                (0.5, 0.5, 0.5, 1)), # Disabled
            frameSize=(-14, 14, -10, 18),
            pos=LPoint3f(x, 0, self.screenHeightPxHalf - 25),
            command=self.folderNew,
            image="icons/FolderNew.png",
            image_scale=14,
            image_pos=(0,0,4),
        )
        self.btnFolderNew.setTransparency(TransparencyAttrib.M_multisample)
        self.btnFolderNew.bind(DGG.ENTER, self.tt.show, ["Create new folder"])
        self.btnFolderNew.bind(DGG.EXIT, self.tt.hide)

        color = (
            (0.8, 0.8, 0.8, 1), # Normal
            (0.9, 0.9, 1, 1), # Click
            (0.8, 0.8, 1, 1), # Hover
            (0.5, 0.5, 0.5, 1)) # Disabled
        self.container = DirectScrolledFrame(
            relief=DGG.RIDGE,
            borderWidth=(2, 2),
            frameColor=(1, 1, 1, 1),
            frameSize=(-self.screenWidthPxHalf+10, self.screenWidthPxHalf-10, -self.screenHeightPxHalf+50, self.screenHeightPxHalf-50),
            canvasSize=(-self.screenWidthPxHalf+31, self.screenWidthPxHalf-10, -self.screenHeightPxHalf+50, self.screenHeightPxHalf-50),
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
            state=DGG.NORMAL,
        )
        self.container.bind(DGG.MWDOWN, self.scroll, [0.01])
        self.container.bind(DGG.MWUP, self.scroll, [-0.01])

        self.btnOk = DirectButton(
            parent=self.mainFrame,
            relief=1,
            frameColor = (
                (0.8, 0.8, 0.8, 1), # Normal
                (0.9, 0.9, 1, 1), # Click
                (0.8, 0.8, 1, 1), # Hover
                (0.5, 0.5, 0.5, 1)), # Disabled
            frameSize=(-45, 45, -6, 14),
            pos=LPoint3f(self.screenWidthPxHalf-160, 0, -self.screenHeightPxHalf+25),
            text = "ok",
            text_scale=12,
            command=command,
            extraArgs=[1],
        )
        self.btnCancel = DirectButton(
            parent=self.mainFrame,
            relief=1,
            frameColor = (
                (0.8, 0.8, 0.8, 1), # Normal
                (0.9, 0.9, 1, 1), # Click
                (0.8, 0.8, 1, 1), # Hover
                (0.5, 0.5, 0.5, 1)), # Disabled
            frameSize=(-45, 45, -6, 14),
            pos=LPoint3f(self.screenWidthPxHalf-55, 0, -self.screenHeightPxHalf+25),
            text = "Cancel",
            text_scale=12,
            command=command,
            extraArgs=[0]
        )

        if self.showFiles:
            self.txtFileName = DirectEntry(
                parent=self.mainFrame,
                relief=DGG.SUNKEN,
                frameColor=(1, 1, 1, 1),
                pad=(0.2, 0.2),
                pos=LPoint3f(-self.screenWidthPxHalf+25, 0, -self.screenHeightPxHalf+25),
                scale=12,
                width=200/12,
                overflow=True,
                command=self.filenameAccept,
                initialText=defaultFilename,
                focusInCommand=base.messenger.send,
                focusInExtraArgs=["unregisterKeyboardEvents"],
                focusOutCommand=base.messenger.send,
                focusOutExtraArgs=["reregisterKeyboardEvents"],
            )

        self.newFolderFrame = DirectFrame(
            parent=self.mainFrame,
            relief=1,
            frameSize=(-self.screenWidthPxHalf+10,self.screenWidthPxHalf-10,-20,20),
            pos=LPoint3f(0, 0, self.screenHeightPxHalf-55),
            frameColor=(0.5,0.5,0.5,1),
        )
        self.txtNewFolderName = DirectLabel(
            parent=self.newFolderFrame,
            text="New Folder Name",
            text_scale=12,
            frameColor=(0,0,0,0),
            text_align=TextNode.ALeft,
            pos=(-self.screenWidthPxHalf+15, 0, -3),
        )
        self.folderName = DirectEntry(
            parent=self.newFolderFrame,
            relief=DGG.SUNKEN,
            frameColor=(1, 1, 1, 1),
            pad=(0.2, 0.2),
            pos=LPoint3f(-self.screenWidthPxHalf+25 + self.txtNewFolderName.getWidth(), 0, -4),
            scale=12,
            width=((self.screenWidthPxHalf-25)*2-self.txtNewFolderName.getWidth() - 100)/12,
            overflow=True,
            command=self.entryAccept,
            initialText="New Folder",
            focusInCommand=base.messenger.send,
            focusInExtraArgs=["unregisterKeyboardEvents"],
            focusOutCommand=base.messenger.send,
            focusOutExtraArgs=["reregisterKeyboardEvents"],
        )
        self.btnCreate = DirectButton(
            parent=self.newFolderFrame,
            relief=1,
            frameColor = (
                (0.8, 0.8, 0.8, 1), # Normal
                (0.9, 0.9, 1, 1), # Click
                (0.8, 0.8, 1, 1), # Hover
                (0.5, 0.5, 0.5, 1)), # Disabled
            frameSize=(-45, 45, -6, 14),
            pos=LPoint3f(self.screenWidthPxHalf-65, 0, -4),
            text = "Create",
            text_scale=12,
            command=self.folderCreate,
            extraArgs=[0]
        )
        self.newFolderFrame.hide()

        self.folderReload()

        # handle window resizing
        self.prevScreenSize = base.getSize()
        self.accept("window-event", self.windowEventHandler)

    def show(self):
        self.mainFrame.show()
        self.accept("window-event", self.windowEventHandler)

    def hide(self):
        self.ignore("window-event")
        self.mainFrame.hide()

    def destroy(self):
        self.ignore("window-event")
        self.mainFrame.destroy()

    def scroll(self, scrollStep, event):
        self.container.verticalScroll.scrollStep(scrollStep)

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

        # start position for the folders and files
        xPos = -self.screenWidthPxHalf + 20 + 50 - 110
        zPos = self.screenHeightPxHalf-60-40

        dirList = []
        fileList = []
        unkList = []

        for entry in content:
            if entry.is_dir():
                dirList.append(entry)
            elif entry.is_file() and self.showFiles:
                fileList.append(entry)
            elif self.showFiles:
                unkList.append(entry)

        def moveNext(entry):
            nonlocal xPos
            nonlocal zPos
            if entry.is_dir() or self.showFiles:
                if xPos + 110 > self.screenWidthPxHalf - 45:
                    # move to the next line if we hit the right border (incl. scrollbar size)
                    xPos = -self.screenWidthPxHalf + 20 + 50
                    zPos -= 110
                else:
                    # move right the next position
                    xPos += 110

        def getKey(item):
            return item.name.lower()

        for entry in sorted(dirList, key=getKey):
            moveNext(entry)
            self.__createFolder(entry, xPos, zPos)
        for entry in sorted(fileList, key=getKey):
            moveNext(entry)
            self.__createFile(entry.name, xPos, zPos)
        for entry in sorted(unkList, key=getKey):
            moveNext(entry)
            self.__createUnknown(entry.name, xPos, zPos)

        # recalculate the canvas size
        self.container["canvasSize"] = (-self.screenWidthPxHalf+31, self.screenWidthPxHalf-15, zPos-90, self.screenHeightPxHalf-50)
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
            base.messenger.send("showWarning", ["Can't create folder"])
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
        btn.bind(DGG.MWDOWN, self.scroll, [0.01])
        btn.bind(DGG.MWUP, self.scroll, [-0.01])
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
        btn.bind(DGG.MWDOWN, self.scroll, [0.01])
        btn.bind(DGG.MWUP, self.scroll, [-0.01])
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
        lbl.bind(DGG.MWDOWN, self.scroll, [0.01])
        lbl.bind(DGG.MWUP, self.scroll, [-0.01])
        lbl.setTransparency(TransparencyAttrib.M_multisample)


    def windowEventHandler(self, window=None):
        if window != base.win:
            # This event isn't about our window.
            return

        if window is not None: # window is none if panda3d is not started
            if self.prevScreenSize == base.getSize():
                return
            self.prevScreenSize = base.getSize()
            self.screenWidthPx = base.getSize()[0]
            self.screenWidthPxHalf = self.screenWidthPx * 0.5
            self.screenHeightPx = base.getSize()[1]
            self.screenHeightPxHalf = self.screenHeightPx * 0.5

            # reposition and resize all gui elements
            self.mainFrame.setPos(self.screenWidthPx/2, 0, -self.screenHeightPx/2)
            self.mainFrame["frameSize"] = (-self.screenWidthPxHalf,self.screenWidthPxHalf,-self.screenHeightPxHalf,self.screenHeightPxHalf)
            self.pathEntryWidth = self.screenWidthPx - 125
            self.pathEntry.setPos(LPoint3f(-self.screenWidthPxHalf + 15, 0, self.screenHeightPxHalf - 25))
            self.pathEntry["width"] = self.pathEntryWidth/12
            x = self.pathEntryWidth/2-28
            self.btnReload.setPos(LPoint3f(x, 0, self.screenHeightPxHalf - 25))
            x += 28
            self.btnFolderUp.setPos(pos=LPoint3f(x, 0, self.screenHeightPxHalf - 25))
            x += 28
            self.btnFolderNew.setPos(pos=LPoint3f(x, 0, self.screenHeightPxHalf - 25))
            self.container["frameSize"] = (-self.screenWidthPxHalf+10, self.screenWidthPxHalf-10, -self.screenHeightPxHalf+50, self.screenHeightPxHalf-50)
            # Note: canvas size of the container will be reset in the
            #       folder Reload call at the end of this function
            self.btnOk.setPos(LPoint3f(self.screenWidthPxHalf-160, 0, -self.screenHeightPxHalf+25))
            self.btnCancel.setPos(LPoint3f(self.screenWidthPxHalf-55, 0, -self.screenHeightPxHalf+25))
            if self.showFiles:
                self.txtFileName.setPos(LPoint3f(-self.screenWidthPxHalf+25, 0, -self.screenHeightPxHalf+25))
            self.newFolderFrame.setPos(LPoint3f(0, 0, self.screenHeightPxHalf-55))
            self.newFolderFrame["frameSize"] = (-self.screenWidthPxHalf+10,self.screenWidthPxHalf-10,-20,20)
            self.txtNewFolderName.setPos(-self.screenWidthPxHalf+15, 0, -3)
            self.folderName.setPos(LPoint3f(-self.screenWidthPxHalf+25 + self.txtNewFolderName.getWidth(), 0, -4))
            self.folderName["width"]=((self.screenWidthPxHalf-25)*2-self.txtNewFolderName.getWidth() - 100)/12
            self.btnCreate.setPos(LPoint3f(self.screenWidthPxHalf-65, 0, -4))

            self.folderReload()
