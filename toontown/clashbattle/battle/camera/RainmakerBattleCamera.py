from direct.interval.IntervalGlobal import *
from panda3d.core import *

from toontown.battle.BattleCamera import BattleCamera
from toontown.battle.environmental.base.EnvironmentalEnum import RainmakerWeather
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class RainmakerBattleCamera(BattleCamera):

    monsoonPos = Point3(-6.8445, -85.6119, 43.6376)
    monsoonHpr = Vec3(-23.136, 0.0, 0.0)

    AUTO_WAITFORINPUT_HEIGHT = False

    def getPosWaitForInput(self):
        if self.isMonsoon():
            return self.monsoonPos
        else:
            return super().getPosWaitForInput()

    def getHprWaitForInput(self):
        if self.isMonsoon():
            return self.monsoonHpr
        else:
            return super().getHprWaitForInput()

    def getMonsoonCamera(self, attackDuration: float) -> Sequence:
        return Sequence(
            Func(camera.setPos, self.getPosWaitForInput()),
            Func(camera.setHpr, self.getHprWaitForInput()),
            Wait(attackDuration),
        )

    def chooseHealShot(self, heals, attackDuration):
        if self.isMonsoon():
            return self.getMonsoonCamera(attackDuration)
        return super().chooseHealShot(heals, attackDuration)

    def chooseTrapShot(self, attackDuration):
        if self.isMonsoon():
            return self.getMonsoonCamera(attackDuration)
        return super().chooseTrapShot(attackDuration)

    def chooseZapShot(self, attackDuration):
        if self.isMonsoon():
            return self.getMonsoonCamera(attackDuration)
        return super().chooseZapShot(attackDuration)

    def chooseThrowShot(self, throws, suitThrowsDict, attackDuration):
        if self.isMonsoon():
            return self.getMonsoonCamera(attackDuration)
        return super().chooseThrowShot(throws, suitThrowsDict, attackDuration)

    def chooseSoundShot(self, sounds, targets, attackDuration):
        if self.isMonsoon():
            return self.getMonsoonCamera(attackDuration)
        return super().chooseSoundShot(sounds, targets, attackDuration)

    def chooseDropShot(self, drops, suitDropsDict, attackDuration):
        if self.isMonsoon():
            return self.getMonsoonCamera(attackDuration)
        return super().chooseDropShot(drops, suitDropsDict, attackDuration)

    def chooseFireShot(self, fires, suitFiresDict, attackDuration):
        if self.isMonsoon():
            return self.getMonsoonCamera(attackDuration)
        return super().chooseFireShot(fires, suitFiresDict, attackDuration)

    def chooseSquirtShot(self, squirts, suitSquirtsDict, attackDuration):
        if self.isMonsoon():
            return self.getMonsoonCamera(attackDuration)
        return super().chooseSquirtShot(squirts, suitSquirtsDict, attackDuration)

    """
    Getters
    """

    def isMonsoon(self) -> bool:
        return self.battle.currentWeather == RainmakerWeather.MONSOON
