if __name__ == "__main__":
    from tools.headless.headlessbase import HeadlessStart
    from tools.headless.headlessbase.HeadlessBase import HeadlessBase
    base = HeadlessBase(wantHotkeys=False)
    if __debug__:
        from toontown.utils.DeveloperInjector import startInjector
        startInjector()
    # base.initCR()  # defines base.cr
    # base.startHeadlessShow()

from toontown.gui import TTGui
from toontown.gui.GUITemplateSliders import GUITemplateSliders
from toontown.gui.GUINode import GUINode
from toontown.gui.CornerAnchor import CornerAnchor
from toontown.gui import UiHelpers
from toontown.gui.EasyManagedItem import EasyManagedItem
from toontown.gui.EasyManagedButton import EasyManagedButton
from toontown.gui.Bounds import Bounds
from toontown.gui.GUIPositionGlobals import ScreenCorner
from toontown.toon.gui import GuiBinGlobals

from toontown.gui.GUIGlobals import GUI_TEXCARD_PREFIX, GUI_ICON_MODEL_PATH, BG_CIRCLE_1_COLOR_DEFAULT
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum

from toontown.toon.npc.shop.NPCToonShopGlobals import NPCShopCategory, ShopCategoryToTitle

from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.utils.InjectorTarget import InjectorTarget
from toontown.utils import ColorHelper
from direct.gui import DirectGuiGlobals
from direct.gui.DirectGui import *
from panda3d.core import *


@DirectNotifyCategory()
class NPCToonShopCategoryButton(EasyManagedButton):
    @InjectorTarget
    def __init__(self, parent, **kw):
        genBgIconsTexcard = loader.loadModel(f'{GUI_ICON_MODEL_PATH}{GUI_TEXCARD_PREFIX}gen_bg_icons')
        circle = genBgIconsTexcard.find('**/circle_1')
        genBgIconsTexcard.removeNode()

        # GUI boilerplate.
        optiondefs = TTGui.kwargsToOptionDefs(
            pos=(0, 0, 0),
            scale=1.0,
            relief=None,
            image=circle,
            image_color=BG_CIRCLE_1_COLOR_DEFAULT,
            text=('', 'Social', 'Social'),
            text_scale=0.45,
            text_pos=(0, -0.9),
            easyWidth=1.0,
            easyPadRight=0.45,

            shopCategory=[NPCShopCategory.Social, self.place],
        )
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, **kw)
        self.postInitialized = False
        self.postInitialiseFuncList.append(lambda: setattr(self, 'postInitialized', True))
        self.initialiseoptions(NPCToonShopCategoryButton)

        self.__funcMap = {
            # Standard categories
            NPCShopCategory.Social: self.__icon_Social,
            NPCShopCategory.Profile: self.__icon_Profile,
            NPCShopCategory.Clothing: self.__icon_All,
            NPCShopCategory.Battle: self.__icon_Battle,
            NPCShopCategory.EstateKits: self.__icon_Estates,
            NPCShopCategory.EstateFurniture: self.__icon_Estates,
            NPCShopCategory.Fishing: self.__icon_Activities,
            NPCShopCategory.Racing: self.__icon_Activities,
            NPCShopCategory.Upgrades: self.__icon_Upgrades,
            NPCShopCategory.TTC: self.__icon_TTC,
            NPCShopCategory.BB: self.__icon_BB,
            NPCShopCategory.YOTT: self.__icon_YOTT,
            NPCShopCategory.DG: self.__icon_DG,
            NPCShopCategory.MML: self.__icon_MML,
            NPCShopCategory.TB: self.__icon_TB,
            NPCShopCategory.AA: self.__icon_AA,
            NPCShopCategory.DDL: self.__icon_DDL,
        }

        # Call these two.
        self.__create()
        self.place()

    def __create(self):
        return

    def place(self):
        if not self.postInitialized:
            return

        iconHolder = NodePath('npctscb-iconHolder')

        icon, iconScale, iconPos = self.__funcMap[self['shopCategory']]()
        if icon and not icon.isEmpty():
            icon.reparentTo(iconHolder)

        self['geom'] = iconHolder
        self['geom_scale'] = iconScale
        self['geom_pos'] = iconPos

        catTitle = ShopCategoryToTitle[self['shopCategory']]
        self['text'] = ('', catTitle, catTitle)

    # region Icon Funcs

    @staticmethod
    def __icon_ClubBg(iconNum):
        clubAssets = loader.loadModel("phase_3.5/models/gui/clubs/club_icons")
        iconGeom = clubAssets.find(f'**/icon_{iconNum}')
        clubAssets.detachNode()
        return iconGeom, 0.75, (0, 0, 0)

    @staticmethod
    def __icon_All():
        iconModels = loader.loadModel('phase_3.5/models/gui/sos_textures')
        iconGeom = iconModels.find('**/district')
        iconModels.detachNode()
        return iconGeom, 0.6, (0, 0, 0)

    @staticmethod
    def __icon_Social():
        chatAssets = loader.loadModel("phase_3.5/models/gui/chat/chat_panel")
        iconGeom = chatAssets.find('**/Circle_Chat_N')
        chatAssets.detachNode()
        return iconGeom, 0.6, (0, 0, 0)

    @staticmethod
    def __icon_Profile():
        profileAssets = loader.loadModel("phase_3.5/models/gui/profile/background")
        iconGeom = profileAssets.find('**/default')
        profileAssets.detachNode()
        return iconGeom, 0.6, (0, 0, 0)

    @staticmethod
    def __icon_Battle():
        iconGeom = base.localAvatar.inventory.buttonLookup(AttackEnum.TOON_THROW, 0).copyTo(NodePath())
        return iconGeom, 4.0, (0, 0, 0)

    @staticmethod
    def __icon_Estates():
        return NPCToonShopCategoryButton.__icon_ClubBg(7)

    @staticmethod
    def __icon_Activities():
        commonIconsTexcard = loader.loadModel(f'{GUI_ICON_MODEL_PATH}{GUI_TEXCARD_PREFIX}icon_common')
        iconGeom = commonIconsTexcard.find('**/fish_1')
        commonIconsTexcard.detachNode()
        return iconGeom, 0.6, (0, 0, 0)

    @staticmethod
    def __icon_Upgrades():
        # In case this ever shows up, it will return a question mark.
        # It shouldn't ever actually show up though.
        questAssets = loader.loadModel('phase_3/models/gui/quest_question')
        iconGeom = questAssets.find("**/quest_exclaim")
        questAssets.detachNode()
        return iconGeom, 0.6, (0, 0, 0)

    @staticmethod
    def __icon_TTC():
        return NPCToonShopCategoryButton.__icon_ClubBg(12)

    @staticmethod
    def __icon_BB():
        return NPCToonShopCategoryButton.__icon_ClubBg(13)

    @staticmethod
    def __icon_YOTT():
        return NPCToonShopCategoryButton.__icon_ClubBg(14)

    @staticmethod
    def __icon_DG():
        return NPCToonShopCategoryButton.__icon_ClubBg(15)

    @staticmethod
    def __icon_MML():
        return NPCToonShopCategoryButton.__icon_ClubBg(16)

    @staticmethod
    def __icon_TB():
        return NPCToonShopCategoryButton.__icon_ClubBg(17)

    @staticmethod
    def __icon_AA():
        return NPCToonShopCategoryButton.__icon_ClubBg(18)

    @staticmethod
    def __icon_DDL():
        return NPCToonShopCategoryButton.__icon_ClubBg(19)

    # endregion
