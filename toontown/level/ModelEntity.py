from toontown.level import BasicEntities
from toontown.level.editor import EditorGlobals


class ModelEntity(BasicEntities.NodePathEntity):
    def __init__(self, level, entId):
        self.collisionsOnly = False
        self.flattenType = 'light'
        self.goonHatType = 'none'
        self.entInitialized = False
        BasicEntities.NodePathEntity.__init__(self, level, entId)
        self.entInitialized = True
        self.model = None
        self.loadModel()

    def destroy(self):
        if self.model:
            self.model.removeNode()
            del self.model
        BasicEntities.NodePathEntity.destroy(self)

    def loadModel(self):
        if self.model:
            self.model.removeNode()
            self.model = None
        if self.modelPath is None:
            return
        try:
            self.model = loader.loadModel(self.modelPath)
        except:
            self.notify.warning(f'invalid model path: {self.modelPath}. Please try again.')
            return

        if self.model:
            if hasattr(self, 'modelNode') and self.modelNode:
                modNode = self.model.find(self.modelNode)
                if modNode:
                    self.model.removeNode()  # Remove the top model after grabbing the node
                    self.model = modNode
                else:
                    self.notify.warning(f'Invalid model node: {modNode}. Defaulting to base model.')
            self.model.reparentTo(self)
            if self.collisionsOnly:
                if EditorGlobals.wantLevelEditor():
                    self.model.setTransparency(1)
                    self.model.setColorScale(1, 1, 1, 0.1)
                else:
                    self.model.hide()
            else:
                self.model.show()
            if self.modelPath in ('phase_9/models/cogHQ/woodCrateB.bam', 'phase_9/models/cogHQ/metal_crateB.bam',
                                  'phase_10/models/cashbotHQ/CBMetalCrate.bam',
                                  'phase_10/models/cogHQ/CBMetalCrate2.bam', 'phase_10/models/cashbotHQ/CBWoodCrate.bam',
                                  'phase_11/models/lawbotHQ/LB_metal_crate.bam',
                                  'phase_11/models/lawbotHQ/LB_metal_crate2.bam'):
                cNode = self.find('**/wall')
                cNode.setZ(cNode, -.75)
                colNode = self.find('**/collision')
                floor = colNode.find('**/floor')
                floor2 = floor.copyTo(colNode)
                floor2.setZ(floor2, -.75)
            if self.goonHatType != 'none':
                self.goonType = {'hardhat': 'pg',
                                 'security': 'sg'}[self.goonHatType]
                self.hat = self.model
                if self.goonType == 'pg':
                    self.hat.find('**/security_hat').hide()
                elif self.goonType == 'sg':
                    self.hat.find('**/hard_hat').hide()
                del self.hat
                del self.goonType
            if self.flattenType == 'light':
                self.model.flattenLight()
            elif self.flattenType == 'medium':
                self.model.flattenMedium()
            elif self.flattenType == 'strong':
                self.model.flattenStrong()

    if EditorGlobals.wantLevelEditor():
        def setModelPath(self, path):
            self.modelPath = path
            self.loadModel()

        def setModelNode(self, nodePath):
            self.modelNode = nodePath
            self.loadModel()

        def setCollisionsOnly(self, collisionsOnly):
            self.collisionsOnly = collisionsOnly
            self.loadModel()

        def setGoonHatType(self, goonHatType):
            self.goonHatType = goonHatType
            self.loadModel()
