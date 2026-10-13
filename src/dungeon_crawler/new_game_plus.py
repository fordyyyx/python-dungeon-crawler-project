"""Starting a New Game+ cycle. The character carries over exactly as they are - level, skills and stats, with one-off boons stacking each cycle -
along with every companion they've recruited, and hardcore. Gear and upgrades, gold, trophies, story flags, and the world are left behind. Each
cycle adds a stacking multiplier to enemy HP and attack, and gets a new run seed."""

import random

from dungeon_crawler.content import build_world
from dungeon_crawler.content.floor_2 import HARDCORE, PROMETHEUS_OFFER_MADE
from dungeon_crawler.difficulty import scale_world

def _all_rooms(all_floors):
    return [room for floor_rooms in all_floors.values() for room in floor_rooms.values()]

def _find_room(all_floors, name):
    return next((room for room in _all_rooms(all_floors) if room.name == name), None)

def _floor_of(all_floors, room) -> str | None:
    return next((key for key, rooms in all_floors.items() if room.name in rooms), None)

def _carried_companions(old_floors, player) -> list:
    """Every recruited companion from the old world - in the party, or waiting in a room - restored to full health with no lingering effects."""
    carried = []
    if player.companion is not None:
        carried.append(player.companion)
    for room in _all_rooms(old_floors):
        for companion in room.companions:
            if companion.name in player.recruited_companions and companion is not player.companion:
                carried.append(companion)
    for companion in carried:
        companion.hp = companion.max_hp
        companion.active_effects = []
    return carried

def _strip_gear(player) -> None:
    """Unequip everything properly - so equipping's stat changes are undone - then empty the inventory."""
    for item in list(player.inventory.items):
        if item.equipped:
            item.unequip(player)
        player.inventory.remove(item)

def start_new_game_plus(player, old_floors):
    """Begin the next cycle. Returns (world, all_floors, starting room). The player object carries over, reset for a new run; the world is built
    fresh and scaled for the new cycle on the next command, by ensure_world_scaled()."""
    carried = _carried_companions(old_floors, player)

    _strip_gear(player)
    player.gold = 0
    player.hp = player.max_hp
    player.active_effects = []
    player.in_combat = False
    player.current_target = None
    player.seen_lines = set()
    player.ng_plus_cycle += 1
    player.run_seed = random.randrange(2 ** 31)
    player.new_game_plus_requested = False
    player.story_flags = {HARDCORE, PROMETHEUS_OFFER_MADE} if HARDCORE in player.story_flags else set()

    world, start, all_floors = build_world()

    carried_names = {companion.name for companion in carried}
    for room in _all_rooms(all_floors):
        for companion in list(room.companions):
            if companion.name in carried_names:
                room.remove_companion(companion)

    for companion in carried:
        home_name = companion.new_game_plus_home or companion.home_room.name
        companion.home_room = _find_room(all_floors, home_name) or start
        if companion is not player.companion:
            companion.home_room.add_companion(companion)
        if companion.new_game_plus_effect is not None:
            companion.new_game_plus_effect(player, all_floors)

    scale_world(world, player.difficulty, player.ng_plus_cycle)

    player.visited_rooms = {start.name}
    start_floor = _floor_of(all_floors, start)
    player.visited_floors = {start_floor} if start_floor else set()

    return world, all_floors, start