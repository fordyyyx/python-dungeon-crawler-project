"""Floor 5 (Shadow of Troy) - Shadow of Army Camp, Shadow of Troy (North/Central/Alleyway/South), Shadow of Pylos."""

from dungeon_crawler.world import Room
from dungeon_crawler.characters import Companion, Enemy

def _grant_achilles_skill_point(player) -> str:
    """Achilles' duel reward - a free skill point."""
    player.skill_tree.skill_points += 1
    return f"{player.name} gains a skill point for besting Achilles."

def create_shade_of_achilles_duellist() -> Enemy:
    """Create the combat form of the Shade of Achilles, fought via 'challenge shade of achilles'. Tougher than his companion form, since the
    duel is non-lethal and can be retried, and swift-footed (dodge_chance). No XP or gold - the reward is a skill point, via defeat_effect.
    Shares the companion's name, so it reads as the same person in combat. Deliberately not in ENEMY_REGISTRY: it only ever exists via
    start_duel(), which links it back to the companion - registering it made 'dev spawn shade of achilles' pick this over the companion."""
    duellist = Enemy(
        name="Shade of Achilles",
        hp=40,
        attack_damage=10,
        armour=3,
        description="He moves faster than anything dead has a right to - the spear is simply there, wherever you aren't looking",
        brace_amount=3,
        aggression_weight=1.4,
        caution_weight=0.8,
        defeat_effect=_grant_achilles_skill_point,
    )
    duellist.dodge_chance = 0.15
    return duellist

def create_shade_of_achilles(home_room: Room | None = None) -> Companion:
    """Create the Shade of Achilles - the game's first real recruitable Companion, in Shadow of Army Camp. He has to be beaten in a duel before
    he'll join. home_room defaults to a detached placeholder only so the no-argument COMPANION_REGISTRY factory still works; build_floor_5()
    passes the real room, and loading a save re-links the real one by name (see save_system.py)."""
    return Companion(
        name="Shade of Achilles",
        hp=30,
        home_room=home_room or Room("Shadow of Army Camp"),
        attack_damage=8,
        armour=2,
        description="He sits apart from the other shades, polishing a spear that will never need polishing again.",
        aggression_weight=1.5,
        caution_weight=0.5,
        brace_amount=3,
        hint=(
            "He doesn't look up. \"Another one sent down to fix what the gods can't be bothered to.\" The polishing stops.\n\n"
            "\"I was the best of the Greeks, you know. And down here I'm a shadow among shadows. I'd rather be a slave on a poor man's "
            "farm, alive, than king of all the dead.\"\n\n"
            "At last he looks at you and something in his face sharpens. \"But a fight - a real one - I could still have that. I won't " \
            "follow anyone I haven't measured. Say 'challenge shade of achilles', and show me you're worth the walk.\""
        ),
        hint_recruitable=(
            "\"You fight like someone with something to prove. Good - so do I. Say 'recruit shade of achilles', and I'll walk the " \
            "rest of this with you.\""
        ),
        duel_enemy_factory=create_shade_of_achilles_duellist,
        duel_won_message="He goes down on one knee - and laughs, for the first time in a very long time. \"There it is.\"",
        duel_lost_message=(
            "His spear stops a finger's width from your throat. \"Not yet.\" He steps back, and the camp is quiet again. "
            "\"Come back when you've learned something.\""
        ),
    )

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

    shadow_of_army_camp.add_companion(create_shade_of_achilles(shadow_of_army_camp))

    return shadow_of_army_camp, {
        room.name: room for room in (shadow_of_army_camp, shadow_of_troy_north, shadow_of_troy_central, shadow_of_troy_alleyway, shadow_of_troy_south, shadow_of_pylos)
    }