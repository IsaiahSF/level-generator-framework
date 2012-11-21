import random, math

from generators.generator import Generator
from generators.testpattern import *
from gameids import *

## Tests features of Map interface for all formats and all games
class TestMap(Generator):
    ## Name
    name = "Universal Map Test"

    ## Description
    description = "Tests all of the Map features"

    ## Supported formats
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

    ##Constructor
    def __init__(self, parent):
        Generator.__init__(self, parent)
        ## category containing all tests
        self.tests = TestCategory('All Tests', [
            TestCategory('Entities', [
                TestCase(self, 'Map.playerStart()', self._testPlayerStart),
                TestCase(self, 'Map.levelChangePoint()', self._testLevelChangePoint, False),
                TestCase(self, 'Map.item()', self._testItem),
                TestCase(self, 'Map.weapon()', self._testWeapon),
                TestCase(self, 'Map.ammunition()', self._testAmmunition),
                TestCase(self, 'Map.health()', self._testHealth),
                TestCase(self, 'Map.armor()', self._testArmor),
                TestCase(self, 'Map.enemy()', self._testEnemy),
                TestCase(self, 'Map.light()', self._testLight),
                TestCase(self, 'Map.sun()', self._testSun)
                ]),
            TestCategory('Geometry', [
                TestCase(self, 'Map.brushRectangular()', self._testBrushRectangular),
                TestCase(self, 'Map.makeWater()', self._testMakeWater),
                TestCase(self, 'Map.brushCylinder()', self._testBrushCylinder),
                TestCase(self, 'Map.brushCone()', self._testBrushCone),
                TestCase(self, 'Map.brushSphere()', self._testBrushSphere),
                TestCase(self, 'Map.texture()', self._testTexture),
                TestCase(self, 'Map.textureSky()', self._testTextureSky),
                TestCase(self, 'Map.heightDisplacement()', self._testHeightDisplacement, False),
                TestCase(self, 'Map.prefab()', self._testPrefab, False)
                ]),
            TestCategory('Cutting, Splitting', [
                TestCase(self, 'Map.cut()', self._testCut, False),
                TestCase(self, 'Map.split()', self._testSplit, False)
                ]),
            TestCategory('Transformation, Copying', [
                TestCase(self, 'Map.translate()', self._testTranslate),
                TestCase(self, 'Map.rotate()', self._testRotate),
                TestCase(self, 'Map.scale()', self._testScale)
                ]),
            TestCategory('Utility Builders', [
                TestCase(self, 'Map.arch()', self._testArch),
                TestCase(self, 'Map.ladder()', self._testLadder),
                TestCase(self, 'Map.stairs()', self._testStairs),
                TestCase(self, 'Map.spiralStairs()', self._testSpiralStairs, False),
                TestCase(self, 'Map.lift()', self._testLift, False),
                TestCase(self, 'Map.slidingDoor()', self._testSlidingDoor, False),
                TestCase(self, 'Map.key()', self._testKey, False)
                ]),
            ], horizontal=True)

    ## Generate map
    def generate(self, gameID):
        ## ID of game
        self.gameID = gameID
        ## high level VMFmap instance
        self.map = self.parent.getMap()
        self.setProgress(0.0)
        ## list of locations to make columns
        self.columns = []
        for i in range(200):
            x = random.randint(-1024, 1024)
            y = random.randint(-1024, 1024)
            if abs(x)+abs(y) > 512:
                self.columns.append([x, y, random.randint(3,9)])
        self.tests.run()
        self.map.save()
        self.setProgress(1.0)
        self.setStatus('Done Running Tests')

    def _testPlayerStart(self):
        self.map.playerStart((0,0,272), random.randint(0,360))
    def _testLevelChangePoint(self):
        raise NotImplementedError
    def _testItem(self):
        for i in range(-64,64,32):
            self.map.item((i,64,416))
    def _testWeapon(self):
        ##ammo for ammunition test
        self.ammo = self.map.weapon((-96,96,272), 1)
    def _testAmmunition(self):
        try:
            type(self.ammo)
        except:
            self.listenerWrite('Map.ammunition() test requires Map.weapon() to be run.\n')
        else:
            self.map.ammunition((96, 96, 272), self.ammo)
    def _testHealth(self):
        self.map.health((-96,-96,272), 99)
    def _testArmor(self):
        self.map.armor((96,-96,272), 99)
    def _testEnemy(self):
        for i in range(-64,64,32):
            self.map.enemy((i,0,416), 1)
            self.map.enemy((i,-64,416), 1)
    def _testLight(self):
        self.map.light((-96,-96,392), (255,0,0), 100)
        self.map.light((96,-96,392), (0,255,0), 100)
        self.map.light((-96,96,392), (0,0,255), 100)
        self.map.light((96,96,392), (255,255,0), 100)
    def _testSun(self):
        self.map.sun((170,70), (255,255,255), 200)
                
    def _testBrushRectangular(self):
        #make test room
        ## brushes representing the ground
        self.ground = self.map.brushRectangular((-1040, -1040, -16), (1040, 1040, 0), self.map.textureFloor)
        ## brushes representing the skybox
        self.skybox = [
            self.map.brushRectangular((-1040, -1040, 1024), (1040, 1040, 1040), self.map.textureFloor),
            self.map.brushRectangular((-1040, -1040, 0), (-1024, 1040, 1024), self.map.textureFloor),
            self.map.brushRectangular((1040, -1040, 0), (1024, 1040, 1024), self.map.textureFloor), 
            self.map.brushRectangular((-1024, 1024, 0), (1024, 1040, 1024), self.map.textureFloor),  
            self.map.brushRectangular((-1024, -1024, 0), (1024, -1040, 1024), self.map.textureFloor),  
            ]
        self.map.brushRectangular((-128,-128,256), (128,128,272), self.map.textureTile)
        self.map.brushRectangular((-128,-128,400), (128,128,416), self.map.textureTile)
        self.map.brushRectangular((-128,-128,272), (-32,-112,400), self.map.textureTile)
        self.map.brushRectangular((128,-128,272), (32,-112,400), self.map.textureTile)
        self.map.brushRectangular((-128,128,272), (-32,112,400), self.map.textureTile)
        self.map.brushRectangular((128,128,272), (32,112,400), self.map.textureTile)
        self.map.brushRectangular((-128,-112,272), (-112,-32,400), self.map.textureTile)
        self.map.brushRectangular((-128,112,272), (-112,32,400), self.map.textureTile)
        self.map.brushRectangular((128,-112,272), (112,-32,400), self.map.textureTile)
        self.map.brushRectangular((128,112,272), (112,32,400), self.map.textureTile)
    def _testMakeWater(self):
        self.map.makeWater((-1024, -1024, 0), (1024, 1024, 28))
    def _testBrushCylinder(self):
        for i in self.columns:
            self.map.brushCylinder((i[0],i[1],0), 16, 128, i[2], (0,0,1), self.map.textureMetal, True)
    def _testBrushCone(self):
        for i in self.columns:
            self.map.brushCone((i[0],i[1],128), 16, 32, i[2], (0,0,1), self.map.textureMetal, True)
    def _testBrushSphere(self):
        for i in self.columns:
            self.map.brushSphere((i[0],i[1],176), 16, i[2], self.map.textureMetal, True)
    def _testTexture(self):
        b = self.map.brushRectangular((-64,-64,0),(64,64,16), self.map.textureCeiling)
        self.map.texture(b, self.map.textureConcrete)
    def _testTextureSky(self):
        try:
            assert len(self.skybox) > 0
        except:
            self.listenerWrite('Map.textureSky() test requires Map.brushRectangular() to be run.\n')
        else:
            for brush in self.skybox:
                self.map.textureSky(brush)
    def _testHeightDisplacement(self):
        raise NotImplementedError
    def _testPrefab(self):
        raise NotImplementedError


    def _testCut(self):
        raise NotImplementedError
    def _testSplit(self):
        raise NotImplementedError

    def _testTranslate(self):
        steps = 8
        height = 128/steps
        brush = self.map.brushCylinder((0,0,128), 32, height, 8, (0,0,1), self.map.textureWood)
        ## slices of support column. Later scaled.
        self.columnSlices = [[brush]]
        for i in range(1,steps):
            copy = self.map.copy([brush])
            self.map.translate(copy, (0,0,height*i))
            self.columnSlices.append(copy)
    def _testRotate(self):
        self.map.brushCylinder((0,0,0), 32, 128, 8, (0,0,1), self.map.textureWood)
        arms = [
            self.map.brushRectangular((-128, -4, 196), (128, 4, 196+16), self.map.textureWood),
            self.map.brushRectangular((-128, -4, 196+16), (-120, 4, 256), self.map.textureWood),
            self.map.brushRectangular((128, -4, 196+16), (120, 4, 256), self.map.textureWood)
            ]
        for i in range(1,4):
                t = self.map.copy(arms)
                self.map.rotate(t, (0,0,math.pi*i/4))
    def _testScale(self):
        try:
            assert len(self.columnSlices) > 0
        except:
            self.listenerWrite('Map.scale() test requires Map.translate() to be run.\n')
        else:
            step = (64/32)/len(self.columnSlices)
            for i in range(1,len(self.columnSlices)):
                self.map.scale(self.columnSlices[i], (1+i*step, 1+i*step, 1))

    def _testArch(self):
        self.map.arch((-32,-128,272), (32,-112,400), 7, False, self.map.textureTile)
        self.map.arch((-32,128,272), (32,112,400), 7, False, self.map.textureTile)
        self.map.arch((128,-32,272), (112,32,400), 7, True, self.map.textureTile)
        self.map.arch((-128,-32,272), (-112,32,400), 7, True, self.map.textureTile)
    def _testLadder(self):
        self.map.ladder((128,-96,0), (128,-96,416), 90)
        self.map.ladder((-128,96,0), (-128,96,416), 270)
        self.map.ladder((96,128,0), (96,128,416), 0)
        self.map.ladder((-96,-128,0), (-96,-128,416), 180)
    def _testStairs(self):
        length = 384
        self.map.stairs((-128-length,-64,0), (-128,64,272), (1,0), self.map.textureStone)
        self.map.stairs((128+length,-64,0), (128,64,272), (-1,0), self.map.textureStone)
        self.map.stairs((-64,-128-length,0), (64,-128,272), (0,1), self.map.textureStone)
        self.map.stairs((-64,128+length,0), (64,128,272), (0,-1), self.map.textureStone)
    def _testSpiralStairs(self):
        raise NotImplementedError
    def _testLift(self):
        raise NotImplementedError
    def _testSlidingDoor(self):
        raise NotImplementedError
    def _testKey(self):
        raise NotImplementedError
