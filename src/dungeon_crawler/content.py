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
    chamber_of_chiron = Room("Chamber of Chiron", "A wide training hall carved into the hillside, weapon racks and practice rings arranged with military precision. Chiron waits at the centre, patient as ever.")
    chamber_of_chiron_north = Room("Chamber of Chiron (North)", "A quiet alcove lined with old scrolls on swordplay and stance. Dust motes drift in a shaft of light from somewhere above.")
    chamber_of_chiron_east = Room("Chamber of Chiron (East)", "A narrow training yard, sand-floored and scarred with the marks of countless practice bouts.")
    chamber_of_chiron_south = Room("Chamber of Chiron (South)", "A straw-stuffed dummy stands bolted to the floor, dented from years of use.")
    chamber_of_chiron_west = Room("Chamber of Chiron (West)", "A small resting nook with a low bench, where those who've trained here catch their breath before what comes next.")

    """Connect the rooms"""
    chamber_of_chiron.connect("north", chamber_of_chiron_north)
    chamber_of_chiron.connect("east", chamber_of_chiron_east)
    chamber_of_chiron.connect("south", chamber_of_chiron_south)
    chamber_of_chiron.connect("west", chamber_of_chiron_west)
    chamber_of_chiron_north.connect("south", chamber_of_chiron)
    chamber_of_chiron_east.connect("west", chamber_of_chiron)
    chamber_of_chiron_south.connect("north", chamber_of_chiron)
    chamber_of_chiron_west.connect("east", chamber_of_chiron)

    """Build the connected dungeon map"""
    dungeon = Map()
    for room in (chamber_of_chiron, chamber_of_chiron_north, chamber_of_chiron_east, chamber_of_chiron_south, chamber_of_chiron_west):
        dungeon.add_room(room)
    entrance = chamber_of_chiron

    """Add enemies and items to rooms"""


    return dungeon, entrance