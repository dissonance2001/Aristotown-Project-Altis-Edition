import math

from direct.interval.LerpInterval import LerpHprInterval
from panda3d.core import Vec4, NodePath, TextNode

from toontown.utils import text
from toontown.battle.attacks.base.AttackEnum import AttackEnum
from toontown.toonbase import TTLocalizer
from toontown.battle import BattleGlobals
from toontown.toonbase import ToontownGlobals
from toontown.battle.BattleEventGlobals import BEG
from toontown.battle.statuses.StatusEffectDefinitions import buildStatusEffectText, buildStatusEffectAttributes,\
    buildStatusEffectImageProperties, buildStatusEffectBuffStatus, \
    NO_ROUNDS, THIS_ROUND, DEBUFF, BUFF, NEUTRAL
from .StatusEffectEnums import *
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.interval.IntervalGlobal import Sequence, LerpColorScaleInterval, Func, Wait, LerpFunctionInterval
from copy import deepcopy

from ...events.apriltoons.findthefamily import FindTheFamilyGlobals
from ...toon.gui import GuiBinGlobals
from ...utils.ColorHelper import hexToPCol

NORMAL = 0
OVERCLOCKED = 1

BuffToCol = {
    BUFF:       Vec4(0.98, 0.914, 0.439, 1),
    DEBUFF:     Vec4(0.349, 0.773, 0.914, 1),
    NEUTRAL:    Vec4(0.9, 0.9, 0.9, 1),
}

StatusEffectAttributes = buildStatusEffectAttributes()
StatusEffectId2Text = buildStatusEffectText()
StatusEffectId2ImageProperties = buildStatusEffectImageProperties()
StatusEffectId2Type = buildStatusEffectBuffStatus()


# Define custom effect titles/descriptions here.
def makeTitleAndDesc(statusEffect, effectId):
    if effectId not in StatusEffectId2Text:
        return 'Unknown Status Effect', ''
    info = StatusEffectId2Text[effectId]
    title = info[0]
    description = info[1]

    if effectId in (SEE.EFFECT_SUIT_DAMAGE_BOOST,):
        description = description % str(round(statusEffect.getMultiplier(), 2))
    elif effectId == SEE.EFFECT_MANAGER_CHAINSAW_CONSULTANT:
        rpm = int(10_000 + statusEffect.revvingUpStacks * 1000)
        title = title % f'{rpm:,}'

        attackMultiplier = round(statusEffect.attackMultiplier, 2)
        defenseMultiplier = int(round((1.0 - statusEffect.defenseMultiplier) * 100))

        components = description[:]
        if statusEffect.revvingUpStacks == 0:
            description = components[0]
        else:
            description = components[1]

        if statusEffect.currentPhase != 2:
            if attackMultiplier != 1:
                description += components[2].format(components[3].format(attackMultiplier))
        else:
            if defenseMultiplier > 0:
                description += components[2].format(components[4].format(abs(defenseMultiplier)))
            elif defenseMultiplier < 0:
                description += components[2].format(components[5].format(abs(defenseMultiplier)))
        
        # Display all of the attack descriptions on the Status Effect based on
        # how many rev stacks we have.
        description += '\1TextSmaller\1'
        for i, desc in TTLocalizer.ChainsawConsultantAttackDesc[statusEffect.currentPhase].items():
            rpm = int(10_000 + i * 1000)
            description += f"\n{TTLocalizer.ChainsawConsultantAttackRPM.format(f'{rpm:,}')}"
            if i <= statusEffect.highestRevStacks:
                description += desc
            else:
                description += TTLocalizer.ChainsawConsultantAttackDescHidden
        description += '\2'

    elif effectId in (SEE.EFFECT_MULTI_LEVEL_MARKETING, SEE.EFFECT_GENERIC_EXTRA_ATTACKS):
        plural = 's' if statusEffect.numExtraAttacks > 1 else ''
        description = description % (int(statusEffect.numExtraAttacks), plural)
    elif effectId == SEE.EFFECT_SUIT_LURED:
        presString = f' ({TTLocalizer.GagPrestiged})' if statusEffect.prestige else ''
        title = title + presString
        description = description % (math.ceil(statusEffect.knockback))
    elif effectId == SEE.EFFECT_OVERCLOCKED_FOREMAN:
        info = info[round(statusEffect.getType())]
        title = info[0]
        description = info[1]
    elif effectId == SEE.EFFECT_TOONS_ACCURACY_UP:
        if statusEffect.getOverride() == -1:
            description = description % abs(int(statusEffect.getAccuracyChange()))
        elif statusEffect.getAccuracyChange() == 100:
            description = info[2]
        else:
            description = info[3] % statusEffect.getAccuracyChange()
    elif effectId in (SEE.EFFECT_CONFUSION, SEE.EFFECT_HYDRATED, SEE.EFFECT_CHEER):
        description = description % abs(int(statusEffect.getAccuracyChange()))
    elif effectId in (SEE.EFFECT_COGS_DAMAGE_DOWN, SEE.EFFECT_SANCTIONED, SEE.EFFECT_COUNT_CREEP, 
                      SEE.EFFECT_SLUSH_FUND, SEE.EFFECT_INK_DRAIN):
        multiplier = statusEffect.getMultiplier()
        description = description % int(round((1.0 - multiplier) * 100))
    elif effectId in (SEE.EFFECT_CHAIN_LINKED,):
        multiplier = int(round((1.0 - statusEffect.getMultiplier()) * 100))
        if multiplier == 0:
            description = description[0] % description[2]
        elif multiplier == 100:
            description = description[0] % (description[1] % multiplier)
        else:
            description = description[0] % ((description[1] % multiplier) + ''.join(description[3:1:-1]))
    elif effectId in (SEE.EFFECT_SUIT_DRENCHED,):
        multiplier = statusEffect.getMultiplier()
        description = description.format(int(round((1.0 - multiplier) * 100)))
    elif effectId in (SEE.EFFECT_VULNERABLE, SEE.EFFECT_MARKED_FOR_LAUGH, SEE.EFFECT_DAMAGE_TAKEN_UP,
                      SEE.EFFECT_MARKED_WOOD, SEE.EFFECT_MANAGER_MAJOR_PLAYER, SEE.EFFECT_KICKBACK,
                      SEE.EFFECT_DAMAGE_TAKEN_DOWN, SEE.EFFECT_TOON_MULT_DAMAGE_UP, SEE.EFFECT_AITH_DAMAGE_TAKEN_UP,
                      SEE.EFFECT_SOAK_RESISTANCE, SEE.EFFECT_OUT_FOR_LUNCH):
        multiplier = statusEffect.getMultiplier()
        description = description % int(round((multiplier - 1.0) * 100))
    elif effectId == SEE.EFFECT_PEACEFUL_SLUMBER:
        multiplier = statusEffect.getMultiplier()
        description = description.format(int(round((multiplier - 1.0) * 100)))
    elif effectId in (SEE.EFFECT_SKELECOG, SEE.EFFECT_VIRTUAL_COG):
        multiplier = int(statusEffect.getChosenPercent() * 100)
        rounds = int(abs(statusEffect.roundModifier))
        plural = '' if rounds == 1 else 's'
        if multiplier == 100:
            description = info[2] % (int(abs(statusEffect.roundModifier)), plural)
        else:
            description = description % ('Red' if multiplier < 100 else 'Green', multiplier, int(abs(statusEffect.roundModifier)), plural)
    elif effectId in (SEE.EFFECT_RIPPED, SEE.EFFECT_SUIT_ADDITIVE_DAMAGE_BOOST, SEE.EFFECT_LAST_TAP,
                      SEE.EFFECT_STAR_OF_THE_SHOW_TOON, SEE.EFFECT_POWER_NAP_KILL_DMG_BOOST, SEE.EFFECT_GATEKEEPER_TOON_PIERCE,
                      SEE.EFFECT_VIRAL_SENSATION):
        multiplier = statusEffect.getMultiplier()
        description = description % int(multiplier)
    elif effectId == SEE.EFFECT_HOLLYWOOD_STAR:
        multiplier = int(statusEffect.getMultiplier())
        description = info[1] % multiplier if multiplier else info[2]
    elif effectId == SEE.EFFECT_STAR_OF_THE_SHOW:
        if statusEffect.isSuperstar():
            title = title[1]
            description = description[1]
        else:
            title = title[0]
            description = description[0]
        multiplier = statusEffect.getMultiplier()
        description = description % int(multiplier)
    elif effectId == SEE.EFFECT_SIPHON:
        multiplier = statusEffect.getMultiplier()
        description = description % (int(round(abs(multiplier - 1) * 100)), int(statusEffect.healingMult))
    elif effectId == SEE.EFFECT_COURT_RECORD:
        gagLevel = statusEffect.getGagLevel()
        levelText = int(gagLevel + 1)
        gagLevel2 = statusEffect.getGagLevel2()
        if gagLevel2 != -1:
            levelText2 = int(gagLevel2 + 1)
            if levelText < levelText2:
                levelText = f'{levelText} and {levelText2}'
            else:
                levelText = f'{levelText2} and {levelText}'
        description = description % levelText
    elif effectId == SEE.EFFECT_SCAPEGOAT_RAGE:
        index = 1 if statusEffect.getInRage() else 0
        title = title[index]
        if index == 0:
            title = title % int(statusEffect.getRageAmount())

        descriptionBase = description[index]
        if index == 1:
            if not statusEffect.getRageAndDesperation():
                descriptionBase = descriptionBase.format(description[2])
            else:
                descriptionBase = descriptionBase.format('')

        description = descriptionBase
    elif effectId == SEE.EFFECT_CASE_MANAGER_HOT:
        amount = statusEffect.getAmount()
        description = description % str(int(amount))
    elif effectId in (SEE.EFFECT_CASE_MANAGER_DOT, SEE.EFFECT_SPARK_PLUG):
        amount = statusEffect.getAmount()
        description = description % str(int(amount))
    elif effectId == SEE.EFFECT_SUIT_TRAPPED:
        level = int(statusEffect.getTrapLevel())
        damage = int(statusEffect.getTrapDamage())
        if level == BattleGlobals.UBER_GAG_LEVEL_INDEX:
            gagString = TTLocalizer.BattleGlobalAvPropUberStrings[AttackEnum.TOON_TRAP]
        else:
            gagString = TTLocalizer.BattleGlobalAvPropStrings[AttackEnum.TOON_TRAP][level]
        # Say some if we're looking at marbles
        article = 'some' if level == 3 else 'a'
        title = title % gagString
        description = description % (article, gagString, BattleGlobals.LureTrappedSuitBonus, damage)
    elif effectId == SEE.EFFECT_LURE_RESISTANCE:
        effectiveness = round(statusEffect.getAmount())
        if effectiveness == -1:
            description = description[0]
        else:
            description = description[1] % (effectiveness, '' if effectiveness == 1 else 's')
    elif effectId == SEE.EFFECT_TOON_DAMAGE_UP:
        gagTrack = int(statusEffect.getGagTrack())
        boostAmount = statusEffect.getMultiplier()
        if gagTrack == -1:
            gagTrackTitle = ''
        else:
            gagTrackTitle = f'{TTLocalizer.BattleGlobalTracksUpper[gagTrack]} '
        formattedGagTrackTitle = f"\1GagTrack_{TTLocalizer.BattleGlobalTracks[gagTrack]}\1{gagTrackTitle}\2" if gagTrack != -1 else ''
        gagTrackDamage = {AttackEnum.TOON_HEAL: "laff", AttackEnum.TOON_LURE: "knockback"}.get(gagTrack, "damage")
        uses = int(round(statusEffect.getUses()))
        numLeft = f' {uses}' if uses > 1 else ''
        title = title % gagTrackTitle
        dealForText = 'heal for' if gagTrack == AttackEnum.TOON_HEAL else 'deal'
        plurality = 's' if uses > 1 else ''
        description = description.format(
            numLeft, formattedGagTrackTitle, plurality, dealForText, f"\1deepGreen\1+{int(boostAmount)}\2", gagTrackDamage
        ) if not statusEffect.isDisabled() else ''
        # Also include "inactive" descriptions for other weaker effects that are not currently in activation
        weakEffects = ([statusEffect] if statusEffect.isDisabled() else []) + statusEffect.otherWeakerEffects[:]
        if len(weakEffects):
            newLine = '\n' if not statusEffect.isDisabled() else ''
            description += f"\1TextSmaller\1{newLine}\2"
        for i, weakEffect in enumerate(weakEffects):
            inactiveBase = info[2]
            weakUses = int(round(weakEffect.getUses()))
            weakNumLeft = f' {weakUses}' if weakUses > 1 else ''
            weakDealText = {AttackEnum.TOON_HEAL: "heal", AttackEnum.TOON_LURE: "knockback"}.get(gagTrack, "damage")
            weakPlurality = 's' if weakUses > 1 else ''
            description += ('' if (i == 0 and statusEffect.isDisabled()) else '\n') + inactiveBase.format(
                f"\1deepGreen\1+{int(weakEffect.getMultiplier())}\2", weakDealText, weakNumLeft, formattedGagTrackTitle, weakPlurality
            )
    elif effectId == SEE.EFFECT_DIVING:
        description = description[1 if statusEffect.hasSavior else 0] + info[2]
    elif effectId == SEE.EFFECT_MANAGER_GATEKEEPER:
        if base.localAvatar.getStatusEffectOfId(SEE.EFFECT_GATEKEEPER_TOON_PIERCE):
            description = info[2]
        else:
            description = description % round(abs(statusEffect.defenseMultiplier - 1) * 100)
    elif effectId == SEE.EFFECT_GATEKEEPER_FODDER_BONUS:
        description = description.format(round(statusEffect.getMultiplier()))
    elif effectId == SEE.EFFECT_MANAGER_FEATHERBEDDER:
        # first format the variables
        damageBoost  = statusEffect.attackMultiplier
        defenseBoost = statusEffect.defenseMultiplier
        # then, make the boost numbers appropriate
        damageBoost  = round(abs(damageBoost - 1) * 100)
        defenseBoost = round(abs(defenseBoost - 1) * 100)
        # format
        if damageBoost != 0 and defenseBoost != 0:
            description = description + (info[2][1] % (damageBoost, defenseBoost))
        else:
            description = description + info[2][0]
    elif effectId == SEE.EFFECT_BACKBURNER:
        damageAmp = round(abs(statusEffect.attackMultiplier))
        defAmp = round(abs(statusEffect.defenseMultiplier - 1) * 100)
        percentHpDamage = round(abs(statusEffect.percentHpDamage) * 100)
        rounds = int(abs(statusEffect.roundModifier))
        plural = '' if rounds == 1 else 's'
        description = description.format(damageAmp, defAmp, percentHpDamage, rounds, plural)
    elif effectId == SEE.EFFECT_WOODCHIPPER:
        amount = statusEffect.getAmount()
        description = description % str(int(amount))
    elif effectId == SEE.EFFECT_MANAGER_PACESETTER:
        timescale = statusEffect.getTimescale()
        maxedOut = statusEffect.isMaxed()
        difficulty = statusEffect.getDifficulty()
        if not maxedOut:
            title = title[0]
            description = description[0] % timescale
        else:
            title = title[1]
            description = description[2]
    elif effectId in (SEE.EFFECT_ENCORE, SEE.EFFECT_WINDED):
        boostAmount = statusEffect.getMultiplier()
        description = description % int(round((boostAmount - 1.0) * 100))
    elif effectId in (SEE.EFFECT_HEAVY_RAIN_RAINMAKER, SEE.EFFECT_POWER_NAP, SEE.EFFECT_FTF_FOREMAN_SLEEPY_POWER_NAP):
        # first format the variables
        damageBoost  = statusEffect.attackMultiplier
        defenseBoost = statusEffect.defenseMultiplier
        # then, make the boost numbers appropriate
        damageBoost  = round(abs(damageBoost - 1) * 100)
        defenseBoost = round(abs(defenseBoost - 1) * 100)
        # format
        description = description % (defenseBoost, damageBoost)
    elif effectId == SEE.EFFECT_MANAGER_FIRESTARTER:
        # first format the variables
        damageBoost  = statusEffect.attackMultiplier
        defenseBoost = statusEffect.defenseMultiplier
        # then, make the boost numbers appropriate
        damageBoost  = int(damageBoost)
        defenseBoost = round(abs(defenseBoost - 1) * 100)
        # format
        description = description % (defenseBoost, damageBoost)
    elif effectId == SEE.EFFECT_FOCUSED_DEFENSE:
        # first format the variables
        defenseBoost = statusEffect.multiplier
        # then, make the boost numbers appropriate
        defenseBoost = round(abs(defenseBoost - 1) * 100)
        # format
        description = description % defenseBoost
    elif effectId == SEE.EFFECT_UNION_BUST:
        roundText = info[2][0 if statusEffect.getRounds() >= 2 else 1]
        description = description + roundText
    elif effectId == SEE.EFFECT_OIL_RAIN_HOT:
        amount = statusEffect.getAmount()
        description = description % str(int(amount))
    elif effectId == SEE.EFFECT_OIL_RAIN_DOT:
        amount = statusEffect.getAmount()
        description = description % str(int(amount))
    elif effectId == SEE.EFFECT_DAMAGE_DOWN:
        # first format the variables
        damageBoost  = statusEffect.getMultiplier()
        # then, make the boost numbers appropriate
        damageBoost  = round(abs(damageBoost - 1) * 100)
        # format
        description = description % damageBoost
    elif effectId == SEE.EFFECT_RED_THREAD:
        multiplier = statusEffect.connectedSuitMultiplier if statusEffect.av.isSuit() else statusEffect.connectedToonMultiplier
        description = description.format(round(multiplier * 100))
    elif effectId == SEE.EFFECT_FLATTENED_DAMAGE_TAKEN:
        multiplier = statusEffect.getMultiplier()
        relativeText = "less" if multiplier < 0 else "more"
        textColor = "Green" if multiplier < 0 else "Red"
        description = description.format(textColor, int(multiplier), relativeText)
    elif effectId == SEE.EFFECT_HEAVY_RAIN:
        from ...toon.DistributedToonBase import DistributedToonBase
        description = description.format(
            av = 'Toon' if isinstance(statusEffect.getAv(), DistributedToonBase) else 'Cog',
            multiplier = round(abs(statusEffect.getMultiplier() - 1) * 100),
            damageAbsorbed = round(statusEffect.extraArgs[1]),
        )
    elif effectId in (SEE.EFFECT_HURRY_SICKNESS,):
        # first format the variables
        damageBoost  = statusEffect.attackMultiplier
        defenseBoost = statusEffect.defenseMultiplier
        # then, make the boost numbers appropriate
        damageBoost  = round(abs(damageBoost - 1) * 100)
        defenseBoost = round(abs(defenseBoost - 1) * 100)
        # format
        if statusEffect.mode != OVERCLOCKED:
            if statusEffect.fromAttorney:
                description = description[2] % damageBoost
            else:
                description = description[0] % damageBoost
        else:
            description = description[1] % (damageBoost, defenseBoost)
    elif effectId in (SEE.EFFECT_TRIAL_BY_FIRE,):
        avType = 'Suit' if statusEffect.getAv().isSuit() else 'Toon'
        heal = str(int(round(statusEffect.getAmount() * 100)))
        description = description % (avType, heal)
    elif effectId == SEE.EFFECT_GHOST_PAYROLL:
        description = description % str(round(statusEffect.getMultiplier(), 2))
    elif effectId == SEE.EFFECT_RUSH_JOB:
        desc, vulnerabilityLine, attorneyDesc = description
        description = (attorneyDesc if statusEffect.fromAttorney else desc) % TTLocalizer.ToonTrackPropertyNames[statusEffect.getTrack()]
        if statusEffect.getAv().style.name != 'psetter':
            vulnerabilityLine = vulnerabilityLine % str(round(abs(statusEffect.DamageMultiplier - 1) * 100))
            description = '\1TextShrink\1' + description + vulnerabilityLine + '\2'
    elif effectId == SEE.EFFECT_BEWITCHMENT:
        vulnerableText = (description[1] % str(round(statusEffect.defenseMultiplier, 2))) if statusEffect.defenseMultiplier != 1 else ''
        description = description[0] % (str(round(abs(statusEffect.getAmount() - 1) * 100)), statusEffect.attackMultiplier, vulnerableText)
    elif effectId == SEE.EFFECT_MANAGER_PLUTOCRAT:
        if statusEffect.marketBubbleStacks > 0:
            description = description[0] % (int(statusEffect.getMultiplier()), round(abs(statusEffect.getShatterMultiplier() - 1) * 100))
        elif statusEffect.marketBubbleStacks == -1:
            description = description[2] % int(round(abs(statusEffect.getVulnerabilityDamage() - 1) * 100))
        else:
            description = description[1]
    elif effectId == SEE.EFFECT_MANAGER_WITCH_HUNTER:
        mobSize = int(statusEffect.client_currentMobSize)
        if mobSize > 0:
            description = description[1] % (int(statusEffect.client_currentMobSize), '' if mobSize == 1 else 's') + description[2]
        else:
            description = description[0] + description[2]
    elif effectId == SEE.EFFECT_WILL_OF_THE_PEOPLE:
        description = description.format(
            str(int(round((1.0 - statusEffect.multiplier) * 100))),
            str(int(round(statusEffect.decreaseAmount * 100))),
            str(int(round(statusEffect.increaseAmount * 100)))
        )
    elif effectId == SEE.EFFECT_AGGRANDIZE:
        description = description % str(int(round(statusEffect.absorbMultiplier * 100)))
    elif effectId in (SEE.EFFECT_COGS_DAMAGE_ABSORB, SEE.EFFECT_COGS_DAMAGE_ABSORB_INSTANT):
        description = description % str(int(round((1 - statusEffect.absorbMultiplier) * 100)))
    elif effectId == SEE.EFFECT_COMMERCIAL:
        rounds = int(statusEffect.getRounds())
        description = description % (str(rounds), '' if rounds < 2 else 's')
    elif effectId == SEE.EFFECT_HARMONIOUS_COLORS:
        if statusEffect.getAv().getStatusEffectOfId(SEE.EFFECT_HR_UNTOUCHABLE):
            description = info[2]
        else:
            description = description % str(int(round((1 - statusEffect.defenseMultiplier) * 100)))
    elif effectId == SEE.EFFECT_HIGHROLLER_CLONE:
        info = info[round(statusEffect.getType())]
        title = info[0]
        description = info[1]
    elif effectId == SEE.EFFECT_PIP_COUNTER:
        pips = int(statusEffect.getRounds())
        description = description % (str(pips), text.plural(pips))
        if statusEffect.cooldownEffects:
            description += '\n'
            for cooldown in statusEffect.cooldownEffects:
                rounds = int(cooldown.getRounds())
                cooldownInfo = info[2] % (TTLocalizer.StatusEffectInactive if cooldown.isDisabled() else '',
                                          str(int(cooldown.pip + 1)), str(rounds), text.plural(rounds))
                description += cooldownInfo
    elif effectId == SEE.EFFECT_TRIVIA:
        description = description % statusEffect.getName()
    elif effectId == SEE.EFFECT_FTF_PRISMATIC_TOON:
        toonName = statusEffect.getAv().getName()
        title = title % toonName
    elif effectId == SEE.EFFECT_FTF_SUPERVISOR_ABACUS:
        description = description % f'{"Above" if statusEffect.isAbove else "Below"} {int(round(statusEffect.levelChoice))} levels'
    elif effectId == SEE.EFFECT_FTF_SUPERVISOR_ACCOUNTANT:
        targetChoice = int(round(statusEffect.targetChoice))
        description = description % f'{targetChoice} target{text.plural(targetChoice)}'
    elif effectId == SEE.EFFECT_PIP_DISCOUNT:
        description = description % str(int(statusEffect.getDiscount()))
    elif effectId == SEE.EFFECT_PUZZLE:
        description = description % BattleGlobals.getFancyTrackText(statusEffect.getTrack())

    if statusEffect.isDisabled() and effectId not in (SEE.EFFECT_TOON_DAMAGE_UP,):
        description = TTLocalizer.StatusEffectInactive + description

    return title, description


# Define custom effect backgrounds/icons here
def getBackgroundAndIconNames(statusEffect, effectId):
    if effectId in StatusEffectId2ImageProperties:
        info = StatusEffectId2ImageProperties[effectId]
    else:
        info = StatusEffectId2ImageProperties[SEE.EFFECT_BASE]
    background, icon, iconSuffix, bgSuffix, iconScale = info
    extraGeom = []

    if effectId == SEE.EFFECT_SUIT_LURED:
        index = 1 if statusEffect.getPrestige() else 0
        icon = icon[index]
    elif effectId == SEE.EFFECT_SCAPEGOAT_RAGE:
        index = 1 if statusEffect.getInRage() else 0
        icon = icon[index]
    elif effectId == SEE.EFFECT_SUIT_TRAPPED:
        level = int(statusEffect.getTrapLevel())
        # Grab the railroad icon from uber battle icons
        if level == BattleGlobals.UBER_GAG_LEVEL_INDEX:
            # Not used anymore, gui is placeholder
            gui = loader.loadModel('phase_3/models/etc/fade')
            icon = gui.find('**/fade')
            gui.removeNode()
        else:
            icon = base.localAvatar.inventory.invModels[AttackEnum.TOON_TRAP][level]
        iconScale = 5
    elif effectId == SEE.EFFECT_LURE_RESISTANCE:
        extraGeom = OnscreenText(parent=None, text='X', font=ToontownGlobals.getSignFont(), fg=(1, 0, 0, 0.75),
                                 scale=1.1, pos=(0.04, -0.375))
    elif effectId == SEE.EFFECT_TOON_DAMAGE_UP:
        gagTrack = int(statusEffect.getGagTrack())
        if gagTrack == -1:
            # Do nothing, the passed through icon is actually what we want here.
            pass
        else:
            # Grab the level 7 gag, they show best on the yellow panels.
            icon = base.localAvatar.inventory.invModels[gagTrack][6]
            iconScale = 5
    elif effectId == SEE.EFFECT_OVERCLOCKED_FOREMAN or effectId in FindTheFamilyGlobals.EffectIdToContainer:
        clubGui = loader.loadModel('phase_3.5/models/gui/clubs/club_backgrounds')
        if effectId == SEE.EFFECT_FTF_FOREMAN_EXPLOSIVE:
            # Do this so we can manipulate it
            extraGeom = clubGui.find('**/bg_24')
            extraGeom.setScale(0.94)
        else:
            icon = clubGui.find('**/bg_24')
            iconScale = 0.94
        clubGui.removeNode()
    elif effectId in (SEE.EFFECT_COGS_DAMAGE_DOWN, SEE.EFFECT_SUIT_DAMAGE_BOOST, SEE.EFFECT_SUIT_ADDITIVE_DAMAGE_BOOST):
        statusEffectImages = loader.loadModel('phase_3.5/models/gui/battlegui/status_effects')
        extraGeom = OnscreenImage(
            parent=None,
            image=statusEffectImages.find('**/' + icon[1] + '_icon')
        )
        statusEffectImages.removeNode()
        icon = icon[0]
    elif effectId == SEE.EFFECT_HYDRATED:
        icon = base.localAvatar.inventory.buttonLookup(4, 1)  # Glass of Water
        iconScale = 6
    elif effectId == SEE.EFFECT_OVERCHARGED:
        iconScale = 0.94
    elif effectId == SEE.EFFECT_RUSH_JOB:
        extraGeom = OnscreenImage(
            parent=None,
            image=base.localAvatar.inventory.invModels[int(statusEffect.getTrack())][6],
            scale = 4.4
        )
    elif effectId == SEE.EFFECT_MANAGER_PACESETTER:
        if statusEffect.isMaxed():
            icon = 'toofast4you'
    elif effectId in (SEE.EFFECT_DANCE_PARTNER, SEE.EFFECT_FTF_FOREMAN_CONTRACTOR_TANGO):
        effectIndex = statusEffect.getEffectIndex() % 4
        loadBase = 'activity/trolley/models/cc_m_mg_rin_'
        modelPath = {
            0: loadBase + 'ring_round',
            1: loadBase + 'ring_square',
            2: loadBase + 'ring_star',
            3: loadBase + 'ring_hex',
        }.get(effectIndex, None)
        if modelPath is not None:
            icon = loader.loadModel(modelPath)
            icon.setTransparency(1)
            icon.setH(90)
            icon.flattenMedium()
            icon.setTwoSided(0)
            icon.setColor(hexToPCol('222222'))
            iconScale = 0.26

            # Attach another icon underneath for funsies
            newIcon = render.attachNewNode('subIcon')
            newIcon = icon.copyTo(newIcon)
            newIcon.reparentTo(icon)
            newIcon.setScale(0.75)
    elif effectId in (SEE.EFFECT_STAR_OF_THE_SHOW, SEE.EFFECT_STAR_OF_THE_SHOW_TOON, SEE.EFFECT_HOLLYWOOD_STAR):
        gagSelectGui = base.loader.loadModel('phase_3.5/models/gui/battlegui/gag_selection_panels')
        prestigeStar = gagSelectGui.find('**/prestige_star')
        prestigeStar.setScale(0.8)
        extraGeom = [prestigeStar]
        if (effectId == SEE.EFFECT_STAR_OF_THE_SHOW and statusEffect.isSuperstar()) or effectId == SEE.EFFECT_HOLLYWOOD_STAR:
            prestigeStar.setColorScale(252/255, 206/255, 89/255, 1.0)
            starburst = loader.loadModel('phase_3.5/models/props/ttcc_gen_starburst')
            starburst.setColorScale(255/255, 255/255, 158/255, 2.0)
            starburst.setScale(0.235)
            extraGeom.insert(0, starburst)

        gagSelectGui.removeNode()
    elif effectId == SEE.EFFECT_LAST_TAP:
        iconScale = min(2.0, iconScale * (1.04 ** (statusEffect.multiplier - 5)))
    elif effectId in (SEE.EFFECT_POWER_NAP, SEE.EFFECT_PEACEFUL_SLUMBER, SEE.EFFECT_FTF_FOREMAN_SLEEPY_POWER_NAP):
        holderNode = NodePath('zzz-holder-node')
        iconImage = loader.loadModel('phase_8/models/props/zzz_treasure')
        iconImage.find("**/p1_2").clearBillboard()
        iconImage.reparentTo(holderNode)
        iconImage.setPos(0, 0, -0.7)
        iconScale = 0.25
        icon = holderNode
    elif effectId == SEE.EFFECT_FTF_NUCLEAR:
        socialPanelGui = loader.loadModel('phase_3.5/models/gui/socialpanel/social_panel_icons')
        icon = socialPanelGui.find('**/CIRCLE2')
        socialPanelGui.removeNode()
    elif effectId in (SEE.EFFECT_FTF_PRISMATIC_TOON, SEE.EFFECT_FTF_DUALCORE):
        clubGui = loader.loadModel('phase_3.5/models/gui/clubs/club_backgrounds')
        icon = clubGui.find(f'**/bg_{"47" if effectId == SEE.EFFECT_FTF_PRISMATIC_TOON else "44"}')
        if effectId == SEE.EFFECT_FTF_DUALCORE:
            icon.setR(180)
        clubGui.removeNode()
    elif effectId == SEE.EFFECT_PIP_DISCOUNT:
        discount = max(1, min(round(statusEffect.getDiscount()), 6))
        from ...gui.DiceButton import DiceButton
        dice = DiceButton.getDicePipIcon(discount)
        dice.setScale(0.64)
        extraGeom = [dice]
    elif effectId == SEE.EFFECT_PIP_COUNTER:
        clubGui = loader.loadModel('phase_3.5/models/gui/clubs/club_backgrounds')
        icon = clubGui.find(f'**/bg_29')
        icon.setColorScale(0.125, 0.125, 0.125, 1.0)
        clubGui.removeNode()
    elif effectId in [SEE.EFFECT_TRIVIA, SEE.EFFECT_PUZZLE, SEE.EFFECT_SHUFFLE]:
        funnyAnswers = ['A', 'B', 'C', 'D']
        funnyColors = [Vec4(0.0, 1.0, 0.0, 1.0),
                       Vec4(1.0, 0.0, 0.0, 1.0),
                       Vec4(0.0, 0.0, 1.0, 1.0),
                       Vec4(1.0, 1.0, 0.0, 1.0)]
        textNode = TextNode('highroller-question-letter-text')
        textNode.setFont(ToontownGlobals.getSignFont())
        textNode.setAlign(TextNode.ACenter)
        textNode.setTextColor(funnyColors[int(statusEffect.letterIndex - 1) % 4])
        textNode.setText(funnyAnswers[int(statusEffect.letterIndex - 1) % 4])
        textGeom = textNode.generate()
        textHolder = NodePath('highroller-question-text-holder')
        textHolder.attachNewNode(textGeom)
        textHolder.setPos(0.0, 0.0, -0.34)
        icon = NodePath('highroller-question-letter-node')
        textHolder.reparentTo(icon)
        iconScale = 0.8
    elif effectId == SEE.EFFECT_HIGHROLLER_CLONE:
        from toontown.instances import HighRollerGlobals
        icon = HighRollerGlobals.CloneType2Visuals.get(statusEffect.getType())[2]
        iconScale = HighRollerGlobals.CloneType2Visuals.get(statusEffect.getType())[3]
    elif effectId == SEE.EFFECT_MANAGER_GATEKEEPER and base.localAvatar.getStatusEffectOfId(SEE.EFFECT_GATEKEEPER_TOON_PIERCE):
        icon = 'broken_shield'
        iconScale = 0.85

    if statusEffect.isDisabled():
        for geom in extraGeom:
            geom.setColorScale(0.5, 0.5, 0.5, 1.0)

    return background, icon, iconScale, extraGeom, iconSuffix, bgSuffix


# Define custom icon colors here
def getCustomBackgroundColor(statusEffect, effectId, bgNode, extraGeom):
    # Default colors here.
    retColor = BuffToCol.get(
        StatusEffectId2Type[effectId],
        BuffToCol[NEUTRAL]
    )

    # Some status effects may have a custom sequence for its color
    colorSequence = None

    def setImageColor(value, startColor=(1, 1, 1, 1), endColor=(1, 1, 1, 1)):
        newColor = (startColor * (1 - value)) + (endColor * value)
        bgNode['image_color'] = newColor

    def setExtraGeomColor(value, index, startColor=(1, 1, 1, 1), endColor=(1, 1, 1, 1)):
        geomPiece = extraGeom[index]
        newColor = (startColor * (1 - value)) + (endColor * value)
        geomPiece.setColorScale(newColor)

    # Custom colors here.
    if effectId == SEE.EFFECT_OVERCLOCKED_FOREMAN:
        colorDict = {
            # Bellow - Violet
            0: Vec4(0.322, 0.086, 0.753, 1.0),
            # Antergy - Orange
            1: Vec4(0.925, 0.635, 0.2, 1.0),
            # Steadfast - Green
            2: Vec4(0.294, 0.918, 0.208, 1.0),
            # Compensation - Cyan
            3: Vec4(0.271, 0.886, 0.859, 1.0),
            # Destruction - Black
            4: Vec4(0.114, 0.02, 0.02, 1.0),
            # Prethinking - Pink
            5: Vec4(0.871, 0.384, 0.91, 1.0),
            # Rebalance - Yellow
            6: Vec4(0.929, 0.945, 0.212, 1.0),
            # Sacrifice - Red
            7: Vec4(0.792, 0.051, 0.051, 1.0),
            # Prismatic - White (Actually rainbow, look below like 5 lines)
            8: Vec4(1, 1, 1, 1),
        }
        retColor = colorDict.get(statusEffect.getType())
        # Prismatic foreman has a rainbow background effect
        if statusEffect.getType() == 8:
            rainbowColorOrder = [7, 1, 6, 2, 3, 4, 0, 5]
            colorSequence = Sequence()
            for i, color in enumerate(rainbowColorOrder):
                lastColor = len(rainbowColorOrder) - 1 if i == 0 else i - 1
                colorSequence.append(LerpFunctionInterval(setImageColor, 0.9, extraArgs=[colorDict[lastColor], colorDict[i]]))

    # Pulsing purple effect for overcharged
    elif effectId == SEE.EFFECT_OVERCHARGED:
        retColor = Vec4(99/255, 23/255, 207/255, 1.0)
        highlightColor = Vec4(186/255, 124/255, 255/255, 1.0)
        colorSequence = Sequence(
            LerpFunctionInterval(setImageColor, 1.5, extraArgs=[retColor, highlightColor], blendType='easeIn'),
            LerpFunctionInterval(setImageColor, 1.5, extraArgs=[highlightColor, retColor], blendType='easeOut')
        )
    # Pulsing purple for prethinker (forward thinking)
    elif effectId == SEE.EFFECT_MANAGER_PRETHINKER:
        retColor = Vec4(119/255, 43/255, 255/255, 1.0)
        highlightColor = Vec4(169/255, 93/255, 255/255, 1.0)
        colorSequence = Sequence(
            LerpFunctionInterval(setImageColor, 1.5, extraArgs=[retColor, highlightColor], blendType='easeInOut'),
            LerpFunctionInterval(setImageColor, 1.5, extraArgs=[highlightColor, retColor], blendType='easeInOut')
        )

    # Pulsing orange
    elif effectId == SEE.EFFECT_DISRUPTIVE_ADVERTISEMENT:
        retColor = BuffToCol[BUFF]
        highlightColor = Vec4(1.0, 0.5, 0.0, 1.0)
        colorSequence = Sequence(
            Func(setImageColor, 1.0, retColor, highlightColor),
            LerpFunctionInterval(setImageColor, 0.6, extraArgs=[highlightColor, retColor], blendType='easeIn'),
            Wait(0.7),
        )

    # Neutral
    elif effectId in (SEE.EFFECT_SKELECOG, SEE.EFFECT_MANAGER_PACESETTER, SEE.EFFECT_MINIBOSS, SEE.EFFECT_HIGHROLLER_MINIGAME_HOST):
        retColor = BuffToCol[NEUTRAL]

    # Also neutral but special thing
    elif effectId == SEE.EFFECT_MANAGER_GATEKEEPER and base.localAvatar.getStatusEffectOfId(SEE.EFFECT_GATEKEEPER_TOON_PIERCE):
        retColor = BuffToCol[NEUTRAL]

    # Also also neutral but special lure thing
    elif effectId == SEE.EFFECT_LURE_RESISTANCE and statusEffect.getAmount() == -1:
        retColor = BuffToCol[BUFF]
        highlightColor = Vec4(1.0, 0.3, 0.3, 1.0)
        colorSequence = Sequence(
            LerpFunctionInterval(setImageColor, 0.7, extraArgs=[retColor, highlightColor], blendType='easeIn'),
            LerpFunctionInterval(setImageColor, 0.7, extraArgs=[highlightColor, retColor], blendType='easeOut')
        )

    # Dark Blue like around the cog borderf
    elif effectId in (SEE.EFFECT_VIRTUAL_COG,):
        retColor = Vec4(0.251, 0.259, 0.318, 1.0)

    elif effectId == SEE.EFFECT_SUIT_DRENCHED:
        retColor = Vec4(19*2.0/255, 31*2.0/255, 66*2.0/255, 1)

    # Pulsing orange
    elif effectId in (SEE.EFFECT_HIVEMIND, SEE.EFFECT_UNION_BUST):
        retColor = BuffToCol[BUFF]
        highlightColor = Vec4(1.0, 0.5, 0.0, 1.0)
        colorSequence = Sequence(
            Func(setImageColor, 1.0, retColor, highlightColor),
            LerpFunctionInterval(setImageColor, 0.6, extraArgs=[highlightColor, retColor], blendType='easeIn'),
            Wait(0.7),
        )

    elif effectId == SEE.EFFECT_MANAGER_PLUTOCRAT:
        if statusEffect.marketBubbleStacks > 0:
            retColor = Vec4(85/255, 138/255, 104/255, 1)
        elif statusEffect.marketBubbleStacks == -1:
            retColor = BuffToCol[NEUTRAL]
            highlightColor = Vec4(1.0, 0.7, 0.3, 1.0)
            colorSequence = Sequence(
                LerpFunctionInterval(setImageColor, 0.7, extraArgs=[retColor, highlightColor], blendType='easeIn'),
                LerpFunctionInterval(setImageColor, 0.7, extraArgs=[highlightColor, retColor], blendType='easeOut')
            )
        else:
            retColor = BuffToCol[NEUTRAL]

    elif effectId == SEE.EFFECT_SLUSH_FUND:
        retColor = Vec4(40/255, 127/255, 133/255, 1)

    elif effectId == SEE.EFFECT_HURRY_SICKNESS:
        retColor = Vec4(186/255, 124/255, 255/255, 1.0)

    elif effectId == SEE.EFFECT_RUSH_JOB:
        retColor = Vec4(*BattleGlobals.TrackColors[int(statusEffect.getTrack())], 1)

    elif effectId in (SEE.EFFECT_POWER_NAP, SEE.EFFECT_FTF_FOREMAN_SLEEPY_POWER_NAP):
        retColor = Vec4(119/255, 43/255, 255/255, 1.0)

    elif effectId == SEE.EFFECT_PEACEFUL_SLUMBER:
        retColor = Vec4(247/255, 54/255, 90/255, 1.0)

    elif effectId in (SEE.EFFECT_DANCE_PARTNER, SEE.EFFECT_FTF_FOREMAN_CONTRACTOR_TANGO):
        effectIndex = statusEffect.getEffectIndex() % 4
        retColor = {
            0: Vec4(*hexToPCol('579FFF')),
            1: Vec4(*hexToPCol('47FF4C')),
            2: Vec4(*hexToPCol('FF9242')),
            3: Vec4(*hexToPCol('A133FF')),
        }.get(effectIndex, BuffToCol[NEUTRAL])

        # If we are tied to this effect, give it a highlight.
        if statusEffect.doesAvIdMatch(avId=base.localAvatar.doId, includeSelf=True):
            highlightColor = Vec4(*hexToPCol('ffffff'))
            colorSequence = Sequence(
                LerpFunctionInterval(setImageColor, 1.5, extraArgs=[retColor, highlightColor], blendType='easeIn'),
                LerpFunctionInterval(setImageColor, 1.5, extraArgs=[highlightColor, retColor], blendType='easeOut')
            )
    elif (effectId == SEE.EFFECT_STAR_OF_THE_SHOW and statusEffect.isSuperstar()) or effectId == SEE.EFFECT_HOLLYWOOD_STAR:
        colorSequence = Sequence(
            LerpHprInterval(extraGeom[0], 5.0, hpr=(0, 0, 360), startHpr=(0, 0, 0))
        )
    elif effectId == SEE.EFFECT_LAST_TAP:
        bgNode.setBin('sorted-gui-popup', GuiBinGlobals.BattleInfoTooltipExtended + 1)
    elif effectId in FindTheFamilyGlobals.EffectIdToContainer:
        retColor = FindTheFamilyGlobals.EffectIdToContainer[effectId].color
        if effectId == SEE.EFFECT_FTF_FOREMAN_EXPLOSIVE:
            seqColor = Vec4(1.0, 0.75, 0.0, 1.0)
            highlightColor = Vec4(1.0, 0.35, 0.0, 1.0)
            colorSequence = Sequence(
                Func(setExtraGeomColor, 1.0, 0, seqColor, highlightColor),
                LerpFunctionInterval(setExtraGeomColor, 0.6, extraArgs=[0, highlightColor, seqColor], blendType='easeIn'),
                Wait(0.7),
            )
    elif effectId == SEE.EFFECT_FTF_NUCLEAR:
        retColor = Vec4(*hexToPCol('6e918c'))
        highlightColor = Vec4(*hexToPCol('ff9a5d'))
        colorSequence = Sequence(
            LerpFunctionInterval(setImageColor, 1.5, extraArgs=[retColor, highlightColor], blendType='easeIn'),
            LerpFunctionInterval(setImageColor, 1.5, extraArgs=[highlightColor, retColor], blendType='easeOut')
        )
    elif effectId in (SEE.EFFECT_FTF_PRISMATIC_TOON, SEE.EFFECT_FTF_DUALCORE):
        retColor = (1, 1, 1, 1)
        retColorDict = {
            0: Vec4(*hexToPCol('579FFF')),
            1: Vec4(*hexToPCol('47FF4C')),
            2: Vec4(*hexToPCol('FF9242')),
            3: Vec4(*hexToPCol('A133FF')),
        }
        colorSequence = Sequence()
        for i in retColorDict:
            lastColor = len(retColorDict) - 1 if i == 0 else i - 1
            colorSequence.append(
                LerpFunctionInterval(setImageColor, 0.9, extraArgs=[retColorDict[lastColor], retColorDict[i]]))

    elif effectId == SEE.EFFECT_HARMONIOUS_COLORS:
        if statusEffect.getAv().getStatusEffectOfId(SEE.EFFECT_HR_UNTOUCHABLE):
            from toontown.instances import HighRollerGlobals
            colorDict = HighRollerGlobals.CloneType2Visuals
            rainbowColorOrder = [i for i in range(len(colorDict.keys()))]
            colorSequence = Sequence()
            for i, color in enumerate(rainbowColorOrder):
                lastColor = len(rainbowColorOrder) - 1 if i == 0 else i - 1
                colorSequence.append(LerpFunctionInterval(setImageColor, 0.9, extraArgs=[colorDict[lastColor][0], colorDict[i][0]]))
        else:
            retColor = BuffToCol[NEUTRAL]
    elif effectId == SEE.EFFECT_PIP_COUNTER:
        retColor = Vec4(0.859, 0.643, 0.165, 1.0)
    elif effectId == SEE.EFFECT_HIGHROLLER_CLONE:
        from toontown.instances import HighRollerGlobals
        cloneColor = HighRollerGlobals.CloneType2Visuals.get(statusEffect.getType())[0]
        colorList = []
        for i in range(3):
            colorList.append((cloneColor[i] + 0.95) / 2)
        colorList.append(1.0)
        retColor = Vec4(*colorList)
    elif effectId == SEE.EFFECT_RED_THREAD:
        retColor = Vec4(1, 0.5, 0, 1.0)

    # Return the color.
    return retColor, colorSequence


# Define custom round values here
def getRoundsValue(statusEffect, effectId):
    rounds = statusEffect.getRounds()

    if effectId == SEE.EFFECT_SCAPEGOAT_RAGE and statusEffect.getInRage():
        rounds = int(statusEffect.getInRage())
    elif effectId in [SEE.EFFECT_TRIVIA, SEE.EFFECT_PUZZLE, SEE.EFFECT_SHUFFLE]:
        rounds = -1

    return rounds


# Grabs the correct status effect class based on id
def createStatusEffect(avProfile, effectId, extraArgs=None):
    statusEffect = StatusEffectAttributes.get(effectId)
    if not statusEffect:
        statusEffect = StatusEffectAttributes.get(SEE.EFFECT_BASE)

    effectClass = statusEffect['class']
    # Deepcopy these to prevent accidental modification of module/class variables that get passed through.
    rounds = deepcopy(statusEffect['rounds'])
    disabledRounds = deepcopy(statusEffect['disabledRounds'])
    if not extraArgs:
        extraArgs = statusEffect.get('extraArgs', [])
    extraArgs = list(deepcopy(extraArgs))

    newEffect = effectClass(avProfile, effectId, rounds, disabledRounds, extraArgs)

    return newEffect
