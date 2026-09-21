"""Floor 5 (Shadow of Troy) - Shadow of Army Camp, Shadow of Troy (North/Central/Alleyway/South), Shadow of Pylos."""

from dungeon_crawler.world import Room

def build_floor_5() -> tuple[Room, dict[str, Room]]:
    """Shadow of Troy - Shadow of Army Camp, Shadow of Troy (North), Shadow of Troy (Central), Shadow of Troy (Alleyway), Shadow of Troy (South), and Shadow of Pylos."""
    shadow_of_army_camp = Room(name="Shadow of Army Camp", description="Rows of ghostly tents flicker at the edge of sight, campfires burning cold and without heat.")
    shadow_of_troy_north = Room(name="Shadow of Troy (North)", description="The pale outline of great walls rises overhead, breached and burning in an endless, silent loop.")
    shadow_of_troy_central = Room(name="Shadow of Troy (Central)", description="Rubble and broken spears cover the ground, the echo of old battle-cries fading in and out like a tide.")
    shadow_of_troy_alleyway = Room(name="Shadow of Troy (Alleyway)", description="A narrow gap between collapsed buildings, footsteps of the dead marching somewhere just out of view.")
    shadow_of_troy_south = Room(name="Shadow of Troy (South)", description="The last defensible ground before the walls fully give way, arrows frozen mid-fall around its edges.")
    shadow_of_pylos = Room(name="Shadow of Pylos", description="A calmer scene than the rest of Troy — a modest hall, a fire, a place that remembers counsel more than war.")

    shadow_of_army_camp.connect("south", shadow_of_troy_north)
    shadow_of_troy_north.connect("north", shadow_of_army_camp)
    shadow_of_troy_north.connect("south", shadow_of_troy_central)
    shadow_of_troy_central.connect("north", shadow_of_troy_north)
    shadow_of_troy_central.connect("west", shadow_of_troy_alleyway)
    shadow_of_troy_alleyway.connect("east", shadow_of_troy_central)
    shadow_of_troy_alleyway.connect("south", shadow_of_troy_south)
    shadow_of_troy_south.connect("north", shadow_of_troy_alleyway)
    shadow_of_troy_south.connect("east", shadow_of_pylos)
    shadow_of_pylos.connect("west", shadow_of_troy_south)

    return shadow_of_army_camp, {
        room.name: room for room in (shadow_of_army_camp, shadow_of_troy_north, shadow_of_troy_central, shadow_of_troy_alleyway, shadow_of_troy_south, shadow_of_pylos)
    }