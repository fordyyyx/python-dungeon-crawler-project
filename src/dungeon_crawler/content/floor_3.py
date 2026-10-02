"""Floor 3 (Low Dungeon) - Bony Crypt, Cave of Harpies, Prayer Room, Dim Corridor, Overgrown Forest, and the hidden Ossuary."""

from dungeon_crawler.world import Room
from dungeon_crawler.items import Weapon, QuestItem, StatusEffectItem, SpellBook, IntellectReward, Trophy
from dungeon_crawler.characters import Enemy
from dungeon_crawler.spells import Spell
from dungeon_crawler.chests import add_random_chest
from dungeon_crawler.content.loot_tables import EARLY_LOOT
from .common import create_small_healing_potion

def create_centaur() -> Enemy:
    """Create the Centaur enemy for Overgrown Forest (floor 3) - drops Centaur's Broken Bow, Athena's required trade item."""
    return Enemy(
        name="Centaur",
        hp=18,
        attack_damage=6,
        armour=1,
        loot=[create_centaurs_broken_bow()],
        description="Half man, half horse, nothing like the patient tutor you met on floor 0 - this one draws its bow the moment it sees you.",
        experience_reward=10,
        gold_reward=20,
    )

def create_crypt_keeper() -> Enemy:
    """Create the Crypt Keeper enemy for Bony Crypt (floor 3) - drops the Vial of Grave Rot."""
    return Enemy(
        name="Crypt Keeper",
        hp=16,
        attack_damage=6,
        armour=1,
        loot=[create_vial_of_grave_rot(), create_small_healing_potion()],
        description="Not a skeleton like the others - this one moves with purpose, tending to bones that were never meant to be disturbed.",
        experience_reward=12,
        gold_reward=18,
        article="the",
    )

def create_harpy() -> Enemy:
    """Create the Harpy enemy for Cave of Harpies (floor 3) - drops the Harpy-fletched Bow. Higher aggression_weight than most early enemies,
    reflecting an erratic aerial assault rather than a steady melee approach."""
    return Enemy(
        name="Harpy",
        hp=13,
        attack_damage=7,
        armour=0,
        loot=[create_harpy_fletched_bow()],
        description="It drops from the cave roof without warning, all talons and shrieking fury before you've even registered movement.",
        experience_reward=11,
        gold_reward=15,
        aggression_weight=1.5,
    )

def create_fanatic() -> Enemy:
    """Create the fanatic enemy for Prayer Room (floor 3) - drops the Tome of Old Prayers."""
    return Enemy(
        name="Fanatic",
        hp=15,
        attack_damage=6,
        armour=0,
        loot=[create_tome_of_old_prayers()],
        description="Still muttering to gods no one else remembers, it turns on you the moment you disturb the murals.",
        experience_reward=13,
        gold_reward=18,
    )

def create_lurker() -> Enemy:
    """Create the lurker enemy for Dim Corridor (floor 3) - the toughest enemy on this floor, fitting for the last room before descending into
    Overgrown Forest and floor 4."""
    return Enemy(
        name="Lurker",
        hp=17,
        attack_damage=7,
        armour=1,
        loot=[create_small_healing_potion()],
        description="You don't see it until it's already close - just a shape the torchlight never quite reaches.",
        experience_reward=14,
        gold_reward=20,
    )

def create_prayer_bolt() -> Spell:
    """Create the Prayer Bolt spell - the game's first real narrative Spell, taught by the Tome of Old Prayers."""
    return Spell(
        name="Prayer Bolt",
        description="A bolt of desperate, half-remembered devotion, thrown more in hope than in skill",
        mana_cost=6,
        damage=8,
    )

def create_tome_of_old_prayers() -> SpellBook:
    """Create the Tome of Old Prayers - the game's first real narrative SpellBook, teaching Prayer Bolt. Dropped by the Fanatic."""
    return SpellBook(
        name="Tome of Old Prayers",
        description="Pages brittle with age, prayers scrawled in a hand that grew more frantic towards the end.",
        spell=create_prayer_bolt(),
        article="the",
    )

def create_harpy_fletched_bow() -> Weapon:
    """Create the Harpy-fletched Bow - the game's first real slot="ranged" weapon (create_test_boss and friends are dev-only; no ranged weapon
    existed as real, reachable content until now). Dropped by the Harpy in Cave of Harpies."""
    return Weapon(
        name="Harpy-fletched Bow",
        description="Strung tight and fletched with feathers still faintly warm - whoever made this didn't have to look far for materials.",
        damage=4,
        slot="ranged",
        weapon_class="ranged",
    )

def create_vial_of_grave_rot() -> StatusEffectItem:
    """Create the Vial of Grave Rot - an offensive StatusEffectItem (poison), the game's first real narrative instance of this item type,
    (create_test_venom_vial() was dev-only until now). Dropped by the Crypt Keeper."""
    return StatusEffectItem(
        name="Vial of Grave Rot",
        description="Thick, dark, and faintly luminous - whatever's in here hasn't been alive for a very long time.",
        effect_name="Poison",
        amount=-3,
        duration=3,
    )

def create_centaurs_broken_bow() -> QuestItem:
    """Create the Centaur's Broken Bow quest item, the required trade item for Athena's reward - dropped by the Centaur (floor 3, Overgrown Forest)."""
    return QuestItem(
        name="Centaur's Broken Bow",
        description="Snapped clean at the riser - proof you closed the distance before it ever got a clean shot off.",
        article="the",
    )

def create_ledger_of_the_unjudged() -> IntellectReward:
    """Create the Ledger of the Unjudged - the Crypt Keeper's record of the dead it arranged in the Ossuary. Reading it grants +2 intellect,
    permanently. The first way to raise intellect beyond levelling, placed on floor 3 so it arrives before floor 4's intellect-gated hidden room."""
    return IntellectReward(
        name="Ledger of the Unjudged",
        description=(
            "Page after page of names in a tiny, careful hand - every one of the dead whose bones are stacked here. Beside each, the same note: "
            "'Not yet judged.' Whoever kept it never stopped hoping someone would come."
        ),
        amount=2,
        article="the",
    )

def create_keepers_lantern() -> Trophy:
    """Create the Keeper's Lantern - a Trophy for the Trophy Room of Zeus, found in the Ossuary."""
    return Trophy(
        name="Keeper's Lantern",
        description="The Crypt Keeper's lantern, stil burning low, as it has for every name in the ledger.",
        article="the",
    )

def build_floor_3() -> tuple[Room, dict[str, Room]]:
    """Low Dungeon - Bony Crypt, Cave of Harpies (with a random chest), Prayer Room, Dim Corridor, and Overgrown Forest, plus the Ossuary, hidden
    below the Bony Crypt."""
    bony_crypt = Room(
        name="Bony Crypt",
        description="Skeletal remains are stacked floor to ceiling in neat, deliberate rows — someone, once, cared enough to arrange them.",
        examine_text=(
            "One wall of skulls doesn't quite match the rest. The stacking is newer, and more careful, as though it was built to cover something "
            "underneath."
        ),
    )
    ossuary = Room(
        name="Ossuary",
        description=(
            "A low, round chamber beneath the crypt, every niche filled with bones laid out with impossible care - sorted, cleaned, each skull "
            "facing the same way. A lectern stands at the centre, and on it, a ledger left open at the last page anyone wrote in."
        ),
    )
    cave_of_harpies = Room(
        name="Cave of Harpies",
        description="Feathers and old bones litter a cave mouth that reeks of carrion; shrieks echo faintly from somewhere above. Wedged into a nest of "
        "sticks and torn cloth sits a battered chest - whatever the harpies dragged up here, they wanted to keep.",
    )
    prayer_room = Room(
        name="Prayer Room",
        description="Faded murals of forgotten gods cover the walls, the air thick with old incense and older dread. Something about the air here feels thin, like a doorway that isn't quite closed - say 'forge' if you feel the pull toward it.",
    )
    dim_corridor = Room(
        name="Dim Corridor",
        description="A low, narrow passage where the torchlight barely reaches the far end.",
    )
    overgrown_forest = Room(
        name="Overgrown Forest",
        description="Twisted black trees crowd close overhead, roots breaking up through the stone floor as if the dungeon itself is being reclaimed.",
        examine_text=(
            "Carved into a half-buried stone, worn but still legible: \"Strength alone does not survive what waits below. "
            "Say 'learn <path>' - attack, defence, or abilities - to spend what you've earned. The labyrinth does not forgive "
            "those who go down unprepared.\""
        ),
    )

    bony_crypt.connect("south", cave_of_harpies)
    cave_of_harpies.connect("north", bony_crypt)
    cave_of_harpies.connect("east", prayer_room)
    cave_of_harpies.connect("south", dim_corridor)
    prayer_room.connect("west", cave_of_harpies)
    dim_corridor.connect("north", cave_of_harpies)
    dim_corridor.connect("south", overgrown_forest)
    overgrown_forest.connect("north", dim_corridor)

    bony_crypt.add_hidden_exit("down", ossuary)
    ossuary.connect("up", bony_crypt)

    overgrown_forest.add_enemy(create_centaur())
    bony_crypt.add_enemy(create_crypt_keeper())
    cave_of_harpies.add_enemy(create_harpy())
    prayer_room.add_enemy(create_fanatic())
    dim_corridor.add_enemy(create_lurker())

    ossuary.add_item(create_ledger_of_the_unjudged())
    ossuary.add_item(create_keepers_lantern())

    add_random_chest(cave_of_harpies, EARLY_LOOT)

    return bony_crypt, {
        room.name: room for room in (bony_crypt, ossuary, cave_of_harpies, prayer_room, dim_corridor, overgrown_forest)
    }