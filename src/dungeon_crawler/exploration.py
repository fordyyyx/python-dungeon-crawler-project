"""Room and item interactions - everything outside of combat: picking up and dropping items, trading with allies,
examining surroundings, and map/movement helpers."""

from dungeon_crawler.characters import Player, Ally, Companion, Enemy
from dungeon_crawler.items import Armour, Weapon
from dungeon_crawler.world import Room

REPAIR_COST_PER_POINT = 2

def pick_up(room: Room, item_name: str, player: Player) -> str:
    """Move the named item from room into player's inventory. Returns an error message if no matching item is present."""
    for item in room.items:
        if item.name.lower() == item_name.lower():
            player.inventory.add(item)
            room.remove_item(item)
            return f"You take the {item.name}. {item.description}"
    return "That's not here."

def take_all(room: Room, player: Player) -> str:
    """Move every item in room into player's inventory, summarised on one line rather than one description per item."""
    items = room.items
    if not items:
        return "There's nothing here to take."
    for item in items:
        room.remove_item(item)
        player.inventory.add(item)
    return f"You take: {', '.join(item.name for item in items)}."

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
        equipped_names = ", ".join(item.name for item in equipped_items)
        return f"{ally.name} shakes their head. \"You'll need to unequip: {equipped_names}.\""

    if not player.has_silver_tongue:
        for name in ally.required_items:
            item = next(item for item in player.inventory.items if item.name == name)
            player.inventory.remove(item)

    player.inventory.add(ally.reward)
    ally.trade_completed = True
    result = f"{ally.name} nods, accepting each item in turn. \"You've done well.\" They hand you the {ally.reward.name}."
    if ally.post_trade_message:
        result += f"\n\n{ally.post_trade_message}"
    return result

def recruit_companion(name: str, room: Room, player: Player) -> str:
    """Recruit the named companion from room onto player's team, if player already holds every item in the companion's required_items
    (and none are currently equipped) - consumes those items on success, mirroring trade_with_ally()'s exact mechanics. Blocks with
    an error is player already has a companion (dismiss_companion() first) or if no matching companion is present."""
    if player.companion is not None:
        return f"You already have a companion, {player.companion.name}. Dismiss them first."

    companion: Companion | None = next((c for c in room.companions if c.name.lower() == name.lower()), None)
    if companion is None:
        return f"There's no one named '{name}' here to recruit."

    player_item_names = [item.name for item in player.inventory.items]
    missing = [item_name for item_name in companion.required_items if item_name not in player_item_names]

    if missing:
        return f"{companion.name} shakes their head. \"You're still missing: {', '.join(missing)}.\""

    equipped_items = [
        item for item in player.inventory.items
        if item.name in companion.required_items and item.equipped
    ]

    if equipped_items:
        equipped_names = ', '.join(item.name for item in equipped_items)
        return f"{companion.name} shakes their head. \"You'll need to unequip: {equipped_names}.\""

    for item_name in companion.required_items:
        item = next(item for item in player.inventory.items if item.name == item_name)
        player.inventory.remove(item)

    room.remove_companion(companion)
    player.companion = companion
    return f"{companion.name} joins you."

def dismiss_companion(player: Player):
    """Release player's current companion, restoring them to full HP and returning them to their home_room, Returns a message explaining
    nothing happened if player has no companion to dismiss."""
    companion = player.companion
    if companion is None:
        return "You don't have a companion to dismiss."

    companion.hp = companion.max_hp
    companion.home_room.add_companion(companion)
    player.companion = None
    return f"{companion.name} returns to {companion.home_room.name}."

def is_exit_locked(room: Room, direction: str, player: Player) -> bool:
    """Whether direction requires an item player doesn't currently hold. An exit not in locked_exits is never locked."""
    if direction not in room.locked_exits:
        return False
    required_item_name = room.locked_exits[direction]
    return required_item_name not in [item.name for item in player.inventory.items]

def get_exit_guardian(room: Room, direction: str) -> Enemy | None:
    """The first living, non-respawning enemy blocking 'direction', or None if the exit isn't guarded or nobody's left to guard it."""
    if direction not in room.guarded_exits:
        return None
    return next((e for e in room.enemies if e.is_alive() and not e.respawns), None)

def display_local_exits(room: Room, player: Player) -> str:
    """Format only the current room's own exits - shows 'Locked Door' in place of the destination name for any exit the player can't yet use."""
    if not room.exits:
        return "There are no exits from this room."
    lines = []
    for direction, target in room.exits.items():
        guardian = get_exit_guardian(room, direction)
        if is_exit_locked(room, direction, player):
            lines.append(f"{direction} -> Locked Door")
        elif guardian is not None:
            lines.append(f"{direction} -> {target.name} (guarded by {guardian.name})")
        elif direction in room.fast_travel_locks:
                    lines.append(f"{direction} -> Sealed Shortcut")
        else:
            lines.append(f"{direction} -> {target.name}")
    return "\n".join(lines)

def display_map(current_room: Room, player: Player) -> str:
    """Format every room reachable from current_room, via a recursive traversal that stops at any locked exit - unlike
    display_local_exits(), this shows the whole currently-reachable map, not just the current room's own exits."""
    visited: set[str] = set()
    lines = []

    def explore(room: Room) -> None:
        """Depth-first visit room and every room reachable from it, appending exit lines to the enclosing lines list. Recursion stops at a locked exit or an already-visited room, so this always terminates even with exit loops."""
        if room.name in visited:
            return
        visited.add(room.name)
        lines.append(f"\n{room.name}")

        unlocked_targets = []
        for direction, target in room.exits.items():
            guardian = get_exit_guardian(room, direction)
            if is_exit_locked(room, direction, player):
                lines.append(f"  {direction} -> Locked Door")
            elif guardian is not None:
                lines.append(f"  {direction} -> {target.name} (guarded by {guardian.name})")
            elif direction in room.fast_travel_locks:
                lines.append(f"{direction} -> Sealed Shortcut")
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
    are genuinely gated, reveal included, not just the flavour text. Intellect gated progress is allowed, since Intellect grows
    with every level with no cap - the guardrail is reachability, not avoidance of gating entirely."""

    if player.intellect < room.required_intellect:
        return "There's something here, but you can't quite make sense of it."

    messages = []
    if room.examine_text:
        messages.append(room.examine_text)
    else:
        messages.append("You look closer, but find nothing you hadn't already noticed.")

    revealed = room.reveal_hidden_exits()
    if revealed:
        messages.append(f"Your search reveals a hidden passage: {', '.join(revealed)}.")

    return "\n".join(messages)

def repair_item(item_name: str, player: Player, room: Room) -> str:
    """Restore a named Armour item to full durability, if room is the Forge and player can afford it. Cost scaled with how much
    durability is missing (REPAIR_COST_PER_POINT gold per point) - a lightly-worn piece costs less to fix than a fully broken one.
    Re-adds the item's defence bonus to player.armour if it had dropped to 0 (broken)."""
    if not room.is_forge:
        return "There's nowhere to repair armour here."

    item = next((i for i in player.inventory.items if i.name.lower() == item_name.lower()), None)
    if item is None or not isinstance(item, Armour):
        return f"You don't have any armour named '{item_name}'."

    missing = item.max_durability - item.durability
    if missing == 0:
        return f"{item.name} doesn't need repairing."

    cost = missing * REPAIR_COST_PER_POINT
    if player.gold < cost:
        return f"Repairing {item.name} costs {cost} gold - you only have {player.gold}."

    player.gold -= cost
    was_broken = item.durability == 0
    item.durability = item.max_durability
    if was_broken:
        player.armour += item.defence
    return f"{item.name} is fully repaired for {cost} gold."

def check_equippable(item_name: str, player: Player) -> str | None:
    """An error message if item_name isn't held, isn't a Weapon/Armour, or is already equipped - otherwise None. Checked before equipping so
    'equip' can never drink a potion, and never spends a combat turn re-equipping something already equipped."""
    item = next((i for i in player.inventory.items if i.name.lower() == item_name.lower()), None)
    if item is None:
        return f"No item named '{item_name}' in inventory."
    if not isinstance(item, (Weapon, Armour)):
        return f"You can't equip the {item.name}."
    if item.equipped:
        return f"{item.name} is already equipped."
    return None

def has_unfinished_trade(ally: Ally) -> bool:
    """Whether ally offers a genuine trade (has required items AND a reward) that hasn't yet been completed. Allies like Prometheus (no reward)
    or Mentor (no required items) never count - they have nothing to trade in the first place."""
    return bool(ally.required_items) and ally.reward is not None and not ally.trade_completed

def get_uncleared_reasons(room: Room) -> list[str]:
    """Why room isn't finished yet - an empty list means it's cleared. A hidden exit is reported vaguely, without naming a direction, so the
    command hints that a room is worth examining rather than spoiling what's there."""
    reasons = []
    if any(enemy.is_alive() and not enemy.respawns for enemy in room.enemies):
        reasons.append("enemies remain")
    if room.items:
        reasons.append("items left behind")
    if any(has_unfinished_trade(ally) for ally in room.allies):
        reasons.append("an unfinished trade")
    if room.hidden_exits:
        reasons.append("something here is worth a closer look")
    return reasons

def get_undiscovered_rooms(all_floors: dict[str, dict[str, Room]], player: Player) -> set[str]:
    """Names of unvisited rooms the player could walk into right now - one step through a usable exit from a room they've already visited.
    An exit counts as usable if it isn't item-locked, guarded, or a sealed Forge shortcut, and only revealed exits are in room.exits, so a hidden
    one is never followed. Limited to one step on purpose: an adjacent room's name is already shown by the map's exit list, so this reveals
    nothing new, whereas following exits further would name rooms the player has never seen."""
    rooms_by_name = {room.name: room for rooms in all_floors.values() for room in rooms.values()}
    undiscovered : set[str] = set()
    for name in player.visited_rooms:
        room = rooms_by_name.get(name)
        if room is None:
            continue
        for direction, target in room.exits.items():
            if target.name in player.visited_rooms:
                continue
            if direction in room.fast_travel_locks:
                continue
            if is_exit_locked(room, direction, player):
                continue
            if get_exit_guardian(room, direction) is not None:
                continue
            undiscovered.add(target.name)
    return undiscovered

def get_uncleared_rooms(all_floors: dict[str, dict[str, Room]], player: Player) -> str:
    """List every visited room that isn't cleared yet, plus every undiscovered room within one step of a visited one (see
    get_undiscovered_rooms()), grouped by floor."""
    undiscovered = get_undiscovered_rooms(all_floors, player)
    lines = []
    for floor_key, rooms in all_floors.items():
        floor_lines = []
        for room in rooms.values():
            if room.name in player.visited_rooms:
                reasons = get_uncleared_reasons(room)
            elif room.name in undiscovered:
                reasons = ["undiscovered"]
            else:
                continue
            if reasons:
                floor_lines.append(f"    {room.name} - {', '.join(reasons)}")
        if floor_lines:
            lines.append(f"{floor_key.replace('_', ' ').title()}:")
            lines.extend(floor_lines)
    return "\n".join(lines) if lines else "Every room you've visited has been cleared."