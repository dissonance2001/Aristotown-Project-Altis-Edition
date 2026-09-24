"""
NPCForceAcknowledge (NPCFA) module: contains the NPCForceAcknowledge Class

Stops & prevents the Toon from whatever they were about to do and prompts them with a message box related to an NPC.
"""


class NPCForceAcknowledge:
    """
    NPCForceAcknowledge (NPCFA)

    Stops & prevents the Toon from whatever they were about to do and prompts them with a message box related to an NPC.
    """

    def __init__(self, doneEvent):
        self.doneEvent = doneEvent
        self.dialog = None

    def enter(self):
        doneStatus = {}
        imgScale = 0.48
        doneStatus['mode'] = 'complete'
        messenger.send(self.doneEvent, [doneStatus])

    def exit(self):
        if self.dialog:
            self.dialog.cleanup()
            self.dialog = None

    def handleOk(self, value):
        messenger.send(self.doneEvent, [self.doneStatus])
