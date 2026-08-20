from __future__ import absolute_import
from toontown.toonbase import ToontownGlobals
from toontown.hood import ZoneUtil

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


groupsPerRow = 1
groupsPerCol = 6

def getSocialPanelGroupBg(group, pgOnly=False):
    activity = ''
    zoneId = 0
    try:
        activity = str(group.get('activity', ''))
        zoneId = int(group.get('zoneId', 0))
    except:
        try:
            activity = str(group.activity)
            zoneId = int(group.zoneId)
        except:
            pass
    name = None
    if not pgOnly:
        name = {
            'Sellbot Factory': 'pg_factory',
            'Lawbot DA Office': 'pg_lawfice',
            'Bossbot Country Club': 'pg_cgc',
            'VP': 'pg_sbhq',
            'CFO': 'pg_cbhq',
            'CJ': 'pg_lbhq',
            'CEO': 'pg_bbhq',
            'Racing': 'pg_race',
            'Golfing': 'pg_minigames',
        }.get(activity)
    if not name:
        try:
            hoodId = ZoneUtil.getHoodId(zoneId)
        except:
            hoodId = zoneId
        hoodMap = {}
        for constName, bgName in (
            ('ToontownCentral', 'pg_ttc'),
            ('DonaldsDock', 'pg_bb'),
            ('DaisyGardens', 'pg_dg'),
            ('MinniesMelodyland', 'pg_mml'),
            ('TheBrrrgh', 'pg_brrrgh'),
            ('OutdoorZone', 'pg_aa'),
            ('DonaldsDreamland', 'pg_ddl'),
            ('GolfZone', 'pg_minigames'),
            ('GoofySpeedway', 'pg_race'),
            ('SellbotHQ', 'pg_sbhq'),
            ('CashbotHQ', 'pg_cbhq'),
            ('LawbotHQ', 'pg_lbhq'),
            ('BossbotHQ', 'pg_bbhq')):
            value = getattr(ToontownGlobals, constName, None)
            if value is not None:
                hoodMap[value] = bgName
        name = hoodMap.get(hoodId)
    return sp_gui_bgs.find('**/%s' % (name or 'pg_brrrgh'))
