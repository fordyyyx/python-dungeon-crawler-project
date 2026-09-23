"""Assembles every floor into one Map via build_world(). Seperated from __init__.py to avoid name collision with dungeon_crawler.world (Room/Map)
- purely a naming convenience, not a meaningful split."""

from dungeon_crawler.world import Room, Map
from .floor_0 import build_floor_0
from .floor_1 import build_floor_1
from .floor_2 import build_floor_2
from .floor_3 import build_floor_3
from .floor_4 import build_floor_4
from .floor_5 import build_floor_5
from .floor_6 import build_floor_6
from .floor_7 import build_floor_7
from .floor_8 import build_floor_8
from .floor_9 import build_floor_9
from .dev_content import build_blank_test_room

def build_world() -> tuple[Map, Room, dict[str, dict[str, Room]]]:
    """Assemble every floor into one Map, wire the inter-floor descend/ascend exits between them, and add the dev-only test room. Returns (the full map, floor 0's starting room, every floor's rooms keyed by floor name then room name)."""
    dungeon = Map()

    floor_0_start, floor_0_rooms = build_floor_0()
    floor_1_start, floor_1_rooms = build_floor_1()
    floor_2_start, floor_2_rooms = build_floor_2()
    floor_3_start, floor_3_rooms = build_floor_3()
    floor_4_start, floor_4_rooms = build_floor_4()
    floor_5_start, floor_5_rooms = build_floor_5()
    floor_6_start, floor_6_rooms = build_floor_6()
    floor_7_start, floor_7_rooms = build_floor_7()
    floor_8_start, floor_8_rooms = build_floor_8()
    floor_9_start, floor_9_rooms = build_floor_9()

    floor_0_rooms["Chamber of Chiron"].connect("descend", floor_1_rooms["Cave Entrance"])
    floor_1_rooms["Styx Crossing"].connect("descend", floor_2_rooms["Library of Athena"])
    floor_2_rooms["Library of Athena"].connect("ascend", floor_1_rooms["Styx Crossing"])
    floor_2_rooms["Forge of Prometheus"].connect("descend", floor_3_rooms["Bony Crypt"])
    floor_3_rooms["Bony Crypt"].connect("ascend", floor_2_rooms["Forge of Prometheus"])
    floor_3_rooms["Overgrown Forest"].connect("descend", floor_4_rooms["Labyrinth of the Minotaur"])
    floor_3_rooms["Overgrown Forest"].guard_exit("descend")
    floor_4_rooms["Labyrinth of the Minotaur"].connect("ascend", floor_3_rooms["Overgrown Forest"])
    floor_4_rooms["Lair of Medusa"].connect("descend", floor_5_rooms["Shadow of Army Camp"])
    floor_4_rooms["Lair of Medusa"].guard_exit("descend")
    floor_5_rooms["Shadow of Army Camp"].connect("ascend", floor_4_rooms["Lair of Medusa"])
    floor_5_rooms["Shadow of Pylos"].connect("descend", floor_6_rooms["Bright Cave"])
    floor_6_rooms["Bright Cave"].connect("ascend", floor_5_rooms["Shadow of Pylos"])
    floor_6_rooms["Bedchamber of Odysseus"].connect("descend", floor_7_rooms["Chamber of the Oracle"])
    floor_7_rooms["Chamber of the Oracle"].connect("ascend", floor_6_rooms["Bedchamber of Odysseus"])
    floor_7_rooms["Bedchamber of Persephone"].connect("descend", floor_8_rooms["Gate of Cerberus"])
    floor_8_rooms["Gate of Cerberus"].connect("ascend", floor_7_rooms["Bedchamber of Persephone"])
    floor_8_rooms["Hall of Hades"].connect("descend", floor_9_rooms["Tartarus"])
    floor_9_rooms["Tartarus"].connect("ascend", floor_8_rooms["Hall of Hades"])

    floor_3_rooms["Prayer Room"].connect("forge", floor_2_rooms["Forge of Prometheus"])
    floor_2_rooms["Forge of Prometheus"].connect("prayer room", floor_3_rooms["Prayer Room"])
    floor_2_rooms["Forge of Prometheus"].lock_fast_travel_exit("prayer room")
    floor_3_rooms["Prayer Room"].register_fast_travel_activation("forge", floor_2_rooms["Forge of Prometheus"], "prayer room")

    floor_4_rooms["Stony Lair"].connect("forge", floor_2_rooms["Forge of Prometheus"])
    floor_2_rooms["Forge of Prometheus"].connect("stony lair", floor_4_rooms["Stony Lair"])
    floor_2_rooms["Forge of Prometheus"].lock_fast_travel_exit("stony lair")
    floor_4_rooms["Stony Lair"].register_fast_travel_activation("forge", floor_2_rooms["Forge of Prometheus"], "stony lair")

    floor_4_rooms["Maze of Pillars"].connect("forge", floor_2_rooms["Forge of Prometheus"])
    floor_2_rooms["Forge of Prometheus"].connect("maze of pillars", floor_4_rooms["Maze of Pillars"])
    floor_2_rooms["Forge of Prometheus"].lock_fast_travel_exit("maze of pillars")
    floor_4_rooms["Maze of Pillars"].register_fast_travel_activation("forge", floor_2_rooms["Forge of Prometheus"], "maze of pillars")

    all_floors = {
        "floor_0": floor_0_rooms,
        "floor_1": floor_1_rooms,
        "floor_2": floor_2_rooms,
        "floor_3": floor_3_rooms,
        "floor_4": floor_4_rooms,
        "floor_5": floor_5_rooms,
        "floor_6": floor_6_rooms,
        "floor_7": floor_7_rooms,
        "floor_8": floor_8_rooms,
        "floor_9": floor_9_rooms,
    }

    for floor_key, floor_rooms in all_floors.items():
        for room in floor_rooms.values():
            dungeon.add_room(room)

    dev_test_room = build_blank_test_room()
    dungeon.add_room(dev_test_room)

    return dungeon, floor_0_start, all_floors