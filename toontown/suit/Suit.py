from direct.actor import Actor
from direct.directnotify import DirectNotifyGlobal
from otp.avatar import Avatar
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
AllSuits = (('walk', 'walk'), ('run', 'walk'), ('neutral', 'neutral'), ('wrecked', 'wrecked'), ('lose3', 'wrecked'),  ('headless-death', 'headless-death'))
AllSuitsMinigame = (('victory', 'victory'),
 ('flail', 'flailing'),
 ('tug-o-war', 'tug-o-war'),
 ('slip-backward', 'slip-backward'),
('lose3', 'wrecked'),
 ('slip-forward', 'slip-forward'))
AllSuitsTutorialBattle = (('lose', 'lose'), ('lose2', 'headless-death'), ('wrecked', 'wrecked'), ('lose3', 'wrecked'), ('dance', 'song-and-dance'),  ('pie-small-react', 'pie-small'), ('squirt-small-react', 'squirt-small'))
AllSuitsBattle = (('drop-react', 'anvil-drop'),
 ('flatten', 'drop'),
('headless-death', 'headless-death'),
('dance', 'song-and-dance'),
('lose3', 'wrecked'),
('wrecked', 'wrecked'),
 ('sidestep-left', 'sidestep-left'),
 ('sidestep-right', 'sidestep-right'),
 ('squirt-large-react', 'squirt-large'),
                  ('sound-react', 'sound-react'),
 ('landing', 'landing'),
 ('reach', 'walknreach'),
 ('rake-react', 'rake'),
 ('hypnotized', 'hypnotize'),
 ('shock', 'shock'),
 ('soak', 'soak'),
 ('lured', 'lured'))
SuitsCEOBattle = (('sit', 'sit'),
 ('sit-eat-in', 'sit-eat-in'),
 ('sit-eat-loop', 'sit-eat-loop'),
 ('sit-eat-out', 'sit-eat-out'),
('lose3', 'wrecked'),
 ('sit-angry', 'sit-angry'),
 ('sit-hungry-left', 'leftsit-hungry'),
 ('sit-hungry-right', 'rightsit-hungry'),
 ('sit-lose', 'sit-lose'),
 ('tray-walk', 'tray-walk'),
 ('tray-neutral', 'tray-neutral'),
 ('sit-lose', 'sit-lose'),
                  ('headless-death', 'headless-death'))
f = (('throw-paper', 'throw-paper', 4), ('phone', 'phone', 4), ('lose3', 'wrecked', 4), ('shredder', 'shredder', 4))
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
 ('smile', 'smile', 4))
hh = (('speak', 'speak', 4),
 ('effort', 'effort', 4),
      ('lose3', 'wrecked', 4),
 ('magic1', 'magic1', 4),
 ('pen-squirt', 'fountain-pen', 4),
 ('finger-wag', 'finger-wag', 4))
cr = (('glower', 'glower', 4),
 ('finger-wag', 'finger-wag', 4),
      ('lose3', 'wrecked', 4),
 ('speak', 'speak', 4))
tbc = (('magic2', 'magic2', 4),
 ('throw-paper', 'throw-paper', 4),
       ('lose3', 'wrecked', 4),
 ('magic3', 'magic3', 4))
trb = (('magic1', 'magic1', 4),
 ('speak', 'speak', 4),
       ('finger-wag', 'finger-wag', 4),
       ('lose3', 'wrecked', 4),
 ('glower', 'glower', 4),
 ('magic3', 'magic3', 4))
dot = (('pen-squirt', 'fountain-pen', 4),
 ('glower', 'glower', 4),
 ('throw-paper', 'throw-paper', 4),
       ('lose3', 'wrecked', 4),
 ('magic1', 'magic1', 4),
 ('magic3', 'magic3', 4),
 ('roll-o-dex', 'roll-o-dex', 4))
dvg = (('glower', 'glower', 4),
 ('magic2', 'magic2', 4),
       ('lose3', 'wrecked', 4),
       ('golf-club-swing', 'golf-club-swing', 4),
 ('quick-jump', 'jump', 4))
cpl = (('glower', 'glower', 4),
 ('throw-paper', 'throw-paper', 4),
       ('lose3', 'wrecked', 4),
       ('throw-object', 'throw-object', 4),
 ('pickpocket', 'pickpocket', 4))
bkp = (('glower', 'glower', 4),
 ('magic2', 'magic2', 4),
       ('magic1', 'magic1', 4),
       ('lose3', 'wrecked', 4),
 ('cigar-smoke', 'cigar-smoke', 4))
kpn = (('glower', 'glower', 4),
 ('golf-club-swing', 'golf-club-swing', 4),
       ('lose3', 'wrecked', 4),
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
('magic3', 'magic3', 4),
      ('lose3', 'wrecked', 4),
      ('frustrated', 'frustrated', 4),
      ('golf-club-swing', 'golf-club-swing', 4),
      ('song-and-dance', 'song-and-dance', 4),
('calculating-costs', 'calculating-costs', 4),
('cease', 'cease', 4),
      ('cigar-smoke', 'cigar-smoke', 4),
       ('throw-paper', 'throw-paper', 4))
msr = (('magic1', 'magic1', 4),
      ('glower', 'glower', 4),
('magic3', 'magic3', 4),
       ('lose3', 'wrecked', 4),
      ('frustrated', 'frustrated', 4),
      ('golf-club-swing', 'golf-club-swing', 4),
      ('song-and-dance', 'song-and-dance', 4),
('calculating-costs', 'calculating-costs', 4),
('cease', 'cease', 4),
      ('cigar-smoke', 'cigar-smoke', 4),
       ('sanction', 'sanction', 4),
       ('pickpocket', 'sanction', 4))
kb = (('pen-squirt', 'fountain-pen', 4),
      ('quick-jump', 'jump', 4),
      ('pickpocket', 'sanction', 4),
      ('magic1', 'magic1', 4),
      ('lose3', 'wrecked', 4),
      ('layoffs', 'layoffs', 4),
('summon', 'summon', 4),
('speak', 'speak', 4),
       ('cease', 'cease', 4),
('calculating-costs', 'calculating-costs', 4),
('cease', 'cease', 4),
       ('magic3', 'magic3', 4),
       ('snap', 'snap', 4),
('throw-paper', 'throw-paper', 4),
 ('throw-object', 'throw-object', 4),
      ('glower', 'glower', 4),
      ('sanction', 'sanction', 4),
('cease', 'cease', 4),
      ('song-and-dance', 'song-and-dance', 4),
      ('cigar-smoke', 'cigar-smoke', 4))
ts = (('quick-jump', 'jump', 4),
      ('pickpocket', 'sanction', 4),
('summon', 'summon', 4),
('speak', 'speak', 4),
      ('lose3', 'wrecked', 4),
       ('cease', 'cease', 4),
      ('magic1', 'magic1', 4),
       ('snap', 'snap', 4),
('calculating-costs', 'calculating-costs', 4),
('cease', 'cease', 4),
('layoffs', 'layoffs', 4),
       ('magic3', 'magic3', 4),
       ('snap', 'snap', 4),
('throw-paper', 'throw-paper', 4),
 ('throw-object', 'throw-object', 4),
      ('glower', 'glower', 4),
      ('sanction', 'sanction', 4),
('cease', 'cease', 4),
      ('song-and-dance', 'song-and-dance', 4),
      ('cigar-smoke', 'cigar-smoke', 4))
tc = (('quick-jump', 'jump', 4),
      ('pickpocket', 'sanction', 4),
('throw-paper', 'throw-paper', 4),
 ('throw-object', 'throw-object', 4),
      ('lose3', 'wrecked', 4),
      ('defense', 'scabbard', 4),
      ('magic1', 'magic1', 4),
      ('glower', 'glower', 4),
      ('magic2', 'magic2', 4),
      ('pen-squirt', 'fountain-pen', 4),
      ('sanction', 'sanction', 4))
tg = (('golf-club-swing', 'golf-club-swing', 4),
      ('cigar-smoke', 'cigar-smoke', 4),
      ('magic1', 'magic1', 4),
      ('glower', 'glower', 4),
      ('speak', 'speak', 4),
      ('lose3', 'wrecked', 4),
      ('song-and-dance', 'song-and-dance', 4),
      ('cigar-smoke', 'firestarter-cigar-smoke', 4),
      ('sanction', 'sanction', 4))
tb = (('quick-jump', 'jump', 4),
      ('effort', 'wheelspin', 4),
      ('deadwood', 'song-and-dance', 4),
('summon', 'summon', 4),
      ('pickpocket', 'pickpocket', 4),
        ('magic3', 'magic3', 4),
('summon', 'summon', 4),
('calculating-costs', 'calculating-costs', 4),
('speak', 'speak', 4),
       ('cease', 'cease', 4),
      ('lose3', 'wrecked', 4),
('song-and-dance', 'song-and-dance', 4),
       ('cease2', 'cease2', 4),
        ('finger-wag', 'cease2', 4),
        ('magic2', 'magic2', 4),
        ('speak', 'speak', 5),
        ('sanction', 'sanction', 4),
('snap', 'snap', 4),
        ('neutral', 'rolled', 4))
adc = (('throw-object', 'throw-object', 4),
      ('throw-paper', 'throw-paper', 4),
        ('magic3', 'magic3', 4),
      ('defense', 'scabbard', 4),
      ('roll-o-dex', 'roll-o-dex', 4),
       ('lose3', 'wrecked', 4),
      ('magic1', 'layoffs', 4),
      ('glower', 'glower', 4),
      ('effort', 'magic3', 4),
('quick-jump', 'jump', 4),
      ('finger-wag', 'cease', 4),
      ('snap', 'snap', 4),
      ('revvedup', 'revvedup', 4),
      ('pickpocket', 'sanction', 4))
drm = (('throw-object', 'throw-object', 4),
      ('throw-paper', 'throw-paper', 4),
        ('magic3', 'magic3', 4),
      ('defense', 'scabbard', 4),
       ('lose3', 'wrecked', 4),
      ('roll-o-dex', 'roll-o-dex', 4),
      ('magic1', 'layoffs', 4),
      ('glower', 'glower', 4),
      ('effort', 'magic3', 4),
('quick-jump', 'jump', 4),
      ('finger-wag', 'cease', 4),
      ('snap', 'snap', 4),
      ('revvedup', 'revvedup', 4),
      ('pickpocket', 'sanction', 4))
cp = (('throw-object', 'throw-object', 4),
      ('throw-paper', 'throw-paper', 4),
       ('sanction', 'sanction', 4),
      ('layoffs', 'layoffs', 4),
      ('rage', 'frustrated', 4),
       ('magic3', 'magic3', 4),
    ('summon', 'summon', 4),
      ('lose3', 'wrecked', 4),
('speak', 'speak', 4),
('falling-knife', 'falling-knife', 4),
       ('cease', 'cease', 4),
('defense', 'scabbard', 4),
       ('cigar-smoke', 'cigar-smoke', 4),
       ('snap', 'snap', 4),
      ('glower', 'glower', 4),
      ('magic2', 'magic2', 4),
      ('pickpocket', 'sanction', 4),
('quick-jump', 'jump', 4),
('summon', 'summon', 4),
      ('speak', 'speak', 4),
      ('cease', 'cease', 4))
fbd = (('throw-object', 'throw-object', 4),
      ('throw-paper', 'throw-paper', 4),
       ('sanction', 'sanction', 4),
('summon', 'summon', 4),
       ('lose3', 'wrecked', 4),
    ('summon', 'summon', 4),
('speak', 'speak', 4),
       ('cease', 'cease', 4),
       ('roll-o-dex', 'roll-o-dex', 4),
('layoffs', 'layoffs', 4),
       ('glower', 'glower', 4),
       ('speak', 'speak', 4),
       ('pickpocket', 'sanction', 4),
       ('magic3', 'magic3', 4),
       ('cigar-smoke', 'firestarter-cigar-smoke', 4),
       ('effort', 'effort', 4),
('cease', 'cease', 4),
('falling-knife', 'falling-knife', 4),
('objection-in', 'cease2', 4),
('snap', 'snap', 4),
       ('magic2', 'magic2', 4),
      ('magic2', 'magic2', 4),
('quick-jump', 'jump', 4),
('deadwood', 'deadwood', 4),
      ('speak', 'speak', 4))
frs = (('magic3', 'magic3', 4),
('calculating-costs', 'calculating-costs', 4),
       ('magic2', 'magic2', 4),
    ('summon', 'summon', 4),
('speak', 'speak', 4),
       ('cease', 'cease', 4),
       ('sanction', 'sanction', 4),
('summon', 'summon', 4),
('deadwood', 'cease3', 4),
       ('finger-wag', 'cease3', 4),
('cease', 'cease3', 4),
       ('lose3', 'wrecked', 4),
('falling-knife', 'falling-knife', 4),
('snap', 'snap', 4),
('objection-in', 'cease3', 4),
       ('cease2', 'cease3', 4),
       ('phone', 'phone', 4),
       ('glower', 'glower', 4),
       ('speak', 'speak', 4))
gtk = (('throw-object', 'throw-object', 4),
      ('throw-paper', 'throw-paper', 4),
       ('sanction', 'sanction', 4),
       ('glower', 'glower', 4),
    ('summon', 'summon', 4),
('speak', 'speak', 4),
       ('lose3', 'wrecked', 4),
       ('cease', 'cease', 4),
('deadwood', 'deadwood', 4),
       ('magic3', 'magic3', 4),
('objection-in', 'cease', 4),
('falling-knife', 'falling-knife', 4),
('summon', 'summon', 4),
       ('pickpocket', 'pickpocket', 4),
('magic1', 'magic1', 4),
       ('effort', 'effort', 4),
       ('snap', 'snap', 4),
       ('frustrated', 'frustrated', 4),
      ('magic2', 'magic2', 4),
      ('speak', 'speak', 4),
      ('cease2', 'cease', 4))
cc = (('speak', 'speak', 4),
    ('glower', 'glower', 4),
      ('lose3', 'wrecked', 4),
    ('phone', 'phone', 4))
tm = (('speak', 'speak', 4),
 ('throw-paper', 'throw-paper', 4),
 ('pickpocket', 'pickpocket', 4),
 ('phone', 'phone', 4),
      ('lose3', 'wrecked', 4),
 ('roll-o-dex', 'roll-o-dex', 4),
 ('finger-wag', 'finger-wag', 4))
nd = (('speak', 'speak', 4),
 ('throw-paper', 'throw-paper', 4),
 ('pickpocket', 'pickpocket', 4),
('magic3', 'magic3', 4),
 ('phone', 'phone', 4),
      ('lose3', 'wrecked', 4),
 ('roll-o-dex', 'roll-o-dex', 4),
 ('finger-wag', 'finger-wag', 4))
gh = (('speak', 'speak', 4),
 ('smile', 'smile', 4),
 ('pickpocket', 'pickpocket', 4),
('throw-paper', 'throw-paper', 4),
 ('throw-object', 'throw-object', 4),
      ('lose3', 'wrecked', 4),
('magic3', 'magic3', 4),
 ('roll-o-dex', 'roll-o-dex', 4))
ms = (('speak', 'speak', 4),
 ('magic3', 'magic3', 4),
      ('lose3', 'wrecked', 4),
      ('phone', 'phone', 4),
 ('pickpocket', 'pickpocket', 4),
('glower', 'glower', 4),
('throw-paper', 'throw-paper', 4),
 ('throw-object', 'throw-object', 4),
('magic1', 'magic1', 4),
 ('roll-o-dex', 'roll-o-dex', 4))
tf = (('speak', 'speak', 4), ('pen-squirt', 'fountain-pen', 4), ('lose3', 'wrecked', 4), ('rubber-stamp', 'rubber-stamp', 4))
m = (('stomp', 'stomp', 4), ('quick-jump', 'jump', 4), ('lose3', 'wrecked', 4), ('phone', 'phone', 4), ('glower', 'glower', 4))
mh = (('effort', 'effort', 4),
 ('throw-paper', 'throw-paper', 4),
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
trm = (('phone', 'phone', 4),
 ('magic2', 'magic2', 4),
 ('cigar-smoke', 'cigar-smoke', 4),
       ('lose3', 'wrecked', 4),
 ('magic3', 'magic3', 4),
 ('glower', 'glower', 4))
ssm = (('speak', 'speak', 4),
 ('magic2', 'magic2', 4),
       ('lose3', 'wrecked', 4),
 ('golf-club-swing', 'golf-club-swing', 4))
isw = (('phone', 'phone', 4),
 ('glower', 'glower', 4),
       ('lose3', 'wrecked', 4),
 ('magic1', 'magic1', 4),
 ('song-and-dance', 'song-and-dance', 4))
ssr = (('smile', 'smile', 4),
 ('speak', 'speak', 4),
       ('lose3', 'wrecked', 4),
       ('cigar-smoke', 'cigar-smoke', 4),
 ('golf-club-swing', 'golf-club-swing', 4),
 ('song-and-dance', 'song-and-dance', 4))
fas = (('throw-paper', 'throw-paper', 4),
       ('magic2', 'magic2', 4),
       ('magic1', 'magic1', 4),
       ('lose3', 'wrecked', 4),
       ('magic3', 'magic3', 4),
       ('rage', 'rage', 4),
       ('speak', 'speak', 4))
mdr = (('throw-paper', 'throw-paper', 4),
       ('magic2', 'magic2', 4),
       ('magic1', 'magic1', 4),
       ('lose3', 'wrecked', 4),
       ('frustrated', 'frustrated', 4),
       ('magic3', 'magic3', 4),
       ('speak', 'speak', 4))
nar = (('throw-paper', 'throw-paper', 4),
       ('magic2', 'magic2', 4),
       ('lose3', 'wrecked', 4),
       ('magic1', 'magic1', 4),
       ('frustrated', 'frustrated', 4),
       ('magic3', 'magic3', 4),
       ('speak', 'speak', 4))
fd = (('glower', 'glower', 4),
        ('speak', 'speak', 4),
('summon', 'effort', 4),
('speak', 'speak', 4),
('calculating-costs', 'phone', 4),
('cease', 'mob-mentality', 4),
      ('lose3', 'wrecked', 4),
       ('cease', 'glower', 4),
        ('magic3', 'magic2', 4),
        ('throw-paper', 'throw-paper', 4),
        ('magic1', 'magic1', 4))
fm = (('glower', 'glower', 4),
        ('speak', 'speak', 4),
      ('lose3', 'wrecked', 4),
        ('magic3', 'magic2', 4),
        ('throw-paper', 'throw-paper', 4),
        ('magic1', 'magic1', 4))
th = (('magic1', 'magic1', 4),
        ('effort', 'effort', 4),
        ('glower', 'glower', 4),
        ('magic2', 'transformation', 4),
      ('lose3', 'wrecked', 4),
        ('pickpocket', 'rushjob', 4))
kc = (('pickpocket', 'sanction', 4),
        ('sanction', 'sanction', 4),
        ('speak', 'speak', 4),
      ('lose3', 'wrecked', 4),
        ('throw-object', 'throw-object', 4),
        ('throw-paper', 'throw-paper', 4),
        ('magic1', 'magic1', 4))
tr = (('glower', 'glower', 4),
        ('pickpocket', 'sanction', 4),
        ('sanction', 'sanction', 4),
        ('throw-object', 'throw-object', 4),
        ('throw-paper', 'throw-paper', 4),
      ('lose3', 'wrecked', 4),
        ('cease2', 'cease2', 4),
        ('magic3', 'magic3', 4),
      ('cease', 'cease', 4),
        ('magic1', 'magic1', 4))
prr = (('pickpocket', 'sanction', 4),
        ('sanction', 'sanction', 4),
       ('song-and-dance', 'song-and-dance', 4),
        ('glower', 'glower', 4),
('calculating-costs', 'calculating-costs', 4),
       ('lose3', 'wrecked', 4),
('cease2', 'cease2', 4),
('falling-knife', 'falling-knife', 4),
('cease', 'cease', 4),
('summon', 'summon', 4),
       ('frustrated', 'frustrated', 4),
       ('magic3', 'magic3', 4),
        ('throw-object', 'throw-object', 4),
        ('throw-paper', 'throw-paper', 4),
        ('magic1', 'magic1', 4),
('neutral', 'rolled', 4))
blr = (('throw-paper', 'throw-paper', 4),
('throw-object', 'throw-object', 4),
('defense', 'scabbard', 4),
('summon', 'summon', 4),
       ('lose3', 'wrecked', 4),
('calculating-costs', 'calculating-costs', 4),
   ('summon', 'summon', 4),
('speak', 'speak', 4),
       ('cease', 'cease', 4),
('effort', 'effort', 4),
('smile', 'smile', 4),
('falling-knife', 'falling-knife', 4),
       ('song-and-dance', 'song-and-dance', 4),
       ('roll-o-dex', 'roll-o-dex', 4),
('sanction', 'sanction', 4),
('deadwood', 'deadwood', 4),
('snap', 'snap', 4),
 ('glower', 'glower', 4),
       ('magic3', 'magic3', 4),
 ('magic1', 'magic1', 4))
dvp = (('magic3', 'magic3', 4),
       ('magic2', 'magic2', 4),
('summon', 'summon', 4),
('calculating-costs', 'calculating-costs', 4),
       ('magic1', 'magic1', 4),
('falling-knife', 'falling-knife', 4),
       ('cease', 'cease', 4),
       ('layoffs', 'layoffs', 4),
       ('lose3', 'wrecked', 4),
       ('glower', 'glower', 4),
   ('summon', 'summon', 4),
('speak', 'speak', 4),
       ('cease', 'cease', 4),
       ('finger-wag', 'cease2', 4),
       ('sanction', 'sanction', 4),
       ('pickpocket', 'sanction', 4),
       ('speak', 'speak', 4))
dsk = (('cigar-smoke', 'firestarter-cigar-smoke', 4),
       ('sanction', 'sanction', 4),
       ('magic3', 'magic3', 4),
('snap', 'snap', 4),
('glower', 'glower', 4),
       ('layoffs', 'layoffs', 4),
('deadwood', 'deadwood', 4),
       ('lose3', 'wrecked', 4),
('falling-knife', 'falling-knife', 4),
   ('summon', 'summon', 4),
('speak', 'speak', 4),
('calculating-costs', 'calculating-costs', 4),
       ('cease', 'cease', 4),
('frustrated', 'frustrated', 4),
('objection-in', 'cease2', 4),
('summon', 'summon', 4),
('quick-jump', 'jump', 4),
('cease', 'cease', 4),
       ('defense', 'scabbard', 4),
       ('throw-paper', 'throw-paper', 4),
       ('magic1', 'magic1', 4),
       ('magic2', 'magic2', 4))
ffm = (('cigar-smoke', 'firestarter-cigar-smoke', 4),
       ('magic2', 'magic2', 4),
('magic1', 'magic1', 4),
       ('magic3', 'magic3', 4),
       ('pickpocket', 'pickpocket', 4),
   ('summon', 'summon', 4),
('speak', 'speak', 4),
       ('lose3', 'wrecked', 4),
       ('cease', 'cease', 4),
('objection-in', 'cease2', 4),
('summon', 'summon', 4),
        ('throw-paper', 'throw-paper', 4),
('glower', 'glower', 4),
        ('speak', 'speak', 4),
        ('sanction', 'sanction', 4),
('cease', 'cease2', 4),
('objection-in', 'cease', 4),
        ('smile', 'smile', 4))
sft = (('glower', 'glower', 4),
    ('pickpocket', 'rushjob', 4),
      ('finger-wag', 'rushjob', 4),
      ('speak', 'speak', 4),
      ('magic3', 'magic3', 4),
    ('sanction', 'rushjob', 4),
       ('lose3', 'wrecked', 4),
    ('smile', 'smile', 4),
      ('neutral', 'pace', 4))
sc = (('throw-paper', 'throw-paper', 4), ('lose3', 'wrecked', 4), ('watercooler', 'watercooler', 4), ('pickpocket', 'pickpocket', 4))
pp = (('throw-paper', 'throw-paper', 4), ('lose3', 'wrecked', 4), ('glower', 'glower', 4), ('finger-wag', 'finger-wag', 4))
tw = (('throw-paper', 'throw-paper', 4), ('lose3', 'wrecked', 4), ('magic3', 'magic3', 4), ('throw-object', 'throw-object', 4), ('magic1', 'magic1', 4), ('speak', 'speak', 4))
bc = (('throw-paper', 'throw-paper', 4), ('lose3', 'wrecked', 4),
 ('glower', 'glower', 4),
 ('magic2', 'magic2', 4),
 ('finger-wag', 'finger-wag', 4))
nc = (('phone', 'phone', 4),
 ('glower', 'glower', 4), ('lose3', 'wrecked', 4),
 ('magic3', 'magic3', 4),
 ('pickpocket', 'pickpocket', 4))
mb = (('phone', 'phone', 4), ('hold-pencil', 'hold-pencil', 4), ('lose3', 'wrecked', 4), ('pickpocket', 'pickpocket', 4))
ls = (('phone', 'phone', 4), ('speak', 'speak', 4), ('smile', 'smile', 4), ('lose3', 'wrecked', 4), ('glower', 'glower', 4))
rb = (('phone', 'phone', 4), ('lose3', 'wrecked', 4), ('throw-object', 'throw-object', 4))
gm = (('phone', 'phone', 4),
      ('throw-paper', 'throw-paper', 4),
 ('glower', 'glower', 4), ('lose3', 'wrecked', 4),
 ('magic2', 'magic2', 4),
 ('pickpocket', 'pickpocket', 4))
ad = (('magic1', 'magic1', 4), ('glower', 'glower', 4), ('lose3', 'wrecked', 4), ('throw-paper', 'throw-paper', 4), ('throw-object', 'throw-object', 4))
cvy = (('watercooler', 'watercooler', 4),
('magic1', 'magic1', 4), ('lose3', 'wrecked', 4),
('magic2', 'magic2', 4),
 ('pickpocket', 'pickpocket', 4),
 ('throw-paper', 'throw-paper', 4))
ptr = (('magic1', 'magic1', 4), ('lose3', 'wrecked', 4), ('throw-paper', 'throw-paper', 4), ('throw-object', 'throw-object', 4), ('hold-pencil', 'hold-pencil', 4))
mld = (('watercooler', 'watercooler', 4),
('magic1', 'magic1', 4), ('lose3', 'wrecked', 4),
 ('pickpocket', 'pickpocket', 4),
 ('throw-paper', 'throw-paper', 4))
pht = (('cigar-smoke', 'cigar-smoke', 4), ('lose3', 'wrecked', 4), ('magic3', 'magic3', 4), ('pickpocket', 'pickpocket', 4), ('golf-club-swing', 'golf-club-swing', 4))
csh = (('magic3', 'magic2', 4), ('lose3', 'wrecked', 4),
       ('magic2', 'magic2', 4),
('phone', 'phone', 4),
('victory', 'victory', 4),
       ('magic1', 'magic1', 4),
       ('sanction', 'sanction', 4),
       ('pickpocket', 'sanction', 4))
bgr = (('magic3', 'magic2', 4),
       ('magic2', 'magic2', 4), ('lose3', 'wrecked', 4),
('phone', 'phone', 4),
('victory', 'victory', 4),
       ('magic1', 'magic1', 4),
       ('sanction', 'sanction', 4),
       ('pickpocket', 'sanction', 4))
mes = (('magic3', 'magic2', 4),
       ('magic2', 'magic2', 4),
('phone', 'phone', 4), ('lose3', 'wrecked', 4),
('victory', 'victory', 4),
       ('magic1', 'magic1', 4),
       ('sanction', 'sanction', 4),
       ('pickpocket', 'sanction', 4))
dm = (('effort', 'wheelspin', 4),
        ('sanction', 'sanction', 4),
        ('magic3', 'magic3', 4), ('lose3', 'wrecked', 4),
        ('finger-wag', 'cease2', 4),
        ('magic2', 'snap', 4),
        ('magic1', 'magic3', 5),
        ('pickpocket', 'sanction', 4))
tcc = (('mob-mentality', 'mob-mentality', 4),
      ('magic3', 'magic2', 4), ('lose3', 'wrecked', 4),
      ('magic2', 'magic2', 4),
      ('watercooler', 'watercooler', 4),
      ('magic1', 'magic1', 4),
      ('glower', 'glower', 4))
fb = (('throw-paper', 'throw-paper', 4),
       ('defense', 'defense', 4), ('lose3', 'wrecked', 4),
       ('hold-eraser', 'hold-eraser', 4),
       ('throw-object', 'throw-object', 4),
        ('mob-mentality', 'mob-mentality', 4),
       ('magic1', 'magic1', 4))
jl = (('throw-paper', 'throw-paper', 4),
        ('throw-object', 'throw-paper', 4),
       ('magic3', 'magic2', 4), ('lose3', 'wrecked', 4),
        ('mob-mentality', 'mob-mentality', 4),
       ('magic1', 'magic1', 4))
gb = (('magic1', 'rake', 4),
        ('mob-mentality', 'mob-mentality', 4),
        ('throw-object', 'throw-object', 4),
('pickpocket', 'pickpocket', 4), ('lose3', 'wrecked', 4),
        ('magic2', 'magic2', 4),
        ('magic3', 'magic3', 4),
('defense', 'scabbard', 4),
        ('sanction', 'sanction', 4),
        ('throw-paper', 'throw-paper', 4))
lbs = (('throw-paper', 'throw-paper', 4),
       ('throw-object', 'throw-object', 4),
       ('magic1', 'magic1', 4), ('lose3', 'wrecked', 4),
       ('defense', 'scabbard', 4),
       ('mob-mentality', 'mob-mentality', 4),
       ('quick-jump', 'jump', 4),
       ('glower', 'glower', 4),
       ('sanction', 'sanction', 4),
       ('pickpocket', 'sanction', 4))
trk = (('magic1', 'magic1', 4),
        ('effort', 'effort', 4),
('pickpocket', 'pickpocket', 4), ('lose3', 'wrecked', 4),
        ('glower', 'glower', 4),
      ('mob-mentality', 'mob-mentality', 4),
        ('throw-object', 'throw-paper', 4),
        ('magic3', 'magic2', 4),
         ('throw-paper', 'throw-paper', 4),
        ('cigar-smoke', 'plutocrat-cigar-smoke', 4))
dsf = (('cigar-smoke', 'cigar-smoke', 4),
 ('glower', 'glower', 4), ('lose3', 'wrecked', 4),
 ('golf-club-swing', 'golf-club-swing', 4),
 ('magic1', 'magic1', 4))
msp = (('effort', 'wheelspin', 4),
        ('sanction', 'sanction', 4),
        ('magic3', 'shot5', 4),
('falling-knife', 'falling-knife', 4),
('summon', 'summon', 4), ('lose3', 'wrecked', 4),
       ('cease', 'cease', 4),
('snap', 'snap', 4),
('song-and-dance', 'shot5', 4),
        ('finger-wag', 'cease', 4),
        ('snap', 'snap', 4),
        ('magic1', 'magic1', 4),
        ('pickpocket', 'sanction', 4),
        ('neutral', 'rolled', 4))
mad = (('magic3', 'magic3', 4),
       ('effort', 'scabbard', 4),
        ('mob-mentality', 'mob-mentality', 4),
       ('magic1', 'magic1', 4),
       ('glower', 'glower', 4),
('snap', 'snap', 4), ('lose3', 'wrecked', 4),
('defense', 'scabbard', 4),
('summon', 'summon', 4),
('objection-in', 'cease2', 4),
('speak', 'speak', 4),
       ('cease', 'cease', 4),
('falling-knife', 'falling-knife', 4),
('summon', 'summon', 4),
       ('pickpocket', 'pickpocket', 4),
       ('smile', 'smile', 4),
('deadwood', 'deadwood', 4),
('song-and-dance', 'song-and-dance', 4),
       ('sanction', 'sanction', 4),
('revvedup', 'revvedup', 4),
('cease', 'cease2', 4),
       ('pickpocket', 'sanction', 4),
('defense', 'scabbard', 4),
       ('neutral', 'rolled', 4))
crf = (('effort', 'wheelspin', 4),
        ('sanction', 'sanction', 4),
('wheelspin', 'wheelspin', 4),
        ('magic3', 'shot5', 4),
('summon', 'summon', 4), ('lose3', 'wrecked', 4),
       ('cease', 'cease', 4),
('snap', 'snap', 4),
('falling-knife', 'falling-knife', 4),
('summon', 'summon', 4),
('speak', 'speak', 4),
       ('cease', 'cease', 4),
('song-and-dance', 'shot5', 4),
        ('finger-wag', 'cease', 4),
        ('snap', 'snap', 4),
        ('magic1', 'magic1', 4),
        ('pickpocket', 'sanction', 4),
        ('neutral', 'rolled', 4))
bf = (('speak', 'speak', 4),
 ('throw-object', 'throw-object', 4),
 ('hold-pencil', 'hold-pencil', 4), ('lose3', 'wrecked', 4),
 ('finger-wag', 'finger-wag', 4))
b = (('magic1', 'magic1', 4),
 ('throw-paper', 'throw-paper', 4),
     ('throw-object', 'throw-object', 4), ('lose3', 'wrecked', 4),
 ('pickpocket', 'pickpocket', 4))
dt = (('speak', 'speak', 4),
 ('throw-object', 'throw-object', 4), ('lose3', 'wrecked', 4),
 ('hold-pencil', 'hold-pencil', 4),
 ('finger-wag', 'finger-wag', 4))
ac = (('rubber-stamp', 'rubber-stamp', 4), ('lose3', 'wrecked', 4),
      ('throw-paper', 'throw-paper', 4),
 ('speak', 'speak', 4),
 ('roll-o-dex', 'roll-o-dex', 4))
bs = (('throw-paper', 'throw-paper', 4),
 ('speak', 'speak', 4), ('lose3', 'wrecked', 4),
 ('roll-o-dex', 'roll-o-dex', 4))
sd = (('magic2', 'magic2', 4),
 ('quick-jump', 'jump', 4), ('lose3', 'wrecked', 4),
 ('magic3', 'magic3', 4),
 ('hold-pencil', 'hold-pencil', 4))
le = (('pen-squirt', 'fountain-pen', 4),
      ('rubber-stamp', 'rubber-stamp', 4), ('lose3', 'wrecked', 4),
 ('phone', 'phone', 4),
 ('speak', 'speak', 4))
bw = (('magic1', 'magic1', 4),
      ('throw-paper', 'throw-paper', 4),
      ('pickpocket', 'pickpocket', 4), ('lose3', 'wrecked', 4),
      ('finger-wag', 'fingerwag', 4))
brv = (('shredder', 'shredder', 4),
    ('magic1', 'magic1', 4),
    ('watercooler', 'watercooler', 4), ('lose3', 'wrecked', 4),
    ('glower', 'glower', 4))
sb = (('magic2', 'magic2', 4),
 ('quick-jump', 'jump', 4),
 ('magic3', 'magic3', 4), ('lose3', 'wrecked', 4),
 ('hold-pencil', 'hold-pencil', 4))
cfp = (('magic1', 'magic1', 4),
      ('throw-paper', 'throw-paper', 4), ('lose3', 'wrecked', 4),
      ('hold-eraser', 'hold-eraser', 4))
arb = (('speak', 'speak', 4),
 ('throw-object', 'throw-object', 4), ('lose3', 'wrecked', 4),
 ('glower', 'glower', 4))
sjg = (('quick-jump', 'jump', 4),
        ('throw-paper', 'throw-paper', 4), ('lose3', 'wrecked', 4),
('throw-object', 'throw-object', 4),
        ('glower', 'glower', 4))
lsc = (('finger-wag', 'fingerwag', 4),
 ('cigar-smoke', 'cigar-smoke', 4), ('lose3', 'wrecked', 4),
 ('magic1', 'magic1', 4),
 ('throw-object', 'throw-object', 4))
jdg = (('magic3', 'magic3', 4),
       ('cease2', 'cease2', 4), ('lose3', 'wrecked', 4),
       ('phone', 'phone', 4),
       ('cease', 'cease', 4),
       ('finger-wag', 'cease', 4),
       ('pickpocket', 'sanction', 4),
       ('sanction', 'sanction', 4),
       ('speak', 'speak', 4))
jur = (('magic2', 'magic2', 4),
       ('objection-in', 'objection-in', 4), ('lose3', 'wrecked', 4),
       ('objection-out', 'objection-out', 4),
        ('quick-jump', 'jump', 4),
       ('magic3', 'magic3', 4),
       ('throw-object', 'throw-object', 5),
       ('throw-paper', 'throw-paper', 5),
       ('magic1', 'magic1', 4))
tlr = (('magic2', 'magic2', 4),
       ('objection-in', 'objection-in', 4), ('lose3', 'wrecked', 4),
       ('objection-out', 'objection-out', 4),
        ('quick-jump', 'jump', 4),
       ('magic3', 'magic3', 4),
       ('throw-object', 'throw-object', 5),
       ('throw-paper', 'throw-paper', 5),
       ('magic1', 'magic1', 4))
cm = (('magic2', 'snap', 4),
      ('bellow', 'bellow', 4), ('lose3', 'wrecked', 4),
      ('glower', 'glower', 4),
      ('magic1', 'magic1', 4),
      ('magic3', 'snap', 4),
      ('throw-object', 'throw-object', 4),
      ('throw-paper', 'throw-paper', 4))
ggm = (('magic2', 'snap', 4),
       ('sanction', 'sanction', 4),
       ('defense', 'scabbard', 4), ('lose3', 'wrecked', 4),
       ('magic3', 'snap', 4),
       ('pickpocket', 'sanction', 4),
       ('throw-object', 'throw-object', 5),
       ('throw-paper', 'throw-paper', 5),
       ('magic1', 'magic1', 4))
jb = (('magic1', 'magic1', 4), ('lose3', 'wrecked', 4),
        ('magic2', 'magic2', 4),
        ('throw-paper', 'throw-paper', 4))
jg = (('pickpocket', 'rushjob', 4),
        ('sanction', 'rushjob', 4),
        ('effort', 'effort', 4), ('lose3', 'wrecked', 4),
        ('magic3', 'magic3', 4),
        ('magic2', 'magic2', 4),
        ('speak', 'speak', 4))
jr = (('throw-paper', 'throw-paper', 4),
      ('magic1', 'magic1', 4),
      ('defense', 'scabbard', 4),
      ('magic3', 'magic3', 4), ('lose3', 'wrecked', 4),
      ('glower', 'glower', 4),
      ('sanction', 'sanction', 4),
      ('pickpocket', 'sanction', 4),
      ('song-and-dance', 'song-and-dance', 4),
      ('neutral', 'rolled', 4))
mp = (('cigar-smoke', 'cigar-smoke', 4),
 ('glower', 'glower', 4), ('lose3', 'wrecked', 4),
 ('golf-club-swing', 'golf-club-swing', 4),
 ('magic1', 'magic1', 4))
laa = (('glower', 'glower', 4),
        ('pickpocket', 'sanction', 4),
        ('sanction', 'sanction', 4), ('lose3', 'wrecked', 4),
('falling-knife', 'falling-knife', 4),
        ('throw-object', 'throw-object', 4),
        ('throw-paper', 'throw-paper', 4),
        ('cease2', 'cease2', 4),
        ('magic3', 'magic3', 4),
      ('cease', 'cease', 4),
        ('magic1', 'magic1', 4))
scg = (('stomp', 'stomp', 4),
('rage', 'rage', 4),
       ('throw-object', 'throw-object', 4),
       ('throw-paper', 'throw-paper', 4),
       ('finger-wag', 'finger-wag', 4),
       ('magic1', 'magic1', 4), ('lose3', 'wrecked', 4),
       ('speak', 'speak', 4),
       ('summon', 'objection-in', 4),
('magic2', 'magic2', 4),
       ('cease', 'objection-in', 4),
       ('defense', 'defense', 4),
       ('glower', 'glower', 4))
csm = (('throw-object', 'throw-object', 4),
       ('throw-paper', 'throw-paper', 4),
       ('effort', 'effort', 4), ('lose3', 'wrecked', 4),
       ('summon', 'summon', 4),
('calculating-costs', 'calculating-costs', 4),
('cease', 'cease', 4),
('objection-in', 'cease', 4),
('falling-knife', 'falling-knife', 4),
       ('speak', 'speak', 4),
       ('roll-o-dex', 'roll-o-dex', 4),
('sanction', 'sanction', 4),
        ('pen-squirt', 'fountain-pen', 4),
       ('magic1', 'magic1', 4))
ste = (('magic3', 'magic3', 4),
       ('cease2', 'cease3', 4),
       ('phone', 'phone', 4),
       ('summon', 'summon', 4),
('speak', 'speak', 4),
('calculating-costs', 'calculating-costs', 4),
       ('cease', 'cease3', 4),
       ('finger-wag', 'cease3', 4),
       ('pickpocket', 'sanction2', 4), ('lose3', 'wrecked', 4),
       ('sanction', 'sanction2', 4))
lit = (('magic2', 'magic2', 4),
      ('bellow', 'bellow', 4),
('speak', 'speak', 4),
      ('glower', 'glower', 4),
('summon', 'summon', 4),
       ('cease', 'cease', 4),
      ('magic1', 'magic1', 4), ('lose3', 'wrecked', 4),
      ('snap', 'snap', 4),
      ('throw-object', 'throw-object', 4),
      ('throw-paper', 'throw-paper', 4))
ca = (('pickpocket', 'pickpocket', 4),
 ('speak', 'speak', 4), ('lose3', 'wrecked', 4),
 ('throw-paper', 'throw-paper', 4),
 ('pen-squirt', 'fountain-pen', 4))
cn = (('speak', 'speak', 4),
 ('throw-paper', 'throw-paper', 4), ('lose3', 'wrecked', 4),
 ('effort', 'effort', 4),
 ('finger-wag', 'finger-wag', 4))
sw = (('pickpocket', 'pickpocket', 4),
 ('speak', 'speak', 4), ('lose3', 'wrecked', 4),
 ('throw-paper', 'throw-paper', 4),
 ('pen-squirt', 'fountain-pen', 4))
mdm = (('smile', 'smile', 4),
 ('roll-o-dex', 'roll-o-dex', 4),
       ('throw-paper', 'throw-paper', 4), ('lose3', 'wrecked', 4),
 ('magic3', 'magic3', 4))
txm = (('magic3', 'magic3', 4),
       ('pen-squirt', 'fountain-pen', 4),
 ('glower', 'glower', 4), ('lose3', 'wrecked', 4),
       ('magic1', 'magic1', 4),
       ('magic2', 'magic2', 4),
 ('magic1', 'magic1', 4))
mg = (('speak', 'speak', 4),
 ('glower', 'glower', 4), ('lose3', 'wrecked', 4),
 ('phone', 'phone', 5),
 ('throw-object', 'throw-object', 4),
 ('magic1', 'magic1', 4))
bfh =  (('pen-squirt', 'fountain-pen', 4),
 ('glower', 'glower', 4), ('lose3', 'wrecked', 4),
 ('magic1', 'magic1', 4))
hho = (('cigar-smoke', 'cigar-smoke', 4), ('lose3', 'wrecked', 4),
 ('throw-paper', 'throw-paper', 4),
 ('magic1', 'magic1', 4),
 ('magic2', 'magic2', 4),
 ('golf-club-swing', 'golf-club-swing', 5))
bdb = (('speak', 'speak', 4),
 ('glower', 'glower', 4),
 ('phone', 'phone', 5),
 ('throw-object', 'throw-object', 4), ('lose3', 'wrecked', 4),
 ('magic1', 'magic1', 4))
bgh = (('pen-squirt', 'fountain-pen', 4), ('lose3', 'wrecked', 4),
       ('throw-object', 'throw-object', 4),
       ('throw-paper', 'throw-paper', 4),
       ('magic1', 'magic1', 4),
('quick-jump', 'jump', 4),
('cigar-smoke', 'cigar-smoke', 4),
       ('magic3', 'magic3', 4),
       ('glower', 'glower', 4))
dfh = (('magic1', 'magic1', 4), ('lose3', 'wrecked', 4), ('throw-paper', 'throw-paper', 4), ('watercooler', 'watercooler', 4))
rng = (('speak', 'speak', 4), ('lose3', 'wrecked', 4),
 ('glower', 'glower', 4),
 ('phone', 'phone', 5),
 ('throw-object', 'throw-object', 4),
 ('magic1', 'magic1', 4))
cps = (('cigar-smoke', 'cigar-smoke', 4),
 ('glower', 'glower', 4),
('calculating-costs', 'calculating-costs', 4),
('cease', 'cease', 4),
('magic1', 'magic1', 4), ('lose3', 'wrecked', 4),
 ('magic2', 'magic2', 4))
tld = (('cigar-smoke', 'cigar-smoke', 4),
 ('glower', 'glower', 4),
('magic1', 'magic1', 4), ('lose3', 'wrecked', 4),
 ('magic2', 'magic2', 4))
gkp = (('pen-squirt', 'fountain-pen', 4),
       ('throw-object', 'throw-object', 4),
       ('throw-paper', 'throw-paper', 4),
('calculating-costs', 'calculating-costs', 4),
('cease', 'cease', 4),
       ('magic1', 'magic1', 4),
       ('magic3', 'magic3', 4), ('lose3', 'wrecked', 4),
       ('glower', 'glower', 4))
ddv = (('pen-squirt', 'fountain-pen', 4),
       ('throw-object', 'throw-object', 4), ('lose3', 'wrecked', 4),
       ('throw-paper', 'throw-paper', 4),
       ('magic1', 'magic1', 4),
('calculating-costs', 'calculating-costs', 4),
('cease', 'cease', 4),
('quick-jump', 'jump', 4),
('cigar-smoke', 'cigar-smoke', 4),
       ('magic3', 'magic3', 4),
       ('glower', 'glower', 4))
dty = (('pen-squirt', 'fountain-pen', 4),
       ('throw-object', 'throw-object', 4), ('lose3', 'wrecked', 4),
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
       ('magic1', 'magic1', 4), ('lose3', 'wrecked', 4),
       ('defense', 'defense', 4),
       ('glower', 'glower', 4))
bsh = (('magic2', 'snap', 4),
       ('sanction', 'sanction', 4), ('lose3', 'wrecked', 4),
       ('defense', 'scabbard', 4),
       ('quick-jump', 'jump', 4),
       ('summon', 'summon', 4),
('summon', 'summon', 4),
('calculating-costs', 'calculating-costs', 4),
('speak', 'speak', 4),
       ('cease', 'cease', 4),
('objection-in', 'cease2', 4),
('cease', 'cease', 4),
       ('pickpocket', 'sanction', 4),
       ('magic3', 'magic3', 4),
       ('throw-object', 'throw-object', 5),
       ('throw-paper', 'throw-paper', 5),
       ('magic1', 'magic1', 4))
ghd = (('pickpocket', 'pickpocket', 4),
        ('sanction', 'rushjob', 4),
       ('summon', 'effort', 4),
        ('phone', 'phone', 4),
       ('magic3', 'magic3', 4),
('falling-knife', 'falling-knife', 4),
       ('glower', 'glower', 4),
('defense', 'defense', 4),
('cease', 'objection-in', 4),
       ('objection-in', 'objection-in', 4),
       ('objection-out', 'objection-out', 4), ('lose3', 'wrecked', 4),
        ('snap', 'snap', 4),
        ('quick-jump', 'jump', 4),
        ('speak', 'speak', 4))
tyh = (('pickpocket', 'pickpocket', 4),
        ('sanction', 'sanction', 4),
       ('summon', 'summon', 4),
        ('phone', 'phone', 4),
       ('magic3', 'magic3', 4),
       ('glower', 'glower', 4),
('calculating-costs', 'calculating-costs', 4),
('falling-knife', 'falling-knife', 4),
('defense', 'defense', 4),
('cease', 'cease3', 4),
       ('cease2', 'cease3', 4),
       ('objection-out', 'objection-out', 4), ('lose3', 'wrecked', 4),
        ('snap', 'snap', 4),
        ('quick-jump', 'jump', 4),
        ('speak', 'speak', 4))
jgd = (('pickpocket', 'pickpocket', 4),
        ('sanction', 'sanction', 4),
       ('summon', 'summon', 4),
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
       ('objection-out', 'objection-out', 4), ('lose3', 'wrecked', 4),
        ('snap', 'snap', 4),
        ('quick-jump', 'jump', 4),
        ('speak', 'speak', 4))
dvk = (('throw-object', 'throw-object', 4),
      ('throw-paper', 'throw-paper', 4),
('layoffs', 'layoffs', 4), ('lose3', 'wrecked', 4),
('deadwood', 'deadwood', 4),
      ('defense', 'scabbard', 4),
      ('magic3', 'snap', 4),
       ('finger-wag', 'cease2', 4),
('falling-knife', 'falling-knife', 4),
      ('glower', 'glower', 4),
      ('speak', 'speak', 4))
otm = (('pickpocket', 'pickpocket', 4),
       ('magic1', 'magic1', 4),
 ('effort', 'effort', 4), ('lose3', 'wrecked', 4),
('glower', 'glower', 4),
      ('defense', 'defense', 4),
       ('layoffs', 'layoffs', 4),
('deadwood', 'deadwood', 4),
      ('throw-object', 'throw-object', 4),
      ('sanction', 'rushjob', 4),
       ('finger-wag', 'rushjob', 4),
('cease', 'come-on', 4),
 ('throw-paper', 'throw-paper', 4),
       ('song-and-dance', 'song-and-dance', 4),
 ('magic3', 'magic3', 4),
 ('throw-paper', 'throw-paper', 4))
cry = (('magic3', 'magic3', 4),
       ('phone', 'phone', 4),
('calculating-costs', 'calculating-costs', 4),
       ('finger-wag', 'cease3', 4),
       ('pickpocket', 'sanction', 4),
       ('sanction', 'sanction', 4), ('lose3', 'wrecked', 4),
       ('cease', 'cease3', 4),
       ('speak', 'speak', 4))
tcm = (('magic3', 'magic3', 4),
       ('golf-club-swing', 'golf-club-swing', 4),
('falling-knife', 'falling-knife', 4),
      ('pickpocket', 'sanction', 4),
      ('magic1', 'magic1', 4),
       ('snap', 'snap', 4),
       ('throw-paper', 'throw-paper', 4),
('layoffs', 'layoffs', 4), ('lose3', 'wrecked', 4),
('deadwood', 'deadwood', 4),
       ('throw-object', 'throw-object', 4),
       ('finger-wag', 'cease2', 4),
('cease', 'cease', 4),
      ('glower', 'glower', 4),
      ('sanction', 'sanction', 4),
      ('song-and-dance', 'song-and-dance', 4),
      ('cigar-smoke', 'cigar-smoke', 4),
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
        print 'Invalid suit name: ', suit
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
         'ttcc_ene_hroller_laugh',
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
                                   'ttcc_ene_ddiver_statement2',
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
    healthColors = (Vec4(0.169, 1, 0, 1),
        Vec4(0.5, 1, 0, 1),
        Vec4(0.75, 1, 0, 1),
        Vec4(1, 1, 0, 1),
        Vec4(1, 0.866, 0, 1),
        Vec4(1, 0.6, 0, 1),
        Vec4(1, 0.5, 0, 1),
        Vec4(1, 0.25, 0, 1.0),
        Vec4(1, 0, 0, 1),
        Vec4(1, 0, 0, 1),
	    Vec4(0, 0, 0, 1),
        Vec4(1, 0, 0, 1),
        Vec4(0.0, 1.0, 1.0, 1),  # overheal
        Vec4(0.741, 0, 1, 1))
    healthGlowColors = (Vec4(0.25, 1, 0.25, 0.5),
        Vec4(0.5, 1, 0.25, .5),
        Vec4(0.75, 1, 0.25, .5),
        Vec4(1, 1, 0.25, 0.5),
        Vec4(1, 0.866, 0.25, .5),
        Vec4(1, 0.6, 0.25, .5),
        Vec4(1, 0.5, 0.25, 0.5),
        Vec4(1, 0.25, 0.25, 0.5),
        Vec4(1, 0, 0, 0.5),
	    Vec4(1, 0, 0, 0.5),
        Vec4(0, 0, 0, 0.5),
        Vec4(1, 0, 0, 0),
        Vec4(0.0, 1.0, 1.0, 0.5),  # overheal
        Vec4(0.741, 0, 1, 0.5))
    medallionColors = {'c': Vec4(0.863, 0.776, 0.769, 1.0),
     's': Vec4(0.843, 0.745, 0.745, 1.0),
     'l': Vec4(0.749, 0.776, 0.824, 1.0),
     'm': Vec4(0.749, 0.769, 0.749, 1.0),
     'g': Vec4(0.863, 0.776, 0.769, 1.0)}

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
        self.healthBar = None
        self.healthCondition = 0
        self.isDisguised = 0
        self.isWaiter = 0
        self.isGovernaught = 0
        self.isExecutive = 0
        self.isManager = 0
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
        self.removeHealthBar()
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
        self.headColor = None
        self.headTexture = None
        self.loseActor = None
        self.zapActor = None
        self.isSkeleton = 0

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
            self.scale = 4.0 / aSize
            self.handColor = VBase4(0.749, 0.647, 0.518, 1)
            self.generateBody()
            self.generateHead('yesman')
            texture = loader.loadTexture('phase_4/maps/bookkeeper.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.generateHead('downsizerHat')
            self.setHeight(5.7)
        elif dna.name == 'mm':
            self.scale = 4.125 / aSize
            self.handColor = SuitDNA.corpPolyColor
            self.generateBody()
            self.generateHead('yesman')
            texture = loader.loadTexture('phase_4/maps/yes_man.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.28)
        elif dna.name == 'ds':
            self.scale = 4.75 / aSize
            self.handColor = (1, 0.839, 0.627, 1)
            self.generateFemaleBody()
            self.generateHead('numbercruncher')
            texture = loader.loadTexture('phase_3.5/maps/voodoo-programmer.png')
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
            self.scale = 5.5 / aSize
            self.handColor = VBase4(0.663, 0.631, 0.624, 1)
            self.generateBody()
            self.generateHead2('telemarketer')
            texture = loader.loadTexture('phase_4/maps/downsizer.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.headTexture = 'DS_hat.png'
            self.generateHead2('hatjp187187')
            self.setHeight(7.54)
        elif dna.name == 'tbc':
            self.scale = 4.5 / bSize
            self.handColor = VBase4(0.388, 0.388, 0.388, 1)
            self.generateBody()
            self.generateHead('beancounter')
            texture = loader.loadTexture('phase_4/maps/downsizer.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.08)
        elif dna.name == 'trb':
            self.scale = 6.0 / aSize
            self.handColor = VBase4(0.776, 0.757, 0.537, 1)
            self.generateBody()
            self.generateHead('bigwig')
            texture = loader.loadTexture('phase_4/maps/affiliate.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
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
            self.scale = 6.0 / aSize
            self.handColor = VBase4(0.749, 0.647, 0.518, 1)
            self.generateBody()
            self.generateHead('yesman')
            texture = loader.loadTexture('phase_4/maps/enforcer.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.5)
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
            self.scale = 6.5 / aSize
            self.handColor = VBase4(0.882, 0.894, 0.004, 1)
            self.generateBody()
            self.generateHead('toxicleader')
            texture = loader.loadTexture('phase_3.5/maps/skull.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.2)
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
            self.generateSkeletonBody()
            self.generateHead('autocaddie', animated=True)
            self.makeAutocaddie()
            self.isSkeleton = 1
            self.setHeight(6.0)
        elif dna.name == 'bg':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.608, 0.525, 0.431, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead('clubpresident', animated=True)
            self.setHeight(8.7)
        elif dna.name == 'msr':
            self.scale = 4.5 / aSize
            self.handColor = VBase4(0.816, 0.643, 0.537, 1)
            self.generateFemaleBody()
            self.makeExecutive()
            self.generateHead2('bossbotClubPresidentHead')
            self.generateHead2('bossbotClubPresidentEarrings')
            self.generateHead2('bossbotClubPresidentHair')
            self.setHeight(6.0)
        elif dna.name == 'kb':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead('derrickhand', animated=True)
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_derrickhand.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(9.0)
            self.setTransparency(1)
        elif dna.name == 'ts':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.generateSkeletonBody()
            self.generateHead('derrickhand_skele', animated=True)
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_derrickhand_skelecog.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(9.0)
            self.isSkeleton = 1
            self.makeAutocaddie()
            self.setTransparency(1)
        elif dna.name == 'tc':
            self.scale = 5.5 / aSize
            self.handColor = VBase4(0.612, 0.612, 0.612, 1)
            self.generateFemaleBody()
            self.makeGatekeeper()
            self.generateHead('gatekeeper', animated=True)
            self.setHeight(6.9)
        elif dna.name == 'tg':
            self.scale = 7.5 / aSize
            self.handColor = VBase4(0.894, 0.235, 0.043, 1)
            self.generateBody()
            self.makeFirestarter()
            self.generateHead('firestarter', animated=True)
            self.setHeight(10.5)
            self.setTransparency(1)
        elif dna.name == 'tb':
            self.scale = 7.3 / aSize
            self.handColor = VBase4(0.675, 0.584, 0.478, 1)
            self.generateBody()
            self.makeMajorPlayer()
            self.generateHead('majorplayer', animated=True)
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_majorplayer.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(10.0)
            self.setTransparency(1)
        elif dna.name == 'adc':
            self.scale = 4.5 / aSize
            self.handColor = VBase4(0.573, 0.384, 0.204, 1)
            self.generateBody()
            self.generateHead('derrickman', animated=True)
            self.setHeight(6.0)
        elif dna.name == 'drm':
            self.scale = 7.5 / aSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.generateBody()
            self.makeChainsaw()
            self.generateHead('chainsaw_b', animated=True)
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_chainsaw.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(11.0)
            self.setTransparency(1)
        elif dna.name == 'cp':
            self.scale = 5.5 / aSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead('circuitbreaker', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_circuitbreaker.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.5)
            self.setTransparency(1)
        elif dna.name == 'fbd':
            self.scale = 7.2 / aSize
            self.handColor = VBase4(0.784, 0.816, 0.847, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead('paperhands', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_paperhands.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(9.5)
            self.setTransparency(1)
        elif dna.name == 'frs':
            self.scale = 7.2 / aSize
            self.handColor = VBase4(0.682, 0.588, 0.482, 1)
            self.generateFemaleBody()
            self.makeExecutive()
            self.generateHead('mouthpiece', animated=True)
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
            self.generateHead('prethinker', animated=True)
            self.setHeight(9.1)
            self.setTransparency(1)
        elif dna.name == 'bf':
            self.scale = 4.2 / cSize
            self.handColor = SuitDNA.legalPolyColor
            self.generateBody()
            self.generateHead('bottom_feeder', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_bottom_feeder.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.6)
        elif dna.name == 'b':
            self.scale = 4.25 / bSize
            self.handColor = VBase4(1, 1, 1, 1)
            self.generateBody()
            self.generateHead('bloodsucker', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_bloodsucker.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.63)
        elif dna.name == 'dt':
            self.scale = 4.0 / bSize
            self.handColor = SuitDNA.legalPolyColor
            self.generateBody()
            self.generateHead('pettifogger', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_pettifogger.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.6)
        elif dna.name == 'ac':
            self.scale = 4.25 / aSize
            self.handColor = SuitDNA.legalPolyColor
            self.generateBody()
            self.generateHead('doubletalker', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_doubletalker.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(5.63)
        elif dna.name == 'bs':
            self.scale = 4.75 / aSize
            self.handColor = VBase4(0.318, 0.333, 0.431, 1)
            self.generateBody()
            self.generateBelt()
            self.generateHead('conveyancer', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_conveyancer.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            # self.generateHead2('belt')
            self.setHeight(6.4)
        elif dna.name == 'sd':
            self.scale = 4.2 / bSize
            self.handColor = SuitDNA.legalPolyColor
            self.generateBody()
            self.generateHead('ambulance_chaser', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_ambulance_chaser.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.1)
        elif dna.name == 'le':
            self.scale = 5.0 / cSize
            self.handColor = VBase4(0.255, 0.318, 0.549, 1)
            self.generateFemaleBody()
            self.generateHead('needlenose', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_needlenose.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.6)
        elif dna.name == 'bw':
            self.scale = 5.2 / aSize
            self.handColor = VBase4(0.647, 0.639, 0.788, 1)
            self.generateBody()
            self.generateHead('backstabber', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_backstabber.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.71)
        elif dna.name == 'brv':
            self.scale = 5.5 / cSize
            self.handColor = VBase4(0.098, 0.098, 0.153, 1)
            self.generateBody()
            self.generateHead('advocate', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_advocate.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.0)
        elif dna.name == 'sb':
            self.scale = 5.65 / bSize
            self.handColor = VBase4(0.678, 0.91, 0.808, 1)
            self.generateBody()
            self.generateHead('spin_doctor', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_spin_doctor.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.9)
        elif dna.name == 'cfp':
            self.scale = 5.65 / bSize
            self.handColor = VBase4(0.647, 0.639, 0.788, 1)
            self.generateFemaleBody()
            self.generateHead('shyster', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_shyster.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.4)
        elif dna.name == 'arb':
            self.scale = 6.8 / aSize
            self.handColor = VBase4(0.25, 0.25, 0.5, 1.0)
            self.generateBody()
            self.generateHead('legal_eagle', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_legal_eagle.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.57)
        elif dna.name == 'sjg':
            self.scale = 6.9 / aSize
            self.handColor = VBase4(1, 1, 1, 1)
            self.generateBody()
            self.generateHead('barrister', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_barrister.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.3)
        elif dna.name == 'lsc':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.573, 0.557, 0.761, 1)
            self.generateBody()
            self.generateHead('bigwig', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_big_wig.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.69)
        elif dna.name == 'jdg':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.584, 0.573, 0.671, 1)
            self.generateFemaleBody()
            self.makeExecutive()
            self.generateHead('clo', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_clo.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.7)
        elif dna.name == 'jur':
            self.scale = 7.2 / bSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.generateSkeletonBody()
            self.makeExecutive()
            self.setTransparency(1)
            self.setHeight(8.7)
        elif dna.name == 'tlr':
            self.scale = 6.4 / bSize
            self.handColor = VBase4(0.608, 0.678, 0.686, 1)
            self.generateFemaleBody()
            self.makeExecutive()
            self.generateHead2('ttr_m_ene_lawbotClerk')
            self.setHeight(8.7)
        elif dna.name == 'cm':
            self.scale = 7.2 / bSize
            self.handColor = VBase4(0.337, 0.392, 0.6, 1)
            self.generateSkeletonBody()
            self.setTransparency(1)
            self.setHeight(8.7)
        elif dna.name == 'ggm':
            self.scale = 5.0 / bSize
            self.handColor = VBase4(0.42, 0.502, 0.62, 1)
            self.generateFemaleBody()
            self.makeExecutive()
            self.generateHead('mouthpiece', animated=True)
            self.setHeight(6.8)
        elif dna.name == 'th':
            self.scale = 5.5 / bSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.generateFemaleBody()
            self.makeExecutive()
            self.generateHead('rainmaker', animated=True)
            self.setHeight(7.5)
            self.setTransparency(1)
        elif dna.name == 'kc':
            self.scale = 6.0 / aSize
            self.handColor = VBase4(0.49, 0.494, 0.675, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead('witchhunter', animated=True)
            self.setHeight(8.0)
            self.setTransparency(1)
        elif dna.name == 'tr':
            self.scale = 6.7 / bSize
            self.handColor = VBase4(1, 1, 1, 1)
            self.generateBody()
            self.makeGovernaught()
            self.generateHead('counterclaim', animated=True)
            self.setHeight(8.69)
            self.setTransparency(1)
        elif dna.name == 'mp':
            self.scale = 5.7 / aSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead('redd', animated=True)
            self.setHeight(7.69)
            self.setTransparency(1)
        elif dna.name == 'laa':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.generateSkeletonBody()
            self.makeWSI()
            self.setHeight(8.69)
            self.setTransparency(1)
        elif dna.name == 'scg':
            self.scale = 5.2 / bSize
            self.handColor = VBase4(0.486, 0.522, 0.686, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead('scapegoat', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_scapegoat.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.8)
        elif dna.name == 'csm':
            self.scale = 6.9 / aSize
            self.handColor = VBase4(0.294, 0.208, 0.149, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead('casemanager', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_casemanager.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.2)
            self.setTransparency(1)
        elif dna.name == 'ste':
            self.scale = 7.1 / aSize
            self.handColor = VBase4(0.322, 0.369, 0.525, 1)
            self.generateFemaleBody()
            self.makeExecutive()
            self.generateHead('stenographer', animated=True)
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
            self.generateHead('litigator', animated=True)
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
            self.scale = 4.0 / aSize
            self.handColor = VBase4(0.616, 0.761, 0.576, 1)
            self.generateBody()
            self.generateHead('twoface')
            texture = loader.loadTexture('phase_3.5/maps/consig.png')
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
            self.scale = 5.0 / bSize
            self.handColor = VBase4(0.616, 0.761, 0.576, 1)
            self.generateBody()
            self.generateHead('movershaker')
            texture = loader.loadTexture('phase_3.5/maps/enter.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.2)
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
            self.scale = 7.0 / cSize
            self.handColor = SuitDNA.moneyPolyColor
            self.generateSkeletonBody()
            self.setHeight(8.88)
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
            self.scale = 6.0 / aSize
            self.handColor = VBase4(0.745, 0.863, 0.659, 1)
            self.generateFemaleBody()
            self.generateHead('twoface')
            texture = loader.loadTexture('phase_3.5/maps/mingler3.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.0)
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
            self.handColor = SuitDNA.moneyPolyColor
            self.generateBody()
            self.generateHead('yesman', animated=False)
            texture = loader.loadTexture('phase_4/maps/robber-baron.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.95)
        elif dna.name == 'csh':
            self.scale = 5.5 / cSize
            self.handColor = VBase4(0.604, 0.71, 0.675, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead2('ttr_m_ene_cashbotAuditor')
            self.setHeight(7.0)
            self.setTransparency(1)
        elif dna.name == 'bgr':
            self.scale = 7.0 / cSize
            self.handColor = VBase4(0.286, 0.29, 0.286, 1)
            self.generateSkeletonBody()
            self.setHeight(9.0)
            self.makeExecutive()
            self.setTransparency(1)
        elif dna.name == 'mes':
            self.scale = 7.0 / cSize
            self.handColor = VBase4(0.286, 0.29, 0.286, 1)
            self.generateSkeletonBody()
            self.setHeight(9.0)
            self.makeExecutive()
            self.setTransparency(1)
        elif dna.name == 'dm':
            self.scale = 5.5 / cSize
            self.handColor = VBase4(0.647, 0.796, 0.627, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead('treekiller', animated=True)
            # self.generateClashHead('phase_12/models/char/suits/ttcc_ene_chainsaw_b-zero.bam', 'phase_12/models/char/suits/ttcc_ene_chainsaw_b-neutral-hurt.bam', 'phase_12/models/char/suits/ttcc_ene_chainsaw_b-neutral.bam')
            self.setHeight(7.5)
        elif dna.name == 'tcc':
            self.scale = 5.5 / cSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.generateSkeletonBody()
            self.setHeight(6.97)
            self.makeExecutive()
            self.setTransparency(1)
        elif dna.name == 'fb':
            self.scale = 6.5 / bSize
            self.handColor = VBase4(0.529, 0.455, 0.369, 1)
            self.generateSkeletonBody()
            self.setHeight(7.5)
            self.makeExecutive()
            self.setTransparency(1)
        elif dna.name == 'jl':
            self.scale = 6.75 / cSize
            self.handColor = VBase4(0.5, 1, 0, 1.0)
            self.generateSkeletonBody()
            self.setHeight(8.23)
            self.makeExecutive()
            self.setTransparency(1)
        elif dna.name == 'gb':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.generateSkeletonBody()
            self.setHeight(8.95)
            self.makeExecutive()
            self.setTransparency(1)
        elif dna.name == 'lbs':
            self.scale = 5.25 / aSize
            self.handColor = VBase4(0.286, 0.29, 0.286, 1)
            self.generateSkeletonBody()
            self.setHeight(7.22)
            self.makeExecutive()
            self.setTransparency(1)
        elif dna.name == 'trk':
            self.scale = 3.5 / cSize
            self.handColor = VBase4(0.702, 0.776, 0.788, 1)
            self.generateBody()
            self.makePlutocrat()
            self.generateHead('plutocrat', animated=True)
            self.setHeight(5.0)
            self.setTransparency(1)
        elif dna.name == 'dsf':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(1, 1, 1, 1)
            self.generateBody()
            self.makeCountErfit()
            self.generateHead('counterclaim', animated=True)
            self.setHeight(10.0)
            self.setTransparency(1)
        elif dna.name == 'msp':
            self.scale = 7.5 / aSize
            self.handColor = VBase4(1, 1, 1, 1)
            self.generateHighRollerBody()
            self.makeHighRollerWhite()
            self.generateHead('highroller', animated=True)
            texture = loader.loadTexture('phase_12/maps/cc_t_ene_highroller.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(10.0)
        elif dna.name == 'mad':
            self.scale = 7.3 / aSize
            self.handColor = VBase4(0.478, 0.588, 0.314, 1)
            self.generateBody()
            self.makeDuckShuffler()
            self.generateHead('chainsaw_c', animated=True)
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_chainsaw_c.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(10.0)
            self.setTransparency(1)
        elif dna.name == 'crf':
            self.scale = 7.5 / aSize
            self.handColor = VBase4(1, 1, 1, 1)
            self.generateHighRollerBody()
            self.makeHighRoller()
            self.generateHead('highroller', animated=True)
            texture = loader.loadTexture('phase_12/maps/cc_t_ene_highroller.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(10.0)
            self.setTransparency(1)
        elif dna.name == 'cc':
            self.scale = 3.5 / cSize
            self.headColor = VBase4(0.25, 0.35, 1.0, 1.0)
            self.handColor = VBase4(0.55, 0.65, 1.0, 1.0)
            self.generateBody()
            self.generateHead2('coldcaller')
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
            self.scale = 4.5 / aSize
            self.handColor = VBase4(0.255, 0.318, 0.549, 1)
            self.generateSkeletonBody()
            self.setHeight(5.65)
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
            self.handColor = VBase4(0.373, 0.286, 0.227, 1)
            self.generateBody()
            self.generateHead('numbercruncher')
            texture = loader.loadTexture('phase_4/maps/software-simian.jpg')
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
            self.scale = 5.0 / bSize
            self.handColor = VBase4(0.918, 0.796, 0.996, 1)
            self.generateBody()
            self.generateHead('movershaker')
            texture = loader.loadTexture('phase_4/maps/installation-wizard.jpg')
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
            self.scale = 5.25 / aSize
            self.handColor = VBase4(0.965, 0.859, 0.831, 1)
            self.generateBody()
            self.generateHead('twoface')
            texture = loader.loadTexture('phase_4/maps/twoface.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.95)
        elif dna.name == 'trm':
            self.scale = 6.5 / cSize
            self.handColor = VBase4(0.718, 0.451, 0.451, 1)
            self.generateBody()
            self.generateHead('flunky')
            texture = loader.loadTexture('phase_4/maps/mademan.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.5)
        elif dna.name == 'ssm':
            self.scale = 5.75 / aSize
            self.handColor = VBase4(0.918, 0.808, 0.871, 1)
            self.generateFemaleBody()
            self.generateHead('twoface')
            texture = loader.loadTexture('phase_4/maps/mingler2.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.61)
        elif dna.name == 'isw':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.522, 0.482, 0.435, 1)
            self.generateBody()
            self.generateHead2('telemarketer')
            texture = loader.loadTexture('phase_4/maps/rootuser.jpg')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(9.5)
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
            self.scale = 6.0 / bSize
            self.handColor = VBase4(0.918, 0.808, 0.871, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead2('sellbotForemanHead')
            self.generateHead2('sellbotForemanGlasses')
            self.generateHead2('sellbotForemanEyebrows')
            self.generateHead2('sellbotForemanHat')
            self.setHeight(8.55)
        elif dna.name == 'mdr':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(1, 0.486, 0, 1)
            self.generateSkeletonBody()
            self.makeExecutive()
            self.setHeight(9.0)
            self.setTransparency(1)
        elif dna.name == 'nar':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(1, 0.486, 0, 1)
            self.generateSkeletonBody()
            self.makeExecutive()
            self.setHeight(9.0)
            self.setTransparency(1)
        elif dna.name == 'fd':
            self.scale = 7.0 / cSize
            self.handColor = VBase4(1, 1, 1, 1.0)
            self.generateSkeletonBody()
            self.generateHead('dopa', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_dopa.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(9.5)
            self.isSkeleton = 1
            self.makeDOPA()
            self.setTransparency(1)
        elif dna.name == 'fm':
            self.scale = 7.0 / cSize
            self.handColor = VBase4(0.345, 0.561, 0.549, 1)
            self.generateFemaleBody()
            self.makeExecutive()
            self.generateHead('deepdiver', animated=True)
            self.setHeight(10.0)
        elif dna.name == 'jb':
            self.scale = 5.0 / bSize
            self.handColor = VBase4(0.886, 0.749, 0.451, 1)
            self.generateBody()
            self.generateHead('bellringer', animated=True)
            self.setHeight(6.8)
        elif dna.name == 'jg':
            self.scale = 4.5 / cSize
            self.handColor = VBase4(1, 1, 1, 1.0)
            self.generateBody()
            self.generateHead('dummy', animated=True)
            self.setHeight(7.0)
        elif dna.name == 'jr':
            self.scale = 5.0 / bSize
            self.handColor = VBase4(0.816, 0.663, 0.859, 1)
            self.generateBody()
            self.makePrethinker()
            self.generateHead('prethinker', animated=True)
            self.setHeight(6.5)
            self.setTransparency(1)
        elif dna.name == 'prr':
            self.scale = 7.3 / aSize
            self.handColor = VBase4(0.663, 0.678, 0.682, 1)
            self.generateBody()
            self.makePrethinker()
            self.generateHead('multislacker', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_multislacker.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(10.0)
            self.setTransparency(1)
        elif dna.name == 'blr':
            self.scale = 6.8 / aSize
            self.handColor = VBase4(0.894, 0.235, 0.043, 1)
            self.generateSkeletonBody()
            self.generateHead('dopa', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_dopa.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.7)
            self.isSkeleton = 1
            self.makeDOPA()
            self.setTransparency(1)
        elif dna.name == 'dvp':
            self.scale = 5.0 / aSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.generateFemaleBody()
            self.makeExecutive()
            self.generateHead('rainmaker', animated=True)
            self.setHeight(6.5)
        elif dna.name == 'dsk':
            self.scale = 7.2 / aSize
            self.handColor = VBase4(0.894, 0.235, 0.043, 1)
            self.generateSkeletonBody()
            self.generateHead('dopr', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_dopr.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.7)
            self.isSkeleton = 1
            self.makeDOPA()
            self.setTransparency(1)
        elif dna.name == 'ffm':
            self.scale = 7.3 / aSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead('sharkwatcher', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_sharkwatcher2.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(9.7)
            self.setTransparency(1)
        elif dna.name == 'sft':
            self.scale = 6.2 / bSize
            self.handColor = VBase4(0.369, 0.369, 0.369, 1)
            self.generatePaceBody()
            self.makePacesetter()
            self.generateHead('pacesetter', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_pacesetter.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.5)
        elif dna.name == 'ca':
            self.scale = 4.0 / cSize
            self.handColor = SuitDNA.boardPolyColor
            self.generateBody()
            self.generateHead('bagholder', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_bagholder.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(4.88)
        elif dna.name == 'cn':
            self.scale = 3.75 / bSize
            self.handColor = VBase4(1, 1, 1, 1)
            self.generateBody()
            self.generateHead('paperhands', animated=True)
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
            self.generateHead('insider', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_insider.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
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
            self.handColor = VBase4(0.416, 0.463, 0.459, 1)
            self.generateBody()
            self.generateHead('circuitbreaker', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_circuitbreaker.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(6.66)
        elif dna.name == 'bfh':
            self.scale = 5.25 / cSize
            self.handColor = VBase4(0.78, 0.769, 0.02, 1)
            self.generateBody()
            self.generateHead('toxicleader')
            self.setHeight(7.2)
        elif dna.name == 'hho':
            self.scale = 5.5 / cSize
            self.handColor = SuitDNA.boardPolyColor
            self.generateBody()
            self.generateHead('deadlock', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_deadlock.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.2)
        elif dna.name == 'bdb':
            self.scale = 6.5 / aSize
            self.handColor = VBase4(0.031, 0.035, 0.035, 1)
            self.generateBody()
            self.generateHead2('magnate')
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_magnate.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.headTexture = 'DS_hat.png'
            self.generateHead2('hatjp187187')
            self.setHeight(7.56)
        elif dna.name == 'bgh':
            self.scale = 6.0 / cSize
            self.handColor = SuitDNA.boardPolyColor
            self.generateBody()
            self.generateHead('sharkwatcher', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_sharkwatcher.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.58)
        elif dna.name == 'dfh':
            self.scale = 7.0 / cSize
            self.handColor = VBase4(0.635, 0.62, 0.651, 1)
            self.generateBody()
            self.generateHead2('bigfish')
            self.setHeight(10.0)
        elif dna.name == 'rng':
            self.scale = 6.5 / aSize
            self.handColor = VBase4(0.031, 0.035, 0.035, 1)
            self.generateBody()
            self.generateHead('magnate', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_magnate.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(7.68)
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
            self.handColor = VBase4(0.388, 0.388, 0.388, 1)
            self.generateBody()
            self.generateHead('headhoncho', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_headhoncho.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(10.61)
        elif dna.name == 'gkp':
            self.scale = 4.5 / aSize
            self.handColor = VBase4(1, 0.486, 0, 1)
            self.generateSkeletonBody()
            self.makeExecutive()
            self.setHeight(6.0)
            self.setTransparency(1)
        elif dna.name == 'ddv':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(1, 0.486, 0, 1)
            self.generateSkeletonBody()
            self.makeExecutive()
            self.setHeight(9.0)
            self.setTransparency(1)
        elif dna.name == 'dty':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(1, 0.486, 0, 1)
            self.generateSkeletonBody()
            self.makeExecutive()
            self.setHeight(9.0)
            self.setTransparency(1)
        elif dna.name == 'dfg':
            self.scale = 5.5 / aSize
            self.handColor = VBase4(0.612, 0.612, 0.612, 1)
            self.generateFemaleBody()
            self.makeGatekeeper()
            self.generateHead('gatekeeper', animated=True)
            self.setHeight(6.9)
        elif dna.name == 'dfr':
            self.scale = 6.0 / bSize
            self.handColor = SuitDNA.boardPolyColor
            self.generateBody()
            self.makeBoardbotManager()
            self.generateHead('dola', animated=True)
            self.setHeight(8.0)
        elif dna.name == 'bsh':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(1, 0.486, 0, 1)
            self.generateBody()
            self.makeBoardbotManager()
            self.generateHead('dold', animated=True)
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_dold.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setTransparency(1)
            self.setHeight(9.31)
        elif dna.name == 'ghd':
            self.scale = 6.0 / bSize
            self.handColor = VBase4(0.09, 0.09, 0.09, 1)
            self.generateLongcoatBody()
            self.generateHead('insider', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_insider_mgr.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.0)
            self.setTransparency(1)
        elif dna.name == 'tyh':
            self.scale = 7.2 / aSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.generateFemaleBody()
            self.makeExecutive()
            self.generateHead('stenographer', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_crystalline.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(10.7)
            self.setTransparency(1)
        elif dna.name == 'jgd':
            self.scale = 7.2 / aSize
            self.handColor = VBase4(0.09, 0.09, 0.09, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead('magnate', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_magnate.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(9.0)
            self.setTransparency(1)
        elif dna.name == 'bby':
            self.scale = 7.3 / aSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.generateBody()
            self.makeExecutive()
            self.generateHead('headhoncho', animated=True)
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_headhoncho_exe.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(10.9)
            self.setTransparency(1)
        elif dna.name == 'dvk':
            self.scale = 6.5 / aSize
            self.handColor = VBase4(0.82, 0, 0, 1)
            self.generateBody()
            self.makeBoardbotManager()
            self.generateHead('redd', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_redd.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.4)
            self.setTransparency(1)
        elif dna.name == 'otm':
            self.scale = 6.0 / bSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.generateBody()
            self.makeBoardbotManager()
            self.generateHead('ottoman', animated=True)
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_ottoman.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(8.0)
            self.setTransparency(1)
        elif dna.name == 'cry':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.generateFemaleBody()
            self.makeBoardbotManager()
            self.generateHead('stenographer', animated=True)
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_crystalline.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(9.7)
            self.setTransparency(1)
        elif dna.name == 'tcm':
            self.scale = 7.5 / aSize
            self.handColor = VBase4(0.4, 0.4, 0.4, 1)
            self.generateBody()
            self.makeBoardbotManager()
            self.generateHead('chairman-a', animated=True)
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_chairman.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.setHeight(9.7)
            self.setTransparency(1)
        self.setName(SuitBattleGlobals.SuitAttributes[dna.name]['name'])
        self.getGeomNode().setScale(self.scale)
        if not self.isSkeleton:
            self.generateHPBase()
            self.generateCorporateMedallion()
            self.generateCorporateMedallion2()
            self.generateHealthBar()
        else:
            self.generateSkeletonHealthBar()
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
        self.setBlend(frameBlend=base.wantSmoothAnims)
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)

    def generateSkeletonBody(self):
        animDict = self.generateAnimDict()
        filePrefix, bodyPhase = ModelDict[self.style.body]
        dept = self.style.dept
        if base.config.GetBool('want-new-cogs', 0):
            if cogExists(filePrefix + 'zero.bam'):
                self.loadModel('phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-zero')
            else:
                self.loadModel('phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-zero')
        else:
            self.loadModel('phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-zero')
        if self.style.body == 'a' and not self.style.name == 'ts' and not self.style.name == 'cg' and not self.style.name == 'dsk' and not self.style.name == 'blr':
            self.generateHead('skullA', animated=True)
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' %
                                         self.style.dept)
            for headPart in self.headParts:
                texture.setMinfilter(Texture.FTNearestMipmapLinear)
                texture.setMagfilter(Texture.FTNearest)
                headPart.setTexture(texture, 1)
        if self.style.body == 'b':
            self.generateHead('skullB', animated=True)
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' %
                                         self.style.dept)
            for headPart in self.headParts:
                texture.setMinfilter(Texture.FTNearestMipmapLinear)
                texture.setMagfilter(Texture.FTNearest)
                headPart.setTexture(texture, 1)
        if self.style.body == 'c' and not self.style.name == 'fd':
            self.generateHead('skullC', animated=True)
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' %
                self.style.dept)
            for headPart in self.headParts:
                texture.setMinfilter(Texture.FTNearestMipmapLinear)
                texture.setMagfilter(Texture.FTNearest)
                headPart.setTexture(texture, 1)
        self.loadAnims(animDict)
        self.setSuitClothesSkeleton()
        self.setBlend(frameBlend=base.wantSmoothAnims)
        #self.generateSkeletonHealthBar()
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
        nameInfo = TTLocalizer.SuitBaseNameWithLevelHP % {'currHP': self.currHP}
        self.setDisplayName(nameInfo)

    def setSuitClothes(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        dept = self.style.dept
        phase = 3.5
        texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_%s.png' % self.style.dept)
        if self.isExecutive and not self.style.name == 'mdm':
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_%s_e.png' % self.style.dept)
        elif self.isManager and not self.style.name == 'crf':
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_%s_e.png' % self.style.dept)
        elif self.isGovernaught and not self.style.name == 'mdm':
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_%s_gov.png' % self.style.dept)
        elif self.style.name == 'mdm':
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_highcollar_%s.png' % self.style.dept)
        elif self.isGovernaught and self.style.name == 'mdm':
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_highcollar_%s_gov.png' % self.style.dept)
        elif self.isExecutive and self.style.name == 'mdm':
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_highcollar_%s_e.png' % self.style.dept)
        # This will only work if you have the texture ttcc_ene_suittex_unemployed.png in phase_3.5/maps, which is the texture that Cogs wear when fired.  This is just in case it can't properly load the above texture.
        texture.setMinfilter(Texture.FTLinearMipmapLinear)
        texture.setMagfilter(Texture.FTLinear)
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
        elif self.style.name == 'sft' and self.style.dept == 's':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'crf':
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

        def __doItTheOldWay__():
            self.leftHand = self.find('**/joint_Lhold')
            self.rightHand = self.find('**/joint_Rhold')
            self.shadowJoint = self.find('**/joint_shadow')
            self.nametagJoint = self.find('**/joint_nameTag')

        if base.config.GetBool('want-new-cogs', 0):
            if dept == 'c':
                texType = 'bossbot'
            elif dept == 'm':
                texType = 'cashbot'
            elif dept == 'l':
                texType = 'lawbot'
            elif dept == 's':
                texType = 'sellbot'
            elif dept == 'g':
                texType = 'boardbot'
            if self.find('**/body').isEmpty():
                __doItTheOldWay__()
            else:
                filepath = 'phase_3.5/maps/tt_t_ene_' + texType + '.jpg'
                if cogExists('/maps/tt_t_ene_' + texType + '.jpg'):
                    bodyTex = loader.loadTexture(filepath)
                    self.find('**/body').setTexture(bodyTex, 1)
                self.leftHand = self.find('**/def_joint_left_hold')
                self.rightHand = self.find('**/def_joint_right_hold')
                self.shadowJoint = self.find('**/def_shadow')
                self.nametagJoint = self.find('**/def_nameTag')
        else:
            __doItTheOldWay__()

        def __doItTheOldWay__():
            self.leftHand = self.find('**/joint_Lhold')
            self.rightHand = self.find('**/joint_Rhold')
            self.shadowJoint = self.find('**/joint_shadow')
            self.nametagJoint = self.find('**/joint_nameTag')

        if base.config.GetBool('want-new-cogs', 0):
            if dept == 'c':
                texType = 'bossbot'
            elif dept == 'm':
                texType = 'cashbot'
            elif dept == 'l':
                texType = 'lawbot'
            elif dept == 's':
                texType = 'sellbot'
            elif dept == 'g':
                texType = 'boardbot'
            if self.find('**/body').isEmpty():
                __doItTheOldWay__()
            else:
                filepath = 'phase_3.5/maps/tt_t_ene_' + texType + '.jpg'
                if cogExists('/maps/tt_t_ene_' + texType + '.jpg'):
                    bodyTex = loader.loadTexture(filepath)
                    self.find('**/body').setTexture(bodyTex, 1)
                self.leftHand = self.find('**/def_joint_left_hold')
                self.rightHand = self.find('**/def_joint_right_hold')
                self.shadowJoint = self.find('**/def_shadow')
                self.nametagJoint = self.find('**/def_nameTag')
        else:
            __doItTheOldWay__()

    def setSuitClothesHighRoller(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        dept = self.style.dept
        phase = 3.5
        texture = loader.loadTexture('phase_12/maps/cc_t_ene_highroller_suit_black.png')  # This will only work if you have the texture ttcc_ene_suittex_unemployed.png in phase_3.5/maps, which is the texture that Cogs wear when fired.  This is just in case it can't properly load the above texture.
        texture.setMinfilter(Texture.FTLinearMipmapLinear)
        texture.setMagfilter(Texture.FTLinear)
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

        def __doItTheOldWay__():
            self.leftHand = self.find('**/joint_Lhold')
            self.rightHand = self.find('**/joint_Rhold')
            self.shadowJoint = self.find('**/joint_shadow')
            self.nametagJoint = self.find('**/joint_nameTag')

        if base.config.GetBool('want-new-cogs', 0):
            if dept == 'c':
                texType = 'bossbot'
            elif dept == 'm':
                texType = 'cashbot'
            elif dept == 'l':
                texType = 'lawbot'
            elif dept == 's':
                texType = 'sellbot'
            elif dept == 'g':
                texType = 'boardbot'
            if self.find('**/body').isEmpty():
                __doItTheOldWay__()
            else:
                filepath = 'phase_3.5/maps/tt_t_ene_' + texType + '.jpg'
                if cogExists('/maps/tt_t_ene_' + texType + '.jpg'):
                    bodyTex = loader.loadTexture(filepath)
                    self.find('**/body').setTexture(bodyTex, 1)
                self.leftHand = self.find('**/def_joint_left_hold')
                self.rightHand = self.find('**/def_joint_right_hold')
                self.shadowJoint = self.find('**/def_shadow')
                self.nametagJoint = self.find('**/def_nameTag')
        else:
            __doItTheOldWay__()

        def __doItTheOldWay__():
            self.leftHand = self.find('**/joint_Lhold')
            self.rightHand = self.find('**/joint_Rhold')
            self.shadowJoint = self.find('**/joint_shadow')
            self.nametagJoint = self.find('**/joint_nameTag')

        if base.config.GetBool('want-new-cogs', 0):
            if dept == 'c':
                texType = 'bossbot'
            elif dept == 'm':
                texType = 'cashbot'
            elif dept == 'l':
                texType = 'lawbot'
            elif dept == 's':
                texType = 'sellbot'
            elif dept == 'g':
                texType = 'boardbot'
            if self.find('**/body').isEmpty():
                __doItTheOldWay__()
            else:
                filepath = 'phase_3.5/maps/tt_t_ene_' + texType + '.jpg'
                if cogExists('/maps/tt_t_ene_' + texType + '.jpg'):
                    bodyTex = loader.loadTexture(filepath)
                    self.find('**/body').setTexture(bodyTex, 1)
                self.leftHand = self.find('**/def_joint_left_hold')
                self.rightHand = self.find('**/def_joint_right_hold')
                self.shadowJoint = self.find('**/def_shadow')
                self.nametagJoint = self.find('**/def_nameTag')
        else:
            __doItTheOldWay__()

    def setSuitClothesRaincoat(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        dept = self.style.dept
        phase = 3.5
        texture = loader.loadTexture('phase_11/maps/ttcc_ene_suittex_rainmake.png')  # This will only work if you have the texture ttcc_ene_suittex_unemployed.png in phase_3.5/maps, which is the texture that Cogs wear when fired.  This is just in case it can't properly load the above texture.
        texture.setMinfilter(Texture.FTLinearMipmapLinear)
        texture.setMagfilter(Texture.FTLinear)
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
        else:
            modelRoot.find('**/necktie-w').show()
        modelRoot.find('**/body').setTexture(texture, 1)

        def __doItTheOldWay__():
            self.leftHand = self.find('**/joint_Lhold')
            self.rightHand = self.find('**/joint_Rhold')
            self.shadowJoint = self.find('**/joint_shadow')
            self.nametagJoint = self.find('**/joint_nameTag')

        if base.config.GetBool('want-new-cogs', 0):
            if dept == 'c':
                texType = 'bossbot'
            elif dept == 'm':
                texType = 'cashbot'
            elif dept == 'l':
                texType = 'lawbot'
            elif dept == 's':
                texType = 'sellbot'
            elif dept == 'g':
                texType = 'boardbot'
            if self.find('**/body').isEmpty():
                __doItTheOldWay__()
            else:
                filepath = 'phase_3.5/maps/tt_t_ene_' + texType + '.jpg'
                if cogExists('/maps/tt_t_ene_' + texType + '.jpg'):
                    bodyTex = loader.loadTexture(filepath)
                    self.find('**/body').setTexture(bodyTex, 1)
                self.leftHand = self.find('**/def_joint_left_hold')
                self.rightHand = self.find('**/def_joint_right_hold')
                self.shadowJoint = self.find('**/def_shadow')
                self.nametagJoint = self.find('**/def_nameTag')
        else:
            __doItTheOldWay__()

        def __doItTheOldWay__():
            self.leftHand = self.find('**/joint_Lhold')
            self.rightHand = self.find('**/joint_Rhold')
            self.shadowJoint = self.find('**/joint_shadow')
            self.nametagJoint = self.find('**/joint_nameTag')

        if base.config.GetBool('want-new-cogs', 0):
            if dept == 'c':
                texType = 'bossbot'
            elif dept == 'm':
                texType = 'cashbot'
            elif dept == 'l':
                texType = 'lawbot'
            elif dept == 's':
                texType = 'sellbot'
            elif dept == 'g':
                texType = 'boardbot'
            if self.find('**/body').isEmpty():
                __doItTheOldWay__()
            else:
                filepath = 'phase_3.5/maps/tt_t_ene_' + texType + '.jpg'
                if cogExists('/maps/tt_t_ene_' + texType + '.jpg'):
                    bodyTex = loader.loadTexture(filepath)
                    self.find('**/body').setTexture(bodyTex, 1)
                self.leftHand = self.find('**/def_joint_left_hold')
                self.rightHand = self.find('**/def_joint_right_hold')
                self.shadowJoint = self.find('**/def_shadow')
                self.nametagJoint = self.find('**/def_nameTag')
        else:
            __doItTheOldWay__()

    def setSuitClothesHighRollerWhite(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        dept = self.style.dept
        phase = 3.5
        texture = loader.loadTexture('phase_12/maps/cc_t_ene_highroller_suit.png')
        texture.setMinfilter(Texture.FTLinearMipmapLinear)
        texture.setMagfilter(Texture.FTLinear)
        texture = loader.loadTexture('phase_12/maps/cc_t_ene_highroller_body2.png')
        # This will only work if you have the texture ttcc_ene_suittex_unemployed.png in phase_3.5/maps, which is the texture that Cogs wear when fired.  This is just in case it can't properly load the above texture.
        texture.setMinfilter(Texture.FTLinearMipmapLinear)
        texture.setMagfilter(Texture.FTLinear)
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
        elif self.style.name == 'crf':
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'msp':
            modelRoot.find('**/necktie-w').hide()
        else:
            modelRoot.find('**/necktie-w').show()
        modelRoot.find('**/body').setTexture(texture, 1)

        def __doItTheOldWay__():
            self.leftHand = self.find('**/joint_Lhold')
            self.rightHand = self.find('**/joint_Rhold')
            self.shadowJoint = self.find('**/joint_shadow')
            self.nametagJoint = self.find('**/joint_nameTag')

        if base.config.GetBool('want-new-cogs', 0):
            if dept == 'c':
                texType = 'bossbot'
            elif dept == 'm':
                texType = 'cashbot'
            elif dept == 'l':
                texType = 'lawbot'
            elif dept == 's':
                texType = 'sellbot'
            elif dept == 'g':
                texType = 'boardbot'
            if self.find('**/body').isEmpty():
                __doItTheOldWay__()
            else:
                filepath = 'phase_3.5/maps/tt_t_ene_' + texType + '.jpg'
                if cogExists('/maps/tt_t_ene_' + texType + '.jpg'):
                    bodyTex = loader.loadTexture(filepath)
                    self.find('**/body').setTexture(bodyTex, 1)
                self.leftHand = self.find('**/def_joint_left_hold')
                self.rightHand = self.find('**/def_joint_right_hold')
                self.shadowJoint = self.find('**/def_shadow')
                self.nametagJoint = self.find('**/def_nameTag')
        else:
            __doItTheOldWay__()

        def __doItTheOldWay__():
            self.leftHand = self.find('**/joint_Lhold')
            self.rightHand = self.find('**/joint_Rhold')
            self.shadowJoint = self.find('**/joint_shadow')
            self.nametagJoint = self.find('**/joint_nameTag')

        if base.config.GetBool('want-new-cogs', 0):
            if dept == 'c':
                texType = 'bossbot'
            elif dept == 'm':
                texType = 'cashbot'
            elif dept == 'l':
                texType = 'lawbot'
            elif dept == 's':
                texType = 'sellbot'
            elif dept == 'g':
                texType = 'boardbot'
            if self.find('**/body').isEmpty():
                __doItTheOldWay__()
            else:
                filepath = 'phase_3.5/maps/tt_t_ene_' + texType + '.jpg'
                if cogExists('/maps/tt_t_ene_' + texType + '.jpg'):
                    bodyTex = loader.loadTexture(filepath)
                    self.find('**/body').setTexture(bodyTex, 1)
                self.leftHand = self.find('**/def_joint_left_hold')
                self.rightHand = self.find('**/def_joint_right_hold')
                self.shadowJoint = self.find('**/def_shadow')
                self.nametagJoint = self.find('**/def_nameTag')
        else:
            __doItTheOldWay__()


    def setSuitClothesSkeleton(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        dept = self.style.dept
        phase = 3.5
        texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' % self.style.dept)
        if self.isExecutive or self.isManager:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' % self.style.dept)
        elif self.isGovernaught:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_gov.png')
        texture.setMinfilter(Texture.FTLinearMipmapLinear)
        texture.setMagfilter(Texture.FTLinear)
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
        elif self.style.name == 'jl':
            modelRoot.find('**/bowtie').show()
            modelRoot.find('**/necktie-w').hide()
        else:
            modelRoot.find('**/necktie-w').show()
        modelRoot.find('**/body').setTexture(texture, 1)

        def __doItTheOldWay__():
            self.leftHand = self.find('**/joint_Lhold')
            self.rightHand = self.find('**/joint_Rhold')
            self.shadowJoint = self.find('**/joint_shadow')
            self.nametagJoint = self.find('**/joint_nameTag')

        if base.config.GetBool('want-new-cogs', 0):
            if dept == 'c':
                texType = 'bossbot'
            elif dept == 'm':
                texType = 'cashbot'
            elif dept == 'l':
                texType = 'lawbot'
            elif dept == 's':
                texType = 'sellbot'
            elif dept == 'g':
                texType = 'boardbot'
            if self.find('**/body').isEmpty():
                __doItTheOldWay__()
            else:
                filepath = 'phase_3.5/maps/tt_t_ene_' + texType + '.jpg'
                if cogExists('/maps/tt_t_ene_' + texType + '.jpg'):
                    bodyTex = loader.loadTexture(filepath)
                    self.find('**/body').setTexture(bodyTex, 1)
                self.leftHand = self.find('**/def_joint_left_hold')
                self.rightHand = self.find('**/def_joint_right_hold')
                self.shadowJoint = self.find('**/def_shadow')
                self.nametagJoint = self.find('**/def_nameTag')
        else:
            __doItTheOldWay__()

        def __doItTheOldWay__():
            self.leftHand = self.find('**/joint_Lhold')
            self.rightHand = self.find('**/joint_Rhold')
            self.shadowJoint = self.find('**/joint_shadow')
            self.nametagJoint = self.find('**/joint_nameTag')

        if base.config.GetBool('want-new-cogs', 0):
            if dept == 'c':
                texType = 'bossbot'
            elif dept == 'm':
                texType = 'cashbot'
            elif dept == 'l':
                texType = 'lawbot'
            elif dept == 's':
                texType = 'sellbot'
            elif dept == 'g':
                texType = 'boardbot'
            if self.find('**/body').isEmpty():
                __doItTheOldWay__()
            else:
                filepath = 'phase_3.5/maps/tt_t_ene_' + texType + '.jpg'
                if cogExists('/maps/tt_t_ene_' + texType + '.jpg'):
                    bodyTex = loader.loadTexture(filepath)
                    self.find('**/body').setTexture(bodyTex, 1)
                self.leftHand = self.find('**/def_joint_left_hold')
                self.rightHand = self.find('**/def_joint_right_hold')
                self.shadowJoint = self.find('**/def_shadow')
                self.nametagJoint = self.find('**/def_nameTag')
        else:
            __doItTheOldWay__()

    def makeWaiter(self, modelRoot = None):
        if not modelRoot:
            modelRoot = self
        self.isWaiter = 1
        texture = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_waiter.png')
        if self.isExecutive:
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_waiter_e.png')
        elif self.isGovernaught:
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_suittex_count.png')
        elif self.isManager:
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_%s_e.png' % self.style.dept)
        modelRoot.find('**/body').setTexture(texture, 1)

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
        if self.style.dept == 'l':
            modelRoot.find('**/bowtie').show()
        elif self.style.dept == 's':
            modelRoot.find('**/necktie-s').show()
        elif self.style.name == 'sft':
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'dfh':
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'crf':
            modelRoot.find('**/necktie-w').hide()
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
                    texture.setMinfilter(Texture.FTNearestMipmapLinear)
                    texture.setMagfilter(Texture.FTNearest)
                    headPart.setTexture(texture, 1)
            else:
                headModel = Actor.Actor('phase_14/models/char/ttcc_ene_' + headType + '-zero')
                self.generateHeadAnims('phase_14/models/char/ttcc_ene_' + headType + '-', headModel,
                                       additionalAnims)
                self.headParts.append(headModel)
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
                headModel.setScale(1.1)
            elif self.style.name == 'tb':
                headModel.setZ(-.05)
                headModel.setY(-.3)
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
            elif headType == 'plutocrat' and self.style.name == 'ffm':
                headModel.setScale(.85)
                headModel.setZ(-.1)
                headModel.setY(-.1)
            elif headType == 'rainmaker' and self.style.name == 'dvp':
                headModel.setScale(1.05)
                headModel.setZ(-.1)
                headModel.setY(0)
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
            elif headType == 'dopr' and self.style.name == 'dsk':
                headModel.setScale(1.3)
            elif headType == 'dopa' and self.style.name == 'blr':
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
                        headTex.setMinfilter(Texture.FTLinearMipmapLinear)
                        headTex.setMagfilter(Texture.FTLinear)
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
        if headType == 'magnate' and self.style.name == 'bdb':
                headModel = loader.loadModel('phase_14/models/char/ttcc_ene_magnate-zero2')
        if headType == 'camera' and self.style.name == 'cps':
                headModel = loader.loadModel('phase_4/models/accessories/newstoon_camera')
        if headType == 'connoisseur_head' and self.style.name == 'bgh':
                headModel = loader.loadModel('phase_14/models/char/ttcc_ene_connoisseur')
        if headType == 'connoisseur_monocle' and self.style.name == 'bgh':
                headModel = loader.loadModel('phase_14/models/char/ttcc_ene_connoisseur')
        if headType == 'connoisseur_hat' and self.style.name == 'cn':
                headModel = loader.loadModel('phase_14/models/char/ttcc_ene_connoisseur')
        if headType == 'connoisseur_head' and self.style.name == 'cn':
                headModel = loader.loadModel('phase_14/models/char/ttcc_ene_connoisseur')
        if headType == 'connoisseur_monocle' and self.style.name == 'cn':
                headModel = loader.loadModel('phase_14/models/char/ttcc_ene_connoisseur')
        if headType == 'movershaker' and self.style.body == 'c':
                headModel = loader.loadModel('phase_4/models/char/suitB-heads')
        if headType == 'bigfish' and self.style.body == 'a':
                headModel = loader.loadModel('phase_3.5/models/char/suitC-heads')
        if headType == 'ambulancechaser' and self.style.body == 'a':
                headModel = loader.loadModel('phase_4/models/char/suitB-heads')
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
        if headType == 'ear01' and self.style.body == 'a':
            headModel = loader.loadModel('phase_4/models/char/mole_cog')
            headModel.setZ(-.4)
            headModel.setScale(.7)
            headModel.setH(180)
        if headType == 'head' and self.style.body == 'a':
            headModel = loader.loadModel('phase_4/models/char/mole_cog')
            headModel.setZ(-.4)
            headModel.setScale(.7)
            headModel.setH(180)
        if headType == 'ear03' and self.style.body == 'a':
            headModel = loader.loadModel('phase_4/models/char/mole_cog')
            headModel.setZ(-.4)
            headModel.setScale(.7)
            headModel.setH(180)
        if headType == 'ear04' and self.style.body == 'a':
            headModel = loader.loadModel('phase_4/models/char/mole_cog')
            headModel.setZ(-.4)
            headModel.setScale(.7)
            headModel.setH(180)
        if headType == 'ear02' and self.style.body == 'a':
            headModel = loader.loadModel('phase_4/models/char/mole_cog')
            headModel.setZ(-.4)
            headModel.setScale(.7)
            headModel.setH(180)
        if headType == 'antenna_stick' and self.style.body == 'a':
            headModel = loader.loadModel('phase_4/models/char/mole_cog')
            headModel.setZ(-.4)
            headModel.setScale(.7)
            headModel.setH(180)
        if headType == 'antenna_ball' and self.style.body == 'a':
            headModel = loader.loadModel('phase_4/models/char/mole_cog')
            headModel.setZ(-.4)
            headModel.setScale(.7)
            headModel.setH(180)
        if headType == 'eye_mouth' and self.style.body == 'a':
            headModel = loader.loadModel('phase_4/models/char/mole_cog')
            headModel.setZ(-.4)
            headModel.setScale(.7)
            headModel.setH(180)
        if headType == 'pupils' and self.style.body == 'a':
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
            if self.style.name == 'cr':
                headPart.setZ(-.1)
                headPart.setY(-.1)
                headPart.setScale(1.05)
                headPart.setH(0)
            if self.style.name == 'isw':
                headPart.setZ(-.1)
                headPart.setY(-.1)
                headPart.setScale(1.05)
                headPart.setH(0)
            if headType == 'hatjp187187' and self.style.name == 'bdb':
                headPart.setZ(-.7)
            if self.headTexture:
                headTex = loader.loadTexture('phase_' + str(phase) + '/maps/' + self.headTexture)
                headTex.setMinfilter(Texture.FTLinearMipmapLinear)
                headTex.setMagfilter(Texture.FTLinear)
                headPart.setTexture(headTex, 1)
            if self.headColor:
                headPart.setColor(self.headColor)
            self.headParts.append(headPart)

        headModel.removeNode()


    def generateHeadAnims(self, path, cActor, additionalAnims=[]):
        anims = ['neutral', 'death', 'grunt', 'murmur', 'question', 'statement', 'neutral-hurt', 'neutral-lured',
                 'stun']
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
        icons = loader.loadModel('phase_3/models/gui/cog_icons')
        dept = self.style.dept
        chestNull = self.find('**/joint_attachMeter')
        if dept == 'c':
            self.corpMedallion = icons.find('**/CorpIcon').copyTo(chestNull)
        elif dept == 's':
            self.corpMedallion = icons.find('**/SalesIcon').copyTo(chestNull)
        elif dept == 'l':
            self.corpMedallion = icons.find('**/LegalIcon').copyTo(chestNull)
        elif dept == 'm':
            self.corpMedallion = icons.find('**/MoneyIcon').copyTo(chestNull)
        elif dept == 'g':
            self.corpMedallion = icons.find('**/BoardIcon').copyTo(chestNull)

        self.corpMedallion.setPosHprScale(0.02, 0.05, 0.04, 180.0, 0.0, 0.0, 0.51, 0.51, 0.51)
        self.corpMedallion.setColor(self.medallionColors[dept])
        self.corpMedallion.setY(-.05)
        icons.removeNode()

    def generateCorporateMedallion3(self):
        icons = loader.loadModel('phase_3/models/gui/cog_icons')
        dept = self.style.dept
        chestNull = self.find('**/joint_attachMeter')
        if dept == 'c':
            self.corpMedallion = icons.find('**/CorpIcon').copyTo(chestNull)
        elif dept == 's':
            self.corpMedallion = icons.find('**/SalesIcon').copyTo(chestNull)
        elif dept == 'l':
            self.corpMedallion = icons.find('**/LegalIcon').copyTo(chestNull)
        elif dept == 'm':
            self.corpMedallion = icons.find('**/MoneyIcon').copyTo(chestNull)
        elif dept == 'g':
            self.corpMedallion = icons.find('**/BoardIcon').copyTo(chestNull)

        self.corpMedallion.setPosHprScale(0.0, 0.0, 0.00, 180.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        self.corpMedallion.setColor(self.medallionColors[dept])
        self.corpMedallion.setY(-.4)
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
        tieTex.setMinfilter(Texture.FTLinearMipmapLinear)
        tieTex.setMagfilter(Texture.FTLinear)
        tie.setTexture(tieTex, 1)

    def generateCorporateMedallion(self):
        icons = loader.loadModel('phase_3.5/models/char/ttcc_ene_insignias')
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
        self.corpMedallion.setScale(1.0)
        self.corpMedallion.setH(180.0)
        if self.style.body == 'c':
            self.corpMedallion.setY(.05)
        if self.style.body == 'a':
            self.corpMedallion.setY(-.05)
        self.corpMedallion.setColor(self.medallionColors[dept])
        icons.removeNode()

    def generateHPBase(self):
        model = loader.loadModel('phase_3.5/models/char/ttcc_ene_insignias')
        dept = self.style.dept
        if base.config.GetBool('want-new-cogs', 0):
            chestNull = self.find('**/def_joint_attachMeter')
            if chestNull.isEmpty():
                chestNull = self.find('**/joint_attachMeter')
        else:
            chestNull = self.find('**/joint_attachMeter')
        if dept == 'c':
            self.corpMedallion = model.find('**/emblem_base').copyTo(chestNull)
        elif dept == 's':
            self.corpMedallion = model.find('**/emblem_base').copyTo(chestNull)
        elif dept == 'l':
            self.corpMedallion = model.find('**/emblem_base').copyTo(chestNull)
        elif dept == 'm':
            self.corpMedallion = model.find('**/emblem_base').copyTo(chestNull)
        elif dept == 'g':
            self.corpMedallion = model.find('**/emblem_base').copyTo(chestNull)
        self.corpMedallion.setScale(1.0)
        self.corpMedallion.setH(180.0)
        if self.style.body == 'c':
            self.corpMedallion.setY(.05)
        if self.style.body == 'a':
            self.corpMedallion.setY(-.05)
        self.corpMedallion.setColor(self.medallionColors[dept])
        model.removeNode()

    def generateHealthBar(self):
        self.removeHealthBar()
        model = loader.loadModel('phase_3.5/models/char/ttcc_ene_insignias')
        button = model.find('**/emblem_hp')
        model.removeNode()

        button.setScale(1)
        button.setH(180.0)
        button.setColor(self.healthColors[0])
        chestNull = self.find('**/joint_attachMeter')
        button.reparentTo(chestNull)
        self.healthBar = button
        glow = button.find('**/glow')
        glow.reparentTo(self.healthBar)
        glow.setScale(1)
        glow.setPos(0, 0, 0)
        glow.setColor(self.healthGlowColors[0])
        button.flattenLight()
        self.healthBarGlow = glow
        self.healthBar.hide()
        self.healthCondition = 0
        if self.style.body == 'c':
            self.healthBar.setY(.05)
        if self.style.body == 'a':
            self.healthBar.setY(-.05)

    def generateSkeletonHealthBar(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.removeHealthBar()
        button = modelRoot.find('**/emblem_healthmeter')

        button.setScale(1)
        button.setColor(self.healthColors[0])
        self.healthBar = button
        glow = modelRoot.find('**/glow')
        glow.reparentTo(self.healthBar)
        glow.setScale(1)
        glow.setPos(0, 0, 0)
        glow.setColor(self.healthGlowColors[0])
        self.healthBarGlow = glow
        self.healthBar.hide()
        self.healthCondition = 0

    def resetHealthBarForSkele(self):
        self.healthBar.setPos(0.0, 0.0, 0.0)

    def updateHealthBar(self, hp, forceUpdate = 0):
        self.currHP -= hp
        health = float(self.currHP) / float(self.maxHP)
        print('UpdateHealthBar MHP %i HP %i' % (self.maxHP, self.currHP))
        print('UpdateHealthBar - health is %f' % health)
        if health > 1.5:
            condition = 13
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
        elif health > 0.25:
            condition = 6
        elif health > 0.20:
            condition = 7
        elif health > 0.15:
            condition = 8
        elif health > 0.10:
            condition = 9
        elif health > 0.0:
            condition = 10
        else:
            condition = 11
        print('UpdateHealthBar - condition is %i' % condition)

        if self.healthCondition != condition or forceUpdate:
            if condition in (10, 11):
                blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.75 if condition == 10 else 0.25),
                                      Task(self.__blinkGray), Task.pause(0.1))
                taskMgr.add(blinkTask, 'blink-task-%s' % id(self))
            else:
                taskMgr.remove(self.uniqueName('blink-task'))
                self.healthBar.setColor(self.healthColors[condition], 1)
                self.healthBarGlow.setColor(self.healthGlowColors[condition], 1)
            self.healthCondition = condition

    def __blinkRed(self, task):
        self.healthBar.setColor(self.healthColors[9], 1)
        self.healthBarGlow.setColor(self.healthGlowColors[9], 1)
        if self.healthCondition == 11:
            self.healthBar.setScale(1.0)

    def __blinkGray(self, task):
        if not self.healthBar:
            return
        self.healthBar.setColor(self.healthColors[10], 1)
        self.healthBarGlow.setColor(self.healthGlowColors[10], 1)
        if self.healthCondition == 11:
            self.healthBar.setScale(1.0)

    def removeHealthBar(self):
        if self.healthBar:
            self.healthBar.removeNode()
            self.healthBar = None
        
        if self.healthCondition == 10 or self.healthCondition == 11:
            taskMgr.remove(self.uniqueName('blink-task'))
        
        self.healthCondition = 0

    def getLoseActor(self, headless=False):
        if self.loseActor == None:
            if not self.isSkeleton:
                filePrefix, phase = TutorialModelDict[self.style.body]
                if self.style.name == 'nd':
                    loseModel = 'phase_3.5/models/char/suitA-f-mod'
                elif self.style.name == 'crf':
                    loseModel = 'phase_3.5/models/char/suitA-hroller-mod'
                elif self.style.name == 'msp':
                    loseModel = 'phase_3.5/models/char/suitA-hroller-mod'
                elif self.style.name == 'nc':
                    loseModel = 'phase_3.5/models/char/suitA-f-mod'
                elif self.style.name == 'cry':
                    loseModel = 'phase_3.5/models/char/suitA-f-mod'
                elif self.style.name == 'ste':
                    loseModel = 'phase_3.5/models/char/suitA-f-mod'
                elif self.style.name == 'frs':
                    loseModel = 'phase_3.5/models/char/suitA-f-mod'
                elif self.style.name == 'tlr':
                    loseModel = 'phase_3.5/models/char/suitA-f-mod'
                elif self.style.name == 'm':
                    loseModel = 'phase_3.5/models/char/suitA-f-mod'
                elif self.style.name == 'dvp':
                    loseModel = 'phase_3.5/models/char/suitA-f-mod'
                elif self.style.name == 'trb':
                    loseModel = 'phase_3.5/models/char/suitA-f-mod'
                elif self.style.name == 'sft':
                    loseModel = 'phase_3.5/models/char/suitB-open-mod'
                elif self.style.name == 'dot':
                    loseModel = 'phase_3.5/models/char/suitA-f-mod'
                elif self.style.name == 'mm':
                    loseModel = 'phase_3.5/models/char/suitC-f-mod'
                elif self.style.name == 'ac':
                    loseModel = 'phase_3.5/models/char/suitC-f-mod'
                elif self.style.name == 'le':
                    loseModel = 'phase_3.5/models/char/suitB-f-mod'
                elif self.style.name == 'ggm':
                    loseModel = 'phase_3.5/models/char/suitB-f-mod'
                elif self.style.name == 'th':
                    loseModel = 'phase_3.5/models/char/suitB-f-mod'
                elif self.style.name == 'dfg':
                    loseModel = 'phase_3.5/models/char/suitA-f-mod'
                elif self.style.name == 'sjg':
                    loseModel = 'phase_3.5/models/char/suitA-f-mod'
                elif self.style.name == 'arb':
                    loseModel = 'phase_3.5/models/char/suitA-f-mod'
                elif self.style.name == 'lsc':
                    loseModel = 'phase_3.5/models/char/suitA-f-mod'
                elif self.style.name == 'ad':
                    loseModel = 'phase_3.5/models/char/suitA-f-mod'
                elif self.style.name == 'dty':
                    loseModel = 'phase_3.5/models/char/suitC-f-mod'
                else:
                    loseModel = 'phase_' + str(phase) + filePrefix + 'lose-mod'
                loseAnim = 'phase_' + str(phase) + filePrefix + 'headless-death'
                self.loseActor = Actor.Actor(loseModel, {'headless-death': loseAnim})
                loseNeck = self.loseActor.find('**/joint_head')
                if headless is False:
                    loseAnim = 'phase_' + str(phase) + filePrefix + 'lose'
                    self.loseActor = Actor.Actor(loseModel, {'lose': loseAnim})
                    loseNeck = self.loseActor.find('**/joint_head')
                    for part in self.headParts:
                        part.instanceTo(loseNeck)

                if self.isWaiter:
                    self.makeWaiter(self.loseActor)
                if self.isManager:
                    self.makeManagerSuit(self.loseActor)
                else:
                    self.setSuitClothes(self.loseActor)
            else:
                loseModel = 'phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-lose-mod'
                filePrefix, phase = TutorialModelDict[self.style.body]
                loseAnim = 'phase_' + str(phase) + filePrefix + 'headless-death'
                self.loseActor = Actor.Actor(loseModel, {'headless-death': loseAnim})
                loseNeck = self.loseActor.find('**/joint_head')
                if headless is False:
                    loseAnim = 'phase_' + str(phase) + filePrefix + 'lose'
                    self.loseActor = Actor.Actor(loseModel, {'lose': loseAnim})
                    loseNeck = self.loseActor.find('**/joint_head')
                    for part in self.headParts:
                        part.instanceTo(loseNeck)

                self.setSuitClothesSkeleton(self.loseActor)

        self.loseActor.setScale(self.scale)
        self.loseActor.setPos(self.getPos())
        self.loseActor.setHpr(self.getHpr())
        shadowJoint = self.loseActor.find('**/joint_shadow')
        dropShadow = loader.loadModel('phase_3/models/props/drop_shadow')
        dropShadow.setScale(0.45)
        dropShadow.setColor(0.0, 0.0, 0.0, 0.5)
        dropShadow.reparentTo(shadowJoint)
        return self.loseActor

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
        self.removePart('modelRoot')
        self.loadModel(model)
        self.loadAnims(anims)
        if self.style.body == 'a' and not self.style.name == 'ts' and not self.style.name == 'cg' and not self.style.name == 'dsk' and not self.style.name == 'blr':
            self.generateHead('skullA', animated=True)
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' %
                                         self.style.dept)
            for headPart in self.headParts:
                texture.setMinfilter(Texture.FTNearestMipmapLinear)
                texture.setMagfilter(Texture.FTNearest)
                headPart.setTexture(texture, 1)
        if self.style.body == 'b':
            self.generateHead('skullB', animated=True)
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' %
                                         self.style.dept)
            for headPart in self.headParts:
                texture.setMinfilter(Texture.FTNearestMipmapLinear)
                texture.setMagfilter(Texture.FTNearest)
                headPart.setTexture(texture, 1)
        if self.style.body == 'c' and not self.style.name == 'fd':
            self.generateHead('skullC', animated=True)
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' %
                self.style.dept)
            for headPart in self.headParts:
                texture.setMinfilter(Texture.FTNearestMipmapLinear)
                texture.setMagfilter(Texture.FTNearest)
                headPart.setTexture(texture, 1)
        self.generateSkeletonHealthBar()
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
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': self.name,
                                                           'dept': 'Skelecog',
                                                           'level': ' N/A v2.0'}
        if self.isExecutive:
            nameInfo = TTLocalizer.SuitBaseNameWithLevelExe % {'name': self.name,
                                                               'dept': 'Skelecog',
                                                               'level': ' N/A'}
        if self.isManager:
            nameInfo = TTLocalizer.SuitBaseNameWithLevelMgr % {'name': self.name,
                                                               'dept': 'Skelecog',
                                                               'level': ' N/A'}
        if self.isGovernaught:
            nameInfo = TTLocalizer.SuitBaseNameWithLevelGov % {'name': self.name,
                                                               'dept': 'Skelecog',
                                                               'level': ' N/A'}
        self.setDisplayName(nameInfo)
        self.leftHand = self.find('**/joint_Lhold')
        self.rightHand = self.find('**/joint_Rhold')
        self.shadowJoint = self.find('**/joint_shadow')
        self.nametagNull = self.find('**/joint_nameTag')

        self.loop(anim)
        self.isSkeleton = 1

    def makeExecutive(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isExecutive = 1
        if self.isSkeleton:
            self.setSuitClothesSkeleton()
            if self.style.body == 'a' and not self.style.name == 'cg':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                             self.style.dept)
                for headPart in self.headParts:
                    texture.setMinfilter(Texture.FTNearestMipmapLinear)
                    texture.setMagfilter(Texture.FTNearest)
                    headPart.setTexture(texture, 1)
            if self.style.body == 'b':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                             self.style.dept)
                for headPart in self.headParts:
                    texture.setMinfilter(Texture.FTNearestMipmapLinear)
                    texture.setMagfilter(Texture.FTNearest)
                    headPart.setTexture(texture, 1)
            if self.style.body == 'c':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                             self.style.dept)
                for headPart in self.headParts:
                    texture.setMinfilter(Texture.FTNearestMipmapLinear)
                    texture.setMagfilter(Texture.FTNearest)
                    headPart.setTexture(texture, 1)
        else:
            self.setSuitClothes()

    def makeManager(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        if self.isSkeleton:
            self.setSuitClothesSkeleton()
            if self.style.body == 'a' and not self.style.name == 'ts' and not self.style.name == 'cg' and not self.style.name == 'dsk' and not self.style.name == 'blr':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                             self.style.dept)
                for headPart in self.headParts:
                    texture.setMinfilter(Texture.FTNearestMipmapLinear)
                    texture.setMagfilter(Texture.FTNearest)
                    headPart.setTexture(texture, 1)
            if self.style.body == 'b':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                             self.style.dept)
                for headPart in self.headParts:
                    texture.setMinfilter(Texture.FTNearestMipmapLinear)
                    texture.setMagfilter(Texture.FTNearest)
                    headPart.setTexture(texture, 1)
            if self.style.body == 'c' and not self.style.name == 'fd':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                             self.style.dept)
                for headPart in self.headParts:
                    texture.setMinfilter(Texture.FTNearestMipmapLinear)
                    texture.setMagfilter(Texture.FTNearest)
                    headPart.setTexture(texture, 1)
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
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')  # This will only work if you have the texture ttcc_ene_suittex_unemployed.png in phase_3.5/maps, which is the texture that Cogs wear when fired.  This is just in case it can't properly load the above texture.
        texture.setMinfilter(Texture.FTLinearMipmapLinear)
        texture.setMagfilter(Texture.FTLinear)
        modelRoot.find('**/body').setTexture(texture, 1)
        torsoTex = loader.loadTexture('phase_3.5/maps/e_blazer_' + self.style.dept + '.png')
        torsoTex.setMinfilter(Texture.FTNearestMipmapLinear)
        torsoTex.setMagfilter(Texture.FTNearest)
        legTex = loader.loadTexture('phase_3.5/maps/e_leg_' + self.style.dept + '.png')
        legTex.setMinfilter(Texture.FTNearestMipmapLinear)
        legTex.setMagfilter(Texture.FTNearest)
        armTex = loader.loadTexture('phase_3.5/maps/e_sleeve_' + self.style.dept + '.png')
        armTex.setMinfilter(Texture.FTNearestMipmapLinear)
        armTex.setMagfilter(Texture.FTNearest)

    def makeDuckShuffler(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_10/maps/ttcc_ene_suittex_duckshfl.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')  # This will only work if you have the texture ttcc_ene_suittex_unemployed.png in phase_3.5/maps, which is the texture that Cogs wear when fired.  This is just in case it can't properly load the above texture.
        texture.setMinfilter(Texture.FTLinearMipmapLinear)
        texture.setMagfilter(Texture.FTLinear)
        modelRoot.find('**/body').setTexture(texture, 1)
        torsoTex = loader.loadTexture('phase_3.5/maps/e_blazer_' + self.style.dept + '.png')
        torsoTex.setMinfilter(Texture.FTNearestMipmapLinear)
        torsoTex.setMagfilter(Texture.FTNearest)
        legTex = loader.loadTexture('phase_3.5/maps/e_leg_' + self.style.dept + '.png')
        legTex.setMinfilter(Texture.FTNearestMipmapLinear)
        legTex.setMagfilter(Texture.FTNearest)
        armTex = loader.loadTexture('phase_3.5/maps/e_sleeve_' + self.style.dept + '.png')
        armTex.setMinfilter(Texture.FTNearestMipmapLinear)
        armTex.setMagfilter(Texture.FTNearest)

    def makeHighRollerWhite(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_12/maps/cc_t_ene_highroller_suit.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')  # This will only work if you have the texture ttcc_ene_suittex_unemployed.png in phase_3.5/maps, which is the texture that Cogs wear when fired.  This is just in case it can't properly load the above texture.
        texture.setMinfilter(Texture.FTLinearMipmapLinear)
        texture.setMagfilter(Texture.FTLinear)
        modelRoot.find('**/body').setTexture(texture, 1)
        torsoTex = loader.loadTexture('phase_3.5/maps/e_blazer_' + self.style.dept + '.png')
        torsoTex.setMinfilter(Texture.FTNearestMipmapLinear)
        torsoTex.setMagfilter(Texture.FTNearest)
        legTex = loader.loadTexture('phase_3.5/maps/e_leg_' + self.style.dept + '.png')
        legTex.setMinfilter(Texture.FTNearestMipmapLinear)
        legTex.setMagfilter(Texture.FTNearest)
        armTex = loader.loadTexture('phase_3.5/maps/e_sleeve_' + self.style.dept + '.png')
        armTex.setMinfilter(Texture.FTNearestMipmapLinear)
        armTex.setMagfilter(Texture.FTNearest)

    def makeBoardbotManager(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_g_e.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')  # This will only work if you have the texture ttcc_ene_suittex_unemployed.png in phase_3.5/maps, which is the texture that Cogs wear when fired.  This is just in case it can't properly load the above texture.
        texture.setMinfilter(Texture.FTLinearMipmapLinear)
        texture.setMagfilter(Texture.FTLinear)
        modelRoot.find('**/body').setTexture(texture, 1)
        torsoTex = loader.loadTexture('phase_3.5/maps/e_blazer_' + self.style.dept + '.png')
        torsoTex.setMinfilter(Texture.FTNearestMipmapLinear)
        torsoTex.setMagfilter(Texture.FTNearest)
        legTex = loader.loadTexture('phase_3.5/maps/e_leg_' + self.style.dept + '.png')
        legTex.setMinfilter(Texture.FTNearestMipmapLinear)
        legTex.setMagfilter(Texture.FTNearest)
        armTex = loader.loadTexture('phase_3.5/maps/e_sleeve_' + self.style.dept + '.png')
        armTex.setMinfilter(Texture.FTNearestMipmapLinear)
        armTex.setMagfilter(Texture.FTNearest)

    def makePrethinker(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_suittex_prethink.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')  # This will only work if you have the texture ttcc_ene_suittex_unemployed.png in phase_3.5/maps, which is the texture that Cogs wear when fired.  This is just in case it can't properly load the above texture.
        texture.setMinfilter(Texture.FTLinearMipmapLinear)
        texture.setMagfilter(Texture.FTLinear)
        modelRoot.find('**/body').setTexture(texture, 1)
        torsoTex = loader.loadTexture('phase_3.5/maps/e_blazer_' + self.style.dept + '.png')
        torsoTex.setMinfilter(Texture.FTNearestMipmapLinear)
        torsoTex.setMagfilter(Texture.FTNearest)
        legTex = loader.loadTexture('phase_3.5/maps/e_leg_' + self.style.dept + '.png')
        legTex.setMinfilter(Texture.FTNearestMipmapLinear)
        legTex.setMagfilter(Texture.FTNearest)
        armTex = loader.loadTexture('phase_3.5/maps/e_sleeve_' + self.style.dept + '.png')
        armTex.setMinfilter(Texture.FTNearestMipmapLinear)
        armTex.setMagfilter(Texture.FTNearest)

    def makeMultislacker(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_suittex_mslacker.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')  # This will only work if you have the texture ttcc_ene_suittex_unemployed.png in phase_3.5/maps, which is the texture that Cogs wear when fired.  This is just in case it can't properly load the above texture.
        texture.setMinfilter(Texture.FTLinearMipmapLinear)
        texture.setMagfilter(Texture.FTLinear)
        modelRoot.find('**/body').setTexture(texture, 1)
        torsoTex = loader.loadTexture('phase_3.5/maps/e_blazer_' + self.style.dept + '.png')
        torsoTex.setMinfilter(Texture.FTNearestMipmapLinear)
        torsoTex.setMagfilter(Texture.FTNearest)
        legTex = loader.loadTexture('phase_3.5/maps/e_leg_' + self.style.dept + '.png')
        legTex.setMinfilter(Texture.FTNearestMipmapLinear)
        legTex.setMagfilter(Texture.FTNearest)
        armTex = loader.loadTexture('phase_3.5/maps/e_sleeve_' + self.style.dept + '.png')
        armTex.setMinfilter(Texture.FTNearestMipmapLinear)
        armTex.setMagfilter(Texture.FTNearest)

    def makePacesetter(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_suittex_pacesetter.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')  # This will only work if you have the texture ttcc_ene_suittex_unemployed.png in phase_3.5/maps, which is the texture that Cogs wear when fired.  This is just in case it can't properly load the above texture.
        texture.setMinfilter(Texture.FTLinearMipmapLinear)
        texture.setMagfilter(Texture.FTLinear)
        modelRoot.find('**/body').setTexture(texture, 1)
        torsoTex = loader.loadTexture('phase_3.5/maps/e_blazer_' + self.style.dept + '.png')
        torsoTex.setMinfilter(Texture.FTNearestMipmapLinear)
        torsoTex.setMagfilter(Texture.FTNearest)
        legTex = loader.loadTexture('phase_3.5/maps/e_leg_' + self.style.dept + '.png')
        legTex.setMinfilter(Texture.FTNearestMipmapLinear)
        legTex.setMagfilter(Texture.FTNearest)
        armTex = loader.loadTexture('phase_3.5/maps/e_sleeve_' + self.style.dept + '.png')
        armTex.setMinfilter(Texture.FTNearestMipmapLinear)
        armTex.setMagfilter(Texture.FTNearest)
        modelRoot.find('**/hands').setColor(self.handColor)
        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()
        modelRoot.find('**/bowtie').hide()
        modelRoot.find('**/necktie-s').setTexture(texture, 1)
        modelRoot.find('**/necktie-w').setTexture(texture, 1)
        modelRoot.find('**/bowtie').setTexture(texture, 1)
        #modelRoot.find('**/body').setTexture(texture, 1)

    def makePlutocrat(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_10/maps/ttcc_ene_suittex_pcrat.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')  # This will only work if you have the texture ttcc_ene_suittex_unemployed.png in phase_3.5/maps, which is the texture that Cogs wear when fired.  This is just in case it can't properly load the above texture.
        texture.setMinfilter(Texture.FTLinearMipmapLinear)
        texture.setMagfilter(Texture.FTLinear)
        modelRoot.find('**/body').setTexture(texture, 1)
        torsoTex = loader.loadTexture('phase_3.5/maps/e_blazer_' + self.style.dept + '.png')
        torsoTex.setMinfilter(Texture.FTNearestMipmapLinear)
        torsoTex.setMagfilter(Texture.FTNearest)
        legTex = loader.loadTexture('phase_3.5/maps/e_leg_' + self.style.dept + '.png')
        legTex.setMinfilter(Texture.FTNearestMipmapLinear)
        legTex.setMagfilter(Texture.FTNearest)
        armTex = loader.loadTexture('phase_3.5/maps/e_sleeve_' + self.style.dept + '.png')
        armTex.setMinfilter(Texture.FTNearestMipmapLinear)
        armTex.setMagfilter(Texture.FTNearest)

    def makeMouthpiece(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_suittex_mouthp.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')  # This will only work if you have the texture ttcc_ene_suittex_unemployed.png in phase_3.5/maps, which is the texture that Cogs wear when fired.  This is just in case it can't properly load the above texture.
        texture.setMinfilter(Texture.FTLinearMipmapLinear)
        texture.setMagfilter(Texture.FTLinear)
        modelRoot.find('**/body').setTexture(texture, 1)
        torsoTex = loader.loadTexture('phase_3.5/maps/e_blazer_' + self.style.dept + '.png')
        torsoTex.setMinfilter(Texture.FTNearestMipmapLinear)
        torsoTex.setMagfilter(Texture.FTNearest)
        legTex = loader.loadTexture('phase_3.5/maps/e_leg_' + self.style.dept + '.png')
        legTex.setMinfilter(Texture.FTNearestMipmapLinear)
        legTex.setMagfilter(Texture.FTNearest)
        armTex = loader.loadTexture('phase_3.5/maps/e_sleeve_' + self.style.dept + '.png')
        armTex.setMinfilter(Texture.FTNearestMipmapLinear)
        armTex.setMagfilter(Texture.FTNearest)

    def makeMajorPlayer(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_mplayer.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')  # This will only work if you have the texture ttcc_ene_suittex_unemployed.png in phase_3.5/maps, which is the texture that Cogs wear when fired.  This is just in case it can't properly load the above texture.
        texture.setMinfilter(Texture.FTLinearMipmapLinear)
        texture.setMagfilter(Texture.FTLinear)
        modelRoot.find('**/body').setTexture(texture, 1)
        torsoTex = loader.loadTexture('phase_3.5/maps/e_blazer_' + self.style.dept + '.png')
        torsoTex.setMinfilter(Texture.FTNearestMipmapLinear)
        torsoTex.setMagfilter(Texture.FTNearest)
        legTex = loader.loadTexture('phase_3.5/maps/e_leg_' + self.style.dept + '.png')
        legTex.setMinfilter(Texture.FTNearestMipmapLinear)
        legTex.setMagfilter(Texture.FTNearest)
        armTex = loader.loadTexture('phase_3.5/maps/e_sleeve_' + self.style.dept + '.png')
        armTex.setMinfilter(Texture.FTNearestMipmapLinear)
        armTex.setMagfilter(Texture.FTNearest)

    def makeFeatherbedder(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_fbed.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')  # This will only work if you have the texture ttcc_ene_suittex_unemployed.png in phase_3.5/maps, which is the texture that Cogs wear when fired.  This is just in case it can't properly load the above texture.
        texture.setMinfilter(Texture.FTLinearMipmapLinear)
        texture.setMagfilter(Texture.FTLinear)
        modelRoot.find('**/body').setTexture(texture, 1)
        torsoTex = loader.loadTexture('phase_3.5/maps/e_blazer_' + self.style.dept + '.png')
        torsoTex.setMinfilter(Texture.FTNearestMipmapLinear)
        torsoTex.setMagfilter(Texture.FTNearest)
        legTex = loader.loadTexture('phase_3.5/maps/e_leg_' + self.style.dept + '.png')
        legTex.setMinfilter(Texture.FTNearestMipmapLinear)
        legTex.setMagfilter(Texture.FTNearest)
        armTex = loader.loadTexture('phase_3.5/maps/e_sleeve_' + self.style.dept + '.png')
        armTex.setMinfilter(Texture.FTNearestMipmapLinear)
        armTex.setMagfilter(Texture.FTNearest)

    def makeFirestarter(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_fires.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')  # This will only work if you have the texture ttcc_ene_suittex_unemployed.png in phase_3.5/maps, which is the texture that Cogs wear when fired.  This is just in case it can't properly load the above texture.
        texture.setMinfilter(Texture.FTLinearMipmapLinear)
        texture.setMagfilter(Texture.FTLinear)
        modelRoot.find('**/body').setTexture(texture, 1)
        torsoTex = loader.loadTexture('phase_3.5/maps/e_blazer_' + self.style.dept + '.png')
        torsoTex.setMinfilter(Texture.FTNearestMipmapLinear)
        torsoTex.setMagfilter(Texture.FTNearest)
        legTex = loader.loadTexture('phase_3.5/maps/e_leg_' + self.style.dept + '.png')
        legTex.setMinfilter(Texture.FTNearestMipmapLinear)
        legTex.setMagfilter(Texture.FTNearest)
        armTex = loader.loadTexture('phase_3.5/maps/e_sleeve_' + self.style.dept + '.png')
        armTex.setMinfilter(Texture.FTNearestMipmapLinear)
        armTex.setMagfilter(Texture.FTNearest)

    def makeChainsaw(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_chainsaw.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')  # This will only work if you have the texture ttcc_ene_suittex_unemployed.png in phase_3.5/maps, which is the texture that Cogs wear when fired.  This is just in case it can't properly load the above texture.
        texture.setMinfilter(Texture.FTLinearMipmapLinear)
        texture.setMagfilter(Texture.FTLinear)
        modelRoot.find('**/body').setTexture(texture, 1)
        torsoTex = loader.loadTexture('phase_3.5/maps/e_blazer_' + self.style.dept + '.png')
        torsoTex.setMinfilter(Texture.FTNearestMipmapLinear)
        torsoTex.setMagfilter(Texture.FTNearest)
        legTex = loader.loadTexture('phase_3.5/maps/e_leg_' + self.style.dept + '.png')
        legTex.setMinfilter(Texture.FTNearestMipmapLinear)
        legTex.setMagfilter(Texture.FTNearest)
        armTex = loader.loadTexture('phase_3.5/maps/e_sleeve_' + self.style.dept + '.png')
        armTex.setMinfilter(Texture.FTNearestMipmapLinear)
        armTex.setMagfilter(Texture.FTNearest)

    def makeDeepDiver(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_suittex_ddiver.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')  # This will only work if you have the texture ttcc_ene_suittex_unemployed.png in phase_3.5/maps, which is the texture that Cogs wear when fired.  This is just in case it can't properly load the above texture.
        texture.setMinfilter(Texture.FTLinearMipmapLinear)
        texture.setMagfilter(Texture.FTLinear)
        modelRoot.find('**/body').setTexture(texture, 1)
        torsoTex = loader.loadTexture('phase_3.5/maps/e_blazer_' + self.style.dept + '.png')
        torsoTex.setMinfilter(Texture.FTNearestMipmapLinear)
        torsoTex.setMagfilter(Texture.FTNearest)
        legTex = loader.loadTexture('phase_3.5/maps/e_leg_' + self.style.dept + '.png')
        legTex.setMinfilter(Texture.FTNearestMipmapLinear)
        legTex.setMagfilter(Texture.FTNearest)
        armTex = loader.loadTexture('phase_3.5/maps/e_sleeve_' + self.style.dept + '.png')
        armTex.setMinfilter(Texture.FTNearestMipmapLinear)
        armTex.setMagfilter(Texture.FTNearest)

    def makeGatekeeper(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_suittex_gatekeep.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')  # This will only work if you have the texture ttcc_ene_suittex_unemployed.png in phase_3.5/maps, which is the texture that Cogs wear when fired.  This is just in case it can't properly load the above texture.
        texture.setMinfilter(Texture.FTLinearMipmapLinear)
        texture.setMagfilter(Texture.FTLinear)
        modelRoot.find('**/body').setTexture(texture, 1)
        torsoTex = loader.loadTexture('phase_3.5/maps/e_blazer_' + self.style.dept + '.png')
        torsoTex.setMinfilter(Texture.FTNearestMipmapLinear)
        torsoTex.setMagfilter(Texture.FTNearest)
        legTex = loader.loadTexture('phase_3.5/maps/e_leg_' + self.style.dept + '.png')
        legTex.setMinfilter(Texture.FTNearestMipmapLinear)
        legTex.setMagfilter(Texture.FTNearest)
        armTex = loader.loadTexture('phase_3.5/maps/e_sleeve_' + self.style.dept + '.png')
        armTex.setMinfilter(Texture.FTNearestMipmapLinear)
        armTex.setMagfilter(Texture.FTNearest)

    def makeWSI(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_l_exe.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')  # This will only work if you have the texture ttcc_ene_suittex_unemployed.png in phase_3.5/maps, which is the texture that Cogs wear when fired.  This is just in case it can't properly load the above texture.
        texture.setMinfilter(Texture.FTLinearMipmapLinear)
        texture.setMagfilter(Texture.FTLinear)
        modelRoot.find('**/body').setTexture(texture, 1)
        torsoTex = loader.loadTexture('phase_3.5/maps/e_blazer_' + self.style.dept + '.png')
        torsoTex.setMinfilter(Texture.FTNearestMipmapLinear)
        torsoTex.setMagfilter(Texture.FTNearest)
        legTex = loader.loadTexture('phase_3.5/maps/e_leg_' + self.style.dept + '.png')
        legTex.setMinfilter(Texture.FTNearestMipmapLinear)
        legTex.setMagfilter(Texture.FTNearest)
        armTex = loader.loadTexture('phase_3.5/maps/e_sleeve_' + self.style.dept + '.png')
        armTex.setMinfilter(Texture.FTNearestMipmapLinear)
        armTex.setMagfilter(Texture.FTNearest)

    def makeAutocaddie(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_c_exe.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')  # This will only work if you have the texture ttcc_ene_suittex_unemployed.png in phase_3.5/maps, which is the texture that Cogs wear when fired.  This is just in case it can't properly load the above texture.
        texture.setMinfilter(Texture.FTLinearMipmapLinear)
        texture.setMagfilter(Texture.FTLinear)
        modelRoot.find('**/body').setTexture(texture, 1)
        torsoTex = loader.loadTexture('phase_3.5/maps/e_blazer_' + self.style.dept + '.png')
        torsoTex.setMinfilter(Texture.FTNearestMipmapLinear)
        torsoTex.setMagfilter(Texture.FTNearest)
        legTex = loader.loadTexture('phase_3.5/maps/e_leg_' + self.style.dept + '.png')
        legTex.setMinfilter(Texture.FTNearestMipmapLinear)
        legTex.setMagfilter(Texture.FTNearest)
        armTex = loader.loadTexture('phase_3.5/maps/e_sleeve_' + self.style.dept + '.png')
        armTex.setMinfilter(Texture.FTNearestMipmapLinear)
        armTex.setMagfilter(Texture.FTNearest)

    def makeDOPA(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_s_exe.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')  # This will only work if you have the texture ttcc_ene_suittex_unemployed.png in phase_3.5/maps, which is the texture that Cogs wear when fired.  This is just in case it can't properly load the above texture.
        texture.setMinfilter(Texture.FTLinearMipmapLinear)
        texture.setMagfilter(Texture.FTLinear)
        modelRoot.find('**/body').setTexture(texture, 1)
        torsoTex = loader.loadTexture('phase_3.5/maps/e_blazer_' + self.style.dept + '.png')
        torsoTex.setMinfilter(Texture.FTNearestMipmapLinear)
        torsoTex.setMagfilter(Texture.FTNearest)
        legTex = loader.loadTexture('phase_3.5/maps/e_leg_' + self.style.dept + '.png')
        legTex.setMinfilter(Texture.FTNearestMipmapLinear)
        legTex.setMagfilter(Texture.FTNearest)
        armTex = loader.loadTexture('phase_3.5/maps/e_sleeve_' + self.style.dept + '.png')
        armTex.setMinfilter(Texture.FTNearestMipmapLinear)
        armTex.setMagfilter(Texture.FTNearest)

    def makeCountErfit(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isGovernaught = 1
        try:
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_suittex_counterfit.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')  # This will only work if you have the texture ttcc_ene_suittex_unemployed.png in phase_3.5/maps, which is the texture that Cogs wear when fired.  This is just in case it can't properly load the above texture.
        texture.setMinfilter(Texture.FTLinearMipmapLinear)
        texture.setMagfilter(Texture.FTLinear)
        modelRoot.find('**/body').setTexture(texture, 1)
        torsoTex = loader.loadTexture('phase_3.5/maps/e_blazer_' + self.style.dept + '.png')
        torsoTex.setMinfilter(Texture.FTNearestMipmapLinear)
        torsoTex.setMagfilter(Texture.FTNearest)
        legTex = loader.loadTexture('phase_3.5/maps/e_leg_' + self.style.dept + '.png')
        legTex.setMinfilter(Texture.FTNearestMipmapLinear)
        legTex.setMagfilter(Texture.FTNearest)
        armTex = loader.loadTexture('phase_3.5/maps/e_sleeve_' + self.style.dept + '.png')
        armTex.setMinfilter(Texture.FTNearestMipmapLinear)
        armTex.setMagfilter(Texture.FTNearest)

    def makeGovernaught(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isGovernaught = 1
        if self.isSkeleton:
            self.setSuitClothesSkeleton()
            if self.style.body == 'a':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_gov.png')
                for headPart in self.headParts:
                    texture.setMinfilter(Texture.FTNearestMipmapLinear)
                    texture.setMagfilter(Texture.FTNearest)
                    headPart.setTexture(texture, 1)
            if self.style.body == 'b':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_gov.png')
                for headPart in self.headParts:
                    texture.setMinfilter(Texture.FTNearestMipmapLinear)
                    texture.setMagfilter(Texture.FTNearest)
                    headPart.setTexture(texture, 1)
            if self.style.body == 'c':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_gov.png')
                for headPart in self.headParts:
                    texture.setMinfilter(Texture.FTNearestMipmapLinear)
                    texture.setMagfilter(Texture.FTNearest)
                    headPart.setTexture(texture, 1)
        else:
            self.setSuitClothes()

    def getHeadParts(self):
        return self.headParts

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
        if self.style.name == 'msr':
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'kb':
            loadDialog(1)
            return DerrickHandDialogArray
        if self.style.name == 'ts':
            loadDialog(1)
            return DerrickSkeleDialogArray
        if self.style.name == 'jdg':
            loadDialog(1)
            return CLODialogArray
        if self.style.name == 'cfp':
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'le':
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'tc' and not self.isSkeleton:
            loadDialog(1)
            return GatekeeperDialogArray
        if self.style.name == 'tg' and not self.isSkeleton:
            loadDialog(1)
            return FirestarterDialogArray
        if self.style.name == 'tb' and not self.isSkeleton:
            loadDialog(1)
            return MajorPlayerDialogArray
        if self.style.name == 'drm' and not self.isSkeleton:
            loadDialog(1)
            return ChainsawORDialogArray
        if self.style.name == 'cp' and not self.isSkeleton:
            loadDialog(1)
            return DOLADialogArray
        if self.style.name == 'dvk' and not self.isSkeleton:
            loadDialog(1)
            return ReddDialogArray
        if self.style.name == 'fbd' and not self.isSkeleton:
            loadDialog(1)
            return CaseManagerDialogArray
        if self.style.name == 'otm' and not self.isSkeleton:
            loadDialog(1)
            return OttomanDialogArray
        if self.style.name == 'frs' and not self.isSkeleton:
            loadDialog(1)
            return StenographerDialogArray
        if self.style.name == 'gtk' and not self.isSkeleton:
            loadDialog(1)
            return PrethinkerDialogArray
        if self.style.name == 'tcm' and not self.isSkeleton:
            loadDialog(1)
            return ChairmanDialogArray
        if self.style.name == 'ds':
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'hh':
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'rb':
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'gh':
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'adc' and not self.isSkeleton:
            loadDialog(1)
            return ChainsawDialogArray
        if self.style.name == 'ssm':
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'dfr' and not self.isSkeleton:
            loadDialog(1)
            return DOLADialogArray
        if self.style.name == 'bsh' and not self.isSkeleton:
            loadDialog(1)
            return DOLDDialogArray
        if self.style.name == 'tlr':
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'cm':
            loadDialog(1)
            return SkelecogDialogArray
        if self.style.name == 'ggm' and not self.isSkeleton:
            loadDialog(1)
            return MouthpieceDialogArray
        if self.style.name == 'th' and not self.isSkeleton:
            loadDialog(1)
            return RainmakerDialogArray
        if self.style.name == 'kc' and not self.isSkeleton:
            loadDialog(1)
            return WitchHunterDialogArray
        if self.style.name == 'tr' and not self.isSkeleton:
            loadDialog(1)
            return CountErfitDialogArray
        if self.style.name == 'mp' and not self.isSkeleton:
            loadDialog(1)
            return ReddDialogArray
        if self.style.name == 'laa':
            loadDialog(1)
            return SkelecogDialogArray
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
        if self.style.name == 'bgr':
            loadDialog(1)
            return SkelecogDialogArray
        if self.style.name == 'dm' and not self.isSkeleton:
            loadDialog(1)
            return TreekillerDialogArray
        if self.style.name == 'tcc':
            loadDialog(1)
            return SkelecogDialogArray
        if self.style.name == 'cvy':
            loadDialog(1)
            return FemaleDialogArray
        if self.style.name == 'fb':
            loadDialog(1)
            return SkelecogDialogArray
        if self.style.name == 'jl':
            loadDialog(1)
            return SkelecogDialogArray
        if self.style.name == 'gb':
            loadDialog(1)
            return SkelecogDialogArray
        if self.style.name == 'lbs':
            loadDialog(1)
            return SkelecogDialogArray
        if self.style.name == 'trk' and not self.isSkeleton:
            loadDialog(1)
            return PlutocratDialogArray
        if self.style.name == 'dsf' and not self.isSkeleton:
            loadDialog(1)
            return CountErfitDialogArray
        if self.style.name == 'msp' and not self.isSkeleton:
            loadDialog(1)
            return HighRollerDialogArray
        if self.style.name == 'mad' and not self.isSkeleton:
            loadDialog(1)
            return ChainsawORDialogArray
        if self.style.name == 'crf' and not self.isSkeleton:
            loadDialog(1)
            return HighRollerDialogArray
        if self.style.name == 'mdr':
            loadDialog(1)
            return SkelecogDialogArray
        if self.style.name == 'ghd':
            loadDialog(1)
            return OttomanDialogArray
        if self.style.name == 'tyh':
            loadDialog(1)
            return StenographerDialogArray
        if self.style.name == 'jgd':
            loadDialog(1)
            return FeatherbedderDialogArray
        if self.style.name == 'bby':
            loadDialog(1)
            return ChairmanDialogArray
        if self.style.name == 'fd':
            loadDialog(1)
            return DOPADialogArray
        if self.style.name == 'fm' and not self.isSkeleton:
            loadDialog(1)
            return DeepDiverDialogArray
        if self.style.name == 'jb' and not self.isSkeleton:
            loadDialog(1)
            return BellringerDialogArray
        if self.style.name == 'jg' and not self.isSkeleton:
            loadDialog(1)
            return DeskJockeyDialogArray
        if self.style.name == 'jr' and not self.isSkeleton:
            loadDialog(1)
            return PrethinkerDialogArray
        if self.style.name == 'prr' and not self.isSkeleton:
            loadDialog(1)
            return PacesetterDialogArray
        if self.style.name == 'blr':
            loadDialog(1)
            return DOPADialogArray
        if self.style.name == 'dvp' and not self.isSkeleton:
            loadDialog(1)
            return RainmakerDialogArray
        if self.style.name == 'frs' and not self.isSkeleton:
            loadDialog(1)
            return RainmakerDialogArray
        if self.style.name == 'ffm' and not self.isSkeleton:
            loadDialog(1)
            return PlutocratDialogArray
        if self.style.name == 'dsk':
            loadDialog(1)
            return DOPRDialogArray
        if self.style.name == 'gtk' and not self.isSkeleton:
            loadDialog(1)
            return PrethinkerDialogArray
        if self.style.name == 'cp' and not self.isSkeleton:
            loadDialog(1)
            return DOLADialogArray
        if self.style.name == 'cry' and not self.isSkeleton:
            loadDialog(1)
            return StenographerDialogArray
        if self.style.name == 'ffm' and not self.isSkeleton:
            loadDialog(1)
            return PlutocratDialogArray
        if self.style.name == 'sft' and not self.isSkeleton:
            loadDialog(1)
            return PacesetterDialogArray
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

    def generateConnoisseur2(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_connoisseur')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(-.1)
        self.isHud = True

    def generateDownsizer(self):
        self.Vault = loader.loadModel('phase_14/models/char/ttcc_ene_downsizer')
        self.Vault.reparentTo(self.find('**/joint_head'))
        self.Vault.setScale(1)
        self.Vault.setPosHpr(0, 0, 0, 0, 0, 0)
        self.Vault.setZ(0)
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