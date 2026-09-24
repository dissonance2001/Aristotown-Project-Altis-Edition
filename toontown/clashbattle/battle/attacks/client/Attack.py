import random
from time import time
from enum import Enum, auto

from panda3d.core import Point3, Vec3
from toontown.chat.constants.ChatGlobals import  CFSpeech, CFTimeout
from direct.interval.IntervalGlobal import *
from direct.showbase.DirectObject import DirectObject

from toontown.audio.IsolatedSoundInterval import IsolatedSoundInterval
from toontown.clashbattle.battle import MovieUtil, SuitBattleGlobals
from toontown.clashbattle.battle.BattleAvatar import BattleAvatar
from toontown.clashbattle.battle.BattleCamera import BattleCamera
from toontown.clashbattle.battle.BattleSounds import globalBattleSoundCache
from toontown.clashbattle.battle.attacks.base.AttackGlobals import getTauntPool
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.attacks.base.AttackTarget import AttackTarget
from toontown.gui.game.condition import ConditionGlobals
from toontown.clashbattle.battle.visuals.VisualEffectEnums import VisualEffectEnum
from toontown.clashbattle.battle import BattleGlobals
from toontown.hood import ZoneUtil
from toontown.clashsuit.suit.ClashSuitBase import ClashSuitBase
from toontown.toon.ClashDistributedToonBase import ClashDistributedToonBase
from toontown.toonbase import TTLocalizer
from toontown.utils.AstronStruct import AstronStruct
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


class AttackAnimKeys(Enum):
    Anim = auto()
    Delay = auto()
    Duration = auto()
    StartTime = auto()
    PlayRate = auto()
    Actor = auto()


@DirectNotifyCategory()
class Attack(AstronStruct, DirectObject):
    """
    Attack: the base class for all attack movies.

    :param attackIndex: The index of the attack.
    :param attackType: The enum value of the attack.
    :param invokerId: The attack invoker's doId.
    :param targets: A list of AttackTarget objects in struct
    form, sent by the server.
    :param level (toon): The level of the gag track.
    :param target (toon): The target of the attack.
    :param taunt (suit): The taunt index.
    :param extraArgs: Any extra arguments.
    """

    __slots__ = (
        # General parameters
        "attackIndex", "attackType", "invokerId", "targets", "extraArgs",
        "invoker", "toons", "suits", "targetObjs", "movie", "playByPlayText",
        "battle", "identifier", "targetDicts",
        
        # Toon specific parameters
        "level", "target",
        
        # Suit specific parameters
        "taunt",
    )

    OPEN_SHOT_DUR = 3.5

    pbpDelay = 0.0
    pbpSubtextDelay = 0.0
    pbpWordwrapMult = 1.0
    pbpFadeInMult = 0.1
    pbpSubtextFadeInMult = 0.2
    pbpFadeOutMult = 0.7

    ANIM_NAME = ""
    CHEAT = False

    forceLoopNeutral = True

    # Determines whether this type of attack will animate
    # in parallel.
    ALLOW_GROUPING = False
    
    # Should this attack completely ignore Sketched's futile attempts
    # to make the animations blend? Please say yes please say yes please say yes
    # please say
    DISRESPECT_ANIM_BLEND = False

    # Do we care to show the play-by-play text?
    SHOW_PLAY_BY_PLAY = True

    # Does this attack want target indicators?
    WANT_TARGET_INDICATORS = True

    def __init__(self, attackIndex: int, attackType: AttackEnum, invokerId: int, targets: list,
                 level: int, target: int, taunt: int, extraArgs: list) -> None:
        self.attackIndex = attackIndex
        self.attackType = attackType
        self.invokerId = invokerId
        self.targets = AttackTarget.fromStructList(targets)
        self.extraArgs = extraArgs

        # Toon specific fields.
        self.level = level
        self.target = target

        # Suit specific fields.
        self.taunt = taunt

        # Fields set by the movie after initialization.
        self.invoker = None
        self.toons = []
        self.suits = []
        self.targetObjs = []
        self.movie = None
        self.playByPlayText = None
        self.battle = None
        self.shownUnlureMovie = False

        # Unique identifier for task names.
        self.identifier = time()

        # A list of dictionaries containing information
        # about each target.
        self.targetDicts = []  # type: list[dict]

    def toStruct(self) -> list:
        return [
            self.attackIndex, self.attackType,
            self.invokerId, AttackTarget.toStructList(self.targets),
            self.level, self.target, self.taunt, self.extraArgs,
        ]

    @property
    def landed(self) -> bool:
        return any(result.landed for result in self.targets)
    
    @property
    def camera(self) -> BattleCamera:
        return self.battle.camera

    @staticmethod
    def isToon(target: BattleAvatar) -> bool:
        return isinstance(target, ClashDistributedToonBase)

    @staticmethod
    def isSuit(target: BattleAvatar) -> bool:
        return isinstance(target, ClashSuitBase)
    
    def sendLocalToonAway(self, zoneId: int, exitState: str='Died') -> None:
        place = base.cr.playGame.getPlace()
        shardId = None
        if getattr(base.cr, 'districtMgr', None):
            shardId = base.cr.districtMgr.getDrainTarget(checkDelayDeletes=True)

        if place:
            place.request(exitState, {
                'loader': ZoneUtil.getLoaderName(zoneId),
                'where': ZoneUtil.getWhereName(zoneId, 1),
                'how': 'TeleportIn',
                'hoodId': ZoneUtil.getHoodId(zoneId),
                'zoneId': zoneId,
                'shardId': shardId,
                'avId': -1,
                'battle': 1,
                'quick': 1,
            })

    def findTarget(self, targetId: int) -> AttackTarget:
        targets = [tgt for tgt in self.targets if tgt.avId == targetId]
        return targets[0]
    
    def findAvatar(self, avId: int):
        return self.battle.findSuit(avId) or self.battle.findToon(avId)
    
    def findTargetDict(self, targetId: int) -> dict:
        targets = [tgt for tgt in self.targetDicts if tgt["avatar"].doId == targetId]
        return targets[0]

    def setTargets(self) -> bool:
        """
        Creates a list of target dictionaries for the attack movie.
        """
        for target in self.targetObjs:
            result = self.findTarget(target.doId)

            if self.isToon(target):
                if target not in self.battle.activeToons:
                    self.notify.warning(f"Target {target.doId} not in active toons!")
                    continue
                toonIndex = self.battle.activeToons.index(target)
                rightToons = [self.battle.activeToons[ti] for ti in range(toonIndex)]

                lenToons = len(self.battle.activeToons)
                leftToons = []
                if lenToons > toonIndex + 1:
                    for ti in range(toonIndex + 1, lenToons):
                        leftToons.append(self.battle.activeToons[ti])

                self.targetDicts.append({
                    "avatar": target,
                    "hp": result.hpAdjust,
                    "died": result.died,
                    "landed": result.landed,
                    "leftToons": leftToons,
                    "rightToons": rightToons,
                })

            elif self.isSuit(target):
                if target not in self.battle.activeSuits:
                    self.notify.warning(f"Target {target.doId} not in active suits!")
                    continue
                suitIndex = self.battle.activeSuits.index(target)

                leftSuits = []
                for si in range(0, suitIndex):
                    asuit = self.battle.activeSuits[si]
                    if not asuit.isLured:
                        leftSuits.append(asuit)

                lenSuits = len(self.battle.activeSuits)
                rightSuits = []
                if lenSuits > suitIndex + 1:
                    for si in range(suitIndex + 1, lenSuits):
                        asuit = self.battle.activeSuits[si]
                        if not asuit.isLured:
                            rightSuits.append(asuit)

                self.targetDicts.append({
                    "avatar": target,
                    "leftSuits": leftSuits,
                    "rightSuits": rightSuits,
                    "hp": result.hpAdjust,
                    "died": result.died,
                    "revive": result.revived,
                    "landed": result.landed,
                })
        return False
    
    def getTauntPool(self, suit, attackType, rounds, tauntIndex) -> list:
        return getTauntPool(suit, attackType, rounds, tauntIndex)

    def getAttackTaunt(self):
        # Grab our proper taunt pool.
        taunt, tauntIndex = self.taunt
        taunts = self.getTauntPool(self.invoker, self.attackType, self.battle.currRound, tauntIndex)
        if taunt >= len(taunts):
            return TTLocalizer.SuitAttackDefaultTaunts[0]
        return taunts[taunt]

    def getAttackMovie(self):
        attackTrack = Sequence(Func(self.doConditionCallout), self.doAttack())
        attackTrack.append(self.getEndTrack())
        camTrack = self.chooseCameraShot(attackTrack.getDuration())
        return attackTrack, camTrack

    def doConditionCallout(self):
        """
        Informs the Toons that they are being targeted.
        """
        if not self.WANT_TARGET_INDICATORS:
            # Ignore if this attack doesn't want target indicators
            return

        toons = []
        for targetDict in self.targetDicts:
            av = targetDict.get('avatar')
            if self.isToon(av):
                hp = targetDict.get('hp')
                if (hp is not None and hp <= 0) or not targetDict['landed']:
                    toons.append(av)

        if len(toons):
            messenger.send(BattleGlobals.BattleAvatarTargetedMessage, [toon.doId for toon in toons])

    def doAttack(self):
        """
        Returns the sequence of the attack.
        By default, it returns an empty sequence.
        """
        return Sequence()

    def chooseCameraShot(self, duration):
        """
        Returns the camera shot and the text that should display for
        the suit attack.
        """
        if duration < 0:
            duration = 1e-06

        camTrack = Sequence()
        camTrack.append(self.getCameraShot(duration))

        # Reason we are making this a method is because we want this executed as the movie is happening, not before
        def getTextColor():
            if self.CHEAT:
                return (0.45, 0.45, 1.0, 1.0)
            elif self.invoker and self.invoker.isSupercharged():
                return (1, 0, 1, 1)
            else:
                return (1, 0, 0, 1)

        def getTextPos():
            if self.CHEAT:
                return (0.0, 0.775)
            else:
                return (0.0, 0.75)

        displayName = self.getAttackDisplayName()

        if self.SHOW_PLAY_BY_PLAY:
            pbpTrack = self.playByPlayText.getShowInterval(
                displayName,
                duration,
                colorOverride=getTextColor,
                posOverride=getTextPos,
                pbpDelay=self.pbpDelay,
                pbpSubtextDelay=self.pbpSubtextDelay,
                wordwrapMult=self.pbpWordwrapMult,
                fadeInMult=self.pbpFadeInMult,
                subtextFadeInMult=self.pbpSubtextFadeInMult,
                fadeOutMult=self.pbpFadeOutMult,
            )
        else:
            pbpTrack = Sequence()

        return Parallel(camTrack, pbpTrack)

    def getAttackDisplayName(self) -> str:
        return TTLocalizer.SuitAttackNames.get(self.attackType, "")

    def getCameraShot(self, duration):
        if len(self.targetDicts) == 1:
            return self.camera.heldRelativeShot(
                self.targetDicts[0]["avatar"],
                0, 12, 13,
                180, -30, 0,
                duration,
                "singleAvatarShot",
            )
        return self.camera.allGroupOverheadShot(duration=duration)

    def getEndTrack(self):
        """Create necessary death/revive tracks for SUITS that died or revived due to this attack."""
        deathReviveTracks = Parallel()

        for target in self.targetObjs:
            if self.isSuit(target):
                result = self.findTarget(target.doId)
                if result.died:
                    deathReviveTracks.append(self.getSuitDeathMovie(target))
                elif result.revived:
                    deathReviveTracks.append(self.getSuitReviveMovie(target))

        # Return their death sequence.
        return Sequence(deathReviveTracks)

    def getSuitReviveMovie(self, suit):
        return MovieUtil.createSuitReviveTrack(suit, None, self.battle, [])

    def getSuitDeathMovie(self, suit):
        return MovieUtil.createSuitDeathTrack(suit, None, self.battle, [])

    def getDeadToonsEventName(self):
        return f"show-dead-toons-{self.attackType}-{self.identifier}"

    """
    These functions are entirely used for creating suit attack movies.
    """

    def getResetTrack(self, suit=None):
        suit = suit or self.invoker
        if not suit or not suit.isLured:
            return Sequence()

        self.shownUnlureMovie = True
        return MovieUtil.createSuitUnlureTrack(suit, self.battle)

    def getSuitTrack(self, delay=1e-06, wantSpeechHeadAnim=True, splicedAnims=None, playRate: float = 1.0, wantDialog=True):
        if self.invoker is None:
            return Sequence()
        if self.battle.getActorPosHpr(self.invoker) is None:
            return Sequence()
        if not self.targetDicts:
            return Sequence()
        toon = self.targetDicts[0]["avatar"]
        targetPos = toon.getPos(self.battle)
        if wantDialog:
            chatFunc = (
                self.invoker.setChatIterative
                if self.invoker.style.name in SuitBattleGlobals.ITERATIVE_CHAT
                else self.invoker.setChatAbsolute
            )
            taunt = self.modifyTauntString(self.getAttackTaunt())
            tauntFunc = Func(chatFunc, taunt, CFSpeech | CFTimeout, wantHeadAnim=wantSpeechHeadAnim)
        else:
            tauntFunc = Sequence()
        track = Sequence(Wait(delay), tauntFunc)
        trapStorage = {}
        trapStorage["trap"] = None

        def reparentTrap(trapStorage=trapStorage):
            trapProp = self.invoker.battleTrapProp
            if trapProp is not None and not trapProp.isEmpty():
                trapProp.wrtReparentTo(self.battle)
                trapStorage["trap"] = trapProp

        blendNeutral = self.invoker.getAnimBlendNeutralData()
        origPos, origHpr = self.battle.getActorPosHpr(self.invoker)

        # Do some work to determine if we need to play the shuffle adjust anim or not
        foo = self.battle.attachNewNode('foo')
        foo.setPos(origPos)
        foo.headsUp(self.battle, targetPos)
        if foo.getH(self.battle) < 0:
            foo.setH(self.battle, foo.getH(self.battle) + 360)
        suitHeadsUpHpr = foo.getHpr(self.battle)
        # Shuffle anim only plays on noticeable H changes
        needShuffle = abs(origHpr[0] - suitHeadsUpHpr[0]) > 2
        foo.removeNode()

        track.append(Func(reparentTrap))
        track.append(Func(self.invoker.headsUp, self.battle, targetPos))
        if splicedAnims:
            track.append(self.getSplicedAnimsTrack(splicedAnims, actor=self.invoker))
        else:
            animSeq = Parallel(ActorInterval(self.invoker, self.getAnimName(), playRate=playRate))
            # Add animation blending between neutral and the wanted attack if this suit
            # has a custom neutral animation.
            # Most attack animations are made with the standard neutral animation in mind,
            # so we're going to cover that up a bit by applying animation blending.
            if blendNeutral and not self.DISRESPECT_ANIM_BLEND:
                neutralAnim = self.invoker.getAnim("neutral", VisualEffectEnum.LURED)
                blendNeutralT = blendNeutral.get("time", 0)
                blendNeutralEase = blendNeutral.get("blendType", "noBlend")
                animSeq.append(
                    ActorInterval(self.invoker, neutralAnim, duration=blendNeutralT)
                )
                animSeq.append(
                    LerpAnimInterval(
                        self.invoker,
                        blendNeutralT,
                        neutralAnim,
                        self.getAnimName(),
                        blendType=blendNeutralEase,
                    )
                )

                animSeq = Parallel(
                    animSeq,
                    Sequence(
                        Func(
                            self.invoker.setBlend,
                            frameBlend=base.wantSmoothAnims,
                            animBlend=True,
                        ),
                        Wait(blendNeutralT),
                        Func(
                            self.invoker.setBlend,
                            frameBlend=base.wantSmoothAnims,
                            animBlend=False,
                        ),
                    )
                )

            track.append(animSeq)

        if needShuffle:
            def loopInvokerAnim(invoker, battle, origHpr, headsUpHpr):
                invoker.play(f"shuffle-{'left' if origHpr[0] > headsUpHpr[0] else 'right'}")

            track.append(Sequence(
                Func(loopInvokerAnim, self.invoker, self.battle, origHpr, suitHeadsUpHpr),
                LerpHprInterval(self.invoker, 10/24, origHpr, startHpr=suitHeadsUpHpr, other=self.battle),
            ))

        neutralSeq = Func(self.neutralAvatar) if self.invoker.getWantEndAttackNeutral() else Sequence()
        if blendNeutral and not self.DISRESPECT_ANIM_BLEND:
            neutralAnim = self.invoker.getAnim("neutral", VisualEffectEnum.LURED)
            blendNeutralT = blendNeutral.get("time", 0)
            blendNeutralEase = blendNeutral.get("blendType", "noBlend")
            neutralSeq = Sequence(
                Parallel(
                    Func(
                        self.invoker.setBlend,
                        frameBlend=base.wantSmoothAnims,
                        animBlend=True,
                    ),
                    ActorInterval(self.invoker, neutralAnim, duration=blendNeutralT),
                    LerpAnimInterval(
                        self.invoker,
                        blendNeutralT,
                        self.getAnimName(),
                        neutralAnim,
                        blendType=blendNeutralEase,
                    ),
                ),
                Wait(0.01),
                neutralSeq,
                Func(
                    self.invoker.setBlend,
                    frameBlend=base.wantSmoothAnims,
                    animBlend=False,
                ),
            )

        track.append(Sequence(Wait(0.01), neutralSeq))
        track.append(Func(self.invoker.setHpr, self.battle, origHpr))

        def returnTrapToSuit(trapStorage=trapStorage):
            trapProp = trapStorage["trap"]
            if trapProp is not None and not trapProp.isEmpty():
                if trapProp.getName() == "traintrack":
                    self.notify.debug("deliberately not parenting traintrack to suit")
                else:
                    trapProp.wrtReparentTo(self.invoker)
                self.invoker.battleTrapProp = trapProp

        track.append(Func(returnTrapToSuit))
        return track

    def doDamage(self, toon, dmg, died, extraText=""):
        if dmg < 0 and toon.getHp() is not None:
            toon.takeDamage(-dmg, extraText=extraText)

    def showProp(self, prop, parent, pos, hpr=None, scale=None):
        prop.reparentTo(parent)
        prop.setPos(pos)
        if hpr:
            prop.setHpr(hpr)
        if scale:
            prop.setScale(scale)

    def animProp(self, prop, propName, propType="actor"):
        if "actor" == propType:
            prop.play(propName)
        elif "model" == propType:
            pass
        else:
            self.notify.error(f"No such propType as: {propType}")

    def suitFacePoint(self, suit, zOffset=0):
        pnt = suit.getPos()
        pnt.setZ(pnt[2] + suit.shoulderHeight + 0.3 + zOffset)
        return Point3(pnt)

    def toonFacePoint(self, toon, zOffset=0, parent=render):
        pnt = toon.getPos(parent)
        pnt.setZ(pnt[2] + toon.shoulderHeight + 0.3 + zOffset)
        return Point3(pnt)

    def toonTorsoPoint(self, toon, zOffset=0):
        pnt = toon.getPos()
        pnt.setZ(pnt[2] + toon.shoulderHeight - 0.2)
        return Point3(pnt)

    def toonGroundPoint(self, toon, zOffset=0, parent=render):
        pnt = toon.getPos(parent)
        pnt.setZ(self.battle.getZ(parent) + zOffset)
        return Point3(pnt)

    def toonGroundMissPoint(self, prop, toon, zOffset=0):
        point = self.toonMissPoint(prop, toon)
        point.setZ(self.battle.getZ() + zOffset)
        return Point3(point)

    def toonMissPoint(self, prop, toon, yOffset=0, parent=None):
        if parent:
            p = self.toonFacePoint(toon) - prop.getPos(parent)
        else:
            p = self.toonFacePoint(toon) - prop.getPos()
        v = Vec3(p)
        baseDistance = v.length()
        v.normalize()
        if parent:
            endPos = prop.getPos(parent) + v * (baseDistance + 5 + yOffset)
        else:
            endPos = prop.getPos() + v * (baseDistance + 5 + yOffset)
        return Point3(endPos)

    def toonMissBehindPoint(self, toon, parent=render, offset=0):
        point = toon.getPos(parent)
        point.setY(point.getY() - 5 + offset)
        return point

    def throwBounceHitPoint(self, prop, toon):
        startPoint = prop.getPos()
        endPoint = self.toonFacePoint(toon)
        return self.throwBouncePoint(startPoint, endPoint)

    def throwBounceMissPoint(self, prop, toon):
        startPoint = prop.getPos()
        endPoint = self.toonFacePoint(toon)
        return self.throwBouncePoint(startPoint, endPoint)

    def throwBouncePoint(self, startPoint, endPoint):
        midPoint = startPoint + (endPoint - startPoint) / 2.0
        midPoint.setZ(0)
        return Point3(midPoint)

    def getSoundTrack(self, fileName, delay=0.01, duration=None, node=None, isolated: bool = False, playRate: float = 1.0, volume: float = 1.0, startTime: float = 0.0):
        soundEffect = globalBattleSoundCache.getSound(fileName)
        intervalClass = IsolatedSoundInterval if isolated else SoundInterval

        if playRate != 1.0:
            soundIval = intervalClass(soundEffect, duration=duration if duration is not None else 0.0, node=node, volume=volume, startTime=startTime)

            def setPlayRate(t: float):
                if soundIval.sound:
                    soundIval.sound.setPlayRate(playRate)

            return Sequence(
                Wait(delay),
                Func(setPlayRate, playRate),
                soundIval,
                Func(setPlayRate, 1.0),
            )
        elif duration:
            return Sequence(
                Wait(delay), intervalClass(soundEffect, duration=duration, node=node, volume=volume, startTime=startTime)
            )
        else:
            return Sequence(Wait(delay), intervalClass(soundEffect, node=node, volume=volume, startTime=startTime))

    def getAnimName(self):
        return self.ANIM_NAME

    def modifyTauntString(self, tauntStr):
        return tauntStr

    def getSuitAnimTrack(
        self, delay=0, doActorInterval=True, wantSpeechHeadAnim=True, forceWait=0, wantDialog=True, playRate: float = 1.0
    ):
        if wantDialog:
            chatFunc = (
                self.invoker.setChatIterative
                if self.invoker.style.name in SuitBattleGlobals.ITERATIVE_CHAT
                else self.invoker.setChatAbsolute
            )
            taunt = self.modifyTauntString(self.getAttackTaunt())
            tauntFunc = Func(chatFunc, taunt, CFSpeech | CFTimeout, wantHeadAnim=wantSpeechHeadAnim)
        else:
            tauntFunc = Sequence()

        blendNeutral = self.invoker.getAnimBlendNeutralData()

        def getActorInterval(blendNeutral=blendNeutral):
            if not doActorInterval:
                return Sequence()

            animSeq = Parallel(ActorInterval(self.invoker, self.getAnimName(), playRate=playRate))
            # Add animation blending between neutral and the wanted attack if this suit
            # has a custom neutral animation.
            # Most attack animations are made with the standard neutral animation in mind,
            # so we're going to cover that up a bit by applying animation blending.
            if blendNeutral:
                neutralAnim = self.invoker.getAnim("neutral", VisualEffectEnum.LURED)
                blendNeutralT = blendNeutral.get("time", 0)
                blendNeutralEase = blendNeutral.get("blendType", "noBlend")
                animSeq.append(
                    ActorInterval(self.invoker, neutralAnim, duration=blendNeutralT)
                )
                animSeq.append(
                    LerpAnimInterval(
                        self.invoker,
                        blendNeutralT,
                        neutralAnim,
                        self.getAnimName(),
                        blendType=blendNeutralEase,
                    )
                )

                animSeq = Parallel(
                    animSeq,
                    Sequence(
                        Func(
                            self.invoker.setBlend,
                            frameBlend=base.wantSmoothAnims,
                            animBlend=True,
                        ),
                        Wait(blendNeutralT),
                        Func(
                            self.invoker.setBlend,
                            frameBlend=base.wantSmoothAnims,
                            animBlend=False,
                        ),
                    )
                )

            return animSeq

        if not doActorInterval:
            neutralSeq = Sequence()
        else:
            neutralSeq = Func(self.neutralAvatar) if self.invoker.getWantEndAttackNeutral() else Sequence()
            if blendNeutral:
                neutralAnim = self.invoker.getAnim("neutral", VisualEffectEnum.LURED)
                blendNeutralT = blendNeutral.get("time", 0)
                blendNeutralEase = blendNeutral.get("blendType", "noBlend")
                neutralSeq = Sequence(
                    Func(
                        self.invoker.setBlend,
                        frameBlend=base.wantSmoothAnims,
                        animBlend=True,
                    ),
                    Parallel(
                        ActorInterval(self.invoker, neutralAnim, duration=blendNeutralT),
                        LerpAnimInterval(
                            self.invoker,
                            blendNeutralT,
                            self.getAnimName(),
                            neutralAnim,
                            blendType=blendNeutralEase,
                        ),
                    ),
                    neutralSeq,
                    Func(
                        self.invoker.setBlend,
                        frameBlend=base.wantSmoothAnims,
                        animBlend=False,
                    ),
                )

        return Sequence(
            Wait(delay),
            tauntFunc,
            getActorInterval(),
            Sequence() if not forceWait else Wait(forceWait),
            Wait(0.01),
            neutralSeq,
        )

    def getSuitSayTrack(self, delay=0, duration: float = None, wantSpeechHeadAnim=True):
        taunt = self.modifyTauntString(self.getAttackTaunt())
        return Sequence(
            Func(self.invoker.setChatAbsolute, taunt, CFSpeech | CFTimeout, wantHeadAnim=wantSpeechHeadAnim),
            (
                Sequence(
                    Wait(duration),
                    Func(self.invoker.clearChat),
                )
            ) if duration is not None else Wait(0.0)
        )

    def getPartTrack(
        self, particleEffect, startDelay, durationDelay, partExtraArgs, softStop=0
    ):
        particleEffect = partExtraArgs[0]
        parent = partExtraArgs[1]
        if len(partExtraArgs) > 2:
            worldRelative = partExtraArgs[2]
        else:
            worldRelative = 1
        return Sequence(
            Wait(startDelay),
            ParticleInterval(
                particleEffect,
                parent,
                worldRelative,
                duration=durationDelay,
                cleanup=True,
                softStopT=softStop,
            ),
        )

    def getToonTrack(self, damageDelay=1e-06, damageAnimNames=None, dodgeDelay=0.0001, dodgeAnimNames=None, splicedDamageAnims=None,
                     splicedDodgeAnims=None, target=None, showDamageExtraTime=0.01, showMissedExtraTime=0.5, group=0, forceHit=0,
                     hpTextType=None, lookAtInvoker: bool=True, damageAnimPlayRate: float = 1.0, dodgeAnimPlayRate: float = 1.0):
        if not target:
            target = self.targetDicts[0]
        toon = target["avatar"]
        if self.isSuit(toon):
            return Sequence()
        dmg = target["hp"]
        animTrack = Sequence()
        if self.invoker is not None and lookAtInvoker:
            animTrack.append(Func(toon.headsUp, self.invoker))
        if target["landed"] or forceHit:
            animTrack.append(
                self.getToonTakeDamageTrack(
                    toon,
                    target["died"],
                    dmg,
                    damageDelay,
                    damageAnimNames,
                    splicedDamageAnims,
                    showDamageExtraTime,
                    group,
                    hpTextType,
                    damageAnimPlayRate=damageAnimPlayRate,
                )
            )
            return animTrack

        animTrack.append(
            self.getToonDodgeTrack(
                target,
                dodgeDelay,
                dodgeAnimNames,
                splicedDodgeAnims,
                showMissedExtraTime,
                dodgeAnimPlayRate=dodgeAnimPlayRate,
            )
        )

        indicatorTrack = Sequence(
            Wait(dodgeDelay + showMissedExtraTime), Func(MovieUtil.indicateMissed, toon)
        )
        return Parallel(animTrack, indicatorTrack)

    def getToonTracks(self, damageDelay=1e-06, damageAnimNames=None, dodgeDelay=1e-06,
                      dodgeAnimNames=None, splicedDamageAnims=None, splicedDodgeAnims=None,
                      showDamageExtraTime=0.01, showMissedExtraTime=0.5, forceHit=0, hpTextType=None,
                      damageAnimPlayRate: float = 1.0, dodgeAnimPlayRate: float = 1.0):
        toonTracks = Parallel()
        for target in self.targetDicts:
            if self.isSuit(target["avatar"]):
                continue
            toonTracks.append(
                self.getToonTrack(
                    damageDelay,
                    damageAnimNames,
                    dodgeDelay,
                    dodgeAnimNames,
                    splicedDamageAnims,
                    splicedDodgeAnims,
                    target=target,
                    showDamageExtraTime=showDamageExtraTime,
                    showMissedExtraTime=showMissedExtraTime,
                    group=1,
                    forceHit=forceHit,
                    hpTextType=hpTextType,
                    damageAnimPlayRate=damageAnimPlayRate,
                    dodgeAnimPlayRate=dodgeAnimPlayRate,
                )
            )

        return toonTracks

    def getToonDodgeTrack(
        self, target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime, dodgeAnimPlayRate: float = 1.0
    ):
        toon = target["avatar"]
        toonTrack = Sequence()
        toonTrack.append(Wait(dodgeDelay))
        if dodgeAnimNames:
            for d in dodgeAnimNames:
                if d == "sidestep":
                    toonTrack.append(self.getAllyToonsDodgeParallel(target, playRate=dodgeAnimPlayRate))
                else:
                    toonTrack.append(ActorInterval(toon, d, playRate=dodgeAnimPlayRate))
        elif splicedDodgeAnims:
            toonTrack.append(self.getSplicedAnimsTrack(splicedDodgeAnims, actor=toon, playRate=dodgeAnimPlayRate))
        toonTrack.append(Func(toon.loop, "neutral"))
        return toonTrack

    def getAllyToonsDodgeParallel(self, target, playRate: float = 1.0):
        toon = target["avatar"]
        leftToons = target["leftToons"]
        rightToons = target["rightToons"]
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
            sidestepAnim = "sidestep-left"
            soundEffect = globalBattleSoundCache.getSound("AV_side_step.ogg")
        else:
            sidestepAnim = "sidestep-right"
            soundEffect = globalBattleSoundCache.getSound("AV_jump_to_side.ogg")
        toonTracks = Parallel()
        for t in toonDodgeList:
            toonTracks.append(
                Sequence(ActorInterval(t, sidestepAnim, playRate=playRate), Func(t.loop, "neutral"))
            )

        toonTracks.append(
            Sequence(ActorInterval(toon, sidestepAnim, playRate=playRate), Func(toon.loop, "neutral"))
        )
        toonTracks.append(Sequence(Wait(0.5), SoundInterval(soundEffect, node=toon)))
        return toonTracks

    def getPropTrack(
        self,
        prop,
        parent,
        posPoints,
        appearDelay,
        remainDelay,
        scaleUpPoint=Point3(1),
        scaleUpTime=0.5,
        scaleDownTime=0.5,
        startScale=Point3(0.01),
        anim=0,
        propName="none",
        animDuration=0.0,
        animStartTime=0.0,
    ):
        if anim == 1:
            track = Sequence(
                Wait(appearDelay),
                Func(self.showProp, prop, parent, *posPoints),
                LerpScaleInterval(
                    prop, scaleUpTime, scaleUpPoint, startScale=startScale
                ),
                ActorInterval(
                    prop, propName, duration=animDuration, startTime=animStartTime
                ),
                Wait(remainDelay),
                Func(MovieUtil.removeProp, prop),
            )
        else:
            track = Sequence(
                Wait(appearDelay),
                Func(self.showProp, prop, parent, *posPoints),
                LerpScaleInterval(
                    prop, scaleUpTime, scaleUpPoint, startScale=startScale
                ),
                Wait(remainDelay),
                LerpScaleInterval(prop, scaleDownTime, MovieUtil.PNT3_NEARZERO),
                Func(MovieUtil.removeProp, prop),
            )
        return track

    def getPropAppearTrack(
        self,
        prop,
        parent,
        posPoints,
        appearDelay,
        scaleUpPoint=Point3(1),
        scaleUpTime=0.5,
        startScale=Point3(0.01),
        poseExtraArgs=None,
        blendType: str = 'noBlend',
    ):
        propTrack = Sequence(
            Wait(appearDelay), Func(self.showProp, prop, parent, *posPoints)
        )
        if poseExtraArgs:
            propTrack.append(Func(prop.pose, *poseExtraArgs))
        propTrack.append(
            LerpScaleInterval(prop, scaleUpTime, scaleUpPoint, startScale=startScale, blendType=blendType)
        )
        return propTrack

    def getPropThrowTrack(
        self,
        prop,
        hitPoints=[],
        missPoints=[],
        hitDuration=0.5,
        missDuration=0.5,
        hitPointNames="none",
        missPointNames="none",
        lookAt="none",
        groundPointOffSet=0,
        missScaleDown=None,
        parent=render,
        target=None,
    ):
        target = target or self.targetDicts[0]
        toon = target["avatar"]
        dmg = target["hp"]

        def getLambdas(nameList, prop, toon):
            for i in range(len(nameList)):
                if nameList[i] == "face":
                    nameList[i] = lambda: self.toonFacePoint(toon)
                elif nameList[i] == "miss":
                    nameList[i] = lambda: self.toonMissPoint(prop, toon)
                elif nameList[i] == "bounceHit":
                    nameList[i] = lambda: self.throwBounceHitPoint(prop, toon)
                elif nameList[i] == "bounceMiss":
                    nameList[i] = lambda: self.throwBounceMissPoint(prop, toon)

            return nameList

        if hitPointNames != "none":
            hitPoints = getLambdas(hitPointNames, prop, toon)
        if missPointNames != "none":
            missPoints = getLambdas(missPointNames, prop, toon)
        propTrack = Sequence()
        propTrack.append(Func(self.movie.needRestoreRenderProp, prop))
        propTrack.append(Func(prop.wrtReparentTo, parent))
        if lookAt != "none":
            propTrack.append(Func(prop.lookAt, lookAt))
        if dmg < 0:
            for i in range(len(hitPoints)):
                pos = hitPoints[i]
                propTrack.append(LerpPosInterval(prop, hitDuration, pos=pos))

        else:
            for i in range(len(missPoints)):
                pos = missPoints[i]
                propTrack.append(LerpPosInterval(prop, missDuration, pos=pos))

            if missScaleDown:
                propTrack.append(
                    LerpScaleInterval(prop, missScaleDown, MovieUtil.PNT3_NEARZERO)
                )
        propTrack.append(Func(MovieUtil.removeProp, prop))
        propTrack.append(Func(self.movie.clearRenderProp, prop))
        return propTrack

    def getThrowTrack(self, obj, target, duration=1.0, parent=render, gravity=-32.144):
        values = {}

        def calcOriginAndVelocity(
            obj=obj,
            target=target,
            values=values,
            duration=duration,
            parent=parent,
            gravity=gravity,
        ):
            if callable(target):
                target = target()
            obj.wrtReparentTo(parent)
            values["origin"] = obj.getPos(parent)
            origin = obj.getPos(parent)
            values["velocity"] = (
                target[2] - origin[2] - 0.5 * gravity * duration * duration
            ) / duration

        return Sequence(
            Func(calcOriginAndVelocity),
            LerpFunctionInterval(
                self.throwPos,
                fromData=0.0,
                toData=1.0,
                duration=duration,
                extraArgs=[obj, duration, target, values, gravity],
            ),
        )

    def throwPos(self, t, obj, duration, target, values, gravity=-32.144):
        origin = values["origin"]
        velocity = values["velocity"]
        if callable(target):
            target = target()
        x = origin[0] * (1 - t) + target[0] * t
        y = origin[1] * (1 - t) + target[1] * t
        time = t * duration
        z = origin[2] + velocity * time + 0.5 * gravity * time * time
        obj.setPos(x, y, z)

    def getToonTakeDamageTrack(
        self,
        toon,
        died,
        dmg,
        delay,
        damageAnimNames=None,
        splicedDamageAnims=None,
        showDamageExtraTime=0.01,
        group=0,
        hpTextType=None,
        damageAnimPlayRate: float = 1.0
    ):
        toonTrack = Sequence()
        toonTrack.append(Wait(delay))

        # Pass through an int to use its general attack hp text definition
        if hpTextType:
            hpTextInfo = TTLocalizer.GeneralAttackHpTexts[hpTextType]
            text = hpTextInfo[0]
            color = hpTextInfo[1]
        else:
            text = ""
            color = (1, 1, 1, 1)

        if damageAnimNames:
            for d in damageAnimNames:
                toonTrack.append(ActorInterval(toon, d, playRate=damageAnimPlayRate))

            indicatorTrack = Sequence(Wait(delay + showDamageExtraTime))
            if dmg < 0:
                indicatorTrack.append(
                    Func(self.doDamage, toon, dmg, died, extraText=text)
                )
            elif hpTextType is not None:
                indicatorTrack.append(Func(toon.showHpString, text, 0.85, 0.7, color))
        else:
            if splicedDamageAnims is not None:
                splicedAnims = self.getSplicedAnimsTrack(splicedDamageAnims, actor=toon, playRate=damageAnimPlayRate)
                toonTrack.append(splicedAnims)
            indicatorTrack = Sequence(Wait(delay + showDamageExtraTime))
            if dmg < 0:
                indicatorTrack.append(
                    Func(self.doDamage, toon, dmg, died, extraText=text)
                )
            elif hpTextType is not None:
                indicatorTrack.append(Func(toon.showHpString, text, 0.85, 0.7, color))
        toonTrack.append(Func(toon.loop, "neutral"))
        return Parallel(toonTrack, indicatorTrack)

    def getSplicedAnimsTrack(self, anims, actor=None, playRate=1.0):
        track = Sequence()
        for nextAnim in anims:
            delay = 1e-06
            if type(nextAnim) is dict:
                # Alternate Dict method of setting anims which has a bit more finetune control
                theAnim = nextAnim[AttackAnimKeys.Anim]
                delay = nextAnim.get(AttackAnimKeys.Delay, delay)
                startTime = nextAnim.get(AttackAnimKeys.StartTime)
                duration = nextAnim.get(AttackAnimKeys.Duration)
                playRate = nextAnim.get(AttackAnimKeys.PlayRate, 1.0)

                if delay > 0:
                    track.append(Wait(delay))
                track.append(ActorInterval(actor, theAnim, startTime=startTime, duration=duration, playRate=playRate))
            else:
                if len(nextAnim) >= 2:
                    if nextAnim[1] > 0:
                        delay = nextAnim[1]
                if len(nextAnim) <= 0:
                    track.append(Wait(delay))
                elif len(nextAnim) == 1:
                    track.append(ActorInterval(actor, nextAnim[0], playRate=playRate))
                elif len(nextAnim) == 2:
                    track.append(Wait(delay))
                    track.append(ActorInterval(actor, nextAnim[0], playRate=playRate))
                elif len(nextAnim) == 3:
                    track.append(Wait(delay))
                    track.append(
                        ActorInterval(
                            actor, nextAnim[0], startTime=nextAnim[2]/playRate, playRate=playRate
                        )
                    )
                elif len(nextAnim) == 4:
                    track.append(Wait(delay))
                    duration = nextAnim[3]
                    if duration < 0:
                        startTime = nextAnim[2]
                        endTime = startTime + duration
                        if endTime <= 0:
                            endTime = 0.01
                        track.append(
                            ActorInterval(
                                actor,
                                nextAnim[0],
                                startTime=startTime/playRate,
                                endTime=endTime/playRate,
                                playRate=playRate,
                            )
                        )
                    else:
                        track.append(
                            ActorInterval(
                                actor,
                                nextAnim[0],
                                startTime=nextAnim[2]/playRate,
                                duration=duration/playRate,
                                playRate=playRate,
                            )
                        )
                elif len(nextAnim) == 5:
                    track.append(Wait(delay))
                    track.append(
                        ActorInterval(
                            nextAnim[4],
                            nextAnim[0],
                            startTime=nextAnim[2]/playRate,
                            duration=nextAnim[3]/playRate,
                            playRate=playRate,
                        )
                    )

        return track

    def getSplicedLerpAnims(
        self, ANIM_NAME, origDuration, newDuration, startTime=0, fps=30, reverse=0
    ):
        anims = []
        addition = 0
        numAnims = origDuration * fps
        timeInterval = newDuration / numAnims
        animInterval = origDuration / numAnims
        if reverse == 1:
            animInterval = -animInterval
        for i in range(0, int(numAnims)):
            anims.append([ANIM_NAME, timeInterval, startTime + addition, animInterval])
            addition += animInterval

        return anims

    def findSuit(self, name: str):
        for target in self.targetObjs:
            if self.isSuit(target) and target.dna.name == name:
                return target

    def neutralAvatar(self):
        """
        Lets the avatar loop neutral.
        """
        if self.forceLoopNeutral:
            self.invoker.neutralAvatar()

    @staticmethod
    def updateSuitHP(suit: ClashSuitBase, hp: int, nonZero: bool=False) -> None:
        suit.updateHealthBar(hp)
        if nonZero and hp == 0:
            return
        suit.showHpText(hp)
    
    def findLocalToonTarget(self):
        for target in self.targetDicts:
            if target["avatar"].isLocal():
                return target["avatar"]
        return random.choice(self.targetDicts)["avatar"]

    def makeActorHPositive(self, actor):
        if actor.getH(self.battle) < 0:
            actor.setH(self.battle, actor.getH(self.battle) + 360)
