from direct.showbase.MessengerGlobal import messenger


class ShardStatusReceiver:

    def __init__(self, air):
        self.air = air

        self.shards = {}

        # Accept the shardStatus event:
        messenger.accept('shardStatus', self, self.handleShardStatus)

        # Query the status of any existing shards:
        self.air.sendNetEvent('queryShardStatus')

    def handleShardStatus(self, channel, status):
        self.shards.setdefault(channel, {}).update(status)

    def getShards(self):
        return self.shards
