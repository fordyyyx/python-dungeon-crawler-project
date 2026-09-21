"""Floor 6 (Odyssey and the Open Sea) - Bright Cave, Calm Waters, Cavern of Polyphemus, Rocky Shore, Narrow River, Poseidon's Depths, Shadow of Ithaca, Muddy Pigsty, Throne Room of Odysseus, Bedchamber of Odysseus."""

from dungeon_crawler.world import Room

def build_floor_6() -> tuple[Room, dict[str, Room]]:
    """The Odyssey and the Open Sea - Bright Cave, Calm Waters, Cavern of Polyphemus, Rocky Shore, Narrow River, Poseidons Depths, Shadow of Ithaca, Muddy Pigsty, Throne Room of Odysseus, and Bedchamber of Odysseus."""
    bright_cave = Room(name="Bright Cave", description="Sunlight streams in from an opening far above, illuminating bones picked disturbingly clean.")
    calm_waters = Room(name="Calm Waters", description="The sea here is unnervingly still, and faint singing drifts across it from somewhere you can't quite place.")
    cavern_of_polyphemus = Room(name="Cavern of Polyphemus", description="A single vast eye socket, carved crudely into the far wall, watches the room, long since gone dark.")
    rocky_shore = Room(name="Rocky Shore", description="Jagged black rocks jut from churning water, six shadows moving beneath the surface in perfect, unsettling unison.")
    narrow_river = Room(name="Narrow River", description="The current here pulls hard toward a whirlpool that never quite stops turning.")
    poseidons_depths = Room(name="Poseidon's Depths", description="The water opens into a vast underwater hall, pressure bearing down from every direction at once.")
    shadow_of_ithaca = Room(name="Shadow of Ithaca", description="A modest, homely room, oddly warm compared to everywhere else on this floor.")
    muddy_pigsty = Room(name="Muddy Pigsty", description="Thick mud and the smell of something herbal linger together in a low, cramped pen.")
    throne_room_of_odysseus = Room(name="Throne Room of Odysseus", description="An once-grand hall, now crowded and disordered, the throne itself sitting conspicuously empty.")
    bedchamber_of_odysseus = Room(name="Bedchamber of Odysseus", description="A quiet room untouched by the chaos elsewhere, a loom standing half-finished in the corner.")

    bright_cave.connect("south", calm_waters)
    calm_waters.connect("north", bright_cave)
    calm_waters.connect("east", cavern_of_polyphemus)
    calm_waters.connect("west", rocky_shore)
    cavern_of_polyphemus.connect("west", calm_waters)
    rocky_shore.connect("east", calm_waters)
    rocky_shore.connect("south", narrow_river)
    narrow_river.connect("north", rocky_shore)
    narrow_river.connect("south", poseidons_depths)
    poseidons_depths.connect("north", narrow_river)
    poseidons_depths.connect("east", shadow_of_ithaca)
    shadow_of_ithaca.connect("west", poseidons_depths)
    shadow_of_ithaca.connect("east", muddy_pigsty)
    shadow_of_ithaca.connect("south", throne_room_of_odysseus)
    muddy_pigsty.connect("west", shadow_of_ithaca)
    throne_room_of_odysseus.connect("north", shadow_of_ithaca)
    throne_room_of_odysseus.connect("west", bedchamber_of_odysseus)
    bedchamber_of_odysseus.connect("east", throne_room_of_odysseus)

    return bright_cave, {
        room.name: room for room in (bright_cave, calm_waters, cavern_of_polyphemus, rocky_shore, narrow_river, poseidons_depths, shadow_of_ithaca, muddy_pigsty, throne_room_of_odysseus, bedchamber_of_odysseus)
    }