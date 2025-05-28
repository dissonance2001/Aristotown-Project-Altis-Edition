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
    elif suit.isImmortal:
        neutralIval = Func(suit.loop, 'highroller-neutral-levitate-loop')
        preWalkTrack = ActorInterval(suit, 'highroller-neutral-levitate-in-out', startTime=1, endTime=0, duration=1)
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
    currentBossHealth = -1
    currentBossHealth2 = -1
    if suit.style.name == 'csm':
        for s in battle.activeSuits:
            if s.dna.name == 'ste' or s.dna.name == 'lit' or s.dna.name == 'scg':
                currentBossHealth = s.currHP
        if currentBossHealth == -1:
            animTrack.append(Func(suit.makeDesperation))
            animTrack.append(Func(suit.makeDamageUp))
    elif suit.style.name == 'scg':
        for s in battle.activeSuits:
            if s.dna.name == 'csm':
                currentBossHealth2 = s.currHP
            if s.dna.name == 'ste' or s.dna.name == 'lit' or s.dna.name == 'csm':
                currentBossHealth = s.currHP
        if currentBossHealth2 == -1:
            animTrack.append(Func(suit.removeInsured))
        if currentBossHealth == -1:
            animTrack.append(Func(suit.makeDesperation))
            animTrack.append(Func(suit.makeDamageUp))
    elif suit.style.name == 'lit':
        for s in battle.activeSuits:
            if s.dna.name == 'csm':
                currentBossHealth2 = s.currHP
            if s.dna.name == 'ste' or s.dna.name == 'scg' or s.dna.name == 'csm':
                currentBossHealth = s.currHP
        if currentBossHealth2 == -1:
            animTrack.append(Func(suit.removeInsured))
        if currentBossHealth == -1:
            animTrack.append(Func(suit.makeDesperation))
            animTrack.append(Func(suit.makeDamageUp))
    elif suit.style.name == 'ste':
        for s in battle.activeSuits:
            if s.dna.name == 'csm':
                currentBossHealth2 = s.currHP
            if s.dna.name == 'scg' or s.dna.name == 'lit' or s.dna.name == 'csm':
                currentBossHealth = s.currHP
        if currentBossHealth2 == -1:
            animTrack.append(Func(suit.removeInsured))
        if currentBossHealth == -1:
            animTrack.append(Func(suit.makeDesperation))
            animTrack.append(Func(suit.makeDamageUp))
    elif suit.style.name == 'gtk':
        for s in battle.activeSuits:
            if s.dna.name == 'frs' or s.dna.name == 'fbd' or s.dna.name == 'cp':
                currentBossHealth = s.currHP
        if currentBossHealth == -1:
            animTrack.append(Func(suit.makeDesperation))
            animTrack.append(Func(suit.makeDamageUp))
    elif suit.style.name == 'frs':
        for s in battle.activeSuits:
            if s.dna.name == 'gtk' or s.dna.name == 'fbd' or s.dna.name == 'cp':
                currentBossHealth = s.currHP
        if currentBossHealth == -1:
            animTrack.append(Func(suit.makeDesperation))
            animTrack.append(Func(suit.makeDamageUp))
    elif suit.style.name == 'fbd':
        for s in battle.activeSuits:
            if s.dna.name == 'frs' or s.dna.name == 'gtk' or s.dna.name == 'cp':
                currentBossHealth = s.currHP
        if currentBossHealth == -1:
            animTrack.append(Func(suit.makeDesperation))
            animTrack.append(Func(suit.makeDamageUp))
    elif suit.style.name == 'cp':
        for s in battle.activeSuits:
            if s.dna.name == 'frs' or s.dna.name == 'fbd' or s.dna.name == 'gtk':
                currentBossHealth = s.currHP
        if currentBossHealth == -1:
            animTrack.append(Func(suit.makeDesperation))
            animTrack.append(Func(suit.makeDamageUp))
    elif suit.style.name == 'ffm':
        for s in battle.activeSuits:
            if s.dna.name == 'dsk' or s.dna.name == 'blr' or s.dna.name == 'dvp':
                currentBossHealth = s.currHP
        if currentBossHealth == -1:
            animTrack.append(Func(suit.makeDesperation))
            animTrack.append(Func(suit.makeDamageUp))
    elif suit.style.name == 'dsk':
        for s in battle.activeSuits:
            if s.dna.name == 'ffm' or s.dna.name == 'blr' or s.dna.name == 'dvp':
                currentBossHealth = s.currHP
        if currentBossHealth == -1:
            animTrack.append(Func(suit.makeDesperation))
            animTrack.append(Func(suit.makeDamageUp))
    elif suit.style.name == 'dvp':
        for s in battle.activeSuits:
            if s.dna.name == 'dsk' or s.dna.name == 'blr' or s.dna.name == 'ffm':
                currentBossHealth = s.currHP
        if currentBossHealth == -1:
            animTrack.append(Func(suit.makeDesperation))
            animTrack.append(Func(suit.makeDamageUp))
    elif suit.style.name == 'blr':
        for s in battle.activeSuits:
            if s.dna.name == 'dsk' or s.dna.name == 'ffm' or s.dna.name == 'dvp':
                currentBossHealth = s.currHP
        if currentBossHealth == -1:
            animTrack.append(Func(suit.makeDesperation))
            animTrack.append(Func(suit.makeDamageUp))
    elif suit.style.name == 'cry':
        for s in battle.activeSuits:
            if s.dna.name == 'dvk' or s.dna.name == 'tcm' or s.dna.name == 'otm':
                currentBossHealth = s.currHP
        if currentBossHealth == -1:
            animTrack.append(Func(suit.makeDesperation))
            animTrack.append(Func(suit.makeDamageUp))
    elif suit.style.name == 'tcm':
        for s in battle.activeSuits:
            if s.dna.name == 'dvk' or s.dna.name == 'cry' or s.dna.name == 'otm':
                currentBossHealth = s.currHP
        if currentBossHealth == -1:
            animTrack.append(Func(suit.makeDesperation))
            animTrack.append(Func(suit.makeDamageUp))
    elif suit.style.name == 'otm':
        for s in battle.activeSuits:
            if s.dna.name == 'dvk' or s.dna.name == 'tcm' or s.dna.name == 'cry':
                currentBossHealth = s.currHP
        if currentBossHealth == -1:
            animTrack.append(Func(suit.makeDesperation))
            animTrack.append(Func(suit.makeDamageUp))
    elif suit.style.name == 'dvk':
        for s in battle.activeSuits:
            if s.dna.name == 'cry' or s.dna.name == 'tcm' or s.dna.name == 'otm':
                currentBossHealth = s.currHP
        if currentBossHealth == -1:
            animTrack.append(Func(suit.makeDesperation))
            animTrack.append(Func(suit.makeDamageUp))
    for s in battle.activeSuits:
        if s.dna.name == 'csm':
            currentBossHealth = s.currHP
    if currentBossHealth == -1:
        animTrack.append(Func(suit.removeInsured))
    x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
    if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
        syphonSuitTrack = Parallel(Func(suit.showHpTextCheat, +0), Func(suit.showHpString, "SYPHONED!"), Func(suit.setHealthForMe, + 0), Func(suit.updateHealthBar, 0))
        insuredSuitTrack = Parallel(Func(suit.showHpTextCheat, +0), Func(suit.showHpString, "INSURED!"), Func(suit.setHealthForMe, 0), Func(suit.updateHealthBar, 0))
    elif suit.currHP + 50 > (suit.maxHP * suit.hardMaxHP) and suit.isInsured:
        insuredSuitTrack = Parallel(Func(suit.showHpTextCheat, x), Func(suit.showHpString, "INSURED!"),
                                    Func(suit.setHealthForMe, x), Func(suit.updateHealthBar, 0))
    elif suit.currHP + dmg > (suit.maxHP * suit.hardMaxHP) and suit.isSyphon:
        syphonSuitTrack = Parallel(Func(suit.showHpTextCheat, x), Func(suit.showHpString, "SYPHONED!"),
                                   Func(suit.setHealthForMe, x), Func(suit.updateHealthBar, 0))
    else:
        syphonSuitTrack = Parallel(Func(suit.showHpTextCheat, +dmg), Func(suit.showHpString, "SYPHONED!"),
                                   Func(suit.setHealthForMe, + dmg), Func(suit.updateHealthBar, 0))
        insuredSuitTrack = Parallel(Func(suit.showHpTextCheat, 50), Func(suit.showHpString, "INSURED!"),
                                    Func(suit.setHealthForMe, 50), Func(suit.updateHealthBar, 0))
    if dmg > 0 and name == MULLIGAN and suit.isSyphon:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        animTrack.append(syphonSuitTrack)
        return animTrack
    elif dmg > 0 and name == MULLIGAN:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == BLAST and suit.isSyphon:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        animTrack.append(syphonSuitTrack)
        return animTrack
    elif dmg > 0 and name == BLAST:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == COURT_MANDATE and suit.isSyphon:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        animTrack.append(syphonSuitTrack)
        return animTrack
    elif dmg > 0 and name == COURT_MANDATE:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == COURT_MANDATE_1 and suit.isSyphon:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        animTrack.append(syphonSuitTrack)
        return animTrack
    elif dmg > 0 and name == COURT_MANDATE_1:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == COURT_MANDATE_2 and suit.isSyphon:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        animTrack.append(syphonSuitTrack)
        return animTrack
    elif dmg > 0 and name == COURT_MANDATE_2:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == COURT_MANDATE_3 and suit.isSyphon:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        animTrack.append(syphonSuitTrack)
        return animTrack
    elif dmg > 0 and name == COURT_MANDATE_3:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == KICK_UP:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == SHAKEDOWN:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == FIRE_COG and suit.isOttomanPhase2:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        animTrack.append(
            getToonTakeDamageTrack(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims,
                                   showDamageExtraTime))
        taunt = random.choice(
            ["You've gotta be quicker than that!", "Move it!", "Think fast!", "Eyes on the prize!",
             "Follow the groove!",
             "Step on it!", "Hurry it up!", "Pump up those reflexes!", "Follow the groove!"])
        animTrack.append(Func(suit.setChatAbsolute,
                              taunt,
                              CFSpeech | CFTimeout))
        animTrack.append(Func(suit.showHpString, "1.05x DMG MULTIPLIER!"))
        animTrack.append(ActorInterval(suit, 'come-on', playRate=suit.getPlayRate('pace')))
        animTrack.append(Func(suit.setPlayRate, suit.getPlayRate() + 0.1, 'pace'))
        return animTrack
    elif dmg > 0 and name == FIRE_COG:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == USURY and suit.isChainsawPhase3:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        animTrack.append(
            getToonTakeDamageTrack(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims,
                                   showDamageExtraTime))
        taunt = random.choice(
            ["DAMAGE TO SHELL- increasing- IDENTIFIED. RETALIATION SHALL BE MET WITH- power- EQUAL FORCE.",
             "OUTER LAYERS AT- getting- RISK. TAKING DEFENSIVE- faster- ACTION.",
             "THREATS HAVE- i have- BEGUN TO- been- ADVANCE. BEGIN- hit- INCREASING ATTACK POWER.", ])
        animTrack.append(Func(suit.setChatAbsolute,
                              taunt,
                              CFSpeech | CFTimeout))
        animTrack.append(Func(suit.showHpString, "1.1x DMG MULTIPLIER!"))
        for headPart in suit.animatedHeadParts:
            headInterval = ActorInterval(headPart, 'revvedup', playRate=suit.getPlayRate('revvedup'))
        animTrack.append(Parallel(headInterval, SoundInterval(base.loadSfx('phase_5/audio/sfx/SA_revving_up.ogg')),
                                  ActorInterval(suit, 'revvedup', playRate=suit.getPlayRate('revvedup'))))
        animTrack.append(Func(suit.setPlayRate, suit.getPlayRate() + 0.1, 'revvedup'))
        animTrack.append(Func(suit.setChatAbsolute, '', CFSpeech | CFTimeout))
        animTrack.append(Func(suit.setNeutralAnimation))
        return animTrack
    elif dmg > 0 and name == USURY:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == OIL_RAIN:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == CHAINSAW_QUAKE and suit.isChainsawPhase2:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        animTrack.append(
            getToonTakeDamageTrack(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims,
                                   showDamageExtraTime))
        taunt = random.choice(
            ["DAMAGE TO SHELL IDENTIFIED. RETALIATION WILL BE MET WITH EQUAL FORCE.",
             "OUTER LAYERS AT RISK. TAKING DEFENSIVE ACTION.",
             "THREATS HAVE BEGUN TO ADVANCE. BEGIN INCREASING ATTACK POWER."])
        animTrack.append(Func(suit.setChatAbsolute,
                              taunt,
                              CFSpeech | CFTimeout))
        animTrack.append(Func(suit.showHpString, "1.05x DMG MULTIPLIER!"))
        animTrack.append(Parallel(SoundInterval(base.loadSfx('phase_5/audio/sfx/SA_revving_up.ogg')),
                                  ActorInterval(suit, 'revvedup', playRate=suit.getPlayRate('revvedup'))))
        animTrack.append(Func(suit.setPlayRate, suit.getPlayRate() + 0.1, 'revvedup'))
        animTrack.append(Func(suit.setNeutralAnimation))
        return animTrack
    elif dmg > 0 and name == CHAINSAW_QUAKE:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == CHAINSAW_DETONATE_2 and suit.isChainsawPhase2:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        animTrack.append(
            getToonTakeDamageTrack(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims,
                                   showDamageExtraTime))
        taunt = random.choice(
            ["DAMAGE TO SHELL IDENTIFIED. RETALIATION WILL BE MET WITH EQUAL FORCE.",
             "OUTER LAYERS AT RISK. TAKING DEFENSIVE ACTION.",
             "THREATS HAVE BEGUN TO ADVANCE. BEGIN INCREASING ATTACK POWER."])
        animTrack.append(Func(suit.setChatAbsolute,
                              taunt,
                              CFSpeech | CFTimeout))
        animTrack.append(Func(suit.showHpString, "1.05x DMG MULTIPLIER!"))
        animTrack.append(Parallel(SoundInterval(base.loadSfx('phase_5/audio/sfx/SA_revving_up.ogg')),
                                  ActorInterval(suit, 'revvedup', playRate=suit.getPlayRate('revvedup'))))
        animTrack.append(Func(suit.setPlayRate, suit.getPlayRate() + 0.1, 'revvedup'))
        animTrack.append(Func(suit.setNeutralAnimation))
        return animTrack
    elif dmg > 0 and name == CHAINSAW_DETONATE_2:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == CHAINSAW_DETONATE and suit.isChainsawPhase2:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        animTrack.append(
            getToonTakeDamageTrack(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims,
                                   showDamageExtraTime))
        taunt = random.choice(
            ["DAMAGE TO SHELL IDENTIFIED. RETALIATION WILL BE MET WITH EQUAL FORCE.",
             "OUTER LAYERS AT RISK. TAKING DEFENSIVE ACTION.",
             "THREATS HAVE BEGUN TO ADVANCE. BEGIN INCREASING ATTACK POWER."])
        animTrack.append(Func(suit.setChatAbsolute,
                              taunt,
                              CFSpeech | CFTimeout))
        animTrack.append(Func(suit.showHpString, "1.05x DMG MULTIPLIER!"))
        animTrack.append(Parallel(SoundInterval(base.loadSfx('phase_5/audio/sfx/SA_revving_up.ogg')),
                                  ActorInterval(suit, 'revvedup', playRate=suit.getPlayRate('revvedup'))))
        animTrack.append(Func(suit.setPlayRate, suit.getPlayRate() + 0.1, 'revvedup'))
        animTrack.append(Func(suit.setNeutralAnimation))
        return animTrack
    elif dmg > 0 and name == CHAINSAW_DETONATE:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == BEGUILE and suit.isSyphon:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        animTrack.append(syphonSuitTrack)
        return animTrack
    elif dmg > 0 and name == BOMB_CAKE:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == CHAINSAW_CANNED:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == TRIBUTE_2:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == SLUSHFUND_2:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == CAGE:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == NOT_THROW_PIANO:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == DETONATE_2:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == COLLECT_CALL:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == BEGUILE:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == CEASE_AND_DESIST and suit.isInsured:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 1.74), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        animTrack.append(insuredSuitTrack)
        return animTrack
    elif dmg > 0 and name == CEASE_AND_DESIST:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 1.74), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == UNION_BUSTER:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        animTrack.append(insuredSuitTrack)
        return animTrack
    elif dmg > 0 and name == WHITE_POWDER:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 1.83), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == WIRETAPPED:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == BOOKKEEPING:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == WIRE_CUT:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == FREEZING_RAIN:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == HEAVY_RAINFALL:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == COLLECT_CALL:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == CONE_OF_SHAME:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == QUALITY_CONTROL_LEVEL_3:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 1.83), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == QUALITY_CONTROL_LEVEL_1:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 1.83), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == AFTERSHOCK:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == QUALITY_CONTROL_LEVEL:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == BOMB:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == DROWNING:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 1.83), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == PAPER_CUT:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == EXPLODING_BILL:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == SNAP_WET and suit.isInsured:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 1.75), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        animTrack.append(insuredSuitTrack)
        return animTrack
    elif dmg > 0 and name == SNAP_WET:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 1.75), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == COURT_SANCTION and suit.isInsured:
        animTrack.append(
            getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 1.55), damageDelay, damageAnimNames,
                                   splicedDamageAnims, showDamageExtraTime))
        animTrack.append(insuredSuitTrack)
        return animTrack
    elif dmg > 0 and name == COURT_SANCTION:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 1.55), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == COURT_RECORD_4 and suit.isInsured:
        animTrack.append(
            getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 1.74), damageDelay, damageAnimNames,
                                   splicedDamageAnims, showDamageExtraTime))
        animTrack.append(insuredSuitTrack)
        return animTrack
    elif dmg > 0 and name == COURT_RECORD_4:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 1.74), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == SNAP and suit.isInsured:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 1.69), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        animTrack.append(insuredSuitTrack)
        return animTrack
    elif dmg > 0 and name == SNAP:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 1.69), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and suit.isSyphon:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        animTrack.append(syphonSuitTrack)
        return animTrack
    elif dmg > 0 and suit.isInsured:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        animTrack.append(insuredSuitTrack)
        return animTrack
    elif dmg > 0 and suit.isOttomanPhase2:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        taunt = random.choice(
            ["You've gotta be quicker than that!", "Move it!", "Think fast!", "Eyes on the prize!", "Follow the groove!",
             "Step on it!", "Hurry it up!", "Pump up those reflexes!", "Follow the groove!"])
        animTrack.append(Func(suit.setChatAbsolute,
                              taunt,
                              CFSpeech | CFTimeout))
        animTrack.append(Func(suit.showHpString, "1.05x DMG MULTIPLIER!"))
        animTrack.append(ActorInterval(suit, 'come-on', playRate=suit.getPlayRate('pace')))
        animTrack.append(Func(suit.setPlayRate, suit.getPlayRate() + 0.1, 'pace'))
        return animTrack
    elif dmg > 0 and suit.isChainsawPhase2:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        taunt = random.choice(
            ["DAMAGE TO SHELL IDENTIFIED. RETALIATION WILL BE MET WITH EQUAL FORCE.", "OUTER LAYERS AT RISK. TAKING DEFENSIVE ACTION.",
             "THREATS HAVE BEGUN TO ADVANCE. BEGIN INCREASING ATTACK POWER."])
        animTrack.append(Func(suit.setChatAbsolute,
                              taunt,
                              CFSpeech | CFTimeout))
        animTrack.append(Func(suit.showHpString, "1.05x DMG MULTIPLIER!"))
        animTrack.append(Parallel(SoundInterval(base.loadSfx('phase_5/audio/sfx/SA_revving_up.ogg')),
                                           ActorInterval(suit, 'revvedup', playRate=suit.getPlayRate('revvedup'))))
        animTrack.append(Func(suit.setPlayRate, suit.getPlayRate() + 0.1, 'revvedup'))
        animTrack.append(Func(suit.setNeutralAnimation))
        return animTrack
    elif dmg > 0 and suit.isChainsawPhase3:
        animTrack.append(
            getToonTakeDamageTrack(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims,
                                   showDamageExtraTime))
        taunt = random.choice(
            ["DAMAGE TO SHELL- increasing- IDENTIFIED. RETALIATION SHALL BE MET WITH- power- EQUAL FORCE.", "OUTER LAYERS AT- getting- RISK. TAKING DEFENSIVE- faster- ACTION.",
             "THREATS HAVE- i have- BEGUN TO- been- ADVANCE. BEGIN- hit- INCREASING ATTACK POWER.",])
        animTrack.append(Func(suit.setChatAbsolute,
                              taunt,
                              CFSpeech | CFTimeout))
        animTrack.append(Func(suit.showHpString, "1.1x DMG MULTIPLIER!"))
        for headPart in suit.animatedHeadParts:
            headInterval =  ActorInterval(headPart, 'revvedup', playRate=suit.getPlayRate('revvedup'))
        animTrack.append(Parallel(headInterval, SoundInterval(base.loadSfx('phase_5/audio/sfx/SA_revving_up.ogg')),
                                  ActorInterval(suit, 'revvedup', playRate=suit.getPlayRate('revvedup'))))
        animTrack.append(Func(suit.setPlayRate, suit.getPlayRate() + 0.1, 'revvedup'))
        animTrack.append(Func(suit.setChatAbsolute, '', CFSpeech | CFTimeout))
        animTrack.append(Func(suit.setNeutralAnimation))
        return animTrack
    elif dmg > 0:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    else:
        animTrack.append(getToonDodgeTrack(target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime))
        indicatorTrack = Sequence(Wait(dodgeDelay + showMissedExtraTime), Func(MovieUtil.indicateMissed, toon))
        return Parallel(animTrack, indicatorTrack)


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
    if died:
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
    if died:
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
    synergySoundTrack = Sequence(Wait(0.9), SoundInterval(globalBattleSoundCache.getSound('SA_synergy.ogg'), node=suit))
    if hitAtleastOneToon > 0:
        fallingSoundTrack = Sequence(Wait(damageDelay + 0.5), SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=suit))
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, fallingSoundTrack, toonTracks)
    else:
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, toonTracks)

def doCourtCalculations(attack):
    suit = attack['suit']
    battle = attack['battle']
    calculator = globalPropPool.getProp('court-costs-calculator')
    suitTrack = Sequence(ActorInterval(attack['suit'], 'calculating-costs'),  Func(suit.setNeutralAnimation), Wait(2.0))
    suitSpeechTrack = Func(suit.setChatAbsolute, "Calculating costs of litigation fees... Price index raised to %s." % attack['target'][0]['hp'], CFSpeech | CFTimeout)
    calcPosPoints = [Point3(-0.35, 0.25, -0.1), VBase3(1.352, 0.0, 180.0)]
    calcDuration = 0.25
    scaleUpPoint = Point3(1.5, 1.5, 1.5)
    calcPropTrack = getPropTrack(calculator, suit.getRightHand(), calcPosPoints, 0, calcDuration,
                                 scaleUpPoint=scaleUpPoint, scaleUpTime=0, anim=1, propName='court-costs-calculator', animStartTime=0,
                                 animDuration=2.9)
    soundTrack = getSoundTrack('SA_calculating_costs.ogg', node=suit)
    return Parallel(suitTrack, soundTrack, suitSpeechTrack, calcPropTrack)

def doCourtRecord(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack.append(Wait(2.0))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    return Parallel(suitTrack, soundTrack)