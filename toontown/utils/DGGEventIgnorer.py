# Since we are binding by press in the inventory so that both left and right
# events can be fired, every event listener must take in the event argument.
# This parameter is seldom useful, so ignore it with this wrapper.
def ignore_event(func):
    def wrapper(*args, **kwargs):
        func(*args[:-1], **kwargs)
    return wrapper
