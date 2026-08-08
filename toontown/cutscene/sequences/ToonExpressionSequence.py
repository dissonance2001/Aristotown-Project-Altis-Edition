from toontown.cutscene.editor.CSEditorEnums import EventDefinitionEnum as EDE
from toontown.cutscene.CutsceneSequenceBase import cutsceneSequence
from direct.interval.IntervalGlobal import Func, Sequence


@cutsceneSequence(name='Expression: Set', enum=EDE.setToonExpression)
def seq_setToonExpression(toonIndex=0, toonExpression='normal', cutsceneDict=None):
    toons = cutsceneDict.get('toons', ())
    if toonIndex < 0 or toonIndex >= len(toons):
        return Sequence()
    toon = toons[toonIndex]
    if not toon:
        return Sequence()

    def setMuzzle():
        try:
            toon.hideAllMuzzles()
        except:
            return
        method = {
            'normal': 'showNormalMuzzle',
            'angry': 'showAngryMuzzle',
            'sad': 'showSadMuzzle',
            'smile': 'showSmileMuzzle',
            'laugh': 'showLaughMuzzle',
            'surprise': 'showSurpriseMuzzle',
        }.get(toonExpression)
        if method and hasattr(toon, method):
            getattr(toon, method)()

    return Sequence(Func(setMuzzle))


@cutsceneSequence(name='Eyes: Set', enum=EDE.setToonEyes)
def seq_setToonEyes(toonIndex=0, toonEyes='normal', cutsceneDict=None):
    toons = cutsceneDict.get('toons', ())
    if toonIndex < 0 or toonIndex >= len(toons):
        return Sequence()
    toon = toons[toonIndex]
    if not toon:
        return Sequence()

    def setEyes():
        if toonEyes == 'normal':
            try:
                toon.normalEyes()
                toon.openEyes()
            except:
                pass
            try:
                toon.startBlink()
            except:
                pass
            return
        try:
            toon.stopBlink()
        except:
            pass
        try:
            toon.blinkEyes()
        except:
            pass
        method = {
            'angry': 'angryEyes',
            'sad': 'sadEyes',
            'surprise': 'surpriseEyes',
        }.get(toonEyes)
        if method and hasattr(toon, method):
            try:
                getattr(toon, method)()
            except:
                pass

    return Sequence(Func(setEyes))
