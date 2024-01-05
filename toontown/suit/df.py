if self.style.body == 'a':
    self.generateHead('skullA', animated=True)
    texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                 self.style.dept)
    for headPart in self.headParts:
        texture.setMinfilter(Texture.FTNearestMipmapLinear)
        texture.setMagfilter(Texture.FTNearest)
        headPart.setTexture(texture, 1)
if self.style.body == 'b':
    self.generateHead('skullB', animated=True)
    texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                 self.style.dept)
    for headPart in self.headParts:
        texture.setMinfilter(Texture.FTNearestMipmapLinear)
        texture.setMagfilter(Texture.FTNearest)
        headPart.setTexture(texture, 1)
if self.style.body == 'c':
    self.generateHead('skullC', animated=True)
    texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                 self.style.dept)
    for headPart in self.headParts:
        texture.setMinfilter(Texture.FTNearestMipmapLinear)
        texture.setMagfilter(Texture.FTNearest)
        headPart.setTexture(texture, 1)