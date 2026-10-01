from pandac.PandaModules import Vec3
from toontown.town import Street

LighthouseFogTask = 'DDStreet-lighthouse-fog-task'
MaxFogDistance = 190.0
FogPoint = Vec3(341.585, -170, 2)

class DDStreet(Street.Street):

    def exit(self):
        taskMgr.remove(LighthouseFogTask)
        Street.Street.exit(self)

    def doEnterZone(self, newZoneId):
        Street.Street.doEnterZone(self, newZoneId)

        if newZoneId in (1315, 1316):
            taskMgr.add(self.__checkAreaFog, LighthouseFogTask)
        else:
            taskMgr.remove(LighthouseFogTask)
            if self.fog:
                self.fog.setLinearRange(0, 400)

    def __checkAreaFog(self, task=None):
        posDiff = Vec3(base.localAvatar.getPos(render) - FogPoint).length()
        if self.fog:
            maxRange = 200 + (200 * min(posDiff / MaxFogDistance, 1))
            self.fog.setLinearRange(0, maxRange)
        return task.cont