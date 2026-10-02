"""Floor 8 (The Final Descent) - Gate of Cerberus, Hall of Hades."""
from dungeon_crawler.world import Room
from dungeon_crawler.items import Armour, Consumable, Weapon, Trophy
from dungeon_crawler.characters import Enemy, Companion
from .common import create_ambrosia

HADES_SPARED = "hades_spared"
HADES_DEFEATED = "hades_defeated"

def create_cerberus() -> Enemy:
    """Create Cerberus - the gatekeeper before Hades, in the Gate of Cerberus. Three phases, one per head, each a different kind of danger. This
    first is the watchful head: heavily armoured, bracing readily - a wall. No rewards on this phase. Guards the way south to the Hall of Hades."""
    return Enemy(
        name="Cerberus",
        hp=90,
        attack_damage=13,
        armour=5,
        brace_amount=5,
        caution_weight=1.3,
        article="",
        next_phase_factory=create_cerberus_two_heads,
        description="Three heads, three sets of eyes, and not one of them blinking. It isn't guarding the gate so much as being it.",
    )

def create_cerberus_two_heads() -> Enemy:
    """Create Cerberus (Two Heads) - the second phase, after the watchful head falls. The raging head: less armour, but the hardest hitter in
    the game so far, and aggressive. No rewards on this phase."""
    return Enemy(
        name="Cerberus (Two Heads)",
        hp=82,
        attack_damage=17,
        armour=3,
        aggression_weight=1.6,
        article="",
        next_phase_factory=create_cerberus_last_head,
        description="One head hangs limp. The other two have stopped watching and started hunting - and they're furious.",
    )

def create_cerberus_last_head() -> Enemy:
    """Create Cerberus (Last Head) - the final phase: the venomous head. Poisons through a natural weapon, the Aconite Fangs - equipped here and
    never dropped, since it isn't in the loot. Its defeat_effect fully restores the player and their companion (the guaranteed recovery before
    Hades). Drops the Hide of Cerberus."""
    cerberus = Enemy(
        name="Cerberus (Last Head)",
        hp=72,
        attack_damage=15,
        armour=3,
        article="",
        loot=[create_hide_of_cerberus(), create_collar_of_cerberus()],
        description="Only one head is left, dripping something that smokes where it hits the stone. Where it lands, pale flowers start to grow.",
        experience_reward=110,
        gold_reward=60,
        defeat_effect=_the_gate_falls_silent,
    )
    create_aconite_fangs().use(cerberus)
    return cerberus

def create_aconite_fangs() -> Weapon:
    """Create the Aconite Fangs - a natural weapon, never a drop. Adds no damage of its own; its only purpose is its poison_chance, which
    attack() already reads from any equipped weapon. The pattern for giving any enemy a weapon property without a new special-case flag."""
    return Weapon(
        name="Aconite Fangs",
        description="Not a weapon anyone could carry - the poison is in the bite itself.",
        damage=0,
        poison_chance=0.35,
    )

def _the_gate_falls_silent(player) -> str:
    """Cerberus' defeat_effect - the guaranteed recovery before Hades. Fully restores the player, and their companion too, reviving them if downed."""
    player.hp = player.max_hp
    lines = ["The last head sinks to the stone, and the gate falls silent. The cold that's followed you all the way down lifts, just for a moment - and you're whole again."]
    companion = player.companion
    if companion is not None:
        companion.hp = companion.max_hp
        lines.append(f"{companion.name} stands straighter too, their wounds gone.")
    return "\n".join(lines)

def create_hide_of_cerberus() -> Armour:
    """Create the Hide of Cerberus - heavy body armour with 7 defence, the best so far. Dropped by Cerberus (Last Head), just before Hades."""
    return Armour(
        name="Hide of Cerberus",
        description="Coarse, black, and warm to the touch in a place where nothing else is. It's turned aside worse than you.",
        defence=7,
        weight="heavy",
        max_durability=22,
        article="the",
    )

def create_hades() -> Enemy:
    """Create Hades - the final boss, in the Hall of Hades. Armoured, heals and braces. His defeat brings a wave of three Restless Shades - the dead
    he's been too busy to judge - then Hades (Helm of Darkness), the final phase. No rewards on this phase."""
    return Enemy(
        name="Hades",
        hp=100,
        attack_damage=15,
        armour=5,
        heal_amount=6,
        brace_amount=5,
        caution_weight=1.2,
        article="",
        next_wave_factories=[create_restless_shade, create_restless_shade, create_restless_shade],
        next_phase_factory=create_hades_helm_of_darkness,
        description="He rises from the throne of bone at last. He looks tired - not weak, but tired, like a man who hasn't slept in an age.",
    )

def create_restless_shade() -> Enemy:
    """Create a Restless Shade - one of three the dead Hades summons between his phases: the souls he's left unjudged. Each drops a Vial of
    Ambrosia, the fight's recovery window."""
    return Enemy(
        name="Restless Shade",
        hp=15,
        attack_damage=9,
        armour=1,
        loot=[create_ambrosia()],
        description="Grey, half-formed, and angry in the way only the long-forgotten can be.",
        experience_reward=10,
        gold_reward=3,
    )

def create_hades_helm_of_darkness() -> Enemy:
    """Create Hades (Helm of Darkness) - the final phase. The helm makes him hard to reach in melee (melee_dodge_chance, as with Paris), his
    bident pierces armour, and he hits harder than anything before him. Yields rather than dying if 'promised_mercy' is set - see the yield
    mechanic - becoming a recruitable companion. His defeat_effect plays the reveal and the recovery either way; defeating him ends the story."""
    return Enemy(
        name="Hades (Helm of Darkness)",
        hp=100,
        attack_damage=18,
        armour=4,
        armour_pierce=2,
        melee_dodge_chance=0.4,
        aggression_weight=1.4,
        article="",
        loot=[create_bident_of_hades(), create_helm_of_darkness()],
        description="He sets a dark helm on his head, and he's simply gone - there's only the sense of him, and the bident, coming from wherever you aren't looking.",
        experience_reward=150,
        gold_reward=80,
        yield_condition_flag="promised_mercy",
        yield_companion_factory=create_hades_companion,
        yield_result_flag=HADES_SPARED,
        defeat_effect=_hades_reveal,
    )

def _hades_reveal(player) -> str:
    """Hades' defeat_effect - the reveal, and the guaranteed recovery before the post-game. Two versions: a spared Hades explains himself and
    restores the player; a dead Hades leaves the truth to be understood too late, and his power washes over the player as his hold breaks."""
    if HADES_SPARED in player.story_flags:
        lines = [
            "Hades drops to one knee and pulls the helm from his head. For a moment, the whole Underworld seems to hold its breath.",
            "\"You think I stopped judging the dead because I stopped caring.\" His voice is hoarse. \"I stopped because every scrap of strength "
            "I had went into holding one door shut. Below this hall is Tartarus, and in Tartarus is Typhon - the thing that nearly tore Olympus "
            "down. For an age, I've held him there alone.\"",
            "He looks up, and there's no anger left in it. \"And you've broken my hold. He's already stirring. Persephone trusted you - so trust "
            "me now. I can still fight.\" He presses a cold hand to your chest, and clean, bright, strength floods through you.",
        ]
    else:
        lines = [
            "Hades falls, and the floor of the hall shudders - not with his death, but with something far beneath it.",
            "As his hold on the Underworld breaks, the dead rush past you like wind, and from somewhere below rises a sound older than the gods: "
            "laughter. In the silence afterwards, you understand - too late - what he was guarding.",
            "What's left of his power hangs in the air a moment, then washes over you.",
        ]
    player.hp = player.max_hp
    if player.companion is not None:
        player.companion.hp = player.companion.max_hp
    lines.append("(You are fully restored.)")
    return "\n\n".join(lines)

def create_hades_companion(home_room: Room | None = None) -> Companion:
    """Create Hades as a companion - recruitable only by sparing him (see the yield mechanic), for the post-game and New Game+. His level-1
    stats are set for the post-game, since he can't be recruited any earlier - and deliberately modest (40 HP / 12 attack / heal 3): at 60 / 16 /
    heal 6 he carried the player through Typhon, which should stay the hardest fight in the game with or without him. home_room follows the
    usual placeholder pattern; the yield mechanic replaces it with the Hall of Hades."""
    return Companion(
        name="Hades",
        hp=40,
        home_room=home_room or Room("Hall of Hades"),
        attack_damage=12,
        armour=4,
        heal_amount=3,
        brace_amount=4,
        description="Helm under one arm, bident in hand, looking at the dark stair down as though he's been dreading it for a very long time.",
        hint=(
            "\"He's waking.\" He doesn't look away from the stair. \"I held him alone for an age. I'd rather not do the last of it alone as well.\"\n\n"
            "\"Say 'recruit hades', if you'll have me.\""
        ),
        rival_lines={
            "Typhon": (
                "Hades grips his bident until his knuckles whiten. \"Hello again, old monster.\" A thin, tired smile. \"You've grown. So "
                "have I.\""
            ),
        },
    )

def create_bident_of_hades() -> Weapon:
    """Create the Bident of Hades - his signature drop: piercing, with lifesteal, as the god of the dead draws life from the living. Drops whether
    he dies or yields."""
    return Weapon(
        name="Bident of Hades",
        description="Two black prongs on a shaft cold enough to numb your hand. Every wound it opens feeds whoever holds it.",
        damage=10,
        weapon_class="piercing",
        armour_pierce=4,
        lifesteal=True,
        article="the",
    )

def create_collar_of_cerberus() -> Trophy:
    """Create the Collar of Cerberus - a Trophy for the Trophy Room of Zeus, dropped by Cerberus (Last Head)."""
    return Trophy(
        name="Collar of Cerberus",
        description="Bronze, three-ringed and enormous, and still warm.",
        article="the",
    )

def create_helm_of_darkness() -> Trophy:
    """Create the Helm of Darkness - a Trophy for the Trophy Room of Zeus, dropped by Hades (Helm of Darkness)."""
    return Trophy(
        name="Helm of Darkness",
        description="His helm, no longer making anyone invisible. It drops whether he is spared or not.",
        article="the",
    )

def build_floor_8() -> tuple[Room, dict[str, Room]]:
    """Final Descent - Gate of Cerberus and Hall of Hades."""
    gate_of_cerberus = Room(
        name="Gate of Cerberus",
        description="Enormous iron-bound doors loom ahead, three sets of eyes glowing faintly in the dark before them. Behind you, a faint heat leaks from a crack in the rock - say 'forge' if you feel the pull toward it.",
    )
    hall_of_hades = Room(
        name="Hall of Hades",
        description="The chamber opens into a vast black hall lit by pale fire; a throne of bone waits at its centre.",
    )

    gate_of_cerberus.connect("south", hall_of_hades)
    hall_of_hades.connect("north", gate_of_cerberus)

    gate_of_cerberus.add_enemy(create_cerberus())
    hall_of_hades.add_enemy(create_hades())

    gate_of_cerberus.guard_exit("south")

    hall_of_hades.cleared_story_flag = HADES_DEFEATED

    return gate_of_cerberus, {
        room.name: room for room in (gate_of_cerberus, hall_of_hades)
    }