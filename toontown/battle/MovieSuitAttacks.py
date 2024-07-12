from toontown.battle import MovieCamera
from toontown.battle import MovieUtil
from toontown.battle import BattleParticles
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from direct.particles import ParticleEffect
from toontown.battle.BattleBase import *
from toontown.battle.BattleBase import *
import PlayByPlayText
from toontown.battle.BattleProps import *
from otp.otpbase import OTPLocalizerEnglish
from toontown.battle.BattleSounds import *
from toontown.battle.SuitBattleGlobals import *
from toontown.chat.ChatGlobals import *
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
    elif name == DISASSEMBLE:
        suitTrack = doDisassemble(attack)
    elif name == DATA_CORRUPTION:
        suitTrack = doDataCorruption(attack)
    elif name == CLOUD_STORAGE:
        suitTrack = doCloudStorage(attack)
    elif name == DISK_SCRATCH:
        suitTrack = doDiskScratch(attack)
    elif name == VOODOO_MAGIC:
        suitTrack = doPickPocket(attack)
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
        suitTrack = doFreeCruiseMulti(attack)
    elif name == SPOTLIGHT:
        suitTrack = doSpotlight(attack)
    elif name == DICE_ROULETTE:
        suitTrack = doDiceRoulette(attack)
    elif name == CONDUCTION:
        suitTrack = doConDuckTion(attack)
    elif name == REFINEMENT:
        suitTrack = doRefinement(attack)
    elif name == EXTRA_TIP:
        suitTrack = doBayouBash(attack)
    elif name == WORKERS_COMPENSATION:
        suitTrack = doWorkersCompensation(attack)
    elif name == COURT_MANDATE:
        suitTrack = doCourtMandate(attack)
    elif name == COURT_MANDATE_1:
        suitTrack = doCourtMandate(attack)
    elif name == COURT_MANDATE_2:
        suitTrack = doCourtMandate(attack)
    elif name == COURT_MANDATE_3:
        suitTrack = doCourtMandate(attack)
    elif name == EVICTION_NOTICE:
        suitTrack = doEvictionNotice(attack)
    elif name == CHOMP:
        suitTrack = doChomp(attack)
    elif name == LD_QUAKE:
        suitTrack = doQuake(attack)
    elif name == SNAP:
        suitTrack = doSnap(attack)
    elif name == BLACK_ORB:
        suitTrack = doBlackOrb(attack)
    elif name == CIGAR_SMOKE:
        suitTrack = doCigarSmoke(attack)
    elif name == CHAINSAW_CANNED:
        suitTrack = doCanned(attack)
    elif name == CLOCK_CHANGE:
        suitTrack = doClockChange(attack)
    elif name == WHITE_POWDER:
        suitTrack = doBayouBash(attack)
    elif name == CLIPON_TIE:
        suitTrack = doClipOnTie(attack)
    elif name == LEGAL_BINDINGS:
        suitTrack = doLegalBindings(attack)
    elif name == NOT_THROW_PIANO:
        suitTrack = doNotThrowPiano(attack)
    elif name == THROW_MONEY:
        suitTrack = doThrowMoney(attack)
    elif name == AMANDAS_DOUGHNUTS:
        suitTrack = doAmandasDoughnuts(attack)
    elif name == GAVEL:
        suitTrack = doGavel(attack)
    elif name == BOMB_CAKE:
        suitTrack = doBombCake(attack)
    elif name == BOMB:
        suitTrack = doBomb(attack)
    elif name == CRUNCH:
        suitTrack = doCrunch(attack)
    elif name == DEMOTION:
        suitTrack = doDemotion(attack)
    elif name == DOUBLE_TALK:
        suitTrack = doDoubleTalk(attack)
    elif name == DOWNSIZE:
        suitTrack = doDownsize(attack)
    elif name == EVICTION_NOTICE:
        suitTrack = doEvictionNotice(attack)
    elif name == INSURANCE_PLAN:
        suitTrack = doInsurancePlan(attack)
    elif name == LD_EVICTION_NOTICE:
        suitTrack = doEvictionNotice(attack)
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
        suitTrack = doGlowerPower(attack)
    elif name == WATER_SPRAY:
        suitTrack = doWaterSpray(attack)
    elif name == PECKING_ORDER_WSI:
        suitTrack = doPeckingOrder(attack)
    elif name == POWER_TRIP_WSI:
        suitTrack = doPowerTrip(attack)
    elif name == CHAINSAW_QUAKE:
        suitTrack = doQuake(attack)
    elif name == MP_QUAKE:
        suitTrack = doQuake(attack)
    elif name == REARRANGE:
        suitTrack = doReOrg(attack)
    elif name == MP_SONG_AND_DANCE:
        suitTrack = doSongAndDance(attack)
    elif name == INK_DRAIN:
        suitTrack = doCaress(attack)
    elif name == BAR:
        suitTrack = doBarMulti(attack)
    elif name == WHEEL_SPIN:
        suitTrack = doWheelSpin(attack)
    elif name == ACCUSATIONS:
        suitTrack = doAccusations(attack)
    elif name == SNAP_WET:
        suitTrack = doSnap(attack)
    elif name == GAME_SHOW:
        suitTrack = doBayouBash2(attack)
    elif name == DUCK_SPIN:
        suitTrack = doSpin(attack)
    elif name == MOB_MENTALITY:
        suitTrack = doMobMentality(attack)
    elif name == QUALITY_CONTROL_GAG:
        suitTrack = doCourtRecord1(attack)
    elif name == QUALITY_CONTROL_GAG_1:
        suitTrack = doCourtRecord1(attack)
    elif name == QUALITY_CONTROL_GAG_2:
        suitTrack = doCourtRecord1(attack)
    elif name == QUALITY_CONTROL_GAG_3:
        suitTrack = doCourtRecord1(attack)
    elif name == QUALITY_CONTROL_LEVEL:
        suitTrack = doCourtRecord1(attack)
    elif name == QUALITY_CONTROL_LEVEL_1:
        suitTrack = doCourtRecord1(attack)
    elif name == QUALITY_CONTROL_LEVEL_2:
        suitTrack = doCourtRecord1(attack)
    elif name == QUALITY_CONTROL_LEVEL_3:
        suitTrack = doCourtRecord1(attack)
    elif name == MANAGERIAL_PROTECTION:
        suitTrack = doManagerialProtection(attack)
    elif name == RADIO_INFREQUENCY:
        suitTrack = doRadioInfrequency(attack)
    elif name == VOICEMAIL:
        suitTrack = doVoicemail(attack)
    elif name == WIRE_CUT:
        suitTrack = doWireCut(attack)
    elif name == PAPER_CUT:
        suitTrack = doPaperCut(attack)
    elif name == EXPLODING_BILL:
        suitTrack = doExplodingBill(attack)
    elif name == FIRE_COG:
        suitTrack = doWhirlwind(attack)
    elif name == GOOD_MORNING_TOONTOWN:
        suitTrack = doGoodMorningToontown(attack)
    elif name == CARESS:
        suitTrack = doSnipe(attack)
    elif name == COLLECT_CALL_FEES:
        suitTrack = doCollectCallCalculations(attack)
    elif name == COLLECT_CALL:
        suitTrack = doCollectCall(attack)
    elif name == SLUSH_FUND:
        suitTrack = doSlushFund(attack)
    elif name == JURY_NOTICE:
        suitTrack = doJuryNotice(attack)
    elif name == CEASE_AND_DESIST:
        suitTrack = doCeaseAndDesist(attack)
    elif name == INVESTMENT:
        suitTrack = doKamikaze(attack)
    elif name == FIELD_PROMOTION:
        suitTrack = doInvestment(attack)
    elif name == WIRETAPPED:
        suitTrack = doWiretapped(attack)
    elif name == SHORT_SQUEEZE:
        suitTrack = doShortSqueeze(attack)
    elif name == BLUE_CHIP:
        suitTrack = doBlueChip(attack)
    elif name == FALLING_KNIFE:
        suitTrack = doFallingKnife(attack)
    elif name == LD_AFTERSHOCK:
        suitTrack = doQuake(attack)
    elif name == LIFE_INSURANCE:
        suitTrack = doLifeInsurance(attack)
    elif name == LD_RED_TAPE:
        suitTrack = doRedTape(attack)
    elif name == LD_RE_ORG:
        suitTrack = doReOrg(attack)
    elif name == MP_HOT_AIR:
        suitTrack = doHotAir(attack)
    elif name == HR_POWER_TRIP:
        suitTrack = doPowerTrip(attack)
    elif name == POISON_SPRAY:
        suitTrack = doPoisonSpray(attack)
    elif name == GUILT_TRIP:
        suitTrack = doGuiltTrip(attack)
    elif name == STEAL_SAFE:
        suitTrack = doStealSafe(attack)
    elif name == COURT_SANCTION:
        suitTrack = doCourtSanction(attack)
    elif name == OIL_RAIN:
        suitTrack = doOilRain(attack)
    elif name == EMBEZZLE:
        suitTrack = doEmbezzle(attack)
    elif name == FLOOD_THE_MARKET:
        suitTrack = doFloodTheMarket(attack)
    elif name == CAGE:
        suitTrack = doCage(attack)
    elif name == CHAINSAW_REVVING_UP:
        suitTrack = doRevvingUp(attack)
    elif name == DETONATE:
        suitTrack = doDetonate(attack, 2)
    elif name == DETONATE_2:
        suitTrack = doDetonate(attack, 3)
    elif name == DETONATE_3:
        suitTrack = doDetonate(attack, 4)
    elif name == HEAD_ROLLER:
        if suit.dna.name == 'crf':
            suitTrack = doBayouBash2(attack)
        else:
            suitTrack = doHeadRoller(attack, 2)
    elif name == HEAD_ROLLER_2:
        if suit.dna.name == 'crf':
            suitTrack = doBayouBash2(attack)
        else:
            suitTrack = doHeadRoller(attack, 3)
    elif name == HEAD_ROLLER_3:
        if suit.dna.name == 'crf':
            suitTrack = doHeadRollerHighRoller(attack, 4)
        else:
            suitTrack = doHeadRoller(attack, 4)
    elif name == UNION_BUST:
        suitTrack = doUnionBust(attack, 2)
    elif name == UNION_BUST_2:
        suitTrack = doUnionBust(attack, 3)
    elif name == UNION_BUST_3:
        suitTrack = doUnionBust(attack, 4)
    elif name == CHAINSAW_DETONATE:
        suitTrack = doDetonate(attack, 2)
    elif name == CHAINSAW_DETONATE_2:
        suitTrack = doDetonate(attack, 3)
    elif name == CHAINSAW_DETONATE_3:
        suitTrack = doDetonate(attack, 4)
    elif name == GUILT_TRIP_WSI:
        suitTrack = doGuiltTrip(attack)
    elif name == MONEY_TRIP:
        suitTrack = doSynergy(attack)
    elif name == UNION_DUES:
        suitTrack = doUnionCalculations(attack)
    elif name == UNION_BUSTER:
        suitTrack = doStomper(attack)
    elif name == EVIL_EYE_WSI:
        suitTrack = doEvilEye(attack)
    elif name == COURT_RECORD_1:
        suitTrack = doCourtRecord1(attack)
    elif name == COURT_RECORD_2:
        suitTrack = doCourtRecord2(attack)
    elif name == COURT_RECORD_3:
        suitTrack = doCourtRecord1(attack)
    elif name == COURT_RECORD_4:
        suitTrack = doCourtRecord2(attack)
    elif name == COURT_RECORD_5:
        suitTrack = doCourtRecord1(attack)
    elif name == BOOKKEEPING:
        suitTrack = doBookKeeping(attack)
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
    elif name == SWIRL_BATH:
        suitTrack = doRolled(attack)
    elif name == LEGALESE:
        suitTrack = doLegalese(attack)
    elif name == COURT_COSTS:
        suitTrack = doCourtCalculations(attack)
    elif name == LAW_BOOK:
        suitTrack = doThrowBook(attack)
    elif name == SNOW:
        suitTrack = doShieldsUp(attack)
    elif name == HEAT_WAVE:
        suitTrack = doHeatWave(attack)
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
        suitTrack = doConeOfShame(attack)
    elif name == QUAKE:
        suitTrack = doQuake(attack)
    elif name == RAZZLE_DAZZLE:
        suitTrack = doRazzleDazzle(attack)
    elif name == RED_TAPE:
        suitTrack = doRedTape(attack)
    elif name == DROWNING:
        suitTrack = doDrowning(attack)
    elif name == HEAVY_RAINFALL:
        suitTrack = doHeavyRain2(attack)
    elif name == AFTERSHOCK:
        suitTrack = doAfterShock(attack)
    elif name == FREEZING_RAIN:
        suitTrack = doFreezingRain(attack)
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
        suitTrack = doRolodex(attack)
    elif name == RESTRAINING_ORDER_WSI:
        suitTrack = doRestrainingOrder(attack)
    elif name == BLAST:
        suitTrack = doBlast(attack)
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
    elif name == WATERCOOLER:
        suitTrack = doWatercooler(attack)
    elif name == WITHDRAWAL:
        suitTrack = doWithdrawal(attack)
    elif name == WRITE_OFF:
        suitTrack = doWriteOff(attack)
    else:
        notify.warning('unknown attack: %d substituting Finger Wag' % name)
        suitTrack = doDefault(attack)
    camTrack = MovieCamera.chooseSuitShot(attack, suitTrack.getDuration())
    battle = attack['battle']
    target = attack['target']
    groupStatus = attack['group']
    if groupStatus == ATK_TGT_SINGLE:
        toon = target['toon']
        toonHprTrack = Sequence(Func(toon.headsUp, battle, MovieUtil.PNT3_ZERO), Func(toon.loop, 'neutral'))
    else:
        toonHprTrack = Parallel()
        for t in target:
            toon = t['toon']
            toonHprTrack.append(Sequence(Func(toon.headsUp, battle, MovieUtil.PNT3_ZERO), Func(toon.loop, 'neutral')))

    suit = attack['suit']
    neutralIval = (Func(suit.loop,  'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    suitTrack = Sequence(suitTrack, neutralIval, toonHprTrack)
    suitPos = suit.getPos(battle)
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    #if battle.isSuitLured(suit):
    resetTrack = getResetTrack(suit, battle)
    resetSuitTrack = Sequence(resetTrack, suitTrack)
    waitTrack = Sequence(Wait(resetTrack.getDuration()), Func(battle.unlureSuit, suit))
    resetCamTrack = Sequence(waitTrack, camTrack)
    return (resetSuitTrack, resetCamTrack)


def getResetTrack(suit, battle):
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    moveDist = Vec3(suit.getPos(battle) - resetPos).length()
    moveDuration = 0.5
    walkTrack = Sequence(Func(suit.setHpr, battle, resetHpr), ActorInterval(suit, 'walk', startTime=1, duration=moveDuration, endTime=1e-05), (Func(suit.loop,  'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))))
    moveTrack = LerpPosInterval(suit, moveDuration, resetPos, other=battle)
    return Parallel(walkTrack, moveTrack)


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
    walkTrack = Sequence(Func(suit.setHpr, battle, resetHpr), ActorInterval(suit, 'walk', startTime=1, duration=moveDuration, endTime=0.0001), (Func(suit.loop,  'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))))
    moveTrack = LerpPosInterval(suit, moveDuration, resetPos, other=battle)
    return Parallel(walkTrack, moveTrack)


def getSuitTrack(attack, delay = 1e-06, splicedAnims = None):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    target = attack['target']
    toon = target['toon']
    name = attack['id']
    targetPos = toon.getPos(battle)
    taunt = getAttackTaunt(attack['name'], tauntIndex)
    trapStorage = {}
    trapStorage['trap'] = None
    track = Sequence(Wait(delay))
    if attack[
        'suitName'] == 'csm':  # It isn't just 'caseman', it really all depends on the shorthand you have for the Case Manager.  If it is not 'caseman', change it to whatever is the actual shorthand for the Case Manager, or the Case Manager will not grunt as intended.
        track.append(Func(suit.setChatAbsolute, random.choice(['Hrm...', 'Hmph...', 'Hm, hm...', 'Hrnhmpf...']),
                          CFSpeech | CFTimeout))
    elif attack[
        'suitName'] == 'fbd':  # It isn't just 'caseman', it really all depends on the shorthand you have for the Case Manager.  If it is not 'caseman', change it to whatever is the actual shorthand for the Case Manager, or the Case Manager will not grunt as intended.
        track.append(Func(suit.setChatAbsolute, random.choice(['Hrm...', 'Hmph...', 'Hm, hm...', 'Hrnhmpf...']),
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
        track.append(ActorInterval(suit, attack['animName']))
    origPos, origHpr = battle.getActorPosHpr(suit)
    track.append(Func(suit.setHpr, battle, origHpr))
    track.append(Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))

    def returnTrapToSuit(suit = suit, trapStorage = trapStorage):
        return

    track.append(Func(returnTrapToSuit))
    return track


def getSuitAnimTrack(attack, delay = 0):
    suit = attack['suit']
    tauntIndex = attack['taunt']
    name = attack['id']
    taunt = getAttackTaunt(attack['name'], tauntIndex)
    track = Sequence(Wait(delay))
    if attack[
        'suitName'] == 'csm':  # It isn't just 'caseman', it really all depends on the shorthand you have for the Case Manager.  If it is not 'caseman', change it to whatever is the actual shorthand for the Case Manager, or the Case Manager will not grunt as intended.
        track.append(Func(suit.setChatAbsolute, random.choice(['Hrm...', 'Hmph...', 'Hm, hm...', 'Hrnhmpf...']),
                          CFSpeech | CFTimeout))
    elif attack[
        'suitName'] == 'fbd':  # It isn't just 'caseman', it really all depends on the shorthand you have for the Case Manager.  If it is not 'caseman', change it to whatever is the actual shorthand for the Case Manager, or the Case Manager will not grunt as intended.
        track.append(Func(suit.setChatAbsolute, random.choice(['Hrm...', 'Hmph...', 'Hm, hm...', 'Hrnhmpf...']),
                          CFSpeech | CFTimeout))
    else:
        track.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    track.append(ActorInterval(suit, attack['animName']))
    track.append(Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    return track


def getPartTrack(particleEffect, startDelay, durationDelay, partExtraArgs):
    particleEffect = partExtraArgs[0]
    parent = partExtraArgs[1]
    if len(partExtraArgs) > 2:
        worldRelative = partExtraArgs[2]
    else:
        worldRelative = 1
    return Sequence(Wait(startDelay), ParticleInterval(particleEffect, parent, worldRelative, duration=durationDelay, cleanup=True))


def getToonTrack(attack, damageDelay = 1e-06, damageAnimNames = None, dodgeDelay = 0.0001, dodgeAnimNames = None, splicedDamageAnims = None, splicedDodgeAnims = None, target = None, showDamageExtraTime = 0.01, showMissedExtraTime = 0.5):
    if not target:
        target = attack['target']
    toon = target['toon']
    battle = attack['battle']
    suit = attack['suit']
    suitPos = suit.getPos(battle)
    dmg = target['hp']
    animTrack = Sequence()
    animTrack.append(Func(toon.headsUp, battle, suitPos))
    if dmg > 0:
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


def getPropThrowTrack(attack, prop, hitPoints = [], missPoints = [], hitDuration = 0.5, missDuration = 0.5, hitPointNames = 'none', missPointNames = 'none', lookAt = 'none', groundPointOffSet = 0, missScaleDown = None, parent = render):
    target = attack['target']
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
    if damageAnimNames:
        for d in damageAnimNames:
            toonTrack.append(ActorInterval(toon, d))

        indicatorTrack = Sequence(Wait(delay + showDamageExtraTime), Func(__doDamage, toon, dmg, died))
    else:
        splicedAnims = getSplicedAnimsTrack(splicedDamageAnims, actor=toon)
        toonTrack.append(splicedAnims)
        indicatorTrack = Sequence(Wait(delay + showDamageExtraTime), Func(__doDamage, toon, dmg, died))
    soundTrack = getSoundTrack('laff_loss.ogg', delay=delay, node=toon)
    toonTrack.append(Func(toon.loop, 'neutral'))
    if died:
        suit = attack['suit']
        toonTrack.append(Wait(3.0))
        if suit.getStyleName() in OTPLocalizerEnglish.SuitDefeatTaunts:
            suitResponseTrack.append(Parallel(Sequence(Wait(3.0), Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitDefeatTaunts[suit.getStyleName()]), CFSpeech | CFTimeout))))
        else:
            suitResponseTrack.append(Parallel(Sequence(Wait(3.0), Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitDefeatTauntsNone), CFSpeech | CFTimeout))))
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


def getSoundTrack(fileName, delay = 0.01, duration = None, node = None):
    soundEffect = globalBattleSoundCache.getSound(fileName)
    if duration:
        return Sequence(Wait(delay), SoundInterval(soundEffect, duration=duration, node=node))
    else:
        return Sequence(Wait(delay), SoundInterval(soundEffect, node=node))


def doClipOnTie(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    tie = globalPropPool.getProp('clip-on-tie')
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        throwDelay = 2.17
        damageDelay = 3.3
        dodgeDelay = 3.1
    elif suitType == 'b':
        throwDelay = 2.17
        damageDelay = 3.3
        dodgeDelay = 3.1
    elif suitType == 'c':
        throwDelay = 1.45
        damageDelay = 2.61
        dodgeDelay = 2.34
    suitTrack = getSuitTrack(attack)
    posPoints = [Point3(0.66, 0.51, 0.28), VBase3(-69.652, -17.199, 67.96)]
    tiePropTrack = Sequence(getPropAppearTrack(tie, suit.getRightHand(), posPoints, 0.5, MovieUtil.PNT3_ONE, scaleUpTime=0.5, poseExtraArgs=['clip-on-tie', 0]))
    if dmg > 0:
        tiePropTrack.append(ActorInterval(tie, 'clip-on-tie', duration=throwDelay, startTime=1.1))
    else:
        tiePropTrack.append(Wait(throwDelay))
    tiePropTrack.append(Func(tie.setHpr, Point3(0, -90, 0)))
    tiePropTrack.append(getPropThrowTrack(attack, tie, [__toonFacePoint(toon)], [__toonGroundPoint(attack, toon, 0.1)], hitDuration=0.4, missDuration=0.8, missScaleDown=1.2))
    toonTrack = getToonTrack(attack, damageDelay, ['conked'], dodgeDelay, ['sidestep'])
    throwSound = getSoundTrack('SA_powertie_throw.ogg', delay=throwDelay + 1, node=suit)
    return Parallel(suitTrack, toonTrack, tiePropTrack, throwSound)

def doDisassemble(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt(attack['name'], tauntIndex)
    tauntInterval = Sequence(Wait(2.1), Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    damageDelay = 2.5
    attackDelay = 2.5
    sprayEffect = BattleParticles.createParticleEffect(file='reorgSpray')
    suitTrack = Sequence(Wait(2.1), ActorInterval(suit, attack['animName']))
    suitPos = suit.getPos(battle)
    cagePropTracks = Parallel()
    cage = loader.loadModel('phase_3.5/models/modules/desk_only')
    cagePos = [Point3(suitPos.getX() - 3, 3, 0), suit.getHpr(battle)]
    cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, 0.01, scaleUpPoint=Point3(1.5), scaleUpTime=2.1),
            Parallel(
                cage.posInterval(0.75, Point3(suitPos.getX() - 3, 3, 0), blendType='easeIn'),
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
                             dodgeAnimNames=['duck'], showDamageExtraTime=2.1, showMissedExtraTime=2.0)
    if dmg > 0:
        return Parallel(suitTrack, tauntInterval, cagePropTracks, toonTrack, headTracks, chestTracks)
    else:
        return Parallel(suitTrack, tauntInterval, cagePropTracks,  toonTrack)


def doClockChange(attack):
    suit = attack['suit']
    battle = attack['battle']

    #cameraTrack = Sequence(LerpPosHprInterval(camera, duration=0.95, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'))
    suitTrack = Sequence(getSuitAnimTrack(attack))
    toonTracks = getToonTracks(attack, suitTrack.getDuration() - 1.5, ['slip-backward'], suitTrack.getDuration() - 1.5, ['shrug'])
    soundTrack = getSoundTrack('SA_clock_trigger.ogg', node=suit)
    return Parallel(suitTrack, toonTracks, soundTrack)



def doPoundKey(attack):
    suit = attack['suit']
    battle = attack['battle']
    phone = globalPropPool.getProp('phone')
    receiver = globalPropPool.getProp('receiver')
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect('PoundKey')
    BattleParticles.setEffectTexture(particleEffect, 'poundsign', color=Vec4(0, 0, 0, 1))
    suitTrack = getSuitTrack(attack)
    partTrack = getPartTrack(particleEffect, 2.1, 1.55, [particleEffect, suit, 0])
    phonePosPoints = [Point3(0.23, 0.17, -0.11), VBase3(5.939, 2.763, -177.591)]
    receiverPosPoints = [Point3(0.23, 0.17, -0.11), VBase3(5.939, 2.763, -177.591)]
    propTrack = Sequence(Wait(0.3), Func(__showProp, phone, suit.getLeftHand(), phonePosPoints[0], phonePosPoints[1]), Func(__showProp, receiver, suit.getLeftHand(), receiverPosPoints[0], receiverPosPoints[1]), LerpScaleInterval(phone, 0.5, MovieUtil.PNT3_ONE, MovieUtil.PNT3_NEARZERO), Wait(0.74), Func(receiver.wrtReparentTo, suit.getRightHand()), LerpPosHprInterval(receiver, 0.0001, Point3(-0.45, 0.48, -0.62), VBase3(-87.47, -18.21, 7.82)), Wait(3.14), Func(receiver.wrtReparentTo, phone), Wait(0.62), LerpScaleInterval(phone, 0.5, MovieUtil.PNT3_NEARZERO), Func(MovieUtil.removeProps, [receiver, phone]))
    toonTrack = getToonTrack(attack, 2.7, ['cringe'], 1.9, ['sidestep'])
    soundTrack = getSoundTrack('SA_hangup.ogg', delay=1.3, node=suit)
    return Parallel(suitTrack, toonTrack, propTrack, partTrack, soundTrack)

def doBayouBash(attack):
    name = attack['id']
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(ActorInterval(attack['suit'], 'snap'), ActorInterval(attack['suit'], 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    #cameraTrack = Func(camera.setPosHpr, 0, -10, 10, 0, -30, 0)
    suitSpeechTrack = Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitBashPhrases), CFSpeech | CFTimeout)
    soundTrack = getSoundTrack('SA_bash.ogg', node=suit)
    if name == WHITE_POWDER:
        suitTrack.append(doWhitePowder(attack))
    return Parallel(suitTrack, soundTrack, suitSpeechTrack)

def doBayouBashSnap(attack):
    name = attack['id']
    suit = attack['suit']
    battle = attack['battle']
    pbpText = attack['playByPlayText']
    pbpDc = PlayByPlayText.PlayByPlayText()

    pbpDesc = pbpDc.getShowIntervalDesc('The Litigator absolutely swamps you with cogs!', 3.5)
    pbpTrack = pbpText.getShowIntervalCheat('Bayou Bash!', 3.5)
    suitTrack = Sequence(ActorInterval(attack['suit'], 'snap'), ActorInterval(attack['suit'], 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    #cameraTrack = Func(camera.setPosHpr, 0, -10, 10, 0, -30, 0)
    suitSpeechTrack = Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitBashPhrases), CFSpeech | CFTimeout)
    soundTrack = getSoundTrack('SA_bash.ogg', node=suit)
    return Parallel(suitTrack, soundTrack, suitSpeechTrack)

def doBayouBash2(attack):
    name = attack['id']
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(ActorInterval(attack['suit'], 'snap'), ActorInterval(attack['suit'], 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    #cameraTrack = Func(camera.setPosHpr, 0, -10, 10, 0, -30, 0)
    suitSpeechTrack = Func(suit.setChatAbsolute, random.choice(["What'ya waitin' for, babe? Hop on fftage! let'ff get hoppin' and boppin', jumpin' and jinglin', ffingin' and ffwingin'!", "Ohoho-no-no, takeff a party to partiffipate and play, and I ffay play!!", "Get ready for the ffho-ho-how of a lifetime, Bobby Dazzler!"]), CFSpeech | CFTimeout)
    soundTrack = getSoundTrack('SA_bash.ogg', node=suit)
    if name == HEAD_ROLLER:
        suitTrack.append(doHeadRollerHighRoller(attack, 2))
    elif name == HEAD_ROLLER_2:
        suitTrack.append(doHeadRollerHighRoller(attack, 3))
    return Parallel(suitTrack, soundTrack, suitSpeechTrack)

def doCourtCalculations(attack):
    suit = attack['suit']
    battle = attack['battle']
    calculator = globalPropPool.getProp('calculator')
    suitTrack = Sequence(ActorInterval(attack['suit'], 'calculating-costs'), ActorInterval(attack['suit'], 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    suitSpeechTrack = Func(suit.setChatAbsolute, "Calculating costs of litigation fees... Price index raised to %s." % attack['target'][0]['hp'], CFSpeech | CFTimeout)
    scaleUpPoint = Point3(1.0, 1.37, 1.31)
    calcPosPoints = [Point3(0.2, 0, 0), VBase3(0.2, 0, 0)]
    calcDuration = 2.0
    calcPropTrack = getPropTrack(calculator, suit.getRightHand(), calcPosPoints, 1e-06, calcDuration,
                                 scaleUpPoint=scaleUpPoint, anim=1, propName='calculator', animStartTime=0.5,
                                 animDuration=2.4)
    soundTrack = getSoundTrack('SA_calculating_costs.ogg', node=suit)
    suitTrack.append(doCourtCosts(attack))
    return Parallel(suitTrack, soundTrack, suitSpeechTrack, calcPropTrack)

def doCollectCallCalculations(attack):
    suit = attack['suit']
    battle = attack['battle']
    calculator = globalPropPool.getProp('calculator')
    suitTrack = Sequence(ActorInterval(attack['suit'], 'calculating-costs'), ActorInterval(attack['suit'], 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    suitSpeechTrack = Func(suit.setChatAbsolute, "Calculating costs of collect call fees... Price index raised to %s." % attack['target'][0]['hp'], CFSpeech | CFTimeout)
    scaleUpPoint = Point3(1.0, 1.37, 1.31)
    calcPosPoints = [Point3(0.2, 0, 0), VBase3(0.2, 0, 0)]
    calcDuration = 2.0
    calcPropTrack = getPropTrack(calculator, suit.getRightHand(), calcPosPoints, 1e-06, calcDuration,
                                 scaleUpPoint=scaleUpPoint, anim=1, propName='calculator', animStartTime=0.5,
                                 animDuration=2.4)
    soundTrack = getSoundTrack('SA_calculating_costs.ogg', node=suit)
    suitTrack.append(doCollectCallFees(attack))
    return Parallel(suitTrack, soundTrack, suitSpeechTrack, calcPropTrack)

def doInterestCalculations(attack):
    suit = attack['suit']
    battle = attack['battle']
    calculator = globalPropPool.getProp('calculator')
    suitTrack = Sequence(ActorInterval(attack['suit'], 'calculating-costs'), ActorInterval(attack['suit'], 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    suitSpeechTrack = Func(suit.setChatAbsolute, "Calculating costs of interest fees... Price index raised to %s." % attack['target'][0]['hp'], CFSpeech | CFTimeout)
    scaleUpPoint = Point3(1.0, 1.37, 1.31)
    calcPosPoints = [Point3(0.2, 0, 0), VBase3(0.2, 0, 0)]
    calcDuration = 2.0
    calcPropTrack = getPropTrack(calculator, suit.getRightHand(), calcPosPoints, 1e-06, calcDuration,
                                 scaleUpPoint=scaleUpPoint, anim=1, propName='calculator', animStartTime=0.5,
                                 animDuration=2.4)
    soundTrack = getSoundTrack('SA_calculating_costs.ogg', node=suit)
    suitTrack.append(doSynergy2(attack))
    return Parallel(suitTrack, soundTrack, suitSpeechTrack, calcPropTrack)

def doUnionCalculations(attack):
    suit = attack['suit']
    battle = attack['battle']
    calculator = globalPropPool.getProp('calculator')
    suitTrack = Sequence(ActorInterval(attack['suit'], 'calculating-costs'), ActorInterval(attack['suit'], 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    suitSpeechTrack = Func(suit.setChatAbsolute, "Calculating costs of union dues... Price index raised to %s." % attack['target'][0]['hp'], CFSpeech | CFTimeout)
    scaleUpPoint = Point3(1.0, 1.37, 1.31)
    calcPosPoints = [Point3(0.2, 0, 0), VBase3(0.2, 0, 0)]
    calcDuration = 2.0
    calcPropTrack = getPropTrack(calculator, suit.getRightHand(), calcPosPoints, 1e-06, calcDuration,
                                 scaleUpPoint=scaleUpPoint, anim=1, propName='calculator', animStartTime=0.5,
                                 animDuration=2.4)
    soundTrack = getSoundTrack('SA_calculating_costs.ogg', node=suit)
    suitTrack.append(doUnionDues(attack))
    return Parallel(suitTrack, soundTrack, suitSpeechTrack, calcPropTrack)


def doShred(attack):
    suit = attack['suit']
    battle = attack['battle']
    paper = globalPropPool.getProp('shredder-paper')
    shredder = globalPropPool.getProp('shredder')
    particleEffect = BattleParticles.createParticleEffect('Shred')
    suitTrack = getSuitTrack(attack)
    partTrack = getPartTrack(particleEffect, 3.5, 1.9, [particleEffect, suit, 0])
    paperPosPoints = [Point3(0.59, -0.31, 0.81), VBase3(79.224, 32.576, -179.449)]
    paperPropTrack = getPropTrack(paper, suit.getRightHand(), paperPosPoints, 2.4, 1e-05, scaleUpTime=0.2, anim=1, propName='shredder-paper', animDuration=1.5, animStartTime=2.8)
    shredderPosPoints = [Point3(0, -0.12, -0.34), VBase3(-90.0, -53.77, -0.0)]
    shredderPropTrack = getPropTrack(shredder, suit.getLeftHand(), shredderPosPoints, 1, 3, scaleUpPoint=Point3(4.81, 4.81, 4.81))
    toonTrack = getToonTrack(attack, suitTrack.getDuration() - 1.1, ['conked'], suitTrack.getDuration() - 3.1, ['sidestep'])
    soundTrack = getSoundTrack('SA_shred.ogg', delay=3.4, node=suit)
    return Parallel(suitTrack, paperPropTrack, shredderPropTrack, partTrack, toonTrack, soundTrack)

def doPaperCut(attack):
    suit = attack['suit']
    battle = attack['battle']
    paper = globalPropPool.getProp('shredder-paper')
    #shredder = globalPropPool.getProp('shredder')
    particleEffect = BattleParticles.createParticleEffect('Shred2')
    suitTrack = getSuitTrack(attack)
    partTrack = getPartTrack(particleEffect, 0.5, 3.0, [particleEffect, suit, 0])
    paperPosPoints = [Point3(0.59, -0.31, 0.81), VBase3(79.224, 32.576, -179.449)]
    paperPropTrack = getPropTrack(paper, suit.getRightHand(), paperPosPoints, .1, 1e-05, scaleUpTime=0.1, anim=1, propName='shredder-paper', animDuration=2.0, animStartTime=0.5)
    #shredderPosPoints = [Point3(0, -0.12, -0.34), VBase3(-90.0, -53.77, -0.0)]
    #shredderPropTrack = getPropTrack(shredder, suit.getLeftHand(), shredderPosPoints, 1, 3, scaleUpPoint=Point3(4.81, 4.81, 4.81))
    toonTrack = getToonTrack(attack, suitTrack.getDuration() - .5, ['cringe'], suitTrack.getDuration() - 3.1, ['sidestep'])
    soundTrack = getSoundTrack('SA_shred.ogg', delay=0.5, node=suit)
    suitSpeechTrack = Sequence(Wait(3.0), Func(suit.setChatAbsolute, 'Hmph, looks like your gags will be less effective.', CFSpeech | CFTimeout))
    return Parallel(suitTrack, paperPropTrack, partTrack, toonTrack, soundTrack, suitSpeechTrack)

def doSongAndDance(attack):
    suit = attack['suit']
    battle = attack['battle']
    cane = globalPropPool.getProp('cane')
    cogHead = suit.find('**/to_head')
    #encounter = {'isSkelecog': suit.getSkelecog()}
    #if encounter['isSkelecog']:
        #pass
   # else:
        #for part in suit.getHeadParts():
           # part.reparentTo(cogHead)
    hat = globalPropPool.getProp('hat')
    hat.setR(326.98)
    suitTrack = getSuitAnimTrack(attack)
    caneposPoints = [Point3(-0.13, 0.18, -0.08)]
    hatposPoints = [Point3(0, -0.10, 1.66)]
    propTrack = Sequence(getPropAppearTrack(cane, suit.getRightHand(), caneposPoints, 0.4, MovieUtil.PNT3_ONE, scaleUpTime=0.1))
    propTrack.append(getPropAppearTrack(hat, cogHead, hatposPoints, 0.4, MovieUtil.PNT3_ONE, scaleUpTime=0.1))
    propTrack.append(Wait(4.6))
    propTrack.append(LerpScaleInterval(hat, 0.1, MovieUtil.PNT3_NEARZERO))
    propTrack.append(LerpScaleInterval(cane, 0.1, MovieUtil.PNT3_NEARZERO))
    propTrack.append(Func(MovieUtil.removeProp, hat))
    propTrack.append(Func(MovieUtil.removeProp, cane))
    damageAnims = ['cringe']
    dodgeAnims = ['applause']
    toonTracks = getToonTracks(attack, 4.1, ['cringe'], 4.223, ['applause'])
    soundTrack = getSoundTrack('AA_heal_happydance.ogg', delay=.01, node=suit)
    return Parallel(suitTrack, toonTracks, propTrack, soundTrack)

def doCaress(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(ActorInterval(attack['suit'], 'kneel-into'), ActorInterval(attack['suit'], 'kneel-caress-into'), ActorInterval(attack['suit'], 'caress'), ActorInterval(attack['suit'], 'kneel-caress-out'), ActorInterval(attack['suit'], 'kneel-out'), ActorInterval(attack['suit'], 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    toonTracks = getToonTrack(attack, 4.1, ['cringe'], 4.223, ['applause'])
    talkTrack = Sequence(Func(suit.setChatAbsolute, "These perfect prestissimo plays have been played and presented by the powerful proprietor of prowess!", CFSpeech | CFTimeout), Wait(2.8), Func(suit.setChatAbsolute, "You can always find me baby, beyond the sea.", CFSpeech | CFTimeout), Wait(2.5), Func(suit.setChatAbsolute, "But like any good song, it's time for this one man big band to fade out!", CFSpeech | CFTimeout), Wait(3.7), Func(suit.setChatAbsolute, "Skibidiba-ta-ta!", CFSpeech | CFTimeout))

    return Parallel(suitTrack, toonTracks, talkTrack)

def doFillWithLead(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    pencil = globalPropPool.getProp('pencil')
    sharpener = globalPropPool.getProp('sharpener')
    BattleParticles.loadParticles()
    sprayEffect = BattleParticles.createParticleEffect(file='fillWithLeadSpray')
    headSmotherEffect = BattleParticles.createParticleEffect(file='fillWithLeadSmother')
    torsoSmotherEffect = BattleParticles.createParticleEffect(file='fillWithLeadSmother')
    legsSmotherEffect = BattleParticles.createParticleEffect(file='fillWithLeadSmother')
    BattleParticles.setEffectTexture(sprayEffect, 'roll-o-dex', color=Vec4(0, 0, 0, 1))
    BattleParticles.setEffectTexture(headSmotherEffect, 'roll-o-dex', color=Vec4(0, 0, 0, 1))
    BattleParticles.setEffectTexture(torsoSmotherEffect, 'roll-o-dex', color=Vec4(0, 0, 0, 1))
    BattleParticles.setEffectTexture(legsSmotherEffect, 'roll-o-dex', color=Vec4(0, 0, 0, 1))
    suitTrack = getSuitTrack(attack)
    sprayTrack = getPartTrack(sprayEffect, 2.5, 1.9, [sprayEffect, suit, 0])
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
    toonTrack = getToonTrack(attack, splicedDamageAnims=damageAnims, dodgeDelay=suitTrack.getDuration() - 3.1, dodgeAnimNames=['sidestep'], showDamageExtraTime=4.5, showMissedExtraTime=1.6)
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
    partDelay = 3.5
    partIvalDelay = 0.7
    partDuration = 1.0
    headTrack = getPartTrack(headSmotherEffect, partDelay, partDuration, [headSmotherEffect, toon, 0])
    torsoTrack = getPartTrack(torsoSmotherEffect, partDelay + partIvalDelay, partDuration, [torsoSmotherEffect, toon, 0])
    legsTrack = getPartTrack(legsSmotherEffect, partDelay + partIvalDelay * 2, partDuration, [legsSmotherEffect, toon, 0])

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

    if dmg > 0:
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
        return Parallel(suitTrack, pencilPropTrack, sharpenerPropTrack, sprayTrack, headTrack, torsoTrack, legsTrack, colorTrack, toonTrack)
    else:
        return Parallel(suitTrack, pencilPropTrack, sharpenerPropTrack, sprayTrack, toonTrack)


def doFountainPen(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    pen = globalPropPool.getProp('pen')

    def getPenTip(pen = pen):
        tip = pen.find('**/joint_toSpray')
        return tip.getPos(render)

    hitPoint = lambda toon = toon: __toonFacePoint(toon)
    missPoint = lambda prop = pen, toon = toon: __toonMissPoint(prop, toon, 0, parent=render)
    hitSprayTrack = MovieUtil.getSprayTrack(battle, VBase4(0, 0, 0, 1), getPenTip, hitPoint, 0.2, 0.2, 0.2, horizScale=0.1, vertScale=0.1)
    missSprayTrack = MovieUtil.getSprayTrack(battle, VBase4(0, 0, 0, 1), getPenTip, missPoint, 0.2, 0.2, 0.2, horizScale=0.1, vertScale=0.1)
    suitTrack = getSuitTrack(attack)
    propTrack = Sequence(Wait(0.01), Func(__showProp, pen, suit.getRightHand(), MovieUtil.PNT3_ZERO), LerpScaleInterval(pen, 0.5, Point3(1.5, 1.5, 1.5)), Wait(1.05))
    if dmg > 0:
        propTrack.append(hitSprayTrack)
    else:
        propTrack.append(missSprayTrack)
    propTrack += [LerpScaleInterval(pen, 0.5, MovieUtil.PNT3_NEARZERO), Func(MovieUtil.removeProp, pen)]
    splashTrack = Sequence()
    if dmg > 0:

        def prepSplash(splash, targetPoint):
            splash.reparentTo(render)
            splash.setPos(targetPoint)
            scale = splash.getScale()
            splash.setBillboardPointWorld()
            splash.setScale(scale)

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
    penSpill = BattleParticles.createParticleEffect(file='penSpill')
    penSpill.setPos(getPenTip())
    penSpillTrack = getPartTrack(penSpill, 1.4, 0.7, [penSpill, pen, 0])
    toonTrack = getToonTrack(attack, 1.81, ['conked'], dodgeDelay=0.11, splicedDodgeAnims=[['duck', 0.01, 0.6]], showMissedExtraTime=1.66)
    soundTrack = getSoundTrack('SA_fountain_pen.ogg', delay=1.6, node=suit)
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack, penSpillTrack, splashTrack)


def doBookKeeping(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    toon = attack['target']['toon']
    if attack['suitName'] == 'csm':
        taunt = random.choice(['Hrm...', 'Hmph...', 'Hm, hm...', 'Hrnhmpf...'])
    elif attack['suitName'] == 'fbd':
        taunt = random.choice(['Hrm...', 'Hmph...', 'Hm, hm...', 'Hrnhmpf...'])
    else:
        taunt = getAttackTaunt(attack['name'], tauntIndex)
    suitTrack = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout),
                         ActorInterval(suit, attack['animName'], duration=3.0), ActorInterval(suit, 'sanction'), ActorInterval(suit, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))

    soundTrack1 = Sequence(SoundInterval(globalBattleSoundCache.getSound('suit_promotion_sfx.ogg'), node=suit))
    soundTrack2 = Sequence(Wait(3.4), SoundInterval(globalBattleSoundCache.getSound('SA_haymaker.ogg'), node=suit))
    soundTrack = Parallel(soundTrack1, soundTrack2)
    toonTrack = getToonTrack(attack, 3.4, ['conked'], 1.9, ['sidestep'])
    notifyTrack = Sequence(Wait(3.4 + 0.75), Func(toon.showHpText, "BANNED!", 10))
    return Parallel(suitTrack, soundTrack, toonTrack, notifyTrack)

def doRadioInfrequency(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt(attack['name'], tauntIndex)
    suitTrack = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout),
                         ActorInterval(suit, attack['animName'], duration=1.5), Wait(4.0), ActorInterval(suit,  attack['animName'], startTime=1.5), ActorInterval(suit, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))

    soundTrack = getSoundTrack('mus_dialup_0.ogg', delay=1.5)
    return Parallel(suitTrack, soundTrack)

def doElectrostaticEnergy(attack):
    suit = attack['suit']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt(attack['name'], tauntIndex)
    suitTrack = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout),
                         ActorInterval(suit, attack['animName'], duration=1.5), Wait(4.0),
                         ActorInterval(suit, attack['animName'], startTime=1.5), ActorInterval(suit, 'neutral%s' % (
            '-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    cagePropTracks = Parallel()
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    cage = loader.loadModel('phase_5/models/props/lightning')
    cagePosition = LerpHprInterval(cage, 0, Point3(180, 0, 0))
    #cage.setH(90)
    #cage.setPosHpr(0, 0, 0, 180, 0, 0)
    toonPos = toon.getPos(battle)
    y = toonPos.getY()
    if dmg == 0:
        y -= 5
    cagePos = [Point3(toonPos.getX(), y, 100.0), toon.getHpr(battle)]
    cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, .90, scaleUpPoint=Point3(4.0), scaleUpTime=1.0), Parallel(cagePosition),
            Parallel(
                cage.posInterval(0.1, Point3(toonPos.getX(), y, 0.1), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/AA_lightning.ogg'), duration=0.75, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_5/audio/sfx/AA_cog_shock.ogg'), node=cage),
            Wait(0.5),
            LerpFunctionInterval(cage.setAlphaScale, fromData=.5, toData=0, duration=0.5),
            Func(MovieUtil.removeProp, cage)
        )
    cagePropTracks.append(cagePropTrack)
    damageAnims = [['slip-forward', 0.0001, 0.5]]
    toonTrack = getToonTrack(attack, damageDelay=2.5, splicedDamageAnims=damageAnims, dodgeDelay=1.75, dodgeAnimNames=[], splicedDodgeAnims=[], showDamageExtraTime=0.5)
    oldcolor = render.getColorScale()
    lightingTrack = Sequence(Wait(0), LerpColorScaleInterval(render, 0.5, (0, 0.992, 1, 1)),
                             LerpColorScaleInterval(render, 2.5, (0, 0.992, 1, 1)),
                             LerpColorScaleInterval(render, 1, (oldcolor)))
    return Parallel(suitTrack, cagePropTracks, toonTrack, lightingTrack)

def doCourtMandate(attack):
    if attack['suitName'] == 'jur':
        suitTrack = doCourtMandateHeadAttorney(attack)
    else:
        suitTrack = doCourtRecord3(attack)
    return suitTrack


def doCourtMandateHeadAttorney(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt(attack['name'], tauntIndex)
    suitTrack = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout),
                         ActorInterval(suit, attack['animName'], duration=3.0), ActorInterval(suit, 'objection-out'), ActorInterval(suit, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))

    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_objection.ogg'), node=suit))
    return Parallel(suitTrack, soundTrack)

def doCourtRecord1(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(getSuitAnimTrack(attack), ActorInterval(attack['suit'], 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    return Parallel(suitTrack, soundTrack)

def doManagerialProtection(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(getSuitAnimTrack(attack), ActorInterval(attack['suit'], 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    notifyTrack = Func(suit.showHpTextWhite, 'IMMUNE!')
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    return Parallel(suitTrack, soundTrack, notifyTrack)

def doCourtRecord2(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(getSuitAnimTrack(attack), ActorInterval(attack['suit'], 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    return Parallel(suitTrack, soundTrack)

def doCourtRecord3(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt(attack['name'], tauntIndex)
    tauntTrack = Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout)
    suitTrack = Sequence(ActorInterval(attack['suit'], 'cease'), ActorInterval(attack['suit'], 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    return Parallel(suitTrack, soundTrack, tauntTrack)

def doRubOut(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    pad = globalPropPool.getProp('pad')
    pencil = globalPropPool.getProp('pencil')
    headEffect = BattleParticles.createParticleEffect('RubOut', color=toon.style.getHeadColor())
    torsoEffect = BattleParticles.createParticleEffect('RubOut', color=toon.style.getArmColor())
    legsEffect = BattleParticles.createParticleEffect('RubOut', color=toon.style.getLegColor())
    suitTrack = getSuitTrack(attack)
    padPosPoints = [Point3(-0.66, 0.81, -0.06), VBase3(14.93, -2.29, 180.0)]
    padPropTrack = getPropTrack(pad, suit.getLeftHand(), padPosPoints, 0.5, 2.57)
    pencilPosPoints = [Point3(0.04, -0.38, -0.1), VBase3(-170.223, -3.762, -62.929)]
    pencilPropTrack = getPropTrack(pencil, suit.getRightHand(), pencilPosPoints, 0.5, 2.57)
    toonTrack = getToonTrack(attack, 2.2, ['conked'], 2.0, ['jump'])
    hideTrack = Sequence()
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
    headTrack = getPartTrack(headEffect, partDelay + 0, 0.5, [headEffect, toon, 0])
    torsoTrack = getPartTrack(torsoEffect, partDelay + 1.1, 0.5, [torsoEffect, toon, 0])
    legsTrack = getPartTrack(legsEffect, partDelay + 2.2, 0.5, [legsEffect, toon, 0])

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

    soundTrack = getSoundTrack('SA_rubout.ogg', delay=1.7, node=suit)
    if dmg > 0:
        hideTrack.append(Wait(2.2))
        hideTrack.append(Func(battle.movie.needRestoreColor))
        hideTrack.append(hideParts(headParts))
        hideTrack.append(Wait(0.4))
        hideTrack.append(hideParts(torsoParts))
        hideTrack.append(Wait(0.4))
        hideTrack.append(hideParts(legsParts))
        hideTrack.append(Wait(1))
        hideTrack.append(showParts(headParts))
        hideTrack.append(showParts(torsoParts))
        hideTrack.append(showParts(legsParts))
        hideTrack.append(Func(battle.movie.clearRestoreColor))
        return Parallel(suitTrack, toonTrack, padPropTrack, pencilPropTrack, soundTrack, hideTrack, headTrack, torsoTrack, legsTrack)
    else:
        return Parallel(suitTrack, toonTrack, padPropTrack, pencilPropTrack, soundTrack)

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
    particleEffect = BattleParticles.createParticleEffect('FingerWag')
    BattleParticles.setEffectTexture(particleEffect, 'blah', color=Vec4(0.55, 0, 0.55, 1))
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        partDelay = 1.3
        damageDelay = 2.7
        dodgeDelay = 1.7
    elif suitType == 'b':
        partDelay = 1.3
        damageDelay = 2.7
        dodgeDelay = 1.8
    elif suitType == 'c':
        partDelay = 1.3
        damageDelay = 2.7
        dodgeDelay = 2.0
    suitTrack = getSuitTrack(attack)
    partTrack = getPartTrack(particleEffect, partDelay, 2, [particleEffect, suit, 0])
    suitName = attack['suitName']
    if suitName == 'mm':
        particleEffect.setPos(0.167, 1.5, 2.731)
    elif suitName == 'tw':
        particleEffect.setPos(0.167, 1.8, 5)
        particleEffect.setHpr(-90.0, -60.0, 180.0)
    elif suitName == 'pp':
        particleEffect.setPos(0.167, 1, 4.1)
    elif suitName == 'bs':
        particleEffect.setPos(0.167, 1, 5.1)
    elif suitName == 'bw':
        particleEffect.setPos(0.167, 1.9, suit.getHeight() - 1.8)
        particleEffect.setP(-110)
    toonTrack = getToonTrack(attack, damageDelay, ['slip-backward'], dodgeDelay, ['sidestep'])
    soundTrack = getSoundTrack('SA_finger_wag.ogg', delay=1.3, node=suit)
    return Parallel(suitTrack, toonTrack, partTrack, soundTrack)


def doWriteOff(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
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
    toon = target['toon']
    suitTrack = getSuitTrack(attack)
    stamp = globalPropPool.getProp('rubber-stamp')
    pad = globalPropPool.getProp('pad')
    cancelled = __makeCancelledNodePath()
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        padPosPoints = [Point3(-0.65, 0.83, -0.04), VBase3(5.625, 4.456, -165.125)]
        stampPosPoints = [Point3(-0.64, -0.17, -0.03), MovieUtil.PNT3_ZERO]
    elif suitType == 'c':
        padPosPoints = [Point3(0.19, -0.55, -0.21), VBase3(-166.76, -4.001, -1.658)]
        stampPosPoints = [Point3(-0.64, -0.08, 0.11), MovieUtil.PNT3_ZERO]
    else:
        padPosPoints = [Point3(-0.65, 0.83, -0.04), VBase3(5.625, 4.456, -165.125)]
        stampPosPoints = [Point3(-0.64, -0.17, -0.03), MovieUtil.PNT3_ZERO]
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

def doDrop(attack):
    suit = attack['suit']
    battle = attack['battle']
    name = attack['id']
    suitTrack = getSuitAnimTrack(attack, delay=0)
    objectTracks = Parallel()
    shadowTracks = Parallel()
    toonTracks = getToonTracks(attack, damageDelay=2.86, damageAnimNames=['Squish'], dodgeDelay=2.86, splicedDodgeAnims=[])
    soundTracks = Parallel()
    for t in attack['target']:
        toon = t['toon']
        dmg = t['hp']
        objName = {
            SANDBAG: 'sandbag',
            ANVIL: 'anvil',
            BIG_WEIGHT: 'weight',
            SAFE: 'safe',
            GRAND_PIANO: 'piano'
        }
        if name == SANDBAG:
            objZOffset = 0.75
            landFrames = 4
        elif name == ANVIL:
            objZOffset = 0.0
            landFrames = 1
        else:
            objZOffset = 0.0
            landFrames = 11
        object = globalPropPool.getProp(objName[name])
        if objName == 'weight':
            object.setScale(object.getScale() * 0.75)
        elif objName == 'safe':
            object.setScale(object.getScale() * 0.85)
        node = object.node()
        node.setBounds(OmniBoundingVolume())
        node.setFinal(1)
        suitTrack = getSuitTrack(attack)
        objectTrack = Sequence()

        def posObject(object, toon, miss, battle = battle):
            object.reparentTo(battle)
            object.setPos(toon.getPos(battle))
            object.setHpr(toon.getHpr(battle))
            if miss:
                object.setY(object.getY(battle) - 5)
            object.setZ(object.getPos(battle)[2] + objZOffset)

        objectTrack.append(Func(battle.movie.needRestoreRenderProp, object))
        objInit = Func(posObject, object, toon, dmg == 0)
        objectTrack.append(Wait(3.3))
        objectTrack.append(objInit)
        if dmg != 0 or name == SANDBAG or name == ANVIL:
            if hasattr(object, 'getAnimControls'):
                animProp = ActorInterval(object, objName[name])
                shrinkProp = LerpScaleInterval(object, 0.3, MovieUtil.PNT3_NEARZERO, startScale=object.getScale())
                objAnimShrink = ParallelEndTogether(animProp, shrinkProp)
                objectTrack.append(objAnimShrink)
            else:
                startingScale = 1.0
                object2 = MovieUtil.copyProp(object)
                posObject(object2, toon, dmg == 0)
                endingPos = object2.getPos()
                startPos = Point3(endingPos[0], endingPos[1], endingPos[2] + 5)
                startHpr = object2.getHpr()
                endHpr = Point3(startHpr[0] + 90, startHpr[1], startHpr[2])
                animProp = LerpPosInterval(object, landFrames / 24.0, endingPos, startPos=startPos)
                shrinkProp = LerpScaleInterval(object, 0.3, MovieUtil.PNT3_NEARZERO, startScale=startingScale)
                bounceProp = Effects.createZBounce(object, 2, endingPos, 0.5, 1.5)
                objAnimShrink = Sequence(Func(object.setScale, startingScale), Func(object.setH, endHpr[0]), animProp, bounceProp, Wait(1.5), shrinkProp)
                objectTrack.append(objAnimShrink)
                MovieUtil.removeProp(object2)
        elif hasattr(object, 'getAnimControls'):
            animProp = ActorInterval(object, objName[name], duration=landFrames / 24.0)

            def poseProp(prop, animName):
                prop.pose(animName, landFrames)

            poseProp = Func(poseProp, object, objName[name])
            wait = Wait(1.0)
            shrinkProp = LerpScaleInterval(object, 0.1, MovieUtil.PNT3_NEARZERO, startScale=object.getScale())
            objectTrack.append(animProp)
            objectTrack.append(poseProp)
            objectTrack.append(wait)
            objectTrack.append(shrinkProp)
        else:
            startingScale = 1.0
            object2 = MovieUtil.copyProp(object)
            posObject(object2, toon, dmg == 0)
            endingPos = object2.getPos()
            startPos = Point3(endingPos[0], endingPos[1], endingPos[2] + 5)
            startHpr = object2.getHpr()
            endHpr = Point3(startHpr[0] + 90, startHpr[1], startHpr[2])
            animProp = LerpPosInterval(object, landFrames / 24.0, endingPos, startPos=startPos)
            shrinkProp = LerpScaleInterval(object, 0.1, MovieUtil.PNT3_NEARZERO, startScale=startingScale)
            bounceProp = Effects.createZBounce(object, 2, endingPos, 0.5, 1.5)
            objAnimShrink = Sequence(Func(object.setScale, startingScale), Func(object.setH, endHpr[0]), animProp, bounceProp, Wait(1.5), shrinkProp)
            objectTrack.append(objAnimShrink)
            MovieUtil.removeProp(object2)
        objectTrack.append(Func(MovieUtil.removeProp, object))
        objectTrack.append(Func(battle.movie.clearRenderProp, object))
        objectTracks.append(objectTrack)
        dropShadow = MovieUtil.copyProp(toon.dropShadow)
        if name == SANDBAG or name == ANVIL:
            dropShadow.setScale(0.8)
        elif name == BIG_WEIGHT:
            dropShadow.setScale(2.0)
        elif name == SAFE:
            dropShadow.setScale(2.3)
        else:
            dropShadow.setScale(3.6)

        def posShadow(dropShadow = dropShadow, toon = toon, battle = battle, hp = dmg):
            dropShadow.reparentTo(battle)
            dropShadow.setPos(toon.getPos(battle))
            dropShadow.setHpr(toon.getHpr(battle))
            if hp == 0:
                dropShadow.setY(dropShadow.getY(battle) - 5)
            dropShadow.setZ(dropShadow.getZ() + 0.5)

        shadowTracks.append(Sequence(
            Wait(1.0),
            Func(battle.movie.needRestoreRenderProp, dropShadow),
            Func(posShadow),
            LerpScaleInterval(dropShadow, 1.86, dropShadow.getScale(), startScale=MovieUtil.PNT3_NEARZERO),
            Wait(0.3),
            Func(MovieUtil.removeProp, dropShadow),
            Func(battle.movie.clearRenderProp, dropShadow)
        ))
        soundTracks.append(Sequence(
            Wait(1.0),
            SoundInterval(globalBattleSoundCache.getSound('incoming_whistleALT.ogg'), duration=1.5, node=toon),
            SoundInterval(globalBattleSoundCache.getSound('AA_drop_%s%s.ogg' % ({SANDBAG: 'sandbag', ANVIL: 'anvil', BIG_WEIGHT: 'bigweight', SAFE: 'safe', GRAND_PIANO: 'piano'}[name], '_miss' if dmg == 0 else '')), duration=2.0, node=toon)
        ))
    return Parallel(suitTrack, objectTracks, shadowTracks, toonTracks, soundTracks)

def doNONWORKINGSHIT(attack):
    suit = attack['suit']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    battle = attack['battle']
    suit = attack['suit']
    battle = attack['battle']
    #targets = attack['target']
    suitTrack = getSuitTrack(attack)
    stomperTracks = Parallel()
    toonTracks = Parallel()
    #for t in targets:
        #toon = t['toon']
        #dmg = t['hp']
    if suit.getStyleDept() == 'Lawbot':
        stomper = loader.loadModel('phase_11/models/lawbotHQ/LB_square_stomper')
    else:
        stomper = loader.loadModel('phase_9/models/cogHQ/square_stomper')
    shaft = stomper.find('**/shaft')
    shaft.setScale(0.75, 15.0, 0.75)
    stomperPrepare = SoundInterval(base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_switch_depressed.ogg'), node=stomper)
    stomperPrepareTime = stomperPrepare.getDuration()
    stomperLift = SoundInterval(base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_stomper_raise.ogg'), node=stomper)
    stomperLiftTime = stomperLift.getDuration()
    smoke = loader.loadModel('phase_4/models/props/test_clouds')
    smoke.reparentTo(toon)
    smoke.setScale(0.5)
    smoke.setColor(0.8, 0.7, 0.5, 1)
    smoke.hide()
    smoke.setBillboardPointEye()
    toonPos = toon.getPos(battle)
    y = toonPos.getY()
    stomperPos = [Point3(toonPos.getX(), y, 20.0), toon.getHpr(battle)]
    stomperTrack = Sequence(
            Parallel(
                getPropAppearTrack(stomper, battle, stomperPos, 0.01, scaleUpPoint=0.0, scaleUpTime=1.0),
                stomperPrepare
            ),
            # LerpPosInterval(stomper, 0.25, Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ())),
            LerpPosInterval(stomper, 0.25, stomperPos,
            Parallel(
                SoundInterval(globalBattleSoundCache.getSound('CHQ_FACT_stomper_small.ogg'), node=stomper),
                Sequence(
                    Wait(1.0),
                    Parallel(
                        stomperLift,
                        LerpPosInterval(stomper, 3, toonPos.getX())
                    ),
                    LerpScaleInterval(stomper, 1.5, MovieUtil.PNT3_ZERO)
                ),
                Sequence(
                    Func(smoke.show),
                    Parallel(
                        LerpScaleInterval(smoke, 0.5, 1),
                        LerpColorScaleInterval(smoke, 0.5, Vec4(0.8, 0.7, 0.5, 0))
                    )
                )
            )
        ))
    stomperTracks.append(stomperTrack)
    if dmg != 0:
        toonTrack = Sequence(
                Func(toon.headsUp, battle, suit.getPos(battle)),
                Wait(stomperPrepareTime + 0.25),
                Parallel(
                    Func(toon.enterFlattened),
                    Func(toon.showHpText, -dmg, openEnded=0),
                    Func(__doDamage, toon, dmg, t['died'])
                ),
                Wait(2.5),
                Parallel(
                    Sequence(
                        Wait(0.5),
                        Func(toon.exitFlattened)
                    ),
                    SoundInterval(base.loader.loadSfx('phase_9/audio/sfx/toon_decompress.ogg'), node=toon),
                    Sequence(
                        ActorInterval(toon, 'jump'),
                        Func(toon.loop, 'neutral')
                    )
                )
            )
        #if t['died']:
            #toonTrack.append(Wait(5.0))
    else:
        toonTrack = Sequence(
                Func(toon.headsUp, battle, suit.getPos(battle)),
                getToonDodgeTrack(attack, t, 0.9, ['sidestep'], None)
            )
    toonTracks.append(toonTrack)
    return Parallel(suitTrack, stomperTracks, toonTracks)

def doWhirlwind(attack):
    suit = attack['suit']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    battle = attack['battle']
    pbpText = attack['playByPlayText']
    pbpDc = PlayByPlayText.PlayByPlayText()

    pbpDesc = pbpDc.getShowIntervalDesc('Your gags will be less effective!', 3.5)
    pbpTrack = pbpText.getShowIntervalCheat('Quality Control!', 3.5)
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                                       "Quality Control dictates that your gags will be less effective for 2 turns.",
                                                       CFSpeech | CFTimeout))
    suitTrack = getSuitTrack(attack)
    suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    cagePropTracks = Parallel()
    # for t in attack['target']:
    # toon = t['toon']
    # dmg = t['hp']
    cage = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_cfg_whirlwind')
    cagePosition = LerpHprInterval(cage, 0, Point3(180, 0, 0))
    # cage.setH(90)
    # cage.setPosHpr(0, 0, 0, 180, 0, 0)
    toonPos = toon.getPos(battle)
    y = toonPos.getY()
    if dmg == 0:
        y -= 5
    cagePos = [Point3(toonPos.getX(), y, 100.0), toon.getHpr(battle)]
    spinTrack = Sequence(LerpHprInterval(cage, 5, Point3(-7200, 0, 0)))
    cagePropTrack = Sequence(
        getPropAppearTrack(cage, battle, cagePos, .50, scaleUpPoint=Point3(2.0), scaleUpTime=1.0),
        Parallel(cagePosition),
        Parallel(
            cage.posInterval(0.5, Point3(toonPos.getX(), y, 0.1), blendType='easeIn'),
            SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/tt_s_ara_cfg_whirlwind.ogg'), duration=0.75, node=cage)
        ),
        Func(base.playSfx, base.loader.loadSfx('phase_5/audio/sfx/tt_s_ara_cfg_toonInWhirlwind.ogg'), node=cage), Parallel(spinTrack),
        LerpFunctionInterval(cage.setAlphaScale, fromData=.5, toData=0, duration=0.5),
        Func(MovieUtil.removeProp, cage)
    )
    cagePropTracks.append(cagePropTrack)
    damageAnims = [['slip-forward', 0.0001, 0.5]]
    damageAnims = []
    damageAnims.append(['duck',
                        0.01,
                        0.01,
                        1.1])
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    toonTrack = getToonTrack(attack, damageDelay=.9, splicedDamageAnims=damageAnims, dodgeDelay=0.91,
                             dodgeAnimNames=['sidestep'], showDamageExtraTime=2.1, showMissedExtraTime=1.0)
    toonSpinTrack = Sequence(Wait(0.9), LerpHprInterval(toon, 0.7, Point3(-10, 0, 0)),
                                 LerpHprInterval(toon, 0.5, Point3(-30, 0, 0)),
                                 LerpHprInterval(toon, 0.2, Point3(-60, 0, 0)),
                                 LerpHprInterval(toon, 0.7, Point3(-700, 0, 0)),
                                 LerpHprInterval(toon, 1.0, Point3(-1310, 0, 0)),
                             LerpHprInterval(toon, 2.0, Point3(-2620, 0, 0)),
                                 LerpHprInterval(toon, 0.4, toon.getHpr()), Wait(0.5))
    oldcolor = render.getColorScale()
    lightingTrack = Sequence(Wait(0), LerpColorScaleInterval(render, 0.5, (0.3, 0.3, 0.3, 1)),
                             LerpColorScaleInterval(render, 5.5, (0.9, 0.3, 0.3, 1)),
                             LerpColorScaleInterval(render, 1, (oldcolor)))
    return Parallel(suitTrack, cagePropTracks, lightingTrack, toonTrack, toonSpinTrack)

def doStomper(attack):
    suit = attack['suit']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    battle = attack['battle']
    suitTrack = getSuitTrack(attack)
    pbpText = attack['playByPlayText']
    pbpDc = PlayByPlayText.PlayByPlayText()

    pbpDesc = pbpDc.getShowIntervalDesc('Your gags will be less effective!', 3.5)
    pbpTrack = pbpText.getShowIntervalCheat('Quality Control!', 3.5)
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     "Quality Control dictates that your gags will be less effective for 2 turns.",
                                     CFSpeech | CFTimeout))
    suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    cagePropTracks = Parallel()
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    cage = loader.loadModel('phase_9/models/cogHQ/square_stomper')
    cagePosition = LerpHprInterval(cage, 0, Point3(0, -90, 0))
    shaft = cage.find('**/shaft')
    shaft.setScale(0.75, 15.0, 0.75)
    toonPos = toon.getPos(battle)
    y = toonPos.getY()
    if dmg == 0:
        y -= 5
    cagePos = [Point3(toonPos.getX(), y, 20.0), toon.getHpr(battle)]
    cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, 0.01, scaleUpPoint=Point3(1.4), scaleUpTime=0.1), Parallel(cagePosition),
            Parallel(
                cage.posInterval(0.5, Point3(toonPos.getX(), y, 0.01), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_stomper_large.ogg'), duration=1.0, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/toon_decompress.ogg'), node=cage),
            Wait(1.5),
            LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0),
            Func(MovieUtil.removeProp, cage)
        )
    cagePropTracks.append(cagePropTrack)
    damageAnims = [['slip-forward', 0.0001, 0.5]]
    toonTrack = getToonTrack(attack, damageDelay=0.5, splicedDamageAnims=damageAnims, dodgeDelay=0.75, dodgeAnimNames=[], splicedDodgeAnims=[], showDamageExtraTime=0.5)
    return Parallel(suitTrack, cagePropTracks, toonTrack)

def doCage(attack):
    suit = attack['suit']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    battle = attack['battle']
    suitTrack = getSuitTrack(attack)
    cagePropTracks = Parallel()
    pbpText = attack['playByPlayText']
    pbpDc = PlayByPlayText.PlayByPlayText()

    pbpDesc = pbpDc.getShowIntervalDesc('All of your gags are off-limits!', 3.5)
    pbpTrack = pbpText.getShowIntervalCheat('Quality Control!', 3.5)
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     "Quality Control that all of your gags are classified as defective.",
                                     CFSpeech | CFTimeout))
    suitTrack.append(Parallel(pbpDesc, pbpTrack, ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    cage = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_crg_toonCage')
    toonPos = toon.getPos(battle)
    y = toonPos.getY()
    if dmg == 0:
        y -= 5
    cagePos = [Point3(toonPos.getX(), y, 20.0), toon.getHpr(battle)]
    cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, 0.01, scaleUpPoint=Point3(0.4), scaleUpTime=1.0),
            Parallel(
                cage.posInterval(0.75, Point3(toonPos.getX(), y, 0.01), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/CHQ_SOS_cage_lower.ogg'), duration=0.75, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/CHQ_SOS_cage_land.ogg'), node=cage),
            Wait(1.5),
            LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0),
            Func(MovieUtil.removeProp, cage)
        )
    cagePropTracks.append(cagePropTrack)
    damageAnims = [['duck', 0.0001, 1.3]]
    toonTrack = getToonTrack(attack, damageDelay=1.5, splicedDamageAnims=damageAnims, dodgeDelay=1.75, dodgeAnimNames=[], splicedDodgeAnims=[], showDamageExtraTime=0.5)
    return Parallel(suitTrack, cagePropTracks, toonTrack)

def doCollectCall(attack):
    suit = attack['suit']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
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
    cagePos = [Point3(toonPos.getX(), x, 20.0), toon.getHpr(battle)]
    cagePos2 = [Point3(toonPos.getX(), x, 20.0), toon.getHpr(battle)]
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
    suitSpeechTrack = Sequence(Wait(6.0), Func(suit.setChatAbsolute, 'It appears that your phone bill is overdue, you will now be punished.', CFSpeech | CFTimeout))
    cagePropTracks.append(cagePropTrack)
    cagePropTracks.append(cagePropTrack2)
    suitTrack.append(Sequence(ActorInterval(suit, 'phone', duration=3.0), Wait(3.0), ActorInterval(suit, 'phone', startTime=3.0)))
    soundTrack1 = getSoundTrack('tt_s_ara_cmg_itemHitsFloor.ogg', delay=1.75, node=suit)
    soundTrack2 = getSoundTrack('SA_bash.ogg', delay=0, node=suit)
    soundTrack3 = getSoundTrack('ENC_cogfall_apart.ogg', delay=8.25, node=suit)
    soundTrack4 = getSoundTrack('telephone_ring.ogg', delay=2.0, node=suit)
    soundTrack = Parallel(soundTrack1, soundTrack2, soundTrack3, soundTrack4)
    toonTrack = Sequence(ActorInterval(toon, 'confused', duration=8.25), ActorInterval(toon, 'conked'))
    return Parallel(explodeTracks, suitTrack, cagePropTracks, toonTrack, soundTrack, suitSpeechTrack, explosionTrack)

def doDiceRoulette(attack):
    suit = attack['suit']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    battle = attack['battle']
    suitTrack = getSuitTrack(attack)
    cagePropTracks = Parallel()
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    cage = loader.loadModel('phase_5/models/props/cc_m_bat_prp_dice')
    toonPos = toon.getPos(battle)
    y = toonPos.getY()
    if dmg == 0:
        y -= 5
    cagePos = [Point3(toonPos.getX(), y, 20.0), toon.getHpr(battle)]
    cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, 0.01, scaleUpPoint=Point3(2.0), scaleUpTime=0.5),
            Parallel(
                cage.posInterval(0.75, Point3(toonPos.getX(), y, 2.01), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/incoming_whistleALT.ogg'), duration=0.75, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/CHQ_SOS_cage_land.ogg'), node=cage),
            Wait(1.5),
            LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0),
            Func(MovieUtil.removeProp, cage)
        )
    cagePropTracks.append(cagePropTrack)
    damageAnims = [['slip-forward', 0.0001, 1.3]]
    toonTrack = getToonTrack(attack, damageDelay=1.5, splicedDamageAnims=damageAnims, dodgeDelay=1.75, dodgeAnimNames=[], splicedDodgeAnims=[], showDamageExtraTime=0.5)
    cameraTrack = Sequence(
        LerpPosHprInterval(camera, duration=0.95, pos=Point3(0, -25, 10), hpr=Point3(0, 0, 0),
                           blendType='easeInOut'))
    return Parallel(suitTrack, cagePropTracks, toonTrack, cameraTrack)

def doAceInTheHole(attack):
    suit = attack['suit']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    battle = attack['battle']
    suitTrack = getSuitTrack(attack)
    cagePropTracks = Parallel()
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    cage = loader.loadModel('phase_5/models/props/cc_a_prp_bat_playcard')
    toonPos = toon.getPos(battle)
    y = toonPos.getY()
    if dmg == 0:
        y -= 5
    cagePos = [Point3(toonPos.getX(), y, 20.0), toon.getHpr(battle)]
    cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, 0.01, scaleUpPoint=Point3(2.0), scaleUpTime=0.5),
            Parallel(
                cage.posInterval(0.75, Point3(toonPos.getX(), y, 2.01), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/incoming_whistleALT.ogg'), duration=0.75, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/CHQ_SOS_cage_land.ogg'), node=cage),
            Wait(1.5),
            LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0),
            Func(MovieUtil.removeProp, cage)
        )
    cagePropTracks.append(cagePropTrack)
    damageAnims = [['slip-forward', 0.0001, 1.3]]
    toonTrack = getToonTrack(attack, damageDelay=1.5, splicedDamageAnims=damageAnims, dodgeDelay=1.75, dodgeAnimNames=[], splicedDodgeAnims=[], showDamageExtraTime=0.5)
    cameraTrack = Sequence(
        LerpPosHprInterval(camera, duration=0.95, pos=Point3(0, -25, 10), hpr=Point3(0, 0, 0),
                           blendType='easeInOut'))
    return Parallel(suitTrack, cagePropTracks, toonTrack, cameraTrack)

def doBar(attack):
    suit = attack['suit']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    battle = attack['battle']
    suitTrack = getSuitTrack(attack)
    cagePropTracks = Parallel()
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    cage = loader.loadModel('phase_10/models/cashbotHQ/GoldBar')
    cagePosition = LerpHprInterval(cage, 0, Point3(90, 0, 0))
    #cage.setH(90)
    #cage.setPosHpr(0, 0, 0, 180, 0, 0)
    toonPos = toon.getPos(battle)
    y = toonPos.getY()
    if dmg == 0:
        y -= 5
    cagePos = [Point3(toonPos.getX(), y, 30.0), toon.getHpr(battle)]
    cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, .90, scaleUpPoint=Point3(2.0), scaleUpTime=0.5), Parallel(cagePosition),
            Parallel(
                cage.posInterval(0.5, Point3(toonPos.getX(), y, 0.1), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/incoming_whistleALT.ogg'), duration=1.0, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_5/audio/sfx/tt_s_ara_cmg_itemHitsFloor.ogg'), node=cage),
            Wait(1.5),
            LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0),
            Func(MovieUtil.removeProp, cage)
        )
    cagePropTracks.append(cagePropTrack)
    damageAnims = [['slip-forward', 0.0001, 1.3]]
    toonTrack = getToonTrack(attack, damageDelay=1.5, splicedDamageAnims=damageAnims, dodgeDelay=1.75, dodgeAnimNames=[], splicedDodgeAnims=[], showDamageExtraTime=0.5)
    return Parallel(suitTrack, cagePropTracks, toonTrack)

def doConeOfShame(attack):
    suit = attack['suit']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    battle = attack['battle']
    suitTrack = getSuitTrack(attack)
    pbpText = attack['playByPlayText']
    pbpDc = PlayByPlayText.PlayByPlayText()

    pbpDesc = pbpDc.getShowIntervalDesc('Your gags will be less effective!', 3.5)
    pbpTrack = pbpText.getShowIntervalCheat('Quality Control!', 3.5)
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     "Quality Control dictates that your gags will be less effective for 2 turns.",
                                     CFSpeech | CFTimeout))
    suitTrack.append(Parallel(pbpDesc, pbpTrack, ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    cagePropTracks = Parallel()
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    cage = loader.loadModel('phase_3.5/models/props/barrier_cone')
    cagePosition = LerpHprInterval(cage, 0, Point3(90, 0, 0))
    #cage.setH(90)
    #cage.setPosHpr(0, 0, 0, 180, 0, 0)
    toonPos = toon.getPos(battle)
    y = toonPos.getY()
    if dmg == 0:
        y -= 5
    cagePos = [Point3(toonPos.getX(), y, 30.0), toon.getHpr(battle)]
    cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, .90, scaleUpPoint=Point3(.5), scaleUpTime=0.1),
            Parallel(
                cage.posInterval(0.5, Point3(toonPos.getX(), y, 0.1), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/incoming_whistleALT.ogg'), duration=1.0, node=cage)
            ), Wait(1.5),
            Func(base.playSfx, base.loader.loadSfx('phase_5/audio/sfx/tt_s_ara_cmg_itemHitsFloor.ogg'), node=cage),
            Wait(1.5),
            LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0),
            Func(MovieUtil.removeProp, cage)
        )
    cagePropTracks.append(cagePropTrack)
    damageAnims = [['slip-forward', 0.0001, 1.3]]
    toonTrack = getToonTrack(attack, damageDelay=0.5, splicedDamageAnims=damageAnims, dodgeDelay=1.75, dodgeAnimNames=[], splicedDodgeAnims=[], showDamageExtraTime=0.5)
    return Parallel(suitTrack, cagePropTracks, toonTrack)

def doBarMulti(attack):
    suit = attack['suit']
    targets = attack['target']
    target = attack['target']
    #toons = target['toon']
    #dmg = target['hp']
    battle = attack['battle']
    suitTrack = getSuitAnimTrack(attack)
    cagePropTracks = Parallel()
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    cage = loader.loadModel('phase_10/models/cashbotHQ/GoldBar')
    #cage.setHpr(90, 90, 90)
    #cage.setH(90)
    #cage.setPosHpr(0, 0, 0, 180, 0, 0)
    for t in attack['target']:
        toon = t['toon']
        toonPos = toon.getPos(battle)
        y = toonPos.getY()
        cagePos = [Point3(toonPos.getX(), y, 90.0), toon.getHpr(battle)]
        cagePosition = LerpHprInterval(cage, 0, Point3(90, 0, 0))
        cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, .90, scaleUpPoint=Point3(3.0), scaleUpTime=0.5), Parallel(cagePosition),
            Parallel(
                cage.posInterval(1.0, Point3(toonPos.getX(), y, 0.1), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/incoming_whistleALT.ogg'), duration=1.0, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_5/audio/sfx/tt_s_ara_cmg_itemHitsFloor.ogg'), node=cage),
            Wait(1.5),
            LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0),
            Func(MovieUtil.removeProp, cage)
        )
        cagePropTracks.append(cagePropTrack)
        damageAnims = [['slip-forward', 0.0001, 1.3]]
        toonTracks = getToonTracks(attack, damageDelay=2.5, splicedDamageAnims=damageAnims, dodgeDelay=1.75, dodgeAnimNames=[], splicedDodgeAnims=[], showDamageExtraTime=0.5)
        cameraTrack = Sequence(
            LerpPosHprInterval(camera, duration=0.95, pos=Point3(0, -25, 10), hpr=Point3(0, 0, 0),
                               blendType='easeInOut'))
        return Parallel(suitTrack, cagePropTracks, toonTracks, cameraTrack)

def doAfterShock(attack):
    suit = attack['suit']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    battle = attack['battle']
    suitTrack = getSuitTrack(attack)
    pbpText = attack['playByPlayText']
    pbpDc = PlayByPlayText.PlayByPlayText()

    pbpDesc = pbpDc.getShowIntervalDesc('Your gags will be less effective!', 3.5)
    pbpTrack = pbpText.getShowIntervalCheat('Quality Control!', 3.5)
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     "Quality Control dictates that your gags will be less effective for 2 turns.",
                                     CFSpeech | CFTimeout))
    suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    cagePropTracks = Parallel()
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    cage = loader.loadModel('phase_5/models/props/lightning')
    cagePosition = LerpHprInterval(cage, 0, Point3(180, 0, 0))
    #cage.setH(90)
    #cage.setPosHpr(0, 0, 0, 180, 0, 0)
    toonPos = toon.getPos(battle)
    y = toonPos.getY()
    if dmg == 0:
        y -= 5
    cagePos = [Point3(toonPos.getX(), y, 100.0), toon.getHpr(battle)]
    cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, .90, scaleUpPoint=Point3(4.0), scaleUpTime=1.0), Parallel(cagePosition),
            Parallel(
                cage.posInterval(0.1, Point3(toonPos.getX(), y, 0.1), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/AA_lightning.ogg'), duration=0.75, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_5/audio/sfx/AA_cog_shock.ogg'), node=cage),
            Wait(0.5),
            LerpFunctionInterval(cage.setAlphaScale, fromData=.5, toData=0, duration=0.5),
            Func(MovieUtil.removeProp, cage)
        )
    cagePropTracks.append(cagePropTrack)
    damageAnims = [['slip-forward', 0.0001, 0.5]]
    toonTrack = getToonTrack(attack, damageDelay=2.5, splicedDamageAnims=damageAnims, dodgeDelay=1.75, dodgeAnimNames=[], splicedDodgeAnims=[], showDamageExtraTime=0.5)
    oldcolor = render.getColorScale()
    lightingTrack = Sequence(Wait(0), LerpColorScaleInterval(render, 0.5, (0.3, 0.3, 0.3, 1)),
                             LerpColorScaleInterval(render, 3.5, (0.9, 0.3, 0.3, 1)),
                             LerpColorScaleInterval(render, 1, (oldcolor)))
    return Parallel(suitTrack, cagePropTracks, toonTrack, lightingTrack)

def doFreeCruise(attack):
    suit = attack['suit']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    battle = attack['battle']
    suitTrack = getSuitTrack(attack)
    cagePropTracks = Parallel()
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    cage = loader.loadModel('phase_5/models/props/ship')
    #cage.setHpr(90, 90, 90)
    #cage.setH(90)
    #cage.setPosHpr(0, 0, 0, 180, 0, 0)
    toonPos = toon.getPos(battle)
    y = toonPos.getY()
    if dmg == 0:
        y -= 5
    cagePos = [Point3(toonPos.getX(), y, 30.0), toon.getHpr(battle)]
    cagePosition = LerpHprInterval(cage, 0, Point3(90, 0, 0))
    cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, .90, scaleUpPoint=Point3(1.5), scaleUpTime=0.5), Parallel(cagePosition),
            Parallel(
                cage.posInterval(1.5, Point3(toonPos.getX(), y, 0.1), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/AA_drop_boat.ogg'), duration=3.0, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/AA_drop_boat_cog.ogg'), node=cage),
            Wait(1.5),
            LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0),
            Func(MovieUtil.removeProp, cage)
        )
    cagePropTracks.append(cagePropTrack)
    damageAnims = [['slip-forward', 0.0001, 1.3]]
    toonTrack = getToonTrack(attack, damageDelay=1.5, splicedDamageAnims=damageAnims, dodgeDelay=1.75, dodgeAnimNames=[], splicedDodgeAnims=[], showDamageExtraTime=0.5)
    cameraTrack = Sequence(
        LerpPosHprInterval(camera, duration=0.95, pos=Point3(0, -20, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'))
    return Parallel(suitTrack, cagePropTracks, toonTrack, cameraTrack)

def doFreeCruiseMulti(attack):
    suit = attack['suit']
    targets = attack['target']
    target = attack['target']
    #toons = target['toon']
    #dmg = target['hp']
    battle = attack['battle']
    suitTrack = getSuitAnimTrack(attack)
    cagePropTracks = Parallel()
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    cage = loader.loadModel('phase_5/models/props/ship')
    #cage.setHpr(90, 90, 90)
    #cage.setH(90)
    #cage.setPosHpr(0, 0, 0, 180, 0, 0)
    for t in attack['target']:
        toon = t['toon']
        toonPos = toon.getPos(battle)
        y = toonPos.getY()
        cagePos = [Point3(toonPos.getX(), y, 100.0), toon.getHpr(battle)]
        cagePosition = LerpHprInterval(cage, 0, Point3(90, 0, 0))
        cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, .90, scaleUpPoint=Point3(1.0), scaleUpTime=0.5), Parallel(cagePosition),
            Parallel(
                cage.posInterval(2.0, Point3(toonPos.getX(), y, 0.1), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/AA_drop_boat.ogg'), duration=2.0, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_5/audio/sfx/AA_drop_boat_cog.ogg'), node=cage),
            Wait(1.5),
            LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0),
            Func(MovieUtil.removeProp, cage)
        )
        cagePropTracks.append(cagePropTrack)
        damageAnims = [['slip-forward', 0.0001, 1.3]]
        toonTracks = getToonTracks(attack, damageDelay=3.5, splicedDamageAnims=damageAnims, dodgeDelay=1.75, dodgeAnimNames=[], splicedDodgeAnims=[], showDamageExtraTime=0.5)
        cameraTrack = Sequence(
            LerpPosHprInterval(camera, duration=0.95, pos=Point3(0, -25, 10), hpr=Point3(0, 0, 0),
                               blendType='easeInOut'))
        return Parallel(suitTrack, cagePropTracks, toonTracks, cameraTrack)

def doDetonate(attack, ind):
    manager = attack['suit']
    battle = attack['battle']
    toons = attack['target']
    targetSuit = battle.activeSuits[ind]

    managerTrack = Sequence(getSuitAnimTrack(attack), ActorInterval(manager, 'neutral%s' % ('-hurt' if float(manager.currHP) / float(manager.maxHP) <= 0.25 else '')))
    suitTrack = Sequence(Wait(1.0), Func(targetSuit.showHpText, "DETONATE!", 10), ActorInterval(targetSuit, 'soak', duration = 1.25), Sequence(MovieUtil.createSuitDeathTrack(targetSuit, None, battle, [], False)))
    toonTrack = getToonTracks(attack, 7.35, ['cringe'], 2.0, ['neutral'])
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_bash.ogg'), node=targetSuit))
    return Parallel(managerTrack, suitTrack, toonTrack, soundTrack)

def doUnionBust(attack, ind):
    manager = attack['suit']
    battle = attack['battle']
    #toons = attack['target']
    targetSuit = battle.activeSuits[ind]

    manager.setHealthForMe(int(manager.currHP + targetSuit.currHP))
    targetSuit.setHealthForMe(int(targetSuit.currHP - targetSuit.currHP))

    managerTrack = Sequence(getSuitAnimTrack(attack), ActorInterval(manager, 'neutral%s' % ('-hurt' if float(manager.currHP) / float(manager.maxHP) <= 0.25 else '')))
    managerTrack.append(Parallel(Sequence(Func(manager.setChatAbsolute,
                                                       "No unions will be formed under my watch, thank you for your contribution.",
                                                       CFSpeech | CFTimeout),
                                       Sequence(Wait(0.5)))))
    suitTrack = Sequence(Wait(1.0), Func(targetSuit.showHpText, "BUSTED!", 10), ActorInterval(targetSuit, 'flatten', duration = 1.25), Sequence(MovieUtil.createSuitCrashTrack(targetSuit)))
    #toonTrack = getToonTracks(attack, 7.35, ['cringe'], 2.0, ['neutral'])
    cagePropTracks = Parallel()
    # for t in attack['target']:
    # toon = t['toon']
    # dmg = t['hp']
    cage = loader.loadModel('phase_9/models/cogHQ/square_stomper')
    cagePosition = LerpHprInterval(cage, 0, Point3(0, -90, 0))
    shaft = cage.find('**/shaft')
    shaft.setScale(0.75, 15.0, 0.75)
    targetSuitPos = targetSuit.getPos(battle)
    y = targetSuitPos.getY()
    cagePos = [Point3(targetSuitPos.getX(), y, 20.0), targetSuit.getHpr(battle)]
    cagePropTrack = Sequence(
        getPropAppearTrack(cage, battle, cagePos, 0.01, scaleUpPoint=Point3(1.4), scaleUpTime=0.1),
        Parallel(cagePosition),
        Parallel(
            cage.posInterval(0.5, Point3(targetSuitPos.getX(), y, 0.01), blendType='easeIn'),
            SoundInterval(base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_stomper_large.ogg'), duration=1.0, node=cage)
        ),
        Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/toon_decompress.ogg'), node=cage),
        Wait(1.5),
        LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0),
        Func(MovieUtil.removeProp, cage)
    )
    cagePropTracks.append(cagePropTrack)
    cagePropTrack2 = Sequence(Wait(2), cagePropTrack)
    selfDamageTrack = Sequence(Wait(2), Func(targetSuit.showHpText, -targetSuit.currHP),
                               Func(targetSuit.updateHealthBar, 0))
    managerHealTrack = Sequence(Wait(2), Func(manager.showHpText, +targetSuit.currHP), Func(manager.updateHealthBar, 0))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_quake.ogg'), node=targetSuit))
    return Parallel(managerTrack, suitTrack, soundTrack, selfDamageTrack, managerHealTrack, cagePropTrack2)

def doHeadRoller(attack, ind):
    manager = attack['suit']
    battle = attack['battle']
    toons = attack['target']
    targetSuit = battle.activeSuits[ind]

    manager.setHealthForMe(int(manager.currHP + targetSuit.currHP))
    targetSuit.setHealthForMe(int(targetSuit.currHP - targetSuit.currHP))

    managerTrack = Sequence(getSuitAnimTrack(attack), Func(manager.loop, 'neutral%s' % ('-hurt' if float(manager.currHP) / float(manager.maxHP) <= 0.25 else '')))
    managerTrack.append(Parallel(Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                       "Someone isn't doing their part around here, your health is now mine.",
                                                       CFSpeech | CFTimeout),
                                       Sequence(Wait(0.5)))))
    suitTrack = Sequence(Wait(1.0), Func(targetSuit.showHpText, "SYPHONED!", 10), ActorInterval(targetSuit, 'soak', duration = 2.25), Sequence(MovieUtil.spawnHeadExplosion(targetSuit, battle)), Func(targetSuit.setChatAbsolute,
                                                       "Ouch.",
                                                       CFSpeech | CFTimeout), Wait(1.0), MovieUtil.createSuitHeadlessDeathTrack(targetSuit, battle))
    selfDamageTrack = Sequence(Wait(2), Func(targetSuit.showHpText, -targetSuit.currHP), Func(targetSuit.updateHealthBar, 0))
    managerHealTrack = Sequence(Wait(2), Func(manager.showHpText, +targetSuit.currHP), Func(manager.updateHealthBar, 0))
    #toonTrack = getToonTracks(attack, 7.35, ['cringe'], 2.0, ['neutral'])
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_bash.ogg'), node=targetSuit))
    return Parallel(managerTrack, suitTrack, soundTrack, selfDamageTrack, managerHealTrack)

def doHeadRollerHighRoller(attack, ind):
    manager = attack['suit']
    battle = attack['battle']
    toons = attack['target']
    targetSuit = battle.activeSuits[ind]

    manager.setHealthForMe(int(manager.currHP + targetSuit.currHP))
    targetSuit.setHealthForMe(int(targetSuit.currHP - targetSuit.currHP))

    managerTrack = Sequence(getSuitAnimTrack(attack), Func(manager.loop, 'neutral%s' % ('-hurt' if float(manager.currHP) / float(manager.maxHP) <= 0.25 else '')))
    managerTrack.append(Parallel(Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                       "WHAT A TWIFFT, BUTTERCUP BLUE!.",
                                                       CFSpeech | CFTimeout),
                                       Sequence(Wait(0.5)))))
    suitTrack = Sequence(Wait(1.0), Func(targetSuit.showHpText, "SYPHONED!", 10), ActorInterval(targetSuit, 'soak', duration = 2.25), Sequence(MovieUtil.spawnHeadExplosion(targetSuit, battle)), Func(targetSuit.setChatAbsolute,
                                                       "Ouch.",
                                                       CFSpeech | CFTimeout), Wait(1.0), MovieUtil.createSuitHeadlessDeathTrack(targetSuit, battle))
    selfDamageTrack = Sequence(Wait(2), Func(targetSuit.showHpText, -targetSuit.currHP), Func(targetSuit.updateHealthBar, 0))
    managerHealTrack = Sequence(Wait(2), Func(manager.showHpText, +targetSuit.currHP), Func(manager.updateHealthBar, 0))
    #toonTrack = getToonTracks(attack, 7.35, ['cringe'], 2.0, ['neutral'])
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_bash.ogg'), node=targetSuit))
    return Parallel(managerTrack, suitTrack, soundTrack, selfDamageTrack, managerHealTrack)

def doSpotlight(attack):
    suit = attack['suit']
    battle = attack['battle']
    healSound = SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'), node=suit)

    suitTracks = Parallel()
    for suit in battle.activeSuits:
        suitTrack = Sequence()
        suitTrack.append(Wait(3))
        suitTrack.append(Parallel(Sequence(Func(suit.setChatAbsolute, "I'll try my best!", CFSpeech | CFTimeout), ActorInterval(suit, 'dance'), Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))))
        suitTrack.append(Parallel(healSound, Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases), CFSpeech | CFTimeout)))
        suit.setHealthForMe(int(suit.currHP + 500))
        suitTrack.append(Func(suit.showHpText, 500))
        suitTrack.append(Func(suit.updateHealthBar, 0))
        suitTrack.append(Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
        #suitTrack.append(Parallel(Sequence(Wait(3), Func(suit.setChatAbsolute, "I'll try my best!", ActorInterval(suit, 'dance'), Wait(7), Func(suit.setChatAbsolute, 'Well adjusted.', CFSpeech | CFTimeout)))))
        suitTracks.append(suitTrack)
    suitTrack = Sequence(getSuitAnimTrack(attack), Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    soundTrack1 = getSoundTrack('SA_bash.ogg', node=suit)
    soundTrack2 = getSoundTrack('LB_camera_shutter_2.ogg', delay=1, node=suit)
    soundTrack3 = getSoundTrack('AA_heal_happydance.ogg', delay=3, node=suit)
    multiTrack = Parallel(soundTrack1, soundTrack2, soundTrack3)
    return Parallel(suitTrack, suitTracks, multiTrack)



def doRazzleDazzle(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    hitSuit = dmg > 0
    sign = globalPropPool.getProp('smile')
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect('Smile')
    suitTrack = getSuitTrack(attack)
    signPosPoints = [Point3(0.0, -0.42, -0.04), VBase3(105.715, 73.977, 65.932)]
    if hitSuit:
        hitPoint = lambda toon = toon: __toonFacePoint(toon)
    else:
        hitPoint = lambda particleEffect = particleEffect, toon = toon, suit = suit: __toonMissPoint(particleEffect, toon, parent=suit.getRightHand())
    signPropTrack = Sequence(Wait(0.5), Func(__showProp, sign, suit.getRightHand(), signPosPoints[0], signPosPoints[1]), LerpScaleInterval(sign, 0.5, Point3(1.39, 1.39, 1.39)), Wait(0.5), Func(battle.movie.needRestoreParticleEffect, particleEffect), Func(particleEffect.start, sign), Func(particleEffect.wrtReparentTo, render), LerpPosInterval(particleEffect, 2.0, pos=hitPoint), Func(particleEffect.cleanup), Func(battle.movie.clearRestoreParticleEffect, particleEffect))
    signPropAnimTrack = ActorInterval(sign, 'smile', duration=4, startTime=0)
    toonTrack = getToonTrack(attack, 2.6, ['cringe'], 1.9, ['sidestep'])
    soundTrack = getSoundTrack('SA_razzle_dazzle.ogg', delay=1.6, node=suit)
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
    costsTrack = Parallel(pbpDesc2, pbpTrack2)
    suitTrack.append(Parallel(Sequence(Wait(0.1), Func(suit.setChatAbsolute,
                                                       'Quality Control dictates that all Level 7 and 8 gags are now classified as defective.',
                                                       CFSpeech | CFTimeout))))
    suitTrack.append(ceaseTrack)
    suitTrack.append(Func(suit.loop, 'neutral%s' % (
        '-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
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
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, damageAnimNames=['slip-forward'], dodgeDelay=0.91,
                               splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.0)
    synergySoundTrack = Sequence(Wait(0.9), SoundInterval(globalBattleSoundCache.getSound('SA_synergy.ogg'), node=suit))
    if hitAtleastOneToon > 0:
        soundTrack1 = Sequence(Wait(2.0),
                               SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=suit))
        soundTrack2 = Sequence(Wait(4.0),
                               SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
        multiTrack = Parallel(soundTrack1, soundTrack2)
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, toonTracks, multiTrack)
    else:
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, toonTracks)

def doUnionDues(attack):
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

    pbpDesc = pbpDc.getShowIntervalDesc('Level 7 and 8 Gags are now off-limits!', 3.5)
    pbpTrack = pbpText.getShowIntervalCheat('Quality Control!', 3.5)
    pbpDesc2 = pbpDc.getShowIntervalDesc('The dues are racking up!', 3.5)
    pbpTrack2 = pbpText.getShowIntervalCheat('Union Dues!', 3.5)
    ceaseTrack = ActorInterval(suit, 'cease')
    particleEffect = BattleParticles.createParticleEffect('Synergy')
    waterfallEffect = BattleParticles.createParticleEffect(file='synergyWaterfall')
    suitTrack = Sequence(getSuitAnimTrack(attack))
    costsTrack = Parallel(pbpDesc2, pbpTrack2)
    suitTrack.append(Parallel(Sequence(Wait(0.1), Func(suit.setChatAbsolute,
                                                       'Quality Control dictates that all Level 7 and 8 gags are now classified as defective.',
                                                       CFSpeech | CFTimeout))))
    suitTrack.append(ceaseTrack)
    suitTrack.append(Func(suit.loop, 'neutral%s' % (
        '-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
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
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, damageAnimNames=['slip-forward'], dodgeDelay=0.91,
                               splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.0)
    synergySoundTrack = Sequence(Wait(0.9), SoundInterval(globalBattleSoundCache.getSound('SA_synergy.ogg'), node=suit))
    if hitAtleastOneToon > 0:
        soundTrack1 = Sequence(Wait(2.0),
                               SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=suit))
        soundTrack2 = Sequence(Wait(4.0),
                               SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
        multiTrack = Parallel(soundTrack1, soundTrack2)
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, toonTracks, multiTrack)
    else:
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, toonTracks)


def doCourtCosts(attack):
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

    pbpDesc = pbpDc.getShowIntervalDesc('Level 6 and 8 Gags are now off-limits!', 3.5)
    pbpTrack = pbpText.getShowIntervalCheat('Court Record!', 3.5)
    pbpDesc2 = pbpDc.getShowIntervalDesc('The fees are racking up!', 3.5)
    pbpTrack2 = pbpText.getShowIntervalCheat('Court Costs!', 3.5)
    ceaseTrack = ActorInterval(suit, 'cease')
    particleEffect = BattleParticles.createParticleEffect('Synergy')
    waterfallEffect = BattleParticles.createParticleEffect(file='synergyWaterfall')
    suitTrack = Sequence(getSuitAnimTrack(attack))
    costsTrack = Parallel(pbpDesc2, pbpTrack2)
    suitTrack.append(Parallel(Sequence(Wait(0.1), Func(suit.setChatAbsolute,
                                   'Any Level 6 and 8 Gags Toons use can and will be held against them in a court of law.', CFSpeech | CFTimeout))))
    suitTrack.append(ceaseTrack)
    suitTrack.append(Func(suit.loop, 'neutral%s' % (
        '-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
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
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, damageAnimNames=['slip-forward'], dodgeDelay=0.91,
                               splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.0)
    synergySoundTrack = Sequence(Wait(0.9), SoundInterval(globalBattleSoundCache.getSound('SA_synergy.ogg'), node=suit))
    if hitAtleastOneToon > 0:
        soundTrack1 = Sequence(Wait(2.0), SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=suit))
        soundTrack2 = Sequence(Wait(4.0),
                               SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
        multiTrack = Parallel(soundTrack1, soundTrack2)
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, toonTracks, multiTrack)
    else:
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, toonTracks)

def doCollectCallFees(attack):
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

    pbpDesc = pbpDc.getShowIntervalDesc('Level 6 and 8 Gags are now off-limits!', 3.5)
    pbpTrack = pbpText.getShowIntervalCheat('Quality Control!', 3.5)
    pbpDesc2 = pbpDc.getShowIntervalDesc('The fees are racking up!', 3.5)
    pbpTrack2 = pbpText.getShowIntervalCheat('Collect Call Costs!', 3.5)
    ceaseTrack = ActorInterval(suit, 'cease')
    particleEffect = BattleParticles.createParticleEffect('Synergy')
    waterfallEffect = BattleParticles.createParticleEffect(file='synergyWaterfall')
    suitTrack = Sequence(getSuitAnimTrack(attack))
    costsTrack = Parallel(pbpDesc2, pbpTrack2)
    suitTrack.append(Parallel(Sequence(Wait(0.1), Func(suit.setChatAbsolute,
                                                       'Quality Control dictates that all Level 6 and 8 gags are now classified as defective.',
                                                       CFSpeech | CFTimeout))))
    suitTrack.append(ceaseTrack)
    suitTrack.append(Func(suit.loop, 'neutral%s' % (
        '-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
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
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, damageAnimNames=['slip-forward'], dodgeDelay=0.91,
                               splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.0)
    synergySoundTrack = Sequence(Wait(0.9), SoundInterval(globalBattleSoundCache.getSound('SA_synergy.ogg'), node=suit))
    if hitAtleastOneToon > 0:
        soundTrack1 = Sequence(Wait(2.0),
                               SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=suit))
        soundTrack2 = Sequence(Wait(4.0),
                               SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
        multiTrack = Parallel(soundTrack1, soundTrack2)
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, toonTracks, multiTrack)
    else:
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, toonTracks)


def doFreezingRain(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.7
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1

    sprayEffect = BattleParticles.createParticleEffect('WaterSpray')
    suitName = suit.getStyleName()
    sprayEffect.setPos(Point3(-5.2, 10.6, 6.7))
    waterfallEffect = BattleParticles.createParticleEffect(file='snowWaterfall')
    suitTrack = getSuitAnimTrack(attack)
    pbpText = attack['playByPlayText']
    pbpDc = PlayByPlayText.PlayByPlayText()

    pbpDesc = pbpDc.getShowIntervalDesc('Your gags will be half as effective!', 3.5)
    pbpTrack = pbpText.getShowIntervalCheat('Quality Control!', 3.5)
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     "Quality Control notices that you have started to slow down, your gags will be less as effective.",
                                     CFSpeech | CFTimeout))
    suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    suitTrack.append(Sequence(ActorInterval(attack['suit'], 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))))
    partTrack = getPartTrack(sprayEffect, 1.0, 1.9, [sprayEffect, suit, 0])
    waterfallTrack = getPartTrack(waterfallEffect, 0.8, 1.9, [waterfallEffect, suit, 0])
    sprayTrack = getPartTrack(sprayEffect, 1.0, 1.9, [sprayEffect, suit, 0])
    damageAnims = [['cringe']]
    dodgeAnims = []
    dodgeAnims.append(['jump',
                       0.01,
                       0,
                       0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.3, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, damageAnimNames=['cringe'], dodgeDelay=0.91,
                               splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.0)
    synergySoundTrack = Sequence(Wait(0.9), SoundInterval(globalBattleSoundCache.getSound('SA_freeze.ogg')))
    if hitAtleastOneToon > 0:
        soundTrack1 = Sequence(Wait(1), SoundInterval(globalBattleSoundCache.getSound('SA_freeze.ogg'), node=suit))
        return Parallel(suitTrack, partTrack, sprayTrack, waterfallTrack, synergySoundTrack, toonTracks, soundTrack1)
    else:
        return Parallel(suitTrack, partTrack, sprayTrack, waterfallTrack, synergySoundTrack, toonTracks)


def doHeatWave(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.7
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1

    particleEffect = BattleParticles.createParticleEffect(file='heatwave')
    waterfallEffect = BattleParticles.createParticleEffect(file='heatwaveWaterfall')
    suitTrack = Sequence(getSuitAnimTrack(attack))
    pbpText = attack['playByPlayText']
    pbpDc = PlayByPlayText.PlayByPlayText()

    pbpDesc = pbpDc.getShowIntervalDesc('Level 6 and 7 gags are off-limits!', 3.5)
    pbpTrack = pbpText.getShowIntervalCheat('Quality Control!', 3.5)
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     "Quality Control dictates that all Level 6 and 7 gags are now classified as defective.",
                                     CFSpeech | CFTimeout))
    suitTrack.append(Wait(3.0))
    suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    suitTrack.append(Sequence(ActorInterval(attack['suit'], 'neutral%s' % (
        '-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))))
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
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, damageAnimNames=['slip-forward'], dodgeDelay=0.91,
                               splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.0)
    soundTrack1 = Sequence(Wait(1), SoundInterval(globalBattleSoundCache.getSound('SA_hot_air.ogg'), node=suit))
    soundTrack2 = Sequence(Wait(0), SoundInterval(globalBattleSoundCache.getSound('SA_bash.ogg'), node=suit))
    multiTrack = Parallel(soundTrack1, soundTrack2)
    if hitAtleastOneToon > 0:
        return Parallel(suitTrack, partTrack, waterfallTrack, toonTracks, multiTrack)
    else:
        return Parallel(suitTrack, partTrack, waterfallTrack, toonTracks, multiTrack)


def doConDuckTion(attack):
    suit = attack['suit']
    battle = attack['battle']
    propDelay = 0.6
    throwDelay = 2.17
    suitTrack = getSuitAnimTrack(attack)
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

    damageAnims = [['cringe', 0.01, 0.14, 0.21],
                   ['cringe', 0.01, 0.14, 0.13],
                   ['cringe', 0.01, 0.43]]
    toonTracks = getToonTracks(attack, damageDelay=4.2, splicedDamageAnims=damageAnims, dodgeDelay=2.8,
                               dodgeAnimNames=['sidestep'], showMissedExtraTime=1.1)
    soundTrack = getSoundTrack('cc_s_sfx_ene_hroller_conducktion.ogg', delay=throwDelay, node=suit)
    return Parallel(suitTrack, allDuckTracks, toonTracks, soundTrack)

def doTvBlast(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target['hp']
    toon = target['toon']
    hips = toon.getHipsParts()
    propDelay = 0.8
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'c':
        suitDelay = 1.13
        dodgeDelay = 3.1
    else:
        suitDelay = 1.83
        dodgeDelay = 3.6
    throwDuration = 1.5
    tv = globalPropPool.getProp('modeltv')
    scale = 1.1
    torso = toon.style.torso
    torso = torso[0]
    if torso == 's':
        scaleUpPoint = Point3(scale * 1.23, scale * 1.23, scale * 1.23)
    elif torso == 'm':
        scaleUpPoint = Point3(scale * 1.23, scale * 1.23, scale * 1.23)
    elif torso == 'l':
        scaleUpPoint = Point3(scale * 1.23, scale * 1.23, scale * 1.23)
    tvHpr = VBase3(-173.47, 0, 0)
    suitTrack = getSuitTrack(attack)
    posPoints = [Point3(-0.14, 0.15, 0.08), VBase3(-10.584, 11.945, -161.684)]
    throwTrack = Sequence(getPropAppearTrack(tv, suit.getRightHand(), posPoints, propDelay, Point3(6, 6, 6), scaleUpTime=0.5))
    propDelay = propDelay + 0.5
    throwTrack.append(Wait(suitDelay))
    hitPoint = toon.getPos(battle)
    hitPoint.setX(hitPoint.getX() + 1.1)
    hitPoint.setY(hitPoint.getY() - 0.5)
    hitPoint.setZ(hitPoint.getZ() + toon.height + 1.1)
    throwTrack.append(Func(battle.movie.needRestoreRenderProp, tv))
    throwTrack.append(getThrowTrack(tv, hitPoint, duration=throwDuration, parent=battle))
    if dmg > 0:
        tv2 = MovieUtil.copyProp(tv)
        hips1 = hips.getPath(2)
        hips2 = hips.getPath(1)
        tv2Point = Point3(hitPoint.getX(), hitPoint.getY() + 6.4, hitPoint.getZ())
        tv2.setPos(tv2Point)
        tv2.setScale(scaleUpPoint)
        tv2.setHpr(tvHpr)
        throwTrack.append(Func(battle.movie.needRestoreHips))
        throwTrack.append(Func(tv.wrtReparentTo, hips1))
        throwTrack.append(Func(tv2.reparentTo, hips2))
        throwTrack.append(Wait(2.4))
        throwTrack.append(Func(MovieUtil.removeProp, tv2))
        throwTrack.append(Func(battle.movie.clearRestoreHips))
        scaleTrack = Sequence(Wait(propDelay + suitDelay), LerpScaleInterval(tv, throwDuration, scaleUpPoint))
        hprTrack = Sequence(Wait(propDelay + suitDelay), LerpHprInterval(tv, throwDuration, tvHpr))
        soundTrack = Sequence(Wait(2.6), SoundInterval(globalBattleSoundCache.getSound('SA_TV_pie_throw.ogg'), node=suit), Wait(2.4),SoundInterval(globalBattleSoundCache.getSound('SA_TV_crash.ogg'), node=suit))
    else:
        land = toon.getPos(battle)
        land.setZ(land.getZ() + 0.7)
        bouncePoint1 = Point3(land.getX(), land.getY() - 1.5, land.getZ() + 2.5)
        bouncePoint2 = Point3(land.getX(), land.getY() - 2.1, land.getZ() - 0.2)
        bouncePoint3 = Point3(land.getX(), land.getY() - 3.1, land.getZ() + 1.5)
        bouncePoint4 = Point3(land.getX(), land.getY() - 4.1, land.getZ() + 0.3)
        throwTrack.append(LerpPosInterval(tv, 0.4, land))
        throwTrack.append(LerpPosInterval(tv, 0.4, bouncePoint1))
        throwTrack.append(LerpPosInterval(tv, 0.3, bouncePoint2))
        throwTrack.append(LerpPosInterval(tv, 0.3, bouncePoint3))
        throwTrack.append(LerpPosInterval(tv, 0.3, bouncePoint4))
        throwTrack.append(Wait(1.1))
        throwTrack.append(LerpScaleInterval(tv, 0.3, MovieUtil.PNT3_NEARZERO))
        scaleTrack = Sequence(Wait(propDelay + suitDelay), LerpScaleInterval(tv, throwDuration, Point3(1.8, 1.8, 1.8)))
        hprTrack = Sequence(Wait(propDelay + suitDelay), LerpHprInterval(tv, throwDuration, tvHpr), Wait(0.4), LerpHprInterval(tv, 0.4, Point3(83.27, 0, 0)), LerpHprInterval(tv, 0.3, Point3(95.24, 0, 0)), LerpHprInterval(tv, 0.2, Point3(-96.34, 0, 0)))
        soundTrack = getSoundTrack('SA_TV_pie_throw.ogg', delay=2.6, node=suit)
    tvTrack = Sequence(Parallel(throwTrack, scaleTrack, hprTrack), Func(MovieUtil.removeProp, tv), Func(battle.movie.clearRenderProp, tv))
    damageAnims = [['think',
      propDelay + suitDelay + throwDuration,
      0.01,
      0.7], ['cringe', 0.01, 0.45]]
    toonTrack = getToonTrack(attack, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['shrug'], showDamageExtraTime=propDelay + suitDelay + 2.4)
    return Parallel(suitTrack, toonTrack, tvTrack, soundTrack)

def doOilRain(attack):
    suit = attack['suit']
    battle = attack['battle']
    BattleParticles.loadParticles()
    partDelay = 0.2
    damageDelay = 3.5
    dodgeDelay = 2.45
    suitTrack = getSuitAnimTrack(attack)
    pbpText = attack['playByPlayText']
    pbpDc = PlayByPlayText.PlayByPlayText()

    pbpDesc = pbpDc.getShowIntervalDesc('Offensive gags will be less effective!', 3.5)
    pbpTrack = pbpText.getShowIntervalCheat('Quality Control!', 3.5)
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     "Quality Control dictates that Offensive gags will be less effective.",
                                     CFSpeech | CFTimeout))
    suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    suitTrack.append(Sequence(ActorInterval(attack['suit'], 'neutral%s' % (
        '-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))))
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
        effectColor = Vec4(0.00, 1.00, 0.00, 1.00) if attack['id'] == ACID_RAIN else Vec4(0.00, 0.00, 0.00, 1.00)
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
            Wait(1.1),
            LerpPosInterval(cloud, 1, pos=targetPoint),
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
            puddle.setColor(Vec4(0.0, 1.0, 0.0, 1) if attack['id'] == ACID_RAIN else Vec4(0.0, 0.0, 0.0, 1))
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
    return Parallel(suitTrack, toonTracks, cloudPropTracks, soundTrack1, puddleTracks)

def doRolled(attack):
    suit = attack['suit']
    battle = attack['battle']
    BattleParticles.loadParticles()
    partDelay = 0.2
    damageDelay = 1.5
    dodgeDelay = 1.45
    suitTrack = getSuitAnimTrack(attack)
    suitTrack.append(doWheelSpin2(attack))
    initialCloudHeight = suit.height + 3
    cloudPosPoints = [Point3(0, 3, initialCloudHeight), VBase3(180, 0, 0)]
    cloudPropTracks = Parallel()
    puddleTracks = Parallel()
    damageAnims = []
    damageAnims.append(['duck',
                        0.01,
                        0.01,
                        1.1])
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    for t in attack['target']:
        toon = t['toon']
        sprayEffect = BattleParticles.createParticleEffect(file='spinSpray')
        sprayTrack = getPartTrack(sprayEffect, 1.0, 1.9, [sprayEffect, suit, 0])
        spinEffect1 = BattleParticles.createParticleEffect(file='spinEffect')
        spinEffect2 = BattleParticles.createParticleEffect(file='spinEffect')
        spinEffect3 = BattleParticles.createParticleEffect(file='spinEffect')
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
        #cloud = globalPropPool.getProp('stormcloud')
        targetPoint = __toonFacePoint(toon)
        targetPoint.setZ(targetPoint[2] + 3)
        cloudPropTrack = Parallel(Sequence(getPartTrack(spinEffect1, 2.1, 3.9, [spinEffect1, battle, 0]), Wait(.1),
                Sequence(getPartTrack(spinEffect2, 2.1, 3.9, [spinEffect2, battle, 0]), Wait(.1),
                Sequence(getPartTrack(spinEffect3, 2.1, 3.9, [spinEffect3, battle, 0])))))
        cloudPropTracks.append(cloudPropTrack)
        cloudPropTracks.append(sprayTrack)
        toonSpinTrack = Sequence(Wait(damageDelay + 0.9), LerpHprInterval(toon, 0.7, Point3(-10, 0, 0)),
                                 LerpHprInterval(toon, 0.5, Point3(-30, 0, 0)),
                                 LerpHprInterval(toon, 0.2, Point3(-60, 0, 0)),
                                 LerpHprInterval(toon, 0.7, Point3(-700, 0, 0)),
                                 LerpHprInterval(toon, 1.0, Point3(-1310, 0, 0)),
                                 LerpHprInterval(toon, 0.4, toon.getHpr()), Wait(0.5))
        toonTracks.append(toonSpinTrack)
    soundTrack = getSoundTrack('tt_s_ara_cfg_toonInWhirlwind.ogg', delay=2.0, node=suit)
    return Parallel(suitTrack, toonTracks, soundTrack)

def doHeavyRain2(attack):
    suit = attack['suit']
    battle = attack['battle']
    BattleParticles.loadParticles()
    partDelay = 0.2
    damageDelay = 3.5
    dodgeDelay = 2.45
    suitTrack = getSuitAnimTrack(attack)
    pbpText = attack['playByPlayText']
    pbpDc = PlayByPlayText.PlayByPlayText()

    pbpDesc = pbpDc.getShowIntervalDesc('Level 6 and 7 gags are off-limits!', 3.5)
    pbpTrack = pbpText.getShowIntervalCheat('Quality Control!', 3.5)
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     "Quality Control dictates that all Level 6 and 7 gags are now classified as defective.",
                                     CFSpeech | CFTimeout))
    suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    initialCloudHeight = suit.height + 3
    cloudPosPoints = [Point3(0, 3, initialCloudHeight), VBase3(180, 0, 0)]
    cloudPropTracks = Parallel()
    puddleTracks = Parallel()
    damageAnims = [['melt'], ['jump', 1.5, 0.4]]
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    for t in attack['target']:
        toon = t['toon']
        rainEffect = BattleParticles.createParticleEffect(file='liquidate2')
        rainEffect2 = BattleParticles.createParticleEffect(file='liquidate2')
        rainEffect3 = BattleParticles.createParticleEffect(file='liquidate2')
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
            Wait(1.1),
            LerpPosInterval(cloud, 1, pos=targetPoint),
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
    #animTrack = Sequence(Wait(2), Func(suit.play, 'cease'))
    soundTrack1 = getSoundTrack('SA_liquidate.ogg', delay=2.0, node=suit)
    soundTrack = Parallel(soundTrack1)
    return Parallel(suitTrack, toonTracks, cloudPropTracks, soundTrack, puddleTracks)

def doEmbezzle(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target['hp']
    bill = loader.loadModel('phase_3.5/models/props/jellybean4')
    bill.setH(0)
    bill.setColor(1,0.9,0)
    glow = loader.loadModel("phase_3.5/models/props/glow.bam")
    glow.reparentTo(bill)
    glow.setScale(0.5)
    glow.setPos(0,0,0)
    glow.setColorScale(Vec4(1, 0.9, 0, 0.3))
    suitTrack = getSuitTrack(attack)
    billPosPoints = [Point3(-0.01, 0.45, -0.25), VBase3(136.424, -46.434, -129.712)]
    billPropTrack = getPropTrack(bill, suit.getRightHand(), billPosPoints, 0.6, 0.55, scaleUpPoint=Point3(5.0, 5.0, 5.0))
    toonTrack = getToonTrack(attack, 0.6, ['cringe'], 0.01, ['sidestep'])
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
    partTrack = getPartTrack(particleEffect, 1.0, 1.9, [particleEffect, suit, 0])
    waterfallTrack = getPartTrack(waterfallEffect, 0.8, 1.9, [waterfallEffect, suit, 0])
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


def doWhitePowder(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTracks = Parallel()
    pbpText = attack['playByPlayText']
    pbpDc = PlayByPlayText.PlayByPlayText()

    pbpDesc = pbpDc.getShowIntervalDesc('The Litigator removes all negative effects from\nthe cogs!', 3.5)
    pbpTrack = pbpText.getShowIntervalCheat('Bayou Bellow!', 3.5)
    for suit in battle.activeSuits:
        suitTrack = Sequence()
        suitTrack.append(Wait(5.0))
        resetTrack = getResetTrack(suit, battle)
        suitTrack.append(Func(battle.unlureSuit, suit))
        suit.setHealthForMe(int(suit.currHP + 100))
        suitTrack.append(Func(suit.showHpText, 100))
        suitTrack.append(Func(suit.updateHealthBar, 0))
        suitTrack.append(resetTrack)
        suitTrack.append(
            Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitBellowPhrases), CFSpeech | CFTimeout))
        suitTrack.append(Wait(2.0))
        suitTrack.append(Func(suit.showHpTextRed, "BELLOW!", 5))
        suitTracks.append(MovieUtil.createSuitBellowInterval(suit))
        suitTracks.append(Wait(5.0))
        suitTracks.append(suitTrack)
        suitTracks.append(Func(suit.loop,  'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    soundTrack = getSoundTrack('SA_bellow.ogg', delay=0.1, node=suit)
    healSound = Sequence(Wait(5.5), SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'), node=suit))
    return Parallel(suitTracks, healSound, soundTrack)

def doMobMentality(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTracks = Parallel()
    for suit in battle.activeSuits:
        suitTrack = getSuitTrack(attack)
        suitTrack.append(Func(suit.play, 'mob-mentality'))
        resetTrack = getResetTrack(suit, battle)
        suitTrack.append(Wait(3.0))
        suitTrack.append(Func(suit.play,  'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
        for headPart in suit.animatedHeadParts:
            suitTrack.append(Func(headPart.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
        suit.setHealthForMe(int(suit.currHP + 100))
        suitTrack.append(Func(suit.showHpText, 100))
        suitTrack.append(Func(suit.updateHealthBar, 0))
        suitTrack.append(resetTrack)
        suitTrack.append(
            Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases), CFSpeech | CFTimeout))
        suitTrack.append(Func(battle.unlureSuit, suit))
        suitTracks.append(suitTrack)
        suitTracks.append(Func(suit.loop,  'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    soundTrack = getSoundTrack('SA_mob_mentality.ogg', node=suit)
    healSound = Sequence(Wait(6.5), SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'), node=suit))
    return Parallel(suitTracks, healSound, soundTrack)

def doGoodMorningToontown(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTracks = Parallel()
    for suit in battle.activeSuits:
        suitTrack = getSuitTrack(attack)
        resetTrack = getResetTrack(suit, battle)
        suitTrack.append(resetTrack)
        suitTrack.append(Func(battle.unlureSuit, suit))
        suitTracks.append(suitTrack)
        suitTracks.append(Func(suit.loop,  'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
        for headPart in suit.animatedHeadParts:
            suitTracks.append(Func(headPart.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    soundTrack = getSoundTrack('cc_s_dlg_ene_hroller_good_morning_clash_general.ogg', node=suit)
    return Parallel(suitTracks, soundTrack)

def doCeaseAndDesist(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTracks = Parallel()
    for suit in battle.activeSuits:
        suitTrack = getSuitTrack(attack)
        resetTrack = getResetTrack(suit, battle)
        suitTrack.append(Func(battle.unlureSuit, suit))
        for headPart in suit.animatedHeadParts:
            suitTrack.append(Func(headPart.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
        suitTrack.append(resetTrack)
        suitTracks.append(suitTrack)
        suitTracks.append(Func(suit.loop,  'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    soundTrack = getSoundTrack('SA_insurance.ogg', node=suit)
    return Parallel(suitTracks, soundTrack)

def doHypnoEyes(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    damageDelay = 1.7
    sprayEffect = BattleParticles.createParticleEffect(file='organizeSpray')
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
    suitTrack = getSuitTrack(attack)
    sprayTrack = getPartTrack(sprayEffect, 1.0, 1.9, [sprayEffect, suit, 0])
    spinTrack1 = getPartTrack(spinEffect1, 2.1, 3.9, [spinEffect1, battle, 0])
    spinTrack2 = getPartTrack(spinEffect2, 2.1, 3.9, [spinEffect2, battle, 0])
    spinTrack3 = getPartTrack(spinEffect3, 2.1, 3.9, [spinEffect3, battle, 0])
    damageAnims = []
    damageAnims.append(['duck',
     0.01,
     0.01,
     1.1])
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.91, dodgeAnimNames=['sidestep'], showDamageExtraTime=2.1, showMissedExtraTime=1.0)
    soundTrack = getSoundTrack('TL_hypnotize.ogg', delay=0.91, node=suit)
    if dmg > 0:
        toonSpinTrack = Sequence(Wait(damageDelay + 0.9), LerpHprInterval(toon, 0.7, Point3(-10, 0, 0)), LerpHprInterval(toon, 0.5, Point3(-30, 0, 0)), LerpHprInterval(toon, 0.2, Point3(-60, 0, 0)), LerpHprInterval(toon, 0.7, Point3(-700, 0, 0)), LerpHprInterval(toon, 1.0, Point3(-1310, 0, 0)), LerpHprInterval(toon, 0.4, toon.getHpr()), Wait(0.5))
        return Parallel(suitTrack, sprayTrack, toonTrack, soundTrack, toonSpinTrack, spinTrack1, spinTrack2, spinTrack3)
    else:
        return Parallel(suitTrack, sprayTrack, toonTrack, soundTrack)

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
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.01, dodgeAnimNames=['duck'], showDamageExtraTime=2.1, showMissedExtraTime=2.0)
    if dmg > 0:
        return Parallel(suitTrack, partTrack, toonTrack, headTracks, chestTracks)
    else:
        return Parallel(suitTrack, partTrack, toonTrack)


def doBlast(attack):
    suit = attack['suit']
    battle = attack['battle']
    leftKnives = []
    rightKnives = []
    explode = []
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    for i in xrange(0, 3):
        leftKnives.append(globalPropPool.getProp('dagger'))
        rightKnives.append(globalPropPool.getProp('dagger'))
        explode.append(globalPropPool.getProp('explosion'))
        cameraTrack = Sequence(LerpPosHprInterval(camera, duration=0.2, pos=Point3(8, 11, 5), hpr=Point3(150, 0, 0),
                                                  blendType='easeInOut'))

    suitTrack = getSuitAnimTrack(attack)
    suitName = suit.getStyleName()
    leftPosPoints = [Point3(0.4, 10, 3.2), MovieUtil.PNT3_ZERO]
    rightPosPoints = [Point3(-0.4, 10, 3.2), MovieUtil.PNT3_ZERO]
    explodePosPoints = [Point3(0, 10, 1), MovieUtil.PNT3_ZERO]
    leftPosPoints1 = [Point3(0.4, 10, 3.2), MovieUtil.PNT3_ZERO]
    rightPosPoints1 = [Point3(-0.4, 10, 3.2), MovieUtil.PNT3_ZERO]
    explodePosPoints1 = [Point3(0, 10, 1), MovieUtil.PNT3_ZERO]
    explodeHprPoints = [Point3(180, 0, 0), MovieUtil.PNT3_ZERO]
    explodeHprPoints1 = [Point3(180, 0, 0), MovieUtil.PNT3_ZERO]
    gearPoint = Point3(suitPos.getX(), suitPos.getY() - 10, suitPos.getZ() + suit.height - 0.2)
    leftKnifeTracks = Parallel()
    rightKnifeTracks = Parallel()
    explodeTracks = Parallel()
    explosionTrack = Sequence()
    explosionTrack.append(Wait(1.5))
    explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
    for i in xrange(0, 3):
        knifeDelay = 0.11
        leftTrack = Sequence()
        leftTrack.append(Wait(1.1))
        leftTrack.append(Wait(i * knifeDelay))
        leftTrack.append(getPropAppearTrack(leftKnives[i], suit, leftPosPoints, 1e-06, Point3(1.1, 1.1, 1.1), scaleUpTime=0.1))
        leftTrack.append(getPropAppearTrack(leftKnives[i], suit, leftPosPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
        leftKnifeTracks.append(leftTrack)
        rightTrack = Sequence()
        rightTrack.append(Wait(1.1))
        rightTrack.append(Wait(i * knifeDelay))
        rightTrack.append(getPropAppearTrack(rightKnives[i], suit, rightPosPoints, 1e-06, Point3(0.1, 0.1, 0.1), scaleUpTime=0.1))
        rightTrack.append(getPropAppearTrack(rightKnives[i], suit, rightPosPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
        rightKnifeTracks.append(rightTrack)
        explodeTrack = Sequence()
        explodeTrack.append(Wait(1.6))
        explodeTrack.append(getPropAppearTrack(explode[i], suit, explodePosPoints, 1e-06, Point3(1.7, 1.7, 1.7), scaleUpTime=0.1))
        explodeTrack.append(getPropAppearTrack(explode[i], suit, explodePosPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
        explodeTrack.append(getPropAppearTrack(explode[i], suit, explodeHprPoints, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
        explodeTrack.append(getPropAppearTrack(explode[i], suit, explodeHprPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.1))
        explodeTracks.append(explodeTrack)

    damageAnims = [['slip-backward', 0.01, 0.35]]
    toonTracks = getToonTracks(attack, damageDelay=1.6, splicedDamageAnims=damageAnims, dodgeDelay=0.7, dodgeAnimNames=['sidestep'])
    soundTrack1 = Sequence(Wait(0),SoundInterval(globalBattleSoundCache.getSound('SA_bash.ogg'), node=suit))
    soundTrack2 = Sequence(Wait(1), SoundInterval(globalBattleSoundCache.getSound('SA_blast.ogg'), node=suit))
    soundTrack = Parallel(soundTrack1, soundTrack2)
    return Parallel(cameraTrack, suitTrack, toonTracks, soundTrack, leftKnifeTracks, rightKnifeTracks, explodeTracks, explosionTrack)

def doBlackOrb(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    eye = globalPropPool.getProp('black-orb')
    damageDelay = 2.44
    dodgeDelay = 1.64
    suitName = suit.getStyleName()
    if suitName == 'cr':
        posPoints = [Point3(-0.46, 4.85, 5.28), VBase3(-155.0, -20.0, 0.0)]
    elif suitName == 'tf':
        posPoints = [Point3(-0.4, 3.65, 5.01), VBase3(-155.0, -20.0, 0.0)]
    elif suitName == 'le':
        posPoints = [Point3(-0.64, 4.45, 5.91), VBase3(-155.0, -20.0, 0.0)]
    else:
        posPoints = [Point3(-0.4, 3.65, 5.01), VBase3(-155.0, -20.0, 0.0)]
    appearDelay = 0.8
    suitHoldStart = 1.06
    suitHoldStop = 1.69
    suitHoldDuration = suitHoldStop - suitHoldStart
    eyeHoldDuration = 1.1
    moveDuration = 1.1
    suitSplicedAnims = []
    suitSplicedAnims.append(['effort',
     0.01,
     0.01,
     suitHoldStart])
    suitSplicedAnims.extend(getSplicedLerpAnims('effort', suitHoldDuration, 1.1, startTime=suitHoldStart))
    suitSplicedAnims.append(['effort', 0.01, suitHoldStop])
    suitTrack = getSuitTrack(attack, splicedAnims=suitSplicedAnims)
    eyeAppearTrack = Sequence(Wait(suitHoldStart), Func(__showProp, eye, suit, posPoints[0], posPoints[1]), LerpScaleInterval(eye, suitHoldDuration, Point3(11, 11, 11)), Wait(eyeHoldDuration * 0.3), LerpHprInterval(eye, 0.02, Point3(205, 40, 0)), Wait(eyeHoldDuration * 0.7), Func(battle.movie.needRestoreRenderProp, eye), Func(eye.wrtReparentTo, battle))
    toonFace = __toonFacePoint(toon, parent=battle)
    if dmg > 0:
        lerpInterval = LerpPosInterval(eye, moveDuration, toonFace)
    else:
        lerpInterval = LerpPosInterval(eye, moveDuration, Point3(toonFace.getX(), toonFace.getY() - 5, toonFace.getZ() - 2))
    eyeMoveTrack = lerpInterval
    eyeRollTrack = LerpHprInterval(eye, moveDuration, Point3(0, 0, -180))
    eyePropTrack = Sequence(eyeAppearTrack, Parallel(eyeMoveTrack, eyeRollTrack), Func(battle.movie.clearRenderProp, eye), Func(MovieUtil.removeProp, eye))
    damageAnims = [['duck',
      0.01,
      0.01,
      1.4], ['slip-backward', 0.01, 0.3]]
    toonTrack = getToonTrack(attack, splicedDamageAnims=damageAnims, damageDelay=damageDelay, dodgeDelay=dodgeDelay, dodgeAnimNames=['duck'], showDamageExtraTime=1.7, showMissedExtraTime=1.7)
    soundTrack = getSoundTrack('SA_magic_orb.ogg', delay=0.5, node=suit)
    return Parallel(suitTrack, toonTrack, eyePropTrack, soundTrack)


def doRevvingUp(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    sanctioned = __makeSanctionedNodePath()
    missPoint = lambda sanctioned=sanctioned, toon=toon: __toonMissPoint(sanctioned, toon)
    propTrack = Sequence(
        Wait(0.5),
        Func(battle.movie.needRestoreRenderProp, sanctioned),
        Func(sanctioned.reparentTo, render),
        Func(sanctioned.setScale, 0.6),
        Func(sanctioned.setPosHpr, suit.getLeftHand(), 0.81, -1.11, -0.16, 0, 85, 90),
        Func(sanctioned.setP, 0),
        Func(sanctioned.setR, 0),
        getPropThrowTrack(attack, sanctioned, [__toonFacePoint(toon)], [missPoint]),
        Func(MovieUtil.removeProp, sanctioned),
        Func(battle.movie.clearRenderProp, sanctioned)
    )
    toonTrack = getToonTrack(attack, 0.8, ['conked'], 0.2, ['sidestep'])
    suitTrack = getSuitTrack(attack)
    suitTrack.append(Parallel(Sequence(Wait(1.0),  Func(suit.setChatAbsolute,
                                   "OFFENSIVE ANOMALY HAS BEEN DETECTED, PUNISHING FROM POINT OF GREATEST RESISTANCE, THREATS HAVE BEGUN TO REPAIR THEMSELVES. TARGETING LARGEST THREAT.",
                                   CFSpeech | CFTimeout),
                              Sequence(Wait(2.5)))))
    soundTrack = getSoundTrack('SA_revving_up.ogg', node=suit)
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack)


def doCourtSanction(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    pbpText = attack['playByPlayText']
    pbpDc = PlayByPlayText.PlayByPlayText()

    pbpDesc = pbpDc.getShowIntervalDesc('Your gags will be less effective!', 3.5)
    pbpTrack = pbpText.getShowIntervalCheat('Court Record!', 3.5)
    sanctioned = __makeSanctionedNodePath()
    missPoint = lambda sanctioned=sanctioned, toon=toon: __toonMissPoint(sanctioned, toon)
    propTrack = Sequence(
        Wait(0.5),
        Func(battle.movie.needRestoreRenderProp, sanctioned),
        Func(sanctioned.reparentTo, render),
        Func(sanctioned.setScale, 0.6),
        Func(sanctioned.setPosHpr, suit.getLeftHand(), 0, 0.11, -0.16, 0, 100, 90),
        Func(sanctioned.setP, 0),
        Func(sanctioned.setR, 0),
        getPropThrowTrack(attack, sanctioned, [__toonFacePoint(toon)], [missPoint]),
        Func(MovieUtil.removeProp, sanctioned),
        Func(battle.movie.clearRenderProp, sanctioned)
    )
    toonTrack = getToonTrack(attack, 0.8, ['conked'], 0.2, ['sidestep'])
    suitTrack = getSuitTrack(attack)
    suitTrack.append(Wait(3.0))
    suitTrackCease =  Parallel(Func(suit.setChatAbsolute,
                                   "Any gags used by the sanctioned toon will be significantly less effective.",
                                   CFSpeech | CFTimeout), ActorInterval(suit, 'cease'), getSoundTrack('SA_cease_and_desist.ogg', node=suit))
    suitTrack.append(suitTrackCease)
    soundTrack = getSoundTrack('SA_sanction.ogg', delay =.5, node=suit)
    notifyTrack = Sequence(Wait(1.0 + 0.75), Func(toon.showHpTextWhite, "SANCTIONED!", 10))
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack, notifyTrack)

def __makeSanctionedNodePath():
    tn = TextNode('CANCELLED')
    tn.setFont(getSuitFont())
    tn.setText('SANCTIONED\nSANCTIONED\nSANCTIONED')
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

def doLifeInsurance(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target['hp']
    suitTrack = getSuitTrack(attack)
    suit.setHealthForMe(int(suit.currHP + 75))
    soundTrack1 = getSoundTrack('SA_life_insurance_register.ogg', delay=0.2, node=suit)
    soundTrack2 = getSoundTrack('SA_life_insurance_loop.ogg', delay=1.7, node=suit)
    selfDamageTrack = Sequence(Wait(2), Func(suit.showHpText, +75), Func(suit.updateHealthBar, 0))
    return Parallel(suitTrack, soundTrack1, soundTrack2, selfDamageTrack)

def doWorkersCompensation(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target['hp']
    suitTrack = getSuitTrack(attack)
    suit.setHealthForMe(int(suit.currHP + 50))
    soundTrack = getSoundTrack('LB_toonup.ogg', delay=2.0, node=suit)
    selfDamageTrack = Sequence(Wait(2), Func(suit.showHpText, +50), Func(suit.updateHealthBar, 0))
    return Parallel(suitTrack, soundTrack, selfDamageTrack)

def doStealSafe(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target['hp']
    suitTrack = getSuitTrack(attack)
    suit.setHealthForMe(int(suit.currHP + (dmg * 3)))
    toonTrack = getToonTrack(attack, 0.6, ['slip-forward'], 0.01, ['applause'])
    selfDamageTrack = Sequence(Wait(2), Func(suit.showHpText, +(dmg * 3)), Func(suit.updateHealthBar, 0))
    multiTrackList = Parallel(suitTrack, toonTrack, selfDamageTrack)
    if dmg > 0:
        soundTrack = getSoundTrack('AA_drop_safe_miss.ogg', delay=0.2, node=suit)
        multiTrackList.append(soundTrack)
    return multiTrackList

def doWheelSpin(attack):
    suit = attack['suit']
    battle = attack['battle']
    #cameraTrack = Sequence(LerpPosHprInterval(camera, duration=1, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'), Wait(1.8), LerpPosHprInterval(camera, duration=0.5, pos=Point3(4, -11, 2), hpr=Point3(30, 0, 0), blendType='easeInOut'), Wait(2), LerpPosHprInterval(camera, duration=0, pos=Point3(3, -5, 10), hpr=Point3(30, -15, 0), blendType='easeInOut'), Wait(3.2), LerpPosHprInterval(camera, duration=0.5, pos=Point3(0, -15, 3), hpr=Point3(0, 10, 0), blendType='easeInOut'))
    suitTrack = Sequence(MovieUtil.createSuitLaughInterval(suit), ActorInterval(suit, 'highroller-neutral-levitate-in-out', duration=1), Func(suit.loop, 'highroller-neutral-levitate-loop'), Wait(9.5), ActorInterval(suit, 'highroller-neutral-levitate-in-out', startTime=1, endTime=0), Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    talkTrack = Sequence(Wait(7.5), Func(suit.setChatAbsolute, "WhAHAHAHAt a ffhow!", CFSpeech | CFTimeout), Wait(2.8), Func(suit.setChatAbsolute, "Oooo-hooo-hooo, ratingff are ffkyrocketing! Line goeff up, head turner! Keep thoffe cameraff rollin'!", CFSpeech | CFTimeout), Wait(4.5), Func(suit.setChatAbsolute, "Let'ff ffee the nefft big play for today!", CFSpeech | CFTimeout), Wait(3.7), Func(suit.setChatAbsolute, "Hope the folkff at home are ready for a real ffhowfftopper!", CFSpeech | CFTimeout), Wait(3.7), Func(suit.setChatAbsolute,  "This duet jufft got a hip hump bump to a five-part big band, babe!"
"I'm the hottest fftar on fftage! Ffo come on inamorata, let'ff burn a hole in those goggle boffeff!"
"Better ffmile before ya burn out!", CFSpeech | CFTimeout))
    soundTrack1 = getSoundTrack('ttcc_ene_hroller_laugh.ogg', node=suit)
    soundTrack2 = getSoundTrack('cc_s_sfx_ene_hroller_reappear_after_wheel.ogg', delay=7.0, node=suit)
    soundTrack3 = getSoundTrack('cc_s_sfx_ene_hroller_sweep_before_wheel.ogg', delay=3.0, node=suit)
    soundTrack = (Parallel(soundTrack1, soundTrack2, soundTrack3))
    return Parallel(talkTrack, suitTrack, soundTrack)

def doWheelSpin2(attack):
    suit = attack['suit']
    battle = attack['battle']
    #cameraTrack = Sequence(LerpPosHprInterval(camera, duration=1, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'), Wait(1.8), LerpPosHprInterval(camera, duration=0.5, pos=Point3(4, -11, 2), hpr=Point3(30, 0, 0), blendType='easeInOut'), Wait(2), LerpPosHprInterval(camera, duration=0, pos=Point3(3, -5, 10), hpr=Point3(30, -15, 0), blendType='easeInOut'), Wait(3.2), LerpPosHprInterval(camera, duration=0.5, pos=Point3(0, -15, 3), hpr=Point3(0, 10, 0), blendType='easeInOut'))
    suitTrack = Sequence(ActorInterval(suit, 'highroller-neutral-levitate-in-out', duration=1), Func(suit.loop, 'highroller-neutral-levitate-loop'), Wait(6.5), ActorInterval(suit, 'highroller-neutral-levitate-in-out', startTime=1, endTime=0), Wait(2.0), MovieUtil.createSuitLaughInterval2(suit))
    talkTrack = Sequence(Func(suit.setChatAbsolute, "Alright, alright, let'ff get thoffe efftraff on ffet, baby doll. Bring 'em in.", CFSpeech | CFTimeout), Wait(2.8), Func(suit.setChatAbsolute, "Peep your eyeff, we've got ffo much in fftore today for you!", CFSpeech | CFTimeout), Wait(2.5), Func(suit.setChatAbsolute, "What'ya waitin' for, babe? Hop on fftage! let'ff get hoppin' and boppin', jumpin' and jinglin', ffingin' and ffwingin'!", CFSpeech | CFTimeout), Wait(3.7), Func(suit.setChatAbsolute, "Hope the folkff at home are ready for a real ffhowfftopper!", CFSpeech | CFTimeout))
    soundTrack = getSoundTrack('ttcc_ene_hroller_laugh.ogg', delay=10.5, node=suit)
    return Parallel(talkTrack, suitTrack, soundTrack)

def doCaseClosed(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    toonPos = toon.getPos(battle)
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    movePoint = toon.getPos(battle)
    #cameraTrack = Sequence(LerpPosHprInterval(camera, duration=1, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'), Wait(1.8), LerpPosHprInterval(camera, duration=0.5, pos=Point3(4, -11, 2), hpr=Point3(30, 0, 0), blendType='easeInOut'), Wait(2), LerpPosHprInterval(camera, duration=0, pos=Point3(3, -5, 10), hpr=Point3(30, -15, 0), blendType='easeInOut'), Wait(3.2), LerpPosHprInterval(camera, duration=0.5, pos=Point3(0, -15, 3), hpr=Point3(0, 10, 0), blendType='easeInOut'))
    suitTrack = Sequence()
    suitTrack.append(LerpPosHprInterval(suit, duration=1, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0)))
    suitTrack.append(Wait(2.0))
    suitTrack.append(MovieUtil.createSuitCaseClosedInterval(suit))
    #suitOpenMouthTrack = MovieUtil.createSuitCaseClosedInterval(suit)
    #talkTrack = Sequence(Wait(7.5), Func(suit.setChatAbsolute, "Alright, alright, let'ff get thoffe efftraff on ffet, baby doll. Bring 'em in.", CFSpeech | CFTimeout), Wait(2.8), Func(suit.setChatAbsolute, "Peep your eyeff, we've got ffo much in fftore today for you!", CFSpeech | CFTimeout), Wait(2.5), Func(suit.setChatAbsolute, "Come on, babe, FFHOW UFF THOFFE NUMBERFF!", CFSpeech | CFTimeout), Wait(3.7), Func(suit.setChatAbsolute, "And now back to our regularly ffcheduled programming.", CFSpeech | CFTimeout))
    toonTrack = getToonTrack(attack, suitTrack.getDuration() - -4, ['slip-backward'], suitTrack.getDuration() - -4, ['bored'])
    soundTrack1 = getSoundTrack('ttcc_ene_hroller_laugh.ogg', node=suit)
    soundTrack2 = getSoundTrack('cc_s_sfx_ene_hroller_reappear_after_wheel.ogg', delay=7.0, node=suit)
    soundTrack3 = getSoundTrack('cc_s_sfx_ene_hroller_sweep_before_wheel.ogg', delay=3.0, node=suit)
    soundTrack = (Parallel(soundTrack1, soundTrack2, soundTrack3))
    return Parallel(suitTrack, toonTrack)

def doAccusations2(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    gavel = globalPropPool.getProp('LB_gavel')
    toonPos = toon.getPos(battle)
    gavelPos = Point3(toonPos.getX(), 2, 0)
    propTrack = Sequence(
        getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos, VBase3(0, 0, 0)], appearDelay=10,
                           scaleUpPoint=Point3(1), scaleUpTime=1.5),
        LerpHprInterval(gavel, 0.5, VBase3(0, 90, 0)),
        Parallel(getSoundTrack('LB_gavel.ogg', node=toon), Sequence(
            Wait(0.1),
            LerpHprInterval(gavel, 0.5, VBase3(0, 0, 0)),
            LerpScaleInterval(gavel, 1.5, MovieUtil.PNT3_ZERO)
        ))
    )
    #cameraTrack = Sequence(LerpPosHprInterval(camera, duration=1, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'), Wait(1.8), LerpPosHprInterval(camera, duration=0.5, pos=Point3(4, -11, 2), hpr=Point3(30, 0, 0), blendType='easeInOut'), Wait(2), LerpPosHprInterval(camera, duration=0, pos=Point3(3, -5, 10), hpr=Point3(30, -15, 0), blendType='easeInOut'), Wait(3.2), LerpPosHprInterval(camera, duration=0.5, pos=Point3(0, -15, 3), hpr=Point3(0, 10, 0), blendType='easeInOut'))
    #suitTrack = getSuitAnimTrack(attack)
    cameraTrack = Sequence(
            LerpPosHprInterval(camera, duration=1, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'),
            Wait(1.8), LerpPosHprInterval(camera, duration=0.5, pos=Point3(4, -11, 2), hpr=Point3(30, 0, 0),
                                          blendType='easeInOut'), Wait(2),
            LerpPosHprInterval(camera, duration=0, pos=Point3(3, -5, 10), hpr=Point3(30, -15, 0),
                               blendType='easeInOut'), Wait(3.2),
            LerpPosHprInterval(camera, duration=0.5, pos=Point3(0, -15, 3), hpr=Point3(0, 10, 0),
                               blendType='easeInOut'))
    suitTrack = getSuitAnimTrack(attack)
    suit.setHealthForMe(int(suit.currHP - 350))
    selfDamageTrack = Sequence(Wait(11.6), Func(suit.showHpText, -350), Func(suit.updateHealthBar, 0))
    talkTrack = Sequence(Wait(3.5), Func(suit.setChatAbsolute,
                                             "This toon has been accused of damaging countless cogs throughout Toontown.",
                                             CFSpeech | CFTimeout), Wait(2.8),
                             Func(suit.setChatAbsolute, "Here is the evidence to support my claim.",
                                  CFSpeech | CFTimeout), Wait(2.5),
                             Func(suit.setChatAbsolute, "Has the jury reached a verdict?",
                                  CFSpeech | CFTimeout), Wait(3.7),
                             Func(suit.setChatAbsolute, "This toon has proven their innocence. This toon has received a gag damage boost as compensation.",
                                  CFSpeech | CFTimeout))
    animTrack = Sequence(Wait(2), ActorInterval(suit, 'speak', startTime=0, endTime=8.6, playRate=1),
                             ActorInterval(suit, 'soak', startTime=0, endTime=2.5, playRate=1))
    toonTrack = getToonTrack(attack, suitTrack.getDuration() - -4, ['bored'], suitTrack.getDuration() - -4,
                                 ['bored'])
    soundTrack = getSoundTrack('SA_hurry_sickness.ogg', delay=12.5, node=suit)
    return Parallel(cameraTrack, talkTrack, suitTrack, animTrack, toonTrack, soundTrack, selfDamageTrack)

def doAccusations(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    toonPos = toon.getPos(battle)
    #cameraTrack = LerpPosHprInterval(camera, duration=1, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut')
    suitTrack = getSuitAnimTrack(attack)
    suit.setHealthForMe(int(suit.currHP + 1000))
    selfDamageTrack = Sequence(Wait(5), Func(suit.showHpText, + 1000), Func(suit.updateHealthBar, 0))
    notifyTrack = Sequence(Wait(2.5), Func(suit.showHpText, "Desperation!\n+1 Round Lure Resistance!\n1.4x Damage Multiplier", 2, openEnded=0))
    talkTrack = Sequence(Wait(2.5), Func(suit.setChatAbsolute, "You may have defeated my partner, however I'm not going down that easily.", CFSpeech | CFTimeout), Wait(3.0), Func(suit.setChatAbsolute, "Let's see how much power you really have. I will be immune to all gags for 1 turn.", CFSpeech | CFTimeout))
    animTrack = Sequence(Wait(5.0), Func(suit.play, 'frustrated'), Func(suit.loop, 'neutral%s' % (
        '-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    soundTrack = getSoundTrack('LB_toonup.ogg', delay=5.0, node=suit)
    return Parallel(talkTrack, suitTrack, animTrack, soundTrack, notifyTrack, selfDamageTrack)

def doGavel(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    gavel = globalPropPool.getProp('LB_gavel')
    toonPos = toon.getPos(battle)
    initialScale = toon.getScale()
    gavelPos = Point3(toonPos.getX(), 2, 0)
    propTrack = Sequence(
        getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos, VBase3(0, 0, 0)], appearDelay=0.0, scaleUpPoint=Point3(1), scaleUpTime=1.5),
        LerpHprInterval(gavel, 0.5, VBase3(0, 90, 0)),
        Parallel(getSoundTrack('LB_gavel.ogg', node=toon), Sequence(
            Wait(0.1),
            LerpHprInterval(gavel, 0.5, VBase3(0, 0, 0)),
            LerpScaleInterval(gavel, 1.5, MovieUtil.PNT3_ZERO)
        ))
    )
    suitTrack = getSuitTrack(attack)
    if dmg > 0:
        toonTrack = Sequence(
            Wait(2.0),
            Parallel(
                Func(toon.enterFlattened),
                Func(toon.showHpText, -dmg, openEnded=0),
                Func(__doDamage, toon, dmg, target['died'])
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
    else:
        toonTrack = Sequence(
            Wait(0.9),
            Parallel(
                Func(MovieUtil.indicateMissed, toon),
                ActorInterval(toon, 'sidestep'),
                getAllyToonsDodgeParallel(target)
            )
        )
    return Parallel(suitTrack, toonTrack, propTrack)

def doGavelOLD(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    gavel = globalPropPool.getProp('LB_gavel')
    damageDelay = 2.44
    dodgeDelay = 1.64
    suitTrack = getSuitTrack(attack)
    gavelPosPoints = [Point3(0, 3, 0), VBase3(180, 0, 0)]
    downTime = 0.25
    upTime = 1
    downAngle = .80
    goingDown = LerpHprInterval(gavel, downTime, Point3(0, downAngle, 0), startHpr=Point3(0, 0, 0))
    goingUp = LerpHprInterval(gavel, upTime, Point3(0, 0, 0), startHpr=Point3(0, downAngle, 0))
    gavelPropTrack = Sequence()
    soundTrack = getSoundTrack('LB_gavel.ogg', delay= 2.25, node=toon)
    soundTrack2 = getSoundTrack('LB_gavel.ogg', delay= 4.0, node=toon)
    if dmg > 0 :
        gavelPropTrack.append(Sequence(getPropAppearTrack(gavel, suit, gavelPosPoints, 1e-06, Point3(1, 1, 1), scaleUpTime=1.0), Wait(1), goingDown, Wait(0.5), goingUp, goingDown, Wait(1), goingUp, Wait(0.5),
                                       getPropAppearTrack(gavel, suit, gavelPosPoints, 1e-06, Point3(0, 0, 0), 1.0, Point3(1, 1, 1)),
                                       Func(battle.movie.clearRenderProp, gavel),
                                       Func(MovieUtil.removeProp, gavel)))
        toonTrack = getToonTrack(attack, 2.25, ['neutral'], 1.0, ['sidestep'])
        return Parallel(suitTrack, toonTrack, gavelPropTrack, soundTrack, soundTrack2)
    else:
        gavelPropTrack.append(
            Sequence(getPropAppearTrack(gavel, suit, gavelPosPoints, 1e-06, Point3(1, 1, 1), scaleUpTime=1.0), Wait(1),
                     goingDown, Wait(0.5), goingUp, goingDown, Wait(1), goingUp, Wait(0.5),
                     getPropAppearTrack(gavel, suit, gavelPosPoints, 1e-06, Point3(0, 0, 0), 1.0, Point3(1, 1, 1)),
                     Func(battle.movie.clearRenderProp, gavel),
                     Func(MovieUtil.removeProp, gavel)))
        toonTrack = getToonTrack(attack, 2.25, ['neutral'], 1.0, ['sidestep'])
        return Parallel(suitTrack, toonTrack, gavelPropTrack, soundTrack)

def doSlushFund(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target['hp']
    theSuit = None
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
    suit.setHealthForMe(int(suit.currHP - (suit.currHP / 4)))
    print('suit.currHP %i' % int(suit.currHP))

    print('ts.currHP %i' % int(theSuit.currHP))
    print('setHP() %i' % int(theSuit.currHP + (suit.currHP / 4)))
    theSuit.setHealthForMe(int(theSuit.currHP + (suit.currHP / 4)))
    print('ts.currHP %i' % int(theSuit.currHP))

    suitTrack = Sequence(getSuitAnimTrack(attack), ActorInterval(attack['suit'], 'neutral%s' % (
        '-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_defense.ogg'), node=suit))
    selfDamageTrack = Sequence(Wait(2), Func(suit.showHpText, -(suit.currHP / 4)), Func(suit.updateHealthBar, 0))
    managerHealTrack = Sequence(Wait(2), Func(theSuit.showHpText, (suit.currHP / 4)), Func(theSuit.updateHealthBar, 0),
                                Func(theSuit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases),
                                     CFSpeech | CFTimeout),
                                SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'), node=theSuit))
    return Parallel(suitTrack, soundTrack, selfDamageTrack, managerHealTrack)


def doPoisonSpray(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target['hp']
    theSuit = None
    for s in battle.activeSuits:
        if s.dna.name == 'ste':
            print('Found manager... using it...')
            theSuit = s
        elif s.dna.name == 'lit':
            print('Found manager... using it...')
            theSuit = s
        elif s.dna.name == 'csm':
            print('Found manager... using it...')
            theSuit = s
        elif s.dna.name == 'gtk':
            print('Found manager... using it...')
            theSuit = s
        elif s.dna.name == 'frs':
            print('Found manager... using it...')
            theSuit = s
        elif s.dna.name == 'fbd':
            print('Found manager... using it...')
            theSuit = s
        elif s.dna.name == 'mad':
            print('Found manager... using it...')
            theSuit = s
        elif s.dna.name == 'crf':
            print('Found manager... using it...')
            theSuit = s
        elif s.dna.name == 'tb':
            print('Found manager... using it...')
            theSuit = s
        elif s.dna.name == 'prr':
            print('Found manager... using it...')
            theSuit = s
        elif s.dna.name == 'dsk':
            print('Found manager... using it...')
            theSuit = s
        elif s.dna.name == 'ffm':
            print('Found manager... using it...')
            theSuit = s
        elif s.dna.name == 'dvp':
            print('Found manager... using it...')
            theSuit = s
        elif s.dna.name == 'bsh':
            print('Found manager... using it...')
            theSuit = s
        elif s.dna.name == 'fd':
            print('Found manager... using it...')
            theSuit = s
        elif s.dna.name == 'kb':
            print('Found manager... using it...')
            theSuit = s
        elif s.dna.name == 'otm':
            print('Found manager... using it...')
            theSuit = s
        elif s.dna.name == 'tcm':
            print('Found manager... using it...')
            theSuit = s
        elif s.dna.name == 'cry':
            print('Found manager... using it...')
            theSuit = s
        elif s.dna.name == 'tyh':
            print('Found manager... using it...')
            theSuit = s
        elif s.dna.name == 'jgd':
            print('Found manager... using it...')
            theSuit = s
        elif s.dna.name == 'bby':
            print('Found manager... using it...')
            theSuit = s
        elif s.dna.name == 'jur':
            print('Found manager... using it...')
            theSuit = s
        elif s.dna.name == 'bg':
            print('Found manager... using it...')
            theSuit = s
        elif s.dna.name == 'tb':
            print('Found manager... using it...')
            theSuit = s
        elif s.dna.name == 'bgr':
            print('Found manager... using it...')
            theSuit = s
        elif s.dna.name == 'mdr':
            print('Found manager... using it...')
            theSuit = s
        elif s.dna.name == 'ddv':
            print('Found manager... using it...')
            theSuit = s
        elif s.dna.name == 'nhy':
            print('Found manager... using it...')
            theSuit = s
        elif s.dna.name == 'wrt':
            print('Found manager... using it...')
            theSuit = s
        elif s.dna.name == 'auh':
            print('Found manager... using it...')
            theSuit = s

    if theSuit == None:
        print('Error finding manager... using self...')
        theSuit = suit

    print('*************************************')

    print('suit.currHP %i' % int(suit.currHP))
    print('setHP() %i' % int(suit.currHP - (suit.currHP/8)))
    suit.setHealthForMe(int(suit.currHP - (suit.currHP/8)))
    print('suit.currHP %i' % int(suit.currHP))

    print('ts.currHP %i' % int(theSuit.currHP))
    print('setHP() %i' % int(theSuit.currHP + (suit.currHP/8)))
    theSuit.setHealthForMe(int(theSuit.currHP + (suit.currHP/8)))
    print('ts.currHP %i' % int(theSuit.currHP))

    suitTrack = Sequence(getSuitAnimTrack(attack), ActorInterval(attack['suit'], 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_defense.ogg'), node=suit))
    selfDamageTrack = Sequence(Wait(2), Func(suit.showHpText, -(suit.currHP/8)), Func(suit.updateHealthBar, 0))
    managerHealTrack = Sequence(Wait(2), Func(theSuit.showHpText, (suit.currHP/8)), Func(theSuit.updateHealthBar, 0), Func(theSuit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases), CFSpeech | CFTimeout),
                                SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'), node=theSuit))
    suitTrack.append(Wait(2.0))
    suitTrack.append(Func(suit.setChatAbsolute, "I told you I'd make it up to you, didn't I?", CFSpeech | CFTimeout))
    return Parallel(suitTrack, soundTrack, selfDamageTrack, managerHealTrack)

def doExtraTip(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target['hp']
    theSuit = None

    if theSuit == None:
        print('Error finding manager... using self...')
        theSuit = suit

    print('*************************************')

    print('ts.currHP %i' % int(theSuit.currHP))
    print('setHP() %i' % int(theSuit.currHP + 500))
    theSuit.setHealthForMe(int(theSuit.currHP + 500))
    print('ts.currHP %i' % int(theSuit.currHP))
    suitTrack = Sequence(getSuitAnimTrack(attack), ActorInterval(suit, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    soundTrack1 = getSoundTrack('SA_paper_throw.ogg', delay=5, node=suit)
    soundTrack2 = getSoundTrack('SA_extra_tip.ogg', delay=3, node=suit)
    multiTrack = Parallel(soundTrack1, soundTrack2)
    healSound = Sequence(Wait(5.0), SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'), node=suit))
    return Parallel(suitTrack, healSound, multiTrack)


def doWaterSpray(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1

    damageDelay = 1.95
    dodgeDelay = 0.95
    sprayEffect = BattleParticles.createParticleEffect('WaterSpray')
    suitName = suit.getStyleName()
    sprayEffect.setPos(Point3(-5.2, 4.6, 2.7))
    suitTrack = getSuitAnimTrack(attack)
    sprayTrack = getPartTrack(sprayEffect, 1.0, 1.9, [sprayEffect, suit, 0])
    liftTracks = Parallel()
    toonRiseTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        if dmg > 0:
            liftEffect = BattleParticles.createParticleEffect('SprayLift')
            liftEffect.setPos(toon.getPos(battle))
            liftEffect.setZ(liftEffect.getZ() - 1.3)
            liftTracks.append(getPartTrack(liftEffect, 1.1, 4.1, [liftEffect, battle, 0]))
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
    damageAnims.append(['slip-forward', 0.01, 0.5])
    dodgeAnims = []
    dodgeAnims.append(['jump',
     0.01,
     0,
     0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.0, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, splicedDodgeAnims=dodgeAnims, showDamageExtraTime=2.7)
    if hitAtleastOneToon == 1:
        soundTrack = getSoundTrack('SA_watercooler_spray_only.ogg', delay=4.4, node=suit)
        return Parallel(suitTrack, sprayTrack, soundTrack, liftTracks, toonTracks, toonRiseTracks)
    else:
        return Parallel(suitTrack, sprayTrack, liftTracks, toonTracks, toonRiseTracks)


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
    waterfallTrack = getPartTrack(waterfallEffect, 0.6, 1.3, [waterfallEffect, suit, 0])
    toonTracks = getToonTracks(attack, 1.8, ['slip-forward'], 1.29, ['jump'])
    soundTrack = Sequence(Wait(1), SoundInterval(globalBattleSoundCache.getSound('SA_money_fall.ogg'), node=suit))
    return Parallel(cameraTrack, suitTrack, partTrack1, partTrack2, waterfallTrack, toonTracks, soundTrack)



def doTeeOff(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    club = globalPropPool.getProp('golf-club')
    ball = globalPropPool.getProp('golf-ball')
    suitTrack = getSuitTrack(attack)
    clubPosPoints = [Point3(0.5, 3.5, -0.5), VBase3(-63.097, -23.988, 18.435)]
    clubPropTrack = getPropTrack(club, suit.getRightHand(), clubPosPoints, 0.5, 5.2, Point3(1.1, 1.1, 1.1))
    suitName = attack['suitName']
    if suitName == 'ym':
        ballPosPoints = [Point3(2.1, 0, 0.1)]
    elif suitName == 'tbc':
        ballPosPoints = [Point3(4.1, 0, 0.1)]
    elif suitName == 'm':
        ballPosPoints = [Point3(3.2, 0, 0.1)]
    elif suitName == 'rb':
        ballPosPoints = [Point3(4.2, 0, 0.1)]
    else:
        ballPosPoints = [Point3(2.1, 0, 0.1)]
    ballPropTrack = Sequence(getPropAppearTrack(ball, suit, ballPosPoints, 1.7, Point3(1.5, 1.5, 1.5)), Func(battle.movie.needRestoreRenderProp, ball), Func(ball.wrtReparentTo, render), Wait(2.15))
    missPoint = lambda ball = ball, toon = toon: __toonMissPoint(ball, toon)
    ballPropTrack.append(getPropThrowTrack(attack, ball, [__toonFacePoint(toon)], [missPoint]))
    ballPropTrack.append(Func(battle.movie.clearRenderProp, ball))
    dodgeDelay = suitTrack.getDuration() - 4.35
    toonTrack = getToonTrack(attack, suitTrack.getDuration() - 2.25, ['conked'], dodgeDelay, ['duck'], showMissedExtraTime=1.7)
    soundTrack = getSoundTrack('SA_tee_off.ogg', delay=4.1, node=suit)
    return Parallel(suitTrack, toonTrack, clubPropTrack, ballPropTrack, soundTrack)

def doAftershock(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    suitTrack = Sequence(getSuitAnimTrack(attack))
    dodgeDelay = suitTrack.getDuration() - 2.35
    toonTrack = getToonTrack(attack, suitTrack.getDuration() - 2.25, ['slip-forward'], dodgeDelay, ['duck'])
    soundTrack1 = getSoundTrack('AA_lightning.ogg', delay=0.1, node=suit)
    soundTrack2 = getSoundTrack('AA_cog_shock.ogg', delay=2.1, node=suit)
    soundTrack = (soundTrack1, soundTrack2)

    oldcolor = render.getColorScale()
    lightingTrack = Sequence(Wait(1), LerpColorScaleInterval(render, 0.5, (0.3, 0.3, 0.3, 1)), LerpColorScaleInterval(render, 2.5, (0.9, 0.3, 0.3, 1)), LerpColorScaleInterval(render, 1, (oldcolor)))
    return Parallel(suitTrack, toonTrack, soundTrack, lightingTrack)


def doBrainStorm(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    BattleParticles.loadParticles()
    snowEffect = BattleParticles.createParticleEffect('BrainStorm')
    snowEffect2 = BattleParticles.createParticleEffect('BrainStorm')
    snowEffect3 = BattleParticles.createParticleEffect('BrainStorm')
    effectColor = Vec4(0.65, 0.79, 0.93, 0.85)
    BattleParticles.setEffectTexture(snowEffect, 'brainstorm-box', color=effectColor)
    BattleParticles.setEffectTexture(snowEffect2, 'brainstorm-env', color=effectColor)
    BattleParticles.setEffectTexture(snowEffect3, 'brainstorm-track', color=effectColor)
    cloud = globalPropPool.getProp('stormcloud')
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        partDelay = 1.2
        damageDelay = 4.5
        dodgeDelay = 3.3
    elif suitType == 'b':
        partDelay = 1.2
        damageDelay = 4.5
        dodgeDelay = 3.3
    elif suitType == 'c':
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
    cloudPropTrack.append(Parallel(ParticleInterval(snowEffect, cloud, worldRelative=0, duration=2.2, cleanup=True), Sequence(Wait(0.5), ParticleInterval(snowEffect2, cloud, worldRelative=0, duration=1.7, cleanup=True)), Sequence(Wait(1.0), ParticleInterval(snowEffect3, cloud, worldRelative=0, duration=1.2, cleanup=True)), Sequence(ActorInterval(cloud, 'stormcloud', startTime=3, duration=0.5), ActorInterval(cloud, 'stormcloud', startTime=2.5, duration=0.5), ActorInterval(cloud, 'stormcloud', startTime=1, duration=1.5))))
    cloudPropTrack.append(Wait(0.4))
    cloudPropTrack.append(LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO))
    cloudPropTrack.append(Func(MovieUtil.removeProp, cloud))
    cloudPropTrack.append(Func(battle.movie.clearRenderProp, cloud))
    damageAnims = [['cringe',
      0.01,
      0.4,
      0.8], ['duck', 1e-06, 1.6]]
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'], showMissedExtraTime=1.1)
    soundTrack = getSoundTrack('SA_brainstorm.ogg', delay=2.6, node=suit)
    return Parallel(suitTrack, toonTrack, cloudPropTrack, soundTrack)


def doBuzzWord(attack):
    suit = attack['suit']
    target = attack['target']
    toon = target['toon']
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
    if suitType == 'a':
        partDelay = 4.0
        partDuration = 2.2
        damageDelay = 4.5
        dodgeDelay = 3.8
    elif suitType == 'b':
        partDelay = 1.3
        partDuration = 2
        damageDelay = 2.5
        dodgeDelay = 1.8
    elif suitType == 'c':
        partDelay = 4.0
        partDuration = 2.2
        damageDelay = 4.5
        dodgeDelay = 3.8
    suitName = suit.getStyleName()
    if suitName == 'm':
        for effect in particleEffects:
            effect.setPos(0, 2.8, suit.getHeight() - 2.5)
            effect.setHpr(0, -20, 0)

    elif suitName == 'mm':
        for effect in particleEffects:
            effect.setPos(0, 2.1, suit.getHeight() - 0.8)

    suitTrack = getSuitTrack(attack)
    particleTracks = []
    for effect in particleEffects:
        particleTracks.append(getPartTrack(effect, partDelay, partDuration, [effect, suit, 0]))

    toonTrack = getToonTrack(attack, damageDelay=damageDelay, damageAnimNames=['cringe'], splicedDodgeAnims=[['duck', dodgeDelay, 1.4]], showMissedExtraTime=dodgeDelay + 0.5)
    soundTrack = getSoundTrack('SA_buzz_word.ogg', delay=3.9, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, *particleTracks)


def doDemotion(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    BattleParticles.loadParticles()
    sprayEffect = BattleParticles.createParticleEffect('DemotionSpray')
    freezeEffect = BattleParticles.createParticleEffect('DemotionFreeze')
    unFreezeEffect = BattleParticles.createParticleEffect(file='demotionUnFreeze')
    BattleParticles.setEffectTexture(sprayEffect, 'snow-particle')
    BattleParticles.setEffectTexture(freezeEffect, 'snow-particle')
    BattleParticles.setEffectTexture(unFreezeEffect, 'snow-particle')
    facePoint = __toonFacePoint(toon)
    freezeEffect.setPos(0, 0, facePoint.getZ())
    unFreezeEffect.setPos(0, 0, facePoint.getZ())
    suitTrack = getSuitTrack(attack)
    partTrack = getPartTrack(sprayEffect, 0.7, 1.1, [sprayEffect, suit, 0])
    partTrack2 = getPartTrack(freezeEffect, 1.4, 2.9, [freezeEffect, toon, 0])
    partTrack3 = getPartTrack(unFreezeEffect, 6.65, 0.5, [unFreezeEffect, toon, 0])
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
    toonTrack = getToonTrack(attack, damageDelay=1.0, splicedDamageAnims=damageAnims, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.6, showDamageExtraTime=1.3)
    soundTrack = getSoundTrack('SA_demotion.ogg', delay=1.2, node=suit)
    if dmg > 0:
        return Parallel(suitTrack, toonTrack, soundTrack, partTrack, partTrack2, partTrack3)
    else:
        return Parallel(suitTrack, toonTrack, soundTrack, partTrack)


def doCanned(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target['hp']
    toon = target['toon']
    hips = toon.getHipsParts()
    propDelay = 0.8
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'c':
        suitDelay = 1.13
        dodgeDelay = 3.1
    else:
        suitDelay = 1.83
        dodgeDelay = 3.6
    throwDuration = 1.5
    can = globalPropPool.getProp('can')
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
    suitTrack = getSuitTrack(attack)
    posPoints = [Point3(-0.14, 0.15, 0.08), VBase3(-10.584, 11.945, -161.684)]
    throwTrack = Sequence(getPropAppearTrack(can, suit.getRightHand(), posPoints, propDelay, Point3(6, 6, 6), scaleUpTime=0.5))
    propDelay = propDelay + 0.5
    throwTrack.append(Wait(suitDelay))
    hitPoint = toon.getPos(battle)
    hitPoint.setX(hitPoint.getX() + 1.1)
    hitPoint.setY(hitPoint.getY() - 0.5)
    hitPoint.setZ(hitPoint.getZ() + toon.height + 1.1)
    throwTrack.append(Func(battle.movie.needRestoreRenderProp, can))
    throwTrack.append(getThrowTrack(can, hitPoint, duration=throwDuration, parent=battle))
    if dmg > 0:
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
        throwTrack.append(Wait(2.4))
        throwTrack.append(Func(MovieUtil.removeProp, can2))
        throwTrack.append(Func(battle.movie.clearRestoreHips))
        scaleTrack = Sequence(Wait(propDelay + suitDelay), LerpScaleInterval(can, throwDuration, scaleUpPoint))
        hprTrack = Sequence(Wait(propDelay + suitDelay), LerpHprInterval(can, throwDuration, canHpr))
        soundTrack = Sequence(Wait(2.6), SoundInterval(globalBattleSoundCache.getSound('SA_canned_tossup_only.ogg'), node=suit), SoundInterval(globalBattleSoundCache.getSound('SA_canned_impact_only.ogg'), node=suit))
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
        soundTrack = getSoundTrack('SA_canned_tossup_only.ogg', delay=2.6, node=suit)
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
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    damageDelay = 2.3
    sprayEffect = BattleParticles.createParticleEffect(file='downsizeSpray')
    cloudEffect = BattleParticles.createParticleEffect(file='downsizeCloud')
    toonPos = toon.getPos(toon)
    cloudPos = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.getHeight() * 0.55)
    cloudEffect.setPos(cloudPos)
    suitTrack = getSuitTrack(attack)
    sprayTrack = getPartTrack(sprayEffect, 1.0, 1.28, [sprayEffect, suit, 0])
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
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.6, dodgeAnimNames=['sidestep'])
    if dmg > 0:
        return Parallel(suitTrack, sprayTrack, cloudTrack, shrinkTrack, toonTrack)
    else:
        return Parallel(suitTrack, sprayTrack, toonTrack)


def doPinkSlip(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    paper = globalPropPool.getProp('pink-slip')
    throwDelay = 3.03
    throwDuration = 0.5
    suitTrack = getSuitTrack(attack)
    posPoints = [Point3(0.07, -0.06, -0.18), VBase3(-172.075, -26.715, -89.131)]
    paperAppearTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.8, Point3(8, 8, 8), scaleUpTime=0.5))
    paperAppearTrack.append(Wait(1.73))
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
    damageAnims = [['jump',
      0.01,
      0.3,
      0.7], ['slip-forward', 0.01]]
    toonTrack = getToonTrack(attack, damageDelay=2.81, splicedDamageAnims=damageAnims, dodgeDelay=2.8, dodgeAnimNames=['jump'], showDamageExtraTime=0.9)
    soundTrack = getSoundTrack('SA_pink_slip.ogg', delay=2.9, duration=1.1, node=suit)
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack)


def doReOrg(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    damageDelay = 1.7
    attackDelay = 1.7
    sprayEffect = BattleParticles.createParticleEffect(file='reorgSpray')
    suitTrack = getSuitTrack(attack)
    partTrack = getPartTrack(sprayEffect, 1.0, 1.9, [sprayEffect, suit, 0])
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
            headTracks.append(Sequence(Wait(attackDelay), LerpPosInterval(part, 0.1, Point3(x - 0.2, y, z - 0.03)), LerpPosInterval(part, 0.1, Point3(x + 0.4, y, z - 0.03)), LerpPosInterval(part, 0.1, Point3(x - 0.4, y, z - 0.03)), LerpPosInterval(part, 0.1, Point3(x + 0.4, y, z - 0.03)), LerpPosInterval(part, 0.1, Point3(x - 0.2, y, z - 0.04)), LerpPosInterval(part, 0.25, Point3(x, y, z + 2.2)), LerpHprInterval(part, 0.4, VBase3(360, 0, 180)), LerpPosInterval(part, 0.3, Point3(x, y, z + 3.1)), LerpPosInterval(part, 0.15, Point3(x, y, z + 0.3)), Wait(0.15), LerpHprInterval(part, 0.6, VBase3(-745, 0, 180), startHpr=VBase3(0, 0, 180)), LerpHprInterval(part, 0.8, VBase3(25, 0, 180), startHpr=VBase3(0, 0, 180)), LerpPosInterval(part, 0.15, Point3(x, y, z + 1)), LerpHprInterval(part, 0.3, VBase3(h, p, r)), Wait(0.2), LerpPosInterval(part, 0.1, Point3(x, y, z)), Wait(0.9)))

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
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.01, dodgeAnimNames=['duck'], showDamageExtraTime=2.1, showMissedExtraTime=2.0)
    if dmg > 0:
        return Parallel(suitTrack, partTrack, toonTrack, headTracks, chestTracks)
    else:
        return Parallel(suitTrack, partTrack, toonTrack)


def doSacked(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target['hp']
    toon = target['toon']
    hips = toon.getHipsParts()
    propDelay = 0.85
    suitDelay = 1.93
    throwDuration = 0.9
    sack = globalPropPool.getProp('sandbag')
    initialScale = Point3(0.65, 1.47, 1.28)
    scaleUpPoint = Point3(1.05, 1.67, 0.98) * 4.1
    sackHpr = VBase3(-154.33, -6.33, 163.8)
    suitTrack = getSuitTrack(attack)
    posPoints = [Point3(0.51, -2.03, -0.73), VBase3(90.0, -24.98, 77.73)]
    sackAppearTrack = Sequence(getPropAppearTrack(sack, suit.getRightHand(), posPoints, propDelay, initialScale, scaleUpTime=0.2))
    propDelay = propDelay + 0.2
    sackAppearTrack.append(Wait(suitDelay))
    hitPoint = toon.getPos(battle)
    if dmg > 0:
        hitPoint.setX(hitPoint.getX() + 2.1)
        hitPoint.setY(hitPoint.getY() + 0.9)
        hitPoint.setZ(hitPoint.getZ() + toon.height + 1.2)
    else:
        hitPoint.setZ(hitPoint.getZ() - 0.2)
    sackAppearTrack.append(Func(battle.movie.needRestoreRenderProp, sack))
    sackAppearTrack.append(getThrowTrack(sack, hitPoint, duration=throwDuration, parent=battle))
    if dmg > 0:
        sack2 = MovieUtil.copyProp(sack)
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
        sackAppearTrack.append(Wait(2.4))
        sackAppearTrack.append(Func(MovieUtil.removeProp, sack2))
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
    toonTrack = getToonTrack(attack, damageDelay=propDelay + suitDelay + throwDuration, splicedDamageAnims=damageAnims, dodgeDelay=3.0, dodgeAnimNames=['sidestep'], showDamageExtraTime=1.8, showMissedExtraTime=0.8)
    return Parallel(suitTrack, toonTrack, sackTrack)


def doGlowerPower(attack):
    suit = attack['suit']
    battle = attack['battle']
    leftKnives = []
    rightKnives = []
    for i in xrange(0, 3):
        leftKnives.append(globalPropPool.getProp('dagger'))
        rightKnives.append(globalPropPool.getProp('dagger'))

    suitTrack = getSuitTrack(attack)
    suitName = suit.getStyleName()
    if suitName == 'hh':
        leftPosPoints = [Point3(0.3, 4.3, 5.3), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.3, 4.3, 5.3), MovieUtil.PNT3_ZERO]
    elif suitName == 'tbc':
        leftPosPoints = [Point3(0.6, 4.5, 6), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.6, 4.5, 6), MovieUtil.PNT3_ZERO]
    else:
        leftPosPoints = [Point3(0.4, 6.0, 7.0), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.4, 6.0, 7.0), MovieUtil.PNT3_ZERO]
    leftKnifeTracks = Parallel()
    rightKnifeTracks = Parallel()
    for i in xrange(0, 3):
        knifeDelay = 0.11
        leftTrack = Sequence()
        leftTrack.append(Wait(1.1))
        leftTrack.append(Wait(i * knifeDelay))
        leftTrack.append(getPropAppearTrack(leftKnives[i], suit, leftPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
        leftTrack.append(getPropThrowTrack(attack, leftKnives[i], hitPointNames=['face'], missPointNames=['miss'], hitDuration=0.3, missDuration=0.3))
        leftKnifeTracks.append(leftTrack)
        rightTrack = Sequence()
        rightTrack.append(Wait(1.1))
        rightTrack.append(Wait(i * knifeDelay))
        rightTrack.append(getPropAppearTrack(rightKnives[i], suit, rightPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
        rightTrack.append(getPropThrowTrack(attack, rightKnives[i], hitPointNames=['face'], missPointNames=['miss'], hitDuration=0.3, missDuration=0.3))
        rightKnifeTracks.append(rightTrack)

    damageAnims = [['slip-backward', 0.01, 0.35]]
    toonTrack = getToonTrack(attack, damageDelay=1.6, splicedDamageAnims=damageAnims, dodgeDelay=0.7, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_glower_power.ogg', delay=1.1, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, leftKnifeTracks, rightKnifeTracks)

def doSnipe(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target['hp']
    toon = target['toon']
    leftKnives = []
    rightKnives = []
    toonPos = toon.getPos(battle)
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.height - 0.2)
    explosionTrack = Sequence()
    explosionTrack.append(Wait(1.5))
    explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
    for i in xrange(0, 3):
        leftKnives.append(globalPropPool.getProp('dagger'))
        rightKnives.append(globalPropPool.getProp('dagger'))

    suitTrack = getSuitTrack(attack)
    suitName = suit.getStyleName()
    if suitName == 'hh':
        leftPosPoints = [Point3(0.3, 4.3, 5.3), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.3, 4.3, 5.3), MovieUtil.PNT3_ZERO]
    elif suitName == 'tbc':
        leftPosPoints = [Point3(0.6, 4.5, 6), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.6, 4.5, 6), MovieUtil.PNT3_ZERO]
    else:
        leftPosPoints = [Point3(0.4, 6.0, 7.0), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.4, 6.0, 7.0), MovieUtil.PNT3_ZERO]
    leftKnifeTracks = Parallel()
    rightKnifeTracks = Parallel()
    for i in xrange(0, 3):
        knifeDelay = 0.11
        leftTrack = Sequence()
        leftTrack.append(Wait(1.1))
        leftTrack.append(Wait(i * knifeDelay))
        leftTrack.append(getPropAppearTrack(leftKnives[i], suit, leftPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
        leftTrack.append(getPropThrowTrack(attack, leftKnives[i], hitPointNames=['face'], missPointNames=['miss'], hitDuration=0.3, missDuration=0.3))
        leftKnifeTracks.append(leftTrack)
        rightTrack = Sequence()
        rightTrack.append(Wait(1.1))
        rightTrack.append(Wait(i * knifeDelay))
        rightTrack.append(getPropAppearTrack(rightKnives[i], suit, rightPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
        rightTrack.append(getPropThrowTrack(attack, rightKnives[i], hitPointNames=['face'], missPointNames=['miss'], hitDuration=0.3, missDuration=0.3))
        rightKnifeTracks.append(rightTrack)

    damageAnims = [['slip-backward', 0.01, 0.35]]
    toonTrack = getToonTrack(attack, damageDelay=1.6, splicedDamageAnims=damageAnims, dodgeDelay=0.7, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_glower_power.ogg', delay=1.1, node=suit)
    soundTrack2 = getSoundTrack('ENC_cogfall_apart.ogg', delay=1.5, node=suit)
    suitSpeechTrack = Sequence(Wait(2.5), Func(suit.setChatAbsolute, 'You better watch your back, our next few attacks will be very painful.', CFSpeech | CFTimeout))
    return Parallel(suitTrack, toonTrack, soundTrack, leftKnifeTracks, rightKnifeTracks, explosionTrack, soundTrack2, suitSpeechTrack)


def doHalfWindsor(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    tie = globalPropPool.getProp('half-windsor')
    throwDelay = 2.17
    damageDelay = 3.4
    dodgeDelay = 2.4
    suitTrack = getSuitTrack(attack)
    posPoints = [Point3(0.02, 0.88, 0.48), VBase3(99, -3, -108.2)]
    tiePropTrack = getPropAppearTrack(tie, suit.getRightHand(), posPoints, 0.5, Point3(7, 7, 7), scaleUpTime=0.5)
    tiePropTrack.append(Wait(throwDelay))
    missPoint = __toonMissBehindPoint(toon, parent=battle)
    missPoint.setX(missPoint.getX() - 1.1)
    missPoint.setZ(missPoint.getZ() + 4)
    hitPoint = __toonFacePoint(toon, parent=battle)
    hitPoint.setX(hitPoint.getX() - 1.1)
    hitPoint.setY(hitPoint.getY() - 0.7)
    hitPoint.setZ(hitPoint.getZ() + 0.9)
    tiePropTrack.append(getPropThrowTrack(attack, tie, [hitPoint], [missPoint], hitDuration=0.4, missDuration=0.8, missScaleDown=0.3, parent=battle))
    damageAnims = [['conked',
      0.01,
      0.01,
      0.4], ['cringe', 0.01, 0.7]]
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    return Parallel(suitTrack, toonTrack, tiePropTrack)


def doHeadShrink(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    damageDelay = 2.1
    dodgeDelay = 1.4
    shrinkSpray = BattleParticles.createParticleEffect(file='headShrinkSpray')
    shrinkCloud = BattleParticles.createParticleEffect(file='headShrinkCloud')
    shrinkDrop = BattleParticles.createParticleEffect(file='headShrinkDrop')
    suitTrack = getSuitTrack(attack)
    sprayTrack = getPartTrack(shrinkSpray, 0.3, 1.4, [shrinkSpray, suit, 0])
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
    cloudTrack.append(Wait(1.42))
    cloudTrack.append(Func(battle.movie.needRestoreParticleEffect, shrinkCloud))
    cloudTrack.append(Func(shrinkCloud.start, battle))
    cloudTrack.append(circleTrack)
    cloudTrack.append(circleTrack)
    cloudTrack.append(LerpFunctionInterval(shrinkCloud.setAlphaScale, fromData=1, toData=0, duration=0.7))
    cloudTrack.append(Func(shrinkCloud.cleanup))
    cloudTrack.append(Func(battle.movie.clearRestoreParticleEffect, shrinkCloud))
    shrinkDelay = 0.8
    shrinkDuration = 1.1
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
        shrinkTrack.append(Wait(1.6))
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
    dropTrack = getPartTrack(shrinkDrop, 1.5, 2.5, [shrinkDrop, toon, 0])
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
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    if dmg > 0:
        shrinkSound = globalBattleSoundCache.getSound('SA_head_shrink_only.ogg')
        growSound = globalBattleSoundCache.getSound('SA_head_grow_back_only.ogg')
        soundTrack = Sequence(Wait(2.1), SoundInterval(shrinkSound, duration=2.1, node=suit), Wait(1.6), SoundInterval(growSound, node=suit))
        return Parallel(suitTrack, sprayTrack, cloudTrack, dropTrack, toonTrack, shrinkTrack, soundTrack)
    else:
        return Parallel(suitTrack, sprayTrack, cloudTrack, dropTrack, toonTrack)


def doRolodex(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    rollodex = globalPropPool.getProp('rollodex')
    particleEffect2 = BattleParticles.createParticleEffect(file='rollodexWaterfall')
    particleEffect3 = BattleParticles.createParticleEffect(file='rollodexStream')
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        propPosPoints = [Point3(-0.51, -0.03, -0.1), VBase3(89.673, 2.166, 177.786)]
        propScale = Point3(1.2, 1.2, 1.2)
        partDelay = 2.6
        part2Delay = 2.8
        part3Delay = 3.2
        partDuration = 1.6
        part2Duration = 1.9
        part3Duration = 1
        damageDelay = 3.8
        dodgeDelay = 2.5
    elif suitType == 'b':
        propPosPoints = [Point3(0.12, 0.24, 0.01), VBase3(99.032, 5.973, -179.839)]
        propScale = Point3(0.91, 0.91, 0.91)
        partDelay = 2.9
        part2Delay = 3.1
        part3Delay = 3.5
        partDuration = 1.6
        part2Duration = 1.9
        part3Duration = 1
        damageDelay = 4
        dodgeDelay = 2.5
    elif suitType == 'c':
        propPosPoints = [Point3(-0.51, -0.03, -0.1), VBase3(89.673, 2.166, 177.786)]
        propScale = Point3(1.2, 1.2, 1.2)
        partDelay = 2.3
        part2Delay = 2.8
        part3Delay = 3.2
        partDuration = 1.9
        part2Duration = 1.9
        part3Duration = 1
        damageDelay = 3.5
        dodgeDelay = 2.5
    hitPoint = lambda toon = toon: __toonFacePoint(toon)
    partTrack2 = getPartTrack(particleEffect2, part2Delay, part2Duration, [particleEffect2, suit, 0])
    partTrack3 = getPartTrack(particleEffect3, part3Delay, part3Duration, [particleEffect3, suit, 0])
    suitTrack = getSuitTrack(attack)
    propTrack = getPropTrack(rollodex, suit.getLeftHand(), propPosPoints, 1e-06, 4.7, scaleUpPoint=propScale, anim=0, propName='rollodex', animDuration=0, animStartTime=0)
    toonTrack = getToonTrack(attack, damageDelay, ['conked'], dodgeDelay, ['sidestep'])
    soundTrack = getSoundTrack('SA_rolodex.ogg', delay=2.8, node=suit)
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack, partTrack2, partTrack3)


def doEvilEye(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    eye = globalPropPool.getProp('evil-eye')
    damageDelay = 2.44
    dodgeDelay = 1.64
    suitName = suit.getStyleName()
    if suitName == 'cr':
        posPoints = [Point3(-0.46, 4.85, 5.28), VBase3(-155.0, -20.0, 0.0)]
    elif suitName == 'tf':
        posPoints = [Point3(-0.4, 3.65, 5.01), VBase3(-155.0, -20.0, 0.0)]
    elif suitName == 'le':
        posPoints = [Point3(-0.64, 4.45, 5.91), VBase3(-155.0, -20.0, 0.0)]
    else:
        posPoints = [Point3(-0.4, 6.0, 7.0), VBase3(-155.0, -20.0, 0.0)]
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
    eyeAppearTrack = Sequence(Wait(suitHoldStart), Func(__showProp, eye, suit, posPoints[0], posPoints[1]), LerpScaleInterval(eye, suitHoldDuration, Point3(11, 11, 11)), Wait(eyeHoldDuration * 0.3), LerpHprInterval(eye, 0.02, Point3(205, 40, 0)), Wait(eyeHoldDuration * 0.7), Func(battle.movie.needRestoreRenderProp, eye), Func(eye.wrtReparentTo, battle))
    toonFace = __toonFacePoint(toon, parent=battle)
    if dmg > 0:
        lerpInterval = LerpPosInterval(eye, moveDuration, toonFace)
    else:
        lerpInterval = LerpPosInterval(eye, moveDuration, Point3(toonFace.getX(), toonFace.getY() - 5, toonFace.getZ() - 2))
    eyeMoveTrack = lerpInterval
    eyeRollTrack = LerpHprInterval(eye, moveDuration, Point3(0, 0, -180))
    eyePropTrack = Sequence(eyeAppearTrack, Parallel(eyeMoveTrack, eyeRollTrack), Func(battle.movie.clearRenderProp, eye), Func(MovieUtil.removeProp, eye))
    damageAnims = [['duck',
      0.01,
      0.01,
      1.4], ['cringe', 0.01, 0.3]]
    toonTrack = getToonTrack(attack, splicedDamageAnims=damageAnims, damageDelay=damageDelay, dodgeDelay=dodgeDelay, dodgeAnimNames=['duck'], showDamageExtraTime=1.7, showMissedExtraTime=1.7)
    soundTrack = getSoundTrack('SA_evil_eye.ogg', delay=1.3, node=suit)
    return Parallel(suitTrack, toonTrack, eyePropTrack, soundTrack)


def doPlayHardball(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    ball = globalPropPool.getProp('baseball')
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        suitDelay = 1.09
        damageDelay = 2.76
        dodgeDelay = 1.86
    elif suitType == 'b':
        suitDelay = 1.79
        damageDelay = 3.46
        dodgeDelay = 2.56
    elif suitType == 'c':
        suitDelay = 1.09
        damageDelay = 2.76
        dodgeDelay = 1.86
    suitTrack = getSuitTrack(attack)
    ballPosPoints = [Point3(0.04, 0.03, -0.31), VBase3(-1.152, 86.581, -76.784)]
    propTrack = Sequence(getPropAppearTrack(ball, suit.getRightHand(), ballPosPoints, 0.8, Point3(5, 5, 5), scaleUpTime=0.5))
    propTrack.append(Wait(suitDelay))
    propTrack.append(Func(battle.movie.needRestoreRenderProp, ball))
    propTrack.append(Func(ball.wrtReparentTo, battle))
    toonPos = toon.getPos(battle)
    x = toonPos.getX()
    y = toonPos.getY()
    z = toonPos.getZ()
    z = z + 0.2
    if dmg > 0:
        propTrack.append(LerpPosInterval(ball, 0.5, __toonFacePoint(toon, parent=battle)))
        propTrack.append(LerpPosInterval(ball, 0.5, Point3(x, y + 3, z)))
        propTrack.append(LerpPosInterval(ball, 0.4, Point3(x, y + 5, z + 2)))
        propTrack.append(LerpPosInterval(ball, 0.3, Point3(x, y + 6, z)))
        propTrack.append(LerpPosInterval(ball, 0.1, Point3(x, y + 7, z + 1)))
        propTrack.append(LerpPosInterval(ball, 0.1, Point3(x, y + 8, z)))
        propTrack.append(LerpPosInterval(ball, 0.1, Point3(x, y + 8.5, z + 0.6)))
        propTrack.append(LerpPosInterval(ball, 0.1, Point3(x, y + 9, z + 0.2)))
        propTrack.append(Wait(0.4))
        soundTrack = getSoundTrack('SA_hardball_impact_only.ogg', delay=2.8, node=suit)
    else:
        propTrack.append(LerpPosInterval(ball, 0.5, Point3(x, y + 2, z)))
        propTrack.append(LerpPosInterval(ball, 0.4, Point3(x, y - 1, z + 2)))
        propTrack.append(LerpPosInterval(ball, 0.3, Point3(x, y - 3, z)))
        propTrack.append(LerpPosInterval(ball, 0.1, Point3(x, y - 4, z + 1)))
        propTrack.append(LerpPosInterval(ball, 0.1, Point3(x, y - 5, z)))
        propTrack.append(LerpPosInterval(ball, 0.1, Point3(x, y - 5.5, z + 0.6)))
        propTrack.append(LerpPosInterval(ball, 0.1, Point3(x, y - 6, z + 0.2)))
        propTrack.append(Wait(0.4))
        soundTrack = getSoundTrack('SA_hardball.ogg', delay=3.1, node=suit)
    propTrack.append(LerpScaleInterval(ball, 0.3, MovieUtil.PNT3_NEARZERO))
    propTrack.append(Func(MovieUtil.removeProp, ball))
    propTrack.append(Func(battle.movie.clearRenderProp, ball))
    damageAnims = [['conked',
      damageDelay,
      0.01,
      0.5], ['slip-backward', 0.01, 0.7]]
    toonTrack = getToonTrack(attack, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'], showDamageExtraTime=3.9)
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack)


def doPowerTie(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    tie = globalPropPool.getProp('power-tie')
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        throwDelay = 2.17
        damageDelay = 3.3
        dodgeDelay = 3.1
    elif suitType == 'b':
        throwDelay = 2.17
        damageDelay = 3.3
        dodgeDelay = 3.1
    elif suitType == 'c':
        throwDelay = 1.45
        damageDelay = 2.61
        dodgeDelay = 2.34
    suitTrack = getSuitTrack(attack)
    posPoints = [Point3(1.16, 0.24, 0.63), VBase3(171.561, 1.745, -163.443)]
    tiePropTrack = Sequence(getPropAppearTrack(tie, suit.getRightHand(), posPoints, 0.5, Point3(3.5, 3.5, 3.5), scaleUpTime=0.5))
    tiePropTrack.append(Wait(throwDelay))
    tiePropTrack.append(Func(tie.setBillboardPointEye))
    tiePropTrack.append(getPropThrowTrack(attack, tie, [__toonFacePoint(toon)], [__toonGroundPoint(attack, toon, 0.1)], hitDuration=0.4, missDuration=0.8))
    toonTrack = getToonTrack(attack, damageDelay, ['conked'], dodgeDelay, ['sidestep'])
    throwSound = getSoundTrack('SA_powertie_throw.ogg', delay=2.3, node=suit)
    if dmg > 0:
        hitSound = getSoundTrack('SA_powertie_impact.ogg', delay=2.9, node=suit)
        return Parallel(suitTrack, toonTrack, tiePropTrack, throwSound, hitSound)
    else:
        return Parallel(suitTrack, toonTrack, tiePropTrack, throwSound)


def doDoubleTalk(attack):
    suit = attack['suit']
    battle = attack['battle']
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect('DoubleTalkLeft')
    particleEffect2 = BattleParticles.createParticleEffect('DoubleTalkRight')
    BattleParticles.setEffectTexture(particleEffect, 'doubletalk-double', color=Vec4(0, 1.0, 0.0, 1))
    BattleParticles.setEffectTexture(particleEffect2, 'doubletalk-good', color=Vec4(0, 1.0, 0.0, 1))
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        partDelay = 3.3
        damageDelay = 3.5
        dodgeDelay = 3.3
    elif suitType == 'b':
        partDelay = 3.3
        damageDelay = 3.5
        dodgeDelay = 3.3
    elif suitType == 'c':
        partDelay = 3.3
        damageDelay = 3.5
        dodgeDelay = 3.3
    suitTrack = getSuitTrack(attack)
    partTrack = getPartTrack(particleEffect, partDelay, 1.8, [particleEffect, suit, 0])
    partTrack2 = getPartTrack(particleEffect2, partDelay, 1.8, [particleEffect2, suit, 0])
    damageAnims = [['duck',
      0.01,
      0.4,
      1.05], ['cringe', 1e-06, 0.8]]
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, splicedDodgeAnims=[['duck', 0.01, 1.4]], showMissedExtraTime=0.9, showDamageExtraTime=0.8)
    soundTrack = getSoundTrack('SA_filibuster.ogg', delay=2.5, node=suit)
    return Parallel(suitTrack, toonTrack, partTrack, partTrack2, soundTrack)


def doFreezeAssets(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    BattleParticles.loadParticles()
    snowEffect = BattleParticles.createParticleEffect('FreezeAssets')
    BattleParticles.setEffectTexture(snowEffect, 'snow-particle')
    cloud = globalPropPool.getProp('stormcloud')
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        partDelay = 0.2
        damageDelay = 3.5
        dodgeDelay = 2.3
    elif suitType == 'b':
        partDelay = 0.2
        damageDelay = 3.5
        dodgeDelay = 2.3
    elif suitType == 'c':
        partDelay = 0.2
        damageDelay = 3.5
        dodgeDelay = 2.3
    suitTrack = getSuitTrack(attack, delay=0.9)
    initialCloudHeight = suit.height + 3
    cloudPosPoints = [Point3(0, 3, initialCloudHeight), MovieUtil.PNT3_ZERO]
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
    cloudPropTrack.append(ParticleInterval(snowEffect, cloud, worldRelative=0, duration=2.1, cleanup=True))
    cloudPropTrack.append(Wait(0.4))
    cloudPropTrack.append(LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO))
    cloudPropTrack.append(Func(MovieUtil.removeProp, cloud))
    cloudPropTrack.append(Func(battle.movie.clearRenderProp, cloud))
    damageAnims = [['cringe',
      0.01,
      0.4,
      0.8], ['duck', 0.01, 1.6]]
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'], showMissedExtraTime=1.2)
    return Parallel(suitTrack, toonTrack, cloudPropTrack)


def doHotAir(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    BattleParticles.loadParticles()
    sprayEffect = BattleParticles.createParticleEffect('HotAir')
    baseFlameEffect = BattleParticles.createParticleEffect(file='firedBaseFlame')
    flameEffect = BattleParticles.createParticleEffect('FiredFlame')
    flecksEffect = BattleParticles.createParticleEffect('SpriteFiredFlecks')
    BattleParticles.setEffectTexture(sprayEffect, 'fire')
    BattleParticles.setEffectTexture(baseFlameEffect, 'fire')
    BattleParticles.setEffectTexture(flameEffect, 'fire')
    BattleParticles.setEffectTexture(flecksEffect, 'roll-o-dex', color=Vec4(0.95, 0.95, 0.0, 1))
    sprayDelay = 1.3
    flameDelay = 3.2
    flameDuration = 2.6
    flecksDelay = flameDelay + 0.8
    flecksDuration = flameDuration - 0.8
    damageDelay = 3.6
    dodgeDelay = 2.0
    suitTrack = getSuitTrack(attack)
    sprayTrack = getPartTrack(sprayEffect, sprayDelay, 2.3, [sprayEffect, suit, 0])
    baseFlameTrack = getPartTrack(baseFlameEffect, flameDelay, flameDuration, [baseFlameEffect, toon, 0])
    flameTrack = getPartTrack(flameEffect, flameDelay, flameDuration, [flameEffect, toon, 0])
    flecksTrack = getPartTrack(flecksEffect, flecksDelay, flecksDuration, [flecksEffect, toon, 0])

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
        colorTrack.append(Wait(4.0))
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
     0.01,
     0.4,
     1.2])
    damageAnims.append(['slip-forward', 0.01, 1.0])
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_hot_air.ogg', delay=1.6, node=suit)
    if dmg > 0:
        return Parallel(suitTrack, toonTrack, sprayTrack, soundTrack, baseFlameTrack, flameTrack, flecksTrack, colorTrack)
    else:
        return Parallel(suitTrack, toonTrack, sprayTrack, soundTrack)


def doPickPocket(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target['hp']
    bill = globalPropPool.getProp('1dollar')
    suitTrack = getSuitTrack(attack)
    billPosPoints = [Point3(-0.01, 0.45, -0.25), VBase3(136.424, -46.434, -129.712)]
    billPropTrack = getPropTrack(bill, suit.getRightHand(), billPosPoints, 0.6, 0.55, scaleUpPoint=Point3(1.41, 1.41, 1.41))
    toonTrack = getToonTrack(attack, 0.6, ['cringe'], 0.01, ['sidestep'])
    multiTrackList = Parallel(suitTrack, toonTrack)
    if dmg > 0:
        soundTrack = getSoundTrack('SA_pick_pocket.ogg', delay=0.2, node=suit)
        multiTrackList.append(billPropTrack)
        multiTrackList.append(soundTrack)
    return multiTrackList
	
def doCigarSmoke(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    if suit.dna.name == 'tld':
        return doHeadHonchoCigarSmoke(attack)
    elif suit.dna.name == 'ffm':
        return doFirestarterCigarSmoke(attack)
    else:
        pass
    BattleParticles.loadParticles()
    smoke = BattleParticles.createParticleEffect('Smoke')
    BattleParticles.setEffectTexture(smoke, 'snow-particle')
    cigar = globalPropPool.getProp('cigar')
    suitTrack = getSuitTrack(attack)
    cigarPosPoints = [Point3(-0.05, -0.2, -0.25), VBase3(180.0, 0.0, 0.0)]
    cigarPropTrack = getPropTrack(cigar, suit.getRightHand(), cigarPosPoints, 0.6, 3.6, scaleUpPoint=Point3(6.0, 6.0, 6.0))
    toonTrack = getToonTrack(attack, 3.55, ['cringe'], 3.0, ['sidestep'])
    multiTrackList = Parallel(suitTrack, toonTrack)
    smokeTrack = getPartTrack(smoke, 3.45, 1.5, [smoke, suit, 0])
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

def doFilibuster(attack):
    suit = attack['suit']
    target = attack['target']
    dmg = target['hp']
    battle = attack['battle']
    BattleParticles.loadParticles()
    sprayEffect = BattleParticles.createParticleEffect(file='filibusterSpray')
    sprayEffect2 = BattleParticles.createParticleEffect(file='filibusterSpray')
    sprayEffect3 = BattleParticles.createParticleEffect(file='filibusterSpray')
    sprayEffect4 = BattleParticles.createParticleEffect(file='filibusterSpray')
    color = Vec4(0.4, 0, 0, 1)
    BattleParticles.setEffectTexture(sprayEffect, 'filibuster-cut', color=color)
    BattleParticles.setEffectTexture(sprayEffect2, 'filibuster-fiscal', color=color)
    BattleParticles.setEffectTexture(sprayEffect3, 'filibuster-impeach', color=color)
    BattleParticles.setEffectTexture(sprayEffect4, 'filibuster-inc', color=color)
    partDelay = 1.3
    partDuration = 1.15
    damageDelay = 2.45
    dodgeDelay = 1.7
    suitTrack = getSuitTrack(attack)
    sprayTrack = getPartTrack(sprayEffect, partDelay, partDuration, [sprayEffect, suit, 0])
    sprayTrack2 = getPartTrack(sprayEffect2, partDelay + 0.8, partDuration, [sprayEffect2, suit, 0])
    sprayTrack3 = getPartTrack(sprayEffect3, partDelay + 1.6, partDuration, [sprayEffect3, suit, 0])
    sprayTrack4 = getPartTrack(sprayEffect4, partDelay + 2.4, partDuration, [sprayEffect4, suit, 0])
    damageAnims = []
    for i in xrange(0, 4):
        damageAnims.append(['cringe',
         1e-05,
         0.3,
         0.8])

    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_filibuster.ogg', delay=1.1, node=suit)
    if dmg > 0:
        return Parallel(suitTrack, toonTrack, soundTrack, sprayTrack, sprayTrack2, sprayTrack3, sprayTrack4)
    else:
        return Parallel(suitTrack, toonTrack, soundTrack, sprayTrack, sprayTrack2, sprayTrack3)


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
    if suitType == 'a':
        partDelay = 1.3
        damageDelay = 1.8
        dodgeDelay = 1.1
    elif suitType == 'b':
        partDelay = 1.3
        damageDelay = 2.5
        dodgeDelay = 1.8
    elif suitType == 'c':
        partDelay = 1.3
        damageDelay = partDelay + 1.4
        dodgeDelay = 0.9
    suitTrack = getSuitTrack(attack)
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
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.9, showDamageExtraTime=1.1)
    return Parallel(suitTrack, toonTrack, upperPartTracks, lowerPartTracks)


def doQuake(attack):
    suit = attack['suit']
    suitTrack = getSuitAnimTrack(attack)
    damageAnims = [['slip-forward'], ['slip-forward', 0.01]]
    dodgeAnims = [['jump'], ['jump', 0.01], ['jump', 0.01]]
    soundTrack = getSoundTrack('SA_quake.ogg', node=suit)
    toonTracks = getToonTracks(attack, damageDelay=1.8, splicedDamageAnims=damageAnims, dodgeDelay=1.1, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=2.8, showDamageExtraTime=1.1)
    return Parallel(suitTrack, toonTracks, soundTrack)

def doQuakeEnraged(attack):
    tauntIndex = attack['taunt']
    taunt = random.choice(
        ["You're on shaky ground now!", "Hey, what's shakin'? You!", "Here it comes, it's the big one!"])
    suit = attack['suit']
    suitTrack = Sequence(ActorInterval(suit, 'quick-jump'))
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))

    damageAnims = [['slip-forward'], ['slip-forward', 0.01]]
    dodgeAnims = [['jump'], ['jump', 0.01], ['jump', 0.01]]
    soundTrack = getSoundTrack('SA_quake.ogg', node=suit)
    suitTrack.append(doEnraged(attack))
    toonTracks = getToonTracks(attack, damageDelay=1.8, splicedDamageAnims=damageAnims, dodgeDelay=1.1, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=2.8, showDamageExtraTime=1.1)
    return Parallel(suitTrack, toonTracks, tauntInterval, soundTrack)

def doShieldsUp(attack):
    tauntIndex = attack['taunt']
    taunt = random.choice(["You're on shaky ground now!", "Hey, what's shakin'? You!", "Here it comes, it's the big one!"])
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    dmg = (attack['target'][0]['hp']) * len(battle.activeToons)
    suit.setHealthForMe(int(suit.currHP + (dmg * 2)))
    selfDamageTrack = Sequence(Wait(7), Func(suit.showHpText, +(dmg * 2)), Func(suit.updateHealthBar, 0))
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout), Wait(6.0), Func(suit.setChatAbsolute, 'Is this the best you toons can do?', CFSpeech | CFTimeout))
    suitTrack = Sequence(ActorInterval(suit, 'quick-jump'), ActorInterval(suit, 'defense'))
    damageAnims = [['slip-forward'], ['slip-forward', 0.01]]
    dodgeAnims = [['jump'], ['jump', 0.01], ['jump', 0.01]]
    soundTrack = getSoundTrack('SA_quake.ogg', node=suit)
    soundTrack2 = getSoundTrack('SA_defense.ogg', delay=6.0, node=suit)
    soundTrack3 = getSoundTrack('LB_toonup.ogg', delay=7.0, node=suit)
    toonTracks = getToonTracks(attack, damageDelay=1.8, splicedDamageAnims=damageAnims, dodgeDelay=1.1, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=2.8, showDamageExtraTime=1.1)
    return Parallel(suitTrack, toonTracks, tauntInterval, soundTrack, soundTrack2, soundTrack3, selfDamageTrack)

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
    toonTracks = getToonTracks(attack, damageDelay=1.1, splicedDamageAnims=damageAnims, dodgeDelay=0.7, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=2.8, showDamageExtraTime=1.1)
    return Parallel(suitTrack, toonTracks)

def doBash(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt(attack['name'], tauntIndex)
    tauntInterval = Sequence(Wait(2.1), Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(Wait(2.1), ActorInterval(suit, attack['animName']))
    suitPos = suit.getPos(battle)
    cagePropTracks = Parallel()
    cage = loader.loadModel('phase_3.5/models/modules/desk_only')
    cagePos = [Point3(suitPos.getX() - 3, 3, 0), suit.getHpr(battle)]
    cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, 0.01, scaleUpPoint=Point3(1.5), scaleUpTime=2.1),
            Parallel(
                cage.posInterval(0.75, Point3(suitPos.getX() - 3, 3, 0), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/asfhdfha.ogg'), duration=0.75, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/asfhafhsdh.ogg'), node=cage),
            Wait(2.0),
            LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0),
            Func(MovieUtil.removeProp, cage)
        )

    cagePropTracks.append(cagePropTrack)
    soundTrack = getSoundTrack('tt_s_ara_cmg_itemHitsFloor.ogg', delay=2.5, node=suit)
    damageAnims = [['slip-forward'], ['slip-forward', 0.01]]
    dodgeAnims = [['jump'], ['jump', 0.01]]
    toonTracks = getToonTracks(attack, damageDelay=2.5, splicedDamageAnims=damageAnims, dodgeDelay=2.5, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=2.8, showDamageExtraTime=2.5)
    return Parallel(suitTrack, tauntInterval, cagePropTracks, toonTracks, soundTrack)

def doDataCorruption(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt(attack['name'], tauntIndex)
    tauntInterval = Sequence(Wait(2.1), Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(Wait(2.1), ActorInterval(suit, attack['animName']))
    suitPos = suit.getPos(battle)
    cagePropTracks = Parallel()
    cage = loader.loadModel('phase_3.5/models/modules/desk_only')
    cagePos = [Point3(suitPos.getX() - 3, 3, 0), suit.getHpr(battle)]
    cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, 0.01, scaleUpPoint=Point3(1.5), scaleUpTime=2.1),
            Parallel(
                cage.posInterval(0.75, Point3(suitPos.getX() - 3, 3, 0), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/asfhdfha.ogg'), duration=0.75, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/asfhafhsdh.ogg'), node=cage),
            Wait(2.0),
            LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0),
            Func(MovieUtil.removeProp, cage)
        )

    cagePropTracks.append(cagePropTrack)
    damageAnims = [['cringe'], ['cringe', 0.01]]
    dodgeAnims = [['jump'], ['jump', 0.01]]
    toonTracks = getToonTracks(attack, damageDelay=2.5, splicedDamageAnims=damageAnims, dodgeDelay=2.5, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=2.8, showDamageExtraTime=2.5)
    oldcolor = render.getColorScale()
    lightingTrack = Sequence(Wait(1), LerpColorScaleInterval(render, 0.5, (0, 0.992, 1, 1)),
                             LerpColorScaleInterval(render, 2.5, (0, 0.992, 1, 1)),
                             LerpColorScaleInterval(render, 1, (oldcolor)))
    return Parallel(suitTrack, tauntInterval, cagePropTracks, toonTracks, lightingTrack)


def doEnraged(attack):
    suit = attack['suit']
    tauntIndex = attack['taunt']
    name = attack['id']
    taunt = getAttackTaunt(attack['name'], tauntIndex)
    damageAnims = [['slip-forward'], ['slip-forward', 0.01]]
    dodgeAnims = [['jump'], ['jump', 0.01]]
    toonTracks = getToonTracks(attack, damageDelay=1.1, splicedDamageAnims=damageAnims, dodgeDelay=0.7, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=2.8, showDamageExtraTime=1.1)
    soundTrack = getSoundTrack('SA_rage.ogg', delay=1.5, node=suit)
    suitTrack = Sequence(Wait(1.5), ActorInterval(suit, attack['animName'], duration=3.0), Func(suit.loop, 'neutral-enraged'), Wait(3.0), Func(suit.setChatAbsolute, "I'll show you who the 'real' goat is, toons!", CFSpeech | CFTimeout))
    headInterval = Sequence(Wait(1.5), MovieUtil.createSuitEnragedInterval(suit, 0))
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    return Parallel(suitTrack, soundTrack, headInterval, tauntInterval)


def doHangUp(attack):
    suit = attack['suit']
    battle = attack['battle']
    phone = globalPropPool.getProp('phone')
    receiver = globalPropPool.getProp('receiver')
    suitTrack = getSuitTrack(attack)
    suitName = suit.getStyleName()
    if suitName == 'tf':
        phonePosPoints = [Point3(-0.23, 0.01, -0.26), VBase3(5.939, 2.763, -177.591)]
        receiverPosPoints = [Point3(-0.13, -0.07, -0.06), VBase3(-1.854, 2.434, -177.579)]
        receiverAdjustScale = Point3(0.8, 0.8, 0.8)
        pickupDelay = 0.44
        dialDuration = 3.07
        finalPhoneDelay = 0.01
        scaleUpPoint = Point3(0.75, 0.75, 0.75)
    else:
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

def doVoicemail(attack):
    suit = attack['suit']
    battle = attack['battle']
    phone = globalPropPool.getProp('phone')
    receiver = globalPropPool.getProp('receiver')
    suitTrack = getSuitTrack(attack)
    suitName = suit.getStyleName()
    if suitName == 'tf':
        phonePosPoints = [Point3(-0.23, 0.01, -0.26), VBase3(5.939, 2.763, -177.591)]
        receiverPosPoints = [Point3(-0.13, -0.07, -0.06), VBase3(-1.854, 2.434, -177.579)]
        receiverAdjustScale = Point3(0.8, 0.8, 0.8)
        pickupDelay = 0.44
        dialDuration = 3.07
        finalPhoneDelay = 0.01
        scaleUpPoint = Point3(0.75, 0.75, 0.75)
    else:
        phonePosPoints = [Point3(0.23, 0.17, -0.11), VBase3(5.939, 2.763, -177.591)]
        receiverPosPoints = [Point3(0.23, 0.17, -0.11), VBase3(5.939, 2.763, -177.591)]
        receiverAdjustScale = MovieUtil.PNT3_ONE
        pickupDelay = 0.74
        dialDuration = 3.07
        finalPhoneDelay = 0.69
        scaleUpPoint = MovieUtil.PNT3_ONE
    propTrack = Sequence(Wait(0.3), Func(__showProp, phone, suit.getLeftHand(), phonePosPoints[0], phonePosPoints[1]), Func(__showProp, receiver, suit.getLeftHand(), receiverPosPoints[0], receiverPosPoints[1]), LerpScaleInterval(phone, 0.5, scaleUpPoint, MovieUtil.PNT3_NEARZERO), Wait(pickupDelay), Func(receiver.wrtReparentTo, suit.getRightHand()), LerpScaleInterval(receiver, 0.01, receiverAdjustScale), LerpPosHprInterval(receiver, 0.0001, Point3(-0.53, 0.21, -0.54), VBase3(-99.49, -35.27, 1.84)), Wait(dialDuration), Func(receiver.wrtReparentTo, phone), Wait(finalPhoneDelay), LerpScaleInterval(phone, 0.5, MovieUtil.PNT3_NEARZERO), Func(MovieUtil.removeProps, [receiver, phone]))
    #toonTrack = getToonTrack(attack, 5.5, ['slip-backward'], 4.7, ['jump'])
    suitSpeechTrack = Sequence(Wait(3.0), Func(suit.setChatAbsolute, "Guess you'll have to attack somebody else this turn, I'm taking a break from this nonsense.", CFSpeech | CFTimeout))
    soundTrack = getSoundTrack('SA_hangup.ogg', delay=1.3, node=suit)
    notifyTrack = Func(suit.showHpTextWhite, 'IMMUNE!')
    return Parallel(suitTrack, propTrack, soundTrack, suitSpeechTrack, notifyTrack)

def doWiretapped(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    phone = globalPropPool.getProp('phone')
    receiver = globalPropPool.getProp('receiver')
    suitTrack = getSuitAnimTrack(attack)
    suitName = suit.getStyleName()
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    gearPoint = Point3(suitPos.getX(), suitPos.getY() - 10, suitPos.getZ() + suit.height - 0.2)
    explosionTrack = Sequence()
    explosionTrack.append(Wait(3.5))
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
        explodeTrack.append(Wait(3.5))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodePosPoints, 1e-06, Point3(1.7, 1.7, 1.7), scaleUpTime=0.1))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodePosPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodeHprPoints, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodeHprPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.1))
        explodeTracks.append(explodeTrack)
    if suitName == 'tf':
        phonePosPoints = [Point3(-0.23, 0.01, -0.26), VBase3(5.939, 2.763, -177.591)]
        receiverPosPoints = [Point3(-0.13, -0.07, -0.06), VBase3(-1.854, 2.434, -177.579)]
        receiverAdjustScale = Point3(0.8, 0.8, 0.8)
        pickupDelay = 0.44
        dialDuration = 3.07
        finalPhoneDelay = 0.01
        scaleUpPoint = Point3(0.75, 0.75, 0.75)
    else:
        phonePosPoints = [Point3(0.23, 0.17, -0.11), VBase3(5.939, 2.763, -177.591)]
        receiverPosPoints = [Point3(0.23, 0.17, -0.11), VBase3(5.939, 2.763, -177.591)]
        receiverAdjustScale = MovieUtil.PNT3_ONE
        pickupDelay = 0.74
        dialDuration = 3.07
        finalPhoneDelay = 0.69
        scaleUpPoint = MovieUtil.PNT3_ONE
    propTrack = Sequence(Wait(0.3), Func(__showProp, phone, suit.getLeftHand(), phonePosPoints[0], phonePosPoints[1]), Func(__showProp, receiver, suit.getLeftHand(), receiverPosPoints[0], receiverPosPoints[1]), LerpScaleInterval(phone, 0.5, scaleUpPoint, MovieUtil.PNT3_NEARZERO), Wait(pickupDelay), Func(receiver.wrtReparentTo, suit.getRightHand()), LerpScaleInterval(receiver, 0.01, receiverAdjustScale), LerpPosHprInterval(receiver, 0.0001, Point3(-0.53, 0.21, -0.54), VBase3(-99.49, -35.27, 1.84)), Wait(dialDuration), Func(receiver.wrtReparentTo, phone), Wait(finalPhoneDelay), LerpScaleInterval(phone, 0.5, MovieUtil.PNT3_NEARZERO), Func(MovieUtil.removeProps, [receiver, phone]))
    toonTracks = getToonTracks(attack, 3.5, ['slip-backward'], 4.7, ['jump'])
    suitSpeechTrack = Sequence(Wait(4.0), Func(suit.setChatAbsolute, "I've tapped into your line, your health is now mine.", CFSpeech | CFTimeout))
    soundTrack = getSoundTrack('SA_hangup.ogg', delay=1.3, node=suit)
    soundTrack1 = getSoundTrack('ENC_cogfall_apart.ogg', delay=3.5, node=suit)
    return Parallel(suitTrack, propTrack, soundTrack, soundTrack1, suitSpeechTrack, toonTracks, explodeTracks, explosionTrack)


def doRedTape(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    tape = globalPropPool.getProp('redtape')
    tubes = []
    for i in xrange(0, 3):
        tubes.append(globalPropPool.getProp('redtape-tube'))

    suitTrack = getSuitTrack(attack)
    suitName = suit.getStyleName()
    if suitName == 'tf' or suitName == 'nc':
        tapePosPoints = [Point3(-0.24, 0.09, -0.38), VBase3(-1.152, 86.581, -76.784)]
    else:
        tapePosPoints = [Point3(0.24, 0.09, -0.38), VBase3(-1.152, 86.581, -76.784)]
    tapeScaleUpPoint = Point3(0.9, 0.9, 0.24)
    propTrack = Sequence(getPropAppearTrack(tape, suit.getRightHand(), tapePosPoints, 0.8, tapeScaleUpPoint, scaleUpTime=0.5))
    propTrack.append(Wait(1.73))
    hitPoint = lambda toon = toon: __toonTorsoPoint(toon)
    propTrack.append(getPropThrowTrack(attack, tape, [hitPoint], [__toonGroundPoint(attack, toon, 0.7)]))
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
        tubeTracks.append(getPropTrack(tubes[partNum], nextPart, tubePosPoints, 3.25, 3.17, scaleUpPoint=scaleUpPoint))

    tubeTracks.append(Func(battle.movie.clearRestoreHips))
    toonTrack = getToonTrack(attack, 3.4, ['struggle'], 2.8, ['jump'])
    soundTrack = getSoundTrack('SA_red_tape.ogg', delay=2.9, node=suit)
    if dmg > 0:
        return Parallel(suitTrack, toonTrack, propTrack, soundTrack, tubeTracks)
    else:
        return Parallel(suitTrack, toonTrack, propTrack, soundTrack)

def doLegalBindings(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    tauntIndex = attack['taunt']

    bindingsTrack = ActorInterval(suit, 'throw-object')
    pbpText = attack['playByPlayText']
    pbpDc = PlayByPlayText.PlayByPlayText()

    pbpDesc = pbpDc.getShowIntervalDesc('The Case Manager has legally bound this toon to\ntake extra damage for 2 turns!', 3.5)
    pbpTrack = pbpText.getShowIntervalCheat('Legal Bindings!', 3.5)
    taunt = random.choice(['Hrm...', 'Hmph...', 'Hm, hm...', 'Hrnhmpf...'])
    tape = globalPropPool.getProp('redtape')
    tauntTrack = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    tubes = []
    for i in xrange(0, 3):
        tubes.append(globalPropPool.getProp('redtape-tube'))

    suitTrack = Parallel(bindingsTrack, tauntTrack)
    suitName = suit.getStyleName()
    if suitName == 'tf' or suitName == 'nc':
        tapePosPoints = [Point3(-0.24, 0.09, -0.38), VBase3(-1.152, 86.581, -76.784)]
    else:
        tapePosPoints = [Point3(0.24, 0.09, -0.38), VBase3(-1.152, 86.581, -76.784)]
    tapeScaleUpPoint = Point3(0.9, 0.9, 0.24)
    propTrack = Sequence(getPropAppearTrack(tape, suit.getRightHand(), tapePosPoints, 0.8, tapeScaleUpPoint, scaleUpTime=0.5))
    propTrack.append(Wait(1.73))
    hitPoint = lambda toon = toon: __toonTorsoPoint(toon)
    propTrack.append(getPropThrowTrack(attack, tape, [hitPoint], [__toonGroundPoint(attack, toon, 0.7)]))
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
        tubeTracks.append(getPropTrack(tubes[partNum], nextPart, tubePosPoints, 3.25, 3.17, scaleUpPoint=scaleUpPoint))

    tubeTracks.append(Func(battle.movie.clearRestoreHips))
    toonTrack = getToonTrack(attack, 3.4, ['struggle'], 3.4, ['struggle'])
    notifyTrack = Sequence(Wait(4.0), Func(toon.showHpTextWhite, "LEGALLY BOUND!", 10))
    soundTrack = getSoundTrack('SA_red_tape.ogg', delay=2.9, node=suit)
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack, tubeTracks, notifyTrack)


def doParadigmShift(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1

    damageDelay = 1.95
    dodgeDelay = 0.95
    sprayEffect = BattleParticles.createParticleEffect('ShiftSpray')
    suitName = suit.getStyleName()
    sprayEffect.setPos(Point3(-5.2, 4.6, 2.7))
    suitTrack = getSuitAnimTrack(attack)
    sprayTrack = getPartTrack(sprayEffect, 1.0, 1.9, [sprayEffect, suit, 0])
    liftTracks = Parallel()
    toonRiseTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        if dmg > 0:
            liftEffect = BattleParticles.createParticleEffect('ShiftLift')
            liftEffect.setPos(toon.getPos(battle))
            liftEffect.setZ(liftEffect.getZ() - 1.3)
            liftTracks.append(getPartTrack(liftEffect, 1.1, 4.1, [liftEffect, battle, 0]))
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
    if hitAtleastOneToon == 1:
        soundTrack = getSoundTrack('SA_paradigm_shift.ogg', delay=2.1, node=suit)
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
    suitTrack = getSuitAnimTrack(attack)

    def getPowerTrack(effect, suit = suit, battle = battle):
        partTrack = Sequence(Wait(1.0), Func(battle.movie.needRestoreParticleEffect, effect), Func(effect.start, suit), Wait(0.4), LerpPosInterval(effect, 1.0, Point3(0, 15, 0.4)), LerpFunctionInterval(effect.setAlphaScale, fromData=1, toData=0, duration=0.4), Func(effect.cleanup), Func(battle.movie.clearRestoreParticleEffect, effect))
        return partTrack

    partTrack1 = getPowerTrack(powerBar1)
    partTrack2 = getPowerTrack(powerBar2)
    waterfallTrack = getPartTrack(waterfallEffect, 0.6, 1.3, [waterfallEffect, suit, 0])
    toonTracks = getToonTracks(attack, 1.8, ['slip-forward'], 1.29, ['jump'])
    return Parallel(suitTrack, partTrack1, partTrack2, waterfallTrack, toonTracks)


def getThrowEndPoint(suit, toon, battle, whichBounce):
    pnt = toon.getPos(toon)
    if whichBounce == 'one':
        pnt.setY(pnt[1] + 8)
    elif whichBounce == 'two':
        pnt.setY(pnt[1] + 5)
    elif whichBounce == 'threeHit':
        pnt.setZ(pnt[2] + toon.shoulderHeight + 0.3)
    elif whichBounce == 'threeMiss':
        pass
    elif whichBounce == 'four':
        pnt.setY(pnt[1] - 5)
    return Point3(pnt)


def doBounceCheck(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    battle = attack['battle']
    toon = target['toon']
    dmg = target['hp']
    hitSuit = dmg > 0
    check = globalPropPool.getProp('bounced-check')
    checkPosPoints = [MovieUtil.PNT3_ZERO, VBase3(95.247, 79.025, 88.849)]
    bounce1Point = lambda suit = suit, toon = toon, battle = battle: getThrowEndPoint(suit, toon, battle, 'one')
    bounce2Point = lambda suit = suit, toon = toon, battle = battle: getThrowEndPoint(suit, toon, battle, 'two')
    hit3Point = lambda suit = suit, toon = toon, battle = battle: getThrowEndPoint(suit, toon, battle, 'threeHit')
    miss3Point = lambda suit = suit, toon = toon, battle = battle: getThrowEndPoint(suit, toon, battle, 'threeMiss')
    bounce4Point = lambda suit = suit, toon = toon, battle = battle: getThrowEndPoint(suit, toon, battle, 'four')
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        throwDelay = 2.5
        dodgeDelay = 4.3
        damageDelay = 5.1
    elif suitType == 'b':
        throwDelay = 1.8
        dodgeDelay = 3.6
        damageDelay = 4.4
    elif suitType == 'c':
        throwDelay = 1.8
        dodgeDelay = 3.6
        damageDelay = 4.4
    suitTrack = getSuitTrack(attack)
    checkPropTrack = Sequence(getPropAppearTrack(check, suit.getRightHand(), checkPosPoints, 1e-05, Point3(8.5, 8.5, 8.5), startScale=MovieUtil.PNT3_ONE))
    checkPropTrack.append(Wait(throwDelay))
    checkPropTrack.append(Func(check.wrtReparentTo, toon))
    checkPropTrack.append(Func(check.setHpr, Point3(0, -90, 0)))
    checkPropTrack.append(getThrowTrack(check, bounce1Point, duration=0.5, parent=toon))
    checkPropTrack.append(getThrowTrack(check, bounce2Point, duration=0.9, parent=toon))
    if hitSuit:
        checkPropTrack.append(getThrowTrack(check, hit3Point, duration=0.7, parent=toon))
    else:
        checkPropTrack.append(getThrowTrack(check, miss3Point, duration=0.7, parent=toon))
        checkPropTrack.append(getThrowTrack(check, bounce4Point, duration=0.7, parent=toon))
        checkPropTrack.append(LerpScaleInterval(check, 0.3, MovieUtil.PNT3_NEARZERO))
    checkPropTrack.append(Func(MovieUtil.removeProp, check))
    toonTrack = getToonTrack(attack, damageDelay, ['conked'], dodgeDelay, ['sidestep'])
    soundTracks = Sequence(getSoundTrack('SA_pink_slip.ogg', delay=throwDelay + 0.5, duration=0.6, node=suit), getSoundTrack('SA_pink_slip.ogg', delay=0.4, duration=0.6, node=suit))
    return Parallel(suitTrack, checkPropTrack, toonTrack, soundTracks)


def doWatercooler(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    watercooler = globalPropPool.getProp('watercooler')

    def getCoolerSpout(watercooler = watercooler):
        spout = watercooler.find('**/joint_toSpray')
        return spout.getPos(render)

    hitPoint = lambda toon = toon: __toonFacePoint(toon)
    missPoint = lambda prop = watercooler, toon = toon: __toonMissPoint(prop, toon, 0, parent=render)
    hitSprayTrack = MovieUtil.getSprayTrack(battle, Point4(0.75, 0.75, 1.0, 0.8), getCoolerSpout, hitPoint, 0.2, 0.2, 0.2, horizScale=0.3, vertScale=0.3)
    missSprayTrack = MovieUtil.getSprayTrack(battle, Point4(0.75, 0.75, 1.0, 0.8), getCoolerSpout, missPoint, 0.2, 0.2, 0.2, horizScale=0.3, vertScale=0.3)
    suitTrack = getSuitTrack(attack)
    posPoints = [Point3(0.48, 0.11, -0.92), VBase3(20.403, 33.158, 69.511)]
    propTrack = Sequence(Wait(1.01), Func(__showProp, watercooler, suit.getLeftHand(), posPoints[0], posPoints[1]), LerpScaleInterval(watercooler, 0.5, Point3(1.15, 1.15, 1.15)), Wait(1.6))
    if dmg > 0:
        propTrack.append(hitSprayTrack)
    else:
        propTrack.append(missSprayTrack)
    propTrack += [Wait(0.01), LerpScaleInterval(watercooler, 0.5, MovieUtil.PNT3_NEARZERO), Func(MovieUtil.removeProp, watercooler)]
    splashTrack = Sequence()
    if dmg > 0:

        def prepSplash(splash, targetPoint):
            splash.reparentTo(render)
            splash.setPos(targetPoint)
            scale = splash.getScale()
            splash.setBillboardPointWorld()
            splash.setScale(scale)

        splash = globalPropPool.getProp('splash-from-splat')
        splash.setColor(0.75, 0.75, 1, 0.8)
        splash.setScale(0.3)
        splashTrack = Sequence(Func(battle.movie.needRestoreRenderProp, splash), Wait(3.2), Func(prepSplash, splash, __toonFacePoint(toon)), ActorInterval(splash, 'splash-from-splat'), Func(MovieUtil.removeProp, splash), Func(battle.movie.clearRenderProp, splash))
    toonTrack = getToonTrack(attack, suitTrack.getDuration() - 1.5, ['cringe'], 2.4, ['sidestep'])
    soundTrack = Sequence(Wait(1.1), SoundInterval(globalBattleSoundCache.getSound('SA_watercooler_appear_only.ogg'), node=suit, duration=1.4722), Wait(0.4), SoundInterval(globalBattleSoundCache.getSound('SA_watercooler_spray_only.ogg'), node=suit, duration=2.313))
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack, splashTrack)


def doFired(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    BattleParticles.loadParticles()
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
    suitTrack = getSuitTrack(attack)
    baseFlameTrack = getPartTrack(baseFlameEffect, 1.0, 1.9, [baseFlameEffect, toon, 0])
    flameTrack = getPartTrack(flameEffect, 1.0, 1.9, [flameEffect, toon, 0])
    flecksTrack = getPartTrack(flecksEffect, 1.8, 1.1, [flecksEffect, toon, 0])
    baseFlameSmallTrack = getPartTrack(baseFlameSmall, 1.0, 1.9, [baseFlameSmall, toon, 0])
    flameSmallTrack = getPartTrack(flameSmall, 1.0, 1.9, [flameSmall, toon, 0])
    flecksSmallTrack = getPartTrack(flecksSmall, 1.8, 1.1, [flecksSmall, toon, 0])

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
    damageAnims.extend(getSplicedLerpAnims('slip-forward', 0.31, 0.8, startTime=1.2))
    toonTrack = getToonTrack(attack, damageDelay=1.5, splicedDamageAnims=damageAnims, dodgeDelay=0.3, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_hot_air.ogg', delay=1.0, node=suit)
    if dmg > 0:
        return Parallel(suitTrack, baseFlameTrack, flameTrack, flecksTrack, toonTrack, colorTrack, soundTrack)
    else:
        return Parallel(suitTrack, baseFlameSmallTrack, flameSmallTrack, flecksSmallTrack, toonTrack, soundTrack)


def doAudit(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    calculator = globalPropPool.getProp('calculator')
    BattleParticles.loadParticles()
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
    suitTrack = getSuitTrack(attack)
    partTrack = getPartTrack(particleEffect, 2.1, 1.9, [particleEffect, suit, 0])
    partTrack2 = getPartTrack(particleEffect2, 2.2, 2.0, [particleEffect2, suit, 0])
    partTrack3 = getPartTrack(particleEffect3, 2.3, 2.1, [particleEffect3, suit, 0])
    partTrack4 = getPartTrack(particleEffect4, 2.4, 2.2, [particleEffect4, suit, 0])
    partTrack5 = getPartTrack(particleEffect5, 2.5, 2.3, [particleEffect5, suit, 0])
    suitName = attack['suitName']
    if suitName == 'nc':
        calcPosPoints = [Point3(-0.15, 0.37, 0.03), VBase3(1.352, -6.518, -6.045)]
        calcDuration = 0.76
        scaleUpPoint = Point3(1.1, 1.85, 1.81)
    else:
        calcPosPoints = [Point3(0.35, 0.52, 0.03), VBase3(1.352, -6.518, -6.045)]
        calcDuration = 1.87
        scaleUpPoint = Point3(1.0, 1.37, 1.31)
    calcPropTrack = getPropTrack(calculator, suit.getLeftHand(), calcPosPoints, 1e-06, calcDuration, scaleUpPoint=scaleUpPoint, anim=1, propName='calculator', animStartTime=0.5, animDuration=3.4)
    toonTrack = getToonTrack(attack, 3.2, ['conked'], 0.9, ['duck'], showMissedExtraTime=2.2)
    soundTrack = getSoundTrack('SA_audit.ogg', delay=1.9, node=suit)
    return Parallel(suitTrack, toonTrack, calcPropTrack, soundTrack, partTrack, partTrack2, partTrack3, partTrack4, partTrack5)


def doCalculate(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    calculator = globalPropPool.getProp('calculator')
    BattleParticles.loadParticles()
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
    suitTrack = getSuitTrack(attack)
    partTrack = getPartTrack(particleEffect, 2.1, 1.9, [particleEffect, suit, 0])
    partTrack2 = getPartTrack(particleEffect2, 2.2, 2.0, [particleEffect2, suit, 0])
    partTrack3 = getPartTrack(particleEffect3, 2.3, 2.1, [particleEffect3, suit, 0])
    partTrack4 = getPartTrack(particleEffect4, 2.4, 2.2, [particleEffect4, suit, 0])
    partTrack5 = getPartTrack(particleEffect5, 2.5, 2.3, [particleEffect5, suit, 0])
    suitName = attack['suitName']
    if suitName == 'nc':
        calcPosPoints = [Point3(-0.15, 0.37, 0.03), VBase3(1.352, -6.518, -6.045)]
        calcDuration = 0.76
        scaleUpPoint = Point3(1.1, 1.85, 1.81)
    else:
        calcPosPoints = [Point3(0.35, 0.52, 0.03), VBase3(1.352, -6.518, -6.045)]
        calcDuration = 1.87
        scaleUpPoint = Point3(1.0, 1.37, 1.31)
    calcPropTrack = getPropTrack(calculator, suit.getLeftHand(), calcPosPoints, 1e-06, calcDuration, scaleUpPoint=scaleUpPoint, anim=1, propName='calculator', animStartTime=0.5, animDuration=3.4)
    toonTrack = getToonTrack(attack, 3.2, ['conked'], 1.8, ['sidestep'])
    return Parallel(suitTrack, toonTrack, calcPropTrack, partTrack, partTrack2, partTrack3, partTrack4, partTrack5)


def doTabulate(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    calculator = globalPropPool.getProp('calculator')
    BattleParticles.loadParticles()
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
    suitTrack = getSuitTrack(attack)
    partTrack = getPartTrack(particleEffect, 2.1, 1.9, [particleEffect, suit, 0])
    partTrack2 = getPartTrack(particleEffect2, 2.2, 2.0, [particleEffect2, suit, 0])
    partTrack3 = getPartTrack(particleEffect3, 2.3, 2.1, [particleEffect3, suit, 0])
    partTrack4 = getPartTrack(particleEffect4, 2.4, 2.2, [particleEffect4, suit, 0])
    partTrack5 = getPartTrack(particleEffect5, 2.5, 2.3, [particleEffect5, suit, 0])
    suitName = attack['suitName']
    if suitName == 'nc':
        calcPosPoints = [Point3(-0.15, 0.37, 0.03), VBase3(1.352, -6.518, -6.045)]
        calcDuration = 0.76
        scaleUpPoint = Point3(1.1, 1.85, 1.81)
    else:
        calcPosPoints = [Point3(0.35, 0.52, 0.03), VBase3(1.352, -6.518, -6.045)]
        calcDuration = 1.87
        scaleUpPoint = Point3(1.0, 1.37, 1.31)
    calcPropTrack = getPropTrack(calculator, suit.getLeftHand(), calcPosPoints, 1e-06, calcDuration, scaleUpPoint=scaleUpPoint, anim=1, propName='calculator', animStartTime=0.5, animDuration=3.4)
    toonTrack = getToonTrack(attack, 3.2, ['conked'], 1.8, ['sidestep'])
    return Parallel(suitTrack, toonTrack, calcPropTrack, partTrack, partTrack2, partTrack3, partTrack4, partTrack5)


def doCrunch(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    throwDuration = 3.03
    suitTrack = getSuitTrack(attack)
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
    numberSpillTrack1 = getPartTrack(numberSpill1, 1.1, 2.2, [numberSpill1, suit, 0])
    numberSpillTrack2 = getPartTrack(numberSpill2, 1.5, 1.0, [numberSpill2, suit, 0])
    numberSprayTracks = Parallel()
    numOfNumbers = random.randint(5, 9)
    for i in xrange(0, numOfNumbers - 1):
        nextSpray = BattleParticles.createParticleEffect(file='numberSpray')
        nextTexture = random.choice(numberNames)
        BattleParticles.setEffectTexture(nextSpray, 'audit-' + nextTexture)
        nextStartTime = random.random() * 0.6 + throwDuration
        nextDuration = random.random() * 0.4 + 1.4
        nextSprayTrack = getPartTrack(nextSpray, nextStartTime, nextDuration, [nextSpray, suit, 0])
        numberSprayTracks.append(nextSprayTrack)

    numberTracks = Parallel()
    for i in xrange(0, numOfNumbers):
        texture = random.choice(numberNames)
        next = MovieUtil.copyProp(BattleParticles.getParticle('audit-' + texture))
        next.reparentTo(suit.getRightHand())
        next.setScale(0.01, 0.01, 0.01)
        next.setColor(Vec4(0.0, 0.0, 0.0, 1.0))
        next.setPos(random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3)
        next.setHpr(VBase3(-1.15, 86.58, -76.78))
        numberTrack = Sequence(Wait(0.9), LerpScaleInterval(next, 0.6, MovieUtil.PNT3_ONE), Wait(1.7), Func(MovieUtil.removeProp, next))
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
    toonTrack = getToonTrack(attack, damageDelay=4.7, splicedDamageAnims=damageAnims, dodgeDelay=3.6, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_crunch.ogg', delay=4.7, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, numberSpillTrack1, numberSpillTrack2, numberTracks, numberSprayTracks)


def doLiquidate(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target['hp']
    toon = target['toon']
    BattleParticles.loadParticles()
    rainEffect = BattleParticles.createParticleEffect(file='liquidate')
    rainEffect2 = BattleParticles.createParticleEffect(file='liquidate')
    rainEffect3 = BattleParticles.createParticleEffect(file='liquidate')
    cloud = globalPropPool.getProp('stormcloud')
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        partDelay = 0.2
        damageDelay = 3.5
        dodgeDelay = 2.45
    elif suitType == 'b':
        partDelay = 0.2
        damageDelay = 3.5
        dodgeDelay = 2.45
    elif suitType == 'c':
        partDelay = 0.2
        damageDelay = 3.5
        dodgeDelay = 2.45
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
    damageAnims = [['melt'], ['jump', 1.5, 0.4]]
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_liquidate.ogg', delay=2.0, node=suit)
    if dmg > 0:
        puddle = globalPropPool.getProp('quicksand')
        puddle.setColor(Vec4(0.0, 0.0, 1.0, 1))
        puddle.setHpr(Point3(120, 0, 0))
        puddle.setScale(0.01)
        puddleTrack = Sequence(Func(battle.movie.needRestoreRenderProp, puddle), Wait(damageDelay - 0.7), Func(puddle.reparentTo, battle), Func(puddle.setPos, toon.getPos(battle)), LerpScaleInterval(puddle, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO), Wait(3.2), LerpFunctionInterval(puddle.setAlphaScale, fromData=1, toData=0, duration=0.8), Func(MovieUtil.removeProp, puddle), Func(battle.movie.clearRenderProp, puddle))
        return Parallel(suitTrack, toonTrack, cloudPropTrack, soundTrack, puddleTrack)
    else:
        return Parallel(suitTrack, toonTrack, cloudPropTrack, soundTrack)

def doHeavyRainfall(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    hitAtleastOneToon = 0
    for t in targets:
        toon = t['toon']
        if t['hp'] > 0:
            hitAtleastOneToon = 1
    BattleParticles.loadParticles()
    damageDelay = 1.5
    dodgeDelay = 1.5
    rainEffect = BattleParticles.createParticleEffect(file='liquidate2')
    rainEffect2 = BattleParticles.createParticleEffect(file='liquidate2')
    rainEffect3 = BattleParticles.createParticleEffect(file='liquidate2')
    cloud = globalPropPool.getProp('stormcloud')
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        partDelay = 0.2
        damageDelay = 3.5
        dodgeDelay = 2.45
    elif suitType == 'b':
        partDelay = 0.2
        damageDelay = 3.5
        dodgeDelay = 2.45
    elif suitType == 'c':
        partDelay = 0.2
        damageDelay = 3.5
        dodgeDelay = 2.45
    suitTrack = getSuitAnimTrack(attack)
    suitTrack.append(Parallel(Sequence(Wait(2.0), Func(suit.setChatAbsolute, "The rain is starting to pick up, any gags used in the next round will have a slight damage debuff.", CFSpeech | CFTimeout), Sequence(Wait(2.5)))))
    targetPoint = __toonFacePoint(toon)
    targetPoint.setZ(targetPoint[2] + 3)
    initialCloudHeight = suit.height + 3
    cloudPosPoints = [Point3(0, 0, initialCloudHeight), VBase3(0, 0, 0)]
    cloudPropTrack = Sequence()
    cloudPropTrack.append(Func(cloud.pose, 'stormcloud', 0))
    cloudPropTrack.append(getPropAppearTrack(cloud, suit, cloudPosPoints, 1e-06, Point3(3, 3, 3), scaleUpTime=0.7))
    cloudPropTrack.append(Func(battle.movie.needRestoreRenderProp, cloud))
    cloudPropTrack.append(Func(cloud.wrtReparentTo, render))
    cloudPropTrack.append(Wait(1.1))
    cloudPropTrack.append(LerpPosInterval(cloud, 1, pos=targetPoint))
    cloudPropTrack.append(Wait(partDelay))
    cloudPropTrack.append(Parallel(Sequence(ParticleInterval(rainEffect, cloud, worldRelative=0, duration=4.1, cleanup=True)), Sequence(Wait(0.1), ParticleInterval(rainEffect2, cloud, worldRelative=0, duration=4.0, cleanup=True)), Sequence(Wait(0.1), ParticleInterval(rainEffect3, cloud, worldRelative=0, duration=4.0, cleanup=True)), Sequence(ActorInterval(cloud, 'stormcloud', startTime=3, duration=0.1), ActorInterval(cloud, 'stormcloud', startTime=1, duration=2.3))))
    cloudPropTrack.append(Wait(0.4))
    cloudPropTrack.append(LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO))
    cloudPropTrack.append(Func(MovieUtil.removeProp, cloud))
    cloudPropTrack.append(Func(battle.movie.clearRenderProp, cloud))
    damageAnims = [['melt'], ['jump', 1.5, 0.4]]
    dodgeAnims = []
    dodgeAnims.append(['jump',
                       0.01,
                       0,
                       0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.0, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    animTrack = Sequence(Wait(2), Func(suit.play,'cease'))
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, splicedDodgeAnims=dodgeAnims, showDamageExtraTime=2.7)
    soundTrack1 = getSoundTrack('SA_liquidate.ogg', delay=2.0, node=suit)
    soundTrack2 = getSoundTrack('SA_cease_and_desist.ogg', delay=4.0, node=suit)
    soundTrack = Parallel(soundTrack1, soundTrack2)
    puddle = globalPropPool.getProp('quicksand')
    puddle.setColor(Vec4(0.0, 0.0, 1.0, 1))
    puddle.setHpr(Point3(120, 0, 0))
    puddle.setScale(0.5)
    puddleTrack = Sequence(Func(battle.movie.needRestoreRenderProp, puddle), Wait(damageDelay - 0.7), Func(puddle.reparentTo, battle), Func(puddle.setPos, toon.getPos(battle)), LerpScaleInterval(puddle, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO), Wait(3.2), LerpFunctionInterval(puddle.setAlphaScale, fromData=1, toData=0, duration=0.8), Func(MovieUtil.removeProp, puddle), Func(battle.movie.clearRenderProp, puddle))
    return Parallel(suitTrack, toonTracks, cloudPropTrack, soundTrack, puddleTrack, animTrack)

def doDrowning(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.5
    dodgeDelay = 1.5
    hitAtleastOneToon = 0
    for t in targets:
        toon = t['toon']
        if t['hp'] > 0:
            hitAtleastOneToon = 1
    BattleParticles.loadParticles()
    suitType = getSuitBodyType(attack['suitName'])
    suitTrack = getSuitAnimTrack(attack)
    damageAnims = [['melt'], ['jump', 1.5, 0.4]]
    dodgeAnims = []
    dodgeAnims.append(['jump',
                       0.01,
                       0,
                       0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.0, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    soundTrack = getSoundTrack('SA_liquidate.ogg', delay=1.0, node=suit)
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay,
                               splicedDodgeAnims=dodgeAnims, showDamageExtraTime=1.7)
    puddle = globalPropPool.getProp('quicksand')
    puddle.setColor(Vec4(0.0, 0.0, 1.0, 1))
    puddle.setHpr(Point3(120, 0, 0))
    puddle.setScale(0.01)
    puddleTrack = Sequence(Func(battle.movie.needRestoreRenderProp, puddle), Wait(damageDelay - 0.7), Func(puddle.reparentTo, battle), Func(puddle.setPos, toon.getPos(battle)), LerpScaleInterval(puddle, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO), Wait(3.2), LerpFunctionInterval(puddle.setAlphaScale, fromData=1, toData=0, duration=0.8), Func(MovieUtil.removeProp, puddle), Func(battle.movie.clearRenderProp, puddle))
    return Parallel(suitTrack, toonTracks, soundTrack, puddleTrack)
		
def doAcidRain(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target['hp']
    toon = target['toon']
    BattleParticles.loadParticles()
    rainEffect = BattleParticles.createParticleEffect(file='acidrain')
    rainEffect2 = BattleParticles.createParticleEffect(file='acidrain')
    rainEffect3 = BattleParticles.createParticleEffect(file='acidrain')
    cloud = globalPropPool.getProp('stormcloud')
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        partDelay = 0.2
        damageDelay = 3.5
        dodgeDelay = 2.45
    elif suitType == 'b':
        partDelay = 0.2
        damageDelay = 3.5
        dodgeDelay = 2.45
    elif suitType == 'c':
        partDelay = 0.2
        damageDelay = 3.5
        dodgeDelay = 2.45
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
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    suitDelay = 1.32
    propDelay = 0.6
    throwDuration = 1.5
    paper = globalPropPool.getProp('newspaper')
    suitTrack = getSuitTrack(attack)
    posPoints = [Point3(-0.07, 0.17, -0.13), VBase3(161.867, -33.149, -48.086)]
    paperTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, propDelay, Point3(3, 3, 3), scaleUpTime=0.5))
    paperTrack.append(Wait(suitDelay))
    hitPoint = toon.getPos(battle)
    hitPoint.setX(hitPoint.getX() + 1.2)
    hitPoint.setY(hitPoint.getY() + 1.5)
    if dmg > 0:
        hitPoint.setZ(hitPoint.getZ() + 1.1)
    movePoint = Point3(hitPoint.getX(), hitPoint.getY() - 1.8, hitPoint.getZ() + 0.2)
    paperTrack.append(Func(battle.movie.needRestoreRenderProp, paper))
    paperTrack.append(Func(paper.wrtReparentTo, battle))
    paperTrack.append(getThrowTrack(paper, hitPoint, duration=throwDuration, parent=battle))
    paperTrack.append(Wait(0.6))
    paperTrack.append(LerpPosInterval(paper, 0.4, movePoint))
    spinTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpHprInterval(paper, throwDuration, Point3(-360, 0, 0)))
    sizeTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpScaleInterval(paper, throwDuration, Point3(6, 6, 6)), Wait(0.95), LerpScaleInterval(paper, 0.4, MovieUtil.PNT3_NEARZERO))
    propTrack = Sequence(Parallel(paperTrack, spinTrack, sizeTrack), Func(MovieUtil.removeProp, paper), Func(battle.movie.clearRenderProp, paper))
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
    toonTrack = getToonTrack(attack, damageDelay=3.8, splicedDamageAnims=damageAnims, dodgeDelay=2.4, dodgeAnimNames=['sidestep'], showDamageExtraTime=0.4, showMissedExtraTime=1.3)
    soundTrack = getSoundTrack('SA_crash.ogg', delay=3.9, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, propTrack)


def doBite(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    teeth = globalPropPool.getProp('teeth')
    propDelay = 0.8
    propScaleUpTime = 0.5
    suitDelay = 1.73
    throwDelay = propDelay + propScaleUpTime + suitDelay
    throwDuration = 0.4
    suitTrack = getSuitTrack(attack)
    posPoints = [Point3(-0.05, 0.41, -0.54), VBase3(4.465, -3.563, 51.479)]
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
        hprTrack = Sequence(Wait(throwDelay), LerpHprInterval(teeth, 0.3, Point3(180, 0, 0)), Wait(0.2), LerpHprInterval(teeth, 0.4, Point3(180, -35, 0), startHpr=Point3(180, 0, 0)), Wait(0.6), LerpHprInterval(teeth, 0.1, Point3(180, -75, 0), startHpr=Point3(180, -35, 0)))
        animTrack = Sequence(Wait(throwDelay), ActorInterval(teeth, 'teeth', duration=throwDuration), ActorInterval(teeth, 'teeth', duration=0.3), Func(teeth.pose, 'teeth', 1), Wait(0.7), ActorInterval(teeth, 'teeth', duration=0.9))
        propTrack = Sequence(Parallel(teethAppearTrack, scaleTrack, hprTrack, animTrack), Func(MovieUtil.removeProp, teeth), Func(battle.movie.clearRenderProp, teeth))
    else:
        flyPoint = __toonFacePoint(toon, parent=battle)
        flyPoint.setY(flyPoint.getY() - 7.1)
        teethAppearTrack.append(LerpPosInterval(teeth, throwDuration, pos=flyPoint))
        teethAppearTrack.append(Func(MovieUtil.removeProp, teeth))
        teethAppearTrack.append(Func(battle.movie.clearRenderProp, teeth))
        propTrack = teethAppearTrack
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
    toonTrack = getToonTrack(attack, damageDelay=3.2, splicedDamageAnims=damageAnims, dodgeDelay=2.9, splicedDodgeAnims=dodgeAnims, showDamageExtraTime=2.4)
    soundTrack = getSoundTrack('SA_bite.ogg', delay=2.9, node=suit)
    suitTrack = Sequence(getSuitAnimTrack(attack))
    return Parallel(suitTrack, toonTrack, soundTrack, propTrack)


def doSnap(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    teeth = globalPropPool.getProp('litigator-teeth')
    propDelay = 0.8
    propScaleUpTime = 0.5
    suitDelay = 1.73
    throwDelay = propDelay + propScaleUpTime + suitDelay
    throwDuration = 0.4
    posPoints = [Point3(-0.05, 0.41, -0.54), VBase3(4.465, -3.563, 51.479)]
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
                            LerpHprInterval(teeth, 0.4, Point3(180, -35, 0), startHpr=Point3(180, 0, 0)), Wait(0.6),
                            LerpHprInterval(teeth, 0.1, Point3(0, -35, 0), startHpr=Point3(180, -35, 0)))
        animTrack = Sequence(Wait(throwDelay), ActorInterval(teeth, 'teeth', duration=throwDuration),
                             ActorInterval(teeth, 'teeth', duration=0.3), Func(teeth.pose, 'teeth', 1), Wait(0.7),
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
    toonTrack = getToonTrack(attack, damageDelay=3.2, splicedDamageAnims=damageAnims, dodgeDelay=2.75,
                             splicedDodgeAnims=dodgeAnims, showDamageExtraTime=1.4)
    soundTrack = getSoundTrack('SA_chomp.ogg', delay=2.9, node=suit)
    notifyTrack = Sequence(Wait(6), Func(toon.showHpTextWhite, "VULNERABLE!", 10))
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack.append(Wait(2))
    suitTrack.append(doBayouBashSnap(attack))
    return Parallel(suitTrack, toonTrack, soundTrack, propTrack, notifyTrack)

def doChomp(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    teeth = globalPropPool.getProp('teeth')
    propDelay = 0.8
    propScaleUpTime = 0.5
    suitDelay = 1.73
    throwDelay = propDelay + propScaleUpTime + suitDelay
    throwDuration = 0.4
    suitTrack = getSuitTrack(attack)
    posPoints = [Point3(-0.05, 0.41, -0.54), VBase3(4.465, -3.563, 51.479)]
    teethAppearTrack = Sequence(getPropAppearTrack(teeth, suit.getRightHand(), posPoints, propDelay, Point3(3, 3, 3), scaleUpTime=propScaleUpTime))
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
        scaleTrack = Sequence(Wait(throwDelay), LerpScaleInterval(teeth, throwDuration, Point3(6, 6, 6)), Wait(0.9), LerpScaleInterval(teeth, 0.2, Point3(10, 10, 10)), Wait(1.2), LerpScaleInterval(teeth, 0.3, MovieUtil.PNT3_NEARZERO))
        hprTrack = Sequence(Wait(throwDelay), LerpHprInterval(teeth, 0.3, Point3(180, 0, 0)), Wait(0.2), LerpHprInterval(teeth, 0.4, Point3(180, -35, 0), startHpr=Point3(180, 0, 0)), Wait(0.6), LerpHprInterval(teeth, 0.1, Point3(0, -35, 0), startHpr=Point3(180, -35, 0)))
        animTrack = Sequence(Wait(throwDelay), ActorInterval(teeth, 'teeth', duration=throwDuration), ActorInterval(teeth, 'teeth', duration=0.3), Func(teeth.pose, 'teeth', 1), Wait(0.7), ActorInterval(teeth, 'teeth', duration=0.9))
        propTrack = Sequence(Parallel(teethAppearTrack, scaleTrack, hprTrack, animTrack), Func(MovieUtil.removeProp, teeth), Func(battle.movie.clearRenderProp, teeth))
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
        hprTrack = Sequence(Wait(throwDelay), LerpHprInterval(teeth, 0.3, Point3(180, 0, 0)), Wait(0.5), LerpHprInterval(teeth, 0.4, Point3(80, 0, 0), startHpr=Point3(180, 0, 0)), LerpHprInterval(teeth, 0.8, Point3(-10, 0, 0), startHpr=Point3(80, 0, 0)))
        animTrack = Sequence(Wait(throwDelay), ActorInterval(teeth, 'teeth', duration=3.6))
        propTrack = Sequence(Parallel(teethAppearTrack, hprTrack, animTrack), Func(MovieUtil.removeProp, teeth), Func(battle.movie.clearRenderProp, teeth))
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
    soundTrack = getSoundTrack('SA_chomp.ogg', delay=2.9, node=suit)
    toonTrack = getToonTrack(attack, damageDelay=3.2, splicedDamageAnims=damageAnims, dodgeDelay=2.75, splicedDodgeAnims=dodgeAnims, showDamageExtraTime=1.4)
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack)

def doInject(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    laptop = globalPropPool.getProp('laptop')
    laptopPosPoints = [Point3(0.2, 0, 0), VBase3(0.2, 0, 0)]
    laptopDuration = 2.8
    scaleUpPoint = Point3(1.5, 1.5, 1.5)
    suitTrack = getSuitTrack(attack)
    damageAnims = []
    damageAnims.append(['swim', 0.01, 0.01, 2.8])
    soundTrack = getSoundTrack('SA_keyboard.ogg', delay=1, node=suit)
    calcPropTrack = getPropTrack(laptop, suit.getLeftHand(), laptopPosPoints, 1e-06, laptopDuration, scaleUpPoint=scaleUpPoint, anim=0, propName='laptop', animStartTime=0, animDuration=0)
    toonTrack = getToonTrack(attack, 2.8, splicedDamageAnims=damageAnims, dodgeDelay=2.8, dodgeAnimNames=['jump'])
    return Parallel(suitTrack, toonTrack, soundTrack, calcPropTrack)

def doEvictionNotice(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    paper = globalPropPool.getProp('shredder-paper')
    suitTrack = getSuitTrack(attack)
    posPoints = [Point3(-0.04, 0.15, -1.38), VBase3(10.584, -11.945, 18.316)]
    propTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.8, MovieUtil.PNT3_ONE, scaleUpTime=0.5))
    propTrack.append(Wait(1.73))
    hitPoint = __toonFacePoint(toon, parent=battle)
    hitPoint.setX(hitPoint.getX() - 1.4)
    missPoint = __toonGroundPoint(attack, toon, 0.7, parent=battle)
    missPoint.setX(missPoint.getX() - 1.1)
    propTrack.append(getPropThrowTrack(attack, paper, [hitPoint], [missPoint], parent=battle))
    toonTrack = getToonTrack(attack, 3.4, ['conked'], 2.8, ['jump'])
    return Parallel(suitTrack, toonTrack, propTrack)


def doInsurancePlan(attack):
    if attack['suitName'] == 'csm':
        suitTrack = doCaseInsurancePlan(attack)
    elif attack['suitName'] == 'cm':
        suitTrack = doCaseInsurancePlan(attack)
    else:
        suitTrack = doOtherInsurancePlan(attack)
    return suitTrack


def doCaseInsurancePlan(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    toon = attack['target']['toon']
    if attack['suitName'] == 'csm':
        taunt = random.choice(['Hrm...', 'Hmph...', 'Hm, hm...', 'Hrnhmpf...'])
    elif attack['suitName'] == 'fbd':
        taunt = random.choice(['Hrm...', 'Hmph...', 'Hm, hm...', 'Hrnhmpf...'])
    else:
        taunt = getAttackTaunt(attack['name'], tauntIndex)

    suitTracks = Parallel()
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    for suit in battle.activeSuits:
        suitTrack = Sequence()
        suit.setHealthForMe(int(suit.currHP + 75))
        suitTrack.append(Wait(5.5))
        suitTrack.append(Func(suit.showHpText, 75))
        suitTrack.append(Func(suit.updateHealthBar, 0))
        suitTrack.append(Parallel(Sequence(Wait(5.5)),
                                  Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases), CFSpeech | CFTimeout)))
        suitTrack.append(
            Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
        suitTracks.append(suitTrack)
        suitTracks.append(tauntInterval)
        suitTracks.append(Parallel(Sequence(Wait(1.5), MovieUtil.createSuitInsuranceInterval(suit))))
    posPoints = [Point3(-0.04, 0.15, -1.38), VBase3(10.584, -11.945, 18.316)]
    knifeTracks = Parallel()
    for suits in battle.activeSuits:
        theSuit = attack['suit']
        knife = globalPropPool.getProp('shredder-paper')
        knifeTrack = Sequence(
            getPropAppearTrack(knife, theSuit.getRightHand(), posPoints, 2, MovieUtil.PNT3_ONE,
                               scaleUpTime=0.1),
            Wait(2.3),
            Parallel(
                getThrowTrack(knife, suits.getPos(battle), 1.95, battle, -34.288),
                LerpHprInterval(knife, 0.8, VBase3(0, 0, 0))
            ),
            Func(MovieUtil.removeProp, knife)
        )
        knifeTracks.append(knifeTrack)
    #cameraTrack = Sequence(LerpPosHprInterval(camera, duration=0.95, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'))
    suitTrack = Sequence(Wait(6.0), Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    #insuranceTrack = MovieUtil.createSuitInsuranceInterval(suit)
    soundTrack1 = getSoundTrack('SA_insurance.ogg', delay=1.5, node=suit)
    soundTrack2 = getSoundTrack('SA_extra_tip.ogg', delay=4.0, node=suit)
    multiTrack = Parallel(soundTrack1, soundTrack2)
    healSound = Sequence(Wait(5.5), SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'), node=suit))
    legalBindingsTrack = Sequence(Wait(8.0), doLegalBindings(attack))
    return Parallel(suitTrack, suitTracks, healSound, legalBindingsTrack, multiTrack, knifeTrack)

def doHeadHonchoCigarSmoke(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    tauntIndex = attack['taunt']
    toon = attack['target']['toon']
    dmg = target['hp']
    taunt = getAttackTaunt(attack['name'], tauntIndex)
    BattleParticles.loadParticles()
    smoke = BattleParticles.createParticleEffect('Smoke')
    BattleParticles.setEffectTexture(smoke, 'snow-particle')
    #cigar = globalPropPool.getProp('cigar')
    cigarPosPoints = [Point3(-0.05, -0.2, -0.25), VBase3(180.0, 0.0, 0.0)]
    #cigarPropTrack = getPropTrack(cigar, suit.getRightHand(), cigarPosPoints, 0.6, 3.6,
                                  #scaleUpPoint=Point3(6.0, 6.0, 6.0))
    toonTrack = getToonTrack(attack, 3.55, ['cringe'], 3.0, ['sidestep'])
    smokeTrack = getPartTrack(smoke, 5.45, 1.5, [smoke, suit, 0])
    suitTracks = Parallel()
    multiTrackList = Parallel(suitTracks, toonTrack)
    multiTrackList.append(smokeTrack)
    tauntInterval = Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout)
    for suit in battle.suits:
        suitTrack = Sequence()
        suitTracks.append(suitTrack)
        suitTracks.append(tauntInterval)
        suitTracks.append(Parallel(Sequence(Wait(1.5), MovieUtil.createSuitHeadHonchoCigarSmokeInterval(suit))))

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

def doFirestarterCigarSmoke(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    tauntIndex = attack['taunt']
    toon = attack['target']['toon']
    dmg = target['hp']
    taunt = getAttackTaunt(attack['name'], tauntIndex)
    BattleParticles.loadParticles()
    smoke = BattleParticles.createParticleEffect('Smoke')
    BattleParticles.setEffectTexture(smoke, 'snow-particle')
    cigar = globalPropPool.getProp('cigar')
    cigarPosPoints = [Point3(-0.05, -0.2, -0.25), VBase3(180.0, 0.0, 0.0)]
    cigarPropTrack = getPropTrack(cigar, suit.getRightHand(), cigarPosPoints, 0.6, 3.6, scaleUpPoint=Point3(6.0, 6.0, 6.0))
    toonTrack = getToonTrack(attack, 3.55, ['cringe'], 3.0, ['sidestep'])
    smokeTrack = getPartTrack(smoke, 5.45, 1.5, [smoke, suit, 0])
    suitTracks = Parallel()
    multiTrackList = Parallel(suitTracks, toonTrack)
    multiTrackList.append(smokeTrack)
    multiTrackList.append(cigarPropTrack)
    tauntInterval = Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout)
    for suit in battle.suits:
        suitTrack = Sequence()
        suitTracks.append(suitTrack)
        suitTracks.append(tauntInterval)
        suitTracks.append(Parallel(Sequence(Wait(1.5), MovieUtil.createSuitFirestarterCigarSmokeInterval(suit))))

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

def doOtherInsurancePlan(attack):
    suit = attack['suit']
    battle = attack['battle']

    suitTracks = Parallel()
    for suit in battle.activeSuits:
        suitTrack = Sequence()
        suit.setHealthForMe(int(suit.currHP + 75))
        suitTrack.append(Wait(3))
        suitTrack.append(Func(suit.showHpText, 75))
        suitTrack.append(Func(suit.updateHealthBar, 0))
        suitTrack.append(Parallel(Sequence(Wait(3)),
                                  Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases), CFSpeech | CFTimeout)))
        suitTrack.append(Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
        suitTracks.append(suitTrack)
    suitTrack = Sequence(getSuitAnimTrack(attack), ActorInterval(suit, 'neutral'))
    soundTrack1 = getSoundTrack('SA_paper_throw.ogg', delay=2, node=suit)
    soundTrack = getSoundTrack('SA_extra_tip.ogg', delay=1.5, node=suit)
    #multiTrack = Parallel(soundTrack1, soundTrack2)
    healSound = Sequence(Wait(3.0), SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'), node=suit))
    return Parallel(suitTrack, suitTracks, healSound, soundTrack)

def doRefinement(attack):
    suit = attack['suit']
    battle = attack['battle']

    suitTracks = Parallel()
    for suit in battle.activeSuits:
        suitTrack = Sequence()
        suit.setHealthForMe(int(suit.currHP + 75))
        suitTrack.append(Wait(3))
        suitTrack.append(Func(suit.showHpText, 75))
        suitTrack.append(Func(suit.updateHealthBar, 0))
        suitTrack.append(Parallel(Sequence(Wait(3)),
                                  Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases), CFSpeech | CFTimeout)))
        suitTrack.append(
            Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
        suitTracks.append(suitTrack)
    suitTrack = Sequence(getSuitAnimTrack(attack), ActorInterval(suit, 'neutral'))
    soundTrack1 = getSoundTrack('SA_repair.ogg', delay=2, node=suit)
    soundTrack2 = getSoundTrack('SA_refinement.ogg', delay=1.5, node=suit)
    multiTrack = Parallel(soundTrack1, soundTrack2)
    healSound = Sequence(Wait(3.0), SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'), node=suit))
    return Parallel(suitTrack, suitTracks, healSound, multiTrack)


def doNotThrowPiano(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    suitDelay = 2.0
    propDelay = 0.6
    throwDuration = 1.5
    piano = globalPropPool.getProp('piano')
    suitTrack = getSuitTrack(attack)
    posPoints = [Point3(-0.01, -0.05, 0.15), VBase3(180.00, -45.00, -45.00)]
    paperTrack = Sequence(
        getPropAppearTrack(piano, suit.getRightHand(), posPoints, propDelay, Point3(2.25, 2.25, 2.25), scaleUpTime=0.5))
    paperTrack.append(Wait(suitDelay))
    hitPoint = toon.getPos(battle)
    hitPoint.setX(hitPoint.getX() + 1.2)
    hitPoint.setY(hitPoint.getY() + 1.5)
    if dmg > 0:
        hitPoint.setZ(hitPoint.getZ() + 1.1)
    movePoint = Point3(hitPoint.getX(), hitPoint.getY() - 1.8, hitPoint.getZ() + 0.2)
    paperTrack.append(Func(battle.movie.needRestoreRenderProp, piano))
    paperTrack.append(Func(piano.wrtReparentTo, battle))
    paperTrack.append(getThrowTrack(piano, hitPoint, duration=throwDuration, parent=battle))
    paperTrack.append(Wait(0.6))
    paperTrack.append(LerpPosInterval(piano, 0.4, movePoint))
    spinTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpHprInterval(piano, throwDuration, Point3(180, 90, 90)))
    sizeTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpScaleInterval(piano, throwDuration, Point3(6, 6, 6)),
                         Wait(0.95), LerpScaleInterval(piano, 0.4, MovieUtil.PNT3_NEARZERO))
    propTrack = Sequence(Parallel(paperTrack, spinTrack, sizeTrack), Func(MovieUtil.removeProp, piano),
                         Func(battle.movie.clearRenderProp, piano))
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
    toonTrack = getToonTrack(attack, damageDelay=4.35, splicedDamageAnims=damageAnims, dodgeDelay=2.4,
                             dodgeAnimNames=['sidestep'], showDamageExtraTime=0.4, showMissedExtraTime=1.3)
    soundTrack = getSoundTrack('AA_drop_piano_miss.ogg', delay=3.9, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, propTrack)


def doThrowMoney(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    bill = globalPropPool.getProp('1dollar')
    suitTrack = getSuitTrack(attack)
    posPoints = [Point3(-0.01, -0.35, 0.15), VBase3(10.584, -11.945, 18.316)]
    propTrack = Sequence(
        getPropAppearTrack(bill, suit.getRightHand(), posPoints, 0.8, MovieUtil.PNT3_ONE, scaleUpTime=0.5))
    propTrack.append(Wait(1.73))
    hitPoint = __toonFacePoint(toon, parent=battle)
    hitPoint.setX(hitPoint.getX() - 1.4)
    missPoint = __toonGroundPoint(attack, toon, 0.7, parent=battle)
    missPoint.setX(missPoint.getX() - 1.1)
    propTrack.append(getPropThrowTrack(attack, bill, [hitPoint], [missPoint], parent=battle))
    toonTrack = getToonTrack(attack, 3.4, ['cringe'], 2.8, ['duck'])
    soundTrack = getSoundTrack('SA_pick_pocket.ogg', delay=2.6, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, propTrack)


def doAmandasDoughnuts(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    doughnut = globalPropPool.getProp('doughnut')
    suitTrack = getSuitTrack(attack)
    posPoints = [Point3(-0.01, -0.85, 0.15), VBase3(10.584, -11.945, 18.316)]
    propTrack = Sequence(
        getPropAppearTrack(doughnut, suit.getRightHand(), posPoints, 0.8, MovieUtil.PNT3_ONE, scaleUpTime=0.5))
    propTrack.append(Wait(1.73))
    hitPoint = __toonFacePoint(toon, parent=battle)
    hitPoint.setX(hitPoint.getX() - 1.4)
    missPoint = __toonGroundPoint(attack, toon, 0.7, parent=battle)
    missPoint.setX(missPoint.getX() - 1.1)
    propTrack.append(getPropThrowTrack(attack, doughnut, [hitPoint], [missPoint], parent=battle))
    damageAnims = [['spit',
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
    toonTrack = getToonTrack(attack, damageDelay=3.2, splicedDamageAnims=damageAnims, dodgeDelay=2.75,
                             splicedDodgeAnims=dodgeAnims, showDamageExtraTime=1.4)
    soundTrack = getSoundTrack('SA_doughnuts.ogg', delay=0.9, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, propTrack)


def doBombCake(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    toonPos = toon.getPos(battle)
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.height - 0.2)
    explosionTrack = Sequence()
    explosionTrack.append(Wait(3.4))
    explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
    cake = globalPropPool.getProp('birthday-cake')
    suitTrack = getSuitTrack(attack)
    posPoints = [Point3(-0.04, -0.15, -0.38), VBase3(180.00, 180.00, 0.00)]
    propTrack = Sequence(
        getPropAppearTrack(cake, suit.getRightHand(), posPoints, 0.8, MovieUtil.PNT3_ONE, scaleUpTime=0.5))
    propTrack.append(Wait(1.73))
    hitPoint = __toonFacePoint(toon, parent=battle)
    hitPoint.setX(hitPoint.getX() - 1.4)
    missPoint = __toonGroundPoint(attack, toon, 0.7, parent=battle)
    missPoint.setX(missPoint.getX() - 1.1)
    propTrack.append(getPropThrowTrack(attack, cake, [hitPoint], [missPoint], parent=battle))
    toonTrack = getToonTrack(attack, 3.4, ['slip-backward'], 2.8, ['jump'])
    soundTrack = getSoundTrack('AA_cake.ogg', delay=3.4, node=suit)
    soundTrack1 = getSoundTrack('ENC_cogfall_apart.ogg', delay=3.4, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, propTrack, explosionTrack, soundTrack1)


def doBomb(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    toonPos = toon.getPos(battle)
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.height - 0.2)
    explosionTrack = Sequence()
    explosionTrack.append(Wait(0.8))
    explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    gearPoint2 = Point3(suitPos.getX(), suitPos.getY(), suitPos.getZ() + suit.height - 0.2)
    explosionTrack2 = Sequence()
    explosionTrack2.append(Wait(1.5))
    explosionTrack2.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint2, scale=3))
    explode = []
    for i in xrange(0, 3):
        explode.append(globalPropPool.getProp('explosion'))
    explodePosPoints = [Point3(0, 15, 5), MovieUtil.PNT3_ZERO]
    explodePosPoints1 = [Point3(0, 15, 5), MovieUtil.PNT3_ZERO]
    explodeHprPoints = [Point3(180, 0, 0), MovieUtil.PNT3_ZERO]
    explodeHprPoints1 = [Point3(180, 0, 0), MovieUtil.PNT3_ZERO]
    explodeTracks = Parallel()
    for i in xrange(0, 3):
        explodeTrack = Sequence()
        explodeTrack.append(Wait(0.8))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodePosPoints, 1e-06, Point3(1.7, 1.7, 1.7), scaleUpTime=0.1))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodePosPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodeHprPoints, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodeHprPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.1))
        explodeTracks.append(explodeTrack)
    dmg = target['hp']
    tnt = globalPropPool.getProp('tnt')
    suit.setHealthForMe(int(suit.currHP - (dmg * 4)))
    suitTrack = Sequence(getSuitAnimTrack(attack), ActorInterval(suit, 'slip-backward'))
    suitTrack.append(Sequence(Parallel(Func(suit.showHpTextRed, "BOMBED!", 10))))
    if suit.currHP <= 0:
        suitTrack.append(MovieUtil.createSuitDeathTrack(suit, battle))
    else:
        suitTrack.append(Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    posPoints = [Point3(-0.04, -0.15, -0.78), VBase3(10.584, -11.945, 18.316)]
    propTrack = Sequence(
        getPropAppearTrack(tnt, suit.getRightHand(), posPoints, 0.1, MovieUtil.PNT3_ONE, scaleUpTime=0.1))
    propTrack.append(Wait(0.1))
    hitPoint = __toonFacePoint(toon, parent=battle)
    hitPoint.setX(hitPoint.getX() - 1.4)
    missPoint = __toonGroundPoint(attack, toon, 0.1, parent=battle)
    missPoint.setX(missPoint.getX() - 1.1)
    propTrack.append(getPropThrowTrack(attack, tnt, [hitPoint], [missPoint], parent=battle))
    toonTrack = getToonTrack(attack, 0.5, ['slip-forward'], 0.5, ['jump'])
    soundTrack = getSoundTrack('ENC_cogfall_apart.ogg', delay=0.5, node=suit)
    soundTrack2 = getSoundTrack('ENC_cogfall_apart.ogg', delay=1.5, node=suit)
    selfDamageTrack = Sequence(Wait(2), Func(suit.showHpText, - (dmg * 4)), Func(suit.updateHealthBar, 0))
    notifyTrack = Sequence(Wait(.5 + 1.5 + 1.5), Func(toon.showHpTextRed, "HUGE LOSS!", 10))
    return Parallel(explodeTracks, suitTrack, toonTrack, soundTrack, soundTrack2, propTrack, notifyTrack, selfDamageTrack, explosionTrack, explosionTrack2)

def doExplodingBill(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    explode = []
    toonPos = toon.getPos(battle)
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.height - 0.2)
    explosionTrack = Sequence()
    explosionTrack.append(Wait(3.5))
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
        explodeTrack.append(Wait(3.5))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodePosPoints, 1e-06, Point3(1.7, 1.7, 1.7), scaleUpTime=0.1))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodePosPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodeHprPoints, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodeHprPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.1))
        explodeTracks.append(explodeTrack)
    dmg = target['hp']
    tnt = globalPropPool.getProp('shredder-paper')
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack.append(Parallel(Func(suit.setChatAbsolute,
                                   "Looks like you received a defective bill, you're going to be vulnerable for 2 turns.",
                                   CFSpeech | CFTimeout)))
    posPoints = [Point3(-0.04, 0.15, -1.38), VBase3(95.247, 79.025, 88.849)]
    propTrack = Sequence(
        getPropAppearTrack(tnt, suit.getRightHand(), posPoints, 3.0, MovieUtil.PNT3_ONE, scaleUpTime=0.1))
    propTrack.append(Wait(0.1))
    hitPoint = __toonFacePoint(toon, parent=battle)
    hitPoint.setX(hitPoint.getX() - 1.4)
    missPoint = __toonGroundPoint(attack, toon, 3.1, parent=battle)
    missPoint.setX(missPoint.getX() - 1.1)
    propTrack.append(getPropThrowTrack(attack, tnt, [hitPoint], [missPoint], parent=battle))
    toonTrack = getToonTrack(attack, 3.5, ['slip-forward'], 0.5, ['jump'])
    soundTrack = getSoundTrack('ENC_cogfall_apart.ogg', delay=3.5, node=suit)
    notifyTrack = Sequence(Wait(.5 + 1.5 + 1.5), Func(toon.showHpTextRed, "EXPLOSION!", 10))
    return Parallel(explodeTracks, suitTrack, toonTrack, soundTrack, propTrack, notifyTrack, explosionTrack)


def doSnowBalls(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect(file='Snowballs')
    BattleParticles.setEffectTexture(particleEffect, 'snow-particle')
    suitTrack = getSuitAnimTrack(attack)
    partTrack = getPartTrack(particleEffect, 1e-05, suitTrack.getDuration() + 1.2, [particleEffect, suit, 0])
    toonTrack = getToonTrack(attack, 1.2, ['cringe'], 0.2, splicedDodgeAnims=[['duck', 1e-05, 0.8]],
                             showMissedExtraTime=0.8)
    headParts = toon.getHeadParts()
    torsoParts = toon.getTorsoParts()
    legsParts = toon.getLegsParts()

    def changeColor(parts):
        track = Parallel()
        for partNum in xrange(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.setColorScale, Vec4(0, 0, 1, 1)))

        return track

    def resetColor(parts):
        track = Parallel()
        for partNum in xrange(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.clearColorScale))

        return track

    soundTrack = getSoundTrack('SA_freeze.ogg', delay=0.4, node=suit)
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
        return Parallel(suitTrack, partTrack, toonTrack, soundTrack, colorTrack)
    else:
        return Parallel(suitTrack, partTrack, toonTrack, soundTrack)


def doFireBalls(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect(file='Fire')
    BattleParticles.setEffectTexture(particleEffect, 'fire')
    suitTrack = getSuitAnimTrack(attack)
    partTrack = getPartTrack(particleEffect, 1e-05, suitTrack.getDuration() + 1.2, [particleEffect, suit, 0])
    toonTrack = getToonTrack(attack, 1.2, ['cringe'], 0.2, splicedDodgeAnims=[['duck', 1e-05, 0.8]],
                             showMissedExtraTime=0.8)
    headParts = toon.getHeadParts()
    torsoParts = toon.getTorsoParts()
    legsParts = toon.getLegsParts()

    def changeColor(parts):
        track = Parallel()
        for partNum in xrange(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.setColorScale, Vec4(0, 0, 0, 0.95)))

        return track

    def resetColor(parts):
        track = Parallel()
        for partNum in xrange(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.clearColorScale))

        return track

    soundTrack = getSoundTrack('SA_hot_air.ogg', delay=0.4, node=suit)
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
        return Parallel(suitTrack, partTrack, toonTrack, soundTrack, colorTrack)
    else:
        return Parallel(suitTrack, partTrack, toonTrack, soundTrack)

def doKamikaze(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTracks = Parallel()
    for suit in battle.activeSuits:
        suitTrack = getSuitAnimTrack(attack)
        suitTrack.append(Wait(0.1))
        suit.setHealthForMe(int(suit.currHP - 200))
        suitTrack.append(Func(suit.showHpText, -200))
        suitTrack.append(Func(suit.updateHealthBar, 0))
        suitTrack.append(Func(suit.play, 'slip-backward'))
        suitTrack.append(Func(suit.setChatAbsolute, 'Ouch.', CFSpeech | CFTimeout))
        suitTrack.append(Func(suit.showHpTextRed, "BOMBED!!", 10))
        suitTrack.append(Wait(3.5))
        suitTracks.append(suitTrack)
        revives = suit.getMaxSkeleRevives() + 1
        if suit.currHP <= 0 and revives > 1:
            suitTrack.append(MovieUtil.createSuitReviveTrack(suit, battle))
        elif suit.currHP <= 0:
            suitTrack.append(MovieUtil.createSuitDeathTrack(suit, battle))
        else:
            suitTrack.append(Func(battle.unlureSuit, suit))
            suitTrack.append(
                Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    posPoints = [Point3(-0.3, 0.4, 0.0), VBase3(0, 0, 90)]
    knifeTracks = Parallel()
    sparkTracks = Parallel()
    suitPos, suitHpr = battle.getActorPosHpr(theSuit)
    gearPoint = Point3(suitPos.getX(), suitPos.getY() - 10, suitPos.getZ() + suit.height - 0.2)
    explosionTrack = Sequence()
    explosionTrack.append(Wait(4.0))
    explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
    suitPos, suitHpr = battle.getActorPosHpr(theSuit)
    gearPoint2 = Point3(suitPos.getX(), suitPos.getY(), suitPos.getZ() + suit.height - 0.2)
    explosionTrack2 = Sequence()
    explosionTrack2.append(Wait(4.0))
    explosionTrack2.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint2, scale=3))
    for t in targets:
        toon = t['toon']
        knife = globalPropPool.getProp('tnt')
        knifeTrack = Sequence(
            getPropAppearTrack(knife, theSuit.getRightHand(), posPoints, 0.25, scaleUpPoint=Point3(0.7), scaleUpTime=0.1),
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
        if t['hp'] != 0:
            sparkTracks.append(Sequence(
                Wait(4.0),
                Parallel(
                    ParticleInterval(sparkEffect, toon, worldRelative=0, duration=3.0, cleanup=True),
                    autoFinish=1
                )
            ))
    damageAnims = [['slip-forward', 0.01, 0.4]]
    toonTracks = getToonTracks(attack, damageDelay=4.0, splicedDamageAnims=damageAnims, dodgeDelay=3.1, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('incoming_whistle.ogg', delay=2.0, node=suit)
    soundTrack2 = getSoundTrack('SA_extra_tip.ogg', delay=1.5, node=suit)
    soundTrack1 = getSoundTrack('ENC_cogfall_apart.ogg', delay=4.0, node=suit)
    return Parallel(suitTracks, knifeTracks, sparkTracks, toonTracks, soundTrack, soundTrack1, soundTrack2, explosionTrack, explosionTrack2)


def doFallingKnife(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    suitTrack = getSuitTrack(attack)
    posPoints = [Point3(-0.3, 0.4, 0.0), VBase3(0, 0, 90)]
    knifeTracks = Parallel()
    sparkTracks = Parallel()
    knife = globalPropPool.getProp('dagger')
    knifeTrack = Sequence(
            getPropAppearTrack(knife, suit.getRightHand(), posPoints, 0.25, scaleUpPoint=Point3(0.7), scaleUpTime=0.1),
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
    toonTracks = getToonTrack(attack, damageDelay=4.0, splicedDamageAnims=damageAnims, dodgeDelay=3.1, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_falling_knife.ogg', node=suit)
    return Parallel(suitTrack, knifeTracks, sparkTracks, toonTracks, soundTrack)

def doFallingKnifeOLD(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    suitDelay = 0.5
    propDelay = 0.6
    throwDuration = 1.5
    paper = globalPropPool.getProp('dagger')
    suitTrack = getSuitTrack(attack)
    posPoints = [Point3(0.00, -1.00, -1.85), VBase3(270.00, 45.00, 45.00)]
    paperTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, propDelay, Point3(1.25, 1.25, 1.25), scaleUpTime=0.1))
    paperTrack.append(Wait(suitDelay))
    hitPoint = toon.getPos(battle)
    hitPoint.setX(hitPoint.getX() + 0)
    hitPoint.setY(hitPoint.getY() + .2)
    if dmg > 0:
        hitPoint.setZ(hitPoint.getZ() + 1.1)
    movePoint = Point3(hitPoint.getX() + 10, hitPoint.getY() - 1.8, hitPoint.getZ() + 0.2)
    paperTrack.append(Func(battle.movie.needRestoreRenderProp, paper))
    paperTrack.append(Func(paper.wrtReparentTo, battle))
    paperTrack.append(getThrowTrack(paper, hitPoint, duration=throwDuration, parent=battle))
    paperTrack.append(Wait(0.6))
    paperTrack.append(LerpPosInterval(paper, 0.4, movePoint))
    spinTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpHprInterval(paper, throwDuration, Point3(-360, -90, -90)))
    sizeTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpScaleInterval(paper, throwDuration, Point3(2, 2, 2)), Wait(0.95), LerpScaleInterval(paper, 0.4, MovieUtil.PNT3_NEARZERO))
    propTrack = Sequence(Parallel(paperTrack, spinTrack, sizeTrack), Func(MovieUtil.removeProp, paper), Func(battle.movie.clearRenderProp, paper))
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
    soundTrack = getSoundTrack('SA_falling_knife.ogg', node=suit)
    toonTrack = getToonTrack(attack, damageDelay=3.35, splicedDamageAnims=damageAnims, dodgeDelay=2.4, dodgeAnimNames=['sidestep'], showDamageExtraTime=0.4, showMissedExtraTime=1.3)
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack)

def doBlueChipOLD(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    suitDelay = 1.0
    propDelay = 0.6
    throwDuration = 1.5
    paper = loader.loadModel('phase_5/models/props/cc_m_prp_gen_chip_blue.bam')
    suitTrack = getSuitTrack(attack)
    posPoints = [Point3(-0.01, -0.05, 0.15), VBase3(270.00, 45.00, 45.00)]
    paperTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, propDelay, Point3(2.25, 2.25, 2.25), scaleUpTime=0.5))
    paperTrack.append(Wait(suitDelay))
    hitPoint = toon.getPos(battle)
    hitPoint.setX(hitPoint.getX() + 0)
    hitPoint.setY(hitPoint.getY() + 1.5)
    if dmg > 0:
        hitPoint.setZ(hitPoint.getZ() + 1.1)
    movePoint = Point3(hitPoint.getX(), hitPoint.getY() - 1.8, hitPoint.getZ() + 0.2)
    paperTrack.append(Func(battle.movie.needRestoreRenderProp, paper))
    paperTrack.append(Func(paper.wrtReparentTo, battle))
    paperTrack.append(getThrowTrack(paper, hitPoint, duration=throwDuration, parent=battle))
    paperTrack.append(Wait(0.6))
    paperTrack.append(LerpPosInterval(paper, 0.4, movePoint))
    spinTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpHprInterval(paper, throwDuration, Point3(-360, 90, 90)))
    sizeTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpScaleInterval(paper, throwDuration, Point3(8, 8, 8)), Wait(0.95), LerpScaleInterval(paper, 0.4, MovieUtil.PNT3_NEARZERO))
    propTrack = Sequence(Parallel(paperTrack, spinTrack, sizeTrack), Func(MovieUtil.removeProp, paper), Func(battle.movie.clearRenderProp, paper))
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
    soundTrack = getSoundTrack('SA_blue_chip.ogg', delay=1.1, node=suit)
    toonTrack = getToonTracks(attack, damageDelay=3.35, splicedDamageAnims=damageAnims, dodgeDelay=2.4, dodgeAnimNames=['sidestep'], showDamageExtraTime=0.4, showMissedExtraTime=1.3)
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack)

def doShortSqueeze(attack):
    battle = attack['battle']
    target = attack['target']
    dmg = target['hp']
    toon = target['toon']
    damageDelay = 1.0
    suitTrack = getSuitTrack(attack)
    damageAnims = [['struggle', 0.01, 0.01, 1.0],
     ['slip-backward', 0.01, 0.01]]
    shakeTracks = Parallel()
    squeezeTracks = Parallel()
    coinTracks = Parallel()
    toonTracks = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.5, dodgeAnimNames=['sidestep'], showDamageExtraTime=1.1)
    soundTracks = Parallel()
    if dmg != 0:
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
    dmg = target['hp']
    toon = target['toon']
    suitDelay = 1.32
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
    chipTrack.append(Wait(0.6))
    chipTrack.append(LerpPosInterval(chip, 0.4, movePoint))
    spinTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpHprInterval(chip, throwDuration, Point3(0, 810, 0)))
    sizeTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpScaleInterval(chip, throwDuration, Point3(6)), Wait(0.95), LerpScaleInterval(chip, 0.4, MovieUtil.PNT3_NEARZERO))
    propTrack = Sequence(Parallel(chipTrack, spinTrack, sizeTrack), Func(MovieUtil.removeProp, chip), Func(battle.movie.clearRenderProp, chip))
    propTracks.append(propTrack)
    toonTracks = getToonTrack(attack, 3.3, ['squish'], 2.0, ['sidestep'])
    squishTrack = Sequence(Wait(3.3), Func(toon.enterFlattened), Wait(2.0), Func(toon.exitFlattened))
    soundTrack = getSoundTrack('SA_blue_chip.ogg', node=suit)
    if dmg > 0:
        return Parallel(suitTrack, toonTracks, propTracks, soundTrack, squishTrack)
    else:
        return Parallel(suitTrack, toonTracks, propTracks, soundTrack)

	
def doThrowBook(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    suitDelay = 2.0
    propDelay = 0.6
    throwDuration = 1.5
    paper = globalPropPool.getProp('lawbook')
    suitTrack = getSuitTrack(attack)
    posPoints = [Point3(0.00, -1.00, -1.85), VBase3(180.00, -45.00, -45.00)]
    paperTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, propDelay, Point3(2.25, 2.25, 2.25), scaleUpTime=0.5))
    paperTrack.append(Wait(suitDelay))
    hitPoint = toon.getPos(battle)
    hitPoint.setX(hitPoint.getX() + 0)
    hitPoint.setY(hitPoint.getY() + 1.5)
    if dmg > 0:
        hitPoint.setZ(hitPoint.getZ() + 1.1)
    movePoint = Point3(hitPoint.getX(), hitPoint.getY() - 1.8, hitPoint.getZ() + 0.2)
    paperTrack.append(Func(battle.movie.needRestoreRenderProp, paper))
    paperTrack.append(Func(paper.wrtReparentTo, battle))
    paperTrack.append(getThrowTrack(paper, hitPoint, duration=throwDuration, parent=battle))
    paperTrack.append(Wait(0.6))
    paperTrack.append(LerpPosInterval(paper, 0.4, movePoint))
    spinTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpHprInterval(paper, throwDuration, Point3(-360, 0, 0)))
    sizeTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpScaleInterval(paper, throwDuration, Point3(6, 6, 6)), Wait(0.95), LerpScaleInterval(paper, 0.4, MovieUtil.PNT3_NEARZERO))
    propTrack = Sequence(Parallel(paperTrack, spinTrack, sizeTrack), Func(MovieUtil.removeProp, paper), Func(battle.movie.clearRenderProp, paper))
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
    soundTrack = getSoundTrack('SA_throw_book.ogg', delay=1.5, node=suit)
    toonTrack = getToonTrack(attack, damageDelay=4.35, splicedDamageAnims=damageAnims, dodgeDelay=2.4, dodgeAnimNames=['sidestep'], showDamageExtraTime=0.4, showMissedExtraTime=1.3)
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack)

def doCloudStorage(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    suitDelay = 0
    propDelay = 3.6
    throwDuration = 1.5
    paper = loader.loadModel('phase_5.5/models/estate/bumper_cloud')
    suitTrack = getSuitTrack(attack)
    posPoints = [Point3(0, 0, 0), VBase3(180.00, -45.00, -45.00)]
    paperTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, propDelay, Point3(1.25, 1.25, 1.25), scaleUpTime=0.1))
    paperTrack.append(Wait(suitDelay))
    hitPoint = toon.getPos(battle)
    hitPoint.setX(hitPoint.getX() + 2)
    hitPoint.setY(hitPoint.getY() + 0.5)
    if dmg > 0:
        hitPoint.setZ(hitPoint.getZ())
    movePoint = Point3(hitPoint.getX(), hitPoint.getY(), hitPoint.getZ())
    paperTrack.append(Func(battle.movie.needRestoreRenderProp, paper))
    paperTrack.append(Func(paper.wrtReparentTo, battle))
    paperTrack.append(getThrowTrack(paper, hitPoint, duration=throwDuration, parent=battle))
    paperTrack.append(Wait(0.6))
    paperTrack.append(LerpPosInterval(paper, 0.1, movePoint))
    spinTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpHprInterval(paper, throwDuration, Point3(-360, 0, 0)))
    sizeTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpScaleInterval(paper, throwDuration, Point3(3, 3, 3)), Wait(0.95), LerpScaleInterval(paper, 0.4, MovieUtil.PNT3_NEARZERO))
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
    soundTrack = getSoundTrack('SA_throw_book.ogg', delay=1.5, node=suit)
    toonTrack = getToonTrack(attack, damageDelay=5.35, splicedDamageAnims=damageAnims, dodgeDelay=2.4, dodgeAnimNames=['sidestep'], showDamageExtraTime=0.4, showMissedExtraTime=1.3)
    return Parallel(suitTrack, toonTrack, propTrack)


def doWithdrawal(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect('Withdrawal')
    BattleParticles.setEffectTexture(particleEffect, 'snow-particle')
    suitTrack = getSuitAnimTrack(attack)
    partTrack = getPartTrack(particleEffect, 1e-05, suitTrack.getDuration() + 1.2, [particleEffect, suit, 0])
    toonTrack = getToonTrack(attack, 1.2, ['cringe'], 0.2, splicedDodgeAnims=[['duck', 1e-05, 0.8]], showMissedExtraTime=0.8)
    headParts = toon.getHeadParts()
    torsoParts = toon.getTorsoParts()
    legsParts = toon.getLegsParts()

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
        return Parallel(suitTrack, partTrack, toonTrack, soundTrack, colorTrack)
    else:
        return Parallel(suitTrack, partTrack, toonTrack, soundTrack)


def doJargon(attack):
    suit = attack['suit']
    battle = attack['battle']
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect(file='jargonSpray')
    particleEffect2 = BattleParticles.createParticleEffect(file='jargonSpray')
    particleEffect3 = BattleParticles.createParticleEffect(file='jargonSpray')
    particleEffect4 = BattleParticles.createParticleEffect(file='jargonSpray')
    BattleParticles.setEffectTexture(particleEffect, 'jargon-brow', color=Vec4(1, 0, 0, 1))
    BattleParticles.setEffectTexture(particleEffect2, 'jargon-deep', color=Vec4(0, 0, 0, 1))
    BattleParticles.setEffectTexture(particleEffect3, 'jargon-hoop', color=Vec4(1, 0, 0, 1))
    BattleParticles.setEffectTexture(particleEffect4, 'jargon-ipo', color=Vec4(0, 0, 0, 1))
    damageDelay = 2.2
    dodgeDelay = 1.5
    partDelay = 1.1
    partInterval = 1.2
    suitTrack = getSuitTrack(attack)
    partTrack = getPartTrack(particleEffect, partDelay + partInterval * 0, 2, [particleEffect, suit, 0])
    partTrack2 = getPartTrack(particleEffect2, partDelay + partInterval * 1, 2, [particleEffect2, suit, 0])
    partTrack3 = getPartTrack(particleEffect3, partDelay + partInterval * 2, 2, [particleEffect3, suit, 0])
    partTrack4 = getPartTrack(particleEffect4, partDelay + partInterval * 3, 1.0, [particleEffect4, suit, 0])
    damageAnims = []
    damageAnims.append(['conked',
     0.0001,
     0,
     0.4])
    damageAnims.append(['conked',
     0.0001,
     2.7,
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
     0.66])
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
    damageAnims.append(['conked',
     0.0001,
     0.4,
     0.14])
    damageAnims.append(['conked',
     0.0001,
     0.4,
     0.14])
    damageAnims.append(['conked', 0.0001, 0.4])
    dodgeAnims = [['duck', 0.0001, 1.2], ['duck', 0.0001, 1.3]]
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.6, showDamageExtraTime=0.7)
    soundTrack = getSoundTrack('SA_jargon.ogg', delay=2.1, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, partTrack, partTrack2, partTrack3, partTrack4)


def doMumboJumbo(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect(file='mumboJumboSpray')
    particleEffect2 = BattleParticles.createParticleEffect(file='mumboJumboSpray')
    particleEffect3 = BattleParticles.createParticleEffect(file='mumboJumboSmother')
    particleEffect4 = BattleParticles.createParticleEffect(file='mumboJumboSmother')
    particleEffect5 = BattleParticles.createParticleEffect(file='mumboJumboSmother')
    BattleParticles.setEffectTexture(particleEffect, 'mumbojumbo-boiler', color=Vec4(1, 0, 0, 1))
    BattleParticles.setEffectTexture(particleEffect2, 'mumbojumbo-creative', color=Vec4(1, 0, 0, 1))
    BattleParticles.setEffectTexture(particleEffect3, 'mumbojumbo-deben', color=Vec4(1, 0, 0, 1))
    BattleParticles.setEffectTexture(particleEffect4, 'mumbojumbo-high', color=Vec4(1, 0, 0, 1))
    BattleParticles.setEffectTexture(particleEffect5, 'mumbojumbo-iron', color=Vec4(1, 0, 0, 1))
    suitTrack = getSuitTrack(attack)
    partTrack = getPartTrack(particleEffect, 2.5, 2, [particleEffect, suit, 0])
    partTrack2 = getPartTrack(particleEffect2, 2.5, 2, [particleEffect2, suit, 0])
    partTrack3 = getPartTrack(particleEffect3, 3.3, 1.7, [particleEffect3, toon, 0])
    partTrack4 = getPartTrack(particleEffect4, 3.3, 1.7, [particleEffect4, toon, 0])
    partTrack5 = getPartTrack(particleEffect5, 3.3, 1.7, [particleEffect5, toon, 0])
    toonTrack = getToonTrack(attack, 3.2, ['cringe'], 2.2, ['sidestep'])
    soundTrack = getSoundTrack('SA_mumbo_jumbo.ogg', delay=2.5, node=suit)
    if dmg > 0:
        return Parallel(suitTrack, toonTrack, soundTrack, partTrack, partTrack2, partTrack3, partTrack4, partTrack5)
    else:
        return Parallel(suitTrack, toonTrack, soundTrack, partTrack, partTrack2)


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
    suitTrack = getSuitAnimTrack(attack)

    def getPowerTrack(effect, suit = suit, battle = battle):
        partTrack = Sequence(Wait(0.7), Func(battle.movie.needRestoreParticleEffect, effect), Func(effect.start, suit), Wait(0.4), LerpPosInterval(effect, 1.0, Point3(0, 15, 0.4)), LerpFunctionInterval(effect.setAlphaScale, fromData=1, toData=0, duration=0.4), Func(effect.cleanup), Func(battle.movie.clearRestoreParticleEffect, effect))
        return partTrack

    partTrack1 = getPowerTrack(powerBar1)
    partTrack2 = getPowerTrack(powerBar2)
    waterfallTrack = getPartTrack(waterfallEffect, 0.6, 0.6, [waterfallEffect, suit, 0])
    toonTracks = getToonTracks(attack, 1.5, ['slip-forward'], 0.86, ['jump'])
    soundTrack = getSoundTrack('SA_guilt_trip.ogg', delay=1.1, node=suit)
    return Parallel(suitTrack, partTrack1, partTrack2, soundTrack, waterfallTrack, toonTracks)


def doRestrainingOrder(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    paper = globalPropPool.getProp('shredder-paper')
    suitTrack = getSuitTrack(attack)
    posPoints = [Point3(-0.04, 0.15, -1.38), VBase3(10.584, -11.945, 18.316)]
    propTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.8, MovieUtil.PNT3_ONE, scaleUpTime=0.5))
    propTrack.append(Wait(1.73))
    hitPoint = __toonFacePoint(toon, parent=battle)
    hitPoint.setX(hitPoint.getX() - 1.4)
    missPoint = __toonGroundPoint(attack, toon, 0.7, parent=battle)
    missPoint.setX(missPoint.getX() - 1.1)
    propTrack.append(getPropThrowTrack(attack, paper, [hitPoint], [missPoint], parent=battle))
    damageAnims = [['conked',
      0.01,
      0.3,
      0.2], ['struggle', 0.01, 0.2]]
    toonTrack = getToonTrack(attack, damageDelay=3.4, splicedDamageAnims=damageAnims, dodgeDelay=2.8, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_paper_throw.ogg', delay=2.9, node=suit)
    if dmg > 0:
        restraintCloud = BattleParticles.createParticleEffect(file='restrainingOrderCloud')
        restraintCloud.setPos(hitPoint.getX(), hitPoint.getY() + 0.5, hitPoint.getZ())
        cloudTrack = getPartTrack(restraintCloud, 3.5, 0.2, [restraintCloud, battle, 0])
        return Parallel(suitTrack, cloudTrack, toonTrack, propTrack, soundTrack)
    else:
        return Parallel(suitTrack, toonTrack, propTrack, soundTrack)

def doSwirlBath(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    damageDelay = 1.7
    sprayEffect = BattleParticles.createParticleEffect(file='spinSpray')
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
    suitTrack = getSuitTrack(attack)
    sprayTrack = getPartTrack(sprayEffect, 1.0, 1.9, [sprayEffect, suit, 0])
    spinTrack1 = getPartTrack(spinEffect1, 2.1, 3.9, [spinEffect1, battle, 0])
    spinTrack2 = getPartTrack(spinEffect2, 2.1, 3.9, [spinEffect2, battle, 0])
    spinTrack3 = getPartTrack(spinEffect3, 2.1, 3.9, [spinEffect3, battle, 0])
    damageAnims = []
    damageAnims.append(['duck',
                        0.01,
                        0.01,
                        1.1])
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.91,
                             dodgeAnimNames=['sidestep'], showDamageExtraTime=2.1, showMissedExtraTime=1.0)
    soundTrack = getSoundTrack('ttcc_ene_hroller_laugh.ogg', delay=0.01, node=suit)
    if dmg > 0:
        toonSpinTrack = Sequence(Wait(damageDelay + 0.9), LerpHprInterval(toon, 0.7, Point3(-10, 0, 0)), LerpHprInterval(toon, 0.5, Point3(-30, 0, 0)), LerpHprInterval(toon, 0.2, Point3(-60, 0, 0)), LerpHprInterval(toon, 0.7, Point3(-700, 0, 0)), LerpHprInterval(toon, 1.0, Point3(-1310, 0, 0)), LerpHprInterval(toon, 0.4, toon.getHpr()), Wait(0.5))
        return Parallel(suitTrack, sprayTrack, toonTrack, soundTrack, toonSpinTrack, spinTrack1, spinTrack2, spinTrack3)
    else:
        return Parallel(suitTrack, sprayTrack, toonTrack, soundTrack)


def doSpin(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    damageDelay = 1.7
    sprayEffect = BattleParticles.createParticleEffect(file='spinSpray')
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
    suitTrack = getSuitTrack(attack)
    sprayTrack = getPartTrack(sprayEffect, 1.0, 1.9, [sprayEffect, suit, 0])
    spinTrack1 = getPartTrack(spinEffect1, 2.1, 3.9, [spinEffect1, battle, 0])
    spinTrack2 = getPartTrack(spinEffect2, 2.1, 3.9, [spinEffect2, battle, 0])
    spinTrack3 = getPartTrack(spinEffect3, 2.1, 3.9, [spinEffect3, battle, 0])
    damageAnims = []
    damageAnims.append(['duck',
     0.01,
     0.01,
     1.1])
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.91, dodgeAnimNames=['sidestep'], showDamageExtraTime=2.1, showMissedExtraTime=1.0)
    if dmg > 0:
        soundTrack = getSoundTrack('tt_s_ara_cfg_toonInWhirlwind.ogg', delay=2.0, node=suit)
        toonSpinTrack = Sequence(Wait(damageDelay + 0.9), LerpHprInterval(toon, 0.7, Point3(-10, 0, 0)), LerpHprInterval(toon, 0.5, Point3(-30, 0, 0)), LerpHprInterval(toon, 0.2, Point3(-60, 0, 0)), LerpHprInterval(toon, 0.7, Point3(-700, 0, 0)), LerpHprInterval(toon, 1.0, Point3(-1310, 0, 0)), LerpHprInterval(toon, 0.4, toon.getHpr()), Wait(0.5))
        return Parallel(suitTrack, sprayTrack, toonTrack, toonSpinTrack, spinTrack1, spinTrack2, spinTrack3, soundTrack)
    else:
        return Parallel(suitTrack, sprayTrack, toonTrack)


def doLegalese(attack):
    suit = attack['suit']
    BattleParticles.loadParticles()
    sprayEffect1 = BattleParticles.createParticleEffect(file='legaleseSpray')
    sprayEffect2 = BattleParticles.createParticleEffect(file='legaleseSpray')
    sprayEffect3 = BattleParticles.createParticleEffect(file='legaleseSpray')
    color = Vec4(0.4, 0, 0, 1)
    BattleParticles.setEffectTexture(sprayEffect1, 'legalese-hc', color=color)
    BattleParticles.setEffectTexture(sprayEffect2, 'legalese-qpq', color=color)
    BattleParticles.setEffectTexture(sprayEffect3, 'legalese-vd', color=color)
    partDelay = 1.3
    partDuration = 1.15
    damageDelay = 1.9
    dodgeDelay = 1.1
    suitTrack = getSuitTrack(attack)
    sprayTrack1 = getPartTrack(sprayEffect1, partDelay, partDuration, [sprayEffect1, suit, 0])
    sprayTrack2 = getPartTrack(sprayEffect2, partDelay + 0.8, partDuration, [sprayEffect2, suit, 0])
    sprayTrack3 = getPartTrack(sprayEffect3, partDelay + 1.6, partDuration, [sprayEffect3, suit, 0])
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
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'], showMissedExtraTime=0.8)
    return Parallel(suitTrack, toonTrack, sprayTrack1, sprayTrack2, sprayTrack3)


def doPeckingOrder(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    throwDuration = 3.03
    throwDelay = 3.2
    suitTrack = getSuitTrack(attack)
    numBirds = random.randint(10, 20)
    birdTracks = Parallel()
    propDelay = 1.5
    for i in xrange(0, numBirds):
        next = globalPropPool.getProp('bird')
        next.setScale(0.01)
        next.reparentTo(suit.getRightHand())
        next.setPos(random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3)
        if dmg > 0:
            hitPoint = Point3(random.random() * 5 - 2.5, random.random() * 2 - 1 - 6, random.random() * 3 - 1.5 + toon.getHeight() - 0.9)
        else:
            hitPoint = Point3(random.random() * 2 - 1, random.random() * 4 - 2 - 15, random.random() * 4 - 2 + 2.2)
        birdTrack = Sequence(Wait(throwDelay), Func(battle.movie.needRestoreRenderProp, next), Func(next.wrtReparentTo, battle), Func(next.setHpr, Point3(90, 20, 0)), LerpPosInterval(next, 1.1, hitPoint))
        scaleTrack = Sequence(Wait(throwDelay), LerpScaleInterval(next, 0.15, Point3(9, 9, 9)))
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
    toonTrack = getToonTrack(attack, damageDelay=4.2, splicedDamageAnims=damageAnims, dodgeDelay=2.8, dodgeAnimNames=['sidestep'], showMissedExtraTime=1.1)
    soundTrack = getSoundTrack('tt_s_ara_cfg_eagleCry.ogg', delay=1.9, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, birdTracks)

def doFreeCruiseBAD(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    throwDuration = 1.03
    throwDelay = 3.2
    suitTrack = getSuitTrack(attack)
    numBirds = 1
    birdTracks = Parallel()
    propDelay = 1.5
    for i in xrange(0, numBirds):
        next = globalPropPool.getProp('ship')
        next.setScale(0.5)
        #next.reparentTo(suit.getRightHand)
        next.setPos(random.random() * 2 - 0.3, random.random() * 2 - 0.3, random.random() * 2 - 0.3)
        if dmg > 0:
            hitPoint = Point3(random.random() * 6 - 2.5, random.random() * 6 - 1 - 6, random.random() * 6 - 1.5 + toon.getHeight() - 0.9)
        else:
            hitPoint = Point3(random.random() * 2 - 1, random.random() * 4 - 2 - 15, random.random() * 4 - 2 + 2.2)
        birdTrack = Sequence(Wait(throwDelay), Func(battle.movie.needRestoreRenderProp, next), Func(next.wrtReparentTo, battle), Func(next.setHpr, Point3(90, 20, 0)), LerpPosInterval(next, 1.1, hitPoint))
        scaleTrack = Sequence(Wait(throwDelay), LerpScaleInterval(next, 0.15, Point3(9, 9, 9)))
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
    toonTrack = getToonTrack(attack, damageDelay=4.2, splicedDamageAnims=damageAnims, dodgeDelay=2.8, dodgeAnimNames=['sidestep'], showMissedExtraTime=1.1)
    soundTrack = getSoundTrack('tt_s_ara_cfg_eagleCry.ogg', delay=1.9, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, birdTracks)
