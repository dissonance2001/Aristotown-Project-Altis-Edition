from toontown.clashbattle.battle.BattleCamera import BattleCamera
from toontown.clashsuit.suit import SuitDNA, SuitGlobals
from toontown.clashbattle.battle.statuses.StatusEffectEnums import SEE
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class MultislackerBattleCamera(BattleCamera):
    """
    A battle camera class that alters allGroupLowShot, flipping the angle to the other side
    to avoid the camera looking at Multislacker's fat dumpy while he's on break
    """

    def isMultislackerOnBreak(self) -> bool:
        bossSuits = [suit for suit in self.battle.activeSuits if suit.dna.name == 'mslacker']
        if not bossSuits:
            return False
        multislacker = bossSuits[0]
        return multislacker.hasStatusEffectOfId(SEE.EFFECT_LUNCH_BREAK_MSLACKER)

    def allGroupLowShot(self, **kwargs):
        if not self.isMultislackerOnBreak():
            return super().allGroupLowShot(**kwargs)

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
            x = -max(min(15 * (widthSum / 20), 20), 15)
            y = -len(self.suits)
            h = -(90 - (len(self.suits) * 3))
            p = max([suit.getHeight() + 1 for suit in self.suits]) / 2
        else:
            x = 15
            y = 3
            h = 90
            p = 0
        return self.heldShot(x, y, 3, h, p, 0, duration, "allGroupLowShot")
