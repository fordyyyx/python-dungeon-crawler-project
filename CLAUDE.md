# Project Context for Claude Code

## What this project is
A text-based dungeon crawler RPG in pure Python, Greek mythology themed, built as an OOP portfolio project. The person building this is a first-year Computer Science student — code should stay readable and instructive, not overly clever or terse.

## Code style
- **British English spelling** in all identifiers, comments, and strings — `armour` not `armor`, `defence` not `defense`, `colour` not `color`, etc.
- `src/` layout: source lives in `src/dungeon_crawler/`, tests in `tests/`
- One responsibility per module (current, post-reorganisation structure —
  see the "Reorganise engine.py" item in roadmap.md's Completed section
  for how this came about):
  - `characters.py` — `Character`, `Player`, `Enemy`, `Ally`, `Skill`, `SkillPath`, `SkillTree`
  - `items.py` — `Item`, `Weapon`, `Armour`, `Consumable`, `QuestItem`, `Inventory`
  - `world.py` — `Room`, `Map`
  - `content.py` — actual game content (instances, not class definitions), organized by floor via `build_floor_0()`, `build_floor_1()`, etc., assembled by `build_world()`. Also holds `ANCESTRIES`, the ancestry-selection data.
  - `combat.py` — combat resolution: `resolve_combat_round`, `resolve_attack_and_check_defeat`, `handle_enemy_defeat`, `format_hp_line`, `flee_combat`, `handle_combat_command`, `get_enemy_display_name`, `handle_target_command`, `choose_enemy_action`/`_score_candidate_actions` (utility-based enemy AI — see "Enemy AI and team combat" below for the full design)
  - `exploration.py` — everything outside combat: `pick_up`, `trade_with_ally`, `is_exit_locked`, `display_local_exits`, `display_map`, `find_floor_for_room`, `handle_examine`
  - `character_creation.py` — `choose_ancestry`, `create_player`
  - `dev_tools.py` — the entire dev command set: `DEV_MODE`, every `handle_dev_*` function, `ITEM_REGISTRY`/`ENEMY_REGISTRY`/`ALLY_REGISTRY`, the `find_*_by_name` helpers
  - `engine.py` — now genuinely slim: `main()`'s loop and top-level command routing only, plus `print_room()` and `get_controls_text()` (both tightly coupled to the loop itself, not moved elsewhere)
  - **Still empty, reserved for upcoming roadmap items** (see roadmap.md for what goes where): `skills.py`, `status_effects.py`, `spells.py`, `save_system.py`, `achievements.py`, `shop.py`, `difficulty.py`. `content.py` is still a single file for now — the plan to split it into a `content/` package (one file per floor) happens as part of "Populate all floors," not this reorganisation.

## Docstrings and comments — retrofit complete, now a maintained standard
The full codebase now has docstrings on every function/class/method,
confirmed via `pydocstyle --convention=pep257` (deliberately ignoring
D205/D209/D400/D401 — those are formatting opinions stricter than this
project's own convention, not gaps). This is no longer just a
going-forward rule; it's the current, verified state of the code.
Run `pydocstyle --convention=pep257 src/dungeon_crawler/
--add-ignore=D203,D212,D213,D205,D209,D400,D401` any time to re-check —
should stay clean as new code is added, per the rule below.

## Docstrings and comments — required on all new code going forward
This is a standing convention starting now, specifically to shrink the
eventual retrofit pass (roadmap item: "Add docstrings and comments
throughout") rather than leave everything until then.
- **Every new function and class gets a docstring** — one line for
  anything simple and self-explanatory from its name/signature, a
  short paragraph only when the behaviour genuinely needs explaining
  (e.g. a non-obvious return shape, a side effect, a design decision
  worth a future reader knowing). Match the project's existing terse
  style — no need for full Google/NumPy-style docstring sections
  (Args/Returns/Raises) unless a function is genuinely complex enough
  to need them.
- **Comments explain *why*, not *what*.** The code should already say
  what it does; a comment earns its place by explaining a
  non-obvious reason, a bug it's guarding against, or a design
  decision that isn't visible from the code alone (e.g. "// ordering
  matters here — see the take_damage() signature history" is a good
  comment; "// add the item to inventory" above `inventory.add(item)`
  is not).
- **Retrofitting old code is explicitly out of scope for now** — that's
  its own dedicated roadmap item, deliberately placed after the
  engine.py reorganisation, so block-level comments can be grouped by
  the new file structure rather than needing to be redone. Don't go
  back and add docstrings to old functions opportunistically while
  working on something else; keep the two passes separate.

## Canonical attribute names — do not drift from these
- `Character.attack_damage` — **not** `attack_power`. This project has used `attack_power` inconsistently in earlier design discussion; `attack_damage` is the real, current name. Always check the actual file before assuming.
- `Character.armour`, `Character.hp`, `Character.max_hp` — as expected.
- `Character.has_double_strike`, `Character.has_thorns`, `Character.has_last_stand` — ability flags, live on `Character` (not `Player`), since `Enemy` could plausibly use them too.
- `Character.pending_damage_reduction` — **built.** Generic flat damage-reduction value, consumed (and reset to `0`) the next time `take_damage()` runs on this character. Lives on `Character`, not `Enemy`, since `take_damage()` doesn't know which subclass `self` is; `Enemy.brace_amount` is just the fixed value that populates it when Defend is chosen.
- `Player.ancestry_label` — set at character creation, displayed in `get_stats()`.
- `Player.intellect` — **Player-only**, not on `Character`. Matches `experience`/`gold`'s precedent, not the ability flags' — nothing currently reads an enemy's or ally's intellect, so it doesn't belong on the shared base class. Set by ancestry (`ANCESTRIES["intellect"]`), grows by 1 on every `level_up()`.
- **Enemy AI fields — all built**: `Enemy.aggression_weight`, `Enemy.caution_weight`, `Enemy.randomness_weight` (utility-scoring weights, defaulting to `1.0`/`1.0`/`0.3`), `Enemy.brace_amount` (flat damage reduction from Defend, default `0`), `Enemy.heal_amount` (flat HP restored by Heal, default `0` — `0` excludes Heal from the candidate list entirely, see "Enemy AI and team combat" below). All plain data, same precedent as `experience_reward`/`gold_reward`, set per `create_*()` call; every existing call works unchanged thanks to the defaults. Tune specific enemies' actual values as part of "Populate all floors" (#12), not before.

## Testing conventions — follow these exactly, don't introduce new patterns
- **Plain `assert` statements only** — do NOT use `pytest.raises`. For testing that an exception is raised, use the manual pattern:
  ```python
  def test_example_raises_error():
      try:
          thing_that_should_fail()
          assert False, "Expected a ValueError but none was raised"
      except ValueError:
          pass
  ```
- **One test per behavior**, not one test per method. Multiple `assert` lines in one test are fine if they're all checking the result of the *same* action — split into separate tests if you'd need "and" to describe what's being checked.
- **Test naming**: `test_<what>_<expected_behavior>`.
- **Arrange-Act-Assert** structure in every test.
- **Identity vs equality**: classes in this project do NOT define `__eq__`. Test object presence with `is`/`in` against actual object references, never a freshly-constructed equivalent. Do not add `__eq__` to make tests easier.
- **Private attributes**: `Room` and `Inventory` use private lists (`_items`, `_enemies`, `_allies`) with controlled methods and a read-only `@property` for reading. Tests must go through public methods/properties, never `._items` etc. directly.
- Tests involving printed output use `capsys` — but note most methods that used to print now **return strings instead** (see below). Check whether `capsys` is actually still needed before using it.
- **Type-checking pattern**: `Room.get_exit()` and `Map.get_room()` return `Room | None`. Any test using the result must `assert result is not None` before accessing attributes, to satisfy Pylance's type narrowing.

## Design principles already established - don't fight these
- Composition over inheritance where the relationship is "has-a" (`Player.inventory`, `Player.skill_tree`), inheritance only for genuine "is-a" relationships.
- `Ally` is a standalone class, NOT `Ally(Character)`. Allies don't have combat stats.
- Functions that coordinate two independent classes (moving an item between a `Room` and a `Player`, trading between an `Ally` and a `Player`) live as standalone functions in `engine.py`. Functions that only touch one class's own state are methods on that class. Exception: `Inventory.use_item()` and `Inventory.unequip_item()` are methods on `Inventory` despite touching a `Character` too - this is established precedent, don't "fix" it to be a standalone function.
- **Per-ally behaviour is data, not branching.** Trade requirements (`Ally.required_items`), rewards (`Ally.reward`), and conditional dialogue (`Ally.hint_complete`) live as attributes on the `Ally` object. Never write `if ally.name == "X"` in `engine.py` - if new per-ally behaviour is needed, add a new attribute to `Ally` instead. The same principle now extends to enemies' combat AI — see "Enemy AI and team combat" below.
- **No `Team` class for combat sides.** Per the "don't add classes for flexibility" rule below, the player's side and the enemies' side are both plain `list[Character]`/`list[Enemy]` (player side is `[player]` until Companions exist) — not a new abstraction. See "Enemy AI and team combat" for the full reasoning.
- **Leading-underscore functions are module-internal helpers.** A function prefixed with `_` (e.g. `combat.py`'s `_score_candidate_actions()`) is not meant to be called from outside its own module — same spirit as `Room`'s `_items`/`_enemies`/`_allies` private lists, just applied to functions instead of attributes. Only introduce this when a helper is genuinely internal-only; most functions in this codebase are called across modules and should stay unprefixed.
- **`take_damage()` returns `tuple[int, str]`**: the actual damage dealt (after armour reduction) and a message (empty string if the target survived). It takes an optional `attacker: Character | None = None` parameter, used only for the Thorns ability to reflect damage back. **Also consumes `Character.pending_damage_reduction`** (built — see "Canonical attribute names" above) before applying armour, resetting it to `0` regardless of whether it changed anything, since a brace only ever protects against the next hit taken.
- **HP status lines use the shared `format_hp_line(player_team, enemy_team)` helper — never rebuild the HP-line string inline in more than one place.** This was independently duplicated once (in `resolve_combat_round()` and separately in `handle_combat_command()`'s `use` branch), and only one copy got updated when the HP-display feature was added, causing a real bug. Any new combat-message code that needs to show HP should call this helper, not reformat it again. **Fully generalized to an N-combatant display** (team combat is built — see "Enemy AI and team combat" below); the enemy side uses `get_enemy_display_name()` for its labels, so a duplicate-named enemy shows its disambiguation number here too.
- **A failed action never consumes the player's turn in combat.** If `use <item>` fails (item not found, per `Inventory.use_item()`'s `ValueError`), `handle_combat_command()` must `return` immediately with the error message, before the enemy gets a turn — never fall through into the enemy's attack. This was a real bug once (the `use` branch caught the exception but still ran the enemy's attack unconditionally afterward). The same rule will apply to Spells (see `roadmap.md`) once they exist — a failed cast (no mana, on cooldown) should not cost a turn either.
- **`handle_enemy_defeat(room, enemy, player)`** — takes `player` now, not just `room`/`enemy`, so it can grant `experience_reward`/`gold_reward` as part of the assembled defeat message. Every call site must pass `player` — this changed once already (added for XP/gold) and is exactly the kind of signature change worth double-checking every call site for, same as `take_damage()`'s history.
- **`Enemy.experience_reward`/`gold_reward`** — plain data, set directly in every `create_*()` function (per the `CLAUDE.md` constructor-vs-follow-up-call rule). Training-only enemies (the Training Dummy) are `0`/`0` deliberately — not worth farming.
- **`Player.gold`** — a resource, not a stat. Displayed in `get_inventory_display()`, never in `get_stats()`. `Player.gain_experience()`/`level_up()` handle XP and leveling; `level_up()` grants exactly one skill point and rolls `experience_to_next_level` forward by ×1.5.
- **`on_death()` returns a string, does not print.** All defeat/loot messaging is assembled and printed once, at the `engine.py` level, in the correct order - never print directly from inside `Character`/`Enemy`/`Player` methods.
- **Equip is single-slot per category.** A `Character` has `equipped_weapon`/`equipped_armour` (max one of each). Equipping a new weapon automatically unequips the old one first - it does not stack. Do not add multi-weapon/dual-wielding support without an explicit design discussion first.
- **Quest items** (`QuestItem` subclass) cannot be dropped (`Inventory.drop_item` raises `ValueError`) and are displayed separately, on their own line, at the bottom of `get_inventory_display()`.
- **Intellect gating (`examine`)**: `Room.examine_text`/`required_intellect` are plain constructor data. `handle_examine(room, player)` gates BOTH the flavour text and the hidden-exit reveal together by the same threshold — a room with `required_intellect > 0` withholds everything until the player meets it; `required_intellect = 0` (the default) means content always shows, same as before this rule was refined. (Revised from an earlier, stricter version of this rule that never gated the reveal at all — see below for why.)
- **Hard rule, Intellect specifically — revised**: Intellect **may** gate required progress, since Intellect grows automatically every level with no cap — nothing is ever *permanently* unreachable, just deferred until the player levels enough. The actual guardrail is **reachability, not avoidance of gating**: any `required_intellect` threshold set anywhere in the game must be realistically achievable within a normal playthrough's pace, not require an absurd amount of grinding relative to where that content sits in the game. When setting a threshold, sanity-check it against how many levels a player would plausibly have reached by that point, not just "is it theoretically possible eventually."
- **Locked exits**: `Room.locked_exits: dict[str, str]` maps a direction to a required item name. `is_exit_locked(room, direction, player)` in `engine.py` checks it. Never hardcode "first room only" logic - locking is what enforces order.
- **Hidden exits**: `Room.hidden_exits: dict[str, Room]` mirrors `locked_exits`'s pattern — exits invisible to `map`/`fullmap` until `Room.reveal_hidden_exits()` promotes them into the normal `.exits` dict. `examine` (alone, no argument) is what triggers the reveal and shows `Room.examine_text`. `examine <item>` is a separate thing — it reuses the existing `Item.description`, no new field.
- **General rule for what goes in a constructor vs. what stays a follow-up call**: plain data (strings, numbers, flags) always goes directly into `__init__` — never set it via a separate call afterward if the constructor already accepts it as a parameter. A follow-up call is only correct when the thing being added needs another object to already exist first (e.g. `Room.add_hidden_exit(direction, room)` needs the target `Room` built first, same as `.connect()`/`.lock_exit()` always have). This is why `Ally`/`Enemy` take their starting `items`/`loot` directly in `__init__`, and why `Room.examine_text` is a constructor parameter, not something set after the fact.
- **`map` vs `fullmap`/`world` are deliberately different**: `map` shows only the current room's own exits (cheap, local). `fullmap`/`world` does a recursive traversal from the current room, stopping at any locked exit, showing everything currently reachable. Don't merge these back into one command.
- **Dev commands** (`handle_dev_command`, gated by the `DEV_MODE` flag, toggled via the `developer mode` command) are testing-only and must never be referenced in the README or any player-facing text.
- Don't add `__eq__`, extra attributes, or extra methods "for flexibility" unless something in the actual design already needs them.

## Enemy AI and team combat
The full system is **built**: team representation, round structure,
target selection, `format_hp_line`'s generalization, the utility-scoring
engine, and all three actions (Attack, Defend/Brace, Heal). One scoring
flaw was found in playtesting and the fix is decided but not yet
implemented — see the end of this section.

- **Team representation**: no `Team` class (see "No `Team` class" above)
  — `player_team: list[Character]` (currently `[player]`) and `enemy_team`
  (i.e. `Room._enemies`, generally passed as `room.enemies`) are plain
  lists, threaded explicitly through every team-aware combat function.
- **Round order**: the player acts first (attack/item/etc.), then every
  still-living member of `enemy_team` takes a turn via
  `choose_enemy_action()`, in list order. Combat stays locked until the
  whole `enemy_team` is defeated or the player flees. Both loops that run
  enemy turns (`resolve_combat_round()`, and the `use ` branch of
  `handle_combat_command()`) stop rolling further enemy actions once the
  player is dead — this was a real bug once (only the `use` branch had
  the check; `resolve_combat_round()` didn't, so a team kill could
  re-trigger `take_damage()`'s `on_death()` message repeatedly for every
  enemy after the one that landed the killing blow).
- **`choose_enemy_action(enemy, player_team) -> str`** is a standalone
  function in `combat.py`, not an `Enemy` method — per the existing rule
  that functions coordinating two independent classes' state live
  standalone (same precedent as `trade_with_ally()`). Returns the name of
  the chosen action (`"attack"`, `"defend"`, or `"heal"`); callers branch
  on that string. `Enemy`'s old `choose_action()` placeholder method has
  been removed entirely — this standalone function replaced it.
- **AI model: utility-based scoring**, via `_score_candidate_actions()`
  (module-internal — see the leading-underscore convention above) and
  `choose_enemy_action()`. `_score_candidate_actions(enemy, player_team)`
  returns a `dict[str, float]` of every candidate action's base score:
  `"attack"` (weighted by `aggression_weight` against kill-potential and
  target HP%), `"defend"` (always a candidate, weighted by
  `caution_weight`), and `"heal"` (only included when
  `enemy.heal_amount > 0` — excluded entirely otherwise, not scored at
  zero). `choose_enemy_action()` adds an independent random noise term to
  every score (from `random.random()`, scaled by `randomness_weight` —
  not `random.uniform()`, to stay consistent with the monkeypatch-testable
  convention below), then returns the highest-scoring action. This is the
  "lucky escape" mechanic.
- **Defend/Brace**: chosen action sets `enemy.pending_damage_reduction =
  enemy.brace_amount`, consumed by `take_damage()` on the next hit this
  enemy takes (see "Canonical attribute names" and the `take_damage()`
  entry above). `brace_amount` has no zero-exclusion rule (unlike Heal) —
  every enemy always has Defend as a live candidate, even at
  `brace_amount = 0` (mechanically a no-op brace). Worth reconsidering if
  this ever proves as awkward in practice as the scoring flaw below.
- **Heal**: restores `min(enemy.heal_amount, enemy.max_hp - enemy.hp)` HP
  (capped at `max_hp`, no overheal). `heal_amount = 0` excludes Heal from
  the candidate list entirely, per the decided design.
- **Personality is per-enemy data, not branching** — `Enemy.aggression_weight`/
  `caution_weight`/`randomness_weight`/`brace_amount`/`heal_amount` (see
  "Canonical attribute names" above), defaulting to a balanced,
  Defend/Heal-inert preset (`1.0`/`1.0`/`0.3`/`0`/`0`) so every existing
  `create_*()` call works unchanged. Tune specific enemies' actual values
  as part of "Populate all floors" (#12), not before.
- **`format_hp_line`** is fully generalized to an N-combatant display,
  using `get_enemy_display_name()` for the enemy side of the line.
- **`get_enemy_display_name(enemy, enemy_team) -> str`** appends a stable
  `(n)` index only when `enemy_team` genuinely has more than one enemy
  sharing that name — uniquely-named enemies display exactly as before.
  The index is computed from position among same-named enemies in the
  *full* `enemy_team` (dead included), so a survivor's number never
  shifts when a same-named teammate dies mid-fight.
- **`handle_target_command(command, enemy_team, player) -> str`** handles
  the player-facing `target <name>` / `target <name> <number>` command,
  setting `player.current_target` (persists across rounds; bare `attack`
  then hits it). Routed from two places: a top-level branch in `main()`
  (for targeting before combat starts) and a branch inside
  `handle_combat_command()` (for switching targets mid-combat) — both
  call the same shared function, no duplicated logic. **Important:** the
  optional trailing number always indexes the same full-team, same-named
  ordering that `get_enemy_display_name()` uses for its labels — not a
  separately-filtered living-only list. This was a real bug once (a
  disambiguation prompt could show a number that no longer matched what
  actually got selected, once a same-named teammate had died); if this
  function is ever touched again, re-verify the number shown and the
  number that selects still agree, especially with a mix of dead/living
  same-named enemies.
- **Flee stays per-enemy**: every still-living enemy in `enemy_team`
  independently rolls its own parting-hit chance off its own HP% —
  `flee_combat(player, enemy_team)`.
- **Retreat/flee is explicitly player-only** — enemies never get it, full
  stop; not a candidate action, not planned as one.
- **Deliberately extensible, not extended yet**: Light/Heavy/Ranged/Spell
  attack variety (roadmap #7) and mana-based Spell-healing (roadmap #6)
  become additional candidate actions in this same scoring function once
  those items are built.

**Known issue, fix decided but not yet built — Defend can permanently
dominate a losing enemy's choices.** Found in playtesting: once an
enemy's HP drops and the player is still healthy, `"defend"`'s score
(`caution_weight * self_missing_hp_ratio`) climbs toward `caution_weight`
while `"attack"`'s score collapses toward `0` (both its terms —
kill-potential and `1 - target_hp_ratio` — are naturally small against a
healthy target). Once Defend wins, nothing in the model ever pulls Attack
back ahead, since Defend doesn't reduce the enemy's own missing-HP% (only
Heal does that) — the enemy turtles for the rest of the fight instead of
attacking at all. **Decided fix**: redefine Defend's score around genuine
incoming danger, not accumulated damage — `self_kill_potential = min(1.0,
max(0, target.attack_damage - enemy.armour) / enemy.hp)`, then
`defend_score = caution_weight * self_kill_potential`. This only spikes
when the player could realistically finish the enemy off soon, so a weak
player can never make a low-HP enemy panic-turtle. Apply this the next
time `_score_candidate_actions()` is touched.

## Dev tooling (engine.py, gated by DEV_MODE / "developer mode")
- `dev set <stat> <value>` is a **single generic command**, not one branch per stat — it reads/writes any real `Player` attribute name (via a small `STAT_ALIASES` dict for shorthand like `atk`/`def`, then `setattr`). New stats (e.g. Intellect) work automatically the moment the attribute exists on `Player` — never add a new hardcoded `dev set` branch for a new stat.
- Three distinct removal scopes, don't conflate them: `dev remove <character>` (one matching instance), `dev remove all <character>` (every instance of that one name), `dev clear room` (everything, regardless of name). None of the three trigger `handle_enemy_defeat()` or loot — a dev removal is not a kill.
- `dev kill` reuses `handle_enemy_defeat()` rather than reimplementing removal/loot logic.
- `handle_dev_command()` returns `tuple[str, Room | None]` — the second element is only non-`None` for `dev teleport`, letting `main()` reassign `current_room`. Every branch must return the tuple shape, including `None` for the room when not teleporting — a bare string return here was a real bug once (`dev spawn` printed the raw tuple because a stale call site hadn't been updated after this return type changed).
- Dev commands are checked **before** the `in_combat` branch in `main()`'s routing, not inside the exploration-only path — they must always work regardless of combat state. This was a real bug, now fixed; don't reintroduce it by nesting the `dev ` check inside another branch.
- Maintenance: every new enemy/ally `create_*()` function needs a matching line in `ENEMY_REGISTRY`/`ALLY_REGISTRY` (mirroring `ITEM_REGISTRY`), so `dev spawn` can find it.

## A known gap in /move-tests — check for this every time
`/move-tests` fixes imports in the *new* file it creates, but does
NOT clean up the *old* file's import line for names that just left.
After every `/move-tests` run, manually check the source file's own
top-level import statement (e.g. `test_engine.py`'s
`from dungeon_crawler.engine import ...` line) and remove any names
that no longer live there — otherwise the file fails to import at
all with a confusing `ImportError`, even though the actual moved
tests are fine. This will happen again on every subsequent
`/move-tests` run during the engine.py reorganisation, not just once.

## Keeping documentation in sync with code
- **`get_controls_text()` (engine.py) and the README's Controls section
  describe the same command list in two places.** There's no shared
  source for this — when a command changes, both must be updated
  by hand. Check both whenever a command is added, removed, or renamed.
  (`target` has already been added to both — see "Enemy AI and team
  combat" above.)
- **The `engine.py` reorganisation is done** — `combat.py`,
  `exploration.py`, `character_creation.py`, and `dev_tools.py` all
  exist now; `engine.py` itself is down to `main()`, `print_room()`,
  and `get_controls_text()`. `CLAUDE.md`'s module ownership list, the
  README's Project Structure section, `roadmap.md`'s own references,
  and the `.claude/commands/` slash commands (`gen-tests.md`,
  `gen-tests-all.md`) were all updated to match as part of finishing
  this item — this note stays here as a record of what that involved,
  in case a similar future split (e.g. `content.py` becoming a
  `content/` package, per "Populate all floors") needs the same
  four-part checklist applied again.
- **Roadmap numbers renumber whenever an item completes or moves.**
  Item #1 ("Enemy `choose_action()` + multiple enemies per room") moved
  to Completed, shifting every subsequent item down by one — any `#N`
  reference anywhere (this file included) needs re-checking against
  `roadmap.md`'s current numbering before trusting it, per `roadmap.md`'s
  own cross-reference rule.

## Ancestry / character creation system
- `content.py` holds `ANCESTRIES: dict[str, dict]` - each entry has `label`, `attack`, `armour`, `hp`, `bonus_skill_point`.
- Stats are **set outright**, not added to a baseline. Picking an ancestry replaces the player's starting stats entirely.
- `engine.py`'s `choose_ancestry()` and `create_player()` handle selection and construction, called in `main()` before the world is built.
- If adding a new ancestry: keep its total "power budget" roughly proportional to existing entries (no strict upgrades over `"basic"` in every stat at once) - see the existing table for the balance pattern (offence-leaning options sacrifice defence, defence-leaning options sacrifice offence, HP-heavy options sacrifice both).

## Testing main() — refined now that monkeypatch is approved
`main()` is no longer entirely off-limits, but it's tested
differently from everything else, and sparingly.
- **A small number of end-to-end smoke tests are worth having** —
  using `monkeypatch.setattr("builtins.input", ...)` fed from an
  iterator of scripted commands, plus `capsys` to capture output.
  These test the whole routing chain in one go (input parsing ->
  dispatch -> the real handler -> the printed result), which unit
  tests on individual handlers can't catch (e.g. a command routed to
  the wrong module after the engine.py split).
- **This is a genuinely different category from every other test in
  this project** — an integration/smoke test, not an isolated
  Arrange-Act-Assert unit test. Don't try to exhaustively script
  every command/state combination through `main()` this way; that's
  combinatorial and belongs to manual playtesting instead. A handful
  of high-value scripted playthroughs (a full happy path, dev-command
  routing) is the right scope — not a replacement for playtesting,
  a complement to it.
- If asked to generate tests for `engine.py`/`main()` specifically,
  this is the one place `monkeypatch` extends beyond its other two
  approved uses (randomness, input/file mocking) — scripted `input()`
  sequences for `main()` smoke tests fall under the same
  input-mocking approval.

## monkeypatch — approved, but only for two specific purposes
`pytest`'s built-in `monkeypatch` fixture is approved as an exception
to the "no new test patterns without asking" rule, but **only** for:
1. **Controlling randomness** — anything using `random` (currently
   `flee_combat()`'s free-hit chance and `choose_enemy_action()`'s
   utility-score randomness term — see "Enemy AI and team combat"
   above; will also apply to Dodge and Heavy Attack's miss chance once
   built) should use `monkeypatch.setattr("random.random", lambda:
   <fixed value>)` to force a specific branch deterministically, rather
   than running the test many times and hoping the probability shows up.
2. **Mocking `input()` or file I/O** — for testing input-driven flows
   (e.g. `choose_ancestry()`/`create_player()`'s prompts) or, once
   built, the save/load system's file reads/writes, without touching
   a real terminal or real disk.
Do NOT reach for `monkeypatch` outside these two cases — it is not a
general green light to mock things. If a new situation seems to call
for it, ask first, the same as any other new pattern.

## When generating tests for existing files
Match the existing test files' style exactly. Check what's already there first - never duplicate. Do not introduce `pytest.raises`, `unittest.mock`, fixtures beyond `capsys`, or any pattern not already in use, without asking first.

## Maintenance reminders
- Every new `create_*()` item function in `content.py` should also be added to `ITEM_REGISTRY` in `engine.py`, so `dev add` can find it.
- Every `create_*()` function for enemies/allies needs a non-empty `description`.