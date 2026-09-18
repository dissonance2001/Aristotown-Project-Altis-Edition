from panda3d.core import NodePath, LoaderOptions, Filename, Character, AnimControlCollection, autoBind
from direct.actor.Actor import Actor
from direct.showbase.Loader import Loader
from toontown.utils.asyncutil.AsyncDirectObject import AsyncDirectObject


class AsyncActor(Actor, AsyncDirectObject):
    """AsyncActor: Extends the Actor's functionality to replace
    the loadModel method, giving it the ability to be ran
    asynchronously.
    """
    AsyncPartClass = None

    def __init__(self, *args, **kwargs):
        Actor.__init__(self, *args, **kwargs)
        AsyncDirectObject.__init__(self)
        self.__asyncPartsLoaded: list = []

    def cleanup(self):
        self.removeAllTasks()
        self.ignoreAll()
        self.__asyncPartsLoaded = []
        AsyncDirectObject.cleanup(self)
        Actor.cleanup(self)

    def asyncPartLoaded(self, asyncPart):
        self.__asyncPartsLoaded.append(asyncPart)
        if len(self.__asyncPartsLoaded) == len([aPart for aPart in self.AsyncPartClass]):
            self.async_loadDone()

    def loadModel(self, modelPath, partName="modelRoot", lodName="lodRoot", copy=True,
                  okMissing=None, autoBindAnims=True, callback=None, extraArgs=None):
        """Actor model loader. Takes a model name (ie file path), a part
        name(defaults to "modelRoot") and an lod name(defaults to "lodRoot").
        """
        assert partName not in self._Actor__subpartDict

        assert self.notify.debug("in loadModel: %s, part: %s, lod: %s, copy: %s" % (modelPath, partName, lodName, copy))

        extraArgs = extraArgs or []

        originallyNodePath = isinstance(modelPath, NodePath)
        if originallyNodePath:
            # If we got a NodePath instead of a string, use *that* as
            # the model directly.
            if copy:
                model = modelPath.copyTo(NodePath())
            else:
                model = modelPath
            self.callback_loadModel(model, modelPath, partName, lodName, autoBindAnims, callback, extraArgs, originallyNodePath)
        else:
            # otherwise, we got the name of the model to load.
            loaderOptions = self.modelLoaderOptions
            if not copy:
                # If copy = 0, then we should always hit the disk.
                loaderOptions = LoaderOptions(loaderOptions)
                loaderOptions.setFlags(loaderOptions.getFlags() & ~LoaderOptions.LFNoRamCache)

            if okMissing is not None:
                if okMissing:
                    loaderOptions.setFlags(loaderOptions.getFlags() & ~LoaderOptions.LFReportErrors)
                else:
                    loaderOptions.setFlags(loaderOptions.getFlags() | LoaderOptions.LFReportErrors)

            # Ensure that custom Python loader hooks are initialized.
            Loader._loadPythonFileTypes()

            # Pass loaderOptions to specify that we want to
            # get the skeleton model.  This only matters to model
            # files (like .mb) for which we can choose to extract
            # either the skeleton or animation, or neither.

            loadReq = base.asyncRequestMgr.loadModel(str(Filename(modelPath)), lambda model: self.callback_loadModel(model, modelPath, partName, lodName, autoBindAnims, callback, extraArgs, originallyNodePath), loaderOptions=loaderOptions)
            self.async_loadRequests.append(loadReq)

    def callback_loadModel(self, model, modelPath, partName, lodName, autoBindAnims,
                           callback=None, extraArgs=None, originallyNodePath=False):
        if not originallyNodePath:
            model = NodePath(model)

        if model.node().isOfType(Character.getClassType()):
            bundleNP = model
        else:
            bundleNP = model.find("**/+Character")

        if bundleNP.isEmpty():
            self.notify.warning("%s is not a character!" % (modelPath))
            model.reparentTo(self.getGeomNode())
        else:
            # Maybe the model file also included some animations.  If
            # so, try to bind them immediately and put them into the
            # animControlDict.
            if autoBindAnims:
                acc = AnimControlCollection()
                autoBind(model.node(), acc, ~0)
                numAnims = acc.getNumAnims()
            else:
                numAnims = 0

            # Now extract out the Character and integrate it with
            # the Actor.

            if lodName != "lodRoot":
                # parent to appropriate node under LOD switch
                bundleNP.reparentTo(self._Actor__LODNode.find(str(lodName)))
            else:
                bundleNP.reparentTo(self.getGeomNode())
            self._Actor__prepareBundle(bundleNP, model.node(), partName, lodName)

            # we rename this node to make Actor copying easier
            bundleNP.node().setName(f"{self.partPrefix}{partName}")

            if numAnims != 0:
                # If the model had some animations, store them in the
                # dict so they can be played.
                self.notify.debug("model contains %s animations." % (numAnims))

                # make sure this lod is in anim control dict
                if self.mergeLODBundles:
                    lodName = 'common'
                animControlDict = self.getAnimControlDict()
                animControlDict.setdefault(lodName, {})
                animControlDict[lodName].setdefault(partName, {})

                for i in range(numAnims):
                    animControl = acc.getAnim(i)
                    animName = acc.getAnimName(i)

                    animDef = self.AnimDef()
                    animDef.animBundle = animControl.getAnim()
                    animDef.animControl = animControl
                    animControlDict[lodName][partName][animName] = animDef

        if callback:
            callback(*extraArgs)
