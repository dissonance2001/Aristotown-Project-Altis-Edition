from pandac.PandaModules import *
from direct.fsm import StateData
from direct.gui.DirectGui import *
from toontown.toonbase import TTLocalizer
from toontown.toonbase.ToontownBattleGlobals import *
from panda3d.core import TextureStage
from direct.interval.IntervalGlobal import *
from toontown.battle import BattleBase
from toontown.toon import IOURegistry
from toontown.toon import NPCToons
from toontown.toon import ToonHead
from toontown.toon import ToonDNA


class TownBattleWaitPanel(StateData.StateData):

    def __init__(self, doneEvent):
        StateData.StateData.__init__(self, doneEvent)
        self.track = None
        self.level = None
        self.iouHead = None

    def load(self):
        gui = loader.loadModel('phase_3.5/models/gui/battlegui/targeting')
        self.rowModels = loader.loadModel('phase_3.5/models/gui/battlegui/gag_selection_panels')
        self.invModel = loader.loadModel('phase_3.5/models/gui/inventory_icons')
        self.status = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.passIcon = self.rowModels.find('**/pass_icon')
        self.fireIcon = self.status.find('**/pinkslip_icon')
        self.sueIcon = self.status.find('**/sued_icon')
        self.sosIcon = self.status.find('**/energized_icon')
        self.invModels = []
        for track in range(len(AvPropsNew)):
            itemList = []
            for item in range(len(AvPropsNew[track])):
                itemList.append(self.invModel.find('**/' + AvPropsNew[track][item]))
            self.invModels.append(itemList)

        self.frame = DirectFrame(
            relief=None,
            image=gui.find('**/targeting_main'),
            text_align=TextNode.ALeft,
            pos=(0, 0, -0.025),
            scale=0.425
        )
        self.frame.hide()
        self.textFrame = DirectFrame(parent=self.frame, relief=None, text='', text_fg=Vec4(0.973, 1, 0, 1), text_font=getMinnieFont(), text_scale=0.1, pos=(0, 0, -0.325))
        self.gagEmblem = DirectFrame(
            parent=self.frame,
            image=self.rowModels.find('**/emblem_gag'),
            pos=(0, 0, 0.145),
            scale=1,
            relief=None
        )
        self.gagEmblem.setBin('fixed', 0)

        self.gagIcon = DirectFrame(
            parent=self.frame,
            relief=None,
            image=None,
            scale=1,
            pos=(0, 0, 0.145)
        )
        self.gagIcon.setBin('fixed', 20)

        self.gagEmblemOrganicTex = loader.loadTexture('phase_3.5/maps/battlegui/pres_scroll_bg.png')
        self.gagEmblemOrganicTex.setWrapU(Texture.WMRepeat)
        self.gagEmblemOrganicTex.setWrapV(Texture.WMRepeat)

        self.gagEmblemScrollStage = TextureStage('wait-gag-emblem-scroll')
        self.gagEmblemScrollIval = LerpFunctionInterval(
            self.updateGagEmblemScroll,
            duration=3.0,
            fromData=0.0,
            toData=1.0
        )
        self.gagEmblemScrollIval.loop()

        self.backButton = DirectButton(parent=self.frame, relief=None, image=(gui.find('**/back_neutral'), gui.find('**/back_press'), gui.find('**/back_hover')), pos=(0, 0, -0.6),
                                        scale=(.75, .5, .5), text="BACK", text_scale=(.175, .25, .25), text_pos=(0.05, -0.1), text_fg=Vec4(0.973, 1, 0, 1), text_font=getMinnieFont(), command=self.__handleBack)
        self.backButton.setBin('fixed', 0) 
        gui.removeNode()

    def setGagEmblemOrganic(self, organic):
        imageNode = self.gagEmblem.component('image0')

        if organic:
            imageNode.setTexture(self.gagEmblemScrollStage, self.gagEmblemOrganicTex, 1)
            imageNode.setTexScale(self.gagEmblemScrollStage, 6, 6)
            imageNode.setTransparency(1)
        else:
            imageNode.clearTexture(self.gagEmblemScrollStage)

    def updateGagEmblemScroll(self, t):
        if not hasattr(self, 'gagEmblem') or self.gagEmblem is None:
            return

        imageNode = self.gagEmblem.component('image0')
        imageNode.setTexOffset(self.gagEmblemScrollStage, t, -t)

    def unload(self):
        self.__clearIOUHead()
        if getattr(self, 'gagEmblemScrollIval', None):
            self.gagEmblemScrollIval.finish()
            self.gagEmblemScrollIval = None

        self.gagIcon.destroy()
        self.gagEmblem.destroy()
        self.backButton.destroy()
        self.frame.destroy()

        self.invModel.removeNode()
        self.rowModels.removeNode()

        del self.gagIcon
        del self.gagEmblem
        del self.backButton
        del self.frame
        del self.invModels
        del self.invModel
        self.status.removeNode()
        del self.status
        self.textFrame.destroy()
        del self.textFrame
        del self.rowModels
        del self.gagEmblemOrganicTex
        del self.gagEmblemScrollStage


    def enter(self, numParticipants, track=None, level=None, mode='Inventory'):
        self.track = track
        self.level = level
        self.__clearIOUHead()
        if mode == 'Inventory' and track is not None and level is not None and track >= 0 and level >= 0:
            self.gagIcon['image'] = self.invModels[track][level]
            self.gagIcon.setScale(3)
            self.gagIcon['image_scale'] = 1

            trackColor = Vec4(TrackColors[track][0], TrackColors[track][1], TrackColors[track][2], 1)
            self.gagEmblem['image_color'] = trackColor
            self.setGagEmblemOrganic(base.localAvatar.checkGagBonus(track, level))

        elif mode == 'IOU':
            definition = IOURegistry.getIOU(level)
            self.gagIcon['image'] = None
            self.gagIcon.setScale(1)
            self.gagIcon.show()
            if definition is not None:
                gagTrack = definition.getGagTrack()
                if gagTrack == -1:
                    self.gagEmblem['image_color'] = Vec4(1, 1, 1, 1)
                else:
                    self.gagEmblem['image_color'] = Vec4(TrackColors[gagTrack][0], TrackColors[gagTrack][1], TrackColors[gagTrack][2], 1)
                self.iouHead = self.__createNPCHead(definition.getNpcId(), 0.45)
                self.iouHead.reparentTo(self.gagIcon)
            self.setGagEmblemOrganic(False)

        elif mode == 'Pass':
            self.gagIcon['image'] = self.passIcon
            self.gagIcon.setScale(.7)
            self.gagIcon['image_scale'] = .7
            self.gagIcon.show()
            self.gagEmblem['image_color'] = Vec4(1, 0, 0, 1)
            self.setGagEmblemOrganic(False)

        elif mode == 'Fire':
            self.gagIcon['image'] = self.fireIcon
            self.gagIcon.setScale(.75)
            self.gagIcon['image_scale'] = .75
            self.gagIcon.show()
            self.gagEmblem['image_color'] = Vec4(0.937, 0.718, 0.816, 1)
            self.setGagEmblemOrganic(False)

        elif mode == 'SOS':
            self.gagIcon['image'] = self.sosIcon
            self.gagIcon.setScale(.75)
            self.gagIcon['image_scale'] = .75
            self.gagIcon.show()

            self.gagEmblem['image_color'] = Vec4(0, 1, 0.031, 1)
            self.setGagEmblemOrganic(False)

        elif mode == 'Sue':
            self.gagIcon['image'] = self.sueIcon
            self.gagIcon.setScale(.75)
            self.gagIcon['image_scale'] = .75
            self.gagIcon.show()
            self.gagEmblem['image_color'] = Vec4(0.682, 0.714, 0.824, 1)
            self.setGagEmblemOrganic(False)

        else:
            self.gagIcon.hide()
            self.setGagEmblemOrganic(False)

        if numParticipants > 1:
            self.textFrame['text'] = "Locked In!"
        else:
            self.textFrame['text'] = "Please wait..."

        self.frame.show()

    def exit(self):
        self.frame.hide()
        self.__clearIOUHead()


    def __clearIOUHead(self):
        if self.iouHead:
            self.iouHead.detachNode()
            self.iouHead.delete()
            self.iouHead = None

    def __createNPCHead(self, npcId, dimension):
        npcInfo = NPCToons.NPCToonDict[npcId]
        dnaList = npcInfo[2]
        gender = npcInfo[3]
        if dnaList == 'r':
            dnaList = NPCToons.getRandomDNA(npcId, gender)
        dna = ToonDNA.ToonDNA()
        dna.newToonFromProperties(*dnaList)
        head = ToonHead.ToonHead()
        head.setupHead(dna, forGui=1)
        head.fitAndCenterHead(dimension, forGui=1)
        return head

    def __handleBack(self):
        doneStatus = {'mode': 'Back'}
        messenger.send(self.doneEvent, [doneStatus])