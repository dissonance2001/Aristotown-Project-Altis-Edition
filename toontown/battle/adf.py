posPoints = [Point3(-0.1, -0.175, 0), VBase3(-10.584, 11.945, -161.684)]

card = globalPropPool.getProp('ttht_m_ene_techbotLaptop')
propTrackNew = Parallel()
    propTrackNew.append(getPropTrack(card, suit.getLeftHand(), laptopPosPoints, 1e-06, 2, scaleUpPoint=scaleUpPoint, scaleUpTime=0,
                                              anim=1, animStartTime=0.5, animDuration=2.5,
                                              propName='ttht_m_ene_techbotLaptop'))

    throwTrack = Sequence(getPropAppearTrack(can, suit.getRightHand(), posPoints, propDelay, Point3(9, 9, 9), scaleUpTime=0.25))
explodePosPoints = [Point3(0, 0, 0), MovieUtil.PNT3_ZERO]
splatName = 'dust'
        splat = globalPropPool.getProp('dust')
        explode = globalPropPool.getProp('dust')
        explode.setTwoSided(True)
explode.setBillboardPointWorld(2)
        explodeTrack = Sequence()
        explodeTrack.append(
            getPropAppearTrack(explode, toon, explodePosPoints, 0, Point3(2, 2, 2), scaleUpTime=0))
        explodeTrack.append(Sequence(ActorInterval(explode, splatName), Func(explode.detachNode)))

battle = attack['battle']
target = attack['target']
    toon = target['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)

spinTrack = Sequence(Wait(propDelay + suitDelay), LerpHprInterval(paper, throwDuration, Point3(0, 0, 0)))
    sizeTrack = Sequence(Wait(propDelay + suitDelay), LerpScaleInterval(paper, throwDuration, Point3(6, 6, 6)), Wait(0.95), LerpScaleInterval(paper, 0.4, MovieUtil.PNT3_NEARZERO))
    propTrack = Sequence(Parallel(paperTrack, spinTrack, sizeTrack), Func(MovieUtil.removeProp, paper), Func(battle.movie.clearRenderProp, paper))

taunt = random.choice(
        ["A-one! A-two! A skiddly-diddly-doo!", "I assure you, I'm not dancing around the issue.",
         "I'm afraid I have you beat.", "Step, kick, kick, leap, kick, touch... Again!", "Think of this as a dance to the death.",
         "When you feel sad, dance!", "Woah Woah Woah...",
         "It's like dreaming with your feet."])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))

suitTrack = Sequence(headsUp, tauntInterval, ActorInterval(suit, 'song-and-dance', playRate=1.25), suitReset, Func(suit.setNeutralAnimation))

elif dmg > 0 and suit.isChainsawPhase2:
animTrack.append(
    getToonTakeDamageTrack(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims,
                           showDamageExtraTime))
taunt = random.choice(
    ["DAMAGE TO SHELL IDENTIFIED. RETALIATION WILL BE MET WITH EQUAL FORCE.",
     "OUTER LAYERS AT RISK. TAKING DEFENSIVE ACTION.",
     "THREATS HAVE BEGUN TO ADVANCE. BEGIN INCREASING ATTACK POWER."])
animTrack.append(Func(suit.setChatAbsolute,
                      taunt,
                      CFSpeech | CFTimeout))
animTrack.append(Func(suit.showHpString, "1.05x DMG MULTIPLIER!"))
animTrack.append(Parallel(SoundInterval(base.loadSfx('phase_5/audio/sfx/SA_revving_up.ogg')),
                          ActorInterval(suit, 'revvedup', playRate=suit.getPlayRate('revvedup'))))
animTrack.append(Func(suit.setPlayRate, suit.getPlayRate() + 0.1, 'revvedup'))
animTrack.append(Func(suit.setNeutralAnimation))
return animTrack
elif dmg > 0 and suit.isChainsawPhase3:
animTrack.append(
    getToonTakeDamageTrack(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims,
                           showDamageExtraTime))
taunt = random.choice(
    ["DAMAGE TO SHELL- increasing- IDENTIFIED. RETALIATION SHALL BE MET WITH- power- EQUAL FORCE.",
     "OUTER LAYERS AT- getting- RISK. TAKING DEFENSIVE- faster- ACTION.",
     "THREATS HAVE- i have- BEGUN TO- been- ADVANCE. BEGIN- hit- INCREASING ATTACK POWER.", ])
animTrack.append(Func(suit.setChatAbsolute,
                      taunt,
                      CFSpeech | CFTimeout))
animTrack.append(Func(suit.showHpString, "1.1x DMG MULTIPLIER!"))
for headPart in suit.animatedHeadParts:
    headInterval = ActorInterval(headPart, 'revvedup', playRate=suit.getPlayRate('revvedup'))
animTrack.append(Parallel(headInterval, SoundInterval(base.loadSfx('phase_5/audio/sfx/SA_revving_up.ogg')),
                          ActorInterval(suit, 'revvedup', playRate=suit.getPlayRate('revvedup'))))
animTrack.append(Func(suit.setPlayRate, suit.getPlayRate() + 0.1, 'revvedup'))
animTrack.append(Func(suit.setChatAbsolute, '', CFSpeech | CFTimeout))
animTrack.append(Func(suit.setNeutralAnimation))
return animTrack


suitTrack.append(Func(suit.setHealthForMe, 50))
elif name == CHAINSAW_DETONATE_3:
suitTrack = doFallingKnifePromotion(attack)
elif name == BOMB_CAKE:
suitTrack = doCloseTheLoopBombCake(attack)
elif name == CHAINSAW_CANNED:
suitTrack = doBlueChipSnipe(attack)
elif name == TRIBUTE_2:
suitTrack = doTeeOffTrap(attack)
elif name == SLUSHFUND_2:
suitTrack = doPinkSlipSnipe(attack)
elif name == CAGE:
suitTrack = doPinkSlipCage(attack)
elif name == STAND_UP_GUY:
suitTrack = doCloseTheLoopPhase2(attack)
elif name == NOT_THROW_PIANO:
suitTrack = doCloseTheLoopPiano(attack)
elif name == DETONATE_2:
suitTrack = doPinkSlipAftershock(attack)

dosnipechairman

gearPoint = Point3(suitPos.getX(), suitPos.getY() - 10, suitPos.getZ() + suit.height - 0.2)
explosionTrack = Sequence()
explosionTrack.append(Wait(4.0))
explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))

camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=3),
                             defaultCamera(attackDuration=5, openShotDuration=3),
                             randomActorShot(suit, battle, attackDuration - 10, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack3 = pbpText.getShowInterval('Pink Slip!', 3.5)
        pbpDesc2 = Sequence(Wait(6.0),
                            pbpDc.getShowIntervalDesc("The Chairman retaliates when zapped!",
                                                      3.5))
        pbpTrack2 = Sequence(Wait(6.0), pbpText.getShowIntervalCheat('Aftershock!', 3.5))
        pbpDesc = Sequence(Wait(10.0), (
            pbpDc.getShowIntervalDesc('The Chairman bans Zap for 2 turns!', 3.5)))
        pbpTrack = Sequence(Wait(10.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack3, pbpTrack, pbpDesc, camTrack2)




camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=2),
                             randomActorShot(suit, battle, attackDuration - 5, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Tabulate!', 3.5)
        pbpDesc = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc('Level 6 and 8 gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        if attack['suit'].dna.name == 'dvk':
            return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(defaultCamera(openShotDuration=2.0))

ceaseTrack = ActorInterval(suit, 'cease')
ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                 "So, I see you are very reliant on your Trap gags. Let's see how you do without them.",
                                 CFSpeech | CFTimeout))
if attack['suit'].dna.name == 'tcm':
    suitTrack.append(Wait(1.0))
    suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))



ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Level 5 and 8 gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'dvk':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))

taunt = random.choice(
    ["DAMAGE TO SHELL IDENTIFIED. RETALIATION WILL BE MET WITH EQUAL FORCE.",
     "OUTER LAYERS AT RISK. TAKING DEFENSIVE ACTION.",
     "THREATS HAVE BEGUN TO ADVANCE. BEGIN INCREASING ATTACK POWER."])
suitTrack.append(Wait(3.0))
suitTrack.append(Func(suit.setChatAbsolute,
                      taunt,
                      CFSpeech | CFTimeout))
suitTrack.append(Func(suit.showHpString, "1.05x DMG MULTIPLIER!"))
suitTrack.append(Parallel(headInterval2, SoundInterval(base.loadSfx('phase_5/audio/sfx/SA_revving_up.ogg')),
                          ActorInterval(suit, 'revvedup')))
suitTrack.append(Func(suit.setNeutralAnimation))




ceaseTrack = ActorInterval(suit, 'cease')
ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                 'Any Toon-Up and Squirt Gags Toons use can and will be held against them in a court of law.',
                                 CFSpeech | CFTimeout))
suitTrack.append(Wait(1.0))
suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))

origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)

calcPropTrack = getPropTrack(calculator, suit.getRightHand(), calcPosPoints, 0, calcDuration,
                                 scaleUpPoint=scaleUpPoint, scaleUpTime=0, anim=1, propName='court-costs-calculator', animStartTime=0,
                                 animDuration=2.9)

toonTrack = getToonTakeDamageTrackCheat(attack, toon, target['died'], int(dmg / 2), 0.8, ['conked'])
notifyTrack = Sequence(Wait(.75), Func(toon.showHpTextCheat, - int(dmg / 2)), Func(toon.showHpString, "SANCTIONED!"))
suitTrack.append(Func(suit.showHpTextCheat, - (dmg * 4)))
suitTrack.append(Func(suit.showHpString, "BELLOW!"))





for suit in battle.activeSuits:
    suitTrack = Sequence()
    suitTrack.append(Wait(3))
    x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
    if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
        suit.setHealthForMe(int(suit.currHP + 0))
        suitTrack.append(Func(suit.showHpText, 0))
    elif suit.currHP + 75 > (suit.maxHP * suit.hardMaxHP):
        suit.setHealthForMe(int(suit.currHP + x))
        suitTrack.append(Func(suit.showHpText, x))
    else:
        suit.setHealthForMe(int(suit.currHP + 75))
        suitTrack.append(Func(suit.showHpText, 75))
    suitTrack.append(Func(suit.updateHealthBar, 0))

    Func(suit.setHealthForMe, int(suit.currHP + x))

 Func(suit.setNeutralAnimation)
Func(suit.setHealthForMe, int(suit.currHP + x)),
suitTrack.append(Func(suit.setHealthForMe,  + x))

targetSuit.setHealthForMe(int(targetSuit.currHP - targetSuit.currHP))
    targetSuit1.setHealthForMe(int(targetSuit1.currHP - targetSuit1.currHP))
    targetSuit2.setHealthForMe(int(targetSuit2.currHP - targetSuit2.currHP))
    targetSuit3.setHealthForMe(int(targetSuit3.currHP - targetSuit3.currHP))
    Func(targetSuit4.setHealthForMe, int(targetSuit4.currHP - targetSuit4.currHP))

resetPos, resetHpr = battle.getActorPosHpr(suit)
    sinkPos = suit.getPos(battle)
    dropPos = suit.getPos(battle)
    sinkPos2 = suit.getPos(battle)
    dropPos2 = suit.getPos(battle)
    sinkPos.setY(sinkPos.getY() + 12.5)
    sinkPos.setZ(sinkPos.getZ() - 4.5)
    sinkPos2.setY(sinkPos.getY() - 22.5)
    moveTrack = Sequence(LerpPosInterval(suit, 1.5, sinkPos2, other=battle), LerpPosInterval(suit, 0, sinkPos, other=battle), Wait(3.9), LerpPosInterval(suit, 0, sinkPos2, other=battle), LerpPosInterval(suit, 1.5, dropPos, other=battle), Func(suit.setPos, battle, dropPos))

    suitTrack = Sequence(ActorInterval(suit, 'walk'), getSuitAnimTrack(attack), ActorInterval(suit, 'walk'))


def doHeadRoller(attack, ind):
    manager = attack['suit']
    battle = attack['battle']
    toons = attack['target']
    targetSuit = battle.activeSuits[ind]

    managerTrack = Sequence(getSuitAnimTrack(attack), Func(manager.loop, 'neutral%s' % ('-hurt' if float(manager.currHP) / float(manager.maxHP) <= 0.25 else '')))
    managerTrack.append(Parallel(Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                       "Someone isn't doing their part around here, your health is now mine.",
                                                       CFSpeech | CFTimeout),
                                       Sequence(Wait(0.5)))))
    suitTrack = Sequence(Wait(1.0), Func(targetSuit.showHpText, "SYPHONED!", 10), ActorInterval(targetSuit, 'soak', duration = 2.25), Sequence(MovieUtil.spawnHeadExplosion(targetSuit, battle)), Func(targetSuit.setChatAbsolute,
                                                       "Ouch.",
                                                       CFSpeech | CFTimeout), Wait(1.0), MovieUtil.createSuitHeadlessDeathTrack(targetSuit, battle))
    selfDamageTrack = Sequence(Wait(2), Func(targetSuit.showHpText, -targetSuit.currHP), Func(targetSuit.updateHealthBar, 0))
    managerHealTrack = Sequence(Wait(2))
    managerHealTrack.append(Wait(8))
    managerHealTrack.append(doWorkersCompensation2(attack, ind))
    #toonTrack = getToonTracks(attack, 7.35, ['cringe'], 2.0, ['neutral'])
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_bash.ogg'), node=targetSuit))
    return Parallel(managerTrack, suitTrack, soundTrack, selfDamageTrack, managerHealTrack)





ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Level 5 and 8 gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'blr':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))


ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Any Level 7 and 8 Gags Toons use can and will be held against them in a court of law.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'ste':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))

for t in attack['target']:
    toon = t['toon']
    duckTracks = Parallel()
    for i in xrange(0, random.randint(7, 10)):
        x = random.random() / 5
        if random.choice([False, True]):
            x *= -1
        y = random.random() / 5
        if random.choice([False, True]):
            y *= -1
        next = loader.loadModel('phase_5/models/props/cc_m_bat_prp_duck_hroller')
        posPoints = [Point3(x, y, -0.5), VBase3(0, 0, 180)]
        duckLandX = (toon.getX(battle) - 0.05) + random.random()
        duckLandY = (toon.getY(battle) - 0.05) + random.random()
        duckTrack = Sequence(
            getPropAppearTrack(next, suit.getRightHand(), posPoints, propDelay, scaleUpPoint=Point3(2.5)),
            Wait(throwDelay - propDelay + random.random()),
            Parallel(
                getThrowTrack(next, Point3(duckLandX, duckLandY + 5, 0.5), parent=battle),
                LerpHprInterval(next, 1.0, VBase3(180, 0, 0)),
                LerpScaleInterval(next, 1.0, Point3(5))
            ),
            squishDuck(next),
            getThrowTrack(next, Point3(duckLandX, duckLandY, 0.5), duration=0.25, parent=battle, gravity=-96.432),
            squishDuck(next),
            getThrowTrack(next, Point3(duckLandX, duckLandY - 5, 0.5), duration=0.25, parent=battle,
                          gravity=-96.432),
            LerpScaleInterval(next, 0.25, Point3(6.25, 6.25, 2.5)),
            LerpScaleInterval(next, 0.25, MovieUtil.PNT3_NEARZERO),
            Func(MovieUtil.removeProp, next)
        )
        duckTracks.append(duckTrack)

    allDuckTracks.append(duckTracks)

if self.battle.activeSuits[i].dna.name == 'blr':
    x = self.TurnsElapsed
    currentBossHealth = -1
    for s in self.battle.suits:
        if s.dna.name == 'dsk' or s.dna.name == 'dvp' or s.dna.name == 'ffm':
            currentBossHealth = s.currHP
    if currentBossHealth == -1 and not self.suitHasCondition(suitId, 'desperation'):
        self.setSuitCondition(suitId, 'desperation', 1, 100, 'setBoth')
    if x % 4 == 0:
        self.setSuitCondition(suitId, 'costscalculator', 1, 10, 'setBoth')
if self.battle.activeSuits[i].dna.name == 'dsk':
    x = self.TurnsElapsed
    currentBossHealth = -1
    for s in self.battle.suits:
        if s.dna.name == 'dvp' or s.dna.name == 'blr' or s.dna.name == 'ffm':
            currentBossHealth = s.currHP
    if currentBossHealth == -1 and not self.suitHasCondition(suitId, 'desperation'):
        self.setSuitCondition(suitId, 'desperation', 1, 100, 'setBoth')
    if x % 3 == 0:
        self.setSuitCondition(suitId, 'insurancecalculator', 1, 10, 'setBoth')
if self.battle.activeSuits[i].dna.name == 'dvp':
    x = self.TurnsElapsed
    currentBossHealth = -1
    for s in self.battle.suits:
        if s.dna.name == 'blr' or s.dna.name == 'dsk' or s.dna.name == 'ffm':
            currentBossHealth = s.currHP
    if currentBossHealth == -1 and not self.suitHasCondition(suitId, 'desperation'):
        self.setSuitCondition(suitId, 'desperation', 1, 100, 'setBoth')
    if x % 4 == 0:
        self.setSuitCondition(suitId, 'costscalculator', 1, 10, 'setBoth')
if self.battle.activeSuits[i].dna.name == 'ffm':
    x = self.TurnsElapsed
    currentBossHealth = -1
    for s in self.battle.suits:
        if s.dna.name == 'blr' or s.dna.name == 'dsk' or s.dna.name == 'dvp':
            currentBossHealth = s.currHP
    if currentBossHealth == -1 and not self.suitHasCondition(suitId, 'desperation'):
        self.setSuitCondition(suitId, 'desperation', 1, 100, 'setBoth')
    if x % 3 == 0 and not self.suitHasCondition(suitId, 'desperation'):
        self.setSuitCondition(suitId, 'costscalculator', 1, 10, 'setBoth')


"There'ff no fun in plaHAHAying it ffafe! Live a little!",
"What'ff life without a little riffk here and there?",
"You'd befft go big or GO HOME!",
"It'ff all or nothing, doll!",
"But what if the fftakeff were EVEN HIGHER?!"


suitTrack = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout),
                         ActorInterval(suit, 'glower'), ActorInterval(suit, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))


card = globalPropPool.getProp('cc_a_prp_bat_playcard')
propTrackNew = Parallel()
propTrackNew.append(Sequence(Wait(5.5),
                            getPropTrack(card, battle, cardPos, 1e-06, 0, scaleUpPoint=scaleUpPoint, scaleUpTime=3,
                                         anim=1, animStartTime=0, animDuration=3.0,
                                         propName='cc_a_prp_bat_playcard'), Wait(1.6)))

elif name == UNION_BUST:
suitTrack = doUnionBust(attack, 2)
elif name == UNION_BUST_2:
suitTrack = doUnionBust(attack, 3)
elif name == UNION_BUST_3:
suitTrack = doUnionBust(attack, 4)

heavyrain2