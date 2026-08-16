from direct.interval.IntervalGlobal import *
from pandac.PandaModules import *
from toontown.toon.DistributedNPCToonBase import *
from direct.task.Task import Task
from toontown.chat.ChatGlobals import *
from toontown.hood import ZoneUtil
from toontown.nametag.NametagGlobals import *
from toontown.quest import QuestChoiceGui
from toontown.quest import QuestParser
from toontown.quest import TrackChoiceGui
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from toontown.toontowngui import TeaserPanel
from toontown.toon import ToonHead
from toontown.toon import ToonHallCustomNPCs

ChoiceTimeout = 20
AVAILABLE_QUEST = 0
QUESTS_FULL = 1
COMPLETED_QUEST = 2
INCOMPLETE_QUEST = 3

class DistributedNPCToon(DistributedNPCToonBase):
    
    def __init__(self, cr):
        DistributedNPCToonBase.__init__(self, cr)

        self.curQuestMovie = None
        self.questChoiceGui = None
        self.trackChoiceGui = None
        self.icon = None
        self.clubGui = None
        self._clubAccessoryNodes = []
        self.npcType = 'Shopkeeper'
        self.questNotifyTypes = [base.loader.loadModel('phase_3/models/gui/quest_exclaim.bam'), base.loader.loadModel('phase_3/models/gui/quest_exclaim_silver.bam'), base.loader.loadModel('phase_3/models/gui/quest_question.bam'), base.loader.loadModel('phase_3/models/gui/quest_question_silver.bam')]
        for icon in self.questNotifyTypes:
            icon.setScale(4)
            icon.setZ(3)
        self.beginCheckTask()


    def _getClubVinciData(self):
        name = getattr(self, 'name', '')
        if name == 'Doe Vinci':
            return {
                'kind': 'creation',
                'headPrefix': '/models/char/toons/head/doevinci-heads-',
                'position': (-0.0291, -3.376, 1.0),
                'heading': 180.0,
                'shirt': 'cosmetics/clothing/maps/cc_t_clth_shirt_npc_doe.png',
                'sleeve': 'cosmetics/clothing/maps/cc_t_clth_shirt_npc_doe_sleeve.png',
                'bottom': 'cosmetics/clothing/maps/cc_t_clth_skirt_npc_doe.png',
                'accessories': (
                    ('cosmetics/hat/models/cc_m_acc_hat_beanie_doe.bam',
                     'cosmetics/hat/maps/cc_t_acc_hat_beanie_doe_yellow.png',
                     'head', (0.0, -0.119, 0.37), (0.0, 10.0, 0.0),
                     (1.0, 1.0, 1.0)),
                    ('cosmetics/neck/models/cc_m_acc_nec_bandana_doe.bam',
                     'cosmetics/neck/maps/cc_t_acc_nec_bandana_doe_1.png',
                     'body', (0.39, -0.713, 0.595),
                     (337.368, 5.39, -0.418), (1.22, 1.189, 1.183)),
                ),
            }
        if name == 'Bro Vinci':
            return {
                'kind': 'shop',
                'headPrefix': '/models/char/toons/head/brovinci-heads-',
                'position': (-0.0707, 3.2519, 1.0),
                'heading': -4.9358,
                'shirt': 'cosmetics/clothing/maps/cc_t_clth_shirt_npc_bro.png',
                'sleeve': 'cosmetics/clothing/maps/cc_t_clth_shirt_npc_bro_sleeve.png',
                'bottom': 'cosmetics/clothing/maps/cc_t_clth_shorts_npc_bro.png',
                'accessories': (
                    ('cosmetics/hat/models/cc_m_acc_hat_hair_bro.bam',
                     'cosmetics/hat/maps/cc_t_acc_hat_hair_bro_brown.png',
                     'head', (0.0, -0.00119, 0.0285),
                     (0.0, 365.17827, 0.0),
                     (1.02956, 1.05154, 0.96088)),
                    ('cosmetics/face/models/cc_m_acc_face_gl_bro.bam',
                     'cosmetics/face/maps/cc_t_acc_face_gl_bro_black.png',
                     'head', (0.0, 0.10827, 0.00746),
                     (0.0, 3.918, 0.0),
                     (0.98433, 0.87821, 0.89471)),
                    ('cosmetics/neck/models/cc_m_acc_nec_necklace_brovinci.bam',
                     'cosmetics/neck/maps/cc_t_acc_nec_necklace_bro_green.png',
                     'body', (0.21805, -0.52942, 0.37327),
                     (365.82687, 356.50393, 360.10788),
                     (1.07851, 1.07625, 1.08305)),
                ),
            }
        return None

    def _isClubVinci(self):
        return self._getClubVinciData() is not None

    def generateToonHead(self, copy=1):
        data = self._getClubVinciData()
        if not data:
            return DistributedNPCToonBase.generateToonHead(self, copy)

        oldPrefix = ToonHead.HeadDict.get('x')
        prefix = data['headPrefix']
        ToonHead.HeadDict['x'] = prefix
        try:
            sourcePath = 'phase_3' + prefix + '1000'
            sourceModel = ToonHead.PreloadHeads.get(sourcePath)
            if sourceModel is None:
                sourceModel = loader.loadModel(sourcePath, okMissing=True)
                if sourceModel:
                    sourceModel.flattenMedium()
                    ToonHead.PreloadHeads[sourcePath] = sourceModel

            if sourceModel:
                # The supplied Vinci heads have one model. Reuse it for all
                # three Altis LOD slots so ToonHead never requests missing files.
                for lod in ('500', '250'):
                    ToonHead.PreloadHeads['phase_3' + prefix + lod] = sourceModel

            return DistributedNPCToonBase.generateToonHead(self, copy)
        finally:
            ToonHead.HeadDict['x'] = oldPrefix

    def setNpcId(self, npcId):
        try:
            DistributedNPCToonBase.setNpcId(self, npcId)
        except AttributeError:
            self.npcId = npcId

        if ToonHallCustomNPCs.getDataForNPC(self):
            self.__startToonHallCustomNPCPositioning()

    def _loadToonHallClothingTexture(self, texturePath):
        texture = loader.loadTexture(texturePath, okMissing=True)
        if texture:
            texture.setMinfilter(Texture.FTLinearMipmapLinear)
            texture.setMagfilter(Texture.FTLinear)
        return texture

    def _applyToonHallExtendedClothing(self):
        # The legacy Toon DNA packet stores shirt, sleeve and bottom texture
        # IDs as uint8. Custom registry IDs can exceed 255, so the AI sends
        # safe zero placeholders and the client applies the real textures here.
        data = ToonHallCustomNPCs.getDataForNPC(self)
        if not data:
            return False

        dna = data.get('dna')
        if not dna or len(dna) < 14:
            return False

        try:
            shirtId = int(dna[8])
            shirtColorId = int(dna[9])
            sleeveId = int(dna[10])
            sleeveColorId = int(dna[11])
            bottomId = int(dna[12])
            bottomColorId = int(dna[13])
        except:
            return False

        # Leave ordinary uint8-compatible NPC clothing to the normal Toon
        # renderer and the existing special-case Toon Hall appearance helpers.
        if (0 <= shirtId <= 255 and
                0 <= sleeveId <= 255 and
                0 <= bottomId <= 255):
            return True

        try:
            from toontown.toon import ToonDNA

            shirtTexture = None
            sleeveTexture = None
            bottomTexture = None

            if 0 <= shirtId < len(ToonDNA.Shirts):
                shirtTexture = self._loadToonHallClothingTexture(
                    ToonDNA.Shirts[shirtId]
                )
            else:
                self.notify.warning(
                    'Custom NPC shirt texture ID %s is unavailable for %s.' %
                    (shirtId, data.get('name', 'unknown NPC'))
                )

            if 0 <= sleeveId < len(ToonDNA.Sleeves):
                sleeveTexture = self._loadToonHallClothingTexture(
                    ToonDNA.Sleeves[sleeveId]
                )
            else:
                self.notify.warning(
                    'Custom NPC sleeve texture ID %s is unavailable for %s.' %
                    (sleeveId, data.get('name', 'unknown NPC'))
                )

            useGirlBottom = data.get('gender', dna[3]) == 'f'
            explicitGirlSkirt = data.get('girlSkirt')
            explicitBoyShorts = data.get('boyShorts')

            if explicitGirlSkirt:
                bottomId = int(explicitGirlSkirt[0])
                bottomColorId = int(explicitGirlSkirt[1])
                useGirlBottom = True
            elif explicitBoyShorts:
                bottomId = int(explicitBoyShorts[0])
                bottomColorId = int(explicitBoyShorts[1])
                useGirlBottom = False

            if useGirlBottom:
                if 0 <= bottomId < len(ToonDNA.GirlBottoms):
                    bottomPath = ToonDNA.GirlBottoms[bottomId][0]
                    bottomTexture = self._loadToonHallClothingTexture(
                        bottomPath
                    )
                else:
                    self.notify.warning(
                        'Custom NPC girl bottom texture ID %s is unavailable '
                        'for %s.' %
                        (bottomId, data.get('name', 'unknown NPC'))
                    )
            else:
                if 0 <= bottomId < len(ToonDNA.BoyShorts):
                    bottomTexture = self._loadToonHallClothingTexture(
                        ToonDNA.BoyShorts[bottomId]
                    )
                else:
                    self.notify.warning(
                        'Custom NPC shorts texture ID %s is unavailable for %s.' %
                        (bottomId, data.get('name', 'unknown NPC'))
                    )

            white = VBase4(1.0, 1.0, 1.0, 1.0)
            if 0 <= shirtColorId < len(ToonDNA.ClothesColors):
                shirtColor = ToonDNA.ClothesColors[shirtColorId]
            else:
                shirtColor = white
            if 0 <= sleeveColorId < len(ToonDNA.ClothesColors):
                sleeveColor = ToonDNA.ClothesColors[sleeveColorId]
            else:
                sleeveColor = white
            if 0 <= bottomColorId < len(ToonDNA.ClothesColors):
                bottomColor = ToonDNA.ClothesColors[bottomColorId]
            else:
                bottomColor = white

            darkBottomColor = bottomColor * 0.5
            darkBottomColor.setW(1.0)
            applied = False

            for lodName in self.getLODNames():
                torso = self.getPart('torso', lodName)
                if not torso:
                    continue

                top = torso.find('**/torso-top')
                if shirtTexture and not top.isEmpty():
                    top.setTexture(shirtTexture, 1)
                    top.setColor(shirtColor)
                    applied = True

                sleeves = torso.find('**/sleeves')
                if sleeveTexture and not sleeves.isEmpty():
                    sleeves.setTexture(sleeveTexture, 1)
                    sleeves.setColor(sleeveColor)
                    applied = True

                bottoms = torso.findAllMatches('**/torso-bot')
                for index in range(bottoms.getNumPaths()):
                    bottom = bottoms.getPath(index)
                    if bottomTexture:
                        bottom.setTexture(bottomTexture, 1)
                    bottom.setColor(bottomColor)
                    applied = True

                caps = torso.findAllMatches('**/torso-bot-cap')
                for index in range(caps.getNumPaths()):
                    caps.getPath(index).setColor(darkBottomColor)

            return applied
        except Exception, error:
            self.notify.warning(
                'Could not apply extended custom NPC clothing for %s: %s' %
                (data.get('name', 'unknown NPC'), error)
            )
            return False

    def __startToonHallCustomNPCPositioning(self):
        taskName = self.uniqueName('positionToonHallCustomNPC')
        taskMgr.remove(taskName)

        if ToonHallCustomNPCs.positionClientNPC(self):
            self._applyToonHallExtendedClothing()
            self.setAnimState('neutral', 0.9, None, None)
            return

        # The distributed NPC can generate before the Toon Hall model. Retry
        # only until the interior exists, then stop permanently.
        taskMgr.doMethodLater(
            0.1,
            self.__positionToonHallCustomNPC,
            taskName
        )

    def _getToonseltownData(self):
        if ZoneUtil.getCanonicalHoodId(getattr(self, 'zoneId', 0)) != ToontownGlobals.Toonseltown:
            return None
        data = {
            'Shinny Upatree': ((101.392, -41.948, 23.6), 60.439, 'Villager'),
            'Candie LaBrum': ((170.5, 6.6, 29.208), 110, 'Spirit of the Past'),
            'Perez Cent': ((70.302, -93.298, 20.716), 72.94, 'Spirit of the Present'),
            'Corgi Diem': ((-216.75, 126.14, 51.147), 96.25, 'Spirit of the Future'),
            'Pepper Minstix': ((-5.252, 301.172, 32.860), 131.719, 'Elf'),
        }
        return data.get(self.getName())

    def _applyToonseltownClothes(self):
        clothes = {
            'Shinny Upatree': (506, 484, 'boy', 276, 'ss'),
            'Candie LaBrum': (515, 492, 'girl', 218, 'md'),
            'Perez Cent': (517, 494, 'boy', 284, 'ss'),
            'Corgi Diem': (163, 154, 'boy', 70, 'ls'),
            'Pepper Minstix': (506, 484, 'boy', 276, 'ms'),
        }
        data = clothes.get(self.getName())
        if not data:
            return False
        try:
            from toontown.toon import ToonDNA
            shirtId, sleeveId, bottomKind, bottomId, torsoCode = data
            if self.style.torso != torsoCode:
                self.swapToonTorso(torsoCode, genClothes=0)
            shirtTex = loader.loadTexture(ToonDNA.Shirts[shirtId], okMissing=True)
            sleeveTex = loader.loadTexture(ToonDNA.Sleeves[sleeveId], okMissing=True)
            if bottomKind == 'boy':
                bottomPath = ToonDNA.BoyShorts[bottomId]
            else:
                bottomPath = ToonDNA.GirlBottoms[bottomId][0]
            bottomTex = loader.loadTexture(bottomPath, okMissing=True)
            if not shirtTex or not sleeveTex or not bottomTex:
                return False
            shirtTex.setMinfilter(Texture.FTLinearMipmapLinear)
            shirtTex.setMagfilter(Texture.FTLinear)
            sleeveTex.setMinfilter(Texture.FTLinearMipmapLinear)
            sleeveTex.setMagfilter(Texture.FTLinear)
            bottomTex.setMinfilter(Texture.FTLinearMipmapLinear)
            bottomTex.setMagfilter(Texture.FTLinear)
            color = ToonDNA.ClothesColors[0]
            darkColor = color * 0.5
            darkColor.setW(1.0)
            for lodName in self.getLODNames():
                torso = self.getPart('torso', lodName)
                top = torso.find('**/torso-top')
                if not top.isEmpty():
                    top.setTexture(shirtTex, 1)
                    top.setColor(color)
                sleeves = torso.find('**/sleeves')
                if not sleeves.isEmpty():
                    sleeves.setTexture(sleeveTex, 1)
                    sleeves.setColor(color)
                bottoms = torso.findAllMatches('**/torso-bot')
                for index in xrange(bottoms.getNumPaths()):
                    bottom = bottoms.getPath(index)
                    bottom.setTexture(bottomTex, 1)
                    bottom.setColor(color)
                torso.findAllMatches('**/torso-bot-cap').setColor(darkColor)
            return True
        except:
            return False

    def _applyToonseltownTransparency(self):
        if self.getName() not in ('Candie LaBrum', 'Perez Cent', 'Corgi Diem'):
            return False
        try:
            track = self.doToonColorScale(VBase4(1, 1, 1, 0.6), 0, keepDefault=1)
            if track:
                track.start()
            return True
        except:
            return False

    def _applyToonseltownNPCState(self):
        data = self._getToonseltownData()
        if not data:
            return False
        self.reparentTo(render)
        self.setPos(*data[0])
        self.setH(data[1])
        self.npcType = data[2]
        self.setToonTag(data[2])
        self._applyToonseltownClothes()
        self._applyToonseltownTransparency()
        self.setAnimState('neutral', 0.9, None, None)
        return True

    def initToonState(self):
        if self._applyToonseltownNPCState():
            return

        customData = ToonHallCustomNPCs.getDataForNPC(self)
        if customData:
            self.__startToonHallCustomNPCPositioning()
            return

        data = self._getClubVinciData()
        if not data:
            return DistributedNPCToonBase.initToonState(self)
        self.reparentTo(render)
        self.setPos(*data['position'])
        self.setH(data['heading'])
        self.setAnimState('neutral', 0.9, None, None)

    def __positionToonHallCustomNPC(self, task):
        if ToonHallCustomNPCs.positionClientNPC(self):
            self._applyToonHallExtendedClothing()
            self.setAnimState('neutral', 0.9, None, None)
            return Task.done

        task.delayTime = 0.1
        return task.again

    def _loadClubTexture(self, path):
        texture = loader.loadTexture(path, okMissing=True)
        if texture:
            texture.setMinfilter(Texture.FTLinearMipmapLinear)
            texture.setMagfilter(Texture.FTLinear)
        return texture

    def _clearClubAccessories(self):
        for node in self._clubAccessoryNodes:
            if node and not node.isEmpty():
                node.removeNode()
        self._clubAccessoryNodes = []

    def _attachClubAccessory(self, modelPath, texturePath, target, pos, hpr, scale):
        model = loader.loadModel(modelPath, okMissing=True)
        if not model:
            return
        texture = self._loadClubTexture(texturePath) if texturePath else None
        if texture:
            model.setTexture(texture, 1)
        model.setPos(*pos)
        model.setHpr(*hpr)
        model.setScale(*scale)
        model.setTwoSided(True)
        if target == 'head':
            targets = self.findAllMatches('**/__Actor_head')
        else:
            targets = self.findAllMatches('**/def_joint_attachFlower')
        for targetNode in targets:
            holder = targetNode.attachNewNode('clubVinciAccessory')
            model.instanceTo(holder)
            self._clubAccessoryNodes.append(holder)

    def _applyClubVinciAppearance(self):
        data = self._getClubVinciData()
        if not data:
            return
        shirt = self._loadClubTexture(data['shirt'])
        sleeve = self._loadClubTexture(data['sleeve'])
        bottom = self._loadClubTexture(data['bottom'])
        for lod in ('1000', '500', '250'):
            torso = self.getPart('torso', lod)
            if torso:
                top = torso.find('**/torso-top')
                if shirt and not top.isEmpty():
                    top.setTexture(shirt, 1)
                sleeves = torso.find('**/sleeves')
                if sleeve and not sleeves.isEmpty():
                    sleeves.setTexture(sleeve, 1)
                if bottom:
                    for geom in torso.findAllMatches('**/torso-bot'):
                        geom.setTexture(bottom, 1)
        self._clearClubAccessories()
        for definition in data['accessories']:
            self._attachClubAccessory(*definition)

    def _prepareClubInteraction(self):
        try:
            place = base.cr.playGame.getPlace()
            if place:
                place.fsm.request('stopped')
        except:
            pass
        try:
            base.localAvatar.stopLookAround()
            self.stopLookAround()
            base.localAvatar.lookAt(self)
            self.lookAt(base.localAvatar)
        except:
            pass

    def _restoreClubInteraction(self, *args):
        self.clubGui = None
        try:
            place = base.cr.playGame.getPlace()
            if place:
                place.fsm.request('walk')
        except:
            pass
        try:
            base.localAvatar.startLookAround()
            self.startLookAround()
        except:
            pass

    def _closeClubGui(self):
        if self.clubGui:
            try:
                self.clubGui.destroy()
            except:
                pass
            self.clubGui = None

    def _handleClubVinciInteraction(self):
        data = self._getClubVinciData()
        manager = getattr(base.cr, 'clubMgr', None)
        if not manager:
            self.setChatAbsolute('The Club system is currently unavailable.', CFSpeech | CFTimeout)
            return

        if data['kind'] == 'creation':
            if manager.isInClub():
                self.setChatAbsolute('You are already a member of a Club!', CFSpeech | CFTimeout)
                manager.openClubPanel()
                return
            self._prepareClubInteraction()
            self.acceptOnce('club-creation-gui-done', self._restoreClubInteraction)
            self.clubGui = manager.openCreationGui(self)
            return

        if not manager.isInClub():
            self.setChatAbsolute('Come back after you have joined or created a Club!', CFSpeech | CFTimeout)
            return
        self._prepareClubInteraction()
        self.acceptOnce('club-shop-gui-done', self._restoreClubInteraction)
        self.clubGui = manager.openShopGui(self)

    def applySakamoreoNametagColor(self):
        if self.getName() != 'Sakamoreo':
            return

        currentColor = self.nametag.getNametagColor()
        red = VBase4(1, 0, 0, 1)

        redNametagColor = (
            (red, currentColor[0][1]),
            (red, currentColor[1][1]),
            (red, currentColor[2][1]),
            (red, currentColor[3][1]),
            currentColor[4]
        )

        self.nametag.setNametagColor(redNametagColor)
        self.nametag.updateAll()

    def _applyCustomNPCDisplayName(self):
        if ToonHallCustomNPCs.isCustomNPC(self) or self._isClubVinci():
            self.npcType = ''
            self.setDisplayName(self.getName())

    def announceGenerate(self):
        DistributedNPCToonBase.announceGenerate(self)
        self._applyToonseltownNPCState()
        if ToonHallCustomNPCs.getDataForNPC(self):
            self.__startToonHallCustomNPCPositioning()
        self._applyCustomNPCDisplayName()
        if self._isClubVinci():
            self._applyClubVinciAppearance()
        self.applySakamoreoNametagColor()

    def setPlayerType(self, playerType):
        DistributedNPCToonBase.setPlayerType(self, playerType)
        self._applyCustomNPCDisplayName()
        self.applySakamoreoNametagColor()

    def allowedToTalk(self):
        return True

    def delayDelete(self):
        DistributedNPCToonBase.delayDelete(self)

        if self.curQuestMovie:
            curQuestMovie = self.curQuestMovie
            self.curQuestMovie = None
            curQuestMovie.timeout(fFinish=1)
            curQuestMovie.cleanup()

    def disable(self):
        self._closeClubGui()
        self._clearClubAccessories()
        self.cleanupMovie()
        taskMgr.remove('update-quests')
        taskMgr.remove(self.uniqueName('positionToonHallCustomNPC'))

        DistributedNPCToonBase.disable(self)

    def cleanupMovie(self):
        self.clearChat()
        self.ignore('chooseQuest')
        if self.questChoiceGui:
            self.questChoiceGui.destroy()
            self.questChoiceGui = None
        self.ignore(self.uniqueName('doneChatPage'))
        if self.curQuestMovie:
            self.curQuestMovie.timeout(fFinish=1)
            self.curQuestMovie.cleanup()
            self.curQuestMovie = None
        if self.trackChoiceGui:
            self.trackChoiceGui.destroy()
            self.trackChoiceGui = None

    def _getCurrentPlace(self):
        playGame = getattr(base.cr, 'playGame', None)
        if playGame is None:
            return None
        try:
            return playGame.getPlace()
        except AttributeError:
            return None

    def _requestWalkState(self, expectedPlace=None):
        place = self._getCurrentPlace()
        if place is None:
            return False

        # A delayed callback from an NPC in the previous place must never
        # change the state of a newly loaded place.
        if expectedPlace is not None and place is not expectedPlace:
            return False

        try:
            place.setState('walk')
        except AttributeError:
            fsm = getattr(place, 'fsm', None)
            if fsm is None:
                return False
            fsm.request('walk')
        return True

    def handleCollisionSphereEnter(self, collEntry):
        customPhrase = ToonHallCustomNPCs.getPhraseForNPC(self)
        if customPhrase is not None:
            self.clearChat()
            self.lookAt(base.localAvatar)
            ToonHallCustomNPCs.playInteractionAnimation(self)
            self.setChatAbsolute(customPhrase, CFSpeech | CFTimeout)
            return

        if self._isClubVinci():
            self._handleClubVinciInteraction()
            return
        place = self._getCurrentPlace()
        if place is None:
            return
        place.fsm.request('quest', [self])
        self.sendUpdate('avatarEnter', [])

    def handleOkTeaser(self):
        self.dialog.destroy()
        del self.dialog
        place = base.cr.playGame.getPlace()
        if place:
            place.fsm.request('walk')

    def finishMovie(self, av, isLocalToon, elapsedTime):
        self.cleanupMovie()
        av.startLookAround()
        self.startLookAround()
        self.detectAvatars()
        self.initPos()
        if isLocalToon:
            self.showNametag2d()
            taskMgr.remove(self.uniqueName('lerpCamera'))
            self.returnCamera()
            self.sendUpdate('setMovieDone', [])
            self.nametag3d.clearDepthTest()
            self.nametag3d.clearBin()
            
    def returnCamera(self):
        avHeight = max(base.localAvatar.getHeight(), 3.0)
        scaleFactor = avHeight * 0.3333333333
        camera.wrtReparentTo(base.localAvatar)
        camera.posQuatInterval(1, (0, -9 * scaleFactor, avHeight), (0, 0, 0), other=base.localAvatar, blendType='easeInOut').start()
        expectedPlace = self._getCurrentPlace()

        def walk():
            self._requestWalkState(expectedPlace)

        Sequence(Wait(1), Func(walk)).start()
        
    def setupCamera(self, mode):
        camera.wrtReparentTo(render)
        if mode == NPCToons.QUEST_MOVIE_QUEST_CHOICE or mode == NPCToons.QUEST_MOVIE_TRACK_CHOICE:
            camera.posQuatInterval(1, (5, 9, self.getHeight() - 0.5), (155, -2, 0), other=self, blendType='easeInOut').start()
        else:
            camera.posQuatInterval(1, (-5, 9, self.getHeight() - 0.5), (-150, -2, 0), other=self, blendType='easeInOut').start()

    def setMovie(self, mode, npcId, avId, quests, timestamp):
        isLocalToon = avId == base.localAvatar.doId
        if mode == NPCToons.QUEST_MOVIE_CLEAR:
            self.cleanupMovie()
            if isLocalToon:
                self.returnCamera()
            return
        if mode == NPCToons.QUEST_MOVIE_TIMEOUT:
            self.cleanupMovie()
            if isLocalToon:
                self.returnCamera()
            self.setPageNumber(0, -1)
            self.clearChat()
            self.startLookAround()
            self.detectAvatars()
            return
        av = base.cr.doId2do.get(avId)
        if av is None:
            self.notify.warning('Avatar %d not found in doId' % avId)
            return
        if mode == NPCToons.QUEST_MOVIE_REJECT:
            rejectString = Quests.chooseQuestDialogReject()
            rejectString = Quests.fillInQuestNames(rejectString, avName=av.name)
            self.setChatAbsolute(rejectString, CFSpeech | CFTimeout)
            if isLocalToon:
                base.localAvatar.posCamera(0, 0)
                self._requestWalkState()
            return
        if mode == NPCToons.QUEST_MOVIE_TIER_NOT_DONE:
            rejectString = Quests.chooseQuestDialogTierNotDone()
            rejectString = Quests.fillInQuestNames(rejectString, avName=av.name)
            self.setChatAbsolute(rejectString, CFSpeech | CFTimeout)
            if isLocalToon:
                base.localAvatar.posCamera(0, 0)
                self._requestWalkState()
            return
        self.setupAvatars(av)
        fullString = ''
        toNpcId = None
        if isLocalToon:
            self.hideNametag2d()
        if mode == NPCToons.QUEST_MOVIE_COMPLETE:
            questId, rewardId, toNpcId = quests
            scriptId = 'quest_complete_' + str(questId)
            if QuestParser.questDefined(scriptId):
                self.curQuestMovie = QuestParser.NPCMoviePlayer(scriptId, av, self)
                self.curQuestMovie.play()
                return
            if isLocalToon:
                self.setupCamera(mode)
            greetingString = Quests.chooseQuestDialog(questId, Quests.GREETING)
            if greetingString:
                fullString += greetingString + '\x07'
            fullString += Quests.chooseQuestDialog(questId, Quests.COMPLETE) + '\x07'
            if rewardId > 2:
                fullString += Quests.getReward(rewardId).getString()
            quest = Quests.QuestDict.get(questId)
            experience = quest[Quests.QuestDictExperienceIndex]
            money = quest[Quests.QuestDictMoneyIndex]
            fullString += TTLocalizer.QuestMovieExpJbReward % {'exp': experience, 'money': money}
            leavingString = Quests.chooseQuestDialog(questId, Quests.LEAVING)
            if leavingString:
                fullString += '\x07' + leavingString
        elif mode == NPCToons.QUEST_MOVIE_QUEST_CHOICE_CANCEL:
            fullString = TTLocalizer.QuestMovieQuestChoiceCancel
        elif mode == NPCToons.QUEST_MOVIE_TRACK_CHOICE_CANCEL:
            fullString = TTLocalizer.QuestMovieTrackChoiceCancel
        elif mode == NPCToons.QUEST_MOVIE_INCOMPLETE:
            questId, completeStatus, toNpcId = quests
            scriptId = 'quest_incomplete_' + str(questId)
            if QuestParser.questDefined(scriptId):
                if self.curQuestMovie:
                    self.curQuestMovie.timeout()
                    self.curQuestMovie.cleanup()
                    self.curQuestMovie = None
                self.curQuestMovie = QuestParser.NPCMoviePlayer(scriptId, av, self)
                self.curQuestMovie.play()
                return
            if isLocalToon:
                self.setupCamera(mode)
            greetingString = Quests.chooseQuestDialog(questId, Quests.GREETING)
            if greetingString:
                fullString += greetingString + '\x07'
            fullString += Quests.chooseQuestDialog(questId, completeStatus)
            leavingString = Quests.chooseQuestDialog(questId, Quests.LEAVING)
            if leavingString:
                fullString += '\x07' + leavingString
        elif mode == NPCToons.QUEST_MOVIE_ASSIGN:
            questId, rewardId, toNpcId = quests
            scriptId = 'quest_assign_' + str(questId)
            if QuestParser.questDefined(scriptId):
                if self.curQuestMovie:
                    self.curQuestMovie.timeout()
                    self.curQuestMovie.cleanup()
                    self.curQuestMovie = None
                self.curQuestMovie = QuestParser.NPCMoviePlayer(scriptId, av, self)
                self.curQuestMovie.play()
                return
            if isLocalToon:
                self.setupCamera(mode)
            fullString += Quests.chooseQuestDialog(questId, Quests.QUEST)
            leavingString = Quests.chooseQuestDialog(questId, Quests.LEAVING)
            if leavingString:
                fullString += '\x07' + leavingString
        elif mode == NPCToons.QUEST_MOVIE_QUEST_CHOICE:
            if isLocalToon:
                self.setupCamera(mode)
            self.setChatAbsolute(TTLocalizer.QuestMovieQuestChoice, CFSpeech)
            if isLocalToon:
                self.acceptOnce('chooseQuest', self.sendChooseQuest)
                self.questChoiceGui = QuestChoiceGui.QuestChoiceGui()
                self.questChoiceGui.setQuests(quests, npcId, ChoiceTimeout)
            return
        elif mode == NPCToons.QUEST_MOVIE_TRACK_CHOICE:
            if isLocalToon:
                self.setupCamera(mode)
            tracks = quests
            self.setChatAbsolute(TTLocalizer.QuestMovieTrackChoice, CFSpeech)
            if isLocalToon:
                self.acceptOnce('chooseTrack', self.sendChooseTrack)
                self.trackChoiceGui = TrackChoiceGui.TrackChoiceGui(tracks, ChoiceTimeout)
            return
        fullString = Quests.fillInQuestNames(fullString, avName=av.name, fromNpcId=npcId, toNpcId=toNpcId)
        self.acceptOnce(self.uniqueName('doneChatPage'), self.finishMovie, extraArgs=[av, isLocalToon])
        self.clearChat()
        self.setPageChat(avId, 0, fullString, 1)

    def sendChooseQuest(self, questId):
        if self.questChoiceGui:
            self.questChoiceGui.destroy()
            self.questChoiceGui = None
        self.sendUpdate('chooseQuest', [questId])

    def sendChooseTrack(self, trackId):
        if self.trackChoiceGui:
            self.trackChoiceGui.destroy()
            self.trackChoiceGui = None
        self.sendUpdate('chooseTrack', [trackId])
		
    def checkQuestStatus(self):
        if self._isClubVinci() or ToonHallCustomNPCs.isCustomNPC(self):
            self.setQuestNotify(None)
            return
        av = base.localAvatar
        retVal = self.hasQuests()
        if retVal is not None:
            self.setQuestNotify(retVal)
        elif self.checkCompletedQuests():
            self.setQuestNotify(COMPLETED_QUEST)
        elif self.checkIncompletedQuests():
            self.setQuestNotify(INCOMPLETE_QUEST)
        else:
            self.setQuestNotify(None)
			
    def setQuestNotify(self, type):
        try:
            if type is None:
                if self.icon:
                    self.icon.detachNode()
                    del self.icon
                return
            if self.icon:
                self.icon.detachNode()
                self.icon = None
            self.icon = self.questNotifyTypes[type]
            np = NodePath(self.nametag.getIcon())
            if np.isEmpty():
                return
            self.icon.reparentTo(np)
        except:
            pass
		
    def hasQuests(self):
        potentialQuests = []
        nyaQuests = []
        av = base.localAvatar
        for quest in Quests.QuestDict.keys():
            questEntry = Quests.QuestDict.get(quest)
            if NPCToons.getNPCName(questEntry[Quests.QuestDictFromNpcIndex]) == self.getName():
                if questEntry[1] == Quests.Start:
                    potentialQuests.append(quest)
        for quest in potentialQuests:
            questEntry = Quests.QuestDict.get(quest)
            if quest in av.getQuestHistory():
                if quest in potentialQuests:
                    potentialQuests.remove(quest)
            for needed in questEntry[0]:
                if not needed in av.getQuestHistory():
                    nyaQuests.append(quest)
                    if quest in potentialQuests:
                        potentialQuests.remove(quest)
        if len(potentialQuests) > 0:
            return AVAILABLE_QUEST
        elif len(nyaQuests) > 0 and len(potentialQuests) == 0:
            return QUESTS_FULL
        else:
            return None
		
    def checkCompletedQuests(self):
        av = base.localAvatar
        for quest in av.quests:
            questId, fromNpcId, toNpcId, rewardId, toonProgress = quest
            newQuest = tuple(quest)
            actualQuest = Quests.getQuest(questId)
            fComplete = actualQuest.getCompletionStatus(av, newQuest) == Quests.COMPLETE
            name = self.getName()
            if fComplete:
                questId, fromNpcId, toNpcId, rewardId, toonProgress = quest
                entry = NPCToons.NPCToonDict.get(toNpcId)
                if entry[1] == name:
                    return True
        return False
		
    def checkIncompletedQuests(self):
        av = base.localAvatar
        for quest in av.quests:
            questId, fromNpcId, toNpcId, rewardId, toonProgress = quest
            newQuest = tuple(quest)
            actualQuest = Quests.getQuest(questId)
            fIncomplete = actualQuest.getCompletionStatus(av, newQuest) == Quests.INCOMPLETE
            name = self.getName()
            if fIncomplete:
                questId, fromNpcId, toNpcId, rewardId, toonProgress = quest
                entry = NPCToons.NPCToonDict.get(toNpcId)
                if entry[1] == name:
                    return True
        return False
		
		
    def beginCheckTask(self):
        taskMgr.doMethodLater(1, self.__updateQuest, 'update-quests')
		
    def __updateQuest(self, task):
        self.checkQuestStatus()
        taskMgr.doMethodLater(1, self.__updateQuest, 'update-quests')
        return Task.done
        
