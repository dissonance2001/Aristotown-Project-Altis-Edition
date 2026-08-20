import cPickle
import json
import os
import random
import re
import time

from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD
from direct.directnotify.DirectNotifyGlobal import directNotify

from toontown.club import ClubGlobals
from toontown.club import ClubShopCatalog
from toontown.club import ClubTaskGenerator
from toontown.groups.DistributedGroupManagerUD import DistributedGroupManagerUD


class DistributedToonClubUD(DistributedObjectGlobalUD):
    """Altis-native persistent Club service.

    The service is UD-owned so Clubs, invites and Club chat work across AI
    districts. Data is kept in user/clubs/clubs.json and is written after every
    mutation. This avoids Clash's PostgreSQL/Prisma dependency while retaining
    persistent Club state on an Altis server.
    """

    notify = directNotify.newCategory('DistributedToonClubUD')
    storagePath = os.path.join('user', 'clubs', 'clubs.json')

    def announceGenerate(self):
        DistributedObjectGlobalUD.announceGenerate(self)
        self.clubs = {}
        self.memberToClub = {}
        self.pendingInvites = {}
        self.nextClubId = 100000
        self._load()
        self.groupManager = DistributedGroupManagerUD(self)
        print '[Clubs] Persistent Club service loaded (%s Clubs).' % len(self.clubs)

    def groupHeartbeat(self, avName, zoneId):
        self.groupManager.heartbeat(avName, zoneId)

    def groupPrepareSuitTeleport(self, targetZone, deptIndex):
        pass

    def groupRequestState(self):
        self.groupManager.requestState()

    def groupRequestBrowse(self):
        self.groupManager.requestBrowse()

    def groupRequestCreate(self, activity, location, zoneId, maxSize, published, avName):
        self.groupManager.requestCreate(activity, location, zoneId, maxSize, published, avName)

    def groupRequestJoin(self, groupId, avName):
        self.groupManager.requestJoin(groupId, avName)

    def groupRequestLeave(self):
        self.groupManager.requestLeave()

    def groupRequestDisband(self):
        self.groupManager.requestDisband()

    def groupRequestKick(self, avId):
        self.groupManager.requestKick(avId)

    def groupRequestMassTeleport(self):
        self.groupManager.requestMassTeleport()

    def groupRequestMassTeleportReady(self, token):
        self.groupManager.requestMassTeleportReady(token)

    def groupRequestPublish(self, published):
        self.groupManager.requestPublish(published)

    def groupRequestInvite(self, avId, avName):
        self.groupManager.requestInvite(avId, avName)

    def groupRespondToInvite(self, groupId, accept, avName):
        self.groupManager.respondToInvite(groupId, accept, avName)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def _load(self):
        try:
            if not os.path.isfile(self.storagePath):
                return
            handle = open(self.storagePath, 'r')
            payload = json.load(handle)
            handle.close()
            self.clubs = payload.get('clubs', {})
            self.nextClubId = int(payload.get('nextClubId', self.nextClubId))
            self.pendingInvites = payload.get('pendingInvites', {})
            self._rebuildMemberMap()
            self._normaliseLoadedData()
            # Persist derived level/task migration immediately so the JSON file
            # no longer carries values from older Altis Club builds.
            self._save()
        except Exception as error:
            self.notify.warning('Could not load Club storage: %s' % error)
            self.clubs = {}
            self.memberToClub = {}
            self.pendingInvites = {}

    def _save(self):
        try:
            directory = os.path.dirname(self.storagePath)
            if not os.path.isdir(directory):
                os.makedirs(directory)
            temporary = self.storagePath + '.tmp'
            handle = open(temporary, 'w')
            json.dump({
                'nextClubId': self.nextClubId,
                'clubs': self.clubs,
                'pendingInvites': self.pendingInvites,
            }, handle, indent=2, sort_keys=True)
            handle.close()
            if os.path.isfile(self.storagePath):
                os.remove(self.storagePath)
            os.rename(temporary, self.storagePath)
        except Exception as error:
            self.notify.warning('Could not save Club storage: %s' % error)

    def _normaliseLoadedData(self):
        for club in self.clubs.values():
            club.setdefault('members', [])
            club.setdefault('coins', 0)
            club.setdefault('jellybeans', 0)
            club['experience'] = max(0, int(club.get('experience', 0)))

            # Build 46 accidentally awarded current-denomination Club Coins as
            # Club XP one-for-one. Clash multiplied Club Coins by 100, but XP
            # remained at the old denomination. Correct affected saved Clubs
            # exactly once and preserve the sub-XP remainder for future gains.
            xpVersion = int(club.get('clubXpDenominationVersion', 0))
            if xpVersion < ClubGlobals.CLUB_XP_DENOMINATION_VERSION:
                oldExperience = club['experience']
                club['experience'] = oldExperience // ClubGlobals.CLUB_COIN_XP_DIVISOR
                club['experienceCoinRemainder'] = (
                    oldExperience % ClubGlobals.CLUB_COIN_XP_DIVISOR)
                club['clubXpDenominationVersion'] = (
                    ClubGlobals.CLUB_XP_DENOMINATION_VERSION)
            else:
                club['experienceCoinRemainder'] = max(
                    0, int(club.get('experienceCoinRemainder', 0)))
                club['experienceCoinRemainder'] %= (
                    ClubGlobals.CLUB_COIN_XP_DIVISOR)

            # Level is derived data. Recalculate it on every load so Clubs
            # created under older Altis curves migrate to Clash's current one.
            club['level'] = ClubGlobals.getLevelForExperience(club['experience'])
            club.setdefault('motd', 'Welcome to our Club!')
            club.setdefault('icon', {'iconId': 0, 'backgroundId': 0, 'themeId': 0, 'backgroundColorId': 0})
            club.setdefault('itemsOwned', [0])
            club.setdefault('boosters', {})
            club.setdefault('tasks', [])
            club['tasks'] = ClubTaskGenerator.makeClubTasks(club)
            club.setdefault('logs', [])
            club.setdefault('created', int(time.time()))
            defaultPermissions = ClubGlobals.getDefaultClubPermissions()
            savedPermissions = club.setdefault('permissions', defaultPermissions)
            for rankKey, rankDefaults in defaultPermissions.items():
                rankPermissions = savedPermissions.setdefault(rankKey, {})
                for permission, enabled in rankDefaults.items():
                    rankPermissions.setdefault(permission, enabled)

    def _rebuildMemberMap(self):
        self.memberToClub = {}
        for clubId, club in self.clubs.items():
            for member in club.get('members', []):
                self.memberToClub[str(int(member.get('avId', 0)))] = str(clubId)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _sender(self):
        return int(self.air.getAvatarIdFromSender())

    def _clubForAv(self, avId):
        clubId = self.memberToClub.get(str(int(avId)))
        return self.clubs.get(str(clubId)) if clubId is not None else None

    def _clubIdForAv(self, avId):
        clubId = self.memberToClub.get(str(int(avId)))
        return int(clubId) if clubId is not None else 0

    def _member(self, club, avId):
        for member in club.get('members', []):
            if int(member.get('avId', 0)) == int(avId):
                return member
        return None

    def _rank(self, club, avId):
        member = self._member(club, avId)
        return int(member.get('rank', ClubGlobals.RANK_MEMBER)) if member else -1

    def _hasPermission(self, club, avId, permission):
        rank = self._rank(club, avId)
        if rank == ClubGlobals.RANK_LEADER:
            return True
        if permission in ClubGlobals.EDITABLE_PERMISSION_KEYS:
            permissions = club.get('permissions', {})
            rankPermissions = permissions.get(str(rank), permissions.get(rank, {}))
            if permission in rankPermissions:
                return bool(rankPermissions.get(permission))
        return ClubGlobals.hasPermission(rank, permission)

    def _notify(self, avId, notifyType, message):
        self.sendUpdateToAvatarId(int(avId), 'receiveNotification', [int(notifyType), str(message)])

    def _makeClubNametag(self, club):
        if not club:
            return ''
        name = str(club.get('name', '') or '')
        if not name:
            return ''
        icon = club.get('icon', {}) or {}
        try:
            themeId = int(icon.get('themeId', 0) or 0)
        except (TypeError, ValueError):
            themeId = 0
        return '\1AltisClubNametagColor-%s\1%s\2' % (themeId, name)

    def _syncMemberNametag(self, avId):
        """Persist and broadcast the member's current Club nametag."""
        avId = int(avId)
        if avId <= 0:
            return

        def queried(dclass, fields):
            if not dclass:
                self.notify.warning(
                    'Could not find Toon %s while syncing Club nametag.' % avId)
                return

            # Resolve the Club again inside the asynchronous callback. This
            # prevents a stale join/leave callback from restoring an old tag.
            tag = self._makeClubNametag(self._clubForAv(avId))
            updates = {'setToonTag': [tag]}
            try:
                self.air.dbInterface.updateObject(
                    self.air.dbId, avId, dclass, updates)

                # The field is required+broadcast. Sending the update through
                # the live Toon object makes every client in its current zone
                # receive it immediately; the DB write covers later generates.
                dg = dclass.aiFormatUpdate(
                    'setToonTag', avId, avId, self.air.ourChannel, [tag])
                self.air.send(dg)
            except Exception as error:
                self.notify.warning(
                    'Could not sync Club nametag for Toon %s: %s' %
                    (avId, error))

        try:
            self.air.dbInterface.queryObject(self.air.dbId, avId, queried)
        except Exception as error:
            self.notify.warning(
                'Could not query Toon %s for Club nametag: %s' %
                (avId, error))

    def _syncClubNametags(self, club):
        for member in club.get('members', []):
            self._syncMemberNametag(int(member.get('avId', 0)))

    def _getClubRewardBoosters(self, club):
        now = int(time.time())
        result = []
        if not club:
            return result
        for key, endTime in club.get('boosters', {}).items():
            try:
                endTime = int(endTime)
                if endTime <= now:
                    continue
                boosterType = ClubGlobals.getClubBoosterType(key)
                if boosterType is None:
                    continue
                result.append([int(boosterType), endTime, 0])
            except:
                pass
        return result

    def _syncMemberBoosters(self, avId):
        avId = int(avId)
        if avId <= 0:
            return

        def queried(dclass, fields):
            if not dclass:
                return
            boosters = self._getClubRewardBoosters(self._clubForAv(avId))
            data = cPickle.dumps(boosters, 1)
            try:
                current = fields.get('setClubBoosters', [None])[0]
            except:
                current = None
            try:
                if current != data:
                    self.air.dbInterface.updateObject(
                        self.air.dbId, avId, dclass,
                        {'setClubBoosters': [data]})
                dg = dclass.aiFormatUpdate(
                    'setClubBoosters', avId, avId, self.air.ourChannel, [data])
                self.air.send(dg)
            except Exception as error:
                self.notify.warning(
                    'Could not sync Club boosters for Toon %s: %s' %
                    (avId, error))

        try:
            self.air.dbInterface.queryObject(self.air.dbId, avId, queried)
        except Exception as error:
            self.notify.warning(
                'Could not query Toon %s for Club boosters: %s' %
                (avId, error))

    def _syncClubBoosters(self, club):
        for member in club.get('members', []):
            self._syncMemberBoosters(int(member.get('avId', 0)))

    def _sendState(self, avId):
        club = self._clubForAv(avId)
        if club:
            self._expireTasksAndBoosters(club)
            publicClub = dict(club)
            publicClub['logs'] = []
            payload = json.dumps(publicClub, separators=(',', ':'))
        else:
            payload = 'null'
        self._syncMemberBoosters(avId)
        self.sendUpdateToAvatarId(int(avId), 'receiveState', [payload])

    def _broadcastState(self, club):
        for member in club.get('members', []):
            self._sendState(int(member.get('avId', 0)))

    def _broadcastNotification(self, club, notifyType, message):
        for member in club.get('members', []):
            self._notify(int(member.get('avId', 0)), notifyType, message)

    def _log(self, club, logType, message, avId=0):
        club.setdefault('logs', []).insert(0, {
            'type': str(logType),
            'message': str(message),
            'avId': int(avId),
            'timestamp': int(time.time()),
        })
        club['logs'] = club['logs'][:250]

    def _cleanName(self, name):
        name = re.sub(r'\s+', ' ', str(name)).strip()
        name = ''.join(ch for ch in name if ch.isalnum() or ch in " '-")
        return name[:ClubGlobals.CLUB_NAME_MAX]

    def _nameExists(self, name):
        lowered = name.lower()
        for club in self.clubs.values():
            if club.get('name', '').lower() == lowered:
                return True
        return False

    def _taskFromId(self, taskId):
        # Compatibility helper for old callers. Generated task IDs are Clash-
        # style chain IDs; legacy catalogue IDs are no longer purchasable.
        try:
            taskId = int(taskId)
        except:
            return None
        if taskId < 1000000:
            return None
        return ClubTaskGenerator.taskFromChainId(taskId)

    def _expireTasksAndBoosters(self, club):
        now = int(time.time())
        changed = False

        # Current Clash-style Club Tasks do not disappear when a timer ends.
        # Keep exactly three generated shared tasks and migrate any legacy
        # purchased task entries automatically.
        normalisedTasks = ClubTaskGenerator.makeClubTasks(club)
        if normalisedTasks != club.get('tasks', []):
            club['tasks'] = normalisedTasks
            changed = True

        for key in list(club.get('boosters', {}).keys()):
            if int(club['boosters'].get(key, 0)) <= now:
                del club['boosters'][key]
                changed = True
        if changed:
            self._save()
            self._syncClubBoosters(club)

    def _awardExperience(self, club, amount, notifyLevelUp=True):
        amount = max(0, int(amount))
        if amount <= 0:
            return
        oldLevel = int(club.get('level', 1))
        club['experience'] = int(club.get('experience', 0)) + amount
        club['level'] = ClubGlobals.getLevelForExperience(club['experience'])
        if club['level'] > oldLevel:
            self._log(club, 'level-up', 'The Club reached level %s!' % club['level'])
            if notifyLevelUp:
                self._broadcastNotification(
                    club, ClubGlobals.NOTIFY_SUCCESS,
                    'Your Club reached level %s!' % club['level'])

    def _awardExperienceFromClubCoins(self, club, coinAmount):
        """Award Clash-denomination Club XP from a Club Coin payout.

        Current Club Coins are worth one hundred times their original
        denomination. Keep the remainder so small payouts, such as fishing,
        still contribute over time instead of being discarded.
        """
        coinAmount = max(0, int(coinAmount))
        if coinAmount <= 0:
            return 0
        total = int(club.get('experienceCoinRemainder', 0)) + coinAmount
        xpAmount = total // ClubGlobals.CLUB_COIN_XP_DIVISOR
        club['experienceCoinRemainder'] = (
            total % ClubGlobals.CLUB_COIN_XP_DIVISOR)
        club['clubXpDenominationVersion'] = (
            ClubGlobals.CLUB_XP_DENOMINATION_VERSION)
        self._awardExperience(club, xpAmount)
        return xpAmount

    def _deductCreationCost(self, avId, callback):
        """Validate and deduct the 20,000 jellybean creation cost from Astron."""
        def queried(dclass, fields):
            if not dclass or 'setMoney' not in fields or 'setBankMoney' not in fields:
                callback(False)
                return
            wallet = int(fields.get('setMoney', [0])[0])
            bank = int(fields.get('setBankMoney', [0])[0])
            total = wallet + bank
            if total < ClubGlobals.CLUB_CREATION_COST:
                callback(False)
                return
            remaining = ClubGlobals.CLUB_CREATION_COST
            takeWallet = min(wallet, remaining)
            wallet -= takeWallet
            remaining -= takeWallet
            bank -= remaining
            updates = {'setMoney': [wallet], 'setBankMoney': [bank]}
            try:
                self.air.dbInterface.updateObject(self.air.dbId, avId, dclass, updates)
                # Update an online Toon immediately as well.
                for fieldName, args in updates.items():
                    dg = dclass.aiFormatUpdate(fieldName, avId, avId, self.air.ourChannel, args)
                    self.air.send(dg)
                callback(True)
            except Exception as error:
                self.notify.warning('Could not deduct Club creation cost: %s' % error)
                callback(False)
        try:
            self.air.dbInterface.queryObject(self.air.dbId, int(avId), queried)
        except Exception as error:
            self.notify.warning('Could not query Toon for Club creation: %s' % error)
            callback(False)

    def _deductJellybeans(self, avId, amount, callback):
        """Validate and deduct Jellybeans from an Astron Toon object."""
        amount = max(0, int(amount))

        def queried(dclass, fields):
            if not dclass or 'setMoney' not in fields or 'setBankMoney' not in fields:
                callback(False)
                return
            wallet = int(fields.get('setMoney', [0])[0])
            bank = int(fields.get('setBankMoney', [0])[0])
            if wallet + bank < amount:
                callback(False)
                return
            remaining = amount
            takeWallet = min(wallet, remaining)
            wallet -= takeWallet
            remaining -= takeWallet
            bank -= remaining
            updates = {'setMoney': [wallet], 'setBankMoney': [bank]}
            try:
                self.air.dbInterface.updateObject(self.air.dbId, int(avId), dclass, updates)
                for fieldName, args in updates.items():
                    dg = dclass.aiFormatUpdate(
                        fieldName, int(avId), int(avId), self.air.ourChannel, args)
                    self.air.send(dg)
                callback(True)
            except Exception as error:
                self.notify.warning('Could not deduct Club Shop Jellybeans: %s' % error)
                callback(False)

        try:
            self.air.dbInterface.queryObject(self.air.dbId, int(avId), queried)
        except Exception as error:
            self.notify.warning('Could not query Toon for Club Shop purchase: %s' % error)
            callback(False)

    def _boosterCategoryForKey(self, key):
        """Resolve new item-ID Booster keys and legacy category keys."""
        try:
            itemId = int(key)
        except:
            return str(key)
        if 2100 <= itemId < 2200:
            itemId -= 100
        entry = ClubShopCatalog.SHOP_ITEMS.get(itemId)
        if entry and str(entry[1]).startswith('booster-'):
            return str(entry[1]).split('-', 1)[1]
        return str(key)

    def _hasActiveBooster(self, club, categories):
        now = int(time.time())
        for key, endTime in club.get('boosters', {}).items():
            if int(endTime) <= now:
                continue
            if self._boosterCategoryForKey(key) in categories:
                return True
        return False

    def _hasActiveClubBoosterType(self, club, boosterTypes):
        now = int(time.time())
        for key, endTime in club.get('boosters', {}).items():
            if int(endTime) <= now:
                continue
            if ClubGlobals.getClubBoosterType(key) in boosterTypes:
                return True
        return False

    def _progressMultiplier(self, club, progressType):
        if self._hasActiveClubBoosterType(club, (60,)):
            return 2
        if progressType in ('cogs', 'bosses') and self._hasActiveBooster(
                club, ('merit',)):
            return 2
        if progressType in ('trolley', 'fish', 'buildings') and (
                self._hasActiveBooster(club, ('activity',))):
            return 2
        if progressType == 'cogs' and self._hasActiveBooster(
                club, ('gag',)):
            return 2
        return 1

    def _coinMultiplier(self, club):
        return 2 if self._hasActiveClubBoosterType(club, (60,)) else 1

    # ------------------------------------------------------------------
    # Client requests
    # ------------------------------------------------------------------
    def requestState(self):
        avId = self._sender()
        # Repairs existing Build 84/87 members as soon as they log in and also
        # clears a stale DB tag from a Toon who is no longer in a Club.
        self._syncMemberNametag(avId)
        self._sendState(avId)
        for invite in self.pendingInvites.get(str(avId), []):
            self.sendUpdateToAvatarId(avId, 'receiveInvite', [
                int(invite['inviterAvId']), invite['inviterName'],
                int(invite['clubId']), invite['clubName']])

    def requestCreateClub(self, name, iconId, backgroundId, themeId, backgroundColorId, avName):
        avId = self._sender()
        if self._clubForAv(avId):
            self._notify(avId, ClubGlobals.NOTIFY_ERROR, 'You are already in a Club.')
            return
        cleanName = self._cleanName(name)
        if len(cleanName) < ClubGlobals.CLUB_NAME_MIN:
            self._notify(avId, ClubGlobals.NOTIFY_ERROR, 'That Club name is too short.')
            return
        if self._nameExists(cleanName):
            self._notify(avId, ClubGlobals.NOTIFY_ERROR, 'That Club name is already being used.')
            return

        def finish(paid):
            if not paid:
                self._notify(avId, ClubGlobals.NOTIFY_ERROR,
                             'You need 20,000 jellybeans to create a Club.')
                return
            clubId = self.nextClubId
            self.nextClubId += 1
            club = {
                'id': clubId,
                'name': cleanName,
                'ownerId': avId,
                'motd': 'Welcome to %s!' % cleanName,
                'created': int(time.time()),
                'icon': {
                    'iconId': int(iconId),
                    'backgroundId': int(backgroundId),
                    'themeId': int(themeId),
                    'backgroundColorId': int(backgroundColorId),
                },
                'members': [{
                    'avId': avId,
                    'name': str(avName),
                    'rank': ClubGlobals.RANK_LEADER,
                    'joined': int(time.time()),
                }],
                'coins': 0,
                'jellybeans': 0,
                'experience': 0,
                'experienceCoinRemainder': 0,
                'clubXpDenominationVersion': ClubGlobals.CLUB_XP_DENOMINATION_VERSION,
                'level': 1,
                'itemsOwned': [0],
                'boosters': {},
                'tasks': [],
                'logs': [],
                'permissions': ClubGlobals.getDefaultClubPermissions(),
            }
            club['tasks'] = ClubTaskGenerator.makeClubTasks(club)
            self.clubs[str(clubId)] = club
            self.memberToClub[str(avId)] = str(clubId)
            self._log(club, 'creation', '%s created the Club.' % avName, avId)
            self._save()
            self._syncMemberNametag(avId)
            self._sendState(avId)
            self._notify(avId, ClubGlobals.NOTIFY_SUCCESS, 'Club created successfully!')
        self._deductCreationCost(avId, finish)

    def requestInvite(self, targetAvId, targetName):
        avId = self._sender()
        club = self._clubForAv(avId)
        if not club or not self._hasPermission(club, avId, ClubGlobals.PERMISSION_INVITE):
            self._notify(avId, ClubGlobals.NOTIFY_ERROR, 'You cannot invite Toons to this Club.')
            return
        targetAvId = int(targetAvId)
        if self._clubForAv(targetAvId):
            self._notify(avId, ClubGlobals.NOTIFY_ERROR, 'That Toon is already in a Club.')
            return
        if len(club.get('members', [])) >= ClubGlobals.CLUB_MAX_MEMBERS:
            self._notify(avId, ClubGlobals.NOTIFY_ERROR, 'Your Club is full.')
            return
        inviter = self._member(club, avId) or {}
        invite = {
            'inviterAvId': avId,
            'inviterName': inviter.get('name', 'A Toon'),
            'clubId': int(club['id']),
            'clubName': club['name'],
            'targetName': str(targetName),
        }
        key = str(targetAvId)
        self.pendingInvites.setdefault(key, [])
        self.pendingInvites[key] = [entry for entry in self.pendingInvites[key]
                                    if int(entry.get('clubId', 0)) != int(club['id'])]
        self.pendingInvites[key].append(invite)
        self._save()
        self.sendUpdateToAvatarId(targetAvId, 'receiveInvite', [
            avId, invite['inviterName'], int(club['id']), club['name']])
        self._notify(avId, ClubGlobals.NOTIFY_INVITE_SENT, 'Club invite sent.')

    def respondToInvite(self, clubId, accept, avName):
        avId = self._sender()
        entries = self.pendingInvites.get(str(avId), [])
        matching = None
        for entry in entries:
            if int(entry.get('clubId', 0)) == int(clubId):
                matching = entry
                break
        if not matching:
            self._notify(avId, ClubGlobals.NOTIFY_ERROR, 'That Club invite is no longer valid.')
            return
        entries.remove(matching)
        if not entries:
            self.pendingInvites.pop(str(avId), None)
        if not accept:
            self._save()
            self._notify(avId, ClubGlobals.NOTIFY_INFO, 'Club invite declined.')
            return
        if self._clubForAv(avId):
            self._notify(avId, ClubGlobals.NOTIFY_ERROR, 'You are already in a Club.')
            return
        club = self.clubs.get(str(int(clubId)))
        if not club or len(club.get('members', [])) >= ClubGlobals.CLUB_MAX_MEMBERS:
            self._notify(avId, ClubGlobals.NOTIFY_ERROR, 'That Club is no longer available.')
            return
        member = {'avId': avId, 'name': str(avName), 'rank': ClubGlobals.RANK_MEMBER,
                  'joined': int(time.time())}
        club['members'].append(member)
        self.memberToClub[str(avId)] = str(int(clubId))
        self._log(club, 'member-joined', '%s joined the Club.' % avName, avId)
        self._save()
        self._syncMemberNametag(avId)
        self._broadcastState(club)
        self._broadcastNotification(club, ClubGlobals.NOTIFY_MEMBER_JOINED,
                                    '%s joined the Club.' % avName)

    def requestLeave(self):
        avId = self._sender()
        club = self._clubForAv(avId)
        if not club:
            return
        member = self._member(club, avId)
        name = member.get('name', 'A Toon') if member else 'A Toon'
        if int(club.get('ownerId', 0)) == avId and len(club.get('members', [])) > 1:
            self._notify(avId, ClubGlobals.NOTIFY_ERROR,
                         'Transfer Club ownership before leaving the Club.')
            return
        club['members'] = [entry for entry in club.get('members', [])
                           if int(entry.get('avId', 0)) != avId]
        self.memberToClub.pop(str(avId), None)
        if not club['members']:
            self.clubs.pop(str(club['id']), None)
        else:
            if int(club.get('ownerId', 0)) == avId:
                successor = sorted(club['members'],
                                   key=lambda entry: (-int(entry.get('rank', 0)), int(entry.get('joined', 0))))[0]
                successor['rank'] = ClubGlobals.RANK_LEADER
                club['ownerId'] = int(successor['avId'])
                self._log(club, 'rank-change', '%s became the Club leader.' % successor.get('name', 'A Toon'),
                          successor['avId'])
            self._log(club, 'member-left', '%s left the Club.' % name, avId)
        self._save()
        self._syncMemberNametag(avId)
        self._sendState(avId)
        if club.get('members'):
            self._broadcastState(club)
            self._broadcastNotification(club, ClubGlobals.NOTIFY_MEMBER_LEFT,
                                        '%s left the Club.' % name)

    def requestKick(self, targetAvId):
        avId = self._sender()
        club = self._clubForAv(avId)
        targetAvId = int(targetAvId)
        if not club or not self._hasPermission(club, avId, ClubGlobals.PERMISSION_KICK):
            self._notify(avId, ClubGlobals.NOTIFY_ERROR, 'You cannot remove Club members.')
            return
        if targetAvId == avId or targetAvId == int(club.get('ownerId', 0)):
            self._notify(avId, ClubGlobals.NOTIFY_ERROR, 'That Toon cannot be removed.')
            return
        target = self._member(club, targetAvId)
        if not target or self._rank(club, targetAvId) >= self._rank(club, avId):
            self._notify(avId, ClubGlobals.NOTIFY_ERROR, 'You cannot remove that Club member.')
            return
        club['members'].remove(target)
        self.memberToClub.pop(str(targetAvId), None)
        name = target.get('name', 'A Toon')
        self._log(club, 'member-kicked', '%s was removed from the Club.' % name, targetAvId)
        self._save()
        self._syncMemberNametag(targetAvId)
        self._sendState(targetAvId)
        self._notify(targetAvId, ClubGlobals.NOTIFY_MEMBER_KICKED,
                     'You were removed from %s.' % club['name'])
        self._broadcastState(club)
        self._broadcastNotification(club, ClubGlobals.NOTIFY_MEMBER_KICKED,
                                    '%s was removed from the Club.' % name)

    def requestSetRank(self, targetAvId, rank):
        avId = self._sender()
        club = self._clubForAv(avId)
        targetAvId = int(targetAvId)
        rank = max(ClubGlobals.RANK_MEMBER, min(int(rank), ClubGlobals.RANK_DEPUTY))
        if not club or not self._hasPermission(club, avId, ClubGlobals.PERMISSION_RANK):
            self._notify(avId, ClubGlobals.NOTIFY_ERROR, 'Only the Club leader can change ranks.')
            return
        target = self._member(club, targetAvId)
        if not target or targetAvId == avId:
            return
        target['rank'] = rank
        self._log(club, 'rank-change', '%s is now a %s.' % (
            target.get('name', 'A Toon'), ClubGlobals.RANK_NAMES.get(rank, 'Member')), targetAvId)
        self._save()
        self._broadcastState(club)
        self._broadcastNotification(club, ClubGlobals.NOTIFY_RANK_CHANGED,
                                    '%s is now a %s.' % (target.get('name', 'A Toon'),
                                                        ClubGlobals.RANK_NAMES.get(rank, 'Member')))

    def requestTransferOwner(self, targetAvId):
        avId = self._sender()
        club = self._clubForAv(avId)
        targetAvId = int(targetAvId)
        if not club or int(club.get('ownerId', 0)) != avId:
            self._notify(avId, ClubGlobals.NOTIFY_ERROR, 'Only the Club leader can transfer ownership.')
            return
        target = self._member(club, targetAvId)
        current = self._member(club, avId)
        if not target or targetAvId == avId:
            return
        if current:
            current['rank'] = ClubGlobals.RANK_DEPUTY
        target['rank'] = ClubGlobals.RANK_LEADER
        club['ownerId'] = targetAvId
        self._log(club, 'ownership-transfer', '%s became the Club leader.' % target.get('name', 'A Toon'), targetAvId)
        self._save()
        self._broadcastState(club)
        self._broadcastNotification(club, ClubGlobals.NOTIFY_RANK_CHANGED,
                                    '%s is now the Club leader.' % target.get('name', 'A Toon'))

    def requestSetMotd(self, motd):
        avId = self._sender()
        club = self._clubForAv(avId)
        if not club or not self._hasPermission(club, avId, ClubGlobals.PERMISSION_MOTD):
            self._notify(avId, ClubGlobals.NOTIFY_ERROR, 'You cannot update the Club message.')
            return
        club['motd'] = str(motd).strip()[:ClubGlobals.CLUB_MOTD_MAX]
        self._log(club, 'motd', 'The Club message was updated.', avId)
        self._save()
        self._broadcastState(club)

    def requestSetPermission(self, rank, permissionId, enabled):
        avId = self._sender()
        club = self._clubForAv(avId)
        rank = int(rank)
        permission = ClubGlobals.getPermissionKey(permissionId)
        if not club or int(club.get('ownerId', 0)) != avId:
            self._notify(avId, ClubGlobals.NOTIFY_ERROR,
                         'Only the Club owner can change permissions.')
            return
        if rank not in (ClubGlobals.RANK_MEMBER, ClubGlobals.RANK_OFFICER,
                        ClubGlobals.RANK_DEPUTY) or not permission:
            return
        permissions = club.setdefault('permissions', ClubGlobals.getDefaultClubPermissions())
        rankPermissions = permissions.setdefault(str(rank), {})
        rankPermissions[permission] = bool(enabled)
        self._log(club, 'permission-change', '%s permission changed for %s.' % (
            ClubGlobals.PERMISSION_LABELS.get(permission, permission),
            ClubGlobals.SETTINGS_RANK_NAMES.get(rank, 'members')), avId)
        self._save()
        self._broadcastState(club)

    def requestUpdateIcon(self, iconId, backgroundId, themeId, backgroundColorId):
        avId = self._sender()

        # Compatibility transport for Jellybean donations. Altis already has
        # requestUpdateIcon in the DC schema, so this avoids adding a new DC
        # field and works with the existing distributed class definition.
        magic = ClubGlobals.DONATION_REQUEST_MAGIC
        if int(iconId) == magic and int(backgroundColorId) == magic:
            amount = (int(backgroundId) & 0xFFFF) | ((int(themeId) & 0xFFFF) << 16)
            self._requestDonateJellybeans(avId, amount)
            return

        club = self._clubForAv(avId)
        if not club or not self._hasPermission(club, avId, ClubGlobals.PERMISSION_CUSTOMIZE):
            self._notify(avId, ClubGlobals.NOTIFY_ERROR, 'You cannot customise this Club.')
            return
        club['icon'] = {
            'iconId': int(iconId), 'backgroundId': int(backgroundId),
            'themeId': int(themeId), 'backgroundColorId': int(backgroundColorId),
        }
        self._log(club, 'customization', 'The Club appearance was updated.', avId)
        self._save()
        self._syncClubNametags(club)
        self._broadcastState(club)

    def _sendDonationResult(self, avId, success, amount, message):
        payload = json.dumps({
            'success': bool(success),
            'amount': int(amount),
            'message': str(message),
        }, separators=(',', ':'))
        self.sendUpdateToAvatarId(
            int(avId), 'receiveNotification',
            [ClubGlobals.NOTIFY_DONATION_RESULT, payload])

    def _requestDonateJellybeans(self, avId, amount):
        avId = int(avId)
        club = self._clubForAv(avId)
        amount = max(0, int(amount))

        if not club:
            self._sendDonationResult(
                avId, False, amount, 'You are not currently in a Club.')
            return
        if amount < 1:
            self._sendDonationResult(
                avId, False, amount, 'Choose at least one Jellybean to donate.')
            return

        current = int(club.get('jellybeans', 0))
        if current >= ClubGlobals.CLUB_MAX_JELLYBEANS:
            self._sendDonationResult(
                avId, False, amount, 'Your Club Jellybean Bank is full.')
            return
        if current + amount > ClubGlobals.CLUB_MAX_JELLYBEANS:
            self._sendDonationResult(
                avId, False, amount,
                'The Club Jellybean Bank cannot hold that many Jellybeans.')
            return

        def finishDonation(paid):
            if not paid:
                self._sendDonationResult(
                    avId, False, amount,
                    'You do not have enough Jellybeans to donate that amount.')
                return

            club['jellybeans'] = int(club.get('jellybeans', 0)) + amount
            member = self._member(club, avId) or {}
            name = member.get('name', 'A Toon')
            plural = '' if amount == 1 else 's'
            message = '%s donated %s Jellybean%s to the Club.' % (
                name, format(amount, ','), plural)
            self._log(club, 'jellybean-donation', message, avId)
            self._save()
            self._broadcastState(club)
            self._broadcastNotification(
                club, ClubGlobals.NOTIFY_SUCCESS, message)
            self._sendDonationResult(
                avId, True, amount,
                'You donated %s Jellybean%s to your Club.' % (
                    format(amount, ','), plural))

        self._deductJellybeans(avId, amount, finishDonation)

    def requestPurchaseItem(self, itemId):
        avId = self._sender()
        club = self._clubForAv(avId)
        itemId = int(itemId)
        item = ClubGlobals.SHOP_ITEMS.get(itemId)
        if not club or not self._hasPermission(
                club, avId, ClubGlobals.PERMISSION_PURCHASE_ITEMS):
            self._notify(
                avId, ClubGlobals.NOTIFY_ERROR,
                'You cannot purchase Club items.')
            return
        if not item:
            self._notify(
                avId, ClubGlobals.NOTIFY_ERROR,
                'That Club item does not exist.')
            return

        name, category, cost, requiredLevel, payload, currency, description = (
            ClubGlobals.unpackShopItem(item)
        )
        cost = int(cost)
        requiredLevel = int(requiredLevel)

        if int(club.get('level', 1)) < requiredLevel:
            self._notify(
                avId, ClubGlobals.NOTIFY_ERROR,
                'Your Club level is too low for that item.')
            return

        isBooster = str(category).startswith('booster-')
        if not isBooster and itemId in club.setdefault('itemsOwned', []):
            self._notify(
                avId, ClubGlobals.NOTIFY_INFO,
                'Your Club already owns %s.' % name)
            return

        def finishPurchase(paid):
            if not paid:
                if currency == ClubGlobals.CURRENCY_JELLYBEANS:
                    message = 'Your Club does not have enough Jellybeans for that item.'
                else:
                    message = 'Your Club does not have enough Club Coins.'
                self._notify(avId, ClubGlobals.NOTIFY_ERROR, message)
                return

            if isBooster:
                # Preserve the exact Booster identity so the Social Panel can
                # display its real boosters.bam icon. Jellybean duplicates use
                # the same normalized key as their Club Coin counterpart.
                boosterItemId = int(itemId)
                if 2100 <= boosterItemId < 2200:
                    boosterItemId -= 100
                boosterKey = str(boosterItemId)
                boosters = club.setdefault('boosters', {})
                startTime = max(
                    int(time.time()), int(boosters.get(boosterKey, 0)))
                boosters[boosterKey] = startTime + int(payload)
                self._log(club, 'booster', '%s was activated.' % name, avId)
                noticeType = ClubGlobals.NOTIFY_BOOSTER_STARTED
            else:
                club.setdefault('itemsOwned', []).append(itemId)
                self._log(club, 'item-purchased', '%s was purchased.' % name, avId)
                noticeType = ClubGlobals.NOTIFY_ITEM_PURCHASED

            self._save()
            self._broadcastState(club)
            self._broadcastNotification(
                club, noticeType, '%s was purchased.' % name)

        if currency == ClubGlobals.CURRENCY_JELLYBEANS:
            if int(club.get('jellybeans', 0)) < cost:
                finishPurchase(False)
                return
            club['jellybeans'] = int(club.get('jellybeans', 0)) - cost
            finishPurchase(True)
            return

        if int(club.get('coins', 0)) < cost:
            finishPurchase(False)
            return
        club['coins'] -= cost
        finishPurchase(True)

    def requestStartTask(self, taskId):
        # Club Tasks are assigned automatically. Keep this legacy DC entry as
        # a harmless compatibility endpoint so old clients cannot purchase one.
        avId = self._sender()
        club = self._clubForAv(avId)
        if not club:
            return
        self._notify(
            avId, ClubGlobals.NOTIFY_INFO,
            'Club Tasks are assigned automatically when a slot is available.')
        self._expireTasksAndBoosters(club)
        self._broadcastState(club)

    def requestRerollTask(self, slot):
        avId = self._sender()
        club = self._clubForAv(avId)
        if not club or not self._hasPermission(
                club, avId, ClubGlobals.PERMISSION_PURCHASE_TASKS):
            self._notify(
                avId, ClubGlobals.NOTIFY_ERROR,
                "You cannot reroll this Club's tasks.")
            return

        self._expireTasksAndBoosters(club)
        slot = int(slot)
        tasks = club.get('tasks', [])
        if slot < 0 or slot >= ClubGlobals.MAX_ACTIVE_TASKS:
            return
        if slot >= len(tasks):
            club['tasks'] = ClubTaskGenerator.makeClubTasks(club)
            tasks = club['tasks']

        oldTask = tasks[slot]
        rerollCost = int(oldTask.get(
            'rerollCost', ClubGlobals.getTaskRerollCost(oldTask)))
        if int(club.get('jellybeans', 0)) < rerollCost:
            self._notify(
                avId, ClubGlobals.NOTIFY_ERROR,
                'Your Club needs %s Jellybeans to reroll that task.' %
                format(rerollCost, ','))
            return

        oldName = oldTask.get('name', 'Club Task')
        club['jellybeans'] = int(club.get('jellybeans', 0)) - rerollCost
        club['tasks'] = ClubTaskGenerator.makeClubTasks(
            club, rerollIndices=[slot])
        newName = club['tasks'][slot].get('name', 'Club Task')
        self._log(
            club, 'task-rerolled',
            '%s was rerolled into %s for %s Jellybeans.' % (
                oldName, newName, format(rerollCost, ',')), avId)
        self._save()
        self._broadcastState(club)
        self._broadcastNotification(
            club, ClubGlobals.NOTIFY_INFO,
            'A Club Task was rerolled: %s' % newName)

    def requestLogs(self, page):
        avId = self._sender()
        club = self._clubForAv(avId)
        if not club:
            self.sendUpdateToAvatarId(avId, 'receiveLogs', ['[]'])
            return
        page = max(0, int(page))
        logs = club.get('logs', [])[page * 25:(page + 1) * 25]
        self.sendUpdateToAvatarId(avId, 'receiveLogs', [json.dumps(logs, separators=(',', ':'))])

    def sendClubChat(self, message):
        avId = self._sender()
        club = self._clubForAv(avId)
        if not club or not self._hasPermission(club, avId, ClubGlobals.PERMISSION_CHAT):
            self._notify(avId, ClubGlobals.NOTIFY_ERROR, 'You cannot use Club chat.')
            return
        member = self._member(club, avId) or {}
        senderName = member.get('name', 'A Toon')
        message = str(message).strip()[:ClubGlobals.CLUB_CHAT_MAX]
        if not message:
            return
        for target in club.get('members', []):
            self.sendUpdateToAvatarId(int(target.get('avId', 0)), 'receiveClubChat',
                                      [avId, senderName, message])

    # ------------------------------------------------------------------
    # AI reports for Club tasks and rewards
    # ------------------------------------------------------------------
    def reportProgressAI(self, avId, progressType, amount):
        try:
            avId = int(avId)
            progressType = str(progressType)
            amount = int(amount)
        except:
            return

        # Magic Word mutations travel through this existing DC field to avoid
        # requiring new distributed methods or changing the active DC hash.
        if progressType == '__magic_coin__':
            self.magicWordAddCoinsAI(avId, amount)
            return
        if progressType == '__magic_level__':
            self.magicWordSetLevelAI(avId, amount)
            return

        if progressType not in ClubTaskGenerator.OBJECTIVE_TYPES:
            self.notify.warning(
                'Ignored invalid Club Task progress type from AI: %s' %
                progressType)
            return
        self._applyProgress(avId, progressType, amount)

    def reportClubCoinsAI(self, avId, amount):
        try:
            avId = int(avId)
            amount = int(amount)
        except:
            return
        if avId <= 0 or amount <= 0:
            return

        club = self._clubForAv(avId)
        if not club:
            return

        # Existing activity callers report 1 reward unit per fish and
        # 10 reward units per completed trolley game. Convert each unit into
        # 10 Club Coins and 1 Club XP. Universal Boosters still double both.
        multiplier = self._coinMultiplier(club)
        coinAmount = (
            amount * ClubGlobals.CLUB_ACTIVITY_COIN_MULTIPLIER * multiplier)
        xpAmount = (
            amount * ClubGlobals.CLUB_ACTIVITY_XP_MULTIPLIER * multiplier)

        club['coins'] = int(club.get('coins', 0)) + coinAmount
        self._awardExperience(
            club, xpAmount, notifyLevelUp=False)
        self._save()
        self._broadcastState(club)

        # Trolley and fishing activity rewards are intentionally silent.

    def magicWordAddCoinsAI(self, avId, amount):
        """Add Club Coins directly without XP, logs, or notifications."""
        try:
            avId = int(avId)
            amount = int(amount)
        except:
            return
        if avId <= 0 or amount <= 0:
            return

        club = self._clubForAv(avId)
        if not club:
            return

        club['coins'] = int(club.get('coins', 0)) + amount
        self._save()
        self._broadcastState(club)

    def magicWordSetLevelAI(self, avId, level):
        """Set a Club to the beginning of an exact level silently."""
        try:
            avId = int(avId)
            level = int(level)
        except:
            return
        if avId <= 0 or level < 1:
            return

        # Keep accidental inputs from causing an excessive XP-curve loop.
        level = min(level, 10000)
        club = self._clubForAv(avId)
        if not club:
            return

        club['experience'] = ClubGlobals.getExperienceForLevel(level)
        club['level'] = level
        club['experienceCoinRemainder'] = 0
        club['clubXpDenominationVersion'] = (
            ClubGlobals.CLUB_XP_DENOMINATION_VERSION)
        self._save()
        self._broadcastState(club)

    def _applyProgress(self, avId, progressType, amount):
        if progressType not in ClubTaskGenerator.OBJECTIVE_TYPES:
            return
        club = self._clubForAv(avId)
        if not club or amount <= 0:
            return

        self._expireTasksAndBoosters(club)
        amount *= self._progressMultiplier(club, progressType)
        changed = False
        completedIndices = []
        completedNames = []
        totalReward = 0
        totalTaskXp = 0

        for index, task in enumerate(club.get('tasks', [])):
            if task.get('progressType') != progressType:
                continue
            goal = max(1, int(task.get('goal', 1)))
            task['progress'] = min(
                goal, int(task.get('progress', 0)) + amount)
            changed = True
            if task['progress'] >= goal:
                completedIndices.append(index)
                completedNames.append(task.get('name', 'Club Task'))
                totalReward += int(task.get('rewardCoins', 0))
                totalTaskXp += max(0, int(task.get('rewardExp', 0)))

        if completedIndices:
            club['coins'] = int(club.get('coins', 0)) + totalReward
            self._awardExperience(club, totalTaskXp)
            taskXp = totalTaskXp
            for taskName in completedNames:
                self._log(
                    club, 'task-complete',
                    '%s was completed.' % taskName, avId)
            # Replace every completed slot immediately. Every Club member sees
            # the same new task in the same slot on the next state update.
            club['tasks'] = ClubTaskGenerator.makeClubTasks(
                club, rerollIndices=completedIndices)

        if changed:
            self._save()
            self._broadcastState(club)
            if completedIndices:
                self._broadcastNotification(
                    club, ClubGlobals.NOTIFY_TASK_COMPLETE,
                    'Club Task complete! +%s CC, +%s XP. A new task is ready.' %
                    (totalReward, taskXp))
