import random
from typing import List

from direct.interval.IntervalGlobal import *

from toontown.clashbattle.battle import BattleGlobals, MovieUtil
from toontown.clashsuit.suit import SuitDNA, SuitGlobals
from toontown.clashsuit.suit.DistributedSuitBase import DistributedSuitBase
from toontown.toon.DistributedToonBase import DistributedToonBase
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from toontown.clashbattle.battle.distributed.DistributedBattleBase import DistributedBattleBase


@DirectNotifyCategory()
class BattleCamera:
    """BattleCamera: Manages the camera throughout the battle."""

    POS_WAIT_FOR_INPUT = BattleGlobals.BattleCamDefaultPos
    HPR_WAIT_FOR_INPUT = BattleGlobals.BattleCamDefaultHpr
    FOV_WAIT_FOR_INPUT = BattleGlobals.BattleCamMenuFov

    AUTO_WAITFORINPUT_HEIGHT = True

    def __init__(self, battle) -> None:
        self.toons = []  # type: List[DistributedToonBase]
        self.suits = []  # type: List[DistributedSuitBase]
        self.battle = battle  # type: DistributedBattleBase

        self._seq: Sequence = None
        self._hasEnteredWaitForInput = False

    def cleanup(self) -> None:
        del self.toons
        del self.suits
        del self.battle

        self.finishSequence()
        del self._seq

    def updateMembers(self, toons, suits) -> None:
        self.toons = toons
        self.suits = suits

    def finishSequence(self) -> None:
        if self._seq is not None:
            self._seq.finish()
            self._seq = None

    """
    Positional getters
    """

    def getPosWaitForInput(self):
        return self.POS_WAIT_FOR_INPUT

    def getHprWaitForInput(self):
        return self.HPR_WAIT_FOR_INPUT

    def getFovWaitForInput(self):
        return self.FOV_WAIT_FOR_INPUT

    """
    Common camera manipulations
    """

    def enterWaitForInput(self, **kwargs) -> None:
        """Move the camera into position for the input state of battle."""

        if camera.getParent() != self.battle:
            camera.wrtReparentTo(self.battle)
        if kwargs.get('autoCamHeight', True) and self.AUTO_WAITFORINPUT_HEIGHT:
            camHeight = max([suit.getHeight() + 1 for suit in self.suits])
            self.getPosWaitForInput().setZ(max(camHeight * 2, 16.5))
        duration = 0.4
        self._hasEnteredWaitForInput = True
        self._seq = camera.posHprInterval(
            duration, self.getPosWaitForInput(), self.getHprWaitForInput(), blendType="easeInOut"
        )
        self._seq.start()
        base.camLens.setMinFov(self.getFovWaitForInput() / (4.0 / 3.0))

    def exitWaitForInput(self):
        """Nothing happens here, normally. Subclasses can override."""
        pass

    """
    Common camera shots
    """

    def focusShot(self, pos, duration, target, other=None, splitFocusPoint=None):
        """focusShot() creates a held shot with camera focused on target arg"""
        track = Sequence()
        if other:
            track.append(Func(camera.setPos, other, pos))
        else:
            track.append(Func(camera.setPos, pos))
        if splitFocusPoint:
            track.append(Func(self.focusCameraBetweenPoints, target, splitFocusPoint))
        else:

            def lookAtTarget():
                camera.lookAt(target() if callable(target) else target)

            track.append(Func(lookAtTarget))
        track.append(Wait(duration))
        return track

    def focusMoveShot(self, pos, duration, target, other=None, name="focusMoveShot"):
        """focusMoveShot() creates a moving shot from the current position to focus
        on the target arg provided"""

        def getMotionEndHpr():
            lookAtPos = target() if callable(target) else target

            # Store original camera state to revert after getting info.
            originalPos = camera.getPos()
            originalHpr = camera.getHpr()

            # Position camera to get the desired hpr
            camera.setPos(pos)
            camera.lookAt(lookAtPos)
            hpr = camera.getHpr()

            # Reset camera state
            camera.setPos(originalPos)
            camera.setHpr(originalHpr)
            return hpr

        return self.motionShot(pos, getMotionEndHpr, duration, other, name)

    @staticmethod
    def heldShot(x, y, z, h, p, r, duration, name="heldShot"):
        track = Sequence(name=name)
        # Let the camera display the toons
        track.append(Func(camera.setPosHpr, x, y, z, h, p, r))
        # Hold that pose
        track.append(Wait(duration))
        return track

    @staticmethod
    def heldRelativeShot(other, x, y, z, h, p, r, duration, name="heldRelativeShot"):
        track = Sequence(name=name)
        # Let the camera display the toons
        track.append(Func(camera.setPosHpr, other, x, y, z, h, p, r))
        # Hold that pose
        track.append(Wait(duration))
        return track

    @staticmethod
    def heldRelativeHeadsUpShot(
        other, x, y, z, headsUpObject, duration, name="heldRelativeHeadsUpShot"
    ):
        track = Sequence(name=name)
        # Let the camera display the toons
        track.append(Func(camera.setPos, other, x, y, z))
        # Heads up the camera towards the given object
        track.append(Func(camera.headsUp, headsUpObject))
        # Hold that pose
        track.append(Wait(duration))
        return track

    @staticmethod
    def motionShot(pos, hpr, duration, other=None, name="motionShot"):
        if other:  # If an other parent exists, use it
            posTrack = LerpPosInterval(camera, duration, pos=pos, other=other)
            hprTrack = LerpHprInterval(camera, duration, hpr=hpr, other=other)
        else:
            posTrack = LerpPosInterval(camera, duration, pos=pos)
            hprTrack = LerpHprInterval(camera, duration, hpr=hpr)
        return Parallel(posTrack, hprTrack, name=name)

    @staticmethod
    def hprShot(hpr, duration, other=None, name="hprShot"):
        if other:  # If an other parent exists, use it
            hprTrack = LerpHprInterval(camera, duration, hpr=hpr, other=other)
        else:
            hprTrack = LerpHprInterval(camera, duration, hpr=hpr)
        return Sequence(hprTrack, name=name)

    """
    Various camera shots
    """

    def suitCameraShakeShot(self, duration, shakeIntensity, quake=0, extraDelay=0.0):
        track = Sequence(name="suitShakeCameraShot")
        if quake == 1:
            shakeDelay = 1.375
            numShakes = 4
            postShakeDelay = 0.75
        else:
            shakeDelay = 0.525
            numShakes = 5
            postShakeDelay = 0.5
        shakeDuration = (duration - shakeDelay - postShakeDelay - extraDelay) / numShakes

        def shakeCameraTrack(shakeIntensity, perShakeDuration, numShakes=4, shakeRate=60.0):
            import random
            shakeTrack = Sequence(name='miniShakeCameraShot')

            # calculate how quick we move each random shake in each stomp
            playRate = 1.0 / shakeRate
            # determine how many mini-shakes per stomp
            miniShakeAmt = int(perShakeDuration / playRate)

            # for each stomp (numShakes), calculate randomness of shake
            for shakeNo in range(numShakes):
                # determine each mini-shake in each stomp with shakeDuration / play rate
                # shakeTrack.append(Func(print, f"shakeIntensity={shakeIntensity}, perShakeDuration={perShakeDuration}, numShakes={numShakes}, shakeRate={shakeRate}, miniShakeAmt={miniShakeAmt}"))
                for playIter in range(miniShakeAmt):
                    randY = (random.random() * 2) - 1
                    randZ = (random.random() * 2) - 1
                    # set x & z with a displacement that depends on 'how long' we've been shaking the screen for
                    displacement = (1 - (playIter / miniShakeAmt)) * shakeIntensity
                    # clamp ranges within [-1.0, 1.0) for camera.lookAt()
                    randY = min(max(randY * displacement, -1.0), 1.0)
                    randZ = min(max(randZ * displacement, -1.0), 1.0)
                    # shakeTrack.append(Func(print, f"playIter {playIter}, x={randY}, z={randZ}, displacement={displacement}"))
                    shakeTrack.append(Func(camera.lookAt, 0, randY, randZ))
                    # make sure the camera waits for this mini-shake to finish before going to the next mini-shake
                    shakeTrack.append(Wait(playRate))
                # reset to pos(0, 0, 0) after each stomp
                shakeTrack.append(Func(camera.lookAt, 0, 0, 0))

            # return the shake sequence that we have thus calculated with dark magicks
            return shakeTrack

        # Allow a reasonable degree of randomness in the camera's positioning
        x = 13 + random.random() * 3
        if random.random() > 0.5:
            x = -x
        z = 12 + random.random() * 3
        # Let the camera display the toons
        track.append(Func(camera.setPos, x, -5, z))

        # Point the camera at the center of the battle, to shoot all the actors
        track.append(Func(camera.lookAt, Point3(0, 0, 0)))
        track.append(Wait(shakeDelay + extraDelay))
        track.append(shakeCameraTrack(shakeIntensity, shakeDuration, numShakes=numShakes))
        track.append(Wait(postShakeDelay))
        return track

    def avatarCloseUpThreeQuarterRightFollowShot(self, avatar, duration):
        track = Sequence(name="avatarCloseUpThreeQuarterRightFollowShot")
        track.append(
            self.heldRelativeShot(
                avatar,
                5.2,
                5.45,
                avatar.getHeight() * 0.66,
                131.5,
                3.6,
                0,
                duration * 0.65,
            )
        )
        track.append(
            LerpHprInterval(
                nodePath=camera,
                other=avatar,
                duration=duration * 0.2,
                hpr=Point3(110, 3.6, 0),
                blendType="easeInOut",
            )
        )
        track.append(Wait(duration * 0.25))
        return track

    @staticmethod
    def avatarCloseUpZoomShot(avatar, duration):
        track = Sequence("avatarCloseUpZoomShot")
        # Let the camera display the toons
        track.append(
            LerpPosHprInterval(
                nodePath=camera,
                other=avatar,
                duration=duration / 2,
                startPos=Point3(0, 10, avatar.getHeight()),
                startHpr=Point3(179, -10, 0),
                pos=Point3(0, 6, avatar.getHeight()),
                hpr=Point3(179, -10, 0),
                blendType="easeInOut",
            )
        )
        track.append(Wait(duration / 2))
        return track

    def allGroupLowShot(self, **kwargs):
        duration = kwargs.get("duration")

        def getWidth(s):
            if s is None or s.getGeomNode() is None:
                return 0
            width = (
                s.getGeomNode().getScale()[0]
                * SuitGlobals.SUIT_BODY_TYPE_WIDTH[SuitDNA.getSuitBodyType(s.dna.name)]
            )
            # Enforce a minimum width.
            return max(width, 4)

        if self.suits:
            # Get the width of each suit in the actor list.
            width = [getWidth(s) for s in self.suits]

            # Calculate the total sum of the suit widths.
            widthSum = sum(width)

            # Get the ratio of the maximum suit width allowed to the
            # width sum.
            widthRatio = max(widthSum / 18, 1)

            # If the ratio wasn't capped, it can be applied to the
            # width sum.
            if widthRatio > 1:
                widthSum -= (10 * widthRatio) - 10
            x = max(min(15 * (widthSum / 20), 20), 15)
            y = -len(self.suits)
            h = 90 - (len(self.suits) * 3)
            p = max([suit.getHeight() + 1 for suit in self.suits]) / 2
        else:
            x = 15
            y = 3
            h = 90
            p = 0
        return self.heldShot(x, y, 3, h, p, 0, duration, "allGroupLowShot")

    def suitGroupThreeQuarterLeftBehindShot(self, **kwargs):
        """Good for toon throws, and some suit magic attacks."""
        duration = kwargs.get("duration")
        if self.suits:
            suitHeight = max([suit.getHeight() + 1 for suit in self.suits])
        else:
            suitHeight = 1

        if MovieUtil.shotDirection == "left":
            x = -12.37
            h = -134.61
        else:
            x = 12.37
            h = 134.61

        return self.heldShot(
            x,
            11.5,
            max(min(suitHeight + 1.5, 15.16), 8.16),
            h,
            -max(min(15 * (suitHeight / 5), 40), 15),
            0,
            duration,
            "suitGroupThreeQuarterLeftBehindShot",
        )

    def avatarCloseUpThreeQuarterLeftShot(self, **kwargs):
        avatar, duration = kwargs.get("avatar"), kwargs.get("duration")
        return self.heldRelativeShot(
            avatar,
            -5.2,
            5.45,
            avatar.getHeight() * 0.66,
            -131.5,
            3.6,
            0,
            duration,
            "avatarCloseUpThreeQuarterLeftShot",
        )

    def avatarBehindShot(self, **kwargs):
        avatar, duration = kwargs.get("avatar"), kwargs.get("duration")
        return self.heldRelativeShot(
            avatar, 5, -7, avatar.getHeight(), 40, -12, 0, duration, "avatarBehindShot"
        )

    def avatarBehindHighShot(self, **kwargs):
        avatar, duration = kwargs.get("avatar"), kwargs.get("duration")
        return self.heldRelativeShot(
            avatar,
            -4,
            -7,
            5 + avatar.getHeight(),
            -30,
            -35,
            0,
            duration,
            "avatarBehindHighShot",
        )

    def avatarBehindHighRightShot(self, **kwargs):
        avatar, duration = kwargs.get("avatar"), kwargs.get("duration")
        return self.heldRelativeShot(
            avatar,
            4,
            -7,
            5 + avatar.getHeight(),
            30,
            -35,
            0,
            duration,
            "avatarBehindHighShot",
        )

    def avatarBehindThreeQuarterRightShot(self, **kwargs):
        avatar, duration = kwargs.get("avatar"), kwargs.get("duration")
        return self.heldRelativeShot(
            avatar,
            7.67,
            -8.52,
            avatar.getHeight() * 0.66,
            25,
            7.5,
            0,
            duration,
            "avatarBehindThreeQuarterRightShot",
        )

    def avatarCloseUpShot(self, **kwargs):
        avatar, duration = kwargs.get("avatar"), kwargs.get("duration")
        return self.heldRelativeShot(
            avatar,
            0,
            8,
            avatar.getHeight() * 0.66,
            179,
            15,
            0,
            duration,
            "avatarCloseUpShot",
        )

    def avatarCloseUpThrowShot(self, **kwargs):
        """Useful for throws and button pushes"""
        avatar, duration = kwargs.get("avatar"), kwargs.get("duration")
        return self.heldRelativeShot(
            avatar,
            3, 8, avatar.getHeight() * 0.66,
            159, 3.6, 0,
            duration, "avatarCloseUpThrowShot",
        )

    def avatarCloseUpThreeQuarterRightShot(self, **kwargs):
        """Throws, button pushes, squirt, and suit attacks
        NOTE: For the course of a battle, toons should have "right" shots,
        and suits should have "left" shots, or vice versa
        """
        avatar, duration = kwargs.get("avatar"), kwargs.get("duration")
        return self.heldRelativeShot(
            avatar,
            5.2,
            5.45,
            avatar.getHeight() * 0.66,
            131.5,
            3.6,
            0,
            duration,
            "avatarCloseUpThreeQuarterRightShot",
        )

    def avatarCloseUpThreeQuarterRightShotWide(self, **kwargs):
        avatar, duration = kwargs.get("avatar"), kwargs.get("duration")
        return self.heldRelativeShot(
            avatar,
            7.2,
            8.45,
            avatar.getHeight() * 0.66,
            131.5,
            3.6,
            0,
            duration,
            "avatarCloseUpThreeQuarterRightShot",
        )

    def avatarCloseUpSquirtShot(self, **kwargs):
        avatar, duration = kwargs.get("avatar"), kwargs.get("duration")
        return self.heldRelativeShot(
            avatar,
            7, 17, avatar.getHeight() * 0.66,
            159, 3.6, 0,
            duration, "avatarCloseUpSquirtShot"
        )

    def avatarCloseUpThreeQuarterLeftSquirtShot(self, **kwargs):
        avatar, duration = kwargs.get("avatar"), kwargs.get("duration")
        return self.heldRelativeShot(
            avatar,
            -8.2, 8.45, avatar.getHeight() * 0.66,
            -131.5, 3.6, 0,
            duration, "avatarCloseUpThreeQuarterLeftShot"
        )

    def avatarCloseUpFireShot(self, **kwargs):
        avatar, duration = kwargs.get("avatar"), kwargs.get("duration")
        return self.heldRelativeShot(
            avatar,
            7, 17, avatar.getHeight() * 0.66,
            159, 3.6, 0,
            duration, "avatarCloseUpFireShot"
        )

    def avatarCloseUpThreeQuarterLeftFireShot(self, **kwargs):
        avatar, duration = kwargs.get("avatar"), kwargs.get("duration")
        return self.heldRelativeShot(
            avatar,
            -8.2, 8.45, avatar.getHeight() * 0.66,
            -131.5, 3.6, 0,
            duration, "avatarCloseUpThreeQuarterLeftShot"
        )

    """
    Various preset held shots
    """

    def allGroupShot(self, **kwargs):
        duration = kwargs.get("duration")
        return self.heldShot(10, 0, 10, 89, -30, 0, duration, "allGroupShot")

    def allGroupOverheadShot(self, **kwargs):
        duration = kwargs.get("duration")
        return self.heldShot(0, -15, 9, 0, -20, 0, duration, "allGroupOverheadShot")

    def allGroupLowerOverheadShot(self, **kwargs):
        duration = kwargs.get("duration")
        return self.heldShot(0, -16.5, 7, 0, -5, 0, duration, "allGroupLowerOverheadShot")

    def allGroupLowDiagonalShot(self, **kwargs):
        duration = kwargs.get("duration")
        return self.heldShot(7, 5, 6, 119, -30, 0, duration, "allGroupLowShot")

    def toonGroupShot(self, **kwargs):
        duration = kwargs.get("duration")
        return self.heldShot(10, 0, 10, 115, -30, 0, duration, "toonGroupShot")

    def toonGroupHighShot(self, **kwargs):
        duration = kwargs.get("duration")
        return self.heldShot(5, 0, 1, 115, 45, 0, duration, "toonGroupHighShot")

    def suitGroupShot(self, **kwargs):
        duration = kwargs.get("duration")
        return self.heldShot(10, 0, 10, 65, -30, 0, duration, "suitGroupShot")

    def suitGroupLowLeftShot(self, **kwargs):
        duration = kwargs.get("duration")
        return self.heldShot(
            8.4, -3.85, 2.75, 36.3, 3.25, 0, duration, "suitGroupLowLeftShot"
        )

    def suitWakeUpShot(self, **kwargs):
        duration = kwargs.get("duration")
        return self.heldShot(10, -5, 10, 65, -30, 0, duration, "suitWakeUpShot")

    """
    Implementation of camera "packages", which are simply a series of held and
    motion shots capturing the action of an attack
    """

    def avatarSideFollowAttack(self, suit, toon, duration, battle):
        # Three part timing on an attack: the windup, the projection, the impact
        # Use slightly random range for windupDuration, between 0-20% of total duration
        windupDuration = duration * (0.1 + random.random() * 0.1)
        projectDuration = duration * 0.75
        impactDuration = duration - windupDuration - projectDuration

        suitHeight = suit.getHeight()
        toonHeight = toon.getHeight()

        # Helper methods to get focal points of the actors for the camera
        def getSuitCentralPoint():
            suitCentralPoint = suit.getPos(battle)
            suitCentralPoint.setZ(suitCentralPoint.getZ() + suitHeight * 0.75)
            return suitCentralPoint

        def getToonCentralPoint():
            toonCentralPoint = toon.getPos(battle)
            toonCentralPoint.setZ(toonCentralPoint.getZ() + toonHeight * 0.75)
            return toonCentralPoint

        # Vary the x-coordinates of the camera
        initialX = random.randint(12, 14)
        finalX = random.randint(7, 8)
        # Vary the y-coordinates of the camera
        initialY = finalY = random.randint(-3, 0)
        # Vary the z-coordinates of the camera
        initialZ = suitHeight * 0.5 + random.random() * suitHeight
        finalZ = toonHeight * 0.5 + random.random() * toonHeight
        # Keep shot direction consistent
        if MovieUtil.shotDirection == "left":
            initialX = -initialX
            finalX = -finalX

        return Sequence(
            self.focusShot(
                Point3(initialX, initialY, initialZ),
                windupDuration,
                getSuitCentralPoint,
            ),
            self.focusMoveShot(
                Point3(finalX, finalY, finalZ), projectDuration, getToonCentralPoint
            ),
            Wait(impactDuration),
        )

    @staticmethod
    def focusCameraBetweenPoints(point1, point2):
        """focusCameraBetweenPoints() finds a bisection point between the arg points provided
        and focuses the camera on this central point"""
        if callable(point1):
            point1 = point1()
        if callable(point2):
            point2 = point2()
        if point1[0] > point2[0]:
            x = point2[0] + (point1[0] - point2[0]) * 0.5
        else:
            x = point1[0] + (point2[0] - point1[0]) * 0.5
        if point1[1] > point2[1]:
            y = point2[1] + (point1[1] - point2[1]) * 0.5
        else:
            y = point1[1] + (point2[1] - point1[1]) * 0.5
        if point1[2] > point2[2]:
            z = point2[2] + (point1[2] - point2[2]) * 0.5
        else:
            z = point1[2] + (point2[2] - point1[2]) * 0.5
        camera.lookAt(Point3(x, y, z))

    def randomCamera(self, suit, toon, battle, attackDuration, openShotDuration):
        """randomCamera() places the camera in random, though effective, position to capture
        the action of an attack, first shooting the attacker and then the defender"""
        return self.randomAttackCam(
            suit, toon, battle, attackDuration, openShotDuration, "suit"
        )

    def randomAttackCam(self, suit, toon, battle, attackDuration, openShotDuration, attackerString="suit"):
        """randomCamSuitAttack() places the camera in a random, though effective position to
        shoot the action of an attacker, if you don't specify the attacker as
        either 'avatar' or 'suit', it defaults to suit"""
        if openShotDuration > attackDuration:  # Ensure that it's not too long
            openShotDuration = attackDuration
        closeShotDuration = attackDuration - openShotDuration

        if attackerString == "suit":
            attacker = suit
            defender = toon
            defenderString = "avatar"
        else:
            attacker = toon
            defender = suit
            defenderString = "suit"
        randomDouble = random.random()
        if randomDouble > 0.6:  # 40% chance
            openShot = self.randomActorShot(
                attacker, battle, openShotDuration, attackerString
            )
        elif randomDouble > 0.2:  # 40% chance
            openShot = self.randomOverShoulderShot(
                suit, toon, battle, openShotDuration, focus=attackerString
            )
        else:
            openShot = self.randomSplitShot(
                attacker, defender, battle, openShotDuration
            )
        randomDouble = random.random()
        if randomDouble > 0.6:  # 40% chance
            closeShot = self.randomActorShot(
                defender, battle, closeShotDuration, defenderString
            )
        elif randomDouble > 0.2:  # 40% chance
            closeShot = self.randomOverShoulderShot(
                suit, toon, battle, closeShotDuration, focus=defenderString
            )
        else:
            closeShot = self.randomSplitShot(
                attacker, defender, battle, closeShotDuration
            )
        return Sequence(openShot, closeShot)

    def randomGroupAttackCam(self, suit, targets, battle, attackDuration, openShotDuration):
        """randomGroupAttackCam() places the camera in a random, though effective position to
        shoot the action of a suit attacking a group of toons (targets)"""
        if openShotDuration > attackDuration:  # Ensure that it's not too long
            openShotDuration = attackDuration
        closeShotDuration = attackDuration - openShotDuration

        # First we shoot the attacking suit
        openShot = self.randomActorShot(
            suit, battle, openShotDuration, "suit", groupShot=0
        )
        closeShot = self.randomToonGroupShot(targets, suit, closeShotDuration, battle)
        return Sequence(openShot, closeShot)

    def randomActorShot(self, actor, battle, duration, actorType, groupShot=0, notRandom=False):
        """randomActorShot() creates a random though effective shot for an actor in
        a battle, specified by arg actor of type actorType ('suit' or 'avatar').  This
        function defaults to single shots of the primary actor, but a groupShot will
        pull the camera out some more."""
        height = actor.getHeight()

        def getCentralPoint():
            centralPoint = actor.getPos(battle)
            centralPoint.setZ(centralPoint.getZ() + height * 0.75)
            return centralPoint

        def getRandom():
            return random.random() if not notRandom else 0.5

        if actorType == "suit":
            x = 4 + getRandom() * 8
            y = -2 - getRandom() * 4
            z = height * 0.5 + getRandom() * height * 1.5
            if groupShot == 1:
                y = -4
                z = height * 0.5
        else:
            x = 2 + getRandom() * 8
            y = -2 + getRandom() * 3
            z = height + getRandom() * height * 1.5
            if groupShot == 1:
                y = y + 3
                z = height * 0.5
        if MovieUtil.shotDirection == "left" or notRandom:
            x = -x

        return self.focusShot(Point3(x, y, z), duration, getCentralPoint)

    def randomSplitShot(self, suit, toon, battle, duration):
        """randomSplitShot() places the camera in random, though effective, position to capture
        both primary actors in an attack"""
        suitHeight = suit.getHeight()
        toonHeight = toon.getHeight()

        def getSuitCentralPoint():
            suitCentralPoint = suit.getPos(battle)
            suitCentralPoint.setZ(suitCentralPoint.getZ() + suitHeight * 0.75)
            return suitCentralPoint

        def getToonCentralPoint():
            toonCentralPoint = toon.getPos(battle)
            toonCentralPoint.setZ(toonCentralPoint.getZ() + toonHeight * 0.75)
            return toonCentralPoint

        x = 9 + self.randomRange(1, 2)
        y = -2 - self.randomRange(1, 2)
        z = suitHeight * 0.5 + self.randomRange(0.5, 1) * suitHeight
        if MovieUtil.shotDirection == "left":
            x = -x

        return self.focusShot(
            Point3(x, y, z),
            duration,
            getToonCentralPoint,
            splitFocusPoint=getSuitCentralPoint,
        )

    def randomOverShoulderShot(self, suit, toon, battle, duration, focus):
        # the future is now
        # return betterGroupHeldShot(suit, duration)
        """randomOverShouldShot() creates a random, though effective, camera shot for a battle
        shooting the actor specified in arg focus ('avatar' or 'suit') over the shoulder of
        the other actor in the attack"""
        suitHeight = suit.getHeight()
        toonHeight = toon.getHeight()

        def getSuitCentralPoint():
            suitCentralPoint = suit.getPos(battle)
            suitCentralPoint.setZ(suitCentralPoint.getZ() + suitHeight * 0.75)
            return suitCentralPoint

        def getToonCentralPoint():
            toonCentralPoint = toon.getPos(battle)
            toonCentralPoint.setZ(toonCentralPoint.getZ() + toonHeight * 0.75)
            return toonCentralPoint

        x = 2 + random.random() * 10
        if focus == "avatar":
            y = 8 + random.random() * 6
            z = suitHeight * 1.2 + random.random() * suitHeight
        else:
            y = -10 - random.random() * 6
            z = toonHeight * 1.5
        if MovieUtil.shotDirection == "left":
            x = -x

        return self.focusShot(
            Point3(x, y, z),
            duration,
            getToonCentralPoint,
            splitFocusPoint=getSuitCentralPoint,
        )

    def randomToonGroupShot(self, toons, suit, duration, battle):
        """randomToonGroupShot() creates a random, though effective camera shot for a group
        of toons (2, 3, or 4) in a battle"""
        # If no toons are available, just return a random actor shot using the suit
        if len(toons) == 0:
            return self.randomActorShot(suit, battle, duration, "suit", groupShot=0)

        # Grab the average height of these toons for the best shot
        sum = 0
        for t in toons:
            toon = t["avatar"]
            height = toon.getHeight()
            sum = sum + height

        avgHeight = (
            sum / len(toons) * 0.75
        )  # Multiply by 0.75 to get the chest of the toon

        # We shoot from the opposite side of the attacking suit
        suitPos = suit.getPos(battle)
        x = 1 + random.random() * 6
        if suitPos.getX() > 0:
            x = -x

        # We'll either shoot a close up or far back over the shoulders of the suits
        if random.random() > 0.5:  # 50% chance
            y = 4 + random.random() * 1
            z = avgHeight + random.random() * 6
        else:
            y = 11 + random.random() * 2
            z = 13 + random.random() * 2
        focalPoint = Point3(0, -4, avgHeight)
        return self.focusShot(Point3(x, y, z), duration, focalPoint)

    """
    Camera manipulations for gag tracks
    """

    ### Toon-Up ###

    def chooseHealShot(self, heals, attackDuration):
        isUber = 0
        for heal in heals:
            if heal["level"] == BattleGlobals.LAST_REGULAR_GAG_LEVEL:
                isUber = 1

        # Compose the track
        if isUber:
            # Pick an open shot
            openShot = self.chooseHealOpenShot(isUber)
            openDuration = openShot.getDuration()
            # If the high dive is involved we want the gag to control camera and we
            # cut straight to the closing shot.
            # since we only do close shot now, attackDuration *should* be okay to use
            # (we add openDuration to un-offset the duration calculation of the close shot,
            # which is attackDuration - openDuration)
            self.notify.debug(
                f"chooseHealShot(): openDuration={openDuration}, attackDuration={attackDuration}, "
                f"openDuration+attackDuration={openDuration + attackDuration}"
            )
            # Pick a close shot
            closeShot = self.chooseHealCloseShot(
                openDuration, attackDuration + openDuration, isUber
            )
            track = Sequence(closeShot)
        else:
            # Pick an open shot
            openShot = self.chooseHealOpenShot(isUber)
            openDuration = openShot.getDuration()
            # Pick a close shot
            closeShot = self.chooseHealCloseShot(
                openDuration, attackDuration, isUber
            )
            track = Sequence(openShot, closeShot)
        # Return it
        return track

    def chooseHealOpenShot(self, isUber=0):
        # General purpose shots
        # Pick a shot and return it
        # This used to include allGroupLowShot, but was removed cause it was a "bad choice"
        return self.toonGroupShot(duration=5.0 if isUber else 2.8)

    def chooseHealCloseShot(self, openDuration, attackDuration, isUber=0):
        # Setup
        duration = attackDuration - openDuration
        # Pick a shot and return it
        if isUber:
            # This used to include allGroupLowDiagonalShot, but was removed cause it was a "bad choice"
            return self.allGroupLowShot(duration=duration)
        return self.toonGroupShot(duration=duration)

    ### Trap (and Lure) ###

    def chooseTrapShot(self, attackDuration):
        # Pick an open shot
        openShot = self.chooseTrapOpenShot()
        openDuration = openShot.getDuration()
        # Pick a close shot
        closeShot = self.chooseTrapCloseShot(openDuration, attackDuration)
        # Compose the track
        track = Sequence(openShot, closeShot)
        # Return it
        return track

    def chooseTrapOpenShot(self):
        # Pick a shot and return it
        return self.allGroupLowShot(duration=3.0)

    def chooseTrapCloseShot(self, openDuration, attackDuration):
        # Pick a shot and return it
        return self.allGroupLowShot(duration=attackDuration - openDuration)

    ### Zap ###

    def chooseZapShot(self, attackDuration):
        # Pick an open shot
        openShot = self.chooseZapOpenShot()
        openDuration = openShot.getDuration()
        # Pick a close shot
        closeShot = self.chooseZapCloseShot(openDuration, attackDuration)
        # Compose the track
        track = Sequence(openShot, closeShot)
        # Return it
        return track

    def chooseZapOpenShot(self):
        # Choose the predefined overhead shot and return it
        return self.allGroupOverheadShot(duration=3.0)

    def chooseZapCloseShot(self, openDuration, attackDuration):
        # Choose the predefined overhead shot and return it
        return self.allGroupOverheadShot(duration=attackDuration - openDuration)

    ### Throw/Sues ###

    def chooseThrowShot(self, throws, suitThrowsDict, attackDuration):
        # Pick an open shot
        openShot = self.chooseThrowOpenShot(throws)
        openDuration = openShot.getDuration()
        # Pick a close shot
        closeShot = self.chooseThrowCloseShot(
            suitThrowsDict, openDuration, attackDuration
        )
        # Compose the track
        track = Sequence(openShot, closeShot)
        # Return it
        return track

    def chooseThrowOpenShot(self, throws):
        # Setup
        numThrows = len(throws)
        av = None
        duration = 2.8
        # The single Toon case
        if numThrows == 1:
            # The attacking Toon
            av = throws[0]["avatar"]
            # Single Toon choices
            shotChoices = [
                self.avatarCloseUpThrowShot,
                self.avatarCloseUpThreeQuarterRightShot,
                self.avatarBehindShot,
                self.allGroupLowShot,
                self.suitGroupThreeQuarterLeftBehindShot,
            ]
        # The multi-toon case
        elif numThrows >= 2 and numThrows <= 4:
            # Multi-suit choices
            shotChoices = [
                self.allGroupLowShot,
                self.suitGroupThreeQuarterLeftBehindShot,
            ]
        else:
            self.notify.error("Bad number of throws: %s" % numThrows)
        # Pick a shot and return it
        track = random.choice(shotChoices)(avatar=av, duration=duration)
        return track

    def chooseThrowCloseShot(self, suitThrowsDict, openDuration, attackDuration):
        # Setup
        numSuits = len(suitThrowsDict)
        av = None
        duration = attackDuration - openDuration
        # The single suit case
        if numSuits == 1:
            # The attacked Suit
            av = base.cr.doId2do[list(suitThrowsDict.keys())[0]]
            # Single Suit choices
            shotChoices = [
                self.avatarCloseUpThrowShot,
                self.avatarCloseUpThreeQuarterLeftShot,
                self.allGroupLowShot,
                self.suitGroupThreeQuarterLeftBehindShot,
            ]
        # The multi suit case (numSuits == 0 is for group throw (SOS/Uber gag))
        elif (
            numSuits >= 2
            and numSuits <= BattleGlobals.MaxBattleAvatars
            or numSuits == 0
        ):
            # Multi-suit choices
            shotChoices = [
                self.allGroupLowShot,
                self.suitGroupThreeQuarterLeftBehindShot,
            ]
        else:
            self.notify.error("Bad number of suits: %s" % numSuits)
        # Pick a shot and return it
        track = random.choice(shotChoices)(avatar=av, duration=duration)
        return track

    ### Squirt ###

    def chooseSquirtShot(self, squirts, suitSquirtsDict, attackDuration):
        # Pick an open shot
        openShot = self.chooseSquirtOpenShot(squirts)
        openDuration = openShot.getDuration()
        # Pick a close shot
        closeShot = self.chooseSquirtCloseShot(suitSquirtsDict, openDuration, attackDuration)
        # Compose the track
        track = Sequence(openShot, closeShot)
        # Return it
        return track

    def chooseSquirtOpenShot(self, squirts):
        # Setup
        numSquirts = len(squirts)
        av = None
        level = squirts[0]['level']
        if level == 1:
            duration = 3.6
        elif level == 2:
            duration = 1.8
        elif level == 3:
            duration = 2.8
        elif level == 4:
            duration = 2.4
        elif level == 5:
            duration = 2.1
        else:
            duration = 2.6
        # The single toon case
        if numSquirts == 1:
            # The attacking Toon
            av = squirts[0]['avatar']
            # Single toon choices
            shotChoices = [
                self.avatarCloseUpSquirtShot,
                self.avatarCloseUpThreeQuarterRightShot,
                self.avatarBehindShot,
                self.allGroupLowShot,
                self.suitGroupThreeQuarterLeftBehindShot,
            ]
        # The multi toon case
        elif numSquirts >= 2 and numSquirts <= 4:
            # Multi suit choices
            shotChoices = [
                self.allGroupLowShot,
                self.suitGroupThreeQuarterLeftBehindShot,
            ]
        else:
            self.notify.error("Bad number of squirts: %s" % numSquirts)
        # Pick a shot and return it
        track = random.choice(shotChoices)(avatar=av, duration=duration)
        return track

    def chooseSquirtCloseShot(self, suitSquirtsDict, openDuration, attackDuration):
        # Setup
        numSuits = len(suitSquirtsDict)
        av = None
        duration = attackDuration - openDuration
        # The single suit case
        if numSuits == 1:
            # The attacked suit
            av = base.cr.doId2do[list(suitSquirtsDict.keys())[0]]
            # Single suit choices
            shotChoices = [
                self.avatarCloseUpSquirtShot,
                self.avatarCloseUpThreeQuarterLeftSquirtShot,
                self.allGroupLowShot,
                self.suitGroupThreeQuarterLeftBehindShot,
            ]
        # The multi suit case
        elif (numSuits >= 2 and numSuits <= 4) or (numSuits == 0):
            # Multi suit choices
            shotChoices = [
                self.allGroupLowShot,
                self.suitGroupThreeQuarterLeftBehindShot,
            ]
        else:
            self.notify.error("Bad number of suits: %s" % numSuits)
        # Pick a shot and return it
        track = random.choice(shotChoices)(avatar=av, duration=duration)
        return track

    ### Sound ###

    def chooseSoundShot(self, sounds, targets, attackDuration):
        # Pick an open shot
        openShot = self.chooseSoundOpenShot(sounds)
        openDuration = openShot.getDuration()
        # Pick a close shot
        closeShot = self.chooseSoundCloseShot(targets, openDuration, attackDuration)
        # Compose the track
        track = Sequence(openShot, closeShot)
        # Return it
        return track

    def chooseSoundOpenShot(self, sounds):
        # Setup
        duration = 2.1
        for sound in sounds:
            if sound["level"] == BattleGlobals.LAST_REGULAR_GAG_LEVEL:
                duration = 3.4

        numSounds = len(sounds)
        av = None
        # The single Toon case
        if numSounds == 1:
            # The attacking Toon
            av = sounds[0]["avatar"]
            # Single Toon choices
            shotChoices = [
                self.avatarCloseUpThreeQuarterRightShot,
                self.allGroupLowShot,
                self.suitGroupThreeQuarterLeftBehindShot,
            ]
        # The multi-toon case
        elif numSounds >= 2 and numSounds <= 4:
            # Multi-suit choices
            shotChoices = [
                self.allGroupLowShot,
                self.suitGroupThreeQuarterLeftBehindShot,
            ]
        else:
            self.notify.error("Bad number of sounds: %s" % numSounds)
        # Pick a shot and return it
        track = random.choice(shotChoices)(avatar=av, duration=duration)
        return track

    def chooseSoundCloseShot(self, targets, openDuration, attackDuration):
        # Setup
        numSuits = len(targets)
        av = None
        duration = attackDuration - openDuration
        # The single Toon case
        if numSuits == 1:
            # The attacked Suit
            av = targets[0]["suit"]
            # Single suit choices
            shotChoices = [
                self.avatarCloseUpThrowShot,
                self.avatarCloseUpThreeQuarterLeftShot,
                self.allGroupLowShot,
                self.suitGroupThreeQuarterLeftBehindShot,
            ]
        # The multi-suit case
        elif (
            numSuits >= 2
            and numSuits <= BattleGlobals.MaxBattleAvatars
            or numSuits == 0
        ):
            # Multi-suit choices
            shotChoices = [
                self.allGroupLowShot,
                self.suitGroupThreeQuarterLeftBehindShot,
            ]
        else:
            self.notify.error("Bad number of suits: %s" % numSuits)
        # Pick a shot and return it
        track = random.choice(shotChoices)(avatar=av, duration=duration)
        return track

    ### Drop ###

    def chooseDropShot(self, drops, suitDropsDict, attackDuration):
        # Pick an open shot
        openShot = self.chooseDropOpenShot(drops)
        openDuration = openShot.getDuration()
        # Pick a close shot
        closeShot = self.chooseDropCloseShot(
            drops, suitDropsDict, openDuration, attackDuration
        )
        # Compose the track
        track = Sequence(openShot, closeShot)
        # Return it
        return track

    def chooseDropOpenShot(self, drops):
        # Setup
        numDrops = len(drops)
        av = None
        duration = 3.0
        # Gag level
        highestLevel = max([drop["level"] for drop in drops])
        # The single Toon case
        if numDrops == 1:
            # The attacking Toon
            av = drops[0]["avatar"]
            # Single Toon choices
            if highestLevel < 4:
                shotChoices = [
                    self.avatarCloseUpThrowShot,
                    self.avatarCloseUpThreeQuarterRightShot,
                    self.avatarBehindShot,
                    self.allGroupLowShot,
                    self.suitGroupThreeQuarterLeftBehindShot,
                ]
            else:
                shotChoices = [self.allGroupOverheadShot]
        # The multi-toon case
        elif 2 <= numDrops <= BattleGlobals.MaxBattleAvatars or numDrops == 0:
            # Multi-toon choices
            if highestLevel < 4:
                shotChoices = [
                    self.allGroupLowShot,
                    self.suitGroupThreeQuarterLeftBehindShot,
                ]
            else:
                shotChoices = [self.allGroupOverheadShot]
        else:
            self.notify.error("Bad number of drops: %s" % numDrops)
        # Pick a shot and return it
        track = random.choice(shotChoices)(avatar=av, duration=duration)
        return track

    def chooseDropCloseShot(self, drops, suitDropsDict, openDuration, attackDuration):
        # Setup
        numSuits = len(suitDropsDict)
        av = None
        highestLevel = max([drop["level"] for drop in drops])
        duration = attackDuration - openDuration
        # The single Toon case
        if numSuits == 1:
            # The attacked Suit
            av = base.cr.doId2do[list(suitDropsDict.keys())[0]]
            if highestLevel < 4:
                shotChoices = [
                    self.avatarCloseUpThrowShot,
                    self.avatarCloseUpThreeQuarterLeftShot,
                    self.allGroupLowShot,
                    self.suitGroupThreeQuarterLeftBehindShot,
                ]
            else:
                shotChoices = [self.allGroupOverheadShot]
        # The multi-suit case
        elif 2 <= numSuits <= BattleGlobals.MaxBattleAvatars or numSuits == 0:
            # Multi-suit choices
            if highestLevel < 4:
                shotChoices = [
                    self.allGroupLowShot,
                    self.suitGroupThreeQuarterLeftBehindShot,
                ]
            else:
                shotChoices = [self.allGroupOverheadShot]
        else:
            self.notify.error("Bad number of suits: %s" % numSuits)
        # Pick a shot and return it
        track = random.choice(shotChoices)(avatar=av, duration=duration)
        return track

    ### Fire ###

    def chooseFireShot(self, fires, suitFiresDict, attackDuration):
        # Pick an open shot
        openShot = self.chooseFireOpenShot(fires)
        openDuration = openShot.getDuration()
        # Pick a close shot
        closeShot = self.chooseFireCloseShot(suitFiresDict, openDuration, attackDuration)
        # Compose the track
        track = Sequence(openShot, closeShot)
        # Return it
        return track

    def chooseFireOpenShot(self, fires):
        # Setup
        numFires = len(fires)
        av = None
        duration = 3.0
        # The single toon case
        if numFires == 1:
            # The attacking Toon
            av = fires[0]['avatar']
            # Single toon choices
            shotChoices = [
                self.avatarCloseUpFireShot,
                self.avatarCloseUpThreeQuarterRightShot,
                self.avatarBehindShot,
                self.allGroupLowShot,
                self.suitGroupThreeQuarterLeftBehindShot,
            ]
        # The multi toon case
        elif numFires >= 2 and numFires <= 4:
            # Multi suit choices
            shotChoices = [
                self.allGroupLowShot,
                self.suitGroupThreeQuarterLeftBehindShot,
            ]
        else:
            self.notify.error("Bad number of fires: %s" % numFires)
        # Pick a shot and return it
        track = random.choice(shotChoices)(avatar=av, duration=duration)
        return track

    def chooseFireCloseShot(self, suitFiresDict, openDuration, attackDuration):
        # Setup
        numSuits = len(suitFiresDict)
        av = None
        duration = attackDuration - openDuration
        # The single suit case
        if numSuits == 1:
            # The attacked suit
            av = base.cr.doId2do[list(suitFiresDict.keys())[0]]
            # Single suit choices
            shotChoices = [
                self.avatarCloseUpFireShot,
                self.avatarCloseUpThreeQuarterLeftFireShot,
                self.allGroupLowShot,
                self.suitGroupThreeQuarterLeftBehindShot,
            ]
        # The multi suit case
        elif (numSuits >= 2 and numSuits <= 4) or (numSuits == 0):
            # Multi suit choices
            shotChoices = [
                self.allGroupLowShot,
                self.suitGroupThreeQuarterLeftBehindShot,
            ]
        else:
            self.notify.error("Bad number of suits: %s" % numSuits)
        # Pick a shot and return it
        track = random.choice(shotChoices)(avatar=av, duration=duration)
        return track

    """
    Camera shot used for the reward sequence
    """

    @staticmethod
    def chooseRewardShot(av, duration, allowGroupShot=1):
        # We actually return an interval that chooses the reward shot
        # on-the-fly, rather than prechoosing it.  This is because the
        # avatar in question may wander away during the reward movie.

        def chooseRewardShotNow(av):
            if av.playingAnim == "victory" or not allowGroupShot:
                # The avatar is still dancing; choose an avatar shot.
                shotChoices = [
                    (0, 8, av.getHeight() * 0.66, 179, 15, 0),
                    (5.2, 5.45, av.getHeight() * 0.66, 131.5, 3.6, 0),
                ]
                shot = random.choice(shotChoices)
                camera.setPosHpr(av, *shot)
            else:
                # The avatar has stopped dancing; give a group shot.
                camera.setPosHpr(10, 0, 10, 115, -30, 0)

        return Sequence(Func(chooseRewardShotNow, av), Wait(duration))

    @staticmethod
    def randomRange(a: float, b: float):
        return a + (random.random() * b)
