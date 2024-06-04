"""
Application:    Power Hierarchy Plugin
Copyright:      PowerHouse Industries Jun 2024
Author:         Brian Etheridge
"""

import os, c4d
# Module for various shared functions
import rh_functions

config = rh_functions.get_config_values()
debug = bool(int(config.get(rh_functions.CONFIG_SECTION, 'debug')))
verbose = bool(int(config.get(rh_functions.CONFIG_SECTION, 'verbose')))
separator = config.get(rh_functions.CONFIG_SECTION, 'separator')

# ===================================================================
def get_hierarchy_objects(obj, obj_list, name_list, name):
# ===================================================================
    # Add the current object to the list
    obj_list.append(obj)
    name_list.append(name)

    # Check if the object has children
    if obj.GetDown():
        # Get the first child object
        child = obj.GetDown()

        # Recursively call the function on the child object
        while child:
            # Recursive call on the down child object
            get_hierarchy_objects(child, obj_list, name_list, (name + separator + child.GetName()))
            # *** get_hierarchy_objects(child, obj_list, name_list, child.GetName())

            # Get the next sibling
            child = child.GetNext()

    return [obj_list, name_list]

# ===================================================================
def find_hierarchy_object(obj, name, exactSearch):
# ===================================================================
    # Is this our target object
    if True == exactSearch:
        if name == obj.GetName():
            return obj
    else:
        # Search for the name
        if -1 != name.lower().find(obj.GetName().lower()):
            return obj

    # Check if the object has children
    if obj.GetDown():
        # Get the first child object
        child = obj.GetDown()

        # Recursively call the function on the child object
        while child:
            # Recursive call on the child object
            returned_obj = find_hierarchy_object(child, name, exactSearch)
            if None != returned_obj:
                return returned_obj

            # Get the next sibling
            child = child.GetNext()

    return None

# ===================================================================
def copy_object_attributes(doc, fromObj, toObj):
# ===================================================================

    if True == debug:
        print("Copying attributes from source object: " + fromObj.GetName() + " to target object: " + toObj.GetName())

    description = toObj.GetDescription(c4d.DESCFLAGS_DESC_NONE)    # Get the description of the target object

    '''
        # This section of code outputs all the description parameters
        for bc, paramid, groupid in description:                    # Iterate over the parameters of the description
            print(bc[c4d.DESC_NAME])                                # Print the current parameter name
            print(paramid)
            print(groupid)
            print("************")
        # The original code restored the 110050 parameter, but not sure what that is
        did_list = [
            c4d.DescID(c4d.DescLevel(110050, 1, 110050)),
            c4d.DescID(c4d.DescLevel(1041666, 1, 110050))
            ]
    '''

    # Backup basic properties
    info_list = []
    did_list = [
        c4d.DescID(c4d.DescLevel(1041666, 1, 110050)),  # Basic properties
        ]
    for bc, paramid, groupid in description:
        try:
            if groupid in did_list:
                if None != toObj[paramid]:
                    info_list.append((paramid, toObj[paramid]))

        except Exception as e:
            message = "Error encountered building parameters " + fromObj.GetName() + ": " + str(e)
            print(message)
            return False

    try:
        fromObj.CopyTo(toObj,
            c4d.COPYFLAGS_NO_BRANCHES|
            c4d.COPYFLAGS_NO_MATERIALPREVIEW|
            c4d.COPYFLAGS_NO_BITS|
            c4d.COPYFLAGS_PRIVATE_IDENTMARKER
            )

        # Restore basic properties in target object
        for info in info_list:
            toObj[info[0]] = info[1]

    except Exception as e:
        message = "Error encountered copying object " + fromObj.GetName() + ": " + str(e)
        print(message)
        return False

    return True

# ===================================================================
def copy_tracks(doc, fromObj, toObj):
# ===================================================================
    if True == debug:
        print("Copying tracks from source object: " + fromObj.GetName() + " to target object: " + toObj.GetName())

    # Retrieves all the CTrack of fromObj. CTracks contains all keyframes information of a parameter.
    tracks = fromObj.GetCTracks()
    if not tracks:
        if True == debug:
            print("No tracks information for source object: " + fromObj.GetName())

    # Defines a list that will contains the ID of parameters we want to copy.
    # Such ID can be found by drag-and-drop a parameter into the python console.
    didListToCopy = [
        c4d.ID_BASEOBJECT_REL_POSITION,
        c4d.ID_BASEOBJECT_REL_ROTATION,
        c4d.ID_BASEOBJECT_REL_SCALE,
        700
        ]

    # Iterates overs the CTracks of fromObj.
    for track in tracks:
        # Retrieves the full parameter ID (DescID) describing a parameter.
        did = track.GetDescriptionID()

        # If the Parameter ID of the current CTracks is not on the trackListToCopy we go to the next one.
        if not did[0].id in didListToCopy:
            if True == debug:
                print("DID not included in our copying process: " + str(did[0].id))
            continue

        # Find if our static object already got an animation track for this parameter ID.
        foundTrack = toObj.FindCTrack(did)
        if foundTrack:
            # Removes the track if found
            if True == debug:
                print("Replacing track in target object for DID: " + str(did[0].id))
            foundTrack.Remove()

        # Copies the initial CTrack in memory. All CCurve and CKey are kept in this CTrack.
        clone = track.GetClone()

        # Inserts the copied CTrack to the static object.
        toObj.InsertTrackSorted(clone)

    # Updates toObj Geometry taking in account previously created keyframes
    animateFlag = c4d.ANIMATEFLAGS_NONE if c4d.GetC4DVersion() > 20000 else c4d.ANIMATEFLAGS_0
    doc.AnimateObject(toObj, doc.GetTime(), animateFlag)

    return