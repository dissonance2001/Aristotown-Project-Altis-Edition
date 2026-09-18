GlobalAsyncManagerTaskName = 'AsyncManager-Global-loadNext'
GlobalAsyncManagerTaskActive = False
GlobalAsyncManagerRequests = []
GlobalAsyncManagerRequestsProcessing = []


class AsyncRequestCallback:
    def __init__(self, modelPath, cb, loaderOptions, *cbArgs, **cbKwargs):
        self.modelPath = modelPath
        self.cb = cb
        self.loaderOptions = loaderOptions
        self.cbArgs = cbArgs
        self.cbKwargs = cbKwargs
        self.processing_callback = None

    def processCallback(self):
        def doCallback(model, self=self):
            self.cb(model, *self.cbArgs, **self.cbKwargs)
            self.finishRequest()

        self.processing_callback = loader.loadModelRaw(self.modelPath, callback=doCallback, loaderOptions=self.loaderOptions)
        if not self.processing_callback:
            self.finishRequest()

    def finishRequest(self):
        if self in GlobalAsyncManagerRequests:
            GlobalAsyncManagerRequests.remove(self)
        if self in GlobalAsyncManagerRequestsProcessing:
            GlobalAsyncManagerRequestsProcessing.remove(self)

        if not len(GlobalAsyncManagerRequests):
            stopGlobalLoadTask()

    def cancel(self):
        if self.processing_callback:
            self.processing_callback.cancel()
            self.processing_callback = None
        self.finishRequest()


def stopGlobalLoadTask():
    taskMgr.remove(GlobalAsyncManagerTaskName)
    global GlobalAsyncManagerTaskActive
    GlobalAsyncManagerTaskActive = False


def handleNextAsyncRequest(task):
    global GlobalAsyncManagerRequests
    if not loader.inBulkBlock:
        nextRequest = GlobalAsyncManagerRequests.pop(0)
        GlobalAsyncManagerRequestsProcessing.append(nextRequest)
        nextRequest.processCallback()
        if not len(GlobalAsyncManagerRequests):
            stopGlobalLoadTask()

    return task.cont


def startGlobalLoadTask():
    taskMgr.add(handleNextAsyncRequest, name=GlobalAsyncManagerTaskName)
    global GlobalAsyncManagerTaskActive
    GlobalAsyncManagerTaskActive = True


def addAsyncRequest(callbackObj):
    GlobalAsyncManagerRequests.append(callbackObj)
    global GlobalAsyncManagerTaskActive
    if not GlobalAsyncManagerTaskActive:
        startGlobalLoadTask()


def loadModel(modelPath, callback, loaderOptions=None, *cbArgs, **cbKwargs) -> AsyncRequestCallback:
    asyncRequestCallback = AsyncRequestCallback(modelPath, callback, loaderOptions=loaderOptions, *cbArgs, **cbKwargs)
    addAsyncRequest(asyncRequestCallback)
    return asyncRequestCallback
