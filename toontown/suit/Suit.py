from direct.actor import Actor
import random
import math
from direct.directnotify import DirectNotifyGlobal
from otp.avatar import Avatar
from direct.interval.IntervalGlobal import *
from toontown.suit import SuitDNA
from toontown.battle import MovieUtil
from toontown.toonbase import ToontownGlobals
from pandac.PandaModules import *
from direct.interval.IntervalGlobal import *
from toontown.battle import BattleParticles
from direct.particles import ParticleEffect
from direct.showutil import Effects
from toontown.battle import SuitBattleGlobals
from toontown.nametag import NametagGlobals
from direct.task.Task import Task
from toontown.battle import BattleProps
from toontown.toonbase import TTLocalizer
from pandac.PandaModules import VirtualFileMountHTTP, VirtualFileSystem, Filename, DSearchPath
from direct.showbase import AppRunnerGlobal
from toontown.nametag import NametagGroup
import string
import os
from toontown.suit import SuitGlobals

aSize = 6.06
bSize = 5.29
cSize = 4.14
SuitDialogArray = []
SkelSuitDialogArray = []
SkelecogDialogFemaleArray = []
PrethinkerDialogArray = []
PacesetterDialogArray = []
CLODialogArray = []
FirestarterDialogArray = []
LitigatorDialogArray = []
CaseManagerDialogArray = []
ScapegoatDialogArray = []
MajorPlayerDialogArray = []
DuckShufflerDialogArray = []
PlutocratDialogArray = []
WitchHunterDialogArray = []
RainmakerDialogArray = []
ChairmanDialogArray = []
OttomanDialogArray = []
CEODialogArray = []
ChainsawDialogArray = []
DOLADialogArray = []
DOPADialogArray = []
DOLDDialogArray = []
DOPRDialogArray = []
DerrickHandDialogArray = []
DerrickSkeleDialogArray = []
DerrickManDialogArray = []
MultislackerDialogArray = []
BellringerDialogArray = []
CountErfitDialogArray = []
FeatherbedderDialogArray = []
DeepDiverDialogArray =[]
GatekeeperDialogArray = []
MouthpieceDialogArray = []
ReddDialogArray = []
DeskJockeyDialogArray = []
ChainsawORDialogArray = []
SkelecogDialogArray = []
HighRollerDialogArray = []
StenographerDialogArray = []
FemaleDialogArray = []
TreekillerDialogArray = []
AllSuits = (('walk', 'walk'), ('run', 'walk'), ('short-squeeze', 'short-squeeze'), ('lose3', 'wrecked'), ('speak', 'speak'), ('glower', 'glower'), ('rolled', 'rolled'),  ('song-and-dance', 'song-and-dance'), ('calculator', 'calculator'), ('calculating-costs', 'calculating-costs'), ('phone', 'phone'), ('blue-chip', 'blue-chip'),
            ('falling-knife', 'falling-knife'), ('throw-object', 'throw-object'), ('flail-wb', 'flailing-wb'), ('tnt-react', 'tnt-react'), ('flail-qs', 'flailing-qs'),
            ('throw-paper', 'throw-paper'), ('mob-mentality', 'mob-mentality'), ('neutral', 'neutral'), ('neutral2', 'neutral'), ('magnet', 'magnet'), ('neutral2-hurt', 'neutral-hurt'),
            ('neutral-hurt', 'neutral-hurt'), ('neutral-unstable', 'neutral-unstable'), ('neutral-enraged-return', 'neutral-enraged-return'), ('ottoman-sit-loop', 'ottoman-sit-loop'),
            ('ottoman-writing-loop', 'ottoman-writing-loop'), ('ottoman-writing-start', 'ottoman-writing-start'), ('ottoman-writing-stop', 'ottoman-writing-stop'),
            ('neutral-override', 'neutral-override'), ('neutral-override-glitched', 'neutral-override-glitched'), ('neutral-enraged-return', 'neutral-enraged-return'),
            ('neutral-enraged', 'neutral-enraged'), ('highroller-neutral-levitate-loop', 'highroller-neutral-levitate-loop'), ('highroller-neutral-levitate-in-out', 'highroller-neutral-levitate-in-out'),
            ('wrecked', 'wrecked'), ('lose3', 'wrecked'), ('headless-death', 'headless-death'),  ('magic1', 'magic1'), ('magic2', 'magic2'), ('magic3', 'magic3'))
AllSuitsMinigame = (('victory', 'victory'), ('flail', 'flailing'), ('flail-wb', 'flailing-wb'), ('tnt-react', 'tnt-react'), ('flail-qs', 'flailing-qs'),  ('tug-o-war', 'tug-o-war'),
                    ('slip-backward', 'slip-backward'), ('lose3', 'wrecked'), ('slip-forward', 'slip-forward'))
AllSuitsTutorialBattle = (('lose', 'lose'), ('lose2', 'headless-death'), ('wrecked', 'wrecked'), ('lose3', 'wrecked'), ('dance', 'song-and-dance'), ('pie-small-react', 'pie-small'),
                          ('squirt-small-react', 'squirt-small'))
AllSuitsBattle = (('drop-react', 'anvil-drop'), ('flatten', 'drop'), ('speak', 'speak'), ('song-and-dance', 'song-and-dance'), ('glower', 'glower'), ('headless-death', 'headless-death'), ('dance', 'song-and-dance'), ('frustrated', 'frustrated-f'),
                  ('lose3', 'wrecked'), ('short-squeeze', 'short-squeeze'), ('gag-miss', 'gag-miss'), ('pie-large', 'pie-large'), ('rolled', 'rolled'), ('pie-large-lured', 'pie-large-lured'), ('highroller-neutral-levitate-loop', 'highroller-neutral-levitate-loop', 4),
                  ('highroller-neutral-levitate-in-out', 'highroller-neutral-levitate-in-out', 4), ('wrecked', 'wrecked'), ('sidestep-left', 'sidestep-left'),
                  ('sidestep-right', 'sidestep-right'), ('squirt-large-react', 'squirt-large'), ('sound-react', 'sound-react'), ('sound-react-bow', 'sound-react-bow'),
                  ('sound-react-nt', 'sound-react-nt'),
                  ('landing', 'landing'), ('reach', 'walknreach-bill'), ('rake-react', 'rake'), ('hypnotized', 'hypnotize'), ('shock', 'shock'), ('large-zap', 'large-zap'),
                  ('small-zap', 'small-zap'), ('soak', 'soak'), ('lured', 'lured'), ('lured2', 'lured'))
SuitsCEOBattle = (('sit', 'sit'), ('sit-eat-in', 'sit-eat-in'), ('sit-eat-loop', 'sit-eat-loop'), ('sit-eat-out', 'sit-eat-out'), ('lose3', 'wrecked'), ('sit-angry', 'sit-angry'),
                  ('sit-exec', 'sit-exec'), ('sit-hungry-left', 'leftsit-hungry'), ('speak', 'speak'), ('sit-hungry-right', 'rightsit-hungry'), ('sit-lose', 'sit-lose'), ('tray-walk', 'tray-walk'),
                  ('tray-neutral', 'tray-neutral'), ('sit-lose', 'sit-lose'), ('headless-death', 'headless-death'))

# Bossbots
f = (('throw-paper', 'throw-paper', 4), ('phone', 'phone', 4), ('shredder', 'shredder', 4))
p = (('pencil-sharpener', 'pencil-sharpener', 4), ('pen-squirt', 'pen-squirt', 4), ('hold-eraser', 'hold-eraser', 4), ('finger-wag', 'finger-wag', 4), ('hold-pencil', 'hold-pencil', 4))
stg = (('finger-wag', 'finger-wag', 4), ('pen-squirt', 'fountain-pen', 4))
ym = (('golf-club-swing', 'golf-club-swing', 4), ('rubber-stamp', 'rubber-stamp', 4), ('smile', 'smile', 4))
enf =  (('roll-o-dex', 'roll-o-dex', 4), ('effort', 'effort', 4), ('smile', 'smile', 4))
mm = (('speak', 'speak', 4), ('effort', 'effort', 4), ('pen-squirt', 'fountain-pen', 4))
blh = (('cigar-smoke', 'cigar-smoke', 4), ('effort', 'effort', 4), ('glower', 'glower', 4), ('roll-o-dex', 'roll-o-dex', 4))
ds = (('glower', 'glower', 4), ('roll-o-dex', 'roll-o-dex', 4))
mldr = (('golf-club-swing', 'golf-club-swing', 4), ('effort', 'effort', 4))
hh = (('glower', 'glower', 4), ('roll-o-dex', 'roll-o-dex', 4))
bsht = (('effort', 'effort', 4), ('speak', 'speak', 4), ('golf-club-swing', 'golf-club-swing', 4))
cr = (('glower', 'glower', 4), ('effort', 'effort', 4), ('pickpocket', 'pickpocket', 4))
txl = (('effort', 'effort', 4), ('glower', 'glower', 4), ('effort', 'effort', 4), ('cigar-smoke', 'cigar-smoke', 4))
tbc = (('glower', 'glower', 4), ('golf-club-swing', 'golf-club-swing', 4), ('cigar-smoke', 'cigar-smoke', 4))
autocad = (('glower', 'glower', 4), ('golf-club-swing', 'golf-club-swing', 4), ('song-and-dance', 'song-and-dance', 4), ('cigar-smoke', 'cigar-smoke', 4))
clubpres = (('glower', 'glower', 4), ('frustrated', 'frustrated', 4), ('golf-club-swing', 'golf-club-swing', 4), ('song-and-dance', 'song-and-dance', 4), ('cigar-smoke', 'cigar-smoke', 4))
derrman = (('pen-squirt', 'fountain-pen', 4), ('glower', 'glower', 4), ('quick-jump', 'jump', 4))
derrhand = (('pen-squirt', 'fountain-pen', 4), ('quick-jump', 'jump', 4), ('glower', 'glower', 4), ('summon', 'summon', 4))
mplayer = (('song-and-dance', 'song-and-dance', 4),  ('quick-jump', 'jump', 4), ('neutral', 'rolled', 4), ('speak', 'speak', 4))
fires = (('speak', 'speak', 4), ('cigar-smoke', 'firestarter-cigar-smoke', 4))
fbed = (('speak', 'speak', 4), ('cigar-smoke', 'firestarter-cigar-smoke', 4))
mplayer2 = (('song-and-dance', 'song-and-dance', 4),  ('quick-jump', 'jump', 4), ('neutral', 'rolled', 4), ('speak', 'speak', 4))
chainsaw = (('roll-o-dex', 'roll-o-dex', 4), ('glower', 'glower', 4), ('quick-jump', 'jump', 4))
chainsaw2 = (('roll-o-dex', 'roll-o-dex', 4), ('glower', 'glower', 4), ('quick-jump', 'jump', 4), ('neutral', 'neutral-override', 4))
phouse = (('magic3-alt', 'magic3-alt', 4), ('effort', 'effort', 4), ('speak', 'speak', 4), ('scabbard', 'scabbard', 4),('summon', 'summon', 4), ('defense', 'defense', 4), ('glower', 'glower', 4))
bkeeper = (('rubber-stamp', 'rubber-stamp', 4), ('sanction', 'sanction', 4), ('effort', 'effort', 4), ('pen-squirt', 'fountain-pen', 4), ('roll-o-dex', 'roll-o-dex', 4))
wtapper = (('rubber-stamp', 'rubber-stamp', 4), ('speak', 'speak', 4), ('snap', 'snap2', 4), ('cease', 'cease3', 4), ('roll-o-dex', 'roll-o-dex', 4))
ambass = (('deadwood', 'deadwood', 4), ('golf-club-swing', 'golf-club-swing', 4), ('glower', 'glower', 4), ('summon', 'summon', 4), ('effort', 'effort', 4), ('cease', 'cease', 4), ('snap', 'snap2', 4))

# Sellbots
cc = (('speak', 'speak', 4), ('glower', 'glower', 4))
tm = (('speak', 'speak', 4), ('pickpocket', 'pickpocket', 4), ('roll-o-dex', 'roll-o-dex', 4), ('finger-wag', 'finger-wag', 4))
cn = (('speak', 'speak', 4), ('pickpocket', 'pickpocket', 4))
nd = (('smile', 'smile', 4), ('roll-o-dex', 'roll-o-dex', 4))
dc = (('glower', 'glower', 4), ('speak', 'speak', 4))
gh = (('speak', 'speak', 4), ('pen-squirt', 'fountain-pen', 4), ('rubber-stamp', 'rubber-stamp', 4))
fcs = (('quick-jump', 'jump', 4), ('effort', 'effort', 4), ('glower', 'glower', 4))
ms = (('effort', 'effort', 4), ('stomp', 'stomp', 4), ('quick-jump', 'jump', 4))
cnd = (('speak', 'speak', 4), ('song-and-dance', 'song-and-dance', 4), ('golf-club-swing', 'golf-club-swing', 4), ('smile', 'smile', 4))
tf = (('smile', 'smile', 4), ('glower', 'glower', 4))
ppl = (('speak', 'speak', 4), ('smile', 'smile', 4), ('golf-club-swing', 'golf-club-swing', 4))
m = (('speak', 'speak', 4), ('golf-club-swing', 'golf-club-swing', 4))
ksp = (('speak', 'speak', 4), ('smile', 'smile', 4))
mh = (('smile', 'smile', 4), ('speak', 'speak', 4), ('golf-club-swing', 'golf-club-swing', 4), ('song-and-dance', 'song-and-dance', 4))
watchm = (('rolled', 'rolled', 4), ('frustrated', 'frustrated', 4), ('speak', 'speak', 4))
foreman = (('rolled', 'rolled', 4), ('frustrated', 'frustrated', 4), ('speak', 'speak', 4))
dopr = (('effort', 'effort', 4), ('glower', 'glower', 4), ('speak', 'speak', 4))
dopa = (('speak', 'speak', 4), ('effort', 'effort', 4))
bellring = (('roll-o-dex', 'roll-o-dex', 4), ('quick-jump', 'jump', 4))
mh2 = (('smile', 'smile', 4), ('speak', 'speak', 4), ('golf-club-swing', 'golf-club-swing', 4), ('song-and-dance', 'song-and-dance', 4), ('neutral', 'rolled', 4), ('shot5', 'shot5', 4))
prethink = (('effort', 'effort', 4), ('speak', 'speak', 4))
mslacker = (('cigar-smoke', 'cigar-smoke', 4), ('pen-squirt', 'fountain-pen', 4))
put = (('snap', 'snap2', 4), ('neutral', 'rolled', 4), ('throttletwo', 'throttletwo', 4), ('shot5', 'shot5', 4), ('pen-squirt', 'fountain-pen', 4))
radiog = (('glower', 'glower', 4), ('quick-jump', 'jump', 4), ('sanction', 'sanction', 4), ('speak', 'speak', 4), ('smile', 'smile', 4))
racket = (('objection', 'objection', 4), ('effort', 'effort', 4), ('rush-job', 'rush-job', 4), ('come-on', 'come-on', 4), ('stomp', 'stomp', 4), ('glower', 'glower', 4))
ubuster = (('summon', 'summon', 4), ('quick-jump', 'jump', 4), ('glower', 'glower', 4), ('sanction', 'sanction', 4))
safesupervis = (('cease', 'cease', 4), ('snap', 'snap2', 4), ('finger-wag', 'finger-wag', 4), ('magic3-alt', 'magic3-alt', 4))
psetter = (('quick-jump', 'jump', 4), ('magic1', 'magic1', 4), ('speak', 'speak', 4), ('smile', 'smile', 4), ('neutral', 'pace', 4), ('neutral2', 'neutral', 4))

# Cashbots
sc = (('watercooler', 'watercooler', 4), ('pickpocket', 'pickpocket', 4))
pp = (('glower', 'glower', 4), ('finger-wag', 'finger-wag', 4), ('pickpocket', 'pickpocket', 4))
shy = (('pickpocket', 'pickpocket', 4), ('pen-squirt', 'fountain-pen', 4))
tw = (('glower', 'glower', 4), ('finger-wag', 'finger-wag', 4))
sw = (('pickpocket', 'pickpocket', 4), ('pen-squirt', 'fountain-pen', 4))
bc = (('hold-pencil', 'hold-pencil', 4), ('pickpocket', 'pickpocket', 4))
fct = (('watercooler', 'watercooler', 4), ('finger-wag', 'finger-wag', 4))
nc = (('cigar-smoke', 'cigar-smoke', 4), ('pen-squirt', 'fountain-pen', 4))
gld = (('pickpocket', 'pickpocket', 4), ('cigar-smoke', 'cigar-smoke', 4), ('effort', 'effort', 4))
mb = (('effort', 'effort', 4), ('pen-squirt', 'fountain-pen', 4))
trs = (('effort', 'effort', 4), ('pickpocket', 'pickpocket', 4), ('smile', 'smile', 4), ('rubber-stamp', 'rubber-stamp', 4))
ls = (('hold-pencil', 'hold-pencil', 4), ('pen-squirt', 'fountain-pen', 4))
bfh = (('watercooler', 'watercooler', 4), ('pickpocket', 'pickpocket', 4))
rb = (('cigar-smoke', 'cigar-smoke', 4), ('pickpocket', 'pickpocket', 4), ('golf-club-swing', 'golf-club-swing', 4))
ovt = (('cigar-smoke', 'cigar-smoke', 4), ('effort', 'effort', 4))
supervis = (('cigar-smoke', 'cigar-smoke', 4), ('pen-squirt', 'fountain-pen', 4))
duckshfl = (('cigar-smoke', 'cigar-smoke', 4), ('sit-dock', 'sit-dock', 4))
treek = (('shredder', 'shredder', 4), ('pen-squirt', 'fountain-pen', 4))
styx = (('watercooler', 'watercooler', 4), ('glower', 'glower', 4))
nix = (('hold-eraser', 'hold-eraser', 4), ('pen-squirt', 'fountain-pen', 4))
hydra = (('cigar-smoke', 'cigar-smoke', 4), ('pen-squirt', 'fountain-pen', 4))
kerberos = (('pickpocket', 'pickpocket', 4), ('pen-squirt', 'fountain-pen', 4))
charon = (('cigar-smoke', 'cigar-smoke', 4), ('pen-squirt', 'fountain-pen', 4))
pcrat = (('pickpocket', 'pickpocket', 4), ('glower', 'glower', 4), ('cigar-smoke', 'plutocrat-cigar-smoke', 4))
hroller = (('cease', 'cease3', 4), ('taunt', 'taunt', 4), ('wheelspin', 'wheelspin', 4), ('shot5', 'shot5', 4), ('bust', 'bust', 4), ('snap', 'snap2', 4), ('song-and-dance', 'song-and-dance', 4), ('walk', 'awalk', 4))
erfit = (('pickpocket', 'pickpocket', 4), ('glower', 'glower', 4), ('cigar-smoke', 'plutocrat-cigar-smoke', 4))
hrollers = (('glower', 'glower', 4), ('sanction', 'sanction', 4), ('snap', 'snap2', 4), ('shot5', 'shot5', 4), ('neutral', 'rolled', 4))
hroller2 = (('wheelspin', 'wheelspin', 4), ('bust', 'bust', 4), ('snap', 'snap2', 4), ('shot5', 'shot5', 4), ('song-and-dance', 'song-and-dance', 4), ('neutral', 'rolled', 4), ('neutral-hurt', 'rolled', 4))

# Lawbots
bf = (('shredder', 'shredder', 4), ('finger-wag', 'finger-wag', 4))
b = (('pickpocket', 'pickpocket', 4), ('pen-squirt', 'fountain-pen', 4))
pf = (('speak', 'speak', 4), ('hold-pencil', 'hold-pencil', 4), ('finger-wag', 'finger-wag', 4))
dt = (('rubber-stamp', 'rubber-stamp', 4), ('speak', 'speak', 4))
cv = (('throw-paper', 'throw-paper', 4), ('speak', 'speak', 4), ('roll-o-dex', 'roll-o-dex', 4))
ac = (('roll-o-dex', 'roll-o-dex', 4), ('quick-jump', 'jump', 4),('stomp', 'stomp', 4))
nn = (('pen-squirt', 'fountain-pen', 4), ('rubber-stamp', 'rubber-stamp', 4), ('speak', 'speak', 4))
bs = (('effort', 'effort', 4), ('pickpocket', 'pickpocket', 4), ('finger-wag', 'finger-wag', 4))
ad = (('shredder', 'shredder', 4), ('watercooler', 'watercooler', 4), ('glower', 'glower', 4))
sd = (('quick-jump', 'jump', 4), ('hold-pencil', 'hold-pencil', 4))
sh = (('hold-eraser', 'hold-eraser', 4), ('pen-squirt', 'fountain-pen', 4))
le = (('speak', 'speak', 4), ('pen-squirt', 'fountain-pen', 4))
br = (('quick-jump', 'jump', 4), ('glower', 'glower', 4))
bw = (('finger-wag', 'fingerwag', 4), ('cigar-smoke', 'cigar-smoke', 4))
whistleb = (('rubber-stamp', 'rubber-stamp', 4), ('speak', 'speak', 4), ('pen-squirt', 'fountain-pen', 4))
clerk = (('quick-jump', 'jump', 4), ('pen-squirt', 'fountain-pen', 4))
arbit = (('cigar-smoke', 'cigar-smoke', 4), ('pen-squirt', 'fountain-pen', 4))
judy = (('cigar-smoke', 'cigar-smoke', 4), ('pen-squirt', 'fountain-pen', 4))
mouthp = (('roll-o-dex', 'roll-o-dex', 4), ('finger-wag', 'finger-wag', 4))
rainmake = (('effort', 'effort', 4), ('sit-dock', 'sit-dock', 4))
whunter = (('mob-mentality', 'mob-mentality', 4), ('speak', 'speak', 4))
erclaim = (('cigar-smoke', 'cigar-smoke', 4), ('pen-squirt', 'fountain-pen', 4))
redd = (('rage', 'rage', 4), ('come-on', 'come-on', 4), ('stomp', 'stomp', 4), ('hold-pencil', 'hold-pencil', 4), ('effort', 'effort', 4))
wsi = (('chainsaw-cutscene-hurt-neutral', 'chainsaw-cutscene-hurt-neutral', 4), ('taunt', 'taunt-alt', 4), ('taunt', 'taunt', 4), ('summon', 'summon', 4), ('glower', 'glower', 4), ('cease', 'cease2', 4))
sgoat = (('stomp', 'stomp', 4), ('rage', 'rage', 4), ('finger-wag', 'finger-wag', 4), ('neutral-enraged', 'neutral-enraged', 4), ('effort', 'effort', 4), ('defense', 'defense', 4))
caseman = (('throw-insurance', 'throw-insurance', 4), ('roll-o-dex', 'roll-o-dex', 4), ('pen-squirt', 'fountain-pen', 4), ('cease', 'cease', 4))
stenog = (('speak', 'speak', 4), ('cease', 'cease3', 4), ('sanction', 'sanction3', 4))
lgator = (('snap2', 'snap2', 4), ('snap', 'snap', 4), ('bellow', 'bellow', 4), ('glower', 'glower', 4))

# Boardbots
bgh = (('pickpocket', 'pickpocket', 4), ('rubber-stamp', 'rubber-stamp', 4), ('short-squeeze', 'short-squeeze', 4))
pph = (('pen-squirt', 'pen-squirt', 4), ('hold-pencil', 'hold-pencil', 4), ('roll-o-dex', 'roll-o-dex', 4), ('short-squeeze', 'short-squeeze', 4))
ca = (('pen-squirt', 'pen-squirt', 4), ('speak', 'speak', 4), ('pen-squirt', 'fountain-pen', 4))
ins = (('pickpocket', 'pickpocket', 4), ('pen-squirt', 'fountain-pen', 4))
mdm = (('smile', 'smile', 4), ('roll-o-dex', 'roll-o-dex', 4))
cbr = (('quick-jump', 'jump', 4), ('effort', 'effort', 4))
txm =  (('pen-squirt', 'fountain-pen', 4), ('glower', 'glower', 4))
dl = (('glower', 'glower', 4), ('short-squeeze', 'short-squeeze', 4))
ang = (('speak', 'speak', 4), ('smile', 'smile', 4))
shw = (('watercooler', 'watercooler', 4), ('glower', 'glower', 4))
bfh2 = (('watercooler', 'watercooler', 4), ('pen-squirt', 'fountain-pen', 4))
mg = (('golf-club-swing', 'golf-club-swing', 4), ('pen-squirt', 'fountain-pen', 4))
chw = (('cigar-smoke', 'cigar-smoke', 4), ('pen-squirt', 'fountain-pen', 4))
hho = (('headhoncho-cigar-smoke', 'headhoncho-cigar-smoke', 4), ('cigar-smoke', 'cigar-smoke', 4))
chairp = (('quick-jump', 'jump', 4), ('pen-squirt', 'fountain-pen', 4))
bdirector = (('quick-jump', 'jump', 4), ('pen-squirt', 'fountain-pen', 4))
ddiver = (('watercooler', 'watercooler', 4), ('pen-squirt', 'fountain-pen', 4))
gatekeep = (('quick-jump', 'jump', 4), ('pen-squirt', 'fountain-pen', 4))
dola = (('quick-jump', 'jump', 4), ('pen-squirt', 'fountain-pen', 4))
dold = (('quick-jump', 'jump', 4), ('pen-squirt', 'fountain-pen', 4))
pbs = (('snap', 'snap2', 4), ('neutral', 'rolled', 4), ('throttletwo', 'throttletwo', 4), ('shot5', 'shot5', 4), ('pen-squirt', 'fountain-pen', 4))
fmaker = (('cigar-smoke', 'cigar-smoke', 4), ('golf-club-swing', 'golf-club-swing', 4), ('neutral', 'rolled', 4), ('shot5', 'shot5', 4))
jgd = (('cigar-smoke', 'cigar-smoke', 4), ('pen-squirt', 'fountain-pen', 4))
bby = (('cigar-smoke', 'cigar-smoke', 4), ('pen-squirt', 'fountain-pen', 4))
dking = (('cigar-smoke', 'cigar-smoke', 4), ('pen-squirt', 'fountain-pen', 4))
ottoman = (('cigar-smoke', 'cigar-smoke', 4), ('pen-squirt', 'fountain-pen', 4))
crystal = (('cigar-smoke', 'cigar-smoke', 4), ('pen-squirt', 'fountain-pen', 4))
chairman = (('cigar-smoke', 'cigar-smoke', 4), ('pen-squirt', 'fountain-pen', 4))

# Techbots
skd = (('speak', 'speak', 4), ('shredder', 'shredder', 4))
cmk = (('speak', 'speak', 4), ('pen-squirt', 'fountain-pen', 4))
dhr = (('cigar-smoke', 'cigar-smoke', 4), ('pen-squirt', 'fountain-pen', 4))
vpr = (('pickpocket', 'pickpocket', 4), ('speak', 'speak', 4))
brn = (('effort', 'effort', 4), ('finger-wag', 'finger-wag', 4), ('speak', 'speak', 4))
sdb = (('finger-wag', 'finger-wag', 4), ('glower', 'glower', 4))
key = (('finger-wag', 'finger-wag', 4), ('glower', 'glower', 4))
kbc = (('speak', 'speak', 4), ('pen-squirt', 'fountain-pen', 4))
blk = (('finger-wag', 'finger-wag', 4), ('glower', 'glower', 4))
sfs = (('glower', 'glower', 4), ('pen-squirt', 'fountain-pen', 4))
pyc = (('finger-wag', 'finger-wag', 4), ('glower', 'glower', 4))
inw = (('speak', 'speak', 4), ('hold-eraser', 'hold-eraser', 4), ('pickpocket', 'pickpocket', 4))
itn = (('cigar-smoke', 'cigar-smoke', 4), ('glower', 'glower', 4), ('speak', 'speak', 4))
rus = (('glower', 'glower', 4), ('pen-squirt', 'fountain-pen', 4))
ant = (('pickpocket', 'pickpocket', 4), ('glower', 'glower', 4))
sya = (('pickpocket', 'pickpocket', 4), ('glower', 'glower', 4))
djockey = (('pen-squirt', 'fountain-pen', 4), ('shredder', 'shredder', 4))
ptjockey = (('cigar-smoke', 'cigar-smoke', 4), ('pen-squirt', 'fountain-pen', 4))
jas = (('cigar-smoke', 'cigar-smoke', 4), ('pen-squirt', 'fountain-pen', 4))
tas = (('cigar-smoke', 'cigar-smoke', 4), ('pen-squirt', 'fountain-pen', 4))
fhu = (('cigar-smoke', 'cigar-smoke', 4), ('pen-squirt', 'fountain-pen', 4))
fsh = (('cigar-smoke', 'cigar-smoke', 4), ('pen-squirt', 'fountain-pen', 4))
fhj = (('cigar-smoke', 'cigar-smoke', 4), ('pen-squirt', 'fountain-pen', 4))
kdh = (('cigar-smoke', 'cigar-smoke', 4), ('pen-squirt', 'fountain-pen', 4))
dar = (('cigar-smoke', 'cigar-smoke', 4), ('pen-squirt', 'fountain-pen', 4))
nhy = (('cigar-smoke', 'cigar-smoke', 4), ('pen-squirt', 'fountain-pen', 4))
wrt = (('cigar-smoke', 'cigar-smoke', 4), ('pen-squirt', 'fountain-pen', 4))
auh = (('cigar-smoke', 'cigar-smoke', 4), ('pen-squirt', 'fountain-pen', 4))

# Pressbots
ppb = (('pickpocket', 'pickpocket', 4), ('hold-eraser', 'hold-eraser', 4), ('hold-pencil', 'hold-pencil', 4))
shb = (('pickpocket', 'pickpocket', 4), ('speak', 'speak', 4))
bsd = (('glower', 'glower', 4), ('speak', 'speak', 4), ('finger-wag', 'finger-wag', 4))
gms = (('rubber-stamp', 'rubber-stamp', 4), ('glower', 'glower', 4), ('speak', 'speak', 4))
sbg = (('effort', 'effort', 4), ('cigar-smoke', 'cigar-smoke', 4), ('pen-squirt', 'fountain-pen', 4))
hck = (('cigar-smoke', 'cigar-smoke', 4), ('pen-squirt', 'fountain-pen', 4))
ath =  (('pencil-sharpener', 'pencil-sharpener', 4), ('pen-squirt', 'pen-squirt', 4), ('hold-eraser', 'hold-eraser', 4), ('finger-wag', 'finger-wag', 4), ('hold-pencil', 'hold-pencil', 4))
ghw = (('speak', 'speak', 4), ('magic1', 'magic1', 4))
dcw = (('smile', 'smile', 4), ('quick-jump', 'jump', 4))
gzt = (('glower', 'glower', 4), ('quick-jump', 'jump', 4))
wnk = (('stomp', 'stomp', 4), ('quick-jump', 'jump', 4))
nsh = (('glower', 'glower', 4), ('quick-jump', 'jump', 4))
std = (('glower', 'glower', 4), ('smile', 'smile', 4), ('golf-club-swing', 'golf-club-swing', 4))
anc = (('speak', 'speak', 4), ('cigar-smoke', 'cigar-smoke', 4), ('golf-club-swing', 'golf-club-swing', 4))
jls = (('speak', 'speak', 4), ('cigar-smoke', 'cigar-smoke', 4), ('golf-club-swing', 'golf-club-swing', 4))
pbl = (('speak', 'speak', 4), ('cigar-smoke', 'cigar-smoke', 4), ('golf-club-swing', 'golf-club-swing', 4))
director = (('golf-club-swing', 'golf-club-swing', 4), ('speak', 'speak', 4), ('cigar-smoke', 'cigar-smoke', 4), ('neutral', 'rolled', 4), ('shot5', 'shot5', 4))
bcaster = (('neutral', 'rolled', 4), ('throttletwo', 'throttletwo', 4), ('shot5', 'shot5', 4), ('pen-squirt', 'fountain-pen', 4))
std2 = (('glower', 'glower', 4), ('smile', 'smile', 4), ('golf-club-swing', 'golf-club-swing', 4), ('neutral', 'rolled', 4), ('shot5', 'shot5', 4))
videog = (('snap', 'snap2', 4), ('neutral', 'rolled', 4), ('throttletwo', 'throttletwo', 4), ('shot5', 'shot5', 4), ('smile', 'smile', 4))
prt = (('speak', 'speak', 4), ('cigar-smoke', 'cigar-smoke', 4), ('golf-club-swing', 'golf-club-swing', 4))
pla = (('speak', 'speak', 4), ('cigar-smoke', 'cigar-smoke', 4), ('golf-club-swing', 'golf-club-swing', 4))
plk = (('speak', 'speak', 4), ('cigar-smoke', 'cigar-smoke', 4), ('golf-club-swing', 'golf-club-swing', 4))
plh = (('speak', 'speak', 4), ('cigar-smoke', 'cigar-smoke', 4), ('golf-club-swing', 'golf-club-swing', 4))
plg = (('speak', 'speak', 4), ('cigar-smoke', 'cigar-smoke', 4), ('golf-club-swing', 'golf-club-swing', 4))
plf = (('speak', 'speak', 4), ('cigar-smoke', 'cigar-smoke', 4), ('golf-club-swing', 'golf-club-swing', 4))
pld = (('speak', 'speak', 4), ('cigar-smoke', 'cigar-smoke', 4), ('golf-club-swing', 'golf-club-swing', 4))
pls = (('speak', 'speak', 4), ('cigar-smoke', 'cigar-smoke', 4), ('golf-club-swing', 'golf-club-swing', 4))
if not base.config.GetBool('want-new-cogs', 0):
    ModelDict = {'a': ('/models/char/suitA-', 4),
     'b': ('/models/char/suitB-', 4),
     'c': ('/models/char/suitC-', 3.5)}
    TutorialModelDict = {'a': ('/models/char/suitA-', 4),
     'b': ('/models/char/suitB-', 4),
     'c': ('/models/char/suitC-', 3.5)}
else:
    ModelDict = {'a': ('/models/char/tt_a_ene_cga_', 4),
     'b': ('/models/char/tt_a_ene_cgb_', 4),
     'c': ('/models/char/tt_a_ene_cgc_', 3.5)}
    TutorialModelDict = {'a': ('/models/char/tt_a_ene_cga_', 4),
     'b': ('/models/char/tt_a_ene_cgb_', 4),
     'c': ('/models/char/tt_a_ene_cgc_', 3.5)}
HeadModelDict = {'a': ('/models/char/suitA-', 4),
 'b': ('/models/char/suitB-', 4),
 'c': ('/models/char/suitC-', 3.5)}

SuitParts = ['phase_3.5/models/char/suitA-mod',
            'phase_3.5/models/char/suitB-mod',
            'phase_3.5/models/char/suitC-mod',
            'phase_4/models/char/suitA-heads',
            'phase_4/models/char/suitB-heads',
            'phase_3.5/models/char/suitC-heads']

Preloaded = {}

def loadModels():
    global Preloaded
    if not Preloaded:
        print 'Preloading suits...'

        def preload(task):
            for filepath in SuitParts:
                Preloaded[filepath] = loader.loadModel(filepath)
                Preloaded[filepath].flattenMedium()

            return task.done

        taskMgr.add(preload, 'preload-suit')

def loadTutorialSuit():
    loader.loadModel('phase_3.5/models/char/suitC-mod')
    loadDialog(1)

def loadSuits(level):
    loadDialog(level)

def unloadSuits(level):
    loadSuitModelsAndAnims(level, flag=0)
    unloadDialog(level)

def loadSuitModelsAndAnims(level, flag = 0):
    for key in ModelDict.keys():
        model, phase = ModelDict[key]
        if flag:
            filepath = 'phase_3.5' + model + 'mod'
            Preloaded[filepath] = loader.loadModel(filepath)
            filepath = 'phase_' + str(phase) + model + 'heads'
            Preloaded[filepath] = loader.loadModel(filepath)

def cogExists(filePrefix):
    searchPath = DSearchPath()
    if AppRunnerGlobal.appRunner:
        searchPath.appendDirectory(Filename.expandFrom('$TT_3_5_ROOT/phase_3.5'))
    else:
        basePath = os.path.expandvars('$TTMODELS') or './ttmodels'
        searchPath.appendDirectory(Filename.fromOsSpecific(basePath + '/built/phase_3.5'))
    filePrefix = filePrefix.strip('/')
    pfile = Filename(filePrefix)
    found = vfs.resolveFilename(pfile, searchPath)
    if not found:
        return False
    return True


def loadSuitAnims(suit, flag = 1):
    if suit in SuitDNA.suitHeadTypes:
        try:
            animList = eval(suit)
        except NameError:
            print(":Suit(warning): Failed to load suit animations!")
            animList = ()

    else:
        return -1
    for anim in animList:
        phase = 'phase_' + str(anim[2])
        filePrefix = ModelDict[bodyType][0]
        animName = filePrefix + anim[1]
        if flag:
            loader.loadModel(animName)
        else:
            loader.unloadModel(animName)

def setChatAbsolute(self, chatString, chatFlags, dialogue = None, interrupt = True):
    searchString = chatString.lower()
    if searchString.find(OTPLocalizer.DialogSpecial) >= 0:
        self.animHead = 'statement'
    elif searchString.find(OTPLocalizer.DialogExclamation) >= 0:
        self.animHead = 'grunt'
    elif searchString.find(OTPLocalizer.DialogQuestion) >= 0:
        self.animHead = 'question'
    else:
        stringLength = len(chatString)
        if stringLength <= OTPLocalizer.DialogLength1:
            self.animHead = 'grunt'
        elif stringLength <= OTPLocalizer.DialogLength2:
            self.animHead = 'murmur'
        elif stringLength <= OTPLocalizer.DialogLength3:
            self.animHead = 'statement'
        else:
            self.animHead = 'statement'
    self.nametag.setChat(chatString, chatFlags)
    self.playCurrentDialogue(dialogue, chatFlags, interrupt)
    for headPart in self.headParts: Sequence(
            ActorInterval(headPart, self.animHead),
            Func(headPart.loop, 'neutral%s' % ('-hurt' if self.healthCondition >= 10 else '',)) # You might want to change the healthCondition thing as it does not reflect the threshold of which you want the head to animate the hurt animation.
        ).start()


def loadDialog(level):
    if len(PrethinkerDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        PrethinkerDialogFiles = ['ttcc_ene_prethink_grunt',
         'ttcc_ene_prethink_murmur',
         'ttcc_ene_prethink_statement',
         'ttcc_ene_prethink_question',
         'ttcc_ene_prethink_grunt']

    global PrethinkerDialogueArray
    for file in PrethinkerDialogFiles:
        PrethinkerDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(PacesetterDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        PacesetterDialogFiles = ['ttcc_ene_psetter_grunt',
         'ttcc_ene_psetter_murmur',
         'ttcc_ene_psetter_statement',
         'ttcc_ene_psetter_question',
         'ttcc_ene_psetter_grunt']

    global PacesetterDialogueArray
    for file in PacesetterDialogFiles:
        PacesetterDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(HighRollerDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        HighRollerDialogFiles = ['ttcc_ene_hroller_grunt',
         'ttcc_ene_hroller_murmur',
         'ttcc_ene_hroller_statement',
         'ttcc_ene_hroller_question',
         'ttcc_ene_hroller_grunt']

    global HighRollerDialogueArray
    for file in HighRollerDialogFiles:
        HighRollerDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(CLODialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        CLODialogFiles = ['ttcc_ene_clo_grunt',
         'ttcc_ene_clo_murmur',
         'ttcc_ene_clo_statement',
         'ttcc_ene_clo_question',
         'ttcc_ene_clo_grunt']

    global CLODialogueArray
    for file in CLODialogFiles:
        CLODialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(FirestarterDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        FirestarterDialogFiles = ['ttcc_ene_fires_grunt',
         'ttcc_ene_fires_murmur',
         'ttcc_ene_fires_statement',
         'ttcc_ene_fires_question',
         'ttcc_ene_fires_grunt']

    global FirestarterDialogueArray
    for file in FirestarterDialogFiles:
        FirestarterDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(LitigatorDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        LitigatorDialogFiles = ['ttcc_ene_lgator_grunt',
         'ttcc_ene_lgator_murmur',
         'ttcc_ene_lgator_statement',
         'ttcc_ene_lgator_question',
         'ttcc_ene_lgator_grunt']

    global LitigatorDialogueArray
    for file in LitigatorDialogFiles:
        LitigatorDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(FemaleDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        FemaleDialogFiles = ['COG_VO_grunt_f',
         'COG_VO_murmur_f',
         'COG_VO_statement_f',
         'COG_VO_question_1_f',
         'COG_VO_grunt_f']

    global FemaleDialogueArray
    for file in FemaleDialogFiles:
        FemaleDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(CaseManagerDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        CaseManagerDialogFiles = ['ttcc_ene_caseman_grunt',
         'ttcc_ene_caseman_murmur',
         'ttcc_ene_caseman_statement',
         'ttcc_ene_caseman_question',
         'ttcc_ene_caseman_grunt']

    global CaseManagerDialogueArray
    for file in CaseManagerDialogFiles:
        CaseManagerDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(ScapegoatDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        ScapegoatDialogFiles = ['ttcc_ene_sgoat_grunt',
         'ttcc_ene_sgoat_murmur',
         'ttcc_ene_sgoat_statement',
         'ttcc_ene_sgoat_question',
         'ttcc_ene_sgoat_grunt']

    global ScapegoatDialogueArray
    for file in ScapegoatDialogFiles:
        ScapegoatDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(MajorPlayerDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        MajorPlayerDialogFiles = ['ttcc_ene_mplayer_grunt',
         'ttcc_ene_mplayer_murmur',
         'ttcc_ene_mplayer_statement',
         'ttcc_ene_mplayer_question',
         'ttcc_ene_mplayer_grunt']

    global MajorPlayerDialogueArray
    for file in MajorPlayerDialogFiles:
        MajorPlayerDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(DuckShufflerDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        DuckShufflerDialogFiles = ['ttcc_ene_duckshfl_grunt',
         'ttcc_ene_duckshfl_murmur',
         'ttcc_ene_duckshfl_statement',
         'ttcc_ene_duckshfl_question',
         'ttcc_ene_duckshfl_grunt']

    global DuckShufflerDialogueArray
    for file in DuckShufflerDialogFiles:
        DuckShufflerDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(PlutocratDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        PlutocratDialogFiles = ['ttcc_ene_pcrat_grunt',
                                   'ttcc_ene_pcrat_murmur',
                                   'ttcc_ene_pcrat_statement',
                                   'ttcc_ene_pcrat_question',
                                   'ttcc_ene_pcrat_grunt']

    global PlutocratDialogueArray
    for file in PlutocratDialogFiles:
        PlutocratDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(WitchHunterDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        WitchHunterDialogFiles = ['ttcc_ene_whunter_grunt',
                                   'ttcc_ene_whunter_murmur',
                                   'ttcc_ene_whunter_statement',
                                   'ttcc_ene_whunter_question',
                                   'ttcc_ene_whunter_grunt']

    global WitchHunterDialogueArray
    for file in WitchHunterDialogFiles:
        WitchHunterDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(RainmakerDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        RainmakerDialogFiles = ['ttcc_ene_rainmake_grunt',
                                   'ttcc_ene_rainmake_murmur',
                                   'ttcc_ene_rainmake_statement',
                                   'ttcc_ene_rainmake_question',
                                   'ttcc_ene_rainmake_grunt']

    global RainmakerDialogueArray
    for file in RainmakerDialogFiles:
        RainmakerDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(StenographerDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        StenographerDialogFiles = ['ttcc_ene_stenog_grunt',
                                   'ttcc_ene_stenog_murmur',
                                   'ttcc_ene_stenog_statement',
                                   'ttcc_ene_stenog_question',
                                   'ttcc_ene_stenog_grunt']

    global StenographerDialogueArray
    for file in StenographerDialogFiles:
        StenographerDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(ChairmanDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        ChairmanDialogFiles = ['ttcc_ene_chairman_grunt',
                                   'ttcc_ene_chairman_murmur',
                                   'ttcc_ene_chairman_statement',
                                   'ttcc_ene_chairman_question',
                                   'ttcc_ene_chairman_grunt']

    global ChairmanDialogueArray
    for file in ChairmanDialogFiles:
        ChairmanDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(OttomanDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        OttomanDialogFiles = ['ttcc_ene_ottoman_grunt',
                                   'ttcc_ene_ottoman_murmur',
                                   'ttcc_ene_ottoman_statement',
                                   'ttcc_ene_ottoman_question',
                                   'ttcc_ene_ottoman_grunt']

    global OttomanDialogueArray
    for file in OttomanDialogFiles:
        OttomanDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(CEODialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        CEODialogFiles = ['ttcc_ene_CEO_grunt',
                                   'ttcc_ene_CEO_murmur',
                                   'ttcc_ene_CEO_statement',
                                   'ttcc_ene_CEO_question',
                                   'ttcc_ene_CEO_grunt']

    global CEODialogueArray
    for file in CEODialogFiles:
        CEODialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(ChainsawDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        ChainsawDialogFiles = ['ttcc_ene_chainsaw_grunt',
                                   'ttcc_ene_chainsaw_murmur',
                                   'ttcc_ene_chainsaw_statement',
                                   'ttcc_ene_chainsaw_question',
                                   'ttcc_ene_chainsaw_grunt']

    global ChainsawDialogueArray
    for file in ChainsawDialogFiles:
        ChainsawDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(DOLADialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        DOLADialogFiles = ['ttcc_ene_dlao_grunt',
                                   'ttcc_ene_dlao_murmur',
                                   'ttcc_ene_dlao_statement',
                                   'ttcc_ene_dlao_question',
                                   'ttcc_ene_dlao_grunt']

    global DOLADialogueArray
    for file in DOLADialogFiles:
        DOLADialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(DOPADialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        DOPADialogFiles = ['ttcc_ene_dopa_grunt_skel',
                                   'ttcc_ene_dopa_murmur_skel',
                                   'ttcc_ene_dopa_statement_skel',
                                   'ttcc_ene_dopa_question_skel',
                                   'ttcc_ene_dopa_grunt_skel']

    global DOPADialogueArray
    for file in DOPADialogFiles:
        DOPADialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(DOLDDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        DOLDDialogFiles = ['ttcc_ene_dold_grunt',
                                   'ttcc_ene_dold_murmur',
                                   'ttcc_ene_dold_statement',
                                   'ttcc_ene_dold_question',
                                   'ttcc_ene_dold_grunt']

    global DOLDDialogueArray
    for file in DOLDDialogFiles:
        DOLDDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(TreekillerDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        TreekillerDialogFiles = ['ttcc_ene_treek_grunt',
                                   'ttcc_ene_treek_murmur',
                                   'ttcc_ene_treek_statement',
                                   'ttcc_ene_treek_question',
                                   'ttcc_ene_treek_grunt']

    global TreekillerDialogueArray
    for file in TreekillerDialogFiles:
        TreekillerDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(DOPRDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        DOPRDialogFiles = ['ttcc_ene_DOPR_grunt_skel',
                                   'ttcc_ene_DOPR_murmur_skel',
                                   'ttcc_ene_DOPR_statement_skel',
                                   'ttcc_ene_DOPR_question_skel',
                                   'ttcc_ene_DOPR_grunt_skel']

    global DOPRDialogueArray
    for file in DOPRDialogFiles:
        DOPRDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(DerrickHandDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        DerrickHandDialogFiles = ['ttcc_ene_derrhand_grunt',
                                   'ttcc_ene_derrhand_murmur',
                                   'ttcc_ene_derrhand_statement',
                                   'ttcc_ene_derrhand_question',
                                   'ttcc_ene_derrhand_grunt']

    global DerrickHandDialogueArray
    for file in DerrickHandDialogFiles:
        DerrickHandDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(DerrickSkeleDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        DerrickSkeleDialogFiles = ['ttcc_ene_derrhand_grunt_skel',
                                   'ttcc_ene_derrhand_murmur_skel',
                                   'ttcc_ene_derrhand_statement_skel',
                                   'ttcc_ene_derrhand_question_skel',
                                   'ttcc_ene_derrhand_grunt_skel']

    global DerrickSkeleDialogueArray
    for file in DerrickSkeleDialogFiles:
        DerrickSkeleDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(DerrickManDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        DerrickManDialogFiles = ['ttcc_ene_derrman_grunt',
                                   'ttcc_ene_derrman_murmur',
                                   'ttcc_ene_derrman_statement',
                                   'ttcc_ene_derrman_question',
                                   'ttcc_ene_derrman_grunt']

    global DerrickManDialogueArray
    for file in DerrickManDialogFiles:
        DerrickManDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(MultislackerDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        MultislackerDialogFiles = ['ttcc_ene_mslacker_grunt',
                                   'ttcc_ene_mslacker_murmur',
                                   'ttcc_ene_mslacker_statement',
                                   'ttcc_ene_mslacker_question',
                                   'ttcc_ene_mslacker_grunt']

    global MultislackerDialogueArray
    for file in MultislackerDialogFiles:
        MultislackerDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(BellringerDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        BellringerDialogFiles = ['ttcc_ene_bellring_grunt',
                                   'ttcc_ene_bellring_murmur',
                                   'ttcc_ene_bellring_statement',
                                   'ttcc_ene_bellring_question',
                                   'ttcc_ene_bellring_grunt']

    global BellringerDialogueArray
    for file in BellringerDialogFiles:
        BellringerDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(CountErfitDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        CountErfitDialogFiles = ['ttcc_ene_erfit_grunt',
                                   'ttcc_ene_erfit_murmur',
                                   'ttcc_ene_erfit_statement',
                                   'ttcc_ene_erfit_question',
                                   'ttcc_ene_erfit_grunt']

    global CountErfitDialogueArray
    for file in CountErfitDialogFiles:
        CountErfitDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(FeatherbedderDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        FeatherbedderDialogFiles = ['ttcc_ene_fbed_grunt',
                                   'ttcc_ene_fbed_murmur',
                                   'ttcc_ene_fbed_statement',
                                   'ttcc_ene_fbed_question',
                                   'ttcc_ene_fbed_grunt']

    global FeatherbedderDialogueArray
    for file in FeatherbedderDialogFiles:
        FeatherbedderDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(DeepDiverDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        DeepDiverDialogFiles = ['ttcc_ene_ddiver_grunt',
                                   'ttcc_ene_ddiver_murmur',
                                   'ttcc_ene_ddiver_statement',
                                   'ttcc_ene_ddiver_question',
                                   'ttcc_ene_ddiver_grunt']

    global DeepDiverDialogueArray
    for file in DeepDiverDialogFiles:
        DeepDiverDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(GatekeeperDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        GatekeeperDialogFiles = ['ttcc_ene_gatekeep_grunt',
                                   'ttcc_ene_gatekeep_murmur',
                                   'ttcc_ene_gatekeep_statement',
                                   'ttcc_ene_gatekeep_question',
                                   'ttcc_ene_gatekeep_grunt']

    global GatekeeperDialogueArray
    for file in GatekeeperDialogFiles:
        GatekeeperDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(MouthpieceDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        MouthpieceDialogFiles = ['ttcc_ene_mouthp_grunt',
         'ttcc_ene_mouthp_murmur',
         'ttcc_ene_mouthp_statement',
         'ttcc_ene_mouthp_question',
         'ttcc_ene_mouthp_grunt']

    global MouthpieceDialogueArray
    for file in MouthpieceDialogFiles:
        MouthpieceDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(ChainsawORDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        ChainsawORDialogFiles = ['ttcc_ene_chainsaw_grunt_or',
                                 'ttcc_ene_chainsaw_murmur_or',
                                 'ttcc_ene_chainsaw_statement_or',
                                 'ttcc_ene_chainsaw_question_or',
                                 'ttcc_ene_chainsaw_grunt_or']

    global ChainsawORDialogueArray
    for file in ChainsawORDialogFiles:
        ChainsawORDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(ReddDialogArray) > 0:
            return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        ReddDialogFiles = ['REDD_grunt',
                                      'REDD_murmur',
                                      'REDD_VO_statement',
                                      'REDD_VO_question',
                                      'REDD_grunt']

    global ReddDialogueArray
    for file in ReddDialogFiles:
        ReddDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(DeskJockeyDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        DeskJockeyDialogFiles = ['ttcc_ene_djockey_grunt',
         'ttcc_ene_djockey_murmur',
         'ttcc_ene_djockey_statement',
         'ttcc_ene_djockey_question',
         'ttcc_ene_djockey_grunt']

    global DeskJockeyDialogueArray
    for file in DeskJockeyDialogFiles:
        DeskJockeyDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(SkelecogDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        SkelecogDialogFiles = ['COG_VO_grunt_skel',
         'COG_VO_murmur_skel',
         'COG_VO_statement_skel',
         'COG_VO_question_skel',
         'COG_VO_grunt_skel']

    global SkelecogDialogueArray
    for file in SkelecogDialogFiles:
        SkelecogDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(SkelecogDialogFemaleArray) > 0:
        return
    else:
        loadPath = 'phase_5/audio/dial/'
        SkelecogDialogFemaleFiles = ['COG_VO_grunt_skel_f',
         'COG_VO_murmur_skel_f',
         'COG_VO_statement_skel_f',
         'COG_VO_question_skel_f',
         'COG_VO_grunt_skel_f']

    global SkelecogDialogueFemaleArray
    for file in SkelecogDialogFemaleFiles:
        SkelecogDialogFemaleArray.append(base.loadSfx(loadPath + file + '.ogg'))

    if len(SuitDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        SuitDialogFiles = ['COG_VO_grunt',
         'COG_VO_murmur',
         'COG_VO_statement',
         'COG_VO_question',
         'COG_VO_grunt']
        for file in SuitDialogFiles:
            SuitDialogArray.append(base.loadSfx(loadPath + file + '.ogg'))

        PrethinkerDialogArray.append(SuitDialogArray[2])
        PrethinkerDialogArray.append(SuitDialogArray[2])
        SuitDialogArray.append(SuitDialogArray[2])
        SuitDialogArray.append(SuitDialogArray[2])



def loadSkelDialog():
    global SkelSuitDialogArray
    if len(SkelSuitDialogArray) > 0:
        return
    else:
        grunt = loader.loadSfx('phase_5/audio/sfx/Skel_COG_VO_grunt.ogg')
        murmur = loader.loadSfx('phase_5/audio/sfx/Skel_COG_VO_murmur.ogg')
        statement = loader.loadSfx('phase_5/audio/sfx/Skel_COG_VO_statement.ogg')
        question = loader.loadSfx('phase_5/audio/sfx/Skel_COG_VO_question.ogg')
        SkelSuitDialogArray = [grunt,
         murmur,
         statement,
         question,
         grunt,
         grunt]


def unloadDialog(level):
    global SuitDialogArray
    global PrethinkerDialogArray
    global PacesetterDialogArray
    global CLODialogArray
    global FirestarterDialogArray
    global LitigatorDialogArray
    global CaseManagerDialogArray
    global ScapegoatDialogArray
    global MajorPlayerDialogArray
    global DuckShufflerDialogArray
    global PlutocratDialogArray
    global WitchHunterDialogArray
    global RainmakerDialogArray
    global ChainsawDialogArray
    global OttomanDialogArray
    global CEODialogArray
    global ChairmanDialogArray
    global DOLADialogArray
    global DOLDDialogArray
    global DOPADialogArray
    global DOPRDialogArray
    global DerrickHandDialogArray
    global DerrickSkeleDialogArray
    global DerrickManDialogArray
    global MultislackerDialogArray
    global BellringerDialogArray
    global CountErfitDialogArray
    global FeatherbedderDialogArray
    global DeepDiverDialogArray
    global GatekeeperDialogArray
    global MouthpieceDialogArray
    global ReddDialogArray
    global DeskJockeyDialogArray
    global ChainsawORDialogArray
    global SkelecogDialogArray
    global SkelecogDialogFemaleArray
    global HighRollerDialogArray
    global StenographerDialogArray
    global FemaleDialogArray
    global TreekillerDialogArray
    SuitDialogArray = []
    PrethinkerDialogArray = []
    PacesetterDialogArray = []
    CLODialogArray = []
    FirestarterDialogArray = []
    LitigatorDialogArray = []
    CaseManagerDialogArray = []
    ScapegoatDialogArray = []
    MajorPlayerDialogArray = []
    DuckShufflerDialogArray = []
    PlutocratDialogArray = []
    WitchHunterDialogArray = []
    RainmakerDialogArray = []
    ChairmanDialogArray = []
    OttomanDialogArray = []
    CEODialogArray = []
    ChainsawDialogArray = []
    DOLADialogArray = []
    DOPADialogArray = []
    DOLDDialogArray = []
    DOPRDialogArray = []
    DerrickHandDialogArray = []
    DerrickSkeleDialogArray = []
    DerrickManDialogArray = []
    MultislackerDialogArray = []
    BellringerDialogArray = []
    CountErfitDialogArray = []
    FeatherbedderDialogArray = []
    DeepDiverDialogArray = []
    GatekeeperDialogArray = []
    MouthpieceDialogArray = []
    ReddDialogArray = []
    DeskJockeyDialogArray = []
    ChainsawORDialogArray = []
    SkelecogDialogArray = []
    SkelecogDialogFemaleArray = []
    HighRollerDialogArray = []
    StenographerDialogArray = []
    FemaleDialogArray = []
    TreekillerDialogArray = []


def unloadSkelDialog():
    global SkelSuitDialogArray
    SkelSuitDialogArray = []


def attachSuitHead(node, suitName):
    suitIndex = SuitDNA.suitHeadTypes.index(suitName)
    suitDNA = SuitDNA.SuitDNA()
    suitDNA.newSuit(suitName)
    suit = Suit()
    suit.setDNA(suitDNA)
    headParts = suit.getHeadParts()
    animatedHeadParts = suit.getAnimatedHeadParts()
    head = node.attachNewNode('head')
    for part in headParts:
        copyPart = part.copyTo(head)
        copyPart.setDepthTest(1)
        copyPart.setDepthWrite(1)


    suit = None
    p1 = Point3()
    p2 = Point3()
    head.calcTightBounds(p1, p2)
    d = p2 - p1
    biggest = max(d[0], d[2])
    column = suitIndex % SuitDNA.suitsPerDept
    s = (0.2 + column / 100.0) / biggest
    pos = -0.14 + (SuitDNA.suitsPerDept - column - 1) / 135.0
    head.setPosHprScale(0, 0, pos, 180, 0, 0, s, s, s)
    return head


class Suit(Avatar.Avatar):
    notify = DirectNotifyGlobal.directNotify.newCategory('Suit')
    __module__ = __name__
    healthColors = (Vec4(0, 1, 0.078, 1),
                    Vec4(0.388, 1, 0, 1),
                    Vec4(0.686, 1, 0, 1),
                    Vec4(0.882, 1, 0, 1),
                    Vec4(0.988, 1, 0, 1),
                    Vec4(1, 0.831, 0, 1),
                    Vec4(1, 0.714, 0, 1),
                    Vec4(1, 0.533, 0, 1.0),
                    Vec4(1, 0, 0, 1),
                    Vec4(1, 0, 0, 1),
                    Vec4(0.3, 0.3, 0.3, 1), #out
                    Vec4(1, 0, 0, 1),
                    Vec4(0.0, 1.0, 1.0, 1),  # overheal
                    Vec4(0.553, 0, 1, 1),  # overcharge
                    Vec4(1, 0.6, 0.89, 1),  # 14 pink silhouette
                    Vec4(0, 0.361, 1, 1),
                    Vec4(1, 1, 1, 1),  # 15 blue silhouette
                    Vec4(186 / 255, 82 / 255, 1, 1),
                    Vec4(0.702, 0, 1, 1),
                    Vec4(1, 1, 1, 1),
                    Vec4(1, 0, 0.906, 1)) # 18 white
    healthGlowColors = (Vec4(0, 1, 0.078, 1),
                    Vec4(0.388, 1, 0, 1),
                    Vec4(0.686, 1, 0, 1),
                    Vec4(0.882, 1, 0, 1),
                    Vec4(0.988, 1, 0, 1),
                    Vec4(1, 0.831, 0, 1),
                    Vec4(1, 0.714, 0, 1),
                    Vec4(1, 0.533, 0, 1.0),
                    Vec4(1, 0, 0, 1),
                    Vec4(1, 0, 0, 1),
                    Vec4(0, 0, 0, 0), #out
                    Vec4(1, 0, 0, 1),
                    Vec4(0.0, 1.0, 1.0, 1),  # overheal
                    Vec4(0.553, 0, 1, 1),  # overcharge
                    Vec4(1, 0.6, 0.89, 1),  # 14 pink silhouette
                    Vec4(0, 0.361, 1, 1),
                    Vec4(1, 1, 1, 1),  # 15 blue silhouette
                    Vec4(186 / 255, 82 / 255, 1, 1),
                        Vec4(0.702, 0, 1, 1),
                        Vec4(1, 1, 1, 1),
                        Vec4(1, 0, 0.906, 1)
                        ) #18 white
    medallionColors = {'c': Vec4(0.863, 0.776, 0.769, 1.0),
     's': Vec4(0.843, 0.745, 0.745, 1.0),
     'l': Vec4(0.749, 0.776, 0.824, 1.0),
     'm': Vec4(0.749, 0.769, 0.749, 1.0),
     'g': Vec4(0.706, 0.773, 0.812, 1.0),
     't': Vec4(0.847, 0.792, 0.851, 1.0),
     'p': Vec4(0.643, 0.51, 0.525, 1.0)
                       }

    def __init__(self):
        try:
            self.Suit_initialized
            return
        except:
            self.Suit_initialized = 1

        Avatar.Avatar.__init__(self)
        self.setFont(ToontownGlobals.getSuitFont())
        self.setPlayerType(NametagGlobals.CCSuit)
        self.setPickable(1)
        self.leftHand = None
        self.rightHand = None
        self.shadowJoint = None
        self.nametagJoint = None
        self.headParts = []
        self.animatedHeadParts = []
        self.healthBar = None
        self.healthBarDisplay = None
        self.healthCondition = 0
        self.isDisguised = 0
        self.isWaiter = 0
        self.isGovernaught = 0
        self.isInsured = 0
        self.isAmbassadorPhase3 = 0
        self.isContracted = 0
        self.isExecutive = 0
        self.isSued = 0
        self.isAngry = 0
        self.isRevived = 0
        self.isLaserRevived = 0
        self.isDanceSession = 0
        self.isImmortal = 0
        self.isSoakImmune = 0
        self.isShielding = 0
        self.isManager = 0
        self.isHeavyRain = 0
        self.isFreezingRain = 0
        self.isStormCell = 0
        self.isOilRain = 0
        self.isFrozen = 0
        self.isImmune = 0
        self.isDamageUp = 0
        self.isDamageReduction = 0
        self.isSoaked = 0
        self.isSyphon = 0
        self.isVulnerable = 0
        self.isEnraged = 0
        self.isAbsorbing = 0
        self.isRental = 0
        self.isLureResist = 0
        self.isTarget = 0
        self.splats = set()

    def delete(self):
        try:
            self.Suit_deleted
            return
        except:
            self.Suit_deleted = 1

        if self.leftHand:
            self.leftHand.removeNode()
            self.leftHand = None

        if self.rightHand:
            self.rightHand.removeNode()
            self.rightHand = None

        if self.shadowJoint:
            self.shadowJoint.removeNode()
            self.shadowJoint = None

        if self.nametagJoint:
            self.nametagJoint.removeNode()
            self.nametagJoint = None

        #for part in self.headParts:
            #part.removeNode()

        self.headParts = []
        self.animatedHeadParts = []
        self.removeHealthBar()
        self.removeHealthBarDisplay()
        Avatar.Avatar.delete(self)

    def setHeight(self, height):
        Avatar.Avatar.setHeight(self, height)
        self.nametag3d.setPos(0, 0, height + 1.0)

    def getRadius(self):
        return 2

    def setDNAString(self, dnaString):
        self.dna = SuitDNA.SuitDNA()
        self.dna.makeFromNetString(dnaString)
        self.setDNA(self.dna)

    def setDNA(self, dna):
        if self.style:
            pass
        else:
            self.style = dna
            self.generateSuit()
            self.initializeDropShadow()
            self.initializeNametag3d()

    def generateSuit(self):
        dna = self.style
        self.headParts = []
        self.animatedHeadParts = []
        self.headColor = None
        self.headTexture = None
        self.loseActor = None
        self.zapActor = None
        self.isSkeleton = 0
        self.isFired = 0
        self.isDazed = 0
        self.isLured = 0
        self.isPhase3 = 0
        self.isDesperation = 0
        self.isImmune = 0
        self.isLitigationManager = 0
        self.isDead = 0
        self.isSoakImmune = 0
        self.isRevive = 0
        self.isDamageReduction = 0
        self.isChainsawPhase2 = 0
        self.isChainsawPhase3 = 0
        self.isLureImmune = 0
        self.isEnraged = 0
        self.isAngry = 0
        self.isOttomanPhase2 = 0
        self.isChairmanPhase2 = 0
        self.isShielding = 0
        self.chainPos = 0
        self.isAbsorbing = 0
        self.isDamageUp = 0
        self.isSoaked = 0
        self.isVirtual = 0
        self.isBookkeeping = 0
        self.headInterval = None
        self.pulseInterval = None
        self.blinkInterval = None
        self.suitColorTrack = None
        self.partTracks = None
        self.extraAttack = 0
        self.damageMult = 0
        self.lureRounds = 0
        self.vulnerability = 0
        self.rageBuilding = 0
        self.powerhouseRotation = 0
        self.statusEffects = 0

        # Bossbots
        if dna.name == 'f':
            self.scale = 4.0 / cSize
            self.handColor = SuitDNA.corpPolyColor
            self.generateBody()
            #self.generateFlunky()
            self.generateHead2('flunky')
            self.generateHead2('glasses')
            self.setHeight(4.88)
        elif dna.name == 'p':
            self.scale = 3.35 / bSize
            self.handColor = SuitDNA.corpPolyColor
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
            self.scale = 2.5 / cSize
            self.handColor = SuitDNA.corpPolyColor
            self.generateFemaleBody()
            self.generateHead2('micromanager')
            texture = loader.loadTexture('phase_3.5/maps/tutorial_suits_palette_3cmla_1.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(3.25)
        elif dna.name == 'blh':
            self.scale = 5.0 / cSize
            self.handColor = VBase4(0.878, 0.733, 0.71, 1)
            self.generateBody()
            self.generateHead2('Blowhard')
            texture = loader.loadTexture('phase_3.5/maps/ttrm_t_ene_head_blowhard.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.25)
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
        elif dna.name == 'mldr':
            self.scale = 6.0 / aSize
            self.handColor = VBase4(0.776, 0.122, 0.157, 1)
            self.generateBody()
            self.generateHead2('ear01')
            self.generateHead2('head')
            self.generateHead2('ear03')
            self.generateHead2('ear04')
            self.generateHead2('ear02')
            self.generateHead2('antenna_stick')
            self.generateHead2('antenna_ball')
            self.generateHead2('eye_mouth')
            self.generateHead2('pupils')
            self.setHeight(7.5)
        elif dna.name == 'hh':
            self.scale = 6.5 / aSize
            self.handColor = SuitDNA.corpPolyColor
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
        elif dna.name == 'cr':
            self.scale = 6.75 / cSize
            self.handColor = SuitDNA.corpPolyColor
            self.generateBody()
            self.generateHead2('flunky')
            texture = loader.loadTexture('phase_4/maps/corporate-raider.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.23)
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
            self.handColor = VBase4(0.749, 0.859, 0.525, 1.0)
            self.generateBody()
            self.generateHead2('bigcheese')
            texture = loader.loadTexture('phase_3.5/maps/suit-heads_palette_3cmla_1.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(9.34)
        elif dna.name == 'autocad':
            self.scale = 4.5 / aSize
            self.handColor = VBase4(1, 1, 1, 1)
            self.makeSkeletonManager()
            self.setHeight(6.0)
        elif dna.name == 'clubpres':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.608, 0.525, 0.431, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('clubpresident', animated=True)
            self.setHeight(8.7)
        elif dna.name == 'derrman':
            self.scale = 4.5 / aSize
            self.handColor = VBase4(0.573, 0.384, 0.204, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('derrickman', animated=True)
            self.setHeight(6.0)
        elif dna.name == 'derrhand':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('derrickhand', animated=True)
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_derrickhand.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(9.0)
            self.setTransparency(1)
        elif dna.name == 'mplayer':
            self.scale = 7.3 / aSize
            self.handColor = VBase4(1, 1, 1, 1)
            self.generateBody()
            self.makeMajorPlayer()
            self.generateHead3('majorplayer', animated=True)
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_majorplayer.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(10.0)
            self.setTransparency(1)
        elif dna.name == 'fires':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.894, 0.235, 0.043, 1)
            self.generateBody()
            self.makeFirestarter()
            self.generateHead3('firestarter', animated=True)
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_firestarter.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(9.5)
            self.setTransparency(1)
        elif dna.name == 'fbed':
            self.scale = 6.2 / cSize
            self.handColor = VBase4(0.235, 0.149, 0.125, 1)
            self.generateBody()
            self.makeFeatherbedder()
            self.generateHead3('featherbedder', animated=True)
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_featherbedder.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.0)
            self.setTransparency(1)
        elif dna.name == 'mplayer2':
            self.scale = 7.3 / aSize
            self.handColor = VBase4(1, 1, 1, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('majorplayer', animated=True)
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_majorplayer.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(10.0)
            self.setTransparency(1)
        elif dna.name == 'chainsaw':
            self.scale = 7.5 / aSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.generateBody()
            self.makeChainsaw()
            self.generateHead3('chainsaw', animated=True)
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_chainsaw_a.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(11.0)
            self.setTransparency(1)
        elif dna.name == 'chainsaw2':
            self.scale = 7.5 / aSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.generateBody()
            self.makeChainsaw()
            self.generateHead3('chainsaw_b', animated=True)
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_chainsaw.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(11.0)
            self.setTransparency(1)
        elif dna.name == 'phouse':
            self.scale = 5.0 / aSize
            self.handColor = VBase4(0.686, 0.569, 0.439, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('circuitbreaker', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_circuitbreaker2.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.66)
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
            self.setTransparency(1)
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
            self.setTransparency(1)
        elif dna.name == 'ambass':
            self.scale = 7.3 / aSize
            self.handColor = VBase4(0.682, 0.588, 0.482, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('prethinker', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_prethinker.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(9.1)
            self.setTransparency(1)

        # Lawbots
        elif dna.name == 'bf':
            self.scale = 4.2 / cSize
            self.handColor = SuitDNA.legalPolyColor
            self.generateBody()
            self.generateHead3('bottom_feeder', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_bottom_feeder.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.6)
        elif dna.name == 'b':
            self.scale = 4.25 / bSize
            self.handColor = VBase4(1, 1, 1, 1)
            self.generateBody()
            self.generateHead3('bloodsucker', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_bloodsucker.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.63)
        elif dna.name == 'pf':
            self.scale = 4.0 / bSize
            self.handColor = SuitDNA.legalPolyColor
            self.generateBody()
            self.generateHead3('pettifogger', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_pettifogger.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.6)
        elif dna.name == 'dt':
            self.scale = 4.25 / aSize
            self.handColor = SuitDNA.legalPolyColor
            self.generateBody()
            self.generateHead3('doubletalker', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_doubletalker.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.63)
        elif dna.name == 'cv':
            self.scale = 4.75 / aSize
            self.handColor = VBase4(0.318, 0.333, 0.431, 1)
            self.generateBody()
            self.generateHead3('conveyancer', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_conveyancer.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.generateHead2('conveyancer_belt')
            self.setHeight(6.4)
        elif dna.name == 'ac':
            self.scale = 4.2 / bSize
            self.handColor = SuitDNA.legalPolyColor
            self.generateBody()
            self.generateHead3('ambulance_chaser', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_ambulance_chaser.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.1)
        elif dna.name == 'nn':
            self.scale = 4.75 / cSize
            self.handColor = VBase4(0.255, 0.318, 0.549, 1)
            self.generateFemaleBody()
            self.generateHead3('needlenose', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_needlenose.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.5)
        elif dna.name == 'bs':
            self.scale = 5.0 / bSize
            self.handColor = VBase4(0.647, 0.639, 0.788, 1)
            self.generateBody()
            self.generateHead3('backstabber', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_backstabber.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.25)
        elif dna.name == 'ad':
            self.scale = 5.5 / cSize
            self.handColor = VBase4(0.098, 0.098, 0.153, 1)
            self.generateBody()
            self.generateHead3('advocate', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_advocate.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.0)
        elif dna.name == 'sd':
            self.scale = 5.65 / bSize
            self.handColor = VBase4(0.678, 0.91, 0.808, 1)
            self.generateBody()
            self.generateHead3('spin_doctor', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_spin_doctor.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.9)
        elif dna.name == 'sh':
            self.scale = 5.65 / bSize
            self.handColor = VBase4(0.647, 0.639, 0.788, 1)
            self.generateFemaleBody()
            self.generateHead3('shyster', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_shyster.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.4)
        elif dna.name == 'le':
            self.scale = 6.8 / aSize
            self.handColor = VBase4(0.25, 0.25, 0.5, 1.0)
            self.generateBody()
            self.generateHead3('legal_eagle', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_legal_eagle.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.2)
        elif dna.name == 'br':
            self.scale = 6.9 / aSize
            self.handColor = VBase4(0.784, 0.816, 0.847, 1)
            self.generateBody()
            self.generateHead3('barrister', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_barrister.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.3)
        elif dna.name == 'bw':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.573, 0.557, 0.761, 1)
            self.generateBody()
            self.generateHead3('bigwig', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_big_wig.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.69)
        elif dna.name == 'whistleb':
            self.scale = 4.5 / aSize
            self.handColor = VBase4(0.722, 0.757, 0.784, 1)
            self.generateFemaleBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/whistleblower.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.makeExecutive()
            self.setHeight(6.0)
        elif dna.name == 'clerk':
            self.scale = 7.2 / bSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.makeSkeletonManager()
            self.setHeight(8.7)
        elif dna.name == 'arbit':
            self.scale = 7.2 / aSize
            self.handColor = VBase4(0.69, 0.678, 0.765, 1)
            self.generateBody()
            self.generateHead3('clo', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_clo.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.makeExecutive()
            self.setHeight(8.7)
        elif dna.name == 'judy':
            self.scale = 4.5 / cSize
            self.handColor = VBase4(0.361, 0.435, 0.694, 1)
            self.generateFemaleBody()
            self.makeExecutive()
            self.generateHead3('judy', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_judy.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.5)
        elif dna.name == 'mouthp':
            self.scale = 5.0 / bSize
            self.handColor = VBase4(0.42, 0.502, 0.62, 1)
            self.generateFemaleBody()
            self.makeExecutive()
            self.generateHead3('mouthpiece', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_mouthpiece.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.8)
        elif dna.name == 'rainmake':
            self.scale = 5.5 / bSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.generateLongcoatBody()
            self.generateHead3('rainmaker', animated=True)
            self.setHeight(7.5)
            self.setTransparency(1)
        elif dna.name == 'whunter':
            self.scale = 6.0 / aSize
            self.handColor = VBase4(0.49, 0.494, 0.675, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('witchhunter', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_witchhunter.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.0)
            self.setTransparency(1)
        elif dna.name == 'erclaim':
            self.scale = 6.7 / bSize
            self.handColor = VBase4(1, 1, 1, 1)
            self.generateBody()
            self.makeCountErclaim()
            self.generateHead3('counterclaim', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_counterclaim1.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.69)
            self.setTransparency(1)
        elif dna.name == 'redd':
            self.scale = 6.2 / bSize
            self.handColor = VBase4(1, 1, 1, 1)
            self.generateBody()
            self.makeRedd()
            self.generateHead3('redd', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_redd.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.69)
            self.setTransparency(1)
        elif dna.name == 'wsi':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.makeSkeletonManager()
            self.setHeight(8.69)
        elif dna.name == 'sgoat':
            self.scale = 5.2 / bSize
            self.handColor = VBase4(0.486, 0.522, 0.686, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('scapegoat', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_scapegoat.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.8)
            self.makeShielding()
        elif dna.name == 'caseman':
            self.scale = 6.9 / aSize
            self.handColor = VBase4(0.294, 0.208, 0.149, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('casemanager', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_casemanager.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.6)
            self.setTransparency(1)
        elif dna.name == 'stenog':
            self.scale = 7.1 / aSize
            self.handColor = VBase4(0.322, 0.369, 0.525, 1)
            self.generateFemaleBody()
            self.makeExecutive()
            self.makeLitigationManager()
            self.generateHead3('stenographer', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_stenographer.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(10.0)
            self.setTransparency(1)
        elif dna.name == 'lgator':
            self.scale = 7.2 / aSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.generateBody()
            self.makeExecutive()
            self.makeLitigationManager()
            self.generateHead3('litigator', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_litigator.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setTransparency(1)
            self.setHeight(9.4)

        # Cashbots
        elif dna.name == 'sc':
            self.scale = 3.0 / cSize
            self.handColor = SuitDNA.moneyPolyColor
            self.generateBody()
            self.generateHead2('coldcaller')
            self.setHeight(4.5)
        elif dna.name == 'pp':
            self.scale = 3.55 / aSize
            self.handColor = VBase4(0.686, 0.212, 0.18, 1.0)
            self.generateBody()
            self.generateHead2('pennypincher')
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
            self.handColor = SuitDNA.moneyPolyColor
            self.generateBody()
            self.generateHead2('tightwad')
            self.setHeight(5.41)
        elif dna.name == 'sw':
            self.scale = 4.34 / aSize
            self.handColor = SuitDNA.boardPolyColor
            self.generateBody()
            self.generateHead2('pennypincher')
            texture = loader.loadTexture('phase_3.5/maps/swindler.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.45)
        elif dna.name == 'bc':
            self.scale = 4.4 / bSize
            self.handColor = SuitDNA.moneyPolyColor
            self.generateBody()
            self.generateHead2('beancounter')
            self.setHeight(5.95)
        elif dna.name == 'fct':
            self.scale = 5.5 / cSize
            self.handColor = VBase4(0.776, 0.831, 0.812, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/fatcat.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.75)
        elif dna.name == 'nc':
            self.scale = 5.25 / aSize
            self.handColor = SuitDNA.moneyPolyColor
            self.generateFemaleBody()
            self.generateHead2('numbercruncher')
            texture = loader.loadTexture('phase_3.5/maps/number_cruncher.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.22)
        elif dna.name == 'gld':
            self.scale = 6.5 / bSize
            self.handColor = VBase4(0.922, 0.682, 0.149, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/GoldenGoose_GoldenGooseFinal.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.5)
        elif dna.name == 'mb':
            self.scale = 5.7 / cSize
            self.handColor = SuitDNA.moneyPolyColor
            self.generateBody()
            self.generateHead2('moneybags')
            texture = loader.loadTexture('phase_3.5/maps/tutorial_suits_palette_3cmla_1.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.2)
        elif dna.name == 'trs':
            self.scale = 6.5 / aSize
            self.handColor = VBase4(0.592, 0.663, 0.627, 1)
            self.generateBody()
            self.generateHead2('yesman')
            texture = loader.loadTexture('phase_3.5/maps/cheapskate.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.5)
        elif dna.name == 'ls':
            self.scale = 6.5 / bSize
            self.handColor = SuitDNA.moneyPolyColor
            self.generateBody()
            self.generateHead2('loanshark')
            texture = loader.loadTexture('phase_3.5/maps/suit-heads_palette_3cmla_2.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.58)
        elif dna.name == 'bfh':
            self.scale = 7.5 / cSize
            self.handColor = VBase4(0.659, 0, 0, 1)
            self.generateFemaleBody()
            self.generateHead2('bigfish')
            self.setHeight(10.7)
        elif dna.name == 'rb':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.655, 0.769, 0.725, 1)
            self.generateBody()
            self.generateHead2('yesman')
            texture = loader.loadTexture('phase_4/maps/robber-baron.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.95)
        elif dna.name == 'ovt':
            self.scale = 6.0 / aSize
            self.handColor = VBase4(0.125, 0.125, 0.125, 1)
            self.generateBody()
            self.generateHead2('overtime')
            self.makeExecutive()
            texture = loader.loadTexture('phase_3.5/maps/ttoff_t_ene_overtime_palette_4amlc_1.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.9)
        elif dna.name == 'supervis':
            self.scale = 7.0 / cSize
            self.handColor = VBase4(0.286, 0.29, 0.286, 1)
            self.makeSkeletonManager()
            self.setHeight(9.0)
        elif dna.name == 'duckshfl':
            self.scale = 5.0 / bSize
            self.handColor = VBase4(0.714, 0.118, 0.055, 1)
            self.generateBody()
            self.makeDuckShuffler()
            self.generateHead3('duckshuffler', animated=True)
            self.setHeight(7.0)
        elif dna.name == 'treek':
            self.scale = 5.5 / cSize
            self.handColor = VBase4(0.647, 0.796, 0.627, 1)
            self.generateBody()
            self.makeTreekiller()
            self.generateHead3('treekiller', animated=True)
            self.setHeight(7.5)
        elif dna.name == 'styx':
            self.scale = 5.5 / cSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.makeSkeletonManager()
            self.setHeight(6.97)
        elif dna.name == 'nix':
            self.scale = 6.25 / bSize
            self.handColor = VBase4(0.529, 0.455, 0.369, 1)
            self.makeSkeletonManager()
            self.setHeight(7.5)
        elif dna.name == 'hydra':
            self.scale = 6.75 / cSize
            self.handColor = VBase4(0.5, 1, 0, 1.0)
            self.makeSkeletonManager()
            self.setHeight(8.23)
        elif dna.name == 'kerberos':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.makeSkeletonManager()
            self.setHeight(8.95)
        elif dna.name == 'charon':
            self.scale = 5.45 / aSize
            self.handColor = VBase4(0.286, 0.29, 0.286, 1)
            self.makeSkeletonManager()
            self.setHeight(7.22)
        elif dna.name == 'pcrat':
            self.scale = 3.5 / cSize
            self.handColor = VBase4(0.702, 0.776, 0.788, 1)
            self.generateBody()
            self.makePlutocrat()
            self.generateHead3('plutocrat', animated=True)
            self.setHeight(5.0)
            self.setTransparency(1)
        elif dna.name == 'hroller':
            self.scale = 7.5 / aSize
            self.handColor = VBase4(0.835, 0.843, 0.847, 1)
            self.generateHighRollerBodyWhite()
            self.generateHead3('highroller', animated=True)
            self.setHeight(10.0)
            self.setTransparency(1)
            self.makeImmortal()
        elif dna.name == 'erfit':
            self.scale = 7.2 / aSize
            self.handColor = VBase4(1, 1, 1, 1.0)
            self.generateBody()
            self.makeCountErfit()
            self.generateHead3('counterclaim', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_counterclaim.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(9.0)
        elif dna.name == 'hrollers':
            self.scale = 7.5 / aSize
            self.handColor = VBase4(0.835, 0.843, 0.847, 1)
            self.generateHighRollerBodyWhite()
            self.generateHead3('highroller', animated=True)
            self.makeVirtual()
            self.setHeight(10.0)
            self.setTransparency(1)
        elif dna.name == 'hroller2':
            self.scale = 7.5 / aSize
            self.handColor = VBase4(0.835, 0.843, 0.847, 1)
            self.generateHighRollerBody()
            self.makeHighRoller()
            self.generateHead3('highroller', animated=True)
            self.setHeight(10.0)
            self.setTransparency(1)

        # Sellbots
        elif dna.name == 'cc':
            self.scale = 3.5 / cSize
            self.handColor = VBase4(0, 0.024, 0.941, 1)
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
        elif dna.name == 'cn':
            self.scale = 4.0 / bSize
            self.handColor = VBase4(1, 1, 1, 1)
            self.generateBody()
            self.generateHead2('connoisseur_hat')
            self.generateHead2('connoisseur_monocle')
            self.generateHead2('connoisseur_head')
            self.setHeight(5.55)
        elif dna.name == 'nd':
            self.scale = 4.35 / aSize
            self.handColor = SuitDNA.salesPolyColor
            self.generateFemaleBody()
            self.generateHead2('numbercruncher')
            texture = loader.loadTexture('phase_3.5/maps/name-dropper.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.98)
        elif dna.name == 'dc':
            self.scale = 4.75 / aSize
            self.handColor = VBase4(0.906, 0.906, 0.933, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/doublecross.png')
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
        elif dna.name == 'fcs':
            self.scale = 5.5 / aSize
            self.handColor = VBase4(0.302, 0.227, 0.357, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/forecaster.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.1)
        elif dna.name == 'ms':
            self.scale = 4.75 / bSize
            self.handColor = VBase4(0.965, 0.859, 0.831, 1)
            self.generateBody()
            self.generateHead2('movershaker')
            texture = loader.loadTexture('phase_4/maps/mover_shaker.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.7)
        elif dna.name == 'cnd':
            self.scale = 6.0 / aSize
            self.handColor = VBase4(0.992, 0.851, 0.757, 1)
            self.generateBody()
            self.generateHead2('yesman')
            texture = loader.loadTexture('phase_4/maps/mr_hollywood1.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.95)
        elif dna.name == 'tf':
            self.scale = 5.75 / aSize
            self.handColor = VBase4(0.965, 0.859, 0.831, 1)
            self.generateBody()
            self.generateHead2('twoface')
            texture = loader.loadTexture('phase_4/maps/twoface.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.45)
        elif dna.name == 'ppl':
            self.scale = 6.0 / aSize
            self.handColor = VBase4(0.584, 0.686, 0.745, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/peoplepleaser.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.8)
        elif dna.name == 'm':
            self.scale = 6.25 / aSize
            self.handColor = VBase4(0.918, 0.808, 0.871, 1)
            self.generateFemaleBody()
            self.generateHead2('twoface')
            texture = loader.loadTexture('phase_4/maps/mingler2.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.11)
        elif dna.name == 'ksp':
            self.scale = 6.5 / aSize
            self.handColor = VBase4(0.733, 0.541, 0.525, 1)
            self.generateFemaleBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/kissup_tex.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.5)
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
            texture = loader.loadTexture('phase_3.5/maps/ttoff_t_ene_overtime_palette_4amlc_12.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.9)
        elif dna.name == 'foreman':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(1, 0.486, 0, 1)
            self.makeSkeletonManager()
            self.setHeight(9.0)
        elif dna.name == 'dopr':
            self.scale = 7.0 / cSize
            self.handColor = VBase4(1, 1, 1, 1.0)
            self.makeSkeletonManager()
            self.makeExecutive()
            self.setHeight(9.5)
        elif dna.name == 'dopa':
            self.scale = 7.0 / cSize
            self.handColor = VBase4(1, 1, 1, 1.0)
            self.makeSkeletonManager()
            self.makeExecutive()
            self.setHeight(9.5)
        elif dna.name == 'bellring':
            self.scale = 5.0 / bSize
            self.handColor = VBase4(0.886, 0.749, 0.451, 1)
            self.generateHighCollarBody()
            self.makeBellringer()
            self.generateHead3('bellringer', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_bellringer.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.0)
        elif dna.name == 'mh2':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.918, 0.886, 0.875, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead2('yesman')
            texture = loader.loadTexture('phase_4/maps/mr_hollywood.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.generateHead2('shades')
            self.setHeight(8.95)
        elif dna.name == 'prethink':
            self.scale = 4.5 / bSize
            self.handColor = VBase4(0.682, 0.604, 0.765, 1)
            self.generateBody()
            self.generateHead3('prethinker', animated=True)
            self.makePrethinker()
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_prethinker3.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.2)
        elif dna.name == 'mslacker':
            self.scale = 5.0 / cSize
            self.handColor = VBase4(0.553, 0.404, 0.537, 1)
            self.generateBody()
            self.makeMultislacker()
            self.generateHead3('multislacker', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_multislacker.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.5)
            self.setTransparency(1)
        elif dna.name == 'put':
            self.scale = 7.5 / aSize
            self.handColor = VBase4(0.835, 0.843, 0.847, 1)
            self.generateBody()
            self.makeVideographer()
            self.generateHead3('multislacker', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_videographer2.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(10.0)
            self.setTransparency(1)
        elif dna.name == 'radiog':
            self.scale = 6.8 / aSize
            self.handColor = VBase4(0.612, 0.376, 0.608, 1)
            self.generateBodyHybrid()
            self.generateHead2('skeleskull_A')
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_s_exe.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.generateHead3('dopa', animated=True)
            self.makeExecutive()
            self.setHeight(8.7)
            self.setTransparency(1)
        elif dna.name == 'racket':
            self.scale = 7.0 / bSize
            self.handColor = VBase4(0.173, 0.173, 0.173, 1)
            self.generateBody()
            self.generateHead3('redd', animated=True)
            self.makeExecutive()
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_racket.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(9.0)
        elif dna.name == 'ubuster':
            self.scale = 7.2 / aSize
            self.handColor = VBase4(0.604, 0.463, 0.62, 1)
            self.generateBodyHybrid()
            self.generateHead2('skeleskull_A')
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_s_exe.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.generateHead3('dopr', animated=True)
            self.makeExecutive()
            self.setHeight(8.7)
            self.setTransparency(1)
        elif dna.name == 'safesupervis':
            self.scale = 7.5 / aSize
            self.handColor = VBase4(1, 0.486, 0, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('dold', animated=True)
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_dold.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(10.0)
            self.setTransparency(1)
        elif dna.name == 'psetter':
            self.scale = 6.2 / bSize
            self.handColor = VBase4(0.369, 0.369, 0.369, 1)
            self.generatePaceBody()
            self.makePacesetter()
            self.generateHead3('pacesetter', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_pacesetter.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.5)

        # Boardbots
        elif dna.name == 'bgh':
            self.scale = 4.0 / cSize
            self.handColor = VBase4(0.427, 0.608, 0.631, 1)
            self.generateBody()
            self.generateHead3('bagholder', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_bagholder.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
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
        elif dna.name == 'ca':
            self.scale = 4.0 / cSize
            self.handColor = SuitDNA.boardPolyColor
            self.generateBody()
            self.generateHead2('flunky')
            texture = loader.loadTexture('phase_3.5/maps/conartist.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.generateHead2('beret')
            self.setHeight(4.88)
        elif dna.name == 'ins':
            self.scale = 5.0 / bSize
            self.handColor = VBase4(0.031, 0.035, 0.035, 1)
            self.generateHighCollarBody()
            self.generateHead3('insider', animated=True)
            self.setHeight(6.7)
        elif dna.name == 'mdm':
            self.scale = 5.0 / aSize
            self.handColor = SuitDNA.boardPolyColor
            self.generateBody()
            self.generateHead2('twoface')
            texture = loader.loadTexture('phase_3.5/maps/middleman.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.7)
        elif dna.name == 'cbr':
            self.scale = 4.8 / aSize
            self.handColor = SuitDNA.boardPolyColor
            self.generateBody()
            self.generateHead3('circuitbreaker', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_circuitbreaker.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.66)
        elif dna.name == 'txm':
            self.scale = 5.25 / cSize
            self.handColor = VBase4(0.706, 0.608, 0.18, 1)
            self.generateBody()
            self.generateHead2('toxicleader')
            self.setHeight(7.2)
        elif dna.name == 'dl':
            self.scale = 5.5 / cSize
            self.handColor = VBase4(0.463, 0.58, 0.592, 1)
            self.generateBody()
            self.generateHead3('deadlock', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_deadlock.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.2)
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
        elif dna.name == 'shw':
            self.scale = 5.75 / cSize
            self.handColor = VBase4(0.427, 0.608, 0.631, 1)
            self.generateBody()
            self.generateHead3('sharkwatcher', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_sharkwatcher.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.25)
        elif dna.name == 'bfh2':
            self.scale = 7.0 / cSize
            self.handColor = VBase4(0.635, 0.62, 0.651, 1)
            self.generateFemaleBody()
            self.generateHead2('bigfish')
            self.setHeight(10.0)
        elif dna.name == 'mg':
            self.scale = 6.8 / aSize
            self.handColor = VBase4(0.169, 0.169, 0.169, 1)
            self.generateBody()
            self.generateHead3('magnate', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_magnate.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.0)
        elif dna.name == 'chw':
            self.scale = 7.0 / aSize
            self.handColor = SuitDNA.boardPolyColor
            self.generateBody()
            self.generateHead2('headhoncho')
            texture = loader.loadTexture('phase_3.5/maps/head-honcho.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.7)
        elif dna.name == 'hho':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.42, 0.42, 0.42, 1)
            self.generateBody()
            self.generateHead3('headhoncho', animated=True)
            self.setHeight(10.61)
        elif dna.name == 'chairp':
            self.scale = 6.0 / aSize
            self.handColor = VBase4(0.686, 0.776, 0.725, 1)
            self.generateBody()
            self.generateHead2('yesman')
            self.makeExecutive()
            texture = loader.loadTexture('phase_4/maps/investor.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.9)
        elif dna.name == 'bdirector':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(1, 0.486, 0, 1)
            self.makeSkeletonManager()
            self.setHeight(9.0)
        elif dna.name == 'ddiver':
            self.scale = 8.0 / cSize
            self.handColor = VBase4(0.404, 0.647, 0.635, 1)
            self.generateFemaleBody()
            self.makeDeepDiver()
            self.generateHead3('deepdiver', animated=True)
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_ddiver.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(11.0)
        elif dna.name == 'gatekeep':
            self.scale = 5.5 / aSize
            self.handColor = VBase4(0.612, 0.612, 0.612, 1)
            self.generateFemaleBody()
            self.makeGatekeeper()
            self.generateHead3('gatekeeper', animated=True)
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_gatekeeper.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.9)
        elif dna.name == 'dola':
            self.scale = 6.0 / bSize
            self.handColor = SuitDNA.boardPolyColor
            self.generateBody()
            self.makeBoardbotManager()
            self.generateHead3('dola', animated=True)
            self.setHeight(8.0)
        elif dna.name == 'dold':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(1, 0.486, 0, 1)
            self.generateBody()
            self.makeBoardbotManager()
            self.generateHead3('dold', animated=True)
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_dold.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setTransparency(1)
            self.setHeight(9.31)
        elif dna.name == 'pbs':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.generateSkeletonBody()
            self.makeExecutive()
            self.setTransparency(1)
            self.setHeight(8.5)
        elif dna.name == 'fmaker':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.835, 0.843, 0.847, 1)
            self.generateBody()
            self.makeVideographer2()
            self.generateHead2('skeleskull_A')
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_g_exe.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.generateHead3('autocaddie', animated=True)
            self.setHeight(8.5)
        elif dna.name == 'jgd':
            self.scale = 7.3 / aSize
            self.handColor = VBase4(1, 1, 1, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('majorplayer', animated=True)
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_majorplayer.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(10.0)
            self.setTransparency(1)
        elif dna.name == 'bby':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.generateSkeletonBody()
            self.makeExecutive()
            self.setTransparency(1)
            self.setHeight(8.5)
        elif dna.name == 'dking':
            self.scale = 6.5 / aSize
            self.handColor = VBase4(0.173, 0.173, 0.173, 1)
            self.generateBody()
            self.makeBoardbotManager()
            self.generateHead3('redd', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_redd.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.4)
            self.setTransparency(1)
        elif dna.name == 'ottoman':
            self.scale = 6.0 / bSize
            self.handColor = VBase4(0.302, 0.255, 0.196, 1)
            self.generateBody()
            self.makeBoardbotManager()
            self.generateHead3('ottoman', animated=True)
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_ottoman.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.0)
            self.setTransparency(1)
        elif dna.name == 'crystal':
            self.scale = 7.25 / aSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.generateBody()
            self.makeBoardbotManager()
            self.generateHead3('chainsaw', animated=True)
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_chainsaw_boardbot.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(9.8)
            self.setTransparency(1)
        elif dna.name == 'chairman':
            self.scale = 7.5 / aSize
            self.handColor = VBase4(0.396, 0.373, 0.322, 1)
            self.generateBody()
            self.makeBoardbotManager()
            self.generateHead3('chairman', animated=True)
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_chairman.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(9.7)
            self.setTransparency(1)

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
        elif dna.name == 'cmk':
            self.scale = 4.25 / cSize
            self.handColor = VBase4(0.871, 0.722, 0.882, 1)
            self.generateBody()
            self.generateHead2('codeMonkey')
            self.setHeight(5.63)
        elif dna.name == 'dhr':
            self.scale = 4.5 / cSize
            self.handColor = VBase4(0.929, 0.835, 0.961, 1)
            self.generateFemaleBody()
            self.generateHead2('dataHoarder')
            self.setHeight(6.5)
        elif dna.name == 'vpr':
            self.scale = 4.25 / aSize
            self.handColor = VBase4(0.596, 0.529, 0.216, 1)
            self.generateBody()
            self.generateHead2('yesman')
            texture = loader.loadTexture('phase_3.5/maps/voodoo_programmer.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.63)
        elif dna.name == 'brn':
            self.scale = 5.25 / aSize
            self.handColor = VBase4(0.984, 0.827, 0.922, 1)
            self.generateBody()
            self.generateHead2('brainiac')
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
            self.scale = 5.0 / aSize
            self.handColor = VBase4(0.345, 0.345, 0.345, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/Material.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.75)
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
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.843, 0.753, 0.929, 1)
            self.generateBody()
            self.generateHead2('movershaker')
            texture = loader.loadTexture('phase_3.5/maps/installation-wizard.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.55)
        elif dna.name == 'itn':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.882, 0.839, 0.929, 1)
            self.generateBody()
            self.generateHead2('industryTitan')
            self.setHeight(9.0)
        elif dna.name == 'rus':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.525, 0.455, 0.369, 1)
            self.generateBody()
            self.generateHead2('telemarketer')
            texture = loader.loadTexture('phase_3.5/maps/telemarketer.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(9.0)
        elif dna.name == 'ant':
            self.scale = 7.0 / bSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.makeSkeletonManager()
            self.setHeight(8.0)
        elif dna.name == 'sya':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.makeSkeletonManager()
            self.setHeight(8.5)
        elif dna.name == 'djockey':
            self.scale = 5.0 / cSize
            self.handColor = VBase4(0.882, 0.847, 0.784, 1)
            self.generateBody()
            self.makeDummy()
            self.generateHead3('dummy', animated=True)
            texture = loader.loadTexture('phase_4/maps/schoolhouse/dummy/ttcc_ene_djockey.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.0)
        elif dna.name == 'ptjockey':
            self.scale = 5.0 / cSize
            self.handColor = VBase4(0.882, 0.847, 0.784, 1)
            self.generateBody()
            self.makeDummy()
            self.generateHead3('dummy', animated=True)
            texture = loader.loadTexture('phase_4/maps/schoolhouse/dummy/ttcc_ene_djockey.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.0)
        elif dna.name == 'jas':
            self.scale = 7.0 / bSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.makeSkeletonManager()
            self.setHeight(8.0)
        elif dna.name == 'tas':
            self.scale = 7.0 / bSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.makeSkeletonManager()
            self.setHeight(8.0)
        elif dna.name == 'fhu':
            self.scale = 7.0 / bSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.makeSkeletonManager()
            self.setHeight(8.0)
        elif dna.name == 'fsh':
            self.scale = 7.0 / bSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.makeSkeletonManager()
            self.setHeight(8.0)
        elif dna.name == 'fhj':
            self.scale = 7.0 / bSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.makeSkeletonManager()
            self.setHeight(8.0)
        elif dna.name == 'kdh':
            self.scale = 7.0 / bSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.makeSkeletonManager()
            self.setHeight(8.0)
        elif dna.name == 'dar':
            self.scale = 6.0 / bSize
            self.handColor = VBase4(0.09, 0.09, 0.09, 1)
            self.generateLongcoatBody()
            self.generateHead3('insider', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_insider_mgr.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.0)
        elif dna.name == 'nhy':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(1, 0.486, 0, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('dold', animated=True)
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_dold.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(9.0)
        elif dna.name == 'wrt':
            self.scale = 7.2 / aSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.generateFemaleBody()
            self.makeExecutive()
            self.generateHead3('stenographer', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_crystalline.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(10.0)
        elif dna.name == 'auh':
            self.scale = 7.3 / aSize
            self.handColor = VBase4(0.773, 0.745, 0.71, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('plutocrat', animated=True)
            texture = loader.loadTexture('phase_10/maps/ttcc_ene_plutocrat.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(9.5)

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
        elif dna.name == 'sbg':
            self.scale = 4.25 / cSize
            self.handColor = VBase4(0.718, 0.667, 0.624, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/sandbagger.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.5)
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
            self.scale = 5.25 / bSize
            self.handColor = VBase4(0.62, 0.89, 0.843, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/ghost_writer.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.75)
        elif dna.name == 'ghw':
            self.scale = 5.25 / aSize
            self.handColor = VBase4(0.173, 0.173, 0.173, 1)
            self.generateBody()
            self.generateHead2('ghostwriter')
            texture = loader.loadTexture('phase_4/maps/ghostwriter.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.6)
        elif dna.name == 'dcw':
            self.scale = 6.0 / aSize
            self.handColor = VBase4(0.984, 0.988, 0.988, 1)
            self.generateBody()
            self.generateHead2('backstabber')
            texture = loader.loadTexture('phase_3.5/maps/doctorwhite.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.3)
        elif dna.name == 'gzt':
            self.scale = 6.25 / aSize
            self.handColor = VBase4(0.514, 0.514, 0.514, 1)
            self.generateBody()
            self.generateHead2('gazetteer')
            texture = loader.loadTexture('phase_4/maps/gazetteer.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.25)
        elif dna.name == 'wnk':
            self.scale = 6.5 / bSize
            self.handColor = VBase4(0.871, 0.855, 0.816, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/whiteknight.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.1)
        elif dna.name == 'nsh':
            self.scale = 6.75 / aSize
            self.handColor = VBase4(0.337, 0.29, 0.278, 1)
            self.generateBody()
            self.generateHead2('newshound')
            texture = loader.loadTexture('phase_4/maps/newshound.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.55)
        elif dna.name == 'std':
            self.scale = 6.75 / aSize
            self.handColor = VBase4(1, 0.973, 0.969, 1)
            self.generateBody()
            self.generateHead2('yesman')
            texture = loader.loadTexture('phase_3.5/maps/stuntdouble.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(9.0)
        elif dna.name == 'anc':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.8, 0.776, 0.765, 1)
            self.generateBody()
            self.generateHead2('anchorman')
            texture = loader.loadTexture('phase_4/maps/anchorman.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(9.0)
        elif dna.name == 'jls':
            self.scale = 7.0 / bSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.makeSkeletonManager()
            self.setHeight(8.0)
        elif dna.name == 'pbl':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.makeSkeletonManager()
            self.setHeight(8.5)
        elif dna.name == 'director':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.835, 0.843, 0.847, 1)
            self.generateBody()
            self.makeVideographer2()
            self.generateHead2('skeleskull_A')
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_p_exe.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.generateHead3('autocaddie', animated=True)
            self.setHeight(8.5)
        elif dna.name == 'bcaster':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.835, 0.843, 0.847, 1)
            self.generateBody()
            self.makeVideographer2()
            self.generateHead3('multislacker', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_videographer2.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.makeVirtual()
            self.makeVulnerable()
            self.setHeight(9.5)
            self.setTransparency(1)
        elif dna.name == 'std2':
            self.scale = 6.75 / aSize
            self.handColor = VBase4(1, 0.973, 0.969, 1)
            self.generateBody()
            self.generateHead2('yesman')
            texture = loader.loadTexture('phase_3.5/maps/stuntdouble.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.generateHead2('shades')
            self.makeExecutive()
            self.setHeight(9.0)
        elif dna.name == 'videog':
            self.scale = 7.5 / aSize
            self.handColor = VBase4(0.835, 0.843, 0.847, 1)
            self.generateBody()
            self.makeVideographer()
            self.generateHead3('multislacker', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_videographer2.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(10.0)
            self.setTransparency(1)
        elif dna.name == 'prt':
            self.scale = 7.0 / bSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.makeSkeletonManager()
            self.setHeight(8.0)
        elif dna.name == 'pla':
            self.scale = 7.0 / bSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.makeSkeletonManager()
            self.setHeight(8.0)
        elif dna.name == 'plk':
            self.scale = 7.0 / bSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.makeSkeletonManager()
            self.setHeight(8.0)
        elif dna.name == 'plh':
            self.scale = 7.0 / bSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.makeSkeletonManager()
            self.setHeight(8.0)
        elif dna.name == 'plg':
            self.scale = 7.0 / bSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.makeSkeletonManager()
            self.setHeight(8.0)
        elif dna.name == 'plf':
            self.scale = 7.0 / bSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.makeSkeletonManager()
            self.setHeight(8.0)
        elif dna.name == 'pld':
            self.scale = 7.0 / bSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.makeSkeletonManager()
            self.setHeight(8.0)
        elif dna.name == 'pls':
            self.scale = 7.0 / bSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.makeSkeletonManager()
            self.setHeight(8.0)
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

    def generateBody(self):
        animDict = self.generateAnimDict()
        filePrefix, bodyPhase = ModelDict[self.style.body]
        if base.config.GetBool('want-new-cogs', 0):
            if cogExists(filePrefix + 'zero.bam'):
                self.loadModel('phase_3.5' + filePrefix + 'zero')
            else:
                self.loadModel('phase_3.5' + filePrefix + 'mod')
        else:
            self.loadModel('phase_3.5' + filePrefix + 'mod')
        self.loadAnims(animDict)
        self.setSuitClothes()
        #if self.style.name == 'dsk' and not self.isSkeleton:
            #self.generateHead2('skeleskull_A')
            #self.generateSkeletonHands()
        #if self.style.name == 'blr' and not self.isSkeleton:
            #self.generateHead2('skeleskull_A')
            #self.generateSkeletonHands()
        self.setBlend(frameBlend=base.wantSmoothAnims)
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)

    def generateSkeletonHands(self):
        animDict = self.generateAnimDict()
        filePrefix, bodyPhase = ModelDict[self.style.body]
        if base.config.GetBool('want-new-cogs', 0):
            if cogExists(filePrefix + 'zero.bam'):
                self.loadModel('phase_3.5/models/char/suitA_skeleton_hands-zero')
            else:
                self.loadModel('phase_3.5/models/char/suitA_skeleton_hands-zero')
        else:
            self.loadModel('phase_3.5/models/char/suitA_skeleton_hands-zero')
        self.loadAnims(animDict)
        self.setHandTexture()
        self.setBlend(frameBlend=base.wantSmoothAnims)
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)

    def generateBodyHybrid(self):
        animDict = self.generateAnimDict()
        filePrefix, bodyPhase = ModelDict[self.style.body]
        if base.config.GetBool('want-new-cogs', 0):
            if cogExists(filePrefix + 'zero.bam'):
                self.loadModel('phase_3.5' + filePrefix + 'zero')
                self.loadModel('phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-zero', 'skelehands')
            else:
                self.loadModel('phase_3.5' + filePrefix + 'mod')
                self.loadModel('phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-zero', 'skelehands')
        else:
            self.loadModel('phase_3.5' + filePrefix + 'mod')
            self.loadModel('phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-zero', 'skelehands')
        self.loadAnims(animDict)
        self.loadAnims(animDict, 'skelehands')
        self.setSuitClothesHybrid()
        self.find('**/hands').hide()
        self.setBlend(frameBlend=base.wantSmoothAnims)
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)

    def generateSkeletonBody(self):
        animDict = self.generateAnimDict()
        filePrefix, bodyPhase = ModelDict[self.style.body]
        dept = self.style.dept
        for headPart in self.headParts:
            headPart.removeNode()
        self.headParts = []
        if base.config.GetBool('want-new-cogs', 0):
            if cogExists(filePrefix + 'zero.bam'):
                self.loadModel('phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-zero')
            else:
                self.loadModel('phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-zero')
        else:
            self.loadModel('phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-zero')
        if self.style.body == 'a' and self.style.name == 'derrhand':
            self.generateHead3('derrickhand_skele', animated=True)
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_derrickhand_skelecog.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(1)
        if self.style.body == 'a' and self.style.name == 'radiog':
            self.generateHead3('dopa', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_dopa.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(1.2)
        if self.style.body == 'a' and self.style.name == 'autocad':
            self.generateHead3('autocaddie', animated=True)
            for headPart in self.headParts:
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(1)
        if self.style.body == 'a' and self.style.name == 'clubpres':
            self.generateHead3('autocaddie', animated=True)
            #texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_c_exe.png')
            for headPart in self.headParts:
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(1)
                #headModel.find('**/head').setTexture(texture, 1)
        if self.style.body == 'a' and self.style.name == 'ubuster':
            self.generateHead3('dopr', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_dopr.png')
            for headPart in self.headParts:
                headPart.setZ(0)
                headPart.setTexture(texture, 1)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(1.3)
        if self.style.body == 'a' and self.style.name == 'ambass':
            self.generateHead3('prethinker2', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_prethinker.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
        if self.style.body == 'a' and not self.style.name == 'autocad' and not self.style.name == 'derrhand' and not self.style.name == 'ambass' and not self.style.name == 'clubpres' and not self.style.name == 'ubuster' and not self.style.name == 'radiog':
            self.generateHead3('skullA', animated=True)
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s2.png' %
                                         self.style.dept)
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(1)
        if self.style.body == 'b':
            self.generateHead3('skullB', animated=True)
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s2.png' %
                                         self.style.dept)
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(1)
        if self.style.body == 'c' and self.style.name == 'dopa':
            self.generateHead3('dopa', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_dopa.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(1)
        if self.style.body == 'c' and self.style.name == 'dopr':
            self.generateHead3('dopr', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_dopr.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(1)
        if self.style.body == 'c' and not self.style.name == 'dopa' and not self.style.name == 'dopr':
            self.generateHead3('skullC', animated=True)
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s2.png' %
                self.style.dept)
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(1)
        self.loadAnims(animDict)
        self.setSuitClothesSkeleton()
        self.setBlend(frameBlend=base.wantSmoothAnims)
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)
        self.isSkeleton = 1

    def generateFemaleBody(self):
        animDict = self.generateAnimDict()
        filePrefix, bodyPhase = ModelDict[self.style.body]
        if base.config.GetBool('want-new-cogs', 0):
            if cogExists(filePrefix + 'zero.bam'):
                self.loadModel('phase_3.5' + filePrefix + 'zero')
            else:
                self.loadModel('phase_3.5' + filePrefix + 'f-mod')
        else:
            self.loadModel('phase_3.5' + filePrefix + 'f-mod')
        self.loadAnims(animDict)
        self.setSuitClothes()
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)
        self.setBlend(frameBlend=base.wantSmoothAnims)

    def generateHighCollarBody(self):
        animDict = self.generateAnimDict()
        filePrefix, bodyPhase = ModelDict[self.style.body]
        if base.config.GetBool('want-new-cogs', 0):
            if cogExists(filePrefix + 'zero.bam'):
                self.loadModel('phase_3.5' + filePrefix + 'zero')
            else:
                self.loadModel('phase_3.5' + filePrefix + 'highcollar-mod')
        else:
            self.loadModel('phase_3.5' + filePrefix + 'highcollar-mod')
        self.loadAnims(animDict)
        self.setSuitClothes()
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)
        self.setBlend(frameBlend=base.wantSmoothAnims)

    def generateCounterFitBody(self):
        animDict = self.generateAnimDict()
        filePrefix, bodyPhase = ModelDict[self.style.body]
        if base.config.GetBool('want-new-cogs', 0):
            if cogExists(filePrefix + 'zero.bam'):
                self.loadModel('phase_3.5' + filePrefix + 'zero')
            else:
                self.loadModel('phase_3.5' + filePrefix + 'erfit-mod')
        else:
            self.loadModel('phase_3.5' + filePrefix + 'erfit-mod')
        self.loadAnims(animDict)
        self.setSuitClothes()
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)
        self.setBlend(frameBlend=base.wantSmoothAnims)

    def generateLongcoatBody(self):
        animDict = self.generateAnimDict()
        filePrefix, bodyPhase = ModelDict[self.style.body]
        if base.config.GetBool('want-new-cogs', 0):
            if cogExists(filePrefix + 'zero.bam'):
                self.loadModel('phase_3.5' + filePrefix + 'zero')
            else:
                self.loadModel('phase_3.5' + filePrefix + 'longcoat-mod')
        else:
            self.loadModel('phase_3.5' + filePrefix + 'longcoat-mod')
        self.loadAnims(animDict)
        self.setSuitClothesRaincoat()
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)
        self.setBlend(frameBlend=base.wantSmoothAnims)

    def generateHighRollerBody(self):
        animDict = self.generateAnimDict()
        filePrefix, bodyPhase = ModelDict[self.style.body]
        if base.config.GetBool('want-new-cogs', 0):
            if cogExists(filePrefix + 'zero.bam'):
                self.loadModel('phase_3.5' + filePrefix + 'zero')
            else:
                self.loadModel('phase_3.5' + filePrefix + 'hroller-mod')
        else:
            self.loadModel('phase_3.5' + filePrefix + 'hroller-mod')
        self.loadAnims(animDict)
        self.setSuitClothesHighRoller()
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)
        self.setBlend(frameBlend=base.wantSmoothAnims)

    def generateHighRollerBodyWhite(self):
        animDict = self.generateAnimDict()
        filePrefix, bodyPhase = ModelDict[self.style.body]
        if base.config.GetBool('want-new-cogs', 0):
            if cogExists(filePrefix + 'zero.bam'):
                self.loadModel('phase_3.5' + filePrefix + 'zero')
            else:
                self.loadModel('phase_3.5' + filePrefix + 'hroller-mod')
        else:
            self.loadModel('phase_3.5' + filePrefix + 'hroller-mod')
        self.loadAnims(animDict)
        self.setSuitClothesHighRollerWhite()
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)
        self.setBlend(frameBlend=base.wantSmoothAnims)

    def generatePaceBody(self):
        animDict = self.generateAnimDict()
        filePrefix, bodyPhase = ModelDict[self.style.body]
        if base.config.GetBool('want-new-cogs', 0):
            if cogExists(filePrefix + 'zero.bam'):
                self.loadModel('phase_3.5' + filePrefix + 'zero')
            else:
                self.loadModel('phase_3.5' + filePrefix + 'open-mod')
        else:
            self.loadModel('phase_3.5' + filePrefix + 'open-mod')
        self.loadAnims(animDict)
        self.setSuitClothes()
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)
        self.setBlend(frameBlend=base.wantSmoothAnims)

    def generateAnimDict(self):
        animDict = {}
        filePrefix, bodyPhase = ModelDict[self.style.body]
        for anim in AllSuits:
            animDict[anim[0]] = 'phase_' + str(bodyPhase) + filePrefix + anim[1]

        for anim in AllSuitsMinigame:
            animDict[anim[0]] = 'phase_4' + filePrefix + anim[1]

        for anim in AllSuitsTutorialBattle:
            filePrefix, bodyPhase = TutorialModelDict[self.style.body]
            animDict[anim[0]] = 'phase_' + str(bodyPhase) + filePrefix + anim[1]

        for anim in AllSuitsBattle:
            animDict[anim[0]] = 'phase_5' + filePrefix + anim[1]

        if self.style.body == 'a':
            animDict['neutral'] = 'phase_4/models/char/suitA-neutral'
            for anim in SuitsCEOBattle:
                animDict[anim[0]] = 'phase_12/models/char/suitA-' + anim[1]
        elif self.style.body == 'b':
            animDict['neutral'] = 'phase_4/models/char/suitB-neutral'
            for anim in SuitsCEOBattle:
                animDict[anim[0]] = 'phase_12/models/char/suitB-' + anim[1]
        elif self.style.body == 'c':
            animDict['neutral'] = 'phase_3.5/models/char/suitC-neutral'
            for anim in SuitsCEOBattle:
                animDict[anim[0]] = 'phase_12/models/char/suitC-' + anim[1]

        try:
            animList = eval(self.style.name)
        except NameError:
            self.notify.warning("Failed to evaluate animList!")
            animList = ()

        for anim in animList:
            phase = 'phase_' + str(anim[2])
            animDict[anim[0]] = phase + filePrefix + anim[1]

        return animDict

    def initializeBodyCollisions(self, collIdStr):
        Avatar.Avatar.initializeBodyCollisions(self, collIdStr)
        if not self.ghostMode:
            self.collNode.setCollideMask(self.collNode.getIntoCollideMask() | ToontownGlobals.PieBitmask)

    def updateNametag(self):
        nameInfo = TTLocalizer.SuitBaseNameWithLevelHP % {'name': self.name,
                                                          'dept': self.getStyleDept(),
                                                          'level': self.getActualLevel(),
                                                          'currHP': self.currHP,
                                                          'maxHP': self.maxHP}
        self.setDisplayName(nameInfo)

    def setSuitClothes(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        dept = self.style.dept
        phase = 3.5
        texture3 = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        texture2 = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_%s.png' % self.style.dept)
        texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_%s.png' % self.style.dept)
        if self.isExecutive and not self.style.name == 'ins' and not self.style.name == 'hroller' and not self.style.name == 'djockey':
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_%s_e.png' % self.style.dept)
        elif self.isManager and not self.style.name == 'hroller2':
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_%s_e.png' % self.style.dept)
        elif self.isExecutive and self.style.name == 'hroller':
            texture = loader.loadTexture('phase_12/maps/cc_t_ene_highroller_suit.png')
        elif self.isExecutive and self.style.name == 'djockey':
            texture = loader.loadTexture('phase_4/maps/schoolhouse/dummy/ttcc_ene_suittex_ptjockey_e.png')
        elif self.isGovernaught and not self.style.name == 'ins':
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_%s_gov.png' % self.style.dept)
        elif not self.isGovernaught and not self.isExecutive and self.style.name == 'ins':
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_highcollar_%s.png' % self.style.dept)
        elif self.isGovernaught and self.style.name == 'ins':
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_highcollar_%s_gov.png' % self.style.dept)
        elif self.isExecutive and self.style.name == 'ins':
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_highcollar_%s_e.png' % self.style.dept)
        modelRoot.find('**/hands').setColor(self.handColor)
        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()
        modelRoot.find('**/bowtie').hide()
        modelRoot.find('**/necktie-s').setTexture(texture, 1)
        if self.style.name == 'wsi':
            modelRoot.find('**/necktie-w').setTexture(texture2, 1)
        else:
            modelRoot.find('**/necktie-w').setTexture(texture, 1)
        modelRoot.find('**/bowtie').setTexture(texture, 1)
        if self.style.dept == 'l':
            modelRoot.find('**/bowtie').show()
        elif self.style.name == 'videog':
            modelRoot.find('**/necktie-w').setTexture(texture3, 1)
            modelRoot.find('**/necktie-s').setTexture(texture3, 1)
            modelRoot.find('**/necktie-s').show()
        elif self.style.name == 'bcaster':
            modelRoot.find('**/necktie-w').setTexture(texture3, 1)
            modelRoot.find('**/necktie-s').setTexture(texture3, 1)
            modelRoot.find('**/necktie-s').show()
        elif self.style.name == 'fmaker':
            modelRoot.find('**/necktie-w').setTexture(texture3, 1)
            modelRoot.find('**/necktie-s').setTexture(texture3, 1)
            modelRoot.find('**/necktie-s').show()
        elif self.style.name == 'director':
            modelRoot.find('**/necktie-w').setTexture(texture3, 1)
            modelRoot.find('**/necktie-s').setTexture(texture3, 1)
            modelRoot.find('**/necktie-s').show()
        elif self.style.name == 'key':
            modelRoot.find('**/necktie-s').show()
        elif self.style.dept == 's':
            modelRoot.find('**/necktie-s').show()
        elif self.style.name == 'psetter':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'hroller2':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'ins':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'redd':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'erclaim':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'hroller':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'erfit':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'dking':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'ddiver':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'gatekeep':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'racket':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'wsi':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/bowtie').hide()
        else:
            modelRoot.find('**/necktie-w').show()
        modelRoot.find('**/body').setTexture(texture, 1)
        self.shadowJoint = self.find('**/joint_shadow')
        self.nametagJoint = self.find('**/joint_nameTag')
        self.leftHand = self.find('**/joint_Lhold')
        self.rightHand = self.find('**/joint_Rhold')

    def setSuitClothesHybrid(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        dept = self.style.dept
        phase = 3.5
        texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_%s.png' % self.style.dept)
        if self.isExecutive:
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_%s_e.png' % self.style.dept)
        elif self.isGovernaught:
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_%s_gov.png' % self.style.dept)
        modelRoot.find('**/hands').hide()
        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()
        modelRoot.find('**/bowtie').hide()
        modelRoot.find('**/necktie-s').setTexture(texture, 1)
        modelRoot.find('**/necktie-w').setTexture(texture, 1)
        modelRoot.find('**/bowtie').setTexture(texture, 1)
        if self.style.dept == 'l':
            modelRoot.find('**/bowtie').show()
        elif self.style.dept == 's':
            modelRoot.find('**/necktie-s').show()
        else:
            modelRoot.find('**/necktie-w').show()
        modelRoot.find('**/body').setTexture(texture, 1)
        self.shadowJoint = self.find('**/joint_shadow')
        self.nametagJoint = self.find('**/joint_nameTag')
        self.leftHand = self.find('**/joint_Lhold')
        self.rightHand = self.find('**/joint_Rhold')

    def setHandTexture(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        dept = self.style.dept
        phase = 3.5
        self.shadowJoint = self.find('**/joint_shadow')
        self.nametagJoint = self.find('**/joint_nameTag')
        self.leftHand = self.find('**/joint_Lhold')
        self.rightHand = self.find('**/joint_Rhold')

    def setSuitClothesHighRoller(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        dept = self.style.dept
        phase = 3.5
        texture = loader.loadTexture('phase_12/maps/cc_t_ene_highroller_suit_black.png')
        modelRoot.find('**/hands').setColor(self.handColor)
        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()
        modelRoot.find('**/bowtie').hide()
        modelRoot.find('**/necktie-s').setTexture(texture, 1)
        modelRoot.find('**/necktie-w').setTexture(texture, 1)
        modelRoot.find('**/bowtie').setTexture(texture, 1)
        if self.style.dept == 'l':
            modelRoot.find('**/bowtie').show()
        elif self.style.dept == 's':
            modelRoot.find('**/necktie-s').show()
        elif self.style.name == 'psetter':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'videog':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'bcaster':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'hroller':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'hroller2':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'hrollers':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'ins':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'erfit':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        else:
            modelRoot.find('**/necktie-w').show()
        modelRoot.find('**/body').setTexture(texture, 1)
        self.shadowJoint = self.find('**/joint_shadow')
        self.nametagJoint = self.find('**/joint_nameTag')
        self.leftHand = self.find('**/joint_Lhold')
        self.rightHand = self.find('**/joint_Rhold')

    def setSuitClothesRaincoat(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        dept = self.style.dept
        phase = 3.5
        texture = loader.loadTexture('phase_11/maps/ttcc_ene_suittex_rainmake.png')
        modelRoot.find('**/hands').setColor(self.handColor)
        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()
        modelRoot.find('**/bowtie').hide()
        modelRoot.find('**/necktie-s').setTexture(texture, 1)
        modelRoot.find('**/necktie-w').setTexture(texture, 1)
        modelRoot.find('**/bowtie').setTexture(texture, 1)
        if self.style.dept == 'l':
            modelRoot.find('**/bowtie').show()
        elif self.style.dept == 's' and not self.style.name == 'racket':
            modelRoot.find('**/necktie-s').show()
        elif self.style.name == 'psetter':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'videog':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'bcaster':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'hroller':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'hrollers':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'ins':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'ghd':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'racket':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        else:
            modelRoot.find('**/necktie-w').show()
        modelRoot.find('**/body').setTexture(texture, 1)
        self.shadowJoint = self.find('**/joint_shadow')
        self.nametagJoint = self.find('**/joint_nameTag')
        self.leftHand = self.find('**/joint_Lhold')
        self.rightHand = self.find('**/joint_Rhold')

    def setSuitClothesHighRollerWhite(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        dept = self.style.dept
        phase = 3.5
        texture = loader.loadTexture('phase_12/maps/cc_t_ene_highroller_suit.png')
        texture2 = loader.loadTexture('phase_12/maps/cc_t_ene_highroller_body2.png')
        texture3 = loader.loadTexture('phase_12/maps/cc_t_ene_highroller_body3.png')
        texture4 = loader.loadTexture('phase_12/maps/cc_t_ene_highroller_body3.png')
        modelRoot.find('**/hands').setColor(self.handColor)
        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()
        modelRoot.find('**/bowtie').hide()
        modelRoot.find('**/necktie-s').setTexture(texture, 1)
        modelRoot.find('**/necktie-w').setTexture(texture, 1)
        modelRoot.find('**/bowtie').setTexture(texture, 1)
        if self.style.dept == 'l':
            modelRoot.find('**/bowtie').show()
        elif self.style.dept == 's':
            modelRoot.find('**/necktie-s').show()
        elif self.style.name == 'psetter':
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'hrollers':
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'hroller':
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'hroller2':
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'erfit':
            modelRoot.find('**/necktie-w').hide()
        else:
            modelRoot.find('**/necktie-w').show()
        modelRoot.find('**/body').setTexture(texture, 1)
        modelRoot.find('**/highroller_body').setTexture(texture2, 1)
        self.shadowJoint = self.find('**/joint_shadow')
        self.nametagJoint = self.find('**/joint_nameTag')
        self.leftHand = self.find('**/joint_Lhold')
        self.rightHand = self.find('**/joint_Rhold')


    def setSuitClothesSkeleton(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        dept = self.style.dept
        phase = 3.5
        texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' % self.style.dept)
        if self.isWaiter:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_waiter.png')
        elif self.style.dept == 'c' and not self.isExecutive and not self.isManager and not self.isGovernaught and not self.isWaiter:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s2.png' % self.style.dept)
        elif self.isExecutive and not self.isWaiter:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' % self.style.dept)
        elif self.isManager and not self.style.name == 'charon' and not self.style.name == 'hydra'\
                and not self.style.name == 'radiog' and not self.style.name == 'ubuster' and not self.style.name == 'kerberos' and not self.style.name == 'nix' and not self.style.name == 'styx' and not self.isWaiter:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' % self.style.dept)
        elif self.isGovernaught and not self.isWaiter:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_gov.png' % self.style.dept)
        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()
        modelRoot.find('**/bowtie').hide()
        modelRoot.find('**/necktie-s').setTexture(texture, 1)
        modelRoot.find('**/necktie-w').setTexture(texture, 1)
        modelRoot.find('**/bowtie').setTexture(texture, 1)
        if self.isWaiter:
            modelRoot.find('**/bowtie').show()
        elif self.style.dept == 'l':
            modelRoot.find('**/bowtie').show()
        elif self.style.dept == 's':
            modelRoot.find('**/necktie-s').show()
        elif self.style.name == 'wsi':
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-w').show()
        elif self.style.name == 'hydra':
            modelRoot.find('**/bowtie').show()
            modelRoot.setColor((0.729, 0.729, 0.729, 1))
            modelRoot.find('**/bowtie').setColor((0.741, 0.82, 0.769, 1))
        elif self.style.name == 'wsi':
            texture2 = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' % self.style.dept)
            modelRoot.find('**/necktie-w').setTexture(texture2, 1)
        elif self.style.name == 'charon':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/necktie-s').show()
            modelRoot.setColor((0.51, 0.49, 0.467, 1))
            modelRoot.find('**/necktie-s').setColor((0.741, 0.82, 0.769, 1))
        elif self.style.name == 'nix':
            modelRoot.find('**/necktie-w').show()
            modelRoot.setColor((0.6, 0.6, 0.6, 1))
            modelRoot.find('**/necktie-w').setColor((0.741, 0.82, 0.769, 1))
        elif self.style.name == 'styx':
            modelRoot.find('**/necktie-w').show()
            modelRoot.setColor((0.671, 0.671, 0.671, 1))
            modelRoot.find('**/necktie-w').setColor((0.741, 0.82, 0.769, 1))
        elif self.style.name == 'kerberos':
            modelRoot.find('**/necktie-w').show()
            modelRoot.setColor((0.62, 0.659, 0.624, 1))
            modelRoot.find('**/necktie-w').setColor((0.741, 0.82, 0.769, 1))
        elif self.style.name == 'rainmake':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'racket':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'erfit':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'erclaim':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'hrollers':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'hroller2':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'hroller':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'bellring':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'psetter':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'ins':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'dking':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'ddiver':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'gatekeep':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'wsi':
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        else:
            modelRoot.find('**/necktie-w').show()
        modelRoot.find('**/body').setTexture(texture, 1)
        self.shadowJoint = self.find('**/joint_shadow')
        self.nametagJoint = self.find('**/joint_nameTag')
        self.leftHand = self.find('**/joint_Lhold')
        self.rightHand = self.find('**/joint_Rhold')

    def makeWaiter(self, modelRoot = None):
        if not modelRoot:
            modelRoot = self
        self.isWaiter = 1
        texture = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_waiter.png')
        if self.isSkeleton:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_waiter.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
        elif self.isExecutive:
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_waiter_e.png')
        elif self.isGovernaught:
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_waiter_gov.png')
        elif self.isManager:
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_%s_e.png' % self.style.dept)
        if self.style.name == 'hho' and not self.isSkeleton and not self.isExecutive:
            texture2 = loader.loadTexture('phase_14/maps/cc_t_ene_headhoncho_waiter.png')
            for headPart in self.headParts:
                headPart.setTexture(texture2, 1)
        modelRoot.find('**/body').setTexture(texture, 1)
        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()
        modelRoot.find('**/bowtie').show()
        modelRoot.find('**/bowtie').setTexture(texture, 1)
        modelRoot.find('**/hands').setColor(0.835, 0.843, 0.847, 1)
        name = self.name
        dept = self.getStyleDept()
        level = str(self.getActualLevel())
        if self.getExecutive():
            level += TTLocalizer.ExecutivePostFix
        if self.getManager():
            level += TTLocalizer.ManagerPostFix
        if self.getGovernaught():
            level += TTLocalizer.GovernaughtPostFix
        if self.getSkeleRevives() > 0:
            level += TTLocalizer.SkeleRevivePostFix % (self.getSkeleRevives() + 1)
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        self.setDisplayName(nameInfo)

    def makeWaiter2(self, modelRoot = None):
        if not modelRoot:
            modelRoot = self
        self.isWaiter = 1
        texture = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_waiter.png')
        if self.isSkeleton:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_waiter.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
        elif self.isExecutive:
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_waiter_e.png')
        elif self.isGovernaught:
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_waiter_gov.png')
        elif self.isManager:
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_waiter_e.png')
        if self.style.name == 'hho' and not self.isSkeleton and not self.isExecutive:
            texture2 = loader.loadTexture('phase_14/maps/cc_t_ene_headhoncho_waiter.png')
            for headPart in self.headParts:
                headPart.setTexture(texture2, 1)
        modelRoot.find('**/body').setTexture(texture, 1)
        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()
        modelRoot.find('**/bowtie').show()
        modelRoot.find('**/bowtie').setTexture(texture, 1)
        modelRoot.find('**/hands').setColor(0.835, 0.843, 0.847, 1)

    def makeManagerSuit(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_%s_e.png' % self.style.dept)
        modelRoot.find('**/hands').setColor(self.handColor)
        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()
        modelRoot.find('**/bowtie').hide()
        modelRoot.find('**/necktie-s').setTexture(texture, 1)
        modelRoot.find('**/necktie-w').setTexture(texture, 1)
        modelRoot.find('**/bowtie').setTexture(texture, 1)
        if self.style.dept == 'l' and not self.style.name == 'redd' and not self.style.name == 'erclaim':
            modelRoot.find('**/bowtie').show()
        elif self.style.dept == 's' and not self.style.name == 'racket':
            modelRoot.find('**/necktie-s').show()
        elif self.style.name == 'psetter':
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'redd':
            modelRoot.find('**/bowtie').hide()
        elif self.style.name == 'erclaim':
            modelRoot.find('**/bowtie').hide()
        elif self.style.name == 'hroller2':
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'racket':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'erfit':
            modelRoot.find('**/necktie-w').hide()
        else:
            modelRoot.find('**/necktie-w').show()
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeRentalSuit(self, suitType, modelRoot = None):
        if not modelRoot:
            modelRoot = self.getGeomNode()
        if suitType == 's':
            torsoTex = loader.loadTexture('phase_3.5/maps/tt_t_ene_sellbotRental_blazer.jpg')
            legTex = loader.loadTexture('phase_3.5/maps/tt_t_ene_sellbotRental_leg.jpg')
            armTex = loader.loadTexture('phase_3.5/maps/tt_t_ene_sellbotRental_sleeve.jpg')
            handTex = loader.loadTexture('phase_3.5/maps/tt_t_ene_sellbotRental_hand.jpg')
        else:
            self.notify.warning('No rental suit for cog type %s' % suitType)
            return

        self.isRental = 1
        modelRoot.find('**/torso').setTexture(torsoTex, 1)
        modelRoot.find('**/arms').setTexture(armTex, 1)
        modelRoot.find('**/legs').setTexture(legTex, 1)
        modelRoot.find('**/hands').setTexture(handTex, 1)

    def generateHead3(self, headType, headColor=None, headTexture=None, modelOverride=None, pathOverride=None,
                     extraArgs={}, animated=False, additionalAnims=[]):
        if base.config.GetBool('want-new-cogs', False):
            filePrefix, phase = HeadModelDict[self.style.body]
        else:
            filePrefix, phase = ModelDict[self.style.body]
        '''if modelOverride:
            headModel = loader.loadModel(modelOverride)
        else:
            headModel = loader.loadModel('phase_' + str(phase) + filePrefix + 'heads')'''
        if animated:
            if headType == 'skelecog' or headType == 'overwhelmingauthorizer' or headType == 'executioner':
                if headType == 'overwhelmingauthorizer':
                    headModel = Actor.Actor('phase_14/models/char/ttcc_ene_%s%s-zero' % (
                    headType, '_exe' if self.isExecutive or self.isManager else ''))
                elif headType == 'executioner':
                    headModel = Actor.Actor('phase_14/models/char/ttcc_ene_executioner-zero')
                else:
                    headModel = Actor.Actor(
                        'phase_14/models/char/cog' + string.upper(self.style.body) + '_robot_head-zero')
                self.generateHeadAnims(
                    'phase_14/models/char/cog' + string.upper(self.style.body) + '_robot_head-',
                    headModel, additionalAnims)
                self.animatedHeadParts.append(headModel)
                if headType != 'overwhelmingauthorizer':
                    if headTexture:
                        try:
                            texture = loader.loadTexture('phase_5/maps/' + headTexture)
                        except:
                            texture = loader.loadTexture('phase_14/maps/' + headTexture)
                    else:
                        if self.style.dept == None:
                            texture = loader.loadTexture('phase_14/maps/ttcc_ene_skelecog_unemployed.png')
                        else:
                            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s%s.png' % (
                            self.style.dept, '_exe' if self.isExecutive or self.isManager else '',))
                    for headPart in self.animatedHeadParts:
                        headPart.setTexture(texture, 1)
            else:
                headModel = Actor.Actor('phase_14/models/char/ttcc_ene_' + headType + '-zero')
                self.generateHeadAnims('phase_14/models/char/ttcc_ene_' + headType + '-', headModel,
                                           additionalAnims)
                self.animatedHeadParts.append(headModel)
            headModel.reparentTo(self.find('**/joint_head'))
            headModel.setBlend(frameBlend=base.wantSmoothAnims)
            if self.headInterval != None:
                self.headInterval.finish()
                del self.headInterval
            self.headInterval = Sequence(Func(headModel.loop, 'neutral')).start()
            if 'x' in extraArgs:
                if extraArgs['x'] != None:
                    headModel.setX(extraArgs['x'])
            if 'y' in extraArgs:
                if extraArgs['y'] != None:
                    headModel.setY(extraArgs['y'])
            if 'z' in extraArgs:
                if extraArgs['z'] != None:
                    headModel.setZ(extraArgs['z'])
            if 'h' in extraArgs:
                if extraArgs['h'] != None:
                    headModel.setH(extraArgs['h'])
            if 'p' in extraArgs:
                if extraArgs['p'] != None:
                    headModel.setP(extraArgs['p'])
            if 'r' in extraArgs:
                if extraArgs['r'] != None:
                    headModel.setR(extraArgs['r'])
            if 'scale' in extraArgs:
                if extraArgs['scale'] != None:
                    headModel.setScale(*extraArgs['scale'])
            self.headParts.append(headModel)
            if headType == 'prethinker' and self.style.name == 'ambass':
                textureGlass = loader.loadTexture('phase_9/maps/ttcc_ene_prethinker_glass.png')
                headModel.find('**/glass').setTexture(textureGlass, 1)
                headModel.setScale(1)
                headModel.setZ(-.1)
                headModel.setY(-.1)
            if headType == 'prethinker2' and self.style.name == 'ambass':
                textureGlass = loader.loadTexture('phase_9/maps/ttcc_ene_prethinker_glass.png')
                headModel.find('**/glass').setTexture(textureGlass, 1)
                headModel.find('**/brain').hide()
                headModel.setScale(1)
                headModel.setZ(-.3)
            elif headType == 'molder':
                headModel.reparentTo(self.find('**/joint_head'))
                headModel.setScale(.7)
                headModel.setZ(-.4)
                headModel.setH(180)
            elif headType == 'shyster' and self.style.name == 'ang':
                textureGlass = loader.loadTexture('phase_11/maps/ttcc_ene_angelinvestor.png')
                headModel.setTexture(textureGlass, 1)
            elif headType == 'firestarter':
                textureFire = loader.loadTexture('phase_12/maps/ttcc_ene_firestarter_fire.png')
                headModel.find('**/fire0').setTexture(textureFire, 1)
                headModel.find('**/fire1').setTexture(textureFire, 1)
                headModel.find('**/fire2').setTexture(textureFire, 1)
                headModel.find('**/fire3').setTexture(textureFire, 1)
                headModel.find('**/fire4').setTexture(textureFire, 1)
                headModel.find('**/fire5').setTexture(textureFire, 1)
                headModel.setScale(1)
                headModel.setZ(-.1)
            elif headType == 'chairman-a':
                headModel.setScale(.7)
                headModel.setY(-.2)
            elif headType == 'magnate' and self.style.name == 'mg' :
                headModel.setZ(-.1)
            elif headType == 'bagholder' and self.style.name == 'bgh' :
                headModel.setZ(.5)
            elif headType == 'paperhands' and self.style.name == 'pph' :
                headModel.setScale(.6)
            elif headType == 'paperhands' and self.style.name == 'bkeeper' :
                headModel.setScale(.7)
                headModel.setY(-.2)
                headModel.setZ(-.1)
            elif headType == 'deadlock' and self.style.name == 'dl':
                headModel.setZ(-.1)
            elif headType == 'chairman':
                headModel.setScale(.7)
                headModel.setY(-.2)
            elif headType == 'highroller':
                headModel.setScale(1.2)
            elif self.style.name == 'mplayer2':
                headModel.setZ(-.05)
                headModel.setY(-.2)
            elif self.style.name == 'mplayer':
                headModel.setZ(-.05)
                headModel.setY(-.2)
            elif self.style.name == 'sgoat':
                headModel.setTwoSided(True)
            elif headType == 'clo':
                headModel.setZ(-.1)
                headModel.setY(-.1)
                headModel.setX(0)
                headModel.setR(-90)
                headModel.setH(90)
                headModel.setScale(.4)
            elif self.style.name == 'videog':
                headModel.setY(-.2)
            elif self.style.name == 'bcaster':
                headModel.setY(-.2)
            elif headType == 'clubpresident' and not self.style.name == 'fmaker' and not self.style.name == 'director':
                headModel.setZ(-.1)
                headModel.setY(-.2)
            elif headType == 'mouthpiece' and self.style.name == 'wtapper':
                headModel.setScale(1.2)
                headModel.setZ(-.15)
                headModel.setY(-.15)
            elif headType == 'rainmaker':
                hair = None
                for stage in headModel.findAllTextureStages("*hair"):
                    headModel.setTexOffset(stage, 0, 0)
                    # 0 - inversion, 0.2 - heavy rain, 0.4 - oil rain, 0.6 - storm cell, 0.8 - fog
            elif headType == 'rainmaker2':
                hair = None
                for stage in headModel.findAllTextureStages("*hair"):
                    headModel.setTexOffset(stage, 0, 0.2)
                    # 0 - inversion, 0.2 - heavy rain, 0.4 - oil rain, 0.6 - storm cell, 0.8 - fog
            elif headType == 'rainmaker3':
                hair = None
                for stage in headModel.findAllTextureStages("*hair"):
                    headModel.setTexOffset(stage, 0, 0.8)
                    # 0 - inversion, 0.2 - heavy rain, 0.4 - oil rain, 0.6 - storm cell, 0.8 - fog
            elif headType == 'rainmaker4':
                hair = None
                for stage in headModel.findAllTextureStages("*hair"):
                    headModel.setTexOffset(stage, 0, 0.4)
                    # 0 - inversion, 0.2 - heavy rain, 0.4 - oil rain, 0.6 - storm cell, 0.8 - fog
            elif headType == 'rainmaker5':
                hair = None
                for stage in headModel.findAllTextureStages("*hair"):
                    headModel.setTexOffset(stage, 0, 0.6)
                    # 0 - inversion, 0.2 - heavy rain, 0.4 - oil rain, 0.6 - storm cell, 0.8 - fog
            elif headType == 'ceo':
                headModel.setZ(-.2)
                headModel.setY(-.2)
                headModel.setX(0)
                headModel.setR(-90)
                headModel.setH(90)
                headModel.setScale(.3)
            elif headType == 'ceo-a':
                headModel.setZ(-.2)
                headModel.setY(-.2)
                headModel.setX(0)
                headModel.setR(-90)
                headModel.setH(90)
                headModel.setScale(.3)
            elif headType == 'cfo':
                headModel.setZ(-.2)
                headModel.setY(-.2)
                headModel.setX(0)
                headModel.setR(-90)
                headModel.setH(90)
                headModel.setScale(.35)
                headModel.setTwoSided(True)
            elif headType == 'vp':
                headModel.setZ(-.2)
                headModel.setY(-.2)
                headModel.setX(0)
                headModel.setR(-90)
                headModel.setH(90)
                headModel.setScale(.35)
            elif headType == 'redd':
                headModel.setScale(.8)
            elif headType == 'witchhunter':
                headModel.setScale(1.3)
            elif headType == 'dola' and self.style.name == 'phouse':
                headModel.setZ(-.1)
                headModel.setY(-.1)
            elif headType == 'dopr' and self.style.name == 'ubuster' and not self.isSkeleton:
                headModel.setScale(1.3)
                headModel.setZ(.25)
                headModel.setY(-.2)
                texture = loader.loadTexture('phase_9/maps/ttcc_ene_dopr.png')
                headModel.setTexture(texture, 1)
            elif headType == 'dopa' and self.style.name == 'radiog' and not self.isSkeleton:
                headModel.setScale(1.2)
                headModel.setZ(.25)
                headModel.setY(-.2)
                texture = loader.loadTexture('phase_9/maps/ttcc_ene_dopa.png')
                headModel.setTexture(texture, 1)
            elif headType == 'boiler':
                headModel.setScale(.09)
                headModel.setZ(-.3)
                headModel.setY(-.2)
                headModel.setH(180)
            elif headType == 'animatronicStenographer':
                headModel.setH(180)
            elif headType == 'featherbedder':
                headModel.setScale(1)
                headModel.setZ(-.1)
            elif headType == 'treekiller':
                headModel.setZ(-.2)
            elif headType == 'derrickman':
                headModel.setScale(1)
                headModel.setZ(-.1)
            elif headType == 'duckshuffler':
                headModel.setScale(1)
                headModel.setZ(-.1)
                headModel.setY(-.1)
            elif headType == 'chainsaw':
                #for stage in headModel.findAllTextureStages("*Chain"):
                    #headModel.setTexOffset(stage, 2, 2)
                headModel.find('**/Chain').setTwoSided(True)
                if self.isChainsawPhase3:
                    headModel.find('**/bulbLeft').hide()
            elif headType == 'prethinker':
                textureGlass = loader.loadTexture('phase_9/maps/ttcc_ene_prethinker_glass.png')
                headModel.find('**/glass').setTexture(textureGlass, 1)
            elif headType == 'prethinker2':
                textureGlass = loader.loadTexture('phase_9/maps/ttcc_ene_prethinker_glass.png')
                headModel.find('**/glass').setTexture(textureGlass, 1)
                headModel.find('**/brain').hide()
            elif headType == 'autocaddie' and not self.style.name == 'fmaker' and not self.style.name == 'director':
                textureGlass = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_c_exe.png')
                textureGlass2 = loader.loadTexture('phase_12/maps/cc_t_ene_ceo.png')
                headModel.find('**/head').setTexture(textureGlass, 1)
                headModel.setTexture(textureGlass2, 1)
            elif headType == 'autocaddie' and self.style.name == 'director':
                headModel.setZ(.25)
                headModel.setY(-.2)
                headModel.setColor(1, 1, 1, 1)
                textureGlass = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_p_exe.png')
                textureGlass2 = loader.loadTexture('phase_12/maps/cc_t_ene_ceo.png')
                headModel.find('**/head').setTexture(textureGlass, 1)
                headModel.setTexture(textureGlass2, 1)
            elif headType == 'autocaddie' and self.style.name == 'fmaker':
                headModel.setZ(.25)
                headModel.setY(-.2)
                headModel.setColor(1, 1, 1, 1)
                textureGlass = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_g_exe.png')
                textureGlass2 = loader.loadTexture('phase_12/maps/cc_t_ene_ceo.png')
                headModel.find('**/head').setTexture(textureGlass, 1)
                headModel.setTexture(textureGlass2, 1)
            elif headType == 'chainsaw_b':
                headModel.find('**/Chain').setTwoSided(True)
            elif headType == 'chainsaw_c':
                headModel.find('**/Chain').setTwoSided(True)
        else:
            if headType == 'skelecog':
                if base.config.GetBool('want-clash-assets', False):
                    headModel = loader.loadModel(
                        'phase_14/models/char/cog' + string.upper(self.style.body) + '_robot_head-zero')
                    headReferences = headModel.findAllMatches('**/skeleskull_' + string.upper(self.style.body))
                else:
                    headModel = loader.loadModel(
                        'phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-head')
                    headReferences = headModel.findAllMatches('**/suit' + string.upper(self.style.body))
            else:
                if pathOverride:
                    headModel = loader.loadModel(pathOverride + headType)
                else:
                    if modelOverride:
                        headModel = loader.loadModel(modelOverride)
                        headReferences = headModel.findAllMatches('**/' + headType)
                    else:
                        try:
                            headModel = loader.loadModel('phase_' + str(phase) + '/models/char/' + headType)
                            headReferences = headModel.findAllMatches('**/' + headType + '.egg')
                        except:
                            headModel = loader.loadModel('phase_' + str(phase) + filePrefix + 'heads')
                            headReferences = headModel.findAllMatches('**/' + headType)
            if pathOverride:
                if headTexture:
                    pass
                if headColor:
                    headModel.setColor(headColor)
                if 'x' in extraArgs:
                    if extraArgs['x'] != None:
                        headModel.setX(extraArgs['x'])
                if 'y' in extraArgs:
                    if extraArgs['y'] != None:
                        headModel.setY(extraArgs['y'])
                if 'z' in extraArgs:
                    if extraArgs['z'] != None:
                        headModel.setZ(extraArgs['z'])
                if 'h' in extraArgs:
                    if extraArgs['h'] != None:
                        headModel.setH(extraArgs['h'])
                if 'p' in extraArgs:
                    if extraArgs['p'] != None:
                        headModel.setP(extraArgs['p'])
                if 'r' in extraArgs:
                    if extraArgs['r'] != None:
                        headModel.setR(extraArgs['r'])
                if 'scale' in extraArgs:
                    if extraArgs['scale'] != None:
                        headModel.setScale(*extraArgs['scale'])
                self.headParts.append(headModel)
            else:
                for i in range(0, headReferences.getNumPaths()):
                    if self.style.body == 'a' or self.style.body == 'b':
                        headPart = self.instance(headReferences.getPath(i), 'modelRoot', 'to_head')
                    else:
                        headPart = self.instance(headReferences.getPath(i), 'modelRoot', 'joint_head')
                    if headTexture:
                        try:
                            headTex = loader.loadTexture('phase_' + str(phase) + '/maps/' + headTexture)
                        except:
                            try:  # Will work on a more viable replacement for specific phases later.
                                headTex = loader.loadTexture('phase_5/maps/' + headTexture)
                            except:
                                try:
                                    headTex = loader.loadTexture('phase_11/maps/' + headTexture)
                                except:
                                    headTex = loader.loadTexture('phase_14/maps/' + headTexture)
                        headPart.setTexture(headTex, 1)
                    if headColor:
                        headPart.setColor(headColor)
                    if 'x' in extraArgs:
                        if extraArgs['x'] != None:
                            headPart.setX(extraArgs['x'])
                    if 'y' in extraArgs:
                        if extraArgs['y'] != None:
                            headPart.setY(extraArgs['y'])
                    if 'z' in extraArgs:
                        if extraArgs['z'] != None:
                            headPart.setZ(extraArgs['z'])
                    if 'h' in extraArgs:
                        if extraArgs['h'] != None:
                            headPart.setH(extraArgs['h'])
                    if 'p' in extraArgs:
                        if extraArgs['p'] != None:
                            headPart.setP(extraArgs['p'])
                    if 'r' in extraArgs:
                        if extraArgs['r'] != None:
                            headPart.setR(extraArgs['r'])
                    if 'scale' in extraArgs:
                        if extraArgs['scale'] != None:
                            headPart.setScale(*extraArgs['scale'])
                    if headType == 'suitA' or headType == 'suitB' or headType == 'suitC':
                        headPart.setZ(headPart.getZ() + {
                            'suitA': -6.05,
                            'suitB': -5.09477996826172,
                            'suitC': -4.15
                        }[headType])
                        if self.isExecutive or self.isManager:
                            if self.style.name == 'mbr':
                                headPart.setColor(VBase4(0.825, 0.6, 0.425, 1.0))
                            else:
                                if headColor == None:
                                    headPart.setColor({
                                                          'c': SuitDNA.corpPolyColor,
                                                          'l': SuitDNA.legalPolyColor,
                                                          'm': SuitDNA.moneyPolyColor,
                                                          's': SuitDNA.salesPolyColor,
                                                          'g': SuitDNA.boardPolyColor,
                                                          None: VBase4(0.5, 0.5, 0.5, 1.0)
                                                      }[SuitDNA.getSuitDept(self.style.name)])
                        else:
                            if self.style.name == 'mbr':
                                headPart.setColor(VBase4(1.0, 0.25, 0.0, 1.0))
                    self.headParts.append(headPart)
                headModel.removeNode()


    def generateHead(self, headType, headColor=None, headTexture=None, modelOverride=None, pathOverride=None,
                     extraArgs={}, animated=False, additionalAnims=[]):
        self.isSkeleton = 0
        self.isGovernaught = 0
        self.isManager = 0
        self.isExecutive = 0
        if base.config.GetBool('want-new-cogs', False):
            filePrefix, phase = HeadModelDict[self.style.body]
        else:
            filePrefix, phase = ModelDict[self.style.body]
        '''if modelOverride:
            headModel = loader.loadModel(modelOverride)
        else:
            headModel = loader.loadModel('phase_' + str(phase) + filePrefix + 'heads')'''
        if animated:
            if headType == 'skullA' or headType == 'skullB' or headType == 'skullC':
                if headType == 'skullC' or headType == 'skullA' or headType == 'skullB':
                    headModel = Actor.Actor('phase_14/models/char/ttcc_ene_%s-zero.bam' %
                        headType)
                else:
                    headModel = Actor.Actor(
                        'phase_14/models/char/' + string.upper(self.style.body) + '-zero')
                self.generateHeadAnims(
                    'phase_14/models/char/ttcc_ene_skull' + string.upper(self.style.body) + '-',
                    headModel, additionalAnims)
                self.headParts.append(headModel)
                if headTexture:
                    try:
                        texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s%s.png' % (
                                self.style.dept, '_exe' if self.isExecutive or self.isManager else '',))
                    except:
                        texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_unemployed.png')
                else:
                    if self.style.dept == None:
                        texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_unemployed.png')
                    else:
                        texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s%s.png' % (
                                self.style.dept, '_exe' if self.isExecutive or self.isManager else '',))
                for headPart in self.headParts:
                    #texture.setMinfilter(Texture.FTNearestMipmapLinear)
                    #texture.setMagfilter(Texture.FTNearest)
                    headPart.setTexture(texture, 1)
            elif headType == 'insider':
                if headTexture:
                    try:
                        texture = loader.loadTexture('phase_14/maps/cc_t_ene_insider%s.png' % ('_exe' if self.isExecutive or self.isGovernaught else '',))
                    except:
                        texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_unemployed.png')
                else:
                    try:
                        texture = loader.loadTexture('phase_14/maps/cc_t_ene_insider%s.png' % ('_exe' if self.isExecutive or self.isGovernaught else '',))
                    except:
                        texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_unemployed.png')
                for headPart in self.headParts:
                    headPart.setTexture(texture, 1)

            else:
                headModel = Actor.Actor('phase_14/models/char/ttcc_ene_' + headType + '-zero')
                self.generateHeadAnims('phase_14/models/char/ttcc_ene_' + headType + '-', headModel,
                                       additionalAnims)
                self.headParts.append(headModel)
            headModel.reparentTo(self.find('**/joint_head'))
            headModel.setBlend(frameBlend=base.wantSmoothAnims)
            if self.style.name == 'crf':
                headModel.loop('neutral', fromFrame=0, toFrame=22)
            elif self.style.name == 'mad':
                headModel.loop('neutral', fromFrame=0, toFrame=22)
            elif self.style.name == 'dsf':
                headModel.loop('neutral', fromFrame=0, toFrame=22)
            elif self.style.name == 'lit':
                headModel.loop('zero')
            else:
                headModel.loop('neutral')
            if 'x' in extraArgs:
                if extraArgs['x'] != None:
                    headModel.setX(extraArgs['x'])
            if 'y' in extraArgs:
                if extraArgs['y'] != None:
                    headModel.setY(extraArgs['y'])
            if 'z' in extraArgs:
                if extraArgs['z'] != None:
                    headModel.setZ(extraArgs['z'])
            if 'h' in extraArgs:
                if extraArgs['h'] != None:
                    headModel.setH(extraArgs['h'])
            if 'p' in extraArgs:
                if extraArgs['p'] != None:
                    headModel.setP(extraArgs['p'])
            if 'r' in extraArgs:
                if extraArgs['r'] != None:
                    headModel.setR(extraArgs['r'])
            if 'scale' in extraArgs:
                if extraArgs['scale'] != None:
                    headModel.setScale(*extraArgs['scale'])
            self.headParts.append(headModel)
            if headType == 'prethinker' and self.style.name == 'gtk':
                headModel.setScale(1)
                headModel.setZ(-.1)
            elif headType == 'molder':
                headModel.reparentTo(self.find('**/joint_head'))
                headModel.setScale(.7)
                headModel.setZ(-.4)
                headModel.setH(180)
            elif headType == 'chairman-a':
                headModel.setScale(.7)
                headModel.setY(-.2)
            elif headType == 'magnate' and self.style.name == 'rng' :
                headModel.setZ(-.1)
            elif headType == 'magnate' and self.style.name == 'jgd' :
                headModel.setZ(-.1)
            elif headType == 'magnate' and self.style.name == 'tlr' :
                headModel.setZ(-.1)
            elif headType == 'bagholder' and self.style.name == 'ca' :
                headModel.setZ(.5)
            elif headType == 'paperhands' and self.style.name == 'cn' :
                headModel.setScale(.6)
            elif headType == 'paperhands' and self.style.name == 'bkeeper' :
                headModel.setScale(.7)
                headModel.setY(-.2)
                headModel.setZ(-.1)
            elif headType == 'deadlock' and self.style.name == 'hho':
                headModel.setZ(-.1)
            elif headType == 'sharkwatcher' and self.style.name == 'ffm':
                headModel.setY(-.1)
            elif headType == 'chairman':
                headModel.setScale(.7)
                headModel.setY(-.2)
            elif headType == 'highroller':
                headModel.setScale(1.2)
            elif self.style.name == 'tb':
                headModel.setZ(-.05)
                headModel.setY(-.3)
            elif self.style.name == 'ts':
                headModel.setZ(-.05)
                headModel.setY(-.3)
            elif headType == 'clo':
                headModel.setZ(-.1)
                headModel.setY(-.1)
                headModel.setX(0)
                headModel.setR(-90)
                headModel.setH(90)
                headModel.setScale(.4)
            elif headType == 'ceo':
                headModel.setZ(-.1)
                headModel.setY(-.1)
                headModel.setX(0)
                headModel.setR(-90)
                headModel.setH(90)
                headModel.setScale(.4)
            elif headType == 'ceo-a':
                headModel.setZ(-.1)
                headModel.setY(-.1)
                headModel.setX(0)
                headModel.setR(-90)
                headModel.setH(90)
                headModel.setScale(.4)
            elif headType == 'cfo':
                headModel.setZ(-.1)
                headModel.setY(-.1)
                headModel.setX(0)
                headModel.setR(-90)
                headModel.setH(90)
                headModel.setScale(.4)
            elif headType == 'vp':
                headModel.setZ(-.1)
                headModel.setY(-.1)
                headModel.setX(0)
                headModel.setR(-90)
                headModel.setH(90)
                headModel.setScale(.4)
            elif self.style.name == 'prr':
                headModel.setY(-.2)
            elif headType == 'clubpresident':
                headModel.setZ(-.1)
                headModel.setY(-.2)
            elif headType == 'mouthpiece' and self.style.name == 'frs':
                headModel.setScale(1.2)
                headModel.setZ(-.15)
                headModel.setY(-.15)
            elif headType == 'plutocrat' and self.style.name == 'auh':
                headModel.setScale(.85)
                headModel.setZ(-.1)
                headModel.setY(-.1)
            elif headType == 'advocate' and self.style.name == 'bdb':
                headModel.setScale(1.05)
                headModel.setZ(-.1)
                headModel.setY(-.2)
                headModel.setY(0)
            elif headType == 'redd':
                headModel.setScale(.8)
            elif headType == 'witchhunter':
                headModel.setScale(1.3)
            elif headType == 'multislacker' and self.style.name == 'blr':
                headModel.setZ(-.1)
                headModel.setY(-.1)
            elif headType == 'dola' and self.style.name == 'cp':
                headModel.setZ(-.1)
                headModel.setY(-.1)
            elif headType == 'judy':
                headModel.setScale(1.05)
                headModel.setZ(-.1)
                headModel.setY(-.1)
            elif headType == 'dopr' and self.style.name == 'dsk' and not self.isSkeleton:
                headModel.setScale(1.3)
            elif headType == 'dopa' and self.style.name == 'blr' and not self.isSkeleton:
                headModel.setScale(1.2)
            elif headType == 'boiler':
                headModel.setScale(.09)
                headModel.setZ(-.3)
                headModel.setY(-.2)
                headModel.setH(180)
            elif headType == 'needlenose' and self.style.name == 'dfh':
                headModel.setScale(1.05)
                headModel.setZ(-.1)
                headModel.setY(-.1)
            elif headType == 'featherbedder':
                headModel.setScale(1)
                headModel.setZ(-.1)
            elif headType == 'treekiller':
                headModel.setZ(-.2)
            elif headType == 'derrickman':
                headModel.setScale(1)
                headModel.setZ(-.1)
            elif headType == 'backstabber':
                headModel.setScale(1.1)
                headModel.setZ(-.1)
                headModel.setY(-.1)
            elif headType == 'duckshuffler':
                headModel.setScale(1)
                headModel.setZ(-.1)
                headModel.setY(-.1)
            elif headType == 'chainsaw':
                headModel.find('**/Chain').setTwoSided(True)
            elif headType == 'chainsaw_b':
                headModel.find('**/Chain').setTwoSided(True)
            elif headType == 'chainsaw_c':
                headModel.find('**/Chain').setTwoSided(True)
        else:
            if headType == 'skelecog':
                if base.config.GetBool('want-clash-assets', True):
                    headModel = loader.loadModel(
                        'phase_14/models/char/' + string.upper(self.style.body) + '_robot_head-zero')
                    headReferences = headModel.findAllMatches('**/skeleskull_' + string.upper(self.style.body))
                else:
                    headModel = loader.loadModel(
                        'phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-head')
                    headReferences = headModel.findAllMatches('**/suit' + string.upper(self.style.body))
            else:
                if pathOverride:
                    headModel = loader.loadModel(pathOverride + headType)
                else:
                    if modelOverride:
                        headModel = loader.loadModel(modelOverride)
                        headReferences = headModel.findAllMatches('**/' + headType)
                    else:
                        try:
                            headModel = loader.loadModel('phase_' + str(phase) + '/models/char/' + headType)
                            headReferences = headModel.findAllMatches('**/' + headType + '.bam')
                        except:
                            headModel = loader.loadModel('phase_' + str(phase) + filePrefix + 'heads')
                            headReferences = headModel.findAllMatches('**/' + headType)
            if pathOverride:
                if headTexture:
                    pass
                if headColor:
                    headModel.setColor(headColor)
                if 'x' in extraArgs:
                    if extraArgs['x'] != None:
                        headModel.setX(extraArgs['x'])
                if 'y' in extraArgs:
                    if extraArgs['y'] != None:
                        headModel.setY(extraArgs['y'])
                if 'z' in extraArgs:
                    if extraArgs['z'] != None:
                        headModel.setZ(extraArgs['z'])
                if 'h' in extraArgs:
                    if extraArgs['h'] != None:
                        headModel.setH(extraArgs['h'])
                if 'p' in extraArgs:
                    if extraArgs['p'] != None:
                        headModel.setP(extraArgs['p'])
                if 'r' in extraArgs:
                    if extraArgs['r'] != None:
                        headModel.setR(extraArgs['r'])
                if 'scale' in extraArgs:
                    if extraArgs['scale'] != None:
                        headModel.setScale(*extraArgs['scale'])
                self.headParts.append(headModel)
            else:
                for i in range(0, headReferences.getNumPaths()):
                    if self.style.body == 'a' or self.style.body == 'b':
                        headPart = self.instance(headReferences.getPath(i), 'modelRoot', 'joint_head')
                    else:
                        headPart = self.instance(headReferences.getPath(i), 'modelRoot', 'joint_head')
                    if self.headTexture:
                        try:
                            headTex = loader.loadTexture('phase_' + str(phase) + '/maps/' + headTexture)
                        except:
                            try:  # Will work on a more viable replacement for specific phases later.
                                headTex = loader.loadTexture('phase_5/maps/' + headTexture)
                            except:
                                try:
                                    headTex = loader.loadTexture('phase_11/maps/' + headTexture)
                                except:
                                    headTex = loader.loadTexture('phase_14/maps/' + headTexture)
                        #headTex.setMinfilter(Texture.FTLinearMipmapLinear)
                        #headTex.setMagfilter(Texture.FTLinear)
                        headPart.setTexture(headTex, 1)
                    if headColor:
                        headPart.setColor(headColor)
                    if 'x' in extraArgs:
                        if extraArgs['x'] != None:
                            headPart.setX(extraArgs['x'])
                    if 'y' in extraArgs:
                        if extraArgs['y'] != None:
                            headPart.setY(extraArgs['y'])
                    if 'z' in extraArgs:
                        if extraArgs['z'] != None:
                            headPart.setZ(extraArgs['z'])
                    if 'h' in extraArgs:
                        if extraArgs['h'] != None:
                            headPart.setH(extraArgs['h'])
                    if 'p' in extraArgs:
                        if extraArgs['p'] != None:
                            headPart.setP(extraArgs['p'])
                    if 'r' in extraArgs:
                        if extraArgs['r'] != None:
                            headPart.setR(extraArgs['r'])
                    if 'scale' in extraArgs:
                        if extraArgs['scale'] != None:
                            headPart.setScale(*extraArgs['scale'])
                    if headType == 'suitA' or headType == 'suitB' or headType == 'suitC':
                        headPart.setZ(headPart.getZ() + {
                            'suitA': -6.05,
                            'suitB': -5.09477996826172,
                            'suitC': -4.15
                        }[headType])
                        if self.isExecutive or self.isManager:
                            if self.style.name == 'mbr':
                                headPart.setColor(VBase4(0.825, 0.6, 0.425, 1.0))
                            else:
                                if headColor == None:
                                    headPart.setColor({
                                                          'c': SuitDNA.corpPolyColor,
                                                          'l': SuitDNA.legalPolyColor,
                                                          'm': SuitDNA.moneyPolyColor,
                                                          's': SuitDNA.salesPolyColor,
                                                          'g': SuitDNA.boardPolyColor,
                                                          None: VBase4(0.5, 0.5, 0.5, 1.0)
                                                      }[SuitDNA.getSuitDept(self.style.name)])
                        else:
                            if self.style.name == 'mbr':
                                headPart.setColor(VBase4(1.0, 0.25, 0.0, 1.0)
                                                  )
                    self.headParts.append(headPart)
                headModel.removeNode()

    def generateHead2(self, headType):
        filePrefix, phase = ModelDict[self.style.body]
        headModel = loader.loadModel('phase_' + str(phase) + filePrefix + 'heads')
        if headType == 'barrister' and self.style.body == 'a':
                headModel = loader.loadModel('phase_4/models/char/suitB-heads')
        if headType == 'loanshark' and self.style.body == 'a':
                headModel = loader.loadModel('phase_4/models/char/suitB-heads')
        if headType == 'beancounter' and self.style.body == 'a':
                headModel = loader.loadModel('phase_4/models/char/suitB-heads')
        if headType == 'telemarketer' and self.style.body == 'a':
                headModel = loader.loadModel('phase_4/models/char/suitB-heads')
        if headType == 'scopejp187187' and self.style.body == 'a':
                headModel = loader.loadModel('phase_4/models/char/suitB-heads')
        if headType == 'bandjp187187' and self.style.body == 'a':
                headModel = loader.loadModel('phase_4/models/char/suitB-heads')
        if headType == 'hatjp187187' and self.style.body == 'a':
                headModel = loader.loadModel('phase_4/models/char/suitB-heads')
        if headType == 'bigfish' and self.style.name == 'bfh2':
                headModel = loader.loadModel('phase_14/models/char/ttcc_ene_bigfish-zero')
        if headType == 'flunky' and self.style.body == 'a':
                headModel = loader.loadModel('phase_3.5/models/char/suitC-heads')
        if headType == 'beret' and self.style.body == 'a':
                headModel = loader.loadModel('phase_3.5/models/char/suitC-heads')
        if headType == 'root' and self.style.name == 'bsht':
            headModel = loader.loadModel('phase_14/models/char/yesman')
        if headType == 'root' and self.style.name == 'whistleb':
            headModel = loader.loadModel('phase_14/models/char/whistleblower')
        if headType == 'root' and self.style.name == 'ksp':
            headModel = loader.loadModel('phase_14/models/char/mingler')
        if headType == 'root' and self.style.name == 'ppl':
            headModel = loader.loadModel('phase_14/models/char/tf_new')
        if headType == 'root' and self.style.name == 'dc':
            headModel = loader.loadModel('phase_14/models/char/doublecross')
        if headType == 'root' and self.style.name == 'fct':
            headModel = loader.loadModel('phase_14/models/char/fatcat')
        if headType == 'root' and self.style.name == 'fcs':
            headModel = loader.loadModel('phase_14/models/char/forecaster')
        if headType == 'root' and self.style.name == 'stg':
            headModel = loader.loadModel('phase_14/models/char/stooge')
        if headType == 'root' and self.style.name == 'ath':
            headModel = loader.loadModel('phase_14/models/char/pencilpusher')
        if headType == 'root' and self.style.name == 'bsd':
            headModel = loader.loadModel('phase_14/models/char/backseat')
        if headType == 'root' and self.style.name == 'gld':
            headModel = loader.loadModel('phase_14/models/char/GoldenGoose')
        if headType == 'root' and self.style.name == 'dcw':
            headModel = loader.loadModel('phase_14/models/char/backstabber')
        if headType == 'root' and self.style.name == 'wnk':
            headModel = loader.loadModel('phase_14/models/char/whiteknight')
        if headType == 'root' and self.style.name == 'std':
            headModel = loader.loadModel('phase_14/models/char/yesman')
        if headType == 'root' and self.style.name == 'std2':
            headModel = loader.loadModel('phase_14/models/char/yesman')
        if headType == 'root' and self.style.name == 'sbg':
            headModel = loader.loadModel('phase_14/models/char/sandbagger')
        if headType == 'root' and self.style.name == 'key':
            headModel = loader.loadModel('phase_14/models/char/keyboard-warrior')
        if headType == 'root' and self.style.name == 'pyc':
            headModel = loader.loadModel('phase_14/models/char/python-charmer_head')
        if headType == 'root' and self.style.name == 'sdb':
            headModel = loader.loadModel('phase_14/models/char/shotgun-debugger_head')
        if headType == 'root' and self.style.name == 'shy':
            headModel = loader.loadModel('phase_14/models/char/shylock')
        if headType == 'Blowhard' and self.style.name == 'blh':
                headModel = loader.loadModel('phase_3.5/models/char/ttrm_m_ene_head_blowhard')
        if headType == 'industryTitan':
                headModel = loader.loadModel('phase_3.5/models/char/ttrpg_tech-heads')
        if headType == 'blackHat':
                headModel = loader.loadModel('phase_3.5/models/char/ttrpg_tech-heads')
        if headType == 'dataHoarder':
            headModel = loader.loadModel('phase_3.5/models/char/ttrpg_tech-heads')
        if headType == 'codeMonkey':
            headModel = loader.loadModel('phase_3.5/models/char/ttrpg_tech-heads')
        if headType == 'brainiac':
            headModel = loader.loadModel('phase_3.5/models/char/ttrpg_tech-heads')
        if headType == 'computerWizard':
            headModel = loader.loadModel('phase_3.5/models/char/ttrpg_tech-heads')
        if headType == 'connoisseur_hat' and self.style.name == 'cn':
                headModel = loader.loadModel('phase_14/models/char/ttcc_ene_connoisseur')
        if headType == 'connoisseur_head' and self.style.name == 'cn':
                headModel = loader.loadModel('phase_14/models/char/ttcc_ene_connoisseur')
        if headType == 'connoisseur_monocle' and self.style.name == 'cn':
                headModel = loader.loadModel('phase_14/models/char/ttcc_ene_connoisseur')
        if headType == 'movershaker' and self.style.body == 'c':
                headModel = loader.loadModel('phase_4/models/char/suitB-heads')
        if headType == 'conveyancer_belt' and self.style.body == 'a':
                headModel = loader.loadModel('phase_14/models/char/ttcc_ene_conveyancer_belt')
        if headType == 'bigfish' and self.style.body == 'a':
                headModel = loader.loadModel('phase_3.5/models/char/suitC-heads')
        if headType == 'overtime' and self.style.body == 'a':
                headModel = loader.loadModel('phase_3.5/models/char/ttoff_m_ene_overtime')
        if headType == 'ambulancechaser' and self.style.body == 'a':
                headModel = loader.loadModel('phase_4/models/char/suitB-heads')
        if headType == 'gumshoe':
            headModel = loader.loadModel('phase_4/models/char/pressbot-heads')
            headModel.setH(180)
        if headType == 'hackette':
            headModel = loader.loadModel('phase_4/models/char/pressbot-heads')
            headModel.setH(180)
        if headType == 'newshound':
            headModel = loader.loadModel('phase_4/models/char/pressbot-heads')
            headModel.setH(180)
        if headType == 'anchorman':
            headModel = loader.loadModel('phase_4/models/char/pressbot-heads')
            headModel.setH(180)
        if headType == 'paperboy':
            headModel = loader.loadModel('phase_4/models/char/pressbot-heads')
            headModel.setH(180)
        if headType == 'shutterbug':
            headModel = loader.loadModel('phase_4/models/char/pressbot-heads')
            headModel.setH(180)
        if headType == 'ghostwriter':
            headModel = loader.loadModel('phase_4/models/char/pressbot-heads')
            headModel.setH(180)
        if headType == 'gazetteer':
            headModel = loader.loadModel('phase_4/models/char/pressbot-heads')
            headModel.setH(180)
        if headType == 'ttr_m_ene_lawbotClerk' and self.style.body == 'b':
            headModel = loader.loadModel('phase_14/models/char/ttr_m_ene_lawbotClerk')
        if headType == 'ttr_m_ene_cashbotAuditor' and self.style.body == 'c':
            headModel = loader.loadModel('phase_14/models/char/ttr_m_ene_cashbotAuditor')
        if headType == 'bossbotClubPresidentEarrings' and self.style.body == 'a':
            headModel = loader.loadModel('phase_14/models/char/ttr_m_ene_bossbotClubPresident')
        if headType == 'bossbotClubPresidentHead' and self.style.body == 'a':
            headModel = loader.loadModel('phase_14/models/char/ttr_m_ene_bossbotClubPresident')
        if headType == 'bossbotClubPresidentHair' and self.style.body == 'a':
            headModel = loader.loadModel('phase_14/models/char/ttr_m_ene_bossbotClubPresident')
        if headType == 'sellbotForemanHead' and self.style.body == 'b':
            headModel = loader.loadModel('phase_14/models/char/ttr_m_ene_sellbotForeman')
        if headType == 'sellbotForemanGlasses' and self.style.body == 'b':
            headModel = loader.loadModel('phase_14/models/char/ttr_m_ene_sellbotForeman')
        if headType == 'sellbotForemanEyebrows' and self.style.body == 'b':
            headModel = loader.loadModel('phase_14/models/char/ttr_m_ene_sellbotForeman')
        if headType == 'sellbotForemanHat' and self.style.body == 'b':
            headModel = loader.loadModel('phase_14/models/char/ttr_m_ene_sellbotForeman')
        if headType == 'skeleskull_A' and self.style.name == 'ubuster':
            headModel = loader.loadModel('phase_5/models/char/skullbase')
            headModel.setZ(-.1)
            headModel.setY(-.2)
            textureGlass = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_s_exe.png')
            headModel.setTexture(textureGlass, 1)
        if headType == 'skeleskull_A' and self.style.name == 'radiog':
            headModel = loader.loadModel('phase_5/models/char/skullbase')
            headModel.setZ(-.1)
            headModel.setY(-.2)
            textureGlass = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_s_exe.png')
            headModel.setTexture(textureGlass, 1)
        if headType == 'skeleskull_A' and self.style.name == 'fmaker':
            headModel = loader.loadModel('phase_5/models/char/skullbase')
            headModel.setZ(-.1)
            headModel.setY(-.2)
            textureGlass = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_g_exe.png')
            headModel.setTexture(textureGlass, 1)
        if headType == 'skeleskull_A' and self.style.name == 'director':
            headModel = loader.loadModel('phase_5/models/char/skullbase')
            headModel.setZ(-.1)
            headModel.setY(-.2)
            textureGlass = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_p_exe.png')
            headModel.setTexture(textureGlass, 1)
        if headType == 'ear01':
            headModel = loader.loadModel('phase_4/models/char/mole_cog')
            headModel.setZ(-.4)
            headModel.setScale(.7)
            headModel.setH(180)
        if headType == 'head':
            headModel = loader.loadModel('phase_4/models/char/mole_cog')
            headModel.setZ(-.4)
            headModel.setScale(.7)
            headModel.setH(180)
        if headType == 'ear03':
            headModel = loader.loadModel('phase_4/models/char/mole_cog')
            headModel.setZ(-.4)
            headModel.setScale(.7)
            headModel.setH(180)
        if headType == 'ear04':
            headModel = loader.loadModel('phase_4/models/char/mole_cog')
            headModel.setZ(-.4)
            headModel.setScale(.7)
            headModel.setH(180)
        if headType == 'ear02':
            headModel = loader.loadModel('phase_4/models/char/mole_cog')
            headModel.setZ(-.4)
            headModel.setScale(.7)
            headModel.setH(180)
        if headType == 'angel_wings':
            headModel = loader.loadModel('phase_13/models/props/angel_wings')
            headModel.setZ(1)
            headModel.setScale(1.5)
        if headType == 'angel_halo':
            headModel = loader.loadModel('phase_13/models/props/angel_halo')
            headModel.setZ(1)
            headModel.setScale(1.5)
        if headType == 'antenna_stick':
            headModel = loader.loadModel('phase_4/models/char/mole_cog')
            headModel.setZ(-.4)
            headModel.setScale(.7)
            headModel.setH(180)
        if headType == 'antenna_ball':
            headModel = loader.loadModel('phase_4/models/char/mole_cog')
            headModel.setZ(-.4)
            headModel.setScale(.7)
            headModel.setH(180)
        if headType == 'eye_mouth':
            headModel = loader.loadModel('phase_4/models/char/mole_cog')
            headModel.setZ(-.4)
            headModel.setScale(.7)
            headModel.setH(180)
        if headType == 'pupils':
            headModel = loader.loadModel('phase_4/models/char/mole_cog')
            headModel.setZ(-.4)
            headModel.setScale(.7)
            headModel.setH(180)
        if headType == 'tightwad' and self.style.body == 'b':
            headModel = loader.loadModel('phase_3.5/models/char/suitC-heads')
        if headType == 'numbercruncher' and self.style.body == 'c':
            headModel = loader.loadModel('phase_4/models/char/suitA-heads')
        headReferences = headModel.findAllMatches('**/' + headType)
        for i in xrange(0, headReferences.getNumPaths()):
            headPart = self.instance(headReferences.getPath(i), 'modelRoot', 'joint_head')
            headPart.setTwoSided(True)
            if self.style.name == 'ang' and headType == 'angel_wings':
                headPart.setZ(1.25)
                headPart.setScale(1.25)
            if self.style.name == 'ang' and headType == 'angel_halo':
                headPart.setZ(1.25)
                headPart.setScale(.75)
            if headType == 'skeleskull_A':
                headPart.setY(-.2)
                headPart.setZ(-.1)
            if self.style.name == 'key':
                headPart.setH(180)
            if self.style.name == 'mldr':
                headPart.setZ(-.4)
                headPart.setScale(.7)
                headPart.setH(180)
            if self.style.name == 'bfh2':
                headPart.setX(-.03)
                headPart.setZ(.1)
                headPart.setY(.1)
            if self.style.name == 'p':
                headPart.setX(.03)
            if self.style.name == 'dc':
                headPart.setZ(-.01)
            if self.style.name == 'ath':
                headPart.setX(.03)
            if self.style.name == 'blh':
                headPart.setY(.1)
            if self.style.name == 'ppl':
                headPart.setZ(0.9)
                headPart.setY(1)
                headPart.setX(-0.05)
                headPart.setScale(4)
            if self.style.name == 'fct':
                headPart.setH(180)
                headPart.setScale(1.15)
            if self.style.name == 'fcs':
                headPart.setH(180)
            if self.style.name == 'ovt':
                headPart.setY(-.2)
                headPart.setScale(1.05)
            if self.style.name == 'gld':
                headPart.setScale(0.8)
            if self.style.name == 'watchm':
                headPart.setY(-.2)
                headPart.setScale(1.05)
            if self.style.name == 'blk':
                headPart.setY(.1)
            if headType == 'root' and self.style.name == 'whistleb': #whistleblower
                headPart.setH(90)
                headPart.setP(90)
                headPart.setR(-90)
                headPart.setScale(1.1)
                headPart.setZ(-.1)
            if headType == 'root': #whistleblower
                headPart.setH(90)
                headPart.setP(90)
                headPart.setR(-90)
                #headPart.setZ(-.1)
            if self.style.name == 'gms':
                headPart.setH(180)
                headPart.setZ(-.1)
            if self.style.name == 'anc':
                headPart.setH(180)
                headPart.setZ(-.1)
                headPart.setY(-.2)
            if self.style.name == 'gzt':
                headPart.setH(180)
                headPart.setZ(-.1)
                headPart.setY(-.1)
            if self.style.name == 'hck':
                headPart.setH(180)
                headPart.setZ(-.1)
                headPart.setY(-.1)
            if self.style.name == 'ppb':
                headPart.setH(180)
                headPart.setZ(-.1)
            if self.style.name == 'ghw':
                headPart.setH(180)
                headPart.setZ(-.1)
                headPart.setY(-.2)
            if self.style.name == 'blh':
                headPart.setH(180)
            if self.style.name == 'shb':
                headPart.setH(180)
                headPart.setZ(-.1)
            if self.style.name == 'nsh':
                headPart.setH(180)
                headPart.setZ(-.1)
                headPart.setY(-.2)
            if self.style.name == 'rus':
                headPart.setZ(-.1)
                headPart.setY(-.1)
                headPart.setScale(1.05)
                headPart.setH(0)
            if self.headTexture:
                headTex = loader.loadTexture('phase_' + str(phase) + '/maps/' + self.headTexture)
                headPart.setTexture(headTex, 1)
            if self.headColor:
                headPart.setColor(self.headColor)
            self.headParts.append(headPart)



    def generateHeadAnims(self, path, cActor, additionalAnims=[]):
        anims = ['neutral', 'death', 'grunt', 'murmur', 'question', 'statement', 'neutral-hurt', 'neutral-lured',
                 'stun', 'enraged', 'insurance', 'bellow', 'ace-in-the-hole', 'wheelspin', 'healing-bell', 'revvedup',
                 'scabbard', 'sparkplug', 'throttle', 'throttle2', 'mouthdrop', 'dive', 'bust',
                 'emergeHead', 'exitWater', 'underwaterHit', 'gamble', 'cigar-smoke', 'gsnap', 'overclocked',
                 'come-on', 'zero' ]
        for anim in additionalAnims:
            anims.append(anim)
        animList = {}
        for anim in anims:
            if self.style.name == 'bonetyred' and anim == 'neutral':
                animList['neutral'] = path + 'neutral-hurt.bam'
            else:
                animList[anim] = path + anim + '.bam'
        cActor.loadAnims(animList)

    def generateCorporateMedallion2(self):
        icons = loader.loadModel('phase_3.5/models/char/ttcc_ene_insignias')
        icons2 = loader.loadModel('phase_3.5/models/gui/cog_icons')
        dept = self.style.dept
        if base.config.GetBool('want-new-cogs', 0):
            chestNull = self.find('**/def_joint_attachMeter')
            if chestNull.isEmpty():
                chestNull = self.find('**/joint_attachMeter')
        else:
            chestNull = self.find('**/joint_attachMeter')
        if dept == 'c':
            self.corpMedallion = icons.find('**/emblem_corp').copyTo(chestNull)
        elif dept == 's':
            self.corpMedallion = icons.find('**/emblem_sales').copyTo(chestNull)
        elif dept == 'l':
            self.corpMedallion = icons.find('**/emblem_legal').copyTo(chestNull)
        elif dept == 'm':
            self.corpMedallion = icons.find('**/emblem_money').copyTo(chestNull)
        elif dept == 'g':
            self.corpMedallion = icons.find('**/emblem_legal').copyTo(chestNull)
            texture = loader.loadTexture('phase_3/maps/ttcc_suit_insignias_palette4.png')
            self.corpMedallion.setTexture(texture, 1)
        elif dept == 't':
            self.corpMedallion = icons.find('**/emblem_legal').copyTo(chestNull)
            texture = loader.loadTexture('phase_3/maps/ttcc_suit_insignias_palette2.png')
            self.corpMedallion.setTexture(texture, 1)
        elif dept == 'p':
            self.corpMedallion = icons.find('**/emblem_legal').copyTo(chestNull)
            texture = loader.loadTexture('phase_3/maps/ttcc_suit_insignias_palette3.png')
            self.corpMedallion.setTexture(texture, 1)

        self.corpMedallion.setPosHprScale(0, -1, 0, 180.0, 0.0, 0.0, 0, 0, 0)
        self.corpMedallion.setColor(self.medallionColors[dept])
        if self.style.name == 'fhj':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'hrollers':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'bcaster':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'hroller':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'hroller':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'nn':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'dhr':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'mm':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'bfh':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'bfh2':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'judy':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'ang':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'ddiver':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'sh':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'mouthp':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'shb':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'hck':
            self.corpMedallion.setZ(.2)
        icons.removeNode()

    def generateCorporateMedallion3(self):
        icons = loader.loadModel('phase_3.5/models/char/ttcc_ene_insignias')
        icons2 = loader.loadModel('phase_3.5/models/gui/cog_icons')
        dept = self.style.dept
        if base.config.GetBool('want-new-cogs', 0):
            chestNull = self.find('**/def_joint_attachMeter')
            if chestNull.isEmpty():
                chestNull = self.find('**/joint_attachMeter')
        else:
            chestNull = self.find('**/joint_attachMeter')
        if dept == 'c':
            self.corpMedallion = icons.find('**/emblem_corp').copyTo(chestNull)
        elif dept == 's':
            self.corpMedallion = icons.find('**/emblem_sales').copyTo(chestNull)
        elif dept == 'l':
            self.corpMedallion = icons.find('**/emblem_legal').copyTo(chestNull)
        elif dept == 'm':
            self.corpMedallion = icons.find('**/emblem_money').copyTo(chestNull)
        elif dept == 'g':
            self.corpMedallion = icons.find('**/emblem_legal').copyTo(chestNull)
            texture = loader.loadTexture('phase_3/maps/ttcc_suit_insignias_palette4.png')
            self.corpMedallion.setTexture(texture, 1)
        elif dept == 't':
            self.corpMedallion = icons.find('**/emblem_legal').copyTo(chestNull)
            texture = loader.loadTexture('phase_3/maps/ttcc_suit_insignias_palette2.png')
            self.corpMedallion.setTexture(texture, 1)
        elif dept == 'p':
            self.corpMedallion = icons.find('**/emblem_legal').copyTo(chestNull)
            texture = loader.loadTexture('phase_3/maps/ttcc_suit_insignias_palette3.png')
            self.corpMedallion.setTexture(texture, 1)

        self.corpMedallion.setPosHprScale(0, -1, 0, 180.0, 0.0, 0.0, 0, 0, 0)
        self.corpMedallion.setColor(self.medallionColors[dept])
        if self.style.name == 'fhj':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'hrollers':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'bcaster':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'hroller':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'hroller':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'nn':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'dhr':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'mm':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'bfh':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'bfh2':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'judy':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'ang':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'ddiver':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'sh':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'mouthp':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'shb':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'hck':
            self.corpMedallion.setZ(.2)
        icons.removeNode()


    def generateCorporateTie(self, modelPath = None):
        if not modelPath:
            modelPath = self
        dept = self.style.dept
        tie = modelPath.find('**/tie')
        if tie.isEmpty():
            self.notify.warning('skelecog has no tie model!!!')
            return

        if dept == 'c':
            tieTex = loader.loadTexture('phase_5/maps/cog_robot_tie_boss.jpg')
        elif dept == 's':
            tieTex = loader.loadTexture('phase_5/maps/cog_robot_tie_sales.jpg')
        elif dept == 'l':
            tieTex = loader.loadTexture('phase_5/maps/cog_robot_tie_legal.jpg')
        elif dept == 'm':
            tieTex = loader.loadTexture('phase_5/maps/cog_robot_tie_money.jpg')
        elif dept == 'g':
            tieTex = loader.loadTexture('phase_5/maps/cog_robot_tie_board.jpg')
        elif dept == 't':
            tieTex = loader.loadTexture('phase_5/maps/cog_robot_tie_sales.jpg')
        elif dept == 'p':
            tieTex = loader.loadTexture('phase_5/maps/cog_robot_tie_sales.jpg')
        #tieTex.setMinfilter(Texture.FTLinearMipmapLinear)
        #tieTex.setMagfilter(Texture.FTLinear)
        tie.setTexture(tieTex, 1)

    def generateCorporateMedallion(self):
        icons = loader.loadModel('phase_3.5/models/char/ttcc_ene_insignias')
        icons2 = loader.loadModel('phase_3.5/models/gui/cog_icons')
        dept = self.style.dept
        if base.config.GetBool('want-new-cogs', 0):
            chestNull = self.find('**/def_joint_attachMeter')
            if chestNull.isEmpty():
                chestNull = self.find('**/joint_attachMeter')
        else:
            chestNull = self.find('**/joint_attachMeter')
        if dept == 'c':
            self.corpMedallion = icons.find('**/emblem_corp').copyTo(chestNull)
        elif dept == 's':
            self.corpMedallion = icons.find('**/emblem_sales').copyTo(chestNull)
        elif dept == 'l':
            self.corpMedallion = icons.find('**/emblem_legal').copyTo(chestNull)
        elif dept == 'm':
            self.corpMedallion = icons.find('**/emblem_money').copyTo(chestNull)
        elif dept == 'g':
            self.corpMedallion = icons.find('**/emblem_legal').copyTo(chestNull)
            texture = loader.loadTexture('phase_3/maps/ttcc_suit_insignias_palette4.png')
            self.corpMedallion.setTexture(texture, 1)
        elif dept == 't':
            self.corpMedallion = icons.find('**/emblem_legal').copyTo(chestNull)
            texture = loader.loadTexture('phase_3/maps/ttcc_suit_insignias_palette2.png')
            self.corpMedallion.setTexture(texture, 1)
        elif dept == 'p':
            self.corpMedallion = icons.find('**/emblem_legal').copyTo(chestNull)
            texture = loader.loadTexture('phase_3/maps/ttcc_suit_insignias_palette3.png')
            self.corpMedallion.setTexture(texture, 1)
        self.corpMedallion.setH(180.0)
        self.corpMedallion.setColor(self.medallionColors[dept])
        if self.style.body == 'c':
            self.corpMedallion.setY(.05)
        if self.style.body == 'a':
            self.corpMedallion.setY(-.1)
            self.corpMedallion.setZ(-.1)
        if self.style.name == 'fhj':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'mad':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'dsf':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'crf':
            self.corpMedallion.setScale(0)
        else:
            self.corpMedallion.setScale(1.175)
        if self.style.name == 'fhj':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'hrollers':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'bcaster':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'hroller':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'hroller':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'nn':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'dhr':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'mm':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'bfh':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'bfh2':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'judy':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'ang':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'ddiver':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'sh':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'mouthp':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'hck':
            self.corpMedallion.setZ(.2)
        icons.removeNode()
        icons2.removeNode()

    def generateHPBase(self):
        model = loader.loadModel('phase_3.5/models/char/ttcc_ene_insignias')
        icons = loader.loadModel('phase_3/models/gui/cog_icons')
        dept = self.style.dept
        if base.config.GetBool('want-new-cogs', 0):
            chestNull = self.find('**/def_joint_attachMeter')
            if chestNull.isEmpty():
                chestNull = self.find('**/joint_attachMeter')
        else:
            chestNull = self.find('**/joint_attachMeter')
        if dept == 'c':
            self.hpBase = model.find('**/emblem_base').copyTo(chestNull)
        elif dept == 's':
            self.hpBase = model.find('**/emblem_base').copyTo(chestNull)
        elif dept == 'l':
            self.hpBase = model.find('**/emblem_base').copyTo(chestNull)
        elif dept == 'm':
            self.hpBase = model.find('**/emblem_base').copyTo(chestNull)
        elif dept == 'g':
            self.hpBase = model.find('**/emblem_base').copyTo(chestNull)
        elif dept == 't':
            self.hpBase = model.find('**/emblem_base').copyTo(chestNull)
        elif dept == 'p':
            self.hpBase = model.find('**/emblem_base').copyTo(chestNull)
        self.hpBase.setH(180.0)
        self.hpBase.setColor(self.medallionColors[dept])
        if self.style.name == 'fhj':
            self.hpBase.setScale(0)
        elif self.style.name == 'hroller2':
            self.hpBase.setScale(0)
        elif self.style.name == 'hroller':
            self.hpBase.setScale(0)
        elif self.style.name == 'hrollers':
            self.hpBase.setScale(0)
        elif self.style.name == 'bcaster':
            self.hpBase.setScale(0)
        else:
            self.hpBase.setScale(1.175)
        if self.style.name == 'nn':
            self.hpBase.setZ(.2)
        elif self.style.name == 'mm':
            self.hpBase.setZ(.2)
        elif self.style.name == 'judy':
            self.hpBase.setZ(.2)
        elif self.style.name == 'ddiver':
            self.hpBase.setZ(.2)
        elif self.style.name == 'sh':
            self.hpBase.setZ(.2)
        elif self.style.name == 'bfh':
            self.hpBase.setZ(.2)
        elif self.style.name == 'dhr':
            self.hpBase.setZ(.2)
        elif self.style.name == 'mouthp':
            self.hpBase.setZ(.2)
        elif self.style.name == 'ang':
            self.hpBase.setZ(.2)
        elif self.style.name == 'bfh2':
            self.hpBase.setZ(.2)
        elif self.style.name == 'hck':
            self.hpBase.setZ(.2)
        if self.style.body == 'c':
            self.hpBase.setY(.05)
        if self.style.body == 'a':
            self.hpBase.setY(-.1)
            self.hpBase.setZ(-.1)
        model.removeNode()
        icons.removeNode()

    def generateHealthBar(self):
        self.removeHealthBar()
        model = loader.loadModel('phase_3.5/models/char/ttcc_ene_insignias')
        button = model.find('**/emblem_hp')
        if self.style.name == 'fhj':
            button.setScale(0)
        elif self.style.name == 'hrollers':
            button.setScale(0)
        elif self.style.name == 'bcaster':
            button.setScale(0)
        elif self.style.name == 'hroller':
            button.setScale(0)
        elif self.style.name == 'hroller2':
            button.setScale(0)
        else:
            button.setScale(1.175)
        button.setH(180.0)
        button.setColor(self.healthColors[0])
        chestNull = self.find('**/joint_attachMeter')
        button.reparentTo(chestNull)
        self.healthBar = button
        glow = button.find('**/glow')
        glow.reparentTo(self.healthBar)
        if self.style.name == 'fhj':
            glow.setScale(0)
        elif self.style.name == 'hrollers':
            glow.setScale(0)
        elif self.style.name == 'bcaster':
            glow.setScale(0)
        elif self.style.name == 'hroller':
            glow.setScale(0)
        elif self.style.name == 'hroller2':
            glow.setScale(0)
        else:
            glow.setScale(1)
        glow.setPos(0, 0, 0)
        glow.setColor(self.healthGlowColors[0])
        self.healthBarGlow = glow
        self.healthCondition = 0
        self.healthBar.hide()
        #self.healthBarGlow.hide()
        if self.style.body == 'c':
            self.healthBar.setY(.05)
        if self.style.body == 'a':
            self.healthBar.setY(-.1)
            self.healthBar.setZ(-.1)
        if self.style.name == 'bfh':
            self.healthBar.setZ(.2)
        elif self.style.name == 'bfh2':
            self.healthBar.setZ(.2)
        elif self.style.name == 'ang':
            self.healthBar.setZ(.2)
        elif self.style.name == 'hck':
            self.healthBar.setZ(.2)
        elif self.style.name == 'mm':
            self.healthBar.setZ(.2)
        elif self.style.name == 'nn':
            self.healthBar.setZ(.2)
        elif self.style.name == 'judy':
            self.healthBar.setZ(.2)
        elif self.style.name == 'dhr':
            self.healthBar.setZ(.2)
        elif self.style.name == 'ddiver':
            self.healthBar.setZ(.2)
        elif self.style.name == 'sh':
            self.healthBar.setZ(.2)
        elif self.style.name == 'bdb':
            self.healthBar.setZ(.2)
        elif self.style.name == 'mouthp':
            self.healthBar.setZ(.2)

    def generateSkeletonHealthBar(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        button = modelRoot.find('**/emblem_healthmeter')
        self.removeHealthBar()
        button.setScale(1)
        button.setColor(self.healthColors[0])
        self.healthBar = button
        glow = modelRoot.find('**/glow')
        glow.reparentTo(self.healthBar)
        glow.setScale(1)
        glow.setPos(0, 0, 0)
        glow.setColor(self.healthGlowColors[0])
        self.healthBarGlow = glow
        self.healthCondition = 0
        self.healthBar.hide()
        #self.healthBarGlow.hide()

    def generateSkeletonHealthBarDisplay(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        button = modelRoot.find('**/emblem_healthmeter')
        button.setScale(1)
        button.setColor(self.healthColors[16])
        self.healthBarDisplay = button
        glow = modelRoot.find('**/glow')
        glow.reparentTo(self.healthBarDisplay)
        glow.setScale(1)
        glow.setPos(0, 0, 0)
        glow.setColor(self.healthGlowColors[16])
        self.healthBarGlowDisplay = glow
        self.healthCondition = 0
        #self.healthBar.hide()
        #self.healthBarGlow.hide()

    def generateSkeletonHealthBarDisplay2(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        button = modelRoot.find('**/emblem_healthmeter')
        button.setScale(1)
        button.setColor(self.healthColors[0])
        self.healthBarDisplay = button
        glow = modelRoot.find('**/glow')
        glow.reparentTo(self.healthBarDisplay)
        glow.setScale(1)
        glow.setPos(0, 0, 0)
        glow.setColor(self.healthGlowColors[0])
        self.healthBarGlowDisplay = glow
        self.healthCondition = 0
        #self.healthBar.hide()
        #self.healthBarGlow.hide()

    def resetHealthBarForSkele(self):
        self.healthBar.setPos(0.0, 0.0, 0.0)

    def updateHealthBar(self, hp, forceUpdate = 0):
        self.currHP -= hp
        messenger.send(self.uniqueName('suitHpUpdate'), [self.currHP, self.maxHP, hp])
        health = float(self.currHP) / float(self.maxHP)
        taskMgr.remove(self.uniqueName('pulse-task'))
        if self.isVirtual and not self.isSkeleton:
            self.healthBar.hide()
            self.healthBarGlow.hide()
            self.hpBase.hide()
            self.corpMedallion.hide()
        if health > 1.5:
            condition = 13
        elif health > 1.25:
            condition = 12
        elif health > 1.0:
            condition = 12
        elif health > 0.95:
            condition = 0
        elif health > 0.9:
            condition = 1
        elif health > 0.8:
            condition = 2
        elif health > 0.7:
            condition = 3
        elif health > 0.6:
            condition = 4
        elif health > 0.5:
            condition = 5
        elif health > 0.4:
            condition = 6
        elif health > 0.25:
            condition = 7
        elif health > 0.2:
            condition = 8
        elif health > 0.1:
            condition = 9
        elif health > 0.0:
            condition = 10
        else:
            condition = 11
        self.condition = condition
        if self.style.name == 'hrollers':
            if self.getActualLevel() == 34:
                self.setDisplayName(self.createNameInfoMagenta())
                if condition == 10:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.75), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                elif condition == 11:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    if self.healthCondition == 10:
                        taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.25), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                else:
                    self.virtualize(20)
            elif self.getActualLevel() == 33:
                self.setDisplayName(self.createNameInfoWhite())
                if condition == 10:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.75), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                elif condition == 11:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    if self.healthCondition == 10:
                        taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.25), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                else:
                    self.virtualize(19)
            elif self.getActualLevel() == 32:
                self.setDisplayName(self.createNameInfoPurple())
                if condition == 10:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.75), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                elif condition == 11:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    if self.healthCondition == 10:
                        taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.25), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                else:
                    self.virtualize(13)
            elif self.getActualLevel() == 31:
                self.setDisplayName(self.createNameInfoLightBlue())
                if condition == 10:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.75), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                elif condition == 11:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    if self.healthCondition == 10:
                        taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.25), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                else:
                    self.virtualize(12)
            elif self.getActualLevel() == 30:
                self.setDisplayName(self.createNameInfoPink())
                if condition == 10:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.75), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                elif condition == 11:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    if self.healthCondition == 10:
                        taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.25), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                else:
                    self.virtualize(14)
            elif self.getActualLevel() == 29:
                self.setDisplayName(self.createNameInfoRed())
                if condition == 10:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.75), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                elif condition == 11:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    if self.healthCondition == 10:
                        taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.25), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                else:
                    self.virtualize(8)
            elif self.getActualLevel() == 28:
                self.setDisplayName(self.createNameInfoBlue())
                if condition == 10:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.75), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                elif condition == 11:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    if self.healthCondition == 10:
                        taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.25), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                else:
                    self.virtualize(15)
            elif self.getActualLevel() == 27:
                self.setDisplayName(self.createNameInfoYellow())
                if condition == 10:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.75), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                elif condition == 11:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    if self.healthCondition == 10:
                        taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.25), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                else:
                    self.virtualize(3)
            elif self.getActualLevel() == 26:
                self.setDisplayName(self.createNameInfoOrange())
                if condition == 10:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.75), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                elif condition == 11:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    if self.healthCondition == 10:
                        taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.25), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                else:
                    self.virtualize(7)
            else:
                self.makeLureImmune()
                self.setDisplayName(self.createNameInfoGreen())
                if condition == 10:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.75), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                elif condition == 11:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    if self.healthCondition == 10:
                        taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.25), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                else:
                    self.virtualize(0)
        if self.style.name == 'clubpres':
            if self.getActualLevel() == 20:
                self.setDisplayName(self.createNameInfoHighStakes())
            elif self.getActualLevel() == 21:
                self.setDisplayName(self.createNameInfoMulligan())
            elif self.getActualLevel() == 22:
                self.setDisplayName(self.createNameInfoAncient())
            elif self.getActualLevel() == 23:
                self.setDisplayName(self.createNameInfoChipFan())
            elif self.getActualLevel() == 24:
                self.setDisplayName(self.createNameInfoPuzzling())
            elif self.getActualLevel() == 25:
                self.setDisplayName(self.createNameInfoShivering())
            else:
                pass
        if self.style.name == 'supervis':
            if self.getActualLevel() == 20:
                self.setDisplayName(self.createNameInfoAbacus())
            elif self.getActualLevel() == 21:
                self.setDisplayName(self.createNameInfoControlling())
            elif self.getActualLevel() == 22:
                self.setDisplayName(self.createNameInfoConfused())
            elif self.getActualLevel() == 23:
                self.setDisplayName(self.createNameInfoAccountant())
            elif self.getActualLevel() == 24:
                self.setDisplayName(self.createNameInfoSpongy())
            elif self.getActualLevel() == 25:
                self.setDisplayName(self.createNameInfoFraudulent())
            else:
                pass
        if self.style.name == 'clerk':
            if self.getActualLevel() == 20:
                self.setDisplayName(self.createNameInfoSneaky())
            elif self.getActualLevel() == 21:
                self.setDisplayName(self.createNameInfoOmnipotent())
            elif self.getActualLevel() == 22:
                self.setDisplayName(self.createNameInfoOverseer())
            elif self.getActualLevel() == 23:
                self.setDisplayName(self.createNameInfoMonolithic())
            elif self.getActualLevel() == 24:
                self.setDisplayName(self.createNameInfoChrono())
            elif self.getActualLevel() == 25:
                self.setDisplayName(self.createNameInfoLaborious())
            else:
                pass
        if self.style.name == 'foreman':
            if self.getActualLevel() == 20:
                self.setDisplayName(self.createNameInfoSleepy())
            elif self.getActualLevel() == 21:
                self.setDisplayName(self.createNameInfoBurning())
            elif self.getActualLevel() == 22:
                self.setDisplayName(self.createNameInfoExplosive())
            elif self.getActualLevel() == 23:
                self.setDisplayName(self.createNameInfoContractor())
            elif self.getActualLevel() == 24:
                self.setDisplayName(self.createNameInfoRedTape())
            elif self.getActualLevel() == 25:
                self.setDisplayName(self.createNameInfoSniper())
            else:
                pass
        #self.healthCondition = condition
        #print('UpdateHealthBar - condition is %i' % condition)

        if self.healthCondition != condition or forceUpdate:
            if condition <= 9:
                taskMgr.remove(self.uniqueName('blink-task'))
                if not self.virtual:
                    self.healthBar.setColor(1, 1, 1, 1)
                    self.healthBarGlow.setColor(1, 1, 1, 1)
                else:
                    self.healthBarGlow.setColor(0, 0, 0, 0)
                    if not self.style.name == 'hrollers':
                        self.virtualize(condition)
                self.__changeColor()
            elif condition == 10:
                taskMgr.remove(self.uniqueName('blink-task'))
                if not self.virtual:
                    self.healthBar.setColor(1, 1, 1, 1)
                    self.healthBarGlow.setColor(1, 1, 1, 1)
                blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.75), Task(self.__pulseGray), Task.pause(0.1))
                taskMgr.add(blinkTask, self.uniqueName('blink-task'))
            elif condition == 11:
                taskMgr.remove(self.uniqueName('blink-task'))
                if not self.virtual:
                    self.healthBar.setColor(1, 1, 1, 1)
                    self.healthBarGlow.setColor(1, 1, 1, 1)
                blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.25), Task(self.__pulseGray), Task.pause(0.1))
                taskMgr.add(blinkTask, self.uniqueName('blink-task'))
            elif condition == 13:
                taskMgr.remove(self.uniqueName('pulse-task'))
                if not self.virtual:
                    self.healthBar.setColor(1, 1, 1, 1)
                    self.healthBarGlow.setColor(1, 1, 1, 1)
                blinkTask = Task.loop(Task(self.__pulsePurple), Task.pause(1), Task(self.__pulsePurpleColor), Task.pause(3))
                taskMgr.add(blinkTask, self.uniqueName('pulse-task'))
            else:
                taskMgr.remove(self.uniqueName('blink-task'))
                if not self.virtual:
                    self.healthBar.setColor(1, 1, 1, 1)
                    self.healthBarGlow.setColor(1, 1, 1, 1)
                else:
                    self.healthBarGlow.setColor(0, 0, 0, 0)
                    if not self.style.name == 'hrollers':
                        self.virtualize(condition)
                self.__changeColor()
            self.healthCondition = condition

    def __blinkRed(self, task):
        if not self.virtual:
            self.healthBar.setColor(self.healthColors[9], 1)
            self.healthBarGlow.setColor(self.healthGlowColors[9], 1)
        elif not self.style.name == 'hrollers':
            self.healthBarGlow.setColor(0, 0, 0, 0)
            self.virtualize(9)
        else:
            self.virtualize(9)

    def __blinkGray(self, task):
        if not self.virtual:
            self.healthBar.setColor(self.healthColors[10], 1)
            self.healthBarGlow.setColor(self.healthGlowColors[10], 1)
        elif not self.style.name == 'hrollers':
            self.healthBarGlow.setColor(0, 0, 0, 0)
            self.virtualize(10)
        else:
            self.virtualize(10)

    def __pulseRed(self, task):
        if not self.virtual:
            self.interval = Parallel(LerpColorScaleInterval(self.healthBar, duration=0, colorScale=(1, 0, 0, 1),
                                   blendType='easeInOut'))
            self.glowInterval = Parallel(LerpColorScaleInterval(self.healthBarGlow, duration=0, colorScale=(1, 0, 0, 1),
                                   blendType='easeInOut'))
            self.interval.start()
            self.glowInterval.start()
        else:
            self.healthBarGlow.setColor(0, 0, 0, 0)
            if self.style.name == 'hrollers':
                if self.getActualLevel() == 34:
                    self.virtualize(20)
                elif self.getActualLevel() == 33:
                    self.virtualize(19)
                elif self.getActualLevel() == 32:
                    self.virtualize(13)
                elif self.getActualLevel() == 31:
                    self.virtualize(12)
                elif self.getActualLevel() == 30:
                    self.virtualize(14)
                elif self.getActualLevel() == 29:
                    self.virtualize(8)
                elif self.getActualLevel() == 28:
                    self.virtualize(15)
                elif self.getActualLevel() == 27:
                    self.virtualize(3)
                elif self.getActualLevel() == 26:
                    self.virtualize(7)
                else:
                    self.virtualize(0)
            else:
                self.virtualizeRed(9)

    def __pulseWhite(self):
        if not self.virtual:
            self.interval = Parallel(LerpColorScaleInterval(self.healthBar, duration=0, colorScale=(1, 1, 1, 1),
                                   blendType='easeInOut'))
            self.glowInterval = Parallel(LerpColorScaleInterval(self.healthBarGlow, duration=0, colorScale=(1, 1, 1, 1),
                                   blendType='easeInOut'))
            self.interval.start()
            self.glowInterval.start()
        else:
            self.healthBarGlow.setColor(0, 0, 0, 0)
            if not self.style.name == 'hrollers':
                self.virtualizeRed(9)

    def __pulseGray(self, task):
        if not self.virtual:
            self.interval = Parallel(LerpColorScaleInterval(self.healthBar, duration=0, colorScale=(0.3, 0.3, 0.3, 1),
                                   blendType='easeInOut'))
            self.glowInterval = Parallel(LerpColorScaleInterval(self.healthBarGlow, duration=0, colorScale=(0, 0, 0, 0),
                                   blendType='easeInOut'))
            self.interval.start()
            self.glowInterval.start()
        else:
            self.healthBarGlow.setColor(0, 0, 0, 0)
            self.virtualizeGray(10)

    def __pulsePurple(self, task):
        if not self.virtual:
            self.interval = Parallel(LerpColorScaleInterval(self.healthBar, duration=1, colorScale=(0.992, 0.227, 1, 1),
                                   blendType='easeInOut'))
            self.glowInterval = Parallel(LerpColorScaleInterval(self.healthBarGlow, duration=1, colorScale=(0.992, 0.227, 1, 1),
                                   blendType='easeInOut'))
            self.interval.start()
            self.glowInterval.start()
        else:
            self.healthBarGlow.setColor(0, 0, 0, 0)
            if not self.style.name == 'hrollers':
                self.virtualizePurple(17)

    def __changeColor(self):
        if self.isImmortal and not self.cog.dna.name == 'hroller' and not self.cog.dna.name == 'hroller2':
            self.interval = Parallel(LerpColorScaleInterval(self.healthBar, duration=1, colorScale=(1, 1, 1, 1),
                                   blendType='easeInOut'))
            self.glowInterval = Parallel(LerpColorScaleInterval(self.healthBarGlow, duration=1, colorScale=(1, 1, 1, 1),
                                   blendType='easeInOut'))
            self.interval.start()
            self.glowInterval.start()
        elif not self.virtual:
            self.interval = Parallel(LerpColorScaleInterval(self.healthBar, duration=1, colorScale=(self.healthColors[self.condition]),
                                   blendType='easeInOut'))
            self.glowInterval = Parallel(LerpColorScaleInterval(self.healthBarGlow, duration=1, colorScale=(self.healthColors[self.condition]),
                                   blendType='easeInOut'))
            self.interval.start()
            self.glowInterval.start()
        else:
            self.healthBarGlow.setColor(0, 0, 0, 0)
            if not self.style.name == 'hrollers':
                self.virtualize(self.condition)

    def __pulsePurpleColor(self, task):
        if not self.virtual:
            self.interval = Parallel(LerpColorScaleInterval(self.healthBar, duration=1, colorScale=(self.healthColors[13]),
                                   blendType='easeInOut'))
            self.glowInterval = Parallel(LerpColorScaleInterval(self.healthBarGlow, duration=1, colorScale=(self.healthGlowColors[13]),
                                   blendType='easeInOut'))
            self.interval.start()
            self.glowInterval.start()
        else:
            self.healthBarGlow.setColor(0, 0, 0, 0)
            if not self.style.name == 'hrollers':
                self.virtualizePurpleColor(13)

    def removeHealthBar(self):
        if self.healthBar:
            self.healthBar.removeNode()
            self.healthBar = None

        if self.healthCondition == 10 or self.healthCondition == 11:
            taskMgr.remove(self.uniqueName('blink-task'))

        self.healthCondition = 0

    def removeHealthBarDisplay(self):
        if self.healthBarDisplay:
            self.healthBarDisplay.removeNode()
            self.healthBarDisplay = None

        self.healthCondition = 0

    def virtualize(self, condition):
        self.healthCondition = 0
        actorNode = self.find('**/__Actor_modelRoot')
        actorCollection = actorNode.findAllMatches('*')
        parts = ()
        for thingIndex in range(0, actorCollection.getNumPaths()):
            thing = actorCollection[thingIndex]
            if thing.getName() not in ('joint_attachMeter', 'joint_nameTag', 'def_nameTag'):
                thing.setColor(1, 1, 1, 1)
                self.interval = Parallel(
                    LerpColorScaleInterval(thing, duration=0, colorScale=(self.healthColors[condition]),
                                           blendType='easeInOut'))
                self.interval.start()
                thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
                thing.setDepthWrite(False)
                thing.setBin('fixed', 1)

    def virtualize3(self, condition):
        self.healthCondition = 0
        actorNode = self.find('**/__Actor_modelRoot')
        actorCollection = actorNode.findAllMatches('*')
        parts = ()
        for thingIndex in range(0, actorCollection.getNumPaths()):
            thing = actorCollection[thingIndex]
            if thing.getName() not in ('joint_attachMeter', 'joint_nameTag', 'def_nameTag'):
                thing.setColor(1, 1, 1, 1)
                self.interval = Parallel(
                    LerpColorScaleInterval(thing, duration=0, colorScale=(self.healthColors[condition]),
                                           blendType='easeInOut'))
                self.interval.start()
                thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
                thing.setDepthWrite(False)
                thing.setBin('fixed', 1)

    def virtualizePurple(self, condition):
        self.healthCondition = 0
        actorNode = self.find('**/__Actor_modelRoot')
        actorCollection = actorNode.findAllMatches('*')
        parts = ()
        for thingIndex in range(0, actorCollection.getNumPaths()):
            thing = actorCollection[thingIndex]
            if thing.getName() not in ('joint_attachMeter', 'joint_nameTag', 'def_nameTag'):
                thing.setColor(1, 1, 1, 1)
                self.interval = Parallel(
                    LerpColorScaleInterval(thing, duration=2, colorScale=(0.702, 0, 1, 1),
                                           blendType='easeInOut'))
                self.interval.start()
                thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
                thing.setDepthWrite(False)
                thing.setBin('fixed', 1)

    def virtualizePurpleColor(self, condition):
        self.healthCondition = 0
        actorNode = self.find('**/__Actor_modelRoot')
        actorCollection = actorNode.findAllMatches('*')
        parts = ()
        for thingIndex in range(0, actorCollection.getNumPaths()):
            thing = actorCollection[thingIndex]
            if thing.getName() not in ('joint_attachMeter', 'joint_nameTag', 'def_nameTag'):
                thing.setColor(1, 1, 1, 1)
                self.interval = Parallel(
                    LerpColorScaleInterval(thing, duration=2, colorScale=(self.healthColors[13]),
                                           blendType='easeInOut'))
                self.interval.start()
                thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
                thing.setDepthWrite(False)
                thing.setBin('fixed', 1)

    def virtualizeGray(self, condition):
        self.healthCondition = 0
        actorNode = self.find('**/__Actor_modelRoot')
        actorCollection = actorNode.findAllMatches('*')
        parts = ()
        for thingIndex in range(0, actorCollection.getNumPaths()):
            thing = actorCollection[thingIndex]
            if thing.getName() not in ('joint_attachMeter', 'joint_nameTag', 'def_nameTag'):
                thing.setColor(1, 1, 1, 1)
                self.interval = Parallel(
                    LerpColorScaleInterval(thing, duration=0, colorScale=(0.3, 0.3, 0.3, 1),
                                           blendType='easeInOut'))
                self.interval.start()
                thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
                thing.setDepthWrite(False)
                thing.setBin('fixed', 1)

    def virtualizeRed(self, condition):
        self.healthCondition = 0
        actorNode = self.find('**/__Actor_modelRoot')
        actorCollection = actorNode.findAllMatches('*')
        parts = ()
        for thingIndex in range(0, actorCollection.getNumPaths()):
            thing = actorCollection[thingIndex]
            if thing.getName() not in ('joint_attachMeter', 'joint_nameTag', 'def_nameTag'):
                thing.setColor(1, 1, 1, 1)
                self.interval = Parallel(
                    LerpColorScaleInterval(thing, duration=0, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'))
                self.interval.start()
                thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
                thing.setDepthWrite(False)
                thing.setBin('fixed', 1)

    def virtualize2(self, condition):
        self.healthCondition = 0
        actorNode = self.find('**/__Actor_modelRoot')
        actorCollection = actorNode.findAllMatches('*')
        parts = ()
        for thingIndex in range(0, actorCollection.getNumPaths()):
            thing = actorCollection[thingIndex]
            if thing.getName() not in ('joint_attachMeter', 'joint_nameTag', 'def_nameTag'):
                thing.setColor(0, 1, 0.063, 1)
                thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
                thing.setDepthWrite(False)
                thing.setBin('fixed', 1)

    def makeVirtual(self, isVirtual = 1):
        self.removeHealthBar()
        self.isVirtual = 1
        self.virtual = isVirtual
        if self.virtual:
            self.virtualize2(0)

    def makeVirtual2(self, isVirtual = 1):
        self.removeHealthBar()
        self.isVirtual = 1
        self.virtual = isVirtual
        if self.virtual:
            self.virtualize2(0)

    def getLoseActor(self, headless=False):
        model = 'phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-zero'
        anims = self.generateAnimDict()
        anim = self.getCurrentAnim()
        dept = self.style.dept
        self.removePart('modelRoot')
        self.removePart('head')
        self.generateSkeletonBody()
        self.loadAnims(anims)
        self.generateSkeletonHealthBar()
        # self.generateHPBase()
        # self.generateCorporateMedallion()
        self.generateCorporateMedallion3()
        # self.generateCorporateTie()
        self.setSuitClothesSkeleton()
        self.setHeight(self.height)
        self.setBlend(frameBlend=base.wantSmoothAnims)
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)
        parts = self.findAllMatches('**/pPlane*')
        for partNum in xrange(0, parts.getNumPaths()):
            bb = parts.getPath(partNum)
            bb.setTwoSided(1)

        # self.setName(TTLocalizer.SuitBaseNameWithLevelMgr)
        self.leftHand = self.find('**/joint_Lhold')
        self.rightHand = self.find('**/joint_Rhold')
        self.shadowJoint = self.find('**/joint_shadow')
        self.nametagNull = self.find('**/joint_nameTag')

        self.isSkeleton = 1

    def cleanupLoseActor(self):
        self.notify.debug('cleanupLoseActor()')
        if self.loseActor != None:
            self.notify.debug('cleanupLoseActor() - got one')
            self.loseActor.cleanup()

        self.loseActor = None

    def getZapActor(self):
        if self.zapActor == None:
            loseModel = 'phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-zero'
            filePrefix, phase = TutorialModelDict[self.style.body]
            shockAnim = 'phase_5' + filePrefix + 'shock'
            self.zapActor = Actor.Actor(loseModel, {'shock': shockAnim})
            self.generateCorporateTie(self.zapActor)



        self.zapActor.setScale(self.scale)
        self.zapActor.setPos(self.getPos())
        self.zapActor.setHpr(self.getHpr())
        shadowJoint = self.zapActor.find('**/joint_shadow')
        dropShadow = loader.loadModel('phase_3/models/props/drop_shadow')
        dropShadow.setScale(0.45)
        dropShadow.setColor(0.0, 0.0, 0.0, 0.5)
        dropShadow.reparentTo(shadowJoint)
        return self.zapActor

    def cleanupZapActor(self):
        self.notify.debug('cleanupLoseActor()')
        if self.zapActor != None:
            self.notify.debug('cleanupLoseActor() - got one')
            self.zapActor.cleanup()

        self.zapActor = None

    def makeSkeleton(self, elite=False):
        model = 'phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-zero'
        anims = self.generateAnimDict()
        anim = self.getCurrentAnim()
        dept = self.style.dept
        self.headParts = []
        self.removePart('modelRoot')
        self.generateSkeletonBody()
        self.loadAnims(anims)
        self.removeHealthBar()
        self.generateSkeletonHealthBar()
        self.generateSkeletonHealthBarDisplay()
        #self.generateHPBase()
        #self.generateCorporateMedallion()
        self.generateCorporateMedallion3()
        #self.generateCorporateTie()
        self.setSuitClothesSkeleton()
        self.setHeight(self.height)
        self.setBlend(frameBlend=base.wantSmoothAnims)
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)
        parts = self.findAllMatches('**/pPlane*')
        for partNum in xrange(0, parts.getNumPaths()):
            bb = parts.getPath(partNum)
            bb.setTwoSided(1)

        #self.setName(TTLocalizer.SuitBaseNameWithLevelMgr)
        self.leftHand = self.find('**/joint_Lhold')
        self.rightHand = self.find('**/joint_Rhold')
        self.shadowJoint = self.find('**/joint_shadow')
        dropShadow = loader.loadModel('phase_3/models/props/drop_shadow')
        dropShadow.setScale(0.45)
        dropShadow.setColor(0.0, 0.0, 0.0, 0.5)
        dropShadow.reparentTo(self.shadowJoint)
        self.nametagNull = self.find('**/joint_nameTag')
        texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' % self.style.dept)
        if self.isWaiter:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_waiter.png')
        elif self.style.dept == 'c' and not self.getExecutive() and not self.getManager() and not self.getGovernaught() and not self.isWaiter:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s2.png' % self.style.dept)
        elif self.getExecutive() and not self.isWaiter:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' % self.style.dept)
        elif self.getManager() and not self.isWaiter:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' % self.style.dept)
        elif self.getGovernaught() and not self.isWaiter:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_gov.png' % self.style.dept)
        self.find('**/body').setTexture(texture, 1)
        self.find('**/emblem_healthmeter').show()
        textureDerrick = loader.loadTexture('phase_12/maps/ttcc_ene_derrickhand_skelecog.png')
        textureDopa = loader.loadTexture('phase_9/maps/ttcc_ene_dopa.png')
        textureDopr = loader.loadTexture('phase_9/maps/ttcc_ene_dopr.png')
        textureAmbassador = loader.loadTexture('phase_9/maps/ttcc_ene_prethinker.png')
        for headPart in self.headParts:
            if self.style.name == 'derrhand':
                headPart.setTexture(textureDerrick, 1)
            elif self.style.name == 'ubuster':
                headPart.setTexture(textureDopr, 1)
            elif self.style.name == 'radiog':
                headPart.setTexture(textureDopa, 1)
            elif self.style.name == 'ambass':
                headPart.setTexture(textureAmbassador, 1)
            else:
                headPart.setTexture(texture, 1)
        dept = self.getStyleDept()
        level = str(self.getActualLevel())
        if self.getExecutive():
            level += TTLocalizer.ExecutivePostFix
        if self.getManager():
            level += TTLocalizer.ManagerPostFix
        if self.getGovernaught():
            level += TTLocalizer.GovernaughtPostFix
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': self.name,
                                                        'dept': dept,
                                                        'level': level}
        self.setDisplayName(nameInfo)

        self.isSkeleton = 1

    def makeSkeletonManager(self, elite=False):
        anims = self.generateAnimDict()
        self.headParts = []
        self.removePart('modelRoot')
        self.generateSkeletonBody()
        self.loadAnims(anims)
        self.removeHealthBar()
        self.generateSkeletonHealthBar()
        self.generateSkeletonHealthBarDisplay()
        #self.generateHPBase()
        #self.generateCorporateMedallion()
        self.generateCorporateMedallion3()
        #self.generateCorporateTie()
        self.setSuitClothesSkeleton()
        self.setHeight(self.height)
        self.setBlend(frameBlend=base.wantSmoothAnims)
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)
        parts = self.findAllMatches('**/pPlane*')
        for partNum in xrange(0, parts.getNumPaths()):
            bb = parts.getPath(partNum)
            bb.setTwoSided(1)

        #self.setName(TTLocalizer.SuitBaseNameWithLevelMgr)
        self.leftHand = self.find('**/joint_Lhold')
        self.rightHand = self.find('**/joint_Rhold')
        self.shadowJoint = self.find('**/joint_shadow')
        self.nametagNull = self.find('**/joint_nameTag')
        dropShadow = loader.loadModel('phase_3/models/props/drop_shadow')
        dropShadow.setScale(0.45)
        dropShadow.setColor(0.0, 0.0, 0.0, 0.5)
        dropShadow.reparentTo(self.shadowJoint)
        self.find('**/emblem_healthmeter').show()

        self.isSkeleton = 1

    def makeSkeleton2(self, elite=False):
        model = 'phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-zero'
        anims = self.generateAnimDict()
        anim = self.getCurrentAnim()
        dept = self.style.dept
        self.headParts = []
        self.removePart('modelRoot')
        self.generateSkeletonBody()
        self.loadAnims(anims)
        self.removeHealthBar()
        self.generateSkeletonHealthBar()
        self.generateSkeletonHealthBarDisplay2()
        #self.generateHPBase()
        #self.generateCorporateMedallion()
        #self.generateCorporateMedallion3()
        #self.generateCorporateTie()
        self.setSuitClothesSkeleton()
        self.setHeight(self.height)
        self.setBlend(frameBlend=base.wantSmoothAnims)
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)
        parts = self.findAllMatches('**/pPlane*')
        for partNum in xrange(0, parts.getNumPaths()):
            bb = parts.getPath(partNum)
            bb.setTwoSided(1)

        #self.setName(TTLocalizer.SuitBaseNameWithLevelMgr)
        self.leftHand = self.find('**/joint_Lhold')
        self.rightHand = self.find('**/joint_Rhold')
        self.shadowJoint = self.find('**/joint_shadow')
        self.nametagNull = self.find('**/joint_nameTag')
        dropShadow = loader.loadModel('phase_3/models/props/drop_shadow')
        dropShadow.setScale(0.45)
        dropShadow.setColor(0.0, 0.0, 0.0, 0.5)
        dropShadow.reparentTo(self.shadowJoint)
        texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' % self.style.dept)
        if self.isWaiter:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_waiter.png')
        elif self.style.dept == 'c' and not self.getExecutive() and not self.getManager() and not self.getGovernaught() and not self.isWaiter:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s2.png' % self.style.dept)
        elif self.getExecutive() and not self.isWaiter:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' % self.style.dept)
        elif self.getManager() and not self.isWaiter:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' % self.style.dept)
        elif self.getGovernaught() and not self.isWaiter:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_gov.png' % self.style.dept)
        self.find('**/body').setTexture(texture, 1)
        self.find('**/emblem_healthmeter').show()
        textureDerrick = loader.loadTexture('phase_12/maps/ttcc_ene_derrickhand_skelecog.png')
        textureDopa = loader.loadTexture('phase_9/maps/ttcc_ene_dopa.png')
        textureDopr = loader.loadTexture('phase_9/maps/ttcc_ene_dopr.png')
        textureAmbassador = loader.loadTexture('phase_9/maps/ttcc_ene_prethinker.png')
        for headPart in self.headParts:
            if self.style.name == 'derrhand':
                headPart.setTexture(textureDerrick, 1)
            elif self.style.name == 'ubuster':
                headPart.setTexture(textureDopr, 1)
            elif self.style.name == 'radiog':
                headPart.setTexture(textureDopa, 1)
            elif self.style.name == 'ambass':
                headPart.setTexture(textureAmbassador, 1)
            else:
                headPart.setTexture(texture, 1)
        dept = self.getStyleDept()
        level = str(self.getActualLevel())
        revives = self.getSkeleRevives()
        if self.getExecutive():
            level += TTLocalizer.ExecutivePostFix
        if self.getManager():
            level += TTLocalizer.ManagerPostFix
        if self.getGovernaught():
            level += TTLocalizer.GovernaughtPostFix
        if self.isSkeleton and revives >=2:
            level += ' v2.0'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': self.name,
                                                        'dept': dept,
                                                        'level': level}
        self.setDisplayName(nameInfo)

        self.isSkeleton = 1
        self.isRevive = 1

    def makeFired(self, elite=False):
        anims = self.generateAnimDict()
        self.setName(self.createNameInfoFired())
        self.corpMedallion.hide()
        texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        textureSkele = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_unemployed.png')
        if self.isSkeleton:
            self.find('**/necktie-s').setTexture(textureSkele, 1)
            self.find('**/necktie-w').setTexture(textureSkele, 1)
            self.find('**/bowtie').setTexture(textureSkele, 1)
            self.find('**/body').setTexture(textureSkele, 1)
            for headPart in self.headParts:
                headPart.setTexture(textureSkele, 1)
        else:
            self.find('**/necktie-s').setTexture(texture, 1)
            self.find('**/necktie-w').setTexture(texture, 1)
            self.find('**/bowtie').setTexture(texture, 1)
            self.find('**/body').setTexture(texture, 1)
        if self.style.name == 'bgh' and not self.isSkeleton:
            texture2 = loader.loadTexture('phase_14/maps/cc_t_ene_bagholder_unemployed.png')
            for headPart in self.headParts:
                headPart.setTexture(texture2, 1)
        if self.style.name == 'ins' and not self.isSkeleton:
            texture2 = loader.loadTexture('phase_14/maps/cc_t_ene_insider_unemployed.png')
            for headPart in self.headParts:
                headPart.setTexture(texture2, 1)
        if self.style.name == 'hho' and not self.isSkeleton:
            texture2 = loader.loadTexture('phase_14/maps/cc_t_ene_headhoncho_unemployed.png')
            for headPart in self.headParts:
                headPart.setTexture(texture2, 1)

        self.isFired = 1

    def makeDesperation(self, elite=False):
        self.isDesperation = 1

    def getSoakRounds(self):
        return self.isSoaked

    def makeSoaked(self, num):
        self.isSoaked = num

    def makeUnSoaked(self, elite=False):
        self.isSoaked = 0

    def makeTarget(self):
        self.isTarget = 1

    def makeUnTarget(self):
        self.isTarget = 0

    def makeImmortal(self, elite=False):
        #self.healthBar.setColor(1, 1, 1, 1)
       # self.healthBarGlow.setColor(1, 1, 1, 1)
        #taskMgr.remove(self.uniqueName('blink-task'))
        #self.__pulseWhite()
        self.isImmortal = 1

    def makeNonImmortal(self, elite=False):
      #  self.healthBar.setColor(1, 1, 1, 1)
       # self.healthBarGlow.setColor(1, 1, 1, 1)
       # taskMgr.remove(self.uniqueName('blink-task'))
       # self.__changeColor()
        self.isImmortal = 0

    def makeLured(self):
        self.isLured = 1

    def addLuredRounds(self, num):
        self.lureRounds = num

    def getLuredRounds(self):
        return self.lureRounds

    def makeUnLured(self, elite=False):
        self.isLured = 0

    def makeLureImmune(self, elite=False):
        self.isLureImmune = 1

    def makeUnLureImmune(self, elite=False):
        self.isLureImmune = 0

    def makeSoakResistant(self, elite=False):
        self.isSoakImmune = 1

    def makeUnSoakResistant(self, elite=False):
        self.isSoakImmune = 0

    def makeSyphon(self, battle):
        self.isSyphon = 1

    def makeInversion(self, elite=False):
        for headPart in self.headParts:
            headPart.removeNode()
        self.headParts = []
        self.generateHead3('rainmaker', animated=True)
        self.isHeavyRain = 0
        self.isFreezingRain = 0
        self.isStormCell = 0
        self.isOilRain = 0

    def makeHeavyRain(self, elite=False):
        for headPart in self.headParts:
            headPart.removeNode()
        self.headParts = []
        self.generateHead3('rainmaker2', animated=True)
        self.isHeavyRain = 1
        self.isFreezingRain = 0
        self.isStormCell = 0
        self.isOilRain = 0

    def makeFreezingRain(self, elite=False):
        for headPart in self.headParts:
            headPart.removeNode()
        self.headParts = []
        self.generateHead3('rainmaker3', animated=True)
        self.isHeavyRain = 0
        self.isFreezingRain = 1
        self.isStormCell = 0
        self.isOilRain = 0

    def makeOilRain(self, elite=False):
        for headPart in self.headParts:
            headPart.removeNode()
        self.headParts = []
        self.generateHead3('rainmaker4', animated=True)
        self.isHeavyRain = 0
        self.isFreezingRain = 0
        self.isStormCell = 0
        self.isOilRain = 1

    def makeStormCell(self, elite=False):
        for headPart in self.headParts:
            headPart.removeNode()
        self.headParts = []
        self.generateHead3('rainmaker5', animated=True)
        self.isHeavyRain = 0
        self.isFreezingRain = 0
        self.isStormCell = 1
        self.isOilRain = 0

    def makeAmbassadorPhase3(self, elite=False):
        for headPart in self.headParts:
            headPart.removeNode()
        self.headParts = []
        self.generateHead3('prethinker2', animated=True)
        texture = loader.loadTexture('phase_9/maps/ttcc_ene_prethinker.png')
        for headPart in self.headParts:
            headPart.setTexture(texture, 1)
        self.isHeavyRain = 0
        self.isFreezingRain = 0
        self.isStormCell = 1
        self.isOilRain = 0

    def makeUnSyphon(self):
        self.isSyphon = 0

    def makeVulnerable(self):
        if self.suitColorTrack != None:
            self.suitColorTrack.finish()
        node = self.getGeomNode().getChild(0)
        self.suitColorTrack = Sequence(
                    LerpColorScaleInterval(node, duration=1, colorScale=(0.89, 0.608, 0.608, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(node, duration=1, colorScale=(1, 1, 1, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(node, duration=1, colorScale=(0.89, 0.608, 0.608, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(node, duration=1, colorScale=(1, 1, 1, 1)))
        self.isVulnerable = 1
        if not self.style.name == 'bcaster':
            self.suitColorTrack.loop()

    def setVulnerability(self, num):
        self.vulnerability = num

    def getVulnerability(self):
        return self.vulnerability

    def setRageBuilding(self, num):
        self.rageBuilding = num

    def getRageBuilding(self):
        return self.rageBuilding

    def setPowerhouseRotation(self, num):
        self.powerhouseRotation = num

    def getPowerhouseRotation(self):
        return self.powerhouseRotation

    def setDamageUp(self, num):
        self.damageMult = num

    def makeLureResist(self):
        self.isLureResist = 1

    def getDamageUp(self):
        return self.damageMult

    def makeUnVulnerable(self):
        self.isVulnerable = 0
        if self.suitColorTrack != None:
            self.suitColorTrack.finish()

    def makeDead(self, elite=False):
        self.isDead = 1

    def makeUnDead(self, elite=False):
        self.isDead = 0

    def makeDazed(self):
        self.isDazed = 1

    def makeUnDazed(self):
        self.isDazed = 0

    def makeRevive(self, elite=False):
        self.isRevived = 1

    def makeLaserRevive(self, elite=False):
        self.isLaserRevived = 1

    def makeDamageUp(self):
        self.isDamageUp = 1

    def makeUnDamageUp(self, elite=False):
        self.isDamageUp = 0

    def makeDamageReduction(self, elite=False):
        self.isDamageReduction = 1

    def makeUnDamageReduction(self, elite=False):
        self.isDamageReduction = 0

    def makeAngry(self, num):
        self.isAngry = num
        self.isShielding = 0

    def getEnrageCounter(self):
        return self.isAngry

    def makeUnShielding(self, elite=False):
        self.isShielding = 0

    def makeShielding(self):
        self.isShielding = 1
        self.isAngry = 0

    def makeWetLitigator(self, elite=False):
        anims = self.generateAnimDict()
        texture2 = loader.loadTexture('phase_11/maps/ttcc_ene_litigator_nf.png')
        for headPart in self.headParts:
            if not self.isSkeleton:
                headPart.setTexture(texture2, 1)

    def makeDryLitigator(self, elite=False):
        anims = self.generateAnimDict()
        texture2 = loader.loadTexture('phase_11/maps/ttcc_ene_litigator.png')
        for headPart in self.headParts:
            if not self.isSkeleton:
                headPart.setTexture(texture2, 1)

    def makeChainsawPhase2(self, elite=False):
        for headPart in self.headParts:
            headPart.removeNode()
        self.headParts = []
        self.generateHead3('chainsaw_b', animated=True)
        texture2 = loader.loadTexture('phase_12/maps/ttcc_ene_chainsaw_b_boardbot.png')
        self.isChainsawPhase2 = 1
        for headPart in self.headParts:
            if not self.isSkeleton:
                headPart.setTexture(texture2, 1)

    def makeChairmanPhase2(self, elite=False):
        for headPart in self.headParts:
            headPart.removeNode()
        self.headParts = []
        self.generateHead3('chairman-a', animated=True)
        self.isChairmanPhase2 = 1
        texture2 = loader.loadTexture('phase_14/maps/ttcc_ene_chairman.png')
        for headPart in self.headParts:
            if not self.isSkeleton:
                headPart.setTexture(texture2, 1)

    def makeOttomanPhase2(self, elite=False):
        self.isOttomanPhase2 = 1

    def makeChainsawPhase3(self, elite=False):
        for headPart in self.headParts:
            headPart.removeNode()
        self.isChainsawPhase2 = 0
        self.isChainsawPhase3 = 1
        self.headParts = []
        self.generateHead3('chainsaw', animated=True)
        texture2 = loader.loadTexture('phase_12/maps/ttcc_ene_chainsaw_boardbot.png')
        for headPart in self.headParts:
            if not self.isSkeleton:
                headPart.setTexture(texture2, 1)

    def makeExecutive(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isExecutive = 1
        if self.isSkeleton:
            self.setSuitClothesSkeleton()
            if self.style.body == 'a' and not self.style.name == 'clubpres' and not self.style.name == 'autocad':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                             self.style.dept)
                for headPart in self.headParts:
                    headPart.setTexture(texture, 1)
            if self.style.body == 'b':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                             self.style.dept)
                for headPart in self.headParts:
                    headPart.setTexture(texture, 1)
            if self.style.body == 'c' and not self.style.name == 'dopa' and not self.style.name == 'dopr':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                             self.style.dept)
                for headPart in self.headParts:
                    headPart.setTexture(texture, 1)
        elif self.style.name == 'ins':
            self.setSuitClothes()
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_insider%s.png' % (
                '_exe' if self.isExecutive or self.isGovernaught else '',))
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
        elif self.style.name == 'hho':
            self.setSuitClothes()
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_headhoncho%s.png' % (
                '_exe' if self.isExecutive or self.isGovernaught else '',))
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
        elif self.style.name == 'bgh':
            self.setSuitClothes()
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_bagholder%s.png' % (
                '_exe' if self.isExecutive or self.isGovernaught else '',))
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
        else:
            self.setSuitClothes()

    def makeManager(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        if self.isSkeleton:
            self.setSuitClothesSkeleton()
            if self.style.body == 'a' and self.style.name == 'radiog' or self.style.name == 'ubuster':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                             self.style.dept)
            if self.style.body == 'a' and self.style.name == 'laa':
                texture2 = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' %
                                             self.style.dept)
                modelRoot.find('**/necktie-w').setTexture(texture2, 1)
                modelRoot.find('**/necktie-w').show()
                modelRoot.find('**/bowtie').hide()
            if self.style.body == 'a' and not self.style.name == 'derrhand' and not self.style.name == 'ubuster' and not self.style.name == 'radiog' \
                and not self.style.name == 'charon' and not self.style.name == 'autocad' and not self.style.name == 'clubpres' and not self.style.name == 'hydra' and not self.style.name == 'kerberos' and not self.style.name == 'nix' and not self.style.name == 'styx':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                             self.style.dept)
                for headPart in self.headParts:
                    headPart.setTexture(texture, 1)
                modelRoot.find('**/body').setTexture(texture, 1)
                modelRoot.find('**/necktie-s').setTexture(texture, 1)
                modelRoot.find('**/necktie-w').setTexture(texture, 1)
                modelRoot.find('**/bowtie').setTexture(texture, 1)
            if self.style.body == 'b' and not self.style.name == 'charon' and not self.style.name == 'hydra' and not self.style.name == 'kerberos' and not self.style.name == 'nix' and not self.style.name == 'styx':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                             self.style.dept)
                for headPart in self.headParts:
                    headPart.setTexture(texture, 1)
                modelRoot.find('**/body').setTexture(texture, 1)
                modelRoot.find('**/necktie-s').setTexture(texture, 1)
                modelRoot.find('**/necktie-w').setTexture(texture, 1)
                modelRoot.find('**/bowtie').setTexture(texture, 1)
            if self.style.body == 'c' and self.style.name == 'dopa' or self.style.name == 'dopr':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                             self.style.dept)
                modelRoot.find('**/body').setTexture(texture, 1)
                modelRoot.find('**/necktie-s').setTexture(texture, 1)
                modelRoot.find('**/necktie-w').setTexture(texture, 1)
                modelRoot.find('**/bowtie').setTexture(texture, 1)
            if self.style.body == 'c' and not self.style.name == 'dopr' and not self.style.name == 'dopa' and not self.style.name == 'charon' and not self.style.name == 'hydra' and not self.style.name == 'kerberos' and not self.style.name == 'nix' and not self.style.name == 'styx':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                             self.style.dept)
                for headPart in self.headParts:
                    headPart.setTexture(texture, 1)
                modelRoot.find('**/body').setTexture(texture, 1)
                modelRoot.find('**/necktie-s').setTexture(texture, 1)
                modelRoot.find('**/necktie-w').setTexture(texture, 1)
                modelRoot.find('**/bowtie').setTexture(texture, 1)
        else:
            self.isManager = 1

    def makeHighRoller(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_12/maps/cc_t_ene_highroller_suit_black.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)


    def makeDuckShuffler(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_10/maps/ttcc_ene_suittex_duckshfl.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeHighRollerWhite(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_12/maps/cc_t_ene_highroller_suit.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeBoardbotManager(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_g_e.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makePrethinker(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_suittex_prethink.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeMultislacker(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_suittex_mslacker.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makePacesetter(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_suittex_pacesetter.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)
        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()

    def makeCountErclaim(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_suittex_count.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)
        modelRoot.find('**/bowtie').hide()
        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()

    def makeRedd(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_l_e.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)
        modelRoot.find('**/bowtie').hide()

    def makePlutocrat(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_10/maps/ttcc_ene_suittex_pcrat.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeMouthpiece(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_suittex_mouthp.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeMajorPlayer(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_mplayer.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeFeatherbedder(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_fbed.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeFirestarter(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_fires.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeChainsaw(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_chainsaw.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeVideographer(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_suittex_videographer.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeVideographer2(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_suittex_videographer2.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeDeepDiver(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_suittex_ddiver.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)
        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()

    def makeGatekeeper(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_suittex_gatekeep.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)
        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()

    def makeWSI(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_l_exe.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeBellringer(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_suittex_bellring.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)
        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()

    def makeTreekiller(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_10/maps/ttcc_ene_suittex_treek.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeAutocaddie(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_c_exe.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeDOPA(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_s_exe.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeCountErfit(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isGovernaught = 1
        try:
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_suittex_counterfit.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeDummy(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isGovernaught = 1
        try:
            texture = loader.loadTexture('phase_4/maps/schoolhouse/dummy/ttcc_ene_suittex_djockey.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeGovernaught(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isGovernaught = 1
        if self.isSkeleton:
            self.setSuitClothesSkeleton()
            if self.style.body == 'a':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_gov.png' % self.style.dept)
                for headPart in self.headParts:
                    headPart.setTexture(texture, 1)
            if self.style.body == 'b':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_gov.png' % self.style.dept)
                for headPart in self.headParts:
                    headPart.setTexture(texture, 1)
            if self.style.body == 'c':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_gov.png' % self.style.dept)
                for headPart in self.headParts:
                    headPart.setTexture(texture, 1)
        elif self.style.name == 'ins':
            self.setSuitClothes()
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_insider%s.png' % (
                '_gov' if self.isExecutive or self.isGovernaught else '',))
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
        elif self.style.name == 'hho':
            self.setSuitClothes()
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_headhoncho%s.png' % (
                '_gov' if self.isExecutive or self.isGovernaught else '',))
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
        elif self.style.name == 'bgh':
            self.setSuitClothes()
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_bagholder%s.png' % (
                '_gov' if self.isExecutive or self.isGovernaught else '',))
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
        else:
            self.setSuitClothes()

    def makeIntoImmune(self):
        self.healthBar.setColor(1, 1, 1, 1)
        self.healthBarGlow.setColor(1, 1, 1, 1)
        taskMgr.remove(self.uniqueName('blink-task'))
        self.__pulseWhite()
        self.isImmune = 1

    def removeImmune(self):
        self.healthBar.setColor(1, 1, 1, 1)
        self.healthBarGlow.setColor(1, 1, 1, 1)
        taskMgr.remove(self.uniqueName('blink-task'))
        self.__changeColor()
        self.isImmune = 0

    def makeIntoCTSManager(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_%s_e.png' % self.style.dept)
        if not self.isSkeleton:
            modelRoot.find('**/body').setTexture(texture, 1)

    def getPartTrack(self, particleEffect, startDelay, durationDelay, partExtraArgs, softStop=0):
        particleEffect = partExtraArgs[0]
        parent = partExtraArgs[1]
        if len(partExtraArgs) > 2:
            worldRelative = partExtraArgs[2]
        else:
            worldRelative = 1
        return Sequence(Wait(startDelay),
                        ParticleInterval(particleEffect, parent, worldRelative, duration=durationDelay, cleanup=True,
                                         softStopT=softStop))

    def makeInsured(self):
        self.isInsured= 1

    def removeInsured(self):
        self.isInsured = 0

    def makeExtraAttacks(self, num):
        self.extraAttack = num
        if self.extraAttack == 1:
            knife = loader.loadModel('phase_5/models/props/ttr_m_prp_bat_dagger')
            knife.setScale(0.5)
            knife.reparentTo(self)
            knife.setZ(self.height)
            self.knifeTrack = Parallel(
            Sequence(
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=1.5, toData=0.0, blendType='easeIn'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=1.5, blendType='easeOut')
                ),
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=1.5, toData=0.0, blendType='easeIn')
                ),
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut')
                ),
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=1.5, blendType='easeOut'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn')
                )
            ),
            LerpHprInterval(knife, 4.0, VBase3(360.0, 270.0, 0.0), startHpr=VBase3(0.0, 270.0, 0.0))
        )
            self.knifeTrack.loop()
        if self.extraAttack == 2:
            knife = loader.loadModel('phase_5/models/props/ttr_m_prp_bat_dagger')
            knife.setScale(0.5)
            knife.reparentTo(self)
            knife.setZ(self.height)
            self.knifeTrack2 = Parallel(
            Sequence(
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=1.5, toData=0.0, blendType='easeIn'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=1.5, blendType='easeOut')
                ),
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=1.5, toData=0.0, blendType='easeIn')
                ),
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut')
                ),
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=1.5, blendType='easeOut'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn')
                )
            ),
            LerpHprInterval(knife, 4.0, VBase3(360.0, 270.0, 0.0), startHpr=VBase3(0.0, 270.0, 0.0))
        )
            self.knifeTrack2.loop()
        if self.extraAttack == 3:
            knife = loader.loadModel('phase_5/models/props/ttr_m_prp_bat_dagger')
            knife.setScale(0.5)
            knife.reparentTo(self)
            knife.setZ(self.height)
            self.knifeTrack3 = Parallel(
            Sequence(
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=1.0, toData=0.0, blendType='easeIn'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=1.0, blendType='easeOut')
                ),
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=-1.0, blendType='easeOut'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=1.0, toData=0.0, blendType='easeIn')
                ),
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=-1.0, toData=0.0, blendType='easeIn'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=-1.0, blendType='easeOut')
                ),
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=1.0, blendType='easeOut'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=-1.0, toData=0.0, blendType='easeIn')
                )
            ),
            LerpHprInterval(knife, 4.0, VBase3(360.0, 270.0, 0.0), startHpr=VBase3(0.0, 270.0, 0.0))
        )
            self.knifeTrack3.loop()
        if self.extraAttack == 4:
            knife = loader.loadModel('phase_5/models/props/ttr_m_prp_bat_dagger')
            knife.setScale(0.5)
            knife.reparentTo(self)
            knife.setZ(self.height)
            self.knifeTrack4 = Parallel(
            Sequence(
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=1.5, toData=0.0, blendType='easeIn'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=1.5, blendType='easeOut')
                ),
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=1.5, toData=0.0, blendType='easeIn')
                ),
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut')
                ),
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=1.5, blendType='easeOut'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn')
                )
            ),
            LerpHprInterval(knife, 4.0, VBase3(360.0, 270.0, 0.0), startHpr=VBase3(0.0, 270.0, 0.0))
        )
            self.knifeTrack4.loop()
        if self.extraAttack == 5:
            knife = loader.loadModel('phase_5/models/props/ttr_m_prp_bat_dagger')
            knife.setScale(0.5)
            knife.reparentTo(self)
            knife.setZ(self.height)
            self.knifeTrack5 = Parallel(
            Sequence(
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=1.5, toData=0.0, blendType='easeIn'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=1.5, blendType='easeOut')
                ),
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=1.5, toData=0.0, blendType='easeIn')
                ),
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut')
                ),
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=1.5, blendType='easeOut'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn')
                )
            ),
            LerpHprInterval(knife, 4.0, VBase3(360.0, 270.0, 0.0), startHpr=VBase3(0.0, 270.0, 0.0))
        )
            self.knifeTrack5.loop()
        if self.extraAttack == 6:
            knife = loader.loadModel('phase_5/models/props/ttr_m_prp_bat_dagger')
            knife.setScale(0.5)
            knife.reparentTo(self)
            knife.setZ(self.height)
            self.knifeTrack6 = Parallel(
            Sequence(
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=1.5, toData=0.0, blendType='easeIn'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=1.5, blendType='easeOut')
                ),
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=1.5, toData=0.0, blendType='easeIn')
                ),
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut')
                ),
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=1.5, blendType='easeOut'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn')
                )
            ),
            LerpHprInterval(knife, 4.0, VBase3(360.0, 270.0, 0.0), startHpr=VBase3(0.0, 270.0, 0.0))
        )
            self.knifeTrack6.loop()
        if self.extraAttack == 7:
            knife = loader.loadModel('phase_5/models/props/ttr_m_prp_bat_dagger')
            knife.setScale(0.5)
            knife.reparentTo(self)
            knife.setZ(self.height)
            self.knifeTrack7 = Parallel(
            Sequence(
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=1.5, toData=0.0, blendType='easeIn'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=1.5, blendType='easeOut')
                ),
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=1.5, toData=0.0, blendType='easeIn')
                ),
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut')
                ),
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=1.5, blendType='easeOut'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn')
                )
            ),
            LerpHprInterval(knife, 4.0, VBase3(360.0, 270.0, 0.0), startHpr=VBase3(0.0, 270.0, 0.0))
        )
            self.knifeTrack7.loop()
        if self.extraAttack == 8:
            knife = loader.loadModel('phase_5/models/props/ttr_m_prp_bat_dagger')
            knife.setScale(0.5)
            knife.reparentTo(self)
            knife.setZ(self.height)
            self.knifeTrack8 = Parallel(
            Sequence(
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=1.5, toData=0.0, blendType='easeIn'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=1.5, blendType='easeOut')
                ),
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=1.5, toData=0.0, blendType='easeIn')
                ),
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut')
                ),
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=1.5, blendType='easeOut'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn')
                )
            ),
            LerpHprInterval(knife, 4.0, VBase3(360.0, 270.0, 0.0), startHpr=VBase3(0.0, 270.0, 0.0))
        )
            self.knifeTrack8.loop()
        if self.extraAttack == 9:
            knife = loader.loadModel('phase_5/models/props/ttr_m_prp_bat_dagger')
            knife.setScale(0.5)
            knife.reparentTo(self)
            knife.setZ(self.height)
            self.knifeTrack9 = Parallel(
            Sequence(
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=1.5, toData=0.0, blendType='easeIn'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=1.5, blendType='easeOut')
                ),
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=1.5, toData=0.0, blendType='easeIn')
                ),
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut')
                ),
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=1.5, blendType='easeOut'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn')
                )
            ),
            LerpHprInterval(knife, 4.0, VBase3(360.0, 270.0, 0.0), startHpr=VBase3(0.0, 270.0, 0.0))
        )
            self.knifeTrack9.loop()
        if self.extraAttack == 10:
            knife = loader.loadModel('phase_5/models/props/ttr_m_prp_bat_dagger')
            knife.setScale(0.5)
            knife.reparentTo(self)
            knife.setZ(self.height)
            self.knifeTrack10 = Parallel(
            Sequence(
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=1.5, toData=0.0, blendType='easeIn'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=1.5, blendType='easeOut')
                ),
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=1.5, toData=0.0, blendType='easeIn')
                ),
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut')
                ),
                Parallel(
                    LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=1.5, blendType='easeOut'),
                    LerpFunctionInterval(knife.setY, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn')
                )
            ),
            LerpHprInterval(knife, 4.0, VBase3(360.0, 270.0, 0.0), startHpr=VBase3(0.0, 270.0, 0.0))
        )
            self.knifeTrack10.loop()


    def getExtraAttacks(self):
        return self.extraAttack

    def removeExtraAttacks(self):
        self.extraAttack = 0
        if self.knifeTrack != None:
            self.knifeTrack.finish()

    def makeBookkeeping(self):
        self.isBookkeeping= 1
        node = self.getGeomNode().getChild(0)
        self.suitColorTrack = Sequence(LerpColorScaleInterval(node, duration=1, colorScale=(0.537, 0.878, 0.533, 1),
                                                         blendType='easeInOut'),
                                  LerpColorScaleInterval(node, duration=1, colorScale=(1, 1, 1, 1),
                                                         blendType='easeInOut'),
                                  LerpColorScaleInterval(node, duration=1, colorScale=(0.537, 0.878, 0.533, 1),
                                                         blendType='easeInOut'),
                                  LerpColorScaleInterval(node, duration=1, colorScale=(1, 1, 1, 1)))
        self.suitColorTrack.loop()

    def removeBookkeeping(self):
        self.isBookkeeping = 0
        if self.suitColorTrack != None:
            self.suitColorTrack.finish()

    def makeDanceSession(self):
        self.isDanceSession = 1

    def removeDanceSession(self):
        self.isDanceSession = 0

    def makeSued(self, num):
        self.isSued = num

    def getSuedRounds(self):
        return self.isSued

    def removeSued(self):
        self.isSued = 0

    def makeContracted(self):
        self.isContracted= 1

    def removeContracted(self):
        self.isContracted = 0

    def makeIntoPhase3(self):
        self.isPhase3 = 1

    def removePhase3(self):
        self.isPhase3 = 0

    def makeLitigationManager(self):
        self.isLitigationManager = 1

    def makeIntoEnraged(self):
        BattleParticles.loadParticles()
        self.isEnraged = 1
        baseFlameEffect = BattleParticles.createParticleEffect(file='firedBaseFlame')
        flameEffect = BattleParticles.createParticleEffect('FiredFlame')
        flecksEffect = BattleParticles.createParticleEffect('SpriteFiredFlecks')
        BattleParticles.setEffectTexture(baseFlameEffect, 'fire')
        BattleParticles.setEffectTexture(flameEffect, 'fire')
        BattleParticles.setEffectTexture(flecksEffect, 'roll-o-dex', color=Vec4(0.95, 0.95, 0.0, 1))
        self.baseFlameTrack = self.getPartTrack(baseFlameEffect, 0, 5.5, [baseFlameEffect, self, 0])
        self.flameTrack = self.getPartTrack(flameEffect, 0, 5.5, [flameEffect, self, 0])
        self.flecksTrack = self.getPartTrack(flecksEffect, 0, 5.5, [flecksEffect, self, 0])
        self.baseFlameTrack.loop()
        self.flameTrack.loop()
        self.flecksTrack.loop()

    def removeEnraged(self):
        self.isEnraged = 0
        if self.baseFlameTrack != None:
            self.baseFlameTrack.finish()
        if self.flameTrack != None:
            self.flameTrack.finish()
        if self.flecksTrack != None:
            self.flecksTrack.finish()

    def makeIntoAbsorbing(self):
        self.isAbsorbing = 1

    def removeAbsorbing(self):
        self.isAbsorbing = 0

    def makeFrozen(self):
        self.isFrozen = 1

    def makeUnFrozen(self):
        self.isFrozen = 0

    def makeIntoSoaked(self):
        self.isSoaked = 1

    def removeSoaked(self):
        self.isSoaked = 0

    def getHeadParts(self):
        return self.headParts

    def getAnimatedHeadParts(self):
        return self.animatedHeadParts

    def getRightHand(self):
        return self.rightHand

    def getLeftHand(self):
        return self.leftHand

    def getShadowJoint(self):
        return self.shadowJoint

    def getNametagJoints(self):
        return []

    def getDialogueArray(self):
        if self.style.name == 'clubpres':
            loadDialog(1)
            return SkelecogDialogArray
        if self.style.name == 'derrman' and not self.isSkeleton:
            loadDialog(1)
            return DerrickManDialogArray
        if self.style.name == 'derrhand' and not self.isSkeleton:
            loadDialog(1)
            return DerrickHandDialogArray
        if self.style.name == 'derrhand' and self.isSkeleton:
            loadDialog(1)
            return DerrickSkeleDialogArray
        if self.style.name == 'fires' and not self.isSkeleton:
            loadDialog(1)
            return FirestarterDialogArray
        if self.style.name == 'fbed' and not self.isSkeleton:
            loadDialog(1)
            return FeatherbedderDialogArray
        if self.style.name == 'mplayer' and not self.isSkeleton:
            loadDialog(1)
            return MajorPlayerDialogArray
        if self.style.name == 'mplayer2' and not self.isSkeleton:
            loadDialog(1)
            return MajorPlayerDialogArray
        if self.style.name == 'chainsaw' and not self.isSkeleton:
            loadDialog(1)
            return ChainsawDialogArray
        if self.style.name == 'chainsaw2' and not self.isSkeleton:
            loadDialog(1)
            return ChainsawORDialogArray
        if self.style.name == 'phouse' and not self.isSkeleton:
            loadDialog(1)
            return DerrickHandDialogArray
        if self.style.name == 'bkeeper' and not self.isSkeleton:
            loadDialog(1)
            return CaseManagerDialogArray
        if self.style.name == 'wtapper' and not self.isSkeleton:
            loadDialog(1)
            return StenographerDialogArray
        if self.style.name == 'ambass' and not self.isSkeleton:
            loadDialog(1)
            return PrethinkerDialogArray
        if self.style.name == 'ambass' and self.isSkeleton:
            loadDialog(1)
            return PrethinkerDialogArray
        if self.style.name == 'mm' and not self.isSkeleton:
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'dhr' and not self.isSkeleton:
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'nn' and not self.isSkeleton:
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'sh' and not self.isSkeleton:
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'mouthp' and not self.isSkeleton:
            loadDialog(1)
            return MouthpieceDialogArray
        if self.style.name == 'whunter' and not self.isSkeleton:
            loadDialog(1)
            return WitchHunterDialogArray
        if self.style.name == 'erfit' and not self.isSkeleton:
            loadDialog(1)
            return CountErfitDialogArray
        if self.style.name == 'rainmake' and not self.isSkeleton:
            loadDialog(1)
            return RainmakerDialogArray
        if self.style.name == 'redd' and not self.isSkeleton:
            loadDialog(1)
            return ReddDialogArray
        if self.style.name == 'sgoat' and not self.isSkeleton:
            loadDialog(1)
            return ScapegoatDialogArray
        if self.style.name == 'caseman' and not self.isSkeleton:
            loadDialog(1)
            return CaseManagerDialogArray
        if self.style.name == 'stenog' and not self.isSkeleton:
            loadDialog(1)
            return StenographerDialogArray
        if self.style.name == 'lgator' and not self.isSkeleton:
            loadDialog(1)
            return LitigatorDialogArray
        if self.style.name == 'nc' and not self.isSkeleton:
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'arbit' and not self.isSkeleton:
            loadDialog(1)
            return CLODialogArray
        if self.style.name == 'arbit' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'ang' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'ang' and not self.isSkeleton:
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'whistleb' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'whistleb' and not self.isSkeleton:
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'bfh' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'bfh' and not self.isSkeleton:
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'shb' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'shb' and not self.isSkeleton:
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'hck' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'hck' and not self.isSkeleton:
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'ksp' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'ksp' and not self.isSkeleton:
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'duckshfl' and not self.isSkeleton:
            loadDialog(1)
            return DuckShufflerDialogArray
        if self.style.name == 'treek' and not self.isSkeleton:
            loadDialog(1)
            return TreekillerDialogArray
        if self.style.name == 'pcrat' and not self.isSkeleton:
            loadDialog(1)
            return PlutocratDialogArray
        if self.style.name == 'hroller' and not self.isSkeleton:
            loadDialog(1)
            return HighRollerDialogArray
        if self.style.name == 'hrollers' and not self.isSkeleton:
            loadDialog(1)
            return HighRollerDialogArray
        if self.style.name == 'hroller2' and not self.isSkeleton:
            loadDialog(1)
            return HighRollerDialogArray
        if self.style.name == 'nd' and not self.isSkeleton:
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'm' and not self.isSkeleton:
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'dopr':
            loadDialog(1)
            return DOPRDialogArray
        if self.style.name == 'dopa':
            loadDialog(1)
            return DOPADialogArray
        if self.style.name == 'bellring' and not self.isSkeleton:
            loadDialog(1)
            return BellringerDialogArray
        if self.style.name == 'erfit' and not self.isSkeleton:
            loadDialog(1)
            return CountErfitDialogArray
        if self.style.name == 'prethink' and not self.isSkeleton:
            loadDialog(1)
            return PrethinkerDialogArray
        if self.style.name == 'mslacker' and not self.isSkeleton:
            loadDialog(1)
            return MultislackerDialogArray
        if self.style.name == 'videog' and not self.isSkeleton:
            loadDialog(1)
            return PacesetterDialogArray
        if self.style.name == 'bcaster' and not self.isSkeleton:
            loadDialog(1)
            return PacesetterDialogArray
        if self.style.name == 'radiog':
            loadDialog(1)
            return DOPADialogArray
        if self.style.name == 'racket' and not self.isSkeleton:
            loadDialog(1)
            return ReddDialogArray
        if self.style.name == 'ubuster':
            loadDialog(1)
            return DOPRDialogArray
        if self.style.name == 'safesupervis' and not self.isSkeleton:
            loadDialog(1)
            return DOLDDialogArray
        if self.style.name == 'psetter' and not self.isSkeleton:
            loadDialog(1)
            return PacesetterDialogArray
        if self.style.name == 'ddiver' and not self.isSkeleton:
            loadDialog(1)
            return DeepDiverDialogArray
        if self.style.name == 'gatekeep' and not self.isSkeleton:
            loadDialog(1)
            return GatekeeperDialogArray
        if self.style.name == 'dola' and not self.isSkeleton:
            loadDialog(1)
            return DOLADialogArray
        if self.style.name == 'dold' and not self.isSkeleton:
            loadDialog(1)
            return DOLDDialogArray
        if self.style.name == 'ghd' and not self.isSkeleton:
            loadDialog(1)
            return HighRollerDialogArray
        if self.style.name == 'fmaker':
            loadDialog(1)
            return SkelecogDialogArray
        if self.style.name == 'director':
            loadDialog(1)
            return SkelecogDialogArray
        if self.style.name == 'jgd' and not self.isSkeleton:
            loadDialog(1)
            return FeatherbedderDialogArray
        if self.style.name == 'bby' and not self.isSkeleton:
            loadDialog(1)
            return ChairmanDialogArray
        if self.style.name == 'dking' and not self.isSkeleton:
            loadDialog(1)
            return ReddDialogArray
        if self.style.name == 'ottoman' and not self.isSkeleton:
            loadDialog(1)
            return OttomanDialogArray
        if self.style.name == 'crystal' and not self.isSkeleton:
            loadDialog(1)
            if self.isChainsawPhase2:
                return ChainsawORDialogArray
            elif self.isChainsawPhase3:
                return ChainsawDialogArray
            else:
                return ChainsawDialogArray
        if self.style.name == 'wrt' and not self.isSkeleton:
            loadDialog(1)
            return StenographerDialogArray
        if self.style.name == 'dar' and not self.isSkeleton:
            loadDialog(1)
            return WitchHunterDialogArray
        if self.style.name == 'nhy' and not self.isSkeleton:
            loadDialog(1)
            return DOLDDialogArray
        if self.style.name == 'auh' and not self.isSkeleton:
            loadDialog(1)
            return PlutocratDialogArray
        if self.style.name == 'chairman' and not self.isSkeleton:
            loadDialog(1)
            return ChairmanDialogArray
        if self.style.name == 'judy' and not self.isSkeleton:
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'judy' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'bfh2' and not self.isSkeleton:
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'bfh2' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'mm' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'wtapper' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'nn' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'sh' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'rainmake' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'stenog' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'mouthp' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'nc' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'nd' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'm' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'crystal' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'yuh' and not self.isSkeleton:
            loadDialog(1)
            return DeskJockeyDialogArray
        if self.style.name == 'phs' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'wrt' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        elif self.isSkeleton:
            loadSkelDialog()
            return SkelSuitDialogArray
        else:
            return SuitDialogArray

    def generateBeanCounter(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_beancounter')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(0)
        self.isHud = True

    def generateToxicManager(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_toxicmanager')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(0)
        self.isHud = True

    def generateHeadHunter(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_headhunter')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(0)
        self.isHud = True

    def generateMagnate(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_magnate-zero')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(0)
        self.isHud = True

    def generateCorporateRaider(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_corporateraider-zero')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(0)
        self.isHud = True

    def generateBigCheese(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_bigcheese')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(0)
        self.isHud = True

    def generateHeadHoncho(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_headhoncho')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(0)
        self.isHud = True

    def generateSwindler(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_swindler')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(0)
        self.isHud = True

    def generateNumberCruncher(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_numbercruncher')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(0)
        self.isHud = True

    def generateMoneyBags(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_moneybags')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(0)
        self.isHud = True

    def generateLoanShark(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_loanshark-zero')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(0)
        self.isHud = True

    def generateLoanShark2(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_loanshark-zero')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(-.1)
        self.isHud = True

    def generateRobberBaron(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_robberbaron-zero')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(0)
        self.isHud = True

    def generateBigFish(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_bigfish')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(0)
        self.isHud = True

    def generateNameDropper(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_namedropper-zero')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(0)
        self.isHud = True

    def generateMoverShaker(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_moverandshaker')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(0)
        self.isHud = True

    def generateTwoFace(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_twoface-zero')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(0)
        self.isHud = True

    def generateMingler(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_mingler-zero')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(0)
        self.isHud = True

    def generateHollywood(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_mrhollywood-zero')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(0)
        self.isHud = True

    def generateMiddleman(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_middleman')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(0)
        self.isHud = True

    def generateColdCaller(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_coldcaller')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(0)
        self.isHud = True

    def generateConArtist(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_conartist')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(0)
        self.isHud = True

    def generateConnoisseur(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_connoisseur')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(0)
        self.isHud = True

    def generateAngelWings(self):
        self.Vault = loader.loadModel('phase_13/models/props/angel_wings')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1.5)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(1)
        self.isHud = True

    def generateAngelHalo(self):
        self.Vault = loader.loadModel('phase_13/models/props/angel_halo')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1.5)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(1)
        self.isHud = True

    def generateFlunky(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_flunky')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(0)
        self.isHud = True

    def generateGladHander(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_gladhander')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(0)
        self.isHud = True

    def generatePencilPusher(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_pencilpusher')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(0)
        self.isHud = True

    def generatePennyPincher(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_pennypincher')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(0)
        self.isHud = True

    def generateShortChange(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_shortchange')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(0)
        self.isHud = True

    def generateTelemarketer(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_telemarketer')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(0)
        self.isHud = True

    def generateTelemarketer2(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_telemarketer')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(-.1)
        self.isHud = True

    def generateTightwad(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_tightwad')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(0)
        self.isHud = True

    def generateYesman(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_yesman')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(0)
        self.isHud = True

    def generateMicromanager(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_micromanager')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(0)
        self.isHud = True

    def generateBelt(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_conveyancer_belt')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(0)
        self.isHud = True

    def generateMolder(self):
        self.Vault = loader.loadModel('phase_12/models/bossbotHQ/mole_cog')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(-.4)
        self.Vault.setScale(.7)
        self.Vault.setH(180)
        self.isHud = True

    def generateSafe(self):
        self.Vault = loader.loadModel('phase_5/models/props/safe-mod')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(-.4)
        self.Vault.setScale(.7)
        self.Vault.setH(180)
        self.isHud = True