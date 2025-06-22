from toontown.toonbase.ToonBaseGlobal import *
from panda3d.core import *
from panda3d.toontown import *
from direct.interval.IntervalGlobal import *
from direct.distributed.ClockDelta import *
from toontown.toonbase import ToontownGlobals
import ToonInterior
from DistributedToonInterior import DistributedToonInterior
import ToonInteriorColors, random
from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObject
import random
from toontown.hood import ZoneUtil
from toontown.char import Char
from toontown.quest import QuestParser
from toontown.hood import ZoneUtil
from direct.actor.Actor import Actor
from direct.fsm import State

class DistributedSchoolHouseInterior(DistributedToonInterior):

    def __init__(self, cr):
        DistributedToonInterior.__init__(self, cr)

    def setup(self):
        self.dnaStore = base.cr.playGame.dnaStore
        self.randomGenerator = random.Random()
        self.randomGenerator.seed(self.zoneId)
        interior = self.randomDNAItem('TI_schoolhouse', self.dnaStore.findNode)
        self.interior = interior.copyTo(render)
        hoodId = ZoneUtil.getCanonicalHoodId(self.zoneId)
        self.colors = ToonInteriorColors.colors[hoodId]
        self.replaceRandomInModel(self.interior)
        doorModelName = 'door_double_round_ul'
        if doorModelName[-1:] == 'r':
            doorModelName = doorModelName[:-1] + 'l'
        else:
            doorModelName = doorModelName[:-1] + 'r'
        door = self.dnaStore.findNode(doorModelName)
        door_origin = render.find('**/door_origin;+s')
        doorNP = door.copyTo(door_origin)
        door_origin.setScale(0.8, 0.8, 0.8)
        door_origin.setPos(door_origin, 0, -0.025, 0)
        color = self.randomGenerator.choice(self.colors['TI_door'])
        DNADoor.setupDoor(doorNP, self.interior, door_origin, self.dnaStore, str(self.block), color)
        doorFrame = doorNP.find('door_*_flat')
        doorFrame.wrtReparentTo(self.interior)
        doorFrame.setColor(color)
        del self.colors
        del self.dnaStore
        del self.randomGenerator
        self.interior.flattenMedium()
        self.chalkboard = Actor('phase_3.5/models/schoolhouse/schoolhouse_classroom_chalkboard-zero.bam',{'draw':'phase_3.5/models/schoolhouse/schoolhouse_classroom_chalkboard-draw.bam'})
        backboard_origin = render.find('**/classroom_chalkboard_locator')
        self.chalkboard.reparentTo(backboard_origin)
        chalkboardBack = loader.loadModel('phase_3.5/models/schoolhouse/schoolhouse_classroom_chalkboard_back.bam')
        desk1 = loader.loadModel('phase_3.5/models/schoolhouse/schoolhouse_classroom_desk_student.bam')
        desk1_origin = render.find('**/classroom_desk_student_locator_1')
        desk1.reparentTo(desk1_origin)
        # desk 2 is crushed by bowling ball and locator doesn't exist
        desk3 = loader.loadModel('phase_3.5/models/schoolhouse/schoolhouse_classroom_desk_student.bam')
        desk3_origin = render.find('**/classroom_desk_student_locator_3')
        desk3.reparentTo(desk3_origin)
        desk4 = loader.loadModel('phase_3.5/models/schoolhouse/schoolhouse_classroom_desk_student.bam')
        desk4_origin = render.find('**/classroom_desk_student_locator_4')
        desk4.reparentTo(desk4_origin)
        GymDoor = loader.loadModel('phase_3.5/models/schoolhouse/schoolhouse_interior_gymDoor.bam')
        GymDoor_origin = render.find('**/classroom_trainingroomEntrance_locator')
        GymDoor.reparentTo(GymDoor_origin)
        GymSign = loader.loadModel('phase_3.5/models/schoolhouse/schoolhouse_classroom_trainingRoom_sign.bam')
        GymSign_origin = render.find('**/classroom_trainingroomTV_locator')
        GymSign.reparentTo(GymSign_origin)
        chalkboardBack.reparentTo(backboard_origin)
        self.chalkboard.loop('draw')

    def disable(self):
        self.enterOff()
        DistributedToonInterior.disable(self)

    def delete(self):
        DistributedToonInterior.delete(self)
    
