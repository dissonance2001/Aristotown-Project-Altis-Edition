
from direct.directnotify import DirectNotifyGlobal
from direct.distributed.PyDatagram import PyDatagram
from direct.showbase.Messenger import Messenger

import sys
if sys.version_info >= (3, 0):
    from pickle import dumps, loads
else:
    from cPickle import dumps, loads


# Messages do not need to be in the MESSAGE_TYPES list.
# This is just an optimization.  If the message is found
# in this list, it is reduced to an integer index and
# the message string is not sent.  Otherwise, the message
# string is sent in the datagram.
MESSAGE_TYPES=(
    "avatarOnline",
    "avatarOffline",
    "create",
    "needUberdogCreates",
    "transferDo",
)

# This is the reverse look up for the recipient of the
# datagram:
MESSAGE_STRINGS={}
for i in zip(MESSAGE_TYPES, range(1, len(MESSAGE_TYPES)+1)):
    MESSAGE_STRINGS[i[0]]=i[1]


class NetMessenger(Messenger):
    """
    This works very much like the Messenger class except that messages
    are sent over the network and (possibly) handled (accepted) on a
    remote machine (server).
    """
    notify = DirectNotifyGlobal.directNotify.newCategory('NetMessenger')

    def __init__(self, air, channels):
        """
        air is the AI Repository.
        channels is a list of channel IDs (uint32 values)
        """
        assert self.notify.debugCall()
        Messenger.__init__(self)
        self.air=air
        self.channels=channels
        for i in self.channels:
            self.air.registerForChannel(i)

    def clear(self):
        assert self.notify.debugCall()
        for i in self.channels:
            self.air.unRegisterChannel(i)
        del self.air
        del self.channels
        Messenger.clear(self)

    def send(self, message, sentArgs=[]):
        """
        Send message to All AI and Uber Dog servers.
        """
        assert self.notify.debugCall()
        datagram = PyDatagram()
        # To:
        datagram.addUint8(1)
        datagram.addChannel(self.channels[0])
        # From:
        datagram.addChannel(self.air.ourChannel)
        #if 1: # We send this just because the air expects it:
        #    # Add an 'A' for AI
        #    datagram.addUint8(ord('A'))

        messageType=MESSAGE_STRINGS.get(message, 0)
        datagram.addUint16(messageType)
        if messageType:
            datagram.addBlob(dumps(sentArgs))
        else:
            datagram.addBlob(dumps((message, sentArgs)))
        self.air.send(datagram)

    def handle(self, msgType, di):
        """
        Handle a NetMessenger-style message read off the wire.
        msgType is the message-type field already parsed by the caller;
        di is the PyDatagramIterator positioned at the pickled payload.
        The payload should be either just sentArgs (if msgType names a
        pre-registered message) or a (messageString, sentArgsList) tuple.
        """
        assert self.notify.debugCall()
        if msgType:
            message=MESSAGE_TYPES[msgType-1]
            sentArgs=loads(di.getBlob())
        else:
            (message, sentArgs) = loads(di.getBlob())
        Messenger.send(self, message, sentArgs=sentArgs)


