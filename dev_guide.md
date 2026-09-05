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
  current room. Enemy, ally, and companion registries are checked in that
  order, so a name can only ever match one of the three.
  - Spawning a companion doesn't automatically add them to your team — follow
    up with `recruit <name>` (companions spawned this way have no
    `required_items`, so recruiting succeeds immediately).
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
  (`player.known_spells`), skipping the need for a `SpellBook` item.
  - Example: `dev grant spell test bolt` — the only spell registered right
    now (see below); mid-combat, `cast test bolt` deals 6 damage and applies
    3 turns of poison in one go.

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
of athena`, `favour of hermes`, `test spellbook`, `test healing tonic`,
`test venom vial`.

**Enemies** (`dev spawn <name>`): `training dummy`, `skeleton warrior`,
`minotaur`, `hades`.

**Allies** (`dev spawn <name>`): `chiron`, `mentor`, `wounded soldier`,
`charon`, `athena`, `ares`, `hermes`, `prometheus`.

**Companions** (`dev spawn <name>`): `test companion` — a dev-only stand-in
with all three AI actions live (non-zero attack, `heal_amount`, and
`brace_amount`), no `required_items`, so `recruit test companion` succeeds
immediately after spawning.

**Spells** (`dev grant spell <name>`): `test bolt` — a dev-only combo spell
(damage + poison in one cast).

## What can't be playtested through real game content yet

Companions, Spells, and status-effect items all have their full engine
built and unit-tested, and are now genuinely reachable in a live `main()`
run through dev tooling (see the recipes above and below) — but none of the
three exist as *real, narrative* content placed anywhere by `build_world()`:

- **Companions.** No room in the actual world holds a recruitable
  `Companion` — `dev spawn test companion` (above) is the only way to reach
  one right now. The full system (recruiting, fighting alongside you, being
  downed, `dismiss`, `Reviver`) works identically either way, since it's the
  same `Companion` class and the same `recruit_companion()`/combat AI either
  way.
- **Spells.** `test bolt` (above) is the only registered `Spell`, and `test
  spellbook` (`dev add`) is the only way to actually pick up a `SpellBook`
  item — no real ally/loot grants one yet. Mana/`rest`/`wait` work fine on
  their own regardless.
- **Status-effect items.** `test healing tonic` and `test venom vial`
  (`dev add`, above) are the only two `StatusEffectItem`s that exist, and
  neither is real loot or a trade reward yet. `dev afflict` (above) remains
  the more direct way to test status-effect ticking without needing either
  item.

Real, narrative versions of all three are expected as part of "Populate all
floors" (`roadmap.md`) — until then, the `test ...` names above are the only
way to reach any of this outside the automated test suite.

- **Ranged attacks — currently unreachable through *any* means, not even dev
  tools.** `attack ranged` requires an equipped ranged (`slot="ranged"`)
  `Weapon`, but no such weapon exists anywhere — not in real game content,
  and not as dev-test content either (unlike Companions/Spells/status-effect
  items above, there's no `create_test_*()` ranged weapon and no
  `ITEM_REGISTRY` entry for one). Until one is added, the only way to
  exercise the `"ranged"` branch of `Character.attack()` at all is a direct
  unit test (see `test_characters.py`/`test_combat.py`), not a live
  `main()` run. `attack`/`attack light`/`attack heavy` need no such
  workaround — every enemy encounter reaches them fine.

Everything else that's landed recently — the helmet/body armour split,
durability degrading in combat, repairing at the Forge of Prometheus (floor
2, `is_forge=True`), Dodge, light/heavy attacks, and the Practice Chamber's
respawning dummy — has real, reachable in-game content and needs no dev-tool
workaround to try.

## The Practice Chamber isn't a dev tool
Unlike everything else in this file, the Practice Chamber (floor 2, next to
the Forge of Prometheus) and its `dummy set <stat> <value>` command are
**real, player-facing content** — reachable by walking there normally, and
working with `DEV_MODE` off. It's listed in `get_controls_text()`/the
README's Controls section like any other command, not hidden the way every
`dev ...` command deliberately is.

- The room's dummy (`Enemy.respawns = True`) resets to full HP - instead of
  being removed - the moment it's defeated, so it can be fought indefinitely.
- Casting a spell inside costs no mana and never starts a cooldown
  (`room.is_practice_chamber` short-circuits both checks in
  `handle_combat_command()`) - items and weapons were already free of any
  resource cost, so nothing changed for those.
- `dummy set <stat> <value>` (message-prefixed `[Practice]`) works the same
  way `dev set` does for the player, minus the `skillpoints` special case
  (the dummy has no skill tree) - see `handle_dummy_set()`/`_apply_stat()`
  in `dev_tools.py`.

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

**Recruit a companion and fight alongside them:**
```
dev spawn test companion
recruit test companion
dev spawn skeleton warrior
attack
```

**Try casting a spell:**
```
dev grant spell test bolt
dev spawn minotaur
attack
cast test bolt
```
(`cast` only works mid-combat, so `attack` first to lock in; a tougher enemy
like the Minotaur keeps it alive long enough to see both the damage and the
poison apply in the same cast.)

**Try the Practice Chamber (free casting, a dummy you can't permanently kill):**
```
dev grant spell test bolt
dev teleport practice chamber
attack
cast test bolt
cast test bolt
```
The second `cast test bolt` succeeds immediately - no cooldown, no mana
spent - which would block it anywhere else. Follow up with
`dummy set atk 20` between fights to make the dummy hit back harder, or
`dummy set hp 100` to make it last longer against high-damage builds.

**Try a secondary ancestor ability without restarting character creation:**
```
dev set has_petrifying_gaze 1
dev spawn skeleton warrior
attack
```
`dev set` writes any real `Player` attribute by name (see above), and that
happens to include all ten secondary-ancestor flags
(`has_reckless_strength`, `has_measured_casting`, `has_swift_feet`,
`has_unyielding_tide`, `has_berserking`, `has_silver_tongue`,
`can_ranged_without_weapon`, `has_petrifying_gaze`, `has_bull_rush`,
`has_iron_hide`) - `setattr` doesn't care that the value arrives as `1`
(an `int`) rather than `True` (a `bool`), and every `if self.has_...:`
check treats them identically. Much faster than restarting the game to
pick a different secondary ancestor each time you want to try one.
