"""Floor 4 (Labyrinth and Greater Monsters) - Labyrinth of the Minotaur, Stony Lair, Cavern of the Cyclops, Mossy Grove, Sandy Expanse, Maze of Pillars, Lair of Medusa."""

from dungeon_crawler.world import Room
from dungeon_crawler.items import QuestItem, Armour, StatusEffectItem, Weapon
from dungeon_crawler.characters import Enemy
from .common import create_bronze_xiphos

def create_minotaur() -> Enemy:
    """Create the Minotaur enemy, placed in the Labyrinth of the Minotaur (floor 4) by build_floor_4()."""
    return Enemy(
        name="Minotaur",
        hp=25,
        attack_damage=8,
        armour=2,
        loot=[create_bronze_xiphos()],
        description="Massive and bull-headed, it turns toward you with a snort that shakes dust from the walls.",
        experience_reward=30,
        gold_reward=18
    )

def create_cyclops() -> Enemy:
    """Create the Cyclops enemy for Cavern of the Cyclops (floor 4) - drops Cyclops' Eye, Ares' required trade item."""
    return Enemy(
        name="Cyclops",
        hp=22,
        attack_damage=7,
        armour=1,
        loot=[create_cyclops_eye()],
        description="It ducks under the cavern's low roof, one vast eye finding you before you've fully stepped inside.",
        experience_reward=25,
        gold_reward=15,
    )

def create_cyclops_eye() -> QuestItem:
    """Create the Cyclops' Eye quest item, the required trade item for Ares' reward - dropped by the Cyclops (floor 4, Cavern of the Cyclops)."""
    return QuestItem(
        name="Cyclops' Eye",
        description="Still faintly warm and unsettlingly heavy for its size - Ares will know exactly what this cost you."
    )

def create_petrified_guardian() -> Enemy:
    """Create the Petrified Guardian enemy for Stony Lair (floor 4) - a warning of Medusa's power, elsewhere on this floor (Lair of Medusa).
    Stone-cursed rather than truly alive, fittingly higher armour than the floor's other early enemies."""
    return Enemy(
        name="Petrified Guardian",
        hp=18,
        attack_damage=6,
        armour=3,
        loot=[create_chipped_stone_aegis()],
        description="Grey and unmoving until you're close enough to matter - one of Medusa's earlier mistakes, still standing guard.",
        experience_reward=16,
        gold_reward=9,
    )

def create_chipped_stone_aegis() -> Armour:
    """Create the Chipped Stone Aegis armour - dropped by the Petrified Guardian in Stony Lair."""
    return Armour(
        name="Chipped Stone Aegis",
        description="Heavier than it should be for its size, faint traces of an old shield-pattern still visible beneath the stone.",
        defence=3,
    )

def create_satyr() -> Enemy:
    """Create the Satyr enemy for Mossy Grove (floor 4) - drops the Wineskin of Dionysus, the game's first real narrative positive StatusEffectItem
    (create_test_healing_tonic() was dev-only until now)."""
    return Enemy(
        name="Satyr",
        hp=15,
        attack_damage=6,
        armour=1,
        loot=[create_wineskin_of_dionysus()],
        description="It grins before it attacks, unsteady on its hooves but faster than that ought to allow.",
        experience_reward=14,
        gold_reward=8,
    )

def create_wineskin_of_dionysus() -> StatusEffectItem:
    """Create the Wineskin of Dionysus - a positive StatusEffectItem (Regen), exercising the 'amount >= 0' branch of StatusEffectItem.use()
    through real content for the first time. Dropped by the Satyr."""
    return StatusEffectItem(
        name="Wineskin of Dionysus",
        description="Warm going down, warmer after - whatever's fermenting in here isn't entirely grapes.",
        effect_name="Regen",
        amount=3,
        duration=3,
    )

def create_lamia() -> Enemy:
    """Create the Lamia enemy for Shadowy Corner (floor 4) - the game's first use of Character.has_lifesteal, draining HP on every successful 
    hit. Drops Lamia's Fang."""
    return Enemy(
        name="Lamia",
        hp=20,
        attack_damage=7,
        armour=1,
        loot=[create_lamias_fang()],
        description="Beautiful only until she smiles - and by then it's already too late to look away.",
        experience_reward=18,
        gold_reward=10,
        has_lifesteal=True,
    )

def create_lamias_fang() -> Weapon:
    """Create the Lamia's Fang weapon - dropped by Lamia in Shadowy Corner. No lifesteal of its own - that's still a separate, undecided
    roadmap item, not something to sneak in unannounced here."""
    return Weapon(
        name="Lamia's Fang",
        description="Curved and needle-thin, more suited to a bite than a swing.",
        damage=5,
    )

def build_floor_4() -> tuple[Room, dict[str, Room]]:
    """Labyrinth & Greater Monsters - Labyrinth of the Minotaur, Cavern of the Cyclops, Stony Lair, Mossy Grove, Shadowy Corner, Sandy Expanse, Maze of Pillars, and Lair of Medusa."""
    labyrinth_of_the_minotaur = Room(name="Labyrinth of the Minotaur", description="Walls of rough-hewn stone stretch on in every direction, identical enough to make the way back uncertain.")
    cavern_of_the_cyclops = Room(name="Cavern of the Cyclops", description="A vast, uneven cave with a single great boulder rolled aside from what was once its entrance.")
    stony_lair = Room(name="Stony Lair", description="Statues in twisted, frozen poses fill every corner — a warning, if you look closely enough.")
    mossy_grove = Room(name="Mossy Grove", description="Soft green moss carpets everything, and the air smells faintly of wine and something wilder underneath.")
    shadowy_corner = Room(name="Shadowy Corner", description="A cramped, lightless space where the shadows seem to move independently of anything casting them.")
    sandy_expanse = Room(name="Sandy Expanse", description="Dry, cracked earth stretches out under an oppressive heat that shouldn't exist this far underground.")
    maze_of_pillars = Room(name="Maze of Pillars", description="Rows of bronze columns rise into darkness overhead, each one etched with faint, mechanical markings.")
    lair_of_medusa = Room(name="Lair of Medusa", description="Stone figures, frozen mid-stride, litter the chamber — every one of them was once someone like you.")

    labyrinth_of_the_minotaur.connect("west", stony_lair)
    labyrinth_of_the_minotaur.connect("east", cavern_of_the_cyclops)
    labyrinth_of_the_minotaur.connect("south", mossy_grove)
    stony_lair.connect("east", labyrinth_of_the_minotaur)
    cavern_of_the_cyclops.connect("west", labyrinth_of_the_minotaur)
    mossy_grove.connect("north", labyrinth_of_the_minotaur)
    mossy_grove.connect("west", shadowy_corner)
    mossy_grove.connect("south", sandy_expanse)
    shadowy_corner.connect("east", mossy_grove)
    sandy_expanse.connect("north", mossy_grove)
    sandy_expanse.connect("east", maze_of_pillars)
    maze_of_pillars.connect("west", sandy_expanse)
    maze_of_pillars.connect("south", lair_of_medusa)
    lair_of_medusa.connect("north", maze_of_pillars)

    labyrinth_of_the_minotaur.add_enemy(create_minotaur())
    cavern_of_the_cyclops.add_enemy(create_cyclops())
    stony_lair.add_enemy(create_petrified_guardian())
    mossy_grove.add_enemy(create_satyr())
    shadowy_corner.add_enemy(create_lamia())

    return labyrinth_of_the_minotaur, {
        room.name: room for room in (labyrinth_of_the_minotaur, stony_lair, cavern_of_the_cyclops, mossy_grove, shadowy_corner, sandy_expanse, maze_of_pillars, lair_of_medusa)
    }
