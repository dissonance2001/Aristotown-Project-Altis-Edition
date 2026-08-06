import os
import struct

from direct.task.Task import Task


class MidiParseError(Exception):
    pass


class PianoMidiFile(object):
    """Small Standard MIDI File parser compatible with Python 2 and 3."""

    DEFAULT_TEMPO = 500000

    def __init__(self, filename):
        self.filename = filename
        self.format = 0
        self.trackCount = 0
        self.division = 480
        self.events = []
        self.duration = 0.0
        self.__parse()

    @staticmethod
    def __byteValue(value):
        if isinstance(value, int):
            return value
        return ord(value)

    @staticmethod
    def __readUInt16(data, offset):
        if offset + 2 > len(data):
            raise MidiParseError('Unexpected end of MIDI data.')
        return struct.unpack('>H', data[offset:offset + 2])[0], offset + 2

    @staticmethod
    def __readUInt32(data, offset):
        if offset + 4 > len(data):
            raise MidiParseError('Unexpected end of MIDI data.')
        return struct.unpack('>I', data[offset:offset + 4])[0], offset + 4

    def __readVariableLength(self, data, offset):
        value = 0
        count = 0
        while True:
            if offset >= len(data):
                raise MidiParseError('Truncated variable-length MIDI value.')
            byte = self.__byteValue(data[offset])
            offset += 1
            value = (value << 7) | (byte & 0x7f)
            count += 1
            if not byte & 0x80:
                return value, offset
            if count >= 4:
                raise MidiParseError('Invalid variable-length MIDI value.')

    def __parseTrack(self, data, trackIndex):
        offset = 0
        tick = 0
        runningStatus = None
        sequence = 0
        parsed = []

        while offset < len(data):
            delta, offset = self.__readVariableLength(data, offset)
            tick += delta
            if offset >= len(data):
                break

            first = self.__byteValue(data[offset])
            if first & 0x80:
                status = first
                offset += 1
                if status < 0xf0:
                    runningStatus = status
            else:
                if runningStatus is None:
                    raise MidiParseError('Running status used before a status byte.')
                status = runningStatus

            if status == 0xff:
                runningStatus = None
                if offset >= len(data):
                    raise MidiParseError('Truncated MIDI meta event.')
                metaType = self.__byteValue(data[offset])
                offset += 1
                length, offset = self.__readVariableLength(data, offset)
                payload = data[offset:offset + length]
                if len(payload) != length:
                    raise MidiParseError('Truncated MIDI meta payload.')
                offset += length

                if metaType == 0x51 and length == 3:
                    tempo = ((self.__byteValue(payload[0]) << 16) |
                             (self.__byteValue(payload[1]) << 8) |
                             self.__byteValue(payload[2]))
                    parsed.append((tick, 0, trackIndex, sequence,
                                   'tempo', tempo, 0))
                    sequence += 1
                elif metaType == 0x2f:
                    break
                continue

            if status == 0xf0 or status == 0xf7:
                runningStatus = None
                length, offset = self.__readVariableLength(data, offset)
                offset += length
                if offset > len(data):
                    raise MidiParseError('Truncated MIDI system-exclusive event.')
                continue

            eventType = status & 0xf0
            channel = status & 0x0f
            if eventType in (0xc0, 0xd0):
                dataLength = 1
            elif 0x80 <= eventType <= 0xe0:
                dataLength = 2
            else:
                raise MidiParseError('Unsupported MIDI status 0x%02X.' % status)

            values = []
            for unused in xrange(dataLength):
                if offset >= len(data):
                    raise MidiParseError('Truncated MIDI channel event.')
                values.append(self.__byteValue(data[offset]))
                offset += 1

            # Channel 10 is normally percussion.  A piano should not translate
            # drum hits into random pitched notes.
            if eventType == 0x90 and values[1] > 0 and channel != 9:
                parsed.append((tick, 1, trackIndex, sequence,
                               'note', values[0], values[1]))
                sequence += 1

        return parsed

    def __parse(self):
        try:
            handle = open(self.filename, 'rb')
            data = handle.read()
            handle.close()
        except IOError as error:
            raise MidiParseError(str(error))

        if len(data) < 14 or data[0:4] != b'MThd':
            raise MidiParseError('This is not a Standard MIDI File.')

        headerLength, offset = self.__readUInt32(data, 4)
        if headerLength < 6 or 8 + headerLength > len(data):
            raise MidiParseError('Invalid MIDI header length.')

        self.format, cursor = self.__readUInt16(data, 8)
        self.trackCount, cursor = self.__readUInt16(data, cursor)
        self.division, cursor = self.__readUInt16(data, cursor)
        if self.format not in (0, 1):
            raise MidiParseError('Only MIDI format 0 and format 1 are supported.')
        offset = 8 + headerLength

        if self.division & 0x8000:
            raise MidiParseError('SMPTE-timed MIDI files are not supported.')
        if self.division <= 0:
            raise MidiParseError('Invalid MIDI timing division.')

        rawEvents = []
        for trackIndex in xrange(self.trackCount):
            if offset + 8 > len(data) or data[offset:offset + 4] != b'MTrk':
                raise MidiParseError('Missing MIDI track %d.' % (trackIndex + 1))
            trackLength, trackDataOffset = self.__readUInt32(data, offset + 4)
            trackStart = trackDataOffset
            trackEnd = trackStart + trackLength
            if trackEnd > len(data):
                raise MidiParseError('Truncated MIDI track %d.' % (trackIndex + 1))
            rawEvents.extend(self.__parseTrack(data[trackStart:trackEnd], trackIndex))
            offset = trackEnd

        rawEvents.sort()
        tempo = self.DEFAULT_TEMPO
        lastTick = 0
        currentSeconds = 0.0
        noteEvents = []

        for tick, priority, trackIndex, sequence, kind, valueA, valueB in rawEvents:
            deltaTicks = tick - lastTick
            if deltaTicks:
                currentSeconds += (float(deltaTicks) * float(tempo) /
                                   float(self.division) / 1000000.0)
                lastTick = tick

            if kind == 'tempo':
                tempo = valueA
            elif kind == 'note':
                noteEvents.append((currentSeconds, valueA, valueB))

        self.events = noteEvents
        if noteEvents:
            self.duration = noteEvents[-1][0]


class PianoMidiPlayer(object):
    # Full five-C range used by the GUI and MIDI playback.
    MIN_NOTE = 36  # C2
    MAX_NOTE = 84  # C6

    def __init__(self, noteCallback, statusCallback=None):
        self.noteCallback = noteCallback
        self.statusCallback = statusCallback
        self.events = []
        self.duration = 0.0
        self.filename = None
        self.index = 0
        self.playhead = 0.0
        self.lastClock = 0.0
        self.playing = False
        self.speed = 1.0
        self.transpose = 0
        self.taskName = 'PianoMidiPlayer-%s' % id(self)

    def __status(self, message):
        if self.statusCallback:
            self.statusCallback(message)

    @staticmethod
    def listMidiFiles(directory):
        try:
            if not os.path.isdir(directory):
                os.makedirs(directory)
        except OSError:
            pass

        try:
            names = os.listdir(directory)
        except OSError:
            return []

        files = []
        for name in names:
            lower = name.lower()
            if lower.endswith('.mid') or lower.endswith('.midi'):
                path = os.path.join(directory, name)
                if os.path.isfile(path):
                    files.append(name)
        files.sort(key=lambda value: value.lower())
        return files

    def load(self, filename):
        self.stop()
        midi = PianoMidiFile(filename)
        self.filename = filename
        self.events = midi.events
        self.duration = midi.duration
        self.index = 0
        self.playhead = 0.0
        self.__status('Loaded %s (%d piano notes, %s)' % (
            os.path.basename(filename), len(self.events),
            self.formatTime(self.duration)))
        return len(self.events)

    def play(self):
        if not self.events:
            self.__status('Select a MIDI file containing note events.')
            return False
        if self.index >= len(self.events):
            self.index = 0
            self.playhead = 0.0

        self.playing = True
        self.lastClock = globalClock.getFrameTime()
        taskMgr.remove(self.taskName)
        taskMgr.add(self.__playTask, self.taskName)
        self.__status('Playing %s' % os.path.basename(self.filename))
        return True

    def pause(self):
        if not self.playing:
            return
        self.playing = False
        taskMgr.remove(self.taskName)
        self.__status('Paused at %s' % self.formatTime(self.playhead))

    def stop(self):
        self.playing = False
        taskMgr.remove(self.taskName)
        self.index = 0
        self.playhead = 0.0
        if self.filename:
            self.__status('Stopped.')

    def setSpeed(self, speed):
        try:
            speed = float(speed)
        except (TypeError, ValueError):
            speed = 1.0
        self.speed = max(0.25, min(4.0, speed))

    def setTranspose(self, semitones):
        try:
            semitones = int(semitones)
        except (TypeError, ValueError):
            semitones = 0
        self.transpose = max(-24, min(24, semitones))

    def __mapNote(self, note):
        note += self.transpose
        while note < self.MIN_NOTE:
            note += 12
        while note > self.MAX_NOTE:
            note -= 12
        return note

    def __playTask(self, task):
        if not self.playing:
            return Task.done

        now = globalClock.getFrameTime()
        elapsed = max(0.0, now - self.lastClock)
        self.lastClock = now
        self.playhead += elapsed * self.speed

        eventCount = len(self.events)
        while self.index < eventCount and self.events[self.index][0] <= self.playhead:
            unusedTime, note, velocity = self.events[self.index]
            self.noteCallback(self.__mapNote(note), velocity, True)
            self.index += 1

        if self.index >= eventCount:
            self.playing = False
            self.__status('Finished %s' % os.path.basename(self.filename))
            return Task.done

        return Task.cont

    def destroy(self):
        self.playing = False
        taskMgr.remove(self.taskName)
        self.events = []
        self.noteCallback = None
        self.statusCallback = None

    @staticmethod
    def formatTime(seconds):
        seconds = max(0, int(round(seconds)))
        return '%d:%02d' % (seconds // 60, seconds % 60)
