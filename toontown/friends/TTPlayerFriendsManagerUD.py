from __future__ import absolute_import
from direct.directnotify import DirectNotifyGlobal
from otp.friends.PlayerFriendsManagerUD import PlayerFriendsManagerUD

class TTPlayerFriendsManagerUD(PlayerFriendsManagerUD):
    notify = DirectNotifyGlobal.directNotify.newCategory("TTPlayerFriendsManagerUD")

