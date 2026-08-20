from __future__ import absolute_import
from direct.directnotify import DirectNotifyGlobal
from direct.showbase.DirectObject import DirectObject

from toontown.instances import InstanceGlobals


class InstanceZoneManagerAI(DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('InstanceZoneManagerAI')

    def __init__(self, air):
        DirectObject.__init__(self)
        self.air = air
        self.instanceTypes = {}
        self.activeInstances = {}
        self._registerBuiltins()

    def _registerBuiltins(self):
        from toontown.suit import DistributedHighRollerBossAI
        from toontown.suit import DistributedVideographerBossAI
        from toontown.suit import DistributedPacesetterBossAI
        from toontown.suit import DistributedChainsawBossAI
        from toontown.suit import DistributedPlutocratBossAI
        from toontown.suit import DistributedCountErfitBossAI
        from toontown.instances.MotoroomInstanceSessionAI import MotoroomInstanceSessionAI

        self.registerInstanceType(
            InstanceGlobals.HIGH_ROLLER,
            DistributedHighRollerBossAI.DistributedHighRollerBossAI)
        self.registerInstanceType(
            InstanceGlobals.VIDEOGRAPHER,
            DistributedVideographerBossAI.DistributedVideographerBossAI)
        self.registerInstanceType(
            InstanceGlobals.PACESETTER,
            DistributedPacesetterBossAI.DistributedPacesetterBossAI)
        self.registerInstanceType(
            InstanceGlobals.CHAINSAW,
            DistributedChainsawBossAI.DistributedChainsawBossAI)
        self.registerInstanceType(
            InstanceGlobals.PLUTOCRAT,
            DistributedPlutocratBossAI.DistributedPlutocratBossAI)
        self.registerInstanceType(
            InstanceGlobals.COUNT_ERFIT,
            DistributedCountErfitBossAI.DistributedCountErfitBossAI)
        self.registerInstanceType(
            InstanceGlobals.MOTOROOM,
            MotoroomInstanceSessionAI)

    def registerInstanceType(self, instanceId, constructor,
                             doneEvent='BossDone', startState='WaitForToons'):
        if not instanceId:
            raise ValueError('instanceId may not be empty')
        self.instanceTypes[instanceId] = {
            'constructor': constructor,
            'doneEvent': doneEvent,
            'startState': startState,
        }
        self.notify.info('Registered instance type %s' % instanceId)

    def hasInstanceType(self, instanceId):
        return instanceId in self.instanceTypes

    def createInstance(self, avIdList, instanceId, *args, **kwargs):
        definition = self.instanceTypes.get(instanceId)
        if definition is None:
            self.notify.warning('Unknown instance type: %r' % (instanceId,))
            return 0

        avIdList = [avId for avId in avIdList if avId]
        if not avIdList:
            self.notify.warning('Refusing to create empty instance %s' % instanceId)
            return 0

        zoneId = self.air.allocateZone()
        instance = None
        try:
            instance = definition['constructor'](self.air, *args, **kwargs)
            instance.generateWithRequired(zoneId)

            self.activeInstances[zoneId] = {
                'instanceId': instanceId,
                'object': instance,
            }

            doneEvent = definition.get('doneEvent')
            if doneEvent:
                self.acceptOnce(
                    instance.uniqueName(doneEvent),
                    self._handleInstanceDone,
                    extraArgs=[zoneId, instance])

            for avId in avIdList:
                instance.addToon(avId)

            startState = definition.get('startState')
            if startState:
                instance.b_setState(startState)

            self.notify.info(
                'Created %s instance in dynamic zone %s for %s' %
                (instanceId, zoneId, avIdList))
            return zoneId
        except Exception:
            self.notify.warning(
                'Failed creating %s instance in zone %s' %
                (instanceId, zoneId))
            if instance is not None:
                try:
                    instance.requestDelete()
                except Exception:
                    pass
            self.activeInstances.pop(zoneId, None)
            self.air.deallocateZone(zoneId)
            raise

    def createBossOffice(self, avIdList, instanceId, *args, **kwargs):
        return self.createInstance(avIdList, instanceId, *args, **kwargs)

    def _handleInstanceDone(self, zoneId, instance):
        current = self.activeInstances.get(zoneId)
        if current is None or current.get('object') is not instance:
            return
        self.destroyInstance(zoneId)

    def destroyInstance(self, zoneId):
        current = self.activeInstances.pop(zoneId, None)
        if current is None:
            return

        instance = current.get('object')
        if instance is not None:
            try:
                self.ignore(instance.uniqueName(
                    self.instanceTypes.get(current.get('instanceId'), {}).get(
                        'doneEvent', 'BossDone')))
            except Exception:
                pass
            try:
                instance.requestDelete()
            except Exception:
                pass

        self.notify.info(
            'Destroyed %s instance in dynamic zone %s' %
            (current.get('instanceId'), zoneId))
        self.air.deallocateZone(zoneId)

    def delete(self):
        for zoneId in list(self.activeInstances.keys()):
            self.destroyInstance(zoneId)
        self.ignoreAll()
        self.instanceTypes = {}
        self.air = None
