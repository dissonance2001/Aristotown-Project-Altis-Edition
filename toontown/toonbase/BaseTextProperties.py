from toontown.gui.GUIGlobals import GUI_ICON_MODEL_PATH, GUI_TEXCARD_PREFIX

if __name__ == "__main__":
    from tools.headless.headlessbase import HeadlessStart
    from tools.headless.headlessbase.HeadlessBase import HeadlessBase

    base = HeadlessBase()

from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TextPropertiesManager, TextProperties, TextGraphic, Texture, NodePath
from toontown.utils import ColorHelper
from toontown.toonbase import ToontownGlobals


def initializeBaseTextProperties():
    # Set up the default colors of the IME candidate strings.
    tpm = TextPropertiesManager.getGlobalPtr()
    candidateActive = TextProperties()
    candidateActive.setTextColor(0, 0, 1, 1)
    tpm.setProperties('candidate_active', candidateActive)
    candidateInactive = TextProperties()
    candidateInactive.setTextColor(0.3, 0.3, 0.7, 1)
    tpm.setProperties('candidate_inactive', candidateInactive)

    battleSubtext = TextProperties()
    battleSubtext.setTextColor(0.85, 0.78, 1.0, 1)
    battleSubtext.setTextScale(0.5)
    tpm.setProperties('battle_subtext', battleSubtext)

    damageSubtext = TextProperties()
    damageSubtext.setTextColor(0.85, 0.78, 1.0, 1)
    damageSubtext.setTextScale(0.8)
    tpm.setProperties('damage_subtext', damageSubtext)

    damageSubtextOrange = TextProperties()
    damageSubtextOrange.setTextColor(1.0, 0.5, 0.0, 1.0)
    damageSubtextOrange.setTextScale(0.8)
    tpm.setProperties('damage_subtext_orange', damageSubtextOrange)

    soakText = TextProperties()
    soakText.setTextColor(0.600, 0.608, 1, 1)
    tpm.setProperties('soak_text', soakText)

    battleInfoSoakText = TextProperties()
    battleInfoSoakText.setTextColor(0.600, 0.608, 1, 1)
    battleInfoSoakText.setFont(ToontownGlobals.getSignFont())
    battleInfoSoakText.setGlyphShift(-0.06)
    tpm.setProperties('BattleInfo_SoakText', battleInfoSoakText)

    battleInfoCheerText = TextProperties()
    battleInfoCheerText.setTextColor(0.5, 1, 0.5, 1)
    battleInfoCheerText.setFont(ToontownGlobals.getSignFont())
    battleInfoCheerText.setGlyphShift(-0.06)
    tpm.setProperties('BattleInfo_CheerText', battleInfoCheerText)

    battleInfoEncoreText = TextProperties()
    battleInfoEncoreText.setTextColor(0.941, 0.807, 0.054, 1)
    battleInfoEncoreText.setFont(ToontownGlobals.getSignFont())
    battleInfoEncoreText.setGlyphShift(-0.06)
    tpm.setProperties('BattleInfo_EncoreText', battleInfoEncoreText)

    battleInfoMFLText = TextProperties()
    battleInfoMFLText.setTextColor(0.992, 0.466, 0.862, 1)
    battleInfoMFLText.setFont(ToontownGlobals.getSignFont())
    battleInfoMFLText.setGlyphShift(-0.06)
    tpm.setProperties('BattleInfo_MFLText', battleInfoMFLText)

    battleInfoDazedText = TextProperties()
    battleInfoDazedText.setTextColor(1.0, 1.0, 0.5, 1)
    battleInfoDazedText.setFont(ToontownGlobals.getSignFont())
    battleInfoDazedText.setGlyphShift(-0.06)
    tpm.setProperties('BattleInfo_DazedText', battleInfoDazedText)

    battleInfoWindedText = TextProperties()
    battleInfoWindedText.setTextColor(0.412, 0.412, 0.705, 1)
    battleInfoWindedText.setFont(ToontownGlobals.getSignFont())
    battleInfoWindedText.setGlyphShift(-0.06)
    tpm.setProperties('BattleInfo_WindedText', battleInfoWindedText)

    deepBlue = TextProperties()
    deepBlue.setTextColor(0, 0, 0.25, 1)
    tpm.setProperties('deepBlue', deepBlue)

    deepGreen = TextProperties()
    deepGreen.setTextColor(0, 0.45, 0, 1)
    tpm.setProperties('deepGreen', deepGreen)

    deepRed = TextProperties()
    deepRed.setTextColor(0.45, 0, 0, 1)
    tpm.setProperties('deepRed', deepRed)

    deepYellow = TextProperties()
    deepYellow.setTextColor(0.859, 0.643, 0.165, 1.0)
    deepYellow.setShadow(.05)
    tpm.setProperties('deepYellow', deepYellow)

    deepGray = TextProperties()
    deepGray.setTextColor(0.25, 0.25, 0.25, 1.0)
    tpm.setProperties('deepGray', deepGray)

    brightBlue = TextProperties()
    brightBlue.setTextColor(0, 0, 1, 1)
    tpm.setProperties('brightBlue', brightBlue)

    brightRed = TextProperties()
    brightRed.setTextColor(1, 0, 0, 1)
    tpm.setProperties('brightRed', brightRed)

    brightGreen = TextProperties()
    brightGreen.setTextColor(0, 1, 0, 1)
    tpm.setProperties('brightGreen', brightGreen)

    from toontown.clashbattle.battle import BattleGlobals
    for i, trackCol in enumerate(BattleGlobals.TrackColors):
        tp = TextProperties()
        tp.setTextColor(*trackCol, 1)
        tp.setShadow(.05)
        tpm.setProperties(f'deepTrackCol_{i}', tp)

    cyan = TextProperties()
    cyan.setTextColor(0, 0.741, 0.741, 1.0)
    tpm.setProperties('cyan', cyan)

    refundRed = TextProperties()
    refundRed.setTextColor(0.698, 0, 0, 1.0)
    tpm.setProperties('refundRed', refundRed)

    yellow = TextProperties()
    yellow.setTextColor(1, 1, 0, 1)
    tpm.setProperties('yellow', yellow)

    orange = TextProperties()
    orange.setTextColor(1, 0.5, 0, 1)
    tpm.setProperties('orange', orange)

    lightorange = TextProperties()
    lightorange.setTextColor(1, 0.75, 0.25, 1)
    tpm.setProperties('lightorange', lightorange)

    purple = TextProperties()
    purple.setTextColor(0.5, 0, 1, 1)
    tpm.setProperties('purple', purple)

    pink = TextProperties()
    pink.setTextColor(1, 0.6, 0.6, 1)
    tpm.setProperties('pink', pink)

    white = TextProperties()
    white.setTextColor(1, 1, 1, 1)
    tpm.setProperties('white', white)

    black = TextProperties()
    black.setTextColor(0, 0, 0, 1)
    tpm.setProperties('black', black)

    gray = TextProperties()
    gray.setTextColor(0.5, 0.5, 0.5, 1)
    tpm.setProperties('gray', gray)

    shiftDown = TextProperties()
    shiftDown.setGlyphShift(-0.06)
    tpm.setProperties('shiftDown', shiftDown)

    signFontProperty = TextProperties()
    signFontProperty.setFont(ToontownGlobals.getSignFont())
    tpm.setProperties("signFont", signFontProperty)

    minnieFontProperty = TextProperties()
    minnieFontProperty.setFont(ToontownGlobals.getMinnieFont())
    tpm.setProperties("minnieFont", minnieFontProperty)

    for i, golfColor in enumerate([(0.925, 0.168, 0.168, 1),
                                   (0.13, 0.59, 0.973, 1),
                                   (0.973, 0.809, 0.129, 1),
                                   (0.598, 0.402, 0.875, 1)]):
        golfColorProperty = TextProperties()
        golfColorProperty.setTextColor(*golfColor)
        tpm.setProperties(f"golfPlayerColor{i}", golfColorProperty)

    chatAllowListInvalidWord = TextProperties()
    chatAllowListInvalidWord.setSlant(0.3)
    chatAllowListInvalidWord.setTextColor(0.93, 1, 0, 1)
    chatAllowListInvalidWord.setShadow(.07)
    tpm.setProperties("CHAT_AL_WORD", chatAllowListInvalidWord)

    chatAllowListInvalidPrefix = TextProperties()
    chatAllowListInvalidPrefix.setTextColor(1, 0, 0, 1)
    chatAllowListInvalidPrefix.setShadow(.07)
    tpm.setProperties("CHAT_AL_PREFIX", chatAllowListInvalidPrefix)

    chatText = TextProperties()
    chatText.setTextColor(1, 1, 1, 1)
    tpm.setProperties("CHAT_TEXT", chatText)

    chatLightPurple = TextProperties()
    chatLightPurple.setTextColor(0.529, 0.447, 0.871, 1)
    tpm.setProperties("CHAT_COLOR_LP", chatLightPurple)

    chatLightGreen = TextProperties()
    chatLightGreen.setTextColor(0.424, 0.835, 0.447, 1)
    tpm.setProperties("CHAT_COLOR_LG", chatLightGreen)

    chatOrange = TextProperties()
    chatOrange.setTextColor(1, 0.6, 0.2, 1)
    tpm.setProperties("CHAT_COLOR_O", chatOrange)

    chatPalered = TextProperties()
    chatPalered.setTextColor(1, 0.376, 0.376, 1)
    tpm.setProperties("CHAT_COLOR_PAL", chatPalered)

    chatCyan = TextProperties()
    chatCyan.setTextColor(0, 0.63, 0.909, 1)
    tpm.setProperties("CHAT_COLOR_C", chatCyan)

    chatYellow = TextProperties()
    chatYellow.setTextColor(1, 1, 0, 1)
    tpm.setProperties("CHAT_COLOR_Y", chatYellow)

    chatMessageInfo = TextProperties()
    chatMessageInfo.setTextColor(0.561, 0.584, 0.671, 1.0)
    chatMessageInfo.setShadow(.05)
    chatMessageInfo.setSlant(0.2)
    tpm.setProperties("CHAT_MSG_INFO", chatMessageInfo)

    chatMessageInfoAlert = TextProperties()
    chatMessageInfoAlert.setTextColor(1, 0.2, 0.2, 1.0)
    chatMessageInfoAlert.setShadow(.05)
    chatMessageInfoAlert.setSlant(0.2)
    tpm.setProperties("CHAT_MSG_INFO_ALERT", chatMessageInfoAlert)

    chatMessagePlayer = TextProperties()
    chatMessagePlayer.setTextColor(0.424, 0.835, 0.447, 1.0)
    chatMessagePlayer.setShadow(.01)
    tpm.setProperties("CHAT_MSG_PLAYER", chatMessagePlayer)

    chatMessagePlayerBlue = TextProperties()
    chatMessagePlayerBlue.setTextColor(0, 0.702, 1, 1.0)
    chatMessagePlayerBlue.setShadow(.05)
    tpm.setProperties("CHAT_MSG_PLAYER_BLUE", chatMessagePlayerBlue)

    chatMessageWhisper = TextProperties()
    chatMessageWhisper.setTextColor(0.686, 0.627, 0.914, 1.0)
    chatMessageWhisper.setShadow(.05)
    chatMessageWhisper.setSlant(0.2)
    tpm.setProperties("CHAT_MSG_WHISPER", chatMessageWhisper)

    chatMessageSystem = TextProperties()
    chatMessageSystem.setTextColor(0.871, 0.388, 0.388, 1.0)
    chatMessageSystem.setShadow(.05)
    tpm.setProperties("CHAT_MSG_SYSTEM", chatMessageSystem)

    chatMessageNpc = TextProperties()
    chatMessageNpc.setTextColor(0.843, 0.855, 0.404, 1.0)
    chatMessageNpc.setShadow(.05)
    tpm.setProperties("CHAT_MSG_NPC", chatMessageNpc)

    chatMessageCog = TextProperties()
    chatMessageCog.setTextColor(0.333, 0.38, 0.941, 1.0)
    chatMessageCog.setShadow(.05)
    tpm.setProperties("CHAT_MSG_COG", chatMessageCog)

    chatMessageClub = TextProperties()
    chatMessageClub.setTextColor(0.392, 0.82, 0.867, 1.0)
    chatMessageClub.setShadow(.05)
    tpm.setProperties("CHAT_MSG_CLUB", chatMessageClub)

    chatMessageGroup = TextProperties()
    chatMessageGroup.setTextColor(0.851, 0.643, 0.408, 1.0)
    chatMessageGroup.setShadow(.05)
    tpm.setProperties("CHAT_MSG_GROUP", chatMessageGroup)

    chatMessageStaffLocal = TextProperties()
    chatMessageStaffLocal.setTextColor(0.949, 0, 0, 1.0)
    chatMessageStaffLocal.setShadow(.05)
    chatMessageStaffLocal.setUnderscore(1)
    tpm.setProperties("CHAT_MSG_STAFFLOCAL", chatMessageStaffLocal)

    chatMessageStaffGlobal = TextProperties()
    chatMessageStaffGlobal.setTextColor(0.718, 0.11, 0.941, 1.0)
    chatMessageStaffGlobal.setShadow(.05)
    chatMessageStaffGlobal.setUnderscore(1)
    tpm.setProperties("CHAT_MSG_STAFFGLOBAL", chatMessageStaffGlobal)

    chatMessageEmote = TextProperties()
    chatMessageEmote.setTextColor(0.3, 0.8, 0.3, 1.0)
    chatMessageEmote.setShadow(.05)
    chatMessageEmote.setSlant(0.2)
    tpm.setProperties("CHAT_MSG_EMOTE", chatMessageEmote)

    ftf_dualCoreColor = TextProperties()
    ftf_dualCoreColor.setTextColor(1.0, 1.0, 1.0, 1.0)
    tpm.setProperties("ftf_dualCoreColor", ftf_dualCoreColor)

    lootFrame_holdShiftColor = TextProperties()
    lootFrame_holdShiftColor.setTextColor(1.0, 1.0, 1.0, 1.0)
    tpm.setProperties("lootFrame_holdShiftColor", lootFrame_holdShiftColor)

    racing_bronze = TextProperties()
    racing_bronze.setTextColor(0.859, 0.643, 0.165, 1.0)
    racing_bronze.setShadow(.05)
    tpm.setProperties('racing_bronze', racing_bronze)

    racing_silver = TextProperties()
    racing_silver.setTextColor(151/255, 178/255, 216/255, 1.0)
    racing_silver.setShadow(.05)
    tpm.setProperties('racing_silver', racing_silver)

    racing_gold = TextProperties()
    racing_gold.setTextColor(216/255, 208/255, 93/255, 1.0)
    racing_gold.setShadow(.05)
    tpm.setProperties('racing_gold', racing_gold)

    black_emphasis = TextProperties()
    black_emphasis.setTextColor(0.0, 0.0, 0.0, 1.0)
    black_emphasis.setShadow(.05)
    tpm.setProperties("black_emphasis", black_emphasis)

    suitText_boardbot = TextProperties()
    suitText_boardbot.setTextColor(ColorHelper.hexToPCol('128285'))
    suitText_boardbot.setShadow(.05)
    tpm.setProperties("suitText_boardbot", suitText_boardbot)

    itemHoverUnderline = TextProperties()
    itemHoverUnderline.setTextColor(1.0, 1.0, 1.0, 0.3)
    tpm.setProperties("item_hover_underline", itemHoverUnderline)

    shop_tag = TextProperties()
    shop_tag.setTextColor(1.0, 0.5, 0.1, 1.0)
    tpm.setProperties("shop_tag", shop_tag)

    shop_subtag = TextProperties()
    shop_subtag.setTextColor(0.8, 0.7, 0.2, 1.0)
    shop_subtag.setTextScale(0.85)
    tpm.setProperties("shop_subtag", shop_subtag)


def initializeBaseTextGraphics():
    tpm = TextPropertiesManager.getGlobalPtr()

    statuses = loader.loadModel('phase_3.5/models/gui/battlegui/status_effects')
    statusIconData = (
        ('soaked', 1.6, (-0.3, 0.3, -0.4, 0.4)),
        ('reward_cooldown', 0.95, (-0.4, 0.3, -0.35, 0.4)),
        ('toon_damage_down', 0.95, (-0.4, 0.3, -0.35, 0.4)),
        ('broken_shield', 0.95, (-0.4, 0.3, -0.35, 0.4)),
        ('sued', 0.95, (-0.4, 0.3, -0.35, 0.4)),
        ('counterfeit', 0.8, (-0.375, 0.3, -0.27, 0.3), '_popup'),
        ('reward_cooldown', 1.85, (-0.4, 0.3, -0.4, 0.3), '_counterfeit'),
        ('counterfeit', 1.85, (-0.4, 0.3, -0.4, 0.3), '_counterfeit'),
        ('red_thread', 1, (-0.45, 0.3, -0.4, 0.3)),
    )

    for seIcon, seScale, seFrame, *extras in statusIconData:
        iconGraphic = TextGraphic()
        icon = statuses.find(f"**/{seIcon}_icon").copyTo(NodePath())
        icon.setScale(seScale)
        iconGraphic.setModel(icon)
        iconGraphic.setFrame(seFrame)
        tpm.setGraphic(f"battle_{seIcon}Icon{extras[0] if len(extras) else ''}", iconGraphic)

    statuses.removeNode()

    commonIconsTexcard = loader.loadModel(f'{GUI_ICON_MODEL_PATH}{GUI_TEXCARD_PREFIX}icon_common')
    throwableIconsTexcard = loader.loadModel(f'{GUI_ICON_MODEL_PATH}{GUI_TEXCARD_PREFIX}icon_throwables')

    beanIcon = TextGraphic()
    beanModel = commonIconsTexcard.find("**/jellybean_1")
    beanModel.setScale(0.8)
    beanIcon.setModel(beanModel)
    beanIcon.setFrame((-0.25, 0.25, -0.2, 0.2))
    beanModel.removeNode()
    tpm.setGraphic("reward_beanIcon", beanIcon)

    jarIcon = TextGraphic()
    jarModel = commonIconsTexcard.find("**/jellybeanJar_1")
    jarModel.setScale(1.75/2)
    jarIcon.setModel(jarModel)
    jarIcon.setFrame((-0.25, 0.25, -0.25, 0.2))
    jarModel.removeNode()
    tpm.setGraphic("reward_beanJarIcon", jarIcon)

    expIcon = TextGraphic()
    expModel = commonIconsTexcard.find('**/exp_1')
    expIcon.setModel(expModel)
    expIcon.setFrame((-0.25, 0.25, -0.2, 0.2))
    expModel.removeNode()
    tpm.setGraphic("reward_expIcon", expIcon)

    fishIcon = TextGraphic()
    fishModel = commonIconsTexcard.find('**/fish_1')
    fishModel.setScale(1.0)
    fishIcon.setModel(fishModel)
    fishIcon.setFrame((-0.25, 0.25, -0.25, 0.2))
    fishModel.removeNode()
    tpm.setGraphic("reward_fishieIcon", fishIcon)

    clubCoinIcon = TextGraphic()
    clubIconModel = loader.loadModel('phase_3.5/models/gui/clubs/club_shop')
    clubCoinIcon.setModel(clubIconModel.find('**/choc'))
    clubCoinIcon.setFrame((-0.35, 0.35, -0.3, 0.2))
    clubIconModel.removeNode()
    tpm.setGraphic("reward_clubCoin", clubCoinIcon)

    disguiseIcon = TextGraphic()
    disguiseModel = commonIconsTexcard.find('**/disguise_3')
    disguiseModel.setScale(0.85)
    disguiseIcon.setModel(disguiseModel)
    disguiseIcon.setFrame((-0.4, 0.4, -0.25, 0.2))
    disguiseModel.removeNode()
    tpm.setGraphic("reward_disguiseIcon", disguiseIcon)

    teleportIcon = TextGraphic()
    teleportModel = commonIconsTexcard.find('**/teleport_1')
    teleportModel.setScale(0.8)
    teleportIcon.setModel(teleportModel)
    teleportIcon.setFrame((-0.25, 0.4, -0.2, 0.2))
    teleportModel.removeNode()
    tpm.setGraphic("reward_teleportIcon", teleportIcon)

    HpTextGenerator = TextNode('HpTextGenerator')
    HpTextGenerator.setFont(ToontownGlobals.getSignFont())
    HpTextGenerator.clearShadow()
    HpTextGenerator.setAlign(TextNode.ACenter)
    r, g, b, a = 0, 0.9, 0, 1
    HpTextGenerator.setTextColor(r, g, b, a)

    for i in range(10):
        HpTextGenerator.setText("+" + str(i + 1))
        hpTextNode = HpTextGenerator.generate()
        realNode = NodePath(hpTextNode)
        realNode.setScale(1)

        laffIcon = TextGraphic()
        laffIcon.setModel(realNode)
        laffIcon.setFrame((-0.5, 0.5, 0.065, 0.3))
        tpm.setGraphic(f"reward_laffIcon{i + 1}", laffIcon)
        del hpTextNode
        realNode.removeNode()
        del realNode

    # Not even using this right now but keeping it around
    for hpString in ['+']:
        HpTextGenerator.setText(hpString)
        hpTextNode = HpTextGenerator.generate()
        realNode = NodePath(hpTextNode)
        realNode.setScale(1)

        stringIcon = TextGraphic()
        stringIcon.setModel(realNode)
        stringIcon.setFrame((-0.35, 0.4, 0.065, 0.3))
        tpm.setGraphic(f"reward_hpString_{hpString}", stringIcon)
        del hpTextNode
        realNode.removeNode()
        del realNode

    del HpTextGenerator

    packageIcon = TextGraphic()
    packageIconCentered = TextGraphic()
    packageModel = commonIconsTexcard.find('**/package_1')
    packageModel.setScale(0.9)
    packageIcon.setModel(packageModel)
    packageIconCentered.setModel(packageModel)
    packageIcon.setFrame((-0.35, 0.4, -0.25, 0.2))
    packageIconCentered.setFrame(-0.4, 0.4, -0.275, 0.2)
    packageModel.removeNode()
    tpm.setGraphic("reward_packageIcon", packageIcon)
    tpm.setGraphic("reward_packageIconCentered", packageIconCentered)

    gumballIcon = TextGraphic()
    gumballModel = commonIconsTexcard.find('**/gumball_1')
    gumballModel.setScale(0.5)
    gumballIcon.setModel(gumballModel)
    gumballIcon.setFrame((-0.5, 0.5, -0.2, 0.2))
    tpm.setGraphic("reward_gumballIcon", gumballIcon)

    pineappleIcon = TextGraphic()
    pineappleModel = throwableIconsTexcard.find('**/pineapple_1')
    pineappleModel.setScale(0.7)
    pineappleIcon.setModel(pineappleModel)
    pineappleIcon.setFrame((-0.7, 0.5, -0.4, 0.2))
    tpm.setGraphic("pineapple", pineappleIcon)

    summonIcon = TextGraphic()
    summonModel = throwableIconsTexcard.find('**/summons_1')
    summonModel.setScale(0.8)
    summonIcon.setModel(summonModel)
    summonIcon.setFrame((-0.25, 0.25, -0.3, 0.2))
    tpm.setGraphic("reward_summonIcon", summonIcon)

    kudosGui = loader.loadModel('phase_3.5/models/gui/kudos/kudos_board_gui')
    for kudosStr in ('Bronze', 'Silver', 'Gold', 'RankUp'):
        kudosIcon = TextGraphic()
        kudosIcon.setModel(kudosGui.find(f'**/Kudos_Ribbon_{kudosStr}'))
        kudosIcon.setFrame(-0.4, 0.4, -0.275, 0.2)
        tpm.setGraphic(f"reward_kudos{kudosStr}", kudosIcon)

        kudosIconSmall = TextGraphic()
        smallGeom = kudosGui.find(f'**/Kudos_Ribbon_{kudosStr}_S')
        smallGeom.setScale(1.3)
        kudosIconSmall.setModel(smallGeom)
        kudosIconSmall.setFrame(-0.4, 0.4, -0.275, 0.2)
        tpm.setGraphic(f"reward_kudos{kudosStr}Small", kudosIconSmall)
    kudosGui.removeNode()

    clubGui = loader.loadModel('phase_3.5/models/gui/clubs/club_icons')
    for clubStr, clubName in (
        ('12', 'TTC'),
        ('13', 'BB'),
        ('14', 'YOTT'),
        ('15', 'DG'),
        ('16', 'MML'),
        ('17', 'TB'),
        ('18', 'AA'),
        ('19', 'DDL'),
    ):
        clubIcon = TextGraphic()
        clubIcon.setModel(clubGui.find(f'**/icon_{clubStr}'))
        clubIcon.setFrame(-0.4, 0.4, -0.275, 0.2)
        tpm.setGraphic(f"club_icon{clubName}", clubIcon)
    clubGui.removeNode()

    invIcons = loader.loadModel('phase_3.5/models/gui/inventory_icons')
    for track in list(range(8)):
        for level in list(range(8)):
            gagIcon = TextGraphic()
            gagGeom = invIcons.find(f'**/prop_{track}_{level}')
            gagGeom.setScale(7)
            gagIcon.setModel(gagGeom)
            gagIcon.setFrame((-0.25, 0.25, -0.275, 0.2))

            tpm.setGraphic(f"icon_battleProp_{track}_{level}", gagIcon)
    invIcons.removeNode()

    syncIcon = TextGraphic()
    battleGui = loader.loadModel('phase_3.5/models/gui/battlegui/gag_selection_panels')
    syncIcon.setModel(battleGui.find('**/sync_icon'))
    syncIcon.setFrame((-0.4, 0.4, -0.36, 0.2))
    battleGui.removeNode()
    tpm.setGraphic("icon_contentSync", syncIcon)

    socialPanelGui = loader.loadModel('phase_3.5/models/gui/socialpanel/social_panel_icons')

    checkmarkIcon = TextGraphic()
    checkmarkIcon.setModel(socialPanelGui.find('**/CIRCLE3'))
    checkmarkIcon.setFrame((-0.4, 0.4, -0.275, 0.2))
    tpm.setGraphic("icon_checkmark", checkmarkIcon)

    circleIcon = TextGraphic()
    circleIcon.setModel(socialPanelGui.find('**/CIRCLE2'))
    circleIcon.setFrame((-0.4, 0.4, -0.275, 0.2))
    tpm.setGraphic("icon_greenCircle", circleIcon)

    socialPanelGui.removeNode()

    sp_gui = loader.loadModel('phase_3.5/models/gui/socialpanel/social_panel')
    groupsIcon = TextGraphic()
    groupsIconNode = sp_gui.find('**/ToonButton_N')
    btnScale = 2.5
    groupsIconNode.setScale(btnScale * (123/84), btnScale, btnScale)
    groupsIcon.setModel(groupsIconNode)
    groupsIcon.setFrame(-1.0, 1.0, -1.0, 1.0)
    tpm.setGraphic('icon_social_groups', groupsIcon)
    sp_gui.removeNode()

    clubGui = loader.loadModel('phase_3.5/models/gui/clubs/club_backgrounds')
    circleClubIconWhite = TextGraphic()
    clubIconNode = clubGui.find('**/bg_30')
    clubIconNode.setScale(1.1)
    circleClubIconWhite.setModel(clubIconNode)
    circleClubIconWhite.setFrame((-0.4, 0.4, -0.2, 0.2))
    tpm.setGraphic("icon_clubTriangleWhite", circleClubIconWhite)
    clubGui.removeNode()

    diceGui = loader.loadModel('phase_4/models/gui/cc_m_gui_gen_dice')
    goldDiceIcon = TextGraphic()
    goldDiceIcon.setModel(diceGui.find(f'**/cc_t_gui_gen_golddice_6_up'))
    goldDiceIcon.setFrame((-0.4, 0.4, -0.275, 0.2))
    tpm.setGraphic("icon_goldDice", goldDiceIcon)
    diceGui.removeNode()

    matchingGameGui = loader.loadModel('phase_3.5/models/gui/matching_game_gui')
    matchingCircleIcon = TextGraphic()
    matchingCircleNode = matchingGameGui.find(f'**/minnieCircle')
    matchingCircleNode.setScale(5)
    matchingCircleIcon.setModel(matchingCircleNode)
    matchingCircleIcon.setFrame((-0.4, 0.2, -0.2, 0.4))
    tpm.setGraphic("icon_matchingCircle", matchingCircleIcon)
    matchingGameGui.removeNode()

    safeGeom = loader.loadModel('phase_10/models/cashbotHQ/CashBotSafe')
    safeGeom.find('**/SafeShadow1').removeNode()
    safeHolder = NodePath('textGraphic-safeHolder')
    safeGeom.reparentTo(safeHolder)
    safeGeom.setZ(-11.5)
    s = 0.9
    safeHolder.setScale(0.1*s, 0.1*s, 0.065*s)
    safeHolder.setDepthTest(1)
    safeHolder.setDepthWrite(1)
    safeIcon = TextGraphic()
    safeIcon.setModel(safeHolder)
    safeIcon.setFrame((-0.5, 0.5, -0.3, 0.3))
    tpm.setGraphic("icon_cashbotSafe", safeIcon)
    safeHolder.removeNode()

    gearIcon = TextGraphic()
    gearGui = loader.loadModel('phase_3/models/gui/cog_icons')
    model = gearGui.find('**/cog')
    gearIcon.setModel(model)
    gearIcon.setFrame(-0.4, 0.4, -0.275, 0.2)
    tpm.setGraphic('gearIcon', gearIcon)
    gearGui.removeNode()

    sellbot = TextGraphic()
    cashbot = TextGraphic()
    lawbot = TextGraphic()
    bossbot = TextGraphic()
    boardbot = TextGraphic()
    insignias = loader.loadModel('phase_3.5/models/char/ttcc_ene_insignias')
    for graphic, suffix in zip(
        [sellbot, cashbot, lawbot, bossbot, boardbot],
        ['sales', 'money', 'legal', 'corp', 'board']
            ):
        model = insignias.find(f'**/emblem_{suffix}')
        model.setScale(1.4)
        graphic.setModel(model)
        graphic.setFrame((-0.4, 0.4, -0.275, 0.2))
    tpm.setGraphic("sellbot", sellbot)
    tpm.setGraphic("cashbot", cashbot)
    tpm.setGraphic("lawbot", lawbot)
    tpm.setGraphic("bossbot", bossbot)
    tpm.setGraphic("boardbot", boardbot)
    insignias.removeNode()

    sellbotNametag = TextGraphic()
    cashbotNametag = TextGraphic()
    lawbotNametag = TextGraphic()
    bossbotNametag = TextGraphic()
    boardbotNametag = TextGraphic()
    insignias = loader.loadModel('phase_3.5/models/char/ttcc_ene_insignias')
    for graphic, suffix in zip(
        [sellbotNametag, cashbotNametag, lawbotNametag, bossbotNametag, boardbotNametag],
        ['sales', 'money', 'legal', 'corp', 'board']
            ):
        model = insignias.find(f'**/emblem_{suffix}')
        model.setScale(1.9)
        graphic.setModel(model)
        graphic.setFrame((-0.45, 0.55, -0.3, 0.3))
    tpm.setGraphic("sellbotNametag", sellbotNametag)
    tpm.setGraphic("cashbotNametag", cashbotNametag)
    tpm.setGraphic("lawbotNametag", lawbotNametag)
    tpm.setGraphic("bossbotNametag", bossbotNametag)
    tpm.setGraphic("boardbotNametag", boardbotNametag)
    insignias.removeNode()

if __name__ == "__main__":
    # Run to test validity of assets
    # Valid assets will not crash client
    initializeBaseTextProperties()
    base.run()
