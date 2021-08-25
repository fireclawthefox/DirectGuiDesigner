import types

from panda3d.core import PGFrameStyle
from direct.gui import DirectGuiGlobals as DGG

class PropertyEditTypes:
    integer = "integer"
    float = "float"
    bool = "bool"
    text = "text"
    base2 = "base2"
    base3 = "base3"
    base4 = "base4"
    command = "command"
    path = "path"
    optionMenu = "optionmenu"
    list = "list"
    tuple = "tuple"
    resetFrameSize = "resetFrameSize"

t = PropertyEditTypes

class Definition:
    def __init__(self,
            internalName,
            visiblename,
            internalType,
            editType=None,
            nullable=False,
            supportStates=False,
            valueOptions=None,
            isInitOption=False,
            getFunctionName=None,
            setFunctionName=None,
            addToExtraOptions=False,
            loaderFunc=None):
        # Name to be shown in the editor
        self.visiblename = visiblename

        # Internal name of this property
        self.internalName = internalName

        # Type of this property
        self.type = internalType

        # defines if the value of this property may be None
        self.nullable = nullable

        # define if this property supports widget states or is only one value
        # for all states of it
        self.supportStates = supportStates

        # The value or values stored in here will be used dependent on the type
        # of property.
        # In case it's a selectable option, the value must be a dictionary
        # consisting of user visible key and code value
        # If it is a runnable command, it should be the name of the function
        # to be called from the element itself
        self.valueOptions = valueOptions

        # define if this is a value only to be set at initialization time. If
        # this is set, the value will be stored in the elementInfos extraOptions
        # dictionary
        self.isInitOption = isInitOption

        # Function pointers to get and set the desired property
        self.getFunctionName = getFunctionName
        self.setFunctionName = setFunctionName

        # If enabled, the option will be set on the element itself as well as in
        # the elementInfos extraOptions dictionary
        self.addToExtraOptions = addToExtraOptions

        # a function which is passed the value entered in the editor to process
        # it prior to setting it in the property (e.g. loadFont or loadModel)
        self.loaderFunc = loaderFunc

        # This can be set to the group of a widget, e.G. the "text" group of a
        # DirectButton to know we're interested in the text_* sub element
        # properties rather than the ones directly available on the root element
        self.elementGroup = ""

        # This value can be used to determine if the value can be taken from the
        # element itself or if it has to be taken from the extra options
        self.canGetValueFromElement = True

        # The edit type defines how the property can be edited in the designer
        if editType is None:
            # if the edit type is not given, try to predict it from values
            # that can definitely be determined
            if self.type == int:
                self.editType = t.integer
            elif self.type == float:
                self.editType = t.float
            elif self.type == bool:
                self.editType = t.bool
            elif self.type == str:
                self.editType = t.text
            elif self.type == types.FunctionType:
                self.editType = t.text
                self.nullable = True
                # even if it's not an init option, we don't want commands to be
                # called in the editor
                self.isInitOption = True
                # since we can't write down functions in textfields, we have to
                # take the value given in the extra options
                self.canGetValueFromElement = False
            elif self.type == list:
                #self.editType = t.list
                self.editType = t.text
                self.canGetValueFromElement = False
            elif self.type == tuple:
                self.editType = t.tuple
            elif self.type == object:
                self.editType = t.text
            else:
                raise Exception(f"Edit type can not be predicted for type: {self.type}")
        else:
            self.editType = editType


POSITION_DEFINITION = Definition('pos', 'Position (X/Y/Z)', object, editType=t.base3, nullable=True)
ROTATION_DEFINITION = Definition('hpr', 'Rotation (H/P/R)', object, editType=t.base3, nullable=True)
SCALE_DEFINITION = Definition('scale', 'Scale (W/H/D)', object, editType=t.base3, nullable=True)
COLOR_DEFINITION = Definition('color', 'Color (R/G/B/A)', object, editType=t.base4, nullable=True)
COMMAND_DEFINITION = Definition('command', 'Command', types.FunctionType)
COMMAND_ARGS_DEFINITION = Definition('extraArgs', 'Extra Arguments for Command', list)
COMMAND_BUTTONS_DEFINITION = Definition('commandButtons', 'Command Buttons', tuple)

# definitions for DirectGuiWidget
DEFAULT_DEFINITIONS = [
    #Definition('parent', 'parent', object, editType=t.optionMenu, nullable=True),

    # this is best implemented in the structure panel with up/down arrows
    #Definition('sort', 'sort', int),
    # Widget's constructor
    Definition('pgFunc', 'Function', types.FunctionType),
    Definition('numStates', 'Number of states', int),
    #Definition('invertedFrames', 'Inverted Frames', tuple, editType=t.base?),
    Definition('sortOrder', 'Sort Order', int),
    # Widget's initial state
    Definition('state', 'State', str, editType=t.optionMenu, valueOptions={"Normal":DGG.NORMAL, "Disabled":DGG.DISABLED}),
    # Widget's frame characteristics
    Definition('relief', 'Relief', int, editType=t.optionMenu, nullable=True, valueOptions={"None":PGFrameStyle.TNone, **DGG.FrameStyleDict}),
    Definition('borderWidth', 'Border Width', tuple, editType=t.base2),
    Definition('borderUvWidth', 'Border UV Width', tuple, editType=t.base2),
    Definition('frameSize', 'Frame Size', object, editType=t.base4, nullable=True),
    Definition('', 'Reset Frame Size', None, editType=t.command, valueOptions='resetFrameSize'),
    Definition('frameColor', 'Frame Color', tuple, editType=t.base4),
    Definition('frameTexture', 'Frame Texture', object, editType=t.path, nullable=True),
    Definition('frameVisibleScale', 'Frame Visible Scale', tuple, editType=t.base2),
    Definition('pad', 'Padding', tuple, editType=t.base2),
    # Override button id (beware! your name may not be unique!)
    Definition('guiId', 'GUI ID', object, editType=t.text, nullable=True),
    # Initial pos/scale of the widget
    POSITION_DEFINITION,
    ROTATION_DEFINITION,
    SCALE_DEFINITION,
    COLOR_DEFINITION,
    # Do events pass through this widget?
    Definition('suppressMouse', 'Suppress Mouse', bool),
    Definition('suppressKeys', 'Suppress Keyboard', bool),
    #Definition('enableEdit', 'Enable Edit', bool),
]

GEOM_DEFINITIONS = [
    Definition('geom', 'Geometry', object, editType=t.path, addToExtraOptions=True),
    POSITION_DEFINITION,
    ROTATION_DEFINITION,
    Definition('scale', '', object),
    Definition('color', '', object),
    #Definition('parent', '', object),
    Definition('sort', '', int)
]
IMAGE_DEFINITIONS = [
    Definition('image', 'Image', object, editType=t.path, addToExtraOptions=True),
    POSITION_DEFINITION,
    ROTATION_DEFINITION,
    Definition('scale', '', object),
    Definition('color', '', object),
    #Definition('parent', '', object),
    Definition('sort', '', int)
]
TEXT_DEFINITIONS = [
    Definition('text','Text', str),
    #Definition('style', 'Style', int), # This is a initialization property only
    Definition('pos', 'Position (X/Y)', object, editType=t.base2),
    Definition('roll', 'Roll', int),
    Definition('scale', 'Scale', object, editType=t.base2, nullable=True),
    Definition('fg', 'Foreground Color', object, editType=t.base4),
    Definition('bg', 'Backgrond Color', object, editType=t.base4),
    Definition('shadow', 'Shadow Color', object, editType=t.base4),
    #Definition('shadowOffset', 'Shadow Offset', tuple, editType=t.base2), # needs to be set on the textNode, there is no way to set this through OnscreenText
    Definition('frame', 'Frame', object, editType=t.base4),
    Definition('align', 'Align', object, editType=t.integer),
    #Definition('wordwrap', 'Wordwrap', object, editType=t.float), #TODO
    #Definition('drawOrder', 'Draw Order', object, editType=t.integer), #TODO
    Definition('decal', 'Decal', int),
    Definition('font', 'Font', object, editType=t.path, addToExtraOptions=True, loaderFunc="loader.loadFont(value)"),
    #Definition('parent', 'Parent', object),
    Definition('sort', 'Sort', int),
    Definition('mayChange', 'May Change', bool),
    #Definition('direction', 'Direction', object)
]


DIRECT_FRAME_DEFINITIONS = DEFAULT_DEFINITIONS + [
    # Frame can have:
    # A background texture
    Definition('image', 'Image', object, editType=t.path, addToExtraOptions=True),
    # A midground geometry item
    Definition('geom', 'Geometry', object, editType=t.path, addToExtraOptions=True),
    # A foreground text node
    Definition('text', 'Text', object, editType=t.text),
    # Change default value of text mayChange flag from 0
    # (OnscreenTexeditType=t.py) to 1
    Definition('textMayChange', 'Text May Change', bool)
]

DIRECT_BUTTON_DEFINITIONS = DIRECT_FRAME_DEFINITIONS + [
    # Command to be called on button click
    COMMAND_DEFINITION,
    COMMAND_ARGS_DEFINITION,
    # Which mouse buttons can be used to click the button
    COMMAND_BUTTONS_DEFINITION,
    # Sounds to be used for button events
    Definition('rolloverSound', 'Rollover Sound', object, editType=t.path),
    Definition('clickSound', 'Click Sound', object, editType=t.path),
    # Can only be specified at time of widget contruction
    # Do the text/graphics appear to move when the button is clicked
    Definition('pressEffect', 'Press Effect', bool, isInitOption=True),
]

DEFAULT_DIALOG_DEFINITIONS = [
    # Define type of DirectGuiWidget
    Definition('dialogName', 'Dialog Name', str),
    # Default position is slightly forward in Y, so as not to
    # intersect the near plane, which is incorrectly set to 0
    # in DX for some reason.
    Definition('text', 'Text', str),
    Definition('text_align', 'Text Align', int),
    Definition('text_scale', 'Text Scale', object, editType=t.base3, nullable=True),
    Definition('borderWidth', 'Border Width', tuple),
    Definition('buttonTextList', 'Button Text List', list),
    Definition('buttonGeomList', 'Button Geom List', list),
    Definition('buttonImageList', 'Button Image List', list),
    Definition('buttonValueList', 'Button Value List', list),
    Definition('buttonHotKeyList', 'Button Hotkey List', list),
    Definition('button_borderWidth', 'Button Border Width', tuple),
    Definition('button_pad', 'Button Padding', tuple),
    Definition('button_relief', 'Button Relief', int),
    Definition('button_text_scale', 'Button Text Scale', object, editType=t.base3, nullable=True),
    Definition('buttonSize', 'Button Size', object, editType=t.base3, nullable=True),
    Definition('topPad', 'Top Padding', float),
    Definition('midPad', 'Middle Padding', float),
    Definition('sidePad', 'Side Padding', float),
    Definition('buttonPadSF', 'Button Padding SF', float),
    # Alpha of fade screen behind dialog
    Definition('fadeScreen', 'Fade Screen', bool),
    COMMAND_DEFINITION,
    COMMAND_ARGS_DEFINITION
]



DEFINITIONS = {
    "DirectButton":DIRECT_BUTTON_DEFINITIONS,
    "DirectCheckBox":DIRECT_BUTTON_DEFINITIONS + [
        Definition('uncheckedImage', 'Unchecked Image', object, editType=t.path),
        Definition('checkedImage', 'Checked Image', object, editType=t.path),
        Definition('isChecked', 'Is Checked', bool)
    ],
    "DirectCheckButton":DIRECT_BUTTON_DEFINITIONS + [
        Definition('indicatorValue', 'Indicator Value', bool),
        # boxBorder defines the space created around the check box
        Definition('boxBorder', 'Box Border', float),
        # boxPlacement maps left, above, right, below
        Definition('boxPlacement', 'Box Placement', str),
        Definition('boxImage', 'Box Image', object, editType=t.path),
        Definition('boxImageScale', 'Box Image Scale', object, editType=t.base3, nullable=True),
        Definition('boxImageColor', 'Box Image Color', object, editType=t.base4, nullable=True),
        Definition('boxRelief', 'Box Relief', str, editType=t.optionMenu)
    ],
    "DirectDialog":DEFAULT_DIALOG_DEFINITIONS,
    "OkDialog":DEFAULT_DIALOG_DEFINITIONS,
    "OkCancelDialog":DEFAULT_DIALOG_DEFINITIONS,
    "YesNoDialog":DEFAULT_DIALOG_DEFINITIONS,
    "YesNoCancelDialog":DEFAULT_DIALOG_DEFINITIONS,
    "RetryCancelDialog":DEFAULT_DIALOG_DEFINITIONS,
    "DirectEntry":DIRECT_FRAME_DEFINITIONS + [
        # Define type of DirectGuiWidget
        Definition('entryFont', 'Entry Font', object, editType=t.path),
        Definition('width', 'Entry Width', float),
        Definition('numLines', 'Num Lines', int),
        Definition('focus', 'Focus', bool),
        Definition('cursorKeys', 'Cursor Keys', bool),
        Definition('obscured', 'Obscured', bool),
        # Setting backgroundFocus allows the entry box to get keyboard
        # events that are not handled by other things (i.e. events that
        # fall through to the background):
        Definition('backgroundFocus', 'Background Focus', bool),
        # Text used for the PGEntry text node
        # NOTE: This overrides the DirectFrame text option
        Definition('initialText', 'Initial Text', str),
        # Enable or disable text overflow scrolling
        Definition('overflow', 'Overflow', bool),
        # Command to be called on hitting Enter
        COMMAND_DEFINITION,
        COMMAND_ARGS_DEFINITION,
        # Command to be called when enter is hit but we fail to submit
        Definition('failedCommand', 'Failed Command', types.FunctionType),
        Definition('failedExtraArgs', 'Failed Command Extra Args', list),
        # commands to be called when focus is gained or lost
        Definition('focusInCommand', 'Focus-In Command', types.FunctionType),
        Definition('focusInExtraArgs', 'Focus-In Command Extra Args', list),
        Definition('focusOutCommand', 'Focus-Out Command', types.FunctionType),
        Definition('focusOutExtraArgs', 'Focus-Out Command Extra Args', list),
        # Sounds to be used for button events
        Definition('rolloverSound', 'Rollover Sound', object, editType=t.path),
        Definition('clickSound', 'Click Sound', object, editType=t.path),
        Definition('autoCapitalize', 'Auto Capitalize', bool),
        Definition('autoCapitalizeAllowPrefixes', 'Auto Capitalize Allow Prefixes', list),
        Definition('autoCapitalizeForcePrefixes', 'Auto Capitalize Force Prefixes', list)
    ],
    "DirectEntryScroll":DIRECT_FRAME_DEFINITIONS + [
        Definition('clipSize', 'Clip Size', object)
    ],
    "DirectFrame":DIRECT_FRAME_DEFINITIONS,
    "DirectLabel":DIRECT_FRAME_DEFINITIONS + [
        Definition('activeState', '', int)
    ],
    "DirectOptionMenu":DIRECT_BUTTON_DEFINITIONS + [
        # List of items to display on the popup menu
        Definition('items', 'Items', list, editType=t.list),
        # Initial item to display on menu button
        # Can be an integer index or the same string as the button
        Definition('initialitem', 'Initial Item', object),
        # Amount of padding to place around popup button indicator
        Definition('popupMarkerBorder', 'Popup Marker Border', tuple),
        # The initial position of the popup marker
        Definition('popupMarker_pos', 'Popup Marker Position', object),
        # Background color to use to highlight popup menu items
        Definition('highlightColor', 'Highlight Color', object),
        # Extra scale to use on highlight popup menu items
        Definition('highlightScale', 'Highlight Scale', tuple),
        # Alignment to use for text on popup menu button
        # Changing this breaks button layout
        Definition('text_align', 'Text Align', int),
        # Remove press effect because it looks a bit funny
        Definition('pressEffect', 'Press Effect', bool)
    ],
    "DirectRadioButton":DIRECT_BUTTON_DEFINITIONS + [
        Definition('indicatorValue', '', bool),
        # variable is a list whose value will be set by this radio button
        Definition('variable', '', list),
        # value is the value to be set when this radio button is selected
        Definition('value', '', list),
        # others is a list of other radio buttons sharing same variable
        Definition('others', '', list),
        # boxBorder defines the space created around the check box
        Definition('boxBorder', '', int),
        # boxPlacement maps left, above, right, below
        Definition('boxPlacement', '', str),
        # boxGeom defines geom to indicate current radio button is selected or not
        Definition('boxGeom', '', object, editType=t.path),
        Definition('boxGeomColor', '', object),
        Definition('boxGeomScale', '', object),
        Definition('boxImage', '', object, editType=t.path),
        Definition('boxImageScale', '', object),
        Definition('boxImageColor', '', object),
        Definition('boxRelief', '', object)
    ],
    "DirectScrollBar":DEFAULT_DEFINITIONS + [
        Definition('range', '', tuple),
        Definition('value', '', float),
        Definition('scrollSize', '', float),
        Definition('pageSize', '', float),
        Definition('orientation', '', str),
        Definition('manageButtons', '', bool),
        Definition('resizeThumb', '', bool),

        # Function to be called repeatedly as the bar is scrolled
        COMMAND_DEFINITION,
        COMMAND_ARGS_DEFINITION
    ],
    "DirectScrolledFrame":DEFAULT_DEFINITIONS + [
        Definition('canvasSize', '', object),
        Definition('manageScrollBars', '', bool),
        Definition('autoHideScrollBars', '', bool),
        Definition('scrollBarWidth', '', float),
        Definition('borderWidth', '', tuple)
    ],
    "DirectScrolledList":DEFAULT_DEFINITIONS + [
        # Define type of DirectGuiWidget
        Definition('items', '', list),
        Definition('itemsAlign', '', int),
        Definition('itemsWordwrap', '', object),
        COMMAND_DEFINITION,
        COMMAND_ARGS_DEFINITION,
        Definition('itemMakeFunction', '', types.FunctionType),
        Definition('itemMakeExtraArgs', '', list),
        Definition('numItemsVisible', '', int),
        Definition('scrollSpeed', '', int),
        Definition('forceHeight', '', object),
        Definition('incButtonCallback', '', types.FunctionType),
        Definition('decButtonCallback', '', types.FunctionType)
    ],
    "DirectScrolledListItem":DEFAULT_DEFINITIONS + [
        COMMAND_DEFINITION,
        COMMAND_ARGS_DEFINITION
    ],
    "DirectSlider":DEFAULT_DEFINITIONS + [
        Definition('range', '', tuple),
        Definition('value', '', float),
        Definition('scrollSize', '', float),
        Definition('pageSize', '', float),
        Definition('orientation', '', str),

        # Function to be called repeatedly as slider is moved
        COMMAND_DEFINITION,
        COMMAND_ARGS_DEFINITION
    ],
    "DirectWaitBar":DEFAULT_DEFINITIONS + [
        Definition('borderWidth', '', tuple),
        Definition('range', '', float),
        Definition('value', '', float),
        Definition('barBorderWidth', '', tuple),
        Definition('barColor', '', object),
        Definition('barTexture', '', object, editType=t.path),
        Definition('barRelief', '', str),
        Definition('sortOrder', '', int)
    ],
    "OnscreenGeom":GEOM_DEFINITIONS,
    "OnscreenImage":IMAGE_DEFINITIONS,
    "OnscreenText":TEXT_DEFINITIONS
}
