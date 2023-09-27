"""The KillRing is where the information is stored to be able to undo/redo actions.
You can think of it as a tree, where every action enlarges a branch.
You can always undo and if you do something new afterward, it will create a new branch with new information.
Changing between branches is fine from the toolbar or with a key combination.
It's inspired by emacs kill-ring.
"""


class KillRingEntry:
    """A KillRingEntry stores the information needed to undo/redo a specific action.
    It also stores some information about where in the KillRings 'tree' the action is.
    """
    def __init__(self, editObject=None, action="", objectType="", oldValue=None, newValue=None):
        self.activeChild = None  # the currently selected child entry
        self.children = []  # list of all children of self (actions that came after self)
        self.parent = None  # the action preceding self

        self.editObject = editObject  # The object that was changed
        self.action = action  # Some tag to know what type of change it was
        self.objectType = objectType  # Another tag to further specify how to handle the action
        self.oldValue = oldValue  # The old value
        self.newValue = newValue  # The new value

    def addChild(self, child):
        """Add a new child entry to self and set it as the active child.

        :param KillRingEntry child: The new child
        """
        self.children.append(child)
        self.activeChild = child

    def setParent(self, parent):
        """Set 'parent' as parent of self.

        :param KillRingEntry parent: The new parent
        """
        self.parent = parent

    def cycleChildren(self):
        """Set next entry in 'self.children' as active child."""
        if len(self.children) < 2: return
        self.children = self.children[-1:] + self.children[:-1]
        self.activeChild = self.children[-1]


class KillRing:
    """Class for storing and retrieving information needed for undo/redo.
    Actually undoing/redoing actions is not handled in this class.
    """
    def __init__(self):
        self.currentRoot = KillRingEntry()  # the currently selected entry
        self.currentRoot.setParent(self.currentRoot)

    def push(self, editObject, action, objectType, oldValue, newValue):
        """Add new action to KillRing.

        :param editObject: The object that was changed
        :param str action: Some tag to know what type of change it was
        :param str objectType: Another tag to further specify how to handle the action
        :param oldValue: The old value
        :param newValue: The new value
        """
        newKill = KillRingEntry(editObject, action, objectType, oldValue, newValue)
        self.currentRoot.addChild(newKill)
        newKill.setParent(self.currentRoot)
        self.currentRoot = newKill

    def pop(self):
        """Revert last push. Change current root to the parent of the current root.

        :return: The old current root
        """
        if self.currentRoot.parent is self.currentRoot: return None
        root = self.currentRoot
        self.currentRoot = self.currentRoot.parent
        return root

    def pull(self):
        """Revert last pop. Change current root to the active child of the current root.

        :return: The new current root
        """
        if self.currentRoot.activeChild is None: return
        self.currentRoot = self.currentRoot.activeChild
        return self.currentRoot

    def cycleChildren(self):
        """Cycle children of current root."""
        # change the active child to the next one in the active kill ring entry
        self.currentRoot.cycleChildren()
