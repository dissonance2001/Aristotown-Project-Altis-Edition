from otp.ai.MagicWordGlobal import *
from toontown.battle import SuitBattleGlobals
from toontown.shtiker import CogPageGlobals
from toontown.suit import SuitDNA
from toontown.suit.SuitInvasionGlobals import IFV2, IFSkelecog, IFWaiter, INVASION_TYPE_MEGA, INVASION_TYPE_NORMAL
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer


def _resolveSuitName(value):
    value = value.lower()
    if value in SuitBattleGlobals.SuitAttributes:
        return value
    for suitName, attributes in list(SuitBattleGlobals.SuitAttributes.items()):
        if attributes.get('name', '').lower() == value:
            return suitName
    return None


def _resolveDept(value):
    value = value.lower()
    aliases = {
        'bossbot': 'c', 'boss': 'c', 'c': 'c',
        'lawbot': 'l', 'law': 'l', 'l': 'l',
        'cashbot': 'm', 'cash': 'm', 'm': 'm',
        'sellbot': 's', 'sell': 's', 's': 's',
        'boardbot': 'g', 'board': 'g', 'g': 'g',
        'techbot': 't', 'tech': 't', 't': 't',
        'pressbot': 'p', 'press': 'p', 'p': 'p',
    }
    return aliases.get(value)


@magicWord(name='invasion', category=CATEGORY_PROGRAMMER, types=[str, int, int, int, int])
def clashInvasion(suitName, mega=0, v2=0, skelecog=0, waiter=0):
    """Starts an invasion by Cog name or Cog code."""
    suitName = _resolveSuitName(suitName)
    if suitName is None:
        return 'Unknown Cog.'
    enabledFlags = [flag for flag in (v2, skelecog, waiter) if flag]
    if len(enabledFlags) > 1:
        return 'Altis invasions support only one of v2, skelecog, or waiter.'
    flags = IFV2 if v2 else IFSkelecog if skelecog else IFWaiter if waiter else 0
    invasionType = INVASION_TYPE_MEGA if mega else INVASION_TYPE_NORMAL
    if simbase.air.suitInvasionManager.startInvasionByName(suitName, flags, invasionType):
        return 'Started a %s invasion.' % SuitBattleGlobals.SuitAttributes[suitName]['name']
    return 'Could not start the invasion.'


@magicWord(name='deptinvasion', category=CATEGORY_PROGRAMMER, types=[str, int])
def clashDeptInvasion(deptName, mega=0):
    """Starts a department-wide Cog invasion."""
    dept = _resolveDept(deptName)
    if dept not in SuitDNA.suitDepts:
        return 'Unknown Cog department.'
    deptIndex = SuitDNA.suitDepts.index(dept)
    invasionType = INVASION_TYPE_MEGA if mega else INVASION_TYPE_NORMAL
    if simbase.air.suitInvasionManager.startInvasion(deptIndex, None, 0, invasionType):
        return 'Started a %s department invasion.' % SuitDNA.suitDeptFullnames[dept]
    return 'Could not start the department invasion.'


@magicWord(name='endinvasion', category=CATEGORY_PROGRAMMER, types=[])
def clashEndInvasion():
    """Ends the current Cog invasion."""
    if simbase.air.suitInvasionManager.stopInvasion():
        return 'Ended the current invasion.'
    return 'There is no active invasion.'


@magicWord(name='building', category=CATEGORY_MODERATOR, types=[str])
def clashBuilding(suitName):
    """Spawns a Cog building nearby using a Cog name or code."""
    suitName = _resolveSuitName(suitName)
    if suitName is None or suitName not in SuitDNA.suitHeadTypes:
        return 'That Cog cannot take over a building.'
    result = spellbook.getTarget().doBuildingTakeover(SuitDNA.suitHeadTypes.index(suitName))
    if result and result[0] == 'success':
        return 'Spawned a %s building.' % SuitBattleGlobals.SuitAttributes[suitName]['name']
    return 'Could not spawn a Cog building here.'


@magicWord(name='cleardisguise', category=CATEGORY_PROGRAMMER, types=[str])
def clashClearDisguise(deptName):
    """Clears the target Toon's disguise for one Cog department."""
    dept = _resolveDept(deptName)
    if dept not in SuitDNA.suitDepts:
        return 'Unknown Cog department.'
    index = SuitDNA.suitDepts.index(dept)
    target = spellbook.getTarget()
    for attribute, setter, value in (
            ('cogParts', target.b_setCogParts, 0),
            ('cogTypes', target.b_setCogTypes, 0),
            ('cogLevels', target.b_setCogLevels, 0),
            ('cogReviveLevels', target.b_setCogReviveLevels, 0),
            ('cogMerits', target.b_setCogMerits, 0)):
        values = list(getattr(target, attribute))
        if index < len(values):
            values[index] = value
            setter(values)
    return 'Cleared the %s disguise.' % SuitDNA.suitDeptFullnames[dept]


@magicWord(name='instakill', category=CATEGORY_PROGRAMMER, types=[int])
def clashInstakill(damage):
    """Sets fixed damage for the target Toon's damaging gags. Use 0 to disable."""
    damage = int(damage)
    if damage < 0 or damage > 60000:
        return 'Damage must be between 0 and 60,000.'
    target = spellbook.getTarget()
    target.instakillDamage = damage
    if damage == 0:
        return 'Disabled fixed gag damage.'
    return 'Set fixed gag damage to %s.' % format(damage, ',')


@magicWord(name='instakillreset', category=CATEGORY_PROGRAMMER, types=[])
def clashInstakillReset():
    """Restores normal gag damage for the target Toon."""
    target = spellbook.getTarget()
    target.instakillDamage = 0
    return 'Restored normal gag damage.'


@magicWord(name='dance', category=CATEGORY_PROGRAMMER, types=[])
def clashDance():
    """Makes every Toon in your current zone dance."""
    invoker = spellbook.getInvoker()
    count = 0
    for toon in list(simbase.air.doId2do.values()):
        if toon.__class__.__name__ != 'DistributedToonAI':
            continue
        if toon.zoneId != invoker.zoneId:
            continue
        toon.b_setAnimState('Victory', 1)
        count += 1
    return 'Made %d Toon%s dance.' % (count, '' if count == 1 else 's')


@magicWord(name='suspicious', category=CATEGORY_PROGRAMMER, types=[])
def clashSuspicious():
    """Writes a test suspicious event to the server log."""
    invoker = spellbook.getInvoker()
    simbase.air.writeServerEvent('suspicious', invoker.doId, 'Triggered with /suspicious')
    return 'Triggered a suspicious server event.'


@magicWord(name='fillgallery', category=CATEGORY_PROGRAMMER, types=[])
def clashFillGallery():
    """Fills the target Toon's Cog gallery and radar."""
    target = spellbook.getTarget()
    deptCount = len(SuitDNA.suitDepts)
    target.b_setCogCount(list(CogPageGlobals.COG_QUOTAS[1]) * deptCount)
    status = [CogPageGlobals.COG_COMPLETE2] * SuitDNA.suitsPerDept
    target.b_setCogStatus(status * deptCount)
    target.b_setCogRadar([1] * len(target.getCogRadar()))
    target.b_setBuildingRadar([1] * len(target.getBuildingRadar()))
    return 'Filled the Cog gallery.'


@magicWord(name='cleargallery', category=CATEGORY_PROGRAMMER, types=[])
def clashClearGallery():
    """Clears the target Toon's Cog gallery and radar."""
    target = spellbook.getTarget()
    deptCount = len(SuitDNA.suitDepts)
    target.b_setCogCount([0] * (SuitDNA.suitsPerDept * deptCount))
    target.b_setCogStatus([0] * (SuitDNA.suitsPerDept * deptCount))
    target.b_setCogRadar([0] * len(target.getCogRadar()))
    target.b_setBuildingRadar([0] * len(target.getBuildingRadar()))
    return 'Cleared the Cog gallery.'


def _runWord(name, arguments):
    return spellbook.doWord(name, arguments)


@magicWord(name='head', category=CATEGORY_CREATIVE, types=[str])
def clashHead(value):
    """Changes the target Toon's species or head code."""
    return _runWord('dna', 'head %s' % value)


@magicWord(name='headsize', category=CATEGORY_CREATIVE, types=[int])
def clashHeadSize(value):
    """Changes the target Toon's head-size index."""
    return _runWord('dna', 'headsize %d' % value)


@magicWord(name='headcolor', category=CATEGORY_CREATIVE, types=[int, int, int])
def clashHeadColor(r, g, b):
    """Changes the target Toon's head color using RGB values."""
    return _runWord('color', 'head %d %d %d' % (r, g, b))


@magicWord(name='torso', category=CATEGORY_CREATIVE, types=[int])
def clashTorso(value):
    """Changes the target Toon's torso index."""
    return _runWord('dna', 'torso %d' % value)


@magicWord(name='armcolor', category=CATEGORY_CREATIVE, types=[int, int, int])
def clashArmColor(r, g, b):
    """Changes the target Toon's arm color using RGB values."""
    return _runWord('color', 'arms %d %d %d' % (r, g, b))


@magicWord(name='legs', category=CATEGORY_CREATIVE, types=[int])
def clashLegs(value):
    """Changes the target Toon's leg-size index."""
    return _runWord('dna', 'legs %d' % value)


@magicWord(name='legcolor', category=CATEGORY_CREATIVE, types=[int, int, int])
def clashLegColor(r, g, b):
    """Changes the target Toon's leg color using RGB values."""
    return _runWord('color', 'legs %d %d %d' % (r, g, b))

def _getPresentThiefHood():
    return simbase.air.hoodId2Hood.get(ToontownGlobals.Toonseltown)


@magicWord(name='presentthiefstart', category=CATEGORY_PROGRAMMER, types=[])
def clashPresentThiefStart():
    """Starts the Present Thief minigame in Toonseltown after the 10-second warning."""
    hood = _getPresentThiefHood()
    if not hood:
        return 'Toonseltown is not loaded.'
    started, message = hood.beginPresentThief()
    return message


@magicWord(name='presentthiefend', category=CATEGORY_PROGRAMMER, types=[])
def clashPresentThiefEnd():
    """Immediately ends the active Present Thief minigame and cleans it up."""
    hood = _getPresentThiefHood()
    if not hood:
        return 'Toonseltown is not loaded.'
    ended, message = hood.endPresentThief()
    hood.scheduleNextMinigame()
    return message



@magicWord(name='setrod', category=CATEGORY_PROGRAMMER, types=[int])
def clashSetRod(rodId):
    """Sets the target's fishing rod (0=Twig, 1=Bamboo, 2=Hardwood, 3=Steel, 4=Gold). Temporary testing aid until the Tell-Tale Carp rod clerk is placed."""
    if rodId < 0 or rodId > 4:
        return 'Rod id must be 0-4 (0=Twig, 1=Bamboo, 2=Hardwood, 3=Steel, 4=Gold).'
    target = spellbook.getTarget()
    target.b_setFishingRod(rodId)
    return 'Set rod to %s.' % TTLocalizer.FishingRodNameDict.get(rodId, rodId)
