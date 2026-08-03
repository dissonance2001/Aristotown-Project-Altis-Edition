import re


COMMANDS = (
    {'name': 'help', 'usage': '[command]', 'description': 'Shows information about a Magic Word command.', 'aliases': (), 'access': 300},
    {'name': 'words', 'usage': '', 'description': 'Lists the Magic Word commands available to you.', 'aliases': (), 'access': 300},
    {'name': 'mp', 'usage': '', 'description': 'Teleports you to the Major Player lobby.', 'aliases': (), 'access': 400},
    {'name': 'pace', 'usage': '', 'description': 'Teleports you to the Pacesetter lobby.', 'aliases': (), 'access': 400},
    {'name': 'acc', 'usage': '', 'description': 'Opens or closes the accessory placement editor.', 'aliases': (), 'access': 400},
    {'name': 'jbs', 'usage': '<amount>', 'description': 'Gives Jellybeans to the target Toon.', 'aliases': (), 'access': 400},
    {'name': 'coin', 'usage': '<amount>', 'description': "Gives Club Coins to the target Toon's Club.", 'aliases': (), 'access': 400},
    {'name': 'clublevel', 'usage': '<level>', 'description': "Sets the target Toon's Club level.", 'aliases': (), 'access': 400},
    {'name': 'pos', 'dispatch': 'xyz', 'usage': '<x> <y> <z>', 'description': 'Sets your Toon position.', 'aliases': (), 'access': 300},
    {'name': 'wireframe', 'dispatch': 'wire', 'usage': '', 'description': 'Toggles wireframe rendering.', 'aliases': (), 'access': 300},
    {'name': 'freecam', 'dispatch': 'oobe', 'usage': '', 'description': 'Toggles the out-of-body camera.', 'aliases': (), 'access': 300},
    {'name': 'placements', 'dispatch': 'acc', 'usage': '', 'description': 'Opens or closes the accessory placement editor.', 'aliases': (), 'access': 400},
    {'name': 'spawn', 'dispatch': 'spawncog', 'usage': '<cog> [level] [revives] [skelecog] [waiter]', 'description': 'Spawns a Cog in the current street.', 'aliases': (), 'access': 400},
    {'name': 'skip', 'dispatch': 'skipmovie', 'usage': '', 'description': 'Skips the current battle movie.', 'aliases': (), 'access': 400},
    {'name': 'pies', 'dispatch': 'givepies', 'usage': '<pieType> [amount]', 'description': 'Gives the target Toon pies.', 'aliases': (), 'access': 450},
    {'name': 'coins', 'dispatch': 'coin', 'usage': '<amount>', 'description': "Gives Club Coins to the target Toon's Club.", 'aliases': (), 'access': 400},
    {'name': 'background', 'dispatch': 'backgroundcolor', 'usage': '[r] [g] [b] [a]', 'description': 'Changes the client background color.', 'aliases': (), 'access': 300},
    {'name': 'paths', 'dispatch': 'suitpaths', 'usage': '', 'description': 'Toggles visible Cog paths.', 'aliases': (), 'access': 300},
    {'name': 'bamfile', 'dispatch': 'tobamfile', 'usage': '[filename]', 'description': 'Exports the current scene to a BAM file.', 'aliases': (), 'access': 400},
    {'name': 'exportbam', 'dispatch': 'tobamfile', 'usage': '[filename]', 'description': 'Exports the current scene to a BAM file.', 'aliases': (), 'access': 400},
    {'name': 'model', 'dispatch': 'loadmodel', 'usage': '<modelPath>', 'description': 'Loads a model at your Toon position.', 'aliases': (), 'access': 400},
    {'name': 'backface', 'dispatch': 'backfaceculling', 'usage': '', 'description': 'Toggles backface culling.', 'aliases': (), 'access': 400},
    {'name': 'bfc', 'dispatch': 'backfaceculling', 'usage': '', 'description': 'Toggles backface culling.', 'aliases': (), 'access': 400},
    {'name': 'frontface', 'dispatch': 'frontfaceculling', 'usage': '', 'description': 'Toggles frontface culling.', 'aliases': (), 'access': 400},
    {'name': 'ffc', 'dispatch': 'frontfaceculling', 'usage': '', 'description': 'Toggles frontface culling.', 'aliases': (), 'access': 400},
    {'name': 'toggleparticles', 'dispatch': 'particles', 'usage': '', 'description': 'Toggles particle rendering.', 'aliases': (), 'access': 400},
    {'name': 'upsidedown', 'dispatch': 'inverted', 'usage': '', 'description': 'Toggles an upside-down camera view.', 'aliases': (), 'access': 400},
    {'name': '3d', 'dispatch': 'stereo', 'usage': '', 'description': 'Toggles stereoscopic rendering.', 'aliases': (), 'access': 400},
    {'name': 'sus', 'dispatch': 'suspicious', 'usage': '', 'description': 'Writes a test suspicious event to the server log.', 'aliases': (), 'access': 400},
    {'name': 'msg', 'dispatch': 'whisper', 'usage': '<message>', 'description': 'Whispers to a nearby Toon.', 'aliases': (), 'access': 300},
    {'name': 'dm', 'dispatch': 'whisper', 'usage': '<message>', 'description': 'Whispers to a nearby Toon.', 'aliases': (), 'access': 300},
    {'name': 'tell', 'dispatch': 'whisper', 'usage': '<message>', 'description': 'Whispers to a nearby Toon.', 'aliases': (), 'access': 300},
    {'name': 'logout', 'usage': '', 'description': 'Takes you back to the Pick-A-Toon screen.', 'aliases': (), 'access': 300},
    {'name': 'tp', 'usage': '<zoneId>', 'description': 'Teleports you to an Altis zone or playground ID.', 'aliases': (), 'access': 300},
    {'name': 'district', 'usage': '<districtId>', 'description': 'Switches to the selected district ID.', 'aliases': (), 'access': 300},
    {'name': 'friend', 'usage': '', 'description': 'Sends a friend request to a nearby Toon.', 'aliases': (), 'access': 300},
    {'name': 'ftp', 'usage': '', 'description': 'Teleports to a nearby Toon through the friend teleport flow.', 'aliases': (), 'access': 300},
    {'name': 'whisper', 'usage': '<message>', 'description': 'Whispers to a nearby Toon.', 'aliases': (), 'access': 300},
    {'name': 'reply', 'dispatch': 'reply', 'usage': '<message>', 'description': 'Replies to the last received whisper.', 'aliases': ('r',), 'access': 300},
    {'name': 'emote', 'usage': '<emoteId>', 'description': 'Uses a SpeedChat emote.', 'aliases': (), 'access': 300},
    {'name': 'music', 'usage': '<0-100>', 'description': 'Sets music volume.', 'aliases': (), 'access': 300},
    {'name': 'sfx', 'usage': '<0-100>', 'description': 'Sets sound-effect volume.', 'aliases': (), 'access': 300},
    {'name': 'volume', 'usage': '<0-100>', 'description': 'Sets music and sound-effect volume.', 'aliases': (), 'access': 300},
    {'name': 'currentvolume', 'usage': '', 'description': 'Shows current music and sound-effect volumes.', 'aliases': (), 'access': 300},
    {'name': 'toggle', 'usage': '', 'description': 'Toggles your Toon collisions.', 'aliases': (), 'access': 300},
    {'name': 'surrounding', 'usage': '', 'description': 'Toggles collision traverser bounds.', 'aliases': (), 'access': 400},
    {'name': 'render', 'usage': '', 'description': 'Toggles rendered CollisionNode geometry.', 'aliases': (), 'access': 400},
    {'name': 'pstats', 'usage': '', 'description': 'Connects the client to Panda3D PStats.', 'aliases': (), 'access': 400},
    {'name': 'texture', 'usage': '', 'description': 'Toggles texture rendering.', 'aliases': (), 'access': 400},
    {'name': 'vertexcolors', 'usage': '', 'description': 'Toggles vertex-color rendering.', 'aliases': (), 'access': 400},
    {'name': 'vertexdensity', 'usage': '', 'description': 'Toggles vertex-density visualization.', 'aliases': (), 'access': 400},
    {'name': 'bounds', 'usage': '[tight]', 'description': 'Toggles model bounds.', 'aliases': (), 'access': 400},
    {'name': 'inverted', 'usage': '', 'description': 'Toggles an upside-down camera view.', 'aliases': (), 'access': 400},
    {'name': 'stereo', 'usage': '', 'description': 'Toggles Altis stereoscopic rendering.', 'aliases': (), 'access': 400},
    {'name': 'reloadtextures', 'usage': '', 'description': 'Releases prepared graphics objects so textures reload.', 'aliases': (), 'access': 400},
    {'name': 'backfaceculling', 'usage': '', 'description': 'Toggles backface culling.', 'aliases': (), 'access': 400},
    {'name': 'frontfaceculling', 'usage': '', 'description': 'Toggles frontface culling.', 'aliases': (), 'access': 400},
    {'name': 'fog', 'usage': '', 'description': 'Toggles fog rendering.', 'aliases': (), 'access': 400},
    {'name': 'particles', 'usage': '', 'description': 'Toggles particle rendering.', 'aliases': (), 'access': 400},
    {'name': 'ls', 'usage': '[includeRender2d]', 'description': 'Prints the scene graph tree to the client log.', 'aliases': (), 'access': 400},
    {'name': 'analyze', 'usage': '[includeRender2d]', 'description': 'Prints scene graph analysis to the client log.', 'aliases': (), 'access': 400},
    {'name': 'tobamfile', 'usage': '[filename]', 'description': 'Exports the current scene to a BAM file.', 'aliases': (), 'access': 400},
    {'name': 'loadmodel', 'usage': '<modelPath>', 'description': 'Loads a model at your Toon position.', 'aliases': (), 'access': 400},
    {'name': 'spam', 'usage': '', 'description': 'Enables verbose DirectNotify output.', 'aliases': ('verbose',), 'access': 400},
    {'name': 'invasion', 'usage': '<cog> [mega] [v2] [skelecog] [waiter]', 'description': 'Starts an invasion by Cog name or code.', 'aliases': (), 'access': 400},
    {'name': 'deptinvasion', 'usage': '<department> [mega]', 'description': 'Starts a department-wide Cog invasion.', 'aliases': (), 'access': 400},
    {'name': 'endinvasion', 'usage': '', 'description': 'Ends the current Cog invasion.', 'aliases': (), 'access': 400},
    {'name': 'building', 'usage': '<cog>', 'description': 'Spawns a Cog building nearby.', 'aliases': (), 'access': 375},
    {'name': 'cleardisguise', 'usage': '<department>', 'description': "Clears the target Toon's Cog disguise for one department.", 'aliases': (), 'access': 400},
    {'name': 'dance', 'usage': '', 'description': 'Makes every Toon in your current zone dance.', 'aliases': (), 'access': 400},
    {'name': 'suspicious', 'usage': '', 'description': 'Writes a test suspicious event to the server log.', 'aliases': (), 'access': 400},
    {'name': 'fillgallery', 'usage': '', 'description': "Fills the target Toon's Cog gallery and radar.", 'aliases': (), 'access': 400},
    {'name': 'cleargallery', 'usage': '', 'description': "Clears the target Toon's Cog gallery and radar.", 'aliases': (), 'access': 400},
    {'name': 'head', 'usage': '<speciesOrCode>', 'description': "Changes the target Toon's species or head code.", 'aliases': (), 'access': 390},
    {'name': 'headsize', 'usage': '<index>', 'description': "Changes the target Toon's head-size index.", 'aliases': (), 'access': 390},
    {'name': 'headcolor', 'usage': '<r> <g> <b>', 'description': "Changes the target Toon's head color.", 'aliases': (), 'access': 390},
    {'name': 'torso', 'usage': '<index>', 'description': "Changes the target Toon's torso index.", 'aliases': (), 'access': 390},
    {'name': 'armcolor', 'usage': '<r> <g> <b>', 'description': "Changes the target Toon's arm color.", 'aliases': (), 'access': 390},
    {'name': 'legs', 'usage': '<index>', 'description': "Changes the target Toon's leg-size index.", 'aliases': (), 'access': 390},
    {'name': 'legcolor', 'usage': '<r> <g> <b>', 'description': "Changes the target Toon's leg color.", 'aliases': (), 'access': 390},
)


NO_TARGET_COMMANDS = set((
    'logout', 'tp', 'district', 'reply', 'r', 'emote',
    'music', 'sfx', 'volume', 'currentvolume', 'toggle', 'surrounding',
    'render', 'pstats', 'texture', 'vertexcolors', 'vertexdensity',
    'bounds', 'inverted', 'stereo', 'reloadtextures', 'backfaceculling',
    'frontfaceculling', 'fog', 'particles', 'ls', 'analyze', 'tobamfile',
    'loadmodel', 'spam', 'wireframe', 'freecam', 'placements', 'acc',
    'background', 'paths', 'bamfile', 'exportbam', 'model', 'backface',
    'bfc', 'frontface', 'ffc', 'toggleparticles', 'upsidedown', '3d',
    'pos'
))

REQUIRED_TARGET_COMMANDS = set((
    'friend', 'ftp', 'whisper', 'msg', 'dm', 'tell'
))

TRANSLATIONS = {}
for _entry in COMMANDS:
    _destination = _entry.get('dispatch') or _entry['name']
    if _entry.get('dispatch'):
        TRANSLATIONS[_entry['name'].lower()] = _destination.lower()
    for _alias in _entry.get('aliases', ()) or ():
        TRANSLATIONS[_alias.lower()] = _destination.lower()


def translateCommandText(commandText):
    pieces = commandText.split(None, 1)
    if not pieces:
        return commandText
    command = pieces[0]
    translated = TRANSLATIONS.get(command.lower(), command)
    if len(pieces) == 1:
        return translated
    return translated + ' ' + pieces[1]


def _cleanText(value):
    if not value:
        return ''
    try:
        value = value.strip()
    except:
        value = str(value).strip()
    return re.sub(r'\s+', ' ', value)


def _getFunctionUsage(word):
    func = getattr(word, 'func', None)
    code = getattr(func, 'func_code', None) or getattr(func, '__code__', None)
    defaults = getattr(func, 'func_defaults', None)
    if defaults is None:
        defaults = getattr(func, '__defaults__', None)
    if code is not None:
        try:
            maximum = code.co_argcount
            minimum = maximum - (len(defaults) if defaults else 0)
            names = code.co_varnames[:maximum]
            output = []
            for index, name in enumerate(names):
                output.append('<%s>' % name if index < minimum else '[%s]' % name)
            return ' '.join(output)
        except:
            pass
    try:
        usage = word.getUsage()
        if usage is not None:
            return _cleanText(usage)
    except:
        pass
    return ''


def _normaliseEntry(entry):
    name = _cleanText(entry.get('name', '')).lower()
    aliases = []
    for alias in entry.get('aliases', ()) or ():
        alias = _cleanText(alias).lower()
        if alias and alias != name and alias not in aliases:
            aliases.append(alias)
    description = _cleanText(entry.get('description', ''))
    usage = _cleanText(entry.get('usage', ''))
    try:
        access = int(entry.get('access', 0))
    except:
        access = 0
    targetMode = entry.get('targetMode')
    if not targetMode:
        dispatch = _cleanText(entry.get('dispatch', '')).lower()
        resolvedName = dispatch or name
        if resolvedName in REQUIRED_TARGET_COMMANDS or name in REQUIRED_TARGET_COMMANDS:
            targetMode = 'required'
        elif resolvedName in NO_TARGET_COMMANDS or name in NO_TARGET_COMMANDS:
            targetMode = 'none'
        else:
            targetMode = 'optional'
    return {
        'name': name,
        'usage': usage,
        'description': description,
        'aliases': tuple(aliases),
        'access': access,
        'targetMode': targetMode,
        'searchTerms': tuple([name] + aliases),
    }


def _discoverSpellbookCommands():
    commands = []
    try:
        from otp.ai.MagicWordGlobal import spellbook
    except:
        return commands
    try:
        iterator = spellbook.words.itervalues()
    except:
        try:
            iterator = spellbook.words.values()
        except:
            return commands
    seenObjects = set()
    for word in iterator:
        if id(word) in seenObjects:
            continue
        seenObjects.add(id(word))
        name = _cleanText(getattr(word, 'name', '')).lower()
        if not name:
            continue
        commands.append({
            'name': name,
            'usage': _getFunctionUsage(word),
            'description': _cleanText(getattr(word, 'doc', '')),
            'aliases': (),
            'access': getattr(word, 'access', 0),
        })
    return commands


def getCommandShortcuts(localAvatar=None):
    try:
        access = localAvatar.getAdminAccess() if localAvatar else 999
    except:
        access = 999
    byName = {}
    for entry in _discoverSpellbookCommands():
        normalised = _normaliseEntry(entry)
        if normalised['name'] and normalised['access'] <= access:
            byName[normalised['name']] = normalised
    for entry in COMMANDS:
        normalised = _normaliseEntry(entry)
        if normalised['name'] and normalised['access'] <= access:
            byName[normalised['name']] = normalised
    output = list(byName.values())
    output.sort(key=lambda item: item['name'])
    return output
