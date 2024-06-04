"""
Application:    Power Hierarchy Plugin
Copyright:      PowerHouse Industries Jun 2024
Author:         Brian Etheridge
"""

import os, platform, c4d
from c4d import documents

try:
    # R2023
    import configparser as configurator
except:
    # Prior to R2023
    import ConfigParser as configurator

__root__ = os.path.dirname(os.path.dirname(__file__))

CONFIG_SECTION = 'CONFIG'

CONFIG_FILE = __root__ + '/config/properties.ini'

# ===================================================================
def get_config_values():
# ===================================================================
    # Returns entries in the config file
    # .....................................................
    config = configurator.ConfigParser()
    # Replace the translate function with 'str', which will stop ini field names from being lower cased
    config.optionxform = str
    config.read(CONFIG_FILE)
      
    return config


# ===================================================================
def get_hierarchy_objects(baseObject):
# ===================================================================
    currentObject = baseObject

    self.objectStack = []

    self.depth = 0
    self.nextDepth = 0

    def __iter__(self):
        return self

    def next(self):
        if self.currentObject == None :
            raise RuntimeError("Current object not found")

        obj = self.currentObject
        self.depth = self.nextDepth

        child = self.currentObject.GetDown()
        if child :
            self.nextDepth = self.depth + 1
            self.objectStack.append(self.currentObject.GetNext())
            self.currentObject = child
        else :
            self.currentObject = self.currentObject.GetNext()
            while( self.currentObject == None and len(self.objectStack) > 0 ) :
                self.currentObject = self.objectStack.pop()
                self.nextDepth = self.nextDepth - 1
        return obj

# ===================================================================
def update_config_values(section, configFields):
# ===================================================================
    # Updates a list of tuples of config field name and values
    # .....................................................

    config = get_config_values()
    verbose = config.get(CONFIG_SECTION, 'verbose')

    # configfields is a list of tuples:
    #    [('field name', 'field value'), ('field name', 'field value'), ...]
    #
    for field in configFields:
        if True == verbose:
            print("Config out: ", field[0], field[1])
        config.set(section, field[0], field[1])

    with open(CONFIG_FILE, 'w') as configFile:
        config.write(configFile)

    return config
