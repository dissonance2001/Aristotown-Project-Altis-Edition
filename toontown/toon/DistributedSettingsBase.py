from toontown.settings.ToontownSettings import DefaultSettings, DistributedSettingKeys
from toontown.utils.AstronStruct import AstronStruct


class DistributedSettingsBase(AstronStruct):
    """
    The base class for distributed player setting definitions.
    """

    # A list of all setting strings to be considered 'distributed'.
    settingKeys = DistributedSettingKeys

    def __init__(self):
        self.settings = [DefaultSettings.get(key) for key in self.settingKeys]

    def toStruct(self):
        # We just return our settings list.
        return self.settings

    @classmethod
    def fromStruct(cls, struct):
        # Create our settings.
        distSettings = cls()

        # Iterate over every value of the struct.
        for index, value in enumerate(struct):
            # We set the value directly to avoid unexpected behavior by
            # changing the values independently, such as the client
            # calling base.updateSettings() per setting.

            # By doing this, we also natively support extensions
            # do the DistributedSettingKeys list, as they will
            # remain unchanged and become their default value.
            if index >= len(distSettings.settings):
                # Only happens on dev, really (i.e. going back in time)
                break
            distSettings.settings[index] = value

        # We call initialize at the end to handle completion behavior.
        distSettings.initialize()
        return distSettings

    def initialize(self):
        """Can be overriden by subclasses."""
        pass

    def changeSetting(self, setting: str, value: float):
        assert setting in self.settingKeys, "Bad setting key passed into DistributedSettings!"
        settingIndex = self.settingKeys.index(setting)
        self.settings[settingIndex] = value

    def getSetting(self, setting: str):
        assert setting in self.settingKeys, "Bad setting key passed into DistributedSettings!"
        settingIndex = self.settingKeys.index(setting)
        return self.settings[settingIndex]
