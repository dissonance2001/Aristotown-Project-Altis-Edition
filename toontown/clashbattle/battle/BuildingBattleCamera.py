from toontown.clashbattle.battle.BattleCamera import BattleCamera


class BuildingBattleCamera(BattleCamera):

    def enterWaitForInput(self, **kwargs) -> None:
        """Move the camera into position for the input state of battle."""
        camHeight = max([suit.getHeight() + 1 for suit in self.suits])
        self.getPosWaitForInput().setZ(min(max(camHeight * 2, 16.5), 18))
        self._seq = camera.posHprInterval(
            0.4, self.getPosWaitForInput(), self.getHprWaitForInput(), blendType = 'easeInOut'
        )
        self._seq.start()
        base.camLens.setMinFov(self.getFovWaitForInput()/(4./3.))
