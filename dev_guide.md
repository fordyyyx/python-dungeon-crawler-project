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
- `dev spawn companion <name>` — spawns only from the companion registry, with
  the current room as the companion's home. Use it for a companion whose name
  an enemy also has (`shade of achilles`, `hades`), since plain `dev spawn`
  finds the enemy first.
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
  - It can't set a miss chance, so it **can't make Blinded** - `dev afflict
    skeleton warrior blinded 0 2` just applies a silent effect that does
    nothing. Use the Olive-wood Stake recipe below instead.

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
  arrival. The room you leave resets its per-visit state (`Room.on_leave()`),
  exactly as walking out does.
- `dev flag <name>` — sets a story flag (`Player.story_flags`), e.g. `dev flag
  suitors_cleared` to make Odysseus recruitable without fighting the Suitors.
  Emptying a room with `dev kill`, `dev remove`, `dev remove all` or `dev
  clear room` sets that room's own cleared flag too, just like a real clear.
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
`bronze breastplate`, `small healing potion`, `cyclops' eye`, `spear of ares`,
`centaur's broken bow`, `skeleton bone`, `breastplate of athena`, `favour of
hermes`, `weathered helm`, `vial of grave rot`, `harpy-fletched bow`, `tome of
old prayers`, `chipped stone aegis`, `wineskin of dionysus`, `lamia's fang`,
`sun-scorched dagger`, `talos' bronze plating`, `serpent's kiss`, `labrys`, `hector's helm`,
`tower shield of ajax`, `field dressing`, `bow of paris`, `cup of kykeon`,
`laestrygonian hide`, `antiphates' club`, `olive-wood stake`, `wheel of cheese`,
`boar's-tusk helm`, `hoplon of the drowned`, `trident of the depths`,
`kelp poultice`, `antinous' goblet`, `penelope's thread`, `pomegranate`, `hide of cerberus`,
`bident of hades`, `heart of typhon` (a `Trophy`), `ledger of the unjudged` and `daedalus' notes`
(both `IntellectReward`s), `clockwork crossbow`, `feather of icarus` (an `EscapeItem`),
`spear of pelion`, `nymphs' honey`, `test spellbook`, `test healing tonic`, `test venom vial`.

**Enemies** (`dev spawn <name>`): `training dummy`, `skeleton warrior`,
`minotaur`, `hades`, `centaur`, `cyclops`, `shade`, `crypt keeper`, `harpy`,
`fanatic`, `lurker`, `petrified guardian`, `satyr`, `lamia`, `ember wraith`,
`talos`, `medusa`, `gorgon`, `medusa (awakened)`, `practice enemy` (the
Practice Chamber's respawning dummy), `shade of hector`, `shade of ajax`,
`myrmidon soldier`, `shade of paris`, `laestrygonian`, `antiphates`, `polyphemus`,
`polyphemus (blinded)`, `head of scylla`, `poseidon`, `hippocampus`,
`poseidon (earth-shaker)`, `suitor`, `antinous`, `eurymachus`, `cerberus`, `cerberus (two heads)`,
`cerberus (last head)`, `restless shade`, `hades (helm of darkness)`, `typhon`, `serpent of typhon`,
`typhon (storm unleashed)` (`hades` and `typhon` are the
first phases, with their waves and final phases attached), `shade of achilles` (his *duel
form*, unlinked - a real, lethal fight with no HP restore; use `dev spawn companion`
for the companion), `charybdis` (invulnerable - she can
only be "beaten" by `dev kill` or the Narrow River puzzle), `test boss` — a dev-only,
two-phase boss (hp 1 throughout) whose first phase is gated behind a
two-add wave, exercising `next_wave_factories`/`wave_gate_factory`/
`next_phase_factory` end-to-end. `medusa`/`gorgon`/`medusa (awakened)` are
the real equivalent now (floor 4, Lair of Medusa) - `test boss` stays
useful for isolated testing without a full room/fight.

**Allies** (`dev spawn <name>`): `chiron`, `mentor`, `wounded soldier`,
`charon`, `athena`, `ares`, `hermes`, `prometheus`, `nestor`, `circe` (a merchant -
see the exchange recipe below), `penelope`, `oracle`, `tiresias`, `persephone`, `icarus`. A spawned
`oracle` or `tiresias` is the *unwired* version - the Oracle's questions are room
interactions of the Chamber of the Oracle, and Tiresias' readings are attached by
`build_world()` - so spawned, Tiresias only has a placeholder line. Teleport to the
real floor 7 rooms to test them (see the recipe below).

**Companions** (`dev spawn companion <name>`): `shade of achilles` — the real floor 5
companion, spawned still needing his duel (`challenge shade of achilles`
before `recruit`) - plain `dev spawn shade of achilles` gives his duel form instead.
`odysseus`, and `hades` - the spared Hades, recruitable straight away (plain `dev
spawn hades` gives the boss).
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

- **Companions.** Two real companions exist now: the Shade of Achilles, in
  Shadow of Army Camp (floor 5), recruited by beating him in a duel, and
  Odysseus, in Shadow of Ithaca (floor 6), who joins once the Suitors in the
  Throne Room are cleared (the `suitors_cleared` story flag) - real content,
  no workaround needed. Penelope's Thread (Bedchamber, beyond the Suitors) is
  the one real `LoyaltyToken`. No `Reviver` is real content yet, so reviving a downed
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
  Satyr in Mossy Grove (floor 4), with a stronger Regen, the Cup of Kykeon,
  given by Nestor in Shadow of Pylos (floor 5) - none needs a workaround. `test
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
exits (the Minotaur, Talos, the Centaur, the Medusa chain, and floor 5's Hector, Ajax and Paris each bar the
way forward until defeated), and the minimum-damage rule (every landed hit
deals at least 1) — has real, reachable in-game content and needs no
dev-tool workaround to try. The
Weathered Helm (Shade's drop, Fields of Asphodel) is also content's first
real `slot="helmet"` item, Lamia is the first enemy with
`Character.has_lifesteal`, and her Fang is the first lifesteal weapon - see `CLAUDE.md`'s "Armour slots and durability"
and "Canonical attribute names." Prometheus has no trade (`trade` just replies
"Prometheus has nothing to trade.") - his role is the one-time hardcore offer
instead (see the recipe below). Athena, Ares, and Hermes all have real dialogue now, including a
line for after their trade (`Ally.hint_traded`).

Floor 6 is all real content too, with no workaround needed: the
giants in Bright Cave, the Sirens' bargain in Calm Waters (the first room
interaction), Polyphemus and his blinded second phase in the Cavern of
Polyphemus (the Olive-wood Stake he drops is the only real source of
Blinded), the six Heads of Scylla in Rocky Shore, and Charybdis' puzzle in
Narrow River - each route guards its way into Poseidon's Depths - then
Poseidon, Odysseus, Circe, the Suitors and Penelope. Floor 7's Oracle,
Tiresias and Persephone (and her Pomegranate) are real content as well.

The hidden rooms are real content too, each found with `examine` and none needing a
workaround: the Banks of the Lethe (south of Fields of Asphodel, floor 1 - forget
every skill for gold), the Ossuary (below the Bony Crypt, floor 3 - the Ledger of
the Unjudged), Daedalus' Workshop and Icarus' Shaft (east of the Maze of Pillars,
floor 4, intellect 5 - the Clockwork Crossbow, Daedalus' Notes, and Icarus with the
Feather of Icarus, the only escape item), the Belly of the Wooden Horse (inside the
Shadow of Army Camp, floor 5 - the Spear of Pelion) and the Cave of the Nymphs (west
of Shadow of Ithaca, floor 6, intellect 6 - Nymphs' Honey and 200 gold). The
intellect gates are real too: with a low-intellect ancestry, the Ledger and the
Notes are what get you there.

Floor 8 is real content too: Cerberus, Hades (spared if you promised
Persephone mercy - he then joins as a companion - or killed if you refused), and
the ending, which opens Tartarus - and floor 9's Typhon and the true ending are
real content too. The one thing a trophy can't do yet is anything: the Heart of
Typhon is a `Trophy`, but the Trophy Room of Zeus it's meant for isn't built.

Two more small things from the same playtesting pass: moving into a new
room restores 1 HP while you're below three-quarters of max HP (`"You
catch your breath as you move on."` - capped by a later balance pass, so
pacing can't heal you to full), and there are eight `forge` shortcut exits straight
back to the Forge of Prometheus from Prayer Room (floor 3), Stony Lair, Maze
of Pillars (floor 4), Shadow of Pylos (floor 5), Shadow of Ithaca (floor 6),
Bedchamber of Persephone (floor 7), Gate of Cerberus (floor 8) and Tartarus
(floor 9) - no dev command needed for either, both are
reachable through normal play. The Forge also has eight reciprocal exits
back out to those same rooms (`prayer room`/`stony lair`/`maze of pillars`/
`shadow of pylos`/`shadow of ithaca`/`bedchamber of persephone`/`gate of
cerberus`/`tartarus` - the last one hidden until Hades falls),
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

**Try an evasive enemy (melee dodge and natural pierce):**
```
dev spawn shade of paris
attack light
dev add bow of paris
equip bow of paris
attack ranged
```
Light and heavy attacks miss Paris about half the time (`"Shade of Paris stays just out of reach!"`); ranged attacks and spells never
do. His arrows ignore 8 of your armour. The first room entry with him present also shows the one-off `"evasive"` hint - spawning him
doesn't, since the hint fires from `print_room()`; use `dev teleport shadow of troy (south)` to see it.

**See an ancestry line:**
```
(name: developer mode, primary ancestry: athena)
floor_2
talk
talk
```
The first `talk` opens with Athena's line for her own descendants; the second doesn't repeat it. Lines match the primary *or* secondary
pick, so an ancestry chosen as the secondary gift works too. Enemy lines fire on sight instead - pick `minotaur`, then `dev teleport
labyrinth of the minotaur`. For a rival line, recruit the Shade of Achilles (below), then walk `south` into Shadow of Troy (North).

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
`prayer room` now succeeds. Stony Lair, Maze of Pillars (floor 4), Shadow of
Pylos (floor 5) and Shadow of Ithaca (floor 6) work the same way.

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
Maze of Pillars (`south`, Talos), Overgrown Forest (`descend`, the Centaur),
Lair of Medusa (`descend`, the whole Medusa chain), floor 5's Hector, Ajax and
Paris, and Rocky Shore (`south`, all six Heads of Scylla) work the same way.

**Try blinding an enemy (the Olive-wood Stake):**
```
dev add olive-wood stake
equip olive-wood stake
dev spawn skeleton warrior
attack
attack
```
Each hit that doesn't kill has a 20% chance to blind (`"Skeleton Warrior is
afflicted with Blinded."`). A blinded enemy has a 30% miss chance for its next
two attacks - counted per attack, so a turn it spends bracing doesn't use any
up - then `"... is no longer blinded."`. For a guaranteed blinded enemy, `dev
spawn polyphemus (blinded)`: he starts at a 35% miss chance for the whole fight.

**Try a room interaction (the Sirens' bargain):**
```
dev teleport calm waters
listen
give in
listen
```
Entering shows `(You could: listen, give in, resist)` and, the first time, the
`"room_interactions"` hint. `listen` changes nothing; `give in` grants 2 skill
points for 5 max HP, permanently; after that every verb answers `"The Sirens
are silent now."`, even after a save and reload (`Room.flags`). Interactions
only work outside combat.

**Solve Charybdis' puzzle:**
```
dev teleport narrow river
attack
climb
watch
watch
let go
row
```
`attack` is refused - Charybdis is invulnerable. The five verbs are the
solution; after each, the whirlpool moves on a phase (still, swallowing,
drained, spewing). Solving drops the Hoplon of the Drowned and opens `west`.
Try a wrong move instead (e.g. `watch` straight away, then anything but `climb`
while she swallows) to see the 12-damage failure and restart. Leaving the room
- including by `dev teleport` - resets a half-finished attempt
(`Room.on_leave()`). `dev kill` skips the puzzle and still gives her rewards.

**Recruit Odysseus and ask his advice:**
```
dev teleport shadow of ithaca
recruit odysseus
dev flag suitors_cleared
recruit odysseus
dev teleport shadow of troy (south)
advice
```
The first `recruit` is refused (`"Not while those men are still in my hall..."`).
With the flag set he joins. `advice` in Paris' room points at a bow or a spell;
in Narrow River or Calm Waters he adds the room's own line. His attacks are
ranged, so Paris can't dodge them.

**Exchange with a merchant (Circe):**
```
dev teleport muddy pigsty
offers
dev add bronze xiphos
dev set gold 30
exchange 1
```
`offers` lists her six exchanges with your gold. `exchange 1` takes the Bronze
Xiphos and 20 gold for a Kelp Poultice. Equip the Xiphos first to see the
"unequip it first" refusal; drop to under 20 gold to see the price refusal -
neither changes anything. Offers never run out.

**Try a loyalty token (Penelope's Thread):**
```
dev spawn test companion
recruit test companion
dev add penelope's thread
dev spawn minotaur
attack
```
Holding the Thread readies the companion's loyalty before the fight. The
first hit that would down them leaves them on 1 HP instead (`"... should have
fallen - but stays standing."`); a second one downs them normally. It re-arms
after the fight ends. For the real route, clear the Throne Room (`dev clear
room` sets `suitors_cleared` too), walk `west`, and `take penelope's thread
from penelope`.

**Talk to floor 7's seers, and hold a branching conversation:**
Start a dev game on `floor_5` (the starting-floor prompt), so the deepest
floor reached is 5 and the Oracle has floor 6 to foretell - `dev teleport`
never adds to `visited_floors`, only walking does.
```
dev teleport chamber of the oracle
talk
ask ahead
ask ahead
ask secrets
dev teleport shadow of thebes
talk
dev teleport bedchamber of persephone
talk
say 2
say 1
talk
```
The first `talk` opens with the twist prophecy (once only). `ask ahead` lists
floor 6's traits and "(2 prophecies remain.)"; asking again isn't spent. `ask
secrets` only finds something on floors you've reached - `dev teleport` never adds
to them - so from a `floor_5` start it names the Shadow of Army Camp (the wooden
horse); start on `floor_1` for Styx Crossing then Fields of Asphodel, or `floor_2` for
the Armoury of Ares (with a low-intellect warning). Tiresias'
reading changes with your kit: try it with and without a bow, a healing item or
`dev spawn test companion` + `recruit test companion`. Persephone gives the
Pomegranate, `say 2` asks her request, `say 1` promises (`promised_mercy`), and the
last `talk` no longer offers it. Try `descend` before answering: it's story-gated
(`map` shows "Persephone is waiting for your answer", `uncleared` "a decision to
make") - either answer opens it, "think about it" doesn't, and `dev flag
promised_mercy` skips the conversation. Walking out mid-conversation ends it - `say 1`
afterwards says you're not in one.

**Spare (or kill) Hades, see the ending, and open the way to Tartarus:**
```
dev flag promised_mercy
dev teleport hall of hades
map
dev kill
dev kill
dev kill
dev kill
dev kill
2
recruit hades
map
descend
```
Before the fight, `map` doesn't list `descend` - Tartarus is concealed. Five
`dev kill`s take Hades, his three Restless Shades and the Helm of Darkness. With
`promised_mercy` he yields - his reveal plays and he's left in the Hall as a
companion (`recruit hades`); without it (or with `dev flag refused_mercy`) he dies
with the other reveal. Either way the ending follows at once, autosaves, and asks:
`2` keeps playing, `1` goes back to the title screen. Then `descend` reaches
Tartarus. `dev clear room` in the Hall is a shortcut to the ending (no reveal, no
yield). `dev flag hades_defeated` alone shows the ending *and* the stair, but Hades
still guards it until he's dealt with.

**Fight Cerberus:**
```
dev teleport gate of cerberus
attack
```
Three phases in a row; the last head's bite can poison (the Aconite Fangs). Its
defeat restores you and your companion to full and drops the Hide of Cerberus,
and only then does `south` open.

**Fight Typhon, and see the true ending:**
```
dev flag hades_defeated
2
dev teleport tartarus
dev kill
dev kill
dev kill
dev kill
dev kill
dev kill
2
take heart of typhon
```
`dev flag hades_defeated` plays the story ending first (answer `2` to keep
going). Six `dev kill`s take Typhon, his four Serpents and Typhon (Storm
Unleashed); the true ending follows at once, autosaves and asks the same
question. `dev flag hades_spared` first gives the version with Hades. To feel the
fight properly, `attack` instead - the Serpents poison and Storm Unleashed can
blind you.

**Try hardcore mode:**
```
dev teleport forge of prometheus
talk
say 1
say 1
save
save 1 2
dev set hp 0
```
The first `talk` makes the offer (once - talk again and he refers back to your
answer). `say 1` twice accepts, repairing all your armour. `save 1 2` is refused -
a hardcore run can only save to its own slot. Dying then skips the reload prompt
and deletes the save; the title screen's slot list no longer shows it. `dev flag
hardcore` switches it on without Prometheus, and a hardcore save shows
"(Hardcore)" in the slot list. To see the offer again, start a New Game - a used-up
offer is saved (`prometheus_offer_made`).

**Forget your skills at the Banks of the Lethe:**
```
dev teleport fields of asphodel
dev kill
examine
south
dev set skillpoints 2
learn attack
learn defence
drink
dev set gold 50
drink deeply
skills
```
`examine` reveals `south` (the hint is the river you can hear). `drink` names the
price and changes nothing; `drink deeply` refuses without charging if you have
nothing learned or too little gold. The price is 25 gold per floor of the deepest
floor reached - from a `floor_0` start that's the 25 minimum; start on a deeper floor
(or walk down) to see it rise. Afterwards `skills` shows every path back at nothing,
with the points refunded, and `stats` shows the bonuses gone.

**Find a hidden room behind an intellect gate (Daedalus' Workshop):**
```
dev teleport maze of pillars
dev kill
examine
dev set intellect 5
examine
east
up
take feather of icarus from icarus
```
The first `examine` (below 5 intellect) only says there's something you can't make
sense of; at 5 it reveals `east`. `use ledger of the unjudged` (`dev add` it, or find
it in the Ossuary below the Bony Crypt) is the real-play way to the extra intellect. The
Cave of the Nymphs works the same way (`dev teleport shadow of ithaca`, intellect 6,
`west`, then `gather the gifts` - once only).

**Escape a fight with the Feather of Icarus:**
```
dev add feather of icarus
use feather of icarus
dev spawn minotaur
attack
use feather of icarus
look
```
The first `use` is refused - there's nothing to escape from - and the Feather stays in
your inventory. Mid-combat it gets you out with no parting blow, however healthy the
enemy, and is used up; the Minotaur is still there afterwards, so a guarded exit stays
guarded. Using it mid-duel ends the duel without a win, like `flee`.

**Check that a damaged save is handled, not a crash:**
Save a game normally, quit, then open `saves/profile_1/slot_1.json` in any
editor and break it (delete the last few characters, or replace a number
with `true`). On the title screen, Load Game lists the slot as `Damaged save -
can't be loaded.`, and picking it prints the "can't be read" message and
returns to the menu. Mid-game `load 1 1` does the same and leaves the current
game running; Delete Save still removes it. (`SaveFileError` - see
`CLAUDE.md`'s "Custom exceptions".)

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
