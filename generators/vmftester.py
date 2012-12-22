import random

from generators.generator import Generator
from generators.testpattern import *
from gameids import *
from formats.vmf import *

## Generator that runs tests on the native VMF format module
#
class TestVMF(Generator):
    ## Name
    name = "Native VMF Test"

    ## Description
    description = "Tests all of the features of the native vmf module. This does not generate a playable map."

    ## Supported format
    formats = [VMF]

    ## Supported games
    games = [
        HL2,
        HL2EP1,
        HL2EP2,
        HL2DM,
        P1,
        P2,
        L4D1,
        L4D2,
        CSS,
        TF2,
        GMOD
        ]

    ## Configuration GUI
    configGUI = TestConfig

    ## Constructor
    def __init__(self, parent):
        Generator.__init__(self, parent)
        ## Heirarchy of test objects
        self.tests = TestCategory('All Tests', [
            TestCategory('Solids', [
                TestCase(self, 'Solid.fromPlanes()', self._testFromPlanes),
                TestCase(self, 'Solid.fromNormals()', self._testFromNormals),
                TestCase(self, 'Solid.fromMinMax()', self._testFromMinMax),
                TestCase(self, 'Solid.fromCylinder()', self._testFromCylinder),
                TestCase(self, 'Solid.fromConvexPolygon()', self._testFromConvexPolygon),
                TestCase(self, 'Solid.fromRevolution()', self._testFromRevolution),
                TestCase(self, 'Solid.fromSphere()', self._testFromSphere)
                ]),
            TestCategory('Transformations', [
                TestCase(self, 'Solid Translation', self._testTranslation),
                TestCase(self, 'Solid Rotation', self._testRotation),
                TestCase(self, 'Solid Scaling', self._testScaling)
                ]),
            TestCategory('Displacements', [
                TestCase(self, 'Solid.fromHeightMap()', self._testFromHeightMap),
                TestCase(self, 'Solid.fromHeightFunction()', self._testFromHeightFunction)
                ])
            ])

    ## Generate map
    def generate(self, gameID):
        ## ID of game
        self.gameID = gameID
        ## high level VMFmap instance
        self.map = self.parent.getMap()
        ## low level VMF instance
        self.native = self.map.getNative()
        self.setProgress(0.0)
        # create hl2dm spawn (or else it will crash)
        if self.gameID == HL2DM:
            Entity(self.native,
                   'info_player_deathmatch')
        self.tests.run()
        self.map.save()
        self.setProgress(1.0)
        self.setStatus('Done Running Tests')
        
    @staticmethod
    def _planeCube(t,b,n,s,e,w):
        planes = [
            [[0,0,t],[1,0,t],[1,-1,t]], #top
            [[0,0,b],[1,0,b],[1,1,b]], #bottom
            [[0,n,0],[1,n,0],[1,n,1]], #north side
            [[0,s,0],[1,s,0],[1,s,-1]], #south side
            [[e,0,0],[e,1,0],[e,1,-1]], #east side
            [[w,0,0],[w,1,0],[w,1,1]] #west side
            ]
        return planes
    
    @staticmethod
    def _normalCube(t,b,n,s,e,w):
        points = [[0,0,t],[0,0,b],[0,n,0],[0,s,0],[e,0,0],[w,0,0]]
        normals = [[0,0,1],[0,0,-1],[0,1,0],[0,-1,0],[1,0,0],[-1,0,0]]
        return points, normals

    @staticmethod
    def _randomCube():
        x = random.randint(-4096,4096)
        y = random.randint(-4096,4096)
        z = random.randint(0,4096)
        x2 = x+random.randint(16,256)
        y2 = y+random.randint(16,256)
        z2 = z+random.randint(16,256)
        return z2,z,y2,y,x2,x
        
    def _testFromPlanes(self):
        # make a room to contain the other tests
        d = 1024*4 #room is 2d by 2d and d high.
        #floor
        Solid.fromPlanes(self.native,
                         self._planeCube(-32,-48,d+16,-d-16,d+16,-d-16),
                         self.map.textureFloor
                         )
        #ceiling
        Solid.fromPlanes(self.native,
                         self._planeCube(d+16,d,d+16,-d-16,d+16,-d-16),
                         'tools/toolsskybox'
                         )
        #north
        Solid.fromPlanes(self.native,
                         self._planeCube(d,-32,d+16,d,d+16,-d-16),
                         self.map.textureWall
                         )
        #south
        Solid.fromPlanes(self.native,
                         self._planeCube(d,-32,-d,-d-16,d+16,-d-16),
                         self.map.textureWall
                         )
        #east
        Solid.fromPlanes(self.native,
                         self._planeCube(d,-32,d,-d,d+16,d),
                         self.map.textureWall
                         )
        #west
        Solid.fromPlanes(self.native,
                         self._planeCube(d,-32,d,-d,-d,-d-16),
                         self.map.textureWall
                         )

    def _testFromNormals(self):
        sides = 16
        radius = 512
        normals = []
        points = []
        materials = []
        #bottom
        points.append([0,0,-32])
        normals.append([0,0,-1])
        materials.append(self.map.textureConcrete)
        #top
        points.append([0,0,0])
        normals.append([0,0,1])
        materials.append(self.map.textureConcrete)
        #sides
        step = math.pi*2/sides
        halfstep = math.pi/sides
        for i in range(sides):
            #side
            points.append([math.sin(i*step)*radius, math.cos(i*step)*radius, 0])
            normals.append([math.sin(i*step), math.cos(i*step), 0])
            materials.append(self.map.textureMetal)
            #bevel
            points.append([math.sin(i*step + halfstep)*(radius + 8), math.cos(i*step + halfstep)*(radius + 8), -32])
            normals.append([math.sin(i*step + halfstep), math.cos(i*step + halfstep), 1])
            materials.append(self.map.textureTile)
        Solid.fromNormals(self.native, points, normals, materials)

    def _testFromMinMax(self):
        for i in range(700):
            x = random.randint(-4096,4096)
            y = random.randint(-4096,4096)
            z = random.randint(1120,2048)
            x2 = x+random.randint(32,512)
            y2 = y+random.randint(32,512)
            z2 = 4096
            Solid.fromMinMax(self.native, [x,y,z], [x2,y2,z2], self.map.textureMetal)

    def _testFromCylinder(self):
        ## list of cylindrical columns to copy/rotate later
        self.columns = []
        for i in range(7):
            self.columns.append(
                Solid.fromCylinder(self.native, [0, i*64 + 64, -32], 16, 64, i+3, self.map.textureWood)
                )
        
    def _testFromConvexPolygon(self):
        sides = 16
        radius = 512
        polygon = []
        step = math.pi*2/sides
        for i in range(sides):
            polygon.append([math.sin(i*step)*radius, math.cos(i*step)*radius])
        Solid.fromConvexPolygon(self.native, [0,0,256], polygon, 16, self.map.textureConcrete)
        
    def _testFromRevolution(self):
        sides = 8
        radius = 480
        profile = [[0,0]]
        step = math.acos(0.5)/sides
        for i in range(sides-1):
            z = math.sin(i*step)*radius*2
            r = math.cos(i*step)*radius*2 - radius
            profile.append([r,z])
        profile.append([0,math.sin(math.acos(0.5))*radius*2])
        Solid.fromRevolution(self.native, [0,0,272], profile, sides, self.map.textureConcrete)
    
    def _testFromSphere(self):
        for i in range(7):
            Solid.fromSphere(self.native, [0, i*64 + 64, 48], 16, i+3, self.map.textureWood)

    def _testTranslation(self):
        base = Solid.fromMinMax(self.native, [960,0,64], [1088, 8, 192], self.map.textureTile)
        steps = 32
        step = math.pi*2/steps
        for i in range(steps):
            new = base.copy()
            matrix = Matrix.fromTranslate(math.sin(i*step)*64, i*8+8, math.cos(i*step)*64)
            new.transform(matrix, True, True)
    
    def _testRotation(self):
        try:
            assert len(self.columns) > 1
        except:
            pass
        else:
            for i in range(len(self.columns)):
                step = math.pi*2/(i + 3)
                for n in range(1, i + 3):
                    copy = self.columns[i].copy()
                    matrix = Matrix.fromZAngle(n*step)
                    copy.transform(matrix, True)
        steps = 24
        step = math.pi*2/steps
        radius = 128
        move = Matrix.fromTranslate(0, 1024, 256)
        for i in range(steps):
            block = Solid.fromMinMax(self.native, [radius, -16, -16], [radius+16, 16, 16], self.map.textureTile)
            rotate = Matrix.fromYAngle(i*step)
            block.transform(rotate, True, True)
            block.transform(move, True, True)
            block = Solid.fromMinMax(self.native, [-16, radius+16, -16], [16, radius+32, 16], self.map.textureTile)
            rotate = Matrix.fromXAngle(i*step)
            block.transform(rotate, True, True)
            block.transform(move, True, True)
            block = Solid.fromMinMax(self.native, [-16, radius+32, -16], [16, radius+48, 16], self.map.textureTile)
            rotate = Matrix.fromZAngle(i*step)
            block.transform(rotate, True, True)
            block.transform(move, True, True)
    
    def _testScaling(self):
        steps = 32
        step = math.pi*2/steps
        for i in range(steps):
            new = Solid.fromMinMax(self.native, [-64, i*8, -64], [64, i*8 + 8, 64], self.map.textureTile)
            matrix = Matrix.fromScale(1 + math.sin(i*step)*0.8, 1, 1 + math.cos(i*step)*0.8)
            new.transform(matrix, True, True)
            matrix = Matrix.fromTranslate(-1024, 0, 128)
            new.transform(matrix, True, True)

    def _testFromHeightMap(self):
        innerRadius = 528
        lower = -48
        upper = 64
        period = 512
        power = 4

        vertexNum = power*power + 1
        magnitude = (upper-lower)/2.0
        size = 1024 #dimension of displacement
        step = size/(vertexNum-1)
        for dy in range(-4096, 4096, size):
            for dx  in range(-4096, 4096, size):
                heightMap = []
                for x in range(0, size+1, int(step)):
                    column = []
                    for y in range(0, size+1, int(step)):
                        tx = dx + x
                        ty = dy + y
                        d = math.sqrt(tx*tx + ty*ty)
                        if (d < innerRadius):
                            height = 0
                        else:
                            d -= innerRadius
                            height = -math.cos(2*math.pi*d/period)*magnitude + magnitude
                        column.append(lower+height)
                    heightMap.append(column)
                Solid.fromHeightMap(self.native, (dx,dy,-64), (size,size,32), heightMap, self.map.textureStone)

    @staticmethod
    def _heightFunction(x, y):
        center = (0, -512)
        radius = 128
        height = 92
        base = -36
        distance = math.sqrt((center[0]-x)**2 + (center[1]-y)**2)
        if distance > radius:
            return base
        else:
            return (math.cos(math.pi * distance/radius)+1) * height/2 + base

    def _testFromHeightFunction(self):
        power = 4
        center = (0, -512)
        
        #put a block in the hole in the middle
        Solid.from3DRect(self.native, (center[0]-32,center[1]-32,-32), (64,64,80), self.map.textureWall)
        
        Solid.fromHeightFunction(
            self.native,
            power,
            [
                [center[0]-128,center[1]-128],
                [center[0]-32,center[1]-32],
                [center[0]+32,center[1]-32],
                [center[0]+128,center[1]-128]
                ],
            TestVMF._heightFunction,
            self.map.textureStone)
        Solid.fromHeightFunction(
            self.native,
            power,
            [
                [center[0]-128,center[1]-128],
                [center[0]-128,center[1]+128],
                [center[0]-32,center[1]+32],
                [center[0]-32,center[1]-32]
                ],
            TestVMF._heightFunction,
            self.map.textureStone)
        Solid.fromHeightFunction(
            self.native,
            power,
            [
                [center[0]-32,center[1]+32],
                [center[0]-128,center[1]+128],
                [center[0]+128,center[1]+128],
                [center[0]+32,center[1]+32]
                ],
            TestVMF._heightFunction,
            self.map.textureStone)
        Solid.fromHeightFunction(
            self.native,
            power,
            [
                [center[0]+32,center[1]-32],
                [center[0]+32,center[1]+32],
                [center[0]+128,center[1]+128],
                [center[0]+128,center[1]-128]
                ],
            TestVMF._heightFunction,
            self.map.textureStone)