"""
Strings related to Club things.
"""
from prisma.enums import ClubInfractionType
from toontown.club.ClubEnums import ClubRank

ClubShopNoItemLabel = "No Item Selected"
ClubShopSelectLeft = "Select an item for more info."

ClubCoins = "Club Coins"
ClubShopRequestPurchase = "Would you like to buy %s for %s %s?\n\nYour Club currently has %s %s."
ClubShopRequestEquip = "Would you like to equip %s for your Club?"

ClubRoleNames = {
    ClubRank.Leader:  'Owner',
    ClubRank.Deputy:  'Captain',
    ClubRank.Officer: 'Scout',
    ClubRank.Member:  'Member',
}

ClubLeaveReasons = {
    'left': "You have left your Club.",
    'disband': "You have disbanded your Club.",
    'kicked': "You were kicked from your Club.",
}

ClubInitialFillName = "Enter club name here."
ClubGUIBlockedNameDialog = "Invalid club name."

ClubDefaultName = "%s's Club"

ClubCreationNPCPhrases = {
    # From the POV of Doe Vinci.
    0: (
        # The player is still in the tutorial. Pass them off elsewhere.
        "Oh, hi! Are you looking for Flippy? He's right down the hall! You can't miss him!",
        "If you're looking for Flippy, he's just down the hall!",
        "Hi! Did you need to talk to Flippy? He's right down the hall!",
    ),
    1: (
        # The player is already in a Club. Tell em to shove off.
        "Whoa, whoa, whoa! Wait a minute! Aren't you already in a club?",
        "Remember, you can invite your Toon Friends to your Club through the Social Panel!",
        "Hold on a second, you're already in a Club!",
        "You're already in a club, _avName_! Invite some of your friends through the Social Panel!",
    ),
    2: (
        # The player is waiting for their club name.
        "Oh hey, your Club's name hasn't been approved yet! Don't worry, you'll get a notification once it is!",
        "Hey _avName_, your Club's name wasn't approved yet! We'll let you know when it is!",
        "I don't think your Club's name was approved yet, but we'll let you know when it is!",
    ),
    3: (
        # The player is getting a club name rewrite.
        "Ready to give your Club a brand new name?",
        "Did you want to give your Club a new name?",
        "Oh, did you want to change your Club's name?",
        "Getting tired of your Club's current name?",
    ),
    4: (
        # The player is trying to change their club name after it was denied.
        "Did you have another name in mind?",
        "Maybe a different name will work?",
        "Ooh, what if you try a different name?",
    ),
    5: (
        # The player is making a brand new club.
        "Hi, _avName_! Did you want to make a Club? It's really fun!",
        "Hi, did you want to make a Club today? You'll love it!",
        "Were you thinking of making a Club today, _avName_? It's super fun!",
    ),
    6: (
        # The player is leaving the club creation GUI (not making club).
        "Aw, no new club today? Maybe you could join a friend's club!",
        "Not ready to make a club today? That's okay, you can come back later!",
        "Second guesses about making a Club? Maybe you could join one!",
    ),
    7: (
        # The player is leaving the club creation GUI (after making a club)
        "Just sign here, here, and here... and viola! You can view it from the Social Panel at any time. Have fun!",
        "Congrats on your brand new Club, _avName_! You can view it from the Social Panel at any time. Have fun!",
    ),
    8: (
        # The player is leaving the club creation GUI (rewrite condition, but didn't rewrite yet)
        "Oh, still stumped on what to name your Club? Come back when you have an idea!",
        "Need to think about the name a little more? That's okay, come back when you're ready!",
        "Are you still not sure about the name of your Club? Let me know when you're ready!",
    ),
    9: (
        # The player is leaving the club creation GUI (rewrite condition, submitted new name rewrite)
        "Alright, your new Club name has been submitted! We'll let you know as soon as it's ready!",
        "Okay, your new Club name has been submitted! We'll get back to you as soon as we can!",
        "Your new Club name has been submitted! As soon as it's ready, we'll let you know.",
    ),
    10: (
        # Player time-out
        "Oh, do you need some extra time to think? That's okay!",
        "Did you need a few more minutes? No problem!",
        "If you need some more time to think, that's okay!",
    ),
    11: (
        # Talking to NPC after name submission failed on the server side
        'Sorry, something happened while submitting your Club Name. Mind trying that again?',
    ),
}

ClubShopNPCPhrases = {
    # From the POV of Bro Vinci.
    0: (
        # The player is still in the tutorial. Pass them off elsewhere.
        "Oh hey dude, you looking for Flippy? He's just down the hall.",
        "You the new Toon? All good, you can find Flips just down the hall.",
        "Hey man! New around here? You can find Flippy just past here.",
    ),
    1: (
        # The player is in a club and entering the club shop
        "S'up _avName_! You looking to buy something for your Club?",
        "Hey, what's up? What can I do for you, dude?",
        "Hey, dude! Did you wanna buy some stuff for your Club?",
        "Welcome, dude! Hope you find everything you need!",
    ),
    2: (
        # The player is not in a club
        "Sorry, dude... you can't use the Club Shop without being in a Club!",
        "Hm, I don't think you're in a club yet! You should talk to my sis!",
        "Uh... it doesn't look like you're in a club, dude.",
    ),
    3: (
        # The player purchased something from the Club Shop successfully
        "Good choice, dude!",
        "Whoa! Nice purchase!",
        "Right on! Totally fits you!",
        "Gotta say, I approve!",
    ),
    4: (
        # The player left the Club Shop without doing anything
        "Not ready yet? Come back later if you want to buy something, dude!",
        "Need more time? I don't blame ya... there's a lot to choose from.",
        "If you don't have any ideas, no worries! I won't be going anywhere.",
    ),
    5: (
        # Player time-out
        "Take your time. No need to rush big decisions, dude.",
        "Did you find anything cool?",
        "Need some extra time to think? No worries, dude.",
        "I hope the options aren't overwhelming you!",
    ),
    6: (
        # Something happened, and the player was unable to purchase the item
        # (Basically an error callback, apologize and tell them to try again)
        "Sorry, dude, I can't find it! Something got mixed up in the back.",
        "Yikes, I think I misplaced it somewhere. Sorry, dude!",
        "Well, that's odd... I can't seem to find that item.",
    ),
    7: (
        # Extremely rare: The user was kicked from their club while in the GUI.
        # Basically troll secret dialog.
        "Yikes, dude... you just got evicted.",
    ),
    8: (
        # Called upon equipping a purchased item (like changing club icon)
        "Sure, you've got it equipped now. Enjoy, dude!",
        "Here you go! It's already yours, dude!",
        "And... done! All equipped! Enjoy it dude!",
    ),
}

"""
Club Update Phrases
"""

Update_PlayerLogin = '%s has logged on.'
Update_PlayerLogout = '%s has logged out.'
Update_SetMOTD = '{user} updated the Club Description: {motd}'
Update_NewMember = '%s has joined the Club.'
Update_MemberLeft = '%s has left the Club.'
Update_MemberKicked = '%s was kicked from the Club.'
Update_RoleChange = '{user} was {gaming} to {role}.'
Update_ItemPurchase = '{user} has purchased {item}!'
Update_ClubIcon = '{user} has updated the Club Icon.'
Update_LevelUp = '{name} is now Level {level}!'
Update_NameApproval = "The Club's name has been approved!"
Update_NameDenied = "The Club's name has been denied."
_Update_ContactSupport = "(For more information, any Owner or Captains can contact support@corporateclash.net.)"
Update_NameRevoked = f"The Club's name has been revoked by the Moderation Team. {_Update_ContactSupport}"
Update_MOTDRevoked = f"The Club's Description has been revoked by the Moderation Team. {_Update_ContactSupport}"
Update_TaskCompleted = 'A Club Task has been completed!'
Update_TaskRerolled = 'A Club Task has been rerolled!'

Update_Heading_EarnedJellybeans = 'Jellybeans Donation'
Update_EarnedJellybeans_withAvId = '{avName} has donated {amount} Jellybean{s} to the Club!'
Update_EarnedJellybeans_withoutAvId = 'Your club has earned {amount} Jellybean{s}!'

ClubInfractionAdminNotify = [
    # Only these club infractions are broadcasted to club's admins.
    # If they are not on the list, it is broadcasted to everyone in the club.
    ClubInfractionType.WARNING,
    ClubInfractionType.MUTE,
    ClubInfractionType.MOTD_EDIT_LOCK,
]
Moderation_InfractionNotes = {
    ClubInfractionType.WARNING: f'Your Club has received a warning from the Moderation Team. {_Update_ContactSupport}',
    ClubInfractionType.MUTE:           'Your Club has been muted for {duration} by the Moderation Team. ' + _Update_ContactSupport,
    ClubInfractionType.JOIN_LOCK:      'Your Club has been locked from inviting new members for {duration} by the Moderation Team. ' + _Update_ContactSupport,
    ClubInfractionType.MOTD_EDIT_LOCK: 'Your Club has been locked from editing the Club Description for {duration} by the Moderation Team. ' + _Update_ContactSupport
}
Moderation_ForceDisband = 'Your Club has been disbanded by the Moderation Team. ' \
                          '(For more information, any former Owner or Captains can contact support@corporateclash.net.)'
