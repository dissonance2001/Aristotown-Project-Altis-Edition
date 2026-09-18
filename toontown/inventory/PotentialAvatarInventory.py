"""
Helpers for carrying a PotentialAvatar's equipped Hammerspace items through
ClientServicesManager's existing DNA field.

The login avatar struct predates Hammerspace and does not contain an equipped
items field.  Packing the extra data behind the fixed-length DNA keeps the
existing DC schema unchanged; the client removes it before constructing
ToonDNA.
"""

import base64
import json

from toontown.inventory.base.InventoryItem import InventoryItem


_MARKER = b'\x00CC-HAMMERSPACE-V1\x00'


def _as_bytes(value):
    if isinstance(value, bytes):
        return value, False
    if isinstance(value, bytearray):
        return bytes(value), False
    if isinstance(value, str):
        return value.encode('latin-1'), True
    return bytes(value), False


def packPotentialAvatarDNA(dna, equippedItems):
    """Append equipped item structs to a DNA net string."""
    dnaBytes, wasText = _as_bytes(dna)
    itemStructs = InventoryItem.toStructList(equippedItems or [])
    payload = json.dumps(itemStructs, separators=(',', ':')).encode('utf-8')
    packed = dnaBytes + _MARKER + base64.b64encode(payload)
    return packed.decode('latin-1') if wasText else packed


def unpackPotentialAvatarDNA(packedDNA):
    """Return ``(cleanDNA, equippedItems)`` from a packed login DNA value."""
    raw, wasText = _as_bytes(packedDNA)
    dnaBytes, marker, payload = raw.rpartition(_MARKER)
    if not marker:
        return packedDNA, []

    try:
        itemStructs = json.loads(base64.b64decode(payload).decode('utf-8'))
        equippedItems = InventoryItem.fromStructList(itemStructs)
    except Exception:
        # Preserve compatibility with old/corrupt avatar-list data.  Treat the
        # entire value as ordinary DNA instead of preventing login.
        return packedDNA, []

    cleanDNA = dnaBytes.decode('latin-1') if wasText else dnaBytes
    return cleanDNA, equippedItems
