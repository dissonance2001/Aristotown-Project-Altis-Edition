import random

from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import ActorInterval, Func, LerpFunctionInterval, Sequence
from direct.showbase.PythonUtil import lerp
from panda3d.core import TransparencyAttrib


def hexToPCol(value):
    value = value.lstrip('#')
    return (
        int(value[0:2], 16) / 255.0,
        int(value[2:4], 16) / 255.0,
        int(value[4:6], 16) / 255.0,
        1.0,
    )


class LavaLamp(Actor):
    modelPath = 'phase_8/models/props/ttcc_prop_lavalamp-zero'
    idleAnimPath = 'phase_8/models/props/ttcc_prop_lavalamp-idle'
    shadowPath = 'phase_3/models/props/drop_shadow'

    colors = (
        ('BA2E28', 'BA682C'),
        ('65BA3B', '4BBA8B'),
        ('3B7BBA', '4032B6'),
        ('9028BA', 'BA296F'),
        ('BAB51C', '5CBA29'),
    )
    colorDuration = 3.0

    def __init__(self, colorIndex=0):
        Actor.__init__(
            self,
            self.modelPath,
            anims={'idle': self.idleAnimPath},
            flattenable=0,
            setFinal=1,
        )

        wantSmoothAnims = getattr(base, 'wantSmoothAnims', False)
        self.setBlend(frameBlend=wantSmoothAnims)

        colorIndex = int(colorIndex) % len(self.colors)
        middleFrame = 40 * colorIndex

        self.idleInterval = Sequence(
            ActorInterval(
                self,
                'idle',
                startFrame=middleFrame,
                endFrame=199,
            ),
            Func(self.pose, 'idle', 0),
            ActorInterval(
                self,
                'idle',
                startFrame=0,
                endFrame=middleFrame,
            ),
        )
        self.idleInterval.loop()
        self.idleInterval.setT(
            random.random() * self.idleInterval.getDuration()
        )

        self.lava = self.find('**/lava')
        self.startColor = hexToPCol(self.colors[colorIndex][0])
        self.endColor = hexToPCol(self.colors[colorIndex][1])

        self.colorInterval = Sequence(
            LerpFunctionInterval(
                self.updateColor,
                duration=self.colorDuration,
                fromData=0.0,
                toData=1.0,
            ),
            LerpFunctionInterval(
                self.updateColor,
                duration=self.colorDuration,
                fromData=1.0,
                toData=0.0,
            ),
        )
        self.colorInterval.loop()
        self.colorInterval.setT(
            random.random() * self.colorInterval.getDuration()
        )

        self.shadow = loader.loadModel(self.shadowPath)
        self.shadow.reparentTo(self)
        self.shadow.flattenLight()
        self.shadow.setScale(0.30)
        self.shadow.setZ(0.025)
        self.shadow.setColor(0, 0, 0, 0.5)
        self.shadow.setTransparency(TransparencyAttrib.MAlpha)

    def cleanup(self):
        if self.idleInterval:
            self.idleInterval.finish()
            self.idleInterval = None

        if self.colorInterval:
            self.colorInterval.finish()
            self.colorInterval = None

        if self.shadow:
            self.shadow.removeNode()
            self.shadow = None

        self.lava = None
        Actor.cleanup(self)

    def updateColor(self, t):
        if self.lava and not self.lava.isEmpty():
            self.lava.setColor(
                lerp(self.startColor[0], self.endColor[0], t),
                lerp(self.startColor[1], self.endColor[1], t),
                lerp(self.startColor[2], self.endColor[2], t),
                lerp(self.startColor[3], self.endColor[3], t),
            )

    def setStartColor(self, pCol=None):
        if pCol is None:
            self.startColor = hexToPCol(self.getDefaultStartColor())
        else:
            self.startColor = pCol

    def setEndColor(self, pCol=None):
        if pCol is None:
            self.endColor = hexToPCol(self.getDefaultEndColor())
        else:
            self.endColor = pCol

    def setSpeed(self, speed):
        self.idleInterval.setPlayRate(speed)
        self.colorInterval.setPlayRate(speed)

    def getDefaultStartColor(self):
        return self.colors[0][0]

    def getDefaultEndColor(self):
        return self.colors[0][1]
