from __future__ import absolute_import
import json
import time

from direct.directnotify.DirectNotifyGlobal import directNotify

from toontown.groups import GroupGlobals
from toontown.toonbase import ToontownGlobals


class DistributedGroupManagerUD(object):
    notify = directNotify.newCategory('DistributedGroupManagerUD')

    def __init__(self, transport):
        self.transport = transport
        self.air = transport.air
        self.groups = {}
        self.memberToGroup = {}
        self.pendingInvites = {}
        self.lastSeen = {}
        self.nextGroupId = 200000
        self.massTeleportSessions = {}
        self.nextMassTeleportToken = 1

    def _sender(self):
        return int(self.air.getAvatarIdFromSender())

    def _cleanText(self, value, length):
        value = str(value).replace('\r', ' ').replace('\n', ' ').strip()
        while '  ' in value:
            value = value.replace('  ', ' ')
        return value[:length]

    def _parseIdentity(self, value):
        value = str(value)
        parts = value.split('\x1f', 1)
        name = self._cleanText(parts[0], 48)
        shardId = 0
        if len(parts) > 1:
            try:
                shardId = int(parts[1])
            except:
                shardId = 0
        return name, shardId

    def _notify(self, avId, notifyType, message):
        self.transport.sendUpdateToAvatarId(int(avId), 'groupReceiveNotification',
                                  [int(notifyType), str(message)[:256]])

    def _groupForAv(self, avId):
        groupId = self.memberToGroup.get(int(avId))
        return self.groups.get(groupId)

    def _publicGroup(self, group):
        return {
            'id': int(group['id']),
            'activity': group['activity'],
            'location': group['location'],
            'zoneId': int(group.get('zoneId', 0)),
            'shardId': int(group.get('shardId', 0)),
            'ownerId': int(group['ownerId']),
            'ownerName': group['ownerName'],
            'maxSize': int(group['maxSize']),
            'published': bool(group['published']),
            'members': list(group['members']),
            'created': int(group['created']),
        }

    def _findMember(self, group, avId):
        avId = int(avId)
        for member in group.get('members', []):
            if int(member.get('avId', 0)) == avId:
                return member
        return None

    def _removePendingInvite(self, targetAvId, groupId):
        key = str(int(targetAvId))
        remaining = [invite for invite in self.pendingInvites.get(key, [])
                     if int(invite.get('groupId', 0)) != int(groupId)]
        if remaining:
            self.pendingInvites[key] = remaining
        else:
            self.pendingInvites.pop(key, None)

    def _removeReservation(self, group, avId):
        avId = int(avId)
        before = len(group.get('members', []))
        group['members'] = [member for member in group.get('members', [])
                            if not (int(member.get('avId', 0)) == avId and member.get('reserved', False))]
        self._removePendingInvite(avId, int(group['id']))
        return len(group.get('members', [])) != before

    def _sendState(self, avId):
        group = self._groupForAv(avId)
        payload = '' if group is None else json.dumps(
            self._publicGroup(group), separators=(',', ':'))
        self.transport.sendUpdateToAvatarId(int(avId), 'groupReceiveState', [payload])

    def _broadcastState(self, group):
        for member in list(group.get('members', [])):
            if member.get('reserved', False):
                continue
            self._sendState(int(member.get('avId', 0)))

    def _sendBrowse(self, avId):
        groups = []
        for group in self.groups.values():
            if not group.get('published', False):
                continue
            groups.append(self._publicGroup(group))
        groups.sort(key=lambda item: (-int(item.get('created', 0)), int(item.get('id', 0))))
        self.transport.sendUpdateToAvatarId(int(avId), 'groupReceiveBrowse',
                                  [json.dumps(groups, separators=(',', ':'))])

    def _removeMember(self, group, avId, kicked=False):
        avId = int(avId)
        group['members'] = [member for member in group.get('members', [])
                            if int(member.get('avId', 0)) != avId]
        self.memberToGroup.pop(avId, None)
        if kicked:
            group.setdefault('banned', {})[str(avId)] = 1
        self._sendState(avId)

    def _disband(self, group, message='The Group was disbanded.'):
        members = list(group.get('members', []))
        groupId = int(group['id'])
        for member in members:
            if member.get('reserved', False):
                continue
            avId = int(member.get('avId', 0))
            self.memberToGroup.pop(avId, None)
            self.transport.sendUpdateToAvatarId(avId, 'groupReceiveState', [''])
            self._notify(avId, GroupGlobals.NOTIFY_INFO, message)
        self.groups.pop(groupId, None)
        for targetId in list(self.pendingInvites.keys()):
            invites = [invite for invite in self.pendingInvites[targetId]
                       if int(invite.get('groupId', 0)) != groupId]
            if invites:
                self.pendingInvites[targetId] = invites
            else:
                self.pendingInvites.pop(targetId, None)

    def _cleanup(self):
        now = int(time.time())
        expiredAvIds = []
        for avId, seen in list(self.lastSeen.items()):
            if now - int(seen) > GroupGlobals.GROUP_TIMEOUT_SECONDS:
                expiredAvIds.append(int(avId))
        for avId in expiredAvIds:
            self.lastSeen.pop(avId, None)
            group = self._groupForAv(avId)
            if group is None:
                continue
            if int(group.get('ownerId', 0)) == avId:
                self._disband(group, 'The Group leader went offline.')
            else:
                self._removeMember(group, avId)
                self._broadcastState(group)
        changedGroups = {}
        for targetId in list(self.pendingInvites.keys()):
            active = []
            for invite in self.pendingInvites[targetId]:
                if now <= int(invite.get('expires', 0)):
                    active.append(invite)
                    continue
                group = self.groups.get(int(invite.get('groupId', 0)))
                if group and self._removeReservation(group, int(targetId)):
                    changedGroups[int(group['id'])] = group
            if active:
                self.pendingInvites[targetId] = active
            else:
                self.pendingInvites.pop(targetId, None)
        for group in changedGroups.values():
            self._broadcastState(group)

    def heartbeat(self, avName, zoneId):
        avId = self._sender()
        self.lastSeen[avId] = int(time.time())
        group = self._groupForAv(avId)
        changed = False
        if group:
            cleanName, shardId = self._parseIdentity(avName)
            member = self._findMember(group, avId)
            if member and not member.get('reserved', False):
                if cleanName and member.get('name') != cleanName:
                    member['name'] = cleanName
                    changed = True
                if int(member.get('zoneId', 0)) != int(zoneId):
                    member['zoneId'] = int(zoneId)
                    changed = True
                if shardId and int(member.get('shardId', 0)) != shardId:
                    member['shardId'] = shardId
                    changed = True
            if int(group.get('ownerId', 0)) == avId:
                if cleanName and group.get('ownerName') != cleanName:
                    group['ownerName'] = cleanName
                    changed = True
                if shardId and int(group.get('shardId', 0)) != shardId:
                    group['shardId'] = shardId
                    changed = True
            if changed:
                self._broadcastState(group)
        self._cleanup()

    def requestState(self):
        avId = self._sender()
        self.lastSeen[avId] = int(time.time())
        self._cleanup()
        self._sendState(avId)
        now = int(time.time())
        for invite in self.pendingInvites.get(str(avId), []):
            if now > int(invite.get('expires', 0)):
                continue
            group = self.groups.get(int(invite.get('groupId', 0)))
            if group is None:
                continue
            self.transport.sendUpdateToAvatarId(avId, 'groupReceiveInvite', [
                int(group['id']), int(invite.get('inviterAvId', 0)),
                invite.get('inviterName', ''), group['activity'], group['location']])

    def requestBrowse(self):
        avId = self._sender()
        self.lastSeen[avId] = int(time.time())
        self._cleanup()
        self._sendBrowse(avId)

    def requestCreate(self, activity, location, zoneId, maxSize, published, avName):
        avId = self._sender()
        self.lastSeen[avId] = int(time.time())
        self._cleanup()
        if self._groupForAv(avId):
            self._notify(avId, GroupGlobals.NOTIFY_ERROR, 'You are already in a Group.')
            self._sendState(avId)
            return
        activity = self._cleanText(activity, 64)
        location = self._cleanText(location, 96)
        avName, shardId = self._parseIdentity(avName)
        if activity not in GroupGlobals.ACTIVITY_NAMES:
            activity = 'Other'
        try:
            maxSize = int(maxSize)
        except:
            maxSize = GroupGlobals.ACTIVITY_SIZES.get(activity, 4)
        maxSize = max(GroupGlobals.GROUP_MIN_SIZE,
                      min(GroupGlobals.GROUP_MAX_SIZE, maxSize))
        defaultSize = int(GroupGlobals.ACTIVITY_SIZES.get(activity, maxSize))
        maxSize = min(maxSize, max(GroupGlobals.GROUP_MIN_SIZE, defaultSize))
        if not location:
            location = 'Current Area'
        groupId = self.nextGroupId
        self.nextGroupId += 1
        group = {
            'id': groupId,
            'activity': activity,
            'location': location,
            'zoneId': int(zoneId),
            'shardId': int(shardId),
            'ownerId': avId,
            'ownerName': avName or ('Toon %s' % avId),
            'maxSize': maxSize,
            'published': bool(published),
            'members': [{'avId': avId, 'name': avName or ('Toon %s' % avId), 'zoneId': 0, 'shardId': int(shardId), 'reserved': False}],
            'created': int(time.time()),
            'banned': {},
        }
        self.groups[groupId] = group
        self.memberToGroup[avId] = groupId
        self._broadcastState(group)
        self._notify(avId, GroupGlobals.NOTIFY_SUCCESS, 'Group created.')

    def requestJoin(self, groupId, avName):
        avId = self._sender()
        self.lastSeen[avId] = int(time.time())
        self._cleanup()
        if self._groupForAv(avId):
            self._notify(avId, GroupGlobals.NOTIFY_ERROR, 'You are already in a Group.')
            return
        group = self.groups.get(int(groupId))
        if group is None:
            self._notify(avId, GroupGlobals.NOTIFY_ERROR, 'That Group no longer exists.')
            self._sendBrowse(avId)
            return
        if not group.get('published', False):
            self._notify(avId, GroupGlobals.NOTIFY_ERROR, 'That Group is private.')
            return
        if str(avId) in group.get('banned', {}):
            self._notify(avId, GroupGlobals.NOTIFY_ERROR, 'You cannot rejoin that Group unless invited.')
            return
        reserved = self._findMember(group, avId)
        if reserved and not reserved.get('reserved', False):
            self._notify(avId, GroupGlobals.NOTIFY_ERROR, 'You are already in that Group.')
            return
        if reserved is None and len(group.get('members', [])) >= int(group.get('maxSize', 4)):
            self._notify(avId, GroupGlobals.NOTIFY_ERROR, 'That Group is full.')
            self._sendBrowse(avId)
            return
        cleanName, shardId = self._parseIdentity(avName)
        cleanName = cleanName or ('Toon %s' % avId)
        if reserved:
            reserved['name'] = cleanName
            reserved['reserved'] = False
            reserved['zoneId'] = 0
            reserved['shardId'] = int(shardId)
            self._removePendingInvite(avId, int(group['id']))
        else:
            group['members'].append({'avId': avId, 'name': cleanName, 'zoneId': 0,
                                     'shardId': int(shardId), 'reserved': False})
        self.memberToGroup[avId] = int(group['id'])
        self._broadcastState(group)
        self._notify(avId, GroupGlobals.NOTIFY_SUCCESS, 'You joined the Group.')
        ownerId = int(group.get('ownerId', 0))
        if ownerId and ownerId != avId:
            self._notify(ownerId, GroupGlobals.NOTIFY_INFO, '%s joined the Group.' % cleanName)

    def requestLeave(self):
        avId = self._sender()
        group = self._groupForAv(avId)
        if group is None:
            self._sendState(avId)
            return
        if int(group.get('ownerId', 0)) == avId:
            self._disband(group)
            return
        self._removeMember(group, avId)
        self._broadcastState(group)
        self._notify(avId, GroupGlobals.NOTIFY_INFO, 'You left the Group.')

    def requestDisband(self):
        avId = self._sender()
        group = self._groupForAv(avId)
        if group is None:
            return
        if int(group.get('ownerId', 0)) != avId:
            self._notify(avId, GroupGlobals.NOTIFY_ERROR, 'Only the Group leader can disband it.')
            return
        self._disband(group)

    def requestKick(self, targetAvId):
        avId = self._sender()
        group = self._groupForAv(avId)
        if group is None or int(group.get('ownerId', 0)) != avId:
            self._notify(avId, GroupGlobals.NOTIFY_ERROR, 'Only the Group leader can kick members.')
            return
        targetAvId = int(targetAvId)
        if targetAvId == avId:
            return
        target = self._findMember(group, targetAvId)
        if target is None:
            return
        targetName = target.get('name', '') or 'Toon'
        if target.get('reserved', False):
            self._removeReservation(group, targetAvId)
            self._broadcastState(group)
            self._notify(avId, GroupGlobals.NOTIFY_SUCCESS, 'Invitation to %s was cancelled.' % targetName)
            return
        if self.memberToGroup.get(targetAvId) != int(group['id']):
            return
        self._removeMember(group, targetAvId, kicked=True)
        self._broadcastState(group)
        self._notify(avId, GroupGlobals.NOTIFY_SUCCESS, 'You kicked %s from the Group.' % targetName)
        self._notify(targetAvId, GroupGlobals.NOTIFY_INFO, 'You were kicked from the Group.')

    def requestMassTeleport(self):
        avId = self._sender()
        self.lastSeen[avId] = int(time.time())
        self._cleanup()
        now = time.time()
        for token, session in list(self.massTeleportSessions.items()):
            if now - session.get('created', now) > 30.0:
                self.massTeleportSessions.pop(token, None)
        group = self._groupForAv(avId)
        if group is None or int(group.get('ownerId', 0)) != avId:
            self._notify(avId, GroupGlobals.NOTIFY_ERROR, 'Only the Group leader can mass teleport members.')
            return
        activity = str(group.get('activity', ''))
        bossLobbies = {
            'VP': ToontownGlobals.SellbotLobby,
            'CFO': ToontownGlobals.CashbotLobby,
            'CJ': ToontownGlobals.LawbotLobby,
            'CEO': ToontownGlobals.BossbotLobby,
        }
        zoneId = int(bossLobbies.get(activity, int(group.get('zoneId', 0) or 0)))
        shardId = int(group.get('shardId', 0) or 0)
        if not zoneId:
            self._notify(avId, GroupGlobals.NOTIFY_ERROR, 'That Group destination is not available.')
            return
        members = []
        for member in list(group.get('members', [])):
            if member.get('reserved', False):
                continue
            memberId = int(member.get('avId', 0))
            memberZone = int(member.get('zoneId', 0) or 0)
            memberShard = int(member.get('shardId', 0) or 0)
            if memberZone == zoneId and (not shardId or memberShard == shardId):
                continue
            members.append(memberId)
        token = 0
        if zoneId in (ToontownGlobals.SellbotLobby, ToontownGlobals.CashbotLobby, ToontownGlobals.LawbotLobby, ToontownGlobals.BossbotLobby) and members:
            token = int(self.nextMassTeleportToken)
            self.nextMassTeleportToken += 1
            if self.nextMassTeleportToken > 0xFFFFFFFF:
                self.nextMassTeleportToken = 1
            self.massTeleportSessions[token] = {
                'members': set(members),
                'ready': set(),
                'created': now,
            }
        for memberId in members:
            self.transport.sendUpdateToAvatarId(memberId, 'groupReceiveMassTeleport', [zoneId, shardId, token])
        teleported = len(members)
        if teleported:
            self._notify(avId, GroupGlobals.NOTIFY_SUCCESS, 'Mass teleport sent to %s Toon%s.' % (teleported, '' if teleported == 1 else 's'))
        else:
            self._notify(avId, GroupGlobals.NOTIFY_INFO, 'Everyone is already at the Group destination.')

    def requestMassTeleportReady(self, token):
        avId = self._sender()
        try:
            token = int(token)
        except:
            return
        session = self.massTeleportSessions.get(token)
        if not session or avId not in session['members']:
            return
        session['ready'].add(avId)
        if session['ready'] >= session['members']:
            for memberId in session['members']:
                self.transport.sendUpdateToAvatarId(memberId, 'groupReceiveMassTeleportStart', [token])
            self.massTeleportSessions.pop(token, None)

    def requestPublish(self, published):
        avId = self._sender()
        group = self._groupForAv(avId)
        if group is None or int(group.get('ownerId', 0)) != avId:
            self._notify(avId, GroupGlobals.NOTIFY_ERROR, 'Only the Group leader can change privacy.')
            return
        group['published'] = bool(published)
        self._broadcastState(group)

    def requestInvite(self, targetAvId, targetName):
        avId = self._sender()
        group = self._groupForAv(avId)
        if group is None:
            self._notify(avId, GroupGlobals.NOTIFY_ERROR, 'Create or join a Group first.')
            return
        targetAvId = int(targetAvId)
        if targetAvId <= 0 or targetAvId == avId:
            return
        if self._groupForAv(targetAvId):
            self._notify(avId, GroupGlobals.NOTIFY_ERROR, 'That Toon is already in a Group.')
            return
        existingMember = self._findMember(group, targetAvId)
        if existingMember:
            if existingMember.get('reserved', False):
                self._notify(avId, GroupGlobals.NOTIFY_INFO, 'That Toon is already invited.')
            else:
                self._notify(avId, GroupGlobals.NOTIFY_ERROR, 'That Toon is already in the Group.')
            return
        if len(group.get('members', [])) >= int(group.get('maxSize', 4)):
            self._notify(avId, GroupGlobals.NOTIFY_ERROR, 'Your Group is full.')
            return
        group.setdefault('banned', {}).pop(str(targetAvId), None)
        inviterName = ''
        for member in group.get('members', []):
            if int(member.get('avId', 0)) == avId:
                inviterName = member.get('name', '')
                break
        targetName = self._cleanText(targetName, 64) or ('Toon %s' % targetAvId)
        invite = {
            'groupId': int(group['id']),
            'inviterAvId': avId,
            'inviterName': inviterName or ('Toon %s' % avId),
            'targetName': targetName,
            'expires': int(time.time()) + GroupGlobals.GROUP_INVITE_TIMEOUT_SECONDS,
        }
        key = str(targetAvId)
        existing = [item for item in self.pendingInvites.get(key, [])
                    if int(item.get('groupId', 0)) != int(group['id'])]
        existing.append(invite)
        self.pendingInvites[key] = existing
        group['members'].append({'avId': targetAvId, 'name': targetName, 'zoneId': 0,
                                 'shardId': 0, 'reserved': True})
        self._broadcastState(group)
        self.transport.sendUpdateToAvatarId(targetAvId, 'groupReceiveInvite', [
            int(group['id']), avId, invite['inviterName'],
            group['activity'], group['location']])
        self._notify(avId, GroupGlobals.NOTIFY_SUCCESS, 'Group invitation sent.')

    def respondToInvite(self, groupId, accept, avName):
        avId = self._sender()
        key = str(avId)
        now = int(time.time())
        match = None
        remaining = []
        for invite in self.pendingInvites.get(key, []):
            if int(invite.get('groupId', 0)) == int(groupId) and now <= int(invite.get('expires', 0)):
                match = invite
            else:
                remaining.append(invite)
        if remaining:
            self.pendingInvites[key] = remaining
        else:
            self.pendingInvites.pop(key, None)
        group = self.groups.get(int(groupId))
        if not accept:
            if group and self._removeReservation(group, avId):
                self._broadcastState(group)
            return
        if match is None:
            if group and self._removeReservation(group, avId):
                self._broadcastState(group)
            self._notify(avId, GroupGlobals.NOTIFY_ERROR, 'That Group invitation expired.')
            return
        if self._groupForAv(avId):
            if group and self._removeReservation(group, avId):
                self._broadcastState(group)
            self._notify(avId, GroupGlobals.NOTIFY_ERROR, 'You are already in a Group.')
            return
        if group is None:
            self._notify(avId, GroupGlobals.NOTIFY_ERROR, 'That Group no longer exists.')
            return
        reserved = self._findMember(group, avId)
        if reserved is None and len(group.get('members', [])) >= int(group.get('maxSize', 4)):
            self._notify(avId, GroupGlobals.NOTIFY_ERROR, 'That Group is full.')
            return
        group.setdefault('banned', {}).pop(str(avId), None)
        cleanName, shardId = self._parseIdentity(avName)
        cleanName = cleanName or ('Toon %s' % avId)
        if reserved:
            reserved['name'] = cleanName
            reserved['reserved'] = False
            reserved['zoneId'] = 0
            reserved['shardId'] = int(shardId)
        else:
            group['members'].append({'avId': avId, 'name': cleanName, 'zoneId': 0,
                                     'shardId': int(shardId), 'reserved': False})
        self.memberToGroup[avId] = int(group['id'])
        self.lastSeen[avId] = int(time.time())
        self._broadcastState(group)
        self._notify(avId, GroupGlobals.NOTIFY_SUCCESS, 'You joined the Group.')
        ownerId = int(group.get('ownerId', 0))
        if ownerId and ownerId != avId:
            self._notify(ownerId, GroupGlobals.NOTIFY_INFO, '%s joined the Group.' % cleanName)

