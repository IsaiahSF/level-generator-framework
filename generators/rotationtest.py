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
        testPrefab = VMF(self.gameID, './generators/rotationtestPrefab.vmf')
        self.listenerWrite('  loaded.\n')
                
        self.listenerWrite('Testing rotations...')
        spacing = 96
        size = 8
        for x in range(0, size+1):
            self.setProgress(x/float(size))
            for y in range(0, size+1):
                for z in range(0, size+1):
                    self.native.addPrefab(testPrefab, pos=[spacing*x, spacing*y, spacing*z], rot=[x*math.pi*2.0/size, y*math.pi*2.0/size, z*math.pi*2.0/size])
        self.listenerWrite('  tested.\n')
        
        self.listenerWrite('Saving map...')
        self.map.save()
        self.listenerWrite('  saved.\n')
        
        self.listenerWrite('Done.\n')
        self.setStatus('Done')
        self.setProgress(1.0)
            
