import os, shutil, subprocess, time, sys
if sys.version_info.major == 2:
    #for Python 2.x
    from Tkinter import *
else:
    #for Python 3.x
    from tkinter import *

from formats.executor import Executor
from formats.sdkutil import SDKUtil
from configgui import ConfigGUI
from gameids import *


## Configuration GUI for setting custom compilation options
class SDKConfigGUI(ConfigGUI):
    
    ## Defines GUI variables and layout
    def populateGUI(self):
        ## custom VBSP arguments entered by user
        self.bspArgs = StringVar()
        self.bspArgs.set(self.parent.customBSP)
        ## custom VVIS arguments entered by user
        self.visArgs = StringVar()
        self.visArgs.set(self.parent.customVIS)
        ## custom VRAD arguments entered by user
        self.radArgs = StringVar()
        self.radArgs.set(self.parent.customRAD)
        ## custom game arguments entered by user
        self.gameArgs = StringVar()
        self.gameArgs.set(self.parent.customGame)
        
        bspLabel = Label(self.window, text = "VBSP Arguments:")
        visLabel = Label(self.window, text = "VVIS Arguments:")
        radLabel = Label(self.window, text = "VRAD Arguments:")
        gameLabel = Label(self.window, text = "Game Arguments:")
        bspEntry = Entry(self.window, textvariable = self.bspArgs)
        visEntry = Entry(self.window, textvariable = self.visArgs)
        radEntry = Entry(self.window, textvariable = self.radArgs)
        gameEntry = Entry(self.window, textvariable = self.gameArgs)
        button1 = Button(
            self.window,
            text = 'OK',
            width = 5,
            command = self.applySettings
            )
        button2 = Button(
            self.window,
            text = 'Cancel',
            width = 5,
            command = self.window.destroy
            )

        bspLabel.grid(column = 0, row = 0, padx = 5, pady = 5, sticky = E)
        visLabel.grid(column = 0, row = 1, padx = 5, pady = 5, sticky = E)
        radLabel.grid(column = 0, row = 2, padx = 5, pady = 5, sticky = E)
        gameLabel.grid(column = 0, row = 3, padx = 5, pady = 5, sticky = E)
        bspEntry.grid(column = 1, row = 0, padx = 5, pady = 5, sticky = W)
        visEntry.grid(column = 1, row = 1, padx = 5, pady = 5, sticky = W)
        radEntry.grid(column = 1, row = 2, padx = 5, pady = 5, sticky = W)
        gameEntry.grid(column = 1, row = 3, padx = 5, pady = 5, sticky = W)
        button1.grid(column = 0, row = 4, padx = 5, pady = 5)
        button2.grid(column = 1, row = 4, padx = 5, pady = 5)

    ## apply user-specified settings and close window
    def applySettings(self):
        self.parent.customBSP = self.bspArgs.get()
        self.parent.customVIS = self.visArgs.get()
        self.parent.customRAD = self.radArgs.get()
        self.parent.customGame = self.gameArgs.get()
        ConfigGUI.closeGUI(self)

## Implements Executor for SDK games.
#
#  Cannot handle unicode paths with python 2.x (3.x is fine)
#
#  @sa Executor
class SDKExecutor(Executor):

    ## human-readable name of the map type
    name = 'Source Development Kit'

    ## the map file format extension this module supports
    mapFormat = VMF

    ## ConfigGUI class for configuring custom compilation
    configGUI = SDKConfigGUI

    ## mapping of gameID to Steam appID used to launch the game through steam
    _appIDs = {
        HL2     : '220',
        HL2EP1  : '380',
        HL2EP2  : '420',
        HL2DM   : '320',
        P1      : '400',
        P2      : '620',
        L4D1    : '500',
        L4D2    : '550',
        TF2     : '440',
        CSS     : '240',
        GMOD    : '4000'
        }

    ## Check for software needed to work with format
    #
    @staticmethod
    def checkReq():
        #check that SDK is installed
        return SDKUtil.check()
    
    ## Check for software needed to work with specific games
    #
    @staticmethod
    def usableGames():
        return SDKUtil.checkGames()
    
    ## Constructor
    #
    #  @param gameID short string identifying what game to use. Must be a constant
    #  in gameids.py
    def __init__(self, gameID):
        result = SDKUtil.findUserAndBasePath()
        ## steam username
        self._userName = result[0]
        ## steam installation directory
        self._basePath = result[1]
        Executor.__init__(self, gameID)
        self._subProgressWeight = 0.0
        self._subProgressOffset = 0.0
        self._metaStatus = ''
        
        #common parameters
        ## Compile at Low priority.
        self.low = False
        ## Enable verbose compilation command line output
        self.verbose = False
        
        #BSP parameters
        ## Custom argument list
        self.customBSP = ''
        ## Only update entities. Ignore brush geometry.
        self.onlyEntities = False
        ## Only update prop entities. Ignore brush geometry.
        self.onlyProps = False
        ## Skip func.detail brush entites.
        self.noDetail = False
        ## Omit water.
        self.noWater = False
        
        #VIS parameters
        ## Custom argument list
        self.customVIS = ''
        ## Skip VVIS (visibility optimization)
        self.doVIS = True
        ## Do quick and dirty visibility optimization
        self.fastVis = False
        ## Skip portal sorting optimization
        self.fastPortals = False
        
        #RAD parameters
        ## Custom argument list
        self.customRAD = ''
        ## Skip VRAD (map lighting)
        self.doRAD = True
        ## Lighting type: 1=ldr, 2=hdr, 3=both
        self.dynamicRange = 1
        ## Do quick and dirty map lighting
        self.fastRad = False
        ## Improve lighting quality. 1 is normal, 16 is "best" lighting quality.
        self.extraSky = None
        ## Set limit on number of light bounces
        self.limitBounce = None
        ## Soft lighting from sun. Sun fills (float) degrees in the sky.
        self.softSun = None
        ## Skip light supersampling
        self.noSuperSampling = False

        #game parameters
        ## Custom argument list
        self.customGame = ''
    
    ## set the game SDKExecutor will use.
    #
    #  This is the game that the level will be compiled for, installed in, and
    #  the game that will be launched.
    #
    #  @param gameID what game to use. Use game ID constant in gameids.py
    #
    def setGameID(self, gameID):
        Executor.setGameID(self, gameID)
        ## location of hammer, compilation utilities, and .fgd data files
        self._hammerPath = SDKUtil.findHammerPath(gameID)
        ## game directory
        self.gamePath = SDKUtil.findGamePath(gameID)

    ## Set compilation quality.
    #
    #  @param quality integer ranging from 0-3 inclusive.
    #  0 skips as much as possible, resulting in a bare, unoptimized, ugly map.
    #  1 takes some shortcuts in quality but doesn't skip major steps.
    #  2 represents a normal level of quality.
    #  3 represents an extra high level of quality.
    def setQuality(self, quality):
        Executor.setQuality(self, quality)
        presets = [
            self.presetFullbright,
            self.presetFast,
            self.presetNormal,
            self.presetBest
            ]
        #call appropriate quality preset method
        presets[self._quality]()

    ## Configure to compile maps without any lighting or visibility optimization
    def presetFullbright(self):
        #skipping VIS may be lagtastic on more complex stuff.
        #(then use fastVis instead)
        self.doVIS = False 
        self.doRAD = False

    ## Configure to compile map sacrificing quality for speed
    def presetFast(self):
        self.presetNormal()
        self.fastVis = True
        self.fastRad = True

    ## Configure to compile map using typical quality settings
    def presetNormal(self):
        self.doRAD = True
        self.doVIS = True
        self.fastVis = False
        self.fastRad = False
        self.extraSky = None

    ## Configure to compile map using extra high quality lighting
    def presetBest(self):
        self.presetNormal()
        self.extraSky = 16 #1 is normal, 16 is equal to '-final'

    ## Set map list.
    #
    #  @param mapList a list of paths to uncompiled map files. The first map in
    #  the list is the map that is loaded in the game or editor, if any.
    def setMapList(self, mapList):
        Executor.setMapList(self, mapList)
        ## list of compiled map files
        self._bspList = [x[:-3]+'bsp' for x in self._mapList]
        if not all(map(os.path.isfile, self._bspList)):
            self._bspList = [None]*len(self._mapList)

    ## Check whether an overwrite will occur when compiling or installing the
    #  level.
    #
    #  @param prefix Checks for any map beginning with this prefix
    #
    #  @return boolean True if an overwrite will occur.
    def checkOverwrite(self, prefix):
        #check install location
        listing = os.listdir(self.gamePath + '/maps/')
        listing = [x for x in listing if x.startswith(prefix)]
        return len(listing) > 0

    ## Open uncompiled map in appropriate map editor.
    #
    #  If there are multiple maps the first one will be opened.
    #
    #  @bug opening map in editor doesn't work for portal 2 (seems like hammer's failure)
    #
    def edit(self):
        if self._mapList == None or len(self._mapList) <= 0:
            raise Exception("No maps specified")
        #the SDK passes some arguments to hammer
        #we will use the same arguments, and add a vmf file for hammer to open
        command = ['"' + self._hammerPath + '/bin/hammer.exe"']
        if self._gameID == GMOD:
            command.append('-game "' + SDKUtil.findGamePath(HL2EP2) + '"')
        else:
            command.append('-game "' + self.gamePath + '"')
        command.append('-nop4')
        command.append('"' + self._mapList[0] + '"')
        command = ' '.join(command)
        command = command.replace('/', '\\') #hammer leik it backwards
        self.listenerWrite(command)
        oldworkdir = os.getcwd()
        os.chdir(self._hammerPath) #Hammer needs this working directory
        subprocess.Popen(command)
        os.chdir(oldworkdir) #restore working directory
        self.setStatus("Started Editor")

    ## Compile a set of maps.
    #
    #  The maps will be compiled and installed for the specified game, using the
    #  specified quality setting.
    def compile(self, custom = False):
        if self._mapList == None or len(self._mapList) <= 0:
            raise Exception("No maps specified")
        self._setMetaProgress(0.0, 0.1)
        self._setMetaStatus("Converting to BSP")
        self.runBSP(custom)
        if self.doVIS or custom:
            self._setMetaProgress(0.1, 0.2)
            self._setMetaStatus("Optimizing Visibility")
            self.runVIS(custom)
        if self.doRAD or custom:
            self._setMetaProgress(0.3, 0.65)
            self._setMetaStatus("Lighting")
            self.runRAD(custom)
        self._setMetaProgress(0.95, 0.05)
        self._setMetaStatus("Installing Map in Game")
        self.installMap()
        self.setProgress(1.0)
        self._setMetaStatus("Finished Compiling")
        return

    ## Set overall progress and amount of progress next subprocess represents
    def _setMetaProgress(self, progress, subweight):
        self.setProgress(progress)
        ## overall progress
        self._subProgressOffset = self.progress
        ## amount of progress next subprocess represents
        self._subProgressWeight = subweight

    ## Set overall status
    def _setMetaStatus(self, status):
        self.setStatus(status)
        ## overall status
        self._metaStatus = self.status
    
    ## Used by subprocess to indicate its own progress
    def _setSubProgress(self, progress):
        assert progress >= 0.0
        assert progress <= 1.0
        self.setProgress(self._subProgressOffset + self._subProgressWeight*progress)

    ## Used by subprocess to indicate its own status
    def _setSubStatus(self, status):
        self.setStatus(self._metaStatus+status)

    ## run a compile utility on the map with specified arguments
    #
    #  Behavior is only defined for vbsp.exe, vvis.exe, and vrad.exe
    def _runCompileUtility(self, name, arguments):
        command = ['"' + self._hammerPath + '/bin/' + name + '.exe"']
        if self.verbose:
            arguments.append('-verbose')
        if self.low:
            arguments.append('-low')
        command.extend(arguments)
        command.append('-game "' + self.gamePath + '"')
        command = [(command + ['"' + x + '"']) for x in self._mapList]
        command = [' '.join(x) for x in command]

        oldworkdir = os.getcwd()
        os.chdir(self._hammerPath) #VBSP needs this to find the materials

        result = [None]*len(command)
        for line in range(len(command)):
            self.listenerWrite(command[line]+'\n\n')
            if len(command)>1:
                self._setSubProgress(float(line)/len(command))
                self._setSubStatus(': Map ' + str(line+1) + '/' + str(len(command)))
            #change startupinfo to suppress window
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            process = subprocess.Popen(
                command[line],
                startupinfo = startupinfo,
                stderr = subprocess.STDOUT,
                stdout = subprocess.PIPE
                )
            try:
                if len(self.listeners)>0:
                    while process.poll() == None:
                        text = process.stdout.read(4)
                        if sys.version_info.major == 3:
                            text = str(text, 'ascii')
                        while text != '':
                            self.listenerWrite(text)
                            text = process.stdout.read(4)
                            if sys.version_info.major == 3:
                                text = str(text, 'ascii')
                        time.sleep(0.05) #~20fps
                else:
                    process.wait()
            except SystemExit:
                #this is raised by the GUI to abort generation/compilation
                #however, we need to stop the external process, so we catch it
                process.kill()
                print('killed external process')
                raise SystemExit() #...and then pass it along
            if process.returncode != 0:
                raise Exception(name + ' failed.')
            
        os.chdir(oldworkdir) #restore working directory

    ## run VBSP on the maps to compile them into .bsp map files
    def runBSP(self, custom = False):
        #https://developer.valvesoftware.com/wiki/VBSP
        assert len(self._mapList) == len(self._bspList)
        arguments = []
        if custom:
            arguments = [self.customBSP]
        else:
            if self.onlyEntities:
                arguments.append('-onlyents')
            if self.onlyProps:
                arguments.append('-onlyprops')
            if self.noDetail:
                arguments.append('-nodetail')
            if self.noWater:
                arguments.append('-nowater')
        self._runCompileUtility('vbsp', arguments)
        #only reaches this if no bsp exceptions (compile succeeds)
        self._bspList = [x[:-3]+'bsp' for x in self._mapList]

    ## Run VVIS on the maps to optimize visibility
    def runVIS(self, custom = False):
        #https://developer.valvesoftware.com/wiki/VVIS
        arguments = []
        if custom:
            arguments = [self.customVIS]
        else:
            if self.fastVis:
                arguments.append('-fast')
            if self.fastPortals:
                arguments.append('-nosort')
        arguments.append('-novconfig') #suppress gui on vproject errors
        self._runCompileUtility('vvis', arguments)
        
    ## Run VRAD on the maps to light them
    def runRAD(self, custom = False):
        #https://developer.valvesoftware.com/wiki/VRAD
        arguments = []
        if custom:
            arguments = [self.customRAD]
        else:
            if self.dynamicRange==1:
                arguments.append('-ldr')
            elif self.dynamicRange==2:
                arguments.append('-hdr')
            elif self.dynamicRange==3:
                arguments.append('-both')
            if self.fastRad:
                arguments.append('-fast')
            if self.extraSky != None:
                arguments.append('-extrasky ' + str(self.extraSky))
            if self.limitBounce != None:
                arguments.append('-bounce ' + str(self.limitBounce))
            if self.softSun != None:
                arguments.append('-softsun ' + str(self.softSun))
            if self.noSuperSampling:
                arguments.append('-noextra')
        self._runCompileUtility('vrad', arguments)

    ## Install maps in appropriate game directory
    #
    #  deletes .ain (node graph) file if it already exists
    #  deletes .nav (nav mesh) file if it already exists
    #
    def installMap(self):
        assert all(map(os.path.isfile, self._bspList))
        #make sure maps folder exists
        if not os.path.isdir(self.gamePath + '/maps'):
            os.mkdir(self.gamePath + '/maps')
        #copy .bsp files
        for n in range(len(self._bspList)):
            self.listenerWrite('\ncopy "' + self._bspList[n] + '" "' + self.gamePath + '"\n\n')
            shutil.copy(self._bspList[n], self.gamePath + '/maps')
            #delete .ain (node graph) file if it already exists
            ainPath = self._bspList[n].split('/')[-1][:-4] + '.ain'
            ainPath = self.gamePath + '/maps/graphs/' + ainPath
            if os.path.isfile(ainPath):
                self.listenerWrite('deleting outdated .ain file\n')
                os.remove(ainPath)
            #delete .nav (nav mesh) file if it already exists
            navPath = self._bspList[n].split('/')[-1][:-4] + '.nav'
            navPath = self.gamePath + '/maps/' + navPath
            if os.path.isfile(navPath):
                self.listenerWrite('deleting outdated .nav file\n')
                os.remove(navPath)

    ## Launch the game and load the (first) map
    #
    def launch(self, custom = False):
        #example:
        #e:\program files (x86)\steam\steam.exe -applaunch 620 -game "e:\program files (x86)\steam\steamapps\common\portal 2\portal2" +map "test"
        assert len(self._bspList) >= 1
        assert self._bspList[0] != None
        command = ['/'.join(self._basePath.split('/')[:-1]) + '/steam.exe']
        command.append('-applaunch ' + str(SDKExecutor._appIDs[self._gameID]))
        command.append('-game "' + self.gamePath + '"')
        command.append('-novid')
        if custom:
            command.append(self.customGame)
        command.append('+map "' + self._bspList[0].split('/')[-1][:-4] + '"')
        command = ' '.join(command)

        self.listenerWrite(command + '\n\n')
        subprocess.Popen(command)
        self.setStatus('Game is Launching...')
