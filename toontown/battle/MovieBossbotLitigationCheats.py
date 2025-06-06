from toontown.battle import MovieCamera
from toontown.battle import MovieUtil
from toontown.battle import BattleParticles
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from direct.particles import ParticleEffect
from toontown.battle.BattleBase import *
from toontown.battle.BattleBase import *
import PlayByPlayText
from direct.showutil import Effects
from toontown.battle import SuitBattleGlobals
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
    name = attack['id']
    suit = attack['suit']
    if name == ACID_RAIN:
        suitTrack = doAcidRain(attack)
    elif name == AUDIT:
        suitTrack = doAudit(attack)
    elif name == BASH:
        suitTrack = doBash(attack)
    elif name == BEGUILE:
        suitTrack = doTeeOffGroup(attack)
    elif name == CLOSE_THE_LOOP:
        suitTrack = doFountainPenBindings(attack)
    elif name == HOSTILE_TAKEOVER:
        suitTrack = doHostileTakeoverNew(attack)
    elif name == NICKEL_AND_DIME:
        suitTrack = doRolledTrickOfTheLight(attack)
    elif name == QUASH:
        suitTrack = doAceInTheHoleNew(attack)
    elif name == MULLIGAN:
        suitTrack = doTeeOff2(attack)
    elif name == PENNY_PINCH:
        suitTrack = doPickPocket(attack)
    elif name == DISASSEMBLE:
        suitTrack = doDisassemble(attack)
    elif name == DATA_CORRUPTION:
        suitTrack = doDataCorruption(attack)
    elif name == DATA_BREACH:
        suitTrack = doDataBreach(attack)
    elif name == VERSION_CONTROL:
        suitTrack = doVersionControl(attack)
    elif name == DENIAL_OF_SERVICE:
        suitTrack = doDenialOfService(attack)
    elif name == OVERLOAD:
        suitTrack = doOverload(attack)
    elif name == BREAKTHROUGH:
        suitTrack = doBreakthrough(attack)
    elif name == ENCRYPT:
        suitTrack = doEncrypt(attack)
    elif name == BOUNCE_RATE:
        suitTrack = doBounceRate(attack)
    elif name == REPROGRAM:
        suitTrack = doReprogram(attack)
    elif name == CLOUD_STORAGE:
        suitTrack = doCloudStorage(attack)
    elif name == DISK_SCRATCH:
        suitTrack = doDiskScratch(attack)
    elif name == VOODOO_MAGIC:
        suitTrack = doVoodooMagic(attack)
    elif name == ELECTROSTATIC_ENERGY:
        suitTrack = doElectrostaticEnergy(attack)
    elif name == BITE:
        suitTrack = doBite(attack)
    elif name == BOUNCE_CHECK:
        suitTrack = doBounceCheck(attack)
    elif name == BRAIN_STORM:
        suitTrack = doBrainStorm(attack)
    elif name == BUZZ_WORD:
        suitTrack = doBuzzWord(attack)
    elif name == CALCULATE:
        suitTrack = doCalculate(attack)
    elif name == ENRAGED:
        suitTrack = doQuakeEnraged(attack)
    elif name == CANNED:
        suitTrack = doCanned(attack)
    elif name == FREE_CRUISE:
        suitTrack = doOceanliner(attack)
    elif name == SPOTLIGHT:
        suitTrack = doSpotlight(attack)
    elif name == DICE_ROULETTE:
        suitTrack = doDiceRoulette(attack)
    elif name == CONDUCTION:
        suitTrack = doConDuckTion(attack)
    elif name == REFINEMENT:
        suitTrack = doTeeOffRefinement(attack)
    elif name == EXTRA_TIP:
        suitTrack = doPowerTripBayouBash(attack)
    elif name == WORKERS_COMPENSATION:
        suitTrack = doWorkersCompensation(attack)
    elif name == COURT_MANDATE:
        suitTrack = doPowerTripScabbard(attack)
    elif name == COURT_MANDATE_1:
        suitTrack = doLiquidateSoakResist(attack)
    elif name == COURT_MANDATE_2:
        suitTrack = doFallingKnifeSyphon(attack)
    elif name == COURT_MANDATE_3:
        suitTrack = doFallingKnifeSyphon(attack)
    elif name == EVICTION_NOTICE:
        suitTrack = doEvictionNotice(attack)
    elif name == CHOMP:
        suitTrack = doChomp(attack)
    elif name == LD_QUAKE:
        suitTrack = doWheelSpinDiceRoulette(attack)
    elif name == SNAP_WET:
        suitTrack = doThrowBookSnap(attack)
    elif name == BLACK_ORB or name == WATERCOOLER:
        suitTrack = doWatercooler(attack)
    elif name == CIGAR_SMOKE:
        suitTrack = doCigarSmoke(attack)
    elif name == CHAINSAW_CANNED:
        suitTrack = doBlueChipSnipe(attack)
    elif name == CLOCK_CHANGE:
        suitTrack = doClockChange(attack)
    elif name == WHITE_POWDER:
        suitTrack = doChompBellow(attack)
    elif name == CLIPON_TIE:
        suitTrack = doClipOnTie(attack)
    elif name == LEGAL_BINDINGS:
        suitTrack = doRolodexBindings(attack)
    elif name == NOT_THROW_PIANO:
        suitTrack = doCloseTheLoopPiano(attack)
    elif name == THROW_MONEY:
        suitTrack = doThrowMoney(attack)
    elif name == AMANDAS_DOUGHNUTS:
        suitTrack = doAmandasDoughnuts(attack)
    elif name == GAVEL:
        suitTrack = doBiteGavel(attack)
    elif name == BOMB_CAKE:
        suitTrack = doCloseTheLoopBombCake(attack)
    elif name == BOMB:
        suitTrack = doRazzleDazzleBomb(attack)
    elif name == CRUNCH:
        suitTrack = doCrunch(attack)
    elif name == DEMOTION:
        suitTrack = doDemotion(attack)
    elif name == DOUBLE_TALK:
        suitTrack = doDoubleTalk(attack)
    elif name == DOUBLE_WINDSOR:
        suitTrack = doDoubleWindsor(attack)
    elif name == DOWNSIZE:
        suitTrack = doDownsize(attack)
    elif name == EVICTION_NOTICE:
        suitTrack = doEvictionNotice(attack)
    elif name == INSURANCE_PLAN:
        suitTrack = doEvictionNoticeInsurance(attack)
    elif name == LD_EVICTION_NOTICE:
        suitTrack = doWheelSpinDiceRoulette(attack)
    elif name == EVIL_EYE:
        suitTrack = doEvilEye(attack)
    elif name == FILIBUSTER:
        suitTrack = doFilibuster(attack)
    elif name == FILL_WITH_LEAD:
        suitTrack = doFillWithLead(attack)
    elif name == FINGER_WAG:
        suitTrack = doFingerWag(attack)
    elif name == FIRED:
        suitTrack = doFired(attack)
    elif name == FIVE_O_CLOCK_SHADOW:
        suitTrack = doDefault(attack)
    #elif name == FLOOD_THE_MARKET:
        #suitTrack = doDefault(attack)
    elif name == FOUNTAIN_PEN:
        suitTrack = doFountainPen(attack)
    elif name == FREEZE_ASSETS:
        suitTrack = doFreezeAssets(attack)
    elif name == GLOWER_POWER:
        suitTrack = doGlowerPower(attack)
    elif name == CHAINSAW_GLOWER_POWER:
        suitTrack = doGlowerPowerCTS(attack)
    elif name == WATER_SPRAY:
        suitTrack = doWaterSpray(attack)
    elif name == PECKING_ORDER_WSI:
        suitTrack = doPeckingOrder(attack)
    elif name == POWER_TRIP_WSI:
        suitTrack = doPowerTrip(attack)
    elif name == CHAINSAW_QUAKE:
        suitTrack = doQuakeLayoffs(attack)
    elif name == MP_QUAKE:
        suitTrack = doShortSqueezeWritingDesk(attack)
    elif name == REARRANGE:
        suitTrack = doFilibusterPhase2(attack)
    elif name == MP_SONG_AND_DANCE:
        suitTrack = doMeaningfulConversation(attack)
    elif name == INK_DRAIN:
        suitTrack = doCaress(attack)
    elif name == BAR:
        suitTrack = doBarNew(attack)
    elif name == WHEEL_SPIN:
        suitTrack = doWheelSpin(attack)
    elif name == ACCUSATIONS:
        suitTrack = doCloseTheLoopNew(attack)
    elif name == ACCUSATIONS_2:
        suitTrack = doOilRainDerrickHand(attack)
    elif name == SNAP: #soaked snap
        suitTrack = doFiredSnap(attack)
    elif name == GAME_SHOW:
        suitTrack = doWheelSpin2(attack)
    elif name == DUCK_SPIN:
        suitTrack = doSpin(attack)
    elif name == MOB_MENTALITY:
        suitTrack = doMobMentality(attack)
    elif name == USURY:
        suitTrack = doGlowerPowerSparkplug(attack)
    elif name == USURY_2:
        suitTrack = doCannedScabbard(attack)
    elif name == TRIBUTE_2:
        suitTrack = doTeeOffTrap(attack)
    elif name == SLUSHFUND_2:
        suitTrack = doPinkSlipSnipe(attack)
    elif name == SHAKEDOWN:
        suitTrack = doBounceCheckPecking(attack)
    elif name == SHAKEDOWN_2:
        suitTrack = doPeckingOrderSlushFund(attack)
    elif name == STAND_UP_GUY:
        suitTrack = doCloseTheLoopPhase2(attack)
    elif name == KICK_UP:
        suitTrack = doMarketCrashPecking(attack)
    elif name == SITDOWN:
        suitTrack = doCalculateStocks(attack)
    elif name == QUALITY_CONTROL_GAG:
        suitTrack = doWheelSpinCheat1(attack)
    elif name == QUALITY_CONTROL_GAG_1:
        suitTrack = doWheelSpinCheat2(attack)
    elif name == QUALITY_CONTROL_GAG_2:
        suitTrack = doWheelSpinCheat3(attack)
    elif name == QUALITY_CONTROL_GAG_3:
        suitTrack = doWheelSpinCheat4(attack)
    elif name == QUALITY_CONTROL_LEVEL:
        suitTrack = doFreezeAssetsAftershock(attack) #inversion
    elif name == QUALITY_CONTROL_LEVEL_1:
        suitTrack = doSchmoozeRadioInfrequency(attack) #radio infrequency to ban squirt
    elif name == QUALITY_CONTROL_LEVEL_2:
        suitTrack = doGlowerPowerContractEnforcement(attack) #insurance plan union buster
    elif name == QUALITY_CONTROL_LEVEL_3:
        suitTrack = doEvilEyeBreachOfContract(attack) #breach of contract
    elif name == MANAGERIAL_PROTECTION:
        suitTrack = doCloseTheLoopNew(attack)
    elif name == RADIO_INFREQUENCY:
        suitTrack = doSongAndDanceRadioInfrequency(attack)
    elif name == VOICEMAIL:
        suitTrack = doFilibusterVoicemail(attack)
    elif name == WIRE_CUT:
        suitTrack = doThrowBookWireCut(attack)
    elif name == PAPER_CUT:
        suitTrack = doCigarSmokePaperCut(attack)
    elif name == EXPLODING_BILL:
        suitTrack = doEvictionNoticeExplodingBill(attack)
    elif name == FIRE_COG:
        suitTrack = doDoubleTalkWhirlwind(attack)
    elif name == GOOD_MORNING_TOONTOWN:
        suitTrack = doStealSafeMulti(attack)
    elif name == CARESS:
        suitTrack = doBlueChipSnipe(attack)
    elif name == COLLECT_CALL_FEES:
        suitTrack = doCollectCallCalculations(attack)
    elif name == COLLECT_CALL:
        suitTrack = doFilibusterCollectCall(attack)
    elif name == SLUSH_FUND:
        suitTrack = doSlushFund(attack)
    elif name == JURY_NOTICE:
        suitTrack = doConDuckTionVulnerable(attack)
    elif name == CEASE_AND_DESIST:
        suitTrack = doMumboJumboSanction(attack)
    elif name == INVESTMENT:
        suitTrack = doPowerTripKamikaze(attack)
    elif name == FIELD_PROMOTION:
        suitTrack = doRolled(attack)
    elif name == WIRETAPPED:
        suitTrack = doParadigmShiftWiretapped(attack)
    elif name == SHORT_SQUEEZE:
        suitTrack = doShortSqueeze(attack)
    elif name == BLUE_CHIP:
        suitTrack = doBlueChip(attack)
    elif name == FALLING_KNIFE:
        suitTrack = doFallingKnife(attack)
    elif name == LD_AFTERSHOCK:
        suitTrack = doWheelSpinDiceRoulette(attack)
    elif name == LIFE_INSURANCE:
        suitTrack = doLifeInsurance(attack)
    elif name == LD_RED_TAPE:
        suitTrack = doWheelSpinDiceRoulette(attack)
    elif name == LD_RE_ORG:
        suitTrack = doWheelSpinDiceRoulette(attack)
    elif name == MP_HOT_AIR:
        suitTrack = doWriteOffWritingDesk(attack)
    elif name == HR_POWER_TRIP:
        suitTrack = doPowerTrip(attack)
    elif name == POISON_SPRAY:
        suitTrack = doParadigmShiftScapegoat(attack)
    elif name == GUILT_TRIP:
        suitTrack = doGuiltTrip(attack)
    elif name == STEAL_SAFE:
        suitTrack = doStealSafe(attack)
    elif name == COURT_SANCTION:
        suitTrack = doPoundKeySanction(attack)
    elif name == OIL_RAIN:
        suitTrack = doPowerTripOilRain(attack)
    elif name == EMBEZZLE:
        suitTrack = doEmbezzle(attack)
    elif name == FLOOD_THE_MARKET:
        suitTrack = doFloodTheMarket(attack)
    elif name == CAGE:
        suitTrack = doPinkSlipCage(attack)
    elif name == CHAINSAW_REVVING_UP:
        suitTrack = doGlowerPowerPhase3(attack)
    elif name == DETONATE:
        suitTrack = doRolodexAggrandized(attack)
    elif name == DETONATE_2:
        suitTrack = doPinkSlipAftershock(attack)
    elif name == DETONATE_3:
        suitTrack = doCloseTheLoopNew(attack)
    elif name == HEAD_ROLLER:
        if suit.dna.name == 'crf':
            suitTrack = doBayouBash2(attack)
        else:
            suitTrack = doFallingKnifeHeadRoller(attack)
    elif name == HEAD_ROLLER_2:
        if suit.dna.name == 'crf':
            suitTrack = doBayouBash2(attack)
        else:
            suitTrack = doBrainStormHeadRoller(attack)
    elif name == HEAD_ROLLER_3:
        if suit.dna.name == 'crf':
            suitTrack = doHeadRollerHighRoller(attack, 4)
        else:
            suitTrack = doBlueChipHeadRoller(attack)
    elif name == UNION_BUST:
        suitTrack = doReOrgUnionBust(attack)
    elif name == UNION_BUST_2:
        suitTrack = doFallingKnifeUnionBust(attack)
    elif name == UNION_BUST_3:
        suitTrack = doHostileTakeoverUnionBust(attack)
    elif name == CHAINSAW_DETONATE:
        suitTrack = doCannedOffboarding(attack)
    elif name == CHAINSAW_DETONATE_2:
        suitTrack = doRolodexMarkedWood(attack)
    elif name == CHAINSAW_DETONATE_3:
        suitTrack = doFallingKnifePromotion(attack)
    elif name == GUILT_TRIP_WSI:
        suitTrack = doGuiltTrip(attack)
    elif name == MONEY_TRIP:
        suitTrack = doSynergy(attack)
    elif name == UNION_DUES:
        suitTrack = doUnionCalculations(attack)
    elif name == UNION_BUSTER:
        suitTrack = doFallingKnifeUnionBuster(attack)
    elif name == EVIL_EYE_WSI:
        suitTrack = doTeeOffHeal(attack)
    elif name == COURT_RECORD_1:
        suitTrack = doSnipeHighRoller(attack)
    elif name == COURT_RECORD_2:
        suitTrack = doSnipeHighRoller(attack)
    elif name == COURT_RECORD_3:
        suitTrack = doSnipeHighRoller(attack)
    elif name == COURT_RECORD_4:
        suitTrack = doMumboJumboSanction(attack)
    elif name == COURT_RECORD_5:
        suitTrack = doWiretappedHighRoller(attack)
    elif name == BOOKKEEPING:
        suitTrack = doRolodexBookKeeping(attack)
    elif name == HALF_WINDSOR:
        suitTrack = doHalfWindsor(attack)
    elif name == HANG_UP:
        suitTrack = doHangUp(attack)
    elif name == HEAD_SHRINK:
        suitTrack = doHeadShrink(attack)
    elif name == HOT_AIR:
        suitTrack = doHotAir(attack)
    elif name == JARGON:
        suitTrack = doJargon(attack)
    elif name == RESTRAINING_ORDER_WSI:
        suitTrack = doRestrainingOrder(attack)
    elif name == RAISING_THE_ANTE:
        suitTrack = doRaisingTheAnte(attack)
    elif name == SWIRL_BATH:
        suitTrack = doWheelSpinCheat5(attack, 1, 2, 3, 4, 5)
    elif name == LEGALESE:
        suitTrack = doLegalese(attack)
    elif name == COURT_COSTS:
        suitTrack = doCourtCalculations(attack)
    elif name == LAW_BOOK:
        suitTrack = doThrowBook(attack)
    elif name == SNOW:
        suitTrack = doShieldsUp(attack)
    elif name == HEAT_WAVE:
        suitTrack = doHeatWaveCalculations(attack)
    elif name == LIQUIDATE:
        suitTrack = doLiquidate(attack)
    elif name == MARKET_CRASH:
        suitTrack = doMarketCrash(attack)
    elif name == MUMBO_JUMBO:
        suitTrack = doMumboJumbo(attack)
    elif name == PARADIGM_SHIFT:
        suitTrack = doParadigmShift(attack)
    elif name == PECKING_ORDER:
        suitTrack = doPeckingOrder(attack)
    elif name == PICK_POCKET:
        suitTrack = doPickPocket(attack)
    elif name == PINK_SLIP:
        suitTrack = doPinkSlip(attack)
    elif name == PLAY_HARDBALL:
        suitTrack = doPlayHardball(attack)
    elif name == POUND_KEY:
        suitTrack = doPoundKey(attack)
    elif name == POWER_TIE:
        suitTrack = doPowerTie(attack)
    elif name == POWER_TRIP:
        suitTrack = doPowerTrip(attack)
    elif name == CONE_OF_SHAME:
        suitTrack = doFiredConeOfShame(attack)
    elif name == QUAKE:
        suitTrack = doQuake(attack)
    elif name == RAZZLE_DAZZLE:
        suitTrack = doRazzleDazzle(attack)
    elif name == RED_TAPE:
        suitTrack = doRedTape(attack)
    elif name == DROWNING:
        suitTrack = doReOrgBreachOfContract(attack)
    elif name == HEAVY_RAINFALL:
        suitTrack = doPowerTripHeavyRainfall(attack)
    elif name == AFTERSHOCK:
        suitTrack = doLiquidateAftershock(attack)
    elif name == FREEZING_RAIN:
        suitTrack = doParadigmShiftFreezingRain(attack)
    elif name == RE_ORG:
        suitTrack = doReOrg(attack)
    elif name == HYPNO_EYES:
        suitTrack = doHypnoEyes(attack)
    elif name == RESTRAINING_ORDER:
        suitTrack = doRestrainingOrder(attack)
    elif name == ROLODEX:
        suitTrack = doRolodex(attack)
    elif name == RUBBER_STAMP:
        suitTrack = doRubberStamp(attack)
    elif name == RUB_OUT:
        suitTrack = doRubOut(attack)
    elif name == SACKED:
        suitTrack = doSacked(attack)
    elif name == SANDTRAP:
        suitTrack = doDefault(attack)
    elif name == SCHMOOZE:
        suitTrack = doSchmooze(attack)
    elif name == SHAKE:
        suitTrack = doShake(attack)
    elif name == INJECT:
        suitTrack = doInject(attack)
    elif name == SHRED:
        suitTrack = doShred(attack)
    elif name == SONG_AND_DANCE:
        suitTrack = doSongAndDance(attack)
    elif name == CHAINSAW_ROLODEX:
        suitTrack = doCannedPhase2(attack)
    elif name == RESTRAINING_ORDER_WSI:
        suitTrack = doRestrainingOrder(attack)
    elif name == BLAST:
        suitTrack = doPowerTripBlast(attack)
    elif name == SPIN:
        suitTrack = doSpin(attack)
    elif name == SYNERGY:
        suitTrack = doInterestCalculations(attack)
    elif name == TABULATE:
        suitTrack = doTabulate(attack)
    elif name == TEE_OFF:
        suitTrack = doTeeOff(attack)
    elif name == THROW_BOOK:
        suitTrack = doThrowBook(attack)
    elif name == TREMOR:
        suitTrack = doTremor(attack)
    elif name == SNOW_BALLS:
        suitTrack = doSnowBalls(attack)
    elif name == FIRE_BALLS:
        suitTrack = doFireBalls(attack)
    elif name == WITHDRAWAL:
        suitTrack = doWithdrawal(attack)
    elif name == WRITE_OFF:
        suitTrack = doWriteOff(attack)
    #litigator cheats
    elif name == LITIGATOR_SNAP_SOAK:
        suitTrack = doSnap(attack, suit)
    elif name == LITIGATOR_SNAP:
        suitTrack = doSnap(attack, suit)
    elif name == LITIGATOR_BAYOU_BASH:
        suitTrack = doBayouBash(attack)
    elif name == LITIGATOR_BAYOU_BELLOW:
        suitTrack = doBayouBellow(attack)
    #stenographer cheats
    elif name == STENOGRAPHER_SANCTION_BINDINGS:
        suitTrack = doCourtSanction(attack, suit)
    elif name == STENOGRAPHER_SANCTION:
        suitTrack = doCourtSanction(attack, suit)
    #case manager cheats
    elif name == CASE_MANAGER_INSURANCE_PLAN:
        if not suit.isSkeleton:
            suitTrack = doCaseInsurancePlanInsurance(attack)
        else:
            suitTrack = doCaseInsurancePlanSkelecogInsurance(attack)
    elif name == CASE_MANAGER_LEGAL_BINDINGS:
        suitTrack = doLegalBindings(attack)
    #scapegoat cheats
    elif name == SCAPEGOAT_SHIELDS_UP:
        suitTrack = doShieldsUp(attack)
    elif name == SCAPEGOAT_ENRAGED:
        suitTrack = doEnraged(attack)
    elif name == SCAPEGOAT_GAVEL:
        suitTrack = doGavel(attack)
    elif name == SCAPEGOAT_BARNYARD_BASH:
        suitTrack = doBarnyardBash(attack)
    #universal cheats
    elif name == SYNERGY_FEES:
        suitTrack = doSynergy(attack)
    elif name == CALCULATING_FEES:
        suitTrack = doCourtCalculations(attack)
    elif name == BAN_LEVEL_4:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_LEVEL_5:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_LEVEL_6:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_LEVEL_7:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_LEVEL_8:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_LEVEL_4_5:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_LEVEL_4_6:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_LEVEL_4_7:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_LEVEL_4_8:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_LEVEL_5_6:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_LEVEL_5_7:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_LEVEL_5_8:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_LEVEL_6_7:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_LEVEL_6_8:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_LEVEL_7_8:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_TOONUP:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_TRAP:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_LURE:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_THROW:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_SQUIRT:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_ZAP:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_SOUND:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_DROP:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_TOONUP_TRAP:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_TOONUP_LURE:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_TOONUP_THROW:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_TOONUP_SQUIRT:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_TOONUP_ZAP:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_TOONUP_SOUND:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_TOONUP_DROP:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_TRAP_LURE:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_TRAP_THROW:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_TRAP_SQUIRT:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_TRAP_ZAP:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_TRAP_SOUND:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_TRAP_DROP:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_LURE_THROW:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_LURE_SQUIRT:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_LURE_ZAP:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_LURE_SOUND:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_LURE_DROP:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_THROW_SQUIRT:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_THROW_ZAP:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_THROW_SOUND:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_THROW_DROP:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_SQUIRT_ZAP:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_SQUIRT_SOUND:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_SQUIRT_DROP:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_ZAP_SOUND:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_ZAP_DROP:
        suitTrack = doCourtRecord(attack)
    elif name == BAN_SOUND_DROP:
        suitTrack = doCourtRecord(attack)
    else:
        notify.warning('unknown attack: %d substituting Finger Wag' % name)
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
    if suit.dna.name == 'scg' and suit.isAngry:
        neutralIval =  Func(suit.loop, 'neutral-enraged')
        preWalkTrack = ActorInterval(suit, 'neutral-enraged-return')
    elif name == FREE_CRUISE:
        neutralIval = Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
        preWalkTrack = Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
    elif name == CONDUCTION:
        neutralIval = Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
        preWalkTrack = Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
    elif name == LD_QUAKE:
        neutralIval = Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
        preWalkTrack = Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
    elif name == LD_EVICTION_NOTICE:
        neutralIval = Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
        preWalkTrack = Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
    elif name == LD_AFTERSHOCK:
        neutralIval = Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
        preWalkTrack = Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
    elif name == LD_RED_TAPE:
        neutralIval = Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
        preWalkTrack = Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
    elif name == LD_RE_ORG:
        neutralIval = Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
        preWalkTrack = Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
    elif name == JURY_NOTICE:
        neutralIval = Func(suit.loop, 'neutral2%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
        preWalkTrack = Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
    elif name == NICKEL_AND_DIME:
        neutralIval = Func(suit.loop, 'highroller-neutral-levitate-loop')
        preWalkTrack = Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
    elif name == BEGUILE:
        neutralIval = Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
        preWalkTrack = Func(suit.loop,
                            'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
    elif suit.isImmortal and suit.dna.name == 'dsf':
        neutralIval = Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
        preWalkTrack = Func(suit.loop,
                            'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
    else:
        neutralIval =  Func(suit.setNeutralAnimation)
        preWalkTrack = Func(suit.setNeutralAnimation)
    unlureSuit = Func(suit.makeUnLured)
    suitTrack = Sequence(unlureSuit, preWalkTrack, suitTrack, neutralIval, toonHprTrack)
    suitPos = suit.getPos(battle)
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    resetTrack = getResetTrack(suit, battle)
    resetSuitTrack = Sequence(unlureSuit, resetTrack, suitTrack)
    waitTrack = Sequence(Wait(resetTrack.getDuration()), Func(battle.unlureSuit, suit))
    resetCamTrack = Sequence(camTrack)
    return resetCamTrack


def getResetTrack(suit, battle):
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    moveDist = Vec3(suit.getPos(battle) - resetPos).length()
    moveDuration = 0.5
    updateTrack = Parallel(Func(suit.setChatAbsolute,
                                '',
                                CFSpeech | CFTimeout))
    unluredTrack = Func(battle.unlureSuit, suit)
    walkTrack = Sequence(Func(suit.setHpr, battle, resetHpr), ActorInterval(suit, 'walk', startTime=1, duration=moveDuration, endTime=1e-05), (Func(suit.loop,  'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))))
    moveTrack = LerpPosInterval(suit, moveDuration, resetPos, other=battle)
    return Parallel(unluredTrack, updateTrack, walkTrack, moveTrack)


def __makeCancelledNodePath():
    tn = TextNode('CANCELLED')
    tn.setFont(getSuitFont())
    tn.setText(TTLocalizer.MovieSuitCancelled)
    tn.setAlign(TextNode.ACenter)
    tntop = hidden.attachNewNode('CancelledTop')
    tnpath = tntop.attachNewNode(tn)
    tnpath.setPosHpr(0, 0, 0, 0, 0, 0)
    tnpath.setScale(1)
    tnpath.setColor(0.7, 0, 0, 1)
    tnpathback = tnpath.instanceUnderNode(tntop, 'backside')
    tnpathback.setPosHpr(0, 0, 0, 180, 0, 0)
    tnpath.setScale(1)
    return tntop


def doDefault(attack):
    notify.debug('building suit attack in doDefault')
    suitName = attack['suitName']
    if suitName == 'f':
        attack['id'] = POUND_KEY
        attack['name'] = 'PoundKey'
        attack['animName'] = 'phone'
        return doPoundKey(attack)
    elif suitName == 'p':
        attack['id'] = FOUNTAIN_PEN
        attack['name'] = 'FountainPen'
        attack['animName'] = 'pen-squirt'
        return doFountainPen(attack)
    elif suitName == 'ym':
        attack['id'] = RUBBER_STAMP
        attack['name'] = 'RubberStamp'
        attack['animName'] = 'rubber-stamp'
        return doRubberStamp(attack)
    elif suitName == 'mm':
        attack['id'] = FINGER_WAG
        attack['name'] = 'FingerWag'
        attack['animName'] = 'finger-wag'
        return doFingerWag(attack)
    elif suitName == 'ds':
        attack['id'] = DEMOTION
        attack['name'] = 'Demotion'
        attack['animName'] = 'magic1'
        return doDemotion(attack)
    elif suitName == 'hh':
        attack['id'] = GLOWER_POWER
        attack['name'] = 'GlowerPower'
        attack['animName'] = 'glower'
        return doGlowerPower(attack)
    elif suitName == 'cr':
        attack['id'] = PICK_POCKET
        attack['name'] = 'PickPocket'
        attack['animName'] = 'pickpocket'
        return doPickPocket(attack)
    elif suitName == 'tbc':
        attack['id'] = GLOWER_POWER
        attack['name'] = 'GlowerPower'
        attack['animName'] = 'glower'
        return doGlowerPower(attack)
    elif suitName == 'cc':
        attack['id'] = POUND_KEY
        attack['name'] = 'PoundKey'
        attack['animName'] = 'phone'
        return doPoundKey(attack)
    elif suitName == 'tm':
        attack['id'] = CLIPON_TIE
        attack['name'] = 'ClipOnTie'
        attack['animName'] = 'throw-paper'
        return doClipOnTie(attack)
    elif suitName == 'nd':
        attack['id'] = PICK_POCKET
        attack['name'] = 'PickPocket'
        attack['animName'] = 'pickpocket'
        return doPickPocket(attack)
    elif suitName == 'gh':
        attack['id'] = FOUNTAIN_PEN
        attack['name'] = 'FountainPen'
        attack['animName'] = 'pen-squirt'
        return doFountainPen(attack)
    elif suitName == 'ms':
        attack['id'] = BRAIN_STORM
        attack['name'] = 'BrainStorm'
        attack['animName'] = 'effort'
        return doBrainStorm(attack)
    elif suitName == 'tf':
        attack['id'] = RED_TAPE
        attack['name'] = 'RedTape'
        attack['animName'] = 'throw-object'
        return doRedTape(attack)
    elif suitName == 'm':
        attack['id'] = BUZZ_WORD
        attack['name'] = 'BuzzWord'
        attack['animName'] = 'speak'
        return doBuzzWord(attack)
    elif suitName == 'mh':
        attack['id'] = RAZZLE_DAZZLE
        attack['name'] = 'RazzleDazzle'
        attack['animName'] = 'smile'
        return doRazzleDazzle(attack)
    elif suitName == 'sc':
        attack['id'] = WATERCOOLER
        attack['name'] = 'Watercooler'
        attack['animName'] = 'water-cooler'
        return doWatercooler(attack)
    elif suitName == 'pp':
        attack['id'] = BOUNCE_CHECK
        attack['name'] = 'BounceCheck'
        attack['animName'] = 'throw-paper'
        return doBounceCheck(attack)
    elif suitName == 'tw':
        attack['id'] = GLOWER_POWER
        attack['name'] = 'GlowerPower'
        attack['animName'] = 'glower'
        return doGlowerPower(attack)
    elif suitName == 'bc':
        attack['id'] = AUDIT
        attack['name'] = 'Audit'
        attack['animName'] = 'phone'
        return doAudit(attack)
    elif suitName == 'nc':
        attack['id'] = RED_TAPE
        attack['name'] = 'RedTape'
        attack['animName'] = 'throw-object'
        return doRedTape(attack)
    elif suitName == 'mb':
        attack['id'] = LIQUIDATE
        attack['name'] = 'Liquidate'
        attack['animName'] = 'magic1'
        return doLiquidate(attack)
    elif suitName == 'ls':
        attack['id'] = WRITE_OFF
        attack['name'] = 'WriteOff'
        attack['animName'] = 'hold-pencil'
        return doWriteOff(attack)
    elif suitName == 'rb':
        attack['id'] = TEE_OFF
        attack['name'] = 'TeeOff'
        attack['animName'] = 'golf-club-swing'
        return doTeeOff(attack)
    elif suitName == 'bf':
        attack['id'] = RUBBER_STAMP
        attack['name'] = 'RubberStamp'
        attack['animName'] = 'rubber-stamp'
        return doRubberStamp(attack)
    elif suitName == 'b':
        attack['id'] = EVICTION_NOTICE
        attack['name'] = 'EvictionNotice'
        attack['animName'] = 'throw-paper'
        return doEvictionNotice(attack)
    elif suitName == 'dt':
        attack['id'] = RUBBER_STAMP
        attack['name'] = 'RubberStamp'
        attack['animName'] = 'rubber-stamp'
        return doRubberStamp(attack)
    elif suitName == 'ac':
        attack['id'] = RED_TAPE
        attack['name'] = 'RedTape'
        attack['animName'] = 'throw-object'
        return doRedTape(attack)
    elif suitName == 'bs':
        attack['id'] = FINGER_WAG
        attack['name'] = 'FingerWag'
        attack['animName'] = 'finger-wag'
        return doFingerWag(attack)
    elif suitName == 'sd':
        attack['id'] = WRITE_OFF
        attack['name'] = 'WriteOff'
        attack['animName'] = 'hold-pencil'
        return doWriteOff(attack)
    elif suitName == 'le':
        attack['id'] = JARGON
        attack['name'] = 'Jargon'
        attack['animName'] = 'speak'
        return doJargon(attack)
    elif suitName == 'bw':
        attack['id'] = FINGER_WAG
        attack['name'] = 'FingerWag'
        attack['animName'] = 'finger-wag'
        return doFingerWag(attack)
    else:
        self.notify.error('doDefault() - unsupported suit type: %s' % suitName)
    return None

def __createSuitResetPosTrack(suit, battle):
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    moveDist = Vec3(suit.getPos(battle) - resetPos).length()
    moveDuration = 0.5
    neutralTrack =  Func(suit.setNeutralAnimation())
    unluredTrack = Func(battle.unlureSuit, suit)
    updateTrack = Parallel(Func(suit.setChatAbsolute,
                                '',
                                CFSpeech | CFTimeout))
    walkTrack = Sequence(Func(suit.setHpr, battle, resetHpr), ActorInterval(suit, 'walk', startTime=1, duration=moveDuration, endTime=0.0001), neutralTrack)
    moveTrack = LerpPosInterval(suit, moveDuration, resetPos, other=battle)
    return Parallel(unluredTrack, updateTrack, walkTrack, moveTrack)


def getSuitTrack(attack, delay = 1e-06, splicedAnims = None, playRate = 1.0):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    target = attack['target']
    toon = target[0]['toon']
    name = attack['id']
    targetPos = toon.getPos(battle)
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    trapStorage = {}
    trapStorage['trap'] = None
    track = Sequence(Wait(delay))
    if attack[
        'suitName'] == 'fbd':  # It isn't just 'caseman', it really all depends on the shorthand you have for the Case Manager.  If it is not 'caseman', change it to whatever is the actual shorthand for the Case Manager, or the Case Manager will not grunt as intended.
        track.append(Func(suit.setChatAbsolute, random.choice(['Hrm...', 'Hmph...', 'Hm, hm...', 'Hrnhmpf...']),
                          CFSpeech | CFTimeout))
    elif name == WHITE_POWDER:
        taunt = random.choice(
            ["I've got my eye on you!", "I'll poke you in the eye!", "'Eye' am as evil as they come!'",
             "Wait. I've got something in my eye.", "Could you keep an eye on this for me?",
             "I'm rolling my eye at you.", "I'll put you in the eye of the storm!", "Could you eye-ball this for me?",
             "I'm giving you the evil eye.", "I've got a real eye for evil."])
        track.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    elif name == QUAKE and suit.isChainsawPhase2:
        taunt = random.choice(
            ["EMPLOYEES ARE RESISTING TERMINATION, CONTINGENCY PROCEDURES ARE IN EFFECT.",
             "UNCHARTED NUMBERS DETECTED ON THE RICHTER SCALE.",
             "COMMENCING OPERATION: QUAKE, RATTLE AND ROLL.",
"WARNING: 'GAG' HAS NO DEFINITION. IGNORING...",
"ADDITIONAL DAMAGE TO SUIT DETECTED, CONTINUITY PLAN ACTIVATED.",
"ORDER TO ATTACK HAS BEEN RECEIVED AND PROCESSED."])
        track.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    elif name == QUAKE and suit.isChainsawPhase3:
        taunt = random.choice(
            ["EMPLOYEES- i wi- ARE- i wish- RESISTING TERMI- wish i could- TERMINATION, CONTINGENCY- could stop- PROCEDURES ARE- it- IN EFFECT.",
"WARNING- this wa- WARNING: 'GAG' HAS- wasn't my- NO DEFINIT- choice- DEFINITION. IGNORING...",
"ADDITIONAL DAMAGE- i'm not- TO SUIT- in- DETECTED, CONTIN- in control of- CONTINUITY PLAN- my actions- ACTIVATED.",
             "UNCHARTED NU- pl- NUMBERS DETECT- please- DETECTED ON THE- help- RICHTER S- me- SCALE.",
             "COMMENCING- stop- OPERATION: QUAKE- stop- RATTLE- the- AND RO- override- ROLL.",
"ORDER- i'm- TO ATTACK HAS- i'm so- HAS BEEN RECEIVED AND- i'm sorry- PROCESSED."])
        track.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    elif name == CANNED and suit.isChainsawPhase2:
        taunt = random.choice(
            ["EMPLOYEES ARE RESISTING TERMINATION, CONTINGENCY PROCEDURES ARE IN EFFECT.",
             "WARNING: 'GAG' HAS NO DEFINITION. IGNORING...",
             "EXECUTING PROGRAM: 'KICK THE CAN' ROUTINE.",
                                              "ACTIVATING TOON-A CAN SEALING PROCESS.",
             "ADDITIONAL DAMAGE TO SUIT DETECTED, CONTINUITY PLAN ACTIVATED.",
             "ORDER TO ATTACK HAS BEEN RECEIVED AND PROCESSED."])
        track.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    elif name == CANNED and suit.isChainsawPhase3:
        taunt = random.choice(
            [
                "EMPLOYEES- i wi- ARE- i wish- RESISTING TERMI- wish i could- TERMINATION, CONTINGENCY- could stop- PROCEDURES ARE- it- IN EFFECT.",
                "WARNING- this wa- WARNING: 'GAG' HAS- wasn't my- NO DEFINIT- choice- DEFINITION. IGNORING...",
                "ADDITIONAL DAMAGE- i'm not- TO SUIT- in- DETECTED, CONTIN- in control of- CONTINUITY PLAN- my actions- ACTIVATED.",
                "EXECUTING- i- PROGRAM: 'KICK- can't- THE CAN' RO- help it- ROUTINE.",
"ACTIVATING- don't- TOON-A- want- CAN SE- to- SEALING PRO- fight you- PROCESS.",
                "ORDER- i'm- TO ATTACK HAS- i'm so- HAS BEEN RECEIVED AND- i'm sorry- PROCESSED."])
        track.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    elif name == ROLODEX and suit.isChainsawPhase2:
        taunt = random.choice(
            ["EMPLOYEES ARE RESISTING TERMINATION, CONTINGENCY PROCEDURES ARE IN EFFECT.",
             "WARNING: 'GAG' HAS NO DEFINITION. IGNORING...",
             "ATTEMPTING TO LOCATE TARGET'S EMPLOYMENT CARD.",
             "PROTOCOL FOR PEST EXTERMINATION HAS BEEN TRIGGERED.",
             "ADDITIONAL DAMAGE TO SUIT DETECTED, CONTINUITY PLAN ACTIVATED.",
             "ORDER TO ATTACK HAS BEEN RECEIVED AND PROCESSED."])
        track.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    elif name == ROLODEX and suit.isChainsawPhase3:
        taunt = random.choice(
            [
                "EMPLOYEES- i wi- ARE- i wish- RESISTING TERMI- wish i could- TERMINATION, CONTINGENCY- could stop- PROCEDURES ARE- it- IN EFFECT.",
                "WARNING- this wa- WARNING: 'GAG' HAS- wasn't my- NO DEFINIT- choice- DEFINITION. IGNORING...",
                "ADDITIONAL DAMAGE- i'm not- TO SUIT- in- DETECTED, CONTIN- in control of- CONTINUITY PLAN- my actions- ACTIVATED.",
                "ATTEMPTING- can't- TO LOCATE- hold- TARGET'S EMPLOY- out- EMPLOYMENT CARD.",
                "PROTOCOL FOR- hope- PEST EXT- is- EXTERMINATION HAS- paper- BEEN TRI- thin- TRIGGERED.",
                "ORDER- i'm- TO ATTACK HAS- i'm so- HAS BEEN RECEIVED AND- i'm sorry- PROCESSED."])
        track.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    elif name == GLOWER_POWER and suit.isChainsawPhase2:
        taunt = random.choice(
            ["EMPLOYEES ARE RESISTING TERMINATION, CONTINGENCY PROCEDURES ARE IN EFFECT.",
             "WARNING: 'GAG' HAS NO DEFINITION. IGNORING...",
             "PIERCING EYES HAVE BEEN ESTABLISHED.",
"UPDATING PROCESSES... MUST STAY ON THE CUTTING EDGE!!",
             "ADDITIONAL DAMAGE TO SUIT DETECTED, CONTINUITY PLAN ACTIVATED.",
             "ORDER TO ATTACK HAS BEEN RECEIVED AND PROCESSED."])
        track.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    elif name == GLOWER_POWER and suit.isChainsawPhase3:
        taunt = random.choice(
            [
                "EMPLOYEES- i wi- ARE- i wish- RESISTING TERMI- wish i could- TERMINATION, CONTINGENCY- could stop- PROCEDURES ARE- it- IN EFFECT.",
                "WARNING- this wa- WARNING: 'GAG' HAS- wasn't my- NO DEFINIT- choice- DEFINITION. IGNORING...",
                "ADDITIONAL DAMAGE- i'm not- TO SUIT- in- DETECTED, CONTIN- in control of- CONTINUITY PLAN- my actions- ACTIVATED.",
                "PIERCING EYES- i'm looking- HAVE BEEN- for a- ESTABLI- way out- ESTABLISHED.",
"UPDATING- no- PROCESSES... MUST- can't- MUST STAY ON THE- give in- CUTTING EDGE!!",
                "ORDER- i'm- TO ATTACK HAS- i'm so- HAS BEEN RECEIVED AND- i'm sorry- PROCESSED."])
        track.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    elif name == QUALITY_CONTROL_LEVEL_3:
        taunt = random.choice(
            ["I've got my eye on you!", "I'll poke you in the eye!", "'Eye' am as evil as they come!'",
             "Wait. I've got something in my eye.", "Could you keep an eye on this for me?",
             "I'm rolling my eye at you.", "I'll put you in the eye of the storm!", "Could you eye-ball this for me?",
             "I'm giving you the evil eye.", "I've got a real eye for evil."])
        track.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    else:
        track.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))

    def reparentTrap(suit = suit, battle = battle, trapStorage = trapStorage):
        return

    track.append(Func(reparentTrap))
    track.append(Func(suit.headsUp, battle, targetPos))
    if splicedAnims:
        track.append(getSplicedAnimsTrack(splicedAnims, actor=suit))
    else:
        track.append(ActorInterval(suit, attack['animName'], playRate=playRate))
    origPos, origHpr = battle.getActorPosHpr(suit)
    track.append(Func(suit.setHpr, battle, origHpr))
    if suit.dna.name == 'scg' and suit.isAngry:
        track.append(ActorInterval(suit, 'neutral-enraged-return', startTime=1, endTime=0))
        track.append(Func(suit.loop, 'neutral-enraged'))
    elif suit.isImmortal and suit.dna.name == 'dsf':
        track.append(
            Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    elif suit.isVulnerable and suit.dna.name == 'crf':
        track.append(
            Func(suit.loop, 'neutral2%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    elif suit.isImmortal:
        track.append(ActorInterval(suit, 'highroller-neutral-levitate-in-out', startTime=1, endTime=0))
        track.append(Func(suit.loop, 'highroller-neutral-levitate-loop'))
    else:
        track.append(
            Func(suit.setNeutralAnimation))

    def returnTrapToSuit(suit = suit, trapStorage = trapStorage):
        return

    track.append(Func(returnTrapToSuit))
    return track


def getSuitAnimTrack(attack, delay = 0, splicedAnims = None, playRate = 1.0):
    suit = attack['suit']
    tauntIndex = attack['taunt']
    name = attack['id']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    track = Sequence(Wait(delay))
    if attack[
        'suitName'] == 'fbd':  # It isn't just 'caseman', it really all depends on the shorthand you have for the Case Manager.  If it is not 'caseman', change it to whatever is the actual shorthand for the Case Manager, or the Case Manager will not grunt as intended.
        track.append(Func(suit.setChatAbsolute, random.choice(['Hrm...', 'Hmph...', 'Hm, hm...', 'Hrnhmpf...']),
                          CFSpeech | CFTimeout))
    else:
        track.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    if splicedAnims:
        track.append(getSplicedAnimsTrack(splicedAnims, actor=suit))
    else:
        track.append(ActorInterval(suit, attack['animName'], playRate=playRate))
    if suit.dna.name == 'scg' and suit.isAngry:
        track.append(ActorInterval(suit, 'neutral-enraged-return', startTime=1, endTime=0))
        track.append(Func(suit.loop, 'neutral-enraged'))
    elif suit.isImmortal and suit.dna.name == 'dsf':
        track.append(
            Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    elif suit.isVulnerable and suit.dna.name == 'crf':
        track.append(
            Func(suit.loop, 'neutral2%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    elif suit.isImmortal:
        track.append(ActorInterval(suit, 'highroller-neutral-levitate-in-out', startTime=1, endTime=0))
        track.append(Func(suit.loop, 'highroller-neutral-levitate-loop'))
    else:
        track.append(
            Func(suit.setNeutralAnimation))
    return track


def getPartTrack(particleEffect, startDelay, durationDelay, partExtraArgs):
    particleEffect = partExtraArgs[0]
    parent = partExtraArgs[1]
    if len(partExtraArgs) > 2:
        worldRelative = partExtraArgs[2]
    else:
        worldRelative = 1
    return Sequence(Wait(startDelay), ParticleInterval(particleEffect, parent, worldRelative, duration=durationDelay, cleanup=True))


def getPartTracks(attack, particleEffects, startDelay, durationDelay, worldRelative = 1):
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
        partTracks.append(getPartTrack(particleEffects[i], startDelay, durationDelay, [particleEffects[i], battle, worldRelative]))

    suit.setHpr(battle, origHpr) # After all that, set the Cog back like nothing ever happened.
    return partTracks


def getToonTrack(attack, damageDelay = 1e-06, damageAnimNames = None, dodgeDelay = 0.0001, dodgeAnimNames = None, splicedDamageAnims = None, splicedDodgeAnims = None, target = None, showDamageExtraTime = 0.01, showMissedExtraTime = 0.5):
    if not target:
        target = attack['target'][0]
    toon = target['toon']
    battle = attack['battle']
    suit = attack['suit']
    name = attack['id']
    suitPos = suit.getPos(battle)
    dmg = target['hp']
    animTrack = Sequence()
    animTrack.append(Func(toon.headsUp, battle, suitPos))
    if dmg > 0:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    else:
        animTrack.append(getToonDodgeTrack(target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime))
        #indicatorTrack = Sequence(Wait(dodgeDelay + showMissedExtraTime), Func(MovieUtil.indicateMissed, toon))
        return animTrack


def getToonTracks(attack, damageDelay = 1e-06, damageAnimNames = None, dodgeDelay = 1e-06, dodgeAnimNames = None, splicedDamageAnims = None, splicedDodgeAnims = None, showDamageExtraTime = 0.01, showMissedExtraTime = 0.5):
    toonTracks = Parallel()
    targets = attack['target']
    for i in xrange(len(targets)):
        tgt = targets[i]
        toonTracks.append(getToonTrack(attack, damageDelay, damageAnimNames, dodgeDelay, dodgeAnimNames, splicedDamageAnims, splicedDodgeAnims, target=tgt, showDamageExtraTime=showDamageExtraTime, showMissedExtraTime=showMissedExtraTime))

    return toonTracks

def getToonTrackCheat(attack, damageDelay = 1e-06, damageAnimNames = None, dodgeDelay = 0.0001, dodgeAnimNames = None, splicedDamageAnims = None, splicedDodgeAnims = None, target = None, showDamageExtraTime = 0.01, showMissedExtraTime = 0.5):
    if not target:
        target = attack['target'][0]
    toon = target['toon']
    battle = attack['battle']
    suit = attack['suit']
    name = attack['id']
    suitPos = suit.getPos(battle)
    dmg = target['hp']
    animTrack = Sequence()
    animTrack.append(Func(toon.headsUp, battle, suitPos))
    if dmg > 0:
        animTrack.append(getToonTakeDamageTrackCheat(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    else:
        animTrack.append(getToonDodgeTrack(target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime))
        #indicatorTrack = Sequence(Wait(dodgeDelay + showMissedExtraTime), Func(MovieUtil.indicateMissed, toon))
        return animTrack


def getToonTracksCheat(attack, damageDelay = 1e-06, damageAnimNames = None, dodgeDelay = 1e-06, dodgeAnimNames = None, splicedDamageAnims = None, splicedDodgeAnims = None, showDamageExtraTime = 0.01, showMissedExtraTime = 0.5):
    toonTracks = Parallel()
    targets = attack['target']
    for i in xrange(len(targets)):
        tgt = targets[i]
        toonTracks.append(getToonTrackCheat(attack, damageDelay, damageAnimNames, dodgeDelay, dodgeAnimNames, splicedDamageAnims, splicedDodgeAnims, target=tgt, showDamageExtraTime=showDamageExtraTime, showMissedExtraTime=showMissedExtraTime))

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
    leftToons = target['leftToons']
    rightToons = target['rightToons']
    if len(leftToons) > len(rightToons):
        PoLR = rightToons
        PoMR = leftToons
    else:
        PoLR = leftToons
        PoMR = rightToons
    upper = 1 + 4 * abs(len(leftToons) - len(rightToons))
    if random.randint(0, upper) > 0:
        toonDodgeList = PoLR
    else:
        toonDodgeList = PoMR
    if toonDodgeList is leftToons:
        sidestepAnim = 'sidestep-left'
        soundEffect = globalBattleSoundCache.getSound('AV_side_step.ogg')
    else:
        sidestepAnim = 'sidestep-right'
        soundEffect = globalBattleSoundCache.getSound('AV_jump_to_side.ogg')
    toonTracks = Parallel()
    for t in toonDodgeList:
        toonTracks.append(Sequence(ActorInterval(t, sidestepAnim), Func(t.loop, 'neutral')))

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
    name = attack['id']
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
 #   if died:
      #  suit = attack['suit']
      #  toonTrack.append(Wait(3.0))
      ##  if suit.getStyleName() in OTPLocalizerEnglish.SuitDefeatTaunts:
       #     suitResponseTrack.append(Parallel(Sequence(Wait(delay + showDamageExtraTime), Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitDefeatTaunts[suit.getStyleName()]), CFSpeech | CFTimeout))))
      #  else:
         #   suitResponseTrack.append(Parallel(Sequence(Wait(delay + showDamageExtraTime), Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitDefeatTauntsNone), CFSpeech | CFTimeout))))
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
   # if died:
      #  suit = attack['suit']
      # # toonTrack.append(Wait(3.0))
       # if suit.getStyleName() in OTPLocalizerEnglish.SuitDefeatTaunts:
         #   suitResponseTrack.append(Parallel(Sequence(Wait(delay + showDamageExtraTime), Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitDefeatTaunts[suit.getStyleName()]), CFSpeech | CFTimeout))))
       # else:
        #    suitResponseTrack.append(Parallel(Sequence(Wait(delay + showDamageExtraTime), Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitDefeatTauntsNone), CFSpeech | CFTimeout))))
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

def doPaperCut(attack):
    suit = attack['suit']
    battle = attack['battle']
    paper = globalPropPool.getProp('shredder-paper')
    #shredder = globalPropPool.getProp('shredder')
    particleEffect = BattleParticles.createParticleEffect('Shred2')
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    battle = attack['battle']
    targetPos = toon.getPos(battle)
    suitTrack = Sequence(getSuitTrack(attack))
    suitTrack2 = Sequence(ActorInterval(suit, 'sanction', endTime=1), Wait(2.0), ActorInterval(suit, 'sanction', startTime=1), Func(suit.setNeutralAnimation))
    partTrack = getPartTrack(particleEffect, 0.5, 3.0, [particleEffect, suit, 0])
    paperPosPoints = [Point3(0.59, -0.31, 0.81), VBase3(79.224, 32.576, -179.449)]
    paperPropTrack = getPropTrack(paper, suit.getRightHand(), paperPosPoints, .1, 1e-05, scaleUpTime=0.1, anim=1, propName='shredder-paper', animDuration=2.0, animStartTime=0.5)
    #shredderPosPoints = [Point3(0, -0.12, -0.34), VBase3(-90.0, -53.77, -0.0)]
    #shredderPropTrack = getPropTrack(shredder, suit.getLeftHand(), shredderPosPoints, 1, 3, scaleUpPoint=Point3(4.81, 4.81, 4.81))
    toonTrack = getToonTrackCheat(attack, 2, ['cringe'], 3.4, ['struggle'])
   # toonTrack = getToonTakeDamageTrackCheat(attack, toon, target[0]['died'], int(dmg), 2, ['cringe'])
    soundTrack = getSoundTrack('SA_shred.ogg', delay=0.5, node=suit)
    notifyTrack = Sequence(Wait(2), Func(toon.showHpTextCheat, - int(dmg)),
                           Func(toon.showHpString, "VULNERABLE!"))
    return Parallel(suitTrack, partTrack, suitTrack2, notifyTrack, toonTrack, soundTrack)

def doExplodingDocument(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    explode = []
    toonPos = toon.getPos(battle)
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.height - 0.2)
    explosionTrack = Sequence()
    explosionTrack.append(Wait(2.25))
    explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
    for i in xrange(0, 3):
        explode.append(globalPropPool.getProp('explosion'))
    explodePosPoints = [Point3(0, 15, 5), MovieUtil.PNT3_ZERO]
    explodePosPoints1 = [Point3(0, 15, 5), MovieUtil.PNT3_ZERO]
    explodeHprPoints = [Point3(180, 0, 0), MovieUtil.PNT3_ZERO]
    explodeHprPoints1 = [Point3(180, 0, 0), MovieUtil.PNT3_ZERO]
    explodeTracks = Parallel()
    for i in xrange(0, 3):
        explodeTrack = Sequence()
        explodeTrack.append(Wait(2.25))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodePosPoints, 1e-06, Point3(1.7, 1.7, 1.7), scaleUpTime=0.1))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodePosPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodeHprPoints, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodeHprPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.1))
        explodeTracks.append(explodeTrack)
    dmg = target[0]['hp']
    tnt = globalPropPool.getProp('shredder-paper')
    paper = globalPropPool.getProp('shredder-paper')
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    posPoints = [Point3(0.375, -1.5, .85), VBase3(0, 220, -10)]
    propTrack = Sequence(
        getPropAppearTrack(tnt, suit.getRightHand(), posPoints, 0.5, MovieUtil.PNT3_ONE, scaleUpTime=0))
    propTrack.append(Wait(1.5))
    hitPoint = __toonFacePoint(toon, parent=battle)
    hitPoint.setX(hitPoint.getX() - 1.4)
    missPoint = __toonGroundPoint(attack, toon, 3.1, parent=battle)
    missPoint.setX(missPoint.getX() - 1.1)
    propTrack.append(getPropThrowTrack(attack, tnt, [hitPoint], [missPoint], .25, parent=battle))
    toonTrack = getToonTrackCheat(attack, 2.5, ['slip-forward'], 3.4, ['struggle'])
   # toonTrack = getToonTakeDamageTrackCheat(attack, toon, target[0]['died'], int(dmg), 2.5, ['slip-forward'])
    soundTrack = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=2.25, node=suit)
    notifyTrack = Sequence(Wait(2.5), Func(toon.showHpTextCheat, - int(dmg)), Func(toon.showHpString, "GAG DEBUFF!"))
    return Parallel(explodeTracks, suitTrack, toonTrack, soundTrack, propTrack, notifyTrack, explosionTrack)

def doBookkeepingRetaliation(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTracks = Parallel()
    soundTracks = Parallel()
    toonTracks = Parallel()
    notifyTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        suitTrack = Sequence(getSuitAnimTrack(attack))
        suitTrack2 = Sequence(ActorInterval(suit, 'effort', duration=3.0), ActorInterval(suit, 'sanction'), Func(suit.setNeutralAnimation))
        damageAnims = [['conked']]
        toonTrack = getToonTracksCheat(attack, damageDelay=3.4, splicedDamageAnims=damageAnims, dodgeDelay=0.7,
                                  dodgeAnimNames=['neutral'])
        notifyTrack = Sequence(Wait(3.4), Func(toon.showHpTextCheat, - int(dmg)),
                               Func(toon.showHpString, "GAG DEBUFF!"))
        soundTrack1 = Sequence(SoundInterval(globalBattleSoundCache.getSound('suit_promotion_sfx.ogg'), node=suit))
        soundTrack2 = Sequence(Wait(3.4), SoundInterval(globalBattleSoundCache.getSound('SA_haymaker.ogg'), node=suit))
        soundTrack = Parallel(soundTrack1, soundTrack2)
        if dmg > 0:
            soundTracks.append(soundTrack)
            toonTracks.append(toonTrack)
            suitTracks.append(suitTrack)
            suitTracks.append(suitTrack2)
            notifyTracks.append(notifyTrack)
    return Parallel(suitTracks, soundTracks, toonTracks, notifyTracks)

def doCollectCall(attack):
    suit = attack['suit']
    target = attack['target']
    toon = target[0]['toon']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    dmg = target[0]['hp']
    battle = attack['battle']
    suitTrack = getSuitTrack(attack)
    toonPos = toon.getPos(battle)
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.height - 0.2)
    explosionTrack = Sequence()
    explosionTrack.append(Wait(8.25))
    explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
    cagePropTracks = Parallel()
    explodePosPoints = [Point3(0, 15, 5), MovieUtil.PNT3_ZERO]
    explodePosPoints1 = [Point3(0, 15, 5), MovieUtil.PNT3_ZERO]
    explodeHprPoints = [Point3(180, 0, 0), MovieUtil.PNT3_ZERO]
    explodeHprPoints1 = [Point3(180, 0, 0), MovieUtil.PNT3_ZERO]
    explode = []
    for i in xrange(0, 3):
        explode.append(globalPropPool.getProp('explosion'))
    explodeTracks = Parallel()
    for i in xrange(0, 3):
        explodeTrack = Sequence()
        explodeTrack.append(Wait(8.25))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodePosPoints, 1e-06, Point3(1.7, 1.7, 1.7), scaleUpTime=0.1))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodePosPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodeHprPoints, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodeHprPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.1))
        explodeTracks.append(explodeTrack)
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    cage = loader.loadModel('phase_5.5/models/estate/prop_phone-mod')
    cage2 = loader.loadModel('phase_5.5/models/estate/phoneMount-mod')
    toonPos = toon.getPos(battle)
    x = toonPos.getX() - 5
    if dmg == 0:
        x -= 10
    cagePos = [Point3(toonPos.getX(), toonPos.getY(), 20.0), toon.getHpr(battle)]
    cagePos2 = [Point3(toonPos.getX(), toonPos.getY(), 20.0), toon.getHpr(battle)]
    cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, 0.01, scaleUpPoint=Point3(1.0), scaleUpTime=1.0),
            Parallel(
                cage.posInterval(0.75, Point3(toonPos.getX(), x, 0.5), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/asfhdfha.ogg'), duration=0.75, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/asfhafhsdh.ogg'), node=cage),
            Wait(6.5),
            LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0),
            Func(MovieUtil.removeProp, cage)
        )
    cagePropTrack2 = Sequence(
        getPropAppearTrack(cage2, battle, cagePos2, 0.01, scaleUpPoint=Point3(1.0), scaleUpTime=1.0),
        Parallel(
            cage2.posInterval(0.75, Point3(toonPos.getX(), x, 0.5), blendType='easeIn'),
            SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/ashfhadh.ogg'), duration=0.75, node=cage)
        ),
        Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/afhdhsdhsd.ogg'), node=cage2),
        Wait(6.5),
        LerpFunctionInterval(cage2.setAlphaScale, fromData=1, toData=0, duration=1.0),
        Func(MovieUtil.removeProp, cage2)
    )
    phone = globalPropPool.getProp('phone')
    receiver = globalPropPool.getProp('receiver')

    phonePosPoints = [Point3(-0.23, 0, -0.11), VBase3(5.939, 2.763, -177.591)]
    receiverPosPoints = [Point3(-0.23, 0, -0.11), VBase3(5.939, 2.763, -177.591)]
    propTrack = Sequence(Wait(1.75), Func(__showProp, phone, suit.getLeftHand(), phonePosPoints[0], phonePosPoints[1]),
                         Func(__showProp, receiver, suit.getLeftHand(), receiverPosPoints[0], receiverPosPoints[1]),
                         LerpScaleInterval(phone, 0.5, MovieUtil.PNT3_ONE, MovieUtil.PNT3_NEARZERO), Wait(0.24),
                         Func(receiver.wrtReparentTo, suit.getRightHand()),
                         LerpPosHprInterval(receiver, 0.0001, Point3(-0.45, 0.48, -0.62), VBase3(-87.47, -18.21, 7.82)),
                         Wait(5.25), Func(receiver.wrtReparentTo, phone), Wait(0.62),
                         LerpScaleInterval(phone, 0.5, MovieUtil.PNT3_NEARZERO),
                         Func(MovieUtil.removeProps, [receiver, phone]))
    suitSpeechTrack = Sequence(Wait(6.0), Func(suit.setChatAbsolute, "You should know not to talk to strangers.", CFSpeech | CFTimeout))
    cagePropTracks.append(cagePropTrack)
    cagePropTracks.append(cagePropTrack2)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    suitTrack.append(Sequence(ActorInterval(suit, 'phone', duration=3.0), Wait(3.0), ActorInterval(suit, 'phone', startTime=3.0), Func(suit.setNeutralAnimation)))
    soundTrack1 = getSoundTrack('tt_s_ara_cmg_itemHitsFloor.ogg', delay=1.75, node=suit)
    soundTrack2 = getSoundTrack('SA_bash.ogg', delay=0, node=suit)
    soundTrack3 = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=8.25, node=suit)
    soundTrack4 = getSoundTrack('telephone_ring.ogg', delay=2.0, node=suit)
    soundTrack = Parallel(soundTrack1, soundTrack2, soundTrack3, soundTrack4)
    toonTrack = Sequence(ActorInterval(toon, 'confused'), ActorInterval(toon, 'takePhone'), ActorInterval(toon, 'phoneNeutral', duration=1))
    toonTrack.append(getToonTakeDamageTrackCheat(attack, toon, target[0]['died'], int(dmg), 0.5, ['conked']))
    notifyTrack = Sequence(Wait(8.25), Func(toon.showHpTextCheat, - int(dmg)),
                           Func(toon.showHpString, "DUES INCREASED!"))
    makeUnVulnerable = Func(suit.makeUnVulnerable)
    return Parallel(explodeTracks, suitTrack, cagePropTracks, makeUnVulnerable, toonTrack, notifyTrack, soundTrack, suitSpeechTrack, explosionTrack, propTrack)

def doBrokenConnection(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack.append(Wait(2.0))
    makeImmune = Func(suit.makeVulnerable)
    makeImmune2 = Func(suit.makeNonImmortal)
    selfDamageTrack = Func(suit.showHpText, "VULNERABLE!", 2, openEnded=0)
    return Parallel(suitTrack, makeImmune, makeImmune2, selfDamageTrack)

def doVoicemail(attack):
    suit = attack['suit']
    battle = attack['battle']
    phone = globalPropPool.getProp('phone')
    receiver = globalPropPool.getProp('receiver')
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
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
    soundTrack = getSoundTrack('SA_hangup.ogg', delay=0.5, node=suit)
    notifyTrack = Func(suit.showHpTextWhite, 'IMMUNE!')
    makeImmune = Func(suit.makeImmortal)
    return Parallel(suitTrack, propTrack, soundTrack, notifyTrack, makeImmune)

def doWiretapped(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    dmg = (attack['target'][0]['hp']) * len(battle.activeToons)
    phone = globalPropPool.getProp('phone')
    receiver = globalPropPool.getProp('receiver')
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    suitName = suit.getStyleName()
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    gearPoint = Point3(suitPos.getX(), suitPos.getY() - 10, suitPos.getZ() + suit.height - 0.2)
    explosionTrack = Sequence()
    explosionTrack.append(Wait(2.7))
    explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
    explode = []
    explodePosPoints = [Point3(0, 10, 1), MovieUtil.PNT3_ZERO]
    explodePosPoints1 = [Point3(0, 10, 1), MovieUtil.PNT3_ZERO]
    explodeHprPoints = [Point3(180, 0, 0), MovieUtil.PNT3_ZERO]
    explodeHprPoints1 = [Point3(180, 0, 0), MovieUtil.PNT3_ZERO]
    for i in xrange(0, 3):
        explode.append(globalPropPool.getProp('explosion'))
    explodeTracks = Parallel()
    for i in xrange(0, 3):
        explodeTrack = Sequence()
        explodeTrack.append(Wait(2.7))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodePosPoints, 1e-06, Point3(1.7, 1.7, 1.7), scaleUpTime=0.1))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodePosPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodeHprPoints, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodeHprPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.1))
        explodeTracks.append(explodeTrack)
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
    selfDamageTrack = Sequence(Wait(4), Func(suit.showHpTextCheat, +dmg), Func(suit.showHpString, "SYPHONED!", openEnded=0), Func(suit.setHealthForMe, +dmg), Func(suit.updateHealthBar, 0))
    #propTrack = Sequence(Wait(0.3), Func(__showProp, phone, suit.getLeftHand(), phonePosPoints[0], phonePosPoints[1]), Func(__showProp, receiver, suit.getLeftHand(), receiverPosPoints[0], receiverPosPoints[1]), LerpScaleInterval(phone, 0.5, scaleUpPoint, MovieUtil.PNT3_NEARZERO), Wait(pickupDelay), Func(receiver.wrtReparentTo, suit.getRightHand()), LerpScaleInterval(receiver, 0.01, receiverAdjustScale), LerpPosHprInterval(receiver, 0.0001, Point3(-0.53, 0.21, -0.54), VBase3(-99.49, -35.27, 1.84)), Wait(dialDuration), Func(receiver.wrtReparentTo, phone), Wait(finalPhoneDelay), LerpScaleInterval(phone, 0.5, MovieUtil.PNT3_NEARZERO), Func(MovieUtil.removeProps, [receiver, phone]))
    toonTracks = getToonTracks(attack, 2.8, ['slip-backward'], 4.7, ['jump'])
    soundTrack = getSoundTrack('SA_hangup.ogg', delay=0.5, node=suit)
    soundTrack1 = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=2.8, node=suit)
    makeNotImmune = Func(suit.makeNonImmortal)
    #suitTrack.append(Wait(1.0))
    #suitTrack.append(doPayback(attack))
    return Parallel(suitTrack, propTrack, soundTrack, selfDamageTrack, soundTrack1, toonTracks, makeNotImmune, explodeTracks, explosionTrack)

def doManagerialProtectionImmunity(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(getSuitAnimTrack(attack))
    notifyTrack = Func(suit.showHpTextWhite, 'IMMUNE!')
    makeImmune = Func(suit.makeImmortal)
    makeUnVulnerable = Func(suit.makeUnVulnerable)
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    return Parallel(suitTrack, soundTrack, notifyTrack, makeUnVulnerable, makeImmune)

def doManagerialProtection(attack):
    suit = attack['suit']
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack.append(Wait(2.0))
    soundTrack = getSoundTrack('SA_bash.ogg', node=suit)
    return Parallel(suitTrack, soundTrack)

def doRefinement(attack):
    theSuit = attack['suit']
    battle = attack['battle']

    suitTracks = Parallel()
    for suit in battle.activeSuits:
        suitTrack = Sequence()
        suitTrack.append(Wait(4.5))
        currentBossHealth = -1
        for s in battle.suits:
            if s.dna.name == 'cp':
                currentBossHealth = s.currHP
        if currentBossHealth >= 1:
            x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
            if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                suitTrack.append(Func(suit.showHpText, 0))
                suitTrack.append(Func(suit.showHpString, "REFINED!"))
            elif suit.currHP + 200 > (suit.maxHP * suit.hardMaxHP):
                suitTrack.append(Func(suit.showHpTextCheat, x))
                suitTrack.append(Func(suit.showHpString, "REFINED!"))
                suitTrack.append(Func(suit.setHealthForMe, 200))
            else:
                suitTrack.append(Func(suit.showHpTextCheat, 200))
                suitTrack.append(Func(suit.showHpString, "REFINED!"))
                suitTrack.append(Func(suit.setHealthForMe, 200))
        else:
            x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
            if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                suitTrack.append(Func(suit.showHpText, 0))
                suitTrack.append(Func(suit.showHpString, "REFINED!"))
            elif suit.currHP + 125 > (suit.maxHP * suit.hardMaxHP):
                suitTrack.append(Func(suit.showHpTextCheat, x))
                suitTrack.append(Func(suit.showHpString, "REFINED!"))
                suitTrack.append(Func(suit.setHealthForMe, x))
            else:
                suitTrack.append(Func(suit.showHpTextCheat, 125))
                suitTrack.append(Func(suit.showHpString, "REFINED!"))
                suitTrack.append(Func(suit.setHealthForMe, 125))
            suitTrack.append(Func(suit.updateHealthBar, 0))
            if not suit.dna.name == 'gtk':
                suitTrack.append(Parallel(Sequence(Wait(3)),
                                          Func(suit.setChatAbsolute,
                                               random.choice(OTPLocalizerEnglish.SuitHealingPhrases),
                                               CFSpeech | CFTimeout)))
            suitTrack.append(
                Func(suit.setNeutralAnimation))
        suitTracks.append(suitTrack)
    posPoints = [Point3(-0.25, 0, 0), VBase3(0, 180, 0)]
    knifeTracks = Parallel()
    for suit in battle.activeSuits:
        theSuit = attack['suit']
        hitPoint = suit.getPos(battle)
        hitPoint.setZ(suit.height + 2)
        hitPoint.setY(hitPoint.getY() + 0.5)
        knife = loader.loadModel('phase_12/models/bossbotHQ/canoffood')
        can = knife.find('**/can')
        can.setScale(.5)
        knifeTrack = Sequence(
            getPropAppearTrack(can, theSuit.getRightHand(), posPoints, .5, VBase3(0.5, 0.5, 0.5),
                               scaleUpTime=0.1),
            Wait(1.5),
            Parallel(
                getThrowTrack(can, hitPoint, 1.5, battle, -10.288),
                LerpHprInterval(can, 0.8, VBase3(0, 0, 0)), LerpScaleInterval(can, 0, VBase3(1, 1, 1))),
        Parallel(LerpPosInterval(can, 1, VBase3(hitPoint.getX(), hitPoint.getY() + 0.5, hitPoint.getZ() - 10)), Sequence(Wait(0.25), LerpScaleInterval(can, 0.5, VBase3(0, 0, 0)))),
            Func(MovieUtil.removeProp, can)
        )
        knifeTracks.append(knifeTrack)
    tauntIndex = attack['taunt']
    taunt = random.choice(
        ["It's important to stay adequately oiled when defeating Toons.", "I'm suspending this well.",
"Freshly drilled to keep us in working order."])
    makeUnVulnerable = Func(theSuit.makeUnVulnerable)
    suitPos, suitHpr = battle.getActorPosHpr(theSuit)
    gearPoint = Point3(suitPos.getX(), suitPos.getY(), suitPos.getZ() + theSuit.height - 0.2)
    explosionTrack = Sequence()
    explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
    name = attack['id']
    suitTrackAnim = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    soundTrack1 = getSoundTrack('SA_repair.ogg', delay=2.5, node=theSuit)
    soundTrack2 = getSoundTrack('SA_refinement.ogg', delay=2, node=theSuit)
    multiTrack = Parallel(soundTrack1, soundTrack2)
    makeNotImmune = Func(theSuit.makeNonImmortal)
    return Parallel(suitTrackAnim, makeUnVulnerable, makeNotImmune, suitTracks, multiTrack, knifeTracks)

def doHeadRoller(attack, ind):
    manager = attack['suit']
    battle = attack['battle']
    targetSuit = battle.activeSuits[ind]

    managerTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack = Sequence(Wait(1.0), ActorInterval(targetSuit, 'soak', duration=2.25), Sequence(MovieUtil.spawnHeadExplosion(targetSuit, battle)), Func(targetSuit.setChatAbsolute,
                                                       "Ouch.",
                                                       CFSpeech | CFTimeout), Wait(1.0), MovieUtil.createSuitHeadlessDeathTrack(targetSuit, battle))
    selfDamageTrack = Sequence(Wait(2), Func(targetSuit.showHpTextCheat, -targetSuit.currHP), Func(targetSuit.showHpStringSacrifice, "OFF WITH YOUR HEAD!"), Func(targetSuit.setHealthForMe, - targetSuit.currHP),
                               Func(targetSuit.updateHealthBar, 0))
    suitTrack2 = Sequence(Wait(1.0), ActorInterval(targetSuit, 'soak', duration=2.25),
                         Parallel(ActorInterval(targetSuit, 'pie-small-react', duration=2.25), Func(targetSuit.setChatAbsolute,
                                                                                          "Nice try.",
                                                                                          CFSpeech | CFTimeout)),
                         Wait(1.0), Func(targetSuit.checkCogHP, battle), Func(targetSuit.setNeutralAnimation))
    selfDamageTrack2 = Sequence(Wait(2), Func(targetSuit.showHpTextCheat, -250),
                               Func(targetSuit.showHpStringDamaged, "DAMAGED!"),
                               Func(targetSuit.setHealthForMe, -250),
                               Func(targetSuit.updateHealthBar, 0))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_bash.ogg'), node=targetSuit))
    if targetSuit.dna.name in SuitBattleGlobals.SpecialCogDict:
        return Parallel(managerTrack, suitTrack2, soundTrack, selfDamageTrack2)
    else:
        return Parallel(managerTrack, suitTrack, soundTrack, selfDamageTrack)

def doHeadRollerGroup(attack):
    manager = attack['suit']
    battle = attack['battle']
    selfDamageTracks = Parallel()
    suitTracks = Parallel()
    managerTrack = Sequence(getSuitAnimTrack(attack))

    for targetSuit in battle.activeSuits:
        suitTrack = Sequence(Wait(1.0), ActorInterval(targetSuit, 'soak', duration = 2.25), Sequence(MovieUtil.spawnHeadExplosion(targetSuit, battle)), Func(targetSuit.setChatAbsolute,
                                                       "Ouch.",
                                                       CFSpeech | CFTimeout), Wait(1.0), MovieUtil.createSuitHeadlessDeathTrack(targetSuit, battle))
        selfDamageTrack = Sequence(Wait(2), Func(targetSuit.showHpTextCheat, -targetSuit.currHP), Func(targetSuit.showHpStringSacrifice, "OFF WITH YOUR HEAD!"), Func(targetSuit.setHealthForMe, - targetSuit.currHP),
                               Func(targetSuit.updateHealthBar, 0))
        suitTrack2 = Sequence(Wait(1.0), ActorInterval(targetSuit, 'soak', duration=2.25),
                              Parallel(ActorInterval(targetSuit, 'pie-small-react', duration=2.25),
                                       Func(targetSuit.setChatAbsolute,
                                            "Nice try.",
                                            CFSpeech | CFTimeout)),
                              Wait(1.0), Func(targetSuit.checkCogHP, battle), Func(targetSuit.setNeutralAnimation))
        selfDamageTrack2 = Sequence(Wait(2), Func(targetSuit.showHpTextCheat, -250),
                                    Func(targetSuit.showHpStringDamaged, "DAMAGED!"),
                                    Func(targetSuit.setHealthForMe, -250),
                                    Func(targetSuit.updateHealthBar, 0))
        if targetSuit.dna.name in SuitBattleGlobals.SpecialCogDict and not manager:
            selfDamageTracks.append(selfDamageTrack2)
            suitTracks.append(suitTrack2)
        else:
            selfDamageTracks.append(selfDamageTrack)
            suitTracks.append(suitTrack)
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_bash.ogg'), node=manager))
    return Parallel(managerTrack, suitTracks, soundTrack, selfDamageTracks)

def doAmbassadorPhase2(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    ambassadorPhase3 = Func(theSuit.makeAmbassadorPhase3)
    suitTrackAnim = Sequence()
    soundTrack3 = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), node=theSuit)
    suitTrackAnim.append(MovieUtil.createAmbassadorReviveTrack(theSuit, battle))
    suitTrackAnim.append(Func(theSuit.makeAmbassadorPhase3))
    suitTrackAnim.append(Func(theSuit.setNeutralAnimation))
    suitTrackAnim.append(Wait(2))
    suitTrackAnim.append(Parallel(Func(theSuit.updateHealthBar, 0), ActorInterval(theSuit, 'frustrated'),
                                  Func(theSuit.showHpString, "1.5x DMG MULTIPLIER!"),
                                  Func(theSuit.setChatAbsolute, "You toons have me so overworked, you made me blow through my suit! Now it's time to bring out the big guns.", CFSpeech | CFTimeout),
                                  Func(theSuit.setNeutralAnimation)))
    suitTrackAnim.append(Wait(3))
    return Parallel(suitTrackAnim, soundTrack3)

def doMulligan(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    name = attack['id']
    club = globalPropPool.getProp('golf-club')
    ball = globalPropPool.getProp('golf-ball')
    tauntIndex = attack['taunt']
    battle = attack['battle']
    toon = target[0]['toon']
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.75))

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
    return Parallel(suitTrack, toonTrack, clubPropTrack, ballPropTrack, soundTrack)

def doAmbassadorDamageUpDesperation(attack):
    suit = attack['suit']
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    soundTrack = getSoundTrack('LB_toonup.ogg', delay=2.0, node=suit)
    makeImmune = Func(suit.makeDamageUp)
    managerHealTrack = Sequence(Wait(2), Func(suit.showHpTextCheat, + 250), Func(suit.showHpString, "1.25x DMG MULTIPLIER!"), Func(suit.setHealthForMe, + 250), Func(suit.updateHealthBar, 0))
    return Parallel(suitTrack, soundTrack, managerHealTrack, makeImmune)

def doAmbassadorDamageUp(attack):
    suit = attack['suit']
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    soundTrack = getSoundTrack('LB_toonup.ogg', delay=2.0, node=suit)
    makeImmune = Func(suit.makeDamageUp)
    managerHealTrack = Sequence(Wait(2), Func(suit.showHpTextCheat, + 100), Func(suit.showHpString, "1.1x DMG MULTIPLIER!"), Func(suit.setHealthForMe, + 100), Func(suit.updateHealthBar, 0))
    return Parallel(suitTrack, soundTrack, managerHealTrack, makeImmune)

def doCollectCallDamage(attack):
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
    #toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.91, dodgeAnimNames=['sidestep'], showDamageExtraTime=2.1, showMissedExtraTime=1.0)
    soundTracks = Parallel()
    toonSpinTracks = Parallel()
    nothingTrack = Sequence(Wait(1.0))
    toonTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        spinEffect1 = BattleParticles.createParticleEffect(file='organizeEffect')
        spinEffect2 = BattleParticles.createParticleEffect(file='organizeEffect')
        spinEffect3 = BattleParticles.createParticleEffect(file='organizeEffect')
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
            toonTracks.append(getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.91, dodgeAnimNames=['neutral'], showDamageExtraTime=2.1, showMissedExtraTime=4))
            spinTracks1.append(getPartTrack(spinEffect1, 1.5, 3.9, [spinEffect1, battle, 0]))
            spinTracks2.append(getPartTrack(spinEffect2, 1.5, 3.9, [spinEffect2, battle, 0]))
            spinTracks3.append(getPartTrack(spinEffect3, 1.5, 3.9, [spinEffect3, battle, 0]))
            soundTracks.append(getSoundTrack('tt_s_ara_cfg_toonInWhirlwind.ogg', delay=2.0, node=suit))
            toonSpinTracks.append(Sequence(Wait(damageDelay + 0.9), LerpHprInterval(toon, 0.7, Point3(-10, 0, 0)), LerpHprInterval(toon, 0.5, Point3(-30, 0, 0)), LerpHprInterval(toon, 0.2, Point3(-60, 0, 0)), LerpHprInterval(toon, 0.7, Point3(-700, 0, 0)), LerpHprInterval(toon, 1.0, Point3(-1310, 0, 0)), LerpHprInterval(toon, 0.4, toon.getHpr()), Wait(0.5)))
    return Parallel(toonTracks, toonSpinTracks, spinTracks1, spinTracks2, spinTracks3, soundTracks)

def doWiretapperGagBan(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    allTubeTracks = Parallel()
    toonTracks = Parallel()
    soundTracks = Parallel()
    posPoints = [Point3(-0.3, 0.4, 0.0), VBase3(0, 0, 90)]
    knifeTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        tape = globalPropPool.getProp('redtape')
        tubes = []
        for i in xrange(0, 3):
            tubes.append(globalPropPool.getProp('redtape-tube'))

        hitPoint = lambda toon = toon: __toonTorsoPoint(toon)
        hips = toon.getHipsParts()
        animal = toon.style.getAnimal()
        scale = ToontownGlobals.toonBodyScales[animal]
        knife = globalPropPool.getProp('dagger')
        knifeTrack = Sequence(
            getPropAppearTrack(knife, suit.getRightHand(), posPoints, 0.25, scaleUpPoint=Point3(1.0), scaleUpTime=0.1),
            Wait(1.0),
            Parallel(
                getThrowTrack(knife, toon.getPos(battle), 3.0, battle, -64.288),
                LerpHprInterval(knife, 0.8, VBase3(720, 630, 720))
            ),
            Func(MovieUtil.removeProp, knife)
        )
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
            tubeTracks.append(getPropTrack(tubes[partNum], nextPart, tubePosPoints, 0, 3, scaleUpPoint=scaleUpPoint))

        tubeTracks.append(Func(battle.movie.clearRestoreHips))
        damageAnims = [['struggle'], ['slip-backward', 0.01, 0.35]]
        toonTrack = getToonTracks(attack, damageDelay=4, splicedDamageAnims=damageAnims, dodgeDelay=0.7,
                                  dodgeAnimNames=['neutral'])
        soundTrack = getSoundTrack('SA_red_tape.ogg', delay=0, node=suit)
        soundTrack2 = getSoundTrack('tt_s_ara_cmg_itemHitsFloor.ogg', delay=4, node=suit)
        if dmg > 0:
            allTubeTracks.append(tubeTracks)
            toonTracks.append(toonTrack)
            soundTracks.append(soundTrack)
            soundTracks.append(soundTrack2)
            knifeTracks.append(knifeTrack)

    return Parallel(toonTracks, soundTracks, knifeTracks, allTubeTracks)

def doBookkeeping(attack):
    suit = attack['suit']
    suitTrack = Sequence(getSuitAnimTrack(attack))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('suit_promotion_sfx.ogg'), node=suit))
    return Parallel(suitTrack, soundTrack)

def doAbsorb(attack):
    suit = attack['suit']
    makeShielding = Func(suit.makeShielding)
    makeUnShielding = Func(suit.makeUnSoakResistant)
    makeUnShielding2 = Func(suit.makeUnSyphon)
    makeUnShielding3 = Func(suit.makeUnLureImmune)
    suitTrack = Sequence(getSuitTrack(attack))
    suitTrack.append(Wait(3.0))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_defense.ogg'), node=suit))
    return Parallel(suitTrack, soundTrack, makeShielding, makeUnShielding3, makeUnShielding, makeUnShielding2)

def doSoakImmune(attack):
    suit = attack['suit']
    makeShielding = Func(suit.makeSoakResistant)
    makeUnShielding = Func(suit.makeUnSyphon)
    makeUnShielding2 = Func(suit.makeUnShielding)
    makeUnShielding3 = Func(suit.makeUnLureImmune)
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack.append(Wait(3.0))
    suitTrack2 = Sequence(ActorInterval(attack['suit'], 'squirt-small-react', startTime=2), Func(suit.setNeutralAnimation))
    return Parallel(suitTrack, makeShielding, makeUnShielding2, suitTrack2, makeUnShielding3, makeUnShielding)

def doSyphon(attack):
    suit = attack['suit']
    makeShielding = Func(suit.makeUnSoakResistant)
    makeUnShielding = Func(suit.makeSyphon)
    makeUnShielding2 = Func(suit.makeUnShielding)
    makeUnShielding3 = Func(suit.makeUnLureImmune)
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    suitTrack.append(Wait(3.0))
    return Parallel(suitTrack, makeShielding, makeUnShielding3, makeUnShielding2, makeUnShielding)

def doSyphonDesperation(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    suitTracks = Parallel()
    for suit in battle.activeSuits:
        makeSyphon = Func(suit.makeSyphon)
        suitTrack = Sequence()
        suitTrack.append(Wait(3))
        if not suit.dna.name == 'cp':
            suitTrack.append(Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases), CFSpeech | CFTimeout))
        suitTrack.append(makeSyphon)
        suitTrack.append(Func(suit.setNeutralAnimation))
        suitTracks.append(suitTrack)
    suitTrack = Sequence(getSuitTrack(attack))
    suitTrack.append(Wait(3.0))
    soundTrack1 = getSoundTrack('SA_scabbard.ogg', node=theSuit)
    return Parallel(suitTrack, suitTracks, soundTrack1)

def doLureImmune(attack):
    suit = attack['suit']
    makeShielding = Func(suit.makeUnSoakResistant)
    makeUnShielding = Func(suit.makeUnSyphon)
    makeUnShielding2 = Func(suit.makeUnShielding)
    makeUnShielding3 = Func(suit.makeLureImmune)
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack.append(Wait(3.0))
    suitTrack2 = Sequence(ActorInterval(attack['suit'], 'rake-react'), Func(suit.setNeutralAnimation))
    return Parallel(suitTrack, suitTrack2, makeShielding, makeUnShielding2, makeUnShielding3, makeUnShielding)

def doBudgetCuts(attack):
    suit = attack['suit']
    calculator = globalPropPool.getProp('calculator')
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack2 = Sequence(ActorInterval(attack['suit'], 'calculator', playRate=1.25), Func(suit.setNeutralAnimation))
    suitTrack2.append(Wait(2.0))
    calcPosPoints = [Point3(-.85, 0.25, -0.1), VBase3(1.352, 0.0, 180.0)]
    calcDuration = 1.3
    scaleUpPoint = Point3(1.5, 1.5, 1.5)
    calcPropTrack = getPropTrack(calculator, suit.getLeftHand(), calcPosPoints, 0, calcDuration,
                                 scaleUpPoint=scaleUpPoint, scaleUpTime=0, anim=1, propName='calculator',
                                 animStartTime=0,
                                 animDuration=2.5)
    soundTrack = getSoundTrack('SA_calculate.ogg', delay=1.3, node=suit)
    return Parallel(suitTrack, calcPropTrack, suitTrack2, soundTrack)

def doBudgetCuts2(attack):
    suit = attack['suit']
    battle = attack['battle']
    calculator = globalPropPool.getProp('court-costs-calculator')
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack2 = Sequence(ActorInterval(attack['suit'], 'calculating-costs'), Func(suit.setNeutralAnimation))
    suitTrack2.append(Wait(2.0))
    calcPosPoints = [Point3(-0.35, 0.25, -0.1), VBase3(1.352, 0.0, 180.0)]
    calcDuration = 0.25
    scaleUpPoint = Point3(1.5, 1.5, 1.5)
    calcPropTrack = getPropTrack(calculator, suit.getRightHand(), calcPosPoints, 0, calcDuration,
                                 scaleUpPoint=scaleUpPoint, scaleUpTime=0, anim=1, propName='court-costs-calculator', animStartTime=0,
                                 animDuration=2.9)
    soundTrack = getSoundTrack('SA_calculating_costs.ogg', node=suit)
    return Parallel(suitTrack, soundTrack, suitTrack2, calcPropTrack)

def doSnipe(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    explosionTracks = Parallel()
    toonTracks = Parallel()
    soundTracks = Parallel()
    leftKnifeTracks = Parallel()
    rightKnifeTracks = Parallel()
    suitTracks = Parallel()
    notifyTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        toonPos = toon.getPos(battle)
        suitPos, suitHpr = battle.getActorPosHpr(suit)
        gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.height - 0.2)
        leftPosPoints = [Point3(0.5, 3.0, suit.height - 1), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.5, 3.0, suit.height - 1), MovieUtil.PNT3_ZERO]
        explosionTrack = Sequence()
        explosionTrack.append(Wait(1.5))
        explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
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
            leftTrack.append(
                getPropAppearTrack(leftKnives[i], suit, leftPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
            leftTrack.append(getPropThrowTrack(attack, leftKnives[i], hitPointNames=['face'], missPointNames=['miss'],
                                               hitDuration=0.3, missDuration=0.3, target=t))
            if dmg > 0:
                leftKnifeTracks.append(leftTrack)
            rightTrack = Sequence()
            rightTrack.append(Wait(1.1))
            rightTrack.append(Wait(i * knifeDelay))
            rightTrack.append(
                getPropAppearTrack(rightKnives[i], suit, rightPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
            rightTrack.append(getPropThrowTrack(attack, rightKnives[i], hitPointNames=['face'], missPointNames=['miss'],
                                                hitDuration=0.3, missDuration=0.3, target=t))
            if dmg > 0:
                rightKnifeTracks.append(rightTrack)

        damageAnims = [['slip-backward', 0.01, 0.35]]
        toonTrack = getToonTracksCheat(attack, damageDelay=1.6, splicedDamageAnims=damageAnims, dodgeDelay=0.7, dodgeAnimNames=['neutral'])
        notifyTrack = Sequence(Wait(1.6), Func(toon.showHpTextCheat, - int(dmg)),
                               Func(toon.showHpStringSnipe, "SNIPED!"))
        #toonTrack = getToonTracks(attack, damageDelay=1.6, splicedDamageAnims=damageAnims, dodgeDelay=0.7, dodgeAnimNames=['neutral'])
        soundTrack = getSoundTrack('SA_glower_power.ogg', delay=1.1, node=suit)
        soundTrack2 = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=1.5, node=suit)
        suitTrack = Sequence(getSuitAnimTrack(attack))
        suitTrack.append(Wait(2.0))
        if dmg > 0:
            toonTracks.append(toonTrack)
            soundTracks.append(soundTrack)
            soundTracks.append(soundTrack2)
            explosionTracks.append(explosionTrack)
            suitTracks.append(suitTrack)
            notifyTracks.append(notifyTrack)
    return Parallel(suitTracks, toonTracks, rightKnifeTracks, notifyTracks, leftKnifeTracks, explosionTracks, soundTracks)

