from panda3d.core import ConfigVariableInt, VBase4, Texture, SequenceNode, NodePath
from direct.actor import Actor
from toontown.toonbase import ToontownGlobals
import random

from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

Props = ((5, 'partyBall', 'partyBall'),
 (5,
  'feather',
  'feather-mod',
  'feather-chan'),
 (5, 'lips', 'lips'),
 (5, 'lipstick', 'lipstick'),
 (5,
  'treasure-chest',
  'treasure-chest-mod',
  'treasure-chest-chan'),
  (5.5, 'popsicle', 'popsicle_treasure'),
  (5,
   'cannon',
   'cannon-mod',
   'cannon-chan',
   'cannon-grow',
   'cannon-miss'),
 (5, 'hat', 'hat'),
 (5, 'cane', 'cane'),
 (5,
  'cubes',
  'cubes-mod',
  'cubes-chan'),
 (5, 'ladder', 'ladder2'),
 (4,
  'fishing-pole',
  'fishing-pole-mod',
  'fishing-pole-chan'),
 (5,
  '1dollar',
  '1dollar-bill-mod',
  '1dollar-bill-chan'),
 (5, 'big-magnet', 'magnet'),
 (5,
  'hypno-goggles',
  'hypnotize-mod',
  'hypnotize-chan'),
 (5, 'slideshow', 'av_screen'),
 (3.5,
  'zapbeam',
  'zap_beam-mod',
  'zap_beam-chan'),
 (3.5, 'joybuzz', 'joybuzz'),
 (5, 'zapRug', 'zapRug'),
 (5, 'lightbulb', 'ttcc_gag_lightbulb'),
 (5, 'radio', 'ttcc_gag_radio'),
 (5, 'stagelight', 'ttcc_gag_stagelight'),
 (3.5, 'battery', 'battery'),
 (3.5, 'tv', 'tv'),
 (3.5, 'tesla', 'tesla'),
 (5, 'lightning', 'lightning'),
  # Unused Zap gags
 (3.5, 'balloon', 'balloon'),
 (3.5, 'tazer', 'tazer'),
 (5,
  'banana',
  'banana-peel-mod',
  'banana-peel-chan'),
 (5,
  'rake',
  'rake-mod',
  'rake-chan'),
 (5,
  'marbles',
  'marbles-mod',
  'marbles-chan'),
 (5,
  'tnt',
  'tnt-mod',
  'tnt-chan'),
 (5, 'trapdoor', 'trapdoor'),
 (5, 'spring', 'spring'),
 (5, 'quicksand', 'quicksand'),
 (5, 'wreckingball', 'wreckingball'),
 (5, 'xspot', 'xspot'),
 (5, 'traintrack', 'traintrack2'),
 (5, 'train', 'train'),
 (5, 'megaphone', 'megaphone'),
 (5, 'aoogah', 'aoogah'),
 (5, 'bikehorn', 'bikehorn'),
 (5, 'bugle', 'bugle'),
 (5, 'elephant', 'elephant'),
 (5, 'fog_horn', 'fog_horn'),
 (5, 'whistle', 'whistle'),
 (5, 'kazoo', 'kazoo'),
 (5, 'singing', 'singing'),
 (3.5, 'creampie', 'tart'),
 (5, 'fruitpie', 'fruit-pie'),
 (3.5, 'cupcake', 'cupcake'),
 (5, 'fruitpie-slice', 'fruit-pie-slice'),
 (5, 'creampie-slice', 'cream-pie-slice'),
 (5,
  'birthday-cake-slice',
  'birthday-cake-slice-mod',
  'birthday-cake-slice-chan'),
 (5,
  'birthday-cake',
  'birthday-cake-mod',
  'birthday-cake-chan'),
 (5, 'wedding-cake', 'wedding_cake'),
 (3.5, 'squirting-flower', 'squirting-flower'),
 (5,
  'glass',
  'glass-mod',
  'glass-chan'),
 (4, 'water-gun', 'water-gun'),
 (5, 'waterBalloon', 'waterBalloon'),
 (3.5, 'bottle', 'bottle'),
 (5,
  'firehose',
  'firehose-mod',
  'firehose-chan'),
 (5, 'hydrant', 'battle_hydrant'),
 (4,
  'stormcloud',
  'stormcloud-mod',
  'stormcloud-chan'),
 (5, 'geyser', 'geyser'),
 (3.5,
  'button',
  'button-mod',
  'button-chan'),
 (3.5, 'button-no-actor', 'button-mod'),
 (5,
  'flowerpot',
  'flowerpot-mod',
  'flowerpot-chan'),
 (5,
  'sandbag',
  'sandbag-mod',
  'sandbag-chan'),
 (5,
  'bowling_ball',
  'bowling_ball-mod',
  'bowling_ball-chan'),
 (4,
  'anvil',
  'anvil-mod',
  'anvil-chan'),
 (5,
  'weight',
  'weight-mod',
  'weight-chan'),
 (5,
  'safe',
  'safe-mod',
  'safe-chan'),
 (5,
  'boulder',
  'boulder-mod',
  'boulder-chan'),
 (5,
  'piano',
  'piano-mod',
  'piano-chan'),
 (5,
  'rake-react',
  'rake-step-mod',
  'rake-step-chan'),
 (5, 'pad', 'pad'),
 (4,
  'propeller',
  'propeller-mod',
  'propeller-chan'),
 (5,
  'calculator',
  'cc_a_prp_bat_calculator-mod',
  'cc_a_prp_bat_calculator-calculate',
  'cc_a_prp_bat_calculator-calculating-costs'),
 (5, 'rollodex', 'roll-o-dex'),
 (5, 'rubber-stamp', 'cc_m_prp_bat_rubberStamp'),
 (5, 'rubber-stamp-pad', 'cc_m_prp_bat_rubberStamp_pad'),
 (5,
  'smile',
  'smile-mod',
  'smile-chan'),
 (5, 'golf-club', 'cc_m_prp_bat_golfClub'),
 (5, 'golf-ball', 'golf-ball'),
 (5, 'redtape', 'redtape'),
 (5, 'redtape-tube', 'redtape-tube'),
 (5, 'bounced-check', 'bounced-check'),
 (5, 'bonus-check', 'bonus-check'),
 (3.5,
  'clip-on-tie',
  'clip-on-tie-mod',
  'clip-on-tie-chan'),
 (5, 'pen', 'pen'),
 (5, 'pen_ballpoint', 'pen_ballpoint'),
 (5, 'pencil', 'pencil'),
 (3.5, 'phone', 'phone'),
 (3.5, 'receiver', 'receiver'),
 (5, 'sharpener', 'sharpener'),
 (5, 'shredder', 'cc_m_prp_bat_shredder'),
 (3.5,
  'shredder-paper',
  'shredder-paper-mod',
  'shredder-paper-chan'),
 (5,
  'watercooler',
  'cc_a_prp_bat_watercooler-mod',
  'cc_a_prp_bat_watercooler-chan'),
 (5, 'dagger', 'dagger'),
 (5, 'card', 'card'),
 (5, 'baseball', 'baseball'),
 (5, 'bird', 'bird'),
 (5, 'can', 'can'),
 (5, 'cigar', 'cigar'),
 (5, 'evil-eye', 'evil-eye'),
 (5, 'gavel', 'gavel'),
 (5, 'half-windsor', 'half-windsor'),
 (5, 'lawbook', 'lawbook'),
 (4, 'pineapple', 'pineapple'),
 (5, 'snowball', 'snowball'),
 (5, 'newspaper', 'newspaper'),
 (5, 'pink-slip', 'pink-slip'),
 (5,
  'teeth',
  'teeth-mod',
  'teeth-chan'),
 (5, 'power-tie', 'power-tie'),
 (3.5, 'spray', 'spray'),
 (3.5, 'splash', 'splash'),
 (3.5,
  'splat',
  'splat-mod',
  'splat-chan'),
 (5,
  'stun',
  '../effects/stun-mod',
  '../effects/stun-chan'),
 (3.5, 'glow', 'glow'),
 (3.5,
  'suit_explosion',
  'suit_explosion-mod',
  'suit_explosion-chan'),
 (3.5, 'suit_explosion_dust', 'dust_cloud'),
 (4, 'ripples', 'ripples'),
 (4, 'wake', 'wake'),
 (4,
  'splashdown',
  'SZ_splashdown-mod',
  'SZ_splashdown-chan'),
 (10, 'treekiller_log', 'treekiller_log'),
 (10, 'treekiller_log_center', 'treekiller_log_center'),
 (10, 'goldbar', 'goldbar'),
 (5, 'duck_hroller', 'cc_m_bat_prp_duck_hroller'),
 (5, 'dice', 'cc_m_bat_prp_dice'),
 (5, 'cup_red', 'cc_m_bat_prp_cup_red'),
 (5, 'cookie', 'cc_m_prp_bat_mouthp_cookie'),
 (3.5, 'blue_chip', 'cc_m_prp_gen_chip_blue'),
 (3.5, 'coin_bronze', 'cc_m_prp_gen_coin_bronze'),
 (3.5, 'coin_silver', 'cc_m_prp_gen_coin_silver'),
 (3.5, 'coin_gold', 'cc_m_prp_gen_coin_gold'),
)
CreampieColor = VBase4(250.0 / 255.0, 241.0 / 255.0, 24.0 / 255.0, 1.0)
PineappleColor = VBase4(250.0 / 255.0, 255.0 / 255.0, 0.0 / 255.0, 1.0)
FruitpieColor = VBase4(55.0 / 255.0, 40.0 / 255.0, 148.0 / 255.0, 1.0)
BirthdayCakeColor = VBase4(176.0 / 255.0, 149.0 / 255.0, 239.0 / 255.0, 1.0)
WeddingCakeColor = VBase4(253.0 / 255.0, 119.0 / 255.0, 220.0 / 255.0, 1.0)
SnowballColor = VBase4(1.0, 1.0, 1.0, 1.0)
Splats = {'cupcake': (0.3, WeddingCakeColor),
          'fruitpie-slice': (0.5, FruitpieColor),
          'creampie-slice': (0.5, CreampieColor),
          'birthday-cake-slice': (0.6, BirthdayCakeColor),
          'fruitpie': (0.65, FruitpieColor),
          'creampie': (0.65, CreampieColor),
          'birthday-cake': (0.7, BirthdayCakeColor),
          'wedding-cake': (0.7, WeddingCakeColor),
          'pineapple': (0.7, PineappleColor),
          'snowball': (0.7, SnowballColor)}
Buttons = ['button', 'heal-button', 'trap-button', 'lure-button', 'squirt-button', 'zap-button', 'drop-button']
Variants = ('cupcake',
            'fruitpie',
            'pineapple',
            'splat-cupcake',
            'dust',
            'kapow',
            'double-windsor',
            'splat-fruitpie-slice',
            'splat-creampie-slice',
            'splat-birthday-cake-slice',
            'splat-fruitpie',
            'splat-creampie',
            'splat-birthday-cake',
            'splat-wedding-cake',
            'splat-pineapple',
            'splat-snowball',
            'splash-from-splat',
            'heal-button',
            'trap-button',
            'lure-button',
            'squirt-button',
            'zap-button',
            'drop-button',
            'clip-on-tie',
            'lips',
            'blue-megaphone',
            'small-magnet',
            '5dollar',
            '10dollar',
            '50dollar',
            'singing',
            'suit_explosion',
            'quicksand',
            'trapdoor',
            'waterBalloon',
            'geyser',
            'ship',
            'trolley',
            'traintrack',
            'litigator_teeth',
            'lightbulb',
            'cookie',
            'calculator')


@DirectNotifyCategory()
class PropPool:
    """
    The PropPool loads props and their animations if they have them.
    """

    def __init__(self):
        self.props = {}
        self.propCache = []
        self.propStrings = {}
        self.propTypes = {}
        self.propAnimNames = {}
        self.maxPoolSize = ConfigVariableInt('prop-pool-size', 8).getValue()
        
        # Load ref's to the props enumerated above
        for p in Props:
            phase = p[0]
            propName = p[1]
            modelName = p[2]
            if len(p) >= 4:
                self.propTypes[propName] = 'actor'
                propPath = self.getPath(phase, modelName)
                self.propStrings[propName] = [propPath]
                for i in range(3, len(p)):
                    animName = p[i]
                    animPath = self.getPath(phase, animName)
                    self.propStrings[propName].append(animPath)
                    if self.propAnimNames.get(propName):
                        self.propAnimNames[propName].append(animName)
                    else:
                        self.propAnimNames[propName] = [animName]

            else:
                propPath = self.getPath(phase, modelName)
                self.propTypes[propName] = 'model'
                self.propStrings[propName] = (propPath,)

        # load the ref's for variant props
        propName = 'cupcake'
        self.propStrings[propName] = (self.getPath(3.5, 'cupcake'),)
        self.propTypes[propName] = 'model'

        propName = 'fruitpie'
        self.propStrings[propName] = (self.getPath(5, 'fruit-pie'),)
        self.propTypes[propName] = 'model'

        propName = 'pineapple'
        self.propStrings[propName] = (self.getPath(4, 'pineapple'),)
        self.propTypes[propName] = 'model'

        propName = 'double-windsor'
        self.propStrings[propName] = (self.getPath(5, 'half-windsor'),)
        self.propTypes[propName] = 'model'
        
        splatAnimFileName = self.getPath(3.5, 'splat-chan')
        for splat in list(Splats.keys()):
            propName = 'splat-' + splat
            self.propStrings[propName] = (self.getPath(3.5, 'splat-mod'), splatAnimFileName)
            self.propTypes[propName] = 'actor'

        buttonAnimFileName = self.getPath(3.5, 'button-chan')
        for button in Buttons:
            propName = button
            self.propStrings[propName] = (self.getPath(3.5, button + '-mod'), buttonAnimFileName)
            self.propTypes[propName] = 'actor'

        propName = 'splash-from-splat'
        self.propStrings[propName] = (self.getPath(3.5, 'splat-mod'), splatAnimFileName)
        self.propTypes[propName] = 'actor'
        
        propName = 'small-magnet'
        self.propStrings[propName] = (self.getPath(5, 'magnet'),)
        self.propTypes[propName] = 'model'
        
        propName = 'blue-megaphone'
        self.propStrings[propName] = (self.getPath(5, 'megaphone'),)
        self.propTypes[propName] = 'model'
        
        propName = '5dollar'
        self.propStrings[propName] = (self.getPath(5, '1dollar-bill-mod'), self.getPath(5, '1dollar-bill-chan'))
        self.propTypes[propName] = 'actor'
        
        propName = '10dollar'
        self.propStrings[propName] = (self.getPath(5, '1dollar-bill-mod'), self.getPath(5, '1dollar-bill-chan'))
        self.propTypes[propName] = 'actor'
        
        propName = '50dollar'
        self.propStrings[propName] = (self.getPath(5, '1dollar-bill-mod'), self.getPath(5, '1dollar-bill-chan'))
        self.propTypes[propName] = 'actor'
        
        propName = 'dust'
        self.propStrings[propName] = (self.getPath(5, 'dust-mod'), self.getPath(5, 'dust-chan'))
        self.propTypes[propName] = 'actor'
        
        propName = 'kapow'
        self.propStrings[propName] = (self.getPath(5, 'kapow-mod'), self.getPath(5, 'kapow-chan'))
        self.propTypes[propName] = 'actor'
        
        propName = 'ship'
        self.propStrings[propName] = ('phase_5/models/props/ship.bam',)
        self.propTypes[propName] = 'model'
        
        propName = 'trolley'
        self.propStrings[propName] = ('phase_4/models/modules/trolley_station_default',)
        self.propTypes[propName] = 'model'

        propName = 'litigator_teeth'
        self.propStrings[propName] = (self.getPath(5, 'teeth-mod'), self.getPath(5, 'teeth-chan'))
        self.propTypes[propName] = 'actor'

    def getPath(self, phase, model):
        return 'phase_%s/models/props/%s' % (phase, model)

    def makeVariant(self, name):
        if name == 'tart':
            # Scale the original pie down
            self.props[name].setScale(0.5)

        elif name == 'fruitpie':
            # Scale down the fruit pie model just a tad bit
            self.props[name].setScale(0.75)

        elif name == 'pineapple':
            # Scale down the pineapple model
            self.props[name].setScale(0.45)

        elif name == 'double-windsor':
            # Scale the half-windsor up.
            # But not by double.
            # Why would we make a double windsor 2x the size of a half windsor?
            # Lunacy.
            self.props[name].setScale(1.5)
            
        elif name[:6] == 'splat-':
            # Munge the various pie splats
            prop = self.props[name]
            scale = prop.getScale() * Splats[name[6:]][0]
            prop.setScale(scale)
            prop.setColor(Splats[name[6:]][1])
            
        elif name == 'splash-from-splat':
            # Hack up a splash for squirt attacks
            self.props[name].setColor(0.75, 0.75, 1.0, 1.0)
            
        elif name == 'clip-on-tie':
            # Yer tie's crooked
            tie = self.props[name]
            tie.getChild(0).setHpr(23.86, -16.03, 9.18)
            
        elif name == 'small-magnet':
            # Make the small magnet smaller
            # Load a red magnet texture onto it
            self.props[name].setScale(0.5)
            tex = loader.loadTexture('phase_5/maps/gag_palette_3.png')
            tex.setMinfilter(Texture.FTLinearMipmapLinear)
            tex.setMagfilter(Texture.FTLinear)
            magNode = self.props[name].find('**/magnet')
            magNode.setTexture(tex, 1)
            
        elif name == 'shredder-paper':
            # Fixing scale point on shredder-paper
            # Note: He doesn't think this is getting run;
            # 'shredder-paper' is not in the list of variants
            
            # To Clash devs: I already checked. This guy is what we call in the industry: wrong.
            paper = self.props[name]
            paper.setPosHpr(2.22, -0.95, 1.16, -48.61, 26.57, -111.51)
            paper.flattenMedium()
            
        elif name == 'lips':
            # Place lips at the origin
            lips = self.props[name]
            lips.setPos(0, 0, -3.04)
            lips.flattenMedium()
            
        elif name == 'blue-megaphone':
            # Set the texture to a blue megaphone
            tex = loader.loadTexture('phase_5/maps/gag_palette_1.png')
            tex.setMinfilter(Texture.FTLinearMipmapLinear)
            tex.setMagfilter(Texture.FTLinear)
            self.props[name].setTexture(tex, 1)
            
        elif name == '5dollar':
            # Set the texture to $5 bill
            tex = loader.loadTexture('phase_5/maps/gag_palette_4.png')
            tex.setMinfilter(Texture.FTLinearMipmapLinear)
            tex.setMagfilter(Texture.FTLinear)
            self.props[name].setTexture(tex, 1)
            
        elif name == '10dollar':
            # Set the texture to $10 bill
            tex = loader.loadTexture('phase_5/maps/gag_palette_5.png')
            tex.setMinfilter(Texture.FTLinearMipmapLinear)
            tex.setMagfilter(Texture.FTLinear)
            self.props[name].setTexture(tex, 1)
            
        elif name == '50dollar':
            # Set the texture to $50 bill
            tex = loader.loadTexture('phase_5/maps/gag_palette_6.png')
            tex.setMinfilter(Texture.FTLinearMipmapLinear)
            tex.setMagfilter(Texture.FTLinear)
            self.props[name].setTexture(tex, 1)
            
        elif name == 'singing':
            # Set the color of the head to blue
            front = self.props[name].find('**/head_front_long')
            head = self.props[name].find('**/TheHeadLong')
            earL = self.props[name].find('**/TheEarLongL')
            earR = self.props[name].find('**/TheEarLongR')
            front.setColor((0.3647, 0.4235, 0.9373, 1.0))
            head.setColor((0.3647, 0.4235, 0.9373, 1.0))
            earL.setColor((0.3647, 0.4235, 0.9373, 1.0))
            earR.setColor((0.3647, 0.4235, 0.9373, 1.0))
            
        elif name == 'dust':
            # Set the draw order of the dust clouds (cloud1 is front)
            bin = 110
            for cloudNum in range(1, 12):
                cloudName = '**/cloud' + str(cloudNum)
                cloud = self.props[name].find(cloudName)
                cloud.setBin('fixed', bin)
                bin -= 10

        elif name == 'kapow':
            # Set the draw order of the kapow
            l = self.props[name].find('**/letters')
            l.setBin('fixed', 20)
            e = self.props[name].find('**/explosion')
            e.setBin('fixed', 10)
            
        elif name == 'suit_explosion':
            # Pick random suit explosion text
            joints = ['**/joint_scale_POW', '**/joint_scale_BLAM', '**/joint_scale_BOOM']
            # Pick two joints to hide at random
            joint = random.choice(joints)
            self.props[name].find(joint).hide()
            joints.remove(joint)
            joint = random.choice(joints)
            self.props[name].find(joint).hide()
            
        elif name == 'quicksand' or name == 'trapdoor':
            # Put these things in the shadow bin to avoid flickering.
            # They are drawn behind the actual drop shadows (which are at
            # sort 0).
            p = self.props[name]
            p.setBin('shadow', -5)
            p.setDepthWrite(0)
            p.getChild(0).setPos(0, 0, ToontownGlobals.FloorOffset)
            
        elif name == 'traintrack' or name == 'traintrack2':
            # Hide the tunnels, and set the bin the same way we did trap door
            prop = self.props[name]
            prop.find('**/tunnel3').hide()
            prop.find('**/tunnel2').hide()
            prop.find('**/tracksA').setPos(0, 0, ToontownGlobals.FloorOffset)
            
        elif name == 'geyser':
            # make the geyser tflip animate
            p = self.props[name]
            s = SequenceNode('geyser')
            p.findAllMatches('**/Splash*').reparentTo(NodePath(s))
            s.loop(0)
            s.setFrameRate(12)
            p.attachNewNode(s)
            p.setTransparency(1)
            
        elif name == 'ship':
            self.props[name] = self.props[name].find('**/ship_gag')
            
        elif name == 'trolley':
            self.props[name] = self.props[name].find('**/trolley_car')

        elif name == 'litigator_teeth':
            # Set the texture to litigator blue teeth
            tex = loader.loadTexture('phase_11/maps/litigator_palette_4allc_1.png')
            tex.setMinfilter(Texture.FTLinearMipmapLinear)
            tex.setMagfilter(Texture.FTLinear)
            self.props[name].setTexture(tex, 1)

        elif name == 'lightbulb':
            # make the lightbulb tflip animate
            p = self.props[name]
            s = SequenceNode('shine')
            p.findAllMatches('**/glow*').reparentTo(NodePath(s))
            s.loop(0)
            s.setFrameRate(12)
            p.attachNewNode(s)
            p.setTransparency(1)
            p.find('**/shine').setBillboardPointEye()
            p.find('**/shine').hide()
            p.find('**/off').show()
            p.find('**/on').hide()

        elif name == 'calculator':
            p = self.props[name]
            # Paper
            p.setTwoSided(True)

    def unloadProps(self):
        for p in list(self.props.values()):
            if not isinstance(p, tuple):
                self.__delProp(p)

        self.props = {}
        self.propCache = []

    def getProp(self, name):
        return self.__getPropCopy(name)

    def __getPropCopy(self, name):
        if self.propTypes[name] == 'actor':
            # Make sure the prop is loaded
            if name not in self.props:
                prop = Actor.Actor()
                prop.loadModel(self.propStrings[name][0])
                animDict = {}
                animDict[name] = self.propStrings[name][1]
                if len(self.propStrings[name]) >= 3:
                    for i in range(2, len(self.propStrings[name])):
                        animDict[self.propAnimNames[name][i-1]] = self.propStrings[name][i]
                prop.loadAnims(animDict)
                prop.setName(name)
                prop.setBlend(frameBlend = base.wantSmoothAnims)
                self.storeProp(name, prop)
                # Modify the geometry if necessary
                if name in Variants:
                    self.makeVariant(name)
            return Actor.Actor(other=self.props[name])
        else:
            # Make sure the prop is loaded   
            if name not in self.props:
                prop = loader.loadModel(self.propStrings[name][0])
                prop.setName(name)
                self.storeProp(name, prop)
                # Modify the geometry if necessary
                if name in Variants:
                    self.makeVariant(name)
            # This must be a copyTo(), since the props may get
            # mangled and mutilated in order to get them
            # oriented the right way, etc.
            return self.props[name].copyTo(hidden)

    def storeProp(self, name, prop):
        # Determine how to store the prop in the prop cache.
        self.props[name] = prop
        self.propCache.append(prop)
        if len(self.props) > self.maxPoolSize:
            oldest = self.propCache.pop(0)
            del self.props[oldest.getName()]
            self.__delProp(oldest)
        self.notify.debug('props = %s' % self.props)
        self.notify.debug('propCache = %s' % self.propCache)

    def getPropType(self, name):
        return self.propTypes[name]

    def __delProp(self, prop):
        """__delProp(self, prop)
        This is a convenience function for deleting prop INSTANCES.
        It does NOT affect the prop dict or cache! Suckah!
        
        Tubby's note: who the hell wrote this crap it reads like it is from the 90s
        Main's note: Suckah!
        """
        if prop is None:
            self.notify.warning('tried to delete null prop!')
            return
        if isinstance(prop, Actor.Actor):
            prop.cleanup()
        else:
            prop.removeNode()

globalPropPool = PropPool()
