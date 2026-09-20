from direct.gui.OnscreenText import OnscreenText
from direct.interval.IntervalGlobal import *
from panda3d.core import *

from toontown.hood import ZoneUtil
from toontown.level import LevelSpec, LevelConstants
from toontown.level.editor import EditorGlobals
from toontown.level.DistributedLevel import DistributedLevel
from toontown.toonbase import TTLocalizer
from toontown.toonbase.ToontownGlobals import StreetNames, getSignFont
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.zone.ZoneSpecRegistry import ZoneSpecRegistry
from toontown.zone.base.PersistentLevelBase import PersistentLevelBase
from toontown.zone.data.TitleColorEnum import TitleColorRegistry
from toontown.zone.entities.PersistentLevelEntityCreator import PersistentLevelEntityCreator
from toontown.zone.cutscene.CutsceneHandler import CutsceneHandler


@DirectNotifyCategory()
class DistributedPersistentLevel(DistributedLevel, PersistentLevelBase):
    """
    A variant of DistributedLevel that can be accessed by many players at a time,
    and is persistent in the world.
    """
    EntityPriorityTypes = ['levelMgr', 'zone', 'propSpinner', 'buildingMgr']

    @property
    def levelType(self):
        return LevelConstants.LevelType.Persistent

    def __init__(self, cr):
        DistributedLevel.__init__(self, cr)
        PersistentLevelBase.__init__(self)
        self.cutsceneHandler = CutsceneHandler()

    def delete(self):
        self.cutsceneHandler.cleanup()
        self.cutsceneHandler = None
        super().delete()

    def addCutscene(self, *args, **kwargs):
        self.cutsceneHandler.addCutscene(*args, **kwargs)

    def initializeTitleText(self):
        self.titleText = OnscreenText(
            '',
            fg=(1, 1, 1, 1),
            font=getSignFont(),
            pos=(0, -0.5),
            scale=TTLocalizer.HtitleText,
            drawOrder=0,
            mayChange=1
        )
        self.smallTitleText = None

    def createEntityCreator(self):
        return PersistentLevelEntityCreator(level=self)

    def privGotSpec(self, levelSpec):
        """
        OK, we've got the spec that we're going to use, either the one
        we provided or the one from the AI. When we call down, the level
        is going to be initialized, and all the local entities will be
        created.
        """
        if EditorGlobals.wantLevelEditor():
            # First, give the spec a factory EntityTypeRegistry if it doesn't
            # have one.
            if not levelSpec.hasEntityTypeReg():
                typeReg = self.getEntityTypeReg()
                levelSpec.setEntityTypeReg(typeReg)

        ignoreLoad = bboard.get(LevelConstants.Bulletin_IgnoreLoad, False)
        # let 'er rip.
        DistributedLevel.privGotSpec(self, levelSpec)
        if not ignoreLoad:
            loader.endBulkLoad('persistentLevel')
        bboard.remove(LevelConstants.Bulletin_IgnoreLoad)

        # NOW we're ready.
        base.persistentLevelReady = 1
        messenger.send('PersistentLevelReady')

        ignoreTitleText = bboard.get(LevelConstants.Bulletin_IgnoreTitleText, False)
        if not ignoreTitleText:
            self.spawnTitleText(initialLoad=True)
        bboard.remove(LevelConstants.Bulletin_IgnoreTitleText)

        def printPos(self=self):
            # print position of localToon relative to the zone that he's in
            try:
                pos = base.localAvatar.getPos(self.getZoneNode(self.lastToonZone))
                h = base.localAvatar.getH(self.getZoneNode(self.lastToonZone))
            except TypeError:  # if they're in-between zones while pressing F2
                return
            print(
                'level pos: %s, h: %s, zone %s' % (repr(pos), h, self.lastToonZone)
            )

            posStr = 'X: %.3f' % pos[0] + \
                     '\nY: %.3f' % pos[1] + \
                     '\nZ: %.3f' % pos[2] + \
                     '\nH: %.3f' % h + \
                     '\nZone: %s' % str(self.lastToonZone)

            base.localAvatar.setChatAbsolute(posStr, CFThought | CFTimeout)

        self.accept('f2', printPos)
        base.localAvatar.setCameraCollisionsCanMove(1)

    def levelAnnounceGenerate(self):
        self.notify.debug('levelAnnounceGenerate')
        DistributedLevel.levelAnnounceGenerate(self)

        # create our spec
        # NOTE: in dev, the AI will probably send us another spec to use
        specFilePath = ZoneSpecRegistry[self.zoneId]
        levelSpec = LevelSpec.LevelSpec(specFilePath)
        if EditorGlobals.wantLevelEditor():
            # give the spec a factory EntityTypeRegistry.
            typeReg = self.getEntityTypeReg()
            levelSpec.setEntityTypeReg(typeReg)

        # if the AI is sending us a spec, we won't have it yet and the
        # level isn't really initialized yet. So we can't assume that we
        # can start doing stuff here. Much of what used to be here
        # has been moved to FactoryLevelMgr, where it really belongs, but...
        # this could be cleaner.
        DistributedLevel.initializeLevel(self, levelSpec)

    def placeLocalToon(self, moveLocalAvatar=True):
        # We will want to visit this later for stuff such as teleporting to friends
        # who may currently be in a persistent level.
        # For doors and tunnels, they are both handled by PersistentLevelPlace.py
        return

    ##############
    # Title Text #
    ##############

    def getBranchText(self):
        streetName = StreetNames.get(self.zoneId)

        return streetName[-1]

    def getHoodText(self):
        hoodId = ZoneUtil.getCanonicalHoodId(self.zoneId)
        hoodText = base.cr.hoodMgr.getFullnameFromId(hoodId)

        return hoodText

    def getTitleTextDescription(self, zoneNum):
        ent = self.entities.get(zoneNum)
        if ent and hasattr(ent, 'description'):
            return ent.description
        return None

    def spawnTitleText(self, initialLoad=False):
        if initialLoad:
            placeName = self.getHoodText()
            description = self.getBranchText()
        else:
            placeName = self.getBranchText()
            description = self.getTitleTextDescription(self.lastCamZone)
        displayText = placeName + '\n' + description
        if description and description != '':
            taskMgr.remove(self.uniqueName('titleText'))
            if self.titleSeq is not None:
                self.titleSeq.finish()
                self.titleSeq = None
            self.titleText.setText(displayText)
            self.titleText.setColor(Vec4(*self.titleColor))
            self.titleColor = TitleColorRegistry.get(self.levelMgrEntity.titleColor, (1, 1, 1, 1))
            self.titleText.setFg(self.titleColor)

            # Only show the big title once per session.
            # If we've already seen it, just show the small title

            titleSeq = None
            if self.lastCamZone not in self.zonesEnteredList:
                self.zonesEnteredList.append(self.lastCamZone)
                titleSeq = Sequence(
                                    # HACK! Let a pause go by to cover the loading pause
                                    # This tricks the taskMgr
                                    Wait(0.1),
                                    Func(self.titleText.show),
                                    self.titleText.colorScaleInterval(0.5, Vec4(1.0, 1.0, 1.0, 1.0)),
                                    Wait(6.0),
                                    self.titleText.colorScaleInterval(0.5, Vec4(1.0, 1.0, 1.0, 0.0)),
                                    Func(self.titleText.hide)
                                    )
            if titleSeq:
                self.titleSeq = titleSeq
            else:
                self.titleSeq = Sequence()
            self.titleSeq.start()

    def d_requestQuestEntityInteract(self, entity):
        self.notify.debug(f'Requesting quest entity interact, ID {entity.entId}.')
        if self.getEntityType(entity.entId) != 'questInteractible':
            return

        self.sendUpdate('requestQuestEntityInteract', [entity.entId])
