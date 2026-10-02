"""Room and item interactions - everything outside of combat: picking up and dropping items, trading with allies,
examining surroundings, map/movement helpers (including locked, guarded, story-gated and concealed exits), talking and companion
advice, and the enemy-trait analysis shared by Odysseus' advice and the floor 7 seers."""

from dungeon_crawler.characters import Player, Ally, Companion, Enemy
from dungeon_crawler.items import Armour, Weapon
from dungeon_crawler.world import Room, StoryGate
from dungeon_crawler.dialogue import start_dialogue

REPAIR_COST_PER_POINT = 2
TRAIT_ORDER = ("heavy_armour", "evasive", "heals", "pierces", "numerous", "puzzle")
ODYSSEUS_ADVICE = {
    "heavy_armour": "That armour's thick. Something that pierces it, or a few heavy blows, will do more than cutting at it.",
    "evasive": "You'll never catch that one up close. Use a bow, or a spell.",
    "heals": "Give it time and they'll patch themselves up. Hit hard and fast.",
    "pierces": "Your armour won't count for much against them - don't trust it to save you.",
    "numerous": "There are a lot of them. Something that hits more than one at once would earn its keep.",
    "puzzle": "You can't fight that. Look around - there'll be another way.",
}
HIDDEN_WAYS_NOTE = "Hidden ways remain somewhere on the floors you've reached."
CHEST_OPENED = "chest_opened"

def pick_up(room: Room, item_name: str, player: Player) -> str:
    """Move the named item from room into player's inventory. Returns an error message if no matching item is present."""
    for item in room.items:
        if item.name.lower() == item_name.lower():
            player.inventory.add(item)
            room.remove_item(item)
            return f"You take {item.with_article(definite=True)}. {item.description}"
    return "That's not here."

def take_all(room: Room, player: Player) -> str:
    """Move every item in room into player's inventory, summarised on one line rather than one description per item."""
    items = room.items
    if not items:
        return "There's nothing here to take."
    for item in items:
        room.remove_item(item)
        player.inventory.add(item)
    return f"You take: {', '.join(item.display_name for item in items)}."

def take_all_from_ally(ally: Ally, player: Player) -> str:
    """Move every item ally is holding into player's inventory."""
    items = list(ally.inventory.items)
    if not items:
        return f"{ally.name} has nothing left to give."
    for item in items:
        ally.inventory.remove(item)
        player.inventory.add(item)
    return f"{ally.name} gives you: {', '.join(item.name for item in items)}."

def trade_with_ally(ally: Ally, player: Player):
    """Exchange player's required_items for ally's reward, if the player has every item and none of them are currently equipped.
    Returns a message explaining what's still missing/equipped if the trade can't complete yet, or the success message otherwise."""
    if not ally.required_items or ally.reward is None:
        return f"{ally.name} has nothing to trade."

    player_item_names = [item.name for item in player.inventory.items]
    missing = [name for name in ally.required_items if name not in player_item_names]

    if missing:
        return f"{ally.name} shakes their head. \"You're still missing: {', '.join(missing)}.\""

    equipped_items = [
        item for item in player.inventory.items
        if item.name in ally.required_items and item.equipped
    ]

    if equipped_items:
        # checked ahead of time rather than letting the removal below hit it - Inventory.remove() has no
        # equipped guard of its own (only drop_item() does), so this is the only place stopping an equipped trade
        equipped_names = ", ".join(item.display_name for item in equipped_items)
        return f"{ally.name} shakes their head. \"You'll need to unequip: {equipped_names}.\""

    if not player.has_silver_tongue:
        for name in ally.required_items:
            item = next(item for item in player.inventory.items if item.name == name)
            player.inventory.remove(item)

    player.inventory.add(ally.reward)
    ally.trade_completed = True
    result = f"{ally.name} nods, accepting each item in turn. \"You've done well.\" They hand you {ally.reward.with_article(definite=True)}."
    if ally.post_trade_message:
        result += f"\n\n{ally.post_trade_message}"
    return result

def recruit_companion(name: str, room: Room, player: Player) -> str:
    """Recruit the named companion from room onto player's team, if player already holds every item in the companion's required_items
    (and none are currently equipped) - consumes those items on success, mirroring trade_with_ally()'s exact mechanics. Blocks with
    an error if player already has a companion (dismiss_companion() first), if no matching companion is present, or if the companion
    still requires a duel (see start_duel())."""
    if player.companion is not None:
        return f"You already have a companion, {player.companion.name}. Dismiss them first."
    companion: Companion | None = next((c for c in room.companions if c.name.lower() == name.lower()), None)
    if companion is None:
        return f"There's no one named '{name}' here to recruit."
    if companion.requires_duel:
        return f"{companion.name} won't follow anyone who hasn't beaten them. Try 'challenge {companion.name.lower()}'."
    if not companion.can_be_recruited(player):
        return companion.recruit_blocked_message or f"{companion.name} isn't ready to join you yet."

    player_item_names = [item.name for item in player.inventory.items]
    missing = [item_name for item_name in companion.required_items if item_name not in player_item_names]

    if missing:
        return f"{companion.name} shakes their head. \"You're still missing: {', '.join(missing)}.\""

    equipped_items = [
        item for item in player.inventory.items
        if item.name in companion.required_items and item.equipped
    ]

    if equipped_items:
        equipped_names = ', '.join(item.display_name for item in equipped_items)
        return f"{companion.name} shakes their head. \"You'll need to unequip: {equipped_names}.\""

    for item_name in companion.required_items:
        item = next(item for item in player.inventory.items if item.name == item_name)
        player.inventory.remove(item)

    room.remove_companion(companion)
    player.companion = companion
    return f"{companion.name} joins you."

def dismiss_companion(player: Player):
    """Release player's current companion, restoring them to full HP and returning them to their home_room, returns a message explaining
    nothing happened if player has no companion to dismiss."""
    companion = player.companion
    if companion is None:
        return "You don't have a companion to dismiss."

    companion.hp = companion.max_hp
    companion.home_room.add_companion(companion)
    player.companion = None
    return f"{companion.name} returns to {companion.home_room.name}."

def take_opening_line(speaker, player: Player) -> str:
    """The speaker's opening line the first time only, recording it in seen_lines - '' if there isn't one, or it's already been heard. The one
    place once-only opening lines are consumed, shared by talk_to() and any room interaction that should also count as a first meeting."""
    line = getattr(speaker, "opening_line", "")
    key = f"opening:{speaker.name}"
    if not line or key in player.seen_lines:
        return ""
    player.seen_lines.add(key)
    return line

def talk_to(speaker, player: Player, room: Room) -> str:
    """The speaker's dialogue, preceded - the first time only - by their opening_line (take_opening_line()), then any ancestry line matching
    the player's primary or secondary ancestry, then any companion line (companion_lines, on an ally or a companion) for the companion in the player's party. A
    speaker with a branching dialogue (Ally.dialogue) starts it in room instead of calling talk() - which is why room is needed. Every
    place that shows ally or companion dialogue (the 'talk' command and auto-talk) goes through this rather than calling speaker.talk() directly,
    so the once-only rule lives in one place and talk() itself stays free of side effects."""
    lines = []
    opening = take_opening_line(speaker, player)
    if opening:
        lines.append(opening)
    for key in (player.ancestry_key, player.secondary_ancestry_key):
        if key is None or key not in speaker.ancestry_lines:
            continue
        seen_key = f"ancestry:{speaker.name}:{key}"
        if seen_key not in player.seen_lines:
            player.seen_lines.add(seen_key)
            lines.append(speaker.ancestry_lines[key])
    companion = player.companion
    if companion is not None:
        companion_line = (getattr(speaker, "companion_lines", None) or {}).get(companion.name)
        seen_key = f"companion:{speaker.name}:{companion.name}"
        if companion_line and seen_key not in player.seen_lines:
            player.seen_lines.add(seen_key)
            lines.append(companion_line)
    if getattr(speaker, "dialogue", None):
        lines.append(start_dialogue(speaker, room, player))
    else:
        lines.append(speaker.talk(player))
    return "\n\n".join(lines)

def get_rival_lines(room: Room, player: Player) -> list[str]:
    """Lines the player's companion says on first meeting a living enemy in room that they have a rival line for. Each line is shown once per save.
    Nothing if the player has no companion, or theirs is downed."""
    companion = player.companion
    if companion is None or not companion.is_alive():
        return []
    lines = []
    for enemy in room.enemies:
        line = companion.rival_lines.get(enemy.name)
        seen_key = f"rival:{companion.name}:{enemy.name}"
        if line and enemy.is_alive() and seen_key not in player.seen_lines:
            player.seen_lines.add(seen_key)
            lines.append(line)
    return lines

def get_enemy_ancestry_lines(room: Room, player: Player) -> list[str]:
    """Lines living enemies in room say on first sight of a player descended from them (primary or secondary ancestry). Each is shown once per save,
    sharing seen_lines' 'ancestry:<speaker>:<key>' keys with talk_to(), so an enemy and an ally can never collide unless they share a name."""
    lines = []
    for enemy in room.enemies:
        if not enemy.is_alive():
            continue
        for key in (player.ancestry_key, player.secondary_ancestry_key):
            if key is None or key not in enemy.ancestry_lines:
                continue
            seen_key = f"ancestry:{enemy.name}:{key}"
            if seen_key not in player.seen_lines:
                player.seen_lines.add(seen_key)
                lines.append(enemy.ancestry_lines[key])
    return lines

def get_advice(room: Room, player: Player) -> str:
    """Advice from the player's companion, if they give it (Companion.gives_advice). Built from the room itself rather than written per room, so
    it stays correct on every floor and after any rebalance: each trait of the living enemies here produces one line, plus the room's own optional
    advice (Room.advice) for anything the traits can't describe, like a puzzle."""
    companion = player.companion
    if companion is None or not companion.gives_advice:
        return "You've no one to ask."

    enemies = [e for e in room.enemies if e.is_alive() and not e.respawns]
    fighting = [e for e in enemies if not e.invulnerable]
    lines = [ODYSSEUS_ADVICE[trait] for trait in enemy_traits(room.enemies) if not (trait == "puzzle" and room.advice)]
    if room.advice:
        lines.append(room.advice)

    if not lines:
        return f"{companion.name} looks around. \"Nothing here worries me. Keep your eyes open anyway.\""
    return "\n".join(f"{companion.name}: \"{line}\"" for line in lines)

def is_exit_locked(room: Room, direction: str, player: Player) -> bool:
    """Whether direction requires an item player doesn't currently hold. An exit not in locked_exits is never locked."""
    if direction not in room.locked_exits:
        return False
    required_item_name = room.locked_exits[direction]
    return required_item_name not in [item.name for item in player.inventory.items]

def get_exit_guardian(room: Room, direction: str) -> Enemy | None:
    """The first living, non-respawning enemy blocking 'direction', or None if the exit isn't guarded or nobody's left to guard it. An
    invulnerable enemy counts, so Charybdis keeps her exit guarded until her puzzle is solved."""
    if direction not in room.guarded_exits:
        return None
    return next((e for e in room.enemies if e.is_alive() and not e.respawns), None)

def get_story_gate(room: Room, direction: str, player: Player) -> StoryGate | None:
    """The story gate still shutting 'direction', or None if there isn't one or the player already has one of its flags."""
    gate = room.story_gates.get(direction)
    if gate is None or any(flag in player.story_flags for flag in gate.required_flags):
        return None
    return gate

def display_local_exits(room: Room, player: Player) -> str:
    """Format only the current room's own exits - 'Locked Door' in place of the destination for an item-locked exit, the destination plus
    '(guarded by <name>)' while a guardian lives, 'Sealed Shortcut' for a fast-travel exit not yet opened from the other side, and the
    destination plus its gate's map_label while a story gate is shut. An exit to a concealed room isn't listed at all."""
    if not room.exits:
        return "There are no exits from this room."
    lines = []
    for direction, target in room.exits.items():
        if is_room_concealed(target, player):
            continue
        guardian = get_exit_guardian(room, direction)
        if is_exit_locked(room, direction, player):
            lines.append(f"{direction} -> Locked Door")
        elif guardian is not None:
            lines.append(f"{direction} -> {target.name} (guarded by {guardian.name})")
        elif direction in room.fast_travel_locks:
            lines.append(f"{direction} -> Sealed Shortcut")
        elif (gate := get_story_gate(room, direction, player)) is not None:
            lines.append(f"{direction} -> {target.name} ({gate.map_label})")
        else:
            lines.append(f"{direction} -> {target.name}")
    return "\n".join(lines) if lines else "There are no exits from this room."

def display_map(current_room: Room, player: Player) -> str:
    """Format every room reachable from current_room, via a recursive traversal that stops at any exit the player can't use yet - locked,
    guarded, a sealed shortcut, or a shut story gate, each labelled as in display_local_exits(). Concealed rooms are left out entirely. Unlike display_local_exits(), this shows the whole
    currently-reachable map, not just the current room's own exits."""
    visited: set[str] = set()
    lines = []

    def explore(room: Room) -> None:
        """Depth-first visit room and every room reachable from it, appending exit lines to the enclosing lines list. Recursion stops at an unusable exit (locked, guarded, sealed or story-gated) or an already-visited room, so this always terminates even with exit loops."""
        if room.name in visited:
            return
        visited.add(room.name)
        lines.append(f"\n{room.name}")

        unlocked_targets = []
        for direction, target in room.exits.items():
            if is_room_concealed(target, player):
                continue
            guardian = get_exit_guardian(room, direction)
            if is_exit_locked(room, direction, player):
                lines.append(f"  {direction} -> Locked Door")
            elif guardian is not None:
                lines.append(f"  {direction} -> {target.name} (guarded by {guardian.name})")
            elif direction in room.fast_travel_locks:
                lines.append(f"  {direction} -> Sealed Shortcut")
            elif (gate := get_story_gate(room, direction, player)) is not None:
                lines.append(f"  {direction} -> {target.name} ({gate.map_label})")
            else:
                lines.append(f"  {direction} -> {target.name}")
                unlocked_targets.append(target)

        for target in unlocked_targets:
            explore(target)

    explore(current_room)
    return "\n".join(lines)

def find_floor_for_room(room: Room, all_floors: dict[str, dict[str, Room]]) -> str | None:
    """Which floor (by name) room belongs to, or None if it isn't in any floor's room dict."""
    for floor_name, rooms in all_floors.items():
        if room.name in rooms:
            return floor_name
    return None

def handle_examine(room: Room, player: Player) -> str:
    """Show extra flavour text and reveal hidden exits, both gated together by required_intellect. A threshold of 0 (the default)
    means content always shows, exactly as before - only rooms explicitly setting a higher threshold (e.g. the Trophy Room's entrance)
    are genuinely gated, reveal included, not just the flavour text. Intellect-gated progress is allowed, since intellect grows by one
    every level and from IntellectReward items - there's no hard cap, but the finite experience in the world sets a soft one, so the guardrail
    is that every gate stays reachable, not avoidance of gating entirely."""
    if player.intellect < room.required_intellect:
        return "There's something here, but you can't quite make sense of it."

    messages = []
    if room.examine_text:
        messages.append(room.examine_text)
    else:
        messages.append("You look closer, but find nothing you hadn't already noticed.")

    revealed = []
    for direction in list(room.hidden_exits):
        room.reveal_hidden_exit(direction)
        revealed += [direction]
    if revealed:
        messages.append(f"Your search reveals a hidden passage: {', '.join(revealed)}.")

    return "\n".join(messages)

def repair_item(item_name: str, player: Player, room: Room) -> str:
    """Restore a named Armour item to full durability, if room is the Forge and player can afford it. Cost scaled with how much
    durability is missing (REPAIR_COST_PER_POINT gold per point) - a lightly-worn piece costs less to fix than a fully broken one.
    A repaired piece's defence counts again automatically, since Character.armour is calculated from worn, unbroken pieces."""
    if not room.is_forge:
        return "There's nowhere to repair armour here."

    item = next((i for i in player.inventory.items if i.name.lower() == item_name.lower()), None)
    if item is None or not isinstance(item, Armour):
        return f"You don't have any armour named '{item_name}'."

    missing = item.max_durability - item.durability
    if missing == 0:
        return f"{item.display_name} doesn't need repairing."

    cost = missing * REPAIR_COST_PER_POINT
    if player.gold < cost:
        return f"Repairing {item.display_name} costs {cost} gold - you only have {player.gold}."

    player.gold -= cost
    item.durability = item.max_durability
    return f"{item.display_name} is fully repaired for {cost} gold."

def check_equippable(item_name: str, player: Player) -> str | None:
    """An error message if item_name isn't held, isn't a Weapon/Armour, or is already equipped - otherwise None. Checked before equipping so
    'equip' can never drink a potion, and never spends a combat turn re-equipping something already equipped."""
    item = next((i for i in player.inventory.items if i.name.lower() == item_name.lower()), None)
    if item is None:
        return f"No item named '{item_name}' in inventory."
    if not isinstance(item, (Weapon, Armour)):
        return f"You can't equip {item.with_article(definite=True)}."
    if item.equipped:
        return f"{item.display_name} is already equipped."
    return None

def has_unfinished_trade(ally: Ally) -> bool:
    """Whether ally offers a genuine trade (has required items AND a reward) that hasn't yet been completed. Allies like Prometheus (no reward)
    or Mentor (no required items) never count - they have nothing to trade in the first place."""
    return bool(ally.required_items) and ally.reward is not None and not ally.trade_completed

def get_uncleared_reasons(room: Room) -> list[str]:
    """Why room isn't finished yet - an empty list means it's cleared."""
    reasons = []
    if any(enemy.is_alive() and not enemy.respawns for enemy in room.enemies):
        reasons.append("enemies remain")
    if room.items:
        reasons.append("items left behind")
    if any(has_unfinished_trade(ally) for ally in room.allies):
        reasons.append("an unfinished trade")
    if "open chest" in room.interactions and CHEST_OPENED not in room.flags:
        reasons.append("a chest unopened")
    return reasons

def get_undiscovered_rooms(all_floors: dict[str, dict[str, Room]], player: Player) -> set[str]:
    """Names of unvisited rooms the player could walk into right now - one step through a usable exit from a room they've already visited.
    An exit counts as usable if it isn't item-locked, guarded, a sealed Forge shortcut or a shut story gate, and doesn't lead to a concealed
    room; only revealed exits are in room.exits, so a hidden one is never followed. Limited to one step on purpose: an adjacent room's name is already shown by the map's exit list, so this reveals
    nothing new, whereas following exits further would name rooms the player has never seen."""
    rooms_by_name = {room.name: room for rooms in all_floors.values() for room in rooms.values()}
    undiscovered : set[str] = set()
    for name in player.visited_rooms:
        room = rooms_by_name.get(name)
        if room is None:
            continue
        for direction, target in room.exits.items():
            if is_room_concealed(target, player):
                continue
            if target.name in player.visited_rooms:
                continue
            if direction in room.fast_travel_locks:
                continue
            if is_exit_locked(room, direction, player):
                continue
            if get_exit_guardian(room, direction) is not None:
                continue
            if get_story_gate(room, direction, player) is not None:
                continue
            undiscovered.add(target.name)
    return undiscovered

def room_is_clear(room: Room) -> bool:
    """Whether room has no living enemy that isn't respawning - the one definition of a 'cleared' room, shared by chests and
    apply_room_cleared_flag(). An unsolved invulnerable enemy, like Charybdis, still counts as living, so a puzzle must be solved first."""
    return not any(enemy.is_alive() and not enemy.respawns for enemy in room.enemies)

def get_uncleared_rooms(all_floors: dict[str, dict[str, Room]], player: Player) -> str:
    """List every visited room that isn't cleared yet (get_uncleared_reasons(), plus 'a decision to make' while one of its story gates is
    shut), plus every undiscovered room within one step of a visited one (see get_undiscovered_rooms()), grouped by floor. Hidden exits are
    never pinned to a room: while any remain on a floor the player has reached, the report ends with HIDDEN_WAYS_NOTE instead."""
    undiscovered = get_undiscovered_rooms(all_floors, player)
    lines = []
    for floor_key, rooms in all_floors.items():
        floor_lines = []
        for room in rooms.values():
            if room.name in player.visited_rooms:
                reasons = get_uncleared_reasons(room)
                if any(get_story_gate(room, direction, player) for direction in room.story_gates):
                    reasons = reasons + ["a decision to make"]
            elif room.name in undiscovered:
                reasons = ["undiscovered"]
            else:
                continue
            if reasons:
                floor_lines.append(f"    {room.name} - {', '.join(reasons)}")
        if floor_lines:
            lines.append(f"{floor_key.replace('_', ' ').title()}:")
            lines.extend(floor_lines)

    hidden_remaining = any(
        room.hidden_exits and not is_room_concealed(room, player)
        for floor_key, rooms in all_floors.items() if floor_key in player.visited_floors
        for room in rooms.values()
    )
    if not lines:
        if hidden_remaining:
            return f"Every room you can reach has been cleared - but {HIDDEN_WAYS_NOTE[0].lower()}{HIDDEN_WAYS_NOTE[1:]}"
        return "Nothing left to find - every room you can reach has been cleared."
    if hidden_remaining:
        lines.append(HIDDEN_WAYS_NOTE)
    return "\n".join(lines)

def deepest_floor_reached(player: Player) -> int:
    """The number of the deepest floor the player has reached - 0 if they've only been on floor 0, or nowhere."""
    reached = [int(key.removeprefix("floor_")) for key in player.visited_floors if key.startswith("floor_")]
    return max(reached, default=0)

def start_duel(name: str, room: Room, player: Player) -> str:
    """Begin a duel with the named companion in the room: they're swapped out for the Enemy their duel_enemy_factory builds, which carries a
    duel_companion link back to them, and combat starts. The duel ends in handle_enemy_defeat() on a win, or end_duel() on a loss or flee
    (combat.py) - either way the companion is returned to the room."""
    companion = next((c for c in room.companions if c.name.lower() == name.lower()), None)
    if companion is None:
        return f"There's no one named '{name}' here to challenge."
    if companion.duel_enemy_factory is None:
        return f"{companion.name} has no interest in fighting you."
    if companion.duel_won:
        return f"{companion.name} has already measured you - there's nothing left to prove."

    opponent = companion.duel_enemy_factory()
    opponent.duel_companion = companion
    opponent.duel_return_hp = player.hp
    room.remove_companion(companion)
    room.add_enemy(opponent)
    player.in_combat = True
    player.current_target = opponent
    return f"{companion.name} accepts. The duel begins.\n{opponent.description}"

def enemy_traits(enemies) -> list[str]:
    """The notable traits of one group of enemies, in TRAIT_ORDER - the analysis shared by Odysseus' advice, the Oracle's 'ask ahead' and
    Tiresias' readings. Each speaker has their own phrasing for each trait; this only decides which traits apply."""
    alive = [e for e in enemies if e.is_alive() and not e.respawns]
    fighting = [e for e in alive if not e.invulnerable]
    found = set()
    if any(e.armour >= 3 for e in fighting):
        found.add("heavy_armour")
    if any(e.melee_dodge_chance > 0 for e in fighting):
        found.add("evasive")
    if any(e.heal_amount > 0 for e in fighting):
        found.add("heals")
    if any(e.armour_pierce > 0 for e in fighting):
        found.add("pierces")
    if len(fighting) >= 3:
        found.add("numerous")
    if any(e.invulnerable for e in alive):
        found.add("puzzle")
    return [trait for trait in TRAIT_ORDER if trait in found]

def encounter_enemies(enemy, depth: int = 0) -> list:
    """The enemy plus everything its fight will bring - wave adds and later phases, built from its factories. Used when describing a floor the player
    hasn't reached, so a boss' second phase counts too. Depth-limited as a safeguard."""
    found = [enemy]
    if depth >= 3:
        return found
    for factory in enemy.next_wave_factories or []:
        found.extend(encounter_enemies(factory(), depth + 1))
    if enemy.next_phase_factory is not None:
        found.extend(encounter_enemies(enemy.next_phase_factory(), depth + 1))
    return found

def floor_traits(rooms: dict[str, Room]) -> list[str]:
    """The traits of a whole floor - each room analysed on its own (so 'numerous' means one room with many enemies, not the floor's total),
    including every phase and wave, then combined in TRAIT_ORDER."""
    found = set()
    for room in rooms.values():
        expanded = [e for enemy in room.enemies for e in encounter_enemies(enemy)]
        found.update(enemy_traits(expanded))
    return [trait for trait in TRAIT_ORDER if trait in found]

def next_floor_key(all_floors: dict[str, dict[str, Room]], player: Player) -> str | None:
    """The floor after the deepest one the player has reached, or None if they haven't reached any or there's nothing below."""
    reached = [int(key.removeprefix("floor_")) for key in player.visited_floors if key.startswith("floor_")]
    if not reached:
        return None
    candidate = f"floor_{max(reached) + 1}"
    if candidate not in all_floors:
        return None
    if all(is_room_concealed(room, player) for room in all_floors[candidate].values()):
        return None
    return candidate

def is_room_concealed(room: Room, player: Player) -> bool:
    """Whether room is still concealed from the player - see Room.concealed_until."""
    return room.concealed_until is not None and room.concealed_until not in player.story_flags

def is_exit_concealed(room: Room, direction: str, player: Player) -> bool:
    """Whether the exit in 'direction' leads to a room that's still concealed."""
    target = room.exits.get(direction)
    return target is not None and is_room_concealed(target, player)