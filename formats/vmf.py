import math, copy, re
import gameids
from formats.fgd import FGD
from formats.sdkutil import SDKUtil


## Unordered collection of keys and associated lists of values.
#
#  DO NOT USE! Used internally for VMF loading and saving.
#  Stores for quick access at the expense of maintaining ordered key value pairs.
class KeyValueDict:

    ## Constructor
    #
    #  Creates empty KeyValueDict
    def __init__(self):
        ## key value pairs
        self.dict = {}

    ## Adds the value to the list specified by the key
    #
    #  @param key key of the value list
    #  @param value value to add to the value list
    def add(self, key, value):
        #assert type(key) == str
        #assert type(value) in (str,list)
        if key in self.dict.keys():
            self.dict[key].append(value)
        else:
            self.dict[key] = [value]

    ## Boolean check whether the specified key is present
    #
    #  @return boolean
    def __contains__(self, key):
        return key in self.dict

    ## Returns a list of values associated with the key
    #
    #  @param key key of the value list
    #  @return list list specified by key 
    def __getitem__(self, key):
        return self.dict[key]

    ## Returns the keys in the instance
    def keys(self):
        return self.dict.keys()

    ## Prints the contents in an easily readable fashion
    #
    #  @param indent indentation amount
    def debugPrint(self, indent=0):
        for key in self.dict.keys():
            values = self.dict[key]
            for value in values:
                if type(value) == str:
                    print(" " * indent + "%s %s" % (key, value))
                else:
                    print(" " * indent + "%s" % (key))
                    value.debugPrint(indent + 1)



## Ordered collection of keys and associated lists of values.
#
#  DO NOT USE! Used internally for VMF loading and saving.
#  Stores ordered key value pairs at the expensive of speed.
class KeyValueList:

    ## Class for internal storage of key value pairs.
    class Pair:
        ## Constructor
        #
        #  @param key name
        #  @param value data associated with key
        def __init__(self, key, value):
            ## name
            self.key = key
            ## data
            self.value = value

    ## Constructor.
    #
    #  Creates an empty KeyValueList instance
    def __init__(self):
        ## ordered key value list
        self.list = []

    ## Adds the value to the list specified by the key
    #
    #  @param key key of the value list
    #  @param value value to add to the value list
    def add(self, key, value):
        assert type(key) == str
        assert type(value) in (str,KeyValueList) # Note: doesn't work in Python 2.6
        self.list.append(KeyValueList.Pair(key,value))

    ## Returns the key value pairs.
    #
    #  @return list list of objects with key and value members
    def getPairs(self):
        return self.list



## Provides a means to manipulate the VMF map format.
#
class VMF:

    _FORMAT_VERSION = 100

    ## Constructor
    #
    #  @param gameId ID of game
    #  @param filename filename of the VMF to load. VMF must be in multiple-line
    #  format.
    def __init__(self, gameId, filename=None):
        ## the game this VMF is meant for. (Determines available entities)
        #  @todo FIXME
        if gameids.getGameFormat(gameId) != gameids.VMF:
            raise Exception("Game ID %s does not use the VMF format." % gameId)
        
        self.gameId = gameId
        self._currentId = 1
        self._prefabCounter = 0 # Counter for replacing '%i' with appropriate prefab number in prefabs
        if filename == None:
            self._setupEmptyMap()
        else:
            self._load(filename)

    ## Sets up an empty map with default values
    def _setupEmptyMap(self):
        # Version info
        ## Is this file a prefab
        self.prefab = False

        # View settings
        ## Enable snap-to-grid in Hammer when editing
        self.snapToGrid = True
        ## Show the grid in Hammer when editing
        self.showGrid = True
        ## Grid scale in Hammer
        self.gridSpacing = 16
        ## Show 3D grid in Hammer
        self.show3DGrid = False

        # Worldspawn
        ## grass sprite texture
        self.detailMaterial = "detail/detailsprites"
        ## information about grass density
        self.detailVBSP = "detail.vbsp"
        ## the maximum screen width of props (some kind of level-of-detail override?)
        self.maxPropScreenWidth = -1
        ## Skybox texture
        self.sky = "sky_day01_01"

        # Solids and entities
        ## list of solids/brushes in this file
        self.solids = []
        ## list of entities in this file
        self.entities = []

        # Cordon
        ## bottom lower left corner of cordon
        self.cordonMin = [-1024, -1024, -1024]
        ## top upper right corner of cordon
        self.cordonMax = [1024, 1024, 1024]
        ## enable cordon
        self.cordonActive = False

    ## Attempts to load the specified filename
    def _load(self, filename):
        inputFile = open(filename)
        vmfKVD = self._buildKVD(inputFile)
        self._parseKVD(vmfKVD)

        # Reset ID counter with maximum ID
        self._currentId = self._findMaxId()

    def _buildKVD(self, inputFile):
        vmfKVD = KeyValueDict()
        line = inputFile.readline()
        while len(line) != 0:
            childKVD = KeyValueDict()
            childKey = re.findall("\S+", line)[0]
            self._readKVDContents(inputFile, childKVD)
            vmfKVD.add(childKey, childKVD)

            line = inputFile.readline()

        return vmfKVD

    def _readKVDContents(self, inputFile, rootKVD):
        inputFile.readline() # Skip '{'
        line = inputFile.readline()
        while line.find('}') == -1:
            if line.find('"') != -1: # Found key value pair
                key, value = re.findall(r'"(.*?)"',line)
                rootKVD.add(key, value)
            else: # Found child
                childKVD = KeyValueDict()
                childKey = re.findall("\S+",line)[0]
                rootKVD.add(childKey, childKVD)
                self._readKVDContents(inputFile, childKVD)

            line = inputFile.readline()   

    def _parseKVD(self, vmfKVD):
        versionKVD = vmfKVD["versioninfo"][0]
        self.prefab = bool(int(versionKVD["prefab"][0]))

        if "viewsettings" in vmfKVD:
            viewKVD = vmfKVD["viewsettings"][0]
            self.snapToGrid = bool(int(viewKVD["bSnapToGrid"][0]))
            self.showGrid = bool(int(viewKVD["bShowGrid"][0]))
            self.gridSpacing = int(viewKVD["nGridSpacing"][0])
            self.show3DGrid = bool(int(viewKVD["bShow3DGrid"][0]))

        worldKVD = vmfKVD["world"][0]
        if "detailmaterial" in worldKVD:
            self.detailMaterial = worldKVD["detailmaterial"][0]
        else:
            self.detailMaterial = ""
        
        if "detailvbsp" in worldKVD:
            self.detailVBSP = worldKVD["detailvbsp"][0]
        else:
            self.detailVBSP = ""
        
        if "maxpropscreenwidth" in worldKVD:
            self.maxPropScreenWidth = int(worldKVD["maxpropscreenwidth"][0])
        else:
            self.maxPropScreenWidth = ""
        
        self.sky = worldKVD["skyname"][0]

        self.solids = []
        if "solid" in worldKVD:
            for solidKVD in worldKVD["solid"]:
                solid = Solid.fromKVD(self, solidKVD)

        self.entities = []
        if "entity" in vmfKVD:
            for entityKVD in vmfKVD["entity"]:
                entity = Entity.fromKVD(self, entityKVD)

        if "cordon" in vmfKVD:
            cordonKVD = vmfKVD["cordon"][0]
            self.cordonMin = SDKUtil.getNumbers(cordonKVD["mins"][0], float)
            self.cordonMax = SDKUtil.getNumbers(cordonKVD["maxs"][0], float)
            self.cordonActive = bool(int(cordonKVD["active"][0]))
        else:
            self.cordonMin = [-1024, -1024, -1024]
            self.cordonMax = [1024, 1024, 1024]
            self.cordonActive = False

    def _findMaxId(self):
        maxId = 0

        for solid in self.solids:
            maxId = max([maxId, solid.id])
            for side in solid.sides:
                maxId = max([maxId, side.id])

        for entity in self.entities:
            maxId = max([maxId, entity.id])

        return maxId

    ## Save vmf map to file
    #
    #  @param filename path to save map to
    def save(self, filename):
        outputFile = open(filename, "w")
        vmfKVL = self._toKVL()
        self._writeKVL(vmfKVL, outputFile, 0)

    def _toKVL(self):
        vmfKVL = KeyValueList()
        
        versionInfoKVL = KeyValueList()
        versionInfoKVL.add("formatversion", str(VMF._FORMAT_VERSION))
        versionInfoKVL.add("prefab", str(int(self.prefab)))
        vmfKVL.add("versioninfo", versionInfoKVL)

        viewSettingsKVL = KeyValueList()
        viewSettingsKVL.add("bSnapToGrid", str(int(self.snapToGrid)))
        viewSettingsKVL.add("bShowGrid", str(int(self.showGrid)))
        viewSettingsKVL.add("nGridSpacing", str(self.gridSpacing))
        viewSettingsKVL.add("bShow3DGrid", str(int(self.show3DGrid)))
        vmfKVL.add("viewsettings", viewSettingsKVL)

        worldKVL = KeyValueList()
        worldKVL.add("id", "1")
        worldKVL.add("classname", "worldspawn")
        worldKVL.add("detailmaterial", self.detailMaterial)
        worldKVL.add("detailvbsp", self.detailVBSP)
        worldKVL.add("maxpropscreenwidth", str(self.maxPropScreenWidth))
        worldKVL.add("skyname", self.sky)
        for solid in self.solids:
            worldKVL.add("solid", solid.toKVL())
        vmfKVL.add("world",worldKVL)

        for entity in self.entities:
            vmfKVL.add("entity", entity.toKVL())

        cordonKVL = KeyValueList()
        cordonKVL.add(
            "mins",
            "(%g %g %g)" % tuple(self.cordonMin)
            )
        cordonKVL.add(
            "maxs",
            "(%g %g %g)" % tuple(self.cordonMax)
            )
        cordonKVL.add("active", str(int(self.cordonActive)))
        vmfKVL.add("cordon",cordonKVL)

        return vmfKVL

    def _writeKVL(self, rootKVL, outputFile, indent):
        for pair in rootKVL.getPairs():
            key, value = pair.key, pair.value
            if type(value) == str:
                outputFile.write("\t" * indent + '"%s" "%s"\n' % (key, value))
            else:
                outputFile.write("\t" * indent + key + "\n")
                outputFile.write("\t" * indent + "{\n")
                self._writeKVL(value, outputFile, indent + 1)
                outputFile.write("\t" * indent + "}\n")

    ## provide a unique ID number for members of this VMF
    def generateId(self):
        self._currentId += 1
        return self._currentId

    ## Insert a prefab
    #
    #  @todo incomplete
    #
    #  @param prefab the prefab VMF object
    #  @param pos translation
    #  @param rot rotation
    #  @param scale scaling
    #  @param materialLock translate and rotate textures with brushes
    #  @param materialScaleLock scale textures with brushes
    def addPrefab(self, prefab, pos=[0,0,0], rot=[0,0,0], scale=[1,1,1], materialLock=True, materialScaleLock=True):
        s = Matrix.fromScale(scale[0], scale[1], scale[2])
        r = Matrix.fromAngles(rot[0], rot[1], rot[2])
        t = Matrix.fromTranslate(pos[0], pos[1], pos[2])
        
        #copy solids
        newSolids = []
        for solid in prefab.solids:
            newSolids.append(solid.copy(self))
        #transform solids
        for solid in newSolids:
            solid.transform(s, materialLock, materialScaleLock, [0,0,0])
            solid.transform(r, materialLock, materialScaleLock, [0,0,0])
            solid.transform(t, materialLock, materialScaleLock, [0,0,0])
        
        #copy entites
        newEntities = []
        for entity in prefab.entities:
            newEntities.append(entity.copy(self))
            
        #transform entities
        for entity in newEntities:
            entity.transform(s, materialLock, materialScaleLock, [0,0,0])
            entity.transform(r, materialLock, materialScaleLock, [0,0,0])
            entity.transform(t, materialLock, materialScaleLock, [0,0,0])
            
        #change names so they don't interfere
        for entity in newEntities:
            for key in entity.getPropertyNames():
                if type(entity[key]) == str:
                    entity[key] = entity[key].replace("&i", str(self._prefabCounter))
            for outputName in entity.outputs.keys():
                for output in entity.outputs[outputName]:
                    output.target = output.target.replace("&i", str(self._prefabCounter))

        self._prefabCounter += 1


## VMF Solid. Used for brushes and also displacements.
class Solid:

    ## default material
    DEFAULT = 0
    ## positive along Z axis
    TOP = 1
    ## negative along Z axis
    BOTTOM = 2
    ## positive along Y axis
    NORTH = 3
    ## negative along Y axis
    SOUTH = 4
    ## positive along X axis
    EAST = 5
    ## negative along X axis
    WEST = 6

    ## X axis
    X_AXIS = 0
    ## Y axis
    Y_AXIS = 1
    ## Z axis
    Z_AXIS = 2

    ## Default Constructor
    #
    #  @param parent VMF containing this solid
    #  @param origin origin of the solid to be used during scaling and rotations
    def __init__(self, parent, origin=[0.0,0.0,0.0]):
        ## VMF containing this solid
        self.parent = parent
        self.parent.solids.append(self)
        ## translation origin
        self.origin = origin

        ## unique node ID
        self.id = parent.generateId()
        ## list of Sides that define this solid
        self.sides = []

    ## Create a copy
    #
    #  @param parent parent object of copy
    #
    #  @return Solid
    def copy(self, parent = None):
        if parent == None:
            parent = self.parent
        new = Solid(parent)
        new.origin = self.origin
        for side in self.sides:
            new.sides.append(side.copy(new))
        return new

    ## INTERNAL! Create Solid from Key-value dictionary. Used in parsing VMF files.
    @staticmethod
    def fromKVD(parent, solidKVD):
        solid = Solid(parent)
        solid.id = int(solidKVD["id"][0])
        for sideKVD in solidKVD["side"]:
            side = Side.fromKVD(solid, sideKVD)
        return solid

    ## Create Solid from 3D planes defined by sets of 3 points.
    #
    #  @param parent VMF containing this solid
    #  @param planes list of planes bounding a convex solid
    #  The order of the points in the plane matters. They are clockwise if you
    #  are looking at it from the outside, counterclockwise if you are viewing
    #  from inside.
    #  @param materials optional material/texture to use on solid.
    #  May be string or list. List order corresponds to list of planes.
    #
    #  @return VMF solid object
    #  @sa Side.__init__()
    @staticmethod
    def fromPlanes(parent, planes, materials=""):
        solid = Solid(parent)
        if type(materials) == str:
            for plane in planes:
                Side(solid, plane, materials)
        elif type(materials) == list:
            assert len(planes) == len(materials)
            for x in range(0, len(planes)):
                Side(solid, planes[x], materials[x])
        else:
            raise Exception() ## @todo FIXME
        
        return solid

    ## Create Solid from 3D planes defined by points and normals.
    #
    #  @param parent VMF containing this solid
    #  @param points list of points on each face
    #  @param normals list of normal vectors for each face
    #  @param materials optional material/texture to use on solid.
    #  May be string or list. List order corresponds to lists of points/normals.
    #
    #  @return VMF solid object
    #  @sa Side.fromNormal()
    @staticmethod
    def fromNormals(parent, points, normals, materials=""):
        assert len(points) == len(normals)
        solid = Solid(parent)
        if type(materials) == str:
            for n in range(len(points)):
                Side.fromNormal(solid, points[n], normals[n], materials)
        elif type(materials) == list:
            assert len(points) == len(materials)
            for n in range(len(points)):
                Side.fromNormal(solid, points[n], normals[n], materials[n])
        else:
            raise Exception() ## @todo FIXME (don't know what zay has in mind)
        return solid

    ## Create rectangular Solid
    #
    #  @param parent VMF containing this solid
    #  @param minPoint minimum (x,y,z) values
    #  @param maxPoint maximum (x,y,z) values
    #  @param textures optional name of texture(s) to use. Single texture can
    #  be defined by a string. Face-specific textures are defined as a dict.
    #  Constants for key values are defined in Solid. Solid.DEFAULT is used to
    #  define the texture used if a face doesn't have a texture specifically
    #  defined.
    #
    #  @return VMF solid object
    @staticmethod
    def fromMinMax(parent, minPoint, maxPoint, textures=""):

        #make material list
        if type(textures) == str:
            materials = textures
        else:
            assert type(textures) == dict
            if Solid.DEFAULT in textures:
                materials = [textures[Solid.DEFAULT]]*6
            else:
                materials = ['']*6
            order = [
                    Solid.TOP,
                    Solid.BOTTOM,
                    Solid.NORTH,
                    Solid.SOUTH,
                    Solid.EAST,
                    Solid.WEST
                    ]
            for side in range(6):
                if order[side] in textures:
                    materials[side] = textures[order[side]]

        #make list of planes
        t = maxPoint[2]
        b = minPoint[2]
        n = maxPoint[1]
        s = minPoint[1]
        e = maxPoint[0]
        w = minPoint[0]
        planes = [
            [[0,0,t],[1,0,t],[1,-1,t]], #top
            [[0,0,b],[1,0,b],[1,1,b]], #bottom
            [[0,n,0],[1,n,0],[1,n,1]], #north side
            [[0,s,0],[1,s,0],[1,s,-1]], #south side
            [[e,0,0],[e,1,0],[e,1,-1]], #east side
            [[w,0,0],[w,1,0],[w,1,1]] #west side
            ]
        
        return Solid.fromPlanes(parent, planes, materials)

    ## Create rectangular solid of a particular size
    #
    #  @param parent VMF containing this solid
    #  @param pos lower left bottom corner. (minimum x,y,z)
    #  @param size size in 3 dimensions (x,y,z)
    #  @param textures optional name of texture(s) to use. Single texture can
    #  be defined by a string. Face-specific textures are defined as a dict.
    #  Constants for key values are defined in Solid. Solid.DEFAULT is used to
    #  define the texture used if a face doesn't have a texture specifically
    #  defined.
    #
    #  @return VMF solid object
    @staticmethod
    def from3DRect(parent, pos, size, textures=""):
        return Solid.fromMinMax(
            parent,
            pos,
            [pos[0]+size[0],
             pos[1]+size[1],
             pos[2]+size[2]],
            textures
            )

    ## Create a rectangular displacement
    #
    #  @param parent VMF containing this displacement
    #  @param pos bottom lower left corner (x,y,z)
    #  @param size size of displacement
    #  @param heightMap square array of height values. Height values are absolute.
    #  @param material texture of displacement
    #
    #  @return VMF solid object
    @staticmethod
    def fromHeightMap(parent, pos, size, heightMap, material=""):
        power = math.log(len(heightMap) - 1)/math.log(2)
        if not power in (2,3,4):
            raise ValueError('invalid heightMap dimension')
        solid = Solid.from3DRect(
            parent,
            pos,
            size,
            material
            )
        offsets = []
        for row in heightMap:
            offsets.append([[0,0,z-pos[2]-size[2]] for z in row])
        solid.sides[0].power = power
        solid.sides[0].displacement = offsets
        solid.sides[0]._startPosition = [pos[0], pos[1], pos[2]]
        return solid

    ## Create cylindrical solid
    #
    #  @param parent VMF containing this solid
    #  @param pos bottom center (x,y,z)
    #  @param radius radius
    #  @param height height of cylinder
    #  @param subdivisions number of sides cylinder will have. [3..*]
    #  @param materials optional material/texture to use on solid.
    #  May be string or list. Order of list is bottom, top, then sides around
    #  circumference starting on the north face going clockwise.
    #
    #  @return VMF solid object
    @staticmethod
    def fromCylinder(parent, pos, radius, height, subdivisions, materials=""):
        if subdivisions < 3:
            raise ValueError("Too few subdivisions: " + str(subdivisions))
        
        planes = []
        points = []
        step = math.pi*2/subdivisions
        for i in range(subdivisions):
            points.append([int(math.sin(i*step)*radius), int(math.cos(i*step)*radius)])

        # Bottom
        planes.append(
            [[0, 0, pos[2]],
             [-1, -1, pos[2]],
             [0, -1, pos[2]]]
            )

        # Top
        planes.append(
            [[0, 0, pos[2]+height],
             [1, 0, pos[2]+height],
             [1, -1, pos[2]+height]]
            )
        # Sides
        for x in range(len(points) - 1):
            planes.append(
                [[pos[0]+points[x][0], pos[1]+points[x][1], 0],
                 [pos[0]+points[x+1][0], pos[1]+points[x+1][1], 0],
                 [pos[0]+points[x+1][0], pos[1]+points[x+1][1], 1]]
                )
        planes.append(
            [[pos[0]+points[-1][0], pos[1]+points[-1][1], 0],
             [pos[0]+points[0][0], pos[1]+points[0][1], 0],
             [pos[0]+points[0][0], pos[1]+points[0][1], 1]]
            )

        return Solid.fromPlanes(parent, planes, materials)

    ## Extrude a solid from a convex polygon
    #
    #  @param parent VMF containing this solid
    #  @param pos bottom origin (x,y,z)
    #  @param polygon polygon defined by list of (x,y) points. (x,y) of pos
    #  applied as offsets. Must be convex. Must be in clockwise order.
    #  @param height height of solid, projected up from pos
    #  @param materials optional material/texture to use on solid.
    #  May be string or list. Order of list is bottom, top, then sides in the
    #  order specified in the polygon
    #
    #  @return VMF solid object
    @staticmethod
    def fromConvexPolygon(parent, pos, polygon, height, materials=""):
        assert len(polygon) >= 3 #a polygon has at least 3 points
        assert all([len(x) == 2 for x in polygon]) #each point must have two values, (x,y)
        planes = []
        
        # Bottom
        planes.append(
            [[pos[0], pos[1], pos[2]],
             [pos[0]-1, pos[1]-1, pos[2]],
             [pos[0], pos[1]-1, pos[2]]]
            )

        # Top
        planes.append(
            [[pos[0], pos[1], pos[2]+height],
             [pos[0]+1, pos[1], pos[2]+height],
             [pos[0]+1, pos[1]-1, pos[2]+height]]
            )
        
        for x in range(len(polygon) - 1):
            planes.append(
                [[pos[0]+polygon[x][0], pos[1]+polygon[x][1], 1],
                 [pos[0]+polygon[x+1][0], pos[1]+polygon[x+1][1], 0],
                 [pos[0]+polygon[x+1][0], pos[1]+polygon[x+1][1], 1]]
                )
        planes.append(
            [[pos[0]+polygon[-1][0], pos[1]+polygon[-1][1], 1],
             [pos[0]+polygon[0][0], pos[1]+polygon[0][1], 0],
             [pos[0]+polygon[0][0], pos[1]+polygon[0][1], 1]]
            )

        return Solid.fromPlanes(parent, planes, materials)

    ## Create a solid by revolving the given 2D shape around the Z axis.
    #
    #  @bug sometimes produces duplicate planes. Likely caused by rounding.
    #  @bug planes sometimes have bad texture axes (parallel to face normal)
    #
    #  @param parent VMF containing this solid
    #  @param pos center of base (x,y,z)
    #  @param profile list of (radius, z) coordinate pairs. Must be convex. Must be ordered from bottom to top. The shape must
    #  start and end with radius = 0.
    #  @param subdivisions number of segments used to approximate revolution
    #  @param material optional material/texture to use on solid. Must be string
    #
    #  @return VMF solid object
    @staticmethod
    def fromRevolution(parent, pos, profile, subdivisions, material=''):
        assert subdivisions >= 3
        assert len(profile) >= 3
        assert int(profile[0][0]) == 0
        assert int(profile[-1][0]) == 0
        assert type(material) == str
        planes = []
        ring = []
        step = math.pi*2.0/subdivisions
        i = 0.0
        for i in range(subdivisions):
            ring.append([math.sin(i*step), math.cos(i*step)])
        #bottom end cap
        if profile[0][0] == profile[1][0]:
            #flat end, one face
            planes.append([
                [0,0,profile[0][0]],
                [1,0,profile[0][0]],
                [1,1,profile[0][0]]
                ])
        else:
            #pointed end cap
            for i in range(len(ring)-1):
                planes.append([
                    [int(ring[i+1][0]*profile[1][0] + pos[0]), int(ring[i+1][1]*profile[1][0] + pos[1]), int(pos[2] + profile[1][1])],
                    [int(ring[i][0]*profile[1][0] + pos[0]), int(ring[i][1]*profile[1][0] + pos[1]), int(pos[2] + profile[1][1])],
                    [int(pos[0]), int(pos[1]), int(pos[2] + profile[0][1])]
                    ])
            planes.append([
                [int(ring[0][0]*profile[1][0] + pos[0]), int(ring[0][1]*profile[1][0] + pos[1]), int(pos[2] + profile[1][1])],
                [int(ring[-1][0]*profile[1][0] + pos[0]), int(ring[-1][1]*profile[1][0] + pos[1]), int(pos[2] + profile[1][1])],
                [int(pos[0]), int(pos[1]), int(pos[2] + profile[0][1])]
                ])
        #middle sections
        for j in range(1, len(profile) - 2):
            for i in range(len(ring)-1):
                planes.append([
                    [int(pos[0] + ring[i][0]*profile[j][0]), int(pos[1] + ring[i][1]*profile[j][0]), int(pos[2]+profile[j][1])],
                    [int(pos[0] + ring[i+1][0]*profile[j][0]), int(pos[1] + ring[i+1][1]*profile[j][0]), int(pos[2]+profile[j][1])],
                    [int(pos[0] + ring[i+1][0]*profile[j+1][0]), int(pos[1] + ring[i+1][1]*profile[j+1][0]), int(pos[2]+profile[j+1][1])]
                    ])
            planes.append([
                [int(pos[0] + ring[-1][0]*profile[j][0]), int(pos[1] + ring[-1][1]*profile[j][0]), int(pos[2]+profile[j][1])],
                [int(pos[0] + ring[0][0]*profile[j][0]), int(pos[1] + ring[0][1]*profile[j][0]), int(pos[2]+profile[j][1])],
                [int(pos[0] + ring[0][0]*profile[j+1][0]), int(pos[1] + ring[0][1]*profile[j+1][0]), int(pos[2]+profile[j+1][1])]
                ])
        #top end cap
        if profile[-1][0] == profile[-2][0]:
            #flat end, one face
            planes.append([
                [0,0,profile[-1][0]],
                [1,0,profile[-1][0]],
                [1,-1,profile[-1][0]]
                ])
        else:
            #pointed end cap
            for i in range(len(ring)-1):
                planes.append([
                    [int(ring[i][0]*profile[-2][0] + pos[0]), int(ring[i][1]*profile[-2][0] + pos[1]), int(pos[2] + profile[-2][1])],
                    [int(ring[i+1][0]*profile[-2][0] + pos[0]), int(ring[i+1][1]*profile[-2][0] + pos[1]), int(pos[2] + profile[-2][1])],
                    [int(pos[0]), int(pos[1]), int(pos[2] + profile[-1][1])]
                    ])
            planes.append([
                [int(ring[-1][0]*profile[-2][0] + pos[0]), int(ring[-1][1]*profile[-2][0] + pos[1]), int(pos[2] + profile[-2][1])],
                [int(ring[0][0]*profile[-2][0] + pos[0]), int(ring[0][1]*profile[-2][0] + pos[1]), int(pos[2] + profile[-2][1])],
                [int(pos[0]), int(pos[1]), int(pos[2] + profile[-1][1])]
                ])
        return Solid.fromPlanes(parent, planes, material)
        

    ## Create a spherical solid
    #
    #  @param parent VMF containing this solid
    #  @param pos center (x,y,z)
    #  @param radius radius
    #  @param subdivisions number of vertical layers and number of sides around each vertical layer.
    #  @param material optional material/texture to use on solid. Must be string.
    #
    #  @return VMF solid object
    @staticmethod
    def fromSphere(parent, pos, radius, subdivisions, material=''):
        profile = []
        step = math.pi/subdivisions
        #this tweak forces the sphere to be the specified radius at its equator despite the approximation.
        if subdivisions%2 == 1:
            tweak = radius/math.cos(step/2.0)
        else:
            tweak = radius
        for i in range(subdivisions):
            profile.append([math.sin(i*step)*tweak, -math.cos(i*step)*radius])
        profile.append([0.0, radius])
        return Solid.fromRevolution(parent, pos, profile, subdivisions, material)

    ## INTERNAL!! export to key-value list format. Used in saving VMF files
    def toKVL(self):
        solidKVL = KeyValueList()
        solidKVL.add("id", str(self.id))
        for side in self.sides:
            solidKVL.add("side", side.toKVL())

        return solidKVL

    ## provide a unique ID number for members of this Solid
    def generateId(self):
        return self.parent.generateId()

    ## transform the solid using a transformation matrix
    #
    #  @param transform a 4x4 transformation matrix
    #  @param materialLock If true, textures are transformed with the solid.
    #  (Hammer calls it texture lock.)
    #  @param materialScaleLock If true, textures scale with the solid.
    #  @param origin optional transformation origin to override solid origin
    #
    #  @sa Matrix
    def transform(self, transform, materialLock=False, materialScaleLock=False, origin=None):
        if origin == None:
            origin = self.origin
        for side in self.sides:
            side.transform(transform, materialLock, materialScaleLock, origin)
        self.origin = transform.transformVector(origin)


## side/face of a vmf solid. Contains displacement information if this side is a
#  displacement.
class Side:

    ## list of valid displacement powers
    POWERS = (2,3,4)

    ## Constructor. Create a side using 3 points on the plane
    #
    #  @param parent Solid containing this side
    #  @param plane 3 coordinates on the plane that defines this side. (x,y,z)
    #  The order of the points matters. They are clockwise if you are looking at
    #  it from the outside, counterclockwise if you are viewing from inside.
    #  @param material optional texture name.
    def __init__(self, parent, plane=[[0,0,0],[0,0,0],[0,0,0]], material=""):
        assert type(material) == str
        ## Solid containing this side
        self.parent = parent
        self.parent.sides.append(self)

        ## unique ID
        self.id = parent.generateId()
        ## plane defined by 3 points
        self.plane = plane
        ## material displayed on this side
        self.material = material
        ## u/v texture axis. defines orientation of texture
        self.textureAxes = self._findNearestAxes()
        ## material offset
        self.offset = [0,0]
        ## material scale
        self.scale = [0.25,0.25]
        ## material rotation
        self.rotation = 0
        ## lightmap scale
        self.lightmapScale = 16
        ## smoothing groups
        self.smoothingGroups = 0
        #  displacement data
        self._vertexNum = 0
        self._startPosition = None
        self._displacement = None
        self._alpha = None

    ## Create a copy
    #
    #  @param parent parent object of copy
    #
    #  @return Side
    def copy(self, parent=None):
        new = copy.copy(self)
        if parent != None:
            new.parent = parent
        new.id = new.parent.generateId()
        new.textureAxes = copy.copy(self.textureAxes)
        new.offset = copy.copy(self.offset)
        new.scale = copy.copy(self.scale)
        return new

    ## Create a side using 1 point on the plane and 1 normal vector
    #
    #  @param parent Solid containing this side
    #  @param pos a point on the side (x,y,z)
    #  @param normal normal vector pointing out from the side
    #  @param material optional texture name.
    #
    #  @return Side
    @staticmethod
    def fromNormal(parent, pos, normal, material=""):
        assert len(pos) == 3
        assert len(normal) == 3
        assert sum(map(abs, normal)) > 0.0003 #normal length must be reasonable
        points = [pos,None,None]
        # generate 2nd point, orthogonal to normal vector
        if abs(normal[0]) > 0.0001:
            points[1] = [
                -normal[1]/float(normal[0]) + pos[0],
                pos[1] + 1,
                pos[2]
                ]
        elif abs(normal[1]) > 0.0001:
            points[1] = [
                pos[0] + 1,
                -normal[0]/float(normal[1]) + pos[1],
                pos[2]
                ]
        else:
            #since normal is nonzero, z!=0 if x==0 and y==0
            points[1] = [
                pos[0],
                pos[1] + 1,
                -normal[1]/float(normal[2]) + pos[2]
                ]
        #get third point by normal X vector(p1->p2)
        #v = vector(from points[0] to points[1])
        v = [
            points[1][0] - points[0][0],
            points[1][1] - points[0][1],
            points[1][2] - points[0][2]
            ]
        #normalize v
        vmag = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]+v[2])
        v[0] = v[0]/vmag
        v[1] = v[1]/vmag
        v[2] = v[2]/vmag
        #v2 is cross product of normal and v
        #if the size of this vector gets out of hand, normalize normal
        v2 = [
            normal[1]*v[2] - normal[2]*v[1],
            normal[2]*v[0] - normal[0]*v[2],
            normal[0]*v[1] - normal[1]*v[0]
            ]
        #using p1-v2 so resulting order will be clockwise (from the outside)
        points[2] = [
            pos[0] - v2[0],
            pos[1] - v2[1],
            pos[2] - v2[2]
            ]
        return Side(parent, points, material)
    
    def _getPower(self):
        if self._vertexNum == 0:
            return 0
        else:
            return math.log(self._vertexNum - 1, 2) #base 2
    
    def _setPower(self, power):
        if power == 0:
            self._vertexNum = 0
            self._startPosition = None
            self._displacement = None
            self._alpha = None
        elif power in Side.POWERS:
            if self.power != power:
                self._vertexNum = int(2**power + 1)
                ## @todo fixme - startPosition should be the real corner of the brush.
                #  @bug (confirmed) displacements in far NE corner are corrupted. startPosition too far away. Looks like an overflow error.
                #  @bug (confirmed) in non-rectangular displacements, a corner other than the one intended can be closer to startPosition - ruins displacement
                self._startPosition = [-8192, -8192, -8192]
                self._displacement = []
                for x in range(0, self._vertexNum):
                    column = []
                    for y in range(0, self._vertexNum):
                        column.append([0,0,0])
                    self._displacement.append(column)
                self._alpha = []
                for x in range(0, self._vertexNum):
                    self._alpha.append([0]*self._vertexNum)
        else:
            raise Exception("Invalid power: " + str(power))
    ## Power of displacement
    power = property(fget=_getPower, fset=_setPower)

    def _getVertexNum(self):
        return self._vertexNum
    ## number of vertices on each axis of displacement
    vertexNum = property(fget=_getVertexNum)

    def _getDisplacement(self):
        if self._vertexNum == 0:
            raise Exception("Cannot access displacement when power is zero.")
        
        return self._displacement
    
    def _setDisplacement(self, displacement):
        if self._vertexNum == 0:
            raise Exception("Cannot modify displacement when power is zero.")

        if len(displacement) != self._vertexNum or \
           len(displacement[0]) != self._vertexNum:
            raise Exception(
                "Power/vertex number mismatch. Expected %ix%i vertices, got %ix%i." %
                (self._vertexNum, self._vertexNum, len(displacement), len(displacement[0]))
                )
        self._displacement = displacement
    ## displacement offset values
    #  displacement is a 2d array of offsets. It is a column-major array, addressed like disp[x][y]
    displacement = property(fget=_getDisplacement, fset=_setDisplacement)

    def _getAlpha(self):
        if self._vertexNum == 0:
            raise Exception("Cannot access alpha when power is zero.")
        
        return self._alpha

    def _setAlpha(self, alpha):
        if self._vertexNum == 0:
            raise Exception("Cannot modify alpha when power is zero.")

        if len(alpha) != self._vertexNum or \
           len(alpha[0]) != self._vertexNum:
            raise Exception(
                "Power/vertex number mismatch. Expected %ix%i vertices, got %ix%i." %
                (self._vertexNum, self._vertexNum, len(alpha), len(alpha[0]))
                )

        self._alpha = alpha
    ## displacement alpha values
    alpha = property(fget=_getAlpha, fset=_setAlpha)

    ## INTERNAL! Create Side from Key-value dictionary. Used in parsing VMF files.
    #
    # @todo doesn't support offsets
    @staticmethod
    def fromKVD(parent, sideKVD):
        # Create side
        side = Side(parent)
        side.id = int(sideKVD["id"][0])

        # Get plane
        planeList = SDKUtil.getNumbers(sideKVD["plane"][0], float)
        side.plane = [
            planeList[0:3],
            planeList[3:6],
            planeList[6:9]
            ]

        side.material = sideKVD["material"][0]

        # Get texture axes, offset and scale
        uAxisList = SDKUtil.getNumbers(sideKVD["uaxis"][0], float)
        vAxisList = SDKUtil.getNumbers(sideKVD["vaxis"][0], float)
        
        side.textureAxes = []
        side.textureAxes.append(uAxisList[0:3])
        side.textureAxes.append(vAxisList[0:3])
        side.offset = [
            uAxisList[3],
            vAxisList[3]
            ]
        side.scale = [
            uAxisList[4],
            vAxisList[4]
            ]

        # Get rotation, lightmap and smoothing groups
        side.rotation = float(sideKVD["rotation"][0])
        side.lightmapScale = int(sideKVD["lightmapscale"][0])
        side.smoothingGroups = int(sideKVD["smoothing_groups"][0])

        # Get displacement, if present
        if "dispinfo" in sideKVD.keys():
            dispInfoKVD = sideKVD["dispinfo"][0]
            Side._displacementFromKVD(side, dispInfoKVD)

        return side

    @staticmethod
    def _displacementFromKVD(side, dispInfoKVD):
        # Get power and calculate number of vertexes
        side.power = int(dispInfoKVD["power"][0])
        
        # Get startposition
        if "startposition" in dispInfoKVD:
            side._startPosition = SDKUtil.getNumbers(
                dispInfoKVD["startposition"][0], float
            )
        else:
            side._startPosition = [0, 0, 0]

        # Get normals
        normalsKVD = dispInfoKVD["normals"][0]
        normals = []
        for x in range(0, side._vertexNum):
            normals.append(
                SDKUtil.getNumbers(
                    normalsKVD["row%i" % x][0],
                    float
                    )
                )

        # Get distances
        distancesKVD = dispInfoKVD["distances"][0]
        distances = []
        for x in range(0, side.vertexNum):
            distances.append(
                SDKUtil.getNumbers(
                    distancesKVD["row%i" % x][0],
                    float
                    )
                )

        # Generate displacement from normals and distances
        side._displacement = []
        for x in range(0, side.vertexNum):
            column = []
            for y in range(0, side.vertexNum):
                column.append(
                    [distances[y][x] * normals[y][x*3],
                     distances[y][x] * normals[y][x*3 + 1],
                     distances[y][x] * normals[y][x*3 + 2]]
                    )
            side._displacement.append(column)

        # Get the alpha
        alphasKVD = dispInfoKVD["alphas"][0]
        side._alpha = []
        for x in range(0, side.vertexNum):
            side._alpha.append(
                SDKUtil.getNumbers(
                    alphasKVD["row%i" % x][0],
                    float
                    )
                )

    ## @bug doesn't work on some face alignments. Sometimes the texture axis are
    #  parallel with the normal, resulting in bad textures and lighting.
    def _findNearestAxes(self):
        a = (
            self.plane[1][0] - self.plane[0][0],
            self.plane[1][1] - self.plane[0][1],
            self.plane[1][2] - self.plane[0][2]
            )

        b = (
            self.plane[2][0] - self.plane[0][0],
            self.plane[2][1] - self.plane[0][1],
            self.plane[2][2] - self.plane[0][2]
            )

        #cross product results in (non-unit) normal vector
        i = abs(a[1]*b[2] - a[2]*b[1])
        j = abs(a[2]*b[0] - a[0]*b[2])
        k = abs(a[0]*b[1] - a[1]*b[0])

        if k > j and k > i: #Up/down
            return [
                [1,0,0],
                [0,-1,0]
                ]
        elif i > j and i > k: #East/west
            return [
                [0,1,0],
                [0,0,-1]
                ]
        else: # North/south
            return [
                [1,0,0],
                [0,0,-1]
                ]

    ## INTERNAL! export to key-value list format. Used in saving VMF files
    def toKVL(self):
        sideKVL = KeyValueList()
        sideKVL.add("id", str(self.id))
        sideKVL.add(
            "plane",
            "(%g %g %g) (%g %g %g) (%g %g %g)" %
            (self.plane[0][0], self.plane[0][1], self.plane[0][2],
             self.plane[1][0], self.plane[1][1], self.plane[1][2],
             self.plane[2][0], self.plane[2][1], self.plane[2][2])
            )
        
        sideKVL.add("material", self.material)
        sideKVL.add(
            "uaxis", "[%g %g %g %g] %g" %
            (self.textureAxes[0][0], self.textureAxes[0][1], self.textureAxes[0][2],
             self.offset[0], self.scale[0])
            )
        sideKVL.add(
            "vaxis", "[%g %g %g %g] %g" %
            (self.textureAxes[1][0], self.textureAxes[1][1], self.textureAxes[1][2],
             self.offset[1], self.scale[1])
            )
        
        sideKVL.add("rotation", str(self.rotation))
        sideKVL.add("lightmapscale", str(self.lightmapScale))
        sideKVL.add("smoothing_groups", str(self.smoothingGroups))

        if self._vertexNum != 0:
            dispInfoKVL = KeyValueList()
            dispInfoKVL.add(
                "power",
                str(self.power)
                )
            
            dispInfoKVL.add(
                "startposition",
                "[%g %g %g]" % tuple(self._startPosition)
            )

            offsetsKVL = KeyValueList()
            offsetNormalsKVL = KeyValueList()
            for y in range(0, len(self.displacement[0])):
                offsetsRow = ""
                for x in range(0, len(self.displacement)):
                    offsetsRow += "%g %g %g " % tuple(self.displacement[x][y])
                    
                offsetsKVL.add("row%i" % y, offsetsRow)

            dispInfoKVL.add("offsets", offsetsKVL)
            #dispInfoKVL.add("offset_normals", offsetNormalsKVL)

            alphasKVL = KeyValueList()
            for y in range(0, len(self.alpha)):
                alphaRow = ""
                for x in range(0, len(self.alpha[y])):
                    alphaRow += "%g " % self.alpha[x][y]
                alphasKVL.add("row%i" % y, alphaRow)
            dispInfoKVL.add("alphas", alphasKVL)

            sideKVL.add("dispinfo", dispInfoKVL)

        return sideKVL

    ## transform the side using a transformation matrix
    #
    #  @param matrix a 4x4 transformation matrix
    #  @param materialLock If true, textures are "locked" to the side and are
    #  transformed with it. Hammer calls it texture lock.
    #  @param materialScaleLock If true, textures scale with the side.
    #  @param origin optional transformation origin to override brush origin
    #  @sa Matrix
    def transform(self, matrix, materialLock=False, materialScaleLock=False, origin=None):
        if origin != None:
            self.transform(
                Matrix.fromTranslate(-origin[0], -origin[1], -origin[2]),
                materialLock,
                materialScaleLock
                )
        
        self.plane = [matrix.transformVector(p) for p in self.plane]
        
        #if it is a displacement, transform startPosition and offset data
        if self._vertexNum != 0:
            self._startPosition = matrix.transformVector(self._startPosition)
            offsets = []
            for x in range(len(self._displacement)):
                column = []
                for y in range(len(self._displacement)):
                    column.append(matrix.rotateVector(self._displacement[x][y]))
                offsets.append(column)
            self._displacement = offsets

        if materialLock:
            uAxis = matrix.rotateVector(self.textureAxes[0])
            vAxis = matrix.rotateVector(self.textureAxes[1])

            uMagnitude = math.sqrt(
                uAxis[0]*uAxis[0] +
                uAxis[1]*uAxis[1] +
                uAxis[2]*uAxis[2]
                )
            vMagnitude = math.sqrt(
                vAxis[0]*vAxis[0] +
                vAxis[1]*vAxis[1] +
                vAxis[2]*vAxis[2]
                )

            if materialScaleLock:
                self.scale[0] *= uMagnitude
                self.scale[1] *= vMagnitude

            #normalize
            uAxis = [
                uAxis[0]/uMagnitude,
                uAxis[1]/uMagnitude,
                uAxis[2]/uMagnitude
                ]
            vAxis = [
                vAxis[0]/vMagnitude,
                vAxis[1]/vMagnitude,
                vAxis[2]/vMagnitude
                ]
            
            self.textureAxes = [
                uAxis,
                vAxis
                ]


            #print("Texture axes:", self.textureAxes) ## @fixme was someone in the middle of debugging something?
            x = matrix._matrix[0][3]
            y = matrix._matrix[1][3]
            z = matrix._matrix[2][3]

            self.offset[0] -= ((self.textureAxes[0][0]*x + 
                                self.textureAxes[0][1]*y + 
                                self.textureAxes[0][2]*z)/self.scale[0])%1024
            self.offset[1] -= ((self.textureAxes[1][0]*x + 
                                self.textureAxes[1][1]*y + 
                                self.textureAxes[1][2]*z)/self.scale[1])%1024
        else:
            self.textureAxes = self._findNearestAxes()
        
        if origin != None:
            self.transform(
                Matrix.fromTranslate(origin[0], origin[1], origin[2]),
                materialLock,
                materialScaleLock
                )


## VMF entity output
class Output(object):
    
    ## constructor
    #
    # @param entity entity to give output
    # @param event event that triggers the output
    # @param target target of the output
    # @param _input input to trigger on the target
    # @param parameters parameter to provide the target input or None if the target input doesn't take a parameter
    # @param delay delay in seconds before the target input is triggered after the event occurs
    # @param fireOnce only allow the output to be triggered once
    def __init__(self, entity, event, target, _input, parameters=None, delay=0, fireOnce=False):    
        self.event = event.lower() # @todo ensure entity has this output?
        self.target = target # @todo ensure target exists?
        self.input = _input # @todo ensure target has input?
        self.parameters = parameters # @todo ensure parameter is correct type?
        self.delay = delay
        self.fireOnce = fireOnce
        self.entity = entity
        self.entity.outputs[event].append(self)


## VMF entity
class Entity(object):
    
    ## @todo tidy up
    ## @todo add output/connection interface

    ## constructor
    #
    #  @param parent VMF containing this entity
    #  @param classname name of entity
    #  @param kwargs entity properties can be set in the constructor using
    #  arguments like origin=[x,y,z], model='props/someModel'
    #
    def __init__(self, parent, classname, **kwargs):
        ## VMF containing this entity
        self.parent = parent
        ## class name or type of this entity
        self.classname = classname
        self.parent.entities.append(self)
        
        ## unique node ID
        self.id = parent.generateId()
        
        definition = FGD.getGameFGD(self.parent.gameId)[self.classname]

        ## entity properties
        self.properties = {}
        for parameter in definition.parameters:
            self.properties[parameter.name] = copy.copy(parameter.default)
        
        if not "origin" in self.properties:
            self.properties["origin"] = [0.0, 0.0, 0.0]

        ## outputs to other entities. Used to trigger things, etc.
        self.outputs = {}
        for output in definition.outputs:
            self.outputs[output.name] = []

        ## list of solids associated with this entity. Used if this is a brush
        #  entity.
        self.solids = []

        for key in kwargs:
            self[key] = kwargs[key]

    ## Create a copy
    #
    #  @todo does not change entity outputs - will interfere with anything that uses the same names, like other copies of the prefab
    #
    #  @param parent parent of the copy
    #  @return Entity
    def copy(self, parent):
        new = Entity(parent, self.classname)
        new.properties = dict(self.properties)
        new.outputs = dict(self.outputs)
        for solid in self.solids:
            solid.copy(new)
        return new

    ## Generate unique ID for a Solid associated with this Entity
    def generateId(self):
        return self.parent.generateId()
    
    def getPropertyNames(self):
        return self.properties.keys()

    ## can get the value of entity properties using Entity[propName]
    def __getitem__(self, key):
        return self.properties[key]

    ## can set the value of entity properties using Entity[propName] = newvalue
    def __setitem__(self, key, value):
        if not key in self.properties.keys():
            raise KeyError(key + ' does not exist in ' + self.classname)
        self.properties[key] = value

    ## INTERNAL! Create Entity from key-value dictionary. Used in parsing VMF files.
    @classmethod
    def fromKVD(cls, parent, entityKVD):
        entity = Entity(parent, entityKVD["classname"][0])
        entity.id = int(entityKVD["id"][0])
        
        definition = FGD.getGameFGD(parent.gameId)[entityKVD["classname"][0]]
        for parameter in definition.parameters:
            if parameter.name in entityKVD.keys():
                if parameter.type == FGD.VOID:
                    entity.properties[parameter.name] = None
                elif parameter.type == FGD.INTEGER:
                    try: # @fixme why is this here?
                        entity.properties[parameter.name] = int(entityKVD[parameter.name][0])
                    except ValueError:
                        entity.properties[parameter.name] = float(entityKVD[parameter.name][0])
                elif parameter.type == FGD.FLOAT:
                    entity.properties[parameter.name] = float(entityKVD[parameter.name][0])
                elif parameter.type == FGD.INTEGER_LIST:
                    entity.properties[parameter.name] = SDKUtil.getNumbers(
                        entityKVD[parameter.name][0], int
                    )
                elif parameter.type in (FGD.VECTOR, FGD.FLOAT_LIST, FGD.ANGLE):
                    entity.properties[parameter.name] = SDKUtil.getNumbers(
                        entityKVD[parameter.name][0], float
                    )
                ## @todo FIXME unreachable
                ## @todo convert angle order to match rest of LGF (XYZ order) (it probably requires trig - naive method below won't work)
                #elif parameter.type == FGD.ANGLE: 
                #    # Convert from YZX to XYZ
                #    angle = SDKUtil.getNumbers(
                #        entityKVD[parameter.name][0], float
                #    )
                #    entity.properties[parameter.name] = [angle[2], angle[0], angle[1]]
                
                # Right handed
                # X = Roll = +counter-clockwise/-clockwise
                # Y = Pitch = +counter-clockwise/-clockwise
                # Z = Yaw = +counter-clockwise/-clockwise
                elif parameter.type == FGD.AXIS:
                    floats = SDKUtil.getNumbers(
                        entityKVD[parameter.name][0],
                        float
                        )
                    assert len(floats) > 0
                    assert len(floats)%3 == 0
                    if len(floats) == 3:
                        entity.properties[parameter.name] = floats
                    else:
                        entity.properties[parameter.name] = []
                        for x in range(0, int(len(floats)/3)):
                            entity.properties[parameter.name].append(floats[x:x+3])
                elif parameter.type == FGD.CHOICE:
                    try:
                        entity.properties[parameter.name] = int(entityKVD[parameter.name][0])
                    except ValueError:
                        if entityKVD[parameter.name][0] in tuple(parameter.choices.values()): # Is the mapping reversed for some reason?
                            selections = {v:k for k, v in parameter.choices.items()} # Inverse of choices
                            entity.properties[parameter.name] = selections[entityKVD[parameter.name][0]]
                        else:
                            entity.properties[parameter.name] = entityKVD[parameter.name][0]
                else:
                    entity.properties[parameter.name] = entityKVD[parameter.name][0]
            else:
                entity.properties[parameter.name] = parameter.default
        
          
        if "origin" in entityKVD.keys():
            entity.properties["origin"] = SDKUtil.getNumbers(
                entityKVD["origin"][0], float
            )
        
        if "connections" in entityKVD.keys():
            connections = entityKVD["connections"][0]
            for key in connections.keys():
                for connection in connections[key]:
                    target, _input, parameter, delay, fireOnce = connection.split(",")
                    
                    fireOnce = fireOnce == 1
                    
                    # If possible, convert the parameter to int, float, or None
                    # (otherwise leave the parameter as a str)
                    if len(parameter) == 0:
                        parameter = None
                    else:
                        try:
                            parameter = int(parameter)
                        except ValueError:
                            try:
                                parameter = float(parameter)
                            except ValueError:
                                pass
                    
                    Output(entity, key.lower(), target, _input, parameter, delay, fireOnce)
        
        if "solid" in entityKVD.keys():
            for solidKVD in entityKVD["solid"]:
                if type(solidKVD) != str:
                    solid = Solid.fromKVD(entity, solidKVD)

    ## INTERNAL!! export to key-value list format. Used in saving VMF files
    def toKVL(self):
        entityKVL = KeyValueList()
        entityKVL.add("id", str(self.id))
        entityKVL.add("classname", self.classname)
        
        if "origin" in self.properties:
            entityKVL.add(
                "origin",
                "%g %g %g" % tuple(self.properties["origin"])
                )
        
        definition = FGD.getGameFGD(self.parent.gameId)[self.classname]
        for parameter in definition.parameters:
            if parameter.name == "origin":
                pass
            elif parameter.type in (FGD.INTEGER, FGD.FLOAT):
                entityKVL.add(
                    parameter.name,
                    "%g " % self.properties[parameter.name]
                    )
            elif parameter.type in (FGD.INTEGER_LIST, FGD.VECTOR, FGD.FLOAT_LIST, FGD.ANGLE):
                valueStr = ""
                for value in self.properties[parameter.name]:
                    valueStr += "%g " % value
                
                entityKVL.add(
                    parameter.name,
                    valueStr
                    )
            ## @todo FIXME unreachable
            ## @todo convert angle order to match rest of LGF (XYZ order) (it probably requires trig - naive method below won't work)
            #elif parameter.type == FGD.ANGLE:
            #    # Convert from XYZ to YZX
            #    entityKVL.add(
            #        parameter.name,
            #        "%g %g %g" % (self.properties[parameter.name][1],
            #                      self.properties[parameter.name][2],
            #                      self.properties[parameter.name][0])
            #        )
            elif parameter.type == FGD.AXIS:                
                valueStr = ""
                if type(self.properties[parameter.name][0]) == list:
                    for valueList in self.properties[parameter.name][:-1]:
                        for value in valueList[:-1]:
                            valueStr += "%g " % value
                        valueStr += str(valueList[-1])
                        valueStr += ", "
                        
                    for value in self.properties[parameter.name][-1][:-1]:
                        valueStr += "%g " % value
                    valueStr += str(self.properties[parameter.name][-1][-1])
                else:
                    for value in self.properties[parameter.name]:
                        valueStr += "%g " % value
                
                entityKVL.add(
                    parameter.name,
                    valueStr
                    )
            elif self.properties[parameter.name] != None and len(str(self.properties[parameter.name])) > 0:
                entityKVL.add(
                    parameter.name,
                    str(self.properties[parameter.name])
                    )
        
        connectionsKVL = KeyValueList()
        for output in self.outputs.keys():
            for connection in self.outputs[output]:
                if connection.parameters == None:
                    parameters = ""
                else:
                    parameters = str(connection.parameters)
                
                value = "%s,%s,%s,%s,%s" % (
                    connection.target,
                    connection.input,
                    parameters,
                    connection.delay,
                    int(connection.fireOnce)
                    )
                
                connectionsKVL.add(output, value)
        entityKVL.add("connections", connectionsKVL)
        
        for solid in self.solids:
            solidKVL = solid.toKVL()
            entityKVL.add("solid", solidKVL)
        
        return entityKVL
    
    ## transform the entity using a transformation matrix
    #
    #  @todo test (especially that all entity parameters are transformed correctly)
    #
    #  @param transform a 4x4 transformation matrix
    #  @param materialLock If true, textures are transformed with the solids (if any).
    #  (Hammer calls it texture lock.)
    #  @param materialScaleLock If true, textures scale with the solids (if any).
    #  @param origin optional transformation origin to override entity origin
    #
    #  @sa Matrix
    def transform(self, transform, materialLock=False, materialScaleLock=False, origin=None):
        if origin == None:
            origin = self.properties["origin"]
        #transform solids
        for solid in self.solids:
            solid.transform(transform, materialLock, materialScaleLock, origin)
        #transform spatial properties
        self.properties["origin"] = transform.transformVector(self.properties["origin"])
        for parameter in FGD.getGameFGD(self.parent.gameId)[self.classname].parameters:
            if parameter.name == "origin":
                pass
            elif parameter.name in self.properties:
                if parameter.type is FGD.VECTOR:
                    self.properties[parameter.name] = transform.transformVector(self.properties[parameter.name])
                elif parameter.type is FGD.AXIS:
                    for x in range(len(self.properties[parameter.name])):
                        self.properties[parameter.name][x] = transform.transformVector(self.properties[parameter.name][x])
                elif parameter.type is FGD.ANGLE:
                    self.properties[parameter.name] = transform.transformAngles(self.properties[parameter.name])

## A special four by four matrix for transformations such as scaling, rotation,
#  and translation.
#
# Angle related helper functions use right handed XYZ Euler angles.
class Matrix:

    # Right handed
    # X = Roll = +counter-clockwise/-clockwise
    # Y = Pitch = +counter-clockwise/-clockwise
    # Z = Yaw = +counter-clockwise/-clockwise

    ## Constructor. Creates identity matrix. If applied, this transformation
    #  matrix does nothing.
    def __init__(self):
        self._matrix = [
            [1.0,0.0,0.0,0.0],
            [0.0,1.0,0.0,0.0],
            [0.0,0.0,1.0,0.0],
            [0.0,0.0,0.0,1.0]
            ]

    ## Create transformation matrix that scales.
    #
    #  @param x scaling factor on x axis
    #  @param y scaling factor on y axis
    #  @param z scaling factor on z axis
    #
    #  @return Matrix
    @staticmethod
    def fromScale(x, y, z):
        matrix = Matrix()
        
        matrix._matrix = [
            [float(x),0.0,0.0,0.0],
            [0.0,float(y),0.0,0.0],
            [0.0,0.0,float(z),0.0],
            [0.0,0.0,0.0,1.0]
            ]

        return matrix

    ## Create transformation matrix that translates, or moves.
    #
    #  @param x offset on x axis
    #  @param y offset on y axis
    #  @param z offset on z axis
    #
    #  @return Matrix
    @staticmethod
    def fromTranslate(x, y, z):
        matrix = Matrix()
        
        matrix._matrix = [
            [1.0,0.0,0.0,float(x)],
            [0.0,1.0,0.0,float(y)],
            [0.0,0.0,1.0,float(z)],
            [0.0,0.0,0.0,1.0]
            ]

        return matrix

    ## Create transformation matrix that rotates.
    #
    #  The rotation order is X,Y,Z. If the rotation doesn't come out as expected
    #  you likely used a different rotation order. Find the equivalent rotation
    #  using this order, or break the rotation into multiple rotate transforms.
    #  @n@n
    #  Right handed coordinate system.@n
    #  X = Roll = +counter-clockwise/-clockwise@n
    #  Y = Pitch = +counter-clockwise/-clockwise@n
    #  Z = Yaw = +counter-clockwise/-clockwise
    #
    #  @param x radians to rotate on x axis (roll)
    #  @param y radians to rotate on y axis (pitch)
    #  @param z radians to rotate on z axis (yaw)
    #
    #  @return Matrix
    @staticmethod
    def fromAngles(x, y, z):
        matrix = Matrix()

        cx = math.cos(x)
        sx = math.sin(x)
        cy = math.cos(y)
        sy = math.sin(y)
        cz = math.cos(z)
        sz = math.sin(z)
        
        ## @todo optimize
        
        matrix._matrix = [
            [cy*cz, -cy*sz, sy, 0.0],
            [cx*sz + cz*sx*sy, cx*cz - sx*sy*sz, -cy*sx, 0.0],
            [sx*sz - cx*cz*sy, cz*sx + cx*sy*sz, cx*cy, 0.0],
            [0.0, 0.0, 0.0, 0.0]
            ]

        return matrix

    ## Create transformation matrix that rotates around x axis.
    #
    #  X = Roll = +counter-clockwise/-clockwise
    #
    #  @param x radians to rotate
    #  @return Matrix
    @staticmethod
    def fromXAngle(x):
        matrix = Matrix()
        
        matrix._matrix = [
            [1.0,0.0,0.0,0.0],
            [0.0,math.cos(x),-math.sin(x),0.0],
            [0.0,math.sin(x),math.cos(x),0.0],
            [0.0,0.0,0.0,1.0]
            ]

        return matrix

    ## Create transformation matrix that rotates around y axis.
    #
    #  Y = Pitch = +counter-clockwise/-clockwise
    #
    #  @param y radians to rotate
    #  @return Matrix
    @staticmethod
    def fromYAngle(y):
        matrix = Matrix()
        
        matrix._matrix = [
            [math.cos(y),0.0,-math.sin(y),0.0],
            [0.0,1.0,0.0,0.0],
            [math.sin(y),0.0,math.cos(y),0.0],
            [0.0,0.0,0.0,1.0]
            ]

        return matrix

    ## Create transformation matrix that rotates around z axis.
    #
    #  Z = Yaw = +counter-clockwise/-clockwise
    #
    #  @param z radians to rotate
    #  @return Matrix
    @staticmethod
    def fromZAngle(z):
        matrix = Matrix()
        
        matrix._matrix = [
            [math.cos(z),-math.sin(z),0.0,0.0],
            [math.sin(z),math.cos(z),0.0,0.0],
            [0.0,0.0,1.0,0.0],
            [0.0,0.0,0.0,1.0]
            ]

        return matrix

    ## Multiplication operator
    #
    #  Uses matrix multiplication. A*B results in a matrix equivalent to
    #  transforming by A and then by B.
    #
    #  @param other other matrix to multiply by
    #  @return result of multiplication
    def __mul__(self, other):
        result = Matrix()
        for x in range(4):
            for y in range(4):
                v = [self._matrix[y][i]*other._matrix[i][x] for i in range(4)]
                result._matrix[y][x] = sum(v)
        return result

    ## Apply matrix transformation to texture axis
    #
    #  @param axis texture axis
    #  @return modified texture axis
    def rotateVector(self, axis):
        x = self._matrix[0][0]*axis[0] + \
            self._matrix[0][1]*axis[1] + \
            self._matrix[0][2]*axis[2]
        y = self._matrix[1][0]*axis[0] + \
            self._matrix[1][1]*axis[1] + \
            self._matrix[1][2]*axis[2]
        z = self._matrix[2][0]*axis[0] + \
            self._matrix[2][1]*axis[1] + \
            self._matrix[2][2]*axis[2]
        return [x,y,z]

    ### Apply only translation part of matrix transformation to a point
    ##
    ##  @param point 3D coordinate to translate
    ##  @return modified 3D coordinate
    #def translateVector(self, point):
    #    x = point[0] + self._matrix[0][3]
    #    y = point[1] + self._matrix[1][3]
    #    z = point[2] + self._matrix[2][3]
    #    return [x,y,z]

    ## Apply full matrix transformation to point
    #
    #  @param point 3D coordinate to transform
    #  @return modified 3D coordinate
    def transformVector(self, point):
        x = self._matrix[0][0]*point[0] + \
            self._matrix[0][1]*point[1] + \
            self._matrix[0][2]*point[2] + \
            self._matrix[0][3]
        y = self._matrix[1][0]*point[0] + \
            self._matrix[1][1]*point[1] + \
            self._matrix[1][2]*point[2] + \
            self._matrix[1][3]
        z = self._matrix[2][0]*point[0] + \
            self._matrix[2][1]*point[1] + \
            self._matrix[2][2]*point[2] + \
            self._matrix[2][3]
        return [x,y,z]
    
    
    ## Apply full matrix transformation to entity angles
    #
    #  @param angles entity "angles" parameter value (in yzx order)
    #  @return modified angles parameter
    def transformAngles(self, angles):
        previous = Matrix.fromAngles(
            math.radians(angles[2]),
            math.radians(angles[0]),
            math.radians(angles[1]))
        matrix = previous * self
        
        #work out angles from our matrix
        #if we ignore the last row and column, it is a rotation matrix (...I think)
        #we can figure out the angles from this.
        
        #entity angles are stored in YZX order, but transformed in ZYX order.
        #composition:
        #http://en.wikipedia.org/wiki/Euler_angles#Matrix_orientation
        #decomposition:
        #http://www.geometrictools.com/Documentation/EulerAngles.pdf

        ## @todo this is broken on rotations around z axis, especially 90 and -90 degrees
        
        # decompose transformation into ZYX order euler angles
        m = lambda x : matrix._matrix[int(x/10)][x%10]
        x = 0
        y = 0
        z = 0
        
        if m(2) < 1:
            if m(2) > -1:
                y = math.asin(m(2))
                x = math.atan2(-m(12),m(22))
                z = math.atan2(-m(1),m(0))
            else: # m(02) == -1
                # not unique: z-x = atan(m(10),m(11))
                y = -math.pi/2
                x = -math.atan2(m(10),m(11))
                z = 0
        else: #m(02) == 1
            #not unique: z+x = atan(m(10),m(11))
            y = math.pi/2
            x = math.atan2(m(10), m(11))
            z = 0
        
        result = [
            math.degrees(y),
            math.degrees(z),
            math.degrees(x)
        ]
        return result
