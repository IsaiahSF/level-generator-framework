import sys
if sys.version_info.major == 2:
    #for Python 2.x
    import tkMessageBox as messagebox
    from Tkinter import *
else:
    #for Python 3.x
    from tkinter import *
    from tkinter import messagebox
    
from configgui import ConfigGUI

## Interface for Test objects
class Test:
    ## makes a gui element representing this object as self.gui
    #
    #  @param parent GUI parent of gui element
    def makeGUI(self, parent):
        raise NotImplementedError
    def _setState(self, boolean):
        raise NotImplementedError
    def _getState(self):
        raise NotImplementedError
    ## whether this test object is enabled or not
    state = property(_getState, _setState)
    ## runs the test
    def run(self):
        raise NotImplementedError

## Group of test objects. Provides visual grouping and GUI element to enable or
#  disable all of them at the same time.
class TestCategory(Test):
    ## constructor
    #
    #  @param name name of category
    #  @param subtests list of test objects in this category
    #  @param horizontal if True, contents are arranged horizontally instead of
    #  vertically.
    def __init__(self, name, subtests, horizontal = False):
        ## name of category
        self.name = name
        ## list of test objects in this category
        self.tests = subtests
        ## gui layout
        self.horizontal = horizontal
        self._all = IntVar()
        if self.state:
            self._all.set(1)
        
    def makeGUI(self, parent):
        ## gui widget that controls the tests in this category
        self.gui = LabelFrame(parent, text=self.name)
        for i in range(len(self.tests)):
            self.tests[i].makeGUI(self.gui)
            self.tests[i].gui.grid(
                column = i*self.horizontal,
                row = i*(not self.horizontal),
                sticky = E+W,
                padx = 10
                )
        Checkbutton(
            self.gui,
            text = 'Select All',
            variable = self._all,
            command = self.setAll,
            onvalue = 1,
            offvalue = 0
            ).grid(
                column = 0,
                row = len(self.tests)*(not self.horizontal) + self.horizontal,
                sticky = W,
                padx = 0,
                pady = 5
                )

    def _setState(self, state):
        self._all.set(state)
        self.setAll()
    def _getState(self):
        return all([x.state for x in self.tests])
    state = property(_getState, _setState)

    ## updates contents to match status of 'select all' checkbox
    def setAll(self):
        state = self._all.get()
        for test in self.tests:
            test.state = state

    def run(self):
        for test in self.tests:
                 test.run()

## A test to run
class TestCase(Test):
    ## Constructor
    #
    #  @param progressSubject ProgressSubject to use to send progress info
    #  @param name name of test
    #  @param function function containing test
    #  @param enabled whether test is enabled in the GUI by default
    #
    def __init__(self, progressSubject, name, function, enabled=True):
        ## name
        self.name = name
        ## test function
        self.function = function
        ## ProgressSubject instance
        self.subject = progressSubject
        ## whether test is enabled
        self.enabled = IntVar()
        self.enabled.set(enabled)
    ## Make GUI element as self.gui
    #
    #  @param parent parent of GUI widget that is created
    #
    def makeGUI(self, parent):
        ## gui widget that controls this test
        self.gui = Checkbutton(
            parent,
            text = self.name,
            variable = self.enabled,
            onvalue = 1,
            offvalue = 0,
            anchor = W
            )
    def _setState(self, boolean):
        self.enabled.set(boolean)
    def _getState(self):
        return self.enabled.get()
    ## Whether the test is enabled, 1 or 0.
    state = property(_getState, _setState)
    ## runs the test and provides some progress updates
    def run(self):
        if self.enabled.get() == 1:
            self.subject.setStatus(self.name)
            self.subject.listenerWrite('Testing ' + self.name + '\n')
            self.function()

## GUI to set what tests to run
class TestConfig(ConfigGUI):

    ## Set up layout of configuration window
    def populateGUI(self):
        self.parent.tests.makeGUI(self.window)
        self.parent.tests.gui.pack()
