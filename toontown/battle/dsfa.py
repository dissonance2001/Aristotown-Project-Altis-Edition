elif name == POWERHOUSE_ABSORB:
camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
elif name == POWERHOUSE_SOAK_IMMUNE:
camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
elif name == POWERHOUSE_LURE_IMMUNE:
camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
elif name == POWERHOUSE_SYPHON:
camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
elif name == POWERHOUSE_SYPHON_DESPERATION:
camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
elif name == POWERHOUSE_SNIPE_VULNERABLE:
camTrack.append(defaultCamera(openShotDuration=1.5))
elif name == POWERHOUSE_SNIPE_GAG_BAN:
camTrack.append(defaultCamera(openShotDuration=1.5))
elif name == POWERHOUSE_SNIPE_SOAKED:
camTrack.append(defaultCamera(openShotDuration=1.5))
elif name == POWERHOUSE_SNIPE_BOOKKEPT:
camTrack.append(defaultCamera(openShotDuration=1.5))
elif name == POWERHOUSE_SNIPE_MULLIGAN:
camTrack.append(defaultCamera(openShotDuration=1.5))
elif name == POWERHOUSE_SNIPE_COLLECT_CALL:
camTrack.append(defaultCamera(openShotDuration=1.5))
# bookkeeper cheats
elif name == BOOKKEEPER_PAPER_CUT_SOAKED:
camTrack.append(defaultCamera(openShotDuration=0.75))
elif name == BOOKKEEPER_PAPER_CUT_MARKED:
camTrack.append(defaultCamera(openShotDuration=0.75))
elif name == BOOKKEEPER_PAPER_CUT:
camTrack.append(defaultCamera(openShotDuration=0.75))
elif name == BOOKKEEPER_EXPLODING_DOCUMENT:
camTrack.append(defaultCamera(openShotDuration=2.0))
elif name == BOOKKEEPER_BOOKKEEPING_RETALIATION:
camTrack.append(defaultCamera(openShotDuration=3.0))
elif name == BOOKKEEPER_BOOKKEEPING:
camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
# wiretapper cheats
elif name == WIRETAPPER_COLLECT_CALL:
camTrack.append(defaultCamera(openShotDuration=1.0))
elif name == WIRETAPPER_COLLECT_CALL_DOT:
if attackDuration > 2:
    camTrack2 = heldShot(10, 0, 10, 115, -30, 0, attackDuration)
    pbpText = attack['playByPlayText']
    pbpDc = PlayByPlayText.PlayByPlayText()
    pbpDesc = pbpDc.getShowIntervalDesc(
        "This toon is forced to pay collect call fees every turn\nuntil their dues are paid!",
        attackDuration - 2)
    pbpTrack = pbpText.getShowIntervalCheat('Collect Call Dues!', attackDuration - 2)
    return Parallel(pbpTrack, pbpDesc, camTrack2)
else:
    camTrack2 = defaultCamera(openShotDuration=0)
    return camTrack2
elif name == WIRETAPPER_WIRETAPPED:
camTrack.append(defaultCamera(openShotDuration=2.0))
elif name == WIRETAPPER_VOICEMAIL:
camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
elif name == WIRETAPPER_BROKEN_CONNECTION:
camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
# ambassador cheats
elif name == AMBASSADOR_HEAD_ROLLER:
camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
elif name == AMBASSADOR_HEAD_ROLLER_GROUP:
camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
elif name == AMBASSADOR_REFINEMENT:
camTrack.append(Sequence(randomActorShot(suit, battle, 2, 'suit'),
                         moveShot(0.0, -15.0, 10.0, 0, -20, 0, 1.5),
                         heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 3.5)))
elif name == AMBASSADOR_PHASE_2:
camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
elif name == AMBASSADOR_DAMAGE_UP:
camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
elif name == AMBASSADOR_MANAGERIAL_PROTECTION:
camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
elif name == AMBASSADOR_MANAGERIAL_PROTECTION_IMMUNITY:
camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
elif name == AMBASSADOR_MULLIGAN:
camTrack.append(defaultCamera(openShotDuration=1.5))