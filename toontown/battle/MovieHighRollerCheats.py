from toontown.battle import MovieCamera
from toontown.battle import MovieUtil
from toontown.battle import BattleParticles
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from direct.particles import ParticleEffect
from toontown.battle.BattleBase import *
from toontown.effects import Splash
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
   # if suit.dna.name == 'scg' and suit.isAngry:
      #  neutralIval =  Func(suit.loop, 'neutral-enraged')
      #  preWalkTrack = ActorInterval(suit, 'neutral-enraged-return')
    if name == FREE_CRUISE:
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
    elif name == HIGH_ROLLER_NO_ATTACK:
        neutralIval = Func(suit.loop, 'neutral2%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
        preWalkTrack = Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
    elif name == NICKEL_AND_DIME:
        neutralIval = Func(suit.loop, 'highroller-neutral-levitate-loop')
        preWalkTrack = Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
    elif name == BEGUILE:
        neutralIval = Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
        preWalkTrack = Func(suit.loop,
                            'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
   # elif suit.isImmortal and suit.dna.name == 'dsf':
       # neutralIval = Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
        #preWalkTrack = Func(suit.loop,
                      #      'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
   # elif suit.isImmortal:
       # neutralIval = Func(suit.loop, 'highroller-neutral-levitate-loop')
       # preWalkTrack = ActorInterval(suit, 'highroller-neutral-levitate-in-out', startTime=1, endTime=0, duration=1)
    else:
        neutralIval =  Func(suit.setNeutralAnimation)
        preWalkTrack = Func(suit.setNeutralAnimation)
    unlureSuit = Func(suit.makeUnLured)
    suitTrack = Sequence(unlureSuit, preWalkTrack, suitTrack, neutralIval, toonHprTrack)
    suitPos = suit.getPos(battle)
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    resetTrack = getResetTrack(suit, battle)
    if name == SCAPEGOAT_COURT_RECORD_BAN:
        resetSuitTrack = Sequence(suitTrack)
    elif name == CASE_MANAGER_COURT_RECORD_BAN:
        resetSuitTrack = Sequence(suitTrack)
    elif name == STENOGRAPHER_COURT_RECORD_BAN:
        resetSuitTrack = Sequence(suitTrack)
    elif name == CASE_MANAGER_LEGALLY_BOUND:
        resetSuitTrack = Sequence(suitTrack)
    elif name == CASE_MANAGER_INSURANCE:
        resetSuitTrack = Sequence(suitTrack)
    elif name == CALCULATING_FEES:
        resetSuitTrack = Sequence(suitTrack)
    elif name == SCAPEGOAT_COURT_RECORD_BAN:
        resetSuitTrack = Sequence(suitTrack)
    else:
        resetSuitTrack = Sequence(unlureSuit, resetTrack, suitTrack)
    resetSuitTrack = Sequence(unlureSuit, resetTrack, suitTrack)
    waitTrack = Sequence(Func(battle.unlureSuit, suit))
    resetCamTrack = Sequence(waitTrack, camTrack)
    return (resetSuitTrack, camTrack)


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
   # if suit.dna.name == 'scg' and suit.isAngry:
   #     track.append(ActorInterval(suit, 'neutral-enraged-return', startTime=1, endTime=0))
   #     track.append(Func(suit.loop, 'neutral-enraged'))
   # elif suit.isImmortal and suit.dna.name == 'dsf':
   #     track.append(
    #        Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    #elif suit.isVulnerable and suit.dna.name == 'crf':
    #    track.append(
     #       Func(suit.loop, 'neutral2%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
   # elif suit.isImmortal:
    #    track.append(ActorInterval(suit, 'highroller-neutral-levitate-in-out', startTime=1, endTime=0))
      #  track.append(Func(suit.loop, 'highroller-neutral-levitate-loop'))
    track.append(
            Func(suit.setNeutralAnimation))
    return track

def getSuitAnimTrackHighRoller(attack, delay = 0, splicedAnims = None, playRate = 1.0):
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
       # track.append(
        #    Func(suit.setNeutralAnimation))
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

def doNoAttack(attack):
    name = attack['id']
    suit = attack['suit']
    battle = attack['battle']
    currentBossHealth = -1
    if suit.isImmortal and not suit.dna.name == 'dsf':
        suitTrack = Sequence(ActorInterval(suit, 'highroller-neutral-levitate-in-out', startTime=1, endTime=0), Func(suit.loop, 'neutral2%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '',)))
        suitTrack.append(Func(suit.makeNonImmortal))
    else:
        suitTrack = Sequence()
    for s in battle.suits:
        if s.dna.name == 'mad' and s.maxHP == 12000:
            currentBossHealth = s.currHP
    if currentBossHealth >= 1:
        for s in battle.activeSuits:
            suitTrack.append(Func(s.makeLureImmune))
    if currentBossHealth <= 0:
        for s in battle.activeSuits:
            suitTrack.append(Func(s.makeUnLureImmune))
    return suitTrack

def playSplashEffect(render, x, y, z):
    from toontown.effects import Splash
    splash = Splash.Splash(render)

    splash.setPos(x, y, z)
    splash.setScale(2)
    splash.play()

def doSplashback(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTracks = Parallel()
    posPoints = [Point3(-0.5, 0, -1), VBase3(0, 0, 0)]
    knifeTracks = Parallel()
    notifyTracks = Parallel()
    splashTracks = Parallel()
    toonTracks = Parallel()
    soundTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        toonPos = toon.getPos(battle)
        suitTrack = getSuitTrack(attack, playRate=2)
        knife = globalPropPool.getProp('waterBalloon')
        splashdown = globalPropPool.getProp('splashdown')
        splashdown.setScale(1)
        #ta = TransparencyAttrib.make(TransparencyAttrib.MBinary)
        #splashdown.node().setAttrib(ta, 1)
        #splashdown.setBin('fixed', 130, 1)
        animDuration = splashdown.getDuration('splashdown')
        splashTrack = Sequence(Wait(4.0), Func(splashdown.reparentTo, toon), Func(splashdown.show), ActorInterval(splashdown, 'splashdown'), Wait(animDuration), Func(splashdown.hide))
        knifeTrack = Sequence(
            getPropAppearTrack(knife, suit.getRightHand(), posPoints, 0.25, scaleUpPoint=Point3(1.0), scaleUpTime=0.1),
            Wait(1.3),
            Parallel(
                getThrowTrack(knife, toon.getPos(battle), 2.35, battle, -64.288),
                LerpHprInterval(knife, 0.8, VBase3(720, 630, 720))
            ),
            Func(MovieUtil.removeProp, knife)
        )
        damageAnims = [['slip-forward', 0.01, 0.4]]
        toonTrack = getToonTracksCheat(attack, damageDelay=4.0, splicedDamageAnims=damageAnims, dodgeDelay=3.1,
                                        dodgeAnimNames=['neutral'])
        notifyTrack = Sequence(Wait(4.0), Func(toon.showHpTextCheat, - int(dmg)),
                               Func(toon.showHpString, "SOAKED?!"))
        soundTrack = getSoundTrack('SA_watercooler_spray_only.ogg', delay=4.0, node=suit)
        if dmg > 0:
            knifeTracks.append(knifeTrack)
            notifyTracks.append(notifyTrack)
            splashTracks.append(splashTrack)
            suitTracks.append(suitTrack)
            soundTracks.append(soundTrack)
            toonTracks.append(toonTrack)
    return Parallel(suitTracks, knifeTracks, toonTracks, soundTracks, splashTracks, notifyTracks)

def doVulnerable(attack):
    name = attack['id']
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(Func(suit.makeVulnerable))
    return suitTrack

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

def doSnipeDamageReduction(attack):
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
                               Func(toon.showHpStringSnipe, "GAG DEBUFF!"))
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

def doSingingBlues(attack):
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
    toonTracks = getToonTracks(attack, 2.8, ['slip-backward'], 4.7, ['jump'])
    soundTrack = getSoundTrack('SA_hangup.ogg', delay=0.5, node=suit)
    soundTrack1 = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=2.8, node=suit)
    return Parallel(suitTrack, propTrack, soundTrack, soundTrack1, toonTracks, explodeTracks, explosionTrack)

def doGameTimeSpawn(attack):
    name = attack['id']
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack2 = Sequence(MovieUtil.createSuitSnapInterval(suit), Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(3.0))
    soundTrack = getSoundTrack('SA_bash.ogg', node=suit)
    return Parallel(suitTrack, soundTrack)

def doSyphon(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    for t in targets:
        dmg = t['hp']
    suitTrack = Sequence(getSuitAnimTrack(attack), Func(suit.setNeutralAnimation))
    suitTrack.append(Func(suit.setHealthForMe, + ((dmg * 4) * len(battle.activeToons))))
    suitTrack.append(Wait(2.0))
    toonTrack = getToonTracks(attack, 0.6, ['slip-forward'], 0.01, ['applause'])
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=0.2, node=suit)
    selfDamageTrack = Sequence(Wait(2), Func(suit.showHpTextCheat, +((dmg * 4) * len(battle.activeToons))), Func(suit.showHpString, "SYPHONED!", openEnded=0), Func(suit.updateHealthBar, 0), soundTrack2)
    multiTrackList = Parallel(suitTrack, toonTrack, selfDamageTrack)
    if dmg > 0:
        soundTrack = getSoundTrack('AA_drop_safe_miss.ogg', delay=0.2, node=suit)
        multiTrackList.append(soundTrack)
    return multiTrackList

def doDonation(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    theSuit = None
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    for s in battle.activeSuits:
        if s.dna.name == 'crf':
            print('Found manager... using it...')
            theSuit = s

    if theSuit == None:
        print('Error finding manager... using self...')
        theSuit = suit

    print('*************************************')

    print('suit.currHP %i' % int(suit.currHP))
    print('setHP() %i' % int(suit.currHP - (suit.currHP / 4)))
    print('suit.currHP %i' % int(suit.currHP))

    print('ts.currHP %i' % int(theSuit.currHP))
    print('setHP() %i' % int(theSuit.currHP + (suit.currHP / 4)))
    print('ts.currHP %i' % int(theSuit.currHP))

    resetPos, resetHpr = battle.getActorPosHpr(suit)
    sinkPos = suit.getPos(battle)
    dropPos = suit.getPos(battle)
    sinkPos2 = suit.getPos(battle)
    dropPos2 = suit.getPos(battle)
    sinkPos.setY(sinkPos.getY() + 12.5)
    sinkPos.setZ(sinkPos.getZ() - 4.5)
    sinkPos2.setY(sinkPos.getY() - 22.5)
    moveTrack = Sequence(LerpPosInterval(suit, 1.5, sinkPos2, other=battle), LerpPosInterval(suit, 0, sinkPos, other=battle), Wait(3.9), LerpPosInterval(suit, 0, sinkPos2, other=battle), LerpPosInterval(suit, 1.5, dropPos, other=battle), Func(suit.setPos, battle, dropPos))

    suitTrack = Sequence(ActorInterval(suit, 'walk'), getSuitAnimTrack(attack), ActorInterval(suit, 'walk'))
    selfDamageTrack = Sequence(Wait(4.0), Func(suit.showHpText, -(suit.currHP / 4)), Func(suit.updateHealthBar, 0))
    selfDamageTrack.append(Func(suit.setHealthForMe, - (suit.currHP / 4)))
    managerHealTrack = Sequence(Wait(4.0), Func(theSuit.showHpText, (suit.currHP / 4)), Func(theSuit.updateHealthBar, 0),
                                Func(theSuit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHighRollerPhrases),
                                     CFSpeech | CFTimeout),
                                SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'), node=theSuit))
    managerHealTrack.append(Func(theSuit.setHealthForMe, + (suit.currHP / 4)))
    return Parallel(suitTrack, moveTrack, selfDamageTrack, managerHealTrack)

def createTNTExplosionTrack(parent, explosionPoint = None, scale = 1.0):
    explosionTrack = Sequence()
    explosion = BattleProps.globalPropPool.getProp('kapow')
    explosion.setBillboardPointEye()
    explosion.setDepthWrite(False)
    if not explosionPoint:
        explosionPoint = Point3(0, 3.6, 2.1)
    explosionTrack.append(Func(explosion.reparentTo, parent))
    explosionTrack.append(Func(explosion.setPos, explosionPoint))
    explosionTrack.append(Func(explosion.setScale, 0.4 * scale))
    explosionTrack.append(ActorInterval(explosion, 'kapow'))
    explosionTrack.append(Wait(0.6))
    explosionTrack.append(Func(MovieUtil.removeProp, explosion))
    return explosionTrack


def doBar(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']

    ship = loader.loadModel('phase_10/models/cashbotHQ/GoldBar')
    ship4 = loader.loadModel('phase_10/models/cashbotHQ/GoldBar')
    ship.setScale(4.085, 4.342, 2.928)
    ship4.setScale(4.085, 4.342, 2.928)
    freeCruiseDelay = 0
    suitTracks = Parallel()
    toonTracks = Parallel()
    soundTrack2 = getSoundTrack('SA_bash.ogg', node=suit)
    for suit in battle.activeSuits:
        suitTrack = getSuitAnimTrack(attack)
        suitTrack.append(Wait(1.35))
        suitTrack.append(Func(suit.setHealthForMe, - (250 * len(battle.activeToons))))
        suitTrack.append(Func(suit.showHpText, - (250 * len(battle.activeToons))))
        suitTrack.append(Func(suit.updateHealthBar, 0))
        suitTrack.append(ActorInterval(suit, 'flatten'))
        suitTracks.append(suitTrack)
        suitTrack.append(Func(suit.setNeutralAnimation))
    objZOffset = 0.0
    landFrames = 2
    node = ship.node()
    node.setBounds(OmniBoundingVolume())
    node.setFinal(1)
    node2 = ship4.node()
    node2.setBounds(OmniBoundingVolume())
    node2.setFinal(1)
    shipTrack = Sequence()
    shipTrack2 = Sequence()

    def posObject(object, toon, miss, battle=battle):
        object.reparentTo(battle)
        object.setPos(toon.getPos(battle))
        object.setHpr(toon.getHpr(battle))
        if miss:
            object.setY(object.getY(battle) - 5)
        object.setZ(object.getPos(battle)[2] + objZOffset)

    def posObject2(object, toon, miss, battle=battle):
        object.reparentTo(battle)
        object.setPos(toon.getPos(battle))
        object.setHpr(toon.getHpr(battle))
        object.setY(object.getY(battle) + 15)
        if miss:
            object.setY(object.getY(battle) - 5)
        object.setZ(object.getPos(battle)[2] + objZOffset)

    shipTrack.append(Func(battle.movie.needRestoreRenderProp, ship))
    shipTrack.append(Wait(2.86 + freeCruiseDelay))
    shipTrack2.append(Func(battle.movie.needRestoreRenderProp, ship4))
    shipTrack2.append(Wait(2.86 + freeCruiseDelay))
    closestTarget = -1
    nearestDistance = 100000.0
    for i in xrange(len(targets)):
        toon = targets[i]['toon']
        toonPos = toon.getPos(battle)
        displacement = Vec3(MovieUtil.calcAvgToonPos(attack))
        displacement -= toonPos
        distance = displacement.lengthSquared()
        if distance < nearestDistance:
            closestTarget = i
            nearestDistance = distance

    hitAtleastOneToon = 1
    shipTrack.append(Func(posObject, ship, targets[closestTarget]['toon'], not hitAtleastOneToon))
    shipTrack2.append(Func(posObject2, ship4, targets[closestTarget]['toon'], not hitAtleastOneToon))
    if hitAtleastOneToon:
        if hasattr(ship, 'getAnimControls'):
            pass  # Not imperative at the moment given the Toontanic does not have the getAnimControls attribute
        elif hasattr(ship4, 'getAnimControls'):
            pass  # Not imperative at the moment given the Toontanic does not have the getAnimControls attribute
        else:
            startingScale = Point3(2.5, 4.5, 1.5)
            ship2 = MovieUtil.copyProp(ship)
            ship3 = MovieUtil.copyProp(ship4)
            suitPos, suitHpr = battle.getActorPosHpr(suit)
            gearPoint = Point3(suitPos.getX() + 5, suitPos.getY() - 5, suitPos.getZ() + suit.height - 1)
            soundTrack = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6))
            explosionTrack = Sequence(Wait(0.5), Parallel(soundTrack, createTNTExplosionTrack(battle, explosionPoint=gearPoint, scale=3)))
            posObject(ship2, targets[closestTarget]['toon'], not hitAtleastOneToon)
            posObject2(ship3, targets[closestTarget]['toon'], not hitAtleastOneToon)
            endingPos = ship2.getPos()
            startPos = Point3(endingPos[0], endingPos[1], endingPos[2] + 5)
            startHpr = ship2.getHpr()
            endingPos2 = ship3.getPos()
            startPos2 = Point3(endingPos2[0], endingPos2[1], endingPos2[2] + 5)
            startHpr2 = ship3.getHpr()
            endHpr = Point3(startHpr[0] + 90, startHpr[1], startHpr[2])
            endHpr2 = Point3(startHpr2[0] + 90, startHpr2[1], startHpr2[2])
            animProp = LerpPosInterval(ship, landFrames / 24.0, endingPos, startPos=startPos)
            shrinkProp = LerpScaleInterval(ship, 0.1, MovieUtil.PNT3_NEARZERO, startScale=startingScale)
            bounceProp = Effects.createZBounce(ship, 2, endingPos, 0.5, 1)
            objAnimShrink = Sequence(Func(ship.setScale, startingScale), Func(ship.setH, endHpr[0]), animProp,
                                     Parallel(bounceProp, explosionTrack), shrinkProp)
            animProp2 = LerpPosInterval(ship4, landFrames / 24.0, endingPos2, startPos=startPos2)
            shrinkProp2 = LerpScaleInterval(ship4, 0.1, MovieUtil.PNT3_NEARZERO, startScale=startingScale)
            bounceProp2 = Effects.createZBounce(ship4, 2, endingPos2, 0.5, 1)
            objAnimShrink2 = Sequence(Func(ship4.setScale, startingScale), Func(ship4.setH, endHpr2[0]), animProp2,
                                     bounceProp2, Wait(1.5), shrinkProp2)
            shipTrack.append(objAnimShrink)
            shipTrack2.append(objAnimShrink2)
            MovieUtil.removeProp(ship2)
            MovieUtil.removeProp(ship3)
    elif hasattr(ship, 'getAnimControls'):
        pass  # Not imperative at the moment given the Toontanic does not have the getAnimControls attribute
    else:
        startingScale = 1.0
        ship2 = MovieUtil.copyProp(ship)
        posObject(ship2, targets[closestTarget]['toon'], not hitAtleastOneToon)
        endingPos = ship2.getPos()
        startPos = Point3(endingPos[0], endingPos[1], endingPos[2] + 5)
        startHpr = ship2.getHpr()
        endHpr = Point3(startHpr[0] + 90, startHpr[1], startHpr[2])
        animProp = LerpPosInterval(ship, landFrames / 24.0, endingPos, startPos=startPos)
        shrinkProp = LerpScaleInterval(ship, 0.1, MovieUtil.PNT3_NEARZERO, startScale=startingScale)
        bounceProp = Effects.createZBounce(ship, 2, endingPos, 0.5, 1)
        objAnimShrink = Sequence(Func(ship.setScale, startingScale), Func(ship.setH, endHpr[0]), animProp, bounceProp,
                                 Wait(1.5), shrinkProp)
        shipTrack.append(objAnimShrink)
        MovieUtil.removeProp(ship2)
    shipTrack.append(Func(MovieUtil.removeProp, ship))
    shipTrack.append(Func(battle.movie.clearRenderProp, ship))
    shipTrack.append(Func(MovieUtil.removeProp, ship4))
    shipTrack.append(Func(battle.movie.clearRenderProp, ship4))
    dropShadow = MovieUtil.copyProp(targets[closestTarget]['toon'].dropShadow)
    dropShadow.setScale(3.6)

    def posShadow(dropShadow=dropShadow, toon=toon, battle=battle, hp=targets[0]['hp']):
        dropShadow.reparentTo(battle)
        dropShadow.setPos(toon.getPos(battle))
        dropShadow.setHpr(toon.getHpr(battle))
        if hp == 0:
            dropShadow.setY(dropShadow.getY(battle) - 5)
        dropShadow.setZ(dropShadow.getZ() + 0.5)

    def posShadow2(dropShadow=dropShadow, toon=toon, battle=battle, hp=targets[0]['hp']):
        dropShadow.reparentTo(battle)
        dropShadow.setPos(toon.getPos(battle))
        dropShadow.setHpr(toon.getHpr(battle))
        dropShadow.setY(dropShadow.getY(battle) + 15)
        if hp == 0:
            dropShadow.setY(dropShadow.getY(battle) - 5)
        dropShadow.setZ(dropShadow.getZ() + 0.5)

    shadowTrack = Sequence(
        Wait(1.0 + freeCruiseDelay),
        Func(battle.movie.needRestoreRenderProp, dropShadow),
        Func(posShadow), Func(posShadow2),
        LerpScaleInterval(dropShadow, 1.86, dropShadow.getScale(), startScale=MovieUtil.PNT3_NEARZERO),
        Wait(0.3),
        Func(MovieUtil.removeProp, dropShadow),
        Func(battle.movie.clearRenderProp, dropShadow)
    )
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        toonTrack2 = Sequence(
        Wait(2.75),
        Parallel(
            Func(toon.enterFlattened),
            Func(toon.showHpText, -dmg, openEnded=0),
            Func(__doDamage, toon, dmg, t['died'])
        ),
        Wait(2.5),
        Parallel(
            Sequence(
                Wait(.5),
                Func(toon.exitFlattened)
            ),
            getSoundTrack('toon_decompress.ogg', node=toon),
            Sequence(
                ActorInterval(toon, 'jump'),
                Func(toon.loop, 'neutral')
            )
        )
    )
        toonTracks.append(toonTrack2)
    hitSounds = Parallel()
    hitSounds.append(getSoundTrack('tt_s_ara_cmg_itemHitsFloor.ogg', delay=2.86 + freeCruiseDelay))
    multiTrackList = Parallel(soundTrack2, suitTracks, shipTrack2, shipTrack, shadowTrack, toonTracks, hitSounds)
    return multiTrackList

def doFreeCruise(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']

    ship = globalPropPool.getProp('ship')
    freeCruiseDelay = 3.1
    suitTrack = getSuitAnimTrack(attack)
    objZOffset = 0.0
    landFrames = 2
    node = ship.node()
    node.setBounds(OmniBoundingVolume())
    node.setFinal(1)
    shipTrack = Sequence()

    def posObject(object, toon, miss, battle=battle):
        object.reparentTo(battle)
        object.setPos(toon.getPos(battle))
        object.setHpr(toon.getHpr(battle))
        if miss:
            object.setY(object.getY(battle) - 5)
        object.setZ(object.getPos(battle)[2] + objZOffset)

    shipTrack.append(Func(battle.movie.needRestoreRenderProp, ship))
    shipTrack.append(Wait(2.86 + freeCruiseDelay))
    closestTarget = -1
    nearestDistance = 100000.0
    for i in xrange(len(targets)):
        toon = targets[i]['toon']
        toonPos = toon.getPos(battle)
        displacement = Vec3(MovieUtil.calcAvgToonPos(attack))
        displacement -= toonPos
        distance = displacement.lengthSquared()
        if distance < nearestDistance:
            closestTarget = i
            nearestDistance = distance

    hitAtleastOneToon = 1
    shipTrack.append(Func(posObject, ship, targets[closestTarget]['toon'], not hitAtleastOneToon))
    if hitAtleastOneToon:
        if hasattr(ship, 'getAnimControls'):
            pass  # Not imperative at the moment given the Toontanic does not have the getAnimControls attribute
        else:
            startingScale = 1.0
            ship2 = MovieUtil.copyProp(ship)
            posObject(ship2, targets[closestTarget]['toon'], not hitAtleastOneToon)
            endingPos = ship2.getPos()
            startPos = Point3(endingPos[0], endingPos[1], endingPos[2] + 5)
            startHpr = ship2.getHpr()
            endHpr = Point3(startHpr[0] + 90, startHpr[1], startHpr[2])
            animProp = LerpPosInterval(ship, landFrames / 24.0, endingPos, startPos=startPos)
            shrinkProp = LerpScaleInterval(ship, 0.1, MovieUtil.PNT3_NEARZERO, startScale=startingScale)
            bounceProp = Effects.createZBounce(ship, 2, endingPos, 0.5, 1)
            objAnimShrink = Sequence(Func(ship.setScale, startingScale), Func(ship.setH, endHpr[0]), animProp,
                                     bounceProp, Wait(1.5), shrinkProp)
            shipTrack.append(objAnimShrink)
            MovieUtil.removeProp(ship2)
    elif hasattr(ship, 'getAnimControls'):
        pass  # Not imperative at the moment given the Toontanic does not have the getAnimControls attribute
    else:
        startingScale = 1.0
        ship2 = MovieUtil.copyProp(ship)
        posObject(ship2, targets[closestTarget]['toon'], not hitAtleastOneToon)
        endingPos = ship2.getPos()
        startPos = Point3(endingPos[0], endingPos[1], endingPos[2] + 5)
        startHpr = ship2.getHpr()
        endHpr = Point3(startHpr[0] + 90, startHpr[1], startHpr[2])
        animProp = LerpPosInterval(ship, landFrames / 24.0, endingPos, startPos=startPos)
        shrinkProp = LerpScaleInterval(ship, 0.1, MovieUtil.PNT3_NEARZERO, startScale=startingScale)
        bounceProp = Effects.createZBounce(ship, 2, endingPos, 0.5, 1)
        objAnimShrink = Sequence(Func(ship.setScale, startingScale), Func(ship.setH, endHpr[0]), animProp, bounceProp,
                                 Wait(1.5), shrinkProp)
        shipTrack.append(objAnimShrink)
        MovieUtil.removeProp(ship2)
    shipTrack.append(Func(MovieUtil.removeProp, ship))
    shipTrack.append(Func(battle.movie.clearRenderProp, ship))
    dropShadow = MovieUtil.copyProp(targets[closestTarget]['toon'].dropShadow)
    dropShadow.setScale(3.6)

    def posShadow(dropShadow=dropShadow, toon=toon, battle=battle, hp=targets[0]['hp']):
        dropShadow.reparentTo(battle)
        dropShadow.setPos(toon.getPos(battle))
        dropShadow.setHpr(toon.getHpr(battle))
        if hp == 0:
            dropShadow.setY(dropShadow.getY(battle) - 5)
        dropShadow.setZ(dropShadow.getZ() + 0.5)

    shadowTrack = Sequence(
        Wait(1.0 + freeCruiseDelay),
        Func(battle.movie.needRestoreRenderProp, dropShadow),
        Func(posShadow),
        LerpScaleInterval(dropShadow, 1.86, dropShadow.getScale(), startScale=MovieUtil.PNT3_NEARZERO),
        Wait(0.3),
        Func(MovieUtil.removeProp, dropShadow),
        Func(battle.movie.clearRenderProp, dropShadow)
    )
    toonTracks = getToonTracks(attack, damageDelay=2.86 + freeCruiseDelay, damageAnimNames=['slip-forward'],
                               dodgeDelay=2.86 + freeCruiseDelay, dodgeAnimNames=['neutral'])
    soundTrack = getSoundTrack('AA_drop_boat%s.ogg' % ('' if hitAtleastOneToon else '_miss'),
                               delay=(0.9 if targets[0]['hp'] == 0 else 1.0) + freeCruiseDelay, node=suit)
    hitSounds = Parallel()
    hitSounds.append(getSoundTrack('AA_drop_boat_cog.ogg', delay=2.86 + freeCruiseDelay))
    suitTrack.append(Func(suit.makeNonImmortal))
    multiTrackList = Parallel(suitTrack, shipTrack, shadowTrack, toonTracks, soundTrack, hitSounds)
    multiTrackList.append(getSoundTrack('AA_heal_happydance.ogg', node=suit))
    return multiTrackList

def doAceInTheHoleOLD(attack):
    suitHighRoller = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    card = globalPropPool.getProp('cc_a_prp_bat_playcard')
    highRollerHead = globalPropPool.getProp('cc_m_chr_ene_highroller')
    taunt = random.choice(
        ["I'm a flying affe, fforaring in the fog! Prepare to be ffcared, babe.", "You know, I've alwayff got an affe up my ffleeve! Ffee?",
         "I'm the biggefft ffenffation, the talk of the town! Hope you haven't forgotten, doll.",
         "It'ff time for my cloffe up! You're getting in all of the action now, folkff!", "Ffhrouded in mifft, you'll ffoon fee who'ff in control of the ffow now!"])
    tauntInterval = Sequence(Func(suitHighRoller.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrackHighRoller = Parallel(ActorInterval(suitHighRoller, 'neutral'), tauntInterval)
    suitTracks = Parallel()
    objZOffset = 0.0
    toonTracks = Parallel()
    def posObject(object, toon, miss, battle=battle):
        object.reparentTo(battle)
        object.setPos(toon.getPos(battle))
        object.setHpr(toon.getHpr(battle))
        if miss:
            object.setY(object.getY(battle) - 5)
        object.setZ(object.getPos(battle)[2] + objZOffset)
    closestTarget = -1
    nearestDistance = 100000.0
    for i in xrange(len(targets)):
        toon = targets[i]['toon']
        toonPos = toon.getPos(battle)
        displacement = Vec3(MovieUtil.calcAvgToonPos(attack))
        displacement -= toonPos
        distance = displacement.lengthSquared()
        if distance < nearestDistance:
            closestTarget = i
            nearestDistance = distance
    cardPos = [Point3(toonPos.getX(), toonPos.getY() - 25, -3.5), toon.getHpr(battle)]
    headPos = [Point3(toonPos.getX(), toonPos.getY() - 25, -3.5), toon.getHpr(battle)]
    scaleUpPoint = Point3(1.1, 1.1, 1.1)
    hitAtleastOneToon = 1
    propTrackHead = Parallel()
    propTrackNew = Parallel()
    propTrackHead.append(Func(posObject, highRollerHead, targets[closestTarget]['toon'], not hitAtleastOneToon))
    propTrackHead.append(Sequence(Wait(5.5),
                             getPropTrack(highRollerHead, battle, headPos, 1e-06, 0, scaleUpPoint=scaleUpPoint,
                                          anim=1, animStartTime=0, animDuration=3.0,
                                          propName='cc_m_chr_ene_highroller'), Wait(1.6)))
    propTrackHead.append(Func(posObject, card, targets[closestTarget]['toon'], not hitAtleastOneToon))
    propTrackNew.append(Sequence(Wait(5.5),
                            getPropTrack(card, battle, cardPos, 1e-06, 0, scaleUpPoint=scaleUpPoint, scaleUpTime=3,
                                         anim=1, animStartTime=0, animDuration=3.0,
                                         propName='cc_a_prp_bat_playcard'), Wait(1.6)))
    for suit in battle.activeSuits:
        suitTrack = Sequence(Wait(3), ActorInterval(suit, 'highroller-neutral-levitate-in-out', startTime=0, endTime=1), Func(suit.loop, 'highroller-neutral-levitate-loop'))
        suitTrack.append(Wait(8))
        suitTrack.append(ActorInterval(suit, 'highroller-neutral-levitate-in-out', startTime=1, endTime=0))
        suitTrack.append(Func(suit.loop, 'neutral'))
        suitTracks.append(suitTrack)
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        toonTrack = Sequence(
        Wait(8.5),
        Parallel(
            Func(toon.enterFlattened),
            Func(toon.showHpTextCheat, - int(dmg)),
            Func(toon.showHpStringSnipe, "VULNERABLE!"),
            Func(__doDamageCheat, toon, dmg, t['died'])
        ),
        Wait(1.0),
        Parallel(
            Sequence(
                Wait(0.5),
                Func(toon.exitFlattened)
            ),
            getSoundTrack('toon_decompress.ogg', node=toon),
            Sequence(
                ActorInterval(toon, 'jump'),
                Func(toon.loop, 'neutral')
            )
        )
    )
        toonTracks.append(toonTrack)
    soundTrack = Sequence(Wait(1.0), SoundInterval(globalBattleSoundCache.getSound('cc_s_sfx_ene_hroller_ace_in_the_hole.ogg')))
    return Parallel(suitTrackHighRoller, suitTracks, toonTracks, propTrackNew, propTrackHead, soundTrack)


def doAceInTheHole(attack):
    suitHighRoller = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    card = globalPropPool.getProp('cc_a_prp_bat_playcard')
    card2 = globalPropPool.getProp('cc_a_prp_bat_playcard2')
    highRollerHead = globalPropPool.getProp('cc_m_chr_ene_highroller')
    taunt = getAttackTaunt(attack['name'], attack['suitName'], attack['taunt'])
    suitTrackHighRoller = Sequence(getSuitAnimTrack(attack))
    suitTracks = Parallel()
    for suit in battle.activeSuits:
        suitTrack = Sequence(Wait(3), ActorInterval(suit, 'highroller-neutral-levitate-in-out', startTime=0, endTime=1),
                             Func(suit.loop, 'highroller-neutral-levitate-loop'))
        suitTrack.append(Wait(8))
        suitTrack.append(ActorInterval(suit, 'highroller-neutral-levitate-in-out', startTime=1, endTime=0))
        suitTrack.append(Func(suit.loop, 'neutral'))
        suitTracks.append(suitTrack)

    headPropTrack = Sequence(
        Wait(5.0),
        Func(__showProp, highRollerHead, battle, Point3(0, -25, -2)),
        ActorInterval(highRollerHead, 'cc_m_chr_ene_highroller'),
        Func(MovieUtil.removeProp, highRollerHead)
    )
    cardPropTrack = Sequence(
        Wait(5.0), Func(__showProp, card2, battle, Point3(0, -25, -2), scale=Point3(1.1, 1.1, 1.1)),
        ActorInterval(card2, 'cc_a_prp_bat_playcard2'),
        Func(MovieUtil.removeProp, card2),
        # I'm not sure of optimal timings, so I'll just copy the old method's timings and let Dissonance decide better ones.  Added 3 more seconds because of the scaleUpTime.
        Func(__showProp, card, battle, Point3(0, -25, -2), scale=Point3(1.1, 1.1, 1.1)),
        ActorInterval(card, 'cc_a_prp_bat_playcard'),
        Func(MovieUtil.removeProp, card))
    toonTracks = Parallel()
    for i in xrange(len(targets)):
        tgt = targets[i]
        toon = tgt['toon']
        dmg = tgt['hp']
        toonTrack = Sequence(
            Wait(8.5),
            Parallel(
                Func(toon.enterFlattened),
                Func(toon.showHpTextCheat, - int(dmg)),
                Func(toon.showHpStringSnipe, "VULNERABLE!"),
                Func(__doDamageCheat, toon, dmg, tgt['died'])
            ),
            Wait(1.0),
            Parallel(
                Sequence(
                    Wait(0.5),
                    Func(toon.exitFlattened)
                ),
                getSoundTrack('toon_decompress.ogg', node=toon),
                Sequence(
                    ActorInterval(toon, 'jump'),
                    Func(toon.loop, 'neutral')
                )
            )
        )
        toonTracks.append(toonTrack)

    soundTrack = getSoundTrack('cc_s_sfx_ene_hroller_ace_in_the_hole.ogg')
    return Parallel(suitTrackHighRoller, suitTracks, toonTracks, headPropTrack, cardPropTrack, soundTrack)

def doTrickOfTheLight(attack):
    suit = attack['suit']
    battle = attack['battle']
    taunt = random.choice(
        ["Every copy of me iff perffonalized.",
         "One ffhowfftopper jufft iffn't enough! There needff to be more!"])
    suitTrack2 = Sequence(getSuitAnimTrackHighRoller(attack))
    suitTrack = Sequence(Wait(2.0), ActorInterval(suit, 'highroller-neutral-levitate-in-out', duration=1), Func(suit.loop, 'highroller-neutral-levitate-loop'), Wait(1.0))
    suitTrack.append(Func(suit.makeImmortal))
    suitTrack.append(Func(suit.makeUnVulnerable))
    return Parallel(suitTrack, suitTrack2)

def doPhase3(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack2 = Sequence(Wait(2.8), ActorInterval(suit, 'song-and-dance'), Func(suit.loop, 'neutral2'))
    suitTrack = Sequence(Func(suit.loop, 'neutral2'), Wait(13.2), MovieUtil.createSuitLaughInterval2(suit), Wait(1.0))
    talkTrack = Sequence(Func(suit.setChatAbsolute, "AND NOW FOR THE FFFTAR OF OUR FFHOW!!!!!!", CFSpeech | CFTimeout), Wait(2.8), Func(suit.setChatAbsolute, "THAT'FF RIGHT EYE-FFPOT FFPOTLIGHT, thiff turnfftyleff been hot all night, let'ff ffee if you can handle the heat!", CFSpeech | CFTimeout), Wait(3.7), Func(suit.setChatAbsolute,  "This duet jufft got a hip hump bump to a five-part big band, babe!", CFSpeech | CFTimeout), Wait(3.7),
                         Func(suit.setChatAbsolute,  "I'm the hottest fftar on fftage! Ffo come on inamorata, let'ff burn a hole in those goggle boffeff!", CFSpeech | CFTimeout), Wait(3.0), Func(suit.setChatAbsolute, "Better ffmile before ya burn out!", CFSpeech | CFTimeout))
    soundTrack1 = getSoundTrack('ttcc_ene_hroller_laugh.ogg', delay=13.2, node=suit)
    suitTrack.append(Func(suit.makeIntoPhase3))
    suitTrack.append(Func(suit.makeImmortal))
    suitTrack.append(Func(suit.makeUnVulnerable))
    return Parallel(talkTrack, suitTrack, suitTrack2, soundTrack1)

def doRolled(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    BattleParticles.loadParticles() # We need to be able to change the color of the particle effects.
    damageDelay = 1.7
    # We want to handle the particle effect differently from Spin since we will be customizing these particle effects.
    sprayEffects = []
    for t in targets:
        sprayEffect = BattleParticles.createParticleEffect(file='spinSpray')
        BattleParticles.setEffectTexture(sprayEffect, 'snow-particle', color=Vec4(random.random(), random.random(), random.random(), 1))
        sprayEffects.append(sprayEffect)

    suitTrack = Sequence(getSuitAnimTrack(attack))
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
        BattleParticles.setEffectTexture(spinEffect1, 'snow-particle', color=Vec4(random.random(), random.random(), random.random(), 1))
        BattleParticles.setEffectTexture(spinEffect2, 'snow-particle', color=Vec4(random.random(), random.random(), random.random(), 1))
        BattleParticles.setEffectTexture(spinEffect3, 'snow-particle', color=Vec4(random.random(), random.random(), random.random(), 1))
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
            spinTracks1.append(getPartTrack(spinEffect1, 1.5, 3.9, [spinEffect1, battle, 0]))
            spinTracks2.append(getPartTrack(spinEffect2, 1.5, 3.9, [spinEffect2, battle, 0]))
            spinTracks3.append(getPartTrack(spinEffect3, 1.5, 3.9, [spinEffect3, battle, 0]))
            soundTracks.append(getSoundTrack('tt_s_ara_cfg_toonInWhirlwind.ogg', delay=2.0, node=suit))
            toonSpinTracks.append(Sequence(Wait(damageDelay + 0.9), LerpHprInterval(toon, 0.7, Point3(-10, 0, 0)), LerpHprInterval(toon, 0.5, Point3(-30, 0, 0)), LerpHprInterval(toon, 0.2, Point3(-60, 0, 0)), LerpHprInterval(toon, 0.7, Point3(-700, 0, 0)), LerpHprInterval(toon, 1.0, Point3(-1310, 0, 0)), LerpHprInterval(toon, 0.4, toon.getHpr()), Wait(0.5)))

    return Parallel(suitTrack, sprayTracks, toonTracks, toonSpinTracks, spinTracks1, spinTracks2, spinTracks3, soundTracks)

def doBust(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    propTracks = Parallel()
    toonTracks = Parallel()
    suitTrackDuration = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        gavel = loader.loadModel('phase_5/models/props/cc_m_bat_prp_dice')
        toonPos = toon.getPos(battle)
        y = toonPos.getY()
        gavelPos = Point3(toonPos.getX(), y, 30)
        propTrack = Sequence(Wait(5.0),
            getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos, VBase3(0, 0, 0)], appearDelay=0.0,
                               scaleUpPoint=Point3(1.5), scaleUpTime=1.5),
            LerpPosInterval(gavel, 0.25, Point3(toonPos.getX(), y, 2.01)),
            LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y, 3)),
            LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y, 2.01)), Sequence(
                Wait(0.5),
                LerpScaleInterval(gavel, .25, MovieUtil.PNT3_ZERO)
            ))

        propTracks.append(propTrack)
        toonTrack = Sequence(
            Wait(6.5),
            Parallel(
                Func(toon.enterFlattened),
                Func(toon.showHpText, -dmg, openEnded=0),
                Func(__doDamage, toon, dmg, t['died'])
            ),
            Wait(1.0),
            Parallel(
                Sequence(
                    Wait(0.5),
                    Func(toon.exitFlattened)
                ),
                getSoundTrack('toon_decompress.ogg', node=toon),
                Sequence(
                    ActorInterval(toon, 'jump'),
                    Func(toon.loop, 'neutral')
                )
            )
        )
        toonTracks.append(toonTrack)
        soundTrack = getSoundTrack('AA_drop_bigweight.ogg', delay=6.5, node=suit)
        suitTrack = Sequence(MovieUtil.createSuitBustInterval(suit))
        talkTrack = Sequence(getSuitAnimTrack(attack))
        soundTrack1 = getSoundTrack('ttcc_ene_hroller_laugh.ogg', delay=0.5, node=suit)
        soundTrack2 = getSoundTrack('SA_bash.ogg', delay=5.0, node=suit)
        suitTrack.append(Func(suit.setNeutralAnimation))
        if dmg > 0:
            return Parallel(talkTrack, suitTrack, soundTrack1, toonTracks, soundTrack, soundTrack2, propTracks)
        else:
            return suitTrackDuration

def doWheelSpin(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(MovieUtil.createSuitLaughInterval(suit))
    if not suit.dna.name == 'crf':
        suitTrack.append(Func(suit.makeImmortal))
        suitTrack.append(Func(suit.makeShielding))
    soundTrack1 = getSoundTrack('ttcc_ene_hroller_laugh.ogg', node=suit)
    soundTrack2 = getSoundTrack('cc_s_sfx_ene_hroller_reappear_after_wheel.ogg', delay=7.0, node=suit)
    soundTrack3 = getSoundTrack('cc_s_sfx_ene_hroller_sweep_before_wheel.ogg', delay=3.0, node=suit)
    suitTrack.append(Func(suit.setNeutralAnimation))
    return Parallel(suitTrack, soundTrack1, soundTrack1, soundTrack2, soundTrack3)

def doDiceRoulette(attack):
    suit = attack['suit']
    battle = attack['battle']
    name = attack['id']
    suitTrack = Sequence(Wait(2.25), MovieUtil.createSuitLaughIntervalDice(suit), Func(suit.setNeutralAnimation))
    suitTrack2 = Sequence(getSuitAnimTrack(attack))
    soundTrack1 = getSoundTrack('ttcc_ene_hroller_laugh.ogg', node=suit)
    soundTrack2 = getSoundTrack('cc_s_sfx_ene_hroller_reappear_after_wheel.ogg', delay=7.0, node=suit)
    soundTrack3 = getSoundTrack('cc_s_sfx_ene_hroller_sweep_before_wheel.ogg', delay=3.0, node=suit)
    soundTrack = Parallel(soundTrack2, soundTrack3)
    if name == HIGH_ROLLER_DICE_ROULETTE_COGS:
        suitTrack.append(doDiceRouletteCogs(attack))
    elif name == HIGH_ROLLER_DICE_ROULETTE_TOONS:
        suitTrack.append(doDiceRouletteToons(attack))
    elif name == HIGH_ROLLER_DICE_ROULETTE_EVERYONE:
        suitTrack.append(doDiceRouletteAll(attack))
    elif name == HIGH_ROLLER_DICE_ROULETTE_NOBODY:
        suitTrack.append(doDiceRouletteNothing(attack))
    return Parallel(suitTrack, soundTrack, suitTrack2)

def doWheelSpin2(attack):
    suit = attack['suit']
    battle = attack['battle']
    #cameraTrack = Sequence(LerpPosHprInterval(camera, duration=1, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'), Wait(1.8), LerpPosHprInterval(camera, duration=0.5, pos=Point3(4, -11, 2), hpr=Point3(30, 0, 0), blendType='easeInOut'), Wait(2), LerpPosHprInterval(camera, duration=0, pos=Point3(3, -5, 10), hpr=Point3(30, -15, 0), blendType='easeInOut'), Wait(3.2), LerpPosHprInterval(camera, duration=0.5, pos=Point3(0, -15, 3), hpr=Point3(0, 10, 0), blendType='easeInOut'))
    suitTrack = Sequence(MovieUtil.createSuitLaughInterval(suit), ActorInterval(suit, 'snap'), Func(suit.setNeutralAnimation))
    talkTrack = Sequence(Wait(8.0), Func(suit.setChatAbsolute, "Alright, alright, let'ff get thoffe efftraff on ffet, baby doll. Bring 'em in.", CFSpeech | CFTimeout), Wait(2.8), Func(suit.setChatAbsolute, "Peep your eyeff, we've got ffo much in fftore today for you!", CFSpeech | CFTimeout))
    soundTrack1 = getSoundTrack('ttcc_ene_hroller_laugh.ogg', node=suit)
    soundTrack2 = getSoundTrack('cc_s_sfx_ene_hroller_reappear_after_wheel.ogg', delay=7.0, node=suit)
    soundTrack3 = getSoundTrack('cc_s_sfx_ene_hroller_sweep_before_wheel.ogg', delay=3.0, node=suit)
    soundTrack4 = getSoundTrack('SA_bash.ogg', delay=8.0, node=suit)
    soundTrack = (Parallel(soundTrack1, soundTrack2, soundTrack3, soundTrack4))
    suitTrack.append(Wait(2.0))
    suitTrack.append(Func(suit.makeImmortal))
    suitTrack.append(Func(suit.makeShielding))
    return Parallel(talkTrack, suitTrack, soundTrack)

def doDiceRouletteCogs(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    taunt = random.choice(
        ["WHAT A TWIFFT!!!",
         "'FFLAM!' What a ffweet ffound!",
         "Now, you ffigned up for thiff!",
         "Here it comeff, boyff!", ])
    suitTrack = Parallel(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    propTracks = Parallel()
    toonTracks = Parallel()
    for suit in battle.activeSuits:
        gavel = loader.loadModel('phase_5/models/props/cc_m_bat_prp_dice')
        toonPos = suit.getPos(battle)
        y = toonPos.getY()
        gavelPos = Point3(toonPos.getX(), y, 30)
        propTrack = Sequence(
            getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos, VBase3(0, 0, 0)], appearDelay=0.0,
                               scaleUpPoint=Point3(2), scaleUpTime=1.5),
            LerpPosInterval(gavel, 0.25, Point3(toonPos.getX(), y, 2.01)),
            LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y, 3)),
            LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y, 2.01)), Sequence(
                Wait(1.5),
                LerpScaleInterval(gavel, .25, MovieUtil.PNT3_ZERO)
            ))
        propTracks.append(propTrack)
        toonTrack = Sequence(
            Wait(1.5),
            Parallel(
                ActorInterval(suit, 'flatten'),
                Func(suit.setHealthForMe, -250),
                Func(suit.showHpText, -250),
                Func(suit.updateHealthBar, 0)
            ))
        toonTrack.append(
                Func(suit.setNeutralAnimation))
        toonTracks.append(toonTrack)
    soundTrack = getSoundTrack('AA_drop_bigweight.ogg', delay=1.5, node=suit)
    return Parallel(suitTrack, toonTracks, propTracks, soundTrack)

def doDiceRouletteNothing(attack):
    suit = attack['suit']
    taunt = random.choice(
        ["Look'ff like nuffin!", "Aww ratff, a total bufft!!",
         "Ffhew! Now that waff a cloffe call, waffn't it, folkff?",
         "Lady Luck iff merffiful today, huh?",
         "And THAT iff why they call you our LUCKY contefftantff!"])
    suitTrack = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout), Wait(2.0))
    suitTrack.append(Wait(1.0))
    return suitTrack

def doDiceRouletteAll(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    taunt = random.choice(
        ["WHAT A TWIFFT!!!",
         "'FFLAM!' What a ffweet ffound!",
         "Now, you ffigned up for thiff!",
         "Here it comeff, boyff!", ])
    suitTrack = Parallel(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    propTracks = Parallel()
    toonTracks = Parallel()
    propTracks2 = Parallel()
    toonTracks2 = Parallel()
    for suit in battle.activeSuits:
        gavel = loader.loadModel('phase_5/models/props/cc_m_bat_prp_dice')
        toonPos = suit.getPos(battle)
        y = toonPos.getY()
        gavelPos = Point3(toonPos.getX(), y, 30)
        propTrack = Sequence(
            getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos, VBase3(0, 0, 0)], appearDelay=0.0,
                               scaleUpPoint=Point3(2.5), scaleUpTime=1.5),
            LerpPosInterval(gavel, 0.25, Point3(toonPos.getX(), y, 2.01)),
            LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y, 3)),
            LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y, 2.01)), Sequence(
                Wait(1.5),
                LerpScaleInterval(gavel, .25, MovieUtil.PNT3_ZERO)
            ))
        propTracks.append(propTrack)
        toonTrack = Sequence(
            Wait(1.5),
            Parallel(
                ActorInterval(suit, 'flatten'),
                Func(suit.setHealthForMe, - (250 * len(battle.activeToons))),
                Func(suit.showHpText, - (250 * len(battle.activeToons))),
                Func(suit.updateHealthBar, 0)
            ))
        toonTrack.append(
            Func(suit.setNeutralAnimation))
        toonTracks.append(toonTrack)
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        gavel = loader.loadModel('phase_5/models/props/cc_m_bat_prp_dice')
        toonPos = toon.getPos(battle)
        y = toonPos.getY()
        gavelPos = Point3(toonPos.getX(), y, 30)
        propTrack2 = Sequence(
            getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos, VBase3(0, 0, 0)], appearDelay=0.0,
                               scaleUpPoint=Point3(1), scaleUpTime=1.5),
            LerpPosInterval(gavel, 0.25, Point3(toonPos.getX(), y, 1)),
            LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y, 2)),
            LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y, 1)), Sequence(
                Wait(1.5),
                LerpScaleInterval(gavel, .25, MovieUtil.PNT3_ZERO)
            ))

        propTracks2.append(propTrack2)
        toonTrack2 = Sequence(
            Wait(1.75),
            Parallel(
                Func(toon.enterFlattened),
                Func(toon.showHpText, -dmg, openEnded=0),
                Func(__doDamage, toon, dmg, t['died'])
            ),
            Wait(1.75),
            Parallel(
                Sequence(
                    Wait(.5),
                    Func(toon.exitFlattened)
                ),
                getSoundTrack('toon_decompress.ogg', node=toon),
                Sequence(
                    ActorInterval(toon, 'jump'),
                    Func(toon.loop, 'neutral')
                )
            )
        )
        toonTracks2.append(toonTrack2)
    soundTrack = getSoundTrack('AA_drop_bigweight.ogg', delay=1.5, node=suit)
    return Parallel(suitTrack, toonTracks, toonTracks2, propTracks2, propTracks, soundTrack)

def doCommercialBreak(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    toon = attack['target']
    suitTracks = Parallel()
    suitTrackHighRoller = Sequence(getSuitAnimTrack(attack))
    suitTrackHighRoller.append(Wait(3.0))
    soundTrack = getSoundTrack('SA_bash.ogg')
    for suit in battle.activeSuits:
        suitTrack = Sequence()
        if not suit.dna.name == 'dsf':
            suitTrack.append(Wait(1.0))
            suitTrack.append(Parallel(ActorInterval(suit, 'soak'), MovieUtil.shortCircuitTrack(suit, battle)))
        suitTracks.append(suitTrack)
    return Parallel(suitTracks, soundTrack, suitTrackHighRoller)

def doDiceRouletteToons(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    taunt = random.choice(
        ["Can't ffquaffh and fftretch your way out of thiff one, Toonff!", "Who'ff ready for ffome cartoon violenffe?!",
         "FForry, babe, but the ratingff don't lie! Thiff iff what the viewerff want!",
         "And the ratingff FFKYROCKET!!!",
         "If it meanff anything, thiff iff gonna hurt me a lot more than it hurtff you!",
         "'Ker-ffplat!' HahaHAHA!!! You Toonff really are funny!"])
    suitTrack = Parallel(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    propTracks = Parallel()
    toonTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        gavel = loader.loadModel('phase_5/models/props/cc_m_bat_prp_dice')
        toonPos = toon.getPos(battle)
        y = toonPos.getY()
        gavelPos = Point3(toonPos.getX(), y, 30)
        propTrack = Sequence(
        getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos, VBase3(0, 0, 0)], appearDelay=0.0,
                           scaleUpPoint=Point3(1), scaleUpTime=1.5),
        LerpPosInterval(gavel, 0.25, Point3(toonPos.getX(), y, 1)),
        LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y, 2)),
        LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y, 1)), Sequence(
            Wait(1.5),
            LerpScaleInterval(gavel, .25, MovieUtil.PNT3_ZERO)
        ))

        propTracks.append(propTrack)
        toonTrack = Sequence(
        Wait(1.75),
        Parallel(
            Func(toon.enterFlattened),
            Func(toon.showHpText, -dmg, openEnded=0),
            Func(__doDamage, toon, dmg, t['died'])
        ),
        Wait(1.75),
        Parallel(
            Sequence(
                Wait(.5),
                Func(toon.exitFlattened)
            ),
            getSoundTrack('toon_decompress.ogg', node=toon),
            Sequence(
                ActorInterval(toon, 'jump'),
                Func(toon.loop, 'neutral')
            )
        )
        )
        toonTracks.append(toonTrack)
    soundTrack = getSoundTrack('AA_drop_bigweight.ogg', delay=1.5, node=suit)
    return Parallel(suitTrack, toonTracks, soundTrack, propTracks)

def doDamageReduction(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = Sequence(getSuitAnimTrack(attack))
    propTracks = Parallel()
    toonTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        piano = globalPropPool.getProp('piano')
        safe = globalPropPool.getProp('safe')
        boulder = globalPropPool.getProp('boulder')
        weight = globalPropPool.getProp('weight')
        toonPos = toon.getPos(battle)
        toonHpr = battle.getActorPosHpr(toon)
        y = toonPos.getY()
        propPos = Point3(toonPos.getX(), y, 30)
        soundTrack2 = getSoundTrack('AA_drop_piano.ogg', delay=1.75, node=suit)
        soundTrack3 = getSoundTrack('AA_drop_boulder.ogg', delay=1.75, node=suit)
        soundTrack4 = getSoundTrack('AA_drop_safe.ogg', delay=1.75, node=suit)
        soundTrack5 = getSoundTrack('AA_drop_bigweight.ogg', delay=1.75, node=suit)
        propTrack = Sequence(Func(piano.reparentTo, battle),
        getPropAppearTrack(piano, parent=battle, posPoints=[propPos, VBase3(180, 90, 0)], appearDelay=0.0,
                           scaleUpPoint=Point3(3), scaleUpTime=1.5),
        LerpPosInterval(piano, 0.25, Point3(toonPos.getX(), y, 1)),
        LerpPosInterval(piano, 0.1, Point3(toonPos.getX(), y, 2)),
        LerpPosInterval(piano, 0.1, Point3(toonPos.getX(), y, 1)), Sequence(
            Wait(1.5),
            LerpScaleInterval(piano, .25, MovieUtil.PNT3_ZERO)
        ))
        propTrack2 = Sequence(Func(safe.reparentTo, battle),
            getPropAppearTrack(safe, parent=battle, posPoints=[propPos, VBase3(0, 0, 0)], appearDelay=0.0,
                               scaleUpPoint=Point3(4.5), scaleUpTime=1.5),
            LerpPosInterval(safe, 0.25, Point3(toonPos.getX(), y, 0)),
            LerpPosInterval(safe, 0.1, Point3(toonPos.getX(), y, 1)),
            LerpPosInterval(safe, 0.1, Point3(toonPos.getX(), y, 0)), Sequence(
                Wait(1.5),
                LerpScaleInterval(safe, .25, MovieUtil.PNT3_ZERO)
            ))
        propTrack3 = Sequence(Func(boulder.reparentTo, battle),
            getPropAppearTrack(boulder, parent=battle, posPoints=[propPos, VBase3(0, 90, 0)], appearDelay=0.0,
                               scaleUpPoint=Point3(2), scaleUpTime=1.5),
            LerpPosInterval(boulder, 0.25, Point3(toonPos.getX(), y, 0)),
            LerpPosInterval(boulder, 0.1, Point3(toonPos.getX(), y, 1)),
            LerpPosInterval(boulder, 0.1, Point3(toonPos.getX(), y, 0)), Sequence(
                Wait(1.5),
                LerpScaleInterval(boulder, .25, MovieUtil.PNT3_ZERO)
            ))
        propTrack4 = Sequence(Func(weight.reparentTo, battle),
            getPropAppearTrack(weight, parent=battle, posPoints=[propPos, VBase3(0, 0, 0)], appearDelay=0.0,
                               scaleUpPoint=Point3(.75), scaleUpTime=1.5),
            LerpPosInterval(weight, 0.25, Point3(toonPos.getX(), y, 0)),
            LerpPosInterval(weight, 0.1, Point3(toonPos.getX(), y, 1)),
            LerpPosInterval(weight, 0.1, Point3(toonPos.getX(), y, 0)), Sequence(
                Wait(1.5),
                LerpScaleInterval(weight, .25, MovieUtil.PNT3_ZERO)
            ))
        if dmg > 0:
            propTracks.append(random.choice((Parallel(propTrack, soundTrack2), Parallel(propTrack2, soundTrack4), Parallel(propTrack3, soundTrack3), Parallel(propTrack4, soundTrack5))))
        toonTrack = Sequence(
        Wait(1.75),
        Parallel(
            Func(toon.enterFlattened),
            Func(toon.showHpTextCheat, - int(dmg)),
            Func(toon.showHpString, "DAZED?!"),
            Func(__doDamageCheat, toon, dmg, t['died'])
        ),
        Wait(1.75),
        Parallel(
            Sequence(
                Wait(.5),
                Func(toon.exitFlattened)
            ),
            getSoundTrack('toon_decompress.ogg', node=toon),
            Sequence(
                ActorInterval(toon, 'jump'),
                Func(toon.loop, 'neutral')
            )
        )
        )
        if dmg > 0:
            toonTracks.append(toonTrack)
    soundTrack = getSoundTrack('SA_bash.ogg', node=suit)
    return Parallel(suitTrack, toonTracks, soundTrack, propTracks)

def doGameTimeCog2(attack, ind):
    manager = attack['suit']
    battle = attack['battle']
    toons = attack['target']
    targetSuit = battle.activeSuits[ind]
    soundTrack3 = getSoundTrack('cc_s_bgm_ara_hroller_int_stinger.ogg', node=manager)
    taunt = random.choice(("Well, babe, let'ff not keep them waiting! HAHAHA!!!",
"Come on, babe, FFHOW UFF THOFFE NUMBERFF!",
"Better hope for ffome HIGH ROLLERFF! HAHAHAHA!",
"Ready to find out which one of you iff really the weakefft link?!",
"WAFFN'T THAT FUN? Let'ff ffee how you did!"))
    x = int((targetSuit.maxHP * targetSuit.hardMaxHP) - targetSuit.currHP)
    cage = globalPropPool.getProp('ttcc_gag_stagelight')
    texture = loader.loadTexture('phase_5/maps/battle/ttcc_gag_stagelight.png')
    texture2 = loader.loadTexture('phase_3/maps/ttcc_lights_palette.png')
    cage.find('**/stagelight').setTexture(texture, 1)
    cage.find('**/spotlight').setTexture(texture2, 1)
    cagePosition = LerpHprInterval(cage, 0, Point3(180, 0, 0))
    suitPos = targetSuit.getPos(battle)
    y = suitPos.getY()
    cagePos = [Point3(0, 0, targetSuit.height + 15), targetSuit.getHpr(battle)]
    for headPart in targetSuit.headParts:
        head = headPart
    cagePropTrack = Sequence(
        getPropAppearTrack(cage, targetSuit, cagePos, 1, scaleUpPoint=Point3(1.5, 1.5, 1.5), scaleUpTime=0),
        Wait(13), SoundInterval(globalBattleSoundCache.getSound('AA_cog_shock.ogg'), node=targetSuit),
        Func(cage.find('**/spotlight').hide),
        Parallel(cagePosition, Func(cage.reparentTo, head)),
        Parallel(cage.posInterval(0.1, Point3(0, 0, 0), blendType='easeIn')), Wait(2),
        LerpFunctionInterval(cage.setAlphaScale, fromData=.5, toData=0, duration=0.5),
        Func(MovieUtil.removeProp, cage)
        )
    managerTrack = Sequence(getSuitAnimTrack(attack), Func(manager.setNeutralAnimation), Wait(18.0))
    managerTrackQuestion = Parallel(Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                       "In the standard Sellbot Factory, what is the name of the Factory Foreman's special ability?",
                                                       CFSpeech | CFTimeout),
                                       Sequence(Wait(5.0), Func(manager.setChatAbsolute,
                                                       taunt,
                                                       CFSpeech | CFTimeout), Parallel(ActorInterval(manager, 'song-and-dance'), soundTrack3, Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                       "Ha-HA!",
                                                       CFSpeech | CFTimeout))))))
    suitTrackQuestion = Sequence(Wait(1.0), Parallel(ActorInterval(targetSuit, 'mob-mentality'), Func(targetSuit.setChatAbsolute,
                                                       "It's my time to shine!", CFSpeech | CFTimeout), Func(targetSuit.setNeutralAnimation)), Wait(3.0), Func(targetSuit.setChatAbsolute,
                                                       "Union Bust!", CFSpeech | CFTimeout), Wait(7.0), Func(targetSuit.loop, 'large-zap'), MovieUtil.shortCircuitTrack(targetSuit, battle))
    managerTrackQuestion2 = Parallel(Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                             "Who does the Major Player fancy?",
                                                             CFSpeech | CFTimeout),
                                             Sequence(Wait(5.0), Func(manager.setChatAbsolute,
                                                                      taunt,
                                                                      CFSpeech | CFTimeout),
                                                      Parallel(ActorInterval(manager, 'song-and-dance'), soundTrack3,
                                                               Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                                                        "Ha-HA!",
                                                                                        CFSpeech | CFTimeout))))))
    suitTrackQuestion2 = Sequence(Wait(1.0),
                                 Parallel(ActorInterval(targetSuit, 'mob-mentality'), Func(targetSuit.setChatAbsolute,
                                                                                           "It's my time to shine!",
                                                                                           CFSpeech | CFTimeout),
                                          Func(targetSuit.setNeutralAnimation)), Wait(3.0),
                                 Func(targetSuit.setChatAbsolute,
                                      "The Flunky!", CFSpeech | CFTimeout), Wait(7.0),
                                 Func(targetSuit.loop, 'large-zap'), MovieUtil.shortCircuitTrack(targetSuit, battle))
    managerTrackQuestion3 = Parallel(Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                             "Which hand does the Head Attorney use during 'Objection'?",
                                                             CFSpeech | CFTimeout),
                                             Sequence(Wait(5.0), Func(manager.setChatAbsolute,
                                                                      taunt,
                                                                      CFSpeech | CFTimeout),
                                                      Parallel(ActorInterval(manager, 'song-and-dance'), soundTrack3,
                                                               Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                                                        "Ha-HA!",
                                                                                        CFSpeech | CFTimeout))))))
    suitTrackQuestion3 = Sequence(Wait(1.0),
                                 Parallel(ActorInterval(targetSuit, 'mob-mentality'), Func(targetSuit.setChatAbsolute,
                                                                                           "It's my time to shine!",
                                                                                           CFSpeech | CFTimeout),
                                          Func(targetSuit.setNeutralAnimation)), Wait(3.0),
                                 Func(targetSuit.setChatAbsolute,
                                      "Right!", CFSpeech | CFTimeout), Wait(7.0),
                                 Func(targetSuit.loop, 'large-zap'), MovieUtil.shortCircuitTrack(targetSuit, battle))
    managerTrackQuestion4 = Parallel(Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                             "TRUE or FALSE: The longest employee position name int he company is the Public Relations Representative?",
                                                             CFSpeech | CFTimeout),
                                             Sequence(Wait(5.0), Func(manager.setChatAbsolute,
                                                                      taunt,
                                                                      CFSpeech | CFTimeout),
                                                      Parallel(ActorInterval(manager, 'song-and-dance'), soundTrack3,
                                                               Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                                                        "Ha-HA!",
                                                                                        CFSpeech | CFTimeout))))))
    suitTrackQuestion4 = Sequence(Wait(1.0),
                                 Parallel(ActorInterval(targetSuit, 'mob-mentality'), Func(targetSuit.setChatAbsolute,
                                                                                           "It's my time to shine!",
                                                                                           CFSpeech | CFTimeout),
                                          Func(targetSuit.setNeutralAnimation)), Wait(3.0),
                                 Func(targetSuit.setChatAbsolute,
                                      "FALSE!", CFSpeech | CFTimeout), Wait(7.0),
                                 Func(targetSuit.loop, 'large-zap'), MovieUtil.shortCircuitTrack(targetSuit, battle))
    managerTrackQuestion5 = Parallel(Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                             "Who is the Name Dropper planning on having lunch with?",
                                                             CFSpeech | CFTimeout),
                                             Sequence(Wait(5.0), Func(manager.setChatAbsolute,
                                                                      taunt,
                                                                      CFSpeech | CFTimeout),
                                                      Parallel(ActorInterval(manager, 'song-and-dance'), soundTrack3,
                                                               Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                                                        "Ha-HA!",
                                                                                        CFSpeech | CFTimeout))))))
    suitTrackQuestion5 = Sequence(Wait(1.0),
                                 Parallel(ActorInterval(targetSuit, 'mob-mentality'), Func(targetSuit.setChatAbsolute,
                                                                                           "It's my time to shine!",
                                                                                           CFSpeech | CFTimeout),
                                          Func(targetSuit.setNeutralAnimation)), Wait(3.0),
                                 Func(targetSuit.setChatAbsolute,
                                      "The Mingler!", CFSpeech | CFTimeout), Wait(7.0),
                                 Func(targetSuit.loop, 'large-zap'), MovieUtil.shortCircuitTrack(targetSuit, battle))
    managerTrackQuestion6 = Parallel(Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                              "What does the acronym C.O.G.S. stand for?",
                                                              CFSpeech | CFTimeout),
                                              Sequence(Wait(5.0), Func(manager.setChatAbsolute,
                                                                       taunt,
                                                                       CFSpeech | CFTimeout),
                                                       Parallel(ActorInterval(manager, 'song-and-dance'), soundTrack3,
                                                                Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                                                         "Ha-HA!",
                                                                                         CFSpeech | CFTimeout))))))
    suitTrackQuestion6 = Sequence(Wait(1.0),
                                  Parallel(ActorInterval(targetSuit, 'mob-mentality'), Func(targetSuit.setChatAbsolute,
                                                                                            "It's my time to shine!",
                                                                                            CFSpeech | CFTimeout),
                                           Func(targetSuit.setNeutralAnimation)), Wait(3.0),
                                  Func(targetSuit.setChatAbsolute,
                                       "Crush Organics until Green and Sad!", CFSpeech | CFTimeout), Wait(7.0),
                                  Func(targetSuit.loop, 'large-zap'), MovieUtil.shortCircuitTrack(targetSuit, battle))
    selfDamageTrack = Sequence(Wait(14), Func(targetSuit.showHpTextCheat, - targetSuit.currHP), Func(targetSuit.showHpString, "WRONG ANSWER!"),
                               Func(targetSuit.setHealthForMe, - targetSuit.currHP),
                               Func(targetSuit.updateHealthBar, 0))
    suitTrack = random.choice((Parallel(managerTrackQuestion, suitTrackQuestion), Parallel(managerTrackQuestion2, suitTrackQuestion2), Parallel(managerTrackQuestion3, suitTrackQuestion3)
                               , Parallel(managerTrackQuestion5, suitTrackQuestion5), Parallel(managerTrackQuestion6, suitTrackQuestion6), Parallel(managerTrackQuestion4, suitTrackQuestion4)))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_bash.ogg'), node=manager))
    soundTrack2 = getSoundTrack('LB_camera_shutter_2.ogg', delay=1, node=manager)
    return Parallel(managerTrack, suitTrack, soundTrack, soundTrack2, cagePropTrack, selfDamageTrack)

def doGameTimeCog(attack, ind):
    manager = attack['suit']
    battle = attack['battle']
    toons = attack['target']
    targetSuit = battle.activeSuits[ind]
    soundTrack3 = getSoundTrack('cc_s_bgm_ara_hroller_int_stinger.ogg', node=manager)
    taunt = random.choice(("Well, babe, let'ff not keep them waiting! HAHAHA!!!",
"Come on, babe, FFHOW UFF THOFFE NUMBERFF!",
"Better hope for ffome HIGH ROLLERFF! HAHAHAHA!",
"Ready to find out which one of you iff really the weakefft link?!",
"WAFFN'T THAT FUN? Let'ff ffee how you did!"))
    x = int((targetSuit.maxHP * targetSuit.hardMaxHP) - targetSuit.currHP)
    cage = globalPropPool.getProp('ttcc_gag_stagelight')
    texture = loader.loadTexture('phase_5/maps/battle/ttcc_gag_stagelight.png')
    texture2 = loader.loadTexture('phase_3/maps/ttcc_lights_palette.png')
    cage.find('**/stagelight').setTexture(texture, 1)
    cage.find('**/spotlight').setTexture(texture2, 1)
    cagePosition = LerpHprInterval(cage, 0, Point3(180, 0, 0))
    suitPos = targetSuit.getPos(battle)
    y = suitPos.getY()
    cagePos = [Point3(0, 0, targetSuit.height + 15), targetSuit.getHpr(battle)]
    for headPart in targetSuit.headParts:
        head = headPart
    cagePropTrack = Sequence(
        getPropAppearTrack(cage, targetSuit, cagePos, 1, scaleUpPoint=Point3(1.5, 1.5, 1.5), scaleUpTime=0),
        Wait(13), SoundInterval(globalBattleSoundCache.getSound('AA_cog_shock.ogg'), node=targetSuit),
        Func(cage.find('**/spotlight').hide),
        Parallel(cagePosition, Func(cage.reparentTo, head)),
        Parallel(cage.posInterval(0.1, Point3(0, 0, 0), blendType='easeIn')), Wait(2),
        LerpFunctionInterval(cage.setAlphaScale, fromData=.5, toData=0, duration=0.5),
        Func(MovieUtil.removeProp, cage)
    )
    managerTrack = Sequence(getSuitAnimTrack(attack), Func(manager.setNeutralAnimation), Wait(18.0))
    managerTrackQuestion = Parallel(Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                       "In the standard Sellbot Factory, what is the name of the Factory Foreman's special ability?",
                                                       CFSpeech | CFTimeout),
                                       Sequence(Wait(5.0), Func(manager.setChatAbsolute,
                                                       taunt,
                                                       CFSpeech | CFTimeout), Parallel(ActorInterval(manager, 'song-and-dance'), soundTrack3, Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                       "Ha-HA!",
                                                       CFSpeech | CFTimeout))))))
    suitTrackQuestion = Sequence(Wait(1.0), Parallel(ActorInterval(targetSuit, 'mob-mentality'), Func(targetSuit.setChatAbsolute,
                                                       "It's my time to shine!", CFSpeech | CFTimeout), Func(targetSuit.setNeutralAnimation)), Wait(3.0), Func(targetSuit.setChatAbsolute,
                                                       "Worker's Compensation!", CFSpeech | CFTimeout), Wait(7.0), ActorInterval(targetSuit, 'large-zap')
                                 , Func(targetSuit.setNeutralAnimation))
    managerTrackQuestion2 = Parallel(Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                             "Who does the Major Player fancy?",
                                                             CFSpeech | CFTimeout),
                                             Sequence(Wait(5.0), Func(manager.setChatAbsolute,
                                                                      taunt,
                                                                      CFSpeech | CFTimeout),
                                                      Parallel(ActorInterval(manager, 'song-and-dance'), soundTrack3,
                                                               Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                                                        "Ha-HA!",
                                                                                        CFSpeech | CFTimeout))))))
    suitTrackQuestion2 = Sequence(Wait(1.0),
                                 Parallel(ActorInterval(targetSuit, 'mob-mentality'), Func(targetSuit.setChatAbsolute,
                                                                                           "It's my time to shine!",
                                                                                           CFSpeech | CFTimeout),
                                          Func(targetSuit.setNeutralAnimation)), Wait(3.0),
                                 Func(targetSuit.setChatAbsolute,
                                      "Himself!", CFSpeech | CFTimeout), Wait(7.0),
                                 ActorInterval(targetSuit, 'large-zap')
                                 , Func(targetSuit.setNeutralAnimation))
    managerTrackQuestion3 = Parallel(Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                             "Which hand does the Head Attorney use during 'Objection'?",
                                                             CFSpeech | CFTimeout),
                                             Sequence(Wait(5.0), Func(manager.setChatAbsolute,
                                                                      taunt,
                                                                      CFSpeech | CFTimeout),
                                                      Parallel(ActorInterval(manager, 'song-and-dance'), soundTrack3,
                                                               Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                                                        "Ha-HA!",
                                                                                        CFSpeech | CFTimeout))))))
    suitTrackQuestion3 = Sequence(Wait(1.0),
                                 Parallel(ActorInterval(targetSuit, 'mob-mentality'), Func(targetSuit.setChatAbsolute,
                                                                                           "It's my time to shine!",
                                                                                           CFSpeech | CFTimeout),
                                          Func(targetSuit.setNeutralAnimation)), Wait(3.0),
                                 Func(targetSuit.setChatAbsolute,
                                      "Left!", CFSpeech | CFTimeout), Wait(7.0),
                                 ActorInterval(targetSuit, 'large-zap')
                                 , Func(targetSuit.setNeutralAnimation))
    managerTrackQuestion4 = Parallel(Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                             "TRUE or FALSE: The longest employee position name int he company is the Public Relations Representative?",
                                                             CFSpeech | CFTimeout),
                                             Sequence(Wait(5.0), Func(manager.setChatAbsolute,
                                                                      taunt,
                                                                      CFSpeech | CFTimeout),
                                                      Parallel(ActorInterval(manager, 'song-and-dance'), soundTrack3,
                                                               Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                                                        "Ha-HA!",
                                                                                        CFSpeech | CFTimeout))))))
    suitTrackQuestion4 = Sequence(Wait(1.0),
                                 Parallel(ActorInterval(targetSuit, 'mob-mentality'), Func(targetSuit.setChatAbsolute,
                                                                                           "It's my time to shine!",
                                                                                           CFSpeech | CFTimeout),
                                          Func(targetSuit.setNeutralAnimation)), Wait(3.0),
                                 Func(targetSuit.setChatAbsolute,
                                      "TRUE!", CFSpeech | CFTimeout), Wait(7.0),
                                 ActorInterval(targetSuit, 'large-zap')
                                 , Func(targetSuit.setNeutralAnimation))
    managerTrackQuestion5 = Parallel(Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                             "Who is the Name Dropper planning on having lunch with?",
                                                             CFSpeech | CFTimeout),
                                             Sequence(Wait(5.0), Func(manager.setChatAbsolute,
                                                                      taunt,
                                                                      CFSpeech | CFTimeout),
                                                      Parallel(ActorInterval(manager, 'song-and-dance'), soundTrack3,
                                                               Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                                                        "Ha-HA!",
                                                                                        CFSpeech | CFTimeout))))))
    suitTrackQuestion5 = Sequence(Wait(1.0),
                                 Parallel(ActorInterval(targetSuit, 'mob-mentality'), Func(targetSuit.setChatAbsolute,
                                                                                           "It's my time to shine!",
                                                                                           CFSpeech | CFTimeout),
                                          Func(targetSuit.setNeutralAnimation)), Wait(3.0),
                                 Func(targetSuit.setChatAbsolute,
                                      "Mr. Hollywood!", CFSpeech | CFTimeout), Wait(7.0),
                                 ActorInterval(targetSuit, 'large-zap')
                                 , Func(targetSuit.setNeutralAnimation))
    managerTrackQuestion6 = Parallel(Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                              "What does the acronym C.O.G.S. stand for?",
                                                              CFSpeech | CFTimeout),
                                              Sequence(Wait(5.0), Func(manager.setChatAbsolute,
                                                                       taunt,
                                                                       CFSpeech | CFTimeout),
                                                       Parallel(ActorInterval(manager, 'song-and-dance'), soundTrack3,
                                                                Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                                                         "Ha-HA!",
                                                                                         CFSpeech | CFTimeout))))))
    suitTrackQuestion6 = Sequence(Wait(1.0),
                                  Parallel(ActorInterval(targetSuit, 'mob-mentality'), Func(targetSuit.setChatAbsolute,
                                                                                            "It's my time to shine!",
                                                                                            CFSpeech | CFTimeout),
                                           Func(targetSuit.setNeutralAnimation)), Wait(3.0),
                                  Func(targetSuit.setChatAbsolute,
                                       "Coal, Oil, and Gas Syndicate!", CFSpeech | CFTimeout), Wait(7.0),
                                  ActorInterval(targetSuit, 'large-zap')
                                  , Func(targetSuit.setNeutralAnimation))
    selfDamageTrack = Sequence(Wait(16), Func(targetSuit.showHpTextCheat, + x), Func(targetSuit.showHpString, "OVERCHARGED!"),
                               Func(targetSuit.setHealthForMe, + x),
                               Func(targetSuit.updateHealthBar, 0), Wait(2.0), Func(targetSuit.showHpTextWhite, '+ 1 ATTACK!'))
    suitTrack = random.choice((Parallel(managerTrackQuestion, suitTrackQuestion), Parallel(managerTrackQuestion2, suitTrackQuestion2), Parallel(managerTrackQuestion3, suitTrackQuestion3)
                               , Parallel(managerTrackQuestion5, suitTrackQuestion5), Parallel(managerTrackQuestion6, suitTrackQuestion6), Parallel(managerTrackQuestion4, suitTrackQuestion4)))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_bash.ogg'), node=manager))
    soundTrack2 = getSoundTrack('LB_camera_shutter_2.ogg', delay=1, node=manager)
    soundTrack5 = getSoundTrack('LB_toonup.ogg', delay=16, node=manager)
    return Parallel(managerTrack, suitTrack, soundTrack, soundTrack2, cagePropTrack, soundTrack5, selfDamageTrack)

def doConduction(attack):
    suit = attack['suit']
    battle = attack['battle']
    propDelay = 0.6
    throwDelay = 1.3
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    allDuckTracks = Parallel()
    squishDuck = lambda duck: Sequence(LerpScaleInterval(duck, 0.25, Point3(6.25, 6.25, 2.5)),
                                       LerpScaleInterval(duck, 0.1, Point3(5)))
    for t in attack['target']:
        toon = t['toon']
        duckTracks = Parallel()
        for i in xrange(0, random.randint(7, 10)):
            x = random.random() / 5
            if random.choice([False, True]):
                x *= -1
            y = random.random() / 5
            if random.choice([False, True]):
                y *= -1
            next = loader.loadModel('phase_5/models/props/cc_m_bat_prp_duck_hroller')
            posPoints = [Point3(x, y, -0.5), VBase3(0, 0, 180)]
            duckLandX = (toon.getX(battle) - 0.05) + random.random()
            duckLandY = (toon.getY(battle) - 0.05) + random.random()
            duckTrack = Sequence(
                getPropAppearTrack(next, suit.getRightHand(), posPoints, propDelay, scaleUpPoint=Point3(2.5)),
                Wait(throwDelay - propDelay + random.random()),
                Parallel(
                    getThrowTrack(next, Point3(duckLandX, duckLandY + 5, 0.5), parent=battle),
                    LerpHprInterval(next, 1.0, VBase3(180, 0, 0)),
                    LerpScaleInterval(next, 1.0, Point3(5))
                ),
                squishDuck(next),
                getThrowTrack(next, Point3(duckLandX, duckLandY, 0.5), duration=0.25, parent=battle, gravity=-96.432),
                squishDuck(next),
                getThrowTrack(next, Point3(duckLandX, duckLandY - 5, 0.5), duration=0.25, parent=battle,
                              gravity=-96.432),
                LerpScaleInterval(next, 0.25, Point3(6.25, 6.25, 2.5)),
                LerpScaleInterval(next, 0.25, MovieUtil.PNT3_NEARZERO),
                Func(MovieUtil.removeProp, next)
            )
            duckTracks.append(duckTrack)

        allDuckTracks.append(duckTracks)
    suitTrack.append(Func(suit.makeNonImmortal))
    damageAnims = [['cringe', 0.01, 0.14, 0.21],
                   ['cringe', 0.01, 0.14, 0.13],
                   ['cringe', 0.01, 0.43]]
    toonTracks = getToonTracks(attack, damageDelay=3.2, splicedDamageAnims=damageAnims, dodgeDelay=2.8,
                               dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('cc_s_sfx_ene_hroller_conducktion.ogg', delay=throwDelay, node=suit)
    return Parallel(suitTrack, allDuckTracks, toonTracks, soundTrack)



