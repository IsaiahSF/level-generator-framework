import pickle

from tkinter import *
from tkinter import ttk


class PresetModel:

    def __init__(self, string, number, strings):
        self.string = string
        self.number = number
        self.strings = strings


class PresetWindow:

    def _writeModel(self, key, value):
        self.model.__dict__[key] = value

    def __init__(self):
        self.window = Tk()
        self.window.title("Preset Test")
        self.window.protocol("WM_DELETE_WINDOW", self.closeGUI)
        self.window.bind("<Destroy>", self.destroyWindow)

        exists = True
        try:
            file = open("./default.p")
        except Exception as e:
            self.model = PresetModel("abc", 42, ["a","b","c"])
            exists = False

        if exists:
            self.loadPreset("./default.p")

        self.preset = StringVar()

        self.string = StringVar()
        self.string.trace("w", lambda name, index, mode: self._writeModel("string", self.string.get()))
        self.string.trace("r", lambda name, index, mode: self.string.set(self.model.string))

        self.number = StringVar()
        self.number.trace("w", lambda name, index, mode: self._writeModel("number", int(self.number.get())))
        self.number.trace("r", lambda name, index, mode: self.number.set(str(self.model.number)))

        row = 0

        Entry(
            self.window,
            textvariable=self.preset
            ).grid(column=0, row=row)
        row += 1

        def loadPreset(preset):
            self.loadPreset(preset)
            self.refresh()

        Button(
            self.window,
            text="Load preset",
            command=lambda: loadPreset(self.preset.get())
            ).grid(column=0, row=row)
        Button(
            self.window,
            text="Save preset",
            command=lambda: self.savePreset(self.preset.get())
            ).grid(column=1, row=row)
        
        row += 1
        
        Entry(
            self.window,
            textvariable=self.string
            ).grid(column=0, row=row)
        row += 1
        
        Entry(
            self.window,
            textvariable=self.number
            ).grid(column=0, row=row)
        row += 1

        self.window.mainloop()

    def loadPreset(self, path):
        file = open(path, "rb")
        self.model = pickle.load(file)

    def refresh(self):
        self.string.set(self.string.get())
        self.number.set(self.number.get())

    def savePreset(self, path):
        file = open(path, "wb")
        pickle.dump(self.model, file)

    def destroyWindow(self, event):
        self.closeGUI()

    def closeGUI(self):
        self.savePreset("./default.p")
        self.window.destroy()


PresetWindow()
