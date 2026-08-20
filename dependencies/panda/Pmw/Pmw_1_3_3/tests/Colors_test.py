# Tests for Pmw color handling.

from __future__ import absolute_import
import six.moves.tkinter
import Test
import Pmw
from six.moves import map

Test.initialise()
testData = ()

defaultPalette = Pmw.Color.getdefaultpalette(Test.root)

c = six.moves.tkinter.Button

colors = ('red', 'orange', 'yellow', 'green', 'blue', 'purple', 'white')
normalcolors = list(map(Pmw.Color.changebrightness,
	(Test.root,) * len(colors), colors, (0.85,) * len(colors)))

kw = {}
tests = (
  (Pmw.Color.setscheme, (Test.root, normalcolors[0]), {'foreground' : 'white'}),
)
testData = testData + ((c, ((tests, kw),)),)

for color in normalcolors[1:]:
    kw = {'text' : color}
    tests = (
      (c.pack, ()),
      ('state', 'active'),
    )
    testData = testData + ((c, ((tests, kw),)),)

    kw = {}
    tests = (
      (Pmw.Color.setscheme, (Test.root, color), {'foreground' : 'red'}),
    )
    testData = testData + ((c, ((tests, kw),)),)

# Restore the default colors.
kw = {}
tests = (
  (Pmw.Color.setscheme, (Test.root,), defaultPalette),
)
testData = testData + ((c, ((tests, kw),)),)

if __name__ == '__main__':
    Test.runTests(testData)
