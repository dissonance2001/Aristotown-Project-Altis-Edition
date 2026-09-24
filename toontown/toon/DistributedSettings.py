from toontown.toon.DistributedSettingsBase import DistributedSettingsBase


class DistributedSettings(DistributedSettingsBase):
    """
    The client-side view of an av's settings.
    """

    def initialize(self):
        # Update our local setting values.
        for index, value in enumerate(self.settings):
            settingKey = self.settingKeys[index]
            settings[settingKey] = value

        # Then, perform our update settings call.
        base.updateSettings()

    def changeSetting(self, setting: str, value: float):
        # This method ends up getting called twice:
        # 1) When the client updates their settings, then tells the server about it.
        # 2) The server then calls it again, when storing the updated value in db.
        super().changeSetting(setting=setting, value=value)

        # Do some client-sided changes as well.
        settings[setting] = value
        messenger.send(f'option-update-{setting}')
        base.updateSettings()
