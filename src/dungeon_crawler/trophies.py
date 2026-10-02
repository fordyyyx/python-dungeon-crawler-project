"""Placing trophies in the Trophy Room of Zeus. Each placed trophy is removed from the inventory and recorded in the room's placed_trophies; reaching
a milestone count runs that milestone's reward, once, recorded in the room's flags."""

from dungeon_crawler.items import Trophy

TROPHY_ROOM_COMPLETE = "trophy_room_complete"

def describe_plinths(room) -> str:
    """Every plinth in the room - a placed trophy on its plinth, or an empty plinth with its clue."""
    lines = [f"Trophies placed: {len(room.placed_trophies)} of {len(room.trophy_plinths)}."]
    for name, clue in room.trophy_plinths:
        lines.append(f"  - {name}" if name in room.placed_trophies else f"  - (empty) {clue}")
    return "\n".join(lines)

def _wanted(room, item) -> bool:
    return isinstance(item, Trophy) and item.name in {name for name, _ in room.trophy_plinths} and item.name not in room.placed_trophies

def _reach_milestones(room, player) -> list[str]:
    """Run every milestone now reached for the first time, in order."""
    messages = []
    for count in sorted(room.trophy_milestones):
        flag = f"trophy_milestone:{count}"
        if len(room.placed_trophies) >= count and flag not in room.flags:
            room.flags.add(flag)
            messages.append(room.trophy_milestones[count](player))
    return messages

def place_trophies(item_name: str, room, player) -> str:
    """Place one named trophy, or every trophy the player carries with 'all'. Outside the Trophy Room, refuses without naming it, so it never gives
    away the hidden room."""
    if not room.is_trophy_room:
        return "There's nowhere here worthy of it."
    if item_name == "all":
        to_place = [item for item in player.inventory.items if _wanted(room, item)]
        if not to_place:
            return "You have no trophies to place."
    else:
        item = next((i for i in player.inventory.items if i.name.lower() == item_name.lower()), None)
        if item is None:
            return f"No item named '{item_name}' in inventory."
        if not _wanted(room, item):
            return f"{item.with_article(definite=True, capitalise=True)} doesn't belong here."
        to_place = [item]

    lines = []
    for item in to_place:
        player.inventory.remove(item)
        room.placed_trophies.add(item.name)
        lines.append(f"You set {item.with_article(definite=True)} on its plinth.")
    lines.extend(_reach_milestones(room, player))
    lines.append(f"(Trophies placed: {len(room.placed_trophies)} of {len(room.trophy_plinths)}.)")
    return "\n".join(lines)