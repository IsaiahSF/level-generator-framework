import math, random, copy
from formats.map import Map
from formats.vmf import VMF as VMFraw
from formats.vmf import Solid, Side, Entity, Matrix
from gameids import *

## Implements Map interface for .vmf map files.
#
#  @sa Map
#  @todo implement
#  @todo entities for l4d* games, cs:s, tf2, portal* games
#  @todo allow slanted ladders
#  @todo ladders for CS:S, Gmod, l4d? (func_ladder instead of func_useableladder)
#  @todo test
#
class VMFMap(Map):
    
    mapFormat = VMF
    
    ##dict of weapon-ammo pairings for HL2
    HL2ammo = {
         'weapon_357'           : 'item_ammo_357',
         'weapon_ar2'           : 'item_ammo_ar2',
         'weapon_crossbow'      : 'item_ammo_crossbow',
         'weapon_crowbar'       : None,
         'weapon_frag'          : 'weapon_frag',
         'weapon_physcannon'    : ['prop_physics', ['model','models/props_junk/sawblade001a.mdl']], #ammo is sawblade physics prop
         'weapon_pistol'        : 'item_ammo_pistol',
         'weapon_rpg'           : 'item_rpg_round',
         'weapon_shotgun'       : 'item_box_buckshot',
         'weapon_smg1'          : 'item_ammo_smg1'
         }
    HL2weapons = [['weapon_crowbar','weapon_pistol','weapon_frag'],
                  ['weapon_smg1','weapon_crossbow','weapon_physcannon'],
                  ['weapon_ar2','weapon_shotgun','weapon_rpg']]
    Hl2enemies = [['npc_cscanner','npc_headcrab','npc_metropolice','npc_zombie','npc_zombie_torso'],
                  ['npc_turret_floor','npc_manhack','npc_poisonzombie','npc_headcrab_black','npc_rollermine'],
                  ['npc_fastzombie','npc_headcrab_fast','npc_antlion','npc_combine_s']]

    def __init__(self, filepath, game):
        Map.__init__(self, filepath, game)
        self._native = VMFraw(game)
        self._sun = None
        #set up default textures
        if self._game == P2:
            self.textureFloor    = 'concrete/concrete_modular_floor001a'
            self.textureWall     = 'tile/white_wall_tile003a'
            self.textureCeiling  = 'tile/tile_ceiling_001a'
            self.textureConcrete = 'concrete/concretewall075a'
            self.textureStone    = 'tile/observation_tilefloor001a'
            self.textureMetal    = 'metal/black_wall_metal_001c'
            self.textureWood     = 'wood/milflr002'
            self.textureTile     = 'tile/white_floor_tile004b'
            self.textureWater    = 'liquids/water_underground_cave'
        elif self._game == L4D1 or self._game == L4D2:
            self.textureFloor    = 'concrete/concrete_floor_02'
            self.textureWall     = 'brick/brickwall_brightred'
            self.textureCeiling  = 'plaster/plaster_ceiling_01'
            self.textureConcrete = 'concrete/concretefloor005a'
            self.textureStone    = 'stone/infwllj'
            self.textureMetal    = 'metal/metalhull003a'
            self.textureWood     = 'wood/woodfloor005a'
            self.textureTile     = 'tile/prodflra'
            self.textureWater    = 'liquids/ruralwater_river'
        else:
            self.textureFloor    = 'concrete/concretefloor023a'
            self.textureWall     = 'brick/brickwall003a'
            self.textureCeiling  = 'plaster/plasterceiling003a'
            self.textureConcrete = 'concrete/concretefloor005a'
            self.textureStone    = 'nature/rockwall010b'
            self.textureMetal    = 'metal/citadel_metalwall076a'
            self.textureWood     = 'wood/woodfloor006a'
            self.textureTile     = 'tile/tilefloor001a'
            self.textureWater    = 'nature/water_canals_city'

    def save(self):
        self._native.save(self._filepath)

    def getNative(self):
        return self._native

    def playerStart(self, origin, angle = 0):
        Entity(
            self._native,
            'info_player_start',
            origin = origin,
            angles = (0, angle, 0)
            )
        Entity(
            self._native,
            'item_suit',
            origin = (origin[0], origin[1], origin[2] + 2)
            )

    def levelChangePoint(self, origin, previousLevel = False):
        raise NotImplementedError
    
    def item(self, origin):
        choice = random.randint(0,2)
        if choice == 0:
            # weapon and ammo
            ammoType = self.weapon((origin[0], origin[1], origin[2]))
            self.ammunition((origin[0], origin[1], origin[2]+12), ammoType)
        elif choice == 1:
            # health
            self.health(origin, random.randint(10,51))
        else:
            # armor
            self.armor(origin, random.randint(10,51))

    def weapon(self, origin, strength = None):
        origin = list(origin)
        origin[2] += 8
        if strength == None:
            strength = random.randint(0,2)
        weapon = random.choice(VMFMap.HL2weapons[strength])
        Entity(self._native, weapon, origin = origin)
        return VMFMap.HL2ammo[weapon]
    
    def ammunition(self, origin, ammoType):
        ## @todo fix ammo amounts to be more reasonable
        assert len(origin) == 3
        origin = list(origin)
        origin[2] += 8
        if ammoType == None:
            return
        if type(ammoType) == list:
            e = Entity(self._native, ammoType[0], origin = origin)
            for prop in ammoType[1:]:
                e[prop[0]] = prop[1]
        else:
            Entity(self._native, ammoType, origin = origin)
    
    def health(self, origin, amount):
        #makes a vertical stack of health items approximating specified value.
        bigpacks = int(amount/25)
        amount -= bigpacks*25
        smallpacks = round(amount/10)
        h = 0
        for pack in range(bigpacks):
            Entity(self._native, 'item_healthkit',
                   origin = (origin[0], origin[1], origin[2] + h)
                   )
            h += 8
        for pack in range(smallpacks):
            Entity(self._native, 'item_healthvial',
                   origin = (origin[0], origin[1], origin[2] + h)
                   )
            h += 8
    
    def armor(self, origin, amount):
        # makes a vertical stack of batteries approximating specified value
        batteries = round(amount/15)
        for battery in range(batteries):
            Entity(self._native, 'item_battery',
                   origin = (origin[0], origin[1], origin[2] + battery*8)
                   )
    
    def enemy(self, origin, direction, strength = None):
        angles = (0, direction, 0)
        if strength == None:
            strength = random.randint(0,2)
        enemy = random.choice(VMFMap.Hl2enemies[strength])
        Entity(self._native, enemy, origin = origin, angles = angles)
    
    def light(self, origin, color, brightness):
        l = Entity(self._native, 'light')
        l['origin'] = origin
        l['_light'] = list(color) + [brightness]
        return l
    
    def sun(self, angles, color, brightness):
        assert angles[1] <= 90
        assert angles[1] >= 0
        if self._sun == None:
            l = Entity(self._native, 'light_environment')
            l['origin'] = (0,0,0)
            s = Entity(self._native, 'env_sun')
            s['origin'] = (16,0,0)
            self._sun = [l,s]
        self._sun[0]['angles'] = [0, (90 - angles[0])%360, 0]
        self._sun[0]['pitch'] = -angles[1]
        self._sun[0]['_light'] = list(color) + [brightness]
        self._sun[0]['_ambient'] = list(color) + [brightness/10]
        self._sun[1]['angles'] = [0, (90 - angles[0])%360, 0]
        self._sun[1]['pitch'] = -angles[1]
        self._sun[1]['use_angles'] = True
    
    def heightDisplacement(self, coords, elevation, heightData, material=""):
        assert len(coords) == 4
        coords = [x+[elevation] for x in coords]
        sides = []
        sides.append(coords[:3]) #top
        bottom = [x[:2]+[elevation-16] for x in coords[:3]]
        bottom.reverse()
        sides.append(bottom) #bottom
        for i in range(4): #sides
            p1 = coords[i]
            p2 = coords[(i+1)%4]
            p3 = copy.copy(p2)
            p3[2] = p3[2] + 1
            sides.append([p1, p2, p3])
        solid = Solid.fromPlanes(self._native, sides, material)
        
        power = math.log(len(heightData)-1, 2)
        solid.sides[0].power = power
        solid.sides[0].displacement = [[[0,0,x] for x in y] for y in heightData]
        solid.sides[0]._startPosition = coords[0]
        
        return solid
    
    def brushRectangular(self, coord1, coord2, texture = None, detail = False):
        temp1 = [coord1[0], coord2[0]]
        temp2 = [coord1[1], coord2[1]]
        temp3 = [coord1[2], coord2[2]]
        temp1.sort()
        temp2.sort()
        temp3.sort()
        w, e = temp1
        s, n = temp2
        b, t = temp3
        assert w != e
        assert s != n
        assert b != t
        planes = [
            [[0,0,t],[1,0,t],[1,-1,t]], #top
            [[0,0,b],[1,0,b],[1,1,b]], #bottom
            [[0,n,0],[1,n,0],[1,n,1]], #north side
            [[0,s,0],[1,s,0],[1,s,-1]], #south side
            [[e,0,0],[e,1,0],[e,1,-1]], #east side
            [[w,0,0],[w,1,0],[w,1,1]] #west side
            ]
        if texture == None:
            texture == ''
        if detail:
            e = Entity(self._native, 'func_detail')
            return Solid.fromPlanes(e, planes, texture)
        else:
            return Solid.fromPlanes(self._native, planes, texture)

    def makeWater(self, coord1, coord2):
        return self.brushRectangular(coord1, coord2, [self.textureWater] + ['tools/toolsnodraw']*5)
    
    def brushCylinder(self, base, radius, height, sides, axis, texture = None, detail = False):
        axis = [abs(x) for x in axis]
        if not sum(axis) == 1:
            raise Exception('axis is not axis-aligned unit vector')
        if axis[0] == 1:
            matrix = Matrix.fromAngles(math.pi/2.0, 0.0, math.pi/2.0)
        elif axis[1] == 1:
            matrix = Matrix.fromXAngle(math.pi/2.0)
        elif axis[2] == 1:
            matrix = None
        else:
            raise Exception('axis is not axis-aligned unit vector')
        if texture == None:
            texture = ''
        if detail:
            e = Entity(self._native, 'func_detail')
            brush = Solid.fromCylinder(e, base, radius, height, sides, texture)
        else:
            brush = Solid.fromCylinder(self._native, base, radius, height, sides, texture)
        if matrix != None:
            brush.transform(matrix)
        return brush
    
    def brushCone(self, base, radius, height, sides, axis, texture = None, detail = False):
        if abs(sum(axis)) != 1:
            raise Exception('axis is not axis-aligned unit vector')
        halfpi = math.pi/2.0
        if axis[0] == 1:
            matrix = Matrix.fromAngles(halfpi, 0.0, -halfpi)
        if axis[0] == -1:
            matrix = Matrix.fromAngles(halfpi, 0.0, halfpi)
        elif axis[1] == 1:
            matrix = Matrix.fromAngles(halfpi, 0.0, math.pi)
        elif axis[1] == -1:
            matrix = Matrix.fromXAngle(halfpi)
        elif axis[2] == 1:
            matrix = None
        elif axis[2] == -1:
            matrix = Matrix.fromYAngle(math.pi)
        else:
            raise Exception('axis is not axis-aligned unit vector')
        assert sides >= 3
        planes = []
        points = []
        step = math.pi*2/sides
        for i in range(sides):
            points.append([int(math.sin(i*step)*radius), int(math.cos(i*step)*radius)])
        # Bottom
        planes.append(
            [[0, 0, base[2]],
             [-1, -1, base[2]],
             [0, -1, base[2]]]
            )
        # Sides
        for x in range(len(points) - 1):
            planes.append(
                [[base[0]+points[x][0], base[1]+points[x][1], base[2]],
                 [base[0]+points[x+1][0], base[1]+points[x+1][1], base[2]],
                 [base[0], base[1], base[2]+height]]
                )
        planes.append(
            [[base[0]+points[-1][0], base[1]+points[-1][1], base[2]],
             [base[0]+points[0][0], base[1]+points[0][1], base[2]],
             [base[0], base[1], base[2]+height]]
            )
        if texture == None:
            texture = ''
        if detail:
            e = Entity(self._native, 'func_detail')
            brush = Solid.fromPlanes(e, planes, texture)
        else:
            brush = Solid.fromPlanes(self._native, planes, texture)
        if matrix != None:
            brush.transform(matrix)
        return brush
    
    def brushSphere(self, center, radius, sides, texture = None, detail = False):
        if texture == None:
            texture = ''
        if detail:
            e = Entity(self._native, 'func_detail')
            return Solid.fromSphere(e, center, radius, sides, texture)
        else:
            return Solid.fromSphere(self._native, center, radius, sides, texture)
    
    def copy(self, objects):
        assert type(objects) == list
        newlist = []
        for thing in objects:
            newlist.append(thing.copy())
        return newlist
    
    def cut(self, brush, origin, normal):
        raise NotImplementedError
    
    def split(self, brush, origin, normal):
        raise NotImplementedError
    
    def translate(self, objects, translation):
        matrix = Matrix.fromTranslate(translation[0], translation[1], translation[2])
        for thing in objects:
            thing.transform(matrix, True, True)
    
    def rotate(self, objects, rotation):
        matrix = Matrix.fromAngles(rotation[0], rotation[1], rotation[2])
        for thing in objects:
            thing.transform(matrix, True, True)
    
    def scale(self, objects, scale):
        matrix = Matrix.fromScale(scale[0], scale[1], scale[2])
        for thing in objects:
            thing.transform(matrix, True, True)
    
    def texture(self, brush, texture):
        for side in brush.sides:
            side.material = texture
    
    def textureSky(self, brush):
        self.texture(brush, 'tools/toolsskybox')
    
    def prefab(self, name, origin, orientation):
        raise NotImplementedError
    
    def arch(self, coord1, coord2, sides, axis, texture = None):
        temp1 = [coord1[0], coord2[0]]
        temp2 = [coord1[1], coord2[1]]
        temp3 = [coord1[2], coord2[2]]
        temp1.sort()
        temp2.sort()
        temp3.sort()
        w, e = temp1
        s, n = temp2
        b, t = temp3
        assert w != e
        assert s != n
        assert b != t
        points = []
        brushes = []
        height = t - b - 4
        if axis:
            #x axis
            width = (n - s)/2.0
        else:
            #y axis
            width = (e - w)/2.0
        step = math.pi/(sides)
        for i in range(sides):
            points.append([int(math.cos(i*step)*width), int(math.sin(i*step)*height)])
        points.append([-int(width), 0])
        if axis:
            #x axis
            for i in range(sides):
                planes = [
                    [[0,0,t],[1,0,t],[1,-1,t]], #top
                    [[1,points[i][0],points[i][1] + b],[0,points[i][0],points[i][1] + b],[0,points[i+1][0],points[i+1][1] + b]], #bottom
                    [[0,points[i][0],0],[1,points[i][0],0],[1,points[i][0],1]], #north side
                    [[0,points[i+1][0],0],[1,points[i+1][0],0],[1,points[i+1][0],-1]], #south side
                    [[e,0,0],[e,1,0],[e,1,-1]], #east side
                    [[w,0,0],[w,1,0],[w,1,1]] #west side
                    ]
                brushes.append(Solid.fromPlanes(self._native, planes, texture))
        else:
            #y axis
            for i in range(sides):
                planes = [
                    [[0,0,t],[1,0,t],[1,-1,t]], #top
                    [[points[i][0],0,points[i][1] + b],[points[i][0],1,points[i][1] + b],[points[i+1][0],1,points[i+1][1] + b]], #bottom                    
                    [[0,n,0],[1,n,0],[1,n,1]], #north side
                    [[0,s,0],[1,s,0],[1,s,-1]], #south side
                    [[points[i][0],0,0],[points[i][0],1,0],[points[i][0],1,-1]], #east side
                    [[points[i+1][0],0,0],[points[i+1][0],1,0],[points[i+1][0],1,1]] #west side
                    ]
                brushes.append(Solid.fromPlanes(self._native, planes, texture))
            
        return brushes
    
    def ladder(self, coord1, coord2, bearing):
        assert coord1[0] == coord2[0]
        assert coord1[1] == coord2[1]
        assert coord1[2] != coord2[2]
        x, y = coord1[:2]
        temp = [coord1[2], coord2[2]]
        temp.sort()
        b, t = temp
        t += 4
        bearing = (90 - bearing)%360
        #make ladder props (only come in 128 high segments >_>)
        for i in range(b, t-t%128, 128):
            e = Entity(
                self._native,
                'prop_static',
                origin = (x, y, i),
                angles = [0, bearing, 0],
                model = 'models/props_c17/metalladder002.mdl'
                )
        #make ladder entites
        bearing = math.radians(bearing)
        offset = (math.cos(bearing)*28, math.sin(bearing)*28)
        l = Entity(
            self._native,
            'func_useableladder',
            origin = (x+offset[0],y+offset[1],b),
            point0 = (x+offset[0],y+offset[1],b),
            point1 = (x+offset[0],y+offset[1],t)
            )
    
    def stairs(self, coord1, coord2, direction, texture = None):
        #step height always 8
        temp1 = [coord1[0], coord2[0]]
        temp2 = [coord1[1], coord2[1]]
        temp3 = [coord1[2], coord2[2]]
        temp1.sort()
        temp2.sort()
        temp3.sort()
        w, e = temp1
        s, n = temp2
        b, t = temp3
        assert w != e
        assert s != n
        assert b != t
        steps = int((t - b)/8)
        if not sum([abs(x) for x in direction]) == 1:
            raise Exception('direction not axis-aligned unit vector')
        brushes = []
        if direction[0] == 0:
            #y-ascending stairs
            direction = direction[1]
            run = direction*(n - s)/(steps - 1)
            if direction == 1:
                #bottom left, top left, top right, bottom right
                clip = (b,t-8,t-8,b)
                start = s
            else:
                clip = (t-8,b,b,t-8)
                start = n
            for i in range(steps-1):
                brushes.append(
                    self.brushRectangular((e, start+run*i, i*8), (w, start+run*(i+1), (i+1)*8), texture, True)
                    )
        elif direction[1] == 0:
            #x-ascending stairs
            direction = direction[0]
            run = direction*(e - w)/(steps - 1)
            if direction == 1:
                clip = (b,b,t-8,t-8)
                start = w
            else:
                clip = (t-8,t-8,b,b)
                start = e
            for i in range(steps-1):
                brushes.append(
                self.brushRectangular((start+run*i, s, i*8), (start+run*(i+1), n, (i+1)*8), texture, True)
                )
        else:
            raise Exception('direction not axis-aligned unit vector')
        brushes.append(
            Solid.fromPlanes(self._native,
                             [[[0,n,0],[1,n,0],[1,n,1]],
                              [[0,s,0],[0,s,1],[1,s,1]],
                              [[e,0,0],[e,0,1],[e,1,1]],
                              [[w,0,0],[w,1,0],[w,1,1]],
                              [[w,s,clip[0]+8],[w,n,clip[1]+8],[e,n,clip[2]+8]],
                              [[w,s,clip[0]],[e,s,clip[3]],[e,n,clip[2]]]
                              ],
                             'tools/toolsplayerclip'
                             )
            )
        return brushes
    
    def spiralStairs(
        self,
        base,
        innerRadius,
        outerRadius,
        stepsPerRevolution,
        stepHeight,
        steps,
        angle,
        reverse,
        texture = None
        ):
        raise NotImplementedError
    
    def lift(self, coord1, coord2, key = None):
        raise NotImplementedError
    
    def slidingDoor(self, coord1, coord2, direction, key = None):
        raise NotImplementedError
    
    def key(self, location, direction):
        raise NotImplementedError
