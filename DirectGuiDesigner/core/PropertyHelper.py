import logging
from DirectGuiDesigner.core import WidgetDefinition
from DirectGuiDesigner.core import CustomWidgets


class PropertyHelper:
    def getFormated(value, isInt=False):
        if type(value) is int or isInt:
            return "{}".format(int(value))
        elif type(value) is not str:
            return "{:0.3f}".format(value)
        else:
            return value

    def getPropertyName(definition):
        propName = definition.internalName
        if definition.elementGroup != "":
            # prepent the group
            propName = f"{definition.elementGroup}_{propName}"
        return propName

    def getValues(definition, elementInfo):
        propName = PropertyHelper.getPropertyName(definition)
        nameAdd = f"{elementInfo.subComponentName}_" if elementInfo.subComponentName != "" else ""
        propName = nameAdd + propName

        if propName in elementInfo.extraOptions:
            value = elementInfo.extraOptions[propName]
            logging.debug(f"Get property from extra options. {propName}={value}")
            return value
        elif not definition.canGetValueFromElement:
            # this has to come from the extra options, otherwise we just return
            # an empty string
            logging.debug(f"Can't get value of property {propName} from the element")
            return ""
        elif definition.getFunctionName:
            try:
                if type(definition.getFunctionName) == str:
                    value = getattr(elementInfo.element, definition.getFunctionName)()
                    return value
                else:
                    return definition.getFunctionName()
            except Exception:
                logging.exception(f"couldn't get value of {propName} by function {definition.getFunctionName}")
        else:
            value = None
            try:
                value = elementInfo.element[propName]
            except Exception:
                component = elementInfo.element
                prop = propName
                if propName == "text_align":
                    if hasattr(elementInfo.element, "component"):
                        return elementInfo.element.component("text0").align
                    else:
                        # we may already have the component at hand
                        return elementInfo.element.align
                if "_" in propName:
                    if hasattr(elementInfo.element, "component"):
                        comp_name = "_".join(propName.split("_")[:-1])
                        try:
                            component = elementInfo.element.component(comp_name)
                        except:
                            # The component may already be the one we were looking for
                            component = elementInfo.element
                    prop = propName.split("_")[-1]
                if hasattr(component, prop):
                    value = getattr(component, prop)
                else:
                    try:
                        # last resort, try get the property directly from the
                        # element with the updated property name without
                        # component parts.
                        #
                        # This is important for components like the popup marker
                        # of option menus and buttons of dialogs and possibly
                        # some others too...
                        value = component[prop]
                    except:
                        logging.debug(f"Couldn't get value for {prop} from {elementInfo.element.name}:{type(elementInfo.element)}")
                        raise
            return value

    def setValue(definition, elementInfo, value, valueAsString=""):
        propName = PropertyHelper.getPropertyName(definition)
        nameAdd = f"{elementInfo.subComponentName}_" if elementInfo.subComponentName != "" else ""
        propName = nameAdd + propName

        if definition.isInitOption:
            # This is an initialization option, so we just store it as extra options
            if valueAsString != "":
                logging.debug(f"Store value as string in extra options. {propName}={valueAsString}")

                if elementInfo.extraOptions[propName] != valueAsString:
                    elementInfo.valueHasChanged[propName] = True

                # if the value as string is set, this is probably the one we
                # want to store (e.g. paths to models, fonts, etc)
                elementInfo.extraOptions[propName] = valueAsString
            else:
                # if no string value is given, store the real value
                logging.debug(f"Store value as extra options. {propName}={value}")
                if propName not in elementInfo.extraOptions \
                or elementInfo.extraOptions[propName] != value:
                    elementInfo.valueHasChanged[propName] = True
                elementInfo.extraOptions[propName] = value
        elif definition.setFunctionName:
            if PropertyHelper.getValues(definition, elementInfo) != valueAsString if valueAsString != "" else value:
                elementInfo.valueHasChanged[propName] = True
            oldValue = PropertyHelper.getValues(definition, elementInfo)
            try:
                if type(definition.setFunctionName) == str:
                    logging.debug(f"Try set value via function name. func: {definition.setFunctionName} value: {value}")
                    getattr(elementInfo.element, definition.setFunctionName)(value)
                else:
                    logging.debug(f"Try set value via function pointer. ptr: {definition.setFunctionName} value: {value}")
                    definition.setFunctionName(value)
                if definition.addToExtraOptions:
                    # check if we want to store it as a string or the real value
                    if valueAsString != "":
                        logging.debug(f"Additionally store value as string in extra options. {propName}={valueAsString}")
                        elementInfo.extraOptions[propName] = valueAsString
                    else:
                        logging.debug(f"Additionally store value as extra options. {propName}={value}")
                        elementInfo.extraOptions[propName] = value
            except Exception:
                # setting the element failed, revert to old value in case it was
                # partly set
                logging.exception(f"couldn't set value of {propName} to value {value}")
                elementInfo.element[propName] = oldValue
        else:
            # get the old value of the property
            oldValue = PropertyHelper.getValues(definition, elementInfo)
            try:
                v = valueAsString if valueAsString != "" else value
                logging.debug(f"Try set value by direct key access. {propName}={v}")
                if PropertyHelper.getValues(definition, elementInfo) != v:
                    elementInfo.valueHasChanged[propName] = True

                # try to set the new value as original type on the property
                propName_orig = propName.replace(nameAdd, "", 1)
                if definition.loaderFunc is not None and isinstance(value, str):
                    if isinstance(definition.loaderFunc, str):
                        value = eval(definition.loaderFunc)
                    else:
                        value = definition.loaderFunc(value)
                elementInfo.element[propName_orig] = value

                # in addition, if this should be stored in extra options
                # (e.g. if we can't get the property value from the element
                # itself in other ways)
                if definition.addToExtraOptions:
                    # check if we want to store it as a string or the real value
                    if valueAsString != "":
                        logging.debug(f"Additionally store value as string in extra options. {propName}={valueAsString}")
                        elementInfo.extraOptions[propName] = valueAsString
                    else:
                        logging.debug(f"Additionally store value as extra options. {propName}={value}")
                        elementInfo.extraOptions[propName] = value

            except Exception:
                # setting the element failed, revert to old value in case it was
                # partly set
                logging.exception(f"couldn't set value of {propName} to value {value}")
                if definition.nullable:
                    elementInfo.element[propName] = None
                elementInfo.element[propName] = oldValue

        if definition.postProcessFunctionName is not None:
            if type(definition.postProcessFunctionName) == str:
                logging.debug(f"Run postprocess command by name. {definition.postProcessFunctionName}")
                getattr(elementInfo.element, definition.postProcessFunctionName)()
            else:
                logging.debug(f"Run postprocess command by pointer. {definition.postProcessFunctionName}")
                definition.postProcessFunctionName()

    @staticmethod
    def getDefinition(elementInfo, internalName):
        if isinstance(elementInfo, dict):
            elementType = elementInfo["type"]

        else:
            elementType = elementInfo.type

        if elementType in WidgetDefinition.DEFINITIONS:
            definitions = WidgetDefinition.DEFINITIONS[elementType]

        elif elementType in CustomWidgets.CustomWidgets.customWidgetDefinitions:
            definitions = CustomWidgets.CustomWidgets.customWidgetDefinitions[elementType]

        else:
            raise ValueError(f"{elementType} not found in definitions")

        for definition in definitions:
            if definition.internalName == internalName:
                return definition

        raise ValueError(f"{internalName} not in definition")
