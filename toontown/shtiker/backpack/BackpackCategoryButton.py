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

from .BackpackCategoryGlobals import BackpackCategory, CategoryToString
from toontown.gui.GUIGlobals import GUI_TEXCARD_PREFIX, GUI_ICON_MODEL_PATH, BG_CIRCLE_1_COLOR_DEFAULT
from toontown.battle.attacks.base.AttackEnum import AttackEnum

from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.utils.InjectorTarget import InjectorTarget
from toontown.utils import ColorHelper
from direct.gui import DirectGuiGlobals
from direct.gui.DirectGui import *
from panda3d.core import *


@DirectNotifyCategory()
class BackpackCategoryButton(EasyManagedButton):
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
            text=('', 'All', 'All'),
            text_scale=0.45,
            text_pos=(0, -0.9),
            easyWidth=1.0,
            easyPadRight=0.45,

            backpackCategory=[BackpackCategory.All, self.place],
        )
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, **kw)
        self.postInitialized = False
        self.postInitialiseFuncList.append(lambda: setattr(self, 'postInitialized', True))
        self.initialiseoptions(BackpackCategoryButton)

        self.__funcMap = {
            # Standard categories
            BackpackCategory.All: self.__icon_All,
            BackpackCategory.Social: self.__icon_Social,
            BackpackCategory.Profile: self.__icon_Profile,
            BackpackCategory.Battle: self.__icon_Battle,
            BackpackCategory.Estates: self.__icon_Estates,
            BackpackCategory.Activities: self.__icon_Activities,
            BackpackCategory.Misc: self.__icon_Misc,
            # Wardrobe categories
            BackpackCategory.W_All: self.__icon_All,
            BackpackCategory.W_Shirts: self.__icon_All,
            BackpackCategory.W_Shorts: self.__icon_All,
            BackpackCategory.W_Skirts: self.__icon_All,
            BackpackCategory.W_Hats: self.__icon_All,
            BackpackCategory.W_Glasses: self.__icon_All,
            BackpackCategory.W_Neck: self.__icon_All,
            BackpackCategory.W_Backpack: self.__icon_All,
            BackpackCategory.W_Shoes: self.__icon_All,
        }

        # Call these two.
        self.__create()
        self.place()

    def __create(self):
        return

    def place(self):
        if not self.postInitialized:
            return

        iconHolder = NodePath('bpcb-iconHolder')

        icon, iconScale, iconPos = self.__funcMap[self['backpackCategory']]()
        if icon and not icon.isEmpty():
            icon.reparentTo(iconHolder)

        self['geom'] = iconHolder
        self['geom_scale'] = iconScale
        self['geom_pos'] = iconPos

        catTitle = CategoryToString[self['backpackCategory']]
        self['text'] = ('', catTitle, catTitle)

    # region Icon Funcs

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
        clubAssets = loader.loadModel("phase_3.5/models/gui/clubs/club_icons")
        iconGeom = clubAssets.find('**/icon_7')
        clubAssets.detachNode()
        return iconGeom, 0.75, (0, 0, 0)

    @staticmethod
    def __icon_Activities():
        commonIconsTexcard = loader.loadModel(f'{GUI_ICON_MODEL_PATH}{GUI_TEXCARD_PREFIX}icon_common')
        iconGeom = commonIconsTexcard.find('**/fish_1')
        commonIconsTexcard.detachNode()
        return iconGeom, 0.6, (0, 0, 0)

    @staticmethod
    def __icon_Misc():
        questAssets = loader.loadModel('phase_3/models/gui/quest_question')
        iconGeom = questAssets.find("**/quest_exclaim")
        questAssets.detachNode()
        return iconGeom, 0.6, (0, 0, 0)

    # endregion
