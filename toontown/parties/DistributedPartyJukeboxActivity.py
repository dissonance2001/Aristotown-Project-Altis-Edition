from __future__ import absolute_import
from toontown.parties.DistributedPartyJukeboxActivityBase import DistributedPartyJukeboxActivityBase
from toontown.parties import PartyGlobals

class DistributedPartyJukeboxActivity(DistributedPartyJukeboxActivityBase):
    notify = directNotify.newCategory('DistributedPartyJukeboxActivity')

    def __init__(self, cr):
        DistributedPartyJukeboxActivityBase.__init__(self, cr, PartyGlobals.ActivityIds.PartyJukebox, PartyGlobals.PhaseToMusicData)
