from panda3d.core import Vec3, Vec4, Point3
from direct.gui.DirectGui import DirectButton, DGG
from direct.interval.IntervalGlobal import Sequence, Parallel, Wait, Func, LerpPosInterval, LerpColorScaleInterval


class MainMenuButton(DirectButton):
    def __init__(self, parent=aspect2d, **kw):
        gui = loader.loadModel('phase_3/models/gui/ttcc_menu_buttons')
        optiondefs = (
            ('relief', None, None),
            ('image', (
                gui.find('**/menubtn'),
                gui.find('**/menubtn-press'),
                gui.find('**/menubtn'),
                gui.find('**/menubtn-press'),
            ), None),
            ('image_scale', (.3, .15, .15), None),
            ('image1_scale', (.3, .15, .15), None),
            ('image2_scale', (.3, .15, .15), None),
            ('text_fg', (1, 1, 1, 1), None),
            ('text_shadow', (0, 0, 0, 1), None),
            ('text_scale', 0.05, None),
            ('text_pos', (0, -0.02), None),
            ('hoverScale', 1.1, None),
        )
        self.defineoptions(kw, optiondefs)
        DirectButton.__init__(self, parent)
        self.initialiseoptions(MainMenuButton)
        scale = self['scale'] or 1.0
        if type(scale) in (int, float):
            hoverScale = scale * self['hoverScale']
        else:
            hoverScale = Vec3(*scale) * self['hoverScale']
        self.bind(DGG.ENTER, hoverButton, [self, hoverScale])
        self.bind(DGG.EXIT, hoverButton, [self, self['scale']])
        gui.removeNode()


class GoodMainMenuButton(MainMenuButton):
    def __init__(self, parent=aspect2d, **kw):
        if 'image_color' not in kw:
            kw['image_color'] = Vec4(0.299805, 0.614258, 1, 1)
        MainMenuButton.__init__(self, parent, **kw)


def hoverButton(button, scale, event=None):
    if scale is None:
        scale = 1.0
    Sequence(
        button.scaleInterval(.1, Vec3(scale) * 1.1, blendType='easeInOut'),
        button.scaleInterval(.1, Vec3(scale), blendType='easeInOut')
    ).start()


def staggeredFadeUp(items):
    seq = Sequence()
    for item in items:
        if item:
            item.setTransparency(1)
            finalPos = item.getPos()
            startPos = Point3(finalPos) - Point3(0, 0, .2)
            item.setColorScale(1, 1, 1, 0)
            par = Parallel(
                LerpPosInterval(item, .2, finalPos, startPos, blendType='easeInOut'),
                LerpColorScaleInterval(item, .2, Vec4(1, 1, 1, 1), Vec4(1, 1, 1, 0), blendType='easeInOut')
            )
            seq.append(Func(par.start))
            seq.append(Wait(.05))
    seq.start()


def staggeredFadePopin(items, scales=None):
    seq = Sequence()
    for i in xrange(len(items)):
        item = items[i]
        if item:
            if scales:
                scale = scales[i]
            else:
                scale = item.getScale()
            item.setTransparency(1)
            item.setScale(0.01)
            item.setColorScale(1, 1, 1, 0)
            par = Parallel(
                Sequence(
                    item.scaleInterval(.2, Vec3(scale * 1.1), blendType='easeInOut'),
                    item.scaleInterval(.1, Vec3(scale), blendType='easeInOut')
                ),
                LerpColorScaleInterval(item, .2, Vec4(1, 1, 1, 1), Vec4(1, 1, 1, 0), blendType='easeInOut')
            )
            seq.append(Func(par.start))
            seq.append(Wait(.05))
    seq.start()
