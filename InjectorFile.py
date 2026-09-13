import traceback
from toontown.minigame.Purchase import Purchase

_original_exitReward = Purchase.exitReward

def _patched_exitReward(self):
    try:
        _original_exitReward(self)
    except Exception as e:
        print("=== exitReward() FAILED ===")
        traceback.print_exc()
        # force-hide the reward widgets anyway so the bug doesn't compound
        try:
            for counter in self.counters:
                counter.reparentTo(hidden)
        except Exception:
            pass
        try:
            for total in self.totalCounters:
                total.reparentTo(hidden)
        except Exception:
            pass

Purchase.exitReward = _patched_exitReward
print("Purchase.exitReward patched")