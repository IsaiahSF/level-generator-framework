import math
from gameids import *

## Map interface. Defines a set of methods complete enough to generate a
#  playable map. Methods must be supported on all formats and all games.
#
class Map:

    ## the map file format extension this module supports
    mapFormat = None

    ## Constructor.
    #
    #  @param filepath file to save map to
    #  @param game game ID
    #
    def __init__(self, filepath, game):
        assert game in GAMES
        ## path where map will be saved
        self._filepath = filepath
        ## game ID
        self._game = game
        ## generic floor texture ID
        self.textureFloor = None
        ## generic wall texture ID
        self.textureWall = None
        ## generic ceiling texture ID
        self.textureCeiling = None
        ## generic concrete texture ID
        self.textureConcrete = None
        ## generic stone texture ID
        self.textureStone = None
        ## generic metal texture ID
        self.textureMetal = None
        ## generic wood texture ID
        self.textureWood = None
        ## generic tile texture ID
        self.textureTile = None
        ## generic water texture ID
        self.textureWater = None

    ## Save the map file.
    def save(self):
        raise NotImplementedError

    ## Access native map features.
    #
    #  @return reference to native map object.
    #
    def getNative(self):
        raise NotImplementedError

    ## Place the player start location
    #
    #  @param origin coordinates of start
    #  @param angle bearing angle player will start out facing
    #
    def playerStart(self, origin, angle = 0):
        raise NotImplementedError

    ## Point location that causes the level to transition
    #
    #  Depending on the game, this may create a physical structure. This
    #  occupies the same space as the player.
    #  The location may trigger the transition when the player enters it, or
    #  when the player activates something at this location.
    #  The next level loaded is the next Map the Generator requests after this
    #  Map.
    #
    #  @param origin location
    #  @param previousLevel boolean If this is true, the previous level is
    #  loaded instead of the next level. This is the Map that Generator
    #  requested before this Map.
    #
    def levelChangePoint(self, origin, previousLevel = False):
        raise NotImplementedError

    ## Create a random item.
    #
    #  Randomly place a weapon and ammo, health, or armor.
    #
    #  @param origin coordinates of item
    #
    def item(self, origin):
        raise NotImplementedError

    ## Create a weapon
    #
    #  Create a weapon to combat enemies with from the approximate strength
    #  category specified. A weapon from the category is selected randomly. If
    #  no strength is specified then the weapon is chosen entirely at random.
    #
    #  @param origin coordinates of item
    #  @param strength strength category of weapon. Integer 0-2. Corresponds to
    #  strength categories of enemies.
    #  @sa enemy()
    #
    #  @return ammo type ID that identifies the ammunition needed for the
    #  Weapon that was created. Value is None if the weapon uses no ammunition.
    #  @sa ammunition()
    #
    def weapon(self, origin, strength = None):
        raise NotImplementedError

    ## Create ammunition
    #
    #  @param origin coordinates of item
    #  @param ammoType identifies type of ammunition
    #
    #  @sa weapon()
    #
    def ammunition(self, origin, ammoType):
        raise NotImplementedError

    ## Place a health pack or other health restoration item
    #
    #  @param origin coordinates of item
    #  @param amount how much health this item restores. Integer. 100 is
    #  considered 100%.
    #
    def health(self, origin, amount):
        raise NotImplementedError
    
    ## Place an armor item
    #
    #  @param origin coordinates of item
    #  @param amount how much armor this item provides. Integer. 100 is
    #  considered 100%.
    #
    def armor(self, origin, amount):
        raise NotImplementedError

    ## Place an enemy
    #
    #  @param origin coordinates of enemy
    #  @param direction bearing angle enemy will be facing
    #  @param strength strength category of enemy. Integer 0-2. Corresponds to
    #  strength categories of weapons used to fight these enemies. If omitted,
    #  enemy is chosen randomly from all categories.
    #  @sa weapon()
    #
    def enemy(self, origin, direction, strength = None):
        raise NotImplementedError

    ## Place a point light source
    #
    #  @param origin coordinates of light source
    #  @param color [R, G, B] color. Integers 0-255.
    #  @param brightness brightness of light source
    #
    def light(self, origin, color, brightness):
        raise NotImplementedError

    ## Place sun in sky. Defines light that will come from sky sources.
    #
    #  @param angles (azimuth, altitude) angle of sun in sky. azimuth is compass
    #  bearing, and altitude is the number of degrees above the horizon (0-90).
    #  @param color [R, G, B] color. Values 0-255.
    #  @param brightness brightness of sun
    #
    def sun(self, angles, color, brightness):
        raise NotImplementedError

    ## Create height displacement
    #
    #  @param coords 4 2D [x,y] coordinates defining the 4 corners of the
    #  displacement, starting in lower left corner.
    #  @param elevation The base elevation of the displacement
    #  @param heightData height data. These values are added to the elevation, meaning they are relative.
    #  Must be 2 dimensional array. Array must be square, with dimensions of
    #  5, 9, or 17.
    #  @param material material displacement will be textured with
    def heightDisplacement(self, coords, elevation, heightData, material=""):
        raise NotImplementedError

    ## Place a rectangular brush.
    #
    #  Brush is aligned orthogonally. Fills rectangular bounding box defined by
    #  two coordinates.
    #
    #  @param coord1 coordinate of one corner
    #  @param coord2 coordinate of opposite corner
    #  @param texture optional texture
    #  @param detail boolean, true if brush should be treated as a (somewhat)
    #  optional detail
    #
    #  @return brush. Exactly what brush is may vary by map format. It can only
    #  be used as an identifier to perform additional operations on the brush.
    #
    def brushRectangular(self, coord1, coord2, texture = None, detail = False):
        raise NotImplementedError

    ## Make rectangular volume of water
    #
    #  The sides of the water brush are not guarunteed to render correctly if exposed.
    #  This depends on the game.
    #
    #  @param coord1 coordinate of one corner
    #  @param coord2 coordinate of opposite corner
    #
    #  @return brush
    #
    def makeWater(self, coord1, coord2):
        raise NotImplementedError

    ## Create cylindrical brush.
    #
    #  @param base coordinate of center of base
    #  @param radius radius of cylinder
    #  @param height height of cylinder
    #  @param sides integer number of sides cylinder will have. At least 3.
    #  @param axis unit vector along one axis. Defines orientation of cylinder.
    #  A vector not aligned with an axis causes an Exception.
    #  @param texture optional texture
    #  @param detail boolean, true if brush should be treated as a (somewhat)
    #  optional detail
    #
    #  @return brush
    #
    def brushCylinder(self, base, radius, height, sides, axis, texture = None, detail = False):
        raise NotImplementedError

    ## Create cone shaped brush.
    #
    #  Cone fills rectangular bounding box defined by two coordinates.
    #
    #  @param base coordinate of center of base
    #  @param radius radius of cylinder
    #  @param height height of cylinder
    #  @param sides integer number of sides cylinder will have. At least 3.
    #  @param axis unit vector, must be aligned along one axis. Defines
    #  orientation of cone.
    #  @param texture optional texture
    #  @param detail boolean, true if brush should be treated as a (somewhat)
    #  optional detail
    #
    #  @return brush
    #
    def brushCone(self, base, radius, height, sides, axis, texture = None, detail = False):
        raise NotImplementedError

    ## Create sphere shaped brush.
    #
    #  Sphere fills rectangular bounding box defined by two coordinates.
    #
    #  @param center center of sphere
    #  @param radius radius of sphere
    #  @param sides integer number of divisions around radius and height. At least 3.
    #  @param texture optional texture
    #  @param detail boolean, true if brush should be treated as a (somewhat)
    #  optional detail
    #
    #  @return brush
    #
    def brushSphere(self, center, radius, sides, texture = None, detail = False):
        raise NotImplementedError

    ## Make identical copies of brushes
    #
    #  @param objects list of one or more things to copy
    #  @return list of brushes
    #
    def copy(self, objects):
        raise NotImplementedError

    ## Carve an existing brush.
    #
    #  @param brush brush identifier obtained from creating a brush.
    #  @param origin coordinates of a point on the cutting plane
    #  @param normal normal vector of cutting plane, pointed outward.
    #
    def cut(self, brush, origin, normal):
        raise NotImplementedError

    ## Split an existing brush.
    #
    #  @param brush brush identifier obtained from creating a brush.
    #  @param origin coordinates of a point on the cutting plane
    #  @param normal normal vector of cutting plane, pointed toward brush to be
    #  split off
    #  @return brush brush that was split off of original brush
    #
    def split(self, brush, origin, normal):
        raise NotImplementedError

    ## Translate an existing brush.
    #
    #  @param objects list of things to translate
    #  @param translation vector (x,y,z)
    #
    def translate(self, objects, translation):
        raise NotImplementedError

    ## Rotate an existing brush.
    #
    #  @param objects list of things to rotate
    #  @param rotation angles (x,y,z)
    #
    def rotate(self, objects, rotation):
        raise NotImplementedError

    ## Scale an existing brush.
    #
    #  @param objects list of things to scale
    #  @param scale scaling factors (x,y,z)
    #
    def scale(self, objects, scale):
        raise NotImplementedError

    ## Apply texture to an existing brush.
    #
    #  Exact texture will vary by game.
    #
    #  @param brush brush identifier obtained from creating a brush
    #  @param texture texture.
    #
    def texture(self, brush, texture):
        raise NotImplementedError

    ## Make brush into sky
    #
    #  Generally used to make a box of sky over outdoor areas.
    #
    #  @param brush brush identifier obtained from creating a brush
    #
    def textureSky(self, brush):
        raise NotImplementedError

    ## Insert a prefab
    #
    #  @param name name of prefab
    #  @param origin location to place prefab
    #  @param orientation angle [pitch, yaw, roll] to place prefab
    #
    def prefab(self, name, origin, orientation):
        raise NotImplementedError

    ## Create an arch
    #
    #  @param coord1 coordinate of one corner
    #  @param coord2 coordinate of opposite corner
    #  @param sides number of sides on interior of arch
    #  @param axis True for x axis, False for y axis
    #  @param texture optional texture
    #
    def arch(self, coord1, coord2, sides, axis, texture = None):
        raise NotImplementedError

    ## Create a ladder
    #
    #  Location and size is defined by two coordinates, one directly above the
    #  other. The coordinates should be on the surface the ladder is mounted to.
    #
    #  @param coord1 coordinate of one end
    #  @param coord2 coordinate of opposite end
    #  @param bearing direction ladder faces. Should point out into the empty
    #  room or space the player approaches from.
    #
    def ladder(self, coord1, coord2, bearing):
        raise NotImplementedError

    ## Create a flight of stairs.
    #
    #  Fills the bounding box defined by two coordinates. Stairs ascend in the
    #  specified direction.
    #
    #  @param coord1 coordinate of one corner
    #  @param coord2 coordinate of opposite corner
    #  @param direction [x,y] unit vector aligned on an axis. Stairs ascend in
    #  this direction.
    #  @param texture optional texture
    #
    def stairs(self, coord1, coord2, direction, texture = None):
        raise NotImplementedError

    ## Create spiral stairs.
    #
    #  This does not create the central column. That can be added by creating
    #  a cylindrical brush. Note that this method does not guaruntee traversable
    #  stairs.
    #
    #  @param base coordinates of center of base at bottom
    #  @param innerRadius radius of central column/shaft.
    #  @param outerRadius outer radius of spiral stairs.
    #  @param stepsPerRevolution number of steps in one complete revolution
    #  @param stepHeight height gained with each step
    #  @param steps number of steps.
    #  @param angle bearing of first step's edge in relation to the base point.
    #  this defines the rotation of the spiral, or where the spiral starts.
    #  @param reverse boolean. Spirals counterclockwise if True.
    #  @param texture optional texture
    #
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

    ## Create lift or elevator.
    #
    #  This may be automatically activated or player activated depending on the
    #  game. It is a simple platform that fills the bottom of the bounded area
    #  and travels to the top of the bounded area, stopping flush with the top
    #  of the bounded area. There are no walls or railings on the lift.
    #
    #  @param coord1 coordinate of one corner
    #  @param coord2 coordinate of opposite corner
    #  @param key ID of key that unlocks this door
    #
    def lift(self, coord1, coord2, key = None):
        raise NotImplementedError

    ## Create a sliding door.
    #
    #  The door fills the bounding volume. It slides in the direction specified
    #  a distance equal to its length in that direction. If the key is specified
    #  then the correct key must be located to unlock this door. The player will
    #  be notified of what key to seek in a manner appropriate to the game.
    #
    #  @param coord1 coordinate of one corner
    #  @param coord2 coordinate of opposite corner
    #  @param direction unit vector aligned with an axis
    #  @param key ID of key that unlocks this door
    #
    def slidingDoor(self, coord1, coord2, direction, key = None):
        raise NotImplementedError

    ## Create a Key
    #
    #  The key may be implemented in many different ways. If the game has a
    #  native key object then that will be used. If no native key mechanism is
    #  available a button or similar mechanism is placed which will remotely
    #  enable things locked with this key. One key can lock many things.
    #
    #  @param location coordinate of base of key
    #  @param direction bearing angle player is meant to approach from
    #
    #  @return key ID. Passed to things that this key unlocks.
    #
    def key(self, location, direction):
        raise NotImplementedError
    
