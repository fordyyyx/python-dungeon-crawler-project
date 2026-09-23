"""Floor 4 (Labyrinth and Greater Monsters) - Labyrinth of the Minotaur, Stony Lair, Cavern of the Cyclops, Mossy Grove, Sandy Expanse, Maze of Pillars, Lair of Medusa."""

from dungeon_crawler.world import Room
from dungeon_crawler.items import QuestItem, Armour, StatusEffectItem, Weapon
from dungeon_crawler.characters import Enemy
from .common import create_small_healing_potion

def create_minotaur() -> Enemy:
    """Create the Minotaur enemy, placed in the Labyrinth of the Minotaur (floor 4) by build_floor_4()."""
    return Enemy(
        name="Minotaur",
        hp=25,
        attack_damage=8,
        armour=2,
        loot=[create_labrys()],
        description="Massive and bull-headed, it turns toward you with a snort that shakes dust from the walls.",
        experience_reward=30,
        gold_reward=18,
        brace_amount=3,
    )

def create_labrys() -> Weapon:
    """Create the Labrys - a double-headed Minoan axe, dropped by the Minotaur. The labyrinth is traditionally said to take its name from this
    weapon."""
    return Weapon(
        name="Labrys",
        description="Two crescent blades on a single haft, heavy enough that every swing feels like it's pulling you along with it.",
        damage=5,
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
        loot=[create_chipped_stone_aegis(), create_small_healing_potion()],
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
        max_durability=10,
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

def create_ember_wraith() -> Enemy:
    """Create the Ember Wraith enemy for Sandy Expanse (floor 4) - the heat here isn't natural, and neither is what's causing it."""
    return Enemy(
        name="Ember Wraith",
        hp=19,
        attack_damage=7,
        armour=1,
        loot=[create_sunscorched_dagger()],
        description="Heat-shimmer given shape, it moves like the air itself is trying to get away from what's underneath.",
        experience_reward=17,
        gold_reward=9,
    )

def create_sunscorched_dagger() -> Weapon:
    """Create the Sun-scorched Dagger weapon - dropped by the Ember Wraith in Sandy Expanse."""
    return Weapon(
        name="Sun-scorched Dagger",
        description="The blade's still faintly hot to the touch, no matter how long it's been out of the wraith's grip.",
        damage=6,
    )

def create_talos() -> Enemy:
    """Create the Talos enemy for Maze of Pillars (floor 4) - the toughest regular enemy on this floor, a bronze automaton guardian rather
    than a living creature. Single-stage by design (see roadmap.md's multi-stage boss fights item for the mechanism that this deliberately
    doesn't use)."""
    return Enemy(
        name="Talos",
        hp=30,
        attack_damage=9,
        armour=3,
        loot=[create_talos_bronze_plating()],
        description="Impossibly large and impossibly quiet - each footstep lands like a verdict not a warning.",
        experience_reward=35,
        gold_reward=20,
    )

def create_talos_bronze_plating() -> Armour:
    """Create Talos' Bronze Plating armour - the best body-slot defence in the game so far. Dropped by Talos."""
    return Armour(
        name="Talos' Bronze Plating",
        description="Impossibly heavy for its size, seamless where it should show a joint - however it was made, it wasn't with hammers.",
        defence=5,
        max_durability=18,
    )

def create_medusa() -> Enemy:
    """Create Medusa (Phase 1) for Lair of Medusa (floor 4) - the floor's climactic multi-stage encounter. Defeating this phase spawns two Gorgons
    (next_wave_factories); once both are cleared, Medusa (Awakened) - the harder final phase - appears automatically (wave_gate_factory). This
    is roadmap.md's multi-stage boss fights item's first real, named use - only create_test_boss() (dev-only) exercised it before now."""
    return Enemy(
        name="Medusa",
        hp=25,
        attack_damage=6,
        armour=2,
        next_wave_factories=[create_gorgon, create_gorgon],
        next_phase_factory=create_medusa_awakened,
        description="She doesn't turn to face you outright - not yet. Even half-seen, something about her is already wrong to look at.",
    )

def create_gorgon() -> Enemy:
    """Create a Gorgon enemy - one of two spawned when Medusa (Phase 1) falls, guarding her final transformation."""
    return Enemy(
        name="Gorgon",
        hp=12,
        attack_damage=5,
        armour=1,
        loot=[create_small_healing_potion()],
        description="Snake-haired and hissing, it moves to block your path rather than your view - Medusa isn't finished yet.",
        experience_reward=8,
        gold_reward=4,
    )

def create_medusa_awakened() -> Enemy:
    """Create Medusa (Awakened) - the final phase, only reachable once both Gorgons are cleared. Harder than Phase 1 on every stat, and the
    first Enemy to carry has_petrifying_gaze (previously only ever a player secondary-ancestry ability) - a deliberate thematic callback,
    not a new mechanic. Drops Serpent's Kiss, the strongest weapon on this floor. heal_amount/brace_amount + a higher caution_weight give her
    genuine defensive options instead of pure damage output, per playtesting feedback - not a new mechanic, just using ones that already existed
    but had never been turned on for any enemy content yet."""
    return Enemy(
        name="Medusa (Awakened)",
        hp=35,
        attack_damage=8,
        armour=3,
        loot=[create_serpents_kiss()],
        description="There's no half-seen about it now - she looks at you directly, and you understand exactly what that means.",
        experience_reward=40,
        gold_reward=25,
        has_petrifying_gaze=True,
        heal_amount=2,
        brace_amount=2,
        caution_weight=1.2
    )

def create_serpents_kiss() -> Weapon:
    """Create Serpent's Kiss - the strongest weapon on floor 4, dropped by Medusa (Awakened)."""
    return Weapon(
        name="Serpent's Kiss",
        description="Curved like a fang, and just as reluctant to let go once it's found its mark.",
        damage=7,
    )

def build_floor_4() -> tuple[Room, dict[str, Room]]:
    """Labyrinth & Greater Monsters - Labyrinth of the Minotaur, Cavern of the Cyclops, Stony Lair, Mossy Grove, Shadowy Corner, Sandy Expanse, Maze of Pillars, and Lair of Medusa."""
    labyrinth_of_the_minotaur = Room(name="Labyrinth of the Minotaur", description="Walls of rough-hewn stone stretch on in every direction, identical enough to make the way back uncertain.")
    cavern_of_the_cyclops = Room(name="Cavern of the Cyclops", description="A vast, uneven cave with a single great boulder rolled aside from what was once its entrance.")
    stony_lair = Room(name="Stony Lair", description="Statues in twisted, frozen poses fill every corner — a warning, if you look closely enough. Something about the air here feels thin, like a doorway that isn't quite closed - say 'forge' if you feel the pull toward it.")
    mossy_grove = Room(name="Mossy Grove", description="Soft green moss carpets everything, and the air smells faintly of wine and something wilder underneath.")
    shadowy_corner = Room(name="Shadowy Corner", description="A cramped, lightless space where the shadows seem to move independently of anything casting them.")
    sandy_expanse = Room(name="Sandy Expanse", description="Dry, cracked earth stretches out under an oppressive heat that shouldn't exist this far underground.")
    maze_of_pillars = Room(name="Maze of Pillars", description="Rows of bronze columns rise into darkness overhead, each one etched with faint, mechanical markings. Something about the air here feels thin, like a doorway that isn't quite closed - say 'forge' if you feel the pull toward it.")
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
    sandy_expanse.add_enemy(create_ember_wraith())
    maze_of_pillars.add_enemy(create_talos())
    lair_of_medusa.add_enemy(create_medusa())

    return labyrinth_of_the_minotaur, {
        room.name: room for room in (labyrinth_of_the_minotaur, stony_lair, cavern_of_the_cyclops, mossy_grove, shadowy_corner, sandy_expanse, maze_of_pillars, lair_of_medusa)
    }
