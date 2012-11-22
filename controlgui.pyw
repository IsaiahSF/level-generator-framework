import os, inspect, threading, traceback, sys, time, imp

#Note that the only officially supported version of Python is 3
print("python version " + str(sys.version_info))
if sys.version_info[0] == 2:
    #for Python 2.x
    from Tkinter import *
    import tkMessageBox as messagebox
    import ttk #more widgets, including progress bar
else:
    #for Python 3.x
    from tkinter import *
    from tkinter import ttk
    from tkinter import messagebox

#interfaces
import formats
import generators
import progressobserver
#constants
from gameids import *

# main page of Doxygen documentation
## @mainpage
#
#  For methods that can be used with any game or format, see the
#  @link formats::map::Map Map @endlink interface.
#
#  @section common_classes Native VMF Module
#  @li @link formats::vmf::VMF VMF @endlink
#  @li @link formats::vmf::Solid Solid @endlink
#  @li @link formats::vmf::Side Side @endlink
#  @li @link formats::vmf::Matrix Matrix @endlink
#
#  @section class_diagram UML Class Diagram
#  @image html "LGF Class Diagram.png"
#

## The main GUI
class ControlGUI:

    ## Where to store generated levels
    mapLocation = os.path.abspath('./maps')

    ## Constructor.
    #
    #  Defines layout of main GUI. Creates the root GUI window and then runs it.
    def __init__(self):
        ## LGF toplevel window
        self.window = Tk()
        self.window.resizable(0, 0) #cannot be resized
        self.window.title("LGF")
        ## worker thread
        self.thread = None
        ## GUI window for displaying information about the generation and
        #  compilation process
        self.progressGUI = None

        #load modules
        ## set of all currently loaded modules
        self.loadedModules = set()
        self.reloadModules()
        
        #gui variable objects
        ## Value of GUI generator selection menu
        self.generatorSelect = StringVar()
        self.generatorSelect.trace('w', self.generatorSelectUpdate)
        ## Value of GUI game selection menu
        self.gameSelect = StringVar()
        self.gameSelect.trace('w', self.gameSelectUpdate)
        ## Value of GUI name prefix text box
        self.nameSelect = StringVar()
        self.nameSelect.trace('w', self._validateMapName)
        ## Value of GUI compile quality control
        self.compileQuality = IntVar()
        ## Value of "Run Game" GUI control
        self.runGame = IntVar()
        ## Value of "Launch Editor" GUI control
        self.runEditor = IntVar()

        #generator and game selection section
        generatorFrame = Frame(
            self.window,
            padx = 6,
            pady = 6,
            relief = RAISED,
            borderwidth = 1)
        Label(generatorFrame, text = "Generator:").grid(
            column = 0,
            row = 0,
            sticky = E)
        Label(generatorFrame, text = "Game:").grid(
            column = 0,
            row = 1,
            sticky = E)
        Label(generatorFrame, text = "Map Name:").grid(
            column = 0,
            row = 2,
            sticky = E)
        ## error message in gui
        self.errorLabel = StringVar()
        self.errorLabel.set('')
        Label(generatorFrame, fg='red', textvariable = self.errorLabel).grid(
            column = 1,
            row = 3,
            sticky = E + W)
        ## generator selection menu widget
        self.generatorSelector = OptionMenu(
            generatorFrame,
            self.generatorSelect,
            'no modules'
            )
        ## game selection menu widget
        self.gameSelector = OptionMenu(
            generatorFrame,
            self.gameSelect,
            'no games'
            )
        self.generatorSelector.configure(anchor = W)
        self.gameSelector.configure(anchor = W)
        self.generatorSelector.grid(column = 1, row = 0, sticky = W, pady = 3)
        self.gameSelector.grid(column = 1, row = 1, sticky = W, pady = 3)
        ## name prefix for map files
        self.mapName = Entry(
            generatorFrame,
            textvariable = self.nameSelect
            )
        self.mapName.grid(column = 1, row = 2, sticky = W, pady = 5, padx = 3)
        Button(
            generatorFrame,
            text = "Settings...",
            width = 8,
            command = self.configureGenerator
            ).grid(column = 2, row = 0, padx = 10)
        Button(
            generatorFrame,
            text = "Reload\nModules",
            width = 8,
            command = self.refreshModules
            ).grid(column = 2, row = 1, rowspan = 2, padx = 10)

        #compile quality selection section
        compileFrame = Frame(
            self.window,
            pady = 9,
            padx = 9,
            relief = RAISED,
            borderwidth = 1)
        qualityRadio0 = Radiobutton(
            compileFrame,
            text = "Bare",
            variable = self.compileQuality,
            value = 0
            )
        qualityRadio1 = Radiobutton(
            compileFrame,
            text = "Fast",
            variable = self.compileQuality,
            value = 1
            )
        qualityRadio2 = Radiobutton(
            compileFrame,
            text = "Normal",
            variable = self.compileQuality,
            value = 2
            )
        qualityRadio3 = Radiobutton(
            compileFrame,
            text = "Full",
            variable = self.compileQuality,
            value = 3
            )
        qualityRadio4 = Radiobutton(
            compileFrame,
            text = "Custom",
            variable = self.compileQuality,
            value = 4
            )
        qualityLabel1 = Label(compileFrame, text = "Speed")
        qualityLabel2 = Label(compileFrame, text = "Quality")
        qualityButton = Button(
            compileFrame,
            text = "Configure...",
            command = self.customCompile,
            padx = 5
            )
        #create double ended arrow on canvas
        qualityCanvas = Canvas(compileFrame, height = 50, width = 10)
        qualityCanvas.create_line(5,0,5,50, arrow = 'both')
        qualityRadio0.grid(column = 0, row = 0, sticky = W)
        qualityRadio1.grid(column = 0, row = 1, sticky = W)
        qualityRadio2.grid(column = 0, row = 2, sticky = W)
        qualityRadio3.grid(column = 0, row = 3, sticky = W)
        qualityRadio4.grid(column = 0, row = 4, sticky = W)
        qualityLabel1.grid(column = 1, row = 0)
        qualityCanvas.grid(column = 1, row = 1, rowspan = 2)
        qualityLabel2.grid(column = 1, row = 3)
        qualityButton.grid(column = 1, row = 4)

        #section that contains options to launch game and/or editor
        optionFrame = Frame(
            self.window,
            padx = 24,
            pady = 18,
            relief = RAISED,
            borderwidth = 1)
        optionEditor = Checkbutton(
            optionFrame,
            text = "Launch Editor",
            variable = self.runEditor,
            command = self.toggleCompile,
            )
        optionGame = Checkbutton(
            optionFrame,
            text = "Run Game",
            variable = self.runGame
            )
        optionEditor.grid(column = 0, row = 0, sticky = W)
        optionGame.grid(column = 0, row = 1, sticky = W)

        #section that has Start button
        buttonFrame = Frame(
            self.window,
            height = 45,
            relief = RAISED,
            borderwidth = 1)
        Button(
            buttonFrame,
            text = "START",
            command = self.start,
            font = ("Arial", "12"), #slightly larger
            default = ACTIVE,
            padx = 15,
            pady = 3,
            ).place(relx = 0.5, rely = 0.5, anchor = CENTER)
        
        #lay out frames
        generatorFrame.grid(
            column = 0,
            row = 0,
            columnspan = 2,
            sticky = N+S+E+W
            )
        compileFrame.grid(column = 0, row = 1, rowspan = 2, sticky = N+S+E+W)
        optionFrame.grid(column = 1, row = 1, sticky = N+S+E+W)
        buttonFrame.grid(column = 1, row = 2, sticky = N+S+E+W, ipady = 10)

        ## list of GUI elements disabled by the "Launch Editor" option
        self.compileElements = [
            qualityRadio0,
            qualityRadio1,
            qualityRadio2,
            qualityRadio3,
            qualityRadio4,
            qualityButton,
            optionGame
            ]

        #update GUI elements that depend on what modules are loaded
        self.updateGUIModules()

        #run GUI
        #blocks until it is closed
        self.window.mainloop()

    def _updateOptionMenuContents(self, widget, contents):
        widget['menu'].delete(0, END)
        for item in contents:
            widget['menu'].add_command(
                label = item,
                command = lambda temp = item: widget.setvar(widget.cget("textvariable"), value = temp)
                )

    def _validateMapName(self, *args):
        prefix = self.nameSelect.get()
        #check for overwrite at map storage location
        if not os.path.isdir('./maps'):
            os.mkdir('./maps')
        listing = os.listdir('./maps')
        listing = [x for x in listing if x.startswith(prefix)]
        #check for overwrite at map installation location
        installCheck = self.selectedExecutor.checkOverwrite(prefix)
        if len(listing) > 0 or installCheck:
            self.errorLabel.set('Map files may be overwritten!')
        else:
            self.errorLabel.set('')

    ## Updates GUI in response to changes in loaded modules
    def updateGUIModules(self):
        #update lists of options
        ## list of Generator names. Used in GUI.
        self.generatorList = list(self.generators.keys())
        self.generatorList.sort()
        ## list of game names. Used in GUI.
        self.gameList = []
        for executor in self.executors.values():
            self.gameList.extend(executor.usableGames())
        self.gameList.sort()
        #update contents of drop-down menus
        self._updateOptionMenuContents(self.generatorSelector, self.generatorList)
        self._updateOptionMenuContents(self.gameSelector, self.gameList)
        #update width of GUI elements
        width = max(map(len, self.generatorList + self.gameList))
        self.generatorSelector['width'] = width
        self.gameSelector['width'] = width
        self.mapName['width'] = width + 6
        #update selections in drop-down menus
        if not self.generatorSelect.get() in self.generatorList:
            self.generatorSelect.set(self.generatorList[0])
        if not self.gameSelect.get() in self.gameList:
            self.gameSelect.set(self.gameList[0])
        #trigger other updates to ensure valid state
        self.generatorSelectUpdate()
        self.gameSelectUpdate()

    ## Updates internal Executor format module depending on game selection
    def gameSelectUpdate(self, *args):
        selection = self.gameSelect.get()
        mapFormat = getGameFormat(selection)
        ## determine the correct instance of executor appropriate for game
        #  selected in menu. Used to configure custom compilation.
        try:
            self.selectedExecutor = self.executors[mapFormat](selection)
        except Exception as e:
            msg = 'Unable to init ' + str(mapFormat) + ' executor\n\n'
            msg = msg + traceback.format_exc()
            ErrorFatal(msg, self.window.destroy)

    ## Disables game menu entries not supported by current generator and
    #  forces to supported game. Also creates an instance of the generator so
    #  it can be configured. OptionMenu command.
    def generatorSelectUpdate(self, *args):
        selection = self.generatorSelect.get()
        ## instance of generator selected in menu. Used to configure generator.
        self.selectedGenerator = self.generators[selection](self)
        #get list of games the generator supports
        supported = self.generators[selection].games
        assert type(supported) in (list, tuple)
        assert len(supported) >= 1 #must support at least one game
        #if selection must be forced, it is changed to default
        default = None
        for i in range(len(self.gameList)): #for each game in the menu
            #if the game is in the supported list make it enabled,
            #otherwise disabled
            state = None
            if self.gameList[i] in supported:
                state = NORMAL #(enabled)
                #default will end up being the first valid option
                if default == None:
                    default = i
            else:
                state = DISABLED
            #set state (enabled/disabled) of the menu item
            self.gameSelector['menu'].entryconfigure(i, state = state)
        #if current selection not in list of supported games
        if self.gameSelect.get() not in supported:
            #set the selection to the default value
            self.gameSelect.set(self.gameList[default])

    ## Disables compilation and game running controls if the "launch editor"
    #  checkbox is selected. Checkbutton command.
    def toggleCompile(self):
        editor = self.runEditor.get()
        state = None
        if editor == 1:
            state = DISABLED
        else:
            state = NORMAL
        for element in self.compileElements:
            element.configure(state = state)

    ## Action for 'Refresh Modules' button. Reloads interfaces and modules, then updates GUI accordingly.
    def refreshModules(self):
        self.reloadModules()
        self.updateGUIModules()

    ## Display controls to set custom compilation options. Connected to "Set"
    #  button.
    def customCompile(self):
        self.selectedExecutor.showGUI(self.window)

    ## Display generator's configuration gui. Connected to "Settings" button.
    def configureGenerator(self):
        self.selectedGenerator.showGUI(self.window)

    ## Generate maps, then either launch editor or compile maps and optionally
    #  launch the chosen game. Connected to "START" button.
    def start(self):
        #verify gui input
        prefix = self.nameSelect.get()
        if not prefix.isalnum() or len(prefix)<1:
            messagebox.showerror(
                'Invalid Input',
                'Invalid Map Name',
                icon = messagebox.ERROR,
                parent = self.window
                )
            return
        ## list of map files generated.
        self.mapFiles = []
        self.thread = threading.Thread(target = self.run)
        #Create progress GUI and attach as listener
        self.progressGUI = ProgressGUI(self.window, self.thread)
        self.selectedExecutor.addListener(self.progressGUI)
        self.selectedGenerator.addListener(self.progressGUI)
        ## Exception that happened in worker thread. Value is None if no
        #  exceptions occur.
        self.runException = None
        ## Text traceback for exception that happens in thread. Value is None
        #  if no exceptions occur.
        self.runTraceback = None
        time.sleep(0.05) #wait for tkinter to show progress GUI
        self.thread.start()
        self.updateProgress() #start update loop

    ## Update loop that runs while generator and executor work
    def updateProgress(self):
        self.progressGUI.update()
        if self.thread.isAlive():
            self.window.after(25, self.updateProgress)
        else:
            #self.progressGUI.closeGUI() #close window when done
            if self.runException != None:
                #handle thread exceptions
                self.progressGUI.setStatus('Error')
                self.progressGUI.write('\n\n')
                self.progressGUI.write(self.runTraceback)
                self.progressGUI.update()
                

    ## Runs Generator and optionally launches editor, compiles, and launches
    #  the game. This method is called by a worker thread. It assumes member
    #  variables will not be changed because progress window has focus.
    #  (Otherwise it is not thread safe!)
    #
    def run(self):
        #run generator
        try:
            self.selectedGenerator.generate(self.gameSelect.get())
        except Exception as e:
            self.runException = e
            self.runTraceback = traceback.format_exc()
            return
        self.progressGUI.write('\n\n')
        #set maps to compile
        self.selectedExecutor.setMapList(self.mapFiles)
        if self.runEditor.get() == 1:
            try:
                self.selectedExecutor.edit() #open editor
            except Exception as e:
                self.runException = e
                self.runTraceback = traceback.format_exc()
                return
        else:
            #set compilation quality settings
            quality = self.compileQuality.get()
            custom = False
            if quality == 4: #custom arguments
                custom = True
            else:
                self.selectedExecutor.setQuality(quality)
            try:
                self.selectedExecutor.compile(custom) #compile
            except Exception as e:
                self.runException = e
                self.runTraceback = traceback.format_exc()
                return
            if self.runGame.get() == 1:
                self.progressGUI.write('\n\n')
                try:
                    self.selectedExecutor.launch(custom) #run game
                except Exception as e:
                    self.runException = e
                    self.runTraceback = traceback.format_exc()
                    return


    ## Load or reload map, executor, and generator modules. Should be resiliant
    #  against syntax errors in modules, new modules, missing modules, and changed
    #  modules.
    #
    #  @n  Updates:
    #  @li self.executors
    #  @li self.maps
    #  @li self.generators
    #
    def reloadModules(self):
        #get rid of instances
        try:
            del self.selectedExecutor
        except:
            pass
        try:
            del self.selectedGenerator
        except:
            pass
        #load/reload interfaces
        for interface in ['formats.executor', 'formats.map', 'generators.generator']:
            if not interface in self.loadedModules:
                try:
                    exec('import ' + interface)
                except Exception as e:
                    msg = 'Unable to load interface ' + interface + '!\n\n'
                    msg = msg + traceback.format_exc()
                    ErrorFatal(msg, self.window.destroy)
                self.loadedModules.add(interface)
            else:
                try:
                    imp.reload(eval(interface))
                except Exception as e:
                    msg = 'Unable to load interface ' + interface + '!\n\n'
                    msg = msg + traceback.format_exc()
                    ErrorFatal(msg, self.window.destroy)
        #load/reload modules
        formatModules = self._loadModules(
            'formats',
            ['__init__.py', 'executor.py', 'map.py']
            )
        generatorModules = self._loadModules(
            'generators',
            ['__init__.py', 'generator.py']
            )
        #recompose module lists
        ## loaded executor modules
        self.executors = {}
        ## loaded map modules
        self.maps = {}
        ## loaded generator modules
        self.generators = {}
        for executor in self._findImplementors(formatModules, formats.executor.Executor):
            requirements = executor.checkReq()
            if requirements == None or len(requirements) == 0:
                self.executors[executor.mapFormat] = executor
            else:
                ErrorWarning('Unable to load ' + executor.mapFormat + ' executor.\n\n' + '\n'.join(requirements))
        for item in self._findImplementors(formatModules, formats.map.Map):
            self.maps[item.mapFormat] = item
        for generator in self._findImplementors(generatorModules, generators.generator.Generator):
            if not all([
                type(generator.name) == str,
                type(generator.description) == str,
                type(generator.formats) in (list,tuple),
                type(generator.games) in (list,tuple)
                ]):
                ErrorWarning('Invalid generator: ' + generator.name)
            else:
                self.generators[generator.name] = generator
        #eliminate incomplete executor-map pairings
        for fmt in (set(self.executors.keys()) - set(self.maps.keys())):
            del self.executors[fmt]
        for fmt in (set(self.maps.keys()) - set(self.executors.keys())):
            del self.maps[fmt]
        #make sure we have at least some modules to work with
        if len(self.executors)==0:
            ErrorFatal("No format modules.", self.window.destroy)
        if len(self.generators)==0:
            ErrorFatal("No generator modules.", self.window.destroy)

    ## Finds and loads modules in given directory
    #
    #  @param folder name of folder to search for modules. Doesn't support more
    #  than a depth of 1.
    #  @param exclude list of file names to exclude, such as __init__.py and the
    #  interface module.
    #
    #  @return list of classes that subclass specified interface
    def _loadModules(self, folder, exclude):
        result = []
        assert os.path.isdir('./' + folder)
        listing = os.listdir('./' + folder)
        listing = filter(lambda x: x.endswith('.py'), listing) #only .py files
        listing = list(set(listing) - set(exclude)) #apply exclusion list
        listing = map(lambda x: x[:-3], listing) #remove extensions
        for item in listing:
            modulename = folder + '.' + item
            if not modulename in self.loadedModules:
                #loading module for the first time
                try:
                    exec('import ' + modulename) #import module
                except ImportError as e:
                    #import errors usually result from missing library
                    #do not result in a loaded module, so don't add to list
                    ErrorWarning('unable to load ' + modulename + \
                                 '\n\n' + traceback.format_exc())
                except Exception as e:
                    #other exceptions while loading seem to result in a loaded
                    #module of some kind - add to list
                    ErrorWarning('unable to load ' + modulename + \
                                 '\n\n' + traceback.format_exc())
                    self.loadedModules.add(modulename)
                else:
                    result.append(eval(modulename))
                    self.loadedModules.add(modulename)
            else:
                #reloading the module
                try:
                    exec('imp.reload(' + modulename + ')') #reload module
                except Exception as e:
                    ErrorWarning('unable to reload ' + modulename + \
                                 '\n\n' + traceback.format_exc())
                else:
                    result.append(eval(modulename))
        return result

    ## Finds classes implementing a given interface
    #
    #  @param modules list of module names to search
    #  @param interface Interface class
    #
    def _findImplementors(self, modules, interface):
        result = []
        for modulename in modules:
            #find classes implementing interface and add to list
            members = inspect.getmembers(modulename) #all members of module
            members = [x[1] for x in members] #the member itself (cut out name)
            members = filter(inspect.isclass, members) #only classes
            for i in members:
                if issubclass(i, interface) and not i == interface:
                    result.append(i)
        return result

    ## Return an open map object appropriate for the current game selected
    #
    #  The file name is already determined as
    #  (ControlGUI.mapLocation)(prefix)(number).(format)
    #  (prefix) is selected by the user in the gui.
    #  (number) is an integer that increments with each map request. reset each
    #  time the generator is run.
    #  (format) is determined by getGameFormat() from gameids.py
    #  This method also makes a list of the maps to compile when generator has
    #  finished. The first map requested by the generator is the map to be
    #  loaded in the editor or game.
    def getMap(self):
        #determine name of new file
        game = self.gameSelect.get()
        extension = getGameFormat(game)
        path = ControlGUI.mapLocation + '/' + self.nameSelect.get()
        path = path + str(1 + len(self.mapFiles)) #add number
        path = path + '.' + extension #add format extension
        self.mapFiles.append(path)
        return self.maps[extension](path, game)

## Thread safe implementation of ProgressObserver. Displays progress in a
#  Toplevel window.
class ProgressGUI(progressobserver.ProgressObserver):
    ## Constructor
    def __init__(self, rootwindow, thread):
        ## Thread that executes process
        self.thread = thread
        ## Float progress value between 0.0 and 1.0 inclusive
        self.progress = 0.0
        ## Brief human-readable status string
        self.status = ''
        ## Contains text to update the console output widget
        self.consoleBuffer = ''
        ## Lock for accessing @ref progress
        self.progressLock = threading.Lock()
        ## Lock for accessing @ref status
        self.statusLock = threading.Lock()
        ## Lock for accessing @ref consoleBuffer
        self.bufferLock = threading.Lock()
        ## Displayed status message
        self.displayedStatus = StringVar()
        self.displayedStatus.set('Pondering')
        ## Displayed progress value
        self.displayedProgress = IntVar()
        self.displayedProgress.set(0)

        ## Toplevel window for progress information
        self.window = Toplevel()
        self.window.transient(rootwindow)
        self.window.resizable(0,0)
        self.window.protocol("WM_DELETE_WINDOW", self.closeGUI)
        self.window.bind("<Destroy>", self.destroyWindow)
        #place window over parent
        self.window.geometry(
            "+%i+%i" %
            (rootwindow.winfo_rootx() + 30, rootwindow.winfo_rooty() + 30)
            )
        self.window.focus_set()
        self.window.grab_set()

        #GUI widgets
        statusWidget = Label(self.window, textvariable = self.displayedStatus)
        progressWidget = ttk.Progressbar(
            self.window,
            orient = 'horizontal',
            mode = 'determinate',
            variable = self.displayedProgress
            )
        ## Text box to display console output
        self.consoleWidget = Text(self.window, wrap = CHAR)
        scrollbar = Scrollbar(self.window)
        self.consoleWidget.config(state=DISABLED)
        self.consoleWidget.config(yscrollcommand = scrollbar.set)
        scrollbar.config(command = self.consoleWidget.yview)

        #GUI layout
        statusWidget.grid(column = 0, columnspan = 2, row = 0)
        progressWidget.grid(
            column = 0,
            columnspan = 2,
            row = 1,
            padx = 20,
            pady = 10,
            sticky = E + W)
        self.consoleWidget.grid(column = 0, row = 2)
        scrollbar.grid(column = 1, row = 2, sticky = N + S)

    ## Catches window destruction event
    def destroyWindow(self, event):
        self.closeGUI()

    ## Close the window
    def closeGUI(self):
        #ignore if thread is still running
        if self.thread.isAlive():
            return
        try:
            self.window.destroy()
        except:
            pass

    ## Update the GUI. Must be called regularly to keep GUI up to date.
    def update(self):
        #update status
        self.statusLock.acquire(True) #True means block until acquired
        self.displayedStatus.set(self.status)
        self.statusLock.release()
        #update progress bar
        self.progressLock.acquire(True)
        self.displayedProgress.set(int(self.progress*100))
        self.progressLock.release()
        #update console
        self.bufferLock.acquire(True)
        self.consoleWidget.configure(state = NORMAL)
        self.consoleWidget.insert(END, self.consoleBuffer)
        self.consoleWidget.configure(state = DISABLED)
        self.consoleBuffer = ''
        self.bufferLock.release()
        #scroll console to bottom
        self.consoleWidget.yview('moveto','1.0')

    ## Console output gets directed here
    #
    #  Behaves like stdout, no newlines are inserted.
    #
    #  @param string data to write to simulated console
    def write(self, string):
        self.bufferLock.acquire(True)
        self.consoleBuffer = self.consoleBuffer + string
        self.bufferLock.release()

    ## Thread safe method. Sets overall progress metric.
    #
    #  @param progress Float between 0.0 and 1.0 inclusive
    def setProgress(self, progress):
        assert type(progress) == float
        assert progress >= 0.0
        assert progress <= 1.0
        self.progressLock.acquire(True)
        self.progress = progress
        self.progressLock.release()
        
    ## Thread safe method. Sets overall status message.
    #
    #  @param status Brief human-readable status string
    def setStatus(self, status):
        self.statusLock.acquire(True)
        self.status = status
        self.statusLock.release()

## Alert the user to an error that occured, but that isn't a show-stopper
class ErrorWarning:
    ## constructor
    #
    #  @param message error message to display
    def __init__(self, message):
        messagebox.showinfo(
            icon = 'warning',
            message = message
            )

## Tell the user that something has gone dreadfully wrong
class ErrorFatal:
    ## constructor
    #
    #  @param message error message to display
    def __init__(self, message, destructor=None):
        messagebox.showinfo(
            icon = 'error',
            message = 'Fatal: '+message)
        #self destruct!
        if destructor:
            destructor()
        sys.exit('fatal error occured')

if __name__ == "__main__":
    ControlGUI()
