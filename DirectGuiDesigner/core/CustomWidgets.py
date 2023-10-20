import os
import logging
import json
import importlib
import pathlib
import sys
import types
from panda3d.core import ConfigVariableString
from DirectGuiDesigner.core.WidgetDefinition import PropertyEditTypes, Definition, DEFINITIONS
from DirectGuiDesigner.dialogs.AddItemDialog import AddByFunction, AddByNode
from DirectGuiDesigner.core.ElementInfo import ElementInfo


class CustomWidget:
    def __init__(self, dispName, clsName, clsFile, module, addItemFunction, addItemExtraArgs, addItemNode, removeItemFunction, importPath):
        self.displayName = dispName
        self.className = clsName
        self.classFile = clsFile
        self.module = module
        self.addItemFunction = addItemFunction
        self.addItemExtraArgs = addItemExtraArgs
        self.addItemNode = addItemNode
        self.removeItemFunction = removeItemFunction
        self.importPath = importPath

    def getPropFunctionName(self):
        return "properties{}".format(self.className)

    def getCreateFunctionName(self):
        return "create{}".format(self.className)

    def callAddItemFunc(self, parentInfo, childInfo, forceOpenDialog=False):
        """Handle all edge cases for adding a new item to a custom element.

        :param parentInfo: The elementInfo of the element to add to
        :param childInfo: The elementInfo of the element to add
        """
        if isinstance(parentInfo, ElementInfo):
            parent = parentInfo.element
        else:
            parent = parentInfo
        child = childInfo.element

        if self.addItemFunction is not None:
            self.__addByFunction(child, parent, childInfo, forceOpenDialog)

        # reparent child to node specified in addItemNode
        if self.addItemNode is not None:
            self.__AddByNode(child, parent, childInfo, forceOpenDialog)

    def __AddByNode(self, child, parent, childInfo, forceOpenDialog=False):
        if isinstance(self.addItemNode, list):
            if childInfo.addItemNode is not None and not forceOpenDialog:
                node = childInfo.addItemNode
            else:
                AddByNode(self, child, childInfo, parent)
                return

        else:
            node = self.addItemNode

        childInfo.addItemNode = node
        node = getattr(parent, node)
        child.reparentTo(node)

    def __addByFunction(self, child, parent, childInfo, forceOpenDialog=False):
        func = getattr(parent, self.addItemFunction)
        if self.addItemExtraArgs is None:
            func(child)
            return

        # call with extra args if they are provided
        extraArgs = []
        if isinstance(self.addItemExtraArgs, list):
            extraArgs = self.addItemExtraArgs
        elif isinstance(self.addItemExtraArgs, dict):
            if childInfo.addItemExtraArgs and not forceOpenDialog:
                extraArgs = childInfo.addItemExtraArgs

            else:
                AddByFunction(self, child, childInfo, func)
                return

        else:
            print("addItemExtraArgs should be of type 'list' or 'dict'")

        childInfo.addItemExtraArgs = extraArgs
        try:
            func(child, *extraArgs)
        except Exception:
            print("error running addItemFunc")


class CustomWidgets:

    customWidgetsDict = {}
    customWidgetDefinitions = {}

    def __init__(self, toolbox, elementHandler):
        self.toolboxExtensionList = [["~Custom Widgets~"]]
        self.toolbox = toolbox
        self.elementHandler = elementHandler

    def getCustomWidgetDefinitions(self):
        return self.customWidgetDefinitions

    def loadCustomWidgets(self):
        configFiles = []  # list of all widget definition files to load
        defaultPath = str(pathlib.PurePosixPath(__file__).parent) + "/widgets"
        if os.path.exists(defaultPath):
            configFiles = [f for f in os.listdir(defaultPath) if os.path.isfile(os.path.join(defaultPath, f)) and f.endswith(".widget")]

        path = ConfigVariableString("custom-widgets-path", "").getValue()
        if path != "" and os.path.exists(path):
            # get a list of all .widget files
            configFiles.extend([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.endswith(".widget")])

        logging.info("no custom widgets found.")

        # handle data in files
        for configFile in configFiles:
            try:
                configFileContent = None
                with open(os.path.join(path, configFile), 'r') as infile:
                    configFileContent = json.load(infile)
                if configFileContent is None:
                    logging.error("Problems reading widget config file: {}".format(infile))
                    continue
                pythonFilePath = os.path.join(path, configFileContent["classFilePath"])
                spec = None
                if pythonFilePath.endswith(".py"):
                    spec = importlib.util.spec_from_file_location(configFileContent["moduleName"], pythonFilePath)
                else:
                    spec = importlib.util.find_spec(configFileContent["classFilePath"])
                if spec is None:
                    continue
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if configFileContent["className"] not in self.customWidgetDefinitions:
                    self.customWidgetDefinitions[configFileContent["className"]] = []

                if "baseWidget" in configFileContent:
                    if configFileContent["baseWidget"] in DEFINITIONS:
                        self.customWidgetDefinitions[configFileContent["className"]] += DEFINITIONS[configFileContent["baseWidget"]]

                if "customProperties" in configFileContent:
                    for prop in configFileContent["customProperties"]:
                        self.__loadPropertyDefinition(configFileContent, prop)

                self.customWidgetsDict[configFileContent["name"]] = CustomWidget(
                    configFileContent["displayName"],
                    configFileContent["className"],
                    configFileContent["classFilePath"],
                    module,
                    configFileContent["addItemFunctionName"] if "addItemFunctionName" in configFileContent else None,
                    configFileContent["addItemExtraArgs"] if "addItemExtraArgs" in configFileContent else None,
                    configFileContent["addItemNode"] if "addItemNode" in configFileContent else None,
                    configFileContent["removeItemFunctionName"] if "removeItemFunctionName" in configFileContent else None,
                    configFileContent["importPath"])
                self.toolboxExtensionList.append([configFileContent["displayName"], configFileContent["className"]])

            except KeyError:
                e = sys.exc_info()[1]
                string = f"Parameter: {e} missing from custom definition file '{configFile}'"
                print(string)

        self.extendToolbox()
        self.extendElementHandler()

    def __loadPropertyDefinition(self, configFileContent, prop):
        try:
            t = None
            if "internalType" in prop:
                if prop["internalType"] == "int":
                    t = int
                elif prop["internalType"] == "float":
                    t = float
                elif prop["internalType"] == "bool":
                    t = bool
                elif prop["internalType"] == "str":
                    t = str
                elif prop["internalType"] == "function":
                    t = types.FunctionType
                elif prop["internalType"] == "list":
                    t = list
                elif prop["internalType"] == "tuple":
                    t = tuple
                elif prop["internalType"] == "object":
                    t = object

            self.customWidgetDefinitions[configFileContent["className"]].append(
                Definition(prop["internalName"],
                           prop["displayName"],
                           t,
                           prop["editType"] if "editType" in prop else None,
                           prop["nullable"] if "nullable" in prop else False,
                           prop["supportStates"] if "supportStates" in prop else False,
                           prop["valueOptions"] if "valueOptions" in prop else None,
                           prop["isInitOption"] if "isInitOption" in prop else False,
                           prop["getFunctionName"] if "getFunctionName" in prop else None,
                           prop["setFunctionName"] if "setFunctionName" in prop else None,
                           prop["addToExtraOptions"] if "addToExtraOptions" in prop else False,
                           prop["loaderFunc"] if "loaderFunc" in prop else None,
                           prop["postProcessFunctionName"] if "postProcessFunctionName" in prop else None,
                           prop["canGetValueFromElement"] if "canGetValueFromElement" in prop else True))
        except KeyError:
            e = sys.exc_info()[1]
            string = f"Parameter: {e} missing from custom property '{prop}'"
            logging.error(string)
            print(string)

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

