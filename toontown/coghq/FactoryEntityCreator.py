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
        notLocal = EntityCreator.notLocal
        self.privRegisterTypes({'activeCell': notLocal,
         'crusherCell': notLocal,
         'battleBlocker': notLocal,
         'beanBarrel': notLocal,
         'button': notLocal,
         'conveyorBelt': ConveyorBelt.ConveyorBelt,
         'crate': notLocal,
         'door': notLocal,
         'directionalCell': notLocal,
         'gagBarrel': notLocal,
         'gear': GearEntity.GearEntity,
         'goon': notLocal,
         'gridGoon': notLocal,
         'golfGreenGame': notLocal,
         'goonClipPlane': GoonClipPlane.GoonClipPlane,
         'grid': notLocal,
         'healBarrel': notLocal,
         'levelMgr': FactoryLevelMgr.FactoryLevelMgr,
         'lift': notLocal,
         'mintProduct': MintProduct.MintProduct,
         'mintProductPallet': MintProductPallet.MintProductPallet,
         'mintShelf': MintShelf.MintShelf,
         'boardOfficeProduct': BoardOfficeProduct.BoardOfficeProduct,
         'boardOfficeProductPallet': BoardOfficeProductPallet.BoardOfficeProductPallet,
         'boardOfficeShelf': BoardOfficeShelf.BoardOfficeShelf,
         'mover': notLocal,
         'paintMixer': PaintMixer.PaintMixer,
         'pathMaster': PathMasterEntity.PathMasterEntity,
         'rendering': RenderingEntity.RenderingEntity,
         'platform': PlatformEntity.PlatformEntity,
         'sinkingPlatform': notLocal,
         'stomper': notLocal,
         'stomperPair': notLocal,
         'laserField': notLocal,
         'securityCamera': notLocal,
         'elevatorMarker': notLocal,
         'trigger': notLocal,
         'moleField': notLocal,
         'maze': notLocal})
