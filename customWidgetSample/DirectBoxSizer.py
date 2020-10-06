"""This module contains the DirectBoxSizer class."""

__all__ = ['DirectBoxSizer']

from panda3d.core import *
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectFrame import DirectFrame


DGG.HORIZONTAL_INVERTED = 'horizontal_inverted'


class DirectItemContainer():
    def __init__(self, element, **kw):
        self.element = element
        #if "stretch" in kw:
        #    if kw.get("stretch"):
        #        pass
        #    del kw["stretch"]
        #self.margin = VBase4(0,0,0,0)
        #if "margin" in kw:
        #    self.margin = kw.get("margin")

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

            ('orientation',    DGG.HORIZONTAL, self.refresh),
            ('itemMargin',     (0,0,0,0),  None),
            ('autoUpdateFrameSize', True,  None),
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
        # sanity check so we don't get here to early
        if not hasattr(self, "bounds"): return
        nextX = 0
        nextY = 0

        sizer_pad = self["pad"]

        b_top = 0
        b_bottom = 0
        b_left = 0
        b_right = 0

        margin_left = 0#self["itemMargin"][0]
        margin_right = 0#self["itemMargin"][1]
        margin_bottom = 0#self["itemMargin"][2]
        margin_top = 0#self["itemMargin"][3]

        if self["autoUpdateFrameSize"]:
            self["frameSize"] = (0, 0, 0, 0)

        if self['orientation'] == DGG.HORIZONTAL:
            # Left to Right
            for item in self["items"]:
                curElem = item.element
                scale = curElem.getScale()[0]
                pad = curElem["pad"][0]
                bw = -curElem["borderWidth"][0] * scale
                bound = curElem.bounds[0] * scale
                curElem.setPos(nextX - bound + margin_left - bw + sizer_pad[0], 0, sizer_pad[1])
                nextX = nextX + curElem.getWidth()*scale + margin_left + margin_right - pad - bw*2

                b_top = max(b_top, (curElem.bounds[3]*scale + pad - bw))
                b_bottom = min(b_bottom, (curElem.bounds[2]*scale - pad + bw))
                b_right = nextX

        elif self['orientation'] == DGG.HORIZONTAL_INVERTED:
            # Right to Left
            for item in self["items"]:
                curElem = item.element
                scale = curElem.getScale()[0]
                pad = -curElem["pad"][0]
                bw = curElem["borderWidth"][0] * scale
                bound = curElem.bounds[1] * scale
                curElem.setPos(nextX - bound - margin_right + bw + sizer_pad[0], 0, sizer_pad[1])
                nextX = nextX - curElem.getWidth()*scale - margin_left - margin_right + pad + bw*2

                b_top = max(b_top, (curElem.bounds[3]*scale + pad - bw))
                b_bottom = min(b_bottom, (curElem.bounds[2]*scale + pad - bw))
                b_left = nextX

        elif self['orientation'] == DGG.VERTICAL:
            # Top to Bottom
            for item in self["items"]:
                curElem = item.element
                scale = curElem.getScale()[2]
                pad = curElem["pad"][1]
                bw = curElem["borderWidth"][1] * scale
                bound = curElem.bounds[3] * scale
                curElem.setPos(sizer_pad[0], 0, nextY - bound - margin_top - bw + sizer_pad[1])
                nextY = nextY - curElem.getHeight()*scale - margin_top - margin_bottom - pad - bw*2

                b_bottom = nextY
                b_left = min(b_left, (curElem.bounds[0]*scale - pad - bw))
                b_right = max(b_right, (curElem.bounds[1]*scale + pad + bw))

        elif self['orientation'] == DGG.VERTICAL_INVERTED:
            # Bottom to Top
            for item in self["items"]:
                curElem = item.element
                scale = curElem.getScale()[2]
                pad = curElem["pad"][1]
                bw = curElem["borderWidth"][1] * scale
                bound = curElem.bounds[2] * scale
                curElem.setPos(sizer_pad[0], 0, nextY - bound + margin_bottom + bw + sizer_pad[1])
                nextY = nextY + curElem.getHeight()*scale + margin_top + margin_bottom + pad + bw*2

                b_top = nextY
                b_left = min(b_left, (curElem.bounds[0]*scale - pad - bw))
                b_right = max(b_right, (curElem.bounds[1]*scale + pad + bw))

        else:
            raise ValueError('Invalid value for orientation: %s' % (self['orientation']))

        if self["autoUpdateFrameSize"]:
            self["frameSize"] = (b_left+sizer_pad[0], b_right+sizer_pad[0], b_bottom+sizer_pad[1], b_top+sizer_pad[1])
