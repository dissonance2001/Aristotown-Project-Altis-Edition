"""
GenericShader.py
Author: Loonatic
Date: 8/15/2021

GenericShader is initialized when TSM is initialized, it is a child of TSM.
This should ensure that the FilterManager is up and running and that there's no default pink Panda shader.
Note: GenericShader does not take FilterManager object unlike other shaders

todo: instead of passing an index int, we should pass a tuple/list for all the nodepath we wanna apply this shader to!
"""
from . import ShaderGlobals
from ..utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class GenericShader:
    def __init__(self, index):
        """
        Index: 0 for render, 1 for render2d, 2 for both
        :param index:
        """
        if index > 2:
            return
        self.index = index
        self.setupGeneric()
        self.notify.info('Loaded')
        base.shaderMode = 'generic'

    def setupGeneric(self):
        """
        Generic Shaders = ShaderAuto
        """
        if self.index == 0:
            render.setShaderAuto()
        elif self.index == 1:
            render2d.setShaderAuto()
        else:
            render.setShaderAuto()
            render2d.setShaderAuto()


    def deleteGeneric(self):
        """
        Removes/cleanup the LUT Manager class entirely
        :return:
        """
        return

    def cleanup(self):
        return

    def cleanRender(self):
        return

    def cleanRender2d(self):
        return

    def getID(self):
        return ShaderGlobals.generic

    def removeShader(self):
        """
        Removes LUTManager but should allow to be initialized again, should be used where LUT filters aren't necessarily needed
        Bug: Doesn't fully cleanup the buffer from memory, trying to cleanup and then init again will cause a memory leak
        todo: make sure everything gets properly removed
        """
        if self.index == 0:
            render.clearShader()
        elif self.index == 1:
            render2d.clearShader()
        else:
            render.clearShader()
            render2d.clearShader()

        base.shaderMode = 'none'
        base.shader = None # todo: make base.shader and base.shader2d

