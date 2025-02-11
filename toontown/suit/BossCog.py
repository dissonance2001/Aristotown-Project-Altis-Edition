import string
import types
from direct.actor import Actor
from direct.directnotify import DirectNotifyGlobal
from direct.fsm import FSM
from direct.fsm import State
from toontown.chat.ChatGlobals import *
from direct.interval.IntervalGlobal import *
from toontown.toonbase.ToonPythonUtil import Functor
from direct.task.Task import Task
from pandac.PandaModules import *
from toontown.suit import Suit
import random
from toontown.suit import SuitDNA
from otp.avatar import Avatar
from toontown.battle import BattleParticles
from toontown.battle import BattleProps
from toontown.nametag import NametagGlobals
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals

GenericModel = 'phase_9/models/char/bossCog'
ModelDict = {'s': 'phase_9/models/char/sellbotBoss',
 'm': 'phase_10/models/char/cashbotBoss',
 'l': 'phase_11/models/char/lawbotBoss',
 'c': 'phase_12/models/char/bossbotBoss',
 'g': 'phase_14/models/char/boardbotBoss'}
AnimList = ('Ff_speech', 'ltTurn2Wave', 'wave', 'Ff_lookRt', 'Ff_neutral_f', 'turn2Fb', 'Ff_neutral', 'Bb_neutral', 'Ff2Bb_spin', 'Bb2Ff_spin', 'Fb_neutral', 'Bf_neutral', 'Fb_firstHit', 'Fb_downNeutral', 'Fb_downHit', 'Fb_fall', 'Fb_down2Up', 'Fb_downLtSwing', 'Fb_downRtSwing', 'Fb_DownThrow', 'Fb_UpThrow', 'Fb_jump', 'golf_swing')


class BossCog(Avatar.Avatar):
    notify = DirectNotifyGlobal.directNotify.newCategory('BossCog')
    healthColors = Suit.Suit.healthColors
    healthGlowColors = Suit.Suit.healthGlowColors
    ANIM_PLAYRATE = 1

    def __init__(self):
        Avatar.Avatar.__init__(self)
        self.setFont(ToontownGlobals.getSuitFont())
        self.setPlayerType(NametagGlobals.CCSuit)
        self.setPickable(0)
        self.doorA = None
        self.doorB = None
        self.bubbleB = None
        self.bubbleL = None
        self.bubbleR = None
        self.bubbleF = None
        self.bubbleFL = None
        self.bubbleFR = None
        self.headParts = []
        self.animatedHeadParts = []
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
        self.warningSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_GOON_tractor_beam_alarmed.ogg')
        self.warningSfx2 = loader.loadSfx('phase_9/audio/sfx/CHQ_GOON_tractor_beam_alarmed.ogg')

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

    def setDNAString(self, dnaString):
        self.dna = SuitDNA.SuitDNA()
        self.dna.makeFromNetString(dnaString)
        self.setDNA(self.dna)

    def setDNA(self, dna):
        if self.style:
            pass
        else:
            self.style = dna
            self.generateBossCog()
            self.initializeDropShadow()
            self.setBlend(frameBlend=base.wantSmoothAnims)
            if base.wantNametags:
                self.initializeNametag3d()

    def generateBossCog(self):
        self.throwSfx = base.loadSfx('phase_9/audio/sfx/CHQ_VP_frisbee_gears.ogg')
        self.swingSfx = base.loadSfx ('phase_9/audio/sfx/CHQ_VP_swipe.ogg')
        self.spinSfx = base.loadSfx('phase_9/audio/sfx/CHQ_VP_spin.ogg')
        self.rainGearsSfx = base.loadSfx('phase_9/audio/sfx/CHQ_VP_raining_gears.ogg')
        self.swishSfx = base.loadSfx('phase_9/audio/sfx/CHQ_VP_swish.ogg')
        self.boomSfx = base.loadSfx('phase_9/audio/sfx/CHQ_VP_boom.ogg')
        self.deathSfx = base.loadSfx('phase_9/audio/sfx/CHQ_VP_big_death.ogg')
        self.treadsSfx = base.loadSfx('phase_9/audio/sfx/CHQ_VP_tractor_treads.ogg')
        self.headshakeSfx = base.loadSfx('phase_9/audio/sfx/CHQ_VP_headshake.ogg')
        self.upSfx = base.loadSfx('phase_9/audio/sfx/CHQ_VP_raise_up.ogg')
        self.downSfx = base.loadSfx('phase_9/audio/sfx/CHQ_VP_collapse.ogg')
        self.reelSfx = base.loadSfx('phase_9/audio/sfx/CHQ_VP_reeling_backwards.ogg')
        self.birdsSfx = base.loadSfx('phase_4/audio/sfx/SZ_TC_bird1.ogg')
        self.dizzyAlert = base.loadSfx('phase_5/audio/sfx/AA_sound_aoogah.ogg')
        if self.style.dept == 'c':
            self.grunt = base.loadSfx('phase_9/audio/sfx/Boss_c_COG_VO_grunt.ogg')
            self.murmur = base.loadSfx('phase_9/audio/sfx/Boss_c_COG_VO_murmur.ogg')
            self.statement = base.loadSfx('phase_9/audio/sfx/Boss_c_COG_VO_statement.ogg')
            self.question = base.loadSfx('phase_9/audio/sfx/Boss_c_COG_VO_question.ogg')
        elif self.style.dept == 'l':
            self.grunt = base.loadSfx('phase_9/audio/sfx/Boss_l_COG_VO_grunt.ogg')
            self.murmur = base.loadSfx('phase_9/audio/sfx/Boss_l_COG_VO_murmur.ogg')
            self.statement = base.loadSfx('phase_9/audio/sfx/Boss_l_COG_VO_statement.ogg')
            self.question = base.loadSfx('phase_9/audio/sfx/Boss_l_COG_VO_question.ogg')
        else:
            self.grunt = base.loadSfx('phase_9/audio/sfx/Boss_COG_VO_grunt.ogg')
            self.murmur = base.loadSfx('phase_9/audio/sfx/Boss_COG_VO_murmur.ogg')
            self.statement = base.loadSfx('phase_9/audio/sfx/Boss_COG_VO_statement.ogg')
            self.question = base.loadSfx('phase_9/audio/sfx/Boss_COG_VO_question.ogg')
        self.dialogArray = [self.grunt,
         self.murmur,
         self.statement,
         self.question,
         self.grunt,
         self.grunt]
        dna = self.style
        filePrefix = ModelDict[dna.dept]
        self.loadModel(GenericModel + '-legs-zero', 'legs')
        if self.style.dept == 'l':
            self.loadModel(filePrefix + '-torso-zero', 'torso')
        else:
            self.loadModel(GenericModel + '-torso-zero', 'torso')
        self.loadModel(filePrefix + '-head-zero', 'head')
        self.twoFaced = dna.dept == 's'
        self.attach('head', 'torso', 'joint34')
        self.attach('torso', 'legs', 'joint_pelvis')
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
        self.corner1Attack = self.rotateNode.attachNewNode('frontAttack')
        self.corner1Attack.setPos(-10, -8, 10)
        self.corner1Attack.setScale(2)
        self.corner2Attack = self.rotateNode.attachNewNode('frontAttack')
        self.corner2Attack.setPos(10, -8, 10)
        self.corner2Attack.setScale(2)
        self.corner3Attack = self.rotateNode.attachNewNode('frontAttack')
        self.corner3Attack.setPos(-10, 8, 10)
        self.corner3Attack.setScale(2)
        self.corner4Attack = self.rotateNode.attachNewNode('frontAttack')
        self.corner4Attack.setPos(10, 8, 10)
        self.corner4Attack.setScale(2)
        if self.style.dept == 'c':
            self.setHeight(30)
        else:
            self.setHeight(25)
        self.nametag3d.setScale(2.5)
        for partName in ('legs', 'torso'):
            animDict = {}
            for anim in AnimList:
                animDict[anim] = '%s-%s-%s' % (GenericModel, partName, anim)

            self.loadAnims(animDict, partName)

        self.stars = BattleProps.globalPropPool.getProp('stun')
        self.stars.setPosHprScale(0, 0, 10, 0, 0, 0, 3, 3, 3)
        self.stars.loop('stun')
        texture = loader.loadTexture('phase_9/maps/cc_t_ene_boss_m.png')
        texture2 = loader.loadTexture('phase_9/maps/cc_t_ene_boss_c.png')
        self.pelvis = self.getPart('torso')
        if self.style.dept == 'm':
            pelvis = self.pelvis.find('**/Object')
            pelvis.setTexture(texture, 1)
        elif self.style.dept == 'c':
            pelvis = self.pelvis.find('**/Object')
            pelvis.setTexture(texture2, 1)
        self.pelvisForwardHpr = VBase3(0, 0, 0)
        self.pelvisReversedHpr = VBase3(-180, 0, 0)
        if self.style.dept == 's':
            self.neck = self.getPart('head')
            self.neck.setTwoSided(True)
            self.neck.hide()
            self.neckForwardHpr = VBase3(0, 0, 0)
            self.neckReversedHpr = VBase3(0, -540, 0)
        elif self.style.dept == 'l':
            self.neck = self.getPart('head')
            self.neck.setTwoSided(True)
            self.neck.hide()
            self.neckForwardHpr = VBase3(0, 0, 0)
            self.neckReversedHpr = VBase3(0, -540, 0)
        elif self.style.dept == 'g':
            self.neck = self.getPart('head')
            self.neck.setTwoSided(True)
            self.neckForwardHpr = VBase3(0, 0, 0)
            self.neckReversedHpr = VBase3(0, -540, 0)
        elif self.style.dept == 'm':
            self.neck = self.getPart('head')
            self.neck.setTwoSided(True)
            self.neck.hide()
            self.neckForwardHpr = VBase3(0, 0, 0)
            self.neckReversedHpr = VBase3(0, -540, 0)
        elif self.style.dept == 'c':
            self.neck = self.getPart('head')
            self.neck.setTwoSided(True)
            self.neck.hide()
            self.neckForwardHpr = VBase3(0, 0, 0)
            self.neckReversedHpr = VBase3(0, -540, 0)
        self.axle = self.find('**/joint_axle')
        self.doorA = self.__setupDoor('**/joint_doorFront', 'doorA', self.doorACallback, VBase3(0, 0, 0), VBase3(0, 0, -80), CollisionPolygon(Point3(5, -4, 0.32), Point3(0, -4, 0), Point3(0, 4, 0), Point3(5, 4, 0.32)))
        self.doorB = self.__setupDoor('**/joint_doorRear', 'doorB', self.doorBCallback, VBase3(0, 0, 0), VBase3(0, 0, 80), CollisionPolygon(Point3(-5, 4, 0.84), Point3(0, 4, 0), Point3(0, -4, 0), Point3(-5, -4, 0.84)))
        treadsModel = loader.loadModel('%s-treads' % GenericModel)
        treadsModel.reparentTo(self.axle)
        self.treadsLeft = treadsModel.find('**/right_tread')
        self.treadsRight = treadsModel.find('**/left_tread')
        self.doorA.request('Closed')
        self.doorB.request('Closed')
        self.setBlend(frameBlend=base.wantSmoothAnims)
        if self.style.dept == 'c':
            self.generateHead3('ceo-a', animated=True)
        elif self.style.dept == 'm':
            self.generateHead3('cfo', animated=True)
        elif self.style.dept == 's':
            self.generateHead3('vp', animated=True)
        elif self.style.dept == 'l':
            self.generateHead3('clo', animated=True)
        self.generateHealthBarBase()
        self.generateCorporateMedallion()

    def initializeBodyCollisions(self, collIdStr):
        Avatar.Avatar.initializeBodyCollisions(self, collIdStr)
        if not self.ghostMode:
            self.collNode.setCollideMask(self.collNode.getIntoCollideMask() | ToontownGlobals.PieBitmask)

    def generateCorporateMedallion(self):
        icons = loader.loadModel('phase_3.5/models/char/ttcc_ene_insignias')
        icons2 = loader.loadModel('phase_3.5/models/gui/cog_icons')
        dept = self.style.dept
        if base.config.GetBool('want-new-cogs', 0):
            chestNull = self.find('**/def_joint_lifeMeter')
            if chestNull.isEmpty():
                chestNull = self.find('**/joint_lifeMeter')
        else:
            chestNull = self.find('**/joint_lifeMeter')
        if dept == 'c':
            self.corpMedallion = icons.find('**/emblem_corp').copyTo(chestNull)
        elif dept == 's':
            self.corpMedallion = icons.find('**/emblem_sales').copyTo(chestNull)
        elif dept == 'l':
            self.corpMedallion = icons.find('**/emblem_legal').copyTo(chestNull)
        elif dept == 'm':
            self.corpMedallion = icons.find('**/emblem_money').copyTo(chestNull)
        elif dept == 'g':
            self.corpMedallion = icons.find('**/emblem_board').copyTo(chestNull)
        elif dept == 't':
            self.corpMedallion = icons2.find('**/TechIcon').copyTo(chestNull)
        self.corpMedallion.setScale(3)
        self.corpMedallion.setP(-20)
        if self.style.dept == 'l':
            self.corpMedallion.setY(1.1)
        else:
            self.corpMedallion.setY(.25)

    def generateHealthBarBase(self):
        self.removeHealthBar()
        chestNull = self.find('**/joint_lifeMeter')
        if chestNull.isEmpty():
            return
        model = loader.loadModel('phase_3.5/models/char/ttcc_ene_insignias')
        button = model.find('**/emblem_hp')
        base = model.find('**/emblem_base')
        base.setScale(3.0)
        base.setP(-20)
        base.reparentTo(chestNull)
        self.healthBar = button
        if self.style.dept == 'l':
            base.setY(1.1)
        else:
            base.setY(.25)

    def generateHealthBar(self):
        self.removeHealthBar()
        chestNull = self.find('**/joint_lifeMeter')
        if chestNull.isEmpty():
            return
        model = loader.loadModel('phase_3.5/models/char/ttcc_ene_insignias')
        button = model.find('**/emblem_hp')
        button.setScale(3.0)
        button.setP(-20)
        button.setColor(self.healthColors[0])
        button.reparentTo(chestNull)
        self.healthBar = button
        glow = button.find('**/glow')
        glow.reparentTo(self.healthBar)
        glow.setScale(1)
        glow.setPos(0, 0, 0)
        glow.setColor(self.healthGlowColors[0])
        if self.style.dept == 'l':
            button.setY(1.1)
        else:
            button.setY(.25)
        self.healthBarGlow = glow
        self.healthCondition = 0

    def updateHealthBar(self):
        if self.healthBar == None:
            return
        health = 1.0 - float(self.bossDamage) / float(self.bossMaxDamage)
        if health > 1.5:
            condition = 13
            self.ANIM_PLAYRATE = 1
        elif health > 1.0:
            condition = 12
            self.ANIM_PLAYRATE = 1
        elif health > 0.95:
            condition = 0
            self.ANIM_PLAYRATE = 1.05
        elif health > 0.9:
            condition = 1
            self.ANIM_PLAYRATE = 1.1
        elif health > 0.8:
            condition = 2
            self.ANIM_PLAYRATE = 1.15
        elif health > 0.7:
            condition = 3
            self.ANIM_PLAYRATE = 1.2
        elif health > 0.6:
            condition = 4
            self.ANIM_PLAYRATE = 1.25
        elif health > 0.5:
            condition = 5
            self.ANIM_PLAYRATE = 1.3
        elif health > 0.4:
            condition = 6
            self.ANIM_PLAYRATE = 1.35
        elif health > 0.25:
            condition = 7
            self.ANIM_PLAYRATE = 1.4
        elif health > 0.2:
            condition = 8
            self.ANIM_PLAYRATE = 1.45
        elif health > 0.1:
            condition = 9
            self.ANIM_PLAYRATE = 1.5
        elif health > 0.0:
            condition = 10
            self.ANIM_PLAYRATE = 2
        else:
            condition = 11
            self.ANIM_PLAYRATE = 1
        
        if self.healthCondition != condition:
            if condition == 10:
                self.healthBar.setColor(1, 1, 1, 1)
                self.healthBarGlow.setColor(1, 1, 1, 1)
                blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.75), Task(self.__pulseGray), Task.pause(0.1))
                taskMgr.add(blinkTask, self.uniqueName('blink-task'))
            elif condition == 11:
                self.healthBar.setColor(1, 1, 1, 1)
                self.healthBarGlow.setColor(1, 1, 1, 1)
                if self.healthCondition == 10:
                    taskMgr.remove(self.uniqueName('blink-task'))
            else:
                if self.style.dept == 'c':
                    self.healthBar.setColor(1, 1, 1, 1)
                    self.healthBarGlow.setColor(1, 1, 1, 1)
                    taskMgr.remove(self.uniqueName('blink-task'))
                    self.__changeColor()
                    self.eyes.setColor(self.healthColors[condition], 1)
                else:
                    self.healthBar.setColor(1, 1, 1, 1)
                    self.healthBarGlow.setColor(1, 1, 1, 1)
                    taskMgr.remove(self.uniqueName('blink-task'))
                    self.__changeColor()
            self.healthCondition = condition

    def generateHead3(self, headType, headColor=None, headTexture=None, modelOverride=None, pathOverride=None,
                     extraArgs={}, animated=False, additionalAnims=[]):
        if animated:
            if headType == 'skelecog' or headType == 'overwhelmingauthorizer' or headType == 'executioner':
                if headType == 'overwhelmingauthorizer':
                    headModel = Actor.Actor('phase_14/models/char/ttcc_ene_%s%s-zero' % (
                    headType, '_exe' if self.isExecutive or self.isManager else ''))
                elif headType == 'executioner':
                    headModel = Actor.Actor('phase_14/models/char/ttcc_ene_executioner-zero')
                else:
                    headModel = Actor.Actor(
                        'phase_14/models/char/cog' + string.upper(self.style.body) + '_robot_head-zero')
                self.generateHeadAnims(
                    'phase_14/models/char/cog' + string.upper(self.style.body) + '_robot_head-',
                    headModel, additionalAnims)
                self.animatedHeadParts.append(headModel)
                if headType != 'autocaddie' and headType != 'overwhelmingauthorizer':
                    if headTexture:
                        try:
                            texture = loader.loadTexture('phase_5/maps/' + headTexture)
                        except:
                            texture = loader.loadTexture('phase_14/maps/' + headTexture)
                    else:
                        if self.style.dept == None:
                            texture = loader.loadTexture('phase_14/maps/ttcc_ene_skelecog_unemployed.png')
                        else:
                            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s%s.png' % (
                            self.style.dept, '_exe' if self.isExecutive or self.isManager else '',))
                    for headPart in self.animatedHeadParts:
                        headPart.setTexture(texture, 1)
            else:
                headModel = Actor.Actor('phase_14/models/char/ttcc_ene_' + headType + '-zero')
                self.generateHeadAnims('phase_14/models/char/ttcc_ene_' + headType + '-', headModel, additionalAnims)
                self.animatedHeadParts.append(headModel)
            headModel.reparentTo(self.find('**/joint34'))
            headModel.setBlend(frameBlend=base.wantSmoothAnims)
            headModel.loop('neutral')
            if headType == 'cfo':
                headModel.setTwoSided(True)
            if headType == 'ceo-a':
                ceoeyes = headModel.find('**/ceo_eyes')
                self.eyes = ceoeyes
            if 'x' in extraArgs:
                if extraArgs['x'] != None:
                    headModel.setX(extraArgs['x'])
            if 'y' in extraArgs:
                if extraArgs['y'] != None:
                    headModel.setY(extraArgs['y'])
            if 'z' in extraArgs:
                if extraArgs['z'] != None:
                    headModel.setZ(extraArgs['z'])
            if 'h' in extraArgs:
                if extraArgs['h'] != None:
                    headModel.setH(extraArgs['h'])
            if 'p' in extraArgs:
                if extraArgs['p'] != None:
                    headModel.setP(extraArgs['p'])
            if 'r' in extraArgs:
                if extraArgs['r'] != None:
                    headModel.setR(extraArgs['r'])
            if 'scale' in extraArgs:
                if extraArgs['scale'] != None:
                    headModel.setScale(*extraArgs['scale'])
            self.headParts.append(headModel)
        else:
            if headType == 'skelecog':
                if base.config.GetBool('want-clash-assets', False):
                    headModel = loader.loadModel(
                        'phase_14/models/char/cog' + string.upper(self.style.body) + '_robot_head-zero')
                    headReferences = headModel.findAllMatches('**/skeleskull_' + string.upper(self.style.body))
                else:
                    headModel = loader.loadModel(
                        'phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-head')
                    headReferences = headModel.findAllMatches('**/suit' + string.upper(self.style.body))
            else:
                if pathOverride:
                    headModel = loader.loadModel(pathOverride + headType)
                else:
                    if modelOverride:
                        headModel = loader.loadModel(modelOverride)
                        headReferences = headModel.findAllMatches('**/' + headType)
                    else:
                        try:
                            headModel = loader.loadModel('phase_' + str(phase) + '/models/char/' + headType)
                            headReferences = headModel.findAllMatches('**/' + headType + '.egg')
                        except:
                            headModel = loader.loadModel('phase_' + str(phase) + filePrefix + 'heads')
                            headReferences = headModel.findAllMatches('**/' + headType)
            if pathOverride:
                if headTexture:
                    pass
                if headColor:
                    headModel.setColor(headColor)
                if 'x' in extraArgs:
                    if extraArgs['x'] != None:
                        headModel.setX(extraArgs['x'])
                if 'y' in extraArgs:
                    if extraArgs['y'] != None:
                        headModel.setY(extraArgs['y'])
                if 'z' in extraArgs:
                    if extraArgs['z'] != None:
                        headModel.setZ(extraArgs['z'])
                if 'h' in extraArgs:
                    if extraArgs['h'] != None:
                        headModel.setH(extraArgs['h'])
                if 'p' in extraArgs:
                    if extraArgs['p'] != None:
                        headModel.setP(extraArgs['p'])
                if 'r' in extraArgs:
                    if extraArgs['r'] != None:
                        headModel.setR(extraArgs['r'])
                if 'scale' in extraArgs:
                    if extraArgs['scale'] != None:
                        headModel.setScale(*extraArgs['scale'])
                self.headParts.append(headModel)
            else:
                for i in range(0, headReferences.getNumPaths()):
                    if self.style.body == 'a' or self.style.body == 'b':
                        headPart = self.instance(headReferences.getPath(i), 'modelRoot', 'to_head')
                    else:
                        headPart = self.instance(headReferences.getPath(i), 'modelRoot', 'joint34')
                    if headTexture:
                        try:
                            headTex = loader.loadTexture('phase_' + str(phase) + '/maps/' + headTexture)
                        except:
                            try:  # Will work on a more viable replacement for specific phases later.
                                headTex = loader.loadTexture('phase_5/maps/' + headTexture)
                            except:
                                try:
                                    headTex = loader.loadTexture('phase_11/maps/' + headTexture)
                                except:
                                    headTex = loader.loadTexture('phase_14/maps/' + headTexture)
                        headPart.setTexture(headTex, 1)
                    if headColor:
                        headPart.setColor(headColor)
                    if 'x' in extraArgs:
                        if extraArgs['x'] != None:
                            headPart.setX(extraArgs['x'])
                    if 'y' in extraArgs:
                        if extraArgs['y'] != None:
                            headPart.setY(extraArgs['y'])
                    if 'z' in extraArgs:
                        if extraArgs['z'] != None:
                            headPart.setZ(extraArgs['z'])
                    if 'h' in extraArgs:
                        if extraArgs['h'] != None:
                            headPart.setH(extraArgs['h'])
                    if 'p' in extraArgs:
                        if extraArgs['p'] != None:
                            headPart.setP(extraArgs['p'])
                    if 'r' in extraArgs:
                        if extraArgs['r'] != None:
                            headPart.setR(extraArgs['r'])
                    if 'scale' in extraArgs:
                        if extraArgs['scale'] != None:
                            headPart.setScale(*extraArgs['scale'])
                    if headType == 'suitA' or headType == 'suitB' or headType == 'suitC':
                        headPart.setZ(headPart.getZ() + {
                            'suitA': -6.05,
                            'suitB': -5.09477996826172,
                            'suitC': -4.15
                        }[headType])
                        if self.isExecutive or self.isManager:
                            if self.style.name == 'mbr':
                                headPart.setColor(VBase4(0.825, 0.6, 0.425, 1.0))
                            else:
                                if headColor == None:
                                    headPart.setColor({
                                                          'c': SuitDNA.corpPolyColor,
                                                          'l': SuitDNA.legalPolyColor,
                                                          'm': SuitDNA.moneyPolyColor,
                                                          's': SuitDNA.salesPolyColor,
                                                          'g': SuitDNA.boardPolyColor,
                                                          None: VBase4(0.5, 0.5, 0.5, 1.0)
                                                      }[SuitDNA.getSuitDept(self.style.name)])
                        else:
                            if self.style.name == 'mbr':
                                headPart.setColor(VBase4(1.0, 0.25, 0.0, 1.0))
                    self.headParts.append(headPart)
                headModel.removeNode()

    def __blinkRed(self, task):
        if self.healthBar:
            self.healthBar.setColor(self.healthColors[9], 1)
        
        return Task.done

    def __blinkGray(self, task):
        if self.healthBar:
            self.healthBar.setColor(self.healthColors[10], 1)
        
        return Task.done

    def __pulseRed(self, task):
        self.interval = Parallel(LerpColorScaleInterval(self.healthBar, duration=.25, colorScale=(1, 0, 0, 1),
                                   blendType='easeInOut'))
        self.glowInterval = Parallel(LerpColorScaleInterval(self.healthBarGlow, duration=.25, colorScale=(1, 0, 0, 1),
                                   blendType='easeInOut'))
        self.interval.start()
        self.glowInterval.start()

    def __pulseGray(self, task):
        self.interval = Parallel(LerpColorScaleInterval(self.healthBar, duration=.25, colorScale=(0.431, 0.431, 0.431, 1),
                                   blendType='easeInOut'))
        self.glowInterval = Parallel(LerpColorScaleInterval(self.healthBarGlow, duration=.25, colorScale=(0, 0, 0, 0),
                                   blendType='easeInOut'))
        self.interval.start()
        self.glowInterval.start()

    def __changeColor(self):
        self.interval = Parallel(LerpColorScaleInterval(self.healthBar, duration=1, colorScale=(self.healthColors[self.healthCondition]),
                                   blendType='easeInOut'))
        self.glowInterval = Parallel(LerpColorScaleInterval(self.healthBarGlow, duration=1, colorScale=(self.healthColors[self.healthCondition]),
                                   blendType='easeInOut'))
        self.interval.start()
        self.glowInterval.start()

    def removeHealthBar(self):
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

    def __rollTreadsInterval(self, object, start = 0, duration = 0, rate = 1):

        def rollTexMatrix(t, object = object):
            object.setTexOffset(TextureStage.getDefault(), t, 0)

        return LerpFunctionInterval(rollTexMatrix, fromData=start, toData=start + rate * duration, duration=duration)

    def rollLeftTreads(self, duration, rate):
        start = self.treadsLeftPos
        self.treadsLeftPos += duration * rate
        return self.__rollTreadsInterval(self.treadsLeft, start=start, duration=duration, rate=rate)

    def rollRightTreads(self, duration, rate):
        start = self.treadsRightPos
        self.treadsRightPos += duration * rate
        return self.__rollTreadsInterval(self.treadsRight, start=start, duration=duration, rate=rate)

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

    def __setupDoor(self, jointName, name, callback, openedHpr, closedHpr, cPoly):
        joint = self.find(jointName)
        children = joint.getChildren()
        animate = joint.attachNewNode(name)
        children.reparentTo(animate)
        cnode = CollisionNode('BossZap')
        cnode.setCollideMask(ToontownGlobals.PieBitmask | ToontownGlobals.WallBitmask | ToontownGlobals.CameraBitmask)
        cnode.addSolid(cPoly)
        animate.attachNewNode(cnode)
        fsm = self.DoorFSM(name, animate, callback, openedHpr, closedHpr, self.uniqueName)
        return fsm

    def doAnimate(self, anim = None, now = 0, queueNeutral = 1, raised = None, forward = None, happy = None):
        if now:
            self.stopAnimate()
        
        if not self.twoFaced:
            happy = 1
        
        if raised == None:
            raised = self.raised
        
        if forward == None:
            forward = self.forward
        
        if happy == None:
            happy = self.happy
        
        if now:
            self.raised = raised
            self.forward = forward
            self.happy = happy
        
        if self.currentAnimIval == None:
            self.accept(self.animDoneEvent, self.__getNextAnim)
        else:
            queueNeutral = 0
        
        ival, changed = self.__getAnimIval(anim, raised, forward, happy)
        if changed or queueNeutral:
            self.queuedAnimIvals.append((ival,
             self.raised,
             self.forward,
             self.happy))
            if self.currentAnimIval == None:
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
            return (self.getAnim(anim), anim != None)
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
        if startNeckHpr != endNeckHpr:
            ival = Sequence(Func(self.neck.setHpr, startNeckHpr), ParallelEndTogether(ival, Sequence(self.neck.hprInterval(0.5, endNeckHpr, startHpr=startNeckHpr, blendType='easeInOut'), Func(self.neck.setHpr, self.neckForwardHpr))))
        elif endNeckHpr != self.neckForwardHpr:
            ival = Sequence(Func(self.neck.setHpr, startNeckHpr), ival, Func(self.neck.setHpr, self.neckForwardHpr))
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
        if anim != None:
            ival = Sequence(ival, self.getAnim(anim))
        
        return (ival, 1)

    def setDizzy(self, dizzy):
        if dizzy and not self.dizzy:
            base.playSfx(self.dizzyAlert)
        
        self.dizzy = dizzy
        if dizzy:
            self.stars.reparentTo(self.pelvis)
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
        if anim == None:
            partName = None
            if self.happy:
                for headPart in self.animatedHeadParts:
                    headPart.setP(0)
                animName = 'Ff_neutral'
            else:
                for headPart in self.animatedHeadParts:
                    headPart.setP(0)
                animName = 'Fb_neutral'
            if self.raised:
                for headPart in self.animatedHeadParts:
                    headPart.setP(0)
                ival = ActorInterval(self, animName)
            else:
                for headPart in self.animatedHeadParts:
                    headPart.setP(0)
                ival = Parallel(ActorInterval(self, animName, partName=['torso', 'head']), ActorInterval(self, 'Fb_downNeutral', partName='legs'))
            if not self.forward:
                ival = Sequence(Func(self.reverseBody), ival, Func(self.forwardBody))
        elif anim == 'down2Up':
            for headPart in self.animatedHeadParts:
                headPart.setP(180)
                headAnim = Parallel(ActorInterval(headPart, 'stun'), Func(headPart.loop, 'neutral%s' % ('-hurt' if self.healthCondition >= 8 else '',)))
                headAnim.start()
            ival = Parallel(SoundInterval(self.upSfx), self.getAngryActorInterval('Fb_down2Up'))
            self.raised = 1
        elif anim == 'up2Down':
            for headPart in self.animatedHeadParts:
                headPart.setP(180)
                headAnim = Parallel(ActorInterval(headPart, 'stun'), Func(headPart.loop, 'neutral%s' % ('-hurt' if self.healthCondition >= 8 else '',)))
                headAnim.start()
            ival = Parallel(SoundInterval(self.downSfx), self.getAngryActorInterval('Fb_down2Up', playRate=-1))
            self.raised = 0
        elif anim == 'throw':
            for headPart in self.animatedHeadParts:
                headPart.setP(180)
            self.doAnimate(None, raised=1, happy=0, queueNeutral=0)
            ival = Parallel()
            ival.append(Parallel(Sequence(SoundInterval(self.throwSfx), duration=0),
                            self.getAngryActorInterval('Fb_UpThrow')))
        elif anim == 'hit':
            if self.raised and self.dizzy:
                self.raised = 0
                ival = self.getAngryActorInterval('Fb_firstHit')
                for headPart in self.animatedHeadParts:
                    headPart.setP(180)
                    headAnim = Sequence(ActorInterval(headPart, 'stun'), Func(headPart.loop, 'neutral-lured'))
                    headAnim.start()
            if self.raised:
                self.raised = 0
                ival = self.getAngryActorInterval('Fb_firstHit')
                for headPart in self.animatedHeadParts:
                    headPart.setP(180)
                    headAnim = Sequence(ActorInterval(headPart, 'stun'), Func(headPart.loop, 'neutral%s' % ('-hurt' if self.healthCondition >= 8 else '',)))
                    headAnim.start()
            else:
                ival = self.getAngryActorInterval('Fb_downHit')
                for headPart in self.animatedHeadParts:
                    headPart.setP(180)
                    headAnim = Sequence(ActorInterval(headPart, 'neutral-lured'), Func(headPart.loop, 'neutral-lured'))
                    headAnim.start()
            ival = Parallel(SoundInterval(self.reelSfx, node=self), ival)
        elif anim == 'ltSwing' or anim == 'rtSwing':
            for headPart in self.animatedHeadParts:
                headPart.setP(0)
            self.doAnimate(None, raised=0, happy=0, queueNeutral=0)
            if anim == 'ltSwing':
                for headPart in self.animatedHeadParts:
                    headPart.setP(0)
                ival = Sequence(Track((0, self.getAngryActorInterval('Fb_downLtSwing')), (0.9, SoundInterval(self.swingSfx, node=self)), (1, Func(self.bubbleL.unstash))), Func(self.bubbleL.stash))
            else:
                for headPart in self.animatedHeadParts:
                    headPart.setP(0)
                ival = Sequence(Track((0, self.getAngryActorInterval('Fb_downRtSwing')), (0.9, SoundInterval(self.swingSfx, node=self)), (1, Func(self.bubbleR.unstash))), Func(self.bubbleR.stash))
        elif anim == 'frontAttack':
            for headPart in self.animatedHeadParts:
                headPart.setP(0)
            if not self.raised:
                self.doAnimate('down2Up', happy=0, queueNeutral=0)
            else:
                self.doAnimate(None, raised=1, happy=0, queueNeutral=0)
            pe = BattleParticles.loadParticleFile('bossCogFrontAttack.ptf')
            pe2 = BattleParticles.loadParticleFile('bossCogFrontAttack.ptf')
            pe3 = BattleParticles.loadParticleFile('bossCogFrontAttack.ptf')
            pe4 = BattleParticles.loadParticleFile('bossCogFrontAttack.ptf')
            pe5 = BattleParticles.loadParticleFile('bossCogFrontAttack.ptf')
            pe6 = BattleParticles.loadParticleFile('bossCogFrontAttack.ptf')
            pe7 = BattleParticles.loadParticleFile('bossCogFrontAttack.ptf')
            pe8 = BattleParticles.loadParticleFile('bossCogFrontAttack.ptf')
            pe.setH(0)
            pe2.setH(180)
            pe3.setH(90)
            pe4.setH(270)
            pe5.setH(45)
            pe6.setH(-45)
            pe7.setH(135)
            pe8.setH(-135)
            ival = Sequence()
            if self.dna.dept == 'm' :
                ival.append(Func(self.setChatAbsolute, random.choice(("Why worry about problems when you can shake them off?", "Let me put my spin on this.", "I'm showering you with praise!")), CFSpeech | CFTimeout))
            elif self.dna.dept == 's' :
                ival.append(Func(self.setChatAbsolute, random.choice(("You're gonna go nuts and bolts for this offer!",
                                                                      "Why worry about problems when you can shake them off?",
                                                                      "Let me put my spin on this.",
                                                                      "I'm showering you with praise!",
                                                                      "Let's get these ideas going!")),
                                 CFSpeech | CFTimeout))
            ival.append(Sequence(Func(self.reverseHead), Parallel(ActorInterval(self, 'Bb2Ff_spin'), Func(self.forwardHead))))
            if self.forward:
                ival = Sequence(Func(self.reverseBody), ParallelEndTogether(ival, self.pelvis.hprInterval(0.5, self.pelvisForwardHpr, blendType='easeInOut')))
            ival = Sequence(Track((0, ival), (0, Sequence(SoundInterval(self.spinSfx, node=self))), (1.3, Parallel(
                SoundInterval(self.rainGearsSfx, node=self),
                ParticleInterval(pe8, self.corner4Attack, worldRelative=0, duration=1.5, cleanup=True),
                ParticleInterval(pe7, self.corner3Attack, worldRelative=0, duration=1.5, cleanup=True),
                ParticleInterval(pe6, self.corner2Attack, worldRelative=0, duration=1.5, cleanup=True),
                ParticleInterval(pe5, self.corner1Attack, worldRelative=0, duration=1.5, cleanup=True),
                ParticleInterval(pe4, self.leftAttack, worldRelative=0, duration=1.5, cleanup=True),
                ParticleInterval(pe3, self.rightAttack, worldRelative=0, duration=1.5, cleanup=True),
                ParticleInterval(pe2, self.backAttack, worldRelative=0, duration=1.5, cleanup=True),
                ParticleInterval(pe, self.frontAttack, worldRelative=0, duration=1.5, cleanup=True), duration=0)),
                                  (1.9, Func(self.bubbleJ.unstash)), (1.9, Func(self.bubbleI.unstash)),
                                  (1.9, Func(self.bubbleH.unstash)), (1.9, Func(self.bubbleG.unstash)),
                                  (1.9, Func(self.bubbleF.unstash)), (1.9, Func(self.bubbleFL.unstash)),
                                  (1.9, Func(self.bubbleFR.unstash)), (1.9, Func(self.bubbleB.unstash))),
                            Func(self.bubbleJ.stash), Func(self.bubbleI.stash), Func(self.bubbleH.stash),
                            Func(self.bubbleG.stash), Func(self.bubbleF.stash), Func(self.bubbleFL.stash),
                            Func(self.bubbleFR.stash), Func(self.bubbleB.stash))
            self.forward = 1
            self.happy = 1
            self.raised = 1
        elif anim == 'areaAttack':
            for headPart in self.animatedHeadParts:
                headPart.setP(0)
            if self.twoFaced:
                self.doAnimate(None, raised=1, happy=0, queueNeutral=1)
            else:
                self.doAnimate(None, raised=1, happy=0, queueNeutral=1)
            ival = Parallel(ActorInterval(self, 'Fb_jump'),
                            Sequence(SoundInterval(self.swishSfx, duration=1.1),
                                     SoundInterval(self.boomSfx, duration=1.9)),
                            Sequence(Wait(1.21), Func(self.announceAreaAttack), Wait(.1), Func(self.announceAreaAttack),
                                     Wait(.1), Func(self.announceAreaAttack), Wait(.1), Func(self.announceAreaAttack),
                                     Wait(.1), Func(self.announceAreaAttack), Wait(.1)))

            if self.dna.dept == 's' :
                ival.append(Func(self.setChatAbsolute, random.choice(("It's a clearance sale! All Toons must go!", 'Pay attention to my pitch!', "This deal will knock your socks off!", "We're sweeping the floor with this limited time offer!")), CFSpeech | CFTimeout))
            if self.twoFaced:
                self.happy = 0
            else:
                self.happy = 1
            self.raised = 1
        elif anim == 'Fb_fall':
            ival = Parallel(ActorInterval(self, 'Fb_fall'), Sequence(SoundInterval(self.reelSfx), SoundInterval(self.deathSfx)))
        elif isinstance(anim, types.StringType):
            ival = ActorInterval(self, anim)
        else:
            ival = anim
        
        return ival
