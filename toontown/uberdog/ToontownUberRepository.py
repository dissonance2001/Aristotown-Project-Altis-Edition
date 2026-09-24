import urllib.parse
from direct.distributed.PyDatagram import *
from otp.distributed.DistributedDirectoryAI import DistributedDirectoryAI
from otp.distributed.OtpDoGlobals import *
from otp.otpbase import BackupManager
from toontown.distributed.ToontownInternalRepository import ToontownInternalRepository
from toontown.suit.SuitInvasionManagerUD import SuitInvasionManagerUD
from toontown.club.ClubCoinServiceUD import ClubCoinServiceUD
from toontown.club.ClubsServiceUD import ClubsServiceUD
from toontown.club.DistributedClubManagerUD import DistributedClubManagerUD


from toontown.rpc.ToontownRPCServer import ToontownRPCServer
from toontown.rpc.ToontownRPCHandler import ToontownRPCHandler

class ToontownUberRepository(ToontownInternalRepository):

    def __init__(self, baseChannel, serverId):
        ToontownInternalRepository.__init__(self, baseChannel, serverId, dcSuffix='UD')
        self.rpcServer = None
        self.rpcClient = None
        self.inventoryDatabase = None

        # NOTE: this connection used to be gated behind the 'want-mongo-client'
        # config var, which meant self.mongodb (and anything built on top of
        # it, like the Hammerspace-equipped-items lookup used by the avatar
        # picker) silently didn't exist unless that flag was explicitly set.
        # The Uberdog needs its own Mongo handle for that to work at all
        # (it can't reach the AI repository's inventoryDb), so this is now
        # unconditional, matching how the AI repository connects.
        #
        # IMPORTANT: the database name is hardcoded to 'altis' to match
        # ToontownAIRepository (self.dbConn.altis) exactly. The AI writes
        # every toon's inventory there; if this ever derives its own name
        # (e.g. from the mongodb-url's path) instead of matching that
        # hardcoded name, the Uberdog silently reads from/writes to a
        # different, empty database and every query here will act as if
        # the avatar has no inventory at all.
        import pymongo
        url = config.GetString('mongodb-url', 'mongodb://localhost')
        replicaset = config.GetString('mongodb-replicaset', '')
        if replicaset:
            self.mongo = pymongo.MongoClient(url, replicaset=replicaset)
        else:
            self.mongo = pymongo.MongoClient(url)
        db = 'altis'
        self.mongodb = self.mongo[db]

        self.notify.setInfo(True)

        self.clubsService: Optional[ClubsServiceUD] = None
        self.clubsManager: Optional[DistributedClubManagerUD] = None
        self.clubCoinService: Optional[ClubCoinServiceUD] = None

    def handleConnected(self):
        self.registerForChannel(MESSENGER_CHANNEL_UD)

        rootObj = DistributedDirectoryAI(self)
        rootObj.generateWithRequiredAndId(self.getGameDoId(), 0, 0)

        endpoint = config.GetString('rpc-server-endpoint', 'http://localhost:8080/')

        self.rpcServer = ToontownRPCServer(endpoint, ToontownRPCHandler(self))
        self.rpcServer.start(useTaskChain=True)
        self.backups = BackupManager.BackupManager(
            filepath = 'user/backups/',
            extension = '.json')
        self.createGlobals()
        self.notify.info('Done.')

    def createGlobals(self):
        """
        Create "global" objects.
        """
        from toontown.inventory.services.InventoryDatabaseUD import InventoryDatabaseUD
        self.inventoryDatabase = InventoryDatabaseUD(self)

        self.csm = simbase.air.generateGlobalObject(OTP_DO_ID_CLIENT_SERVICES_MANAGER, 'ClientServicesManager')
        self.chatAgent = simbase.air.generateGlobalObject(OTP_DO_ID_CHAT_MANAGER, 'ChatAgent')
        self.friendsManager = simbase.air.generateGlobalObject(OTP_DO_ID_TTA_FRIENDS_MANAGER, 'TTAFriendsManager')
        self.deliveryManager = simbase.air.generateGlobalObject(OTP_DO_ID_TOONTOWN_DELIVERY_MANAGER, 'DistributedDeliveryManager')
        self.codeRedemptionMgr = simbase.air.generateGlobalObject(OTP_DO_ID_TOONTOWN_CODE_REDEMPTION_MANAGER, 'TTCodeRedemptionMgr')
        self.invasionMgr = SuitInvasionManagerUD(self)
        self.invasionMgr.startInitialInvasion()
        self.clubsManager = self.generateGlobalObject(OTP_DO_ID_GLOBAL_CLUB_MANAGER, 'DistributedClubManager')

