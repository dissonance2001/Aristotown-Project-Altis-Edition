"""Level.py: contains the Level class"""

import string
import types
from toontown.level import LevelConstants
from toontown.level.editor import EditorGlobals
from direct.showbase.PythonUtil import lineInfo, uniqueElements, uniqueName
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

"""
Any data that can be edited by a level editor must be represented as
an attribute of an entity owned by the level, in order to keep the
level-editing interface simple and constant (there are at least three
places where the entire editing interface must be duplicated).
To support this, we have entities such as 'levelMgr' and 'zoneEntity' that
contain crucial level information, much of which is needed when setting
up the level object, and is needed before other entity types can be
effectively created. (If you try to create a distributed entity, but
you don't yet have the information for the zone that it's in, because
you haven't created the zone's ZoneEntity, you're hurting.)
"""

"""
ZONE TERMINOLOGY
zoneNum / zoneEntId: the number that a modeler chooses for a zone, and also
                     the entity ID of the ZoneEntity that represents a zone
zoneId: the network ID of a zone
"""


@DirectNotifyCategory()
class Level:
    """Level: representation of a game level, keeps track of all of the
    entities and their interrelations, and creates and destroys entities"""
    EntityPriorityTypes = ['levelMgr', 'zone', 'propSpinner']

    @property
    def levelType(self):
        return LevelConstants.LevelType.Standard

    def __init__(self):
        self.levelSpec = None
        self.initialized = 0
        # in case our instance doesn't have self.uniqueName, we'll manually generate 'unique names', and use those in
        # its place
        self.__manualEventNames = {}

    def initializeLevel(self, levelId, levelSpec, scenarioIndex):
        """subclass should call this as soon as it has located
        its spec data. levelId should be a unique integer (a doId works
        just fine) that differentiates this level from all other levels
        that may exist concurrently."""
        self.levelId = levelId
        self.levelSpec = levelSpec
        self.scenarioIndex = scenarioIndex

        self.levelSpec.setScenario(self.scenarioIndex)

        if EditorGlobals.wantLevelEditor():
            self.levelSpec.setLevel(self)

        # create some handy tables

        # entranceId to entrance entity
        self.entranceId2entity = {}

        # dict of entId -> list of callbacks to be called upon creation
        self.entId2createCallbacks = {}

        # this list contains the entIds of entities that we have actually
        # created, in order of creation
        self.createdEntIds = []

        # non-ordered list of entIds of entities that are not 'local', i.e.
        # they are created by someone else (i.e. the AI) and will come and go.
        self.nonlocalEntIds = {}

        # non-ordered list of entIds of entities that do not ever have any
        # representation on this side (i.e. client-side or AI-side). Populated
        # as the entities get their turn to be created.
        self.nothingEntIds = {}

        # get an entity creator object
        self.entityCreator = self.createEntityCreator()

        # entity type -> list of entIds
        self.entType2ids = self.levelSpec.getEntType2ids(self.levelSpec.getAllEntIds())

        # create empty list for any entity types that are not represented
        # in the spec
        for entType in self.entityCreator.getEntityTypes():
            self.entType2ids.setdefault(entType, [])

        # Create all the entities
        self.createAllEntities(priorityTypes=self.EntityPriorityTypes)

        # check on the singleton entities
        # we make our own references to them rather than expect them to
        # create the references so that the editor can create dummy
        # do-nothing entities

        # there should be one and only one levelMgr
        self.levelMgrEntity = self.getEntity(LevelConstants.LevelMgrEntId)
        # there should be one and only one UberZone
        self.uberZoneEntity = self.getEntity(LevelConstants.UberZoneEntId)

        if EditorGlobals.wantLevelEditor():
            self.editMgrEntity = self.getEntity(LevelConstants.EditMgrEntId)
        else:
            self.editMgrEntity = None  # Don't generate an edit mgr on live

        self.initialized = 1

    def isInitialized(self):
        return self.initialized

    def getLevelId(self):
        return self.levelId

    def destroyLevel(self):
        if self.initialized:
            self.destroyAllEntities()
            del self.levelMgrEntity
            del self.uberZoneEntity
            del self.editMgrEntity
            del self.entityCreator
            del self.entId2createCallbacks
            del self.entranceId2entity
            self.levelSpec.destroy()
            del self.levelSpec
            del self.createdEntIds
            del self.nonlocalEntIds
            del self.nothingEntIds
        self.initialized = 0
        if hasattr(self, 'entities'):
            del self.entities
        if hasattr(self, 'levelSpec'):
            self.levelSpec.destroy()
            del self.levelSpec

    def createEntityCreator(self):
        Level.notify.error('concrete Level class must override %s' % lineInfo()[2])

    def createAllEntities(self, priorityTypes = []):
        """creates all entities in the spec. priorityTypes is an
        optional ordered list of entity types to create first."""
        # this will be filled in as the entities are created and report in
        # this includes distributed objects on the client
        self.entities = {}

        # get list of all entity types we need to create
        entTypes = self.entityCreator.getEntityTypes()

        self.onLevelPreCreate()

        # first create the types in the priority list
        for type in priorityTypes:
            self.createAllEntitiesOfType(type)
            entTypes.remove(type)

        # create the other entities in any old order
        for type in entTypes:
            self.createAllEntitiesOfType(type)

        self.onLevelPostCreate()

    def destroyAllEntities(self):
        self.nonlocalEntIds = {}
        self.nothingEntIds = {}
        # destroy the entities that we created in reverse order
        if not uniqueElements(self.createdEntIds):
            Level.notify.warning('%s: self.createdEntIds is not unique: %s' % (getattr(self, 'doId', None), self.createdEntIds))
        while len(self.createdEntIds) > 0:
            entId = self.createdEntIds.pop()
            entity = self.getEntity(entId)
            if entity is not None:
                Level.notify.debug('destroying %s %s' % (self.getEntityType(entId), entId))
                entity.destroy()
            else:
                Level.notify.error('trying to destroy entity %s, but it is already gone' % entId)

    def createAllEntitiesOfType(self, entType):
        """creates all entities of a given type"""

        self.onEntityTypePreCreate(entType)

        for entId in self.entType2ids[entType]:
            self.createEntity(entId)

        self.onEntityTypePostCreate(entType)

    def createEntity(self, entId):
        spec = self.levelSpec.getEntitySpec(entId)
        Level.notify.debug('creating %s %s' % (spec['type'], entId))
        entity = self.entityCreator.createEntity(entId)
        # NOTE: the entity is not considered to really be created until
        # it has all of its initial spec data; see 'initializeEntity'
        # below.
        announce = False
        if entity == 'nonlocal':
            self.nonlocalEntIds[entId] = None
        elif entity == 'nothing':
            self.nothingEntIds[entId] = None
            announce = True
        else:
            self.createdEntIds.append(entId)
            announce = True

        if announce:
            # call the create handler
            # we used to do this in initializeEntity, but that did not
            # allow for additional initialization to be performed in
            # derived entity __init__ funcs before their presence was announced
            # Note that now DistributedEntity's are responsible for calling
            # this for themselves
            self.onEntityCreate(entId)

        return entity

    def initializeEntity(self, entity):
        """populate an entity with its spec data. This is not done
        in createEntity in order to allow other pieces of code to create
        entities; this is called directly by Entity.
        """
        entId = entity.entId
        spec = self.levelSpec.getEntitySpec(entId)
        # on initialization, set items directly on entity
        for key, value in list(spec.items()):
            if key in ('type', 'name', 'comment'):
                continue
            entity.setAttribInit(key, value)

        # entity is initialized, add it to the list of entities
        # Make sure they're calling down to Entity.destroy
        self.entities[entId] = entity

    def getEntity(self, entId):
        if hasattr(self, 'entities'):
            return self.entities.get(entId)
        return None

    def getEntitiesOfType(self, entityType: str):
        return [entity for entity in self.entities.values() if self.getEntityType(entity.entId) == entityType]

    def getEntityType(self, entId):
        return self.levelSpec.getEntityType(entId)

    def getEntityZoneEntId(self, entId):
        """return entId of zone that contains the entity"""
        return self.levelSpec.getEntityZoneEntId(entId)

    def getEntityZoneId(self, entId):
        """return network zoneId of zone that contains the entity"""
        # this is called during entity creation on the AI; we have to
        # handle this carefully, since the information required to
        # produce a zoneId is not available until the level's zone
        # entities have been instantiated.
        zoneEntId = self.getEntityZoneEntId(entId)
        # fundamental entities (levelMgr) are responsible for creating
        # tables like 'zoneNum2zoneId'; if those tables haven't been
        # created yet, just return None
        if not hasattr(self, 'zoneNum2zoneId'):
            return None
        # this might return None if all of our zone entities haven't
        # been created yet. this could be a problem if zone entities
        # are ever distributed. it also means that no distributed entities
        # should be created before the zone entities.
        return self.zoneNum2zoneId.get(zoneEntId)

    def getZoneId(self, zoneEntId):
        """look up network zoneId by zone entId"""
        return self.zoneNum2zoneId[zoneEntId]

    def getZoneNumFromId(self, zoneId):
        """returns the model zoneNum that corresponds to a network zoneId"""
        return self.zoneId2zoneNum[zoneId]

    def getParentTokenForEntity(self, entId):
        """returns a unique parent token for this entity"""
        # default impl
        # subclasses can override to allow for multiple levels present
        # on the client simultaneously
        return entId

    # these events are thrown as the level initializes itself
    # LEVEL
    def getLevelPreCreateEvent(self):
        """This is the event that is thrown immediately before the level
        creates its entities."""
        if hasattr(self, 'uniqueName'):
            return self.uniqueName(f'levelPreCreate-{self.levelId}')
        else:
            if 'levelPreCreateEvent' not in self.__manualEventNames:
                self.__manualEventNames['levelPreCreateEvent'] = uniqueName(f'levelPreCreate-{self.levelId}')
            return self.__manualEventNames['levelPreCreateEvent']

    def getLevelPostCreateEvent(self):
        """This is the event that is thrown immediately after the level
        creates its entities."""
        if hasattr(self, 'uniqueName'):
            return self.uniqueName(f'levelPostCreate-{self.levelId}')
        else:
            if 'levelPostCreateEvent' not in self.__manualEventNames:
                self.__manualEventNames['levelPostCreateEvent'] = uniqueName(f'levelPostCreate-{self.levelId}')
            return self.__manualEventNames['levelPostCreateEvent']

    # ENTITY TYPE
    def getEntityTypePreCreateEvent(self, entType):
        """This is the event that is thrown immediately before the level
        creates the entities of the given type."""
        if hasattr(self, 'uniqueName'):
            return self.uniqueName(f'entityTypePreCreate-{self.levelId}-{entType}')
        else:
            if 'entityTypePreCreateEvent' not in self.__manualEventNames:
                self.__manualEventNames['entityTypePreCreateEvent'] = uniqueName(f'entityTypePreCreate-{self.levelId}')
            return self.__manualEventNames['entityTypePreCreateEvent'] + f'-{entType}'

    def getEntityTypePostCreateEvent(self, entType):
        """This is the event that is thrown immediately after the level
        creates the entities of the given type."""
        if hasattr(self, 'uniqueName'):
            return self.uniqueName(f'entityTypePostCreate-{self.levelId}-{entType}')
        else:
            if 'entityTypePostCreateEvent' not in self.__manualEventNames:
                self.__manualEventNames['entityTypePostCreateEvent'] = uniqueName(f'entityTypePostCreate-{self.levelId}')
            return self.__manualEventNames['entityTypePostCreateEvent'] + f'-{entType}'

    # ENTITY
    def getEntityCreateEvent(self, entId):
        """This is the event that is thrown immediately after a
        particular entity is initialized"""
        if hasattr(self, 'uniqueName'):
            return self.uniqueName(f'entityCreate-{self.levelId}-{entId}')
        else:
            if 'entityCreateEvent' not in self.__manualEventNames:
                self.__manualEventNames['entityCreateEvent'] = uniqueName(f'entityCreate-{self.levelId}')
            return self.__manualEventNames['entityCreateEvent'] + f'-{entId}'

    def getEntityOfTypeCreateEvent(self, entType):
        """This event is thrown immediately after each instance of the
        given entity type is created; handlers must accept an entId"""
        if hasattr(self, 'uniqueName'):
            return self.uniqueName(f'entityOfTypeCreate-{self.levelId}-{entType}')
        else:
            if 'entityOfTypeCreateEvent' not in self.__manualEventNames:
                self.__manualEventNames['entityOfTypeCreateEvent'] = uniqueName(f'entityOfTypeCreate-{self.levelId}')
            return self.__manualEventNames['entityOfTypeCreateEvent'] + f'-{entType}'

    # these handlers are called as the level initializes itself
    # LEVEL
    def onLevelPreCreate(self):
        """Level is about to create its entities"""
        messenger.send(self.getLevelPreCreateEvent())

    def onLevelPostCreate(self):
        """Level is done creating its entities"""
        messenger.send(self.getLevelPostCreateEvent())

    # ENTITY TYPE
    def onEntityTypePreCreate(self, entType):
        """Level is about to create these entities"""
        messenger.send(self.getEntityTypePreCreateEvent(entType))

    def onEntityTypePostCreate(self, entType):
        """Level has just created these entities"""
        messenger.send(self.getEntityTypePostCreateEvent(entType))

    # ENTITY
    def onEntityCreate(self, entId):
        """Level has just created this entity"""
        # send the entity-create event
        messenger.send(self.getEntityCreateEvent(entId))
        # send the entity-of-type create event
        messenger.send(self.getEntityOfTypeCreateEvent(self.getEntityType(entId)), [entId])
        # call any callbacks
        if entId in self.entId2createCallbacks:
            for callback in self.entId2createCallbacks[entId]:
                callback()

            del self.entId2createCallbacks[entId]

    # Use to set a callback to be called when entity is created.
    # If entity already exists, callback will be called immediately.
    def setEntityCreateCallback(self, entId, callback):
        ent = self.getEntity(entId)
        if ent is not None:
            # entity already exists
            callNow = True
        elif entId in self.nothingEntIds:
            # entity has been 'created' but will never manifest
            callNow = True
        else:
            # entity has not been created
            callNow = False

        if callNow:
            callback()
        else:
            self.entId2createCallbacks.setdefault(entId, [])
            self.entId2createCallbacks[entId].append(callback)

    # these are events and handlers that are invoked as entities are destroyed
    def getEntityDestroyEvent(self, entId):
        """This is the event that is thrown immediately before an
        entity is destroyed"""
        if hasattr(self, 'uniqueName'):
            return self.uniqueName(f'entityDestroy-{self.levelId}-{entId}')
        else:
            if 'entityDestroyEvent' not in self.__manualEventNames:
                self.__manualEventNames['entityDestroyEvent'] = uniqueName(f'entityDestroy-{self.levelId}')
            return self.__manualEventNames['entityDestroyEvent'] + f'-{entId}'

    def onEntityDestroy(self, entId):
        """Level is about to destroy this entity"""
        # send the entity-destroy event
        messenger.send(self.getEntityDestroyEvent(entId))

        del self.entities[entId]
        # if we created this entity, remove its entId from the
        # createdEntIds list
        if entId in self.createdEntIds:
            # this should only happen if someone deleted an entity
            # with an editor
            self.createdEntIds.remove(entId)

    def handleVisChange(self):
        """the zone visibility lists have changed"""
        pass

    if EditorGlobals.wantLevelEditor():
        def getAttribChangeEventName(self):
            return 'attribChange-%s' % self.levelId

        def getInsertEntityEventName(self):
            return 'insertEntity-%s' % self.levelId

        def getRemoveEntityEventName(self):
            return 'removeEntity-%s' % self.levelId

        def handleAttribChange(self, entId, attrib, value, username = None):
            entity = self.getEntity(entId)
            if entity is not None:
                entity.handleAttribChange(attrib, value)
            messenger.send(self.getAttribChangeEventName(), [entId, attrib, value, username])
            return

        def setEntityCreatorUsername(self, entId, editUsername):
            pass

        def handleEntityInsert(self, entId):
            self.entType2ids[self.getEntityType(entId)].append(entId)
            self.createEntity(entId)
            messenger.send(self.getInsertEntityEventName(), [entId])

        def handleEntityRemove(self, entId):
            messenger.send(self.getRemoveEntityEventName(), [entId])
            if entId in self.createdEntIds:
                entity = self.getEntity(entId)
                entity.destroy()
            elif entId in self.nothingEntIds:
                del self.nothingEntIds[entId]
            elif entId in self.nonlocalEntIds:
                del self.nonlocalEntIds[entId]
            self.entType2ids[self.getEntityType(entId)].remove(entId)
