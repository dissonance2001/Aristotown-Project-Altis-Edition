from direct.gui.DirectGui import DirectLabel
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task
from pandac.PandaModules import CollisionNode, CollisionPolygon, Point3, TextNode, TransparencyAttrib
from toontown.battle.BattleProps import globalPropPool
from toontown.safezone.PianoGui import PianoGui
from toontown.toonbase import ToontownGlobals


class GrandPiano(DirectObject):
    POSITION = (24.906, 19.635, 4.025)
    HPR = (-158.067, 0.0, 0.0)
    MODEL_HPR = (0.0, 0.0, 0.0)
    SCALE = 1.0
    GROUND_OFFSET = -0.78
    USE_DISTANCE = 9.0
    AUDIO_DIRECTORY = 'resources/instruments/piano/audio'
    MIDI_DIRECTORY = 'resources/instruments/piano/midi'

    def __init__(self):
        DirectObject.__init__(self)
        self.destroyed = False
        self.gui = None
        self.promptVisible = False
        self.chatBindingsSuspended = False
        self.keepAwakeTaskName = self.__taskName('keepAwake')
        self.collisionNodePath = None
        self.modelRoot = render.attachNewNode('GrandPianoRoot')
        self.modelRoot.setPosHpr(self.POSITION[0], self.POSITION[1], self.POSITION[2], self.HPR[0], self.HPR[1], self.HPR[2])
        try:
            self.model = globalPropPool.getProp('piano')
        except Exception as error:
            print('[GrandPiano] Could not load gag piano: %s' % error)
            self.model = None
        if self.model is None or self.model.isEmpty():
            print('[GrandPiano] Could not load BattleProps piano.')
            self.model = None
            self.modelRoot.removeNode()
            self.modelRoot = None
        else:
            self.model.reparentTo(self.modelRoot)
            self.model.setHpr(*self.MODEL_HPR)
            self.model.setScale(self.SCALE)
            self.model.pose('piano', 11)
            try:
                self.model.update()
            except:
                pass
            self.__centerAndGroundModel()
            self.__makeCollision()
        self.prompt = DirectLabel(parent=aspect2d, relief=None, text='Press Control to play the Grand Piano', text_align=TextNode.ACenter, text_scale=0.055, text_fg=(1.0, 1.0, 0.75, 1.0), text_shadow=(0.0, 0.0, 0.0, 1.0), text_shadowOffset=(0.04, 0.04), pos=(0.0, 0.0, -0.78))
        self.prompt.setTransparency(TransparencyAttrib.MAlpha)
        self.prompt.hide()
        self.accept('control', self.__tryOpen)
        taskMgr.add(self.__proximityTask, self.__taskName('proximity'))

    def __taskName(self, suffix):
        return 'GrandPiano-%s-%s' % (suffix, id(self))

    def __getBounds(self):
        if self.model is None:
            return None
        try:
            try:
                return self.model.getTightBounds(self.modelRoot)
            except TypeError:
                return self.model.getTightBounds()
        except:
            return None

    def __centerAndGroundModel(self):
        bounds = self.__getBounds()
        if not bounds:
            return
        minimum, maximum = bounds
        centerX = (minimum.getX() + maximum.getX()) * 0.5
        centerY = (minimum.getY() + maximum.getY()) * 0.5
        self.model.setPos(self.model.getX() - centerX, self.model.getY() - centerY, self.model.getZ() - minimum.getZ() + self.GROUND_OFFSET)

    def __makeCollision(self):
        bounds = self.__getBounds()
        if not bounds:
            return
        minimum, maximum = bounds
        width = maximum.getX() - minimum.getX()
        depth = maximum.getY() - minimum.getY()
        mx = minimum.getX() + width * 0.08
        Mx = maximum.getX() - width * 0.08
        my = minimum.getY() + depth * 0.08
        My = maximum.getY() - depth * 0.08
        mz = max(-0.05, minimum.getZ())
        Mz = maximum.getZ()
        node = CollisionNode('GrandPianoCollision')
        node.setIntoCollideMask(ToontownGlobals.WallBitmask)
        node.addSolid(CollisionPolygon(Point3(mx, My, mz), Point3(mx, my, mz), Point3(mx, my, Mz), Point3(mx, My, Mz)))
        node.addSolid(CollisionPolygon(Point3(Mx, my, mz), Point3(Mx, My, mz), Point3(Mx, My, Mz), Point3(Mx, my, Mz)))
        node.addSolid(CollisionPolygon(Point3(mx, my, mz), Point3(Mx, my, mz), Point3(Mx, my, Mz), Point3(mx, my, Mz)))
        node.addSolid(CollisionPolygon(Point3(Mx, My, mz), Point3(mx, My, mz), Point3(mx, My, Mz), Point3(Mx, My, Mz)))
        self.collisionNodePath = self.modelRoot.attachNewNode(node)

    def __localAvatarAvailable(self):
        return hasattr(base, 'localAvatar') and base.localAvatar is not None

    def __isCloseEnough(self):
        if self.model is None or not self.__localAvatarAvailable():
            return False
        try:
            toonPosition = base.localAvatar.getPos(render)
            usePosition = Point3(*self.POSITION)
            return (toonPosition - usePosition).length() <= self.USE_DISTANCE
        except:
            return False

    def __suspendChatHotkeys(self):
        if self.chatBindingsSuspended:
            return
        chatLog = getattr(getattr(base, 'cr', None), 'chatLog', None)
        if chatLog is None:
            return
        try:
            chatLog.ignore(getattr(base, 'CHAT_HOTKEY', 't'))
            chatLog.ignore('c')
            self.chatBindingsSuspended = True
        except:
            pass

    def __restoreChatHotkeys(self):
        if not self.chatBindingsSuspended:
            return
        chatLog = getattr(getattr(base, 'cr', None), 'chatLog', None)
        if chatLog is not None:
            try:
                chatLog.accept(getattr(base, 'CHAT_HOTKEY', 't'), chatLog.focusChat)
                chatLog.accept('c', chatLog.chatHotkey)
            except:
                pass
        self.chatBindingsSuspended = False

    def __keepAwakeTask(self, task):
        if self.destroyed or self.gui is None:
            return Task.done
        try:
            messenger.send('wakeup')
        except:
            pass
        if self.__localAvatarAvailable():
            try:
                if getattr(base.localAvatar, 'sleepFlag', 0):
                    base.localAvatar.wakeUp()
            except:
                pass
        return Task.again

    def __startKeepAwake(self):
        taskMgr.remove(self.keepAwakeTaskName)
        try:
            messenger.send('wakeup')
        except:
            pass
        taskMgr.doMethodLater(20.0, self.__keepAwakeTask, self.keepAwakeTaskName)

    def __stopKeepAwake(self):
        taskMgr.remove(self.keepAwakeTaskName)

    def __setPromptVisible(self, visible):
        visible = bool(visible)
        if visible == self.promptVisible:
            return
        self.promptVisible = visible
        if visible:
            self.prompt.show()
        else:
            self.prompt.hide()

    def __proximityTask(self, task):
        if self.destroyed:
            return Task.done
        self.__setPromptVisible(self.gui is None and self.__isCloseEnough())
        return Task.cont

    def __tryOpen(self):
        if self.destroyed or self.gui is not None or not self.__isCloseEnough():
            return
        self.openGui()

    def openGui(self):
        if self.gui is not None:
            return
        self.__setPromptVisible(False)
        self.__suspendChatHotkeys()
        self.__startKeepAwake()
        try:
            base.localAvatar.disableAvatarControls()
        except:
            try:
                base.localAvatar.controlManager.disableControls()
            except:
                pass
        try:
            base.localAvatar.loop('neutral')
        except:
            pass
        self.gui = PianoGui(closeCommand=self.closeGui, audioDirectory=self.AUDIO_DIRECTORY, midiDirectory=self.MIDI_DIRECTORY)

    def closeGui(self):
        gui = self.gui
        self.gui = None
        if gui is not None:
            gui.destroy()
        self.__restoreChatHotkeys()
        self.__stopKeepAwake()
        if self.__localAvatarAvailable():
            try:
                base.localAvatar.enableAvatarControls()
            except:
                try:
                    base.localAvatar.controlManager.enableControls()
                except:
                    pass

    def destroy(self):
        if self.destroyed:
            return
        self.destroyed = True
        taskMgr.remove(self.__taskName('proximity'))
        self.__stopKeepAwake()
        self.ignoreAll()
        self.closeGui()
        if self.prompt is not None:
            self.prompt.destroy()
            self.prompt = None
        if self.collisionNodePath is not None:
            self.collisionNodePath.removeNode()
            self.collisionNodePath = None
        if self.model is not None:
            try:
                self.model.cleanup()
            except:
                try:
                    self.model.removeNode()
                except:
                    pass
            self.model = None
        if self.modelRoot is not None:
            self.modelRoot.removeNode()
            self.modelRoot = None
