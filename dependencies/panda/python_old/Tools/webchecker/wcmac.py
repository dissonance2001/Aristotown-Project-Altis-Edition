from __future__ import absolute_import
import webchecker, sys
from six.moves import input
webchecker.DEFROOT = "http://www.python.org/python/"
webchecker.MAXPAGE = 50000
webchecker.verbose = 2
sys.argv.append('-x')
webchecker.main()
input("\nCR to exit: ")
