"""Floor 6 (Odyssey and the Open Sea) - Bright Cave, Calm Waters, Cavern of Polyphemus, Rocky Shore, Narrow River, Poseidon's Depths, Shadow of Ithaca, Muddy Pigsty, Throne Room of Odysseus, Bedchamber of Odysseus."""

from dungeon_crawler.world import Room
from dungeon_crawler.characters import Enemy, BLINDED_EFFECT_NAME, Companion, Ally
from dungeon_crawler.items import Weapon, Armour, Consumable, StatusEffectItem, LoyaltyToken
from dungeon_crawler.status_effects import StatusEffect
from dungeon_crawler.combat import resolve_pending_defeats
from dungeon_crawler.exchange import Offer
from .common import create_cup_of_kykeon, create_small_healing_potion
from dungeon_crawler.content import create_bronze_xiphos, create_weathered_helm, create_bronze_breastplate, create_harpy_fletched_bow, create_wineskin_of_dionysus

SIRENS_SKILL_POINTS = 2
SIRENS_HP_COST = 5
SIRENS_BARGAIN_FLAG = "sirens_bargain_taken"
CHARYBDIS_PHASES = ("still", "swallowing", "drained", "spewing")
CHARYBDIS_PHASE_TEXT = {
    "still": "The water lies flat and glassy. Charybdis is resting - for now.",
    "swallowing": "The sea begins to slide towards the centre of the channel, faster and faster. Anything on the water goes with it.",
    "drained": "The channel is empty down to the black rock. Everything she took is somewhere far below, in her throat.",
    "spewing": "With a roar, Charybdis heaves the sea back up - and flung up with it, spinning, is your raft.",
}
CHARYBDIS_FAIL_DAMAGE = 12

def create_laestrygonian() -> Enemy:
    """Create a Laestrygonian - one of the giant cannibals from Book 10 of the Odyssey, placed in Bright Cave alongside their king, Antiphates.
    High damage, and a natural armour_pierce (the same mechanic as floor 5 enemies), since they fight with thrown boulders that armour does
    little against. Drops Laestrygonian Hide."""
    return Enemy(
        name="Laestrygonian",
        hp=30,
        attack_damage=12,
        armour=1,
        armour_pierce=2,
        loot=[create_laestrygonian_hide()],
        description="Twice the height of a man and built like a cliff face, it's already lifting a boulder the size of your chest.",
        experience_reward=30,
        gold_reward=15,
        aggression_weight=1.3,
    )

def create_antiphates() -> Enemy:
    """Create Antiphates, king of the Laestrygonians, placed in Bright Cave with one of his giants. A tougher version of the same boulder-throwing
    giant, with a different name so the two are rebuilt with their own loot after a save and load - enemies are restored from ENEMY_REGISTRY
    by name. Drops Antiphates' Club."""
    return Enemy(
        name="Antiphates",
        hp=36,
        attack_damage=13,
        armour=2,
        armour_pierce=2,
        loot=[create_antiphates_club()],
        description="Bigger even than the giant beside him, wearing a crown of hammered bronze and an expression that says you're dinner.",
        experience_reward=36,
        gold_reward=20,
        aggression_weight=1.3,
        article="",
    )

def create_laestrygonian_hide() -> Armour:
    """Create Laestrygonian Hide - medium body armour with 5 defence, the first medium body piece since the Bronze Breastplate. It sits between
    the Breastplate of Athena (light, 4) and Talos' Bronze Plating (heavy, 6). Dropped by the Laestrygonian."""
    return Armour(
        name="Laestrygonian Hide",
        description="A single cured hide from something enormous, stitched with sinew. It's stiff, and it smells, but blades skid off it.",
        defence=5,
        weight="medium",
        max_durability=14,
    )

def create_antiphates_club() -> Weapon:
    """Create Antiphates' Club - a heavy, two-handed weapon with no signature since Antiphates isn't a boss. A straight alternative to the Labrys:
    more damage, but no cleave. Dropped by Antiphates."""
    return Weapon(
        name="Antiphates' Club",
        description="A tree trunk with the branches knocked off and bronze nails driven into the end. You need both hands just to lift it.",
        damage=8,
        weapon_class="heavy",
        article="",
    )

def _sirens_offer_open(player, room) -> bool:
    """The Sirens' offer stays open until it's accepted - refusing never closes it."""
    return SIRENS_BARGAIN_FLAG not in room.flags

def _listen_to_sirens(player, room) -> str:
    """Hear the offer - changes nothing, and can be repeated. Accepting is a separate verb, so a curious 'listen' never costs anything."""
    return (
        "You let the song reach you. The voices are warm, and they know your name.\n\n" \
        "\"Stay a while. We know everything that happened at Troy, and everything that happens on earth. Listen to us, and you'll " \
        "go on knowing more than any mortal ever has.\" A pause, as soft as the water. \"All it costs is a little of what keeps you " \
        "standing. You'll hardly miss it.\"\n\n" \
        f"(Say 'give in' to accept: +{SIRENS_SKILL_POINTS} skill points, but -{SIRENS_HP_COST} max HP, permanently. "
        "Or 'resist' to turn away - the offer won't go anywhere.)"
    )

def _give_in_to_sirens(player, room) -> str:
    """Accept the bargain: skill points now, max HP lost for good. Max HP never drops below 1, and current HP is capped to the new maximum. Recorded
    in room.flags, so the Sirens fall silent for the rest of the run."""
    room.flags.add(SIRENS_BARGAIN_FLAG)
    player.skill_tree.skill_points += SIRENS_SKILL_POINTS
    player.max_hp = max(1, player.max_hp - SIRENS_HP_COST)
    player.hp = min(player.hp, player.max_hp)
    return (
        "You stop resisting. The song pours into you, and for a moment you understand everything - Troy, the gods, the shape of the sea. When " \
        "it ends, you're kneeling on the rocks, and something in you is thinner than it was.\n\n"
        f"(+{SIRENS_SKILL_POINTS} skill points. Max HP is now {player.max_hp}.)"
    )

def _resist_sirens(player, room) -> str:
    """Turn away - costs nothing, and the offer stays open."""
    return (
        "You fix your eyes on the far shore and keep walking. The singing follows you a little way, then fades - patient, as if it knows " \
        "you'll be back."
    )

def create_polyphemus() -> Enemy:
    """Create Polyphemus - floor 6's optional mini-boss in the Cavern of Polyphemus, and Poseidon's son. A slow, heavy brute who braces. Defeating
    him brings on Polyphemus (Blinded) via next_phase_factory, the same system as Medusa. No rewards on this phase - only the final phase counts.
    Speaks to Cyclops' and Poseidon's descendants."""
    return Enemy(
        name="Polyphemus",
        hp=42,
        attack_damage=12,
        armour=3,
        brace_amount=4,
        next_phase_factory=create_polyphemus_blinded,
        description="He's rolled a boulder across the cave mouth behind you, and now he's counting you the way he counts his sheep.",
        ancestry_lines={
            "cyclops": (
                "He sniffs the air, and the great eye narrows. \"Kin? Here?\" A slow, pleased rumble. \"Then you'll understand. Nobody "
                "leaves my cave.\""
            ),
            "poseidon": (
                "He goes still. \"You smell of the sea. Of him.\" Something like hurt crosses his face. \"Father never came when I called. "
                "Maybe he'll come for you.\""
            ),
        },
        article=""
    )

def create_polyphemus_blinded() -> Enemy:
    """Create Polyphemus (Blinded) - the final phase, blinded by the stake. Starts with a permanent Blinded effect (0.35 miss chance - its duration
    is simply longer than any fight can last), and hits far harder than his first phase: wild, and devastating when he connects. Drops the
    Olive-wood Stake."""
    polyphemus = Enemy(
        name="Polyphemus (Blinded)",
        hp=36,
        attack_damage=17,
        armour=3,
        loot=[create_olive_wood_stake()],
        description="Roaring, clutching his ruined eye, he swings at every sound in the cave - and when he finds you, he doesn't hold back.",
        experience_reward=60,
        gold_reward=35,
        aggression_weight=1.6,
        article="",
    )
    polyphemus.apply_status_effect(StatusEffect(BLINDED_EFFECT_NAME, 0, 999, miss_chance=0.35))
    return polyphemus

def create_olive_wood_stake() -> Weapon:
    """Create the Olive-wood Stake - the weapon that blinded Polyphemus, cut from his own club. Piercing, with a signature chance to blind
    whatever it hits. Dropped by Polyphemus (Blinded)."""
    return Weapon(
        name="Olive-wood Stake",
        description="Hardened in the fire, still blackened at the point. It was cut from his own club.",
        damage=7,
        weapon_class="piercing",
        armour_pierce=3,
        blind_chance=0.2,
    )

def create_wheel_of_cheese() -> Consumable:
    """Create a Wheel of Cheese - an 8 HP heal from Polyphemus' own stores, as in the myth. Two are placed in the Cavern of Polyphemus."""
    return Consumable(
        name="Wheel of Cheese",
        heal_amount=8,
        description="Firm, pale, and enormous - Polyphemus makes it from his own flocks' milk, and he'd be furious to see you eat it.",
    )

def create_head_of_scylla() -> Enemy:
    """Create a Head of Scylla - six are placed in Rocky Shore, one per head in the myth, guarding the route south to Poseidon's Depths.
    Individually weak, but six attacks a round make it the fight where armour matters most: every point is subtracted from six separate hits
    (though each still deals at least MINIMUM_DAMAGE). No armour of its own, so cleave and Twin Strike are strong here. No item loot
    - six identical heads can only drop identical items, so the room's reward is the Boar's-Tusk Helm on the rocks instead."""
    return Enemy(
        name="Head of Scylla",
        hp=12,
        attack_damage=7,
        armour=0,
        description="A long, scaled neck ending in a mouth with three rows of teeth. It isn't alone - it never is.",
        experience_reward=12,
        gold_reward=5,
        aggression_weight=1.4,
    )

def create_boars_tusk_helm() -> Armour:
    """Create the Boar's-Tusk Helm - the first heavy helmet (3 defence), completing the helmet choices: the Weathered Helm (light, 1),
    Hector's Helm (medium, 2) and this. The Iliad describes Odysseus wearing one. Placed on the rocks in Rocky Shore, left by one of the six
    men Scylla took."""
    return Armour(
        name="Boar's-Tusk Helm",
        description="Rows of boar's tusks stitched onto thick felt - an Ithacan's helmet. Its owner didn't need it once Scylla reached down.",
        defence=3,
        slot="helmet",
        weight="heavy",
        max_durability=14,
    )

def _charybdis_state(room) -> dict:
    """This visit's puzzle state - where the whirlpool is in its cycle, where the player is, and whether she's thrown the raft back up yet. Lives
    in room.transient_state, so it resets whenever the player leaves."""
    return room.transient_state.setdefault("charybdis", {"phase": 0, "position": "raft", "freed": False})

def _unsolved_charybdis(room):
    """The living placeholder, or None once the puzzle is solved."""
    return next((enemy for enemy in room.enemies if enemy.invulnerable and enemy.is_alive()), None)

def resolve_charybdis_action(verb: str, phase: str, state: dict) -> tuple[str, str]:
    """The puzzle's rules, kept free of the room and player so they can be tested directly. Returns (outcome, message), where outcome is 'ok',
    'fail', or 'solved', and may update state's position and freed. The solution follows the myth: climb while she swallows, watch while she's
    drained, let go as she spews the raft back up, row while the water is still."""
    if state["position"] == "raft":
        if verb == "climb" and phase in ("still", "swallowing"):
            state["position"] = "tree"
            return "ok", "You haul yourself up into the fig tree's branches and cling on."
        if phase == "swallowing":
            return "fail", "The sea pulls the raft out from under you, and you with it - down the whirlpool."
        if verb == "row":
            if phase == "still" and state["freed"]:
                return "solved", "You row with everything you have across the still water, and the channel falls away behind you."
            return "ok", "The current has the raft - you can't row clear while she has hold of the water."
        if verb == "let go":
            return "ok", "You're not holding on to anything."
        return "ok", ""

    if verb == "let go":
        if phase == "spewing":
            state["position"] = "raft"
            state["freed"] = True
            return "ok", "You let go and land hard on the raft as it's flung back up - out of her pull, for now."
        if phase == "still":
            state["position"] = "raft"
            return "ok", "You drop back onto the raft, still caught in the current."
        return "fail", "You let go - and fall straight into her open throat."
    if verb == "row":
        return "ok", "There's nothing to row from up there."
    if verb == "climb":
        return "ok", "You're already up in the fig tree."
    return "ok", "You hold on."

def _charybdis_verb(verb: str):
    """Build the room-interaction handler for one Charybdis verb. Applies the rules, then advances the whirlpool one step and describes it -
    or, on a failure, deals CHARYBDIS_FAIL_DAMAGE (which can kill) and restarts the puzzle; or, on success, 'defeats' the placeholder so
    the guard opens and its XP, gold, and loot are given out."""
    def handler(player, room) -> str:
        state = _charybdis_state(room)
        phase = CHARYBDIS_PHASES[state["phase"]]
        outcome, message = resolve_charybdis_action(verb, phase, state)

        if outcome == "fail":
            player.hp = max(0, player.hp - CHARYBDIS_FAIL_DAMAGE)
            room.transient_state.pop("charybdis", None)
            lines = [message, f"(You take {CHARYBDIS_FAIL_DAMAGE} damage.)"]
            lines.append("The sea closes over you." if not player.is_alive() else "The river spits you back out where you started, gasping.")
            return "\n".join(lines)

        if outcome == "solved":
            charybdis = _unsolved_charybdis(room)
            if charybdis is not None:
                charybdis.hp = 0
            room.transient_state.pop("charybdis", None)
            defeat_messages = resolve_pending_defeats(player, room)
            return "\n".join(line for line in (message, defeat_messages) if line)

        state["phase"] = (state["phase"] + 1) % len(CHARYBDIS_PHASES)
        next_phase = CHARYBDIS_PHASES[state["phase"]]
        return "\n".join(line for line in (message, CHARYBDIS_PHASE_TEXT[next_phase]) if line)
    return handler

def _charybdis_unsolved(player, room) -> bool:
    """Whether the Charybdis verbs still do anything."""
    return _unsolved_charybdis(room) is not None

def _charybdis_subsides(player) -> str:
    """Charybdis' defeat_effect - the message when the puzzle is solved."""
    return "Behind you, Charybdis sinks into a slow, sullen turning. Among the wreckage she's thrown up, something glints."

def create_charybdis() -> Enemy:
    """Create Charybdis - an invulnerable placeholder for the whirlpool in Narrow River. Can't be fought; it's 'defeated' by solving the fig-tree
    puzzle (see _charybdis_verb()), which gives out its XP, gold, and the Hoplon of the Drowned through the normal defeat handling. Guards
    the Charybdis route to Poseidon's Depths until then."""
    return Enemy(
        name="Charybdis",
        hp=1,
        attack_damage=0,
        article="",
        invulnerable=True,
        invulnerable_message="You can't fight a whirlpool - you'll have to find another way past.",
        description="Charybdis churns at the centre of the channel - not a creature you can strike, but a mouth in the sea itself.",
        loot=[create_hoplon_of_the_drowned()],
        experience_reward=50,
        gold_reward=25,
        defeat_effect=_charybdis_subsides,
    )

def create_hoplon_of_the_drowned() -> Armour:
    """Create the Hoplon of the Drowned - a light shield with 2 defence, between the Wooden Shield (light, 1) and the heavy shields. The Charybdis
    route's reward, comparable to the Boar's-Tusk Helm on Scylla's route. Thrown up from the wreckage when the puzzle is solved."""
    return Armour(
        name="Hoplon of the Drowned",
        description="A round bronze shield, crusted with salt and dented by something that wasn't a weapon. Someone carried it a long way to lose it here.",
        defence=2,
        slot="shield",
        weight="light",
        max_durability=12,
        article="the",
    )

def create_poseidon() -> Enemy:
    """Create Poseidon - floor 6's boss in Poseidon's Depths, and meant to be the hardest fight in the game so far.
    Phase 1: armoured, pierces armour with his trident (natural armour_pierce), and heals and braces readily - the sea is on his side. Its defeat
    brings two Hippocampi (next_wave_factories); once both fall, Poseidon (Earth-Shaker) appears. No rewards on this phase. Speaks to Poseidon's
    and Odysseus' descendants."""
    return Enemy(
        name="Poseidon",
        hp=48,
        attack_damage=13,
        armour=4,
        armour_pierce=3,
        heal_amount=8,
        brace_amount=4,
        caution_weight=1.4,
        article="",
        next_wave_factories=[create_hippocampus, create_hippocampus],
        next_phase_factory=create_poseidon_earth_shaker,
        description="Waist-deep in water that has no business being this far underground, trident resting on his shoulder. He hasn't decided yet whether you're worth standing up for.",
        ancestry_lines={
            "poseidon": (
                "He looks at you with something between fondness and disappointment. \"One of mine. And you came all this way to fight "
                "me.\" The water around him begins to stir. \"Then I'll show you what that blood is for.\""
            ),
            "odysseus": (
                "The water goes utterly still. \"Odysseus.\" He says it the way other gods say curses. \"I'd know that blood anywhere - I "
                "spent ten years drowning his crew. I won't need ten years for you.\""
            ),
        },
    )

def create_hippocampus() -> Enemy:
    """Create a Hippocampus - one of two spawned when Poseidon's first phase falls, guarding his second. Fast and aggressive, but fragile. Each
    drops a Kelp Poultice, giving the player a recovery window before the harder phase."""
    return Enemy(
        name="Hippocampus",
        hp=14,
        attack_damage=9,
        armour=1,
        loot=[create_kelp_poultice()],
        description="Half horse, half fish, and mostly teeth - it circles through the flooded hall faster than anything should be able to swim.",
        experience_reward=14,
        gold_reward=6,
        aggression_weight=1.5,
    )

def create_poseidon_earth_shaker() -> Enemy:
    """Create Poseidon (Earth-Shaker) - the final phase. Hits much harder, still pierces armour and still heals, but less, and less readily -
    dangerous rather than stubborn. Drops the Trident of the Depths."""
    return Enemy(
        name="Poseidon (Earth-Shaker)",
        hp=42,
        attack_damage=16,
        armour=3,
        armour_pierce=3,
        heal_amount=5,
        aggression_weight=1.6,
        caution_weight=0.8,
        article="",
        loot=[create_trident_of_the_depths()],
        description="The floor of the hall cracks and heaves beneath you. Whatever amusement he had is gone - this is the god who drowns cities.",
        experience_reward=90,
        gold_reward=50,
    )

def create_trident_of_the_depths() -> Weapon:
    """Create the Trident of the Depths - Poseidon's signature drop. Piercing, with cleave as its signature (its three prongs), making it the first
    weapon to combine the two. Cleave still only triggers on heavy attacks, like the Labrys."""
    return Weapon(
        name="Trident of the Depths",
        description="Not his own trident - he'd never part with that - but forged in the same deep places, and it remembers the sea.",
        damage=8,
        weapon_class="piercing",
        armour_pierce=3,
        cleave=True,
        article="the",
    )

def create_kelp_poultice() -> Consumable:
    """Create a Kelp Poultice - a 12 HP heal, dropped by each Hippocampus in Poseidon's fight."""
    return Consumable(
        name="Kelp Poultice",
        heal_amount=12,
        description="A wad of cold, salty kelp that draws the sting out of a wound faster than it has any right to."
    )

def create_odysseus(home_room: Room | None = None) -> Companion:
    """Create Odysseus - the second recruitable companion, in Shadow of Ithaca, and the clever counterpart to Achilles: he fights at range
    (attack_type 'ranged', so evasive enemies can't dodge him) and answers 'advice' (gives_advice). Recruitable once the 'suitors_cleared'
    story flag is set - the Throne Room sets it when its Suitors are cleared (Room.cleared_story_flag).

    Levels are kept separately per companion, so Achilles will be several levels ahead by the time Odysseus can join. His level-1 stats are
    set to roughly match Achilles at the end of floor 6, so recruiting him later isn't a step backwards. home_room follows the same placeholder
    pattern as create_shade_of_achilles()."""
    return Companion(
        name="Odysseus",
        hp=36,
        home_room=home_room or Room("Shadow of Ithaca"),
        attack_damage=11,
        armour=2,
        description="Grey at the temples, a great bow across his back, watching the door to the throne room the way a hunter watches a thicket.",
        brace_amount=3,
        heal_amount=4,
        attack_type="ranged",
        gives_advice=True,
        required_story_flag="suitors_cleared",
        recruit_blocked_message="\"Not while those men are still in my hall,\" Odysseus says. \"Deal with them first.\"",
        hint=(
            "\"Twenty years,\" he says quietly, without looking away from the door. \"Ten at Troy, ten getting home. And I come back to "
            "find my hall full of men eating my stores and courting my wife.\"\n\n"
            "At last he turns to you. \"I could use a strong arm. Clear them out of my hall, and I'm yours for whatever's left of this "
            "road. You'll find I'm more use than most - I tend to see things coming.\""
        ),
        hint_recruitable=(
            "\"My hall's quiet again. I owe you that.\" He shoulders the bow. \"Say 'recruit odysseus', and I'll walk the rest of this "
            "with you. Fair warning - I'll have opinions. Ask for my advice whenever you like.\""
        ),
        ancestry_lines={
            "odysseus": (
                "He looks at you properly, and his face softens. \"One of mine? You've the look of someone who talks their way out of "
                "things.\" A crooked smile. \"Good. That's the part worth inheriting.\""
            ),
        },
    )

def create_circe() -> Ally:
    """Create Circe - a transformation trading post in Muddy Pigsty, and the first merchant (see exchange.py). Her offers are of two kinds:
    gear the player has outgrown, turned into something useful, and fixed recipes that turn weaker consumables into stronger ones. Prices are
    provisional until gold income is settled - to be tuned alongside Charon's shop."""
    return Ally(
        name="Circe",
        description="She's scattering grain for the pigs and humming, and every so often one of them looks up at you with an expression far too human for a pig.",
        hint=(
            "\"Oh, don't look at them like that. They were rude to me.\" She dusts the grain from her hands. \"You, though - you've "
            "manners, and you've clearly been carrying things you've no use for. I can change them. For a price, naturally.\"\n\n"
            "\"Say 'offers' to see what I'll do, and 'exchange' with the number when something takes your fancy.\""
        ),
        required_items=[],
        items=[],
        offers=[
            Offer(gold_cost=20, output_factory=create_kelp_poultice, input_factory=create_bronze_xiphos),
            Offer(gold_cost=20, output_factory=create_kelp_poultice, input_factory=create_weathered_helm),
            Offer(gold_cost=30, output_factory=create_cup_of_kykeon, input_factory=create_bronze_breastplate),
            Offer(gold_cost=30, output_factory=create_cup_of_kykeon, input_factory=create_harpy_fletched_bow),
            Offer(gold_cost=10, output_factory=create_kelp_poultice, input_factory=create_small_healing_potion),
            Offer(gold_cost=20, output_factory=create_cup_of_kykeon, input_factory=create_wineskin_of_dionysus),
        ],
        exchange_line="She murmurs something over it, and when you look again, it isn't what it was.",
    )

def create_suitor() -> Enemy:
    """Create a Suitor - one of three nameless suitors in the Throne Room, alongside Antinous and Eurymachus. Individually the weakest enemy
    on floor 6; the room's difficulty comes from five attackers at once, meant to bring it close to (but deliberately not above)
    Poseidon. No item loot, since identical enemies can only carry identical items - but they're rich, so the gold adds up."""
    return Enemy(
        name="Suitor",
        hp=16,
        attack_damage=8,
        armour=1,
        description="Well fed, well dressed, and furious at the interruption - he's grabbed a spear from the wall and has no idea how to hold it properly.",
        experience_reward=14,
        gold_reward=15,
    )

def create_antinous() -> Enemy:
    """Create Antinous - the most arrogant of the suitors, and the first to die in the Odyssey. First in the room's enemy list, so he's the
    player's default target too. Aggressive. Drops Antinous' Goblet."""
    return Enemy(
        name="Antinous",
        hp=24,
        attack_damage=10,
        armour=2,
        article="",
        aggression_weight=1.5,
        loot=[create_antinous_goblet()],
        description="He's still holding his golden goblet, wine sloshing over the rim, and he looks at you as though you're a servant who's forgotten their place.",
        experience_reward=24,
        gold_reward=45,
        ancestry_lines={
            "odysseus": (
                "Antinous' goblet stops halfway to his mouth. \"That face.\" For the first time, he looks uncertain. \"No. He's dead. "
                "He's been dead for years.\" He throws the goblet aside. \"Kill it anyway.\""
            ),
        },
    )

def create_eurymachus() -> Enemy:
    """Create Eurymachus - the suitor who tries to talk his way out of it in the Odyssey. Defensive rather than aggressive: braces readily and
    patches himself up, dragging the fight out. Drops a Kelp Poultice."""
    return Enemy(
        name="Eurymachus",
        hp=22,
        attack_damage=9,
        armour=2,
        article="",
        brace_amount=3,
        heal_amount=4,
        caution_weight=1.3,
        loot=[create_kelp_poultice()],
        description="Smiling, palms open, already explaining that none of this was really his idea - with a sword held low behind his back.",
        experience_reward=22,
        gold_reward=40,
    )

def create_antinous_goblet() -> StatusEffectItem:
    """Create Antinous' Goblet - a strong heal-over-time (Regen 5 for 3 turns, 15 HP in all), and a free action like any positive
    StatusEffectItem. Dropped by Antinous."""
    return StatusEffectItem(
        name="Antinous' Goblet",
        description="Solid gold, dented where it hit the floor, and still half full of very good wine.",
        effect_name="Regen",
        amount=5,
        duration=3,
        article="",
    )

def create_penelope() -> Ally:
    """Create Penelope - in the Bedchamber of Odysseus, the last room on floor 6, beyond the Suitors. Gives Penelope's Thread, the first
    LoyaltyToken, freely. Reacts once to Odysseus - their reunion, the end of the Odyssey - and to Achilles, through companion_lines."""
    return Ally(
        name="Penelope",
        description="She sits at the loom with her back to the door, and doesn't turn when you come in - but her hands have stopped moving.",
        hint=(
            "She pulls a thread free with practised fingers, undoing a whole row. \"Habit,\" she says, seeing your look. \"For three years I "
            "wove this by day and unpicked it by night, and not one of those men ever noticed.\"\n\n"
            "She sets the shuttle down. \"You've cleared my hall. I have no gold to give you - but I know something about standing by someone "
            "when everyone tells you to give up.\" She snips a length of thread from the loom and holds it out. \"Keep this with you, and "
            "whoever walks beside you will find it much harder to leave. Say 'take penelope's thread from penelope'.\""
        ),
        required_items=[],
        items=[create_penelopes_thread()],
        companion_lines={
            "Odysseus": (
                "Penelope rises from the loom - and stops. For a long moment, neither of them moves. \"You look older,\" she says at last, and "
                "her voice breaks halfway through. Odysseus laughs, or tries to. \"So I've been told.\"\n\n"
                "She crosses the room and takes his face in her hands, as if making sure it's real. \"The bed,\" she whispers. \"Tell me about "
                "the bed.\" \"An olive tree, still rooted in the ground. I built the room around it.\" She closes her eyes. \"Then it's you.\""
            ),
            "Shade of Achilles": (
                "She looks at Achilles for a long moment. \"My husband went to war because of men like you.\" It's not quite an accusation. "
                "\"He came home anyway. See that this one does too.\""
            ),
        },
    )

def create_penelopes_thread() -> LoyaltyToken:
    """Create Penelope's Thread - the first LoyaltyToken. While held, the player's companion survives the first blow each fight that would down
    them. Given by Penelope."""
    return LoyaltyToken(
        name="Penelope's Thread",
        description="A single length of thread from her loom - woven by day, unpicked by night, for three years. It's held on longer than anyone expected.",
        article="",
    )

def build_floor_6() -> tuple[Room, dict[str, Room]]:
    """The Odyssey and the Open Sea - Bright Cave, Calm Waters, Cavern of Polyphemus, Rocky Shore, Narrow River, Poseidons Depths, Shadow of Ithaca, Muddy Pigsty, Throne Room of Odysseus, and Bedchamber of Odysseus."""
    bright_cave = Room(name="Bright Cave", description="Sunlight streams in from an opening far above, illuminating bones picked disturbingly clean.")
    calm_waters = Room(name="Calm Waters", description="The sea here is unnervingly still, and faint singing drifts across it from somewhere you can't quite place.")
    cavern_of_polyphemus = Room(name="Cavern of Polyphemus", description="A single vast eye socket, carved crudely into the far wall, watches the room, long since gone dark.")
    rocky_shore = Room(name="Rocky Shore", description="Jagged black rocks jut from churning water, six shadows moving beneath the surface in perfect, unsettling unison.")
    narrow_river = Room(name="Narrow River", description="The current here pulls hard toward a whirlpool that never quite stops turning. A gnarled fig tree clings to the rock above it, and a small raft bobs at the water's edge, already being drawn in.")
    poseidons_depths = Room(name="Poseidon's Depths", description="The water opens into a vast underwater hall, pressure bearing down from every direction at once.")
    shadow_of_ithaca = Room(name="Shadow of Ithaca", description="A modest, homely room, oddly warm compared to everywhere else on this floor. Something about the hearth feels like a doorway that isn't quite closed - say 'forge' if you feel the pull toward it.")
    muddy_pigsty = Room(name="Muddy Pigsty", description="Thick mud and the smell of something herbal linger together in a low, cramped pen.")
    throne_room_of_odysseus = Room(name="Throne Room of Odysseus", description="An once-grand hall, now crowded and disordered, the throne itself sitting conspicuously empty.")
    bedchamber_of_odysseus = Room(name="Bedchamber of Odysseus", description="A quiet room untouched by the chaos elsewhere, a loom standing half-finished in the corner.")

    bright_cave.connect("south", calm_waters)
    calm_waters.connect("north", bright_cave)
    calm_waters.connect("east", cavern_of_polyphemus)
    calm_waters.connect("west", rocky_shore)
    calm_waters.connect("south", narrow_river)
    cavern_of_polyphemus.connect("west", calm_waters)
    rocky_shore.connect("east", calm_waters)
    rocky_shore.connect("south", poseidons_depths)
    narrow_river.connect("north", calm_waters)
    narrow_river.connect("west", poseidons_depths)
    poseidons_depths.connect("north", rocky_shore)
    poseidons_depths.connect("east", narrow_river)
    poseidons_depths.connect("south", shadow_of_ithaca)
    shadow_of_ithaca.connect("north", poseidons_depths)
    shadow_of_ithaca.connect("east", muddy_pigsty)
    shadow_of_ithaca.connect("south", throne_room_of_odysseus)
    muddy_pigsty.connect("west", shadow_of_ithaca)
    throne_room_of_odysseus.connect("north", shadow_of_ithaca)
    throne_room_of_odysseus.connect("west", bedchamber_of_odysseus)
    bedchamber_of_odysseus.connect("east", throne_room_of_odysseus)

    calm_waters.add_interaction("listen", _listen_to_sirens, _sirens_offer_open, "The Sirens are silent now.")
    calm_waters.add_interaction("give in", _give_in_to_sirens, _sirens_offer_open, "The Sirens are silent now.")
    calm_waters.add_interaction("resist", _resist_sirens, _sirens_offer_open, "There's nothing left to resist.")
    for verb in ("watch", "climb", "let go", "row"):
        narrow_river.add_interaction(verb, _charybdis_verb(verb), _charybdis_unsolved, "The water is calm now - Charybdis has let you pass.")

    bright_cave.add_enemy(create_antiphates())
    bright_cave.add_enemy(create_laestrygonian())
    cavern_of_polyphemus.add_enemy(create_polyphemus())
    for _ in range(6):
        rocky_shore.add_enemy(create_head_of_scylla())
    narrow_river.add_enemy(create_charybdis())
    poseidons_depths.add_enemy(create_poseidon())
    throne_room_of_odysseus.add_enemy(create_antinous())
    throne_room_of_odysseus.add_enemy(create_eurymachus())
    for _ in range(3):
        throne_room_of_odysseus.add_enemy(create_suitor())

    muddy_pigsty.add_ally(create_circe())
    bedchamber_of_odysseus.add_ally(create_penelope())

    shadow_of_ithaca.add_companion(create_odysseus(shadow_of_ithaca))

    cavern_of_polyphemus.add_item(create_wheel_of_cheese())
    cavern_of_polyphemus.add_item(create_wheel_of_cheese())
    rocky_shore.add_item(create_boars_tusk_helm())

    calm_waters.advice = (
        "I heard them once, tied to my own mast. What they offer is real - and so is what it costs. Don't let anyone tell you the "
        "choice is easy."
    )
    narrow_river.advice = "When she starts to swallow, get above her. I'll say no more than that - I'd hate to spoil it."

    rocky_shore.guard_exit("south")
    narrow_river.guard_exit("west")
    poseidons_depths.guard_exit("south")
    throne_room_of_odysseus.guard_exit("west")

    throne_room_of_odysseus.cleared_story_flag = "suitors_cleared"
    throne_room_of_odysseus.cleared_message = (
        "The hall falls silent at last. Somewhere back in the Shadow of Ithaca, a man who has waited twenty years lets out a long breath."
    )

    return bright_cave, {
        room.name: room for room in (bright_cave, calm_waters, cavern_of_polyphemus, rocky_shore, narrow_river, poseidons_depths, shadow_of_ithaca, muddy_pigsty, throne_room_of_odysseus, bedchamber_of_odysseus)
    }