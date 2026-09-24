from direct.gui.DirectGui import *
from panda3d.core import *
from direct.interval.IntervalGlobal import *
from direct.interval.LerpInterval import LerpPosInterval

from toontown.clashsuit.suit import BossCogGlobals
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import ToontownIntervals
import random

# Bar Colors
# lime = (201/255, 255/255, 150/255, 1)
# yellow = (255/255, 241/255, 18/255, 1)
# purple = (240/255, 0/255, 255/255, 1)
from toontown.toonbase.MarginManagerCell import ScreenCellFlag

red = (255 / 255, 48 / 255, 0 / 255, 1)

# Value that the directWaitBar uses (minRange-maxRange)
# Don't reduce below 10% of maxRange or waitbar will have an aneurysm. This is due to directwaitbars being weird
# about vertical placement based on value. If the is small enough.
# The waitbar will move upwards.  To avoid this issue the bar is hidden a bit and requires 10% fill
# before becoming visible.
minRange = 25
maxRange = 100  # Don't set 0 or bad division
# 10%, Value that waitbar's value has to be before it is visible in the gui. # Used for calculating vertical alignment.
minVisible = maxRange / 10

# How much a gag icon must shift vertically for each value.  This is value and not evidence amount.
valueVerticalShift = .009  # Recalc if gui size is changed

# The gag icons reference point pos (bottom of the bar).  Where the fill actually becomes visible
verticalStart = -.334  # Recalc if gui size is changed, based on where the bar is at minRange

# Scale for the evidence label GUI element.
evidenceLabelScale = 0.145


class EvidenceGUI(DirectFrame):
    """
    EvidenceGUI(DirectFrame)

    This is the GUI bar used in the evidence round of the CLO to give a visual representation of what gag
    a player will have in the final round based on evidence earned.
    """

    def __init__(self, hardmode = False):
        """
        :type hardmode: bool
        """
        DirectFrame.__init__(self, relief = None, sortOrder = 50)
        self.av = None
        self.evidenceTotal = 0
        self.track = None
        # Determine which requirements to use based on if this is hardmode or not
        if hardmode:
            evidenceRequirements = BossCogGlobals.HardmodeLawbotBossSoundEvidenceRequirement
        else:
            evidenceRequirements = BossCogGlobals.LawbotBossSoundEvidenceRequirement

        # Value for a gag.  This is how much evidence is required to get the gag for the final round.
        self.bugleAmount = evidenceRequirements['bugle']
        self.aoogahAmount = evidenceRequirements['aoogah']
        self.trunkAmount = evidenceRequirements['trunk']
        self.fogAmount = evidenceRequirements['fog']
        self.maxEvidence = evidenceRequirements['max']  # Don't set 0 or bad division

        self.isLoaded = 0
        self.load()

    def load(self):
        # Bar
        gui = loader.loadModel('phase_11/models/gui/clo_evidence_gui')
        bgImage = gui.find("**/base")
        # -.25,0,.7 is the correct pos, but bar is placed here to allow for animation of coming from off screen
        self.barBG = DirectFrame(parent = self,
                                 relief = None,
                                 image = bgImage,
                                 pos = (1.0, 0.0, .70))
        bottomImage = gui.find('**/bottom')
        self.bottom = DirectFrame(parent = self.barBG,
                                  relief = None,
                                  image = bottomImage,
                                  scale = .3,
                                  pos = (0.013, 0.0, -0.41),
                                  sortOrder = 2)

        # Fill
        fillTexture = loader.loadTexture('phase_11/maps/clo_evidence_gui_filler.png')
        self.fill = DirectWaitBar(parent = self.barBG,
                                  relief = None,
                                  barTexture = fillTexture,
                                  barColor = red,
                                  sortOrder = 1,
                                  hpr = (0.0, 0.0, -90.0),
                                  pos = (0.0165, 0.0, 0.068),
                                  scale = (1, 0, 1),
                                  value = minRange,
                                  frameSize = (-0.495, 0.495, -0.53, 0.53))
        self.fill.setTransparency(1)

        evidenceIcon = loader.loadTexture('phase_11/maps/paper_rain.png')
        self.evidenceLabel = DirectFrame(parent = self,
                                         relief = None,
                                         scale = evidenceLabelScale,
                                         pos = (-0.5, 0.0, 0.3),
                                         image = evidenceIcon,
                                         image_pos = (0.0, 0.0, 0.575),
                                         text = TTLocalizer.LawbotBossEvidenceCollected % 0,
                                         text_font = ToontownGlobals.getInterfaceFont(),
                                         text_fg = (1, 1, 1, 1),
                                         text_shadow = (0, 0, 0, 1),
                                         text_pos = (0.0, 0.0, -0.2),
                                         text_scale = 0.8,
                                         textMayChange = 1,
                                         sortOrder = 2)
        self.evidenceLabel.setTransparency(1)

        # GagIcons
        bugleTexture = gui.find('**/bugle')
        aoogahTexture = gui.find('**/aoogah')
        trunkTexture = gui.find('**/trunk')
        fogHornTexture = gui.find('**/foghorn')
        self.bugle = DirectFrame(parent = self.barBG,
                                 relief = None,
                                 image = bugleTexture,
                                 scale = (0.4, 0, 0.4),
                                 pos = (0.111, 0, self.calculateGagIconZ(0)),
                                 sortOrder = 2)
        self.bugle.setColorScale((0.4, 0.4, 0.4, 1))
        self.aoogah = DirectFrame(parent = self.barBG,
                                  relief = None,
                                  image = aoogahTexture,
                                  scale = (0.4, 0, 0.4),
                                  pos = (-0.08, 0.0, self.calculateGagIconZ(1)),
                                  sortOrder = 2,
                                  hpr = (180, 0, 0))
        self.aoogah.setColorScale((0.4, 0.4, 0.4, 1))
        self.trunk = DirectFrame(parent = self.barBG,
                                 relief = None,
                                 image = trunkTexture,
                                 scale = (0.4, 0.0, 0.4),
                                 pos = (0.111, 0, self.calculateGagIconZ(2)),
                                 sortOrder = 2)
        self.trunk.setColorScale((0.4, 0.4, 0.4, 1))
        self.fogHorn = DirectFrame(parent = self.barBG,
                                   relief = None,
                                   image = fogHornTexture,
                                   scale = (0.4, 0.0, 0.4),
                                   pos = (-0.08, 0.0, self.calculateGagIconZ(3)),
                                   sortOrder = 2,
                                   hpr = (180, 0.0, 0.0))
        self.fogHorn.setColorScale((0.4, 0.4, 0.4, 1))
        self.updateHighlight()
        self.enterRight()
        gui.removeNode()
        del gui
        del fillTexture
        del evidenceIcon
        self.isLoaded = 1
        # Do not allow chat to show on the right side of the screen while it is occupied by us.
        base.flagScreenCells(ScreenCellFlag.cloEvidenceMeter, base.rightCells)

    def destroy(self):
        if self.track:
            if self.track.isPlaying():
                self.track.finish()
            del self.track
        DirectFrame.destroy(self)
        self.isLoaded = 0
        # Re-allow chat to show on the right side of the screen.
        base.unflagScreenCells(ScreenCellFlag.cloEvidenceMeter, base.rightCells)

    def updateHighlight(self):
        """
        Checks to see if the value of fill matches the location of the gag icon
        """
        if self.evidenceTotal >= self.bugleAmount:
            self.bugle.clearColorScale()
        if self.evidenceTotal >= self.aoogahAmount:
            self.aoogah.clearColorScale()
        if self.evidenceTotal >= self.trunkAmount:
            self.trunk.clearColorScale()
        if self.evidenceTotal >= self.fogAmount:
            self.fogHorn.clearColorScale()

    def updateEvidence(self, avId, evidence):
        """
        Called every time a toon hits a cog
        """
        if avId == base.localAvatar.doId:
            oldEvidenceTotal = self.evidenceTotal
            self.evidenceTotal += evidence

            # Can't update the bar if it doesn't exist!
            if not self.isLoaded:
                return
            oldValue = self.fill['value']
            newValue = (self.evidenceTotal * ((maxRange - minRange) / self.maxEvidence)) + minRange
            self.updateHighlight()

            def bounceEvidenceLabel():
                name = 'evidenceLabelBoing'
                ToontownIntervals.start(
                    ToontownIntervals.getPulseLargerIval(self.evidenceLabel, name, scale = evidenceLabelScale)
                )

            if self.track:
                if self.track.isPlaying():
                    self.track.pause()
                del self.track

            self.track = Parallel(
                LerpFunctionInterval(
                    self.__lerpValue,
                    fromData = oldValue,
                    toData = newValue,
                    duration = 0.5,
                    blendType = 'easeOut'
                ),
                LerpFunctionInterval(
                    self.__lerpEvidenceTotal,
                    fromData = oldEvidenceTotal,
                    toData = self.evidenceTotal,
                    duration = 0.5,
                    blendType = 'easeOut'
                ),
                Func(bounceEvidenceLabel)
            )
            self.track.start()

    def __lerpValue(self, value):
        """
        Used to make the bar fill up smoothly
        """
        self.fill['value'] = value

    def __lerpEvidenceTotal(self, value):
        """
        Used to make evidence total count up smoothly.

        :param value:
        """
        self.evidenceLabel.setText(TTLocalizer.LawbotBossEvidenceCollected % int(value))

    def calculateGagIconZ(self, gag):
        """
        This function determines the vertical coordinate for the gag icons.
        It is based on a static bar size (ie if scale of bar changes global variables must be changed)
        """
        gags = (self.bugleAmount, self.aoogahAmount, self.trunkAmount, self.fogAmount)

        # Position that the gag icon would be if it were at the absolute bottom of the bar
        pos = verticalStart

        # Add in the shift needed to move to the point of the bar that we are filling in by default (0 evidence gained)
        pos += (minRange - minVisible) * valueVerticalShift

        # Add in the shift needed to move to the point that matches the evidence needed to get the gag
        pos += ((maxRange - minRange) / self.maxEvidence) * gags[gag] * valueVerticalShift
        return pos

    def enterRight(self):
        """
        Brings the bar in from right of screen
        """
        self.track = LerpPosInterval(self.barBG, 1, (-0.25, 0.0, 0.7), blendType = 'easeOut')
        self.track.start()
