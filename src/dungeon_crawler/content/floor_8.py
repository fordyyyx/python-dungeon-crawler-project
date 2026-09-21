"""Floor 8 (The Final Descent) - Gate of Cerberus, Hall of Hades."""
from dungeon_crawler.world import Room
from dungeon_crawler.items import Consumable
from dungeon_crawler.characters import Enemy

def create_hades() -> Enemy:
    """Create the Hades enemy - the endgame boss (see roadmap.md's multi-stage boss fights item); not yet placed in any floor."""
    return Enemy(
        name="Hades",
        hp=60,
        attack_damage=15,
        armour=5,
        loot=[create_ambrosia()],
        description="He doesn't rise from the throne immediately — he doesn't need to.",
        experience_reward=80,
        gold_reward=55
    )

def create_ambrosia() -> Consumable:
    """Create the Vial of Ambrosia consumable."""
    return Consumable(
        name="Vial of Ambrosia",
        heal_amount=20,
        description="Golden and faintly humming - mortal hands were never meant to hold this.",
    )

def build_floor_8() -> tuple[Room, dict[str, Room]]:
    """Final Descent - Gate of Cerberus and Hall of Hades."""
    gate_of_cerberus = Room(name="Gate of Cerberus", description="Enormous iron-bound doors loom ahead, three sets of eyes glowing faintly in the dark before them.")
    hall_of_hades = Room(name="Hall of Hades", description="The chamber opens into a vast black hall lit by pale fire; a throne of bone waits at its centre.")

    gate_of_cerberus.connect("south", hall_of_hades)
    hall_of_hades.connect("north", gate_of_cerberus)

    return gate_of_cerberus, {
        room.name: room for room in (gate_of_cerberus, hall_of_hades)
    }