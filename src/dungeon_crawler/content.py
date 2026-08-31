from dungeon_crawler.world import Room, Map
from dungeon_crawler.items import Item, Weapon, Armour, Consumable, QuestItem, SkillPointReward
from dungeon_crawler.characters import Enemy, Player, Ally

ANCESTRIES: dict[str, dict] = {
    "basic":    {"label": "No lineage",                 "attack": 3, "armour": 1, "hp": 20, "bonus_skill_point": False},
    "ares":     {"label": "Descendant of Ares",         "attack": 5, "armour": 1, "hp": 19, "bonus_skill_point": False},
    "athena":   {"label": "Descendant of Athena",       "attack": 4, "armour": 3, "hp": 20, "bonus_skill_point": False},
    "hermes":   {"label": "Descendant of Hermes",       "attack": 4, "armour": 1, "hp": 22, "bonus_skill_point": False},
    "poseidon": {"label": "Descendant of Poseidon",     "attack": 2, "armour": 5, "hp": 19, "bonus_skill_point": False},
    "achilles": {"label": "Descendant of Achilles",     "attack": 6, "armour": 1, "hp": 16, "bonus_skill_point": False},
    "odysseus": {"label": "Descendant of Odysseus",     "attack": 3, "armour": 1, "hp": 20, "bonus_skill_point": True},
    "atalanta": {"label": "Descendant of Atalanta",     "attack": 5, "armour": 1, "hp": 20, "bonus_skill_point": False},
    "medusa":   {"label": "Descendant of Medusa",       "attack": 2, "armour": 4, "hp": 19, "bonus_skill_point": False},
    "minotaur": {"label": "Descendant of the Minotaur", "attack": 6, "armour": 0, "hp": 21, "bonus_skill_point": False},
    "cyclops":  {"label": "Descendant of a Cyclops",    "attack": 3, "armour": 0, "hp": 25, "bonus_skill_point": False},
}

def create_skeleton_warrior() -> Enemy:
    """Create a skeleton warrior enemy"""
    return Enemy(
        name="Skeleton Warrior", 
        hp=8,
        attack_damage=3,
        armour=0,
        loot=[create_small_healing_potion()],
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
        damage=6,
        description="Bronze-tipped and perfectly balanced - it feels less like you're holding a weapon, and more like it's holding you steady",
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
        reward=create_charons_coin(),
        post_trade_message = "You feel ready. Type 'descend' when you're prepared to leave this place behind.",
        items=[]
    )

def create_training_dummy() -> Enemy:
    return Enemy(
        name="Training Dummy",
        hp=5,
        attack_damage=0,
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
        hint=(
            "\"You've got the sword and shield now, I take it. Good.\" "
            "He reaches into his coat and produces a small, worn token. "
            "\"Here — take this. Say 'take mentor's token from mentor', and it's yours. "
            "Bring it to Chiron along with the rest, and he'll see you're ready.\"\n\n"
            "He adds, almost as an afterthought: \"And should you ever pick up more than you can "
            "carry, 'drop' works just as well as 'take' — no shame in travelling light.\""
        ),
        required_items=[],
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

def create_wounded_soldier() -> Ally:
    return Ally(
        name="Wounded Soldier",
        description="Bandaged and pale, but still sharp-eyed — clearly more useful than his condition suggests.",
        hint=(
            "\"Take these, if you're heading further down,\" he says, nodding at a Bronze Xiphos, a Bronze Breastplate "
            "and a Small Healing Potion beside him. \"I won't need them where I'm going. "
            "Say 'take <item> from wounded soldier' for each - you'll want all three."
        ),
        hint_complete="",
        required_items=[],
        items=[create_bronze_xiphos(), create_bronze_breastplate(), create_small_healing_potion()],
    )

def create_charon() -> Ally:
    return Ally(
        name="Charon",
        description="He holds out one weathered hand, saying nothing, waiting for the coin he already knows you'll need.",
        hint=(
            "\"You have the coin. Good.\" His voice is dry, unhurried. "
            "\"Cross when you're ready — the water won't wait for anyone, but it won't rush you either.\""
        ),
    )

def create_bronze_breastplate() -> Armour:
    return Armour(
        name="Bronze Breastplate",
        defence=2,
        description="Dented and a size too large, but the bronze is sound - better than the wood you started with, if only just."
    )

def create_small_healing_potion() -> Consumable:
    return Consumable(
        name="Small Healing Potion",
        heal_amount=5,
        description="A cloudy vial, more herb than magic - enough to steady a shaking hand, not much more."
    )

def create_athena() -> Ally:
    return Ally(
        name="Athena",
        description="Calm, measured, and faintly amused — as if she already knows exactly how this ends.",
        hint="",
        hint_complete="",
        required_items = ["Centaur's Broken Bow"],
        items=[],
        reward=create_breastplate_of_athena()
    )

def create_ares() -> Ally:
    return Ally(
        name="Ares",
        description="He barely looks up from sharpening a blade, though he's clearly aware of every move you make.",
        hint="",
        hint_complete="",
        required_items=["Cyclops' Eye"],
        items=[],
        reward=create_spear_of_ares()
    )

def create_hermes() -> Ally:
    return Ally(
        name="Hermes",
        description="Never quite still, halfway through some errand even while talking to you.",
        hint="",
        hint_complete="",
        required_items=["Skeleton Bone"],
        reward=create_hermes_favour(),
        items=[]
    )

def create_prometheus() -> Ally:
    return Ally(
        name="Prometheus",
        description="Chained but unbroken, watching you with the weary patience of someone who's paid dearly for helping before.",
        hint="",
        hint_complete="",
        required_items=[],
        items=[]
    )

def create_cyclops_eye() -> QuestItem:
    return QuestItem(
        name="Cyclops' Eye",
        description="Still faintly warm and unsettlingly heavy for its size - Ares will know exactly what this cost you."
    )

def create_breastplate_of_athena() -> Armour:
    return Armour(
        name="Breastplate of Athena",
        description="Cool to the touch even in the deepest heat, etched with an owl that seems to watch whichever way danger comes from.",
        defence=4,
    )

def create_centaurs_broken_bow() -> QuestItem:
    return QuestItem(
        name="Centaur's Broken Bow",
        description="Snapped clean at the riser - proof you closed the distance before it ever got a clean shot off."
    )

def create_hermes_favour() -> SkillPointReward:
    return SkillPointReward(
        name="Favour of Hermes",
        description="Quick, light, and gone before you've noticed - much like the god who gave it.",
        points = 1
    )

def build_blank_test_room() -> Room:
    """A single, deliberately empty room for dev testing - not connected to anything via exits, only ever reached by 
    'dev teleport dev test room'. Nothing pre-populated; use dev spawn / dev add once inside. """
    return Room(
        "Dev Test Room",
        "A featureless void, useful for exactly nothing except testing things in isolation."
    )

def build_floor_0() -> tuple[Room, dict[str, Room]]:
    chamber_of_chiron = Room("Chamber of Chiron", "A wide training hall carved into the hillside, weapon racks and practice rings arranged with "
        "military precision. Chiron waits at the centre, patient as ever. He watches you a moment, "
        "waiting — say 'talk' if you want to know why you're here.")
    chamber_of_chiron_north = Room("Chamber of Chiron (North)", "A quiet alcove lined with old scrolls on swordplay and stance. Dust motes drift in a shaft "
        "of light from somewhere above. A wooden sword rests against the wall. "
        "Chiron's voice follows you in: \"Say 'take wooden sword' to pick it up, then 'use wooden sword' "
        "to ready it properly.\"")
    chamber_of_chiron_east = Room("Chamber of Chiron (East)", "A narrow training yard, sand-floored and scarred with the marks of countless practice bouts. "
        "A wooden shield leans against a post. \"Use it the same way as the sword,\" Chiron calls. "
        "\"And if you ever need it off your arm again, 'unequip wooden shield' does the job.\"")
    chamber_of_chiron_south = Room("Chamber of Chiron (South)", "A straw-stuffed dummy stands bolted to the floor, dented from years of use. "
        "Chiron's voice calls from behind you: \"Go on — type 'attack' and show me what you've got.\"")
    chamber_of_chiron_west = Room("Chamber of Chiron (West)", "A small resting nook with a low bench, where those who've trained here catch their breath before what comes next.")
    
    chamber_of_chiron.connect("north", chamber_of_chiron_north)
    chamber_of_chiron.connect("east", chamber_of_chiron_east)
    chamber_of_chiron.connect("south", chamber_of_chiron_south)
    chamber_of_chiron.connect("west", chamber_of_chiron_west)
    chamber_of_chiron_north.connect("south", chamber_of_chiron)
    chamber_of_chiron_east.connect("west", chamber_of_chiron)
    chamber_of_chiron_south.connect("north", chamber_of_chiron)
    chamber_of_chiron_west.connect("east", chamber_of_chiron)

    chamber_of_chiron.add_ally(create_chiron())
    chamber_of_chiron_south.add_enemy(create_training_dummy())
    chamber_of_chiron_north.add_item(create_wooden_sword())
    chamber_of_chiron_east.add_item(create_wooden_shield())
    chamber_of_chiron_west.add_ally(create_mentor())

    chamber_of_chiron.lock_exit("east", "Wooden Sword")
    chamber_of_chiron.lock_exit("south", "Wooden Shield")
    chamber_of_chiron.lock_exit("west", "Dummy Head")
    chamber_of_chiron.lock_exit("descend", "Charon's Coin")

    return chamber_of_chiron, {
        room.name: room for room in (
            chamber_of_chiron, chamber_of_chiron_north, chamber_of_chiron_east, chamber_of_chiron_south, chamber_of_chiron_west,
        )
    }

def build_floor_1() -> tuple[Room, dict[str, Room]]:
    cave_entrance = Room("Cave Entrance", "A jagged fissure in the hillside breathes cold air from below; the last daylight fades behind you as you descend.")

    styx_crossing = Room("Styx Crossing", "Black water laps against a crumbling stone landing; something pale drifts just beneath the surface.")
    fields_of_asphodel = Room("Fields of Asphodel", "An endless grey meadow beneath a colourless sky, where the ordinary dead wander without purpose or memory.")
    sunken_vault = Room("Sunken Vault", "Half-flooded and littered with old offerings, this side chamber was clearly sealed off for a reason.")

    cave_entrance.connect("descend", styx_crossing)
    styx_crossing.connect("ascend", cave_entrance)
    styx_crossing.connect("east", fields_of_asphodel)
    fields_of_asphodel.connect("west", styx_crossing)
    styx_crossing.connect("down", sunken_vault)
    sunken_vault.connect("up", styx_crossing)

    cave_entrance.add_ally(create_wounded_soldier())
    styx_crossing.add_ally(create_charon())
    sunken_vault.add_enemy(create_skeleton_warrior())

    return cave_entrance, {
        room.name: room for room in (cave_entrance, styx_crossing, fields_of_asphodel, sunken_vault)
    }

def build_floor_2() -> tuple[Room, dict[str, Room]]:
    library_of_athena = Room(name="Library of Athena", description="Towering shelves of scrolls creak under their own weight; an owl watches from the rafters, unblinking.")
    armoury_of_ares = Room(name="Armoury of Ares", description="Racks of corroded bronze weapons line the walls, still faintly warm to the touch.")
    hall_of_hermes = Room(name="Hall of Hermes", description="A cluttered waypoint stacked with parcels and letters never delivered, sandals of every size hung along one wall.")
    forge_of_prometheus = Room(name="Forge of Prometheus", description="The air shimmers with heat from a fire that never seems to go out, chained tools scattered across a worn anvil.")

    library_of_athena.connect("west", armoury_of_ares)
    library_of_athena.connect("south", hall_of_hermes)
    armoury_of_ares.connect("east", library_of_athena)
    hall_of_hermes.connect("north", library_of_athena)
    hall_of_hermes.connect("south", forge_of_prometheus)
    forge_of_prometheus.connect("north", hall_of_hermes)

    return library_of_athena, {
        room.name: room for room in (library_of_athena, armoury_of_ares, hall_of_hermes, forge_of_prometheus)
    }

def build_world() -> tuple[Map, Room, dict[str, dict[str, Room]]]:
    dungeon = Map()

    floor_0_start, floor_0_rooms = build_floor_0()
    floor_1_start, floor_1_rooms = build_floor_1()
    floor_2_start, floor_2_rooms = build_floor_2()

    floor_0_rooms["Chamber of Chiron"].connect("descend", floor_1_rooms["Cave Entrance"])
    floor_1_rooms["Styx Crossing"].connect("descend", floor_2_rooms["Library of Athena"])
    floor_2_rooms["Library of Athena"].connect("ascend", floor_1_rooms["Styx Crossing"])

    all_floors = {
        "floor_0": floor_0_rooms,
        "floor_1": floor_1_rooms,
        "floor_2": floor_2_rooms,
    }

    for floor_rooms in all_floors.values():
        for room in floor_rooms.values():
            dungeon.add_room(room)

    dev_test_room = build_blank_test_room()
    dungeon.add_room(dev_test_room)

    return dungeon, floor_0_start, all_floors
        