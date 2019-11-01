import os
import logging
import json
import importlib
from panda3d.core import ConfigVariableString

class CustomWidget():
    def __init__(self, dispName, clsName, clsFile, enabledProps, module, addItemFunction, removeItemFunction, importPath):
        self.displayName = dispName
        self.className = clsName
        self.classFile = clsFile
        self.enabledProperties = enabledProps
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
        path = ConfigVariableString("custom-widgets-path", "").getValue()
        if path == "": return
        if not os.path.exists(path):
            if path != "":
                logging.error("custom widgets path doesn't exist!")
                return

        configFiles = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.endswith(".widget")]

        for configFile in configFiles:
            configFileContent = None
            with open(os.path.join(path, configFile), 'r') as infile:
                configFileContent = json.load(infile)
            if configFileContent is None:
                logging.error("Problems reading widget config file: {}".format(infile))
                return
            pythonFilePath = os.path.join(path, configFileContent["classfilePath"])
            spec = importlib.util.spec_from_file_location(configFileContent["moduleName"], pythonFilePath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            self.customWidgetsDict[configFileContent["name"]] = CustomWidget(
                configFileContent["displayName"],
                configFileContent["className"],
                configFileContent["classfilePath"],
                configFileContent["enabledProperties"],
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

