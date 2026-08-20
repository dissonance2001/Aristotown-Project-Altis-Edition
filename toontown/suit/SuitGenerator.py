from toontown.suit import SuitDNA
from toontown.battle import SuitBattleGlobals
from toontown.nametag import NametagGlobals
from panda3d.core import TransparencyAttrib
from toontown.nametag import NametagGroup

class SuitGenerator(object):

    @staticmethod
    def generateSuit(self):
        aSize = 6.06
        bSize = 5.29
        cSize = 4.14
        dna = self.style
        self.headParts = []
        self.animatedHeadParts = []
        self.zapActorHeadParts = []
        self.headColor = None
        self.headTexture = None
        self.loseActor = None
        self.zapActor = None
        self.zapActorPowerhouse = None
        self.zapActorPowerhouseSquirt = None
        self.zapActorPowerhouseZap = None
        self.isSkeleton = 0
        self.isFired = 0
        self.isDazed = 0
        self.isSwole = 0
        self.isLured = 0
        self.isPhase3 = 0
        self.isDesperation = 0
        self.desperationMult = 0
        self.isImmune = 0
        self.isLitigationManager = 0
        self.isOverpressured = 0
        self.isShadow = 0
        self.isDead = 0
        self.isSoakImmune = 0
        self.isRevive = 0
        self.damageReduction = 0
        self.isDamageReduction = 0
        self.isChainsawPhase2 = 0
        self.isChainsawPhase3 = 0
        self.isLureImmune = 0
        self.isEnraged = 0
        self.isMarked = 0
        self.isAngry = 0
        self.isOttomanPhase2 = 0
        self.isChairmanPhase2 = 0
        self.isShielding = 0
        self.chainPos = 0
        self.isAbsorbing = 0
        self.isDamageUp = 0
        self.isSoaked = 0
        self.isFemale = 0
        self.isBuff = 0
        self.isFemaleSkelecog = 0
        self.isVirtual = 0
        self.isBookkeeping = 0
        self.headInterval = None
        self.pulseInterval = None
        self.blinkInterval = None
        self.suitColorTrack = None
        self.texRollIval = None
        self.partTracks = None
        self.extraAttack = 0
        self.extraAbility = 0
        self.damageMult = 0
        self.lureRounds = 0
        self.vulnerability = 0
        self.rageBuilding = 0
        self.powerhouseRotation = 0
        self.statusEffects = 0

        # Bossbots
        if dna.name == 'f':
            self.scale = 4.0 / cSize
            self.handColor = VBase4(0.922, 0.827, 0.812, 1)
            self.generateBody()
            #self.generateFlunky()
            self.generateHead2('flunky')
            self.generateHead2('glasses')
            self.setHeight(4.88)
        elif dna.name == 'p':
            self.scale = 3.35 / bSize
            self.handColor = VBase4(0.612, 0.565, 0.58, 1)
            self.generateBody()
            self.generateHead2('pencilpusher')
            texture = loader.loadTexture('phase_3.5/maps/pencil_pusher.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.0)
        elif dna.name == 'stg':
            self.scale = 4.0 / cSize
            self.handColor = VBase4(0.675, 0.537, 0.522, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/stooge.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.0)
        elif dna.name == 'ym':
            self.scale = 4.125 / aSize
            self.handColor = VBase4(0.918, 0.886, 0.875, 1)
            self.generateBody()
            self.generateHead2('yesman')
            texture = loader.loadTexture('phase_4/maps/yes_man.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.28)
        elif dna.name == 'psh':
            self.scale = 3.35 / bSize
            self.handColor = VBase4(0.749, 0.675, 0.635, 1)
            self.generateBody()
            self.generateHead2('pushover')
            self.setHeight(5.0)
        elif dna.name == 'enf':
            self.scale = 4.75 / aSize
            self.handColor = VBase4(0.749, 0.647, 0.518, 1)
            self.generateBody()
            self.generateHead2('yesman')
            texture = loader.loadTexture('phase_4/maps/enforcer.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.23)
        elif dna.name == 'mm':
            self.scale = 1.25 / cSize
            self.handColor = VBase4(0.945, 0.867, 0.839, 1)
            self.generateFemaleBody()
            self.generateHead2('micromanager')
            texture = loader.loadTexture('phase_3.5/maps/tutorial_suits_palette_3cmla_1.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(1.625)
        elif dna.name == 'ds':
            self.scale = 4.5 / bSize
            self.handColor = VBase4(0.643, 0.608, 0.596, 1)
            self.generateBody()
            self.generateHead2('telemarketer')
            texture = loader.loadTexture('phase_4/maps/downsizer.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.headTexture = 'DS_hat.png'
            self.generateHead2('hatjp187187')
            self.setHeight(6.08)
        elif dna.name == 'blh':
            self.scale = 5.25 / cSize
            self.handColor = VBase4(0.878, 0.733, 0.71, 1)
            self.generateBody()
            self.generateHead2('Blowhard')
            texture = loader.loadTexture('phase_3.5/maps/ttrm_t_ene_head_blowhard.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.6)
        elif dna.name == 'stck':
            self.scale = 4.75 / bSize
            self.handColor = VBase4(0.749, 0.675, 0.635, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/stickler.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.0)
        elif dna.name == 'hh':
            self.scale = 6.5 / aSize
            self.handColor = VBase4(0.902, 0.808, 0.788, 1)
            self.generateBody()
            self.generateHead2('headhunter')
            texture = loader.loadTexture('phase_3.5/maps/suit-heads_palette_3cmla_2.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.45)
        elif dna.name == 'bsht':
            self.scale = 6.25 / aSize
            self.handColor = VBase4(0.831, 0.831, 0.831, 1)
            self.generateBody()
            self.generateHead2('yesman')
            texture = loader.loadTexture('phase_14/maps/bigshot.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.45)
        elif dna.name == 'mldr':
            self.scale = 6.25 / aSize
            self.handColor = VBase4(0.659, 0.094, 0.125, 1)
            self.generateBody()
            self.generateHead2('ear01')
            self.generateHead2('head')
            self.generateHead2('ear03')
            self.generateHead2('ear04')
            self.generateHead2('ear02')
            self.generateHead2('antenna_ball')
            self.generateHead2('antenna_stick')
            self.generateHead2('eye_mouth')
            self.generateHead2('pupils')
            self.setHeight(7.45)
        elif dna.name == 'ppg':
            self.scale = 6.25 / aSize
            self.handColor = VBase4(0.761, 0.671, 0.596, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/propagandist_propagandist_tex.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.45)
        elif dna.name == 'ksp':
            self.scale = 6.75 / aSize
            self.handColor = VBase4(0.733, 0.541, 0.525, 1)
            self.generateFemaleBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/kissup_tex.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.75)
        elif dna.name == 'cr':
            self.scale = 6.75 / cSize
            self.handColor = VBase4(0.784, 0.706, 0.667, 1)
            self.generateBody()
            self.generateHead2('flunky')
            texture = loader.loadTexture('phase_4/maps/corporate-raider.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.23)
        elif dna.name == 'wnk':
            self.scale = 6.5 / bSize
            self.handColor = VBase4(0.871, 0.855, 0.816, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/whiteknight.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.1)
        elif dna.name == 'drk':
            self.scale = 6.5 / bSize
            self.handColor = VBase4(0.255, 0.247, 0.231, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/darkhorse.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.1)
        elif dna.name == 'txl':
            self.scale = 6.75 / aSize
            self.handColor = VBase4(0.882, 0.894, 0.004, 1)
            self.generateBody()
            self.generateHead2('toxicleader')
            texture = loader.loadTexture('phase_3.5/maps/skull.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.5)
        elif dna.name == 'tbc':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.827, 0.898, 0.631, 1.0)
            self.generateBody()
            self.generateHead2('bigcheese')
            texture = loader.loadTexture('phase_3.5/maps/suit-heads_palette_3cmla_1.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(9.34)
        elif dna.name == 'autocad':
            self.scale = 4.34 / aSize
            self.handColor = VBase4(1, 1, 1, 1)
            self.makeSkeletonManager()
            self.makeExecutive()
            self.setHeight(5.45)
        elif dna.name == 'clubpres':
            self.scale = 7.35 / aSize
            self.handColor = VBase4(0.608, 0.525, 0.431, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead2('skeleskull_A')
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_c_exe.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.generateHead3('autocaddie', animated=True)
            self.setHeight(9.25)
            self.isSkelecogDialogue = 1
        elif dna.name == 'derrman':
            self.scale = 4.75 / aSize
            self.handColor = VBase4(0.573, 0.384, 0.204, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('derrickman', animated=True)
            self.setHeight(6.7)
        elif dna.name == 'derrhand':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('derrickhand', animated=True)
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_derrickhand.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.85)
           # self.setTransparency(1)
        elif dna.name == 'mplayer':
            self.scale = 7.1 / aSize
            self.handColor = VBase4(1, 1, 1, 1)
            self.generateMajorPlayerBody()
            self.makeMajorPlayer()
            self.generateHead3('majorplayer', animated=True)
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_majorplayer.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(10.0)
        elif dna.name == 'mplayers':
            self.scale = 7.1 / aSize
            self.handColor = VBase4(1, 1, 1, 1)
            self.generateMajorPlayerBody()
            self.makeMajorPlayer()
            self.generateHead3('majorplayer', animated=True)
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_majorplayer.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.makeVirtual()
            self.setSuitStatusEffect('vulnerable', modifier=100)
            self.setHeight(10.0)
           # self.setTransparency(1)
        elif dna.name == 'fires':
            self.scale = 6.5 / aSize
            self.handColor = VBase4(0.894, 0.235, 0.043, 1)
            self.generateBody()
            self.makeFirestarter()
            self.generateHead3('firestarter', animated=True)
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_firestarter.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.7)
           #self.setTransparency(1)
        elif dna.name == 'fbed':
            self.scale = 5.5 / cSize
            self.handColor = VBase4(0.235, 0.149, 0.125, 1)
            self.generateBody()
            self.makeFeatherbedder()
            self.generateHead3('featherbedder', animated=True)
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_featherbedder.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.7)
            #self.setTransparency(1)
        elif dna.name == 'choreo':
            self.scale = 7.05 / aSize
            self.handColor = VBase4(0.608, 0.525, 0.431, 1)
            self.generateMajorPlayerBody()
            self.makeVideographer2()
            self.generateHead3('headhoncho', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_headhoncho_choreo.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(10.15)
        elif dna.name == 'chainsaw':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.generateBody()
            self.makeChainsaw()
            self.generateHead3('chainsaw', animated=True)
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_chainsaw.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(10.2)
           # self.setTransparency(1)
            self.setChainsawTexRoll(.5)
        elif dna.name == 'phouse':
            self.scale = 5.0 / aSize
            self.handColor = VBase4(0.686, 0.569, 0.439, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('circuitbreaker', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_circuitbreaker2.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.0)
            #self.setSuitStatusEffect('toleranceBuilding')
        elif dna.name == 'bkeeper':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.784, 0.745, 0.69, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('paperhands', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_stockbroker.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(9.2)
           # self.setTransparency(1)
        elif dna.name == 'wtapper':
            self.scale = 7.2 / aSize
            self.handColor = VBase4(0.682, 0.588, 0.482, 1)
            self.generateFemaleBody()
            self.makeExecutive()
            self.generateHead3('mouthpiece', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_wiretapper.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(9.5)
           # self.setTransparency(1)
        elif dna.name == 'ambass':
            self.scale = 7.3 / aSize
            self.handColor = VBase4(0.682, 0.588, 0.482, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('prethinker', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_ambassador.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(9.1)
           # self.setTransparency(1)
            self.setSuitStatusEffect('ambassadorOverconfidence', turns=5)

        # Lawbots
        elif dna.name == 'bf':
            self.scale = 4.0 / cSize
            self.handColor = VBase4(0.792, 0.78, 0.878, 1)
            self.generateBody()
            self.generateHead3('bottom_feeder', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_bottom_feeder.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(4.81)
        elif dna.name == 'b':
            self.scale = 4.375 / bSize
            self.handColor = VBase4(1, 1, 1, 1)
            self.generateBody()
            self.generateHead3('bloodsucker', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_bloodsucker.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.17)
        elif dna.name == 'bsd':
            self.scale = 4.0 / cSize
            self.handColor = VBase4(0.675, 0.675, 0.753, 1)
            self.generateBody()
            self.generateHead2('backseat')
            self.setHeight(5.5)
        elif dna.name == 'pf':
            self.scale = 4.35 / bSize
            self.handColor = VBase4(0.533, 0.561, 0.725, 1)
            self.generateBody()
            self.generateHead3('pettifogger', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_pettifogger.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.17)
        elif dna.name == 'dt':
            self.scale = 4.25 / aSize
            self.handColor = VBase4(0.714, 0.714, 0.808, 1)
            self.generateBody()
            self.generateHead3('doubletalker', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_doubletalker.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.63)
        elif dna.name == 'dcr':
            self.scale = 4.0 / aSize
            self.handColor = VBase4(0.871, 0.871, 0.906, 1)
            self.generateBody()
            self.generateHead2('doublecross')
            self.setHeight(5.5)
        elif dna.name == 'cv':
            self.scale = 4.5 / aSize
            self.handColor = VBase4(0.318, 0.333, 0.431, 1)
            self.generateBody()
            self.generateHead3('conveyancer', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_conveyancer.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.generateHead2('conveyancer_belt')
            self.setHeight(6.25)
        elif dna.name == 'ac':
            self.scale = 4.35 / bSize
            self.handColor = VBase4(0.714, 0.714, 0.808, 1)
            self.generateBody()
            self.generateHead3('ambulance_chaser', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_ambulance_chaser.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.39)
        elif dna.name == 'nn':
            self.scale = 4.5 / cSize
            self.handColor = VBase4(0.255, 0.318, 0.549, 1)
            self.generateFemaleBody()
            self.generateHead3('needlenose', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_needlenose.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.41)
        elif dna.name == 'bs':
            self.scale = 5.05 / bSize
            self.handColor = VBase4(0.647, 0.639, 0.788, 1)
            self.generateBody()
            self.generateHead3('backstabber', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_backstabber.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.95)
        elif dna.name == 'dcw':
            self.scale = 5.05 / aSize
            self.handColor = VBase4(0.984, 0.988, 0.988, 1)
            self.generateBody()
            self.generateHead2('backstabber')
            texture = loader.loadTexture('phase_3.5/maps/doctorwhite.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.95)
        elif dna.name == 'bck':
            self.scale = 5.05 / aSize
            self.handColor = VBase4(0.596, 0.604, 0.631, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/back_burner.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.95)
        elif dna.name == 'ad':
            self.scale = 5.25 / cSize
            self.handColor = VBase4(0.098, 0.098, 0.153, 1)
            self.generateBody()
            self.generateHead3('advocate', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_advocate.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.56)
        elif dna.name == 'sd':
            self.scale = 5.65 / bSize
            self.handColor = VBase4(0.678, 0.91, 0.808, 1)
            self.generateBody()
            self.generateHead3('spin_doctor', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_spin_doctor.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.9)
        elif dna.name == 'surg':
            self.scale = 5.65 / bSize
            self.handColor = VBase4(0.659, 0.757, 0.984, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/surgeongeneral_tex.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.generateHead2('scopejp187187')
            self.generateHead2('bandjp187187')
            self.setHeight(7.9)
        elif dna.name == 'rat':
            self.scale = 5.65 / bSize
            self.handColor = VBase4(0.62, 0.62, 0.706, 1)
            self.generateBody()
            self.generateHead2('ratifier')
            self.generateHead2('rat_glasses')
            self.setHeight(7.25)
        elif dna.name == 'sh':
            self.scale = 5.65 / bSize
            self.handColor = VBase4(0.647, 0.639, 0.788, 1)
            self.generateFemaleBody()
            self.generateHead3('shyster', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_shyster.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.95)
        elif dna.name == 'le':
            self.scale = 6.5 / aSize
            self.handColor = VBase4(0.659, 0.647, 0.804, 1.0)
            self.generateBody()
            self.generateHead3('legal_eagle', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_legal_eagle.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.45)
        elif dna.name == 'br':
            self.scale = 6.75 / aSize
            self.handColor = VBase4(0.784, 0.816, 0.847, 1)
            self.generateBody()
            self.generateHead3('barrister', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_barrister.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.75)
        elif dna.name == 'magi':
            self.scale = 6.75 / aSize
            self.handColor = VBase4(0.639, 0.639, 0.729, 1)
            self.generateBody()
            self.generateHead2('magister')
            self.setHeight(8.25)
        elif dna.name == 'bw':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.573, 0.557, 0.761, 1)
            self.generateBody()
            self.generateHead3('bigwig', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_big_wig.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.69)
        elif dna.name == 'bf2':
            self.scale = 4.0 / cSize
            self.handColor = VBase4(0.792, 0.78, 0.878, 1)
            self.generateBody()
            self.generateHead2('tightwad')
            texture = loader.loadTexture('phase_3.5/maps/bottom-feeder.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(4.81)
        elif dna.name == 'b2':
            self.scale = 4.375 / bSize
            self.handColor = VBase4(1, 1, 1, 1)
            self.generateBody()
            self.generateHead2('movershaker')
            texture = loader.loadTexture('phase_4/maps/blood-sucker.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.17)
        elif dna.name == 'dt2':
            self.scale = 4.25 / aSize
            self.handColor = VBase4(0.714, 0.714, 0.808, 1)
            self.generateBody()
            self.generateHead2('twoface')
            texture = loader.loadTexture('phase_4/maps/double-talker.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.63)
        elif dna.name == 'ac2':
            self.scale = 4.35 / bSize
            self.handColor = VBase4(0.714, 0.714, 0.808, 1)
            self.generateBody()
            self.generateHead2('ambulancechaser')
            texture = loader.loadTexture('phase_4/maps/suit-heads_palette_3cmla_1.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.39)
        elif dna.name == 'bs2':
            self.scale = 5.05 / aSize
            self.handColor = VBase4(0.616, 0.533, 0.761, 1)
            self.generateBody()
            self.generateHead2('backstabber')
            texture = loader.loadTexture('phase_4/maps/suit-heads_palette_3cmla_1.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.95)
        elif dna.name == 'sd2':
            self.scale = 5.65 / bSize
            self.handColor = VBase4(0.62, 0.914, 0.784, 1)
            self.generateBody()
            self.generateHead2('telemarketer')
            texture = loader.loadTexture('phase_4/maps/spin_doctor.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.generateHead2('scopejp187187')
            self.generateHead2('bandjp187187')
            self.setHeight(7.9)
        elif dna.name == 'le2':
            self.scale = 6.5 / aSize
            self.handColor = VBase4(0.25, 0.25, 0.5, 1.0)
            self.generateBody()
            self.generateHead2('legaleagle')
            texture = loader.loadTexture('phase_4/maps/suit-heads_palette_3cmla_2.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.45)
        elif dna.name == 'bw2':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.573, 0.557, 0.761, 1)
            self.generateBody()
            self.generateHead2('bigwig')
            texture = loader.loadTexture('phase_4/maps/suit-heads_palette_3cmla_2.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.69)
        elif dna.name == 'test':
            self.scale = 7.2 / aSize
            self.handColor = VBase4(0.69, 0.678, 0.765, 1)
            self.generateFemaleBody()
            self.generateHead3('clo', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_clo.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.makeExecutive()
            self.setHeight(9.25)
        elif dna.name == 'whistleb':
            self.scale = 5.0 / aSize
            self.handColor = VBase4(0.722, 0.757, 0.784, 1)
            self.generateFemaleBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/whistleblower.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.6)
        elif dna.name == 'clerk':
            self.scale = 7.25 / bSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.makeSkeletonManager()
            self.makeExecutive()
            self.setHeight(8.75)
        elif dna.name == 'arbit':
            self.scale = 7.2 / aSize
            self.handColor = VBase4(0.69, 0.678, 0.765, 1)
            self.generateFemaleBody()
            self.generateHead3('clo', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_clo.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.makeExecutive()
            self.setHeight(9.25)
        elif dna.name == 'judy':
            self.scale = 4.5 / cSize
            self.handColor = VBase4(0.361, 0.435, 0.694, 1)
            self.generateFemaleBody()
            self.makeExecutive()
            self.generateHead3('judy', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_judy.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.41)
        elif dna.name == 'mouthp':
            self.scale = 4.77 / bSize
            self.handColor = VBase4(0.42, 0.502, 0.62, 1)
            self.generateFemaleBody()
            self.makeExecutive()
            self.generateHead3('mouthpiece', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_mouthpiece.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.7)
        elif dna.name == 'rainmake':
            self.scale = 5.0 / bSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.generateLongcoatBody()
            self.generateHead3('rainmaker', animated=True)
            self.setHeight(6.7)
           # self.setTransparency(1)
        elif dna.name == 'whunter':
            self.scale = 6.2 / aSize
            self.handColor = VBase4(0.49, 0.494, 0.675, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('witchhunter', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_witchhunter.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.0)
          #  self.setTransparency(1)
        elif dna.name == 'erclaim':
            self.scale = 6.5 / bSize
            self.handColor = VBase4(1, 1, 1, 1)
            self.generateBody()
            self.makeCountErclaim()
            self.generateHead3('counterfit', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_counterclaim1.png')
            from panda3d.core import TextureAttrib

            for headPart in self.headParts:
                
                gn_path = headPart.find("**/+GeomNode")

                if not gn_path.isEmpty():
                    geomNode = gn_path.node()

                    for i in range(geomNode.getNumGeoms()):
                        state = geomNode.getGeomState(i)
                        tex_attr = state.getAttrib(TextureAttrib)

                        if tex_attr:
                            for stage in tex_attr.getOnStages():
                                current_tex = tex_attr.getOnTexture(stage)
                                if current_tex and "ttcc_ene_counterfit" in current_tex.getFilename().getBasename():
                                    new_state = state.setAttrib(tex_attr.addOnStage(stage, texture))
                                    geomNode.setGeomState(i, new_state)
            self.setHeight(9.25)
           # self.setTransparency(1)
        elif dna.name == 'redd':
            self.scale = 6.375 / bSize
            self.handColor = VBase4(0.173, 0.173, 0.173, 1)
            self.generateBody()
            self.makeRedd()
            self.generateHead3('redd', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_redd.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.37)
           # self.setTransparency(1)
        elif dna.name == 'wsi':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.makeSkeletonManager()
            self.makeExecutive()
            self.setHeight(8.69)
        elif dna.name == 'sgoat':
            self.scale = 5.325 / bSize
            self.handColor = VBase4(0.486, 0.522, 0.686, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('scapegoat', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_scapegoat.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.5)
            #self.makeShielding()
            self.setSuitStatusEffect('rageBuilding')
        elif dna.name == 'caseman':
            self.scale = 6.75 / aSize
            self.handColor = VBase4(0.294, 0.208, 0.149, 1)
            self.generateBody()
            self.makeExecutive()
            self.makeLitigationManager()
            self.generateHead3('casemanager', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_casemanager.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.25)
           # self.setTransparency(1)
        elif dna.name == 'stenog':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.322, 0.369, 0.525, 1)
            self.generateFemaleBody()
            self.makeExecutive()
            self.makeLitigationManager()
            self.generateHead3('stenographer', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_stenographer.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(10.0)
          #  self.setTransparency(1)
        elif dna.name == 'lgator':
            self.scale = 7.25 / aSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.generateBody()
            self.makeExecutive()
            self.makeLitigationManager()
            self.generateHead3('litigator', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_litigator.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
           # self.setTransparency(1)
            self.setHeight(9.25)

        # Cashbots
        elif dna.name == 'sc':
            self.scale = 2.5 / cSize
            self.handColor = VBase4(0.294, 0.655, 0.871, 1.0)
            self.generateBody()
            self.generateHead2('coldcaller')
            self.setHeight(3.25)
        elif dna.name == 'pp':
            self.scale = 3.55 / aSize
            self.handColor = VBase4(0.847, 0.435, 0.408, 1.0)
            self.generateBody()
            self.generateHead2('pennypincher')
            texture = loader.loadTexture('phase_4/maps/suit-heads_palette_3cmla_3.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.26)
        elif dna.name == 'qc':
            self.scale = 3.55 / aSize
            self.handColor = VBase4(0.839, 0.765, 0.576, 1.0)
            self.generateBody()
            self.generateHead2('pennypincher')
            texture = loader.loadTexture('phase_4/maps/quarter_catcher.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.26)
        elif dna.name == 'nb':
            self.scale = 3.55 / aSize
            self.handColor = VBase4(0.612, 0.627, 0.698, 1.0)
            self.generateBody()
            self.generateHead2('pennypincher')
            texture = loader.loadTexture('phase_4/maps/nickel_nabber.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.26)
        elif dna.name == 'shy':
            self.scale = 4.0 / bSize
            self.handColor = VBase4(0.741, 0.773, 0.741, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/shylock.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.5)
        elif dna.name == 'tw':
            self.scale = 4.5 / cSize
            self.handColor = VBase4(0.796, 0.91, 0.878, 1.0)
            self.generateBody()
            self.generateHead2('tightwad')
            self.setHeight(5.41)
        elif dna.name == 'trs':
            self.scale = 4.5 / aSize
            self.handColor = VBase4(0.592, 0.663, 0.627, 1)
            self.generateBody()
            self.generateHead2('yesman')
            texture = loader.loadTexture('phase_3.5/maps/cheapskate.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.25)
        elif dna.name == 'pwn':
            self.scale = 4.5 / aSize
            self.handColor = VBase4(0.773, 0.843, 0.82, 1)
            self.generateBody()
            self.generateHead2('pawnbroker')
            self.setHeight(6.0)
        elif dna.name == 'bc':
            self.scale = 4.4 / bSize
            self.handColor = VBase4(0.671, 0.722, 0.682, 1.0)
            self.generateBody()
            self.generateHead2('beancounter')
            self.setHeight(5.95)
        elif dna.name == 'nc':
            self.scale = 5.25 / aSize
            self.handColor = VBase4(0.761, 0.953, 0.906, 1)
            self.generateFemaleBody()
            self.generateHead2('numbercruncher')
            texture = loader.loadTexture('phase_3.5/maps/number_cruncher.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.22)
        elif dna.name == 'cow':
            self.scale = 5.4 / cSize
            self.handColor = VBase4(0.929, 0.976, 0.918, 1)
            self.generateFemaleBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/cashCow.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.2)
        elif dna.name == 'brck':
            self.scale = 5.4 / cSize
            self.handColor = VBase4(0.89, 0.804, 0.49, 1)
            self.generateBody()
            self.generateHead2('goldbricks')
            self.setHeight(7.0)
        elif dna.name == 'mb':
            self.scale = 5.7 / cSize
            self.handColor = VBase4(0.831, 0.859, 0.847, 1)
            self.generateBody()
            self.generateHead2('moneybags')
            texture = loader.loadTexture('phase_3.5/maps/tutorial_suits_palette_3cmla_1.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.2)
        elif dna.name == 'aud':
            self.scale = 5.4 / cSize
            self.handColor = VBase4(0.514, 0.631, 0.522, 1)
            self.generateFemaleBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/bookkeeper_BookkeeperFinal.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.2)
        elif dna.name == 'ls':
            self.scale = 6.5 / bSize
            self.handColor = VBase4(0.655, 0.71, 0.694, 1)
            self.generateBody()
            self.generateHead2('loanshark')
            texture = loader.loadTexture('phase_3.5/maps/suit-heads_palette_3cmla_2.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.58)
        elif dna.name == 'fct':
            self.scale = 7.0 / cSize
            self.handColor = VBase4(0.776, 0.831, 0.812, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/fatcat.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(9.5)
        elif dna.name == 'gld':
            self.scale = 6.5 / bSize
            self.handColor = VBase4(0.922, 0.682, 0.149, 1)
            self.generateFemaleBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/GoldenGoose_GoldenGooseFinal.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.5)
        elif dna.name == 'bfh':
            self.scale = 7.5 / cSize
            self.handColor = VBase4(0.659, 0, 0, 1)
            self.generateFemaleBody()
            self.generateHead2('bigfish')
            self.setHeight(10.7)
        elif dna.name == 'timer':
            self.scale = 6.5 / aSize
            self.handColor = VBase4(0.318, 0.318, 0.318, 1)
            self.generateBody()
            self.generateHead2('overtime')
            self.setHeight(8.0)
        elif dna.name == 'rb':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.902, 0.949, 0.933, 1)
            self.generateBody()
            self.generateHead2('yesman')
            texture = loader.loadTexture('phase_4/maps/robber-baron.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.95)
        elif dna.name == 'ovt':
            self.scale = 7.25 / bSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.makeSkeletonManager()
            self.setHeight(8.75)
        elif dna.name == 'supervis':
            self.scale = 7.35 / cSize
            self.handColor = VBase4(0.286, 0.29, 0.286, 1)
            self.makeSkeletonManager()
            self.makeExecutive()
            self.setHeight(10.25)
        elif dna.name == 'duckshfl':
            self.scale = 4.75 / bSize
            self.handColor = VBase4(0.714, 0.118, 0.055, 1)
            self.generateBody()
            self.makeDuckShuffler()
            self.generateHead3('duckshuffler', animated=True)
            self.setHeight(6.6)
        elif dna.name == 'treek':
            self.scale = 5.3 / cSize
            self.handColor = VBase4(0.647, 0.796, 0.627, 1)
            self.generateBody()
            self.makeTreekiller()
            self.generateHead3('treekiller', animated=True)
            self.setHeight(6.7)
        elif dna.name == 'payman':
            self.scale = 4.5 / aSize
            self.handColor = VBase4(0.8, 0.776, 0.741, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('plutocrat', animated=True)
            texture = loader.loadTexture('phase_10/maps/ttcc_ene_plutocrat.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.0)
        elif dna.name == 'bookkeep':
            self.scale = 5.75 / cSize
            self.handColor = VBase4(0.251, 0.361, 0.325, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('chairman', animated=True)
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_bookkeeper.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.75)
         #   self.setTransparency(1)
        elif dna.name == 'racket':
            self.scale = 7.2 / aSize
            self.handColor = VBase4(0.169, 0.169, 0.169, 1)
            self.generateCounterFitBody()
            self.generateHead3('magnate', animated=True)
            #self.makeExecutive()
            self.makeRacketeer()
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_racket_cash.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
                headPart.setTwoSided(True)
            self.setHeight(9.2)
            #self.makeCollectCall(0)
            self.setSuitStatusEffect('protectionRacket')
        elif dna.name == 'liquidr':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.29, 0.424, 0.376, 1)
            self.generateFemaleBody()
            self.makeExecutive()
            self.makeLitigationManager()
            self.generateHead3('gatekeeper', animated=True)
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_gatekeeper_hw.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(10.0)
        elif dna.name == 'treasure':
            self.scale = 7.2 / aSize
            self.handColor = VBase4(0.408, 0.58, 0.529, 1)
            self.generateBody()
            self.makeExecutive()
            self.makeLitigationManager()
            self.generateHead3('litigator', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_treasurer.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
          #  self.setTransparency(1)
            self.setHeight(9.4)
        elif dna.name == 'charon':
            self.scale = 5.7 / aSize
            self.handColor = VBase4(0.294, 0.651, 0.871, 1)
            self.makeSkeletonManager()
            self.setHeight(6.7)
        elif dna.name == 'nix':
            self.scale = 5.8 / bSize
            self.handColor = VBase4(0.294, 0.651, 0.871, 1)
            self.makeSkeletonManager()
            self.setHeight(6.8)
        elif dna.name == 'hydra':
            self.scale = 6.3 / cSize
            self.handColor = VBase4(0.294, 0.651, 0.871, 1)
            self.makeSkeletonManager()
            self.setHeight(8.0)
        elif dna.name == 'styx':
            self.scale = 5.4 / cSize
            self.handColor = VBase4(0.294, 0.651, 0.871, 1)
            self.makeSkeletonManager()
            self.setHeight(6.8)
        elif dna.name == 'kerberos':
            self.scale = 6.9 / aSize
            self.handColor = VBase4(0.294, 0.651, 0.871, 1)
            self.makeSkeletonManager()
            self.setHeight(8.5)
        elif dna.name == 'pcrat':
            self.scale = 3.2 / cSize
            self.handColor = VBase4(0.702, 0.776, 0.788, 1)
            self.generateBody()
            self.makePlutocrat()
            self.generateHead3('plutocrat', animated=True)
            self.setHeight(4.5)
         #   self.setTransparency(1)
        elif dna.name == 'hroller':
            self.scale = 7.1 / aSize
            self.handColor = VBase4(1, 1, 1, 1)
            self.generateHighRollerBodyWhite()
            self.generateHead3('highroller', animated=True)
            self.setHeight(10.0)
           # self.setTransparency(1)
           # self.makeImmortal()
        elif dna.name == 'erfit':
            self.scale = 7.35 / aSize
            self.handColor = VBase4(1, 1, 1, 1.0)
            self.generateCounterFitBody()
            self.makeCountErfit()
            self.generateHead3('counterfit', animated=True)
            self.setHeight(10.25)
        elif dna.name == 'hrollers':
            self.scale = 7.1 / aSize
            self.handColor = VBase4(1, 1, 1, 1)
            self.generateHighRollerBodyWhite()
            self.generateHead3('highroller', animated=True)
            self.makeVirtual()
            # self.makeDamageReduction()
            # self.setDamageReduction(10)
            self.setSuitStatusEffect('refractionBarrier', modifier=10)
            self.setHeight(10.0)
          #  self.setTransparency(1)
        elif dna.name == 'hroller2':
            self.scale = 7.1 / aSize
            self.handColor = VBase4(1, 1, 1, 1)
            self.generateHighRollerBody()
            self.makeHighRoller()
            self.generateHead3('highroller', animated=True)
            self.setHeight(10.0)
            self.setSuitStatusEffect('silhouetteImmune', modifier=10)
            self.setSuitStatusEffect('silhouetteShielding', modifier=10)
           # self.setTransparency(1)

        # Sellbots
        elif dna.name == 'cc':
            self.scale = 3.5 / cSize
            self.handColor = VBase4(0.075, 0.227, 0.867, 1)
            self.generateBody()
            self.generateHead2('coldcaller')
            texture = loader.loadTexture('phase_3.5/maps/tutorial_suits_palette_3cmla_69.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(4.63)
        elif dna.name == 'tm':
            self.scale = 3.75 / bSize
            self.handColor = VBase4(0.965, 0.859, 0.831, 1)
            self.generateBody()
            self.generateHead2('telemarketer')
            texture = loader.loadTexture('phase_4/maps/telemarketer.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.24)
        elif dna.name == 'sbg':
            self.scale = 4.25 / cSize
            self.handColor = VBase4(0.718, 0.667, 0.624, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/sandbagger.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.5)
        elif dna.name == 'nd':
            self.scale = 4.35 / aSize
            self.handColor = VBase4(0.804, 0.741, 0.839, 1)
            self.generateFemaleBody()
            self.generateHead2('numbercruncher')
            texture = loader.loadTexture('phase_3.5/maps/name-dropper.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.98)
        elif dna.name == 'dc':
            self.scale = 4.75 / aSize
            self.handColor = VBase4(0.824, 0.788, 0.847, 1)
            self.generateBody()
            self.generateHead2('twoface')
            texture = loader.loadTexture('phase_3.5/maps/consig.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.2)
        elif dna.name == 'gh':
            self.scale = 4.75 / cSize
            self.handColor = VBase4(0.918, 0.886, 0.875, 1)
            self.generateBody()
            self.generateHead2('gladhander')
            texture = loader.loadTexture('phase_3.5/maps/tutorial_suits_palette_3cmla_1.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.4)
        elif dna.name == 'mad':
            self.scale = 4.75 / cSize
            self.handColor = VBase4(0.918, 0.886, 0.875, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/madhander_madhander.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.4)
        elif dna.name == 'ms':
            self.scale = 4.75 / bSize
            self.handColor = VBase4(0.965, 0.859, 0.831, 1)
            self.generateBody()
            self.generateHead2('movershaker')
            texture = loader.loadTexture('phase_4/maps/mover_shaker.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.7)
        elif dna.name == 'lvw':
            self.scale = 5.0 / aSize
            self.handColor = VBase4(0.843, 0.133, 0.169, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/livewire.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.7)
        elif dna.name == 'bam':
            self.scale = 4.75 / bSize
            self.handColor = VBase4(0.682, 0.737, 0.533, 1)
            self.generateBody()
            self.generateHead2('bamboozler')
            self.setHeight(6.7)
        elif dna.name == 'tf':
            self.scale = 5.25 / aSize
            self.handColor = VBase4(0.965, 0.859, 0.831, 1)
            self.generateBody()
            self.generateHead2('twoface')
            texture = loader.loadTexture('phase_4/maps/twoface.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.95)
        elif dna.name == 'fcs':
            self.scale = 5.5 / aSize
            self.handColor = VBase4(0.302, 0.227, 0.357, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/forecaster.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.1)
        elif dna.name == 'ppl':
            self.scale = 5.75 / aSize
            self.handColor = VBase4(0.698, 0.635, 0.737, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/peoplepleaser.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.61)
        elif dna.name == 'm':
            self.scale = 5.75 / aSize
            self.handColor = VBase4(0.918, 0.808, 0.871, 1)
            self.generateFemaleBody()
            self.generateHead2('twoface')
            texture = loader.loadTexture('phase_4/maps/mingler2.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.61)
        elif dna.name == 'cnd':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.992, 0.851, 0.757, 1)
            self.generateBody()
            self.generateHead2('yesman')
            texture = loader.loadTexture('phase_4/maps/mr_hollywood1.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.generateHead2('shades')
            self.setHeight(8.95)
        elif dna.name == 'std':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(1, 0.973, 0.969, 1)
            self.generateBody()
            self.generateHead2('yesman')
            texture = loader.loadTexture('phase_3.5/maps/stuntdouble.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.generateHead2('shades')
            self.setHeight(8.95)
        elif dna.name == 'mh':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.918, 0.886, 0.875, 1)
            self.generateBody()
            self.generateHead2('yesman')
            texture = loader.loadTexture('phase_4/maps/mr_hollywood.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.generateHead2('shades')
            self.setHeight(8.95)
        elif dna.name == 'watchm':
            self.scale = 6.0 / aSize
            self.handColor = VBase4(0.125, 0.125, 0.125, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead2('overtime')
            texture = loader.loadTexture('phase_3.5/maps/ttoff_t_ene_overtime_palette_4amlc_1.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.9)
        elif dna.name == 'foreman':
            self.scale = 7.35 / aSize
            self.handColor = VBase4(1, 0.486, 0, 1)
            self.makeSkeletonManager()
            self.makeExecutive()
            self.setHeight(9.25)
        elif dna.name == 'dopr':
            self.scale = 6.25 / cSize
            self.handColor = VBase4(1, 1, 1, 1.0)
            self.makeSkeletonManager()
            self.makeExecutive()
            self.setHeight(8.25)
        elif dna.name == 'dopa':
            self.scale = 7.25 / cSize
            self.handColor = VBase4(1, 1, 1, 1.0)
            self.makeSkeletonManager()
            self.makeExecutive()
            self.setHeight(10.5)
        elif dna.name == 'bellring':
            self.scale = 4.75 / bSize
            self.handColor = VBase4(0.886, 0.749, 0.451, 1)
            self.generateHighCollarBody()
            self.makeBellringer()
            self.generateHead3('bellringer', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_bellringer.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.7)
        elif dna.name == 'mh2':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.918, 0.886, 0.875, 1)
            self.generateMajorPlayerBody()
            self.makeExecutive()
            self.generateHead2('yesman')
            texture = loader.loadTexture('phase_4/maps/mr_hollywood.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.generateHead2('shades')
            self.setHeight(8.95)
        elif dna.name == 'cnd2':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.992, 0.851, 0.757, 1)
            self.generateMajorPlayerBody()
            self.makeExecutive()
            self.generateHead2('yesman')
            texture = loader.loadTexture('phase_4/maps/mr_hollywood1.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.generateHead2('shades')
            self.setHeight(8.95)
        elif dna.name == 'std2':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(1, 0.973, 0.969, 1)
            self.generateMajorPlayerBody()
            self.makeExecutive()
            self.generateHead2('yesman')
            texture = loader.loadTexture('phase_3.5/maps/stuntdouble.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.generateHead2('shades')
            self.setHeight(8.95)
        elif dna.name == 'prethink':
            self.scale = 3.75 / bSize
            self.handColor = VBase4(0.682, 0.604, 0.765, 1)
            self.generateBody()
            self.generateHead3('prethinker', animated=True)
            self.makePrethinker()
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_prethinker.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.2)
        elif dna.name == 'mslacker':
            self.scale = 4.4 / cSize
            self.handColor = VBase4(0.553, 0.404, 0.537, 1)
            self.generateBody()
            self.makeMultislacker()
            self.generateHead3('multislacker', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_multislacker.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.7)
           # self.setTransparency(1)
        elif dna.name == 'cinema':
            self.scale = 7.05 / aSize
            self.handColor = VBase4(0.647, 0.486, 0.663, 1)
            self.generateMajorPlayerBody()
            self.makeVideographer2()
            self.generateHead3('headhoncho', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_headhoncho_cinema.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(10.15)
        elif dna.name == 'radiog':
            self.scale = 7.1 / aSize
            self.handColor = VBase4(0.612, 0.376, 0.608, 1)
            self.generateMajorPlayerBody()
            self.makeExecutive()
            self.generateHead2('skeleskull_A')
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_s_exe.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.generateHead3('dopa', animated=True)
            self.setHeight(9.6)
          #  self.setTransparency(1)
        elif dna.name == 'hustle':
            self.scale = 5.0 / aSize
            self.handColor = VBase4(0.486, 0.447, 0.42, 1)
            self.generateBody()
            self.generateHead3('dola', animated=True)
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_dola.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.makeExecutive()
            self.setHeight(7.25)
          #  self.setTransparency(1)
        elif dna.name == 'ubuster':
            self.scale = 7.1 / aSize
            self.handColor = VBase4(0.604, 0.463, 0.62, 1)
            self.generateBody()
            self.generateHead2('skeleskull_A')
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_s_exe.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.generateHead3('dopr', animated=True)
            self.makeExecutive()
            self.setHeight(8.9)
            self.setTransparency(1)
        elif dna.name == 'safesupervis':
            self.scale = 7.3 / aSize
            self.handColor = VBase4(0.286, 0.176, 0.286, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('firestarter', animated=True)
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_firestarter_2.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(10.3)
           # self.setTransparency(1)
        elif dna.name == 'psetter':
            self.scale = 5.65 / bSize
            self.handColor = VBase4(0.369, 0.369, 0.369, 1)
            self.generatePaceBody()
            self.makePacesetter()
            self.generateHead3('pacesetter', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_pacesetter.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.1)

        # Boardbots
        elif dna.name == 'bgh':
            self.scale = 4.0 / cSize
            self.handColor = VBase4(0.427, 0.608, 0.631, 1)
            self.generateBody()
            self.generateHead3('bagholder', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_bagholder.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.45)
        elif dna.name == 'ca':
            self.scale = 4.0 / cSize
            self.handColor = VBase4(0.439, 0.431, 0.435, 1)
            self.generateBody()
            self.generateHead2('flunky')
            texture = loader.loadTexture('phase_3.5/maps/conartist.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.generateHead2('beret')
            self.setHeight(4.88)
        elif dna.name == 'pph':
            self.scale = 3.75 / bSize
            self.handColor = VBase4(1, 1, 1, 1)
            self.generateBody()
            self.generateHead3('paperhands', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_paperhands.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.24)
        elif dna.name == 'cn':
            self.scale = 4.0 / bSize
            self.handColor = VBase4(1, 1, 1, 1)
            self.generateBody()
            self.generateHead2('connoisseur_hat')
            self.generateHead2('connoisseur_monocle')
            self.generateHead2('connoisseur_head')
            self.setHeight(5.55)
        elif dna.name == 'ins':
            self.scale = 4.34 / bSize
            self.handColor = VBase4(0.031, 0.035, 0.035, 1)
            self.generateHighCollarBody()
            self.generateHead3('insider', animated=True)
            self.setHeight(5.8)
        elif dna.name == 'sw':
            self.scale = 4.34 / aSize
            self.handColor = VBase4(0.612, 0.635, 0.62, 1)
            self.generateBody()
            self.generateHead2('pennypincher')
            texture = loader.loadTexture('phase_3.5/maps/swindler.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.0)
        elif dna.name == 'mdm':
            self.scale = 5.0 / aSize
            self.handColor = VBase4(0.459, 0.447, 0.439, 1)
            self.generateBody()
            self.generateHead2('middleman')
            self.generateHead2('downsizerHat')
            self.setHeight(6.7)
        elif dna.name == 'cbr':
            self.scale = 5.0 / aSize
            self.handColor = VBase4(0.537, 0.6, 0.592, 1)
            self.generateBody()
            self.generateHead3('circuitbreaker', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_circuitbreaker.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.3)
        elif dna.name == 'txm':
            self.scale = 5.0 / cSize
            self.handColor = VBase4(0.769, 0.694, 0.314, 1)
            self.generateBody()
            self.generateHead2('toxicleader')
            self.setHeight(7.0)
        elif dna.name == 'dl':
            self.scale = 5.25 / cSize
            self.handColor = VBase4(0.463, 0.58, 0.592, 1)
            self.generateBody()
            self.generateHead3('deadlock', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_deadlock.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.2)
        elif dna.name == 'neg':
            self.scale = 5.5 / aSize
            self.handColor = VBase4(0.902, 0.91, 0.906, 1)
            self.generateBody()
            self.generateHead2('twoface')
            texture = loader.loadTexture('phase_3.5/maps/middleman.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.2)
        elif dna.name == 'shw':
            self.scale = 5.6 / cSize
            self.handColor = VBase4(0.427, 0.608, 0.631, 1)
            self.generateBody()
            self.generateHead3('sharkwatcher', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_sharkwatcher.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.25)
        elif dna.name == 'rng':
            self.scale = 6.5 / aSize
            self.handColor = VBase4(0.047, 0.051, 0.055, 1.0)
            self.generateBody()
            self.generateHead2('magnate')
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_magnate.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.45)
        elif dna.name == 'cor':
            self.scale = 5.75 / aSize
            self.handColor = VBase4(0.459, 0.447, 0.439, 1)
            self.generateBody()
            self.generateHead2('yesman')
            texture = loader.loadTexture('phase_4/maps/middleman_custom.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.5)
        elif dna.name == 'sab':
            self.scale = 5.75 / aSize
            self.handColor = VBase4(0.459, 0.447, 0.439, 1)
            self.generateBody()
            self.generateHead2('yesman')
            texture = loader.loadTexture('phase_4/maps/middleman_custom1.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.5)
        elif dna.name == 'vul':
            self.scale = 6.0 / bSize
            self.handColor = VBase4(0.733, 0.49, 0.49, 1)
            self.generateFemaleBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/VultureCapitalistEdit.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.0)
        elif dna.name == 'stol':
            self.scale = 6.5 / aSize
            self.handColor = VBase4(0.263, 0.278, 0.31, 1.0)
            self.generateBody()
            self.generateHead2('legaleagle')
            texture = loader.loadTexture('phase_4/maps/stool_pigeon.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.45)
        elif dna.name == 'mg':
            self.scale = 6.8 / aSize
            self.handColor = VBase4(0.169, 0.169, 0.169, 1)
            self.generateBody()
            self.generateHead3('magnate', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_magnate.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
                headPart.setTwoSided(True)
            self.setHeight(8.5)
        elif dna.name == 'chw':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.682, 0.643, 0.624, 1)
            self.generateBody()
            self.generateHead2('headhoncho')
            texture = loader.loadTexture('phase_3.5/maps/head-honcho.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.7)
        elif dna.name == 'bfh2':
            self.scale = 7.5 / cSize
            self.handColor = VBase4(0.635, 0.62, 0.651, 1)
            self.generateFemaleBody()
            self.generateHead2('bigfish')
            self.setHeight(10.7)
        elif dna.name == 'ang':
            self.scale = 6.5 / bSize
            self.handColor = VBase4(0.733, 0.733, 0.733, 1)
            self.generateFemaleBody()
            self.generateHead3('shyster', animated=True)
            self.generateHead2('angel_halo')
            self.generateHead2('angel_wings')
            #texture = loader.loadTexture('phase_14/maps/cc_t_ene_magnate.png')
            #for headPart in self.headParts:
                #headPart.setTexture(texture, 1)
            self.setHeight(9.5)
        elif dna.name == 'hho':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.42, 0.42, 0.42, 1)
            self.generateBody()
            self.generateHead3('headhoncho', animated=True)
            self.setHeight(10.1)
        elif dna.name == 'ddiver':
            self.scale = 7.0 / cSize
            self.handColor = VBase4(0.404, 0.647, 0.635, 1)
            self.generateFemaleBody()
            self.makeDeepDiver()
            self.generateHead3('deepdiver', animated=True)
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_ddiver.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.8)
        elif dna.name == 'gatekeep':
            self.scale = 5.0 / aSize
            self.handColor = VBase4(0.612, 0.612, 0.612, 1)
            self.generateFemaleBody()
            self.makeGatekeeper()
            self.generateHead3('gatekeeper', animated=True)
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_gatekeeper.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.7)
        elif dna.name == 'dola':
            self.scale = 6.75 / bSize
            self.handColor = VBase4(0.486, 0.447, 0.42, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('dola', animated=True)
            self.setHeight(9.9)
        elif dna.name == 'dold':
            self.scale = 7.5 / aSize
            self.handColor = VBase4(1, 0.486, 0, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('dold', animated=True)
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_dold.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
           # self.setTransparency(1)
            self.setHeight(9.9)
        elif dna.name == 'liquid':
            self.scale = 6.25 / aSize
            self.handColor = VBase4(0.498, 0.635, 0.655, 1.0)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('bellringer', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_bellringer_board.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.5)
            # self.makeVulnerable()
            # self.setVulnerability(125)
        elif dna.name == 'rkeeper':
            self.scale = 7.1 / aSize
            self.handColor = VBase4(0.341, 0.341, 0.341, 1)
            self.generateFemaleBody()
            self.makeExecutive()
            self.generateHead3('stenographer', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_stenographer_boardbot.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(10.1)
            # self.makeVulnerable()
            # self.setVulnerability(125)
          #  self.setTransparency(1)
        elif dna.name == 'cbutcher':
            self.scale = 7.1 / aSize
            self.handColor = VBase4(0, 0, 0, 1)
            self.generateFemaleBody()
            self.makeExecutive()
            self.generateHead3('stenographer', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_stenographer_boardbot_phantom.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
                headPart.setColor((1, 1, 1, 1))
            self.setHeight(10.1)
            self.setColor((0, 0, 0, 1))
            # self.makeVulnerable()
            # self.setVulnerability(125)
            self.setSuitStatusEffect('phantomRecordkeeper')
        elif dna.name == 'cdirector':
            self.scale = 7.25 / aSize
            self.handColor = VBase4(0.478, 0.478, 0.486, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('chainsaw', animated=True)
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_chainsaw_boardbot.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(10.55)
            self.setChainsawTexRollContingency(0)
            #self.setTransparency(1)
            # self.makeVulnerable()
            # self.setVulnerability(125)
        elif dna.name == 'dking':
            self.scale = 6.75 / aSize
            self.handColor = VBase4(0.173, 0.173, 0.173, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('redd', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_dking.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.65)
           # self.setTransparency(1)
            # self.makeVulnerable()
            # self.setVulnerability(125)
        elif dna.name == 'ottoman':
            self.scale = 6.0 / bSize
            self.handColor = VBase4(0.302, 0.255, 0.196, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('ottoman', animated=True)
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_ottoman.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.0)
           # self.setTransparency(1)
        elif dna.name == 'fmaker':
            self.scale = 7.05 / aSize
            self.handColor = VBase4(0.518, 0.651, 0.643, 1)
            self.generateMajorPlayerBody()
            self.makeVideographer2()
            self.generateHead3('headhoncho', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_headhoncho_fmaker.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(10.15)
        elif dna.name == 'chairman':
            self.scale = 2.5 / cSize
            self.handColor = VBase4(0.396, 0.373, 0.322, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('chairman-a', animated=True)
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_chairman.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(3.25)
           # self.setTransparency(1)

        # Techbots
        elif dna.name == 'skd':
            self.scale = 4.0 / cSize
            self.handColor = VBase4(0.992, 0.855, 0.878, 1)
            self.generateBody()
            self.generateHead2('flunky')
            texture = loader.loadTexture('phase_3.5/maps/scriptkiddie.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.1)
        elif dna.name == 'skd2':
            self.scale = 4.0 / cSize
            self.handColor = VBase4(0.941, 0.831, 0.914, 1)
            self.generateBody()
            self.generateHead2('scriptKiddie')
            self.setHeight(5.1)
        elif dna.name == 'cmk':
            self.scale = 4.25 / cSize
            self.handColor = VBase4(0.263, 0.208, 0.173, 1)
            self.generateBody()
            self.generateHead2('gladhander')
            texture = loader.loadTexture('phase_3.5/maps/code_monkey.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.63)
        elif dna.name == 'cmk2':
            self.scale = 4.25 / cSize
            self.handColor = VBase4(0.863, 0.718, 0.875, 1)
            self.generateBody()
            self.generateHead2('codeMonkey')
            self.setHeight(5.63)
        elif dna.name == 'dhr':
            self.scale = 4.5 / cSize
            self.handColor = VBase4(0.929, 0.835, 0.961, 1)
            self.generateFemaleBody()
            self.generateHead2('dataHoarder')
            self.setHeight(6.5)
        elif dna.name == 'shrp':
            self.scale = 5.5 / bSize
            self.handColor = VBase4(0.792, 0.561, 0.529, 1)
            self.generateBody()
            self.generateHead2('telemarketer')
            texture = loader.loadTexture('phase_3.5/maps/sharpseer.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.8)
        elif dna.name == 'vpr':
            self.scale = 4.25 / aSize
            self.handColor = VBase4(0.796, 0.706, 0.29, 1)
            self.generateBody()
            self.generateHead2('yesman')
            texture = loader.loadTexture('phase_3.5/maps/voodoo_programmer.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.63)
        elif dna.name == 'pdx':
            self.scale = 4.25 / bSize
            self.handColor = VBase4(0.886, 0.757, 0.843, 1)
            self.generateBody()
            self.generateHead2('pointDexter')
            self.setHeight(5.63)
        elif dna.name == 'vpr2':
            self.scale = 4.25 / aSize
            self.handColor = VBase4(0.596, 0.529, 0.216, 1)
            self.generateBody()
            self.generateHead2('voodoo')
            self.setHeight(5.63)
        elif dna.name == 'brn':
            self.scale = 5.25 / aSize
            self.handColor = VBase4(0.984, 0.827, 0.922, 1)
            self.generateBody()
            self.generateHead2('brainiac')
            self.setHeight(7.0)
        elif dna.name == 'phis':
            self.scale = 5.25 / aSize
            self.handColor = VBase4(0.996, 0.839, 0.643, 1)
            self.generateFemaleBody()
            self.generateHead2('numbercruncher')
            texture = loader.loadTexture('phase_3.5/maps/voodoo-programmer.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.0)
        elif dna.name == 'sdb':
            self.scale = 5.0 / cSize
            self.handColor = VBase4(0.478, 0.467, 0.463, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/default_COLOR_0_COLOR_0.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.0)
        elif dna.name == 'key':
            self.scale = 5.5 / aSize
            self.handColor = VBase4(0.345, 0.345, 0.345, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/Material.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.0)
        elif dna.name == 'kbc':
            self.scale = 5.2 / bSize
            self.handColor = VBase4(0.682, 0.682, 0.675, 1)
            self.generateBody()
            self.generateHead2('beancounter')
            texture = loader.loadTexture('phase_3.5/maps/keyboard_cowboy.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.81)
        elif dna.name == 'blk':
            self.scale = 6.0 / bSize
            self.handColor = VBase4(0.925, 0.882, 0.961, 1)
            self.generateBody()
            self.generateHead2('blackHat')
            self.setHeight(8.0)
        elif dna.name == 'sfs':
            self.scale = 5.85 / aSize
            self.handColor = VBase4(0.369, 0.282, 0.224, 1)
            self.generateBody()
            self.generateHead2('numbercruncher')
            texture = loader.loadTexture('phase_3.5/maps/software_simian.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.8)
        elif dna.name == 'oilg':
            self.scale = 6.0 / aSize
            self.handColor = VBase4(0.929, 0.929, 0.929, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/Data-Ogligarch.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.8)
        elif dna.name == 'pyc':
            self.scale = 6.0 / aSize
            self.handColor = VBase4(0.447, 0.302, 0.471, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/phong1_COLOR_0_COLOR_0.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
                headPart.setTwoSided(True)
                headPart.setTransparency(1)
            self.setHeight(8.1)
        elif dna.name == 'inw':
            self.scale = 6.5 / bSize
            self.handColor = VBase4(0.843, 0.753, 0.929, 1)
            self.generateBody()
            self.generateHead2('movershaker')
            texture = loader.loadTexture('phase_3.5/maps/installation-wizard.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.95)
        elif dna.name == 'inw2':
            self.scale = 6.5 / bSize
            self.handColor = VBase4(0.643, 0.533, 0.651, 1)
            self.generateBody()
            self.generateHead2('installer-wizard')
            self.setHeight(8.95)
        elif dna.name == 'chg':
            self.scale = 6.5 / bSize
            self.handColor = VBase4(0.643, 0.533, 0.651, 1)
            self.generateFemaleBody()
            self.generateHead2('Change Agent head')
            self.setHeight(9.0)
        elif dna.name == 'cpu':
            self.scale = 6.5 / bSize
            self.handColor = VBase4(0.941, 0.859, 0.941, 1)
            self.generateBody()
            self.generateHead2('computerWizard')
            self.setHeight(8.95)
        elif dna.name == 'itn':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.882, 0.839, 0.929, 1)
            self.generateBody()
            self.generateHead2('industryTitan')
            self.setHeight(9.0)
        elif dna.name == 'asm':
            self.scale = 6.5 / cSize
            self.handColor = VBase4(0.843, 0.525, 0.518, 1)
            self.generateBody()
            self.generateHead2('flunky')
            texture = loader.loadTexture('phase_3.5/maps/mademan.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.1)
        elif dna.name == 'rus':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.525, 0.455, 0.369, 1)
            self.generateBody()
            self.generateHead2('telemarketer')
            texture = loader.loadTexture('phase_3.5/maps/telemarketer.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(9.0)
        elif dna.name == 'rus2':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.357, 0.243, 0.141, 1)
            self.generateBody()
            self.generateHead2('root_user')
            self.setHeight(9.5)
        elif dna.name == 'djockey':
            self.scale = 4.0 / cSize
            self.handColor = VBase4(0.882, 0.847, 0.784, 1)
            self.generateBody()
            self.makeDummy()
            self.generateHead3('dummy', animated=True)
            texture = loader.loadTexture('phase_4/maps/schoolhouse/dummy/ttcc_ene_djockey.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.1)
        elif dna.name == 'ptjockey':
            self.scale = 4.0 / cSize
            self.handColor = VBase4(0.882, 0.847, 0.784, 1)
            self.generateBody()
            self.makeDummy()
            self.generateHead3('dummy', animated=True)
            texture = loader.loadTexture('phase_4/maps/schoolhouse/dummy/ttcc_ene_djockey.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.1)
        elif dna.name == 'bcaster':
            self.scale = 7.1 / aSize
            self.handColor = VBase4(0.322, 0.325, 0.325, 1)
            self.generateMajorPlayerBody()
            self.makeVideographer2()
            self.generateHead3('multislacker', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_videographer2.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.makeVirtual()
            # self.makeVulnerable()
            # self.setVulnerability(125)
            self.setSuitStatusEffect('vulnerable', modifier=100)
            self.setHeight(10.6)
            self.setTransparency(1)
        elif dna.name == 'videog':
            self.scale = 7.1 / aSize
            self.handColor = VBase4(0.322, 0.325, 0.325, 1)
            self.generateMajorPlayerBody()
            self.makeVideographer()
            self.generateHead3('multislacker', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_videographer2.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(10.6)
            self.setTransparency(1)

        # Pressbots
        elif dna.name == 'ppb':
            self.scale = 3.75 / bSize
            self.handColor = VBase4(0.824, 0.808, 0.765, 1)
            self.generateBody()
            self.generateHead2('paperboy')
            texture = loader.loadTexture('phase_4/maps/paperboy.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.1)
        elif dna.name == 'shb':
            self.scale = 3.0 / cSize
            self.handColor = VBase4(0.314, 0.333, 0.396, 1)
            self.generateFemaleBody()
            self.generateHead2('shutterbug')
            texture = loader.loadTexture('phase_4/maps/shutterbug.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(4.0)
        elif dna.name == 'bsd':
            self.scale = 4.0 / cSize
            self.handColor = VBase4(0.675, 0.675, 0.753, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/backseat.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.5)
        elif dna.name == 'gms':
            self.scale = 4.0 / cSize
            self.handColor = VBase4(0.702, 0.608, 0.255, 1)
            self.generateBody()
            self.generateHead2('gumshoe')
            texture = loader.loadTexture('phase_4/maps/gumshoe.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.7)
        elif dna.name == 'hck':
            self.scale = 4.5 / bSize
            self.handColor = VBase4(0.918, 0.918, 0.918, 1)
            self.generateFemaleBody()
            self.generateHead2('hackette')
            texture = loader.loadTexture('phase_4/maps/hackette.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.0)
        elif dna.name == 'ath':
            self.scale = 4.25 / bSize
            self.handColor = VBase4(0.62, 0.89, 0.843, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/ghost_writer.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.75)
        elif dna.name == 'ghw':
            self.scale = 5.25 / aSize
            self.handColor = VBase4(0.173, 0.173, 0.173, 1)
            self.generateBody()
            self.generateHead2('ghostwriter')
            texture = loader.loadTexture('phase_4/maps/ghostwriter.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.6)
        elif dna.name == 'gzt':
            self.scale = 6.25 / aSize
            self.handColor = VBase4(0.514, 0.514, 0.514, 1)
            self.generateBody()
            self.generateHead2('gazetteer')
            texture = loader.loadTexture('phase_4/maps/gazetteer.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.25)
        elif dna.name == 'nsh':
            self.scale = 6.75 / aSize
            self.handColor = VBase4(0.337, 0.29, 0.278, 1)
            self.generateBody()
            self.generateHead2('newshound')
            texture = loader.loadTexture('phase_4/maps/newshound.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.55)
        elif dna.name == 'anc':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.8, 0.776, 0.765, 1)
            self.generateBody()
            self.generateHead2('anchorman')
            texture = loader.loadTexture('phase_4/maps/anchorman.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(9.0)
        elif dna.name == 'director':
            self.scale = 7.1 / aSize
            self.handColor = VBase4(0.745, 0.42, 0.42, 1)
            self.generateMajorPlayerBody()
            self.makeVideographer2()
            self.generateHead3('majorplayer', animated=True)
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_director.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(10.05)
            #self.isSkelecogDialogue = 1
            self.setSuitStatusEffect('directorShielding', modifier=50)
        # DUMMY BOSSES
        elif dna.name == 'ceo':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.341, 0.341, 0.341, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('ceo-a', animated=True)
            self.setHeight(9.05)
        elif dna.name == 'clo':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.341, 0.341, 0.341, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('clo', animated=True)
            self.setHeight(9.05)
        elif dna.name == 'cfo':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.341, 0.341, 0.341, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('cfo', animated=True)
            self.setHeight(9.05)
        elif dna.name == 'vp':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.341, 0.341, 0.341, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('vp', animated=True)
            self.setHeight(9.05)
        elif dna.name == 'chairman2':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.341, 0.341, 0.341, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('chairman-a', animated=True)
            self.setHeight(9.05)
        elif dna.name == 'cj':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.341, 0.341, 0.341, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead2('bossCog-head')
            self.setHeight(9.05)
        elif dna.name == 'cio':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.341, 0.341, 0.341, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead2('Vert')
            self.setHeight(9.05)
        elif dna.name == 'hocn':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.341, 0.341, 0.341, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead2('sellbotBoss-head-zero')
            self.setHeight(9.05)
        self.setName(SuitBattleGlobals.SuitAttributes[dna.name]['name'])
        self.getGeomNode().setScale(self.scale)
        if not self.isSkeleton and not self.isVirtual:
            self.generateHealthBar()
            self.generateCorporateMedallion()
            #self.generateCorporateMedallion3()
            self.generateHPBase()
        elif self.isVirtual:
            self.generateHealthBar()
            self.generateCorporateMedallion3()
            self.generateHPBase()
        else:
            #self.generateSkeletonHealthBar()
            self.generateCorporateMedallion3()
        return