"""Floor 1 (The Underworld Gateway) - Cave Entrance, Styx Crossing, Fields of Asphodel, Sunken Vault, and the Banks of the Lethe."""

from dungeon_crawler.world import Room
from dungeon_crawler.items import Armour, QuestItem, Weapon
from dungeon_crawler.characters import Enemy, Ally
from dungeon_crawler.exploration import deepest_floor_reached
from .common import create_small_healing_potion

LETHE_GOLD_PER_FLOOR = 25
"""The Lethe's price per floor of the deepest floor reached."""

def create_skeleton_warrior() -> Enemy:
    """Create a skeleton warrior enemy"""
    return Enemy(
        name="Skeleton Warrior",
        hp=8,
        attack_damage=4,
        armour=0,
        loot=[create_small_healing_potion(), create_skeleton_bone()],
        description="Bones held together by little more than old habit, still gripping a rusted blade with mechanical resolve.",
        experience_reward=5,
        gold_reward=2,
    )

def create_shade() -> Enemy:
    """Create the Shade enemy for Fields of Asphodel (floor 1) - drops the Weathered Helm, the game's first real slot="helmet" item."""
    return Enemy(
        name="Shade",
        hp=7,
        attack_damage=4,
        armour=0,
        loot=[create_weathered_helm()],
        description="Barely more than mist given shape, it drifts toward you without any real malice - just habit, worn thin over centuries.",
        experience_reward=4,
        gold_reward=1,
    )

def create_weathered_helm() -> Armour:
    """Create the Weathered Helm armour - a helmet-slot piece dropped by the Shade in Fields of Asphodel."""
    return Armour(
        name="Weathered Helm",
        description="Bronze gone dull and pitted, but the shape still holds - whoever wore it last isn't wearing it now.",
        defence=1,
        slot="helmet",
        weight="light",
        max_durability=5,
    )

def create_skeleton_bone() -> QuestItem:
    """Create the Skeleton Bone quest item, the required trade item for Hermes' reward - dropped by the Skeleton Warrior"""
    return QuestItem(
        name="Skeleton Bone",
        description="Picked clean, oddly light - the kind of thing a god who deals in messages and thresholds might want as proof of passage."
    )

def create_wounded_soldier() -> Ally:
    """Create the Wounded Soldier ally, who gives away starting gear for floor 1 with no trade required."""
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
    """Create the Charon ally, who ferries the player across the Styx."""
    return Ally(
        name="Charon",
        description="He holds out one weathered hand, saying nothing, waiting for the coin he already knows you'll need.",
        hint=(
            "\"You have the coin. Good.\" His voice is dry, unhurried. "
            "\"Cross when you're ready — the water won't wait for anyone, but it won't rush you either.\""
        ),
    )

def create_bronze_breastplate() -> Armour:
    """Create the Bronze Breastplate armour."""
    return Armour(
        name="Bronze Breastplate",
        defence=2,
        description="Dented and a size too large, but the bronze is sound - better than the wood you started with, if only just.",
        weight="medium",
        max_durability=8,
    )

def create_bronze_xiphos() -> Weapon:
    """Create the Bronze Xiphos weapon."""
    return Weapon(
        name="Bronze Xiphos",
        description="A short, leaf-bladed sword - favoured by soldiers who valued speed over reach.",
        damage=3,
        weapon_class="blade",
    )

def lethe_cost(player) -> int:
    """What forgetting costs right now: LETHE_GOLD_PER_FLOOR for each floor of the deepest one reached, and never less than one floor's worth.
    Based on the deepest floor rather than rooms visited, so exploring thoroughly never makes it dearer."""
    return LETHE_GOLD_PER_FLOOR * max(1, deepest_floor_reached(player))

def _drink(player, room) -> str:
    """Explain what the lethe does and what it would cost now. Changes nothing."""
    return (
        "The river moves so slowly it barely seems to move at all. The dead kneel along its banks and drink, and when they stand, whatever "
        "they were has left them.\n\n"
        "A little of it would take less. Enough to make you forget everything you've learned - every skill - and leave you free to learn it "
        "again, differently.\n\n"
        f"(Say 'drink deeply' to forget every skill and have all their points returned. It will cost {lethe_cost(player)} gold.)"
    )

def _drink_deeply(player, room) -> str:
    """Forget every skill and refund all their points, for lethe_cost(). Refuses without charging if there's nothing to forget or the player
    can't afford it."""
    if player.skill_tree.total_unlocked == 0:
        return "You drink, and nothing happens. There's nothing in you yet for the river to take."
    cost = lethe_cost(player)
    if player.gold < cost:
        return f"The river doesn't give its gift freely. It will cost {cost} gold - you have {player.gold}."
    player.gold -= cost
    refunded = player.skill_tree.forget_all(player)
    return (
        "You kneel and drink deeply. The water is so cold it burns, and then it isn't anything at all.\n\n"
        "When you stand, the shape of every skill you learned is gone - but the strength that learned them is still there, waiting to be "
        "spent again.\n\n"
        f"(Paid {cost} gold. {refunded} skill point{'s' if refunded != 1 else ''} returned - say 'skills' to see them.)"
    )

def build_floor_1() -> tuple[Room, dict[str, Room]]:
    """Build the Styx-crossing floor, including two rooms reached through hidden exits: the Sunken Vault (down from Styx Crossing) and the Banks
    of the Lethe (south from Fields of Asphodel, hinted at by its examine text), where the drink/drink deeply interactions let the player
    forget every skill for a refund of their points. Returns (starting room, every room on this floor keyed by name)."""
    cave_entrance = Room(
        name="Cave Entrance",
        description="A jagged fissure in the hillside breathes cold air from below; the last daylight fades behind you as you descend.",
    )
    styx_crossing = Room(
        name="Styx Crossing",
        description="Black water laps against a crumbling stone landing; something pale drifts just beneath the surface.",
        examine_text=(
            "The stonework here looks subtly disturbed — as if something below "
            "has shifted, recently, on its own."
        ),
    )
    fields_of_asphodel = Room(
        name="Fields of Asphodel",
        description="An endless grey meadow beneath a colourless sky, where the ordinary dead wander without purpose or memory.",
        examine_text=(
            "Past the grey grass, you can hear water where no water should be - a slow river, somewhere just out of sight to the south."
        ),
    )
    banks_of_the_lethe = Room(
        name="Banks of the Lethe",
        description=(
            "A black river moves so slowly it barely seems to move at all. The dead kneel along its banks to drink, and rise with nothing in "
            "their eyes. Whatever they were, the water has taken it."
        ),
    )
    sunken_vault = Room(
        name="Sunken Vault",
        description="Half-flooded and littered with old offerings, this side chamber was clearly sealed off for a reason.",
    )

    cave_entrance.connect("descend", styx_crossing)
    styx_crossing.connect("ascend", cave_entrance)
    styx_crossing.connect("east", fields_of_asphodel)
    fields_of_asphodel.connect("west", styx_crossing)

    styx_crossing.add_hidden_exit("down", sunken_vault)
    sunken_vault.connect("up", styx_crossing)
    fields_of_asphodel.add_hidden_exit("south", banks_of_the_lethe)
    banks_of_the_lethe.connect("north", fields_of_asphodel)

    cave_entrance.add_ally(create_wounded_soldier())
    styx_crossing.add_ally(create_charon())
    sunken_vault.add_enemy(create_skeleton_warrior())
    fields_of_asphodel.add_enemy(create_shade())

    banks_of_the_lethe.add_interaction("drink", _drink)
    banks_of_the_lethe.add_interaction("drink deeply", _drink_deeply)

    return cave_entrance, {
        room.name: room for room in (cave_entrance, styx_crossing, fields_of_asphodel, banks_of_the_lethe, sunken_vault)
    }