from abc import abstractmethod

from toontown.modifiers.ModifierEnums import ModifierType
from toontown.utils.AstronStruct import AstronStruct


class Modifier(AstronStruct):
    """
    The Modifier base class holds data for how a modifier is to be employed.
    """

    def __init__(self, arguments=None):
        if arguments is None:
            arguments = []
        self.arguments = arguments

    @abstractmethod
    def modify(self, value, do, context=None):
        """
        Modifies a value into any other.
        """
        raise NotImplementedError

    """
    Modifier state changing
    """

    def onModifierPreAdd(self, do):
        """
        Called whenever the modifier is added. (Client side)
        This method is called BEFORE the Modifier is applied.
        :type do: ModifiableDO
        """
        return

    def onModifierPostAdd(self, do):
        """
        Called whenever the modifier is added. (Client side)
        This method is called AFTER the Modifier is applied.
        :type do: ModifiableDO
        """
        return

    def onModifierPreRemove(self, do):
        """
        Called whenever the modifier is removed. (Client side)
        This method is called BEFORE the Modifier is applied.
        :type do: ModifiableDO
        """
        return

    def onModifierPostRemove(self, do):
        """
        Called whenever the modifier is removed. (Client side)
        This method is called AFTER the Modifier is applied.
        :type do: ModifiableDO
        """
        return

    def onModifierPreAddAI(self, do):
        """
        Called whenever the modifier is added. (AI side)
        This method is called BEFORE the Modifier is applied.
        :type do: ModifiableDOAI
        """
        return

    def onModifierPostAddAI(self, do):
        """
        Called whenever the modifier is added. (AI side)
        This method is called AFTER the Modifier is applied.
        :type do: ModifiableDOAI
        """
        return

    def onModifierPreRemoveAI(self, do):
        """
        Called whenever the modifier is removed. (AI side)
        This method is called BEFORE the Modifier is applied.
        :type do: ModifiableDOAI
        """
        return

    def onModifierPostRemoveAI(self, do):
        """
        Called whenever the modifier is removed. (AI side)
        This method is called AFTER the Modifier is applied.
        :type do: ModifiableDOAI
        """
        return

    """
    Astron Struct
    """

    def toStruct(self):
        return [int(self.getModifierType())] + self.arguments

    @classmethod
    def fromStruct(cls, struct):
        # Get the arguments.
        modifierType = struct[0]
        arguments = list(struct[1:])

        # Set up the class.
        from toontown.modifiers.ModifierClasses import ModifierClasses
        modifierClass = ModifierClasses.get(ModifierType(modifierType))

        # Create it. If there's a crash here, the class init needs to have default arguments.
        modifier = modifierClass()

        # Populate and send it.
        modifier.setArguments(arguments)
        return modifier

    def setArguments(self, arguments):
        self.arguments = arguments

    """
    Getters
    """

    def getModifierType(self):
        from toontown.modifiers.ModifierClasses import ModifierClasses
        for modifierType, modifierCls in ModifierClasses.items():
            if type(self) is modifierCls:
                return modifierType
        raise KeyError("Modifier was not defined in ModifierClasses.")