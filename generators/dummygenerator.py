import time, random, string, sys
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

## Dummy configuration GUI for testing and demonstration purposes
class DummyConfig(ConfigGUI):
    ## Sets up layout of configuration window
    def populateGUI(self):
        ## GUI variable for total duration in seconds.
        self.timeVar = StringVar()
        self.timeVar.set(str(self.parent.time))
        ## GUI variable for step duration, or how often to update progress.
        self.stepVar = StringVar()
        self.stepVar.set(str(self.parent.step))
        
        Label(self.window, text = "Time:").grid(
            column = 0,
            row = 0,
            sticky = E,
            padx = 5,
            pady = 5
            )
        Label(self.window, text = "Step:").grid(
            column = 0,
            row = 1,
            sticky = E,
            padx = 5,
            pady = 5
            )
        Entry(
            self.window,
            textvariable = self.timeVar,
            width = 8
            ).grid(column = 1, row = 0, sticky = W, padx = 20, pady = 5)
        Entry(
            self.window,
            textvariable = self.stepVar,
            width = 8
            ).grid(column = 1, row = 1, sticky = W, padx = 20, pady = 5)
        Button(
            self.window,
            text = "Ok",
            width = 5,
            command = self.setValues,
            padx = 50
            ).grid(column = 0, row = 2, padx = 20, pady = 5)
        Button(
            self.window,
            text = "Cancel",
            width = 5,
            command = self.window.destroy,
            padx = 50
            ).grid(column = 1, row = 2, padx = 20, pady = 5)

    ## applies configuration window settings to generator
    def setValues(self):
        try:
            time = float(self.timeVar.get())
            step = float(self.stepVar.get())
            assert time > 0
            assert step > 0
        except:
            messagebox.showerror('Error','Values must be positive numbers')
        else:
            self.parent.time = time
            self.parent.step = step
            self.closeGUI()
        

## Dummy generator for testing and demonstration purposes
class DummyGenerator1(Generator):
    ## Name
    name = "Dummy Generator"

    ## Description
    description = "This is a test generator. It doesn't do anything."

    ## Supported format
    formats = [VMF]

    ## Supported games
    games = [
        HL2,
        HL2EP2,
        HL2DM
        ]

    ## Configuration gui
    configGUI = DummyConfig

    ## Constructor
    def __init__(self, parent):
        Generator.__init__(self, parent)
        ## Seconds to pretend to generate something
        self.time = 6.0
        ## Seconds between progress updates
        self.step = 0.01

    ## Pretends to generate something. Demonstrates progress window
    def generate(self, gameID):
        self.setStatus('Pretending to Generate')
        total = int(self.time/self.step)
        for i in range(total):
            time.sleep(self.step)
            self.setProgress(float(i)/total)
            nonsense = random.choice(string.ascii_uppercase)+'ubba '
            self.listenerWrite(nonsense)
        self.setProgress(1.0)
        self.setStatus('Done Pretending')
            
