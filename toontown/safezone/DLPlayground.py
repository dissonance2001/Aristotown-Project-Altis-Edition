from toontown.safezone import Playground
from toontown.toonbase import TTLocalizer
from panda3d.core import Vec4


class DLPlayground(Playground.Playground):

    def enter(self, requestStatus):
        Playground.Playground.enter(self, requestStatus)
        render.setColorScale(Vec4(.55, .55, .65, 1))
        # Add the fog to the sky np
        self.fog.attachFog([base.cr.playGame.hood.sky])

    def exit(self):
        # Fog is totally cleaned up in Playground's exit call
        Playground.Playground.exit(self)
        render.setColorScale(Vec4(1, 1, 1, 1))
