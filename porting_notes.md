# Porting Notes — Ideas for a Future Visual Port

A running scratchpad for anything worth remembering when this eventually becomes
a graphical game (Unreal Engine, using C++ — see the design conversation this
came from; originally planned as a Godot/GDScript port, changed once C++ itself
became the actual goal rather than just the destination). Nothing here should
influence the Python build itself; this is purely for later. Add to it whenever
something occurs to you mid-build.

---

## General principles worth carrying over
- The underlying class design (`Character`/`Item`/`Room`/`SkillTree` hierarchy)
  should translate close to directly — the port is a new presentation layer,
  not a redesign. Resist the urge to "fix" settled design decisions during
  the port itself; note disagreements here instead and revisit deliberately.
- Anywhere the text version currently prints a message, the visual version
  needs both a visible *and* readable equivalent (text log, floating combat
  text, etc.) — some players will still want to read what happened, not just
  see a number change.

- The one-off hint system (`hints.py` - each mechanic explained once, the
  first time it matters, then never again per save) maps directly onto a
  non-blocking tutorial toast or tooltip. Keep the "once per save, never
  repeated" rule, and the principle that the text lives in one table rather
  than at each trigger site - that's what makes the hints easy to reword or
  localise later.

## Combat
- **Lifesteal (`Character.has_lifesteal`, first used by Lamia) wants a visible drain effect** - a beam or
  particle trail flowing from the target to the attacker, timed with the attacker's HP bar ticking up, rather
  than just a second line of combat text under the damage number.
- **Multi-stage boss phase transitions and wave-gated adds are a natural fit for a cutscene beat or arena
  reveal** - the seamless "combat never unlocks" transition (`next_phase_factory`) that reads as a single
  printed line in text wants a proper beat in a visual version (a brief cinematic camera pull, a boss
  roar, an arena lighting change) rather than just swapping the health bar's portrait instantly. The
  wave-gate mechanic (`next_wave_factories`/`wave_gate_factory` - clear every add before the boss reveals
  its next phase) maps naturally onto a visible "adds remaining" counter or highlighted-add-portraits UI,
  so the player understands *why* the boss isn't transitioning yet without needing to infer it themselves.
- **The Practice Chamber (a respawning, stat-customisable dummy, free spellcasting) is a natural fit for a dedicated training-room
  mode** - a UI that surfaces its free-action nature explicitly (no resource bars depleting, an obvious "practice" badge) rather than
  relying on the player noticing mana/cooldowns just aren't moving. The dummy's customisable stats (`dummy set <stat> <value>` in
  text) become sliders or a stat-editor panel in a visual version, rather than typed commands.
- Both combatants' HP should be visible **simultaneously** as health bars,
  rather than the sequential "you take damage, then see the result" text
  flow — a visual version can show both changing in real time. With full
  team combat now built, this means a health bar per living combatant on
  both sides at once, not just a 1v1 pair.
- The combat lock (in_combat / current_target) maps naturally onto a
  dedicated combat screen or UI mode — action buttons (Attack / Flee /
  Use Item) replacing the typed command list.
- Damage numbers (already shown in text as "for X damage") are a natural fit
  for floating combat text popping off the target on hit.
- `on_death()`'s message returns are a good hook point for a death
  animation/sprite-swap trigger — the method already tells you exactly when
  and on whom to play it.
- Double Strike / Thorns / Last Stand each want their own visual "tell" —
  a second swing animation, a reflected-damage flash on the attacker, and a
  clear "saved from death" effect respectively — so the player registers
  *which* ability fired without reading text.
- The flee mechanic's HP-scaled chance of a free hit could be shown as a
  visible risk meter before the player commits to fleeing, rather than a
  hidden roll — more readable in a graphical UI than it needs to be in text.
- **Team combat and target selection are now built (`player_team`/
  `enemy_team`, `target <name> <number>`).** A visual version replaces
  typed disambiguation entirely — clicking directly on an enemy's sprite
  or portrait *is* the target selection, so `get_enemy_display_name()`'s
  stable `(n)` numbering (needed purely because text has no equivalent of
  "point at the one you mean") becomes unnecessary. Duplicate-named
  enemies just need visually distinguishable positions/portraits instead.
- **Defend/Brace and Heal (the enemy AI's non-attack actions) each want
  their own visual tell too**, same reasoning as Double Strike/Thorns/Last
  Stand above — a bracing stance or shield-up animation, and a heal glow
  or HP-tick-up effect, so the player registers *which* action an enemy
  took without reading text.
- **The enemy AI's utility-based action choice (Attack/Defend/Heal) is a
  natural fit for a telegraphed "intent" icon** above the enemy a beat
  before it resolves — a common roguelike/tactics convention that doesn't
  exist in the turn-locked text version (the player only learns what an
  enemy did after it's already happened). Worth considering deliberately
  for the port, since it changes the combat's information/tension balance
  rather than just its presentation.
- **Attack variety (light/heavy/ranged) is a natural fit for a stance or
  attack-type selector** (radial menu, face buttons, or a weapon-switch
  prompt) rather than typed `attack heavy`/`attack ranged`. The heavy
  attack's miss chance is a good windup/telegraph animation moment - a
  visible wind-up that can whiff, rather than a hidden dice roll the player
  only sees the result of.
- **A free action (a genuine heal) not ending the turn deserves its own
  clear visual "still your turn" feedback** - text can just print the
  enemy's turn or not, but a UI needs something explicit (no turn-transition
  animation, a distinct "free action" flash, etc.) so the player isn't left
  wondering whether their action actually went through.

## World / Map
- The room network (Room.exits as a dict) maps naturally onto a node-based
  or grid-based map screen — the existing `fullmap`/`world` traversal logic
  (stopping at locked exits) could drive what's actually drawn/revealed.
- Locked exits are a natural fit for a visible "locked door" sprite/icon
  rather than text saying "Locked Door" — could show *what's* required on
  hover, rather than only on a failed attempt.
- Each room's description (currently flavour text) is what art direction/
  background art would replace or accompany — worth keeping the text as art
  direction reference when the time comes, not throwing it away.
- Multi-floor structure (descend/ascend) suggests a level-select or vertical
  progression map as an option, rather than only room-by-room navigation.
- The new one-way `"forge"` shortcut exits (Prayer Room, Stony Lair, Maze of
  Pillars back to the Forge of Prometheus) are a natural fit for a fast-travel
  waypoint UI - a shimmering-doorway visual already exists in the text
  description, ready-made as art direction. The two-way, unlock-on-first-use
  version (`Room.fast_travel_locks`, now enforced in the text version too)
  maps directly onto the genre-standard "discover a waypoint, then teleport
  freely between discovered ones" pattern - a visual version could show
  still-locked return paths greyed out on the waypoint list rather than only
  refusing them on a failed attempt.
- A small HP tick on movement (`PASSIVE_REGEN_PER_MOVE`) wants its own subtle
  cue distinct from a potion heal - a faint pulse on the HP bar as you cross
  into a new room reads very differently from a burst heal effect, and that
  distinction matters for the player understanding *why* their HP just moved. It
  only ever regenerates up to three-quarters of max HP, so the pulse should
  visibly stop at a marked line on the bar - otherwise players will wonder why
  walking stopped healing them.
- Guarded exits (`Room.guarded_exits` - a floor's key fights bar the way
  forward until defeated) are a natural fit for the boss physically standing
  in the doorway, or a sealed-door visual that breaks open on the kill -
  rather than the text version's refusal message on a failed move. Worth
  marking guarded exits on the map screen too; the text version doesn't show
  them until you try one.
- The `uncleared` command (which rooms you've visited still hold enemies,
  items, an open trade, or a hidden passage - plus unexplored rooms one step
  away) is really a map overlay waiting to happen - a marker or glow on
  unfinished rooms, and a "?" on undiscovered doorways, rather than a typed
  report. Keep its spoiler-safety: only rooms the player has seen, or can see
  the doorway to, get marked, and a hidden passage is hinted at, never
  pointed to. `toggle auto
  map` similarly becomes an always-on minimap, which most visual versions
  would simply have by default.

## Items / Inventory
- Equip slots are a natural fit for a paper-doll style UI — both weapons
  (melee/ranged) and armour (helmet/body) now occupy two independent slots
  each, so a paper doll would show four simultaneous equip points rather
  than two; within each slot, "equipping replaces, doesn't stack" already
  matches how visual equip slots typically work, so no logic change needed,
  just a UI showing it.
- Armour durability (now shown in the text inventory as `3/5 durability`) is a
  natural fit for a small wear bar on each paper-doll slot, changing colour as
  it nears breaking - the text version only shows it when you open the
  inventory, but a player should be able to see gear about to break mid-fight.
- `take all` is the text version's "loot all" button - a single prompt over a
  pile of drops (or an ally's offered gifts) rather than one click per item.
- Quest items being visually separated (already true in the text inventory)
  suggests a distinct visual "key items" pouch/tab in a graphical inventory
  screen.
- Item descriptions (already written with flavour) are ready-made tooltip
  text.

## NPCs / Dialogue
- `Ally.hint` / `hint_complete` are effectively dialogue nodes already —
  could map onto a simple dialogue-tree/text-box system fairly directly,
  since the conditional-hint logic (required_items check) already exists.
- Trade UI is a natural drag-and-drop or button-based exchange screen,
  replacing the typed `trade` command — the underlying `trade_with_ally()`
  logic (missing items / equipped items check) doesn't need to change.

## Skill Tree
- The three-path, three-tier structure is a natural fit for a visual skill
  tree UI (the genre-standard branching-node look) — `SkillPath.unlocked_count`
  already tracks exactly what a UI would need to show progress per branch.
- `level_up()`'s return message is a good hook for a "Level Up!" moment —
  a flash, a sound, a brief pause — same pattern as `on_death()` already
  being a natural animation trigger point.
- Gold (`Player.gold`) and XP toward the next level are the two obvious
  candidates for a persistent HUD element (a counter and a progress bar
  respectively) rather than something only checked via a menu, the way
  the text version's `inventory`/`stats` commands currently work.

## Character Creation
- Ancestry selection is a natural fit for a character-select screen with
  portraits per option, rather than a text list — the ANCESTRIES dict
  already has everything needed (label, stats) to drive such a screen.
- The two-step primary/secondary ancestor pick (stats, then a passive
  ability from a different figure) suggests a two-panel or two-stage
  select screen — primary on one side with live stat previews, secondary
  on the other with an icon/tooltip per ability rather than the text
  version's plain description line. Graying out (not hiding) whichever
  figure was already picked as primary would read more clearly than the
  text version's "you've already claimed that blood, try again" reprompt.

## Save / Load
- Profile/slot selection (3 profiles, 5 slots each) is a natural fit for a
  save-slot picker screen — `slot_summary()`'s one-line format (name, level,
  ancestry, current room) is already exactly what such a UI would show per
  slot.
- The current JSON-per-slot format (`save_system.py`) is a reasonable
  reference for *what* fields a save actually needs, but Unreal's own
  `USaveGame`/`SaveGameToSlot` system would likely replace it outright
  rather than reading the same JSON — treat `save_system.py` as a spec of
  what to persist, not how.
- Autosave firing silently on the first crossing into a new floor (a plain
  `"(autosaved)"` line in text) wants a small, unobtrusive UI cue in a
  visual version — a corner icon or brief toast, not a loading-screen
  moment, since nothing actually pauses for it.
- The deliberate "full room snapshot every save, not a delta of only
  changed rooms" simplification (safe for a text game's trivial JSON size)
  is worth revisiting for a visual port with much larger per-room state
  (positions, animation state, particle spawns) — a real delta/dirty-flag
  model becomes worth the complexity there in a way it isn't here.
- Dying now prompts "Reload your last save?" rather than always ending the
  run outright — a natural fit for a classic "Continue? Yes/No" game-over
  screen (with a countdown timer, if the port wants to lean into that genre
  convention) rather than a plain yes/no text prompt.

## Input
- Controller support (stick for movement, buttons for actions) should be
  built Unreal-native, not retrofitted into the Python version — Unreal's
  Enhanced Input system already unifies keyboard/controller/stick under one
  input mapping context, whereas Python's `input()`-based text loop would
  need an awkward parallel translation layer bolted on for comparatively
  little payoff.

## Open questions to resolve when the port actually starts
- Turn-based text combat maps easily onto a turn-based visual battle screen
  — but worth deciding then whether to keep it turn-based, or take the
  opportunity to make it real-time/action-based instead. Not a decision to
  make now.
- Does the visual version keep the same floor-by-floor gating, or would a
  more open, explorable 2D map feel better once movement isn't typing a
  direction?