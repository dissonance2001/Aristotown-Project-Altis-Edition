from __future__ import absolute_import
from direct.distributed.PyDatagram import PyDatagram
from otp.distributed import OtpDoGlobals

import six.moves.cPickle, zlib


class ToontownNetMessengerAI:
    """
    This works very much like the NetMessenger class except that
    this is much simpler and makes much more sense.
    """
    notify = directNotify.newCategory('ToontownNetMessengerAI')

    def __init__(self, air, msgType=54321):
        self.air = air
        self.air.registerForChannel(OtpDoGlobals.MESSENGER_CHANNEL_ALL)
        self.msgType = msgType
        
    def prepare(self, message, sentArgs=[], channels=None):
        dg = PyDatagram()

        if channels is None:
            channels = [OtpDoGlobals.MESSENGER_CHANNEL_ALL]

        dg.addInt8(len(channels))
        for channel in channels:
            dg.addChannel(channel)

        dg.addChannel(self.msgType)
        dg.addUint16(self.msgType)
        dg.addString(message)
        dg.addBlob(zlib.compress(six.moves.cPickle.dumps(sentArgs)))
        return dg
        
    def send(self, message, sentArgs=[], channels=None):
        self.notify.debug('sendNetEvent: %s %r' % (message, sentArgs))
        dg = self.prepare(message, sentArgs, channels)
        self.air.send(dg)
        
    def handle(self, msgType, di):
        message = di.getString()
        data = zlib.decompress(di.getString())
        sentArgs = six.moves.cPickle.loads(data)
        messenger.send(message, sentArgs)
