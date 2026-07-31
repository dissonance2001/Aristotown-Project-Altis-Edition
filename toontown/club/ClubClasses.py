class ClubIcon:
    def __init__(self, iconId=0, backgroundId=0, clubCol=0, bgCol=0):
        self.iconId = int(iconId or 0)
        self.backgroundId = int(backgroundId or 0)
        self.clubCol = int(clubCol or 0)
        self.bgCol = int(bgCol or 0)

    def toDict(self):
        return {
            'iconId': self.iconId,
            'backgroundId': self.backgroundId,
            'themeId': self.clubCol,
            'backgroundColorId': self.bgCol,
        }
