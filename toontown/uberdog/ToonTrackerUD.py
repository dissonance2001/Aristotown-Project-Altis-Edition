from typing import Dict, Set, Optional, List, TYPE_CHECKING

from direct.showbase.DirectObject import DirectObject

from toontown.clashbattle.battle import BattleGlobals
from toontown.toon.DistributedSettingsAI import DistributedSettingsAI
from toontown.uberdog.CachedToonStats import CachedToonStats
from toontown.uberdog.UberdogGlobalsUD import NET_MESSENGER_REGISTER_SHARD
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

if TYPE_CHECKING:
    from toontown.uberdog.ToontownUberRepository import ToontownUberRepository


@DirectNotifyCategory()
class ToonTrackerUD(DirectObject):
    """
    Tracks the Zone Group of every Toon across all shards.

    Zone Group
    ----------
    A Zone Group is a collection of zones.
    For example, a zone group would be all the vis-groups of Silly Street (2100 to 2199).
    This allows staff to communicate street wide during events or moderation duties.
    """

    def __init__(self, air: 'ToontownUberRepository'):
        self.air = air

        # State
        self._allToons: Dict[int, CachedToonStats] = dict()     # The mapping between avIds to their stats.
        self._cachedStats: Dict[int, CachedToonStats] = dict()  # Cached toon stats. Pulled from here if the Toon is offline.
        self._district2Toons: Dict[int, Set[int]] = dict()  # The mapping of district ID to avIds.
        self._toons2District: Dict[int, int] = dict()       # The mapping of avIds to district ID.
        self._toons2Name: Dict[int, str] = dict()           # The mapping of avIds to general stats.

        # Events
        self.air.netMessenger.accept("updateAvatar",               self, self.__handleToonUpdate)
        self.air.netMessenger.accept("avatarExitedShard",          self, self.__handleToonLeftShard)
        self.air.netMessenger.accept("shardAnnounceToonStats",     self, self.__handleUpdateShardAvatars)
        self.air.netMessenger.accept(NET_MESSENGER_REGISTER_SHARD, self, self.registerShard)

    """
    Getters
    """

    def getAllToons(self) -> Set[int]:
        """
        Returns a set containing the doId of every toon logged into the shard.

        :return: A set of doIds of toons logged into the shard.
        """
        return set(self._allToons.keys())

    def getToonsInDistrict(self, districtId: int) -> Set[int]:
        """
        Returns the set of all avIds in a given district.
        """
        return self._district2Toons.get(districtId)

    def getDistrictIdOfAvId(self, avId: int) -> Optional[int]:
        """
        Gets the district ID that a Toon is in.
        Returns None if they are not present.
        """
        return self._toons2District.get(avId, None)

    def getDistrictIdsOfAvIds(self, *avIds) -> Set[int]:
        """
        Given a list of avIds, return the set of all districts they are in.
        """
        districtSet = set()
        for avId in avIds:
            district = self.getDistrictIdOfAvId(avId)
            if district is not None:
                districtSet.add(district)
        return districtSet

    def isAvIdOnline(self, avId: int):
        """
        Determines if an avId is online.
        """
        return self.getDistrictIdOfAvId(avId) is not None

    """
    Toon Stat accessing
    """

    def getToonStats(self, avId: int, includeOffline: bool = False, callback: callable = None) -> Optional[CachedToonStats]:
        """Gets a toons stats."""
        toonStats = self._allToons.get(avId)
        if toonStats is None and includeOffline:
            return self._getCachedStats(avId, callback)
        return toonStats

    def getToonName(self, avId: int, defaultName: str = 'Toon', includeOffline: bool = False, callback: callable = None) -> Optional[str]:
        """Gets a toon's name."""
        toonStats = self.getToonStats(avId, includeOffline=True, callback=callback)
        if toonStats is None and includeOffline:
            return None
        return toonStats.getName() if toonStats else defaultName

    """
    Toon Stat caching
    """

    def __cacheOp(self, avIds: list, callback: callable, freshStats: list = None, addToCache: bool = False):
        if freshStats is None:
            freshStats = []
        self.notify.debug(f'Calling __cacheOp with avIds: {avIds}')
        self.air.dbInterface.queryObject(
            self.air.dbId,
            avIds[0],
            lambda dclass, fields: self.__cacheResp(dclass, fields, avIds, callback, addToCache, freshStats),
        )

    def __cacheResp(self, dclass, fields, avIds, callback, addToCache, freshStats):
        # Make the stats for this Toon.
        avId = avIds.pop(0)
        self.notify.debug(f'Cache Response: making avId {avId}')
        # if dclass == self.air.dclassesByName['DistributedToonUD']:
        toonStats = CachedToonStats(
            avId=avId,
            level=fields.get('setToonLevel', [0])[0],
            name=fields.get('setName', ['Toon'])[0],
            zoneId=0,
            districtId=0,
            hp=fields.get('setMaxHp', [0])[0],
            gagLevels=BattleGlobals.getGagLevels(
                experience=fields.get('setExperience', [[0] * len(BattleGlobals.Tracks)])[0],
                trackAccess=fields.get('setTrackAccess', [[0] * len(BattleGlobals.Tracks)])[0],
            ),
            gagPrestiges=fields.get('setTrackBonusLevel', [[-1] * len(BattleGlobals.Tracks)])[0],
            settings=DistributedSettingsAI.fromStruct(fields.get('setPlayerSettings', [[]])[0]),
        )
        freshStats.append(toonStats)
        if addToCache:
            self._cachedStats[avId] = toonStats

        # Handle callback if necessary.
        if avIds:
            # Do another query.
            self.notify.debug(f'Cache Response: made avId {avId}. running again with {avIds}')
            self.__cacheOp(avIds, callback, freshStats=freshStats, addToCache=addToCache)
        elif callback:
            # We are done.
            self.notify.debug(f'Cache Response: made avId {avId}. running callback {callback}({freshStats})')
            callback(*freshStats)

    def getFreshToonStats(self, *requestedAvIds, callback: callable, addToCache: bool = False) -> None:
        """
        Requests for fresh toon stats.
        Callback is called with decomposed List[CachedToonStats].
        """
        self.__cacheOp(list(requestedAvIds), callback, addToCache=addToCache)

    def askCache(self, *requestedAvIds, callback: callable = None) -> None:
        """Requests for several avIds to be cached."""
        def cacheOp(avIds: list):
            def response(dclass, fields):
                # Make the stats for this Toon.
                avId = avIds.pop(0)
                if dclass == self.air.dclassesByName['DistributedToonUD']:
                    self._cachedStats[avId] = CachedToonStats(
                        avId=avId,
                        level=fields.get('setToonLevel', [0])[0],
                        name=fields.get('setName', ['Toon'])[0],
                        zoneId=0,
                        districtId=0,
                        hp=fields.get('setMaxHp', [0])[0],
                        gagLevels=BattleGlobals.getGagLevels(
                            experience=fields.get('setExperience', [[0] * len(BattleGlobals.Tracks)])[0],
                            trackAccess=fields.get('setTrackAccess', [[0] * len(BattleGlobals.Tracks)])[0],
                        ),
                        gagPrestiges=fields.get('setTrackBonusLevel', [-1] * len(BattleGlobals.Tracks))[0],
                        settings=DistributedSettingsAI.fromStruct(fields.get('setPlayerSettings', [[]])[0]),
                    )

                # Handle callback if necessary.
                if avIds:
                    # Do another query.
                    cacheOp(avIds)
                else:
                    # We are done.
                    callback()

            self.air.dbInterface.queryObject(
                self.air.dbId,
                avIds[0],
                response,
            )

        cacheOp(list(requestedAvIds))

    def _getCachedStats(self, avId: int, callback: callable = None) -> Optional[CachedToonStats]:
        """Returns cached stats. Pulls from offline Toons."""
        cachedStats = self._cachedStats.get(avId)
        if cachedStats is None:
            if callback is not None:
                self.askCache(avId, callback=callback)
            return None
        return cachedStats

    """
    Toon Register Handling.
    These methods help ensure that the UD is always cognizant
    of all online players and where they are located.
    """

    def __handleToonUpdate(self, toonStats: CachedToonStats):
        """
        Fired when a toon joins the shard.

        :param av: The toon that joined the shard.
        """
        avId = toonStats.getAvId()
        self._allToons[avId] = toonStats
        if avId in self._cachedStats:
            del self._cachedStats[avId]
        self.__addToonToDistrict(avId, toonStats.getDistrictId())
        self.notify.debug(f"Toon {avId} joined shard {toonStats.getDistrictId()}")

        # Send local UD messenger.
        messenger.send('UD_ToonJoined', [avId])

    def __handleToonLeftShard(self, avId: int, districtId: int):
        """
        Fired when a toon leaves the shard.

        :param av: The toon that left the shard.
        """
        if avId in self._allToons:
            toonStats = self._allToons.pop(avId)
            self._cachedStats[avId] = toonStats
        self.__removeToonFromDistrict(avId, districtId)
        self.notify.debug(f"Toon {avId} left shard {districtId}")

        # Send local UD messenger.
        messenger.send('UD_ToonLeft', [avId])

    def __addToonToDistrict(self, avId: int, districtId: int):
        """Adds a Toon to the District map."""
        # Make sure the Toon is only recognized in one district.
        self.__removeToonFromDistrict(avId, districtId)

        # Add them to the district->toon mappings.
        districtSet = self._district2Toons.get(districtId, set())
        if not districtSet:
            self._district2Toons[districtId] = districtSet
        districtSet.add(avId)

        # Also add them to the toon->district mappings.
        self._toons2District[avId] = districtId

    def __removeToonFromDistrict(self, avId: int, districtId: int):
        """Removes a Toon from the District map."""
        # Find the district ID they are in, remove them from the toons->district map.
        if avId in self._toons2District:
            del self._toons2District[avId]

        # Now remove them from the district->toons map.
        districtSet = self._district2Toons.get(districtId, None)
        if districtSet and avId in districtSet:
            districtSet.remove(avId)

            # Cleanup the district set if necessary.
            if len(districtSet) == 0:
                del self._district2Toons[districtId]

    def __cleanupDistrict(self, districtId: int):
        """Cleans up an entire district."""
        # Go through all Toons in this district and clean them up.
        for avId in self._district2Toons.get(districtId, set()).copy():
            self.__removeToonFromDistrict(avId, districtId)

    def __handleUpdateShardAvatars(self, toonStats: List[CachedToonStats]):
        """Called when a DistrictID tells us all about the avs present."""
        # Add all these avIds to the district now.
        for toonStat in toonStats:
            self.__handleToonUpdate(toonStat)

    def registerShard(self, airChannel, shardId, online):
        """Shard registration. This happens when both the district goes up and down,
        so we should always cleanup when it is sent."""
        self.__cleanupDistrict(shardId)
