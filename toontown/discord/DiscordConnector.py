from __future__ import absolute_import
import json
from io import open as io_open
import os
import re
import socket
import struct
import subprocess
import time
import uuid
from datetime import datetime

from toontown.discord import DiscordPresets
from toontown.hood import ZoneUtil
from direct.directnotify.DirectNotifyGlobal import directNotify
import six

# Corporate Clash's public Discord application ID. Replace this with an
# Altis-owned Discord application ID when one is available.
client_id = '1538380119322664970'

notify = directNotify.newCategory('DiscordRPC')


class DiscordConnector(object):
    """Small Python 2-compatible Discord IPC client."""

    def __init__(self):
        self.platform = self._get_platform()
        self.ipc = self._get_ipc()
        self.pid = os.getpid()
        self.connected = False
        self.socket = None

    def _get_platform(self):
        try:
            return os.name
        except:
            return 'nt' if '\\' in os.environ.get('COMSPEC', '') else 'posix'

    def _get_ipc(self):
        if self.platform == 'nt':
            return r'\\?\pipe\discord-ipc-0'

        path = (os.environ.get('XDG_RUNTIME_DIR') or
                os.environ.get('TMPDIR') or
                os.environ.get('TMP') or
                os.environ.get('TEMP'))
        if not path:
            try:
                proc = subprocess.Popen(
                    ['getconf', 'DARWIN_USER_TEMP_DIR'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
                path = proc.communicate()[0].strip()
            except:
                path = None
        return re.sub(r'/$', '', path or '/tmp') + '/discord-ipc-0'

    def _read_response(self):
        """Read one Discord IPC response without Python 3-only APIs."""
        if self.platform == 'nt':
            header = ''
            while len(header) < 8:
                chunk = self.socket.read(8 - len(header))
                if not chunk:
                    break
                header += chunk
        else:
            header = self.socket.recv(8)

        if len(header) < 8:
            raise IOError('Incomplete Discord IPC header')

        opcode, length = struct.unpack('<ii', header[:8])
        data = ''
        while len(data) < length:
            if self.platform == 'nt':
                chunk = self.socket.read(length - len(data))
            else:
                chunk = self.socket.recv(length - len(data))
            if not chunk:
                break
            data += chunk

        if len(data) != length:
            raise IOError('Incomplete Discord IPC payload')

        try:
            return json.loads(data.decode('utf-8'))
        except AttributeError:
            return json.loads(data)

    def _send(self, opcode, payload):
        data = json.dumps(payload, separators=(',', ':')).encode('utf-8')
        packet = struct.pack('<ii', opcode, len(data)) + data

        if self.platform == 'nt':
            self.socket.write(packet)
            try:
                self.socket.flush()
            except:
                pass
        else:
            self.socket.sendall(packet)

        try:
            return self._read_response()
        except Exception as exc:
            notify.warning('Discord RPC response could not be read: %s' % exc)
            return None

    def connect(self):
        if self.connected:
            return True

        try:
            if self.platform == 'nt':
                self.socket = io_open(self.ipc, 'w+b')
            else:
                self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self.socket.connect(self.ipc)

            response = self._send(0, {'v': 1, 'client_id': client_id})
            if response and response.get('evt') == 'ERROR':
                raise IOError('Discord handshake rejected: %s' % response.get('data'))
            self.connected = True
            notify.info('Connected to Discord Rich Presence.')
            return True
        except Exception as exc:
            notify.warning('Failed to start Discord Rich Presence: %s' % exc)
            self.socket = None
            self.connected = False
            return False

    def disconnect(self):
        if not self.connected:
            return
        try:
            if self.platform != 'nt':
                self.socket.shutdown(socket.SHUT_RDWR)
        except:
            pass
        try:
            self.socket.close()
        except:
            pass
        self.socket = None
        self.connected = False
        notify.info('Disconnected from Discord Rich Presence.')

    def update_activity(self, activity):
        if not self.connected:
            return
        payload = {
            'cmd': 'SET_ACTIVITY',
            'args': {
                'activity': activity,
                'pid': self.pid
            },
            'nonce': str(uuid.uuid4())
        }
        try:
            self._send(1, payload)
        except Exception as exc:
            notify.warning('Failed to update Discord Rich Presence: %s' % exc)


class Activity(object):
    def __init__(self):
        self.launchTimestamp = time.mktime(datetime.now().timetuple())
        self.large_img = None
        self.large_img_hover = None
        self.district = None
        self.state = None
        self.toonName = None
        self.currentHp = None
        self.maxHp = None
        self.partySize = None
        self.maxPartySize = None
        self.displayParty = False

    def clearRP(self):
        self.large_img = None
        self.large_img_hover = None
        self.district = None
        self.state = None
        self.toonName = None
        self.currentHp = None
        self.maxHp = None
        self.partySize = None
        self.maxPartySize = None
        self.displayParty = False

    def setZone(self, zoneId):
        zone = DiscordPresets.zones.get(zoneId)
        if zone is None:
            try:
                zone = DiscordPresets.zones.get(ZoneUtil.getBranchZone(zoneId))
            except:
                zone = None
        if zone and zone.get('zoneName') != self.state:
            self.state = zone.get('zoneName')
            self.large_img = zone.get('zoneImage')
            self.large_img_hover = zone.get('zoneImageHover')
            self.displayParty = False
            self.maxPartySize = None
            return True
        return False

    def applyPreset(self, preset, imageIndex=0, fillin=None, hover_fillin=None):
        info = DiscordPresets.presets.get(preset)
        if not info:
            notify.warning('Unknown Discord RPC preset: %s' % preset)
            return

        self.state = info.get('state')
        if 'large_image_key' in info:
            self.large_img = info['large_image_key']

        if isinstance(self.state, list):
            self.state = self.state[min(imageIndex, len(self.state) - 1)]
        if fillin is not None and isinstance(self.state, six.string_types) and '%s' in self.state:
            try:
                self.state = self.state % fillin
            except TypeError:
                pass

        if isinstance(self.large_img, list):
            self.large_img = self.large_img[min(imageIndex, len(self.large_img) - 1)]

        self.large_img_hover = info.get('large_image_hover')
        if self.large_img_hover is not None and hover_fillin is not None and '%s' in self.large_img_hover:
            try:
                self.large_img_hover = self.large_img_hover % hover_fillin
            except TypeError:
                pass

        self.displayParty = 'party' in info
        self.maxPartySize = info.get('max_party_size')

    def send(self):
        output = {'assets': {}, 'timestamps': {}}
        details = ''

        if self.toonName:
            details += self.toonName
        if self.currentHp is not None and self.maxHp is not None:
            details += ' (%s/%s)' % (self.currentHp, self.maxHp)
        if details:
            output['details'] = details
        if self.district:
            output['assets']['large_text'] = self.district
        if self.state:
            output['state'] = self.state
        if self.large_img:
            output['assets']['large_image'] = self.large_img
        if self.large_img_hover:
            output['assets']['large_text'] = self.large_img_hover
        if self.launchTimestamp:
            output['timestamps']['start'] = self.launchTimestamp

        if self.displayParty and self.partySize:
            party = list(self.partySize)
            if self.maxPartySize and party[1] > self.maxPartySize:
                party[1] = self.maxPartySize
            output['party'] = {'size': party}

        return output
