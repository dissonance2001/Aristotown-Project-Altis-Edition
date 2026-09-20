import math
import random

from panda3d.core import TextEncoder, TextNode, Vec4
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *

from toontown.clashbattle.battle import BattleGlobals, Fanfare
from toontown.coghq import CogDisguiseGlobals
from toontown.gui.ScaledFrame import ScaledFrame
from toontown.quest3.base.Quester import Quester
from toontown.quest3.base.QuestReference import QuestReference
from toontown.quest3.gui.Quest3Poster import QuestPoster
from toontown.shtiker import DisguisePage
from toontown.clashsuit.suit import SuitDNA
from toontown.toonbase import ToontownGlobals, TTLocalizer
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class RewardPanel(ScaledFrame):
    SkipBattleMovieEvent = 'skip-battle-movie-event'
    BAR_TIME = 0.5

    QUEST_POSTER_POS = (
        (-0.3, 0, 0.05, 0, 0, 0),
        (0.3, 0, 0.05, 0, 0, 0),
        (-0.3, 0, -0.28, 0, 0, 0),
        (0.3, 0, -0.28, 0, 0, 0)
    )

    def __init__(self, name: str) -> None:
        self.notify.debug('Initializing!')
        super().__init__(
            parent=aspect2d,
            relief=None,
            pos=(0, 0, 0.54),
            frameSize=(-1/2 * 1.75, 1/2 * 1.75, -1/2 * 0.9, 1/2 * 0.75),
            popIn=True,
        )
        self.initialiseoptions(RewardPanel)
        self['shadowStrength'] = 0.04

        self.trackLabels = []
        self.trackIncLabels = []
        self.trackBars = []
        self.trackBarsOffset = 0
        self.meritLabels = []
        self.meritIncLabels = []
        self.meritBars = []

        self.load(name)

    def load(self, name: str) -> None:
        # Create our frames.
        self.frame_gagExp = self.createcomponent(
            "Frame0", (), "frame", DirectFrame,
            parent=self, relief=None, pos=(-0.32, 0, 0.24),
        )
        self.frame_items = self.createcomponent(
            "Frame1", (), "frame", DirectFrame,
            parent=self, relief=None, text=TTLocalizer.RewardPanelItems,
            text_pos=(0, 0.2), text_scale=0.08
        )
        self.frame_cogParts = self.createcomponent(
            "Frame2", (), "frame", DirectFrame,
            parent=self, relief=None, text=TTLocalizer.RewardPanelCogPart,
            text_pos=(0, 0.2), text_scale=0.08
        )
        self.frame_quests = self.createcomponent(
            "Frame3", (), "frame", DirectFrame,
            parent=self, relief=None, text=TTLocalizer.RewardPanelToonTasks,
            text_pos=(0, 0.25), text_scale=0.06
        )
        self.frame_newGag = self.createcomponent(
            "Frame4", (), "frame", DirectFrame,
            parent=self, relief=None, pos=(0, 0, 0.24), text='', text_wordwrap=14.4,
            text_pos=(0, -0.46), text_scale=0.06,
        )
        self.frame_endTrack = self.createcomponent(
            "Frame5", (), "frame", DirectFrame,
            parent=self, relief=None, pos=(0, 0, 0.24), text='', text_wordwrap=14.4,
            text_pos=(0, -0.46), text_scale=0.06
        )
        self.frame_promotion = self.createcomponent(
            "Frame6", (), "frame", DirectFrame,
            parent=self, relief=None, pos=(0, 0, 0.24), text='', text_wordwrap=14.4,
            text_pos=(0, -0.46), text_scale=0.06
        )

        # Create our labels.
        self.label_avName = self.createcomponent(
            "Label0", (), "label", DirectLabel,
            parent=self, relief=None, pos=(0, 0, 0.315), text=name, text_scale=0.08,
        )
        self.label_multiplier = self.createcomponent(
            "Label2", (), "label", DirectLabel,
            parent=self, relief=None, pos=(-0.7, 0, 0.2), hpr=(0, 0, -30), text='', text_scale=0.06
        )
        self.label_items = self.createcomponent(
            "Label3", (), "label", DirectLabel,
            parent=self.frame_items, text='', text_scale=0.06
        )
        self.label_cogParts = self.createcomponent(
            "Label4", (), "label", DirectLabel,
            parent=self.frame_cogParts, text='', text_scale=0.06
        )
        self.label_congratsLeft = self.createcomponent(
            "Label5", (), "label", DirectLabel,
            parent=self.frame_newGag, pos=(-0.2, 0, -0.1), text='', text_pos=(0, 0), text_scale=0.06
        )
        self.label_congratsLeft.setHpr(0, 0, -30)
        self.label_congratsRight = self.createcomponent(
            "Label6", (), "label", DirectLabel,
            parent=self.frame_newGag, pos=(0.2, 0, -0.1), text='', text_pos=(0, 0), text_scale=0.06
        )
        self.label_congratsRight.setHpr(0, 0, 30)

        # Create the quest posters.
        self.notify.debug("Setting Quests Labels!")
        self.questPosters = []
        for i in range(ToontownGlobals.MaxQuestCarryLimit):
            questPoster = QuestPoster(parent=self.frame_quests)
            questPoster.setPosHpr(*self.QUEST_POSTER_POS[i])
            questPoster.setScale(0.6)
            questPoster.setMapIndex(i + 1)
            questPoster.reverseBG(reverse=i % 2)
            self.questPosters.append(questPoster)

        self.notify.debug("Setting Merit Labels!")
        for i in range(len(SuitDNA.suitDepts)):
            deptName = TextEncoder.upper(SuitDNA.suitDeptFullnames[SuitDNA.suitDepts[i]])
            self.meritLabels.append(self.createcomponent(
                f"Label{100 + i}", (), "label", DirectLabel,
                parent=self.frame_gagExp,
                relief=None,
                text=deptName,
                text_scale=0.05,
                text_align=TextNode.ARight,
                pos=(TTLocalizer.RPmeritLabelPosX, 0, -0.09 * i - 0.125),
                text_pos=(0, -0.02),
            ))

            self.meritIncLabels.append(self.createcomponent(
                f"Label{200 + i}", (), "label", DirectLabel,
                parent=self.frame_gagExp,
                relief=None,
                text="",
                text_scale=0.05,
                text_align=TextNode.ALeft,
                pos=(0.7, 0, -0.09 * i - 0.125),
                text_pos=(0, -0.02),
            ))

            self.meritBars.append(self.createcomponent(
                f"WaitBar{i}", (), "waitbar", DirectWaitBar,
                parent=self.frame_gagExp,
                relief=DGG.SUNKEN,
                frameSize=(-1, 1, -0.15, 0.15),
                borderWidth=(0.02, 0.02),
                scale=0.25,
                frameColor=(
                    DisguisePage.DeptColors[i][0] * 0.7,
                    DisguisePage.DeptColors[i][1] * 0.7,
                    DisguisePage.DeptColors[i][2] * 0.7,
                    1,
                ),
                barColor=(
                    DisguisePage.DeptColors[i][0],
                    DisguisePage.DeptColors[i][1],
                    DisguisePage.DeptColors[i][2],
                    1,
                ),
                text="0/0 " + TTLocalizer.RewardPanelMeritBarLabels[i],
                text_scale=TTLocalizer.RPmeritBarLabels,
                text_fg=(0, 0, 0, 1),
                text_align=TextNode.ALeft,
                text_pos=(-0.96, -0.05),
                pos=(TTLocalizer.RPmeritBarsPosX, 0, -0.09 * i - 0.125),
            ))

        self.notify.debug("Setting Track Labels!")
        for track in BattleGlobals.ATTACK_TRACKS:
            if track in BattleGlobals.GAG_TRACK_ORDER:
                i = BattleGlobals.GAG_TRACK_ORDER.index(track)
            else:
                i = track
            trackName = TextEncoder.upper(BattleGlobals.Tracks[track])
            self.trackLabels.append(self.createcomponent(
                f"Label{400 + i}", (), "label", DirectLabel,
                parent=self.frame_gagExp,
                relief=None,
                text=trackName,
                text_scale=TTLocalizer.RPtrackLabels,
                text_align=TextNode.ARight,
                pos=(0.13, 0, -0.09 * i),
                text_pos=(0, -0.02),
            ))

            self.trackIncLabels.append(self.createcomponent(
                f"Label{500 + i}", (), "label", DirectLabel,
                parent=self.frame_gagExp,
                relief=None,
                text='',
                text_scale=0.05,
                text_align=TextNode.ALeft,
                pos=(0.65, 0, -0.09 * i),
                text_pos=(0, -0.02)
            ))

            self.trackBars.append(self.createcomponent(
                f"WaitBar{100 + i}", (), "waitbar", DirectWaitBar,
                parent=self.frame_gagExp,
                relief=DGG.SUNKEN,
                frameSize=(-1, 1, -0.15, 0.15),
                borderWidth=(0.02, 0.02),
                scale=0.25,
                frameColor=(
                    BattleGlobals.TrackColors[track][0] * 0.7,
                    BattleGlobals.TrackColors[track][1] * 0.7,
                    BattleGlobals.TrackColors[track][2] * 0.7,
                    1,
                ),
                barColor=(
                    BattleGlobals.TrackColors[track][0],
                    BattleGlobals.TrackColors[track][1],
                    BattleGlobals.TrackColors[track][2],
                    1,
                ),
                text="0/0",
                text_scale=0.18,
                text_fg=(0, 0, 0, 1),
                text_align=TextNode.ACenter,
                text_pos=(0, -0.05),
                pos=(0.4, 0, -0.09 * i),
            ))

        self.notify.debug("Setting Battle GUI!")
        battleGui = loader.loadModel("phase_3.5/models/gui/battlegui/skip_button")
        self.skipButton = self.createcomponent(
            "Button0", (), "button", DirectButton,
            parent=self,
            relief=None,
            image=(
                battleGui.find("**/skipSectionUp"),
                battleGui.find("**/skipSectionDown"),
                battleGui.find("**/skipSectionRollOver"),
                battleGui.find("**/skipSectionDisabled"),
            ),
            pos=(0.815, 0, -0.395),
            scale=(0.39, 1.0, 0.39),
            text=("", TTLocalizer.RewardPanelSkip, TTLocalizer.RewardPanelSkip, ""),
            text_scale=TTLocalizer.RPskipScale,
            text_fg=Vec4(1, 1, 1, 1),
            text_shadow=Vec4(0, 0, 0, 1),
            text_pos=TTLocalizer.RPskipPos,
            textMayChange=0,
            command=self._handleSkip,
        )
        battleGui.removeNode()
        self.notify.debug("Initialization done!")

    def getNextExpValue(self, curSkill, trackIndex):
        retVal = BattleGlobals.regMaxSkill
        for amount in BattleGlobals.Levels[trackIndex]:
            if curSkill < amount:
                retVal = amount
                return retVal

        return retVal

    def initCogPartFrame(self):
        self.notify.debug('Initializing Cog Part Frame!')
        self.frame_endTrack.hide()
        self.frame_gagExp.hide()
        self.frame_newGag.hide()
        self.label_multiplier.hide()
        self.frame_promotion.hide()
        self.frame_quests.hide()
        self.frame_items.hide()
        self.frame_cogParts.show()
        self.label_cogParts['text'] = ''

    def initQuestFrame(self, originalQuests):
        self.notify.debug('Initializing Quest Frame!')
        self.frame_endTrack.hide()
        self.frame_gagExp.hide()
        self.label_multiplier.hide()
        self.frame_newGag.hide()
        self.frame_promotion.hide()
        self.frame_quests.show()
        self.frame_items.hide()
        self.frame_cogParts.hide()

        for i, questPoster in enumerate(self.questPosters):
            questPoster.show()
            if i < len(originalQuests):
                questReference = QuestReference.fromStruct(originalQuests[i])
                questPoster.setQuestReference(questReference)
            else:
                questPoster.setQuestReference(None)

    def initGagFrame(self, toon, expList, meritList, noSkip = False):
        self.notify.debug('Initializing Gag Frame!')
        self.label_avName['text'] = toon.getName()
        self.frame_endTrack.hide()
        self.frame_gagExp.show()
        self.label_multiplier.show()
        self.frame_newGag.hide()
        self.frame_promotion.hide()
        self.frame_quests.hide()
        self.frame_items.hide()
        self.frame_cogParts.hide()
        trackBarOffset = 0
        self.skipButton['state'] = DGG.DISABLED if noSkip else DGG.NORMAL
        for i in range(len(SuitDNA.suitDepts)):
            meritBar = self.meritBars[i]
            meritLabel = self.meritLabels[i]
            totalMerits = CogDisguiseGlobals.getTotalMerits(toon, i)
            reviveLevel = toon.getCogReviveLevels()[i]
            merits = meritList[i]
            self.meritIncLabels[i].hide()
            if toon.cogParts[i] != 0:
                if not self.trackBarsOffset:
                    trackBarOffset = 0.47
                    self.trackBarsOffset = 1
                meritBar.show()
                meritLabel.show()
                if CogDisguiseGlobals.isSuitComplete(toon.cogParts, i):
                    if totalMerits and reviveLevel < 0:
                        meritBar['range'] = totalMerits
                        meritBar['value'] = merits
                        if merits == totalMerits:
                            meritBar['text'] = TTLocalizer.RewardPanelMeritAlert
                        else:
                            meritBar['text'] = '%s/%s %s' % (merits, totalMerits, TTLocalizer.RewardPanelMeritBarLabels[i])
                    else:
                        meritBar['range'] = 1
                        meritBar['value'] = 1
                        meritBarText = TTLocalizer.RewardPanelMeritsMaxed
                        if reviveLevel >= 0:
                            # If they have access to suit switching, they are fully maxed
                            if toon.suitSwitching[i] > -1:
                                meritBarText = TTLocalizer.RewardPanelMeritsMaxed + TTLocalizer.AvatarSuitPanelExecutive
                            else:
                                meritBarText += ' (' + TTLocalizer.DisguisePageCogLevel % (reviveLevel + 1) + TTLocalizer.AvatarSuitPanelExecutive + ')'
                        meritBar['text'] = meritBarText
                else:
                    meritBar['range'] = CogDisguiseGlobals.PartsPerSuit[i]
                    meritBar['value'] = CogDisguiseGlobals.getTotalParts(toon.cogParts[i])
                    meritBar['text'] = '%s/%s %s' % (CogDisguiseGlobals.getTotalParts(toon.cogParts[i]), CogDisguiseGlobals.PartsPerSuit[i], TTLocalizer.RewardPanelParts)
                self.resetMeritBarColor(i)
            else:
                meritBar.hide()
                meritLabel.hide()

        for i in range(len(expList)):
            curExp = expList[i]
            trackBar = self.trackBars[i]
            trackLabel = self.trackLabels[i]
            trackIncLabel = self.trackIncLabels[i]
            trackBar.setX(trackBar.getX() - trackBarOffset)
            trackLabel.setX(trackLabel.getX() - trackBarOffset)
            trackIncLabel.setX(trackIncLabel.getX() - trackBarOffset)
            trackIncLabel.hide()
            if toon.hasTrackAccess(i):
                trackBar.show()
                if curExp >= BattleGlobals.regMaxSkill:
                    trackBar['range'] = BattleGlobals.regMaxSkill
                    # uberCurrExp = curExp - BattleGlobals.regMaxSkill
                    trackBar['value'] = BattleGlobals.regMaxSkill
                    trackBar['text'] = TTLocalizer.RewardPanelMeritsMaxed
                else:
                    nextExp = self.getNextExpValue(curExp, i)
                    trackBar['range'] = nextExp
                    trackBar['value'] = curExp
                    trackBar['text'] = '%s/%s' % (curExp, nextExp)
                self.resetBarColor(i)
            else:
                trackBar.hide()

    def incrementExp(self, track, newValue, toon):
        self.notify.debug('incrementExp() was called!')
        trackBar = self.trackBars[track]
        oldValue = trackBar['value']
        newValue = min(BattleGlobals.MaxSkill, newValue)
        nextExp = self.getNextExpValue(newValue, track)
        if newValue >= BattleGlobals.regMaxSkill:
            newValue = BattleGlobals.regMaxSkill
            nextExp = BattleGlobals.regMaxSkill
            trackBar['text'] = TTLocalizer.RewardPanelMeritsMaxed
        else:
            trackBar['text'] = '%s/%s' % (newValue, nextExp)
        trackBar['range'] = nextExp
        trackBar['value'] = newValue
        trackBar['barColor'] = (BattleGlobals.TrackColors[track][0],
         BattleGlobals.TrackColors[track][1],
         BattleGlobals.TrackColors[track][2], 1)

    def resetBarColor(self, track):
        self.notify.debug('Resetting Bar Color for %s!' % str(track))
        self.trackBars[track]['barColor'] = (BattleGlobals.TrackColors[track][0] * 0.8,
         BattleGlobals.TrackColors[track][1] * 0.8,
         BattleGlobals.TrackColors[track][2] * 0.8, 1)

    def incrementMerits(self, toon, dept, newValue, totalMerits):
        meritBar = self.meritBars[dept]
        # oldValue = meritBar['value']
        if totalMerits:
            newValue = min(totalMerits, newValue)
            meritBar['range'] = totalMerits
            meritBar['value'] = newValue
            if newValue == totalMerits:
                meritBar['text'] = TTLocalizer.RewardPanelMeritAlert
                meritBar['barColor'] = (DisguisePage.DeptColors[dept][0],
                 DisguisePage.DeptColors[dept][1],
                 DisguisePage.DeptColors[dept][2],
                 1)
            else:
                meritBar['text'] = '%s/%s %s' % (newValue, totalMerits, TTLocalizer.RewardPanelMeritBarLabels[dept])

    def resetMeritBarColor(self, dept):
        self.meritBars[dept]['barColor'] = (DisguisePage.DeptColors[dept][0] * 0.8,
         DisguisePage.DeptColors[dept][1] * 0.8,
         DisguisePage.DeptColors[dept][2] * 0.8,
         1)

    def getRandomCongratsPair(self, toon):
        congratsStrings = TTLocalizer.RewardPanelCongratsStrings
        numStrings = len(congratsStrings)
        indexList = list(range(numStrings))
        index1 = random.choice(indexList)
        indexList.remove(index1)
        index2 = random.choice(indexList)
        string1 = congratsStrings[index1]
        string2 = congratsStrings[index2]
        return (string1, string2)

    def newGag(self, toon, track, level):
        self.frame_endTrack.hide()
        self.frame_gagExp.hide()
        self.frame_newGag.show()
        self.frame_promotion.hide()
        self.frame_quests.hide()
        self.frame_items.hide()
        self.frame_newGag['text'] = TTLocalizer.RewardPanelNewGag % {'gagName': BattleGlobals.Tracks[track].capitalize(),
         'avName': toon.getName()}
        self.label_congratsLeft['text'] = ''
        self.label_congratsRight['text'] = ''
        gagOriginal = base.localAvatar.inventory.buttonLookup(track, level)
        self.newGagIcon = gagOriginal.copyTo(self.frame_newGag)
        self.newGagIcon.setPos(0, 0, -0.25)
        self.newGagIcon.setScale(1.5)

    def cleanupNewGag(self):
        self.frame_endTrack.hide()
        if self.newGagIcon:
            self.newGagIcon.removeNode()
            self.newGagIcon = None

        self.frame_gagExp.show()
        self.frame_newGag.hide()
        self.frame_promotion.hide()
        self.frame_quests.hide()
        self.frame_items.hide()

    def getNewGagIntervalList(self, toon, track, level):
        leftCongratsAnticipate = 1.0
        rightCongratsAnticipate = 1.0
        finalDelay = 1.5
        leftString, rightString = self.getRandomCongratsPair(toon)
        intervalList = [Func(self.newGag, toon, track, level),
            Wait(leftCongratsAnticipate),
            Func(self.label_congratsLeft.setProp, 'text', leftString),
            Wait(rightCongratsAnticipate),
            Func(self.label_congratsRight.setProp, 'text', rightString),
            Wait(finalDelay),
            Func(self.cleanupNewGag)]

        return intervalList

    def vanishFrames(self):
        self.hide()
        self.frame_endTrack.hide()
        self.frame_gagExp.hide()
        self.frame_newGag.hide()
        self.frame_promotion.hide()
        self.frame_quests.hide()
        self.frame_items.hide()
        self.frame_cogParts.hide()

    def endTrack(self, toon, toonList, track):
        for t in toonList:
            if t == base.localAvatar:
                self.show()

        self.frame_endTrack.show()
        self.frame_endTrack['text'] = TTLocalizer.RewardPanelEndTrack % {'gagName': BattleGlobals.Tracks[track].capitalize(),
            'avName': toon.getName()}
        gagLast = base.localAvatar.inventory.buttonLookup(track, BattleGlobals.MAX_LEVEL_INDEX)
        self.gagIcon = gagLast.copyTo(self.frame_endTrack)
        self.gagIcon.setPos(0, 0, -0.25)
        self.gagIcon.setScale(1.5)

    def cleanIcon(self):
        self.gagIcon.removeNode()
        self.gagIcon = None

    def cleanupEndTrack(self):
        self.frame_endTrack.hide()
        self.frame_gagExp.show()
        self.frame_newGag.hide()
        self.frame_promotion.hide()
        self.frame_quests.hide()
        self.frame_items.hide()

    def getEndTrackIntervalList(self, toon, toonList, track):
        intervalList = [Func(self.endTrack, toon, toonList, track), Wait(2.0), Func(self.cleanIcon)]
        return intervalList

    def showTrackIncLabel(self, track, earnedSkill, guestWaste = 0):
        if guestWaste:
            self.trackIncLabels[track]['text'] = ''
        elif earnedSkill > 0:
            self.trackIncLabels[track]['text'] = '+ ' + str(earnedSkill)
        elif earnedSkill < 0:
            self.trackIncLabels[track]['text'] = ' ' + str(earnedSkill)
        self.trackIncLabels[track].show()

    def showMeritIncLabel(self, dept, earnedMerits):
        self.meritIncLabels[dept]['text'] = '+ ' + str(earnedMerits)
        self.meritIncLabels[dept].show()

    def getTrackIntervalList(self, toon, track, origSkill, earnedSkill):
        self.notify.debug("getTrackIntervalList() was called!")
        tickDelay = 1.0 / 60
        intervalList = []
        intervalList.append(Func(self.showTrackIncLabel, track, earnedSkill))
        numTicks = int(math.ceil(self.BAR_TIME / tickDelay))
        for i in range(numTicks):
            t = (i + 1) / float(numTicks)
            newValue = int(origSkill + t * earnedSkill + 0.5)
            intervalList.append(Func(self.incrementExp, track, newValue, toon))
            intervalList.append(Wait(tickDelay))

        intervalList.append(Func(self.resetBarColor, track))
        intervalList.append(Wait(0.1))
        nextExpValue = self.getNextExpValue(origSkill, track)
        finalGagFlag = 0
        while origSkill + earnedSkill >= nextExpValue and origSkill < nextExpValue and not finalGagFlag:
            if nextExpValue != BattleGlobals.MaxSkill:
                intervalList += self.getNewGagIntervalList(toon, track, BattleGlobals.Levels[track].index(nextExpValue))
            newNextExpValue = self.getNextExpValue(nextExpValue, track)
            if newNextExpValue == nextExpValue:
                finalGagFlag = 1
            else:
                nextExpValue = newNextExpValue

        return intervalList

    def getMeritIntervalList(self, toon, dept, origMerits, earnedMerits):
        self.notify.debug("getMeritIntervalList() was called!")
        tickDelay = 1.0 / 60
        intervalList = []
        totalMerits = CogDisguiseGlobals.getTotalMerits(toon, dept)
        if toon.cogReviveLevels[dept] >= 0: # No merits for maxed suits
            totalMerits = 0
        neededMerits = 0
        if totalMerits and origMerits != totalMerits:
            neededMerits = totalMerits - origMerits
            intervalList.append(Func(self.showMeritIncLabel, dept, min(neededMerits, earnedMerits)))
        numTicks = int(math.ceil(self.BAR_TIME / tickDelay))
        for i in range(numTicks):
            t = (i + 1) / float(numTicks)
            newValue = int(origMerits + t * earnedMerits + 0.5)
            intervalList.append(Func(self.incrementMerits, toon, dept, newValue, totalMerits))
            intervalList.append(Wait(tickDelay))

        intervalList.append(Func(self.resetMeritBarColor, dept))
        intervalList.append(Wait(0.1))
        if toon.cogLevels[dept] < ToontownGlobals.MaxCogSuitLevel:
            if neededMerits and toon.readyForPromotion(dept):
                intervalList.append(Wait(0.4))
                intervalList += self.getPromotionIntervalList(toon, dept)
        return intervalList

    def promotion(self, toon, dept):
        self.frame_endTrack.hide()
        self.frame_gagExp.hide()
        self.frame_newGag.hide()
        self.frame_promotion.show()
        self.frame_quests.hide()
        self.frame_items.hide()
        name = SuitDNA.suitDepts[dept]
        self.frame_promotion['text'] = TTLocalizer.RewardPanelPromotion % SuitDNA.suitDeptFullnames[name]
        icons = loader.loadModel('phase_3/models/gui/cog_icons')
        if dept == 0:
            self.deptIcon = icons.find('**/BoardIcon').copyTo(self.frame_promotion)
        elif dept == 1:
            self.deptIcon = icons.find('**/CorpIcon').copyTo(self.frame_promotion)
        elif dept == 2:
            self.deptIcon = icons.find('**/LegalIcon').copyTo(self.frame_promotion)
        elif dept == 3:
            self.deptIcon = icons.find('**/MoneyIcon').copyTo(self.frame_promotion)
        elif dept == 4:
            self.deptIcon = icons.find('**/SalesIcon').copyTo(self.frame_promotion)
        icons.removeNode()
        self.deptIcon.setPos(0, 0, -0.225)
        self.deptIcon.setScale(0.33)

    def cleanupPromotion(self):
        if not hasattr(self, 'deptIcon'):
            return
        self.deptIcon.removeNode()
        self.deptIcon = None
        self.frame_endTrack.hide()
        self.frame_gagExp.show()
        self.frame_newGag.hide()
        self.frame_promotion.hide()
        self.frame_quests.hide()
        self.frame_items.hide()
        return

    def getPromotionIntervalList(self, toon, dept):
        finalDelay = 2.0
        intervalList = [Func(self.promotion, toon, dept), Wait(finalDelay), Func(self.cleanupPromotion)]
        return intervalList

    def getQuestIntervalList(self, toon: Quester, originalQuests, updatedQuests):
        """Creates an interval list by determining the progress of the
        toon's current quests, which is achieved by hashing their objectives
        with any updated/completed quests that may have been sent to the client.

        :param toon: The quester object.
        :param originalQuests: A list of quest references sent by the server which
        represents their quests prior to being updated by BattleExperienceAI.assignRewards().
        :param updatedQuests: A list of QuestReference structs representing their quests
        after having been updated by BattleExperience.assignRewards().
        """
        self.notify.debug("getQuestIntervalList() was called!")
        intervalList = []

        for i, questPoster in enumerate(self.questPosters):
            if i < len(originalQuests):
                questReference = QuestReference.fromStruct(originalQuests[i])
                questPoster.setQuestReference(questReference)
            else:
                questPoster.setQuestReference(None)

        for i, updatedQr in enumerate(updatedQuests):
            updatedQuest = QuestReference.fromStruct(updatedQr)
            if not self.questPosters[i].questReference:
                continue
            interval = self.questPosters[i].getProgressInterval(updatedQuest, toon)
            if interval:
                intervalList.append(interval)

        return intervalList

    def getCogPartIntervalList(self, toon, cogPartList):
        itemName = CogDisguiseGlobals.getPartName(cogPartList)
        intervalList = []
        if intervalList:
            intervalList.append(Func(self.label_cogParts.setProp, 'text', itemName))
            intervalList.append(Wait(1))
        return intervalList

    def getExpTrack(self, toon, origExp, earnedExp, originalQuests,
                    origMeritList, meritList, partList, toonList,
                    updatedQuests, noSkip = False):
        self.notify.debug("getExpTrack() was called!")
        self.notify.debug("earnedExp = %s" % str(earnedExp))
        self.notify.debug("meritList = %s" % str(meritList))
        expTrack = Sequence(Func(self.initGagFrame, toon, origExp, origMeritList, noSkip=noSkip), Wait(1.0))
        endTracks = [0, 0, 0, 0, 0, 0, 0, 0]
        trackEnded = 0
        self.notify.debug("Appending Track Interval Lists!")
        for track in BattleGlobals.GAG_TRACK_ORDER:
            if track in BattleGlobals.ATTACK_TRACKS:
                trackIndex = BattleGlobals.ATTACK_TRACKS.index(track)
            else:
                trackIndex = track
            if earnedExp[trackIndex] > 0:
                expTrack += self.getTrackIntervalList(toon, trackIndex, origExp[trackIndex], earnedExp[trackIndex])
                maxExp = BattleGlobals.MaxSkill
                if origExp[trackIndex] < maxExp and earnedExp[trackIndex] + origExp[trackIndex] >= maxExp:
                    endTracks[trackIndex] = 1
                    trackEnded = 1

        self.notify.debug("Appending Merit Interval Lists!")
        numDepts = len(SuitDNA.suitDepts)
        for dept in reversed(range(numDepts)):
            if meritList[dept]:
                expTrack += self.getMeritIntervalList(toon, dept, origMeritList[dept], meritList[dept])

        expTrack.append(Wait(0.75))
        self.notify.debug('partList = %s' % partList)
        newPart = 0
        for part in partList:
            if part != 0:
                newPart = 1
                break

        if newPart:
            partList = self.getCogPartIntervalList(toon, partList)
            if partList:
                expTrack.append(Func(self.initCogPartFrame))
                expTrack.append(Wait(0.25))
                expTrack += partList
                expTrack.append(Wait(0.5))
        questList = self.getQuestIntervalList(
            toon, originalQuests, updatedQuests)
        if questList:
            expTrack.append(Func(self.initQuestFrame, originalQuests))
            expTrack.append(Wait(0.25))
            delay = 0.0
            questTrack = Parallel()
            for questInterval in questList:
                questTrack.append(Sequence(Wait(delay), questInterval))
                delay += 0.25
            expTrack.append(questTrack)
        expTrack.append(Wait(0.25))
        if trackEnded:
            expTrack.append(Func(self.vanishFrames))
            expTrack.append(Fanfare.makeFanfare(0, toon)[0])
            for i in range(len(endTracks)):
                if endTracks[i] == 1:
                    expTrack += self.getEndTrackIntervalList(toon, toonList, i)

            expTrack.append(Func(self.cleanupEndTrack))
        return expTrack

    def _handleSkip(self):
        messenger.send(self.SkipBattleMovieEvent)
