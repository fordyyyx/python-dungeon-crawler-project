"""Floor 0 (Chiron's Training Grounds) - Chamber of Chiron + 4 variants."""

from dungeon_crawler.world import Room
from dungeon_crawler.items import Weapon, Armour, QuestItem
from dungeon_crawler.characters import Enemy, Ally

def create_chiron() -> Ally:
    """Create the Chiron ally - floor 0's trade gatekeeper for descending to floor 1."""
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
    """Create the Training Dummy enemy - zero XP/gold reward deliberately, since it's training-only (see CLAUDE.md)."""
    return Enemy(
        name="Training Dummy",
        hp=5,
        attack_damage=0,
        description="Straw and old rope, bolted to the floor. It has never once landed a real hit, and it isn't about to start now.",
        armour=0,
        loot=[create_dummy_head()],
        experience_reward=0,
        gold_reward=0
    )

def create_wooden_sword() -> Weapon:
    """Create the Wooden Sword weapon."""
    return Weapon(
        name="Wooden Sword",
        description="Blunt, splintered, and entirely harmless to anyone but a straw dummy — exactly as intended.",
        damage=1,
        weapon_class="blade",
    )

def create_wooden_shield() -> Armour:
    """Create the Wooden Shield armour."""
    return Armour(
        name="Wooden Shield",
        description="Warped and dry-rotted at the edges, but it'll turn aside a training blow well enough.",
        defence=1,
        slot="shield",
        weight="light",
        max_durability=6,
    )

def create_mentor() -> Ally:
    """Create the Mentor ally, who hands over the Mentor's Token needed for Chiron's trade."""
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
    """Create the Dummy Head quest item, one of Chiron's four required trade items."""
    return QuestItem(
        name="Dummy Head",
        description="A straw-stuffed head, still faintly dented from your practice blows — proof enough for Chiron that the lesson's been learned.",
    )

def create_charons_coin() -> QuestItem:
    """Create the Charon's Coin quest item - Chiron's trade reward, and the item required to unlock the descend exit to floor 1."""
    return QuestItem(
        name="Charon's Coin",
        description="Cold and unnaturally heavy for its size — the ferryman won't so much as glance at you without it."
    )

def create_mentors_token() -> QuestItem:
    """Create the Mentor's Token quest item, one of Chiron's four required trade items."""
    return QuestItem(
        name="Mentor's Token",
        description="A small carved token, worn smooth — Mentor's simple way of saying you've earned his approval."
    )

def build_floor_0() -> tuple[Room, dict[str, Room]]:
    """Build the tutorial floor - a central chamber with four spoke rooms, each exit locked behind the item taught/found in the room before it. Returns (starting room, every room on this floor keyed by name)."""
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