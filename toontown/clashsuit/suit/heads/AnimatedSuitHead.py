"""
This class was built as an extension to Suit.py
It is not intended to be used in a standalone situation.
For more information, contact Tubby.
"""

from panda3d.core import Texture
from direct.actor.Actor import Actor

from toontown.battle.BattleAvatar import BattleAvatar
from toontown.battle.visuals.VisualEffectEnums import VisualEffectEnum
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

OffsetDict = {          # Head Z value offsets for manual relocation of heads
    'chairman': -0.15,
    'ottoman': -0.15,
    'bellring': -0.15,
    'derrman': (0, -0.2, -0.1),
    'fbed': (0, 0.05, -0.05),
    'clubpres': (0, -0.1, -0.1),
    'mplayer': (0, -0.2, 0),
    'treek': (0, 0.1, -0.15),
    'ddiver': 0.1,
    'gatekeep': 0.1,
    'dopr': -0.05,
    'dold': (0, -0.05, 0.03),
    'bgh': (0, 0, 0.57),
    'pph': (0, -0.05, -0.1),
    'dl': (0, 0, -0.05),
    'shw': (0, 0.05, 0),
    'mg': (0, 0, -0.075),
}
SkelecogOffsetDict = {  # Head Z value offsets for manual relocation of skelecog heads
    'dopr': -0.05,
    'derrhand': (0, 0.05, 0),
}

HeadScaleDict = {
    'whunter': 1.3,
    'treek': 0.9,
    'mouthp': 1.1,
    'hroller': 1.17,
    'bgh': 0.95,
    'pph': 0.715,
}
SkelecogHeadScaleDict = {
    'dopa': 0.9,
}

HprDict = {

}
SkelecogHprDict = {

}

# For any cogs that should simply play the 'stun' animation once instead of looping it
NoLoopStunNormal = (
    # Sellbots
    'prethinker',
    # Cashbots
    'treek',
    # Lawbots
    'mouthp', 'whunter',
    # Bossbots
    'djockey', 'ptjockey',
    # Boardbots
    'bgh', 'pph', 'ins', 'dl', 'shw', 'dlao', 'dold', 'gatekeep',
)
NoLoopStunSkelecog = ('derrhand',)

AllSuitHeads = (  # Animations to be used by all suits. Stored as ''anim dict key : internal file animation postfix''
  ('neutral', 'neutral'),
  ('talk', 'murmur'),
  ('murmur', 'murmur'),
  ('grunt', 'grunt'),
  ('statement', 'statement'),
  ('question', 'question')
  )
AllSuitBattleHeads = (  # Animations to be used by all standard suits. This would exclude boss cogs.
  ('stun', 'stun'),
  ('neutral-lured', 'neutral-lured'),
  ('neutral-hurt', 'neutral-hurt'),
  ('death', 'death')
  )

# Begin definitions of special cog head references
AdditionalHeadAnims = {
    'chairman': (            # Chairman is included here since he is technically a suit
      ('mouth-drop', 'mouth-drop'),
      ),
    'ottoman': (            # Ottoman is included here since he is technically a suit
      ('yawn', 'yawn'),
      ),
    'bf': (
      ('scared_af', 'scared_af'),
    ),
    'sgoat': (
      ('enraged', 'enraged'),
    ),
    'caseman': (
      ('insurance', 'insurance'),
    ),
    'duckshfl': (
        ('gamble', 'gamble'),
        ('fusiondance-shot1', 'fusiondance-shot1'),
        ('fusiondance-shot2', 'fusiondance-shot2'),
        ('fusiondance-shot3', 'fusiondance-shot3'),
        ('fusiondance-shot4', 'fusiondance-shot4'),
        ('fusiondance-shot5', 'fusiondance-shot5'),
    ),
    'ddiver': (
        ('dive', 'dive'),
        ('emergeHead', 'emergeHead'),
        ('exitWater', 'exitWater'),
        ('underwaterHit', 'underwaterHit'),
    ),
    'bellring': (
        ('healing-bell', 'healing-bell'),
    ),
    'fires': (
        ('cigar-smoke', 'cigar-smoke'),
    ),
    'mslacker': (
        ('lunch-start', 'lunch-start'),
        ('lunch-loop', 'lunch-loop'),
        ('lunch-end', 'lunch-end'),
    ),
    'mplayer': (
        ('fusiondance-shot1', 'fusiondance-shot1'),
        ('fusiondance-shot2', 'fusiondance-shot2'),
        ('fusiondance-shot3', 'fusiondance-shot3'),
        ('fusiondance-shot4', 'fusiondance-shot4'),
        ('fusiondance-shot5', 'fusiondance-shot5'),
    ),
    'pcrat': (
        ('cigar-smoke', 'cigar-smoke'),
    ),
    # Chainsaw's animations are defined in ChainsawAnimatedSuitHead.py
    'psetter': (
        ('come-on', 'come-on'),
        ('overclocked', 'overclocked'),
    ),
    'hroller': (
        ('wheelspin', 'wheelspin'),
        ('fusiondance-shot1', 'fusiondance-shot1'),
        ('fusiondance-shot2', 'fusiondance-shot2'),
        ('fusiondance-shot3', 'fusiondance-shot3'),
        ('fusiondance-shot4', 'fusiondance-shot4'),
        ('fusiondance-shot5', 'fusiondance-shot5'),
        ('ace-in-the-hole', 'ace-in-the-hole'),
    ),
    'hho': (
        ('cigar-smoke', 'cigar-smoke'),
    ),
    # Begin definitions of Bosscog animations
    'l': (                   # Animation overrides for CLO head
      ('Ff_cross_arms_into', 'Ff_cross_arms_into'),
      ('Ff_cross_arms_loop', 'Ff_cross_arms_loop'),
      ('Ff_cross_arms_out', 'Ff_cross_arms_out'),
      ('Ff_trapfall', 'Ff_trapfall'),
      ('Ff_trapland', 'Ff_trapland'),
      ('hit', 'hit'),
    ),
}


@DirectNotifyCategory()
class AnimatedSuitHead(Actor):
    def __init__(self, suit, headType, headTexture=None, isBoss=False, isSkeleton=False):
        headModel = loader.loadModel(headType)
        Actor.__init__(self, headModel, None, None, flattenable=0, setFinal=1)
        self.setBlend(frameBlend=base.wantSmoothAnims)
        self.suit = suit
        self.headType = headType
        self.headTexture = headTexture
        self.isBoss = isBoss
        self.isSkeleton = isSkeleton
        self.forceHurt = False
        self.forceUnhurt = False
        self.ignoreNeutral = False
        self.createHead()
        self.setShaderAuto()

    def createHead(self):
        animDict = {}
        headName = self.headType[:-4]
        
        for anim in AllSuitHeads:                           # Standard animations, talking, neutral, etc.
            animDict[anim[0]] = headName + anim[1]
            
        if not self.isBoss:                                 # Standard Suits
            for anim in AllSuitBattleHeads:                 # Battle specific reactions.
                animDict[anim[0]] = headName + anim[1]
            
            try:
                animList = AdditionalHeadAnims[self.suit.style.name]  # Get the animation list for this suit
            except KeyError:                                # Not defined, continue on with our lives
                self.notify.debug("No such anim list for suit type: " + self.suit.style.name)
                animList = ()
        else:                                               # Boss Suits
            try:
                animList = AdditionalHeadAnims[self.suit.style.dept]  # Get the animation list for this dept's boss
            except KeyError:                                # Not defined, continue on with our lives
                self.notify.debug("No such anim list for boss type: " + self.suit.style.dept)
                animList = ()

        for anim in animList:                               # Iterate through defined animations, add to animation dictionary
            animDict[anim[0]] = headName + anim[1]

        self.loadAnims(animDict)
        if self.isBoss:
            self.reparentTo(self.suit.find('**/joint34'))
        else:
            self.reparentTo(self.suit.find('**/joint_head'))
            self.applyOffset()
        self.setTwoSided(True)
        self.loop('neutral')
        if not self.isBoss:
            self.suit.headParts.append(self)
        self.suit.specialHead = self

        if self.headTexture:
            if self.headTexture.find('**/') != -1:
                texCard = loader.loadModel('char/suit/models/cc_m_texcard_ene_skel_body_common')
                headTex = texCard.find(self.headTexture).findTexture('*')
                texCard.removeNode()
            else:
                headTex = loader.loadTexture(self.headTexture)
            headTex.setMinfilter(Texture.FTLinearMipmapLinear)
            headTex.setMagfilter(Texture.FTLinear)
            self.suit.specialHead.setTexture(headTex, 1)

    def applyOffset(self):
        # Different offset dict for skelecogs in particular
        baseDict = SkelecogOffsetDict if self.isSkeleton else OffsetDict
        offset = baseDict.get(self.suit.style.name, 0)
        # Assume it's Z if its a single number, all axises if its a tuple/list
        if type(offset) in (list, tuple):
            self.setPos(offset)
        else:
            self.setZ(offset)

        # Now apply any hpr transformations needed
        hprDict = SkelecogHprDict if self.isSkeleton else HprDict
        hpr = hprDict.get(self.suit.style.name, (0, 0, 0))
        self.setHpr(hpr)

        # Now apply any scale transformations needed
        scaleDict = SkelecogHeadScaleDict if self.isSkeleton else HeadScaleDict
        scale = scaleDict.get(self.suit.style.name, 1.0)
        self.setScale(scale)

    def loopNeutral(self):
        if not hasattr(self, 'suit'):
            return
        if self.ignoreNeutral:
            return
        # It's a boss cog, just play neutral animation
        if self.isBoss:
            self.loop('neutral')
        else:
            # If the suit is lured
            # If the suit is a battle avatar, use the lured visual effect to check since it's more accurate timing.
            # Otherwise, just check isLured.
            if isinstance(self.suit, BattleAvatar):
                for ve in self.suit.getVisualEffects():
                    if ve.neutralHeadAnim is not None:
                        self.loop(ve.neutralHeadAnim)
                        return
            elif self.suit.isLured:
                self.loop('neutral-lured')
                return

            # If we want to force the suit head to show the hurt animation (e.g. cutscenes)
            if self.forceHurt:
                self.loop('neutral-hurt')
                return

            # Now actually look into playing the right anim
            if hasattr(self.suit, 'maxHp') and not self.forceUnhurt:
                if self.suit.getHp() < int(self.suit.getMaxHp() * 0.25) and hasattr(self.suit, 'healthInitialized') and self.suit.healthInitialized:
                    self.loop('neutral-hurt')
                else:
                    self.loop('neutral')
            else:
                self.loop('neutral')

    def cleanup(self):
        if hasattr(self, 'suit'):
            del self.suit
        Actor.cleanup(self)

    def setHurtMode(self, mode):
        self.forceHurt = mode
        self.loopNeutral()

    def setForceUnhurtMode(self, mode):
        self.forceUnhurt = mode
        self.loopNeutral()

    def playStun(self):
        if not hasattr(self, 'suit'):
            return

        noLoopStunBank = NoLoopStunSkelecog if self.suit.isSkeleton else NoLoopStunNormal
        playFunc = self.play if self.suit.style.name in noLoopStunBank else self.loop
        playFunc('stun')

    def modifyZapHeadActor(self, headGeom):
        """
        Used to modify the geom of zap head actors if necessary, if they use this special head class.
        """
        return

    def makeExecutive(self, headGeom=None, isSkeleton=None):
        """
        Some subclasses may choose to alter the head when made executive.
        """
        return

    def makeUnemployed(self, headGeom=None, isSkeleton=None):
        """
        Some subclasses may choose to alter the head when made unemployed.
        """
        return
