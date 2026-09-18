from __future__ import annotations
from enum import IntEnum
from typing import Optional, Dict

from toontown.inventory.base.InventoryItem import InventoryItem
from toontown.inventory.enums.ItemEnums import MusicDiscItemType
from toontown.inventory.enums.RarityEnums import Rarity
from toontown.inventory.base.ItemDefinition import ItemDefinition
from toontown.utils import ColorHelper
from panda3d.core import NodePath, Texture, Vec4


class MusicDiscItemDefinition(ItemDefinition):
    """
    The definition structure for music discs.
    """

    def __init__(self,
                 musicPath: str,
                 discColor: Vec4 = Vec4(1, 1, 1, 1),
                 texturePath: str | None = None,
                 **kwargs) -> None:
        super().__init__(**kwargs)
        self.musicPath = musicPath
        self.discColor = discColor
        self.texturePath = texturePath

    def getMusicPath(self) -> str:
        return self.musicPath

    def getDiscColor(self) -> Vec4:
        return self.discColor

    def getTexturePath(self) -> str | None:
        return self.texturePath

    def getItemTypeName(self) -> str:
        return "Music Disc"

    def getRewardName(self, item: Optional[InventoryItem] = None) -> str:
        return f'{self.getName()} Music Disc'

    def makeItemModel(self, *extraArgs, item: Optional[InventoryItem] = None) -> NodePath:
        """
        Returns a nodepath that represents this item.
        """
        disk = loader.loadModel('props/general/models/cc_m_gen_prp_vinyl_disk')
        if self.getTexturePath() is not None:
            texture = loader.loadTexture(self.getTexturePath())
            texture.setMinfilter(Texture.FTLinearMipmapLinear)
            texture.setMagfilter(Texture.FTLinear)
            disk.setTexture(texture, 1)

        disk.find('**/disc_outer').setColorScale(self.getDiscColor())
        disk.flattenStrong()

        return disk


# The registry dictionary for music discs.
MusicDiscRegistry: Dict[IntEnum, MusicDiscItemDefinition] = {
    # Prethinker
    MusicDiscItemType.Merc_Prethinker_1: MusicDiscItemDefinition(
        name="Brain Blast!",
        description="Prethinker's phase 1 battle theme.",
        rarity=Rarity.Common,
        musicPath="prethinker_battle",
        discColor=ColorHelper.hexToPCol('8124d0'),
    ),
    MusicDiscItemType.Merc_Prethinker_2: MusicDiscItemDefinition(
        name="Stress Headache!",
        description="Prethinker's phase 2 battle theme.",
        rarity=Rarity.Common,
        musicPath="prethinker_battle_forward",
        discColor=ColorHelper.hexToPCol('8124d0'),
    ),

    # Rainmaker
    MusicDiscItemType.Merc_Rainmaker_1: MusicDiscItemDefinition(
        name="Cold Front",
        description="Rainmaker's normal battle theme.",
        rarity=Rarity.Common,
        musicPath="rainmaker_empty",
        discColor=ColorHelper.hexToPCol('4a369c'),
    ),
    MusicDiscItemType.Merc_Rainmaker_2: MusicDiscItemDefinition(
        name="Dew Point",
        description="Rainmaker's battle theme in fog.",
        rarity=Rarity.Common,
        musicPath="rainmaker_fog",
        discColor=ColorHelper.hexToPCol('4a369c'),
    ),
    MusicDiscItemType.Merc_Rainmaker_3: MusicDiscItemDefinition(
        name="Flash Flood",
        description="Rainmaker's battle theme in heavy rain.",
        rarity=Rarity.Common,
        musicPath="rainmaker_heavy",
        discColor=ColorHelper.hexToPCol('4a369c'),
    ),
    MusicDiscItemType.Merc_Rainmaker_4: MusicDiscItemDefinition(
        name="Eye of the Storm",
        description="Rainmaker's battle theme in monsoon.",
        rarity=Rarity.Common,
        musicPath="rainmaker_monsoon",
        discColor=ColorHelper.hexToPCol('4a369c'),
    ),
    MusicDiscItemType.Merc_Rainmaker_5: MusicDiscItemDefinition(
        name="Blackened Seas",
        description="Rainmaker's battle theme in oil rain.",
        rarity=Rarity.Common,
        musicPath="rainmaker_oil",
        discColor=ColorHelper.hexToPCol('4a369c'),
    ),
    MusicDiscItemType.Merc_Rainmaker_6: MusicDiscItemDefinition(
        name="Sorrowful Storms",
        description="Rainmaker's battle theme in storm cell.",
        rarity=Rarity.Common,
        musicPath="rainmaker_storm",
        discColor=ColorHelper.hexToPCol('4a369c'),
    ),
    MusicDiscItemType.Merc_Rainmaker_7: MusicDiscItemDefinition(
        name="Hope For Someday",
        description="Rainmaker's ending cutscene theme.",
        rarity=Rarity.Common,
        musicPath="rainmaker_end",
        discColor=ColorHelper.hexToPCol('4a369c'),
    ),

    # Witch Hunter
    MusicDiscItemType.Merc_WitchHunter_1: MusicDiscItemDefinition(
        name="The Hunter",
        description="Witch Hunter's normal battle theme.",
        rarity=Rarity.Common,
        musicPath="witchhunter_battle",
        discColor=ColorHelper.hexToPCol('334688'),
    ),
    MusicDiscItemType.Merc_WitchHunter_2: MusicDiscItemDefinition(
        name="Crowd Control",
        description="Witch Hunter's medium mob battle theme.",
        rarity=Rarity.Common,
        musicPath="witchhunter_battle_2",
        discColor=ColorHelper.hexToPCol('334688'),
    ),
    MusicDiscItemType.Merc_WitchHunter_3: MusicDiscItemDefinition(
        name="Flash Mob",
        description="Witch Hunter's large mob battle theme.",
        rarity=Rarity.Common,
        musicPath="witchhunter_battle_3",
        discColor=ColorHelper.hexToPCol('334688'),
    ),

    # Multislacker
    MusicDiscItemType.Merc_Multislacker_1: MusicDiscItemDefinition(
        name="Slacker Swing",
        description="Multislacker's normal battle theme.",
        rarity=Rarity.Common,
        musicPath="multislacker_battle",
        discColor=ColorHelper.hexToPCol('9863d0'),
    ),
    MusicDiscItemType.Merc_Multislacker_2: MusicDiscItemDefinition(
        name="My Dad Says That The Union Forces Us To Take Breaks",
        description="Multislacker's foreman battle theme.",
        rarity=Rarity.Common,
        musicPath="multislacker_battle_foreman",
        discColor=ColorHelper.hexToPCol('9863d0'),
    ),

    # Major Player
    MusicDiscItemType.Merc_MajorPlayer_1: MusicDiscItemDefinition(
        name="Takes Two Ta Tango-ago-go!",
        description="Major Player's phase 1 battle theme.",
        rarity=Rarity.Common,
        musicPath="majorplayer_battle",
        discColor=ColorHelper.hexToPCol('d0c049'),
    ),
    MusicDiscItemType.Merc_MajorPlayer_2: MusicDiscItemDefinition(
        name="Last Tap!",
        description="Major Player's phase 2 battle theme.",
        rarity=Rarity.Common,
        musicPath="majorplayer_battle_2",
        discColor=ColorHelper.hexToPCol('d0c049'),
    ),

    # Plutocrat
    MusicDiscItemType.Merc_Plutocrat_1: MusicDiscItemDefinition(
        name="Knocked Out of Orbit",
        description="Satellite Investors' battle theme.",
        rarity=Rarity.Common,
        musicPath="plutocrat_investors",
        discColor=ColorHelper.hexToPCol('15c1d0'),
    ),
    MusicDiscItemType.Merc_Plutocrat_2: MusicDiscItemDefinition(
        name="Snow Squabble",
        description="Plutocrat's normal battle theme.",
        rarity=Rarity.Common,
        musicPath="plutocrat_battle",
        discColor=ColorHelper.hexToPCol('15c1d0'),
    ),
    MusicDiscItemType.Merc_Plutocrat_3: MusicDiscItemDefinition(
        name="Snow Squallble",
        description="Plutocrat's snow squall battle theme.",
        rarity=Rarity.Common,
        musicPath="plutocrat_battle_cold",
        discColor=ColorHelper.hexToPCol('15c1d0'),
    ),

    # Chainsaw Consultant
    MusicDiscItemType.Merc_ChainsawConsultant_1: MusicDiscItemDefinition(
        name="Corporate Pruning",
        description="Chainsaw Consultant's phase 1 battle theme.",
        rarity=Rarity.Common,
        musicPath="chainsaw_battle",
        discColor=ColorHelper.hexToPCol('805622'),
    ),
    MusicDiscItemType.Merc_ChainsawConsultant_2: MusicDiscItemDefinition(
        name="Wrongful Termination",
        description="Chainsaw Consultant's phase 1 battle theme.",
        rarity=Rarity.Common,
        musicPath="chainsaw_battle",
        discColor=ColorHelper.hexToPCol('805622'),
    ),
    MusicDiscItemType.Merc_ChainsawConsultant_3: MusicDiscItemDefinition(
        name="There Is No Severance Package",
        description="Chainsaw Consultant's phase 1 battle theme.",
        rarity=Rarity.Common,
        musicPath="chainsaw_battle",
        discColor=ColorHelper.hexToPCol('805622'),
    ),

    # Pacesetter
    MusicDiscItemType.Merc_Pacesetter_1: MusicDiscItemDefinition(
        name="1998 toontown dance mix",
        description="Pacesetter's phase 1 battle theme.",
        rarity=Rarity.Common,
        musicPath="pacesetter_battle",
        discColor=ColorHelper.hexToPCol('5f1c80'),
    ),
    MusicDiscItemType.Merc_Pacesetter_2: MusicDiscItemDefinition(
        name="OVERCLOCKED",
        description="Pacesetter's phase 2 battle theme.",
        rarity=Rarity.Common,
        musicPath="pacesetter_final",
        discColor=ColorHelper.hexToPCol('5f1c80'),
    ),

    # Street mercs
    MusicDiscItemType.Merc_Street_DuckShuffler: MusicDiscItemDefinition(
        name="Stacking the Deck",
        description="Duck Shuffler's battle theme.",
        rarity=Rarity.Common,
        musicPath="duckshuffler_battle",
        discColor=ColorHelper.hexToPCol('c50b0e'),
    ),
    MusicDiscItemType.Merc_Street_DeepDiver: MusicDiscItemDefinition(
        name="Making Waves",
        description="Deep Diver's battle theme.",
        rarity=Rarity.Common,
        musicPath="deepdiver_battle",
        discColor=ColorHelper.hexToPCol('167a8d'),
    ),
    MusicDiscItemType.Merc_Street_Gatekeeper: MusicDiscItemDefinition(
        name="Holding The Line",
        description="Gatekeeper's battle theme.",
        rarity=Rarity.Common,
        musicPath="gatekeeper_battle",
        discColor=ColorHelper.hexToPCol('aaaaaa'),
    ),
    MusicDiscItemType.Merc_Street_Bellringer: MusicDiscItemDefinition(
        name="For Whom The Bell Tolls",
        description="Bellringer's battle theme.",
        rarity=Rarity.Common,
        musicPath="bellringer_battle",
        discColor=ColorHelper.hexToPCol('ca9b1a'),
    ),
    MusicDiscItemType.Merc_Street_Mouthpiece: MusicDiscItemDefinition(
        name="Mouthpiece Battle Theme",
        description="Mouthpiece's battle theme.",
        rarity=Rarity.Common,
        musicPath="mouthpiece_battle",
        discColor=ColorHelper.hexToPCol('6285ca'),
    ),
    MusicDiscItemType.Merc_Street_Firestarter: MusicDiscItemDefinition(
        name="Heating Up",
        description="Firestarter's battle theme.",
        rarity=Rarity.Common,
        musicPath="firestarter_battle",
        discColor=ColorHelper.hexToPCol('ca460f'),
    ),
    MusicDiscItemType.Merc_Street_Treekiller: MusicDiscItemDefinition(
        name="Treekiller Battle theme",
        description="Treekiller's battle theme.",
        rarity=Rarity.Common,
        musicPath="treekiller_battle",
        discColor=ColorHelper.hexToPCol('329b39'),
    ),
    MusicDiscItemType.Merc_Street_Featherbedder: MusicDiscItemDefinition(
        name="Featherbedder Battle Theme",
        description="Featherbedder's battle theme.",
        rarity=Rarity.Common,
        musicPath="featherbedder_battle",
        discColor=ColorHelper.hexToPCol('852f1a'),
    ),
}
