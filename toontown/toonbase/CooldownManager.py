from time import time


class CooldownResult:
    def __init__(self, outcome, timeLeft):
        self.outcome = outcome
        self.timeLeft = timeLeft


class CooldownManager():
    """
    Quick and easy way to handle cooldowns.
    Class Inits with the cooldown duration
    Then call .check(avid) and this class handles the rest.
    """
    def __init__(self, duration):
        self.updateDuration(duration)
        self.cooldownDict = {}

    def updateDuration(self, duration):
        if not isinstance(duration, int):
            raise Exception('Error: Duration passed to CooldownManager is not of type int')
        self.duration = duration

    def check(self, avid):
        """
        Checks to see if the cooldown period has finished or not.

        You can call .outcome to get a Bool to see if the avid is cooled down
        True - User is cool
        False - User is still cooling down
        Also you can call .timeLeft to get the amount of time left before they are cool

        :param int avid: ID of the toon to be checked. (This can be anything but we mainly use this for toons)
        :returns: Instance of CooldownResult
        """

        # First check to see if they're in the system yet
        if avid not in self.cooldownDict:
            self.cooldownDict[avid] = time() + self.duration
            return CooldownResult(True, 0)

        # So they're already in the system
        if time() >= self.cooldownDict[avid]:  # User has cooled down
            self.cooldownDict[avid] = time() + self.duration
            return CooldownResult(True, 0)

        # Looks like they're not quite cool enough yet
        return CooldownResult(False, round(self.cooldownDict[avid] - time()))
