from __future__ import absolute_import
from direct.gui.DirectGui import DirectFrame
from pandac.PandaModules import TransparencyAttrib

from toontown.club.ClubClasses import ClubIcon

try:
    from toontown.club.ClubShopCatalog import (
        SHOP_COLORS,
        SHOP_COLOR_PULSERS,
        COLOR_PAYLOAD_OFFSET,
    )
except ImportError:
    SHOP_COLORS = ()
    SHOP_COLOR_PULSERS = {}
    COLOR_PAYLOAD_OFFSET = 1000


class ClubIconGUI(DirectFrame):
    backgrounds = loader.loadModel('phase_3.5/models/gui/clubs/club_backgrounds')
    icons = loader.loadModel('phase_3.5/models/gui/clubs/club_icons')

    # Corporate Clash's sixteen default Club colours used by Club creation.
    COLORS = (
        (0.800, 0.176, 0.176, 1),
        (0.804, 0.408, 0.176, 1),
        (0.804, 0.647, 0.176, 1),
        (0.729, 0.804, 0.176, 1),
        (0.490, 0.804, 0.176, 1),
        (0.259, 0.804, 0.176, 1),
        (0.176, 0.804, 0.333, 1),
        (0.176, 0.804, 0.565, 1),
        (0.176, 0.804, 0.804, 1),
        (0.176, 0.573, 0.804, 1),
        (0.176, 0.333, 0.804, 1),
        (0.251, 0.176, 0.804, 1),
        (0.490, 0.176, 0.804, 1),
        (0.722, 0.176, 0.804, 1),
        (0.804, 0.176, 0.647, 1),
        (0.804, 0.176, 0.416, 1),
    )

    @classmethod
    def _normalizeColorId(cls, colorId):
        try:
            return int(colorId or 0)
        except (TypeError, ValueError):
            return 0

    @classmethod
    def getColorSource(cls, colorId):
        """Resolve a saved colour ID to a static tuple or ClubColorPulser."""
        colorId = cls._normalizeColorId(colorId)

        # Shop colours are saved as 1000 + palette index.
        if SHOP_COLORS and colorId >= COLOR_PAYLOAD_OFFSET:
            paletteIndex = colorId - COLOR_PAYLOAD_OFFSET
            pulser = SHOP_COLOR_PULSERS.get(paletteIndex)
            if pulser is not None:
                return pulser
            if 0 <= paletteIndex < len(SHOP_COLORS):
                return SHOP_COLORS[paletteIndex]

        # Club creation uses the original sixteen zero-based indexes.
        if 0 <= colorId < len(cls.COLORS):
            return cls.COLORS[colorId]

        # Compatibility fallback for malformed or old saved values.
        return cls.COLORS[colorId % len(cls.COLORS)]

    @classmethod
    def getColor(cls, colorId):
        source = cls.getColorSource(colorId)
        if hasattr(source, 'getColor'):
            return source.getColor()
        return source

    @classmethod
    def isAnimatedColor(cls, colorId):
        return hasattr(cls.getColorSource(colorId), 'canUpdate') and \
               cls.getColorSource(colorId).canUpdate()

    def __init__(self, parent=None, clubIcon=None, **kw):
        DirectFrame.__init__(self, parent=parent, relief=None, **kw)
        self.initialiseoptions(ClubIconGUI)
        self.setTransparency(TransparencyAttrib.MAlpha)
        self.clubIcon = clubIcon or ClubIcon()
        self.backgroundFrame = DirectFrame(parent=self, relief=None)
        self.iconFrame = DirectFrame(parent=self, relief=None, scale=0.88)
        self.backgroundFrame.setTransparency(TransparencyAttrib.MAlpha)
        self.iconFrame.setTransparency(TransparencyAttrib.MAlpha)
        self._colorTaskName = 'ClubIconGUI-colorPulse-%s' % id(self)
        self._destroyed = False
        self.refresh()

    def setIcon(self, clubIcon):
        self.clubIcon = clubIcon
        self.refresh()

    def _findFirst(self, model, names):
        for name in names:
            node = model.find('**/%s' % name)
            if not node.isEmpty():
                return node
        return None

    def _stopColorTask(self):
        taskMgr.remove(self._colorTaskName)

    def _startColorTask(self):
        self._stopColorTask()
        icon = self.clubIcon
        if self.isAnimatedColor(icon.clubCol) or self.isAnimatedColor(icon.bgCol):
            taskMgr.doMethodLater(0.05, self._updateColorPulse,
                                  self._colorTaskName)

    def _applyColors(self):
        if self._destroyed:
            return
        icon = self.clubIcon
        self.backgroundFrame['image_color'] = self.getColor(icon.clubCol)
        self.backgroundFrame['geom_color'] = self.getColor(icon.bgCol)

    def _updateColorPulse(self, task):
        if self._destroyed or self.isEmpty():
            return task.done
        self._applyColors()
        task.delayTime = 0.05
        return task.again

    def refresh(self):
        self._stopColorTask()
        icon = self.clubIcon
        baseNode = self._findFirst(self.backgrounds, ('base', 'Base', 'background_base'))
        backgroundNode = None
        iconNode = None

        if icon.backgroundId:
            backgroundNode = self._findFirst(self.backgrounds, (
                'bg_%s' % icon.backgroundId,
                'background_%s' % icon.backgroundId,
            ))

        if icon.iconId:
            iconNode = self._findFirst(self.icons, (
                'icon_%s' % icon.iconId,
                'Icon_%s' % icon.iconId,
            ))

        self.backgroundFrame['image'] = baseNode
        self.backgroundFrame['geom'] = backgroundNode
        self.iconFrame['geom'] = iconNode
        self.iconFrame['geom_color'] = (1, 1, 1, 1)
        self._applyColors()
        self._startColorTask()

    def destroy(self):
        if self._destroyed:
            return
        self._destroyed = True
        self._stopColorTask()
        DirectFrame.destroy(self)
