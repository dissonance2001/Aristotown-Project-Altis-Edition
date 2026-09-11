from toontown.toonbase import ToontownGlobals
from panda3d.core import TextNode

tn = TextNode('widthTest')
tn.setFont(ToontownGlobals.SuitFont)
tn.setWordwrap(999)

tn.setText('Double Crosser')
print('Double Crosser width:', tn.getWidth())

tn.setText('Flunky')
print('Flunky width:', tn.getWidth())

tn.setText("Redd 'Heir' Wing")
print("Redd 'Heir' Wing width:", tn.getWidth())