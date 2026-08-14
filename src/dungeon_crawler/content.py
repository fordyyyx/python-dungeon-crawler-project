from dungeon_crawler.world import Room, Map
from dungeon_crawler.items import Item, Weapon, Armour, Consumable
from dungeon_crawler.characters import Enemy, Player

def create_skeleton_warrior() -> Enemy:
    """Create a skeleton warrior enemy"""
    return Enemy(
        name="Skeleton Warrior", 
        hp=8,
        attack_damage=3,
        armour=0,
        )

def create_minotaur() -> Enemy:
    return Enemy(
        name="Minotaur",
        hp=25,
        attack_damage=8,
        armour=2,
        loot=[create_bronze_xiphos()],
    )

def create_hades() -> Enemy:
    return Enemy(
        name="Hades",
        hp=60,
        attack_damage=15,
        armour=5,
        loot=[create_ambrosia()],
    )

def create_bronze_xiphos() -> Weapon:
    return Weapon(
        name="Bronze Xiphos",
        description="A short, leaf-bladed sword - favoured by soldiers who valued speed over reach.",
        damage=3,
    )

def create_spear_of_ares() -> Weapon:
    return Weapon(
        name="Spear of Ares",
        damage=8,
        description="Bronze-tipped and still warm, as if recently thrown in anger.",
    )

def create_aegis_fragment() -> Armour:
    return Armour(
        name="Shield of Aegis (fragment)",
        defence=2,
        description="A shard of bronze etched with a single unblinking eye.",
    )

def create_ambrosia() -> Consumable:
    return Consumable(
        name="Vial of Ambrosia",
        heal_amount=20,
        description="Golden and faintly humming - mortal hands were never meant to hold this.",
    )

def build_world() -> tuple[Map, Room]:
    """Build the rooms"""
    entrance = Room("Cave Entrance", "A jagged fissure in the hillside breathes cold air from below; the last daylight fades behind you as you descend.")
    styx_crossing = Room("Styx Crossing", "Black water laps against a crumbling stone landing; something pale drifts just beneath the surface.")
    library_of_athena = Room("Library of Athena", "Towering shelves of scrolls creak under their own weight; an owl watches from the rafters, unblinking.")
    armoury_of_ares = Room("Armoury of Ares", "Racks of corroded bronze weapons line the walls, still faintly warm to the touch.")
    hall_of_hades = Room("Hall of Hades", "The chamber opens into a vast black hall lit by pale fire, a throne of bone waits at its centre.")
    sunken_vault = Room("Sunken Vault", "Half-flooded and littered with old offerings, this side chamber was clearly sealed off for a reason.")

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

    """Add enemies and items to rooms"""
    sunken_vault.add_enemy(create_skeleton_warrior)
    sunken_vault.add_item(create_ambrosia)
    armoury_of_ares.add_item(create_bronze_xiphos)
    library_of_athena.add_item(create_aegis_fragment)
    hall_of_hades.add_enemy(create_hades)

    return dungeon, entrance