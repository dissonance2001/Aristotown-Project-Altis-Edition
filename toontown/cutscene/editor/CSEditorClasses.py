class CSEditorException(Exception):
    pass


class EventArgument(object):
    def __init__(self, kwarg=None, name='Undefined', type=None, default=None):
        self.kwarg = kwarg
        self.name = name
        self.type = type
        self.default = default
