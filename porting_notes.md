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

## Combat
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

## Items / Inventory
- Equip slots are a natural fit for a paper-doll style UI — both weapons
  (melee/ranged) and armour (helmet/body) now occupy two independent slots
  each, so a paper doll would show four simultaneous equip points rather
  than two; within each slot, "equipping replaces, doesn't stack" already
  matches how visual equip slots typically work, so no logic change needed,
  just a UI showing it.
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