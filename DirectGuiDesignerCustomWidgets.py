import os
import logging
import json
import importlib
import pathlib
from panda3d.core import ConfigVariableString
from DirectGuiDesignerProperties import PropertyInfo

class CustomWidget():
    def __init__(self, dispName, clsName, clsFile, enabledProps, customProperties, module, addItemFunction, removeItemFunction, importPath):
        self.displayName = dispName
        self.className = clsName
        self.classFile = clsFile
        self.enabledProperties = enabledProps
        self.customProperties = customProperties
        self.module = module
        self.addItemFunction = addItemFunction
        self.removeItemFunction = removeItemFunction
        self.importPath = importPath

    def getPropFunctionName(self):
        return "properties{}".format(self.className)

    def getCreateFunctionName(self):
        return "create{}".format(self.className)

class DirectGuiDesignerCustomWidgets():
    def __init__(self, toolbox, elementHandler):
        self.toolboxExtensionList = [["~Custom Widgets~"]]
        self.toolbox = toolbox
        self.elementHandler = elementHandler
        self.customWidgetsDict = {}

    def loadCustomWidgets(self):
        configFiles = []
        defaultPath = str(pathlib.PurePosixPath(__file__).parent) + "/widgets"
        if os.path.exists(defaultPath):
            configFiles = [f for f in os.listdir(defaultPath) if os.path.isfile(os.path.join(path, f)) and f.endswith(".widget")]

        path = ConfigVariableString("custom-widgets-path", "").getValue()
        if path != "" and os.path.exists(path):
            # get a list of all .widget files
            configFiles.extend([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.endswith(".widget")])

        logging.info("no custom widgets found.")


        for configFile in configFiles:
            configFileContent = None
            with open(os.path.join(path, configFile), 'r') as infile:
                configFileContent = json.load(infile)
            if configFileContent is None:
                logging.error("Problems reading widget config file: {}".format(infile))
                continue
            pythonFilePath = os.path.join(path, configFileContent["classfilePath"])
            spec = None
            if pythonFilePath.endswith(".py"):
                spec = importlib.util.spec_from_file_location(configFileContent["moduleName"], pythonFilePath)
            else:
                spec = importlib.util.find_spec(configFileContent["classfilePath"])
            if spec is None:
                print("spec is None")
                print(spec)
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            customProperties = []
            if "customProperties" in configFileContent:
                for prop in configFileContent["customProperties"]:
                    command = prop["customCommandName"] if "customCommandName" in prop else None
                    selectionDict = prop["customSelectionDict"] if "customSelectionDict" in prop else None
                    customProperties.append(PropertyInfo(prop["displayName"], prop["propertyName"], prop["propertyType"], command, selectionDict))

            self.customWidgetsDict[configFileContent["name"]] = CustomWidget(
                configFileContent["displayName"],
                configFileContent["className"],
                configFileContent["classfilePath"],
                configFileContent["enabledProperties"],
                customProperties,
                module,
                configFileContent["addItemFunctionName"] if "addItemFunctionName" in configFileContent else None,
                configFileContent["removeItemFunctionName"] if "removeItemFunctionName" in configFileContent else None,
                configFileContent["importPath"])
            self.toolboxExtensionList.append([configFileContent["displayName"], configFileContent["className"]])
        self.extendToolbox()
        self.extendElementHandler()

    def extendToolbox(self):
        self.toolbox.toolboxEntries += self.toolboxExtensionList
        self.toolbox.createEntries()

    def getWidget(self, widgetName):
        if widgetName in self.customWidgetsDict.keys():
            return self.customWidgetsDict[widgetName]
        return None

    def extendElementHandler(self):
        for widgetName, widget in self.customWidgetsDict.items():
            self.__createNewElement(widgetName, widget)

    def __createNewElement(self, widgetName, widget):
        self.elementHandler.createCustomWidgetMethods(widget)

