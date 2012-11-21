import os

#code execution must start from the root folder (LevelGen) for this to work
from progresssubject import ProgressSubject
from gameids import *

## Defines interface for executors.
#
#  This class is an interface. It defines the requirements for format Executors,
#  which control compilation and game launching for specific level formats.
class Executor(ProgressSubject):

    ## human-readable name of the map type
    name = None

    ## the map file format extension this module supports
    mapFormat = None

    ## ConfigGUI implementation to contain GUI mess
    configGUI = None

    ## Constructor
    #
    #  @param gameID short string identifying what game to use. Must be in the
    #  Executor.gameIDs list.
    def __init__(self, gameID):
        ProgressSubject.__init__(self)
        ## integer ranging from 0-3 inclusive.
        #  0 skips as much as possible, resulting in a bare, unoptimized, ugly map.
        #  1 takes some shortcuts in quality but doesn't skip major steps.
        #  2 represents a normal level of quality.
        #  3 represents an extra high level of quality.
        self._quality = 2
        ## List of map files to compile
        self._mapList = None
        self.setGameID(gameID)
        ## ConfigGUI implementation to contain GUI mess.
        if self.__class__.configGUI == None or \
           self.__class__.name == None:
            raise NotImplementedError()
        self.configGUI = self.__class__.configGUI(self.__class__.name, self)

    ## GUI to configure compilation options
    def showGUI(self, rootwindow):
        self.configGUI.showGUI(rootwindow)

    ## Get the game Executor is set to use.
    #
    #  This is the game that the level will be compiled for, installed in, and
    #  the game that will be launched.
    #
    #  @return string ID of game
    def getGameID(self):
        return self._gameID

    ## set the game Executor will use.
    #
    #  This is the game that the level will be compiled for, installed in, and
    #  the game that will be launched.
    #
    #  @param gameID short string identifying what game to use. Must be in
    #  Executor.gameIDs list.
    def setGameID(self, gameID):
        assert gameID in getFormatGames(self.mapFormat)
        ## name of game for editing, compiling, and running levels
        self._gameID = gameID

    ## Set compilation quality.
    #
    #  @param quality integer ranging from 0-3 inclusive.
    #  0 skips as much as possible, resulting in a bare, unoptimized, ugly map.
    #  1 takes some shortcuts in quality but doesn't skip major steps.
    #  2 represents a normal level of quality.
    #  3 represents an extra high level of quality.
    def setQuality(self, quality):
        assert type(quality) == int
        assert quality>=0 and quality<=3
        self._quality = quality

    ## Set map list.
    #
    #  @param mapList a list of paths to uncompiled map files. The first map in
    #  the list is the map that is loaded in the game or editor, if any.
    def setMapList(self, mapList):
        #able to accept single map as string instead of 1-item list
        if type(mapList) == str:
            mapList = [mapList]
        assert type(mapList) == list
        #all must be valid files
        assert all(map(os.path.isfile, mapList))
        #all must have correct file extension
        assert all(map(lambda x: x.endswith(self.mapFormat), mapList))
        self._mapList = map(os.path.abspath, mapList)
        self._mapList = map(lambda x: x.replace('\\','/'), self._mapList)
        self._mapList = list(self._mapList)

    ## Check whether an overwrite will occur when compiling or installing levels
    #
    #  @param prefix Checks for any map beginning with this prefix
    #
    #  @return boolean True if an overwrite will occur.
    def checkOverwrite(self, prefix):
        raise NotImplementedError()

    ## Open uncompiled map in appropriate map editor.
    #
    #  If there are multiple maps the first one will be opened.
    def edit(self):
        raise NotImplementedError()

    ## Compile a set of maps.
    #
    #  The maps will be compiled and installed for the specified game, using the
    #  specified quality setting.
    def compile(self):
        raise NotImplementedError()

    ## Launch generated map in game.
    #
    #  @exception Exception game has not yet been compiled and installed.
    def launch(self):
        raise NotImplementedError()

