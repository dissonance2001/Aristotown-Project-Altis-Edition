# Making a New Cutscene From Scratch

A complete walkthrough of the Corporate Clash cutscene system: registering a new
cutscene, choosing its room, spawning its cast, building the timeline in the
editor, and wiring the finished product into real gameplay code.

See also: [SuitShortnames.md](SuitShortnames.md) for every valid `makeSuits(...)` name.

---

## 1. How the system is put together

```
toontown/cutscene/
    editor/                  <- the standalone GUI tool (CSEnvStart.py entry point)
    repository/
        CutsceneKeyEnum.py    <- every cutscene's identity (an enum member)
        CutsceneRegistry.py   <- maps each enum member -> a .ctsc file path
        CutsceneSetups.py     <- one @cutsceneSetup function per cutscene (the cast/room)
        CutsceneLoader.py     <- the class that ties a key + setup func + .ctsc data together
    sequences/                <- the actual subevent implementations (ToonSequence.py,
                                 SuitSequence.py, CameraSequence.py, GeneralSequence.py,
                                 AudioSequence.py, ParticleSequence.py, CogBattleSequence.py,
                                 CogBossSequence.py, GUISequence.py, EnvironmentSequence.py,
                                 ToonExpressionSequence.py)
    CutsceneSequenceBase.py   <- turns each sequence function into an "EventDefinition"
    CutsceneParticles.py

resources/phase_N/data/cutscenes/<name>/<name>.ctsc   <- the actual authored data (JSON)
```

The **`.ctsc` file** is just a JSON timeline of Events, each containing SubEvents
(one call into a `sequences/*.py` function). It has no idea what a "suit" or
"camera" object actually *is* at runtime — that's supplied separately by a
**setup function** in `CutsceneSetups.py`, which builds a `cutsceneDict`
(the cast: toons, suits, bosses, nodes, sounds, dialogue, etc.) and hands it to
the `.ctsc` data at playback time. This split is why the same `.ctsc` file can
be replayed with a totally different cast in a future patch, and why the
**editor** fakes up its own throwaway cast (`editor=True` branch) instead of
needing a live game session.

---

## 2. Step 1 — Register the cutscene's identity

Every cutscene needs three things before it can exist at all:

### a) An enum member — `toontown/cutscene/repository/CutsceneKeyEnum.py`

```python
class CutsceneKeyEnum(Enum):
    ...
    Witchhunter_Death = auto()
    MyNewBoss_Intro = auto()   # <- add yours near related entries
```

Order doesn't matter functionally (nothing serializes this enum by its integer
value to disk or network), but keep it grouped with related cutscenes for
readability.

### b) A registry entry — `toontown/cutscene/repository/CutsceneRegistry.py`

```python
newEntry(key=CutsceneKeyEnum.MyNewBoss_Intro, filePath='phase_11/data/cutscenes/mynewboss/mynewboss_intro.ctsc')
```

`filePath` is relative to `resources/`. This is the ONLY place the `.ctsc`
file's path is declared — get it wrong and `CutsceneLoader` will fail to find
your data (`json.loads(vfs.readFile(...))` will error).

### c) The actual `.ctsc` file — `resources/<filePath above>`

It can start as an empty array `[]`; you'll build it in the editor and export
over it (see Section 8). Create the directory if it doesn't exist yet.

---

## 3. Step 2 — Set up the `Distributed<Boss>` class

Every cutscene setup function needs a "room" object to call `loadEnvironment()`
on (see Section 4a). If you're building a brand-new encounter rather than
reusing an existing one, this class doesn't exist yet — here's how to make it.

### Where it lives

- Ordinary taskline/instance bosses: `toontown/instances/DistributedMyNewBoss.py`
- Street/Instance Mercs: `toontown/instances/mercs/DistributedInstanceMyNewBoss.py`

Either way, for a real (non-editor-only) boss you'll eventually need **two**
files, not one:

- `DistributedMyNewBoss.py` — the client-side class (this is the one the
  cutscene system cares about).
- `DistributedMyNewBossAI.py` — the server-side counterpart that actually
  drives the fight's state machine, HP, rewards, etc.

...plus a matching entry in `astron/dclass/toon.dc`:

```
from toontown.instances import DistributedMyNewBoss/AI
...
dclass DistributedMyNewBoss : DistributedInstance {
};
```

(The `/AI` suffix tells Astron's DC compiler that both the client class and
its AI counterpart come from `DistributedMyNewBoss.py`/`DistributedMyNewBossAI.py`.
An empty `{ }` body is fine if you're not adding any new distributed fields.)

**For cutscene-editing purposes, only the client-side class and its
`loadEnvironment()` method matter** — the editor never touches the AI side or
the network at all (see the "cutscene editor during a live session" note
below). Everything past this point in this section is what you need to get a
room rendering in the editor; the AI-side fight logic (FSM states, battle
phases, victory/death sequencing) is a much larger separate task best learned
by reading a comparable existing `...AI.py` file end to end.

### The minimal client-side class

The simplest working template — mirroring `toontown/instances/DistributedDerrickMan.py`,
one of the plainer taskline bosses — is:

```python
from panda3d.core import *
from direct.interval.IntervalGlobal import *
from direct.fsm import FSM

from toontown.instances import DistributedInstance
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class DistributedMyNewBoss(DistributedInstance.DistributedInstance, FSM.FSM):
    allowClickedNameTag = True

    def __init__(self, cr):
        DistributedInstance.DistributedInstance.__init__(self, cr)
        FSM.FSM.__init__(self, 'DistributedMyNewBoss')
        # Any encounter-specific state (safezone, elevator type, etc.) goes here.

    def loadEnvironment(self):
        DistributedInstance.DistributedInstance.loadEnvironment(self)
        self.geom = loader.loadModel('phase_X/models/modules/my_room_model')
        self.battleANode = self.geom.attachNewNode('battleA')
        self.battleANode.setPosHpr(0, 0, 0, 0, 0, 0)
        self.geom.reparentTo(render)   # <- don't forget this; see the gotcha below
```

A few important points, all drawn from real existing implementations:

- **Base class**: `DistributedInstance.DistributedInstance` (in
  `toontown/instances/DistributedInstance.py`) is what every boss/instance
  ultimately inherits from — it provides `__init__`, `announceGenerate`,
  `disable`/`delete`, and a **no-op** `loadEnvironment()`/`unloadEnvironment()`
  pair (`def loadEnvironment(self): pass`) that every subclass fully
  overrides. Mixing in `FSM.FSM` (`direct.fsm.FSM`) alongside it is the
  standard pattern for anything with fight-phase states, even though those
  states themselves are mostly an AI-side/real-gameplay concern.
- **`__init__(self, cr)`** always takes the client repository as its only
  real argument — this is exactly what the editor's setup function calls:
  `DistributedMyNewBoss(base.cr)` with `.doId = -420` set manually afterward
  (a real doId is normally assigned by the server on generate; the editor
  never talks to a server, so it just fakes one).
- **`loadEnvironment()`** is where you load whatever models make up the room
  and attach at least one **battle node** — a plain child `NodePath`
  (`self.geom.attachNewNode('battleA')` or similar) that acts as a stable
  origin for positioning toons/suits. This is what your cutscene setup
  function's `instance.battleNode` (or `instance.geom`, or whatever you name
  it) will actually be.
- **Always `reparentTo(render)` everything your cutscene will reference,
  inside `loadEnvironment()` itself** — not conditionally, not later in some
  FSM state. `DistributedCountErfit` is a cautionary example of getting this
  wrong: it loads a second model (`self.bossGeom`) but only reparents it to
  `render` much later, inside a real-gameplay FSM transition
  (`exitPreparePrepareBattleTwo`) that the cutscene editor never runs — so
  anything built on top of that pattern renders as an empty room in the
  editor. Simpler bosses like `DistributedDerrickMan` avoid this by
  reparenting straight through `loadEnvironment()`, and that's the pattern to
  copy for a new boss.
- Look at multiple existing examples before committing to a structure —
  `toontown/instances/DistributedDerrickMan.py` (plain taskline boss),
  `toontown/instances/DistributedCountErfit.py` (event boss with an elevator
  + two-stage boss room), and `toontown/instances/mercs/DistributedInstanceWitchhunter.py`
  (a merc, via the `DistributedInstanceMerc` intermediate base) each show a
  different level of complexity for essentially the same job.

Once this class exists and its `loadEnvironment()` runs cleanly, you're ready
for Section 4 — plug it into a `@cutsceneSetup` function exactly like the
`DistributedMyNewBoss` references already used throughout this guide.

---

## 4. Step 3 — Write the setup function

This is the most important, most easily-botched step: it decides **what room
you're in** and **what cast exists**. Add a new function to `CutsceneSetups.py`:

```python
@cutsceneSetup(CutsceneKeyEnum.MyNewBoss_Intro)
def __myNewBossIntroSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        # ---- Editor-only fake cast, for previewing in the standalone tool ----
        from toontown.instances.DistributedMyNewBoss import DistributedMyNewBoss
        instance = DistributedMyNewBoss(base.cr)
        instance.doId = -420          # any negative placeholder doId works
        instance.loadEnvironment()    # loads the room's models

        toons = CSEditorUtil.makeToons(4)
        suits = CSEditorUtil.makeSuits('mynewboss', 'mh', 'mh')
        for avatar in toons + suits:
            avatar.reparentTo(render)
    else:
        # ---- Real gameplay: everything is handed in by the caller ----
        toons, suits, instance = CSEditorUtil.getKwargs(kwargs, 'toons', 'suits', 'instance')

    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene(suits, maxSuitCount=3)
    cutsceneLoader.addActorsToCutscene(suits + toons)
    cutsceneLoader.addNodesToCutscene([instance.geom])
    return cutsceneLoader
```

### 4a. Choosing the room

The "room" is whatever model(s) the encounter's `Distributed<Boss/Instance>`
class loads in its `loadEnvironment()` method — that's the thing to call.
Look at the instance's file (e.g. `toontown/instances/DistributedCountErfit.py`,
`toontown/instances/mercs/DistributedInstanceWitchhunter.py`) to see:

- What `self.geom` / `self.bossGeom` / `self.battleNode` etc. actually are.
- **Whether everything gets reparented to `render` inside `loadEnvironment()`
  itself, or only later, as part of the real fight's FSM.** This is a real
  trap — `DistributedCountErfit.loadEnvironment()` attaches `self.geom` to
  `render` but leaves `self.bossGeom` (and anything parented under it, like
  the boss elevator) floating disconnected until a *much later* FSM state
  (`exitPreparePrepareBattleTwo`) reparents it. In real gameplay that FSM step
  always runs first, so nobody notices — but the editor only calls
  `loadEnvironment()` and nothing else, so anything that depends on a later
  FSM step will silently never appear. If your new cutscene's room shows
  "nothing" in the editor, this is the first thing to check: **manually
  reparent whatever your `.ctsc` events will reference, right after
  `loadEnvironment()`, in the `editor:` branch.**
- If the instance has a pre-built battle formation node (like Witchhunter's
  `instance.battleNode`), prefer using it — it's already a sane, tested
  parent/origin for actor positioning.

### 4b. Suit spawn points

There are three ways cast members get positioned, and most cutscenes mix all
three:

1. **Formation helper** — `CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[...], newParent=battle)`
   drops toons/suits into the standard battle-circle formation
   (`BattleBase.toonPoints` / `BattleBase.suitPoints`) under a given parent
   node. Good for "everyone is already here when the cutscene starts."
2. **Manual placement** — just `avatar.reparentTo(render)` (or some other
   node) and, if needed, `avatar.setPos(...)` directly in the setup function.
   This is what you do for suits that should start **off-camera/invisible**
   and get moved into place later purely by `.ctsc` events (see next point).
3. **Event-driven arrival** — most dramatic entrances (a suit flying in,
   walking up, teleporting) are NOT positioned in the setup function at all.
   Instead: `hideSuit`/`showSuit` (start hidden), then a movement subevent —
   `suitSupaFly` (propeller fly-in/out), `moveActor`, `turnSingleSuitToPoint`,
   or `tpToonsToElevator` — does the actual positioning once the timeline
   reaches that point. This is how the original `Witchhunter_Death`
   cutscene brings its two mob-mentality cogs in (`hideSuit` at t=0,
   `showSuit` + `suitSupaFly(flyType=2)` at t=8).

If a suit will use `suitSupaFly` (which calls `attachPropeller()` under the
hood), **lock its propeller** at t=0 via `suitLockPropeller(suitIndex, locked=True)`
if you want the propeller to stay visibly attached after it lands — and
remember to unlock it (`locked=0`) in your cleanup event, or it'll stay stuck
on for any *later* cutscene that reuses the same suit object.

### 4c. `addXToCutscene` cheat-sheet (`CutsceneLoader` methods)

| Method | Populates | Notes |
|---|---|---|
| `addToonsToCutscene(list, maxToonCount=N)` | `cutsceneDict['toons']` | Pads with `None` up to `maxToonCount` |
| `addSuitsToCutscene(list, maxSuitCount=N)` | `cutsceneDict['suits']` | Pads with `None`. **Give the real count if you can** — `.ctsc` events on a `None` slot silently no-op |
| `addBossesToCutscene(list, maxBossCount=N)` | `cutsceneDict['bosses']` | For `BossCog`/`CSEditorUtil.makeBosses(*deptNames)` |
| `addActorsToCutscene(list)` | `cutsceneDict['actors']` | Used by `actorDialogue`/`actorChat`/`moveActor`/`turnActor`/`hideNametag`. Order = `actorIndex`. Usually `suits + toons` |
| `addNodesToCutscene(list)` | `cutsceneDict['nodes']` (appended) | Starts pre-seeded as `[render, hidden, camera]` (indices 0-2) — your list starts at index 3. Used by `nodeIndex` args (camera reparent targets, explosion targets, turn-to-node targets, etc.) |
| `addElevatorsToCutscene(list)` | `cutsceneDict['elevators']` | Used by `cameraToElevator`/`tpToonsToElevator` |
| `addDialogueToCutscene(list_or_tuple)` | `cutsceneDict['messages']` | Indexed by `messageIndex` in `actorDialogue`/`actorChat`. Can be an inline tuple in the setup function, or `TTLocalizer.InstanceMinibossCutscenes['key'][0 or 1]` |
| `addSoundsToCutscene(list_of_paths_or_AudioSound)` | `cutsceneDict['sounds']` | Indexed by `sfxIndex` in `playSoundEffect`. String paths get auto-loaded via `loader.loadSfx` |
| `addMusicToCutscene(list_of_music_codes)` | `cutsceneDict['music']` | Indexed by `musicIndex` in `playMusic`/`stopMusic` |
| `addParticleSystemsToCutscene(names)` | `cutsceneDict['particles']` | Via `getCutsceneParticleSystems` |
| `addVisualEffectsToCutscene(enums)` | `cutsceneDict['visualEffects']` | Indexed by `vfxIndex` in `suitApplyVisualEffect` etc. |
| `addFunctionsToCutscene(callables)` | `cutsceneDict['functions']` | For `functionCall`/`functionLerp` subevents |
| `addArgumentsToCutscene(list)` | `cutsceneDict['arguments']` | Generic argument pool some subevents pull from |
| `addStuffToCutscene(*things, ...)` | (auto-sorts) | Lazy one-shot alternative to calling the above individually — sorts by `isinstance` (Toon/Suit/BossCog/Actor/etc.) |

**Every index space above is independent.** `actorIndex 0` and `suitIndex 0`
and `nodeIndex 0` are three completely different lookups — mixing them up is
one of the easiest mistakes to make when hand-editing a `.ctsc` file.

---

## 5. Step 4 — Point the editor at your new cutscene

Edit `toontown/cutscene/editor/CSEnvConfig.py`:

```python
CutsceneEditKey = CutsceneKeyEnum.MyNewBoss_Intro
EditMode = True   # loads your registered .ctsc file via the setup function above
```

Launch it from the repo root:

```
Panda3D-1.10.11/python/python.exe -m toontown.cutscene.editor.CSEnvStart
```

If the room is empty or the camera looks at nothing, press **F2** for
free-camera (oobe) mode and fly around — this tells you immediately whether
your cast/room actually exists in the scene graph (see the `bossGeom` trap
above) versus just being out of the current camera's framing.

---

## 6. Step 5 — Learn the GUI layout

The editor is its own standalone window (not overlaid on anything else), with
a real 3D view of your cutscene looping in the background while you work.
Everything is laid out in a handful of fixed panels:

### Top bar — playback & timeline

- A horizontal **progress bar** across the very top of the screen. Click or
  drag anywhere on it to scrub to that point in time. Colored blocks along it
  are your Events — green normally, gold when selected. Hover a block to see
  its name; **right-click** a block to snap the time-entry field to its exact
  start time.
- A **pause button** (`=` / `>`) in the top-left toggles playback; the **`p`**
  key does the same thing without needing to click.
- Two small text-entry fields: top-left shows/sets the **current time**
  (type a number + Enter to jump there), top-right shows/sets the cutscene's
  total **duration** (typing a larger number here extends the track; it also
  auto-grows to fit your latest event automatically).

### Bottom-left panel — Events

- **Name** and **time** fields for whichever event is currently selected.
- Two checkboxes, **Ordered** vs **Simultaneous** — this is the event's
  `sequenceMode` (`Sequence` vs `Parallel`) from the raw JSON.
- **`<<` / `>>`** buttons jump to the previous/next event in time order.
- **`+`** creates a brand-new event at the current playhead time.
- **`x`** deletes the selected event (the very first `time: 0.0`
  "Initialization" event can't be deleted — it's protected).
- Below that, a scrollable list of the selected event's **subevents**, each
  as a colored block (color = its category, matching the picker below) with
  its own controls: an `x` to delete it, `>` to **extract** it into a brand
  new event of its own (handy for splitting an overloaded event apart), and
  up/down arrows to reorder it within the event (matters for `Sequence`-mode
  events, where order = playback order).
- **Add Subevent** flips this same panel into a categorized picker of every
  available subevent type (grouped by `ToonSequence`/`SuitSequence`/
  `CameraSequence`/etc., matching the colors above). Click a category header
  to see its entries, click an entry to attach a new subevent of that type to
  whichever event is currently selected. Hidden categories
  (`HiddenCategoryNames` in `CSEnvConfig.py`) and individually
  `hidden=True`-flagged subevent types won't show up here at all — see the
  troubleshooting note in Section 10 if you're looking for one that's missing.

### Bottom-right panel — Subevent arguments

Click a subevent (either in the list above, or its colored block) to select
it — this panel then fills with one **adjuster** control per argument the
underlying `sequences/*.py` function takes: sliders for numbers/positions,
dropdowns for suit/toon/node/animation choices, checkboxes for booleans, text
fields for strings, etc. Changes here apply live — scrub the timeline back
across the subevent to preview the result immediately.

### Top-left "Edit" dropdown

A small toolbox of bulk-editing utilities, currently just **Move**: shifts
every event within a chosen time range by a fixed offset. Useful for
inserting time into the middle of an already-built timeline without manually
re-typing every subsequent event's `time` field by hand.

### Hotkeys

| Key | Action |
|---|---|
| `Space` | Autosave the current state to `cutscene_editor_autosave.json` |
| `p` | Toggle pause/unpause |
| `F2` | Toggle free-camera (oobe) mode — fly around independent of the cutscene's own camera track, great for scouting shots or confirming content actually exists in the scene |

### A typical editing loop

1. Scrub/jump to roughly where you want something to happen.
2. Hit **`+`** to drop a new event there (or select an existing nearby one if
   you want to add to it instead of making a new one).
3. Set **Ordered**/**Simultaneous** depending on whether its subevents should
   play back-to-back or all at once.
4. Click **Add Subevent**, pick a type from the categorized list.
5. Select the new subevent block, tune its arguments in the bottom-right
   panel while watching the 3D view.
6. Repeat. Use `<<`/`>>` to hop between existing events as the timeline grows,
   and the top progress bar to spot-check playback at any point.
7. `Space` periodically to autosave — see Section 8 for turning that into
   your final `.ctsc` file.

---

## 7. Step 6 — Build the timeline

### Events vs. Subevents

- An **Event** is a point in time (`time`) with a `sequenceMode`:
  - `Sequence` — its subevents play one after another.
  - `Parallel` — its subevents all start at the same time.
- Each **Subevent** is one call into a decorated function in `sequences/*.py`
  (an `EventDefinition`, referenced by its `eventDefEnum` name in the raw
  JSON, e.g. `"moveCameraPos"`).
- In the GUI: select an event (bottom-left panel), hit **Add Subevent** to
  flip into the categorized picker, click a type to attach it, then use the
  bottom-right panel to tune its arguments live.
- `HiddenCategoryNames` in `CSEnvConfig.py` can hide whole categories from
  that picker (not individual entries). Some individual subevents are marked
  `hidden=True` in their own decorator (e.g. `Erfit: Summon Suit`) — those
  never appear in the "Add" picker at all, even if their category is shown,
  but they still work fine and still display normally if they're already
  present in loaded `.ctsc` data.

### Dialogue

- `actorDialogue` (speech bubble w/ optional nametag hide) and `actorChat`
  (raw chat bubble) both take `actorIndex` + `messageIndex` (into whatever
  you passed to `addDialogueToCutscene`) plus `duration`/`delay`.
- `actorShutUp` force-clears whatever bubble is currently showing for that
  actor — always fire this for every speaking actor in your final "clean up"
  event so nothing lingers after the cutscene ends.

### Camera

| Subevent | What it does |
|---|---|
| `reparentCamera(targetIndex, wrt)` | Re-parents the camera to a node (index into the `nodes` list). `wrt` keeps its current world transform across the reparent |
| `moveCameraPos` / `moveCameraHpr` / `moveCameraPosHpr` | Lerp position/rotation/both. Always fill in `startPos`/`startHpr` (or set `useStartPos`/`useStartHpr` to `false` to just use wherever the camera currently is) |
| `changeCameraFov` | Lerp field of view |
| `cameraToElevator` | Hidden/specialized — snaps to a registered elevator (`addElevatorsToCutscene`) |

Camera moves compound on whatever the *previous* camera event left it at —
plan your shot list roughly chronologically before hand-authoring exact
numbers, or just eyeball it live in the editor and read back the resulting
values (right panel shows live pos/hpr as you nudge, and F2/oobe lets you
scout good camera spots by hand).

### Suit/toon animation & movement

- `doSuitAnim` / `animateAllToons` / `animateSingleToon` — one-shot or looping
  animation, with optional blend-out to an `endAnim`.
- `doSuitBlendAnim` — smooth crossfade between two named anims (nicer than a
  hard cut for e.g. walk→neutral).
- `doSuitPingpong` / `pingpongSingleToon` — play an anim forward then
  backward repeatedly (good for nervous fidgeting / comedic beats).
- `turnSingleSuitToPoint` / `turnSingleSuitToNode` / `turnSingleSuitToHpr`
  (and the `turnSuitsTo*`/`turnToonsTo*` "all" variants) — reorient toward a
  raw point, a registered node, or an explicit HPR.
- `moveActor` / `turnActor` — the generic (works on suits or toons) position/
  rotation setter, used for anything not covered by the suit/toon-specific
  helpers above.
- `suitSupaFly` — propeller fly in (`flyType=2`) or out (`flyType=1`) to a
  `destPos`. This is the standard "cog arrives/departs dramatically" move.
- `tpToonsToElevator` / `moveToonsToBattlePos` / `moveToonsInBlock` — group
  toon formation/teleport helpers, typically used at the very start (getting
  toons out of the elevator) or transition points.

**Safe, generic animation names** confirmed across multiple existing
cutscenes (work on any suit body): `neutral`, `walk`, `run`, `flail`,
`slip-forward`. Character-specific special anims (`mob-mentality`,
`transformation`, `rage-sgoat`, `objection-in/loop/out`, etc.) only exist on
the specific boss they were built for — check that character's existing
cutscenes before reusing one on a different suit type. Same idea for toons:
`neutral`, `walk`, `run`, `wave`, `slip-forward`, `sit` are broadly safe.

### Effects

- `createExplosion(nodeIndex, scale)` — a cartoon "kapow" burst at a node's
  position (the node needs `.getHeight()`, so target a Suit/Toon/BossCog, not
  an arbitrary prop).
- `playSoundEffect(sfxIndex, hasNode, nodeIndex, loop, hasDuration, duration, volume, startTime, isInterval)`
  — plays whatever you registered via `addSoundsToCutscene`. Browse
  `resources/phase_N/audio/sfx/*.ogg` for existing stingers before assuming
  you need a new asset — there's a lot already there (gavels, alarms,
  paper-throws, zaps, etc., grouped by phase and roughly named by their
  source system, e.g. `LB_` = Lawbot, `SA_` = suit attack).
- `playMusic` / `stopMusic` — via `addMusicToCutscene`.
- Particle/GUI/environment sequences (`ParticleSequence.py`,
  `GUISequence.py`, `EnvironmentSequence.py`) exist for fog, screen fades,
  spawned particle systems, etc. — check those files directly for exact
  signatures before using one; some (like the High Roller ones) are built
  for one specific encounter's assets and won't generalize.

### Suit lifecycle housekeeping

Every suit that should start invisible needs, at `time: 0.0`:
- `hideSuit(suitIndex)`
- `hideNametag(actorIndex)` (matching index into the *actors* list, not suits)
- `suitLockPropeller(suitIndex, locked=True)` if it'll `suitSupaFly` in later
  and you want the propeller to stay attached afterward

And your final "clean up" event should mirror all of that in reverse:
`actorShutUp` for every speaking actor, `suitLockPropeller(..., locked=0)`
for every suit you locked, and reset the camera FOV back to its default
(usually `60.0`) so nothing bleeds into whatever plays next.

---

## 8. Step 7 — Save and export your work

- **Space** autosaves the current state to `cutscene_editor_autosave.json` in
  the working directory (also fires automatically every ~20s). This is a
  scratch/recovery file, not your final asset.
- There is no in-editor "save to resources" button. When you're happy with
  it, copy the JSON content out of the autosave file (it's the same
  `Cutscene.toDict()` shape as the real `.ctsc` format) into your actual file
  at `resources/<filePath from CutsceneRegistry>`.
- Reload the editor (or press `p`/scrub the timeline) to sanity-check the
  final file loads and plays cleanly from a cold start, not just from
  whatever state you were mid-editing.

---

## 9. Step 8 — Wire it into real gameplay

Somewhere in your boss/instance's AI or client code, at the point the
cutscene should actually play:

```python
cutsceneLoader = CutsceneLoader.createLoader(
    key=CutsceneKeyEnum.MyNewBoss_Intro,
    toons=toons,      # real DistributedToon objects
    suits=suits,       # real DistributedSuit objects
    instance=self,     # the real instance object
)
track = cutsceneLoader.buildCutscene(callback=self.someCallback, delayDeleteToons=True)
track.start()
```

The kwargs you pass here are exactly what your setup function's `else:`
branch (`CSEditorUtil.getKwargs(kwargs, 'toons', 'suits', 'instance')`) pulls
out — keep the kwarg names consistent between the two, or the live game
version will raise a `KeyError` even though the editor preview works fine.

---

## 10. Troubleshooting checklist

- **Room/cast is empty in the editor** — press F2/oobe first to rule out a
  camera-framing issue before assuming content failed to load. If oobe shows
  a truly empty scene, check whether your instance's `loadEnvironment()`
  actually reparents everything to `render`, or whether (like Erfit's
  `bossGeom`) part of it only gets attached later in the real FSM flow that
  the editor skips — add the missing `reparentTo(render)` call directly in
  your setup function's `editor:` branch.
- **A dropdown crashes with `KeyError: 'Unknown option "text_scale"'`** —
  this was a real bug in `CSPanelAdjusters.py`'s `DropdownSuits`/`DropdownToons`
  (now fixed) where padded/empty slots got handed to the GUI as raw `None`
  instead of a placeholder label. If you hit this again on a different
  dropdown class (`DropdownActors`, `DropdownBossCogs`, `DropdownNode`, etc.
  — several still have the same unfixed pattern), it means that slot is
  genuinely empty; give the real count to `maxSuitCount`/`maxToonCount`/etc.
  where you can, to avoid empty slots existing at all.
- **A subevent silently does nothing** — almost always means its target
  index (`suitIndex`/`toonIndex`/`nodeIndex`/`actorIndex`) points at a `None`
  slot. Every `seq_*` function in `sequences/*.py` guards with
  `if not suit: return Sequence()` — no error, just nothing happens.
  Double-check your `maxXCount` matches your real cast size.
- **Scrubbing the timeline crashes with `AssertionError: !is_empty()`** — a
  `Func` in the track tried to operate on an empty/disconnected `NodePath`
  (commonly `reparentTo` onto something with no parent, e.g.
  `attachPropeller()`'s joint lookup coming up empty, or a node from the
  "room is empty" bug above). Cross-reference whichever subevent is near the
  current scrub position.
- **Cutscene works in editor but errors in real gameplay** — check that your
  setup function's non-editor kwarg names match exactly what the real caller
  passes to `CutsceneLoader.createLoader(...)`.
