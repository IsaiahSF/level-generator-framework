import sys, math
if sys.version_info.major == 2:
    #for Python 2.x
    import tkMessageBox as messagebox
    from Tkinter import *
else:
    #for Python 3.x
    from tkinter import *
    from tkinter import messagebox

from generators.generator import Generator
from configgui import ConfigGUI
from gameids import *
from formats.vmf import VMF

## Dummy configuration GUI for testing and demonstration purposes
class RotateConfig(ConfigGUI):
    ## Sets up layout of configuration window
    def populateGUI(self):
        Label(self.window, text = "No settings.").pack()

## Dummy generator for testing and demonstration purposes
class RotateGenerator(Generator):
    ## Name
    name = "Rotation Test"

    ## Description
    description = "This tests prefab rotation."

    ## Supported format
    formats = [VMF]

    ## Supported games
    games = [
        HL2
        ]

    ## Configuration gui
    configGUI = RotateConfig

    ## Constructor
    def __init__(self, parent):
        Generator.__init__(self, parent)

    ## Pretends to generate something. Demonstrates progress window
    def generate(self, gameID):
        ## ID of game
        self.gameID = gameID
        ## high level VMFmap instance
        self.map = self.parent.getMap()
        ## low level VMF instance
        self.native = self.map.getNative()
        self.setStatus('Generating')
        self.setProgress(0.0)
        
        self.listenerWrite('Loading prefab...')
        testPrefab = VMF(self.gameID, './maps/test_prefab2.vmf')
        self.listenerWrite('  loaded.\n')
        
        self.listenerWrite('Adding prefab.\n')
        self.native.addPrefab(testPrefab)
        #z rotations
        self.listenerWrite('Testing z rotations.\n')
        for a in range(1,17):
            self.native.addPrefab(testPrefab, pos=[-a*48, 0, 0], rot=[0, 0, a*math.pi/8])
        #x rotations
        self.listenerWrite('Testing x rotations.\n')
        for a in range(1,17):
            self.native.addPrefab(testPrefab, pos=[a*48, 0, 0], rot=[a*math.pi/8, 0, 0])
        #y rotations
        self.listenerWrite('Testing y rotations.\n')
        for a in range(1,17):
            self.native.addPrefab(testPrefab, pos=[0, a*48, 0], rot=[0, a*math.pi/8, 0])
        
        
        self.listenerWrite('Saving map...')
        self.map.save()
        self.listenerWrite('  saved.\n')
        
        self.listenerWrite('Done.\n')
        self.setStatus('Done')
        self.setProgress(1.0)
            
