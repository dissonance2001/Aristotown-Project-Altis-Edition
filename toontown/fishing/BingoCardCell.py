from direct.fsm import FSM
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from toontown.fishing import BingoGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class BingoCardCell(DirectButton, FSM.FSM):
    """
    BingoCardCell(DirectButton, FSM)

    Provide an atomic cell button that is used to visually represent the Card pieces for the player.

    Create a BingoCard Cell that houses all of the relevant information about that particular BINGO
    spot of the card.
    """

    def __init__(self, cellId, fish, model, color, parent, **kw):
        """
        This method provides initial construction of the Cell.
        It initializes the DirectButton and FSM base classes from which it is derived.
        In addition, it manually sets itself to the 'Off' State so that the enterOff method is called.

        :param cellId: Id Number of the Cell
        :param fish: The type of fish it represents with the logo.
        :param model:
        :param color:
        :param parent: The card that to which it belongs.
        :param kw: OptionDefs for the DirectButton.
        """
        self.model = model
        self.color = color
        buttonToUse = self.model.find('**/mickeyButton')

        # Option Definitions for the Cell. This should override any
        # FishPanel specific optiondefs.
        optiondefs = (
            ('parent', parent, None),
            ('relief', None, None),
            ('state', DGG.DISABLED, None),
            ('image', buttonToUse, None),
            ('image_color', self.color, None),
            ('image_hpr', (0, 90, 0), None),
            ('image_pos', (0, 0, 0), None),
            ('pressEffect', False, None)
        )

        self.defineoptions(kw, optiondefs)
        DirectButton.__init__(self, parent)
        FSM.FSM.__init__(self, 'BingoCardCell')
        self.initialiseoptions(BingoCardCell)

        # FishPanel Initialization should be completed by this point.
        # Finalize the remaining BingoCardCell initialization.
        self.fish = fish
        # Assign the cell Index of the card
        self.cellId = cellId
        self.request('Off')

    def destroy(self):
        """
        This method cleans up the Cell so that there are no persisting memory leaks.
        """
        DirectButton.destroy(self)

    def setImageTo(self, button):
        """
        This method sets the image field appropriately
        """
        button.setHpr(0, 90, 0)
        button.setPos(0, 0, 0)
        button.setScale(BingoGlobals.CellImageScale)
        button.setColor(self.color[0], self.color[1], self.color[2], self.color[3])
        self['image'] = button
        self.setImage()

    def getButtonName(self):
        """
        This method gets the name of the button to use for this fish

        :return: BingoGlobals.FishButtonDict[genus][0]
        """
        genus = self.getFishGenus()
        return BingoGlobals.FishButtonDict[genus][0]

    def generateLogo(self):
        """
        This method generates the appropriate type of logo based on its type of Cell, Free or Fish Logo.
        """
        buttonName = self.getButtonName()
        buttonToUse = self.model.find('**/' + buttonName)
        self.setImageTo(buttonToUse)

    def generateMarkedLogo(self):
        """
        This method generates the actual Marked Logo.
        At this point the free logo is cancel button logo so this SHOULD be CHANGED!!!
        """
        self.setImageTo(self.model.find('**/mickeyButton'))

    def setFish(self, fish):
        """
        This method sets the type of Fish that this cell represents.

        :param fish: The fish the cell instance represents.
        """
        if self.fish:
            del self.fish
        self.fish = fish

    def getFish(self):
        """
        This method returns the type of Fish that the cell instance represents.

        :return: The fish the cell instance represents.
        """
        return self.fish

    def getFishGenus(self):
        """
        This method returns the type of Genus of the Fish that the cell instance represents.

        :return: The fish genus the cell instance represents. (-1 for middle/free spot)
        """
        if self.fish == 'Free':
            return -1
        return self.fish.getGenus()

    def getFishSpecies(self):
        """
        This method returns the type of Species of the Fish that the cell instance represents.

        :return: species - The fish species the cell instance represents
        """
        return self.fish.getSpecies()

    def enable(self, callback = None):
        """
        This method requests a state transition to enable the cell for gameplay use.

        :param callback: the callback routine to be called when the cell is pressed. (None)
        """
        self.request('On', callback)

    def disable(self):
        """
        This method requests a state transition to disable the cell for gameplay use.
        It also hides the fish logo if it exists.
        """
        self.request('Off')
        if not self.fish == 'Free':
            self.generateMarkedLogo()

    #################################################################
    # Finite State Machine Methods
    #################################################################
    #  - FSM States:
    #     - Off           Transitions To On
    #     - On            Transitions To Off
    #################################################################

    def enterOff(self):
        """
        This method disables the Cell Button and removes the callback method reference.
        """
        self['state'] = DGG.DISABLED
        self['command'] = None

    def filterOff(self, request, args):
        """
        This method filters out the state transitions so that it only allows valid transition attempts.
        It allows Off to transition to Off or On.

        :param request: The Transition State
        :param args: additional arguments
        """
        if request == 'On':
            return (request, args)
        elif request == 'Off':
            return request
        else:
            self.notify.debug('filterOff: Invalid State Transition from Off to %s' % request)

    def enterOn(self, args):
        """
        This method enables the Cell Button and adds a callback method reference.

        :param args: additional arguments
        """
        # Enable DirectButton Capabilities.
        self['state'] = DGG.NORMAL
        if args[0]:
            self['command'] = Func(args[0], self.cellId).start

    def filterOn(self, request, args):
        """
        This method filters out the state transitions so that it only allows valid transition attempts.
        It allows On to transition to Off only.

        :param request: The Transition State
        :param args: additional arguments
        """
        if request == 'Off':
            return request
        else:
            self.notify.debug('filterOn: Invalid State Transition from Off to %s' % request)
