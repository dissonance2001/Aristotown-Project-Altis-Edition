from otp.level import EntityCreator
from toontown.coghq import FactoryLevelMgr
from toontown.coghq import PlatformEntity
from toontown.coghq import ConveyorBelt
from toontown.coghq import GearEntity
from toontown.coghq import PaintMixer
from toontown.coghq import GoonClipPlane
from toontown.coghq import MintProduct
from toontown.coghq import MintProductPallet
from toontown.coghq import MintShelf
from toontown.coghq.boardbothq import BoardOfficeProduct
from toontown.coghq.boardbothq import BoardOfficeProductPallet
from toontown.coghq.boardbothq import BoardOfficeShelf
from toontown.coghq import PathMasterEntity
from toontown.coghq import RenderingEntity

class FactoryEntityCreator(EntityCreator.EntityCreator):

    def __init__(self, level):
        EntityCreator.EntityCreator.__init__(self, level)
        nothing = EntityCreator.nothing
        unimplemented = EntityCreator.unimplemented
        self.privRegisterTypes({'activeCell': unimplemented,
         'crusherCell': unimplemented,
         'battleBlocker': unimplemented,
         'beanBarrel': unimplemented,
         'button': unimplemented,
         'conveyorBelt': ConveyorBelt.ConveyorBelt,
         'crate': unimplemented,
         'door': unimplemented,
         'directionalCell': unimplemented,
         'gagBarrel': unimplemented,
         'gear': GearEntity.GearEntity,
         'goon': unimplemented,
         'gridGoon': unimplemented,
         'golfGreenGame': unimplemented,
         'goonClipPlane': GoonClipPlane.GoonClipPlane,
         'grid': unimplemented,
         'healBarrel': unimplemented,
         'levelMgr': FactoryLevelMgr.FactoryLevelMgr,
         'lift': unimplemented,
         'mintProduct': MintProduct.MintProduct,
         'mintProductPallet': MintProductPallet.MintProductPallet,
         'mintShelf': MintShelf.MintShelf,
         'boardOfficeProduct': BoardOfficeProduct.BoardOfficeProduct,
         'boardOfficeProductPallet': BoardOfficeProductPallet.BoardOfficeProductPallet,
         'boardOfficeShelf': BoardOfficeShelf.BoardOfficeShelf,
         'mover': unimplemented,
         'paintMixer': PaintMixer.PaintMixer,
         'pathMaster': PathMasterEntity.PathMasterEntity,
         'rendering': RenderingEntity.RenderingEntity,
         'platform': PlatformEntity.PlatformEntity,
         'sinkingPlatform': unimplemented,
         'stomper': unimplemented,
         'stomperPair': unimplemented,
         'laserField': unimplemented,
         'securityCamera': unimplemented,
         'elevatorMarker': unimplemented,
         'trigger': unimplemented,
         'moleField': unimplemented,
         'maze': unimplemented})
