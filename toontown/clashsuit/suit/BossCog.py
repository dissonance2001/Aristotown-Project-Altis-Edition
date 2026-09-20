from toontown.clashsuit.suit import BossCogGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from direct.fsm import FSM
from direct.interval.IntervalGlobal import *
from direct.showbase import PythonUtil
from direct.task.Task import Task
from panda3d.core import *
from toontown.nametag import NametagGroup
from toontown.nametag import NametagGlobals
from toontown.chat.enums.ChatChannel import ChatChannel
from toontown.chat.enums.ChatContentType import ChatContentType
from toontown.chat.enums.ChatNpcPreset import ChatNpcPreset
from toontown.clashsuit.suit.heads.AnimatedSuitHead import AnimatedSuitHead
from toontown.clashsuit.suit import BossSuitHealthMeter
from toontown.clashsuit.suit import SuitHealthMeter
from toontown.clashsuit.suit import SuitDNA
from toontown.toonbase import TTLocalizer
from otp.avatar import Avatar
from toontown.clashbattle.battle import BattleParticles
from toontown.clashbattle.battle import BattleProps
from otp import *
from toontown.toonbase import ToontownGlobals

GenericModel = 'phase_9/models/char/bossCog'
ModelDict = {
    's': 'phase_9/models/char/sellbotBoss',
    'm': 'phase_10/models/char/cashbotBoss',
    'l': 'phase_11/models/char/lawbotBoss',
    'c': 'phase_12/models/char/bossbotBoss',
    'g': 'phase_12/models/char/bossbotBoss'
}
AnimList = (
    'Ff_speech', 'ltTurn2Wave', 'wave', 'Ff_lookRt', 'turn2Fb', 'Ff_neutral', 'Bb_neutral', 'Ff2Bb_spin', 'Bb2Ff_spin',
    'Fb_neutral', 'Bf_neutral', 'Fb_firstHit', 'Fb_downNeutral', 'Fb_downHit', 'Fb_fall', 'Fb_down2Up',
    'Fb_downLtSwing', 'Fb_downRtSwing', 'Fb_DownThrow', 'Fb_UpThrow', 'Fb_jump', 'golf_swing', 'Ff_cross_arms',
    'leftlook', 'Ff_cross_arms_into', 'Ff_cross_arms_loop', 'Ff_cross_arms_out', 'Ff_trapfall', 'Ff_trapland')
FemaleVariantAnims = ('Ff_neutral',)



@DirectNotifyCategory()
class BossCog(Avatar.Avatar):
    
    healthColors = SuitHealthMeter.HEALTH_COLORS
    healthGlowColors = SuitHealthMeter.HEALTH_COLORS  # TEMP: Until i port this system over to boss cogs
    oldHealthGlowColors = (
        Vec4(0.25, 1, 0.25, 0.5),
        Vec4(0.5, 1, 0.25, .5),
        Vec4(0.75, 1, 0.25, .5),
        Vec4(1, 1, 0.25, 0.5),
        Vec4(1, 0.866, 0.25, .5),
        Vec4(1, 0.6, 0.25, .5),
        Vec4(1, 0.5, 0.25, 0.5),
        Vec4(1, 0.25, 0.25, 0.5),
        Vec4(1, 0.25, 0.25, 0.5),
        Vec4(0.3, 0.3, 0.3, 0),
        Vec4(.1, .9, .9, .65),
        Vec4(0.6, .1, 1, .75),
        Vec4(1, 1, 1, 0.5)
    )
    medallionColors = {
        # Bossbot
        'c': Vec4(0.863, 0.776, 0.769, 1.0),
        # Sellbot [Sales]
        's': Vec4(0.843, 0.745, 0.745, 1.0),
        # Lawbot [Legal]
        'l': Vec4(0.749, 0.776, 0.824, 1.0),
        # Cashbot [Marketing]
        'm': Vec4(0.749, 0.769, 0.749, 1.0),
        # Boardbot
        'g': Vec4(0.863, 0.776, 0.769, 1.0)
    }
    customVoiceDepts = ('c', 'l')
    specialHeadDepts = ('l',)
    femaleBosses = ('l',)
    ANIM_PLAYRATE = 1
    UseNewHealthMeter = False

    def __init__(self):
        Avatar.Avatar.__init__(self)
        self.setFont(ToontownGlobals.getSuitFont())
        self.setPlayerType(NametagGroup.CCSuit)
        self.setPickable(1)
        self.doorA = None
        self.doorB = None
        self.bubbleB = None
        self.bubbleL = None
        self.bubbleR = None
        self.bubbleF = None
        self.bubbleFL = None
        self.bubbleFR = None
        self.cqueue = None
        self.rays = None
        self.ray1 = None
        self.ray2 = None
        self.ray3 = None
        self.e1 = None
        self.e2 = None
        self.e3 = None
        self.specialHead = None
        self.raised = 1
        self.forward = 1
        self.happy = 1
        self.dizzy = 0
        self.nowRaised = 1
        self.nowForward = 1
        self.nowHappy = 1
        self.currentAnimIval = None
        self.queuedAnimIvals = []
        self.treadsLeftPos = 0
        self.treadsRightPos = 0
        self.healthBar = None
        self.healthCondition = 0
        self.animDoneEvent = 'BossCogAnimDone'
        self.animIvalName = 'BossCogAnimIval'
        self.jumpTime = ClockObject()
        self.jumpFullTime = 0
    
    def cleanup(self):
        self.unstickBoss()
        return super().cleanup()

    def resetJumpFullTime(self):
        self.jumpFullTime = 0

    def delete(self):
        Avatar.Avatar.delete(self)
        self.removeHealthBar()
        self.setDizzy(0)
        self.stopAnimate()
        if self.doorA:
            self.doorA.request('Off')
            self.doorB.request('Off')
            self.doorA = None
            self.doorB = None
        if self.specialHead:
            self.specialHead.cleanup()
            self.specialHead.delete()

    def setDNAString(self, dnaString):
        self.dna = SuitDNA.SuitDNA()
        self.dna.makeFromNetString(dnaString)
        self.setDNA(self.dna)

    def setDNA(self, dna):
        if not self.style:
            self.style = dna
            self.generateBossCog()
            self.initializeDropShadow()
            self.dropShadow.setScale(10)
            if base.wantNametags:
                self.initializeNametag3d()

    def generateBossCog(self):
        self.throwSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_VP_frisbee_gears.ogg')
        self.swingSfx = loader.loadSfx ('phase_9/audio/sfx/CHQ_VP_swipe.ogg')
        self.spinSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_VP_spin.ogg')
        self.rainGearsSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_VP_raining_gears.ogg')
        self.swishSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_VP_swish.ogg')
        self.boomSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_VP_boom.ogg')
        self.deathSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_VP_big_death.ogg')
        self.treadsSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_VP_tractor_treads.ogg')
        self.headshakeSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_VP_headshake.ogg')
        self.upSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_VP_raise_up.ogg')
        self.downSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_VP_collapse.ogg')
        self.reelSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_VP_reeling_backwards.ogg')
        self.birdsSfx = loader.loadSfx('phase_4/audio/sfx/SZ_TC_bird1.ogg')
        self.dizzyAlert = loader.loadSfx('phase_5/audio/sfx/AA_sound_aoogah.ogg')
        dna = self.style
        filePrefix = ModelDict[dna.dept]
        if dna.dept in self.customVoiceDepts:
            self.grunt = loader.loadSfx('phase_9/audio/sfx/Boss_%s_COG_VO_grunt.ogg' % dna.dept)
            self.murmur = loader.loadSfx('phase_9/audio/sfx/Boss_%s_COG_VO_murmur.ogg' % dna.dept)
            self.statement = loader.loadSfx('phase_9/audio/sfx/Boss_%s_COG_VO_statement.ogg' % dna.dept)
            self.question = loader.loadSfx('phase_9/audio/sfx/Boss_%s_COG_VO_question.ogg' % dna.dept)
        else:
            self.grunt = loader.loadSfx('phase_9/audio/sfx/Boss_COG_VO_grunt.ogg')
            self.murmur = loader.loadSfx('phase_9/audio/sfx/Boss_COG_VO_murmur.ogg')
            self.statement = loader.loadSfx('phase_9/audio/sfx/Boss_COG_VO_statement.ogg')
            self.question = loader.loadSfx('phase_9/audio/sfx/Boss_COG_VO_question.ogg')
        self.dialogArray = [self.grunt,
         self.murmur,
         self.statement,
         self.question,
         self.grunt,
         self.murmur,
         self.statement]
        self.loadModel(GenericModel + '-legs-zero', 'legs')
        self.loadModel(filePrefix + '-torso-zero', 'torso')
        if dna.dept not in self.specialHeadDepts:
            self.loadModel(filePrefix + '-head-zero', 'head')
            self.attach('head', 'torso', 'joint34')
        else:
            AnimatedSuitHead(self, filePrefix + '-head-zero', isBoss=True)
        self.attach('torso', 'legs', 'joint_pelvis')
        self.twoFaced = dna.dept == 's'
        self.rotateNode = self.attachNewNode('rotate')
        geomNode = self.getGeomNode()
        geomNode.reparentTo(self.rotateNode)
        self.frontAttack = self.rotateNode.attachNewNode('frontAttack')
        self.frontAttack.setPos(0, -10, 10)
        self.frontAttack.setScale(2)
        self.rightAttack = self.rotateNode.attachNewNode('frontAttack')
        self.rightAttack.setPos(10, 0, 10)
        self.rightAttack.setScale(2)
        self.leftAttack = self.rotateNode.attachNewNode('frontAttack')
        self.leftAttack.setPos(-10, 0, 10)
        self.leftAttack.setScale(2)
        self.backAttack = self.rotateNode.attachNewNode('frontAttack')
        self.backAttack.setPos(0, 10, 10)
        self.backAttack.setScale(2)
        self.setHeight(26)
        self.nametag3d.setScale(2)
        parts = ['legs', 'torso']
        if dna.dept not in self.specialHeadDepts:
            parts.append('head')
        for partName in parts:
            animDict = {}
            if dna.dept in self.femaleBosses:
                for anim in AnimList:
                    if anim in FemaleVariantAnims:
                        animDict[anim] = '%s-%s-%s' % (GenericModel, partName, anim + '_f')
                    else:
                        animDict[anim] = '%s-%s-%s' % (GenericModel, partName, anim)
            else:
                for anim in AnimList:
                    animDict[anim] = '%s-%s-%s' % (GenericModel, partName, anim)

            self.loadAnims(animDict, partName)

        self.stars = BattleProps.globalPropPool.getProp('stun')
        self.stars.setPosHprScale(7, 0, 0, 0, 0, -90, 3, 3, 3)
        self.stars.loop('stun')
        self.pelvis = self.getPart('torso')
        self.pelvisForwardHpr = VBase3(0, 0, 0)
        self.pelvisReversedHpr = VBase3(-180, 0, 0)
        if dna.dept in self.specialHeadDepts:
            self.neck = self.specialHead
        else:
            self.neck = self.getPart('head')
        self.neck.setTwoSided(True)
        self.neckForwardHpr = VBase3(0, 0, 0)
        self.neckReversedHpr = VBase3(0, -540, 0)
        self.setBlend(frameBlend = base.wantSmoothAnims)
        self.axle = self.find('**/joint_axle')
        self.doorA = self.setupDoorA('**/joint_doorFront', 'doorA', self.doorACallback, VBase3(0, 0, 0), VBase3(0, 0, -80))
        self.doorB = self.setupDoorB('**/joint_doorRear', 'doorB', self.doorBCallback, VBase3(0, 0, 0), VBase3(0, 0, 80))
        treadsModel = loader.loadModel('%s-treads' % GenericModel)
        treadsModel.reparentTo(self.axle)
        self.treadsLeft = treadsModel.find('**/right_tread')
        self.treadsRight = treadsModel.find('**/left_tread')
        self.doorA.request('Closed')
        self.doorB.request('Closed')
        self.generateCorporateMedallion()

    def initializeBodyCollisions(self, collIdStr):
        Avatar.Avatar.initializeBodyCollisions(self, collIdStr)
        if not self.ghostMode:
            self.collNode.setCollideMask(self.collNode.getIntoCollideMask() | ToontownGlobals.PieBitmask)

    def getDialogTypeName(self, chatString):
        searchString = chatString.lower()
        stringLength = len(chatString)
        if stringLength <= TTLocalizer.DialogLength1:
            length = 1
        elif stringLength <= TTLocalizer.DialogLength2:
            length = 2
        elif stringLength <= TTLocalizer.DialogLength3:
            length = 3
        else:
            length = 4
        if searchString.find(TTLocalizer.DialogSpecial) >= 0:
            type = 'murmur'
        elif searchString.find(TTLocalizer.DialogExclamation) >= 0:
            type = 'grunt'
        elif searchString.find(TTLocalizer.DialogQuestion) >= 0:
            type = 'question'
        elif searchString.find(TTLocalizer.DialogIndifferent) >= 0:
            type = 'statement'
            return type
        else:
            type = 'statement'
        if type == 'statement':
            if length == 1:
                type = 'grunt'
            elif length == 2:
                type = 'murmur'
            elif length >= 3:
                type = 'statement'
        return type

    def setChatAbsolute(self, chatString, chatFlags, dialogue=None, interrupt=1, wantBalloonAnim=True):
        Avatar.Avatar.setChatAbsolute(self, chatString, chatFlags, dialogue, interrupt, wantBalloonAnim)
        senderId = 0 if not hasattr(self, 'doId') else self.doId
        base.cr.chatManager.receiveChatMessage(ChatChannel.NPC, ChatNpcPreset.Boss, ChatContentType.Text, chatString, senderId, self.getName())

        if self.specialHead:
            type = self.getDialogTypeName(chatString)
            if type in self.specialHead.getAnimNames():
                self.specialHead.play(type)
            else:
                self.specialHead.play('talk')

    def clearChat(self):
        Avatar.Avatar.clearChat(self)
        if self.specialHead:
            self.specialHead.loopNeutral()

    def playDialogue(self, type, length):
        sound = Avatar.Avatar.getDialogueSfx(self, type, length)
        base.playSfx(sound)

    def generateCorporateMedallion(self):
        if self.UseNewHealthMeter:
            if not self.healthBar:
                self.healthBar = BossSuitHealthMeter.BossSuitHealthMeter(self)
                self.healthBar.generate(SuitHealthMeter.MODE_ROAM)
            else:
                self.healthBar.updateMeterMode(SuitHealthMeter.MODE_ROAM)
        else:
            icons = loader.loadModel('phase_3/models/gui/cog_icons')
            dept = self.dna.dept
            chestNull = self.find('**/joint_lifeMeter')
            if chestNull.isEmpty():
                return
            if dept == 'c':
                self.corpMedallion = icons.find('**/CorpIcon').copyTo(chestNull)
            elif dept == 's':
                self.corpMedallion = icons.find('**/SalesIcon').copyTo(chestNull)
            elif dept == 'l':
                self.corpMedallion = icons.find('**/LegalIcon').copyTo(chestNull)
                self.corpMedallion.setY(0.8)
            elif dept == 'm':
                self.corpMedallion = icons.find('**/MoneyIcon').copyTo(chestNull)
            elif dept == 'g':
                self.corpMedallion = icons.find('**/BoardIcon').copyTo(chestNull)

            self.corpMedallion.setP(-20)
            self.corpMedallion.setScale(2.0)
            self.corpMedallion.setColor(self.medallionColors[dept])

            icons.removeNode()

    def generateHealthBar(self):
        if self.UseNewHealthMeter:
            self.healthBar.updateMeterMode(SuitHealthMeter.MODE_BATTLE)
        else:
            self.generateOldHealthBar()

    def generateOldHealthBar(self):
        self.removeHealthBar()
        chestNull = self.find('**/joint_lifeMeter')
        if chestNull.isEmpty():
            return
        self.corpMedallion.hide()
        model = loader.loadModel('phase_3.5/models/gui/matching_game_gui')
        button = model.find('**/minnieCircle')
        button.setScale(6.0)
        button.setP(-20)
        button.setColor(self.healthColors[0])
        button.reparentTo(chestNull)
        self.healthBar = button
        glow = BattleProps.globalPropPool.getProp('glow')
        glow.reparentTo(self.healthBar)
        glow.setScale(0.28)
        glow.setPos(-0.005, 0.01, 0.015)
        glow.setColor(self.oldHealthGlowColors[0])
        if self.dna.dept == 'l':
            self.healthBar.setY(0.8)
        button.flattenLight()
        self.healthBarGlow = glow
        self.healthCondition = 0

    def updateHealthBar(self):
        if self.UseNewHealthMeter:
            if self.healthBar:
                self.healthBar.updateHealthBar()
        else:
            if not self.healthBar:
                return
            health = 1.0 - float(self.bossDamage) / float(self.bossMaxDamage)
            if health > 0.95:
                condition = 0
            elif health > 0.9:
                condition = 1
            elif health > 0.8:
                condition = 2
            elif health > 0.7:
                condition = 3
            elif health > 0.6:
                condition = 4
            elif health > 0.5:
                condition = 5
            elif health > 0.3:
                condition = 6
            elif health > 0.15:
                condition = 7
            elif health > 0.05:
                condition = 8
            elif health > 0.0:
                condition = 9
            else:
                condition = 10

            if self.healthCondition != condition:
                taskMgr.remove(self.uniqueName('blink-task'))
                if condition == 9:
                    blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.75), Task(self.__blinkGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                elif condition == 10:
                    blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.25), Task(self.__blinkGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                else:
                    self.healthBar.setColor(self.healthColors[condition], 1)
                    self.healthBarGlow.setColor(self.oldHealthGlowColors[condition], 1)
                self.healthCondition = condition

    def __blinkRed(self, task):
        if self.healthBar:
            self.healthBar.setColor(self.healthColors[8], 1)
            self.healthBarGlow.setColor(self.oldHealthGlowColors[8], 1)
            if self.healthCondition == 10:
                self.healthBar.setScale(1.17)

        return Task.done

    def __blinkGray(self, task):
        if self.healthBar:
            self.healthBar.setColor(self.healthColors[9], 1)
            self.healthBarGlow.setColor(self.oldHealthGlowColors[9], 1)
            if self.healthCondition == 10:
                self.healthBar.setScale(1.0)

        return Task.done

    def getHealthPercentage(self):
        try:
            health = (float(self.bossMaxDamage) - float(self.bossDamage)) / float(self.bossMaxDamage)
        except ZeroDivisionError:
            health = 0.96
        return health

    def removeHealthBar(self):
        if self.UseNewHealthMeter:
            if self.healthBar:
                self.healthBar.delete()
                self.healthBar = None
        else:
            if self.healthBar:
                self.healthBar.removeNode()
                self.healthBar = None

            if self.healthCondition == 9 or self.healthCondition == 10:
                taskMgr.remove(self.uniqueName('blink-task'))

            self.healthCondition = 0

    def reverseHead(self):
        self.neck.setHpr(self.neckReversedHpr)

    def forwardHead(self):
        self.neck.setHpr(self.neckForwardHpr)

    def reverseBody(self):
        self.pelvis.setHpr(self.pelvisReversedHpr)

    def forwardBody(self):
        self.pelvis.setHpr(self.pelvisForwardHpr)

    def getShadowJoint(self):
        return self.getGeomNode()

    def getNametagJoints(self):
        return []

    def getDialogueArray(self):
        return self.dialogArray

    def doorACallback(self, isOpen):
        pass

    def doorBCallback(self, isOpen):
        pass

    def __rollTreadsInterval(self, obj, start = 0, duration = 0, rate = 1):

        def rollTexMatrix(t, obj = obj):
            obj.setTexOffset(TextureStage.getDefault(), t, 0)

        return LerpFunctionInterval(rollTexMatrix, fromData=start, toData=start + rate * duration, duration=duration)

    def rollLeftTreads(self, duration, rate):
        start = self.treadsLeftPos
        self.treadsLeftPos += duration * rate
        return self.__rollTreadsInterval(self.treadsLeft, start=start, duration=duration, rate=rate)

    def rollRightTreads(self, duration, rate):
        start = self.treadsRightPos
        self.treadsRightPos += duration * rate
        return self.__rollTreadsInterval(self.treadsRight, start=start, duration=duration, rate=rate)
    
    def stickBossToFloor(self):
        self.unstickBoss()
        self.ray1 = CollisionRay(0.0, 10.0, 20.0, 0.0, 0.0, -1.0)
        self.ray2 = CollisionRay(0.0, 0.0, 20.0, 0.0, 0.0, -1.0)
        self.ray3 = CollisionRay(0.0, -10.0, 20.0, 0.0, 0.0, -1.0)
        rayNode = CollisionNode('stickBossToFloor')
        rayNode.addSolid(self.ray1)
        rayNode.addSolid(self.ray2)
        rayNode.addSolid(self.ray3)
        rayNode.setFromCollideMask(ToontownGlobals.FloorBitmask)
        rayNode.setIntoCollideMask(BitMask32.allOff())
        self.rays = self.attachNewNode(rayNode)
        self.cqueue = CollisionHandlerQueue()
        base.cTrav.addCollider(self.rays, self.cqueue)

    def unstickBoss(self):
        if self.rays:
            base.cTrav.removeCollider(self.rays)
            self.rays.removeNode()
        self.rays = None
        self.ray1 = None
        self.ray2 = None
        self.ray3 = None
        self.e1 = None
        self.e2 = None
        self.e3 = None
        self.rotateNode.clearTransform()
        self.cqueue = None

    def rollBoss(self, t, fromPos, deltaPos):
        self.setPos(fromPos + deltaPos * t)
        if not self.cqueue:
            return
        self.cqueue.sortEntries()
        numEntries = self.cqueue.getNumEntries()
        if numEntries != 0:
            for i in range(self.cqueue.getNumEntries() - 1, -1, -1):
                entry = self.cqueue.getEntry(i)
                solid = entry.getFrom()
                if solid == self.ray1:
                    self.e1 = entry
                elif solid == self.ray2:
                    self.e2 = entry
                elif solid == self.ray3:
                    self.e3 = entry
                else:
                    self.notify.warning('Unexpected ray in __liftBoss')
                    return

            self.cqueue.clearEntries()
        if not (self.e1 and self.e2 and self.e3):
            self.notify.debug('Some points missed in __liftBoss')
            return
        p1 = self.e1.getSurfacePoint(self)
        p2 = self.e2.getSurfacePoint(self)
        p3 = self.e3.getSurfacePoint(self)
        p2a = (p1 + p3) / 2
        if p2a[2] > p2[2]:
            center = p2a
        else:
            center = p2
        self.setZ(self, center[2])
        if p1[2] > p2[2] + 0.01 or p3[2] > p2[2] + 0.01:
            mat = Mat4(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            if abs(p3[2] - center[2]) < abs(p1[2] - center[2]):
                lookAt(mat, Vec3(p1 - center), CSDefault)
            else:
                lookAt(mat, Vec3(center - p3), CSDefault)
            self.rotateNode.setMat(mat)
        else:
            self.rotateNode.clearTransform()

    def rollBossToPoint(self, fromPos, fromHpr, toPos, toHpr, reverse):
        vector = Vec3(toPos - fromPos)
        distance = vector.length()
        if toHpr is None:
            mat = Mat3(0, 0, 0, 0, 0, 0, 0, 0, 0)
            headsUp(mat, vector, CSDefault)
            scale = VBase3(0, 0, 0)
            shear = VBase3(0, 0, 0)
            toHpr = VBase3(0, 0, 0)
            decomposeMatrix(mat, scale, shear, toHpr, CSDefault)
        if fromHpr:
            newH = PythonUtil.fitDestAngle2Src(fromHpr[0], toHpr[0])
            toHpr = VBase3(newH, 0, 0)
        else:
            fromHpr = toHpr
        turnTime = abs(toHpr[0] - fromHpr[0]) / BossCogGlobals.BossCogTurnSpeed
        if toHpr[0] < fromHpr[0]:
            leftRate = BossCogGlobals.BossCogTreadSpeed
        else:
            leftRate = -BossCogGlobals.BossCogTreadSpeed
        if reverse:
            rollTreadRate = -BossCogGlobals.BossCogTreadSpeed
        else:
            rollTreadRate = BossCogGlobals.BossCogTreadSpeed
        rollTime = distance / BossCogGlobals.BossCogRollSpeed
        deltaPos = toPos - fromPos
        track = Sequence(Func(self.setPos, fromPos), Func(self.headsUp, toPos), Parallel(self.hprInterval(turnTime, toHpr, fromHpr), self.rollLeftTreads(turnTime, leftRate), self.rollRightTreads(turnTime, -leftRate)), Parallel(LerpFunctionInterval(self.rollBoss, duration=rollTime, extraArgs=[fromPos, deltaPos]), self.rollLeftTreads(rollTime, rollTreadRate), self.rollRightTreads(rollTime, rollTreadRate)))
        return (track, toHpr)

    class DoorFSM(FSM.FSM):

        def __init__(self, name, animate, callback, openedHpr, closedHpr, uniqueName):
            FSM.FSM.__init__(self, name)
            self.animate = animate
            self.callback = callback
            self.openedHpr = openedHpr
            self.closedHpr = closedHpr
            self.uniqueName = uniqueName
            self.ival = 0
            self.openSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_VP_door_open.ogg')
            self.closeSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_VP_door_close.ogg')
            self.request('Closed')

        def filterOpening(self, request, args):
            if request == 'close':
                return 'Closing'

            return self.defaultFilter(request, args)

        def enterOpening(self):
            intervalName = self.uniqueName('open-%s' % self.animate.getName())
            self.callback(0)
            ival = Parallel(SoundInterval(self.openSfx, node=self.animate, volume=0.2), self.animate.hprInterval(1, self.openedHpr, blendType='easeInOut'), Sequence(Wait(0.2), Func(self.callback, 1)), name=intervalName)
            ival.start()
            self.ival = ival

        def exitOpening(self):
            self.ival.pause()
            self.ival = None

        def filterOpened(self, request, args):
            if request == 'close':
                return 'Closing'

            return self.defaultFilter(request, args)

        def enterOpened(self):
            self.animate.setHpr(self.openedHpr)
            self.callback(1)

        def filterClosing(self, request, args):
            if request == 'open':
                return 'Opening'

            return self.defaultFilter(request, args)

        def enterClosing(self):
            intervalName = self.uniqueName('close-%s' % self.animate.getName())
            self.callback(1)
            ival = Parallel(SoundInterval(self.closeSfx, node=self.animate, volume=0.2), self.animate.hprInterval(1, self.closedHpr, blendType='easeInOut'), Sequence(Wait(0.8), Func(self.callback, 0)), name=intervalName)
            ival.start()
            self.ival = ival

        def exitClosing(self):
            self.ival.pause()
            self.ival = None

        def filterClosed(self, request, args):
            if request == 'open':
                return 'Opening'

            return self.defaultFilter(request, args)

        def enterClosed(self):
            self.animate.setHpr(self.closedHpr)
            self.callback(0)

    def setupDoorA(self, jointName, name, callback, openedHpr, closedHpr):
        cSolid = CollisionPolygon(Point3(5, -4, 0.32), Point3(0, -4, 0), Point3(0, 4, 0), Point3(5, 4, 0.32))
        return self.setupDoor(jointName, name, callback, openedHpr, closedHpr, cSolid)

    def setupDoorB(self, jointName, name, callback, openedHpr, closedHpr):
        cSolid = CollisionPolygon(Point3(-5, 4, 0.84), Point3(0, 4, 0), Point3(0, -4, 0), Point3(-5, -4, 0.84))
        return self.setupDoor(jointName, name, callback, openedHpr, closedHpr, cSolid)

    def setupDoor(self, jointName, name, callback, openedHpr, closedHpr, cSolid):
        joint = self.find(jointName)
        children = joint.getChildren()
        animate = joint.attachNewNode(name)
        children.reparentTo(animate)
        cNode = CollisionNode('BossZap')
        cNode.setCollideMask(ToontownGlobals.PieBitmask | ToontownGlobals.WallBitmask | ToontownGlobals.CameraBitmask)
        cNode.addSolid(cSolid)
        animate.attachNewNode(cNode)
        fsm = self.DoorFSM(name, animate, callback, openedHpr, closedHpr, self.uniqueName)
        return fsm

    def uniqueName(self, idString):
        return f'{idString}-{id(self)}'

    def doAnimate(self, anim = None, now = 0, queueNeutral = 1, raised = None, forward = None, happy = None):
        if now:
            self.stopAnimate()

        if not self.twoFaced:
            happy = 1

        if raised is None:
            raised = self.raised

        if forward is None:
            forward = self.forward

        if happy is None:
            happy = self.happy

        if now:
            self.raised = raised
            self.forward = forward
            self.happy = happy

        if self.currentAnimIval is None:
            self.accept(self.animDoneEvent, self.__getNextAnim)
        else:
            queueNeutral = 0

        ival, changed = self.__getAnimIval(anim, raised, forward, happy)
        if changed or queueNeutral:
            self.queuedAnimIvals.append((ival,
             self.raised,
             self.forward,
             self.happy))
            if self.currentAnimIval is None:
                self.__getNextAnim()

    def stopAnimate(self):
        self.ignore(self.animDoneEvent)
        self.queuedAnimIvals = []
        if self.currentAnimIval:
            self.currentAnimIval.setDoneEvent('')
            self.currentAnimIval.finish()
            self.currentAnimIval = None

        self.raised = self.nowRaised
        self.forward = self.nowForward
        self.happy = self.nowHappy

    def __getNextAnim(self):
        if self.queuedAnimIvals:
            ival, raised, forward, happy = self.queuedAnimIvals[0]
            del self.queuedAnimIvals[0]
        else:
            ival, changed = self.__getAnimIval(None, self.raised, self.forward, self.happy)
            raised = self.raised
            forward = self.forward
            happy = self.happy
        if self.currentAnimIval:
            self.currentAnimIval.setDoneEvent('')
            self.currentAnimIval.finish()

        self.currentAnimIval = ival
        self.currentAnimIval.start(playRate=self.ANIM_PLAYRATE)
        self.nowRaised = raised
        self.nowForward = forward
        self.nowHappy = happy

    def __getAnimIval(self, anim, raised, forward, happy):
        ival, changed = self.__doGetAnimIval(anim, raised, forward, happy)
        seq = Sequence(ival, name=self.animIvalName)
        seq.setDoneEvent(self.animDoneEvent)
        return (seq, changed)

    def __doGetAnimIval(self, anim, raised, forward, happy):
        if raised == self.raised and forward == self.forward and happy == self.happy:
            return (self.getAnim(anim), anim is not None)
        startsHappy = self.happy
        endsHappy = self.happy
        ival = Sequence()
        if raised and not self.raised:
            upIval = self.getAngryActorInterval('Fb_down2Up')
            if self.forward:
                ival = upIval
            else:
                ival = Sequence(Func(self.reverseBody), upIval, Func(self.forwardBody))
            ival = Parallel(SoundInterval(self.upSfx, node=self), ival)
        if forward != self.forward:
            if forward:
                animName = 'Bb2Ff_spin'
            else:
                animName = 'Ff2Bb_spin'
            ival = Sequence(ival, ActorInterval(self, animName))
            startsHappy = 1
            endsHappy = 1

        startNeckHpr = self.neckForwardHpr
        endNeckHpr = self.neckForwardHpr
        if self.happy != startsHappy:
            startNeckHpr = self.neckReversedHpr
        if happy != endsHappy:
            endNeckHpr = self.neckReversedHpr
        if self.twoFaced:
            if startNeckHpr != endNeckHpr:
                ival = Sequence(Func(self.neck.setHpr, startNeckHpr), ParallelEndTogether(ival, Sequence(self.neck.hprInterval(0.5, endNeckHpr, startHpr=startNeckHpr, blendType='easeInOut'), Func(self.neck.setHpr, self.neckForwardHpr))))
            elif endNeckHpr != self.neckForwardHpr:
                ival = Sequence(Func(self.neck.setHpr, startNeckHpr), ival, Func(self.neck.setHpr, self.neckForwardHpr))
        else:
            ival = Sequence(Func(self.forwardHead), ival, Func(self.forwardHead))
        if not raised and self.raised:
            downIval = self.getAngryActorInterval('Fb_down2Up', playRate=-1)
            if forward:
                ival = Sequence(ival, downIval)
            else:
                ival = Sequence(ival, Func(self.reverseBody), downIval, Func(self.forwardBody))
            ival = Parallel(SoundInterval(self.downSfx, node=self), ival)

        self.raised = raised
        self.forward = forward
        self.happy = happy
        if anim is not None:
            ival = Sequence(ival, self.getAnim(anim))

        return (ival, 1)

    def setDizzy(self, dizzy):
        if dizzy and not self.dizzy:
            base.playSfx(self.dizzyAlert)

        self.dizzy = dizzy
        if dizzy:
            self.stars.reparentTo(self.neck)
            base.playSfx(self.birdsSfx, looping=1)
        else:
            self.stars.detachNode()
            self.birdsSfx.stop()

    def getAngryActorInterval(self, animName, **kw):
        if self.happy:
            ival = Sequence(Func(self.reverseHead), ActorInterval(self, animName, **kw), Func(self.forwardHead))
        else:
            ival = ActorInterval(self, animName, **kw)

        return ival

    def getAnim(self, anim):
        ival = None
        if anim is None:
            partName = None
            if not self.twoFaced or self.happy:
                animName = 'Ff_neutral'
            else:
                animName = 'Fb_neutral'
            if self.raised:
                ival = ActorInterval(self, animName)
            else:
                if self.style.dept in self.specialHeadDepts:
                    ival = Parallel(ActorInterval(self, animName, partName=['torso']), ActorInterval(self, 'Fb_downNeutral', partName='legs'))
                else:
                    ival = Parallel(ActorInterval(self, animName, partName=['torso', 'head']), ActorInterval(self, 'Fb_downNeutral', partName='legs'))
            if not self.forward:
                ival = Sequence(Func(self.reverseBody), ival, Func(self.forwardBody))
        elif anim == 'down2Up':
            ival = Parallel(SoundInterval(self.upSfx, node=self), self.getAngryActorInterval('Fb_down2Up'))
            self.raised = 1
        elif anim == 'up2Down':
            ival = Parallel(SoundInterval(self.downSfx, node=self), self.getAngryActorInterval('Fb_down2Up', playRate=-1))
            self.raised = 0
        elif anim == 'throw':
            self.doAnimate(None, raised=1, happy=0, queueNeutral=0)
            if self.style.dept == 'l':
                throwSfx = loader.loadSfx('phase_11/audio/sfx/LB_boss_paper_throw.ogg')
            else:
                throwSfx = self.throwSfx
            ival = Parallel(Sequence(SoundInterval(throwSfx, node=self), duration=0), self.getAngryActorInterval('Fb_UpThrow'))
        elif anim == 'hit':
            if self.raised:
                self.raised = 0
                ival = self.getAngryActorInterval('Fb_firstHit')
            else:
                ival = self.getAngryActorInterval('Fb_downHit')
            ival = Parallel(SoundInterval(self.reelSfx, node=self), ival)
        elif anim == 'ltSwing' or anim == 'rtSwing':
            self.doAnimate(None, raised=0, happy=0, queueNeutral=0)
            if anim == 'ltSwing':
                ival = Sequence(Track((0, self.getAngryActorInterval('Fb_downLtSwing')), (0.9, SoundInterval(self.swingSfx, node=self)), (1, Func(self.bubbleL.unstash))), Func(self.bubbleL.stash))
            else:
                ival = Sequence(Track((0, self.getAngryActorInterval('Fb_downRtSwing')), (0.9, SoundInterval(self.swingSfx, node=self)), (1, Func(self.bubbleR.unstash))), Func(self.bubbleR.stash))
        elif anim == 'frontAttack' or anim == 'frontAttackPaper':
            self.doAnimate(None, raised=1, happy=0, queueNeutral=0)
            if anim == 'frontAttack':
                pe = BattleParticles.loadParticleFile('bossCogFrontAttack.ptf')
                pe2 = BattleParticles.loadParticleFile('bossCogFrontAttack.ptf')
                pe3 = BattleParticles.loadParticleFile('bossCogFrontAttack.ptf')
                pe4 = BattleParticles.loadParticleFile('bossCogFrontAttack.ptf')
                spinSound = self.rainGearsSfx
            else:
                pe =  BattleParticles.createParticleEffect(file='bossCogPaperFrontAttack')
                pe2 = BattleParticles.createParticleEffect(file='bossCogPaperFrontAttack')
                pe3 = BattleParticles.createParticleEffect(file='bossCogPaperFrontAttack')
                pe4 = BattleParticles.createParticleEffect(file='bossCogPaperFrontAttack')
                spinSound = base.loader.loadSfx('phase_11/audio/sfx/LB_boss_paper_spin.ogg')
            pe2.setH(180)
            pe3.setH(90)
            pe4.setH(270)
            if self.twoFaced:
                ival = Sequence(Func(self.reverseHead), ActorInterval(self, 'Bb2Ff_spin'), Func(self.forwardHead))
            else:
                ival = Sequence(ActorInterval(self, 'Bb2Ff_spin'))
            if self.forward:
                ival = Sequence(Func(self.reverseBody), ParallelEndTogether(ival, self.pelvis.hprInterval(0.5, self.pelvisForwardHpr, blendType='easeInOut')))
            ival = Sequence(
                Track(
                    (0, ival),
                    (0, Sequence(SoundInterval(self.spinSfx, node=self))),
                    (1.3, Parallel(SoundInterval(spinSound, node=self),
                                   ParticleInterval(pe4, self.leftAttack, worldRelative=0, duration=1.5, cleanup=True),
                                   ParticleInterval(pe3, self.rightAttack, worldRelative=0, duration=1.5, cleanup=True),
                                   ParticleInterval(pe2, self.backAttack, worldRelative=0, duration=1.5, cleanup=True),
                                   ParticleInterval(pe, self.frontAttack, worldRelative=0, duration=1.5, cleanup=True), duration=0)),
                    (1.9, Func(self.bubbleF.unstash)),
                    (1.9, Func(self.bubbleFL.unstash)),
                    (1.9, Func(self.bubbleFR.unstash)),
                    (1.9, Func(self.bubbleB.unstash))),
                Func(self.bubbleF.stash),
                Func(self.bubbleFL.stash),
                Func(self.bubbleFR.stash),
                Func(self.bubbleB.stash),
            )
            self.forward = 1
            self.happy = 0
            self.raised = 1
        elif anim == 'areaAttack':
            if self.style.dept == 'l':
                self.doAnimate(None, raised=1, happy=1, queueNeutral=0)
            elif self.twoFaced:
                self.doAnimate(None, raised=1, happy=0, queueNeutral=0)
            else:
                self.doAnimate(None, raised=1, happy=1, queueNeutral=1)
            self.jumpTime.tick()
            ival = Sequence()
            if not self.twoFaced:
                ival.append(Func(self.reverseHead))
            ival.append(Parallel(
                Func(base.localAvatar.doBossJumpIndicator),
                ActorInterval(self, 'Fb_jump'),
                Sequence(
                    SoundInterval(self.swishSfx, duration=1.1, node=base.localAvatar),
                    SoundInterval(self.boomSfx, duration=1.9)
                ),
                Sequence(
                    Wait(1.21),
                    Func(self.announceAreaAttack),
                    Wait(.1),
                    Func(self.announceAreaAttack),
                    Wait(.1),
                    Func(self.announceAreaAttack),
                    Func(self.resetJumpFullTime),
                )
            ))
            if not self.twoFaced:
                ival.append(Func(self.forwardHead))
            if self.style.dept == 'l':
                ival = Sequence(Func(self.loop, 'Ff_neutral'), Wait(1), ival)
            if self.twoFaced:
                self.happy = 0
            else:
                self.happy = 1
            self.raised = 1
        elif anim == 'Fb_fall':
            ival = Parallel(ActorInterval(self, 'Fb_fall'), Sequence(SoundInterval(self.reelSfx, node=self), Wait(1.0), SoundInterval(self.deathSfx)))
        elif isinstance(anim, str):
            ival = ActorInterval(self, anim)
        else:
            ival = anim

        return ival
