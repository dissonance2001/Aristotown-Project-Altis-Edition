from toontown.toonbase import ToontownGlobals

TAB_FRIENDS = 0
TAB_GROUPS = 1
TAB_MAIL = 2
TAB_CLUBS = 3
TAB_FRIENDS_INVITE = 4

DEFAULT_TAB = TAB_FRIENDS
friendYOffset = 0.5


def _loadModel(path):
    if hasattr(loader, 'loadModelRaw'):
        model = loader.loadModelRaw(path)
    else:
        model = loader.loadModel(path)
    return model


sp_gui = _loadModel('phase_3.5/models/gui/socialpanel/social_panel')
sp_gui_icons = _loadModel('phase_3.5/models/gui/socialpanel/social_panel_icons')
sp_gui_bgs = _loadModel('phase_3.5/models/gui/socialpanel/social_panel_groupbgs')
social_buttons_gui = _loadModel('phase_3.5/models/gui/cc_m_txc_gui_social_buttons')
