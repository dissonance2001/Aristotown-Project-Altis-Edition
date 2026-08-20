from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from panda3d.core import *

from otp.nametag.NametagConstants import CFSpeech, CFTimeout
from toontown.battle import MovieUtil
from toontown.battle.BattleProps import *
from toontown.duckhuntbossbattle import FourBossBattleGlobals
from toontown.duckhuntbossbattle.DistributedRebornBossCog import DistributedRebornBossCog
from toontown.toonbase import ToontownGlobals


class DistributedCFOBoss(DistributedRebornBossCog):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedCFOBoss')

    def __init__(self, cr):
        self.notify.debug('----- __init___')
        DistributedRebornBossCog.__init__(self, cr)
        self.bossIndex = 1
        self.bossDamage = 0
        self.bossMaxDamage = 24
        self.currentWoodIndex = 0
        self.woodPile = []
        self.toonsWithWood = []
        self.placedWood = []
        self.droppedWood = []
        self.woodPileCollision = None
        self.arrow = None
        self.arrowHover = None
        self.localWoodIndex = None
        self.woodDropLabel = None
        self.localToonDroppedWood = False
        self.placeSfx = loader.loadSfx('phase_4/audio/sfx/MG_sfx_travel_game_bell_for_trolley.ogg')
        self.pickupSfx = loader.loadSfx('phase_3.5/audio/sfx/GUI_stickerbook_open.ogg')
        self.tornadoSeqs = []
        self.tornadoAttack = None
        self.deathAnimation = None
        self.largeAttackSeq = None
        self.deleteWoodSeqs = []
        self.trolleyIval = None

    def announceGenerate(self):
        DistributedRebornBossCog.announceGenerate(self)
        target = CollisionTube(0, -1, 4, 0, -1, 9, 3.5)
        targetNode = CollisionNode('CFOTarget')
        targetNode.addSolid(target)
        targetNode.setCollideMask(ToontownGlobals.PieBitmask)
        self.targetNodePath = self.pelvis.attachNewNode(targetNode)
        self.accept('droppedWood', self.__droppedWood)

    def disable(self):
        DistributedRebornBossCog.disable(self)
        render.clearTag('pieCode')
        self.targetNodePath.detachNode()
        for tornadoSeq in self.tornadoSeqs:
            if tornadoSeq:
                tornadoSeq.finish()
        self.tornadoSeqs = []
        for deleteWoodSeq in self.deleteWoodSeqs:
            if deleteWoodSeq:
                deleteWoodSeq.finish()
        self.deleteWoodSeqs = []
        if self.tornadoAttack:
            self.tornadoAttack.finish()
        self.tornadoAttack = None
        if self.arrowHover:
            self.arrowHover.finish()
            self.arrowHover = None
        if self.arrow:
            self.arrow.removeNode()
            self.arrow = None
        if self.woodDropLabel:
            self.woodDropLabel.destroy()
            self.woodDropLabel = None
        for wood in self.woodPile:
            if wood:
                wood.removeNode()
        self.woodPile = []
        for placedWood in self.placedWood:
            if placedWood:
                placedWood.removeNode()
        self.placedWood = []
        if self.woodPileCollision:
            self.woodPileCollision.removeNode()
        self.woodPileCollision = None
        if self.deathAnimation:
            self.deathAnimation.finish()
        self.deathAnimation = None
        if self.largeAttackSeq:
            self.largeAttackSeq.finish()
        self.largeAttackSeq = None
        if self.trolleyIval:
            self.trolleyIval.finish()
        self.trolleyIval = None
        self.ignoreAll()
        self.removeAllTasks()

    def beginBattleTwo(self):
        # Set up the CFO health bar...
        self.generateHealthBar()
        self.updateHealthBar()
        self.healthBar.hide()

        # Create the wood pile...
        for i in xrange(len(FourBossBattleGlobals.WoodPilePosHprs)):
            wood = loader.loadModel('phase_14/models/props/table-wood')
            wood.setPosHpr(*FourBossBattleGlobals.WoodPilePosHprs[i])
            wood.reparentTo(render)
            self.woodPile.append(wood)

        # Setup the wood pile collision...
        pileNode = CollisionNode('PileCollisions')
        pileBox = CollisionBox(Point3(0, -99, 0), 10, 2, 2)
        pileNode.addSolid(pileBox)
        self.woodPileCollision = self.bossBattle.geom.attachNewNode(pileNode)
        self.accept('enterPileCollisions', self.__enteredPileCollision)

        # Pre-generate the track...
        for x in range(len(FourBossBattleGlobals.WoodTrackYs)):
            placedWood = loader.loadModel('phase_14/models/props/table-wood')
            placedWood.setPosHprScale(46.5, FourBossBattleGlobals.WoodTrackYs[x], 0.0, 0.0, 0.0, 0.0, 3.0, 3.0, 3.0)
            placedWood.reparentTo(hidden)
            woodColl = CollisionNode('WoolColl' + str(x))
            woodBox = CollisionBox(0, 1, 0.75, 0.5)
            woodBox.setTangible(0)
            woodColl.addSolid(woodBox)
            woodNode = render.attachNewNode(woodColl)
            woodNode.setPosHprScale(46.5, FourBossBattleGlobals.WoodTrackYs[x], 0.0, 0.0, 0.0, 0.0, 3.0, 3.0, 3.0)
            self.placedWood.append(placedWood)

    def __enteredPileCollision(self, _):
        if base.localAvatar.isStunned or self.localToonDroppedWood:
            return
        self.sendUpdate('requestGrabWood', [self.currentWoodIndex])

    def grabWood(self, avId, index):
        if not avId:
            return

        if avId in self.toonsWithWood:
            return

        av = self.cr.doId2do.get(avId)
        if not av:
            return

        self.toonsWithWood.append(avId)

        if av == base.localAvatar:
            base.localAvatar.controlManager.disableAvatarJump()
            base.localAvatar.currentSpeed = ToontownGlobals.ToonForwardSpeed / 4
            base.localAvatar.currentReverseSpeed = ToontownGlobals.ToonReverseSpeed / 4
            base.localAvatar.controlManager.setSpeeds(ToontownGlobals.ToonForwardSpeed / 4,
                                                      ToontownGlobals.ToonJumpForce / 4,
                                                      ToontownGlobals.ToonReverseSpeed / 4,
                                                      ToontownGlobals.ToonRotateSpeed / 4)
            base.playSfx(self.pickupSfx)
            self.arrow = loader.loadModel('phase_14/models/props/woodtrack_arrow')
            self.arrow.find('**/dropshadow').removeNode()
            self.arrow.reparentTo(self.placedWood[index])
            self.arrow.wrtReparentTo(render)
            self.arrowHover = Sequence(self.arrow.posInterval(1, (self.arrow.getX(), self.arrow.getY(), -1)),
                                       self.arrow.posInterval(1, (self.arrow.getX(), self.arrow.getY(), 0)))
            self.arrowHover.loop()
            self.accept('enterWoolColl' + str(index), self.__enteredSpotCollision, extraArgs=[index])
            self.accept('escape', self.__droppedWood)
            self.localWoodIndex = index
            self.woodDropLabel = DirectLabel(text=FourBossBattleGlobals.WoodAdvice, text_fg=VBase4(1, 1, 1, 1),
                                             text_align=TextNode.ACenter, relief=None, pos=(0, 0, 0.69), scale=0.1)

        av.animFSM.request('SlowCatching')

        if index >= len(self.woodPile):
            return

        if index not in self.droppedWood:
            self.currentWoodIndex += 1

        woodPiece = self.woodPile[index]

        if index in self.droppedWood:
            self.ignore('enterDroppedWoolColl' + str(index))

        woodPiece.reparentTo(av.find('**/rightHand'))
        woodPiece.setPosHpr(0, -1, 0.35, 90, 0, 5)

    def __enteredSpotCollision(self, index, _):
        self.sendUpdate('requestPlaceWood', [index])

    def placeWood(self, avId, index):
        if not avId:
            return

        if avId not in self.toonsWithWood:
            return

        av = self.cr.doId2do.get(avId)
        if not av:
            return

        self.toonsWithWood.remove(avId)

        if av == base.localAvatar:
            base.localAvatar.controlManager.enableAvatarJump()
            base.localAvatar.currentSpeed = ToontownGlobals.ToonForwardSpeed
            base.localAvatar.currentReverseSpeed = ToontownGlobals.ToonReverseSpeed
            base.localAvatar.controlManager.setSpeeds(ToontownGlobals.ToonForwardSpeed,
                                                      ToontownGlobals.ToonJumpForce,
                                                      ToontownGlobals.ToonReverseSpeed,
                                                      ToontownGlobals.ToonRotateSpeed)
            base.playSfx(self.placeSfx)
            if self.arrowHover:
                self.arrowHover.finish()
                self.arrowHover = None
            if self.arrow:
                self.arrow.removeNode()
                self.arrow = None
            self.ignore('enterWoolColl' + str(index))
            self.ignore('escape')
            self.localWoodIndex = None
            if self.woodDropLabel:
                self.woodDropLabel.destroy()
                self.woodDropLabel = None

        av.animFSM.request('Happy')
        av.startSmooth()

        if index >= len(self.woodPile):
            return

        if index in self.droppedWood:
            self.droppedWood.remove(index)

        self.bossDamage += 1
        self.updateHealthBar()
        woodPiece = self.woodPile[index]
        woodPiece.removeNode()
        self.placedWood[index].reparentTo(render)

    def __droppedWood(self):
        if self.localWoodIndex is not None:
            self.sendUpdate('requestDropWood', [self.localWoodIndex])

    def dropWood(self, avId, index):
        if not avId:
            return

        if avId not in self.toonsWithWood:
            return

        av = self.cr.doId2do.get(avId)
        if not av:
            self.droppedWood.append(index)
            woodPiece = self.woodPile[index]
            woodPiece.wrtReparentTo(render)
            woodPiece.setZ(0.1)
            woodColl = CollisionNode('DroppedWoolColl' + str(index))
            woodBox = CollisionBox(0, 4, 0.75, 0.5)
            woodBox.setTangible(0)
            woodColl.addSolid(woodBox)
            woodPiece.attachNewNode(woodColl)
            self.accept('enterDroppedWoolColl' + str(index), self.__enteredDroppedWoodCollision, extraArgs=[index])
            return

        self.toonsWithWood.remove(avId)

        if av == base.localAvatar:
            base.localAvatar.controlManager.enableAvatarJump()
            base.localAvatar.currentSpeed = ToontownGlobals.ToonForwardSpeed
            base.localAvatar.currentReverseSpeed = ToontownGlobals.ToonReverseSpeed
            base.localAvatar.controlManager.setSpeeds(ToontownGlobals.ToonForwardSpeed,
                                                      ToontownGlobals.ToonJumpForce,
                                                      ToontownGlobals.ToonReverseSpeed,
                                                      ToontownGlobals.ToonRotateSpeed)
            if self.arrowHover:
                self.arrowHover.finish()
                self.arrowHover = None
            if self.arrow:
                self.arrow.removeNode()
                self.arrow = None
            self.ignore('enterWoolColl' + str(index))
            self.ignore('escape')
            if self.woodDropLabel:
                self.woodDropLabel.destroy()
                self.woodDropLabel = None
            self.localToonDroppedWood = True
            taskMgr.doMethodLater(3, self.removeGracePeriod, self.uniqueName('removeGracePeriod'))

        av.animFSM.request('Happy')
        av.startSmooth()

        if index >= len(self.woodPile):
            return

        self.droppedWood.append(index)
        woodPiece = self.woodPile[index]
        woodPiece.reparentTo(av)
        woodPiece.setPosHprScale(0, 0, 0, 0, 0, 0, 1, 1, 1)
        woodPiece.wrtReparentTo(render)
        woodPiece.setZ(0.1)
        woodColl = CollisionNode('DroppedWoolColl' + str(index))
        woodBox = CollisionBox(0, 4, 0.75, 0.5)
        woodBox.setTangible(0)
        woodColl.addSolid(woodBox)
        woodPiece.attachNewNode(woodColl)
        self.accept('enterDroppedWoolColl' + str(index), self.__enteredDroppedWoodCollision, extraArgs=[index])

    def __enteredDroppedWoodCollision(self, index, _):
        if base.localAvatar.isStunned or self.localToonDroppedWood:
            return
        self.sendUpdate('requestGrabWood', [index])

    def removeGracePeriod(self, task):
        self.localToonDroppedWood = False
        return task.done

    def doMoneyTornadoAttack(self, attackCode, pathNum, spawnNum):
        whirlSfx = loader.loadSfx('phase_5/audio/sfx/tt_s_ara_cfg_whirlwind.ogg')
        tornadoNode = NodePath("tornadoNode")
        tornadoNode.setPos(*FourBossBattleGlobals.TornadoPaths[pathNum][spawnNum])
        tornadoNode.setZ(1)
        tornadoNode.setScale(0.25)
        tornadoNode.reparentTo(render)
        damageCollision = CollisionNode('tornadoDamageColl')
        damageRadius = CollisionTube(0, 0, -15, 0, 0, 60, 27.5)
        damageRadius.setTangible(0)
        damageCollision.addSolid(damageRadius)
        tornadoNode.attachNewNode(damageCollision)
        damageCollision.setName('Tornado')
        damageCollision.setTag('attackCode', str(attackCode))
        self.accept('enterTornado', self.zapLocalToon, extraArgs=[ToontownGlobals.BossCogMoneyTornadoAttack])
        if spawnNum < 4:
            destNum = spawnNum + 1
        else:
            destNum = 0
        tornadoSeq = Parallel(Func(base.playSfx, whirlSfx, looping=1, node=tornadoNode),
                              tornadoNode.posInterval(11, FourBossBattleGlobals.TornadoPaths[pathNum][destNum]))
        for x in range(40):
            tornadoNode.attachNewNode("billNode" + str(x))
            bill = loader.loadModel('phase_10/models/cashbotHQ/MoneyStack')
            bill.setTwoSided(True)
            bill.setPosHprScale(0, 0, 0, random.randint(0, 360), 0, random.randint(0, 360), 3.0 - (x * 0.03),
                                3.0 - (x * 0.03), 3.0 - (x * 0.03))
            bill.reparentTo(tornadoNode.find('**/billNode' + str(x)))
            bill.hide()
            originalBillZ = tornadoNode.find('**/billNode' + str(x)).getZ()
            originalBillH = bill.getH()
            originalBillR = bill.getR()
            seq = Sequence(
                Parallel(
                    Sequence(
                        tornadoNode.find('**/billNode' + str(x)).posInterval(0.5, (0, 0, random.randint(-10, 10))),
                        tornadoNode.find('**/billNode' + str(x)).posInterval(0.5, (0, 0, originalBillZ))
                    ),
                    Sequence(
                        bill.hprInterval(0.5, (random.randint(-360, 360), 0, random.randint(-360, 360))),
                        bill.hprInterval(0.5, (originalBillH, 0, originalBillR))
                    ),
                    tornadoNode.find('**/billNode' + str(x)).hprInterval(1, (-360, 0, 0))
                )
            )
            whirlSeq = Sequence(
                Wait(x * 0.1),
                Func(bill.show),
                Func(seq.loop),
                bill.posInterval(0.5, (30 - x / 2, 0, 75 - (x ** 1.3))),
                Wait(10),
                Func(bill.removeNode)
            )
            if x == 39:
                whirlSeq.append(Func(tornadoNode.removeNode))
                whirlSeq.append(Func(whirlSfx.stop))
                whirlSeq.append(Func(self.tornadoDone, tornadoSeq))
            tornadoSeq.append(whirlSeq)
        self.tornadoSeqs.append(tornadoSeq)
        tornadoSeq.start()

    def tornadoDone(self, tornadoSeq):
        if tornadoSeq in self.tornadoSeqs:
            self.tornadoSeqs.remove(tornadoSeq)

    def doLargeAttack(self, avId):
        self.bossBattle.bossGui.largeAttackFlash(self.bossIndex)
        self.largeAttackSeq = Sequence(
            Wait(3),
            ActorInterval(self, 'Ff_point'), Func(self.loop, 'Ff_neutral')
        )
        self.largeAttackSeq.start()
        self.setChatAbsolute("I'll cover the finances C.E.O.- Ramp up Goon production!", CFSpeech | CFTimeout)

    def setAttackCode(self, attackCode, avId=0, pathNum=None, spawnNum=None, tornadoNum=1):
        DistributedRebornBossCog.setAttackCode(self, attackCode, avId)
        if attackCode == ToontownGlobals.BossCogMoneyTornadoAttack:
            self.setDizzy(0)
            self.setChatAbsolute(random.choice(FourBossBattleGlobals.SmallAttackCFOPhrases), CFSpeech | CFTimeout)
            self.tornadoAttack = Sequence()
            for x in range(tornadoNum):
                self.tornadoAttack.append(Func(self.doMoneyTornadoAttack, attackCode, pathNum, spawnNum))
                self.tornadoAttack.append(Wait(3.0))
                if pathNum < 4:
                    pathNum += 1
                else:
                    pathNum = 0
            self.tornadoAttack.start()

    def setIsDead(self, isDead, dingDing, toon):
        DistributedRebornBossCog.setIsDead(self, isDead)
        if isDead:
            self.__handleCFODeath(dingDing, toon)

    def displayFinalHit(self):
        self.bossBattle.bossGui.showCfoFinalHit()

    def deliverFinalHit(self):
        self.sendUpdate('finalHit', [])

    def __handleCFODeath(self, dingDing, lastToon):
        # Hide final hit GUI...
        self.bossBattle.bossGui.hideCfoFinalHit()

        # Models...
        trainHole = loader.loadModel('phase_5/models/props/traintrack2')
        trainHole.find('**/tracksA').removeNode()
        trainHole.setPosHprScale(46.00, 0.35, -1.04, 90.00, 0.00, 0.00, 14.10, 8.00, .001)
        trainHole.reparentTo(render)

        explosion = loader.loadModel('phase_3.5/models/props/explosion')
        explosion.setZ(15.0)
        explosion.setScale(15.0)
        explosion.setBillboardPointEye()
        explosion.hide()
        explosion.reparentTo(render.find('**/CFOStand'))
        explosion.wrtReparentTo(render)

        cars = [('BoxCar', 85), ('BoxCar', 163), ('FlatCar', 237), ('FlatCar', 325),
                ('TankCar', 410), ('TankCar', 498), ('BoxCar', 587), ('BoxCar', 663), ('BoxCar', 740)]
        trainNode = render.attachNewNode('killerTrain')
        locomotive = loader.loadModel('phase_10/models/cogHQ/CashBotLocomotive')
        locomotive.setPosHpr(46.624, -223, 0.0, -90, 0.0, 0.0)
        locomotive.reparentTo(trainNode)
        allColls = locomotive.findAllMatches('**/+CollisionNode')
        for part, pos in cars:
            trainPiece = loader.loadModel('phase_10/models/cogHQ/CashBot%s' % (part))
            trainPiece.setPosHpr(46.624, -223 - pos, 0.0, -90., 0.0, 0.0)
            trainPiece.reparentTo(trainNode)

            carColls = trainPiece.findAllMatches('**/+CollisionNode')
            allColls += carColls

        for collNode in allColls:
            collNode.setName('TrainColl')
            collNode.setCollideMask(ToontownGlobals.WallBitmask)

        self.accept('enterTrainColl', self.__handleTrainCollision)

        # Sfx...
        growSfx = loader.loadSfx('phase_5/audio/sfx/toonbldg_grow.ogg')
        warningSfx = loader.loadSfx('phase_10/audio/sfx/CBHQ_TRAIN_stopstart.ogg')
        warningInterval = SoundInterval(warningSfx, startTime=3.8)
        trainStart = loader.loadSfx('phase_5/audio/sfx/TL_train.ogg')
        hit1 = loader.loadSfx('phase_5/audio/sfx/TL_train_cog.ogg')
        hit2 = loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart.ogg')
        buttonSfx = loader.loadSfx('phase_3.5/audio/sfx/AA_squirt_flowersquirt.ogg')

        # Toon Sequence...
        buttonTrack = Sequence()
        if lastToon:
            toon = base.cr.doId2do.get(lastToon)
            button = globalPropPool.getProp('button')
            button2 = MovieUtil.copyProp(button)
            buttons = [button, button2]
            hands = toon.getLeftHands()
            buttonTrack = Sequence()
            buttonTrack.append(Func(MovieUtil.showProps, buttons, hands))
            buttonTrack.append(
                Parallel(
                    ActorInterval(toon, 'pushbutton'),
                    SoundInterval(buttonSfx, node=toon)
                )
            )
            buttonTrack.append(Func(MovieUtil.removeProps, buttons))
            buttonTrack.append(Func(toon.loop, 'neutral'))

        self.deathAnimation = Sequence(
            buttonTrack,
            Parallel(
                Func(growSfx.play), warningInterval,
                Sequence(
                    Wait(2.75), Func(trainStart.play),
                    Func(self.setChatAbsolute, "Huh? What's making all that ruckus?",
                         CFSpeech | CFTimeout),
                    Wait(2.75), Func(hit1.play), Wait(.25), Func(hit2.play),
                ),
                Func(self.trolleySequence, dingDing),
                Sequence(
                    Wait(5.2),
                    Parallel(
                        trainNode.posHprInterval(2.0, (0.0, 1164.0, 0.0), (0.0, 0.0, 0.0)),
                        Sequence(
                            Wait(.45), Func(explosion.show),
                            Func(render.find('**/CFOStand').wrtReparentTo, trainNode),
                            Func(render.find('**/MPodium_shadow').removeNode),
                            Wait(.69), Func(explosion.removeNode)
                        )
                    )
                ),
                Sequence(
                    trainHole.scaleInterval(1.25, (14.1, 8, 13.5), blendType='easeInOut'),
                    trainHole.scaleInterval(.420, (14.1, 8, 12.5), blendType='easeInOut'),
                )
            ),
            Wait(2.69),
            Parallel(
                trainHole.scaleInterval(1.0, (14.1, 8, .001), blendType='easeInOut'), Func(self.deleteWood),
            ),
            Func(trainHole.removeNode), Func(trainNode.removeNode)
        )
        self.deathAnimation.start()

    def __handleTrainCollision(self, _):
        base.localAvatar.b_squish(10)

    def deleteWood(self):
        for wood in render.findAllMatches('**/wood'):
            deleteWoodSeq = Sequence(
                wood.posInterval(1.5, (wood.getX(), wood.getY(), -1)),
                Func(wood.removeNode)
            )
            deleteWoodSeq.append(Func(self.deleteWoodDone, deleteWoodSeq))
            self.deleteWoodSeqs.append(deleteWoodSeq)
            deleteWoodSeq.start()

    def deleteWoodDone(self, deleteWoodSeq):
        if deleteWoodSeq in self.deleteWoodSeqs:
            self.deleteWoodSeqs.remove(deleteWoodSeq)

    def trolleySequence(self, dingDing):
        # Adds the trolley easter egg sequence if
        # dingDing is True. (Little Cat was here.)
        if dingDing:
            def animateTrolley(task):
                # Animates the trolley itself.
                for i in range(self.numKeys):
                    key = self.keys[i]
                    ref = self.keyRef[i]
                    h = key.getH()
                    key.setH(ref, h + 10)

                # FIXME: Make the wheels move a bit better.
                for i in range(self.numFrontWheels):
                    frontWheel = self.frontWheels[i]
                    ref = self.frontWheelRef[i]
                    h = frontWheel.getH()
                    frontWheel.setH(ref, h + 5)

                for i in range(self.numBackWheels):
                    backWheel = self.backWheels[i]
                    ref = self.backWheelRef[i]
                    h = backWheel.getH()
                    backWheel.setH(ref, h + 10)

                return task.again

            def setAnimateTrolley(trolley, start):
                if start:
                    taskMgr.add(animateTrolley, 'animateTrolley')
                else:
                    taskMgr.remove('animateTrolley')

            # Trolley Models
            station = loader.loadModel('phase_4/models/modules/trolley_station_TT.bam')
            trolley = station.find('**/trolley_car')
            trolley.reparentTo(render)
            trolley.setPosHpr(45.0, -114.0, 0.0, 0.0, 0.0, 0.0)
            station.removeNode()
            trolley.hide()

            # Set the collision.
            trolleyNode = CollisionNode('TrolleyCollision')
            trolleyBox = CollisionBox(Point3(1, 0, 10), 8, 10, 8)
            trolleyNode.addSolid(trolleyBox)
            trolley.attachNewNode(trolleyNode)

            # Get the parts needed to animate the trolley.
            self.keys = trolley.findAllMatches('**/key')
            self.numKeys = self.keys.getNumPaths()
            self.keyInit = []
            self.keyRef = []
            for i in range(self.numKeys):
                key = self.keys[i]
                key.setTwoSided(1)
                ref = trolley.attachNewNode('key' + `i` + 'ref')
                ref.setPosHpr(key, 0, 0, 0, 0, 0, 0)
                self.keyRef.append(ref)
                self.keyInit.append(key.getTransform())

            self.frontWheels = trolley.findAllMatches('**/front_wheels')
            self.numFrontWheels = self.frontWheels.getNumPaths()
            self.frontWheelInit = []
            self.frontWheelRef = []
            for i in range(self.numFrontWheels):
                wheel = self.frontWheels[i]
                ref = trolley.attachNewNode('frontWheel' + `i` + 'ref')
                ref.setPosHpr(wheel, 0, 0, 0, 0, 0, 0)
                self.frontWheelRef.append(ref)
                self.frontWheelInit.append(wheel.getTransform())

            self.backWheels = trolley.findAllMatches('**/back_wheels')
            self.numBackWheels = self.backWheels.getNumPaths()
            self.backWheelInit = []
            self.backWheelRef = []
            for i in range(self.numBackWheels):
                wheel = self.backWheels[i]
                ref = trolley.attachNewNode('backWheel' + `i` + 'ref')
                ref.setPosHpr(wheel, 0, 0, 0, 0, 0, 0)
                self.backWheelRef.append(ref)
                self.backWheelInit.append(wheel.getTransform())

            # Trolley Sfx
            trolleyAwaySfx = loader.loadSfx('phase_4/audio/sfx/SZ_trolley_away.ogg')
            trolleyBellSfx = loader.loadSfx('phase_4/audio/sfx/SZ_trolley_bell.ogg')
            trolleyHitSfx = loader.loadSfx('phase_4/audio/sfx/MG_sfx_travel_game_bell_for_trolley.ogg')
            trolleyHitStandSfx = loader.loadSfx('phase_5/audio/sfx/TL_train_cog.ogg')

            # The grand entrance!
            self.trolleyIval = Sequence(
                Wait(1.67),
                Func(setAnimateTrolley, trolley, True),
                Func(trolleyBellSfx.play),
                Func(trolleyAwaySfx.play),
                Func(trolley.show),
                trolley.posHprInterval(2.75, (45.0, 19.837, 0.0), (0.0, 0.0, 0.0)),
                Func(setAnimateTrolley, trolley, False),
                Func(trolleyAwaySfx.stop),
                Func(trolleyHitStandSfx.play),
                trolley.posHprInterval(.45, (45.0, 14.449, 0.0), (0.0, 0.0, 0.0)),
                Wait(.70),
                Func(trolleyHitSfx.play),
                LerpScaleInterval(trolley, .1, VBase3(1, 2, 0.025)),
                Wait(1.7),
                LerpScaleInterval(trolley, .1, VBase3(1.4, 1.4, 1.4)),
                LerpScaleInterval(trolley, .1 / 2.0, VBase3(0.8, 0.8, 0.8)),
                LerpScaleInterval(trolley, .1, 1.0),
                Func(setAnimateTrolley, trolley, True),
                Func(trolleyBellSfx.play),
                Func(trolleyAwaySfx.play),
                LerpPosHprInterval(trolley, 3, (45.0, -113.5, 0.0), (0.0, 0.0, 0.0), blendType='easeIn'),
                Func(setAnimateTrolley, trolley, False),
                Func(trolley.removeNode)
            )
            self.trolleyIval.start()
