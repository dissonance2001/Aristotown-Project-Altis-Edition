"""
The localizer file for Quest names and other data.
"""
from toontown.quest3.QuestDialogue import QuestTextGigaDict
from toontown.quest3.QuestEnums import QuestSource, QuestItemName, QuestItemName
from toontown.quest3.base.QuestReference import QuestReference, QuestId
from toontown.quest3.base.QuestText import QuestText
from toontown.quest3.SpecialQuestZones import SpecialQuestZones as SQZ
from toontown.toonbase import ToontownGlobals

"""
QUEST SOURCE
"""

SourceDescriptions = {
    QuestSource.MainQuest:  'For the main taskline.',
    QuestSource.SideQuest:  'For any offered sidetasks.',
    QuestSource.Directive:  'For any overclocked Directives.',
    QuestSource.DailyQuest: 'For any quests offered daily.',
    QuestSource.ClubQuest:  'For any quests designed for Clubs.',
    QuestSource.KudosQuest: 'For any rank-up Kudos Tasks.',
}

"""
QUEST HEADLINES
"""

# The task headlines for quest chains.
QuestChainHeadlines = {
    QuestSource.MainQuest: {
        1: "Welcome to Toontown!",
        2: "Time for First Impressions",
        3: "Zit's Time to Pump Iron",
        4: "Jokey Jam",
        5: "Sticky Situation",
        6: "The Numbers Mason...",
        7: "Letter Rip!",
        8: "A Taste of Toontown",
        9: "Gathering Gags",
        10: "Smart Minds Think Unalike",
        11: "Find The Rain",
        12: "Oh, Barnacles!",
        13: "Someone's Been Drinking Saltwater...",
        14: "First Day of School!",
        15: "Big Binnacle Bash",
        16: "Big Binnacle Bash",
        17: "Contacting Live Support...",
        18: "Baby's First Steps",
        19: "Unite The Buccaneers!",
        20: "I Can See Clearly Now...",
        21: "A Captain For Hire",
        22: "Ye Olde Cog Bash!",
        23: "Ye Olde Cog Bash!",
        24: "Ye Olde Missing Postage",
        25: "Cog Flu",
        26: "Executing The Executives",
        27: "Executing The Executives",
        28: "Researching The Executed",
        29: "Ye Olde Restoration Project",
        30: "Ye Olde Restoration Project",
        31: "Trained and Ready",
        32: "Wilted Sunflowers",
        33: "Bert.",
        34: "Never Out Of Style",
        35: "A Boxing Lesson To Forget",
        36: "Not So Vine...",
        37: "Not So Vine...",
        38: "Reed's Needs",
        39: "Secret Agent Toon",
        40: "The Great Factory Haul",
        41: "The Last Training",
        42: "Tracing Tasty Treasure",
        43: "LaughTrack.mp3",
        44: "KAAAAZOOOOOOO!",
        45: "Chop Shop Blues",
        46: "Dull Scissors & Expectations",
        47: "To Catch a Cashbot",
        48: "The Plan's a Go",
        49: "Oldman On Vacation?",
        50: "The New Heater",
        51: "That Smelly Smell",
        52: "Prepping For The Winter?",
        53: "FIND THE OLDMAN!",
        54: "Lil' Old Eyes",
        55: "Cog Suit Architect",
        56: "Actually Help Rocky",
        57: "It's a Hard Knock Life",
        58: "Or Your Money Back!",
        59: "Stir Crazy",
        60: "Crazy Construction Time",
        61: "Help The Needy",
        62: "Silence Is Golden",
        63: "The Best Investment Is...",
        64: "All Rise",
        65: "All Rise",
        66: "It's Time.",
        67: "The Star of The Show",
        68: "Wakey, Wakey!",
        69: "Bahama Pajama Drama",
        70: "The Not-So-Tucked-Inn",
        71: "Battle Of The Bedheads",
        72: "Lawfully Strange",
        73: "All-Seeing Eye Doctors",
        74: "Gathering Intel",
        75: "The Day Is Saved!",
    },
    QuestSource.SideQuest: {
        1: "Pete's Apology",
        2: "Trashcat Troubles",
        3: "Cream-Be-Gone",
        4: "Fire Safety",
        5: "Monkey See Monkey Do",
        6: "New Toony Tourist",
        7: "Pilfering Propellers",
        8: "Dressing Sea-Lads & Lasses",
        9: "The Salty Spit-toon",
        10: "The Salty Spit-toon",
        11: "Straight to Boardwalk",
        12: "First Mate Makeover",
        13: "Swimming Kiwi",
        14: "Used To Be An Adventurer",
        15: "Dungeon Duty",
        16: "Page Studying 101",
        17: "Midlife Crisis",
        18: "Midlife Crisis",
        19: "Not-So-Tall Tales",
        20: "The Golden Penny",
        21: "The Secret Weapon",
        22: "Garden Tending",
        23: "The Magical Fruit",
        24: "Not-So-Instant Film",
        25: "Not-So-Instant Film",
        26: "Greener Thumbs",
        27: "Wedding Planner",
        28: "Triple Scoop, Please!",
        29: "Big Band Marching.",
        30: "Flat Notes & Profiles.",
        31: "Flat Notes & Profiles.",
        32: "What's That Sound?",
        33: "Got You Covered!",
        34: "Piano Player",
        35: "Ice Cold Warmth",
        36: "Bundle Up!",
        37: "Snow Pale",
        38: "Stevey The Snowman!",
        39: "Stevey The Snowman!",
        40: "Hybernation Invitation",
        41: "Gathering Warmth",
        42: "FORE!!",
        43: "Suit Up, Ranger.",
        44: "Down We Go",
        45: "Training Season",
        46: "When Nature Calls",
        47: "Survival Kit Builder",
        48: "Alternative Transportation",
        49: "MerchandiZzzing",
        50: "Short Story",
        51: "Short Story",
        53: "The Ol' West",
        54: "Camera Repair",
        55: "Bugged Out Bughunter",
        56: "Baked Goods",
        57: "Playing Dress-Up",
        58: "Knit Up Goods",
        59: "Presidential Appreciation",
        60: "Santa's Outfit",
        61: "Bigger Bags",
        62: "Antler Adhesive",
        63: "ELF Enrollment",
        64: "Fashion Design",
        65: "Tree Topper",
        66: "Candy Maker",
        67: "Board Up",
        68: "Stocking Stuffers",
        69: "A Task from the Past",
        70: "Toonsmas Day Feast",
        71: "For Years to Come...",
    },
    QuestSource.Directive: {
        1: "Report Roundup",
        2: "Crossword Crisis",
        3: "Needle Nonsense",
        4: "Temperature Troubles",
        5: "Docket Dilemma",
        6: "Memo Mishap",
        7: "Fashion Fiasco",
    },
    QuestSource.KudosQuest: {
        1: 'Taking Out The Trash',
        2: 'Panic! At the Discount',
        3: 'Give and Cake',
        4: 'The Mysterious Duck',
        5: 'Easy As Pie In The Sky',
        6: 'An Oldie but a Goodie',
        7: 'Double Coil and Trouble',
        8: 'Scraping News',
        9: 'Brainiacs in the Basement',
        11: 'Are you squidding me?',
        12: 'Sandcastle Savings',
        13: 'Silverware Sting',
        14: 'Salt, Pepper, Paprika',
        15: 'Stopping the Scuttlebutt',
        16: 'Huge Oppor-tuna-ty',
        17: '7th Layer Wrapping Paper',
        18: 'Barbarian Barbara',
        19: 'A Misty Mystery',
        21: 'Reinforced Training',
        22: 'Box Machina',
        23: 'Doodragon Festival',
        24: 'At The Gate',
        25: 'Good Toons or Bad Toons?',
        26: 'Unsweet Tooth',
        27: 'Fishing Fiasco',
        28: 'The Royal Grail',
        29: 'Looming Lawbot',
        31: 'Forecast Fallacy',
        32: 'Ant Stop Me Now',
        33: 'Groovy Paintings',
        34: 'Ringing the Right Bell',
        35: 'Floral Fisticuffs',
        36: 'Top-Notch Tuft Toons',
        37: 'Quaking and Breaking',
        38: 'Miss-ting Mail',
        39: 'The Couch Slouch',
        41: 'Networking?',
        42: 'Banker Besties',
        43: 'Rocked Out',
        44: 'Cookie Conundrum',
        45: 'Fools Brass',
        46: 'Bach in Business',
        47: 'Phonic Phraudulence',
        48: 'Musical Monstrosity',
        49: 'Let\'s Dance!',
        51: 'Tour De Brrrgh',
        52: 'Slippery Circuit!',
        53: 'Paula\'s Parent Present Party',
        54: 'I\'m Melting, I\'m Melting!',
        55: 'Snowglobal Emergency!',
        56: 'Art for Auntie',
        57: 'Soup Served Sad',
        58: 'Keeping Cool',
        59: 'Joining the System',
        61: 'Beanevolent Mr. Bean',
        62: 'Easy Elementary Earnings',
        63: 'Perilous Party Preparations',
        64: 'The Side of Caution',
        65: 'Dendrochrojewelry',
        66: 'Pet A\'tree\'ciation',
        67: 'Nathan\'s Nutrition',
        68: 'Nuthing to Sneeze At',
        69: 'I Saw What I Chain-Saw',
        71: 'Professor Problem\'s Peril',
        72: 'Quiet Hours',
        73: 'Candy Conundrum',
        74: 'Make Your Bed and Lie in It',
        75: 'What Night is It?',
        76: 'No Time for Beauty Sleep',
        77: 'Doze Were Mine!',
        78: 'So easy, you could do it in your sleep!',
        79: 'Give it a Rest!',
    }
}


# The task headlines for specific objectives on specific quest chains.
QuestChainObjectiveHeadlines = {
    QuestSource.MainQuest: {
        3: {
            1: "A Hairy Introduction",
        },
        5: {
            1: "Big Bumpin'",
        },
        12: {
            5: "Butter Flippers",
            6: "Butter Flippers",
            7: "Butter Flippers",
        },
        13: {
            1: "Butter Flippers",
        },
        14: {
            1: "Someone's Been Drinking Saltwater...",
            2: "Red Rover, Red Rover...",
        },
        17: {
            1: "Meet Misty",
        },
        19: {
            1: "The Important Stuff",
        },
        20: {
            1: "Charting Smart Charts",
            2: "Charting Smart Charts",
            3: "Charting Smart Charts",
            4: "Charting Smart Charts",
            5: "Charting Smart Charts",
            6: "Unite The Buccaneers!",
        },
        21: {
            11: "The Weakest Link",
            12: "The Weakest Link",
            13: "The Office",
            14: "The Office",
        },
        22: {
            1: "Flippy's Plans",
            2: "Ye Olde Basics",
        },
        24: {
            1: "Dangalf's Lessons",
        },
        28: {
            1: "Executing The Executives",
            2: "Executing The Executives",
        },
        30: {
            8: "The Secret In The Dungeon",
        },
        32: {
            1: "Trained and Ready",
            2: "The Zucchini",
            3: "The Rose",
            11: "Where The Grass Grows...",
            12: "Where The Grass Grows...",
            13: "Where The Grass Grows...",
            14: "Where The Grass Grows...",
            15: "Where The Grass Grows...",
            16: "Where The Grass Grows...",
        },
        33: {
            1: "Ketchum?",
            13: "Never Out Of Style",
            14: "Never Out Of Style",
        },
        35: {
            1: "Never Out Of Style",
            2: "Never Out Of Style",
            3: "Petunia's Place",
            10: "Not So Vine...",
        },
        38: {
            1: "Hard to Reed",
        },
        39: {
            1: "Reed's Needs",
            2: "Rose's Words",
            3: "Stretch and Squash",
            4: "Lima... Seen?",
            5: "Enter The Big Scary Place",
        },
        41: {
            1: "What's Behind Door #1?",
            4: "The Great Market Crash",
        },
        42: {
            1: "Flippy's Been Expecting You",
            2: "Can Anybody Find Moe...",
        },
        46: {
            1: "Going Through The Moetions",
            2: "Going Through The Moetions",
            3: "Slow Cruising",
            4: "Slow Cruising",
            5: "Slow Cruising",
            10: "Take a Deeeeep Breath",
            11: "Take a Deeeeep Breath",
            12: "Take a Deeeeep Breath",
        },
        47: {
            4: "Mints, Anyone?",
        },
        48: {
            2: "The Vault Heist",
            3: "The Show Must Go On",
        },
        49: {
            1: "Rocky Joins The Battle",
            2: "Ye Olde Wizarde",
            3: "Ye Olde Wizarde",
            4: "Home's Where the Wizard's At?",
            5: "Home's Where the Wizard's At?",
            6: "Let's Retrace His Steps...",
            7: "Let's Retrace His Steps...",
            12: "Lil' Oldman! Lil' Oldman?",
            13: "Lil' Oldman! Lil' Oldman?",
            14: "Lil' Oldman! Lil' Oldman?",
        },
        50: {
            1: "The Ol' Pub",
            2: "The Ol' Pub",
            13: "The Magic Cap",
            14: "The Magic Cap",
            15: "The Magic Cap",
            16: "The Magic Cap",
            17: "The Magic Cap",
            18: "The Magic Cap",
        },
        53: {
            3: "Mingle The Mingler",
            4: "Destroy The Mingler",
            5: "REALLY Destroy The Mingler",
            6: "Please the Oldman",
            7: "Please the Oldman",
        },
        54: {
            1: "Look Good, Feel Good",
            8: "Sweet Buck Tooth",
            9: "Sweet Buck Tooth",
            10: "Blast From The Past!",
            11: "Blast From The Past Pt. 2!",
        },
        55: {
            1: "Helping Rocky",
            2: "Nevermind, Helping Oldman",
            3: "Is This Malpractice?",
            9: "Just Another Day At The Office",
        },
        56: {
            2: "Bumpy Plans",
            3: "Topple The Law",
        },
        57: {
            1: "Flippy's Message",
            2: "First Draft Pick",
            3: "Enlisting In The Army",
        },
        58: {
            1: "First Impressions",
        },
        59: {
            1: "Or Your Money Back!",
        },
        60: {
            1: "Stir Crazy",
        },
        61: {
            1: "Crazy Construction Time",
        },
        62: {
            1: "Help The Needy",
        },
        63: {
            1: "Silence Is Golden",
        },
        64: {
            1: "The Best Investment Is...",
        },
        65: {
            2: "Surprise Supplies Check!",
            3: "A Real Banquet Breaker",
        },
        66: {
            1: "A Real Banquet Breaker",
            2: "Suit Up.",
        },
        67: {
            2: "But Wait, There's More?",
            3: "The Dimm Doctor",
            4: "The Rumbling in Drowsy Dreamland",
            5: "Fitting Into The Crowd",
        },
        68: {
            5: "Eggs and Bakey!",
            6: "Just a Hunch...",
            7: "Just a Hunch...",
            8: "Look What I Found!",
            9: "Back To It!",
        },
        69: {
            1: "Zee Exterminatah",
            2: "Zee Exterminatah",
            3: "Zee Exterminatah",
            4: "Zee Exterminatah",
        },
        70: {
            1: "Dozin'",
            2: "Another Hunch...",
            3: "Is it the Golden Ticket?",
            4: "I've Been Working In The Dreamland...",
        },
        71: {
            1: "Bring Us A Dream",
            2: "Bring Us A Dream",
            3: "Bring Us A Dream",
            4: "Bring Us A Dream",
        },
        72: {
            1: "Snoozin'",
            2: "It's Time To Pay Up",
            3: "It's Time To Pay Up",
            4: "It's Time To Pay Up",
            9: "Three Pieces...",
        },
        74: {
            1: "Yes. Hand Development Affairs.",
            2: "Not-So-Secret Secret Agent",
            6: "Delivering Intel",
            7: "LORD LOWDEN CLEAR, HELP!!!",
            8: "Put Me In, Coach.",
            9: "The Final Battle. For Now.",
        },
    },
}

# Auxillary text by quest objective.
# This is text that usually appears in between the icon geoms.
QuestObjectiveAuxillaryText = {
}

# Quest info text.
# Format strings are provided here.
QuestInfoFormats = {

}

# Descriptions for sidequests on the sidequest directory.
SideQuestDescriptions = {
    QuestSource.SideQuest: {
        1: "Professor Pete feels remorseful for the drama he's put you through during your first moments in Toontown, and he's willing to make it up to you!",
        2: "Travis the Trashcat has been busy keeping Toontown's streets clean for a long time, but now he needs your help!",
        3: "Nona Seeya's vanishing cream has been flying off the shelves! Either that or it's been vanishing itself! Help her and reap the rewards!",
        4: "Things have been a bit... explosive at Short Fuses' shop. Help him get his next big project going, and you'll get some fancy new fireproof threads!",
        5: "Liar, liar, pants on fire! ...Or is it? These two monkey Toons are in a heated squabble. Try to make sense of it and get rewarded!",
        6: "Tumbles has come to Toontown! Have a talk with him and enjoy the sights maaaaaaan.",
        7: "N.D. Skye is a top merchant for selling Airplanes, but he's no pilot! Despite this, he does have a way to get around Barnacle Boatyard preeeetty quickly!",
        8: "Aye, me matey! You best be dressed for sailing when roaming the boardwalks of Barnacle Boatyard! Fishy Frank will set ye up!",
        9: "How tough are ya'? Reg is the main man and bouncer to The Salty Spit-toon, one of the most exclusive sailor clubs in Toontown. No weenies allowed!",
        10: "How tough are ya'? Reg is the main man and bouncer to The Salty Spit-toon, one of the most exclusive sailor clubs in Toontown. No weenies allowed!",
        11: "Davey Drydock loves long walks along the boardwalk, inspecting it, and... being completely terrified of it. Why? Better go see for yourself!",
        12: "Choppy McDougals a talented Toon. The best at shining peglegs and patching eyepatches! And he's willing to give you the perfect pirate makeover!",
        13: "Tumbles has made his way to Barnacle Boatyard. He wants to enjoy the beach, but needs your help!",
        14: "Ariel Septim VII has had quite the pain in the knee as of late! Help him become pain-free, and you'll travel nearly as good as he did back in the day!",
        15: "Timmy Riddle's been locked away for good after disobeying the elders. But... maybe you could learn a thing or two from him still...",
        16: "Suit up, young page, for you shall begin your required training for knighthood. A prestigious honor amongst Ye Olde Toontowne Toons!",
        17: "Youthful Yannis just isn't feeling quite the same these days... Visit him and help him feel the youthfulness inside him once more!",
        18: "Youthful Yannis just isn't feeling quite the same these days... Visit him and help him feel the youthfulness inside him once more!",
        19: "Thea Troubadour has told some of the tallest tales of Ye Olde Toontowne. But could his latest tale actually tell some truth?",
        20: "Tumbles has found the wishing well in Ye Olde Toontowne, and he'd like to make a wish! Maybe you could help him?",
        21: "Samantha Spade is on the hunt to crack the case on the big, secret weapon! Help her, and she'll give you some intel of her own in exchange!",
        22: "Tracy Trowel has done it! She's created quite possibly her finest piece of clothing yet! Visit and you might just get a pair!",
        23: "Beans, beans, the magical fruit. The more you eat, the more you... you get the idea. Help Stinky Jim out, and get a free fruit basket of your own!",
        24: "Cynthia's got her hands on a brand new instant-film camera! Or... maybe slightly used... a few times...",
        25: "Cynthia's got her hands on a brand new instant-film camera! Or... maybe slightly used... a few times...",
        26: "Eugene's made a shocking new discovery after testing new dyes for his green bean jeans. You better head over right away and see what's up!",
        27: "Tumbles has made his way to Daffodil Gardens and would like to help set-up a wedding! Perhaps you could lend a hand?",
        28: "Luciano Scoop's looking for his next big scoop for tomorrow's newspaper! Report on a few headline material stories, and get a paparazzi's dream reward!",
        29: "Step in line! Grab your instruments! Tootie Twostep has some uniforms prepared, and you're next in the marching line to receive one!",
        30: "Barry B. is an expert at exterminating flat notes, and teaching Toons the way of jazz. If you're in need of jazzy clear-minded focus, you better head over!",
        31: "Barry B. is an expert at exterminating flat notes, and teaching Toons the way of jazz. If you're in need of jazzy clear-minded focus, you better head over!",
        32: "Toons everywhere are experiencing a case of the \"Big head\". Take a trip on down, what's the worst that could happen?",
        33: "Got a hole in the roof? Leaky? Just that time again to replace it? Tony Deff has you covered. Until he runs out of supplies, that is... Why not help?",
        34: "Tumbles has made it to Mezzo Melodyland and it makes him want to play some music! Maybe you can help him get his hands on a piano?",
        35: "Solar Ray's spent all his toony life studying solar panels and using it in his own items. Help him, and learn a trick that he picked up along the way!",
        36: "Johnny Cashmere's a warm puppy in a very, very cold place. It doesn't make for the best results! Help Johnny keep warm, and you'll get warm as well!",
        37: "Eddie The Yeti is notable for having a stunning complexion. If you have a word with him, he might tell you how he maintains it!",
        38: "Steve The Snowman has come to life! Why bother reading the rest of this description? Go talk to the talking snowman!",
        39: "Steve The Snowman has come to life! Why bother reading the rest of this description? Go talk to the talking snowman!",
        40: "Paula Behr's on a mission to make The Brrrgh known as the go-to vacation spot. You even get to show off the special perk Toons can get!",
        41: "Tumbles wants to help Toons in The Brrrgh keep warm! If you find him you might be able to help!",
        42: "Hanniball is a big-time provider of all things golf. The Cogs love golf. The Cogs take from Hanniball frequently. Help him with this, and get rewarded!",
        43: "Tolkein A. Hiking has his eyes on you to be the brand new park ranger of Acorn Acres! You better head down there right away and start your duties!",
        44: "On one fateful day, Problematic Pete got stumped on a question, and his legs shrunk! Now he sells this ability for profit, and you might be able to get in on it too!",
        45: "Training season is upon us! You gotta work it! Pump that iron! Don't skip leg day, or else you'll upset Coach GaZebo!",
        46: "Toilet-trees are practical, and T.P. Papre is a practical Toon. Help get his practical product placed practically everywhere, and you'll be presented with a practical prize!",
        47: "Tumbles is in Acorn Acres and wants a souvenir! Maybe you could get one for him?",
        48: "Car? Plane? Horse? ...Sheep? Any way to travel around is useful to Orville... probably... Assist him by traveling on over to his shop!",
        49: "Zari is a zany and zealous zalesman, and they're not gonna ztop until their warez are zold! Ztop by and get yourzelf a nice prize!",
        50: "Ready for your bedtime story? Better head on over to Babyface MacDougal's shop. You'll be sent on a wild ride. Don't worry though, it's short!",
        51: "Ready for your bedtime story? Better head on over to Babyface MacDougal's shop. You'll be sent on a wild ride. Don't worry though, it's short!",
        53: "Cowboy George is tired of the norm. He's here to have a little western fun! If you're into that idea, then saddle up and head on over to his shop!",
        54: "Tumbles has dropped his camera before making it to Drowsy Dreamland and it is in dire need of repair. Could you help him?",
        55: "Bay T. Tester is a bashful boy around big beta bugs, and these bountiful butterflies are beyond big! Be a big benefit to Bay T. Tester and bounce those big bugs back and be rewarded!",
        56: "Jen Jerbread is just as excited for Toonsmas in Toonseltown as everyone else! However, they seem to be having a shortage on ingredients for their gingerbread... Maybe you could stop by and help?",
        57: "Tinker has been trying to create some special clothes based on his toys with Granny Thread! You should assist them in creating the clothing and they may give you a pair in return!",
        58: "Granny Thread is trying to create a cute little sweater based on Bernard the Elf, she may even give you the sweater if you help her!",
        59: 'You should appreciate the "president.',
        60: "Pepper Minstix has left Santa's outfit at the drycleaners and forgot which one he left it at! Please help them find Santa's outfit or Toonsmas is ruined!",
        61: "St. Bernard is helping Santa prepare for his big day, but it seems his bag isn't big enough for all of the goodies he has for the Toons!",
        62: "Rudolph is worried about losing his antlers after the holiday season ends! Perhaps you should speak to him and find a solution?",
        63: "Santa has returned to his day job after a hard night of delivering presents! Perhaps you should stop by and see if there isn't anything you can do for him.",
        64: "Someone needs some help with putting together their newest fasion! Maybe you should stop by and help!",
        65: "One of the elves in Toonseltown loves putting the star on the tree! However, they need protection from the pine needles.",
        66: "We're making candy canes! Stop by and make your own!",
        67: "The Toons of Toonseltown appreciate what you've done for them! You should help them put together your fun reward!",
        68: "The Toons around Toonseltown want to show their appreciation to you in the form of stocking stuffers! Ask around!",
        69: "Candie LaBrum is very fascinated with the history of Toontown and loves to collect artifacts from the past. They are the 'Spirit of Toonsmas Past', and they need your help!",
        70: "Perez Cent doesn’t like being corrected or talked back to, for he knows all, (so he says) and is a bit bossy. That being said, he needs your help with the Toonsmas feast!",
        71: "Corgi Diem is the spirit from the future that watches of Candie LaBrum and Perez Cent. They have some presents they would like your help delivering!",
    },
    QuestSource.Directive: {
        1: "Judy's got some rewards in store for hard-working Lawbots! Put in some work and you'll get to move up the executive corporate ladder! (Part 1)",
        2: "Judy's got some rewards in store for hard-working Lawbots! Put in some work and you'll get to move up the executive corporate ladder! (Part 2)",
        3: "Judy's got some rewards in store for hard-working Lawbots! Put in some work and you'll get to move up the executive corporate ladder! (Part 3)",
        4: "Judy's got some rewards in store for hard-working Lawbots! Put in some work and you'll get to move up the executive corporate ladder! (Part 4)",
        5: "Judy's got some rewards in store for hard-working Lawbots! Put in some work and you'll get to move up the executive corporate ladder! (Part 5)",
        6: "Judy's got some rewards in store for hard-working Lawbots! Put in some work and you'll get to move up the executive corporate ladder! (Part 6)",
        7: "Judy's got some rewards in store for hard-working Lawbots! Put in some work and you'll get to move up the executive corporate ladder! (Part 7)",    
    },
}

# Rewards for sidequests on the sidequest directory.
SideQuestRewards = {
    QuestSource.SideQuest: {
        1: "TTC Teleport Access",
        2: "Trashcat Outfit",
        3: "Invisible Cheesy Effect",
        4: "Firefighter Outfit",
        5: "Zany Nametag",
        6: "Selfie Pose",
        7: "Barnacle Boatyard Teleport Access",
        8: "Sailor Outfit",
        9: "Big Legs Cheesy Effect + Nautical Nametag",
        10: "Big Legs Cheesy Effect + Nautical Nametag",
        11: "Boardwalk Nametag",
        12: "Wonky Nametag",
        13: "Diving Pose",
        14: "Ye Olde Toontowne Teleport Access",
        15: "Ye Olde Toontowne Color Filter Option",
        16: "Knight Outfit",
        17: "Transparent Cheesy Effect + Poetic Nametag",
        18: "Transparent Cheesy Effect + Poetic Nametag",
        19: "Small Head Cheesy Effect",
        20: "Casting Pose",
        21: "Daffodil Gardens Teleport Access",
        22: "Gardening Outfit",
        23: "Samba Hat",
        24: "Flat Portrait Cheesy Effect + Silly Nametag",
        25: "Flat Portrait Cheesy Effect + Silly Nametag",
        26: "Green Toon Cheesy Effect",
        27: "Running Pose",
        28: "Mezzo Melodyland Teleport Access",
        29: "Marching Band Outfit",
        30: "Flat Profile Cheesy Effect + Whimsical Nametag",
        31: "Flat Profile Cheesy Effect + Whimsical Nametag",
        32: "Big Head Cheesy Effect",
        33: "Fancy Nametag",
        34: "Presenting Pose",
        35: "The Brrrgh Teleport Access",
        36: "Snowflake Outfit",
        37: "No Color Cheesy Effect",
        38: "Wireframe Cheesy Effect + Shivering Nametag",
        39: "Wireframe Cheesy Effect + Shivering Nametag",
        40: "Big White Toon Cheesy Effect",
        41: "Surprised Pose",
        42: "Acorn Acres Teleport Access",
        43: "Park Ranger Outfit",
        44: "Small Legs Cheesy Effect",
        45: "Big Toon Cheesy Effect",
        46: "Practical Nametag",
        47: "Greened Pose",
        48: "Drowsy Dreamland Teleport Access",
        49: "Zzz Outfit",
        50: "Small Toon Cheesy Effect + Action Nametag",
        51: "Small Toon Cheesy Effect + Action Nametag",
        53: "Western Nametag",
        54: "Yawning Pose",
        55: "Beta Tester Outfit",
        56: "Gingerbread Outfit",
        57: "Traditional Tin Soldier/Ragdoll outfit",
        58: "Ugly Sweater",
        59: "Wrapping Nameplate",
        60: "Santa's Outfit",
        61: "Red Santa Hat",
        62: "Deer Antlers/Red Deer Nose",
        63: "Red Elf Outfit",
        64: "Tin Soldier Hat/Ragdoll Regal",
        65: "Star Hat",
        66: "Candy Cane Backpack",
        67: "Snowboard Backpack",
        68: "Fireplace Background",
        69: "Spirit of Toonsmas Past's Outfit",
        70: "Spirit of Toonsmas Present's Outfit",
        71: "Spirit of Toonsmas Future's Outfit"
    },
    QuestSource.Directive: {
        1: "Executive Lobby Key",
        2: "Profile Background + Needlenose Promotion",
        3: "1 Point Laff Boost + Conveyancer Promotion",
        4: "Profile Pose + Advocate Promotion",
        5: "1 Point Laff Boost + Shyster Promotion",
        6: "Nameplate + Barrister Promotion",
        7: "1 Point Laff Boost + Max Level Barrister Promotion + Lawbot Suit Switching",
    }
}

"""
Various Single-Strings
"""
Gag = "Gag"
Gags = "Gags"
AuxillaryText_Complete = "Return to:"
AuxillaryText_For = "for:"
AuxillaryText_From = 'from:'
AuxillaryText_To = 'to:'
AuxillaryText_Against = 'against:'
AuxillaryText_With = 'with:'
AuxillaryText_Less_Than = 'with less than:'
QuestObjective_Complete = "COMPLETE"
TheFish = 'the Fish'
Fishing = 'fishing'
AtYourHome = 'At your estate'
LevelXGag = '{amount} Level {level} {gag}'
OnDaTrolley = 'The Trolley'
OnTheTrolley = "On the trolley"
TreasureDive = "Treasure Dive"
InThePlayground = 'In the playground'
RideTheTrolley = 'Ride on the trolley'
GoSwim = 'Go for a Swim'
AtTheGagShop = "At the Gag Shop"
Anywhere = "Anywhere"
JungleVines = 'Jungle Vines'
IceSlide = 'Ice Slide'
BefriendCog = "Make friends with a Cog"
GivenLaff = "%s Laff"
GivenBut1Laff = "Nevermind...\nGood luck!"
QuestProgress_Complete = "Complete"

"""
Objective Headlines
"""

HL_Throw = "THROW"
HL_Collect = "COLLECT"
HL_Trolley = "TROLLEY"
HL_Visit = "VISIT"
HL_Swim = "SWIM"
HL_Recover = "RECOVER"
HL_Win = "WIN"
HL_Fish = "GO FISHING"
HL_Search = "SEARCH"
HL_Purchase = "PURCHASE"
HL_Book = "SHTIKERBOOK"
HL_Obtain = "OBTAIN"
HL_Mail = "MAIL"
HL_Investigate = "INVESTIGATE"
HL_Deliver = "DELIVER"
HL_Defeat = "DEFEAT"
HL_Infiltrate = "INFILTRATE"
HL_Wanted = "WANTED"
HL_CogFriend = "BEFRIEND A COG"
HL_Disguise = "SUIT UP"
HL_PicnicGames = "PICNIC GAMES"
HL_Earn = "EARN"
HL_Complete = "COMPLETE"
HL_Race = "RACE"
HL_Stun = "STUN"
HL_Damage = "DAMAGE"
HL_Feed = "FEED"
HL_Destroy = "DESTROY"
HL_Stomp = "STOMP"
HL_Golf = "GOLF"
HL_SAD = "SADDEN"
HL_KNOCK = "LAUGH"
HL_Ride = "RIDE"
HL_JumpOn = "JUMP ON"
HL_Interact = "INTERACT"

"""
Objective prefixes
"""

PFX_DEFEAT = 'Defeat '
PFX_INFILTRATE = 'Infiltrate '
PFX_VISIT = 'Visit '
PFX_FISH = 'Fish up '
PFX_RECOVER = 'Recover '
PFX_DELIVER = 'Deliver '
PFX_OBTAIN = 'Obtain '
PFX_INVESTIGATE = 'Investigate '
PFX_DIVEFOR = 'Dive for '
PFX_TAKEDOWN = 'Take down '
PFX_SWINGFOR = 'Vine swing for '
PFX_CATCH = 'Catch '
PFX_GRAB = 'Grab '
PFX_THROW = 'Throw '
PFX_EARN = 'Earn '
PFX_DESTROY = 'Destroy '
PFX_JUMP_ON_MML = 'Jump on a Drum '
PFX_INTERACT = 'Interact with '

"""
Objective progress
"""

PROG_Throw = '{value} of {range} items thrown'
PROG_Collect = '{value} of {range} collected'
PROG_Recover = '{value} of {range} recovered'
PROG_Defeat = '{value} of {range} defeated'
PROG_Infiltrate = '{value} of {range} infiltrated'
PROG_Deliver = '{value} of {range} delivered'
PROG_Win = '{value} of {range} won'
PROG_Play = '{value} of {range} played'
PROG_Earn = '{value} of {range} earned'
PROG_Complete = '{value} of {range} completed'
PROG_Stun = '{value} of {range} stuns'
PROG_Damage = '{value} of {range} damage'
PROG_Feed = '{value} of {range} fed'
PROG_Destroy = '{value} of {range} destroyed'
PROG_Stomp = '{value} of {range} stomped'
PROG_GolfHits = '{value} of {range} hits'
PROG_Rotations = '{value} of {range} rotations'
PROG_Jumps = '{value} of {range} jumps'
PROG_Interact = '{value} of {range} interacted'
PROG_Befriended = '{value} of {range} befriended'
PROG_Assembled = '{value} of {range} assembled'
PROG_Times = '{value} of {range} times'

"""
Objective goals
"""

OBJ_Recover = "Recover %s from %s"
OBJ_Defeat = "Defeat %s"
OBJ_Infiltrate = "Infiltrate %s"
OBJ_Visit = "Visit %s"
OBJ_Catch = "Catch %s"
OBJ_Assemble = "Assemble a %s Cog Disguise"
OBJ_CogFriend = "Befriend a Cog"
OBJ_Deliver = "Deliver %s"
OBJ_DeliverTo = "Deliver %s to %s"
OBJ_Investigate = "Investigate %s"
OBJ_Collect = "Collect %s"
OBJ_Mailbox = "Check your Mailbox"
OBJ_Obtain = "Obtain %s"
OBJ_OpenBook = "Open your Shtikerbook"
OBJ_PurchaseGag = "Purchase a Gag"
OBJ_Win = "Win a %s"
OBJ_Play = "Play a %s"
OBJ_Throw = "Throw %s"
OBJ_Earn = "Earn %s %s"
OBJ_Complete = "Complete a %s"
OBJ_RacePlacement = "Place %s in a %s Race"
OBJ_GolfPlacement = "Place %s in a %s Course"
OBJ_Stun = "Stun %s"
OBJ_Feed = "Feed %s"
OBJ_Stomp = "Stomp %s"
OBJ_Sad = "Find a way to go Sad"
OBJ_Knock = "Laugh at a knock knock joke"
OBJ_Ride = "Ride %s"
OBJ_JumpOn = "Jump on %s"
OBJ_Destroy = "Destroy %s"
OBJ_Damage = "Deal %s damage"
OBJ_Interact = "Interact with %s"

"""
Reward phrases
"""

RWD_Antlers = '\1white\1\5reward_packageIcon\5\2 Red-Nose Deer Species Effect'
RWD_Background = '\1white\1\5reward_packageIcon\5\2 %s Profile Background'
RWD_Gumballs = '\1white\1\5reward_gumballIcon\5\2 %s Gumballs'
RWD_Jellybeans = '\1white\1\5reward_beanJarIcon\5\2 %s Jellybeans'
RWD_ClubCoins = '\1white\1\5reward_clubCoin\5\2 %s Club Coins'
RWD_CheesyEffect = '\1white\1\5reward_packageIcon\5\2 %s Cheesy Effect'
RWD_SuitPromote = '\1grey\1\5reward_disguiseIcon\5\2 Executive Suit Promotion'
RWD_ToonExp = '\1white\1\5reward_expIcon\5\2 %s Experience'
RWD_Furniture = '\1white\1\5reward_packageIcon\5\2 %s'
RWD_Shirt = '\1white\1\5reward_packageIcon\5\2 %s Shirt'
RWD_Short = '\1white\1\5reward_packageIcon\5\2 %s Shorts'
RWD_Skirt = '\1white\1\5reward_packageIcon\5\2 %s Skirt'
RWD_Accessory = '\1white\1\5reward_packageIcon\5\2 %s'
RWD_Laff = '\1white\1\5reward_laffIcon%s\5\2 Laff Boost'
RWD_Nameplate = '\1white\1\5reward_packageIcon\5\2 %s Profile Nameplate'
RWD_Nametag = '\1white\1\5reward_packageIcon\5\2 %s Nametag Font'
RWD_ProfilePose = '\1white\1\5reward_packageIcon\5\2 %s Profile Pose'
RWD_SuitSwitch = '\1grey\1\5reward_disguiseIcon\5\2 %s Disguise Switching'
RWD_TPAccess = '\1white\1\5reward_teleportIcon\5\2 %s Teleport Access'
RWD_Kudos = '\1white\1\5reward_kudos%sSmall\5\2 %s %s Kudos XP'
RWD_PGMult = '\1white\1\5icon_battleProp_{track}_{level}\5\2 +{amount} {location} Gag Exp. Mult.'
RWD_PGDiscount = '\1white\1\5reward_beanJarIcon\5\2 %s%% Cheaper Gags in %s'
RWD_Booster = '%s Hour %s'

"""
Speedchat Phrases
"""

SC_GoFishing = "I need to fish up %s from %s."
SC_Defeat = "I need to defeat %s."
SC_DefeatLocation = "I need to defeat %s%s."
SC_Infiltrate = "I need to infiltrate %s."
SC_InfiltrateLocation = "I need to infiltrate %s%s."
SC_RecoverCogs = "I need to recover %s from %s%s."
SC_Deliver = "I need to deliver {}."
SC_Obtain = "I need to obtain %s."
SC_Investigate = "I need to investigate the %s."
SC_Mail = 'I need to check my mail.'
SC_DeliverGags = 'I need to deliver a Level %s Gag.'
SC_Book = 'I need to open my Shtickerbook.'
SC_Snowball = 'I need to collect some snowballs.'
SC_TreasureChest = 'I need to go diving for some Treasure Chests.'
SC_DeliverJbs = 'I need to deliver some Jellybeans.'
SC_EarnJbs = 'I need to earn some Jellybeans.'
SC_Building = "I need to defeat %s%s."
SC_Laff_Building = "I need to defeat %s%s with less than %s%% Laff."
SC_Laff_Building_1Laff = "I need to defeat %s%s without going sad, whelp."
SC_CogDisguise = 'I need to assemble my %s Cog disguise.'
SC_ThrowPies = 'I need to throw some pies.'
SC_Treasure = 'I need to collect some treasures.'
SC_Trolley = 'I need to ride the trolley.'
SC_Swim = 'I need to go for a swim.'
SC_Search = "I need to search for a %s."
SC_Gags = 'I need to buy some gags from the Gag Shop.'
SC_JungleVines = 'I need to play Jungle Vines for some bananas.'
SC_IceSlide = 'I need to play Ice Slide for some treasure barrels.'
SC_CogFriend = 'I need to make friends with a Cog.'
SC_CatchingGame = 'I need to play Catching Game for some %s.'
SC_Fishing = 'I need to catch %s "%s" fish.'
SC_Visit = 'I need to see %s.'
SC_VisitPlayground = 'I need to go to %s Playground.'
SC_VisitSpecific = 'I need to go %(to)s %(street)s in %(hood)s.'
SC_VisitBuilding = 'I need to visit %s%s.'
SC_VisitBuildingWhere = 'Where is %s%s?'
SC_PGTWin = 'I need to win %s.'
SC_PGTPlay = 'I need to play %s.'
SC_GagExp = 'I need to earn %s %s experience.'
SC_RaceComplete = 'I need to complete {totalRaces}{trackName} race{s}.'
SC_GolfComplete = 'I need to complete %s %s golf courses.'
SC_Stun = 'I need to stun %s %s.'
SC_Damage = 'I need to deal %s damage to %s.'
SC_DamageWeapon = 'I need to deal %s damage to %s with %s.'
SC_Feed = 'I need to feed %s %s.'
SC_Collect = 'I need to collect %s%s.'
SC_Destroy = 'I need to destroy %s %s with %s.'
SC_Stomp = 'I need to stomp %s%s.'
SC_GolfHits = 'I need to hit %s with %s golf balls.'
SC_Sad = 'I need to go Sad.'
SC_Knock = 'I need to go laugh at a knock knock joke.'
SC_Ride = 'I need to ride the piano %s time%s.'
SC_JumpOn = 'I need to jump on a drum %s time%s.'
SC_Interact = 'I need to interact with %s.'

"""
Quest poster specific strings
"""

QP_JustForFun = "Just for fun!"
QP_Expire = "Expires in %s days!"
QP_ConfirmDelete = 'Are you sure you want to delete this ToonTask?'
QP_ConfirmSideDelete = 'Are you sure you want to delete this Sidetask?'
QP_ConfirmKudosDelete = 'Are you sure you want to delete this Kudos ToonTask?'
QP_SuitConfirmDelete = 'Are you sure you want to delete this Directive?'

"""
Cog Zone Name Overrides
"""

DefeatCogZoneNames = {
    ToontownGlobals.SchoolHouse: ' in the Schoolhouse Basement',
    ToontownGlobals.LighthouseInt: ' at the Lighthouse Pier',
    ToontownGlobals.ChainsawLogging: ' at Cut to the Chase! Logging Co',
}

"""
Various QuestEnum matches
"""


QuestItemNames = {
    'default':                                  ('The World\'s Most Radical Trout!!', 'The World\'s Most Radical Trouts!!', 'a '),
    QuestItemName.ExerciseSupplies:             ('Exercise Supplies', 'Exercise Supplies', 'some '),
    QuestItemName.LaughingGas:                  ('Laughing Gas', 'Laughing Gas', 'some '),
    QuestItemName.JokeRepairTools:              ('Joke Repair Tools', 'Joke Repair Tools', ''),
    QuestItemName.ReservationTicket:            ('Reservation Ticket', 'Reservation Tickets', 'a '),
    QuestItemName.UnstickingObject:             ('Unsticking Object', 'Unsticking Objects', 'an '),
    QuestItemName.DecorativeGlue:               ('Decorative Glue', 'Decorative Glues', 'some '),
    QuestItemName.GlassJar:                     ('Glass Jar', 'Glass Jars', 'a '),
    QuestItemName.Glue:                         ('Glue', 'Glue', 'some '),
    QuestItemName.AddingMachine:                ('Adding Machine', 'Adding Machines', 'an '),
    QuestItemName.MachineParts:                 ('Machine Parts', 'Machine Parts', 'some '),
    QuestItemName.PapercutProofGloves:          ('Papercut-Proof Gloves', 'Papercut-Proof Gloves', 'some '),
    QuestItemName.MailPackage:                  ('Mail Package', 'Mail Packages', 'a '),
    QuestItemName.ClownTires:                   ('Clown Tire', 'Clown Tires', 'a '),
    QuestItemName.BoxOfMeatballProduct:         ('Box of Meatball Product', 'Boxes of Meatball Product', 'a '),
    QuestItemName.PencilShavings:               ('Pencil Shavings', 'Pencil Shavings', 'some '),
    QuestItemName.Springs:                      ('Spring', 'Springs', 'a '),
    QuestItemName.LoveLetter:                   ('Love letter', 'Love letters', 'a '),
    QuestItemName.SupplyOfInk:                  ('Supply of ink', 'Supply of ink', 'a '),
    QuestItemName.Keys:                         ('Key', 'Keys', 'a '),
    QuestItemName.CogGears:                     ('Cog Gear', 'Cog Gears', 'a '),
    QuestItemName.HeavyCogGears:                ('Heavy Cog Gear', 'Heavy Cog Gears', 'a '),
    QuestItemName.MechanicalBelt:               ('Mechanical Belt', 'Mechanical Belts', 'a '),
    QuestItemName.PBJFish:                      ('PBJ Fish', 'PBJ Fishes', 'a '),
    QuestItemName.BeardSupply:                  ('Beard Supply', 'Beard Supplies', 'a '),
    QuestItemName.SampleOfInk:                  ('Sample of Ink', 'Samples of Ink', 'a '),
    QuestItemName.BagOfSalt:                    ('Bag of Salt', 'Bags of Salt', 'a '),
    QuestItemName.PlasticContainer:             ('Plastic Container', 'Plastic Containers', 'a '),
    QuestItemName.Igniter:                      ('Igniter', 'Igniters', 'an '),
    QuestItemName.MetalCasing:                  ('Metal Casing', 'Metal Casings', 'a '),
    QuestItemName.MetalPlate:                   ('Metal Plate', 'Metal Plates', 'a '),
    QuestItemName.Baloney:                      ('Baloney', 'Baloneys', 'some '),
    QuestItemName.LostItem:                     ('Lost Item', 'Lost Items', 'some '),
    QuestItemName.LostandFoundBox:              ('Lost and Found Box', 'Lost and Found Boxes', 'a '),
    QuestItemName.SuitThread:                   ('Suit Thread', 'Suit Threads', 'some '),
    QuestItemName.Pencil:                       ('Pencil', 'Pencils', 'a '),
    QuestItemName.Book:                         ('Book', 'Books', 'a '),
    QuestItemName.SparePart:                    ('Spare Part', 'Spare Parts', 'a '),
    QuestItemName.SpareMetal:                   ('Spare Metal', 'Spare Metals', 'some '),
    QuestItemName.Binnacle:                     ('Binnacle', 'Binnacles', 'a '),
    QuestItemName.BoxingGloves:                 ('Boxing Gloves', 'Boxing Gloves', 'some '),
    QuestItemName.Swordfish:                    ('Swordfish', 'Swordfish', 'a '),
    QuestItemName.Shoe:                         ('Shoes', 'Shoes', 'some '),
    QuestItemName.Numbers:                      ('Numbers', 'Numbers', 'some '),
    QuestItemName.DebriefingList:               ('Debriefing List', 'Debriefing Lists', 'a '),
    QuestItemName.GlassLens:                    ('Glass Lens', 'Glass Lenses', 'a '),
    QuestItemName.WoodenPlank:                  ('Wooden Plank', 'Wooden Planks', 'a '),
    QuestItemName.WoodcuttingTools:             ('Woodcutting Tools', 'Woodcutting Tools', 'some '),
    QuestItemName.CogActivityChart:             ('Cog Activity Chart', 'Cog Activity Charts', 'a '),
    QuestItemName.Telescope:                    ('Telescope', 'Telescopes', 'a '),
    QuestItemName.HullParts:                    ('Hull Parts', 'Hull Parts', 'some '),
    QuestItemName.UselessArtifact:              ('Useless Artifact', 'Useless Artifacts', 'a '),
    QuestItemName.Jewel:                        ('Jewel', 'Jewels', 'a '),
    QuestItemName.TwinJewel:                    ('Twin Jewel', 'Twin Jewels', 'a '),
    QuestItemName.LargeGreenPantset:            ('Large Green Pantset', 'Large Green Pantsets', 'a '),
    QuestItemName.MerlinsFavoriteQuill:         ("Merlin's Favorite Quill", "Merlin's Favorite Quills", ''),
    QuestItemName.Package:                      ('Package', 'Packages', 'a '),
    QuestItemName.RoundTable:                   ('Round Table', 'Round Tables', 'a '),
    QuestItemName.Counterweight:                ('Counterweight', 'Counterweights', 'a '),
    QuestItemName.Information:                  ('Information', 'Information', 'some '),
    QuestItemName.JugglingStick:                ('Juggling Stick', 'Juggling Sticks', 'a '),
    QuestItemName.Iron:                         ('Iron', 'Iron', 'some '),
    QuestItemName.SwordMaterials:               ('Sword Materials', 'Sword Materials', 'some '),
    QuestItemName.ExecutivePromotionPapers:     ('Executive Promotion Papers', 'Executive Promotion Papers', 'some '),
    QuestItemName.StolenPotion:                 ('Stolen Potion', 'Stolen Potions', 'a '),
    QuestItemName.Wiring:                       ('Wiring', 'Wiring', 'some '),
    QuestItemName.WirePillow:                   ('Wire Pillow', 'Wire Pillows', 'a '),
    QuestItemName.GrowthPotion:                 ('Growth Potion', 'Growth Potions', 'a '),
    QuestItemName.Furniture:                    ('Furniture', 'Furniture', 'some '),
    QuestItemName.MetalFraming:                 ('Metal Framing', 'Metal Framing', 'some '),
    QuestItemName.MetalFramings:                ('Metal Framings', 'Metal Framings', 'some '),
    QuestItemName.SellbotMetalPiece:            ('Sellbot Metal Piece', 'Sellbot Metal Pieces', 'a '),
    QuestItemName.BoxofSunflowers:              ('Box of Sunflowers', 'Box of Sunflowers', 'a '),
    QuestItemName.CaesarSalad:                  ('Caesar Salad', 'Caesar Salads', 'a '),
    QuestItemName.Hair:                         ('Hair', 'Hairs', 'some '),
    QuestItemName.Plastics:                     ('Plastics', 'Plastics', 'some '),
    QuestItemName.CompressPack:                 ('Compress Pack', 'Compress Packs', 'a '),
    QuestItemName.LightBlueButton:              ('Light Blue Button', 'Light Blue Buttons', 'a '),
    QuestItemName.LeavesAndPocketLint:          ('Leaves & Pocket Lint', 'Leaves & Pocket Lint', 'some '),
    QuestItemName.ClockParts:                   ('Clock Parts', 'Clock Parts', 'some '),
    QuestItemName.Clock:                        ('Clock', 'Clocks', 'a '),
    QuestItemName.ReedsBlankie:                 ("Reed's Blankie", "Reed's Blankies", ''),
    QuestItemName.Riddle:                       ('Riddle', 'Riddles', 'a '),
    QuestItemName.Kazoo:                        ('Kazoo', 'Kazoos', 'a '),
    QuestItemName.MetalParts:                   ('Metal Parts', 'Metal Parts', 'some '),
    QuestItemName.RubberCement:                 ('Rubber Cement', 'Rubber Cement', 'some '),
    QuestItemName.InsurancePapers:              ('Insurance Papers', 'Insurance Papers', 'some '),
    QuestItemName.BookingChart:                 ('Booking Chart', 'Booking Charts', 'a '),
    QuestItemName.Note:                         ('Note', 'Notes', 'a '),
    QuestItemName.KitchenUtensils:              ('Kitchen Utensils', 'Kitchen Utensils', 'some '),
    QuestItemName.Tweezers:                     ('Tweezers', 'Tweezers', 'some '),
    QuestItemName.Earrings:                     ('Earrings', 'Earrings', 'some '),
    QuestItemName.Records:                      ('Records', 'Records', 'some '),
    QuestItemName.Pinecones:                    ('Pinecones', 'Pinecones', 'some '),
    QuestItemName.StickyGeorgesKeys:            ("Sticky George's Keys", "Sticky George's Keys", ''),
    QuestItemName.HeaterParts:                  ('Heater Parts', 'Heater Parts', 'some '),
    QuestItemName.DryIce:                       ('Dry Ice', 'Dry Ice', 'some '),
    QuestItemName.Teeth:                        ('Teeth', 'Teeth', 'some '),
    QuestItemName.HeadMirror:                   ('Head Mirror', 'Head Mirrors', 'a '),
    QuestItemName.DicedIce:                     ('Diced Ice', 'Diced Ice', 'some '),
    QuestItemName.Puppies:                      ('15 Puppies', '15 Puppies', ''),
    QuestItemName.Fin:                          ('Fin', 'Fins', 'a '),
    QuestItemName.Cheese:                       ('Cheese', 'Cheese', 'some '),
    QuestItemName.FlavoringPowder:              ('Flavoring Powder', 'Flavoring Powder', 'some '),
    QuestItemName.BigBurgerIngredients:         ('Big Burger Ingredients', 'Big Burger Ingredients', ''),
    QuestItemName.Tie:                          ('Tie', 'Ties', 'a '),
    QuestItemName.Glasses:                      ('Glasses', 'Glasses', 'some '),
    QuestItemName.Monacle:                      ('Monacle', 'Monacles', 'a '),
    QuestItemName.Shades:                       ('Shades', 'Shades', 'some '),
    QuestItemName.CogParts:                     ('Cog Parts', 'Cog Parts', 'some '),
    QuestItemName.ExternalTemperatureSensor:    ('External Temperature Sensor', 'External Temperature Sensor', 'a '),
    QuestItemName.SensorSuitPiece:              ('Sensor Suit Piece', 'Sensor Suit Pieces', 'a '),
    QuestItemName.CoinFlavoredBreathMint:       ('Coin-Flavored Breath Mint', 'Coin-Flavored Breath Mint', 'a '),
    QuestItemName.StorageDocuments:             ('Storage Documents', 'Storage Documents', 'some '),
    QuestItemName.Purse:                        ('Purse', 'Purses', 'a '),
    QuestItemName.Camera:                       ('Camera', 'Cameras', 'a '),
    QuestItemName.Film:                         ('Film', 'Film', 'some '),
    QuestItemName.ShinyMetalPlates:             ('Shiny Metal Plates', 'Shiny Metal Plates', 'some '),
    QuestItemName.CrazyDynamite:                ('Crazy Dynamite', 'Crazy Dynamite', 'some '),
    QuestItemName.SuitSealantPaste:             ('Suit Sealant Paste', 'Suit Sealant Paste', 'some '),
    QuestItemName.Wig:                          ('Wig', 'Wigs', 'a '),
    QuestItemName.OldBoot:                      ('Old Boot', 'Old Boots', 'an '),
    QuestItemName.Key:                          ('Key', 'Keys', 'a '),
    QuestItemName.StinkyCheese:                 ('Stinky Cheese', 'Stinky Cheeses', 'some '),
    QuestItemName.PieceofCloth:                 ('Piece of Cloth', 'Pieces of Cloth', 'a '),
    QuestItemName.Pajamas:                      ('Pajamas', 'Pajamas', 'some '),
    QuestItemName.Drawing:                      ('Drawing', 'Drawings', 'a '),
    QuestItemName.Feather:                      ('Feather', 'Feathers', 'a '),
    QuestItemName.MagicBeamProjectorParts:      ('Magic Beam Projector Parts', 'Magic Beam Projector Parts', 'some '),
    QuestItemName.Dime:                         ('Dime', 'Dimes', 'a '),
    QuestItemName.FolderofDocuments:            ('Folder of Documents', 'Folder of Documents', 'a '),
    QuestItemName.Propeller:                    ('Propeller', 'Propellers', 'a '),
    QuestItemName.WindowPanes:                  ('Window Panes', 'Window Panes', 'some '),
    QuestItemName.SmallSewingNeedles:           ('Small Sewing Needles', 'Small Sewing Needles', 'some '),
    QuestItemName.PieceofThread:                ('Piece of Thread', 'Pieces of Thread', 'a '),
    QuestItemName.Lumber:                       ('Lumber', 'Lumber', 'some '),
    QuestItemName.StrongWire:                   ('Strong Wire', 'Strong Wires', 'a '),
    QuestItemName.Bandage:                      ('Bandage', 'Bandages', 'a '),
    QuestItemName.MoneyBag:                     ('Money Bag', 'Money Bags', 'a '),
    QuestItemName.Food:                         ('Food', 'Food', 'some '),
    QuestItemName.MechanicalPieces:             ('Mechanical Pieces', 'Mechanical Pieces', 'some '),
    QuestItemName.PieceofPlastic:               ('Piece of Plastic', 'Pieces of Plastic', 'a '),
    QuestItemName.TrustyTrowel:                 ('Trusty Trowel', 'Trusty Trowels', 'the '),
    QuestItemName.MoustacheHair:                ('Moustache Hair', 'Moustache Hairs', 'some '),
    QuestItemName.MetallicSeven:                ('Metallic Seven', 'Metallic Sevens', 'a '),
    QuestItemName.JellybeanRegister:            ('Jellybean Register', 'Jellybean Registers', 'a '),
    QuestItemName.LightBulb:                    ('Light Bulb', 'Light Bulbs', 'a '),
    QuestItemName.MagicBean:                    ('Magic Bean', 'Magic Beans', 'a '),
    QuestItemName.PieceofDenim:                 ('Piece of Denim', 'Pieces of Denim', 'a '),
    QuestItemName.PieceofGold:                  ('Piece of Gold', 'Pieces of Gold', 'a '),
    QuestItemName.Tuner:                        ('Tuner', 'Tuners', 'a '),
    QuestItemName.SolarCellPart:                ('Solar Cell Part', 'Solar Cell Parts', 'a '),
    QuestItemName.ElasticBand:                  ('Elastic Band', 'Elastic Bands', 'a '),
    QuestItemName.XXLKittenMittens:             ('XXL Kitten Mittens', 'XXL Kitten Mittens', 'a pair of '),
    QuestItemName.SuperHat:                     ('Super Hat', 'Super Hats', 'a '),
    QuestItemName.OilCoveredStick:              ('Oil Covered Stick', 'Oil Covered Sticks', 'an '),
    QuestItemName.BurningStick:                 ('Burning Stick', 'Burning Stick', 'a '),
    QuestItemName.GolfClub:                     ('Golf Club', 'Golf Clubs', 'a '),
    QuestItemName.GolfBall:                     ('Golf Ball', 'Golf Balls', 'a '),
    QuestItemName.GolfCap:                      ('Golf Cap', 'Golf Caps', 'a '),
    QuestItemName.Goldentooth:                  ('Golden tooth', 'Golden teeth', 'a '),
    QuestItemName.Greenplant:                   ('Green plant', 'Green plants', 'a '),
    QuestItemName.BeltandButtons:               ('Belt and Buttons', 'Belts and Buttons', 'a '),
    QuestItemName.QualityMetal:                 ('Quality Metal', 'Quality Metals', 'some '),
    QuestItemName.PieceofCheese:                ('Piece of Cheese', 'Pieces of Cheese', 'a '),
    QuestItemName.PieceofZephyrCloth:           ('Piece of Zephyr Cloth', 'Pieces of Zephyr Cloth', 'a '),
    QuestItemName.ZanyMaterials:                ('Zany Materials', 'Zany Materials', 'some '),
    QuestItemName.BagofHourglassSand:           ('Bag of Hourglass Sand', 'Bags of Hourglass Sand', 'a '),
    QuestItemName.ForemansTimecard:             ("Foreman's Timecard", "Foreman's Timecard", ''),
    QuestItemName.RustyCan:                     ('Rusty Can', 'Rusty Cans', 'a '),
    QuestItemName.BugSuitPart:                  ('Bug Suit Part', 'Bug Suit Parts', 'a '),
    QuestItemName.ElphabatsMaterials:           ("Elphabat's Materials", "Elphabat's Materials", ''),
    QuestItemName.OpticalCamera:                ('Optical Camera', 'Optical Cameras', 'a '),
    QuestItemName.RepurposedCamera:             ('Repurposed Camera', 'Repurposed Cameras', 'a '),
    QuestItemName.Egg:                          ('Egg', 'Eggs', 'an '),
    QuestItemName.ContainerofSalt:              ('Container of Salt', 'Containers of Salt', 'a '),
    QuestItemName.BakingSoda:                   ('Baking Soda', 'Baking Soda', 'some '),
    QuestItemName.PieceofRedTape:               ('Piece of Red Tape', 'Pieces of Red Tape', 'a '),
    QuestItemName.IncompleteClothing:           ('Incomplete Clothing', 'Incomplete Clothing', 'some '),
    QuestItemName.GooglyEyes:                   ('Googly Eyes', 'Googly Eyes', 'some '),
    QuestItemName.GreenThread:                  ('Green Thread', 'Green Thread', 'some '),
    QuestItemName.SomethingShiny:               ('Something Shiny', 'Something Shiny', ''),
    QuestItemName.GoldCoin:                     ('Gold Coin', 'Gold Coins', 'a '),
    QuestItemName.StickyRedTape:                ('Sticky Red Tape', 'Sticky Red Tape', 'some '),
    QuestItemName.Ticket:                       ('Ticket', 'Tickets', 'a '),
    QuestItemName.RedSuit:                      ('Red Suit', 'Red Suits', 'a '),
    QuestItemName.SantasSuit:                   ("Santa's Suit", "Santa's Suit", ''),
    QuestItemName.Bag:                          ('Bag', 'Bags', 'a '),
    QuestItemName.DollarBill:                   ('Dollar Bill', 'Dollar Bills', 'a '),
    QuestItemName.SantasBag:                    ("Santa's Bag", "Santa's Bag", ''),
    QuestItemName.Mustache:                     ('Mustache', 'Mustaches', 'a '),
    QuestItemName.ItemwithFlair:                ('Item with Flair', 'Items with Flair', 'an '),
    QuestItemName.PaperMaterial:                          ('Paper Material', 'Paper Material', 'some '),
    QuestItemName.Glove:                        ('Glove', 'Gloves', 'a '),
    QuestItemName.ThickSuit:                    ('Thick Suit', 'Thick Suits', 'a '),
    QuestItemName.PackageofPlasticWrap:         ('Package of Plastic Wrap', 'Packages of Plastic Wrap', 'a '),
    QuestItemName.PlasticBoard:                 ('Plastic Board', 'Plastic Boards', 'a '),
    QuestItemName.PieceofLining:                ('Piece of Lining', 'Pieces of Lining', 'a '),
    QuestItemName.LeatherStrap:                 ('Leather Strap', 'Leather Straps', 'a '),
    QuestItemName.Stick:                        ('Stick', 'Sticks', 'a '),
    QuestItemName.SortaStockings:               ('Sorta-Stockings', 'Sorta-Stockings', ''),
    QuestItemName.Memo:                         ('Memo', 'Memos', 'a '),
    QuestItemName.VialofInk:                    ('Vial of Ink', 'Vials of Ink', 'a '),
    QuestItemName.CogSuitSleeve:                ('Cog Suit Sleeve', 'Cog Suit Sleeves', 'a '),
    QuestItemName.SparkingMechanism:            ('Sparking Mechanism', 'Sparking Mechanisms', 'a '),
    QuestItemName.Firecrackers:                 ('Firecrackers', 'Firecrackers', 'some '),
    QuestItemName.PieceofPondLitter:            ('Piece of Pond Litter', 'Pieces of Pond Litter', 'a '),
    QuestItemName.BouquetofRoses:               ('Bouquet of Roses', 'Bouquet of Roses', 'a '),
    QuestItemName.Chocolate:                    ('Chocolate', 'Chocolates', 'some '),
    QuestItemName.Fiddle:                       ('Fiddle', 'Fiddles', 'a '),
    QuestItemName.GreenSheetMetal:              ('Green Sheet Metal', 'Green Sheet Metal', 'some '),
    QuestItemName.CoinBag:                      ('Coin Bag', 'Coin Bags', 'a '),
    QuestItemName.GoldenCoin:                   ('Golden Coin', 'Golden Coins', 'a '),
    QuestItemName.SuitFabrics:                  ('Suit Fabrics', 'Suit Fabrics', 'some '),
    QuestItemName.CourtDocument:                ('Court Document', 'Court Documents', 'a '),
    QuestItemName.SheetMetal:                   ('Sheet Metal', 'Sheet Metal', 'some '),
    QuestItemName.Number:                       ('Number', 'Numbers', 'a '),
    QuestItemName.MetalPipe:                    ('Metal Pipe', 'Metal Pipes', 'a '),
    QuestItemName.Pulley:                       ('Pulley', 'Pulleys', 'a '),
    QuestItemName.Tubing:                       ('Tubing', 'Tubing', 'some '),
    QuestItemName.EasterBasket:                 ('Easter Basket', 'Easter Baskets', 'an '),
    QuestItemName.ChocolateEgg:                 ('Chocolate Egg', 'Chocolate Eggs', 'a '),
    QuestItemName.HypnoGlasses:                 ('Hypno Glasses', 'Hypno Glasses', 'some '),
    QuestItemName.Nightlight:                   ('Nightlight', 'Nightlights', 'a '),
    QuestItemName.Lamps:                        ('Lamps', 'Lamps', 'some '),
    QuestItemName.SpookyStorybook:              ('Spooky Storybook', 'Spooky Storybooks', 'a '),
    QuestItemName.Seaweed:                      ('Seaweed', 'Seaweed', 'some '),
    QuestItemName.Bat:                          ('Bat', 'Bats', 'a '),
    QuestItemName.CreepyCrawly:                 ('Creepy Crawly', 'Creepy Crawlies', 'a '),
    QuestItemName.Costume:                      ('Costume', 'Costumes', 'a '),
    QuestItemName.Candy:                        ('Candy', 'Candy', 'some '),
    QuestItemName.Bean:                         ('Bean', 'Beans', 'a '),
    QuestItemName.Vegetables:                   ('Vegetables', 'Vegetables', 'some '),
    QuestItemName.DoorHinge:                    ('Door Hinge', 'Door Hinges', 'a '),
    QuestItemName.MashedPotatoes:               ('Mashed Potatoes', 'Mashed Potatoes', 'some '),
    QuestItemName.FlunkyGlasses:                ('Flunky Glasses', 'Flunky Glasses', 'some '),
    QuestItemName.Bandana:                      ('Bandana', 'Bandanas', 'a '),
    QuestItemName.AcornsontheCob:               ('Acorns on the Cob', 'Acorns on the Cob', 'some '),
    QuestItemName.IceCream:                     ('Ice Cream', 'Ice Cream', 'some '),
    QuestItemName.PairofGlasses:                ('Pair of Glasses', 'Pairs of Glasses', 'a '),
    QuestItemName.Present:                      ('Present', 'Presents', 'a '),
    QuestItemName.LeftoverAcornsontheCob:       ('Leftover Acorns on the Cob', 'Leftover Acorns on the Cob', 'some '),
    QuestItemName.Shirt:                        ('Shirt', 'Shirts', 'a '),
    QuestItemName.Oil:                          ('Oil', 'Oil', 'some '),
    QuestItemName.RollofYarn:                   ('Roll of Yarn', 'Rolls of Yarn', 'a '),
    QuestItemName.VolunteerRangerShirt:         ('Volunteer Ranger Shirt', 'Volunteer Ranger Shirts', 'a '),
    QuestItemName.Ruler:                        ('Ruler', 'Rulers', 'a '),
    QuestItemName.PatentReport:                 ('Patent Report', 'Patent Reports', 'some '),
    QuestItemName.BusinessReport:               ('Business Report', 'Business Report', 'a '),
    QuestItemName.Assignment:                   ('Assignment', 'Assignment', 'an '),
    QuestItemName.Needle:                       ('Needle', 'Needles', 'some '),
    QuestItemName.BeanString:                   ('Bean String', 'Bean Strings', 'some '),
    QuestItemName.Ice:                          ('Ice', 'Ice', 'some '),
    QuestItemName.Pen:                          ('Pen', 'Pen', 'a '),
    QuestItemName.WaterCoolerWater:             ('Water Cooler Water', 'Water Cooler Water', 'some '),
    QuestItemName.WigPowderDirections:          ('Wig Powder Directions', 'Wig Powder Directions', 'some '),
    QuestItemName.Wood:                         ('Wood', 'Wood', 'some '),
    QuestItemName.Ink:                          ('Ink', 'Ink', 'some '),
    QuestItemName.TravelGuidePage:              ('Travel Guide Page', 'Travel Guide Pages', 'a '),
    QuestItemName.PairofGoggles:                ('Pair of Goggles', 'Pairs of Goggles', 'a '),
    QuestItemName.Sunscreen:                    ('Sunscreen', 'Sunscreen', 'some '),
    QuestItemName.GoldPenny:                    ('Gold Penny', 'Gold Pennies', 'a '),
    QuestItemName.Monocle:                      ('Monocle', 'Monocles', 'a '),
    QuestItemName.ChocolateCoin:                ('Chocolate Coin', 'Chocolate Coins', 'a '),
    QuestItemName.SewingNeedle:                 ('Sewing Needle', 'Sewing Needles', 'a '),
    QuestItemName.Button:                       ('Button', 'Buttons', 'a '),
    QuestItemName.Tuxedo:                       ('Tuxedo', 'Tuxedos', 'a '),
    QuestItemName.DiamondRing:                  ('Diamond Ring', 'Diamond Rings', 'a '),
    QuestItemName.PianoKey:                     ('Piano Key', 'Piano Keys', 'a '),
    QuestItemName.Piano:                        ('Piano', 'Pianos', 'a '),
    QuestItemName.PianoTuna:                    ('Piano Tuna', 'Piano Tunas', 'a '),
    QuestItemName.RollofFilm:                   ('Roll of Film', 'Rolls of Film', 'a '),
    QuestItemName.WarmItem:                     ('Warm Item', 'Warm Items', 'a '),
    QuestItemName.IceCap:                       ('Ice Cap', 'Ice Caps', 'an '),
    QuestItemName.Boot:                         ('Boot', 'Boots', 'a '),
    QuestItemName.Briefcase:                    ('Briefcase', 'Briefcases', 'a '),
    QuestItemName.Stone:                        ('Stone', 'Stone', 'some '),
    QuestItemName.PackofTrailMix:               ('Pack of Trail Mix', 'Packs of Trail Mix', 'a '),
    QuestItemName.Smores:                       ("S'mores", "S'mores", 'some '),
    QuestItemName.SurvivalKit:                  ('Survival Kit', 'Survival Kits', 'a '),
    QuestItemName.BrokenCamera:                 ('Broken Camera', 'Broken Cameras', 'a '),
    QuestItemName.MetalPolish:                  ('Metal Polish', 'Metal Polish', 'some '),
    QuestItemName.FixedCamera:                  ('Fixed Camera', 'Fixed Cameras', 'a '),
    QuestItemName.BridalItems:                  ('Bridal Items', 'Bridal Items', 'some '),
    QuestItemName.Swingsets:                    ('Candy Swingsets', 'Candy Swingsets', 'some '),
    QuestItemName.LotsOfFruit:                  ('39-Fruit Basket', '39-Fruit Basket', 'a '),
    QuestItemName.BarOfSoap:                    ('Bar of Soap', 'Bars of Soap', 'a '),
    QuestItemName.ClassifiedDocs:               ('Classified Documents', 'Classified Documents', 'some '),
    QuestItemName.MedicalEval:                  ('Medical Evaluation', 'Medical Evaluations', 'a '),
    QuestItemName.RubberDuck:                   ('Rubber Ducky', 'Rubber Duckies', 'a '),
    QuestItemName.Coil:                         ('Coil', 'Coils', 'a '),
    QuestItemName.CogRadarUnit:                 ('Cog Radar Unit', 'Cog Radar Units', 'a '),
    QuestItemName.Starfish:                     ('Starfish', 'Starfish', 'a '),
    QuestItemName.DiningSet:                    ('Dining Set', 'Dining Sets', 'a '),
    QuestItemName.SmallClockHand:               ('Small Clock Hand', 'Small Clock Hands', 'a '),
    QuestItemName.BigClockHand:                 ('Big Clock Hand', 'Big Clock Hands', 'a '),
    QuestItemName.Washer:                       ('Washer', 'Washers', 'a '),
    QuestItemName.ReinforcedBolt:               ('Reinforced Bolt', 'Reinforced Bolts', 'a '),
    QuestItemName.BeanJar:                      ('Bean Jar', 'Bean Jars', 'a '),
    QuestItemName.JellybeanBag:                 ('Jellybean Bag', 'Bags of Jellybeans', 'a '),
    QuestItemName.Motor:                        ('Motor', 'Motors', 'a '),
    QuestItemName.BoxButNotReally:              ('"Box"?', '"Boxes"?', 'a '),
    QuestItemName.FreshlyBakedPies:             ('Freshly Baked Pies', 'Freshly Baked Pies', 'some '),
    QuestItemName.Handkerchief:                 ('Handkerchief', 'Handkerchiefs', 'a '),
    QuestItemName.Garbage:                      ('Garbage', 'Pieces of Garbage', 'some '),
    QuestItemName.QualityFishingRod:            ('Quality Fishing Rod', 'Quality Fishing Rods', 'a '),
    QuestItemName.MaroonGem:                    ('Maroon Gem', 'Maroon Gems', 'a '),
    QuestItemName.GreenGem:                     ('Green Gem', 'Green Gems', 'a '),
    QuestItemName.IndigoGem:                    ('Indigo Gem', 'Indigo Gems', 'a '),
    QuestItemName.BoxOfWritingSupplies:         ('Box of Writing Supplies', 'Boxes of Writing Supplies', 'a '),
    QuestItemName.TarotCard:                    ('Tarot Card', 'Tarot Cards', 'a '),
    QuestItemName.Fertilizer:                   ('Bag of Fertilizer', 'Bags of Fertilizer', 'a '),
    QuestItemName.Ointment:                     ('Tube of Ointment', 'Tubes of Ointment', 'a '),
    QuestItemName.BoxOfAnts:                    ('Box of Ants', 'Boxes of Ants', 'a '),
    QuestItemName.FineCollar:                   ('Fine Collar', 'Fine Collars', 'a '),
    QuestItemName.Bell:                         ('Bell', 'Bells', 'a '),
    QuestItemName.GlassOfWater:                 ('Glass of Water', 'Glasses of Water', 'a '),
    QuestItemName.FineBell:                     ('Fine Bell', 'Fine Bells', 'a '),
    QuestItemName.Flower:                       ('Flower', 'Flowers', 'a '),
    QuestItemName.CouchBlueprints:              ('Couch Blueprints', 'Couch Blueprints', 'some '),
    QuestItemName.Photograph:                   ('Photograph', 'Photographs', 'a '),
    QuestItemName.StackOfPaper:                 ('Stack of Paper', 'Stacks of Paper', 'a '),
    QuestItemName.PancakeMix:                   ('Bag of Pancake Mix', 'Bags of Pancake Mix', 'a '),
    QuestItemName.CookieRecipe:                 ('Cookie Recipe', 'Cookie Recipes', 'a '),
    QuestItemName.SaxBrassButNotReally:         ('"Sax Brass"?', '"Sax Brasses"?', 'some '),
    QuestItemName.ZincVitamins:                 ('Zinc Vitamin', 'Zinc Vitamins', 'a '),
    QuestItemName.InsurancePermit:              ('Insurance Permit', 'Insurance Permits', 'an '),
    QuestItemName.FraudulentPaperwork:          ('Fraudulent Paperwork', 'Fraudulent Paperwork', 'some '),
    QuestItemName.RoadSalt:                     ('Chunk of Road Salt', 'Chunks of Road Salt', 'a '),
    QuestItemName.Honey:                        ('Jar of Honey', 'Jars of Honey', 'a '),
    QuestItemName.NeatThing:                    ('Neat Thing', 'Neat Things', 'a '),
    QuestItemName.IndustrialGlass:              ('Industrial Glass', 'Industrial Glass', 'some '),
    QuestItemName.Artwork:                      ('Artwork', 'Artwork', 'some '),
    QuestItemName.IcicleBicycle:                ('Icicle Bicycle', 'Icicle Bicycles', 'the '),
    QuestItemName.Sapling:                      ('Sapling', 'Saplings', 'a '),
    QuestItemName.BoxOfPartyPoppers:            ('Box of Party Poppers', 'Boxes of Party Poppers', 'a '),
    QuestItemName.PunchBowl:                    ('Punch Bowl', 'Punch Bowls', 'a '),
    QuestItemName.SoakedLeaves:                 ('Soaked Leaves', 'Soaked Leaves', 'some '),
    QuestItemName.TreePuppies:                  ('Tree Puppies', 'Tree Puppies', 'adorable '),
    QuestItemName.TissueBox:                    ('Tissue Box', 'Tissue Boxes', 'a '),
    QuestItemName.Nut:                          ('Nut', 'Nuts', 'a '),
    QuestItemName.EarPlug:                      ('Ear Plug', 'Ear Plugs', 'an '),
    QuestItemName.Microphone:                   ('Microphone', 'Microphones', 'a '),
    QuestItemName.Megaphone:                    ('Megaphone', 'Megaphones', 'a '),
    QuestItemName.Calendar:                     ('Calendar', 'Calendars', 'a '),
    QuestItemName.Lipstick:                     ('Lipstick', 'Lipsticks', 'a '),
    QuestItemName.FilmReel:                     ('Film Reel', 'Film Reels', 'a '),
    QuestItemName.Bubble:                       ('Bubble', 'Bubbles', 'a '),
    QuestItemName.ShrinkMeter:                  ('Shrink Meter', 'Shrink Meters', 'a '),
    QuestItemName.Gyroscope:                    ('Gyroscope', 'Gyroscopes', 'a '),
    QuestItemName.VisualCalibrator:             ('Visual Calibrator', 'Visual Calibrators', 'a '),
    QuestItemName.Toothpaste:                   ('Tube of Toothpaste', 'Tubes of Toothpaste', 'a '),
    QuestItemName.PackageOfFishBait:            ('Package of Fish Bait', 'Packages of Fish Bait', 'a '),
}


def itemTuple2Word(itemTuple: tuple, count: int = 1, capitalizeFirstInSingular: bool = False, wantIcon: bool = False):
    """Converts an item tuple to a word, given a count of the rewards."""
    packageIcon = "\1white\1\5reward_packageIconCentered\5\2 " if wantIcon else ''
    if count == 1:
        prefix = itemTuple[2]
        if capitalizeFirstInSingular:
            prefix = prefix.capitalize()
        return f'{prefix}{packageIcon}{itemTuple[0]}'
    else:
        return f'{count} {packageIcon}{itemTuple[1]}'


def getQuestItemText(questItem: QuestItemName, count: int = 1, capitalizeFirstInSingular: bool = False, wantIcon: bool = False):
    questItemTuple = QuestItemNames.get(questItem, QuestItemNames['default'])
    return itemTuple2Word(itemTuple=questItemTuple, count=count, capitalizeFirstInSingular=capitalizeFirstInSingular, wantIcon=wantIcon).strip()


"""
Functions for localization access.
"""


def getQuestHeadline(questReference: QuestReference, objectiveSelected: int = 0):
    """Given a quest reference, get the quest headline."""
    questId = questReference.getQuestId()

    # Do we have a part headline?
    questSourceHeadline = QuestChainObjectiveHeadlines.get(questId.getQuestSource())
    if questSourceHeadline:
        # Is the quest chain in here?
        questChainHeadline = questSourceHeadline.get(questId.getChainId())
        if questChainHeadline:
            # Is the quest part in here?
            questObjectiveHeadline = questChainHeadline.get(questId.getObjectiveId())
            if questObjectiveHeadline:
                # This is the objective's headline (overrides the chain).
                return questObjectiveHeadline.strip()

    # Use the quest chain's defined headline.
    questSourceHeadline = QuestChainHeadlines.get(questId.getQuestSource())
    if questSourceHeadline:
        # Is the quest chain in here?
        questChainHeadline = questSourceHeadline.get(questId.getChainId())
        if questChainHeadline:
            # This is the headline.
            return questChainHeadline.strip()

    # Try the quest objective headline.
    from toontown.quest3.base.QuestLine import QuestLine
    questObjective = QuestLine.dereferenceQuestReference(questReference).getObjectiveIndex(objectiveSelected)
    questObjectiveHeadline = questObjective.getHeadline(questReference, objectiveSelected)
    if questObjectiveHeadline:
        # This is the headline.
        return questObjectiveHeadline.strip()

    # No defined headline.
    return ''


def getQuestObjectiveText(questReference: QuestReference, objectiveSelected: int = 0):
    """Given a quest reference, get the quest objective headline text."""
    # Get the quest objective headline.
    from toontown.quest3.base.QuestLine import QuestLine
    questObjective = QuestLine.dereferenceQuestReference(questReference).getObjectiveIndex(objectiveSelected)
    questObjectiveHeadline = questObjective.getHeadline(questReference, objectiveSelected)
    if questObjectiveHeadline:
        # This is the headline.
        return questObjectiveHeadline.strip()
    return ''


def getQuestAuxillaryText(questReference: QuestReference, objectiveSelected: int = 0):
    """Given a quest reference, get the quest auxillary text."""
    # Get the quest auxillary text.
    from toontown.quest3.base.QuestLine import QuestLine
    questObjective = QuestLine.dereferenceQuestReference(questReference).getObjectiveIndex(objectiveSelected)
    questObjectiveAuxillaryText = QuestObjectiveAuxillaryText.get(type(questObjective))
    if questObjectiveAuxillaryText:
        # This is the aux text.
        return questObjectiveAuxillaryText.strip()
    return ''


def getQuestInfoText(questReference: QuestReference, objectiveSelected: int = 0):
    """Given a quest reference, get the quest info text."""
    # Get the quest info text format.
    from toontown.quest3.base.QuestLine import QuestLine
    questObjective = QuestLine.dereferenceQuestReference(questReference).getObjectiveIndex(objectiveSelected)
    questObjectiveInfoFormat = QuestInfoFormats.get(type(questObjective), None)

    # Format the info text in a way the objective wants.
    objectiveTextStrings = questObjective.getInfoTextStrings(questReference=questReference)

    # If there are no text strings, no formatting.
    if not objectiveTextStrings:
        return None

    # Otherwise, format them.
    if questObjectiveInfoFormat:
        return (questObjectiveInfoFormat % objectiveTextStrings).strip()
    else:
        return '\n'.join(objectiveTextStrings).strip()


def getQuestText(questId: QuestId, assigned: bool = False) -> QuestText:
    """Gets the QuestText object from a questId."""
    questTextSourceDict = QuestTextGigaDict.get(questId.getQuestSource(), None)
    if questTextSourceDict is None:
        return QuestText()
    questTextChainDict = questTextSourceDict.get(questId.getChainId())
    if not questTextChainDict:
        return QuestText()

    # We are being assigned a new quest. Use the first (0th) dialogue.
    if assigned:
        questText = questTextChainDict.get(0)
    else:
        questText = questTextChainDict.get(questId.getObjectiveId())

    if not questText:
        return QuestText()
    if type(questText) not in (tuple, list):
        return questText
    return questText[questId.getSubObjectiveId()]


"""
Misc localization strings
"""

# Key: NPC ID, Value: Unique Dialogue
QuestChoiceUnique = {
    # Judy
    12101: 'Do you have an appointment with Ms. Morsecode?',
}

QuestChoice = 'Choose a ToonTask.'

# Key: NPC ID, Value: Unique Dialogue
QuestChoiceCancelUnique = {
    # Judy
    12101: 'Get back to work, this is no place to loiter.',
}

QuestChoiceCancel = 'Come back when you are ready to decide! Bye!'

InstanceNotAvailable = {
    # Derrick Man
    1: "You hear the sounds of oil bubbling and machines whirring. You decide not to enter.",
    # LAA
    2: "You hear the flicker of monitors and camera buzzes. You decide not to enter.",
    # PRR
    3: "Wait, what? Why do you want to go into a prison cell?",
    # DOPA
    4: "You hear a lot of arguing and self-pitying about failed banquets. You decide to come back later.",
    # OCLO
    5: "Did you pick the lock to get in here? C.O.G.S. Incorporated will not tolerate misdemeanors of this level. I'm going to tell your manager.",
    # Prethinker
    6: "What sounds like Cog voices can be heard from the cellar door... Maybe this isn't such a good idea yet.",
    # Rainmaker
    7: "There is a storm approaching. Perhaps you should come back when it has passed.",
    # Witch Hunter
    8: "'Away, rapscallions,' a mysterious voice yells from atop the tower. 'Do not harass me with your rede!'",
    # Multislacker
    9: "You want to open the door to enter, but you're just too tired.",
    # Major Player
    10: "You hear swing music blasting through the elevator, but the show isn't until tonight.",
    # Plutocrat
    11: "Upon approaching the door, you feel a shiver down your spine. Or maybe that's just your stomach. You consider getting pizza instead.",
    # Chainsaw Consultant
    12: "You hear cannons inside, but not the good kind. As well as... a chainsaw? It probably isn't a good idea to barge into here.",
    # Pacesetter
    13: "You approach the elevator, but as soon as you hit the line you hear a beep. You need to turn back.",
}

SpecialQuestZone2Name = {
    SQZ.AnyCogHQ: ("to", "in", "Any Cog HQ"),
    SQZ.SellbotFactory: ("to the", "in the", "Sellbot Factory"),
    SQZ.CashbotMints: ("to the", "in the", "Cashbot Mints"),
    SQZ.LawbotLawfices: ("to the", "in the", "Lawbot Lawfices"),
    SQZ.BossbotGolfCourses: ("to the", "in the", "Bossbot Golf Courses"),
    SQZ.SellbotBoss: ("to the", "in the", "Sellbot Towers Rooftop"),
    SQZ.LawbotBoss: ("to the", "in the", "Lawbot Executive Lawfice"),
    SQZ.HM_LawbotBoss: ("to the", "in the", "Lawbot Executive Lawfice"),
    SQZ.BossbotBoss: ("to the", "in the", "Bossbot Banquet Hall"),
    SQZ.CeosOffice: ("to the", "in the", "C.E.O.'s Office"),
}

SpecialQuestZone2Icon = {
    SQZ.AnyCogHQ: '\1white\1\5gearIcon\5\2',
    SQZ.SellbotFactory: '\1white\1\5sellbotNametag\5\2',
    SQZ.CashbotMints: '\1white\1\5cashbotNametag\5\2',
    SQZ.LawbotLawfices: '\1white\1\5lawbotNametag\5\2',
    SQZ.BossbotGolfCourses: '\1white\1\5bossbotNametag\5\2',
    SQZ.SellbotBoss: '\1white\1\5sellbotNametag\5\2',
    SQZ.LawbotBoss: '\1white\1\5lawbotNametag\5\2',
    SQZ.HM_LawbotBoss: '\1white\1\5lawbotNametag\5\2',
    SQZ.BossbotBoss: '\1white\1\5bossbotNametag\5\2',
    SQZ.CeosOffice: '\1white\1\5bossbotNametag\5\2',
}

KudosQuestNameBase = '{xpType} Kudos Task'
KudosQuestPrefixNames = {
    1: 'Bronze',
    2: 'Silver',
    3: 'Gold',
}
