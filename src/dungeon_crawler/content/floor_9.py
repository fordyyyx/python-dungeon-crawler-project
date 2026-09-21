"""Floor 9 (Tartarus)."""

from dungeon_crawler.world import Room

def build_floor_9() -> tuple[Room, dict[str, Room]]:
    """Tartarus."""
    tartarus = Room(name="Tartarus", description="The walls fall away entirely into an endless black chasm, heat and pressure pressing in from every direction at once.")

    return tartarus, {
        tartarus.name: tartarus
    }