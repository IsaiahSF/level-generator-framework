import sys, os, random, time, pygame, numpy, math
if sys.version_info.major == 2:
    #for Python 2.x
    import tkMessageBox as messagebox
    from Tkinter import *
else:
    #for Python 3.x
    from tkinter import *
    from tkinter import messagebox
    import tkinter.filedialog
    import tkinter.ttk

from generators.generator import Generator
from configgui import ConfigGUI
from gameids import *
from formats.vmf import *

## GUI to set what tests to run
class HeightMapConfig(ConfigGUI):

    def write(self, name, value):
        self.parent.__dict__[name] = value

    ## Set up layout of configuration window
    def populateGUI(self):
        #try:
        #    import pickle
        #    file = open("C:/Users/Zay/Desktop/dump.p","rb")
        #    self.parent = pickle.load(file)
        #except Exception as e:
        #    print(e)
        
        # Prop list
        self.props = []
        self.layerPaths = {}
        
        # Variables
        self.size = IntVar()
        #self.size.trace("w", lambda name, index, mode: self.write("size", self.size.get()))
        #self.size.trace("r", lambda name, index, mode: self.size.set(self.parent.size))
        #self.size.set(16384)
        self.heightMap = StringVar()
        #self.heightMap.trace("w", lambda name, index, mode: self.write("heightMap", self.heightMap.get()))
        #self.heightMap.trace("r", lambda name, index, mode: self.heightMap.set(self.parent.heightMap))
        
        self.alpha = StringVar()
        self.alpha.set("<constant>")
        self.alpha.trace("w", self.setAlpha)
        self.alphaConstant = IntVar()
        self.alphaConstant.set(0)
        self.material = StringVar()
        #self.material.trace("w", lambda name, index, mode: self.write("material", self.material.get()))
        #self.material.trace("r", lambda name, index, mode: self.material.set(self.parent.material))
        self.material.set("dev/dev_blendmeasure2")
        self.maxHeight = IntVar()
        self.maxHeight.set(1024)
        self.skyHeight = IntVar()
        self.skyHeight.set(1024)
        self.waterEnabled = BooleanVar()
        self.waterMaterial = StringVar()
        self.waterMaterial.set("dev/dev_water2")
        self.waterHeight = IntVar()
        
        style = {"padx":6, "pady":2}
        
        
        # Entry frame
        entryFrame = Frame(
            self.window,
            relief = RAISED,
            borderwidth = 1,
            padx=6,
            pady=6
            )
        entryFrame.grid(column=0, row=0, rowspan=2, sticky=W+E+N+S)
        
        row = 0     

        # size
        Label(entryFrame, text="Size:").grid(
            column=0,
            row=row,
            **style)

        Entry(entryFrame, textvariable=self.size, width=6).grid(
            column=1,
            row=row,
            **style
            )

        Scale(
            entryFrame, from_=0, to=32768,
            variable=self.size, orient=HORIZONTAL,
            length=200, showvalue=0,
            command=lambda args: self.scaleCheck(self.size, 1024),
            ).grid(column=2, row=row, columnspan=2, **style)

        row += 1

        # heightmap
        Label(entryFrame, text="Heightmap:").grid(
            column=0,
            row=row,
            **style)

        self.heightMapCombo = tkinter.ttk.Combobox(
            entryFrame,
            textvariable=self.heightMap
            )
        self.heightMapCombo.grid(column=1, row=row, columnspan=3, sticky="we", **style)

        row += 1

        # alpha
        Label(entryFrame, text="Alpha:").grid(
            column=0,
            row=row,
            **style
            )

        self.alphaCombo = tkinter.ttk.Combobox(
            entryFrame,
            textvariable=self.alpha,
            values="<constant>"
            )
        self.alphaCombo.grid(column=1, row=row, columnspan=2, sticky="we", **style)
        
        self.alphaEntry = Entry(entryFrame, textvariable=self.alphaConstant, width=6)
        self.alphaEntry.grid(
            column=3,
            row=row,
            sticky="we",
            **style
            )

        row += 1

        # material
        Label(entryFrame, text="Material:").grid(
            column=0,
            row=row,
            **style
            )

        #Entry(entryFrame, textvariable=self.material).grid(
        #    column=1,
        #    row=row,
        #    columnspan=3,
        #    sticky="we",
        #    **style
        #    )
        materials = ["dev/dev_blendmeasure2"]
        #if self.parent.gameid == HL2EP2:
        materials.append("nature/blenddirtgrass001a")
        materials.append("nature/blenddirtrock_mine01b")
        materials.append("nature/blendgrassdirt001a")
        
        tkinter.ttk.Combobox(entryFrame, textvariable=self.material, values=tuple(materials)).grid(
            column=1,
            row=row,
            columnspan=3,
            sticky="we",
            **style
            )


        row += 1

        # max height
        Label(entryFrame, text="Max height:").grid(
            column=0,
            row=row,
            **style
            )

        Entry(entryFrame, textvariable=self.maxHeight, width=6).grid(
            column=1,
            row=row,
            **style
            )
        
        Scale(
            entryFrame, from_=0, to=32768,
            variable=self.maxHeight, orient=HORIZONTAL,
            length=200, showvalue=0,
            command=lambda args: self.scaleCheck(self.maxHeight, 1024)
            ).grid(column=2, row=row, columnspan=2, **style)

        row += 1

        # Sky height
        Label(entryFrame, text="Sky height:").grid(
            column=0,
            row=row,
            **style
            )

        Entry(entryFrame, textvariable=self.skyHeight, width=6).grid(
            column=1,
            row=row,
            **style
            )
        
        Scale(
            entryFrame, from_=0, to=32768,
            variable=self.skyHeight, orient=HORIZONTAL,
            length=200, showvalue=0,
            command=lambda args: self.scaleCheck(self.skyHeight, 1024)
            ).grid(column=2, row=row, columnspan=2, **style)

        row += 1

        # Water
        Label(entryFrame, text="Add water:").grid(
            column=0,
            row=row,
            **style
            )

        Checkbutton(
            entryFrame, variable=self.waterEnabled,
            command=self.setWaterEnabled).grid(column=1, row=row, sticky=W, **style)

        row += 1

        # water material
        Label(entryFrame, text="Water material:").grid(
            column=0,
            row=row,
            **style
            )

        self.waterMaterialEntry = Entry(entryFrame, textvariable=self.waterMaterial, state=DISABLED)
        self.waterMaterialEntry.grid(
            column=1,
            row=row,
            columnspan=3,
            sticky=W+E,
            **style
            )

        row += 1

        # water height
        Label(entryFrame, text="Water height:").grid(
            column=0,
            row=row,
            **style
            )

        self.waterHeightEntry = Entry(entryFrame, textvariable=self.waterHeight, state=DISABLED)
        self.waterHeightEntry.grid(
            column=1,
            row=row,
            columnspan=3,
            sticky=W+E,
            **style
            )

        row += 1
        
        
        # Layer frame       
        layerFrame = Frame(
            self.window,
            padx = 6,
            pady = 6,
            relief = RAISED,
            borderwidth = 1
            )
        layerFrame.grid(column=1, row=0, sticky=W+E+N+S)
        
        row = 0
        
        # layer list
        self.layerList = Listbox(
            layerFrame,
            height=5
            )
        self.layerList.grid(
            column=0, row=row, sticky=W+E, columnspan=2)
        
        row += 1

        # layer controls
        Button(
            layerFrame,
            text = "Add layer",
            command = self.addLayer
            ).grid(column=0, row=row, **style)

        Button(
            layerFrame,
            text = "Remove layer",
            command = self.removeLayer
            ).grid(column=1, row=row, **style)

        row += 1

        # Prop list frame
        propFrame = Frame(
            self.window,
            padx = 6,
            pady = 6,
            relief = RAISED,
            borderwidth = 1
            )
        propFrame.grid(column=1, row=1, sticky=W+E+N+S)
        
        row = 0

        # prop list        
        self.propList = Listbox(
            propFrame,
            height=5
            )
        self.propList.grid(
            column=0, row=row,
            columnspan=2, sticky=W+E)

        row += 1

        # add prop button
        Button(
            propFrame,
            text = "Add prop",
            command = self.addProp,
            ).grid(column=0, row=row, **style)
        
        # remove prop button
        Button(
            propFrame,
            text = "Remove prop",
            command = self.addProp,
            ).grid(column=1, row=row, **style)

        row += 1
        
        # Dialog control frame
        controlFrame = Frame(
            self.window,
            padx = 6,
            pady = 6,
            relief = RAISED,
            borderwidth = 1
            )
        controlFrame.grid(column=0, row=2, columnspan=3, sticky=W+E+N+S)
        
        # control buttons
        Button(
            controlFrame,
            text = "Ok",
            width = 2,
            command = self.setValues,
            padx = 10
            ).grid(column=0, row=row, padx=10, pady=5)
        Button(
            controlFrame,
            text = "Cancel",
            width = 2,
            command = self.closeGUI,
            padx = 10
            ).grid(column=1, row=row, padx=10, pady=5)

        row += 1
        
    def scaleCheck(self, variable, increment):
        variable.set(increment*(round(variable.get()/increment)))

    ## @bug file dialog isn't completely modal
    def addLayer(self):
        layerPath = tkinter.filedialog.askopenfilename(
            parent=self.root,
            filetypes=[("Bitmaps", ".bmp")]
            )
        if len(layerPath) > 0:
            base = os.path.splitext(os.path.basename(layerPath))[0]
            if not base in self.layerPaths.keys():
                self.layerList.insert(END, base)
                self.heightMapCombo["values"] = self.layerList.get(0, END)
                self.alphaCombo["values"] = ("<constant>", ) + self.layerList.get(0, END)
            self.layerPaths[base] = layerPath

    def removeLayer(self):
        selection = self.layerList.curselection()
        if len(selection) > 0:
            selectionStr = self.layerList.get(self.layerList.curselection())
            
            del self.layerPaths[selectionStr]
            
            self.layerList.delete(selection)
            if self.heightMapCombo.get() == selectionStr:
                self.heightMapCombo.set("")
            elif self.alphaCombo.get() == selectionStr:
                self.alphaCombo.set("")

            self.heightMapCombo["values"] = self.layerList.get(0, END)
            self.alphaCombo["values"] = ("<constant>", ) + self.layerList.get(0, END)
    
    def setAlpha(self, *args):
        print("Setting alpha")
        if self.alpha.get() == "<constant>":
            self.alphaEntry["state"] = NORMAL
        else:
            self.alphaEntry["state"] = DISABLED

    def setWaterEnabled(self):
        if self.waterEnabled.get():
            self.waterMaterialEntry["state"] = NORMAL
            self.waterHeightEntry["state"] = NORMAL
        else:
            self.waterMaterialEntry["state"] = DISABLED
            self.waterHeightEntry["state"] = DISABLED

    def addProp(self):
        addProp = AddProp("Add prop", self)
        addProp.showGUI(self.root)
        
    ## applies configuration window settings to generator
    def setValues(self):
        self.parent.layerPaths = []
        for key in self.layerPaths.keys():
            self.parent.layerPaths.append(self.layerPaths[key])

        self.parent.props = self.props
        self.parent.size = self.size.get()
        self.parent.heightmapPath = self.layerPaths[self.heightMap.get()]
        if self.alphaEntry["state"] == DISABLED:
            self.parent.alphaPath = self.layerPaths[self.alpha.get()]
            self.alphaScalar = None
        else:
            self.parent.alphaScalar = self.alphaConstant.get()
            self.parent.alphaPath = None
        self.parent.material = self.material.get()
        self.parent.maxHeight = self.maxHeight.get()
        self.parent.skyHeight = self.skyHeight.get()
        if self.waterEnabled.get():
            self.parent.waterHeight = self.waterHeight.get()
        else:
            self.parent.waterHeight = -1
        self.parent.waterMaterial = self.waterMaterial.get()
       
        self.closeGUI()

    def closeGUI(self):
        #print("Saving...")
        #import pickle
        #print(self.parent)
        #self.parent.configGUI = None
        #self.parent.parent = None
        #file = open("C:/Users/Zay/Desktop/dump.p","wb")
        #pickle.dump(self.parent, file)
        
        ConfigGUI.closeGUI(self)


class AddProp(ConfigGUI):

    def populateGUI(self):
        # Variables
        self.type = StringVar(self.window)
        self.layer = StringVar(self.window)
        self.layer.set("<none>")
        self.model = StringVar(self.window)
        self.radius = IntVar(self.window)
        self.radius.set(16)
        self.probability = DoubleVar(self.window)
        self.probability.set(100)
        self.zOffset = IntVar(self.window)

        # Styles
        style = {"padx":6, "pady":2, "sticky":W+E}

        # Settings frame
        settingsFrame = Frame(
            self.window,
            padx = 6,
            pady = 6,
            relief = RAISED,
            borderwidth = 1
            )
        settingsFrame.grid(column=0, row=0, sticky=W+E+N+S)
        
        row = 0
        
        # type
        Label(settingsFrame, text="Type:").grid(
            column=0,
            row=row
            )

        combo = tkinter.ttk.Combobox(
            settingsFrame,
            textvariable=self.type,
            values=("prop_static","prop_physics")
            )
        combo.grid(column=1, row=row, **style)
        combo.set("prop_static")

        row += 1
        
        # layer
        Label(settingsFrame, text="Layer:").grid(
            column=0,
            row=row
            )

        tkinter.ttk.Combobox(
            settingsFrame,
            textvariable=self.layer,
            values=("<none>", ) + self.parent.layerList.get(0, END)
            ).grid(column=1, row=row, **style)

        row += 1

        # model
        Label(settingsFrame, text="Model:").grid(
            column=0,
            row=row
            )

        Entry(settingsFrame, textvariable=self.model).grid(
            column=1,
            row=row,
            **style
            )

        row += 1

        # exclusion radius
        Label(settingsFrame, text="Exclusion radius:").grid(
            column=0,
            row=row
            )

        Entry(settingsFrame, textvariable=self.radius).grid(
            column=1,
            row=row,
            **style
            )

        row += 1

        # relative probability
        Label(settingsFrame, text="Relative probability (%):").grid(
            column=0,
            row=row,
            **style
            )

        Scale(settingsFrame, from_=0.1, to=100, resolution=0.1,
              variable=self.probability, orient=HORIZONTAL
              ).grid(column=1, row=row, **style)

        row += 1

        # z offset
        Label(settingsFrame, text="Z offset:").grid(
            column=0,
            row=row
            )

        Entry(settingsFrame, textvariable=self.zOffset).grid(
            column=1,
            row=row,
            **style
            )
        
        row += 1

        # Dialog control frame
        controlFrame = Frame(
            self.window,
            padx = 6,
            pady = 6,
            relief = RAISED,
            borderwidth = 1
            )
        controlFrame.grid(column=0, row=1, sticky=W+E+N+S)
        
        Button(
            controlFrame,
            text = "Ok",
            width = 2,
            command = self.setValues,
            padx = 10
            ).grid(column=0, row=0, padx=10, pady=5)
        Button(
            controlFrame,
            text = "Cancel",
            width = 2,
            command = self.closeGUI,
            padx = 10
            ).grid(column=1, row=0, padx=10, pady=5)

        row += 1

    def setValues(self):
        layer = self.layer.get()
        if layer == "<none>":
            layer = None
        else:
            layer = self.parent.layerPaths[layer]
        
        self.parent.props.append(
            Prop(layer, self.type.get(), self.model.get(),
                 self.radius.get(), self.probability.get()/100, self.zOffset.get())
            )
        self.parent.propList.insert(0, self.model.get())
        self.closeGUI()



class Prop:

    def __init__(self, layer, type, model, radius, probability, zOffset):
        self.layer = layer
        self.type = type
        self.model = model
        self.radius = radius
        self.probability = probability
        self.zOffset = zOffset

## Generator that runs tests on the native VMF format module
#
class HeightMap(Generator):
    ## Name
    name = "Heightmap Generator"

    ## Description
    description = "..."

    ## Supported format
    formats = [VMF]

    ## Supported games
    games = [
        HL2,
        HL2EP1,
        HL2EP2,
        # HL2DM, #Half Life 2 Death Match crashes. missing vital spawn point entities.
        P1,
        P2,
        L4D1,
        L4D2,
        CSS,
        TF2,
        GMOD
        ]

    ## Configuration GUI
    configGUI = HeightMapConfig

    ## Displacement power
    POWER = 2
    EDGE_NUM = 2**POWER
    VERTEX_NUM = EDGE_NUM + 1

    class Exclusion:
        def __init__(self, pos, radius):
            self.pos = pos
            self.radius = radius

    ## Constructor
    def __init__(self, parent):
        Generator.__init__(self, parent)
        self.size = 2048
        #self.layerPaths = []
        #self.props = []

    ## Generate map
    def generate(self, gameID):
        self.gameID = gameID
        self.map = self.parent.getMap()
        vmf = self.map.getNative()

        # Set status
        self.setStatus("Generating")

        # Load resources
        layers = {}
        for path in self.layerPaths:
            if not path in layers:
                surface = pygame.image.load(path)
                layers[path] = pygame.surfarray.array3d(surface)
                layers[path] = numpy.fliplr(layers[path]) # Flip Y-axis

        # Alias for heightmap and alpha
        heightmap = layers[self.heightmapPath]
        if self.alphaPath != None:
            alpha = layers[self.alphaPath]

        # Scale heightmap
        heightmap = heightmap*(self.maxHeight/256)

        # Generate displacements       
        dispNum = int((len(heightmap)-1)/self.EDGE_NUM)
        dispSize = int(self.size/dispNum)
        
        self.listenerWrite(
            "Adding %i power %i displacements of size %i.\n" %
            (dispNum*dispNum, self.POWER, dispSize)
            )
        for y in range(0, dispNum):
            for x in range(0, dispNum):
                solid = Solid.fromMinMax(
                    vmf,
                    [x*dispSize,y*dispSize,-128],
                    [(x+1)*dispSize,(y+1)*dispSize,0],
                    self.material
                    )
                solid.sides[0].power = self.POWER

                for u in range(0, self.VERTEX_NUM):
                    for v in range(0, self.VERTEX_NUM):
                        i = x*self.EDGE_NUM + u
                        j = y*self.EDGE_NUM + v
                        
                        # Set displacement height
                        solid.sides[0].displacement[u][v][2] = int(heightmap[i,j][0])

                        # Set alpha value
                        if self.alphaPath != None:
                            solid.sides[0].alpha[u][v] = int(
                                alpha[i, j][0]
                                )
                        else:
                            solid.sides[0].alpha[u][v] = self.alphaScalar
        
        self.listenerWrite("Finished adding displacements.\n")

        # Add props
        propNum = 0
        vertexSize = dispSize/self.EDGE_NUM
        exclusions = []
        for prop in self.props:
            for y in range(0, len(heightmap)):
                for x in range(0, len(heightmap)):                        
                    if (prop.layer == None or random.random()*256 < layers[prop.layer][x,y][0]) and \
                       random.random() < prop.probability:
                        pos = [
                            x*vertexSize,
                            y*vertexSize,
                            heightmap[x,y][0] + prop.zOffset
                            ]

                        canAdd = True
                        for exclusion in exclusions:
                            offset = [
                                exclusion.pos[0]-pos[0],
                                exclusion.pos[1]-pos[1],
                                ]
                            distance = math.sqrt(offset[0]*offset[0] + offset[1]*offset[1])

                            if distance < exclusion.radius and distance < prop.radius:
                                canAdd = False
                                break

                        if canAdd:                           
                            entity = Entity(vmf, prop.type)
                            entity["origin"] = pos
                            entity["angles"] = [0, 0, random.randrange(0,360)]
                            entity["model"] = prop.model

                            if prop.radius > 0:
                                exclusions.append(self.Exclusion(pos, prop.radius))
                            
                            propNum += 1

        self.listenerWrite("Added %i props.\n" % propNum)

        # Add sky       
        skyHeight = self.maxHeight + self.skyHeight
        
        # top
        Solid.fromMinMax(
            vmf,
            [0, 0, skyHeight],
            [self.size, self.size, skyHeight + 128],
            "tools/toolsskybox"
            )

        # bottom
        Solid.fromMinMax(
            vmf,
            [0,0,-256],
            [self.size,self.size,-128],
            "tools/toolsskybox"
            )

        # north
        Solid.fromMinMax(
            vmf,
            [0,self.size,-128],
            [self.size,self.size+128,skyHeight],
            "tools/toolsskybox"
            )

        # south
        Solid.fromMinMax(
            vmf,
            [0,-128,-128],
            [self.size,0,skyHeight],
            "tools/toolsskybox"
            )

        # east
        Solid.fromMinMax(
            vmf,
            [self.size,0,-128],
            [self.size+128,self.size,skyHeight],
            "tools/toolsskybox"
            )

        # west
        Solid.fromMinMax(
            vmf,
            [-128,0,-128],
            [0,self.size,skyHeight],
            "tools/toolsskybox"
            )

        self.listenerWrite("Added sky.\n")

        # Add water       
        if self.waterHeight > 0:            
            solid = Solid.fromMinMax(
                vmf,
                [0,0,-128],
                [self.size,self.size,self.waterHeight]
                )
            for side in solid.sides:
                side.material = "tools/toolsnodraw"
            solid.sides[0].material = self.waterMaterial

            self.listenerWrite("Added water.\n")

        # Save the map
        self.map.save()

        # Say that we are done
        self.setProgress(1.0)
        self.setStatus('Done')
