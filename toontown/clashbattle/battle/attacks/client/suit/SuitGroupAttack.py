from toontown.battle.attacks.client.suit.SuitSingleAttack import SuitSingleAttack


class SuitGroupAttack(SuitSingleAttack):

    def getCameraShot(self, duration):
        return self.camera.randomGroupAttackCam(
            self.invoker, self.targetDicts, self.battle, duration, self.OPEN_SHOT_DUR)
