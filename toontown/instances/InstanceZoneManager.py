from direct.distributed import DistributedObject
from direct.directnotify import DirectNotifyGlobal


class InstanceZoneManager(DistributedObject.DistributedObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('InstanceZoneManager')

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)

    def generate(self):
        DistributedObject.DistributedObject.generate(self)
        self.notify.debug('generate')

    def disable(self):
        DistributedObject.DistributedObject.disable(self)

    def delete(self):
        DistributedObject.DistributedObject.delete(self)