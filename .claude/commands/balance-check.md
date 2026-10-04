Read CLAUDE.md for project context, then run a full difficulty/balance audit of
the game as it currently stands. This is a read-only analysis pass — do NOT
modify any file under src/ or tests/. The goal is a set of concrete,
numbered suggestions the user can choose to apply themselves, not an
automatic fix.

Verify every claim against the actual code (grep/read the real files), never
against what roadmap.md/CLAUDE.md/map.md already say, since those can
themselves be stale — and since this command file's own words will go stale
the moment content changes, don't trust anything here beyond the
instructions themselves; rebuild every number from the current code on every
run.

## Context to establish first

- **The game has difficulty settings** (`difficulty.py`'s `DIFFICULTIES` —
  read it on this run for the settings that exist, what each multiplies, and
  how each changes passive regeneration). **Normal is the baseline**: every
  number written in the content files (enemy hp/attack/armour, loot, XP/gold
  rewards, player starting stats) is Normal's tuning, and every other setting
  is only a multiplier away from it, not a separate tuning pass. So:
  - **Phases 1-4 measure Normal**, and frame every suggestion there around:
    **Normal should read as a standard "medium" difficulty** — beatable by a
    reasonably careful player without grinding, capable of real player
    deaths on a careless one.
  - **Phase 5 measures every other setting** against what that setting is
    meant to be.
  - A problem that shows up on every setting is a baseline problem: suggest
    a change to the enemy or item itself. A problem on one setting only is
    that setting's problem: suggest a change to its multipliers or its
    regeneration, never to an enemy's own stats.
- Build the player's expected power curve directly from the real code, not
  from memory or from this file:
  - `content/ancestries.py`'s `ANCESTRIES` for starting `attack`/`armour`/
    `hp`/`intellect` per ancestry (use `"basic"` as the reference case
    unless the user asks for a specific one).
  - `characters.py`'s `level_up()`/`gain_experience()` for the XP curve, and
    each `Skill` subclass (`AttackBoostSkill`, `DefenceBoostSkill`,
    `DoubleStrikeSkill`, `LastStandSkill`, `ThornsSkill`, `DodgeSkill`) for
    what a spent skill point is actually worth.
  - `combat.py`'s attack/damage formulas (`Character.attack()`,
    `take_damage()`) for how attack/armour/weapon damage actually convert
    into damage dealt and taken — don't assume a naive subtraction if the
    real formula does more (heavy multiplier, flat reductions, dodge,
    durability, lifesteal, etc).
  - Weapons/armour actually reachable on the critical path per floor (walk
    each `build_floor_N()` and note what a player passing straight through
    would pick up and could plausibly have equipped by that point).
  - **A linear, no-grinding playthrough is the baseline assumption**: the
    player fights every enemy actually placed in a room they pass through on
    the critical path (not extra respawns or optional detours), completes
    reachable trades, and spends skill points as earned. Note explicitly
    when a room/encounter is optional (off the critical path) rather than
    folding it into the baseline curve.

## Phase 1 — Per-encounter difficulty pass

For every floor 0-9 (note explicitly if a floor is still an unpopulated
shell — don't skip it, just say so and move on), and every enemy actually
placed via `add_enemy()` in that floor's `build_floor_N()`:

- Compute, using the real formulas, roughly how many player turns it takes
  to defeat the enemy at that point's expected player stats/gear, and
  roughly how many enemy turns it takes to defeat the player back,
  accounting for the enemy's own `attack_damage`/`armour` and the player's
  expected `hp`/`armour`/dodge at that point.
- For a multi-stage enemy (`next_phase_factory`/`next_wave_factories`),
  total the effective HP/toughness across every phase and every spawned
  add, not just the first phase's own `hp` — that's the fight's real
  length.
- Weigh in anything that meaningfully skews the fight beyond raw stats:
  `has_lifesteal` (sustain), `has_petrifying_gaze`/other special abilities,
  high `aggression_weight`/`heal_amount` (a more "optimal" AI), `respawns`
  (excluded from lethality concerns — it's meant to be freely farmable).
- Flag anything that reads as clearly too easy (near-zero risk, one or two
  hits) or clearly too hard (the enemy could plausibly kill the player
  before the player kills it) for where it sits in the progression —
  especially on early floors, where a "too hard" read is a much bigger
  problem than later on.
- Note floor-to-floor *and* room-to-room escalation: does difficulty climb
  roughly smoothly, or are there sudden spikes/dips relative to
  neighbouring encounters (including within a single floor, not just
  across floors)?
- Sanity-check `experience_reward`/`gold_reward` against how dangerous/tough
  the enemy actually is — flag anything wildly over- or under-paying for
  its difficulty.

## Phase 2 — Forced-path / softlock audit

Across every floor, trace every `Room.locked_exits` (item-gated) and
`Room.hidden_exits`/`required_intellect` gate, and every `Ally.
required_items` trade, back to its source(s):

- **Single point of failure**: does the required item/trade have exactly
  one source in the whole game (one enemy drop, one trade reward, one room
  pickup), with the gate it unlocks being the only way to reach something
  the player still needs (a whole floor, a required trade, etc.)? Flag it.
- **Missable/consumable gating items**: is the required item a `QuestItem`
  (safe — can't be dropped) or a plain droppable/usable item that could be
  dropped, traded away, or otherwise lost/consumed before it's used? A
  progress-gating requirement resting on a non-`QuestItem` is a real risk —
  flag it even if no concrete path to actually losing it is obvious yet.
- **Stat-gated progress with a single source**: does any encounter or gate
  effectively require the player to already have a minimum `hp`/`attack`/
  `armour` (to survive it, or to hit hard enough to clear it in reasonable
  time) that's only reachable via one specific item/trade/drop, with no
  alternative gear, ally/companion help, consumable, or strategy that gets
  a player to comparable power another way? Flag it, and name the single
  source.
- **One-way/dead-end routing**: for every `connect()` call, check whether an
  exit that moves the player forward (e.g. `descend`) has a real way back
  (`ascend` or equivalent) where the room design implies one should exist,
  and whether any hidden/locked exit reveal could leave a player stranded
  away from content they still need with no way back to get it.
- For each finding, state plainly: what's gated, on what, where the single
  source is, and what happens to a player who reaches the gate without it.

## Phase 3 — Optional simulated spot-check

For any Phase 1 finding you're genuinely unsure about from the static maths
alone (a close call, not a clear-cut "too easy"/"too hard"), you may run a
disposable simulation to check it empirically: script N (e.g. 200-500)
randomised mock fights using the real `create_*()`/combat functions at the
encounter's expected player stats, and report win rate / average player HP
remaining / average turn count. This script is scratch-only — run it
in-memory (e.g. `python -c`) or from the scratchpad directory, never saved
into `src/`, `tests/`, or anywhere in the repo. Use this to confirm or walk
back a static-math flag, not to replace Phase 1 for every encounter — it's a
spot-check for the borderline cases, not a full pass.

## Phase 4 — Gold economy measurement

Measure the gold economy as it stands, as the baseline for pricing (Charon's
shop, and every provisional price already in the game). This phase measures
and reports only — like the rest of this command, it changes no game code
or numbers.

Simulate two player types through floors 0-9, each across a few builds
(e.g. attack-led, defence-led, balanced), using the real content and combat
functions as in Phase 3:

- **A careful player** — clears every room, optional and hidden ones
  included, and paces their fights (walks to the regen cap before each one).
- **A rushing explorer** — fights only what gates the way forward, and skips
  optional rooms.

At the end of each floor, report for each player type:

- **Gold earned so far**, split into enemy gold, treasure (room rewards such
  as the Cave of the Nymphs), and sales — assume they sell everything they
  don't use or wear. Use the real sell rule if one exists in the code (read
  it, don't assume it); if selling isn't built, say so, state the rule you
  assumed, and keep sales as a clearly separate column.
- **Gold spent so far on Forge repairs**, and how many armour points that
  repaired (from the real repair cost in `exploration.py`, repairing
  whenever a forge or forge shortcut is reachable).
- **Gold held** after those repairs.
- **Healing items used on that floor**, and healing items still held.

Also report, from the current code:

- **Every gold sink's price against income** — the Lethe's cost at each
  floor as a fraction of that floor's income, and likewise any other
  price that scales.
- **Every merchant offer's cost** (Circe's, and Charon's once he has stock),
  and the first point at which each player type has enough gold for it.
- **Every one-off gold reward** (the Cave of the Nymphs' gold, any chest) —
  when it arrives, and what fraction of the gold held at that point it is.

Summarise with one table per player type (a row per floor), and **flag any
floor a player ends holding less than one floor's typical repair cost** -
that's the point where armour starts staying broken.

The names above are examples of what exists today. Find the sinks, offers
and rewards by reading the code on this run, so anything added since is
measured too and anything removed isn't reported from memory.

## Phase 5 — Difficulty settings

Measure every setting in `DIFFICULTIES` other than Normal, which Phases 1-4
already covered. Take the settings, their multipliers and their regeneration
rules from the code on this run — if a setting has been added, removed or
retuned, measure what's there.

**Scale the world the way the game does.** Use the real scaling functions
(`scale_world()`/`scale_for()`, or whatever the code now calls them) rather
than multiplying stats by hand, so every enemy the simulation fights —
including wave adds and later boss phases, which are created mid-fight —
goes through the same route it does in play. If any enemy turns up
unscaled, that's a correctness bug: report it under bugs, not as balance.
Apply the setting's own regeneration (its cap, and how much a move
restores) wherever the simulated player paces between fights, and anything
else the setting scales (today, Charybdis' puzzle damage).

**Run the same simulated players as Phase 4** on each setting — the careful
player and the rushing explorer, across the same builds — plus a careless
full-clearer (clears everything, but doesn't pace and drinks late). For each
setting, report:

- **Survival** for each player type and build, and where the deaths happen.
- **The lowest HP reached** in each gating fight and each boss, as a
  fraction of max HP, beside Normal's figure for the same fight.
- **Healing items used, and still held at the end**, and **gold spent on
  repairs** — gold and loot are the same on every setting, so these two are
  where a setting shows up in the economy. Don't repeat Phase 4's full gold
  tables; report only what differs from Normal.
- **How much of the setting's effect is the stat multipliers and how much is
  regeneration** — rerun one build with Normal's regeneration to separate
  them, so a suggestion can name the right lever.

**Judge each setting against its own description** (`Difficulty.description`
and the module's docstring — read them, don't assume the wording):

- The easiest setting should let a careless player finish; if a careful one
  never drops below most of their HP, say so, but that's what it's for.
- A setting between the easiest and Normal should be clearly more forgiving
  than Normal for every player type while still being able to kill a
  careless one.
- The hardest setting should punish carelessness hard and take a careful
  player close in the boss fights, without making any single fight a coin
  flip for a careful player — flag any gating fight a careful player loses
  more than about one time in ten.
- The settings should be **ordered, with real gaps between them**: flag two
  neighbouring settings that play almost the same, and any fight that is
  *easier* on a harder setting (rounding of scaled stats can do this).

Check these specifically:

- **The gap between explorers and rushers** on each setting. Easier settings
  are meant to help players who don't explore, through enemy stats and
  regeneration, since gear upgrades only reach players who do. Report whether
  the rusher's survival actually improves on the easier settings, and by how
  much compared with the careful player's.
- **The skill gate** (today the Minotaur, meant to stop a player who has
  invested no skill points). Report whether it still holds on each setting.
  Whether it *should* hold on the easiest one is the user's decision — state
  what happens and ask, rather than calling it a fault.
- **Rounding and floors.** Low stats scale coarsely: list any enemy whose
  scaled attack rounds to the same value on two settings, or to 0, and any
  fight where the scaled attack falls to or below the player's expected
  armour, so every hit lands only the minimum damage and the multiplier does
  nothing.
- **Hardcore.** It raises a run to the hardest setting part-way through
  (read `floor_2.py` for when and how), and one death ends the run. Report
  the chance a careful and a careless player finish a hardcore run — the
  earlier floors on Normal, the rest on the hardest setting — since that's
  the number a hardcore achievement would rest on.
- **New Game+ cycles**, only once New Game+ can actually be started in play:
  measure the first few cycles with the carried-over character. Until then,
  just note the per-cycle multiplier from the code and that it's unmeasured.

Report one table per setting (a row per floor, as in Phase 4), plus one
comparison table across all settings: survival by player type, lowest HP at
the last boss, and healing items left over.

## Rules

- Read-only pass — do not modify any file under `src/` or `tests/`, and
  don't create or leave behind any file in the repo itself (a scratch
  simulation script, if used, stays outside the tracked project).
- Every number/claim must come from actually reading the current code on
  this run — don't reuse figures from a previous run or from roadmap.md/
  CLAUDE.md/map.md's own descriptions.
- Suggestions, not fixes: phrase findings as "consider lowering X's armour
  from 3 to 2" or "consider giving room Y an alternate route," not as a
  diff to apply. Don't touch any source file. For a setting other than
  Normal, phrase them as changes to that setting ("consider raising Hard's
  attack multiplier from 1.2 to 1.3"), and say what the change would do to
  the figures you measured.
- If something looks like a genuine correctness bug rather than a balance
  opinion (e.g. a stat that's clearly a typo, or a gate that's unreachable
  by any means at all) call that out separately from balance suggestions,
  since it's a different kind of problem.

## Report format

Structure the final report as:
1. **Baseline assumptions** — the player power curve you derived and from
   what (ancestry, XP/level formula, skill point value, expected gear per
   floor), and the difficulty settings as the code defines them, so the user
   can sanity-check the assumptions themselves.
2. **Per-floor difficulty notes (Normal)** — floor by floor, each populated
   encounter with a one-line verdict (too easy / on-target / too hard /
   spike) and a short reason; unpopulated floors get a one-line "not yet
   populated" note.
3. **Forced-path / softlock findings** — one entry per finding, each stating
   the gate, its single source, and the consequence of missing it.
4. **Gold economy (Normal)** — Phase 4's per-floor table for each player
   type, the sink/offer/reward figures, and any floor flagged as short of a
   repair.
5. **Difficulty settings** — Phase 5's table for each setting, the
   comparison table across settings, a one-line verdict per setting against
   its own description, and the specific checks (explorer/rusher gap, the
   skill gate, rounding, hardcore, New Game+).
6. **Correctness bugs found, if any** — kept separate from balance opinions.
7. A short closing summary: whether Normal sits at "medium", whether each
   other setting does what it says, and the handful of changes that would
   matter most if the user only made a few — saying for each whether it's a
   change to the baseline or to one setting.
