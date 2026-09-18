from typing import Optional

from toontown.utils.EnhancedIntEnum import EnhancedIntEnum


class Process(EnhancedIntEnum):
    Client = 1
    AI = 2
    UberDog = 3
    NoPanda = 4


# Caching the current process, since it doesn't change.
# Don't use this value directly, use the getCurrentProcess function to be consistent.
try:
    _currentProcess = {
        "client": Process.Client,
        "ai": Process.AI,
        "uberdog": Process.UberDog
    }.get(process)
except NameError:
    _currentProcess = Process.NoPanda


def getCurrentProcess() -> Optional[Process]:
    """
    Returns what process we're running on.

    :return: The process we're running on or None if the process is unknown.
    """
    return _currentProcess
