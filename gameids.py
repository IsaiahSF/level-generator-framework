#Game ID constants
HL2 =       'Half Life 2'
HL2EP1 =    'Half Life 2 Episode 1'
HL2EP2 =    'Half Life 2 Episode 2'
HL2DM =     'Half Life 2 Deathmatch'
P1 =        'Portal'
P2 =        'Portal 2'
L4D1 =      'Left 4 Dead (1)'
L4D2 =      'Left 4 Dead 2'
TF2 =       'Team Fortress 2'
CSS =       'Counter Strike: Source'
GMOD =      "Garry's Mod"

GAMES = [HL2, HL2EP1, HL2EP2, HL2DM, P1, P2, L4D1, L4D2, TF2, CSS, GMOD]

#Format extension constants
VMF =       'vmf'

FORMATS = [VMF]

#Game-Format associations
gameFormats = {
    HL2     : VMF,
    HL2EP1  : VMF,
    HL2EP2  : VMF,
    HL2DM   : VMF,
    P1      : VMF,
    P2      : VMF,
    L4D1    : VMF,
    L4D2    : VMF,
    TF2     : VMF,
    CSS     : VMF,
    GMOD    : VMF
    }

## get the format used by the specified game
def getGameFormat(gameID):
    return gameFormats[gameID]

## get a list of games supported by the specified format
def getFormatGames(formatExtension):
    result = []
    for x in gameFormats.keys():
        if gameFormats[x] == formatExtension:
            result.append(x)
    return result

