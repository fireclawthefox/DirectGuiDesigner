"""This module contains the DirectBoxSizer class."""

__all__ = ['DirectBoxSizer']

from panda3d.core import *
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectFrame import DirectFrame


DGG.HORIZONTAL_INVERTED = 'horizontal_inverted'


class DirectItemContainer():
    def __init__(self, element, **kw):
        self.element = element
        if "stretch" in kw:
            if kw.get("stretch"):
                pass
            del kw["stretch"]
        self.margin = VBase4(0,0,0,0)
        if "margin" in kw:
            self.margin = kw.get("margin")

class DirectBoxSizer(DirectFrame):
    """
    TODO
    """
    def __init__(self, parent = None, **kw):
        optiondefs = (
            # Define type of DirectGuiWidget
            ('items',          [],         None),
            ('pgFunc',         PGItem,     None),
            ('numStates',      1,          None),
            ('state',          DGG.NORMAL, None),#self.inactiveInitState, None),

            ('orientation',    DGG.HORIZONTAL, None),
            ('itemMargin',     (0,0,0,0),  None),
            )
        # Merge keyword options with default options
        self.defineoptions(kw, optiondefs)

        # Initialize superclasses
        DirectFrame.__init__(self, parent)

        # Call option initialization functions
        self.initialiseoptions(DirectBoxSizer)

    def addItem(self, element, **kw):
        element.reparentTo(self)
        container = DirectItemContainer(element, **kw)
        self["items"].append(container)
        self.refresh()

    def removeItem(self, element):
        """
        Remove this item from the panel
        """
        for item in self["items"]:
            if element == item.element:
                self["items"].remove(item)
                self.refresh()
                return 1
        return 0

    def refresh(self):
        bounds = self.bounds

        if self['orientation'] == DGG.HORIZONTAL:
            # Left to Right
            nextX = bounds[0]
            for item in self["items"]:
                curElem = item.element
                scale = curElem.getScale()[0]
                elemBounds = curElem.bounds
                curElem.setPos(nextX - elemBounds[0]*scale + item.margin[0], 0, self.getCenter()[1])
                nextX = nextX + curElem.getWidth()*scale + item.margin[0] + item.margin[1]

        elif self['orientation'] == DGG.HORIZONTAL_INVERTED:
            # Right to Left
            nextX = bounds[1]
            for item in self["items"]:
                curElem = item.element
                scale = curElem.getScale()[0]
                elemBounds = curElem.bounds
                curElem.setPos(nextX - elemBounds[1]*scale - item.margin[1], 0, self.getCenter()[1])
                nextX = nextX - curElem.getWidth()*scale - item.margin[0] - item.margin[1]

        elif self['orientation'] == DGG.VERTICAL:
            # Top to Bottom
            nextY = bounds[3]
            for item in self["items"]:
                curElem = item.element
                scale = curElem.getScale()[2]
                elemBounds = curElem.bounds
                curElem.setPos(self.getCenter()[0], 0, nextY - elemBounds[3]*scale - item.margin[3])
                nextY = nextY - curElem.getHeight()*scale - item.margin[3] - item.margin[2]

        elif self['orientation'] == DGG.VERTICAL_INVERTED:
            # Bottom to Top
            nextY = bounds[2]
            for item in self["items"]:
                curElem = item.element
                scale = curElem.getScale()[2]
                elemBounds = curElem.bounds
                curElem.setPos(self.getCenter()[0], 0, nextY - elemBounds[2]*scale + item.margin[2])
                nextY = nextY + curElem.getHeight()*scale + item.margin[3] + item.margin[2]

        else:
            raise ValueError('Invalid value for orientation: %s' % (self['orientation']))
