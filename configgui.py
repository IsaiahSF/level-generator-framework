import sys
if sys.version_info.major == 2:
    #for Python 2.x
    from Tkinter import *
else:
    #for Python 3.x
    from tkinter import *

## module configuration GUI
class ConfigGUI:
    ## Constructor.
    #
    #  @param name Title of the configuration window
    #  @param parent Module to configure
    def __init__(self, name, parent):
        ## Title displayed on window
        self.name = name
        ## instance of module to configure
        self.parent = parent
        
    ## GUI to configure generator options
    #
    #  @param rootwindow Main program window
    def showGUI(self, rootwindow):
        ## Toplevel() Tkinter object for generator compilation GUI
        self.root = rootwindow
        self.window = Toplevel()
        self.window.transient(rootwindow)
        self.window.resizable(0, 0)
        self.window.title(self.name)
        self.window.protocol("WM_DELETE_WINDOW", self.closeGUI)
        self.window.bind("<Destroy>", self.destroyWindow)
        self.populateGUI() #add window contents
        #place window over parent
        self.window.geometry(
            "+%i+%i" %
            (rootwindow.winfo_rootx() + 30, rootwindow.winfo_rooty() + 30)
            )
        self.window.focus_set()
        self.window.grab_set()
        self.window.wait_window(self.window)

    ## Catches window destruction event
    def destroyWindow(self, event):
        self.closeGUI()

    ## Close the generator configuration window. Implementations may extend
    # this method to apply the GUI settings to the generator.
    def closeGUI(self):
        try:
            self.window.destroy()
        except:
            pass

    ## Populate @ref window with widgets and controls
    def populateGUI(self):
        raise NotImplementedError()

