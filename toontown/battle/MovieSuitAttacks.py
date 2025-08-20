from toontown.battle import MovieCamera
from toontown.battle import MovieLawbotLitigationCheats
from toontown.battle import MovieBossbotLitigationCheats
from toontown.battle import MovieSellbotLitigationCheats
from toontown.battle import MovieHighRollerCheats
from toontown.battle import MovieDirectorsCheats
from toontown.battle import MovieUniversalCheats
from toontown.battle import MovieUtil
from toontown.battle import BattleParticles
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from toontown.effects import DustCloud
from direct.particles import ParticleEffect
from toontown.battle.BattleBase import *
from toontown.battle.BattleBase import *
import PlayByPlayText
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

def __doDamage(toon, dmg, died):
    if dmg > 0 and toon.hp != None:
        toon.takeDamage(dmg)

def __doDamageCheat(toon, dmg, died):
    if dmg > 0 and toon.hp != None:
        toon.takeDamageCheat(dmg)

def __showProp(prop, parent, pos, hpr = None, scale = None):
    prop.reparentTo(parent)
    prop.setPos(pos)
    if hpr:
        prop.setHpr(hpr)
    if scale:
        prop.setScale(scale)

def __animProp(prop, propName, propType = 'actor'):
    if 'actor' == propType:
        prop.play(propName)
    elif 'model' == propType:
        pass
    else:
        self.notify.error('No such propType as: %s' % propType)

def __suitFacePoint(suit, zOffset = 0):
    pnt = suit.getPos()
    pnt.setZ(pnt[2] + suit.shoulderHeight + 0.3 + zOffset)
    return Point3(pnt)


def __toonFacePoint(toon, zOffset = 0, parent = render):
    pnt = toon.getPos(parent)
    pnt.setZ(pnt[2] + toon.shoulderHeight + 0.3 + zOffset)
    return Point3(pnt)


def __toonTorsoPoint(toon, zOffset = 0):
    pnt = toon.getPos()
    pnt.setZ(pnt[2] + toon.shoulderHeight - 0.2)
    return Point3(pnt)


def __toonGroundPoint(attack, toon, zOffset = 0, parent = render):
    pnt = toon.getPos(parent)
    battle = attack['battle']
    pnt.setZ(battle.getZ(parent) + zOffset)
    return Point3(pnt)


def __toonGroundMissPoint(attack, prop, toon, zOffset = 0):
    point = __toonMissPoint(prop, toon)
    battle = attack['battle']
    point.setZ(battle.getZ() + zOffset)
    return Point3(point)


def __toonMissPoint(prop, toon, yOffset = 0, parent = None):
    if parent:
        p = __toonFacePoint(toon) - prop.getPos(parent)
    else:
        p = __toonFacePoint(toon) - prop.getPos()
    v = Vec3(p)
    baseDistance = v.length()
    v.normalize()
    if parent:
        endPos = prop.getPos(parent) + v * (baseDistance + 5 + yOffset)
    else:
        endPos = prop.getPos() + v * (baseDistance + 5 + yOffset)
    return Point3(endPos)


def __toonMissBehindPoint(toon, parent = render, offset = 0):
    point = toon.getPos(parent)
    point.setY(point.getY() - 5 + offset)
    return point


def __throwBounceHitPoint(prop, toon):
    startPoint = prop.getPos()
    endPoint = __toonFacePoint(toon)
    return __throwBouncePoint(startPoint, endPoint)


def __throwBounceMissPoint(prop, toon):
    startPoint = prop.getPos()
    endPoint = __toonFacePoint(toon)
    return __throwBouncePoint(startPoint, endPoint)


def __throwBouncePoint(startPoint, endPoint):
    midPoint = startPoint + (endPoint - startPoint) / 2.0
    midPoint.setZ(0)
    return Point3(midPoint)


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
        suitTrack = doFountainPenBindings(attack)
    elif name == 'HostileTakeover':
        suitTrack = doHostileTakeoverNew(attack)
    elif name == 'NickelAndDime':
        suitTrack = doNickelAndDime(attack)
    elif name == 'Quash':
        suitTrack = doAceInTheHoleNew(attack)
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
        suitTrack = doBounceRate(attack)
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
        suitTrack = doFingerWag(attack)
    elif name == 'Fired':
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
        suitTrack = doTremor(attack)
    elif name == 'Withdrawal':
        suitTrack = doWithdrawal(attack)
    elif name == 'WriteOff':
        suitTrack = doWriteOff(attack)
        #redd heir-wing cheats
    elif name == 'ReddAutoRepair':
        suitTrack = MovieLawbotLitigationCheats.doAutoRepair(attack)
    elif name == 'ReddLiquidationSale':
        suitTrack = doLiquidate(attack)
    elif name == 'ReddPeckingOrder':
        suitTrack = MovieLawbotLitigationCheats.doPeckingOrder(attack)
        # wsi cheats
    elif name == 'WSICeaseAndDesist':
        suitTrack = MovieLawbotLitigationCheats.doCeaseAndDesist(attack)
    elif name == 'WSIJuryNotice':
        suitTrack = MovieLawbotLitigationCheats.doJuryNotice(attack)
    #litigator cheats
    elif name == 'LitigatorSnapSoak':
        suitTrack = MovieLawbotLitigationCheats.doSnap(attack, suit)
    elif name == 'LitigatorSnap':
        suitTrack = MovieLawbotLitigationCheats.doSnap(attack, suit)
    elif name == 'LitigatorBayouBash':
        suitTrack = MovieLawbotLitigationCheats.doBayouBash(attack)
    elif name == 'LitigatorBayouBellow':
        suitTrack = MovieLawbotLitigationCheats.doBayouBellow(attack)
    #stenographer cheats
    elif name == 'StenographerSanctionBindings':
        suitTrack = MovieLawbotLitigationCheats.doCourtSanctionBindings(attack)
    elif name == 'StenographerSanction':
        suitTrack = MovieLawbotLitigationCheats.doCourtSanction(attack)
    elif name == 'StenographerCourtRecordBan':
        suitTrack = MovieLawbotLitigationCheats.doGavelCourtRecord(attack)
    #case manager cheats
    elif name == 'CaseManagerInsurancePlan':
        if not suit.isSkeleton:
            suitTrack = MovieLawbotLitigationCheats.doCaseInsurancePlanInsurance(attack)
        else:
            suitTrack = MovieLawbotLitigationCheats.doCaseInsurancePlanSkelecogInsurance(attack)
    elif name == 'CaseManagerInsurance':
        suitTrack = MovieLawbotLitigationCheats.doCaseInsurance(attack)
    elif name == 'CaseManagerLegalBindings':
        suitTrack = MovieLawbotLitigationCheats.doLegalBindings(attack)
    elif name == 'CaseManagerLegallyBound':
        suitTrack = MovieLawbotLitigationCheats.doLegallyBound(attack)
    elif name == 'CaseManagerCourtRecordBan':
        suitTrack = MovieLawbotLitigationCheats.doGavelCourtRecord(attack)
    #scapegoat cheats
    elif name == 'ScapegoatShieldsUp':
        suitTrack = MovieLawbotLitigationCheats.doShieldsUp(attack)
    elif name == 'ScapegoatEnraged':
        suitTrack = MovieLawbotLitigationCheats.doEnraged(attack)
    elif name == 'ScapegoatGavel':
        suitTrack = MovieLawbotLitigationCheats.doGavel(attack)
    elif name == 'ScapegoatBarnyardBash':
        suitTrack = MovieLawbotLitigationCheats.doBarnyardBash(attack)
    elif name == 'ScapegoatCourtRecordBan':
        suitTrack = MovieLawbotLitigationCheats.doGavelCourtRecord(attack)
    #powerhouse cheats
    elif name == 'PowerhouseAbsorb':
        suitTrack = MovieBossbotLitigationCheats.doAbsorb(attack)
    elif name == 'PowerhouseSoakImmune':
        suitTrack = MovieBossbotLitigationCheats.doSoakImmune(attack)
    elif name == 'PowerhouseLureImmune':
        suitTrack = MovieBossbotLitigationCheats.doLureImmune(attack)
    elif name == 'PowerhouseSyphon':
        suitTrack = MovieBossbotLitigationCheats.doSyphon(attack)
    elif name == 'PowerhouseSyphonDesperation':
        suitTrack = MovieBossbotLitigationCheats.doSyphonDesperation(attack)
    elif name == 'PowerhouseSnipeVulnerable':
        suitTrack = MovieBossbotLitigationCheats.doSnipe(attack)
    elif name == 'PowerhouseSnipeGagBan':
        suitTrack = MovieBossbotLitigationCheats.doSnipe(attack)
    elif name == 'PowerhouseSnipeSoaked':
        suitTrack = MovieBossbotLitigationCheats.doSnipe(attack)
    elif name == 'PowerhouseSnipeBookkept':
        suitTrack = MovieBossbotLitigationCheats.doSnipe(attack)
    elif name == 'PowerhouseSnipeMulligan':
        suitTrack = MovieBossbotLitigationCheats.doSnipe(attack)
    elif name == 'PowerhouseSnipeCollectCall':
        suitTrack = MovieBossbotLitigationCheats.doSnipe(attack)
    #bookkeeper cheats
    elif name == 'BookkeeperPaperCutSoaked':
        suitTrack = MovieBossbotLitigationCheats.doPaperCut(attack)
    elif name == 'BookkeeperPaperCutMarked':
        suitTrack = MovieBossbotLitigationCheats.doPaperCut(attack)
    elif name == 'BookkeeperPaperCut':
        suitTrack = MovieBossbotLitigationCheats.doPaperCut(attack)
    elif name == 'BookkeeperExplodingDocument':
        suitTrack = MovieBossbotLitigationCheats.doExplodingDocument(attack)
    elif name == 'BookkeeperBookkeepingRetaliation':
        suitTrack = MovieBossbotLitigationCheats.doBookkeepingRetaliation(attack)
    elif name == 'BookkeeperBookkeeping':
        suitTrack = MovieBossbotLitigationCheats.doBookkeeping(attack)
    #wiretapper cheats
    elif name == 'WiretapperCollectCall':
        suitTrack = MovieBossbotLitigationCheats.doCollectCall(attack)
    elif name == 'WiretapperCollectCallDamage':
        suitTrack = MovieBossbotLitigationCheats.doCollectCallDamage(attack)
    elif name == 'WiretapperWiretapped':
        suitTrack = MovieBossbotLitigationCheats.doWiretapped(attack)
    elif name == 'WiretapperVoicemail':
        suitTrack = MovieBossbotLitigationCheats.doVoicemail(attack)
    elif name == 'WiretapperBrokenConnection':
        suitTrack = MovieBossbotLitigationCheats.doBrokenConnection(attack)
    elif name == 'WiretapperGagBan':
        suitTrack = MovieBossbotLitigationCheats.doWiretapperGagBan(attack)
    #ambassador cheats
    elif name == 'AmbassadorHeadRoller':
        suitTrack = MovieBossbotLitigationCheats.doHeadRoller(attack, 2)
    elif name == 'AmbassadorHeadRollerGroup':
        suitTrack = MovieBossbotLitigationCheats.doHeadRollerGroup(attack)
    elif name == 'AmbassadorRefinement':
        suitTrack = MovieBossbotLitigationCheats.doRefinement(attack)
    elif name == 'AmbassadorRefinementManager':
        suitTrack = MovieBossbotLitigationCheats.doRefinementManager(attack)
    elif name == 'AmbassadorPhase2':
        suitTrack = MovieBossbotLitigationCheats.doAmbassadorPhase2(attack)
    elif name == 'AmbassadorDamageUp':
        suitTrack = MovieBossbotLitigationCheats.doAmbassadorDamageUp(attack)
    elif name == 'AmbassadorManagerialProtection':
        suitTrack = MovieBossbotLitigationCheats.doManagerialProtection(attack)
    elif name == 'AmbassadorManagerialProtectionImmunity':
        suitTrack = MovieBossbotLitigationCheats.doManagerialProtectionImmunity(attack)
    elif name == 'AmbassadorMulligan':
        suitTrack = MovieBossbotLitigationCheats.doMulligan(attack)
    elif name == 'AmbassadorGhostMentality':
        suitTrack = MovieBossbotLitigationCheats.doGhostMentality(attack)
        # safety supervisor
    elif name == 'SafetyHighPressure':
        suitTrack = MovieSellbotLitigationCheats.doHighPressure(attack)
    elif name == 'SafetyHeatWave':
        suitTrack = MovieSellbotLitigationCheats.doHeatWave(attack)
    elif name == 'SafetyHeatWaveCalculation':
        suitTrack = MovieSellbotLitigationCheats.doHeatWaveCalculation(attack)
    elif name == 'SafetyViolation':
        suitTrack = MovieSellbotLitigationCheats.doViolation(attack)
    elif name == 'SafetyPromotion':
        suitTrack = MovieSellbotLitigationCheats.doPromotion(attack, 1)
    elif name == 'SafetyPromotion2':
        suitTrack = MovieSellbotLitigationCheats.doPromotion(attack, 2)
    elif name == 'SafetyPromotion3':
        suitTrack = MovieSellbotLitigationCheats.doPromotion(attack, 3)
    elif name == 'SafetyPromotion4':
        suitTrack = MovieSellbotLitigationCheats.doPromotion(attack, 4)
    elif name == 'SafetyPromotion5':
        suitTrack = MovieSellbotLitigationCheats.doPromotion(attack, 5)
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
    elif name == 'UnionBusterUnionWages':
        suitTrack = MovieSellbotLitigationCheats.doUnionWages(attack)
    elif name == 'UnionBusterBreachOfContract':
        suitTrack = MovieSellbotLitigationCheats.doBreachOfContract(attack)
    elif name == 'UnionBusterBreachOfContract2':
        suitTrack = MovieSellbotLitigationCheats.doBreachOfContractGroup(attack)
    elif name == 'UnionBusterBreachOfContract3':
        suitTrack = MovieSellbotLitigationCheats.doBreachOfContractGroup(attack)
    elif name == 'UnionBusterBreachOfContract4':
        suitTrack = MovieSellbotLitigationCheats.doBreachOfContractGroup(attack)
    elif name == 'UnionBusterContractEnforcement':
        suitTrack = MovieSellbotLitigationCheats.doContractEnforcement(attack)
        # racketeer
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
        suitTrack = MovieSellbotLitigationCheats.doExtortion2(attack)
    elif name == 'RacketeerCompensation':
        suitTrack = MovieSellbotLitigationCheats.doCompensation(attack)
    elif name == 'RacketeerHustling':
        suitTrack = MovieSellbotLitigationCheats.doHustling(attack)
    elif name == 'RacketeerRacketeering':
        suitTrack = MovieSellbotLitigationCheats.doRacketeering(attack)
    elif name == 'RacketeerPeckingOrderRetaliation':
        suitTrack = MovieSellbotLitigationCheats.doPeckingOrderGroup(attack)
    elif name == 'RacketeerPeckingOrderRetaliationSoak':
        suitTrack = doPeckingOrder(attack)
        # radiographer
    elif name == 'RadiographerRadioInfrequency':
        suitTrack = MovieSellbotLitigationCheats.doRadioInfrequency(attack)
    elif name == 'RadiographerHotTake':
        suitTrack = MovieSellbotLitigationCheats.doHotTake(attack)
    elif name == 'RadiographerHotTakeRetaliation':
        suitTrack = MovieSellbotLitigationCheats.doHotTake(attack)
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
        suitTrack = MovieSellbotLitigationCheats.doDanceSession(attack)
        # high roller phase 1
    elif name == 'HighRollerNoAttack':
        suitTrack = MovieHighRollerCheats.doNoAttack(attack)
    elif name == 'HighRollerWheelSpin':
        suitTrack = MovieHighRollerCheats.doWheelSpin(attack)
    elif name == 'HighRollerPuzzle':
        suitTrack = MovieHighRollerCheats.doPuzzle(attack)
    elif name == 'HighRollerPuzzleBan':
        suitTrack = MovieHighRollerCheats.doPuzzleBan(attack)
    elif name == 'HighRollerGameOver':
        suitTrack = MovieHighRollerCheats.doGameOver(attack)
    elif name == 'HighRollerCommercialBreak':
        suitTrack = MovieHighRollerCheats.doCommercialBreak(attack)
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
        suitTrack = MovieHighRollerCheats.doRaisingTheAnte(attack)
    # high roller silhouette cheats
    elif name == 'HighRollerDonation':
        suitTrack = MovieHighRollerCheats.doDonation(attack)
    elif name == 'HighRollerSyphon':
        suitTrack = MovieHighRollerCheats.doSyphon(attack)
    elif name == 'HighRollerBar':
        suitTrack = MovieHighRollerCheats.doBar(attack)
    elif name == 'HighRollerSingingBlues':
        suitTrack = MovieHighRollerCheats.doSingingBlues(attack)
    elif name == 'HighRollerDamageReduction':
        suitTrack = MovieHighRollerCheats.doDamageReduction(attack)
    elif name == 'HighRollerSplashback':
        suitTrack = MovieHighRollerCheats.doSplashback(attack)
    elif name == 'HighRollerCheerRetaliation':
        suitTrack = MovieHighRollerCheats.doSnipe(attack)
    #videographer cheats
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
    #filmmaker cheats
    elif name == 'FilmmakerCameraFlash':
        suitTrack = MovieHighRollerCheats.doCameraFlash(attack)
    elif name == 'FilmmakerCameraRewind':
        suitTrack = MovieHighRollerCheats.doCameraRewind(attack)
    elif name == 'FilmmakerBudgetCuts':
        suitTrack = MovieHighRollerCheats.doBudgetCuts(attack)
    #director cheats
    elif name == 'DirectorCut':
        suitTrack = MovieHighRollerCheats.doCut(attack)
    elif name == 'DirectorAction':
        suitTrack = MovieHighRollerCheats.doAction(attack)
    elif name == 'DirectorActionRetaliation':
        suitTrack = MovieHighRollerCheats.doSnipe(attack)
    elif name == 'DirectorBackToOnes':
        suitTrack = MovieHighRollerCheats.doBackToOnes(attack)
    #universal cheats
    elif name == 'TargetCheck':
        suitTrack = MovieHighRollerCheats.doNoAttack(attack)
    elif name == 'Desperation':
        suitTrack = MovieUniversalCheats.doDesperation(attack)
    elif name == 'SynergyFees':
        suitTrack = MovieUniversalCheats.doSynergy(attack)
    elif name == 'CalculatingFees':
        suitTrack = MovieUniversalCheats.doCourtCalculations(attack)
    elif name == 'DeathCheck':
        suitTrack = MovieUniversalCheats.doDeathCheck(attack)
    elif name == 'SoakRemoval':
        suitTrack = MovieUniversalCheats.doSoakRemoval(attack)
    elif name == 'SueApplication':
        suitTrack = MovieUniversalCheats.doSueApplication(attack)
    elif name == 'SueRemoval':
        suitTrack = MovieUniversalCheats.doSueRemoval(attack)
    elif name == 'BanLevel4':
        if suit.dna.name == 'wtapper':
            suitTrack = MovieBossbotLitigationCheats.doBudgetCuts(attack)
        else:
            suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanLevel5':
        if suit.dna.name == 'wtapper':
            suitTrack = MovieBossbotLitigationCheats.doBudgetCuts(attack)
        else:
            suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanLevel6':
        if suit.dna.name == 'wtapper':
            suitTrack = MovieBossbotLitigationCheats.doBudgetCuts(attack)
        else:
            suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanLevel7':
        if suit.dna.name == 'wtapper':
            suitTrack = MovieBossbotLitigationCheats.doBudgetCuts(attack)
        else:
            suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanLevel8':
        if suit.dna.name == 'wtapper':
            suitTrack = MovieBossbotLitigationCheats.doBudgetCuts(attack)
        else:
            suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanLevel45':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanLevel46':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanLevel47':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanLevel48':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanLevel56':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanLevel57':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanLevel58':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanLevel67':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanLevel68':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanLevel78':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanToonup':
        if suit.dna.name == 'wtapper':
            suitTrack = MovieBossbotLitigationCheats.doBudgetCuts(attack)
        else:
            suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanTrap':
        if suit.dna.name == 'wtapper':
            suitTrack = MovieBossbotLitigationCheats.doBudgetCuts(attack)
        else:
            suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanLure':
        if suit.dna.name == 'wtapper':
            suitTrack = MovieBossbotLitigationCheats.doBudgetCuts(attack)
        else:
            suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanThrow':
        if suit.dna.name == 'wtapper':
            suitTrack = MovieBossbotLitigationCheats.doBudgetCuts(attack)
        else:
            suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanSquirt':
        if suit.dna.name == 'wtapper':
            suitTrack = MovieBossbotLitigationCheats.doBudgetCuts(attack)
        else:
            suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanZap':
        if suit.dna.name == 'wtapper':
            suitTrack = MovieBossbotLitigationCheats.doBudgetCuts(attack)
        else:
            suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanSound':
        if suit.dna.name == 'wtapper':
            suitTrack = MovieBossbotLitigationCheats.doBudgetCuts(attack)
        else:
            suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanDrop':
        if suit.dna.name == 'wtapper':
            suitTrack = MovieBossbotLitigationCheats.doBudgetCuts(attack)
        else:
            suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanToonupTrap':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanToonupLure':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanToonupThrow':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanToonupSquirt':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanToonupZap':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanToonupSound':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanToonupDrop':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanTrapLure':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanTrapThrow':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanTrapSquirt':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanTrapZap':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanTrapSound':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanTrapDrop':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanLureThrow':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanLureSquirt':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanLureZap':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanLureSound':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanLureDrop':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanThrowSquirt':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanThrowZap':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanThrowSound':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanThrowDrop':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanSquirtZap':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanSquirtSound':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanSquirtDrop':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanZapSound':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanZapDrop':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    elif name == 'BanSoundDrop':
        suitTrack = MovieUniversalCheats.doCourtRecord(attack)
    else:
        notify.warning('unknown attack: %s substituting Finger Wag' % name)
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
        neutralIval =  Func(suit.setNeutralAnimation)
        preWalkTrack = Func(suit.setNeutralAnimation)
        unlureSuit = Parallel(Func(suit.makeUnLured), Func(battle.unlureSuit, suit))
        checkLuredCog = Func(suit.checkCogLured, battle)
        unlureSuit = Func(suit.makeUnLured)
        suitTrack = Sequence(preWalkTrack, suitTrack, neutralIval, toonHprTrack)
        suitPos = suit.getPos(battle)
        resetPos, resetHpr = battle.getActorPosHpr(suit)
        resetTrack = getResetTrack(suit, battle)
        if name == 'ScapegoatCourtRecordBan':
            resetSuitTrack = Sequence(suitTrack)
        elif name == 'CaseManagerCourtRecordBan':
            resetSuitTrack = Sequence(suitTrack)
        elif name == 'StenographerCourtRecordBan':
            resetSuitTrack = Sequence(suitTrack)
        elif name == 'CaseManagerLegallyBound':
            resetSuitTrack = Sequence(suitTrack)
        elif name == 'CaseManagerInsurance':
            resetSuitTrack = Sequence(suitTrack)
        elif name == 'CalculatingFees':
            resetSuitTrack = Sequence(suitTrack)
        elif name == 'ScapegoatCourtRecordBan':
            resetSuitTrack = Sequence(suitTrack)
        elif name == 'HighRollerNoAttack':
            resetSuitTrack = Sequence(suitTrack, unlureSuit)
        elif name == 'SoakRemoval':
            resetSuitTrack = Sequence(suitTrack)
        elif name == 'SueApplication':
            resetSuitTrack = Sequence(suitTrack)
        elif name == 'SueRemoval':
            resetSuitTrack = Sequence(suitTrack)
        elif name == 'UnionBusterUnionBusterDamage':
            resetSuitTrack = Sequence(suitTrack)
        elif name == 'SafetyHeatWaveCalculation':
            resetSuitTrack = Sequence(suitTrack)
        elif name == 'SafetyViolation':
            resetSuitTrack = Sequence(suitTrack)
        elif name == 'UnionBusterUnionCalculator':
            resetSuitTrack = Sequence(suitTrack)
        elif name == 'WiretapperCollectCallDamage':
            resetSuitTrack = Sequence(suitTrack)
        elif name == 'WiretapperGagBan':
            resetSuitTrack = Sequence(suitTrack)
        elif name == 'PowerhouseSnipeVulnerable':
            resetSuitTrack = Sequence(suitTrack)
        elif name == 'PowerhouseSnipeGagBan':
            resetSuitTrack = Sequence(suitTrack)
        elif name == 'PowerhouseSnipeBookkept':
            resetSuitTrack = Sequence(suitTrack)
        elif name == 'PowerhouseSnipeSoaked':
            resetSuitTrack = Sequence(suitTrack)
        elif name == 'PowerhouseSnipeCollectCall':
            resetSuitTrack = Sequence(suitTrack)
        elif name == 'PowerhouseSnipeMulligan':
            resetSuitTrack = Sequence(suitTrack)
        else:
            resetSuitTrack = Sequence(unlureSuit, resetTrack, suitTrack)
        waitTrack = Sequence(Func(battle.unlureSuit, suit))
        resetCamTrack = Sequence(waitTrack, camTrack)
    else:
        resetSuitTrack = Sequence(suitTrack, toonHprTrack) # Make sure we play the movie and, if necessary, reset the Toon's position.
    return (resetSuitTrack, camTrack)


def getResetTrack(suit, battle):
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    moveDist = Vec3(suit.getPos(battle) - resetPos).length()
    moveDuration = 0
    unluredTrack = Func(battle.unlureSuit, suit)
    unSuedTrack = Func(battle.unSueSuit, suit)
    walkTrack = Sequence(Func(suit.setHpr, battle, resetHpr), Func(suit.setNeutralAnimation))
    moveTrack = LerpPosInterval(suit, moveDuration, resetPos, other=battle)
    return Parallel(unluredTrack, unSuedTrack, walkTrack, moveTrack)


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
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    moveDist = Vec3(suit.getPos(battle) - resetPos).length()
    moveDuration = 0.5
    neutralTrack =  Func(suit.setNeutralAnimation())
    unluredTrack = Func(battle.unlureSuit, suit)
    updateTrack = Func(battle.unSueSuit, suit)
    walkTrack = Sequence(Func(suit.setHpr, battle, resetHpr), ActorInterval(suit, 'walk', startTime=1, duration=moveDuration, endTime=0.0001), neutralTrack)
    moveTrack = LerpPosInterval(suit, moveDuration, resetPos, other=battle)
    return Parallel(unluredTrack, updateTrack, walkTrack, moveTrack)


def getSuitTrack(attack, delay = 1e-06, splicedAnims = None, playRate = 1.0):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    target = attack['target']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    trapStorage = {}
    trapStorage['trap'] = None
    track = Sequence(Wait(delay))
    unsueTrack = Func(battle.unSueSuit, suit)
    for s in battle.activeSuits:
        if s.dna.name == 'psetter':
            theSuit = s
            track.append(Func(s.setPlayRate2, theSuit.getPlayRate2() + .25))
    if attack[
        'suitName'] == 'nothing':  # It isn't just 'caseman', it really all depends on the shorthand you have for the Case Manager.  If it is not 'caseman', change it to whatever is the actual shorthand for the Case Manager, or the Case Manager will not grunt as intended.
        track.append(Func(suit.setChatAbsolute, random.choice(['Hrm...', 'Hmph...', 'Hm, hm...', 'Hrnhmpf...']),
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'hho' and attack['name'] == 'CigarSmoke':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    else:
        track.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))

    def reparentTrap(suit = suit, battle = battle, trapStorage = trapStorage):
        return

    track.append(Func(reparentTrap))
    track.append(Func(suit.headsUp, battle, targetPos))
    if splicedAnims:
        track.append(getSplicedAnimsTrack(splicedAnims, actor=suit))
    else:
        if attack['suitName'] == 'hho' and attack['name'] == 'CigarSmoke':
            track.append(ActorInterval(suit, 'headhoncho-cigar-smoke', playRate=playRate))
        else:
            track.append(ActorInterval(suit, attack['animName'], playRate=playRate))
    origPos, origHpr = battle.getActorPosHpr(suit)
    track.append(Func(suit.setHpr, battle, origHpr))
    # if suit.dna.name == 'scg' and suit.isAngry:
    #     track.append(ActorInterval(suit, 'neutral-enraged-return', startTime=1, endTime=0))
    #     track.append(Func(suit.loop, 'neutral-enraged'))
    # elif suit.isImmortal and suit.dna.name == 'dsf':
    #     track.append(
    #        Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    # elif suit.isVulnerable and suit.dna.name == 'crf':
    #    track.append(
    #       Func(suit.loop, 'neutral2%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    # elif suit.isImmortal:
    #    track.append(ActorInterval(suit, 'highroller-neutral-levitate-in-out', startTime=1, endTime=0))
    #  track.append(Func(suit.loop, 'highroller-neutral-levitate-loop'))
    track.append(
        Func(suit.setNeutralAnimation))

    def returnTrapToSuit(suit = suit, trapStorage = trapStorage):
        return

    track.append(Func(returnTrapToSuit))
    track.append(unsueTrack)
    return track


def getSuitAnimTrack(attack, delay = 0, splicedAnims = None, playRate = 1.0):
    suit = attack['suit']
    tauntIndex = attack['taunt']
    battle = attack['battle']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    track = Sequence(Wait(delay))
    unsueTrack = Func(battle.unSueSuit, suit)
    for s in battle.activeSuits:
        if s.dna.name == 'psetter':
            theSuit = s
            track.append(Func(s.setPlayRate2, theSuit.getPlayRate2() + .5))
    if attack[
        'suitName'] == 'nothing':  # It isn't just 'caseman', it really all depends on the shorthand you have for the Case Manager.  If it is not 'caseman', change it to whatever is the actual shorthand for the Case Manager, or the Case Manager will not grunt as intended.
        track.append(Func(suit.setChatAbsolute, random.choice(['Hrm...', 'Hmph...', 'Hm, hm...', 'Hrnhmpf...']),
                          CFSpeech | CFTimeout))
    else:
        track.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    if splicedAnims:
        track.append(getSplicedAnimsTrack(splicedAnims, actor=suit))
    else:
        track.append(ActorInterval(suit, attack['animName'], playRate=playRate))
        # if suit.dna.name == 'scg' and suit.isAngry:
        #     track.append(ActorInterval(suit, 'neutral-enraged-return', startTime=1, endTime=0))
        #     track.append(Func(suit.loop, 'neutral-enraged'))
        # elif suit.isImmortal and suit.dna.name == 'dsf':
        #     track.append(
        #        Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
        # elif suit.isVulnerable and suit.dna.name == 'crf':
        #    track.append(
        #       Func(suit.loop, 'neutral2%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
        # elif suit.isImmortal:
        #    track.append(ActorInterval(suit, 'highroller-neutral-levitate-in-out', startTime=1, endTime=0))
        #  track.append(Func(suit.loop, 'highroller-neutral-levitate-loop'))
    track.append(
            Func(suit.setNeutralAnimation))
    track.append(unsueTrack)
    return track


def getPartTrack(particleEffect, startDelay, durationDelay, partExtraArgs, softStop = 0):
    particleEffect = partExtraArgs[0]
    parent = partExtraArgs[1]
    if len(partExtraArgs) > 2:
        worldRelative = partExtraArgs[2]
    else:
        worldRelative = 1
    return Sequence(Wait(startDelay), ParticleInterval(particleEffect, parent, worldRelative, duration=durationDelay, cleanup=True, softStopT=softStop))


def getPartTracks(attack, particleEffects, startDelay, durationDelay, worldRelative = 1, softStop = 0):
    '''
    Author: Professor Control
    '''
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    partTracks = Parallel()
    origHpr = battle.getActorPosHpr(suit)[1]
    for i in xrange(len(targets)):
        tgt = targets[i]
        toon = tgt['toon']
        origHpr = battle.getActorPosHpr(suit)[1] # We only want the rotation.
        particleEffects[i].reparentTo(suit) # Reparent the particle effect to the Cog.
        suit.headsUp(battle, toon.getPos(battle)) # Briefly turn the Cog to the Toon.
        particleEffects[i].wrtReparentTo(battle) # Drop the particle effect.
        partTracks.append(getPartTrack(particleEffects[i], startDelay, durationDelay, [particleEffects[i], battle, worldRelative], softStop))

    suit.setHpr(battle, origHpr) # After all that, set the Cog back like nothing ever happened.
    return partTracks


def getToonTrack(attack, damageDelay = 1e-06, damageAnimNames = None, dodgeDelay = 0.0001, dodgeAnimNames = None, splicedDamageAnims = None, splicedDodgeAnims = None, target = None, showDamageExtraTime = 0.01, showMissedExtraTime = 0.5):
    if not target:
        target = attack['target'][0]
    toon = target['toon']
    battle = attack['battle']
    suit = attack['suit']
    if suit:
        suitPos = suit.getPos(battle)
    toonPos = toon.getPos(battle)
    indicator = loader.loadModel('phase_5/models/effects/cc_m_txc_fx_bat_target_indicators')
    indicator.setHpr(0, -90, 0)
    indicator.setPos(toonPos.getX(), toonPos.getY(), .05)
    dmg = target['hp']
    animTrack = Sequence()
    if suit:
        animTrack.append(Func(toon.headsUp, battle, suitPos))
    indicatorTracks = Sequence(Func(indicator.reparentTo, battle), LerpScaleInterval(indicator, 0, Point3(4, 1, 4)),
                                   LerpColorScaleInterval(indicator, 0.5, Vec4(1, 0, 0, 1)), LerpColorScaleInterval(indicator, 0.5, Vec4(0, 0, 0, 0)),
                                 LerpColorScaleInterval(indicator, 0.5, Vec4(1, 0, 0, 1)),
                                 LerpColorScaleInterval(indicator, 0.5, Vec4(0, 0, 0, 0)),
                                 LerpColorScaleInterval(indicator, 0.5, Vec4(1, 0, 0, 1)), LerpColorScaleInterval(indicator, 0.5, Vec4(0, 0, 0, 0)),
                          Func(indicator.reparentTo, hidden), Func(indicator.clearColorScale), Func(MovieUtil.removeProp, indicator))
    currentBossHealth = -1
    currentBossHealth2 = -1
    if suit:
        if suit.style.name == 'caseman':
            for s in battle.activeSuits:
                if s.dna.name == 'sgoat' or s.dna.name == 'lgator' or s.dna.name == 'stenog':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1:
                animTrack.append(Func(suit.makeDesperation))
                animTrack.append(Func(suit.makeDamageUp))
        elif suit.style.name == 'sgoat':
            for s in battle.activeSuits:
                if s.dna.name == 'caseman':
                    currentBossHealth2 = s.currHP
                if s.dna.name == 'stenog' or s.dna.name == 'lgator' or s.dna.name == 'caseman':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1:
                animTrack.append(Func(suit.makeDesperation))
                animTrack.append(Func(suit.makeDamageUp))
        elif suit.style.name == 'lgator':
            for s in battle.activeSuits:
                if s.dna.name == 'caseman':
                    currentBossHealth2 = s.currHP
                if s.dna.name == 'sgoat' or s.dna.name == 'stenog' or s.dna.name == 'caseman':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1:
                animTrack.append(Func(suit.makeDesperation))
                animTrack.append(Func(suit.makeDamageUp))
        elif suit.style.name == 'stenog':
            for s in battle.activeSuits:
                if s.dna.name == 'caseman':
                    currentBossHealth2 = s.currHP
                if s.dna.name == 'sgoat' or s.dna.name == 'lgator' or s.dna.name == 'caseman':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1:
                animTrack.append(Func(suit.makeDesperation))
                animTrack.append(Func(suit.makeDamageUp))
        elif suit.style.name == 'ambass':
            for s in battle.activeSuits:
                if s.dna.name == 'wtapper' or s.dna.name == 'bkeeper' or s.dna.name == 'phouse':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1:
                animTrack.append(Func(suit.makeDesperation))
                animTrack.append(Func(suit.makeDamageUp))
        elif suit.style.name == 'wtapper':
            for s in battle.activeSuits:
                if s.dna.name == 'phouse' or s.dna.name == 'bkeeper' or s.dna.name == 'ambass':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1:
                animTrack.append(Func(suit.makeDesperation))
                animTrack.append(Func(suit.makeDamageUp))
        elif suit.style.name == 'bkeeper':
            for s in battle.activeSuits:
                if s.dna.name == 'wtapper' or s.dna.name == 'phouse' or s.dna.name == 'ambass':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1:
                animTrack.append(Func(suit.makeDesperation))
                animTrack.append(Func(suit.makeDamageUp))
        elif suit.style.name == 'phouse':
            for s in battle.activeSuits:
                if s.dna.name == 'wtapper' or s.dna.name == 'bkeeper' or s.dna.name == 'ambass':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1:
                animTrack.append(Func(suit.makeDesperation))
                animTrack.append(Func(suit.makeDamageUp))
        elif suit.style.name == 'safesupervis':
            for s in battle.activeSuits:
                if s.dna.name == 'ubuster' or s.dna.name == 'radiog' or s.dna.name == 'racket':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1:
                animTrack.append(Func(suit.makeDesperation))
                animTrack.append(Func(suit.makeDamageUp))
        elif suit.style.name == 'ubuster':
            for s in battle.activeSuits:
                if s.dna.name == 'radiog' or s.dna.name == 'safesupervis' or s.dna.name == 'racket':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1:
                animTrack.append(Func(suit.makeDesperation))
                animTrack.append(Func(suit.makeDamageUp))
        elif suit.style.name == 'racket':
            for s in battle.activeSuits:
                if s.dna.name == 'ubuster' or s.dna.name == 'safesupervis' or s.dna.name == 'radiog':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1:
                animTrack.append(Func(suit.makeDesperation))
                animTrack.append(Func(suit.makeDamageUp))
        elif suit.style.name == 'radiog':
            for s in battle.activeSuits:
                if s.dna.name == 'ubuster' or s.dna.name == 'safesupervis' or s.dna.name == 'racket':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1:
                animTrack.append(Func(suit.makeDesperation))
                animTrack.append(Func(suit.makeDamageUp))
        for s in battle.activeSuits:
                currentBossHealth = s.currHP
        if currentBossHealth == -1:
            animTrack.append(Func(suit.removeInsured))
        x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
        if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
            syphonSuitTrack = Parallel(Func(suit.showHpTextCheat, +0), Func(suit.showHpString, "SYPHONED!"), Func(suit.setHealthForMe, + 0), Func(suit.updateHealthBar, 0))
        elif suit.currHP + dmg > (suit.maxHP * suit.hardMaxHP) and suit.isSyphon:
            syphonSuitTrack = Parallel(Func(suit.showHpTextCheat, x), Func(suit.showHpString, "SYPHONED!"),
                                       Func(suit.setHealthForMe, x), Func(suit.updateHealthBar, 0))
        else:
            syphonSuitTrack = Parallel(Func(suit.showHpTextCheat, +dmg), Func(suit.showHpString, "SYPHONED!"),
                                       Func(suit.setHealthForMe, + dmg), Func(suit.updateHealthBar, 0))
    if suit:
        if dmg > 0 and suit.isSyphon:
            animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
            animTrack.append(syphonSuitTrack)
            return Parallel(animTrack, indicatorTracks)
        elif dmg > 0:
            animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
            return Parallel(animTrack, indicatorTracks)
        else:
            animTrack.append(getToonDodgeTrack(target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime))
            indicatorTrack = Sequence(Wait(dodgeDelay + showMissedExtraTime), Func(MovieUtil.indicateMissed, toon))
            return Parallel(animTrack, indicatorTrack, indicatorTracks)
    elif dmg > 0:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return Parallel(animTrack, indicatorTracks)
    else:
        animTrack.append(getToonDodgeTrack(target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime))
        indicatorTrack = Sequence(Wait(dodgeDelay + showMissedExtraTime), Func(MovieUtil.indicateMissed, toon))
        return Parallel(animTrack, indicatorTrack, indicatorTracks)


def getToonTracks(attack, damageDelay = 1e-06, damageAnimNames = None, dodgeDelay = 1e-06, dodgeAnimNames = None, splicedDamageAnims = None, splicedDodgeAnims = None, showDamageExtraTime = 0.01, showMissedExtraTime = 0.5):
    toonTracks = Parallel()
    targets = attack['target']
    for i in xrange(len(targets)):
        tgt = targets[i]
        toonTracks.append(getToonTrack(attack, damageDelay, damageAnimNames, dodgeDelay, dodgeAnimNames, splicedDamageAnims, splicedDodgeAnims, target=tgt, showDamageExtraTime=showDamageExtraTime, showMissedExtraTime=showMissedExtraTime))

    return toonTracks


def getToonDodgeTrack(target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime):
    toon = target['toon']
    toonTrack = Sequence()
    toonTrack.append(Wait(dodgeDelay))
    if dodgeAnimNames:
        for d in dodgeAnimNames:
            if d == 'sidestep':
                toonTrack.append(getAllyToonsDodgeParallel(target))
            else:
                toonTrack.append(ActorInterval(toon, d))

    else:
        toonTrack.append(getSplicedAnimsTrack(splicedDodgeAnims, actor=toon))
    toonTrack.append(Func(toon.loop, 'neutral'))
    return toonTrack


def getAllyToonsDodgeParallel(target):
    toon = target['toon']
    sidestepAnim = random.choice(('sidestep-right', 'sidestep-left'))
    soundEffect = globalBattleSoundCache.getSound(random.choice(('AV_jump_to_side.ogg', 'AV_side_step.ogg')))
    toonTracks = Parallel()
    toonTracks.append(Sequence(ActorInterval(toon, sidestepAnim), Func(toon.loop, 'neutral')))
    toonTracks.append(Sequence(Wait(0.5), SoundInterval(soundEffect, node=toon)))
    return toonTracks


def getPropTrack(prop, parent, posPoints, appearDelay, remainDelay, scaleUpPoint = Point3(1), scaleUpTime = 0.5, scaleDownTime = 0.5, startScale = Point3(0.01), anim = 0, propName = 'none', animDuration = 0.0, animStartTime = 0.0):
    if anim == 1:
        track = Sequence(Wait(appearDelay), Func(__showProp, prop, parent, *posPoints), LerpScaleInterval(prop, scaleUpTime, scaleUpPoint, startScale=startScale), ActorInterval(prop, propName, duration=animDuration, startTime=animStartTime), Wait(remainDelay), Func(MovieUtil.removeProp, prop))
    else:
        track = Sequence(Wait(appearDelay), Func(__showProp, prop, parent, *posPoints), LerpScaleInterval(prop, scaleUpTime, scaleUpPoint, startScale=startScale), Wait(remainDelay), LerpScaleInterval(prop, scaleDownTime, MovieUtil.PNT3_NEARZERO), Func(MovieUtil.removeProp, prop))
    return track


def getPropAppearTrack(prop, parent, posPoints, appearDelay, scaleUpPoint = Point3(1), scaleUpTime = 0.5, startScale = Point3(0.01), poseExtraArgs = None):
    propTrack = Sequence(Wait(appearDelay), Func(__showProp, prop, parent, *posPoints))
    if poseExtraArgs:
        propTrack.append(Func(prop.pose, *poseExtraArgs))
    propTrack.append(LerpScaleInterval(prop, scaleUpTime, scaleUpPoint, startScale=startScale))
    return propTrack


def getPropThrowTrack(attack, prop, hitPoints = [], missPoints = [], hitDuration = 0.25, missDuration = 0.25, hitPointNames = 'none', missPointNames = 'none', lookAt = 'none', groundPointOffSet = 0, missScaleDown = None, parent = render, target = None):
    '''
    target: Similar to what getToonTrack() has, we will use this to take note of a target.  Leave as none so that, by default, only the first targeted Toon gets the object thrown at them.
    '''
    if not target:
        target = attack['target'][0]
    toon = target['toon']
    dmg = target['hp']
    battle = attack['battle']

    def getLambdas(list, prop, toon):
        for i in xrange(len(list)):
            if list[i] == 'face':
                list[i] = lambda toon = toon: __toonFacePoint(toon)
            elif list[i] == 'miss':
                list[i] = lambda prop = prop, toon = toon: __toonMissPoint(prop, toon)
            elif list[i] == 'bounceHit':
                list[i] = lambda prop = prop, toon = toon: __throwBounceHitPoint(prop, toon)
            elif list[i] == 'bounceMiss':
                list[i] = lambda prop = prop, toon = toon: __throwBounceMissPoint(prop, toon)

        return list

    if hitPointNames != 'none':
        hitPoints = getLambdas(hitPointNames, prop, toon)
    if missPointNames != 'none':
        missPoints = getLambdas(missPointNames, prop, toon)
    propTrack = Sequence()
    propTrack.append(Func(battle.movie.needRestoreRenderProp, prop))
    propTrack.append(Func(prop.wrtReparentTo, parent))
    if lookAt != 'none':
        propTrack.append(Func(prop.lookAt, lookAt))
    if dmg > 0:
        for i in xrange(len(hitPoints)):
            pos = hitPoints[i]
            propTrack.append(LerpPosInterval(prop, hitDuration, pos=pos))

    else:
        for i in xrange(len(missPoints)):
            pos = missPoints[i]
            propTrack.append(LerpPosInterval(prop, missDuration, pos=pos))

        if missScaleDown:
            propTrack.append(LerpScaleInterval(prop, missScaleDown, MovieUtil.PNT3_NEARZERO))
    propTrack.append(Func(MovieUtil.removeProp, prop))
    propTrack.append(Func(battle.movie.clearRenderProp, prop))
    return propTrack


def getThrowTrack(object, target, duration = 1.0, parent = render, gravity = -32.144):
    values = {}

    def calcOriginAndVelocity(object = object, target = target, values = values, duration = duration, parent = parent, gravity = gravity):
        if callable(target):
            target = target()
        object.wrtReparentTo(parent)
        values['origin'] = object.getPos(parent)
        origin = object.getPos(parent)
        values['velocity'] = (target[2] - origin[2] - 0.5 * gravity * duration * duration) / duration

    return Sequence(Func(calcOriginAndVelocity), LerpFunctionInterval(throwPos, fromData=0.0, toData=1.0, duration=duration, extraArgs=[object,
     duration,
     target,
     values,
     gravity]))


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


def getToonTakeDamageTrack(attack, toon, died, dmg, delay, damageAnimNames = None, splicedDamageAnims = None, showDamageExtraTime = 0.01):
    toonTrack = Sequence()
    toonTrack.append(Wait(delay))
    suitResponseTrack = Sequence()
    suit = attack['suit']
    if damageAnimNames:
        for d in damageAnimNames:
            toonTrack.append(ActorInterval(toon, d))

        indicatorTrack = Sequence(Wait(delay + showDamageExtraTime), Func(__doDamage, toon, dmg, died))
    else:
        splicedAnims = getSplicedAnimsTrack(splicedDamageAnims, actor=toon)
        toonTrack.append(splicedAnims)
        indicatorTrack = Sequence(Wait(delay + showDamageExtraTime), Func(__doDamage, toon, dmg, died))
    soundTrack = getSoundTrack('laff_loss.ogg', delay=delay + showDamageExtraTime, node=toon)
    toonTrack.append(Func(toon.loop, 'neutral'))
    if toon.hp - dmg <= 0:
        suit = attack['suit']
        toonTrack.append(Wait(3.0))
        if suit.getStyleName() in OTPLocalizerEnglish.SuitDefeatTaunts:
            suitResponseTrack.append(Parallel(Sequence(Wait(delay + showDamageExtraTime), Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitDefeatTaunts[suit.getStyleName()]), CFSpeech | CFTimeout))))
        else:
            suitResponseTrack.append(Parallel(Sequence(Wait(delay + showDamageExtraTime), Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitDefeatTauntsNone), CFSpeech | CFTimeout))))
    return Parallel(toonTrack, indicatorTrack, suitResponseTrack, soundTrack)


def getToonTakeDamageTrackCheat(attack, toon, died, dmg, delay, damageAnimNames = None, splicedDamageAnims = None, showDamageExtraTime = 0.01):
    toonTrack = Sequence()
    toonTrack.append(Wait(delay))
    suitResponseTrack = Sequence()
    suit = attack['suit']
    if damageAnimNames:
        for d in damageAnimNames:
            toonTrack.append(ActorInterval(toon, d))

        indicatorTrack = Sequence(Wait(delay + showDamageExtraTime), Func(__doDamageCheat, toon, dmg, died))
    else:
        splicedAnims = getSplicedAnimsTrack(splicedDamageAnims, actor=toon)
        toonTrack.append(splicedAnims)
        indicatorTrack = Sequence(Wait(delay + showDamageExtraTime), Func(__doDamageCheat, toon, dmg, died))
    soundTrack = getSoundTrack('laff_loss.ogg', delay=delay + showDamageExtraTime, node=toon)
    toonTrack.append(Func(toon.loop, 'neutral'))
    if toon.hp - dmg <= 0:
        suit = attack['suit']
        toonTrack.append(Wait(3.0))
        if suit.getStyleName() in OTPLocalizerEnglish.SuitDefeatTaunts:
            suitResponseTrack.append(Parallel(Sequence(Wait(delay + showDamageExtraTime), Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitDefeatTaunts[suit.getStyleName()]), CFSpeech | CFTimeout))))
        else:
            suitResponseTrack.append(Parallel(Sequence(Wait(delay + showDamageExtraTime), Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitDefeatTauntsNone), CFSpeech | CFTimeout))))
    return Parallel(toonTrack, indicatorTrack, suitResponseTrack, soundTrack)


def getSplicedAnimsTrack(anims, actor = None):
    track = Sequence()
    for nextAnim in anims:
        delay = 1e-06
        if len(nextAnim) >= 2:
            if nextAnim[1] > 0:
                delay = nextAnim[1]
        if len(nextAnim) <= 0:
            track.append(Wait(delay))
        elif len(nextAnim) == 1:
            track.append(ActorInterval(actor, nextAnim[0]))
        elif len(nextAnim) == 2:
            track.append(Wait(delay))
            track.append(ActorInterval(actor, nextAnim[0]))
        elif len(nextAnim) == 3:
            track.append(Wait(delay))
            track.append(ActorInterval(actor, nextAnim[0], startTime=nextAnim[2]))
        elif len(nextAnim) == 4:
            track.append(Wait(delay))
            duration = nextAnim[3]
            if duration < 0:
                startTime = nextAnim[2]
                endTime = startTime + duration
                if endTime <= 0:
                    endTime = 0.01
                track.append(ActorInterval(actor, nextAnim[0], startTime=startTime, endTime=endTime))
            else:
                track.append(ActorInterval(actor, nextAnim[0], startTime=nextAnim[2], duration=duration))
        elif len(nextAnim) == 5:
            track.append(Wait(delay))
            track.append(ActorInterval(nextAnim[4], nextAnim[0], startTime=nextAnim[2], duration=nextAnim[3]))

    return track


def getSplicedLerpAnims(animName, origDuration, newDuration, startTime = 0, fps = 30, reverse = 0):
    anims = []
    addition = 0
    numAnims = origDuration * fps
    timeInterval = newDuration / numAnims
    animInterval = origDuration / numAnims
    if reverse == 1:
        animInterval = -animInterval
    for i in xrange(0, int(numAnims)):
        anims.append([animName,
         timeInterval,
         startTime + addition,
         animInterval])
        addition += animInterval

    return anims


def getSoundTrack(fileName, delay = 0.01, duration = 0.0, node = None):
    return Sequence(Wait(delay), SoundInterval(globalBattleSoundCache.getSound(fileName), duration=duration, node=node))


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
    posPoints = [Point3(0.375, -1.5, .85), VBase3(0, 220, -10)]
    propTrack = Sequence(
        getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.25, MovieUtil.PNT3_ONE, scaleUpTime=0.25))
    propTrack.append(Wait(1.55))
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
            Wait(2),
            Parallel(hideParts(headParts), hideParts(torsoParts), hideParts(legsParts), dustCloudHideIval),
            Wait(1.7),
            Parallel(showParts(headParts), showParts(torsoParts), showParts(legsParts), dustCloudShowIval),
        ))

    toonTrack.append(getToonTrack(attack, 2.0, ['conked'], 2.5, ['jump']))

    return Parallel(suitTrack, toonTrack, propTrack)

def doGoldDust(attack):
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
        BattleParticles.setEffectTexture(snowEffect, 'snow-particle', Vec4(0.898, 0.811, 0.446, 1.0))
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
        cloudPropTrack.append(Wait(partDelay))
        cloudPropTrack.append(
            ParticleInterval(snowEffect, cloud, worldRelative=0, duration=3.1, cleanup=True, softStopT=-1))
        cloudPropTrack.append(Wait(0.4))
        cloudPropTrack.append(LerpScaleInterval(cloud, 0.25, MovieUtil.PNT3_NEARZERO))
        cloudPropTrack.append(Func(MovieUtil.removeProp, cloud))
        cloudPropTrack.append(Func(battle.movie.clearRenderProp, cloud))
        cloudPropTracks.append(cloudPropTrack)

    damageAnims = [['cringe',
                    0.01,
                    0.4,
                    0.8], ['duck', 0.01, 1.6]]
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay,
                               dodgeAnimNames=['sidestep'], showMissedExtraTime=1.2)
    soundTrack = getSoundTrack('SA_brainstorm.ogg', delay=1.3, node=suit)
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
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    tie = globalPropPool.getProp('clip-on-tie')
    suitType = getSuitBodyType(attack['suitName'])
    throwDelay = 1.25
    damageDelay = 2
    dodgeDelay = 1
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    posPoints = [Point3(-1, 1, -.25), VBase3(0, 0, 0)]
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
            getPropAppearTrack(tie, suit.getRightHand(), posPoints, 0.5, Point3(1.5, 1.5, 1.5), scaleUpTime=0.25))
        tiePropTrack.append(ActorInterval(tie, 'clip-on-tie', duration=throwDelay, startTime=1.1))
        tiePropTrack.append(Func(tie.setBillboardPointEye))
        tiePropTrack.append(
            getPropThrowTrack(attack, tie, [__toonFacePoint(toon)], [__toonGroundPoint(attack, toon, 0.1)],
                              hitDuration=0.25, missDuration=0.8))
        explodeTrack.append(
            getPropAppearTrack(explode, toon, explodePosPoints, 0, Point3(2, 2, 2), scaleUpTime=0))
        explodeTrack.append(Sequence(ActorInterval(explode, splatName), Func(explode.detachNode)))
    else:
        explodePosPoints = [Point3(0, -7, 0), MovieUtil.PNT3_ZERO]
        tiePropTrack = Sequence(
            getPropAppearTrack(tie, suit.getRightHand(), posPoints, 0.5, Point3(1.5, 1.5, 1.5), scaleUpTime=0.25))
        tiePropTrack.append(ActorInterval(tie, 'clip-on-tie', duration=throwDelay, startTime=1.1))
        tiePropTrack.append(getThrowTrack(tie, missPoint2, duration=0.5, parent=battle, gravity=-300))
        #tiePropTrack.append(LerpHprInterval(tie, 0, VBase3(0, 90, 0)))
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
    toonTrack = getToonTrack(attack, damageDelay, ['conked'], dodgeDelay, ['duck'])
    throwSound = getSoundTrack('SA_powertie_throw.ogg', delay=throwDelay + .5, node=suit)
    return Parallel(suitTrack, toonTrack, tiePropTrack, throwSound)


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
            Func(MovieUtil.removeProp, sandTrap),
            Func(battle.movie.clearRenderProp, sandTrap)
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
            Func(MovieUtil.removeProp, clock)
        )
        clockPropTracks.append(clockPropTrack)

    damageAnims = [['melt'], ['jump', 1.5, 0.4]]
    toonTracks = getToonTracks(attack, damageDelay=7.1, splicedDamageAnims=damageAnims, dodgeDelay=6.05, dodgeAnimNames=['sidestep'])
    return Parallel(suitTrack, clockPropTracks, toonTracks)

def doDisassemble(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    tauntInterval = Sequence(Wait(1), Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    damageDelay = 1.5
    attackDelay = 1.5
    sprayEffect = BattleParticles.createParticleEffect(file='reorgSpray')
    suitTrack = Sequence(Wait(1), ActorInterval(suit, attack['animName']))
    suitPos = suit.getPos(battle)
    cagePropTracks = Parallel()
    cage = loader.loadModel('phase_3.5/models/modules/desk_only')
    card = globalPropPool.getProp('ttht_m_ene_techbotLaptop')
    propTrackNew = Parallel()
    laptopPosPoints = [Point3(-2, 1.5, 2.5), VBase3(0, 0, 0)]
    laptopDuration = 2.8
    scaleUpPoint = Point3(1.75, 1.75, 1.75)
    propTrackNew.append(
        getPropTrack(card, cage, laptopPosPoints, 1e-06, 2, scaleUpPoint=scaleUpPoint, scaleUpTime=0,
                     anim=1, animStartTime=0.5, animDuration=2.5,
                     propName='ttht_m_ene_techbotLaptop'))
    cagePos = [Point3(suitPos.getX() - 3, suitPos.getY() - 3, 0), suit.getHpr(battle)]
    cagePropTrack = Sequence(
        getPropAppearTrack(cage, battle, cagePos, 0.01, scaleUpPoint=Point3(1.5), scaleUpTime=1),
        Parallel(
            SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/asfhdfha.ogg'), duration=0.75, node=cage)
        ),
        Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/asfhafhsdh.ogg'), node=cage),
        Wait(2.0),
        LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0),
        Func(MovieUtil.removeProp, cage)
    )

    cagePropTracks.append(cagePropTrack)
    partTrack = getPartTrack(sprayEffect, 1.0, 1.9, [sprayEffect, suit, 0])
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
            headTracks.append(Sequence(Wait(attackDelay), LerpPosInterval(part, 0.1, Point3(x - 0.2, y, z - 0.03)),
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

        def getChestTrack(part, attackDelay=attackDelay):
            origScale = part.getScale()
            return Sequence(Wait(attackDelay), LerpHprInterval(part, 1.1, VBase3(180, 0, 0)), Wait(1.1),
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
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.01,
                             dodgeAnimNames=['duck'])
    if dmg > 0:
        return Parallel(suitTrack, tauntInterval, cagePropTracks, toonTrack, propTrackNew, headTracks, chestTracks)
    else:
        return Parallel(suitTrack, tauntInterval, cagePropTracks, propTrackNew, toonTrack)


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
    partTracks = getPartTracks(attack, particleEffects, 1.1, 3.0, 0, softStop=-1)
    phonePosPoints = [Point3(-0.23, 0, -0.11), VBase3(5.939, 2.763, -177.591)]
    receiverPosPoints = [Point3(-0.23, 0, -0.11), VBase3(5.939, 2.763, -177.591)]
    propTrack = Sequence(Func(__showProp, phone, suit.getLeftHand(), phonePosPoints[0], phonePosPoints[1]), Func(__showProp, receiver, suit.getLeftHand(), receiverPosPoints[0], receiverPosPoints[1]), LerpScaleInterval(phone, 0.5, MovieUtil.PNT3_ONE, MovieUtil.PNT3_NEARZERO), Wait(0.24), Func(receiver.wrtReparentTo, suit.getRightHand()), LerpPosHprInterval(receiver, 0.0001, Point3(-0.45, 0.48, -0.62), VBase3(-87.47, -18.21, 7.82)), Wait(2.14), Func(receiver.wrtReparentTo, phone), Wait(0.62), LerpScaleInterval(phone, 0.5, MovieUtil.PNT3_NEARZERO), Func(MovieUtil.removeProps, [receiver, phone]))
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
        sparklePosPoints = [Point3(-0.1, 1, -1.5), VBase3(335, 0, 0)]
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

def doCloseTheLoop(attack):
    suit = attack['suit']
    battle = attack['battle']
    phone = globalPropPool.getProp('phone')
    receiver = globalPropPool.getProp('receiver')
    suitTrack = getSuitTrack(attack)
    suitName = suit.getStyleName()
    phonePosPoints = [Point3(0.23, 0.17, -0.11), VBase3(5.939, 2.763, -177.591)]
    receiverPosPoints = [Point3(0.23, 0.17, -0.11), VBase3(5.939, 2.763, -177.591)]
    receiverAdjustScale = MovieUtil.PNT3_ONE
    pickupDelay = 0.74
    dialDuration = 3.07
    finalPhoneDelay = 0.69
    scaleUpPoint = MovieUtil.PNT3_ONE
    propTrack = Sequence(Wait(0.3), Func(__showProp, phone, suit.getLeftHand(), phonePosPoints[0], phonePosPoints[1]), Func(__showProp, receiver, suit.getLeftHand(), receiverPosPoints[0], receiverPosPoints[1]), LerpScaleInterval(phone, 0.5, scaleUpPoint, MovieUtil.PNT3_NEARZERO), Wait(pickupDelay), Func(receiver.wrtReparentTo, suit.getRightHand()), LerpScaleInterval(receiver, 0.01, receiverAdjustScale), LerpPosHprInterval(receiver, 0.0001, Point3(-0.53, 0.21, -0.54), VBase3(-99.49, -35.27, 1.84)), Wait(dialDuration), Func(receiver.wrtReparentTo, phone), Wait(finalPhoneDelay), LerpScaleInterval(phone, 0.5, MovieUtil.PNT3_NEARZERO), Func(MovieUtil.removeProps, [receiver, phone]))
    toonTrack = getToonTrack(attack, 5.5, ['slip-backward'], 4.7, ['jump'])
    soundTrack = getSoundTrack('SA_hangup.ogg', delay=1.3, node=suit)
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack)

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

    particleEffect = BattleParticles.createParticleEffect(file='nickelDime')
    waterfallEffect = BattleParticles.createParticleEffect(file='nickelDimeWaterfall')
    suitTrack = getSuitAnimTrack(attack)
    partTrack = getPartTrack(particleEffect, 1.0, 1.9, [particleEffect, suit, 0])
    waterfallTrack = getPartTrack(waterfallEffect, 0.8, 1.9, [waterfallEffect, suit, 0])
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
    suitTrack = getSuitAnimTrack(attack)

    def getPowerTrack(effect, suit = suit, battle = battle):
        partTrack = Sequence(Wait(0.7), Func(battle.movie.needRestoreParticleEffect, effect), Func(effect.start, suit), Wait(0.4), LerpPosInterval(effect, 1.0, Point3(0, 15, 0.4)), LerpFunctionInterval(effect.setAlphaScale, fromData=1, toData=0, duration=0.4), Func(effect.cleanup), Func(battle.movie.clearRestoreParticleEffect, effect))
        return partTrack

    partTrack1 = getPowerTrack(powerBar1)
    partTrack2 = getPowerTrack(powerBar2)
    waterfallTrack = getPartTrack(waterfallEffect, 0.6, 0.6, [waterfallEffect, suit, 0])
    toonTracks = getToonTracks(attack, 1.5, ['slip-forward'], 0.86, ['jump'])
    soundTrack = getSoundTrack('ttr_s_ene_bat_quash.ogg', delay=0.2, node=suit)
    return Parallel(suitTrack, partTrack1, partTrack2, soundTrack, waterfallTrack, toonTracks)


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


def doElectrostaticEnergy(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    suitTrack = Sequence(getSuitAnimTrack(attack))
    targets = attack['target']
    cagePropTracks = Parallel()
    smokeTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        toonPos = toon.getPos(battle)
        smoke = loader.loadModel('phase_4/models/props/test_clouds')
        smoke.setColor(0.8, 0.7, 0.5, 1)
        smoke.setBillboardPointEye()
        smokeTrack = Sequence(Wait(1), Func(smoke.reparentTo, toon),
                              Parallel(LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
                                       LerpColorScaleInterval(smoke, 1, Vec4(1, 1, 1, 0))),
                              Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale),
                              Func(MovieUtil.removeProp, smoke))
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
        cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, 1, scaleUpPoint=Point3(2.0, 2.0, 10.0), scaleUpTime=0),
            Parallel(cagePosition),
            Parallel(
                cage.posInterval(0, Point3(toonPos.getX(), y, 0.1), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/AA_lightning.ogg'), duration=0.75, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_5/audio/sfx/AA_cog_shock.ogg'), node=cage),
            Wait(0.5),
            LerpFunctionInterval(cage.setAlphaScale, fromData=.5, toData=0, duration=0.5),
            Func(MovieUtil.removeProp, cage)
        )
        cagePropTracks.append(cagePropTrack)
        smokeTracks.append(smokeTrack)
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    damageAnims = [['slip-forward', 0.0001, 0.5]]
    toonTrack = getToonTracks(attack, damageDelay=1, splicedDamageAnims=damageAnims, dodgeDelay=.75, dodgeAnimNames=[], splicedDodgeAnims=[], showDamageExtraTime=0.5)
    oldcolor = render.getColorScale()
    lightingTrack = Sequence(Wait(0), LerpColorScaleInterval(render, 0.5, (0, 0.992, 1, 1)),
                             LerpColorScaleInterval(render, 2.5, (0, 0.992, 1, 1)),
                             LerpColorScaleInterval(render, 1, (oldcolor)))
    return Parallel(suitTrack, cagePropTracks, smokeTracks, toonTrack)

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
    pad = loader.loadModel('phase_3.5/models/props/cc_m_prp_gen_coin_silver')
    suitTrack = getSuitAnimTrack(attack)
    padPosPoints = [Point3(0, 0, 0), VBase3(14.93, -2.29, 180.0)]
    padPropTrack = getPropTrack(pad, suit.getLeftHand(), padPosPoints, 0.5, 2.57)
    toonTrack = getToonTracks(attack, 2.2, ['cringe'], 2.0, ['jump'])
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
        particleEffect.setPos(0.167, 1.9, suit.getHeight() - 1.8)
        particleEffect.setP(-110)
        particleEffects.append(particleEffect)

    suitType = getSuitBodyType(attack['suitName'])
    partDelay = 1.3
    damageDelay = 2.7
    dodgeDelay = 1.7
    suitTrack = getSuitTrack(attack)
    partTracks = getPartTracks(attack, particleEffects, partDelay, 4.0, 0, softStop=-2.0)
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
    stampPosPoints = [Point3(-0.25, -0.5, -0.25), VBase3(0, -90, 0)]
    padPropTrack = getPropTrack(pad, suit.getLeftHand(), padPosPoints, 1e-06, 3.2)
    missPoint = lambda cancelled = cancelled, toon = toon: __toonMissPoint(cancelled, toon)
    propTrack = Sequence(Func(__showProp, stamp, suit.getRightHand(), stampPosPoints[0], stampPosPoints[1]), LerpScaleInterval(stamp, 0.5, MovieUtil.PNT3_ONE), Wait(2.6), Func(battle.movie.needRestoreRenderProp, cancelled), Func(cancelled.reparentTo, render), Func(cancelled.setScale, 0.6), Func(cancelled.setPosHpr, stamp, 0.81, -1.11, -0.16, 0, 0, 90), Func(cancelled.setP, 0), Func(cancelled.setR, 0))
    propTrack.append(getPropThrowTrack(attack, cancelled, [__toonFacePoint(toon)], [missPoint]))
    propTrack.append(Func(MovieUtil.removeProp, cancelled))
    propTrack.append(Func(battle.movie.clearRenderProp, cancelled))
    propTrack.append(Wait(0.3))
    propTrack.append(LerpScaleInterval(stamp, 0.5, MovieUtil.PNT3_NEARZERO))
    propTrack.append(Func(MovieUtil.removeProp, stamp))
    toonTrack = getToonTrack(attack, 3.4, ['conked'], 1.9, ['sidestep'])
    soundTrack = getSoundTrack('SA_rubber_stamp.ogg', delay=1.3, duration=1.1, node=suit)
    return Parallel(suitTrack, toonTrack, propTrack, padPropTrack, soundTrack)


def doRazzleDazzle(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    hitSuit = dmg > 0
    sign = globalPropPool.getProp('smile')
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect('Smile')
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    signPosPoints = [Point3(0.0, -0.42, -0.04), VBase3(105.715, 73.977, 65.932)]
    if hitSuit:
        hitPoint = lambda toon = toon: __toonFacePoint(toon)
    else:
        hitPoint = lambda particleEffect = particleEffect, toon = toon, suit = suit: __toonMissPoint(particleEffect, toon, parent=suit.getRightHand())
    signPropTrack = Sequence(Func(__showProp, sign, suit.getRightHand(), signPosPoints[0], signPosPoints[1]), LerpScaleInterval(sign, 0.5, Point3(1.39, 1.39, 1.39)), Wait(0.5), Func(battle.movie.needRestoreParticleEffect, particleEffect), Func(particleEffect.start, sign), Func(particleEffect.wrtReparentTo, render), LerpPosInterval(particleEffect, 1.0, pos=hitPoint), Func(particleEffect.cleanup), LerpScaleInterval(sign, 0.5, Point3(0, 0, 0)), Func(battle.movie.clearRestoreParticleEffect, particleEffect))
    signPropAnimTrack = ActorInterval(sign, 'smile', duration=2.5, startTime=1)
    toonTrack = getToonTrack(attack, 2.0, ['cringe'], 1.3, ['sidestep'])
    soundTrack = getSoundTrack('SA_razzle_dazzle.ogg', delay=0.8, node=suit)
    return Sequence(Parallel(suitTrack, signPropTrack, signPropAnimTrack, toonTrack, soundTrack), Func(MovieUtil.removeProp, sign))


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


def doSynergy2(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.7
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1
    pbpText = attack['playByPlayText']
    pbpDc = PlayByPlayText.PlayByPlayText()

    pbpDesc = pbpDc.getShowIntervalDesc('Level 6 and 7 Gags are now off-limits!', 3.5)
    pbpTrack = pbpText.getShowIntervalCheat('Quality Control!', 3.5)
    pbpDesc2 = pbpDc.getShowIntervalDesc('The interest fees are racking up!', 3.5)
    pbpTrack2 = pbpText.getShowIntervalCheat('Compound Interest!', 3.5)
    ceaseTrack = ActorInterval(suit, 'cease')
    particleEffect = BattleParticles.createParticleEffect('Synergy')
    waterfallEffect = BattleParticles.createParticleEffect(file='synergyWaterfall')
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack.append(Func(suit.setNeutralAnimation))
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
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, damageAnimNames=['slip-forward'], dodgeDelay=0.91,
                               splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.0)
    synergySoundTrack = Sequence(Wait(0.9), SoundInterval(globalBattleSoundCache.getSound('SA_synergy.ogg'), node=suit))
    if hitAtleastOneToon > 0:
        soundTrack1 = Sequence(Wait(2.0),
                               SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=suit))
        multiTrack = Parallel(soundTrack1)
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, toonTracks, multiTrack)
    else:
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, toonTracks)


def doEmbezzle(attack):
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
    billPosPoints = [Point3(-0.01, 0.45, -0.25), VBase3(136.424, -46.434, -129.712)]
    billPropTrack = getPropTrack(bill, suit.getRightHand(), billPosPoints, 0.6, 0.55, scaleUpPoint=Point3(5.0, 5.0, 5.0))
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
    partTrack = getPartTrack(particleEffect, 1.0, 3.9, [particleEffect, suit, 0], softStop=-2)
    waterfallTrack = getPartTrack(waterfallEffect, 0.8, 3.9, [waterfallEffect, suit, 0], softStop=-2)
    damageAnims = [['melt'], ['jump', 1.5, 0.4]]
    dodgeAnims = []
    dodgeAnims.append(['jump',
     0.01,
     0,
     0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.3, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.91, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.0, showDamageExtraTime=1.0)
    synergySoundTrack = Sequence(Wait(0.9), SoundInterval(globalBattleSoundCache.getSound('SA_synergy.ogg'), node=suit))
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
    sinkPos = suit.getPos(battle)
    dropPos = suit.getPos(battle)
    sinkPos2 = suit.getPos(battle)
    dropPos2 = suit.getPos(battle)
    sinkPos.setY(sinkPos.getY() + 12.5)
    sinkPos.setZ(sinkPos.getZ() - 4.5)
    sinkPos2.setY(sinkPos.getY() - 30.5)
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    targetPos2 = toon.getPos(battle)
    headsUp2 = Func(suit.setHpr, battle, origHpr)
    moveTrack = Sequence(LerpPosInterval(suit, 2.75, sinkPos2, other=battle), Func(suit.setPos, battle, dropPos))
    suitTrack = Sequence(tauntInterval, headsUp, ActorInterval(suit, 'walk'), ActorInterval(suit, 'walk'), headsUp2, Func(suit.setNeutralAnimation))
    damageAnims = []
    damageAnims.append(['cringe'])
    toonTrack = getToonTrack(attack, damageDelay=2.5, splicedDamageAnims=damageAnims, dodgeDelay=0.91, dodgeAnimNames=['sidestep'])
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
    knifeDelay = 4.0
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
    soundTrack = Sequence(Wait(4.0), SoundInterval(globalBattleSoundCache.getSound('SA_hostile_takeover.ogg'), node=suit))
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
    toonTracks = getToonTracks(attack, suitTrack.getDuration() - 1.75, ['slip-backward'], 1.5, ['duck'],
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
    makeNonImmortal = Func(suit.makeNonImmortal)
    suitTrack.append(makeNonImmortal)
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
    damageDelay = 3.5
    dodgeDelay = 3.3
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
        cloudPropTrack.append(Wait(partDelay))
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
        freezeEffect.setPos(0, 0, facePoint.getZ())
        unFreezeEffect.setPos(0, 0, facePoint.getZ())
        if dmg > 0:
            partTracks2.append(getPartTrack(freezeEffect, 2.4, 2.9, [freezeEffect, toon, 0], softStop=-1))
            partTracks3.append(getPartTrack(unFreezeEffect, 6.65, 1.5, [unFreezeEffect, toon, 0], softStop=-1))

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
    toonTracks = getToonTracks(attack, damageDelay=1.0, splicedDamageAnims=damageAnims, dodgeDelay=0.0001, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.6, showDamageExtraTime=1.3)
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
    for t in targets:
        BattleParticles.loadParticles()
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
    suitDelay = 1.23
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
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    posPoints = [Point3(-0.1, -0.175, 0), VBase3(-10.584, 11.945, -161.684)]
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
      propDelay + suitDelay + throwDuration,
      0.01,
      0.7], ['slip-backward', 0.01, 0.45]]
    toonTrack = getToonTrack(attack, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'], showDamageExtraTime=propDelay + suitDelay + 2.4)
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

    damageDelay = 1.5
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
        soundTrack = getSoundTrack('SA_head_shrink_only.ogg', delay=2, node=suit)
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
    throwDelay = 2.43
    throwDuration = 0.5
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    posPoints = [Point3(-0.25, -0.35, 0), VBase3(-180, 0, 0)]
    propTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        paper = globalPropPool.getProp('pink-slip')
        paperAppearTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.8, Point3(8, 8, 8), scaleUpTime=0.25))
        paperAppearTrack.append(Wait(0.93))
        hitPoint = __toonGroundPoint(attack, toon, 0.2, parent=battle)
        paperAppearTrack.append(Func(battle.movie.needRestoreRenderProp, paper))
        paperAppearTrack.append(Func(paper.wrtReparentTo, battle))
        paperAppearTrack.append(LerpPosInterval(paper, throwDuration, hitPoint))
        if dmg > 0:
            paperPause = 0.01
            slidePoint = Point3(hitPoint.getX(), hitPoint.getY() - 5, hitPoint.getZ() + 4)
            landPoint = Point3(hitPoint.getX(), hitPoint.getY() - 5, hitPoint.getZ())
            paperAppearTrack.append(Wait(paperPause))
            paperAppearTrack.append(LerpPosInterval(paper, 0.2, slidePoint))
            paperAppearTrack.append(LerpPosInterval(paper, 1.1, landPoint))
            paperSpinTrack = Sequence(Wait(throwDelay), LerpHprInterval(paper, throwDuration, VBase3(300, 0, 0)), Wait(paperPause), LerpHprInterval(paper, 1.3, VBase3(-200, 100, 100)))
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
    sprayEffects = BattleParticles.createParticleEffect('DemotionSpray2')
    BattleParticles.loadParticles()
    BattleParticles.setEffectTexture(sprayEffects, 'snow-particle',
                                     color=Vec4(1, 0, 0, 1))
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    partTracks = getPartTrack(sprayEffects, 0.5, 3.0, [sprayEffects, suit, 0], softStop=-1)
    allHeadTracks = Parallel()
    allChestTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
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
    leftPosPoints = [Point3(0.5, 5, suit.height - 2.5), MovieUtil.PNT3_ZERO]
    rightPosPoints = [Point3(-0.5, 5, suit.height - 2.5), MovieUtil.PNT3_ZERO]
    leftKnifeTracks = Parallel()
    rightKnifeTracks = Parallel()
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
    throwDelay = 1.25
    damageDelay = 2.25
    dodgeDelay = 1
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    posPoints = [Point3(-1, 0.5, -.1), VBase3(99, -90, -108.2)]
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
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    propTrack = getPropTrack(rollodex, suit.getLeftHand(), propPosPoints, 1e-06, 4.7, scaleUpPoint=propScale, anim=0, propName='rollodex', animDuration=0, animStartTime=0)
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
    posPoints = [Point3(-0.4, 5.5, suit.height - 2), VBase3(-155.0, -20.0, 0.0)]
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
    soundTrack = getSoundTrack('SA_evil_eye.ogg', delay=1.3, node=suit)
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
    hitAtleastOneToon = False
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = True

    suitType = getSuitBodyType(attack['suitName'])
    throwDelay = 1.25
    damageDelay = 2
    dodgeDelay = 1
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    posPoints = [Point3(-0.8, 0.5, -0.25), VBase3(90, 90, 0)]
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
    damageDelay = 2.5
    dodgeDelay = 2.25
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    partTrack = getPartTrack(particleEffect, partDelay, 2.8, [particleEffect, suit, 0], softStop=-1)
    partTrack2 = getPartTrack(particleEffect2, partDelay, 2.8, [particleEffect2, suit, 0], softStop=-1)
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
        cloudPropTrack.append(Wait(partDelay))
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
        BattleParticles.setEffectTexture(sprayEffect, 'fire')
        sprayEffects.append(sprayEffect)

    sprayDelay = 0.6
    flameDelay = 1.25
    flameDuration = 3.5
    flecksDelay = flameDelay + 0.8
    flecksDuration = flameDuration - 0.8
    damageDelay = 1.5
    dodgeDelay = 1.0
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    sprayTracks = getPartTracks(attack, sprayEffects, sprayDelay, 2.3, 0)
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


def doPickPocket(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    bill = globalPropPool.getProp('1dollar')
    suitTrack = getSuitTrack(attack)
    suitTrack.append(Wait(1.0))
    billPosPoints = [Point3(-0.01, 0.45, -0.25), VBase3(136.424, -46.434, -129.712)]
    billPropTrack = getPropTrack(bill, suit.getRightHand(), billPosPoints, 0.6, 0.55, scaleUpPoint=Point3(1.41, 1.41, 1.41))
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
    billPosPoints = [Point3(-0.01, 0.45, -0.25), VBase3(136.424, -46.434, -129.712)]
    billPropTrack = getPropTrack(bill, suit.getRightHand(), billPosPoints, 0.6, 0.55, scaleUpPoint=Point3(1.41, 1.41, 1.41))
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
    if suit.dna.name == 'hho' and not suit.isSkeleton:
        return doHeadHonchoCigarSmoke(attack)
    elif suit.dna.name == 'fires' and not suit.isSkeleton:
        return doFirestarterCigarSmoke(attack)
    else:
        pass
    BattleParticles.loadParticles()
    smoke = BattleParticles.createParticleEffect('Smoke')
    BattleParticles.setEffectTexture(smoke, 'snow-particle')
    cigar = globalPropPool.getProp('cigar')
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    elif suitType == 'c':
        suitTrack = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout), ActorInterval(suit, attack['animName'], duration=4.25), Func(suit.setNeutralAnimation))
    cigarPosPoints = [Point3(-0.05, -0.2, -0.25), VBase3(180.0, 0.0, 0.0)]
    cigarPropTrack = getPropTrack(cigar, suit.getRightHand(), cigarPosPoints, 0, 2.6, scaleUpPoint=Point3(7.0, 7.0, 7.0))
    toonTrack = getToonTrack(attack, 2.55, ['cringe'], 2.0, ['sidestep'])
    multiTrackList = Parallel(suitTrack, toonTrack)
    smokeTrack = getPartTrack(smoke, 2.45, 3.0, [smoke, suit, 0], softStop=-2)
    multiTrackList.append(cigarPropTrack)
    multiTrackList.append(smokeTrack)

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

    partDelay = 0.3
    partDuration = 2.15
    damageDelay = 1.25
    dodgeDelay = 0.7
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    sprayTracks = getPartTracks(attack, sprayEffects, partDelay, partDuration, 0, softStop=-1)
    sprayTracks2 = getPartTracks(attack, sprayEffects2, partDelay + 0.8, partDuration, 0, softStop=-1)
    sprayTracks3 = getPartTracks(attack, sprayEffects3, partDelay + 1.6, partDuration, 0, softStop=-1)
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
            sprayTracks.append(getPartTrack(sprayEffects4[i], partDelay, partDuration, [sprayEffects4[i], battle, 0]))

    suit.setHpr(battle, origHpr)
    damageAnims = []
    for i in xrange(0, 3):
        damageAnims.append(['cringe',
         1e-05,
         0.3,
         0.8])

    damageAnims.append(['cringe', 1e-05, 0.3])
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
     'schmooze-instant',
     'schmooze-master',
     'schmooze-viz']
    for i in xrange(0, 4):
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
    for i in xrange(0, 4):
        upperPartTracks.append(getPartTrack(upperEffects[i], partDelay + i * 0.65, 0.8, [upperEffects[i], suit, 0]))
        lowerPartTracks.append(getPartTrack(lowerEffects[i], partDelay + i * 0.65 + 0.7, 1.0, [lowerEffects[i], suit, 0]))

    damageAnims = []
    for i in xrange(0, 3):
        damageAnims.append(['conked',
         0.01,
         0.3,
         0.71])

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
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    tauntInterval = Sequence(Wait(1), Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(Wait(1), ActorInterval(suit, attack['animName']), Func(suit.setNeutralAnimation))
    suitPos = suit.getPos(battle)
    cagePropTracks = Parallel()
    cage = loader.loadModel('phase_3.5/models/modules/desk_only')
    card = globalPropPool.getProp('ttht_m_ene_techbotLaptop')
    propTrackNew = Parallel()
    laptopPosPoints = [Point3(-2, 1.5, 2.5), VBase3(0, 0, 0)]
    laptopDuration = 2.8
    scaleUpPoint = Point3(1.75, 1.75, 1.75)
    propTrackNew.append(
        getPropTrack(card, cage, laptopPosPoints, 1e-06, 2, scaleUpPoint=scaleUpPoint, scaleUpTime=0,
                     anim=1, animStartTime=0.5, animDuration=2.5,
                     propName='ttht_m_ene_techbotLaptop'))
    cagePos = [Point3(suitPos.getX() - 3, suitPos.getY() - 3, 0), suit.getHpr(battle)]
    cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, 0.01, scaleUpPoint=Point3(1.5), scaleUpTime=1),
            Parallel(
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/asfhdfha.ogg'), duration=0.75, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/asfhafhsdh.ogg'), node=cage),
            Wait(2.0),
            LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0),
            Func(MovieUtil.removeProp, cage)
        )

    cagePropTracks.append(cagePropTrack)
    soundTrack = getSoundTrack('tt_s_ara_cmg_itemHitsFloor.ogg', delay=1.5, node=suit)
    damageAnims = [['slip-backward']]
    dodgeAnims = [['jump']]
    toonTracks = getToonTracks(attack, damageDelay=1.5, splicedDamageAnims=damageAnims, dodgeDelay=1.0, splicedDodgeAnims=dodgeAnims)
    return Parallel(suitTrack, tauntInterval, cagePropTracks, propTrackNew, toonTracks, soundTrack)

def doDataCorruption(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    tauntInterval = Sequence(Wait(1), Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(Wait(1), ActorInterval(suit, attack['animName']), Func(suit.setNeutralAnimation))
    suitPos = suit.getPos(battle)
    cagePropTracks = Parallel()
    cage = loader.loadModel('phase_3.5/models/modules/desk_only')
    card = globalPropPool.getProp('ttht_m_ene_techbotLaptop')
    propTrackNew = Parallel()
    laptopPosPoints = [Point3(-2, 1.5, 2.5), VBase3(0, 0, 0)]
    laptopDuration = 2.8
    scaleUpPoint = Point3(1.75, 1.75, 1.75)
    propTrackNew.append(
        getPropTrack(card, cage, laptopPosPoints, 1e-06, 2, scaleUpPoint=scaleUpPoint, scaleUpTime=0,
                     anim=1, animStartTime=0.5, animDuration=2.5,
                     propName='ttht_m_ene_techbotLaptop'))
    cagePos = [Point3(suitPos.getX() - 3, suitPos.getY() - 3, 0), suit.getHpr(battle)]
    cagePropTrack = Sequence(
        getPropAppearTrack(cage, battle, cagePos, 0.01, scaleUpPoint=Point3(1.5), scaleUpTime=1),
        Parallel(
            SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/asfhdfha.ogg'), duration=0.75, node=cage)
        ),
        Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/asfhafhsdh.ogg'), node=cage),
        Wait(2.0),
        LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0),
        Func(MovieUtil.removeProp, cage)
    )

    cagePropTracks.append(cagePropTrack)
    damageAnims = [['cringe']]
    dodgeAnims = [['jump']]
    toonTracks = getToonTracks(attack, damageDelay=1.5, splicedDamageAnims=damageAnims, dodgeDelay=1.0,
                               splicedDodgeAnims=dodgeAnims)
    oldcolor = render.getColorScale()
    lightingTrack = Sequence(Wait(1), LerpColorScaleInterval(render, 0.5, (0, 0.992, 1, 1)),
                             LerpColorScaleInterval(render, 1.5, (0, 0.992, 1, 1)),
                             LerpColorScaleInterval(render, 1, (oldcolor)))
    return Parallel(suitTrack, tauntInterval, cagePropTracks, toonTracks, propTrackNew, lightingTrack)


def doHangUp(attack):
    suit = attack['suit']
    battle = attack['battle']
    phone = globalPropPool.getProp('phone')
    receiver = globalPropPool.getProp('receiver')
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    suitName = suit.getStyleName()
    phonePosPoints = [Point3(-0.23, 0, -0.11), VBase3(5.939, 2.763, -177.591)]
    receiverPosPoints = [Point3(-0.23, 0, -0.11), VBase3(5.939, 2.763, -177.591)]
    propTrack = Sequence(Func(__showProp, phone, suit.getLeftHand(), phonePosPoints[0], phonePosPoints[1]),
                         Func(__showProp, receiver, suit.getLeftHand(), receiverPosPoints[0], receiverPosPoints[1]),
                         LerpScaleInterval(phone, 0.5, MovieUtil.PNT3_ONE, MovieUtil.PNT3_NEARZERO), Wait(0.24),
                         Func(receiver.wrtReparentTo, suit.getRightHand()),
                         LerpPosHprInterval(receiver, 0.0001, Point3(-0.45, 0.48, -0.62), VBase3(-87.47, -18.21, 7.82)),
                         Wait(2.14), Func(receiver.wrtReparentTo, phone), Wait(0.62),
                         LerpScaleInterval(phone, 0.5, MovieUtil.PNT3_NEARZERO),
                         Func(MovieUtil.removeProps, [receiver, phone]))
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


def getThrowEndPoint(suit, toon, battle, whichBounce):
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
    check = globalPropPool.getProp('bounced-check')
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'c':
        checkPosPoints = [Point3(0, -0.5, 0), VBase3(-90, 90, 0)]
    else:
        checkPosPoints = [Point3(-0.25, -0.425, 0), VBase3(-180, 0, 0)]
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
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'c':
        checkPosPoints = [Point3(0, 0.5, -1), VBase3(-90, 90, 0)]
    else:
        checkPosPoints = [Point3(1.5, 0.65, 0), VBase3(-180, 0, 0)]
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
    toonTracks = getToonTracks(attack, damageDelay=suitTrack.getDuration() - 1.5, damageAnimNames=['cringe'], dodgeDelay=2.4, splicedDodgeAnims=dodgeAnims)
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
        baseFlameSmallTrack = getPartTrack(baseFlameSmall, 1.0, 3.9, [baseFlameSmall, toon, 0], softStop=-1)
        flameSmallTrack = getPartTrack(flameSmall, 1.0, 3.9, [flameSmall, toon, 0], softStop=-1)
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


def doAudit(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    calculator = globalPropPool.getProp('calculator')
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
        calcPosPoints = [Point3(-.85, 0.25, -0.1), VBase3(1.352, 0.0, 180.0)]
        calcDuration = 1.3
        scaleUpPoint = Point3(1.5, 1.5, 1.5)
    if suitType == 'b':
        calcPosPoints = [Point3(0, 0.25, -0.025), VBase3(1.352, 0.0, 180.0)]
        calcDuration = 1.3
        scaleUpPoint = Point3(1.5, 1.5, 1.5)
    if suitType == 'c':
        calcPosPoints = [Point3(0, 0.25, -0.025), VBase3(1.352, 0.0, 180.0)]
        calcDuration = 1.3
        scaleUpPoint = Point3(1.5, 1.5, 1.5)
    calcPropTrack = getPropTrack(calculator, suit.getLeftHand(), calcPosPoints, 0, calcDuration,
                                 scaleUpPoint=scaleUpPoint, scaleUpTime=0, anim=1, propName='calculator',
                                 animStartTime=0,
                                 animDuration=2.5)
    toonTracks = getToonTracks(attack, 2.6, ['conked'], 0.9, ['duck'], showMissedExtraTime=2.2)
    soundTrack = getSoundTrack('SA_audit.ogg', delay=1.3, node=suit)
    return Parallel(suitTrack, toonTracks, calcPropTrack, soundTrack, partTracks, partTracks2, partTracks3, partTracks4, partTracks5)


def doCalculate(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    calculator = globalPropPool.getProp('calculator')
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
        calcPosPoints = [Point3(-.85, 0.25, -0.1), VBase3(1.352, 0.0, 180.0)]
        calcDuration = 1.3
        scaleUpPoint = Point3(1.5, 1.5, 1.5)
    if suitType == 'b':
        calcPosPoints = [Point3(0, 0.25, -0.025), VBase3(1.352, 0.0, 180.0)]
        calcDuration = 1.3
        scaleUpPoint = Point3(1.5, 1.5, 1.5)
    if suitType == 'c':
        calcPosPoints = [Point3(0, 0.25, -0.025), VBase3(1.352, 0.0, 180.0)]
        calcDuration = 1.3
        scaleUpPoint = Point3(1.5, 1.5, 1.5)
    calcPropTrack = getPropTrack(calculator, suit.getLeftHand(), calcPosPoints, 0, calcDuration,
                                 scaleUpPoint=scaleUpPoint, scaleUpTime=0, anim=1, propName='calculator',
                                 animStartTime=0,
                                 animDuration=2.5)
    toonTracks = getToonTracks(attack, 2.6, ['conked'], 1.2, ['sidestep'])
    soundTrack = getSoundTrack('SA_calculate.ogg', delay=1.3, node=suit)
    return Parallel(suitTrack, toonTracks, calcPropTrack, soundTrack, partTracks, partTracks2, partTracks3, partTracks4, partTracks5)


def doTabulate(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    calculator = globalPropPool.getProp('calculator')
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
        calcPosPoints = [Point3(-.85, 0.25, -0.1), VBase3(1.352, 0.0, 180.0)]
        calcDuration = 1.3
        scaleUpPoint = Point3(1.5, 1.5, 1.5)
    if suitType == 'b':
        calcPosPoints = [Point3(0, 0.25, -0.025), VBase3(1.352, 0.0, 180.0)]
        calcDuration = 1.3
        scaleUpPoint = Point3(1.5, 1.5, 1.5)
    if suitType == 'c':
        calcPosPoints = [Point3(0, 0.25, -0.025), VBase3(1.352, 0.0, 180.0)]
        calcDuration = 1.3
        scaleUpPoint = Point3(1.5, 1.5, 1.5)
    calcPropTrack = getPropTrack(calculator, suit.getLeftHand(), calcPosPoints, 0, calcDuration,
                                 scaleUpPoint=scaleUpPoint, scaleUpTime=0, anim=1, propName='calculator',
                                 animStartTime=0,
                                 animDuration=2.5)
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
    damageAnims = [['melt'], ['jump', 1.5, 0.4]]
    for t in attack['target']:
        toon = t['toon']
        BattleParticles.loadParticles()
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
        cloudPropTrack.append(Wait(partDelay))
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
    cloudPropTrack.append(Wait(partDelay))
    cloudPropTrack.append(Parallel(Sequence(ParticleInterval(rainEffect, cloud, worldRelative=0, duration=3.1, cleanup=True, softStopT=-1)), Sequence(Wait(0.1), ParticleInterval(rainEffect2, cloud, worldRelative=0, duration=3.0, cleanup=True, softStopT=-1)), Sequence(Wait(0.1), ParticleInterval(rainEffect3, cloud, worldRelative=0, duration=3.0, cleanup=True, softStopT=-1)), Sequence(ActorInterval(cloud, 'stormcloud', startTime=3, duration=0.1), ActorInterval(cloud, 'stormcloud', startTime=1, duration=2.3))))
    cloudPropTrack.append(Wait(0.4))
    cloudPropTrack.append(LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO))
    cloudPropTrack.append(Func(MovieUtil.removeProp, cloud))
    cloudPropTrack.append(Func(battle.movie.clearRenderProp, cloud))
    damageAnims = [['melt'], ['jump', 1.5, 0.4]]
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_liquidate.ogg', delay=2.0, node=suit)
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
    posPoints = [Point3(-0.35, 0, 0), VBase3(90, 180, 0)]
    propTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        teeth = globalPropPool.getProp('teeth')
        teethAppearTrack = Sequence(getPropAppearTrack(teeth, suit.getRightHand(), posPoints, propDelay, Point3(4, 4, 4), scaleUpTime=propScaleUpTime))
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
    posPoints = [Point3(-0.35, 0, 0), VBase3(90, 180, 0)]
    propTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        teeth = globalPropPool.getProp('teeth')
        teethAppearTrack = Sequence(getPropAppearTrack(teeth, suit.getRightHand(), posPoints, propDelay, Point3(4, 4, 4),
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
    propTrackNew.append(getPropTrack(card, suit.getLeftHand(), laptopPosPoints, 1e-06, 2, scaleUpPoint=scaleUpPoint, scaleUpTime=0,
                                              anim=1, animStartTime=0.5, animDuration=2.5,
                                              propName='ttht_m_ene_techbotLaptop'))
    #calcPropTrack = getPropTrack(laptop, suit.getLeftHand(), laptopPosPoints, 1e-06, laptopDuration, scaleUpPoint=scaleUpPoint, anim=0, propName='laptop', animStartTime=0, animDuration=0)
    toonTracks = getToonTracks(attack, 2.8, splicedDamageAnims=damageAnims, dodgeDelay=2.8, dodgeAnimNames=['jump'])
    return Parallel(suitTrack, toonTracks, soundTrack, propTrackNew, partTracks, partTracks2, partTracks3, partTracks4, partTracks5)

def doEvictionNotice(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    posPoints = [Point3(0.375, -1.5, .85), VBase3(0, 220, -10)]
    propTracks = Parallel()
    for t in targets:
        toon = t['toon']
        paper = globalPropPool.getProp('shredder-paper')
        propTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.25, MovieUtil.PNT3_ONE, scaleUpTime=0.25))
        propTrack.append(Wait(1.55))
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

    toonTracks = getToonTracks(attack, 2, ['conked'], 2, ['jump'])
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
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    smoke = BattleParticles.createParticleEffect('Smoke')
    BattleParticles.setEffectTexture(smoke, 'snow-particle')
    cigar = globalPropPool.getProp('cigar')
    cigarPosPoints = [Point3(-0.05, -0.2, -0.25), VBase3(180.0, 0.0, 0.0)]
    cigarPropTrack = getPropTrack(cigar, suit.getRightHand(), cigarPosPoints, 1.5, 2,
                                  scaleUpPoint=Point3(6.0, 6.0, 6.0))
    toonTrack = getToonTrack(attack, 2.55, ['cringe'], 2.0, ['sidestep'])
    smokeTrack = getPartTrack(smoke, 2.45, 3.0, [smoke, suit, 0], softStop=-2)
    suitTracks = Parallel(getSuitTrack(attack), MovieUtil.createSuitHeadHonchoCigarSmokeInterval(suit))
    multiTrackList = Parallel(suitTracks, toonTrack, cigarPropTrack)
    multiTrackList.append(smokeTrack)

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

def doFirestarterCigarSmoke(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    tauntIndex = attack['taunt']
    toon = attack['target'][0]['toon']
    dmg = target[0]['hp']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    BattleParticles.loadParticles()
    smoke = BattleParticles.createParticleEffect('Smoke')
    BattleParticles.setEffectTexture(smoke, 'snow-particle')
    # cigar = globalPropPool.getProp('cigar')
    cigarPosPoints = [Point3(-0.05, -0.2, -0.25), VBase3(180.0, 0.0, 0.0)]
    # cigarPropTrack = getPropTrack(cigar, suit.getRightHand(), cigarPosPoints, 0.6, 3.6,
    # scaleUpPoint=Point3(6.0, 6.0, 6.0))
    toonTrack = getToonTrack(attack, 3.55, ['cringe'], 3.0, ['sidestep'])
    smokeTrack = getPartTrack(smoke, 3.45, 2.5, [smoke, suit, 0], softStop=-1)
    suitTracks = Parallel()
    multiTrackList = Parallel(suitTracks, toonTrack)
    multiTrackList.append(smokeTrack)
    tauntInterval = Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout)
    suitTrack = Sequence()
    suitTracks.append(suitTrack)
    suitTracks.append(tauntInterval)
    suitTracks.append(MovieUtil.createSuitFirestarterCigarSmokeInterval(suit))

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
        colorTrack.append(Wait(3.6))
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


def doFallingKnife(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = getSuitTrack(attack)
    posPoints = [Point3(-0.3, 0.4, 0.0), VBase3(0, 0, 90)]
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
        sparks.setPoolSize(10)
        sparks.setLitterSize(10)
        sparks.renderer.setEdgeColor(Vec4(1.0, 1.0, 1.0, 1.0))
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
            for i in xrange(0, 8):
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
                    Func(MovieUtil.removeProp, coin)
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
    chipTrack.append(Func(battle.movie.needRestoreRenderProp, chip))
    chipTrack.append(Func(chip.wrtReparentTo, battle))
    chipTrack.append(getThrowTrack(chip, hitPoint, duration=throwDuration, parent=battle, gravity=-64.288))
    chipTrack.append(Effects.createZBounce(chip, 3, movePoint, 0.5, 1.0))
    chipTrack.append(LerpPosInterval(chip, 0.4, movePoint))
    spinTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpHprInterval(chip, throwDuration, Point3(0, 810, 0)))
    #spinTrack2 = Sequence(Wait(propDelay + suitDelay + 1.45), LerpHprInterval(chip, throwDuration, Point3(0, 0, 90)))
    #bounceTrack2 = Sequence(Wait(propDelay + suitDelay + 1.45), Effects.createZBounce(chip, .25, hitPoint, 0.5, 1.5), Effects.createZBounce(chip, .25, hitPoint, 0.5, 1.5), Effects.createZBounce(chip, .25, hitPoint, 0.5, 1.5))
    sizeTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpScaleInterval(chip, throwDuration, Point3(6)), Wait(0.95), LerpScaleInterval(chip, 0.4, MovieUtil.PNT3_NEARZERO))
    propTrack = Sequence(Parallel(chipTrack, sizeTrack, spinTrack), Func(MovieUtil.removeProp, chip), Func(battle.movie.clearRenderProp, chip))
    propTracks.append(propTrack)
    soundTrack2 = getSoundTrack('toon_decompress.ogg', node=suit)
    toonTracks = getToonTrack(attack, 3.3, ['squish'], 2.0, ['sidestep'])
    squishTrack = Sequence(Wait(3.05), Func(toon.enterFlattened), Wait(2.0), Parallel(ActorInterval(toon, 'jump'), soundTrack2, Func(toon.loop, 'neutral'), Sequence(Wait(0.5), Func(toon.exitFlattened))))
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
        hitPoint.setY(hitPoint.getY() + 1.5)
        missPoint2 = toon.getPos(battle)
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
    damageDelay = 2.5
    dodgeDelay = 2.25
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    partTrack = getPartTrack(particleEffect, partDelay, 2.8, [particleEffect, suit, 0], softStop=-1)
    partTrack2 = getPartTrack(particleEffect2, partDelay, 2.8, [particleEffect2, suit, 0], softStop=-1)
    damageAnims = [['duck',
                    0.01,
                    0.4,
                    1.05], ['cringe', 1e-06, 0.8]]
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay,
                             splicedDodgeAnims=[['duck', 0.01, 1.4]], showMissedExtraTime=0.9, showDamageExtraTime=0.8)
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
            partTracks3.append(getPartTrack(particleEffect3, 2.25, 2.7, [particleEffect3, toon, 0], softStop=-1))
            partTracks4.append(getPartTrack(particleEffect4, 2.25, 2.7, [particleEffect4, toon, 0], softStop=-1))
            partTracks5.append(getPartTrack(particleEffect5, 2.25, 2.7, [particleEffect5, toon, 0], softStop=-1))

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
    posPoints = [Point3(0.375, -1.5, .85), VBase3(0, 220, -10)]
    propTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        paper = globalPropPool.getProp('shredder-paper')
        propTrack = Sequence(
            getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.5, MovieUtil.PNT3_ONE, scaleUpTime=0))
        propTrack.append(Wait(1.55))
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
    toonTracks = getToonTracks(attack, damageDelay=2.3, splicedDamageAnims=damageAnims, dodgeDelay=1.7, dodgeAnimNames=['sidestep'])
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
    posPoints = [Point3(0, 0, 0), VBase3(-90, 270, 90)]
    x = toon.getX(battle)
    y = toon.getY(battle)
    z = toon.getZ(battle)
    cagePosition = Parallel(LerpHprInterval(paper, 0.25, Point3(-90, 0, 0)), LerpScaleInterval(paper, 0.25, Point3(2, 2, 2)), LerpPosInterval(paper, 0.25, Point3(x, y + 15, z + 2)))
    cagePosition2 = Parallel(LerpPosInterval(paper, 0.25, Point3(x, y + 10, z + 2)))
    propTrack = Sequence(
        Parallel(Func(paper.play, 'ttht_m_ene_fileFolder'), getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.5, Point3(1.5, 1.5, 1.5), scaleUpTime=0.25)),
                 Wait(1.25), Func(paper.reparentTo, toon), cagePosition, Wait(1), cagePosition2)
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
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    sprayTracks = getPartTracks(attack, sprayEffects, 1.0, 1.9, 0)
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
            if dmg > 0:
                hitPoint = Point3(random.random() * 5 - 2.5, random.random() * 2 - 1 - 6,
                                  random.random() * 3 - 1.5 + toon.getHeight() - 0.9)
            else:
                hitPoint = Point3(random.random() * 2 - 1, random.random() * 4 - 2 - 15, random.random() * 4 - 2 + 2.2)
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
