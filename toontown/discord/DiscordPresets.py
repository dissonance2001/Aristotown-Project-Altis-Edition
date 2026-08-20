from __future__ import absolute_import
from toontown.toonbase import TTLocalizer

"""
Presets can be used to define rich presence status which aren't dynamicly done.
These are great for activities, menus and other elements of the game which use dynamic zones
Using the DiscordHandler call apply_preset with the preset name to set it.
"""

ALTIS_ZONE_NAMES = {
    1836: 'Lighthouse',
    2513: 'Toon Hall',
    2516: 'Toontown School House',
    2921: "Derrickman's Lobby",
    3740: 'Mozzarella Styx Pizzeria',
    4874: 'The Musical Master of Melody',
    6837: 'Cut to the Chase! Logging Co.',
    7507: 'Dungeon',
    8501: 'Speedway Karting',
    9613: 'Fast Asleep - All Star Suites',
    10101: 'Sellbot HQ VP Lobby',
    12300: 'Overclocked CLO Lobby',
}

def zoneName(zoneId):
    # Altis has fewer TTLocalizer aliases than Corporate Clash. Always
    # resolve zones dynamically and never let an unknown zone crash startup.
    try:
        street = TTLocalizer.GlobalStreetNames.get(zoneId)
        if street:
            return street[-1]
    except AttributeError:
        pass

    try:
        title = TTLocalizer.zone2TitleDict.get(zoneId)
        if title:
            return title[0] or ('Zone %s' % zoneId)
    except AttributeError:
        pass

    if zoneId in ALTIS_ZONE_NAMES:
        return ALTIS_ZONE_NAMES[zoneId]

    return 'Zone %s' % zoneId

SUIT_NAMES = {
    'derrman': 'Derrickman',
    'duckshfl': 'Duck Shuffler',
    'prethink': 'Prethinker',
    'dlao': 'Director of Land Acquisition',
    'ddiver': 'Deep Diver',
    'rainmake': 'Rainmaker',
    'dopr': 'Director of Public Relations',
    'gatekeep': 'Gatekeeper',
    'whunter': 'Witch Hunter',
    'bellring': 'Bellringer',
    'mslacker': 'Multislacker',
    'mouthp': 'Mouthpiece',
    'mplayer': 'Major Player',
    'fires': 'Firestarter',
    'pcrat': 'Plutocrat',
    'treek': 'Treekiller',
    'chainsaw': 'Chainsaw Consultant',
    'fbed': 'Featherbedder',
    'psetter': 'Pacesetter',
    'count': 'Count Erfit',
    'hroller': 'High Roller',
}

def suitName(name):
    return SUIT_NAMES.get(name, name)

zones = {
    1000: {
        'zoneName': zoneName(1000),
        'zoneImage': 'bb_pg',
    },
    1100: {
        'zoneName': zoneName(1100),
        'zoneImage': 'bb_bb',
    },
    1200: {
        'zoneName': zoneName(1200),
        'zoneImage': 'bb_ss',
    },
    1300: {
        'zoneName': zoneName(1300),
        'zoneImage': 'bb_ll',
    },
    1400: {
        'zoneName': zoneName(1400),
        'zoneImage': 'bb_aa',
    },
    1836: {
        'zoneName': zoneName(1836),
        'zoneImage': 'bb_lighthouse',
    },
    2000: {
        'zoneName': zoneName(2000),
        'zoneImage': 'ttc_pg',
    },
    2100: {
        'zoneName': zoneName(2100),
        'zoneImage': 'ttc_ss',
    },
    2200: {
        'zoneName': zoneName(2200),
        'zoneImage': 'ttc_ll',
    },
    2300: {
        'zoneName': zoneName(2300),
        'zoneImage': 'ttc_pp',
    },
    2400: {
        'zoneName': zoneName(2400),
        'zoneImage': 'ttc_ww',
    },
    2513: {
        'zoneName': 'Visiting ' + zoneName(2513),
        'zoneImage': 'ttc_toonhall',
    },
    2516: {
        'zoneName': 'Learning at the ' + zoneName(2516),
        'zoneImage': 'ttc_schoolhouse',
    },
    2921: {
        'zoneName': zoneName(2921),
        'zoneImage': 'ttc_gagsoline',
        'zoneImageHover': 'Derrick Man\'s Lobby',
    },
    3000: {
        'zoneName': zoneName(3000),
        'zoneImage': 'tb_pg',
    },
    3100: {
        'zoneName': zoneName(3100),
        'zoneImage': 'tb_ww',
    },
    3200: {
        'zoneName': zoneName(3200),
        'zoneImage': 'tb_ss',
    },
    3300: {
        'zoneName': zoneName(3300),
        'zoneImage': 'tb_pp',
    },
    3400: {
        'zoneName': zoneName(3400),
        'zoneImage': 'tb_aa',
    },
    3740: {
        'zoneName': zoneName(3740),
        'zoneImage': 'tb_pizza',
    },
    4000: {
        'zoneName': zoneName(4000),
        'zoneImage': 'mml_pg',
    },
    4100: {
        'zoneName': zoneName(4100),
        'zoneImage': 'mml_aa',
    },
    4200: {
        'zoneName': zoneName(4200),
        'zoneImage': 'mml_bb',
    },
    4300: {
        'zoneName': zoneName(4300),
        'zoneImage': 'mml_tt',
    },
    4400: {
        'zoneName': zoneName(4400),
        'zoneImage': 'mml_ss',
    },
    4874: {
        'zoneName': zoneName(4874),
        'zoneImage': 'mml_brubot',
    },
    5000: {
        'zoneName': zoneName(5000),
        'zoneImage': 'dg_pg',
    },
    5100: {
        'zoneName': zoneName(5100),
        'zoneImage': 'dg_pp',
    },
    5200: {
        'zoneName': zoneName(5200),
        'zoneImage': 'dg_dd',
    },
    5300: {
        'zoneName': zoneName(5300),
        'zoneImage': 'dg_tt',
    },
    5400: {
        'zoneName': zoneName(5400),
        'zoneImage': 'dg_ss',
    },
    6000: {
        'zoneName': zoneName(6000),
        'zoneImage': 'aa_pg',
    },
    6100: {
        'zoneName': zoneName(6100),
        'zoneImage': 'aa_aa',
    },
    6200: {
        'zoneName': zoneName(6200),
        'zoneImage': 'aa_pp',
    },
    6300: {
        'zoneName': zoneName(6300),
        'zoneImage': 'aa_ww',
    },
    6400: {
        'zoneName': zoneName(6400),
        'zoneImage': 'aa_ll',
    },
    6837: {
        'zoneName': 'Cut to the Chase! Logging Co.',
        'zoneImage': 'aa_loggingcorp',
    },
    7000: {
        'zoneName': zoneName(7000),
        'zoneImage': 'yott_pg',
    },
    7100: {
        'zoneName': zoneName(7100),
        'zoneImage': 'yott_kk',
    },
    7200: {
        'zoneName': zoneName(7200),
        'zoneImage': 'yott_nn',
    },
    7300: {
        'zoneName': zoneName(7300),
        'zoneImage': 'yott_ww',
    },
    7507: {
        'zoneName': zoneName(7507),
        'zoneImage': 'yott_dungeon',
    },
    8000: {
        'zoneName': zoneName(8000),
        'zoneImage': 'mg_rr',
    },
    8501: {
        'zoneName': zoneName(8501),
        'zoneImage': 'mg_rr_ks',
    },
    9000: {
        'zoneName': zoneName(9000),
        'zoneImage': 'ddl_pg',
    },
    9100: {
        'zoneName': zoneName(9100),
        'zoneImage': 'ddl_ll',
    },
    9200: {
        'zoneName': zoneName(9200),
        'zoneImage': 'ddl_pp',
    },
    9300: {
        'zoneName': zoneName(9300),
        'zoneImage': 'ddl_tt',
    },
    9613: {
        'zoneName': zoneName(9613),
        'zoneImage': 'ddl_suites',
    },
    10000: {
        'zoneName': zoneName(10000),
        'zoneImage': 'sbhq_pg',
    },
    10100: {
        'zoneName': zoneName(10100),
        'zoneImage': 'sbhq_vp_lobby',
    },
    10101: {
        'zoneName': zoneName(10101),
        'zoneImage': 'sbhq_jr_lobby',
    },
    10200: {
        'zoneName': zoneName(10200),
        'zoneImage': 'sbhq_factory_lobby',
    },
    11000: {
        'zoneName': zoneName(11000),
        'zoneImage': 'cbhq_pg',
    },
    11100: {
        'zoneName': zoneName(11100),
        'zoneImage': 'cbhq_cfo_lobby',
    },
    12000: {
        'zoneName': zoneName(12000),
        'zoneImage': 'lbhq_pg',
    },
    12100: {
        'zoneName': zoneName(12100),
        'zoneImage': 'lbhq_clo_lobby',
    },
    12200: {
        'zoneName': zoneName(12200),
        'zoneImage': 'lbhq_lawfice_lobby',
    },
    12300: {
        'zoneName': zoneName(12300),
        'zoneImage': 'lbhq_oclo_lobby'
    },
    13000: {
        'zoneName': zoneName(13000),
        'zoneImage': 'bbhq_pg',
    },
    13100: {
        'zoneName': zoneName(13100),
        'zoneImage': 'bbhq_ceo_lobby',
    },
    17000: {
        'zoneName': zoneName(17000),
        'zoneImage': 'mg_gf_pg',
    },
    18000: {
        'zoneName': zoneName(18000),
        'zoneImage': 'tst_pg',
    },
    19000: {
        'zoneName': zoneName(19000),
        'zoneImage': 'warning',
    },
}
presets = {
    # Game Setup
    'loading_game': {
        'state': 'Entering Toontown!',
        'large_image_key': 'mat_default',
    },
    'main_menu': {
        'state': 'At the Main Menu!',
        'large_image_key': 'menu_intro',
    },
    'pick_a_toon': {
        'state': 'Picking a Toon!',
        'large_image_key': 'menu_intro',
    },
    'make_a_toon': {
        'state': 'Making a Toon!',
        'large_image_key': 'mat_default',
    },
    'redraw_a_toon': {
        'state': 'Redrawing a Toon!',
        'large_image_key': 'mat_default',
    },
    'toontorial': {
        'state': 'In the Toontorial!',
        'large_image_key': 'ttc_schoolhouse',
    },

    ##  Globals (All Playgrounds) ##
    'trolley': {
        'state': 'On the trolley in %s!',
        'large_image_key': 'global_trolley',
    },
    'estate': {
        'state': 'At the Estate!',
        'large_image_key': 'global_estate',
    },

    # Activities
    'fishing': {
        'state': 'Fishing at %s!',
        'large_image_key': 'global_fishing',
    },
    'golfing': {
        'state': 'Golfing at %s!',
        'large_image_key': 'mg_golfing',
    },
    'racing': {
        'state': 'Racing on %s!',
        'large_image_key': 'mg_racing',
        'party': True,
        'max_party_size': 8,
    },
    'toono': {
        'state': 'Playing TOONO!',
        'large_image_key': 'mg_toono',
    },
    'chess': {
        'state': 'Playing Chess!',
        'large_image_key': 'mg_chess',
    },
    'checkers': {
        'state': 'Playing Checkers!',
        'large_image_key': 'mg_checkers',
    },

    ## Instances ##

    # Global
    'cog_bldg': {
        'state': 'On floor %s of a %s-story %s Cog Building!',
        'large_image_key': ['cog_bldg_bottom', 'cog_bldg_middle', 'cog_bldg_top', 'cog_bldg_roof'],
        'party': True,
        'max_party_size': 4,
    },
    'cog_battle': { # No large_image_key to reuse whichever one we had before
        'state': 'Battling Cogs %s %s!',
        'party': True,
        'max_party_size': 4,
    },

    # Toontown Central
    'derrickman': {
        'state': 'Saving Rain!',
        'large_image_hover': 'Fighting the %s!' % suitName('derrman'),
        'large_image_key': 'instance_derrickman',
    },
    'duckshfl': {
        'state': 'Raithing the Thtaketh!',
        'large_image_hover': 'Fighting the %s' %suitName('duckshfl') + ' on %s!',
        'large_image_key': 'merc_duckshfl',
    },
    'prethink': {
        'state': 'Outwitting the Prethinker!',
        'large_image_hover': 'Fighting the %s!' %suitName('prethink'),
        'large_image_key': 'instance_prethinker'
    },

    # Barnacle Boatyard
    'dola': {
        'state': 'Trespassing on the Architect\'s turf!',
        'large_image_hover': 'Fighting the %s!' % suitName('dlao'),
        'large_image_key': 'instance_dola',
    },
    'ddiver': {
        'state': 'Taking a dive!',
        'large_image_hover': 'Fighting the %s' % suitName('ddiver') + ' on %s!',
        'large_image_key': 'merc_ddiver',
    },
    'rainmake': {
        'state': 'Weathering the storm!',
        'large_image_hover': 'Fighting the %s!' % suitName('rainmake'),
        'large_image_key': 'instance_rainmake'
    },

    # Ye Olde Toontowne
    'dopr': {
        'state': 'Breaking into jail!',
        'large_image_hover': 'Fighting the %s!' % suitName('dopr'),
        'large_image_key': 'instance_dopr',
    },
    'gatekeep': {
        'state': 'Holding the front line!',
        'large_image_hover': 'Fighting the %s' % suitName('gatekeep') + ' on %s!',
        'large_image_key': 'merc_gatekeep',
    },
    'whunter': {
        'state': 'Managing the mob!',
        'large_image_hover': 'Fighting the %s!' % suitName('whunter'),
        'large_image_key': 'instance_whunter'
    },

    # Daffodil Gardens
    'bellring': {
        'state': 'Hearing the bells toll!',
        'large_image_hover': 'Fighting the %s' % suitName('bellring') + ' on %s!',
        'large_image_key': 'merc_bellring',
    },

    # Sellbot HQ
    'sb-factory': {
        'state': 'Infiltrating the Sellbot HQ Factory!',
        'large_image_key': 'sbhq_factory_inside',
    },
    'boss-s-1': {
        'state': 'Fighting the VP!',
        'large_image_key': 'sbhq_vp_battle',
        'large_image_hover': 'Sellbot Towers',
        'party': True,
        'max_party_size': 8,
    },
    'boss-s-2': {
        'state': 'Fighting the Cogs!',
        'large_image_key': 'sbhq_vp_battle',
        'large_image_hover': 'Sellbot Towers',
        'party': True,
        'max_party_size': 8,
    },
    'boss-s-3': {
        'state': 'Chasing the VP!',
        'large_image_key': 'sbhq_vp_battle',
        'large_image_hover': 'Sellbot Towers',
        'party': True,
        'max_party_size': 8,
    },
    'boss-s-4': {
        'state': 'Fighting Skelecogs!',
        'large_image_key': 'sbhq_vp_battle',
        'large_image_hover': 'Sellbot Towers',
        'party': True,
        'max_party_size': 8,
    },
    'boss-s-5': {
        'state': 'Throwing pies!',
        'large_image_key': 'sbhq_vp_battle',
        'large_image_hover': 'Sellbot Towers',
        'party': True,
        'max_party_size': 8,
    },
    'mslacker': {
        'state': 'Taking a lunch break!',
        'large_image_hover': 'Fighting the %s!' % suitName('mslacker'),
        'large_image_key': 'instance_mslacker'
    },

    # Mezzo Melodyland
    'mouthp': {
        'state': 'Baking cookies!',
        'large_image_hover': 'Fighting the %s' % suitName('mouthp') + ' on %s!',
        'large_image_key': 'merc_mouthp',
    },
    'mplayer': {
        'state': 'Skibidobabadadoo...',
        'large_image_hover': 'Fighting the %s!' % suitName('mplayer'),
        'large_image_key': 'instance_mplayer'
    },

    # Cashbot HQ
    'cb-mint': {
        'state': 'Infiltrating the Cashbot %s!',
        'large_image_key': 'cbhq_mint',
    },
    'boss-m-1': {
        'state': 'Fighting the CFO!',
        'large_image_key': 'cbhq_cfo_battle',
        'large_image_hover': 'Cashbot Vault',
        'party': True,
        'max_party_size': 8,
    },
    'boss-m-2': {
        'state': 'Fighting the Cogs!',
        'large_image_key': 'cbhq_cfo_battle',
        'large_image_hover': 'Cashbot Vault',
        'party': True,
        'max_party_size': 8,
    },
    'boss-m-3': {
        'state': 'Chasing the CFO!',
        'large_image_key': 'cbhq_cfo_battle',
        'large_image_hover': 'Cashbot Vault',
        'party': True,
        'max_party_size': 8,
    },
    'boss-m-4': {
        'state': 'Fighting the Skelecogs!',
        'large_image_key': 'cbhq_cfo_battle',
        'large_image_hover': 'Cashbot Vault',
        'party': True,
        'max_party_size': 8,
    },
    'boss-m-5': {
        'state': 'Stomping Goons!',
        'large_image_key': 'cbhq_cfo_battle',
        'large_image_hover': 'Cashbot Vault',
        'party': True,
        'max_party_size': 8,
    },
    'boss-m-6': {
        'state': 'Operating a crane!',
        'large_image_key': 'cbhq_cfo_battle',
        'large_image_hover': 'Cashbot Vault',
        'party': True,
        'max_party_size': 8,
    },

    # The Brrrgh
    'fires': {
        'state': 'Heating it up!',
        'large_image_hover': 'Fighting the %s' % suitName('fires') + ' on %s!',
        'large_image_key': 'merc_fires',
    },
    'pcrat': {
        'state': 'In sub-zero temperatures!',
        'large_image_hover': 'Fighting the %s!' % suitName('pcrat'),
        'large_image_key': 'instance_pcrat'
    },

    # Lawbot HQ
    'lawfice': {
        'state': 'Infiltrating a %s!',
        'large_image_key': 'lbhq_lawfice',
    },
    'boss-l-1': {
        'state': 'Fighting the CLO!',
        'large_image_key': 'lbhq_clo_battle',
        'large_image_hover': 'Lawbot Executive Lawfice',
        'party': True,
        'max_party_size': 8,
    },
    'boss-l-2': {
        'state': 'Fighting the Cogs!',
        'large_image_key': 'lbhq_clo_battle',
        'large_image_hover': 'Lawbot Executive Lawfice',
        'party': True,
        'max_party_size': 8,
    },
    'boss-l-3': {
        'state': 'Gathering evidence!',
        'large_image_key': 'lbhq_clo_battle',
        'large_image_hover': 'Lawbot Executive Lawfice',
        'party': True,
        'max_party_size': 8,
    },
    'boss-l-4': {
        'state': 'Fighting the laser Cogs!',
        'large_image_key': 'lbhq_clo_battle',
        'large_image_hover': 'Lawbot Executive Lawfice',
        'party': True,
        'max_party_size': 8,
    },
    'boss-l-5': {
        'state': 'Trapping the CLO!',
        'large_image_key': 'lbhq_clo_battle',
        'large_image_hover': 'Lawbot Executive Lawfice',
        'party': True,
        'max_party_size': 8,
    },
    'boss-ol-1': {
        'state': 'Fighting the OCLO!',
        'large_image_key': 'lbhq_clo_battle',
        'large_image_hover': 'Lawbot Executive Lawfice',
        'party': True,
        'max_party_size': 8,
    },
    'boss-ol-2': {
        'state': 'Fighting the laser Cogs!',
        'large_image_key': 'lbhq_clo_battle',
        'large_image_hover': 'Lawbot Executive Lawfice',
        'party': True,
        'max_party_size': 8,
    },
    'boss-ol-3': {
        'state': 'Fighting the Litigation Team!',
        'large_image_key': 'lbhq_clo_battle',
        'large_image_hover': 'Lawbot Executive Lawfice',
        'party': True,
        'max_party_size': 8,
    },
    'boss-ol-4': {
        'state': 'Gathering evidence!',
        'large_image_key': 'lbhq_clo_battle',
        'large_image_hover': 'Lawbot Executive Lawfice',
        'party': True,
        'max_party_size': 8,
    },
    'boss-ol-5': {
        'state': 'Trapping the OCLO!',
        'large_image_key': 'lbhq_clo_battle',
        'large_image_hover': 'Lawbot Executive Lawfice',
        'party': True,
        'max_party_size': 8,
    },

    # Acorn Acres
    'treek': {
        'state': 'Peeling the bark!',
        'large_image_hover': 'Fighting the %s' % suitName('treek') + ' on %s!',
        'large_image_key': 'merc_treek',
    },
    'chainsaw': {
        'state': 'Revving it up!',
        'large_image_hover': 'Fighting the %s!' % suitName('chainsaw'),
        'large_image_key': 'instance_chainsaw'
    },

    # Bossbot HQ
    'bb-golf': {
        'state': 'Infiltrating the Bossbot %s',
        'large_image_key': 'bbhq_cgc',
    },
    'boss-c-1': {
        'state': 'Fighting the CEO!',
        'large_image_key': 'bbhq_ceo_battle',
        'large_image_hover': 'Bossbot HQ Clubhouse',
        'party': True,
        'max_party_size': 8,
    },
    'boss-c-2': {
        'state': 'Fighting the waiters!',
        'large_image_key': 'bbhq_ceo_battle',
        'large_image_hover': 'Bossbot HQ Clubhouse',
        'party': True,
        'max_party_size': 8,
    },
    'boss-c-3': {
        'state': 'Serving at the banquet!',
        'large_image_key': 'bbhq_ceo_battle',
        'large_image_hover': 'Bossbot HQ Clubhouse',
        'party': True,
        'max_party_size': 8,
    },
    'boss-c-4': {
        'state': 'Fighting the Cogs!',
        'large_image_key': 'bbhq_ceo_battle',
        'large_image_hover': 'Bossbot HQ Clubhouse',
        'party': True,
        'max_party_size': 8,
    },
    'boss-c-5-s': {
        'state': 'Seltzering the CEO!',
        'large_image_key': 'bbhq_ceo_battle',
        'large_image_hover': 'Bossbot HQ Clubhouse',
        'party': True,
        'max_party_size': 8,
    },
    'boss-c-5-g': {
        'state': 'Golfing in the CEO!',
        'large_image_key': 'bbhq_ceo_battle',
        'large_image_hover': 'Bossbot HQ Clubhouse',
        'party': True,
        'max_party_size': 8,
    },
    'boss-c-5': {
        'state': 'Running from the CEO!',
        'large_image_key': 'bbhq_ceo_battle',
        'large_image_hover': 'Bossbot HQ Clubhouse',
        'party': True,
        'max_party_size': 8,
    },
    'directors': {
        'state': 'Infiltrating the CEO\'s Office!',
        'large_image_hover': 'Fighting the %s!' % 'Directors',
        'large_image_key': 'instance_bbhq',
    },

    # Drowsy Dreamland
    'fbed': {
        'state': 'Trying not... to... zzz...',
        'large_image_hover': 'Fighting the %s' % suitName('fbed') + ' on %s!',
        'large_image_key': 'merc_fbed',
    },
    'psetter': {
        'state': 'Setting the Pace!',
        'large_image_hover': 'Fighting the %s!' % suitName('psetter'),
        'large_image_key': 'instance_psetter'
    },
    'psetter_overclocked': {
        'state': 'Trying to keep up!',
        'large_image_hover': 'Fighting the %s!' % suitName('psetter'),
        'large_image_key': 'instance_psetter'
    },

    ##  Events ##

    'counterclaim': {
        'state': ['Fighting the spooky Skelecogs!', 'Fighting %s!' % suitName('count')],
        'large_image_key': ['instance_erfit'],
    },
    'counterfit': {
        'state': ['Inside the Tower of Power!', 'Getting swole!', 'Skipping leg day!'],
        'large_image_key': ['instance_erfit'],
    },
    'erfit': {
        'state': ['Inside the Tower of Power!', 'Getting swole!', 'Skipping leg day!'],
        'large_image_hover': 'Fighting Count Erfit!',
        'large_image_key': 'instance_erfit'
    },
    'videographer': {
        'state': ['Stealing the Spotlight!', 'Cutting the Production Short!', 'Surviving the Final Cut!'],
        'large_image_hover': 'Fighting the Videographer!',
        'large_image_key': 'instance_videog'
    },
    'hroller': {
        'state': 'Winning it big!',
        'large_image_hover': 'Fighting the %s!' % suitName('hroller'),
        'large_image_key': 'instance_hroller'
    },

    # Ottoman
    'boss-coo': {
        'state': 'Getting bored...',
        'large_image_key': 'bored_ottoman',
        'party': True,
        'max_party_size': 8,
    },

}
