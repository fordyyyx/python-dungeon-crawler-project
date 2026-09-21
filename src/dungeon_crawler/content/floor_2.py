"""Floor 2 (Domains of the Gods) - Library of Athena, Armoury of Ares, Trophy Room of Zeus, Hall of Hermes, Forge of Prometheus, Practice Chamber."""

from dungeon_crawler.world import Room
from dungeon_crawler.items import Armour, Weapon, SkillPointReward
from dungeon_crawler.characters import Enemy, Ally

def create_practice_dummy() -> Enemy:
    """Player-customisable practice dummy - respawns=True (see handle_enemy_defeat()), zero XP/gold reward regardless of what 'dummy set'
    changes. Distinct from the narrative Training Dummy at Chamber of Chiron (South) - that one is a one-time tutorial enemy;
    this is a genuine, repeatable testing sandbox."""
    return Enemy(
        name="Practice Enemy",
        hp=20,
        attack_damage=1,
        armour=0,
        description="A well-worn straw dummy, stitched back together more times than anyone's bothered to count.",
        experience_reward=0,
        gold_reward=0,
        respawns=True,
    )

def create_athena() -> Ally:
    """Create the Athena ally for floor 2, placed in the Library of Athena by build_floor_2()."""
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
    """Create the Ares ally for floor 2, placed in the Armoury of Ares by build_floor_2()."""
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
    """Create the Hermes ally for floor 2, placed in the Hall of Hermes by build_floor_2()."""
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
    """Create the Prometheus ally for floor 2, placed in the Forge of Prometheus by build_floor_2()."""
    return Ally(
        name="Prometheus",
        description="Chained but unbroken, watching you with the weary patience of someone who's paid dearly for helping before.",
        hint="",
        hint_complete="",
        required_items=[],
        items=[]
    )

def create_breastplate_of_athena() -> Armour:
    """Create the Breastplate of Athena armour - Athena's trade reward, reachable now that create_athena() is placed in build_floor_2()."""
    return Armour(
        name="Breastplate of Athena",
        description="Cool to the touch even in the deepest heat, etched with an owl that seems to watch whichever way danger comes from.",
        defence=4,
    )

def create_spear_of_ares() -> Weapon:
    """Create the Spear of Ares weapon."""
    return Weapon(
        name="Spear of Ares",
        damage=6,
        description="Bronze-tipped and perfectly balanced - it feels less like you're holding a weapon, and more like it's holding you steady",
    )

def create_hermes_favour() -> SkillPointReward:
    """Create the Favour of Hermes skill point reward - Hermes' trade reward, reachable now that create_hermes() is placed in build_floor_2()."""
    return SkillPointReward(
        name="Favour of Hermes",
        description="Quick, light, and gone before you've noticed - much like the god who gave it.",
        points = 1
    )

def build_floor_2() -> tuple[Room, dict[str, Room]]:
    """Domains of the Gods - Library of Athena, Armoury of Ares, Trophy Room of Zeus, Hall of Hermes, and Forge of Prometheus."""
    library_of_athena = Room(name="Library of Athena", description="Towering shelves of scrolls creak under their own weight; an owl watches from the rafters, unblinking.")
    armoury_of_ares = Room(name="Armoury of Ares", description="Racks of corroded bronze weapons line the walls, still faintly warm to the touch.", examine_text="One section of the far wall looks less like stone, and more like it's been built to resemble stone.", required_intellect=3)
    hall_of_hermes = Room(name="Hall of Hermes", description="A cluttered waypoint stacked with parcels and letters never delivered, sandals of every size hung along one wall.")
    forge_of_prometheus = Room(name="Forge of Prometheus", description="The air shimmers with heat from a fire that never seems to go out, chained tools scattered across a worn anvil.", is_forge=True)
    practice_chamber = Room(name="Practice Chamber", description="A sand-floored alcove beside the forge's heat, a single straw-and-rope dummy standing ready at its centre.", is_practice_chamber=True)
    trophy_room_of_zeus = Room(name="Trophy Room of Zeus", description="A narrow chamber lit by no visible flame, empty display alcoves lining every wall, patiently waiting to be filled.")

    library_of_athena.connect("west", armoury_of_ares)
    library_of_athena.connect("south", hall_of_hermes)
    armoury_of_ares.connect("east", library_of_athena)
    armoury_of_ares.add_hidden_exit("north", trophy_room_of_zeus)
    trophy_room_of_zeus.connect("south", armoury_of_ares)
    hall_of_hermes.connect("north", library_of_athena)
    hall_of_hermes.connect("south", forge_of_prometheus)
    forge_of_prometheus.connect("north", hall_of_hermes)
    forge_of_prometheus.connect("east", practice_chamber)
    practice_chamber.connect("west", forge_of_prometheus)

    practice_chamber.add_enemy(create_practice_dummy())
    library_of_athena.add_ally(create_athena())
    armoury_of_ares.add_ally(create_ares())
    hall_of_hermes.add_ally(create_hermes())
    forge_of_prometheus.add_ally(create_prometheus())

    return library_of_athena, {
        room.name: room for room in (library_of_athena, armoury_of_ares, hall_of_hermes, forge_of_prometheus, trophy_room_of_zeus, practice_chamber)
    }