self.status = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.status2 = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.status3 = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.status4 = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.status5 = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.status6 = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.status7 = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.status8 = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.attackIcon7 = self.status8.find('**/default_background')  # fourth upper
        self.attackIcon7.reparentTo(self.healthNode)
        self.attackIcon7.setPosHprScale(0.115, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
        self.attackIcon7.hide()
        self.attackIcon6 = self.status7.find('**/default_background')  # third upper
        self.attackIcon6.reparentTo(self.healthNode)
        self.attackIcon6.setPosHprScale(-0.045, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
        self.attackIcon6.hide()
        self.attackIcon5 = self.status6.find('**/default_background')  # second upper
        self.attackIcon5.reparentTo(self.healthNode)
        self.attackIcon5.setPosHprScale(-0.2075, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
        self.attackIcon5.hide()
        self.attackIcon4 = self.status5.find('**/default_background')  # first upper
        self.attackIcon4.reparentTo(self.healthNode)
        self.attackIcon4.setPosHprScale(-0.37, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
        self.attackIcon4.hide()
        self.attackIcon3 = self.status4.find('**/default_background')  # fourth
        self.attackIcon3.reparentTo(self.healthNode)
        self.attackIcon3.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.attackIcon2 = self.status3.find('**/default_background')  # third
        self.attackIcon2.reparentTo(self.healthNode)
        self.attackIcon2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.attackIcon1 = self.status2.find('**/default_background')  # second
        self.attackIcon1.reparentTo(self.healthNode)
        self.attackIcon1.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.attackIcon = self.status.find('**/default_background')  # first
        self.attackIcon.reparentTo(self.healthNode)
        self.attackIcon.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)