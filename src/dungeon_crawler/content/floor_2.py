"""Floor 2 (Domains of the Gods) - Library of Athena, Armoury of Ares, Trophy Room of Zeus, Hall of Hermes, Forge of Prometheus, Practice Chamber."""

from dungeon_crawler.world import Room
from dungeon_crawler.items import Armour, Weapon, SkillPointReward
from dungeon_crawler.characters import Enemy, Ally
from dungeon_crawler.dialogue import DialogueNode, DialogueOption

PROMETHEUS_OFFER_MADE = "prometheus_offer_made"
HARDCORE = "hardcore"

def create_practice_dummy() -> Enemy:
    """Player-customisable practice dummy - respawns=True (see handle_enemy_defeat()), zero XP/gold reward regardless of what 'dummy set'
    changes. Distinct from the narrative Training Dummy at Chamber of Chiron (South) - that one is a one-time tutorial enemy;
    this is a genuine, repeatable testing sandbox."""
    return Enemy(
        name="Practice Enemy",
        hp=20,
        attack_damage=1,
        armour=0,
        description="A well-worn straw dummy, stitched back together more times than anyone's bothered to count.",
        experience_reward=0,
        gold_reward=0,
        respawns=True,
    )

def create_athena() -> Ally:
    """Create the Athena ally for floor 2, placed in the Library of Athena by build_floor_2()."""
    return Ally(
        name="Athena",
        description="Calm, measured, and faintly amused — as if she already knows exactly how this ends.",
        hint=(
            "She closes the scroll she's reading, unhurried. \"So Chiron sent another. Good. Listen carefully, because I will "
            "only explain this once.\"\n\n"
            "\"Hades has stopped judging the dead. The souls still arrive, but nothing is decided - they pile up in Asphodel, the "
            "old monsters of the deeper levels wander wherever they please, and the river runs thick with the unsettled. It is the "
            "oldest law beneath the earth, and he has simply set it aside.\"\n\n"
            "\"We cannot go down and make him answer for it. An oath older than any of us keeps gods out of his halls - these "
            "rooms are as far as we may reach. So we send you.\"\n\n"
            "She taps the table. \"You'll need better than bronze where you're going. At the bottom of the next level there's a "
            "forest, and in it a centaur who shoots at anything that moves. Bring me its bow, and I'll give you something worth "
            "wearing.\""
        ),
        hint_complete="\"The centaur's bow. So you closed the distance - good. Say 'trade' and it's yours.\"",
        hint_traded="\"Wear it well. Hades is patient, and so are his halls - don't mistake either for weakness.\"",
        post_trade_message="\"The owl on it watches whichever side you forget to.\"",
        ancestry_lines={
            "athena": (
                "Her eyes rest on you a moment longer than they need to. \"Mine, then. I wondered when one of you would come down.\" "
                "A faint smile. \"Don't make me regret the family resemblance.\""
            ),
        },
        required_items = ["Centaur's Broken Bow"],
        items=[],
        reward=create_breastplate_of_athena()
    )

def create_ares() -> Ally:
    """Create the Ares ally for floor 2, placed in the Armoury of Ares by build_floor_2()."""
    return Ally(
        name="Ares",
        description="He barely looks up from sharpening a blade, though he's clearly aware of every move you make.",
        hint=(
            "\"Athena's told you the story, I expect. She likes telling it.\" He tests the edge against his thumb. \"Here's the part "
            "she leaves out: you'll have to kill things to get there, and most of them are bigger than you.\"\n\n"
            "\"Two levels down, past the forest and into the labyrinth, there's a Cyclops. Bring me its eye, and I'll give you a "
            "spear that doesn't bend.\""
        ),
        hint_complete="\"That's the eye. Say 'trade'.\"",
        hint_traded="\"Don't hold it like a broom. Point, then push.\"",
        post_trade_message="\"Now go and use it on something that deserves it.\"",
        ancestry_lines={
            "ares": "He looks you over properly for the first time. \"Well. You've got my shoulders. Let's see if you've got the rest.\"",
        },
        required_items=["Cyclops' Eye"],
        items=[],
        reward=create_spear_of_ares()
    )

def create_hermes() -> Ally:
    """Create the Hermes ally for floor 2, placed in the Hall of Hermes by build_floor_2()."""
    return Ally(
        name="Hermes",
        description="Never quite still, halfway through some errand even while talking to you.",
        hint=(
            "\"Messages, messages - and not one of them delivered, because the dead aren't moving on to receive them.\" He glances "
            "up, already halfway into another stack.\n\n"
            "\"You want to help? There's a vault beneath the landing at Styx Crossing - sealed off, easy to miss. 'examine' the "
            "stonework there and you'll find the way down. Bring me a bone from whatever's guarding it. Proof you've been somewhere "
            "nobody's meant to go - I collect those.\""
        ),
        hint_complete="\"Oh, that's a good one. Say 'trade' - quickly, I've places to be.\"",
        hint_traded="\"Still here? The dead won't judge themselves - which is rather the whole problem, isn't it?\"",
        post_trade_message="\"A little something for your trouble. Use it wisely - or quickly, which is usually the same thing.\"",
        ancestry_lines={
            "hermes": (
                "\"Oh - it's one of mine!\" For a moment, he actually stops moving, \"You'll be fine. Probably. We're very good at "
                "getting out of things.\""
            ),
        },
        required_items=["Skeleton Bone"],
        reward=create_hermes_favour(),
        items=[]
    )

def _prometheus_opening(player) -> str:
    """Where Prometheus' conversation begins: his offer if he's never made it, otherwise a short line that depends on the answer."""
    if PROMETHEUS_OFFER_MADE not in player.story_flags:
        return "offer"
    return "after_accepted" if HARDCORE in player.story_flags else "after_declined"

def _make_offer(player) -> str:
    """The offer counts as made the moment it's shown - declining, or leaving mid-conversation, both use it up."""
    player.story_flags.add(PROMETHEUS_OFFER_MADE)
    return ""

def _accept_hardcore(player) -> str:
    """Turn hardcore on for this save, and fully repair every piece of armour the player is carrying, equipped or not. No other reward -
    hardcore is an optional challenge, not a trade."""
    player.story_flags.add(HARDCORE)
    for item in player.inventory.items:
        if isinstance(item, Armour):
            item.durability = item.max_durability
    return "(Hardcore mode is now on for this save. All your armour has been fully repaired.)"

def create_prometheus() -> Ally:
    """Create Prometheus - in the Forge of Prometheus. Makes a one-time offer: hardcore mode for the rest of the playthrough, in exchange for a
    full repair of the player's armour. The offer counts as made as soon as it's shown. Accepting takes two steps, since it can't be undone. A
    save loaded from before meeting him gets the offer again, since in that save it was never made."""
    leave = DialogueOption("Leave him to his work", None)
    return Ally(
        name="Prometheus",
        description="Chained but unbroken, watching you with the weary patience of someone who's paid dearly for helping before.",
        dialogue_start=_prometheus_opening,
        dialogue={
            "offer": DialogueNode(
                on_enter=_make_offer,
                text=(
                    "He looks up from the anvil for the first time, and the chains on his wrists clink. \"I gave your kind fire once, and I've "
                    "paid for it every day since. So I know something about choices that can't be taken back.\"\n\n"
                    "\"Here's one. I'll mend everything you're carrying, good as the day it was forged. In return, you walk the rest of this road "
                    "with no second chances. Fall once, and it's over.\"\n\n"
                    "\"I make this offer once.\""
                ),
                options=[
                    DialogueOption("Accept his offer", "confirm"),
                    DialogueOption("Decline", "declined"),
                ],
            ),
            "confirm": DialogueNode(
                text=(
                    "\"Be sure,\" he says. \"From this moment, if you die, this journey is over. Your save is gone, and there's no reloading it. "
                    "Nothing in this world will undo that.\""
                ),
                options=[
                    DialogueOption("Accept - no second chances", "accepted", effect=_accept_hardcore),
                    DialogueOption("Think again", "offer"),
                ],
            ),
            "accepted": DialogueNode(
                text=(
                    "He takes your armour one piece at a time, and the forge flares white. When he hands it back, every dent and crack is gone. "
                    "\"There. Now you know what it costs to have something made whole.\"\n\n"
                    "\"If it wears thin again, bring it here and say 'repair' followed by its name. I'll charge you like anyone else - but I'll do it.\""
                ),
                options=[leave],
            ),
            "declined": DialogueNode(
                text=(
                    "He nods, and turns back to the anvil. \"Wise, probably. Most who come here would rather live.\"\n\n"
                    "\"The forge is yours whenever you need it. Bring your armour here and say 'repair' followed by its name.\""
                ),
                options=[leave],
            ),
            "after_accepted": DialogueNode(
                text="\"Still walking without a second chance, I see.\" Something that might be respect. \"Keep going.\"",
                options=[leave],
            ),
            "after_declined": DialogueNode(
                text=(
                    "\"The offer's gone - I only make it once.\" He doesn't look up. \"But the forge is still yours. 'repair' and the item's name, "
                    "whenever you need it.\""
                ),
                options=[leave],
            ),
        },
    )

def create_breastplate_of_athena() -> Armour:
    """Create the Breastplate of Athena armour - Athena's trade reward, reachable now that create_athena() is placed in build_floor_2()."""
    return Armour(
        name="Breastplate of Athena",
        description="Cool to the touch even in the deepest heat, etched with an owl that seems to watch whichever way danger comes from.",
        defence=4,
        weight="light",
        max_durability=15,
        article="the",
    )

def create_spear_of_ares() -> Weapon:
    """Create the Spear of Ares weapon."""
    return Weapon(
        name="Spear of Ares",
        damage=6,
        description="Bronze-tipped and perfectly balanced - it feels less like you're holding a weapon, and more like it's holding you steady",
        weapon_class="piercing",
        armour_pierce=2,
        article="the",
    )

def create_hermes_favour() -> SkillPointReward:
    """Create the Favour of Hermes skill point reward - Hermes' trade reward, reachable now that create_hermes() is placed in build_floor_2()."""
    return SkillPointReward(
        name="Favour of Hermes",
        description="Quick, light, and gone before you've noticed - much like the god who gave it.",
        points = 1,
        article="the",
    )

def build_floor_2() -> tuple[Room, dict[str, Room]]:
    """Domains of the Gods - Library of Athena, Armoury of Ares, Trophy Room of Zeus, Hall of Hermes, and Forge of Prometheus."""
    library_of_athena = Room(
        name="Library of Athena",
        description="Towering shelves of scrolls creak under their own weight; an owl watches from the rafters, unblinking.",
    )
    armoury_of_ares = Room(
        name="Armoury of Ares",
        description="Racks of corroded bronze weapons line the walls, still faintly warm to the touch.",
        examine_text="One section of the far wall looks less like stone, and more like it's been built to resemble stone.",
        required_intellect=3
    )
    hall_of_hermes = Room(
        name="Hall of Hermes",
        description="A cluttered waypoint stacked with parcels and letters never delivered, sandals of every size hung along one wall.",
    )
    forge_of_prometheus = Room(
        name="Forge of Prometheus",
        description="The air shimmers with heat from a fire that never seems to go out, chained tools scattered across a worn anvil. Faint doorways shimmer at the edges of the room, each one waiting to be opened from the other side.",
        is_forge=True
    )
    practice_chamber = Room(
        name="Practice Chamber",
        description="A sand-floored alcove beside the forge's heat, a single straw-and-rope dummy standing ready at its centre.",
        is_practice_chamber=True
    )
    trophy_room_of_zeus = Room(
        name="Trophy Room of Zeus",
        description="A narrow chamber lit by no visible flame, empty display alcoves lining every wall, patiently waiting to be filled.",
    )

    library_of_athena.connect("west", armoury_of_ares)
    library_of_athena.connect("south", hall_of_hermes)
    armoury_of_ares.connect("east", library_of_athena)
    armoury_of_ares.add_hidden_exit("north", trophy_room_of_zeus)
    trophy_room_of_zeus.connect("south", armoury_of_ares)
    hall_of_hermes.connect("north", library_of_athena)
    hall_of_hermes.connect("south", forge_of_prometheus)
    forge_of_prometheus.connect("north", hall_of_hermes)
    forge_of_prometheus.connect("east", practice_chamber)
    practice_chamber.connect("west", forge_of_prometheus)

    practice_chamber.add_enemy(create_practice_dummy())
    library_of_athena.add_ally(create_athena())
    armoury_of_ares.add_ally(create_ares())
    hall_of_hermes.add_ally(create_hermes())
    forge_of_prometheus.add_ally(create_prometheus())

    return library_of_athena, {
        room.name: room for room in (library_of_athena, armoury_of_ares, hall_of_hermes, forge_of_prometheus, trophy_room_of_zeus, practice_chamber)
    }