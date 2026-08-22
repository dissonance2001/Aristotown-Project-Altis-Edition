import random

from panda3d.core import NodePath, NodePathCollection, CullBinManager, CharacterJoint, LineSegs


def removeNoRenders(target=None):
    """
    Searches the scene(or given model) for any nodes with <Tag> norender { 1 } instances & removes them.
    Only used for debugging/prototyping models.

    Don't use this function outside of testing!!

    :param NodePath np: Model, presumably some area model.
    """
    if not target:
        target = render
    for node in target.findAllMatches("**/NORENDER_*"):
        node.removeNode()
    # for node in render.ls():
    #     if node.hasTag("norender"):
    #         print("node %s has norender tag, deleting" % node.getName())
    #         node.removeNode()


def removeCollisionNodes(target=None):
    if target is None:
        target = [render]
    if type(target) is not list:
        target = [target]
    for nodepath in target:
        for node in nodepath.findAllMatches("**/+CollisionNode"):
            node.removeNode()


def revealLocators(target=None, showText=True, locatorNodes=None):
    if not target:
        target = render
    if locatorNodes is None:
        locatorNodes = [
            "**/*locator*",
            "**/*origin*",
            "**/loc_*",
        ]
    if type(locatorNodes) is not list:
        locatorNodes = [locatorNodes]

    locator = loader.loadModel("models/misc/objectHandles")
    locator.flattenStrong()
    arrow = loader.loadModel("models/misc/Dirlight")
    arrow.setColor((1, 0, 0, 1))

    text = None
    if showText:
        from panda3d.core import TextNode
        from toontown.toonbase.ToontownGlobals import getInterfaceFont
        text = TextNode("locators")
        text.setFont(getInterfaceFont())
        text.setAlign(TextNode.ACenter)
        text.setTextColor(1.0, 1.0, 1.0, 1.0)

    for locNode in locatorNodes:
        for node in target.findAllMatches(locNode):
            loc = locator.copyTo(node)
            arrow.copyTo(loc)
            if text is not None:
                text.setText(node.getName())
                name = loc.attachNewNode(text.generate())
                name.setBillboardPointEye()
                name.setZ(1)


def revealSceneNodes(target=None, showText=True, nodeType="ModelNode"):
    """
    aggressive revealer
    """
    if not target:
        target = render

    nodetype2color = {
        "ModelNode": [(1, 0, 0, 1), (1, 1, 1, 1)],
        "PandaNode": [(1, 0, 1, 1), (0.6, 1, 1, 1)],
    }
    arrowColor, textColor = nodetype2color.get(nodeType, [(1, 1, 1, 1), (1, 1, 1, 1)])

    locator = loader.loadModel("models/misc/objectHandles")
    locator.flattenStrong()
    arrow = loader.loadModel("models/misc/Dirlight")
    arrow.setColor(arrowColor)
    arrowScale = 1 if nodeType == "ModelNode" else 0.5
    arrow.setScale(arrowScale)

    text = None
    if showText:
        from panda3d.core import TextNode
        from toontown.toonbase.ToontownGlobals import getInterfaceFont
        text = TextNode("locators")
        text.setFont(getInterfaceFont())
        text.setAlign(TextNode.ACenter)
        text.setTextColor(textColor)

    for node in target.findAllMatches("**/+%s" % nodeType):
        loc = locator.copyTo(node)
        arrow.copyTo(loc)
        if text is not None:
            text.setText(node.getName())
            name = loc.attachNewNode(text.generate())
            name.setBillboardPointEye()
            name.setZ(1)


def verboseTriggers(target=None):
    if not target:
        target = render

    def __enterTrigger(*args):
        print "enter"

    def __exitTrigger(*args):
        print "exit"

    for node in target.findAllMatches("**/*trigger*"):
        base.accept('enter' + node.getName(), __enterTrigger)
        base.accept('exit' + node.getName(), __exitTrigger)


def flashCullBins(randomColors=False, alpha=255):
    from toontown.utils.ColorHelper import randomNormalizedColor, hexToPCol

    cullbinColorCode = {
        "background": hexToPCol('e3342f', alpha),
        "ground": hexToPCol('f6993f', alpha),
        "shadow": hexToPCol('ffed4a', alpha),
        "opaque": hexToPCol('38c172', alpha),
        "transparent": hexToPCol('4dc0b5', alpha),
        "fixed": hexToPCol('3490dc', alpha),
        "unsorted": hexToPCol('6574cd', alpha),
        "gui-popup": hexToPCol('9561e2', alpha),
        "sorted-gui-popup": hexToPCol('f66d9b', alpha),
    }

    cbm = CullBinManager.getGlobalPtr()
    for bin_index in cbm.getBins():
        cbm.setBinFlashActive(bin_index, not cbm.getBinFlashActive(bin_index))
        color = cullbinColorCode.get(cbm.getBinName(bin_index))
        if not color or randomColors:
            color = randomNormalizedColor(alpha / 255.0)
        cbm.setBinFlashColor(bin_index, color)


def showJointLines(actor, part, parentNode=None, indent="", nodesToIgnore=[]):
    linepaths = NodePathCollection()

    def walkJointHierarchy(actor, part, parentNode=None, indent=""):
        if isinstance(part, CharacterJoint):
            np = actor.exposeJoint(None, 'modelRoot', part.getName())
            if parentNode and (parentNode.getName() != "root" and parentNode.getName() not in nodesToIgnore):
                lines = LineSegs()
                lines.setThickness(3.0)
                lines.setColor(random.random(), random.random(), random.random())
                lines.moveTo(0, 0, 0)
                lines.drawTo(np.getPos(parentNode))
                lnp = parentNode.attachNewNode(lines.create())
                linepaths.addPath(lnp)

                lnp.setBin("fixed", 40)
                lnp.setDepthWrite(False)
                lnp.setDepthTest(False)
                lnp.setTwoSided(True)

            parentNode = np

        if part is not None:
            for child in part.getChildren():
                walkJointHierarchy(actor, child, parentNode, indent + "  ")

    walkJointHierarchy(actor, part, parentNode, indent)
    return linepaths