from dungeon_crawler.world import Room, Map
from dungeon_crawler.items import Item, Weapon, Armour
from dungeon_crawler.characters import Enemy, Player

def build_world() -> tuple[Map, Room]:
    """Build the rooms"""
    entrance = Room("Cave Entrance", "")
    styx_crossing = Room("Styx Crossing", "")
    library_of_athena = Room("Library of Athena", "")
    armoury_of_ares = Room("Armoury of Ares", "")
    hall_of_hades = Room("Hall of Hades", "")
    sunken_vault = Room("Sunken Vault", "")

    """Connect the rooms"""
    entrance.connect("north", styx_crossing)
    styx_crossing.connect("south", entrance)
    entrance.connect("south", sunken_vault)
    sunken_vault.connect("north", entrance)
    styx_crossing.connect("east", library_of_athena)
    library_of_athena.connect("west", styx_crossing)
    styx_crossing.connect("west", armoury_of_ares)
    armoury_of_ares.connect("east", styx_crossing)
    styx_crossing.connect("north", hall_of_hades)
    hall_of_hades.connect("south", styx_crossing)

    """Build the connected dungeon map"""
    dungeon = Map()
    for room in (entrance, styx_crossing, library_of_athena, armoury_of_ares, hall_of_hades, sunken_vault):
        dungeon.add_room(room)

    return dungeon, entrance