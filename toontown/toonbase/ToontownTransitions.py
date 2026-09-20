from direct.showbase.Transitions import *
from panda3d.core import *
from direct.gui.DirectGui import DirectFrame
from direct.gui import DirectGuiGlobals as DGG
from direct.interval.IntervalGlobal import *
from toontown.toon.gui import GuiBinGlobals


class ToontownTransitions(Transitions):
    def __init__(self, loader, model=None, scale=3.0, pos=Vec3(0, 0, 0)):
        Transitions.__init__(self, loader, model, scale, pos)
        self.__transitionFuture = None

    def loadIris(self):
        Transitions.loadIris(self)
        self.iris.reparentTo(aspect2d, DGG.FADE_SORT_INDEX)
        self.iris.setBin('sorted-gui-popup', GuiBinGlobals.FadeBin)

    def loadFade(self):
        Transitions.loadFade(self)
        self.fade.reparentTo(aspect2d, DGG.FADE_SORT_INDEX),
        self.fade.setBin('sorted-gui-popup', GuiBinGlobals.FadeBin)

    def fadeScreen(self, alpha=0.5, t=0.3, finishIval=None, blendType='easeOut'):
        """
        Fades in a semitransparent screen over the camera plane
        to darken out the world. Useful for drawing attention to
        a dialog box for instance
        """

        if (t == 0):
            # Fade in immediately with no lerp
            #print "transitiosn: fadeIn 0.0"
            self.noTransitions()
            self.loadFade()
            
            self.fade.reparentTo(aspect2d, DGG.FADE_SORT_INDEX)
            self.fade.setBin('sorted-gui-popup', GuiBinGlobals.FadeBin)
            self.fade.setColor(self.alphaOn[0],
                               self.alphaOn[1],
                               self.alphaOn[2],
                               alpha)            

            fut = AsyncFuture()
            fut.setResult(None)
            return fut
        else:
            # Create a sequence that lerps the color out, then
            # parents the fade to hidden
            self.transitionIval = self.getFadeScreenIval(alpha, t, finishIval, blendType)
            self.transitionIval.append(Func(self.__finishTransition))
            self.__transitionFuture = AsyncFuture()
            self.transitionIval.start()
            return self.__transitionFuture
                           
    def getFadeScreenIval(self, alpha=0.5, t=0.5, finishIval=None, blendType='noBlend'):
        """
        Returns an interval without starting it.  This is particularly useful in
        cutscenes, so when the cutsceneIval is escaped out of we can finish the fade immediately
        """
        #self.noTransitions() masad: this creates a one frame pop, is it necessary?
        self.loadFade()
        alphaResult = (self.alphaOn[0], self.alphaOn[1], self.alphaOn[2], alpha)

        transitionIval = Sequence(
            Func(self.fade.reparentTo, aspect2d, DGG.FADE_SORT_INDEX),
            Func(self.fade.setBin, 'sorted-gui-popup', GuiBinGlobals.FadeBin),
            Func(self.fade.showThrough),  # in case aspect2d is hidden for some reason
            self.lerpFunc(self.fade, t,
                          alphaResult,
                          blendType=blendType),
            name = self.fadeTaskName
        )
        if finishIval:
            transitionIval.append(finishIval)
        return transitionIval

    def irisIn(self, t=0.5, finishIval=None, blendType = 'noBlend', delay=0.0):
        """
        Play an iris in transition over t seconds.
        Places a polygon on the aspect2d plane then lerps the scale
        of the iris polygon up so it looks like we iris in. When the
        scale lerp is finished, it parents the iris polygon to hidden.
        """
        self.noTransitions()
        self.loadIris()
        if t == 0:
            self.iris.detachNode()
            fut = AsyncFuture()
            fut.setResult(None)
            return fut
        else:
            def reparentIris():
                self.iris.reparentTo(aspect2d, DGG.FADE_SORT_INDEX)
                self.iris.setBin('sorted-gui-popup', GuiBinGlobals.FadeBin)

            scale = 0.18 * max(base.a2dRight, base.a2dTop)
            self.transitionIval = Sequence(
                Wait(delay),
                Func(reparentIris),
                LerpScaleInterval(self.iris, t, scale = scale, startScale = 0.01, blendType=blendType),
                Func(self.iris.detachNode),
                Func(self.__finishTransition),
                name=self.irisTaskName,
            )
            self.__transitionFuture = AsyncFuture()
            if finishIval:
                self.transitionIval.append(finishIval)
            self.transitionIval.start()
            return self.__transitionFuture

    def irisOut(self, t=0.5, finishIval=None, blendType='noBlend', delay=0.0):
        """
        Play an iris out transition over t seconds.
        Places a polygon on the aspect2d plane then lerps the scale
        of the iris down so it looks like we iris out. When the scale
        lerp is finished, it leaves the iris polygon covering the
        aspect2d plane until you irisIn or call noIris.
        """
        self.noTransitions()
        self.loadIris()
        self.loadFade()  # we need this to cover up the hole.
        if t == 0:
            self.iris.detachNode()
            self.fadeOut(0)
            fut = AsyncFuture()
            fut.setResult(None)
            return fut
        else:
            def reparentIris():
                self.iris.reparentTo(aspect2d, DGG.FADE_SORT_INDEX)
                self.iris.setBin('sorted-gui-popup', GuiBinGlobals.FadeBin)

            scale = 0.18 * max(base.a2dRight, base.a2dTop)
            self.transitionIval = Sequence(
                Wait(delay),
                Func(reparentIris),
                LerpScaleInterval(self.iris, t, scale = 0.01, startScale = scale, blendType=blendType),
                Func(self.iris.detachNode),
                # Use the fade to cover up the hole that the iris would leave
                Func(self.fadeOut, 0),
                Func(self.__finishTransition),
                name=self.irisTaskName,
            )
            self.__transitionFuture = AsyncFuture()
            if finishIval:
                self.transitionIval.append(finishIval)
            self.transitionIval.start()
            return self.__transitionFuture

    def getFadeInIval(self, t=0.5, finishIval=None, blendType='noBlend'):
        """
        Returns an interval without starting it.  This is particularly useful in
        cutscenes, so when the cutsceneIval is escaped out of we can finish the fade immediately
        """
        #self.noTransitions() masad: this creates a one frame pop, is it necessary?
        self.loadFade()

        transitionIval = Sequence(
            Func(self.fade.reparentTo, aspect2d, DGG.FADE_SORT_INDEX),
            Func(self.fade.setBin, 'sorted-gui-popup', GuiBinGlobals.FadeBin),
            Func(self.fade.showThrough),  # in case aspect2d is hidden for some reason
            self.lerpFunc(self.fade, t,
                          self.alphaOff,
                          # self.alphaOn,
                          blendType=blendType
                          ),
            Func(self.fade.detachNode),
            name = self.fadeTaskName,
        )
        if finishIval:
            transitionIval.append(finishIval)
        return transitionIval

    def getFadeOutIval(self, t=0.5, finishIval=None, blendType='noBlend'):
        """
        Create a sequence that lerps the color out, then
        parents the fade to hidden
        """
        self.noTransitions()
        self.loadFade()

        transitionIval = Sequence(
            Func(self.fade.reparentTo, aspect2d, DGG.FADE_SORT_INDEX),
            Func(self.fade.setBin, 'sorted-gui-popup', GuiBinGlobals.FadeBin),
            Func(self.fade.showThrough),  # in case aspect2d is hidden for some reason
            self.lerpFunc(self.fade, t,
                          self.alphaOn,
                          # self.alphaOff,
                          blendType=blendType
                          ),
            name = self.fadeTaskName,
        )
        if finishIval:
            transitionIval.append(finishIval)
        return transitionIval

    def fadeIn(self, t=0.5, finishIval=None, blendType='noBlend', delay=0.0):
        """
        Play a fade in transition over t seconds.
        Places a polygon on the aspect2d plane then lerps the color
        from black to transparent. When the color lerp is finished, it
        parents the fade polygon to hidden.
        """
        gsg = base.win.getGsg()
        if gsg:
            # If we're about to fade in from black, go ahead and
            # preload all the textures etc.
            base.graphicsEngine.renderFrame()
            base.render.prepareScene(gsg)
            base.render2d.prepareScene(gsg)

        if t == 0:
            # Fade in immediately with no lerp
            # print("transitions: fadeIn 0.0")
            self.noTransitions()
            self.loadFade()
            self.fade.detachNode()
            fut = AsyncFuture()
            fut.setResult(None)
            return fut
        else:
            # Create a sequence that lerps the color out, then
            # parents the fade to hidden
            self.transitionIval = Sequence(Wait(delay), self.getFadeInIval(t, finishIval, blendType))
            self.transitionIval.append(Func(self.__finishTransition))
            self.__transitionFuture = AsyncFuture()
            self.transitionIval.start()
            return self.__transitionFuture

    def __finishTransition(self):
        if self.__transitionFuture:
            self.__transitionFuture.setResult(None)
            self.__transitionFuture = None
