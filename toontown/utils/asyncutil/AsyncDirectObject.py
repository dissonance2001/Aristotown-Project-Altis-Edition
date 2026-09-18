from direct.showbase.DirectObject import DirectObject
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

from typing import List, Tuple, Dict


@DirectNotifyCategory()
class AsyncDirectObject(DirectObject):
    def __init__(self):
        self.async_isLoaded = False
        # List [Function, args, kwargs, priority]
        self.async_loadCallbacks: List[Tuple[callable, Tuple, Dict, int]] = []
        self.async_addedWaitGenerateTask = False
        self.async_loadRequests: list = []

    def cleanup(self):
        self.removeAllTasks()
        self.async_clearLoadRequests()
        self.async_isLoaded = False
        self.async_loadCallbacks = []
        self.async_addedWaitGenerateTask = False

    def async_clearLoadRequests(self):
        for loadReq in self.async_loadRequests:
            if loadReq:
                loadReq.cancel()
        self.async_loadRequests = []

    def async_addLoadCallback(self, callbackFunc: callable, *callbackArgs, **callbackKwargs):
        """
        Adds a load callback to the async object.
        Load callbacks should only be added on the main thread (default task chain).
        """

        # First check to see if we have a custom priority for
        # when this callback should be ran in relation to others
        asyncPriority = 0
        if 'asyncPriority' in callbackKwargs:
            asyncPriority = callbackKwargs.pop('asyncPriority')

        if self.async_isLoaded:
            # Instantly call callback if already async loaded
            callbackFunc(*callbackArgs, **callbackKwargs)
        else:
            # Not done async loading, add done callbacks
            self.async_loadCallbacks.append((callbackFunc, callbackArgs, callbackKwargs, asyncPriority))
            # Add a task to wait for the object to be done generating, check ASAP
            if not self.async_addedWaitGenerateTask:
                self.async_addedWaitGenerateTask = True
                self.addTask(self.__async_checkGenerateTask, name=self.async_waitForGenerateTaskName)

    def __async_checkGenerateTask(self, task=None):
        if not self.async_isLoaded:
            return task.cont

        self.__async_runLoadCallbacks()
        return task.done

    def __async_runLoadCallbacks(self):
        # Run through each load callback and call them with their relevant args/kwargs, sorted by priority.
        for loadCallback, args, kwargs, _ in sorted(self.async_loadCallbacks, key=lambda x: x[3], reverse=True):
            loadCallback(*args, **kwargs)
        self.async_loadCallbacks = []

    @property
    def async_waitForGenerateTaskName(self):
        return f'AsyncDirectObject-WaitForGenerate-{id(self)}'

    @property
    def async_abortEventName(self):
        return f'AsyncDirectObject-Abort-{id(self)}'

    def async_abort(self):
        messenger.send(self.async_abortEventName)

    def async_loadDone(self):
        # Mark the async load as finished.
        # This will later on trigger the callbacks on the main thread.
        self.async_isLoaded = True
