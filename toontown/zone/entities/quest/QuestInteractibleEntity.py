from panda3d.core import *
from toontown.level.editor import EditorGlobals
from toontown.zone.entities.quest.QuestAnimatedEntity import QuestAnimatedEntity
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.toonbase import ToontownGlobals


@DirectNotifyCategory(debug=True)
class QuestInteractibleEntity(QuestAnimatedEntity):
    def __init__(self, level, entId):
        super().__init__(level, entId)
        self.collSphereName = f'QuestInteractibleEntity-{self.level.doId}-{self.entId}'
        self.loadSphere()

    def loadSphere(self):
        collSphere = CollisionSphere(0, 0, 0, self.sphereRadius)
        collSphere.setTangible(0)
        collSphereNode = CollisionNode(self.collSphereName)
        collSphereNode.setIntoCollideMask(ToontownGlobals.WallBitmask)
        collSphereNode.addSolid(collSphere)
        self.sphereNodePath = self.attachNewNode(collSphereNode)
        self.sphereNodePath.setPos(self.spherePos)
        if EditorGlobals.wantLevelEditor():
            self.sphereNodePath.setColorScale(1, 0, 0, 1)
            self.sphereNodePath.show()

        self.accept('enter' + self.collSphereName, self.__collisionEnter)

    def __collisionEnter(self, _=None):
        if not self.hadWantedQuest:
            return

        place = base.localAvatar.getPlace()
        if place and place.getState() == 'Walk':
            self.level.d_requestQuestEntityInteract(self)

    if EditorGlobals.wantLevelEditor():
        def setSphereRadius(self, sphereRadius):
            self.sphereRadius = sphereRadius
            self.ignore('enter' + self.collSphereName)
            self.sphereNodePath.removeNode()
            self.loadSphere()

        def setSpherePos(self, spherePos):
            self.spherePos = spherePos
            self.ignore('enter' + self.collSphereName)
            self.sphereNodePath.removeNode()
            self.loadSphere()
