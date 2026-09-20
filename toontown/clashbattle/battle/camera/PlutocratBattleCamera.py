from toontown.clashbattle.battle.BattleCamera import BattleCamera
from toontown.clashsuit.suit import SuitDNA, SuitGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class PlutocratBattleCamera(BattleCamera):
    """
    A battle camera class that alters allGroupLowShot to raise it above the fence in the arena
    """

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
            widthRatio = max(widthSum / 13, 1)

            # If the ratio wasn't capped, it can be applied to the
            # width sum.
            if widthRatio > 1:
                widthSum -= (7.5 * widthRatio) - 7.5
            x = max(min(12 * (widthSum / 15), 15), 12)
            y = -len(self.suits)
            h = 90 - (len(self.suits) * 2)
            p = max([suit.getHeight() + 1 for suit in self.suits]) / 2
        else:
            x = 15
            y = 3
            h = 90
            p = 0
        return self.heldShot(x, y, 3, h, p, 0, duration, "allGroupLowShot")
