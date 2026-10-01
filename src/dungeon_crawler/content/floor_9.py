"""Floor 9 (Tartarus)."""

from dungeon_crawler.world import Room
from dungeon_crawler.items import Trophy, Weapon
from dungeon_crawler.characters import Enemy
from .floor_8 import create_ambrosia

TYPHON_DEFEATED = "typhon_defeated"

def create_typhon() -> Enemy:
    """Create Typhon - the post-game mega boss in Tartarus, far above Hades on the difficulty ladder. Phase 1: the storm-giant rising - huge,
    armoured, bracing, piercing armour. His defeat brings four Serpents of Typhon, then Typhon (Storm Unleashed). No rewards on this phase."""
    return Enemy(
        name="Typhon",
        hp=90,
        attack_damage=20,
        armour=5,
        armour_pierce=3,
        brace_amount=6,
        caution_weight=1.1,
        article="",
        next_wave_factories=[create_serpent_of_typhon] * 4,
        next_phase_factory=create_typhon_storm_unleashed,
        description="He fills the chasm. A hundred serpent heads coil from his shoulders, and every one of them turns to look at you.",
    )

def create_serpent_of_typhon() -> Enemy:
    """Create a Serpent of Typhon - one of four heads that tear free between his phases. Venomous, through a natural weapon. Each drops a Vial of
    Ambrosia, the fight's recovery window."""
    serpent = Enemy(
        name="Serpent of Typhon",
        hp=18,
        attack_damage=10,
        armour=2,
        loot=[create_ambrosia()],
        description="A serpent's head as long as a ship, still trailing the dark from where it tore free.",
        experience_reward=20,
        gold_reward=10,
        aggression_weight=1.4,
    )
    create_serpent_venom().use(serpent)
    return serpent

def create_typhon_storm_unleashed() -> Enemy:
    """Create Typhon (Storm Unleashed) - the final phase and the hardest-hitting enemy in the game. The storm makes him hard to reach in melee
    (melee_dodge_chance), and his fire and ash blind through a natural weapon. Drops the Heart of Typhon, a Trophy. Tartarus'
    cleared_story_flag sets 'typhon_defeated' when he falls, triggering the true ending."""
    typhon = Enemy(
        name="Typhon (Storm Unleashed)",
        hp=110,
        attack_damage=24,
        armour=4,
        armour_pierce=4,
        melee_dodge_chance=0.25,
        heal_amount=8,
        aggression_weight=1.5,
        caution_weight=0.6,
        article="",
        loot=[create_heart_of_typhon()],
        description="The sky of Tartarus tears open. He's all fire and wind and fury now - there's no telling where the next blow will come from.",
        experience_reward=250,
        gold_reward=150,
    )
    create_storm_of_ash().use(typhon)
    return typhon

def create_serpent_venom() -> Weapon:
    """Natural weapon for the Serpents of Typhon - poison only, never dropped."""
    return Weapon(name="Serpent Venom", description="The poison is in the bite itself.", damage=0, poison_chance=0.3)

def create_storm_of_ash() -> Weapon:
    """Natural weapon for Typhon (Storm Unleashed) - blinding only, never dropped."""
    return Weapon(name="Storm of Ash", description="Fire and ash, thrown in your face.", damage=0, blind_chance=0.3)

def create_heart_of_typhon() -> Trophy:
    """Create the Heart of Typhon - the trophy for defeating Typhon, for the Trophy Room of Zeus."""
    return Trophy(
        name="Heart of Typhon",
        description="A stone the size of your fist that still burns faintly, like a coal that refuses to go out. Zeus will want to see this.",
        article="the",
    )

def build_floor_9() -> tuple[Room, dict[str, Room]]:
    """Tartarus."""
    tartarus = Room(
        name="Tartarus",
        description="The walls fall away entirely into an endless black chasm, heat and pressure pressing in from every direction at once. One thread of that heat feels almost familiar - say 'forge' if you feel the pull toward it.",
    )

    tartarus.concealed_until = "hades_defeated"

    tartarus.add_enemy(create_typhon())

    tartarus.cleared_story_flag = TYPHON_DEFEATED

    return tartarus, {
        tartarus.name: tartarus
    }