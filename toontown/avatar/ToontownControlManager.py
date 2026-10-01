from direct.controls.ControlManager import ControlManager
from direct.showbase.InputStateGlobal import inputState
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class ToontownControlManager(ControlManager):
    def __init__(self, enable=True):
        self.forceTokens = None
        self.craneControlsEnabled = False

        self.lmbControlEnabled = False
        self.lmbStateToken = None

        ControlManager.__init__(self, enable)

    def enable(self):
        assert self.notify.debugCall(id(self))

        if self.isEnabled:
            assert self.notify.debug('already isEnabled')
            return

        self.isEnabled = 1

        self.enableControls()

        # keep track of what we do on the inputState so we can undo it later on
        #self.inputStateTokens = []
        if base.wantExtraMovement:
            ist = self.inputStateTokens
            ist.append(inputState.watch("run", 'runningEvent', "running-on", "running-off"))

            ist.append(inputState.watchWithModifiers("forward", base.MOVE_UP, inputSource=inputState.ArrowKeys))
            ist.append(inputState.watchWithModifiers("forward", 'arrow_up', inputSource=inputState.ArrowKeys))
            ist.append(inputState.watch("forward", "force-forward", "force-forward-stop"))

            ist.append(inputState.watchWithModifiers("reverse", base.MOVE_DOWN, inputSource=inputState.ArrowKeys))
            ist.append(inputState.watchWithModifiers("reverse", 'arrow_down', inputSource=inputState.ArrowKeys))
            ist.append(inputState.watchWithModifiers("reverse", "mouse4", inputSource=inputState.Mouse))

            ist.append(inputState.watchWithModifiers("turnLeft", base.MOVE_LEFT, inputSource=inputState.ArrowKeys))
            ist.append(inputState.watchWithModifiers("turnLeft", 'arrow_left', inputSource=inputState.ArrowKeys))
            ist.append(inputState.watch("turnLeft", "mouse-look_left", "mouse-look_left-done"))
            ist.append(inputState.watch("turnLeft", "force-turnLeft", "force-turnLeft-stop"))

            ist.append(inputState.watchWithModifiers("turnRight", base.MOVE_RIGHT, inputSource=inputState.ArrowKeys))
            ist.append(inputState.watchWithModifiers("turnRight", 'arrow_right', inputSource=inputState.ArrowKeys))
            ist.append(inputState.watch("turnRight", "mouse-look_right", "mouse-look_right-done"))
            ist.append(inputState.watch("turnRight", "force-turnRight", "force-turnRight-stop"))

            ist.append(inputState.watchWithModifiers("jump", base.JUMP))
            ist.append(inputState.watchWithModifiers("jump", 'control'))
        else:
            ist = self.inputStateTokens
            ist.append(inputState.watch("run", 'runningEvent', "running-on", "running-off"))

            ist.append(inputState.watchWithModifiers("forward", base.MOVE_UP, inputSource=inputState.ArrowKeys))
            ist.append(inputState.watch("forward", "force-forward", "force-forward-stop"))

            ist.append(inputState.watchWithModifiers("reverse", base.MOVE_DOWN, inputSource=inputState.ArrowKeys))
            ist.append(inputState.watchWithModifiers("reverse", "mouse4", inputSource=inputState.Mouse))

            ist.append(inputState.watchWithModifiers("turnLeft", base.MOVE_LEFT, inputSource=inputState.ArrowKeys))
            ist.append(inputState.watch("turnLeft", "mouse-look_left", "mouse-look_left-done"))
            ist.append(inputState.watch("turnLeft", "force-turnLeft", "force-turnLeft-stop"))

            ist.append(inputState.watchWithModifiers("turnRight", base.MOVE_RIGHT, inputSource=inputState.ArrowKeys))
            ist.append(inputState.watch("turnRight", "mouse-look_right", "mouse-look_right-done"))
            ist.append(inputState.watch("turnRight", "force-turnRight", "force-turnRight-stop"))

            ist.append(inputState.watchWithModifiers("jump", base.JUMP))

        self.setTurn(1)

        if self.currentControls:
            self.currentControls.enableAvatarControls()

    def _clearMovementInputState(self):
        for state in ('run', 'forward', 'reverse', 'turnLeft', 'turnRight', 'slideLeft', 'slideRight', 'jump'):
            inputState.set(state, False)
            inputState.set(state, False, inputSource=inputState.ArrowKeys)
            inputState.set(state, False, inputSource=inputState.WASD)

    def enableControls(self):
        if self.forceTokens:
            for token in self.forceTokens:
                token.release()
            self.forceTokens = []
        self._clearMovementInputState()

    def disableControls(self):
        self._clearMovementInputState()
        if base.wantTalkKey:
            self.forceTokens = [
                inputState.force('jump', 0, 'ToontownControlManager.disableControls'),
                inputState.force('forward', 0, 'ToontownControlManager.disableControls'),
                inputState.force('turnLeft', 0, 'ToontownControlManager.disableControls'),
                inputState.force('slideLeft', 0, 'ToontownControlManager.disableControls'),
                inputState.force('reverse', 0, 'ToontownControlManager.disableControls'),
                inputState.force('turnRight', 0, 'ToontownControlManager.disableControls'),
                inputState.force('slideRight', 0, 'ToontownControlManager.disableControls')
            ]

    def setTurn(self, turn):
        self.__WASDTurn = turn

        if not self.isEnabled:
            return

        turnLeftWASDSet = inputState.isSet("turnLeft", inputSource=inputState.ArrowKeys)
        turnRightWASDSet = inputState.isSet("turnRight", inputSource=inputState.ArrowKeys)
        slideLeftWASDSet = inputState.isSet("slideLeft", inputSource=inputState.ArrowKeys)
        slideRightWASDSet = inputState.isSet("slideRight", inputSource=inputState.ArrowKeys)

        for token in self.WASDTurnTokens:
            token.release()

        if turn:
            if base.wantExtraMovement:
                self.WASDTurnTokens = (
                    inputState.watchWithModifiers("turnLeft", base.MOVE_LEFT, inputSource=inputState.ArrowKeys),
                    inputState.watchWithModifiers("turnLeft", 'arrow_left', inputSource=inputState.ArrowKeys),
                    inputState.watchWithModifiers("turnRight", base.MOVE_RIGHT, inputSource=inputState.ArrowKeys),
                    inputState.watchWithModifiers("turnRight", 'arrow_right', inputSource=inputState.ArrowKeys),
                    )
            else:
                self.WASDTurnTokens = (
                    inputState.watchWithModifiers("turnLeft", base.MOVE_LEFT, inputSource=inputState.ArrowKeys),
                    inputState.watchWithModifiers("turnRight", base.MOVE_RIGHT, inputSource=inputState.ArrowKeys),
                    )

            inputState.set("turnLeft", slideLeftWASDSet, inputSource=inputState.ArrowKeys)
            inputState.set("turnRight", slideRightWASDSet, inputSource=inputState.ArrowKeys)

            inputState.set("slideLeft", False, inputSource=inputState.ArrowKeys)
            inputState.set("slideRight", False, inputSource=inputState.ArrowKeys)

        else:
            if base.wantExtraMovement:
                self.WASDTurnTokens = (
                    inputState.watchWithModifiers("slideLeft", base.MOVE_LEFT, inputSource=inputState.ArrowKeys),
                    inputState.watchWithModifiers("slideLeft", 'arrow_left', inputSource=inputState.ArrowKeys),
                    inputState.watchWithModifiers("slideRight", base.MOVE_RIGHT, inputSource=inputState.ArrowKeys),
                    inputState.watchWithModifiers("slideRight", 'arrow_right', inputSource=inputState.ArrowKeys),
                    )
            else:
                self.WASDTurnTokens = (
                    inputState.watchWithModifiers("slideLeft", base.MOVE_LEFT, inputSource=inputState.ArrowKeys),
                    inputState.watchWithModifiers("slideRight", base.MOVE_RIGHT, inputSource=inputState.ArrowKeys),
                    )

            inputState.set("slideLeft", turnLeftWASDSet, inputSource=inputState.ArrowKeys)
            inputState.set("slideRight", turnRightWASDSet, inputSource=inputState.ArrowKeys)

            inputState.set("turnLeft", False, inputSource=inputState.ArrowKeys)
            inputState.set("turnRight", False, inputSource=inputState.ArrowKeys)

    def enableCraneControls(self):
        """
        This function should only be called for when our controls are disabled, but we need to map our movement keys to
        functions. (i.e. on a crane, on a banquet table, etc.)
        This serves as an improved implementation of 'passMessagesThrough'.
        """
        if self.isEnabled and self.craneControlsEnabled:
            return

        if base.wantExtraMovement:
            ist = self.inputStateTokens
            ist.extend((
                inputState.watchWithModifiers("forward", base.MOVE_UP, inputSource=inputState.ArrowKeys),
                inputState.watchWithModifiers("forward", 'arrow_up', inputSource=inputState.ArrowKeys),
                inputState.watchWithModifiers("reverse", base.MOVE_DOWN, inputSource=inputState.ArrowKeys),
                inputState.watchWithModifiers("reverse", 'arrow_down', inputSource=inputState.ArrowKeys),
                inputState.watchWithModifiers("turnLeft", base.MOVE_LEFT, inputSource=inputState.ArrowKeys),
                inputState.watchWithModifiers("turnLeft", 'arrow_left', inputSource=inputState.ArrowKeys),
                inputState.watchWithModifiers("turnRight", base.MOVE_RIGHT, inputSource=inputState.ArrowKeys),
                inputState.watchWithModifiers("turnRight", 'arrow_right', inputSource=inputState.ArrowKeys)
            ))
        else:
            ist = self.inputStateTokens
            ist.extend((
                inputState.watchWithModifiers("forward", base.MOVE_UP, inputSource=inputState.ArrowKeys),
                inputState.watchWithModifiers("reverse", base.MOVE_DOWN, inputSource=inputState.ArrowKeys),
                inputState.watchWithModifiers("turnLeft", base.MOVE_LEFT, inputSource=inputState.ArrowKeys),
                inputState.watchWithModifiers("turnRight", base.MOVE_RIGHT, inputSource=inputState.ArrowKeys)
            ))

    def disableCraneControls(self):
        """
        Disables crane controls, if they are currently set.
        """
        if not self.isEnabled and not self.craneControlsEnabled:
            return

        for token in self.inputStateTokens:
            token.release()
        self.inputStateTokens = []

    def enableLMBForward(self):
        if not self.isEnabled:
            return

        if not self.lmbStateToken:
            self.lmbStateToken = inputState.watchWithModifiers("forward", "mouse1")

    def disableLMBForward(self):
        if self.lmbStateToken:
            messenger.send('mouse1-up')  # cleans this up so that we don't infinitely run.
            self.lmbStateToken.release()
            self.lmbStateToken = None
