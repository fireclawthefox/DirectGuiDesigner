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

## Screenshots

![Editor Window after startup](/Screenshots/startup.png?raw=true "The Editor")
![Editor in use, creating a LogIn screen](/Screenshots/simpleGUI.png?raw=true "A simple LogIn screen made in the app")
![Export a created GUI](/Screenshots/export.png?raw=true "Export as python script")

## Requirements
- Python 3.x
- Panda3D 1.10.4.1+

## Manual
Hit F1 to see the help screen

### Startup
To start the DirectGUI Designer, simply run the DirectGuiDesigner.py script

<code>python DirectGuiDesigner.py</code>

### Basic Editing
1. Click on an element in the toolbox.<br />
-> this will place the element at (0,0,0) parented to the selected element or the root if nothing was selected.
2. Left click on the item you want to edit.
3. Drag and Drop to position the element and use the properties panel to set all desired options.

### Editor Scale
The editor supports two units of measurement, the default window aspect related one where ranges usually go from -1 to 1 and the center being in the middle of the window. The other system uses the pixel2d nodepath and hence scales according to pixels. It 0 location is at the top left corner of the editor and extends to 1920 by -1080 by default. It usually don't go into a negative value for screen coordinates but you can set negative pixel values for relative positioning.
To switch between those scales, just hit the button in the menu bar that has the ruler symbol on it.

### Remove elements
Click on the X in the structure view, hit Ctrl-Delete or use the respective button from the toolbar

### Save and export
To save The designed GUI as a DirectGuiDesigner project, hit Ctrl-S or the respective button in the toolbar.
This will save a Json file that can later be loaded by the designer again.

To export as a python script that can directly be used in projects, either hit Ctrl-E or click the button in the toolbar.

### Use exported scripts
The python script will always contain a class called Gui which you can pass a NodePath to be used as root parent element for the GUI. Simply instancing the class will make the GUI visible by default. If this is not desired, hide the root NodePath as given on initialization or edit the class and add a dedicated show/hide function.

### Configuration
To change configurations, simply use the editors settings dialog available through the menubar Tools>Options or the cogwheel in the toolbar.

These custom configuration variables have been introduced for the editor.

|Name|Type|Description|
|---|---|---|
|skip-ask-for-quit|bool|If set to True, the dialog to ask for confirmation when quitting the Designer will not be shown. Defaults to False|
|create-executable-scripts|bool|If set to True, the saved python scripts will contain everything to directly run. Defaults to False|
|show-toolbar|bool|If set to True, the toolbar over the editor area will be shown, otherwise only the menubar will be displayed. Defaults to True|
|custom-widgets-path|String|The path to a folder which will contain custom designed DirectGui widgets.|

The Designer will create a hidden configuration file called .DirectGuiDesigner.prc in the users Home directory. It will contain all custom configurations from the list above with their default values and can be changed/extended with other Panda3D configurations.

### Custom Widgets
To add your own DirectGui elements to the editor you must make sure the following points are given.

1. Put all your widgets in one dedicated folder and make sure it's through the custom-widgets-path configuration.
2. Widgets have to adhere to the usual DirectGui coding style
3. All widgets need a .widget definition file. See below for further information

#### Widget Definition files
A .widget definition file is necessary to add support for your custom widget in the designer. Those files are simple json files containing information about your element like display name, class name and so on. An example of such a file can be found in the customWidgetSample folder. Here's a list of keys that should be given in the definition file:

|Name|Type|Description|Optional|
|---|---|---|---|
|name|String|The unique name or ID of this widget|No|
|moduleName|String|The name of the python module|No|
|displayName|String|The name of the widget as it will be displayed in the toolbox|No|
|className|String|The class name in the module which should be used|No|
|classfilePath|String|Path to the python file which should be imported|No|
|enabledProperties|List|A list of properties that should be enabled for the widget in the properties editor|No|
|addItemFunctionName|String|A special function name which should be called when other elements get parented to this widget|Yes|
|removeItemFunctionName|String|A special function name which should be called when other elements get removed from this widget|Yes|
|importPath|String|The import statement which should be added to exported python file|No|


## Known Bugs and missing features
- Some element specific options aren't available in the properties editor yet
