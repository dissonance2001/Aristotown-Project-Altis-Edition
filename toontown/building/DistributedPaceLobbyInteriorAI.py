from toontown.building.DistributedToonInteriorAI import *
from toontown.toonbase import ToontownGlobals

class DistributedPaceLobbyInteriorAI(DistributedToonInteriorAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedPaceLobbyInteriorAI")