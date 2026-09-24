"""Floor 5 (Shadow of Troy) - Shadow of Army Camp, Shadow of Troy (North/Central/Alleyway/South), Shadow of Pylos."""

from dungeon_crawler.world import Room
from dungeon_crawler.characters import Companion, Enemy, Ally
from dungeon_crawler.items import Armour, Consumable, Weapon, StatusEffectItem

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
        ancestry_lines={
            "achilles": (
                "He stares at you for a long moment, the spear forgotten. \"Neoptolemus' line, then. My son never did anything quietly "
                "either.\" Something close to pride crosses his face, and is gone. \"Let's see if the blood ran true.\""
            ),
        },
        rival_lines={
            "Shade of Hector": (
                "Achilles goes very still. \"Hector.\" Just the name. Then, quieter: \"I dragged him three times round the walls of his own city. "
                "I'd like to think I've changed.\" His grip tightens on the spear. \"Let's find out.\""
            ),
            "Myrmidon Soldier": (
                "\"Those are my Myrmidons.\" Something in his voice cracks. \"They followed me to Troy. They'd have followed me anywhere. "
                "Make it quick, if you can.\""
            ),
            "Shade of Ajax": (
                "Achilles lowers his spear, just slightly. \"Ajax. He carried me off the field when I fell - held them all back while "
                "he did it.\" A pause. \"I never got to thank him. I don't suppose I'll get the chance now either.\""
            ),
            "Shade of Paris": (
                "Achilles stops dead. Without seeming to notice, he shifts his weight off his left foot. \"Him.\" The word comes out flat. "
                "\"The best of the Greeks, killed by a man who never once stood close enough to be hit.\" He raises the spear. \"Keep him "
                "talking, if you can. I'd like him to see it coming.\""
            )
        }
    )

def create_shade_of_hector() -> Enemy:
    """Create the Shade of Hector for Shadow of Troy (North) - high armour, no tricks. No brace, heal or special ability: the whole challenge is
    getting through armour 5, which makes this the fight piercing weapons, heavy attacks and Twin Strike's armour-ignoring second hit are built for.
    Drops Hector's Helm."""
    return Enemy(
        name="Shade of Hector",
        hp=32,
        attack_damage=9,
        armour=5,
        loot=[create_hectors_helm()],
        description="Bronze from crest to greaves, the plume on his helm still stirring in a wind you can't feel. He doesn't taunt. He simply waits.",
        experience_reward=38,
        gold_reward=22,
    )

def create_hectors_helm() -> Armour:
    """Create Hector's Helm - a medium helmet-slot piece, the first helmet to improve on the Weathered Helm. Dropped by the Shade of Hector."""
    return Armour(
        name="Hector's Helm",
        description="Tall-crested and polished to a shine that hasn't dulled, even here.",
        defence=2,
        slot="helmet",
        weight="medium",
        max_durability=12,
    )

def create_shade_of_ajax() -> Enemy:
    """Create the Shade of Ajax for Shadow of Troy (Central) - brute force, no abilities. The deliberate opposite of the Shade of Hector in the
    previous room: the highest HP and damage of any regular enemy so far, but almost no armour, so the player's defence matters far more than
    armour-beating tools like piercing. Drops the Tower Shield of Ajax."""
    return Enemy(
        name="Shade of Ajax",
        hp=46,
        attack_damage=12,
        armour=1,
        loot=[create_tower_shield_of_ajax()],
        description="Head and shoulders above every other shade on the field, he fights like a landslide - no footwork, no feints, just weight.",
        experience_reward=42,
        gold_reward=24,
    )

def create_tower_shield_of_ajax() -> Armour:
    """Create the Tower Shield of Ajax - a heavy shield-slot piece, the strongest shield so far. Its weight and the shield slot's two-handed
    rule are the cost: no heavy weapons, and +10% miss chance on every attack. Dropped by the Shade of Ajax."""
    return Armour(
        name="Tower Shield of Ajax",
        description="Seven layers of oxhide faced with bronze, taller than you are. Carrying it feels less like holding a shield and more like hiding behind a wall",
        defence=4,
        slot="shield",
        weight="heavy",
        max_durability=20,
    )

def create_myrmidon_soldier() -> Enemy:
    """Create a Myrmidon Soldier - placed in a pair in Shadow of Troy (Alleyway), the first room with more than one ordinary enemy. Achilles' own
    men: disciplined rather than dangerous alone, with solid armour and a brace they use readily (caution_weight above default). Each drops a
    Field Dressing, giving the player some recovery before Troy (South). Its name must stay exactly "Myrmidon Soldier" - Achilles' rival
    line is keyed to it."""
    return Enemy(
        name="Myrmidon Soldier",
        hp=22,
        attack_damage=8,
        armour=3,
        loot=[create_field_dressing()],
        description="Bronze-armoured and silent, moving in step with the soldier beside it, as if they'd never stopped drilling.",
        experience_reward=20,
        gold_reward=10,
        brace_amount=3,
        caution_weight=1.2,
    )

def create_field_dressing() -> Consumable:
    """Create a Field Dressing - a 10 HP heal, the first step up from the Small Healing Potion's 5. Dropped by each Myrmidon Soldier."""
    return Consumable(
        name="Field Dressing",
        heal_amount=10,
        description="Clean linen and a salve that smells of honey and pine - soldier's way of staying on their feet.",
    )

def create_shade_of_paris() -> Enemy:
    """Create the Shade of Paris for Shadow of Troy (South) - an evasive archer, the first enemy to use melee_dodge_chance and a natural armour_pierce.
    Low HP, but half of all melee attacks miss him and his arrows ignore most armour, so both the 'just hit it' and 'stack armour' approaches struggle
    - a bow, spells, or the atalanta ancestry are the answer. Drops the Bow of Paris."""
    return Enemy(
        name="Shade of Paris",
        hp=20,
        attack_damage=10,
        armour=1,
        loot=[create_bow_of_paris()],
        description="He never lets you get close - always a step back, always another arrow already on the string.",
        experience_reward=40,
        gold_reward=30,
        melee_dodge_chance=0.5,
        armour_pierce=4,
    )

def create_bow_of_paris() -> Weapon:
    """Create the Bow of Paris - a ranged weapon that pierces 2 armour, the first upgrade over the Harpy-fletched Bow. Dropped by the Shade of
    Paris."""
    return Weapon(
        name="Bow of Paris",
        description="Light, elegant, and far deadlier than it looks - it's already killed the best of the Greeks once.",
        damage=6,
        slot="ranged",
        weapon_class="ranged",
        armour_pierce=2,
    )

def create_nestor() -> Ally:
    """Create Nestor for Shadow of Pylos - advice only, no trade. Points the player ahead to floor 6 (the sea) and gives away a Cup of Kykeon.
    Placed at the end of floor 5 as a breather after Paris, before the descent."""
    return Ally(
        name="Nestor",
        description="An old man by a small fire, who looks up as if you're exactly the company he was hoping for.",
        hint=(
            "\"A visitor! Sit, sit. You'll have come from Troy - everyone comes from Troy, eventually, I was there, you know. Ten "
            "years. I gave Agamemnon advice every single day, and he took it perhaps twice.\"\n\n"
            "\"So let me give you some, and you can do better than he did. Below here is the sea, and the sea doesn't fight fair. "
            "You'll hear singing - lovely singing. Don't go towards it. Further on, the water narrows between two dangers, and you won't "
            "slip past both. Choose the one that costs you something over the one that costs you everything.\"\n\n"
            "He presses a cup into your hands. \"And take this with you - kykeon. It set Machaon back on his feet when an arrow had him "
            "down. Say 'take cup of kykeon from nestor'. And don't argue. Nobody ever wins an argument with me - they just stop having it.\""
        ),
        required_items=[],
        items=[create_cup_of_kykeon()],
    )

def create_cup_of_kykeon() -> StatusEffectItem:
    """Create the Cup of Kykeon - a strong heal-over-time (Regen 4 for 4 turns, 16 HP in total). As a positive StatusEffectItem it's a free
    action in combat. Given by Nestor in Shadow of Pylos, ahead of the descent to floor 6."""
    return StatusEffectItem(
        name="Cup of Kykeon",
        description="Wine, barley, and grated goat's cheese - an odd mixture, but it warms you from the inside out.",
        effect_name="Regen",
        amount=4,
        duration=4,
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
    shadow_of_troy_north.add_enemy(create_shade_of_hector())
    shadow_of_troy_central.add_enemy(create_shade_of_ajax())
    shadow_of_troy_alleyway.add_enemy(create_myrmidon_soldier())
    shadow_of_troy_alleyway.add_enemy(create_myrmidon_soldier())
    shadow_of_troy_south.add_enemy(create_shade_of_paris())
    shadow_of_pylos.add_ally(create_nestor())

    return shadow_of_army_camp, {
        room.name: room for room in (shadow_of_army_camp, shadow_of_troy_north, shadow_of_troy_central, shadow_of_troy_alleyway, shadow_of_troy_south, shadow_of_pylos)
    }