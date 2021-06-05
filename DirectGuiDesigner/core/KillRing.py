
class KillRingEntry():
    def __init__(self, editObject=None, action="", objectType="", oldValue=None, newValue=None):
        self.activeChild = None
        self.children = []
        self.parent = None

        self.editObject = editObject
        self.action = action
        self.objectType = objectType
        self.oldValue = oldValue
        self.newValue = newValue

    def addChild(self, child):
        self.children.append(child)
        self.activeChild = child

    def setParent(self, parent):
        self.parent = parent

    def cycleChildren(self):
        if len(self.children) < 2: return
        self.children = self.children[-1:] + self.children[:-1]
        self.activeChild = self.children[-1]

class KillRing():
    def __init__(self):
        self.currentRoot = KillRingEntry()
        self.currentRoot.setParent(self.currentRoot)

    def push(self, editObject, action, objectType, oldValue, newValue):
        newKill = KillRingEntry(editObject, action, objectType, oldValue, newValue)
        self.currentRoot.addChild(newKill)
        newKill.setParent(self.currentRoot)
        self.currentRoot = newKill

    def pop(self):
        # revert last push
        if self.currentRoot.parent is self.currentRoot: return None
        root = self.currentRoot
        self.currentRoot = self.currentRoot.parent
        return root

    def pull(self):
        # revert last pop
        if self.currentRoot.activeChild is None: return
        self.currentRoot = self.currentRoot.activeChild
        return self.currentRoot

    def cycleChildren(self):
        # change the active child to the next one in the active kill ring entry
        self.currentRoot.cycleChildren()
