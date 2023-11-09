# DirectGuiDesigner
A Visual Editor for Panda3Ds Direct GUI

## Features
- Toolbox with all DirectGui elements
- Drag and drop to re-position elements in the designer
- Properties editor for most common element options
- Place elements freely or with a guidance grid
- GUI structure viewer
- Save and load projects as json files
- Export to python script for easy integration
- Support for custom DirectGui like elements

## Screenshots

![Editor Window after startup](/Screenshots/startup.png?raw=true "The Editor")
![Editor in use, creating a simple chat window](/Screenshots/simpleGUI.png?raw=true "A simple chat window made with the editor")
![Export a created GUI](/Screenshots/export.png?raw=true "Export as python script")

## Requirements
- Python 3.x
- Panda3D 1.10.4.1+
- DirectFolderBrowser
- DirectGuiExtension

To install them, using pip:
`pip install -r requirements.txt`

## Manual
Hit F1 to see the help screen

### Startup
To start the DirectGUI Designer, simply run the main.py script

`python main.py`

### Build binaries
To create binaries of the Designer, call the following

`python setup.py build_apps`

This will create a new folder called build with subdirectories for the various operating systems which will contain the binaries.

### Basic Editing
1. Click on an element in the toolbox.<br />
-> this will place the element at (0,0,0) parented to the selected element or the root if nothing was selected.
2. Left-click on the item you want to edit.
3. Drag and Drop to position the element and use the properties panel to set all desired options.

### Editor Scale
The editor supports two units of measurement, the default window aspect related one where ranges usually go from -1 to 1 and the center being in the middle of the window. 
The other system uses the pixel2d nodepath and hence scales according to pixels. 
It 0 location is at the top left corner of the editor and extends to 1920 by -1080 by default. 
It usually don't go into a negative value for screen coordinates but you can set negative pixel values for relative positioning.
To switch between those scales, just hit the button in the menu bar that has the ruler symbol on it.

### Remove elements
Click on the X in the structure view, hit Ctrl-Delete or use the respective button from the toolbar

### Undo/Redo cycle
Using the usual Ctrl-Z and Ctrl-Y you can undo and redo most of the changes done in the editor. 
There is no limit to the undo/redo steps and using Ctrl-Shift-Y you can cycle through different redo paths.

### Save and export
To save The designed GUI as a DirectGuiDesigner project, hit Ctrl-S or the respective button in the toolbar.
This will save a Json file that can later be loaded by the designer again.

To export as a python script that can directly be used in projects, either hit Ctrl-E or click the button in the toolbar.
If enabled in the settings, the python exporter will create scripts that can directly be run.

#### Autosave
The designer will automatically save the project after a specific time has elapsed. If the project has not been saved before, the autosave file will be created in your systems temp directory. 
Otherwise it will be placed next to your saved project with a .1 appended at the end.
To change the autosave delay, open the options dialog and change the value in the spinner box dedicated for the autosave delay or change the config variable `autosave-delay`. 
The minimum value is set to 10 and the max value is set to 3600 (1 hour) while the default delay is set to 60 (1 minute).

### Use exported scripts
The python script will always contain a class called Gui which you can pass a NodePath to be used as root parent element for the GUI. 
Simply instancing the class will make the GUI visible by default. 
If this is not desired, hide the root NodePath as given on initialization. 
As you shouldn't edit the exported class due to edits being overwritten with a new export, you should create another python module which will handle the connection of the apps logic with the gui. 
This dedicated module could for example implement a show and hide method to easily change the visibility of the gui or set and gather values of the GUI without having to change the actual GUI design module code.

Here is a small example of how to load and instantiate a GUI. We expect the gui to be exported to a file called myGui.py:
```
from myGui import GUI as MyGui
myGui = MyGui()
```

In a real world application you may want to create a handler class around your GUI class to cleanly abstract your data from the view. 
A simple example of such a class could look like the following.
```
from myGui import GUI as MyGui
class MyGuiHandler(MyGui):
    def __init__(self):
        MyGui.__init__(self)
    def setData(self, someData):
        self.someElement["text"] = someData.text
```


### Configuration
To change configurations, simply use the editors settings dialog available through the menubar Tools>Options or the cogwheel in the toolbar.

These custom configuration variables have been introduced for the editor.

| Name                      | Type    | Description                                                                                                                                                                |
|---------------------------|---------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| skip-ask-for-quit         | bool    | If set to True, the dialog to ask for confirmation when quitting the Designer will not be shown. Defaults to False                                                         |
| create-executable-scripts | bool    | If set to True, the saved python scripts will contain everything to directly run. Defaults to False                                                                        |
| show-toolbar              | bool    | If set to True, the toolbar over the editor area will be shown, otherwise only the menubar will be displayed. Defaults to True                                             |
| custom-widgets-path       | String  | The path to a folder which will contain custom designed DirectGui widgets.                                                                                                 |
| custom-model-path         | String  | A path to a folder containing textures, models and other assets required by your gui. You can add this property more than once and each line should only contain one path. |
| autosave-delay            | Integer | Delay in seconds at which the project is automatically saved to a special auto-save file.                                                                                  |

The Designer will create a hidden configuration file called .DirectGuiDesigner.prc in the users Home directory. 
It will contain all custom configurations from the list above with their default values and can be changed/extended with other Panda3D configurations.

### Custom Widgets
To add your own DirectGui elements to the editor you must make sure the following points are given.

1. Put all your widgets in one dedicated folder and make sure it's through the custom-widgets-path configuration.
2. Widgets have to adhere to the usual DirectGui coding style
3. All widgets need a .widget definition file. See below for further information

#### Widget Definition files
A .widget definition file is necessary to add support for your custom widget in the designer. 
Those files are simple json files containing information about your element like display name, class name and so on. 
An example of such a file can be found in the customWidgetSample folder. Here's a list of keys that should be given in the definition file:

| Name                   | Type           | Description                                                                                                                                                                                              | Optional |
|------------------------|----------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| name                   | String         | The unique name or ID of this widget                                                                                                                                                                     | No       |
| moduleName             | String         | The name of the python module                                                                                                                                                                            | No       |
| displayName            | String         | The name of the widget as it will be displayed in the toolbox                                                                                                                                            | No       |
| className              | String         | The class name in the module which should be used                                                                                                                                                        | No       |
| classFilePath          | String         | Path to the python file which should be imported                                                                                                                                                         | No       |
| baseWidget             | String         | The name of the widget this custom widget is based upon, e.g. DirectFrame or DirectButton                                                                                                                | Yes      |
| customProperties       | List           | A list information for custom properties                                                                                                                                                                 | No       |
| addItemFunctionName    | String         | A special function name which should be called when other elements get parented to this widget                                                                                                           | Yes      |
| addItemExtraArgs       | List or Dict   | Some extra args that should get passed when addItemFunction is called. A list is used to specify the values directly in the widget definition file. To let the user choose the values use a dict instead | Yes      |
| AddItemNode            | List or String | The name (or list of names) of the node(s) to reparent other elements to                                                                                                                                 | Yes      | 
| removeItemFunctionName | String         | A special function name which should be called when other elements get removed from this widget                                                                                                          | Yes      |
| importPath             | String         | The import statement which should be added to exported python file                                                                                                                                       | No       |

When specifying addItemExtraArgs as a dict, it should have the following format:
```
"addItemExtraArgs" = {
    "some_argument_name": {
        "type": "int",
        "defaultValue": 4
    },
    "some_other_arg": {
        "type": "element",
        "defaultValue": null
    }
}
```
The types that are recognized at the moment is: str, int, float and element. 
Where element allows the user to choose one other element to pass in as an argument.

#### Custom Properties
The customProperties list will contain definition dictionaries of your widgets properties.
These dictionaries will have the following structure, not all options are mandatory though, see below for further information:
```
{
    "internalName":"thePropertiesName",
    "displayName":"The display name",
    "internalType":"int",
    "editType":"int",
    "nullable":false,
    "supportStates":false,
    "valueOptions":"",
    "isInitOption":"",
    "getFunctionName":"",
    "setFunctionName":"",
    "addToExtraOptions":"",
    "loaderFunc":"",
    "postProcessFunctionName":"",
    "canGetValueFromElement":"",
    "defaultValue":""
}
```

| Name                    | Type   | Description                                                                                                                                                                                                                                                                                                | Optional | values                                                                                                                                         |
|-------------------------|--------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------------------------------------|
| internalName            | String | The name of this property as it is used on the widget e.g. widget["internalName"]                                                                                                                                                                                                                          | No       |                                                                                                                                                |
| displayName             | String | The visible name of this property as it will be shown in the Designer                                                                                                                                                                                                                                      | No       |                                                                                                                                                |
| internalType            | String | The data type representation for this property                                                                                                                                                                                                                                                             | Yes      | int", "float", "bool", "str", "function", "list", "tuple", "object"                                                                            |
| editType                | String | The edit type of this property. This value can also be automatically determined by the internalType                                                                                                                                                                                                        | Yes      | "int", "float", "bool", "text", "base2", "base3", "base4", "command", "path", "optionMenu", "list", "tuple", "resetFrameSize", "fitToChildren" |
| nullable                | Bool   | Determines if this property can be set to None                                                                                                                                                                                                                                                             | Yes      |                                                                                                                                                |
| supportStates           | Bool   | Determines if this property support the multiple states of a widget (e.g. the Buttons normal/hover/clicked/disabled state)                                                                                                                                                                                 | Yes      |                                                                                                                                                |
| valueOptions            | Value  | The value or values stored in here will be used dependent on the type of property. In case it's a selectable option, the value must be a dictionary consisting of user visible key and code value If it is a runnable command, it should be the name of the function to be called from the element itself. | Yes      |                                                                                                                                                |
| isInitOption            | Bool   | define if this is a value only to be set at initialization time.                                                                                                                                                                                                                                           | Yes      |                                                                                                                                                |
| getFunctionName         | String | Function name to get the property                                                                                                                                                                                                                                                                          | Yes      |                                                                                                                                                |
| setFunctionName         | String | Function name to set the property                                                                                                                                                                                                                                                                          | Yes      |                                                                                                                                                |
| addToExtraOptions       | Bool   | This is for special properties which can not be directly set on the item in the editor but should rather be stored separately                                                                                                                                                                              | Yes      |                                                                                                                                                |
| loaderFunc              | String | A function which is passed the value entered in the editor to process it prior to setting it in the property (e.g. loadFont or loadModel) The value can be given to the function by using value. E.g. "loader.loadFont(value) which will call the load Font given the properties value                     | Yes      |                                                                                                                                                |
| postProcessFunctionName | String | A Function name which will be called after setting this property                                                                                                                                                                                                                                           | Yes      |                                                                                                                                                |
| canGetValueFromElement  | Bool   | Determines if the value of this property can be got directly from it using the ["internalName"]                                                                                                                                                                                                            | Yes      |                                                                                                                                                |
| defaultValue            | Any    | Specifies what default value this property should have.                                                                                                                                                                                                                                                    | Yes      |                                                                                                                                                |

The values for the internalType are defined as follows:

| Name           | Description                                                                                        |
|----------------|----------------------------------------------------------------------------------------------------|
| int            | Integer values                                                                                     |
| float          | Floating point values                                                                              |
| base2          | Two floating point values                                                                          |
| base3          | Three floating point values                                                                        |
| base4          | Four floating point values                                                                         |
| text           | A String entry                                                                                     |
| path           | A path selection                                                                                   |
| bool           | A Boolean selection                                                                                |
| tuple          | An extendable list of values representing a python tuple                                           |
| list           | An extendable list of values representing a python list                                            |
| optionMenu     | A selection using the values in valueOptions                                                       |
| command        | Used in combination with the customCommandName value to create a button that will call the command |
| resetFrameSize | A special command to reset the widgets frameSize                                                   |
| fitToChildren  | A special command to fit the widgets frameSize to its children                                     |
