
from panda3d.core import ConfigVariableBool

if ConfigVariableBool('astron-support', True):
    from direct.distributed.AstronNetMessenger import AstronNetMessenger as NetMessenger
else:
    from direct.distributed.OTPNetMessenger import OTPNetMessenger as NetMessenger
