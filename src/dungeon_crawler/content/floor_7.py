"""Floor 7 (Prophecy and the Elder Dead) - Chamber of the Oracle, Shadow of Thebes, Bedchamber of Persephone."""

from dungeon_crawler.world import Room

def build_floor_7() -> tuple[Room, dict[str, Room]]:
    """Prophecy & the Elder Dead - Chamber of the Oracle, Shadow of Thebes, and Bedchamber of Persephone."""
    chamber_of_the_oracle = Room(name="Chamber of the Oracle", description="Smoke curls from a fissure in the floor, and the air itself seems to hum with something just out of hearing.")
    shadow_of_thebes = Room(name="Shadow of Thebes", description="A still, dim chamber where even the shadows seem to be listening.")
    bedchamber_of_persephone = Room(name="Bedchamber of Persephone", description="Half the room blooms with strange dark flowers; the other half lies frostbitten and bare.")

    chamber_of_the_oracle.connect("south", shadow_of_thebes)
    shadow_of_thebes.connect("north", chamber_of_the_oracle)
    shadow_of_thebes.connect("south", bedchamber_of_persephone)
    bedchamber_of_persephone.connect("north", shadow_of_thebes)

    return chamber_of_the_oracle, {
        room.name: room for room in (chamber_of_the_oracle, shadow_of_thebes, bedchamber_of_persephone)
    }