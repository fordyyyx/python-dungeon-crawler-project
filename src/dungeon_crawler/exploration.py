"""Room and item interactions - everything outside of combat: picking up and dropping items, trading with allies,
examining surroundings, and map/movement helpers."""

from dungeon_crawler.characters import Player, Ally
from dungeon_crawler.world import Room


def pick_up(room: Room, item_name: str, player: Player) -> str:
    for item in room.items:
        if item.name.lower() == item_name.lower():
            player.inventory.add(item)
            room.remove_item(item)
            return f"You take the {item.name}. {item.description}"
    return "That's not here."

def trade_with_ally(ally: Ally, player: Player):
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
        equipped_names = ", ".join(item.name for item in equipped_items)
        return f"{ally.name} shakes their head. \"You'll need to unequip: {equipped_names}.\""

    for name in ally.required_items:
        item = next(item for item in player.inventory.items if item.name == name)
        player.inventory.remove(item)

    player.inventory.add(ally.reward)
    ally.trade_completed = True
    result = f"{ally.name} nods, accepting each item in turn. \"You've done well.\" They hand you the {ally.reward.name}."
    if ally.post_trade_message:
        result += f"\n\n{ally.post_trade_message}"
    return result

def is_exit_locked(room: Room, direction: str, player: Player) -> bool:
    if direction not in room.locked_exits:
        return False
    required_item_name = room.locked_exits[direction]
    return required_item_name not in [item.name for item in player.inventory.items]

def display_local_exits(room: Room, player: Player) -> str:
    if not room.exits:
        return "There are no exits from this room."
    lines = []
    for direction, target in room.exits.items():
        if is_exit_locked(room, direction, player):
            lines.append(f"{direction} -> Locked Door")
        else:
            lines.append(f"{direction} -> {target.name}")
    return "\n".join(lines)

def display_map(current_room: Room, player: Player) -> str:
    visited: set[str] = set()
    lines = []

    def explore(room: Room) -> None:
        if room.name in visited:
            return
        visited.add(room.name)
        lines.append(f"\n{room.name}")

        unlocked_targets = []
        for direction, target in room.exits.items():
            if is_exit_locked(room, direction, player):
                lines.append(f"  {direction} -> Locked Door")
            else:
                lines.append(f"  {direction} -> {target.name}")
                unlocked_targets.append(target)

        for target in unlocked_targets:
            explore(target)

    explore(current_room)
    return "\n".join(lines)

def find_floor_for_room(room: Room, all_floors: dict[str, dict[str, Room]]) -> str | None:
    for floor_name, rooms in all_floors.items():
        if room.name in rooms:
            return floor_name
    return None

def handle_examine(room: Room, player: Player) -> str:
    """Show a room's extra flavour text and reveal any hidden exits ot has."""
    messages = []
    if room.examine_text:
        if room.required_intellect <= player.intellect:
            messages.append(room.examine_text)
        else:
            messages.append("There's something here, but you can't quite make sense of it.")
    else:
        messages.append("You look closer, but find nothing you hadn't already noticed.")

    revealed = room.reveal_hidden_exits()
    if revealed:
        messages.append(f"Your search reveals a hidden passage: {', '.join(revealed)}.")

    return "\n".join(messages)