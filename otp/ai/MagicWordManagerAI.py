from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from otp.ai.MagicWordGlobal import *
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.MsgTypes import *
from toontown.toon.DistributedToonAI import DistributedToonAI
from toontown.toon import ClashAIMagicWords
import time
import datetime
import os

class MagicWordManagerAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("MagicWordManagerAI")

    def sendMagicWord(self, word, targetId):
        invokerId = self.air.getAvatarIdFromSender()
        invoker = self.air.doId2do.get(invokerId)

        if not isinstance(self.air.doId2do.get(targetId), DistributedToonAI):
            self.sendUpdateToAvatarId(invokerId, 'sendMagicWordResponse', ['Target is not a toon object!'])
            return

        if not invoker:
            self.sendUpdateToAvatarId(invokerId, 'sendMagicWordResponse', ['missing invoker'])
            return
        now = time.strftime("%c")
        if invoker.getAdminAccess() < MINIMUM_MAGICWORD_ACCESS:
            self.air.writeServerEvent('suspicious', invokerId, 'Attempted to issue magic word: %s' % word)
            dg = PyDatagram()
            dg.addServerHeader(self.GetPuppetConnectionChannel(invokerId), self.air.ourChannel, CLIENTAGENT_EJECT)
            dg.addUint16(126)
            dg.addString('Magic Words are reserved for administrators only!')
            self.air.send(dg)
            return

        target = self.air.doId2do.get(targetId)
        if not target:
            self.sendUpdateToAvatarId(invokerId, 'sendMagicWordResponse', ['missing target'])
            return

        response = spellbook.process(invoker, target, word)
        if response:
            self.sendUpdateToAvatarId(invokerId, 'sendMagicWordResponse', [response])

        self.air.writeServerEvent('magic-word',
                                  invokerId, invoker.getAdminAccess(),
                                  targetId, target.getAdminAccess(),
                                  word, response)

        if not os.path.exists('user/logs/mw'):
            os.makedirs('user/logs/mw')

        print(("%s | %s : %s\n" % (now, invokerId, word)))

        if os.getenv('DISTRICT_NAME', 'Test Canvas') == "Test Canvas":
            return
        baseword = word
        if ' ' in word:
            baseword = word.split()[0]


@magicWord(category=CATEGORY_COMMUNITY_MANAGER, types=[str])
def help(wordName=None):
    print('help called with %s' % (wordName))
    if not wordName:
        return "What were you interested getting help for?"
    word = spellbook.words.get(wordName.lower())   # look it up by its lower case value
    if not word:
        accessLevel = spellbook.getInvoker().getAdminAccess()
        wname = wordName.lower()
        for key in spellbook.words:
            if spellbook.words.get(key).access <= accessLevel:
                if wname in key:
                    return 'Did you mean %s' % (spellbook.words.get(key).name)
        return 'I have no clue what %s is refering to' % (wordName)
    return word.doc

@magicWord(category=CATEGORY_COMMUNITY_MANAGER, types=[])
def words():
    accessLevel = spellbook.getInvoker().getAdminAccess()
    wordString = None
    for key in spellbook.words:
       word = spellbook.words.get(key)
       if word.access <= accessLevel:
           if wordString is None:
               wordString = key
           else:
               wordString += ", ";
               wordString += key;
    if wordString is None:
        return "You are chopped liver"
    else:
        return wordString


@magicWord(category=CATEGORY_PROGRAMMER, types=[])
def mp():
    toon = spellbook.getTarget()
    teleportTargetId = toon.getDoId()

    if teleportTargetId not in toon.magicWordTeleportRequests:
        toon.magicWordTeleportRequests.append(teleportTargetId)

    toon.magicTeleportInitiate(teleportTargetId, 4000, 4874)
    return 'Teleporting to the Major Player Lobby.'


@magicWord(category=CATEGORY_PROGRAMMER, types=[])
def pace():
    toon = spellbook.getTarget()
    teleportTargetId = toon.getDoId()

    if teleportTargetId not in toon.magicWordTeleportRequests:
        toon.magicWordTeleportRequests.append(teleportTargetId)

    toon.magicTeleportInitiate(teleportTargetId, 9000, 9613)
    return 'Teleporting to the Pacesetter Lobby.'

@magicWord(category=CATEGORY_PROGRAMMER, types=[])
def cs():
    toon = spellbook.getTarget()
    teleportTargetId = toon.getDoId()

    if teleportTargetId not in toon.magicWordTeleportRequests:
        toon.magicWordTeleportRequests.append(teleportTargetId)

    toon.magicTeleportInitiate(teleportTargetId, 6000, 6837)
    return 'Teleporting to the Chainsaw Consultant Lobby.'

def _getClubManagerAI():
    manager = getattr(simbase.air, 'clubMgr', None)
    if manager is not None:
        return manager

    # Fallback for repositories that generated the global object without
    # assigning it to air.clubMgr.
    for obj in list(simbase.air.doId2do.values()):
        if obj.__class__.__name__ == 'DistributedToonClubAI':
            return obj
    return None


@magicWord(category=CATEGORY_PROGRAMMER, types=[int])
def jbs(amount):
    """Give the targeted Toon Jellybeans, overflowing into the bank."""
    toon = spellbook.getTarget()
    amount = int(amount)
    if amount <= 0:
        return 'Amount must be greater than zero.'

    before = int(toon.getTotalMoney())
    toon.addMoney(amount)
    after = int(toon.getTotalMoney())
    awarded = max(0, after - before)

    if awarded <= 0:
        return 'That Toon cannot hold any more Jellybeans.'
    if awarded < amount:
        return 'Gave %s Jellybeans; the Toon bank is now full.' % (
            format(awarded, ','))
    return 'Gave %s Jellybeans.' % format(awarded, ',')


@magicWord(category=CATEGORY_PROGRAMMER, types=[int])
def coin(amount):
    """Give Club Coins to the targeted Toon's Club without adding Club XP."""
    toon = spellbook.getTarget()
    amount = int(amount)
    if amount <= 0:
        return 'Amount must be greater than zero.'
    if amount > 0xFFFFFFFF:
        return 'That Club Coin amount is too large.'

    manager = _getClubManagerAI()
    if manager is None:
        return 'The Club manager is not available.'
    if not manager.magicWordAddClubCoins(toon.doId, amount):
        return 'Could not give Club Coins.'

    return "Gave the targeted Toon's Club %s Club Coins." % (
        format(amount, ','))


@magicWord(category=CATEGORY_PROGRAMMER, types=[int])
def clublevel(level):
    """Set the targeted Toon's Club to the beginning of an exact level."""
    toon = spellbook.getTarget()
    level = int(level)
    if level < 1:
        return 'Club level must be at least 1.'
    if level > 10000:
        return 'Club level cannot be higher than 10,000.'

    manager = _getClubManagerAI()
    if manager is None:
        return 'The Club manager is not available.'
    if not manager.magicWordSetClubLevel(toon.doId, level):
        return 'Could not set the Club level.'

    return "Set the targeted Toon's Club to level %s." % format(level, ',')

