from __future__ import absolute_import
from __future__ import print_function
import inspect
import json
import os

from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectEntry import DirectEntry
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectOptionMenu import DirectOptionMenu
from direct.gui.DirectScrolledFrame import DirectScrolledFrame
from direct.interval.IntervalGlobal import Sequence
from direct.showbase.DirectObject import DirectObject
from panda3d.core import TextNode

from toontown.cutscene.CutsceneSequenceBase import cutsceneMethodDefs
from toontown.cutscene.repository.CutsceneRuntime import buildCutsceneData, getRegisteredEventNames
import six


_editor = None


def _safeName(obj, fallback):
    if obj is None:
        return fallback
    try:
        name = obj.getName()
        if name:
            return name
    except:
        pass
    try:
        name = obj.getNodePath().getName()
        if name:
            return name
    except:
        pass
    try:
        name = obj.get_name()
        if name:
            return name
    except:
        pass
    return '%s %s' % (obj.__class__.__name__, fallback)


def _isActor(obj):
    return hasattr(obj, 'getAnimNames') and hasattr(obj, 'getPos') and hasattr(obj, 'setPos')


def _isToon(obj):
    name = obj.__class__.__name__.lower()
    return _isActor(obj) and 'toon' in name and 'suit' not in name


def _isSuit(obj):
    name = obj.__class__.__name__.lower()
    return _isActor(obj) and ('suit' in name or 'cog' in name)


def _isBoss(obj):
    name = obj.__class__.__name__.lower()
    return _isActor(obj) and 'boss' in name


def _uniqueObjects(objects):
    result = []
    seen = set()
    for obj in objects:
        if obj is None:
            continue
        ident = id(obj)
        if ident in seen:
            continue
        seen.add(ident)
        result.append(obj)
    return result


def _objectListFromCR():
    cr = getattr(base, 'cr', None)
    if cr is None:
        return []
    try:
        return list(cr.doId2do.values())
    except:
        return []


def _defaultCutsceneDict():
    objects = _objectListFromCR()
    localAvatar = getattr(base, 'localAvatar', None)
    toons = _uniqueObjects(([localAvatar] if localAvatar else []) + [obj for obj in objects if _isToon(obj)])
    suits = _uniqueObjects([obj for obj in objects if _isSuit(obj)])
    bosses = _uniqueObjects([obj for obj in objects if _isBoss(obj)])
    actors = _uniqueObjects(toons + suits + bosses)
    nodes = [render, camera]
    try:
        place = base.cr.playGame.getPlace()
        if place is not None:
            loaderObj = getattr(place, 'loader', None)
            geom = getattr(loaderObj, 'geom', None)
            if geom is not None and not geom.isEmpty():
                nodes.append(geom)
    except:
        pass
    nodes.extend(actors)
    try:
        for child in render.getChildren():
            nodes.append(child)
    except:
        pass
    nodes = _uniqueObjects(nodes)
    return {
        'actors': actors,
        'affectsCamera': True,
        'arguments': [],
        'editorCleanup': [],
        'elevators': [],
        'functions': [],
        'maxPlayers': max(1, len(toons)),
        'messages': [],
        'music': [],
        'nodes': nodes,
        'sounds': [],
        'suits': suits,
        'toons': toons,
        'visualEffects': [],
        'bosses': bosses,
        'suppressSuitNametags': False,
    }


def _jsonValue(text, default=None):
    value = text.strip()
    if not value:
        return default
    lowered = value.lower()
    if lowered == 'true':
        return True
    if lowered == 'false':
        return False
    if lowered == 'none':
        return None
    try:
        return json.loads(value)
    except:
        pass
    try:
        if '.' in value:
            return float(value)
        return int(value)
    except:
        return value


def _displayValue(value):
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if value is None:
        return 'null'
    if isinstance(value, (list, tuple, dict)):
        return json.dumps(value)
    return str(value)


def _cleanJsonData(value):
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if key == 'cutsceneDict':
                continue
            result[key] = _cleanJsonData(item)
        return result
    if isinstance(value, (list, tuple)):
        return [_cleanJsonData(item) for item in value]
    return value


def _getMethodArgs(method):
    try:
        spec = inspect.getargspec(method)
    except:
        return []
    args = list(spec.args)
    defaults = list(spec.defaults or ())
    firstDefault = len(args) - len(defaults)
    result = []
    for index, name in enumerate(args):
        if name == 'cutsceneDict':
            continue
        if index >= firstDefault:
            default = defaults[index - firstDefault]
        else:
            default = None
        result.append((name, default))
    return result


def _collectionForArg(name):
    lower = name.lower()
    if 'message' in lower and 'index' in lower:
        return 'messages'
    if 'actor' in lower and 'index' in lower:
        return 'actors'
    if 'toon' in lower and 'index' in lower:
        return 'toons'
    if 'suit' in lower and 'index' in lower:
        return 'suits'
    if 'boss' in lower and 'index' in lower:
        return 'bosses'
    if 'node' in lower and 'index' in lower:
        return 'nodes'
    if 'elevator' in lower and 'index' in lower:
        return 'elevators'
    if ('sound' in lower or 'sfx' in lower) and 'index' in lower:
        return 'sounds'
    if 'music' in lower and 'index' in lower:
        return 'music'
    if 'function' in lower and 'index' in lower:
        return 'functions'
    if 'visualeffect' in lower and 'index' in lower:
        return 'visualEffects'
    return None


def _labelCollection(values):
    labels = []
    for index, value in enumerate(values):
        if isinstance(value, six.string_types):
            text = value
        else:
            text = _safeName(value, str(index))
        labels.append('%d: %s' % (index, text))
    return labels


class AltisCutsceneEditor(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)
        getRegisteredEventNames()
        self.cutsceneDict = _defaultCutsceneDict()
        self.events = []
        self.selectedEvent = None
        self.selectedSubeventKey = None
        self.track = None
        self.trackLength = 60.0
        self.playing = False
        self.previewMode = False
        self.baseline = {}
        self.eventButtons = []
        self.subeventButtons = []
        self.argWidgets = []
        self.resourceStatus = None
        self.sfxPaths = []
        self.musicPaths = []
        self.nodePatterns = []
        self.spawnedSuits = []
        self.spawnedSuitTypes = []
        self.pendingExportPath = 'cutscene_exports/custom_cutscene.ctsc'
        self._captureBaseline()
        self._loadAutosave()
        self._buildGui()
        self._refreshAll()
        self.accept('escape', self._handleEscape)
        self.accept('space', self.togglePlay)
        taskMgr.add(self._updateTask, 'altis-cutscene-editor-update')

    def _captureBaseline(self):
        self.baseline = {}
        objects = _uniqueObjects(self.cutsceneDict.get('actors', []) + self.cutsceneDict.get('nodes', []))
        for obj in objects:
            try:
                self.baseline[id(obj)] = (obj, obj.getParent(), obj.getTransform(), obj.isHidden())
            except:
                pass
        try:
            self.baselineFov = base.camLens.getMinFov()
        except:
            self.baselineFov = None

    def _restoreBaseline(self):
        for obj, parent, transform, hiddenState in self.baseline.values():
            try:
                obj.reparentTo(parent)
                obj.setTransform(transform)
                if hiddenState:
                    obj.hide()
                else:
                    obj.show()
            except:
                pass
        if self.baselineFov is not None:
            try:
                base.camLens.setMinFov(self.baselineFov)
            except:
                pass

    def _makeToonButton(self, parent, text, pos, command, width=1.2, scale=0.35, textScale=0.09, textColor=(1, 1, 1, 1), extraArgs=None):
        options = {
            'parent': parent,
            'text': text,
            'pos': pos,
            'command': command,
            'relief': None,
            'scale': scale,
            'text_scale': textScale,
            'text_pos': (0, -0.02),
            'text_fg': textColor,
            'text1_fg': textColor,
            'text2_fg': textColor,
            'text_shadow': (0, 0, 0, 1),
        }
        if extraArgs is not None:
            options['extraArgs'] = extraArgs
        if getattr(self, 'toonButtonImages', None) is not None:
            options['image'] = self.toonButtonImages
            options['image_scale'] = (width, 1, 0.72)
        else:
            options['relief'] = DGG.RAISED
            options['frameColor'] = (0.20, 0.36, 0.56, 1)
        return DirectButton(**options)

    def _buildGui(self):
        bg = (0.035, 0.043, 0.055, 0.98)
        header = (0.055, 0.068, 0.09, 1)
        toolbar = (0.075, 0.086, 0.11, 1)
        panel = (0.07, 0.078, 0.098, 1)
        panelInner = (0.09, 0.10, 0.125, 1)
        section = (0.105, 0.125, 0.165, 1)
        accent = (0.24, 0.48, 0.78, 1)
        button = (0.16, 0.19, 0.25, 1)
        buttonHot = (0.22, 0.29, 0.39, 1)
        danger = (0.30, 0.16, 0.18, 1)
        entry = (0.12, 0.13, 0.16, 1)
        textMain = (0.95, 0.97, 1, 1)
        textDim = (0.68, 0.73, 0.82, 1)

        try:
            self.buttonGui = loader.loadModel('phase_3/models/gui/quit_button')
            self.toonButtonImages = (
                self.buttonGui.find('**/QuitBtn_UP'),
                self.buttonGui.find('**/QuitBtn_DN'),
                self.buttonGui.find('**/QuitBtn_RLVR'),
                self.buttonGui.find('**/QuitBtn_UP'),
            )
        except:
            self.buttonGui = None
            self.toonButtonImages = None

        self.root = DirectFrame(parent=aspect2d, frameColor=bg, frameSize=(-1.32, 1.32, -0.96, 0.96), pos=(0, 0, 0))
        DirectFrame(parent=self.root, frameColor=header, frameSize=(-1.32, 1.32, -0.085, 0.085), pos=(0, 0, 0.875))
        DirectFrame(parent=self.root, frameColor=accent, frameSize=(-1.32, 1.32, -0.006, 0.006), pos=(0, 0, 0.785))
        self.title = DirectLabel(parent=self.root, text='Cutscene Editor', text_align=TextNode.ALeft, text_scale=0.055, text_fg=textMain, frameColor=(0, 0, 0, 0), pos=(-1.27, 0, 0.875))
        self.timeLabel = DirectLabel(parent=self.root, text='0.00 / 60.00', text_scale=0.037, text_fg=textDim, frameColor=(0, 0, 0, 0), pos=(0.02, 0, 0.875))
        self.playButton = self._makeToonButton(self.root, 'Play', (0.35, 0, 0.875), self.togglePlay, width=0.95)
        self.previewButton = self._makeToonButton(self.root, 'Preview', (0.55, 0, 0.875), self.previewFullScreen, width=1.15, textColor=(1.0, 0.95, 0.45, 1))
        self.restartButton = self._makeToonButton(self.root, 'Restart', (0.76, 0, 0.875), self.restartPreview, width=1.12)
        self.refreshButton = self._makeToonButton(self.root, 'Refresh Scene', (1.00, 0, 0.875), self.refreshScene, width=1.55, textScale=0.075)
        self.closeButton = self._makeToonButton(self.root, 'Close', (1.24, 0, 0.875), self.close, width=0.95, textColor=(1.0, 0.65, 0.65, 1))

        DirectFrame(parent=self.root, frameColor=toolbar, frameSize=(-1.29, 1.29, -0.06, 0.06), pos=(0, 0, 0.705))
        DirectLabel(parent=self.root, text='TIME', text_align=TextNode.ALeft, text_scale=0.025, text_fg=textDim, frameColor=(0, 0, 0, 0), pos=(-1.24, 0, 0.705))
        self.timeEntry = DirectEntry(parent=self.root, initialText='0.0', scale=0.032, width=7, text_fg=textMain, frameColor=entry, pos=(-1.08, 0, 0.705), command=self._jumpTimeEntry)
        DirectLabel(parent=self.root, text='LENGTH', text_align=TextNode.ALeft, text_scale=0.025, text_fg=textDim, frameColor=(0, 0, 0, 0), pos=(-0.79, 0, 0.705))
        self.durationEntry = DirectEntry(parent=self.root, initialText=str(self.trackLength), scale=0.032, width=7, text_fg=textMain, frameColor=entry, pos=(-0.57, 0, 0.705), command=self._durationEntry)
        DirectLabel(parent=self.root, text='FILE', text_align=TextNode.ALeft, text_scale=0.025, text_fg=textDim, frameColor=(0, 0, 0, 0), pos=(-0.27, 0, 0.705))
        self.exportEntry = DirectEntry(parent=self.root, initialText=self.pendingExportPath, scale=0.029, width=24, text_fg=textMain, frameColor=entry, pos=(-0.15, 0, 0.705))
        self.loadButton = self._makeToonButton(self.root, 'Load', (0.76, 0, 0.705), self.loadFromEntry, width=0.95, scale=0.32)
        self.saveButton = self._makeToonButton(self.root, 'Export', (1.05, 0, 0.705), self.export, width=1.12, scale=0.32, textColor=(1.0, 0.95, 0.45, 1))

        DirectFrame(parent=self.root, frameColor=panel, frameSize=(-0.405, 0.405, -0.525, 0.525), pos=(-0.87, 0, 0.055))
        DirectFrame(parent=self.root, frameColor=panel, frameSize=(-0.405, 0.405, -0.525, 0.525), pos=(-0.01, 0, 0.055))
        DirectFrame(parent=self.root, frameColor=panel, frameSize=(-0.405, 0.405, -0.525, 0.525), pos=(0.85, 0, 0.055))
        DirectFrame(parent=self.root, frameColor=section, frameSize=(-0.405, 0.405, -0.045, 0.045), pos=(-0.87, 0, 0.535))
        DirectFrame(parent=self.root, frameColor=section, frameSize=(-0.405, 0.405, -0.045, 0.045), pos=(-0.01, 0, 0.535))
        DirectFrame(parent=self.root, frameColor=section, frameSize=(-0.405, 0.405, -0.045, 0.045), pos=(0.85, 0, 0.535))
        DirectLabel(parent=self.root, text='EVENTS', text_scale=0.033, text_fg=textMain, frameColor=(0, 0, 0, 0), pos=(-0.87, 0, 0.535))
        DirectLabel(parent=self.root, text='SUBEVENTS', text_scale=0.033, text_fg=textMain, frameColor=(0, 0, 0, 0), pos=(-0.01, 0, 0.535))
        DirectLabel(parent=self.root, text='ARGUMENTS', text_scale=0.033, text_fg=textMain, frameColor=(0, 0, 0, 0), pos=(0.85, 0, 0.535))
        self.eventFrame = DirectScrolledFrame(parent=self.root, frameColor=panelInner, frameSize=(-0.37, 0.37, -0.43, 0.43), canvasSize=(-0.34, 0.34, -6, 0.40), pos=(-0.87, 0, 0.045), scrollBarWidth=0.035)
        self.subeventFrame = DirectScrolledFrame(parent=self.root, frameColor=panelInner, frameSize=(-0.37, 0.37, -0.28, 0.28), canvasSize=(-0.34, 0.34, -6, 0.25), pos=(-0.01, 0, -0.105), scrollBarWidth=0.035)
        self.argsFrame = DirectScrolledFrame(parent=self.root, frameColor=panelInner, frameSize=(-0.37, 0.37, -0.43, 0.43), canvasSize=(-0.34, 0.34, -12, 0.40), pos=(0.85, 0, 0.045), scrollBarWidth=0.035)

        DirectFrame(parent=self.root, frameColor=panel, frameSize=(-0.405, 0.405, -0.205, 0.205), pos=(-0.87, 0, -0.695))
        DirectFrame(parent=self.root, frameColor=panel, frameSize=(-0.405, 0.405, -0.205, 0.205), pos=(-0.01, 0, -0.695))
        DirectFrame(parent=self.root, frameColor=panel, frameSize=(-0.405, 0.405, -0.205, 0.205), pos=(0.85, 0, -0.695))
        DirectLabel(parent=self.root, text='EVENT DETAILS', text_align=TextNode.ALeft, text_scale=0.027, text_fg=textDim, frameColor=(0, 0, 0, 0), pos=(-1.23, 0, -0.525))
        DirectLabel(parent=self.root, text='SCENE ACTORS', text_align=TextNode.ALeft, text_scale=0.027, text_fg=textDim, frameColor=(0, 0, 0, 0), pos=(-0.37, 0, -0.525))
        DirectLabel(parent=self.root, text='RESOURCES', text_align=TextNode.ALeft, text_scale=0.027, text_fg=textDim, frameColor=(0, 0, 0, 0), pos=(0.49, 0, -0.525))

        DirectLabel(parent=self.root, text='Category', text_align=TextNode.ALeft, text_scale=0.024, text_fg=textDim, frameColor=(0, 0, 0, 0), pos=(-0.34, 0, 0.445))
        self.categoryMenu = DirectOptionMenu(parent=self.root, relief=DGG.FLAT, items=[''], scale=0.027, text_fg=textMain, frameColor=button, pos=(-0.14, 0, 0.445), command=self._categoryChanged)
        DirectLabel(parent=self.root, text='Type', text_align=TextNode.ALeft, text_scale=0.024, text_fg=textDim, frameColor=(0, 0, 0, 0), pos=(-0.34, 0, 0.355))
        self.typeMenu = DirectOptionMenu(parent=self.root, relief=DGG.FLAT, items=[''], scale=0.024, text_fg=textMain, frameColor=button, pos=(-0.14, 0, 0.355))
        self.addSubeventButton = self._makeToonButton(self.root, '+ Add', (-0.18, 0, 0.245), self.addSubevent, width=1.05, scale=0.31, textColor=(1.0, 0.95, 0.45, 1))
        self.deleteSubeventButton = self._makeToonButton(self.root, 'Delete', (0.20, 0, 0.245), self.deleteSubevent, width=1.0, scale=0.31, textColor=(1.0, 0.65, 0.65, 1))

        DirectLabel(parent=self.root, text='Name', text_align=TextNode.ALeft, text_scale=0.025, text_fg=textDim, frameColor=(0, 0, 0, 0), pos=(-1.23, 0, -0.60))
        self.eventNameEntry = DirectEntry(parent=self.root, initialText='', scale=0.030, width=17, text_fg=textMain, frameColor=entry, pos=(-1.08, 0, -0.60), focusOutCommand=self._applyEventHeader)
        DirectLabel(parent=self.root, text='Time', text_align=TextNode.ALeft, text_scale=0.025, text_fg=textDim, frameColor=(0, 0, 0, 0), pos=(-1.23, 0, -0.69))
        self.eventTimeEntry = DirectEntry(parent=self.root, initialText='0.0', scale=0.030, width=6, text_fg=textMain, frameColor=entry, pos=(-1.08, 0, -0.69), focusOutCommand=self._applyEventHeader)
        DirectLabel(parent=self.root, text='Mode', text_align=TextNode.ALeft, text_scale=0.025, text_fg=textDim, frameColor=(0, 0, 0, 0), pos=(-0.84, 0, -0.69))
        self.modeMenu = DirectOptionMenu(parent=self.root, relief=DGG.FLAT, items=['Parallel', 'Sequence'], scale=0.030, text_fg=textMain, frameColor=button, pos=(-0.69, 0, -0.69), command=self._setEventMode)
        self.addEventButton = self._makeToonButton(self.root, '+ New Event', (-1.09, 0, -0.82), self.addEvent, width=1.45, scale=0.31, textColor=(1.0, 0.95, 0.45, 1))
        self.deleteEventButton = self._makeToonButton(self.root, 'Delete Event', (-0.68, 0, -0.82), self.deleteEvent, width=1.45, scale=0.31, textColor=(1.0, 0.65, 0.65, 1))

        DirectLabel(parent=self.root, text='Suit', text_align=TextNode.ALeft, text_scale=0.023, text_fg=textDim, frameColor=(0, 0, 0, 0), pos=(-0.37, 0, -0.60))
        self.suitSpawnEntry = DirectEntry(parent=self.root, initialText='Flunky', scale=0.027, width=15, text_fg=textMain, frameColor=entry, pos=(-0.21, 0, -0.60), command=self.spawnSuit)
        self.spawnSuitButton = self._makeToonButton(self.root, 'Spawn', (0.24, 0, -0.60), self.spawnSuit, width=1.0, scale=0.27, textScale=0.08)
        DirectLabel(parent=self.root, text='Type a Cog name or DNA code', text_align=TextNode.ALeft, text_scale=0.021, text_fg=textDim, frameColor=(0, 0, 0, 0), pos=(-0.37, 0, -0.68))
        self.removeSuitButton = self._makeToonButton(self.root, 'Remove Last', (-0.11, 0, -0.79), self.removeLastSpawnedSuit, width=1.45, scale=0.28, textColor=(1.0, 0.65, 0.65, 1), textScale=0.075)

        DirectLabel(parent=self.root, text='Message', text_align=TextNode.ALeft, text_scale=0.023, text_fg=textDim, frameColor=(0, 0, 0, 0), pos=(0.49, 0, -0.59))
        self.messageEntry = DirectEntry(parent=self.root, initialText='', scale=0.027, width=17, text_fg=textMain, frameColor=entry, pos=(0.68, 0, -0.59))
        self.messageButton = self._makeToonButton(self.root, 'Add', (1.20, 0, -0.59), self.addMessage, width=0.82, scale=0.27, textScale=0.085)
        DirectLabel(parent=self.root, text='Node', text_align=TextNode.ALeft, text_scale=0.023, text_fg=textDim, frameColor=(0, 0, 0, 0), pos=(0.49, 0, -0.68))
        self.nodeEntry = DirectEntry(parent=self.root, initialText='**/', scale=0.027, width=17, text_fg=textMain, frameColor=entry, pos=(0.68, 0, -0.68))
        self.nodeButton = self._makeToonButton(self.root, 'Add', (1.20, 0, -0.68), self.addNode, width=0.82, scale=0.27, textScale=0.085)
        DirectLabel(parent=self.root, text='Audio', text_align=TextNode.ALeft, text_scale=0.023, text_fg=textDim, frameColor=(0, 0, 0, 0), pos=(0.49, 0, -0.77))
        self.audioEntry = DirectEntry(parent=self.root, initialText='', scale=0.027, width=14, text_fg=textMain, frameColor=entry, pos=(0.68, 0, -0.77))
        self.sfxButton = self._makeToonButton(self.root, '+ SFX', (1.07, 0, -0.77), self.addSfx, width=0.95, scale=0.26, textScale=0.082)
        self.musicButton = self._makeToonButton(self.root, '+ Music', (1.23, 0, -0.77), self.addMusic, width=1.05, scale=0.26, textScale=0.078)

        DirectFrame(parent=self.root, frameColor=header, frameSize=(-1.32, 1.32, -0.035, 0.035), pos=(0, 0, -0.925))
        self.resourceStatus = DirectLabel(parent=self.root, text='', text_align=TextNode.ALeft, text_scale=0.024, text_fg=textDim, frameColor=(0, 0, 0, 0), pos=(-1.27, 0, -0.927))
        self._buildTypeMenus()

    def _buildTypeMenus(self):
        self.typeByFriendly = {}
        self.typesByCategory = {}
        for enumName, data in cutsceneMethodDefs.items():
            if data.get('hidden'):
                continue
            friendly = data.get('name', enumName)
            category = friendly.split(':', 1)[0] if ':' in friendly else 'Other'
            display = friendly
            if display in self.typeByFriendly and self.typeByFriendly[display] != enumName:
                display = '%s (%s)' % (friendly, enumName)
            self.typeByFriendly[display] = enumName
            self.typesByCategory.setdefault(category, []).append(display)
        categories = sorted(self.typesByCategory.keys())
        if not categories:
            categories = ['Other']
            self.typesByCategory['Other'] = []
        self.categoryMenu['items'] = categories
        self.categoryMenu.set(0)
        self._categoryChanged(categories[0])

    def _categoryChanged(self, category):
        items = sorted(self.typesByCategory.get(category, []))
        if not items:
            items = ['']
        self.typeMenu['items'] = items
        self.typeMenu.set(0)

    def _eventData(self):
        return self.events

    def _loadAutosave(self):
        path = 'cutscene_editor_autosave.ctsc'
        if not os.path.isfile(path):
            return
        try:
            handle = open(path, 'r')
            try:
                data = json.load(handle)
            finally:
                handle.close()
            if isinstance(data, list):
                self.events = data
                return
            if not isinstance(data, dict):
                return
            self.events = data.get('events', [])
            self.trackLength = float(data.get('trackLength', self.trackLength))
            self.pendingExportPath = data.get('exportPath', self.pendingExportPath)
            self.cutsceneDict['messages'] = list(data.get('messages', []))
            self.sfxPaths = list(data.get('sfxPaths', []))
            self.musicPaths = list(data.get('musicPaths', []))
            self.nodePatterns = list(data.get('nodePatterns', []))
            self._reloadSavedResources()
            self._applyManifestOrdering(data.get('manifest', {}))
        except:
            self.events = []

    def _reloadSavedResources(self):
        for pattern in self.nodePatterns:
            try:
                node = render.find(pattern)
            except:
                node = None
            if node is not None and not node.isEmpty() and node not in self.cutsceneDict['nodes']:
                self.cutsceneDict['nodes'].append(node)
        self.cutsceneDict['sounds'] = []
        for path in self.sfxPaths:
            try:
                sound = loader.loadSfx(path)
            except:
                sound = None
            if sound is not None:
                self.cutsceneDict['sounds'].append(sound)
        self.cutsceneDict['music'] = []
        for path in self.musicPaths:
            try:
                music = loader.loadMusic(path)
            except:
                music = None
            if music is not None:
                self.cutsceneDict['music'].append(music)

    def _workspaceData(self):
        return {
            'events': self.events,
            'exportPath': self.exportEntry.get().strip() if hasattr(self, 'exportEntry') else self.pendingExportPath,
            'manifest': self._manifestData(),
            'messages': self.cutsceneDict.get('messages', []),
            'musicPaths': self.musicPaths,
            'nodePatterns': self.nodePatterns,
            'sfxPaths': self.sfxPaths,
            'spawnedSuitTypes': list(self.spawnedSuitTypes),
            'trackLength': self.trackLength,
        }

    def autosave(self):
        try:
            self._writeJsonFile('cutscene_editor_autosave.ctsc', self._workspaceData())
            return True
        except Exception as error:
            print(('[Cutscene Editor] Autosave error: %s' % error))
            return False

    def loadFromEntry(self):
        path = self.exportEntry.get().strip()
        if not path or not os.path.isfile(path):
            self.resourceStatus['text'] = 'Cutscene file not found: %s' % path
            return
        try:
            handle = open(path, 'r')
            try:
                data = json.load(handle)
            finally:
                handle.close()
        except Exception as error:
            self.resourceStatus['text'] = 'Could not load: %s' % error
            return
        if isinstance(data, dict) and 'events' in data:
            data = data['events']
        if not isinstance(data, list):
            self.resourceStatus['text'] = 'That file is not a CTSC event list.'
            return
        manifestPath = os.path.splitext(path)[0] + '.setup.json'
        if os.path.isfile(manifestPath):
            try:
                manifestHandle = open(manifestPath, 'r')
                try:
                    manifest = json.load(manifestHandle)
                finally:
                    manifestHandle.close()
                self.cutsceneDict['messages'] = list(manifest.get('messages', []))
                self.sfxPaths = list(manifest.get('sfxPaths', []))
                self.musicPaths = list(manifest.get('musicPaths', []))
                self.nodePatterns = list(manifest.get('nodePatterns', []))
                self.trackLength = float(manifest.get('trackLength', self.trackLength))
                self.durationEntry.enterText(str(self.trackLength))
                self._reloadSavedResources()
                self._applyManifestOrdering(manifest)
            except Exception as error:
                print(('[Cutscene Editor] Setup manifest error: %s' % error))
        self.events = data
        self.selectedEvent = self.events[0] if self.events else None
        keys = self._subeventKeys(self.selectedEvent) if self.selectedEvent else []
        self.selectedSubeventKey = keys[0] if keys else None
        self._refreshAll()
        self._rebuildPreview(0.0)
        self.resourceStatus['text'] = 'Loaded: %s' % path

    def export(self):
        path = self.exportEntry.get().strip() or 'cutscene_exports/custom_cutscene.ctsc'
        if not path.lower().endswith('.ctsc'):
            path += '.ctsc'
            self.exportEntry.enterText(path)
        try:
            self._writeJsonFile(path, self.events)
            manifestPath = os.path.splitext(path)[0] + '.setup.json'
            self._writeJsonFile(manifestPath, self._manifestData())
        except Exception as error:
            self.resourceStatus['text'] = 'Export failed: %s' % error
            print(('[Cutscene Editor] Export error: %s' % error))
            return
        self.autosave()
        self.resourceStatus['text'] = 'Exported CTSC + setup manifest.'

    def _applyManifestOrdering(self, manifest):
        if not isinstance(manifest, dict):
            return
        for key in ('actors', 'toons', 'suits', 'bosses', 'nodes', 'elevators'):
            expected = manifest.get(key)
            current = list(self.cutsceneDict.get(key, []))
            if not expected or not current:
                continue
            remaining = list(current)
            ordered = []
            for label in expected:
                expectedName = str(label).split(': ', 1)[-1]
                found = None
                for obj in remaining:
                    actualName = _safeName(obj, '')
                    if actualName == expectedName:
                        found = obj
                        break
                if found is not None:
                    ordered.append(found)
                    remaining.remove(found)
            ordered.extend(remaining)
            self.cutsceneDict[key] = ordered

    def _manifestData(self):
        result = {}
        for key in ('actors', 'toons', 'suits', 'bosses', 'nodes', 'elevators'):
            result[key] = _labelCollection(self.cutsceneDict.get(key, []))
        result['messages'] = list(self.cutsceneDict.get('messages', []))
        result['sfxPaths'] = list(self.sfxPaths)
        result['musicPaths'] = list(self.musicPaths)
        result['nodePatterns'] = list(self.nodePatterns)
        result['spawnedSuitTypes'] = list(self.spawnedSuitTypes)
        result['trackLength'] = self.trackLength
        return result

    def _writeJsonFile(self, path, data):
        directory = os.path.dirname(path)
        if directory and not os.path.isdir(directory):
            os.makedirs(directory)
        tempPath = path + '.tmp'
        handle = open(tempPath, 'w')
        try:
            json.dump(_cleanJsonData(data), handle, indent=2, sort_keys=True)
        except:
            handle.close()
            try:
                os.remove(tempPath)
            except:
                pass
            raise
        handle.close()
        if os.path.isfile(path):
            os.remove(path)
        os.rename(tempPath, path)

    def addEvent(self):
        current = self._currentTime()
        event = {'time': round(current, 3), 'name': 'Event %d' % (len(self.events) + 1), 'sequenceMode': 'Parallel', 'subEvents': {}}
        self.events.append(event)
        self.events.sort(key=lambda item: float(item.get('time', 0.0)))
        self.selectedEvent = event
        self.selectedSubeventKey = None
        self._refreshAll()
        self._rebuildPreview(current)

    def deleteEvent(self):
        if self.selectedEvent is None:
            return
        if self.selectedEvent in self.events:
            self.events.remove(self.selectedEvent)
        self.selectedEvent = self.events[0] if self.events else None
        self.selectedSubeventKey = None
        self._refreshAll()
        self._rebuildPreview(self._currentTime())

    def _selectEvent(self, event):
        self.selectedEvent = event
        keys = self._subeventKeys(event)
        self.selectedSubeventKey = keys[0] if keys else None
        self._refreshAll()
        self.setTime(float(event.get('time', 0.0)))

    def _subeventKeys(self, event=None):
        event = event or self.selectedEvent
        if event is None:
            return []
        keys = list(event.setdefault('subEvents', {}).keys())
        def keyValue(value):
            try:
                return int(value)
            except:
                return 0
        return sorted(keys, key=keyValue)

    def addSubevent(self):
        if self.selectedEvent is None:
            return
        display = self.typeMenu.get()
        enumName = self.typeByFriendly.get(display)
        if not enumName:
            return
        data = cutsceneMethodDefs.get(enumName)
        if data is None:
            return
        kwargs = {}
        for name, default in _getMethodArgs(data['method']):
            kwargs[name] = default
        subevents = self.selectedEvent.setdefault('subEvents', {})
        newKey = str(max([int(k) for k in subevents.keys()] + [-1]) + 1)
        subevents[newKey] = {'eventDefEnum': enumName, 'kwargs': kwargs}
        self.selectedSubeventKey = newKey
        self._refreshAll()
        self._rebuildPreview(self._currentTime())

    def deleteSubevent(self):
        if self.selectedEvent is None or self.selectedSubeventKey is None:
            return
        subevents = self.selectedEvent.setdefault('subEvents', {})
        if self.selectedSubeventKey in subevents:
            del subevents[self.selectedSubeventKey]
        keys = self._subeventKeys()
        self.selectedSubeventKey = keys[0] if keys else None
        self._refreshAll()
        self._rebuildPreview(self._currentTime())

    def _selectSubevent(self, key):
        self.selectedSubeventKey = key
        self._refreshSubevents()
        self._refreshArgs()

    def _setEventMode(self, mode):
        if self.selectedEvent is None:
            return
        self.selectedEvent['sequenceMode'] = mode
        self._rebuildPreview(self._currentTime())

    def _applyEventHeader(self):
        if self.selectedEvent is None:
            return
        self.selectedEvent['name'] = self.eventNameEntry.get()
        try:
            self.selectedEvent['time'] = max(0.0, float(self.eventTimeEntry.get()))
        except:
            pass
        self.events.sort(key=lambda item: float(item.get('time', 0.0)))
        self._refreshEvents()
        self._rebuildPreview(self._currentTime())

    def _refreshAll(self):
        self._refreshEvents()
        self._refreshSubevents()
        self._refreshArgs()
        self._refreshHeader()
        self._refreshResources()

    def _clearWidgets(self, widgets):
        for widget in widgets:
            try:
                widget.destroy()
            except:
                pass
        del widgets[:]

    def _refreshEvents(self):
        self._clearWidgets(self.eventButtons)
        canvas = self.eventFrame.getCanvas()
        y = 0.35
        for event in self.events:
            selected = event is self.selectedEvent
            label = '%6.2f  %s' % (float(event.get('time', 0.0)), event.get('name', 'Event'))
            button = DirectButton(parent=canvas, text=label, text_align=TextNode.ALeft, text_scale=0.035, frameColor=(0.24, 0.48, 0.78, 1) if selected else (0.13, 0.15, 0.19, 1), relief=DGG.FLAT, frameSize=(-0.33, 0.32, -0.045, 0.045), pos=(-0.32, 0, y), command=self._selectEvent, extraArgs=[event])
            self.eventButtons.append(button)
            y -= 0.1
        self.eventFrame['canvasSize'] = (-0.34, 0.34, min(-0.43, y - 0.1), 0.40)

    def _refreshSubevents(self):
        self._clearWidgets(self.subeventButtons)
        canvas = self.subeventFrame.getCanvas()
        if self.selectedEvent is None:
            return
        y = 0.22
        subevents = self.selectedEvent.setdefault('subEvents', {})
        for key in self._subeventKeys():
            subevent = subevents[key]
            enumName = subevent.get('eventDefEnum', '')
            data = cutsceneMethodDefs.get(enumName, {})
            friendly = data.get('name', enumName)
            selected = key == self.selectedSubeventKey
            button = DirectButton(parent=canvas, text='%s. %s' % (key, friendly), text_align=TextNode.ALeft, text_scale=0.031, frameColor=(0.24, 0.48, 0.78, 1) if selected else (0.13, 0.15, 0.19, 1), relief=DGG.FLAT, frameSize=(-0.33, 0.32, -0.05, 0.05), pos=(-0.32, 0, y), command=self._selectSubevent, extraArgs=[key])
            self.subeventButtons.append(button)
            y -= 0.11
        self.subeventFrame['canvasSize'] = (-0.34, 0.34, min(-0.28, y - 0.1), 0.25)

    def _refreshArgs(self):
        self._clearWidgets(self.argWidgets)
        if self.selectedEvent is None or self.selectedSubeventKey is None:
            return
        subevent = self.selectedEvent.setdefault('subEvents', {}).get(self.selectedSubeventKey)
        if subevent is None:
            return
        enumName = subevent.get('eventDefEnum')
        data = cutsceneMethodDefs.get(enumName)
        if data is None:
            return
        kwargs = subevent.setdefault('kwargs', {})
        canvas = self.argsFrame.getCanvas()
        y = 0.35
        for name, default in _getMethodArgs(data['method']):
            if name not in kwargs:
                kwargs[name] = default
            label = DirectLabel(parent=canvas, text=name, text_align=TextNode.ALeft, text_scale=0.03, text_fg=(1, 1, 1, 1), frameColor=(0, 0, 0, 0), pos=(-0.33, 0, y))
            self.argWidgets.append(label)
            collection = _collectionForArg(name)
            if collection is not None:
                values = self.cutsceneDict.get(collection, [])
                items = _labelCollection(values)
                if not items:
                    items = ['0: <empty>']
                menu = DirectOptionMenu(parent=canvas, items=items, scale=0.028, pos=(-0.08, 0, y), command=self._argMenuChanged, extraArgs=[name])
                current = kwargs.get(name, 0)
                try:
                    current = int(current)
                except:
                    current = 0
                menu.set(max(0, min(current, len(items) - 1)))
                self.argWidgets.append(menu)
            elif isinstance(kwargs.get(name), bool):
                menu = DirectOptionMenu(parent=canvas, items=['false', 'true'], scale=0.028, pos=(-0.08, 0, y), command=self._argBoolChanged, extraArgs=[name])
                menu.set(1 if kwargs.get(name) else 0)
                self.argWidgets.append(menu)
            elif name == 'blendType':
                items = ['noBlend', 'easeIn', 'easeOut', 'easeInOut']
                menu = DirectOptionMenu(parent=canvas, items=items, scale=0.028, pos=(-0.08, 0, y), command=self._argTextMenuChanged, extraArgs=[name])
                try:
                    menu.set(items.index(kwargs.get(name)))
                except:
                    menu.set(3)
                self.argWidgets.append(menu)
            elif name == 'targetGroup':
                items = ['All', 'Players', 'NPCs']
                menu = DirectOptionMenu(parent=canvas, items=items, scale=0.028, pos=(-0.08, 0, y), command=self._argTextMenuChanged, extraArgs=[name])
                try:
                    menu.set(items.index(kwargs.get(name)))
                except:
                    menu.set(0)
                self.argWidgets.append(menu)
            else:
                entry = DirectEntry(parent=canvas, initialText=_displayValue(kwargs.get(name)), scale=0.028, width=12, pos=(-0.08, 0, y))
                entry['focusOutCommand'] = self._argEntryFocusOut
                entry['focusOutExtraArgs'] = [entry, name]
                entry['command'] = self._argEntryChanged
                entry['extraArgs'] = [name]
                self.argWidgets.append(entry)
            y -= 0.095
        self.argsFrame['canvasSize'] = (-0.34, 0.34, min(-0.43, y - 0.1), 0.40)

    def _argMenuChanged(self, selected, name):
        try:
            value = int(str(selected).split(':', 1)[0])
        except:
            value = 0
        self._setArg(name, value)

    def _argBoolChanged(self, selected, name):
        self._setArg(name, selected == 'true')

    def _argTextMenuChanged(self, selected, name):
        self._setArg(name, selected)

    def _argEntryChanged(self, text, name):
        current = self._selectedKwargs().get(name)
        self._setArg(name, _jsonValue(text, current))

    def _argEntryFocusOut(self, entry, name):
        self._argEntryChanged(entry.get(), name)

    def _selectedKwargs(self):
        if self.selectedEvent is None or self.selectedSubeventKey is None:
            return {}
        return self.selectedEvent.setdefault('subEvents', {}).setdefault(self.selectedSubeventKey, {}).setdefault('kwargs', {})

    def _setArg(self, name, value):
        self._selectedKwargs()[name] = value
        self._rebuildPreview(self._currentTime())

    def _refreshHeader(self):
        if self.selectedEvent is None:
            self.eventNameEntry.enterText('')
            self.eventTimeEntry.enterText('0.0')
            return
        self.eventNameEntry.enterText(str(self.selectedEvent.get('name', '')))
        self.eventTimeEntry.enterText(str(self.selectedEvent.get('time', 0.0)))
        mode = self.selectedEvent.get('sequenceMode', 'Parallel')
        self.modeMenu.set(1 if mode == 'Sequence' else 0)

    def _refreshResources(self):
        text = 'Toons %d | Suits %d | Actors %d | Nodes %d | Messages %d | SFX %d | Music %d' % (
            len(self.cutsceneDict.get('toons', [])), len(self.cutsceneDict.get('suits', [])), len(self.cutsceneDict.get('actors', [])), len(self.cutsceneDict.get('nodes', [])), len(self.cutsceneDict.get('messages', [])), len(self.cutsceneDict.get('sounds', [])), len(self.cutsceneDict.get('music', [])))
        self.resourceStatus['text'] = text

    def _resolveSuitType(self, text):
        value = str(text).strip().lower()
        if not value:
            return None
        try:
            from toontown.suit import SuitDNA
            from toontown.battle import SuitBattleGlobals
        except:
            return None
        for suitType in SuitDNA.suitHeadTypes:
            if str(suitType).lower() == value:
                return suitType
        matches = []
        for suitType in SuitDNA.suitHeadTypes:
            data = SuitBattleGlobals.SuitAttributes.get(suitType, {})
            name = str(data.get('name', '')).strip()
            if name.lower() == value:
                return suitType
            if value and value in name.lower():
                matches.append(suitType)
        if len(matches) == 1:
            return matches[0]
        return None

    def _addSpawnedSuitToScene(self, suit):
        for key in ('suits', 'actors', 'nodes'):
            values = self.cutsceneDict.setdefault(key, [])
            if suit not in values:
                values.append(suit)

    def spawnSuit(self, text=None):
        if text is None:
            text = self.suitSpawnEntry.get()
        suitType = self._resolveSuitType(text)
        if suitType is None:
            self.resourceStatus['text'] = 'Unknown or ambiguous Cog: %s' % text
            return
        try:
            from toontown.avatar import ToontownAvatarUtils
            suit = ToontownAvatarUtils.createCog(suitType, coll=False)
            avatar = getattr(base, 'localAvatar', None)
            if avatar is not None:
                suit.reparentTo(avatar)
                suit.setPos(0, 8, 0)
                suit.setH(180)
                suit.wrtReparentTo(render)
            else:
                suit.reparentTo(render)
                suit.setPos(0, 8, 0)
            suit.loop('neutral')
        except Exception as error:
            self.resourceStatus['text'] = 'Could not spawn Cog: %s' % error
            print(('[Cutscene Editor] Cog spawn error: %s' % error))
            return
        self.spawnedSuits.append(suit)
        self.spawnedSuitTypes.append(suitType)
        self._addSpawnedSuitToScene(suit)
        self._captureBaseline()
        self._refreshAll()
        self._rebuildPreview(self._currentTime())
        self.resourceStatus['text'] = 'Spawned %s for this editor scene.' % _safeName(suit, suitType)

    def removeLastSpawnedSuit(self):
        if not self.spawnedSuits:
            self.resourceStatus['text'] = 'No editor-spawned Cogs to remove.'
            return
        suit = self.spawnedSuits.pop()
        if self.spawnedSuitTypes:
            self.spawnedSuitTypes.pop()
        for key in ('suits', 'actors', 'nodes'):
            values = self.cutsceneDict.get(key, [])
            if suit in values:
                values.remove(suit)
        try:
            suit.delete()
        except:
            try:
                suit.removeNode()
            except:
                pass
        self._captureBaseline()
        self._refreshAll()
        self._rebuildPreview(self._currentTime())
        self.resourceStatus['text'] = 'Removed the last editor-spawned Cog.'

    def refreshScene(self):
        oldMessages = self.cutsceneDict.get('messages', [])
        oldSounds = self.cutsceneDict.get('sounds', [])
        oldMusic = self.cutsceneDict.get('music', [])
        oldFunctions = self.cutsceneDict.get('functions', [])
        oldArguments = self.cutsceneDict.get('arguments', [])
        self.cutsceneDict = _defaultCutsceneDict()
        for suit in self.spawnedSuits:
            self._addSpawnedSuitToScene(suit)
        self.cutsceneDict['messages'] = oldMessages
        self.cutsceneDict['sounds'] = oldSounds
        self.cutsceneDict['music'] = oldMusic
        self._reloadSavedResources()
        self.cutsceneDict['functions'] = oldFunctions
        self.cutsceneDict['arguments'] = oldArguments
        self._captureBaseline()
        self._refreshAll()
        self._rebuildPreview(self._currentTime())

    def addMessage(self):
        text = self.messageEntry.get()
        if not text:
            return
        self.cutsceneDict['messages'].append(text)
        self.messageEntry.enterText('')
        self._refreshAll()

    def addNode(self):
        pattern = self.nodeEntry.get().strip()
        if not pattern:
            return
        node = render.find(pattern)
        if node.isEmpty():
            self.resourceStatus['text'] = 'Node not found: %s' % pattern
            return
        if node not in self.cutsceneDict['nodes']:
            self.cutsceneDict['nodes'].append(node)
        if pattern not in self.nodePatterns:
            self.nodePatterns.append(pattern)
        self._captureBaseline()
        self._refreshAll()

    def addSfx(self):
        path = self.audioEntry.get().strip()
        if not path:
            return
        try:
            sound = loader.loadSfx(path)
        except:
            sound = None
        if sound is None:
            self.resourceStatus['text'] = 'Could not load SFX: %s' % path
            return
        self.cutsceneDict['sounds'].append(sound)
        self.sfxPaths.append(path)
        self.audioEntry.enterText('')
        self._refreshAll()

    def addMusic(self):
        path = self.audioEntry.get().strip()
        if not path:
            return
        try:
            music = loader.loadMusic(path)
        except:
            music = None
        if music is None:
            self.resourceStatus['text'] = 'Could not load music: %s' % path
            return
        self.cutsceneDict['music'].append(music)
        self.musicPaths.append(path)
        self.audioEntry.enterText('')
        self._refreshAll()

    def _currentTime(self):
        if self.track is not None:
            try:
                return self.track.getT()
            except:
                pass
        try:
            return max(0.0, float(self.timeEntry.get()))
        except:
            return 0.0

    def setTime(self, timeValue):
        timeValue = max(0.0, min(float(timeValue), self.trackLength))
        if self.track is None:
            self._rebuildPreview(timeValue)
        else:
            wasPlaying = self.playing
            try:
                self.track.pause()
                self.track.setT(timeValue)
            except:
                self._rebuildPreview(timeValue)
            if wasPlaying and self.track is not None:
                try:
                    self.track.resume()
                except:
                    pass
        self.timeEntry.enterText('%.3f' % timeValue)

    def _jumpTimeEntry(self, text):
        try:
            self.setTime(float(text))
        except:
            pass

    def _durationEntry(self, text):
        try:
            self.trackLength = max(0.1, float(text))
        except:
            self.durationEntry.enterText(str(self.trackLength))
            return
        self._rebuildPreview(min(self._currentTime(), self.trackLength))

    def _cleanupTrack(self):
        if self.track is not None:
            try:
                self.track.pause()
            except:
                pass
            try:
                self.track.finish()
            except:
                pass
            self.track = None
        for action in self.cutsceneDict.get('editorCleanup', []):
            if callable(action):
                try:
                    action()
                except:
                    pass
        self.cutsceneDict['editorCleanup'] = []
        self._restoreBaseline()

    def _rebuildPreview(self, timeValue=0.0):
        wasPlaying = self.playing
        self._cleanupTrack()
        try:
            self.track = buildCutsceneData(self.events, self.cutsceneDict, '<Cutscene Editor>', self.trackLength)
            self.track.start()
            self.track.pause()
            self.track.setT(max(0.0, min(timeValue, self.trackLength)))
            if wasPlaying:
                self.track.resume()
        except Exception as error:
            self.track = None
            self.playing = False
            self.playButton['text'] = 'Play'
            self.resourceStatus['text'] = 'Preview error: %s' % error
            print(('[Cutscene Editor] Preview error: %s' % error))

    def _handleEscape(self):
        if self.previewMode:
            self._endPreviewMode()
            return
        self.close()

    def previewFullScreen(self):
        if self.previewMode:
            return
        self.restartPreview()
        if self.track is None:
            return
        self.previewMode = True
        try:
            self.root.hide()
        except:
            pass
        self.playing = True
        self.playButton['text'] = 'Pause'
        try:
            self.track.resume()
        except:
            self.playing = False
            self.previewMode = False
            self.playButton['text'] = 'Play'
            try:
                self.root.show()
            except:
                pass

    def _endPreviewMode(self):
        if not self.previewMode:
            return
        self.previewMode = False
        self.playing = False
        try:
            if self.track is not None:
                self.track.pause()
        except:
            pass
        self.playButton['text'] = 'Play'
        try:
            self.root.show()
        except:
            pass
        self.timeEntry.enterText('%.3f' % self._currentTime())

    def togglePlay(self):
        if self.track is None:
            self._rebuildPreview(self._currentTime())
        if self.track is None:
            return
        if self.playing:
            self.playing = False
            self.playButton['text'] = 'Play'
            try:
                self.track.pause()
            except:
                pass
        else:
            if self._currentTime() >= self.trackLength - 0.01:
                self.setTime(0.0)
            self.playing = True
            self.playButton['text'] = 'Pause'
            try:
                self.track.resume()
            except:
                self.playing = False
                self.playButton['text'] = 'Play'

    def restartPreview(self):
        self.playing = False
        self.playButton['text'] = 'Play'
        self._rebuildPreview(0.0)
        self.setTime(0.0)

    def _updateTask(self, task):
        current = self._currentTime()
        if current > self.trackLength:
            current = self.trackLength
        self.timeLabel['text'] = '%.2f / %.2f' % (current, self.trackLength)
        if self.playing:
            self.timeEntry.enterText('%.3f' % current)
            if current >= self.trackLength - 0.02:
                if self.previewMode:
                    self._endPreviewMode()
                else:
                    self.playing = False
                    self.playButton['text'] = 'Play'
                    try:
                        self.track.pause()
                    except:
                        pass
        return task.cont

    def close(self):
        global _editor
        if self.previewMode:
            self._endPreviewMode()
        self.autosave()
        taskMgr.remove('altis-cutscene-editor-update')
        self.ignoreAll()
        self._cleanupTrack()
        for suit in list(self.spawnedSuits):
            try:
                suit.delete()
            except:
                try:
                    suit.removeNode()
                except:
                    pass
        self.spawnedSuits = []
        self.spawnedSuitTypes = []
        try:
            self.root.destroy()
        except:
            pass
        try:
            if getattr(self, 'buttonGui', None) is not None:
                self.buttonGui.removeNode()
        except:
            pass
        self.buttonGui = None
        self.toonButtonImages = None
        _editor = None


def openEditor():
    global _editor
    if _editor is not None:
        return 'The Cutscene Editor is already open.'
    _editor = AltisCutsceneEditor()
    return 'Opened the Cutscene Editor.'


def toggleEditor():
    global _editor
    if _editor is None:
        return openEditor()
    _editor.close()
    return 'Closed the Cutscene Editor.'
