def doGolfAreaAttack(self):
    toons = []
    for toonId in self.involvedToons:
        toon = base.cr.doId2do.get(toonId)
        if toon:
            toons.append(toon)

    if not toons:
        return

    neutral = 'Fb_neutral'
    if not self.twoFaced:
        neutral = 'Ff_neutral'

    if not self.raised:
        neutral1Anim = self.getAnim('down2Up')
        self.raised = 1
    else:
        neutral1Anim = ActorInterval(self, neutral, startFrame=48)

    throwAnim = self.getAnim('areaAttack')
    neutral2Anim = ActorInterval(self, neutral)
    extraAnim = Sequence()
    if False:
        extraAnim = ActorInterval(self, neutral)

    gearModel = self.getGearFrisbee()
    gearModel.setScale(0.2)
    gearRoots = []
    allGearTracks = Parallel()
    for toon in toons:
        gearRoot = self.rotateNode.attachNewNode('gearRoot-atk%d' % (toons.index(toon)))
        gearRoot.setZ(10)
        toToonH = PythonUtil.fitDestAngle2Src(0, gearRoot.getH() + 180)
        gearRoot.setTag('attackCode', str(ToontownGlobals.BossCogGolfAreaAttack))
        gearRoot.lookAt(toon)
        gearTrack = Parallel()
        for i in xrange(10):
            nodeName = '%s-%s' % (str(i), globalClock.getFrameTime())
            node = gearRoot.attachNewNode(nodeName)
            node.hide()
            node.wrtReparentTo(gearRoot)
            distance = toon.getDistance(node)
            toonPos = toon.getPos(render)
            nodePos = node.getPos(render)
            vector = toonPos - nodePos
            gear = gearModel.instanceTo(node)
            x = random.uniform(-5, 5)
            z = random.uniform(-3, 3)
            p = random.uniform(-720, -90)
            y = distance + random.uniform(5, 15)
            if i == 2:
                x = 0
                z = 0
                y = distance + 10

            def detachNode(node):
                if not node.isEmpty():
                    node.detachNode()
                return Task.done

            def detachNodeLater(node=node):
                if node.isEmpty():
                    return
                node.node().setBounds(BoundingSphere(Point3(0, 0, 0), distance * 1.5))
                node.node().setFinal(1)
                self.doMethodLater(0.005, detachNode, 'detach-%s-%s' % (gearRoot.getName(), node.getName()),
                                   extraArgs=[node])

            gearTrack.append(Sequence(Wait(26.0 / 24.0), Wait(i * 0.15), Func(node.show),
                                      Parallel(node.posInterval(1, Point3(x, y, z), fluid=1),
                                               node.hprInterval(1, VBase3(0, p, 0), fluid=1)),
                                      Func(detachNodeLater)))

        allGearTracks.append(gearTrack)

    def detachGearRoots(gearRoots=gearRoots):
        for gearRoot in gearRoots:

            def detachGearRoot(task, gearRoot=gearRoot):
                if not gearRoot.isEmpty():
                    gearRoot.detachNode()
                return task.done

            if gearRoot.isEmpty():
                continue
            self.doMethodLater(0.01, detachGearRoot, 'detach-%s' % gearRoot.getName())

        gearRoots = []

    rotateFire = Parallel(self.pelvis.hprInterval(2, VBase3(toToonH + 1440, 0, 0)), allGearTracks)
    seq = Sequence(Func(base.playSfx, self.warningSfx),
                   ParallelEndTogether(self.pelvis.hprInterval(2, VBase3(toToonH, 0, 0)), neutral1Anim), extraAnim,
                   Parallel(Sequence(rotateFire, Func(detachGearRoots), Func(self.pelvis.setHpr, VBase3(0, 0, 0))),
                            Sequence(throwAnim, neutral2Anim), Sequence(Wait(0.85),
                                                                        SoundInterval(self.swingClubSfx, node=self,
                                                                                      duration=0.45, cutOff=300,
                                                                                      listenerNode=base.localAvatar))))
    self.doAnimate(seq, now=1, raised=1)