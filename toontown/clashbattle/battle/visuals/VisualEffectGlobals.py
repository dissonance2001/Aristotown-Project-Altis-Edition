# Grabs the correct status effect class based on id
from toontown.clashbattle.battle.visuals.VisualEffectAttributes import VisualEffectList


def createVisualEffect(avProfile, effectEnum, extraArgs=None):
    extraArgs = extraArgs if extraArgs else []
    effectClass = VisualEffectList[effectEnum]
    newEffect = effectClass(avProfile, effectEnum, extraArgs)

    return newEffect
