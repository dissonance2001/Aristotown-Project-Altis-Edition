"""
Debug magic words for granting hammerspace items directly, for testing while
the real purchase paths (catalog shop, closet/trunk, Tailor unlocks) are still
being built. Matches the spirit of Clash's staff-only /hammerspace give
shortcut, but looks items up by (partial, case-insensitive) name instead of
raw itemType/itemId numbers, since that's much easier to use for testing.

Usage in chat:
    ~hammerspace give <search text>
    ~hammerspace give <quantity> <search text>
    ~hammerspace find <search text>
    ~hammerspace giveall

Examples:
    ~hammerspace give racer jumpsuit
    ~hammerspace give 3 racing flag
    ~hammerspace find racing
    ~hammerspace giveall

NOTE: Altis's magic word parser splits on whitespace with the LAST declared
parameter absorbing all remaining text, so the search text must come last --
hence quantity (when given) comes before it.
"""
from otp.ai.MagicWordGlobal import *

from toontown.inventory.base.InventoryItem import InventoryItem
from toontown.inventory.registry.ItemTypeRegistry import ItemTypeRegistry

# How many matches to list back when a search is ambiguous.
MAX_LISTED_MATCHES = 10


def _findItemsByName(searchText: str):
    """
    Returns a list of (itemSubtype, name) tuples matching the human-readable
    item name, Clash-style enum name, or numeric item ID.
    """
    searchText = searchText.lower().strip()
    matches = []
    seen = set()
    for itemType, subtypeDict in ItemTypeRegistry.items():
        for itemSubtype, itemDef in subtypeDict.items():
            try:
                name = itemDef.getName()
            except Exception:
                continue
            enumName = getattr(itemSubtype, 'name', str(itemSubtype))
            enumValue = str(getattr(itemSubtype, 'value', itemSubtype))
            terms = (
                name.lower() if name else '',
                enumName.lower(),
                enumValue.lower(),
            )
            if not any(searchText in term for term in terms if term):
                continue

            key = itemSubtype
            if key in seen:
                continue
            seen.add(key)
            matches.append((itemSubtype, name, enumName, enumValue))

    def sortKey(entry):
        name = (entry[1] or '').lower()
        enumName = entry[2].lower()
        enumValue = entry[3].lower()
        terms = (name, enumName, enumValue)
        if searchText in terms:
            exactRank = 0
        else:
            exactRank = 1
        prefixMatches = [term for term in terms if term.startswith(searchText) and term]
        if prefixMatches:
            prefixRank = 0
            prefixLength = min(len(term) for term in prefixMatches)
        else:
            prefixRank = 1
            prefixLength = 0
        positions = [term.find(searchText) for term in terms if term and searchText in term]
        position = min(positions) if positions else 999999
        return (exactRank, prefixRank, prefixLength, position, name or enumName)

    matches.sort(key=sortKey)
    return [(itemSubtype, name) for itemSubtype, name, _, _ in matches]


@magicWord(category=CATEGORY_ADMINISTRATOR, types=[str, str])
def hammerspace(subcommand, rest=''):
    """
    Hammerspace debug tools.
      ~hammerspace give <search text>             -- grants 1 of the best match
      ~hammerspace give <quantity> <search text>  -- grants N of the best match
      ~hammerspace find <search text>             -- lists matching items
      ~hammerspace giveall                        -- grants one of everything (slow!)
    """
    invoker = spellbook.getInvoker()
    inventory = invoker.getHammerspace()
    if not inventory:
        return "Toon hammerspace is not yet initialized."

    subcommand = subcommand.lower()
    rest = rest.strip()

    if subcommand == 'give':
        if not rest:
            return "Usage: ~hammerspace give [quantity] <search text>"

        # Allow an optional leading quantity: "give 3 racing flag"
        quantity = 1
        parts = rest.split(None, 1)
        if len(parts) == 2 and parts[0].isdigit():
            quantity = max(1, int(parts[0]))
            searchText = parts[1]
        else:
            searchText = rest

        matches = _findItemsByName(searchText)
        if not matches:
            return f"No item found matching '{searchText}'."

        itemSubtype, name = matches[0]
        item = InventoryItem.fromSubtype(itemSubtype, quantity=quantity)
        if inventory.addItem(item, quantity=quantity):
            extra = ''
            if len(matches) > 1:
                extra = f" (+{len(matches) - 1} other matches; use ~hammerspace find to list them)"
            return f"Gave {quantity}x {name}.{extra}"
        return f"Failed to add item: {name}"

    elif subcommand == 'find':
        if not rest:
            return "Usage: ~hammerspace find <search text>"
        matches = _findItemsByName(rest)
        if not matches:
            return f"No item found matching '{rest}'."
        shown = matches[:MAX_LISTED_MATCHES]
        names = ', '.join(name for _, name in shown)
        suffix = f" (+{len(matches) - len(shown)} more)" if len(matches) > len(shown) else ''
        return f"{len(matches)} match(es): {names}{suffix}"

    elif subcommand == 'giveall':
        quantity = max(1, int(rest)) if rest.isdigit() else 1
        given = 0
        savedCallbacks = list(inventory._deltaCallbacks)
        inventory._deltaCallbacks = []
        try:
            for itemType, subtypeDict in ItemTypeRegistry.items():
                for itemSubtype, itemDef in subtypeDict.items():
                    try:
                        item = InventoryItem.fromSubtype(itemSubtype, quantity=quantity)
                        item.getItemDefinition()
                    except Exception:
                        continue
                    if inventory.addItem(item, quantity=quantity):
                        given += 1
        finally:
            inventory._deltaCallbacks = savedCallbacks

        invoker.air.inventoryManager.setAvatarInventory(invoker.doId, inventory)
        return f"Gave {given} different items."

    return ("Usage: ~hammerspace give [quantity] <search text> | "
            "~hammerspace find <search text> | ~hammerspace giveall")
