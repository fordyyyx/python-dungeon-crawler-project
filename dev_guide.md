# Developer & Playtesting Guide

Everything here is for people poking at the game itself, not playing it straight
through — the full `dev ...` command set, what real content exists to spawn/add
right now, and which newer systems can't be reached through normal play yet
(and how to test them anyway). None of this appears in-game via `controls` —
dev commands are deliberately hidden from that list.

## Activating developer mode
- **The title screen comes first now** — New Game / Load Game / Delete Save /
  Quit, then a profile and slot prompt. None of this is dev-specific; pick
  New Game and any empty profile/slot to reach the name prompt below. (Real
  save files land under `saves/` in the working directory — fine for
  throwaway dev testing, but worth clearing out afterwards if you don't want
  test saves cluttering the slot picker.)
- **At the very start of a run**: when asked "What is your name, hero?", type
  `developer mode`. This renames you to `Dev`, sets `player.dev_mode = True`,
  and adds an extra prompt letting you pick which floor to start on
  (`floor_0` through `floor_9`).
- **Mid-game**: type `developer mode` as a command at any point to toggle
  `player.dev_mode` on or off, without restarting. Dev commands only work
  while it's on.
- **`dev_mode` is per-save now, not per-process** — it lives on `Player`
  (round-tripped through `save_system.py` like any other field, having moved
  off an old `dev_tools.py` module global), so a save you started in
  developer mode reloads back into developer mode, and a normal save stays
  normal, regardless of what any other save/session did.
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
  `def`/`armour` sets the *total* armour, worn gear included - the difference
  goes into `base_armour`, so unequipping gear afterwards drops it back down.
  `skillpoints` is special-cased (it lives on `player.skill_tree`, not
  directly on `player`). Setting `hp` above `max_hp` raises `max_hp` to
  match, and setting `max_hp` below the current `hp` clamps `hp` down.
- `dev set durability <helmet|body|shield> <value>` — directly sets the
  durability of whatever `Armour` is equipped in that slot (clamped to
  `0..max_durability`); `player.armour` follows automatically, since it's
  calculated from worn, unbroken pieces. Returns an error if nothing is
  equipped there, or if the slot isn't one of the three.
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
  - Example: `dev grant spell test bolt` — mid-combat, `cast test bolt`
    deals 6 damage and applies 3 turns of poison in one go.
  - Example: `dev grant spell prayer bolt` — the real spell (see below);
    `cast prayer bolt` deals 8 damage for 6 mana.

### Movement and world state
- `dev teleport <room name>` — case-insensitive teleport to any room in the
  dungeon (including the dev test room), clearing your combat state on
  arrival.
- `dev unlock <direction>` — removes one locked exit from the current room.
- `dev unlock all` — removes every locked exit from the current room.
  Both go through `Room.unlock_exit()`, the same permanent unlock as walking
  through a locked door normally, so they're saved like any other.

### Skills
- `dev learn <path>` — grants a free skill point and immediately spends it on
  `attack`, `defence`, or `abilities` (refunded automatically if the path
  name is invalid, so it never costs you a point on a typo). Repeat four
  times on `abilities` to reach Dodge (Double Strike → Thorns → Last Stand →
  Dodge, in that order). `attack` and `defence` each have five tiers
  (+2/+3/+4/+5/+6), so it takes five on either to max it.

### Misc
- `dev help` — prints a short in-game summary of the command set (terser
  than this file).

## What's actually spawnable/addable right now

These are the only names `dev add`/`dev spawn` currently recognise (matched
case-insensitively):

**Items** (`dev add <name>`): `wooden sword`, `wooden shield`, `dummy head`,
`mentor's token`, `charon's coin`, `bronze xiphos`, `vial of ambrosia`,
`bronze breastplate`, `small healing potion`, `cyclops eye`, `spear of ares`,
`centaur's broken bow`, `skeleton bone`, `breastplate of athena`, `favour of
hermes`, `weathered helm`, `vial of grave rot`, `harpy-fletched bow`, `tome of
old prayers`, `chipped stone aegis`, `wineskin of dionysus`, `lamia's fang`,
`sun-scorched dagger`, `talos' bronze plating`, `serpent's kiss`, `labrys`,
`test spellbook`, `test healing tonic`, `test venom vial`.

**Enemies** (`dev spawn <name>`): `training dummy`, `skeleton warrior`,
`minotaur`, `hades`, `centaur`, `cyclops`, `shade`, `crypt keeper`, `harpy`,
`fanatic`, `lurker`, `petrified guardian`, `satyr`, `lamia`, `ember wraith`,
`talos`, `medusa`, `gorgon`, `medusa (awakened)`, `practice enemy` (the
Practice Chamber's respawning dummy), `test boss` — a dev-only,
two-phase boss (hp 1 throughout) whose first phase is gated behind a
two-add wave, exercising `next_wave_factories`/`wave_gate_factory`/
`next_phase_factory` end-to-end. `medusa`/`gorgon`/`medusa (awakened)` are
the real equivalent now (floor 4, Lair of Medusa) - `test boss` stays
useful for isolated testing without a full room/fight.

**Allies** (`dev spawn <name>`): `chiron`, `mentor`, `wounded soldier`,
`charon`, `athena`, `ares`, `hermes`, `prometheus`.

**Companions** (`dev spawn <name>`): `shade of achilles` — the real floor 5
companion, spawned still needing his duel (`challenge shade of achilles`
before `recruit`); his duel form is deliberately *not* spawnable on its own.
`test companion` — a dev-only stand-in
with all three AI actions live (non-zero attack, `heal_amount`, and
`brace_amount`), no `required_items`, so `recruit test companion` succeeds
immediately after spawning.

**Spells** (`dev grant spell <name>`): `test bolt` — a dev-only combo spell
(damage + poison in one cast); `prayer bolt` — the real spell taught by the
Tome of Old Prayers (8 damage, 6 mana).

## What can't be playtested through real game content yet

Companions, Spells, and status-effect items all have their full engine
built and unit-tested, and are now genuinely reachable in a live `main()`
run through dev tooling (see the recipes above and below), and all three
now exist as real content too, Spells only partly:

- **Companions.** One real companion exists now: the Shade of Achilles, in
  Shadow of Army Camp (floor 5), recruited by beating him in a duel. He's the
  only one, and no `Reviver` is real content yet, so reviving a downed
  companion still needs `dismiss` (which restores them) or a dev-added item.
  `test companion` remains useful as a companion with no duel, no
  `required_items`, and all three AI actions live.
- **Spells.** One real spell exists now: Prayer Bolt, taught by the Tome of
  Old Prayers, which drops from the Fanatic in Prayer Room (floor 3) - no
  workaround needed. It's the only real one, though: `test bolt`/`test
  spellbook` remain the only way to reach a spell with a status-effect
  component. Mana/`rest`/`wait` work fine on their own regardless.
- **Status-effect items.** Both kinds are real content now: the Vial of
  Grave Rot (a 3-turn poison) drops from the Crypt Keeper in Bony Crypt
  (floor 3), and the Wineskin of Dionysus (a 3-turn Regen) drops from the
  Satyr in Mossy Grove (floor 4) - neither needs a workaround. `test
  healing tonic`/`test venom vial` are now just dev-only duplicates of the
  two real items' effects. `dev afflict` (above) remains the more direct
  way to test status-effect ticking without needing any item.

More real content of each kind is expected as part of "Populate all
floors" (`roadmap.md`).

- **Ranged attacks are reachable now.** The Harpy-fletched Bow (`slot="ranged"`,
  4 damage) drops from the Harpy in Cave of Harpies (floor 3), or `dev add
  harpy-fletched bow` skips the trip. Equip it with `use`, then `attack
  ranged` works. It's the only ranged weapon, and there's no `create_test_*()`
  one.

Everything else that's landed recently — the helmet/body/shield armour
slots, weapon classes (blade, two-handed heavy, piercing, ranged), armour
weight and the miss chances it adds, doors that stay open once opened,
durability degrading in combat, repairing at the Forge of Prometheus (floor
2, `is_forge=True`), Dodge, light/heavy attacks, the Practice Chamber's
respawning dummy, every floor 1/3/4 enemy (Shade, Crypt Keeper, Harpy,
Fanatic, Lurker, Petrified Guardian, Satyr, Lamia, Ember Wraith, Talos,
Medusa), Hermes'/Athena's/Ares' now-completable trades, reloading from
your last save on death instead of the game always just ending, guarded
exits (the Minotaur, Talos, the Centaur and the Medusa chain each bar the
way forward until defeated), and the minimum-damage rule (every landed hit
deals at least 1) — has real, reachable in-game content and needs no
dev-tool workaround to try. The
Weathered Helm (Shade's drop, Fields of Asphodel) is also content's first
real `slot="helmet"` item, Lamia is the first enemy with
`Character.has_lifesteal`, and her Fang is the first lifesteal weapon - see `CLAUDE.md`'s "Armour slots and durability"
and "Canonical attribute names." Only Prometheus' trade is still unwritten
content (no required items or reward, so `trade` just replies "Prometheus
has nothing to trade." and never completes) - see roadmap.md's "Populate all
floors." Athena, Ares, and Hermes all have real dialogue now, including a
line for after their trade (`Ally.hint_traded`).

Two more small things from the same playtesting pass: moving into a new
room restores 1 HP while you're below three-quarters of max HP (`"You
catch your breath as you move on."` - capped by a later balance pass, so
pacing can't heal you to full), and there are three new `forge` shortcut exits straight
back to the Forge of Prometheus from Prayer Room (floor 3), Stony Lair, and
Maze of Pillars (floor 4) - no dev command needed for either, both are
reachable through normal play. The Forge also has three reciprocal exits
back out to those same rooms (`prayer room`/`stony lair`/`maze of pillars`),
each locked until you've used the one-way `forge` exit from that room at
least once - see the recipe below, and `CLAUDE.md`'s "Fast-travel locks"
for how the enforcement works.

A few newer player commands are also all real, non-dev, and reachable with
no workaround: `take all`/`take all from <ally>`, `equip <item>`, `toggle
auto map`, and `uncleared`. One dev-relevant quirk when testing `uncleared`:
it works from `Player.visited_rooms` (plus each visited room's open
neighbours, reported as "undiscovered"), which is updated by normal movement
(and the starting room) but **not** by `dev teleport` - a room you only ever
teleported into never shows up in the report, and neither do its
neighbours. Walk into it (or out and back in) to register it. Level-ups now also raise max HP by
`HP_PER_LEVEL` (2), so `dev set level` is not the same as a real level-up
(it only changes the number). `dev set experience` is a plain write too -
nothing levels until the next real XP gain - so to trigger a genuine
`level_up()`, set experience just below the threshold, then `dev spawn
shade` and `dev kill` it (a dev kill grants the enemy's real XP).

**One-off hints only ever show once per save.** `Player.seen_hints` is
saved like any other field, so once you've seen e.g. the combat or forge
hint in a save, it won't appear again there - even after a reload. There's
no dev command to reset it (`dev set` only writes whole numbers, not sets),
so to see a hint again, start a fresh New Game. The full hint text and
every trigger are in `hints.py` and `CLAUDE.md`'s "One-off contextual
hints".

## The Practice Chamber isn't a dev tool
Unlike everything else in this file, the Practice Chamber (floor 2, next to
the Forge of Prometheus) and its `dummy set <stat> <value>` command are
**real, player-facing content** — reachable by walking there normally, and
working with `player.dev_mode` off. It's listed in `get_controls_text()`/the
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

**Try weapon classes - cleave, and the two-handed/shield swap:**
```
dev add labrys
dev add chipped stone aegis
use chipped stone aegis
use labrys
stats
dev spawn gorgon
dev spawn gorgon
attack heavy
```
Equipping the Labrys unequips the Aegis (a two-handed weapon and a shield
push each other off), and `stats` shows the miss chances before and after.
A landed `attack heavy` cleaves into the second Gorgon for half the swing.
`use chipped stone aegis` again unequips the Labrys.

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

**Duel the Shade of Achilles, then recruit him:**
```
dev teleport shadow of army camp
talk
challenge shade of achilles
attack
```
Losing is safe - the duel ends, your HP is restored, and you can
`challenge` again. `dev set atk 999` before `attack` wins it in one hit; the
win grants a skill point, and then `recruit shade of achilles` works. To test
companion levelling, recruit him and `dev kill` a few enemies - he gains the
same XP you do.

**Try a multi-stage boss fight (wave, then phase transition):**
```
dev spawn test boss
attack
attack
attack
attack
```
Every enemy in this chain has 1 hp, so a single hit kills each one. The first
`attack` kills Test Boss and spawns two Test Adds (the wave) - `current_target`
auto-updates to the first one. The second `attack` kills that add; since its
sibling is still alive, nothing else happens yet. The third `attack` kills the
last add, triggering the deferred transition to Test Boss (Phase 2). The
fourth `attack` kills Phase 2 for good, ending combat with its own gold/XP
reward. Same chain, real stats and lore: `dev spawn medusa` (or just walk to
the Lair of Medusa, floor 4) for the genuine fight - Medusa (Phase 1) falls
to a wave of two Gorgons, then Medusa (Awakened) appears once both are dead.

**Try the forge shortcut and its fast-travel lock:**
```
dev teleport forge of prometheus
prayer room
dev teleport prayer room
forge
prayer room
```
The first `prayer room` fails - `"You haven't opened this shortcut yet -
reach it from the other side first."` - since the Forge's reciprocal exit
starts locked (`Room.fast_travel_locks`). `dev teleport prayer room` then
`forge` moves you from Prayer Room straight to the Forge - real content, no
dev command needed for that part - and prints `"The path back opens behind
you."`, unlocking the reciprocal exit (`Room.exit_activations`). The final
`prayer room` now succeeds. Stony Lair and Maze of Pillars (floor 4) work
the same way.

**Try a guarded exit:**
```
dev teleport labyrinth of the minotaur
south
dev clear room
south
```
The first `south` fails - `"Minotaur bars the way - you'll have to deal with it
first."` - since the Labyrinth's `south` exit is guarded (`Room.guarded_exits`)
while he lives. `west`/`east`/`ascend` stay open throughout. `dev clear room`
empties the room with no loot; use `dev kill` instead if you want his Labrys
drop and XP. Either way, the second `south` walks straight into Mossy Grove.
Maze of Pillars (`south`, Talos), Overgrown Forest (`descend`, the Centaur) and
Lair of Medusa (`descend`, the whole Medusa chain) work the same way.

**Try a ranged attack:**
```
dev add harpy-fletched bow
use harpy-fletched bow
dev spawn skeleton warrior
attack ranged
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
