import collections
import time


class RateLimiter:
    def __init__(self, max_hits, period, block_actions: bool = False):
        self.max_hits = max_hits
        self.period = period
        self.block_actions = block_actions

        self.hits = collections.deque()

    def blocked(self):
        time_left = 0
        current_time = time.time()

        # clear out the hits that are expired.
        while self.hits and (current_time - self.hits[0]) >= self.period:
            self.hits.popleft()

        # only do this if we know the deque is longer than the max_hits, an efficiency
        if len(self.hits) >= self.max_hits:
            time_left = max(self.hits[0] - current_time + self.period, 0)

        # append current time to the deque, but only if not blocked
        if not time_left or self.block_actions:
            self.hits.append(current_time)

        return time_left

    def tryRequest(self):
        rate_limit = self.blocked()
        return rate_limit and rate_limit <= self.period


class IdRateLimiter:
    """
    A RateLimiter container class that has an interface
    for checking if an ID is being rate limited.
    """

    def __init__(self, max_hits, period, block_actions: bool = False):
        self.max_hits = max_hits
        self.period = period
        self.block_actions = block_actions
        self.ratelimiters = {}

    def userBlocked(self, avId):
        if avId not in self.ratelimiters:
            self.ratelimiters[avId] = RateLimiter(max_hits=self.max_hits, period=self.period, block_actions=self.block_actions)
        return self.ratelimiters[avId].tryRequest()
