from direct.actor import Actor
from direct.directnotify import DirectNotifyGlobal
from otp.avatar import Avatar
from direct.interval.IntervalGlobal import *
from toontown.suit import SuitDNA
from toontown.toonbase import ToontownGlobals
from pandac.PandaModules import *
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
AllSuits = (('walk', 'walk'),
            ('run', 'walk'),
('calculator', 'calculator'),
('calculating-costs', 'calculating-costs'),
('phone', 'phone'),
('blue-chip', 'blue-chip'),
('falling-knife', 'falling-knife'),
('throw-object', 'throw-object'),
('flail-wb', 'flailing-wb'),
                    ('tnt-react', 'tnt-react'),
                    ('flail-qs', 'flailing-qs'),
('throw-paper', 'throw-paper'),
('mob-mentality', 'mob-mentality'),
            ('neutral', 'neutral'),
('neutral2', 'neutral'),
('magnet', 'magnet'),
('neutral2-hurt', 'neutral-hurt'),
            ('neutral-hurt', 'neutral-hurt'),
            ('neutral-unstable', 'neutral-unstable'),
            ('neutral-enraged-return', 'neutral-enraged-return'),
            ('ottoman-sit-loop', 'ottoman-sit-loop'),
('ottoman-writing-loop', 'ottoman-writing-loop'),
('ottoman-writing-start', 'ottoman-writing-start'),
('ottoman-writing-stop', 'ottoman-writing-stop'),
('neutral-override', 'neutral-override'),
('neutral-override-glitched', 'neutral-override-glitched'),
            ('neutral-enraged-return', 'neutral-enraged-return'),
            ('neutral-enraged', 'neutral-enraged'),
('highroller-neutral-levitate-loop', 'highroller-neutral-levitate-loop'),
('highroller-neutral-levitate-in-out', 'highroller-neutral-levitate-in-out'),
            ('wrecked', 'wrecked'),
            ('lose3', 'wrecked'),
            ('headless-death', 'headless-death'))
AllSuitsMinigame = (('victory', 'victory'),
                    ('flail', 'flailing'),
                    ('flail-wb', 'flailing-wb'),
                    ('tnt-react', 'tnt-react'),
                    ('flail-qs', 'flailing-qs'),
                    ('tug-o-war', 'tug-o-war'),
                    ('slip-backward', 'slip-backward'),
                    ('lose3', 'wrecked'),
                    ('slip-forward', 'slip-forward'))
AllSuitsTutorialBattle = (('lose', 'lose'),
                          ('lose2', 'headless-death'),
                          ('wrecked', 'wrecked'),
                          ('lose3', 'wrecked'),
                          ('dance', 'song-and-dance'),
                          ('pie-small-react', 'pie-small'),
                          ('squirt-small-react', 'squirt-small'))
AllSuitsBattle = (('drop-react', 'anvil-drop'),
 ('flatten', 'drop'),
 ('headless-death', 'headless-death'),
 ('dance', 'song-and-dance'),
                  ('frustrated', 'frustrated-f'),
 ('lose3', 'wrecked'),
                  ('gag-miss', 'gag-miss'),
                  ('pie-large', 'pie-large'),
                  ('pie-large-lured', 'pie-large-lured'),
('highroller-neutral-levitate-loop', 'highroller-neutral-levitate-loop', 4),
('highroller-neutral-levitate-in-out', 'highroller-neutral-levitate-in-out', 4),
 ('wrecked', 'wrecked'),
 ('sidestep-left', 'sidestep-left'),
 ('sidestep-right', 'sidestep-right'),
 ('squirt-large-react', 'squirt-large'),
 ('sound-react', 'sound-react'),
                  ('sound-react-bow', 'sound-react-bow'),
                  ('sound-react-nt', 'sound-react-nt'),
 ('landing', 'landing'),
 ('reach', 'walknreach-bill'),
 ('rake-react', 'rake'),
 ('hypnotized', 'hypnotize'),
 ('shock', 'shock'),
('large-zap', 'large-zap'),
('small-zap', 'small-zap'),
 ('soak', 'soak'),
                  ('lured', 'lured'),
 ('lured2', 'lured'))
SuitsCEOBattle = (('sit', 'sit'),
 ('sit-eat-in', 'sit-eat-in'),
 ('sit-eat-loop', 'sit-eat-loop'),
 ('sit-eat-out', 'sit-eat-out'),
 ('lose3', 'wrecked'),
 ('sit-angry', 'sit-angry'),
('sit-exec', 'sit-exec'),
 ('sit-hungry-left', 'leftsit-hungry'),
 ('sit-hungry-right', 'rightsit-hungry'),
 ('sit-lose', 'sit-lose'),
 ('tray-walk', 'tray-walk'),
 ('tray-neutral', 'tray-neutral'),
 ('sit-lose', 'sit-lose'),
 ('headless-death', 'headless-death'))
f = (('throw-paper', 'throw-paper', 4),
     ('phone', 'phone', 4),
     ('lose3', 'wrecked', 4),
     ('shredder', 'shredder', 4))
p = (('pencil-sharpener', 'pencil-sharpener', 4),
     ('pen-squirt', 'pen-squirt', 4),
     ('lose3', 'wrecked', 4),
     ('hold-eraser', 'hold-eraser', 4),
     ('finger-wag', 'finger-wag', 4),
     ('hold-pencil', 'hold-pencil', 4))
ym = (('magic3', 'magic3', 4),
      ('finger-wag', 'finger-wag', 4),
      ('throw-paper', 'throw-paper', 4),
      ('lose3', 'wrecked', 4),
      ('throw-object', 'throw-object', 4))
mm = (('golf-club-swing', 'golf-club-swing', 4),
      ('magic3', 'magic3', 4),
      ('lose3', 'wrecked', 4),
      ('rubber-stamp', 'rubber-stamp', 4),
      ('smile', 'smile', 4))
ds =  (('roll-o-dex', 'roll-o-dex', 4),
       ('magic3', 'magic3', 4),
       ('lose3', 'wrecked', 4),
('effort', 'effort', 4),
       ('smile', 'smile', 4))
hh = (('speak', 'speak', 4),
      ('effort', 'effort', 4),
      ('lose3', 'wrecked', 4),
      ('magic1', 'magic1', 4),
      ('pen-squirt', 'fountain-pen', 4))
cr = (('glower', 'glower', 4),
       ('lose3', 'wrecked', 4),
('effort', 'effort', 4),
       ('speak', 'speak', 4),
       ('cigar-smoke', 'cigar-smoke', 4),
       ('magic2', 'magic2', 4),
       ('golf-club-swing', 'golf-club-swing', 4),
       ('quick-jump', 'jump', 4))
tbc = (('magic2', 'magic2', 4),
('magic3', 'magic3', 4),
       ('throw-paper', 'throw-paper', 4),
       ('throw-object', 'throw-object', 4),
       ('lose3', 'wrecked', 4))
trb = (('magic1', 'magic1', 4),
       ('speak', 'speak', 4),
('golf-club-swing', 'golf-club-swing', 4),
       ('lose3', 'wrecked', 4),
       ('glower', 'glower', 4),
       ('magic3', 'magic3', 4))
dot = (('glower', 'glower', 4),
       ('throw-paper', 'throw-paper', 4),
       ('lose3', 'wrecked', 4),
       ('magic1', 'magic1', 4),
       ('magic3', 'magic3', 4),
       ('roll-o-dex', 'roll-o-dex', 4))
dvg = (('glower', 'glower', 4),
       ('lose3', 'wrecked', 4),
('effort', 'effort', 4),
       ('speak', 'speak', 4),
       ('cigar-smoke', 'cigar-smoke', 4),
       ('magic2', 'magic2', 4),
       ('golf-club-swing', 'golf-club-swing', 4),
       ('quick-jump', 'jump', 4))
cpl = (('glower', 'glower', 4),
('effort', 'effort', 4),
       ('throw-paper', 'throw-paper', 4),
       ('lose3', 'wrecked', 4),
       ('throw-object', 'throw-object', 4),
       ('pickpocket', 'pickpocket', 4))
bkp = (('glower', 'glower', 4),
       ('magic2', 'magic2', 4),
       ('magic1', 'magic1', 4),
('effort', 'effort', 4),
       ('lose3', 'wrecked', 4),
       ('cigar-smoke', 'cigar-smoke', 4))
kpn = (('glower', 'glower', 4),
       ('golf-club-swing', 'golf-club-swing', 4),
       ('lose3', 'wrecked', 4),
       ('magic3', 'magic3', 4),
       ('magic1', 'magic1', 4),
       ('cigar-smoke', 'cigar-smoke', 4))
cg = (('magic1', 'magic1', 4),
      ('glower', 'glower', 4),
      ('calculating-costs', 'calculating-costs', 4),
      ('cease', 'cease', 4),
      ('magic3', 'magic3', 4),
      ('lose3', 'wrecked', 4),
      ('golf-club-swing', 'golf-club-swing', 4),
      ('song-and-dance', 'song-and-dance', 4),
      ('cigar-smoke', 'cigar-smoke', 4))
bg = (('magic1', 'magic1', 4),
      ('glower', 'glower', 4),
      ('falling-knife', 'falling-knife', 4),
      ('lose3', 'wrecked', 4),
      ('frustrated', 'frustrated', 4),
      ('golf-club-swing', 'golf-club-swing', 4),
      ('song-and-dance', 'song-and-dance', 4),
      ('cigar-smoke', 'cigar-smoke', 4),
      ('throw-paper', 'throw-paper', 4))
msr = (('magic1', 'magic1', 4),
      ('pen-squirt', 'fountain-pen', 4),
      ('lose3', 'wrecked', 4),
      ('quick-jump', 'jump', 4))
kb = (('pen-squirt', 'fountain-pen', 4),
      ('quick-jump', 'jump', 4),
      ('pickpocket', 'sanction', 4),
      ('magic1', 'magic1', 4),
      ('magic3', 'magic3', 4),
      ('lose3', 'wrecked', 4),
      ('falling-knife', 'falling-knife', 4),
      ('objection-in', 'cease', 4),
      ('glower', 'glower', 4),
      ('summon', 'summon', 4),
      ('speak', 'speak', 4),
      ('cease', 'cease', 4),
      ('throw-paper', 'throw-paper', 4),
      ('throw-object', 'throw-object', 4),
      ('layoffs', 'layoffs', 4))
ts = (('pen-squirt', 'fountain-pen', 4),
      ('quick-jump', 'jump', 4),
      ('pickpocket', 'sanction', 4),
      ('magic1', 'magic1', 4),
('neutral', 'rolled', 4),
      ('magic3', 'magic3', 4),
      ('lose3', 'wrecked', 4),
      ('defense', 'defense', 4),
      ('objection-in', 'cease', 4),
      ('glower', 'glower', 4),
      ('summon', 'summon', 4),
      ('speak', 'speak', 4),
      ('cease', 'cease', 4),
      ('throw-paper', 'throw-paper', 4),
      ('throw-object', 'throw-object', 4),
      ('layoffs', 'layoffs', 4))
tc = (('speak', 'speak', 4),
      ('cigar-smoke', 'firestarter-cigar-smoke', 4),
      ('magic2', 'magic2', 4),
      ('magic1', 'magic1', 4))
tg = (('throw-object', 'throw-object', 4),
      ('throw-paper', 'throw-paper', 4),
      ('magic1', 'magic1', 4))
tb = (('quick-jump', 'jump', 4),
      ('speak', 'speak', 4),
      ('snap', 'snap', 4),
('highroller-neutral-levitate-loop', 'highroller-neutral-levitate-loop', 4),
('highroller-neutral-levitate-in-out', 'highroller-neutral-levitate-in-out', 4),
('caress', 'caress', 4),
('kneel-caress-into', 'kneel-caress-into', 4),
('kneel-into', 'kneel-into', 4),
('kneel-out', 'kneel-out', 4),
('kneel-caress-out', 'kneel-caress-out', 4),
      ('cease', 'cease', 4),
      ('song-and-dance', 'song-and-dance', 4),
      ('summon', 'summon', 4),
      ('pickpocket', 'pickpocket', 4),
      ('magic3', 'magic3', 4),
      ('neutral', 'rolled', 4))
adc = (('throw-object', 'throw-object', 4),
       ('throw-paper', 'throw-paper', 4),
       ('snap', 'snap', 4),
       ('defense', 'scabbard', 4),
       ('roll-o-dex', 'roll-o-dex', 4),
       ('lose3', 'wrecked', 4),
       ('glower', 'glower', 4),
       ('quick-jump', 'jump', 4),
       ('finger-wag', 'cease', 4),
       ('revvedup', 'revvedup', 4))
drm = (('throw-object', 'throw-object', 4),
       ('throw-paper', 'throw-paper', 4),
       ('snap', 'snap', 4),
       ('defense', 'scabbard', 4),
       ('roll-o-dex', 'roll-o-dex', 4),
       ('lose3', 'wrecked', 4),
       ('glower', 'glower', 4),
       ('quick-jump', 'jump', 4),
       ('finger-wag', 'cease', 4),
       ('revvedup', 'revvedup', 4),
       ('neutral', 'neutral-override', 4))
cp = (('magic3', 'magic3', 4),
('magic2', 'magic2', 4),
      ('throw-object', 'throw-object', 4),
      ('throw-paper', 'throw-paper', 4),
      ('lose3', 'wrecked', 4),
      ('sanction', 'sanction', 4),
      ('scabbard', 'scabbard', 4),
      ('golf-club-swing', 'golf-club-swing', 4),
      ('summon', 'summon', 4),
      ('defense', 'defense', 4),
      ('snap', 'snap', 4),
      ('glower', 'glower', 4),
      ('magic1', 'magic1', 4),
      ('quick-jump', 'jump', 4))
fbd = (('throw-object', 'throw-object', 4),
       ('throw-paper', 'throw-paper', 4),
       ('falling-knife', 'falling-knife', 4),
       ('sanction', 'sanction', 4),
       ('lose3', 'wrecked', 4),
       ('frustrated', 'frustrated', 4),
       ('effort', 'effort', 4),
       ('speak', 'speak', 4),
       ('roll-o-dex', 'roll-o-dex', 4),
       ('glower', 'glower', 4),
       ('pickpocket', 'sanction', 4),
       ('cigar-smoke', 'cigar-smoke', 4),
       ('snap', 'snap', 4),
       ('cease', 'cease', 4),
       ('magic2', 'magic2', 4))
frs = (('magic3', 'magic3', 4),
       ('calculating-costs', 'calculating-costs', 4),
       ('magic2', 'magic2', 4),
       ('speak', 'speak', 4),
       ('snap', 'snap', 4),
       ('frustrated', 'frustrated-f', 4),
       ('sanction', 'sanction2', 4),
       ('cease', 'cease3', 4),
       ('lose3', 'wrecked', 4),
       ('phone', 'phone', 4))
gtk = (('magic3', 'magic3', 4),
       ('throw-object', 'throw-object', 4),
       ('throw-paper', 'throw-paper', 4),
       ('golf-club-swing', 'golf-club-swing', 4),
       ('glower', 'glower', 4),
       ('summon', 'summon', 4),
       ('speak', 'speak', 4),
       ('frustrated', 'frustrated', 4),
       ('lose3', 'wrecked', 4),
       ('cease2', 'sanction', 4),
       ('objection-in', 'cease', 4),
       ('summon', 'summon', 4),
       ('cease', 'cease', 4),
       ('pickpocket', 'pickpocket', 4),
       ('magic1', 'magic1', 4),
       ('effort', 'effort', 4),
       ('snap', 'snap', 4),
       ('magic2', 'magic2', 4),
       ('speak', 'speak', 4))
cc = (('speak', 'speak', 4),
      ('glower', 'glower', 4),
      ('lose3', 'wrecked', 4),
      ('phone', 'phone', 4))
tm = (('speak', 'speak', 4),
      ('throw-paper', 'throw-paper', 4),
      ('throw-object', 'throw-object', 4),
      ('pickpocket', 'pickpocket', 4),
      ('phone', 'phone', 4),
      ('lose3', 'wrecked', 4),
      ('roll-o-dex', 'roll-o-dex', 4),
      ('finger-wag', 'finger-wag', 4))
nd = (('speak', 'speak', 4),
      ('magic3', 'magic3', 4),
      ('phone', 'phone', 4),
      ('lose3', 'wrecked', 4))
gh = (('smile', 'smile', 4),
      ('lose3', 'wrecked', 4),
      ('magic3', 'magic3', 4),
      ('roll-o-dex', 'roll-o-dex', 4))
ms = (('lose3', 'wrecked', 4),
      ('phone', 'phone', 4),
      ('glower', 'glower', 4),
      ('magic1', 'magic1', 4),
      ('magic3', 'magic3', 4))
tf = (('speak', 'speak', 4),
      ('pen-squirt', 'fountain-pen', 4),
      ('lose3', 'wrecked', 4),
      ('rubber-stamp', 'rubber-stamp', 4))
m = (('stomp', 'stomp', 4),
     ('quick-jump', 'jump', 4),
     ('smile', 'smile', 4),
     ('phone', 'phone', 4),
     ('glower', 'glower', 4))
mh = (('effort', 'effort', 4),
      ('lose3', 'wrecked', 4),
      ('stomp', 'stomp', 4),
      ('quick-jump', 'jump', 4))
ka = (('speak', 'speak', 4),
      ('song-and-dance', 'song-and-dance', 4),
      ('lose3', 'wrecked', 4),
      ('golf-club-swing', 'golf-club-swing', 4),
      ('smile', 'smile', 4))
mka = (('phone', 'phone', 4),
       ('smile', 'smile', 4),
       ('throw-object', 'throw-object', 4),
       ('magic3', 'magic3', 4),
       ('lose3', 'wrecked', 4),
       ('glower', 'glower', 4))
trm = (('speak', 'speak', 4),
       ('magic2', 'magic2', 4),
('smile', 'smile', 4),
('magic3', 'magic3', 4),
       ('lose3', 'wrecked', 4),
       ('golf-club-swing', 'golf-club-swing', 4))
ssm = (('speak', 'speak', 4),
       ('magic2', 'magic2', 4),
       ('lose3', 'wrecked', 4),
       ('golf-club-swing', 'golf-club-swing', 4))
isw = (('speak', 'speak', 4),
       ('smile', 'smile', 4),
       ('phone', 'phone', 4),
       ('pickpocket', 'pickpocket', 4),
       ('glower', 'glower', 4),
       ('effort', 'effort', 4),
       ('lose3', 'wrecked', 4),
       ('magic1', 'magic1', 4))
ssr = (('smile', 'smile', 4),
       ('speak', 'speak', 4),
       ('lose3', 'wrecked', 4),
       ('golf-club-swing', 'golf-club-swing', 4),
       ('song-and-dance', 'song-and-dance', 4))
fas = (('magic2', 'magic2', 4),
       ('pickpocket', 'sanction', 4),
       ('cease2', 'sanction', 4),
       ('lose3', 'wrecked', 4),
       ('cigar-smoke', 'cigar-smoke', 4))
mdr = (('throw-paper', 'throw-paper', 4),
       ('magic2', 'magic2', 4),
       ('magic1', 'magic1', 4),
       ('lose3', 'wrecked', 4),
('rolled', 'rolled', 4),
       ('frustrated', 'frustrated', 4),
       ('magic3', 'magic3', 4),
       ('speak', 'speak', 4))
nar = (('throw-paper', 'throw-paper', 4),
       ('magic2', 'magic2', 4),
       ('effort', 'effort', 4),
       ('magic1', 'magic1', 4),
       ('glower', 'glower', 4),
       ('magic3', 'magic2', 4),
       ('speak', 'speak', 4))
fd = (('glower', 'glower', 4),
      ('speak', 'speak', 4),
      ('frustrated', 'effort', 4),
      ('speak', 'speak', 4),
      ('calculating-costs', 'phone', 4),
      ('cease', 'mob-mentality', 4),
      ('lose3', 'wrecked', 4),
      ('short-squeeze', 'short-squeeze', 4),
      ('summon', 'glower', 4),
      ('magic3', 'magic2', 4),
      ('effort', 'effort', 4),
      ('magic1', 'magic1', 4))
fm = (('quick-jump', 'jump', 4),
      ('phone', 'phone', 4),
      ('lose3', 'wrecked', 4),
      ('roll-o-dex', 'roll-o-dex', 4))
th = (('magic1', 'magic1', 4), #Rainmaker
        ('effort', 'effort', 4),
        ('glower', 'glower', 4),
('cease', 'objection', 4),
        ('magic3', 'magic3', 4),
      ('lose3', 'wrecked', 4),
        ('glower', 'glower', 4))
whunter = (('mob-mentality', 'mob-mentality', 4), #Witch Hunter
           ('sanction', 'sanction', 4),
           ('speak', 'speak', 4),
           ('lose3', 'wrecked', 4),
           ('throw-object', 'throw-object', 4),
           ('throw-paper', 'throw-paper', 4),
           ('magic1', 'magic1', 4))
tr = (('snap', 'mob-mentality', 4), #Count Erclaim
        ('pickpocket', 'defense', 4),
        ('throw-object', 'throw-object', 4),
('effort', 'effort', 4),
        ('throw-paper', 'throw-paper', 4),
      ('lose3', 'wrecked', 4),
      ('quick-jump', 'jump', 4),
        ('magic1', 'magic1', 4))
prr = (('song-and-dance', 'song-and-dance', 4),
       ('glower', 'glower', 4),
('highroller-neutral-levitate-loop', 'highroller-neutral-levitate-loop', 4),
('highroller-neutral-levitate-in-out', 'highroller-neutral-levitate-in-out', 4),
       ('calculating-costs', 'calculating-costs', 4),
       ('lose3', 'wrecked', 4),
       ('speak', 'speak', 4),
('snap', 'snap', 4),
('sanction', 'sanction', 4),
('effort', 'effort', 4),
       ('cease2', 'sanction', 4),
       ('falling-knife', 'falling-knife', 4),
       ('cease', 'cease', 4),
       ('frustrated', 'frustrated', 4),
       ('magic3', 'magic3', 4),
       ('neutral', 'rolled', 4))
blr = (('defense', 'defense', 4),
       ('lose3', 'wrecked', 4),
       ('calculating-costs', 'calculating-costs', 4),
       ('speak', 'speak', 4),
       ('sanction', 'sanction', 4),
       ('cease', 'cease', 4),
('golf-club-swing', 'golf-club-swing', 4),
       ('pickpocket', 'pickpocket', 4),
('summon', 'summon', 4),
       ('frustrated', 'frustrated', 4),
       ('smile', 'smile', 4),
       ('song-and-dance', 'song-and-dance', 4),
       ('roll-o-dex', 'roll-o-dex', 4),
       ('snap', 'snap', 4),
       ('glower', 'glower', 4),
       ('magic3', 'magic3', 4))
dvp = (('magic3', 'magic3', 4),
       ('magic2', 'magic2', 4),
('short-squeeze', 'short-squeeze', 4),
       ('magic1', 'magic1', 4),
       ('effort', 'effort', 4),
       ('transformation', 'transformation', 4),
       ('objection', 'objection', 4),
       ('frustrated', 'frustrated', 4),
       ('lose3', 'wrecked', 4),
       ('glower', 'glower', 4),
       ('speak', 'speak', 4))
dsk = (('objection-in', 'cease', 4),
       ('magic3', 'magic3', 4),
       ('snap', 'snap', 4),
       ('glower', 'glower', 4),
('summon', 'summon', 4),
       ('lose3', 'wrecked', 4),
('falling-knife', 'falling-knife', 4),
       ('deadwood', 'deadwood', 4),
       ('effort', 'effort', 4),
       ('speak', 'speak', 4),
       ('calculating-costs', 'calculating-costs', 4),
       ('cease', 'cease', 4),
       ('frustrated', 'frustrated', 4),
       ('quick-jump', 'jump', 4),
       ('snap', 'snap', 4),
('sanction', 'sanction', 4),
       ('magic1', 'magic1', 4),
       ('magic2', 'magic2', 4))
ffm = (('cigar-smoke', 'cigar-smoke', 4),
       ('frustrated', 'frustrated', 4),
       ('magic2', 'magic2', 4),
       ('golf-club-swing', 'golf-club-swing', 4),
       ('magic3', 'magic3', 4),
       ('finger-wag', 'finger-wag', 4),
('magic3-alt', 'magic3-alt', 4),
       ('firestarter-cigar-smoke', 'firestarter-cigar-smoke', 4),
       ('snap', 'snap', 4),
       ('pickpocket', 'pickpocket', 4),
       ('summon', 'summon', 4),
('falling-knife', 'falling-knife', 4),
       ('speak', 'speak', 4),
       ('lose3', 'wrecked', 4),
       ('magic1', 'magic1', 4),
('revvedup', 'revvedup', 4),
       ('cease', 'cease2', 4),
       ('glower', 'glower', 4)
       )
sft = (('quick-jump', 'jump', 4),
       ('magic1', 'magic1', 4),
       ('speak', 'speak', 4),
       ('magic3', 'magic3', 4),
       ('lose3', 'wrecked', 4),
       ('smile', 'smile', 4),
       ('neutral', 'pace', 4))
sc = (('throw-paper', 'throw-paper', 4),
      ('lose3', 'wrecked', 4),
      ('watercooler', 'watercooler', 4),
      ('pickpocket', 'pickpocket', 4))
pp = (('throw-paper', 'throw-paper', 4),
      ('lose3', 'wrecked', 4),
      ('glower', 'glower', 4),
      ('finger-wag', 'finger-wag', 4))
tw = (('throw-paper', 'throw-paper', 4),
      ('lose3', 'wrecked', 4),
      ('magic3', 'magic3', 4),
      ('throw-object', 'throw-object', 4),
      ('magic1', 'magic1', 4),
      ('speak', 'speak', 4))
bc = (('throw-paper', 'throw-paper', 4),
      ('lose3', 'wrecked', 4),
      ('glower', 'glower', 4),
      ('magic2', 'magic2', 4),
      ('finger-wag', 'finger-wag', 4))
nc = (('phone', 'phone', 4),
      ('lose3', 'wrecked', 4),
      ('magic3', 'magic3', 4),
      ('pickpocket', 'pickpocket', 4))
mb = (('phone', 'phone', 4),
      ('hold-pencil', 'hold-pencil', 4),
      ('lose3', 'wrecked', 4),
      ('pickpocket', 'pickpocket', 4))
ls = (('phone', 'phone', 4),
      ('speak', 'speak', 4),
('finger-wag', 'finger-wag', 4),
      ('smile', 'smile', 4),
('magic1', 'magic1', 4),
      ('lose3', 'wrecked', 4),
      ('glower', 'glower', 4))
rb = (('phone', 'phone', 4),
      ('lose3', 'wrecked', 4),
      ('throw-object', 'throw-object', 4))
gm = (('speak', 'speak', 4),
       ('smile', 'smile', 4),
       ('phone', 'phone', 4),
       ('pickpocket', 'pickpocket', 4),
       ('glower', 'glower', 4),
       ('effort', 'effort', 4),
      ('magic2', 'magic2', 4),
       ('lose3', 'wrecked', 4),
       ('magic1', 'magic1', 4))
ad = (('magic1', 'magic1', 4),
      ('glower', 'glower', 4),
      ('lose3', 'wrecked', 4),
      ('effort', 'effort', 4),
      ('throw-paper', 'throw-paper', 4),
      ('throw-object', 'throw-object', 4))
cvy = (('magic1', 'magic1', 4),
       ('lose3', 'wrecked', 4),
       ('magic2', 'magic2', 4),
       ('pickpocket', 'pickpocket', 4),
       ('throw-paper', 'throw-paper', 4))
ptr = (('lose3', 'wrecked', 4),
       ('throw-paper', 'throw-paper', 4),
       ('throw-object', 'throw-object', 4),
       ('hold-pencil', 'hold-pencil', 4))
mld = (('watercooler', 'watercooler', 4),
       ('magic1', 'magic1', 4),
       ('lose3', 'wrecked', 4),
       ('pickpocket', 'pickpocket', 4),
       ('throw-paper', 'throw-paper', 4))
pht = (('cigar-smoke', 'cigar-smoke', 4),
       ('lose3', 'wrecked', 4),
       ('magic3', 'magic3', 4),
       ('pickpocket', 'pickpocket', 4),
       ('golf-club-swing', 'golf-club-swing', 4))
csh = (('magic3', 'magic3', 4),
       ('calculating-costs', 'calculating-costs', 4),
       ('lose3', 'wrecked', 4),
       ('magic2', 'magic2', 4),
       ('phone', 'phone', 4),
       ('victory', 'victory', 4),
       ('magic1', 'magic1', 4),
       ('sanction', 'sanction', 4),
       ('pickpocket', 'sanction', 4))
bgr = (('magic1', 'magic1', 4),
('magic2', 'magic2', 4),
('glower', 'glower', 4),
('calculating-costs', 'calculator', 4),
('magic3', 'magic2', 4),
       ('lose3', 'wrecked', 4))
mes = (('magic3', 'magic2', 4),
       ('magic1', 'magic1', 4),
       ('short-squeeze', 'short-squeeze', 4),
       ('phone', 'phone', 4),
       ('lose3', 'wrecked', 4),)
dm = (('effort', 'wheelspin', 4),
      ('sanction', 'sanction', 4),
      ('magic3', 'magic3', 4),
      ('lose3', 'wrecked', 4),
      ('finger-wag', 'cease2', 4),
      ('magic2', 'snap', 4),
      ('magic1', 'magic3', 5),
      ('pickpocket', 'sanction', 4))
tcc = (('mob-mentality', 'mob-mentality', 4),
       ('magic3', 'magic2', 4),
       ('lose3', 'wrecked', 4),
       ('magic2', 'magic2', 4),
       ('watercooler', 'watercooler', 4),
       ('magic1', 'magic1', 4),
       ('glower', 'glower', 4))
fb = (('throw-paper', 'throw-paper', 4),
      ('defense', 'defense', 4),
      ('lose3', 'wrecked', 4),
      ('hold-eraser', 'hold-eraser', 4),
      ('throw-object', 'throw-object', 4),
      ('mob-mentality', 'mob-mentality', 4),
      ('magic1', 'magic1', 4))
jl = (('throw-paper', 'throw-paper', 4),
      ('throw-object', 'throw-paper', 4),
      ('magic3', 'magic2', 4),
      ('lose3', 'wrecked', 4),
      ('mob-mentality', 'mob-mentality', 4),
      ('magic1', 'magic1', 4))
gb = (('magic1', 'rake', 4),
      ('mob-mentality', 'mob-mentality', 4),
      ('throw-object', 'throw-object', 4),
      ('pickpocket', 'pickpocket', 4),
      ('lose3', 'wrecked', 4),
      ('magic2', 'magic2', 4),
      ('magic3', 'magic3', 4),
      ('defense', 'scabbard', 4),
      ('sanction', 'sanction', 4),
      ('throw-paper', 'throw-paper', 4))
lbs = (('throw-paper', 'throw-paper', 4),
       ('throw-object', 'throw-object', 4),
       ('magic1', 'magic1', 4),
       ('lose3', 'wrecked', 4),
       ('defense', 'scabbard', 4),
       ('mob-mentality', 'mob-mentality', 4),
       ('quick-jump', 'jump', 4),
       ('glower', 'glower', 4),
       ('sanction', 'sanction', 4),
       ('pickpocket', 'sanction', 4))
trk = (('magic1', 'magic1', 4),
       ('effort', 'effort', 4),
       ('pickpocket', 'pickpocket', 4),
       ('lose3', 'wrecked', 4),
       ('glower', 'glower', 4),
       ('mob-mentality', 'mob-mentality', 4),
       ('throw-object', 'throw-paper', 4),
       ('magic3', 'magic2', 4),
       ('throw-paper', 'throw-paper', 4),
       ('cigar-smoke', 'plutocrat-cigar-smoke', 4))
dsf = (('magic3', 'magic3', 4),
       ('effort', 'scabbard', 4),
       ('magic1', 'magic1', 4),
       ('glower', 'glower', 4),
('scabbard', 'scabbard', 4),
('highroller-neutral-levitate-loop', 'highroller-neutral-levitate-loop', 4),
('highroller-neutral-levitate-in-out', 'highroller-neutral-levitate-in-out', 4),
('wheelspin', 'wheelspin', 4),
('bust', 'bust', 4),
       ('speak', 'speak', 4),
       ('lose3', 'wrecked', 4),
       ('calculating-costs', 'calculating-costs', 4),
       ('objection-in', 'cease', 4),
       ('cease', 'cease', 4),
('snap', 'snap', 4),
       ('falling-knife', 'falling-knife', 4),
       ('pickpocket', 'pickpocket', 4),
       ('song-and-dance', 'song-and-dance', 4),
       ('frustrated', 'frustrated', 4),
       ('walk', 'awalk', 4),
       ('revvedup', 'revvedup', 4))
msp = (('magic3', 'magic3', 4),
       ('mob-mentality', 'mob-mentality', 4),
       ('throw-paper', 'throw-paper', 4),
       ('throw-object', 'throw-object', 4),
('quick-jump', 'jump', 4),
('cease', 'cease', 4),
('glower', 'glower', 4),
('defense', 'defense', 4),
('pickpocket', 'sanction', 4),
       ('finger-wag', 'finger-wag', 4))
mad = (('magic1', 'magic1', 4),
       ('glower', 'glower', 4),
('highroller-neutral-levitate-loop', 'highroller-neutral-levitate-loop', 4),
('highroller-neutral-levitate-in-out', 'highroller-neutral-levitate-in-out', 4),
       ('sanction', 'sanction', 4),
       ('lose3', 'wrecked', 4),
('snap', 'snap', 4),
('shot5', 'shot5', 4),
       ('defense', 'defense', 4),
('phone', 'phone', 4),
       ('neutral', 'rolled', 4),
       ('neutral-hurt', 'rolled', 4))
crf = (('effort', 'wheelspin', 4),
       ('wheelspin', 'wheelspin', 4),
       ('cease', 'cease', 4),
('bust', 'bust', 4),
       ('magic3', 'magic3', 4),
       ('frustrated', 'frustrated', 4),
       ('highroller-neutral-levitate-loop', 'highroller-neutral-levitate-loop', 4),
('highroller-neutral-levitate-in-out', 'highroller-neutral-levitate-in-out', 4),
       ('lose3', 'wrecked', 4),
       ('cease', 'cease', 4),
       ('snap', 'snap', 4),
       ('speak', 'speak', 4),
       ('song-and-dance', 'song-and-dance', 4),
       ('finger-wag', 'cease', 4),
       ('magic1', 'magic1', 4),
       ('neutral', 'rolled', 4),
       ('neutral-hurt', 'rolled', 4))
bf = (('shredder', 'shredder', 4),
      ('lose3', 'wrecked', 4),
      ('phone', 'phone', 4))
b = (('magic1', 'magic1', 4),
     ('throw-paper', 'throw-paper', 4),
     ('throw-object', 'throw-object', 4),
     ('lose3', 'wrecked', 4),
     ('pickpocket', 'pickpocket', 4))
dt = (('speak', 'speak', 4),
      ('throw-object', 'throw-object', 4),
      ('lose3', 'wrecked', 4),
      ('hold-pencil', 'hold-pencil', 4),
      ('finger-wag', 'finger-wag', 4))
ac = (('rubber-stamp', 'rubber-stamp', 4),
      ('lose3', 'wrecked', 4),
      ('throw-paper', 'throw-paper', 4),
      ('speak', 'speak', 4),
      ('roll-o-dex', 'roll-o-dex', 4))
bs = (('throw-paper', 'throw-paper', 4),
      ('speak', 'speak', 4),
      ('lose3', 'wrecked', 4),
      ('roll-o-dex', 'roll-o-dex', 4))
sd = (('magic2', 'magic2', 4),
      ('quick-jump', 'jump', 4),
      ('lose3', 'wrecked', 4),
      ('magic3', 'magic3', 4),
      ('hold-pencil', 'hold-pencil', 4))
le = (('pen-squirt', 'fountain-pen', 4),
      ('rubber-stamp', 'rubber-stamp', 4),
      ('lose3', 'wrecked', 4),
      ('phone', 'phone', 4),
      ('speak', 'speak', 4))
bw = (('magic1', 'magic1', 4),
      ('throw-paper', 'throw-paper', 4),
      ('throw-object', 'throw-object', 4),
      ('effort', 'effort', 4),
      ('pickpocket', 'pickpocket', 4),
      ('lose3', 'wrecked', 4),
      ('finger-wag', 'finger-wag', 4))
brv = (('shredder', 'shredder', 4),
       ('magic1', 'magic1', 4),
       ('watercooler', 'watercooler', 4),
       ('lose3', 'wrecked', 4),
       ('glower', 'glower', 4))
sb = (('magic2', 'magic2', 4),
      ('quick-jump', 'jump', 4),
      ('magic3', 'magic3', 4),
      ('lose3', 'wrecked', 4),
      ('hold-pencil', 'hold-pencil', 4))
cfp = (('magic1', 'magic1', 4),
       ('throw-paper', 'throw-paper', 4),
       ('lose3', 'wrecked', 4),
       ('hold-eraser', 'hold-eraser', 4))
arb = (('speak', 'speak', 4),
       ('throw-object', 'throw-object', 4),
       ('lose3', 'wrecked', 4),
       ('glower', 'glower', 4))
sjg = (('quick-jump', 'jump', 4),
       ('throw-paper', 'throw-paper', 4),
       ('lose3', 'wrecked', 4),
       ('throw-object', 'throw-object', 4),
       ('glower', 'glower', 4))
lsc = (('finger-wag', 'fingerwag', 4),
       ('cigar-smoke', 'cigar-smoke', 4),
       ('lose3', 'wrecked', 4),
       ('magic1', 'magic1', 4),
       ('throw-object', 'throw-object', 4))
jdg = (('magic3', 'magic3', 4),
('magic1', 'magic1', 4),
       ('lose3', 'wrecked', 4),
       ('phone', 'phone', 4),
       ('cease', 'cease', 4),
       ('calculating-costs', 'calculating-costs', 4),
       ('sanction', 'sanction', 4),
       ('speak', 'speak', 4))
jur = (('magic2', 'magic2', 4),
       ('objection-in', 'objection-in', 4),
       ('lose3', 'wrecked', 4),
       ('objection-out', 'objection-out', 4),
       ('quick-jump', 'jump', 4),
('pace', 'pace', 4),
       ('magic3', 'magic3', 4),
       ('throw-object', 'throw-object', 5),
       ('throw-paper', 'throw-paper', 5),
       ('magic1', 'magic1', 4))
tlr = (('magic2', 'snap', 4),
('quick-jump', 'jump', 4),
      ('sanction', 'sanction3', 4),
      ('snap', 'snap2', 4),
      ('magic3', 'magic3', 4),
      ('speak', 'speak', 4),
      ('cease', 'cease3', 4),
      ('magic1', 'magic1', 4),
      ('calculating-costs', 'calculating-costs', 4),
      ('throw-object', 'throw-object', 4),
      ('throw-paper', 'throw-paper', 4))
cm = (('speak', 'speak', 4),
       ('phone', 'phone', 4),
      ('effort', 'effort', 4),
       ('magic1', 'magic1', 4),
      ('pen-squirt', 'fountain-pen', 4))
ggm = (('magic2', 'snap', 4),
       ('calculating-costs', 'phone', 4),
       ('cease', 'objection', 4), ('lose3', 'wrecked', 4),
       ('magic3', 'magic3', 4),
       ('roll-o-dex', 'roll-o-dex', 4),
('finger-wag', 'finger-wag', 4),
       ('throw-object', 'throw-object', 5),
       ('throw-paper', 'throw-paper', 5),
       ('magic1', 'magic1', 4))
jb = (('smile', 'smile', 4), #Mr. Hollywood (MP)
       ('speak', 'speak', 4),
('glower', 'glower', 4),
       ('lose3', 'wrecked', 4),
       ('golf-club-swing', 'golf-club-swing', 4),
       ('song-and-dance', 'song-and-dance', 4),
      ('neutral', 'rolled', 4))
prethink = (('pickpocket', 'rushjob', 4), #Prethinker
            ('sanction', 'rushjob', 4),
            ('effort', 'effort', 4),
            ('lose3', 'wrecked', 4),
            ('magic3', 'magic3', 4),
            ('magic2', 'magic2', 4),
            ('speak', 'speak', 4))
jr = (('throw-paper', 'throw-paper', 4), # Multislacker
      ('magic1', 'magic1', 4),
('magic2', 'magic2', 4),
      ('defense', 'scabbard', 4),
      ('magic3', 'magic3', 4), ('lose3', 'wrecked', 4),
      ('glower', 'glower', 4),
      ('sanction', 'sanction', 4),
      ('pickpocket', 'sanction', 4),
      ('song-and-dance', 'song-and-dance', 4))
mp = (('hold-pencil', 'hold-pencil', 4),
     ('magic1', 'magic1', 4),
     ('lose3', 'wrecked', 4),
('effort', 'effort', 4),
      ('stomp', 'stomp', 4),
      ('glower', 'glower', 4),
('pickpocket', 'defense', 4),
('cease', 'objection', 4),
     ('speak', 'speak', 4),
     ('magic1', 'magic1', 4))
laa = (('glower', 'glower', 4),
       ('sanction', 'sanction', 4),
('pickpocket', 'pickpocket', 4),
       ('effort', 'effort', 4),
       ('speak', 'speak', 4),
       ('quick-jump', 'jump', 4),
       ('golf-club-swing', 'golf-club-swing', 4),
       ('falling-knife', 'falling-knife', 4),
       ('throw-object', 'throw-object', 4),
       ('finger-wag', 'finger-wag', 4),
       ('throw-paper', 'throw-paper', 4),
       ('cease2', 'cease2', 4),
       ('magic2', 'magic2', 4),
('magic3', 'magic3', 4),
       ('cease', 'cease', 4),
       ('magic1', 'magic1', 4))
scg = (('stomp', 'stomp', 4),
('jump', 'stomp', 4),
       ('rage', 'rage', 4),
('glower', 'glower', 4),
       ('throw-object', 'throw-object', 4),
       ('throw-paper', 'throw-paper', 4),
       ('finger-wag', 'finger-wag', 4),
       ('frustrated', 'defense', 4),
('quick-jump', 'jump', 4),
       ('magic1', 'magic1', 4),
       ('lose3', 'wrecked', 4),
       ('neutral-enraged', 'neutral-enraged', 5),
       ('speak', 'speak', 4),
       ('effort', 'effort', 4),
       ('magic2', 'magic2', 4),
       ('cease', 'objection', 4),
       ('defense', 'defense', 4),
       ('glower', 'glower', 4))
csm = (('throw-object', 'throw-object', 4),
       ('throw-paper', 'throw-paper', 4),
       ('effort', 'effort', 4),
       ('lose3', 'wrecked', 4),
       ('cease', 'cease', 4),
('pickpocket', 'sanction', 4),
       ('frustrated', 'frustrated', 4),
       ('objection-in', 'cease', 4),
       ('falling-knife', 'throw-insurance', 4),
       ('throw-insurance', 'throw-insurance', 4),
       ('speak', 'speak', 4),
       ('roll-o-dex', 'roll-o-dex', 4),
       ('sanction', 'sanction', 4),
       ('pen-squirt', 'fountain-pen', 4),
       ('magic1', 'magic1', 4))
ste = (('magic3', 'magic3', 4),
       ('cease2', 'cease3', 4),
       ('phone', 'phone', 4),
       ('frustrated', 'frustrated-f', 4),
       ('speak', 'speak', 4),
       ('calculating-costs', 'calculating-costs', 4),
       ('cease', 'cease3', 4),
       ('finger-wag', 'cease3', 4),
       ('pickpocket', 'sanction', 4),
       ('lose3', 'wrecked', 4),
       ('sanction', 'sanction3', 4))
lit = (('magic2', 'magic2', 4),
       ('bellow', 'bellow', 4),
       ('speak', 'speak', 4),
       ('glower', 'glower', 4),
       ('summon', 'summon', 4),
       ('frustrated', 'frustrated', 4),
       ('cease', 'cease', 4),
       ('magic1', 'magic1', 4),
       ('lose3', 'wrecked', 4),
       ('snap2', 'snap2', 4),
       ('snap', 'snap', 4),
       ('throw-object', 'throw-object', 4),
       ('throw-paper', 'throw-paper', 4))
ca = (('pickpocket', 'pickpocket', 4),
      ('speak', 'speak', 4),
      ('lose3', 'wrecked', 4),
      ('rubber-stamp', 'rubber-stamp', 4),
      ('throw-paper', 'throw-paper', 4),
      ('throw-object', 'throw-object', 4),
      ('short-squeeze', 'short-squeeze', 4),
      ('pen-squirt', 'fountain-pen', 4))
cn = (('speak', 'speak', 4),
      ('throw-paper', 'throw-paper', 4),
      ('lose3', 'wrecked', 4),
      ('effort', 'effort', 4),
      ('pen-squirt', 'pen-squirt', 4),
      ('hold-pencil', 'hold-pencil', 4),
      ('roll-o-dex', 'roll-o-dex', 4),
      ('short-squeeze', 'short-squeeze', 4),
      ('finger-wag', 'finger-wag', 4))
sw = (('pickpocket', 'pickpocket', 4),
      ('speak', 'speak', 4),
      ('lose3', 'wrecked', 4),
      ('throw-paper', 'throw-paper', 4),
      ('pen-squirt', 'fountain-pen', 4))
mdm = (('pickpocket', 'pickpocket', 4),
       ('phone', 'phone', 4),
       ('lose3', 'wrecked', 4),
       ('magic1', 'magic1', 4))
txm = (('magic3', 'magic3', 4),
       ('glower', 'glower', 4),
       ('throw-paper', 'throw-paper', 4),
       ('lose3', 'wrecked', 4),
       ('roll-o-dex', 'roll-o-dex', 4))
mg = (('quick-jump', 'jump', 4),
      ('effort', 'effort', 4),
      ('lose3', 'wrecked', 4),
      ('glower', 'glower', 5),
      ('magic1', 'magic1', 4))
bfh =  (('pen-squirt', 'fountain-pen', 4),
        ('glower', 'glower', 4),
        ('lose3', 'wrecked', 4),
        ('magic1', 'magic1', 4))
hho = (('glower', 'glower', 4),
       ('lose3', 'wrecked', 4),
       ('throw-paper', 'throw-paper', 4),
       ('throw-object', 'throw-object', 4),
       ('magic1', 'magic1', 4),
       ('short-squeeze', 'short-squeeze', 4))
bdb = (('glower', 'glower', 4),
       ('phone', 'phone', 5),
       ('magic3', 'magic3', 4),
('speak', 'speak', 4),
('magic2', 'magic2', 4),
('smile', 'smile', 4),
       ('magic1', 'magic1', 4))
bgh = (('lose3', 'wrecked', 4),
       ('throw-object', 'throw-object', 4),
       ('throw-paper', 'throw-paper', 4),
       ('magic1', 'magic1', 4),
       ('watercooler', 'watercooler', 4),
       ('glower', 'glower', 4))
dfh = (('magic1', 'magic1', 4),
       ('lose3', 'wrecked', 4),
       ('throw-paper', 'throw-paper', 4),
       ('watercooler', 'watercooler', 4))
rng = (('magic2', 'magic2', 4),
       ('lose3', 'wrecked', 4),
       ('golf-club-swing', 'golf-club-swing', 4),
       ('phone', 'phone', 5),
       ('throw-object', 'throw-object', 4),)
cps = (('cigar-smoke', 'cigar-smoke', 4),
       ('magic1', 'magic1', 4),
       ('lose3', 'wrecked', 4),
       ('magic2', 'magic2', 4))
tld = (('headhoncho-cigar-smoke', 'headhoncho-cigar-smoke', 4),
       ('throw-object', 'throw-object', 4),
       ('magic1', 'magic1', 4),
('cigar-smoke', 'cigar-smoke', 4),
       ('lose3', 'wrecked', 4),
       ('magic2', 'magic2', 4))
gkp = (('pen-squirt', 'fountain-pen', 4),
       ('throw-object', 'throw-object', 4),
       ('throw-paper', 'throw-paper', 4),
       ('calculating-costs', 'calculating-costs', 4),
       ('cease', 'cease', 4),
       ('magic1', 'magic1', 4),
       ('magic3', 'magic3', 4),
       ('lose3', 'wrecked', 4),
       ('glower', 'glower', 4))
ddv = (('pen-squirt', 'fountain-pen', 4),
       ('throw-object', 'throw-object', 4),
       ('lose3', 'wrecked', 4),
       ('throw-paper', 'throw-paper', 4),
       ('magic1', 'magic1', 4),
       ('calculating-costs', 'calculating-costs', 4),
       ('cease', 'cease', 4),
       ('quick-jump', 'jump', 4),
       ('cigar-smoke', 'cigar-smoke', 4),
       ('magic3', 'magic3', 4),
       ('glower', 'glower', 4))
dty = (('pen-squirt', 'fountain-pen', 4),
       ('watercooler', 'watercooler', 4),
       ('lose3', 'wrecked', 4),
       ('throw-paper', 'throw-paper', 4),
       ('calculating-costs', 'calculating-costs', 4),
       ('cease', 'cease', 4),
       ('magic1', 'magic1', 4),
       ('quick-jump', 'jump', 4),
       ('cigar-smoke', 'cigar-smoke', 4),
       ('magic3', 'magic3', 4),
       ('glower', 'glower', 4))
dfg = (('magic2', 'snap', 4),
      ('bellow', 'bellow', 4), ('lose3', 'wrecked', 4),
      ('glower', 'glower', 4),
      ('magic1', 'magic1', 4),
      ('magic3', 'snap', 4),
      ('throw-object', 'throw-object', 4),
      ('throw-paper', 'throw-paper', 4))
dfr = (('stomp', 'rage', 4),
       ('throw-object', 'throw-object', 4),
       ('throw-paper', 'throw-paper', 4),
       ('neutral-enraged', 'neutral-enraged', 4),
       ('enraged', 'enraged', 4),
       ('magic1', 'magic1', 4), ('lose3', 'wrecked', 4),
       ('defense', 'defense', 4),
       ('glower', 'glower', 4))
bsh = (('lose3', 'wrecked', 4),
       ('quick-jump', 'jump', 4),
       ('summon', 'summon', 4),
       ('frustrated', 'frustrated', 4),
       ('calculating-costs', 'calculating-costs', 4),
       ('speak', 'speak', 4),
       ('cease', 'cease', 4),
       ('objection-in', 'cease', 4),
('glower', 'glower', 4),
       ('sanction', 'sanction', 4),
       ('magic3', 'magic3', 4),
       ('throw-object', 'throw-object', 5),
       ('throw-paper', 'throw-paper', 5),
       ('magic1', 'magic1', 4))
ghd = (('pickpocket', 'pickpocket', 4),
       ('frustrated', 'rage', 4),
       ('rage', 'rage', 4),
       ('sanction', 'rushjob', 4),
       ('summon', 'effort', 4),
       ('phone', 'phone', 4),
       ('magic3', 'magic3', 4),
       ('calculating-costs', 'phone', 4),
       ('glower', 'glower', 4),
       ('defense', 'defense', 4),
       ('cease', 'objection-in', 4),
       ('objection-in', 'objection-in', 4),
       ('objection-out', 'objection-out', 4),
       ('lose3', 'wrecked', 4),
       ('quick-jump', 'jump', 4),
       ('speak', 'speak', 4))
tyh = (('pickpocket', 'pickpocket', 4),
       ('sanction', 'sanction', 4),
       ('phone', 'phone', 4),
       ('magic3', 'magic3', 4),
       ('frustrated', 'frustrated-f', 4),
       ('glower', 'glower', 4),
       ('calculating-costs', 'calculating-costs', 4),
       ('cease', 'cease3', 4),
       ('cease2', 'cease3', 4),
       ('objection-out', 'objection-out', 4),
       ('lose3', 'wrecked', 4),
       ('speak', 'speak', 4))
jgd = (('pickpocket', 'pickpocket', 4),
       ('sanction', 'sanction', 4),
       ('summon', 'summon', 4),
       ('frustrated', 'frustrated', 4),
       ('phone', 'phone', 4),
       ('magic3', 'magic3', 4),
       ('magic1', 'magic1', 4),
       ('glower', 'glower', 4),
       ('throw-object', 'throw-object', 4),
       ('throw-paper', 'throw-paper', 4),
       ('defense', 'defense', 4),
       ('cease', 'cease', 4),
       ('cease2', 'cease2', 4),
       ('objection-out', 'objection-out', 4), ('lose3', 'wrecked', 4),
       ('snap', 'snap', 4),
       ('quick-jump', 'jump', 4),
       ('speak', 'speak', 4))
bby = (('pickpocket', 'sanction2', 4),
       ('sanction', 'sanction', 4),
       ('falling-knife', 'falling-knife', 4),
       ('summon', 'summon', 4),
       ('effort', 'effort', 4),
       ('frustrated', 'frustrated', 4),
       ('phone', 'phone', 4),
       ('magic3', 'magic3', 4),
       ('magic2', 'magic2', 4),
       ('magic1', 'magic1', 4),
       ('cigar-smoke', 'cigar-smoke', 4),
       ('layoffs', 'layoffs', 4),
       ('glower', 'glower', 4),
       ('golf-club-swing', 'golf-club-swing', 4),
       ('throw-paper', 'throw-paper', 4),
       ('throw-object', 'throw-object', 4),
       ('defense', 'defense', 4),
       ('cease', 'cease', 4),
       ('cease2', 'cease2', 4),
       ('objection-out', 'objection-out', 4),
       ('lose3', 'wrecked', 4),
       ('snap', 'snap', 4),
       ('quick-jump', 'jump', 4),
       ('speak', 'speak', 4))
dvk = (('throw-object', 'throw-object', 4),
       ('throw-paper', 'throw-paper', 4),
       ('cease', 'cease', 4),
       ('finger-wag', 'cease', 4),
       ('magic3', 'magic3', 4),
       ('glower', 'glower', 4),
       ('speak', 'speak', 4))
otm = (('effort', 'effort', 4),
('pencil-sharpener', 'pencil-sharpener', 4),
     ('hold-eraser', 'hold-eraser', 4),
     ('hold-pencil', 'hold-pencil', 4),
('speak', 'speak', 4),
('roll-o-dex', 'roll-o-dex', 4),
('short-squeeze', 'short-squeeze', 4),
       ('phone', 'phone', 4),
       ('pace', 'pace', 4),
       ('cease', 'rushjob', 4),
       ('come-on', 'come-on', 4),
       ('throw-paper', 'throw-paper', 4))
cry = (('finger-wag', 'cease', 4),
       ('glower', 'glower', 4),
('roll-o-dex', 'roll-o-dex', 4),
       ('revvedup', 'revvedup', 4),
       ('scabbard', 'scabbard', 4),
       ('throttle', 'throttle', 4),
('cease', 'cease', 4),
       ('sparkplug', 'sparkplug', 4),
       ('quick-jump', 'jump', 4),
       ('snap', 'snap-override', 4),
       ('layoffs', 'layoffs', 4))
tcm = (('golf-club-swing', 'golf-club-swing', 4),
       ('falling-knife', 'falling-knife', 4),
       ('snap', 'snap', 4),
       ('effort', 'effort', 4),
('summon', 'summon', 4),
       ('layoffs', 'layoffs', 4),
       ('cease', 'cease', 4),
       ('glower', 'glower', 4))
skd = (('phone', 'phone', 4),
      ('speak', 'speak', 4),
      ('lose3', 'wrecked', 4),
      ('calculator', 'calculator', 4),
      ('shredder', 'shredder', 4))
cmk = (('pickpocket', 'pickpocket', 4),
      ('phone', 'phone', 4),
      ('lose3', 'wrecked', 4),
      ('calculator', 'calculator', 4),
      ('finger-wag', 'finger-wag', 4),
       ('magic1', 'magic1', 4))
phs = (('magic1', 'magic1', 4),
('magic2', 'magic2', 4),
      ('speak', 'speak', 4),
      ('lose3', 'wrecked', 4),
       ('calculator', 'calculator', 4),
      ('pen-squirt', 'fountain-pen', 4))
vpr = (('magic3', 'magic3', 4),
       ('pickpocket', 'pickpocket', 4),
       ('speak', 'speak', 4),
       ('lose3', 'wrecked', 4),
       ('magic1', 'magic1', 4))
kyl = (('magic2', 'magic2', 4),
       ('effort', 'effort', 4),
('finger-wag', 'finger-wag', 4),
       ('speak', 'speak', 4))
sdb = (('watercooler', 'watercooler', 4),
      ('effort', 'effort', 4),
      ('lose3', 'wrecked', 4),
('finger-wag', 'finger-wag', 4),
      ('glower', 'glower', 4),
      ('magic1', 'magic1', 4))
gry =  (('pen-squirt', 'fountain-pen', 4),
        ('glower', 'glower', 4),
('finger-wag', 'finger-wag', 4),
('sanction', 'sanction', 4),
        ('calculator', 'calculator', 4),
        ('lose3', 'wrecked', 4),
        ('magic1', 'magic1', 4))
kbc = (('glower', 'glower', 4),
        ('lose3', 'wrecked', 4),
       ('speak', 'speak', 4),
       ('calculator', 'calculator', 4),
        ('magic1', 'magic1', 4))
shp = (('speak', 'speak', 4),
       ('magic2', 'magic2', 4),
       ('speak', 'speak', 4),
       ('lose3', 'wrecked', 4))
sfs = (('lose3', 'wrecked', 4),
       ('magic1', 'magic1', 4),
       ('magic3', 'magic3', 4),
       ('watercooler', 'watercooler', 4),
       ('glower', 'glower', 4))
pyc = (('magic1', 'magic1', 4),
('magic2', 'magic2', 4),
       ('lose3', 'wrecked', 4),
('finger-wag', 'finger-wag', 4),
('magic3', 'magic3', 4),
       ('glower', 'glower', 4),
       ('smile', 'smile', 4))
inw = (('magic2', 'magic2', 4),
       ('lose3', 'wrecked', 4),
       ('speak', 'speak', 4),
('hold-eraser', 'hold-eraser', 4),
       ('calculator', 'calculator', 4),
       ('pickpocket', 'pickpocket', 4))
sys = (('cigar-smoke', 'cigar-smoke', 4),
       ('glower', 'glower', 4),
       ('speak', 'speak', 4),
       ('magic1', 'magic1', 4))
rus = (('glower', 'glower', 4),
       ('magic1', 'magic1', 4),
       ('lose3', 'wrecked', 4),
       ('speak', 'speak', 4))
ant = (('pen-squirt', 'fountain-pen', 4),
       ('throw-object', 'throw-object', 4),
       ('throw-paper', 'throw-paper', 4),
       ('magic1', 'magic1', 4),
       ('pickpocket', 'pickpocket', 4),
       ('calculator', 'calculator', 4),
       ('lose3', 'wrecked', 4),
       ('glower', 'glower', 4))
sya = (('frustrated', 'frustrated-f', 4),
       ('throw-object', 'throw-object', 4),
       ('throw-paper', 'throw-paper', 4),
('finger-wag', 'finger-wag', 4),
       ('magic1', 'magic1', 4),
('speak', 'speak', 4),
       ('pickpocket', 'pickpocket', 4),
       ('calculator', 'calculator', 4),
       ('sanction', 'sanction', 4),
       ('glower', 'glower', 4))
yuh = (('pen-squirt', 'fountain-pen', 4),
       ('throw-object', 'throw-object', 4),
('throw-paper', 'throw-paper', 4),
       ('lose3', 'wrecked', 4),
       ('throw-paper', 'throw-paper', 4),
       ('calculating-costs', 'calculating-costs', 4),
       ('shredder', 'shredder', 4),
       ('magic1', 'magic1', 4),
       ('quick-jump', 'jump', 4),
       ('cigar-smoke', 'cigar-smoke', 4),
       ('phone', 'phone', 4),
       ('glower', 'glower', 4))
yhi = (('magic2', 'snap', 4),
      ('bellow', 'bellow', 4), ('lose3', 'wrecked', 4),
      ('glower', 'glower', 4),
      ('magic1', 'magic1', 4),
      ('magic3', 'snap', 4),
      ('throw-object', 'throw-object', 4),
      ('throw-paper', 'throw-paper', 4))
jas = (('stomp', 'rage', 4),
       ('throw-object', 'throw-object', 4),
       ('throw-paper', 'throw-paper', 4),
       ('magic1', 'magic1', 4), ('lose3', 'wrecked', 4),
       ('defense', 'defense', 4),
       ('glower', 'glower', 4))
tas = (('lose3', 'wrecked', 4),
       ('quick-jump', 'jump', 4),
       ('summon', 'summon', 4),
       ('frustrated', 'frustrated', 4),
       ('calculating-costs', 'calculating-costs', 4),
       ('speak', 'speak', 4),
       ('cease', 'cease', 4),
       ('objection-in', 'cease', 4),
       ('cease2', 'sanction', 4),
       ('magic3', 'magic3', 4),
       ('throw-object', 'throw-object', 4),
       ('throw-paper', 'throw-paper', 4),
       ('magic1', 'magic1', 4))
fhu = (('pickpocket', 'pickpocket', 4),
       ('frustrated', 'rage', 4),
       ('rage', 'rage', 4),
       ('sanction', 'rushjob', 4),
       ('summon', 'effort', 4),
       ('phone', 'phone', 4),
       ('magic3', 'magic3', 4),
       ('calculating-costs', 'phone', 4),
       ('glower', 'glower', 4),
       ('defense', 'defense', 4),
       ('cease', 'objection-in', 4),
       ('objection-in', 'objection-in', 4),
       ('objection-out', 'objection-out', 4),
       ('lose3', 'wrecked', 4),
       ('quick-jump', 'jump', 4),
       ('speak', 'speak', 4))
fsh = (('pickpocket', 'pickpocket', 4),
       ('sanction', 'sanction', 4),
       ('phone', 'phone', 4),
       ('magic3', 'magic3', 4),
       ('frustrated', 'frustrated-f', 4),
       ('glower', 'glower', 4),
       ('calculating-costs', 'calculating-costs', 4),
       ('cease', 'cease3', 4),
       ('cease2', 'cease3', 4),
       ('objection-out', 'objection-out', 4),
       ('lose3', 'wrecked', 4),
       ('speak', 'speak', 4))
fhj = (('pickpocket', 'pickpocket', 4),
       ('sanction', 'sanction', 4),
       ('summon', 'summon', 4),
('magic3-alt', 'magic3-alt', 4),
       ('frustrated', 'frustrated', 4),
       ('phone', 'phone', 4),
('smile', 'smile', 4),
       ('finger-wag', 'finger-wag', 4),
       ('magic3', 'magic3', 4),
       ('cigar-smoke', 'cigar-smoke', 4),
('magic2', 'magic2', 4),
       ('glower', 'glower', 4),
       ('effort', 'effort', 4),
('magic1', 'magic1', 4),
       ('throw-object', 'throw-object', 4),
       ('throw-paper', 'throw-paper', 4),
       ('roll-o-dex', 'roll-o-dex', 4),
('golf-club-swing', 'golf-club-swing', 4),
       ('cease', 'cease', 4),
       ('cease2', 'cease2', 4),
       ('objection-out', 'objection-out', 4),
       ('lose3', 'wrecked', 4),
       ('snap', 'snap', 4),
       ('quick-jump', 'jump', 4),
       ('speak', 'speak', 4))
kdh = (('pickpocket', 'sanction2', 4),
       ('sanction', 'sanction', 4),
       ('falling-knife', 'blue-chip', 4),
       ('summon', 'summon', 4),
       ('effort', 'effort', 4),
       ('frustrated', 'frustrated', 4),
       ('phone', 'phone', 4),
       ('magic3', 'magic3', 4),
       ('magic2', 'magic2', 4),
       ('magic1', 'magic1', 4),
       ('cigar-smoke', 'cigar-smoke', 4),
       ('layoffs', 'layoffs', 4),
       ('glower', 'glower', 4),
       ('golf-club-swing', 'golf-club-swing', 4),
       ('throw-paper', 'throw-paper', 4),
       ('throw-object', 'throw-object', 4),
       ('defense', 'defense', 4),
       ('cease', 'cease', 4),
       ('cease2', 'cease2', 4),
       ('objection-out', 'objection-out', 4),
       ('lose3', 'wrecked', 4),
       ('snap', 'snap', 4),
       ('quick-jump', 'jump', 4),
       ('speak', 'speak', 4))
dar = (('glower', 'glower', 4),
       ('hold-eraser', 'hold-eraser', 4),
('defense', 'defense', 4),
('magic1', 'magic1', 4),
('magic3', 'magic3', 4),
('mob-mentality', 'mob-mentality', 4),
('falling-knife', 'blue-chip', 4),
('calculator', 'calculator', 4),
('sanction', 'objection', 4),
       ('speak', 'speak', 4))
nhy = (('glower', 'glower', 4),
       ('magic3', 'magic3', 4),
('speak', 'speak', 4),
('summon', 'summon', 4),
('magic1', 'magic1', 4),
('falling-knife', 'falling-knife', 4),
       ('cease', 'cease', 4))
wrt = (('magic3', 'magic3', 4),
       ('phone', 'phone', 4),
       ('calculating-costs', 'calculating-costs', 4),
('calculator', 'calculator', 4),
       ('finger-wag', 'cease3', 4),
       ('pickpocket', 'sanction', 4),
       ('magic1', 'magic1', 4),
       ('effort', 'effort', 4),
       ('snap', 'snap', 4),
       ('sanction', 'sanction', 4),
       ('summon', 'summon', 4),
       ('frustrated', 'frustrated-f', 4),
       ('sanction', 'sanction', 4),
       ('lose3', 'wrecked', 4),
       ('cease', 'cease3', 4),
       ('speak', 'speak', 4))
auh = (('magic3', 'magic3', 4),
       ('golf-club-swing', 'golf-club-swing', 4),
       ('falling-knife', 'falling-knife', 4),
('blue-chip', 'blue-chip', 4),
       ('pickpocket', 'sanction', 4),
       ('magic1', 'magic1', 4),
       ('snap', 'snap', 4),
       ('throw-paper', 'throw-paper', 4),
       ('throw-object', 'throw-object', 4),
('calculating-costs', 'calculating-costs', 4),
       ('throw-paper', 'throw-paper', 4),
('summon', 'summon', 4),
('magic3', 'magic3', 4),
       ('frustrated', 'frustrated', 4),
       ('layoffs', 'layoffs', 4),
       ('lose3', 'wrecked', 4),
       ('deadwood', 'deadwood', 4),
       ('throw-object', 'throw-object', 4),
       ('finger-wag', 'cease2', 4),
       ('cease', 'cease', 4),
       ('glower', 'glower', 4),
       ('sanction', 'sanction', 4),
       ('song-and-dance', 'song-and-dance', 4),
       ('cigar-smoke', 'cigar-smoke', 4),
('speak', 'speak', 4),
       ('sanction', 'sanction', 4))
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
                    Vec4(0.431, 0.431, 0.431, 1), #out
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
                    Vec4(0.431, 0.431, 0.431, 1), #out
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
     't': Vec4(0.847, 0.792, 0.851, 1.0)
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
        self.isExecutive = 0
        self.isAngry = 0
        self.isRevived = 0
        self.isLaserRevived = 0
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

        if dna.name == 'f':
            self.scale = 4.0 / cSize
            self.handColor = SuitDNA.corpPolyColor
            self.generateBody()
            #self.generateFlunky()
            self.generateHead('flunky')
            self.generateHead('glasses')
            self.setHeight(4.88)
        elif dna.name == 'p':
            self.scale = 3.35 / bSize
            self.handColor = SuitDNA.corpPolyColor
            self.generateBody()
            self.generateHead('pencilpusher')
            texture = loader.loadTexture('phase_3.5/maps/pencil_pusher.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.0)
        elif dna.name == 'ym':
            self.scale = 4.0 / cSize
            self.handColor = VBase4(0.702, 0.608, 0.255, 1)
            self.generateBody()
            self.generateHead2('gumshoe')
            texture = loader.loadTexture('phase_4/maps/gumshoe.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.7)
        elif dna.name == 'mm':
            self.scale = 4.125 / aSize
            self.handColor = VBase4(0.918, 0.886, 0.875, 1)
            self.generateBody()
            self.generateHead('yesman')
            texture = loader.loadTexture('phase_4/maps/yes_man.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.28)
        elif dna.name == 'ds':
            self.scale = 4.75 / aSize
            self.handColor = VBase4(0.749, 0.647, 0.518, 1)
            self.generateBody()
            self.generateHead('yesman')
            texture = loader.loadTexture('phase_4/maps/enforcer.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.23)
        elif dna.name == 'hh':
            self.scale = 2.5 / cSize
            self.handColor = SuitDNA.corpPolyColor
            self.generateFemaleBody()
            self.generateHead('micromanager')
            texture = loader.loadTexture('phase_3.5/maps/tutorial_suits_palette_3cmla_1.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(3.25)
        elif dna.name == 'cr':
            self.scale = 6.0 / cSize
            self.handColor = VBase4(0.878, 0.733, 0.71, 1)
            self.generateBody()
            self.generateHead2('Blowhard')
            texture = loader.loadTexture('phase_3.5/maps/ttrm_t_ene_head_blowhard.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.5)
        elif dna.name == 'tbc':
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
        elif dna.name == 'trb':
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
        elif dna.name == 'dot':
            self.scale = 6.5 / aSize
            self.handColor = SuitDNA.corpPolyColor
            self.generateBody()
            self.generateHead('headhunter')
            texture = loader.loadTexture('phase_3.5/maps/suit-heads_palette_3cmla_2.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.45)
        elif dna.name == 'dvg':
            self.scale = 6.25 / aSize
            self.handColor = VBase4(0.831, 0.831, 0.831, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/bigshot.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.45)
        elif dna.name == 'cpl':
            self.scale = 6.75 / cSize
            self.handColor = SuitDNA.corpPolyColor
            self.generateBody()
            self.generateHead('flunky')
            texture = loader.loadTexture('phase_4/maps/corporate-raider.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.23)
        elif dna.name == 'bkp':
            self.scale = 6.75 / aSize
            self.handColor = VBase4(0.882, 0.894, 0.004, 1)
            self.generateBody()
            self.generateHead('toxicleader')
            texture = loader.loadTexture('phase_3.5/maps/skull.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.5)
        elif dna.name == 'kpn':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.749, 0.859, 0.525, 1.0)
            self.generateBody()
            self.generateHead('bigcheese')
            texture = loader.loadTexture('phase_3.5/maps/suit-heads_palette_3cmla_1.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(9.34)
        elif dna.name == 'cg':
            self.scale = 4.5 / aSize
            self.handColor = VBase4(1, 1, 1, 1)
            self.makeSkeletonManager()
            self.setHeight(6.0)
        elif dna.name == 'bg':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.608, 0.525, 0.431, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('clubpresident', animated=True)
            self.setHeight(8.7)
        elif dna.name == 'msr':
            self.scale = 4.5 / aSize
            self.handColor = VBase4(0.573, 0.384, 0.204, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('derrickman', animated=True)
            self.setHeight(6.0)
        elif dna.name == 'kb':
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
        elif dna.name == 'ts':
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
        elif dna.name == 'tc':
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
        elif dna.name == 'tg':
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
        elif dna.name == 'tb':
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
        elif dna.name == 'adc':
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
        elif dna.name == 'drm':
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
        elif dna.name == 'cp':
            self.scale = 5.0 / aSize
            self.handColor = VBase4(0.863, 0.349, 0.122, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('dola', animated=True)
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_dola.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.5)
            self.setTransparency(1)
        elif dna.name == 'fbd':
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
        elif dna.name == 'frs':
            self.scale = 7.2 / aSize
            self.handColor = VBase4(0.682, 0.588, 0.482, 1)
            self.generateFemaleBody()
            self.makeExecutive()
            self.generateHead3('mouthpiece', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_wiretapper.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(9.0)
            self.setTransparency(1)
        elif dna.name == 'gtk':
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
        elif dna.name == 'dt':
            self.scale = 4.0 / bSize
            self.handColor = SuitDNA.legalPolyColor
            self.generateBody()
            self.generateHead3('pettifogger', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_pettifogger.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.6)
        elif dna.name == 'ac':
            self.scale = 4.25 / aSize
            self.handColor = SuitDNA.legalPolyColor
            self.generateBody()
            self.generateHead3('doubletalker', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_doubletalker.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.63)
        elif dna.name == 'bs':
            self.scale = 4.75 / aSize
            self.handColor = VBase4(0.318, 0.333, 0.431, 1)
            self.generateBody()
            self.generateHead3('conveyancer', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_conveyancer.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.generateHead2('conveyancer_belt')
            self.setHeight(6.4)
        elif dna.name == 'sd':
            self.scale = 4.2 / bSize
            self.handColor = SuitDNA.legalPolyColor
            self.generateBody()
            self.generateHead3('ambulance_chaser', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_ambulance_chaser.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.1)
        elif dna.name == 'le':
            self.scale = 4.75 / cSize
            self.handColor = VBase4(0.255, 0.318, 0.549, 1)
            self.generateFemaleBody()
            self.generateHead3('needlenose', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_needlenose.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.5)
        elif dna.name == 'bw':
            self.scale = 5.0 / bSize
            self.handColor = VBase4(0.647, 0.639, 0.788, 1)
            self.generateBody()
            self.generateHead3('backstabber', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_backstabber.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.25)
        elif dna.name == 'brv':
            self.scale = 5.5 / cSize
            self.handColor = VBase4(0.098, 0.098, 0.153, 1)
            self.generateBody()
            self.generateHead3('advocate', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_advocate.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.0)
        elif dna.name == 'sb':
            self.scale = 5.65 / bSize
            self.handColor = VBase4(0.678, 0.91, 0.808, 1)
            self.generateBody()
            self.generateHead3('spin_doctor', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_spin_doctor.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.9)
        elif dna.name == 'cfp':
            self.scale = 5.65 / bSize
            self.handColor = VBase4(0.647, 0.639, 0.788, 1)
            self.generateFemaleBody()
            self.generateHead3('shyster', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_shyster.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.4)
        elif dna.name == 'arb':
            self.scale = 6.8 / aSize
            self.handColor = VBase4(0.25, 0.25, 0.5, 1.0)
            self.generateBody()
            self.generateHead3('legal_eagle', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_legal_eagle.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.57)
        elif dna.name == 'sjg':
            self.scale = 6.9 / aSize
            self.handColor = VBase4(0.784, 0.816, 0.847, 1)
            self.generateBody()
            self.generateHead3('barrister', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_barrister.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.3)
        elif dna.name == 'lsc':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.573, 0.557, 0.761, 1)
            self.generateBody()
            self.generateHead3('bigwig', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_big_wig.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.69)
        elif dna.name == 'jdg':
            self.scale = 4.5 / aSize
            self.handColor = VBase4(0.722, 0.757, 0.784, 1)
            self.generateFemaleBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/whistleblower.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.makeExecutive()
            self.setHeight(6.0)
        elif dna.name == 'jur':
            self.scale = 7.2 / bSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.makeSkeletonManager()
            self.setHeight(8.7)
        elif dna.name == 'tlr':
            self.scale = 7.2 / aSize
            self.handColor = VBase4(0.69, 0.678, 0.765, 1)
            self.generateBody()
            self.generateHead3('clo', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_clo.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.makeExecutive()
            self.setHeight(8.7)
        elif dna.name == 'cm':
            self.scale = 4.5 / cSize
            self.handColor = VBase4(0.361, 0.435, 0.694, 1)
            self.generateFemaleBody()
            self.makeExecutive()
            self.generateHead3('judy', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_judy.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.5)
        elif dna.name == 'ggm':
            self.scale = 5.0 / bSize
            self.handColor = VBase4(0.42, 0.502, 0.62, 1)
            self.generateFemaleBody()
            self.makeExecutive()
            self.generateHead3('mouthpiece', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_mouthpiece.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.8)
        elif dna.name == 'th':
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
        elif dna.name == 'tr':
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
        elif dna.name == 'mp':
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
        elif dna.name == 'laa':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.makeSkeletonManager()
            self.setHeight(8.69)
        elif dna.name == 'scg':
            self.scale = 5.2 / bSize
            self.handColor = VBase4(0.486, 0.522, 0.686, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('scapegoat', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_scapegoat.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.8)
        elif dna.name == 'csm':
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
        elif dna.name == 'ste':
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
        elif dna.name == 'lit':
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
        elif dna.name == 'sc':
            self.scale = 3.0 / cSize
            self.handColor = SuitDNA.moneyPolyColor
            self.generateBody()
            self.generateHead('coldcaller')
            self.setHeight(4.5)
        elif dna.name == 'pp':
            self.scale = 3.55 / aSize
            self.handColor = VBase4(1.0, 0.5, 0.6, 1.0)
            self.generateBody()
            self.generateHead('pennypincher')
            self.setHeight(5.26)
        elif dna.name == 'tw':
            self.scale = 4.0 / bSize
            self.handColor = VBase4(0.741, 0.773, 0.741, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/shylock.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.5)
        elif dna.name == 'bc':
            self.scale = 4.5 / cSize
            self.handColor = SuitDNA.moneyPolyColor
            self.generateBody()
            self.generateHead('tightwad')
            self.setHeight(5.41)
        elif dna.name == 'nc':
            self.scale = 4.34 / aSize
            self.handColor = SuitDNA.boardPolyColor
            self.generateBody()
            self.generateHead('pennypincher')
            texture = loader.loadTexture('phase_3.5/maps/swindler.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.45)
        elif dna.name == 'mb':
            self.scale = 4.4 / bSize
            self.handColor = SuitDNA.moneyPolyColor
            self.generateBody()
            self.generateHead('beancounter')
            self.setHeight(5.95)
        elif dna.name == 'ls':
            self.scale = 5.5 / cSize
            self.handColor = VBase4(0.776, 0.831, 0.812, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/fatcat.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.75)
        elif dna.name == 'rb':
            self.scale = 5.25 / aSize
            self.handColor = SuitDNA.moneyPolyColor
            self.generateFemaleBody()
            self.generateHead('numbercruncher')
            texture = loader.loadTexture('phase_3.5/maps/number_cruncher.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.22)
        elif dna.name == 'gm':
            self.scale = 6.5 / aSize
            self.handColor = VBase4(0.125, 0.125, 0.125, 1)
            self.generateBody()
            self.generateHead2('overtime')
            texture = loader.loadTexture('phase_3.5/maps/ttoff_t_ene_overtime_palette_4amlc_1.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.2)
        elif dna.name == 'ad':
            self.scale = 5.3 / cSize
            self.handColor = SuitDNA.moneyPolyColor
            self.generateBody()
            self.generateHead('moneybags')
            texture = loader.loadTexture('phase_3.5/maps/tutorial_suits_palette_3cmla_1.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.97)
        elif dna.name == 'cvy':
            self.scale = 6.5 / aSize
            self.handColor = VBase4(0.784, 0.804, 0.78, 1)
            self.generateFemaleBody()
            self.generateHead('twoface')
            texture = loader.loadTexture('phase_3.5/maps/mingler3.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.5)
        elif dna.name == 'ptr':
            self.scale = 6.5 / bSize
            self.handColor = SuitDNA.moneyPolyColor
            self.generateBody()
            self.generateHead2('loanshark')
            texture = loader.loadTexture('phase_3.5/maps/suit-heads_palette_3cmla_2.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.58)
        elif dna.name == 'mld':
            self.scale = 7.5 / cSize
            self.handColor = VBase4(0.659, 0, 0, 1)
            self.generateBody()
            self.generateHead('bigfish')
            self.setHeight(10.7)
        elif dna.name == 'pht':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.655, 0.769, 0.725, 1)
            self.generateBody()
            self.generateHead('yesman', animated=False)
            texture = loader.loadTexture('phase_4/maps/robber-baron.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.95)
        elif dna.name == 'csh':
            self.scale = 4.5 / aSize
            self.handColor = VBase4(0.286, 0.29, 0.286, 1)
            self.makeSkeletonManager()
            self.setHeight(6.0)
        elif dna.name == 'bgr':
            self.scale = 7.0 / cSize
            self.handColor = VBase4(0.286, 0.29, 0.286, 1)
            self.makeSkeletonManager()
            self.setHeight(9.0)
        elif dna.name == 'mes':
            self.scale = 5.0 / bSize
            self.handColor = VBase4(0.714, 0.118, 0.055, 1)
            self.generateBody()
            self.makeDuckShuffler()
            self.generateHead3('duckshuffler', animated=True)
            self.setHeight(7.0)
        elif dna.name == 'dm':
            self.scale = 5.5 / cSize
            self.handColor = VBase4(0.647, 0.796, 0.627, 1)
            self.generateBody()
            self.makeTreekiller()
            self.generateHead3('treekiller', animated=True)
            self.setHeight(7.5)
        elif dna.name == 'tcc':
            self.scale = 5.5 / cSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.makeSkeletonManager()
            self.setHeight(6.97)
        elif dna.name == 'fb':
            self.scale = 6.25 / bSize
            self.handColor = VBase4(0.529, 0.455, 0.369, 1)
            self.makeSkeletonManager()
            self.setHeight(7.5)
        elif dna.name == 'jl':
            self.scale = 6.75 / cSize
            self.handColor = VBase4(0.5, 1, 0, 1.0)
            self.makeSkeletonManager()
            self.setHeight(8.23)
        elif dna.name == 'gb':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.makeSkeletonManager()
            self.setHeight(8.95)
        elif dna.name == 'lbs':
            self.scale = 5.45 / aSize
            self.handColor = VBase4(0.286, 0.29, 0.286, 1)
            self.makeSkeletonManager()
            self.setHeight(7.22)
        elif dna.name == 'trk':
            self.scale = 3.5 / cSize
            self.handColor = VBase4(0.702, 0.776, 0.788, 1)
            self.generateBody()
            self.makePlutocrat()
            self.generateHead3('plutocrat', animated=True)
            self.setHeight(5.0)
            self.setTransparency(1)
        elif dna.name == 'dsf':
            self.scale = 7.5 / aSize
            self.handColor = VBase4(1, 1, 1, 1)
            self.generateHighRollerBodyWhite()
            self.generateHead3('highroller', animated=True)
            self.setHeight(10.0)
            self.setTransparency(1)
        elif dna.name == 'msp':
            self.scale = 7.2 / aSize
            self.handColor = VBase4(1, 1, 1, 1.0)
            self.generateBody()
            self.makeCountErclaim()
            self.generateHead3('counterclaim', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_counterclaim.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(9.0)
        elif dna.name == 'mad':
            self.scale = 7.5 / aSize
            self.handColor = VBase4(1, 1, 1, 1)
            self.generateHighRollerBodyWhite()
            self.generateHead3('highroller', animated=True)
            self.makeVirtual()
            self.setHeight(10.0)
            self.setTransparency(1)
        elif dna.name == 'crf':
            self.scale = 7.5 / aSize
            self.handColor = VBase4(1, 1, 1, 1)
            self.generateHighRollerBody()
            self.makeHighRoller()
            self.generateHead3('highroller', animated=True)
            self.setHeight(10.0)
            self.setTransparency(1)
        elif dna.name == 'cc':
            self.scale = 3.5 / cSize
            self.handColor = VBase4(0.039, 0.09, 0.702, 1)
            self.generateBody()
            self.generateHead2('coldcaller')
            texture = loader.loadTexture('phase_3.5/maps/coldcaller.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(4.63)
        elif dna.name == 'tm':
            self.scale = 3.75 / bSize
            self.handColor = VBase4(0.965, 0.859, 0.831, 1)
            self.generateBody()
            self.generateHead('telemarketer')
            texture = loader.loadTexture('phase_4/maps/telemarketer.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.24)
        elif dna.name == 'nd':
            self.scale = 4.0 / bSize
            self.handColor = VBase4(1, 1, 1, 1)
            self.generateBody()
            self.generateHead2('connoisseur_hat')
            self.generateHead2('connoisseur_monocle')
            self.generateHead2('connoisseur_head')
            self.setHeight(5.55)
        elif dna.name == 'gh':
            self.scale = 4.35 / aSize
            self.handColor = SuitDNA.salesPolyColor
            self.generateFemaleBody()
            self.generateHead('numbercruncher')
            texture = loader.loadTexture('phase_3.5/maps/name-dropper.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.98)
        elif dna.name == 'ms':
            self.scale = 4.75 / aSize
            self.handColor = VBase4(0.906, 0.906, 0.933, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/doublecross.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.2)
        elif dna.name == 'tf':
            self.scale = 4.75 / cSize
            self.handColor = VBase4(0.918, 0.886, 0.875, 1)
            self.generateBody()
            self.generateHead('gladhander')
            texture = loader.loadTexture('phase_3.5/maps/tutorial_suits_palette_3cmla_1.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.4)
        elif dna.name == 'm':
            self.scale = 5.5 / aSize
            self.handColor = VBase4(0.302, 0.227, 0.357, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/forecaster.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.1)
        elif dna.name == 'mh':
            self.scale = 4.75 / bSize
            self.handColor = VBase4(0.965, 0.859, 0.831, 1)
            self.generateBody()
            self.generateHead('movershaker')
            texture = loader.loadTexture('phase_4/maps/mover_shaker.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.7)
        elif dna.name == 'ka':
            self.scale = 6.0 / aSize
            self.handColor = VBase4(0.992, 0.851, 0.757, 1)
            self.generateBody()
            self.generateHead('yesman')
            texture = loader.loadTexture('phase_4/maps/mr_hollywood1.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.95)
        elif dna.name == 'mka':
            self.scale = 5.75 / aSize
            self.handColor = VBase4(0.965, 0.859, 0.831, 1)
            self.generateBody()
            self.generateHead('twoface')
            texture = loader.loadTexture('phase_4/maps/twoface.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.45)
        elif dna.name == 'trm':
            self.scale = 6.0 / aSize
            self.handColor = VBase4(0.584, 0.686, 0.745, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/peoplepleaser.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.8)
        elif dna.name == 'ssm':
            self.scale = 6.25 / aSize
            self.handColor = VBase4(0.918, 0.808, 0.871, 1)
            self.generateFemaleBody()
            self.generateHead('twoface')
            texture = loader.loadTexture('phase_4/maps/mingler2.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.11)
        elif dna.name == 'isw':
            self.scale = 6.5 / aSize
            self.handColor = VBase4(0.733, 0.541, 0.525, 1)
            self.generateFemaleBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/kissup_tex.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.5)
        elif dna.name == 'ssr':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.918, 0.886, 0.875, 1)
            self.generateBody()
            self.generateHead('yesman')
            texture = loader.loadTexture('phase_4/maps/mr_hollywood.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.generateHead('shades')
            self.setHeight(8.95)
        elif dna.name == 'fas':
            self.scale = 4.5 / aSize
            self.handColor = VBase4(1, 0.486, 0, 1)
            self.makeSkeletonManager()
            self.setHeight(6.0)
        elif dna.name == 'mdr':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(1, 0.486, 0, 1)
            self.makeSkeletonManager()
            self.setHeight(9.0)
        elif dna.name == 'nar':
            self.scale = 7.0 / cSize
            self.handColor = VBase4(1, 1, 1, 1.0)
            self.makeSkeletonManager()
            self.setHeight(9.5)
        elif dna.name == 'fd':
            self.scale = 7.0 / cSize
            self.handColor = VBase4(1, 1, 1, 1.0)
            self.makeSkeletonManager()
            self.setHeight(9.5)
        elif dna.name == 'fm':
            self.scale = 5.0 / bSize
            self.handColor = VBase4(0.886, 0.749, 0.451, 1)
            self.generateHighCollarBody()
            self.makeBellringer()
            self.generateHead3('bellringer', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_bellringer.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.0)
        elif dna.name == 'jb':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.918, 0.886, 0.875, 1)
            self.generateBody()
            self.generateHead('yesman')
            texture = loader.loadTexture('phase_4/maps/mr_hollywood.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.generateHead('shades')
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
        elif dna.name == 'jr':
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
        elif dna.name == 'prr':
            self.scale = 7.3 / aSize
            self.handColor = VBase4(1, 1, 1, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('multislacker', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_multislacker.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(10.0)
            self.setTransparency(1)
        elif dna.name == 'blr':
            self.scale = 6.8 / aSize
            self.handColor = VBase4(0.612, 0.376, 0.608, 1)
            self.generateBody()
            self.generateHead2('skeleskull_A')
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_s_exe.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.generateHead3('dopa', animated=True)
            self.makeExecutive()
            self.setHeight(8.7)
            self.setTransparency(1)
        elif dna.name == 'dvp':
            self.scale = 5.5 / bSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.generateLongcoatBody()
            self.generateHead3('rainmaker', animated=True)
            self.setHeight(7.0)
        elif dna.name == 'dsk':
            self.scale = 7.2 / aSize
            self.handColor = VBase4(0.604, 0.463, 0.62, 1)
            self.generateBody()
            self.generateHead2('skeleskull_A')
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_s_exe.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.generateHead3('dopr', animated=True)
            self.makeExecutive()
            self.setHeight(8.7)
            self.setTransparency(1)
        elif dna.name == 'ffm':
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
        elif dna.name == 'sft':
            self.scale = 6.2 / bSize
            self.handColor = VBase4(0.369, 0.369, 0.369, 1)
            self.generatePaceBody()
            self.makePacesetter()
            self.generateHead3('pacesetter', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_pacesetter.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.5)
        elif dna.name == 'ca':
            self.scale = 4.0 / cSize
            self.handColor = VBase4(0.427, 0.608, 0.631, 1)
            self.generateBody()
            self.generateHead3('bagholder', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_bagholder.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(4.88)
        elif dna.name == 'cn':
            self.scale = 3.75 / bSize
            self.handColor = VBase4(1, 1, 1, 1)
            self.generateBody()
            self.generateHead3('paperhands', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_paperhands.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.24)
        elif dna.name == 'sw':
            self.scale = 4.0 / cSize
            self.handColor = SuitDNA.boardPolyColor
            self.generateBody()
            self.generateHead('flunky')
            texture = loader.loadTexture('phase_3.5/maps/conartist.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.generateHead('beret')
            self.setHeight(4.88)
        elif dna.name == 'mdm':
            self.scale = 5.0 / bSize
            self.handColor = VBase4(0.031, 0.035, 0.035, 1)
            self.generateHighCollarBody()
            self.generateHead3('insider', animated=True)
            self.setHeight(6.7)
        elif dna.name == 'txm':
            self.scale = 5.0 / aSize
            self.handColor = SuitDNA.boardPolyColor
            self.generateBody()
            self.generateHead('twoface')
            texture = loader.loadTexture('phase_3.5/maps/middleman.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.7)
        elif dna.name == 'mg':
            self.scale = 4.8 / aSize
            self.handColor = SuitDNA.boardPolyColor
            self.generateBody()
            self.generateHead3('circuitbreaker', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_circuitbreaker.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.66)
        elif dna.name == 'bfh':
            self.scale = 5.25 / cSize
            self.handColor = VBase4(0.706, 0.608, 0.18, 1)
            self.generateBody()
            self.generateHead('toxicleader')
            self.setHeight(7.2)
        elif dna.name == 'hho':
            self.scale = 5.5 / cSize
            self.handColor = VBase4(0.463, 0.58, 0.592, 1)
            self.generateBody()
            self.generateHead3('deadlock', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_deadlock.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.2)
        elif dna.name == 'bdb':
            self.scale = 6.5 / bSize
            self.handColor = VBase4(0.91, 0.91, 0.91, 1)
            self.generateFemaleBody()
            self.generateHead3('shyster', animated=True)
            self.generateHead2('angel_halo')
            self.generateHead2('angel_wings')
            #texture = loader.loadTexture('phase_14/maps/cc_t_ene_magnate.png')
            #for headPart in self.headParts:
                #headPart.setTexture(texture, 1)
            self.setHeight(9.5)
        elif dna.name == 'bgh':
            self.scale = 5.75 / cSize
            self.handColor = VBase4(0.427, 0.608, 0.631, 1)
            self.generateBody()
            self.generateHead3('sharkwatcher', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_sharkwatcher.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.25)
        elif dna.name == 'dfh':
            self.scale = 7.0 / cSize
            self.handColor = VBase4(0.635, 0.62, 0.651, 1)
            self.generateFemaleBody()
            self.generateHead2('bigfish')
            self.setHeight(10.0)
        elif dna.name == 'rng':
            self.scale = 6.8 / aSize
            self.handColor = VBase4(0.169, 0.169, 0.169, 1)
            self.generateBody()
            self.generateHead3('magnate', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_magnate.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.0)
        elif dna.name == 'cps':
            self.scale = 7.0 / aSize
            self.handColor = SuitDNA.boardPolyColor
            self.generateBody()
            self.generateHead('headhoncho')
            texture = loader.loadTexture('phase_3.5/maps/head-honcho.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.7)
        elif dna.name == 'tld':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.42, 0.42, 0.42, 1)
            self.generateBody()
            self.generateHead3('headhoncho', animated=True)
            self.setHeight(10.61)
        elif dna.name == 'gkp':
            self.scale = 4.5 / aSize
            self.handColor = VBase4(1, 0.486, 0, 1)
            self.makeSkeletonManager()
            self.setHeight(6.0)
        elif dna.name == 'ddv':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(1, 0.486, 0, 1)
            self.makeSkeletonManager()
            self.setHeight(9.0)
        elif dna.name == 'dty':
            self.scale = 8.0 / cSize
            self.handColor = VBase4(0.404, 0.647, 0.635, 1)
            self.generateFemaleBody()
            self.makeDeepDiver()
            self.generateHead3('deepdiver', animated=True)
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_ddiver.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(11.0)
        elif dna.name == 'dfg':
            self.scale = 5.5 / aSize
            self.handColor = VBase4(0.612, 0.612, 0.612, 1)
            self.generateFemaleBody()
            self.makeGatekeeper()
            self.generateHead3('gatekeeper', animated=True)
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_gatekeeper.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.9)
        elif dna.name == 'dfr':
            self.scale = 6.0 / bSize
            self.handColor = SuitDNA.boardPolyColor
            self.generateBody()
            self.makeBoardbotManager()
            self.generateHead3('dola', animated=True)
            self.setHeight(8.0)
        elif dna.name == 'bsh':
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
        elif dna.name == 'ghd':
            self.scale = 6.0 / bSize
            self.handColor = VBase4(0.09, 0.09, 0.09, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('vp', animated=True)
            self.setHeight(8.0)
            self.setTransparency(1)
        elif dna.name == 'tyh':
            self.scale = 7.2 / aSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('cfo', animated=True)
            self.setHeight(10.7)
            self.setTransparency(1)
        elif dna.name == 'jgd':
            self.scale = 7.2 / aSize
            self.handColor = VBase4(0.09, 0.09, 0.09, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('ceo-a', animated=True)
            self.setHeight(9.0)
            self.setTransparency(1)
        elif dna.name == 'bby':
            self.scale = 7.3 / aSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead3('ceo', animated=True)
            self.setHeight(10.9)
            self.setTransparency(1)
        elif dna.name == 'dvk':
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
        elif dna.name == 'otm':
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
        elif dna.name == 'cry':
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
        elif dna.name == 'tcm':
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
        elif dna.name == 'phs':
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
        elif dna.name == 'kyl':
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
        elif dna.name == 'gry':
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
        elif dna.name == 'shp':
            self.scale = 6.0 / aSize
            self.handColor = VBase4(0.58, 0.392, 0.49, 1)
            self.generateBody()
            self.generateHead2('root')
            texture = loader.loadTexture('phase_14/maps/devil.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.3)
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
        elif dna.name == 'sys':
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
        elif dna.name == 'yuh':
            self.scale = 5.0 / cSize
            self.handColor = VBase4(0.882, 0.847, 0.784, 1)
            self.generateBody()
            self.makeDummy()
            self.generateHead3('dummy', animated=True)
            texture = loader.loadTexture('phase_4/maps/schoolhouse/dummy/ttcc_ene_djockey.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.0)
        elif dna.name == 'yhi':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.generateSkeletonBody()
            self.makeExecutive()
            self.setTransparency(1)
            self.setHeight(8.5)
        elif dna.name == 'jas':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.generateSkeletonBody()
            self.makeExecutive()
            self.setTransparency(1)
            self.setHeight(8.5)
        elif dna.name == 'tas':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.generateSkeletonBody()
            self.makeExecutive()
            self.setTransparency(1)
            self.setHeight(8.5)
        elif dna.name == 'fhu':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.generateSkeletonBody()
            self.makeExecutive()
            self.setTransparency(1)
            self.setHeight(8.5)
        elif dna.name == 'fsh':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.generateSkeletonBody()
            self.makeExecutive()
            self.setTransparency(1)
            self.setHeight(8.5)
        elif dna.name == 'fhj':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.generateBody()
            self.generateHead2('skeleskull_A')
            self.generateHead3('skullA', animated=True)
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_c2.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.makeExecutive()
            self.makeVirtual()
            self.setTransparency(1)
            self.setHeight(8.5)
        elif dna.name == 'kdh':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.generateBody()
            self.generateHead3('highroller', animated=True)
            self.makeExecutive()
            self.setTransparency(1)
            self.setHeight(8.5)
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
        self.setName(SuitBattleGlobals.SuitAttributes[dna.name]['name'])
        self.getGeomNode().setScale(self.scale)
        if not self.isSkeleton:
            self.generateHealthBar()
            self.generateCorporateMedallion()
            self.generateCorporateMedallion2()
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
                self.loadModel('phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-zero')
            else:
                self.loadModel('phase_3.5' + filePrefix + 'mod')
                self.loadModel('phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-zero')
        else:
            self.loadModel('phase_3.5' + filePrefix + 'mod')
            self.loadModel('phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-zero')
        self.loadAnims(animDict)
        self.setSuitClothesHybrid()
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
        if self.style.body == 'a' and self.style.name == 'kb':
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
        if self.style.body == 'a' and self.style.name == 'blr':
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
        if self.style.body == 'a' and self.style.name == 'cg':
            self.generateHead3('autocaddie', animated=True)
            for headPart in self.headParts:
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(1)
        if self.style.body == 'a' and self.style.name == 'bg':
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
        if self.style.body == 'a' and self.style.name == 'dsk':
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
        if self.style.body == 'a' and self.style.name == 'gtk':
            self.generateHead3('prethinker2', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_prethinker.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
        if self.style.body == 'a' and not self.style.name == 'cg' and not self.style.name == 'kb' and not self.style.name == 'gtk' and not self.style.name == 'bg' and not self.style.name == 'dsk' and not self.style.name == 'blr':
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
        if self.style.body == 'c' and self.style.name == 'fd':
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
        if self.style.body == 'c' and self.style.name == 'nar':
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
        if self.style.body == 'c' and not self.style.name == 'fd' and not self.style.name == 'nar':
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
        texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_%s.png' % self.style.dept)
        if self.isExecutive and not self.style.name == 'mdm' and not self.style.name == 'dsf' and not self.style.name == 'yuh':
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_%s_e.png' % self.style.dept)
        elif self.isManager and not self.style.name == 'crf':
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_%s_e.png' % self.style.dept)
        elif self.isExecutive and self.style.name == 'dsf':
            texture = loader.loadTexture('phase_12/maps/cc_t_ene_highroller_suit.png')
        elif self.isExecutive and self.style.name == 'yuh':
            texture = loader.loadTexture('phase_4/maps/schoolhouse/dummy/ttcc_ene_suittex_ptjockey_e.png')
        elif self.isGovernaught and not self.style.name == 'mdm':
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_%s_gov.png' % self.style.dept)
        elif not self.isGovernaught and not self.isExecutive and self.style.name == 'mdm':
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_highcollar_%s.png' % self.style.dept)
        elif self.isGovernaught and self.style.name == 'mdm':
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_highcollar_%s_gov.png' % self.style.dept)
        elif self.isExecutive and self.style.name == 'mdm':
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_highcollar_%s_e.png' % self.style.dept)
        modelRoot.find('**/hands').setColor(self.handColor)
        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()
        modelRoot.find('**/bowtie').hide()
        modelRoot.find('**/necktie-s').setTexture(texture, 1)
        modelRoot.find('**/necktie-w').setTexture(texture, 1)
        modelRoot.find('**/bowtie').setTexture(texture, 1)
        if self.style.dept == 'l':
            modelRoot.find('**/bowtie').show()
        elif self.style.name == 'gry':
            modelRoot.find('**/necktie-s').show()
        elif self.style.dept == 's':
            modelRoot.find('**/necktie-s').show()
        elif self.style.name == 'sft':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'crf':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'mdm':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'mp':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'tr':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'dsf':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'msp':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'dvk':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'dty':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'dfg':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'dvp':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
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
        elif self.style.name == 'sft':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'prr':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'dsf':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'crf':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'tb':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'mad':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'mdm':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'msp':
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
        elif self.style.dept == 's' and not self.style.name == 'dvp':
            modelRoot.find('**/necktie-s').show()
        elif self.style.name == 'sft':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'prr':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'crf':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'tb':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'mad':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'mdm':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'ghd':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'dvp':
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
        elif self.style.name == 'sft':
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'dfh':
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'mad':
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'dsf':
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'crf':
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'msp':
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
        elif self.isManager and not self.style.name == 'lbs' and not self.style.name == 'jl'\
                and not self.style.name == 'blr' and not self.style.name == 'dsk' and not self.style.name == 'gb' and not self.style.name == 'fb' and not self.style.name == 'tcc' and not self.isWaiter:
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
        elif self.style.name == 'laa':
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-w').show()
        elif self.style.name == 'jl':
            modelRoot.find('**/bowtie').show()
            modelRoot.setColor((0.729, 0.729, 0.729, 1))
            modelRoot.find('**/bowtie').setColor((0.741, 0.82, 0.769, 1))
        elif self.style.name == 'lbs':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/necktie-s').show()
            modelRoot.setColor((0.51, 0.49, 0.467, 1))
            modelRoot.find('**/necktie-s').setColor((0.741, 0.82, 0.769, 1))
        elif self.style.name == 'fb':
            modelRoot.find('**/necktie-w').show()
            modelRoot.setColor((0.6, 0.6, 0.6, 1))
            modelRoot.find('**/necktie-w').setColor((0.741, 0.82, 0.769, 1))
        elif self.style.name == 'tcc':
            modelRoot.find('**/necktie-w').show()
            modelRoot.setColor((0.671, 0.671, 0.671, 1))
            modelRoot.find('**/necktie-w').setColor((0.741, 0.82, 0.769, 1))
        elif self.style.name == 'gb':
            modelRoot.find('**/necktie-w').show()
            modelRoot.setColor((0.62, 0.659, 0.624, 1))
            modelRoot.find('**/necktie-w').setColor((0.741, 0.82, 0.769, 1))
        elif self.style.name == 'th':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'dvp':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'msp':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'tr':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'mad':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'crf':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'dsf':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'fm':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'sft':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'mdm':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'dvk':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'dfg':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'dty':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'dar':
            modelRoot.find('**/necktie-w').hide()
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
        if self.style.name == 'tld' and not self.isSkeleton and not self.isExecutive:
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
        if self.style.name == 'tld' and not self.isSkeleton and not self.isExecutive:
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
        if self.style.dept == 'l' and not self.style.name == 'mp' and not self.style.name == 'tr':
            modelRoot.find('**/bowtie').show()
        elif self.style.dept == 's' and not self.style.name == 'dvp':
            modelRoot.find('**/necktie-s').show()
        elif self.style.name == 'sft':
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'mp':
            modelRoot.find('**/bowtie').hide()
        elif self.style.name == 'tr':
            modelRoot.find('**/bowtie').hide()
        elif self.style.name == 'dfh':
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'crf':
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'dvp':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/necktie-s').show()
        elif self.style.name == 'msp':
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
                textureGlass = loader.loadTexture('phase_9/maps/ttcc_ene_prethinker_glass.png')
                headModel.find('**/glass').setTexture(textureGlass, 1)
                headModel.setScale(1)
                headModel.setZ(-.1)
                headModel.setY(-.1)
            if headType == 'prethinker2' and self.style.name == 'gtk':
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
            elif headType == 'shyster' and self.style.name == 'bdb':
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
            elif headType == 'magnate' and self.style.name == 'rng' :
                headModel.setZ(-.1)
            elif headType == 'magnate' and self.style.name == 'jgd' :
                headModel.setZ(-.1)
            #elif headType == 'magnate' and self.style.name == 'bdb' :
                #headModel.setZ(-.1)
            elif headType == 'magnate' and self.style.name == 'jdg' :
                headModel.setZ(-.1)
            elif headType == 'bagholder' and self.style.name == 'ca' :
                headModel.setZ(.5)
            elif headType == 'paperhands' and self.style.name == 'cn' :
                headModel.setScale(.6)
            elif headType == 'paperhands' and self.style.name == 'fbd' :
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
            elif self.style.name == 'scg':
                headModel.setTwoSided(True)
            elif headType == 'clo':
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
            elif headType == 'plutocrat' and self.style.name == 'auh':
                headModel.setScale(.85)
                headModel.setZ(-.1)
                headModel.setY(-.1)
            elif headType == 'skullA' and self.style.name == 'fhj' and not self.isSkeleton:
                headModel.setZ(.25)
                headModel.setY(-.2)
            elif headType == 'skullA' and self.style.name == 'gry' and not self.isSkeleton:
                headModel.setZ(.25)
                headModel.setY(-.2)
            elif headType == 'advocate' and self.style.name == 'bdb':
                headModel.setScale(1.05)
                headModel.setZ(-.1)
                headModel.setY(-.2)
                headModel.setY(0)
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
            elif headType == 'multislacker' and self.style.name == 'blr':
                headModel.setZ(-.1)
                headModel.setY(-.1)
            elif headType == 'dola' and self.style.name == 'cp':
                headModel.setZ(-.1)
                headModel.setY(-.1)
            elif headType == 'dopr' and self.style.name == 'dsk' and not self.isSkeleton:
                headModel.setScale(1.3)
                headModel.setZ(.25)
                headModel.setY(-.2)
                texture = loader.loadTexture('phase_9/maps/ttcc_ene_dopr.png')
                headModel.setTexture(texture, 1)
            elif headType == 'dopa' and self.style.name == 'blr' and not self.isSkeleton:
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
            elif headType == 'autocaddie':
                textureGlass = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_c_exe.png')
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
            elif headType == 'paperhands' and self.style.name == 'fbd' :
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
        if headType == 'bigfish' and self.style.name == 'dfh':
                headModel = loader.loadModel('phase_14/models/char/ttcc_ene_bigfish-zero')
        if headType == 'flunky' and self.style.body == 'a':
                headModel = loader.loadModel('phase_3.5/models/char/suitC-heads')
        if headType == 'beret' and self.style.body == 'a':
                headModel = loader.loadModel('phase_3.5/models/char/suitC-heads')
        if headType == 'connoisseur_hat' and self.style.name == 'bgh':
                headModel = loader.loadModel('phase_14/models/char/ttcc_ene_connoisseur')
        if headType == 'greyhat' and self.style.name == 'gry':
            headModel = loader.loadModel('phase_14.5/models/char/grey-hat')
        if headType == 'root' and self.style.name == 'dvg':
            headModel = loader.loadModel('phase_14/models/char/yesman')
        if headType == 'root' and self.style.name == 'trb':
            headModel = loader.loadModel('phase_14/models/char/yesman')
        if headType == 'root' and self.style.name == 'jdg':
            headModel = loader.loadModel('phase_14/models/char/whistleblower')
        if headType == 'root' and self.style.name == 'ls':
            headModel = loader.loadModel('phase_14/models/char/bookkeeper')
        if headType == 'root' and self.style.name == 'cvy':
            headModel = loader.loadModel('phase_14/models/char/yesman')
        if headType == 'magnate' and self.style.name == 'bdb':
                headModel = loader.loadModel('phase_14/models/char/ttcc_ene_magnate-zero2')
        if headType == 'camera' and self.style.name == 'cps':
                headModel = loader.loadModel('phase_4/models/accessories/newstoon_camera')
        if headType == 'root' and self.style.name == 'isw':
            headModel = loader.loadModel('phase_14/models/char/mingler')
        if headType == 'root' and self.style.name == 'trm':
            headModel = loader.loadModel('phase_14/models/char/tf_new')
        if headType == 'root' and self.style.name == 'shp':
            headModel = loader.loadModel('phase_14/models/char/devil')
        if headType == 'root' and self.style.name == 'ms':
            headModel = loader.loadModel('phase_14/models/char/doublecross')
        if headType == 'root' and self.style.name == 'ls':
            headModel = loader.loadModel('phase_14/models/char/fatcat')
        if headType == 'root' and self.style.name == 'm':
            headModel = loader.loadModel('phase_14/models/char/forecaster')
        if headType == 'root' and self.style.name == 'gry':
            headModel = loader.loadModel('phase_14/models/char/keyboard-warrior')
        if headType == 'root' and self.style.name == 'pyc':
            headModel = loader.loadModel('phase_14/models/char/python-charmer_head')
        if headType == 'root' and self.style.name == 'sdb':
            headModel = loader.loadModel('phase_14/models/char/shotgun-debugger_head')
        if headType == 'root' and self.style.name == 'tw':
            headModel = loader.loadModel('phase_14/models/char/shylock')
        if headType == 'Blowhard' and self.style.name == 'cr':
                headModel = loader.loadModel('phase_3.5/models/char/ttrm_m_ene_head_blowhard')
        if headType == 'industryTitan':
                headModel = loader.loadModel('phase_3.5/models/char/ttrpg_tech-heads')
        if headType == 'dataHoarder':
            headModel = loader.loadModel('phase_3.5/models/char/ttrpg_tech-heads')
        if headType == 'codeMonkey':
            headModel = loader.loadModel('phase_3.5/models/char/ttrpg_tech-heads')
        if headType == 'brainiac':
            headModel = loader.loadModel('phase_3.5/models/char/ttrpg_tech-heads')
        if headType == 'computerWizard':
            headModel = loader.loadModel('phase_3.5/models/char/ttrpg_tech-heads')
        if headType == 'connoisseur_head' and self.style.name == 'bgh':
                headModel = loader.loadModel('phase_14/models/char/ttcc_ene_connoisseur')
        if headType == 'connoisseur_monocle' and self.style.name == 'bgh':
                headModel = loader.loadModel('phase_14/models/char/ttcc_ene_connoisseur')
        if headType == 'connoisseur_hat' and self.style.name == 'nd':
                headModel = loader.loadModel('phase_14/models/char/ttcc_ene_connoisseur')
        if headType == 'connoisseur_head' and self.style.name == 'nd':
                headModel = loader.loadModel('phase_14/models/char/ttcc_ene_connoisseur')
        if headType == 'connoisseur_monocle' and self.style.name == 'nd':
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
        if headType == 'skeleskull_A' and self.style.name == 'dsk':
            headModel = loader.loadModel('phase_5/models/char/skullbase')
            headModel.setZ(-.1)
            headModel.setY(-.2)
            textureGlass = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_s_exe.png')
            headModel.setTexture(textureGlass, 1)
        if headType == 'skeleskull_A' and self.style.name == 'blr':
            headModel = loader.loadModel('phase_5/models/char/skullbase')
            headModel.setZ(-.1)
            headModel.setY(-.2)
            textureGlass = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_s_exe.png')
            headModel.setTexture(textureGlass, 1)
        if headType == 'skeleskull_A' and self.style.name == 'gry':
            headModel = loader.loadModel('phase_5/models/char/skullbase')
            headModel.setZ(-.1)
            headModel.setY(-.2)
            textureGlass = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_s.png')
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
            if self.style.name == 'bdb' and headType == 'angel_wings':
                headPart.setZ(1.25)
                headPart.setScale(1.25)
            if self.style.name == 'bdb' and headType == 'angel_halo':
                headPart.setZ(1.25)
                headPart.setScale(.75)
            if headType == 'skeleskull_A':
                headPart.setY(-.2)
                headPart.setZ(-.1)
            if self.style.name == 'gry':
                headPart.setH(180)
            if self.style.name == 'trb':
                headPart.setZ(-.4)
                headPart.setScale(.7)
                headPart.setH(180)
            if self.style.name == 'trm':
                headPart.setZ(0.9)
                headPart.setY(1)
                headPart.setX(-0.05)
                headPart.setScale(4)
            if self.style.name == 'ls':
                headPart.setH(180)
                headPart.setScale(1.15)
            if self.style.name == 'm':
                headPart.setH(180)
            if self.style.name == 'gm':
                headPart.setY(-.2)
                headPart.setScale(1.05)
            if self.style.name == 'shp':
                headPart.setX(0.05)
            if headType == 'root' and self.style.name == 'jdg': #whistleblower
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
            if self.style.name == 'ym':
                headPart.setH(180)
                headPart.setZ(-.1)
            if self.style.name == 'cr':
                headPart.setH(180)
            if self.style.name == 'rus':
                headPart.setZ(-.1)
                headPart.setY(-.1)
                headPart.setScale(1.05)
                headPart.setH(0)
            if headType == 'hatjp187187' and self.style.name == 'bdb':
                headPart.setZ(-.7)
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
            self.corpMedallion = icons.find('**/emblem_board').copyTo(chestNull)
        elif dept == 't':
            self.corpMedallion = icons.find('**/emblem_board').copyTo(chestNull)
            texture = loader.loadTexture('phase_3/maps/ttcc_suit_insignias_palette2.png')
            self.corpMedallion.setTexture(texture, 1)

        self.corpMedallion.setPosHprScale(0, -1, 0, 180.0, 0.0, 0.0, 0, 0, 0)
        self.corpMedallion.setColor(self.medallionColors[dept])
        if self.style.name == 'fhj':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'mad':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'dsf':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'crf':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'le':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'phs':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'hh':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'ls':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'dfh':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'cm':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'bdb':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'dty':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'cfp':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'ggm':
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
            self.corpMedallion = icons.find('**/emblem_board').copyTo(chestNull)
        elif dept == 't':
            self.corpMedallion = icons.find('**/emblem_board').copyTo(chestNull)
            texture = loader.loadTexture('phase_3/maps/ttcc_suit_insignias_palette2.png')
            self.corpMedallion.setTexture(texture, 1)

        self.corpMedallion.setPosHprScale(0, -1, 0, 180.0, 0.0, 0.0, 0, 0, 0)
        self.corpMedallion.setColor(self.medallionColors[dept])
        if self.style.name == 'fhj':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'mad':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'dsf':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'crf':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'le':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'hh':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'cm':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'dty':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'phs':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'bdb':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'cfp':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'dfh':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'ggm':
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
            self.corpMedallion = icons.find('**/emblem_board').copyTo(chestNull)
        elif dept == 't':
            self.corpMedallion = icons.find('**/emblem_board').copyTo(chestNull)
            texture = loader.loadTexture('phase_3/maps/ttcc_suit_insignias_palette2.png')
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
        if self.style.name == 'le':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'hh':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'phs':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'cm':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'bdb':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'dty':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'cfp':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'dfh':
            self.corpMedallion.setZ(.2)
        elif self.style.name == 'ggm':
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
        self.hpBase.setH(180.0)
        self.hpBase.setColor(self.medallionColors[dept])
        if self.style.name == 'fhj':
            self.hpBase.setScale(0)
        elif self.style.name == 'mad':
            self.hpBase.setScale(0)
        elif self.style.name == 'dsf':
            self.hpBase.setScale(0)
        elif self.style.name == 'crf':
            self.hpBase.setScale(0)
        else:
            self.hpBase.setScale(1.175)
        if self.style.name == 'le':
            self.hpBase.setZ(.2)
        elif self.style.name == 'hh':
            self.hpBase.setZ(.2)
        elif self.style.name == 'cm':
            self.hpBase.setZ(.2)
        elif self.style.name == 'dty':
            self.hpBase.setZ(.2)
        elif self.style.name == 'cfp':
            self.hpBase.setZ(.2)
        elif self.style.name == 'phs':
            self.hpBase.setZ(.2)
        elif self.style.name == 'ggm':
            self.hpBase.setZ(.2)
        elif self.style.name == 'bdb':
            self.hpBase.setZ(.2)
        elif self.style.name == 'dfh':
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
        elif self.style.name == 'mad':
            button.setScale(0)
        elif self.style.name == 'dsf':
            button.setScale(0)
        elif self.style.name == 'crf':
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
        elif self.style.name == 'mad':
            glow.setScale(0)
        elif self.style.name == 'dsf':
            glow.setScale(0)
        elif self.style.name == 'crf':
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
        if self.style.name == 'le':
            self.healthBar.setZ(.2)
        elif self.style.name == 'dfh':
            self.healthBar.setZ(.2)
        elif self.style.name == 'hh':
            self.healthBar.setZ(.2)
        elif self.style.name == 'cm':
            self.healthBar.setZ(.2)
        elif self.style.name == 'phs':
            self.healthBar.setZ(.2)
        elif self.style.name == 'dty':
            self.healthBar.setZ(.2)
        elif self.style.name == 'cfp':
            self.healthBar.setZ(.2)
        elif self.style.name == 'bdb':
            self.healthBar.setZ(.2)
        elif self.style.name == 'ggm':
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
        if self.style.name == 'mad':
            if self.maxHP > 13000:
                self.setDisplayName(self.createNameInfoMagenta())
                self.virtualize(20)
            elif self.maxHP > 12000:
                self.setDisplayName(self.createNameInfoWhite())
                self.virtualize(19)
            elif self.maxHP > 11000:
                self.setDisplayName(self.createNameInfoPurple())
                self.virtualize(13)
            elif self.maxHP > 10000:
                self.setDisplayName(self.createNameInfoLightBlue())
                self.virtualize(12)
            elif self.maxHP > 9000:
                self.setDisplayName(self.createNameInfoPink())
                self.virtualize(14)
            elif self.maxHP > 8000:
                self.setDisplayName(self.createNameInfoRed())
                self.virtualize(8)
            elif self.maxHP > 7000:
                self.setDisplayName(self.createNameInfoBlue())
                self.virtualize(15)
            elif self.maxHP > 6000:
                self.setDisplayName(self.createNameInfoYellow())
                self.virtualize(3)
            elif self.maxHP > 5000:
                self.setDisplayName(self.createNameInfoOrange())
                self.virtualize(7)
            else:
                self.setDisplayName(self.createNameInfoGreen())
                self.virtualize(0)
        if self.style.name == 'bg':
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
        if self.style.name == 'bgr':
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
        if self.style.name == 'jur':
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
        if self.style.name == 'mdr':
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
        #self.healthCondition = condition
        #print('UpdateHealthBar - condition is %i' % condition)

        if self.healthCondition != condition or forceUpdate:
            if condition <= 9:
                taskMgr.remove(self.uniqueName('blink-task'))
                if not self.virtual:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    self.healthBar.setColor(1, 1, 1, 1)
                    self.healthBarGlow.setColor(1, 1, 1, 1)
                else:
                    self.healthBarGlow.setColor(0, 0, 0, 0)
                    taskMgr.remove(self.uniqueName('blink-task'))
                    if not self.style.name == 'mad':
                        self.virtualize(condition)
                self.__changeColor()
            elif condition == 10:
                taskMgr.remove(self.uniqueName('blink-task'))
                if not self.virtual:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    self.healthBar.setColor(1, 1, 1, 1)
                    self.healthBarGlow.setColor(1, 1, 1, 1)
                blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.75), Task(self.__pulseGray), Task.pause(0.1))
                taskMgr.add(blinkTask, self.uniqueName('blink-task'))
            elif condition == 11:
                taskMgr.remove(self.uniqueName('blink-task'))
                if not self.virtual:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    self.healthBar.setColor(1, 1, 1, 1)
                    self.healthBarGlow.setColor(1, 1, 1, 1)
                if self.healthCondition == 10:
                    taskMgr.remove(self.uniqueName('blink-task'))
                blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.25), Task(self.__pulseGray), Task.pause(0.1))
                taskMgr.add(blinkTask, self.uniqueName('blink-task'))
            elif condition == 13:
                taskMgr.remove(self.uniqueName('blink-task'))
                if not self.virtual:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    self.healthBar.setColor(1, 1, 1, 1)
                    self.healthBarGlow.setColor(1, 1, 1, 1)
                blinkTask = Task.loop(Task(self.__pulsePurple), Task.pause(1.5), Task(self.__pulsePurpleColor), Task.pause(1.5))
                taskMgr.add(blinkTask, self.uniqueName('blink-task'))
            else:
                taskMgr.remove(self.uniqueName('blink-task'))
                if not self.virtual:
                    self.healthBar.setColor(1, 1, 1, 1)
                    self.healthBarGlow.setColor(1, 1, 1, 1)
                    taskMgr.remove(self.uniqueName('blink-task'))
                else:
                    self.healthBarGlow.setColor(0, 0, 0, 0)
                    taskMgr.remove(self.uniqueName('blink-task'))
                    if not self.style.name == 'mad':
                        self.virtualize(condition)
                self.__changeColor()
            self.healthCondition = condition

    def __blinkRed(self, task):
        if not self.virtual:
            self.healthBar.setColor(self.healthColors[9], 1)
            self.healthBarGlow.setColor(self.healthGlowColors[9], 1)
        elif not self.style.name == 'mad':
            self.healthBarGlow.setColor(0, 0, 0, 0)
            self.virtualize(9)
        else:
            self.virtualize(9)

    def __blinkGray(self, task):
        if not self.virtual:
            self.healthBar.setColor(self.healthColors[10], 1)
            self.healthBarGlow.setColor(self.healthGlowColors[10], 1)
        elif not self.style.name == 'mad':
            self.healthBarGlow.setColor(0, 0, 0, 0)
            self.virtualize(10)
        else:
            self.virtualize(10)

    def __pulseRed(self, task):
        if not self.virtual:
            self.interval = Parallel(LerpColorScaleInterval(self.healthBar, duration=.25, colorScale=(1, 0, 0, 1),
                                   blendType='easeInOut'))
            self.glowInterval = Parallel(LerpColorScaleInterval(self.healthBarGlow, duration=.25, colorScale=(1, 0, 0, 1),
                                   blendType='easeInOut'))
            self.interval.start()
            self.glowInterval.start()
        else:
            self.healthBarGlow.setColor(0, 0, 0, 0)
            if not self.style.name == 'mad':
                self.virtualizeRed(9)

    def __pulseWhite(self):
        if not self.virtual:
            self.interval = Parallel(LerpColorScaleInterval(self.healthBar, duration=.25, colorScale=(1, 1, 1, 1),
                                   blendType='easeInOut'))
            self.glowInterval = Parallel(LerpColorScaleInterval(self.healthBarGlow, duration=.25, colorScale=(1, 1, 1, 1),
                                   blendType='easeInOut'))
            self.interval.start()
            self.glowInterval.start()
        else:
            self.healthBarGlow.setColor(0, 0, 0, 0)
            if not self.style.name == 'mad':
                self.virtualizeRed(9)

    def __pulseGray(self, task):
        if not self.virtual:
            self.interval = Parallel(LerpColorScaleInterval(self.healthBar, duration=.25, colorScale=(0.431, 0.431, 0.431, 1),
                                   blendType='easeInOut'))
            self.glowInterval = Parallel(LerpColorScaleInterval(self.healthBarGlow, duration=.25, colorScale=(0, 0, 0, 0),
                                   blendType='easeInOut'))
            self.interval.start()
            self.glowInterval.start()
        else:
            self.healthBarGlow.setColor(0, 0, 0, 0)
            if not self.style.name == 'mad':
                self.virtualizeGray(10)

    def __pulsePurple(self, task):
        if not self.virtual:
            self.interval = Parallel(LerpColorScaleInterval(self.healthBar, duration=1, colorScale=(0.702, 0, 1, 1),
                                   blendType='easeInOut'))
            self.glowInterval = Parallel(LerpColorScaleInterval(self.healthBarGlow, duration=1, colorScale=(0.702, 0, 1, 1),
                                   blendType='easeInOut'))
            self.interval.start()
            self.glowInterval.start()
        else:
            self.healthBarGlow.setColor(0, 0, 0, 0)
            if not self.style.name == 'mad':
                self.virtualizePurple(17)

    def __changeColor(self):
        if not self.virtual:
            self.interval = Parallel(LerpColorScaleInterval(self.healthBar, duration=1, colorScale=(self.healthColors[self.condition]),
                                   blendType='easeInOut'))
            self.glowInterval = Parallel(LerpColorScaleInterval(self.healthBarGlow, duration=1, colorScale=(self.healthColors[self.condition]),
                                   blendType='easeInOut'))
            self.interval.start()
            self.glowInterval.start()
        else:
            self.healthBarGlow.setColor(0, 0, 0, 0)
            if not self.style.name == 'mad':
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
            if not self.style.name == 'mad':
                self.virtualize(13)

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
                    LerpColorScaleInterval(thing, duration=1, colorScale=(self.healthColors[condition]),
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
                    LerpColorScaleInterval(thing, duration=.25, colorScale=(self.healthColors[condition]),
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
                    LerpColorScaleInterval(thing, duration=1, colorScale=(0.702, 0, 1, 1),
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
                    LerpColorScaleInterval(thing, duration=.25, colorScale=(0.431, 0.431, 0.431, 1),
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
                    LerpColorScaleInterval(thing, duration=.25, colorScale=(1, 0, 0, 1),
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
            if self.style.name == 'kb':
                headPart.setTexture(textureDerrick, 1)
            elif self.style.name == 'dsk':
                headPart.setTexture(textureDopr, 1)
            elif self.style.name == 'blr':
                headPart.setTexture(textureDopa, 1)
            elif self.style.name == 'gtk':
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
            if self.style.name == 'kb':
                headPart.setTexture(textureDerrick, 1)
            elif self.style.name == 'dsk':
                headPart.setTexture(textureDopr, 1)
            elif self.style.name == 'blr':
                headPart.setTexture(textureDopa, 1)
            elif self.style.name == 'gtk':
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
        if self.style.name == 'ca' and not self.isSkeleton:
            texture2 = loader.loadTexture('phase_14/maps/cc_t_ene_bagholder_unemployed.png')
            for headPart in self.headParts:
                headPart.setTexture(texture2, 1)
        if self.style.name == 'mdm' and not self.isSkeleton:
            texture2 = loader.loadTexture('phase_14/maps/cc_t_ene_insider_unemployed.png')
            for headPart in self.headParts:
                headPart.setTexture(texture2, 1)
        if self.style.name == 'tld' and not self.isSkeleton:
            texture2 = loader.loadTexture('phase_14/maps/cc_t_ene_headhoncho_unemployed.png')
            for headPart in self.headParts:
                headPart.setTexture(texture2, 1)

        self.isFired = 1

    def makeDesperation(self, elite=False):
        self.isDesperation = 1

    def makeSoaked(self, elite=False):
        self.isSoaked = 1

    def makeUnSoaked(self, elite=False):
        self.isSoaked = 0

    def makeImmortal(self, elite=False):
        self.healthBar.setColor(1, 1, 1, 1)
        self.healthBarGlow.setColor(1, 1, 1, 1)
        taskMgr.remove(self.uniqueName('blink-task'))
        self.__pulseWhite()
        self.isImmortal = 1

    def makeNonImmortal(self, elite=False):
        self.healthBar.setColor(1, 1, 1, 1)
        self.healthBarGlow.setColor(1, 1, 1, 1)
        taskMgr.remove(self.uniqueName('blink-task'))
        self.__changeColor()
        self.isImmortal = 0

    def makeLured(self, elite=False):
        self.isLured = 1

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

    def makeSyphon(self, elite=False):
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

    def makeUnSyphon(self, elite=False):
        self.isSyphon = 0

    def makeVulnerable(self, elite=False):
        self.isVulnerable = 1

    def makeUnVulnerable(self, elite=False):
        self.isVulnerable = 0

    def makeDead(self, elite=False):
        self.isDead = 1

    def makeUnDead(self, elite=False):
        self.isDead = 0

    def makeRevive(self, elite=False):
        self.isRevived = 1

    def makeLaserRevive(self, elite=False):
        self.isLaserRevived = 1

    def makeDamageUp(self, elite=False):
        self.isDamageUp = 1

    def makeUnDamageUp(self, elite=False):
        self.isDamageUp = 0

    def makeDamageReduction(self, elite=False):
        self.isDamageReduction = 1

    def makeUnDamageReduction(self, elite=False):
        self.isDamageReduction = 0

    def makeAngry(self, elite=False):
        self.isAngry = 1
        self.isShielding = 0

    def makeUnShielding(self, elite=False):
        self.isShielding = 0

    def makeShielding(self, elite=False):
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
            if self.style.body == 'a' and not self.style.name == 'bg' and not self.style.name == 'cg':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                             self.style.dept)
                for headPart in self.headParts:
                    headPart.setTexture(texture, 1)
            if self.style.body == 'b':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                             self.style.dept)
                for headPart in self.headParts:
                    headPart.setTexture(texture, 1)
            if self.style.body == 'c':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                             self.style.dept)
                for headPart in self.headParts:
                    headPart.setTexture(texture, 1)
        elif self.style.name == 'mdm':
            self.setSuitClothes()
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_insider%s.png' % (
                '_exe' if self.isExecutive or self.isGovernaught else '',))
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
        elif self.style.name == 'tld':
            self.setSuitClothes()
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_headhoncho%s.png' % (
                '_exe' if self.isExecutive or self.isGovernaught else '',))
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
        elif self.style.name == 'ca':
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
            if self.style.body == 'a' and self.style.name == 'blr' or self.style.name == 'dsk':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                             self.style.dept)
            if self.style.body == 'a' and not self.style.name == 'ts' and not self.style.name == 'kb' and not self.style.name == 'dsk' and not self.style.name == 'blr' \
                and not self.style.name == 'lbs' and not self.style.name == 'bg' and not self.style.name == 'cg' and not self.style.name == 'jl' and not self.style.name == 'gb' and not self.style.name == 'fb' and not self.style.name == 'tcc':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                             self.style.dept)
                for headPart in self.headParts:
                    headPart.setTexture(texture, 1)
                modelRoot.find('**/body').setTexture(texture, 1)
                modelRoot.find('**/necktie-s').setTexture(texture, 1)
                modelRoot.find('**/necktie-w').setTexture(texture, 1)
                modelRoot.find('**/bowtie').setTexture(texture, 1)
            if self.style.body == 'b' and not self.style.name == 'lbs' and not self.style.name == 'jl' and not self.style.name == 'gb' and not self.style.name == 'fb' and not self.style.name == 'tcc':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                             self.style.dept)
                for headPart in self.headParts:
                    headPart.setTexture(texture, 1)
                modelRoot.find('**/body').setTexture(texture, 1)
                modelRoot.find('**/necktie-s').setTexture(texture, 1)
                modelRoot.find('**/necktie-w').setTexture(texture, 1)
                modelRoot.find('**/bowtie').setTexture(texture, 1)
            if self.style.body == 'c' and self.style.name == 'fd' or self.style.name == 'nar':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                             self.style.dept)
                modelRoot.find('**/body').setTexture(texture, 1)
                modelRoot.find('**/necktie-s').setTexture(texture, 1)
                modelRoot.find('**/necktie-w').setTexture(texture, 1)
                modelRoot.find('**/bowtie').setTexture(texture, 1)
            if self.style.body == 'c' and not self.style.name == 'fd' and not self.style.name == 'nar' and not self.style.name == 'lbs' and not self.style.name == 'jl' and not self.style.name == 'gb' and not self.style.name == 'fb' and not self.style.name == 'tcc':
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
        elif self.style.name == 'mdm':
            self.setSuitClothes()
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_insider%s.png' % (
                '_gov' if self.isExecutive or self.isGovernaught else '',))
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
        elif self.style.name == 'tld':
            self.setSuitClothes()
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_headhoncho%s.png' % (
                '_gov' if self.isExecutive or self.isGovernaught else '',))
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
        elif self.style.name == 'ca':
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

    def makeInsured(self):
        self.isInsured= 1

    def removeInsured(self):
        self.isInsured = 0

    def makeIntoPhase3(self):
        self.isPhase3 = 1

    def removePhase3(self):
        self.isPhase3 = 0

    def makeLitigationManager(self):
        self.isLitigationManager = 1

    def makeIntoEnraged(self):
        self.loop('neutral-enraged')
        self.isEnraged = 1

    def removeEnraged(self):
        self.isEnraged = 0

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
        if self.style.name == 'bg':
            loadDialog(1)
            return SkelecogDialogArray
        if self.style.name == 'msr' and not self.isSkeleton:
            loadDialog(1)
            return DerrickManDialogArray
        if self.style.name == 'kb' and not self.isSkeleton:
            loadDialog(1)
            return DerrickHandDialogArray
        if self.style.name == 'kb' and self.isSkeleton:
            loadDialog(1)
            return DerrickSkeleDialogArray
        if self.style.name == 'tc' and not self.isSkeleton:
            loadDialog(1)
            return FirestarterDialogArray
        if self.style.name == 'tg' and not self.isSkeleton:
            loadDialog(1)
            return FeatherbedderDialogArray
        if self.style.name == 'tb' and not self.isSkeleton:
            loadDialog(1)
            return MajorPlayerDialogArray
        if self.style.name == 'ts' and not self.isSkeleton:
            loadDialog(1)
            return MajorPlayerDialogArray
        if self.style.name == 'adc' and not self.isSkeleton:
            loadDialog(1)
            return ChainsawDialogArray
        if self.style.name == 'drm' and not self.isSkeleton:
            loadDialog(1)
            return ChainsawORDialogArray
        if self.style.name == 'cp' and not self.isSkeleton:
            loadDialog(1)
            return DOLADialogArray
        if self.style.name == 'fbd' and not self.isSkeleton:
            loadDialog(1)
            return CaseManagerDialogArray
        if self.style.name == 'frs' and not self.isSkeleton:
            loadDialog(1)
            return StenographerDialogArray
        if self.style.name == 'gtk' and not self.isSkeleton:
            loadDialog(1)
            return PrethinkerDialogArray
        if self.style.name == 'gtk' and self.isSkeleton:
            loadDialog(1)
            return PrethinkerDialogArray
        if self.style.name == 'hh' and not self.isSkeleton:
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'phs' and not self.isSkeleton:
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'le' and not self.isSkeleton:
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'cfp' and not self.isSkeleton:
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'ggm' and not self.isSkeleton:
            loadDialog(1)
            return MouthpieceDialogArray
        if self.style.name == 'whunter' and not self.isSkeleton:
            loadDialog(1)
            return WitchHunterDialogArray
        if self.style.name == 'tr' and not self.isSkeleton:
            loadDialog(1)
            return CountErfitDialogArray
        if self.style.name == 'th' and not self.isSkeleton:
            loadDialog(1)
            return RainmakerDialogArray
        if self.style.name == 'mp' and not self.isSkeleton:
            loadDialog(1)
            return ReddDialogArray
        if self.style.name == 'scg' and not self.isSkeleton:
            loadDialog(1)
            return ScapegoatDialogArray
        if self.style.name == 'csm' and not self.isSkeleton:
            loadDialog(1)
            return CaseManagerDialogArray
        if self.style.name == 'ste' and not self.isSkeleton:
            loadDialog(1)
            return StenographerDialogArray
        if self.style.name == 'lit' and not self.isSkeleton:
            loadDialog(1)
            return LitigatorDialogArray
        if self.style.name == 'rb' and not self.isSkeleton:
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'tlr' and not self.isSkeleton:
            loadDialog(1)
            return CLODialogArray
        if self.style.name == 'tlr' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'cvy' and not self.isSkeleton:
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'bdb' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'bdb' and not self.isSkeleton:
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'jdg' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'jdg' and not self.isSkeleton:
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'isw' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'isw' and not self.isSkeleton:
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'mes' and not self.isSkeleton:
            loadDialog(1)
            return DuckShufflerDialogArray
        if self.style.name == 'dm' and not self.isSkeleton:
            loadDialog(1)
            return TreekillerDialogArray
        if self.style.name == 'trk' and not self.isSkeleton:
            loadDialog(1)
            return PlutocratDialogArray
        if self.style.name == 'dsf' and not self.isSkeleton:
            loadDialog(1)
            return HighRollerDialogArray
        if self.style.name == 'mad' and not self.isSkeleton:
            loadDialog(1)
            return HighRollerDialogArray
        if self.style.name == 'crf' and not self.isSkeleton:
            loadDialog(1)
            return HighRollerDialogArray
        if self.style.name == 'gh' and not self.isSkeleton:
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'ssm' and not self.isSkeleton:
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'nar':
            loadDialog(1)
            return DOPRDialogArray
        if self.style.name == 'fd':
            loadDialog(1)
            return DOPADialogArray
        if self.style.name == 'fm' and not self.isSkeleton:
            loadDialog(1)
            return BellringerDialogArray
        if self.style.name == 'msp' and not self.isSkeleton:
            loadDialog(1)
            return CountErfitDialogArray
        if self.style.name == 'prethink' and not self.isSkeleton:
            loadDialog(1)
            return PrethinkerDialogArray
        if self.style.name == 'jr' and not self.isSkeleton:
            loadDialog(1)
            return MultislackerDialogArray
        if self.style.name == 'prr' and not self.isSkeleton:
            loadDialog(1)
            return PacesetterDialogArray
        if self.style.name == 'blr':
            loadDialog(1)
            return DOPADialogArray
        if self.style.name == 'dvp' and not self.isSkeleton:
            loadDialog(1)
            return RainmakerDialogArray
        if self.style.name == 'dsk':
            loadDialog(1)
            return DOPRDialogArray
        if self.style.name == 'ffm' and not self.isSkeleton:
            loadDialog(1)
            return DOLDDialogArray
        if self.style.name == 'sft' and not self.isSkeleton:
            loadDialog(1)
            return PacesetterDialogArray
        if self.style.name == 'dty' and not self.isSkeleton:
            loadDialog(1)
            return DeepDiverDialogArray
        if self.style.name == 'dfg' and not self.isSkeleton:
            loadDialog(1)
            return GatekeeperDialogArray
        if self.style.name == 'dfr' and not self.isSkeleton:
            loadDialog(1)
            return DOLADialogArray
        if self.style.name == 'bsh' and not self.isSkeleton:
            loadDialog(1)
            return DOLDDialogArray
        if self.style.name == 'ghd' and not self.isSkeleton:
            loadDialog(1)
            return WitchHunterDialogArray
        if self.style.name == 'tyh' and not self.isSkeleton:
            loadDialog(1)
            return StenographerDialogArray
        if self.style.name == 'jgd' and not self.isSkeleton:
            loadDialog(1)
            return FeatherbedderDialogArray
        if self.style.name == 'bby' and not self.isSkeleton:
            loadDialog(1)
            return ChairmanDialogArray
        if self.style.name == 'dvk' and not self.isSkeleton:
            loadDialog(1)
            return ReddDialogArray
        if self.style.name == 'otm' and not self.isSkeleton:
            loadDialog(1)
            return OttomanDialogArray
        if self.style.name == 'cry' and not self.isSkeleton:
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
        if self.style.name == 'tcm' and not self.isSkeleton:
            loadDialog(1)
            return ChairmanDialogArray
        if self.style.name == 'cm' and not self.isSkeleton:
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'cm' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'dfh' and not self.isSkeleton:
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'dfh' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'hh' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'frs' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'le' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'cfp' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'th' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'ste' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'ggm' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'rb' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'cvy' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'gh' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'ssm' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'dvp' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'cry' and self.isSkeleton:
            loadDialog(1)
            return SkelecogDialogFemaleArray
        if self.style.name == 'tyh' and self.isSkeleton:
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