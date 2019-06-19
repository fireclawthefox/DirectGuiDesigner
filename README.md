# DirectGuiDesigner
A Visual Editor for Panda3Ds Direct GUI

## Features
- Toolbox with all DirectGui elements
- Drag and drop to re-position elements in the designer
- Properties editor for most common element options
- Place elements freely or with a guidance grid
- GUI structure viewer
- Export to python script for easy integration

## Screenshots

![Editor Window after startup](/Screenshots/startup.png?raw=true "The Editor")
![Editor in use, creating a LogIn screen](/Screenshots/simpleGUI.png?raw=true "A simple LogIn screen made in the app")
![Export a created GUI](/Screenshots/export.png?raw=true "Export as python script")

## Requirements
Python 3.x
Panda3D 1.10.x

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

### Remove elements
Click on the X in the structure view, hit Ctrl-Delete or use the respective button from the toolbar

### Save and export
To save The designed GUI as a DirectGuiDesigner project, hit Ctrl-S or the respective button in the toolbar.
This will save a Json file that can later be loaded by the designer again.

To export as a python script that can directly be used in projects, either hit Ctrl-E or click the button in the toolbar.

### Use exported scripts
The python script will always contain a class called Gui which you can pass a NodePath to be used as root parent element for the GUI. Simply instancing the class will make the GUI visible by default. If this is not desired, hide the root NodePath as given on initialization or edit the class and add a dedicated show/hide function.

## Known Bugs and missing features
- DirectGui has heavy flickering and sometimes doesn't render gui controls correct
    -> As a workaround until this is fixed, scale the window or select/deselct elements in the editor to make it refresh the elements
- Most of the element specific options aren't available in the properties editor yet
- There might be crashes when saving and loading GUIs with the more exotic GUI elements
- Some elements (esp. those with sub controls) will not export correct yet, those need manual editing in the exported python script
- Removing elements with sub elements makes app unstable (DEV NOTE: need to clean elementDict from removed sub elements)
