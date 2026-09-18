from toontown.chat.enums.ChatChannel import ChatChannel
from toontown.chat.enums.ChatContentType import ChatContentType
from toontown.chat.enums.ChatSystemMessagePreset import ChatSystemMessagePreset
from toontown.toonbase import TTLocalizer

CFSpeech = 1 << 0
CFThought = 1 << 1
CFQuicktalker = 1 << 2
CFTimeout = 1 << 3
CFPageButton = 1 << 4
CFQuitButton = 1 << 5
CFNoQuitButton = 1 << 6
CFReversed = 1 << 7

"""
Channels
"""
Channels_NonPlayer = {ChatChannel.System, ChatChannel.NPC}
"""The channels only server entities can speak on."""

Channels_StaffOnly = {ChatChannel.StaffLocal, ChatChannel.StaffGlobal}
"""The channels only staff can speak on."""

"""
Clubs
"""
Club_Message = 1
"""A normal message being sent within the club."""

Club_Shout = 2
"""A message being broadcast to the entire club."""

Club_Update = 3
"""A message from the stars above (aka, uberdog) about any club changes."""

"""
Moderation
"""
Moderation_MailToonName = TTLocalizer.NPCToonNames[2201]  # Postmaster Pete
"""The toon who reports issues back to the sender."""

Moderation_MinimumLength = 1
"""The minimum length a chat message can be."""

Moderation_MaximumLength = 100
"""The maximum length a chat message can be."""

Moderation_RateLimitPeriod = {
    ChatContentType.Text: 10,
    ChatContentType.SpeedChat: 4,
    ChatContentType.Sticker: 2,
}
"""The duration of a rate limit period in seconds."""

Moderation_RateLimitAmount = {
    ChatContentType.Text: 8,
    ChatContentType.SpeedChat: 3,
    ChatContentType.Sticker: 1,
}
"""The amount of messages that can be sent inside of the rate limit period."""

Moderation_MutedContentType = {ChatContentType.SpeedChat, ChatContentType.Sticker}
"""The only types of content that muted users can speak with."""

"""
Sender
"""
Sender_NoId = 0

"""
System Messages
"""
System_BlockedInTutorial = {ChatSystemMessagePreset.Invasion, ChatSystemMessagePreset.Default}
"""The system message presets which won't be shown in the tutorial."""

System_DontLog = {ChatSystemMessagePreset.Alert, ChatSystemMessagePreset.PlayerLogin}
"""The system message presets which won't show in the chat display."""

"""
Whisper
"""
Whisper_TargetLimit = 4
"""The amount of toons that can be selected for a whisper."""

Whisper_SoundEffect = "phase_3.5/audio/sfx/GUI_whisper_3.ogg"
"""The sound effect to play when receiving a whisper."""

Whisper_SoundEffect_Club = "phase_3.5/audio/sfx/UI_chat_message_club.ogg"
"""The sound effect to play when receiving a club whisper."""

Whisper_SoundEffect_Group = "phase_3.5/audio/sfx/UI_chat_message_group.ogg"
"""The sound effect to play when receiving a group whisper."""

Whisper_SoundEffect_Staff = "phase_3.5/audio/sfx/UI_chat_message_staff.ogg"
"""The sound effect to play when receiving a staff whisper."""

Whisper_SoundEffect_ClubShout = "phase_3.5/audio/sfx/UI_social_clubshout.ogg"
"""The sound effect to play when receiving a club shout."""

Whisper_Confirmation = 4
"""The modifier on the whisper channel to signify a whisper confirmation."""
