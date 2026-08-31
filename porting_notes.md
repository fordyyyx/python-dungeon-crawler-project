# Porting Notes — Ideas for a Future Visual Port

A running scratchpad for anything worth remembering when this eventually becomes
a graphical game (Godot, most likely — see the design conversation this came
from). Nothing here should influence the Python build itself; this is purely
for later. Add to it whenever something occurs to you mid-build.

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
- Both combatants' HP should be visible **simultaneously** as health bars,
  rather than the sequential "you take damage, then see the result" text
  flow — a visual version can show both changing in real time.
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
- Equip slots (weapon/armour) are a natural fit for a paper-doll style UI —
  the "equipping replaces, doesn't stack" rule already matches how visual
  equip slots typically work, so no logic change needed, just a UI showing it.
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

## Input
- Controller support (stick for movement, buttons for actions) should be
  built Godot-native, not retrofitted into the Python version — Godot's
  Input system already unifies keyboard/controller/stick under one action
  map, whereas Python's `input()`-based text loop would need an awkward
  parallel translation layer bolted on for comparatively little payoff.

## Open questions to resolve when the port actually starts
- Turn-based text combat maps easily onto a turn-based visual battle screen
  — but worth deciding then whether to keep it turn-based, or take the
  opportunity to make it real-time/action-based instead. Not a decision to
  make now.
- Does the visual version keep the same floor-by-floor gating, or would a
  more open, explorable 2D map feel better once movement isn't typing a
  direction?