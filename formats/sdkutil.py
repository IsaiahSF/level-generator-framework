import os, re
from gameids import *

## Provides commonly used utility functions
class SDKUtil:
    
    ## mapping of gameID to game directory
    _gamePaths = {
        HL2     : '%username%/half-life 2/hl2',
        HL2EP1  : '%username%/half-life 2 episode one/episodic',
        HL2EP2  : '%username%/half-life 2 episode two/ep2',
        HL2DM   : '%username%/half-life 2 deathmatch/hl2mp',
        P1      : '%username%/portal/portal',
        P2      : 'common/portal 2/portal2',
        L4D1    : 'common/left 4 dead/left4dead',
        L4D2    : 'common/left 4 dead 2/left4dead2',
        TF2     : '%username%/team fortress 2/tf',
        CSS     : '%username%/counter-strike source/cstrike',
        GMOD    : '%username%/garrysmod/garrysmod'
        }

    ## Checks if Source SDK is installed
    #
    #  @return boolean True if installed
    #
    @staticmethod
    def check():
        returnval = []
        if os.getenv('sourcesdk') == None:
            returnval.append("Source SDK needs to be installed and run at least once.")
        return returnval
    
    ## Checks if path contains all required utilities
    #
    #  @return boolean
    #
    @staticmethod
    def checkHammerPath(hammerPath):
        return all([
            os.path.isdir(hammerPath + '/bin'),
            os.path.isfile(hammerPath + '/bin/hammer.exe'),
            os.path.isfile(hammerPath + '/bin/vbsp.exe'),
            os.path.isfile(hammerPath + '/bin/vvis.exe'),
            os.path.isfile(hammerPath + '/bin/vrad.exe')
            ])
    
    ## Check for needed game utilities
    #
    #  @return list List of gameIDs that can be worked on
    #
    @staticmethod
    def checkGames():
        gamelist = []
        #check for compilation utilities
        userName, basePath = SDKUtil.findUserAndBasePath()
        hammerPath = None
        #portal 2
        hammerPath = basePath + '/common/portal 2'
        if SDKUtil.checkHammerPath(hammerPath):
            gamelist.append(P2)
        #l4d1
        hammerPath = basePath + '/common/left 4 dead'
        if SDKUtil.checkHammerPath(hammerPath):
            gamelist.append(L4D1)
        #l4d2
        hammerPath = basePath + '/common/left 4 dead 2'
        if SDKUtil.checkHammerPath(hammerPath):
            gamelist.append(L4D2)
        #counter strike source, team fortress 2
        hammerPath = basePath + '/' + userName + '/sourcesdk/bin/orangebox'
        if SDKUtil.checkHammerPath(hammerPath):
            gamelist.extend([CSS, TF2])
        #hl2, hl2dm, hl2ep1, hl2ep2, portal 1
        hammerPath = basePath + '/' + userName + '/sourcesdk/bin/source2009'
        if SDKUtil.checkHammerPath(hammerPath):
            gamelist.extend([HL2, HL2EP1, HL2EP2, HL2DM, GMOD])
        #check that game directory can be found
        gamelist = [x for x in gamelist if os.path.isdir(SDKUtil.findGamePath(x))]
        return gamelist

    ## finds steam username and steam installation path
    #
    #  @return (user, path) tuple
    #
    @staticmethod
    def findUserAndBasePath():
        #uses an environment variable
        value = os.getenv('sourcesdk')
        if value == None:
            raise Exception("Source SDK must be installed and run at least once.")
        
        #manipulate path to get base path and steam username
        value = value.replace('\\', '/')
        value = value.split('/')
        ## Steam _userName
        user = value[-2]
        ## Path of Steam installation
        base = '/'.join(value[:-2])
        return user, base

    ## Finds the bin path for hammer
    #
    #  @param gameID game to find bin path for
    #  @return path
    #
    @staticmethod
    def findHammerPath(gameID):
        userName, basePath = SDKUtil.findUserAndBasePath()
        assert os.path.isdir(basePath)
        #different engine versions?
        hammerPath = None
        if gameID == P2:
            #works for portal 2
            hammerPath = basePath + '/common/portal 2'
        elif gameID == L4D1:
            hammerPath = basePath + '/common/left 4 dead'
        elif gameID == L4D2:
            #works for l4d2
            hammerPath = basePath + '/common/left 4 dead 2'
        elif gameID == CSS or gameID == TF2:
            #works for counter strike and team fortress 2
            hammerPath = basePath + '/' + userName + '/sourcesdk/bin/orangebox'
        else:
            #works for hl2, hl2dm, hl2ep1, hl2ep2, portal 1
            #but not portal 2, l4d2, hl2dm(?)
            hammerPath = basePath + '/' + userName + '/sourcesdk/bin/source2009'
        #validate
        if not SDKUtil.checkHammerPath(hammerPath):
            raise Exception("Game or game SDK/authoring tools not set up correctly for " + str(gameID) + ".")
        ## Path of directory containing hammer, VBSP, VVIS, VRAD.
        return hammerPath

    ## Find game installtion path
    #
    #  @param game gameID of game
    #  @return path (contains /maps where maps are installed)
    @staticmethod
    def findGamePath(game):
        userName, basePath = SDKUtil.findUserAndBasePath()
        assert os.path.isdir(basePath)
        assert SDKUtil._gamePaths[game]!=None
        gamepath = basePath + '/' + SDKUtil._gamePaths[game]
        gamepath = gamepath.replace('%username%', userName)
        ## Path of game directory. contains maps folder for compiled maps
        return gamepath

    ## parse a list of numbers
    #
    #  @param string string to parse
    #  @param cast type to cast results to
    #  @return list of numbers
    #
    @staticmethod
    def getNumbers(string, cast):
        string = string.replace(",","")
        string = string.replace("(","")
        string = string.replace(")","")
        string = string.replace("[","")
        string = string.replace("]","")
        
        return list(map(
            cast,
            re.findall("\S+", string)
            ))
