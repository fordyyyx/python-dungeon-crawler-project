# Developer & Playtesting Guide

Everything here is for people poking at the game itself, not playing it straight
through — the full `dev ...` command set, what real content exists to spawn/add
right now, and which newer systems can't be reached through normal play yet
(and how to test them anyway). None of this appears in-game via `controls` —
dev commands are deliberately hidden from that list.

## Activating developer mode
- **At the very start of a run**: when asked "What is your name, hero?", type
  `developer mode`. This renames you to `Dev`, activates `DEV_MODE`, and adds
  an extra prompt letting you pick which floor to start on (`floor_0` through
  `floor_9`).
- **Mid-game**: type `developer mode` as a command at any point to toggle
  `DEV_MODE` on or off, without restarting. Dev commands only work while it's
  on.
- Dev commands are checked ahead of the combat-lock routing, so they always
  work — even mid-fight.

## The dev test room
A deliberately empty room, not connected to anything and not part of any
floor — reachable only via `dev teleport dev test room`. Useful as a blank
slate for spawning/adding things without any of a real room's existing
content getting in the way.

## Full dev command reference

### Stats
- `dev set <stat> <value>` — generic: writes any real, whole-number `Player`
  attribute by name (`hp`, `attack_damage`, `armour`, `gold`, `experience`,
  `level`, `intellect`, `mana`, `max_mana`, etc.), plus shorthand aliases
  `atk` → `attack_damage`, `def` → `armour`, `hp` → `hp`, `maxhp` → `max_hp`.
  `skillpoints` is special-cased (it lives on `player.skill_tree`, not
  directly on `player`). Setting `hp` above `max_hp` raises `max_hp` to
  match, and setting `max_hp` below the current `hp` clamps `hp` down.
- `dev set durability <helmet|body> <value>` — directly sets the durability
  of whatever `Armour` is equipped in that slot (clamped to
  `0..max_durability`), correctly adjusting `player.armour` if this crosses
  the broken/repaired threshold. Returns an error if nothing is equipped
  there.
- **Limitation**: `dev set` always parses the value as a whole number
  (`int(...)`) — it **cannot** set float-valued stats (`dodge_chance`,
  `aggression_weight`, `caution_weight`, `randomness_weight`) or non-numeric
  ones (`ancestry_label`, `companion`). Use `dev learn abilities` (below) to
  reach Dodge instead.

### Items and characters
- `dev add <item>` — adds a known item straight to your inventory (see the
  registry list below for exactly what "known" means right now).
- `dev spawn <character>` — spawns a known enemy, ally, or companion into the
  current room.
- `dev remove <character>` — removes the first matching enemy or ally in the
  room by name.
- `dev remove all <character>` — removes every instance of that name.
- `dev clear room` — removes every enemy and ally in the room, regardless of
  name.
- None of the three removal commands trigger loot, XP, or gold — a dev
  removal is not a kill.
- `dev kill` — instantly defeats your current combat target if it's in the
  room, otherwise the room's first enemy. This *does* grant real loot/XP/gold,
  since it reuses the same defeat-handling as a normal kill.

### Status effects
- `dev afflict <target> <effect> <amount> <duration>` — applies a
  `StatusEffect` directly to `player`, `companion`, or a named enemy in the
  room. `amount` is a whole number (negative = damage per tick, positive =
  heal per tick); `effect` must be a single word (no spaces). This is
  currently the **only** way to reach status effects in actual play — see
  "What can't be playtested yet" below.
  - Example: `dev afflict player poison -3 4` — 3 damage/turn for 4 turns.
  - Example: `dev afflict companion regen 5 3` — 5 HP/turn for 3 turns.
  - Example: `dev afflict skeleton warrior poison -2 3` — multi-word enemy
    names work too; the last three tokens are always `effect`, `amount`, and
    `duration`, so everything before them is the target name, however many
    words that is.

### Spells
- `dev grant spell <name>` — grants a known spell straight to your spellbook
  (`player.known_spells`), skipping the need for a `SpellBook` item. See
  "What can't be playtested yet" below — right now there's nothing registered
  for this to find.

### Movement and world state
- `dev teleport <room name>` — case-insensitive teleport to any room in the
  dungeon (including the dev test room), clearing your combat state on
  arrival.
- `dev unlock <direction>` — removes one locked exit from the current room.
- `dev unlock all` — removes every locked exit from the current room.

### Skills
- `dev learn <path>` — grants a free skill point and immediately spends it on
  `attack`, `defence`, or `abilities` (refunded automatically if the path
  name is invalid, so it never costs you a point on a typo). Repeat four
  times on `abilities` to reach Dodge (Double Strike → Thorns → Last Stand →
  Dodge, in that order).

### Misc
- `dev help` — prints a short in-game summary of the command set (terser
  than this file).

## What's actually spawnable/addable right now

These are the only names `dev add`/`dev spawn` currently recognise (matched
case-insensitively):

**Items** (`dev add <name>`): `wooden sword`, `wooden shield`, `dummy head`,
`mentor's token`, `charon's coin`, `bronze xiphos`, `shield of aegis
(fragment)`, `vial of ambrosia`, `bronze breastplate`, `small healing
potion`, `cyclops eye`, `spear of ares`, `centaur's broken bow`, `breastplate
of athena`, `favour of hermes`.

**Enemies** (`dev spawn <name>`): `training dummy`, `skeleton warrior`,
`minotaur`, `hades`.

**Allies** (`dev spawn <name>`): `chiron`, `mentor`, `wounded soldier`,
`charon`, `athena`, `ares`, `hermes`, `prometheus`.

**Companions, Spells**: none yet — see below.

## What can't be playtested yet

Three systems have their full engine built and unit-tested, but no real
in-game content to actually reach them through *any* command, dev-assisted or
not:

- **Companions.** No `Companion` exists anywhere in the built world, and
  `dev spawn`'s companion lookup has an empty registry to search — `recruit`
  can never succeed right now. The whole system (recruiting, fighting
  alongside you, being downed, `dismiss`, `Reviver`) is exercised only by the
  automated test suite.
- **Spells.** No `Spell` is registered anywhere, so `dev grant spell` can
  never find one, and there's no `SpellBook` item to pick up either — you can
  never end up with anything in `known_spells`, so `cast <spell>` can never
  actually be tried in play. Mana/`rest`/`wait` work fine on their own; there
  is simply nothing to spend the mana on yet.
- **Status-effect items.** No `StatusEffectItem` is registered in `dev add`'s
  item list, and none exist as real loot/trade rewards either. `dev afflict`
  (above) is the one deliberate exception carved out specifically so this
  system *can* be playtested despite that — it applies the same
  `StatusEffect`/`apply_status_effect()` machinery a real item or spell would.

Everything else that's landed recently — the helmet/body armour split,
durability degrading in combat, repairing at the Forge of Prometheus (floor
2, `is_forge=True`), and Dodge — has real, reachable in-game content and
needs no dev-tool workaround to try.

## Quick recipes

**Test armour durability and repair without grinding combat:**
```
dev add bronze breastplate
use bronze breastplate
dev set durability body 1
dev teleport forge of prometheus
dev set gold 100
repair bronze breastplate
```

**Try Dodge:**
```
dev learn abilities
dev learn abilities
dev learn abilities
dev learn abilities
```

**Try poison/regen ticking:**
```
dev spawn skeleton warrior
dev afflict skeleton warrior poison -2 3
attack
```
