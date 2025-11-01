from direct.actor.DistributedActor import DistributedActor
from direct.distributed import DistributedNode
from direct.interval.IntervalGlobal import *
from toontown.toonbase import ToonPythonUtil as PythonUtil
from direct.task import Task
from pandac.PandaModules import *
from Avatar import Avatar
from otp.ai.MagicWordGlobal import *
from otp.otpbase import OTPGlobals
from toontown.battle.BattleProps import globalPropPool

class DistributedAvatar(DistributedActor, Avatar):
    HpTextGenerator = TextNode('HpTextGenerator')
    HpTextEnabled = 1
    ManagesNametagAmbientLightChanged = True

    def __init__(self, cr):
        try:
            self.DistributedAvatar_initialized
            return
        except:
            self.DistributedAvatar_initialized = 1

        Avatar.__init__(self)
        DistributedActor.__init__(self, cr)
        self.hpText = None
        self.hp = None
        self.hpTextInterval2 = None
        self.hpTextInterval = None
        self.maxHp = None

    def disable(self):
        try:
            del self.DistributedAvatar_announced
            return
        except:
            self.DistributedAvatar_announced = 1

        self.reparentTo(hidden)
        self.removeActive()
        self.disableBodyCollisions()
        self.hideHpText()
        self.hp = None
        self.ignore('nameTagShowAvId')
        self.ignore('nameTagShowName')
        DistributedActor.disable(self)

    def delete(self):
        try:
            self.DistributedAvatar_deleted
            return
        except:
            self.DistributedAvatar_deleted = 1
            
        Avatar.delete(self)
        DistributedActor.delete(self)

    def generate(self):
        DistributedActor.generate(self)
        if not self.isLocal():
            self.addActive()
            self.considerUnderstandable()
        
        self.setParent(OTPGlobals.SPHidden)
        self.setTag('avatarDoId', str(self.doId))
        self.accept('nameTagShowAvId', self.__nameTagShowAvId)
        self.accept('nameTagShowName', self.__nameTagShowName)

    def announceGenerate(self):
        try:
            self.DistributedAvatar_announced
            return
        except:
            self.DistributedAvatar_announced = 1

        if not self.isLocal():
            self.initializeBodyCollisions('distAvatarCollNode-' + str(self.doId))
        DistributedActor.announceGenerate(self)

    def __setTags(self, extra = None):
        if hasattr(base, 'idTags'):
            if base.idTags:
                self.__nameTagShowAvId()
            else:
                self.__nameTagShowName()

    def do_setParent(self, parentToken):
        if not self.isDisabled():
            nametag2d = self.nametag.getNametag2d()
            if parentToken == OTPGlobals.SPHidden:
                nametag2d.hideNametag()
            else:
                nametag2d.showNametag()
            nametag2d.update()
            DistributedActor.do_setParent(self, parentToken)
            self.__setTags()

    def toonUp(self, hpGained):
        if self.hp == None or hpGained < 0:
            return
        oldHp = self.hp
        if self.hp + hpGained <= 0:
            self.hp += hpGained
        else:
            self.hp = min(max(self.hp, 0) + hpGained, self.maxHp)
        hpGained = self.hp - max(oldHp, 0)
        if hpGained > 0:
            self.showHpText(hpGained)
            self.hpChange(quietly=0)

    def takeDamage(self, hpLost, bonus = 0):
        if self.hp == None or hpLost < 0:
            return
        oldHp = self.hp
        self.hp = self.hp - hpLost
        hpLost = oldHp - self.hp
        if hpLost > 0:
            self.showHpText(-hpLost, bonus)
            self.hpChange(quietly=0)
            if self.hp <= 0 and oldHp > 0:
                self.died()

    def takeDamageCheat(self, hpLost, bonus = 0):
        if self.hp == None or hpLost < 0:
            return
        oldHp = self.hp
        self.hp = self.hp - hpLost
        hpLost = oldHp - self.hp
        if hpLost > 0:
            self.hpChange(quietly=0)
            if self.hp <= 0 and oldHp > 0:
                self.died()

    def setHp(self, hitPoints):
        justRanOutOfHp = (hitPoints is not None and self.hp is not None and self.hp - hitPoints > 0) and (hitPoints <= 0)
        self.hp = hitPoints
        self.hpChange(quietly=0)
        if justRanOutOfHp:
            self.died()

    def hpChange(self, quietly = 0):
        if hasattr(self, 'doId'):
            if self.hp != None and self.maxHp != None:
                messenger.send(self.uniqueName('hpChange'), [self.hp, self.maxHp, quietly])
            if self.hp != None and self.hp > 0:
                messenger.send(self.uniqueName('positiveHP'))

    def died(self):
        pass

    def getHp(self):
        return self.hp

    def setMaxHp(self, hitPoints):
        self.maxHp = hitPoints
        self.hpChange()

    def getMaxHp(self):
        return self.maxHp

    def getName(self):
        return Avatar.getName(self)

    def setName(self, name):
        try:
            self.node().setName('%s-%d' % (name, self.doId))
            self.gotName = 1
        except:
            pass

        return Avatar.setName(self, name)

    def getToonTag(self):
        return Avatar.getToonTag(self)

    def setToonTag(self, tag):
        return Avatar.setToonTag(self, tag)

    def showHpTextRed(self, number, bonus = 0, scale = 1):
        if self.HpTextEnabled and not self.ghostMode:
            if number != 0:
                if self.hpText:
                    self.hideHpText()
                self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
                if number < 0:
                    self.HpTextGenerator.setText(str(number))
                else:
                    self.HpTextGenerator.setText(str(number))
                self.HpTextGenerator.clearShadow()
                self.HpTextGenerator.setAlign(TextNode.ACenter)
                if bonus == 1:
                    r = 1.0
                    g = 0
                    b = 0
                    a = 1
                elif bonus == 2:
                    r = 1.0
                    g = 0
                    b = 0
                    a = 1
                elif bonus == 3:
                    r = 1
                    g = 0
                    b = 0
                    a = 1.0
                    scale = 0.9
                elif bonus == 4:
                    r = 1
                    g = 0
                    b = 0
                    a = 1.0
                    scale = 0.9
                elif number < 0:
                    r = 1
                    g = 0
                    b = 0
                    a = 1
                else:
                    r = 1
                    g = 0
                    b = 0
                    a = 1
                if self.hpTextInterval:
                    self.hpTextInterval.finish()
                    self.hpTextInterval = None
                if self.hpTextInterval2:
                    self.hpTextInterval2.finish()
                    self.hpTextInterval2 = None
                self.HpTextGenerator.setTextColor(r, g, b, a)
                self.hpTextNode = self.HpTextGenerator.generate()
                self.hpText = self.attachNewNode(self.hpTextNode)
                self.hpText.setScale(scale)
                self.hpText.setBillboardAxis()
                self.hpText.setBin('fixed', 100)
                self.hpText.setPos(0, 0, self.height / 2)
                self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), Wait(1.5), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Sequence(Wait(0.8), Func(self.hideHpText)))
                self.hpTextInterval.start()

    def showHpTextWhite(self, number, bonus = 0, scale = 1):
        if self.HpTextEnabled and not self.ghostMode:
            if number != 0:
                if self.hpText:
                    self.hideHpText()
                self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
                if number < 0:
                    self.HpTextGenerator.setText(str(number))
                else:
                    self.HpTextGenerator.setText(str(number))
                self.HpTextGenerator.clearShadow()
                self.HpTextGenerator.setAlign(TextNode.ACenter)
                if bonus == 1:
                    r = 1.0
                    g = 1
                    b = 1
                    a = 1
                elif bonus == 2:
                    r = 1.0
                    g = 1
                    b = 1
                    a = 1
                elif bonus == 3:
                    r = 1.0
                    g = 1
                    b = 1
                    a = 1
                    scale = 0.9
                elif bonus == 4:
                    r = 1.0
                    g = 1
                    b = 1
                    a = 1
                    scale = 0.9
                elif number < 0:
                    r = 1.0
                    g = 1
                    b = 1
                    a = 1
                else:
                    r = 1.0
                    g = 1
                    b = 1
                    a = 1
                if self.hpTextInterval:
                    self.hpTextInterval.finish()
                    self.hpTextInterval = None
                if self.hpTextInterval2:
                    self.hpTextInterval2.finish()
                    self.hpTextInterval2 = None
                self.HpTextGenerator.setTextColor(r, g, b, a)
                self.hpTextNode = self.HpTextGenerator.generate()
                self.hpText = self.attachNewNode(self.hpTextNode)
                self.hpText.setScale(scale)
                self.hpText.setBillboardAxis()
                self.hpText.setBin('fixed', 100)
                self.hpText.setPos(0, 0, self.height / 2)
                self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), Wait(1.5), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Sequence(Wait(0.8), Func(self.hideHpText)))
                self.hpTextInterval.start()

    def showHpText(self, number, bonus = 0, scale = 1):
        if self.HpTextEnabled and not self.ghostMode:
            if number != 0:
                if self.hpText:
                    self.hideHpText()
                self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
                if number < 0:
                    self.HpTextGenerator.setText(str(number))
                else:
                    self.HpTextGenerator.setText(str(number))
                self.HpTextGenerator.clearShadow()
                self.HpTextGenerator.setAlign(TextNode.ACenter)
                if bonus == 1:
                    r = 1.0
                    g = 1.0
                    b = 0
                    a = 1
                elif bonus == 2:
                    r = 1.0
                    g = 0.5
                    b = 0
                    a = 1
                elif bonus == 3:
                    r = 0.6
                    g = 0.2
                    b = 0.8
                    a = 1.0
                    scale = 0.9
                elif bonus == 4:
                    r = 0.93
                    g = 0.51
                    b = 0.93
                    a = 1.0
                    scale = 0.9
                elif number < 0:
                    r = 0.9
                    g = 0
                    b = 0
                    a = 1
                else:
                    r = 0
                    g = 0.9
                    b = 0
                    a = 1
                if self.hpTextInterval:
                    self.hpTextInterval.finish()
                    self.hpTextInterval = None
                if self.hpTextInterval2:
                    self.hpTextInterval2.finish()
                    self.hpTextInterval2 = None
                self.HpTextGenerator.setTextColor(r, g, b, a)
                self.hpTextNode = self.HpTextGenerator.generate()
                self.hpText = self.attachNewNode(self.hpTextNode)
                self.hpText.setScale(scale)
                self.hpText.setBillboardAxis()
                self.hpText.setBin('fixed', 100)
                self.hpText.setPos(0, 0, self.height / 2)
                self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), Wait(1.5), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Sequence(Wait(0.8), Func(self.hideHpText)))
                self.hpTextInterval.start()

    def showHpTextNew(self, number, text=None, bonus=0, scale=1, attackTrack=-1, colorCode=0):
        if self.HpTextEnabled and not self.ghostMode:
            if number != 0:
                if self.hpText:
                    self.hideHpText()
                self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
                if number < 0:
                    self.HpTextGenerator.setText(str(number))
                elif type(number) in [int, float]:
                    self.HpTextGenerator.setText('+' + str(number))
                else:
                    self.HpTextGenerator.setText(str(number))
                self.HpTextGenerator.clearShadow()
                self.HpTextGenerator.setAlign(TextNode.ACenter)
                if bonus == 1:
                    r = 1.0
                    g = 1.0
                    b = 0
                    a = 1
                elif bonus == 2:
                    r = 1.0
                    g = 0.5
                    b = 0
                    a = 1
                elif bonus == 3:
                    r = 0.6
                    g = 0.2
                    b = 0.8
                    a = 1.0
                    scale = 0.9
                elif bonus == 4:
                    r = 0.93
                    g = 0.51
                    b = 0.93
                    a = 1.0
                    scale = 0.9
                elif number < 0:
                    r = 0.9
                    g = 0
                    b = 0
                    a = 1
                else:
                    r = 0
                    g = 0.9
                    b = 0
                    a = 1
                if self.hpTextInterval:
                    self.hpTextInterval.finish()
                    self.hpTextInterval = None
                if self.hpTextInterval2:
                    self.hpTextInterval2.finish()
                    self.hpTextInterval2 = None
                self.HpTextGenerator.setTextColor(r, g, b, a)
                self.hpTextNode = self.HpTextGenerator.generate()
                self.hpText = self.attachNewNode(self.hpTextNode)
                self.hpText.setScale(scale)
                self.hpText.setBillboardAxis()
                self.hpText.setBin('fixed', 100)
                self.hpText.setPos(0, 0, self.height / 2)
                if text != None:
                    self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 2.5), blendType='easeOut'), Wait(1.0), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
                    self.hpTextInterval.start()
                else:
                    self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), Wait(1.0),
                                                   LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
                    self.hpTextInterval.start()

        if text != None:
            self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
            self.HpTextGenerator.setText(text)
            self.HpTextGenerator.clearShadow()
            self.HpTextGenerator.setAlign(TextNode.ACenter)
            r = a = 1.0
            g = b = 0.0
            if colorCode == 0:
                self.HpTextGenerator.setTextColor(1, 0, 0, 1) # Red
            if colorCode == 1:
                self.HpTextGenerator.setTextColor(0.871, 0.827, 1, 1) # Default Cheat Color
            if colorCode == 3:
                self.HpTextGenerator.setTextColor(1, 0.953, 0, 1) # Yellow
            if colorCode == 4:
                self.HpTextGenerator.setTextColor(1, 0.561, 0, 1) # Orange
            if colorCode == 5:
                self.HpTextGenerator.setTextColor(0.851, 0, 1, 1) # Purple
            self.hpTextNode = self.HpTextGenerator.generate()
            self.hpText2 = self.attachNewNode(self.hpTextNode)
            self.hpText2.setScale(scale)
            self.hpText2.setBillboardAxis()
            self.hpText2.setBin('fixed', 99)
            self.hpText2.setPos(0, 0, self.height / 2)
            self.hpTextInterval2 = Sequence(self.hpText2.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), Wait(1.0), LerpColorScaleInterval(self.hpText2, .25, Vec4(0, 0, 0, 0)),
                                           Func(self.hideHpText))
            self.hpTextInterval2.start()

    def showHpTextCheat(self, number, bonus = 0, scale = 1):
        if self.HpTextEnabled and not self.ghostMode:
            if number != 0:
                if self.hpText:
                    self.hideHpText()
                self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
                if number < 0:
                    self.HpTextGenerator.setText(str(number))
                else:
                    self.HpTextGenerator.setText(str(number))
                self.HpTextGenerator.clearShadow()
                self.HpTextGenerator.setAlign(TextNode.ACenter)
                if bonus == 1:
                    r = 1.0
                    g = 1.0
                    b = 0
                    a = 1
                elif bonus == 2:
                    r = 1.0
                    g = 0.5
                    b = 0
                    a = 1
                elif bonus == 3:
                    r = 0.6
                    g = 0.2
                    b = 0.8
                    a = 1.0
                    scale = 0.9
                elif bonus == 4:
                    r = 0.93
                    g = 0.51
                    b = 0.93
                    a = 1.0
                    scale = 0.9
                elif number < 0:
                    r = 0.9
                    g = 0
                    b = 0
                    a = 1
                else:
                    r = 0
                    g = 0.9
                    b = 0
                    a = 1
                if self.hpTextInterval:
                    self.hpTextInterval.finish()
                    self.hpTextInterval = None
                if self.hpTextInterval2:
                    self.hpTextInterval2.finish()
                    self.hpTextInterval2 = None
                self.HpTextGenerator.setTextColor(r, g, b, a)
                self.hpTextNode = self.HpTextGenerator.generate()
                self.hpText = self.attachNewNode(self.hpTextNode)
                self.hpText.setScale(scale)
                self.hpText.setBillboardAxis()
                self.hpText.setBin('fixed', 100)
                self.hpText.setPos(0, 0, self.height / 2)
                self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 2.5), blendType='easeOut'), Wait(1.5), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Sequence(Wait(0.8), Func(self.hideHpText)))
                self.hpTextInterval.start()

    def showHpTextVulnerable(self, number, bonus = 0, scale = 1):
        if self.HpTextEnabled and not self.ghostMode:
            if number != 0:
                if self.hpText:
                    self.hideHpText()
                self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
                if number < 0:
                    self.HpTextGenerator.setText(str(number) + '\n' + 'VULNERABLE!')
                else:
                    self.HpTextGenerator.setText(str(number))
                self.HpTextGenerator.clearShadow()
                self.HpTextGenerator.setAlign(TextNode.ACenter)
                if bonus == 1:
                    r = 1.0
                    g = 1.0
                    b = 0
                    a = 1
                elif bonus == 2:
                    r = 1.0
                    g = 0.5
                    b = 0
                    a = 1
                elif bonus == 3:
                    r = 0.6
                    g = 0.2
                    b = 0.8
                    a = 1.0
                    scale = 0.9
                elif bonus == 4:
                    r = 0.93
                    g = 0.51
                    b = 0.93
                    a = 1.0
                    scale = 0.9
                elif number < 0:
                    r = 0.9
                    g = 0
                    b = 0
                    a = 1
                else:
                    r = 0
                    g = 0.9
                    b = 0
                    a = 1
                if self.hpTextInterval:
                    self.hpTextInterval.finish()
                    self.hpTextInterval = None
                if self.hpTextInterval2:
                    self.hpTextInterval2.finish()
                    self.hpTextInterval2 = None
                self.HpTextGenerator.setTextColor(r, g, b, a)
                self.hpTextNode = self.HpTextGenerator.generate()
                self.hpText = self.attachNewNode(self.hpTextNode)
                self.hpText.setScale(scale)
                self.hpText.setBillboardAxis()
                self.hpText.setBin('fixed', 100)
                self.hpText.setPos(0, 0, self.height / 2)
                self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), Wait(1.5), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Sequence(Wait(0.8), Func(self.hideHpText)))
                self.hpTextInterval.start()



    def showHpString(self, text, duration = 0.85, scale = 1):
        if self.HpTextEnabled and not self.ghostMode:
            if self.hpTextInterval:
                self.hpTextInterval.finish()
                self.hpTextInterval = None
            if self.hpTextInterval2:
                self.hpTextInterval2.finish()
                self.hpTextInterval2 = None
            self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
            self.HpTextGenerator.setText(text)
            self.HpTextGenerator.clearShadow()
            self.HpTextGenerator.setAlign(TextNode.ACenter)
            r = a = 1.0
            g = b = 0.0
            self.HpTextGenerator.setTextColor(0.871, 0.827, 1, 1)
            self.hpTextNode = self.HpTextGenerator.generate()
            self.hpText = self.attachNewNode(self.hpTextNode)
            self.hpText.setScale(scale)
            self.hpText.setBillboardAxis()
            self.hpText.setBin('fixed', 99)
            self.hpText.setPos(0, 0, self.height / 2)
            self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'),Wait(1.5), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
            self.hpTextInterval.start()

    def showHpStringSnipe(self, text, duration = 0.85, scale = 1):
        if self.HpTextEnabled and not self.ghostMode:
            if self.hpTextInterval:
                self.hpTextInterval.finish()
                self.hpTextInterval = None
            if self.hpTextInterval2:
                self.hpTextInterval2.finish()
                self.hpTextInterval2 = None
            self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
            self.HpTextGenerator.setText(text)
            self.HpTextGenerator.clearShadow()
            self.HpTextGenerator.setAlign(TextNode.ACenter)
            r = a = 1.0
            g = b = 0.0
            self.HpTextGenerator.setTextColor(1, 0.561, 0, 1)
            self.hpTextNode = self.HpTextGenerator.generate()
            self.hpText = self.attachNewNode(self.hpTextNode)
            self.hpText.setScale(scale)
            self.hpText.setBillboardAxis()
            self.hpText.setBin('fixed', 99)
            self.hpText.setPos(0, 0, self.height / 2)
            self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'),Wait(1.5), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
            self.hpTextInterval.start()

    def showHpStringViral(self, text, duration = 0.85, scale = 1):
        if self.HpTextEnabled and not self.ghostMode:
            if self.hpTextInterval:
                self.hpTextInterval.finish()
                self.hpTextInterval = None
            if self.hpTextInterval2:
                self.hpTextInterval2.finish()
                self.hpTextInterval2 = None
            self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
            self.HpTextGenerator.setText(text)
            self.HpTextGenerator.clearShadow()
            self.HpTextGenerator.setAlign(TextNode.ACenter)
            r = a = 1.0
            g = b = 0.0
            self.HpTextGenerator.setTextColor(0.988, 0, 1, 1)
            self.hpTextNode = self.HpTextGenerator.generate()
            self.hpText = self.attachNewNode(self.hpTextNode)
            self.hpText.setScale(scale)
            self.hpText.setBillboardAxis()
            self.hpText.setBin('fixed', 99)
            self.hpText.setPos(0, 0, self.height / 2)
            self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'),Wait(1.5), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
            self.hpTextInterval.start()


    def showHpStringMissed(self, text, duration = 0.85, scale = 1):
        if self.HpTextEnabled and not self.ghostMode:
            if self.hpTextInterval:
                self.hpTextInterval.finish()
                self.hpTextInterval = None
            if self.hpTextInterval2:
                self.hpTextInterval2.finish()
                self.hpTextInterval2 = None
            self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
            self.HpTextGenerator.setText(text)
            self.HpTextGenerator.clearShadow()
            self.HpTextGenerator.setAlign(TextNode.ACenter)
            r = a = 1.0
            g = b = 0.0
            self.HpTextGenerator.setTextColor(1, 0, 0, 1)
            self.hpTextNode = self.HpTextGenerator.generate()
            self.hpText = self.attachNewNode(self.hpTextNode)
            self.hpText.setScale(scale)
            self.hpText.setBillboardAxis()
            self.hpText.setBin('fixed', 99)
            self.hpText.setPos(0, 0, self.height / 2)
            self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'),Wait(1.5), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
            self.hpTextInterval.start()

    def hideHpText(self):
        try:
            if self.hpText:
                taskMgr.remove(self.uniqueName('hpText'))
                self.hpText.removeNode()
                self.hpText = None
            if self.hpTextInterval:
                self.hpTextInterval.finish()
                self.hpTextInterval = None
        except:
            pass

    def getStareAtNodeAndOffset(self):
        return (self, Point3(0, 0, self.height))

    def getAvIdName(self):
        return '%s\n%s' % (self.getName(), self.doId)

    def __nameTagShowAvId(self, extra = None):
        self.setDisplayName(self.getAvIdName())

    def __nameTagShowName(self, extra = None):
        self.setDisplayName(self.getName())

    def askAvOnShard(self, avId):
        if base.cr.doId2do.get(avId):
            messenger.send('AvOnShard%s' % avId, [True])
        else:
            self.sendUpdate('checkAvOnShard', [avId])

    def confirmAvOnShard(self, avId, onShard = True):
        messenger.send('AvOnShard%s' % avId, [onShard])

    def getDialogueArray(self):
        return None

@magicWord(category=CATEGORY_COMMUNITY_MANAGER)
def warp():
    """
    Warp the target to the invoker's current position, and rotation.
    """
    invoker = spellbook.getInvoker()
    target = spellbook.getTarget()
    if invoker.doId == target.doId:
        return "You can't warp yourself!"
    target.setPosHpr(invoker.getPos(), invoker.getHpr())


@magicWord(category=CATEGORY_COMMUNITY_MANAGER, types=[str])
def loop(anim):
    """
    Animate the target using animation [anim] on the entire actor.
    """
    target = spellbook.getTarget()
    target.loop(anim)


@magicWord(category=CATEGORY_COMMUNITY_MANAGER, types=[str, int, str])
def pose(anim, frame, part=None):
    """
    Freeze the target on frame [frame] of animation [anim] on the entire actor,
    or optional [part] of the actor.
    """
    target = spellbook.getTarget()
    target.pose(anim, frame, partName=part)


@magicWord(category=CATEGORY_COMMUNITY_MANAGER, types=[str, int, int, str])
def pingpong(anim, start=None, end=None, part=None):
    """
    Animate the target by bouncing back and forth between the start and end, or
    the optional frames <start>, and [end] of animation [anim] on the entire
    actor, or optional <part> of the actor.
    """
    target = spellbook.getTarget()
    target.pingpong(anim, partName=part, fromFrame=start, toFrame=end)

@magicWord(category=CATEGORY_COMMUNITY_MANAGER, types=[str])
def rightHand(prop=None):
    """
    Parents the optional <prop> to the target's right hand node.
    """
    target = spellbook.getTarget()
    rightHand = target.find('**/rightHand')
    if prop is None:
        for child in rightHand.getChildren():
            child.removeNode()
    else:
        for child in rightHand.getChildren():
            child.removeNode()
        requestedProp = globalPropPool.getProp(prop)
        requestedProp.reparentTo(rightHand)

@magicWord(category=CATEGORY_COMMUNITY_MANAGER, types=[str])
def leftHand(prop=None):
    """
    Parents the optional <prop> to the target's left hand node.
    """
    target = spellbook.getTarget()
    leftHand = target.find('**/leftHand')
    if prop is None:
        for child in leftHand.getChildren():
            child.removeNode()
    else:
        for child in leftHand.getChildren():
            child.removeNode()
        requestedProp = globalPropPool.getProp(prop)
        requestedProp.reparentTo(leftHand)