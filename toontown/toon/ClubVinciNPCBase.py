from __future__ import absolute_import
from pandac.PandaModules import Texture
from toontown.toon import ToonHead
from toontown.toon.DistributedNPCToon import DistributedNPCToon
from toontown.nametag.NametagGlobals import CFSpeech, CFTimeout


class ClubVinciNPCBase(DistributedNPCToon):
    customHeadPrefix = None
    exactPosition = (0, 0, 0)
    exactHeading = 0
    shirtTexture = None
    sleeveTexture = None
    bottomTexture = None
    accessoryDefinitions = ()

    def __init__(self, cr):
        DistributedNPCToon.__init__(self, cr)
        self.npcType = ''
        self.clubGui = None
        self._clubAccessoryNodes = []

    def generateToonHead(self, copy=1):
        if not self.customHeadPrefix:
            return DistributedNPCToon.generateToonHead(self, copy)
        oldPrefix = ToonHead.HeadDict.get('x')
        ToonHead.HeadDict['x'] = self.customHeadPrefix
        try:
            for lod in ('1000', '500', '250'):
                key = 'phase_3' + self.customHeadPrefix + lod
                if key not in ToonHead.PreloadHeads:
                    model = loader.loadModel(key, okMissing=True)
                    if model:
                        model.flattenMedium()
                        ToonHead.PreloadHeads[key] = model
            return DistributedNPCToon.generateToonHead(self, copy)
        finally:
            ToonHead.HeadDict['x'] = oldPrefix

    def initToonState(self):
        self.reparentTo(render)
        self.setPos(*self.exactPosition)
        self.setH(self.exactHeading)
        self.setAnimState('neutral', 0.9, None, None)

    def announceGenerate(self):
        DistributedNPCToon.announceGenerate(self)
        self.npcType = ''
        self.setDisplayName(self.getName())
        self._applyVinciAppearance()

    def disable(self):
        self._closeClubGui()
        DistributedNPCToon.disable(self)

    def _loadTexture(self, path):
        tex = loader.loadTexture(path, okMissing=True)
        if tex:
            tex.setMinfilter(Texture.FTLinearMipmapLinear)
            tex.setMagfilter(Texture.FTLinear)
        return tex

    def _applyVinciAppearance(self):
        shirt = self._loadTexture(self.shirtTexture) if self.shirtTexture else None
        sleeve = self._loadTexture(self.sleeveTexture) if self.sleeveTexture else None
        bottom = self._loadTexture(self.bottomTexture) if self.bottomTexture else None
        for lod in ('1000', '500', '250'):
            torso = self.getPart('torso', lod)
            if torso:
                top = torso.find('**/torso-top')
                if shirt and not top.isEmpty():
                    top.setTexture(shirt, 1)
                sleeves = torso.find('**/sleeves')
                if sleeve and not sleeves.isEmpty():
                    sleeves.setTexture(sleeve, 1)
                if bottom:
                    for geom in torso.findAllMatches('**/torso-bot'):
                        geom.setTexture(bottom, 1)
        self._clearClubAccessories()
        for definition in self.accessoryDefinitions:
            self._attachAccessory(*definition)

    def _clearClubAccessories(self):
        for node in self._clubAccessoryNodes:
            if node and not node.isEmpty():
                node.removeNode()
        self._clubAccessoryNodes = []

    def _attachAccessory(self, modelPath, texturePath, target, pos, hpr, scale):
        model = loader.loadModel(modelPath, okMissing=True)
        if not model:
            return
        texture = self._loadTexture(texturePath) if texturePath else None
        if texture:
            model.setTexture(texture, 1)
        model.setPos(*pos)
        model.setHpr(*hpr)
        model.setScale(*scale)
        model.setTwoSided(True)
        if target == 'head':
            targets = self.findAllMatches('**/__Actor_head')
        else:
            targets = self.findAllMatches('**/def_joint_attachFlower')
        for targetNode in targets:
            holder = targetNode.attachNewNode('clubVinciAccessory')
            model.instanceTo(holder)
            self._clubAccessoryNodes.append(holder)

    def _prepareInteraction(self):
        try:
            place = base.cr.playGame.getPlace()
            if place:
                place.fsm.request('stopped')
        except:
            pass
        try:
            base.localAvatar.stopLookAround()
            self.stopLookAround()
            base.localAvatar.lookAt(self)
            self.lookAt(base.localAvatar)
        except:
            pass

    def _restoreInteraction(self, *args):
        self.clubGui = None
        try:
            place = base.cr.playGame.getPlace()
            if place:
                place.fsm.request('walk')
        except:
            pass
        try:
            base.localAvatar.startLookAround()
            self.startLookAround()
        except:
            pass

    def _closeClubGui(self):
        if self.clubGui:
            try:
                self.clubGui.destroy()
            except:
                pass
            self.clubGui = None
