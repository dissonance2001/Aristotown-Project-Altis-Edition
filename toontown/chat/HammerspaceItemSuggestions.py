import re
from difflib import SequenceMatcher

from direct.gui.DirectGui import DirectLabel
from pandac.PandaModules import TextNode
from toontown.gui.TTGui import ScrollWheelFrame
from toontown.inventory.registry.ItemTypeRegistry import ItemTypeRegistry

MAX_SUGGESTIONS = 8
_ITEM_NAME_CACHE = None


def _normalize(value):
    return re.sub(r'[^a-z0-9]+', ' ', value.lower()).strip()


def _getItemNames():
    global _ITEM_NAME_CACHE
    if _ITEM_NAME_CACHE is not None:
        return _ITEM_NAME_CACHE
    names = []
    seen = set()
    for subtypeDict in ItemTypeRegistry.values():
        for itemSubtype, itemDef in subtypeDict.items():
            try:
                name = itemDef.getName()
            except Exception:
                continue
            if not name:
                continue
            key = (str(itemSubtype), name)
            if key in seen:
                continue
            seen.add(key)
            names.append(name)
    _ITEM_NAME_CACHE = names
    return _ITEM_NAME_CACHE


class HammerspaceItemSuggestions:
    def __init__(self, parent):
        self.frame = ScrollWheelFrame(
            parent=parent,
            relief=None,
            pos=(-0.205, 0, 0.38),
            scale=0.035,
            frameSize=(-0.02, 12.0, -0.02, 6.9),
            canvasSize=(-0.02, 12.0, -3.0, 7.0),
            autoHideScrollBars=False,
            manageScrollBars=False,
            verticalScroll_pos=(12.3, 0, 3.45),
            verticalScroll_frameSize=(-0.45, 0.45, -3.45, 3.45),
            verticalScroll_relief=None,
            verticalScroll_resizeThumb=0,
            verticalScroll_thumb_relief=None,
        )
        self.frame['scrollDistance'] = 2.0
        self.labels = []
        self.hide()

    def destroy(self):
        for label in self.labels:
            label.destroy()
        self.labels = []
        self.frame.destroy()

    def hide(self):
        self.frame.hide()

    def update(self, text):
        suggestions = self._getSuggestions(text)
        for label in self.labels:
            label.destroy()
        self.labels = []
        if not suggestions:
            self.hide()
            return

        for index, suggestion in enumerate(suggestions):
            label = DirectLabel(
                parent=self.frame.canvas,
                relief=None,
                pos=(0.1, 0, 6.55 - index * 0.62),
                scale=1.0,
                text=suggestion,
                text_align=TextNode.ALeft,
                text_fg=(1, 1, 1, 1),
                text_shadow=(0, 0, 0, 1),
                textMayChange=0,
                text_wordwrap=31,
            )
            self.labels.append(label)

        height = max(7.0, len(suggestions) * 0.62 + 0.3)
        canvasSize = self.frame['canvasSize']
        canvasSize[2] = -height
        canvasSize[3] = 7.0
        self.frame['canvasSize'] = canvasSize
        self.frame['scrollCorrection'] = None
        self.frame.verticalScroll.setValue(0)
        self.frame.show()

    def _getSuggestions(self, text):
        match = re.match(r'^(?:/|~)hammerspace\s+give(?:\s+|$)(.*)$', text, re.IGNORECASE)
        if not match:
            return []

        query = match.group(1).strip()
        if not query:
            return []

        parts = query.split(None, 1)
        if len(parts) == 2 and parts[0].isdigit():
            query = parts[1].strip()
        if not query:
            return []

        normalizedQuery = _normalize(query)
        if not normalizedQuery:
            return []

        output = []
        seen = set()
        for subtypeDict in ItemTypeRegistry.values():
            for itemSubtype, itemDef in subtypeDict.items():
                if itemSubtype in seen:
                    continue
                seen.add(itemSubtype)
                enumName = getattr(itemSubtype, 'name', str(itemSubtype))
                try:
                    displayName = itemDef.getName() or ''
                except Exception:
                    displayName = ''
                searchNames = (
                    _normalize(enumName),
                    _normalize(displayName),
                    str(getattr(itemSubtype, 'value', itemSubtype)).lower(),
                )
                if any(normalizedQuery in name for name in searchNames if name):
                    score = 1000 if any(name.startswith(normalizedQuery) for name in searchNames if name) else 900
                    output.append((score, enumName, displayName))

        output.sort(key=lambda result: (-result[0], result[1].lower()))
        return [
            '%s  |  %s' % (enumName, displayName) if displayName else enumName
            for _, enumName, displayName in output[:MAX_SUGGESTIONS]
        ]
