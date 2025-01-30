self.enraged = status.find('**/rage_mode_icon')  # second slot enraged
        self.enraged.reparentTo(self.healthNode)
        self.enraged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.enraged.hide()
        self.shielding = status.find('**/defense_mode_icon')  # second slot defense
        self.shielding.reparentTo(self.healthNode)
        self.shielding.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.shielding.hide()
        self.enraged2 = status2.find('**/rage_mode_icon')  # third slot enraged
        self.enraged2.reparentTo(self.healthNode)
        self.enraged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.enraged2.hide()
        self.shielding2 = status2.find('**/defense_mode_icon')  # third slot defense
        self.shielding2.reparentTo(self.healthNode)
        self.shielding2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.shielding2.hide()
        self.enraged3 = status3.find('**/rage_mode_icon')  # fourth slot enraged
        self.enraged3.reparentTo(self.healthNode)
        self.enraged3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.enraged3.hide()
        self.shielding3= status3.find('**/defense_mode_icon')  # fourth slot defense
        self.shielding3.reparentTo(self.healthNode)
        self.shielding3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.shielding3.hide()
        self.overcharged = status.find('**/overcharge_icon') # second slot overcharge
        self.overcharged.reparentTo(self.healthNode)
        self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.overcharged.hide()
        self.overcharged2 = status2.find('**/overcharge_icon') #third slot overcharge
        self.overcharged2.reparentTo(self.healthNode)
        self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.overcharged2.hide()
        self.lured = status.find('**/lured_prestige_icon') #lure resistance overcharge first slot
        self.lured.reparentTo(self.healthNode)
        self.lured.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.lured.hide()
        self.luredCog = status.find('**/lured_icon')  # lure icon first
        self.luredCog.reparentTo(self.healthNode)
        self.luredCog.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.luredCog.hide()
        self.luredCog2 = status2.find('**/lured_icon')  # lure icon 2nd
        self.luredCog2.reparentTo(self.healthNode)
        self.luredCog2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.luredCog2.hide()
        self.luredCog3 = status3.find('**/lured_icon')  # lure icon 3rd
        self.luredCog3.reparentTo(self.healthNode)
        self.luredCog3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.luredCog3.hide()
        self.luredCog4 = status4.find('**/lured_icon')  # lure icon 4th
        self.luredCog4.reparentTo(self.healthNode)
        self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.luredCog4.hide()
        self.luredManager = status2.find('**/lured_prestige_icon') # lure resistance manager first slot
        self.luredManager.reparentTo(self.healthNode)
        self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.luredManager.hide()
        self.luredManager2 = status3.find('**/lured_prestige_icon') #lure resistance second slot
        self.luredManager2.reparentTo(self.healthNode)
        self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165) #second slot lure resist
        self.luredManager2.hide()
        self.insured = status3.find('**/insured_icon') #second slot insurance
        self.insured.reparentTo(self.healthNode)
        self.insured.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.insured.hide()
        self.insured2 = status2.find('**/insured_icon')
        self.insured2.reparentTo(self.healthNode)
        self.insured2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165) #third slot insurance
        self.insured2.hide()
        self.damageUp = status2.find('**/suit_damage_up_icon') #second slot damage up
        self.damageUp.reparentTo(self.healthNode)
        self.damageUp.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.damageUp.hide()
        self.damageUp2 = status.find('**/suit_damage_up_icon') # third slot damage up
        self.damageUp2.reparentTo(self.healthNode)
        self.damageUp2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.damageUp2.hide()
        self.damageUpMgr = status3.find('**/suit_damage_up_icon') # 4th slot damage up
        self.damageUpMgr.reparentTo(self.healthNode)
        self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.damageUpMgr.hide()
        self.skeleton = status.find('**/skelecog_icon')
        self.skeleton.reparentTo(self.healthNode)
        self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.skeleton.hide()
        self.virtual = status.find('**/virtual_icon')
        self.virtual.reparentTo(self.healthNode)
        self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.virtual.hide()
        self.immortal = status.find('**/worker_management_icon') #second slot immunity icon
        self.immortal.reparentTo(self.healthNode)
        self.immortal.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.immortal.hide()
        self.immortal2 = status.find('**/unite_cooldown_icon')  # third slot immunity icon
        self.immortal2.reparentTo(self.healthNode)
        self.immortal2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.immortal2.hide()
        self.immortal3 = status2.find('**/focused_defense_icon')  # third slot immunity icon
        self.immortal3.reparentTo(self.healthNode)
        self.immortal3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.immortal3.hide()
        self.immortal4 = status.find('**/focused_defense_icon')  # fourth slot immunity icon
        self.immortal4.reparentTo(self.healthNode)
        self.immortal4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.immortal4.hide()
        self.vulnerable = status.find('**/vulnerable_icon')  # first slot vulnerability icon
        self.vulnerable.reparentTo(self.healthNode)
        self.vulnerable.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.vulnerable.hide()
        self.vulnerable2 = status2.find('**/vulnerable_icon') # second slot vulnerability icon
        self.vulnerable2.reparentTo(self.healthNode)
        self.vulnerable2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.vulnerable2.hide()
        self.vulnerable3 = status3.find('**/vulnerable_icon') # third slot vulnerability icon
        self.vulnerable3.reparentTo(self.healthNode)
        self.vulnerable3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.vulnerable3.hide()
        self.vulnerable4 = status4.find('**/vulnerable_icon')  # fourth slot vulnerability icon
        self.vulnerable4.reparentTo(self.healthNode)
        self.vulnerable4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.vulnerable4.hide()
        self.soakResist = status.find('**/soaked_icon')  # first slot soak resist icon
        self.soakResist.reparentTo(self.healthNode)
        self.soakResist.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.soakResist.hide()
        self.soakResist2 = status2.find('**/soaked_icon')  # 2 slot soak resist icon
        self.soakResist2.reparentTo(self.healthNode)
        self.soakResist2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.soakResist2.hide()
        self.soakResist3 = status3.find('**/soaked_icon')  # 3 slot soak resist icon
        self.soakResist3.reparentTo(self.healthNode)
        self.soakResist3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.soakResist3.hide()
        self.soakResist4 = status4.find('**/soaked_icon')  # 4 slot soak resist icon
        self.soakResist4.reparentTo(self.healthNode)
        self.soakResist4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.soakResist4.hide()
        self.syphon = status.find('**/ink_drain_icon')  # 1 slot soak syphon icon
        self.syphon.reparentTo(self.healthNode)
        self.syphon.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.syphon.hide()
        self.syphon2 = status2.find('**/ink_drain_icon')  # 2 slot soak syphon icon
        self.syphon2.reparentTo(self.healthNode)
        self.syphon2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.syphon2.hide()
        self.syphon3 = status3.find('**/ink_drain_icon')  # 3 slot soak syphon icon
        self.syphon3.reparentTo(self.healthNode)
        self.syphon3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.syphon3.hide()
        self.syphon4 = status4.find('**/ink_drain_icon')  # 4 slot soak syphon icon
        self.syphon4.reparentTo(self.healthNode)
        self.syphon4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.syphon4.hide()
        self.absorbing = status.find('**/damage_absorb_icon')  # 1 slot absorb icon
        self.absorbing.reparentTo(self.healthNode)
        self.absorbing.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.absorbing.hide()
        self.absorbing2 = status2.find('**/damage_absorb_icon')  # 2 slot absorb icon
        self.absorbing2.reparentTo(self.healthNode)
        self.absorbing2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.absorbing2.hide()
        self.absorbing3 = status3.find('**/damage_absorb_icon')  # 3 slot absorb icon
        self.absorbing3.reparentTo(self.healthNode)
        self.absorbing3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.absorbing3.hide()
        self.absorbing4 = status4.find('**/damage_absorb_icon')  # 4 slot absorb icon
        self.absorbing4.reparentTo(self.healthNode)
        self.absorbing4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.absorbing4.hide()
        self.damageReduction = status.find('**/shield_icon')  # 1 slot damage reduction
        self.damageReduction.reparentTo(self.healthNode)
        self.damageReduction.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.damageReduction.hide()
        self.damageReduction2 = status2.find('**/shield_icon')  # 2 slot damage reduction
        self.damageReduction2.reparentTo(self.healthNode)
        self.damageReduction2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.damageReduction2.hide()
        self.damageReduction3 = status3.find('**/shield_icon')  # 3 slot damage reduction
        self.damageReduction3.reparentTo(self.healthNode)
        self.damageReduction3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.damageReduction3.hide()
        self.damageReduction4 = status4.find('**/shield_icon')  # 4 slot damage reduction
        self.damageReduction4.reparentTo(self.healthNode)
        self.damageReduction4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.damageReduction4.hide()