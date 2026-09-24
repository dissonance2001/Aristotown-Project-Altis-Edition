from direct.distributed import ClockDelta
from direct.interval.IntervalGlobal import *
from panda3d.core import *
from toontown.toon.ClashDistributedToonBase import ClashDistributedToonBase
from toontown.chat.enums.ChatChannel import ChatChannel
from toontown.chat.enums.ChatContentType import ChatContentType
from toontown.chat.enums.ChatNpcPreset import ChatNpcPreset
from toontown.nametag import NametagGlobals
from toontown.toonbase import ToontownGlobals
from direct.gui.DirectGui import *
from toontown.toon.npc import NPCToons


class DistributedNPCToonBase(ClashDistributedToonBase):
    def __init__(self, cr):
        try:
            self.DistributedNPCToon_initialized
            return
        except:
            self.DistributedNPCToon_initialized = 1

        super().__init__(cr)
        self.previousCameraPosHpr = []
        self.__initCollisions()
        # Not pickable
        self.setPickable(0)
        # These guys are specifically non-player characters.
        self.setPlayerType(NametagGlobals.CCNonPlayer)
        self.canSpawn = True
        self.isNPC = True
        self.overheadIcon = None
        self.overheadIconInterval = None

    def disable(self):
        """
        Called when the DistributedObject is removed from active duty and stored in a cache.
        """
        self.ignoreAll()
        # Ignore the sphere after the finish because
        # the end of the movie adds it in
        self.ignore('enter' + self.cSphereNode.getName())
        self.ignore('nameTagShowName')
        self.ignore('nameTagShowAvId')
        self.ignore(self.nametag.getUniqueId())
        self.ignore('teleportBegin')
        self.removeOverheadIcon()
        # Kill any quest choice guis that may be active
        # Kill any movies that may be playing
        super().disable()

    def delete(self):
        try:
            self.DistributedNPCToon_deleted
            return
        except:
            self.DistributedNPCToon_deleted = 1

        self.__deleteCollisions()
        super().delete()

    def generate(self):
        """
        Called when the DistributedObject is reintroduced to the world, either for the first time or from the cache.
        """
        super().generate()
        # We cannot get a unique name until we have been generated
        self.cSphereNode.setName(self.uniqueName('NPCToon'))
        self.detectAvatars()
        # Since we know where the NPC will be standing, we can
        # immediately parent him to render.  This initializes the
        # nametag, etc.
        self.setParent(ToontownGlobals.SPRender)
        self.startLookAround()


    def generateToon(self):
        """
        Create a toon from dna (an array of strings)
        NOTE: DistributedNPCToon overrides this because they do not
        need all this extra junk
        """
        self.setLODs()
        # load the toon legs
        self.generateToonLegs()
        # load the toon head
        self.generateToonHead()
        # load the toon torso
        self.generateToonTorso()
        # color the toon as specified by the dna
        self.generateToonColor()
        self.parentToonParts()
        # Make small toons with big heads
        self.rescaleToon()
        self.resetHeight()

        # Initialize arrays of pointers to useful nodes for the toon
        self.rightHands = []
        self.leftHands = []
        self.headParts = []
        self.hipsParts = []
        self.torsoParts = []
        self.legsParts = []
        self.__bookActors = []
        self.__holeActors = []

        self.setShaderAuto()

    def announceGenerate(self):
        # This method is called after all the required fields have
        # been filled in.  In particular, the DNA will have been set,
        # so we can safely set an animation state.

        # This may be overidden by derived classes
        self.initToonState()
        super().announceGenerate()
        # if we cannot spawn, hide ourselves from the world!
        if not self.getCanSpawn():
            self.hideNPCToon()

    def initToonState(self):
        # We'll make all NPC toons loop their neutral cycle by
        # default.  Normally this is sent from the AI, but because the
        # server sometimes loses updates that immediately follow the
        # generate, we might lose that message.
        self.setAnimState('neutral', 0.9, None, None)

        # TODO: make this a node path collection
        npcOrigin = render.find('**/npc_origin_' + str(self.posIndex))

        # Now he's no longer parented to render, but no one minds.
        if not npcOrigin.isEmpty():
            self.reparentTo(npcOrigin)
            self.initPos()

    def initPos(self):
        self.clearMat()

    def wantsSmoothing(self):
        # This overrides a function from DistributedSmoothNode to
        # indicate that NPC's should not ever be smoothed, even though
        # they do inherit (indirectly) from DistributedSmoothNode.
        return 0

    def detectAvatars(self):
        """
        listen for the collision sphere enter event
        """
        self.accept('enter' + self.cSphereNode.getName(), self.prompt)

    def prompt(self, collEntry):
        if settings['interactkey']:
            self.accept('exit' + self.cSphereNode.getName(), self.handleCollisionSphereExit)
            self.accept('teleportBegin', self.handleCollisionSphereExit)
            self.accept(base.INTERACT, self.activate, [collEntry])
            if hasattr(self, "name"):
                text = ("Press " + str(base.INTERACT).upper() + " to interact with %s" %self.getName())
            else:
                text = "Press " + str(base.INTERACT).upper() + " to interact"

            self.enterText = OnscreenText(
                text = text,
                style = 3,
                scale = .09,
                parent = base.a2dBottomCenter,
                fg = (1, 0.9, 0.1, 1),
                pos = (0.0, 0.5)
            )
            self.enterText.setColorScale(1, 1, 1, 0)
            self.colorSeq = Sequence(
                LerpColorScaleInterval(self.enterText, .8, VBase4(1, 1, 1, 1)),
                LerpColorScaleInterval(self.enterText, .8, VBase4(.5, .6, 1, .9)), name='NPCTextprompt').loop()
        else:
            self.activate(collEntry)

    def activate(self, collEntry):
        if settings['interactkey']:
            self.handleCollisionSphereExit()
        self.handleCollisionSphereEnter(collEntry)

    def handleCollisionSphereExit(self, collEntry=None):
        self.ignore('exit' + self.cSphereNode.getName())
        self.ignore('teleportBegin')
        self.ignore(base.INTERACT)
        if hasattr(self, "colorSeq"):
            if self.colorSeq:
                self.colorSeq.finish()
                self.colorSeq = None
        if hasattr(self, "enterText"):
            self.enterText.removeNode()
            del self.enterText

    def ignoreAvatars(self):
        """
        Do not listen for the enter coll sphere event.
        """
        self.ignore('enter' + self.cSphereNode.getName())

    def getCollSphereRadius(self):
        return 3.25

    def __initCollisions(self):
        self.cSphere = CollisionTube(0.0, 1.0, 0.0, 0.0, 1.0, 5.0, self.getCollSphereRadius())
        self.cSphere.setTangible(0)
        self.cSphereNode = CollisionNode('cSphereNode')
        self.cSphereNode.addSolid(self.cSphere)
        self.cSphereNodePath = self.attachNewNode(self.cSphereNode)
        self.cSphereNodePath.hide()
        self.cSphereNode.setCollideMask(ToontownGlobals.WallBitmask)

    def __deleteCollisions(self):
        self.ignore('teleportBegin')
        self.ignore(base.INTERACT)
        if hasattr(self, "colorSeq"):
            if self.colorSeq:
                self.colorSeq.finish()
                self.colorSeq = None
        if hasattr(self, "enterText"):
            self.enterText.removeNode()
            del self.enterText
        del self.cSphere
        del self.cSphereNode
        self.cSphereNodePath.removeNode()
        del self.cSphereNodePath

    def handleCollisionSphereEnter(self, collEntry):
        """
        Response for a toon walking up to this NPC
        """
        pass

    def setupAvatars(self, av):
        """
        Prepare avatars for the quest movie
        """
        av.headsUp(self, 0, 0, 0)
        self.headsUp(av, 0, 0, 0)
        av.stopLookAround()
        av.lerpLookAt(Point3(-0.5, 4, 0), time=0.5)
        self.stopLookAround()
        self.lerpLookAt(Point3(av.getPos(self)), time=0.5)

    def b_setPageNumber(self, paragraph, pageNumber):
        self.setPageNumber(paragraph, pageNumber)
        self.d_setPageNumber(paragraph, pageNumber)

    def d_setPageNumber(self, paragraph, pageNumber):
        timestamp = ClockDelta.globalClockDelta.getFrameNetworkTime()
        self.sendUpdate('setPageNumber', [paragraph, pageNumber, timestamp])

    def freeAvatar(self):
        """
        This is a message from the AI used to free the avatar from movie mode
        """
        base.cr.playGame.getPlace().setState('Walk')

    def setPositionIndex(self, posIndex):
        """
        This required field sets the NPC's position index.
        Each zone has N NPCs, and N corresponding NPC origins in the model.
        """
        self.posIndex = posIndex

    def setHealthDisplay(self, mode):
        """
        Override from DisToon, don't ever show laff meters for NPCs
        """
        pass

    def removeOverheadIcon(self):
        if self.overheadIconInterval:
            self.overheadIconInterval.finish()
            del self.overheadIconInterval

        if self.overheadIcon:
            self.overheadIcon.detachNode()
            del self.overheadIcon

    def setOverheadIcon(self, iconName: str):
        defaultIcon = (None, None)
        iconInfo = {
            'fist': ('phase_3.5/models/gui/tt_m_gui_gm_toonResistance_fist', '**/*fistIcon*')
        }

        icon = loader.loadModel(iconInfo.get(iconName, defaultIcon)[0])
        self.overheadIcon = icon.find(iconInfo.get(iconName, defaultIcon)[1])
        np = NodePath(self.nametag.getNameIcon())
        if np.isEmpty():
            return
        self.overheadIcon.flattenStrong()
        self.overheadIcon.reparentTo(np)
        self.overheadIcon.setScale(4)
        self.overheadIcon.setZ(-2.4)
        self.overheadIconInterval = LerpHprInterval(self.overheadIcon, 3.0, Point3(0, 0, 0), Point3(-360, 0, 0))
        self.overheadIconInterval.loop()

    def hideNPCToon(self):
        #self.setPos(100, 100, 100)
        #self.hide()    # this is good, *however*...
        self.hideNametag2d()
        self.hideNametag3d()
        self.stash()    # this is better :) (no collision checks with this one *and* hides them too!)

    def setCanSpawn(self, canSpawn):
        self.canSpawn = canSpawn

    def getCanSpawn(self):
        return self.canSpawn
