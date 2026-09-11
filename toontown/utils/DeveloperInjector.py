import os
import traceback
from typing import TYPE_CHECKING
from toontown.utils.DirectNotifyCategory import getNotify
if TYPE_CHECKING:
    from toontown.utils.BuiltinHelper import base


tempFileName = "injectorFile.py"
notify = getNotify('Dev Injector')


def startInjector():
    """Starts the developer injector"""
    base.accept('f10', handleInjectionRequest)
    if not os.path.isfile(tempFileName):
        notify.info("Creating injector file.")
        with open(tempFileName, 'w') as tempFile:
            tempFile.write("from toontown.utils.BuiltinHelper import *\n\n")


def handleInjectionRequest():
    """Listens for the F10 key to be pressed and injects the code."""
    notify.info("Injecting!")
    with open(tempFileName, 'r') as tempFile:
        try:
            exec(tempFile.read(), globals())
        except Exception:
            traceback.print_exc()
