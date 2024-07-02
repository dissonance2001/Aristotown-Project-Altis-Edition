from panda3d.core import *
from panda3d.direct import *
from toontown.battle.BattleGlobals import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase.ToontownBattleGlobals import *
from direct.directnotify import DirectNotifyGlobal
import string
from toontown.toon import LaffMeter
from toontown.battle import BattleBase
from toontown.toonbase import ToontownBattleGlobals
from direct.gui.DirectGui import *
from panda3d.core import *
from panda3d.direct import *
from toontown.toonbase import TTLocalizer

class TownBattleToonPanel(DirectFrame):
    notify = DirectNotifyGlobal.directNotify.newCategory('TownBattleToonPanel')

    def __init__(self, id):
        if settings['newGui'] == True:
            gui = loader.loadModel('phase_3.5/models/gui/battle_gui_new')
        else:
            gui = loader.loadModel('phase_3.5/models/gui//battlegui/toon_panel')
        
        DirectFrame.__init__(self, relief=None, image=gui.find('**/toon_panel_frame'))
        self.setScale(0.5)
        self.initialiseoptions(TownBattleToonPanel)
        self.avatar = None
        self.sosText = DirectLabel(parent=self, relief=None, pos=(0.22, 0, 0.03), text=TTLocalizer.TownBattleToonSOS, text_fg=(0.176, 1, 0, 1), text_scale=0.1, text_font=getSignFont())
        self.sosText.hide()
        self.fireText = DirectLabel(parent=self, relief=None, pos=(0.22, 0, 0.03), text=TTLocalizer.TownBattleToonFire, text_fg=(1, 0, 0, 1), text_scale=0.1, text_font=getSignFont())
        self.fireText.hide()
        self.roundsText = DirectLabel(parent=self, relief=None, pos=(-0.2, -0.2, 0.1), text='', text_scale=0.08, text_fg=(0.176, 1, 0, 1), text_font=getSignFont())
        self.roundsText.hide()
        self.damageText = DirectLabel(parent=self, relief=None, pos=(-0.2, -0.2, 0.1), text='', text_scale=0.08, text_fg=(1, 0, 0, 1), text_font=getSignFont())
        self.damageText.hide()
        self.selfHealText = DirectLabel(parent=self, relief=None, pos=(-0.2, -0.2, 0.05), text='', text_scale=0.06, text_fg=(0.176, 1, 0, 1), text_font=getSignFont())
        self.selfHealText.hide()
        self.exeDamageText = DirectLabel(parent=self, relief=None, pos=(-0.2, -0.2, 0.05), text='', text_scale=0.06, text_fg=(1, 0, 0, 1), text_font=getSignFont())
        self.exeDamageText.hide()
        self.soakedRoundsText = DirectLabel(parent=self, relief=None, pos=(-0.2, -0.2, 0.05), text='', text_scale=0.06, text_fg=(0.176, 1, 0, 1), text_font=getSignFont())
        self.soakedRoundsText.hide()
        self.soakedDamageText = DirectLabel(parent=self, relief=None, pos=(-0.2, -0.2, 0.05), text='', text_scale=0.06, text_fg=(1, 0, 0, 1), text_font=getSignFont())
        self.soakedDamageText.hide()
        self.knockbackText = DirectLabel(parent=self, relief=None, pos=(-0.2, -0.2, 0.05), text='', text_scale=0.06, text_fg=(1, 0, 0, 1), text_font=getSignFont())
        self.knockbackText.hide()
        self.undecidedText2 = DirectLabel(parent=self, relief=None, pos=(-0.2, -0.2, 0.075),
                                         text='CHOOSING...', text_scale=0.08, text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont())
        self.undecidedText = DirectLabel(parent=self, relief=None, pos=(0.22, 0.05, -0.03), text=TTLocalizer.TownBattleUndecided, text_scale=0.3, text_fg=(1, 1, 1, 1), text_font=getSignFont())
        self.passText = DirectLabel(parent=self, relief=None, pos=(0.2, 0, 0.03),
                                    text='', text_scale=0.1, text_fg=(1, 0, 0, 1), text_font=getSignFont())
        self.passText.hide()
        self.hpChangeEvent = None
        self.gagNode = self.attachNewNode('gag')
        self.gagNode.setScale(2.0)
        self.hasGag = 0
        passGui = gui.find('**/lock_locked')
        passGui.detachNode()
        self.passNode = self.attachNewNode('pass')
        self.passNode.setPos(0.22, 0, -0.0)
        passGui.setScale(0.2)
        passGui.reparentTo(self.passNode)
        self.passNode.hide()
        self.laffMeter = None
        self.whichText = DirectLabel(parent=self, text='', pos=(0.22, 0.1, -0.24), text_scale=0.1, text_font=getSignFont())
        self.hide()
        gui.removeNode()

    def setLaffMeter(self, avatar):
        self.notify.debug('setLaffMeter: new avatar %s' % avatar.doId)
        if self.avatar == avatar:
            messenger.send(self.avatar.uniqueName('hpChange'), [avatar.hp, avatar.maxHp, 1])
        else:
            if self.avatar:
                self.cleanupLaffMeter()
            self.avatar = avatar
            self.laffMeter = LaffMeter.LaffMeter(avatar.style, avatar.hp, avatar.maxHp)
            self.laffMeter.setAvatar(self.avatar)
            self.laffMeter.reparentTo(self)
            self.laffMeter.setPos(-0.2, 0.14, -0.1)
            self.laffMeter.setScale(0.1)
            self.laffMeter.start()

    def setHealthText(self, hp, maxHp, quietly = 0):
        self.healthText['text'] = TTLocalizer.TownBattleHealthText % {'hitPoints': hp,
         'maxHit': maxHp}

    def show(self):
        DirectFrame.show(self)
        if self.laffMeter:
            self.laffMeter.start()

    def hide(self):
        DirectFrame.hide(self)
        if self.laffMeter:
            self.laffMeter.stop()

    def updateLaffMeter(self, hp):
        if self.laffMeter:
            self.laffMeter.adjustFace(hp, self.avatar.maxHp)
        self.setHealthText(hp, maxHp)

    def setValues(self, index, track, level = None, numTargets = None, targetIndex = None, localNum = None):
        self.notify.debug('Toon Panel setValues: index=%s track=%s level=%s numTargets=%s targetIndex=%s localNum=%s' % (index,
         track,
         level,
         numTargets,
         targetIndex,
         localNum))
        self.undecidedText.hide()
        self.undecidedText2.hide()
        self.sosText.hide()
        self.fireText.hide()
        self.roundsText.hide()
        self.damageText.hide()
        self.exeDamageText.hide()
        self.soakedDamageText.hide()
        self.soakedRoundsText.hide()
        self.knockbackText.hide()
        self.selfHealText.hide()
        self.gagNode.hide()
        self.whichText.hide()
        self.passNode.hide()
        self.passText.hide()
        if self.hasGag:
            self.gag.removeNode()
            self.hasGag = 0
        if track == BattleBase.NO_ATTACK or track == BattleBase.UN_ATTACK:
            self.undecidedText.show()
            self.undecidedText2.show()
        elif track == BattleBase.PASS_ATTACK:
            self.passText.show()
            self.passText['text'] = 'PASS'
        elif track == BattleBase.FIRE:
            self.fireText.show()
            self.whichText.show()
            self.whichText['text'] = self.determineWhichText(numTargets, targetIndex, localNum, index, track)
        elif track == BattleBase.SOS or track == BattleBase.NPCSOS or track == BattleBase.PETSOS:
            self.sosText.show()
        elif track >= MIN_TRACK_INDEX and track <= MAX_TRACK_INDEX:
            self.undecidedText.hide()
            self.passText.hide()
            self.gagNode.show()
            invButton = base.localAvatar.inventory.buttonLookup(track, level)
            self.gag = invButton.instanceUnderNode(self.gagNode, 'gag')
            self.gag.setScale(0.8)
            self.gag.setPos(0.105, -0.2, 0.035)
            if self.avatar.trackBonusLevel[track] >= 1:
                self.gag.setColor(0.6, 0.6, 1.0, 1)
            else:
                self.gag.setColor(1, 1, 1, 1)
            self.hasGag = 1
            allGagBoost = False
            if 'allGagBoost' in base.localAvatar.battleConditions:
                allGagBoost = True
            damage = int(getAvPropDamage(track, level, self.avatar.experience.getExp(track)))
            lureValue = int(
                ((ToontownBattleGlobals.AvLureKnockback[level] * 100) / 2))
            if track == HEAL_TRACK and 'healBoost' in base.localAvatar.battleConditions:
                damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['healBoost'][0] * 0.01) + 1.0)))
            elif track == TRAP_TRACK and 'trapBoost' in base.localAvatar.battleConditions:
                damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['trapBoost'][0] * 0.01) + 1.0)))
            elif track == LURE_TRACK and 'lureBoost' in base.localAvatar.battleConditions:
                damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['lureBoost'][0] * 0.01) + 1.0)))
                lureValue = int(
                    ((ToontownBattleGlobals.AvLureKnockback[level] * 100) +
                     base.localAvatar.battleConditions['lureBoost'][
                         0]) / 2)
            elif track == SOUND_TRACK and 'soundBoost' in base.localAvatar.battleConditions:
                damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['soundBoost'][0] * 0.01) + 1.0)))
            elif track == THROW_TRACK and 'throwBoost' in base.localAvatar.battleConditions:
                damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['throwBoost'][0] * 0.01) + 1.0)))
            elif track == SQUIRT_TRACK and 'squirtBoost' in base.localAvatar.battleConditions:
                damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['squirtBoost'][0] * 0.01) + 1.0)))
            elif track == ZAP_TRACK and 'zapBoost' in base.localAvatar.battleConditions:
                damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['zapBoost'][0] * 0.01) + 1.0)))
            elif track == DROP_TRACK and 'dropBoost' in base.localAvatar.battleConditions:
                damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['dropBoost'][0] * 0.01) + 1.0)))
            if allGagBoost:
                damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['allGagBoost'][0] * 0.01) + 1.0)))
                lureValue = int(
                    ((ToontownBattleGlobals.AvLureKnockback[level] * 100) +
                     base.localAvatar.battleConditions['allGagBoost'][
                         0]) / 2)
            if numTargets is not None and targetIndex is not None and localNum is not None:
                self.whichText.show()
                self.whichText['text'] = self.determineWhichText(numTargets, targetIndex, localNum, index, track)
            if track == LURE_TRACK:
                self.roundsText.show()
                self.roundsText['text'] = 'Rounds: ' + str(NumRoundsLured[level] + 1)
                self.knockbackText.show()
                self.knockbackText['text'] = 'Knockback: ' + str(lureValue)+'%'
            if track == HEAL_TRACK:
                self.damageText.show()
                self.damageText['text'] = 'Heals: ' + str(damage)
                self.selfHealText.show()
                self.selfHealText['text'] = 'Self Heal: ' + str(damage / 2.5)
                self.selfHealText.setColor(0.176, 1, 0, 1)
            if track == TRAP_TRACK:
                self.damageText.show()
                self.damageText['text'] = 'Damage: ' + str(damage)
                self.exeDamageText.show()
                self.exeDamageText['text'] = 'Exe./Gov.: ' + str(damage * 1.3)
            if track == SOUND_TRACK:
                self.damageText.show()
                self.damageText['text'] = 'Damage: ' + str(damage)
            if track == THROW_TRACK:
                self.damageText.show()
                self.damageText['text'] = 'Damage: ' + str(damage)
                self.selfHealText.show()
                self.selfHealText['text'] = 'Self Heal: ' + str(damage/5)
            if track == DROP_TRACK:
                self.damageText.show()
                self.damageText['text'] = 'Damage: ' + str(damage)
            if track == SQUIRT_TRACK:
                self.damageText.show()
                self.damageText['text'] = 'Damage: ' + str(damage)
                self.soakedRoundsText.show()
                self.soakedRoundsText['text'] = 'Rounds: ' + str(ToontownBattleGlobals.AvSoakRounds[level])
            if track == ZAP_TRACK:
                self.damageText.show()
                self.damageText['text'] = 'Damage: ' + str(damage)
                self.soakedDamageText.show()
                self.soakedDamageText['text'] = 'If Soaked: ' + str(damage * 3)
        else:
            self.notify.error('Bad track value: %s' % track)

    def determineWhichText(self, numTargets, targetIndex, localNum, index, track):
        returnStr = ''
        targetList = range(numTargets)
        targetList.reverse()
        try:
            if self.avatar.trackBonusLevel[track] >= 1:
                marker = 'O'
            else:
                marker = 'X'
        except:
            marker = 'X'
        for i in targetList:
            if targetIndex == -1:
                returnStr += marker
            elif targetIndex == -2:
                if i == index:
                    returnStr += '-'
                else:
                    returnStr += marker
            elif targetIndex >= 0 and targetIndex <= 5:
                if i == targetIndex:
                    returnStr += marker
                else:
                    returnStr += '-'
            else:
                self.notify.error('Bad target index: %s' % targetIndex)

        return returnStr

    def cleanup(self):
        self.ignoreAll()
        self.cleanupLaffMeter()
        if self.hasGag:
            self.gag.removeNode()
            del self.gag
        self.gagNode.removeNode()
        del self.gagNode
        DirectFrame.destroy(self)

    def cleanupLaffMeter(self):
        self.notify.debug('Cleaning up laffmeter!')
        self.ignore(self.hpChangeEvent)
        if self.laffMeter:
            self.laffMeter.destroy()
            self.laffMeter = None