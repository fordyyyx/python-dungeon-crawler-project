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

- **No difficulty-scaling system exists yet** (see roadmap.md's "Difficulty
  system" item — a future global multiplier with per-boss overrides). Every
  number in the game right now (enemy hp/attack/armour, loot, XP/gold
  rewards, player starting stats) is therefore the single baseline tuning
  everything else will eventually scale from. Frame every suggestion around:
  **this baseline should read as a standard "medium" difficulty** — beatable
  by a reasonably careful player without grinding, capable of real player
  deaths on a careless one — since easier/harder modes will only ever be a
  multiplier away from these numbers, not a separate tuning pass.
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

## Rules

- Read-only pass — do not modify any file under `src/` or `tests/`, and
  don't create or leave behind any file in the repo itself (a scratch
  simulation script, if used, stays outside the tracked project).
- Every number/claim must come from actually reading the current code on
  this run — don't reuse figures from a previous run or from roadmap.md/
  CLAUDE.md/map.md's own descriptions.
- Suggestions, not fixes: phrase findings as "consider lowering X's armour
  from 3 to 2" or "consider giving room Y an alternate route," not as a
  diff to apply. Don't touch any source file.
- If something looks like a genuine correctness bug rather than a balance
  opinion (e.g. a stat that's clearly a typo, or a gate that's unreachable
  by any means at all) call that out separately from balance suggestions,
  since it's a different kind of problem.

## Report format

Structure the final report as:
1. **Baseline assumptions** — the player power curve you derived and from
   what (ancestry, XP/level formula, skill point value, expected gear per
   floor), so the user can sanity-check the assumptions themselves.
2. **Per-floor difficulty notes** — floor by floor, each populated encounter
   with a one-line verdict (too easy / on-target / too hard / spike) and a
   short reason; unpopulated floors get a one-line "not yet populated" note.
3. **Forced-path / softlock findings** — one entry per finding, each stating
   the gate, its single source, and the consequence of missing it.
4. **Correctness bugs found, if any** — kept separate from balance opinions.
5. A short closing summary: overall read on whether the current baseline
   sits at "medium," and the handful of changes that would matter most if
   the user only made a few.
