"""Floor 7 (Prophecy and the Elder Dead) - Chamber of the Oracle, Shadow of Thebes, Bedchamber of Persephone."""

from dungeon_crawler.world import Room
from dungeon_crawler.characters import Ally
from dungeon_crawler.items import Consumable, StatusEffectItem, Weapon
from dungeon_crawler.dialogue import DialogueNode, DialogueOption
from dungeon_crawler.exploration import floor_traits, next_floor_key, take_opening_line

ORACLE_PROPHECIES = 3
ORACLE_TWIST = (
    "Her eyes roll back, and the voice that comes out of her is not hers. \"The one you hunt does not guard a throne. He guards a door - "
    "and you will be the one to open it.\""
)
ORACLE_PHRASES = {
    "heavy_armour": "Below, bronze sits thick on those who wait for you. Edges will skid; points will not.",
    "evasive": "Something below never lets you close. Only what flies will reach it.",
    "heals": "What you wound below will close its wounds. Strike before they mend.",
    "pierces": "Below, your armour is a promise that will be broken.",
    "numerous": "Below, you will not face one. You will face many.",
    "puzzle": "Below, there is a thing no blade can reach. Look for the other way.",
}
ORACLE_NOTHING_STRANGE = "Below, there is only strength against strength. I see no trick in it."
PROMISED_MERCY = "promised_mercy"
REFUSED_MERCY = "refused_mercy"
POMEGRANATE_GIVEN = "persephone_pomegranate_given"

def _prophecies_used(room) -> int:
    return sum(1 for flag in room.flags if flag.startswith("prophecy:"))

def _prophecies_remain(player, room) -> bool:
    return _prophecies_used(room) < ORACLE_PROPHECIES

def _with_twist(oracle, player, message: str) -> str:
    return "\n\n".join(line for line in (take_opening_line(oracle, player), message) if line)

def _remaining_note(room) -> str:
    left = ORACLE_PROPHECIES - _prophecies_used(room)
    return "(She will answer no more.)" if left == 0 else f"({left} prophecies remain.)"

def _ask_ahead(oracle, all_floors):
    """'ask ahead' - the next floor's traits in the Oracle's voice. Not used up if there's no floor below, it has no enemies yet, or she's
    already foretold it."""
    def handler(player, room) -> str:
        floor_key = next_floor_key(all_floors, player)
        if floor_key is None or not any(r.enemies for r in all_floors[floor_key].values()):
            return _with_twist(oracle, player, "\"I see nothing below you that I can name.\" (That prophecy was not spent.)")
        flag = f"prophecy:ahead:{floor_key}"
        if flag in room.flags:
            return _with_twist(oracle, player, "\"I have told you what waits below. Go and meet it.\" (That prophecy was not spent.)")
        room.flags.add(flag)
        traits = floor_traits(all_floors[floor_key])
        lines = [ORACLE_PHRASES[trait] for trait in traits] or [ORACLE_NOTHING_STRANGE]
        return _with_twist(oracle, player, "\n".join(f"\"{line}\"" for line in lines) + f"\n{_remaining_note(room)}")
    return handler

def _ask_secrets(oracle, all_floors):
    """'ask secrets' - the first room, on floors already reached, with a hidden exit the player hasn't found and she hasn't named. Warns if
    finding it needs more intellect than the player has. Not used up if there's nothing left to reveal. Assumes examining a room removes its
    revealed exits from hidden_exits, as uncleared already relies on."""
    def handler(player, room) -> str:
        for floor_key, rooms in all_floors.items():
            if floor_key not in player.visited_floors:
                continue
            for candidate in rooms.values():
                flag = f"prophecy:secret:{candidate.name}"
                if candidate.hidden_exits and flag not in room.flags:
                    room.flags.add(flag)
                    line = f"\"In {candidate.name}, a way lies hidden that you have walked straight past.\""
                    if candidate.required_intellect > player.intellect:
                        line += f"\n\"It will not show itself to a mind duller than {candidate.required_intellect}.\""
                    return _with_twist(oracle, player, f"{line}\n{_remaining_note(room)}")
        return _with_twist(oracle, player, "\"You have missed nothing I can see.\" (That prophecy was not spent.)")
    return handler

def _oracle_greeting(player) -> str:
    return (
        "The Pythia sits above the fissure, breathing the smoke, and speaks without looking at you. \"Ask and I will answer - three "
        "times, and no more. Ask what lies ahead, or ask what you have missed.\""
    )

def create_oracle() -> Ally:
    """Create the Oracle - the Pythia of Delphi, in the Chamber of the Oracle. Gives the twist prophecy once, free, then three prophecies the
    player directs ('ask ahead', 'ask secrets' - wired in wire_floor_7_seers(), since they need the whole world)."""
    return Ally(
        name="Oracle",
        description="A woman on a tripod above a crack in the floor, veiled in smoke, murmuring to something no one else can hear.",
        opening_line=ORACLE_TWIST,
        dialogue_function=_oracle_greeting,
    )

def _tiresias_reading(all_floors):
    """Build Tiresias' readings: the player's own readiness, weighed against the next floor's traits. Free and unlimited - regenerated each
    time, so it always reflects the player as they are now."""
    def reading(player) -> str:
        lines = []
        points = player.skill_tree.skill_points
        if points:
            lines.append(f"You hold {points} skill point{'s' if points != 1 else ''} you have not spent. Spend them - you will not get the chance later.")

        floor_key = next_floor_key(all_floors, player)
        traits = floor_traits(all_floors[floor_key]) if floor_key else []
        weapon = player.equipped_melee_weapon
        companion = player.companion
        can_reach_at_range = (
            player.equipped_ranged_weapon is not None or player.can_ranged_without_weapon or bool(player.known_spells)
            or (companion is not None and companion.attack_type == "ranged")
        )
        if "evasive" in traits and not can_reach_at_range:
            lines.append("Something below keeps its distance, and you have nothing that reaches it - no bow, no spell.")
        if "pierces" in traits and player.armour_weight_penalty() > 0:
            lines.append("You pay for your armour with every swing, and what waits below will cut straight through it anyway.")
        if "heavy_armour" in traits and (weapon is None or (weapon.weapon_class not in ("piercing", "heavy") and not weapon.armour_pierce)):
            lines.append("Your blade will skid off what waits below. Carry something with a point.")
        if "numerous" in traits and (weapon is None or not weapon.cleave):
            lines.append("Many will come at you at once, and nothing you carry strikes more than one.")

        unused = next(
            (item for item in player.inventory.items if isinstance(item, Weapon) and not item.equipped
             and (item.cleave or item.lifesteal or item.poison_chance or item.blind_chance)),
             None,
        )
        if unused is not None:
            lines.append(f"You carry {unused.with_article()} and never raise it.")
        has_healing = any(
            (isinstance(item, Consumable) and item.heal_amount > 0) or (isinstance(item, StatusEffectItem) and item.amount > 0)
            for item in player.inventory.items
        )
        if not has_healing:
            lines.append("You carry nothing to mend yourself.")
        if companion is None:
            lines.append("You walk alone. You need not.")
        elif not companion.is_alive():
            lines.append(f"{companion.name} lies broken beside you. See to that before you go down.")

        opening = "The old man turns his blind eyes on you, and they seem to see further than yours ever have."
        if not lines:
            return f"{opening}\n\"I look, and I find nothing waiting. Go down, then.\""
        return opening + "\n" + "\n".join(f"\"{line}\"" for line in lines)
    return reading

def create_tiresias() -> Ally:
    """Create Tiresias - the blind seer, in the Shadow of Thebes. His readings are generated by _tiresias_reading(), wired in
    wire_floor_7_seers() because they need the whole world. Until then he has a plain placeholder line."""
    return Ally(
        name="Tiresias",
        description="An old man leaning on a staff, eyes white and unseeing, head tilted as if listening to something behind you.",
        hint="\"Not yet,\" he murmurs. \"Come back when I can see you properly.\"",
    )

def create_pomegranate() -> Consumable:
    """Create the Pomegranate - a full heal, kept as a consumable (heal_amount far above any max HP, capped by Consumable.use()). Given by
    Persephone; floor 7's recovery before Cerberus."""
    return Consumable(
        name="Pomegranate",
        heal_amount=999,
        description="Split open, the seeds glowing faintly red. Eating even a few would restore you completely - and she'd know better than anyone what else they can do.",
    )

def _give_pomegranate(player) -> str:
    if POMEGRANATE_GIVEN in player.story_flags:
        return ""
    player.story_flags.add(POMEGRANATE_GIVEN)
    player.inventory.add(create_pomegranate())
    return "Before you can speak, she presses something into your hands - a pomegranate, split open, the seeds glowing faintly. (You receive a Pomegranate.)"

def _choice_not_made(player) -> bool:
    return PROMISED_MERCY not in player.story_flags and REFUSED_MERCY not in player.story_flags

def _set_flag(flag):
    def effect(player) -> str:
        player.story_flags.add(flag)
        return ""
    return effect

def create_persephone() -> Ally:
    """Create Persephone - in her bedchamber, the last room on floor 7, and the first branching dialogue. Gives a Pomegranate the first time
    you speak to her, whatever you choose. Gives her side of the twist (why Hades stopped judging the dead) as one topic, and asks you to spare
    him - setting 'promised_mercy' or 'refused_mercy', a final choice. Either answer opens the descent to floor 8, which is story-gated on it
    (build_world()); which one is planned to decide whether Hades can yield and become a companion there."""
    back = DialogueOption("Ask something else", "start")
    leave = DialogueOption("Leave her be", None)
    return Ally(
        name="Persephone",
        description="She sits between the two halves of the room - flowers on one side, frost on the other - as though she belongs to neither.",
        dialogue={
            "start": DialogueNode(
                text="\"You came down a long way to find him.\" She doesn't need to say who. \"Ask what you want to ask.\"",
                on_enter=_give_pomegranate,
                options=[
                    DialogueOption("Ask why Hades stopped judging the dead", "why"),
                    DialogueOption("Ask what she wants of you", "request", available=_choice_not_made),
                    leave,
                ],
            ),
            "why": DialogueNode(
                text=(
                    "\"He hasn't stopped caring for them. He loves this place more than I ever managed to.\" She looks at the frost. \"But "
                    "something takes everything he has - every hour, every day - and there's nothing left over for the dead. He won't tell me "
                    "what. I stopped asking a long time ago.\""
                ),
                options=[back, leave],
            ),
            "request": DialogueNode(
                text=(
                    "\"When you reach him, you'll think the worst of him. Everyone does.\" She meets your eyes. \"Beat him if you must. But "
                    "don't kill him. I can't tell you why - you'll understand when you see what he's been doing.\""
                ),
                options=[
                    DialogueOption("Promise to spare him", "promised", effect=_set_flag(PROMISED_MERCY)),
                    DialogueOption("Refuse", "refused", effect=_set_flag(REFUSED_MERCY)),
                    DialogueOption("Say you need to think about it", "start"),
                ],
            ),
            "promised": DialogueNode(
                text="Something in her shoulders loosens. \"Thank you. He won't thank you - not at first. But he will.\"",
                options=[leave]
            ),
            "refused": DialogueNode(
                text="She nods slowly, as though she expected nothing else. \"Then I hope you're right about him. I don't think you are.\"",
                options=[leave]
            ),
        },
    )

def wire_floor_7_seers(all_floors: dict[str, dict[str, Room]]) -> None:
    """Give the Oracle her questions and Tiresias his readings - both need the whole world, so this runs from build_world() once every floor
    exists. Rebuilt with the world on every load, so nothing here needs saving."""
    chamber = all_floors["floor_7"]["Chamber of the Oracle"]
    oracle = chamber.allies[0]
    chamber.add_interaction("ask ahead", _ask_ahead(oracle, all_floors), _prophecies_remain, "\"I have said all I will say.\"")
    chamber.add_interaction("ask secrets", _ask_secrets(oracle, all_floors), _prophecies_remain, "\"I have said all I will say.\"")

    tiresias = all_floors["floor_7"]["Shadow of Thebes"].allies[0]
    tiresias.dialogue_function = _tiresias_reading(all_floors)


def build_floor_7() -> tuple[Room, dict[str, Room]]:
    """Prophecy & the Elder Dead - Chamber of the Oracle, Shadow of Thebes, and Bedchamber of Persephone."""
    chamber_of_the_oracle = Room(name="Chamber of the Oracle", description="Smoke curls from a fissure in the floor, and the air itself seems to hum with something just out of hearing.")
    shadow_of_thebes = Room(name="Shadow of Thebes", description="A still, dim chamber where even the shadows seem to be listening.")
    bedchamber_of_persephone = Room(name="Bedchamber of Persephone", description="Half the room blooms with strange dark flowers; the other half lies frostbitten and bare. Somewhere between the two, a thread of warmth that doesn't belong to either - say 'forge' if you feel the pull toward it.")

    chamber_of_the_oracle.connect("south", shadow_of_thebes)
    shadow_of_thebes.connect("north", chamber_of_the_oracle)
    shadow_of_thebes.connect("south", bedchamber_of_persephone)
    bedchamber_of_persephone.connect("north", shadow_of_thebes)

    chamber_of_the_oracle.add_ally(create_oracle())
    shadow_of_thebes.add_ally(create_tiresias())
    bedchamber_of_persephone.add_ally(create_persephone())

    return chamber_of_the_oracle, {
        room.name: room for room in (chamber_of_the_oracle, shadow_of_thebes, bedchamber_of_persephone)
    }