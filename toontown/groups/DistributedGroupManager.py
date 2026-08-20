from __future__ import absolute_import
import json
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.showbase.DirectObject import DirectObject

from toontown.groups import GroupGlobals
from toontown.hood import ZoneUtil
from toontown.toonbase import ToontownGlobals


class DistributedGroupManager(DirectObject):
    notify = directNotify.newCategory('DistributedGroupManager')

    def __init__(self, transport):
        DirectObject.__init__(self)
        self.transport = transport
        self.cr = transport.cr
        self.group = None
        self.joinableGroups = []
        self.pendingInvites = []
        self._initialTaskName = 'group-manager-initial-%s' % id(self)
        self._heartbeatTaskName = 'group-manager-heartbeat-%s' % id(self)
        self._massTeleportReadyTaskName = 'group-manager-mass-ready-%s' % id(self)
        self._massTeleportFallbackTaskName = 'group-manager-mass-fallback-%s' % id(self)
        self._massTeleportArrival = None
        self._massTeleportReleased = set()

    def start(self):
        taskMgr.doMethodLater(0.5, self._initialStateTask, self._initialTaskName)
        taskMgr.doMethodLater(GroupGlobals.GROUP_HEARTBEAT_SECONDS,
                              self._heartbeatTask, self._heartbeatTaskName)

    def stop(self):
        taskMgr.remove(self._initialTaskName)
        taskMgr.remove(self._heartbeatTaskName)
        taskMgr.remove(self._massTeleportReadyTaskName)
        taskMgr.remove(self._massTeleportFallbackTaskName)
        self._massTeleportArrival = None
        self._massTeleportReleased = set()
        self.ignoreAll()

    def _send(self, field, args=None):
        if args is None:
            args = []
        self.transport.sendUpdate(field, args)

    def _localName(self):
        try:
            return str(base.localAvatar.getName())[:48]
        except:
            return ''

    def _identity(self):
        name = self._localName()
        try:
            shardId = int(base.localAvatar.defaultShard)
        except:
            shardId = 0
        return ('%s\x1f%s' % (name, shardId))[:64]

    def _localZone(self):
        try:
            return int(base.localAvatar.getZoneId())
        except:
            try:
                return int(base.localAvatar.getLocation()[1])
            except:
                return 0

    def _initialStateTask(self, task):
        if hasattr(base, 'localAvatar') and base.localAvatar:
            self.requestState()
            self.requestBrowse()
            self.heartbeat()
            return task.done
        return task.again

    def _heartbeatTask(self, task):
        if hasattr(base, 'localAvatar') and base.localAvatar:
            self.heartbeat()
        return task.again

    def heartbeat(self):
        self._send('groupHeartbeat', [self._identity(), self._localZone()])

    def prepareSuitTeleport(self, targetZone, deptIndex):
        targetZone = int(targetZone)
        try:
            base.localAvatar._groupLobbyFacingZone = targetZone
        except:
            pass
        self._send('groupPrepareSuitTeleport', [targetZone, int(deptIndex)])

    def requestState(self):
        self._send('groupRequestState')

    def requestBrowse(self):
        self._send('groupRequestBrowse')

    def requestCreate(self, activity, location, zoneId, maxSize, published=True):
        self._send('groupRequestCreate', [str(activity)[:64], str(location)[:96],
                                          int(zoneId), int(maxSize), int(bool(published)),
                                          self._identity()])
        self.heartbeat()

    def requestJoin(self, groupId):
        self._send('groupRequestJoin', [int(groupId), self._identity()])
        self.heartbeat()

    def requestLeave(self):
        self._send('groupRequestLeave')
        if self.group:
            self.group = None
            messenger.send('group-tracker-state', [None])
            messenger.send('group-tracker-left')
            self.requestBrowse()

    def requestDisband(self):
        self._send('groupRequestDisband')
        if self.isOwner():
            self.group = None
            messenger.send('group-tracker-state', [None])
            messenger.send('group-tracker-left')
            self.requestBrowse()

    def requestKick(self, avId):
        self._send('groupRequestKick', [int(avId)])

    def requestMassTeleport(self):
        if self.isOwner():
            self._send('groupRequestMassTeleport')

    def requestPublish(self, published):
        self._send('groupRequestPublish', [int(bool(published))])

    def requestInvite(self, avId, avName=''):
        self._send('groupRequestInvite', [int(avId), str(avName)[:64]])

    def respondToInvite(self, groupId, accept):
        self._send('groupRespondToInvite', [int(groupId), int(bool(accept)),
                                             self._identity()])
        if accept:
            self.heartbeat()

    def receiveState(self, groupJson):
        oldGroupId = 0
        if self.group:
            try:
                oldGroupId = int(self.group.get('id', 0))
            except:
                oldGroupId = 0
        try:
            self.group = json.loads(groupJson) if groupJson else None
        except Exception as error:
            self.notify.warning('Could not decode Group state: %s' % error)
            self.group = None
        newGroupId = 0
        if self.group:
            try:
                newGroupId = int(self.group.get('id', 0))
            except:
                newGroupId = 0
        messenger.send('group-tracker-state', [self.group])
        if not oldGroupId and newGroupId:
            messenger.send('group-tracker-joined', [self.group])
        elif oldGroupId and not newGroupId:
            messenger.send('group-tracker-left')

    def receiveBrowse(self, groupsJson):
        try:
            groups = json.loads(groupsJson) if groupsJson else []
            if not isinstance(groups, list):
                groups = []
        except Exception as error:
            self.notify.warning('Could not decode Group browser state: %s' % error)
            groups = []
        self.joinableGroups = groups
        messenger.send('group-tracker-browse', [self.joinableGroups])

    def receiveInvite(self, groupId, inviterAvId, inviterName, activity, location):
        invite = {
            'groupId': int(groupId),
            'inviterAvId': int(inviterAvId),
            'inviterName': str(inviterName),
            'activity': str(activity),
            'location': str(location),
        }
        self.pendingInvites.append(invite)
        messenger.send('group-tracker-invite', [invite])
        self._showInvite(invite)

    def _bossLobbyDept(self, zoneId):
        return {
            ToontownGlobals.BossbotLobby: 0,
            ToontownGlobals.LawbotLobby: 1,
            ToontownGlobals.CashbotLobby: 2,
            ToontownGlobals.SellbotLobby: 3,
        }.get(int(zoneId))

    def _groupLobbySlot(self):
        try:
            localId = int(base.localAvatar.doId)
            members = []
            if self.group:
                for member in self.group.get('members', []):
                    if member.get('reserved', False):
                        continue
                    try:
                        avId = int(member.get('avId', 0) or 0)
                    except:
                        avId = 0
                    if avId:
                        members.append(avId)
            if localId in members:
                return members.index(localId)
        except:
            pass
        return 0

    def _currentHood(self):
        try:
            hoodId = base.cr.playGame.getPlaceId()
            if hoodId is not None:
                return int(hoodId)
        except:
            pass
        try:
            return int(ZoneUtil.getHoodId(self._localZone()))
        except:
            return 0

    def _currentShard(self):
        try:
            return int(base.localAvatar.defaultShard)
        except:
            return 0

    def _teleportPlace(self):
        try:
            return base.cr.playGame.getPlace()
        except:
            return None

    def _placeCanTeleport(self, place):
        if not place:
            return False
        try:
            return place.getState() in ('walk', 'stickerBook')
        except:
            return False

    def teleportToGroupZone(self, zoneId, shardId=0, massTeleportToken=0):
        try:
            zoneId = int(zoneId)
            shardId = int(shardId or 0)
        except:
            return False
        if not zoneId:
            return False
        localZone = self._localZone()
        localShard = self._currentShard()
        if localZone == zoneId and (not shardId or localShard == shardId):
            return True
        place = self._teleportPlace()
        if not self._placeCanTeleport(place):
            return False
        hoodId = int(ZoneUtil.getHoodId(zoneId))
        deptIndex = self._bossLobbyDept(zoneId)
        targetShard = shardId if shardId and shardId != localShard else None
        extraStatus = None
        if deptIndex is not None:
            self.prepareSuitTeleport(zoneId, deptIndex)
            extraStatus = {
                'groupLobbyTeleport': True,
                'groupLobbyDeptIndex': int(deptIndex),
                'groupLobbySlot': int(self._groupLobbySlot()),
            }
            if massTeleportToken:
                extraStatus['groupMassTeleportToken'] = int(massTeleportToken)
        try:
            place.requestTeleport(hoodId, zoneId, targetShard, -1, extraStatus)
            return True
        except Exception as error:
            self.notify.warning('Group teleport failed: %s' % error)
            return False

    def receiveMassTeleport(self, zoneId, shardId, massTeleportToken=0):
        try:
            zoneId = int(zoneId)
            shardId = int(shardId)
        except:
            return
        if not zoneId:
            return
        localZone = self._localZone()
        localShard = self._currentShard()
        if localZone == zoneId and (not shardId or localShard == shardId):
            return
        if not self.teleportToGroupZone(zoneId, shardId, massTeleportToken):
            self.notify.warning('Mass Group teleport could not start.')

    def deferMassTeleportArrival(self, token, place, requestStatus):
        try:
            token = int(token)
        except:
            return False
        if not token:
            return False
        self._massTeleportArrival = (token, place, dict(requestStatus))
        taskMgr.remove(self._massTeleportReadyTaskName)
        taskMgr.remove(self._massTeleportFallbackTaskName)
        if token in self._massTeleportReleased:
            self._finishMassTeleportArrival(token)
            return True
        taskMgr.doMethodLater(0.05, self._massTeleportReadyTask, self._massTeleportReadyTaskName)
        taskMgr.doMethodLater(8.0, self._massTeleportFallbackTask, self._massTeleportFallbackTaskName)
        return True

    def _massTeleportReadyTask(self, task):
        arrival = self._massTeleportArrival
        if not arrival:
            return task.done
        token = arrival[0]
        try:
            if not base.localAvatar.isDisguised:
                return task.again
        except:
            return task.again
        self._send('groupRequestMassTeleportReady', [int(token)])
        return task.done

    def _massTeleportFallbackTask(self, task):
        arrival = self._massTeleportArrival
        if arrival:
            self._finishMassTeleportArrival(arrival[0])
        return task.done

    def receiveMassTeleportStart(self, token):
        try:
            token = int(token)
        except:
            return
        self._massTeleportReleased.add(token)
        self._finishMassTeleportArrival(token)

    def _finishMassTeleportArrival(self, token):
        arrival = self._massTeleportArrival
        if not arrival or int(arrival[0]) != int(token):
            return
        taskMgr.remove(self._massTeleportReadyTaskName)
        taskMgr.remove(self._massTeleportFallbackTaskName)
        self._massTeleportArrival = None
        self._massTeleportReleased.discard(int(token))
        place = arrival[1]
        requestStatus = arrival[2]
        if place and hasattr(place, '_continueTeleportInPostZoneComplete'):
            place._continueTeleportInPostZoneComplete(requestStatus)

    def receiveNotification(self, notifyType, message):
        notifyType = int(notifyType)
        message = str(message)
        messenger.send('group-tracker-notification', [notifyType, message])
        try:
            from toontown.notifications.NotificationManager import getNotificationManager
            from toontown.notifications.notificationData.GenericTextNotification import GenericTextNotification
            title = 'Group Update'
            if notifyType == GroupGlobals.NOTIFY_ERROR:
                title = 'Group Error'
            getNotificationManager().addNotification(GenericTextNotification(
                title=title,
                subtitle=message))
        except Exception as error:
            self.notify.warning('Could not open Group notification alert: %s' % error)
            try:
                base.localAvatar.setSystemMessage(0, message)
            except:
                pass

    def _showInvite(self, invite):
        try:
            from toontown.notifications.NotificationManager import getNotificationManager
            from toontown.notifications.notificationData.GenericYesNoNotification import GenericYesNoNotification

            def acceptInvite(invite=invite):
                self.respondToInvite(invite['groupId'], True)

            def rejectInvite(invite=invite):
                self.respondToInvite(invite['groupId'], False)

            text = '%s invited you to their Group:\n%s at %s' % (
                invite['inviterName'], invite['activity'], invite['location'])
            notification = GenericYesNoNotification(
                title='Group Invitation',
                subtitle=text,
                onYes=acceptInvite,
                onNo=rejectInvite,
                onDismiss=rejectInvite,
                dedupeKey=('group-invite', int(invite['groupId'])))
            getNotificationManager().addNotification(notification)
        except Exception as error:
            self.notify.warning('Could not open Group invite alert: %s' % error)

    def isInGroup(self):
        return bool(self.group)

    def isOwner(self):
        if not self.group:
            return False
        try:
            return int(self.group.get('ownerId', 0)) == int(base.localAvatar.doId)
        except:
            return False
