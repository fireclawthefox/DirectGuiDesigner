from panda3d.core import ConfigVariableString

class CustomWidget():
    def __init__(self, dispName, clsName, clsFile, enabledProps, module):
        self.displayName = dispName
        self.className = clsName
        self.classFile = clsFile
        self.enabledProperties = enabledProps
        self.module = module

    def getPropFunctionName(self):
        return "properties{}".format(self.className)

    def getCreateFunctionName(self):
        return "create{}".format(self.className)

class DirectGuiDesignerCustomWidgets():
    def __init__(self, toolbox, elementHandler):
        self.toolboxExtensionList = ["~Custom Widgets~"]
        self.toolbox = toolbox
        self.elementHandler = elementHandler

    def loadCustomWidgets(self):
        path = ConfigVariableString("custom-widgets-path", []).getValue()
        configFiles = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.endswith(".widget")]

        for configFile in configFiles:
            configFileContent = None
            with open(configFile, 'r') as infile:
                configFileContent = json.load(infile)
            if configFileContent is None:
                logging.error("Problems reading widget config file: {}".format(infile))
                return

            spec = importlib.util.spec_from_file_location(configFileContent["moduleName"], configFileContent["classfilePath"])
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            #module.MyClass()
            #todo: fill dict with info about custom element modules
            #{name: class, other stuff like import path and such if that's not in the class itself}

            self.customWidgetsDict[configFileContent["name"]] = CustomWidget(
                configFileContent["displayName"],
                configFileContent["className"],
                configFileContent["classfilePath"],
                configFileContent["enabledProperties"],
                module)

        #modules = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.endswith(".py")]
        '''
        spec = importlib.util.spec_from_file_location("module.name", "/path/to/file.py")
        foo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(foo)
        foo.MyClass()
        todo: fill dict with info about custom element modules
        {name: class, other stuff like import path and such if that's not in the class itself}
        '''
        #print(modules)

    def extendToolbox(self):
        self.toolbox.toolboxEntries.append(self.toolboxExtensionList)
        self.toolbox.createEntries()

    def extendElementHandler(self):
        for widgetName, widget in self.widgetList.items():
            self.__createNewElement(widgetName, widget)

    def __createNewElement(self, widgetName, widget)
        self.toolboxExtensionList.append(widget.displayName, widgetName)

        # TODO: Maybe we need to go from the elementHandler back to the customWidgets class to gather information about the widget
        def propertiesMethod(self, element, elementDict):
            widget = customWidgets.getWidget(element)
            for propName in widget.enabledProperties:
                self.propertiesFrame.propertyList[propName] = True
            self.propertiesFrame.setupProperties("{} Properties".widget.displayName, element, elementDict)

        def createMethod(self, parent=None):
            widget = customWidgets.getWidget(element)
            parent = self.getEditorRootCanvas() if parent is None else parent
            pos = self.editorCenter if parent == self.getEditorRootCanvas() else (0,0,0)
            element = getattr(widget.module, widget.className)(
                parent=parent,
                pos=pos)
            elementInfo = ElementInfo(element, elementName)
            self.setupBind(elementInfo)
            return elementInfo

        setattr(self.elementHandler, widget.getPropFunctionName(), propertiesMethod)
        setattr(self.elementHandler, widget.getCreateFunctionName(), createMethod)
