import os
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectGui import (DirectButton, DirectFrame, DirectLabel,
                                  DirectSlider)
from direct.task.Task import Task
from pandac.PandaModules import KeyboardButton, TextNode, TransparencyAttrib
from toontown.safezone.PianoMidiPlayer import PianoMidiPlayer, MidiParseError
from toontown.toon.socialpanel.SocialPanelGlobals import sp_gui
from toontown.toonbase import ToontownGlobals
class PianoSoundBank(object):
    SOURCE_MIN_NOTE = 41
    SOURCE_MAX_NOTE = 64
    MIN_NOTE = 36
    MAX_NOTE = 84
    VOICES_PER_NOTE = 3
    def __init__(self, audioDirectory):
        self.audioDirectory = audioDirectory
        self.voices = {}
        self.voiceIndexes = {}
        self.playRates = {}
        self.masterVolume = 1.0
        self.__load()
    def __sampleForNote(self, note):
        sourceNote = note
        while sourceNote < self.SOURCE_MIN_NOTE:
            sourceNote += 12
        while sourceNote > self.SOURCE_MAX_NOTE:
            sourceNote -= 12
        sourceNote = max(self.SOURCE_MIN_NOTE,
                         min(self.SOURCE_MAX_NOTE, sourceNote))
        playRate = 2.0 ** ((float(note) - float(sourceNote)) / 12.0)
        return sourceNote, playRate
    def __load(self):
        for note in xrange(self.MIN_NOTE, self.MAX_NOTE + 1):
            sourceNote, playRate = self.__sampleForNote(note)
            sampleIndex = sourceNote - self.SOURCE_MIN_NOTE + 1
            filename = '%s/key%02d.ogg' % (
                self.audioDirectory.rstrip('/\\'), sampleIndex)
            filename = filename.replace('\\', '/')
            noteVoices = []
            for unused in xrange(self.VOICES_PER_NOTE):
                sound = loader.loadSfx(filename)
                if sound:
                    try:
                        sound.setPlayRate(playRate)
                    except:
                        pass
                    noteVoices.append(sound)
            self.voices[note] = noteVoices
            self.voiceIndexes[note] = 0
            self.playRates[note] = playRate
    def setMasterVolume(self, volume):
        try:
            volume = float(volume)
        except (TypeError, ValueError):
            volume = 1.0
        self.masterVolume = max(0.0, min(1.0, volume))
    def play(self, note, velocity=110):
        voices = self.voices.get(note, [])
        if not voices:
            return
        index = self.voiceIndexes[note] % len(voices)
        self.voiceIndexes[note] = index + 1
        sound = voices[index]
        try:
            velocity = max(1, min(127, int(velocity)))
        except (TypeError, ValueError):
            velocity = 110
        velocityVolume = 0.55 + (float(velocity) / 127.0) * 0.45
        volume = self.masterVolume * velocityVolume
        try:
            sound.stop()
            sound.setTime(0.0)
            sound.setPlayRate(self.playRates.get(note, 1.0))
            sound.setVolume(volume)
            sound.play()
        except:
            base.playSfx(sound, volume=volume)
    def stopAll(self):
        for voices in self.voices.values():
            for sound in voices:
                try:
                    sound.stop()
                except:
                    pass
    def destroy(self):
        self.stopAll()
        self.voices = {}
        self.voiceIndexes = {}
        self.playRates = {}
class PianoGui(DirectFrame):
    MIN_NOTE = 36
    MAX_NOTE = 84
    WINDOW_STARTS = (36, 48, 60)
    WINDOW_SIZE = 25
    NOTE_NAMES = ('C', 'C#', 'D', 'D#', 'E', 'F',
                  'F#', 'G', 'G#', 'A', 'A#', 'B')
    WHITE_CLASSES = (0, 2, 4, 5, 7, 9, 11)
    RAW_MAIN_WHITE_KEYS = ('a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'")
    RAW_EXTRA_WHITE_KEYS = ('z', 'x', '.', '/')
    RAW_BLACK_KEYS = ('q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p')
    RAW_EVENT_ALIASES = {';': ('raw-;', 'raw-semicolon'),
                         "'": ("raw-'", 'raw-apostrophe', 'raw-quote'),
                         '[': ('raw-[', 'raw-open_bracket', 'raw-lbracket'),
                         '.': ('raw-.', 'raw-period'),
                         '/': ('raw-/', 'raw-slash')}
    AZERTY_WHITE_LABELS = ('Q', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M', '%')
    AZERTY_EXTRA_WHITE_LABELS = ('W', 'X', ':', '!')
    AZERTY_BLACK_LABELS = ('A', 'Z', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P')
    QWERTY_WHITE_LABELS = ('A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', "'")
    QWERTY_EXTRA_WHITE_LABELS = ('Z', 'X', '.', '/')
    QWERTY_BLACK_LABELS = ('Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P')
    SPEED_VALUES = (0.5, 1.0, 1.5)
    def __init__(self, closeCommand, audioDirectory, midiDirectory):
        DirectFrame.__init__(
            self,
            parent=aspect2d,
            relief=DGG.RAISED,
            frameSize=(-1.29, 1.29, -0.86, 0.86),
            frameColor=(0.12, 0.10, 0.13, 0.98),
            borderWidth=(0.012, 0.012),
        )
        self.initialiseoptions(PianoGui)
        self.setTransparency(TransparencyAttrib.MAlpha)
        self.setBin('sorted-gui-popup', 700)
        self.closeCommand = closeCommand
        self.audioDirectory = audioDirectory
        self.midiDirectory = midiDirectory
        self.destroyed = False
        self.soundBank = PianoSoundBank(audioDirectory)
        self.midiPlayer = PianoMidiPlayer(self.playNote, self.__setStatus)
        self.keyButtons = []
        self.keyBaseColors = []
        self.heldKeys = {}
        self.useRawKeyboard = self.__rawKeyboardAvailable()
        self.keyboardLayout = self.__detectKeyboardLayout()
        self.slotKeyLabels, self.keyEventBindings = self.__makeKeyboardLayout()
        self.keyboardEventNames = []
        self.orangeButtonGeom = (sp_gui.find('**/OrangeButton_N'),
                                 sp_gui.find('**/OrangeButton_P'),
                                 sp_gui.find('**/OrangeButton_H'))
        self.blueButtonColors = ((0.10, 0.38, 0.63, 1.0),
                                 (0.06, 0.23, 0.41, 1.0),
                                 (0.17, 0.56, 0.78, 1.0),
                                 (0.12, 0.18, 0.24, 0.78))
        self.redButtonColors = ((0.64, 0.16, 0.20, 1.0),
                                (0.42, 0.08, 0.12, 1.0),
                                (0.82, 0.25, 0.29, 1.0),
                                (0.28, 0.12, 0.14, 0.78))
        self.windowIndex = 1
        self.windowStartNote = self.WINDOW_STARTS[self.windowIndex]
        self.songFiles = []
        self.selectedSong = None
        self.selectedSongIndex = -1
        self.midiVisible = False
        self.previousVolume = 1.0
        self.speedIndex = 1
        self.transposeValue = 0
        self.pendingMidiNotes = []
        self.midiFollowScheduled = False
        self.midiFollowTaskName = 'PianoGui-midiFollow-%s' % id(self)
        self.__makeHeader()
        self.__makeTopControls()
        self.__makeMidiControls()
        self.__makeKeyboard()
        self.__bindKeyboard()
        self.__refreshKeyboardLabels()
        self.refreshMidiFiles()
        self.__setMidiVisible(False)
    def __styleButton(self, button, closeButton=False):
        frame = button['frameSize']
        width = frame[1] - frame[0]
        height = frame[3] - frame[2]
        colors = self.redButtonColors if closeButton else self.blueButtonColors
        button['relief'] = None
        button['frameColor'] = (0, 0, 0, 0)
        button['geom'] = self.orangeButtonGeom
        button['geom_scale'] = (width * 0.98, 1, height)
        button['geom_pos'] = (0, 0, 0)
        button['geom0_color'] = colors[0]
        button['geom1_color'] = colors[1]
        button['geom2_color'] = colors[2]
        button['geom3_color'] = colors[3]
        button['pressEffect'] = 0
        button['text_align'] = TextNode.ACenter
        button['text_pos'] = (0, -0.012)
        button['text_fg'] = (1.0, 1.0, 1.0, 1.0)
        button['text_shadow'] = (0.0, 0.0, 0.0, 1.0)
        button['text_shadowOffset'] = (0.015, 0.015)
        button['text_font'] = ToontownGlobals.getInterfaceFont()
        return button
    def __styleSlider(self, slider):
        slider['relief'] = DGG.FLAT
        slider['frameColor'] = (0.035, 0.055, 0.065, 1.0)
        slider['borderWidth'] = (0.005, 0.005)
        try:
            thumb = slider.component('thumb')
            thumb['relief'] = None
            thumb['frameColor'] = (0, 0, 0, 0)
            thumb['frameSize'] = (-0.06, 0.06, -0.22, 0.22)
            thumb['pressEffect'] = 0
        except:
            pass
        marker = DirectFrame(
            parent=slider,
            relief=None,
            frameSize=(-0.055, 0.055, -0.19, 0.19),
            frameColor=(0, 0, 0, 0),
            geom=self.orangeButtonGeom[0],
            geom_scale=(0.11, 1, 0.38),
            geom_color=self.blueButtonColors[0],
            state=DGG.DISABLED,
        )
        marker.setBin('sorted-gui-popup', 704)
        slider.pianoMarker = marker
        self.__updateSliderMarker(slider)
        return slider
    def __updateSliderMarker(self, slider):
        if not hasattr(slider, 'pianoMarker'):
            return
        minimum, maximum = slider['range']
        value = float(slider['value'])
        if maximum == minimum:
            x = 0.0
        else:
            x = -1.0 + 2.0 * ((value - minimum) / float(maximum - minimum))
        slider.pianoMarker.setX(x)
    def __makeHeader(self):
        self.title = DirectLabel(
            parent=self,
            relief=None,
            text='Grand Piano',
            text_scale=0.085,
            text_fg=(1.0, 0.92, 0.65, 1.0),
            text_shadow=(0, 0, 0, 1),
            pos=(0, 0, 0.75),
        )
        self.subtitle = DirectLabel(
            parent=self,
            relief=None,
            text='49-note range: C2-C6',
            text_scale=0.038,
            text_fg=(0.92, 0.92, 0.92, 1.0),
            pos=(0, 0, 0.665),
        )
        self.closeButton = DirectButton(
            parent=self,
            relief=DGG.RAISED,
            text='X',
            text_scale=0.055,
            frameSize=(-0.075, 0.075, -0.065, 0.065),
            frameColor=(0.55, 0.16, 0.18, 1.0),
            pos=(1.16, 0, 0.75),
            command=self.__requestClose,
        )
        self.__styleButton(self.closeButton, closeButton=True)
        self.layoutButton = DirectButton(
            parent=self,
            relief=None,
            text=self.keyboardLayout.upper(),
            text_scale=0.036,
            frameSize=(-0.17, 0.17, -0.052, 0.052),
            pos=(-1.03, 0, 0.75),
            command=self.__toggleKeyboardLayout,
            pressEffect=0,
        )
        self.__styleButton(self.layoutButton)
        self.accept('escape', self.__requestClose)
    def __makeTopControls(self):
        self.midiToggleButton = DirectButton(
            parent=self,
            relief=DGG.RAISED,
            text='Show',
            text_scale=0.041,
            frameSize=(-0.16, 0.16, -0.055, 0.055),
            pos=(-1.02, 0, 0.565),
            command=self.__toggleMidi,
            pressEffect=0,
        )
        self.__styleButton(self.midiToggleButton)
        self.octaveDownButton = DirectButton(
            parent=self,
            relief=DGG.RAISED,
            text='<',
            text_scale=0.052,
            frameSize=(-0.07, 0.07, -0.055, 0.055),
            pos=(-0.62, 0, 0.565),
            command=self.__changeWindow,
            extraArgs=[-1],
            pressEffect=0,
        )
        self.__styleButton(self.octaveDownButton)
        self.rangeLabel = DirectLabel(
            parent=self,
            relief=None,
            text='',
            text_scale=0.039,
            text_fg=(1, 1, 1, 1),
            pos=(-0.36, 0, 0.565),
        )
        self.octaveUpButton = DirectButton(
            parent=self,
            relief=DGG.RAISED,
            text='>',
            text_scale=0.052,
            frameSize=(-0.07, 0.07, -0.055, 0.055),
            pos=(-0.09, 0, 0.565),
            command=self.__changeWindow,
            extraArgs=[1],
            pressEffect=0,
        )
        self.__styleButton(self.octaveUpButton)
        self.volumeLabel = DirectLabel(
            parent=self,
            relief=None,
            text='Volume: 100%',
            text_scale=0.037,
            text_fg=(1, 1, 1, 1),
            pos=(0.30, 0, 0.565),
        )
        self.volumeSlider = DirectSlider(
            parent=self,
            range=(0.0, 1.0),
            value=1.0,
            pageSize=0.05,
            scale=0.28,
            pos=(0.73, 0, 0.565),
            command=self.__volumeChanged,
        )
        self.__styleSlider(self.volumeSlider)
        self.muteButton = DirectButton(
            parent=self,
            relief=DGG.RAISED,
            text='Mute',
            text_scale=0.037,
            frameSize=(-0.11, 0.11, -0.05, 0.05),
            pos=(1.10, 0, 0.565),
            command=self.__toggleMute,
            pressEffect=0,
        )
        self.__styleButton(self.muteButton)
    def __makeMidiControls(self):
        self.midiPanel = DirectFrame(
            parent=self,
            relief=DGG.RIDGE,
            frameSize=(-1.18, 1.18, -0.225, 0.225),
            frameColor=(0.18, 0.16, 0.20, 0.98),
            borderWidth=(0.008, 0.008),
            pos=(0, 0, 0.285),
        )
        self.midiPanel.setTransparency(TransparencyAttrib.MAlpha)
        self.songLabel = DirectLabel(
            parent=self.midiPanel, relief=None, text='Song:',
            text_align=TextNode.ARight, text_scale=0.041,
            text_fg=(1, 1, 1, 1), pos=(-1.04, 0, 0.145))
        self.previousSongButton = DirectButton(
            parent=self.midiPanel, relief=DGG.RAISED,
            text='<', text_scale=0.045,
            frameSize=(-0.07, 0.07, -0.048, 0.048),
            pos=(-0.84, 0, 0.145), command=self.__changeSong,
            extraArgs=[-1], pressEffect=0)
        self.__styleButton(self.previousSongButton)
        self.songNameLabel = DirectLabel(
            parent=self.midiPanel, relief=DGG.SUNKEN,
            frameSize=(-0.62, 0.62, -0.048, 0.048),
            frameColor=(0.08, 0.09, 0.10, 1.0),
            borderWidth=(0.004, 0.004),
            text='No MIDI files found', text_scale=0.036,
            text_fg=(1.0, 1.0, 0.92, 1.0),
            text_align=TextNode.ACenter, pos=(-0.12, 0, 0.145))
        self.nextSongButton = DirectButton(
            parent=self.midiPanel, relief=DGG.RAISED,
            text='>', text_scale=0.045,
            frameSize=(-0.07, 0.07, -0.048, 0.048),
            pos=(0.61, 0, 0.145), command=self.__changeSong,
            extraArgs=[1], pressEffect=0)
        self.__styleButton(self.nextSongButton)
        self.songCounterLabel = DirectLabel(
            parent=self.midiPanel, relief=None, text='0 / 0',
            text_scale=0.032, text_fg=(0.82, 0.88, 1.0, 1.0),
            pos=(0.77, 0, 0.145))
        self.refreshButton = DirectButton(
            parent=self.midiPanel, relief=DGG.RAISED,
            text='Refresh', text_scale=0.035,
            frameSize=(-0.105, 0.105, -0.048, 0.048),
            pos=(1.04, 0, 0.145), command=self.refreshMidiFiles,
            pressEffect=0)
        self.__styleButton(self.refreshButton)
        self.playButton = DirectButton(
            parent=self.midiPanel, relief=DGG.RAISED,
            text='Play', text_scale=0.041,
            frameSize=(-0.115, 0.115, -0.05, 0.05),
            pos=(-0.91, 0, 0.015), command=self.__playMidi, pressEffect=0)
        self.__styleButton(self.playButton)
        self.pauseButton = DirectButton(
            parent=self.midiPanel, relief=DGG.RAISED,
            text='Pause', text_scale=0.041,
            frameSize=(-0.115, 0.115, -0.05, 0.05),
            pos=(-0.63, 0, 0.015), command=self.midiPlayer.pause, pressEffect=0)
        self.__styleButton(self.pauseButton)
        self.stopButton = DirectButton(
            parent=self.midiPanel, relief=DGG.RAISED,
            text='Stop', text_scale=0.041,
            frameSize=(-0.115, 0.115, -0.05, 0.05),
            pos=(-0.35, 0, 0.015), command=self.__stopMidi, pressEffect=0)
        self.__styleButton(self.stopButton)
        self.speedLabel = DirectLabel(
            parent=self.midiPanel, relief=None, text='Speed:',
            text_scale=0.038, text_fg=(1, 1, 1, 1),
            pos=(-0.04, 0, 0.015))
        self.speedButton = DirectButton(
            parent=self.midiPanel, relief=DGG.RAISED,
            text='1.00x', text_scale=0.037,
            frameSize=(-0.13, 0.13, -0.045, 0.045),
            pos=(0.22, 0, 0.015), command=self.__cycleSpeed,
            pressEffect=0)
        self.__styleButton(self.speedButton)
        self.transposeLabel = DirectLabel(
            parent=self.midiPanel, relief=None,
            text='Transpose: 0', text_scale=0.035,
            text_fg=(1, 1, 1, 1), pos=(0.61, 0, 0.015))
        self.transposeDownButton = DirectButton(
            parent=self.midiPanel, relief=DGG.RAISED,
            text='-', text_scale=0.045,
            frameSize=(-0.055, 0.055, -0.045, 0.045),
            pos=(0.91, 0, 0.015), command=self.__changeTranspose,
            extraArgs=[-1], pressEffect=0)
        self.__styleButton(self.transposeDownButton)
        self.transposeUpButton = DirectButton(
            parent=self.midiPanel, relief=DGG.RAISED,
            text='+', text_scale=0.045,
            frameSize=(-0.055, 0.055, -0.045, 0.045),
            pos=(1.08, 0, 0.015), command=self.__changeTranspose,
            extraArgs=[1], pressEffect=0)
        self.__styleButton(self.transposeUpButton)
        self.statusLabel = DirectLabel(
            parent=self.midiPanel,
            relief=None,
            text='',
            text_scale=0.031,
            text_fg=(0.82, 0.88, 1.0, 1.0),
            text_wordwrap=70,
            pos=(0, 0, -0.145),
        )
    def __makeKeyboard(self):
        self.keyboardHolder = DirectFrame(
            parent=self,
            relief=None,
            frameSize=(-1.2, 1.2, -0.38, 0.38),
            pos=(0, 0, -0.22),
        )
        startX = -1.04
        spacing = 0.148
        whiteIndex = 0
        for slot in xrange(self.WINDOW_SIZE):
            pitchClass = slot % 12
            keyName = self.slotKeyLabels.get(slot, '')
            if pitchClass in self.WHITE_CLASSES:
                x = startX + whiteIndex * spacing
                whiteIndex += 1
                color = (0.95, 0.95, 0.91, 1.0)
                button = DirectButton(
                    parent=self.keyboardHolder,
                    relief=DGG.FLAT,
                    pressEffect=0,
                    frameSize=(-0.069, 0.069, -0.33, 0.33),
                    frameColor=color,
                    borderWidth=(0.007, 0.007),
                    text=('[' + keyName + ']') if keyName else '',
                    text_scale=0.030,
                    text_fg=(0.08, 0.08, 0.08, 1.0),
                    text_pos=(0, -0.27),
                    pos=(x, 0, 0),
                    command=self.__mouseNote,
                    extraArgs=[slot],
                )
            else:
                x = startX + (whiteIndex - 0.5) * spacing
                color = (0.08, 0.08, 0.09, 1.0)
                button = DirectButton(
                    parent=self.keyboardHolder,
                    relief=DGG.FLAT,
                    pressEffect=0,
                    frameSize=(-0.044, 0.044, -0.20, 0.20),
                    frameColor=color,
                    borderWidth=(0.005, 0.005),
                    text=('[' + keyName + ']') if keyName else '',
                    text_scale=0.025,
                    text_fg=(1.0, 1.0, 1.0, 1.0),
                    text_pos=(0, -0.14),
                    pos=(x, -0.1, 0.135),
                    command=self.__mouseNote,
                    extraArgs=[slot],
                )
                button.setBin('sorted-gui-popup', 702)
            self.keyButtons.append(button)
            self.keyBaseColors.append(color)
        self.keyboardHelp = DirectLabel(
            parent=self,
            relief=None,
            text='%s layout.  Left / Right changes octave.' % self.keyboardLayout.upper(),
            text_scale=0.030,
            text_fg=(0.85, 0.85, 0.85, 1.0),
            pos=(0, 0, -0.79),
        )
    def __rawKeyboardAvailable(self):
        try:
            if base.win is None:
                return False
            try:
                base.win.getKeyboardMap()
            except AttributeError:
                base.win.get_keyboard_map()
            return True
        except:
            return False
    def __getKeyboardMap(self):
        if base.win is None:
            return None
        try:
            return base.win.getKeyboardMap()
        except AttributeError:
            try:
                return base.win.get_keyboard_map()
            except:
                return None
        except:
            return None
    def __mappedKeyLabel(self, rawKey, keyboardMap):
        label = ''
        if keyboardMap is not None:
            try:
                button = KeyboardButton.asciiKey(rawKey)
                label = keyboardMap.getMappedButtonLabel(button)
            except AttributeError:
                try:
                    button = KeyboardButton.ascii_key(rawKey)
                    label = keyboardMap.get_mapped_button_label(button)
                except:
                    label = ''
            except:
                label = ''
        try:
            return label.upper()
        except:
            return label
    def __detectKeyboardLayout(self):
        if not self.useRawKeyboard:
            return 'azerty'
        keyboardMap = self.__getKeyboardMap()
        qLabel = self.__mappedKeyLabel('q', keyboardMap)
        aLabel = self.__mappedKeyLabel('a', keyboardMap)
        if qLabel == 'A' or aLabel == 'Q':
            return 'azerty'
        if qLabel == 'Q' or aLabel == 'A':
            return 'qwerty'
        return 'azerty'
    def __makeKeyboardLayout(self):
        whiteSlots = [slot for slot in xrange(self.WINDOW_SIZE)
                      if slot % 12 in self.WHITE_CLASSES]
        blackSlots = [slot for slot in xrange(self.WINDOW_SIZE)
                      if slot % 12 not in self.WHITE_CLASSES]
        mainWhiteSlots = whiteSlots[2:-2]
        extraWhiteSlots = whiteSlots[:2] + whiteSlots[-2:]
        if self.keyboardLayout == 'azerty':
            whiteLabels = self.AZERTY_WHITE_LABELS
            extraWhiteLabels = self.AZERTY_EXTRA_WHITE_LABELS
            blackLabels = self.AZERTY_BLACK_LABELS
        else:
            whiteLabels = self.QWERTY_WHITE_LABELS
            extraWhiteLabels = self.QWERTY_EXTRA_WHITE_LABELS
            blackLabels = self.QWERTY_BLACK_LABELS
        labels = {}
        bindings = []
        for rawKey, label, slot in zip(self.RAW_MAIN_WHITE_KEYS,
                                       whiteLabels, mainWhiteSlots):
            labels[slot] = label
            bindings.append((rawKey, label, slot))
        for rawKey, label, slot in zip(self.RAW_EXTRA_WHITE_KEYS,
                                       extraWhiteLabels, extraWhiteSlots):
            labels[slot] = label
            bindings.append((rawKey, label, slot))
        for rawKey, label, slot in zip(self.RAW_BLACK_KEYS,
                                       blackLabels, blackSlots):
            labels[slot] = label
            bindings.append((rawKey, label, slot))
        return labels, bindings
    def __eventNamesForBinding(self, rawKey, label):
        if self.useRawKeyboard:
            return self.RAW_EVENT_ALIASES.get(rawKey, ('raw-' + rawKey,))
        value = label.lower()
        if label == '%':
            return ('%', 'shift-u_grave')
        if label == u'\u00a8':
            return ('^', 'shift-^', 'asciicircum')
        return (value,)
    def __unbindKeyboardNotes(self):
        for eventName in self.keyboardEventNames:
            self.ignore(eventName)
        self.keyboardEventNames = []
        self.heldKeys = {}
    def __bindKeyboard(self):
        self.accept('arrow_left', self.__changeWindow, [-1])
        self.accept('arrow_right', self.__changeWindow, [1])
        self.__unbindKeyboardNotes()
        for rawKey, label, slot in self.keyEventBindings:
            eventNames = self.__eventNamesForBinding(rawKey, label)
            bindingId = '%s:%s:%s' % (self.keyboardLayout, rawKey, slot)
            for eventName in eventNames:
                self.accept(eventName, self.__keyboardDown,
                            [bindingId, slot])
                self.accept(eventName + '-up', self.__keyboardUp,
                            [bindingId])
                self.keyboardEventNames.append(eventName)
                self.keyboardEventNames.append(eventName + '-up')
    def __toggleKeyboardLayout(self):
        self.keyboardLayout = ('qwerty' if self.keyboardLayout == 'azerty'
                               else 'azerty')
        self.slotKeyLabels, self.keyEventBindings = self.__makeKeyboardLayout()
        self.__bindKeyboard()
        self.__refreshKeyboardLabels()
        self.layoutButton['text'] = self.keyboardLayout.upper()
        self.keyboardHelp['text'] = '%s layout.  Left / Right changes octave.' % self.keyboardLayout.upper()
    def __noteName(self, note):
        octave = note // 12 - 1
        return '%s%d' % (self.NOTE_NAMES[note % 12], octave)
    def __currentNote(self, slot):
        return self.windowStartNote + slot
    def __refreshKeyboardLabels(self):
        for slot, button in enumerate(self.keyButtons):
            note = self.__currentNote(slot)
            keyName = self.slotKeyLabels.get(slot, '')
            noteName = self.__noteName(note)
            if note % 12 in self.WHITE_CLASSES:
                button['text'] = ('%s\n[%s]' % (noteName, keyName)
                                  if keyName else noteName)
            else:
                button['text'] = ('%s\n[%s]' % (noteName, keyName)
                                  if keyName else noteName)
        firstName = self.__noteName(self.windowStartNote)
        lastName = self.__noteName(self.windowStartNote + self.WINDOW_SIZE - 1)
        self.rangeLabel['text'] = '%s - %s' % (firstName, lastName)
        self.octaveDownButton['state'] = (
            DGG.DISABLED if self.windowIndex == 0 else DGG.NORMAL)
        self.octaveUpButton['state'] = (
            DGG.DISABLED if self.windowIndex == len(self.WINDOW_STARTS) - 1
            else DGG.NORMAL)
    def __setWindowIndex(self, newIndex, clearHeld=True):
        newIndex = max(0, min(len(self.WINDOW_STARTS) - 1, int(newIndex)))
        if newIndex == self.windowIndex:
            return False
        if clearHeld:
            for note in self.heldKeys.values():
                self.__setKeyHighlighted(note, False)
            self.heldKeys = {}
        self.windowIndex = newIndex
        self.windowStartNote = self.WINDOW_STARTS[newIndex]
        self.__refreshKeyboardLabels()
        return True
    def __changeWindow(self, direction):
        self.__setWindowIndex(self.windowIndex + int(direction), True)
    def __bestWindowForNote(self, note):
        candidates = []
        for index, startNote in enumerate(self.WINDOW_STARTS):
            if startNote <= note < startNote + self.WINDOW_SIZE:
                candidates.append(index)
        if self.windowIndex in candidates:
            return self.windowIndex
        if candidates:
            candidates.sort(key=lambda index: abs(index - self.windowIndex))
            return candidates[0]
        if note < self.WINDOW_STARTS[0]:
            return 0
        return len(self.WINDOW_STARTS) - 1
    def __queueMidiWindowFollow(self, note):
        self.pendingMidiNotes.append(note)
        if self.midiFollowScheduled:
            return
        self.midiFollowScheduled = True
        taskMgr.doMethodLater(
            0.012, self.__followMidiWindowTask, self.midiFollowTaskName)
    def __followMidiWindowTask(self, task):
        self.midiFollowScheduled = False
        if self.destroyed:
            return Task.done
        notes = self.pendingMidiNotes
        self.pendingMidiNotes = []
        if not notes:
            return Task.done
        targetNote = max(notes)
        self.__setWindowIndex(self.__bestWindowForNote(targetNote), False)
        for note in notes:
            self.__flashKey(note)
        return Task.done
    def __mouseNote(self, slot):
        self.playNote(self.__currentNote(slot), 112, False)
    def __keyboardDown(self, key, slot):
        if key in self.heldKeys:
            return
        note = self.__currentNote(slot)
        self.heldKeys[key] = note
        self.__setKeyHighlighted(note, True)
        self.soundBank.play(note, 112)
    def __keyboardUp(self, key):
        note = self.heldKeys.pop(key, None)
        if note is not None:
            self.__setKeyHighlighted(note, False)
    def playNote(self, note, velocity=110, fromMidi=False):
        if self.destroyed:
            return
        if note < self.MIN_NOTE or note > self.MAX_NOTE:
            return
        self.soundBank.play(note, velocity)
        if fromMidi:
            self.__queueMidiWindowFollow(note)
        else:
            self.__flashKey(note)
    def __flashKey(self, note):
        if not self.__noteIsVisible(note):
            return
        self.__setKeyHighlighted(note, True)
        taskName = 'PianoGui-keyFlash-%s-%s' % (id(self), note)
        taskMgr.remove(taskName)
        taskMgr.doMethodLater(
            0.12, self.__releaseFlashedKey, taskName, extraArgs=[note])
    def __releaseFlashedKey(self, note):
        if note not in self.heldKeys.values():
            self.__setKeyHighlighted(note, False)
        return Task.done
    def __noteIsVisible(self, note):
        return (self.windowStartNote <= note <
                self.windowStartNote + self.WINDOW_SIZE)
    def __setKeyHighlighted(self, note, highlighted):
        if not self.__noteIsVisible(note):
            return
        slot = note - self.windowStartNote
        if slot < 0 or slot >= len(self.keyButtons):
            return
        button = self.keyButtons[slot]
        if highlighted:
            button['frameColor'] = (1.0, 0.72, 0.22, 1.0)
        else:
            button['frameColor'] = self.keyBaseColors[slot]
    def __toggleMidi(self):
        self.__setMidiVisible(not self.midiVisible)
    def __setMidiVisible(self, visible):
        self.midiVisible = bool(visible)
        if self.midiVisible:
            self.midiPanel.show()
            self.midiToggleButton['text'] = 'Hide'
            self.keyboardHolder.setZ(-0.49)
            self.keyboardHelp.hide()
        else:
            self.midiPanel.hide()
            self.midiToggleButton['text'] = 'Show'
            self.keyboardHolder.setZ(-0.22)
            self.keyboardHelp.show()
    def __volumeChanged(self):
        value = float(self.volumeSlider['value'])
        self.soundBank.setMasterVolume(value)
        self.__updateSliderMarker(self.volumeSlider)
        percent = int(round(value * 100.0))
        self.volumeLabel['text'] = 'Volume: %d%%' % percent
        self.muteButton['text'] = 'Unmute' if percent == 0 else 'Mute'
    def __toggleMute(self):
        current = float(self.volumeSlider['value'])
        if current > 0.0:
            self.previousVolume = current
            self.volumeSlider['value'] = 0.0
        else:
            self.volumeSlider['value'] = max(0.05, self.previousVolume)
        self.__volumeChanged()
    def refreshMidiFiles(self):
        previousSelection = self.selectedSong
        self.songFiles = PianoMidiPlayer.listMidiFiles(self.midiDirectory)
        if self.songFiles:
            if previousSelection in self.songFiles:
                self.selectedSongIndex = self.songFiles.index(
                    previousSelection)
            else:
                self.selectedSongIndex = 0
            self.__updateSongSelection()
            self.__setStatus('Found %d MIDI file(s). Selected %s.' % (
                len(self.songFiles), self.selectedSong))
        else:
            self.selectedSong = None
            self.selectedSongIndex = -1
            self.__updateSongSelection()
            self.__setStatus(
                'Drop .mid or .midi files into %s, then Refresh.' %
                self.midiDirectory.replace('\\', '/'))
    def __changeSong(self, direction):
        if not self.songFiles:
            return
        self.selectedSongIndex = (self.selectedSongIndex + int(direction)) % (
            len(self.songFiles))
        self.__updateSongSelection()
        self.__setStatus('Selected %s. Press Play.' % self.selectedSong)
    def __updateSongSelection(self):
        hasSongs = bool(self.songFiles)
        state = DGG.NORMAL if hasSongs else DGG.DISABLED
        self.previousSongButton['state'] = state
        self.nextSongButton['state'] = state
        self.playButton['state'] = state
        if not hasSongs:
            self.selectedSong = None
            self.songNameLabel['text'] = 'No MIDI files found'
            self.songCounterLabel['text'] = '0 / 0'
            return
        self.selectedSongIndex = max(
            0, min(len(self.songFiles) - 1, self.selectedSongIndex))
        self.selectedSong = self.songFiles[self.selectedSongIndex]
        self.songNameLabel['text'] = self.selectedSong
        self.songCounterLabel['text'] = '%d / %d' % (
            self.selectedSongIndex + 1, len(self.songFiles))
    def __playMidi(self):
        if not self.selectedSong:
            self.__setStatus('Add a MIDI file and press Refresh first.')
            return
        fullPath = os.path.join(self.midiDirectory, self.selectedSong)
        if self.midiPlayer.filename != fullPath:
            try:
                self.midiPlayer.load(fullPath)
            except (MidiParseError, IOError, ValueError) as error:
                self.__setStatus('Could not load %s: %s' %
                                 (self.selectedSong, error))
                return
            except Exception as error:
                self.__setStatus('MIDI error in %s: %s' %
                                 (self.selectedSong, error))
                return
        self.midiPlayer.play()
    def __stopMidi(self):
        self.midiPlayer.stop()
        self.soundBank.stopAll()
    def __cycleSpeed(self):
        self.speedIndex = (self.speedIndex + 1) % len(self.SPEED_VALUES)
        speed = self.SPEED_VALUES[self.speedIndex]
        self.midiPlayer.setSpeed(speed)
        self.speedButton['text'] = '%.2fx' % speed
    def __changeTranspose(self, direction):
        self.transposeValue = max(-24, min(24, self.transposeValue + int(direction)))
        self.midiPlayer.setTranspose(self.transposeValue)
        self.transposeLabel['text'] = 'Transpose: %d' % self.transposeValue
        self.transposeDownButton['state'] = DGG.DISABLED if self.transposeValue <= -24 else DGG.NORMAL
        self.transposeUpButton['state'] = DGG.DISABLED if self.transposeValue >= 24 else DGG.NORMAL
    def __setStatus(self, message):
        if not self.destroyed and hasattr(self, 'statusLabel'):
            self.statusLabel['text'] = message
    def __requestClose(self):
        if self.closeCommand:
            self.closeCommand()
    def destroy(self):
        if self.destroyed:
            return
        self.destroyed = True
        self.ignoreAll()
        taskMgr.remove(self.midiFollowTaskName)
        self.pendingMidiNotes = []
        self.midiFollowScheduled = False
        for note in xrange(self.MIN_NOTE, self.MAX_NOTE + 1):
            taskMgr.remove('PianoGui-keyFlash-%s-%s' % (id(self), note))
        if self.midiPlayer is not None:
            self.midiPlayer.destroy()
            self.midiPlayer = None
        if self.soundBank is not None:
            self.soundBank.destroy()
            self.soundBank = None
        self.keyButtons = []
        self.keyBaseColors = []
        self.heldKeys = {}
        self.slotKeyLabels = {}
        self.keyEventBindings = []
        self.keyboardEventNames = []
        if getattr(self, 'buttonAssets', None) is not None:
            self.buttonAssets.removeNode()
            self.buttonAssets = None
            self.roundedButtonImage = None
        self.closeCommand = None
        DirectFrame.destroy(self)
