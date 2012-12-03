import os, gameids, copy, re
from formats.sdkutil import SDKUtil


## Parses entity information from a .fgd file.
#
#  Entities can be accessed by name like a dict.
class FGD:
    
    ## @todo tidy up mess that zay created
    ## @todo remove unnecessary code
    
    ## void data type
    VOID = "fgd_void"
    ## string data tyle
    STRING = "fgd_string"
    ## boolean data type
    BOOLEAN = "fgd_boolean"
    ## integer data type
    INTEGER = "fgd_integer"
    ## decimal number data type
    FLOAT = "fgd_float"
    ## integer list data type
    INTEGER_LIST = "fgd_integer_list"
    ## decimal number list data type
    FLOAT_LIST = "fgd_float_list"
    ## vector data type
    VECTOR = "fgd_vector"
    ## angle data type
    ANGLE = "fgd_angle"
    ## axis data type
    AXIS = "fgd_axis"
    ## choice data type
    CHOICE = "fgd_choice"
    
    _CONVERSION = {
        VOID:['void'],
        STRING:[
            'string', 'filterclass', 'material', 'npcclass', 'scene',
            'sound', 'pointentityclass', 'sprite', 'studio',
            'target_destination', 'target_name_or_class', 'target_source',
            'decal', 'instance_file', 'instance_variable', 'instance_parm'
            ],
        BOOLEAN:['bool'],
        INTEGER:['integer','node_dest', 'flags'],
        FLOAT:['float'],
        INTEGER_LIST:['color255','sidelist'],
        FLOAT_LIST:['color1'],
        VECTOR:['origin', 'vector'],
        ANGLE:['angle'],
        AXIS:['axis','vecline'],
        CHOICE:['choices','flags']
    }
    
    _DEFAULTS = {
        'void':'',
        'string':'',
        'integer':0,
        'float':0.0,
        'choices':0,
        'flags':0,
        'axis':[[0,0,0],[0,0,1]],
        'angle':[0.0,0.0,0.0],
        'color255':[0,0,0],
        'color1':[1.0,1.0,1.0],
        'filterclass':'',
        'material':'',
        'node_dest':0,
        'npcclass':'',
        'origin':[0.0,0.0,0.0],
        'pointentityclass':'',
        'scene':'',
        'sidelist':[],
        'sound':'',
        'sprite':'',
        'studio':'',
        'target_destination':'',
        'target_name_or_class':'',
        'target_source':'',
        'vecline':[[0,0,0],[0,0,1]],
        'vector':[0.0,0.0,0.0]
    }

    ## Valid class types for an FGD file
    #
    # @@MaterialExclusion and @@AutoVisGroup aren't classes and are an exception.
    classTypes = [
        '@BaseClass',
        '@PointClass',
        '@NPCClass',
        '@SolidClass',
        '@KeyFrameClass',
        '@MoveClass',
        '@FilterClass',
        '@MaterialExclusion',
        '@AutoVisGroup'
        ]
    ## Hammer display elements. These tell Hammer how to display the entity.
    #  An entity may have any number of these, and multiples of each type.
    properties = {
        'halfgridsnap', #only property without parenthesis
        'base',
        'color',
        'iconsprite',
        'size',
        'wirebox',
        'line',
        'cylinder', #unknown
        'sphere',
        'sidelist', #unknown. name of parameter that is list of sides
        'studio',
        'studioprop',
        'lightprop', #unknown. model?
        'quadbounds', #unknown. boolean?
        'light', #unknown. boolean?
        'lightcone', #unknown. boolean?
        'frustum', #unknown
        'sprite', #unknown. boolean?
        'decal', #unknown. boolean?
        'overlay', #unknown. boolean?
        'overlay_transition', #unknown. boolean?
        'keyframe', #unknown. boolean?
        'animator', #unknown. boolean?
        'instance', #unknown. boolean?
        'sweptplayerhull', #unknown. boolean?
        }

    _FGDDict = {}

    ## Get the appropriate FGD object for the specified game
    #
    #  @param gameId game ID
    #  @return FGD object
    @classmethod
    def getGameFGD(cls, gameId):
        if gameId not in gameids.GAMES:
            raise Exception("Game ID %s not a valid game ID." % gameId)
        
        if gameId not in cls._FGDDict:
            user, base = SDKUtil.findUserAndBasePath()
            path = base + "/" + user
            if gameId == gameids.HL2:
                path += "/sourcesdk/bin/source2007/bin/halflife2.fgd"
            elif gameId == gameids.HL2DM:
                path += "/sourcesdk/bin/source2007/bin/hl2mp.fgd"
            elif gameId == gameids.HL2EP1:
                path += "/sourcesdk/bin/ep1/bin/halflife2.fgd"
            elif gameId == gameids.HL2EP2:
                path += "/sourcesdk/bin/source2009/bin/halflife2.fgd"
            elif gameId == gameids.P1:
                raise NotImplementedError() ## @todo implement
            elif gameId == gameids.P2:
                raise NotImplementedError() ## @todo implement
            elif gameId == gameids.L4D1:
                raise NotImplementedError() ## @todo implement
            elif gameId == gameids.L4D2:
                raise NotImplementedError() ## @todo implement
            elif gameId == gameids.TF2:
                raise NotImplementedError() ## @todo implement
            elif gameId == gameids.CSS:
                raise NotImplementedError() ## @todo implement
            elif gameId == gameids.GMOD:
                raise NotImplementedError() ## @todo implement
            
            cls._FGDDict[gameId] = FGD(path)

        return cls._FGDDict[gameId]

    ## Parse nested segments. Each segment is replaced with a list of the section's contents
    #
    #  @param data string to operate on
    #  @param start character that marks start of section. A beginning bracket.
    #  @param end character that marks end of section. An ending bracket.
    #
    @staticmethod
    def parseNested(data, start, end):
        assert type(data) == str
        assert type(start) == str
        assert type(end) == str
        assert start != end
        result = [[]] #used as stack. starts with empty root layer
        cursor = 0
        startmark = data.find(start, cursor)
        endmark = data.find(end, cursor)
        while True:
            if endmark == -1: #should mean there are no more brackets
                if startmark != -1: #there are starting brackets left with no ending brackets
                    raise Exception('bracket left open')
                if len(result) > 1: #we still have unclosed layers on the stack
                    raise Exception('bracket left open')
                if len(data) > cursor + 1:
                    result[-1].append(data[cursor:])
                break #loop exits here only (aside from exceptions)
            if startmark == -1 or endmark < startmark: #ending bracket comes next
                #decrement level in heirarchy
                if len(result) <= 1: #we ran out of layers on the stack (first layer is root)
                    raise Exception('unexpected end bracket')
                if endmark > cursor:
                    result[-1].append(data[cursor:endmark])
                segment = result.pop() #remove layer from stack
                result[-1].append(segment) #append completed layer to parent layer
                #find next end marker
                cursor = endmark + 1
                endmark = data.find(end, cursor)
            else: #starting bracket comes next
                #increment level in heirarchy
                if startmark > cursor:
                    result[-1].append(data[cursor:startmark])
                result.append([]) #add layer to stack
                #find next start marker
                cursor = startmark + 1
                startmark = data.find(start, cursor)
        return result[0]

    ## after heirarchy of brackets is formed, break strings into multiple strings at newlines
    # ['abc \n def',['a \n b \n c'],'gh \n i'] -->['abc ', ' def',['a ', ' b ', ' c'],'gh ', ' i']
    @staticmethod
    def _breakNewlines(item):
        if type(item) == list:
            thing = 0
            while thing < len(item):
                broken = FGD._breakNewlines(item[thing])
                if type(item[thing]) == str:
                    item.pop(thing)
                    for i in range(len(broken)):
                        item.insert(thing + i, broken[i])
                else:
                    item[thing] = broken
                thing += 1
        else:
            item = item.strip()
            item = item.split('\n')
        return item

    ## replace strings with symbols. symbol can be used to access string with self.stringDict
    #
    #  @param symbol quote character that bounds strings
    def _parseQuotes(self, symbol):
        ## dictionary of symbol-string pairs.
        #  Strings are replaced with symbols. This dict is used to retrieve the string contents when a symbol is
        #  encountered.
        self.stringDict = {}
        strings = 0
        data = self.data.split(symbol)
        if not len(data)%2 == 1:
            #must be odd number of chunks for even number of quotes
            raise Exception('quote left open in string')
        for i in range(1,len(data),2):
            name = '&stringsymbol%(#)d&' % {'#' : strings}
            self.stringDict[name] = data[i]
            data[i] = name
            strings += 1
        self.data = ''.join(data)

    ## Constructor
    #
    #  @param filepath path of FGD file to parse
    def __init__(self, filepath):
        assert os.path.isfile(filepath)
        ## Path of FGD file this object represents
        self.filepath = os.path.abspath(filepath)
        self.filepath = self.filepath.replace('\\','/')
        ## Dict of entities described by this file. Key is entity name, value is entity object.
        self.entities = {}
        self._load(filepath)

    ## enables len(FGD) for number of entities in file
    def __len__(self):
        return len(self.entities)

    ## enables access via FGD[key]
    #
    #  @param key name of entity to retrieve
    def __getitem__(self, key):
        return self.entities[key]

    ## enables iteration through contained entities
    def __iter__(self):
        return iter(self.entities)

    ## enables (x in FGD) to check if x is an entity in this FGD
    #
    #  @param item name of entity
    def __contains__(self, item):
       return item in self.entities

    def _addEntity(self, entity):
        assert isinstance(entity, FGD.Entity)
        self.entities[entity.name] = entity

    def _load(self, filepath):
        assert os.path.isfile(filepath)
        filepath = os.path.abspath(filepath)
        filepath = filepath.replace('\\','/')

        #load file
        with open(filepath, 'r') as f:
            ## contents of file
            self.data = f.readlines()
        
        #preprocess file
        #remove comments
        for i in range(len(self.data)):
            if '//' in self.data[i]:
                self.data[i] = self.data[i].split('//',1)[0] + '\n'
        #remove white space and blank lines
        self.data = ''.join(self.data)
        self.data = self.data.replace('\t', ' ')
        while '  ' in self.data:
            self.data = self.data.replace('  ', ' ')
        while '\n\n' in self.data:
            self.data = self.data.replace('\n\n', '\n')

        #join split strings
        self.data = self.data.replace('" +\n"', '')
        self.data = self.data.replace('" +\n "', '')
        self.data = self.data.replace('"+\n"', '')
        self.data = self.data.replace('"+\n "', '')
        self.data = self.data.replace('" +\n', '"\n') #remove trailing string splits

        #parse quotes
        self._parseQuotes('"')
        #parse brackets
        self.data = FGD.parseNested(self.data, '[', ']')
        #break at newlines again
        self.data = FGD._breakNewlines(self.data)
        
        #process file
        cursor = 0
        while cursor < len(self.data):
            if type(self.data[cursor]) != str:
                raise IOError('Unexpected brackets')
            line = self.data[cursor] 
            line = line.split(' ')
            if line[0] == '@include':
                # parse included files
                importPath = filepath.rsplit('/',1)[0]
                importPath += '/' + self.stringDict[ line[1] ]
                imported = FGD(importPath)
                self.entities.update(imported.entities)
            elif line[0].startswith('@mapsize'):
                #this line defines the maximum map size this game uses
                pass
            elif line[0] in FGD.classTypes:
                item = self.data[cursor]
                cursor += 1
                while type(self.data[cursor]) == str:
                    item += self.data[cursor]
                    cursor += 1
                parameters = self.data[cursor]
                parameters = [x for x in parameters if x != '']
                #add class
                self._addEntity( FGD.Entity(self, item, parameters) )
            else:
                raise IOError('Unrecognized line: ' + self.data[cursor])
            cursor += 1

    ## Container for information about class parameters, inputs, and outputs
    # @todo clean and improve code, fix nonsensical elements of parsing strategy
    class Entity:
        ## valid data types for parameters, inputs, and outputs.
        valueTypes = {
            'void',
            'bool',
            'string',
            'integer',
            'float',
            'choices',
            'flags',
            'axis',
            'angle',
            'color255',
            'color1',
            'filterclass',
            'material',
            'node_dest',
            'npcclass',
            'origin',
            'pointentityclass',
            'scene',
            'sidelist',
            'sound',
            'sprite',
            'studio',
            'target_destination',
            'target_name_or_class',
            'target_source',
            'vecline',
            'vector'
            }

        ## Constructor
        #
        #  @param parent FGD file that contains this entity
        #  @param classLine first line of class definition
        #  @param parameters contents of bracketed section defining class parameters, inputs, and outputs
        def __init__(self, parent, classLine, parameters):
            ## FGD file that contains this entity
            self.parent = parent
            ## name of entity
            self.name = None
            ## type of entity
            self.type = None
            ## description of entity
            self.description = None
            ## list of Hammer display elements
            self.display = []
            ## list of entity member variables that can be set
            #these are only dicts while parsing, at the end they are only lists
            #this forces uniqueness of parameters, and overwrites upon duplication
            self.parameters = {}
            ## list of entity inputs
            self.inputs = {}
            ## list of entity outputs
            self.outputs = {}

            #parse classLine
            #parse description
            data = classLine.split(':')
            assert len(data) <= 2
            if len(data) == 2:
                self.description = data[1]
            #parse name
            data = data[0].split('=')
            data = [x.strip() for x in data]
            assert len(data) == 2
            self.name = data[1]
            #parse hammer display properties
            data = FGD.parseNested(data[0], '(', ')')
            data[0] = data[0].split(' ')
            self.type = data[0][0]
            assert self.type in FGD.classTypes
            data[0] = ' '.join(data[0][1:])
            #split grouped properties
            cursor = 0
            while cursor < len(data):
                if type(data[cursor]) == str:
                    replacement = data[cursor].split(' ')
                    data.pop(cursor)
                    data = data[:cursor] + replacement + data[cursor:]
                    cursor += len(replacement)
                cursor += 1
            data = [x for x in data if x != ''] #remove blank strings
            cursor = 0
            while cursor < len(data):
                prop = data[cursor]
                if not type(prop) == str:
                    raise Exception()
                prop = prop.strip()
                if not prop in FGD.properties:
                    raise Exception('unrecognized entity property')
                if prop == 'halfgridsnap':
                    self.display.append([prop, None])
                    cursor += 1
                else:
                    self.display.append([prop, data[cursor+1]])
                    cursor += 2

            #inherit classes named via base()
            for e in self.display:
                if e[0] == 'base':
                    bases = [x.strip() for x in e[1][0].split(',')] #get list of classes to inherit from
                    for base in bases:
                        base = self.parent.entities[base]
                        for param in base.parameters:
                            self.parameters[param.name] = param
                        for param in base.inputs:
                            self.inputs[param.name] = param
                        for param in base.outputs:
                            self.outputs[param.name] = param
            
            #parse parameters
            cursor = 0
            while cursor < len(parameters):
                data = parameters[cursor].lower()
                if data.endswith('='):
                    data = data[:-1]
                data = data.split(':')
                data = [x.strip() for x in data]
                data[0] = FGD.parseNested(data[0], '(', ')')
                data[0][0] = data[0][0].split(' ')

                kind = None
                if data[0][0][0] in ['input','output']:
                    kind = data[0][0][0]
                    data[0][0] = data[0][0][1:]
                name = data[0][0][0]
                valueType = data[0][1][0].strip().lower()
                shortDescription = None
                longDescription = None
                default = None
                choices = None
                if len(data) >= 2:
                    shortDescription = parent.stringDict[ data[1] ]
                if len(data) >= 3 and data[2] != '':
                    try:
                        default = str(int(data[2]))
                    except:
                        default = parent.stringDict[ data[2] ]
                if len(data) >= 4:
                    longDescription = parent.stringDict[ data[3] ]
                if valueType == 'choices' or valueType == 'flags':
                    if valueType == 'flags':
                        flagDefault = 0
                    
                    cursor += 1
                    temp = [x for x in parameters[cursor] if x != '']
                    choices = dict()
                    for line in temp:
                        line = [x.strip() for x in line.split(':')]
                        try:
                            line[0] = int(line[0])
                        except:
                            line[0] = parent.stringDict[ line[0] ]
                        try:
                            line[1] = int(line[1])
                        except:
                            line[1] = parent.stringDict[ line[1] ]
                        if valueType == 'flags':
                            if line[2] == '1':
                                flagDefault += int(line[0])
                        choices[line[0]] = line[1]
                    
                    if valueType == 'flags':
                        default = str(flagDefault)

                try:
                    valueType = self._convertType(valueType)
                    default = self._parseDefault(valueType, default, choices)
                    
                    param = FGD.Parameter(name, valueType, default, shortDescription, longDescription, choices)
                    if kind == 'input':
                        self.inputs[param.name] = param
                    elif kind == 'output':
                        self.outputs[param.name] = param
                    elif kind == None:
                        self.parameters[param.name] = param
                    else:
                        raise Exception('Parameter must only be prepended with input or output.')
                except Exception as e:
                    print("Exception", e)
                    print("|".join([str(x) for x in [valueType, default, choices, shortDescription, longDescription]]))
                cursor += 1
            
            #convert inputs, outputs, parameters into lists
            self.inputs = self.inputs.values()
            self.outputs = self.outputs.values()
            self.parameters = self.parameters.values()
        
        def _convertType(self, _type):
            for conversionType in FGD._CONVERSION.keys():
                if _type in FGD._CONVERSION[conversionType]:
                    return conversionType
            
            raise Exception("Could not convert type: " + _type)
        
        def _parseDefault(self, _type, default, choices):
            assert(_type in FGD._CONVERSION.keys())
            if _type == FGD.BOOLEAN:
                if default != None:
                    try:
                        return bool(default)
                    except ValueError:
                        return False
                else:
                    return False
            elif _type == FGD.INTEGER:
                if default != None:
                    try:
                        return int(default)
                    except ValueError:
                        return 0
                else:
                    return 0
            elif _type == FGD.FLOAT:
                if default != None:
                    try:
                        return float(default)
                    except ValueError:
                        return 0.0
                else:
                    return 0.0
            elif _type == FGD.INTEGER_LIST:
                if default != None:
                    return SDKUtil.getNumbers(default, int)
                else:
                    return [0,0,0]
            elif _type in (FGD.VECTOR, FGD.FLOAT_LIST, FGD.ANGLE):
                if default != None:
                    return SDKUtil.getNumbers(default, float)
                else:
                    return [0.0, 0.0, 0.0]
            elif _type == FGD.ANGLE:
                if default != None:
                    # Convert from YZX to XYZ
                    angle = SDKUtil.getNumbers(default, float)
                    return [angle[2], angle[0], angle[1]]
                else:
                    return [0.0, 0.0, 0.0]
            elif _type == FGD.AXIS:
                if default != None:
        
                    floats = SDKUtil.getNumbers(default, float)
                    return [floats[0:3],floats[3:6]]
                else:
                    [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
            elif _type == FGD.CHOICE:
                if default == None:
                    default = tuple(choices.keys())[0]
                    
                # Turn to integer if possible
                try:
                    default = int(default)
                except ValueError:
                    pass
                
                return default
            elif _type == FGD.STRING:
                if default != None:
                    return default
                else:
                    return ""
            elif _type == FGD.VOID:
                return None
            else:
                raise Exception("Not supported type.")

    ## container for parameter data
    class Parameter:

        ## constructor
        #
        #  @param name name
        #  @param _type data type
        #  @param default default value
        #  @param summary summary of purpose
        #  @param description explanation of purpose
        #  @param choices dictionary of multiple choice options
        #
        def __init__(self, name, _type, default, summary, description, choices):
            ## name of parameter
            self.name = name
            ## data type
            self.type = _type
            ## default value
            self.default = default
            ## summary of purpose
            self.summary = summary
            ## longer explanation
            self.description = description
            ## dictionary of valid multiple choice options if data type is 'choices'
            self.choices = choices
        
        def __repr__(self):
            return "FGD.Entity.Parameter[name=%s type=%s default=%s summary=%s description=%s choices=%s]" % (self.name, self.type, self.default, self.summary, self.description, self.choices)

