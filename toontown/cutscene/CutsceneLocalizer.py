"""
Dialogue and other text for cutscenes or cutscene-like scenarios
"""

# region -=- Toontorial -=-
# Script for the Combat Tutorial
TutorialCombat = (
    # Turn 0 (Squirt)
    (
        ["Ready to train? First thing's first, the battle interface!"],
        # Show Toons Panels
        ["At the bottom, each Toon has a panel that includes their Laff Meter and what they're planning to do."],
        # Show Cog Panels
        ["Cogs also have their own panels, located at the top. This shows their health and level."],
        # Show Gag Panel
        ["But most importantly, we have your inventory of Gags smack dab in the middle!",
         "Each row represents a Gag Track. I'll be walking you through the uses of each one.",
         "Something to remember is that Gags are used in Track order, from top to bottom. Now let's get to using some!"],
        # Allow Gag to be used
        ["Here's a \1GagTrack_squirt\1Squirt\2 Gag for you to use on that Desk Jockey! Click on it to attack!"],
    ),
    # Turn 1 (Drop) (summon 1 dummy after this turn)
    (
        ["Great shot! As you might have noticed, it took some \1BattleInfo_Damage\1Damage\2, shown by the number that popped up!",
         "Also, they became \1BattleInfo_SoakText\1Soaked\2!"],
        # Arrow Pointing at Status Effects
        ["\1BattleInfo_SoakText\1Soaked\2 is something we call a Status Effect, which you can see is slotted into that Cog's panel.",
         "Hovering over a Status Effect will give you a brief description of what it does. It's good to always be aware of the situation!",
         "One of the benefits of \1BattleInfo_SoakText\1Soaked\2 is that the Cog is less likely to dodge our gags."],
        # Allow Gag to be used
        ["This is a great time to use \1GagTrack_drop\1Drop\2! It's a very powerful type of Gag, but has low accuracy."],
    ),
    # Turn 2 (Zap) (the new dummy should die to this attack)
    (
        ["Nice, we both hit it! Because of that, we dealt bonus \1BattleInfo_Combo\1Combo\2 damage!",
         "\1GagTrack_squirt\1Squirt\2, \1GagTrack_throw\1Throw\2 and \1GagTrack_drop\1Drop\2 Gags deal \1BattleInfo_Combo\1Combo\2 damage when used with other Gags of their track.",
         "However, they used an ability that summoned another Cog! Fortunately, we have ways of dealing with multiple Cogs at once.",
         "\1GagTrack_zap\1Zap\2 Gags can only affect \1BattleInfo_SoakText\1Soaked\2 Cogs, but their electricity can jump to other \1BattleInfo_SoakText\1Soaked\2 targets."],
        # Allow Gag to be used
        ["How about you use \1GagTrack_zap\1Zap\2 while I use \1GagTrack_squirt\1Squirt\2 to \1BattleInfo_SoakText\1Soak\2 both of them?"],
    ),
    # Turn 3 (Lure)
    (
        ["Good teamwork! We even managed to destroy one of them. Hopefully Pete won't be mad about that..."],
        # Arrow Pointing at Status Effects
        ["Notice how the Cog isn't \1BattleInfo_SoakText\1Soaked\2 anymore? \1GagTrack_zap\1Zap\2 dries off all the Cogs it hits!"],
        ["Also, when I \1BattleInfo_SoakText\1Soaked\2 the Cog next to the one I targeted, it was dealt a little bit of \1GagTrack_squirt\1Splash\2 damage."],
        # Allow Gag to be used
        ["Anyways, let's move on. Go ahead and use a \1GagTrack_lure\1Lure\2 Gag now."],
    ),
    # Turn 4 (Throw)
    (
        ["Guess our friend found that quite alluring!"],
        # Arrow Pointing at Status Effects
        ["\1GagTrack_lure\1Lured\2 is a Status Effect just like \1BattleInfo_SoakText\1Soaked\2, so you can hover over it for info as well!",
         "\1GagTrack_lure\1Lured\2 guarantees that our \1GagTrack_squirt\1Squirt\2, \1GagTrack_throw\1Throw\2 and \1GagTrack_sound\1Sound\2 Gags will hit."],
        # Allow Gag to be used
        ["Let's take advantage of it by using \1GagTrack_throw\1Throw\2 Gags!"],
    ),
    # Turn 5 (Trap) (summon 3 dummies after this turn and start attacking Lowden)
    (
        ["Oof! That sure was a splat fest! See how it was \1BattleInfo_Knockback\1Knocked Back\2 and isn't \1GagTrack_lure\1Lured\2 anymore?",
         "Both \1GagTrack_throw\1Throw\2 and \1GagTrack_squirt\1Squirt\2 Gags deal bonus damage equal to the \1BattleInfo_Knockback\1Knockback\2 value of the \1GagTrack_lure\1Lured\2 effect.",
         "Other sources of damage will still \1GagTrack_lure\1Unlure\2 the Cog but will not gain \1BattleInfo_Knockback\1Knockback\2 damage, so be careful!",
         "In addition, \1GagTrack_drop\1Drop\2 Gags cannot hit \1GagTrack_lure\1Lured\2 Cogs."],
        # Allow Gag to be used
        ["The next track I'll have you use is \1GagTrack_trap\1Trap\2. Go ahead and throw down a banana peel!"],
    ),
    # Turn 6 (Toon-Up)
    (
        ["Ouch! I wasn't expecting that... Pete's been messing with the script, I guess.",
         "When you start fighting actual Cogs, they will attack every turn after the Toons finish using their Gags.",
         "Ugh! Anyway, you can see that the \1GagTrack_trap\1Trap\2 hasn't done anything yet.",
         "Cogs must be \1GagTrack_lure\1Lured\2 into \1GagTrack_trap\1Traps\2 for them to work.",
         "This many Cogs isn't a good situation... I'm going to \1GagTrack_lure\1Lure\2 them all with my magnet so that they can't attack."],
        # Allow Gag to be used
        ["Could you give me a \1GagTrack_toon-up\1Toon-Up\2 to help me shake off that hit I took earlier? It will also help my accuracy!"],
    ),
    # Turn 7 (Sound) (all of the desk jockeys should die to this attack)
    (
        ["That fall's gotten them \1BattleInfo_DazedText\1dazed\2 and confused now!"],
        ["\1GagTrack_trap\1Traps\2 deal lots of damage and also apply the \1BattleInfo_DazedText\1Dazed\2 effect.",
         "Similar to \1BattleInfo_SoakText\1Soaked\2, \1GagTrack_trap\1Dazed\2 makes the Cog less likely to dodge our attacks."],
        ["Now then, I've had about enough of these Desk Jockeys!",
         "Time for the last track, \1GagTrack_sound\1Sound\2! It hits all the Cogs in the battle!"],
        # Allow Gag to be used
        ["\1GagTrack_sound\1Sound\2 off, rookie!"],
    ),
    # Turn 8 (direct damage gag of choice) (player gets hit by dummy turn before)
    (
        ["Are you OK, rookie? This Desk Jockey is a tough one..."],
        ["Using \1GagTrack_sound\1Sound\2 gives you the \1BattleInfo_EncoreText\1Encore\2 effect, which makes your next gag stronger!",
         "If you use \1GagTrack_sound\1Sound\2 when you have \1BattleInfo_EncoreText\1Encore\2, however, you'll become "
         "\1BattleInfo_WindedText\1Winded\2, which makes your \1GagTrack_sound\1Sound\2 Gags weaker for a few turns.",
         "And that should be everything you need to know about fighting Cogs!"],
        ["I'll give you a \1GagTrack_toon-up\1Toon-Up\2 to get you back to full laff. Choose a Gag to finish this fight!"]
    ),
)

# Script for the start of the tutorial, before you go into the training room. Pete lets you know the basic controls.
TutorialPreTrainingRoomScript = {
    0: "Hey, Professor Pete! Here's that Toon I was talking about earlier-- mind showing them the ropes?",
    1: "Sure thing, Lord Lowden Clear! Could you set things up in the training room?",
    2: "Roger! I'll see you shortly, rookie.",
    3: "Hey there, friend! Let's get the simple stuff out of the way. You can move your Toon with the MOVEMENT keys! The default buttons are W, A, S and D.",
    4: "Alright, now try JUMPING! The default button is SPACE BAR!",
    5: "Looking good! Speaking of looking, you can rotate your camera by holding RIGHT CLICK. You can even combine it with movement!",
    6: "To really get moving, try SPRINTING! The default button for it is SHIFT!",
    7: "Mess around as much as you want, then come up to me when you're ready to continue.",
    8: "Great job! Welcome to Toontown, a place full of laughter and fun!\x07Well... that's the idea at least.\x07Lowden will be able to explain our situation better than I can, though.\x07Speaking of, he should be ready for you by now!",
    9: "Go ahead and check out the training room!",
}

# Script for when you enter the training room, right before the combat tutorial. Lowden briefs you on Laff and Cogs.
TutorialTrainingRoomScript = {
    1: "Welcome to the training room, rookie! Let's get you prepared!",
    2: "First thing's first: you need a Laff Meter! Now where is it...",
    3: "Ah, there it is! Your Laff Meter signifies how happy you are at any point in time!",
    4: "However, if your Laff hits 0...",
    5: "You'll become sad and will be sent back to the nearest playground!\x07Luckily, when in the playground, you can find treasures! These will heal you back up quickly.",
    6: "Why would your Laff hit 0, you may ask?",
    7: "Well, you see, currently we are under an invasion. An invasion conducted by robots.\x07We call them Cogs.",
    8: "These no fun robots can't take a joke. Thankfully, jokes are our specialty!\x07Gags are used to battle the Cogs around town, and I'm going to teach you how to use them!",
    9: "Let's get started! Approach that Cog dummy over there!",
    10: "Get that Desk Jockey!",
    11: "Great job, rookie! I think you're ready to take on the Cogs!\x07You now have a very tough decision to make. Which two Gag Tracks will you start with?\x07Once you've decided, head back out to the classroom. Pete will want to talk with you.\x07I've got to get back to Toon HQ now. See ya, rookie!"
}

# Script for after you finish the combat tutorial in the training room. Pete tells you important non-combat info.
TutorialPostTrainingRoomScript = {
    1:  "Welcome back! I take it that training went well?\x07Well, I have a few welcome gifts for you! They do require some explanation, though.",
    2:  "This is your Shtickerbook! It contains all sorts of handy tools to help you around Toontown. Go ahead and open it!",
    3:  "This is the Districts page. Each District is a copy of Toontown. If you want to meet up with friends, make sure you're in the same District!",
    4:  "Let's continue to the next page, shall we?",
    5:  "This is the Map page, where you can view the entirety of Toontown! Some parts of town are covered by clouds, but they will become visible once you've visited them!\x07The 'Go Home' button will take you to your own Toon estate, while the 'Minigames' button will take you to the Minigames area! The 'Playground' button takes you to the nearest playground.",
    6:  "That's everything for the Map page, let's continue to the next one.",
    7:  "This is your ToonTasks page. Here, you can see everything you're assigned to do around Toontown! Oh look, you have one right now!",
    8:  "Looks like Mayor Flippy wants to see you in Toon Hall after this. Let's hurry onto the next page then!",
    9:  "This is the Items and Codes section, here is where you can customize your Toon!",
    10: "Let's continue to the Clothing tab of the page.",
    11: "This is your Toon's wardrobe! It's pretty empty right now since you just got here, but there are many ways to expand your fashion!",
    12: "You look Toontastic right now regardless! Let's continue to the next page.",
    13: "Now, this is your Cog Gallery. We don't have much information on the Cogs right now, so you'll have to fill this out as you encounter them.\x07There are lots of other useful pages in the Shtickerbook, so make sure to check them out when you get the chance!",
    14: "Go ahead and close the Shtickerbook now.",
    15: "Has everything I said made sense?",
    16: "Cat got your tongue?\x07Oh, you must not know how to speak with SpeedChat yet!",
    17: "Click the SpeedChat button on the far left to say something to me!",
    18: "Great job!",
    19: "By the way, you aren't locked to just these phrases. You can expand the Chat Panel to freely type what you'd like and see what others are saying.\x07Oh, and one more thing...",
    20: "Here you go!",
    21: "This is the Experi-o-Meter, where the experience you earn from doing activities around town goes!\x07Your level will increase as you gain more experience.\x07This unlocks all kinds of cool things, like Training Points, increased Gag storage, and increased Laff!",
    22: "That's all from me! Flippy wants to see you in Toon Hall, so head there first!"
}
# endregion

# region -=- Battle -=-
# region -=- Suit -=-
# region -=- Visual Effects -=-
MultislackerEndMandatoryLunch = [
    ["Ahh, that hit the spot!",
     "Sigh... lunch break over...",
     "Hmm, maybe I should add more kerosene next time."],
    ["Oh, you're still here?",
     "Did you enjoy your break as well?",
     "Thanks for covering for me, guys.",
     "Could you just leave already?"]
]
# endregion
# region Instance Bosses
MultislackerForemanJoinDialogue = ["We've got work to do, gentlemen."]
MajorPlayerStartMatching = [
    "Have I got a special tune just for you, baby!",
    "Woah-oh! Don’t get spooked by Bru’s boogie-woogie, babe.",
    "Oh now-now-now here's the fan favorite feature!",
    "Don't get burnt by the beat!",
    "Come on babe, everyone is watching!",
    "I told ya you'd dance! Can't resist the rhythm.",
    "Get ready for the sforzando commando, babe!",
    "Gotta dance animato espressivo baby-o!",
    "I'll lead this dance just follow these steps...",
    "Let me show you how to swing!",
    "Just try to get this tune out of your head!"
]
MajorPlayerDanceCommand = "DANCE!"
MajorPlayerResultGood = ["Smooth steps babe, you've danced this dance before! Now here's a real rockin' rhythm!"]
MajorPlayerResultBad = [
    "Don't be blue, babe. I get it, I get it. Not everyone can match the Master's musical movements!",
    "Ooo baby blue, did I do a number on you!",
    "Takes two to tango, babe. Not two left feet.",
    "Oh no-no-no, babe, you are all off tempo!",
    "I told you to follow my moves babe, not.... whatever that was.",
    "What? First time being asked to dance?",
    "Sorry babe, that's not enough--I don't slow dance.",
    "Sorry babe, it's finito!",
    "Rhythm like a steam engine, and you better stay off the tracks babe.",
]
MajorPlayerLastTapDanceSuccess = [
    "Holy boogie woogie, baby! You really know how to play I must say!",
    "Keep up that june-bug jump, and this musical master might put your noted name on the album too!",
]
HighRollerDiceRouletteDialog = [
    # Starting dice roll...
    ("Lady Luck, you better be on my ffide tonight! Let'ff roll on it!",
     "Everyone getff a piece of thiff! No Ffuit or Toon left unharmed.",
     "Where the diffe will land, nobody knowff--effept for me!",
     "Hoping we don't land on ffnake eyeff here, right folkff?",
     "Pain iff ffhared equally between all participantff."),
    # Nothing
    ("Look'ff like nuffin!!",
     "Aww ratff, a total bufft!!",
     "Lady Luck iff merffiful today, huh?",
     "Ffhew! Not that waff a cloffe call, waffn't it, folkff?",
     "And THAT iff why they call you our LUCKY contefftantff!"),
    # Suits hit
    ("Here it comeff, boyff!",
     "WHAT A TWIFFT!!!",
     "And the ratingff FFKYROCKET!!!",
     "Now, you ffigned up for thiff!",
     "'FFLAM!' What a ffweet ffound!"),
    # Toons hit
    ("If it meanff anything, thiff iff gonna hurt me a lot more than it hurtff you!",
     "Can't ffquaffh and fftretch your way out of thiff one, Toonff!",
     "Who'ff ready for ffome cartoon violenffe?!",
     "Fforry, babe, but the ratingff don't lie! Thiff iff what the viewerff want!",
     "'Ker-ffplat!' HahAHAHA!!! You Toonff really are funny!"),
]
HighRollerMinigameResultsDialogue = [
    ("Well, babe, let'ff not keep them waiting! HAHAHA!!!",
    "Better hope for ffome HIGH ROLLERFF! HAHAHAHA!",
    "Come on, babe, FFHOW UFF THOFFE NUMBERFF!",
    "Ready to find out which one of you iff really the weakefft link?!",
    "WAFFN'T THAT FUN? Let'ff ffee how you did!"),
    "Ha-HA!"
]
HighRollerAceInTheHoleDialogue = [
    ("It'ff time for my cloffe up! You're getting in all of the action now, folkff!",
     "Ffhrouded in mifft, you'll ffoon ffee who'ff in control of the ffhow now!",
     "You know, I've alwayff got an affe up my ffleeve! Ffee?",
     "I'm a flying affe, fforaring in the fog! Prepare to be ffcared, babe.",
     "I'm the biggefft ffenffation, the talk of the town! Hope you haven't forgotten, doll.")
]
HighRollerPhaseTwoDialogue = [
    "WhAHAHAHAt a ffhow!",
    "Oooo-hooo-hooo, ratingff are ffkyrocketing! Line goeff up, head turner! Keep thoffe cameraff rollin'!",
    "Let'ff ffee the nefft big play for today!",
    "WHAT A TWIFFT, BUTTERCUP BLUE!",
    "Hope the folkff at home are ready for a real ffhowfftopper!",
    "Give a warm, hot on the oven, flaff fire, round of applauffe for my ffecond favorite ffet of...",
    ["Lollyggaggerff, tomfoolerff, jokerff, hoaxerff, trickffterff, jokeffmithff, humoriftfth,",
    "Jefterff, hooliganff, goofballff, ffharletonff, ffcounderlff, rapffcallinff, miffcreantff, jokeffterff, japerff, hoodlumff,",
    "Ffcallywagff, clownff, quipffterff, harlequinff, buffoonff, wiffecrackerff, raffcalff, ne'er-do-wellff",
    "Rabbelroufferff, ffhenaiganifferff, goofffterff, merrymakerff, ruffianff, ffkylarkff, gooberff,",],
    "Knuckleheadff... the very ffpeffial... Dave Brubot Quartet! Ffanff a ffimiliar ffafe, of courffe!!",
    "Bring 'em in, baby doll!",
    "Have fun with thiff one, ffweetie pie!",
]
HighRollerEndingDialogue = [
    "NOW FAT FAF A FREAL FADIO FROCK FTOP!",
    "They'll ffave thif viffage on the ffpotlight for any Golden Age hit!",
    "You know the play of the game, the tune ain't tame, gotta keep the ffhow ROLLIN'!",
    "Let'ff get in the hot ffhot eye-ffpot ffpotlight one lafft time before they roll the credtiff, humdinger!",
    "Give a big one for the headline, top banana!",
    "...What'ff that whifftling ffound?",
]
HighRollerCreditsInitial = [
    ("Executive Producer", "Major Player"),
    ("Non-executive Producer", "Chip Fan Club President"),
    ("Non-producing Executive", "Duck Shuffler"),
    ("Writer", "Hat Rack"),
    ("Gaffer", "Bendy Bendson"),
    ("Tape", "Bottom Feeder"),
    ("Cog Wrangler", "Emmett Basil"),
    ("1st Runner", "Who"),
    ("2nd Runner", "What"),
    ("3rd Runner", "I don't know"),
    ("Flunky Trainer", "Leaf Blower"),
    ("Focus Puller", "Hand Holder"),
    ("Foley Artist", "Con Artist"),
    ("Hype Ducks", "Low Ballers"),
    ("Grip", "Vacant"),
    ("Title", "Name"),
    ("Drip Meister", "Flundger"),
    ("Dividend King", "Dividend King"),
    ("Contest Winner!!!", "Pencil Pusher!\nCongrats to Pencil Pusher for winning the HIGH ROLLER Sticky Note x500 Pack!"),
    ("Personal Trainer", "Count Chad Erfit"),
    ("Plant Caretaker", "Thomas Saggs"),
    ("Nutritionist", "Count Vladimir Erclaim"),
    ("'Chup Sourcer", "Count Vladimir Erclaim"),
    ("Body Double", "Key Actor"),
    ("General Manager", "Micromanager"),
    ("On-location Meteorologist", "Rainmaker"),
    ("Father Figure", "John Toontown"),
    ("Cereal Soaker", "Milkman"),
    ("Toontown Cinematic Universe Founder", "Jaymo"),
    ("Special Thanks", "The 100+ Flunkies who risked their lives in the name of stunning performance! (As many Flunkies as possible were harmed during the production of this episode.)"),
    ("The Viewer", "That's you!!!"),
]
HighRollerCreditsFinal = [
    "High Roller",
    "Adventurous Animation",
    "Curious Creature",
    "Trivia Titan",
    "????????????",
]
HighRollerTeleporterAdvertising = [
    "Have you guyth heard of High Roller'th High Roller? It'th the betht!!!",
    "Pttht! Hey! Come over here!",
    "You Toonth like gameth, right? Becauthe you're gonna LOVE thith!!!",
    "High Roller'th High Roller hath the highetht thtaketh! Like, thuper high!",
    "Do you have time to thpare? We know a GREAT way to thpend it!!!",
]
HighRollerTeleporterPreTutorial = [
    "Hey! I think they're lookin' for you in... Toon Hall, wath it?",
    "Oh, you're the Toon that blue guy wath lookin' for! Yeah, Flippy!",
    "Hey, I heard that Flippy guy needth ya. Talk with him, THEN we'll watch the show!!!",
    "Aren't the Toon Hall folk lookin' for you? Thomethin' about Flippy needin' to talk with you?",
    "Wait, are you...? Woah, Flippy hath been looking for you EVERYWHERE, don'tcha know?",
]
HighRollerTeleporterFirstInteract = [
    "Oh my gosh, we got thomeone! We got thomeone! Thay your line!",
    "Oh!!! Uh... \"Hello, Toon! Do you like high caketh?\"",
    "It'th \"thtaketh,\" not \"caketh!\" Ugh, I'll do it.",
    "Hey, Toon! We're the Low Ballerth, and we're here to invite YOU to Mr. High Roller'th show!",
    "Yeah, yeah! It'th the greatetht, in cathe you didn't know. And tho ith Mr. High Roller!!!",
    "Oh my gosh, right? I've never theen shadeth that cool. Like, EVER.",
    "Lithten! We have our own fan club; The Low Rollerth!",
    "Yeah! And anyone who jointh getth a thpecial warp thraight to the show!",
    "What'dya thay? Are you in???",
    # Player prompt to nod their head
    "THEY'RE IN!!!",
    "YETH!!! Welcome to the Low Rollerth, buddy!",
    "If you ever wanna uthe that warp, jutht come to uth! You'll be there in no time!!!",
]
HighRollerTeleporterPromptTeleport = [
    "Hey, Toon! Do you wanna watch Mr. High Roller'th show? You should!!!",
    "Hey! Mr. High Roller'th show ith about to thtart!!! Do you wanna watch with uth?",
    "Hello, fellow Low Roller!!! Are you ready for the show of your life?",
    "Toon! We're about to watch Mr. High Roller'th show! Come with uth!!!",
    "Hey there, Toon! Are you ready to rock with Mr. High Roller?!",
]
HighRollerTeleporterAcceptTeleport = [
    "Aw, yeah! Let'th go!!!",
    "I knew it!!! You never dithapoint, Low Roller!",
    "YEAH!!! I mean, cool. Good dethision.",
    "Thpoken like a true Low Roller!!!",
    "Awethome!!! We'll thee you there! Be sure to bring thnackth!!!",
]
HighRollerTeleporterDenyTeleport = [
    "What? That'th not very \"Low Roller\" of you!!!",
    "Really? You're joking right? Pleathe thay you're joking...",
    "Uhm... I thought Low Rollerth watched all of Mr. High Roller'th showth, right?",
    "Theriouthly!? Are you a really real, hardcore Low Roller? Then you gotta thay \"yeth!\"",
    'Oh, no, that\'th the part where you thay, "Yeth pleathe, fellow Low Roller!"',
]
HighRollerTeleporterLobbyNotInteracted = "Hey there! Are you gonna watch Mr. High Roller'th show too?!"
HighRollerTeleporterLobbyPromptTeleport = [
    'Hey there! Do you wanna head back to your... Uh, "playground," wath it?',
    "Howdy! Ready to head back home?",
    "Hey, fellow Low Roller! Do you want uth to thend you back home?",
    "Hello! Do you wanna go home? To reflect on the show, of courthe!!!",
    "Mr. High Roller'th showth are intenthe, huh? Wanna head back?",
]
HighRollerTeleporterLobbyAcceptTeleport = [
    "Cool beanth! Here goeth!",
    "Thoundth cool! I hope you had fun!",
    "Alright! And be sure not to mith out on the next show, okay?",
    "Anything for a fellow Low Roller! Let'th go!",
    "Okay! You'll be back for the next show, right?",
]
HighRollerTeleporterLobbyDenyTeleport = [
    "Wanna watch more? I totally get you!!!",
    "Hooked on the show and jutht can't leave?! Me too, bud.",
    "Ooh, thoundth like thomeone wantth to watch again!!!",
    "I get it, it'th hard to leave thomething tho cool tho far behind!",
    "Thpoken like a true Low Roller! We could thtay here all day!!! I think.",
]
HighRollerTeleporterGUIWantTeleport = "Would you like to teleport to the \1deepRed\1Major Player's Lobby\2 in Mezzo Melodyland to watch \1deepYellow\1HIGH ROLLER'S HIGH ROLLER\2?\n\nYou can teleport back to the playground at any time by talking to the \1deepGreen\1Low Ballers inside the lobby\2."
HighRollerTeleporterLobbyGUIWantTeleport = "Would you like to teleport back to the {0} playground?\n\nYou can teleport back to the \1deepRed\1Major Player's Lobby\2 to watch \1deepYellow\1HIGH ROLLER'S HIGH ROLLER\2 at any time by talking to the \1deepGreen\1Low Ballers in the playground\2."
# endregion
# endregion
# endregion
