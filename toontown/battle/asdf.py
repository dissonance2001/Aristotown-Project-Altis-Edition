theSuit = attack['suit']
        hitPoint = suit.getPos(battle)
        hitPoint.setZ(suit.height + 2)
        hitPoint.setY(hitPoint.getY() + 0.5)
        knife = globalPropPool.getProp('shredder-paper')
        knifeTrack = Sequence(
            getPropAppearTrack(knife, theSuit.getRightHand(), posPoints, .5, VBase3(1, 1, 1),
                               scaleUpTime=0.1),
            Wait(2.3),
            Parallel(
                getThrowTrack(knife, hitPoint, 1.5, battle, -30.288),
                LerpHprInterval(knife, 0.8, VBase3(0, -20, -20))),
            Parallel(LerpPosInterval(knife, 1, VBase3(hitPoint.getX(), hitPoint.getY() + 0.5, hitPoint.getZ() - 10)),
                     Sequence(Wait(0.25), LerpScaleInterval(knife, 0.5, VBase3(0, 0, 0)))),
            Func(MovieUtil.removeProp, knife)
        )
        knifeTracks.append(knifeTrack)

self.generateHead3('prethinker', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_prethinker.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)


posPoints = [Point3(-0.25, 0.75, 0), VBase3(90, 0, 0)]
            hitPoint = suit.getPos(battle)
hitPoint.setZ(suit.height + 2)
        hitPoint.setY(hitPoint.getY() + 0.5)
            knife = globalPropPool.getProp('bonus-check')
            knifeTrack = Sequence(
            getPropAppearTrack(knife, theSuit.getRightHand(), posPoints, .5, VBase3(8.5, 8.5, 8.5),
                               scaleUpTime=0.1),
            Wait(2.3),
            Parallel(
                getThrowTrack(knife, hitPoint, 1.5, battle, -30.288),
                LerpHprInterval(knife, 0.8, VBase3(0, 90, 0))),
            Parallel(LerpPosInterval(knife, 1, VBase3(hitPoint.getX(), hitPoint.getY() + 0.5, hitPoint.getZ() - 10)),
                     Sequence(Wait(0.25), LerpScaleInterval(knife, 0.5, VBase3(0, 0, 0)))),
            Func(MovieUtil.removeProp, knife)
        )
        knifeTracks.append(knifeTrack)
            knifeTrack = Sequence(
                getPropAppearTrack(knife, theSuit.getRightHand(), posPoints, .5, Point3(8.5, 8.5, 8.5),
                                   scaleUpTime=0.1),
                Wait(2.3),
                Parallel(
                    getThrowTrack(knife, hitPoint, 1.95, battle, -34.288),
                    LerpHprInterval(knife, 0.8, VBase3(0, 90, 0)),
                    Sequence(Wait(1.25), LerpScaleInterval(knife, .7, VBase3(0, 0, 0)))),
                Func(MovieUtil.removeProp, knife)
            )
            knifeTracks.append(knifeTrack)





cage = loader.loadModel('phase_5/models/props/cc_m_bat_prp_dice')
def doGavel(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target['toon']
    dmg = target['hp']
    gavel = globalPropPool.getProp('LB_gavel')
    toonPos = toon.getPos(battle)
    initialScale = toon.getScale()
    gavelPos = Point3(toonPos.getX(), 2, 0)
    propTrack = Sequence(
        getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos, VBase3(0, 0, 0)], appearDelay=0.0, scaleUpPoint=Point3(1), scaleUpTime=1.5),
        LerpHprInterval(gavel, 0.5, VBase3(0, 90, 0)),
        Parallel(getSoundTrack('LB_gavel.ogg', node=toon), Sequence(
            Wait(0.1),
            LerpHprInterval(gavel, 0.5, VBase3(0, 0, 0)),
            LerpScaleInterval(gavel, 1.5, MovieUtil.PNT3_ZERO)
        ))
    )
    taunt = "Any gags Toons use can and will be held against them in a court of law."
    suitTrack = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout),
                         ActorInterval(suit, 'effort', playRate=1.25))
    toonTrack = Sequence(
            Wait(2.0),
            Parallel(
                Func(toon.enterFlattened),
                Func(toon.showHpText, 0, openEnded=0),
                Func(__doDamage, toon, 0, target['died'])
            ),
            Wait(1.0),
            Parallel(
                Sequence(
                    Wait(0.5),
                    Func(toon.exitFlattened)
                ),
                getSoundTrack('toon_decompress.ogg', node=toon),
                Sequence(
                    ActorInterval(toon, 'jump'),
                    Func(toon.loop, 'neutral')
                )
            )
        )
    return Parallel(suitTrack, toonTrack, propTrack)

def doGavelCourtRecord(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    propTracks = Parallel()
    toonTracks = Parallel()
    for t in targets:
        toon = t['toon']
        gavel = globalPropPool.getProp('LB_gavel')
        dmg = t['hp']
        toonPos = toon.getPos(battle)
        gavelPos = Point3(toonPos.getX(), 2, 0)
        propTrack = Sequence(
            getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos, VBase3(0, 0, 0)], appearDelay=0.0,
                               scaleUpPoint=Point3(1), scaleUpTime=1.5),
            LerpHprInterval(gavel, 0.5, VBase3(0, 90, 0)),
            Parallel(getSoundTrack('LB_gavel.ogg', node=toon), Sequence(
                Wait(0.1),
                LerpHprInterval(gavel, 0.5, VBase3(0, 0, 0)),
                LerpScaleInterval(gavel, 1.5, MovieUtil.PNT3_ZERO)
            ))
        )
        propTracks.append(propTrack)
        toonTrack = Sequence(
            Wait(2.0),
            Parallel(
                Func(toon.enterFlattened),
                Func(toon.showHpText, -dmg, openEnded=0),
                Func(__doDamage, toon, dmg, t['died'])
            ),
            Wait(1.0),
            Parallel(
                Sequence(
                    Wait(0.5),
                    Func(toon.exitFlattened)
                ),
                getSoundTrack('toon_decompress.ogg', node=toon),
                Sequence(
                    ActorInterval(toon, 'jump'),
                    Func(toon.loop, 'neutral')
                )
            )
        )
        toonTracks.append(toonTrack)
    return Parallel(toonTracks, propTracks)


toon = t['toon']
        dmg = t['hp']
        gavel = loader.loadModel('phase_5/models/props/cc_m_bat_prp_dice')
        toonPos = toon.getPos(battle)
        y = toonPos.getY()
        gavelPos = Point3(toonPos.getX(), y, 30)
        propTrack2 = Sequence(
        getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos, VBase3(0, 0, 0)], appearDelay=0.0,
                           scaleUpPoint=Point3(2), scaleUpTime=1.5),
        LerpPosInterval(gavel, 0.25, Point3(toonPos.getX(), y, 2.01)),
        LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y, 3)),
        LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y, 2.01)), Sequence(
            Wait(1.5),
            LerpScaleInterval(gavel, .25, MovieUtil.PNT3_ZERO)
        ))

        propTracks2.append(propTrack2)
        toonTrack2 = Sequence(
        Wait(2.0),
        Parallel(
            Func(toon.enterFlattened),
            Func(toon.showHpText, -dmg, openEnded=0),
            Func(__doDamage, toon, dmg, t['died'])
        ),
        Wait(1.0),
        Parallel(
            Sequence(
                Wait(0.5),
                Func(toon.exitFlattened)
            ),
            getSoundTrack('toon_decompress.ogg', node=toon),
            Sequence(
                ActorInterval(toon, 'jump'),
                Func(toon.loop, 'neutral')
            )
        )
        )
        toonTracks2.append(toonTrack2)