"""
Application:    Power Hierarchy Plugin
Copyright:      PowerHouse Industries Jun 2024
Author:         Brian Etheridge

Description:
    A utility to copy animation tracks between similar object hierarchies in Cinema 4D.
"""

import os, sys
import c4d
from c4d import gui, bitmaps, utils
from c4d import documents
from c4d import modules
from c4d import storage
# Add modules to the path before trying to reference them
__root__ = os.path.dirname(__file__)
if os.path.join(__root__, 'modules') not in sys.path: sys.path.insert(0, os.path.join(__root__, 'modules'))
# Module for various shared functions
import rh_functions, rh_hierarchy_functions

__res__ = c4d.plugins.GeResource()
__res__.Init(__root__)

# Unique ID obtained from www.plugincafe.com
PLUGIN_ID = 48484848
GROUP_ID_HELP = 100000
GROUP_ID_FORM = 100001
GROUP_ID_BUTTONS = 100002
FRAME_RANGES_HELP_1 = 100005
FRAME_RANGES_HELP_2 = 100006

SOURCE_HIERARCHY_TEXT = 100010
SOURCE_HIERARCHY_EDIT = 100011
TARGET_HIERARCHY_TEXT = 100012
TARGET_HIERARCHY_EDIT = 100013
CLOSE_BUTTON = 100014
GO_BUTTON = 100015
TAG_LINE = 100020

SOURCE = 'source'
TARGET = 'target'

config = rh_functions.get_config_values()
debug = bool(int(config.get(rh_functions.CONFIG_SECTION, 'debug')))
verbose = bool(int(config.get(rh_functions.CONFIG_SECTION, 'verbose')))

# ===================================================================
class HierarchyDlg(c4d.gui.GeDialog):
# ===================================================================
    # Clunky way to distinguish between source and target
    dragName = ''
    dragToNameField = ''

    source = config.get(rh_functions.CONFIG_SECTION, 'source')
    target = config.get(rh_functions.CONFIG_SECTION, 'target')

    # ===================================================================
    def Message(self, msg, result):
    # Event handler used for drag and drop purposes
    # ===================================================================

        if msg.GetId() == c4d.BFM_DRAGEND:
            # We only want to assign the name when the drag process has ended
            # But at this point the drop area is not set, so record the drag details below and then use them here
            if SOURCE == self.dragToNameField:
                self.SetString(SOURCE_HIERARCHY_EDIT, self.dragName)

            if TARGET == self.dragToNameField:
                self.SetString(TARGET_HIERARCHY_EDIT, self.dragName)

        if msg.GetId() == c4d.BFM_DRAGRECEIVE:
            # check if the dragging operation is into the edit form field
            if True == self.CheckDropArea(SOURCE_HIERARCHY_EDIT,msg,True,True):
                draginfo = self.GetDragObject(msg)
                obj = draginfo['object']

                if 1 == len(obj):
                    if 5140 == obj[0].GetType():
                        self.dragName = obj[0].GetName()
                        self.dragToNameField = SOURCE
                        return gui.GeDialog.Message(self, msg, result)

                    else:
                        gui.MessageDialog('Invalid object type: ' + str(obj[0].GetType()))

                # otherwise, signal that is not allowed
                return self.SetDragDestination(c4d.MOUSE_FORBIDDEN, SOURCE_HIERARCHY_EDIT)

            elif True == self.CheckDropArea(TARGET_HIERARCHY_EDIT,msg,True,True):
                draginfo = self.GetDragObject(msg)
                obj = draginfo['object']
                if 1 == len(obj):
                    if 5140 == obj[0].GetType():
                        self.dragName = obj[0].GetName()
                        self.dragToNameField = TARGET
                        return gui.GeDialog.Message(self, msg, result)

                    else:
                        gui.MessageDialog('Invalid object type: ' + str(obj[0].GetType()))

                # otherwise, signal that is not allowed
                return self.SetDragDestination(c4d.MOUSE_FORBIDDEN)

        return gui.GeDialog.Message(self, msg, result)

    # ===================================================================
    def CreateLayout(self):
    # ===================================================================
        """ Called when Cinema 4D creates the dialog """

        self.SetTitle("Power Hierarchy")

        self.GroupBegin(id=GROUP_ID_HELP, flags=c4d.BFH_SCALEFIT, cols=1, rows=2)
        # Spaces: left, top, right, bottom
        self.GroupBorderSpace(10,10,10,10)
        """ Instructions """
        self.AddStaticText(id=FRAME_RANGES_HELP_1, flags=c4d.BFV_MASK, initw=720, name="Copy attributes and animation tracks from the source to target hierarchy objects", borderstyle=c4d.BORDER_NONE)
        self.AddStaticText(id=FRAME_RANGES_HELP_2, flags=c4d.BFV_MASK, initw=720, name="", borderstyle=c4d.BORDER_NONE)
        self.GroupEnd()

        self.GroupBegin(id=GROUP_ID_FORM, flags=c4d.BFH_SCALEFIT, cols=2, rows=3)
        # Spaces: left, top, right, bottom
        self.GroupBorderSpace(10,0,10,0)
        """ Custom ranges field """
        self.AddStaticText(id=SOURCE_HIERARCHY_TEXT, flags=c4d.BFV_MASK, initw=160, name="Source hierarchy:", borderstyle=c4d.BORDER_NONE)
        self.AddEditText(id=SOURCE_HIERARCHY_EDIT, flags=c4d.BFV_MASK, initw=340, inith=16, editflags=0)
        self.AddStaticText(id=TARGET_HIERARCHY_TEXT, flags=c4d.BFV_MASK, initw=160, name="Target hierarchy:", borderstyle=c4d.BORDER_NONE)
        self.AddEditText(id=TARGET_HIERARCHY_EDIT, flags=c4d.BFV_MASK, initw=340, inith=16, editflags=0)
        self.AddStaticText(id=TAG_LINE, flags=c4d.BFH_FIT | c4d.BFH_RIGHT, initw=440, name="Powerhouse Industries", borderstyle=c4d.BORDER_NONE)
        self.AddStaticText(id=TAG_LINE, flags=c4d.BFH_RIGHT, initw=440, name="", borderstyle=c4d.BORDER_NONE)
        # self.AddStaticText(id=TAG_LINE, flags=c4d.BFH_RIGHT, initw=440, name="https://powerhouse.industries", borderstyle=c4d.BORDER_NONE)
        self.GroupEnd()

        self.SetString(SOURCE_HIERARCHY_EDIT, self.source)
        self.SetString(TARGET_HIERARCHY_EDIT, self.target)

        self.GroupBegin(id=GROUP_ID_BUTTONS, flags=c4d.BFH_SCALEFIT, cols=4, rows=5)
        # Spaces: left, top, right, bottom
        self.GroupBorderSpace(10,20,10,20)
        """ Button fields """
        self.AddButton(id=CLOSE_BUTTON, flags=c4d.BFH_RIGHT | c4d.BFV_CENTER, initw=100, inith=16, name="Close")
        self.AddButton(id=GO_BUTTON, flags=c4d.BFH_RIGHT | c4d.BFV_CENTER, initw=150, inith=16, name="Go ahead")
        self.GroupEnd()

        self.SetDragDestination(c4d.MOUSE_INSERTCOPY, SOURCE_HIERARCHY_EDIT)
        self.SetDragDestination(c4d.MOUSE_INSERTCOPY, TARGET_HIERARCHY_EDIT)

        return True

    # ===================================================================
    def Command(self, messageId, bc):
    # ===================================================================
        """
        Called when the user clicks on the dialog or clicks a button
            messageId (int): The ID of the resource that triggered the event
            bc (c4d.BaseContainer): The original message container
        Returns False on error else True.
        """

        # User click on Ok button
        if messageId == GO_BUTTON:

            # Get the active document
            doc = c4d.documents.GetActiveDocument()
            if doc is None:
                print("No document object found")
                return False

            self.source_obj = doc.SearchObject(self.GetString(SOURCE_HIERARCHY_EDIT))
            if None != self.source_obj:
                self.source = self.source_obj.GetName()
            self.target_obj = doc.SearchObject(self.GetString(TARGET_HIERARCHY_EDIT))
            if None != self.target_obj:
                self.target = self.target_obj.GetName()

            if True == verbose:
                print("Go button clicked for source: " + self.source)
                print("Go button clicked for target: " + self.target)

            try:
                # Validate the source and target objects
                self.isValid()

                # Save changes to the config file
                rh_functions.update_config_values(rh_functions.CONFIG_SECTION, [
                    ('source', str(self.source)),
                    ('target', str(self.target))
                    ])
            except Exception as e:
                message = str(e)
                print(message)
                gui.MessageDialog(message)
                return False

            obj_list = []
            name_list = []

            # Call the recursive function to load hierarchy objects, starting from the top
            lists = rh_hierarchy_functions.get_hierarchy_objects(self.source_obj, obj_list, name_list, self.source_obj.GetName())

            # Print the names of all objects in hierarchy
            if True == verbose:
                print("\nObjects: ")
                for obj in lists[0]:
                    print(obj.GetName())

            if True == debug:
                print("\nCompound names: ")
                for name in lists[1]:
                    print("\t" + name)

            # Iterate entries in the object list
            for source_obj_element in lists[0]:
                # Ignore the top level source object
                if source_obj_element.GetName() == self.source:
                    continue

                # Find the corresponding name in the target
                target_obj_element = rh_hierarchy_functions.find_hierarchy_object(self.target_obj, source_obj_element.GetName())
                if None != target_obj_element:

                    # *** Start by copying over the attributes
                    rh_hierarchy_functions.copy_object_attributes(doc, source_obj_element, target_obj_element)

                    # *** Now copy the animation tracks
                    rh_hierarchy_functions.copy_tracks(doc, source_obj_element, target_obj_element)

                else:
                    print("For source name: " + source_obj_element.GetName() + " could not find target object")

            # Update C4D interface
            c4d.EventAdd()

            # Completion
            gui.MessageDialog("Attributes and animation tracks copied from " + self.source + " to " + self.target)

        # User clicked on the Close button
        elif messageId == CLOSE_BUTTON:

            print("Dialog closed")
            # Close the Dialog
            self.Close()
            return True

        return True

    # ===================================================================
    def isValid(self):
    # ===================================================================
        """
        Check that we have been supplied with both source and target objects
        """

        message = ''
        sep = "\n"
        if None == self.source_obj:
            message += (sep + "Source object is required")

        if None == self.target_obj:
            message += (sep + "Target object is required")

        if None != self.source_obj and self.source_obj == self.target_obj:
            message += (sep + "Source and target cannot be the same object")

        if None != self.source_obj and None == self.source_obj.GetDown():
            message += (sep + "Source must have at least one child")

        if "" != message:
            raise RuntimeError(message)

        return

# ===================================================================
class HierarchyDlgCommand(c4d.plugins.CommandData):
# ===================================================================
    """
    Command Data class holding the RenderDlg instance
    """
    dialog = None

    # ===================================================================
    def Execute(self, doc):
    # ===================================================================
        """
        Called when the user executes CallCommand() or a menu option
        Returns True if the command success.
        """

        # Creates the dialog if it does not already exists
        if self.dialog is None:
            self.dialog = HierarchyDlg()

        # Opens the dialog
        return self.dialog.Open(dlgtype=c4d.DLG_TYPE_ASYNC, pluginid=PLUGIN_ID, defaultw=720, defaulth=32)

    # ===================================================================
    def RestoreLayout(self, sec_ref):
    # ===================================================================
        """
        Restore an asynchronous dialog that has been displayed in the users layout
        Returns True if the restore successful
        """
        # Creates the dialog if its not already exists
        if self.dialog is None:
            self.dialog = HierarchyDlg()

        # Restores the layout
        return self.dialog.Restore(pluginid=PLUGIN_ID, secret=sec_ref)

# ===================================================================
# main entry function
# ===================================================================
if __name__ == "__main__":
    try:
        print("* Setting up Power Hierarchy Version 1")

        # Retrieves the icon path
        directory, _ = os.path.split(__file__)
        fn = os.path.join(directory, "res", "icon_hierarchy.tif")

        # Creates a BaseBitmap
        bbmp = c4d.bitmaps.BaseBitmap()
        if bbmp is None:
            raise MemoryError("Failed to create a BaseBitmap.")

        # Init the BaseBitmap with the icon
        if bbmp.InitWith(fn)[0] != c4d.IMAGERESULT_OK:
            raise MemoryError("Failed to initialise the BaseBitmap.")

        # Registers the plugin
        c4d.plugins.RegisterCommandPlugin(id=PLUGIN_ID,
                                          str="Power Hierarchy",
                                          info=0,
                                          help="Power Hierarchy",
                                          dat=HierarchyDlgCommand(),
                                          icon=bbmp)

        print("* Power Hierarchy set up ok")

    except Exception as e:
        message = "* Error on Power Hierarchy set up: " + str(e)
        print(message)
        gui.MessageDialog(message)
