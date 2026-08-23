from dungeon_crawler.world import Room, Map
from dungeon_crawler.items import Item, Weapon, Armour, Consumable, QuestItem
from dungeon_crawler.characters import Enemy, Player, Ally

def create_skeleton_warrior() -> Enemy:
    """Create a skeleton warrior enemy"""
    return Enemy(
        name="Skeleton Warrior", 
        hp=8,
        attack_damage=3,
        armour=0,
        description="Bones held together by little more than old habit, still gripping a rusted blade with mechanical resolve.",
        )

def create_minotaur() -> Enemy:
    return Enemy(
        name="Minotaur",
        hp=25,
        attack_damage=8,
        armour=2,
        loot=[create_bronze_xiphos()],
        description="Massive and bull-headed, it turns toward you with a snort that shakes dust from the walls.",
    )

def create_hades() -> Enemy:
    return Enemy(
        name="Hades",
        hp=60,
        attack_damage=15,
        armour=5,
        loot=[create_ambrosia()],
        description="He doesn't rise from the throne immediately — he doesn't need to.",
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

def create_chiron() -> Ally:
    return Ally(
        name="Chiron",
        description="Half man, half horse, entirely patient — he's trained more heroes than he can easily count, and it shows.",
        hint=("The old centaur looks up as you enter, unsurprised. "
            "\"Another one sent down by the gods, then. Good. The Underworld never runs short of monsters, "
            "only ever short of heroes who know what they're doing.\"\n\n"
            "He gestures to the doorways around the chamber.\n\n"
            "\"Before you go anywhere, learn to move. This chamber has four ways out — "
            "north, east, south, and west. Type the direction, and you'll go there. "
            "Try each one. See what waits behind each door, then come back and tell me what you've learned.\""),
        hint_complete=(
            "\"You've gathered everything, then? Good.\" "
            "He looks over the sword, the shield, the dummy's head, and the token from his old friend. "
            "\"Type 'trade' and I'll see what you've brought me.\""),
        required_items=["Wooden Sword", "Wooden Shield", "Dummy Head", "Mentor's Token"],
        items=[]
    )

def create_training_dummy() -> Enemy:
    return Enemy(
        name="Training Dummy",
        hp=5,
        description="Straw and old rope, bolted to the floor. It has never once landed a real hit, and it isn't about to start now.",
        armour=0,
        loot=[create_dummy_head()]
    )

def create_wooden_sword() -> Weapon:
    return Weapon(
        name="Wooden Sword",
        description="Blunt, splintered, and entirely harmless to anyone but a straw dummy — exactly as intended.",
        damage=1
    )

def create_wooden_shield() -> Armour:
    return Armour(
        name="Wooden Shield",
        description="Warped and dry-rotted at the edges, but it'll turn aside a training blow well enough.",
        defence=1
    )

def create_mentor() -> Ally:
    return Ally(
        name="Mentor",
        description="He nods once in greeting, the kind of nod that says he's seen a lot of hopefuls pass through here.",
        hint="\"You've got the sword and shield now, I take it. Good.\" "
            "He tilts his head toward the main chamber. "
            "\"That's all Chiron needs to see. Go back to him, hand over what you've collected, "
            "and he'll give you Charon's Coin in return — you'll need it to cross the Styx.\"",
        items=[create_mentors_token()],
    )

def create_dummy_head() -> QuestItem:
    return QuestItem(
        name="Dummy Head",
        description="A straw-stuffed head, still faintly dented from your practice blows — proof enough for Chiron that the lesson's been learned.",
    )

def create_charons_coin() -> QuestItem:
    return QuestItem(
        name="Charon's Coin",
        description="Cold and unnaturally heavy for its size — the ferryman won't so much as glance at you without it."
    )

def create_mentors_token() -> QuestItem:
    return QuestItem(
        name="Mentor's Token",
        description="A small carved token, worn smooth — Mentor's simple way of saying you've earned his approval."
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
    chamber_of_chiron.add_ally(create_chiron())
    chamber_of_chiron_south.add_enemy(create_training_dummy())
    chamber_of_chiron_north.add_item(create_wooden_sword())
    chamber_of_chiron_east.add_item(create_wooden_shield())
    chamber_of_chiron_west.add_ally(create_mentor())

    """Lock rooms"""
    chamber_of_chiron.lock_exit("east", "Wooden Sword")
    chamber_of_chiron.lock_exit("south", "Wooden Shield")
    chamber_of_chiron.lock_exit("west", "Dummy Head")

    return dungeon, entrance