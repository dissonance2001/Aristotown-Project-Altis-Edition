from toontown.building.DistributedToonInteriorAI import *
from toontown.toonbase import ToontownGlobals

class DistributedPizzeriaInteriorAI(DistributedToonInteriorAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedPizzeriaInteriorAI")