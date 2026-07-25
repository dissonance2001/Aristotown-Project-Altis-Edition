from toontown.battle import MovieCamera
from toontown.battle.attacks.suits import MovieLawbotLitigationCheats
from toontown.battle.attacks.suits import MovieBossbotLitigationCheats
from toontown.battle.attacks.suits import MovieBoardbotLitigationCheats
from toontown.battle.attacks.suits import MovieSellbotLitigationCheats
from toontown.battle.attacks.suits import MovieCashbotLitigationCheats
from toontown.battle.attacks.suits import MovieHighRollerCheats
from toontown.battle.attacks.suits import MovieDirectorsCheats
from toontown.battle.attacks.suits import MovieUniversalCheats
from toontown.battle.attacks.suits import MovieFaceTheFamilyCheats
from toontown.battle.attacks.suits import MovieCountCheats
from toontown.battle.attacks.suits import MovieIntervals
from toontown.battle import MovieUtil
from toontown.battle import BattleParticles
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from toontown.effects import DustCloud
from direct.particles import ParticleEffect
from toontown.battle.BattleBase import *
from toontown.battle.BattleBase import *
from direct.showutil import Effects
from toontown.battle.BattleProps import *
from otp.otpbase import OTPLocalizerEnglish
from toontown.battle.BattleSounds import *
from toontown.battle.SuitBattleGlobals import *
from toontown.chat.ChatGlobals import *
from toontown.toonbase import ToontownBattleGlobals
from toontown.battle import BattleProps
from toontown.suit import Suit
from toontown.nametag import NametagGlobals
from toontown.nametag.NametagGlobals import *
from toontown.suit.SuitDNA import *
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from toontown.toonbase.ToontownGlobals import *

notify = DirectNotifyGlobal.directNotify.newCategory('MovieSuitAttacks')

def throwPos(t, object, duration, target, values, gravity = -32.144):
    origin = values['origin']
    velocity = values['velocity']
    if callable(target):
        target = target()
    x = origin[0] * (1 - t) + target[0] * t
    y = origin[1] * (1 - t) + target[1] * t
    time = t * duration
    z = origin[2] + velocity * time + 0.5 * gravity * time * time
    object.setPos(x, y, z)

def __doDamage(toon, dmg, died):
    return MovieIntervals.__doDamage(toon, dmg, died)

def __doDamageCheat(toon, dmg, died):
    return MovieIntervals.__doDamageCheat(toon, dmg, died)

def __showProp(prop, parent, pos, hpr = None, scale = None):
    return MovieIntervals.__showProp(prop, parent, pos, hpr, scale)

def __animProp(prop, propName, propType = 'actor'):
    return MovieIntervals.__animProp(prop, propName, propType)

def __suitFacePoint(suit, zOffset = 0):
    return MovieIntervals.__suitFacePoint(suit, zOffset)

def __toonFacePoint(toon, zOffset = 0, parent = render):
    return MovieIntervals.__toonFacePoint(toon, zOffset, parent)

def __toonTorsoPoint(toon, zOffset = 0):
    return MovieIntervals.__toonTorsoPoint(toon, zOffset)

def __toonGroundPoint(attack, toon, zOffset = 0, parent = render):
    return MovieIntervals.__toonGroundPoint(attack, toon, zOffset, parent)

def __toonGroundMissPoint(attack, prop, toon, zOffset = 0):
    return MovieIntervals.__toonGroundMissPoint(attack, prop, toon, zOffset)

def __toonMissPoint(prop, toon, yOffset = 0, parent = None):
    return MovieIntervals.__toonMissPoint(prop, toon, yOffset, parent)

def __toonMissBehindPoint(toon, parent = render, offset = 0):
    return MovieIntervals.__toonMissBehindPoint(toon, parent, offset)

def __throwBounceHitPoint(prop, toon):
    return MovieIntervals.__throwBounceHitPoint(prop, toon)

def __throwBounceMissPoint(prop, toon):
    return MovieIntervals.__throwBounceMissPoint(prop, toon)

def __throwBouncePoint(startPoint, endPoint):
    return MovieIntervals.__throwBouncePoint(startPoint, endPoint)

def getResetTrack(suit, battle):
    return MovieIntervals.getResetTrack(suit, battle)

def __makeCancelledNodePath():
    tn = TextNode('CANCELLED')
    tn.setFont(getSuitFont())
    tn.setText(TTLocalizer.MovieSuitCancelled)
    tn.setAlign(TextNode.ACenter)
    tntop = hidden.attachNewNode('CancelledTop')
    tnpath = tntop.attachNewNode(tn)
    tnpath.setPosHpr(0, 0, 0, 90, 0, 0)
    tnpath.setScale(1)
    tnpath.setColor(0.7, 0, 0, 1)
    tnpathback = tnpath.instanceUnderNode(tntop, 'backside')
    tnpathback.setPosHpr(0, 0, 0, 180, 0, 0)
    tnpath.setScale(1)
    return tntop

def doDefault(attack):
    notify.debug('building suit attack in doDefault')
    suitName = attack['suitName']
    attack['name'] = 'SoakRemoval'
    attack['animName'] = 'nothing'
    return MovieUniversalCheats.SoakRemoval(attack)

def __createSuitResetPosTrack(suit, battle):
    return MovieIntervals.__createSuitResetPosTrack(suit, battle)


def getSuitTrack(attack, delay = 1e-06, splicedAnims = None, playRate = 1.0):
    groupStatus = attack['group']
    if groupStatus == ATK_TGT_GROUP:
        return MovieIntervals.getSuitAnimTrackAttack(attack, delay, splicedAnims, playRate)
    else:
        return MovieIntervals.getSuitTrack(attack, delay, splicedAnims, playRate)


def getSuitAnimTrack(attack, delay = 0, splicedAnims = None, playRate = 1.0):
    groupStatus = attack['group']
    if groupStatus == ATK_TGT_SINGLE:
            return MovieIntervals.getSuitTrack(attack, delay, splicedAnims, playRate)
    else:
        return MovieIntervals.getSuitAnimTrackAttack(attack, delay, splicedAnims, playRate)


def getPartTrack(particleEffect, startDelay, durationDelay, partExtraArgs, softStop = 0):
    return MovieIntervals.getPartTrack(particleEffect, startDelay, durationDelay, partExtraArgs, softStop)


def getPartTracks(attack, particleEffects, startDelay, durationDelay, worldRelative = 1, softStop = 0):
    return MovieIntervals.getPartTracks(attack, particleEffects, startDelay, durationDelay, worldRelative, softStop)


def getToonTrack(attack, damageDelay = 1e-06, damageAnimNames = None, dodgeDelay = 0.0001, dodgeAnimNames = None, splicedDamageAnims = None, splicedDodgeAnims = None, target = None, showDamageExtraTime = 0.01, showMissedExtraTime = 0.5):
    return MovieIntervals.getToonTrack(attack, damageDelay, damageAnimNames, dodgeDelay, dodgeAnimNames, splicedDamageAnims, splicedDodgeAnims, target, showDamageExtraTime, showMissedExtraTime)


def getToonTracks(attack, damageDelay = 1e-06, damageAnimNames = None, dodgeDelay = 1e-06, dodgeAnimNames = None, splicedDamageAnims = None, splicedDodgeAnims = None, showDamageExtraTime = 0.01, showMissedExtraTime = 0.5):
    return MovieIntervals.getToonTracks(attack, damageDelay, damageAnimNames, dodgeDelay, dodgeAnimNames, splicedDamageAnims, splicedDodgeAnims, showDamageExtraTime, showMissedExtraTime)


def getToonDodgeTrack(target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime):
    return MovieIntervals.getToonDodgeTrack(target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime)


def getAllyToonsDodgeParallel(target):
    return MovieIntervals.getAllyToonsDodgeParallel(target)

def getPropTrack(prop, parent, posPoints, appearDelay, remainDelay, scaleUpPoint = Point3(1), scaleUpTime = 0.5, scaleDownTime = 0.5, startScale = Point3(0.01), anim = 0, propName = 'none', animDuration = 0.0, animStartTime = 0.0):
    return MovieIntervals.getPropTrack(prop, parent, posPoints, appearDelay, remainDelay, scaleUpPoint, scaleUpTime, scaleDownTime, startScale, anim, propName, animDuration, animStartTime)

def getPropAppearTrack(prop, parent, posPoints, appearDelay, scaleUpPoint = Point3(1), scaleUpTime = 0.5, startScale = Point3(0.01), poseExtraArgs = None, blendType='noBlend'):
    return MovieIntervals.getPropAppearTrack(prop, parent, posPoints, appearDelay, scaleUpPoint, scaleUpTime, startScale, poseExtraArgs, blendType)

def getPropThrowTrack(attack, prop, hitPoints = [], missPoints = [], hitDuration = 0.25, missDuration = 0.25, hitPointNames = 'none', missPointNames = 'none', lookAt = 'none', groundPointOffSet = 0, missScaleDown = None, parent = render, target = None):
    return MovieIntervals.getPropThrowTrack(attack, prop, hitPoints, missPoints, hitDuration, missDuration, hitPointNames, missPointNames, lookAt, groundPointOffSet, missScaleDown, parent, target)

def getThrowTrack(object, target, duration = 1.0, parent = render, gravity = -32.144):
    return MovieIntervals.getThrowTrack(object, target, duration, parent, gravity)

def getToonTakeDamageTrack(attack, toon, died, dmg, delay, damageAnimNames = None, splicedDamageAnims = None, showDamageExtraTime = 0.01):
    return MovieIntervals.getToonTakeDamageTrack(attack, toon, died, dmg, delay, damageAnimNames, splicedDamageAnims, showDamageExtraTime)

def getToonTakeDamageTrackCheat(attack, toon, died, dmg, delay, damageAnimNames = None, splicedDamageAnims = None, showDamageExtraTime = 0.01):
    return MovieIntervals.getToonTakeDamageTrackCheat(attack, toon, died, dmg, delay, damageAnimNames, splicedDamageAnims, showDamageExtraTime)

def getSplicedAnimsTrack(anims, actor = None):
    return MovieIntervals.getSplicedAnimsTrack(anims, actor)

def getSplicedLerpAnims(animName, origDuration, newDuration, startTime = 0, fps = 30, reverse = 0):
    return MovieIntervals.getSplicedLerpAnims(animName, origDuration, newDuration, startTime, fps, reverse)

def getSoundTrack(fileName, delay = 0.01, duration = 0.0, node = None):
    return Sequence(Wait(delay), SoundInterval(globalBattleSoundCache.getSound(fileName), duration=duration, node=node))

def getToonTrackCheat(attack, damageDelay = 1e-06, damageAnimNames = None, dodgeDelay = 0.0001, dodgeAnimNames = None, splicedDamageAnims = None, splicedDodgeAnims = None, target = None, showDamageExtraTime = 0.01, showMissedExtraTime = 0.5):
    return MovieIntervals.getToonTrackCheat(attack, damageDelay, damageAnimNames, dodgeDelay, dodgeAnimNames, splicedDamageAnims, splicedDodgeAnims, target, showDamageExtraTime, showMissedExtraTime)

def getToonTrackCheat2(attack, damageDelay = 1e-06, damageAnimNames = None, dodgeDelay = 0.0001, dodgeAnimNames = None, splicedDamageAnims = None, splicedDodgeAnims = None, target = None, showDamageExtraTime = 0.01, showMissedExtraTime = 0.5):
    return MovieIntervals.getToonTrackCheat2(attack, damageDelay, damageAnimNames, dodgeDelay, dodgeAnimNames, splicedDamageAnims, splicedDodgeAnims, target, showDamageExtraTime, showMissedExtraTime)


def getToonDodgeTrackCheat(target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime):
    return MovieIntervals.getToonDodgeTrackCheat(target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime)


def getToonTracksCheat(attack, damageDelay = 1e-06, damageAnimNames = None, dodgeDelay = 1e-06, dodgeAnimNames = None, splicedDamageAnims = None, splicedDodgeAnims = None, showDamageExtraTime = 0.01, showMissedExtraTime = 0.5):
    return MovieIntervals.getToonTracksCheat(attack, damageDelay, damageAnimNames, dodgeDelay, dodgeAnimNames, splicedDamageAnims, splicedDodgeAnims, showDamageExtraTime, showMissedExtraTime)

suitTrackResetNames = [
]

suitTrack2ResetNames = [
    'ScapegoatCourtRecordBan',
    'ScapegoatRageBuilding',
    'PowerhouseToleranceBuilding',
    'CaseManagerCourtRecordBan',
    'StenographerCourtRecordBan',
    'CaseManagerLegallyBound',
    'CaseManagerInsurance',
    'CaseManagerInsurance2',
    'RadiographerDanceSession',
    'RecordkeeperPhantomEntrySpawn',
    'RecordkeeperPhantomEntryDamage',
        'WiretapperCollectCall2',
    'CalculatingFees',
    'TollmasterMandatoryToll',
    'TollmasterResonanceTax',
    'TollmasterResonanceTax2',
    'TollmasterResonanceTax3',
    'TollmasterResonanceTax4',
    'RacketeerOverextendedLeverage',
    'TollmasterResonanceTax5',
    'ButcherRevvingUp',
    'ButcherRevvingUpWhipsaw',
    'WiretapperCollectCall',
    'Desperation',
    'Desperation2',
    'PresidentSensational',
    'PresidentViralSensation',
    'LureRemoval',
    'LureRemovalPreToon',
    'LureRemovalHeal',
    'LureRemovalTrap',
    'LureRemovalLure',
    'LureRemovalSound',
    'LureRemovalThrow',
    'LureRemovalSquirt',
    'LureRemovalZap',
    'LureRemovalDrop',
    'ScapegoatBarnyardBash',
    'DeathCheck',
    'CogSpawn',
    'SoakRemoval',
    'DrenchDecrement',
    'OilRemoval',
    'SyphonMovie',
    'HighRollerSingingBlues',
    'MintFraudulentDamage',
    'DividendTotalMarketMeltdownDamage',
    'PresidentTargetCheck',
    'PresidentPuzzling',
    'HighRollerPhase3',
    'GagBanRetaliationHeal',
    'GagBanRetaliationTrap',
    'GagBanRetaliationLure',
    'GagBanRetaliationThrow', # CHANGE DEPENDING ON MANAGER!!!!
    'GagBanRetaliationSquirt',
    'GagBanRetaliationZap',
    'GagBanRetaliationSound',
    'GagBanRetaliationDrop',
    'MarkRemoval',
    'SueApplication',
    'SueRemoval',
    'SueDamage',
    'RacketeerHustling',
    'ZapMovie',
    'AbilityQueued',
    'HighRollerSplashback',
    'HighRollerCheerRetaliation',
    'ErfitPhase2',
    'ErclaimHemmorageHealing',
    'ErclaimHemmorage',
    'UnstableTransformation',
    'DirectorBudgetExpansion',
    'UnionBusterUnionBusterDamage',
    'DividendZapRetaliation',
    'AmbassadorMulligan',
    'ArbitratorObjection',
    'AbsorbMovie',
    'TargetCheck',
    'AbsorbMovieLevel',
    'HighRollerLureResistance',
    'HighRollerLureResistance2',
    'ErclaimScopeCreep',
    'AbilityQueuedPreToon',
    'AbsorbMovieLure',
    'AbsorbMovieThrow',
    'AbsorbMovieSquirt',
    'HustlerLimitedTimeOfferApprove',
    'AbsorbMovieZap',
    'AbsorbMovieSound',
    'AbsorbMovieDrop',
    'AbsorbMovieLevelLure',
    'AbsorbMovieLevelThrow',
    'AbsorbMovieLevelSquirt',
    'HustlerLimitedTimeOfferDenied',
    'AbsorbMovieLevelZap',
    'ErfitHydrationCheckRevert',
    'AbsorbMovieLevelSound',
    'AbsorbMovieLevelDrop',
    'ButcherSparkPlugDamage',
    'RecordkeeperMinutesTaken',
    'DividendLiquidationEventDamage',
    'RecordkeeperRedlinedClauseMissedPayment',
    'RecordkeeperMinutesTakenDamage',
    'RecordkeeperMinutesTakenContingency',
    'ContingencyRiskThresholdBreach',
    'ButcherMarkedWood',
    'ForemanUnionized',
    'ButcherOffboarding',
    'ButcherOffboarding2',
    'ButcherOffboarding3',
    'UnionBusterContractEnforcementHealing',
    'ButcherOffboarding5',
    'MintUsury',
    'ButcherAggrandize',
    'ForemanContributing',
    'ButcherAggrandize2',
    'HighStakesHeal',
    'HighStakesTrap',
    'HighStakesLure',
    'HighStakesSound',
    'HighStakesThrow',
    'HighStakesSquirt',
    'HighStakesZap',
    'HighStakesDrop',
    'ButcherAggrandize3',
    'ButcherAggrandize4',
    'ButcherAggrandize5',
    'ButcherSparkPlug',
    'ButcherScabbard',
    'ForemanContractorDeath',
    'ButcherLayoffs',
    'PowerhouseAbsorb',
    'SafetyHeatWaveCalculation',
    'SafetyViolation',
    'UnionBusterUnionCalculator',
    'ForemanBurningDamage',
    'ForemanSleepyOvercharge',
    'ForemanExplosion',
    'ForemanContractor',
    'MintPolicyTerminated',
    'MintAbacusAbove15',
    'MintAbacusBelow15',
    'MintAccountant1',
    'MintAccountant2',
    'MintAccountant3',
    'MintApprove',
    'MintDisapprove',
    'MintAccountant4',
    'MintAccountant5',
    'WiretapperGagBan',
    'WiretapperBusySignal',
    'PowerhouseSnipeVulnerable',
    'KnockbackThrow',
    'KnockbackSquirt',
    'ComboThrow',
    'ComboSquirt',
    'ComboDrop',
    'PowerhouseGroundbreakerRevert',
    'PowerhouseSnipeGagBan',
    'RadiographerHotTakeDamage',
    'PowerhouseSnipeBookkept',
    'PowerhouseSnipeMulligan',
    'PowerhouseBurnDamage',
]

def doSuitAttack(attack):
    notify.debug('building suit attack in doSuitAttack: %s' % attack['name'])
    name = attack['name']
    suit = attack['suit']
    if name == 'AcidRain':
        suitTrack = doAcidRain(attack)
    elif name == 'Aftershock':
        suitTrack = doQuake(attack)
    elif name == 'Audit':
        suitTrack = doAudit(attack)
    elif name == 'Bash':
        suitTrack = doBash(attack)
    elif name == 'Beguile':
        suitTrack = doBeguile(attack)
    elif name == 'CloseTheLoop':
        suitTrack = doCloseTheLoop(attack)
    elif name == 'HostileTakeover':
        suitTrack = doHostileTakeoverNew(attack)
    elif name == 'NickelAndDime':
        suitTrack = doNickelAndDime(attack)
    elif name == 'Quash':
        suitTrack = doQuash(attack)
    elif name == 'PennyPinch':
        suitTrack = doPennyPinch(attack)
    elif name == 'Disassemble':
        suitTrack = doDisassemble(attack)
    elif name == 'DataCorruption':
        suitTrack = doDataCorruption(attack)
    elif name == 'DataBreach':
        suitTrack = doDataBreach(attack)
    elif name == 'VersionControl':
        suitTrack = doVersionControl(attack)
    elif name == 'DenialOfService':
        suitTrack = doDenialOfService(attack)
    elif name == 'Overload':
        suitTrack = doOverload(attack)
    elif name == 'Breakthrough':
        suitTrack = doBreakthrough(attack)
    elif name == 'Encrypt':
        suitTrack = doEncrypt(attack)
    elif name == 'BounceRate':
        suitTrack = doBounceCheck(attack)
    elif name == 'Reprogram':
        suitTrack = doReprogram(attack)
    elif name == 'CloudStorage':
        suitTrack = doCloudStorage(attack)
    elif name == 'DoubleCross':
        suitTrack = doDoubleCross(attack)
    elif name == 'Forecast':
        suitTrack = doBrainStorm(attack)
    elif name == 'GoldDust':
        suitTrack = doGoldDust(attack)
    elif name == 'GoldRush':
        suitTrack = doGoldRush(attack)
    elif name == 'DiskScratch':
        suitTrack = doDiskScratch(attack)
    elif name == 'MysteriousDisappearance':
        suitTrack = doMysteriousDisappearance(attack)
    elif name == 'VoodooMagic':
        suitTrack = doVoodooMagic(attack)
    elif name == 'ElectrostaticEnergy':
        suitTrack = doElectrostaticEnergy(attack)
    elif name == 'Bite':
        if suit.isAngry:
            suitTrack = Sequence(ActorInterval(suit, 'neutral-enraged-return'), doBite(attack))
        else:
            suitTrack = doBite(attack)
    elif name == 'BounceCheck':
        suitTrack = doBounceCheck(attack)
    elif name == 'BrainStorm':
        suitTrack = doBrainStorm(attack)
    elif name == 'BuzzWord':
        suitTrack = doBuzzWord(attack)
    elif name == 'Calculate':
        suitTrack = doCalculate(attack)
    elif name == 'Canned':
        suitTrack = doCanned(attack)
    elif name == 'EvictionNotice':
        suitTrack = doEvictionNotice(attack)
    elif name == 'Chomp':
        suitTrack = doChomp(attack)
    elif name == 'Watercooler':
        suitTrack = doWatercooler(attack)
    elif name == 'CigarSmoke':
        suitTrack = doCigarSmoke(attack)
    elif name == 'SmokeAndMirrors':
        suitTrack = doCigarSmoke(attack)
    elif name == 'StolenScene':
            suitTrack = doStolenScene(attack)
    elif name == 'ClipOnTie':
        suitTrack = doClipOnTie(attack)
    elif name == 'Crunch':
        suitTrack = doCrunch(attack)
    elif name == 'Demotion':
        suitTrack = doDemotion(attack)
    elif name == 'DoubleTalk':
        suitTrack = doDoubleTalk(attack)
    elif name == 'Downsize':
        suitTrack = doDownsize(attack)
    elif name == 'EvictionNotice':
        suitTrack = doEvictionNotice(attack)
    elif name == 'EvilEye':
        suitTrack = doEvilEye(attack)
    elif name == 'FiveOClockShadow':
        suitTrack = doFiveOClockShadow(attack)
    elif name == 'SandTrap':
        suitTrack = doSandTrap(attack)
    elif name == 'Filibuster':
        suitTrack = doFilibuster(attack)
    elif name == 'FillWithLead':
        suitTrack = doFillWithLead(attack)
    elif name == 'FingerWag':
        if suit.isAngry:
            suitTrack = Sequence(ActorInterval(suit, 'neutral-enraged-return'), doFingerWag(attack))
        else:
            suitTrack = doFingerWag(attack)
    elif name == 'Fired':
        if suit.dna.name == 'safesupervis':
            suitTrack = doFiredPressurizer(attack)
        else:
            suitTrack = doFired(attack)
    elif name == 'FountainPen':
        suitTrack = doFountainPen(attack)
    elif name == 'FreezeAssets':
        suitTrack = doFreezeAssets(attack)
    elif name == 'GlowerPower':
        suitTrack = doGlowerPower(attack)
    elif name == 'ReArrange':
        suitTrack = doFilibusterPhase2(attack)
    elif name == 'ShortSqueeze':
        suitTrack = doShortSqueeze(attack)
    elif name == 'BlueChip':
        suitTrack = doBlueChip(attack)
    elif name == 'FallingKnife':
        suitTrack = doFallingKnife(attack)
    elif name == 'GuiltTrip':
        if suit.isAngry:
            suitTrack = Sequence(ActorInterval(suit, 'neutral-enraged-return'), doGuiltTrip(attack))
        else:
            suitTrack = doGuiltTrip(attack)
    elif name == 'Embezzle':
        suitTrack = doEmbezzle(attack)
    elif name == 'FloodTheMarket':
        suitTrack = doFloodTheMarket(attack)
    elif name == 'MoneyTrip':
        suitTrack = doSynergy(attack)
    elif name == 'HalfWindsor':
        suitTrack = doHalfWindsor(attack)
    elif name == 'HangUp':
        suitTrack = doHangUp(attack)
    elif name == 'HeadShrink':
        suitTrack = doHeadShrink(attack)
    elif name == 'HotAir':
        if suit.dna.name == 'safesupervis':
            suitTrack = doHotAirPressurizer(attack)
        else:
            suitTrack = doHotAir(attack)
    elif name == 'Jargon':
        suitTrack = doJargon(attack)
    elif name == 'Legalese':
        suitTrack = doLegalese(attack)
    elif name == 'LawBook':
        suitTrack = doThrowBook(attack)
    elif name == 'Liquidate':
        suitTrack = doLiquidate(attack)
    elif name == 'MarketCrash':
        suitTrack = doMarketCrash(attack)
    elif name == 'MumboJumbo':
        suitTrack = doMumboJumbo(attack)
    elif name == 'ParadigmShift':
        if suit.isAngry:
            suitTrack = Sequence(ActorInterval(suit, 'neutral-enraged-return'), doParadigmShift(attack))
        else:
            suitTrack = doParadigmShift(attack)
    elif name == 'PeckingOrder':
        suitTrack = doPeckingOrder(attack)
    elif name == 'PickPocket':
        suitTrack = doPickPocket(attack)
    elif name == 'PinkSlip':
        suitTrack = doPinkSlip(attack)
    elif name == 'PlayHardball':
        suitTrack = doPlayHardball(attack)
    elif name == 'PoundKey':
        suitTrack = doPoundKey(attack)
    elif name == 'PowerTie':
        suitTrack = doPowerTie(attack)
    elif name == 'PowerTrip':
        suitTrack = doPowerTrip(attack)
    elif name == 'Quake':
        suitTrack = doQuake(attack)
    elif name == 'RazzleDazzle':
        suitTrack = doRazzleDazzle(attack)
    elif name == 'RedTape':
        suitTrack = doRedTape(attack)
    elif name == 'ReOrg':
        suitTrack = doReOrg(attack)
    elif name == 'RestrainingOrder':
        suitTrack = doRestrainingOrder(attack)
    elif name == 'Rolodex':
        suitTrack = doRolodex(attack)
    elif name == 'RubberStamp':
        suitTrack = doRubberStamp(attack)
    elif name == 'RubOut':
        suitTrack = doRubOut(attack)
    elif name == 'Sacked':
        suitTrack = doSacked(attack)
    elif name == 'Schmooze':
        suitTrack = doSchmooze(attack)
    elif name == 'TestSchmooze':
        suitTrack = doSchmooze(attack)
    elif name == 'Shake':
        suitTrack = doShake(attack)
    elif name == 'Inject':
        suitTrack = doInject(attack)
    elif name == 'Shred':
        suitTrack = doShred(attack)
    elif name == 'SongAndDance':
        suitTrack = doSongAndDance(attack)
    elif name == 'Spin':
        suitTrack = doSpin(attack)
    elif name == 'Synergy':
        suitTrack = doInterestCalculations(attack)
    elif name == 'Tabulate':
        suitTrack = doTabulate(attack)
    elif name == 'Golf':
        suitTrack = doTeeOff(attack)
    elif name == 'ThrowBook':
        suitTrack = doThrowBook(attack)
    elif name == 'Novel':
        suitTrack = doThrowBook(attack)
    elif name == 'Newspaper':
        suitTrack = doMarketCrash(attack)
    elif name == 'Tremor':
        if suit.isAngry:
            suitTrack = Sequence(ActorInterval(suit, 'neutral-enraged-return'), doTremor(attack))
        else:
            suitTrack = doTremor(attack)
    elif name == 'Withdrawal':
        suitTrack = doWithdrawal(attack)
    elif name == 'WriteOff':
        suitTrack = doWriteOff(attack)
        #redd heir-wing cheats
    elif name == 'ReddAutoRepair':
        suitTrack = MovieLawbotLitigationCheats.doAutoRepair(attack)
    elif name == 'ReddLiquidationSale':
        suitTrack = MovieLawbotLitigationCheats.doLiquidationSale(attack)
    elif name == 'ReddPeckingOrder':
        suitTrack = MovieLawbotLitigationCheats.doPeckingOrder(attack)
        # wsi cheats
    elif name == 'WSICeaseAndDesist':
        suitTrack = MovieLawbotLitigationCheats.doCeaseAndDesist(attack)
    elif name == 'WSIJuryNotice':
        suitTrack = MovieLawbotLitigationCheats.doJuryNotice(attack)
        # arbitrator cheats
    elif name == 'ArbitratorObjection':
        if suit.isAngry:
            suitTrack = Sequence(ActorInterval(suit, 'neutral-enraged-return'), MovieLawbotLitigationCheats.doGavelCourtRecord2(attack))
        else:
            suitTrack = MovieLawbotLitigationCheats.doGavelCourtRecord2(attack)
    elif name == 'ArbitratorPaperFiling':
        suitTrack = MovieLawbotLitigationCheats.doPaperweight(attack)
    elif name == 'ArbitratorWhirlwind':
        suitTrack = MovieLawbotLitigationCheats.doWhirlwind(attack)
    elif name == 'ArbitratorThrowBook':
        suitTrack = MovieLawbotLitigationCheats.doThrowBookCog(attack, 1)
    elif name == 'ArbitratorThrowBook2':
        suitTrack = MovieLawbotLitigationCheats.doThrowBookCog(attack, 2)
    elif name == 'ArbitratorThrowBook3':
        suitTrack = MovieLawbotLitigationCheats.doThrowBookCog(attack, 3)
    elif name == 'ArbitratorThrowBook4':
        suitTrack = MovieLawbotLitigationCheats.doThrowBookCog(attack, 4)
    elif name == 'ArbitratorThrowBook5':
        suitTrack = MovieLawbotLitigationCheats.doThrowBookCog(attack, 5)
    #litigator cheats
    elif name == 'LitigatorSnapSoak':
        suitTrack = MovieLawbotLitigationCheats.doSnapBindings(attack, suit)
    elif name == 'LitigatorSnapBindings':
        suitTrack = MovieLawbotLitigationCheats.doSnapBindings(attack, suit)
    elif name == 'LitigatorSnap':
        suitTrack = MovieLawbotLitigationCheats.doSnap(attack, suit)
    elif name == 'LitigatorSnapStenographer':
        suitTrack = MovieLawbotLitigationCheats.doSnapStenographer(attack, suit)
    elif name == 'LitigatorBayouBash':
        suitTrack = MovieLawbotLitigationCheats.doBayouBash(attack)
    elif name == 'LitigatorBayouBellow':
        suitTrack = MovieLawbotLitigationCheats.doBayouBellow(attack)
    #stenographer cheats
    elif name == 'StenographerSanctionBindings':
        suitTrack = MovieLawbotLitigationCheats.doCourtSanction2(attack)
    elif name == 'StenographerSanctionSuppression':
        suitTrack = MovieLawbotLitigationCheats.doCourtSanction2(attack)
    elif name == 'StenographerSanction':
        suitTrack = MovieLawbotLitigationCheats.doCourtSanction(attack)
    elif name == 'StenographerSanctionLitigator':
        suitTrack = MovieLawbotLitigationCheats.doCourtSanctionLitigator(attack)
    elif name == 'StenographerCourtRecordBan':
        suitTrack = MovieLawbotLitigationCheats.doGavelCourtRecord(attack)
    #case manager cheats
    elif name == 'CaseManagerInsurancePlanScapegoat':
        suitTrack = MovieLawbotLitigationCheats.doCaseInsurancePlanInsuranceScapegoat(attack, 1, 3, 5)
    elif name == 'CaseManagerInsurancePlanScapegoat2':
        suitTrack = MovieLawbotLitigationCheats.doCaseInsurancePlanInsuranceScapegoat(attack, 0, 2, 4)
    elif name == 'CaseManagerInsurancePlan':
        suitTrack = MovieLawbotLitigationCheats.doCaseInsurancePlanInsurance(attack, 1, 3, 5)
    elif name == 'CaseManagerInsurancePlan2':
        suitTrack = MovieLawbotLitigationCheats.doCaseInsurancePlanInsurance(attack, 0, 2, 4)
    elif name == 'CaseManagerInsurance':
        suitTrack = MovieLawbotLitigationCheats.doCaseInsurance(attack)
    elif name == 'CaseManagerInsurance2':
        suitTrack = MovieLawbotLitigationCheats.doCaseInsuranceScapegoat(attack)
    elif name == 'CaseManagerLegalBindings':
        suitTrack = MovieLawbotLitigationCheats.doLegalBindings(attack)
    elif name == 'CaseManagerLegalBindings2':
        suitTrack = MovieLawbotLitigationCheats.doCaseInsurancePlanInsurance2(attack)
    elif name == 'CaseManagerLegallyBound':
        suitTrack = MovieLawbotLitigationCheats.doLegallyBound(attack)
    elif name == 'CaseManagerCourtRecordBan':
        suitTrack = MovieLawbotLitigationCheats.doGavelCourtRecord(attack)
    #scapegoat cheats
    elif name == 'ScapegoatRageBuilding':
        suitTrack = MovieUniversalCheats.doRageBuilding(attack)
    elif name == 'ScapegoatShieldsUp':
        suitTrack = MovieLawbotLitigationCheats.doShieldsUp(attack)
    elif name == 'ScapegoatEnraged':
        suitTrack = MovieLawbotLitigationCheats.doEnraged(attack)
    elif name == 'ScapegoatGavel':
        if suit.isAngry:
            suitTrack = Sequence(ActorInterval(suit, 'neutral-enraged-return'), MovieLawbotLitigationCheats.doSuppression(attack))
        else:
            suitTrack = MovieLawbotLitigationCheats.doSuppression(attack)
    elif name == 'ScapegoatBarnyardBash':
        suitTrack = MovieLawbotLitigationCheats.doSuppressionRevert(attack)
    elif name == 'ScapegoatCourtRecordBan':
        suitTrack = MovieLawbotLitigationCheats.doGavelCourtRecord(attack)
    #powerhouse cheats
    elif name == 'PowerhouseToleranceBuilding':
        suitTrack = MovieUniversalCheats.doRageBuilding(attack)
    elif name == 'PowerhouseAbsorb':
        suitTrack = MovieBossbotLitigationCheats.doAbsorb(attack)
    elif name == 'PowerhouseSoakImmune':
        suitTrack = MovieBossbotLitigationCheats.doSoakImmune(attack)
    elif name == 'PowerhouseGroundbreaker':
        suitTrack = MovieBossbotLitigationCheats.doGroundbreaker(attack)
    elif name == 'PowerhouseGroundbreakerRevert':
        suitTrack = MovieBossbotLitigationCheats.doGroundbreakerRevert(attack)
    elif name == 'PowerhouseLureImmune':
        suitTrack = MovieBossbotLitigationCheats.doLureImmune(attack)
    elif name == 'PowerhouseSyphon':
        suitTrack = MovieBossbotLitigationCheats.doSyphon(attack)
    elif name == 'PowerhouseZapImmune':
        suitTrack = MovieBossbotLitigationCheats.doZapImmune(attack)
    elif name == 'PowerhouseDropImmune':
        suitTrack = MovieBossbotLitigationCheats.doDropImmune(attack)
    elif name == 'PowerhouseSyphonDesperation':
        suitTrack = MovieBossbotLitigationCheats.doSyphonDesperation(attack)
    elif name == 'PowerhouseSnipeVulnerable':
        suitTrack = MovieBossbotLitigationCheats.doThrowImmune(attack)
    elif name == 'PowerhouseSnipeGagBan':
        suitTrack = MovieBossbotLitigationCheats.doAftershock(attack)
    elif name == 'PowerhouseSnipeSoaked':
        suitTrack = MovieBossbotLitigationCheats.doAftershock(attack)
    elif name == 'PowerhouseSnipeBookkept':
        suitTrack = MovieBossbotLitigationCheats.doAftershock(attack)
    elif name == 'PowerhouseSnipeMulligan':
        suitTrack = MovieBossbotLitigationCheats.doSoundImmune(attack)
    elif name == 'PowerhouseSnipeCollectCall':
        suitTrack = MovieBossbotLitigationCheats.doGeneration3(attack)
    elif name == 'PowerhouseGeneration':
        suitTrack = MovieBossbotLitigationCheats.doGeneration(attack)
    elif name == 'PowerhouseGeneration2':
        suitTrack = MovieBossbotLitigationCheats.doGeneration2(attack)
    elif name == 'PowerhouseBurnDamage':
        suitTrack = MovieBossbotLitigationCheats.doAftershockDamage(attack)
    #bookkeeper cheats
    elif name == 'BookkeeperPaperCutSoaked':
        suitTrack = MovieBossbotLitigationCheats.doPaperCutMulti(attack)
    elif name == 'BookkeeperPaperCutMarked':
        suitTrack = MovieBossbotLitigationCheats.doBookkeepingDamageUp(attack)
    elif name == 'BookkeeperPaperCut':
        suitTrack = MovieBossbotLitigationCheats.doPaperCut(attack)
    elif name == 'AmbassadorAdvancement2':
        suitTrack = MovieBossbotLitigationCheats.doPaperCut(attack)
    elif name == 'AmbassadorAdvancement3':
        suitTrack = MovieBossbotLitigationCheats.doPaperCut(attack)
    elif name == 'BookkeeperExplodingDocument':
        suitTrack = MovieBossbotLitigationCheats.doOverseer(attack)
    elif name == 'BookkeeperBookkeepingRetaliation':
        suitTrack = MovieBossbotLitigationCheats.doBookkeepingRetaliation(attack)
    elif name == 'BookkeeperBookkeeping':
        suitTrack = MovieBossbotLitigationCheats.doBookkeeping(attack)
    elif name == 'BookkeeperMandatoryFiling':
        suitTrack = MovieBossbotLitigationCheats.doMandatoryFiling(attack)
    #wiretapper cheats
    elif name == 'WiretapperCollectCall':
        suitTrack = MovieBossbotLitigationCheats.doCollectCall(attack)
    elif name == 'WiretapperCollectCall2':
        suitTrack = MovieBossbotLitigationCheats.doVoicemail(attack)
    elif name == 'WiretapperCollectCallDamage':
        suitTrack = MovieBossbotLitigationCheats.doCollectCallDues(attack)
    elif name == 'WiretapperWiretapped':
        suitTrack = MovieBossbotLitigationCheats.doWiretapped(attack)
    elif name == 'WiretapperVoicemail':
        suitTrack = MovieBossbotLitigationCheats.doVoicemailReal(attack)
    elif name == 'WiretapperBrokenConnection':
        suitTrack = MovieBossbotLitigationCheats.doBrokenConnection(attack)
    elif name == 'WiretapperGagBan':
        suitTrack = MovieBossbotLitigationCheats.doCloseTheLoopNew(attack)
    elif name == 'WiretapperBusySignal':
        suitTrack = MovieBossbotLitigationCheats.doBusySignal(attack)
    #ambassador cheats
    elif name == 'AmbassadorHeadRoller':
        suitTrack = MovieBossbotLitigationCheats.doDamageUp1(attack)
    elif name == 'AmbassadorHeadRoller':
        suitTrack = MovieBossbotLitigationCheats.doDamageUp1(attack)
    elif name == 'AmbassadorHeadRoller2':
        suitTrack = MovieBossbotLitigationCheats.doDamageUp2(attack)
    elif name == 'AmbassadorHeadRoller3':
        suitTrack = MovieBossbotLitigationCheats.doDamageUp3(attack)
    elif name == 'AmbassadorHeadRoller4':
        suitTrack = MovieBossbotLitigationCheats.doDamageUp4(attack)
    elif name == 'AmbassadorHeadRoller5':
        suitTrack = MovieBossbotLitigationCheats.doDamageUp5(attack)
    elif name == 'AmbassadorAdvancement':
        suitTrack = MovieBossbotLitigationCheats.doAdvancement(attack)
    elif name == 'AmbassadorAdvancement4':
        suitTrack = MovieBossbotLitigationCheats.doAdvancement(attack, 4)
    elif name == 'AmbassadorAdvancement5':
        suitTrack = MovieBossbotLitigationCheats.doAdvancement(attack, 5)
    elif name == 'AmbassadorHeadRollerGroup':
        suitTrack = MovieBossbotLitigationCheats.doHeadRollerGroup(attack)
    elif name == 'AmbassadorRefinement':
        suitTrack = MovieBossbotLitigationCheats.doOilRainHeal(attack)
    elif name == 'AmbassadorRefinementManager':
        suitTrack = MovieBossbotLitigationCheats.doOilRainHealManager(attack)
    elif name == 'AmbassadorPhase2':
        suitTrack = MovieBossbotLitigationCheats.doAmbassadorPhase2(attack)
    elif name == 'AmbassadorDamageUp':
        suitTrack = MovieBossbotLitigationCheats.doAmbassadorDamageUp(attack)
    elif name == 'AmbassadorManagerialProtection':
        suitTrack = MovieBossbotLitigationCheats.doTeeOff(attack)
    elif name == 'AmbassadorManagerialProtectionImmunity':
        suitTrack = MovieBossbotLitigationCheats.doTeeOff(attack)
    elif name == 'AmbassadorMulligan':
        suitTrack = MovieBossbotLitigationCheats.doFore(attack)
    elif name == 'AmbassadorGhostMentality':
        suitTrack = MovieBossbotLitigationCheats.doGhostMentality(attack)
        # liquidator
    elif name == 'LiquidatorOilRain':
        suitTrack = MovieBoardbotLitigationCheats.doOilRain(attack)
    elif name == 'LiquidatorOilRainDamage':
        suitTrack = MovieBoardbotLitigationCheats.doOilRainDamage(attack)
    elif name == 'LiquidatorFreezingRain':
        suitTrack = MovieBoardbotLitigationCheats.doFreezingRain(attack)
    elif name == 'LiquidatorHeavyRain':
        suitTrack = MovieBoardbotLitigationCheats.doHeavyRain(attack)
    elif name == 'LiquidatorHeavyRainDamage':
        suitTrack = MovieBoardbotLitigationCheats.doHeavyRainDamage(attack)
    elif name == 'LiquidatorStormCell':
        suitTrack = MovieBoardbotLitigationCheats.doStormCell(attack)
    elif name == 'LiquidatorStormCellDamage':
        suitTrack = MovieBoardbotLitigationCheats.doStormCellDamage(attack)
    elif name == 'LiquidatorInversion':
        suitTrack = MovieBoardbotLitigationCheats.doInversion(attack)
    elif name == 'LiquidatorMonsoon':
        suitTrack = MovieBoardbotLitigationCheats.doMonsoon(attack)
    elif name == 'LiquidatorTornado':
        suitTrack = MovieBoardbotLitigationCheats.doTornado(attack)
        # tollmaster
    elif name == 'TollmasterRushHour':
        suitTrack = MovieBoardbotLitigationCheats.doRushHour(attack)
    elif name == 'TollmasterMandatoryToll':
        suitTrack = MovieBoardbotLitigationCheats.doMandatoryToll(attack)
    elif name == 'TollmasterMandatoryTollFinal':
        suitTrack = MovieBoardbotLitigationCheats.doMandatoryTollFinal(attack)
    elif name == 'TollmasterResonanceTax':
        suitTrack = MovieBoardbotLitigationCheats.doResonanceTax(attack)
    elif name == 'TollmasterResonanceTax2':
        suitTrack = MovieBoardbotLitigationCheats.doResonanceTax2(attack)
    elif name == 'TollmasterResonanceTax3':
        suitTrack = MovieBoardbotLitigationCheats.doResonanceTax3(attack)
    elif name == 'TollmasterResonanceTax4':
        suitTrack = MovieBoardbotLitigationCheats.doResonanceTax4(attack)
    elif name == 'TollmasterResonanceTax5':
        suitTrack = MovieBoardbotLitigationCheats.doResonanceTax5(attack)
    elif name == 'TollmasterMissedPayment':
        suitTrack = MovieBoardbotLitigationCheats.doMissedPayment(attack)
    elif name == 'TollmasterLedgerOfSound':
        suitTrack = MovieBoardbotLitigationCheats.doLedgerOfSound(attack)
    elif name == 'TollmasterBalanceTheLedger':
        suitTrack = MovieBoardbotLitigationCheats.doBalanceTheLedger(attack)
    elif name == 'TollmasterBalanceTheLedger2':
        suitTrack = MovieBoardbotLitigationCheats.doBalanceTheLedger2(attack)
    elif name == 'TollmasterBalanceTheLedger3':
        suitTrack = MovieBoardbotLitigationCheats.doBalanceTheLedger3(attack)
    elif name == 'TollmasterBalanceTheLedger4':
        suitTrack = MovieBoardbotLitigationCheats.doBalanceTheLedger4(attack)
    elif name == 'TollmasterBalanceTheLedger5':
        suitTrack = MovieBoardbotLitigationCheats.doBalanceTheLedger5(attack)
        # record keeper
    elif name == 'RecordkeeperMinutesTaken':
        suitTrack = MovieBoardbotLitigationCheats.doPermanentRecordAudit(attack)
    elif name == 'RecordkeeperMinutesTakenContingency':
        suitTrack = MovieBoardbotLitigationCheats.doPermanentRecordAuditBanned(attack)
    elif name == 'RecordkeeperMinutesTakenDamage':
        suitTrack = MovieBoardbotLitigationCheats.doMinutesTakenDamageBooks(attack)
    elif name == 'RecordkeeperPaperTrail':
        suitTrack = MovieBoardbotLitigationCheats.doShadowToon(attack)
    elif name == 'RecordkeeperRevisedFiling':
        suitTrack = MovieBoardbotLitigationCheats.doRevisedFiling(attack)
    elif name == 'RecordkeeperRevisedFilingLiquidation':
        suitTrack = MovieBoardbotLitigationCheats.doShadowToon2(attack)
    elif name == 'RecordkeeperRedlinedClause':
        suitTrack = MovieBoardbotLitigationCheats.doRedlinedClause(attack)
    elif name == 'RecordkeeperRedlinedClauseMissedPayment':
        suitTrack = MovieBoardbotLitigationCheats.doMinutesTaken(attack)
    elif name == 'RecordkeeperAuditCycle':
        suitTrack = MovieBoardbotLitigationCheats.doAuditCycle(attack)
    elif name == 'RecordkeeperPhantomEntrySpawn':
        suitTrack = MovieBoardbotLitigationCheats.doPhantomEntrySpawn(attack)
    elif name == 'RecordkeeperPhantomEntryDamage':
        suitTrack = MovieBoardbotLitigationCheats.doPhantomEntryDamage(attack)
    elif name == 'RecordkeeperPhantomEntrySacrifice':
        suitTrack = MovieBoardbotLitigationCheats.doPhantomEntrySacrifice(attack)
        # corporate butcherer
    elif name == 'ButcherOverride':
        if suit.isChainsawPhase3:
            suitTrack = MovieBoardbotLitigationCheats.doOverridePhase3(attack)
        else:
            suitTrack = MovieBoardbotLitigationCheats.doOverride(attack)
    elif name == 'ButcherOverrideRemoval':
        if suit.isChainsawPhase3:
            suitTrack = MovieBoardbotLitigationCheats.doOverrideRemovalPhase3(attack)
        else:
            suitTrack = MovieBoardbotLitigationCheats.doOverrideRemoval(attack)
    elif name == 'ButcherRevvingUp':
        suitTrack = MovieBoardbotLitigationCheats.doRevvingUp(attack)
    elif name == 'ButcherRevvingUpWhipsaw':
        suitTrack = MovieBoardbotLitigationCheats.doRevvingUpWhipsaw(attack)
    elif name == 'ButcherKickback':
        suitTrack = MovieBoardbotLitigationCheats.doKickback(attack)
    elif name == 'ButcherMarkedWood':
        suitTrack = MovieBoardbotLitigationCheats.do7000RPM(attack)
    elif name == 'ButcherOffboarding':
        suitTrack = MovieBoardbotLitigationCheats.do2000RPMOffboarding(attack, 1)
    elif name == 'ButcherOffboarding2':
        suitTrack = MovieBoardbotLitigationCheats.do2000RPMOffboarding(attack, 2)
    elif name == 'ButcherOffboarding3':
        suitTrack = MovieBoardbotLitigationCheats.do2000RPMOffboarding(attack, 3)
    elif name == 'ButcherOffboarding4':
        suitTrack = MovieBoardbotLitigationCheats.do2000RPMOffboarding(attack, 4)
    elif name == 'ButcherOffboarding5':
        suitTrack = MovieBoardbotLitigationCheats.do2000RPMOffboarding(attack, 5)
    elif name == 'ButcherAggrandize':
        suitTrack = MovieBoardbotLitigationCheats.do3000RPMAggrandize(attack, 1)
    elif name == 'ButcherAggrandize2':
        suitTrack = MovieBoardbotLitigationCheats.do3000RPMAggrandize(attack, 2)
    elif name == 'ButcherAggrandize3':
        suitTrack = MovieBoardbotLitigationCheats.do3000RPMAggrandize(attack, 3)
    elif name == 'ButcherAggrandize4':
        suitTrack = MovieBoardbotLitigationCheats.do3000RPMAggrandize(attack, 4)
    elif name == 'ButcherAggrandize5':
        suitTrack = MovieBoardbotLitigationCheats.do3000RPMAggrandize(attack, 5)
    elif name == 'ButcherSparkPlug':
        suitTrack = MovieBoardbotLitigationCheats.do2000RPMSparkPlug(attack)
    elif name == 'ButcherSparkPlugDamage':
        suitTrack = MovieBoardbotLitigationCheats.doSparkPlugDamage(attack)
    elif name == 'ButcherScabbard':
        suitTrack = MovieBoardbotLitigationCheats.do7000RPMScabbard(attack)
    elif name == 'ButcherLayoffs':
        suitTrack = MovieBoardbotLitigationCheats.do10000RPM(attack)
        # contingency director
    elif name == 'ContingencyFailsafeProtocol':
        suitTrack = MovieBoardbotLitigationCheats.doFailsafeProtocol(attack)
    elif name == 'ContingencyRiskThresholdBreach75':
        suitTrack = MovieBoardbotLitigationCheats.doRiskThresholdBreach75(attack)
    elif name == 'ContingencyRiskThresholdBreach50':
        suitTrack = MovieBoardbotLitigationCheats.doMarkedWood(attack) # Marking Application
    elif name == 'ContingencyRiskThresholdBreach25':
        suitTrack = MovieHighRollerCheats.doSnipe(attack) # Marking Damage
    elif name == 'ContingencySelfRepair':
        suitTrack = MovieBoardbotLitigationCheats.doSelfRepair(attack)
    elif name == 'ContingencyContingencyClause':
        suitTrack = MovieBoardbotLitigationCheats.doContingencyClause(attack)
    elif name == 'ContingencyContingencyClauseRetaliation':
        suitTrack = MovieBoardbotLitigationCheats.doRiskThresholdBreach25(attack)
    elif name == 'ContingencyRedundantAuthority':
        suitTrack = MovieBoardbotLitigationCheats.doRedundantAuthority(attack)
    elif name == 'ContingencyOperationalFreeze':
        suitTrack = MovieFaceTheFamilyCheats.doHighStakesContingency(attack)
    elif name == 'ContingencyForecastCollapse':
        suitTrack = MovieBoardbotLitigationCheats.doForecastCollapse(attack)
    elif name == 'ContingencyRiskThresholdBreach':
        suitTrack = MovieBoardbotLitigationCheats.doRiskThresholdBreach(attack)
    elif name == 'ContingencyMarkLiquidated':
        suitTrack = MovieBoardbotLitigationCheats.doMarkedWood(attack)
    elif name == 'ContingencyMarkRevisedFiling':
        suitTrack = MovieHighRollerCheats.doNoAttack(attack)
        # dividend king
    elif name == 'DividendAccountRollover':
        suitTrack = MovieBoardbotLitigationCheats.doAccountRollover(attack)
    elif name == 'DividendAccountRollover2':
        suitTrack = MovieBoardbotLitigationCheats.doAccountRollover2(attack)
    elif name == 'DividendAccountRollover3':
        suitTrack = MovieBoardbotLitigationCheats.doAccountRollover3(attack)
    elif name == 'DividendAccountRollover4':
        suitTrack = MovieBoardbotLitigationCheats.doAccountRollover4(attack)
    elif name == 'DividendAccountRollover5':
        suitTrack = MovieBoardbotLitigationCheats.doAccountRollover5(attack)
    elif name == 'DividendLiquidationEvent':
        suitTrack = MovieBoardbotLitigationCheats.doLiquidationEvent(attack)
    elif name == 'DividendLiquidationEventDamage':
        suitTrack = MovieBoardbotLitigationCheats.doLiquidationEventDamage(attack)
    elif name == 'DividendTotalMarketMeltdown':
        suitTrack = MovieBoardbotLitigationCheats.doTotalMarketMeltdown(attack)
    elif name == 'DividendTotalMarketMeltdown2':
        suitTrack = MovieBoardbotLitigationCheats.doTotalMarketMeltdown2(attack)
    elif name == 'DividendTotalMarketMeltdownDamage':
        suitTrack = MovieBoardbotLitigationCheats.doMeltdownDamage(attack)
    elif name == 'DividendPeckingOrder':
        suitTrack = MovieBoardbotLitigationCheats.doScabbard(attack)
    elif name == 'DividendPeckingOrderZapped':
        suitTrack = MovieBoardbotLitigationCheats.doEmbezzle(attack)
    elif name == 'DividendZapRetaliation':
        suitTrack = MovieBoardbotLitigationCheats.doThrowRetaliation(attack)
        # ottoman cheats
    elif name == 'OttomanRevisedDraft':
        suitTrack = MovieBoardbotLitigationCheats.doWhirlwind(attack)
    elif name == 'OttomanRedPenReview':
        suitTrack = MovieBoardbotLitigationCheats.doRedPenReview(attack)
    elif name == 'OttomanFootnoteOverload':
        suitTrack = MovieBoardbotLitigationCheats.doFootnoteOverload(attack)
    elif name == 'OttomanPerformanceReview':
        suitTrack = MovieBoardbotLitigationCheats.doPerformanceReview(attack)
    elif name == 'OttomanPerformanceReviewRevert':
        suitTrack = MovieBoardbotLitigationCheats.doPerformanceReviewRevert(attack)
        # crystalline cheats
    elif name == 'CrystalShatteringClarity':
        suitTrack = MovieBoardbotLitigationCheats.doShatteringClarity(attack)
    elif name == 'CrystalRefractDamage':
        suitTrack = MovieBoardbotLitigationCheats.doRefractDamage(attack)
    elif name == 'CrystalRefractDamageRetaliation':
        suitTrack = MovieBoardbotLitigationCheats.doRefractDamageRetaliation(attack)
    elif name == 'CrystalFracturedLimitsOffensive':
        suitTrack = MovieBoardbotLitigationCheats.doFracturedLimits(attack)
    elif name == 'CrystalFracturedLimitsDefensive':
        suitTrack = MovieBoardbotLitigationCheats.doFracturedLimits(attack)
    elif name == 'CrystalFracturedLimitsRetaliation':
        suitTrack = MovieBoardbotLitigationCheats.doFracturedLimitsRetaliation(attack)
    elif name == 'CrystalPrismaticDistortion':
        suitTrack = MovieBoardbotLitigationCheats.doPrismaticDistortion(attack)
        # chairman cheats
    elif name == 'ChairmanTrapRetaliation':
        suitTrack = MovieBoardbotLitigationCheats.doTrapRetaliation(attack)
    elif name == 'ChairmanLureRetaliation':
        suitTrack = MovieBoardbotLitigationCheats.doLureRetaliation(attack)
    elif name == 'ChairmanThrowRetaliation':
        suitTrack = MovieBoardbotLitigationCheats.doThrowRetaliation(attack)
    elif name == 'ChairmanSquirtRetaliation':
        suitTrack = MovieBoardbotLitigationCheats.doSquirtRetaliation(attack)
    elif name == 'ChairmanZapRetaliation':
        suitTrack = MovieBoardbotLitigationCheats.doZapRetaliation(attack)
    elif name == 'ChairmanSoundRetaliation':
        suitTrack = MovieBoardbotLitigationCheats.doSoundRetaliation(attack)
    elif name == 'ChairmanDropRetaliation':
        suitTrack = MovieBoardbotLitigationCheats.doDropRetaliation(attack)
    elif name == 'ChairmanCage':
        suitTrack = MovieBoardbotLitigationCheats.doCage(attack)
    elif name == 'ChairmanPhase2':
        suitTrack = MovieBoardbotLitigationCheats.doPhase2(attack)
    elif name == 'ChairmanOvertime':
        suitTrack = MovieBoardbotLitigationCheats.doOvertime(attack, 1)
    elif name == 'ChairmanOvertime2':
        suitTrack = MovieBoardbotLitigationCheats.doOvertime(attack, 2)
    elif name == 'ChairmanOvertime3':
        suitTrack = MovieBoardbotLitigationCheats.doOvertime(attack, 3)
    elif name == 'ChairmanOvertime4':
        suitTrack = MovieBoardbotLitigationCheats.doOvertime(attack, 4)
    elif name == 'ChairmanOvertime5':
        suitTrack = MovieBoardbotLitigationCheats.doOvertime(attack, 5)
    elif name == 'ChairmanHostileLiquidation':
        suitTrack = MovieBoardbotLitigationCheats.doHostileLiquidation(attack, 1)
    elif name == 'ChairmanHostileLiquidation2':
        suitTrack = MovieBoardbotLitigationCheats.doHostileLiquidation(attack, 2)
    elif name == 'ChairmanHostileLiquidation3':
        suitTrack = MovieBoardbotLitigationCheats.doHostileLiquidation(attack, 3)
    elif name == 'ChairmanHostileLiquidation4':
        suitTrack = MovieBoardbotLitigationCheats.doHostileLiquidation(attack, 4)
    elif name == 'ChairmanHostileLiquidation5':
        suitTrack = MovieBoardbotLitigationCheats.doHostileLiquidation(attack, 5)
    elif name == 'ChairmanSnipe':
        suitTrack = MovieBoardbotLitigationCheats.doSnipe(attack)
        # safety supervisor
    elif name == 'SafetyOverpressureDeath':
        suitTrack = MovieSellbotLitigationCheats.doOverpressureDeath(attack)
    elif name == 'SafetyOverpressured':
        suitTrack = MovieSellbotLitigationCheats.doOverpressured(attack, 1)
    elif name == 'SafetyOverpressured2':
        suitTrack = MovieSellbotLitigationCheats.doOverpressured(attack, 2)
    elif name == 'SafetyOverpressured3':
        suitTrack = MovieSellbotLitigationCheats.doOverpressured(attack, 3)
    elif name == 'SafetyOverpressured4':
        suitTrack = MovieSellbotLitigationCheats.doOverpressured(attack, 4)
    elif name == 'SafetyOverpressured5':
        suitTrack = MovieSellbotLitigationCheats.doOverpressured(attack, 5)
    elif name == 'SafetyHighPressure':
        suitTrack = MovieSellbotLitigationCheats.doHighPressure(attack)
    elif name == 'SafetyHeatWave':
        suitTrack = MovieSellbotLitigationCheats.doHeatWave(attack)
    elif name == 'SafetyHeatWaveCalculation':
        suitTrack = MovieSellbotLitigationCheats.doHeatWaveCalculation(attack)
    elif name == 'SafetyViolation':
        suitTrack = MovieSellbotLitigationCheats.doOverheat2(attack)
    elif name == 'SafetyPromotion':
        suitTrack = MovieSellbotLitigationCheats.doPromotion(attack, 1)
    elif name == 'SafetyPromotion2':
        suitTrack = MovieSellbotLitigationCheats.doOverheat(attack)
    elif name == 'SafetyPromotion3':
        suitTrack = MovieSellbotLitigationCheats.doPromotion(attack, 3)
    elif name == 'SafetyPromotion4':
        suitTrack = MovieSellbotLitigationCheats.doPromotion(attack, 4)
    elif name == 'SafetyPromotion5':
        suitTrack = MovieSellbotLitigationCheats.doPromotion(attack, 5)
    elif name == 'SafetySoakRetaliation':
        suitTrack = MovieSellbotLitigationCheats.doOverheat2(attack)
        # hustler
    elif name == 'HustlerLimitedTimeOfferApprove':
        suitTrack = MovieSellbotLitigationCheats.doLimitedTimeOfferApprove(attack)
    elif name == 'HustlerLimitedTimeOfferDenied':
        suitTrack = MovieSellbotLitigationCheats.doLimitedTimeOfferDenied(attack)
    elif name == 'HustlerSalesPitch':
        suitTrack = MovieSellbotLitigationCheats.doSalesPitch(attack)
    elif name == 'HustlerCustomerRetention':
        suitTrack = MovieSellbotLitigationCheats.doCustomerRetention(attack)
    elif name == 'HustlerClosingTime':
        suitTrack = MovieSellbotLitigationCheats.doClosingTime(attack)
    elif name == 'HustlerBaitAndSwitch':
        suitTrack = MovieHighRollerCheats.doContentSync(attack)
    elif name == 'HustlerExclusiveOffer':
        suitTrack = MovieSellbotLitigationCheats.doContractEnforcementBan(attack)
    elif name == 'HustlerExclusiveOfferRetaliation':
        suitTrack = MovieSellbotLitigationCheats.doExclusiveRetaliation(attack)
    elif name == 'HustlerHalfWindsor':
        suitTrack = doSpin(attack)
        # traffic manager
    elif name == 'UnionBusterContractEnforcementHealing':
        suitTrack = MovieSellbotLitigationCheats.doContractEnforcementHealing(attack)
    elif name == 'TrafficDetour':
        suitTrack = MovieSellbotLitigationCheats.doDetourNew(attack)
    elif name == 'TrafficCongestionPricing':
        suitTrack = MovieSellbotLitigationCheats.doRoadBlock(attack)
    elif name == 'TrafficRedLight':
        suitTrack = MovieSellbotLitigationCheats.doRedLight(attack)
    elif name == 'TrafficRedLightRetaliation':
        suitTrack = MovieSellbotLitigationCheats.doContingencyClauseRetaliation(attack)
    elif name == 'TrafficGreenLight':
        suitTrack = MovieSellbotLitigationCheats.doGreenLight(attack)
    elif name == 'TrafficGreenLightRetaliation':
        suitTrack = MovieSellbotLitigationCheats.doContingencyClauseRetaliation(attack)
    elif name == 'TrafficYield':
        suitTrack = MovieSellbotLitigationCheats.doYield(attack)
    elif name == 'UnionBusterBreachOfContract':
        suitTrack = MovieSellbotLitigationCheats.doBreachOfContract(attack) # YIELD VARIATIONS
    elif name == 'UnionBusterBreachOfContract2':
        suitTrack = MovieSellbotLitigationCheats.doBreachOfContract2(attack)
    elif name == 'UnionBusterBreachOfContract3':
        suitTrack = MovieSellbotLitigationCheats.doBreachOfContract2(attack)
    elif name == 'UnionBusterBreachOfContract4':
        suitTrack = MovieSellbotLitigationCheats.doBreachOfContract2(attack)
        # union buster
    elif name == 'UnionBusterUnionDues':
        suitTrack = MovieUniversalCheats.doSynergy(attack)
    elif name == 'UnionBusterUnionCalculator':
        suitTrack = MovieSellbotLitigationCheats.doUnionCalculator(attack)
    elif name == 'UnionBusterUnionBust':
        suitTrack = MovieSellbotLitigationCheats.doUnionBust(attack)
    elif name == 'UnionBusterUnionBuster':
        suitTrack = MovieSellbotLitigationCheats.doUnionBuster(attack)
    elif name == 'UnionBusterUnionBusterDamage':
        suitTrack = MovieSellbotLitigationCheats.doUnionBusterDamage(attack)
    elif name == 'UnionBusterNoStrikeClause':
        suitTrack = MovieSellbotLitigationCheats.doUnionBuster(attack)
    elif name == 'UnionBusterUnionWages':
        suitTrack = MovieSellbotLitigationCheats.doUnionWages(attack)
    elif name == 'UnionBusterUnionWages2':
        suitTrack = MovieSellbotLitigationCheats.doUnionWages2(attack)
    elif name == 'UnionBusterUnionWages3':
        suitTrack = MovieSellbotLitigationCheats.doUnionWages3(attack)
    elif name == 'UnionBusterUnionWages4':
        suitTrack = MovieSellbotLitigationCheats.doUnionWages4(attack)
    elif name == 'UnionBusterUnionWages5':
        suitTrack = MovieSellbotLitigationCheats.doUnionWages5(attack)
    elif name == 'UnionBusterContractEnforcement':
        suitTrack = MovieSellbotLitigationCheats.doShadowToon(attack)
    elif name == 'UnionBusterContractEnforcement2':
        suitTrack = MovieSellbotLitigationCheats.doHotTake(attack)
        # racketeer
    elif name == 'RacketeerOverextendedLeverage2':
        suitTrack = MovieSellbotLitigationCheats.doOverextendedLeverage(attack)
    elif name == 'RacketeerOverextendedLeverage':
        suitTrack = MovieSellbotLitigationCheats.doProtectedRacket(attack)
    elif name == 'RacketeerProfiteering':
        suitTrack = MovieSellbotLitigationCheats.doProfiteering(attack, 1)
    elif name == 'RacketeerProfiteering2':
        suitTrack = MovieSellbotLitigationCheats.doProfiteering(attack, 2)
    elif name == 'RacketeerProfiteering3':
        suitTrack = MovieSellbotLitigationCheats.doProfiteering(attack, 3)
    elif name == 'RacketeerProfiteering4':
        suitTrack = MovieSellbotLitigationCheats.doProfiteering(attack, 4)
    elif name == 'RacketeerProfiteering5':
        suitTrack = MovieSellbotLitigationCheats.doProfiteering(attack, 5)
    elif name == 'RacketeerExtortion':
        suitTrack = MovieSellbotLitigationCheats.doExtortion(attack)
    elif name == 'RacketeerExtortion2':
        suitTrack = MovieSellbotLitigationCheats.doProtectionPayout(attack)
    elif name == 'RacketeerCompensation':
        suitTrack = MovieSellbotLitigationCheats.doCompensation(attack)
    elif name == 'RacketeerHustling': # Pressurizer Target Check
        suitTrack = MovieHighRollerCheats.doNoAttack(attack)
    elif name == 'RacketeerRacketeering':
        suitTrack = MovieSellbotLitigationCheats.doRacketeering(attack)
    elif name == 'RacketeerPeckingOrderRetaliation':
        suitTrack = MovieSellbotLitigationCheats.doPeckingOrderGroup(attack)
    elif name == 'RacketeerPeckingOrderRetaliationSoak':
        suitTrack = MovieSellbotLitigationCheats.doOverheat2(attack)
        # radiographer
    elif name == 'RadiographerRadioInfrequency':
        suitTrack = MovieSellbotLitigationCheats.doRadioInfrequency(attack)
    elif name == 'RadiographerHotTake':
        suitTrack = MovieSellbotLitigationCheats.doHotTake(attack)
    elif name == 'RadiographerHotTakeDamage':
        suitTrack = MovieSellbotLitigationCheats.doHotTakeDamage(attack)
    elif name == 'RadiographerHotTakeRetaliation': # Pressurizer Rise From The Ashes
        suitTrack = MovieSellbotLitigationCheats.doShadowToon(attack)
    elif name == 'RadiographerOvermodulated':
        suitTrack = MovieSellbotLitigationCheats.doOvermodulated(attack, 1)
    elif name == 'RadiographerOvermodulated2':
        suitTrack = MovieSellbotLitigationCheats.doOvermodulated(attack, 2)
    elif name == 'RadiographerOvermodulated3':
        suitTrack = MovieSellbotLitigationCheats.doOvermodulated(attack, 3)
    elif name == 'RadiographerOvermodulated4':
        suitTrack = MovieSellbotLitigationCheats.doOvermodulated(attack, 4)
    elif name == 'RadiographerOvermodulated5':
        suitTrack = MovieSellbotLitigationCheats.doOvermodulated(attack, 5)
    elif name == 'RadiographerDanceSession':
        suitTrack = MovieHighRollerCheats.doNoAttack(attack)
        # payroll manager
    elif name == 'PayrollPayrollProcessing':
        suitTrack = MovieCashbotLitigationCheats.doPayrollProcessing(attack)    
    elif name == 'PayrollPerformanceBonus':
        suitTrack = MovieCashbotLitigationCheats.doPerformanceBonus(attack)    
        # derrick man cheat
    elif name == 'DerrickManRefinement':
        suitTrack = MovieDirectorsCheats.doRefinementDerrickMan(attack)
        #  dola cheat
    elif name == 'DOLAInkDrain':
        suitTrack = MovieDirectorsCheats.doInkDrainDOLA(attack)
        #  dopr cheat
    elif name == 'DOPRAmbushMarketing':
        suitTrack = MovieDirectorsCheats.doAmbushMarketing(attack)
        # erclaim erfit cheats
    elif name == 'ErclaimHemmorage':
        suitTrack = MovieCountCheats.doHemmorage(attack)
    elif name == 'ErclaimHemmorageHealing':
        suitTrack = MovieCountCheats.doHemmorageHealing(attack)
    elif name == 'ErclaimLaffSteal':
        suitTrack = MovieCountCheats.doLaffSteal(attack)
    elif name == 'ErclaimRiseFromTheScrap':
        suitTrack = MovieCountCheats.doRiseFromTheScrap(attack)
    elif name == 'ErclaimScopeCreep':
        suitTrack = MovieCountCheats.doScopeCreep(attack)
    elif name == 'ErclaimPhase2':
        suitTrack = MovieCountCheats.doErclaimPhase2(attack)
    elif name == 'ErclaimSacrifice':
        suitTrack = MovieCountCheats.doSacrifice(attack)
    elif name == 'ErclaimSacrifice2':
        suitTrack = MovieCountCheats.doSacrifice(attack)
    elif name == 'ErclaimSacrifice3':
        suitTrack = MovieCountCheats.doSacrifice(attack)
    elif name == 'ErclaimSacrifice4':
        suitTrack = MovieCountCheats.doSacrifice(attack)
    elif name == 'ErclaimSacrifice5':
        suitTrack = MovieCountCheats.doSacrifice(attack)
    elif name == 'ErfitWringOut':
        suitTrack = MovieCountCheats.doWringOut(attack)
    elif name == 'ErfitHydrationCheck':
        suitTrack = MovieCountCheats.doHydrationCheck(attack)
    elif name == 'ErfitHydrationCheckRevert':
        suitTrack = MovieCountCheats.doHydrationCheckRevert(attack)
    elif name == 'ErfitProToonShake':
        suitTrack = MovieCountCheats.doProToonShake(attack)
    elif name == 'ErfitGainsFromTheScrap':
        suitTrack = MovieCountCheats.doGainsFromTheScrap(attack)
    elif name == 'ErfitGainsFromTheScrap2':
        suitTrack = MovieCountCheats.doGainsFromTheScrap(attack)
    elif name == 'ErfitGainsFromTheScrap3':
        suitTrack = MovieCountCheats.doGainsFromTheScrap(attack)
    elif name == 'ErfitGainsFromTheScrap4':
        suitTrack = MovieCountCheats.doGainsFromTheScrap(attack)
    elif name == 'ErfitGainsFromTheScrap5':
        suitTrack = MovieCountCheats.doGainsFromTheScrap(attack)
    elif name == 'ErfitPersonalTrainer':
        suitTrack = MovieCountCheats.doPersonalTrainer(attack)
    elif name == 'ErfitPhase2':
        suitTrack = MovieCountCheats.doProToonShakeDamage(attack)
        # high roller phase 1
    elif name == 'HighRollerLureResistance':
        suitTrack = MovieHighRollerCheats.doLureResistance(attack, 1, 3, 5)
    elif name == 'HighRollerLureResistance2':
        suitTrack = MovieHighRollerCheats.doLureResistance(attack, 2, 4, 6)
    elif name == 'HighRollerPhase2':
        suitTrack = MovieHighRollerCheats.doPhase2(attack)
    elif name == 'HighRollerNoAttack':
        suitTrack = MovieHighRollerCheats.doNoAttack(attack)
    elif name == 'HighRollerWheelSpin':
        suitTrack = MovieHighRollerCheats.doWheelSpin(attack)
    elif name == 'HighRollerPuzzle':
        suitTrack = MovieHighRollerCheats.doPuzzle(attack)
    elif name == 'HighRollerPuzzleBan':
        suitTrack = MovieHighRollerCheats.doPuzzleBan(attack)
    elif name == 'HighRollerGameOver':
        suitTrack = MovieHighRollerCheats.doCommercialBreak(attack)
    elif name == 'HighRollerGameOver2':
        suitTrack = MovieHighRollerCheats.doCommercialBreak(attack)
    elif name == 'HighRollerCommercialBreak':
        suitTrack = MovieHighRollerCheats.doCommercialBreak2(attack)
    elif name == 'HighRollerGameTimeSpawn':
        suitTrack = MovieHighRollerCheats.doGameTimeSpawn(attack)
    elif name == 'HighRollerGameTimeCog':
        suitTrack = MovieHighRollerCheats.doGameTimeCog(attack, 1)
    elif name == 'HighRollerGameTimeCog2':
        suitTrack = MovieHighRollerCheats.doGameTimeCog2(attack, 1)
    elif name == 'HighRollerGameTimeCog3':
        suitTrack = MovieHighRollerCheats.doGameTimeCog(attack, 2)
    elif name == 'HighRollerGameTimeCog4':
        suitTrack = MovieHighRollerCheats.doGameTimeCog2(attack, 2)
    elif name == 'HighRollerGameTimeCog5':
        suitTrack = MovieHighRollerCheats.doGameTimeCog(attack, 3)
    elif name == 'HighRollerGameTimeCog6':
        suitTrack = MovieHighRollerCheats.doGameTimeCog2(attack, 3)
    elif name == 'HighRollerGameTimeCog7':
        suitTrack = MovieHighRollerCheats.doGameTimeCog(attack, 4)
    elif name == 'HighRollerGameTimeCog8':
        suitTrack = MovieHighRollerCheats.doGameTimeCog2(attack, 4)
    elif name == 'HighRollerGameTimeCog9':
        suitTrack = MovieHighRollerCheats.doGameTimeCog(attack, 5)
    elif name == 'HighRollerGameTimeCog10':
        suitTrack = MovieHighRollerCheats.doGameTimeCog2(attack, 5)
    elif name == 'HighRollerBust':
        suitTrack = MovieHighRollerCheats.doBust(attack)
    # high roller phase 2 cheats
    elif name == 'HighRollerPhase3':
        suitTrack = MovieHighRollerCheats.doPhase3(attack)
    # high roller phase 3 cheats
    elif name == 'HighRollerFreeCruise':
        suitTrack = MovieHighRollerCheats.doFreeCruise(attack)
    elif name == 'HighRollerRolled':
        suitTrack = MovieHighRollerCheats.doRolled(attack)
    elif name == 'HighRollerConduction':
        suitTrack = MovieHighRollerCheats.doConduction(attack)
    elif name == 'HighRollerDiceRouletteCogs':
        suitTrack = MovieHighRollerCheats.doDiceRoulette(attack)
    elif name == 'HighRollerDiceRouletteToons':
        suitTrack = MovieHighRollerCheats.doDiceRoulette(attack)
    elif name == 'HighRollerDiceRouletteEveryone':
        suitTrack = MovieHighRollerCheats.doDiceRoulette(attack)
    elif name == 'HighRollerDiceRouletteNobody':
        suitTrack = MovieHighRollerCheats.doDiceRoulette(attack)
    elif name == 'HighRollerTrickOfTheLight':
        suitTrack = MovieHighRollerCheats.doTrickOfTheLight(attack)
    elif name == 'HighRollerAceInTheHole':
        suitTrack = MovieHighRollerCheats.doAceInTheHole(attack)
    elif name == 'HighRollerVulnerable':
        suitTrack = MovieHighRollerCheats.doVulnerable(attack)
    elif name == 'HighRollerRaisingTheAnte':
        suitTrack = MovieHighRollerCheats.doFreeCruise(attack)
    # high roller silhouette cheats
    elif name == 'HighRollerDonation':
        suitTrack = MovieHighRollerCheats.doDonation(attack)
    elif name == 'HighRollerSyphon':
        suitTrack = MovieHighRollerCheats.doSyphon(attack)
    elif name == 'HighRollerBar':
        suitTrack = MovieHighRollerCheats.doBar(attack)
    elif name == 'HighRollerBar2':
        suitTrack = MovieHighRollerCheats.doBar(attack)
    elif name == 'HighRollerSingingBlues':
        suitTrack = MovieHighRollerCheats.doSingingBluesMegaphone(attack)
    elif name == 'HighRollerDamageReduction':
        suitTrack = MovieFaceTheFamilyCheats.doHighStakes(attack)
    elif name == 'HighRollerSplashback':
        suitTrack = MovieHighRollerCheats.doSplashback(attack)
    elif name == 'HighRollerCheerRetaliation':
        suitTrack = MovieHighRollerCheats.doSnipe(attack)
    #videographer cheats
    elif name == 'VideographerHardCut':
        suitTrack = MovieHighRollerCheats.doHardCut(attack)
    elif name == 'VideographerRisingStars':
        suitTrack = MovieHighRollerCheats.doRisingStars(attack)
    elif name == 'VideographerRisingStars2':
        suitTrack = MovieHighRollerCheats.doRisingStars(attack)
    elif name == 'VideographerRisingStarsSilhouette':
        suitTrack = MovieHighRollerCheats.doRisingStars(attack)
    elif name == 'VideographerRisingStarsSacrifice':
        suitTrack = MovieHighRollerCheats.doRisingStarsSacrifice(attack)
    elif name == 'VideographerVideoStatic':
        suitTrack = MovieHighRollerCheats.doVideoStatic(attack)
    elif name == 'VideographerElectricShock':
        suitTrack = MovieHighRollerCheats.doElectricShock(attack, 2)
    elif name == 'VideographerElectricShock2':
        suitTrack = MovieHighRollerCheats.doElectricShock(attack, 3)
    elif name == 'VideographerElectricShock3':
        suitTrack = MovieHighRollerCheats.doElectricShock(attack, 4)
    elif name == 'VideographerElectricShock4':
        suitTrack = MovieHighRollerCheats.doElectricShock(attack, 5)
    elif name == 'VideographerAttackRewind':
        suitTrack = MovieHighRollerCheats.doAttackRewind(attack)
    elif name == 'VideographerDirectorCuts':
        suitTrack = MovieHighRollerCheats.doDirectorCuts(attack)
    elif name == 'VideographerDeath':
        suitTrack = MovieHighRollerCheats.doVideographerDeath(attack)
    # broadcaster cheats
    elif name == 'BroadcasterDonation':
        suitTrack = MovieHighRollerCheats.doDonation2(attack)
    elif name == 'BroadcasterDonation2':
        suitTrack = MovieHighRollerCheats.doDonationFail(attack)
    elif name == 'BroadcasterViralSensation':
        suitTrack = MovieHighRollerCheats.doViralSensation(attack)
    #filmmaker cheats
    elif name == 'ChoreoChoreography':
        suitTrack = MovieHighRollerCheats.doChoreography(attack)
    elif name == 'FilmmakerCameraFlash':
        suitTrack = MovieHighRollerCheats.doCameraFlash(attack)
    elif name == 'FilmmakerCameraRewind':
        suitTrack = MovieHighRollerCheats.doCameraRewind(attack)
    elif name == 'FilmmakerBudgetCuts':
        suitTrack = MovieHighRollerCheats.doNoAttack(attack)
    #director cheats
    elif name == 'DirectorCut':
        suitTrack = MovieHighRollerCheats.doCut(attack)
    elif name == 'DirectorAction':
        suitTrack = MovieHighRollerCheats.doAction(attack)
    elif name == 'DirectorActionRetaliation':
        suitTrack = MovieHighRollerCheats.doSnipeMegaphone(attack)
    elif name == 'DirectorBackToOnes':
        suitTrack = MovieHighRollerCheats.doBackToOnes(attack)
    elif name == 'DirectorProductionBudget':
        suitTrack = MovieHighRollerCheats.doSynergy(attack)
    elif name == 'DirectorBudgetExpansion':
        suitTrack = MovieHighRollerCheats.doBudgetExpansion(attack)
    #universal cheats
    elif name == 'TargetCheck':
        suitTrack = MovieHighRollerCheats.doNoAttack(attack)
    elif name == 'AmbassadorTargetCheck':
        suitTrack = MovieHighRollerCheats.doNoAttack(attack)
    elif name == 'Desperation':
        suitTrack = MovieHighRollerCheats.doDesperation(attack)
    elif name == 'Desperation2':
        suitTrack = MovieUniversalCheats.doDesperation2(attack)
    elif name == 'SynergyFees':
        suitTrack = MovieUniversalCheats.doSynergy(attack)
    elif name == 'CalculatingFees':
        suitTrack = MovieUniversalCheats.doCourtCalculations(attack)
    elif name == 'DeathCheck':
        suitTrack = MovieUniversalCheats.doDeathCheck(attack)
    elif name == 'CogSpawn':
        suitTrack = MovieHighRollerCheats.doNoAttack(attack)
    elif name == 'SoakRemoval':
        suitTrack = MovieUniversalCheats.doSoakRemoval(attack)
    elif name == 'DrenchDecrement':
        suitTrack = MovieUniversalCheats.doDrenchDecrement(attack)
    elif name == 'OilRemoval':
        suitTrack = MovieBossbotLitigationCheats.doOilRemoval(attack)
    elif name == 'GovernaughtDeath':
        suitTrack = MovieUniversalCheats.doGovernaughtDeath(attack)
    elif name == 'MarkRemoval':
        suitTrack = MovieUniversalCheats.doMarkRemoval(attack)
    elif name in (
    'LureRemovalPreToon',
    'LureRemoval',
    'LureRemovalHeal',
    'LureRemovalTrap',
    'LureRemovalLure',
    'LureRemovalSound',
    'LureRemovalThrow',
    'LureRemovalSquirt',
    'LureRemovalZap',
    'LureRemovalDrop'
        ):
        suitTrack = MovieUniversalCheats.doLureRemoval(attack)
    elif name == 'SyphonMovie':
        suitTrack = MovieUniversalCheats.doSyphonMovie(attack)
    elif name == 'DamageMovie':
        suitTrack = MovieUniversalCheats.doDamageMovie(attack)
    elif name == 'SueApplication':
        suitTrack = MovieUniversalCheats.doSueApplication(attack)
    elif name == 'SueRemoval':
        suitTrack = MovieUniversalCheats.doSueRemoval(attack)
    elif name == 'SueDamage':
        suitTrack = MovieUniversalCheats.doSueDamage(attack)
    elif name == 'ZapMovie':
        suitTrack = MovieUniversalCheats.doZapMovie(attack)
    elif name == 'AbilityQueued':
        suitTrack = MovieUniversalCheats.doAbilityQueued(attack)
    elif name == 'AbilityQueuedPreToon':
        suitTrack = MovieUniversalCheats.doAbilityQueued(attack)
    elif name == 'AbsorbMovie':
        suitTrack = MovieUniversalCheats.doAbsorbMovie(attack)
    elif name == 'AbsorbMovieLevel':
        suitTrack = MovieUniversalCheats.doAbsorbMovieLevel(attack)
    elif name == 'ForemanPolish':
        suitTrack = MovieBossbotLitigationCheats.doOilRainHeal(attack)
    elif name == 'ForemanExtortion':
        suitTrack = MovieSellbotLitigationCheats.doExtortion(attack)
    elif name == 'ForemanSnipe':
        suitTrack = MovieHighRollerCheats.doSnipe(attack)
    elif name == 'ForemanRedTape':
        suitTrack = MovieFaceTheFamilyCheats.doRedTape(attack)
    elif name == 'ForemanContractor':
        suitTrack = MovieFaceTheFamilyCheats.doContractor(attack)
    elif name == 'ForemanContributing':
        suitTrack = MovieFaceTheFamilyCheats.doContributing(attack)
    elif name == 'ForemanContractorDeath':
        suitTrack = MovieFaceTheFamilyCheats.doContractorRemoval(attack)
    elif name == 'ForemanBurning':
        suitTrack = MovieFaceTheFamilyCheats.doOverheat(attack)
    elif name == 'ForemanUnionized':
        suitTrack = MovieFaceTheFamilyCheats.doUnionized(attack)
    elif name == 'ForemanBurningDamage':
        suitTrack = MovieBossbotLitigationCheats.doSlowBurn(attack)
    elif name == 'ForemanSleepyOvercharge':
        suitTrack = MovieFaceTheFamilyCheats.doSleepyOvercharge(attack)
    elif name == 'ForemanExplosion':
        suitTrack = MovieFaceTheFamilyCheats.doExplosion(attack)
    elif name == 'ForemanCompensation':
        suitTrack = MovieFaceTheFamilyCheats.doCompensation(attack)
    elif name == 'ForemanCompensation2':
        suitTrack = MovieFaceTheFamilyCheats.doCompensation2(attack)
    elif name == 'ForemanCompensation3':
        suitTrack = MovieFaceTheFamilyCheats.doCompensation3(attack)
    elif name == 'ForemanCompensation4':
        suitTrack = MovieFaceTheFamilyCheats.doCompensation4(attack)
    elif name == 'ForemanCompensation5':
        suitTrack = MovieFaceTheFamilyCheats.doCompensation5(attack)
    elif name == 'MintLifeInsurance':
        suitTrack = MovieFaceTheFamilyCheats.doLifeInsurance(attack)
    elif name == 'MintScheming':
        suitTrack = MovieFaceTheFamilyCheats.doScheming(attack)
    elif name == 'MintPolicyTerminated':
        suitTrack = MovieFaceTheFamilyCheats.doPolicyTerminated(attack)
    elif name == 'MintFraudulentDamage':
        suitTrack = MovieFaceTheFamilyCheats.doFraudulentDamage(attack)
    elif name == 'MintAbacusAbove15':
        suitTrack = MovieFaceTheFamilyCheats.doAccountantRequirement(attack)
    elif name == 'MintAbacusBelow15':
        suitTrack = MovieFaceTheFamilyCheats.doAccountantRequirement(attack)
    elif name == 'MintAccountant1':
        suitTrack = MovieFaceTheFamilyCheats.doAccountantRequirement(attack)
    elif name == 'MintAccountant2':
        suitTrack = MovieFaceTheFamilyCheats.doAccountantRequirement(attack)
    elif name == 'MintAccountant3':
        suitTrack = MovieFaceTheFamilyCheats.doAccountantRequirement(attack)
    elif name == 'MintAccountant4':
        suitTrack = MovieFaceTheFamilyCheats.doAccountantRequirement(attack)
    elif name == 'MintAccountant5':
        suitTrack = MovieFaceTheFamilyCheats.doAccountantRequirement(attack)
    elif name == 'MintUsury':
        suitTrack = MovieFaceTheFamilyCheats.doUsury(attack)
    elif name == 'MintApprove':
        suitTrack = MovieFaceTheFamilyCheats.doApproveDisapprove(attack)
    elif name == 'MintDisapprove':
        suitTrack = MovieFaceTheFamilyCheats.doApproveDisapprove(attack)
    elif name == 'MintHurrySickness':
        suitTrack = MovieFaceTheFamilyCheats.doHurrySickness(attack)
    elif name == 'MintMovingGoalposts':
        suitTrack = MovieHighRollerCheats.doContentSync(attack)
    elif name == 'MintLureResistance':
        suitTrack = MovieHighRollerCheats.doLureResistance(attack, 1, 3, 5)
    elif name == 'MintLureResistance2':
        suitTrack = MovieHighRollerCheats.doLureResistance(attack, 2, 4, 6)
    elif name == 'MintLedger':
        suitTrack = MovieBoardbotLitigationCheats.doLedgerOfSound(attack)
    elif name == 'MintAudit':
        suitTrack = MovieBoardbotLitigationCheats.doAuditCycle(attack)
    elif name == 'MintSynergy':
        suitTrack = doSynergy(attack)
    elif name == 'MintCompoundingInterest':
        suitTrack = doSynergy(attack)
    elif name == 'WhistleCompensation':
        suitTrack = MovieLawbotLitigationCheats.doCompensation(attack)
    elif name == 'AttorneyRemand':
        suitTrack = MovieHighRollerCheats.doRemand(attack)
    elif name == 'AttorneyObjection':
        suitTrack = MovieFaceTheFamilyCheats.doObjection(attack)
    elif name == 'AttorneyObjectionSustained':
        suitTrack = MovieFaceTheFamilyCheats.doObjectionSustained(attack)
    elif name == 'AttorneyDrainingPower':
        suitTrack = MovieFaceTheFamilyCheats.doDrainingPower(attack)
    elif name == 'AttorneyInkDrain':
        suitTrack = MovieFaceTheFamilyCheats.doInkDrain(attack)
    elif name == 'AttorneyShakedownVulnerable':
        suitTrack = MovieFaceTheFamilyCheats.doShakedownVulnerable(attack)
    elif name == 'AttorneyShakedownCooldown':
        suitTrack = MovieFaceTheFamilyCheats.doShakedownCooldown(attack)
    elif name == 'AttorneyObjectionOverruled':
        suitTrack = MovieFaceTheFamilyCheats.doObjectionOverruled(attack)
    elif name == 'AttorneyChrono':
        suitTrack = MovieFaceTheFamilyCheats.doComeOn(attack)
    elif name in (
        'AttorneyOverseer',
        'AttorneyOverseerDrop',
        'AttorneyOverseerSquirt',
        'AttorneyOverseerThrow'
    ):
        suitTrack = MovieFaceTheFamilyCheats.doOverseer(attack)
    elif name in (
        'KnockbackThrow',
    'KnockbackSquirt'
    ):
        suitTrack = MovieUniversalCheats.doKnockback(attack)
    elif name in (
            'ComboThrow',
    'ComboSquirt',
    'ComboDrop'
    ):
        suitTrack = MovieUniversalCheats.doCombo(attack)
    elif name == 'AttorneyRushJob':
        suitTrack = MovieFaceTheFamilyCheats.doRushJob(attack)
    elif name == 'AttorneyHurrySickness':
        suitTrack = MovieFaceTheFamilyCheats.doHurrySickness(attack)
    elif name == 'AttorneyDizzy':
        suitTrack = MovieLawbotLitigationCheats.doWhirlwind(attack)
    elif name == 'UnstableTransformation':
        suitTrack = MovieFaceTheFamilyCheats.doUnstableTransformation(attack)

    elif name == 'RushJobTrap':
        suitTrack = MovieFaceTheFamilyCheats.doRushJobTrap(attack)

    elif name == 'RushJobLure':
        suitTrack = MovieFaceTheFamilyCheats.doRushJobLure(attack)

    elif name == 'RushJobThrow':
        suitTrack = MovieFaceTheFamilyCheats.doRushJobThrow(attack)

    elif name == 'RushJobSquirt':
        suitTrack = MovieFaceTheFamilyCheats.doRushJobSquirt(attack)

    elif name == 'RushJobZap':
        suitTrack = MovieFaceTheFamilyCheats.doRushJobZap(attack)

    elif name == 'RushJobSound':
        suitTrack = MovieFaceTheFamilyCheats.doRushJobSound(attack)

    elif name == 'RushJobDrop':
        suitTrack = MovieFaceTheFamilyCheats.doRushJobDrop(attack)
        
    elif name == 'PresidentTargetCheck':
        suitTrack = MovieHighRollerCheats.doNoAttack(attack)
    elif name == 'PresidentMandatoryFiling':
        suitTrack = MovieBossbotLitigationCheats.doMandatoryFiling(attack)
    elif name == 'PresidentLiability':
        suitTrack = MovieBossbotLitigationCheats.doPaperCut(attack)
    elif name == 'PresidentLiability2':
        suitTrack = MovieBossbotLitigationCheats.doPaperCutMulti(attack)
    elif name == 'PresidentExtraTip':
        suitTrack = MovieFaceTheFamilyCheats.doExtraTip(attack, 1)
    elif name == 'PresidentExtraTip2':
        suitTrack = MovieFaceTheFamilyCheats.doExtraTip(attack, 2)
    elif name == 'PresidentExtraTip3':
        suitTrack = MovieFaceTheFamilyCheats.doExtraTip(attack, 3)
    elif name == 'PresidentExtraTip4':
        suitTrack = MovieFaceTheFamilyCheats.doExtraTip(attack, 4)
    elif name == 'PresidentExtraTip5':
        suitTrack = MovieFaceTheFamilyCheats.doExtraTip(attack, 5)
    elif name == 'PresidentExtraTip6':
        suitTrack = MovieFaceTheFamilyCheats.doExtraTip(attack, 0)
    elif name == 'PresidentSnap':
        suitTrack = MovieLawbotLitigationCheats.doSnap(attack, suit)
    elif name == 'PresidentSyphon':
        suitTrack = MovieFaceTheFamilyCheats.doSyphon(attack)
    elif name == 'PresidentBayouBellow':
        suitTrack = MovieLawbotLitigationCheats.doBayouBellow(attack)
    elif name == 'PresidentSnipe':
        suitTrack = MovieHighRollerCheats.doSnipe(attack)
    elif name == 'PresidentDeepFreeze':
        suitTrack = MovieFaceTheFamilyCheats.doDeepFreeze(attack)
    elif name == 'PresidentFrozenDeath':
        suitTrack = MovieFaceTheFamilyCheats.doFrozenDeath(attack)
    elif name == 'PresidentPuzzling':
        suitTrack = MovieFaceTheFamilyCheats.doPuzzling(attack)
    elif name == 'PresidentDriver':
        suitTrack = MovieFaceTheFamilyCheats.doDriver(attack)
    elif name == 'PresidentMulligan':
        suitTrack = MovieFaceTheFamilyCheats.doMulligan(attack)
    elif name == 'PresidentSensational':
        suitTrack = MovieFaceTheFamilyCheats.doSensational(attack)
    elif name == 'PresidentViralSensation':
        suitTrack = MovieFaceTheFamilyCheats.doViralSensation(attack)
    elif name == 'PresidentHighStakes':
        suitTrack = MovieFaceTheFamilyCheats.doHighStakes(attack)
    elif name in (
    'HighStakesHeal',
    'HighStakesTrap',
    'HighStakesLure',
    'HighStakesSound',
    'HighStakesThrow',
    'HighStakesSquirt',
    'HighStakesZap',
    'HighStakesDrop'
        ):
        suitTrack = MovieFaceTheFamilyCheats.doHighStakesNew(attack)
    elif name in (
        'BanLevel4', 'BanLevel5', 'BanLevel6', 'BanLevel7', 'BanLevel8',
        'BanLevel45', 'BanLevel46', 'BanLevel47', 'BanLevel48',
        'BanLevel56', 'BanLevel57', 'BanLevel58',
        'BanLevel67', 'BanLevel68', 'BanLevel78',

        'BanToonup', 'BanTrap', 'BanLure', 'BanThrow',
        'BanSquirt', 'BanZap', 'BanSound', 'BanDrop',

        'BanToonupTrap', 'BanToonupLure', 'BanToonupThrow', 'BanToonupSquirt',
        'BanToonupZap', 'BanToonupSound', 'BanToonupDrop',

        'BanTrapLure', 'BanTrapThrow', 'BanTrapSquirt', 'BanTrapZap',
        'BanTrapSound', 'BanTrapDrop',

        'BanLureThrow', 'BanLureSquirt', 'BanLureZap',
        'BanLureSound', 'BanLureDrop',

        'BanThrowSquirt', 'BanThrowZap', 'BanThrowSound', 'BanThrowDrop',

        'BanSquirtZap', 'BanSquirtSound', 'BanSquirtDrop',

        'BanZapSound', 'BanZapDrop',

        'BanSoundDrop'
    ):
        if suit.dna.name == 'cdirector':
            suitTrack = MovieBoardbotLitigationCheats.doContningencyClauseBanMovie(attack)
        elif suit.dna.name == 'wtapper':
            suitTrack = MovieBossbotLitigationCheats.doBudgetCuts(attack)
        elif suit.dna.name == 'ubuster':
            suitTrack = MovieSellbotLitigationCheats.doContractEnforcementBan(attack)
        else:
            suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name in (
        'DisableToonupTrap', 'DisableToonupLure', 'DisableToonupThrow',
        'DisableToonupSquirt', 'DisableToonupZap', 'DisableToonupSound', 'DisableToonupDrop',

        'DisableTrapLure', 'DisableTrapThrow', 'DisableTrapSquirt',
        'DisableTrapZap', 'DisableTrapSound', 'DisableTrapDrop',

        'DisableLureThrow', 'DisableLureSquirt', 'DisableLureZap',
        'DisableLureSound', 'DisableLureDrop',

        'DisableThrowSquirt', 'DisableThrowZap', 'DisableThrowSound', 'DisableThrowDrop',

        'DisableSquirtZap', 'DisableSquirtSound', 'DisableSquirtDrop',

        'DisableZapSound', 'DisableZapDrop',

        'DisableSoundDrop',

        'DisableLevel45', 'DisableLevel46', 'DisableLevel47', 'DisableLevel48',
        'DisableLevel56', 'DisableLevel57', 'DisableLevel58',
        'DisableLevel67', 'DisableLevel68', 'DisableLevel78'
                                        ):
        suitTrack = MovieUniversalCheats.doCourtMandate(attack)
    elif name in (
        'GagBanRetaliationHeal',
        'GagBanRetaliationTrap',
        'GagBanRetaliationLure',
        'GagBanRetaliationThrow',
        'GagBanRetaliationSquirt',
        'GagBanRetaliationZap',
        'GagBanRetaliationSound',
        'GagBanRetaliationDrop'
    ):
        if suit.dna.name in ('stenog', 'caseman'):
            suitTrack = MovieLawbotLitigationCheats.doGavelCourtRecord(attack)
        elif suit.dna.name == 'wtapper':
            suitTrack = MovieBossbotLitigationCheats.doCloseTheLoopNew(attack)
        elif suit.dna.name == 'racket':
            suitTrack = MovieSellbotLitigationCheats.doPeckingOrderGroup(attack)
        elif suit.dna.name == 'cdirector':
            suitTrack = MovieBoardbotLitigationCheats.doRiskThresholdBreach25(attack)
        elif suit.dna.name == 'ubuster':
            suitTrack = MovieSellbotLitigationCheats.doBreachOfContractGroup(attack)
        else:
            suitTrack = MovieUniversalCheats.doCourtMandate(attack)
    elif name in (
        'AbsorbMovieLure',
        'AbsorbMovieThrow',
        'AbsorbMovieSquirt',
        'AbsorbMovieZap',
        'AbsorbMovieSound',
        'AbsorbMovieDrop'
    ):
        suitTrack = MovieUniversalCheats.doAbsorbMovie(attack)
    elif name in (
        'AbsorbMovieLevelLure',
        'AbsorbMovieLevelThrow',
        'AbsorbMovieLevelSquirt',
        'AbsorbMovieLevelZap',
        'AbsorbMovieLevelSound',
        'AbsorbMovieLevelDrop'
    ):
        suitTrack = MovieUniversalCheats.doAbsorbMovieLevel(attack)
    else:
        notify.warning('unknown attack: %s substituting EEEEEEEEEEEEEE' % name)
        suitTrack = doDefault(attack)
    camTrack = MovieCamera.chooseSuitShot(attack, suitTrack.getDuration())
    battle = attack['battle']
    target = attack['target']
    groupStatus = attack['group']
    toonHprTrack = Parallel()
    for t in target:
        toon = t['toon']
        toonHprTrack.append(Sequence(Func(toon.headsUp, battle, MovieUtil.PNT3_ZERO), Func(toon.loop, 'neutral')))

    suit = attack['suit']
    # Let's see if the Cog exists to attack (Cog's ID cannot be -1).
    if suit:
        if name in suitTrack2ResetNames:
            resetSuitTrack = Sequence(suitTrack)
        else:
            resetSuitTrack = Sequence(Parallel(toonHprTrack, suitTrack, Func(suit.clearSuitStatusEffect, 'lured'), Func(suit.setDizzy, 0), Func(battle.unlureSuit, suit)))
    else:
        resetSuitTrack = Parallel(suitTrack, toonHprTrack) # Make sure we play the movie and, if necessary, reset the Toon's position.
    return (resetSuitTrack, camTrack)


def doUnderPressure(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    propDelay = 0.7
    suitTrack = getSuitTrack(attack)
    propTracks = Parallel()
    pressTracks = Parallel()
    soundTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        underPressure = globalPropPool.getProp('under-pressure')
        leftGear = underPressure.find('**/geo_gear01')
        rightGear = underPressure.find('**/geo_gear02')
        stomper = underPressure.find('**/geo_stomperBase')
        stomper.setPos(Point3(0, 0, 35))
        propTrack = Sequence(
            Func(__showProp, underPressure, battle, pos=toon.getPos(battle)),
            Wait(propDelay),
            Parallel(
                LerpHprInterval(leftGear, 0.2, VBase3(0, -90, 0)),
                LerpHprInterval(rightGear, 0.2, VBase3(0, 90, 0))
            ),
            Wait(0.5),
            Parallel(
                LerpHprInterval(leftGear, 0.4, VBase3(0, 0, 0), blendType='easeIn'),
                LerpHprInterval(rightGear, 0.4, VBase3(0, 0, 0), blendType='easeIn')
            )
        )
        if dmg > 0:
            # TODO if possible: Get actual Under Pressure sound effects.
            propTrack.append(LerpPosInterval(stomper, 0.1, Point3(0, 0, 7)))
            propTrack.append(Wait(0.5))
            propTrack.append(LerpPosInterval(stomper, 0.9, Point3(0, 0, 30), blendType='easeInOut'))
            pressTracks.append(Sequence(
                Wait(0.8),
                LerpScaleInterval(toon, 0.1, VBase3(1, 0.05, 1), blendType='easeInOut'),
                Wait(0.9),
                LerpScaleInterval(toon, 0.1, VBase3(2, 2, 0.025)),
                Wait(1.0),
                Parallel(
                    Sequence(
                        Wait(0.4),
                        LerpScaleInterval(toon, 0.1, VBase3(1.4, 1.4, 1.4), blendType='easeInOut'),
                        LerpScaleInterval(toon, 0.05, VBase3(0.8, 0.8, 0.8), blendType='easeInOut'),
                        LerpScaleInterval(toon, 0.1 / 3.0, VBase3(1.0, 1.0, 1.0), blendType='easeInOut')
                    ),
                    SoundInterval(loader.loadSfx('phase_9/audio/sfx/toon_decompress.ogg'), node=toon)
                )
            ))
            soundTracks.append(
                Track(
                    (0.9, SoundInterval(loader.loadSfx('phase_9/audio/sfx/CHQ_SOS_cage_land.ogg'), node=toon)),
                    (1.9, SoundInterval(globalBattleSoundCache.getSound('CHQ_FACT_stomper_small.ogg'), node=toon))
                )
            )
        else:
            soundTracks.append(Sequence(
                Wait(0.9),
                SoundInterval(loader.loadSfx('phase_9/audio/sfx/CHQ_SOS_cage_land.ogg'), node=toon)
            ))
        propTrack.append(Func(MovieUtil.removeProp, underPressure))
        propTracks.append(propTrack)

    toonTracks = Parallel()
    for i in range(len(targets)):
        tgt = targets[i]
        toon = tgt['toon']
        dmg = tgt['hp']
        died = tgt['died']
        toonTrack = Sequence(Func(toon.headsUp, battle, suit.getPos(battle)))
        if dmg > 0:
            animTrack = Sequence(
                Wait(0.9),
                Func(toon.surpriseEyes),
                Func(toon.showSurpriseMuzzle),
                ActorInterval(toon, 'cringe', duration=2.0),
                Func(toon.hideSurpriseMuzzle),
                Func(toon.openEyes),
                Func(toon.startBlink),
                ActorInterval(toon, 'jump', startTime=0.2)
            )
            indicatorTrack = Sequence(
                Wait(0.91),
                Func(__doDamage, toon, dmg, died)
            )
            # If I, Professor Control, am right, you cut out the extra time when a Toon went sad.  If you don't like the sad extension, remove the condition and what's under it.
            if died:
                animTrack.append(Wait(5.0))
            toonTrack.append(Parallel(animTrack, indicatorTrack))
        else:
            toonTrack.append(getToonDodgeTrack(attack, tgt, 0.5, ['sidestep']))
        toonTracks.append(toonTrack)

    return Parallel(suitTrack, propTracks, pressTracks, toonTracks, soundTracks)


def doDoubleCross(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    BattleParticles.loadParticles()
    x = MovieUtil.copyProp(BattleParticles.getParticle('audit-mult'))
    x.setColor(1, 0, 0, 1)
    x2 = MovieUtil.copyProp(BattleParticles.getParticle('audit-mult'))
    x2.setColor(1, 0, 0, 1)
    damageDelay = 2
    dodgeDelay = 1
    suitName = suit.getStyleName()
    posPoints = [Point3(0.8, 4.65, suit.height - 2), VBase3(-155.0, 20.0, 90.0)]
    posPoints2 = [Point3(-0.8, 4.65, suit.height - 2), VBase3(-155.0, 20.0, 90.0)]
    appearDelay = 0.8
    suitHoldStart = 1.06
    suitHoldStop = 1.69
    suitHoldDuration = suitHoldStop - suitHoldStart
    xHoldDuration = 1.1
    moveDuration = 1.1
    suitSplicedAnims = []
    suitSplicedAnims.append(['glower',
                             0.01,
                             0.01,
                             suitHoldStart])
    suitSplicedAnims.extend(getSplicedLerpAnims('glower', suitHoldDuration, 1.1, startTime=suitHoldStart))
    suitSplicedAnims.append(['glower', 0.01, suitHoldStop])
    suitTrack = getSuitTrack(attack, splicedAnims=suitSplicedAnims)

    xTracks = Parallel()

    xAppearTrack = Sequence(Wait(suitHoldStart), Func(__showProp, x, suit, posPoints[0], posPoints[1]),
                            LerpScaleInterval(x, suitHoldDuration, Point3(1.2, 1.2, 1.2)), Wait(xHoldDuration * 0.3),
                            Func(battle.movie.needRestoreRenderProp, x), Func(x.wrtReparentTo, battle))
    toonFace = __toonFacePoint(toon, parent=battle)
    if dmg > 0:
        lerpInterval = LerpPosInterval(x, moveDuration, toonFace)
    else:
        lerpInterval = LerpPosInterval(x, moveDuration,
                                       Point3(toonFace.getX(), toonFace.getY() - 5, toonFace.getZ() - 2))
    xMoveTrack = lerpInterval
    xPropTrack = Sequence(xAppearTrack, xMoveTrack, Func(battle.movie.clearRenderProp, x),
                          Func(MovieUtil.removeProp, x))

    x2AppearTrack = Sequence(Wait(suitHoldStart), Func(__showProp, x2, suit, posPoints2[0], posPoints2[1]),
                             LerpScaleInterval(x2, suitHoldDuration, Point3(1.5, 1.5, 1.5)), Wait(xHoldDuration * 0.3),
                             Func(battle.movie.needRestoreRenderProp, x2), Func(x2.wrtReparentTo, battle))
    if dmg > 0:
        lerpInterval2 = LerpPosInterval(x2, moveDuration, toonFace)
    else:
        lerpInterval2 = LerpPosInterval(x2, moveDuration,
                                        Point3(toonFace.getX(), toonFace.getY() - 5, toonFace.getZ() - 2))
    x2MoveTrack = lerpInterval2
    x2PropTrack = Sequence(x2AppearTrack, x2MoveTrack, Func(battle.movie.clearRenderProp, x2),
                           Func(MovieUtil.removeProp, x2))

    xTracks.append(xPropTrack)
    xTracks.append(x2PropTrack)

    damageAnims = [['duck',
                    0.01,
                    0.01,
                    1.4], ['cringe', 0.01, 0.3]]
    toonTrack = getToonTrack(attack, splicedDamageAnims=damageAnims, damageDelay=damageDelay, dodgeDelay=dodgeDelay,
                             dodgeAnimNames=['duck'], showDamageExtraTime=1.5, showMissedExtraTime=1.5)
    return Parallel(suitTrack, toonTrack, xTracks)


def doMysteriousDisappearance(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    paper = globalPropPool.getProp('shredder-paper')
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        posPoints = [Point3(.675, -1.5, -0.075), VBase3(10, 250, -10)]
    else:
        posPoints = [Point3(.825, -1.5, -0.05), VBase3(10, 250, -10)]
    propTrack = Sequence(
        getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.5, MovieUtil.PNT3_ONE, scaleUpTime=0.25))
    propTrack.append(Wait(1.2))
    hitPoint = __toonFacePoint(toon, parent=battle)
    hitPoint.setX(hitPoint.getX() - 1.4)
    missPoint = __toonGroundPoint(attack, toon, 0.7, parent=battle)
    missPoint.setX(missPoint.getX() - 1.1)
    propTrack.append(getPropThrowTrack(attack, paper, [hitPoint], [missPoint], parent=battle))

    headParts = toon.getHeadParts()
    torsoParts = toon.getTorsoParts()
    legsParts = toon.getLegsParts()
    toonPos = toon.getPos(render)

    def hideParts(parts):
        track = Parallel()
        for partNum in range(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.setTransparency, 1))
            track.append(LerpFunctionInterval(nextPart.setAlphaScale, fromData=1, toData=0, duration=0.2))

        return track

    def showParts(parts):
        track = Parallel()
        for partNum in range(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.clearColorScale))
            track.append(Func(nextPart.clearTransparency))

        return track

    dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
    dustCloud.setBillboardAxis(2.0)
    dustCloud.setZ(3)
    dustCloud.setScale(0.4)
    dustCloud.createTrack()

    toonTrack = Parallel()
    if dmg > 0:
        dustCloudHideIval = Sequence(Func(dustCloud.reparentTo, render),
                                     Func(dustCloud.setPos, Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + 3)),
                                     dustCloud.track, Func(dustCloud.detachNode), name='dustCloadIval')
        dustCloudShowIval = Sequence(Func(dustCloud.reparentTo, render),
                                     Func(dustCloud.setPos, Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + 3)),
                                     dustCloud.track, Func(dustCloud.detachNode), Func(dustCloud.destroy),
                                     name='dustCloadIval2')

        toonTrack.append(Sequence(
            Wait(2.3),
            Parallel(hideParts(headParts), hideParts(torsoParts), hideParts(legsParts), dustCloudHideIval),
            Wait(1.7),
            Parallel(showParts(headParts), showParts(torsoParts), showParts(legsParts), dustCloudShowIval),
        ))

    toonTrack.append(getToonTrack(attack, 2.3, ['conked'], 2.5, ['jump']))

    return Parallel(suitTrack, toonTrack, propTrack)

def doGoldDust(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    BattleParticles.loadParticles()
    suitType = getSuitBodyType(attack['suitName'])
    partDelay = 0
    damageDelay = 1.5
    dodgeDelay = 1.3
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    initialCloudHeight = suit.height + 3
    cloudPosPoints = [Point3(0, 3, initialCloudHeight), MovieUtil.PNT3_ZERO]
    cloudPropTracks = Parallel()
    for t in targets:
        toon = t['toon']
        snowEffect = BattleParticles.createParticleEffect('FreezeAssets')
        BattleParticles.setEffectTexture(snowEffect, 'snow-particle', Vec4(0.898, 0.811, 0.446, 1.0))
        cloud = globalPropPool.getProp('stormcloud')
        cloudPropTrack = Sequence()
        cloudPropTrack.append(Func(cloud.pose, 'stormcloud', 0))
        cloudPropTrack.append(getPropAppearTrack(cloud, suit, cloudPosPoints, 1e-06, Point3(3, 3, 3), scaleUpTime=0.25))
        cloudPropTrack.append(Func(battle.movie.needRestoreRenderProp, cloud))
        cloudPropTrack.append(Func(cloud.wrtReparentTo, render))
        targetPoint = __toonFacePoint(toon)
        targetPoint.setZ(targetPoint[2] + 3)
        cloudPropTrack.append(LerpPosInterval(cloud, .25, pos=targetPoint))
        cloudPropTrack.append(Wait(partDelay))
        cloudPropTrack.append(
            ParticleInterval(snowEffect, cloud, worldRelative=0, duration=3.5, cleanup=True, softStopT=-1))
        cloudPropTrack.append(Wait(0.4))
        cloudPropTrack.append(LerpScaleInterval(cloud, 0.25, MovieUtil.PNT3_NEARZERO))
        cloudPropTrack.append(Func(cloud.removeNode))
        cloudPropTracks.append(cloudPropTrack)

    damageAnims = [['cringe',
                    0.01,
                    0.4,
                    0.8], ['duck', 0.01, 1.6]]
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay,
                               dodgeAnimNames=['sidestep'], showMissedExtraTime=1.2)
    soundTrack = getSoundTrack('SA_brainstorm.ogg', delay=0.7, node=suit)
    return Parallel(suitTrack, toonTracks, cloudPropTracks, soundTrack)

def doGoldRush(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.7
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1

    particleEffect = BattleParticles.createParticleEffect('GoldRush')
    waterfallEffect = BattleParticles.createParticleEffect(file='goldRushWaterfall')
    suitTrack = getSuitAnimTrack(attack)
    partTrack = getPartTrack(particleEffect, 1.0, 3.9, [particleEffect, suit, 0], softStop=-2)
    waterfallTrack = getPartTrack(waterfallEffect, 0.8, 3.9, [waterfallEffect, suit, 0], softStop=-2)
    damageAnims = [['slip-forward']]
    dodgeAnims = []
    dodgeAnims.append(['jump',
     0.01,
     0,
     0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.3, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, damageAnimNames=['slip-forward'], dodgeDelay=0.91, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.0)
    synergySoundTrack = Sequence(Wait(0.9), SoundInterval(globalBattleSoundCache.getSound('SA_synergy.ogg'), node=suit))
    if hitAtleastOneToon > 0:
        fallingSoundTrack = Sequence(Wait(damageDelay + 0.5), SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=suit))
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, fallingSoundTrack, toonTracks)
    else:
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, toonTracks)


def doClipOnTie(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitType = getSuitBodyType(attack['suitName'])
    throwDelay = 1.0
    damageDelay = throwDelay + 1.23
    dodgeDelay = damageDelay - 0.20
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        posPoints = [Point3(0.66, 0.51, -0.45), VBase3(-69.652, -57.199, 67.96)]
        scale = Point3(1.0, 1.0, 1.0)
    else:
        posPoints = [Point3(0.66, 0.51, -0.45), VBase3(-69.652, -57.199, 67.96)]
        scale = Point3(1.0, 1.0, 1.0)
    tiePropTracks = Parallel()
    hitAtleastOneToon = False
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = True
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        tie = globalPropPool.getProp('clip-on-tie')
        tiePropTrack = Sequence(
                        getPropAppearTrack(
                            tie,
                            suit.getRightHand(),
                            posPoints,
                            0.25,
                            scale,
                            scaleUpTime=0.25,
                            poseExtraArgs=['clip-on-tie', 0],
                            blendType='easeIn',
                        )
                    )
        tiePropTrack.append(
                            ActorInterval(tie, 'clip-on-tie', duration=throwDelay, startTime=1.1)
                        )
        tiePropTrack.append(Wait(0.50))
        tiePropTrack.append(Func(battle.movie.needRestoreRenderProp, tie))
        tiePropTrack.append(Func(tie.wrtReparentTo, render))
        tiePropTrack.append(Func(tie.setHpr, Point3(0, -90, 0)))
        if dmg > 0:
            tiePropTrack.append(Parallel(
                ProjectileInterval(
                    tie, endPos=__toonFacePoint(toon), duration=0.3, gravityMult=-5.0,
                ),
                LerpHprInterval(tie, 0.3, (110, 160, 0)),
            ))
        else:
            startH, endH = 180, 280
            yoffset = random.randint(0, 20) / 10.0
            xoffset = random.randint(-7, 7) / 10.0
            tiePropTrack.append(Parallel(
                ProjectileInterval(
                    tie, endPos=__toonGroundPoint(attack, toon, 0.1) + Vec3(0, 4 + yoffset, 0), duration=0.5, gravityMult=4.0,
                ),
                LerpHprInterval(tie, 0.5, (startH, 270, 0)),
            ))
            tiePropTrack.append(Parallel(
                ProjectileInterval(
                    tie, endPos=__toonGroundPoint(attack, toon, 0.1) + Vec3(xoffset, 3.5 + yoffset, 0), duration=0.15, gravityMult=1.0,
                ),
                LerpHprInterval(tie, 0.30, (endH + random.randint(-30, 30), 270, 45), blendType='easeOut'),
                Wait(0.60),
            ))
            tiePropTrack.append(LerpScaleInterval(tie, duration=0.30, scale=MovieUtil.PNT3_NEARZERO, blendType='easeIn'))
        tiePropTrack.append(Func(tie.removeNode))
        tiePropTracks.append(tiePropTrack)
    soundTrack = getSoundTrack('LB_evidence_miss.ogg', node=suit)
    toonTrack = getToonTracks(attack, damageDelay, ['slip-backward'], dodgeDelay, ['neutral'])
    throwSound = getSoundTrack('SA_powertie_throw.ogg', delay=throwDelay + 1.05, node=suit)
    return Parallel(suitTrack, toonTrack, tiePropTracks, throwSound)


def doSandTrap(attack):
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.3
    dodgeDelay = 0.25
    suitTrack = getSuitTrack(attack)
    damageAnims = [['melt'], ['jump', 1.5, 0.4]]
    puddleTracks = Parallel()
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay,
                               dodgeAnimNames=['sidestep'])
    soundTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        sandTrap = globalPropPool.getProp('quicksand')
        sandTrap.setHpr(Point3(120, 0, 0))
        sandTrap.setScale(0.01)
        puddleTracks.append(Sequence(
            Func(battle.movie.needRestoreRenderProp, sandTrap),
            Wait(damageDelay - 0.7),
            Func(sandTrap.reparentTo, battle),
            Func(sandTrap.setPos, toon.getPos(battle)),
            LerpScaleInterval(sandTrap, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO),
            Wait(0.3 if dmg == 0 else 3.2),
            LerpFunctionInterval(sandTrap.setAlphaScale, fromData=1, toData=0, duration=0.8),
            Func(sandTrap.removeNode)
        ))
        soundTracks.append(getSoundTrack('TL_quicksand.ogg', delay=0.5, duration=0.67 if dmg == 0 else 0.0, node=toon))

    return Parallel(suitTrack, toonTracks, soundTracks, puddleTracks)

def doFiveOClockShadow(attack):
    battle = attack['battle']
    targets = attack['target']
    suitTrack = getSuitTrack(attack)
    clockPropTracks = Parallel()
    for t in targets:
        toon = t['toon']
        clock = globalPropPool.getProp('clock')
        hourHand = clock.find('**/hour_hand')
        minuteHand = clock.find('**/minute_hand')
        x, y, z = toon.getPos(battle)
        clockPosPoints = [Point3(x, y, z + 0.01), VBase3(toon.getH(), 90, 0)]
        clockPropTrack = Sequence(
            getPropAppearTrack(clock, battle, clockPosPoints, 0.0, scaleUpPoint=Point3(1.0, 0.01, 1.0), scaleUpTime=1.0),
            Parallel(
                LerpHprInterval(minuteHand, 5.0, VBase3(0, 0, -1800)),
                LerpHprInterval(hourHand, 5.0, VBase3(0, 0, -150))
            ),
            Func(base.playSfx, globalBattleSoundCache.getSound('telephone_ring.ogg'), node=clock),
            Wait(0.4),
            LerpColorScaleInterval(clock, 1.0, Vec4(0.0, 0.0, 0.0, 1.0)),
            Wait(0.3 if t['hp'] == 0 else 3.9),
            LerpFunctionInterval(clock.setAlphaScale, duration=0.8, fromData=1, toData=0),
            Func(clock.removeNode)
        )
        clockPropTracks.append(clockPropTrack)

    damageAnims = [['melt'], ['jump', 1.5, 0.4]]
    toonTracks = getToonTracks(attack, damageDelay=7.1, splicedDamageAnims=damageAnims, dodgeDelay=6.05, dodgeAnimNames=['sidestep'])
    return Parallel(suitTrack, clockPropTracks, toonTracks)

def doDisassemble(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    suitTrack = Sequence(Wait(1.0), getSuitAnimTrack(attack))
    sprayEffect = BattleParticles.createParticleEffect('ReOrgSprayNew')
    desk = loader.loadModel('phase_3.5/models/modules/desk_only')
    desk.reparentTo(battle)
    desk.setPos(suit, 2.5, 3.5, 1.0)
    desk.setHpr(suit, 0, 0, 0)
    desk.setScale(0.01)
    desk.setTransparency(1)
    desk.setAlphaScale(1)

    laptop = globalPropPool.getProp('ttht_m_ene_techbotLaptop')
    laptop.reparentTo(desk)
    laptop.setPos(-2.0, 1.5, 2.5)
    laptop.setHpr(0, 0, 0)
    laptop.setScale(1.75)

    deskTrack = Sequence(
        LerpScaleInterval(
            desk,
            1.0,
            Point3(1.5, 1.5, 1.5),
            startScale=Point3(0.01, 0.01, 0.01)
        ),

        SoundInterval(
            base.loader.loadSfx('phase_5/audio/sfx/asfhdfha.ogg'),
            duration=0.75,
            node=desk
        ),

        Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/asfhafhsdh.ogg'), node=desk),

        Wait(1.0),

        LerpFunctionInterval(desk.setAlphaScale, fromData=1, toData=0, duration=1.0),

        Func(cleanupBashDesk, desk, laptop)
    )

    laptopTrack = Sequence(
        Wait(0.2),
        ActorInterval(laptop, 'ttht_m_ene_techbotLaptop', playRate=1.5)
    )

    toonTracks = getToonTracks(
        attack,
        damageDelay=1.5,
        splicedDamageAnims=[['slip-backward']],
        dodgeDelay=1.0,
        splicedDodgeAnims=[['jump']]
    )

    soundTrack = getSoundTrack('tt_s_ara_cmg_itemHitsFloor.ogg', delay=1.5, node=suit)

    sprayEffects = BattleParticles.createParticleEffect('ReOrgSprayNew')
    BattleParticles.loadParticles()
    BattleParticles.setEffectTexture(sprayEffects, 'snow-particle',
                                        color=Vec4(1, 0, 0, 1))
    partTrack = getPartTrack(sprayEffects, 1.5, 3.0, [sprayEffects, toon, 0], softStop=-1)
    if dmg > 0:
        headParts = toon.getHeadParts()
        headTracks = Parallel()
        for partNum in xrange(0, headParts.getNumPaths()):
            part = headParts.getPath(partNum)
            x = part.getX()
            y = part.getY()
            z = part.getZ()
            h = part.getH()
            p = part.getP()
            r = part.getR()
            headTracks.append(Sequence(Wait(2), LerpPosInterval(part, 0.1, Point3(x - 0.2, y, z - 0.03)),
                                       LerpPosInterval(part, 0.1, Point3(x + 0.4, y, z - 0.03)),
                                       LerpPosInterval(part, 0.1, Point3(x - 0.4, y, z - 0.03)),
                                       LerpPosInterval(part, 0.1, Point3(x + 0.4, y, z - 0.03)),
                                       LerpPosInterval(part, 0.1, Point3(x - 0.2, y, z - 0.04)),
                                       LerpPosInterval(part, 0.25, Point3(x, y, z + 2.2)),
                                       LerpHprInterval(part, 0.4, VBase3(360, 0, 180)),
                                       LerpPosInterval(part, 0.3, Point3(x, y, z + 3.1)),
                                       LerpPosInterval(part, 0.15, Point3(x, y, z + 0.3)), Wait(0.15),
                                       LerpHprInterval(part, 0.6, VBase3(-745, 0, 180), startHpr=VBase3(0, 0, 180)),
                                       LerpHprInterval(part, 0.8, VBase3(25, 0, 180), startHpr=VBase3(0, 0, 180)),
                                       LerpPosInterval(part, 0.15, Point3(x, y, z + 1)),
                                       LerpHprInterval(part, 0.3, VBase3(h, p, r)), Wait(0.2),
                                       LerpPosInterval(part, 0.1, Point3(x, y, z)), Wait(0.9)))

        def getChestTrack(part, attackDelay=1):
            origScale = part.getScale()
            return Sequence(Wait(2), LerpHprInterval(part, 1.1, VBase3(180, 0, 0)), Wait(1.1),
                            LerpHprInterval(part, 1.1, part.getHpr()))

        chestTracks = Parallel()
        arms = toon.findAllMatches('**/arms')
        sleeves = toon.findAllMatches('**/sleeves')
        hands = toon.findAllMatches('**/hands')
        for partNum in xrange(0, arms.getNumPaths()):
            chestTracks.append(getChestTrack(arms.getPath(partNum)))
            chestTracks.append(getChestTrack(sleeves.getPath(partNum)))
            chestTracks.append(getChestTrack(hands.getPath(partNum)))

    damageAnims = [['neutral',
                    0.01,
                    0.01,
                    0.5], ['juggle',
                           0.01,
                           0.01,
                           1.48], ['think', 0.01, 2.28]]
    dodgeAnims = []
    dodgeAnims.append(['think',
                       0.01,
                       0,
                       0.6])
    toonTrack = getToonTrack(attack, damageDelay=2, splicedDamageAnims=damageAnims, dodgeDelay=0.01,
                             dodgeAnimNames=['duck'])
    if dmg > 0:
        return Parallel(suitTrack, partTrack, deskTrack, laptopTrack, toonTracks, headTracks, chestTracks)
    else:
        return Parallel(suitTrack, partTrack, deskTrack, laptopTrack, toonTracks)


def doPoundKey(attack):
    suit = attack['suit']
    battle = attack['battle']
    phone = globalPropPool.getProp('phone')
    receiver = globalPropPool.getProp('receiver')
    BattleParticles.loadParticles()
    particleEffects = []
    for t in attack['target']:
        particleEffect = BattleParticles.createParticleEffect('PoundKey')
        BattleParticles.setEffectTexture(particleEffect, 'poundsign', color=Vec4(0, 0, 0, 1))
        particleEffects.append(particleEffect)

    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    partTracks = getPartTracks(attack, particleEffects, 1.1, 4.0, 0, softStop=-2)
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        phonePosPoints = [Point3(-0.26011560693641655, 0.26011560693641655, -0.1), VBase3(180, 180, 0)]
        receiverPosPoints = [Point3(0, -0.43352601156069426, -0.8670520231213885), VBase3(90, 0, 0)]
    if suitType == 'b':
        phonePosPoints = [Point3(0.5202312138728296, 0.26011560693641655, 0), VBase3(180, 180, 0)]
        receiverPosPoints = [Point3(-0.23, 0, -0.11), VBase3(5.939, 2.763, -177.591)]
    if suitType == 'c':
        phonePosPoints = [Point3(0.5202312138728296, 0.26011560693641655, 0), VBase3(180, 180, 0)]
        receiverPosPoints = [Point3(-0.23, 0, -0.11), VBase3(5.939, 2.763, -177.591)]
    propTrack = Sequence(Func(__showProp, phone, suit.getLeftHand(), *phonePosPoints), Func(__showProp, receiver, suit.getLeftHand(), *receiverPosPoints), LerpScaleInterval(phone, 0.5, MovieUtil.PNT3_ONE, MovieUtil.PNT3_NEARZERO), Wait(0.24), Func(receiver.wrtReparentTo, suit.getRightHand()), LerpPosHprInterval(receiver, 0.0001, Point3(-0.45, 0.48, -0.62), VBase3(-87.47, -18.21, 7.82)), Wait(2.14), Func(receiver.wrtReparentTo, phone), Wait(0.62), LerpScaleInterval(phone, 0.5, MovieUtil.PNT3_NEARZERO), Func(MovieUtil.removeProps, [receiver, phone]))
    toonTracks = getToonTracks(attack, 2.0, ['cringe'], 1.3, ['sidestep'])
    soundTrack = getSoundTrack('SA_hangup.ogg', delay=.5, node=suit)
    return Parallel(suitTrack, toonTracks, propTrack, partTracks, soundTrack)


def doShred(attack):
    suit = attack['suit']
    battle = attack['battle']
    paper = globalPropPool.getProp('shredder-paper')
    shredder = globalPropPool.getProp('shredder')
    particleEffect = BattleParticles.createParticleEffect('Shred')
    suitTrack = getSuitTrack(attack)
    partTrack = getPartTrack(particleEffect, 3.5, 3.9, [particleEffect, suit, 0], softStop=-2)
    paperPosPoints = [Point3(0.59, -0.31, 0.81), VBase3(79.224, 32.576, -179.449)]
    paperPropTrack = getPropTrack(paper, suit.getRightHand(), paperPosPoints, 2.4, 1e-05, scaleUpTime=0.2, anim=1, propName='shredder-paper', animDuration=1.5, animStartTime=2.8)
    shredderPosPoints = [Point3(0, 0, -0.5), VBase3(-90.0, -53.77, -0.0)]
    shredderPropTrack = getPropTrack(shredder, suit.getLeftHand(), shredderPosPoints, 1, 3, scaleUpPoint=Point3(4.81, 4.81, 4.81))
    toonTrack = getToonTrack(attack, suitTrack.getDuration() - 1.1, ['conked'], suitTrack.getDuration() - 3.1, ['sidestep'])
    soundTrack = getSoundTrack('SA_shred.ogg', delay=3.4, node=suit)
    return Parallel(suitTrack, paperPropTrack, shredderPropTrack, partTrack, toonTrack, soundTrack)


def doSongAndDance(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = getSuitAnimTrack(attack)
    toonTracks = getToonTracks(attack, 4.1, ['cringe'], 4.223, ['applause'])
    soundTrack = getSoundTrack('AA_heal_happydance.ogg', delay=.01, node=suit)
    return Parallel(suitTrack, toonTracks, soundTrack)


def doFillWithLead(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    pencil = globalPropPool.getProp('pencil')
    sharpener = globalPropPool.getProp('sharpener')
    BattleParticles.loadParticles()
    sprayEffects = []
    for t in targets:
        sprayEffect = BattleParticles.createParticleEffect(file='fillWithLeadSpray')
        BattleParticles.setEffectTexture(sprayEffect, 'roll-o-dex', color=Vec4(0, 0, 0, 1))
        sprayEffects.append(sprayEffect)

    suitTrack = getSuitTrack(attack)
    sprayTracks = getPartTracks(attack, sprayEffects, 2.5, 1.9, 0)
    pencilPosPoints = [Point3(-0.29, -0.33, -0.13), VBase3(160.565, -11.653, -169.244)]
    pencilPropTrack = getPropTrack(pencil, suit.getRightHand(), pencilPosPoints, 0.7, 3.2, scaleUpTime=0.2)
    sharpenerPosPoints = [Point3(0.0, 0.0, -0.03), MovieUtil.PNT3_ZERO]
    sharpenerPropTrack = getPropTrack(sharpener, suit.getLeftHand(), sharpenerPosPoints, 1.3, 2.3, scaleUpPoint=MovieUtil.PNT3_ONE)
    damageAnims = []
    damageAnims.append(['conked',
     suitTrack.getDuration() - 1.5,
     1e-05,
     1.4])
    damageAnims.append(['conked',
     1e-05,
     0.7,
     0.7])
    damageAnims.append(['conked',
     1e-05,
     0.7,
     0.7])
    damageAnims.append(['conked', 1e-05, 1.4])
    toonTracks = getToonTracks(attack, splicedDamageAnims=damageAnims, dodgeDelay=suitTrack.getDuration() - 3.1, dodgeAnimNames=['sidestep'], showDamageExtraTime=4.5, showMissedExtraTime=1.6)
    headTracks = Parallel()
    torsoTracks = Parallel()
    legsTracks = Parallel()
    colorTracks = Parallel()
    partDelay = 3.5
    partIvalDelay = 0.7
    partDuration = 2.0

    def colorParts(parts):
        track = Parallel()
        for partNum in xrange(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.setColorScale, Vec4(0, 0, 0, 1)))

        return track

    def resetParts(parts):
        track = Parallel()
        for partNum in xrange(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.clearColorScale))

        return track

    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        headSmotherEffect = BattleParticles.createParticleEffect(file='fillWithLeadSmother')
        torsoSmotherEffect = BattleParticles.createParticleEffect(file='fillWithLeadSmother')
        legsSmotherEffect = BattleParticles.createParticleEffect(file='fillWithLeadSmother')
        BattleParticles.setEffectTexture(headSmotherEffect, 'roll-o-dex', color=Vec4(0, 0, 0, 1))
        BattleParticles.setEffectTexture(torsoSmotherEffect, 'roll-o-dex', color=Vec4(0, 0, 0, 1))
        BattleParticles.setEffectTexture(legsSmotherEffect, 'roll-o-dex', color=Vec4(0, 0, 0, 1))
        animal = toon.style.getAnimal()
        bodyScale = ToontownGlobals.toonBodyScales[animal]
        headEffectHeight = __toonFacePoint(toon).getZ()
        legsHeight = ToontownGlobals.legHeightDict[toon.style.legs] * bodyScale
        torsoEffectHeight = ToontownGlobals.torsoHeightDict[toon.style.torso] * bodyScale / 2 + legsHeight
        legsEffectHeight = legsHeight / 2
        effectX = headSmotherEffect.getX()
        effectY = headSmotherEffect.getY()
        headSmotherEffect.setPos(effectX, effectY - 1.5, headEffectHeight)
        torsoSmotherEffect.setPos(effectX, effectY - 1, torsoEffectHeight)
        legsSmotherEffect.setPos(effectX, effectY - 0.6, legsEffectHeight)
        if dmg > 0:
            headTracks.append(getPartTrack(headSmotherEffect, partDelay, partDuration, [headSmotherEffect, toon, 0], softStop=-1))
            torsoTracks.append(getPartTrack(torsoSmotherEffect, partDelay + partIvalDelay, partDuration, [torsoSmotherEffect, toon, 0], softStop=-1))
            legsTracks.append(getPartTrack(legsSmotherEffect, partDelay + partIvalDelay * 2, partDuration, [legsSmotherEffect, toon, 0], softStop=-1))
            colorTrack = Sequence()
            headParts = toon.getHeadParts()
            torsoParts = toon.getTorsoParts()
            legsParts = toon.getLegsParts()
            colorTrack.append(Wait(partDelay + 0.2))
            colorTrack.append(Func(battle.movie.needRestoreColor))
            colorTrack.append(colorParts(headParts))
            colorTrack.append(Wait(partIvalDelay))
            colorTrack.append(colorParts(torsoParts))
            colorTrack.append(Wait(partIvalDelay))
            colorTrack.append(colorParts(legsParts))
            colorTrack.append(Wait(2.5))
            colorTrack.append(resetParts(headParts))
            colorTrack.append(resetParts(torsoParts))
            colorTrack.append(resetParts(legsParts))
            colorTrack.append(Func(battle.movie.clearRestoreColor))
            colorTracks.append(colorTrack)

    return Parallel(suitTrack, pencilPropTrack, sharpenerPropTrack, sprayTracks, headTracks, torsoTracks, legsTracks, colorTracks, toonTracks)

def doBeguile(attack):
    suit = attack['suit']
    targets = attack['target']
    hitAtleastOneToon = False
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = True

    if base.config.GetBool('want-new-cogs', False):
        head = suit.find('**/to_head')
        if head.isEmpty():
            head = suit.find('**/joint_head')
    else:
        head = suit.find('**/joint_head')
    sparkle = globalPropPool.getProp('smile')
    suitSplicedAnims = [['glower', 0.01, 0.01, 1.5],
     ['glower', 2.0, 1.51]]
    suitTrack = Sequence(getSuitAnimTrack(attack))
    if suit.dna.name == 'videog':
        sparklePosPoints = [Point3(-0.1, 0.25, -1.5), VBase3(360, 0, 0)]
    elif suit.dna.name == 'hustle':
        sparklePosPoints = [Point3(-0.05, 0.65, -1.5), VBase3(335, 0, 0)]
    else:
        sparklePosPoints = [Point3(-0.1, 0.35, -1.5), VBase3(335, 0, 0)]
    sparklePropTrack = Sequence(Wait(1.0))
    sparklePropTrack.append(Func(__showProp, sparkle, head, sparklePosPoints[0], sparklePosPoints[1]))
    sparklePropTrack.append(Func(sparkle.find('**/scale_joint_sign').hide))
    sparklePropTrack.append(ActorInterval(sparkle, 'smile', startFrame=39))
    sparklePropTrack.append(Func(MovieUtil.removeProp, sparkle))
    dodgeAnims = [['duck', 1e-06, 0.8]]
    toonTracks = getToonTracks(attack, damageDelay=2.1, damageAnimNames=['cringe'], dodgeDelay=1.7, splicedDodgeAnims=dodgeAnims)
    soundTrack = getSoundTrack('ttr_s_ene_bat_beguile%s.ogg' % ('' if hitAtleastOneToon else 'Miss'), node=suit)
    return Parallel(suitTrack, sparklePropTrack, toonTracks, soundTrack)

def doHostileTakeover(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    BattleParticles.loadParticles()
    rainEffect = BattleParticles.createParticleEffect(file='hostileTakeover')
    rainEffect2 = BattleParticles.createParticleEffect(file='hostileTakeover')
    rainEffect3 = BattleParticles.createParticleEffect(file='hostileTakeover')
    cloud = globalPropPool.getProp('stormcloud')
    suitType = getSuitBodyType(attack['suitName'])
    partDelay = 1.2
    damageDelay = 4.5
    dodgeDelay = 3.3
    suitTrack = getSuitTrack(attack, delay=0.9)
    initialCloudHeight = suit.height + 3
    cloudPosPoints = [Point3(0, 3, initialCloudHeight), VBase3(180, 0, 0)]
    cloudPropTrack = Sequence()
    cloudPropTrack.append(Func(cloud.pose, 'stormcloud', 0))
    cloudPropTrack.append(getPropAppearTrack(cloud, suit, cloudPosPoints, 1e-06, Point3(3, 3, 3), scaleUpTime=0.7))
    cloudPropTrack.append(Func(battle.movie.needRestoreRenderProp, cloud))
    cloudPropTrack.append(Func(cloud.wrtReparentTo, render))
    targetPoint = __toonFacePoint(toon)
    targetPoint.setZ(targetPoint[2] + 3)
    cloudPropTrack.append(Wait(1.1))
    cloudPropTrack.append(LerpPosInterval(cloud, 1, pos=targetPoint))
    cloudPropTrack.append(Wait(partDelay))
    cloudPropTrack.append(Parallel(Sequence(ParticleInterval(rainEffect, cloud, worldRelative=0, duration=2.1, cleanup=True)), Sequence(Wait(0.1), ParticleInterval(rainEffect2, cloud, worldRelative=0, duration=2.0, cleanup=True)), Sequence(Wait(0.1), ParticleInterval(rainEffect3, cloud, worldRelative=0, duration=2.0, cleanup=True)), Sequence(ActorInterval(cloud, 'stormcloud', startTime=3, duration=0.1), ActorInterval(cloud, 'stormcloud', startTime=1, duration=2.3))))
    cloudPropTrack.append(Wait(0.4))
    cloudPropTrack.append(LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO))
    cloudPropTrack.append(Func(MovieUtil.removeProp, cloud))
    cloudPropTrack.append(Func(battle.movie.clearRenderProp, cloud))
    damageAnims = [['cringe',
      0.01,
      0.4,
      0.8], ['duck', 1e-06, 1.6]]
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'], showMissedExtraTime=1.1)
    soundTrack = getSoundTrack('SA_liquidate.ogg', delay=2.6, node=suit)
    #soundTrack = getSoundTrack('ttr_s_ene_bat_hostileTakeover.ogg', delay=2.6, node=suit)
    return Parallel(suitTrack, toonTrack, cloudPropTrack, soundTrack)


def doNickelAndDime(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.7
    hitAtleastOneToon = False
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = True

    particleEffect = BattleParticles.createParticleEffect('NickelAndDime') 
    waterfallEffect = BattleParticles.createParticleEffect(file='nickelDimeWaterfall')
    suitTrack = getSuitAnimTrack(attack)
    partTrack = getPartTrack(particleEffect, 1.0, 2.9, [particleEffect, suit, 0], softStop=-2)
    waterfallTrack = getPartTrack(waterfallEffect, 0.8, 2.9, [waterfallEffect, suit, 0], softStop=-2)
    damageAnims = [['slip-forward']]
    dodgeAnims = []
    dodgeAnims.append(['jump',
     0.01,
     0,
     0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.3, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, damageAnimNames=['slip-forward'], dodgeDelay=0.91, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.0)
    soundTrack = getSoundTrack('ttr_s_ene_bat_nickelAndDime%s.ogg' % ('' if hitAtleastOneToon else ''), node=suit)
    return Parallel(suitTrack, partTrack, waterfallTrack, soundTrack, toonTracks)


def doQuash(attack):
    targets = attack['target']
    suitTrack = getSuitAnimTrack(attack)
    partTracks = Parallel()
    toonTracks = getToonTracks(attack, 1.6, ['slip-forward'], 1e-06, ['duck'])
    soundTracks = Parallel()
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        if dmg > 0:
            particleEffect = BattleParticles.createParticleEffect(file='quash')
            partTrack = getPartTrack(particleEffect, 0.01, 3.5, [particleEffect, toon, 0], softStop=-1)
            partTracks.append(partTrack)

    if hitAtleastOneToon > 0:
        soundTracks.append(getSoundTrack('ttr_s_ene_bat_quash.ogg', node=toon))

    return Parallel(suitTrack, partTracks, toonTracks, soundTracks)


def doFountainPen(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    pen = globalPropPool.getProp('pen')

    def getPenTip(pen = pen):
        tip = pen.find('**/joint_toSpray')
        return tip.getPos(render)

    suitTrack = getSuitTrack(attack)
    propTrack = Sequence(Wait(0.01), Func(__showProp, pen, suit.getRightHand(), MovieUtil.PNT3_ZERO), LerpScaleInterval(pen, 0.5, Point3(1.5, 1.5, 1.5)), Wait(1.05))
    sprayTracks = Parallel()
    for t in targets:
        toon = t['toon']
        hitPoint = lambda toon = toon: __toonFacePoint(toon)
        missPoint = lambda prop = pen, toon = toon: __toonMissPoint(prop, toon, 0, parent=render)
        hitSprayTrack = MovieUtil.getSprayTrack(battle, VBase4(0, 0, 0, 1), getPenTip, hitPoint, 0.2, 0.2, 0.2, horizScale=0.1, vertScale=0.1)
        missSprayTrack = MovieUtil.getSprayTrack(battle, VBase4(0, 0, 0, 1), getPenTip, missPoint, 0.2, 0.2, 0.2, horizScale=0.1, vertScale=0.1)
        if t['hp'] > 0:
            sprayTracks.append(hitSprayTrack)
        else:
            sprayTracks.append(missSprayTrack)
    
    propTrack.append(sprayTracks)
    propTrack += [LerpScaleInterval(pen, 0.5, MovieUtil.PNT3_NEARZERO), Func(MovieUtil.removeProp, pen)]

    def prepSplash(splash, targetPoint):
        splash.reparentTo(render)
        splash.setPos(targetPoint)
        scale = splash.getScale()
        splash.setBillboardPointWorld()
        splash.setScale(scale)

    splashTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        if dmg > 0:
            splash = globalPropPool.getProp('splash-from-splat')
            splash.setColor(0, 0, 0, 1)
            splash.setScale(0.15)
            splashTrack = Sequence(Func(battle.movie.needRestoreRenderProp, splash), Wait(1.65), Func(prepSplash, splash, __toonFacePoint(toon)), ActorInterval(splash, 'splash-from-splat'), Func(MovieUtil.removeProp, splash), Func(battle.movie.clearRenderProp, splash))
            headParts = toon.getHeadParts()
            splashTrack.append(Func(battle.movie.needRestoreColor))
            for partNum in xrange(0, headParts.getNumPaths()):
                nextPart = headParts.getPath(partNum)
                splashTrack.append(Func(nextPart.setColorScale, Vec4(0, 0, 0, 1)))

            splashTrack.append(Func(MovieUtil.removeProp, splash))
            splashTrack.append(Wait(2.6))
            for partNum in xrange(0, headParts.getNumPaths()):
                nextPart = headParts.getPath(partNum)
                splashTrack.append(Func(nextPart.clearColorScale))

            splashTrack.append(Func(battle.movie.clearRestoreColor))
            splashTracks.append(splashTrack)

    penSpill = BattleParticles.createParticleEffect(file='penSpill')
    penSpill.setPos(getPenTip())
    penSpillTrack = getPartTrack(penSpill, 1.4, 0.7, [penSpill, pen, 0])
    toonTracks = getToonTracks(attack, 1.81, ['conked'], dodgeDelay=0.11, splicedDodgeAnims=[['duck', 0.01, 0.6]], showMissedExtraTime=1.66)
    soundTrack = getSoundTrack('SA_fountain_pen.ogg', delay=1.6, node=suit)
    return Parallel(suitTrack, toonTracks, propTrack, soundTrack, penSpillTrack, splashTracks)

def makeZapBeamTrack(battle, coil, suit, tDelay, duration):
    beam = globalPropPool.getProp('zap_beam')
    beam.loop('zap_beam')
    beam.setTransparency(1)
    beam.setTwoSided(True)
    beam.hide()
    beam.setH(90)

    beamStageData = []

    def getBeamGeomStages(beam):
        data = []

        for geomNp in beam.findAllMatches('**/+GeomNode'):
            stages = geomNp.findAllTextureStages()

            for i in xrange(stages.getNumTextureStages()):
                ts = stages.getTextureStage(i)

                tex = geomNp.getTexture(ts)
                if tex:
                    tex.setWrapU(tex.WMRepeat)
                    tex.setWrapV(tex.WMRepeat)

                data.append((geomNp, ts))

        return data

    def setupBeam():
        startPos = coil.getPos(render) + Point3(0, 0, coil.getHeight() + 1)
        endPos = suit.getPos(render) + Point3(0, 0, suit.getHeight() * .5)

        beam.reparentTo(render)
        beam.show()
        beam.setPos(startPos)
        beam.headsUp(endPos)

        diff = endPos - startPos
        flatDist = (Point3(endPos[0], endPos[1], startPos[2]) - startPos).length()

        if flatDist > 0.01:
            pitch = math.degrees(math.atan2(diff[2], flatDist))
        else:
            pitch = 0.0

        # If this angles the wrong way, change + pitch to - pitch.
        beam.setP(beam.getP() + pitch)

        dist = diff.length()
        beam.setScale(1, dist * 10, 1)
        beam.setColorScale(1, 1, 1, 1)

        del beamStageData[:]
        beamStageData.extend(getBeamGeomStages(beam))

        for geomNp, ts in beamStageData:
            if not geomNp.isEmpty():
                geomNp.setTexOffset(ts, 0, 0)

    def phaseZap(t):
        offset = t * 14.0

        for geomNp, ts in beamStageData:
            if not geomNp.isEmpty():
                # Keep this axis if it matches your working direction.
                # Swap to (offset, 0), (-offset, 0), or (0, offset) if needed.
                geomNp.setTexOffset(ts, offset, 0)

    def cleanupBeam():
        for geomNp, ts in beamStageData:
            if not geomNp.isEmpty():
                geomNp.clearTexTransform(ts)

        if beam and not beam.isEmpty():
            try:
                beam.stop('zap_beam')
            except:
                pass

            try:
                MovieUtil.removeProp(beam)
            except:
                beam.removeNode()

    return Sequence(
        Wait(tDelay),
        Func(setupBeam),

        Parallel(
            LerpFunctionInterval(
                phaseZap,
                duration,
                fromData=0.0,
                toData=1.0
            ),

            Sequence(
                Wait(max(0.0, duration - 0.2)),
                LerpColorScaleInterval(
                    beam,
                    0.2,
                    Vec4(1, 1, 1, 0),
                    startColorScale=Vec4(1, 1, 1, 1)
                )
            )
        ),

        Wait(0.2),
        Func(cleanupBeam)
    )


def doElectrostaticEnergy(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    suitTrack = Sequence(Wait(1.0), getSuitAnimTrack(attack))
    targets = attack['target']
    cagePropTracks = Parallel()
    smokeTracks = Parallel()
    zapSfx = loader.loadSfx('phase_5/audio/sfx/AA_cog_shock.ogg')
    zapTrack = Sequence(Wait(2.0), SoundInterval(zapSfx, volume=0.6))
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        toonPos = toon.getPos(battle)
        smoke = loader.loadModel('phase_4/models/props/test_clouds')
        smoke.setColor(0.8, 0.7, 0.5, 1)
        smoke.setBillboardPointEye()
        smokeTrack = Sequence(Wait(2), Func(smoke.reparentTo, toon),
                              Parallel(LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
                                       LerpColorScaleInterval(smoke, 1, Vec4(1, 1, 1, 0))),
                              Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale),
                              Func(smoke.removeNode))
        cage = loader.loadModel('phase_5/models/props/lightning')
        cage.setColorScale(0, 0.961, 1, 1)
        cagePosition = LerpHprInterval(cage, 0, Point3(180, 0, 0))
        # cage.setH(90)
        # cage.setPosHpr(0, 0, 0, 180, 0, 0)
        toonPos = toon.getPos(battle)
        y = toonPos.getY()
        if dmg == 0:
            y -= 5
        cagePos = [Point3(toonPos.getX(), y, 100.0), toon.getHpr(battle)]
        cagePropTrack = Sequence(makeZapBeamTrack(
                battle,
                suit,
                toon,
                tDelay=2,
                duration=2
            ))
        cagePropTracks.append(cagePropTrack)
        smokeTracks.append(smokeTrack)
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    damageAnims = [['slip-forward', 0.0001, 0.5]]
    toonTrack = getToonTracks(attack, damageDelay=2, splicedDamageAnims=damageAnims, dodgeDelay=1.75, dodgeAnimNames=['sidestep'], splicedDodgeAnims=[], showDamageExtraTime=0)
    return Parallel(suitTrack, zapTrack, cagePropTracks, smokeTracks, toonTrack)

def doRubOut(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    pad = globalPropPool.getProp('pad')
    pencil = globalPropPool.getProp('pencil')
    suitTrack = getSuitTrack(attack)
    padPosPoints = [Point3(-0.66, 0.81, -0.06), VBase3(14.93, -2.29, 180.0)]
    padPropTrack = getPropTrack(pad, suit.getLeftHand(), padPosPoints, 0.5, 2.57)
    pencilPosPoints = [Point3(0.04, -0.38, -0.1), VBase3(-170.223, -3.762, -62.929)]
    pencilPropTrack = getPropTrack(pencil, suit.getRightHand(), pencilPosPoints, 0.5, 2.57)
    toonTracks = getToonTracks(attack, 2.2, ['conked'], 2.0, ['jump'])

    def hideParts(parts):
        track = Parallel()
        for partNum in xrange(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.setTransparency, 1))
            track.append(LerpFunctionInterval(nextPart.setAlphaScale, fromData=1, toData=0, duration=0.2))

        return track

    def showParts(parts):
        track = Parallel()
        for partNum in xrange(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.clearColorScale))
            track.append(Func(nextPart.clearTransparency))

        return track

    hideTracks = Parallel()
    headTracks = Parallel()
    torsoTracks = Parallel()
    legsTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        headEffect = BattleParticles.createParticleEffect('RubOut', color=toon.style.getHeadColor())
        torsoEffect = BattleParticles.createParticleEffect('RubOut', color=toon.style.getArmColor())
        legsEffect = BattleParticles.createParticleEffect('RubOut', color=toon.style.getLegColor())
        headParts = toon.getHeadParts()
        torsoParts = toon.getTorsoParts()
        legsParts = toon.getLegsParts()
        animal = toon.style.getAnimal()
        bodyScale = ToontownGlobals.toonBodyScales[animal]
        headEffectHeight = __toonFacePoint(toon).getZ()
        legsHeight = ToontownGlobals.legHeightDict[toon.style.legs] * bodyScale
        torsoEffectHeight = ToontownGlobals.torsoHeightDict[toon.style.torso] * bodyScale / 2 + legsHeight
        legsEffectHeight = legsHeight / 2
        effectX = headEffect.getX()
        effectY = headEffect.getY()
        headEffect.setPos(effectX, effectY - 1.5, headEffectHeight)
        torsoEffect.setPos(effectX, effectY - 1, torsoEffectHeight)
        legsEffect.setPos(effectX, effectY - 0.6, legsEffectHeight)
        partDelay = 2.5
        if dmg > 0:
            headTracks.append(getPartTrack(headEffect, partDelay + 0, 1.5, [headEffect, toon, 0], softStop=-1))
            torsoTracks.append(getPartTrack(torsoEffect, partDelay + 1.1, 1.5, [torsoEffect, toon, 0], softStop=-1))
            legsTracks.append(getPartTrack(legsEffect, partDelay + 2.2, 1.5, [legsEffect, toon, 0], softStop=-1))
            hideTracks.append(Sequence(
                Wait(2.2),
                Func(battle.movie.needRestoreColor),
                hideParts(headParts),
                Wait(0.4),
                hideParts(torsoParts),
                Wait(0.4),
                hideParts(legsParts),
                Wait(1),
                showParts(headParts),
                showParts(torsoParts),
                showParts(legsParts),
                Func(battle.movie.clearRestoreColor)
            ))

    soundTrack = getSoundTrack('SA_rubout.ogg', delay=1.7, node=suit)
    return Parallel(suitTrack, toonTracks, padPropTrack, pencilPropTrack, soundTrack, hideTracks, headTracks, torsoTracks, legsTracks)

def doDiskScratch(attack):
    suit = attack['suit']
    targets = attack['target']
    pad = loader.loadModel('props/general/models/cc_m_gen_prp_vinyl_disk')
    pad.setScale(.5)
    suitTrack = getSuitAnimTrack(attack)
    padPosPoints = [Point3(-0.564399421128801, 0, -0.13024602026049337), VBase3(90, 90, 0)]
    padPropTrack = getPropTrack(pad, suit.getLeftHand(), padPosPoints, 0.5, 2.57, scaleUpPoint = Point3(.5))
    padPropTrack.append(Func(pad.removeNode))
    toonTrack = getToonTracks(attack, 3.2, ['cringe'], 3.0, ['nothing'])
    oldcolor = render.getColorScale()
    lightingTrack = Sequence(Wait(1), LerpColorScaleInterval(render, 0.5, (0, 0.992, 1, 1)),
                             LerpColorScaleInterval(render, 2.5, (0, 0.992, 1, 1)),
                             LerpColorScaleInterval(render, 1, (oldcolor)))
    soundTrack = getSoundTrack('SA_rubout.ogg', delay=1.7, node=suit)

    return Parallel(suitTrack, toonTrack, padPropTrack, soundTrack, lightingTrack)


def doFingerWag(attack):
    suit = attack['suit']
    battle = attack['battle']
    BattleParticles.loadParticles()
    particleEffects = []
    for t in attack['target']:
        particleEffect = BattleParticles.createParticleEffect('FingerWag')
        BattleParticles.setEffectTexture(particleEffect, 'blah', color=Vec4(0.55, 0, 0.55, 1))
        suitName = attack['suitName']
        if suit.dna.name == "mm":
            particleEffect.setPos(0.167, 1.0, 1.3)
        elif suit.dna.name == "tm":
            particleEffect.setPos(0, 1.1, suit.getHeight() - 1.2)
        elif suit.dna.name == "tw" or suit.dna.name == "stg":
            particleEffect.setPos(0.167, 1.8, 5)
            particleEffect.setHpr(-90.0, -60.0, 180.0)
        elif suit.dna.name == "p":
            particleEffect.setPos(0.167, 1.4, 3.6)
        elif suit.dna.name == "pp":
            particleEffect.setPos(0.167, 1, 4.1)
        elif suit.dna.name == "pf":
            particleEffect.setPos(0.167, 1.4, 4.65)
        elif suit.dna.name == "bs" or suit.dna.name == "fct":
            particleEffect.setPos(0.167, 1.4, 5.3)
        elif suit.dna.name == "bw":
            particleEffect.setPos(0.167, 2.0, suit.getHeight() - 1.75)
            particleEffect.setP(-110)
        elif suit.dna.name == "sgoat":
            particleEffect.setPos(0.167, 1.9, suit.getHeight() - 2)
            particleEffect.setP(-110)
        elif suit.dna.name == "mouthp":
            particleEffect.setPos(0.167, 2.2, suit.getHeight() - 1.9)
            particleEffect.setP(-110)
        elif suit.dna.name in ["erfit", "cdirector", "videog", "safesupervis"]:
            particleEffect.setPos(0.167, 1.9, suit.getHeight() - 1.9)
            particleEffect.setP(-115)
        else:
            particleEffect.setPos(0, 1.1, suit.getHeight() - 1.2)
        particleEffects.append(particleEffect)

    suitType = getSuitBodyType(attack['suitName'])
    partDelay = 1.3
    damageDelay = 2.7
    dodgeDelay = 1.7
    suitTrack = getSuitTrack(attack)
    partTracks = getPartTracks(attack, particleEffects, partDelay, 3.5, 0, softStop=-2.0)
    toonTracks = getToonTracks(attack, damageDelay, ['slip-backward'], dodgeDelay, ['sidestep'])
    soundTrack = getSoundTrack('SA_finger_wag.ogg', delay=1.3, node=suit)
    return Parallel(suitTrack, toonTracks, partTracks, soundTrack)


def doWriteOff(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    pad = globalPropPool.getProp('pad')
    pencil = globalPropPool.getProp('pencil')
    BattleParticles.loadParticles()
    checkmark = MovieUtil.copyProp(BattleParticles.getParticle('checkmark'))
    checkmark.setBillboardPointEye()
    suitTrack = getSuitTrack(attack)
    padPosPoints = [Point3(-0.25, 1.38, -0.08), VBase3(-19.078, -6.603, -171.594)]
    padPropTrack = getPropTrack(pad, suit.getLeftHand(), padPosPoints, 0.5, 2.57, Point3(1.89, 1.89, 1.89))
    missPoint = lambda checkmark = checkmark, toon = toon: __toonMissPoint(checkmark, toon)
    pencilPosPoints = [Point3(-0.47, 1.08, 0.28), VBase3(21.045, 12.702, -176.374)]
    extraArgsForShowProp = [pencil, suit.getRightHand()]
    extraArgsForShowProp.extend(pencilPosPoints)
    pencilPropTrack = Sequence(Wait(0.5), Func(__showProp, *extraArgsForShowProp), LerpScaleInterval(pencil, 0.5, Point3(1.5, 1.5, 1.5), startScale=Point3(0.01)), Wait(2), Func(battle.movie.needRestoreRenderProp, checkmark), Func(checkmark.reparentTo, render), Func(checkmark.setScale, 1.6), Func(checkmark.setPosHpr, pencil, 0, 0, 0, 0, 0, 0), Func(checkmark.setP, 0), Func(checkmark.setR, 0))
    pencilPropTrack.append(getPropThrowTrack(attack, checkmark, [__toonFacePoint(toon)], [missPoint]))
    pencilPropTrack.append(Func(MovieUtil.removeProp, checkmark))
    pencilPropTrack.append(Func(battle.movie.clearRenderProp, checkmark))
    pencilPropTrack.append(Wait(0.3))
    pencilPropTrack.append(LerpScaleInterval(pencil, 0.5, MovieUtil.PNT3_NEARZERO))
    pencilPropTrack.append(Func(MovieUtil.removeProp, pencil))
    toonTrack = getToonTrack(attack, 3.4, ['slip-forward'], 2.4, ['sidestep'])
    soundTrack = Sequence(Wait(2.3), SoundInterval(globalBattleSoundCache.getSound('SA_writeoff_pen_only.ogg'), duration=0.9, node=suit), SoundInterval(globalBattleSoundCache.getSound('SA_writeoff_ding_only.ogg'), node=suit))
    return Parallel(suitTrack, toonTrack, padPropTrack, pencilPropTrack, soundTrack)


def doRubberStamp(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    suitTrack = getSuitTrack(attack)
    stamp = globalPropPool.getProp('cc_m_prp_bat_rubberStamp')
    pad = globalPropPool.getProp('cc_m_prp_bat_rubberStamp_pad')
    cancelled = __makeCancelledNodePath()
    suitType = getSuitBodyType(attack['suitName'])
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        padPosPoints = [Point3(-0.75, 0, -0.125), VBase3(90, 0, 180)]
    if suitType == 'b':
        padPosPoints = [Point3(-0.75, 0, -0.125), VBase3(90, 0, 180)]
    if suitType == 'c':
        padPosPoints = [Point3(-0.25, 0.25, -0.125), VBase3(90, 0, 180)]
    stampPosPoints = [Point3(-0.08219178082191902, -0.7397260273972606, -0.125), VBase3(90, 0, 90)]
    padPropTrack = getPropTrack(pad, suit.getLeftHand(), padPosPoints, 1e-06, 3.2)
    missPoint = lambda cancelled = cancelled, toon = toon: __toonMissPoint(cancelled, toon)
    propTrack = Sequence(Func(__showProp, stamp, suit.getRightHand(), stampPosPoints[0], stampPosPoints[1]), LerpScaleInterval(stamp, 0.5, Point3(1.2, 1.2, 1.2)), Wait(2.6), Func(battle.movie.needRestoreRenderProp, cancelled), Func(cancelled.reparentTo, render), Func(cancelled.setScale, 0.6), Func(cancelled.setPosHpr, stamp, 0.81, -1.11, -0.16, 0, 0, 90), Func(cancelled.setP, 0), Func(cancelled.setR, 0))
    propTrack.append(getPropThrowTrack(attack, cancelled, [__toonFacePoint(toon)], [missPoint]))
    propTrack.append(Func(MovieUtil.removeProp, cancelled))
    propTrack.append(Func(battle.movie.clearRenderProp, cancelled))
    propTrack.append(Wait(0.3))
    propTrack.append(LerpScaleInterval(stamp, 0.5, MovieUtil.PNT3_NEARZERO))
    propTrack.append(Func(MovieUtil.removeProp, stamp))
    toonTrack = getToonTrack(attack, 3.4, ['conked'], 1.9, ['sidestep'])
    soundTrack = getSoundTrack('SA_rubber_stamp.ogg', delay=0.5, node=suit)
    return Parallel(suitTrack, toonTrack, propTrack, padPropTrack, soundTrack)


def doRazzleDazzle(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    sign = globalPropPool.getProp('smile')
    signPropTracks = Parallel()
    signPropAnimTracks = Parallel()
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    BattleParticles.loadParticles()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        hitSuit = dmg > 0
        particleEffect = BattleParticles.createParticleEffect('Smile')
        signPosPoints = [Point3(0.0, -0.42, -0.04), VBase3(105.715, 73.977, 65.932)]
        if hitSuit:
            hitPoint = lambda toon = toon: __toonFacePoint(toon)
        else:
            hitPoint = lambda particleEffect = particleEffect, toon = toon, suit = suit: __toonMissPoint(particleEffect, toon, parent=suit.getRightHand())
        signPropTrack = Sequence(Func(__showProp, sign, suit.getRightHand(), signPosPoints[0], signPosPoints[1]), LerpScaleInterval(sign, 0.5, Point3(1.39, 1.39, 1.39)), Wait(0.5), Func(battle.movie.needRestoreParticleEffect, particleEffect), Func(particleEffect.start, sign), Func(particleEffect.wrtReparentTo, render), LerpPosInterval(particleEffect, 1.0, pos=hitPoint), Func(particleEffect.cleanup), LerpScaleInterval(sign, 0.5, Point3(0, 0, 0)), Func(battle.movie.clearRestoreParticleEffect, particleEffect))
        signPropAnimTrack = ActorInterval(sign, 'smile', duration=2.5, startTime=1)
        signPropTracks.append(signPropTrack)
        signPropAnimTracks.append(signPropAnimTrack)
    toonTrack = getToonTracks(attack, 2.0, ['cringe'], 1.0, ['sidestep'])
    soundTrack = getSoundTrack('SA_razzle_dazzle.ogg', delay=0.8, node=suit)
    return Sequence(Parallel(suitTrack, signPropTracks, signPropAnimTracks, toonTrack, soundTrack), Func(MovieUtil.removeProp, sign))


def doSynergy(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.7
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1

    particleEffect = BattleParticles.createParticleEffect('Synergy')
    waterfallEffect = BattleParticles.createParticleEffect(file='synergyWaterfall')
    suitTrack = getSuitAnimTrack(attack)
    partTrack = getPartTrack(particleEffect, 1.0, 3.4, [particleEffect, suit, 0], softStop=-2)
    waterfallTrack = getPartTrack(waterfallEffect, 0.8, 3.4, [waterfallEffect, suit, 0], softStop=-2)
    damageAnims = [['slip-forward']]
    dodgeAnims = []
    dodgeAnims.append(['jump',
     0.01,
     0,
     0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.3, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, damageAnimNames=['slip-forward'], dodgeDelay=0.91, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.0)
    synergySoundTrack = Sequence(Wait(0.9), SoundInterval(globalBattleSoundCache.getSound('SA_synergy.ogg'), node=suit))
    if hitAtleastOneToon > 0:
        fallingSoundTrack = Sequence(Wait(damageDelay + 0.5), SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=suit))
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, fallingSoundTrack, toonTracks)
    else:
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, toonTracks)


def doEmbezzleOLD(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    bill = loader.loadModel('phase_3.5/models/props/jellybean4')
    bill.setH(0)
    bill.setColor(1,0.9,0)
    glow = loader.loadModel("phase_3.5/models/props/glow.bam")
    glow.reparentTo(bill)
    glow.setScale(0.5)
    glow.setPos(0,0,0)
    glow.setColorScale(Vec4(1, 0.9, 0, 0.3))
    suitTrack = getSuitTrack(attack)
    suitTrack.append(Wait(1.0))
    billPosPoints = [Point3(-0.21707670043415206, 0.30390738060781786, -0.4775687409551388), VBase3(-301.64978292329954, 0, 0)]
    billPropTrack = getPropTrack(bill, suit.getRightHand(), billPosPoints, 0.6, 0.55, scaleUpPoint=Point3(2.0, 2.0, 2.0))
    toonTrack = getToonTrack(attack, 0.25, ['cringe'], 0.01, ['sidestep'])
    glowTrack = Sequence()
    glowTrack.append(Wait(4.0))
    glowTrack.append(Func(glow.hide))
    multiTrackList = Parallel(suitTrack, toonTrack, glowTrack)
    if dmg > 0:
        soundTrack = getSoundTrack('SA_pick_pocket.ogg', delay=0.2, node=suit)
        multiTrackList.append(billPropTrack)
        multiTrackList.append(soundTrack)
    return multiTrackList

def doEmbezzle(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    BattleParticles.loadParticles()
    bill = globalPropPool.getProp('10dollar')
    suitTrack = getSuitTrack(attack)
    billPosPoints = [Point3(-0.13024602026049337, 0.45, -0.25), VBase3(136.424, -46.434, -129.712)]
    billPropTrack = getPropTrack(bill, suit.getRightHand(), billPosPoints, 0.25, 1.0, scaleUpPoint=Point3(2.115, 2.115, 2.115))
    partTrack = Parallel()
    for i in range(10):
        dollar = MovieUtil.copyProp(BattleParticles.getParticle('dollar-sign'))
        dollar.reparentTo(hidden)
        dollar.setColor(VBase4(0.0, 1.0, 0.0, 1.0))
        dollar.setBillboardPointEye()
        radius = random.random() - 0.5
        angle = random.random() * 2.0 * math.pi
        partTrack.append(Sequence(
            Wait(0.55 + (i * 0.01)),
            Func(__showProp, dollar, suit.getRightHand(), *billPosPoints),
            Func(dollar.wrtReparentTo, battle),
            Func(dollar.setHpr, VBase3(0, 0, 0)),
            Parallel(
                LerpFunctionInterval(dollar.setZ, 0.5, suit.getRightHand().getZ() + 1.0, suit.getRightHand().getZ() - 1.0, blendType='easeIn'),
                LerpScaleInterval(dollar, 0.5, MovieUtil.PNT3_NEARZERO)
            ),
            Func(MovieUtil.removeProp, dollar),
            Func(battle.movie.clearRenderProp, dollar)
        ))

    toonTrack = getToonTrack(attack, 0.6, ['cringe'], 0.01, ['sidestep'])
    multiTrackList = Parallel(suitTrack, toonTrack)
    if target[0]['hp'] > 0:
        soundTrack = getSoundTrack('ttr_s_ene_bat_embezzle.ogg', node=suit)
        multiTrackList.append(billPropTrack)
        multiTrackList.append(soundTrack)
        multiTrackList.append(partTrack)
    return multiTrackList

def doFloodTheMarket(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.7
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1

    particleEffect = BattleParticles.createParticleEffect(file='floodTheMarket')
    waterfallEffect = BattleParticles.createParticleEffect(file='floodTheMarketWaterfall')
    suitTrack = getSuitAnimTrack(attack)
    partTrack = getPartTrack(particleEffect, 1.0, 3.4, [particleEffect, suit, 0], softStop=-2)
    waterfallTrack = getPartTrack(waterfallEffect, 0.8, 3.4, [waterfallEffect, suit, 0], softStop=-2)
    damageAnims = [['melt'], ['jump', 1.5, 0.4]]
    dodgeAnims = []
    dodgeAnims.append(['jump',
     0.01,
     0,
     0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.3, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.91, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.0, showDamageExtraTime=1.0)
    synergySoundTrack = Sequence(Wait(0.9), SoundInterval(globalBattleSoundCache.getSound('ttr_s_ene_bat_floodTheMarket.ogg'), node=suit))
    if hitAtleastOneToon > 0:
        puddleCounter = 0
        for t in targets:
            toon = t['toon']
            if t['hp'] > 0:
                if puddleCounter == 0:
                    puddle = globalPropPool.getProp('quicksand')
                    puddle.setColor(Vec4(0.0, 0.0, 1.0, 1))
                    puddle.setHpr(Point3(120, 0, 0))
                    puddle.setScale(0.01)
                    puddleTrack = Sequence(Func(battle.movie.needRestoreRenderProp, puddle), Func(puddle.reparentTo, battle), Func(puddle.setPos, toon.getPos(battle)), LerpScaleInterval(puddle, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO), Wait(3.2), LerpFunctionInterval(puddle.setAlphaScale, fromData=1, toData=0, duration=0.8), Func(MovieUtil.removeProp, puddle), Func(battle.movie.clearRenderProp, puddle))
                if puddleCounter == 1:
                    puddle2 = globalPropPool.getProp('quicksand')
                    puddle2.setColor(Vec4(0.0, 0.0, 1.0, 1))
                    puddle2.setHpr(Point3(120, 0, 0))
                    puddle2.setScale(0.01)
                    puddleTrack1 = Sequence(Func(battle.movie.needRestoreRenderProp, puddle2), Func(puddle2.reparentTo, battle), Func(puddle2.setPos, toon.getPos(battle)), LerpScaleInterval(puddle2, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO), Wait(3.2), LerpFunctionInterval(puddle2.setAlphaScale, fromData=1, toData=0, duration=0.8), Func(MovieUtil.removeProp, puddle2), Func(battle.movie.clearRenderProp, puddle2))
                if puddleCounter == 2:
                    puddle3 = globalPropPool.getProp('quicksand')
                    puddle3.setColor(Vec4(0.0, 0.0, 1.0, 1))
                    puddle3.setHpr(Point3(120, 0, 0))
                    puddle3.setScale(0.01)
                    puddleTrack2 = Sequence(Func(battle.movie.needRestoreRenderProp, puddle3), Func(puddle3.reparentTo, battle), Func(puddle3.setPos, toon.getPos(battle)), LerpScaleInterval(puddle3, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO), Wait(3.2), LerpFunctionInterval(puddle3.setAlphaScale, fromData=1, toData=0, duration=0.8), Func(MovieUtil.removeProp, puddle3), Func(battle.movie.clearRenderProp, puddle3))
                if puddleCounter == 3:
                    puddle4 = globalPropPool.getProp('quicksand')
                    puddle4.setColor(Vec4(0.0, 0.0, 1.0, 1))
                    puddle4.setHpr(Point3(120, 0, 0))
                    puddle4.setScale(0.01)
                    puddleTrack3 = Sequence(Func(battle.movie.needRestoreRenderProp, puddle4), Func(puddle4.reparentTo, battle), Func(puddle4.setPos, toon.getPos(battle)), LerpScaleInterval(puddle4, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO), Wait(3.2), LerpFunctionInterval(puddle4.setAlphaScale, fromData=1, toData=0, duration=0.8), Func(MovieUtil.removeProp, puddle4), Func(battle.movie.clearRenderProp, puddle4))
                puddleCounter +=1
        if puddleCounter == 1:
            puddleCounter = 0
            return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, puddleTrack, toonTracks)
        if puddleCounter == 2:
            puddleCounter = 0
            return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, puddleTrack, puddleTrack1, toonTracks)
        if puddleCounter == 3:
            puddleCounter = 0
            return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, puddleTrack, puddleTrack1,  puddleTrack2, toonTracks)
        if puddleCounter == 4:
            puddleCounter = 0
            return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, puddleTrack, puddleTrack1,  puddleTrack2,  puddleTrack3, toonTracks)
    else:
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, toonTracks)

def doReprogram(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    target = attack['target']
    toon = target[0]['toon']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    battle = attack['battle']
    targetPos = toon.getPos(battle)
    sinkPos = suit.getPos(battle)
    dropPos = suit.getPos(battle)
    sinkPos2 = suit.getPos(battle)
    dropPos2 = suit.getPos(battle)
    sinkPos.setY(sinkPos.getY() + 12.5)
    sinkPos.setZ(sinkPos.getZ() - 4.5)
    sinkPos2.setY(sinkPos.getY() - 30.5)
    sinkPos2.setX(targetPos.getX())
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    targetPos2 = toon.getPos(battle)
    headsUp2 = Func(suit.setHpr, battle, origHpr)
    moveTrack = Sequence(LerpPosInterval(suit, 2.75, sinkPos2, other=battle), Func(suit.setPos, battle, dropPos))
    suitTrack = Sequence(tauntInterval, headsUp, ActorInterval(suit, 'walk'), ActorInterval(suit, 'walk'), headsUp2, Func(suit.setNeutralAnimation))
    damageAnims = []
    damageAnims.append(['cringe'])
    toonTrack = getToonTrack(attack, damageDelay=2.25, splicedDamageAnims=damageAnims, dodgeDelay=0.91, dodgeAnimNames=['sidestep'])
    return Parallel(suitTrack, moveTrack, toonTrack)


def doDenialOfService(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    sanctioned = loader.loadModel('phase_5/models/props/ttrpg_m_ene_prp_deniedSign')
    missPoint = lambda sanctioned=sanctioned, toon=toon: __toonMissPoint(sanctioned, toon)
    propTrack = Sequence(
        Wait(0.5),
        Func(battle.movie.needRestoreRenderProp, sanctioned),
        Func(sanctioned.reparentTo, render),
        Func(sanctioned.setScale, 2),
        Func(sanctioned.setPosHpr, suit.getLeftHand(), 0, 0.11, -0.16, 0, 80, 90),
        Func(sanctioned.setP, 0),
        Func(sanctioned.setR, 0),
        getPropThrowTrack(attack, sanctioned, [__toonFacePoint(toon)], [missPoint], .25),
        Func(MovieUtil.removeProp, sanctioned),
        Func(battle.movie.clearRenderProp, sanctioned)
    )
    toonTrack = getToonTrack(attack, 0.8, ['conked'], 0.2, ['sidestep'])
    # toonTrack = getToonTrack(attack, 0.8, ['conked'], 0.2, ['sidestep'])
    taunt = random.choice(
        ["Someone isn't doing their part around here.", "This company will not tolerate any breach of contract, you will be punished.",
         "Your contract has been breached, now suffer the consequence!", "What happened to your little strategy called 'teamwork'?",])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    suitTrack = getSuitTrack(attack)
    soundTrack = getSoundTrack('SA_hurry_sickness.ogg', delay =.5, node=suit)
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack)


def doHostileTakeoverNew(attack):
    suit = attack['suit']
    battle = attack['battle']
    knifeDelay = 1.0
    suitTrack = getSuitAnimTrack(attack, playRate=1.25)
    knifeTracks = Parallel()
    for i in xrange(120):
        knife = globalPropPool.getProp('dagger')
        knifePos = Point3(random.randrange(-10.0, 10.0), random.randrange(-10.0, -4.0), 10.0)
        landPos = Point3(knifePos.getX() - 3.0, knifePos.getY() - 3, -2.0)
        knifeTrack = Sequence(
            Wait(knifeDelay + 0.025 * i),
            Func(knife.reparentTo, battle),
            Func(knife.setPos, knifePos),
            Func(knife.lookAt, landPos),
            Func(knife.setScale, Point3(0.75)),
            LerpPosInterval(knife, 0.1, landPos),
            Func(MovieUtil.removeProp, knife)
        )
        knifeTracks.append(knifeTrack)
    damageAnims = [['slip-forward', 0.01, 0.4, 1.2],
     ['slip-forward', 0.01, 1.0]]
    dodgeAnims = [['duck', 1e-06, 0.8]]
    toonTracks = getToonTracks(attack, damageDelay=knifeDelay + 0.11, splicedDamageAnims=damageAnims, dodgeDelay=knifeDelay - 0.1, splicedDodgeAnims=dodgeAnims)
    soundTrack = Sequence(Wait(1.0), SoundInterval(globalBattleSoundCache.getSound('ttr_s_ene_bat_hostileTakeover.ogg'), node=suit))
    return Parallel(suitTrack, knifeTracks, soundTrack, toonTracks)


def doMoneyTrip(attack):
    suit = attack['suit']
    battle = attack['battle']
    cameraTrack = Sequence(LerpPosHprInterval(camera, duration=0.25, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'))
    centerColor = Vec4(0, 1.0, 0, 1.0)
    edgeColor = Vec4(0, 1.0, 0, 1.0)
    powerBar1 = BattleParticles.createParticleEffect(file='moneytrip')
    powerBar2 = BattleParticles.createParticleEffect(file='moneytrip2')
    powerBar1.setPos(0, 6.1, 0.4)
    powerBar1.setHpr(-60, 0, 0)
    powerBar2.setPos(0, 6.1, 0.4)
    powerBar2.setHpr(60, 0, 0)
    powerBar1Particles = powerBar1.getParticlesNamed('particles-1')
    powerBar2Particles = powerBar2.getParticlesNamed('particles-1')
    powerBar1Particles.renderer.setCenterColor(centerColor)
    powerBar1Particles.renderer.setEdgeColor(edgeColor)
    powerBar2Particles.renderer.setCenterColor(centerColor)
    powerBar2Particles.renderer.setEdgeColor(edgeColor)
    waterfallEffect = BattleParticles.createParticleEffect('Waterfall')
    waterfallEffect.setScale(11)
    waterfallParticles = waterfallEffect.getParticlesNamed('particles-1')
    waterfallParticles.renderer.setCenterColor(centerColor)
    waterfallParticles.renderer.setEdgeColor(edgeColor)
    suitName = suit.getStyleName()
    if suitName == 'mh':
        waterfallEffect.setPos(0, 4, 3.6)
    suitTrack = getSuitAnimTrack(attack)

    def getPowerTrack(effect, suit = suit, battle = battle):
        partTrack = Sequence(Wait(1.0), Func(battle.movie.needRestoreParticleEffect, effect), Func(effect.start, suit), Wait(0.4), LerpPosInterval(effect, 1.0, Point3(0, 15, 0.4)), LerpFunctionInterval(effect.setAlphaScale, fromData=1, toData=0, duration=0.4), Func(effect.cleanup), Func(battle.movie.clearRestoreParticleEffect, effect))
        return partTrack

    partTrack1 = getPowerTrack(powerBar1)
    partTrack2 = getPowerTrack(powerBar2)
    waterfallTrack = getPartTrack(waterfallEffect, 0.6, 2.3, [waterfallEffect, suit, 0], softStop=-1)
    toonTracks = getToonTracks(attack, 1.8, ['slip-forward'], 1.29, ['jump'])
    soundTrack = Sequence(Wait(1), SoundInterval(globalBattleSoundCache.getSound('SA_money_fall.ogg'), node=suit))
    return Parallel(cameraTrack, suitTrack, partTrack1, partTrack2, waterfallTrack, toonTracks, soundTrack)



def doTeeOff(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    club = globalPropPool.getProp('golf-club')
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    clubPosPoints = [Point3(0.2, 3.3, -0.5), VBase3(0.0, 45.0, 270.0)]
    clubPropTrack = getPropTrack(club, suit.getRightHand(), clubPosPoints, 0.25, 3, Point3(1.1, 1.1, 1.1))
    suitName = attack['suitName']
    ballPosPoints = [Point3(5.1, 4.0, 0.1)]
    ballPropTracks = Parallel()
    for t in targets:
        toon = t['toon']
        ball = globalPropPool.getProp('golf-ball')
        ballPropTrack = Sequence(getPropAppearTrack(ball, suit, ballPosPoints, 1.25, Point3(1.75, 1.75, 1.75)),
                                 Func(battle.movie.needRestoreRenderProp, ball), Func(ball.wrtReparentTo, render),
                                 Wait(1.125))
        missPoint = lambda ball=ball, toon=toon: __toonMissPoint(ball, toon)
        ballPropTrack.append(getPropThrowTrack(attack, ball, [__toonFacePoint(toon)], [missPoint], .1, target=t))
        ballPropTrack.append(Func(battle.movie.clearRenderProp, ball))
        ballPropTracks.append(ballPropTrack)

    dodgeDelay = suitTrack.getDuration()
    toonTracks = getToonTracks(attack, 3, ['slip-backward'], 1.5, ['duck'],
                               showMissedExtraTime=1.7)
    soundTrack = getSoundTrack('SA_tee_off.ogg', delay=2.5, node=suit)
    return Parallel(suitTrack, toonTracks, clubPropTrack, ballPropTracks, soundTrack)

def doTeeOffGroup(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    club = globalPropPool.getProp('golf-club')
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.5))
    clubPosPoints = [Point3(0.2, 3.3, -0.5), VBase3(0.0, 45.0, 270.0)]
    clubPropTrack = getPropTrack(club, suit.getRightHand(), clubPosPoints, 0.25, 3, Point3(1.1, 1.1, 1.1))
    ballPropTracks = Parallel()
    for t in targets:
        toon = t['toon']
        ball = globalPropPool.getProp('golf-ball')
        suitName = attack['suitName']
        ballPosPoints = [Point3(5.1, 4.0, 0.1)]
        ballPropTrack = Sequence(getPropAppearTrack(ball, suit, ballPosPoints, 1.25, Point3(1.75, 1.75, 1.75)),
                                 Func(battle.movie.needRestoreRenderProp, ball), Func(ball.wrtReparentTo, render),
                                 Wait(1.125))
        missPoint = lambda ball=ball, toon=toon: __toonMissPoint(ball, toon)
        ballPropTrack.append(getThrowTrack(ball, toon.getPos(battle), 0.1, battle, .1))
        ballPropTrack.append(Func(MovieUtil.removeProp, ball))
        ballPropTracks.append(ballPropTrack)
    dodgeDelay = suitTrack.getDuration()
    toonTracks = getToonTracks(attack, suitTrack.getDuration() - 1.75, ['slip-backward'], 1.5, ['duck'],
                             showMissedExtraTime=1.7)
    soundTrack = getSoundTrack('SA_tee_off.ogg', delay=2.5, node=suit)
    return Parallel(suitTrack, toonTracks, clubPropTrack, ballPropTracks, soundTrack)


def doTeeOff2(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    club = globalPropPool.getProp('golf-club')
    ball = globalPropPool.getProp('golf-ball')
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    clubPosPoints = [Point3(0.2, 3.3, -0.5), VBase3(0.0, 45.0, 270.0)]
    clubPropTrack = getPropTrack(club, suit.getRightHand(), clubPosPoints, 0.25, 3, Point3(1.1, 1.1, 1.1))
    suitName = attack['suitName']
    ballPosPoints = [Point3(5.1, 4.0, 0.1)]
    ballPropTrack = Sequence(getPropAppearTrack(ball, suit, ballPosPoints, 1.25, Point3(1.5, 1.5, 1.5)),
                             Func(battle.movie.needRestoreRenderProp, ball), Func(ball.wrtReparentTo, render),
                             Wait(1.125))
    missPoint = lambda ball=ball, toon=toon: __toonMissPoint(ball, toon)
    ballPropTrack.append(getPropThrowTrack(attack, ball, [__toonFacePoint(toon)], [missPoint], .1))
    ballPropTrack.append(Func(battle.movie.clearRenderProp, ball))
    dodgeDelay = suitTrack.getDuration()
    toonTrack = getToonTrack(attack, suitTrack.getDuration() - 1.75, ['slip-backward'], 1.5, ['duck'],
                             showMissedExtraTime=1.7)
    soundTrack = getSoundTrack('SA_tee_off.ogg', delay=2.5, node=suit)
    mulliganTrack = Sequence(Wait(6.0), doMulligan(attack))
    return Parallel(suitTrack, toonTrack, clubPropTrack, ballPropTrack, soundTrack, mulliganTrack)


def doMulliganGroup(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    club = globalPropPool.getProp('golf-club')
    tauntIndex = attack['taunt']
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    taunt = random.choice(
        ['Let me just make this quick adjustment...', "That last shot didn't go the way that I wanted it to.",
         "Let's try this again.", 'I certainly will take a mulligan.'])
    suitTrack = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout),
                         ActorInterval(suit, 'golf-club-swing', playRate=1.75), suitReset, Func(suit.setNeutralAnimation))
    clubPosPoints = [Point3(0.2, 3.3, -0.5), VBase3(0.0, 45.0, 270.0)]
    clubPropTrack = getPropTrack(club, suit.getRightHand(), clubPosPoints, 0.25, 2.5, Point3(1.1, 1.1, 1.1))
    ballPropTracks = Parallel()
    for t in targets:
        toon = t['toon']
        ball = globalPropPool.getProp('golf-ball')
        suitName = attack['suitName']
        ballPosPoints = [Point3(5.1, 4.0, 0.1)]
        ballPropTrack = Sequence(getPropAppearTrack(ball, suit, ballPosPoints, 1.2, Point3(1.5, 1.5, 1.5)),
                                 Func(battle.movie.needRestoreRenderProp, ball), Func(ball.wrtReparentTo, render),
                                 Wait(0.75))
        missPoint = lambda ball=ball, toon=toon: __toonMissPoint(ball, toon)
        ballPropTrack.append(getThrowTrack(ball, toon.getPos(battle), 0.1, battle, 0.1))
        ballPropTrack.append(Func(MovieUtil.removeProp, ball))
        ballPropTracks.append(ballPropTrack)
    dodgeDelay = suitTrack.getDuration()
    toonTracks = getToonTracks(attack, 2.5, ['slip-backward'], 1, ['duck'],
                             showMissedExtraTime=1.7)
    soundTrack = getSoundTrack('SA_tee_off.ogg', delay=2, node=suit)
    return Parallel(suitTrack, toonTracks, clubPropTrack, ballPropTracks, soundTrack)

def doMulligan(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    club = globalPropPool.getProp('golf-club')
    ball = globalPropPool.getProp('golf-ball')
    tauntIndex = attack['taunt']
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    taunt = random.choice(['Let me just make this quick adjustment...', "That last shot didn't go the way that I wanted it to.", "Let's try this again.", 'I certainly will take a mulligan.'])
    suitTrack = Sequence(headsUp, Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout),
                         ActorInterval(suit, 'golf-club-swing', playRate=1.75), suitReset, Func(suit.setNeutralAnimation))

    clubPosPoints = [Point3(0.2, 3.3, -0.5), VBase3(0.0, 45.0, 270.0)]
    clubPropTrack = getPropTrack(club, suit.getRightHand(), clubPosPoints, 0.25, 2.5, Point3(1.1, 1.1, 1.1))
    suitName = attack['suitName']
    ballPosPoints = [Point3(5.1, 4.0, 0.1)]
    ballPropTrack = Sequence(getPropAppearTrack(ball, suit, ballPosPoints, 1.2, Point3(1.5, 1.5, 1.5)),
                             Func(battle.movie.needRestoreRenderProp, ball), Func(ball.wrtReparentTo, render),
                             Wait(0.75))
    missPoint = lambda ball=ball, toon=toon: __toonMissPoint(ball, toon)
    ballPropTrack.append(getPropThrowTrack(attack, ball, [__toonFacePoint(toon)], [missPoint], .1))
    ballPropTrack.append(Func(battle.movie.clearRenderProp, ball))
    dodgeDelay = suitTrack.getDuration()
    toonTrack = getToonTrack(attack, 2.5, ['slip-backward'], 1, ['duck'],
                             showMissedExtraTime=1.7)
    soundTrack = getSoundTrack('SA_tee_off.ogg', delay=2, node=suit)
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                      "So, I see you are very reliant on your Trap gags. Let's see how you do without them.",
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'tcm':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    return Parallel(suitTrack, toonTrack, clubPropTrack, ballPropTrack, soundTrack)


def doBrainStorm(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    BattleParticles.loadParticles()
    suitType = getSuitBodyType(attack['suitName'])
    partDelay = 1.2
    damageDelay = 2.5
    dodgeDelay = 2.3
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    initialCloudHeight = suit.height + 3
    cloudPosPoints = [Point3(0, 3, initialCloudHeight), VBase3(180, 0, 0)]
    cloudPropTracks = Parallel()
    for t in targets:
        toon = t['toon']
        snowEffect = BattleParticles.createParticleEffect('BrainStorm')
        snowEffect2 = BattleParticles.createParticleEffect('BrainStorm')
        snowEffect3 = BattleParticles.createParticleEffect('BrainStorm')
        effectColor = Vec4(0.65, 0.79, 0.93, 0.85)
        BattleParticles.setEffectTexture(snowEffect, 'brainstorm-box', color=effectColor)
        BattleParticles.setEffectTexture(snowEffect2, 'brainstorm-env', color=effectColor)
        BattleParticles.setEffectTexture(snowEffect3, 'brainstorm-track', color=effectColor)
        cloud = globalPropPool.getProp('stormcloud')
        cloudPropTrack = Sequence()
        cloudPropTrack.append(Func(cloud.pose, 'stormcloud', 0))
        cloudPropTrack.append(getPropAppearTrack(cloud, suit, cloudPosPoints, 1e-06, Point3(3, 3, 3), scaleUpTime=0.7))
        cloudPropTrack.append(Func(battle.movie.needRestoreRenderProp, cloud))
        cloudPropTrack.append(Func(cloud.wrtReparentTo, render))
        targetPoint = __toonFacePoint(toon)
        targetPoint.setZ(targetPoint[2] + 3)
        cloudPropTrack.append(Wait(0.5))
        cloudPropTrack.append(LerpPosInterval(cloud, .5, pos=targetPoint))
        cloudPropTrack.append(Parallel(ParticleInterval(snowEffect, cloud, worldRelative=0, duration=3.2, cleanup=True, softStopT=-1), Sequence(Wait(0.5), ParticleInterval(snowEffect2, cloud, worldRelative=0, duration=2.7, cleanup=True, softStopT=-1)), Sequence(Wait(1.0), ParticleInterval(snowEffect3, cloud, worldRelative=0, duration=2.2, cleanup=True, softStopT=-1)), Sequence(ActorInterval(cloud, 'stormcloud', startTime=3, duration=0.5), ActorInterval(cloud, 'stormcloud', startTime=2.5, duration=0.5), ActorInterval(cloud, 'stormcloud', startTime=1, duration=1.5))))
        cloudPropTrack.append(Wait(0.4))
        cloudPropTrack.append(LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO))
        cloudPropTrack.append(Func(MovieUtil.removeProp, cloud))
        cloudPropTrack.append(Func(battle.movie.clearRenderProp, cloud))
        cloudPropTracks.append(cloudPropTrack)

    damageAnims = [['cringe',
      0.01,
      0.4,
      0.8], ['duck', 1e-06, 1.6]]
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'], showMissedExtraTime=1.1)
    soundTrack = getSoundTrack('SA_brainstorm.ogg', delay=1.9, node=suit)
    return Parallel(suitTrack, toonTracks, cloudPropTracks, soundTrack)


def doBuzzWord(attack):
    suit = attack['suit']
    target = attack['target']
    toon = target[0]['toon']
    battle = attack['battle']
    BattleParticles.loadParticles()
    particleEffects = []
    texturesList = ['buzzwords-crash',
     'buzzwords-inc',
     'buzzwords-main',
     'buzzwords-over',
     'buzzwords-syn']
    for i in xrange(0, 5):
        effect = BattleParticles.createParticleEffect('BuzzWord')
        if random.random() > 0.5:
            BattleParticles.setEffectTexture(effect, texturesList[i], color=Vec4(1, 0.94, 0.02, 1))
        else:
            BattleParticles.setEffectTexture(effect, texturesList[i], color=Vec4(0, 0, 0, 1))
        particleEffects.append(effect)

    suitType = getSuitBodyType(attack['suitName'])
    partDelay = 2.25
    partDuration = 2.5
    damageDelay = 2.5
    dodgeDelay = 2.0
    suitName = suit.getStyleName()
    for effect in particleEffects:
        effect.setPos(0, 2.8, suit.getHeight() - 2.5)
        effect.setHpr(0, -20, 0)

    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    particleTracks = []
    for effect in particleEffects:
        particleTracks.append(getPartTrack(effect, partDelay, partDuration, [effect, suit, 0], softStop=-1))

    toonTrack = getToonTrack(attack, damageDelay=damageDelay, damageAnimNames=['cringe'], splicedDodgeAnims=[['duck', dodgeDelay, 1.4]], showMissedExtraTime=dodgeDelay + 0.5)
    soundTrack = getSoundTrack('SA_buzz_word.ogg', delay=2.0, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, *particleTracks)


def doDemotion(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    BattleParticles.loadParticles()
    sprayEffects = []
    for t in targets:
        sprayEffect = BattleParticles.createParticleEffect('DemotionSpray')
        BattleParticles.setEffectTexture(sprayEffect, 'snow-particle')
        sprayEffects.append(sprayEffect)

    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    partTracks = getPartTracks(attack, sprayEffects, 0.7, 2.1, 0, softStop=-1)
    partTracks2 = Parallel()
    partTracks3 = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        freezeEffect = BattleParticles.createParticleEffect('DemotionFreeze')
        unFreezeEffect = BattleParticles.createParticleEffect(file='demotionUnFreeze')
        BattleParticles.setEffectTexture(freezeEffect, 'snow-particle')
        BattleParticles.setEffectTexture(unFreezeEffect, 'snow-particle')
        facePoint = __toonFacePoint(toon)
        freezeEffect.setPos(0, 0, 2)
        unFreezeEffect.setPos(0, 0, 2)
        if dmg > 0:
            partTracks2.append(getPartTrack(freezeEffect, 1.4, 2.9, [freezeEffect, toon, 0], softStop=-1))
            partTracks3.append(getPartTrack(unFreezeEffect, 4.65, 2.0, [unFreezeEffect, toon, 0], softStop=-1))

    dodgeAnims = [['duck', 1e-06, 0.8]]
    damageAnims = []
    damageAnims.append(['cringe',
     0.01,
     0,
     0.5])
    damageAnims.extend(getSplicedLerpAnims('cringe', 0.4, 0.5, startTime=0.5))
    damageAnims.extend(getSplicedLerpAnims('cringe', 0.3, 0.5, startTime=0.9))
    damageAnims.extend(getSplicedLerpAnims('cringe', 0.3, 0.6, startTime=1.2))
    damageAnims.append(['cringe', 1.6, 1.5])
    toonTracks = getToonTracks(attack, damageDelay=0.0, splicedDamageAnims=damageAnims, dodgeDelay=0.0001, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.6, showDamageExtraTime=3.0)
    soundTrack = getSoundTrack('SA_demotion.ogg', delay=1.2, node=suit)
    return Parallel(suitTrack, toonTracks, soundTrack, partTracks, partTracks2, partTracks3)

def doDataBreach(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    partTracks = Parallel()
    partTracks2 = Parallel()
    partTracks3 = Parallel()
    partTracks4 = Parallel()
    BattleParticles.loadParticles()
    for t in targets:
        sprayEffect = BattleParticles.createParticleEffect('DemotionSpray2')
        sprayEffect2 = BattleParticles.createParticleEffect('DemotionSpray2')
        freezeEffect = BattleParticles.createParticleEffect('DemotionFreeze2')
        unFreezeEffect = BattleParticles.createParticleEffect(file='demotionUnFreeze2')
        BattleParticles.setEffectTexture(sprayEffect, 'snow-particle')
        BattleParticles.setEffectTexture(freezeEffect, 'snow-particle')
        BattleParticles.setEffectTexture(unFreezeEffect, 'snow-particle')
        toon = t['toon']
        dmg = t['hp']
        facePoint = __toonFacePoint(toon)
        freezeEffect.setPos(0, 0, facePoint.getZ())
        unFreezeEffect.setPos(0, 0, facePoint.getZ())
        partTrack = getPartTrack(sprayEffect, 1.7, 1.1, [sprayEffect, suit, 0], softStop=-1)
        partTrack4 = getPartTrack(sprayEffect, 2.4, 3.9, [sprayEffect2, toon, 0], softStop=-1)
        partTrack2 = getPartTrack(freezeEffect, 2.4, 3.9, [freezeEffect, toon, 0], softStop=-1)
        partTrack3 = getPartTrack(unFreezeEffect, 6.65, 1.5, [unFreezeEffect, toon, 0], softStop=-1)
        partTracks.append(partTrack)
        if dmg > 0:
            partTracks4.append(partTrack4)
            partTracks2.append(partTrack2)
            partTracks3.append(partTrack3)
    dodgeAnims = [['duck', 1e-06, 0.8]]
    damageAnims = []
    damageAnims.append(['cringe',
     0.01,
     0,
     0.5])
    damageAnims.extend(getSplicedLerpAnims('cringe', 0.4, 0.5, startTime=0.5))
    damageAnims.extend(getSplicedLerpAnims('cringe', 0.3, 0.5, startTime=0.9))
    damageAnims.extend(getSplicedLerpAnims('cringe', 0.3, 0.6, startTime=1.2))
    damageAnims.append(['cringe', 2.6, 1.5])
    toonTrack = getToonTracks(attack, damageDelay=1.0, splicedDamageAnims=damageAnims, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.6, showDamageExtraTime=1.3)
    soundTrack = getSoundTrack('SA_dataBreach.ogg', delay=1.2, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, partTracks, partTracks2, partTracks3, partTracks4)


def doCanned(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    hips = toon.getHipsParts()
    propDelay = 0.45
    suitType = getSuitBodyType(attack['suitName'])
    suitDelay = 1
    dodgeDelay = 2.6
    throwDuration = 1.5
    can = globalPropPool.getProp('can')
    explode = []
    scale = 26
    torso = toon.style.torso
    torso = torso[0]
    if torso == 's':
        scaleUpPoint = Point3(scale * 2.63, scale * 2.63, scale * 1.9975)
    elif torso == 'm':
        scaleUpPoint = Point3(scale * 2.63, scale * 2.63, scale * 1.7975)
    elif torso == 'l':
        scaleUpPoint = Point3(scale * 2.63, scale * 2.63, scale * 2.31)
    canHpr = VBase3(-173.47, -0.42, 162.09)
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.75))
    posPoints = [Point3(-0.1734104046242777, -0.5202312138728331, -0.45), VBase3(-10, 90, -170.635838150289)]
    throwTrack = Sequence(getPropAppearTrack(can, suit.getRightHand(), posPoints, propDelay, Point3(9, 9, 9), scaleUpTime=0.25))
    propDelay = propDelay + 0.5
    throwTrack.append(Wait(suitDelay))
    hitPoint = toon.getPos(battle)
    hitPoint.setX(hitPoint.getX() + 1.1)
    hitPoint.setY(hitPoint.getY() - 0.5)
    hitPoint.setZ(hitPoint.getZ() + toon.height + 1.1)
    throwTrack.append(Func(battle.movie.needRestoreRenderProp, can))
    throwTrack.append(getThrowTrack(can, hitPoint, duration=throwDuration, parent=battle))
    explodePosPoints = [Point3(0, 0, 0), MovieUtil.PNT3_ZERO]
    if dmg > 0:
        splatName = 'dust'
        splat = globalPropPool.getProp('dust')
        explode = globalPropPool.getProp('dust')
        explode.setTwoSided(True)
        explode.setBillboardPointWorld(2)
        explodeTrack = Sequence()
        explodeTrack.append(
            getPropAppearTrack(explode, toon, explodePosPoints, 0, Point3(2, 2, 2), scaleUpTime=0))
        explodeTrack.append(Sequence(ActorInterval(explode, splatName), Func(explode.detachNode)))
        dustTrack = Parallel(Func(splat.reparentTo, toon),
                             Sequence(ActorInterval(splat, splatName), Func(splat.detachNode)))
        can2 = MovieUtil.copyProp(can)
        hips1 = hips.getPath(2)
        hips2 = hips.getPath(1)
        can2Point = Point3(hitPoint.getX(), hitPoint.getY() + 6.4, hitPoint.getZ())
        can2.setPos(can2Point)
        can2.setScale(scaleUpPoint)
        can2.setHpr(canHpr)
        throwTrack.append(Func(battle.movie.needRestoreHips))
        throwTrack.append(Func(can.wrtReparentTo, hips1))
        throwTrack.append(Func(can2.reparentTo, hips2))
        throwTrack.append(Func(MovieUtil.removeProp, can2))
        throwTrack.append(Func(MovieUtil.removeProp, can))
        soundTrack = getSoundTrack('LB_evidence_miss.ogg', node=suit)
        throwTrack.append(Parallel(explodeTrack, soundTrack))
        throwTrack.append(Wait(2.4))
        throwTrack.append(Func(battle.movie.clearRestoreHips))
        scaleTrack = Sequence(Wait(propDelay + suitDelay), LerpScaleInterval(can, throwDuration, scaleUpPoint))
        hprTrack = Sequence(Wait(propDelay + suitDelay), LerpHprInterval(can, throwDuration, canHpr))
        soundTrack = Sequence(Wait(1.2), SoundInterval(globalBattleSoundCache.getSound('SA_canned_tossup_only.ogg'), node=suit), SoundInterval(globalBattleSoundCache.getSound('SA_canned_impact_only.ogg'), node=suit))
    else:
        land = toon.getPos(battle)
        land.setZ(land.getZ() + 0.7)
        bouncePoint1 = Point3(land.getX(), land.getY() - 1.5, land.getZ() + 2.5)
        bouncePoint2 = Point3(land.getX(), land.getY() - 2.1, land.getZ() - 0.2)
        bouncePoint3 = Point3(land.getX(), land.getY() - 3.1, land.getZ() + 1.5)
        bouncePoint4 = Point3(land.getX(), land.getY() - 4.1, land.getZ() + 0.3)
        throwTrack.append(LerpPosInterval(can, 0.4, land))
        throwTrack.append(LerpPosInterval(can, 0.4, bouncePoint1))
        throwTrack.append(LerpPosInterval(can, 0.3, bouncePoint2))
        throwTrack.append(LerpPosInterval(can, 0.3, bouncePoint3))
        throwTrack.append(LerpPosInterval(can, 0.3, bouncePoint4))
        throwTrack.append(Wait(1.1))
        throwTrack.append(LerpScaleInterval(can, 0.3, MovieUtil.PNT3_NEARZERO))
        scaleTrack = Sequence(Wait(propDelay + suitDelay), LerpScaleInterval(can, throwDuration, Point3(11, 11, 11)))
        hprTrack = Sequence(Wait(propDelay + suitDelay), LerpHprInterval(can, throwDuration, canHpr), Wait(0.4), LerpHprInterval(can, 0.4, Point3(83.27, 19.52, -177.92)), LerpHprInterval(can, 0.3, Point3(95.24, -72.09, 88.65)), LerpHprInterval(can, 0.2, Point3(-96.34, -2.63, 179.89)))
        soundTrack = getSoundTrack('SA_canned_tossup_only.ogg', delay=1.7, node=suit)
    canTrack = Sequence(Parallel(throwTrack, scaleTrack, hprTrack), Func(MovieUtil.removeProp, can), Func(battle.movie.clearRenderProp, can))
    damageAnims = [['struggle',
      propDelay + suitDelay + throwDuration - .5,
      0.01,
      0.7], ['slip-backward', 0.01, 0.45]]
    toonTrack = getToonTrack(attack, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'], showDamageExtraTime=propDelay + suitDelay + 1.9)
    return Parallel(suitTrack, toonTrack, canTrack, soundTrack)


def doDownsize(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    toon = targets[0]['toon']
    dmg = targets[0]['hp']
    hitAtleastOneToon = False
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = True

    damageDelay = 2.0
    sprayEffects = [BattleParticles.createParticleEffect(file='downsizeSpray') for t in targets]
    cloudEffect = BattleParticles.createParticleEffect(file='downsizeCloud')
    toonPos = toon.getPos(toon)
    cloudPos = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.getHeight() * 0.55)
    cloudEffect.setPos(cloudPos)
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    sprayTracks = getPartTracks(attack, sprayEffects, 1.0, 2.28, 0, softStop=-1)
    cloudTracks = Parallel()
    shrinkTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        cloudEffect = BattleParticles.createParticleEffect(file='downsizeCloud')
        toonPos = toon.getPos(toon)
        cloudPos = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.getHeight() * 0.55)
        cloudEffect.setPos(cloudPos)
        cloudTracks.append(getPartTrack(cloudEffect, 2.1, 2.9, [cloudEffect, toon, 0], softStop=-1))
        if dmg > 0:
            initialScale = toon.getScale()
            downScale = Vec3(0.4, 0.4, 0.4)
            shrinkTracks.append(Sequence(Wait(damageDelay + 0.5), Func(battle.movie.needRestoreToonScale), LerpScaleInterval(toon, 1.0, downScale * 1.1), LerpScaleInterval(toon, 0.1, downScale * 0.9), LerpScaleInterval(toon, 0.1, downScale * 1.05), LerpScaleInterval(toon, 0.1, downScale * 0.95), LerpScaleInterval(toon, 0.1, downScale), Wait(2.1), LerpScaleInterval(toon, 0.5, initialScale * 1.5), LerpScaleInterval(toon, 0.15, initialScale * 0.5), LerpScaleInterval(toon, 0.15, initialScale * 1.2), LerpScaleInterval(toon, 0.15, initialScale * 0.8), LerpScaleInterval(toon, 0.15, initialScale), Func(battle.movie.clearRestoreToonScale)))

    cloudTrack = getPartTrack(cloudEffect, 2.1, 1.9, [cloudEffect, toon, 0])
    if dmg > 0:
        initialScale = toon.getScale()
        downScale = Vec3(0.4, 0.4, 0.4)
        shrinkTrack = Sequence(Wait(damageDelay + 0.5), Func(battle.movie.needRestoreToonScale), LerpScaleInterval(toon, 1.0, downScale * 1.1), LerpScaleInterval(toon, 0.1, downScale * 0.9), LerpScaleInterval(toon, 0.1, downScale * 1.05), LerpScaleInterval(toon, 0.1, downScale * 0.95), LerpScaleInterval(toon, 0.1, downScale), Wait(2.1), LerpScaleInterval(toon, 0.5, initialScale * 1.5), LerpScaleInterval(toon, 0.15, initialScale * 0.5), LerpScaleInterval(toon, 0.15, initialScale * 1.2), LerpScaleInterval(toon, 0.15, initialScale * 0.8), LerpScaleInterval(toon, 0.15, initialScale), Func(battle.movie.clearRestoreToonScale))
    damageAnims = []
    damageAnims.append(['juggle',
     0.01,
     0.87,
     0.5])
    damageAnims.append(['lose',
     0.01,
     2.17,
     0.93])
    damageAnims.append(['lose',
     0.01,
     3.1,
     -0.93])
    damageAnims.append(['struggle',
     0.01,
     0.8,
     1.8])
    damageAnims.append(['sidestep-right',
     0.01,
     2.97,
     1.49])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.6, dodgeAnimNames=['sidestep'])
    if hitAtleastOneToon:
        soundTrack = getSoundTrack('SA_head_shrink_only.ogg', delay=2.5, node=suit)
        return Parallel(suitTrack, sprayTracks, cloudTracks, shrinkTracks, soundTrack, toonTracks)
    else:
        return Parallel(suitTrack, sprayTracks, cloudTracks, shrinkTracks, toonTracks)

def doVersionControl(attack):
    suit = attack['suit']
    battle = attack['battle']
    damageDelay = 1.5
    targets = attack['target']
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    shrinkTracks = Parallel()
    cloudTracks = Parallel()
    sprayTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        sprayEffect = BattleParticles.createParticleEffect(file='downsizeSpray2')
        cloudEffect = BattleParticles.createParticleEffect(file='downsizeCloud2')
        toonPos = toon.getPos(toon)
        cloudPos = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.getHeight() * 0.55)
        cloudEffect.setPos(cloudPos)
        sprayTrack = getPartTrack(sprayEffect, 1.0, 2.28, [sprayEffect, suit, 0], softStop=-1)
        cloudTrack = getPartTrack(cloudEffect, 2.1, 2.9, [cloudEffect, toon, 0], softStop=-1)
        if dmg > 0:
            initialScale = toon.getScale()
            downScale = Vec3(0.4, 0.4, 0.4)
            shrinkTrack = Sequence(Wait(damageDelay + 0.5), Func(battle.movie.needRestoreToonScale),
                                   LerpScaleInterval(toon, 1.0, downScale * 1.1),
                                   LerpScaleInterval(toon, 0.1, downScale * 0.9),
                                   LerpScaleInterval(toon, 0.1, downScale * 1.05),
                                   LerpScaleInterval(toon, 0.1, downScale * 0.95),
                                   LerpScaleInterval(toon, 0.1, downScale), Wait(2.1),
                                   LerpScaleInterval(toon, 0.5, initialScale * 1.5),
                                   LerpScaleInterval(toon, 0.15, initialScale * 0.5),
                                   LerpScaleInterval(toon, 0.15, initialScale * 1.2),
                                   LerpScaleInterval(toon, 0.15, initialScale * 0.8),
                                   LerpScaleInterval(toon, 0.15, initialScale),
                                   Func(battle.movie.clearRestoreToonScale))
            shrinkTracks.append(shrinkTrack)
            cloudTracks.append(cloudTrack)
            sprayTracks.append(sprayTrack)
    damageAnims = []
    damageAnims.append(['juggle',
     0.01,
     0.87,
     0.5])
    damageAnims.append(['lose',
     0.01,
     2.17,
     0.93])
    damageAnims.append(['lose',
     0.01,
     3.1,
     -0.93])
    damageAnims.append(['struggle',
     0.01,
     0.8,
     1.8])
    damageAnims.append(['sidestep-right',
     0.01,
     2.97,
     1.49])
    toonTrack = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.6, dodgeAnimNames=['duck'])
    soundTrack = getSoundTrack('SA_head_shrink_only.ogg', delay=2, node=suit)
    return Parallel(suitTrack, sprayTracks, cloudTracks, shrinkTracks, soundTrack, toonTrack)


def doPinkSlip(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    propTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        throwDelay = 2.43
        throwDuration = 0.5
        suitType = getSuitBodyType(attack['suitName'])
        if suitType == 'c':
            posPoints = [Point3(-.1, -0.390738060781473, 0.02), VBase3(-4.688856729377676, 176.3531114327062, 176.61360347322716)]
        elif suitType == 'b':
            posPoints = [Point3(-0.13024602026049337, -0.390738060781473, -0.08670520231213885), VBase3(-5.73082489146168, -174.27745664739885, 173.48769898697537)]
        else:
            posPoints = [Point3(-0.26011560693641655, -0.3468208092485554, 0.0), VBase3(-7.283236994219635, -180.0, -188.3236994219653)]
        paper = globalPropPool.getProp('pink-slip')
        paperAppearTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.8, Point3(8.5, 8.5, 8.5), scaleUpTime=0.25))
        paperAppearTrack.append(Wait(0.93))
        hitPoint = __toonGroundPoint(attack, toon, 0.2, parent=battle)
        paperAppearTrack.append(Func(battle.movie.needRestoreRenderProp, paper))
        paperAppearTrack.append(Func(paper.wrtReparentTo, battle))
        paperAppearTrack.append(Parallel(LerpHprInterval(paper, throwDuration, VBase3(0, 0, 0)), LerpPosInterval(paper, throwDuration, hitPoint)))
        if dmg > 0:
            paperPause = 0.01
            slidePoint = Point3(hitPoint.getX(), hitPoint.getY() - 5, hitPoint.getZ() + 4)
            landPoint = Point3(hitPoint.getX(), hitPoint.getY() - 5, hitPoint.getZ())
            paperAppearTrack.append(Wait(paperPause))
            paperAppearTrack.append(LerpPosInterval(paper, 0.2, slidePoint))
            paperAppearTrack.append(LerpPosInterval(paper, 1.1, landPoint))
            paperSpinTrack = Sequence(Wait(throwDelay), LerpHprInterval(paper, throwDuration, VBase3(0, 0, 0)), Wait(paperPause), LerpHprInterval(paper, 1.3, VBase3(-200, 100, 100)))
        else:
            slidePoint = Point3(hitPoint.getX(), hitPoint.getY() - 5, hitPoint.getZ())
            paperAppearTrack.append(LerpPosInterval(paper, 0.5, slidePoint))
            paperSpinTrack = Sequence(Wait(throwDelay), LerpHprInterval(paper, throwDuration, VBase3(300, 0, 0)), LerpHprInterval(paper, 0.5, VBase3(10, 0, 0)))
        propTrack = Sequence()
        propTrack.append(Parallel(paperAppearTrack, paperSpinTrack))
        propTrack.append(LerpScaleInterval(paper, 0.4, MovieUtil.PNT3_NEARZERO))
        propTrack.append(Func(MovieUtil.removeProp, paper))
        propTrack.append(Func(battle.movie.clearRenderProp, paper))
        propTracks.append(propTrack)

    damageAnims = [['jump',
      0.01,
      0.3,
      0.7], ['slip-forward', 0.01]]
    toonTracks = getToonTracks(attack, damageDelay=1.75, splicedDamageAnims=damageAnims, dodgeDelay=1.75, dodgeAnimNames=['jump'], showDamageExtraTime=0.9)
    soundTrack = getSoundTrack('SA_pink_slip.ogg', delay=2.1, duration=1.1, node=suit)
    return Parallel(suitTrack, toonTracks, propTrack, soundTrack)


def doReOrg(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.2
    attackDelay = 1.2
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    partTracks = Parallel()
    allHeadTracks = Parallel()
    allChestTracks = Parallel()
    BattleParticles.loadParticles()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        sprayEffects = BattleParticles.createParticleEffect('ReOrgSprayNew')
        BattleParticles.setEffectTexture(sprayEffects, 'snow-particle',
                                         color=Vec4(1, 0, 0, 1))
        partTrack = getPartTrack(sprayEffects, 0.5, 3.0, [sprayEffects, toon, 0], softStop=-1)
        partTracks.append(partTrack)
        if dmg > 0:
            headParts = toon.getHeadParts()
            print '***********headParts pos=', headParts[0].getPos()
            print '***********headParts hpr=', headParts[0].getHpr()
            headTracks = Parallel()
            for partNum in xrange(0, headParts.getNumPaths()):
                part = headParts.getPath(partNum)
                x = part.getX()
                y = part.getY()
                z = part.getZ()
                h = part.getH()
                p = part.getP()
                r = part.getR()
                headTracks.append(Sequence(Wait(attackDelay), LerpPosInterval(part, 0.1, Point3(x - 0.2, y, z - 0.03)), LerpPosInterval(part, 0.1, Point3(x + 0.4, y, z - 0.03)), LerpPosInterval(part, 0.1, Point3(x - 0.4, y, z - 0.03)), LerpPosInterval(part, 0.1, Point3(x + 0.4, y, z - 0.03)), LerpPosInterval(part, 0.1, Point3(x - 0.2, y, z - 0.04)), LerpPosInterval(part, 0.25, Point3(x, y, z + 2.2)), LerpHprInterval(part, 0.25, VBase3(360, 0, 180)), LerpPosInterval(part, 0.25, Point3(x, y, z + 3.1)), LerpPosInterval(part, 0.1, Point3(x, y, z + 0.3)), Wait(0.1), LerpHprInterval(part, 0.35, VBase3(-745, 0, 180), startHpr=VBase3(0, 0, 180)), LerpHprInterval(part, 0.5, VBase3(25, 0, 180), startHpr=VBase3(0, 0, 180)), LerpPosInterval(part, 0.15, Point3(x, y, z + 1)), LerpHprInterval(part, 0.3, VBase3(h, p, r)), Wait(0.2), LerpPosInterval(part, 0.1, Point3(x, y, z)), Wait(0.1)))
            
            allHeadTracks.append(headTracks)

            def getChestTrack(part, attackDelay = attackDelay):
                origScale = part.getScale()
                return Sequence(Wait(attackDelay), LerpHprInterval(part, 1.1, VBase3(180, 0, 0)), Wait(1.1), LerpHprInterval(part, 1.1, part.getHpr()))

            chestTracks = Parallel()
            arms = toon.findAllMatches('**/arms')
            sleeves = toon.findAllMatches('**/sleeves')
            hands = toon.findAllMatches('**/hands')
            print '*************arms hpr=', arms[0].getHpr()
            for partNum in xrange(0, arms.getNumPaths()):
                chestTracks.append(getChestTrack(arms.getPath(partNum)))
                chestTracks.append(getChestTrack(sleeves.getPath(partNum)))
                chestTracks.append(getChestTrack(hands.getPath(partNum)))
            
            allChestTracks.append(chestTracks)

    damageAnims = [['neutral',
      0.01,
      0.01,
      0.5], ['juggle',
      0.01,
      0.01,
      1.48], ['think', 0.01, 2.28]]
    dodgeAnims = []
    dodgeAnims.append(['think',
     0.01,
     0,
     0.6])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.01, dodgeAnimNames=['duck'], showDamageExtraTime=2.1, showMissedExtraTime=2.0)
    return Parallel(suitTrack, partTracks, toonTracks, allHeadTracks, allChestTracks)

def doSacked(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    hips = toon.getHipsParts()
    propDelay = 0.45
    suitDelay = 1.43
    throwDuration = 0.5
    sack = globalPropPool.getProp('sandbag')
    initialScale = Point3(0.5, 0.5, 0.5)
    scaleUpPoint = Point3(0.5, 0.5, 0.5) * 4.0
    sackHpr = VBase3(0, 0, 0)
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    posPoints = [Point3(-0.35, 0, 0), VBase3(0, 180, 0)]
    sackAppearTrack = Sequence(getPropAppearTrack(sack, suit.getRightHand(), posPoints, propDelay, initialScale, scaleUpTime=0.25))
    propDelay = propDelay + 0.2
    sackAppearTrack.append(Wait(suitDelay))
    hitPoint = toon.getPos(battle)
    if dmg > 0:
        hitPoint.setY(hitPoint.getY() + 0.9)
    else:
        hitPoint.setZ(hitPoint.getZ() - 0.2)
    sackAppearTrack.append(Func(battle.movie.needRestoreRenderProp, sack))
    sackAppearTrack.append(getThrowTrack(sack, hitPoint, duration=throwDuration, parent=battle, gravity=-200))
    explodePosPoints = [Point3(0, 0, 0), MovieUtil.PNT3_ZERO]
    if dmg > 0:
        sack2 = MovieUtil.copyProp(sack)
        splatName = 'dust'
        splat = globalPropPool.getProp('dust')
        explode = globalPropPool.getProp('dust')
        explode.setTwoSided(True)
        explode.setBillboardPointWorld(2)
        explodeTrack = Sequence()
        explodeTrack.append(
            getPropAppearTrack(explode, toon, explodePosPoints, 0, Point3(3, 3, 3), scaleUpTime=0))
        explodeTrack.append(Sequence(ActorInterval(explode, splatName), Func(explode.detachNode)))
        hips1 = hips.getPath(2)
        hips2 = hips.getPath(1)
        sack2.hide()
        sack2.reparentTo(battle)
        sack2.setPos(Point3(hitPoint.getX(), hitPoint.getY(), hitPoint.getZ()))
        sack2.setScale(scaleUpPoint)
        sack2.setHpr(sackHpr)
        sackAppearTrack.append(Func(battle.movie.needRestoreHips))
        sackAppearTrack.append(Func(sack.wrtReparentTo, hips1))
        sackAppearTrack.append(Func(sack2.show))
        sackAppearTrack.append(Func(sack2.wrtReparentTo, hips2))
        sackAppearTrack.append(Func(MovieUtil.removeProp, sack2))
        sackAppearTrack.append(Func(MovieUtil.removeProp, sack))
        soundTrack = getSoundTrack('LB_evidence_miss.ogg', node=suit)
        sackAppearTrack.append(Parallel(explodeTrack, soundTrack))
        sackAppearTrack.append(Wait(2.4))
        sackAppearTrack.append(Func(battle.movie.clearRestoreHips))
        scaleTrack = Sequence(Wait(propDelay + suitDelay), LerpScaleInterval(sack, throwDuration, scaleUpPoint), Wait(1.8), LerpScaleInterval(sack, 0.3, MovieUtil.PNT3_NEARZERO))
        hprTrack = Sequence(Wait(propDelay + suitDelay), LerpHprInterval(sack, throwDuration, sackHpr))
        sackTrack = Sequence(Parallel(sackAppearTrack, scaleTrack, hprTrack), Func(MovieUtil.removeProp, sack), Func(battle.movie.clearRenderProp, sack))
    else:
        sackAppearTrack.append(Wait(1.1))
        sackAppearTrack.append(LerpScaleInterval(sack, 0.3, MovieUtil.PNT3_NEARZERO))
        sackTrack = Sequence(sackAppearTrack, Func(MovieUtil.removeProp, sack), Func(battle.movie.clearRenderProp, sack))
    damageAnims = [['struggle',
      0.01,
      0.01,
      0.7], ['slip-backward', 0.01, 0.45]]
    soundTrack = getSoundTrack('SA_sacked.ogg', node=suit)
    toonTrack = getToonTrack(attack, damageDelay=propDelay + suitDelay + throwDuration, splicedDamageAnims=damageAnims, dodgeDelay=1.0, dodgeAnimNames=['sidestep'], showDamageExtraTime=0.8, showMissedExtraTime=0.8)
    return Parallel(suitTrack, toonTrack, soundTrack, sackTrack)


def doGlowerPower(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']

    suitTrack = getSuitTrack(attack)
    suitName = suit.getStyleName()
    DefaultPoints = (
        [Point3(0.4, 3.8, 3.7), MovieUtil.PNT3_ZERO],
        [Point3(-0.4, 3.8, 3.7), MovieUtil.PNT3_ZERO],
    )
    PosPoints = {
        "dopr": (
            [Point3(0.6, 4.5, 5.55), MovieUtil.PNT3_ZERO],
            [Point3(-0.3, 4.5, 5.55), MovieUtil.PNT3_ZERO],
        ),
        "dopa": (
            [Point3(0.6, 5.2, 7.6), MovieUtil.PNT3_ZERO],
            [Point3(-0.4, 5.2, 7.6), MovieUtil.PNT3_ZERO],
        ),
        "tw": (
            [Point3(0.45, 3.5, 3.9), MovieUtil.PNT3_ZERO],
            [Point3(-0.35, 3.5, 3.9), MovieUtil.PNT3_ZERO],
        ),
        "asm": (
            [Point3(0.45, 3.5, 5.9), MovieUtil.PNT3_ZERO],
            [Point3(-0.35, 3.5, 5.9), MovieUtil.PNT3_ZERO],
        ),
        "ad": (
            [Point3(0.36, 4.2, 4.55), MovieUtil.PNT3_ZERO],
            [Point3(-0.36, 4.2, 4.55), MovieUtil.PNT3_ZERO],
        ),
        "phouse": (
            [Point3(0.36, 4.2, 4.55), MovieUtil.PNT3_ZERO],
            [Point3(-0.36, 4.2, 4.55), MovieUtil.PNT3_ZERO],
        ),
        "lvw": (
            [Point3(0.36, 4.2, 4.75), MovieUtil.PNT3_ZERO],
            [Point3(-0.36, 4.2, 4.75), MovieUtil.PNT3_ZERO],
        ),
        "shrp": (
            [Point3(0.36, 4.2, 4.75), MovieUtil.PNT3_ZERO],
            [Point3(-0.36, 4.2, 4.75), MovieUtil.PNT3_ZERO],
        ),
        "hh": (
            [Point3(0.54, 4.3, 5.4), MovieUtil.PNT3_ZERO],
            [Point3(-0.06, 4.3, 5.4), MovieUtil.PNT3_ZERO],
        ),
         "sfs": (
            [Point3(0.54, 4.3, 5.4), MovieUtil.PNT3_ZERO],
            [Point3(-0.06, 4.3, 5.4), MovieUtil.PNT3_ZERO],
        ),
         "gzt": (
            [Point3(0.54, 4.3, 5.4), MovieUtil.PNT3_ZERO],
            [Point3(-0.06, 4.3, 5.4), MovieUtil.PNT3_ZERO],
        ),
        "mldr": (
            [Point3(0.54, 4.3, 5.4), MovieUtil.PNT3_ZERO],
            [Point3(-0.06, 4.3, 5.4), MovieUtil.PNT3_ZERO],
        ),
        "sab": (
            [Point3(0.54, 4.3, 5.4), MovieUtil.PNT3_ZERO],
            [Point3(-0.06, 4.3, 5.4), MovieUtil.PNT3_ZERO],
        ),
        "tbc": (
            [Point3(0.6, 5.3, 6.0), MovieUtil.PNT3_ZERO],
            [Point3(-0.1, 5.3, 6.0), MovieUtil.PNT3_ZERO],
        ),
        "txl": (
            [Point3(0.6, 5.3, 6.25), MovieUtil.PNT3_ZERO],
            [Point3(-0.1, 5.3, 6.25), MovieUtil.PNT3_ZERO],
        ),
         "drk": (
            [Point3(0.6, 5.3, 6.0), MovieUtil.PNT3_ZERO],
            [Point3(-0.1, 5.3, 6.0), MovieUtil.PNT3_ZERO],
        ),
        "ambass": (
            [Point3(0.6, 5.3, 6.0), MovieUtil.PNT3_ZERO],
            [Point3(-0.1, 5.3, 6.0), MovieUtil.PNT3_ZERO],
        ),
        "liquid": (
            [Point3(0.6, 5.3, 6.0), MovieUtil.PNT3_ZERO],
            [Point3(-0.1, 5.3, 6.0), MovieUtil.PNT3_ZERO],
        ),
        "ubuster": (
            [Point3(0.6, 5.3, 6.0), MovieUtil.PNT3_ZERO],
            [Point3(-0.1, 5.3, 6.0), MovieUtil.PNT3_ZERO],
        ),
        "hustle": (
            [Point3(0.6, 5.3, 5.0), MovieUtil.PNT3_ZERO],
            [Point3(-0.1, 5.3, 5.0), MovieUtil.PNT3_ZERO],
        ),
        "autocad": (
            [Point3(0.4, 3.8, 3.7), MovieUtil.PNT3_ZERO],
            [Point3(-0.1, 3.8, 3.7), MovieUtil.PNT3_ZERO],
        ),
        "cdirector": (
            [Point3(0.6, 5.8, 6.45), MovieUtil.PNT3_ZERO],
            [Point3(0.0, 5.8, 6.45), MovieUtil.PNT3_ZERO],
        ),
        "clubpres": (
            [Point3(0.7, 5.5, 6.8), MovieUtil.PNT3_ZERO],
            [Point3(0.1, 5.5, 6.8), MovieUtil.PNT3_ZERO],
        ),
        "chainsaw": (
            [Point3(0.6, 5.8, 6.2), MovieUtil.PNT3_ZERO],
            [Point3(0.0, 5.8, 6.2), MovieUtil.PNT3_ZERO],
        ),
        "dl": (
            [Point3(0.66, 4.2, 4.85), MovieUtil.PNT3_ZERO],
            [Point3(-0.06, 4.2, 4.85), MovieUtil.PNT3_ZERO],
        ),
        "shw": (
            [Point3(1.3, 4.75, 6.2), MovieUtil.PNT3_ZERO],
            [Point3(-0.9, 4.75, 6.2), MovieUtil.PNT3_ZERO],
        ),
    }
    leftKnifeTracks = Parallel()
    rightKnifeTracks = Parallel()
    leftPosPoints, rightPosPoints = PosPoints.get(
            suit.dna.name, DefaultPoints
        )
    for t in targets:
        leftKnives = []
        rightKnives = []
        for i in xrange(0, 3):
            leftKnives.append(globalPropPool.getProp('dagger'))
            rightKnives.append(globalPropPool.getProp('dagger'))

        for i in xrange(0, 3):
            knifeDelay = 0.11
            leftTrack = Sequence()
            leftTrack.append(Wait(1.1))
            leftTrack.append(Wait(i * knifeDelay))
            leftTrack.append(getPropAppearTrack(leftKnives[i], suit, leftPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
            leftTrack.append(getPropThrowTrack(attack, leftKnives[i], hitPointNames=['face'], missPointNames=['miss'], hitDuration=0.3, missDuration=0.3, target=t))
            leftKnifeTracks.append(leftTrack)
            rightTrack = Sequence()
            rightTrack.append(Wait(1.1))
            rightTrack.append(Wait(i * knifeDelay))
            rightTrack.append(getPropAppearTrack(rightKnives[i], suit, rightPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
            rightTrack.append(getPropThrowTrack(attack, rightKnives[i], hitPointNames=['face'], missPointNames=['miss'], hitDuration=0.3, missDuration=0.3, target=t))
            rightKnifeTracks.append(rightTrack)

    damageAnims = [['slip-backward', 0.01, 0.35]]
    toonTracks = getToonTracks(attack, damageDelay=1.6, splicedDamageAnims=damageAnims, dodgeDelay=0.7, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_glower_power.ogg', delay=1.1, node=suit)
    return Parallel(suitTrack, toonTracks, soundTrack, leftKnifeTracks, rightKnifeTracks)

def doHalfWindsor(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitType = getSuitBodyType(attack['suitName'])
    throwDelay = 1.0
    damageDelay = throwDelay + 1.23
    dodgeDelay = damageDelay - 0.20
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'c':
        posPoints = [Point3(-0.04341534008683112, -1.0853835021707674, 0.04341534008683112), VBase3(87.00434153400869, -180.0, -257.88712011577422)]
    elif suitType == 'b':
        posPoints = [Point3(-0.04341534008683112, -1.0853835021707674, 0.04341534008683112), VBase3(87.00434153400869, -180.0, -257.88712011577422)]
    else:
        posPoints = [Point3(-0.13024602026049337, -1.2590448625180883, 0.04341534008683112), VBase3(87.00434153400869, -180.0, -257.88712011577422)]
    tiePropTracks = Parallel()
    hitAtleastOneToon = False
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = True
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        tie = globalPropPool.getProp('half-windsor')
        tiePropTrack = Sequence(
                        getPropAppearTrack(
                            tie,
                            suit.getRightHand(),
                            posPoints,
                            0.25,
                            Vec3(7, 7, 7),
                            scaleUpTime=0.25,
                            blendType='easeIn',
                        )
                    )
        tiePropTrack.append(Wait(throwDelay))
        tiePropTrack.append(Wait(0.50))
        tiePropTrack.append(Func(battle.movie.needRestoreRenderProp, tie))
        tiePropTrack.append(Func(tie.wrtReparentTo, render))
        tiePropTrack.append(Func(tie.setHpr, Point3(0, -90, 0)))
        if dmg > 0:
            tiePropTrack.append(Parallel(
                ProjectileInterval(
                    tie, endPos=__toonFacePoint(toon), duration=0.3, gravityMult=-5.0,
                ),
                LerpHprInterval(tie, 0.3, (110, 160, 0)),
            ))
        else:
            startH, endH = -180, -280
            yoffset = random.randint(0, 20) / 10.0
            xoffset = random.randint(-7, 7) / 10.0
            tiePropTrack.append(Parallel(
                ProjectileInterval(
                    tie, endPos=__toonGroundPoint(attack, toon, 0.1) + Vec3(0, 4 + yoffset, 0), duration=0.5, gravityMult=4.0,
                ),
                LerpHprInterval(tie, 0.5, (startH, 270, 0)),
            ))
            tiePropTrack.append(Parallel(
                ProjectileInterval(
                    tie, endPos=__toonGroundPoint(attack, toon, 0.1) + Vec3(xoffset, 3.5 + yoffset, 0), duration=0.15, gravityMult=1.0,
                ),
                LerpHprInterval(tie, 0.30, (endH + random.randint(-30, 30), 270, 45), blendType='easeOut'),
                Wait(0.60),
            ))
            tiePropTrack.append(LerpScaleInterval(tie, duration=0.30, scale=MovieUtil.PNT3_NEARZERO, blendType='easeIn'))
        tiePropTrack.append(Func(tie.removeNode))
        tiePropTracks.append(tiePropTrack)
    soundTrack = getSoundTrack('LB_evidence_miss.ogg', node=suit)
    toonTrack = getToonTracks(attack, damageDelay, ['slip-backward'], dodgeDelay, ['neutral'])
    throwSound = getSoundTrack('SA_half_windsor_throw.ogg', delay=throwDelay + 0.8, node=suit)
    if hitAtleastOneToon:
        hitSound = getSoundTrack('SA_writeoff_ding_only.ogg', delay=throwDelay + 1.05, node=suit)
        return Parallel(suitTrack, toonTrack, tiePropTracks, throwSound, hitSound)
    else:
        return Parallel(suitTrack, toonTrack, tiePropTracks, throwSound)


def doHalfWindsorOLD(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    throwDelay = 1.25
    damageDelay = 2.25
    dodgeDelay = 1
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'c':
        posPoints = [Point3(0.04341534008683112, -1.0853835021707674, -0.04341534008683112), VBase3(87.00434153400869, 176.3531114327062, 176.61360347322716)]
    elif suitType == 'b':
        posPoints = [Point3(-0.04341534008683112, -1.0853835021707674, 0.04341534008683112), VBase3(87.00434153400869, -180.0, -257.88712011577422)]
    else:
        posPoints = [Point3(-0.13024602026049337, -1.2590448625180883, 0.04341534008683112), VBase3(87.00434153400869, -180.0, -257.88712011577422)]
    tiePropTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        tie = globalPropPool.getProp('half-windsor')
        splatName = 'dust'
        splat = globalPropPool.getProp('dust')
        hitPoint = toon.getPos(battle)
        hitPoint.setX(hitPoint.getX() + 1.5)
        hitPoint.setY(hitPoint.getY() + 1.5)
        hitPoint.setZ(hitPoint.getZ() + .75)
        missPoint2 = toon.getPos(battle)
        missPoint2.setX(hitPoint.getX() + 1.5)
        missPoint2.setY(hitPoint.getY() - 7)
        missPoint = Point3(missPoint2.getX(), missPoint2.getY(), missPoint2.getZ())
        explode = globalPropPool.getProp('dust')
        explode.setTwoSided(True)
        explode.setBillboardPointWorld(2)
        explodeTrack = Sequence()
        if dmg > 0:
            explodePosPoints = [Point3(0, 0, 0), MovieUtil.PNT3_ZERO]
            tiePropTrack = Sequence(
                getPropAppearTrack(tie, suit.getRightHand(), posPoints, 0.5, Point3(7, 7, 7), scaleUpTime=0.25))
            tiePropTrack.append(Wait(throwDelay))
            tiePropTrack.append(Func(tie.setBillboardPointEye))
            tiePropTrack.append(
                getPropThrowTrack(attack, tie, [__toonFacePoint(toon)], [__toonGroundPoint(attack, toon, 0.1)],
                                  hitDuration=0.25, missDuration=0.8, target=t))
            explodeTrack.append(
                getPropAppearTrack(explode, toon, explodePosPoints, 0, Point3(2, 2, 2), scaleUpTime=0))
            explodeTrack.append(Sequence(ActorInterval(explode, splatName), Func(explode.detachNode)))
        else:
            explodePosPoints = [Point3(0, -7, 0), MovieUtil.PNT3_ZERO]
            tiePropTrack = Sequence(
                getPropAppearTrack(tie, suit.getRightHand(), posPoints, 0.5, Point3(7, 7, 7), scaleUpTime=0.25))
            tiePropTrack.append(Wait(throwDelay))
            tiePropTrack.append(getThrowTrack(tie, missPoint2, duration=0.5, parent=battle, gravity=-300))
            tiePropTrack.append(LerpHprInterval(tie, 0, VBase3(0, 90, 0)))
            explodeTrack.append(
                getPropAppearTrack(explode, toon, explodePosPoints, 0, Point3(2, 2, 2), scaleUpTime=0))
            explodeTrack.append(Sequence(ActorInterval(explode, splatName), Func(explode.detachNode)))
            tiePropTrack.append(Wait(0.6))
            tiePropTrack.append(LerpPosInterval(tie, 0.4, missPoint))
            tiePropTrack.append(LerpScaleInterval(tie, 0.1, MovieUtil.PNT3_NEARZERO))
            tiePropTrack.append(Func(MovieUtil.removeProp, tie))
            tiePropTrack.append(Func(battle.movie.clearRenderProp, tie))
        soundTrack = getSoundTrack('LB_evidence_miss.ogg', node=suit)
        tiePropTrack.append(Parallel(explodeTrack, soundTrack))
        tiePropTracks.append(tiePropTrack)

    damageAnims = [['conked',
      0.01,
      0.01,
      0.4], ['cringe', 0.01, 0.7]]
    soundTrack = getSoundTrack('SA_half_windsor_throw.ogg', delay=2.0, node=suit)
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['duck'])
    return Parallel(suitTrack, toonTracks, tiePropTracks, soundTrack)


def doDoubleWindsor(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    throwDelay = 1.25
    damageDelay = 2.25
    dodgeDelay = 2
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    posPoints = [Point3(-1, 0.5, -.1), VBase3(99, -90, -108.2)]
    tiePropTracks = Parallel()
    for t in targets:
        toon = t['toon']
        tie = globalPropPool.getProp('double-windsor')
        tiePropTrack = getPropAppearTrack(tie, suit.getRightHand(), posPoints, 0.5, Point3(7, 7, 7), scaleUpTime=0.25)
        tiePropTrack.append(Wait(throwDelay))
        missPoint = __toonMissBehindPoint(toon, parent=battle)
        missPoint.setX(missPoint.getX() - 1.1)
        missPoint.setZ(missPoint.getZ() + 4)
        hitPoint = __toonFacePoint(toon, parent=battle)
        hitPoint.setX(hitPoint.getX() - 1.1)
        hitPoint.setY(hitPoint.getY() - 0.7)
        hitPoint.setZ(hitPoint.getZ() + 0.9)
        explodePosPoints = [Point3(0, 0, 0), MovieUtil.PNT3_ZERO]
        splatName = 'dust'
        splat = globalPropPool.getProp('dust')
        explode = globalPropPool.getProp('dust')
        explode.setTwoSided(True)


        explode.setBillboardPointWorld(2)
        explodeTrack = Sequence()
        explodeTrack.append(
        getPropAppearTrack(explode, toon, explodePosPoints, 0, Point3(2, 2, 2), scaleUpTime=0))
        explodeTrack.append(Sequence(ActorInterval(explode, splatName), Func(explode.detachNode)))
        tiePropTrack.append(getPropThrowTrack(attack, tie, [hitPoint], [missPoint], hitDuration=0.25, missDuration=0.8, missScaleDown=0.3, parent=battle, target=t))
        soundTrack = getSoundTrack('LB_evidence_miss.ogg', node=suit)
        tiePropTrack.append(Parallel(explodeTrack, soundTrack))
        tiePropTracks.append(tiePropTrack)

    damageAnims = [['conked',
      0.01,
      0.01,
      0.4], ['cringe', 0.01, 0.7]]
    soundTrack = getSoundTrack('SA_half_windsor_throw.ogg', delay=2.0, node=suit)
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    return Parallel(suitTrack, toonTracks, tiePropTracks, soundTrack)


def doHeadShrink(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    hitAtleastOneToon = False
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = True

    damageDelay = 1.5
    dodgeDelay = 0.9
    shrinkSprays = [BattleParticles.createParticleEffect(file='headShrinkSpray') for t in targets]
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    sprayTracks = getPartTracks(attack, shrinkSprays, 0.3, 2.4, 0, softStop=-1)
    cloudTracks = Parallel()
    shrinkTracks = Parallel()
    dropTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        shrinkCloud = BattleParticles.createParticleEffect(file='headShrinkCloud')
        shrinkDrop = BattleParticles.createParticleEffect(file='headShrinkDrop')
        shrinkCloud.reparentTo(battle)
        adjust = 0.4
        x = toon.getX(battle)
        y = toon.getY(battle) - adjust
        z = 8
        shrinkCloud.setPos(Point3(x, y, z))
        shrinkDrop.setPos(Point3(0, 0 - adjust, 7.5))
        off = 0.7
        cloudPoints = [Point3(x + off, y, z),
         Point3(x + off / 2, y + off / 2, z),
         Point3(x, y + off, z),
         Point3(x - off / 2, y + off / 2, z),
         Point3(x - off, y, z),
         Point3(x - off / 2, y - off / 2, z),
         Point3(x, y - off, z),
         Point3(x + off / 2, y - off / 2, z),
         Point3(x + off, y, z),
         Point3(x, y, z)]
        circleTrack = Sequence()
        for point in cloudPoints:
            circleTrack.append(LerpPosInterval(shrinkCloud, 0.14, point, other=battle))

        cloudTrack = Sequence()
        cloudTrack.append(Wait(0.82))
        cloudTrack.append(Func(battle.movie.needRestoreParticleEffect, shrinkCloud))
        cloudTrack.append(Func(shrinkCloud.start, battle))
        cloudTrack.append(circleTrack)
        cloudTrack.append(circleTrack)
        cloudTrack.append(LerpFunctionInterval(shrinkCloud.setAlphaScale, fromData=1, toData=0, duration=0.7))
        cloudTrack.append(Func(shrinkCloud.cleanup))
        cloudTrack.append(Func(battle.movie.clearRestoreParticleEffect, shrinkCloud))
        cloudTracks.append(cloudTrack)
        shrinkDelay = 0.4
        shrinkDuration = 0.6
        shrinkTrack = Sequence()
        if dmg > 0:
            headParts = toon.getHeadParts()
            initialScale = headParts.getPath(0).getScale()[0]
            shrinkTrack.append(Wait(damageDelay + shrinkDelay))

            def scaleHeadParallel(scale, duration, headParts = headParts):
                headTracks = Parallel()
                for partNum in xrange(0, headParts.getNumPaths()):
                    nextPart = headParts.getPath(partNum)
                    headTracks.append(LerpScaleInterval(nextPart, duration, Point3(scale, scale, scale)))

                return headTracks

            shrinkTrack.append(Func(battle.movie.needRestoreHeadScale))
            shrinkTrack.append(scaleHeadParallel(0.6, shrinkDuration))
            shrinkTrack.append(Wait(1.0))
            shrinkTrack.append(scaleHeadParallel(initialScale * 3.2, 0.4))
            shrinkTrack.append(scaleHeadParallel(initialScale * 0.7, 0.4))
            shrinkTrack.append(scaleHeadParallel(initialScale * 2.5, 0.3))
            shrinkTrack.append(scaleHeadParallel(initialScale * 0.8, 0.3))
            shrinkTrack.append(scaleHeadParallel(initialScale * 1.9, 0.2))
            shrinkTrack.append(scaleHeadParallel(initialScale * 0.85, 0.2))
            shrinkTrack.append(scaleHeadParallel(initialScale * 1.7, 0.15))
            shrinkTrack.append(scaleHeadParallel(initialScale * 0.9, 0.15))
            shrinkTrack.append(scaleHeadParallel(initialScale * 1.3, 0.1))
            shrinkTrack.append(scaleHeadParallel(initialScale, 0.1))
            shrinkTrack.append(Func(battle.movie.clearRestoreHeadScale))
            shrinkTrack.append(Wait(0.7))
            shrinkTracks.append(shrinkTrack)
        dropTracks.append(getPartTrack(shrinkDrop, 1.0, 3.0, [shrinkDrop, toon, 0], softStop=-1))

    damageAnims = []
    damageAnims.append(['cringe',
     0.01,
     0.65,
     0.2])
    damageAnims.extend(getSplicedLerpAnims('cringe', 0.64, 1.0, startTime=0.85))
    damageAnims.append(['cringe', 0.4, 1.49])
    damageAnims.append(['conked',
     0.01,
     3.6,
     -1.6])
    damageAnims.append(['conked',
     0.01,
     3.1,
     0.4])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    if hitAtleastOneToon:
        shrinkSound = globalBattleSoundCache.getSound('SA_head_shrink_only.ogg')
        growSound = globalBattleSoundCache.getSound('SA_head_grow_back_only.ogg')
        soundTrack = Sequence(Wait(1.5), SoundInterval(shrinkSound, duration=2.1, node=suit), SoundInterval(growSound, node=suit))
        return Parallel(suitTrack, sprayTracks, cloudTracks, dropTracks, toonTracks, shrinkTracks, soundTrack)
    else:
        return Parallel(suitTrack, sprayTracks, cloudTracks, dropTracks, toonTracks, shrinkTracks)


def doRolodex(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    toon = targets[0]['toon'] # I normally do not want to, but I'll leave this because the only thing that really needs it is hitPoint, which is pretty much for nothing since Anesidora reveals Disney's Toontown Online cut out one of their Rolodex particles that would have used it.
    rollodex = globalPropPool.getProp('rollodex')
    particleEffect2 = BattleParticles.createParticleEffect(file='rollodexWaterfall')
    particleEffects3 = [BattleParticles.createParticleEffect(file='rollodexStream') for t in targets]
    suitType = getSuitBodyType(attack['suitName'])
    propPosPoints = [Point3(-0.51, -0.03, -0.1), VBase3(89.673, 2.166, 177.786)]
    propScale = Point3(1.2, 1.2, 1.2)
    partDelay = 2.6
    part2Delay = 2.2
    part3Delay = 2.6
    partDuration = 1.6
    part2Duration = 2.3
    part3Duration = 2
    damageDelay = 3.0
    dodgeDelay = 1.9
    hitPoint = lambda toon = toon: __toonFacePoint(toon)
    partTrack2 = getPartTrack(particleEffect2, part2Delay, part2Duration, [particleEffect2, suit, 0], softStop=-1)
    partTracks3 = getPartTracks(attack, particleEffects3, part3Delay, part3Duration, 0, softStop=-1)
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    propTrack = getPropTrack(rollodex, suit.getLeftHand(), propPosPoints, 1e-06, 3.7, scaleUpPoint=propScale, anim=0, propName='rollodex', animDuration=0, animStartTime=0)
    toonTracks = getToonTracks(attack, damageDelay, ['conked'], dodgeDelay, ['sidestep'])
    soundTrack = getSoundTrack('SA_rolodex.ogg', delay=1.8, node=suit)
    return Parallel(suitTrack, toonTracks, propTrack, soundTrack, partTrack2, partTracks3)


def doEvilEye(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 2.44
    dodgeDelay = 1.64
    suitName = suit.getStyleName()
    eyePos = {
            "cr": [Point3(-0.25, 4.85, 5.75), VBase3(-155.0, -20.0, 0.0)],
            "tf": [Point3(-0.4, 3.85, 5.01), VBase3(-155.0, -20.0, 0.0)],
            "shrp": [Point3(-0.4, 3.85, 5.01), VBase3(-155.0, -20.0, 0.0)],
            "rng": [Point3(-0.3, 4.7, 5.3), VBase3(-155.0, -20.0, 0.0)],
            "le": [Point3(-0.3, 4.7, 5.3), VBase3(-155.0, -20.0, 0.0)],
            "le2": [Point3(-0.3, 4.7, 5.3), VBase3(-155.0, -20.0, 0.0)],
            "bsht": [Point3(-0.3, 4.7, 5.3), VBase3(-155.0, -20.0, 0.0)],
            "nsh": [Point3(-0.3, 4.7, 5.3), VBase3(-155.0, -20.0, 0.0)],
            "dl": [Point3(-0.35, 4.0, 5.01), VBase3(-155.0, -20.0, 0.0)],
            "txm": [Point3(-0.35, 4.0, 5.01), VBase3(-155.0, -20.0, 0.0)],
            "br": [Point3(-0.4, 5.0, 5.5), VBase3(-155.0, -20.0, 0.0)],
            "itn": [Point3(-0.4, 5.0, 5.5), VBase3(-155.0, -20.0, 0.0)],
            "lgator": [Point3(-0.35, 5.5, 6.4), VBase3(-155.0, -20.0, 0.0)],
            "ubuster": [Point3(-0.35, 5.5, 6.4), VBase3(-155.0, -20.0, 0.0)],
            "wsi": [Point3(-0.35, 5.5, 6.4), VBase3(-155.0, -20.0, 0.0)],
        }

    posPoints = eyePos.get(
            suit.dna.name,
            [Point3(-0.4, 3.65, 5.01), VBase3(-155.0, -20.0, 0.0)],
        )
    appearDelay = 0.8
    suitHoldStart = 1.06
    suitHoldStop = 1.69
    suitHoldDuration = suitHoldStop - suitHoldStart
    eyeHoldDuration = 1.1
    moveDuration = 1.1
    suitSplicedAnims = []
    suitSplicedAnims.append(['glower',
     0.01,
     0.01,
     suitHoldStart])
    suitSplicedAnims.extend(getSplicedLerpAnims('glower', suitHoldDuration, 1.1, startTime=suitHoldStart))
    suitSplicedAnims.append(['glower', 0.01, suitHoldStop])
    suitTrack = getSuitTrack(attack, splicedAnims=suitSplicedAnims)
    eyePropTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        eye = globalPropPool.getProp('evil-eye')
        eyeAppearTrack = Sequence(Wait(suitHoldStart), Func(__showProp, eye, suit, posPoints[0], posPoints[1]), LerpScaleInterval(eye, suitHoldDuration, Point3(11, 11, 11)), Wait(eyeHoldDuration * 0.3), LerpHprInterval(eye, 0.02, Point3(205, 40, 0)), Wait(eyeHoldDuration * 0.7), Func(battle.movie.needRestoreRenderProp, eye), Func(eye.wrtReparentTo, battle))
        toonFace = __toonFacePoint(toon, parent=battle)
        if dmg > 0:
            lerpInterval = LerpPosInterval(eye, moveDuration, toonFace)
        else:
            lerpInterval = LerpPosInterval(eye, moveDuration, Point3(toonFace.getX(), toonFace.getY() - 5, toonFace.getZ() - 2))
        eyeMoveTrack = lerpInterval
        eyeRollTrack = LerpHprInterval(eye, moveDuration, Point3(0, 0, -180))
        eyePropTrack = Sequence(eyeAppearTrack, Parallel(eyeMoveTrack, eyeRollTrack), Func(battle.movie.clearRenderProp, eye), Func(MovieUtil.removeProp, eye))
        eyePropTracks.append(eyePropTrack)

    damageAnims = [['duck',
      0.01,
      0.01,
      1.4], ['cringe', 0.01, 0.3]]
    toonTracks = getToonTracks(attack, splicedDamageAnims=damageAnims, damageDelay=damageDelay, dodgeDelay=dodgeDelay, dodgeAnimNames=['duck'], showDamageExtraTime=1.7, showMissedExtraTime=1.7)
    soundTrack = getSoundTrack('SA_evil_eye.ogg', delay=1.1, node=suit)
    return Parallel(suitTrack, toonTracks, eyePropTracks, soundTrack)


def doPlayHardball(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    hitAtleastOneToon = False
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = True

    suitType = getSuitBodyType(attack['suitName'])
    suitDelay = 1.3
    damageDelay = 2.25
    dodgeDelay = 1.86
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    ballPosPoints = [Point3(-0.25, 0.03, -0.31), VBase3(-1.152, 86.581, -76.784)]
    propTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        ball = globalPropPool.getProp('baseball')
        propTrack = Sequence(getPropAppearTrack(ball, suit.getRightHand(), ballPosPoints, 0.5, Point3(7, 7, 7), scaleUpTime=0.25))
        propTrack.append(Wait(suitDelay))
        propTrack.append(Func(battle.movie.needRestoreRenderProp, ball))
        propTrack.append(Func(ball.wrtReparentTo, battle))
        toonPos = toon.getPos(battle)
        x = toonPos.getX()
        y = toonPos.getY()
        z = toonPos.getZ()
        z = z + 0.2
        if dmg > 0:
            propTrack.append(LerpPosInterval(ball, 0.25, __toonFacePoint(toon, parent=battle)))
            propTrack.append(LerpPosInterval(ball, 0.5, Point3(x, y + 3, z)))
            propTrack.append(LerpPosInterval(ball, 0.4, Point3(x, y + 5, z + 2)))
            propTrack.append(LerpPosInterval(ball, 0.3, Point3(x, y + 6, z)))
            propTrack.append(LerpPosInterval(ball, 0.1, Point3(x, y + 7, z + 1)))
            propTrack.append(LerpPosInterval(ball, 0.1, Point3(x, y + 8, z)))
            propTrack.append(LerpPosInterval(ball, 0.1, Point3(x, y + 8.5, z + 0.6)))
            propTrack.append(LerpPosInterval(ball, 0.1, Point3(x, y + 9, z + 0.2)))
        else:
            propTrack.append(LerpPosInterval(ball, 0.25, Point3(x, y + 2, z)))
            propTrack.append(LerpPosInterval(ball, 0.4, Point3(x, y - 1, z + 2)))
            propTrack.append(LerpPosInterval(ball, 0.3, Point3(x, y - 3, z)))
            propTrack.append(LerpPosInterval(ball, 0.1, Point3(x, y - 4, z + 1)))
            propTrack.append(LerpPosInterval(ball, 0.1, Point3(x, y - 5, z)))
            propTrack.append(LerpPosInterval(ball, 0.1, Point3(x, y - 5.5, z + 0.6)))
            propTrack.append(LerpPosInterval(ball, 0.1, Point3(x, y - 6, z + 0.2)))
        propTrack.append(Wait(0.4))
        propTrack.append(LerpScaleInterval(ball, 0.3, MovieUtil.PNT3_NEARZERO))
        propTrack.append(Func(MovieUtil.removeProp, ball))
        propTrack.append(Func(battle.movie.clearRenderProp, ball))
        propTracks.append(propTrack)

    damageAnims = [['conked',
      damageDelay,
      0.01,
      0.5], ['slip-backward', 0.01, 0.7]]
    toonTracks = getToonTracks(attack, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'], showDamageExtraTime=3.9)
    soundTrack = getSoundTrack('SA_hardball%s.ogg' % ('_impact_only' if hitAtleastOneToon else ''), delay=1.8, node=suit)
    return Parallel(suitTrack, toonTracks, propTracks, soundTrack)

def doPowerTie(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitType = getSuitBodyType(attack['suitName'])
    throwDelay = 1.0
    damageDelay = throwDelay + 1.23
    dodgeDelay = damageDelay - 0.20
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        posPoints = [Point3(0.10380622837370268, 0.7266435986159152, -1.0380622837370233), VBase3(90, -6.228373702422147, 0)]
    elif suitType == 'b':
        posPoints = [Point3(-0.04341534008683112, 0.6512301013024597, -0.9117221418234465), VBase3(90, 0, 0)]
    else:
        posPoints = [Point3(-0.13024602026049337, 0.5643994211287975, -0.9985528219971052), VBase3(90, 11.201157742402302, 0)]
    tiePropTracks = Parallel()
    hitAtleastOneToon = False
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = True
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        tie = globalPropPool.getProp('power-tie')
        tiePropTrack = Sequence(
                        getPropAppearTrack(
                            tie,
                            suit.getRightHand(),
                            posPoints,
                            0.25,
                            Vec3(3.5, 3.5, 3.5),
                            scaleUpTime=0.25,
                            blendType='easeIn',
                        )
                    )
        tiePropTrack.append(Wait(throwDelay))
        tiePropTrack.append(Wait(0.50))
        tiePropTrack.append(Func(battle.movie.needRestoreRenderProp, tie))
        tiePropTrack.append(Func(tie.wrtReparentTo, render))
        tiePropTrack.append(Func(tie.setHpr, Point3(0, -90, 0)))
        if dmg > 0:
            tiePropTrack.append(Parallel(
                ProjectileInterval(
                    tie, endPos=__toonFacePoint(toon), duration=0.3, gravityMult=-5.0,
                ),
                LerpHprInterval(tie, 0.3, (110, 160, 0)),
            ))
        else:
            startH, endH = 180, 240
            yoffset = random.randint(0, 20) / 10.0
            xoffset = random.randint(-7, 7) / 10.0
            tiePropTrack.append(Parallel(
                ProjectileInterval(
                    tie, endPos=__toonGroundPoint(attack, toon, 0.1) + Vec3(0, 4 + yoffset, 0), duration=0.5, gravityMult=4.0,
                ),
                LerpHprInterval(tie, 0.5, (startH, 270, 0)),
            ))
            tiePropTrack.append(Parallel(
                ProjectileInterval(
                    tie, endPos=__toonGroundPoint(attack, toon, 0.1) + Vec3(xoffset, 3.5 + yoffset, 0), duration=0.15, gravityMult=1.0,
                ),
                LerpHprInterval(tie, 0.30, (endH + random.randint(-30, 30), 270, 45), blendType='easeOut'),
                Wait(0.60),
            ))
            tiePropTrack.append(LerpScaleInterval(tie, duration=0.30, scale=MovieUtil.PNT3_NEARZERO, blendType='easeIn'))
        tiePropTrack.append(Func(tie.removeNode))
        tiePropTracks.append(tiePropTrack)
    soundTrack = getSoundTrack('LB_evidence_miss.ogg', node=suit)
    toonTrack = getToonTracks(attack, damageDelay, ['slip-backward'], dodgeDelay, ['neutral'])
    throwSound = getSoundTrack('SA_powertie_throw.ogg', delay=throwDelay + 0.8, node=suit)
    if hitAtleastOneToon:
        hitSound = getSoundTrack('SA_powertie_impact.ogg', delay=throwDelay + 1.05, node=suit)
        return Parallel(suitTrack, toonTrack, tiePropTracks, throwSound, hitSound)
    else:
        return Parallel(suitTrack, toonTrack, tiePropTracks, throwSound)


def doPowerTieOLD(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    hitAtleastOneToon = False
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = True

    suitType = getSuitBodyType(attack['suitName'])
    throwDelay = 1.25
    damageDelay = 2
    dodgeDelay = 1
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    if suitType == 'a':
        posPoints = [Point3(0.10380622837370268, 0.7266435986159152, -1.0380622837370233), VBase3(90, -6.228373702422147, 0)]
    elif suitType == 'b':
        posPoints = [Point3(-0.04341534008683112, 0.6512301013024597, -0.9117221418234465), VBase3(90, 0, 0)]
    else:
        posPoints = [Point3(-0.13024602026049337, 0.5643994211287975, -0.9985528219971052), VBase3(90, 11.201157742402302, 0)]
    tiePropTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        tie = globalPropPool.getProp('power-tie')
        splatName = 'dust'
        splat = globalPropPool.getProp('dust')
        hitPoint = toon.getPos(battle)
        hitPoint.setX(hitPoint.getX() + 1.5)
        hitPoint.setY(hitPoint.getY() + 1.5)
        hitPoint.setZ(hitPoint.getZ() + .75)
        missPoint2 = toon.getPos(battle)
        missPoint2.setX(hitPoint.getX() + 1.5)
        missPoint2.setY(hitPoint.getY() - 7)
        missPoint = Point3(missPoint2.getX(), missPoint2.getY(), missPoint2.getZ())
        explode = globalPropPool.getProp('dust')
        explode.setTwoSided(True)
        explode.setBillboardPointWorld(2)
        explodeTrack = Sequence()
        if dmg > 0:
            explodePosPoints = [Point3(0, 0, 0), MovieUtil.PNT3_ZERO]
            tiePropTrack = Sequence(
                getPropAppearTrack(tie, suit.getRightHand(), posPoints, 0.5, Point3(3.5, 3.5, 3.5), scaleUpTime=0.25))
            tiePropTrack.append(Wait(throwDelay))
            tiePropTrack.append(Func(tie.setBillboardPointEye))
            tiePropTrack.append(
                getPropThrowTrack(attack, tie, [__toonFacePoint(toon)], [__toonGroundPoint(attack, toon, 0.1)],
                                  hitDuration=0.25, missDuration=0.8, target=t))
            explodeTrack.append(
                getPropAppearTrack(explode, toon, explodePosPoints, 0, Point3(2, 2, 2), scaleUpTime=0))
            explodeTrack.append(Sequence(ActorInterval(explode, splatName), Func(explode.detachNode)))
        else:
            explodePosPoints = [Point3(0, -7, 0), MovieUtil.PNT3_ZERO]
            tiePropTrack = Sequence(
                getPropAppearTrack(tie, suit.getRightHand(), posPoints, 0.5, Point3(3.5, 3.5, 3.5), scaleUpTime=0.25))
            tiePropTrack.append(Wait(throwDelay))
            tiePropTrack.append(getThrowTrack(tie, missPoint2, duration=0.5, parent=battle, gravity=-300))
            tiePropTrack.append(LerpHprInterval(tie, 0, VBase3(0, 90, 0)))
            explodeTrack.append(
                getPropAppearTrack(explode, toon, explodePosPoints, 0, Point3(2, 2, 2), scaleUpTime=0))
            explodeTrack.append(Sequence(ActorInterval(explode, splatName), Func(explode.detachNode)))
            tiePropTrack.append(Wait(0.6))
            tiePropTrack.append(LerpPosInterval(tie, 0.4, missPoint))
            tiePropTrack.append(LerpScaleInterval(tie, 0.1, MovieUtil.PNT3_NEARZERO))
            tiePropTrack.append(Func(MovieUtil.removeProp, tie))
            tiePropTrack.append(Func(battle.movie.clearRenderProp, tie))
        soundTrack = getSoundTrack('LB_evidence_miss.ogg', node=suit)
        tiePropTrack.append(Parallel(explodeTrack, soundTrack))
        tiePropTracks.append(tiePropTrack)

    toonTracks = getToonTracks(attack, damageDelay, ['conked'], dodgeDelay, ['duck'])
    throwSound = getSoundTrack('SA_powertie_throw.ogg', delay=2, node=suit)
    if hitAtleastOneToon:
        hitSound = getSoundTrack('SA_powertie_impact.ogg', delay=2.4, node=suit)
        return Parallel(suitTrack, toonTracks, tiePropTracks, throwSound, hitSound)
    else:
        return Parallel(suitTrack, toonTracks, tiePropTracks, throwSound)

def doCloseTheLoop(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    centerColor = Vec4(0.1, 0.1, 0.1, 0.4)
    edgeColor = Vec4(0.4, 0.1, 0.9, 0.7)
    powerBar1 = BattleParticles.createParticleEffect(file='powertrip')
    powerBar2 = BattleParticles.createParticleEffect(file='powertrip2')
    powerBar1.setPos(0, 6.1, 0.4)
    powerBar1.setHpr(-60, 0, 0)
    powerBar2.setPos(0, 6.1, 0.4)
    powerBar2.setHpr(60, 0, 0)
    powerBar1Particles = powerBar1.getParticlesNamed('particles-1')
    powerBar2Particles = powerBar2.getParticlesNamed('particles-1')
    powerBar1Particles.renderer.setCenterColor(centerColor)
    powerBar1Particles.renderer.setEdgeColor(edgeColor)
    powerBar2Particles.renderer.setCenterColor(centerColor)
    powerBar2Particles.renderer.setEdgeColor(edgeColor)
    waterfallEffect = BattleParticles.createParticleEffect('Waterfall')
    waterfallEffect.setScale(11)
    waterfallParticles = waterfallEffect.getParticlesNamed('particles-1')
    waterfallParticles.renderer.setCenterColor(centerColor)
    waterfallParticles.renderer.setEdgeColor(edgeColor)
    suitName = suit.getStyleName()

    def getPowerTrack(effect, suit = suit, battle = battle):
        partTrack = Sequence(Func(battle.movie.needRestoreParticleEffect, effect), Func(effect.start, suit), LerpFunctionInterval(effect.setAlphaScale, fromData=0, toData=1, duration=1.0), Wait(1.5), LerpPosInterval(effect, 1.0, Point3(0, 25, 0.4)), LerpFunctionInterval(effect.setAlphaScale, fromData=1, toData=0, duration=0.4), Func(effect.cleanup), Func(battle.movie.clearRestoreParticleEffect, effect))
        return partTrack

    partTrack1 = getPowerTrack(powerBar1)
    partTrack2 = getPowerTrack(powerBar2)
    waterfallTrack = getPartTrack(waterfallEffect, 2.5, 2.3, [waterfallEffect, suit, 0], softStop=-1)
    phone = globalPropPool.getProp('phone')
    receiver = globalPropPool.getProp('receiver')
    BattleParticles.loadParticles()

    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        phonePosPoints = [Point3(-0.26011560693641655, 0.26011560693641655, -0.1), VBase3(180, 180, 0)]
        receiverPosPoints = [Point3(0, -0.43352601156069426, -0.8670520231213885), VBase3(90, 0, 0)]
    if suitType == 'b':
        phonePosPoints = [Point3(0.5202312138728296, 0.26011560693641655, 0), VBase3(180, 180, 0)]
        receiverPosPoints = [Point3(-0.23, 0, -0.11), VBase3(5.939, 2.763, -177.591)]
    if suitType == 'c':
        phonePosPoints = [Point3(0.5202312138728296, 0.26011560693641655, 0), VBase3(180, 180, 0)]
        receiverPosPoints = [Point3(-0.23, 0, -0.11), VBase3(5.939, 2.763, -177.591)]
    propTrack = Sequence(Func(__showProp, phone, suit.getLeftHand(), *phonePosPoints), Func(__showProp, receiver, suit.getLeftHand(), *receiverPosPoints), LerpScaleInterval(phone, 0.5, MovieUtil.PNT3_ONE, MovieUtil.PNT3_NEARZERO), Wait(0.24), Func(receiver.wrtReparentTo, suit.getRightHand()), LerpPosHprInterval(receiver, 0.0001, Point3(-0.45, 0.48, -0.62), VBase3(-87.47, -18.21, 7.82)), Wait(2.14), Func(receiver.wrtReparentTo, phone), Wait(0.62), LerpScaleInterval(phone, 0.5, MovieUtil.PNT3_NEARZERO), Func(MovieUtil.removeProps, [receiver, phone]))
    toonTracks = getToonTracks(attack, 2.8, ['slip-forward'], 2.29, ['jump'])
    hitAtleastOneToon = False
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = True
    if hitAtleastOneToon > 0:
        soundTrack = Parallel(getSoundTrack('ttr_s_ene_bat_closeTheLoop.ogg', delay=0, node=suit))
    else:
        soundTrack = Parallel(getSoundTrack('ttr_s_ene_bat_closeTheLoopMiss.ogg', delay=0, node=suit))
    return Parallel(suitTrack, toonTracks, propTrack, partTrack1, partTrack2, soundTrack)

def doMoneyTalks(attack):
    suit = attack['suit']
    battle = attack['battle']
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect('moneyTalksRight')
    particleEffect2 = BattleParticles.createParticleEffect('moneyTalksLeft')
    BattleParticles.setEffectTexture(particleEffect, 'doubletalk-double', color=Vec4(0, 1.0, 0.0, 1))
    BattleParticles.setEffectTexture(particleEffect2, 'doubletalk-good', color=Vec4(0, 1.0, 0.0, 1))
    suitType = getSuitBodyType(attack['suitName'])
    partDelay = 2.25
    damageDelay = 2.0
    dodgeDelay = 2.25
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    partTrack = getPartTrack(particleEffect, partDelay, 2.5, [particleEffect, suit, 0], softStop=-1)
    partTrack2 = getPartTrack(particleEffect2, partDelay, 2.5, [particleEffect2, suit, 0], softStop=-1)
    damageAnims = [['duck',
      0.01,
      0.4,
      1.05], ['cringe', 1e-06, 0.8]]
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, splicedDodgeAnims=[['duck', 0.01, 1.4]], showMissedExtraTime=0.9, showDamageExtraTime=0.8)
    soundTrack = getSoundTrack('SA_doubletalk.ogg', delay=2, node=suit)
    return Parallel(suitTrack, toonTrack, partTrack, partTrack2, soundTrack)


def doDoubleTalk(attack):
    suit = attack['suit']
    battle = attack['battle']
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect('DoubleTalkLeft')
    particleEffect2 = BattleParticles.createParticleEffect('DoubleTalkRight')
    BattleParticles.setEffectTexture(particleEffect, 'doubletalk-double', color=Vec4(0, 1.0, 0.0, 1))
    BattleParticles.setEffectTexture(particleEffect2, 'doubletalk-good', color=Vec4(0, 1.0, 0.0, 1))
    suitType = getSuitBodyType(attack['suitName'])
    partDelay = 2.25
    damageDelay = 2.0
    dodgeDelay = 2.25
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    partTrack = getPartTrack(particleEffect, partDelay, 2.5, [particleEffect, suit, 0], softStop=-.5)
    partTrack2 = getPartTrack(particleEffect2, partDelay, 2.5, [particleEffect2, suit, 0], softStop=-.5)
    damageAnims = [['duck',
      0.01,
      0.4,
      1.05], ['cringe', 1e-06, 0.8]]
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, splicedDodgeAnims=[['duck', 0.01, 1.4]], showMissedExtraTime=0.9, showDamageExtraTime=0.8)
    soundTrack = getSoundTrack('SA_doubletalk.ogg', delay=2, node=suit)
    return Parallel(suitTrack, toonTrack, partTrack, partTrack2, soundTrack)


def doFreezeAssets(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    BattleParticles.loadParticles()
    suitType = getSuitBodyType(attack['suitName'])
    partDelay = 0.2
    damageDelay = 2
    dodgeDelay = 1.3
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    initialCloudHeight = suit.height + 3
    cloudPosPoints = [Point3(0, 3, initialCloudHeight), MovieUtil.PNT3_ZERO]
    cloudPropTracks = Parallel()
    for t in targets:
        toon = t['toon']
        snowEffect = BattleParticles.createParticleEffect('FreezeAssets')
        BattleParticles.setEffectTexture(snowEffect, 'snow-particle')
        cloud = globalPropPool.getProp('stormcloud')
        cloudPropTrack = Sequence()
        cloudPropTrack.append(Func(cloud.pose, 'stormcloud', 0))
        cloudPropTrack.append(getPropAppearTrack(cloud, suit, cloudPosPoints, 1e-06, Point3(3, 3, 3), scaleUpTime=0.25))
        cloudPropTrack.append(Func(battle.movie.needRestoreRenderProp, cloud))
        cloudPropTrack.append(Func(cloud.wrtReparentTo, render))
        targetPoint = __toonFacePoint(toon)
        targetPoint.setZ(targetPoint[2] + 3)
        cloudPropTrack.append(Wait(0.6))
        cloudPropTrack.append(LerpPosInterval(cloud, .5, pos=targetPoint))
        cloudPropTrack.append(ParticleInterval(snowEffect, cloud, worldRelative=0, duration=3.1, cleanup=True, softStopT=-1))
        cloudPropTrack.append(Wait(0.4))
        cloudPropTrack.append(LerpScaleInterval(cloud, 0.25, MovieUtil.PNT3_NEARZERO))
        cloudPropTrack.append(Func(MovieUtil.removeProp, cloud))
        cloudPropTrack.append(Func(battle.movie.clearRenderProp, cloud))
        cloudPropTracks.append(cloudPropTrack)

    damageAnims = [['cringe',
      0.01,
      0.4,
      0.8], ['duck', 0.01, 1.6]]
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'], showMissedExtraTime=1.2)
    soundTrack = getSoundTrack('SA_brainstorm.ogg', delay=2.3, node=suit)
    return Parallel(suitTrack, toonTracks, cloudPropTracks, soundTrack)


def doHotAir(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    BattleParticles.loadParticles()
    sprayEffects = []
    for t in targets:
        sprayEffect = BattleParticles.createParticleEffect('HotAir')
        #BattleParticles.setEffectTexture(sprayEffect, 'fire')
        sprayEffects.append(sprayEffect)

    sprayDelay = 0.25
    flameDelay = 2.0
    flameDuration = 3.5
    flecksDelay = flameDelay + 0.8
    flecksDuration = flameDuration - 0.8
    damageDelay = 2.0
    dodgeDelay = 1.0
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    sprayTracks = getPartTracks(attack, sprayEffects, sprayDelay, 3.5, 0, softStop=-2)
    baseFlameTracks = Parallel()
    flameTracks = Parallel()
    flecksTracks = Parallel()
    colorTracks = Parallel()
    damageAnims = []
    damageAnims.append(['cringe',
                        0.01,
                        0.7,
                        0.62])
    damageAnims.append(['slip-forward',
                        0.01,
                        0.4,
                        1.2])
    damageAnims.append(['slip-forward', 0.01, 1.0])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=1.0, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_hot_air.ogg', delay=0.5, node=suit)
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        baseFlameEffect = BattleParticles.createParticleEffect(file='firedBaseFlame')
        flameEffect = BattleParticles.createParticleEffect('FiredFlame')
        flecksEffect = BattleParticles.createParticleEffect('SpriteFiredFlecks')
        BattleParticles.setEffectTexture(baseFlameEffect, 'fire')
        BattleParticles.setEffectTexture(flameEffect, 'fire')
        BattleParticles.setEffectTexture(flecksEffect, 'roll-o-dex', color=Vec4(0.95, 0.95, 0.0, 1))
        baseFlameTrack = getPartTrack(baseFlameEffect, flameDelay, flameDuration, [baseFlameEffect, toon, 0], softStop=-1)
        flameTrack = getPartTrack(flameEffect, flameDelay, flameDuration, [flameEffect, toon, 0], softStop=-1)
        flecksTrack = getPartTrack(flecksEffect, flecksDelay, flecksDuration, [flecksEffect, toon, 0], softStop=-1)

        def changeColor(parts):
            track = Parallel()
            for partNum in xrange(0, parts.getNumPaths()):
                nextPart = parts.getPath(partNum)
                track.append(Func(nextPart.setColorScale, Vec4(0, 0, 0, 1)))

            return track

        def resetColor(parts):
            track = Parallel()
            for partNum in xrange(0, parts.getNumPaths()):
                nextPart = parts.getPath(partNum)
                track.append(Func(nextPart.clearColorScale))

            return track

        if dmg > 0:
            headParts = toon.getHeadParts()
            torsoParts = toon.getTorsoParts()
            legsParts = toon.getLegsParts()
            colorTrack = Sequence()
            colorTrack.append(Wait(2.0))
            colorTrack.append(Func(battle.movie.needRestoreColor))
            colorTrack.append(changeColor(headParts))
            colorTrack.append(changeColor(torsoParts))
            colorTrack.append(changeColor(legsParts))
            colorTrack.append(Wait(2.5))
            colorTrack.append(resetColor(headParts))
            colorTrack.append(resetColor(torsoParts))
            colorTrack.append(resetColor(legsParts))
            colorTrack.append(Func(battle.movie.clearRestoreColor))
            baseFlameTracks.append(baseFlameTrack)
            flameTracks.append(flameTrack)
            flecksTracks.append(flecksTrack)
            colorTracks.append(colorTrack)

    return Parallel(suitTrack, toonTracks, sprayTracks, soundTrack, baseFlameTracks, flameTracks, flecksTracks, colorTracks)

def doStolenScene(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    bill = loader.loadModel('props/general/models/cc_m_gen_prp_vinyl_disk')
    suitTrack = getSuitTrack(attack)
    suitTrack.append(Wait(1.0))
    billPosPoints = [Point3(-0.564399421128801, 0, -0.6512301013024597), VBase3(90, 45, 0)]
    billPropTrack = getPropTrack(bill, suit.getRightHand(), billPosPoints, 0.25, 1.0, scaleUpPoint=Point3(.5, .5, .5))
    toonTrack = getToonTrack(attack, 0.25, ['cringe'], 0.01, ['sidestep'])
    multiTrackList = Parallel(suitTrack, toonTrack)
    if dmg > 0:
        soundTrack = getSoundTrack('SA_pick_pocket.ogg', delay=0.2, node=suit)
        multiTrackList.append(billPropTrack)
        multiTrackList.append(soundTrack)
    return multiTrackList


def doPickPocket(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    bill = globalPropPool.getProp('1dollar')
    suitTrack = getSuitTrack(attack)
    suitTrack.append(Wait(1.0))
    billPosPoints = [Point3(-0.13024602026049337, 0.45, -0.25), VBase3(136.424, -46.434, -129.712)]
    billPropTrack = getPropTrack(bill, suit.getRightHand(), billPosPoints, 0.25, 1.0, scaleUpPoint=Point3(1.41, 1.41, 1.41))
    toonTrack = getToonTrack(attack, 0.25, ['cringe'], 0.01, ['sidestep'])
    multiTrackList = Parallel(suitTrack, toonTrack)
    if dmg > 0:
        soundTrack = getSoundTrack('SA_pick_pocket.ogg', delay=0.2, node=suit)
        multiTrackList.append(billPropTrack)
        multiTrackList.append(soundTrack)
    return multiTrackList

def doPennyPinch(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    coinTypes = ['bronze', 'silver', 'gold']
    bill = loader.loadModel('phase_3.5/models/props/cc_m_prp_gen_coin_' + random.choice(coinTypes) + '.bam')
    suitTrack = getSuitTrack(attack)
    billPosPoints = [Point3(-0.3039073806078143, 0.30390738060781786, -0.390738060781473), VBase3(-91.17221418234442, -50.79594790159189, 0)]
    billPropTrack = getPropTrack(bill, suit.getRightHand(), billPosPoints, 0.25, 1.0, scaleUpPoint=Point3(1.25, 1.25, 1.25))
    billPropTrack.append(Func(bill.removeNode))
    toonTrack = getToonTrack(attack, 0.25, ['cringe'], 0.01, ['sidestep'])
    multiTrackList = Parallel(suitTrack, toonTrack)
    if dmg > 0:
        soundTrack = getSoundTrack('SA_pick_pocket.ogg', delay=0.2, node=suit)
        multiTrackList.append(billPropTrack)
        multiTrackList.append(soundTrack)
    return multiTrackList

def doVoodooMagic(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    target = attack['target']
    toon = target[0]['toon']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    battle = attack['battle']
    sinkPos = suit.getPos(battle)
    dropPos = suit.getPos(battle)
    sinkPos2 = suit.getPos(battle)
    dropPos2 = suit.getPos(battle)
    sinkPos.setY(sinkPos.getY() + 12.5)
    sinkPos.setZ(sinkPos.getZ() - 4.5)
    sinkPos2.setY(sinkPos.getY() - 32)
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    targetPos2 = toon.getPos(battle)
    headsUp2 = Func(suit.setHpr, battle, origHpr)
    moveTrack = Sequence(LerpPosInterval(suit, 0, sinkPos2, other=battle), headsUp, Wait(3.0), suitReset, Func(suit.setPos, battle, dropPos))
    suitTrack = Sequence(getSuitTrack(attack))
    suitTrack.append(Wait(1.0))
    dmg = target[0]['hp']
    bill = globalPropPool.getProp('1dollar')
    billPosPoints = [Point3(-0.01, 0.45, -0.25), VBase3(136.424, -46.434, -129.712)]
    billPropTrack = getPropTrack(bill, suit.getRightHand(), billPosPoints, 0.6, 0.55,
                                 scaleUpPoint=Point3(1.41, 1.41, 1.41))
    toonTrack = getToonTrack(attack, 0.6, ['cringe'], 0.01, ['sidestep'])
    multiTrackList = Parallel(suitTrack, toonTrack)
    if dmg > 0:
        soundTrack = getSoundTrack('SA_pick_pocket.ogg', delay=0.2, node=suit)
        multiTrackList.append(billPropTrack)
        multiTrackList.append(soundTrack)
    return Parallel(suitTrack, moveTrack, multiTrackList, toonTrack)

def doCigarSmoke(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    if suit.dna.name in ['cinema', 'choreo', 'fmaker', 'director'] and not suit.isSkeleton:
        return doSmokeAndMirrors(attack)
    elif suit.dna.name == 'hho' and not suit.isSkeleton:
        return doHeadHonchoCigarSmoke(attack)
    elif suit.dna.name == 'payman' and not suit.isSkeleton:
        return doHeadHonchoCigarSmoke(attack)
    elif suit.dna.name == 'fires' and not suit.isSkeleton:
        return doFirestarterCigarSmoke(attack)
    elif suit.dna.name == 'safesupervis' and not suit.isSkeleton:
        return doFirestarterCigarSmoke(attack)
    else:
        pass
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
        cigarPosPoints = [Point3(-0.05, -0.2, -0.25), VBase3(180.0, 0.0, 0.0)]
        cigarScale = Point3(7.0, 7.0, 7.0)
    elif suitType == 'c':
        suitTrack = Sequence(getSuitTrack(attack))
        cigarPosPoints = [Point3(0.13024602026048981, -0.26011560693641655, -0.21707670043415206), VBase3(180.0, 0.0, 0.0)]
        cigarScale = Point3(5.0, 5.0, 5.0)
    BattleParticles.loadParticles()
    baseFlameSmall = BattleParticles.createParticleEffect(file='cigarSmokeAtk')
    baseFlameEffect = BattleParticles.createParticleEffect(file='cigarSmokeAtk')
    cigarSmoke = BattleParticles.createParticleEffect(file='smoke')
    baseFlameSmall.setScale(0.7)
    cigar = globalPropPool.getProp('cigar')
    propTrack = getPropTrack(cigar, suit.getRightHand(), cigarPosPoints, 0.5, 3.5, scaleUpPoint=cigarScale)
    baseFlameTrack = getPartTrack(baseFlameEffect, 2.25, 3.25, [baseFlameEffect, suit, 0], softStop=-2)
    baseFlameSmallTrack = getPartTrack(baseFlameSmall, 2.25, 3.25, [baseFlameSmall, suit, 0], softStop=-2)
    partTrack = getPartTrack(cigarSmoke, 1, 4.0, [cigarSmoke, suit, 0], softStop=-2)

    def changeColor(parts):
        track = Parallel()
        for partNum in range(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(nextPart.colorScaleInterval(0.1, Vec4(0.5, 0.5, 0.5, 1)))

        return track

    def resetColor(parts):
        track = Parallel()
        for partNum in range(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.clearColorScale))

        return track

    if dmg > 0:
        headParts = toon.getHeadParts()
        torsoParts = toon.getTorsoParts()
        legsParts = toon.getLegsParts()
        colorTrack = Sequence()
        colorTrack.append(Wait(2.55))
        colorTrack.append(Func(battle.movie.needRestoreColor))
        colorTrack.append(changeColor(headParts))
        colorTrack.append(changeColor(torsoParts))
        colorTrack.append(changeColor(legsParts))
        colorTrack.append(Wait(3.5))
        colorTrack.append(resetColor(headParts))
        colorTrack.append(resetColor(torsoParts))
        colorTrack.append(resetColor(legsParts))
        colorTrack.append(Func(battle.movie.clearRestoreColor))
    damageAnims = []
    damageAnims.append(['cringe',
     0.01,
     0.7,
     0.62])
    damageAnims.append(['slip-forward',
     1e-05,
     0.4,
     1.2])
    damageAnims.extend(getSplicedLerpAnims('slip-forward', 0.31, 0.8, startTime=4.2))
    toonTrack = getToonTrack(attack, 2.8, ['cringe'], 2.0, ['sidestep'])
    soundTrack = getSoundTrack('SA_filibuster.ogg', delay=2.25, node=suit)
    if dmg > 0:
        return Parallel(suitTrack, propTrack, baseFlameTrack, toonTrack, partTrack, colorTrack, soundTrack)
    else:
        return Parallel(suitTrack, propTrack, baseFlameSmallTrack, partTrack, toonTrack, soundTrack)
	
def doCigarSmokeOLD(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    if suit.dna.name == 'hho' and not suit.isSkeleton:
        return doHeadHonchoCigarSmoke(attack)
    elif suit.dna.name == 'payman' and not suit.isSkeleton:
        return doHeadHonchoCigarSmoke(attack)
    elif suit.dna.name == 'fires' and not suit.isSkeleton:
        return doFirestarterCigarSmoke(attack)
    elif suit.dna.name == 'safesupervis' and not suit.isSkeleton:
        return doFirestarterCigarSmoke(attack)
    else:
        pass
    BattleParticles.loadParticles()
    smoke = BattleParticles.createParticleEffect('Smoke')
    #BattleParticles.setEffectTexture(smoke, 'snow-particle')
    cigar = globalPropPool.getProp('cigar')
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
        cigarPosPoints = [Point3(-0.05, -0.2, -0.25), VBase3(180.0, 0.0, 0.0)]
    elif suitType == 'c':
        suitTrack = Sequence(getSuitTrack(attack))
        cigarPosPoints = [Point3(0.13024602026048981, -0.390738060781473, -0.21707670043415206), VBase3(180.0, 0.0, 0.0)]
    cigarPropTrack = getPropTrack(cigar, suit.getRightHand(), cigarPosPoints, 0, 4.0, scaleUpPoint=Point3(7.0, 7.0, 7.0))
    toonTrack = getToonTrack(attack, 2.8, ['cringe'], 2.0, ['sidestep'])
    multiTrackList = Parallel(suitTrack, toonTrack)
    smokeTrack = getPartTrack(smoke, 2.75, 2.75, [smoke, suit, 0], softStop=-2)
    multiTrackList.append(cigarPropTrack)
    multiTrackList.append(smokeTrack)
    baseFlameEffect = BattleParticles.createParticleEffect(file='cigarSmokeAtk')
    baseFlameSmall = BattleParticles.createParticleEffect(file='cigarSmokeAtk')
    baseFlameSmall.setScale(0.7)

    def changeColor(parts):
        track = Parallel()
        for partNum in xrange(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.setColorScale, Vec4(0, 0, 0, 1)))

        return track

    def resetColor(parts):
        track = Parallel()
        for partNum in xrange(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.clearColorScale))

        return track

    if dmg > 0:
        headParts = toon.getHeadParts()
        torsoParts = toon.getTorsoParts()
        legsParts = toon.getLegsParts()
        colorTrack = Sequence()
        colorTrack.append(Wait(2.6))
        colorTrack.append(Func(battle.movie.needRestoreColor))
        colorTrack.append(changeColor(headParts))
        colorTrack.append(changeColor(torsoParts))
        colorTrack.append(changeColor(legsParts))
        colorTrack.append(Wait(2.2))
        colorTrack.append(resetColor(headParts))
        colorTrack.append(resetColor(torsoParts))
        colorTrack.append(resetColor(legsParts))
        colorTrack.append(Func(battle.movie.clearRestoreColor))
        multiTrackList.append(colorTrack)
    return multiTrackList

def doFilibuster(attack):
    suit = attack['suit']
    targets = attack['target']
    dmg = targets[0]['hp']
    battle = attack['battle']
    BattleParticles.loadParticles()
    sprayEffects = []
    sprayEffects2 = []
    sprayEffects3 = []
    sprayEffects4 = []
    for t in targets:
        sprayEffect = BattleParticles.createParticleEffect(file='filibusterSpray')
        sprayEffect2 = BattleParticles.createParticleEffect(file='filibusterSpray')
        sprayEffect3 = BattleParticles.createParticleEffect(file='filibusterSpray')
        sprayEffect4 = BattleParticles.createParticleEffect(file='filibusterSpray')
        color = Vec4(0.4, 0, 0, 1)
        BattleParticles.setEffectTexture(sprayEffect, 'filibuster-cut', color=color)
        BattleParticles.setEffectTexture(sprayEffect2, 'filibuster-fiscal', color=color)
        BattleParticles.setEffectTexture(sprayEffect3, 'filibuster-impeach', color=color)
        BattleParticles.setEffectTexture(sprayEffect4, 'filibuster-inc', color=color)
        sprayEffects.append(sprayEffect)
        sprayEffects2.append(sprayEffect2)
        sprayEffects3.append(sprayEffect3)
        sprayEffects4.append(sprayEffect4)

    partDelay = 0.5
    partDuration = 2.15
    damageDelay = 1.25
    dodgeDelay = 0.7
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    sprayTracks = getPartTracks(attack, sprayEffects, partDelay, partDuration, 0, softStop=-1)
    sprayTracks2 = getPartTracks(attack, sprayEffects2, partDelay + 0.5, partDuration, 0, softStop=-1)
    sprayTracks3 = getPartTracks(attack, sprayEffects3, partDelay + 1.0, partDuration, 0, softStop=-1)
    # How many of the fourth Filibuster word we need will depend on the Toons that get hit.  Therefore, we will have to manually recreate this rather than use the method.
    sprayTracks4 = Parallel()
    origHpr = battle.getActorPosHpr(suit)[1]
    for i in xrange(len(targets)):
        tgt = targets[i]
        toon = tgt['toon']
        if tgt['hp'] > 0:
            sprayEffects4[i].reparentTo(suit)
            suit.headsUp(battle, toon.getPos(battle))
            sprayEffects4[i].wrtReparentTo(battle)
            sprayTracks.append(getPartTrack(sprayEffects4[i], partDelay + 1.5, partDuration, [sprayEffects4[i], battle, 0]))

    suit.setHpr(battle, origHpr)
    damageAnims = []
    for i in xrange(0, 3):
        damageAnims.append(['cringe',
         1e-05,
         0.3,
         0.5])

    damageAnims.append(['cringe', 1e-05, 0.5])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_filibuster.ogg', delay=0.1, node=suit)
    return Parallel(suitTrack, toonTracks, soundTrack, sprayTracks, sprayTracks2, sprayTracks3, sprayTracks4)


def doSchmooze(attack):
    suit = attack['suit']
    battle = attack['battle']
    BattleParticles.loadParticles()
    upperEffects = []
    lowerEffects = []
    textureNames = ['schmooze-genius',
                    'schmooze-viz',
     'schmooze-instant',
     'schmooze-master',
                    'schmooze-genius',
     'schmooze-viz']
    for i in xrange(0, 6):
        upperEffect = BattleParticles.createParticleEffect(file='schmoozeUpperSpray')
        lowerEffect = BattleParticles.createParticleEffect(file='schmoozeLowerSpray')
        BattleParticles.setEffectTexture(upperEffect, textureNames[i], color=Vec4(0, 0, 1, 1))
        BattleParticles.setEffectTexture(lowerEffect, textureNames[i], color=Vec4(0, 0, 1, 1))
        upperEffects.append(upperEffect)
        lowerEffects.append(lowerEffect)

    suitType = getSuitBodyType(attack['suitName'])
    partDelay = 0.3
    damageDelay = partDelay + 0.4
    dodgeDelay = 0.4
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    upperPartTracks = Parallel()
    lowerPartTracks = Parallel()
    for i in xrange(0, 6):
        upperPartTracks.append(getPartTrack(upperEffects[i], partDelay + i * 0.35, 1.25, [upperEffects[i], suit, 0]))
        lowerPartTracks.append(getPartTrack(lowerEffects[i], partDelay + i * 0.35 + 0.7, 1.25, [lowerEffects[i], suit, 0]))

    damageAnims = []
    for i in xrange(0, 3):
        damageAnims.append(['conked',
         0.01,
         0.3,
         0.51])

    damageAnims.append(['conked', 0.01, 0.3])
    dodgeAnims = []
    dodgeAnims.append(['duck',
     0.01,
     0.2,
     2.7])
    dodgeAnims.append(['duck',
     0.01,
     1.22,
     1.28])
    dodgeAnims.append(['duck', 0.01, 3.16])
    soundTrack = getSoundTrack('SA_schmooze.ogg', delay=damageDelay, node=suit)
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.9, showDamageExtraTime=1.1)
    return Parallel(suitTrack, toonTrack, upperPartTracks, lowerPartTracks, soundTrack)


def doQuake(attack):
    suit = attack['suit']
    suitTrack = getSuitAnimTrack(attack)
    damageAnims = [['slip-forward'], ['slip-forward', 0.01]]
    dodgeAnims = [['jump'], ['jump', 0.01], ['jump', 0.01]]
    soundTrack = getSoundTrack('SA_quake.ogg', node=suit)
    toonTracks = getToonTracks(attack, damageDelay=1.8, splicedDamageAnims=damageAnims, dodgeDelay=1.1, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=2.8, showDamageExtraTime=1.1)
    return Parallel(suitTrack, toonTracks, soundTrack)

def doTremor(attack):
    suit = attack['suit']
    suitTrack = getSuitAnimTrack(attack)
    damageAnims = [['slip-forward'], ['slip-forward', 0.01]]
    dodgeAnims = [['jump'], ['jump', 0.01]]
    toonTracks = getToonTracks(attack, damageDelay=1.1, splicedDamageAnims=damageAnims, dodgeDelay=0.7, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=2.8, showDamageExtraTime=1.1)
    soundTrack = getSoundTrack('SA_tremor.ogg', delay=0.9, node=suit)
    return Parallel(suitTrack, soundTrack, toonTracks)


def doShake(attack):
    suit = attack['suit']
    suitTrack = getSuitAnimTrack(attack)
    damageAnims = [['slip-forward'], ['slip-forward', 0.01]]
    dodgeAnims = [['jump'], ['jump', 0.01]]
    soundTrack = getSoundTrack('SA_shake.ogg', delay=0, node=suit)
    toonTracks = getToonTracks(attack, damageDelay=1.1, splicedDamageAnims=damageAnims, dodgeDelay=0.7, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=2.8, showDamageExtraTime=1.1)
    return Parallel(suitTrack, toonTracks, soundTrack)

def doBash(attack):
    suit = attack['suit']
    battle = attack['battle']

    suitTrack = Sequence(Wait(1.0), getSuitAnimTrack(attack))

    desk = loader.loadModel('phase_3.5/models/modules/desk_only')
    desk.reparentTo(battle)
    desk.setPos(suit, 2.5, 3.5, 1.0)
    desk.setHpr(suit, 0, 0, 0)
    desk.setScale(0.01)
    desk.setTransparency(1)
    desk.setAlphaScale(1)

    laptop = globalPropPool.getProp('ttht_m_ene_techbotLaptop')
    laptop.reparentTo(desk)
    laptop.setPos(-2.0, 1.5, 2.5)
    laptop.setHpr(0, 0, 0)
    laptop.setScale(1.75)

    deskTrack = Sequence(
        LerpScaleInterval(
            desk,
            1.0,
            Point3(1.5, 1.5, 1.5),
            startScale=Point3(0.01, 0.01, 0.01)
        ),

        SoundInterval(
            base.loader.loadSfx('phase_5/audio/sfx/asfhdfha.ogg'),
            duration=0.75,
            node=desk
        ),

        Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/asfhafhsdh.ogg'), node=desk),

        Wait(1.0),

        LerpFunctionInterval(desk.setAlphaScale, fromData=1, toData=0, duration=1.0),

        Func(cleanupBashDesk, desk, laptop)
    )

    laptopTrack = Sequence(
        Wait(0.2),
        ActorInterval(laptop, 'ttht_m_ene_techbotLaptop', playRate=1.5)
    )

    toonTracks = getToonTracks(
        attack,
        damageDelay=1.5,
        splicedDamageAnims=[['slip-backward']],
        dodgeDelay=1.0,
        splicedDodgeAnims=[['jump']]
    )

    soundTrack = getSoundTrack('tt_s_ara_cmg_itemHitsFloor.ogg', delay=1.5, node=suit)

    return Parallel(suitTrack, deskTrack, laptopTrack, toonTracks, soundTrack)


def cleanupBashDesk(desk, laptop=None):
    if laptop:
        try:
            MovieUtil.removeProp(laptop)
        except:
            try:
                laptop.removeNode()
            except:
                pass

    if desk:
        try:
            desk.removeNode()
        except:
            pass


def doDataCorruption(attack):
    suit = attack['suit']
    battle = attack['battle']

    suitTrack = Sequence(Wait(1.0), getSuitAnimTrack(attack))

    desk = loader.loadModel('phase_3.5/models/modules/desk_only')
    desk.reparentTo(battle)
    desk.setPos(suit, 2.5, 3.5, 1.0)
    desk.setHpr(suit, 0, 0, 0)
    desk.setScale(0.01)
    desk.setTransparency(1)
    desk.setAlphaScale(1)

    laptop = globalPropPool.getProp('ttht_m_ene_techbotLaptop')
    laptop.reparentTo(desk)
    laptop.setPos(-2.0, 1.5, 2.5)
    laptop.setHpr(0, 0, 0)
    laptop.setScale(1.75)

    deskTrack = Sequence(
        LerpScaleInterval(
            desk,
            1.0,
            Point3(1.5, 1.5, 1.5),
            startScale=Point3(0.01, 0.01, 0.01)
        ),

        SoundInterval(
            base.loader.loadSfx('phase_5/audio/sfx/asfhdfha.ogg'),
            duration=0.75,
            node=desk
        ),

        Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/asfhafhsdh.ogg'), node=desk),

        Wait(1.0),

        LerpFunctionInterval(desk.setAlphaScale, fromData=1, toData=0, duration=1.0),

        Func(cleanupBashDesk, desk, laptop)
    )

    laptopTrack = Sequence(
        Wait(0.2),
        ActorInterval(laptop, 'ttht_m_ene_techbotLaptop', playRate=1.5)
    )

    toonTracks = getToonTracks(
        attack,
        damageDelay=1.5,
        splicedDamageAnims=[['slip-backward']],
        dodgeDelay=1.0,
        splicedDodgeAnims=[['jump']]
    )

    damageAnims = [['cringe']]
    dodgeAnims = [['jump']]
    toonTracks = getToonTracks(attack, damageDelay=1.5, splicedDamageAnims=damageAnims, dodgeDelay=1.0,
                               splicedDodgeAnims=dodgeAnims)
    oldcolor = render.getColorScale()
    lightingTrack = Sequence(Wait(1), LerpColorScaleInterval(render, 0.5, (0, 0.992, 1, 1)),
                             LerpColorScaleInterval(render, 1.5, (0, 0.992, 1, 1)),
                             LerpColorScaleInterval(render, 1, (oldcolor)))
    return Parallel(lightingTrack, suitTrack, deskTrack, laptopTrack, toonTracks)


def doHangUp(attack):
    suit = attack['suit']
    battle = attack['battle']
    phone = globalPropPool.getProp('phone')
    receiver = globalPropPool.getProp('receiver')
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    suitName = suit.getStyleName()
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        phonePosPoints = [Point3(-0.26011560693641655, 0.26011560693641655, -0.1), VBase3(180, 180, 0)]
        receiverPosPoints = [Point3(0, -0.43352601156069426, -0.8670520231213885), VBase3(90, 0, 0)]
    if suitType == 'b':
        phonePosPoints = [Point3(0.5202312138728296, 0.26011560693641655, 0), VBase3(180, 180, 0)]
        receiverPosPoints = [Point3(-0.23, 0, -0.11), VBase3(5.939, 2.763, -177.591)]
    if suitType == 'c':
        phonePosPoints = [Point3(0.5202312138728296, 0.26011560693641655, 0), VBase3(180, 180, 0)]
        receiverPosPoints = [Point3(-0.23, 0, -0.11), VBase3(5.939, 2.763, -177.591)]
    propTrack = Sequence(Func(__showProp, phone, suit.getLeftHand(), *phonePosPoints), Func(__showProp, receiver, suit.getLeftHand(), *receiverPosPoints), LerpScaleInterval(phone, 0.5, MovieUtil.PNT3_ONE, MovieUtil.PNT3_NEARZERO), Wait(0.24), Func(receiver.wrtReparentTo, suit.getRightHand()), LerpPosHprInterval(receiver, 0.0001, Point3(-0.45, 0.48, -0.62), VBase3(-87.47, -18.21, 7.82)), Wait(2.14), Func(receiver.wrtReparentTo, phone), Wait(0.62), LerpScaleInterval(phone, 0.5, MovieUtil.PNT3_NEARZERO), Func(MovieUtil.removeProps, [receiver, phone]))
    toonTracks = getToonTracks(attack, 3, ['slip-backward'], 2.5, ['jump'])
    soundTrack = getSoundTrack('SA_hangup.ogg', delay=0.5, node=suit)
    return Parallel(suitTrack, toonTracks, propTrack, soundTrack)


def doRedTape(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    suitName = suit.getStyleName()
    tapePosPoints = [Point3(-0.25, 0, -0.25), VBase3(0, 0, 0)]
    tapeScaleUpPoint = Point3(1, 1, 0.74)
    propTracks = Parallel()
    allTubeTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        tape = globalPropPool.getProp('redtape')
        tubes = []
        for i in xrange(0, 3):
            tubes.append(globalPropPool.getProp('redtape-tube'))

        propTrack = Sequence(getPropAppearTrack(tape, suit.getRightHand(), tapePosPoints, 0.25, tapeScaleUpPoint, scaleUpTime=0.25))
        propTrack.append(Wait(1.55))
        hitPoint = lambda toon = toon: __toonTorsoPoint(toon)
        propTrack.append(getPropThrowTrack(attack, tape, [hitPoint], [__toonGroundPoint(attack, toon, 0)], .25, target=t))
        propTracks.append(propTrack)
        hips = toon.getHipsParts()
        animal = toon.style.getAnimal()
        scale = ToontownGlobals.toonBodyScales[animal]
        legs = toon.style.legs
        torso = toon.style.torso
        torso = torso[0]
        animal = animal[0]
        tubeHeight = -0.8
        if torso == 's':
            scaleUpPoint = Point3(scale * 2.03, scale * 2.03, scale * 0.7975)
        elif torso == 'm':
            scaleUpPoint = Point3(scale * 2.03, scale * 2.03, scale * 0.7975)
        elif torso == 'l':
            scaleUpPoint = Point3(scale * 2.03, scale * 2.03, scale * 1.11)
        if animal == 'h' or animal == 'd':
            tubeHeight = -0.87
            scaleUpPoint = Point3(scale * 1.69, scale * 1.69, scale * 0.67)
        tubePosPoints = [Point3(0, 0, tubeHeight), MovieUtil.PNT3_ZERO]
        tubeTracks = Parallel()
        tubeTracks.append(Func(battle.movie.needRestoreHips))
        for partNum in xrange(0, hips.getNumPaths()):
            nextPart = hips.getPath(partNum)
            tubeTracks.append(getPropTrack(tubes[partNum], nextPart, tubePosPoints, 2.2, 3.17, scaleUpPoint=scaleUpPoint))
        tubeTracks.append(Func(battle.movie.clearRestoreHips))
        if dmg > 0:
            allTubeTracks.append(tubeTracks)

    toonTracks = getToonTracks(attack, 2.2, ['struggle'], 1.7, ['jump'])
    soundTrack = getSoundTrack('SA_red_tape.ogg', delay=1.7, node=suit)
    return Parallel(suitTrack, toonTracks, propTracks, soundTrack, allTubeTracks)


def doParadigmShift(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    hitAtleastOneToon = False
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = True

    damageDelay = 1.35
    dodgeDelay = 0.95
    sprayEffect = BattleParticles.createParticleEffect('ShiftSpray')
    suitName = suit.getStyleName()
    sprayEffect.setPos(Point3(-5.2, 4.6, 2.7))
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    sprayTrack = getPartTrack(sprayEffect, 1.0, 2.9, [sprayEffect, suit, 0], softStop=-1)
    liftTracks = Parallel()
    toonRiseTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        if dmg > 0:
            liftEffect = BattleParticles.createParticleEffect('ShiftLift')
            liftEffect.setPos(toon.getPos(battle))
            liftEffect.setZ(liftEffect.getZ() - 1.3)
            liftTracks.append(getPartTrack(liftEffect, 1.1, 5.1, [liftEffect, battle, 0], softStop=-1))
            shadow = toon.dropShadow
            fakeShadow = MovieUtil.copyProp(shadow)
            x = toon.getX()
            y = toon.getY()
            z = toon.getZ()
            height = 3
            groundPoint = Point3(x, y, z)
            risePoint = Point3(x, y, z + height)
            shakeRight = Point3(x, y + 0.7, z + height)
            shakeLeft = Point3(x, y - 0.7, z + height)
            shakeTrack = Sequence()
            shakeTrack.append(Wait(damageDelay + 0.25))
            shakeTrack.append(Func(shadow.hide))
            shakeTrack.append(LerpPosInterval(toon, 1.1, risePoint))
            for i in xrange(0, 17):
                shakeTrack.append(LerpPosInterval(toon, 0.03, shakeLeft))
                shakeTrack.append(LerpPosInterval(toon, 0.03, shakeRight))

            shakeTrack.append(LerpPosInterval(toon, 0.1, risePoint))
            shakeTrack.append(LerpPosInterval(toon, 0.1, groundPoint))
            shakeTrack.append(Func(shadow.show))
            shadowTrack = Sequence()
            shadowTrack.append(Func(battle.movie.needRestoreRenderProp, fakeShadow))
            shadowTrack.append(Wait(damageDelay + 0.25))
            shadowTrack.append(Func(fakeShadow.hide))
            shadowTrack.append(Func(fakeShadow.setScale, 0.27))
            shadowTrack.append(Func(fakeShadow.reparentTo, toon))
            shadowTrack.append(Func(fakeShadow.setPos, MovieUtil.PNT3_ZERO))
            shadowTrack.append(Func(fakeShadow.wrtReparentTo, battle))
            shadowTrack.append(Func(fakeShadow.show))
            shadowTrack.append(LerpScaleInterval(fakeShadow, 0.4, Point3(0.17, 0.17, 0.17)))
            shadowTrack.append(Wait(1.81))
            shadowTrack.append(LerpScaleInterval(fakeShadow, 0.1, Point3(0.27, 0.27, 0.27)))
            shadowTrack.append(Func(MovieUtil.removeProp, fakeShadow))
            shadowTrack.append(Func(battle.movie.clearRenderProp, fakeShadow))
            toonRiseTracks.append(Parallel(shakeTrack, shadowTrack))

    damageAnims = []
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.9, startTime=2.06))
    damageAnims.append(['slip-backward', 0.01, 0.5])
    dodgeAnims = []
    dodgeAnims.append(['jump',
     0.01,
     0,
     0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.0, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, splicedDodgeAnims=dodgeAnims, showDamageExtraTime=2.7)
    if hitAtleastOneToon:
        soundTrack = getSoundTrack('SA_paradigm_shift.ogg', delay=1.5, node=suit)
        return Parallel(suitTrack, sprayTrack, soundTrack, liftTracks, toonTracks, toonRiseTracks)
    else:
        return Parallel(suitTrack, sprayTrack, liftTracks, toonTracks, toonRiseTracks)


def doPowerTrip(attack):
    suit = attack['suit']
    battle = attack['battle']
    centerColor = Vec4(0.1, 0.1, 0.1, 0.4)
    edgeColor = Vec4(0.4, 0.1, 0.9, 0.7)
    powerBar1 = BattleParticles.createParticleEffect(file='powertrip')
    powerBar2 = BattleParticles.createParticleEffect(file='powertrip2')
    powerBar1.setPos(0, 6.1, 0.4)
    powerBar1.setHpr(-60, 0, 0)
    powerBar2.setPos(0, 6.1, 0.4)
    powerBar2.setHpr(60, 0, 0)
    powerBar1Particles = powerBar1.getParticlesNamed('particles-1')
    powerBar2Particles = powerBar2.getParticlesNamed('particles-1')
    powerBar1Particles.renderer.setCenterColor(centerColor)
    powerBar1Particles.renderer.setEdgeColor(edgeColor)
    powerBar2Particles.renderer.setCenterColor(centerColor)
    powerBar2Particles.renderer.setEdgeColor(edgeColor)
    waterfallEffect = BattleParticles.createParticleEffect('Waterfall')
    waterfallEffect.setScale(11)
    waterfallParticles = waterfallEffect.getParticlesNamed('particles-1')
    waterfallParticles.renderer.setCenterColor(centerColor)
    waterfallParticles.renderer.setEdgeColor(edgeColor)
    suitName = suit.getStyleName()
    if suitName == 'mh':
        waterfallEffect.setPos(0, 4, 3.6)
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))

    def getPowerTrack(effect, suit = suit, battle = battle):
        partTrack = Sequence(Wait(1.0), Func(battle.movie.needRestoreParticleEffect, effect), Func(effect.start, suit), Wait(0.4), LerpPosInterval(effect, 1.0, Point3(0, 25, 0.4)), LerpFunctionInterval(effect.setAlphaScale, fromData=1, toData=0, duration=0.4), Func(effect.cleanup), Func(battle.movie.clearRestoreParticleEffect, effect))
        return partTrack

    partTrack1 = getPowerTrack(powerBar1)
    partTrack2 = getPowerTrack(powerBar2)
    waterfallTrack = getPartTrack(waterfallEffect, 0.6, 2.3, [waterfallEffect, suit, 0], softStop=-1)
    toonTracks = getToonTracks(attack, 1.8, ['slip-forward'], 1.29, ['jump'])
    soundTrack = getSoundTrack('SA_powertrip.ogg', delay=1.8, node=suit)
    return Parallel(suitTrack, partTrack1, partTrack2, waterfallTrack, soundTrack, toonTracks)


def getThrowEndPointOLD(suit, toon, battle, whichBounce):
    pnt = toon.getPos(toon)
    if whichBounce == 'one':
        pnt.setY(pnt[1] + 10)
    elif whichBounce == 'two':
        pnt.setY(pnt[1] + 6.5)
    elif whichBounce == 'three':
        pnt.setY(pnt[1] + 3)
    elif whichBounce == 'threeHit':
        pass
    elif whichBounce == 'threeMiss':
        pnt.setY(pnt[1] - 5)
    elif whichBounce == 'four':
        pnt.setY(pnt[1] - 5)
    return Point3(pnt)

def doBounceCheck(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    battle = attack['battle']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    hitSuit = dmg > 0
    check = globalPropPool.getProp("bounced-check")
    checkPosPoints = [MovieUtil.PNT3_ZERO, VBase3(90, 90, 180)]
    bounce1Point = lambda: getThrowEndPoint(toon, "one", battle)
    bounce2Point = lambda: getThrowEndPoint(toon, "two", battle)
    hitPoint = lambda: getThrowEndPoint(toon, "hit", battle)
    missPoint = lambda: getThrowEndPoint(toon, "miss", battle)
    throwDelay = 48/24 / 2
    dodgeDelay = 1.7 + throwDelay
    damageDelay = 2.0 + throwDelay
    suitTrack = getSuitTrack(attack, playRate=2)
    checkPropTrack = Sequence(
        getPropAppearTrack(
            check,
            suit.getRightHand(),
            checkPosPoints,
            1e-05,
            Point3(8.5, 8.5, 8.5),
            startScale=MovieUtil.PNT3_ONE,
        )
    )
    checkPropTrack.append(Wait(throwDelay))
    checkPropTrack.append(Func(check.wrtReparentTo, battle))
    releaseDur = checkPropTrack.getDuration()
    grav = -130
    checkPropTrack.append(
        getThrowTrack(check, bounce1Point, duration=0.5, parent=battle, gravity=grav)
    )
    checkPropTrack.append(
        getThrowTrack(check, bounce2Point, duration=0.6, parent=battle, gravity=grav)
    )
    if hitSuit:
        checkPropTrack.append(
            getThrowTrack(check, hitPoint, duration=0.5, parent=battle, gravity=grav)
        )
    else:
        checkPropTrack.append(
            getThrowTrack(check, missPoint, duration=0.5, parent=battle, gravity=grav)
        )
        checkPropTrack.append(
            LerpScaleInterval(check, 0.1, MovieUtil.PNT3_NEARZERO, blendType='easeIn')
        )
    endDur = checkPropTrack.getDuration() - releaseDur - 0.01
    checkPropTrack.append(Sequence(
        Func(check.setScale, MovieUtil.PNT3_NEARZERO),
        Wait(1.0),
        Func(MovieUtil.removeProp, check)
    ))
    spinCheckTrack = Sequence(
        Wait(releaseDur),
        LerpHprInterval(check, endDur, startHpr=(0, 90, 0), hpr=(1200, 90, 0)),
    )
    toonTrack = Parallel(
        getToonTrack(attack, damageDelay, ['nothing'], dodgeDelay, ['nothing']),
        Sequence(
            Wait(damageDelay),
            ActorInterval(toon, 'slip-backward', playRate=1.3),
            Func(toon.loop, 'neutral'),
        ) if hitSuit else Sequence(Wait(dodgeDelay), Func(toon.doEmote, 24), Wait(1.5), Func(toon.loop, 'neutral')),
    )

    soundName = "SA_pink_slip.ogg"  # "AA_drop_anvil_miss.ogg"  # "SA_pink_slip.ogg"
    soundTracks = Parallel(
        getSoundTrack(soundName, delay=throwDelay + 0.2, duration=0.7,
                            node=suit),
        getSoundTrack(soundName, delay=throwDelay+0.8, duration=0.7, node=suit),
        getSoundTrack(soundName, delay=throwDelay+1.4, duration=0.7, node=suit),
    )
    hitSeq = Sequence()
    if hitSuit:
        hitSeq = getSoundTrack("Toon_bodyfall_synergy.ogg", delay=throwDelay + 1.9,
                                    duration=0.6, node=suit)

    BattleParticles.loadParticles()
    trailEffect = BattleParticles.createParticleEffect(file='bouncecheck')
    partTrack = getPartTrack(trailEffect, releaseDur, endDur+1.0, [trailEffect, check, 1], softStop=-1.0)

    return Parallel(suitTrack, checkPropTrack, toonTrack, soundTracks, spinCheckTrack, partTrack, hitSeq)

def getThrowEndPoint(toon, whichBounce, battle):
    pnt = toon.getPos(battle)
    if whichBounce == "one":
        pnt = Vec3(-5.0, 0.0, 0.8)
    elif whichBounce == "two":
        pnt = Vec3(2.75, -2.0, 0.8)
    elif whichBounce == "hit":
        pnt.setZ(pnt[2] + toon.shoulderHeight + 0.3)
    elif whichBounce == "miss":
        pnt = Vec3(0, -8, 13)
    return Point3(pnt)


def doBounceCheckOLD(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    battle = attack['battle']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    hitSuit = dmg > 0
    check = globalPropPool.getProp('bounced-check')
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'c':
        checkPosPoints = [Point3(-.1, -0.390738060781473, 0.02), VBase3(-4.688856729377676, 176.3531114327062, 176.61360347322716)]
    elif suitType == 'b':
        checkPosPoints = [Point3(-0.13024602026049337, -0.390738060781473, -0.08670520231213885), VBase3(-5.73082489146168, -174.27745664739885, 173.48769898697537)]
    else:
        checkPosPoints = [Point3(-0.3468208092485554, -0.5202312138728331, -0.08670520231213885), VBase3(-7.814761215629517, -177.91907514450867, -188.3236994219653)]
    bounce1Point = lambda suit = suit, toon = toon, battle = battle: getThrowEndPoint(suit, toon, battle, 'one')
    bounce2Point = lambda suit = suit, toon = toon, battle = battle: getThrowEndPoint(suit, toon, battle, 'two')
    bounce3Point = lambda suit=suit, toon=toon, battle=battle: getThrowEndPoint(suit, toon, battle, 'three')
    hit3Point = lambda suit = suit, toon = toon, battle = battle: getThrowEndPoint(suit, toon, battle, 'threeHit')
    miss3Point = lambda suit = suit, toon = toon, battle = battle: getThrowEndPoint(suit, toon, battle, 'threeMiss')
    bounce4Point = lambda suit = suit, toon = toon, battle = battle: getThrowEndPoint(suit, toon, battle, 'four')
    suitType = getSuitBodyType(attack['suitName'])
    throwDelay = 1
    dodgeDelay = 1.0
    damageDelay = 4.0
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    checkPropTrack = Sequence(getPropAppearTrack(check, suit.getRightHand(), checkPosPoints, .5, Point3(8.5, 8.5, 8.5), startScale=MovieUtil.PNT3_ONE))
    checkPropTrack.append(Wait(throwDelay))
    checkPropTrack.append(Func(check.wrtReparentTo, toon))
    checkPropTrack.append(Func(check.setHpr, Point3(0, -90, 0)))
    if hitSuit:
        checkPropTrack.append(getThrowTrack(check, bounce1Point, duration=0.5, parent=toon, gravity=-200))
        checkPropTrack.append(getThrowTrack(check, bounce2Point, duration=0.5, parent=toon, gravity=-200))
        checkPropTrack.append(getThrowTrack(check, bounce3Point, duration=0.5, parent=toon, gravity=-200))
        checkPropTrack.append(getThrowTrack(check, hit3Point, duration=0.5, parent=toon, gravity=-200))
        checkPropTrack.append(Func(MovieUtil.removeProp, check))
        explodePosPoints = [Point3(0, 0, 0), MovieUtil.PNT3_ZERO]
        splatName = 'dust'
        splat = globalPropPool.getProp('dust')
        explode = globalPropPool.getProp('dust')
        explode.setTwoSided(True)
        explode.setBillboardPointWorld(2)
        explodeTrack = Sequence()
        explodeTrack.append(
        getPropAppearTrack(explode, toon, explodePosPoints, 0, Point3(2, 2, 2), scaleUpTime=0))
        explodeTrack.append(Sequence(ActorInterval(explode, splatName), Func(explode.detachNode)))
        soundTrack = getSoundTrack('LB_evidence_miss.ogg', node=suit)
        checkPropTrack.append(Parallel(explodeTrack, soundTrack))
    else:
        checkPropTrack.append(Func(check.setHpr, Point3(0, 0, 0)))
        checkPropTrack.append(getThrowTrack(check, miss3Point, duration=0.5, parent=toon, gravity=-300))
        checkPropTrack.append(LerpScaleInterval(check, 0.3, MovieUtil.PNT3_NEARZERO))
        checkPropTrack.append(Func(MovieUtil.removeProp, check))
        explodePosPoints = [Point3(0, -5, 0), MovieUtil.PNT3_ZERO]
        splatName = 'dust'
        splat = globalPropPool.getProp('dust')
        explode = globalPropPool.getProp('dust')
        explode.setTwoSided(True)
        explode.setBillboardPointWorld(2)
        explodeTrack = Sequence()
        explodeTrack.append(
            getPropAppearTrack(explode, toon, explodePosPoints, 0, Point3(2, 2, 2), scaleUpTime=0))
        explodeTrack.append(Sequence(ActorInterval(explode, splatName), Func(explode.detachNode)))
        soundTrack = getSoundTrack('LB_evidence_miss.ogg', node=suit)
        checkPropTrack.append(Parallel(explodeTrack, soundTrack))
    toonTrack = getToonTrack(attack, damageDelay, ['conked'], dodgeDelay, ['duck'])
    if hitSuit:
        soundTracks = Sequence(getSoundTrack('SA_pink_slip.ogg', delay=throwDelay + 1, duration=0.5, node=suit), getSoundTrack('SA_pink_slip.ogg', duration=0.5, node=suit), getSoundTrack('SA_pink_slip.ogg', duration=0.6, node=suit))
    else:
        soundTracks = Sequence(getSoundTrack('SA_pink_slip.ogg', delay=throwDelay + 1, duration=0.5, node=suit))

    return Parallel(suitTrack, checkPropTrack, toonTrack, soundTracks)

def doBounceRate(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    battle = attack['battle']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    hitSuit = dmg > 0
    check = globalPropPool.getProp('ttrpg_m_ene_prp_bouncedRate')
    check.setTwoSided(True)
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'c':
        checkPosPoints = [Point3(0.04341534008683112, -0.390738060781473, 0.02), VBase3(177.65557163531116, 180.0, 190.1591895803184)]
    elif suitType == 'b':
        checkPosPoints = [Point3(-0.13024602026049337, -0.390738060781473, -0.08670520231213885), VBase3(-5.73082489146168, -174.27745664739885, 173.48769898697537)]
    else:
        checkPosPoints = [Point3(1.6063675832127373, 0.30390738060781786, -0.13024602026049337), VBase3(-7.814761215629517, 180.0, 180)]
    bounce1Point = lambda suit=suit, toon=toon, battle=battle: getThrowEndPoint(suit, toon, battle, 'one')
    bounce2Point = lambda suit=suit, toon=toon, battle=battle: getThrowEndPoint(suit, toon, battle, 'two')
    bounce3Point = lambda suit=suit, toon=toon, battle=battle: getThrowEndPoint(suit, toon, battle, 'three')
    hit3Point = lambda suit=suit, toon=toon, battle=battle: getThrowEndPoint(suit, toon, battle, 'threeHit')
    miss3Point = lambda suit=suit, toon=toon, battle=battle: getThrowEndPoint(suit, toon, battle, 'threeMiss')
    bounce4Point = lambda suit=suit, toon=toon, battle=battle: getThrowEndPoint(suit, toon, battle, 'four')
    suitType = getSuitBodyType(attack['suitName'])
    throwDelay = 1
    dodgeDelay = 1.0
    damageDelay = 4.0
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    checkPropTrack = Sequence(
        getPropAppearTrack(check, suit.getRightHand(), checkPosPoints, .5, Point3(2, 2, 2),
                           startScale=MovieUtil.PNT3_ONE))
    checkPropTrack.append(Wait(throwDelay))
    checkPropTrack.append(Func(check.wrtReparentTo, toon))
    checkPropTrack.append(Func(check.setHpr, Point3(0, -90, 0)))
    if hitSuit:
        checkPropTrack.append(getThrowTrack(check, bounce1Point, duration=0.5, parent=toon, gravity=-200))
        checkPropTrack.append(getThrowTrack(check, bounce2Point, duration=0.5, parent=toon, gravity=-200))
        checkPropTrack.append(getThrowTrack(check, bounce3Point, duration=0.5, parent=toon, gravity=-200))
        checkPropTrack.append(getThrowTrack(check, hit3Point, duration=0.5, parent=toon, gravity=-200))
        checkPropTrack.append(Func(MovieUtil.removeProp, check))
        explodePosPoints = [Point3(0, 0, 0), MovieUtil.PNT3_ZERO]
        splatName = 'dust'
        splat = globalPropPool.getProp('dust')
        explode = globalPropPool.getProp('dust')
        explode.setTwoSided(True)
        explode.setBillboardPointWorld(2)
        explodeTrack = Sequence()
        explodeTrack.append(
            getPropAppearTrack(explode, toon, explodePosPoints, 0, Point3(2, 2, 2), scaleUpTime=0))
        explodeTrack.append(Sequence(ActorInterval(explode, splatName), Func(explode.detachNode)))
        soundTrack = getSoundTrack('LB_evidence_miss.ogg', node=suit)
        checkPropTrack.append(Parallel(explodeTrack, soundTrack))
    else:
        checkPropTrack.append(Func(check.setHpr, Point3(0, 0, 0)))
        checkPropTrack.append(getThrowTrack(check, miss3Point, duration=0.5, parent=toon, gravity=-300))
        checkPropTrack.append(LerpScaleInterval(check, 0.3, MovieUtil.PNT3_NEARZERO))
        checkPropTrack.append(Func(MovieUtil.removeProp, check))
        explodePosPoints = [Point3(0, -5, 0), MovieUtil.PNT3_ZERO]
        splatName = 'dust'
        splat = globalPropPool.getProp('dust')
        explode = globalPropPool.getProp('dust')
        explode.setTwoSided(True)
        explode.setBillboardPointWorld(2)
        explodeTrack = Sequence()
        explodeTrack.append(
            getPropAppearTrack(explode, toon, explodePosPoints, 0, Point3(2, 2, 2), scaleUpTime=0))
        explodeTrack.append(Sequence(ActorInterval(explode, splatName), Func(explode.detachNode)))
        soundTrack = getSoundTrack('LB_evidence_miss.ogg', node=suit)
        checkPropTrack.append(Parallel(explodeTrack, soundTrack))
    toonTrack = getToonTrack(attack, damageDelay, ['conked'], dodgeDelay, ['duck'])
    if hitSuit:
        soundTracks = Sequence(getSoundTrack('SA_pink_slip.ogg', delay=throwDelay + 1, duration=0.5, node=suit),
                               getSoundTrack('SA_pink_slip.ogg', duration=0.5, node=suit),
                               getSoundTrack('SA_pink_slip.ogg', duration=0.6, node=suit))
    else:
        soundTracks = Sequence(getSoundTrack('SA_pink_slip.ogg', delay=throwDelay + 1, duration=0.5, node=suit))
    return Parallel(suitTrack, checkPropTrack, toonTrack, soundTracks)


def doWatercooler(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    watercooler = globalPropPool.getProp('cc_a_prp_bat_watercooler')

    def getCoolerSpout(watercooler = watercooler):
        spout = watercooler.find('**/Dispenser') # Unlike the previous model, it appears that the spout's node is Dispenser.
        return spout.getPos(render)

    suitTrack = getSuitAnimTrack(attack) # I'm not going to have the Cog turn since it appears that, ever since Clash v1.7, Cogs no longer turn to face the Toon when performing the Watercooler attack.
    posPoints = [Point3(0.5, 0.2, 0), VBase3(90, 0, 180)]
    # Not a huge fan of how getPropTrack() is handling the watercooler prop.  I'll create my own version, then.
    propTrack = Sequence(
        Func(__showProp, watercooler, suit.getLeftHand(), *posPoints),
        ActorInterval(watercooler, 'cc_a_prp_bat_watercooler'),
        Func(MovieUtil.removeProp, watercooler)
    )
    sprayTracks = Parallel()
    splashTracks = Parallel()

    def prepSplash(splash, targetPoint):
        splash.reparentTo(render)
        splash.setPos(targetPoint)
        scale = splash.getScale()
        splash.setBillboardPointWorld()
        splash.setScale(scale)

    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        hitPoint = lambda toon = toon: __toonFacePoint(toon)
        missPoint = lambda prop = watercooler, toon = toon: __toonMissPoint(prop, toon, 0, parent=render)
        sprayTrack = Sequence()
        sprayTrack.append(Wait(3.11))
        sprayTrack.append(MovieUtil.getSprayTrack(battle, Point4(0.75, 0.75, 1.0, 0.8), getCoolerSpout, hitPoint if dmg > 0 else missPoint, 0.2, 0.2, 0.2, horizScale=0.3, vertScale=0.3))
        sprayTracks.append(sprayTrack)
        if dmg > 0:
            splash = globalPropPool.getProp('splash-from-splat')
            splash.setColor(0.75, 0.75, 1, 0.8)
            splash.setScale(0.3)
            splashTracks.append(Sequence(Func(battle.movie.needRestoreRenderProp, splash), Wait(3.2), Func(prepSplash, splash, __toonFacePoint(toon)), ActorInterval(splash, 'splash-from-splat'), Func(MovieUtil.removeProp, splash), Func(battle.movie.clearRenderProp, splash)))

    dodgeAnims = []
    dodgeAnims.append(['jump',
     0.01,
     0,
     0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.0, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    toonTracks = getToonTracks(attack, damageDelay=suitTrack.getDuration() - 2.25, damageAnimNames=['cringe'], dodgeDelay=2.25, splicedDodgeAnims=dodgeAnims)
    soundTrack = Sequence(Wait(1.1), SoundInterval(globalBattleSoundCache.getSound('SA_watercooler_appear_only.ogg'), node=suit, duration=1.4722), Wait(0.4), SoundInterval(globalBattleSoundCache.getSound('SA_watercooler_spray_only.ogg'), node=suit, duration=2.313))
    return Parallel(suitTrack, toonTracks, propTrack, sprayTracks, soundTrack, splashTracks)


def doFired(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    BattleParticles.loadParticles()
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    baseFlameTracks = Parallel()
    flameTracks = Parallel()
    flecksTracks = Parallel()
    baseFlameSmallTracks = Parallel()
    flameSmallTracks = Parallel()
    flecksSmallTracks = Parallel()
    colorTracks = Parallel()
    damageAnims = []
    damageAnims.append(['cringe',
                        0.01,
                        0.7,
                        0.62])
    damageAnims.append(['slip-forward',
                        1e-05,
                        0.4,
                        1.2])
    damageAnims.extend(getSplicedLerpAnims('slip-forward', 0.31, 0.8, startTime=1.2))
    toonTracks = getToonTracks(attack, damageDelay=1.5, splicedDamageAnims=damageAnims, dodgeDelay=0.3, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_hot_air.ogg', delay=1.0, node=suit)
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        baseFlameEffect = BattleParticles.createParticleEffect(file='firedBaseFlame')
        flameEffect = BattleParticles.createParticleEffect('FiredFlame')
        flecksEffect = BattleParticles.createParticleEffect('SpriteFiredFlecks')
        BattleParticles.setEffectTexture(baseFlameEffect, 'fire')
        BattleParticles.setEffectTexture(flameEffect, 'fire')
        BattleParticles.setEffectTexture(flecksEffect, 'roll-o-dex', color=Vec4(0.8, 0.8, 0.8, 1))
        baseFlameSmall = BattleParticles.createParticleEffect(file='firedBaseFlame')
        flameSmall = BattleParticles.createParticleEffect('FiredFlame')
        flecksSmall = BattleParticles.createParticleEffect('SpriteFiredFlecks')
        BattleParticles.setEffectTexture(baseFlameSmall, 'fire')
        BattleParticles.setEffectTexture(flameSmall, 'fire')
        BattleParticles.setEffectTexture(flecksSmall, 'roll-o-dex', color=Vec4(0.8, 0.8, 0.8, 1))
        baseFlameSmall.setScale(0.7)
        flameSmall.setScale(0.7)
        flecksSmall.setScale(0.7)
        baseFlameTrack = getPartTrack(baseFlameEffect, 1.0, 3.9, [baseFlameEffect, toon, 0], softStop=-1)
        flameTrack = getPartTrack(flameEffect, 1.0, 3.9, [flameEffect, toon, 0], softStop=-1)
        flecksTrack = getPartTrack(flecksEffect, 1.8, 2.1, [flecksEffect, toon, 0], softStop=-1)
        baseFlameSmallTrack = getPartTrack(baseFlameSmall, 1.0, 2.9, [baseFlameSmall, toon, 0], softStop=-1)
        flameSmallTrack = getPartTrack(flameSmall, 1.0, 2.9, [flameSmall, toon, 0], softStop=-1)
        flecksSmallTrack = getPartTrack(flecksSmall, 1.8, 2.1, [flecksSmall, toon, 0], softStop=-1)

        def changeColor(parts):
            track = Parallel()
            for partNum in xrange(0, parts.getNumPaths()):
                nextPart = parts.getPath(partNum)
                track.append(Func(nextPart.setColorScale, Vec4(0, 0, 0, 1)))

            return track

        def resetColor(parts):
            track = Parallel()
            for partNum in xrange(0, parts.getNumPaths()):
                nextPart = parts.getPath(partNum)
                track.append(Func(nextPart.clearColorScale))

            return track

        if dmg > 0:
            headParts = toon.getHeadParts()
            torsoParts = toon.getTorsoParts()
            legsParts = toon.getLegsParts()
            colorTrack = Sequence()
            colorTrack.append(Wait(2.0))
            colorTrack.append(Func(battle.movie.needRestoreColor))
            colorTrack.append(changeColor(headParts))
            colorTrack.append(changeColor(torsoParts))
            colorTrack.append(changeColor(legsParts))
            colorTrack.append(Wait(2.5))
            colorTrack.append(resetColor(headParts))
            colorTrack.append(resetColor(torsoParts))
            colorTrack.append(resetColor(legsParts))
            colorTrack.append(Func(battle.movie.clearRestoreColor))
            baseFlameTracks.append(baseFlameTrack)
            flameTracks.append(flameTrack)
            flecksTracks.append(flecksTrack)
            colorTracks.append(colorTrack)
        else:
            baseFlameTracks.append(baseFlameSmallTrack)
            flameTracks.append(flameSmallTrack)
            flecksTracks.append(flecksSmallTrack)

    return Parallel(suitTrack, baseFlameTracks, flameTracks, flecksTracks, toonTracks, colorTracks, soundTrack)

def doFiredPressurizer(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    BattleParticles.loadParticles()
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    baseFlameTracks = Parallel()
    flameTracks = Parallel()
    flecksTracks = Parallel()
    baseFlameSmallTracks = Parallel()
    flameSmallTracks = Parallel()
    flecksSmallTracks = Parallel()
    colorTracks = Parallel()
    damageAnims = []
    damageAnims.append(['cringe',
                        0.01,
                        0.7,
                        0.62])
    damageAnims.append(['slip-forward',
                        1e-05,
                        0.4,
                        1.2])
    damageAnims.extend(getSplicedLerpAnims('slip-forward', 0.31, 0.8, startTime=1.2))
    toonTracks = getToonTracks(attack, damageDelay=1.5, splicedDamageAnims=damageAnims, dodgeDelay=0.3, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_hot_air.ogg', delay=1.0, node=suit)
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        baseFlameEffect = BattleParticles.createParticleEffect(file='firedBaseFlame2')
        flameEffect = BattleParticles.createParticleEffect('FiredFlame2')
        flecksEffect = BattleParticles.createParticleEffect('SpriteFiredFlecks')
        BattleParticles.setEffectTexture(flecksEffect, 'roll-o-dex', color=Vec4(0.8, 0.8, 0.8, 1))
        baseFlameSmall = BattleParticles.createParticleEffect(file='firedBaseFlame2')
        flameSmall = BattleParticles.createParticleEffect('FiredFlame2')
        flecksSmall = BattleParticles.createParticleEffect('SpriteFiredFlecks')
        BattleParticles.setEffectTexture(flecksSmall, 'roll-o-dex', color=Vec4(0.8, 0.8, 0.8, 1))
        baseFlameSmall.setScale(0.7)
        flameSmall.setScale(0.7)
        flecksSmall.setScale(0.7)
        baseFlameTrack = getPartTrack(baseFlameEffect, 1.0, 3.9, [baseFlameEffect, toon, 0], softStop=-1)
        flameTrack = getPartTrack(flameEffect, 1.0, 3.9, [flameEffect, toon, 0], softStop=-1)
        flecksTrack = getPartTrack(flecksEffect, 1.8, 2.1, [flecksEffect, toon, 0], softStop=-1)
        baseFlameSmallTrack = getPartTrack(baseFlameSmall, 1.0, 2.9, [baseFlameSmall, toon, 0], softStop=-1)
        flameSmallTrack = getPartTrack(flameSmall, 1.0, 2.9, [flameSmall, toon, 0], softStop=-1)
        flecksSmallTrack = getPartTrack(flecksSmall, 1.8, 2.1, [flecksSmall, toon, 0], softStop=-1)

        def changeColor(parts):
            track = Parallel()
            for partNum in xrange(0, parts.getNumPaths()):
                nextPart = parts.getPath(partNum)
                track.append(Func(nextPart.setColorScale, Vec4(0, 0, 0, 1)))

            return track

        def resetColor(parts):
            track = Parallel()
            for partNum in xrange(0, parts.getNumPaths()):
                nextPart = parts.getPath(partNum)
                track.append(Func(nextPart.clearColorScale))

            return track

        if dmg > 0:
            headParts = toon.getHeadParts()
            torsoParts = toon.getTorsoParts()
            legsParts = toon.getLegsParts()
            colorTrack = Sequence()
            colorTrack.append(Wait(2.0))
            colorTrack.append(Func(battle.movie.needRestoreColor))
            colorTrack.append(changeColor(headParts))
            colorTrack.append(changeColor(torsoParts))
            colorTrack.append(changeColor(legsParts))
            colorTrack.append(Wait(2.5))
            colorTrack.append(resetColor(headParts))
            colorTrack.append(resetColor(torsoParts))
            colorTrack.append(resetColor(legsParts))
            colorTrack.append(Func(battle.movie.clearRestoreColor))
            baseFlameTracks.append(baseFlameTrack)
            flameTracks.append(flameTrack)
            flecksTracks.append(flecksTrack)
            colorTracks.append(colorTrack)
        else:
            baseFlameTracks.append(baseFlameSmallTrack)
            flameTracks.append(flameSmallTrack)
            flecksTracks.append(flecksSmallTrack)

    return Parallel(suitTrack, baseFlameTracks, flameTracks, flecksTracks, toonTracks, colorTracks, soundTrack)

def doHotAirPressurizer(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    BattleParticles.loadParticles()
    sprayEffects = []
    for t in targets:
        sprayEffect = BattleParticles.createParticleEffect('HotAirPressurizer')
        #BattleParticles.setEffectTexture(sprayEffect, 'fire')
        sprayEffects.append(sprayEffect)

    sprayDelay = 0.25
    flameDelay = 2.0
    flameDuration = 3.5
    flecksDelay = flameDelay + 0.8
    flecksDuration = flameDuration - 0.8
    damageDelay = 2.0
    dodgeDelay = 1.0
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    sprayTracks = getPartTracks(attack, sprayEffects, sprayDelay, 3.5, 0, softStop=-2)
    baseFlameTracks = Parallel()
    flameTracks = Parallel()
    flecksTracks = Parallel()
    colorTracks = Parallel()
    damageAnims = []
    damageAnims.append(['cringe',
                        0.01,
                        0.7,
                        0.62])
    damageAnims.append(['slip-forward',
                        0.01,
                        0.4,
                        1.2])
    damageAnims.append(['slip-forward', 0.01, 1.0])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=1.0, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_hot_air.ogg', delay=0.5, node=suit)
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        baseFlameEffect = BattleParticles.createParticleEffect(file='firedBaseFlame2')
        flameEffect = BattleParticles.createParticleEffect('FiredFlame2')
        flecksEffect = BattleParticles.createParticleEffect('SpriteFiredFlecks')
        BattleParticles.setEffectTexture(flecksEffect, 'roll-o-dex', color=Vec4(0.95, 0.95, 0.0, 1))
        baseFlameTrack = getPartTrack(baseFlameEffect, flameDelay, flameDuration, [baseFlameEffect, toon, 0], softStop=-1)
        flameTrack = getPartTrack(flameEffect, flameDelay, flameDuration, [flameEffect, toon, 0], softStop=-1)
        flecksTrack = getPartTrack(flecksEffect, flecksDelay, flecksDuration, [flecksEffect, toon, 0], softStop=-1)

        def changeColor(parts):
            track = Parallel()
            for partNum in xrange(0, parts.getNumPaths()):
                nextPart = parts.getPath(partNum)
                track.append(Func(nextPart.setColorScale, Vec4(0, 0, 0, 1)))

            return track

        def resetColor(parts):
            track = Parallel()
            for partNum in xrange(0, parts.getNumPaths()):
                nextPart = parts.getPath(partNum)
                track.append(Func(nextPart.clearColorScale))

            return track

        if dmg > 0:
            headParts = toon.getHeadParts()
            torsoParts = toon.getTorsoParts()
            legsParts = toon.getLegsParts()
            colorTrack = Sequence()
            colorTrack.append(Wait(2.0))
            colorTrack.append(Func(battle.movie.needRestoreColor))
            colorTrack.append(changeColor(headParts))
            colorTrack.append(changeColor(torsoParts))
            colorTrack.append(changeColor(legsParts))
            colorTrack.append(Wait(2.5))
            colorTrack.append(resetColor(headParts))
            colorTrack.append(resetColor(torsoParts))
            colorTrack.append(resetColor(legsParts))
            colorTrack.append(Func(battle.movie.clearRestoreColor))
            baseFlameTracks.append(baseFlameTrack)
            flameTracks.append(flameTrack)
            flecksTracks.append(flecksTrack)
            colorTracks.append(colorTrack)

    return Parallel(suitTrack, toonTracks, sprayTracks, soundTrack, baseFlameTracks, flameTracks, flecksTracks, colorTracks)


def doAudit(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    calculator = globalPropPool.getProp('calculator')
    calculator.setTwoSided(True)
    BattleParticles.loadParticles()
    particleEffects = []
    particleEffects2 = []
    particleEffects3 = []
    particleEffects4 = []
    particleEffects5 = []
    for t in targets:
        particleEffect = BattleParticles.createParticleEffect('Calculate')
        BattleParticles.setEffectTexture(particleEffect, 'audit-one', color=Vec4(0, 0, 0, 1))
        particleEffect2 = BattleParticles.createParticleEffect('Calculate')
        BattleParticles.setEffectTexture(particleEffect2, 'audit-two', color=Vec4(0, 0, 0, 1))
        particleEffect3 = BattleParticles.createParticleEffect('Calculate')
        BattleParticles.setEffectTexture(particleEffect3, 'audit-three', color=Vec4(0, 0, 0, 1))
        particleEffect4 = BattleParticles.createParticleEffect('Calculate')
        BattleParticles.setEffectTexture(particleEffect4, 'audit-four', color=Vec4(0, 0, 0, 1))
        particleEffect5 = BattleParticles.createParticleEffect('Calculate')
        BattleParticles.setEffectTexture(particleEffect5, 'audit-mult', color=Vec4(0, 0, 0, 1))
        particleEffects.append(particleEffect)
        particleEffects2.append(particleEffect2)
        particleEffects3.append(particleEffect3)
        particleEffects4.append(particleEffect4)
        particleEffects5.append(particleEffect5)

    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    partTracks = getPartTracks(attack, particleEffects, 1.5, 2.5, 0, softStop=-1)
    partTracks2 = getPartTracks(attack, particleEffects2, 1.6, 2.5, 0, softStop=-1)
    partTracks3 = getPartTracks(attack, particleEffects3, 1.7, 2.6, 0, softStop=-1)
    partTracks4 = getPartTracks(attack, particleEffects4, 1.8, 2.7, 0, softStop=-1)
    partTracks5 = getPartTracks(attack, particleEffects5, 1.9, 2.8, 0, softStop=-1)
    suitName = attack['suitName']
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        calcPosPoints = [Point3(-0.7803468208092497, 0.26011560693641655, -0.1), VBase3(0, 0.0, 170.63583815028903)]
        calculator.setScale(1.25)
    if suitType == 'b':
        calcPosPoints = [Point3(0, 0.43352601156069426, 0), VBase3(0, 0.0, 180.0)]
        calculator.setScale(1)
    if suitType == 'c':
        calcPosPoints = [Point3(0, 0.34682080924855896, 0), VBase3(0, 0.0, 180.0)]
        calculator.setScale(1)
    calcPropTrack = Sequence(
        Func(__showProp, calculator, suit.getLeftHand(), *calcPosPoints),
        ActorInterval(calculator, 'calculator', playRate=1.25),
        Func(MovieUtil.removeProp, calculator)
    )
    toonTracks = getToonTracks(attack, 2.6, ['conked'], 0.9, ['duck'], showMissedExtraTime=2.2)
    soundTrack = getSoundTrack('SA_audit.ogg', delay=1.3, node=suit)
    return Parallel(suitTrack, toonTracks, calcPropTrack, soundTrack, partTracks, partTracks2, partTracks3, partTracks4, partTracks5)

def doCalculate(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    calculator = globalPropPool.getProp('calculator')
    calculator.setTwoSided(True)
    BattleParticles.loadParticles()
    particleEffects = []
    particleEffects2 = []
    particleEffects3 = []
    particleEffects4 = []
    particleEffects5 = []
    for t in targets:
        particleEffect = BattleParticles.createParticleEffect('Calculate')
        BattleParticles.setEffectTexture(particleEffect, 'audit-one', color=Vec4(0, 0, 0, 1))
        particleEffect2 = BattleParticles.createParticleEffect('Calculate')
        BattleParticles.setEffectTexture(particleEffect2, 'audit-plus', color=Vec4(0, 0, 0, 1))
        particleEffect3 = BattleParticles.createParticleEffect('Calculate')
        BattleParticles.setEffectTexture(particleEffect3, 'audit-mult', color=Vec4(0, 0, 0, 1))
        particleEffect4 = BattleParticles.createParticleEffect('Calculate')
        BattleParticles.setEffectTexture(particleEffect4, 'audit-three', color=Vec4(0, 0, 0, 1))
        particleEffect5 = BattleParticles.createParticleEffect('Calculate')
        BattleParticles.setEffectTexture(particleEffect5, 'audit-div', color=Vec4(0, 0, 0, 1))
        particleEffects.append(particleEffect)
        particleEffects2.append(particleEffect2)
        particleEffects3.append(particleEffect3)
        particleEffects4.append(particleEffect4)
        particleEffects5.append(particleEffect5)

    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    partTracks = getPartTracks(attack, particleEffects, 1.5, 2.5, 0, softStop=-1)
    partTracks2 = getPartTracks(attack, particleEffects2, 1.6, 2.5, 0, softStop=-1)
    partTracks3 = getPartTracks(attack, particleEffects3, 1.7, 2.6, 0, softStop=-1)
    partTracks4 = getPartTracks(attack, particleEffects4, 1.8, 2.7, 0, softStop=-1)
    partTracks5 = getPartTracks(attack, particleEffects5, 1.9, 2.8, 0, softStop=-1)
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        calcPosPoints = [Point3(-0.7803468208092497, 0.26011560693641655, -0.1), VBase3(0, 0.0, 170.63583815028903)]
        calculator.setScale(1.25)
    if suitType == 'b':
        calcPosPoints = [Point3(0, 0.43352601156069426, 0), VBase3(0, 0.0, 180.0)]
        calculator.setScale(1)
    if suitType == 'c':
        calcPosPoints = [Point3(0, 0.34682080924855896, 0), VBase3(0, 0.0, 180.0)]
        calculator.setScale(1)
    calcPropTrack = Sequence(
        Func(__showProp, calculator, suit.getLeftHand(), *calcPosPoints),
        ActorInterval(calculator, 'calculator', playRate=1.25),
        Func(MovieUtil.removeProp, calculator)
    )
    toonTracks = getToonTracks(attack, 2.6, ['conked'], 1.2, ['sidestep'])
    soundTrack = getSoundTrack('SA_calculate.ogg', delay=1.3, node=suit)
    return Parallel(suitTrack, toonTracks, calcPropTrack, soundTrack, partTracks, partTracks2, partTracks3, partTracks4, partTracks5)


def doTabulate(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    calculator = globalPropPool.getProp('calculator')
    calculator.setTwoSided(True)
    BattleParticles.loadParticles()
    particleEffects = []
    particleEffects2 = []
    particleEffects3 = []
    particleEffects4 = []
    particleEffects5 = []
    for t in targets:
        particleEffect = BattleParticles.createParticleEffect('Calculate')
        BattleParticles.setEffectTexture(particleEffect, 'audit-plus', color=Vec4(0, 0, 0, 1))
        particleEffect2 = BattleParticles.createParticleEffect('Calculate')
        BattleParticles.setEffectTexture(particleEffect2, 'audit-minus', color=Vec4(0, 0, 0, 1))
        particleEffect3 = BattleParticles.createParticleEffect('Calculate')
        BattleParticles.setEffectTexture(particleEffect3, 'audit-mult', color=Vec4(0, 0, 0, 1))
        particleEffect4 = BattleParticles.createParticleEffect('Calculate')
        BattleParticles.setEffectTexture(particleEffect4, 'audit-div', color=Vec4(0, 0, 0, 1))
        particleEffect5 = BattleParticles.createParticleEffect('Calculate')
        BattleParticles.setEffectTexture(particleEffect5, 'audit-one', color=Vec4(0, 0, 0, 1))
        particleEffects.append(particleEffect)
        particleEffects2.append(particleEffect2)
        particleEffects3.append(particleEffect3)
        particleEffects4.append(particleEffect4)
        particleEffects5.append(particleEffect5)

    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    partTrack = getPartTrack(particleEffect, 1.5, 2.5, [particleEffect, suit, 0], softStop=-1)
    partTrack2 = getPartTrack(particleEffect2, 1.6, 2.5, [particleEffect2, suit, 0], softStop=-1)
    partTrack3 = getPartTrack(particleEffect3, 1.7, 2.6, [particleEffect3, suit, 0], softStop=-1)
    partTrack4 = getPartTrack(particleEffect4, 1.8, 2.7, [particleEffect4, suit, 0], softStop=-1)
    partTrack5 = getPartTrack(particleEffect5, 1.9, 2.8, [particleEffect5, suit, 0], softStop=-1)
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        calcPosPoints = [Point3(-0.7803468208092497, 0.26011560693641655, -0.1), VBase3(0, 0.0, 170.63583815028903)]
        calculator.setScale(1.25)
    if suitType == 'b':
        calcPosPoints = [Point3(0, 0.43352601156069426, 0), VBase3(0, 0.0, 180.0)]
        calculator.setScale(1)
    if suitType == 'c':
        calcPosPoints = [Point3(0, 0.34682080924855896, 0), VBase3(0, 0.0, 180.0)]
        calculator.setScale(1)
    calcPropTrack = Sequence(
        Func(__showProp, calculator, suit.getLeftHand(), *calcPosPoints),
        ActorInterval(calculator, 'calculator', playRate=1.25),
        Func(MovieUtil.removeProp, calculator)
    )
    toonTracks = getToonTracks(attack, 2.6, ['conked'], 1.2, ['sidestep'])
    soundTrack = getSoundTrack('SA_calculate.ogg', delay=1.3, node=suit)
    return Parallel(suitTrack, toonTracks, soundTrack, calcPropTrack, partTrack, partTrack2, partTrack3, partTrack4, partTrack5)


def doCrunch(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    throwDuration = 1.75
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    numberNames = ['one',
     'two',
     'three',
     'four',
     'five',
     'six']
    BattleParticles.loadParticles()
    numberSpill1 = BattleParticles.createParticleEffect(file='numberSpill')
    numberSpill2 = BattleParticles.createParticleEffect(file='numberSpill')
    spillTexture1 = random.choice(numberNames)
    spillTexture2 = random.choice(numberNames)
    BattleParticles.setEffectTexture(numberSpill1, 'audit-' + spillTexture1)
    BattleParticles.setEffectTexture(numberSpill2, 'audit-' + spillTexture2)
    numberSpillTrack1 = getPartTrack(numberSpill1, .5, 3.1, [numberSpill1, suit, 0], softStop=-1)
    numberSpillTrack2 = getPartTrack(numberSpill2, .5, 3.1, [numberSpill2, suit, 0], softStop=-1)
    numberSprayTracks = Parallel()
    numOfNumbers = random.randint(10, 15)
    for i in xrange(0, numOfNumbers - 1):
        nextSpray = BattleParticles.createParticleEffect(file='numberSpray')
        nextTexture = random.choice(numberNames)
        BattleParticles.setEffectTexture(nextSpray, 'audit-' + nextTexture)
        nextStartTime = random.random() * 0.6 + throwDuration
        nextDuration = random.random() * 0.4 + 1.4
        nextSprayTrack = getPartTrack(nextSpray, nextStartTime, nextDuration + 1, [nextSpray, suit, 0], softStop=-1)
        numberSprayTracks.append(nextSprayTrack)

    numberTracks = Parallel()
    for i in xrange(0, numOfNumbers):
        texture = random.choice(numberNames)
        next = MovieUtil.copyProp(BattleParticles.getParticle('audit-' + texture))
        numberTrack = Sequence(Wait(0.5), Parallel(Func(next.reparentTo, suit.getRightHand()),
        Func(next.setScale, 0.01, 0.01, 0.01),
        Func(next.setColor, Vec4(0.0, 0.0, 0.0, 1.0)),
        Func(next.setPos, random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3),
        Func(next.setHpr, VBase3(-1.15, 86.58, -76.78)), ),
                               LerpScaleInterval(next, 0.25, MovieUtil.PNT3_ONE), Wait(1.1), Func(MovieUtil.removeProp, next))
        numberTracks.append(numberTrack)

    damageAnims = []
    damageAnims.append(['cringe',
     0.01,
     0.14,
     0.28])
    damageAnims.append(['cringe',
     0.01,
     0.16,
     0.3])
    damageAnims.append(['cringe',
     0.01,
     0.13,
     0.22])
    damageAnims.append(['slip-forward', 0.01, 0.6])
    toonTrack = getToonTrack(attack, damageDelay=3, splicedDamageAnims=damageAnims, dodgeDelay=2.6, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_crunch.ogg', delay=3, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, numberSpillTrack1, numberSpillTrack2, numberTracks, numberSprayTracks)

def doLiquidateGROUP(attack):
    suit = attack['suit']
    battle = attack['battle']
    BattleParticles.loadParticles()
    partDelay = 0
    damageDelay = 1.5
    dodgeDelay = 1

    suitTrack = Sequence(Wait(0.5), getSuitTrack(attack, playRate=1.25))
    initialCloudHeight = suit.height + 3
    cloudPosPoints = [Point3(0, 3, initialCloudHeight), VBase3(180, 0, 0)]
    cloudPropTracks = Parallel()
    puddleTracks = Parallel()
    damageAnims = [['melt'], ['jump', 1.5, 0.4]]
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    for t in attack['target']:
        toon = t['toon']
        rainEffect = BattleParticles.createParticleEffect(file='liquidate')
        rainEffect2 = BattleParticles.createParticleEffect(file='liquidate')
        rainEffect3 = BattleParticles.createParticleEffect(file='liquidate')
        effectColor = Vec4(0.00, 1.00, 1.00, 1.00) #if attack['id'] == ACID_RAIN else Vec4(0.00, 0.00, 0.00, 1.00)
        BattleParticles.setEffectTexture(rainEffect, 'raindrop', color=effectColor)
        BattleParticles.setEffectTexture(rainEffect2, 'raindrop', color=effectColor)
        BattleParticles.setEffectTexture(rainEffect3, 'raindrop', color=effectColor)
        cloud = globalPropPool.getProp('stormcloud')
        targetPoint = __toonFacePoint(toon)
        targetPoint.setZ(targetPoint[2] + 3)
        cloudPropTrack = Sequence(
            Func(cloud.pose, 'stormcloud', 0),
            getPropAppearTrack(cloud, suit, cloudPosPoints, 1e-06, Point3(3, 3, 3), scaleUpTime=0.7),
            Func(battle.movie.needRestoreRenderProp, cloud),
            Func(cloud.wrtReparentTo, render),
            Wait(0.5),
            LerpPosInterval(cloud, .5, pos=targetPoint),
            Wait(partDelay),
            Parallel(
                Sequence(
                    ParticleInterval(rainEffect, cloud, worldRelative=0, duration=4.1, cleanup=True)
                ),
                Sequence(
                    Wait(0.1),
                    ParticleInterval(rainEffect2, cloud, worldRelative=0, duration=4.0, cleanup=True)
                ),
                Sequence(
                    Wait(0.1),
                    ParticleInterval(rainEffect3, cloud, worldRelative=0, duration=4.0, cleanup=True)
                ),
                Sequence(
                    ActorInterval(cloud, 'stormcloud', startTime=3, duration=0.1),
                    ActorInterval(cloud, 'stormcloud', startTime=1, duration=4.3)
                )
            ),
            Wait(0.4),
            LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO),
            Func(MovieUtil.removeProp, cloud),
            Func(battle.movie.clearRenderProp, cloud)
        )
        cloudPropTracks.append(cloudPropTrack)
        if t['hp'] != 0:
            puddle = globalPropPool.getProp('quicksand')
            puddle.setColor(Vec4(0.00, 0.00, 0.00, 1.00)) #if attack['id'] == ACID_RAIN else Vec4(0.0, 0.0, 0.0, 1))
            puddle.setHpr(Point3(120, 0, 0))
            puddle.setScale(0.01)
            puddleTrack = Sequence(
                Func(battle.movie.needRestoreRenderProp, puddle),
                Wait(damageDelay - 0.7),
                Func(puddle.reparentTo, battle),
                Func(puddle.setPos, toon.getPos(battle)),
                LerpScaleInterval(puddle, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO),
                Wait(3.2),
                LerpFunctionInterval(puddle.setAlphaScale, fromData=1, toData=0, duration=0.8),
                Func(MovieUtil.removeProp, puddle),
                Func(battle.movie.clearRenderProp, puddle)
            )
            puddleTracks.append(puddleTrack)
    soundTrack1 = getSoundTrack('SA_liquidate.ogg', delay=2.0, node=suit)
    soundTrack = Parallel(soundTrack1)
    return Parallel(suitTrack, toonTracks, cloudPropTracks, soundTrack, puddleTracks)



def doLiquidate(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    partDelay = 0
    damageDelay = 1.5
    dodgeDelay = 1
    cloudPropTracks = Parallel()
    puddleTracks = Parallel()
    suitTrack = Sequence(Wait(0.5), getSuitTrack(attack, playRate=1.25))
    BattleParticles.loadParticles()
    damageAnims = [['melt'], ['jump', 1.5, 0.4]]
    for t in attack['target']:
        toon = t['toon']
        cloud = globalPropPool.getProp('stormcloud')
        rainEffect = BattleParticles.createParticleEffect(file='liquidate')
        rainEffect2 = BattleParticles.createParticleEffect(file='liquidate')
        rainEffect3 = BattleParticles.createParticleEffect(file='liquidate')
        initialCloudHeight = suit.height + 3
        cloudPosPoints = [Point3(0, 3, initialCloudHeight), VBase3(180, 0, 0)]
        cloudPropTrack = Sequence()
        cloudPropTrack.append(Func(cloud.pose, 'stormcloud', 0))
        cloudPropTrack.append(getPropAppearTrack(cloud, suit, cloudPosPoints, 1e-06, Point3(3, 3, 3), scaleUpTime=0.25))
        cloudPropTrack.append(Func(battle.movie.needRestoreRenderProp, cloud))
        cloudPropTrack.append(Func(cloud.wrtReparentTo, render))
        targetPoint = __toonFacePoint(toon)
        targetPoint.setZ(targetPoint[2] + 3)
        cloudPropTrack.append(Wait(0.6))
        cloudPropTrack.append(LerpPosInterval(cloud, .5, pos=targetPoint))
        cloudPropTrack.append(Parallel(
            Sequence(ParticleInterval(rainEffect, cloud, worldRelative=0, duration=3.1, cleanup=True, softStopT=-1)),
            Sequence(Wait(0.1), ParticleInterval(rainEffect2, cloud, worldRelative=0, duration=3.0, cleanup=True, softStopT=-1)),
            Sequence(Wait(0.1), ParticleInterval(rainEffect3, cloud, worldRelative=0, duration=3.0, cleanup=True, softStopT=-1)),
            Sequence(ActorInterval(cloud, 'stormcloud', startTime=3, duration=0.1), ActorInterval(cloud, 'stormcloud', startTime=1, duration=2.3))))
        cloudPropTrack.append(Wait(0.4))
        cloudPropTrack.append(LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO))
        cloudPropTrack.append(Func(MovieUtil.removeProp, cloud))
        cloudPropTrack.append(Func(battle.movie.clearRenderProp, cloud))
        cloudPropTracks.append(cloudPropTrack)
        if t['hp'] != 0:
            puddle = globalPropPool.getProp('quicksand')
            puddle.setColor(Vec4(0.0, 0.0, 1.0, 1))
            puddle.setHpr(Point3(120, 0, 0))
            puddle.setScale(0.01)
            puddleTrack = Sequence(Func(battle.movie.needRestoreRenderProp, puddle), Wait(damageDelay - 0.7), Func(puddle.reparentTo, battle), Func(puddle.setPos, toon.getPos(battle)), LerpScaleInterval(puddle, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO), Wait(3.2), LerpFunctionInterval(puddle.setAlphaScale, fromData=1, toData=0, duration=0.8), Func(MovieUtil.removeProp, puddle), Func(battle.movie.clearRenderProp, puddle))
            puddleTracks.append(puddleTrack)
    soundTrack1 = getSoundTrack('SA_liquidate.ogg', delay=1.0, node=suit)
    soundTrack = Parallel(soundTrack1)
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay,
                             dodgeAnimNames=['sidestep'])
    return Parallel(suitTrack, toonTracks, puddleTracks, cloudPropTracks, soundTrack)

		
def doAcidRain(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    BattleParticles.loadParticles()
    rainEffect = BattleParticles.createParticleEffect(file='acidrain')
    rainEffect2 = BattleParticles.createParticleEffect(file='acidrain')
    rainEffect3 = BattleParticles.createParticleEffect(file='acidrain')
    cloud = globalPropPool.getProp('stormcloud')
    suitType = getSuitBodyType(attack['suitName'])
    partDelay = 0
    damageDelay = 1.5
    dodgeDelay = 1
    suitTrack = Sequence(Wait(0.5), getSuitTrack(attack, playRate=1.25))
    initialCloudHeight = suit.height + 3
    cloudPosPoints = [Point3(0, 3, initialCloudHeight), VBase3(180, 0, 0)]
    cloudPropTrack = Sequence()
    cloudPropTrack.append(Func(cloud.pose, 'stormcloud', 0))
    cloudPropTrack.append(getPropAppearTrack(cloud, suit, cloudPosPoints, 1e-06, Point3(3, 3, 3), scaleUpTime=0.25))
    cloudPropTrack.append(Func(battle.movie.needRestoreRenderProp, cloud))
    cloudPropTrack.append(Func(cloud.wrtReparentTo, render))
    targetPoint = __toonFacePoint(toon)
    targetPoint.setZ(targetPoint[2] + 3)
    cloudPropTrack.append(Wait(0.6))
    cloudPropTrack.append(LerpPosInterval(cloud, .5, pos=targetPoint))
    cloudPropTrack.append(Parallel(Sequence(ParticleInterval(rainEffect, cloud, worldRelative=0, duration=3.1, cleanup=True, softStopT=-1)), Sequence(Wait(0.1), ParticleInterval(rainEffect2, cloud, worldRelative=0, duration=3.0, cleanup=True, softStopT=-1)), Sequence(Wait(0.1), ParticleInterval(rainEffect3, cloud, worldRelative=0, duration=3.0, cleanup=True, softStopT=-1)), Sequence(ActorInterval(cloud, 'stormcloud', startTime=3, duration=0.1), ActorInterval(cloud, 'stormcloud', startTime=1, duration=2.3))))
    cloudPropTrack.append(Wait(0.4))
    cloudPropTrack.append(LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO))
    cloudPropTrack.append(Func(MovieUtil.removeProp, cloud))
    cloudPropTrack.append(Func(battle.movie.clearRenderProp, cloud))
    damageAnims = [['melt'], ['jump', 1.5, 0.4]]
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_acid.ogg', delay=2.0, node=suit)
    if dmg > 0:
        puddle = globalPropPool.getProp('quicksand')
        puddle.setColor(Vec4(0.0, 1.0, 0.0, 1))
        puddle.setHpr(Point3(120, 0, 0))
        puddle.setScale(0.01)
        puddleTrack = Sequence(Func(battle.movie.needRestoreRenderProp, puddle), Wait(damageDelay - 0.7), Func(puddle.reparentTo, battle), Func(puddle.setPos, toon.getPos(battle)), LerpScaleInterval(puddle, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO), Wait(3.2), LerpFunctionInterval(puddle.setAlphaScale, fromData=1, toData=0, duration=0.8), Func(MovieUtil.removeProp, puddle), Func(battle.movie.clearRenderProp, puddle))
        return Parallel(suitTrack, toonTrack, cloudPropTrack, soundTrack, puddleTrack)
    else:
        return Parallel(suitTrack, toonTrack, cloudPropTrack, soundTrack)


def doMarketCrash(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitDelay = 1.5
    propDelay = .5
    throwDuration = 1.0
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    posPoints = [Point3(-0.25, 1, 0), VBase3(90, 90, 0)]
    propTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        paper = globalPropPool.getProp('newspaper')
        paperTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, propDelay, Point3(3.5, 3.5, 3.5), scaleUpTime=0))
        paperTrack.append(Wait(suitDelay))
        hitPoint = toon.getPos(battle)
        hitPoint.setX(hitPoint.getX() + 1.5)
        hitPoint.setY(hitPoint.getY() + 1.5)
        hitPoint.setZ(hitPoint.getZ() + .75)
        missPoint2 = toon.getPos(battle)
        missPoint2.setX(hitPoint.getX() + 1.5)
        missPoint2.setY(hitPoint.getY() - 7)
        movePoint = Point3(hitPoint.getX(), hitPoint.getY() - 1.8, hitPoint.getZ() + 0.2)
        missPoint = Point3(missPoint2.getX(), missPoint2.getY(), missPoint2.getZ())
        paperTrack.append(Func(battle.movie.needRestoreRenderProp, paper))
        paperTrack.append(Func(paper.wrtReparentTo, battle))
        if dmg > 0:
            paperTrack.append(getThrowTrack(paper, hitPoint, duration=throwDuration, parent=battle, gravity=-100))
            paperTrack.append(Wait(0.6))
            paperTrack.append(LerpPosInterval(paper, 0.4, movePoint))
        else:
            paperTrack.append(getThrowTrack(paper, missPoint2, duration=throwDuration, parent=battle, gravity=-100))
            paperTrack.append(Wait(0.6))
            paperTrack.append(LerpPosInterval(paper, 0.4, missPoint))
        spinTrack = Sequence(Wait(propDelay + suitDelay), LerpHprInterval(paper, throwDuration, Point3(0, 0, 0)))
        sizeTrack = Sequence(Wait(propDelay + suitDelay), LerpScaleInterval(paper, throwDuration, Point3(7, 7, 7)), Wait(0.95), LerpScaleInterval(paper, 0.4, MovieUtil.PNT3_NEARZERO))
        propTrack = Sequence(Parallel(paperTrack, spinTrack, sizeTrack), Func(MovieUtil.removeProp, paper), Func(battle.movie.clearRenderProp, paper))
        propTracks.append(propTrack)

    damageAnims = []
    damageAnims.append(['cringe',
     0.01,
     0.21,
     0.08])
    damageAnims.append(['slip-forward',
     0.01,
     0.6,
     0.85])
    damageAnims.extend(getSplicedLerpAnims('slip-forward', 0.31, 0.95, startTime=1.2))
    damageAnims.append(['slip-forward', 0.01, 1.51])
    toonTracks = getToonTracks(attack, damageDelay=3, splicedDamageAnims=damageAnims, dodgeDelay=1.5, dodgeAnimNames=['duck'])
    soundTrack = getSoundTrack('SA_market_crash.ogg', node=suit)
    return Parallel(suitTrack, toonTracks, soundTrack, propTrack)


def doBite(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1

    propDelay = 0.25
    propScaleUpTime = 0.25
    suitDelay = 1.45
    throwDelay = propDelay + propScaleUpTime + suitDelay
    throwDuration = 0.25
    suitTrack = getSuitTrack(attack)
    posPoints = [Point3(-0.25, 0, 0), VBase3(90, 180, 0)]
    propTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        teeth = globalPropPool.getProp('teeth')
        teethAppearTrack = Sequence(getPropAppearTrack(teeth, suit.getRightHand(), posPoints, propDelay, Point3(3, 3, 3), scaleUpTime=propScaleUpTime))
        teethAppearTrack.append(Wait(suitDelay))
        teethAppearTrack.append(Func(battle.movie.needRestoreRenderProp, teeth))
        teethAppearTrack.append(Func(teeth.wrtReparentTo, battle))
        if dmg > 0:
            x = toon.getX(battle)
            y = toon.getY(battle)
            z = toon.getZ(battle)
            toonHeight = z + toon.getHeight()
            flyPoint = Point3(x, y + 2.7, toonHeight * 0.8)
            teethAppearTrack.append(LerpPosInterval(teeth, throwDuration, pos=flyPoint))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.4, pos=Point3(x, y + 3.2, toonHeight * 0.7)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.3, pos=Point3(x, y + 4.7, toonHeight * 0.5)))
            teethAppearTrack.append(Wait(0.2))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.1, pos=Point3(x, y - 0.2, toonHeight * 0.9)))
            teethAppearTrack.append(Wait(0.4))
            scaleTrack = Sequence(Wait(throwDelay), LerpScaleInterval(teeth, throwDuration, Point3(8, 8, 8)), Wait(0.9), LerpScaleInterval(teeth, 0.2, Point3(14, 14, 14)), Wait(1.2), LerpScaleInterval(teeth, 0.3, MovieUtil.PNT3_NEARZERO))
            hprTrack = Sequence(Wait(throwDelay), LerpHprInterval(teeth, 0.3, Point3(180, 0, 0)), Wait(0.2), LerpHprInterval(teeth, 0.4, Point3(180, -35, 0), startHpr=Point3(180, 0, 0)), Wait(0.1), LerpHprInterval(teeth, 0.1, Point3(180, -75, 0), startHpr=Point3(180, -35, 0)))
            animTrack = Sequence(Wait(throwDelay), ActorInterval(teeth, 'teeth', duration=throwDuration), ActorInterval(teeth, 'teeth', duration=0.3), Func(teeth.pose, 'teeth', 1), Wait(0.7), ActorInterval(teeth, 'teeth', duration=0.9))
            propTrack = Sequence(Parallel(teethAppearTrack, scaleTrack, hprTrack, animTrack), Func(MovieUtil.removeProp, teeth), Func(battle.movie.clearRenderProp, teeth))
        else:
            flyPoint = __toonFacePoint(toon, parent=battle)
            flyPoint.setY(flyPoint.getY() - 7.1)
            teethAppearTrack.append(LerpPosInterval(teeth, throwDuration, pos=flyPoint))
            teethAppearTrack.append(Func(MovieUtil.removeProp, teeth))
            teethAppearTrack.append(Func(battle.movie.clearRenderProp, teeth))
            propTrack = teethAppearTrack
        propTracks.append(propTrack)

    damageAnims = [['cringe',
      0.01,
      0.7,
      1.2], ['conked',
      0.01,
      0.2,
      2.1], ['conked', 0.01, 3.2]]
    dodgeAnims = [['cringe',
      0.01,
      0.7,
      0.2], ['duck', 0.01, 1.6]]
    toonTracks = getToonTracks(attack, damageDelay=2.1, splicedDamageAnims=damageAnims, dodgeDelay=1.7, splicedDodgeAnims=dodgeAnims, showDamageExtraTime=2.4)
    soundTrack = getSoundTrack('SA_bite%s.ogg' % ('' if hitAtleastOneToon else '_miss'), delay=2, node=suit)
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    return Parallel(suitTrack, toonTracks, soundTrack, propTracks)


def doChomp(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1
    propDelay = 0.25
    propScaleUpTime = 0.25
    suitDelay = 1.55
    throwDelay = propDelay + propScaleUpTime + suitDelay
    throwDuration = 0.25
    posPoints = [Point3(-0.25, 0, 0), VBase3(90, 180, 0)]
    propTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        teeth = globalPropPool.getProp('teeth')
        teethAppearTrack = Sequence(getPropAppearTrack(teeth, suit.getRightHand(), posPoints, propDelay, Point3(3, 3, 3),
                                                       scaleUpTime=propScaleUpTime))
        teethAppearTrack.append(Wait(suitDelay))
        teethAppearTrack.append(Func(battle.movie.needRestoreRenderProp, teeth))
        teethAppearTrack.append(Func(teeth.wrtReparentTo, battle))
        if dmg > 0:
            x = toon.getX(battle)
            y = toon.getY(battle)
            z = toon.getZ(battle)
            toonHeight = z + toon.getHeight()
            flyPoint = Point3(x, y + 2.7, toonHeight * 0.7)
            teethAppearTrack.append(LerpPosInterval(teeth, throwDuration, pos=flyPoint))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.4, pos=Point3(x, y + 3.2, toonHeight * 0.7)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.3, pos=Point3(x, y + 4.7, toonHeight * 0.5)))
            teethAppearTrack.append(Wait(0.2))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.1, pos=Point3(x, y, toonHeight + 3)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.1, pos=Point3(x, y - 1.2, toonHeight * 0.7)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.1, pos=Point3(x, y - 0.7, toonHeight * 0.4)))
            teethAppearTrack.append(Wait(0.4))
            scaleTrack = Sequence(Wait(throwDelay), LerpScaleInterval(teeth, throwDuration, Point3(6, 6, 6)), Wait(0.9),
                                  LerpScaleInterval(teeth, 0.2, Point3(10, 10, 10)), Wait(1.2),
                                  LerpScaleInterval(teeth, 0.3, MovieUtil.PNT3_NEARZERO))
            hprTrack = Sequence(Wait(throwDelay), LerpHprInterval(teeth, 0.3, Point3(180, 0, 0)), Wait(0.2),
                                LerpHprInterval(teeth, 0.4, Point3(180, -35, 0), startHpr=Point3(180, 0, 0)), Wait(0.1),
                                LerpHprInterval(teeth, 0.1, Point3(0, -35, 0), startHpr=Point3(180, -35, 0)))
            animTrack = Sequence(Wait(throwDelay), ActorInterval(teeth, 'teeth', duration=throwDuration),
                                 ActorInterval(teeth, 'teeth', duration=0.3),
                                 Func(teeth.pose, 'teeth', 1), Wait(0.7),
                                 ActorInterval(teeth, 'teeth', duration=0.9))
            propTrack = Sequence(Parallel(teethAppearTrack, scaleTrack, hprTrack, animTrack),
                                 Func(MovieUtil.removeProp, teeth), Func(battle.movie.clearRenderProp, teeth))
        else:
            x = toon.getX(battle)
            y = toon.getY(battle)
            z = toon.getZ(battle)
            z = z + 0.2
            flyPoint = Point3(x, y - 2.1, z)
            teethAppearTrack.append(LerpPosInterval(teeth, throwDuration, pos=flyPoint))
            teethAppearTrack.append(Wait(0.2))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x + 0.5, y - 2.5, z)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x + 1.0, y - 3.0, z + 0.4)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x + 1.3, y - 3.6, z)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x + 0.9, y - 3.1, z + 0.4)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x + 0.3, y - 2.6, z)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x - 0.1, y - 2.2, z + 0.4)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x - 0.4, y - 1.9, z)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x - 0.7, y - 2.1, z + 0.4)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x - 0.8, y - 2.3, z)))
            teethAppearTrack.append(LerpScaleInterval(teeth, 0.6, MovieUtil.PNT3_NEARZERO))
            hprTrack = Sequence(Wait(throwDelay), LerpHprInterval(teeth, 0.3, Point3(180, 0, 0)), Wait(0.5),
                                LerpHprInterval(teeth, 0.4, Point3(80, 0, 0), startHpr=Point3(180, 0, 0)),
                                LerpHprInterval(teeth, 0.8, Point3(-10, 0, 0), startHpr=Point3(80, 0, 0)))
            animTrack = Sequence(Wait(throwDelay), ActorInterval(teeth, 'teeth', duration=3.6))
            propTrack = Sequence(Parallel(teethAppearTrack, hprTrack, animTrack), Func(MovieUtil.removeProp, teeth),
                                 Func(battle.movie.clearRenderProp, teeth))
        propTracks.append(propTrack)

    damageAnims = [['cringe',
                    0.01,
                    0.7,
                    1.2],
                   ['spit',
                    0.01,
                    2.95,
                    1.47],
                   ['spit',
                    0.01,
                    4.42,
                    0.07],
                   ['spit',
                    0.08,
                    4.49,
                    -0.07],
                   ['spit',
                    0.08,
                    4.42,
                    0.07],
                   ['spit',
                    0.08,
                    4.49,
                    -0.07],
                   ['spit',
                    0.08,
                    4.42,
                    0.07],
                   ['spit',
                    0.08,
                    4.49,
                    -0.07],
                   ['spit', 0.01, 4.42]]
    dodgeAnims = [['jump', 0.01, 0.01]]
    toonTracks = getToonTracks(attack, damageDelay=2.1, splicedDamageAnims=damageAnims, dodgeDelay=1.75,
                               splicedDodgeAnims=dodgeAnims, showDamageExtraTime=1.4)
    soundTrack = getSoundTrack('SA_bite%s.ogg' % ('' if hitAtleastOneToon else '_miss'), delay=2, node=suit)
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    return Parallel(suitTrack, toonTracks, soundTrack, propTracks)


def doInject(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    laptop = globalPropPool.getProp('laptop')
    card = globalPropPool.getProp('ttht_m_ene_techbotLaptop')
    card.setScale(1.5)
    BattleParticles.loadParticles()
    particleEffects = []
    particleEffects2 = []
    particleEffects3 = []
    particleEffects4 = []
    particleEffects5 = []
    for t in targets:
        particleEffect = BattleParticles.createParticleEffect('Calculate')
        BattleParticles.setEffectTexture(particleEffect, 'audit-one', color=Vec4(0, 0, 0, 1))
        particleEffect2 = BattleParticles.createParticleEffect('Calculate')
        BattleParticles.setEffectTexture(particleEffect2, 'audit-two', color=Vec4(0, 0, 0, 1))
        particleEffect3 = BattleParticles.createParticleEffect('Calculate')
        BattleParticles.setEffectTexture(particleEffect3, 'audit-three', color=Vec4(0, 0, 0, 1))
        particleEffect4 = BattleParticles.createParticleEffect('Calculate')
        BattleParticles.setEffectTexture(particleEffect4, 'audit-four', color=Vec4(0, 0, 0, 1))
        particleEffect5 = BattleParticles.createParticleEffect('Calculate')
        BattleParticles.setEffectTexture(particleEffect5, 'audit-mult', color=Vec4(0, 0, 0, 1))
        particleEffects.append(particleEffect)
        particleEffects2.append(particleEffect2)
        particleEffects3.append(particleEffect3)
        particleEffects4.append(particleEffect4)
        particleEffects5.append(particleEffect5)

    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    partTracks = getPartTracks(attack, particleEffects, 1.5, 2.5, 0, softStop=-1)
    partTracks2 = getPartTracks(attack, particleEffects2, 1.6, 2.5, 0, softStop=-1)
    partTracks3 = getPartTracks(attack, particleEffects3, 1.7, 2.6, 0, softStop=-1)
    partTracks4 = getPartTracks(attack, particleEffects4, 1.8, 2.7, 0, softStop=-1)
    partTracks5 = getPartTracks(attack, particleEffects5, 1.9, 2.8, 0, softStop=-1)
    laptopPosPoints = [Point3(0, 0.75, -0.2), VBase3(0, 0, 180)]
    laptopDuration = 2.8
    scaleUpPoint = Point3(1.5, 1.5, 1.5)
    damageAnims = []
    damageAnims.append(['cringe'])
    soundTrack = getSoundTrack('SA_keyPunch.ogg', node=suit)
    propTrackNew = Parallel()
    propTrackNew = Sequence(
        Func(__showProp, card, suit.getLeftHand(), *laptopPosPoints),
        ActorInterval(card, 'ttht_m_ene_techbotLaptop', playRate=1.5),
        Func(MovieUtil.removeProp, card)
    )
    #propTrackNew.append(getPropTrack(card, suit.getLeftHand(), laptopPosPoints, 1e-06, 2, scaleUpPoint=scaleUpPoint, scaleUpTime=0,
                                         #     anim=1, animStartTime=0.5, animDuration=2.5,
                                          #    propName='ttht_m_ene_techbotLaptop'))
    #calcPropTrack = getPropTrack(laptop, suit.getLeftHand(), laptopPosPoints, 1e-06, laptopDuration, scaleUpPoint=scaleUpPoint, anim=0, propName='laptop', animStartTime=0, animDuration=0)
    toonTracks = getToonTracks(attack, 2.8, splicedDamageAnims=damageAnims, dodgeDelay=2.8, dodgeAnimNames=['jump'])
    return Parallel(suitTrack, toonTracks, soundTrack, propTrackNew, partTracks, partTracks2, partTracks3, partTracks4, partTracks5)

def doEvictionNotice(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        posPoints = [Point3(0.88, -2.21917, -0.22), VBase3(10, 250, -10)]
        scale = Point3(1.2, 1.2, 1.2)
    else:
        posPoints = [Point3(.78, -1.89, -.17), VBase3(10, 250, -10)]
        scale = Point3(1, 1, 1)
    propTracks = Parallel()
    for t in targets:
        toon = t['toon']
        paper = globalPropPool.getProp('shredder-paper')
        propTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.75, scale, scaleUpTime=0.25))
        propTrack.append(Wait(0.95))
        hitPoint = __toonFacePoint(toon, parent=battle)
        hitPoint.setX(hitPoint.getX() - 1.4)
        missPoint = __toonGroundPoint(attack, toon, 0.5, parent=battle)
        missPoint.setX(missPoint.getX() - 1.1)
        propTrack.append(getPropThrowTrack(attack, paper, [hitPoint], [missPoint], .25, parent=battle, target=t))
        explodePosPoints = [Point3(0, 0, 0), MovieUtil.PNT3_ZERO]
        splatName = 'dust'
        splat = globalPropPool.getProp('dust')
        explode = globalPropPool.getProp('dust')
        explode.setTwoSided(True)


        explode.setBillboardPointWorld(2)
        explodeTrack = Sequence()
        explodeTrack.append(
        getPropAppearTrack(explode, toon, explodePosPoints, 0, Point3(2, 2, 2), scaleUpTime=0))
        explodeTrack.append(Sequence(ActorInterval(explode, splatName), Func(explode.detachNode)))
        soundTrack = getSoundTrack('LB_evidence_miss.ogg', node=suit)
        propTrack.append(Parallel(explodeTrack, soundTrack))
        propTracks.append(propTrack)

    toonTracks = getToonTracks(attack, 2.2, ['conked'], 2, ['jump'])
    return Parallel(suitTrack, toonTracks, propTracks)



def doCloseTheLoopNew(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    taunt = random.choice(["Don't bring a Gag to a knife fight.",
"Get to the point!",
"I have some sharp words for you.",
"I won't fall for your childish pranks.",
"I'll use this occasion to sharpen my skills.",
"I'm the sharpest Suit around!",
"It's knife to meet you.",
"My tactics are on the cutting edge.",
"This attack is a cut above the rest.",
"Toons like you can't cut it with us.",
"Twice the pride, double the fall.",
"You'll find that this company never cuts corners.",
"Your chances of victory are in free fall."])
    taunt2 = random.choice(['Let me loop you in on how things work.',
 'This ought to throw you in for a loop.',
 "Oh my, you're really out of the loop!",
 'Found a loophole in the system? Time to close it.',
 "Now I'm closing in on you!"])
    tauntInterval = Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout)
    tauntInterval2 = Func(suit.setChatAbsolute, taunt2, CFSpeech | CFTimeout)
    suitTrack = Sequence(tauntInterval, ActorInterval(suit, 'effort', duration=2.5, playRate=1.5), tauntInterval2, ActorInterval(suit, 'glower'), Func(suit.setNeutralAnimation))
    allKnifeTracks = Parallel()
    toon = target[0]['toon']
    numKnives = 15
    knifeTracks = Sequence()
    knives = [globalPropPool.getProp('dagger') for i in range(numKnives)]
    step = math.radians(360.0 / numKnives)
    radius = 4.0
    prepareKnives = Parallel()
    for i in range(len(knives)):
        angle = i * step
        x = radius * math.cos(angle) + toon.getX(battle)
        y = radius * math.sin(angle) + toon.getY(battle)
        knife = knives[i]
        prepareKnives.append(Sequence(
            Wait(i * 0.1),
            Func(knife.reparentTo, battle),
            Func(knife.setPos, Point3(x, y, 1.0)),
            Func(knife.lookAt, Point3(toon.getX(battle), toon.getY(battle), 1.0)),
            Func(base.playSfx, globalBattleSoundCache.getSound('SA_wire_cut_knife.ogg'), node=toon),
            LerpScaleInterval(knife, 0.25, Point3(0.5), startScale=Point3(0.01)),
            ))

    knifeTracks.append(prepareKnives)
    knifeTracks.append(Wait(1.7))
    closeTrack = Parallel()
    for knife in knives:
        closeTrack.append(Sequence(
                LerpPosInterval(knife, 0.2, Point3(toon.getX(battle), toon.getY(battle), 1.0), blendType='easeIn'),
                Func(MovieUtil.removeProp, knife)
            ))

    knifeTracks.append(closeTrack)
    allKnifeTracks.append(knifeTracks)

    damageAnims = [['slip-backward', 0.01, 0.6]]
    partTracks = Parallel()
    toonTracks = getToonTrack(attack, damageDelay=3.55, splicedDamageAnims=damageAnims, dodgeDelay=2.2,
                               dodgeAnimNames=['jump'])
    soundTracks = Parallel()
    sparkEffect = BattleParticles.loadParticleFile('resistanceEffectSparkle.ptf')
    sparks = sparkEffect.getParticlesNamed('particles-1')
    sparks.setPoolSize(20)
    sparks.setLitterSize(20)
    sparks.renderer.setEdgeColor(Vec4(1.0, 1.0, 1.0, 1.0))
    sparks.renderer.setEdgeColor(Vec4(1.0, 0.0, 0.0, 1.0))
    partTracks.append(Sequence(
            Wait(3.55),
            Parallel(
                ParticleInterval(sparkEffect, toon, worldRelative=0, duration=3.0, cleanup=True),
                autoFinish=1
            )
        ))
    soundTracks.append(getSoundTrack('tt_s_ara_cmg_toonHit.ogg', delay=3.55, node=toon))
    # I have no clue what to do with this.  I know we have the new method of the cheats, but it seems all of these were kept for some reason.
    # name = attack['id']
    # if name == DETONATE_3:
    #     suitTrack.append(Wait(2))
    #     suitTrack.append(doRefinement(attack))
    # if name == REFINEMENT:
    #     suitTrack.append(Wait(2))
    #     suitTrack.append(doRefinement(attack))
    # if name == MANAGERIAL_PROTECTION:
    #     suitTrack.append(Wait(2))
    #     suitTrack.append(doManagerialProtection(attack))
    return Parallel(suitTrack, allKnifeTracks, partTracks, toonTracks, soundTracks)

def doSmokeAndMirrors(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    tauntIndex = attack['taunt']
    toon = attack['target'][0]['toon']
    dmg = target[0]['hp']
    taunt = getAttackTaunt('CigarSmoke', attack['suitName'], tauntIndex)
    BattleParticles.loadParticles()
    battle = attack['battle']
    toon = target[0]['toon']
    suitTrack = Parallel(getSuitTrack(attack), MovieUtil.createSuitHeadHonchoCigarSmokeInterval(suit))
    baseFlameSmall = BattleParticles.createParticleEffect(file='cigarSmokeAtk')
    baseFlameEffect = BattleParticles.createParticleEffect(file='cigarSmokeAtk')
    cigarSmoke = BattleParticles.createParticleEffect(file='smoke')
    baseFlameSmall.setScale(0.7)
    cigar = globalPropPool.getProp('cigar')
    cigarPosPoints = [Point3(-0.05, -0.2, -0.25), VBase3(180.0, 0.0, 0.0)]
    cigarScale = Point3(7.0, 7.0, 7.0)
    propTrack = getPropTrack(cigar, suit.getRightHand(), cigarPosPoints, 1.5, 2.5, scaleUpPoint=cigarScale)
    baseFlameTrack = getPartTrack(baseFlameEffect, 2.25, 3.25, [baseFlameEffect, suit, 0], softStop=-2)
    baseFlameSmallTrack = getPartTrack(baseFlameSmall, 2.25, 3.25, [baseFlameSmall, suit, 0], softStop=-2)
    partTrack = getPartTrack(cigarSmoke, 2.0, 3.5, [cigarSmoke, suit, 0], softStop=-2)
    hitSuit = dmg > 0
    particles = []
    particleTracks = Parallel()
    for i in xrange(0, 5):
        particleEffect = BattleParticles.createParticleEffect('Smile')
        particleEffect.setZ(suit.height - 1)
        particleEffect.setScale(2)
        particles.append(particleEffect)

    if hitSuit:
        hitPoint = lambda toon = toon: __toonFacePoint(toon)
    else:
        hitPoint = lambda particleEffect = particleEffect, toon = toon, suit = suit: __toonMissPoint(particleEffect, toon, parent=suit.getRightHand())

    for i in xrange(0, 5):
        particleTrack = Parallel()
        particleTrack.append(Sequence(Wait(2), Wait(i * .25), Func(particles[i].start, suit),
                                Func(particles[i].wrtReparentTo, render), 
                                LerpPosInterval(particles[i], 1.5, pos=hitPoint), 
                                Func(particles[i].cleanup),
                                Func(battle.movie.clearRestoreParticleEffect, particles[i])))
        particleTracks.append(particleTrack)


    def changeColor(parts):
        track = Parallel()
        for partNum in range(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(nextPart.colorScaleInterval(0.1, Vec4(0.5, 0.5, 0.5, 1)))

        return track

    def resetColor(parts):
        track = Parallel()
        for partNum in range(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.clearColorScale))

        return track

    if dmg > 0:
        headParts = toon.getHeadParts()
        torsoParts = toon.getTorsoParts()
        legsParts = toon.getLegsParts()
        colorTrack = Sequence()
        colorTrack.append(Wait(2.55))
        colorTrack.append(Func(battle.movie.needRestoreColor))
        colorTrack.append(changeColor(headParts))
        colorTrack.append(changeColor(torsoParts))
        colorTrack.append(changeColor(legsParts))
        colorTrack.append(Wait(3.5))
        colorTrack.append(resetColor(headParts))
        colorTrack.append(resetColor(torsoParts))
        colorTrack.append(resetColor(legsParts))
        colorTrack.append(Func(battle.movie.clearRestoreColor))
    damageAnims = []
    damageAnims.append(['cringe',
                        0.01,
                        0.7,
                        0.62])
    damageAnims.append(['slip-forward',
                        1e-05,
                        0.4,
                        1.2])
    damageAnims.extend(getSplicedLerpAnims('slip-forward', 0.31, 0.8, startTime=4.2))
    toonTrack = getToonTrack(attack, 2.55, ['cringe'], 2.0, ['sidestep'])
    soundTrack = getSoundTrack('SA_filibuster.ogg', delay=2.25, node=suit)
    soundTrack2 = getSoundTrack('SA_razzle_dazzle.ogg', delay=2.25, node=suit)
    if dmg > 0:
        return Parallel(suitTrack, soundTrack2, particleTracks, propTrack, baseFlameTrack, toonTrack, partTrack, colorTrack, soundTrack)
    else:
        return Parallel(suitTrack, soundTrack2, particleTracks, propTrack, baseFlameSmallTrack, partTrack, toonTrack, soundTrack)


def doHeadHonchoCigarSmoke(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    tauntIndex = attack['taunt']
    toon = attack['target'][0]['toon']
    dmg = target[0]['hp']
    taunt = getAttackTaunt('CigarSmoke', attack['suitName'], tauntIndex)
    BattleParticles.loadParticles()
    battle = attack['battle']
    toon = target[0]['toon']
    suitTrack = Parallel(getSuitTrack(attack), MovieUtil.createSuitHeadHonchoCigarSmokeInterval(suit))
    baseFlameSmall = BattleParticles.createParticleEffect(file='cigarSmokeAtk')
    baseFlameEffect = BattleParticles.createParticleEffect(file='cigarSmokeAtk')
    cigarSmoke = BattleParticles.createParticleEffect(file='smoke')
    baseFlameSmall.setScale(0.7)
    cigar = globalPropPool.getProp('cigar')
    cigarPosPoints = [Point3(-0.05, -0.2, -0.25), VBase3(180.0, 0.0, 0.0)]
    cigarScale = Point3(7.0, 7.0, 7.0)
    propTrack = getPropTrack(cigar, suit.getRightHand(), cigarPosPoints, 1.5, 2.5, scaleUpPoint=cigarScale)
    baseFlameTrack = getPartTrack(baseFlameEffect, 2.25, 3.25, [baseFlameEffect, suit, 0], softStop=-2)
    baseFlameSmallTrack = getPartTrack(baseFlameSmall, 2.25, 3.25, [baseFlameSmall, suit, 0], softStop=-2)
    partTrack = getPartTrack(cigarSmoke, 2.0, 3.5, [cigarSmoke, suit, 0], softStop=-2)

    def changeColor(parts):
        track = Parallel()
        for partNum in range(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(nextPart.colorScaleInterval(0.1, Vec4(0.5, 0.5, 0.5, 1)))

        return track

    def resetColor(parts):
        track = Parallel()
        for partNum in range(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.clearColorScale))

        return track

    if dmg > 0:
        headParts = toon.getHeadParts()
        torsoParts = toon.getTorsoParts()
        legsParts = toon.getLegsParts()
        colorTrack = Sequence()
        colorTrack.append(Wait(2.55))
        colorTrack.append(Func(battle.movie.needRestoreColor))
        colorTrack.append(changeColor(headParts))
        colorTrack.append(changeColor(torsoParts))
        colorTrack.append(changeColor(legsParts))
        colorTrack.append(Wait(3.5))
        colorTrack.append(resetColor(headParts))
        colorTrack.append(resetColor(torsoParts))
        colorTrack.append(resetColor(legsParts))
        colorTrack.append(Func(battle.movie.clearRestoreColor))
    damageAnims = []
    damageAnims.append(['cringe',
                        0.01,
                        0.7,
                        0.62])
    damageAnims.append(['slip-forward',
                        1e-05,
                        0.4,
                        1.2])
    damageAnims.extend(getSplicedLerpAnims('slip-forward', 0.31, 0.8, startTime=4.2))
    toonTrack = getToonTrack(attack, 2.8, ['cringe'], 2.0, ['sidestep'])
    soundTrack = getSoundTrack('SA_filibuster.ogg', delay=2.25, node=suit)
    if dmg > 0:
        return Parallel(suitTrack, propTrack, baseFlameTrack, toonTrack, partTrack, colorTrack, soundTrack)
    else:
        return Parallel(suitTrack, propTrack, baseFlameSmallTrack, partTrack, toonTrack, soundTrack)

def doFirestarterCigarSmoke(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    tauntIndex = attack['taunt']
    toon = attack['target'][0]['toon']
    dmg = target[0]['hp']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    suitTrack = Parallel(getSuitTrack(attack, playRate=1.25), MovieUtil.createSuitFirestarterCigarSmokeInterval(suit))
    BattleParticles.loadParticles()
    baseFlameSmall = BattleParticles.createParticleEffect(file='cigarSmokeAtk')
    baseFlameEffect = BattleParticles.createParticleEffect(file='cigarSmokeAtk')
    cigarSmoke = BattleParticles.createParticleEffect(file='smoke')
    baseFlameSmall.setScale(0.7)
    cigar = globalPropPool.getProp('cigar')
    cigarPosPoints = [Point3(0, -0.08670520231213885, 0), VBase3(180.0, 0.0, 0.0)]
    cigarScale = Point3(4.0, 4.0, 4.0)
    propTrack = getPropTrack(cigar, suit.getRightHand(), cigarPosPoints, 0.5, 3.5, scaleUpPoint=cigarScale)
    baseFlameTrack = getPartTrack(baseFlameEffect, 2.25, 3.25, [baseFlameEffect, suit, 0], softStop=-2)
    baseFlameSmallTrack = getPartTrack(baseFlameSmall, 2.25, 3.25, [baseFlameSmall, suit, 0], softStop=-2)
    partTrack = getPartTrack(cigarSmoke, 2.0, 3.5, [cigarSmoke, suit, 0], softStop=-2)

    def changeColor(parts):
        track = Parallel()
        for partNum in range(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(nextPart.colorScaleInterval(0.1, Vec4(0.5, 0.5, 0.5, 1)))

        return track

    def resetColor(parts):
        track = Parallel()
        for partNum in range(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.clearColorScale))

        return track

    if dmg > 0:
        headParts = toon.getHeadParts()
        torsoParts = toon.getTorsoParts()
        legsParts = toon.getLegsParts()
        colorTrack = Sequence()
        colorTrack.append(Wait(2.55))
        colorTrack.append(Func(battle.movie.needRestoreColor))
        colorTrack.append(changeColor(headParts))
        colorTrack.append(changeColor(torsoParts))
        colorTrack.append(changeColor(legsParts))
        colorTrack.append(Wait(3.5))
        colorTrack.append(resetColor(headParts))
        colorTrack.append(resetColor(torsoParts))
        colorTrack.append(resetColor(legsParts))
        colorTrack.append(Func(battle.movie.clearRestoreColor))
    damageAnims = []
    damageAnims.append(['cringe',
                        0.01,
                        0.7,
                        0.62])
    damageAnims.append(['slip-forward',
                        1e-05,
                        0.4,
                        1.2])
    damageAnims.extend(getSplicedLerpAnims('slip-forward', 0.31, 0.8, startTime=4.2))
    toonTrack = getToonTrack(attack, 2.8, ['cringe'], 2.0, ['sidestep'])
    soundTrack = getSoundTrack('SA_filibuster.ogg', delay=2.25, node=suit)
    if dmg > 0:
        return Parallel(suitTrack, propTrack, baseFlameTrack, toonTrack, partTrack, colorTrack, soundTrack)
    else:
        return Parallel(suitTrack, propTrack, baseFlameSmallTrack, partTrack, toonTrack, soundTrack)


def doFallingKnife(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = getSuitTrack(attack)
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        posPoints = [Point3(-0.1935483870967758, 0.4516129032258078, 0.0), VBase3(0, 0, 0)]
    else:
        posPoints = [Point3(-0.06451612903225978, 0.5806451612903203, 0.0), VBase3(0, 0, 0)]
    knifeTracks = Parallel()
    sparkTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        knife = globalPropPool.getProp('dagger')
        knifeTrack = Sequence(
            getPropAppearTrack(knife, suit.getRightHand(), posPoints, 0.25, scaleUpPoint=Point3(1.0), scaleUpTime=0.1),
            Wait(1.3),
            Parallel(
                getThrowTrack(knife, toon.getPos(battle), 2.35, battle, -64.288),
                LerpHprInterval(knife, 0.8, VBase3(720, 630, 720))
            ),
            Func(MovieUtil.removeProp, knife)
        )
        knifeTracks.append(knifeTrack)
        sparkEffect = BattleParticles.loadParticleFile('resistanceEffectSparkle.ptf')
        sparks = sparkEffect.getParticlesNamed('particles-1')
        if sparks:
            sparks.setPoolSize(10)
            sparks.setLitterSize(10)
            sparks.renderer.setEdgeColor(Vec4(1.0, 0.0, 0.0, 1.0))
        if dmg != 0:
            sparkTracks.append(Sequence(
                Wait(4.0),
                Parallel(
                    ParticleInterval(sparkEffect, toon, worldRelative=0, duration=3.0, cleanup=True),
                    autoFinish=1
                )
            ))

    damageAnims = [['slip-forward', 0.01, 0.4]]
    toonTracks = getToonTracks(attack, damageDelay=4.0, splicedDamageAnims=damageAnims, dodgeDelay=3.1, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_falling_knife.ogg', node=suit)
    return Parallel(suitTrack, knifeTracks, sparkTracks, toonTracks, soundTrack)

def doShortSqueeze(attack):
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.0
    suitTrack = getSuitTrack(attack)
    damageAnims = [['struggle', 0.01, 0.01, 1.0],
     ['slip-backward', 0.01, 0.01]]
    shakeTracks = Parallel()
    squeezeTracks = Parallel()
    coinTracks = Parallel()
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.5, dodgeAnimNames=['sidestep'], showDamageExtraTime=1.1)
    soundTracks = Parallel()
    for t in targets:
        dmg = t['hp']
        toon = t['toon']
        if dmg > 0:
            x = toon.getX(); y = toon.getY(); z = toon.getZ()
            groundPoint = Point3(x, y, z)
            moveTime = 0.15
            shakeTrack = Sequence(Wait(damageDelay))
            for i in xrange(0, 5):
                shakeTrack.append(LerpPosInterval(toon, moveTime, Point3(x, y, z + 3)))
                shakeTrack.append(LerpPosInterval(toon, moveTime, Point3(x, y, z + 1.5)))

            shakeTrack.append(LerpPosInterval(toon, 0.15, groundPoint))
            shakeTracks.append(shakeTrack)
            initialScale = toon.getScale()
            xScale, yScale, zScale = initialScale
            squeezeTrack = Sequence(
                Wait(damageDelay),
                Func(battle.movie.needRestoreToonScale),
                LerpScaleInterval(toon, 0.1, Vec3(xScale * 0.6, yScale * 0.46, zScale * 1.2)),
                Wait(1.1),
                LerpScaleInterval(toon, 0.2, Vec3(xScale * 1.2, yScale * 1.2, zScale * 0.8)),
                LerpScaleInterval(toon, 0.2, initialScale),
                Func(battle.movie.clearRestoreToonScale)
            )
            squeezeTracks.append(squeezeTrack)
            coinTrack = Parallel()
            coinTypes = ['bronze', 'silver', 'gold']
            for i in xrange(0, 20):
                coin = loader.loadModel('phase_3.5/models/props/cc_m_prp_gen_coin_' + random.choice(coinTypes) + '.bam')
                pnt = toon.getPos(toon); pnt.setZ(pnt[2] + toon.shoulderHeight - 0.2); startPos = Point3(pnt)
                xOffset = random.random() * 5
                if random.choice([False, True]):
                    xOffset *= -1
                yOffset = random.random() * 5
                if random.choice([False, True]):
                    yOffset *= -1
                landPos = toon.getPos(battle)
                landPos.setX(landPos.getX() + xOffset); landPos.setY(landPos.getY() + yOffset)
                coinTrack.append(Sequence(
                    Wait(damageDelay + 0.1 * i),
                    Func(__showProp, coin, toon, startPos, VBase3(random.randint(0, 359), random.randint(0, 359), random.randint(0, 359)), Point3(1.0)),
                    getThrowTrack(coin, landPos, 1.0, battle),
                    Func(coin.removeNode)
                ))

            coinTracks.append(coinTrack)
            soundTracks.append(Track(
                (1.0, SoundInterval(globalBattleSoundCache.getSound('SA_short_squeeze.ogg'), node=toon)),
                (2.4, SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=toon))
            ))

    return Parallel(suitTrack, shakeTracks, squeezeTracks, coinTracks, toonTracks, soundTracks)

def doBlueChip(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    tauntIndex = attack['taunt']
    dmg = target[0]['hp']
    toon = attack['target'][0]['toon']

    chip = globalPropPool.getProp("chip_blue")
    firstHoldPosPoints = [Point3(-0.0012, 0.5083, -0.1271), Point3(-100, 0, 0)]
    grabPosPoints = [Point3(-0.2336, -0.0272, -0.0817), Point3(76.7974, -95.719, 0)]

    damageDelay = 3.1
    dodgeDelay = 2.2

    suitTrack = getSuitTrack(attack)

    landPos = toon.getPos(render)
    landPos.setZ(landPos.getZ() + 0.25)
    landUpPos = toon.getPos(render)
    landUpPos.setZ(landUpPos.getZ() + 0.8)

    invokerScale = suit.getScale()
    if getSuitBodyType(attack['suitName']) == 'a':
        scaleFactor = 1.19636963  # Head honcho scale
        startX, startY = 2.9, 4.2
        endX, endY = 0.7, 5.1
        startZ = 7.4
        endZ = 8.8
        chipHandScale = 1.15
        chipGrabScale = 1.15
        chipFlipMult = 6.5
    else:
        scaleFactor = 0.82041587901  # Insider scale
        startX, startY = 0.9, 2.1
        endX, endY = 0.9, 2.45
        startZ = 3.0
        endZ = 4.4
        chipHandScale = 0.95
        chipGrabScale = 0.8
        chipFlipMult = 5.0

    propTrack = Sequence(
        getPropAppearTrack(
            chip,
            suit.getRightHand(),
            firstHoldPosPoints,
            0.2,
            Point3(chipHandScale),
            scaleUpTime=0.25,
        ),
    )

    chipHandPosRenderStart = Point3(startX * (invokerScale[0] / scaleFactor),
                                    startY * (invokerScale[0] / scaleFactor),
                                    startZ * (invokerScale[0] / scaleFactor))
    chipHandPosRenderEnd = Point3(endX * (invokerScale[0] / scaleFactor),
                                    endY * (invokerScale[0] / scaleFactor),
                                    endZ * (invokerScale[0] / scaleFactor))

    propFlyTrack = Sequence(
        Wait(1.05),
        Func(chip.wrtReparentTo, suit),
        Parallel(
            ProjectileInterval(chip, startPos=chipHandPosRenderStart, endPos=chipHandPosRenderEnd, duration=0.5, gravityMult=chipFlipMult),
            LerpHprInterval(chip, 0.5, (90, -360, 0), startHpr=(0, 90, 0)),
        ),
        Func(chip.wrtReparentTo, suit.getRightHand()),
        Func(chip.setPosHpr, Point3(-0.2336, -0.0272, -0.0817), Point3(76.7974, -95.719, 0)),
        Func(chip.setScale, chipGrabScale),
        Wait(0.7),
        Func(chip.wrtReparentTo, render),
        Parallel(
            ProjectileInterval(chip, endPos=landPos, duration=0.95, gravityMult=2.15),
            LerpHprInterval(chip, 0.95, (0, 450, 0), startHpr=(0, 90, 0)),
            Sequence(
                Wait(0.25),
                LerpScaleInterval(chip, 0.65, 6.5),
            ),
        ),
        Parallel(
            LerpHprInterval(chip, 0.15, (20, 441, 0)),
            LerpPosInterval(chip, 0.15, landUpPos, blendType='easeOut'),
        ),
        Parallel(
            LerpHprInterval(chip, 0.225, (40, 450, 0)),
            LerpPosInterval(chip, 0.225, landPos, blendType='easeIn'),
        ),
        LerpHprInterval(chip, 0.3, (60, 450, 0)),
        LerpHprInterval(chip, 0.3, (70, 450, 0), blendType='easeOut'),
        Wait(0.1),
        LerpScaleInterval(chip, 0.35, 0.01, blendType='easeIn'),
        Func(chip.hide),
    )

    toonTrack = getToonTrack(attack, 3.3, ['squish'], 2.0, ['sidestep'])
    soundTrack2 = getSoundTrack('toon_decompress.ogg', node=suit)
    toonReactTrack = Sequence(Wait(3.05), Func(toon.playDialogueForString, "!"), Func(toon.enterFlattened), Wait(1.0), Parallel(ActorInterval(toon, 'jump'), soundTrack2, Func(toon.loop, 'neutral'),   Sequence(Wait(0.5), Func(toon.exitFlattened))))
    soundTrack = getSoundTrack(
        "SA_blue_chip.ogg", delay=0, node=suit
    )
    if dmg > 0:
        return Sequence(
            Parallel(
                suitTrack, toonTrack, toonReactTrack, soundTrack, propTrack, propFlyTrack,
            ),
            Func(MovieUtil.removeProp, chip),
        )
    else:
        return Sequence(
                Parallel(
                    suitTrack, toonTrack, soundTrack, propTrack, propFlyTrack,
                ),
                Func(MovieUtil.removeProp, chip),
            )


def doBlueChipOLD(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    suitDelay = 1.07
    propDelay = 0.6
    throwDuration = 1.0
    suitTrack = getSuitTrack(attack)
    if getSuitBodyType(attack['suitName']) == 'a':
        posPoints = [Point3(0.05, 0.5, -0.15), VBase3(70, 0, 0)]
    else:
        posPoints = [Point3(0.0, 0.4, -0.05), VBase3(90, 0, 0)]
    suit.pose('blue-chip', (1.5) * suit.getAnimControls('blue-chip', None, None)[0].getFrameRate() * 1) # The posing thing should be handled in a way similar to the way the defeat animation is handled where the time is gotten from an equation using a frame
    suit.update(0)
    chipFlipLandPos = suit.getRightHand().getPos(battle)
    if getSuitBodyType(attack['suitName']) == 'a':
        chipFlipLandPos.setX(chipFlipLandPos.getX() - 0.35); chipFlipLandPos.setY(chipFlipLandPos.getY() + 0.0); chipFlipLandPos.setZ(chipFlipLandPos.getZ() - 0.15)
    else:
        chipFlipLandPos.setX(chipFlipLandPos.getX() - 0.2); chipFlipLandPos.setY(chipFlipLandPos.getY() + 0.0); chipFlipLandPos.setZ(chipFlipLandPos.getZ() - 0.05)
    suit.loop('neutral')
    propTracks = Parallel()
    chip = loader.loadModel('phase_5/models/props/cc_m_prp_gen_chip_blue.bam')
    endingPos = chip.getPos()
    chipTrack = Sequence(
            getPropAppearTrack(chip, suit.getRightHand(), posPoints, propDelay - propDelay, Point3(1.0) if getSuitBodyType(attack['suitName']) == 'a' else Point3(0.75), scaleUpTime=0.5),
            Wait(0.5),
            Parallel(
                getThrowTrack(chip, chipFlipLandPos, 0.5, battle, -160.72),
                LerpHprInterval(chip, 0.5, VBase3(90, 450, 90))
            ),
            Func(chip.reparentTo, suit.getRightHand()),
            Func(chip.setPos, Point3(-0.35, 0.0, -0.15) if getSuitBodyType(attack['suitName']) == 'a' else Point3(-0.2, 0.0, -0.05)),
            Wait(suitDelay + propDelay - 1.0)
        )
    hitPoint = toon.getPos(battle)
    movePoint = Point3(hitPoint.getX(), hitPoint.getY(), hitPoint.getZ())
    movePoint2 = Point3(hitPoint.getX(), hitPoint.getY(), hitPoint.getZ() + .25)
    chipTrack.append(Func(battle.movie.needRestoreRenderProp, chip))
    chipTrack.append(Func(chip.wrtReparentTo, battle))
    chipTrack.append(getThrowTrack(chip, hitPoint, duration=throwDuration, parent=battle, gravity=-64.288))
    chipTrack.append(Parallel(Effects.createZBounce(chip, 3, movePoint2, 0.5, 0.5)))
    chipTrack.append(LerpPosInterval(chip, 0.4, movePoint))
    spinTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpHprInterval(chip, throwDuration, Point3(0, 810, 0)))
    spinTrack2 = Sequence(Wait(propDelay + suitDelay + 1.45), LerpHprInterval(
                chip,
                throwDuration,
                VBase3(0, 90, 90),
                startHpr=VBase3(0, 90, 0),
                other=battle
            ))
    #bounceTrack2 = Sequence(Wait(propDelay + suitDelay + 1.45), Effects.createZBounce(chip, .25, hitPoint, 0.5, 1.5), Effects.createZBounce(chip, .25, hitPoint, 0.5, 1.5), Effects.createZBounce(chip, .25, hitPoint, 0.5, 1.5))
    sizeTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpScaleInterval(chip, throwDuration, Point3(7)), Wait(0.95), LerpScaleInterval(chip, 0.4, MovieUtil.PNT3_NEARZERO))
    propTrack = Sequence(Parallel(chipTrack, sizeTrack, spinTrack2, spinTrack), Func(chip.removeNode))
    propTracks.append(propTrack)
    soundTrack2 = getSoundTrack('toon_decompress.ogg', node=suit)
    toonTracks = getToonTrack(attack, 3.3, ['squish'], 2.0, ['sidestep'])
    squishTrack = Sequence(Wait(3.05), Func(toon.enterFlattened), Wait(1.0), Parallel(ActorInterval(toon, 'jump'), soundTrack2, Func(toon.loop, 'neutral'), Sequence(Wait(0.5), Func(toon.exitFlattened))))
    soundTrack = getSoundTrack('SA_blue_chip.ogg', node=suit)
    if dmg > 0:
        return Parallel(suitTrack, toonTracks, propTracks, soundTrack, squishTrack)
    else:
        return Parallel(suitTrack, toonTracks, propTracks, soundTrack)

	
def doThrowBook(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitDelay = 1.5
    propDelay = 0.1
    throwDuration = 1.0
    paper = globalPropPool.getProp('lawbook')
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    posPoints = [Point3(-0.5, 0, 0), VBase3(0, 0, 180)]
    propTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        paperTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, propDelay, Point3(2.25, 2.25, 2.25), scaleUpTime=0.5))
        paperTrack.append(Wait(suitDelay))
        hitPoint = toon.getPos(battle)
        hitPoint.setX(hitPoint.getX() + 0)
        hitPoint.setY(hitPoint.getY() - .25)
        missPoint2 = toon.getPos(battle)
        missPoint2.setY(hitPoint.getY() - 7)
        movePoint = Point3(hitPoint.getX(), hitPoint.getY(), hitPoint.getZ() + 0.2)
        missPoint = Point3(missPoint2.getX(), missPoint2.getY(), missPoint2.getZ())
        paperTrack.append(Func(battle.movie.needRestoreRenderProp, paper))
        paperTrack.append(Func(paper.wrtReparentTo, battle))
        if dmg > 0:
            paperTrack.append(getThrowTrack(paper, hitPoint, duration=throwDuration, parent=battle, gravity=-100))
            paperTrack.append(Wait(0.6))
            paperTrack.append(LerpPosInterval(paper, 0.4, movePoint))
        else:
            paperTrack.append(getThrowTrack(paper, missPoint2, duration=throwDuration, parent=battle, gravity=-100))
            paperTrack.append(Wait(0.6))
            paperTrack.append(LerpPosInterval(paper, 0.4, missPoint))
        spinTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpHprInterval(paper, throwDuration, Point3(-360, 360, 360)))
        sizeTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpScaleInterval(paper, throwDuration, Point3(7, 7, 7)), Wait(0.95), LerpScaleInterval(paper, 0.75, MovieUtil.PNT3_NEARZERO))
        propTrack = Sequence(Parallel(paperTrack, spinTrack, sizeTrack), Func(MovieUtil.removeProp, paper), Func(battle.movie.clearRenderProp, paper))
        propTracks.append(propTrack)

    damageAnims = []
    damageAnims.append(['cringe',
     0.01,
     0.21,
     0.08])
    damageAnims.append(['slip-forward',
     0.01,
     0.6,
     0.85])
    damageAnims.extend(getSplicedLerpAnims('slip-forward', 0.31, 0.95, startTime=1.2))
    damageAnims.append(['slip-forward', 0.01, 1.51])
    soundTrack = getSoundTrack('SA_throw_book.ogg', node=suit)
    toonTracks = getToonTracks(attack, damageDelay=3, splicedDamageAnims=damageAnims, dodgeDelay=1.5, dodgeAnimNames=['duck'], showDamageExtraTime=0.4, showMissedExtraTime=1.3)
    return Parallel(suitTrack, toonTracks, propTracks, soundTrack)

def doCloudStorage(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    suitDelay = 0
    propDelay = 2.5
    throwDuration = 1.5
    paper = globalPropPool.getProp('stormcloud')
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    posPoints = [Point3(0, 0, 0), VBase3(0, 0, 0)]
    paperTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, propDelay, Point3(3.5, 3.5, 3.5), scaleUpTime=0.1))
    paperTrack.append(Wait(suitDelay))
    hitPoint = toon.getPos(battle)
    movePoint = Point3(hitPoint.getX(), hitPoint.getY(), hitPoint.getZ())
    paperTrack.append(Func(battle.movie.needRestoreRenderProp, paper))
    paperTrack.append(Func(paper.wrtReparentTo, battle))
    paperTrack.append(getThrowTrack(paper, hitPoint, duration=throwDuration, parent=battle))
    paperTrack.append(Wait(0.6))
    paperTrack.append(LerpPosInterval(paper, 0.1, movePoint))
    spinTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpHprInterval(paper, throwDuration, Point3(-360, 0, 0)))
    sizeTrack = Sequence(Wait(propDelay + suitDelay + 0.2), Parallel(LerpScaleInterval(paper, throwDuration, Point3(8, 8, 8)), Func(paper.loop, 'stormcloud')), LerpScaleInterval(paper, 1, MovieUtil.PNT3_NEARZERO))
    propTrack = Sequence(Parallel(paperTrack, sizeTrack), Func(MovieUtil.removeProp, paper), Func(battle.movie.clearRenderProp, paper))
    damageAnims = []
    damageAnims.append(['cringe',
     0.01,
     0.21,
     0.08])
    damageAnims.append(['slip-forward',
     0.01,
     0.6,
     0.85])
    damageAnims.extend(getSplicedLerpAnims('slip-forward', 0.31, 0.95, startTime=1.2))
    damageAnims.append(['slip-forward', 0.01, 1.51])
    shrinkTrack = Sequence(Wait(4.25), LerpScaleInterval(toon, 1, MovieUtil.PNT3_NEARZERO), Wait(2.0), LerpScaleInterval(toon, 0.5, Point3(1, 1, 1)))
    toonTrack = getToonTrack(attack, damageDelay=5.35, splicedDamageAnims=damageAnims, dodgeDelay=2.4, dodgeAnimNames=['sidestep'], showDamageExtraTime=0.4, showMissedExtraTime=1.3)
    if dmg > 0:
        return Parallel(suitTrack, toonTrack, propTrack, shrinkTrack)
    else:
        return Parallel(suitTrack, toonTrack, propTrack)


def doWithdrawal(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect('Withdrawal')
    BattleParticles.setEffectTexture(particleEffect, 'snow-particle')
    suitTrack = getSuitAnimTrack(attack)
    partTrack = getPartTrack(particleEffect, 1e-05, suitTrack.getDuration() + 2.2, [particleEffect, suit, 0], softStop=-1)
    toonTracks = getToonTracks(attack, 1.2, ['cringe'], 0.2, splicedDodgeAnims=[['duck', 1e-05, 0.8]], showMissedExtraTime=0.8)

    def changeColor(parts):
        track = Parallel()
        for partNum in xrange(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.setColorScale, Vec4(0, 0, 0, 1)))

        return track

    def resetColor(parts):
        track = Parallel()
        for partNum in xrange(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.clearColorScale))

        return track

    soundTrack = getSoundTrack('SA_withdrawl.ogg', delay=1.4, node=suit)
    colorTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        headParts = toon.getHeadParts()
        torsoParts = toon.getTorsoParts()
        legsParts = toon.getLegsParts()
        if dmg > 0:
            colorTrack = Sequence()
            colorTrack.append(Wait(1.6))
            colorTrack.append(Func(battle.movie.needRestoreColor))
            colorTrack.append(Parallel(changeColor(headParts), changeColor(torsoParts), changeColor(legsParts)))
            colorTrack.append(Wait(2.9))
            colorTrack.append(resetColor(headParts))
            colorTrack.append(resetColor(torsoParts))
            colorTrack.append(resetColor(legsParts))
            colorTrack.append(Func(battle.movie.clearRestoreColor))
            colorTracks.append(colorTrack)

    return Parallel(suitTrack, partTrack, toonTracks, soundTrack, colorTracks)


def doJargon(attack):
    suit = attack['suit']
    battle = attack['battle']
    BattleParticles.loadParticles()
    particleEffects = []
    particleEffects2 = []
    particleEffects3 = []
    particleEffects4 = []
    for t in attack['target']:
        particleEffect = BattleParticles.createParticleEffect(file='jargonSpray')
        particleEffect2 = BattleParticles.createParticleEffect(file='jargonSpray')
        particleEffect3 = BattleParticles.createParticleEffect(file='jargonSpray')
        particleEffect4 = BattleParticles.createParticleEffect(file='jargonSpray')
        BattleParticles.setEffectTexture(particleEffect, 'jargon-brow', color=Vec4(1, 0, 0, 1))
        BattleParticles.setEffectTexture(particleEffect2, 'jargon-deep', color=Vec4(0, 0, 0, 1))
        BattleParticles.setEffectTexture(particleEffect3, 'jargon-hoop', color=Vec4(1, 0, 0, 1))
        BattleParticles.setEffectTexture(particleEffect4, 'jargon-ipo', color=Vec4(0, 0, 0, 1))
        particleEffects.append(particleEffect)
        particleEffects2.append(particleEffect2)
        particleEffects3.append(particleEffect3)
        particleEffects4.append(particleEffect4)

    damageDelay = 1
    dodgeDelay = 0.9
    partDelay = 0.25
    partInterval = 1
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    partTracks = getPartTracks(attack, particleEffects, partDelay + partInterval * 0, 3, 0, softStop=-1)
    partTracks2 = getPartTracks(attack, particleEffects2, partDelay + partInterval * 1, 3, 0, softStop=-1)
    partTracks3 = getPartTracks(attack, particleEffects3, partDelay + partInterval * 2, 3, 0, softStop=-1)
    partTracks4 = getPartTracks(attack, particleEffects4, partDelay + partInterval * 3, 2.0, 0, softStop=-1)
    damageAnims = []
    damageAnims.append(['conked',
     0.0001,
     0,
     0.4])
    damageAnims.append(['conked',
     0.0001,
     0.7,
     0.85])
    damageAnims.append(['conked',
     0.0001,
     0.4,
     0.09])
    damageAnims.append(['conked',
     0.0001,
     0.4,
     0.09])
    damageAnims.append(['conked',
     0.0001,
     0.4,
     0.86])
    damageAnims.append(['conked', 0.0001, 0.4])
    dodgeAnims = [['duck', 0.0001, 1.2], ['duck', 0.0001, 1.3]]
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.6, showDamageExtraTime=0.7)
    soundTrack = getSoundTrack('SA_jargon.ogg', delay=1.5, node=suit)
    return Parallel(suitTrack, toonTracks, soundTrack, partTracks, partTracks2, partTracks3, partTracks4)

def doOverload(attack):
    suit = attack['suit']
    battle = attack['battle']
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect('DoubleTalkLeft')
    particleEffect2 = BattleParticles.createParticleEffect('DoubleTalkRight')
    BattleParticles.setEffectTexture(particleEffect, 'doubletalk-double', color=Vec4(0, 1.0, 0.0, 1))
    BattleParticles.setEffectTexture(particleEffect2, 'doubletalk-good', color=Vec4(0, 1.0, 0.0, 1))
    suitType = getSuitBodyType(attack['suitName'])
    partDelay = 2.25
    damageDelay = 2.0
    dodgeDelay = 2.25
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    partTrack = getPartTrack(particleEffect, partDelay, 2.5, [particleEffect, suit, 0], softStop=-1)
    partTrack2 = getPartTrack(particleEffect2, partDelay, 2.5, [particleEffect2, suit, 0], softStop=-1)
    damageAnims = [['duck',
      0.01,
      0.4,
      1.05], ['cringe', 1e-06, 0.8]]
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, splicedDodgeAnims=[['duck', 0.01, 1.4]], showMissedExtraTime=0.9, showDamageExtraTime=0.8)
    soundTrack = getSoundTrack('SA_doubletalk.ogg', delay=2, node=suit)
    return Parallel(suitTrack, toonTrack, partTrack, partTrack2, soundTrack)


def doMumboJumbo(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    toon = targets[0]['toon']
    dmg = targets[0]['hp']
    BattleParticles.loadParticles()
    particleEffects = []
    particleEffects2 = []
    for t in targets:
        particleEffect = BattleParticles.createParticleEffect(file='mumboJumboSpray')
        particleEffect2 = BattleParticles.createParticleEffect(file='mumboJumboSpray')
        BattleParticles.setEffectTexture(particleEffect, 'mumbojumbo-boiler', color=Vec4(1, 0, 0, 1))
        BattleParticles.setEffectTexture(particleEffect2, 'mumbojumbo-creative', color=Vec4(1, 0, 0, 1))
        particleEffects.append(particleEffect)
        particleEffects2.append(particleEffect2)

    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    partTracks = getPartTracks(attack, particleEffects, 1.5, 2, 0)
    partTracks2 = getPartTracks(attack, particleEffects2, 1.5, 2, 0)
    partTracks3 = Parallel()
    partTracks4 = Parallel()
    partTracks5 = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        particleEffect3 = BattleParticles.createParticleEffect(file='mumboJumboSmother')
        particleEffect4 = BattleParticles.createParticleEffect(file='mumboJumboSmother')
        particleEffect5 = BattleParticles.createParticleEffect(file='mumboJumboSmother')
        BattleParticles.setEffectTexture(particleEffect3, 'mumbojumbo-deben', color=Vec4(1, 0, 0, 1))
        BattleParticles.setEffectTexture(particleEffect4, 'mumbojumbo-high', color=Vec4(1, 0, 0, 1))
        BattleParticles.setEffectTexture(particleEffect5, 'mumbojumbo-iron', color=Vec4(1, 0, 0, 1))
        if dmg > 0:
            partTracks3.append(getPartTrack(particleEffect3, 1.5, 2.7, [particleEffect3, toon, 0], softStop=-1))
            partTracks4.append(getPartTrack(particleEffect4, 1.5, 2.7, [particleEffect4, toon, 0], softStop=-1))
            partTracks5.append(getPartTrack(particleEffect5, 1.5, 2.7, [particleEffect5, toon, 0], softStop=-1))

    toonTracks = getToonTracks(attack, 1.5, ['cringe'], 1.6, ['sidestep'])
    soundTrack = getSoundTrack('SA_mumbo_jumbo.ogg', delay=1.5, node=suit)
    return Parallel(suitTrack, toonTracks, soundTrack, partTracks, partTracks2, partTracks3, partTracks4, partTracks5)


def doGuiltTrip(attack):
    suit = attack['suit']
    battle = attack['battle']
    centerColor = Vec4(1.0, 0.2, 0.2, 0.9)
    edgeColor = Vec4(0.9, 0.9, 0.9, 0.4)
    powerBar1 = BattleParticles.createParticleEffect(file='guiltTrip')
    powerBar2 = BattleParticles.createParticleEffect(file='guiltTrip')
    powerBar1.setPos(0, 6.1, 0.4)
    powerBar1.setHpr(-90, 0, 0)
    powerBar2.setPos(0, 6.1, 0.4)
    powerBar2.setHpr(90, 0, 0)
    powerBar1.setScale(5)
    powerBar2.setScale(5)
    powerBar1Particles = powerBar1.getParticlesNamed('particles-1')
    powerBar2Particles = powerBar2.getParticlesNamed('particles-1')
    powerBar1Particles.renderer.setCenterColor(centerColor)
    powerBar1Particles.renderer.setEdgeColor(edgeColor)
    powerBar2Particles.renderer.setCenterColor(centerColor)
    powerBar2Particles.renderer.setEdgeColor(edgeColor)
    waterfallEffect = BattleParticles.createParticleEffect('Waterfall')
    waterfallEffect.setScale(11)
    waterfallParticles = waterfallEffect.getParticlesNamed('particles-1')
    waterfallParticles.renderer.setCenterColor(centerColor)
    waterfallParticles.renderer.setEdgeColor(edgeColor)
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))

    def getPowerTrack(effect, suit = suit, battle = battle):
        partTrack = Sequence(Wait(0.7), Func(battle.movie.needRestoreParticleEffect, effect), Func(effect.start, suit), Wait(0.4), LerpPosInterval(effect, 1.0, Point3(0, 25, 0.4)), LerpFunctionInterval(effect.setAlphaScale, fromData=1, toData=0, duration=0.4), Func(effect.cleanup), Func(battle.movie.clearRestoreParticleEffect, effect))
        return partTrack

    partTrack1 = getPowerTrack(powerBar1)
    partTrack2 = getPowerTrack(powerBar2)
    waterfallTrack = getPartTrack(waterfallEffect, 0.6, 1.6, [waterfallEffect, suit, 0], softStop=-1)
    toonTracks = getToonTracks(attack, 1.5, ['slip-forward'], 0.86, ['jump'])
    soundTrack = getSoundTrack('SA_guilt_trip.ogg', delay=1.1, node=suit)
    return Parallel(suitTrack, partTrack1, partTrack2, soundTrack, waterfallTrack, toonTracks)


def doRestrainingOrder(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    #for s in battle.activeSuits:
        #if s.dna.name == 'laa':
            #theSuit = s
        #suitTrack.append(Func(s.setPlayRate2, theSuit.getPlayRate2() + .5))
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        posPoints = [Point3(0.88, -2.21917, -0.22), VBase3(10, 250, -10)]
        scale = Point3(1.2, 1.2, 1.2)
    else:
        posPoints = [Point3(.78, -1.89, -.17), VBase3(10, 250, -10)]
        scale = Point3(1, 1, 1)
    propTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        paper = globalPropPool.getProp('shredder-paper')
        propTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.75, scale, scaleUpTime=0.25))
        propTrack.append(Wait(0.95))
        hitPoint = __toonFacePoint(toon, parent=battle)
        hitPoint.setX(hitPoint.getX() - 1.4)
        missPoint = __toonGroundPoint(attack, toon, 0.7, parent=battle)
        missPoint.setX(missPoint.getX() - 1.1)
        propTrack.append(getPropThrowTrack(attack, paper, [hitPoint], [missPoint], .25, parent=battle))
        explodePosPoints = [Point3(0, 0, 0), MovieUtil.PNT3_ZERO]
        splatName = 'dust'
        splat = globalPropPool.getProp('dust')
        explode = globalPropPool.getProp('dust')
        explode.setTwoSided(True)

        explode.setBillboardPointWorld(2)
        explodeTrack = Sequence()
        explodeTrack.append(
            getPropAppearTrack(explode, toon, explodePosPoints, 0, Point3(2, 2, 2), scaleUpTime=0))
        explodeTrack.append(Sequence(ActorInterval(explode, splatName), Func(explode.detachNode)))
        soundTrack = getSoundTrack('LB_evidence_miss.ogg', node=suit)
        propTrack.append(Parallel(explodeTrack, soundTrack))
        propTracks.append(propTrack)

    damageAnims = [['conked',
      0.01,
      0.3,
      0.2], ['struggle', 0.01, 0.2]]
    toonTracks = getToonTracks(attack, damageDelay=2.2, splicedDamageAnims=damageAnims, dodgeDelay=1.7, dodgeAnimNames=['sidestep'])
    return Parallel(suitTrack, toonTracks, propTracks)

def doBreakthrough(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = Sequence(ActorInterval(suit, 'finger-wag', endTime=1), Wait(1.0), getSuitTrack(attack, playRate=1.5))
    propTracks = Parallel()
    for t in targets:
        toon = t['toon']
        paper = loader.loadModel('phase_5/models/props/lightbulb')
        paper.find('**/Bulb_Coil').hide()
        cagePosition = Parallel(LerpPosInterval(paper, 0.25, Point3(-0.25, 0, -1.5)))
        posPoints = [Point3(0, 0, suit.height + 2), VBase3(0, 0, 0)]
        propTrack = Sequence(
            getPropAppearTrack(paper, suit, posPoints, 0.25, Point3(1.5, 1.5, 1.5), scaleUpTime=0.25))
        propTrack.append(Wait(1))
        propTrack.append(Func(paper.find('**/Bulb_Coil').show))
        propTrack.append(Wait(1))
        propTrack.append(Parallel(Func(paper.reparentTo, suit.getRightHand()), cagePosition))
        propTrack.append(Wait(1.25))
        hitPoint = __toonFacePoint(toon, parent=battle)
        hitPoint.setX(hitPoint.getX() - 1.4)
        missPoint = __toonGroundPoint(attack, toon, 0.7, parent=battle)
        missPoint.setX(missPoint.getX() - 1.1)
        propTrack.append(getPropThrowTrack(attack, paper, [hitPoint], [missPoint], .25, parent=battle, target=t))
        propTrack.append(Func(paper.removeNode))
        explodePosPoints = [Point3(0, 0, 0), MovieUtil.PNT3_ZERO]
        splatName = 'dust'
        splat = globalPropPool.getProp('dust')
        explode = globalPropPool.getProp('dust')
        explode.setTwoSided(True)
        explode.setBillboardPointWorld(2)
        explodeTrack = Sequence()
        explodeTrack.append(
            getPropAppearTrack(explode, toon, explodePosPoints, 0, Point3(2, 2, 2), scaleUpTime=0))
        explodeTrack.append(Sequence(ActorInterval(explode, splatName), Func(explode.detachNode)))
        soundTrack = getSoundTrack('LB_evidence_miss.ogg', node=suit)
        propTrack.append(Parallel(explodeTrack, soundTrack))
        propTracks.append(propTrack)

    damageAnims = [['conked',
      0.01,
      0.3,
      0.2], ['struggle', 0.01, 0.2]]
    toonTracks = getToonTracks(attack, damageDelay=4.25, splicedDamageAnims=damageAnims, dodgeDelay=3.5, dodgeAnimNames=['sidestep'])
    soundTrack2 = getSoundTrack('SA_breakthrough.ogg', delay=1.25, node=suit)
    return Parallel(suitTrack, toonTracks, propTracks, soundTrack2)

def doEncrypt(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    paper = globalPropPool.getProp('ttht_m_ene_fileFolder')
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    posPoints = [Point3(-0.4775687409551388, 0, -0.13024602026049337), VBase3(-90, 0, 90)]
    x = toon.getX(battle)
    y = toon.getY(battle)
    z = toon.getZ(battle)
    cagePosition = Parallel(
        LerpHprInterval(paper, 0.25, Point3(-90, 0, 0)),
        LerpScaleInterval(paper, 0.25, Point3(2, 2, 2)),
        LerpPosInterval(paper, 0.25, Point3(0, 3.5, 2))  # 3.5 units in front, 2 up
    )

    cagePosition2 = LerpPosInterval(
        paper,
        0.25,
        Point3(0, .5, 2)
    )
    propTrack = Sequence(
        Parallel(Func(paper.play, 'ttht_m_ene_fileFolder'), getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.5, Point3(1.5, 1.5, 1.5), scaleUpTime=0.25)),
                 Wait(1.25), Func(paper.wrtReparentTo, toon), cagePosition, Wait(1), cagePosition2)
    propTrack.append(Wait(0.25))
    hitPoint = __toonFacePoint(toon, parent=battle)
    hitPoint.setX(hitPoint.getX() - 1.4)
    missPoint = __toonGroundPoint(attack, toon, 0.7, parent=battle)
    missPoint.setX(missPoint.getX() - 1.1)
    #propTrack.append(getPropThrowTrack(attack, paper, [hitPoint], [missPoint], .5, parent=battle, lookAt=toon))
    explodePosPoints = [Point3(0, 0, 0), MovieUtil.PNT3_ZERO]
    splatName = 'dust'
    splat = globalPropPool.getProp('dust')
    explode = globalPropPool.getProp('dust')
    explode.setTwoSided(True)

    explode.setBillboardPointWorld(2)
    explodeTrack = Sequence()
    explodeTrack.append(
        getPropAppearTrack(explode, toon, explodePosPoints, 0, Point3(2, 2, 2), scaleUpTime=0))
    explodeTrack.append(Sequence(ActorInterval(explode, splatName), Func(explode.detachNode)))
    soundTrack = getSoundTrack('LB_evidence_miss.ogg', node=suit)
    propTrack.append(Parallel(explodeTrack, soundTrack, Func(MovieUtil.removeProp, paper), Func(battle.movie.clearRenderProp, paper)))
    damageAnims = [['struggle', 0.01, 0.2]]
    toonTrack = getToonTrack(attack, damageDelay=3.85, splicedDamageAnims=damageAnims, dodgeDelay=3, dodgeAnimNames=['sidestep'])
    return Parallel(suitTrack, toonTrack, propTrack)


def doSpin(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.7
    sprayEffects = [BattleParticles.createParticleEffect(file='spinSpray') for t in targets]
    suitTrack = Sequence(getSuitTrack(attack))
    sprayTracks = getPartTracks(attack, sprayEffects, 1.0, 3.9, 0, softStop=-2)
    spinTracks1 = Parallel()
    spinTracks2 = Parallel()
    spinTracks3 = Parallel()
    damageAnims = []
    damageAnims.append(['duck',
     0.01,
     0.01,
     1.1])
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.91, dodgeAnimNames=['sidestep'], showDamageExtraTime=2.1, showMissedExtraTime=1.0)
    soundTracks = Parallel()
    toonSpinTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        spinEffect1 = BattleParticles.createParticleEffect(file='spinEffect')
        spinEffect2 = BattleParticles.createParticleEffect(file='spinEffect')
        spinEffect3 = BattleParticles.createParticleEffect(file='spinEffect')
        spinEffect1.reparentTo(toon)
        spinEffect2.reparentTo(toon)
        spinEffect3.reparentTo(toon)
        height1 = toon.getHeight() * (random.random() * 0.2 + 0.7)
        height2 = toon.getHeight() * (random.random() * 0.2 + 0.4)
        height3 = toon.getHeight() * (random.random() * 0.2 + 0.1)
        spinEffect1.setPos(0.8, -0.7, height1)
        spinEffect1.setHpr(0, 0, -random.random() * 10 - 85)
        spinEffect1.setHpr(spinEffect1, 0, 50, 0)
        spinEffect2.setPos(0.8, -0.7, height2)
        spinEffect2.setHpr(0, 0, -random.random() * 10 - 85)
        spinEffect2.setHpr(spinEffect2, 0, 50, 0)
        spinEffect3.setPos(0.8, -0.7, height3)
        spinEffect3.setHpr(0, 0, -random.random() * 10 - 85)
        spinEffect3.setHpr(spinEffect3, 0, 50, 0)
        spinEffect1.wrtReparentTo(battle)
        spinEffect2.wrtReparentTo(battle)
        spinEffect3.wrtReparentTo(battle)
        if dmg > 0:
            spinTracks1.append(getPartTrack(spinEffect1, 1.5, 5.9, [spinEffect1, battle, 0], softStop=-2))
            spinTracks2.append(getPartTrack(spinEffect2, 1.5, 5.9, [spinEffect2, battle, 0], softStop=-2))
            spinTracks3.append(getPartTrack(spinEffect3, 1.5, 5.9, [spinEffect3, battle, 0], softStop=-2))
            soundTracks.append(getSoundTrack('tt_s_ara_cfg_toonInWhirlwind.ogg', delay=2.0, node=suit))
            toonSpinTracks.append(Sequence(Wait(damageDelay + 0.9), LerpHprInterval(toon, 0.7, Point3(-10, 0, 0)), LerpHprInterval(toon, 0.5, Point3(-30, 0, 0)), LerpHprInterval(toon, 0.2, Point3(-60, 0, 0)), LerpHprInterval(toon, 0.7, Point3(-700, 0, 0)), LerpHprInterval(toon, 1.0, Point3(-1310, 0, 0)), LerpHprInterval(toon, 0.4, toon.getHpr()), Wait(0.5)))

    return Parallel(suitTrack, sprayTracks, toonTracks, toonSpinTracks, spinTracks1, spinTracks2, spinTracks3, soundTracks)


def doLegalese(attack):
    suit = attack['suit']
    BattleParticles.loadParticles()
    sprayEffects1 = []
    sprayEffects2 = []
    sprayEffects3 = []
    for t in attack['target']:
        sprayEffect1 = BattleParticles.createParticleEffect(file='legaleseSpray')
        sprayEffect2 = BattleParticles.createParticleEffect(file='legaleseSpray')
        sprayEffect3 = BattleParticles.createParticleEffect(file='legaleseSpray')
        color = Vec4(0.4, 0, 0, 1)
        BattleParticles.setEffectTexture(sprayEffect1, 'legalese-hc', color=color)
        BattleParticles.setEffectTexture(sprayEffect2, 'legalese-qpq', color=color)
        BattleParticles.setEffectTexture(sprayEffect3, 'legalese-vd', color=color)
        sprayEffects1.append(sprayEffect1)
        sprayEffects2.append(sprayEffect2)
        sprayEffects3.append(sprayEffect3)

    partDelay = 0.5
    partDuration = 1.75
    damageDelay = 1
    dodgeDelay = 0.8
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    sprayTracks1 = getPartTracks(attack, sprayEffects1, partDelay, partDuration, 0, softStop=-.5)
    sprayTracks2 = getPartTracks(attack, sprayEffects2, partDelay + 0.8, partDuration, 0, softStop=-.5)
    sprayTracks3 = getPartTracks(attack, sprayEffects3, partDelay + 1.6, partDuration, 0, softStop=-.5)
    damageAnims = []
    damageAnims.append(['cringe',
     1e-05,
     0.3,
     0.8])
    damageAnims.append(['cringe',
     1e-05,
     0.3,
     0.8])
    damageAnims.append(['cringe', 1e-05, 0.3])
    soundTrack = getSoundTrack('SA_jargon.ogg', delay=1, node=suit)
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'], showMissedExtraTime=0.8)
    return Parallel(suitTrack, toonTracks, soundTrack, sprayTracks1, sprayTracks2, sprayTracks3)


def doPeckingOrder(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    throwDuration = 3.03
    throwDelay = 2
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    numBirds = random.randint(10, 20)
    birdTracks = Parallel()
    propDelay = 1.5
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        for i in xrange(0, numBirds):
            next = globalPropPool.getProp('bird')
            #next.setScale(0.01)
            #next.reparentTo(suit.getRightHand())
          #  next.setPos(random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3)
            toonPos = toon.getPos(battle)

            if dmg > 0:
                hitPoint = Point3(
                    toonPos[0] + (random.random() * 1.5 - 0.75),
                    toonPos[1] + (random.random() * 1.0 - 0.5),
                    toonPos[2] + toon.getHeight() * 0.5 + (random.random() * 1.0 - 0.5)
                )
            else:
                hitPoint = Point3(
                    toonPos[0] + (random.random() * 3.0 - 1.5),
                    toonPos[1] - 3.0 + (random.random() * 2.0 - 1.0),
                    toonPos[2] + toon.getHeight() * 0.5 + (random.random() * 2.0 - 1.0)
                )
            birdTrack = Sequence(Wait(throwDelay), Func(next.setScale, 0.01), Func(next.reparentTo, suit.getRightHand()),
                                 Func(next.setPos, random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3), Func(battle.movie.needRestoreRenderProp, next),
                                 Func(next.wrtReparentTo, battle), Func(next.setHpr, Point3(90, 20, 0)),
                                 LerpPosInterval(next, 0.5, hitPoint))
            scaleTrack = Sequence(Wait(throwDelay), LerpScaleInterval(next, 0.5, Point3(9, 9, 9)), LerpScaleInterval(next, .5, Point3(0, 0, 0)))
            birdTracks.append(Sequence(Parallel(birdTrack, scaleTrack), Func(MovieUtil.removeProp, next)))
    damageAnims = []
    damageAnims.append(['cringe',
                        0.01,
                        0.14,
                        0.21])
    damageAnims.append(['cringe',
                        0.01,
                        0.14,
                        0.13])
    damageAnims.append(['cringe', 0.01, 0.43])
    toonTrack = getToonTracks(attack, damageDelay=2.5, splicedDamageAnims=damageAnims, dodgeDelay=0.75,
                              dodgeAnimNames=['duck'], showMissedExtraTime=1.1)
    soundTrack = getSoundTrack('tt_s_ara_cfg_eagleCry.ogg', delay=2, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, birdTracks)
