"""
The GUI panel manager for the Edit Tab.

"""
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectEntry import DirectEntry
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel


"""
Tools
"""


class MoveTool(DirectFrame):

    frameColor = (0.8, 0.8, 0.8, 0.3)

    def __init__(self, mgr, **kw):
        optiondefs = (
            ('frameColor', self.frameColor, None),
            ('frameSize', (-0.5, 0.5, -0.3, 0.3), None),
            ('pos', (0, 0, 0), None),
        )
        self.defineoptions(kw, optiondefs)
        DirectFrame.__init__(self, aspect2d, **kw)
        self.initialiseoptions(MoveTool)

        # Init some class variables
        self.startTime = None
        self.endTime = None
        self.moveAmount = 0
        self.mgr = mgr  # type: CSEditorManager

        # Title
        DirectLabel(
            parent=self,
            text="Move Tool", text_scale=0.06,
            pos=(0, 0, self['frameSize'][3] - 0.05),
        )

        # Entries + Labels
        # Start Time
        self.entryStartTime = DirectEntry(
            parent=self, command=self.setStartTime,
            initialText='N/A', width=4, numLines=1,
            scale=.05, pos=(self['frameSize'][0] + 0.075, 0, self['frameSize'][3] - 0.2), frameColor=self.frameColor,
        )
        DirectLabel(
            parent=self,
            text="Start Time", text_scale=0.06,
            pos=(self.entryStartTime.getX() + 0.1, 0, self.entryStartTime.getZ() + 0.05),
        )
        # Match Button (matches start time with current time)
        DirectButton(
            parent=self, command=self.matchStartTime,
            text="Match", text_scale=0.05, text_pos=(0, -0.01),
            pos=(self.entryStartTime.getX() + 0.1, 0, self.entryStartTime.getZ() - 0.05),
            frameSize=(-0.08, 0.09, -0.03, 0.03),
            frameColor=(0.8, 0.8, 0.8, 1.0),
        )

        # End Time
        self.entryEndTime = DirectEntry(
            parent=self, command=self.setEndTime,
            initialText='N/A', width=4, numLines=1,
            scale=.05, pos=(self['frameSize'][1] - 0.275, 0, self['frameSize'][3] - 0.2), frameColor=self.frameColor,
        )
        DirectLabel(
            parent=self,
            text="End Time", text_scale=0.06,
            pos=(self.entryEndTime.getX() + 0.1, 0, self.entryEndTime.getZ() + 0.05),
        )
        # Match Button (matches end time with current time)
        DirectButton(
            parent=self, command=self.matchEndTime,
            text="Match", text_scale=0.05, text_pos=(0, -0.01),
            pos=(self.entryEndTime.getX() + 0.1, 0, self.entryEndTime.getZ() - 0.05),
            frameSize=(-0.08, 0.09, -0.03, 0.03),
            frameColor=(0.8, 0.8, 0.8, 1.0),
        )

        # Move Amount
        self.entryMoveAmount = DirectEntry(
            parent=self, command=self.setMoveAmount,
            initialText='N/A', width=4, numLines=1,
            scale=.05, pos=(-0.1, 0, self['frameSize'][2] + 0.15), frameColor=self.frameColor,
        )
        DirectLabel(
            parent=self,
            text="Move Amount", text_scale=0.06,
            pos=(self.entryMoveAmount.getX() + 0.1, 0, self.entryMoveAmount.getZ() + 0.05),
        )

        # Submit button
        DirectButton(
            parent=self, command=self.submit,
            text="Move Events", text_scale=0.06, text_pos=(0, -0.02),
            pos=(0, 0, self['frameSize'][2] + 0.05), frameSize=(-0.18, 0.18, -0.04, 0.04),
            frameColor=(0.863, 0.773, 0.616, 1.0),
        )

        # Exit button
        DirectButton(
            parent=self, command=self.hide,
            text="X", text_scale=0.06, text_pos=(0, -0.02),
            pos=(self['frameSize'][1] - 0.05, 0, self['frameSize'][3] - 0.05), frameSize=(-0.04, 0.04, -0.04, 0.04),
            frameColor=(0.8, 0.8, 0.8, 1.0),
        )

    def setInitialValues(self):
        self.startTime = self.mgr.currentTime
        self.entryStartTime.enterText(str(self.startTime))

        self.endTime = self.mgr.trackLength
        self.entryEndTime.enterText(str(self.endTime))

        #self.moveAmount = 0
        self.entryMoveAmount.enterText(str(self.moveAmount))

    def matchStartTime(self):
        self.entryStartTime.enterText(str(self.mgr.currentTime))

    def matchEndTime(self):
        self.entryEndTime.enterText(str(self.mgr.currentTime))

    def setStartTime(self, value):
        try:
            float(value)
        except TypeError:
            return
        self.startTime = float(value)

    def setEndTime(self, value):
        try:
            float(value)
        except TypeError:
            return
        self.endTime = float(value)

    def setMoveAmount(self, value):
        try:
            float(value)
        except TypeError:
            return
        self.moveAmount = float(value)

    def submit(self):
        self.setStartTime(self.entryStartTime.get(plain=True))
        self.setEndTime(self.entryEndTime.get(plain=True))
        self.setMoveAmount(self.entryMoveAmount.get(plain=True))
        messenger.send('requestMoveEventsInRange', [self.moveAmount, self.startTime, self.endTime])
        self.hide()

    def show(self):
        super().show()
        self.setInitialValues()


"""
Dropdown Button
"""


class CSPanelEdit(DirectFrame):

    toolDict = {
        'Move': MoveTool,
    }
    buttonFrameSize = (-0.10, 0.10, -0.04, 0.04)
    distanceBetweenButtons = abs(buttonFrameSize[2]) + abs(buttonFrameSize[3])
    toolButtons = []

    def __init__(self, mgr, **kw):
        optiondefs = (
            ('pos', (0.60, 0, -0.06), None),
        )
        self.defineoptions(kw, optiondefs)
        DirectFrame.__init__(self, base.a2dTopLeft, **kw)
        self.initialiseoptions(CSPanelEdit)

        # set properties of panel
        self.mgr = mgr  # type: CSEditorManager

        # Edit Button
        DirectButton(
            parent=self, command=self.toggleToolButtons,
            text="Edit", text_scale=0.06, text_pos=(0, -0.02),
            pos=(0, 0, 0), frameSize=self.buttonFrameSize,
            frameColor=(0.863, 0.773, 0.616, 1.0),
        )

        for toolName in self.toolDict:
            # Init tool window
            tool = self.toolDict[toolName](mgr)
            tool.hide()

            # Dropdown button to show tool
            zPos = -((len(self.toolButtons) + 1) * self.distanceBetweenButtons)
            self.toolButtons.append(
                DirectButton(
                    parent=self, command=lambda: self.openTool(tool),
                    text=toolName, text_scale=0.06, text_pos=(0, -0.02),
                    pos=(0, 0, zPos), frameSize=self.buttonFrameSize,
                    frameColor=(0.663, 0.573, 0.416, 1.0),
                )
            )
        self.toggleToolButtons()

    def toggleToolButtons(self):
        for button in self.toolButtons:
            if button.isHidden():
                button.show()
            else:
                button.hide()

    def openTool(self, tool):
        tool.show()
        self.toggleToolButtons()
