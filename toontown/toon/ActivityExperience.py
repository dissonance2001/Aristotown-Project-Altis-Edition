class ActivityExperience:
    def getLevelMaxExp(self, level):
        level = int(level)
        return 15 * (level + 1) * (level + 6)

    def getTotalExp(self, level):
        level = int(level)
        return sum(self.getLevelMaxExp(currentLevel) for currentLevel in range(level))
