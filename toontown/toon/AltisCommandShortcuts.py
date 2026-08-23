import re


COMMANDS = (
    {'name': 'help', 'usage': '[command]', 'description': 'Shows information about a Magic Word command.', 'aliases': (), 'access': 300},
    {'name': 'words', 'usage': '', 'description': 'Lists the Magic Word commands available to you.', 'aliases': (), 'access': 300},
    {'name': 'mp', 'usage': '', 'description': 'Teleports you to the Major Player lobby.', 'aliases': (), 'access': 400},
    {'name': 'pace', 'usage': '', 'description': 'Teleports you to the Pacesetter lobby.', 'aliases': (), 'access': 400},
    {'name': 'cs', 'usage': '', 'description': 'Teleports you to the Chainsaw Consultant lobby.', 'aliases': (), 'access': 400, 'targetMode': 'none'},
    {'name': 'presentthiefstart', 'usage': '', 'description': 'Starts the Present Thief minigame in Toonseltown after the 10-second warning.', 'aliases': (), 'access': 400, 'targetMode': 'none'},
    {'name': 'presentthiefend', 'usage': '', 'description': 'Immediately ends the active Present Thief minigame and cleans it up.', 'aliases': (), 'access': 400, 'targetMode': 'none'},
    {'name': 'pizza', 'usage': '', 'description': 'Teleports you directly to the Pizzeria.', 'aliases': (), 'access': 400, 'targetMode': 'none'},
    {'name': 'printpos', 'usage': '', 'description': 'Prints your Toon position and rotation.', 'aliases': ('ppos',), 'access': 400, 'targetMode': 'none'},
    {'name': 'acc', 'usage': '', 'description': 'Opens or closes the accessory placement editor.', 'aliases': (), 'access': 400},
    {'name': 'jbs', 'usage': '<amount>', 'description': 'Gives Jellybeans to the target Toon.', 'aliases': (), 'access': 400},
    {'name': 'coin', 'usage': '<amount>', 'description': "Gives Club Coins to the target Toon's Club.", 'aliases': (), 'access': 400},
    {'name': 'clublevel', 'usage': '<level>', 'description': "Sets the target Toon's Club level.", 'aliases': (), 'access': 400},
    {'name': 'instakill', 'usage': '<damage 0-60000>', 'description': "Sets fixed damage for the target Toon's damaging gags; 0 disables it.", 'aliases': (), 'access': 400},
    {'name': 'instakillreset', 'usage': '', 'description': 'Restores normal gag damage for the target Toon.', 'aliases': ('resetinstakill',), 'access': 400, 'targetMode': 'optional'},
    {'name': 'unlimitedgags', 'usage': '', 'description': "Toggles automatic gag restocking at the start of each battle round.", 'aliases': (), 'access': 390, 'targetMode': 'optional'},
    {'name': 'maxtoon', 'usage': '[missingTrack]', 'description': "Maxes your Toon's stats for end-level gameplay.", 'aliases': (), 'access': 375, 'targetMode': 'none'},
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
    {'name': 'a2d', 'usage': '', 'description': 'Toggle aspect2d.', 'aliases': (), 'access': 300},
    {'name': 'accesslevel', 'usage': '<accessLevel> [storage] [showGM]', 'description': "Modify the target's access level.", 'aliases': (), 'access': 450},
    {'name': 'achievements', 'usage': '<command> <achId>', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 400},
    {'name': 'addholiday', 'usage': '<holidayId>', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 400},
    {'name': 'addtpaccess', 'usage': '<zone>', 'description': 'Adds teleport access to target', 'aliases': (), 'access': 400},
    {'name': 'allgardenspecials', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 400},
    {'name': 'allsummons', 'usage': '', 'description': "Max the invoker's summons", 'aliases': (), 'access': 375},
    {'name': 'backgroundcolor', 'usage': '[r] [g] [b] [a]', 'description': 'Set the background color. Specify no arguments for the default background color.', 'aliases': (), 'access': 300},
    {'name': 'backpack', 'usage': '<backpackIndex> [backpackTex]', 'description': "Modify the invoker's backpack.", 'aliases': (), 'access': 390},
    {'name': 'badname', 'usage': '', 'description': "Revoke the target's name.", 'aliases': (), 'access': 375},
    {'name': 'ban', 'usage': '<reason>', 'description': 'Ban and Kick the target from the game server.', 'aliases': (), 'access': 375},
    {'name': 'banid', 'usage': '<id> <reason>', 'description': 'Ban and Kick the short id from the game server.', 'aliases': (), 'access': 375},
    {'name': 'bank', 'usage': '<command> <value>', 'description': "Modifies the target's bank money values.", 'aliases': (), 'access': 400},
    {'name': 'boardbothq', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 390},
    {'name': 'catalog', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 300},
    {'name': 'cfo2', 'usage': '', 'description': 'Skips to the next round of the CFO.', 'aliases': (), 'access': 400},
    {'name': 'cfocutscene1', 'usage': '', 'description': 'Skips to the next round of the CFO.', 'aliases': (), 'access': 400},
    {'name': 'chatmode', 'usage': '[mode]', 'description': 'Set the chat mode of the current avatar.', 'aliases': (), 'access': 375},
    {'name': 'cheesyeffect', 'usage': '<value> [hood] [expire]', 'description': "Modify the target's cheesy effect.", 'aliases': (), 'access': 400},
    {'name': 'clearsos', 'usage': '', 'description': "Clear's the invoker's SOS card inventory", 'aliases': (), 'access': 400},
    {'name': 'cogindex', 'usage': '<index>', 'description': "Modifies the invoker's Cog index.", 'aliases': (), 'access': 450},
    {'name': 'collisionsoff', 'usage': '', 'description': 'Turns collisions off.', 'aliases': (), 'access': 300},
    {'name': 'collisionson', 'usage': '', 'description': 'Turns collisions on.', 'aliases': (), 'access': 300},
    {'name': 'color', 'usage': '<part> <r> <g> <b>', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 390},
    {'name': 'disablegc', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 400},
    {'name': 'disguise', 'usage': '<command> <suitIndex> <value>', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 400},
    {'name': 'dna', 'usage': '<part> <value>', 'description': 'Modify a DNA part on the invoker.', 'aliases': (), 'access': 390},
    {'name': 'dump_doid2do', 'usage': '', 'description': 'Please note that this MW should NOT be used more than it needs to be on a live cluster. This is very hacked together and is purely so we can get a dump of doId2do to get an idea...', 'aliases': (), 'access': 400},
    {'name': 'emptyhouse', 'usage': '', 'description': 'delete everything in the house', 'aliases': (), 'access': 400},
    {'name': 'enablegc', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 400},
    {'name': 'endflying', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 400},
    {'name': 'endmaze', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 400},
    {'name': 'explorer', 'usage': '', 'description': 'Toggle the scene graph explorer.', 'aliases': (), 'access': 300},
    {'name': 'factorywarp', 'usage': '<zoneNum>', 'description': 'Warp to a specific factory zone.', 'aliases': (), 'access': 400},
    {'name': 'fillattic', 'usage': '', 'description': 'move everything to the attic', 'aliases': (), 'access': 400},
    {'name': 'findcloset', 'usage': '', 'description': 'find the closet', 'aliases': (), 'access': 400},
    {'name': 'fires', 'usage': '<count>', 'description': "Modifies the invoker's pink slip count.", 'aliases': (), 'access': 400},
    {'name': 'fireworks', 'usage': '[showName]', 'description': 'Starts a fireworks show on the AI server.', 'aliases': (), 'access': 500},
    {'name': 'fish', 'usage': '<fishName>', 'description': 'Register/unregister the fish to be caught on the invoker.', 'aliases': (), 'access': 450},
    {'name': 'fishingrod', 'usage': '<rod>', 'description': "Modify the target's fishing rod value.", 'aliases': (), 'access': 400},
    {'name': 'gardenflowerall', 'usage': '[species] [variety]', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 400},
    {'name': 'gardengrowflowers', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 400},
    {'name': 'gardenpickall', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 400},
    {'name': 'gencertificate', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 400},
    {'name': 'generatenpcs', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 400},
    {'name': 'getzone', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 400},
    {'name': 'ghost', 'usage': '', 'description': 'Toggles invisibility on the invoker. Anyone with an access level below the invoker will not be able to see him or her.', 'aliases': (), 'access': 300},
    {'name': 'givepies', 'usage': '<pieType> [numPies]', 'description': 'Give the target (numPies) of (pieType) pies.', 'aliases': (), 'access': 450},
    {'name': 'glasses', 'usage': '<glassesIndex> [glassesTex]', 'description': "Modify the invoker's glasses.", 'aliases': (), 'access': 390},
    {'name': 'globalteleport', 'usage': '', 'description': 'Activates the global teleport cheat for the invoker.', 'aliases': (), 'access': 300},
    {'name': 'globaltp', 'usage': '<streetZone>', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 390},
    {'name': 'gmicon', 'usage': '[accessLevel]', 'description': "Toggles the target's GM icon. If an access level is provided, however, the target's GM icon will be overridden.", 'aliases': (), 'access': 275},
    {'name': 'goto', 'usage': '<avIdShort>', 'description': 'Teleport to the avId specified.', 'aliases': (), 'access': 375},
    {'name': 'gravity', 'usage': '<value>', 'description': "Modifies the invoker's gravity. For default, use 0.", 'aliases': (), 'access': 450},
    {'name': 'growtree', 'usage': '<track> <index> [grown]', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 400},
    {'name': 'hat', 'usage': '<hatIndex> [hatTex]', 'description': "Modify the invoker's hat.", 'aliases': (), 'access': 390},
    {'name': 'hp', 'usage': '<hp>', 'description': "Modify the invoker's current HP.", 'aliases': (), 'access': 400},
    {'name': 'hpr', 'usage': '<h> <p> <r>', 'description': 'Modifies the rotation of the invoker.', 'aliases': (), 'access': 300},
    {'name': 'i60pan', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 390},
    {'name': 'i60panstop', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 390},
    {'name': 'i60reset', 'usage': '', 'description': "Reset the target's stats for insomnia gamplay", 'aliases': (), 'access': 500},
    {'name': 'i60skip', 'usage': '', 'description': "Set the target's stats for insomnia gamplay", 'aliases': (), 'access': 500},
    {'name': 'idnametags', 'usage': '', 'description': 'Display avatar IDs inside nametags.', 'aliases': (), 'access': 300},
    {'name': 'immortal', 'usage': '', 'description': 'Make target (if 400+) or self (if 399-) immortal.', 'aliases': (), 'access': 390},
    {'name': 'inventory', 'usage': '<a> [b] [c]', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 400},
    {'name': 'kick', 'usage': '[reason]', 'description': 'Kick the target from the game server.', 'aliases': (), 'access': 375},
    {'name': 'kickid', 'usage': '<id> [reason]', 'description': 'Kick the target from the game server.', 'aliases': (), 'access': 375},
    {'name': 'killceo', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 450},
    {'name': 'killcfo', 'usage': '', 'description': 'Kills the CFO.', 'aliases': (), 'access': 400},
    {'name': 'killchairman', 'usage': '', 'description': 'Kills the Chairman.', 'aliases': (), 'access': 400},
    {'name': 'killcj', 'usage': '', 'description': 'Kills the CJ.', 'aliases': (), 'access': 450},
    {'name': 'killcount', 'usage': '', 'description': 'Kills the CJ.', 'aliases': (), 'access': 450},
    {'name': 'killdirectors', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 450},
    {'name': 'killvp', 'usage': '', 'description': 'Kills the VP.', 'aliases': (), 'access': 400},
    {'name': 'killvpsecond', 'usage': '', 'description': 'Kills the VP.', 'aliases': (), 'access': 400},
    {'name': 'lefthand', 'usage': '[prop]', 'description': "Parents the optional <prop> to the target's left hand node.", 'aliases': (), 'access': 300},
    {'name': 'loop', 'usage': '<anim>', 'description': 'Animate the target using animation [anim] on the entire actor.', 'aliases': (), 'access': 300},
    {'name': 'manualsos', 'usage': '<count> <npcId>', 'description': "Modifies the invoker's specified SOS card count.", 'aliases': (), 'access': 400},
    {'name': 'maxfishtank', 'usage': '<maxFishTank>', 'description': "Modify the target's max fish tank value.", 'aliases': (), 'access': 400},
    {'name': 'maxhp', 'usage': '<maxHp>', 'description': "Modify the invoker's max HP.", 'aliases': (), 'access': 400},
    {'name': 'minigame', 'usage': '<command> [arg0]', 'description': 'A command set for Trolley minigames.', 'aliases': (), 'access': 400},
    {'name': 'money', 'usage': '<money>', 'description': "Modifies the target's current money value.", 'aliases': (), 'access': 400},
    {'name': 'name', 'usage': '[name]', 'description': "Modify the target's name.", 'aliases': (), 'access': 375},
    {'name': 'namenametags', 'usage': '', 'description': 'Display only avatar names inside nametags.', 'aliases': (), 'access': 300},
    {'name': 'nametagstyle', 'usage': '<nametagStyle>', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 375},
    {'name': 'neglect', 'usage': '', 'description': "Toggle the neglection of network updates on the invoker's client.", 'aliases': (), 'access': 300},
    {'name': 'oobe', 'usage': '', 'description': "Toggle the 'out of body experience' view.", 'aliases': (), 'access': 300},
    {'name': 'oobecull', 'usage': '', 'description': "Toggle the 'out of body experience' view with culling debugging.", 'aliases': (), 'access': 400},
    {'name': 'pettest', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 400},
    {'name': 'pingpong', 'usage': '<anim> [start] [end] [part]', 'description': 'Animate the target by bouncing back and forth between the start and end, or the optional frames <start>, and [end] of animation [anim] on the entire actor, or optional <part> of...', 'aliases': (), 'access': 300},
    {'name': 'placer', 'usage': '', 'description': 'Toggle the camera placer.', 'aliases': (), 'access': 300},
    {'name': 'pose', 'usage': '<anim> <frame> [part]', 'description': 'Freeze the target on frame [frame] of animation [anim] on the entire actor, or optional [part] of the actor.', 'aliases': (), 'access': 300},
    {'name': 'pouch', 'usage': '<amt>', 'description': "Set the target's max gag limit.", 'aliases': (), 'access': 375},
    {'name': 'printdna', 'usage': '', 'description': 'Print the targets DNA in a pretty fashion.', 'aliases': (), 'access': 400},
    {'name': 'promote', 'usage': '<dept> [revive]', 'description': 'Promotes the invoker by 1 level, if flag is defined, it promotes the v2.0 suit by one level.', 'aliases': (), 'access': 400},
    {'name': 'quests', 'usage': '<command> [arg0] [arg1]', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 400},
    {'name': 'race', 'usage': '<command>', 'description': 'A command set for races.', 'aliases': (), 'access': 400},
    {'name': 'recovercloset', 'usage': '', 'description': 'recover the closet', 'aliases': (), 'access': 400},
    {'name': 'removeholiday', 'usage': '<holidayId>', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 400},
    {'name': 'restart', 'usage': '<minutes>', 'description': 'Initiate the maintenance message sequence. It will last for the specified amount of <minutes>.', 'aliases': (), 'access': 500},
    {'name': 'restartcraneround', 'usage': '', 'description': 'Restarts the crane round in the CFO.', 'aliases': (), 'access': 450},
    {'name': 'revealmap', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 400},
    {'name': 'righthand', 'usage': '[prop]', 'description': "Parents the optional <prop> to the target's right hand node.", 'aliases': (), 'access': 300},
    {'name': 'run', 'usage': '', 'description': 'Toggles debugging run speed.', 'aliases': (), 'access': 300},
    {'name': 'setmailboxmgronline', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 400},
    {'name': 'setmaxmoney', 'usage': '<moneyVal>', 'description': "Set target's money and maxMoney values.", 'aliases': (), 'access': 400},
    {'name': 'setsillymeterphase', 'usage': '<phase>', 'description': 'Sets the Silly Meters Phase!', 'aliases': (), 'access': 400},
    {'name': 'shoes', 'usage': '<shoesIndex> [shoesTex]', 'description': "Modify the invoker's shoes.", 'aliases': (), 'access': 390},
    {'name': 'shovelskill', 'usage': '<skill>', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 400},
    {'name': 'skipbdlitcutscene', 'usage': '', 'description': 'Skips to the final round of the VP.', 'aliases': (), 'access': 400},
    {'name': 'skipceo', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 450},
    {'name': 'skipceofinal', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 450},
    {'name': 'skipceofirst', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 450},
    {'name': 'skipcfo', 'usage': '', 'description': 'Skips to the final round of the CFO.', 'aliases': (), 'access': 450},
    {'name': 'skipchairman', 'usage': '', 'description': 'Skips to the final round of the Chairman.', 'aliases': (), 'access': 400},
    {'name': 'skipchairman2', 'usage': '', 'description': 'Skips to the final round of the VP.', 'aliases': (), 'access': 400},
    {'name': 'skipcj', 'usage': '', 'description': 'Skips to the final round of the CJ.', 'aliases': (), 'access': 450},
    {'name': 'skipcj2', 'usage': '', 'description': 'Skips to the final round of the CJ.', 'aliases': (), 'access': 450},
    {'name': 'skipcjfinal', 'usage': '', 'description': 'Kills the CJ.', 'aliases': (), 'access': 450},
    {'name': 'skipcount', 'usage': '', 'description': 'Skips to the final round of the CJ.', 'aliases': (), 'access': 450},
    {'name': 'skipcount2', 'usage': '', 'description': 'Skips to the final round of the CJ.', 'aliases': (), 'access': 450},
    {'name': 'skipcountfinal', 'usage': '', 'description': 'Kills the CJ.', 'aliases': (), 'access': 450},
    {'name': 'skipdirectors', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 450},
    {'name': 'skipdirectorscutscene', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 450},
    {'name': 'skipdirectorsfinal', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 450},
    {'name': 'skipdirectorsfirst', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 450},
    {'name': 'skipexecutscene', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 450},
    {'name': 'skiplitcutscene', 'usage': '', 'description': 'Kills the CJ.', 'aliases': (), 'access': 450},
    {'name': 'skipmovie', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 400},
    {'name': 'skipsblitcutscene', 'usage': '', 'description': 'Skips to the final round of the VP.', 'aliases': (), 'access': 400},
    {'name': 'skipvp', 'usage': '', 'description': 'Skips to the final round of the VP.', 'aliases': (), 'access': 400},
    {'name': 'skipvp2', 'usage': '', 'description': 'Skips to the final round of the VP.', 'aliases': (), 'access': 400},
    {'name': 'skipvpsecond', 'usage': '', 'description': 'Skips to the final round of the VP.', 'aliases': (), 'access': 400},
    {'name': 'skyclan', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 390},
    {'name': 'sleep', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 375},
    {'name': 'slow', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 300},
    {'name': 'soprano', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 390},
    {'name': 'sos', 'usage': '<count> <name>', 'description': "Modifies the invoker's specified SOS card count.", 'aliases': (), 'access': 400},
    {'name': 'spawncog', 'usage': '<name> [level] [revives] [skelecog] [waiter]', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 400},
    {'name': 'speednormal', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 300},
    {'name': 'spooky', 'usage': '', 'description': "Activates the 'spooky' effect on the current area.", 'aliases': (), 'access': 390},
    {'name': 'startholiday', 'usage': '<holidayId>', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 400},
    {'name': 'sues', 'usage': '<count>', 'description': "Modifies the invoker's sue count.", 'aliases': (), 'access': 400},
    {'name': 'suit', 'usage': '<command> [suitName] [isMega] [flags]', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 450},
    {'name': 'suitpaths', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 300},
    {'name': 'summonbuilding', 'usage': '<suitIndex>', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 375},
    {'name': 'summoncogdo', 'usage': '<track> [difficulty]', 'description': 'Spawns a Field Office with the given type and difficulty', 'aliases': (), 'access': 375},
    {'name': 'system', 'usage': '<message>', 'description': 'Broadcast a <message> to the game server.', 'aliases': (), 'access': 500},
    {'name': 'tag', 'usage': '[tag]', 'description': "Modify the target's tag.", 'aliases': (), 'access': 375},
    {'name': 'target', 'usage': '', 'description': 'Returns the current Spellbook target.', 'aliases': (), 'access': 300},
    {'name': 'testdialouge', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 400},
    {'name': 'testsimplemail', 'usage': '<contents>', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 400},
    {'name': 'tickets', 'usage': '<tickets>', 'description': "Set the invoker's racing tickets value.", 'aliases': (), 'access': 400},
    {'name': 'togglebooks', 'usage': '', 'description': "Toggle The CJ's large attack. (Bookselves)", 'aliases': (), 'access': 600},
    {'name': 'toonexp', 'usage': '<exp>', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 400},
    {'name': 'toonlevel', 'usage': '<level>', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 400},
    {'name': 'toonseltown', 'usage': '', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 390},
    {'name': 'track', 'usage': '<command> <track> [value]', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 400},
    {'name': 'trackbonus', 'usage': '[trackIndex] [trackIndex2] [trackIndex3] [trackIndex4] [trackIndex5] [trackIndex6] [trackIndex7] [trackIndex8]', 'description': "Modify the invoker's track bonus level.", 'aliases': (), 'access': 400},
    {'name': 'trainingpoints', 'usage': '<points>', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 400},
    {'name': 'treefruit', 'usage': '<track> <index>', 'description': 'Altis Magic Word command.', 'aliases': (), 'access': 400},
    {'name': 'trophyscore', 'usage': '<value>', 'description': "Modifies the target's trophy score.", 'aliases': (), 'access': 450},
    {'name': 'unites', 'usage': '[value]', 'description': 'Restock all resistance messages.', 'aliases': (), 'access': 400},
    {'name': 'unlocks', 'usage': '', 'description': "Unlocks the invoker's teleport access, emotions, and pet trick phrases.", 'aliases': (), 'access': 400},
    {'name': 'update', 'usage': '<minutes> <reason>', 'description': 'Initiate the update message sequence. It will last for the specified amount of <minutes>.', 'aliases': (), 'access': 500},
    {'name': 'warn', 'usage': '<banWorthy>', 'description': 'Warns the user.', 'aliases': (), 'access': 375},
    {'name': 'warp', 'usage': '', 'description': "Warp the target to the invoker's current position, and rotation.", 'aliases': (), 'access': 300},
    {'name': 'wire', 'usage': '', 'description': "Toggle the 'wireframe' view.", 'aliases': (), 'access': 300},
    {'name': 'xyz', 'usage': '<x> <y> <z>', 'description': 'Modifies the position of the invoker.', 'aliases': (), 'access': 300},
    {'name': 'zone', 'usage': '<zoneId>', 'description': "Changes the invoker's zone ID.", 'aliases': (), 'access': 450},
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
        iterator = iter(spellbook.words.values())
    except:
        try:
            iterator = list(spellbook.words.values())
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
