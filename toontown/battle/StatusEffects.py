'''
Use this file to hold all status effect data.
'''
from toontown.toonbase.ToonPythonUtil import getBase
from toontown.toonbase.ToontownBattleGlobals import HEAL_TRACK, TRAP_TRACK, LURE_TRACK, THROW_TRACK, SQUIRT_TRACK, ZAP_TRACK, SOUND_TRACK, DROP_TRACK, AvPropsNew, AvPropStrings

import builtins
from typing import Literal, Union, Optional

DEFAULT_STATUS_ICON_PATH: Literal['phase_3.5/models/gui/battlegui/status_effects.bam'] = 'phase_3.5/models/gui/battlegui/status_effects.bam'
TRACK_2_CONSTANT: dict[int, str] = {HEAL_TRACK: 'Toon-up',
 TRAP_TRACK: 'Trap',
 LURE_TRACK: 'Lure',
 THROW_TRACK: 'Throw',
 SQUIRT_TRACK: 'Squirt',
 ZAP_TRACK: 'Zap',
 SOUND_TRACK: 'Sound',
 DROP_TRACK: 'Drop'}

base = getBase()

def isTrack(variable) -> bool:
    '''
    Verify that we have a track constant.
    '''
    return variable is HEAL_TRACK or variable is TRAP_TRACK or variable is LURE_TRACK or variable is THROW_TRACK or variable is SQUIRT_TRACK or variable is ZAP_TRACK or variable is SOUND_TRACK or variable is DROP_TRACK

def getIcon(node: str, fromPath: str = DEFAULT_STATUS_ICON_PATH):
    return builtins.loader.loadModel(fromPath).find(f'**/{node}')

# def getIcon(node: str, fromPath: str = DEFAULT_STATUS_ICON_PATH):
#     pass

def makePercent(number):
    '''
    Depending on the instance, we may want to list percentages rather than multipliers, though it is purely for display.
    
    :param number: The number, preferably one with a decimal.
    '''
    if True:
        return (1.0 - number) * 100.0
    else:
        return (number - 1.0) * 100.0

class StatusEffect:
    '''
    All status effects shall inherit this class, with basic functionalities.

    Attributes:
        roundsLeft (int): An int that determines how many rounds of the status effect remain.  -1 for it to be permanent unless cleared.
        good (bool):
        name (str): The name of the status effect.  Really, it's the header and can have some status things in it if desired, like Scapegoat's rage or Chainsaw Consultant's RPM.
        desc (str): The description of the status effect that describes what it does.
        hidden (bool): Whether or not this status effect is hidden (e.g. the 340% damage vulnerability Count Erfit gets from maxing out his arms).
    '''
    roundsLeft: int
    good: bool = True
    name: str = 'Status Effect'
    desc: str = 'No description available.'
    hidden: bool = False

    def __init__(self, roundsLeft: int, name: str = 'Status Effect', desc: str = 'No description available.', icon: Optional[str] = None, iconPath: str = DEFAULT_STATUS_ICON_PATH, hidden = False) -> None:
        '''
        Parameters:
            roundsLeft (int): An int that determines how many rounds of the status effect remain.  -1 for it to be permanent unless cleared.
            name (str): The name of the status effect.  Really, it's the header and can have some status things in it if desired, like Scapegoat's rage or Chainsaw Consultant's RPM.
            desc (str): The description of the status effect that describes what it does.
            icon (str|LiteralString|None): The icon node of the status effect based on the given path.
            iconPath (str): For when we might want a different collection of model nodes for the icon (e.g. the Glass of Water for the Hydrated status effect).
            hidden (bool): Whether or not this status effect is hidden (e.g. the 340% damage vulnerability Count Erfit gets from maxing out his arms).
        '''
        self.roundsLeft = roundsLeft
        self.name = name
        self.desc = desc
        # Professor Control: I don't know if this will work or if I am missing something.
        if icon:
            self.icon = getIcon(icon, fromPath=iconPath)
        self.hidden = hidden

    
    def setRoundsLeft(self, roundsLeft: int) -> None:
        '''
        There are likely some cases where we would like to change the rounds around, so this method will be convenient.
        '''
        self.roundsLeft = roundsLeft

    
    def updateEffect(self) -> None:
        '''
        Other classes will inherit this, but it will be overridden.
        We may want to change a few attributes as the turns pass, or they may get changed outside of these classes.  Keep them up to date with this method.
        '''
        pass


    def subtractRound(self) -> None:
        '''
        Call this every round for all status effects to subtract the rounds and to update the effect if necessary.
        '''
        self.roundsLeft -= 1
        self.updateEffect()


# region General
class DamageModifier(StatusEffect):
    '''
    Change the outgoing damage of whoever has this status effect.

    Attributes:
        damageMod (int|float): The damage modifier.
    '''
    damageMod: Union[int, float]

    def __init__(self, roundsLeft: int, damageMod: Union[int, float], hidden: bool = False) -> None:
        '''
        :param int|float damageMod: The damage modifier.  It can either be an int which will offer a flat damage change, or a float which will be a multiplier.
        '''
        StatusEffect.__init__(self, roundsLeft, hidden=hidden)
        self.damageMod = damageMod
        self.updateEffect()


    def updateEffect(self) -> None:
        if isinstance(self.damageMod, float):
            self.good = self.damageMod >= 1.0
            self.desc = "This combatant's attacks are {}x as powerful.".format(self.damageMod)
        else:
            self.good = self.damageMod >= 0
            self.desc = 'This combatant is dealing {} {} damage.'.format(self.damageMod, 'more' if self.good else 'less')
        self.name = 'Damage {}'.format('Up' if self.good else 'Down')
        self.icon = getIcon('toon_damage_{}_icon'.format('up' if self.good else 'down')) # I do not yet know how I would distinguish between a Cog and a Toon, but I think that is some BattleCalculatorAI.py stuff that can be resolved later.


class DefenseModifier(StatusEffect):
    '''
    Change the incoming damage of whoever has this status effect.

    Attributes:
        defenseMod (int|float): The defense modifier.
    '''
    defenseMod: Union[int, float]

    def __init__(self, roundsLeft: int, defenseMod: Union[int, float], hidden: bool = False) -> None:
        '''
        :param int|float defenseMod: The defense modifier.  It can either be an int which will offer a flat damage change, or a float which will be a multiplier.  NOTE: For int, negative means the combatant will take less damage, while positive will make them take more damage.  For float, of course, incoming damage is multiplied.
        '''
        StatusEffect.__init__(self, roundsLeft, hidden=hidden)
        self.defenseMod = defenseMod
        self.updateEffect()


    def updateEffect(self) -> None:
        if isinstance(self.defenseMod, float):
            self.good = self.defenseMod <= 1.0
            self.desc = 'This combatant is taking {}x as much damage.'.format(self.defenseMod)
        else:
            self.good = self.defenseMod <= 0
            self.desc = 'This combatant is taking {} {} damage.'.format(abs(self.defenseMod), 'less' if self.good else 'more')
        self.name = 'Damage Reduction' if self.good else 'Vulnerable'
        self.icon = getIcon('{}shield_icon'.format('' if self.good else 'broken_'))


class DamageOverTime(StatusEffect):
    '''
    Damage or heal over a number of turns.

    Attributes:
        hpPerRound (int): How much HP per round the avatar gains (negative) or loses (positive).
    '''
    hpPerRound: int

    def __init__(self, roundsLeft: int, hpPerRound: int, attack: str, hidden: bool = False) -> None:
        '''
        hpPerRound: As one would expect, this is an int determines the amount of damage taken per round.  Despite being a damage over time, we should use a negative integer to denote healing over time.
        attack: The attack that plays for the damage over time. It should not be a method where a Cog is needed for it to function.
        '''
        StatusEffect.__init__(self, roundsLeft, hidden=hidden)
        self.updateEffect()


    def updateEffect(self) -> None:
        self.good = self.hpPerRound < 0
        self.name = 'Heal Over Time' if self.good else 'Damage Over Time'
        self.desc = 'This combatant is {} {} HP per round.'.format('gaining' if self.good else 'losing', abs(self.hpPerRound))
        self.icon = getIcon('{}_over_time_icon'.format('heal' if self.good else 'damage'))


class AccuracyModifier(StatusEffect):
    '''
    Alter the accuracy of an attack.

    Attributes:
        accuracyMod (int): The modifier for attack accuracy.
    '''
    accuracyMod: int

    def __init__(self, roundsLeft: int, accuracyMod: int, hidden: bool = False):
        '''
        accuracyMod: The amount of accuracy to increase or decrease.
        '''
        StatusEffect.__init__(self, roundsLeft, hidden=hidden)
        self.accuracyMod = accuracyMod
        self.updateEffect()
    
    def updateEffect(self):
        '''
        Should the accuracy ever change, be sure that the icons are up to date.
        '''
        self.good = self.accuracyMod >= 0
        self.name = 'Accuracy {}'.format('Up' if self.good else 'Down')
        self.desc = "This combatant's attacks are {}\u0025 {} accurate.".format(str(abs(self.accuracyMod)), 'more' if self.good else 'less')
        self.icon = getIcon('toon_accuracy_{}_icon'.format('up' if self.good else 'down'))


class DamageAbsorption(StatusEffect):
    '''
    Take some damage on behalf of other Cogs.

    Attributes:
        intercepting (int|float): How much HP will be intercepted.  If an int, a flat number of damage, but if a float, then a multiplier (e.g. if it is set to 0.25, another Cog will take 0.75 of the damage while this Cog takes the rest).
        damageAmp (int|float): How much additional damage will be taken as a result of absorbing, either a float or an int.  If an int, flat damage change.  If float, it's a multiplier.
    '''
    intercepting: Union[int, float]
    damageAmp: Union[int, float]

    def __init__(self, roundsLeft: int, intercepting: Union[int, float], damageAmp: Union[int, float] = 1.0, hidden: bool = False) -> None:
        '''
        :param int|float intercepting: How much HP will be intercepted.  If an int, a flat number of damage, but if a float, then a multiplier (e.g. if it is set to 0.25, another Cog will take 0.75 of the damage while this Cog takes the rest).
        :param damageAmp: How much additional damage will be taken as a result of absorbing, either a float or an int.  If an int, flat damage change.  If float, it's a multiplier.
        '''
        StatusEffect.__init__(self, roundsLeft, name='Damage Absorption', icon='damage_absorb_icon', hidden=hidden)
        self.damageAmp = damageAmp
        self.intercepting = intercepting
        self.good = True


    def updateEffect(self) -> None:
        self.desc = 'This Cog will endure '
        if isinstance(self.intercepting, float):
            self.desc += '{}x the damage the other Cogs take'.format(self.intercepting)
        else:
            self.desc += 'up to {} damage for each Cog'.format(self.intercepting)
        if isinstance(self.damageAmp, float):
            self.desc = ' and take {}x as much damage from absorbing'.format(self.damageAmp)
        elif self.damageAmp > 0:
            self.desc += ' and take {} more damage from absorptions'.format(self.damageAmp)
        elif self.damageAmp < 0:
            self.desc += ', but will take {} less damage from absorptions'.format(self.damageAmp)
        self.desc += '.'


class Siphon(DamageModifier):
    '''
    Regain HP after landing a hit.  Inheriting the DamageModifier class since the Major Player's siphon offers an attack deficit.  It might also be possible to use this as a recoil, but that can be done later.

    Attributes:
        stealHp (int|float): Either an int or a float.  If int, give that amount of HP if the attack lands.  If a float, then make it a multiplier based on how much health was taken.
    '''
    stealHp: Union[int, float]

    def __init__(self, roundsLeft: int, damageMod: Union[int, float], stealHp: Union[int, float], hidden: bool = False) -> None:
        '''
        stealHp: Either an int or a float.  If int, give that amount of HP if the attack lands.  If a float, then make it a multiplier based on how much health was taken.
        '''
        DamageModifier.__init__(self, roundsLeft, damageMod, hidden=hidden)
        self.stealHp = stealHp
        self.name = 'Siphon'
        self.icon = getIcon('ink_drain_icon')
        self.good = True
        self.updateEffect()

    
    def updateEffect(self):
        self.desc = 'This Cog is ready to siphon your Laff! It '
        if isinstance(self.damageMod, float) and self.damageMod != 1.0:
            self.desc += 'does {}x damage{} '.format(self.damageMod, ', but ' if self.damageMod < 0.0 else ' and ')
        elif isinstance(self.damageMod, int) and self.damageMod != 0:
            self.desc += 'does {} {} damage{} '.format(abs(self.damageMod), 'less' if self.damageMod < 0 else 'more', ', but ' if self.damageMod < 0 else ' and ')
        self.desc += 'will heal '
        if isinstance(self.stealHp, float):
            self.desc += 'for {}x the damage it deals!'.format(self.stealHp)
        else:
            self.desc += '{} HP for each Toon it successfully hits!'.format(self.stealHp)

# endregion

# region Toons' status effects
class DisableSOS:
    pass


class DisableUnites:
    pass


class DisableSues:
    pass


class DisableFires:
    pass


class UniteCooldown(DisableUnites):
    '''
    Forbid the use of unites.
    '''

    def __init__(self, roundsLeft: int) -> None:
        StatusEffect.__init__(self, roundsLeft, name='Unite Cooldown', desc='Your Unites are currently on cooldown.', icon='unite_cooldown_icon')
        self.good = False


class RewardCooldown(DisableSOS, DisableUnites, DisableSues, DisableFires):
    '''
    Forbid the use of rewards.
    '''

    def __init__(self, roundsLeft: int) -> None:
        StatusEffect.__init__(self, roundsLeft, name='Reward Cooldown', desc='Your Boss Rewards are currently on cooldown.', icon='reward_cooldown_icon')
        self.good = False


class Cheer(AccuracyModifier):
    '''
    Glorified accuracy boost.
    '''

    def __init__(self, roundsLeft: Literal[1, 2] = 1) -> None:
        '''
        roundsLeft: Make this variate because of the prestige.
        '''
        AccuracyModifier.__init__(self, roundsLeft, 10)
        self.name = 'Cheer'
        self.icon = getIcon('cheer_icon')
        self.updateEffect()


    def updateEffect(self) -> None:
        self.good = self.accuracyMod >= 0
        self.desc = "This Toon's attack accuracy is increased by {}\u0025.".format(self.accuracyMod)


class Trapped(StatusEffect):
    '''
    A Trap gets laid in front of a Cog; when a Cog is Lured, the Trap is set off, dealing damage.
    '''

    def __init__(self, level: int, damage: int) -> None:
        '''
        Parameters:
            level: The level of the Trap which determines the icon via index (min 0, max 7).
            damage: How much damage will occur when the Trap is sprung.
        '''
        StatusEffect.__init__(self, -1, name='Trapped', icon=AvPropsNew[TRAP_TRACK][level], iconPath='phase_3.5/models/gui/inventory_icons')
        self.damage: int = damage
        self.desc = 'This Cog is TRAPPED by a {}! LURE Gags are 20\u0025 more accurate against this Cog. Once LURED, they will take {} damage.'.format(AvPropStrings[TRAP_TRACK][level], self.damage)
        self.good = False # Trapped is in a weird place for "good"...  On one hand, it technically is a bad status effect, but we don't want it to be removed forcefully, right?


class MarkedForLaugh(DefenseModifier):
    '''
    A damage vulnerability for when a Toon uses Throw against a Cog.
    '''

    def __init__(self) -> None:
        DefenseModifier.__init__(self, 1, 1.1)
        self.name = 'Marked for Laugh'
        self.icon = getIcon('marked_icon')
        self.good = False
        self.updateEffect()


    def updateEffect(self) -> None:
        self.desc = 'This Cog is more vulnerable, and will take {}\u0025 more damage.'.format((self.defenseMod - 1.0) * 100)

# endregion

# Cogs' status effects.
# General.
class ExtraAttacks(StatusEffect):
    '''
    Allow the Cog to attack extra times.

    Attributes:
        extraAttacks (int): How many extra attacks the Cog gets.
    '''
    extraAttacks: int

    def __init__(self, extraAttacks: int, roundsLeft: int = -1, hidden: bool = False) -> None:
        '''
        :param int roundsLeft: I have no clue why this would be used, but I'm thinking of if a grunt Cog would use this for some reason?  I'll keep this parameter just in case we have ideas.
        '''
        StatusEffect.__init__(self, roundsLeft, name='Additional Attack', icon='extra_attacks_icon', hidden=hidden)
        self.extraAttacks = extraAttacks
        self.good = True
        self.updateEffect()
    
    def updateEffect(self) -> None:
        self.desc = 'This Cog has gained {} extra attack{}!'.format(self.extraAttacks, '' if abs(self.extraAttacks) == 1 else 's')

class LureResistance(StatusEffect):
    '''
    Limit the max turns a Cog can be Lured for.

    Attributes:
        maxLureRounds (int): The maximum number of rounds a Cog can be Lured for.
    '''
    maxLureRounds: int

    def __init__(self, maxLureRounds: int, roundsLeft: int = -1, hidden: bool = False) -> None:
        '''
        :param bool hidden: It's a Witch Hunter thing.
        '''
        StatusEffect.__init__(self, roundsLeft, name='Lure Resistance', icon=None)
        self.maxLureRounds = maxLureRounds
        self.hidden = hidden
        self.good = True
        self.updateEffect()


    def updateEffect(self) -> None:
        if self.maxLureRounds == 0:
            self.desc = 'This Cog is entirely immune to being LURED.'
        else:
            self.desc = 'This Cog will stay LURED for {} round{}.'.format(self.maxLureRounds, '' if abs(self.maxLureRounds) == 1 else 's')


class FireImmunity:
    '''
    Prevent the Cog from being fired.
    '''
    pass


class SueImmunity:
    '''
    Prevent the Cog from being sued.
    '''
    pass


class ManagerBeneficiary(StatusEffect, FireImmunity, SueImmunity):
    '''
    Grant the Cog Manager benefits (immunity to Pink Slips and Cease and Desists).
    '''

    def __init__(self, roundsLeft: int = -1, hidden: bool = False) -> None:
        StatusEffect.__init__(self, roundsLeft, name='Manager Beneficiary', desc='This Cog cannot be fired or sued.', icon='tie_icon', hidden=hidden)
        self.good = True


class Overcharged(DamageModifier, LureResistance, ManagerBeneficiary):
    '''
    All Cogs that have at least 1.5x their health will gain this status effect.
    '''

    def __init__(self):
        ManagerBeneficiary.__init__(self, -1)
        self.damageMod = 1.5
        self.maxLureRounds = 2
        self.name = 'Overcharged'
        self.desc = 'This Cog is Overcharged!\n\nWhile Overcharged, they have high Lure Resistance, deal 50\u0025 more damage, and receive the same benefits as Manager Cogs.'
        self.icon = getIcon('overcharge_icon')


class FocusedDefense(DefenseModifier):
    '''
    Unlike the standard defense modifier, this one will only work for the first Gag track per round.
    '''

    def __init__(self, roundsLeft: int, defenseMod: Union[int, float]) -> None:
        DefenseModifier.__init__(self, roundsLeft, defenseMod)
        self.icon = getIcon('focused_defense_icon')

    
    def updateEffect(self) -> None:
        pass


class SoakResistance(DefenseModifier):
    '''
    Only take reduced damage whenever the Cog gets soaked.
    '''
    pass


class BanGags(StatusEffect):
    '''
    Use this status effect to ban individual Gags.
    '''

    def __init__(self, roundsLeft, bannedGags, pickable = True) -> None:
        '''
        :param bannedGags: A list of tuples with two indices, the first being the track and the second being the level (e.g. bannedGags = [(SOUND_TRACK, 8), (DROP_TRACK, 6)]).  Gag levels are the actual (non-programatic) Gag levels, so keep this in mind.
        :param bool pickable: Whether or not the banned Gags are pickable, which can result in a punishment.  TODO: Figure out how to do it.
        '''
        from toontown.toonbase.TTLocalizer import BattleGlobalAvPropStrings # Get all of the Gag names.
        for bannedGag in bannedGags:
            if not isTrack(bannedGag[0]):
                raise ValueError('The Gag track is not any track constant (see toontown/battle/StatusEffects.py for more info)!')

        StatusEffect.__init__(self, roundsLeft, name='Gag Ban', icon='backfire_icon')
        self.bannedGags = bannedGags
        self.pickable = pickable
        self.good = False
        self.updateEffect()


    def updateEffect(self) -> None:
        pass


class GagBans(StatusEffect):
    '''
    Use this status effect to ban Gags based on level, track, or both.
    '''

    def __init__(self, roundsLeft, bannedLevels = ([], True), bannedTracks = ([], True)):
        '''
        :param bannedLevels: A tuple with two indices; the first is a list of the banned levels, while the second is whether or not they can be chosen.  TODO: Penalty.
        :param bannedTracks: A tuple with two indices; the first is a list of the banned tracks, while the second is whether or not they can be chosen.  TODO: Penalty.
        '''
        StatusEffect.__init__(self, roundsLeft, name='Gag Ban', desc='A status effect.', icon='backfire_icon')
        self.bannedLevels = bannedLevels
        self.bannedTracks = bannedTracks
        self.good = False

class BanGagLevels(StatusEffect):
    '''
    Ban Gag levels.  The Gags can either be selectable or nonselectable.  If selectable, incur a punishment on Toons.

    Attributes:
        bannedLevels: The levels that cannot be used.
        pickable (bool): Optionally make banned gags pickable, but this should be coupled with a penalty.
    '''
    pickable: bool

    def __init__(self, roundsLeft: int, bannedLevels, pickable: bool = True) -> None:
        '''
        :param bannedLevels: A list of Gag levels that will be forbidden to use.
        '''
        StatusEffect.__init__(self, roundsLeft, name='Gag Level Prohibition', icon='backfire_icon')
        self.bannedLevels = bannedLevels
        self.pickable = pickable
        self.good = False
        self.updateEffect()
    

    def updateEffect(self) -> None:
        if len(self.bannedLevels) == 1:
            listBannedGags = str(self.bannedLevels[0])
        elif len(self.bannedLevels) == 2:
            listBannedGags = '{} or {}'.format(self.bannedLevels[0], self.bannedLevels[1])
        else:
            listBannedGags = str(self.bannedLevels[0])
            for i in range(1, len(self.bannedLevels) - 1):
                listBannedGags += ', ' + str(self.bannedLevels[i])

            listBannedGags += ', or ' + str(self.bannedLevels[-1])
        if self.pickable:
            self.desc = 'This Toon will face a punishment if they use level {} Gags.'.format(listBannedGags)
        else:
            self.desc = "This Toon's level {} Gags have been disabled.".format(listBannedGags)


class BanGagTracks(StatusEffect):
    '''
    Ban Gag tracks.  The Gags can either be selectable or nonselectable.  If selectable, incur a punishment on Toons.
    Attributes:
        bannedTracks: The tracks that cannot be used.
        pickable (bool): Optionally make banned gags pickable, but this should be coupled with a penalty.
    '''
    pickable: bool

    def __init__(self, roundsLeft: int, bannedTracks, pickable: bool = True) -> None:
        '''
        :param bannedTracks: A list of Gag tracks that will be forbidden to use.  Use only the imports to keep track of the tracks.
        '''
        for bannedTrack in bannedTracks:
            if not isTrack(bannedTrack): # Check to make sure we are using the constant.
                raise ValueError('bannedTrack is not any track constant (see toontown/battle/StatusEffects.py for more info)!')

        StatusEffect.__init__(self, roundsLeft, name='Gag Track Prohibition', icon='backfire_icon')
        self.bannedTracks = bannedTracks
        self.pickable = pickable
        self.good = False
        self.updateEffect()


    def updateEffect(self) -> None:
        listBannedGags: str
        if len(self.bannedTracks) == 1:
            listBannedGags = TRACK_2_CONSTANT[self.bannedTracks[0]]
        elif len(self.bannedTracks) == 2:
            listBannedGags = TRACK_2_CONSTANT[self.bannedTracks[0]] + (' or ' if self.pickable else ' and ') + TRACK_2_CONSTANT[self.bannedTracks[1]]
        else:
            listBannedGags = TRACK_2_CONSTANT[self.bannedTracks[0]]
            for i in range(1, len(self.bannedTracks) - 1):
                listBannedGags += ', ' + self.bannedTracks[i]

            listBannedGags += (', or ' if self.pickable else ', and ') + TRACK_2_CONSTANT[self.bannedTracks[-1]]
        if self.pickable:
            self.desc = f'This Toon will face a punishment if they use {listBannedGags} Gags.'
        else:
            self.desc = f"This Toon's {listBannedGags} Gags have been disabled."


# region Firestarter
class Pyromaniac(DamageModifier, DefenseModifier):
    '''
    The Firestarter's effect for when fellow Cogs get defeated.
    '''

    def __init__(self) -> None:
        DamageModifier.__init__(self, -1, 0)
        self.defenseMod = 1.0
        self.name = 'Pyromaniac'
        self.icon = getIcon('pyromaniac_icon')
        self.updateEffect()

    
    def updateEffect(self) -> None:
        self.hidden = self.damageMod > 0
        self.desc = 'The Firestarter is taking {}\u0025 less damage and dealing {} more damage!'.format((1.0 - self.defenseMod) * 100, self.damageMod)

# endregion

# region Featherbedder
class Overhire(DamageModifier, DefenseModifier):
    '''
    The Featherbedder's damage and defense modifier depending on how many Cogs are present in battle.
    '''

    def __init__(self) -> None:
        DamageModifier.__init__(self, -1, 1.0)
        self.defenseMod = 1.0
        self.updateEffect()


    def updateEffect(self):
        self.desc = 'The Featherbedder is stronger together! '
        if self.damageMod == 1.0 and self.defenseMod == 1.0:
            self.desc += '...But not when alone.'


class PowerNap(DamageModifier, DefenseModifier):
    '''
    Cogs that join in the battle will be sleepy and weak, but as they wake, the damage and defense deficits become lesser.
    '''

    def __init__(self) -> None:
        DefenseModifier.__init__(self, 2, 0.1)
        self.damageMod = 0.0
        self.name = 'Power Nap'
        self.updateEffect()
    
    def updateEffect(self) -> None:
        self.defenseMod += 0.2
        self.damageMod += 0.2
        self.desc = 'This Cog is taking a power nap, and will take time to wake up. Currently, they will take {}\u0025 less damage and deal {}\u0025 less damage.'.format((1.0 - self.defenseMod) * 100, (1.0 - self.damageMod) * 100)


class PeacefulSlumber(DefenseModifier):
    '''
    The Featherbedder's way of preventing cheese so that he can have some Overhire.
    '''

    def __init__(self) -> None:
        DefenseModifier.__init__(self, -1, 1.0, hidden=True)
        self.name = 'Peaceful Slumber'
        self.good = True
        self.updateEffect()


    def updateEffect(self):
        self.hidden = self.defenseMod <= 1.0
        self.desc = 'The Featherbedder is taking {}\u0025 less damage.\n\nEvery round that they are alone, they will gain a 25\u0025 damage resistance.'.format(str((1.0 - self.defenseMod) * 100))

# endregion

# region Major Player
class RisingStarSuit(DamageModifier, ManagerBeneficiary):
    '''
    The Major Player's buff for his rising stars.
    '''

    def __init__(self, damageMod: int = 25) -> None:
        '''
        :param damageMod: The initial damage modifier for the Rising Stars.  Should be changeable due to differences in phases (phase 1 is an initial 30 damage buff, while phase 2 is 15).  Have a -5 difference due to updateEffect() causing an additional +5 damage boost upon initialization.
        '''
        DamageModifier.__init__(self, -1, damageMod)
        self.name = 'Rising Star'
        self.updateEffect()


    def updateEffect(self) -> None:
        self.damageMod += 5
        self.desc = 'This Cog is a Rising Star! Alongside a health boost, they will deal {} more damage (growing every turn). They also receive the same benefits as Manager Cogs.'.format(self.damageMod)


class LastTap(DamageModifier):
    '''
    The Major Player's slowly-increasing damage buff.
    '''

    def __init__(self) -> None:
        DamageModifier.__init__(self, -1, 4)
        self.name = 'Last Tap!'
        self.icon = getIcon('last_tap_icon')
        self.updateEffect()


    def updateEffect(self) -> None:
        self.damageMod += 1
        self.desc = 'The Major Player is going in for a grand finale! He will be dealing {} {} damage.'.format(self.damageMod, 'less' if self.damageMod < 0 else 'more')

# endregion

# region Chainsaw Consultant
class RevvingUp(DamageModifier, DefenseModifier):
    '''
    A status effect that determines how the Chainsaw Consultant operates.

    Attributes:
        rpm (int): How much RPM &times; 1,000 the Chainsaw Consultant has.
        reforesting (bool): Determines which perk and cheats he uses.&nbsp; If <code>False</code>, he gets a damage multiplier and access to cheats from phases 1 and 3 (Deadwood and Layoffs may need to be handled a different way).&nbsp; If <code>True</code>, he gets a damage resistance/vulnerability and access to phase 2 cheats.
        milestonesReached (dict): Whether or not RPM thresholds have been reached, which would reveal cheats at the corresponding RPM value.
        abilities (dict): The abilities the Chainsaw Consultant can use at the correct threshold.
    '''
    rpm: int
    reforesting: bool = False
    milestonesReached: dict[bool, dict[int, bool]] = {
        False: {
            12: False,
            14: False,
            17: False
        },
        True: {
            13: False,
            15: False,
            17: False
        }
    }
    abilities: dict[bool, dict[int, str]] = {
        False: {
            12: 'Offboarding',
            14: 'Cut the Slack',
            17: 'Marked Wood'
        },
        True: {
            13: 'Aggrandize',
            15: 'Chain Link',
            17: 'Scabbard'
        }
    }

    def __init__(self) -> None:
        StatusEffect.__init__(self, -1, icon='chainsaw_icon')
        self.damageMod = 1.0 # TODO: Figure out a way to prohibit this from being triggered when in Reforestation Mode.
        self.defenseMod = 1.0 # TODO: Figure out a way to prohibit this from being triggered when not in Reforestation Mode.
        self.good = True
        self.updateEffect()


    def updateEffect(self) -> None:
        for milestone in self.milestonesReached[self.reforesting]:
            if self.rpm >= milestone:
                self.milestonesReached[self.reforesting][milestone] = True

        self.damageMod = 1.0 if self.reforesting else (float(self.rpm) * 0.1)
        self.defenseMod = max(0.0, 1.0 + ((float(self.rpm) - 15.0) * 0.1)) if self.reforesting else 1.0
        self.name = 'Revved-Up: {},000 RPM'.format(self.rpm)
        self.desc = 'The Chainsaw Consultant is '
        if self.rpm > 10:
            self.desc += 'revving up!'
        else:
            self.desc += 'operating under normal conditions.'
        if self.reforesting:
            difference = int(round(abs(self.defenseMod - 1.0) * 100.0))
            if difference:
                self.desc += ' He will take {}\u0025 {} damage!'.format(difference, 'less' if self.defenseMod < 1.0 else 'more')
            else:
                self.desc += ' He will take normal damage!'
        elif self.rpm > 10:
            self.desc += ' He will deal {}\u0025 more damage!'.format(str((self.damageMod - 1.0) * 100))
        self.desc += '\n'
        for milestone in list(self.abilities[self.reforesting].keys()):
            self.desc += '\nAt {},000 RPM: '.format(milestone)
            if self.milestonesReached[self.reforesting][milestone]:
                self.desc += "Can use '{}'".format(self.abilities[self.reforesting][milestone])
            else:
                self.desc += '?????'

class Kickback(DefenseModifier):
    '''
    Glorified defense modifier for the Chainsaw Consultant.
    '''

    def __init__(self, defenseMod: float = 1.3) -> None:
        '''
        defenseMod: Allow for varying amounts due to the varying nature of Kickback (default 30% vulnerability, or 1.3x the damage).
        '''
        DefenseModifier.__init__(self, 2, defenseMod)
        self.name = 'Kickback'
        self.icon = getIcon('kickback_icon')
        self.updateEffect()


    def updateEffect(self) -> None:
        self.desc = 'The Chainsaw Consultant will take {}\u0025 more damage.'.format(str((self.defenseMod - 1.0) * 100))


class MarkedWood(StatusEffect):
    '''
    A Toon with this Status Effect will be dealt extra damage exclusively from the Chainsaw Consultant, hence why the DefenseModifier class will not be inherited.
    '''

    def __init__(self):
        StatusEffect.__init__(self, 1, name='Marked Wood', desc='The Chainsaw Consultant has marked this Toon, and unless interrupted by a different Toon, will target them this turn! They will take 75\u0025 more damage from his next attack.', icon='marked_wood_icon')
        self.defenseMod = 1.75
        self.good = False


class MarkedWoodSuit(StatusEffect):
    '''
    This is a status effect for whoever just marked a Toon. It will be hidden, but it will still be used to keep track of who he is going to target next.
    '''

    def __init__(self, targetId):
        '''
        :param targetId: The Toon he will target next.
        '''
        StatusEffect.__init__(self, 1, name='Marked Wood', desc='This Cog will retaliate against the last Toon who hits them or the Toon they marked if not hit.\n\nCurrent target: {}'.format(targetId), icon='marked_wood_icon', hidden=True)
        self.whoIWillTarget = targetId
        self.good = True


class SparkPlug(DamageOverTime):
    '''
    Chainsaw Consultant's damage over time.
    '''

    def __init__(self, attack: str) -> None:
        DamageOverTime.__init__(self, 2, 20, attack)
        self.name = 'Spark Plug'
        self.icon = getIcon('sparkplug_icon')
        self.updateEffect()


    def updateEffect(self) -> None:
        self.desc = 'This Toon will take {} damage per round.'.format(self.hpPerRound)

# endregion

# Bossbot Litigation Team
class TankMentality(Siphon, DamageAbsorption, LureResistance):
    '''
    The Powerhouse's perpetually changing status effect.
    '''

    def __init__(self):
        StatusEffect.__init__(self, -1, name='Tank Mentality', desc='The Powerhouse has no additional strengths at the moment.', icon=None)
        self.mode = None # Tank Mentality starts with nothing.
        self.good = True
        self.stealHp = 0.0
        self.intercepting = 0.0

    
    def updateEffect(self):
        '''
        Effects and what is shown will change depending on the mode it is set to.
        '''
        if not self.mode:
            self.icon = None
            self.desc = 'The Powerhouse has no additional strengths at the moment.'
        elif self.mode == 'syphon':
            self.icon = getIcon('ink_drain_icon')
            self.desc = 'The Powerhouse is syphoning Laff.'
        elif self.mode == 'absorbing':
            self.icon = getIcon('damage_absorb_icon')
            self.desc = 'The Powerhouse is absorbing damage.'
        elif self.mode == 'lureimmune':
            self.maxLureRounds = 0
            self.desc = 'The Powerhouse is immune to being Lured.'


# region Rainmaker
class StormCell(StatusEffect):
    '''
    When in this weather phase, she has pent-up damage and unleashes it after several turns, reduced when she is hit with Gags.

    Attributes:
        storedDamage (int): How much damage she will deal at the end of the phase.
    '''
    storedDamage: int

    def __init__(self):
        self.name = 'Storm Cell'
        self.desc = 'The Rainmaker is about to unleash a powerful lightning attack! The power of this attack is reduced for each Gag that hits her.'
        self.icon = getIcon('stormcell_icon')
        self.storedDamage = 36


class Monsoon(DefenseModifier):
    '''
    The defense modifier applied when the Rainmaker goes Monsoon.
    '''

    def __init__(self):
        DefenseModifier.__init__(self, 3, 0.1)
        self.name = 'Monsoon'
        self.desc = 'The Rainmaker is taking significantly less damage.'
        self.icon = getIcon('schadenfreude_icon')

# endregion

# region Witch Hunter
class WillOfThePeople(DefenseModifier):
    '''
    The Witch Hunter's fluctuating defense modifier.
    '''

    def __init__(self) -> None:
        DefenseModifier.__init__(self, -1, 0.6)
        self.name = 'Will of the People'
        self.updateEffect()

    
    def updateEffect(self) -> None:
        # I'm going to trust in BattleCalculatorAI shenanigans to fix up the damage resistances.
        self.desc = "The Witch Hunter is taking {}\u0025 less damage! Each time another Cog is defeated, this bonus decreases by 5\u0025. Each time 'Mob Mentality' is used, this bonus increases by 10\u0025.".format((1.0 - self.defenseMod) * 100)
        self.hidden = self.defenseMod >= 1.0


class Bewitchment(DefenseModifier):
    '''
    The Witch Hunter bewitches Toons to be targeted more frequently and take more damage.
    '''

    def __init__(self, defenseMod: float = 1.1) -> None:
        DefenseModifier.__init__(self, 1, defenseMod)
        self.name = 'Bewitchment'
        self.icon = getIcon('bewitched_icon')
        self.updateEffect()


    def updateEffect(self):
        self.desc = 'This Toon is Bewitched! Cogs are 75\u0025 more likely to target them, but they will deal 1.3x more damage to the Witch Hunter. Additionally, they will take {}x more damage.'.format(self.defenseMod)

# endregion

# region Count Erclaim
class ScopeCreep(DefenseModifier):
    '''
    Count Erclaim's ever-growing damage resistance.
    '''

    def __init__(self):
        DefenseModifier.__init__(self, -1, 1.0) # He will have this effect at the start, but it shall be hidden until he first uses it to increase his defense.
        self.icon = getIcon('scope_creep_icon')
        self.updateEffect()


    def updateEffect(self):
        self.hidden = self.defenseMod == 1.0
        self.desc = "The Count's damage resistance is creeping up, taking {}\u0025 less damage.".format((1.0 - self.defenseMod) * 100)

# endregion

# region Litigation Team
class Overconfidence(DamageModifier):
    '''
    However much less damage they deal due to overconfidence, probably as a result of them being altogether, and strength in numbers.
    '''

    def __init__(self) -> None:
        DamageModifier.__init__(self, -1, 0.6, hidden=False)
        self.name = 'Overconfidence'
        self.updateEffect()


    def updateEffect(self) -> None:
        self.desc = 'The Litigation Team overestimates their chances. They deal {}\u0025 less damage with their attacks'.format((1.0 - self.damageMod) * 100)


class Snapped(DefenseModifier):
    '''
    Glorified vulnerability for the Litigator's Snap.
    '''

    def __init__(self, defenseMod: float = 1.2) -> None:
        '''
        defenseMod: Allow this to be variate for various cases: 1. the Litigator snaps normally (1.2x damage taken), 2. the Litigator retaliates when soaked (1.1x damage taken), 3. the Litigator snaps with the Stenographer (1.4x damage taken), or 4. Chip Fan Club President snaps (1.25x damage taken).
        '''
        DefenseModifier.__init__(self, 2, defenseMod)
        self.icon = getIcon('vulnerable_icon')
        self.updateEffect()


    def updateEffect(self) -> None:
        self.desc = 'This Toon takes {}\u0025 more damage while vulnerable.'.format(str((self.defenseMod - 1.0) * 100))


class Sanctioned(DamageModifier):
    '''
    The Stenographer's gag effectiveness reduction.
    Professor Control: I have no idea if this means all things about a gag are decreased or if it's just the damage.  For now, just do damage.
    '''

    def __init__(self, damageMod: float = 0.5) -> None:
        '''
        damageMod: This must be variate due to the multiple cases this has, for example standard (0.5), with the Litigator (0.25), or after the Legal Bindings expire (0.75).
        '''
        DamageModifier.__init__(self, 2, damageMod)
        self.name = 'Sanctioned'


class CourtRecordStenographer(BanGagLevels):
    
    def __init__(self, bannedLevels) -> None:
        BanGagLevels.__init__(self, -1, bannedLevels, True)
        self.name = 'Court Record'


class Insurance(DamageOverTime, LureResistance, ManagerBeneficiary, DamageModifier):
    '''
    The Case Manager's heal over time effect for his Insurance Plan as well as other perks.
    '''

    def __init__(self, attack: str, hpPerRound: int = -50, damageMod: float = 1.0) -> None:
        '''
        hpPerRound: Allow this to be variate for when the Case Manager uses this while alone (-50) or when he is paired with the Scapegoat (-85).
        damageMod: If the Case Manager is paired with the Scapegoat, then his Insurance grants a 15% damage boost, or a 1.15x damage multiplier.
        '''
        DamageOverTime.__init__(self, 2, hpPerRound, attack)
        self.maxLureRounds = 2
        self.damageMod = damageMod
        self.name = 'Insurance'


    def updateEffect(self) -> None:
        self.desc = 'This Cog is insured! While insured, they have high Lure resistance, heal {} health every round, and receive the same benefits as Manager Cogs.'.format(abs(self.hpPerRound))


class LegallyBound(DamageOverTime):
    '''
    The Case Manager's damage over time effect for his Legal Bindings.
    '''

    def __init__(self, hpPerRound: int = 20) -> None:
        DamageOverTime.__init__(self, 2, hpPerRound, 'CaseManagerLegallyBound')
        self.name = 'Legally Bound'
        self.updateEffect()


    def updateEffect(self) -> None:
        self.desc = 'While legally bound, this Toon will take {} damage per round.'.format(self.hpPerRound)


class CourtRecordCaseManager(BanGagTracks):

    def __init__(self, bannedTracks) -> None:
        BanGagTracks.__init__(self, -1, bannedTracks, True)
        self.name = 'Court Record'


class RageBuilding(DamageAbsorption):
    '''
    Status effect for the Scapegoat abosrbing damage while getting angrier as the turns pass and actions are taken.

    Attributes:
        rage (float): The anger in the Scapegoat.&nbsp; Once it reaches 100\u0025, he loses this in exchange for Enraged.
    '''
    rage: float

    def __init__(self):
        DamageAbsorption.__init__(self, -1, 0.3)
        self.rage = 0.0 # Every 10 damage is 1 rage, so every 1 damage is 0.1 rage; we can still do ints, we just have to do a little more conversion.
        self.icon = getIcon('defense_mode_icon')
        self.updateEffect()

    
    def updateEffect(self) -> None:
        '''
        We know how easily angered the Scapegoat gets, causing his rage to rise.  Update the name every turn.
        '''
        self.name = 'Rage Building: {}\u0025'.format(self.rage)
        self.desc = "Scapegoat's rage is building...\n\nScapegoat will absorb {}\u0025 of the damage dealt to other Cogs while in this mode!".format(self.intercepting * 100)


class Enraged(DamageModifier, DefenseModifier):
    '''
    The temporary status effect that the Scapegoat gets when he gets angry.
    '''

    def __init__(self, defenseMod: float = 0.75) -> None:
        '''
        defenseMod: This number is different depending on whether or not he is in desperation (0.75 for normal, 0.7 for desperation).
        '''
        DamageModifier.__init__(self, 2, 1.3)
        self.defenseMod = defenseMod
        self.name = 'Enraged'
        self.icon = getIcon('rage_mode_icon')
        self.updateEffect()


    def updateEffect(self) -> None:
        self.desc = "The Scapegoat is enraged!\n\nScapegoat will deal {}\u0025 more damage while in this mode!".format((self.damageMod - 1.0) * 100)


class EvidenceSuppression(StatusEffect):
    '''
    The Scapegoat's means of hiding a Toon.
    '''
    
    def __init__(self) -> None:
        pass

# endregion

# region Mint Supervisor
class InsurancePolicy(StatusEffect):
    '''
    As long as he has his assets, the Mint Supervisor is insured.  Damage increase should probably be handled in its own DamageModifier status effect, like Corporate Clash.
    '''

    def __init__(self):
        StatusEffect.__init__(self, -1, name='Insurance Policy')
        self.good = True

# endregion

# region Plutocrat
class LayLow(DefenseModifier):
    '''
    Charon's defense system for taking reduced damage at the cost of taking more Shatter damage.
    '''

    def __init__(self) -> None:
        DefenseModifier.__init__(self, -1, 0.8)
        self.name = 'Lay Low'
        self.updateEffect()


    def updateEffect(self) -> None:
        self.desc = 'Charon takes +300\u0025 Shatter damage but -{}\u0025 damage from Gags.'.format(str((1.0 - self.defenseMod) * 100))


class GhostPayroll(DamageModifier):
    '''
    Glorified attack buff for Satellite Investors.
    '''

    def __init__(self) -> None:
        DamageModifier.__init__(self, -1, 1.3)
        self.name = 'Ghost Payroll'
        self.icon = getIcon('ghost_payroll_icon')
        self.updateEffect()


    def updateEffect(self) -> None:
        self.desc = 'This Satellite investor will deal {}x more damage.'.format(self.damageMod)


class SlushFund(DefenseModifier):
    '''
    Glorified defense for Plutocrat and his Satellite Investors.
    '''

    def __init__(self) -> None:
        DefenseModifier.__init__(self, 2, 0.8)
        self.icon = getIcon('slush_fund_icon')
        self.updateEffect()


    def updateEffect(self) -> None:
        self.desc = 'This Cog will take {}\u0025 {} damage!'.format(str((1.0 - self.defenseMod) * 100), 'less' if self.good else 'more')


class MarketBubble(DamageModifier, DefenseModifier):
    '''
    The Plutocrat's progressively-increasing damage buff with a risk of being shattered.

    Attributes:
        crashTurns (int): The amount of turns that the Plutocrat has the damage vulnerability for.
    '''
    crashTurns: int

    def __init__(self) -> None:
        StatusEffect.__init__(self, -1, name='Market Bubble', icon='market_bubble_icon')
        self.damageMod = 0
        self.defenseMod = 1.0
        self.crashTurns = 1 # Undone in updateEffect()
        self.good = True
        self.updateEffect()

    
    def updateEffect(self):
        self.crashTurns -= 1 # Reduce the crash turns every round.
        if self.damageMod > 0:
            self.desc = "The Market Bubble is growing! The Plutocrat's attacks will deal {} more damage. SHATTER damage dealt to the Plutocrat is increased by {}\u0025, and will burst the Market bubble.".format(self.damageMod, self.damageMod / 3 * 5)
        elif self.crashTurns > 0:
            self.desc = 'The Market Bubble has crashed! The Plutocrat will take {}\u0025 more damage per attack.'.format((1.0 - self.defenseMod) * 100)
        else:
            self.desc = 'The Market Bubble is currently inactive.'

# endregion

# region Count Erfit
class Ripped(DamageModifier):
    '''
    Count Erfit's damage boost that climbs with sacrificed Cogs.
    '''

    def __init__(self) -> None:
        DamageModifier.__init__(self, -1, 0, hidden=True)
        self.name = 'Ripped'
        self.icon = getIcon('ripped_icon')
        self.updateEffect()

    
    def updateEffect(self) -> None:
        self.hidden = self.damageMod > 0
        self.desc = 'Count Erfit is getting ripped! All of his attacks will deal {} {} damage.'.format(abs(self.damageMod), 'more' if self.good else 'less')


class Hydrated(AccuracyModifier):
    '''
    Glorified accuracy bonus for Count Erfit and the Rainmaker.
    '''

    def __init__(self, roundsLeft: int = 2) -> None:
        AccuracyModifier.__init__(self, roundsLeft, 20)
        self.name = 'Hydrated'
        self.icon = getIcon('inventory_glass_of_water', fromPath='phase_3.5/models/gui/inventory_icons')
        self.updateEffect()


    def updateEffect(self) -> None:
        self.desc = 'This combatant is hydrated, and their accuracy is {} by {}\u0025.'.format('increased' if self.good else 'decreased', abs(self.accuracyMod))


class DriedOut(AccuracyModifier):
    '''
    At first glance it appears to be a glorified accuracy deficit, but when paired with hydration, it causes something extra (Energized).
    '''

    def __init__(self) -> None:
        AccuracyModifier.__init__(self, 3, -50)
        self.desc = 'This toon has been wrung dry and has {}\u0025 accuracy!'.format(self.accuracyMod)


# endregion

# region High Roller
class RaisingTheAnte(DamageModifier):
    '''
    High Roller's damage-up for the Toons.
    '''

    def __init__(self, damageMod: float = 10.0) -> None:
        '''
        damageMod: Do we want varied Gag damages?  I don't know, but just in case, I'll leave a 15.0 damage multiplier by default.
        '''
        DamageModifier.__init__(self, -1, damageMod, hidden=False)
        self.name = 'Raising the Ante'
        self.icon = getIcon('raise_the_ante_icon')
        self.updateEffect()


    def updateEffect(self) -> None:
        self.desc = 'The stakes are much higher, and so are your Gag damages! Gags are {}x more powerful!'.format(self.damageMod)


class HarmoniousColors(DefenseModifier):
    '''
    The High Roller's ever-waning defense against the Toons.
    '''

    def __init__(self):
        DefenseModifier.__init__(self, -1, 0.0)
        self.name = 'Harmonious Colors'
        self.desc = 'The colors, they are so pretty... High Roller is currently INVINCIBLE!!'
        self.icon = getIcon('harmonious_colors_icon')


    def updateEffect(self):
        '''
        We are probably handling it much differently in Aristotown, but Clash has it to after one round, the status effect becomes a 95%-damage-resistance.  The gradual decrease in defense as High Roller Silhouettes are defeated should probably be handled in BattleCalculatorAI.
        '''
        if self.defenseMod < 0.05:
            self.defenseMod = 0.05
        self.desc = "The colors, they are so pretty... High Roller's Silhouettes are causing him to take {}\u0025 less damage.".format(str((1.0 - self.defenseMod) * 100))


class RefractionBarrier(DefenseModifier):
    '''
    Glorified defense for High Roller Silhouettes.
    '''

    def __init__(self) -> None:
        DefenseModifier.__init__(self, -1, -222)
        self.desc = 'This silhouette is a strange being of light! Attacks will do {} {} damage on it!'.format(abs(self.defenseMod), 'less' if self.good else 'more')

# endregion

# region Director of Public Affairs
class DisruptiveAdvertisement(StatusEffect):
    '''
    A status effect that merely announces the Cog is getting more attacks.
    '''

    def __init__(self) -> None:
        StatusEffect.__init__(self, 1, name='Disruptive Advertisement', desc='If not interrupted, the D.O.P.A. will gain an extra attack!', icon='disruptive_advertisement_icon')
        self.good = True

# endregion

# region Prethinker
class ForwardThinking(StatusEffect):
    '''
    Needed for Brain Wave.
    '''

    def __init__(self) -> None:
        StatusEffect.__init__(self, -1, name='Forward Thinking', desc='The Prethinker and his peers will brainstorm your demise at the end of every turn!', icon='brain_icon')
        self.good = True

# endregion

# region Multislacker
class OffTheClock(DefenseModifier):
    '''
    Defense modifier for when the Multislacker is accompanied by other Cogs.
    '''

    def __init__(self) -> None:
        DefenseModifier.__init__(self, -1, 0.3)
        self.name = 'Off the Clock'
        self.updateEffect()


    def updateEffect(self) -> None:
        self.desc = 'While other Cogs are in battle, the Multislacker takes {}\u0025 less damage!'.format(str((1.0 - self.defenseMod) * 100))

# endregion

# region Pacesetter
class RushJob(StatusEffect, FireImmunity):
    '''
    Rush Jobs are status effects that should be cleared when the Cog is hit with the corresponding Gag track.

    Attribute:
        trackToUse (int): The track that needs to be used to clear this effect.
    '''
    trackToUse: int
    defenseMod: Union[int, float] = 1.0

    def __init__(self, trackToUse: int) -> None:
        '''
        trackToUse: The Gag track that must be used to clear the status effect.  It must use the imports, or we are not proceeding.
        '''
        if isTrack(trackToUse):
            self.trackToUse = trackToUse
        else:
            raise ValueError('trackToUse is not any track constant (see toontown/battle/StatusEffects.py for more info)!')
        self.roundsLeft = -1
        self.good = True
        self.name = 'Rush Job'
        if True: # TODO: Figure out a proper way to check whether or not the Cog that has the Rush Job is the Pacesetter.
            self.defenseMod = 0.6 # This class does not inherit the DefenseModifier class, so it should not really matter for now.
        else:
            self.defenseMod = 1.0
        self.updateEffect()


    def updateEffect(self) -> None:
        self.desc = 'The Pacesetter will punish ALL Toons if you do not use {} on this Cog!! This Cog cannot be fired, but the right Gag used against this Cog will be much more likely to hit.'.format(TRACK_2_CONSTANT[self.trackToUse])
        # TODO: Figure out a proper way to check whether or not the Cog that has the Rush Job is the Pacesetter.
        if isinstance(self.defenseMod, float):
            if self.defenseMod != 1.0:
                self.desc += '\n\nThe wrong Gag will deal {}\u0025 less damage.'.format((1.0 - self.defenseMod) * 100)
        elif self.defenseMod != 0:
            self.desc += '\n\nThe wrong Gag will deal {} {} damage.'.format(self.defenseMod, 'more' if self.defenseMod <= 0 else 'less')
        self.icon = getIcon(AvPropsNew[self.trackToUse][6], fromPath='phase_3.5/models/gui/inventory_icons')
            
            

class HurrySickness(DamageModifier):
    '''
    Glorified damage down for the Pacesetter.
    '''

    def __init__(self) -> None:
        DamageModifier.__init__(self, 2, 0.6)
        self.name = 'Hurry Sickness'
        self.icon = getIcon('hurry_sickness_icon')
        self.updateEffect()


    def updateEffect(self) -> None:
        self.desc = "This Toon couldn't keep up with the Pacesetter and thus will deal {}\u0025 less damage.".format(str((1.0 - self.damageMod) * 100))


class MovingGoalposts(BanGags):
    '''
    The Pacesetter's constantly changing Gag bans.
    '''

    def __init__(self) -> None:
        BanGags.__init__(self, -1, [], pickable=True)
        self.name = 'Moving Goalposts'
        self.desc = 'Every round, the Pacesetter randomizes blocked Gag levels!'
        self.updateEffect()

    
    def updateEffect(self):
        self.bannedGags = []
        from random import randint
        for track in (HEAL_TRACK, TRAP_TRACK, LURE_TRACK, THROW_TRACK, SQUIRT_TRACK, ZAP_TRACK, SOUND_TRACK, DROP_TRACK):
            self.bannedGags.append((track, randint(5, 8)))

# endregion

# region Pressure Division
class OffTheAir(DamageModifier, DefenseModifier):
    '''
    A little proof-of-concept thing to show what is possible with this new style of cheats.
    '''

    def __init__(self) -> None:
        DamageModifier.__init__(self, 3, 0.7)
        self.defenseMod = 0.7
        self.name = 'Off the Air'


class Hustling(StatusEffect):
    '''
    The Racketeer will need Toons to pick a Gag track.
    '''

    def __init__(self, trackToUse: int) -> None:
        '''
        trackToUse: The Gag track that must be used to clear the status effect.  It must use the imports, or we are not proceeding.
        '''
        if isTrack(trackToUse):
            self.trackToUse = trackToUse
        else:
            raise ValueError('trackToUse is not any track constant (see toontown/battle/StatusEffects.py for more info)!')
        StatusEffect.__init__(self, 1, name='Hustling')
        self.desc = 'The Racketeer has ordered this Toon to use the {} Track!'.format(TRACK_2_CONSTANT[self.trackToUse])
        self.good = False


class Contracted(StatusEffect):
    '''
    The Union Buster can give this as a result of Contract Enforcement.
    '''

    def __init__(self) -> None:
        StatusEffect.__init__(self, 99, name='Contracted', desc='This Cog has been contracted!') # Professor Control: I don't really know what a Contracted Cog can do besides potentially avoiding the Union Bust.
        self.good = True

# endregion

# region Land Acquisiton Architect/Director of Land Development
class InkDrain(DamageModifier):
    '''
    Used to reduce Gag effectiveness.
    '''

    def __init__(self, damageMod: float = 0.75) -> None:
        '''
        damageMod: If the L.A.A. uses this, it's a 25% deficit (0.75x the damage). If the D.O.L.D. uses this, it's a 40% deficit (0.6x the damage).
        '''
        DamageModifier.__init__(self, 2, damageMod)
        self.name = 'Ink Drain'
        self.icon = getIcon('ink_drain_icon')
        self.updateEffect()

    
    def updateEffect(self) -> None:
        self.desc = 'All gags are {}\u0025 {} effective.'.format((1.0 - self.damageMod) * 100, 'more' if self.good else 'less')

# endregion

# region Gatekeeper
class CoreCompetency(DamageModifier, LureResistance):

    def __init__(self) -> None:
        LureResistance.__init__(self, 2)
        self.damageMod = 0
        self.updateEffect()


    def updateEffect(self) -> None:
        '''
        Every turn, use this method to add 3 more damage to the buff.
        '''
        self.damageMod += 3
        self.desc = 'This Cog has a +100 health bonus! Additionally, the Cog is dealing {} {} damage, gaining more every round. Destroy this Cog to steal their damage bonus!'.format(self.damageMod, 'less' if self.damageMod < 0 else 'more')

# endregion
