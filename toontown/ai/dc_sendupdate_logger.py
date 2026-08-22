# dc_sendupdate_logger.py  (v2)
#
# Diagnostic patch for the "Unable to decode UTF-8 string; use blob type
# for binary data" assertion in dcPacker.cxx.
#
# v1 only wrapped sendUpdate() and generateWithRequired(), and missed
# helper methods like sendUpdateToAvatarId / sendUpdateToAccountId /
# sendUpdateToChannel, which build their own datagrams without calling
# sendUpdate(). This version instead auto-discovers and wraps EVERY
# method whose name matches the send/generate family, using a generic
# *args/**kwargs wrapper so it can't break method signatures it doesn't
# know about.
#
# USAGE: identical to before -- overwrite the old dc_sendupdate_logger.py
# with this file (same filename), no other changes needed. Delete the old
# dc_sendupdate_log.txt first so you're only looking at the new run.

import io
import os

_LOG_PATH = os.path.join(os.getcwd(), 'dc_sendupdate_log.txt')
_log_file = None


def _get_log():
    global _log_file
    if _log_file is None:
        _log_file = io.open(_LOG_PATH, 'a', encoding='utf-8', errors='backslashreplace')
        _log_file.write(u'\n--- new session ---\n')
        _log_file.flush()
    return _log_file


def _check_value(v, depth=0):
    """Return (display_string, is_flagged) for a value, recursing into
    lists/tuples since args are often passed as a single list."""
    if depth > 4:
        return ('<nested too deep>', False)
    if isinstance(v, bytes):
        try:
            v.decode('utf-8')
            return ('bytes(%r)' % (v[:80],), False)
        except UnicodeDecodeError:
            return ('bytes(%r)[INVALID-UTF8]' % (v[:80],), True)
    if isinstance(v, str):
        try:
            v.encode('utf-8')
            return ('str(%r)' % (v[:80],), False)
        except UnicodeEncodeError:
            return ('str(%r)[INVALID-UTF8]' % (v[:80],), True)
    if isinstance(v, (list, tuple)):
        flagged = False
        parts = []
        for item in v[:40]:
            s, f = _check_value(item, depth + 1)
            parts.append(s)
            flagged = flagged or f
        return ('[' + ', '.join(parts) + ']', flagged)
    try:
        return (repr(v)[:120], False)
    except Exception as e:
        return ('<unreprable: %s>' % e, False)


def _safe_repr_args(args, kwargs):
    parts = []
    any_flag = False
    for a in args:
        s, f = _check_value(a)
        parts.append(s)
        any_flag = any_flag or f
    for k, v in kwargs.items():
        s, f = _check_value(v)
        parts.append('%s=%s' % (k, s))
        any_flag = any_flag or f
    marker = u'   <<<<< LIKELY CULPRIT' if any_flag else u''
    return u', '.join(parts) + marker


def _wrap_method(cls, methodName):
    if not hasattr(cls, methodName):
        return False
    original = getattr(cls, methodName)
    if not callable(original):
        return False

    def wrapper(self, *args, **kwargs):
        log = _get_log()
        doId = getattr(self, 'doId', '?')
        clsName = self.__class__.__name__
        log.write(u'%s.%s doId=%s args=[%s]\n' % (
            clsName, methodName, doId, _safe_repr_args(args, kwargs)))
        log.flush()
        return original(self, *args, **kwargs)

    try:
        setattr(cls, methodName, wrapper)
    except (AttributeError, TypeError):
        return False
    return True


def install():
    """Auto-discover and monkeypatch every method on the AI-side
    distributed-object / repository classes whose name looks like it
    sends a DC update or generates an object, so we catch the field
    write no matter which helper method it goes through."""
    targets = []

    try:
        from direct.distributed.DistributedObjectAI import DistributedObjectAI
        targets.append(DistributedObjectAI)
    except ImportError:
        pass
    try:
        from direct.distributed.DistributedObjectGlobalAI import DistributedObjectGlobalAI
        targets.append(DistributedObjectGlobalAI)
    except ImportError:
        pass
    try:
        from direct.distributed.ConnectionRepository import ConnectionRepository
        targets.append(ConnectionRepository)
    except ImportError:
        pass
    try:
        from direct.distributed.AIRepositoryBase import AIRepositoryBase
        targets.append(AIRepositoryBase)
    except ImportError:
        pass

    patched_count = 0
    patched_names = set()
    for cls in targets:
        if getattr(cls, '_dc_logger_patched', False):
            continue
        for methodName in dir(cls):
            lname = methodName.lower()
            if not (lname.startswith('sendupdate') or
                    'generatewithrequired' in lname or
                    lname.startswith('sendgenerate')):
                continue
            if _wrap_method(cls, methodName):
                patched_count += 1
                patched_names.add(methodName)
        cls._dc_logger_patched = True

    if patched_count:
        print('[dc_sendupdate_logger] installed on %d methods: %s -- logging to %s' % (
            patched_count, sorted(patched_names), _LOG_PATH))
    else:
        print('[dc_sendupdate_logger] WARNING: nothing patched, check import paths')
