from toontown.suit import SuitHealthMeter
from toontown.toonbase import ToontownGlobals

class BossSuitHealthMeter(SuitHealthMeter.SuitHealthMeter):

    def __init__(self, suit):
        SuitHealthMeter.SuitHealthMeter.__init__(self, suit)
        self.dept = self.suit.dna.dept
        
    def generate(self, startMode=-1):
        if startMode != -1:
            self.mode = startMode
        
        self.geom = loader.loadModel('phase_3.5/models/char/ttcc_ene_insignias')
        dept = self.suit.dna.dept
        chestNull = self.suit.find('**/joint_lifeMeter')
        self.geom.reparentTo(chestNull)
        
        boardIcon = self.geom.find('**/emblem_board')
        corpIcon = self.geom.find('**/emblem_corp')
        legalIcon = self.geom.find('**/emblem_legal')
        moneyIcon = self.geom.find('**/emblem_money')
        salesIcon = self.geom.find('**/emblem_sales')
        
        self.icons = [boardIcon, corpIcon, legalIcon, moneyIcon, salesIcon]
            
        self.hpParts = [self.geom.find('**/emblem_hp'), self.geom.find('**/glow')]
        for part in self.hpParts:
            part.setColorScale(SuitHealthMeter.HEALTH_COLORS[0])
            part.stash()
            
        self.geom.setScale(3, 4.5, 3)
        if self.dept == 'l':
            self.geom.setY(1.2)
        else:
            self.geom.setP(-20)
            self.geom.setY(0.315)
        
        self.updateMeterMode(self.mode)

    def updateMeterMode(self, newMode):
        self.mode = newMode
        if self.mode == SuitHealthMeter.MODE_ROAM:
            for i in range(len(self.icons)): # Initialize colors of all insignias
                icon = self.icons[i]
                icon.stash()

            icon = self.icons[ToontownGlobals.cogDept2index.get(self.dept, 0)].unstash() # Unstash the icon for this dept, if not defined, default to board
            for part in self.hpParts:
                part.stash()
        else:
            for part in self.hpParts:
                part.unstash()

    def setHealthColor(self, colorIdx):
        if self.hpParts:
            for part in self.hpParts:
                part.setColorScale(SuitHealthMeter.HEALTH_COLORS[colorIdx])
