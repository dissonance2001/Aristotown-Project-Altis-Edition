from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from direct.task.TaskManagerGlobal import taskMgr


@DirectNotifyCategory()
class QuickShopper:
    SFX_START_TIME = 0.075

    def __init__(self, isIncrement: bool):
        self.sfx = None
        self.isIncrement = isIncrement
        self.isFirst = True
        self.timer = 0

    def load(self):
        self.sfx = loader.loadSfx("phase_3/audio/sfx/GUI_create_toon_fwd.ogg")

    def unload(self):
        del self.sfx
        taskMgr.remove("quickShop")

    def activate(self, shopAction):
        if taskMgr.hasTaskNamed("quickShop"):
            taskMgr.remove("quickShop")
            return
        self.reset()
        taskMgr.add(
            self.quickShop,
            "quickShop",
            extraArgs = [shopAction],
            appendTask = True,
        )

    def reset(self):
        self.isFirst = True
        self.timer = 0
        self.sfx.setPlayRate(1)

    def quickShop(self, shopAction, task):
        actionSuccess = shopAction()
        if not actionSuccess:
            return task.done
        if actionSuccess > 0:
            self.playSfx()
            self.scheduleNext(shopAction)
            self.timer += self.calculateDelay()
            self.sfx.setPlayRate(self.calculateSfxRate())
        return task.done

    def playSfx(self):
        if not self.isFirst:  # prevents duplicate sfx caused by button sfx
            base.playSfx(self.sfx, interrupt = True, time = self.SFX_START_TIME)
        else:
            self.isFirst = False

    def scheduleNext(self, shopAction):
        # have to add new task if want to change delay time
        taskMgr.doMethodLater(
            self.calculateDelay(),
            self.quickShop,
            "quickShop",
            extraArgs = [shopAction],
            appendTask = True,
        )

    def calculateDelay(self):
        return max(0.01, pow(9 / 10, self.timer) - 0.90)

    def calculateSfxRate(self):
        return 1 + self.timer if self.isIncrement else 1 / (1 + 0.25 * self.timer)
