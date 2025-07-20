'''
Use this file to hold all status effect data.
'''
DEFAULT_STATUS_ICON_PATH = 'phase_3.5/models/gui/battlegui/status_effects'

# def getIcon(node, fromPath = DEFAULT_STATUS_ICON_PATH):
#     return loader.loadModel(fromPath).find('**/' + node)

class StatusEffect:
    '''
    All status effects shall inherit this class, with basic functionalities.
    '''

    def __init__(self, roundsLeft, good, name = 'Status Effect', desc = 'A status effect.', icon = None, iconPath = DEFAULT_STATUS_ICON_PATH, targetable = True, tenured = False, hidden = False):
        '''
        roundsLeft: An int that determines how many rounds of the status effect remain.  -1 for it to be permanent unless cleared.
        good: A boolean that determines if this status effect is good or bad, which is supposed to be for the circle behind icon.
        name: The name of the status effect.  Really, it's the header and can have some status things in it if desired, like Scapegoat's rage or Chainsaw Consultant's RPM.
        desc: The description of the status effect that describes what it does.
        icon: The icon node of the status effect based on the given path.
        iconPath: For when we might want a different collection of model nodes for the icon (e.g. the Glass of Water for the Hydrated status effect).
        hidden: Whether or not this status effect is hidden (e.g. the 340% damage vulnerability Count Erfit gets from maxing out his arms).
        '''
        self.roundsLeft = roundsLeft
        self.good = good
        self.name = name
        self.desc = desc
        # Professor Control: I don't know if this will work or if I am missing something.
        # if icon:
        #     self.icon = loader.loadModel(iconPath).find('**/%s' % icon)
        self.targetable = targetable
        self.tenured = tenured
        self.hidden = hidden
    
    def setRoundsLeft(self, roundsLeft):
        '''
        There are likely some cases where we would like to change the rounds around, so this method will be convenient.
        '''
        self.roundsLeft = roundsLeft
    
    def updateEffect(self):
        '''
        Other classes will inherit this, but it will be overridden.
        We may want to change a few attributes as the turns pass, or they may get changed outside of these classes.  Keep them up to date with this method.
        '''
        pass

    def subtractRound(self):
        '''
        Call this every round for all status effects to subtract the rounds and to update the effect if necessary.
        '''
        self.roundsLeft -= 1
        self.updateEffect()

# General status effects.
class DamageModifier(StatusEffect):
    '''
    Change the outgoing damage of whoever has this status effect.
    '''

    def __init__(self, roundsLeft, damageMod, hidden = False):
        '''
        damageMod: The damage modifier.  It can either be an int which will offer a flat damage change, or a float which will be a multiplier.
        '''
        good = damageMod >= 0.0
        if isinstance(damageMod, float):
            desc = "This combatant's attacks are %sx as powerful." % damageMod
        else:
            desc = 'This combatant is dealing %s %s damage.' % (abs(damageMod), 'more' if good else 'less')
        StatusEffect.__init__(self, roundsLeft, good, name='Damage %s' % ('Up' if good else 'Down'), desc=desc, icon='toon_damage_%s_icon' % ('up' if good else 'down'), hidden=hidden) # For the icon, I did not yet know how I would distinguish between a Cog and a Toon, but I think that is some BattleCalculatorAI.py stuff that can be resolved later.
        self.damageMod = damageMod

class DefenseModifier(StatusEffect):
    '''
    Change the incoming damage of whoever has this status effect.
    '''

    def __init__(self, roundsLeft, defenseMod, hidden = False):
        '''
        defenseMod: The defense modifier.  It can either be an int which will offer a flat damage change, or a float which will be a multiplier.  NOTE: For int, negative means the combatant will take less damage, while positive will make them take more damage.  For float, of course, incoming damage is multiplied.
        '''
        good = defenseMod <= 0.0
        if isinstance(defenseMod, float):
            desc = 'This combatant is taking %sx as much damage.' % defenseMod
        else:
            desc = 'This combatant is taking %s %s damage.' % (abs(defenseMod), 'less' if good else 'more')
        StatusEffect.__init__(self, roundsLeft, good, name='Damage Reduction' if good else 'Vulnerable', desc=desc, icon='%sshield_icon' % ('' if good else '_broken'), hidden=hidden)
        self.defenseMod = defenseMod

class DamageOverTime(StatusEffect):
    '''
    Damage or heal over a number of turns.
    '''

    def __init__(self, roundsLeft, hpPerRound, attack, hidden = False):
        '''
        hpPerRound: As one would expect, this is an int determines the amount of damage taken per round.  Despite being a damage over time, we should use a negative integer to denote healing over time.
        attack: The attack that plays for the damage over time. It should not be a method where a Cog is needed for it to function.
        '''
        good = hpPerRound < 0
        desc = 'This combatant is %s %s HP per round.' % ('gaining' if good else 'losing', abs(hpPerRound))
        StatusEffect.__init__(self, roundsLeft, good, '%s Over Time' % ('Heal' if good else 'Damage'), desc=desc, icon='%s_over_time_icon' % ('heal' if good else 'damage'))
        self.hpPerRound = hpPerRound
        self.attack = attack

class AccuracyModifier(StatusEffect):
    '''
    Alter the accuracy of an attack.
    '''

    def __init__(self, roundsLeft, accuracyMod, hidden = False):
        '''
        accuracyMod: The amount of accuracy to increase or decrease.
        '''
        good = accuracyMod >= 0.0
        StatusEffect.__init__(self, roundsLeft, good, name='Accuracy %s' % ('Up' if good else 'Down'), desc="This combatant's attacks are %s %s accurate." % (str(accuracyMod) + '%', 'more' if good else 'less'), icon='toon_accuracy_%s_icon' % ('up' if good else 'down'), hidden=hidden)
        self.accuracyMod = accuracyMod
    
    def updateEffect(self):
        '''
        Should the accuracy ever change, be sure that the icons are up to date.
        '''
        self.good = self.accuracyMod >= 0.0
        self.desc = "This combatant's attacks are %s %s accurate." % (str(self.accuracyMod) + '%', 'more' if self.good else 'less')
        # self.icon = loader.loadModel(DEFAULT_STATUS_ICON_PATH).find('**/toon_accuracy_%s_icon' % 'up' if self.good else 'down')

class DamageAbsorption(StatusEffect):
    '''
    Take some damage on behalf of other Cogs.
    '''

    def __init__(self, roundsLeft, intercepting, hidden = False):
        '''
        intercepting: How much HP will be intercepted.  If an int, a flat number of damage, but if a float, then a multiplier (e.g. if it is set to 0.25, another Cog will take 0.75 of the damage while this Cog takes the rest).
        '''
        StatusEffect.__init__(self, roundsLeft, True, name='Damage Absorption', desc='This Cog will endure %sx the other Cogs take.' % intercepting, icon='damage_absorb_icon', hidden=hidden)
        self.intercepting = intercepting

class Siphon(DamageModifier):
    '''
    Regain HP after landing a hit.  Inheriting the DamageModifier class since the Major Player's siphon offers an attack deficit.  It might also be possible to use this as a recoil, but that can be done later.
    '''

    def __init__(self, roundsLeft, damageMod, stealHp, hidden = False):
        '''
        stealHp: Either an int or a float.  If int, give that amount of HP if the attack lands.  If a float, then make it a multiplier based on how much health was taken.
        '''
        DamageModifier.__init__(self, roundsLeft, damageMod, hidden=hidden)
        self.stealHp = stealHp
        self.name = 'Siphon'
        # self.icon = loader.loadModel(DEFAULT_STATUS_ICON_PATH).find('**/ink_drain_icon')
        self.updateEffect()
    
    def updateEffect(self):
        self.desc = 'This Cog is ready to siphon your Laff! It '
        if isinstance(self.damageMod, float):
            self.desc += 'does %sx damage%s ' % (self.damageMod, ', but' if self.damageMod < 0.0 else ' and')
        else:
            self.desc += 'does %s %s damage%s ' % (abs(self.damageMod), 'less' if self.damageMod < 0 else 'more', ', but' if self.damageMod < 0 else ' and')
        self.desc += 'will heal '
        if isinstance(self.stealHp, float):
            self.desc += 'for %sx the damage it deals!' % self.stealHp
        else:
            self.desc += '%s HP for each Toon it successfully hits!' % self.stealHp

# Toons' status effects.
class UniteCooldown(StatusEffect):
    '''
    Forbid the use of unites.
    '''

    def __init__(self, roundsLeft):
        StatusEffect.__init__(self, roundsLeft, False, name='Unite Cooldown', desc='Your Unites are currently on cooldown.', icon=None)
        self.noUnites = True

class RewardCooldown(StatusEffect):
    '''
    Forbid the use of rewards.
    '''

    def __init__(self, roundsLeft, noUnites = True, noSOS = True, noForges = True, noSues = True, noFires = True):
        StatusEffect.__init__(self, roundsLeft, False, name='Reward Cooldown', desc='Your Boss Rewards are currently on cooldown.', icon=None)
        self.noUnites = noUnites
        self.noSOS = noSOS
        self.noForges = noForges
        self.noSues = noSues
        self.noFires = noFires

class Cheer(AccuracyModifier):
    '''
    Glorified accuracy boost.
    '''

    def __init__(self, roundsLeft = 1):
        '''
        roundsLeft: Make this variate because of the prestige.
        '''
        AccuracyModifier.__init__(self, roundsLeft, 10.0)
        self.name = 'Cheer'
        self.desc = "This Toon's attack accuracy is increased by %s%." % self.accuracyMod
        # self.icon = loader.loadModel(DEFAULT_STATUS_ICON_PATH).find('**/cheer_icon')

class MarkedForLaugh(DefenseModifier):
    '''
    A damage vulnerability for when a Toon uses Throw against a Cog.
    '''

    def __init__(self):
        DefenseModifier.__init__(self, 1, 1.1)
        self.name = 'Marked for Laugh'
        self.desc = 'This Cog is more vulnerable, and will take 10% more damage.'
        # self.icon = loader.loadModel(DEFAULT_STATUS_ICON_PATH).find('**/marked_icon')

# Cogs' status effects.
# General.
class ExtraAttacks(StatusEffect):
    '''
    Allow the Cog to attack extra times.
    '''

    def __init__(self, extraAttacks, roundsLeft = -1, hidden = False):
        '''
        roundsLeft: I have no clue why this would be used, but I'm thinking of if a grunt Cog would use this for some reason?  I'll keep this parameter just in case we have ideas.
        '''
        desc = 'This Cog has gained %s extra attack%s!' % (extraAttacks, '' if extraAttacks == abs(1) else 's')
        StatusEffect.__init__(self, roundsLeft, True, name='Additional Attack', desc=desc, icon='extra_attacks_icon', hidden=hidden)

class LureResistance(StatusEffect):
    '''
    Limit the max turns a Cog can be Lured for.
    '''

    def __init__(self, maxLureRounds, roundsLeft = -1, hidden = False):
        '''
        hidden: It's a Witch Hunter thing.
        '''
        if maxLureRounds == 0:
            desc = 'This Cog is entirely immune to being LURED.'
        else:
            desc = 'This Cog will stay LURED for %s %s.' % (maxLureRounds, '' if abs(maxLureRounds) == 1 else 's')
        StatusEffect.__init__(self, roundsLeft, True, name='Lure Resistance', desc=desc, icon=None)
        self.maxLureRounds = maxLureRounds
        self.hidden = hidden

class ManagerBeneficiary(StatusEffect):
    '''
    Grant the Cog Manager benefits (immunity to Pink Slips and Cease and Desists).
    '''

    def __init__(self, roundsLeft = -1, hidden = False):
        StatusEffect.__init__(self, roundsLeft, True, name='Manager Beneficiary', desc='This Cog cannot be fired or sued.', icon='tie_icon', tenured=True, hidden=hidden)

class Overcharged(DamageModifier, LureResistance, ManagerBeneficiary):
    '''
    All Cogs that have at least 1.5x their health will gain this status effect.
    '''

    def __init__(self):
        ManagerBeneficiary.__init__(self, -1)
        self.damageMod = 1.5
        self.maxLureRounds = 2
        self.name = 'Overcharged'
        self.desc = 'This Cog is Overcharged!\n\nWhile Overcharged, they have high Lure Resistance, deal 50% more damage, and receive the same benefits as Manager Cogs.'
        # self.icon = loader.loadModel(DEFAULT_STATUS_ICON_PATH).find('**/overcharge_icon')

class GagBans(StatusEffect):
    '''
    No clue what I am going to do with this.
    '''
    pass

class BanGagLevels(StatusEffect):
    '''
    Ban Gag levels.  The Gags can either be selectable or nonselectable.  If selectable, incur a punishment on Toons.
    '''

    def __init__(self, roundsLeft, bannedLevels, pickable = True):
        '''
        bannedLevels: A list of Gag levels that will be forbidden to use.
        '''
        StatusEffect.__init__(self, roundsLeft, False, name='Gag Level Prohibition', icon='backfire_icon')
        self.bannedLevels = bannedLevels
        self.pickable = pickable
        if len(bannedLevels) == 1:
            listBannedGags = str(bannedLevels[0])
        elif len(bannedLevels) == 2:
            listBannedGags = '%s or %s' % (bannedLevels[0], bannedLevels[1])
        else:
            listBannedGags = str(bannedLevels[0])
            for i in range(1, len(bannedLevels) - 1):
                listBannedGags += ', ' + str(bannedLevels[i])

            listBannedGags = ', or ' + str(bannedLevels[len(bannedLevels) - 1])
        if self.pickable:
            self.desc = 'This Toon will face a punishment if they use level %s Gags.' % listBannedGags
        else:
            self.desc = "This Toon's level %s Gags have been disabled." % listBannedGags

class BanGagTracks(StatusEffect):
    '''
    Ban Gag tracks.  The Gags can either be selectable or nonselectable.  If selectable, incur a punishment on Toons.
    '''
    from toontown.toonbase.ToontownBattleGlobals import HEAL_TRACK, TRAP_TRACK, LURE_TRACK, THROW_TRACK, SQUIRT_TRACK, ZAP_TRACK, SOUND_TRACK, DROP_TRACK

    def __init__(self, roundsLeft, bannedTracks, pickable = True):
        '''
        bannedTracks: A list of Gag tracks that will be forbidden to use.  Use only the imports to keep track of the tracks.
        '''
        for bannedTrack in bannedTracks:
            if bannedTrack is not self.HEAL_TRACK and bannedTrack is not self.TRAP_TRACK and bannedTrack is not self.LURE_TRACK and bannedTrack is not self.THROW_TRACK and bannedTrack is not self.SQUIRT_TRACK and bannedTrack is not self.ZAP_TRACK and bannedTrack is not self.SOUND_TRACK and bannedTrack is not self.DROP_TRACK: # Check to make sure we are using the constant.
                raise ValueError('bannedTrack is not any track constant (see toontown/battle/StatusEffects.py for more info)!')

        StatusEffect.__init__(self, roundsLeft, False, name='Gag Track Prohibition', icon='backfire_icon')
        self.bannedTracks = bannedTracks
        self.pickable = pickable
        TRACK_2_CONSTANT = {self.HEAL_TRACK: 'Toon-up',
         self.TRAP_TRACK: 'Trap',
         self.LURE_TRACK: 'Lure',
         self.THROW_TRACK: 'Throw',
         self.SQUIRT_TRACK: 'Squirt',
         self.ZAP_TRACK: 'Zap',
         self.DROP_TRACK: 'Drop'}
        if len(bannedTracks) == 1:
            listBannedGags = TRACK_2_CONSTANT[bannedTracks[0]]
        elif len(bannedTracks) == 2:
            listBannedGags = TRACK_2_CONSTANT[bannedTracks[0]] + ' or ' + TRACK_2_CONSTANT[bannedTracks[1]]
        else:
            listBannedGags = TRACK_2_CONSTANT[bannedTracks[0]]
            for i in range(1, len(bannedTracks) - 1):
                listBannedGags += ', ' + bannedTracks[i]

            listBannedGags = ', or ' + TRACK_2_CONSTANT[bannedTracks[len(bannedTracks) - 1]]
        if self.pickable:
            self.desc = 'This Toon will face a punishment if they use %s Gags.' % listBannedGags
        else:
            self.desc = "This Toon's %s Gags have been disabled."

# Firestarter
class Pyromaniac(DamageModifier, DefenseModifier):
    '''
    The Firestarter's effect for when fellow Cogs get defeated.
    '''

    def __init__(self):
        DamageModifier.__init__(self, -1, 5, hidden=False)
        self.defenseMod = 0.92
        self.name = 'Pyromaniac'
        # self.icon = loader.loadModel(DEFAULT_STATUS_ICON_PATH).find('**/pyromaniac_icon')
    
    def updateEffect(self):
        self.desc = 'The Firestarter is taking %s%s less damage and dealing %s more damage!' % (1.0 - self.defenseMod, '%', self.damageMod)

# Featherbedder
class PeacefulSlumber(DefenseModifier):
    '''
    The Featherbedder's way of preventing cheese so that he can have some Overhire.
    '''

    def __init__(self):
        DefenseModifier.__init__(self, -1, 0.0, hidden=True)
        self.name = 'Peaceful Slumber'
        self.updateEffect()
    
    def updateEffect(self):
        self.hidden = self.defenseMod <= 1.0
        self.desc = 'The Featherbedder is taking %s less damage.\n\nEvery round that they are alone, they will gain a %s damage resistance.' % (str((1.0 - self.defenseMod) * 100) + '%', '%')

# Major Player
class LastTap(DamageModifier):
    '''
    The Major Player's slowly-increasing damage buff.
    '''

    def __init__(self):
        DamageModifier.__init__(self, -1, 4)
        self.name = 'Last Tap!'
        # self.icon = loader.loadModel(DEFAULT_STATUS_ICON_PATH).find('**/last_tap_icon')
        self.updateEffect()
    
    def updateEffect(self):
        self.damageMod += 1
        self.desc = 'The Major Player is going in for a grand finale! He will be dealing %s more damage.' % self.damageMod

# Chainsaw Consultant
class RevvingUp(StatusEffect):
    '''
    A status effect that determines how the Chainsaw Consultant operates.
    '''

    def __init__(self):
        StatusEffect.__init__(self, -1, True, name='Revved-Up: 10,000 RPM', icon='chainsaw_icon')
        self.rpm = 10 # For the sake of display (I don't know how to do Python input masking if that's even possible), do this and multiply this number by 1000 to see "actual" RPM.
        self.reforesting = False # Determines which perk and cheats he uses. If False, he gets a damage multiplier and access to cheats from phases 1 and 3 (Deadwood and Layoffs may need to be handled a different way). If True, he gets a damage resistance/vulnerability and access to phase 2 cheats.
        self.damageMod = 1.0 # TODO: Figure out a way to prohibit this from being triggered when in Reforestation Mode.
        self.defenseMod = 0.5 # TODO: Figure out a way to prohibit this from being triggered when not in Reforestation Mode.
        self.milestonesReached = {
            # The keys are booleans for Reforestation mode.
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
        self.abilities = {
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
    
    def updateEffect(self):
        for i in range(len(self.milestonesReached[self.reforesting].keys())):
            if self.rpm >= self.milestonesReached[self.reforesting][i]:
                self.milestonesReached[self.reforesting][i] = True

        self.damageMod = float(self.rpm) * 0.1
        # Formula for defense mod is yet undetermined.
        self.name = 'Revved-Up: %s,000 RPM' % self.rpm
        self.desc = 'The Chainsaw Consultant is '
        if self.rpm > 10:
            self.desc += 'revving up!'
        else:
            self.desc += 'operating under normal conditions.'
        if self.reforesting:
            self.desc += ' He will take %s %s damage!'
        elif self.rpm > 10:
            self.desc += ' He will deal %s more damage!' % (str((self.damageMod - 1.0) * 100) + '%')
        self.desc += '\n'
        for milestone in self.abilities[self.reforesting].keys():
            self.desc += '\nAt %s,000 RPM: ' % milestone
            if self.milestonesReached[self.reforesting][milestone]:
                self.desc += "Can use '%s'" % self.abilities[self.reforesting][milestone]
            else:
                self.desc += '?????'

class SparkPlug(DamageOverTime):
    '''
    Chainsaw Consultant's damage over time.
    '''

    def __init__(self, attack):
        DamageOverTime.__init__(self, 2, 20, attack)
        self.name = 'Spark Plug'
        self.desc = 'This Toon will take %s damage per round.' % self.hpPerRound
        # self.icon = loader.loadModel(DEFAULT_STATUS_ICON_PATH).find('**/sparkplug_icon')

# Witch Hunter
class WillOfThePeople(DefenseModifier):
    '''
    The Witch Hunter's fluctuating defense modifier.
    '''

    def __init__(self):
        DefenseModifier.__init__(self, -1, 0.6)
        self.name = 'Will of the People'
        self.updateEffect()
    
    def updateEffect(self):
        # I'm going to trust in BattleCalculatorAI shenanigans to fix up the damage resistances.
        self.desc = "The Witch Hunter is taking %s%s less damage! Each time another Cog is defeated, this bonus decreases by 5%. Each time 'Mob Mentality' is used, this bonus increases by 10%." % ((1.0 - self.defenseMod) * 100, '%')
        self.hidden = self.defenseMod >= 1.0

# Litigation Team
class Snapped(DefenseModifier):
    '''
    Glorified vulnerability for the Litigator's Snap.
    '''

    def __init__(self, defenseMod = 1.2):
        '''
        defenseMod: Allow this to be variate for various cases: 1. the Litigator snaps normally (1.2x damage taken), 2. the Litigator retaliates when soaked (1.1x damage taken), 3. the Litigator snaps with the Stenographer (1.4x damage taken), or 4. Chip Fan Club President snaps (1.25x damage taken).
        '''
        DefenseModifier.__init__(self, 2, defenseMod)
        # self.icon = loader.loadModel(DEFAULT_STATUS_ICON_PATH).find('**/vulnerable_icon')
        self.desc = 'This Toon takes %s% more damage while vulnerable.' % ((defenseMod - 1) * 100)

class Insurance(DamageOverTime, LureResistance, ManagerBeneficiary):
    '''
    The Case Manager's heal over time effect for his Insurance Plan as well as other perks.
    '''

    def __init__(self, attack, roundsLeft = 2, hpPerRound = -50):
        '''
        roundsLeft: This is probably a matter to concern ourselves with later, as we do not have functionality for a random Cog to be chosen, at least not to my (Professor Control's) knowledge, but the Case Manager gets Insurance only for one round.  Let the number here be variate to account for that scenario when we cross that bridge.
        hpPerRound: Allow this to be variate for when the Case Manager uses this while alone (-50) or when he is paired with the Scapegoat (-85).
        '''
        DamageOverTime.__init__(self, roundsLeft, hpPerRound, attack)
        self.maxLureRounds = 2
        self.tenured = True
        self.name = 'Insurance'
        self.desc = 'This Cog is insured! While insured, they have high Lure resistance, heal %s health every round, and receive the same benefits as Manager Cogs.' % abs(self.hpPerRound)

class LegallyBound(DamageOverTime):
    '''
    The Case Manager's damage over time effect for his Legal Bindings.
    '''

    def __init__(self):
        '''
        attack: We need this to be able to make the attack the Case Manager's Legally Bound and have his doId.
        '''
        DamageOverTime.__init__(self, 2, 20, 'CaseManagerLegallyBound')
        self.name = 'Legally Bound'
        self.desc = 'While legally bound, this Toon will take 20 damage per round.'

class RageBuilding(DamageAbsorption):
    '''
    Status effect for the Scapegoat abosrbing damage while getting angrier as the turns pass and actions are taken.
    '''

    def __init__(self):
        DamageAbsorption.__init__(self, -1, 0.3)
        self.rage = 0.0 # Every 10 damage is 1 rage, so every 1 damage is 0.1 rage; we can still do ints, we just have to do a little more conversion.
        self.desc = "Scapegoat's rage is building...\n\nScapegoat will absorb 30% of the damage dealt to other Cogs while in this mode!"
        # self.icon = loader.loadModel(DEFAULT_STATUS_ICON_PATH).find('**/defense_mode_icon')
        self.updateEffect()
    
    def updateEffect(self):
        '''
        We know how easily angered the Scapegoat gets, causing his rage to rise.  Update the name every turn.
        '''
        self.name = 'Rage Building: %s' % (str(self.rage) + '%')

class Enraged(DamageModifier):
    '''
    The temporary status effect that the Scapegoat gets when he gets angry.
    '''

    def __init__(self):
        DamageModifier.__init__(self, 2, 1.3)
        self.name = 'Enraged'
        self.desc = "The Scapegoat is enraged!\n\nScapegoat will deal 30% more damage while in this mode!"
        # self.icon = loader.loadModel(DEFAULT_STATUS_ICON_PATH).find('**/rage_mode_icon')

# Mint Supervisor
class InsurancePolicy(StatusEffect):
    '''
    As long as he has his assets, the Mint Supervisor is insured.  Damage increase should probably be handled in its own DamageModifier status effect, like Corporate Clash.
    '''

    def __init__(self):
        StatusEffect.__init__(self, -1, True, name='Insurance Policy')

# Plutocrat
class GhostPayroll(DamageModifier):
    '''
    Glorified attack buff for Satellite Investors.
    '''
    def __init__(self):
        DamageModifier.__init__(self, -1, 1.3)
        self.name = 'Ghost Payroll'
        # self.icon = loader.loadModel(DEFAULT_STATUS_ICON_PATH).find('**/ghost_payroll_icon')
        self.updateEffect()
    
    def updateEffect(self):
        self.desc = 'This Satellite investor will deal %sx more damage.' % self.damageMod

class SlushFund(DefenseModifier):
    '''
    Glorified defense for Plutocrat and his Satellite Investors.
    '''

    def __init__(self):
        DefenseModifier.__init__(self, 2, 0.85)
        self.desc = 'This Cog will take 15% less damage!'
        # self.icon = loader.loadModel(DEFAULT_STATUS_ICON_PATH).find('**/slush_fund_icon')

class MarketBubble(DamageModifier, DefenseModifier):
    '''
    The Plutocrat's progressively-increasing damage buff with a risk of being shattered.
    '''

    def __init__(self):
        StatusEffect.__init__(self, -1, True, name='Market Bubble', desc='The Market Bubble is currently inactive.', icon='market_bubble_icon')
        self.damageMod = 0
        self.defenseMod = 0
        self.crashTurns = 0
    
    def updateEffect(self):
        pass

# Count Erfit
class Ripped(DamageModifier):
    '''
    Count Erfit's damage boost that climbs with sacrificed Cogs.
    '''

    def __init__(self):
        DamageModifier.__init__(self, -1, 0, hidden=True)
        self.name = 'Ripped'
        # self.icon = loader.loadModel(DEFAULT_STATUS_ICON_PATH).find('**/ripped_icon')
        self.updateEffect()
    
    def updateEffect(self):
        self.good = self.damageMod > 0
        self.hidden = self.good
        self.desc = 'Count Erfit is getting ripped! All of his attacks will deal %s %s damage.' % (abs(self.damageMod), 'more' if self.good else 'less')

# High Roller
class RaisingTheAnte(DamageModifier):
    '''
    High Roller's damage-up for the Toons.
    '''

    def __init__(self, damageMod = 15.0):
        '''
        damageMod: Do we want varied Gag damages?  I don't know, but just in case, I'll leave a 15.0 damage multiplier by default.
        '''
        DamageModifier.__init__(self, -1, damageMod, hidden=False)
        self.name = 'Raising the Ante'
        self.desc = 'The stakes are much higher, and so are your Gag damages! Gags are %sx more powerful!' % self.damageMod
        # self.icon = loader.loadModel(DEFAULT_STATUS_ICON_PATH).find('**/raise_the_ante_icon')

class HarmoniousColors(DefenseModifier):
    '''
    The High Roller's ever-waning defense against the Toons.
    '''

    def __init__(self):
        DefenseModifier.__init__(self, -1, 0.0)
        self.name = 'Harmonious Colors'
        self.desc = 'The colors, they are so pretty... High Roller is currently INVINCIBLE!!'
        # self.icon = loader.loadModel(DEFAULT_STATUS_ICON_PATH).find('**/harmonious_colors_icon')
    
    def updateEffect(self):
        '''
        We are probably handling it much differently in Aristotown, but Clash has it to after one round, the status effect becomes a 95%-damage-resistance.  The gradual decrease in defense as High Roller Silhouettes are defeated should probably be handled in BattleCalculatorAI.
        '''
        if self.defenseMod < 0.05:
            self.defenseMod = 0.05
        self.desc = "The colors, they are so pretty... High Roller's Silhouettes are causing him to take %s less damage." % (str((1.0 - self.defenseMod) * 100) + '%')

class RefractionBarrier(DefenseModifier):
    '''
    Glorified defense for High Roller Silhouettes.
    '''

    def __init__(self):
        DefenseModifier.__init__(self, -1, -222)
        self.desc = 'This silhouette is a strange being of light! Attacks will do %s %s damage on it!' % (abs(self.defenseMod), 'less' if self.good else 'more')

class DisruptiveAdvertisement(StatusEffect):
    '''
    A status effect that merely announces the Cog is getting more attacks.
    '''

    def __init__(self):
        StatusEffect.__init__(self, 1, True, name='Disruptive Advertisement', desc='If not interrupted, the D.O.P.A. will gain an extra attack!', icon='disruptive_advertisement_icon')

class OffTheClock(DefenseModifier):
    '''
    Defense modifier for when the Multislacker is accompanied by other Cogs.
    '''

    def __init__(self):
        DefenseModifier.__init__(self, -1, 0.3)
        self.name = 'Off the Clock'
        self.desc = 'While other Cogs are in battle, the Multislacker takes %s less damage!' % (str((1.0 - self.defenseMod) * 100) + '%')

class HurrySickness(DamageModifier):
    '''
    Glorified damage down for the Pacesetter.
    '''

    def __init__(self):
        DamageModifier.__init__(self, 2, 0.6)
        self.name = 'Hurry Sickness'
        self.desc = "This Toon couldn't keep up with the Pacesetter and thus will deal %s less damage." % (str((1.0 - self.damageMod) * 100) + '%')
        # self.icon = loader.loadModel(DEFAULT_STATUS_ICON_PATH).find('**/hurry_sickness_icon')

class DanceSession(DamageModifier, DefenseModifier):
    '''
    A little proof-of-concept thing to show what is possible with this new style of cheats.
    '''

    def __init__(self):
        DamageModifier.__init__(self, -1, )
        self.defenseMod = 0.7

class Contracted(StatusEffect):
    '''
    The Union Buster can give this as a result of Contract Enforcement.
    '''

    def __init__(self):
        StatusEffect.__init__(self, 99, True, name='Contracted', desc='This Cog has been contracted!') # Professor Control: I don't really know what a Contracted Cog can do besides potentially avoiding the Union Bust.

class CoreCompetency(DamageModifier, LureResistance):

    def __init__(self):
        LureResistance.__init__(self, 2)
        self.damageMod = 0
        self.updateEffect()
    
    def updateEffect(self):
        '''
        Every turn, use this method to add 3 more damage to the buff.
        '''
        self.damageMod += 3
        self.desc = 'This Cog has a +100 health bonus! Additionally, the Cog is dealing %s more damage, gaining more every round. Destroy this Cog to steal their damage bonus!' % self.damageMod
