from direct.directnotify import DirectNotifyGlobal
from direct.showbase import DirectObject
from pandac.PandaModules import *
import random
from toontown.hood import ZoneUtil
from toontown.toonbase import ToontownGlobals

class HoodMgr(DirectObject.DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('HoodMgr')

    ToontownCentralInitialDropPoints = (
        [-90.7, -60, 0.025, 102.575, 0, 0],
        [-91.4, -40.5, -3.948, 125.763, 0, 0],
        [-107.8, -17.8, -1.937, 149.456, 0, 0],
        [-108.7, 12.8, -1.767, 158.756, 0, 0],
        [-42.1, -22.8, -1.328, -248.1, 0, 0],
        [-35.2, -60.2, 0.025, -265.639, 0, 0]
    )
    ToontownCentralHQDropPoints = (
        [-43.5, 42.6, -0.55, -100.454, 0, 0],
        [-53.0, 12.5, -2.948, 281.502, 0, 0],
        [-40.3, -18.5, -0.913, -56.674, 0, 0],
        [-1.9, -37.0, 0.025, -23.43, 0, 0],
        [1.9, -5.9, 4, -37.941, 0, 0]
    )
    ToontownCentralTunnelDropPoints = (
        [-28.3, 40.1, 0.25, 17.25, 0, 0],
        [-63.75, 58.96, -0.5, -23.75, 0, 0],
        [-106.93, 17.66, -2.2, 99, 0, 0],
        [-116.0, -21.5, -0.038, 50, 0, 0],
        [74.88, -115, 2.53, -224.41, 0, 0],
        [30.488, -101.5, 2.53, -179.23, 0, 0]
    )
    dropPoints = {
        ToontownGlobals.DonaldsDock: (
            (-28, -2.5, 5.8, 120, 0, 0),
            (-22, 13, 5.8, 155.6, 0, 0),
            (67, 47, 5.7, 134.7, 0, 0),
            (62, 19, 5.7, 97, 0, 0),
            (66, -27, 5.7, 80.5, 0, 0),
            (-114, -7, 5.7, -97, 0, 0),
            (-108, 36, 5.7, -153.8, 0, 0),
            (-116, -46, 5.7, -70.1, 0, 0),
            (-63, -79, 5.7, -41.2, 0, 0),
            (-2, -79, 5.7, 57.4, 0, 0),
            (-38, -78, 5.7, 9.1, 0, 0),
        ),
        ToontownGlobals.ToontownCentral: (
            (-60, -8, 1.3, -90, 0, 0),
            (-66, -9, 1.3, -274, 0, 0),
            (17, -28, 4.1, -44, 0, 0),
            (74.34, -25.42, 4, 330, 0, 0),
            (-9.6, 61.1, 0, 132, 0, 0),
            (-109.0, -2.5, -1.656, -90, 0, 0),
            (-35.4, -81.3, 0.5, -4, 0, 0),
            (-103, 72, 0, -141, 0, 0),
            (93.5, -148.4, 2.5, 43, 0, 0),
            (25, 123.4, 2.55, 272, 0, 0),
            (48, 39, 4, 201, 0, 0),
            (-80, -61, 0.1, -265, 0, 0),
            (-46.875, 43.68, -1.05, 124, 0, 0),
            (34, -105, 2.55, 45, 0, 0),
            (16, -75, 2.55, 56, 0, 0),
            (-27, -56, 0.1, 45, 0, 0),
            (-70, 4.6, -1.9, 90, 0, 0),
            (-130.7, 50, 0.55, -111, 0, 0),
        ),
        ToontownGlobals.TheBrrrgh: (
            (35, -32, 6.2, 138, 0, 0),
            (26, -105, 6.2, -339, 0, 0),
            (-29, -139, 6.2, -385, 0, 0),
            (-79, -123, 6.2, -369, 0, 0),
            (-114, -86, 3, -54, 0, 0),
            (-136, 9, 6.2, -125, 0, 0),
            (-75, 92, 6.2, -187, 0, 0),
            (-7, 75, 6.2, -187, 0, 0),
            (-106, -42, 8.6, -111, 0, 0),
            (-116, -44, 8.3, -20, 0, 0),
        ),
        ToontownGlobals.MinniesMelodyland: (
            (86, 44, -13.5, 121.1, 0, 0),
            (88, -8, -13.5, 91, 0, 0),
            (92, -76, -13.5, 62.5, 0, 0),
            (53, -112, 6.5, 65.8, 0, 0),
            (-69, -71, 6.5, -67.2, 0, 0),
            (-75, 21, 6.5, -100.9, 0, 0),
            (-21, 72, 6.5, -129.5, 0, 0),
            (56, 72, 6.5, 138.2, 0, 0),
            (-41, 47, 6.5, -98.9, 0, 0),
        ),
        ToontownGlobals.DaisyGardens: (
            (-0.998, 9.147, 0.025, -5.663, 0, 0),
            (47.207, 51.395, 0.025, -77.411, 0.0, 0.0),
            (113.105, 120.739, 0.025, -33.388, 0.0, 0.0),
            (119.15, 187.219, 0.025, 28.91, 0.0, 0.0),
            (93.115, 240.878, 14.016, -38.148, 0.0, 0.0),
            (71.4, 288.892, 14.025, 44.651, 0.0, 0.0),
            (39.726, 329.26, 13.925, 125.246, 0.0, 0.0),
            (-24.758, 307.053, 14.025, 119.294, 0.0, 0.0),
            (-74.713, 273.668, 14.026, 133.668, 0.0, 0.0),
            (-81.067, 229.671, 14.025, 181.866, 0.0, 0.0),
            (-117.23, 185.184, 0.025, 163.659, 0.0, 0.0),
        ),
        ToontownGlobals.DonaldsDreamland: (
            (77, 91, 0, 124.4, 0, 0),
            (29, 92, 0, -154.5, 0, 0),
            (-28, 49, -16.4, -142, 0, 0),
            (21, 40, -16, -65.1, 0, 0),
            (48, 27, -15.4, -161, 0, 0),
            (-2, -22, -15.2, -132.1, 0, 0),
            (-92, -88, 0, -116.3, 0, 0),
            (-56, -93, 0, -21.5, 0, 0),
            (20, -88, 0, -123.4, 0, 0),
            (76, -90, 0, 11, 0, 0),
        ),
        ToontownGlobals.GoofySpeedway: (
            (-0.7, 62, 0.08, 182, 0, 0),
            (-1, -30, 0.06, 183, 0, 0),
            (-13, -120, 0, 307, 0, 0),
            (16.4, -120, 0, 65, 0, 0),
            (-0.5, -90, 0, 182, 0, 0),
            (-30, -25, -0.373, 326, 0, 0),
            (29, -17, -0.373, 32, 0, 0),
        ),
        ToontownGlobals.YeOlde: (
            (-36.449, -53.55, -5.016, 181.787, 0, 0),
            (115.881, 52.188, 0.86, -226.598, 0, 0),
            (120.179, -54.35, 14.102, 90, 0, 0),
            (36.593, -186.919, -2.467, 45, 0, 0),
            (-62.952, -151.194, -3.482, -45, 0, 0),
            (-115.153, 17.958, -7.647, 180, 0, 0),
            (-175.182, 136.711, -4.937, -135, 0, 0),
            (-123.985, 183.236, -3.998, -163.92, 0, 0),
            (-77.104, 208.237, -6.264, 145, 0, 0),
            (-25.697, 190.629, 5.357, 218.019, 0, 0),
            (103.801, 203.246, 13.022, 190.782, 0, 0),
            (74.949, 109.793, 3.975, 175.186, 0, 0),
            (29.368, 25.597, -4.773, 45.888, 0, 0),
            (29.471, -55.92, -4.823, 180, 0, 0),
        ),
        ToontownGlobals.GolfZone: (
            (-49.6, 102, 0, 162, 0, 0),
            (-22.8, 36.6, 0, 157.5, 0, 0),
            (40, 51, 0, 185, 0, 0),
            (48.3, 122.2, 0, 192, 0, 0),
            (106.3, 69.2, 0, 133, 0, 0),
            (-81.5, 47.2, 0, 183, 0, 0),
            (-80.5, -84.2, 0, 284, 0, 0),
        ),
        ToontownGlobals.OutdoorZone: (
            (-61.973, 93.547, 8.964, 180, 0, 0),
            (-108.504, 29.004, 8.964, 235, 0, 0),
            (12.368, -10.092, 0.025, 145, 0, 0),
            (-14.025, -105.955, 0.025, 45, 0, 0),
            (-57.927, -62.121, 3.88, 250, 0, 0),
        ),
        ToontownGlobals.Tutorial: (
            (130.9, -8.6, -1.3, 105.5, 0, 0),
        ),
        ToontownGlobals.SellbotHQ: (
            (56.91, -173.576, -7.037, 15.061, 0, 0),
            (-53.105, -197.259, -4.812, 25.87, 0, 0),
            (-103, -118, 0.367, 622.422, 0, 0),
            (-5.361, -228.596, -10.817, -118.934, 0, 0),
            (-8.2536, -175.53, -19.5944, -313.592, 0, 0),
            (66.7811, -96.8434, 0.286679, -567.363, 0, 0),
        ),
        ToontownGlobals.CashbotHQ: (
            (91, -427, -23.439, 0, 0, 0),
            (111, -427, -23.439, 0, 0, 0),
            (129, -427, -23.439, 0, 0, 0),
            (146, -427, -23.439, 0, 0, 0),
            (35.131, 265.161, -23.555, 0, 0, 0),
            (188, 344, -23.555, 0, 0, 0),
            (122.708, 505.169, 32.246, 0, 0, 0),
        ),
        ToontownGlobals.LawbotHQ: (
            (-35.432, 21.653, 0, 330.44, 0, 0),
            (-66.767, 115.397, 9.689, 270, 0, 0),
            (-46.02, 165.068, 0, 212, 0, 0),
            (0, 195.095, 19.378, 0, 0, 0),
            (45, 164.014, 0, 157.618, 0, 0),
            (0, 10, 0, 0, 0, 0),
        ),
        ToontownGlobals.BossbotHQ: (
            (11.633, 114.287, 0.025, 243.842, 0, 0),
            (108.612, 115.797, 0.025, 154.363, 0, 0),
            (165.025, 13.956, 0.025, 51.109, 0, 0),
            (152.751, -65.008, 0.025, 87.825, 0, 0),
            (92.445, -109.89, 0.025, -24.941, 0, 0),
            (-8.754, -118.139, 0.025, -27.095, 0, 0),
            (-44.559, -39.683, 0.025, -48.538, 0, 0),
            (-42.851, 29.715, 0.025, -98.688, 0, 0),
            (-18.028, 86.208, 0.025, -136.916, 0, 0),
            (77.135, 53.741, 0.025, -193.584, 0, 0),
        ),
        ToontownGlobals.BoardbotHQ: (
            (0, 0, 0, 0, 0, 0),
        ),
        ToontownGlobals.TechbotHQ: (
            (73.6944, 101.238, -68.818, 180, 0, 0),
        ),
        ToontownGlobals.Toonseltown: (
            (-281.346, 118.352, 50.951, 209.286, 0, 0),
            (-294.247, 125.543, 51.071, 201.03, 0, 0),
            (-277.649, 132.573, 51.089, 200.16, 0, 0),
        ),
        ToontownGlobals.ToontownCentralOld: (
            (-60, -8, 1.3, -90, 0, 0),
            (-66, -9, 1.3, -274, 0, 0),
            (17, -28, 4.1, -44, 0, 0),
            (87.7, -22, 4, 66, 0, 0),
            (-9.6, 61.1, 0, 132, 0, 0),
            (-109.0, -2.5, -1.656, -90, 0, 0),
            (-35.4, -81.3, 0.5, -4, 0, 0),
            (-103, 72, 0, -141, 0, 0),
            (93.5, -148.4, 2.5, 43, 0, 0),
            (25, 123.4, 2.55, 272, 0, 0),
            (48, 39, 4, 201, 0, 0),
            (-80, -61, 0.1, -265, 0, 0),
            (-46.875, 43.68, -1.05, 124, 0, 0),
            (34, -105, 2.55, 45, 0, 0),
            (16, -75, 2.55, 56, 0, 0),
            (-27, -56, 0.1, 45, 0, 0),
            (100, 27, 4.1, 150, 0, 0),
            (-70, 4.6, -1.9, 90, 0, 0),
            (-130.7, 50, 0.55, -111, 0, 0),
        ),
        ToontownGlobals.SkyClan: (
            (-225.757, 6.384, -6.129, -10.348, 0, 0),
            (-214.115, 7.052, -6.129, 26.97, 0, 0),
            (-205.811, 7.252, -6.129, 46.111, 0, 0),
            (-207.663, -3.543, -6.129, 16.679, 0, 0),
            (-218.349, -5.428, -6.129, 1.086, 0, 0),
            (-198.765, 4.83, -6.129, 37.027, 0, 0),
            (-213.455, 46.915, -6.103, 156.676, 0, 0),
            (-200.335, 28.52, -6.128, 107.46, 0, 0),
            (-202.435, 35.676, -6.127, 112.53, 0, 0),
        ),
        ToontownGlobals.MyEstate: (
            (0, 0, 0, 0, 0, 0),
        ),
    }
    DefaultDropPoint = [0, 0, 0, 0, 0, 0]
    hoodName2Id = {
        'dd': ToontownGlobals.DonaldsDock,
        'tt': ToontownGlobals.ToontownCentral,
        'tto': ToontownGlobals.ToontownCentralOld,
        'br': ToontownGlobals.TheBrrrgh,
        'mm': ToontownGlobals.MinniesMelodyland,
        'dg': ToontownGlobals.DaisyGardens,
        'oz': ToontownGlobals.OutdoorZone,
        'ot': ToontownGlobals.YeOlde,
        'ff': ToontownGlobals.FunnyFarm,
        'gs': ToontownGlobals.GoofySpeedway,
        'dl': ToontownGlobals.DonaldsDreamland,
        'bosshq': ToontownGlobals.BossbotHQ,
        'sellhq': ToontownGlobals.SellbotHQ,
        'cashhq': ToontownGlobals.CashbotHQ,
        'lawhq': ToontownGlobals.LawbotHQ,
        'gz': ToontownGlobals.GolfZone,
        'boardhq': ToontownGlobals.BoardbotHQ,
        'techhq':ToontownGlobals.TechbotHQ,
        'ts': ToontownGlobals.Toonseltown,
    }
    hoodId2Name = {
        ToontownGlobals.DonaldsDock: 'dd',
        ToontownGlobals.ToontownCentral: 'tt',
        ToontownGlobals.ToontownCentralOld: 'tto',
        ToontownGlobals.Tutorial: 'tt',
        ToontownGlobals.TheBrrrgh: 'br',
        ToontownGlobals.MinniesMelodyland: 'mm',
        ToontownGlobals.DaisyGardens: 'dg',
        ToontownGlobals.OutdoorZone: 'oz',
        ToontownGlobals.YeOlde: 'ot',
        ToontownGlobals.FunnyFarm: 'ff',
        ToontownGlobals.GoofySpeedway: 'gs',
        ToontownGlobals.DonaldsDreamland: 'dl',
        ToontownGlobals.BossbotHQ: 'bosshq',
        ToontownGlobals.SellbotHQ: 'sellhq',
        ToontownGlobals.CashbotHQ: 'cashhq',
        ToontownGlobals.LawbotHQ: 'lawhq',
        ToontownGlobals.GolfZone: 'gz',
        ToontownGlobals.BoardbotHQ: 'boardhq',
        ToontownGlobals.TechbotHQ: 'techhq',
        ToontownGlobals.Toonseltown: 'ts',
    }
    dbgDropMode = 0
    currentDropPoint = 0

    def __init__(self, cr):
        self.cr = cr

    def getDropPoint(self, dropPointList):
        if self.dbgDropMode == 0:
            return random.choice(dropPointList)
        else:
            droppnt = self.currentDropPoint % len(dropPointList)
            self.currentDropPoint = (self.currentDropPoint + 1) % len(dropPointList)
            return dropPointList[droppnt]

    def getAvailableZones(self):
        if base.launcher == None:
            return self.getZonesInPhase(4) + self.getZonesInPhase(6) + self.getZonesInPhase(8) + self.getZonesInPhase(9) + self.getZonesInPhase(10) + self.getZonesInPhase(11) + self.getZonesInPhase(12) + self.getZonesInPhase(13)
        else:
            zones = []
            for phase in set(ToontownGlobals.phaseMap.values()):
                if base.launcher.getPhaseComplete(phase):
                    zones = zones + self.getZonesInPhase(phase)
            return zones

    def getZonesInPhase(self, phase):
        p = []
        for i in list(ToontownGlobals.phaseMap.items()):
            if i[1] == phase:
                p.append(i[0])
        return p

    def getPhaseFromHood(self, hoodId):
        hoodId = ZoneUtil.getCanonicalHoodId(hoodId)
        return ToontownGlobals.phaseMap[hoodId]

    def getPlaygroundCenterFromId(self, hoodId):
        dropPointList = self.dropPoints.get(hoodId, None)
        if dropPointList:
            return self.getDropPoint(dropPointList)
        else:
            self.notify.warning('getPlaygroundCenterFromId: No such hood name as: ' + str(hoodId))
            return self.DefaultDropPoint

    def getIdFromName(self, hoodName):
        id = self.hoodName2Id.get(hoodName)
        if id:
            return id
        else:
            self.notify.error('No such hood name as: %s' % hoodName)

    def getNameFromId(self, hoodId):
        name = self.hoodId2Name.get(hoodId)
        if name:
            return name
        else:
            self.notify.error('No such hood id as: %s' % hoodId)

    def getFullnameFromId(self, hoodId):
        hoodId = ZoneUtil.getCanonicalZoneId(hoodId)
        return ToontownGlobals.hoodNameMap[hoodId][-1]

    def addLinkTunnelHooks(self, hoodPart, nodeList, currentZoneId):
        tunnelOriginList = []
        for i in nodeList:
            linkTunnelNPC = i.findAllMatches('**/linktunnel*')
            for p in range(linkTunnelNPC.getNumPaths()):
                linkTunnel = linkTunnelNPC.getPath(p)
                name = linkTunnel.getName()
                nameParts = name.split('_')
                hoodStr = nameParts[1]
                zoneStr = nameParts[2]
                hoodId = self.getIdFromName(hoodStr)
                zoneId = int(zoneStr)
                hoodId = ZoneUtil.getTrueZoneId(hoodId, currentZoneId)
                zoneId = ZoneUtil.getTrueZoneId(zoneId, currentZoneId)
                linkSphere = linkTunnel.find('**/tunnel_trigger')
                if linkSphere.isEmpty():
                    linkSphere = linkTunnel.find('**/tunnel_sphere')
                if not linkSphere.isEmpty():
                    cnode = linkSphere.node()
                    cnode.setName('tunnel_trigger_' + hoodStr + '_' + zoneStr)
                    cnode.setCollideMask(ToontownGlobals.WallBitmask | ToontownGlobals.GhostBitmask)
                else:
                    linkSphere = linkTunnel.find('**/tunnel_trigger_' + hoodStr + '_' + zoneStr)
                    if linkSphere.isEmpty():
                        self.notify.error('tunnel_trigger not found')
                tunnelOrigin = linkTunnel.find('**/tunnel_origin')
                if tunnelOrigin.isEmpty():
                    self.notify.error('tunnel_origin not found')
                tunnelOriginPlaceHolder = render.attachNewNode('toph_' + hoodStr + '_' + zoneStr)
                tunnelOriginList.append(tunnelOriginPlaceHolder)
                tunnelOriginPlaceHolder.setPos(tunnelOrigin.getPos(render))
                tunnelOriginPlaceHolder.setHpr(tunnelOrigin.getHpr(render))
                hood = base.cr.playGame.hood
                if ZoneUtil.tutorialDict:
                    how = 'teleportIn'
                    tutorialFlag = 1
                else:
                    how = 'tunnelIn'
                    tutorialFlag = 0
                hoodPart.accept('enter' + linkSphere.getName(), hoodPart.handleEnterTunnel, [{'loader': ZoneUtil.getLoaderName(zoneId),
                  'where': ZoneUtil.getToonWhereName(zoneId),
                  'how': how,
                  'hoodId': hoodId,
                  'zoneId': zoneId,
                  'shardId': None,
                  'tunnelOrigin': tunnelOriginPlaceHolder,
                  'tutorial': tutorialFlag}])

        return tunnelOriginList

    def extractGroupName(self, groupFullName):
        return groupFullName.split(':', 1)[0]

    def makeLinkTunnelName(self, hoodId, currentZone):
        return '**/toph_' + self.getNameFromId(hoodId) + '_' + str(currentZone)
