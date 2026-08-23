import hashlib
import hmac
import json
import os
import random
import time

from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD
from direct.distributed.PyDatagram import *
from direct.distributed.MsgTypes import CLIENTAGENT_EJECT, CLIENTAGENT_OPEN_CHANNEL, CLIENTAGENT_SET_CLIENT_ID, \
    CLIENTAGENT_SET_STATE, STATESERVER_OBJECT_SET_OWNER, STATESERVER_OBJECT_DELETE_RAM, CLIENTAGENT_ADD_POST_REMOVE, \
    CLIENTAGENT_ADD_SESSION_OBJECT, CLIENTAGENT_CLEAR_POST_REMOVES, CLIENTAGENT_CLOSE_CHANNEL, \
    CLIENTAGENT_REMOVE_SESSION_OBJECT
from direct.fsm.FSM import FSM
from panda3d.core import *
import requests

from toontown.distributed import OtpDoGlobals
from toontown.ai import HolidayGlobals
from toontown.makeatoon.NameGenerator import NameGenerator
from toontown.namepanel import NameCheck
from toontown.quest3.questlines.MainQuestLine import MainQuestLine
from toontown.rpc import ServerEnvAI
from toontown.toon.ToonDNA import ToonDNA
from toontown.toon.Experience import Experience
from toontown.toonbase import TTLocalizer, PermissionGlobals
from toontown.toonbase import ToontownGlobals, TTCCGlobals
from toontown.ai.NameCheckAI import judgeNamePattern
from toontown.district.DistrictGlobals import DistrictState, CSM_OVERRIDE_SPAWNING_DISTRICT_FACTOR, DistrictType
from toontown.uberdog.ClientServiceManagerGlobals import PreferDistrictMode

from toontown.uberdog.ToontownUberRepository import ToontownUberRepository
from toontown.uberdog.UberdogGlobalsUD import NET_MESSENGER_REQUEST_SPAWNING_SHARD_RESPONSE, \
    NET_MESSENGER_REQUEST_SPAWNING_SHARD
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.utils.RateLimiter import RateLimiter
from toontown.inventory.PotentialAvatarInventory import packPotentialAvatarDNA

accountDBType = "local"

_true = ['true', 'True', 't', 'T', '1', 'yes', 'Yes', 'YES']


def getDevCookie(cookie: int) -> str:
    return str(20000000 + (100 * cookie))


@DirectNotifyCategory()
class LocalAccountDB:
    def __init__(self, csm, air):
        self.csm = csm
        self.air = air  # type: ToontownUberRepository

    def lookup(self, websiteUserId, cookie, ip, callback, sender, permissions, csm):
        if __debug__:
            import os
            # this allows us to simply define dev csm in dev scripts
            runDevCsm = os.environ.get('CLASH_DEVCSM', ConfigVariableBool('want-dev-csm', False).getValue()) in _true
        else:
            runDevCsm = False

        if runDevCsm:
            # generate a 'unique' cookie via the dev 'cookie' passed in via the local client, then take the calculated
            # cookie int and make it into a str (this is very important, since the create account op makes this a str,
            #   and not doing so here means we will create yet another account with the same cookie value)
            devCookie = getDevCookie(int(cookie))
            devAccountCheck = LookupDevCSMAccountFSM(csm, sender)
            devAccountCheck.request('Start', cookie)

            response = {
                'success': True,
                'userId': devCookie,
                'websiteUserId': websiteUserId,
                'accountId': 0 if devAccountCheck.createAccount else devAccountCheck.accountId,
                'permissions': list(PermissionGlobals.Preset_All),  # Since we're a developer, give all the permissions!
            }
            callback(response)
            return

        if len(cookie) != 64:  # Cookies should be exactly 64 Characters long!
            callback({'success': False, 'reason': 122})
            return

        accountCheck = EnsureAccountFSM(csm, sender)
        accountCheck.request('Start', cookie)

        if accountCheck.createAccount:
            response = {
                'success': True,
                'userId': cookie,
                'accountId': 0,
                'websiteUserId': websiteUserId,
                'permissions': permissions,
            }
            callback(response)
            return response
        else:
            response = {
                'success': True,
                'userId': cookie,
                'accountId': int(accountCheck.accountId),
                'websiteUserId': websiteUserId,
                'permissions': permissions,
            }

            callback(response)
            return response

    def addNameRequest(self, avId, name):
        # add type a name
        self.notify.debug(f"name for avid {avId} requested: `{name}`")
        response = self.air.rpcClient.call('gs/names/toon/+', json={"avid": avId, "name": name})

        if not response or response.status_code != 200:
            # effectively 'pass' here since the website has recovery code that adds pending names it doesn't know about
            self.notify.debug(f"Unable to add name request from {avId} ({name})")

        return 'Success'

    def getNameStatus(self, _avId, _index, _wishname, callback):
        # check type a name
        self.notify.debug("debug: checking name from %s" %(_avId))

        if os.environ.get('CLASH_DEVCSM'):
            return callback("APPROVED", _wishname, "", _avId, _index)

        _response = self.air.rpcClient.call('gs/names/toon/check',
                                            json={"avid": _avId, "index": _index, "wishname": _wishname})

        if not _response or _response.status_code != 200:
            return
        response = _response.json()

        status = response.get("status")
        if status == -1:
            state = "REJECTED"
        elif status == 0:
            state = "PENDING"
        elif status == 1:
            state = "APPROVED"
        else:
            self.notify.debug("Get name status for av %s didnt return an expected value, got %s, setting to PENDING" % (
            _avId, str(status)))
            state = "ERROR"

        if not response.get("success"):
            state = "ERROR"
        callback(state, response.get('name'), response.get('denyreason'), _avId, _index)

    def removeNameRequest(self, avId):
        return


# --- FSMs ---
class OperationFSM(FSM):
    TARGET_CONNECTION = False

    def __init__(self, csm: 'ClientServicesManagerUD', target: int):
        self.csm = csm
        self.target = target

        super().__init__(self.__class__.__name__)

    def enterKill(self, reason=''):
        if self.TARGET_CONNECTION:
            self.csm.killConnection(self.target, reason)
        else:
            self.csm.killAccount(self.target, reason)
        self.demand('Off')

    def enterOff(self):
        try:
            if self.TARGET_CONNECTION:
                del self.csm.connection2fsm[self.target]
            else:
                del self.csm.account2fsm[self.target]
        except KeyError:
            print("keyerror CSMUD enterOff")
            pass


@DirectNotifyCategory()
class LookupDevCSMAccountFSM(OperationFSM):
    def enterStart(self, devClientId):
        if __debug__:
            import os
            # this allows us to simply define dev csm in dev scripts
            runDevCsm = os.environ.get('CLASH_DEVCSM', ConfigVariableBool('want-dev-csm', False).getValue()) in _true
        else:
            # TODO: figure out if QA also uses dev csm, but not running with __debug__
            runDevCsm = ConfigVariableBool('want-dev-csm', False).getValue()

        if not runDevCsm:
            self.notify.error("This operation is only valid on DevCSM!", exception=ValueError)
        # in the strange event we didn't make this cookie a str, go ahead and make it a str (or try to anyways)
        self.cookie = getDevCookie(int(devClientId))
        self.createAccount = False
        self.accountId = 0
        self.websiteUserId = int(devClientId)
        self.demand('Lookup')

    def enterLookup(self):
        query = self.csm.air.mongodb.astron.objects.find({"fields.ACCOUNT_ID": {"$eq": self.cookie, "$exists": True}})
        results = []
        for document in query:
            results.append(document)

        if len(results) == 0:
            self.createAccount = True
        elif len(results) == 1:
            if not results[0].get('_id'):
                self.notify.warning("First document linked to cookie %s does not have an ID!" % self.cookie)
                return

            if results[0].get('dclass') != "Account":
                self.notify.warning("First document linked to cookie %s is not an account object" % self.cookie)
                return

            self.accountId = results[0]['_id']
            self.websiteUserId = results[0]['fields']['WEBSITE_USER_ID']
        else:
            # eh, I can't really be bothered to try to fix the issue for any current local DB's
            # plus, they're local test db's that can be dropped + regenerated fairly easily anyways...
            self.notify.error(f"Detected issue with ACCOUNT_ID {self.cookie}; "
                              "repair operation not currently implemented for this!",
                              exception=NotImplementedError)


@DirectNotifyCategory()
class EnsureAccountFSM(OperationFSM):
    def enterStart(self, cookie):
        self.cookie = cookie
        self.createAccount = False
        self.accountId = 0
        self.websiteUserId = 0
        self.demand('Lookup')

    def enterLookup(self):
        query = self.csm.air.mongodb.astron.objects.find({"fields.ACCOUNT_ID": {"$eq": self.cookie, "$exists": True}})
        results = []
        for document in query:
            results.append(document)

        if len(results) == 0:
            self.createAccount = True
        elif len(results) == 1:
            if not results[0].get('_id'):
                self.notify.warning("First document linked to cookie %s does not have an ID!" % self.cookie)
                return

            if results[0].get('dclass') != "Account":
                self.notify.warning("First document linked to cookie %s is not an account object" % self.cookie)
                return

            self.accountId = results[0]['_id']
            self.websiteUserId = results[0]['fields']['WEBSITE_USER_ID']
        else:
            self.results = results
            self.demand('Repair')

    def enterRepair(self):
        # TODO: This operation is not safe anymore and should be removed
        self.levelTotals = {}
        self.notify.info("Beginning account repair operation for cookie %s with %d accounts" % (self.cookie, len(self.results)))
        for account in self.results:
            if not account.get('_id'):
                self.notify.warning("Document linked to cookie %s does not have an ID!" % self.cookie)
                continue

            if account.get('dclass') != "Account":
                self.notify.warning("Document %d linked to cookie %s is not an account object" % (account['_id'], self.cookie))
                continue

            # At this point, we already know that the object is an account object so we can index it directly
            self.levelTotals[account['_id']] = 0
            for avId in account['fields']['ACCOUNT_AV_SET']:
                if avId == 0:
                    continue

                toon = self.csm.air.mongodb.astron.objects.find({"_id": avId})[0]
                if toon.get('dclass') != "DistributedToon":
                    self.notify.warning("Toon %d linked to account %d was not a toon while repairing cookie %s!" % (avId, account['_id'], self.cookie))
                    continue

                exp = toon['fields']['setToonLevel']['level']
                self.levelTotals[account['_id']] += exp

        if len(self.levelTotals) == 0:
            # The accounts that are linked to the cookie must be corrupt
            self.createAccount = True
            return

        winner = max(self.levelTotals, key=self.levelTotals.get)
        self.notify.info("Account %d won with %d cumulative level" % (winner, self.levelTotals[winner]))
        self.accountId = winner
        for account in self.results:
            if account.get('_id'):
                if account['_id'] == winner:
                    continue

                self.notify.info("Cleaning up account %d" % account['_id'])
                self.csm.air.mongodb.astron.objects.delete_one({'_id': account['_id']})
            else:
                continue


@DirectNotifyCategory()
class LoginAccountFSM(OperationFSM):
    TARGET_CONNECTION = True

    def enterStart(self, websiteUserId, token, ip, permissions, muted, wantSpeedchatPlus, nameSubmissionLocked):
        self.websiteUserId = websiteUserId
        self.token = token
        self.ip = ip
        self.permissions = permissions
        self.muted = muted  # type: bool
        self.wantSpeedchatPlus = wantSpeedchatPlus
        self.nameSubmissionLocked = nameSubmissionLocked
        self.demand('QueryAccountDB')

    def enterQueryAccountDB(self):
        self.csm.accountDB.lookup(self.websiteUserId, self.token, self.ip, self.__handleLookup, self.target, self.permissions, self.csm)

    def __handleLookup(self, result):
        if not result.get('success'):
            self.csm.air.writeServerEvent('tokenRejected', self.target, self.token)
            self.demand('Kill', result.get('reason'))
            return

        self.websiteUserId = int(result.get('websiteUserId', 0))
        self.userId = result.get('userId', 0)
        self.accountId = result.get('accountId', 0)
        self.permissions = result.get('permissions', [])
        if self.accountId:
            self.demand('RetrieveAccount')
        else:
            self.demand('CreateAccount')

    def enterRetrieveAccount(self):
        self.csm.air.dbInterface.queryObject(self.csm.air.dbId, self.accountId, self.__handleRetrieve)

    def __handleRetrieve(self, dclass, fields):
        if dclass != self.csm.air.dclassesByName['AccountUD']:
            self.demand('CreateAccount')
            return

        self.account = fields
        self.demand('SetAccount')

    def enterCreateAccount(self):
        self.account = {
            'ACCOUNT_AV_SET': [0] * 6,
            'ACCOUNT_AV_SET_DEL': [],
            'WANT_SPEEDCHAT_PLUS': self.wantSpeedchatPlus,
            'CREATED': time.ctime(),
            'LAST_LOGIN': time.ctime(),
            'ACCOUNT_ID': str(self.userId),
            'WEBSITE_USER_ID': self.websiteUserId,
            'PERMISSIONS': self.permissions,
            'NAME_SUBMISSION_LOCKED': self.nameSubmissionLocked
        }
        self.csm.air.dbInterface.createObject(
            self.csm.air.dbId,
            self.csm.air.dclassesByName['AccountUD'],
            self.account,
            self.__handleCreate)

    def __handleCreate(self, accountId):
        if self.state != 'CreateAccount':
            self.notify.warning('Received a create account response outside of the CreateAccount state.')
            self.demand('Kill', 106)
            return

        if not accountId:
            self.notify.warning('Database failed to construct an account object!')
            self.demand('Kill', 106)
            return

        self.accountId = accountId
        self.csm.air.writeServerEvent('accountCreated', accountId)
        self.demand('SetAccount')

    def enterSetAccount(self):
        # If necessary, update their account information:
        if self.permissions is not None and set(self.account.get('PERMISSIONS', {})) != set(self.permissions):
            self.csm.air.dbInterface.updateObject(
                self.csm.air.dbId,
                self.accountId,
                self.csm.air.dclassesByName['AccountUD'],
                {'PERMISSIONS': self.permissions})
        if self.wantSpeedchatPlus != self.account.get('WANT_SPEEDCHAT_PLUS'):
            self.csm.air.dbInterface.updateObject(
                self.csm.air.dbId,
                self.accountId,
                self.csm.air.dclassesByName['AccountUD'],
                {'WANT_SPEEDCHAT_PLUS': self.wantSpeedchatPlus})
        if self.nameSubmissionLocked != self.account.get('NAME_SUBMISSION_LOCKED'):
            self.csm.air.dbInterface.updateObject(
                self.csm.air.dbId,
                self.accountId,
                self.csm.air.dclassesByName['AccountUD'],
                {'NAME_SUBMISSION_LOCKED': self.nameSubmissionLocked})
        # If there's anybody on the account, kill them for redundant login:
        datagram = PyDatagram()
        datagram.addServerHeader(
            self.csm.GetAccountConnectionChannel(self.accountId),
            self.csm.air.ourChannel,
            CLIENTAGENT_EJECT)
        datagram.addUint16(100)
        datagram.addString('This account has been logged in from elsewhere.')
        self.csm.air.send(datagram)

        # Next, add this connection to the account channel.
        datagram = PyDatagram()
        datagram.addServerHeader(
            self.target,
            self.csm.air.ourChannel,
            CLIENTAGENT_OPEN_CHANNEL)
        datagram.addChannel(self.csm.GetAccountConnectionChannel(self.accountId))
        self.csm.air.send(datagram)

        # Now set their sender channel to represent their account affiliation:
        datagram = PyDatagram()
        datagram.addServerHeader(
            self.target,
            self.csm.air.ourChannel,
            CLIENTAGENT_SET_CLIENT_ID)
        # Account ID in high 32 bits, 0 in low (no avatar):
        datagram.addChannel(self.accountId << 32)
        self.csm.air.send(datagram)

        # Un-sandbox them!
        datagram = PyDatagram()
        datagram.addServerHeader(
            self.target,
            self.csm.air.ourChannel,
            CLIENTAGENT_SET_STATE)
        datagram.addUint16(2)  # ESTABLISHED
        self.csm.air.send(datagram)

        # Update the last login timestamp:
        self.csm.air.dbInterface.updateObject(
            self.csm.air.dbId,
            self.accountId,
            self.csm.air.dclassesByName['AccountUD'],
            {'LAST_LOGIN': time.ctime(),
             'ACCOUNT_ID': str(self.userId)})

        if self.muted:
            self.notify.info(f'New muted account logged in: {self.accountId:d} (websiteUserId: {self.websiteUserId:d})')
            self.csm.air.netMessenger.send('accountMuted', [self.accountId])
        else:
            # for re-logins after mute has ended, send this again but with the second param `remove_instead` set to True
            self.csm.air.netMessenger.send('accountMuted', [self.accountId, True])

        self.notify.info(f"Web account ID logged in: {self.websiteUserId:d}")
        # We're done.
        self.csm.air.writeServerEvent('accountLogin', self.target, self.accountId, self.userId, self.websiteUserId)
        self.csm.sendUpdateToChannel(self.target, 'acceptLogin', [int(time.time()), 'success', self.account.get('PERMISSIONS', []), self.account.get('NAME_SUBMISSION_LOCKED', False)])
        self.demand('Off')


@DirectNotifyCategory()
class CreateAvatarFSM(OperationFSM):
    def enterStart(self, dna, index, tracks, pg, skipTutorial):
        # Basic sanity-checking:
        if index >= 6:
            self.demand('Kill', 107)
            return

        # Sanity-check for non 2-tracking
        if len(set([x for x in tracks if x is not None])) != 2:
            self.csm.air.writeServerEvent(
                'suspicious',
                f'Account {self.target} tried to create a Toon with track access {tracks}!'
            )
            self.demand('Kill', 107)
            return

        tempDna = ToonDNA()

        if not tempDna.isValidNetString(dna):
            self.demand('Kill', 107)
            return

        tempDna.makeFromNetString(dna)

        def checkForHoliday(checkedHoliday):
            if checkedHoliday in HolidayGlobals.YEARLY_HOLIDAYS_DICT:
                holidayRange = HolidayGlobals.YEARLY_HOLIDAYS_DICT[checkedHoliday]
                start = holidayRange.startDatetime
                end = holidayRange.endDatetime
                now = holidayRange.nowDatetime
                # if the holiday is both active and our current time is within the holiday, return True
                if holidayRange.active and start < now < end:
                    return True
            return False

        if tempDna.getAnimal() == 'turkey':
            if not any(checkForHoliday(x) for x in (ToontownGlobals.APRIL_FOOLS, ToontownGlobals.THANKSGIVING)): # No turkeys on non-turkey day and non-april fools
                self.demand('Kill', 107)
                return

        self.index = index
        self.dna = dna
        self.pg = pg
        self.trackAccess = [0, 0, 0, 0, 0, 0, 0, 0]
        self.achievements = []
        self.trainingPoints = [0, 0, 0, 0, 0, 0, 0, 0]
        self.choices = []
        self.skipTutorial = skipTutorial
        self.quests, self.questHistory = MainQuestLine.getStarterQuestData(skipTutorial=skipTutorial)
        enum = 0
        achievementIds = [24, 25, 26, 27, 93, 94, 28, 29]
        for track in tracks:
            if enum < 2:
                self.trackAccess[track] = 1
                self.trainingPoints[track] = 2
            enum += 1
            self.choices.append(track)
            self.achievements.append(achievementIds[track])

        # Okay, we're good to go, let's query their account.
        self.demand('RetrieveAccount')

    def enterRetrieveAccount(self):
        self.csm.air.dbInterface.queryObject(
            self.csm.air.dbId, self.target, self.__handleRetrieve)

    def __handleRetrieve(self, dclass, fields):
        if dclass != self.csm.air.dclassesByName['AccountUD']:
            self.demand('Kill', 107)
            return

        self.account = fields

        self.avList = self.account['ACCOUNT_AV_SET']
        # Sanitize:
        self.avList = self.avList[:6]
        self.avList += [0] * (6-len(self.avList))

        # Make sure the index is open:
        if self.avList[self.index]:
            self.demand('Kill', 107)
            return

        # Okay, there's space. Let's create the avatar!
        self.demand('CreateAvatar')

    def enterCreateAvatar(self):
        dna = ToonDNA()
        dna.makeFromNetString(self.dna)
        try:
            colorString = TTLocalizer.NumToColor[dna.headColor]
        except:
            colorString = "Colorful"
        animalType = TTLocalizer.AnimalToSpecies[dna.getAnimal()]
        name = ' '.join((colorString, animalType))

        toonFields = {
            'setName': (name,),
            'WishNameState': ('OPEN',),
            'WishName': ('',),
            'setDNAString': (self.dna,),
            'setDISLid': (self.target,),
        }

        maxHp = 15

        exp = Experience()

        for i, t in enumerate(self.trackAccess):
            if t:
                chosenExp = 0
                exp[i] = chosenExp

        toonFields['setExperience'] = (exp,)
        toonFields['setTrackAccess'] = (self.trackAccess,)
        toonFields['setSpentTrainingPoints'] = (self.trainingPoints,)
        toonFields['setAchievements'] = (self.achievements,)
        toonFields['setMaxHp'] = (maxHp,)
        toonFields['setHp'] = (maxHp,)
        # TODO: check if this needs to change
        toonFields['setRawQuestReferences'] = (self.quests,)
        toonFields['setRawQuestHistory'] = (self.questHistory,)
        if self.skipTutorial:
            toonFields['setQuestCarryLimit'] = (4,)
        toonFields['setTutorialAck'] = (self.skipTutorial,)
        toonFields['setCreatedAt'] = (int(time.time()),)

        self.csm.air.dbInterface.createObject(
            self.csm.air.dbId,
            self.csm.air.dclassesByName['DistributedToonUD'],
            toonFields,
            self.__handleCreate)

    def __handleCreate(self, avId):
        if not avId:
            self.demand('Kill', 108)
            return

        self.avId = avId
        self.demand('StoreAvatar')

    def enterStoreAvatar(self):
        # Associate the avatar with the account...
        self.avList[self.index] = self.avId
        self.csm.air.dbInterface.updateObject(
            self.csm.air.dbId,
            self.target,
            self.csm.air.dclassesByName['AccountUD'],
            {'ACCOUNT_AV_SET': self.avList},
            {'ACCOUNT_AV_SET': self.account['ACCOUNT_AV_SET']},
            self.__handleStoreAvatar)

    def __handleStoreAvatar(self, fields):
        if fields:
            self.demand('Kill', 108)
            return

        # Otherwise, we're done!
        self.csm.air.writeServerEvent('avatarCreated', self.avId, self.target, self.dna.hex(), self.index)
        self.csm.sendUpdateToAccountId(self.target, 'createAvatarResp', [self.avId])
        self.demand('Off')


@DirectNotifyCategory()
class AvatarOperationFSM(OperationFSM):
    POST_ACCOUNT_STATE = 'Off'  # This needs to be overridden.

    def enterRetrieveAccount(self):
        # Query the account:
        self.csm.air.dbInterface.queryObject(
            self.csm.air.dbId, self.target, self.__handleRetrieve)

    def __handleRetrieve(self, dclass, fields):
        if dclass != self.csm.air.dclassesByName['AccountUD']:
            self.demand('Kill', 106)
            return

        self.account = fields

        self.avList = self.account['ACCOUNT_AV_SET']
        # Sanitize:
        self.avList = self.avList[:6]
        self.avList += [0] * (6-len(self.avList))

        self.demand(self.POST_ACCOUNT_STATE)


@DirectNotifyCategory()
class GetAvatarsFSM(AvatarOperationFSM):
    POST_ACCOUNT_STATE = 'QueryAvatars'

    def enterStart(self):
        self.demand('RetrieveAccount')

    def enterQueryAvatars(self):
        self.pendingAvatars = set()
        self.avatarFields = {}
        for avId in self.avList:
            if avId:
                self.pendingAvatars.add(avId)

                def response(dclass, fields, avId=avId):
                    if self.state != 'QueryAvatars':
                        return
                    if dclass != self.csm.air.dclassesByName['DistributedToonUD']:
                        self.demand('Kill', 109)
                        return
                    self.avatarFields[avId] = fields
                    self.pendingAvatars.remove(avId)
                    if not self.pendingAvatars:
                        self.demand('SendAvatars')

                self.csm.air.dbInterface.queryObject(
                    self.csm.air.dbId,
                    avId,
                    response)

        if not self.pendingAvatars:
            self.demand('SendAvatars')

    def enterSendAvatars(self):
        potentialAvs = []
        avCount = len([x for x in self.avList if x != 0])

        def finishUpdate():
            if len(potentialAvs) == avCount:
                self.csm.sendUpdateToAccountId(self.target, 'setAvatars', [potentialAvs])
                self.demand('Off')

        avidToFields = {}
        avidToName = {}

        def getPackedDNA(avId, fields):
            try:
                inventory = self.csm.air.inventoryDatabase.queryInventory(avId)
                equippedItems = inventory.cache.getEquippedItems() if inventory else []
                return packPotentialAvatarDNA(fields['setDNAString'][0], equippedItems)
            except Exception as error:
                self.notify.warning('Unable to load equipped items for avatar %s: %s' % (avId, error))
                return fields['setDNAString'][0]

        for avId, fields in list(self.avatarFields.items()):
            avidToFields[avId] = fields
            index = self.avList.index(avId)
            wishName = fields.get('WishName', [''])[0]
            wishNameState = fields.get('WishNameState', [''])[0]
            global nameState
            name = fields['setName'][0]
            nametagStyle = 1  # TODO: Make this work with hammerspace, if we dont rework the whole main menu
            club = fields.get('setToonClubs', [[]])[0]
            avidToName[avId] = name
            nameState = 0

            if wishNameState == 'OPEN':
                nameState = 1
            elif wishNameState in ['PENDING', 'APPROVED', 'ERROR']:
                def nameStatusCallback(state, name, denyreason, _avid, _index):
                    _fields = avidToFields[_avid]
                    nameState = 0
                    name = avidToName[avId]

                    self.csm.air.dbInterface.updateObject(
                        self.csm.air.dbId,
                        _avid,
                        self.csm.air.dclassesByName['DistributedToonUD'],
                        {'WishNameState': [state]}
                    )
                    if state == 'PENDING':
                        nameState = 2
                    elif state == 'APPROVED':
                        nameState = 3
                        name = _fields['WishName'][0]
                    elif state == 'REJECTED':
                        nameState = 4
                    elif state == 'ERROR':
                        nameState = 2

                    potentialAvs.append([_avid, name, getPackedDNA(_avid, _fields), _index, nameState, denyreason, _fields['setHp'][0], _fields['setMaxHp'][0], nametagStyle, club])
                    finishUpdate()

                self.csm.accountDB.getNameStatus(avId, index, wishName, nameStatusCallback)
                continue
            elif wishNameState == "PENDING_SUBMIT":
                nameState = 2
                # This is a hack to make sure that, eventually, the website does get the new toon name request
                # if for some reason it fails the first time. This is required so that we're triple sure that the
                # website _will not_ get into a state where it'll just accept the new name without actually going
                # into a pending review.
                try:
                    # TODO (maybe): only make this call on non-local envs
                    _response = simbase.air.rpcClient.call('gs/names/toon/+', json={"avid": avId, "name": fields.get('WishName')[0]})
                    if not _response:
                        self.notify.warning('GSAPI for toon name failed.')
                    elif _response.status_code == 200:
                        simbase.air.dbInterface.updateObject(
                            self.csm.air.dbId,
                            avId,
                            self.csm.air.dclassesByName['DistributedToonUD'],
                            {'WishNameState': ["PENDING"]}
                        )
                    elif _response.status_code == 400:
                        self.notify.warning('Received 400 status_code from GS toon name API, indicating something is '
                                            '_really_ wrong.')
                    else:
                        self.notify.warning('Received non-200 status_code from GS toon name API.')
                except Exception as e:
                    import sentry_sdk
                    sentry_sdk.capture_exception(e)
                    # Just pass here, and let the next log in deal with submitting again
                    self.notify.warning('Unable to contact GS toon name API.')

                # send RPC to website with new name
                # if that fails, just pass and wait again for the next relog
                pass
            elif wishNameState == 'REJECTED':
                nameState = 4
            potentialAvs.append([avId, name, getPackedDNA(avId, fields), index, nameState, 'N/A', fields['setHp'][0], fields['setMaxHp'][0], nametagStyle, club])

        finishUpdate()


# This inherits from GetAvatarsFSM, because the delete operation ends in a
# setAvatars message being sent to the client.
@DirectNotifyCategory()
class DeleteAvatarFSM(GetAvatarsFSM):
    POST_ACCOUNT_STATE = 'ProcessDelete'

    def enterStart(self, avId):
        self.avId = avId
        GetAvatarsFSM.enterStart(self)

    def enterProcessDelete(self):
        if self.avId not in self.avList:
            self.demand('Kill', 107)
            return

        index = self.avList.index(self.avId)
        self.avList[index] = 0

        avsDeleted = list(self.account.get('ACCOUNT_AV_SET_DEL', []))
        if len(avsDeleted) >= 100:
            avsDeleted.pop(0)
        avsDeleted.append([self.avId, int(time.time())])

        self.csm.air.dbInterface.updateObject(
            self.csm.air.dbId,
            self.target,
            self.csm.air.dclassesByName['AccountUD'],
            {'ACCOUNT_AV_SET': self.avList,
             'ACCOUNT_AV_SET_DEL': avsDeleted},
            {'ACCOUNT_AV_SET': self.account['ACCOUNT_AV_SET'],
             'ACCOUNT_AV_SET_DEL': self.account['ACCOUNT_AV_SET_DEL']},
            self.__handleDelete)

    def __handleDelete(self, fields):
        if fields:
            self.demand('Kill', 106)
            return

        dclass = self.csm.air.dclassesByName['TTFriendsManagerUD']
        doId = OtpDoGlobals.OTP_DO_ID_TT_FRIENDS_MANAGER
        datagram = dclass.aiFormatUpdate('clearList', doId, doId, self.csm.air.ourChannel, [self.avId])
        self.csm.air.send(datagram)

        self.csm.air.netMessenger.send('onAvatarDeleted', [self.avId])
        self.csm.air.writeServerEvent('avatarDeleted', self.avId, self.target)
        self.demand('QueryAvatars')


@DirectNotifyCategory()
class SetNameTypedFSM(AvatarOperationFSM):
    POST_ACCOUNT_STATE = 'RetrieveAvatar'

    def enterStart(self, avId, name):
        self.avId = avId
        self.name = name
        self.demand('RetrieveAccount')

    def enterRetrieveAvatar(self):
        if self.account and self.account.get('NAME_SUBMISSION_LOCKED', False):
            self.demand('Kill', 107)
            return

        if self.avId:
            if self.avId not in self.avList:
                self.demand('Kill', 107)
                return

            self.csm.air.dbInterface.queryObject(self.csm.air.dbId, self.avId, self.__handleAvatar)
        else:
            # avId is 0 (new Toon), so we can skip the avatar check
            self.demand('JudgeName')

    def __handleAvatar(self, dclass, fields):
        if dclass != self.csm.air.dclassesByName['DistributedToonUD']:
            self.demand('Kill', 109)
            return

        if fields['WishNameState'][0] != 'OPEN':
            self.demand('Kill', 110)
            return

        self.demand('JudgeName')

    def enterJudgeName(self):
        # Let's see if the name is valid; None if all checks pass:
        status = NameCheck.checkName(self.name) is None

        if self.avId and status:
            resp = self.csm.accountDB.addNameRequest(self.avId, self.name)
            if resp != 'Success':
                self.notify.debug("enterJudgeName: FAILURE")
                status = False
            else:
                self.notify.debug(f"enterJudgeName: SUCCESS {self.name}")
                self.csm.air.dbInterface.updateObject(
                    self.csm.air.dbId,
                    self.avId,
                    self.csm.air.dclassesByName['DistributedToonUD'],
                    {'WishNameState': ('PENDING',),
                     'WishName': (self.name,)})

        if self.avId:
            self.csm.air.writeServerEvent('avatarWishname', self.avId, self.name)

        self.csm.sendUpdateToAccountId(self.target, 'setNameTypedResp', [self.avId, status])
        self.notify.debug(f"enterJudgeName: {self.avId} {status}")
        self.demand('Off')


class SetNamePatternFSM(AvatarOperationFSM):
    notify = directNotify.newCategory('SetNamePatternFSM')
    POST_ACCOUNT_STATE = 'RetrieveAvatar'

    def enterStart(self, avId, pattern):
        self.avId = avId
        self.pattern = pattern

        if self.avId:
            self.demand('RetrieveAccount')
            return

        # Hmm, self.avId was 0. Okay, let's just cut to the judging:
        self.demand('SetName')

    def enterRetrieveAvatar(self):
        if self.avId and self.avId not in self.avList:
            self.demand('Kill', 107)
            return

        self.csm.air.dbInterface.queryObject(self.csm.air.dbId, self.avId,
                                             self.__handleAvatar)

    def __handleAvatar(self, dclass, fields):
        if dclass != self.csm.air.dclassesByName['DistributedToonUD']:
            self.demand('Kill', 109)
            return

        if fields['WishNameState'][0] != 'OPEN':
            self.demand('Kill', 110)
            return

        self.demand('SetName')

    def enterSetName(self):
        status, name = judgeNamePattern(self.pattern, self.csm.nameGenerator)

        if status and self.avId:
            self.csm.air.dbInterface.updateObject(
                self.csm.air.dbId,
                self.avId,
                self.csm.air.dclassesByName['DistributedToonUD'],
                {'WishNameState': ('',),
                 'WishName': ('',),
                 'setName': (name,)})

            self.csm.air.writeServerEvent('avatarWishname', self.avId, name)

        self.csm.sendUpdateToAccountId(self.target, 'setNamePatternResp', [self.avId, status])
        self.demand('Off')


@DirectNotifyCategory()
class AcknowledgeNameFSM(AvatarOperationFSM):
    POST_ACCOUNT_STATE = 'GetTargetAvatar'

    def enterStart(self, avId):
        self.avId = avId
        self.demand('RetrieveAccount')

    def enterGetTargetAvatar(self):
        # Make sure the target avatar is part of the account:
        if self.avId not in self.avList:
            self.demand('Kill', 107)
            return

        self.csm.air.dbInterface.queryObject(self.csm.air.dbId, self.avId,
                                             self.__handleAvatar)

    def __handleAvatar(self, dclass, fields):
        if dclass != self.csm.air.dclassesByName['DistributedToonUD']:
            self.demand('Kill', 109)
            return

        # Process the WishNameState change.
        wishNameState = fields['WishNameState'][0]
        wishName = fields['WishName'][0]
        name = fields['setName'][0]

        if wishNameState == 'APPROVED':
            wishNameState = ''
            name = wishName
            wishName = ''
            self.csm.accountDB.removeNameRequest(self.avId)
        elif wishNameState == 'REJECTED':
            wishNameState = 'OPEN'
            wishName = ''
            self.csm.accountDB.removeNameRequest(self.avId)
        else:
            self.demand('Kill', "Tried to acknowledge name on an avatar in %s state!" % wishNameState)
            return

        # Push the change back through:
        self.csm.air.dbInterface.updateObject(
            self.csm.air.dbId,
            self.avId,
            self.csm.air.dclassesByName['DistributedToonUD'],
            {'WishNameState': (wishNameState,),
             'WishName': (wishName,),
             'setName': (name,)},
            {'WishNameState': fields['WishNameState'],
             'WishName': fields['WishName'],
             'setName': fields['setName']})

        self.csm.sendUpdateToAccountId(self.target, 'acknowledgeAvatarNameResp', [])
        self.demand('Off')


@DirectNotifyCategory()
class LoadAvatarFSM(AvatarOperationFSM):
    POST_ACCOUNT_STATE = 'GetTargetAvatar'

    def __init__(self, csm: 'ClientServicesManagerUD', target):
        super().__init__(csm, target)
        self.avId: int = 0
        self.preferDistrictMode: PreferDistrictMode = PreferDistrictMode.DefaultDistrict

    def enterStart(self, avId: int, preferDistrictMode: PreferDistrictMode):
        self.avId = avId
        self.preferDistrictMode = preferDistrictMode
        self.demand('RetrieveAccount')

    def enterGetTargetAvatar(self):
        # Make sure the target avatar is part of the account:
        if self.avId not in self.avList:
            self.demand('Kill', 107)
            return

        self.csm.air.dbInterface.queryObject(self.csm.air.dbId, self.avId,
                                             self.__handleAvatar)

    def __handleAvatar(self, dclass, fields):
        if dclass != self.csm.air.dclassesByName['DistributedToonUD']:
            self.demand('Kill', 109)
            return

        self.avatar = fields
        self.demand('SetAvatar')

    def enterSetAvatarTask(self, channel, task):
        # Finally, grant ownership and shut down.
        datagram = PyDatagram()
        datagram.addServerHeader(self.avId, self.csm.air.ourChannel, STATESERVER_OBJECT_SET_OWNER)
        datagram.addChannel(self.target << 32 | self.avId)
        self.csm.air.send(datagram)

        self.csm.air.writeServerEvent('avatarChosen', self.avId, self.target)
        self.demand('Off')
        return task.done

    def enterSetAvatar(self):
        channel = self.csm.GetAccountConnectionChannel(self.target)

        # First, give them a POSTREMOVE to unload the avatar, just in case they
        # disconnect while we're working.
        datagramCleanup = PyDatagram()
        datagramCleanup.addServerHeader(self.avId, channel, STATESERVER_OBJECT_DELETE_RAM)
        datagramCleanup.addUint32(self.avId)
        datagram = PyDatagram()
        datagram.addServerHeader(channel, self.csm.air.ourChannel, CLIENTAGENT_ADD_POST_REMOVE)
        datagram.addBlob(datagramCleanup.getMessage())
        self.csm.air.send(datagram)

        # grab a list of all available districts to spawn into
        allDistrictsData = self.csm.air.districtTracker.districts.values()  # allows us to only pull once per av OP

        # get all online non-diagnostic districts
        onlineDistricts = [data.shardId for data in allDistrictsData if data.state == DistrictState.ONLINE]
        """
        # uh, might as well make sure the diagnostic districts aren't also offline for whatever reason
        diagnosticsDistricts = [data['shardId'] for data in allDistrictsData if data['diagnosticsDistrict']
                                and data['status'] != DistrictState.OFFLINE]
        # TODO: check to see if we want admins to randomly log into draining districts, and if so, do something different with this
        if Permission.Staff in self.account.get("PERMISSIONS", []):
            # Account has admin access; add draining districts into the list (if not diagnostic district, though
            #  I also can't see why a diagnostic district would get into a closed state either...)
            onlineDistricts.extend([data['shardId'] for data in allDistrictsData if not data['diagnosticsDistrict'] and data['status'] == DistrictState.CLOSED])
        """

        if not len(onlineDistricts):
            # If no available districts, kill connection
            self.demand('Kill', 626)
            return

        # Decide if we should use the default spawning district, or the lowest population one
        shardId = None
        if random.random() > CSM_OVERRIDE_SPAWNING_DISTRICT_FACTOR and self.preferDistrictMode == PreferDistrictMode.DefaultDistrict:
            shardId = self.csm.spawningDistrict
            self.notify.debug(f"Choosing spawning shard {shardId} for avatar {self.avId}.")
        else:
            self.notify.debug(f"Not using spawning shard {shardId} for avatar {self.avId}.")

        if shardId is None or shardId == 0:
            # choose the lowest pop district
            lowestPop = None
            for shard in allDistrictsData:
                if shard.districtType != DistrictType.GAME:
                    continue
                if shard.shardId in onlineDistricts and (lowestPop is None or shard.population < lowestPop):
                    shardId = shard.shardId
                    self.notify.debug(f"Shard {shardId} has pop {shard.population}, lower than {lowestPop}.")
                    lowestPop = shard.population
            self.notify.debug(f"Choosing shard {shardId} with pop {lowestPop} for avatar {self.avId}.")

        # Activate the avatar on the DBSS:
        self.csm.air.sendActivate(self.avId, 0, 0, self.csm.air.dclassesByName['DistributedToonUD'], {
            'setPermissions': [self.account.get('PERMISSIONS', [])],
            'setSpeedchatPlus': [self.account.get('WANT_SPEEDCHAT_PLUS', True)],
            # we send the shardId here because its an easy enough way for us to send it w/o potentially screwing with Astron SET_LOCATION bits immediately
            'setCurrentShard': [shardId]
        })

        # Next, add them to the avatar channel:
        datagram = PyDatagram()
        datagram.addServerHeader(channel, self.csm.air.ourChannel, CLIENTAGENT_OPEN_CHANNEL)
        datagram.addChannel(self.csm.GetPuppetConnectionChannel(self.avId))
        self.csm.air.send(datagram)

        # Now set their sender channel to represent their account affiliation:
        datagram = PyDatagram()
        datagram.addServerHeader(channel, self.csm.air.ourChannel, CLIENTAGENT_SET_CLIENT_ID)
        datagram.addChannel(self.target << 32 | self.avId)
        self.csm.air.send(datagram)

        # Finally, make the avatar a session object:
        datagram = PyDatagram()
        datagram.addServerHeader(channel, self.csm.air.ourChannel, CLIENTAGENT_ADD_SESSION_OBJECT)
        datagram.addUint32(self.avId)
        self.csm.air.send(datagram)

        # Eliminate race conditions.
        taskMgr.doMethodLater(0.2, self.enterSetAvatarTask, 'avatarTask-%s' % (self.avId), extraArgs=[channel],
                              appendTask=True)


@DirectNotifyCategory()
class UnloadAvatarFSM(OperationFSM):
    def enterStart(self, avId):
        self.avId = avId

        # We don't even need to query the account, we know the avatar is being played!
        self.demand('UnloadAvatar')

    def enterUnloadAvatar(self):
        channel = self.csm.GetAccountConnectionChannel(self.target)

        dclass = self.csm.air.dclassesByName['TTFriendsManagerUD']
        doId = OtpDoGlobals.OTP_DO_ID_TT_FRIENDS_MANAGER
        datagram = dclass.aiFormatUpdate('goingOffline', doId, doId, self.csm.air.ourChannel, [self.avId])
        self.notify.debug(f"enterUnloadAvatar(): sending 'goingOffline' for avatar {self.avId} via dclass lookup.")
        self.csm.air.send(datagram)

        # Clear off POSTREMOVE:
        datagram = PyDatagram()
        datagram.addServerHeader(channel, self.csm.air.ourChannel, CLIENTAGENT_CLEAR_POST_REMOVES)
        self.csm.air.send(datagram)

        # Remove avatar channel:
        datagram = PyDatagram()
        datagram.addServerHeader(channel, self.csm.air.ourChannel, CLIENTAGENT_CLOSE_CHANNEL)
        datagram.addChannel(self.csm.GetPuppetConnectionChannel(self.avId))
        self.csm.air.send(datagram)

        # Reset sender channel:
        datagram = PyDatagram()
        datagram.addServerHeader(channel, self.csm.air.ourChannel, CLIENTAGENT_SET_CLIENT_ID)
        datagram.addChannel(self.target<<32)
        self.csm.air.send(datagram)

        # Remove the avatar as a session object
        datagram = PyDatagram()
        datagram.addServerHeader(channel, self.csm.air.ourChannel, CLIENTAGENT_REMOVE_SESSION_OBJECT)
        datagram.addUint32(self.avId)
        self.csm.air.send(datagram)

        # Unload avatar object:
        datagram = PyDatagram()
        datagram.addServerHeader(self.avId, channel, STATESERVER_OBJECT_DELETE_RAM)
        datagram.addUint32(self.avId)
        self.csm.air.send(datagram)

        # Done!
        self.csm.air.writeServerEvent('avatarUnload', self.avId)
        self.demand('Off')


ip_check_endpoint = os.environ.get("API_IP_CHECKER_ENDPOINT", "https://ip-checker.corpclash.com")


@DirectNotifyCategory()
class ClientServicesManagerUD(DistributedObjectGlobalUD):
    def __init__(self, air):
        super().__init__(air)
        self.air = air  # type: ToontownUberRepository

        # For processing name patterns.
        self.nameGenerator = NameGenerator()

        # Temporary HMAC key:
        self.key = os.environ.get('CHALLENGE_KEY')

        # Rate limiters to prevent spamming
        self.rateLimiters = {}

        self.blacklistedHWIDs = []
        csmid = ConfigVariableInt('csm-id', 4211).getValue()
        self.__csmId = csmid
        self.context = int(f'{csmid}00000')

        self.__pendingChallenges = {}
        self.__solvedChallenges = {}

        self._spawningDistrict = 0

    def announceGenerate(self):
        print("DEBUG: ClientServicesManagerUD announceGenerate")
        """
        Handle all required fields having been filled in.
        """
        DistributedObjectGlobalUD.announceGenerate(self)

        # These keep track of the connection/account IDs currently undergoing an
        # operation on the CSM. This is to prevent (hacked) clients from firing up more
        # than one operation at a time, which could potentially lead to exploitation
        # of race conditions.
        self.connection2fsm = {}
        self.account2fsm = {}
        self.pendingLogins = {}

        # Instantiate our account DB interface:
        self.accountDB = LocalAccountDB(self, self.air)

        # we can now accept requests for our csmID
        # make sure we tell the loadBalancer to remove us if we dc for a bit
        datagram = self.air.netMessenger.prepare('csmRespondId', [
            self.air.ourChannel, 0
        ])
        self.air.addPostRemove(datagram)
        # accept the request message
        self.air.netMessenger.accept('csmRequestId', self, self.__handleRequestCSMID)
        # also send it now, should the LB be up already (it normally should)
        self.__handleRequestCSMID()

        self.air.netMessenger.accept(NET_MESSENGER_REQUEST_SPAWNING_SHARD_RESPONSE, self, self._updateSpawningDistrict)

    def killConnection(self, connId, reason):
        datagram = PyDatagram()
        datagram.addServerHeader(connId, self.air.ourChannel, CLIENTAGENT_EJECT)
        datagram.addUint16(reason)
        datagram.addString("An authentication error occurred.")
        self.air.send(datagram)

    def killConnectionFSM(self, connId):
        fsm = self.connection2fsm.get(connId)

        if not fsm:
            self.notify.warning('Tried to kill connection %d for duplicate FSM, but none exists!' % connId)
            return

        self.killConnection(connId, 103)

    def killAccount(self, accountId, reason):
        self.killConnection(self.GetAccountConnectionChannel(accountId), reason)

    def killAccountFSM(self, accountId):
        fsm = self.account2fsm.get(accountId)
        if not fsm:
            self.notify.warning('Tried to kill account %d for duplicate FSM, but none exists!' % (accountId))
            return

        self.killAccount(accountId, 103)

    def runAccountFSM(self, fsmtype, *args):
        sender = self.air.getAccountIdFromSender()

        if not sender:
            self.killAccount(sender, 1)

        if sender in self.account2fsm:
            self.killAccountFSM(sender)
            return

        self.account2fsm[sender] = fsmtype(self, sender)
        self.account2fsm[sender].request('Start', *args)

    def requestChallenge(self):
        sender = self.air.getMsgSender()
        challenge = TTCCGlobals.getRandomSpecialSecret()
        self.__pendingChallenges[sender] = challenge
        self.sendUpdateToChannel(sender, 'requestChallengeResponse', [challenge])

    def requestSolveChallenge(self, solved):
        sender = self.air.getMsgSender()

        if sender not in self.__pendingChallenges:
            self.notify.warning(f"Sender {sender} attempted to request solved challenge 2.0 without having a pending challenge.")
            self.killConnection(sender, 122)
            return

        # grab reference
        challenge = self.__pendingChallenges[sender]

        # cleanup/consume challenge
        del self.__pendingChallenges[sender]

        # do the solve on our side
        ourSolved = TTCCGlobals.getSpecialSecret(challenge)

        # check if the client solved it correctly
        success = ourSolved == int(solved)
        if not success:
            # no patrick mayonnaise is not an instrument
            self.notify.warning(f"Sender {sender} failed to solve challenge 2.0! expected: {ourSolved}, got: {int(solved)}")
            self.killConnection(sender, 122)
            return

        # ok you seem legit
        self.__solvedChallenges[sender] = True
        self.sendUpdateToChannel(sender, 'requestSolveChallengeResponse', [])

    def login(self, cookie, authKey, clientDateTime):
        sender = self.air.getMsgSender()

        if __debug__:
            import os
            runDevCsm = os.environ.get('CLASH_DEVCSM', ConfigVariableBool('want-dev-csm', False).getValue()) in _true
        else:
            runDevCsm = ConfigVariableBool('want-dev-csm', False).getValue()

        if not runDevCsm:
            if sender not in self.__solvedChallenges:
                self.notify.warning(f"Sender {sender} attempted to login without solving challenge 2.0.")
                self.killConnection(sender, 122)
                return
            del self.__solvedChallenges[sender]

            # if the client time is more than five minutes out of sync from the servers, kill the connection
            serverDateTime = int(time.time())
            if abs(clientDateTime - serverDateTime) > 300:
                self.killConnection(sender, 129)

        if runDevCsm:
            muted = False
            cookie = cookie.split("#")[0]
            try:
                int(cookie, base=10)
            except Exception:
                self.notify.warning("Developer client number passed to CSM is not an integer! Value: {}".format(cookie))
                return
            self.connection2fsm[sender] = LoginAccountFSM(self, sender)
            self.connection2fsm[sender].request(
                'Start',
                int(cookie, base=10) & 0xFFFFFFFF,
                cookie,
                '',
                list(PermissionGlobals.Preset_All),
                muted,
                True,
                False,
            )
            return

        hwid = cookie.split("#")[1]
        backupCookie = cookie.split("#")[0]
        cookie = cookie.split("#")[0]
        self.pendingLogins[self.context] = (sender, hwid, backupCookie, cookie, authKey)

        datagram = PyDatagram()
        datagram.addServerHeader(sender, self.air.ourChannel, OtpDoGlobals.CLIENTAGENT_GET_NETWORK_ADDRESS)
        datagram.addUint32(self.context)
        self.air.send(datagram)
        self.air.writeServerEvent('login-begin', sender)
        taskMgr.doMethodLater(10, self.completeLogin, 'loginTimeout-%d' % (self.context), extraArgs=[self.context, ''])
        self.context += 1

    def completeLogin(self, context, ip):
        self.notify.info(f"Begin login ctx {context}")
        login = self.pendingLogins.get(context)
        if not login:
            return

        sender = login[0]
        hwid = login[1]
        backupCookie = login[2]
        cookie = login[3]
        authKey = login[4]
        del self.pendingLogins[context]
        taskMgr.remove('loginTimeout-%d' % context)

        self.notify.info(f"got cookie {cookie}")
        _response = self.air.rpcClient.call('gs/processlogin', json={"hwid": hwid, "token": cookie})
        try:
            if _response.status_code >= 500:
                self.notify.warning(f"Website seems to have died. Ejecting client")
                self.killConnection(sender, 122)
                return

            success = _response.status_code == 200

            self.air.writeServerEvent('login-response', success)
            if not success:
                self.notify.warning(f"Website returned status code {_response.status_code}, which is not success. Ejecting client. ({str(_response.json())})")
                self.killConnection(sender, 122)
                return
        except AttributeError:
            self.notify.warning(f"Website seems to have died. Ejecting client")
            self.killConnection(sender, 122)
            return

        response = _response.json()

        if not response.get("status"):
            self.notify.warning(f"processLogin failed for {sender}: {response.get('friendlyreason')}")
            self.air.writeServerEvent('client-token-rejected', sender)
            self.killConnection(sender, 122)
            return

        if not response.get("realtoken"):
            self.notify.warning(f"processLogin failed for {sender}: no real token")
            self.killConnection(sender, 122)
            return

        if not response.get("website_user_id"):
            self.notify.warning(f"processLogin failed for {sender}: no website_user_id")
            self.killConnection(sender, 122)
            return

        if response.get("isbanned"):
            self.air.writeServerEvent('client-hwid-rejected', sender)
            self.killConnection(sender, 101)

        digest_maker = hmac.new(self.key.encode('utf-8'), digestmod=hashlib.sha512)
        digest_maker.update(backupCookie.encode('utf-8'))

        if not digest_maker.hexdigest() == authKey:
            self.air.writeServerEvent('bad-digest', sender, ip, response.get("realtoken"))
            self.notify.info(f"Sender {sender} ({ip}) sent CSM packet without correct challenge, booting.")
            self.killConnection(sender, 121)
            return

        if sender >> 32:
            self.killConnection(sender, 102)
            return

        if sender in self.connection2fsm:
            self.killConnectionFSM(sender)
            return

        if ServerEnvAI.WANT_IP_CHECKER:
            self.notify.info(f"Checking IP with IP Checker: {ip}")
            _ip_checker_response = requests.get(
                f'{ip_check_endpoint}/check-ip/{ip}',
                headers={
                    "Authorization": f"Bearer {ServerEnvAI.IP_CHECKER_API_KEY}"
                }
            )

            if not _ip_checker_response:
                self.notify.warning(f"IP Checker seems to have died. Ejecting client")
                self.killConnection(sender, 123)
                return

            if _ip_checker_response.status_code != 200:
                self.notify.warning(f"IP Checker returned status code {_ip_checker_response.status_code}, which is not success. Ejecting client")
                self.killConnection(sender, 123)
                return

            ip_checker_response = _ip_checker_response.json()
            if not ip_checker_response.get('success', True):
                self.notify.warning(f"IP Checker returned success = False (message: {ip_checker_response.get('message', '')}). Ejecting client")
                self.killConnection(sender, 123)
                return

            ip_checker_blocked = ip_checker_response.get('blocked')

            if ip_checker_blocked:
                self.notify.warning(f"IP {ip} is blocked by IP Checker. Ejecting client")
                self.killConnection(sender, 121)
                self.air.writeServerEvent('client-ip-rejected', sender)
                return

            self.notify.info(f"IP {ip} not blocked by IP Checker, continuing.")
        else:
            self.notify.info(f"WANT_IP_CHECKER: {ServerEnvAI.WANT_IP_CHECKER}, skipping.")

        self.connection2fsm[sender] = LoginAccountFSM(self, sender)
        self.connection2fsm[sender].request('Start', int(response.get("website_user_id")),
                                            response.get("realtoken"), ip, response.get("permissions"),
                                            response.get("muted"), response.get("want_speedchat_plus"), response.get('name_submission_locked'))

    def requestAvatars(self):
        avId = self.air.getMsgSender()
        if self.rateLimited(avId):
            return
        self.notify.debug('Received avatar list request from %d' % avId)
        self.runAccountFSM(GetAvatarsFSM)

    def createAvatar(self, dna, index, tracks, pg, skipTutorial):
        self.runAccountFSM(CreateAvatarFSM, dna, index, tracks, pg, skipTutorial)

    def deleteAvatar(self, avId):
        if self.rateLimited(avId):
            return
        self.runAccountFSM(DeleteAvatarFSM, avId)

    def setNameTyped(self, avId, name):
        if self.rateLimited(avId):
            return
        self.runAccountFSM(SetNameTypedFSM, avId, name)

    def setNamePattern(self, avId, p1, f1, p2, f2, p3, f3, p4, f4):
        self.runAccountFSM(SetNamePatternFSM, avId, [(p1, f1), (p2, f2), (p3, f3), (p4, f4)])

    def acknowledgeAvatarName(self, avId):
        if self.rateLimited(avId):
            return
        self.runAccountFSM(AcknowledgeNameFSM, avId)

    def chooseAvatar(self, avId: int, preferDistrictMode: int):
        if self.rateLimited(avId):
            return

        currentAvId = self.air.getAvatarIdFromSender()
        accountId = self.air.getAccountIdFromSender()
        try:
            preferDistrictMode = PreferDistrictMode(preferDistrictMode)
        except ValueError:
            self.killAccount(accountId, 107)
            return

        if currentAvId and avId:
            self.killAccount(accountId, 107)
            return
        elif not currentAvId and not avId:
            # This isn't really an error, the client is probably just making sure
            # none of its Toons are active.
            return

        if avId:
            self.runAccountFSM(LoadAvatarFSM, avId, preferDistrictMode)
        else:
            self.runAccountFSM(UnloadAvatarFSM, currentAvId)

    def rateLimited(self, avId) -> bool:
        if avId not in self.rateLimiters:
            self.rateLimiters[avId]: RateLimiter = RateLimiter(max_hits=3, period=1)
        rateLimiter: RateLimiter = self.rateLimiters.get(avId)
        return rateLimiter.tryRequest()

    # load balancer functions

    def __handleRequestCSMID(self):
        print(f"DEBUG: __handleRequestCSMID called, sending csmId={self.__csmId}")
        self.air.netMessenger.send('csmRespondId', [
            self.air.ourChannel, self.__csmId
        ])

    def _updateSpawningDistrict(self, shardId: int):
        self.notify.debug(f"Received new spawning shard: {shardId}")
        self._spawningDistrict = shardId

    def _handleRequestSpawningDistrict(self):
        self.air.netMessenger.send(NET_MESSENGER_REQUEST_SPAWNING_SHARD, [])

    @property
    def spawningDistrict(self) -> int:
        return self._spawningDistrict
