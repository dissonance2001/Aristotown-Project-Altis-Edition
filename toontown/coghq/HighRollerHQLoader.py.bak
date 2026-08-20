from direct.fsm import State, StateData, ClassicFSM
from direct.directnotify import DirectNotifyGlobal
from toontown.coghq import CogHQLoader
from toontown.coghq import HighRollerBossBattle


class HighRollerHQLoader(CogHQLoader.CogHQLoader):
    notify = DirectNotifyGlobal.directNotify.newCategory(
        'HighRollerHQLoader')

    def __init__(self, hood, parentFSMState, doneEvent):
        StateData.StateData.__init__(self, doneEvent)
        self.hood = hood
        self.parentFSMState = parentFSMState
        self.placeDoneEvent = 'highRollerLoaderPlaceDone'
        self.townBattleDoneEvent = 'town-battle-done'
        self.fsm = ClassicFSM.ClassicFSM(
            'HighRollerHQLoader',
            [State.State('start', None, None,
                         ['quietZone', 'highRollerBossBattle']),
             State.State('highRollerBossBattle',
                         self.enterHighRollerBossBattle,
                         self.exitHighRollerBossBattle,
                         ['quietZone']),
             State.State('quietZone', self.enterQuietZone,
                         self.exitQuietZone, ['highRollerBossBattle']),
             State.State('final', None, None, ['start'])],
            'start', 'final')
        self.musicFile = ('phase_13/audio/bgm/april_toons/highroller/'
                          'cc_s_bgm_ara_hroller_int_battle.ogg')
        self.lobbyMusicFile = self.musicFile


    def isInThisHq(self, status):
        # This loader is hosted inside Minnie's Melodyland for the fast sigil
        # route.  A return to the MML playground is the same hood but a
        # different loader, so it must be handed back to MMHood rather than
        # being treated as another internal High Roller place.
        return (status.get('loader') == 'highRollerLoader' and
                status.get('hoodId') == self.hood.hoodId)

    def loadPlaceGeom(self, zoneId):
        # The distributed High Roller boss owns the arena model and collision.
        # A hood loader must not add Cashbot HQ or CFO geometry here.
        self.geom = None

    def unloadPlaceGeom(self):
        if getattr(self, 'geom', None):
            self.geom.removeNode()
        self.geom = None

    def enterHighRollerBossBattle(self, requestStatus):
        self.placeClass = HighRollerBossBattle.HighRollerBossBattle
        self.enterPlace(requestStatus)
        # Go directly from the sigil transition into the boss introduction.
        # Do not display a separate hood/location title over the opening shot.
        base.cr.forbidCheesyEffects(1)

    def exitHighRollerBossBattle(self):
        taskMgr.remove('titleText')
        self.hood.hideTitleText()
        self.exitPlace()
        self.placeClass = None
        base.cr.forbidCheesyEffects(0)
