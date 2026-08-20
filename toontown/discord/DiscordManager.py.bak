from toontown.discord import DiscordConnector


class DiscordManager(object):
    def __init__(self):
        self.connector = DiscordConnector.DiscordConnector()
        self.activity = DiscordConnector.Activity()

    def toonLoggedOut(self):
        self.activity.clearRP()
        self.send()

    def setToonName(self, name):
        self.activity.toonName = name
        self.send()

    def setZone(self, zoneId):
        if self.activity.setZone(zoneId):
            self.send()

    def setHp(self, hp):
        self.activity.currentHp = hp
        self.send()

    def setMaxHp(self, hp):
        self.activity.maxHp = hp
        self.send()

    def setDistrict(self, name):
        self.activity.district = name
        self.send()

    def updateParty(self, current, started):
        self.activity.partySize = [current, started]
        self.send()

    def start(self):
        # Rich Presence is enabled by default for Altis.  The previous version
        # referenced a 'settings' global that is not imported in this module,
        # which prevented startup from ever reaching the IPC connection.
        if self.connector.connect():
            self.send()

    def stop(self):
        self.connector.disconnect()

    def send(self):
        self.connector.update_activity(self.activity.send())

    def applyPreset(self, preset, imageIndex=0, fillin=None, hover_fillin=None):
        self.activity.applyPreset(preset, imageIndex=imageIndex,
                                   fillin=fillin, hover_fillin=hover_fillin)
        self.send()

    def handleSettingsToggle(self, value):
        if value:
            self.start()
        else:
            self.stop()
