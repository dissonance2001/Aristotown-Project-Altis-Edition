from enum import Enum, auto


class HoverFrameTypes(Enum):
    InventoryItem = auto()
    ToonTip = auto()
    Scavenge = auto()
    ShopBuyCantAfford = auto()
    ShopBuyFailedReq = auto()
