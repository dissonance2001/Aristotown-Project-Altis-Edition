import inspect
from direct.gui import DirectGuiGlobals as DGG
t = base.transitions
print(type(t), inspect.getsourcefile(type(t)))
f = aspect2d.find('**/DirectFrame-fade')
d = aspect2d.find('**/DirectDialog-pg186')
print('fade  sort/bin:', f.getSort(), f.getBinName(), f.getBinDrawOrder())
print('dialog sort/bin:', d.getSort(), d.getBinName(), d.getBinDrawOrder())
print(DGG.FADE_SORT_INDEX, DGG.NO_FADE_SORT_INDEX)