import inspect, sys

if sys.version_info.major == 2:
    #for Python 2.x
    from Tkinter import *
else:
    #for Python 3.x
    from tkinter import *

#code execution must start from the root folder (LevelGen) for this to work
from progresssubject import ProgressSubject
from configgui import ConfigGUI

## Defines interface for generators.
#
#  This class is an interface. It defines the requirements for generators, which
#  generate levels.
#
class Generator(ProgressSubject):

    ## human-readable name of the generator
    name = None

    ## human-readable description, notes and/or instructions
    description = None

    ## list of map file format extensions supported by this generator.
    #  must be defined in gameids.py
    formats = None

    ## list of games supported by this generator.
    #  must be defined in gameids.py
    games = None

    ## ConfigGUI implementation to contain GUI mess
    configGUI = None

    ## Constructor
    def __init__(self, parent):
        ProgressSubject.__init__(self)
        assert inspect.ismethod(parent.getMap) #need this method to get maps
        ## a class instance with a .newMap() method that returns a Map object.
        self.parent = parent
        ## ConfigGUI implementation to contain GUI mess.
        if self.__class__.configGUI == None:
            raise NotImplementedError()
        self.configGUI = self.__class__.configGUI(self.__class__.name, self)

    ## GUI to configure generator options
    def showGUI(self, rootwindow):
        self.configGUI.showGUI(rootwindow)
    
    ## Generates the map(s)
    def generate(self, gameID):
        raise NotImplementedError()
