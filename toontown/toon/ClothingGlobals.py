from strenum import StrEnum

BaseTexturePath = "cosmetics/clothing/maps/"
BaseTextureExtension = ".png"


class ClothingTopType(StrEnum):
    """
    The type of "top" this clothing item is
    Will determine which model/mesh to load
    """
    Shirt = "shirt"


class ClothingBottomType(StrEnum):
    """
    The type of "bottom" this clothing item is
    Will determine which model/mesh to load
    """
    Shorts = "shorts"
    Skirt = "skirt"
