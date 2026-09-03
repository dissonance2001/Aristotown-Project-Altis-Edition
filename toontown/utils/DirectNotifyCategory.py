from direct.directnotify import DirectNotifyGlobal


def getNotify(name, info=True, warning=True, debug=False, logging=False):
    """
    Creates a DirectNotify object with sane defaults.
    """
    notify = DirectNotifyGlobal.directNotify.newCategory(name)
    notify.setInfo(info)
    notify.setWarning(warning)
    notify.setDebug(debug)
    notify.setLogging(logging)  # NB: not recommended to enable, generates an empty logfile.
    return notify


def DirectNotifyCategory(info=True, warning=True, debug=False, logging=False):
    """
    A decorator for initializing a DirectNotify category on an object.

    ```
    @DirectNotifyCategory()
    class MainKoala:
        # direct notify category is already assumed from the decorator
        # this line would not be necessary:
        #   notify = DirectNotifyGlobal.directNotify.newCategory('MainKoala')
        ...
    ```
    """
    assert not callable(info), "DirectNotifyCategory.info passed a callable - did you forget to parenthesize?"

    def inner(cls):
        notify = getNotify(cls.__name__, info, warning, debug, logging)
        cls.notify = notify

        return cls

    return inner


__all__ = ('getNotify', 'DirectNotifyCategory', )
