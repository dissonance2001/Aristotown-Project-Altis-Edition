from direct.gui.DirectGui import DirectButton, DirectFrame, DirectLabel
from direct.gui import DirectGuiGlobals as DGG
from pandac.PandaModules import TextNode

from toontown.toon.socialpanel.SocialPanelGlobals import sp_gui, getSocialPanelGroupBg, groupsPerCol
from toontown.toon.socialpanel.groups.SocialPanelText import ExtendedOnscreenText


class SocialPanelGroup(DirectFrame):
    DEFAULT_SIZE = (-1.9916, 1.9933, 0, 6.14)
    h_padding = 0.27
    v_padding = 0.04

    def __init__(self, canvas, group, pos, manager, empty=False, filtering=False):
        l, r, _, _ = self.DEFAULT_SIZE
        DirectFrame.__init__(
            self, parent=canvas, pos=pos, relief=DGG.GROOVE,
            frameSize=(l + self.h_padding, r - self.h_padding,
                       self.getPanelHeight() + self.v_padding, -self.v_padding),
            frameColor=(0.89, 0.925, 0.914, 0.0),
            borderWidth=(0.01, 0.01))
        self.initialiseoptions(SocialPanelGroup)
        self.group = group or {}
        self.manager = manager
        self.empty = empty
        self.filtering = filtering
        self.load()

    def load(self):
        panelHeight = self.getPanelHeight()
        self.frame_base = DirectFrame(
            parent=self, pos=(0, 0, panelHeight / 2.0), relief=None,
            frameColor=(1, 1, 1, 0),
            geom=sp_gui.find('**/SocialPanel_Groups_Box_Base'),
            geom_scale=(456.0 / 129.0, 1, 1))
        self.frame_image = DirectFrame(
            parent=self, pos=(0, 0, panelHeight / 2.0), relief=None,
            frameColor=(1, 1, 1, 0),
            geom=getSocialPanelGroupBg(self.group),
            geom_scale=(0.96 * (456.0 / 129.0), 1, 0.83))
        self.frame_gradient = DirectFrame(
            parent=self, pos=(0, 0, panelHeight / 2.0), relief=None,
            frameColor=(1, 1, 1, 0),
            geom=sp_gui.find('**/SocialPanel_Groups_Box_Gradient'),
            geom_scale=(0.96 * (456.0 / 129.0), 1, 0.83),
            geom_color=(0.835, 0.98, 0.824, 1))
        self.text_title = ExtendedOnscreenText(
            parent=self, scale=0.24, pos=(-1.64, -0.33),
            text=self._title(), align=TextNode.ALeft,
            fg=(0, 0, 0, 1), wordwrap=14)
        self.text_desc = DirectLabel(
            parent=self, relief=None, scale=0.2, pos=(-1.64, 0, -0.65),
            text=self._description(), text_align=TextNode.ALeft,
            text_fg=(0, 0, 0, 1))
        self.text_toons = DirectLabel(
            parent=self, relief=None, scale=0.24, pos=(0.41, 0, -0.84),
            text=self._toonsDescription(), text_align=TextNode.ARight,
            text_fg=(0, 0, 0, 1))
        self.button_view = DirectButton(
            parent=self, pos=(1.38, 0, -0.77), relief=None,
            frameSize=(-0.29, 0.29, -0.14, 0.14),
            geom=(sp_gui.find('**/OrangeButton_N'),
                  sp_gui.find('**/OrangeButton_P'),
                  sp_gui.find('**/OrangeButton_H')),
            geom_scale=(0.21 * (151.0 / 55.0), 1, 0.26),
            geom_color=(0.85, 0.85, 0.85, 1),
            text='View', text_scale=0.21, text_pos=(0, -0.062),
            text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
            command=self._view)
        self.button_join = DirectButton(
            parent=self, pos=(0.75, 0, -0.77), relief=None,
            frameSize=(-0.29, 0.29, -0.14, 0.14),
            geom=(sp_gui.find('**/OrangeButton_N'),
                  sp_gui.find('**/OrangeButton_P'),
                  sp_gui.find('**/OrangeButton_H')),
            geom_scale=(0.21 * (151.0 / 55.0), 1, 0.26),
            geom_color=(0.85, 0.85, 0.85, 1),
            text='Join', text_scale=0.21, text_pos=(0, -0.062),
            text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
            command=self._join)
        if self.empty:
            self._makeEmpty()
        else:
            if len(self.group.get('members', [])) >= int(self.group.get('maxSize', 4)):
                failModel = sp_gui.find('**/SocialPanel_Groups_Box_Base_Fail')
                if not failModel.isEmpty():
                    self.frame_base['geom'] = failModel
                self.frame_gradient['geom_color'] = (0.98, 0.76, 0.77, 1)
            self._updateJoinButton()

    def _title(self):
        name = str(self.group.get('activity', 'Group'))
        if len(name) >= 30:
            return name[:27] + '...'
        return name

    def _description(self):
        district = self._districtName()
        location = self.group.get('location', 'Current Area')
        return '%s\n%s' % (district, location)

    def _districtName(self):
        shardId = int(self.group.get('shardId', 0) or 0)
        if shardId:
            try:
                return str(base.cr.getShardName(shardId))
            except:
                pass
        try:
            return str(base.cr.getShardName(base.localAvatar.defaultShard))
        except:
            return 'District'

    def _toonsDescription(self):
        return '%s/%s' % (len(self.group.get('members', [])), int(self.group.get('maxSize', 4)))

    def _updateJoinButton(self):
        localId = int(getattr(base.localAvatar, 'doId', 0))
        localGroup = getattr(self.manager, 'group', None)
        memberIds = [int(member.get('avId', 0)) for member in self.group.get('members', [])]
        if localId in memberIds or localGroup:
            self.button_join.hide()
        else:
            self.button_join.show()
            if len(memberIds) >= int(self.group.get('maxSize', 4)):
                self.button_join['state'] = DGG.DISABLED
            else:
                self.button_join['state'] = DGG.NORMAL

    def _makeEmpty(self):
        self.frame_gradient.hide()
        self.frame_image.hide()
        self.text_desc.hide()
        self.text_toons.hide()
        self.button_view.hide()
        self.button_join.hide()
        self.text_title['pos'] = (0, -0.57)
        self.text_title.setAlign(TextNode.ACenter)
        if self.filtering:
            self.text_title.setTextWithVerticalAlignment('No filtered groups available.\nChange your filter settings or disable the filter.')
        else:
            self.text_title.setTextWithVerticalAlignment('No groups available.\nPress Create to make a group.')

    def _view(self):
        messenger.send('social-panel-groups-view', [self.group])

    def _join(self):
        self.manager.requestJoin(int(self.group.get('id', 0)))

    def bindToScroll(self, scrollFrame):
        for gui in (self, self.frame_base, self.frame_image, self.frame_gradient,
                    self.button_join, self.button_view):
            try:
                gui.bind(DGG.WHEELUP, scrollFrame.verticalScroll.scrollStep, extraArgs=[-1])
                gui.bind(DGG.WHEELDOWN, scrollFrame.verticalScroll.scrollStep, extraArgs=[1])
            except:
                pass

    def getPanelHeight(self):
        canvasSize = self.DEFAULT_SIZE
        return (canvasSize[2] - canvasSize[3]) / float(groupsPerCol)
