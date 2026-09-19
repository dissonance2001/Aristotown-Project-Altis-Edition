from typing import Optional

from panda3d.core import *
from direct.interval.IntervalGlobal import Sequence, Parallel, LerpColorScaleInterval, Wait
from direct.task.Task import Task
from toontown.toonbase import ToontownGlobals

MODE_ROAM = 0
MODE_BATTLE = 1

HEALTH_COLORS = (
    Vec4(0, 1, 0, 1),
    Vec4(0.5, 1, 0, 1),
    Vec4(0.75, 1, 0, 1),
    Vec4(1, 1, 0, 1),
    Vec4(1, 0.866, 0, 1),
    Vec4(1, 0.6, 0, 1),
    Vec4(1, 0.5, 0, 1),
    Vec4(1, 0.25, 0, 1.0),
    Vec4(1, 0, 0, 1),
    Vec4(0.3, 0.3, 0.3, 1),
    Vec4(0, .9, .9, 1),
    Vec4(1, 1, 1, 1),  # White "Roam-mode" for skelecogs
    Vec4(0.6, 0, 1, 1),  # Overcharge
    Vec4(186/255, 82/255, 1.0, 1.0)  # Overcharge energy flicker
)


class SuitHealthMeter:

    SUITS_HIDE_METER = (
        'hroller',
        'hrollerc',
    )

    def __init__(self, suit):
        self.geom = None
        self.mode = MODE_ROAM
        self.hpCond = 0
        self.suit = suit
        self.skeleton = False
        self.icons = []
        self.hpParts = []
        self.dept = self.suit.style.dept
        self.overchargeSeq = None
        
    def generate(self, skeleton=False, startMode=-1):
        if startMode != -1:
            self.mode = startMode
        
        if skeleton:
            self.skeleton = True
            self.hpParts = [self.suit.find('**/emblem_healthmeter'), self.suit.find('**/glow')]
        else:
            self.geom = loader.loadModel('phase_3.5/models/char/ttcc_ene_insignias')
            chestNull = self.suit.find('**/joint_attachMeter')
            self.geom.reparentTo(chestNull)
            
            boardIcon = self.geom.find('**/emblem_board')
            corpIcon = self.geom.find('**/emblem_corp')
            legalIcon = self.geom.find('**/emblem_legal')
            moneyIcon = self.geom.find('**/emblem_money')
            salesIcon = self.geom.find('**/emblem_sales')
            
            self.icons = [boardIcon, corpIcon, legalIcon, moneyIcon, salesIcon]

            if self.suit.style.name in self.SUITS_HIDE_METER:
                self.geom.hide()
            self.hpParts = [self.geom.find('**/emblem_hp'), self.geom.find('**/glow')]
            for part in self.hpParts:
                part.setColorScale(HEALTH_COLORS[0])
                part.stash()

            self.geom.setH(180)
            body = self.suit.style.body
            female = self.suit.style.isFemale()
            if body == 'a':
                if female:
                    self.geom.setY(-0.1)
                else:
                    self.geom.setY(-0.125)
            elif body == 'b':
                if female:
                    self.geom.setY(0)
                else:
                    self.geom.setY(-0.025)
            else:
                if female:
                    self.geom.setPos(0, 0.03, 0.2)
                    self.geom.setP(4)
                else:
                    self.geom.setY(0.075)

        self.updateMeterMode(self.mode)

    def updateMeterMode(self, newMode):
        if not self.suit:
            # May happen if a 2.0 is reviving
            return

        if not self.suit.healthColored:
            self.mode = newMode
            if self.skeleton:
                if self.mode == MODE_ROAM:
                    self.setHealthColor(11)  # Just display a light off. Insignia is only for fully built models
            else:
                if self.mode == MODE_ROAM:
                    for i in range(len(self.icons)):
                        icon = self.icons[i]
                        icon.stash()

                    icon = self.icons[ToontownGlobals.cogDept2index.get(self.dept, 0)].unstash() # Unstash the icon for this dept, if not defined, default to board
                    for part in self.hpParts:
                        part.stash()
                else:
                    for part in self.hpParts:
                        part.unstash()
                
    def delete(self):
        if self.overchargeSeq:
            self.overchargeSeq.finish()
            self.overchargeSeq = None

        if self.geom:
            self.geom.removeNode()
            self.geom = None
        taskMgr.remove('blink-task-%s' % id(self))
        self.suit = None
        self.dept = None
        self.hpCond = 0
        
    def getParts(self):
        return self.hpParts
        
    def setColorScaleOff(self, priority=0):
        # Stops the health light from inheriting a color scale applied to a cog (like virtual skelecogs)
        if self.geom:
            self.geom.setColorScaleOff(priority)
        else:
            for part in self.hpParts:
                part.setColorScaleOff(priority)

    def setHealthColor(self, colorIdx, healthColorId: Optional[int] = None):
        if self.overchargeSeq:
            self.overchargeSeq.finish()
            self.overchargeSeq = None

        if self.suit.healthColored:
            actorNode = self.suit.find('**/__Actor_modelRoot')
            actorCollection = actorNode.findAllMatches('*')
            for thing in actorCollection:
                if thing.getName() not in ('joint_attachMeter', 'joint_nameTag', 'def_nameTag'):
                    if colorIdx == 10:
                        color = Vec4(1, 0, 0, 1)
                    else:
                        color = HEALTH_COLORS[healthColorId or colorIdx]
                    thing.setColorScale(color)
                    thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
                    thing.setDepthWrite(False)
                    thing.setBin('fixed', 1)
        elif self.hpParts:
            for part in self.hpParts:
                part.setColorScale(HEALTH_COLORS[colorIdx])
            if colorIdx == 9:
                self.hpParts[1].hide()  # Hide the glow effect when the light is off
            else:
                self.hpParts[1].show()

            if colorIdx == 12:
                self.overchargeSeq = Sequence(
                    Wait(1.5),
                    Parallel(
                        LerpColorScaleInterval(self.hpParts[0], 1.0, HEALTH_COLORS[13], blendType='easeInOut'),
                        LerpColorScaleInterval(self.hpParts[1], 1.0, HEALTH_COLORS[13], blendType='easeInOut')
                    ),
                    Parallel(
                        LerpColorScaleInterval(self.hpParts[0], 1.0, HEALTH_COLORS[12], blendType='easeInOut'),
                        LerpColorScaleInterval(self.hpParts[1], 1.0, HEALTH_COLORS[12], blendType='easeInOut')
                    ),
                )
                self.overchargeSeq.loop()
        
    def updateHealthBar(self, forceUpdate = 0):
        health = self.suit.getHealthPercentage()
        if hasattr(self.suit, 'isSupercharged') and self.suit.isSupercharged():
            condition = 12
        elif health > 1.0:
            condition = 11
        elif health > 0.95:
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

        if self.hpCond != condition or forceUpdate:
            if condition == 9:
                blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.75), Task(self.__blinkGray), Task.pause(0.1))
                taskMgr.add(blinkTask, 'blink-task-%s' % id(self))
            elif condition == 10:
                if self.hpCond == 9:
                    taskMgr.remove('blink-task-%s' % id(self))
                blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.25), Task(self.__blinkGray), Task.pause(0.1))
                taskMgr.add(blinkTask, 'blink-task-%s' % id(self))
            elif condition == 11:
                taskMgr.remove('blink-task-%s' % id(self))
                self.setHealthColor(10)
            else:
                taskMgr.remove('blink-task-%s' % id(self))
                self.setHealthColor(condition)
            self.hpCond = condition
    
    def __blinkRed(self, task):
        self.setHealthColor(8, healthColorId=9)
        
        return Task.done
    
    def __blinkGray(self, task):
        self.setHealthColor(9)
        
        return Task.done
