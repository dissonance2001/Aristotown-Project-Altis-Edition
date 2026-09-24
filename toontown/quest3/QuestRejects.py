"""
Module for NPC reject dialogue and all associated functions.
"""

from copy import deepcopy
import random

from toontown.clashbattle.battle import SuitBattleGlobals
from toontown.hood import ZoneUtil
from toontown.toon.npc import NPCToons
from toontown.toonbase import ToontownGlobals


QuestsRejectDefault = (
    'Heya, _avName_!',
    'Whatcha need?',
    'Hello! How are you doing?',
    'Hi there.',
    "How's it going?",
    "Sorry _avName_, I'm a bit busy right now.",
    'Yes?',
    'Howdy, _avName_!',
    'Welcome, _avName_!',
    "Hey, _avName_! How's it hanging?",
    "Need any help?",
    "Hi _avName_, what brings you here?"
)
QuestsRejectYott = (
    'Greetings, _avName_.',
    'What dost thou needeth?',
    'Greetings! How dost thou?',
    'Welcometh, traveller.',
    "How goeth it?",
    "Forgiveth me, _avName_, I'm a bit busy right now.",
    'Yes?',
    'How doth thou, _avName_?',
    'What sayeth thee, _avName_?',
    "Good morrow, _avName_. How hangeth it?",
    "Needeth any help?",
    "_avName_, what bringeth thou here?"
)
QuestsRejectYottNPCs = []
# Yott Playground
for npcId in range(7000, 7012 + 1):
    QuestsRejectYottNPCs.append(npcId)
# Knight Knoll
for npcId in range(7100, 7119 + 1):
    QuestsRejectYottNPCs.append(npcId)
# Noble Nook
for npcId in range(7200, 7221 + 1):
    QuestsRejectYottNPCs.append(npcId)
# Wizard Way
for npcId in range(7300, 7317 + 1):
    QuestsRejectYottNPCs.append(npcId)
QuestsRejectYottNPCs.remove(7303)   # Mad Ernage does not have yottspeak

QuestsRejectTumbles = (  # Tumbles
    "Hey, maaaaaaan.",
    "Got something?",
    "What's new, pal?",
    "Ay, how are ya?",
    "Toontown looks righteous! Have ya noticed the scenery?",
    "How can I help ya, maaaaaaan?"
)
QuestsRejectTumblesCold = (  # Tumbles
    "H-h-hey, maaaaaaan.",
    "G-g-got something?",
    "W-w-what's new, pal?",
    "Trrrrr.. it's s-so cold...",
)
QuestsRejectDefined = {
    # Cog HQs
    12101: (  # Judy
        "Please, _suitName_. I'm rather busy at the moment.",
        'Schedule an appointment for some other time.',
        'Talk to my secretary.',
        "Not now! This puzzle won't solve itself!",
        'Important business only, please.',
        "Sorry, can't talk right now, _suitName_."),
    # Major characters
    2001: (  # Flippy
        "I hope your day has been Toontastic!",
        "What brings you to my office?",
        "Hello _avName_! How is your stay in Toontown?",
        "I think I could use a secretary..."),
    2003: (  # Professor Pete
        "Did you know using Gags effectively requires some math?",
        "If you have questions about those Cogs, I will try to help in any way I can!",
        "When will you be coming back to class?",
        "Expand your mind, _avName_!"),
    2007: (  # Lowden
        "Anything new to report?",
        "What can I do to help, Ranger?",
        "Keep those Gags stocked. You may never know when you need them.",
        "Disguises are only used in the Headquarters. No, not this Headquarters."),
    2008: (  # Mata Hairy
        "If you have a report, hand it to Lowden.",
        "If you ever have any questions about Cashbots, I am your Toon.",
        "Since when have Cogs learned to smell?",
        "Is there anything I can do to assist?"),
    2009: (  # Bumpy Bumblebehr
        "What can I do for you, pal?",
        "Know your limits! You don't want to take on more than you can BEAR.",
        "I wonder how my three daughters are doing...",
        "Watch out for those Lawbots on the streets!"),
    2010: (  # Good Ol' Gilliam Gil Giggles G. Gall
        "If you are ever hungry, be sure to swing by! I always bring some homemade snacks.",
        "Have you seen the C.E.O.'s banquet choices? Yuck!",
        "It's hard to sneak around certain areas of Bossbot Headquarters without that four-armed Cog finding me!",
        "If you got any questions about Bossbots, do let me know!"),
    9801: (  # Doctor Dimm
        "Come to help with my studies?",
        "I wonder what that crazy monkey is up to...",
        "Got any toonsten filament I could use for my nightlights?",
        "Did you know that red is the ideal color for nightlights? It's true!"),
    3004: (  # Rocky
        "Got any Jellyfish sandwiches?",
        "The cold weather isn't that bad once you get used to it.",
        "I think I should just take a month's vacation during Halloween...",
        "Thanks for keeping those Lawbots off my tail.",
        # April Toons-specific
        # "Do you think there are any vampires among us, _avName_?",
        # "That purple building at Polar Place looks real suspicious, don'tcha think?",
        # "Vampires. All. Stink.",
        # "When I get off my shift, I'm going to vent to Dr. Easy over some Hambrrrgers.",
        # "I fear no Cog. But...",
        # "I'm calling an emergency meeting with Flippy soon, this vampire situation is getting ridiculous!",
        # "We managed to sabotage Lawbot HQ, but I can't even eject a single vampire from my own house..."
    ),
    3112: (  # Lil Oldman
        "You do not need my assistance.",
        "Go away.",
        "I'm in the middle of something.",
        "What.",
        "Shoo! SHOO! Away with you!"),
    5313: (  # Coach Z
        "Be sure to have strong Gags in a fight. Or else.",
        "Any news about Lima? No?",
        "Remember not to use Sound on Lured Cogs.",
        "Here at the Squash & Stretch, we toughen your knowledge in Sellbots!"),
    7010: (  # Timothy Riddle
        "Spare change?",
        "Have any extra snacks?",
        "Diddily-deed, diddly-dood! You are now enchanted to give me some food!",
        "Can you ask them to turn the heat up in here? It's freezing!"),
    7205: (  # Webster
        "Is there something you inquire about?",
        "If there is something you wish to learn of, I have books that can answer anything.",
        "I hope the purpose of your visit does not include dockets...",
        "What information can I provide to you?"),
    7003: (  # Al Bumbledorf
        "If you ever see a snake, take care of it immediately.",
        "I wonder what the boy is up to nowadays...",
        "Trust me young one, I am older than I look.",
        "Toons are stronger together and weaker when separate."),
    4119: (  # Moe Zart
        "It's hard to keep track of time. I'll start composing, then next thing you know, it's four in the morning.",
        "If you ever need lessons, be sure to stop by!",
        "You're keeping those Cashbots in check... right?"
    ),
    1116: (  # Barnacle Bessie
        "Have you tried water-skiing? I highly recommend it!",
        "Never go out alone in the fog!",
        "It is thanks to Doctor Dimm I have the best lighthouse lights!"),
    90042: QuestsRejectTumbles,
    90043: QuestsRejectTumbles,
    90044: QuestsRejectTumbles,
    90045: QuestsRejectTumbles,
    90046: QuestsRejectTumbles,
    90047: QuestsRejectTumbles,
    90048: QuestsRejectTumbles,
    90049: QuestsRejectTumbles,
    # More taskline npcs
    2134: (  # Silent Simone
        ''
    ),
    5204: (  # Bert.
        "Did you bring any dirt?",
        "You are dirty, no dirt party for you.",
        "You brought dirt? Let's party!",
        "You're a fan of dirt? Name all types of dirt."),
    1420: (  # Salty Spit-toon (Reg)
        "Welcome to the Salty Spit-toon.",
        "Hey kid, how tough are ya?",
        "Can ya open this bottle of ketchup?",
        "Think tough, like Reg."
    ),
    5416: (  # Cool Ray
        "Heyyyyy, what's up?",
        "Sup, _avName_.",
        "That's a real DAB moment, dawg!",
        "I'm the raddest Toon in town!"
    ),
    4408: (  # Barry B.
        "Hey, ya like jazz?",
        "I couldn't decide if I wanted to wear yellow and black or black and yellow today!",
        "I got all B's on my report card!"
    ),
    4406: (  # Kazoo Kid
        "KAAAAZZZOOOOOO!!",
        "I wanna have fun, fun, fun, fun, FUN!!",
        "Waait a minute, who ARE you?",
        "You know what? I think we're gonna be friends."
    ),
    2311: (  # Franz Neckvein
        "Velcome to my gym.",
        "Hello, leetle Toon.",
        "Remember to use ze legs, not ze back."
    ),
    3015: (  # Steve the Snowman
        "Ice to meet you, _avName_!",
        "It's a little warm out here, don't you think?",
        "Are my coal buttons fastened?",
        "You ever wonder how there's bears in these waters?",
        "It's snow great to see you!"
    ),
    6203: (  # Professor Pi
        "Prepare for combat, _avName_.",
        "Are you here for tanning supplies, or to train?",
        "Are those Bossbots taken care of?"
    ),
    # Random places
    9001: (  # Snooze Bar (Snoozin' Susan)
        "Welcome to the Snooze Bar!",
        "Can I getcha something?",
        "I assure you, _avName_, this is a restaurant."
    ),
    9003: (  # DDL library (Drowsy Dennis)
        "Welcome to Lullaby Library!",
        "A good book always puts me to sleep.",
        "I assure you, _avName_, this is a library.",
        "Look at all these books!"
    ),
    2002: (  # TTC bank (Banker Bob)
        "Need to make a deposit?",
        "Welcome to the bank, _avName_!",
        "Can I open an account for you?",
        "Our adding machines are over 20 years old!"
    ),
    2005: (  # TTC library (Librarian Larry)
        "Shh. Be quiet.",
        "I'm trying to read here.",
        "...",
        "Do you need something?"
    ),
    # Non-taskline NPCs
    3138: (  # Chef Bumblesoup
        'Come crack your teeth into a freshly-frozen Hambrrrger!',
        'Nobody can do it like Hambrrrgers does it!',
        'Would you like a side of frozen fries with that?',
        'Guaranteed 30-minute brain freeze with our slushies, or your money back!',
        'My hambrrrgers are selling like cold cakes!',
        'What\'s your order number?',
        'Here to claim your 10% off? I\'m gonna need to see those cracked teeth and a receipt.'
    )
}
QuestsRejectDefinedWinter = {
    90043: QuestsRejectTumblesCold,
}


def getNpcInfo(npcId):
    npcName = NPCToons.getNPCName(npcId)
    npcZone = NPCToons.getNPCZone(npcId)
    hoodId = ZoneUtil.getCanonicalHoodId(npcZone)
    hoodName = base.cr.hoodMgr.getFullnameFromId(hoodId)
    buildingName = NPCToons.getBuildingTitle(npcZone)
    branchId = ZoneUtil.getCanonicalBranchZone(npcZone)
    streetName = ToontownGlobals.StreetNames[branchId][-1]
    isInPlayground = ZoneUtil.isPlayground(branchId)
    return (npcName, hoodName, buildingName, streetName, isInPlayground)


def getNpcLocationDialog(fromNpcId, toNpcId):
    if not toNpcId:
        return (None, None, None, None)
    fromNpcZone = None
    fromBranchId = None
    if fromNpcId:
        fromNpcZone = NPCToons.getNPCZone(fromNpcId)
        fromBranchId = ZoneUtil.getCanonicalBranchZone(fromNpcZone)
    toNpcZone = NPCToons.getNPCZone(toNpcId)
    toBranchId = ZoneUtil.getCanonicalBranchZone(toNpcZone)
    toNpcName, toHoodName, toBuildingName, toStreetName, isInPlayground = getNpcInfo(toNpcId)
    if fromBranchId == toBranchId:
        if isInPlayground:
            streetDesc = 'in this playground'
            street = 'in this playground'
        else:
            streetDesc = 'on this street'
            street = 'on this street'
    elif isInPlayground:
        streetDesc = 'in the %s playground' % toHoodName
        street = 'in the %s playground' % toHoodName
    else:
        streetDesc = 'on %(toStreetName)s in %(toHoodName)s' % {
            'toStreetName': toStreetName,
            'toHoodName': toHoodName
        }
        street = 'on %(toStreetName)s' % {'toStreetName': toStreetName}

    paragraph = '\x07%(building)s "%(buildingName)s"...\x07...%(buildingVerb)s %(street)s.' % {
        'building': "%s's building is called" % toNpcName,
        'buildingName': toBuildingName,
        'buildingVerb': 'which is',
        'street': streetDesc
    }

    return (paragraph, toBuildingName, streetDesc, street)


def chooseQuestDialogReject(npcId):
    if npcId in QuestsRejectDefined:
        if not QuestsRejectDefined[npcId]:
            return ''
        return random.choice(QuestsRejectDefined[npcId])
    if npcId in QuestsRejectYottNPCs:
        return random.choice(QuestsRejectYott)
    return random.choice(QuestsRejectDefault)


def fillInQuestNames(text: str, avName: str=None, fromNpcId: int=None, toNpcId: int=None, av=None):
    text = deepcopy(text)
    toNpcName = ''
    fromNpcName = ''
    where = ''
    buildingName = ''
    streetDesc = ''
    street = ''

    if avName is not None:
        text = text.replace('_avName_', avName)
    if av is not None:
        if hasattr(av, 'suit'):
            suitName = SuitBattleGlobals.SuitAttributes[av.suit.style.name]['name']
        else:
            suitName = avName
        text = text.replace('_suitName_', suitName)
    if toNpcId:
        toNpcName = str(NPCToons.getNPCName(toNpcId))
        where, buildingName, streetDesc, street = getNpcLocationDialog(fromNpcId, toNpcId)
    if fromNpcId:
        fromNpcName = str(NPCToons.getNPCName(fromNpcId))

    replacements = {
        '_toNpcName_':    toNpcName,
        '_fromNpcName_':  fromNpcName,
        '_where_':        where,
        '_buildingName_': buildingName,
        '_streetDesc_':   streetDesc,
        '_street_':       street,
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text
