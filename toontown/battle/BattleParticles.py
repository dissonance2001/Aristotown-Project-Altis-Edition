import os
from direct.particles.ParticleEffect import *
from direct.directnotify import DirectNotifyGlobal
from direct.showbase import AppRunnerGlobal
from toontown.battle import ParticleDefs

notify = DirectNotifyGlobal.directNotify.newCategory('BattleParticles')
TutorialParticleEffects = ('gearExplosionBig.ptf', 'gearExplosionSmall.ptf', 'gearExplosion.ptf')
ParticleNames = ('nickelDimeWaterfall', 'nickelDime', 'audit-div', 'audit-five', 'audit-four', 'audit-minus', 'audit-mult', 'audit-one', 'audit-plus', 'audit-six', 'audit-three', 'audit-two', 'blah', 'brainstorm-box', 'brainstorm-env', 'brainstorm-track', 'buzzwords-crash', 'buzzwords-inc', 'buzzwords-main', 'buzzwords-over', 'buzzwords-syn', 'confetti', 'doubletalk-double', 'doubletalk-dup', 'doubletalk-good', 'filibuster-cut', 'filibuster-fiscal', 'filibuster-impeach', 'filibuster-inc', 'jargon-brow', 'jargon-deep', 'jargon-hoop', 'jargon-ipo', 'legalese-hc', 'legalese-qpq', 'legalese-vd', 'mumbojumbo-boiler', 'mumbojumbo-creative', 'mumbojumbo-deben', 'mumbojumbo-high', 'mumbojumbo-iron', 'poundsign', 'schmooze-genius', 'schmooze-instant', 'schmooze-master', 'schmooze-viz', 'roll-o-dex', 'rollodex-card', 'dagger', 'fire', 'snow-particle', 'raindrop', 'gear', 'checkmark', 'dollar-sign', 'spark')
particleModel = None
particleSearchPath = None

def loadParticles():
    global particleModel
    if particleModel == None:
        particleModel = loader.loadModel('phase_3.5/models/props/suit-particles')

def unloadParticles():
    global particleModel
    if particleModel != None:
        particleModel.removeNode()
    del particleModel
    particleModel = None


def getParticle(name):
    if name in ParticleNames:
        particle = particleModel.find('**/' + str(name))
        return particle
    else:
        notify.warning('getParticle() - no name: %s' % name)
        return None
    
    return None

def loadParticleFile(name):
    assert name.endswith('.ptf')
    name = name[:-4] # Strip .ptf
    particleFunc = ParticleDefs.ParticleTable[name]

    effect = ParticleEffect()
    particleFunc(effect)
    return effect

def createParticleEffect(name = None, file = None, numParticles = None, color = None):
    if not name:
        fileName = file + '.ptf'
        return loadParticleFile(fileName)
    if name == 'GearExplosion':
        return __makeGearExplosion(numParticles)
    elif name == 'BigGearExplosion':
        return __makeGearExplosion(numParticles, 'Big')
    elif name == 'WideGearExplosion':
        return __makeGearExplosion(numParticles, 'Wide')
    elif name == 'BrainStorm':
        return loadParticleFile('brainStorm.ptf')
    elif name == 'ReOrgSprayNew':
        return loadParticleFile('ReOrgSprayNew.ptf')
    elif name == 'BuzzWord':
        return loadParticleFile('buzzWord.ptf')
    elif name == 'Calculate':
        return loadParticleFile('calculate.ptf')
    elif name == 'Confetti':
        return loadParticleFile('confetti.ptf')
    elif name == 'DemotionFreeze':
        return loadParticleFile('demotionFreeze.ptf')
    elif name == 'FireSpray':
        return loadParticleFile('FireSpray.ptf')
    elif name == 'FireSprayCan':
        return loadParticleFile('FireSprayCan.ptf')
    elif name == 'FireSprayPromotion':
        return loadParticleFile('FireSprayPromotion.ptf')
    elif name == 'BurnSpray':
        return loadParticleFile('BurnSpray.ptf')
    elif name == 'ZapSpray':
        return loadParticleFile('ZapSpray.ptf')
    elif name == 'demotionUnFreeze2':
        return loadParticleFile('demotionUnFreeze2.ptf')
    elif name == 'DemotionSpray':
        return loadParticleFile('demotionSpray.ptf')
    elif name == 'DemotionSpray3':
        return loadParticleFile('reOrgSpray2.ptf')
    elif name == 'downsizeCloud2':
        return loadParticleFile('downsizeCloud2.ptf')
    elif name == 'downsizeSpray2':
        return loadParticleFile('downsizeSpray2.ptf')
    elif name == 'DemotionFreeze2':
        return loadParticleFile('demotionFreeze2.ptf')
    elif name == 'DemotionSpray2':
        return loadParticleFile('demotionSpray2.ptf')
    elif name == 'DoubleTalkLeft':
        return loadParticleFile('doubleTalkLeft.ptf')
    elif name == 'DoubleTalkRight':
        return loadParticleFile('doubleTalkRight.ptf')
    elif name == 'FingerWag':
        return loadParticleFile('fingerwag.ptf')
    elif name == 'FiredFlame':
        return loadParticleFile('firedFlame.ptf')
    elif name == 'FiredFlame2':
        return loadParticleFile('firedFlame2.ptf')
    elif name == 'FreezeAssets':
        return loadParticleFile('freezeAssets.ptf')
    elif name == 'GlowerPower':
        return loadParticleFile('glowerPowerKnives.ptf')
    elif name == 'HostileTakeover':
        return loadParticleFile('glowerPowerKnives.ptf')
    elif name == 'WaterSpray':
        return loadParticleFile('waterSpray.ptf')
    elif name == 'nickelDime':
        return loadParticleFile('nickelDime.ptf')
    elif name == 'nickelDimeWaterfall':
        return loadParticleFile('nickelDimeWaterfall.ptf')
    elif name == 'SprayLift':
        return __makeSprayLift()
    elif name == 'HeavyRainfall':
        return loadParticleFile('liquidate2.ptf')
    elif name == 'paperRainfall':
        return loadParticleFile('paperRainfall.ptf')
    elif name == 'HotAir':
        return loadParticleFile('hotAirSpray.ptf')
    elif name == 'HotAir2':
        return loadParticleFile('hotAirSpray2.ptf')
    elif name == 'PoundKey':
        return loadParticleFile('poundkey.ptf')
    elif name == 'ShiftSpray':
        return loadParticleFile('shiftSpray.ptf')
    elif name == 'PoisonSpray':
        return loadParticleFile('poisonSpray.ptf')
    elif name == 'oilRain':
        return loadParticleFile('oilRain.ptf')
    elif name == 'PoisonLift':
        return __makePoisonLift()
    elif name == 'SprayLift':
        return __makeSprayLift()
    elif name == 'ShiftLift':
        return __makeShiftLift()
    elif name == 'InsuranceLift':
        return __makeInsuranceLift()
    elif name == 'SyphonLift':
        return __makeSyphonLift()
    elif name == 'Shred':
        return loadParticleFile('shred.ptf')
    elif name == 'Smile':
        return loadParticleFile('smile.ptf')
    elif name == 'Smoke':
        return loadParticleFile('smoke.ptf')
    elif name == 'SpriteFiredFlecks':
        return loadParticleFile('spriteFiredFlecks.ptf')
    elif name == 'Synergy':
        return loadParticleFile('synergy.ptf')
    elif name == 'Waterfall':
        return loadParticleFile('waterfall.ptf')
    elif name == 'dataSpray':
        return loadParticleFile('dataSpray.ptf')
    elif name == 'FreezingRain':
        return loadParticleFile('snow.ptf')
    elif name == 'SnowWaterfall':
        return loadParticleFile('snowWaterfall.ptf')
    elif name == 'HeatWave':
        return loadParticleFile('heatwave.ptf')
    elif name == 'GoldRush':
        return loadParticleFile('goldRush.ptf')
    elif name == 'HeatWaveWaterfall':
        return loadParticleFile('heatwaveWaterfall.ptf')
    elif name == 'OrganizeEffect':
        return loadParticleFile('organizeEffect.ptf')
    elif name == 'OrganizeSpray':
        return loadParticleFile('organizeSpray.ptf')
    elif name == 'SplashLines':
        return loadParticleFile('splashlines.ptf')
    elif name == 'PoundKey':
        return loadParticleFile('poundkey.ptf')
    elif name == 'RubOut':
        return __makeRubOut(color)
    elif name == 'SplashLines':
        return loadParticleFile('splashlines.ptf')
    elif name == 'Shred2':
        return loadParticleFile('shred2.ptf')
    elif name == 'Withdrawal':
        return loadParticleFile('withdrawal.ptf')
    else:
        notify.warning('createParticleEffect() - no name: %s' % name)
    return None


def setEffectTexture(effect, name, color = None):
    particles = effect.getParticlesNamed('particles-1')
    np = getParticle(name)
    if color:
        particles.renderer.setColor(color)
    particles.renderer.setFromNode(np)


def __makeGearExplosion(numParticles = None, style = 'Normal'):
    if style == 'Normal':
        effect = loadParticleFile('gearExplosion.ptf')
    elif style == 'Big':
        effect = loadParticleFile('gearExplosionBig.ptf')
    elif style == 'Wide':
        effect = loadParticleFile('gearExplosionWide.ptf')
    if numParticles:
        particles = effect.getParticlesNamed('particles-1')
        particles.setPoolSize(numParticles)
    return effect


def __makeRubOut(color = None):
    effect = loadParticleFile('demotionUnFreeze.ptf')
    loadParticles()
    setEffectTexture(effect, 'snow-particle')
    particles = effect.getParticlesNamed('particles-1')
    particles.renderer.setInitialXScale(0.03)
    particles.renderer.setFinalXScale(0.0)
    particles.renderer.setInitialYScale(0.02)
    particles.renderer.setFinalYScale(0.0)
    if color:
        particles.renderer.setColor(color)
    else:
        particles.renderer.setColor(Vec4(0.54, 0.92, 0.32, 0.7))
    return effect


def __makeShiftLift():
    effect = loadParticleFile('pixieDrop.ptf')
    particles = effect.getParticlesNamed('particles-1')
    particles.renderer.setCenterColor(Vec4(1, 1, 0, 0.9))
    particles.renderer.setEdgeColor(Vec4(1, 1, 0, 0.6))
    particles.emitter.setRadius(0.01)
    effect.setHpr(0, 180, 0)
    effect.setPos(0, 0, 0)
    return effect

def __makeInsuranceLift():
    effect = loadParticleFile('pixieDrop.ptf')
    particles = effect.getParticlesNamed('particles-1')
    particles.renderer.setCenterColor(Vec4(0, 1, 0.078, 0.9))
    particles.renderer.setEdgeColor(Vec4(0, 1, 0.078, 0.6))
    particles.emitter.setRadius(0.01)
    effect.setHpr(0, 180, 0)
    effect.setPos(0, 0, 0)
    return effect

def __makeSyphonLift():
    effect = loadParticleFile('pixieDrop.ptf')
    particles = effect.getParticlesNamed('particles-1')
    particles.renderer.setCenterColor(Vec4(1, 0, 0, 0.9))
    particles.renderer.setEdgeColor(Vec4(1, 0, 0, 0.6))
    particles.emitter.setRadius(0.01)
    effect.setHpr(0, 180, 0)
    effect.setPos(0, 0, 0)
    return effect


def __makePoisonLift():
    effect = loadParticleFile('pixieDrop.ptf')
    particles = effect.getParticlesNamed('particles-1')
    particles.renderer.setCenterColor(Vec4(0, 1, 0, 1))
    particles.renderer.setEdgeColor(Vec4(0, 1, 0, 1))
    particles.emitter.setRadius(0.01)
    effect.setHpr(0, 180, 0)
    effect.setPos(0, 0, 0)
    return effect


def __makeSprayLift():
    effect = loadParticleFile('pixieDrop.ptf')
    particles = effect.getParticlesNamed('particles-1')
    particles.renderer.setCenterColor(Vec4(0.5, 1, 1, 1))
    particles.renderer.setEdgeColor(Vec4(0.5, 1, 1, 1))
    particles.emitter.setRadius(0.01)
    effect.setHpr(0, 180, 0)
    effect.setPos(0, 0, 0)
    return effect
