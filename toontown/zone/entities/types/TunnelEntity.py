from toontown.hood import ZoneUtil
from toontown.level import BasicEntities
from toontown.level.editor import EditorGlobals
from toontown.toonbase import ToontownGlobals


class TunnelEntity(BasicEntities.NodePathEntity):
    """
    TunnelEntity(BasicEntities.NodePathEntity)

    A simple tunnel that allows the player to move between other level zones.
    It can also be used to move between Levels and DNA.
    """

    def __init__(self, level, entId):
        BasicEntities.NodePathEntity.__init__(self, level, entId)
        self.tunnelModel = None
        self.tunnelEventName = None
        self.requestData = {}
        self.initTunnel()

    def destroy(self):
        self.destroyTunnel()
        if self.tunnelEventName:
            self.ignore(self.tunnelEventName)
            self.tunnelEventName = None
        self.requestData = {}
        BasicEntities.NodePathEntity.destroy(self)

    def initTunnel(self):
        self.tunnelModel = loader.loadModel(self.tunnelModelPath)
        self.tunnelModel.flattenLight()
        self.tunnelModel.reparentTo(self)
        self.setupTunnelHooks()

    def setupTunnelHooks(self):
        self.notify.debug("setupTunnelHooks()")
        hoodId = ZoneUtil.getHoodId(self.destinationZone)

        # Get the actual collision sphere node
        linkSphere = self.tunnelModel.find('**/tunnel_trigger')
        # HACK: until cog tunnel trigger is renamed
        if linkSphere.isEmpty():
            linkSphere = self.tunnelModel.find('**/tunnel_sphere')
        if not linkSphere.isEmpty():
            # ...first time through this geometry.
            # Rename it to make it unique
            cnode = linkSphere.node()
            cnode.setName(f'tunnel_trigger_{self.tunnelId}_{self.destinationTunnelId}_{self.destinationZone}')
            # It should be collidable to ghosts too
            cnode.setCollideMask(ToontownGlobals.WallBitmask | ToontownGlobals.GhostBitmask)
        else:
            # We've been through this already (i.e. we may have gone into a building and then went out again).
            linkSphere = self.tunnelModel.find(f'tunnel_trigger_{self.tunnelId}_{self.destinationTunnelId}_{self.destinationZone}')
            if linkSphere.isEmpty():
                self.notify.error('tunnel_trigger not found')

        # Get the actual tunnel_origin
        tunnelOrigin = self.tunnelModel.find('**/tunnel_origin')
        if tunnelOrigin.isEmpty():
            self.notify.error('tunnel_origin not found')
        # Create a place holder node
        tunnelOriginPlaceHolder = render.attachNewNode(f'toph_{self.tunnelId}_{self.destinationTunnelId}_{self.destinationZone}')

        # Set the pos and hpr of the place holder
        tunnelOriginPlaceHolder.setPos(tunnelOrigin.getPos(render))
        tunnelOriginPlaceHolder.setHpr(tunnelOrigin.getHpr(render))

        # We will want to tunnel in.
        # DEV NOTE: This can be a great place to put in custom scenarios for tunnel in loads.
        how = 'TunnelIn'
        self.tunnelEventName = 'enter' + linkSphere.getName()
        self.requestData = {
                'loader': ZoneUtil.getLoaderName(self.destinationZone),
                'where': ZoneUtil.getToonWhereName(self.destinationZone),
                'how': how,
                'hoodId': hoodId,
                'zoneId': self.destinationZone,
                'shardId': None,
                'destinationTunnelId': self.destinationTunnelId,
                'tunnelOrigin': tunnelOriginPlaceHolder,
                'legacyDestination': self.legacyDestination,
            }
        self.accept(self.tunnelEventName, self.handleEnterTunnel)

    def handleEnterTunnel(self, collEntry=None):
        place = base.localAvatar.getPlace()
        if not place:
            return

        place.handleEnterTunnel(self.requestData, collEntry)

    def destroyTunnel(self):
        if self.tunnelModel:
            self.tunnelModel.removeNode()
            self.tunnelModel = None

    if EditorGlobals.wantLevelEditor():
        def attribChanged(self, attrib, value):
            """
            :param attrib:
            :param value:
            """
            self.destroyTunnel()
            self.ignore(self.tunnelEventName)
            self.initTunnel()
