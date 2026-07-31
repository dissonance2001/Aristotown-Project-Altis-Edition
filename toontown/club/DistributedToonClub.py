import json
import os

from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.showbase.DirectObject import DirectObject

from toontown.club import ClubGlobals


class DistributedToonClub(DistributedObjectGlobal, DirectObject):
    """Client-facing, Python 2 compatible Club manager for Project Altis."""

    notify = directNotify.newCategory('DistributedToonClub')

    def __init__(self, cr):
        DistributedObjectGlobal.__init__(self, cr)
        DirectObject.__init__(self)
        self.club = None
        self.pendingInvites = []
        self.lastLogs = []
        self._requestedInitialState = False
        self.personalSettings = dict(ClubGlobals.PERSONAL_SETTING_DEFAULTS)
        self._personalSettingsAvatarId = 0
        self._clubNametagPulseTaskName = 'ClubNametag-colorPulse-%s' % id(self)

    def announceGenerate(self):
        DistributedObjectGlobal.announceGenerate(self)
        self.cr.clubMgr = self
        # Compatibility alias used by the Clash-style chat port.
        self.cr.guildManager = self
        taskMgr.doMethodLater(0.5, self._requestInitialState, self.uniqueName('requestClubState'))
        print '[Clubs] Club manager loaded.'

    def disable(self):
        taskMgr.remove(self.uniqueName('requestClubState'))
        taskMgr.remove(self._clubNametagPulseTaskName)
        if getattr(self.cr, 'clubMgr', None) is self:
            self.cr.clubMgr = None
        if getattr(self.cr, 'guildManager', None) is self:
            self.cr.guildManager = None
        DistributedObjectGlobal.disable(self)

    def delete(self):
        taskMgr.remove(self._clubNametagPulseTaskName)
        self.ignoreAll()
        DistributedObjectGlobal.delete(self)

    def _requestInitialState(self, task):
        if hasattr(base, 'localAvatar') and base.localAvatar:
            self.requestState()
            return task.done
        return task.again

    # ------------------------------------------------------------------
    # Requests
    # ------------------------------------------------------------------
    def requestState(self):
        self.sendUpdate('requestState', [])

    def requestCreateClub(self, name, icon=None):
        iconId = 0
        backgroundId = 0
        themeId = 0
        backgroundColorId = 0
        if icon is not None:
            iconId = int(getattr(icon, 'iconId', getattr(icon, 'icon', 0)) or 0)
            backgroundId = int(getattr(icon, 'backgroundId', getattr(icon, 'background', 0)) or 0)
            themeId = int(getattr(icon, 'clubCol', getattr(icon, 'theme', 0)) or 0)
            backgroundColorId = int(getattr(icon, 'bgCol', getattr(icon, 'backgroundColor', 0)) or 0)
        self.sendUpdate('requestCreateClub', [str(name), iconId, backgroundId, themeId, backgroundColorId,
                                              base.localAvatar.getName()])

    def requestInvite(self, targetAvId, targetName=''):
        self.sendUpdate('requestInvite', [int(targetAvId), str(targetName)])

    def respondToInvite(self, clubId, accept):
        self.sendUpdate('respondToInvite', [int(clubId), int(bool(accept)), base.localAvatar.getName()])

    def requestLeave(self):
        self.sendUpdate('requestLeave', [])

    def requestKick(self, avId):
        self.sendUpdate('requestKick', [int(avId)])

    def requestSetRank(self, avId, rank):
        self.sendUpdate('requestSetRank', [int(avId), int(rank)])

    def requestTransferOwner(self, avId):
        self.sendUpdate('requestTransferOwner', [int(avId)])

    def requestSetMotd(self, motd):
        self.sendUpdate('requestSetMotd', [str(motd)[:ClubGlobals.CLUB_MOTD_MAX]])

    def requestSetPermission(self, rank, permission, enabled):
        permissionId = ClubGlobals.PERMISSION_KEY_TO_ID.get(permission, permission)
        self.sendUpdate('requestSetPermission', [int(rank), int(permissionId), int(bool(enabled))])

    def requestUpdateIcon(self, iconId, backgroundId, themeId, backgroundColorId):
        self.sendUpdate('requestUpdateIcon', [int(iconId), int(backgroundId), int(themeId), int(backgroundColorId)])

    def requestPurchaseItem(self, itemId):
        self.sendUpdate('requestPurchaseItem', [int(itemId)])

    def requestDonateJellybeans(self, amount):
        amount = max(0, int(amount))
        if not amount or not self.isInClub():
            return False

        # Project Altis already has requestUpdateIcon in its DC schema. Encode
        # the donation through that existing field so older clients/servers do
        # not require a new DC field or disconnect on sendUpdate.
        low = amount & 0xFFFF
        high = (amount >> 16) & 0xFFFF
        magic = ClubGlobals.DONATION_REQUEST_MAGIC
        self.sendUpdate('requestUpdateIcon', [magic, low, high, magic])
        return True

    def requestStartTask(self, taskId=0):
        # Club Tasks are assigned automatically. Retain this method only for
        # compatibility with older GUI callers.
        return False

    def requestRerollTask(self, slot):
        self.sendUpdate('requestRerollTask', [int(slot)])

    def requestLogs(self, page=0):
        self.sendUpdate('requestLogs', [int(page)])

    def sendClubChat(self, message):
        if not self.isInClub():
            return False
        message = str(message).strip()[:ClubGlobals.CLUB_CHAT_MAX]
        if not message:
            return False
        self.sendUpdate('sendClubChat', [message])
        return True

    # Compatibility methods used by TalkAssistant/GuildManager callers.
    def sendTalk(self, message):
        return self.sendClubChat(message)

    def sendSC(self, msgIndex, msgType=None):
        try:
            from otp.chat.ChatGlobals import SPEEDCHAT_CUSTOM, SPEEDCHAT_EMOTE
            decoder = base.talkAssistant.SCDecoder
            if msgType == SPEEDCHAT_CUSTOM:
                message = decoder.decodeSCCustomMsg(msgIndex)
            elif msgType == SPEEDCHAT_EMOTE:
                message = decoder.decodeSCEmoteWhisperMsg(msgIndex, base.localAvatar.getName())
            else:
                message = decoder.decodeSCStaticTextMsg(msgIndex)
        except:
            try:
                from otp.otpbase import OTPLocalizer
                message = OTPLocalizer.SpeedChatStaticText[msgIndex]
            except:
                message = 'SpeedChat message %s' % msgIndex
        return self.sendClubChat(message)

    # ------------------------------------------------------------------
    # Server responses
    # ------------------------------------------------------------------
    def receiveState(self, clubJson):
        try:
            state = json.loads(clubJson)
        except Exception as error:
            self.notify.warning('Could not decode Club state: %s' % error)
            state = None
        self.club = state
        self._loadPersonalSettings()
        self._applyLocalState()
        messenger.send('club-state-updated', [self.club])

    def receiveInvite(self, inviterAvId, inviterName, clubId, clubName):
        invite = {
            'inviterAvId': inviterAvId,
            'inviterName': inviterName,
            'clubId': clubId,
            'clubName': clubName,
        }
        self.pendingInvites.append(invite)
        messenger.send('club-invite-received', [invite])
        self._showInviteDialog(invite)

    def receiveNotification(self, notifyType, message):
        notifyType = int(notifyType)

        # Donation results travel through the existing receiveNotification DC
        # field. Convert the compact payload back into the local GUI event and
        # do not display the encoded payload as a normal Club notification.
        if notifyType == ClubGlobals.NOTIFY_DONATION_RESULT:
            try:
                payload = json.loads(str(message))
                success = bool(payload.get('success', False))
                amount = int(payload.get('amount', 0))
                resultMessage = str(payload.get('message', ''))
            except Exception as error:
                self.notify.warning('Could not decode donation result: %s' % error)
                success = False
                amount = 0
                resultMessage = 'The Club Jellybean donation result was invalid.'
            messenger.send('club-jellybean-donation-result', [
                success, amount, resultMessage])
            return

        messenger.send('club-notification', [notifyType, message])

        if notifyType == ClubGlobals.NOTIFY_COIN_EARNED:
            popupSetting = ClubGlobals.SETTING_COIN_NOTIFICATIONS
        elif int(notifyType) == ClubGlobals.NOTIFY_ERROR:
            popupSetting = None
        else:
            popupSetting = ClubGlobals.SETTING_UPDATE_POPUPS

        showPopup = True if popupSetting is None else self.getPersonalSetting(popupSetting)
        chatLog = getattr(self.cr, 'chatLog', None)
        if chatLog:
            category = chatLog.TAB_CLUBS if self.isInClub() else chatLog.TAB_ALERTS
            try:
                chatLog.addToLog('\1orangeText\1Club Update\2: %s' % message,
                                 category=category, showNotification=showPopup)
            except TypeError:
                chatLog.addToLog('\1orangeText\1Club Update\2: %s' % message, category=category)
        if showPopup:
            self._showClubPopup('Club Update: %s' % message)

    def receiveClubChat(self, senderAvId, senderName, message):
        showPopup = self.getPersonalSetting(ClubGlobals.SETTING_MESSAGE_POPUPS)
        chatLog = getattr(self.cr, 'chatLog', None)
        if chatLog:
            try:
                chatLog.addToLog('\1playerGreen\1%s\2: %s' % (senderName, message),
                                 senderAvId, category=chatLog.TAB_CLUBS,
                                 showNotification=showPopup)
            except TypeError:
                chatLog.addToLog('\1playerGreen\1%s\2: %s' % (senderName, message),
                                 senderAvId, category=chatLog.TAB_CLUBS)
        if showPopup and int(senderAvId) != int(getattr(base.localAvatar, 'doId', 0)):
            self._showClubPopup('%s: %s' % (senderName, message))
        messenger.send('club-chat-received', [senderAvId, senderName, message])

    def receiveLogs(self, logsJson):
        try:
            self.lastLogs = json.loads(logsJson)
        except:
            self.lastLogs = []
        messenger.send('club-logs-updated', [self.lastLogs])

    def _applyLocalState(self):
        if not hasattr(base, 'localAvatar') or not base.localAvatar:
            return
        if self.club:
            member = self.getMember(base.localAvatar.doId) or {}
            base.localAvatar.guildId = int(self.club.get('id', 0))
            base.localAvatar.guildName = self.club.get('name', '')
            base.localAvatar.guildRank = int(member.get('rank', ClubGlobals.RANK_MEMBER))
        else:
            base.localAvatar.guildId = 0
            base.localAvatar.guildName = ''
            base.localAvatar.guildRank = 0
        self._applyPersonalSettings()
        chatLog = getattr(self.cr, 'chatLog', None)
        if chatLog and hasattr(chatLog, 'setClubAvailable'):
            chatLog.setClubAvailable(bool(self.club))

    # ------------------------------------------------------------------
    # Query helpers used by UI and NPCs
    # ------------------------------------------------------------------
    def isInClub(self):
        return bool(self.club and self.club.get('id'))

    def getClubId(self):
        return int(self.club.get('id', 0)) if self.club else 0

    def getClubName(self):
        return self.club.get('name', '') if self.club else ''

    def getMembers(self):
        return list(self.club.get('members', [])) if self.club else []

    def getMember(self, avId):
        for member in self.getMembers():
            if int(member.get('avId', 0)) == int(avId):
                return member
        return None

    def getLocalRank(self):
        member = self.getMember(getattr(base.localAvatar, 'doId', 0))
        return int(member.get('rank', ClubGlobals.RANK_MEMBER)) if member else ClubGlobals.RANK_MEMBER

    def localAvIsOwner(self):
        return self.getLocalRank() == ClubGlobals.RANK_LEADER

    def getRankPermission(self, rank, permission):
        rank = int(rank)
        if rank == ClubGlobals.RANK_LEADER:
            return True
        if self.club:
            permissions = self.club.get('permissions', {})
            rankPermissions = permissions.get(str(rank), permissions.get(rank, {}))
            if permission in rankPermissions:
                return bool(rankPermissions.get(permission))
        return ClubGlobals.hasPermission(rank, permission)

    def localAvHasPermission(self, permission):
        return self.getRankPermission(self.getLocalRank(), permission)

    def getClubCoins(self):
        return int(self.club.get('coins', 0)) if self.club else 0

    def getClubJellybeans(self):
        return int(self.club.get('jellybeans', 0)) if self.club else 0

    # Corporate Clash compatibility name used by Club Shop code.
    def getJellybeans(self):
        return self.getClubJellybeans()

    def getClubLevel(self):
        return int(self.club.get('level', 1)) if self.club else 1

    # ------------------------------------------------------------------
    # Personal Club settings
    # ------------------------------------------------------------------
    def _personalSettingsPath(self):
        return os.path.join('user', 'settings', 'club_personal_settings.json')

    def _loadPersonalSettings(self):
        avId = int(getattr(getattr(base, 'localAvatar', None), 'doId', 0))
        if not avId or self._personalSettingsAvatarId == avId:
            return
        self._personalSettingsAvatarId = avId
        self.personalSettings = dict(ClubGlobals.PERSONAL_SETTING_DEFAULTS)
        try:
            path = self._personalSettingsPath()
            if os.path.isfile(path):
                handle = open(path, 'r')
                payload = json.load(handle)
                handle.close()
                saved = payload.get(str(avId), {})
                for key in ClubGlobals.PERSONAL_SETTING_KEYS:
                    if key in saved:
                        self.personalSettings[key] = bool(saved[key])
        except Exception as error:
            self.notify.warning('Could not load personal Club settings: %s' % error)

    def _savePersonalSettings(self):
        avId = int(getattr(getattr(base, 'localAvatar', None), 'doId', 0))
        if not avId:
            return
        path = self._personalSettingsPath()
        payload = {}
        try:
            if os.path.isfile(path):
                handle = open(path, 'r')
                payload = json.load(handle)
                handle.close()
        except:
            payload = {}
        payload[str(avId)] = dict(self.personalSettings)
        try:
            directory = os.path.dirname(path)
            if not os.path.isdir(directory):
                os.makedirs(directory)
            temporary = path + '.tmp'
            handle = open(temporary, 'w')
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.close()
            if os.path.isfile(path):
                os.remove(path)
            os.rename(temporary, path)
        except Exception as error:
            self.notify.warning('Could not save personal Club settings: %s' % error)

    def getPersonalSetting(self, key):
        self._loadPersonalSettings()
        return bool(self.personalSettings.get(key, ClubGlobals.PERSONAL_SETTING_DEFAULTS.get(key, True)))

    def setPersonalSetting(self, key, enabled):
        if key not in ClubGlobals.PERSONAL_SETTING_KEYS:
            return
        self._loadPersonalSettings()
        self.personalSettings[key] = bool(enabled)
        self._savePersonalSettings()
        self._applyPersonalSettings()
        messenger.send('club-personal-setting-changed', [key, bool(enabled)])

    def _getClubThemeId(self):
        if not self.club:
            return 0
        icon = self.club.get('icon', {}) or {}
        try:
            return int(icon.get('themeId', 0) or 0)
        except (TypeError, ValueError):
            return 0

    def _stopClubNametagPulse(self):
        taskMgr.remove(self._clubNametagPulseTaskName)

    def _updateClubNametagPulse(self, task):
        localAvatar = getattr(base, 'localAvatar', None)
        if not localAvatar or not self.club or not self.getPersonalSetting(ClubGlobals.SETTING_SHOW_NAMETAG):
            return task.done

        try:
            from toontown.club.ClubIconGUI import ClubIconGUI
            if not ClubIconGUI.isAnimatedColor(self._getClubThemeId()):
                return task.done
            localAvatar.setToonTag(self._makeColoredClubTag())
        except Exception as error:
            self.notify.warning('Could not animate Club nametag colour: %s' % error)
            return task.done

        task.delayTime = 0.05
        return task.again

    def _makeColoredClubTag(self):
        if not self.club:
            return ''

        clubName = str(self.club.get('name', '') or '')
        if not clubName:
            return ''

        themeId = self._getClubThemeId()

        try:
            # Use the exact same full palette resolver as the Club icon GUI.
            from toontown.club.ClubIconGUI import ClubIconGUI
            color = ClubIconGUI.getColor(themeId)

            from pandac.PandaModules import TextProperties, TextPropertiesManager
            propertyName = 'AltisClubNametagColor-%s' % themeId
            properties = TextProperties()
            properties.setTextColor(*color)
            TextPropertiesManager.getGlobalPtr().setProperties(propertyName, properties)

            # DistributedPlayer's Toon tag supplies the size/shadow.  This
            # nested text property replaces only its old fixed brown colour.
            return '\1%s\1%s\2' % (propertyName, clubName)
        except Exception as error:
            self.notify.warning('Could not apply Club nametag colour: %s' % error)
            return clubName

    def _applyPersonalSettings(self):
        self._stopClubNametagPulse()
        localAvatar = getattr(base, 'localAvatar', None)
        if not localAvatar:
            return
        tag = ''
        showNametag = self.club and self.getPersonalSetting(ClubGlobals.SETTING_SHOW_NAMETAG)
        if showNametag:
            tag = self._makeColoredClubTag()
        try:
            localAvatar.setToonTag(tag)
        except Exception as error:
            self.notify.warning('Could not update Club nametag: %s' % error)
            return

        if showNametag:
            try:
                from toontown.club.ClubIconGUI import ClubIconGUI
                if ClubIconGUI.isAnimatedColor(self._getClubThemeId()):
                    taskMgr.doMethodLater(0.05, self._updateClubNametagPulse,
                                          self._clubNametagPulseTaskName)
            except Exception as error:
                self.notify.warning('Could not start Club nametag animation: %s' % error)

    def _showClubPopup(self, message):
        try:
            from toontown.chat.ChatGlobals import WTSystem
            base.localAvatar.displayWhisper(0, str(message), WTSystem)
        except:
            pass

    def openClubPanel(self):
        try:
            base.localAvatar.socialPanel.enter()
            base.localAvatar.socialPanel.showClubsTab()
            return
        except:
            pass
        messenger.send('open-club-panel')

    def openCreationGui(self, npc=None):
        from toontown.toon.gui.ClubCreationGUI import ClubCreationGUI
        return ClubCreationGUI(npc)

    def openShopGui(self, npc=None):
        from toontown.toon.gui.ClubShopGUI import ClubShopGUI
        return ClubShopGUI(npc)

    def _showInviteDialog(self, invite):
        try:
            from toontown.toontowngui import TTDialog
            text = '%s invited you to join\n%s.\n\nWould you like to join?' % (
                invite['inviterName'], invite['clubName'])
            dialog = TTDialog.TTGlobalDialog(
                doneEvent='clubInviteDialogDone',
                message=text,
                style=TTDialog.TwoChoice)
            dialog.show()

            def done(dialog=dialog, invite=invite):
                status = dialog.doneStatus
                self.ignore('clubInviteDialogDone')
                dialog.cleanup()
                self.respondToInvite(invite['clubId'], status == 'ok')
            self.acceptOnce('clubInviteDialogDone', done)
        except Exception as error:
            self.notify.warning('Could not open Club invite dialog: %s' % error)
