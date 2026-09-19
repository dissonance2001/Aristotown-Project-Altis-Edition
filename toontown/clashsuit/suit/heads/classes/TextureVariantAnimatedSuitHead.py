from panda3d.core import Texture
from enum import Enum, auto
from typing import Dict

from toontown.suit.heads.AnimatedSuitHead import AnimatedSuitHead
from toontown.suit.heads.AnimatedSuitHeadRepository import AnimatedSuitHeadClass
from toontown.suit import SuitGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


class TexVariantType(Enum):
    Executive  = auto()
    Unemployed = auto()
    ExecutiveSkeleton = auto()
    UnemployedSkeleton = auto()


SuitNameToTexture: Dict[str, Dict[TexVariantType, str]] = {
    'bgh': {
        TexVariantType.Executive: 'phase_14/maps/cc_t_ene_bagholder_exe.png',
        TexVariantType.Unemployed: 'phase_14/maps/cc_t_ene_bagholder_unemployed.png',
    },
    'ins': {
        TexVariantType.Executive: 'phase_14/maps/cc_t_ene_insider_exe.png',
        TexVariantType.Unemployed: 'phase_14/maps/cc_t_ene_insider_unemployed.png',
    },
    'hho': {
        TexVariantType.Executive: 'phase_14/maps/cc_t_ene_headhoncho_exe.png',
        TexVariantType.Unemployed: 'phase_14/maps/cc_t_ene_headhoncho_unemployed.png',
    },
}


@DirectNotifyCategory()
@AnimatedSuitHeadClass(suitName=('bgh', 'ins', 'hho'))
class TextureVariantAnimatedSuitHead(AnimatedSuitHead):
    """
    An animated suit head that can change textures depending on the following conditions:
    - Is executive, or
    - Is unemployed, or
    - Is executive and a skelecog, or
    - Is unemployed and a skelecog

    There are options for headGeom and skelecog to be passed through because of the existence of zapHeadActors.
    """

    def makeExecutive(self, headGeom=None, isSkeleton=None):
        if not headGeom:
            headGeom = self
        if isSkeleton is None:
            isSkeleton = self.isSkeleton
        self.loadHeadTexOfType(headGeom, isSkeleton, normalType=TexVariantType.Executive,
                               skeletonType=TexVariantType.ExecutiveSkeleton)

    def makeUnemployed(self, headGeom=None, isSkeleton=None):
        if not headGeom:
            headGeom = self
        if isSkeleton is None:
            isSkeleton = self.isSkeleton
        self.loadHeadTexOfType(headGeom, isSkeleton, normalType=TexVariantType.Unemployed,
                               skeletonType=TexVariantType.UnemployedSkeleton)

    def loadHeadTexOfType(self, headGeom, isSkeleton: bool, normalType: TexVariantType, skeletonType: TexVariantType):
        headTexBank = SuitNameToTexture.get(self.suit.style.name)
        if not headTexBank:
            return

        headTexPath = headTexBank.get(skeletonType if isSkeleton else normalType)
        if not headTexPath:
            return
        headTex = loader.loadTexture(headTexPath)
        if not headTex:
            return

        headTex.setMinfilter(Texture.FTLinearMipmapLinear)
        headTex.setMagfilter(Texture.FTLinear)

        headGeom.setTexture(headTex, 1)
