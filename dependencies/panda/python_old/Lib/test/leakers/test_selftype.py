# Reference cycles involving only the ob_type field are rather uncommon
# but possible.  Inspired by SF bug 1469629.

from __future__ import absolute_import
import gc
import six

def leak():
    class T(type):
        pass
    class U(six.with_metaclass(T, type)):
        pass
    U.__class__ = U
    del U
    gc.collect(); gc.collect(); gc.collect()
