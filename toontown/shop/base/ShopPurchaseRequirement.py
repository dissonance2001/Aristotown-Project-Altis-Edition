from typing import Union, Tuple


class ShopPurchaseRequirement:
    """
    An object that allows for certain items to have requirements
    for the player to be able to purchase them.
    """

    def __repr__(self):
        return f"ShopPurchaseRequirement({self.getRequirementText()})"

    def meetsPurchaseRequirement(self, av) -> bool:
        """Does the av meet the requirements to be able to purchase this item?"""
        return True

    def getRequirementText(self) -> str:
        return "Requires something"


# Make typehint for ShopPurchaseRequirement.
# On built, these types will not exist, so we will
# handle the exception with a simplification.
try:
    PurchaseRequirements = Union[ShopPurchaseRequirement, Tuple[ShopPurchaseRequirement]]
except NameError:
    PurchaseRequirements = ShopPurchaseRequirement
