import gc
import math  # these imports are used; certain files commit "from otp.ai.AIBase import *". a heinous crime, but we're not interested in playing whack-a-mole atm
import os
import sys
import time
from typing import Union, TYPE_CHECKING

from panda3d.core import (ClockObject, GraphicsEngine, NodePath, Notify,
                          PandaNode, PStatClient, RenderState, Thread,
                          TransformState, TrueClock, VirtualFileSystem,
                          loadPrcFileData, ConfigVariableBool, ConfigVariableDouble, ConfigVariableInt)
from direct.interval.IntervalManager import ivalMgr
from direct.showbase import DConfig, ExceptionVarDump
from direct.showbase.BulletinBoardGlobal import bulletinBoard
from direct.showbase.EventManagerGlobal import eventMgr
from direct.showbase.JobManagerGlobal import jobMgr
from direct.showbase.MessengerGlobal import messenger
from direct.task import Task
from direct.task.TaskManagerGlobal import taskMgr
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

if TYPE_CHECKING:
    from toontown.ai.ToontownAIRepository import ToontownAIRepository
    from toontown.uberdog.ToontownUberRepository import ToontownUberRepository


_true = ['true', 'True', 't', 'T', '1', 'yes', 'Yes', 'YES']

@DirectNotifyCategory()
class AIBase:
    def __init__(self):
        # AIR get sets after initialization to either to the AIR or the UDR,
        # depending on the process.
        self.air = None # type: Union[ToontownAIRepository, ToontownUberRepository]
        __builtins__['__dev__'] = ConfigVariableBool('want-dev', False).getValue()
        logStackDump = (ConfigVariableBool('log-stack-dump', (not __dev__)).getValue() or \
            ConfigVariableBool('ai-log-stack-dump', (not __dev__)).getValue())
        uploadStackDump = ConfigVariableBool('upload-stack-dump', False).getValue()

        if logStackDump or uploadStackDump:
            ExceptionVarDump.install(logStackDump, uploadStackDump)
        if ConfigVariableBool('use-vfs', 1):
            vfs = VirtualFileSystem.getGlobalPtr()
        else:
            vfs = None

        # Store dconfig variables
        self.wantTk = ConfigVariableBool('want-tk', False).getValue()

        # How long should the AI sleep between frames to keep CPU usage down
        self.AISleep = float(os.environ.get('AI_SLEEP', 0.02))
        self.AIRunningNetYield = os.environ.get('AI_RUNNING_NET_YIELD', False) in _true
        self.AIForceSleep = ConfigVariableBool('ai-force-sleep', False).getValue()
        self.eventMgr = eventMgr
        self.messenger = messenger
        self.bboard = bulletinBoard

        self.taskMgr = taskMgr
        Task.TaskManager.taskTimerVerbose = ConfigVariableBool('task-timer-verbose', False).getValue()
        Task.TaskManager.extendedExceptions = ConfigVariableBool('extended-exceptions', False).getValue()

        self.sfxManagerList = None
        self.musicManager = None  # AudioManager
        self.jobMgr = jobMgr

        self.hidden = NodePath('hidden')

        # This graphics engine is not intended to ever draw anything, it advanced clocks and clears pstats state,
        # just like on the client.
        self.graphicsEngine = GraphicsEngine()

        # Get a pointer to Panda's global ClockObject, used for synchronizing events between Python and C.
        # object is exactly in sync with the TrueClock.
        globalClock = ClockObject.getGlobalClock()

        # Since we have already started up a TaskManager, and probably a number of tasks;
        # and since the TaskManager had to use the TrueClock to tell time until this moment, make sure the globalClock
        self.trueClock = TrueClock.getGlobalPtr()
        globalClock.setRealTime(self.trueClock.getShortTime())
        # set the amount of time used to compute average frame rate
        globalClock.setAverageFrameRateInterval(30.0)
        globalClock.tick()

        # Now we can make the TaskManager start using the new globalClock.
        taskMgr.globalClock = globalClock

        __builtins__['globalClock'] = globalClock
        __builtins__['vfs'] = vfs
        __builtins__['hidden'] = self.hidden

        self.notify.info('__dev__ == %s' % __dev__)

        self.wantStats = ConfigVariableBool('want-pstats', False).getValue()
        Task.TaskManager.pStatsTasks = ConfigVariableBool('pstats-tasks', False).getValue()
        # Set up the TaskManager to reset the PStats clock back whenever we resume from a pause.
        # This callback function is a little hacky, but we can't call it directly from within the TaskManager because
        # he doesn't know about PStats (and has to run before libpanda is even loaded).
        taskMgr.resumeFunc = PStatClient.resumeAfterPause

        # in production, we want to use fake textures.
        defaultValue = 1
        if __dev__:
            defaultValue = 0

        wantFakeTextures = ConfigVariableBool('want-fake-textures-ai', defaultValue).getValue()
        if wantFakeTextures:
            # Setting textures-header-only is a little better than using fake-texture-image.
            # Textures' headers are read to check their number of channels, etc., and then a 1x1 blue texture is created
            # It loads quickly, consumes very little memory, and doesn't require a bogus texture to be loaded repeatedly
            loadPrcFileData('aibase', 'textures-header-only 1')

        self.newDBRequestGen = ConfigVariableBool('new-database-request-generate', True).getValue()

        self.waitShardDelete = ConfigVariableBool('wait-shard-delete', True).getValue()
        self.blinkTrolley = ConfigVariableBool('blink-trolley', False).getValue()
        self.fakeDistrictPopulations = ConfigVariableBool('fake-district-populations', False).getValue()

        self.sqlAvailable = ConfigVariableBool('sql-available', True).getValue()

        self.taskMgr.add(self.__garbageCollectStates, 'garbageCollectStates', priority = 46)

        self.createStats()

        self.restart()
    
    @property
    def config(self) -> DConfig:
        if __debug__:
            self.notify.warning(f"'simbase.config' is deprecated")
        return DConfig

    def __garbageCollectStates(self, state):
        """
        This task is started only when we have garbage-collect-states set in the Config.prc file,
        in which case we're responsible for taking out Panda's garbage from time to time.
        This is not to be confused with Python's garbage collection.
        """
        TransformState.garbageCollect()
        RenderState.garbageCollect()
        return Task.cont

    def setupCpuAffinities(self, minChannel):
        if process == 'uberdog':
            affinityMask = ConfigVariableInt('uberdog-cpu-affinity-mask', -1).getValue()
        else:
            affinityMask = ConfigVariableInt('ai-cpu-affinity-mask', -1).getValue()
        if affinityMask != -1:
            TrueClock.getGlobalPtr().setCpuAffinity(affinityMask)
        else:
            # this is useful on machines that perform better with each process assigned to a single CPU
            autoAffinity = ConfigVariableBool('auto-single-cpu-affinity', False).getValue()
            if process == 'uberdog':
                affinity = ConfigVariableInt('uberdog-cpu-affinity', -1).getValue()
                if autoAffinity and affinity == -1:
                    affinity = 2
            else:
                affinity = ConfigVariableInt('ai-cpu-affinity', -1).getValue()
                if autoAffinity and affinity == -1:
                    affinity = 1
            if affinity != -1:
                TrueClock.getGlobalPtr().setCpuAffinity(1 << affinity)
            elif autoAffinity:
                if process == 'uberdog':
                    # set the affinity based on our channel range
                    channelSet = int(minChannel / 1000000)
                    channelSet -= 240
                    # add an offset so that the default uberdog affinity is 2
                    affinity = channelSet + 3
                    # this could be better if we know how many CPUs we have;
                    # for now spread the uberdogs across 4 processors
                    TrueClock.getGlobalPtr().setCpuAffinity(1 << affinity % 4)

    #########################################################################
    # This is the yield function for simple timing based .. no consideration for Network and such..
    ###########################################################################
    def taskManagerDoYield(self, frameStartTime, nextScheuledTaksTime):
        minFinTime = frameStartTime + self.MaxEpockSpeed
        if nextScheuledTaksTime > 0 and nextScheuledTaksTime < minFinTime:
            minFinTime = nextScheuledTaksTime
        delta = minFinTime - globalClock.getRealTime()
        while delta > 0.002:
            time.sleep(delta)
            delta = minFinTime - globalClock.getRealTime()

    def createStats(self, hostname = None, port = None):
        # Can specify pstats-host in config
        # Default is localhost
        if not self.wantStats:
            return False
        if PStatClient.isConnected():
            PStatClient.disconnect()
        # these default values match the C++ default values
        if hostname is None:
            hostname = ''
        if port is None:
            port = -1
        PStatClient.connect(hostname, port)
        return PStatClient.isConnected()

    def __sleepCycleTask(self, task):
        # To keep the AI task from running too fast, we sleep a bit here
        time.sleep(self.AISleep)
        return Task.cont

    def __resetPrevTransform(self, state):
        """
        Clear out the previous velocity deltas now, after we have rendered (the previous frame).
        We do this after the render, so that we can draw a representation of spheres along with their velocities.

        At the beginning of the frame really means after the command prompt, which allows the user to interactively
        query these deltas meaningfully.
        """
        PandaNode.resetAllPrevTransform()
        return Task.cont

    def __ivalLoop(self, state):
        """
        Execute all intervals in the global ivalMgr.
        """
        ivalMgr.step()
        return Task.cont

    def __igLoop(self, state):
        """
        This advances the clocks and clears pstats state
        """
        self.graphicsEngine.renderFrame()
        return Task.cont

    def shutdown(self):
        self.taskMgr.remove('ivalLoop')
        self.taskMgr.remove('igLoop')
        self.taskMgr.remove('aiSleep')
        self.eventMgr.shutdown()

    def restart(self):
        self.shutdown()
        # __resetPrevTransform goes at the very beginning of the frame.
        self.taskMgr.add(self.__resetPrevTransform, 'resetPrevTransform', priority = -51)

        # spawn the ivalLoop with a later priority, so that it will run after most tasks, but before igLoop.
        self.taskMgr.add(self.__ivalLoop, 'ivalLoop', priority = 20)
        self.taskMgr.add(self.__igLoop, 'igLoop', priority = 50)
        if self.AISleep >= 0 and (not self.AIRunningNetYield or self.AIForceSleep):
            self.taskMgr.add(self.__sleepCycleTask, 'aiSleep', priority = 55)
        self.eventMgr.restart()

    def getRepository(self):
        return self.air

    def run(self):
        self.taskMgr.run()
