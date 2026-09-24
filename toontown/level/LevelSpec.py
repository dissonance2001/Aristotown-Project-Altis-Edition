"""LevelSpec module: contains the LevelSpec class"""

import types
from panda3d.core import HashVal
from direct.showbase.PythonUtil import list2dict, safeRepr
from toontown.level import LevelConstants
from toontown.level.editor import EditorGlobals
import os
import json

if EditorGlobals.wantLevelEditor():
    import importlib
    from toontown.level.SpecImports import *


from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class LevelSpec:
    """contains spec data for a level, is responsible for handing the data
    out upon request, as well as recording changes made during editing, and
    saving out modified spec data"""

    SystemEntIds = (LevelConstants.UberZoneEntId,
                    LevelConstants.LevelMgrEntId,
                    LevelConstants.EditMgrEntId)
    ValueTypeName2Type = {
        "LPoint3f": LPoint3f,
        "LVector3f": LVector3f,
        "LVector4f": LVector4f,
        "tuple": tuple,
    }

    def __init__(self, spec=None, scenario=0):
        """spec must be passed in as a python module or a dictionary.
        If not passed in, will create a new spec."""
        newSpec = 0

        self.jsonData = False

        def getNewEditMgr():
            return {'type': 'editMgr', 'name': 'EditMgr', 'parentEntId': 0, 'insertEntity': None, 'removeEntity': None, 'requestNewEntity': None, 'requestSave': None}

        if isinstance(spec, types.ModuleType):
            if EditorGlobals.wantLevelEditor():
                # reload the spec module to pick up changes
                importlib.reload(spec)
            self.specDict = spec.levelSpec
            if EditorGlobals.wantLevelEditor():
                self.specDict['globalEntities'][LevelConstants.EditMgrEntId] = getNewEditMgr()
                self.setFilename(spec.__file__)
        elif isinstance(spec, str):
            self.jsonData = True
            self.specDict = self.privLoadJsonData(spec)
            if EditorGlobals.wantLevelEditor():
                self.specDict['globalEntities'][LevelConstants.EditMgrEntId] = getNewEditMgr()
                vfs = VirtualFileSystem.getGlobalPtr()
                self.setFilename(Filename.expandFrom(f'../resources/{spec}').toOsSpecific())
        elif isinstance(spec, dict):
            # we need this for repr/eval-ing LevelSpecs
            self.specDict = spec
        elif spec is None:
            if EditorGlobals.wantLevelEditor():
                newSpec = 1
                self.specDict = {'globalEntities': {},
                                 'scenarios': [{}]}

        # this maps an entId to the dict that holds its spec;
        # entities are either in the global dict or a scenario dict
        # update the map of entId to spec dict
        self.entId2specDict = {}
        self.entId2specDict.update(list2dict(self.getGlobalEntIds(), value=self.privGetGlobalEntityDict()))
        for i in range(self.getNumScenarios()):
            self.entId2specDict.update(list2dict(self.getScenarioEntIds(i), value=self.privGetScenarioEntityDict(i)))

        self.setScenario(scenario)

        if EditorGlobals.wantLevelEditor():
            if newSpec:
                # add basic required entities
                from . import EntityTypes
                from . import EntityTypeRegistry
                etr = EntityTypeRegistry.EntityTypeRegistry(EntityTypes)
                self.setEntityTypeReg(etr)

                # UberZone
                entId = LevelConstants.UberZoneEntId
                self.insertEntity(entId, 'zone')
                self.doSetAttrib(entId, 'name', 'UberZone')
                # LevelMgr
                entId = LevelConstants.LevelMgrEntId
                self.insertEntity(entId, 'levelMgr')
                self.doSetAttrib(entId, 'name', 'LevelMgr')
                # EditMgr
                entId = LevelConstants.EditMgrEntId
                self.insertEntity(entId, 'editMgr')
                self.doSetAttrib(entId, 'name', 'EditMgr')

    @staticmethod
    def privLoadJsonData(dataPath):
        # First, we need to actually do some re-formatting to the data,
        # so that json can load the string.
        if __debug__:
            dataPath = '../resources/' + dataPath
        dataPath = Filename(dataPath)

        vfs = VirtualFileSystem.getGlobalPtr()
        jsonDict = json.loads(vfs.readFile(dataPath, True))

        def getNewValue(value):
            if type(value) is dict and len(value) == 1:
                for typeNameReplacement in LevelSpec.ValueTypeName2Type.keys():
                    if typeNameReplacement in value.keys():
                        replaceClass = LevelSpec.ValueTypeName2Type[typeNameReplacement]
                        return replaceClass(
                            (*value[typeNameReplacement],)) if typeNameReplacement == 'tuple' else replaceClass(
                            *value[typeNameReplacement])

            return value

        def getNewDict(existingDict):
            newDict = {}
            for entId, entityDict in existingDict.items():
                newEntityDict = {}
                for varKey in entityDict:
                    newEntityDict[varKey] = getNewValue(entityDict[varKey])
                newDict[int(entId)] = newEntityDict

            return newDict

        newGlobalDict = dict(globalEntities=getNewDict(jsonDict['globalEntities']), scenarios=[])
        for i in range(len(jsonDict['scenarios'])):
            newGlobalDict['scenarios'].append(getNewDict(jsonDict['scenarios'][i]))

        return newGlobalDict

    def destroy(self):
        del self.specDict
        del self.entId2specDict
        del self.scenario
        if hasattr(self, 'level'):
            del self.level
        if hasattr(self, 'entTypeReg'):
            del self.entTypeReg

    def getNumScenarios(self):
        return len(self.specDict['scenarios'])

    def setScenario(self, scenario):
        self.scenario = scenario

    def getScenario(self):
        return self.scenario

    def getGlobalEntIds(self):
        return list(self.privGetGlobalEntityDict().keys())

    def getScenarioEntIds(self, scenario = None):
        if scenario is None:
            scenario = self.scenario
        return list(self.privGetScenarioEntityDict(scenario).keys())

    def getAllEntIds(self):
        """this returns all of the entIds involved in the current scenario"""
        return self.getGlobalEntIds() + self.getScenarioEntIds()

    def getAllEntIdsFromAllScenarios(self):
        """this returns all of the entIds involved in all scenarios"""
        entIds = self.getGlobalEntIds()
        for scenario in range(self.getNumScenarios()):
            entIds.extend(self.getScenarioEntIds(scenario))

        return entIds

    def getEntitySpec(self, entId):
        specDict = self.entId2specDict[entId]
        return specDict[entId]

    if EditorGlobals.wantLevelEditor():
        @staticmethod
        def getCopyOfSpec(spec):
            # Return a copy of the spec, making sure that none of the attributes
            # are shared between the original and the copy (i.e. Point3's)
            specCopy = {}

            for key in list(spec.keys()):
                specCopy[key] = eval(repr(spec[key]))
            return specCopy

    def getEntitySpecCopy(self, entId):
        # return a copy of the spec, making sure that none of the attributes
        # are shared between the original and the copy (i.e. Point3's)
        specDict = self.entId2specDict[entId]
        return self.getCopyOfSpec(specDict[entId])

    def getEntityType(self, entId):
        return self.getEntitySpec(entId)['type']

    def getEntityZoneEntId(self, entId):
        """ return the entId of the zone that entity is in; if entity
        is a zone, returns its entId """
        spec = self.getEntitySpec(entId)
        specType = spec['type']
        # if it's a zone, this is our entity
        if specType == 'zone':
            return entId
        # keep looking up the heirarchy for a zone entity
        return self.getEntityZoneEntId(spec['parentEntId'])

    def getEntType2ids(self, entIds):
        """given list of entIds, return dict of entType->entIds"""
        entType2ids = {}
        for entId in entIds:
            specType = self.getEntityType(entId)
            entType2ids.setdefault(specType, [])
            entType2ids[specType].append(entId)

        return entType2ids

    # private support functions to abstract dict structure
    def privGetGlobalEntityDict(self):
        return self.specDict['globalEntities']

    def privGetScenarioEntityDict(self, scenario):
        return self.specDict['scenarios'][scenario]

    def printZones(self):
        """currently prints list of zoneNum->zone name"""
        # this could be more efficient
        allIds = self.getAllEntIds()
        type2id = self.getEntType2ids(allIds)
        zoneIds = type2id['zone']
        # omit the UberZone
        if 0 in zoneIds:
            zoneIds.remove(0)
        zoneIds.sort()
        for zoneNum in zoneIds:
            spec = self.getEntitySpec(zoneNum)
            print('zone %s: %s' % (zoneNum, spec['name']))

    if EditorGlobals.wantLevelEditor():
        def setLevel(self, level):
            self.level = level

        def hasLevel(self):
            return hasattr(self, 'level')

        def setEntityTypeReg(self, entTypeReg):
            self.entTypeReg = entTypeReg
            for entId in self.getAllEntIds():
                spec = self.getEntitySpec(entId)
                entityType = self.getEntityType(entId)
                typeDesc = self.entTypeReg.getTypeDesc(entityType)
                attribDescDict = typeDesc.getAttribDescDict()
                for attribName, desc in attribDescDict.items():
                    if attribName not in spec:
                        spec[attribName] = desc.getDefaultValue()

            self.checkSpecIntegrity()

        def hasEntityTypeReg(self):
            return hasattr(self, 'entTypeReg')

        def setFilename(self, filename):
            self.filename = filename

        def doSetAttrib(self, entId, attrib, value):
            """do the dirty work of changing an attrib value"""
            specDict = self.entId2specDict[entId]
            specDict[entId][attrib] = value

        def setAttribChange(self, entId, attrib, value, username):
            """ we're being asked to change an attribute """
            LevelSpec.notify.info('setAttribChange(%s): %s, %s = %s' % (username, entId, attrib, repr(value)))
            self.doSetAttrib(entId, attrib, value)
            if self.hasLevel():
                # let the level know that this attribute value has
                # officially changed
                self.level.handleAttribChange(entId, attrib, value, username)

        def insertEntity(self, entId, entType, parentEntId = 'unspecified'):
            LevelSpec.notify.info('inserting entity %s (%s)' % (entId, entType))
            globalEnts = self.privGetGlobalEntityDict()
            self.entId2specDict[entId] = globalEnts

            # create a new entity spec entry w/ default values
            globalEnts[entId] = {}
            spec = globalEnts[entId]
            attribDescs = self.entTypeReg.getTypeDesc(entType).getAttribDescDict()
            for name, desc in list(attribDescs.items()):
                spec[name] = desc.getDefaultValue()

            spec['type'] = entType
            if parentEntId != 'unspecified':
                spec['parentEntId'] = parentEntId

            if self.hasLevel():
                # notify the level
                self.level.handleEntityInsert(entId)
            else:
                LevelSpec.notify.warning('no level to be notified of insertion')

        """ this was never used/tested but may come in handy
        def insertEntityWithSpec(self, entId, spec):
            # use this to add an entity with an existing spec
            # NOTE: DO NOT use this to add an entity with an editor; this
            # will not propogate the spec to the level. For now, editors
            # should manually insert the item and set each attribute
            # individually.
            self.insertEntity(entId, spec['type'])
            specCopy = self.getCopyOfSpec(spec)
            del specCopy['type']
            for attribName, value in specCopy.items():
                self.doSetAttrib(entId, attribName, value)
                """

        def removeEntity(self, entId):
            LevelSpec.notify.info('removing entity %s' % entId)
            if self.hasLevel():
                # notify the level
                self.level.handleEntityRemove(entId)
            else:
                LevelSpec.notify.warning('no level to be notified of removal')

            # remove the entity's spec
            dict = self.entId2specDict[entId]
            del dict[entId]
            del self.entId2specDict[entId]

        def removeZoneReferences(self, removedZoneNums):
            """call with a list of zoneNums of zone entities that have just
            been removed; will clean up references to those zones"""
            # get dict of entType->entIds, for ALL scenarios
            type2ids = self.getEntType2ids(self.getAllEntIdsFromAllScenarios())
            # figure out which entity types have attributes that need to be
            # updated
            for type in type2ids:
                typeDesc = self.entTypeReg.getTypeDesc(type)
                visZoneListAttribs = typeDesc.getAttribsOfType('visZoneList')
                if len(visZoneListAttribs) > 0:
                    # this entity type has at least one attrib of type
                    # 'visZoneList'.
                    # run through all of the existing entities of this type
                    for entId in type2ids[type]:
                        spec = self.getEntitySpec(entId)
                        # for each attrib of type 'visZoneList'...
                        for attribName in visZoneListAttribs:
                            # remove each of the removed zoneNums
                            for zoneNum in removedZoneNums:
                                while zoneNum in spec[attribName]:
                                    spec[attribName].remove(zoneNum)

        @staticmethod
        def getSpecImportsModuleName():
            # name of module that should be imported by spec py file
            return 'toontown.level.SpecImports'

        def getFilename(self):
            """
            Only used for documentation purposes.

            :returns: a filename if it makes sense for the particular item.
            """
            return self.filename

        @staticmethod
        def privGetBackupFilename(filename):
            return '%s.bak' % filename

        def saveToDisk(self, filename=None, makeBackup=1):
            """returns zero on failure"""
            if filename is None:
                filename = self.filename
                if filename.endswith('.pyc'):
                    filename = filename.replace('.pyc', '.py')

            if makeBackup and self.privFileExists(filename):
                # create a backup
                try:
                    backupFilename = self.privGetBackupFilename(filename)
                    self.privRemoveFile(backupFilename)
                    os.rename(filename, backupFilename)
                except OSError as e:
                    LevelSpec.notify.warning('error during backup: %s' % str(e))

            LevelSpec.notify.info("writing to '%s'" % filename)
            self.privRemoveFile(filename)
            if self.jsonData:
                returnVal = self.privSaveJsonToDisk(filename)
            else:
                returnVal = self.privSaveToDisk(filename)
            return returnVal

        def privSaveToDisk(self, filename):
            """internal. saves spec to file. returns zero on failure"""
            retval = 1
            # wb to create a UNIX-format file
            f = open(filename, 'wb')
            try:
                f.write(self.getPrettyString().encode())
            except IOError:
                retval = 0

            f.close()
            return retval

        def privSaveJsonToDisk(self, filename):
            f = open(filename, mode='w')
            retval = 1
            try:
                json.dump(self.getJsonSafeDict(), f, indent=4)
            except OSError:
                retval = 0

            f.close()
            return retval

        @staticmethod
        def privFileExists(filename):
            try:
                os.stat(filename)
                return 1
            except OSError:
                return 0

        @staticmethod
        def privRemoveFile(filename):
            try:
                os.remove(filename)
                return 1
            except OSError:
                return 0

        def getPrettyString(self):
            """Returns a string that contains the spec data, nicely formatted.
            This should be used when writing the spec out to file."""
            import pprint

            tabWidth = 4
            tab = ' ' * tabWidth
            # structure names
            globalEntitiesName = 'GlobalEntities'
            scenarioEntitiesName = 'Scenario%s'
            topLevelName = 'levelSpec'

            def getPrettyEntityDictStr(name, dict, tabs = 0):

                def t(n):
                    return (tabs + n) * tab

                def sortList(lst, firstElements = []):
                    """sort list; elements in firstElements will be put
                    first, in the order that they appear in firstElements;
                    rest of elements will follow, sorted"""
                    elements = list(lst)
                    # put elements in order
                    result = []
                    for el in firstElements:
                        if el in elements:
                            result.append(el)
                            elements.remove(el)

                    elements.sort()
                    result.extend(elements)
                    return result

                firstTypes = ('levelMgr', 'editMgr', 'zone')
                firstAttribs = ('type', 'name', 'comment', 'parentEntId',
                                'pos', 'x', 'y', 'z',
                                'hpr', 'h', 'p', 'r',
                                'scale', 'sx', 'sy', 'sz',
                                'color',
                                'model')
                str = t(0) + '%s = {\n' % name
                # get list of types
                entIds = list(dict.keys())
                entType2ids = self.getEntType2ids(entIds)
                # put types in order
                types = sortList(list(entType2ids.keys()), firstTypes)
                for type in types:
                    str += t(1) + '# %s\n' % type.upper()
                    entIds = entType2ids[type]
                    entIds.sort()
                    for entId in entIds:
                        str += t(1) + '%s: {\n' % entId
                        spec = dict[entId]
                        attribs = sortList(list(spec.keys()), firstAttribs)
                        for attrib in attribs:
                            str += t(2) + "'%s': %s,\n" % (attrib, repr(spec[attrib]))

                        # maybe this will help with github merges?
                        str += t(2) + '},  # end entity %s\n' % entId

                str += t(1) + '}\n'
                return str

            def getPrettyTopLevelDictStr(tabs = 0):

                def t(n):
                    return (tabs + n) * tab

                str = t(0) + '%s = {\n' % topLevelName
                str += t(1) + "'globalEntities': %s,\n" % globalEntitiesName
                str += t(1) + "'scenarios': [\n"
                for i in range(self.getNumScenarios()):
                    str += t(2) + '%s,\n' % (scenarioEntitiesName % i)

                str += t(2) + '],\n'
                str += t(1) + '}\n'
                return str

            str = 'from %s import *\n' % self.getSpecImportsModuleName()
            str += '\n'

            # add the global entities
            str += getPrettyEntityDictStr('GlobalEntities', self.privGetGlobalEntityDict())
            str += '\n'

            # add the scenario entities
            numScenarios = self.getNumScenarios()
            for i in range(numScenarios):
                str += getPrettyEntityDictStr('Scenario%s' % i, self.privGetScenarioEntityDict(i))
                str += '\n'

            # add the top-level table
            str += getPrettyTopLevelDictStr()

            self.testPrettyString(prettyString=str)

            return str

        def getJsonSafeDict(self):
            """Returns a dict that should be json-safe to export out to a resources file"""

            def getNewValue(value):
                varType = type(value)
                if varType in (LVector3f, LVector4f, LPoint3f, tuple):
                    return {f"{varType.__name__}": [*value]}

                return value

            def getNewDict(existingDict):
                newDict = {}
                for entId, entityDict in existingDict.items():
                    newEntityDict = {}
                    for varKey in entityDict:
                        newEntityDict[varKey] = getNewValue(entityDict[varKey])
                    newDict[str(entId)] = newEntityDict

                return newDict

            newGlobalDict = dict(globalEntities=getNewDict(self.privGetGlobalEntityDict()), scenarios=[])
            for i in range(self.getNumScenarios()):
                newGlobalDict['scenarios'].append(getNewDict(self.privGetScenarioEntityDict(i)))

            return newGlobalDict

        def _recurKeyTest(self, dict1, dict2):
            # recursive key test for testPrettyString
            # cannot be sub function due to exec call in testPrettyString
            s = ''  # error out string
            errorCount = 0  # number of non-matching keys; more or less

            # If set of keys don't match than they are not the same
            if set(dict1.keys()) != set(dict2.keys()):
                return 0
            for key in dict1:
                # if they are both dictionaries we must test the subkeys
                # this is because dicts are unordered and we are using repr to dump the
                # values into strings for comparision
                if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                    if not self._recurKeyTest(dict1[key], dict2[key]):
                        return 0
                # If they are not dicts turn the values into strings and compare the strings
                else:
                    strd1 = repr(dict1[key])
                    strd2 = repr(dict2[key])
                    if strd1 != strd2:
                        # If the strings don't match print an error
                        s += '\nBAD VALUE(%s): %s != %s\n' % (key, strd1, strd2)
                        errorCount += 1  # We could just bail here but instead we accumulate the errors

            print(s)
            if errorCount == 0:
                return 1
            else:
                return 0

        def testPrettyString(self, prettyString=None):
            pass

        def checkSpecIntegrity(self):
            # make sure there are no duplicate entIds
            entIds = self.getGlobalEntIds()
            entIds = list2dict(entIds)
            for i in range(self.getNumScenarios()):
                for id in self.getScenarioEntIds(i):
                    entIds[id] = None

            if self.entTypeReg is not None:
                # check each spec
                allEntIds = entIds
                for entId in allEntIds:
                    spec = self.getEntitySpec(entId)
                    entType = spec['type']
                    typeDesc = self.entTypeReg.getTypeDesc(entType)
                    attribNames = typeDesc.getAttribNames()
                    attribDescs = typeDesc.getAttribDescDict()

                    # are there any unknown attribs in the spec?
                    for attrib in list(spec.keys()):
                        if attrib not in attribNames:
                            LevelSpec.notify.warning("entId %s (%s): unknown attrib '%s', omitting" % (entId, spec['type'], attrib))
                            del spec[attrib]

                    # does the spec have all of its attributes?
                    for attribName in attribNames:
                        if attribName not in spec:
                            LevelSpec.notify.warning("entId %s (%s): missing attrib '%s'" % (entId, spec['type'], attribName))

        def stringHash(self):
            h = HashVal()
            h.hashString(repr(self))
            return h.asHex()

        def __hash__(self):
            return hash(repr(self))

        def __str__(self):
            return 'LevelSpec'

        def __repr__(self):
            return 'LevelSpec(%s, scenario=%s)' % (safeRepr(self.specDict), safeRepr(self.scenario))
