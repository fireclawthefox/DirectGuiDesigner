class ElementInfo:
    """Wrapper around a GUI element to hold some extra information."""
    def __init__(self, element, elementType, name=None, parent=None, extraOptions=None, createAfter=None, customImportPath=None, addItemExtraArgs=None, addItemNode=None):
        # The actual GUI element
        self.element = element

        # Name of the element type
        self.type = elementType

        # Visible Name (Node-Name) of the element
        if name is not None:
            self.name = name
        else:
            self.name = element.guiId.replace("-","")

        # The ElementInfo or NodePath of the Parent of this element
        self.parent = parent

        # A dictionary of options and their values
        if extraOptions is not None:
            self.extraOptions = extraOptions
        else:
            self.extraOptions = {}

        # The command to be called by the element
        self.command = None

        # Extra arguments to be passed to the command
        self.extraArgs = None

        # elements after which have to be created first, prior to creating this
        if createAfter is not None:
            self.createAfter = createAfter
        else:
            self.createAfter = []

        self.customImportPath = customImportPath

        self.subComponentName = ""
        self.valueHasChanged = {}

        # extra args to be passed when reparenting to the current parent
        if addItemExtraArgs is None:
            self.addItemExtraArgs = []
        else:
            self.addItemExtraArgs = addItemExtraArgs

        self.addItemNode = addItemNode

    def __str__(self):
        return f"""ELEMENT INFO:
            Element: {self.element}
            Element Type: {self.type}
            Name: {self.name}
            Parent: {self.parent}
            Extra Options: {self.extraOptions}
            Create After: {self.createAfter}
            Custom import path: {self.customImportPath}
            Command: {self.command}
            Extra Args: {self.extraArgs}
            Sub Component Name: {self.subComponentName}
            Changed Values: {self.valueHasChanged}
            Extra args to addItemFunc: {self.addItemExtraArgs}
            Parent Node: {self.addItemNode}
            """
