"""
Battle
"""
Battle_LocalToon_Joined = "Chat_Battle_LocalToon_Joined"
"""Fired by the battle system when the local toon joins a battle."""

Battle_LocalToon_Left = "Chat_Battle_LocalToon_Left"
"""Fired by the battle system when the local toon leaves a battle."""

"""
Chat Manager
"""
Manager_NewMessage = "Chat_Manager_NewMessage"
"""Fired by the ChatManager when a new message is received."""

Manager_NewMessage_LocalToon_SpeedChat_NonQuest = "Chat_Manager_NewMessage_LocalToon_SpeedChat_NonQuest"
"""Fired by the ChatManager when the local toon sends a non-Quest SpeedChat message."""

Manager_NewMessage_LocalToon_SpeedChat_Quest = "Chat_Manager_NewMessage_LocalToon_SpeedChat_Quest"
"""Fired by the ChatManager when the local toon sends a Quest SpeedChat message."""

"""
Chat Store
"""
Store_LogZoneMessage = "Store_LogZoneMessage"
"""Can be fired with [av, msg] to force the logging of a message."""

"""
Chat Window
"""
UI_Window_Changed = "Chat_UI_Window_Changed"
"""Fired by various sources to request the current window is changed."""

UI_Tab_Changed = "Chat_UI_Tab_Changed"
"""Fired by various sources to request the current tab is changed."""

"""
Clubs
"""
Club_LocalToon_Joined = "enterClub"  # Defined by the Club Manager
"""Fired by the club manager when the local toon joins a club."""

Club_LocalToon_Left = "exitClub"  # Defined by the Club Manager
"""Fired by the club manager when the local toon leaves a club."""

"""
Entry
"""
UI_EntryBox_TextChanged = "Chat_UI_EntryBox_TextChanged"
"""Fired by the entry box when the entered text is changed."""

UI_EntryBox_FocusChanged = "Chat_UI_EntryBox_FocusChanged"
"""Fired by the entry box when the focus state is changed."""

UI_EntryBox_RequestOverwrite = "Chat_UI_EntryBox_RequestOverwrite"
"""Fired by various sources to overwrite the current content written in the entry box."""

UI_EntryBox_RequestFocus = "Chat_UI_EntryBox_RequestFocus"
"""Fired by various sources to change the keyboard focus to the entry box."""

UI_EntryBox_MessageSent = "Chat_UI_EntryBox_MessageSent"
"""Fires by the entry box when enter or send is pressed to send a message."""

UI_EntryBox_MessageSent_Empty = "Chat_UI_EntryBox_MessageSent_Empty"
"""Fires by the entry box when enter or send is pressed to send a message, but the message is empty."""

"""
Focus System
"""
UI_FocusMode_ModeConfigured = "option-update-chat-focus-mode"  # Event text follows the settings conventions
"""Fired by the configuration system that the user changed their focus mode."""

UI_FocusMode_MarkAsActive = "Chat_UI_FocusMode_MarkAsActive"
"""Fired by various UI elements to inform the focus system they're active."""

UI_FocusMode_MarkAsInactive = "Chat_UI_FocusMode_MarkAsInactive"
"""Fired by various UI elements to inform the focus system they're inactive."""

UI_FocusMode_StateChanged = "Chat_UI_FocusMode_StateChanged"
"""Fired by the focus system to inform the focus state has changed."""

"""
Notifications
"""

UI_Request_Notification_Show = "Chat_UI_Request_Notification_Show"  # args: [ChatTabButton]
"""Call to request a notification to show on a ChatTabButton."""

UI_Request_Notification_Hide = "Chat_UI_Request_Notification_Hide"  # args: [ChatTabButton]
"""Call to request a notification to hide on a ChatTabButton."""

UI_Notification_Show = "Chat_UI_Notification_Show"  # args: [ChatTabButton]
"""Fired by ChatTabButton when the notification is revealed."""

UI_Notification_Hide = "Chat_UI_Notification_Hide"  # args: [ChatTabButton]
"""Fired by ChatTabButton when the notification is hidden."""

"""
Groups
"""
Groups_LocalToon_Joined = "Chat_Groups_LocalToon_Joined"
"""Fired by the group manager when the local toon joins a group."""

Groups_LocalToon_Left = "Chat_Groups_LocalToon_Left"
"""Fired by the group manager when the local toon leaves a group."""

"""
Settings
"""
UI_Settings_MainTab_Whispers_Configured = "option-update-chat-main-whispers"  # Event text follows the settings conventions
UI_Settings_MainTab_Alerts_Configured = "option-update-chat-main-alerts"  # Event text follows the settings conventions
UI_Settings_MainTab_Npc_Configured = "option-update-chat-main-npc"  # Event text follows the settings conventions
UI_Settings_MainTab_Clubs_Configured = "option-update-chat-main-clubs"  # Event text follows the settings conventions
UI_Settings_MainTab_Groups_Configured = "option-update-chat-main-groups"  # Event text follows the settings conventions
UI_Settings_LineCount_Configured = "option-update-chat-line-count"  # Event text follows the settings conventions
UI_Settings_Stickers_Sort_Configured = "option-update-sticker-sort-by-usage"  # Event text follows the settings conventions
UI_Settings_Container_Scale_Configured = "option-update-chat-scale"  # Event text follows the settings conventions
UI_Settings_SpeedChat_ColorConfigured = "Chat_UI_Settings_SpeedChat_ColorConfigured"

"""
Shortcuts
"""
UI_Shortcuts_ItemSelected = "Chat_UI_Shortcuts_Item_Selected"
"""Fired by a Shortcut choice when it's clicked."""

UI_Shortcuts_StaffChatToggle = "Chat_UI_Shortcuts_StaffChat"
"""Toggles the Staff Chat functionality."""

UI_Generate_Shortcuts = "UI_Generate_Shortcuts"
"""Take a wild guess"""

"""
Stickers
"""
UI_Sticker_Pack_Changed = "Chat_UI_Sticker_Pack_Changed"
"""Fired by the local toon when stickers are added or removed from their sticker pack."""

UI_Sticker_Pack_Ordered = "Chat_UI_Sticker_Pack_Ordered"
"""Fired by the local toon when the order of their sticker pack is updated."""

UI_Sticker_Row_Option_changed = "option-update-sticker-menu-rows"
"""Fired by the options manager whenever a Toon updates the sticker rows setting."""

"""
Store
"""
UI_MessageStore_Updated = "Chat_UI_MessageStore_Updated"
"""Fired by the message store when a message is added to one or more message collections."""

UI_MessageStore_Cleared = "Chat_UI_MessageStore_Cleared"
"""Fired by the message store when a message collection is cleared."""

"""
Whisper
"""
UI_WhisperTargets_Add = "Chat_UI_WhisperTargets_Add"
"""Fired by various sources to add a whisper target."""

UI_WhisperTargets_Remove = "Chat_UI_WhisperTargets_Remove"
"""Fired by various sources to remove a whisper target."""

UI_WhisperTargets_Updated = "Chat_UI_WhisperTargets_Updated"
"""Fired by the whisper manager when a toon is added or removed from the whisper targets."""

UI_WhisperTargets_SetLock = "Chat_UI_WhisperTargets_SetLock"
"""Sets the lock on a Whisper Target, to prevent it from removal."""
