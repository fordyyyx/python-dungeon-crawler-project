from dungeon_crawler.characters import Player
from dungeon_crawler.world import Room
from dungeon_crawler.items import Trophy, Weapon, QuestItem
from dungeon_crawler.trophies import TROPHY_ROOM_COMPLETE, describe_plinths, place_trophies

PLINTHS = [("Horn", "A curved notch."), ("Nail", "A tiny plinth."), ("Heart", "A scorched plinth.")]

def trophy_room(milestones=None) -> Room:
    room = Room("Trophy Room", is_trophy_room=True)
    room.trophy_plinths = list(PLINTHS)
    room.trophy_milestones = milestones or {}
    return room

def trophy(name: str) -> Trophy:
    return Trophy(name=name, description="", article="the")

def hunter(*names: str) -> Player:
    """A player carrying a trophy of each name given."""
    player = Player(name="Hero", hp=20)
    for name in names:
        player.inventory.add(trophy(name))
    return player

def test_trophy_room_complete_flag_name():
    assert TROPHY_ROOM_COMPLETE == "trophy_room_complete"

# ---- describe_plinths ----

def test_describe_plinths_shows_every_clue_while_nothing_is_placed():
    assert describe_plinths(trophy_room()) == (
        "Trophies placed: 0 of 3.\n"
        "  - (empty) A curved notch.\n"
        "  - (empty) A tiny plinth.\n"
        "  - (empty) A scorched plinth."
    )

def test_describe_plinths_names_a_placed_trophy_instead_of_its_clue():
    room = trophy_room()
    room.placed_trophies.add("Nail")
    assert describe_plinths(room) == (
        "Trophies placed: 1 of 3.\n"
        "  - (empty) A curved notch.\n"
        "  - Nail\n"
        "  - (empty) A scorched plinth."
    )

def test_describe_plinths_never_names_a_trophy_not_yet_placed():
    """The clues are the only hint - an empty plinth mustn't give its trophy's name away."""
    description = describe_plinths(trophy_room())
    assert all(name not in description for name, _ in PLINTHS)

# ---- place_trophies: one trophy ----

def test_place_trophies_outside_the_trophy_room_changes_nothing():
    player = hunter("Horn")
    message = place_trophies("horn", Room("Hall"), player)
    assert message == "There's nowhere here worthy of it."
    assert [item.name for item in player.inventory.items] == ["Horn"]

def test_place_trophies_sets_the_trophy_on_its_plinth():
    room = trophy_room()
    player = hunter("Horn")
    message = place_trophies("horn", room, player)
    assert message == "You set the Horn on its plinth.\n(Trophies placed: 1 of 3.)"
    assert room.placed_trophies == {"Horn"}
    assert player.inventory.items == []

def test_place_trophies_matches_the_name_whatever_its_case():
    room = trophy_room()
    place_trophies("HORN", room, hunter("Horn"))
    assert room.placed_trophies == {"Horn"}

def test_place_trophies_an_item_the_player_does_not_have():
    room = trophy_room()
    assert place_trophies("horn", room, hunter()) == "No item named 'horn' in inventory."
    assert room.placed_trophies == set()

def test_place_trophies_refuses_something_that_is_not_a_trophy():
    room = trophy_room()
    player = Player(name="Hero", hp=20)
    sword = Weapon(name="Sword", description="", damage=3)
    player.inventory.add(sword)
    assert place_trophies("sword", room, player) == "The Sword doesn't belong here."
    assert sword in player.inventory.items

def test_place_trophies_refuses_a_quest_item_that_is_not_a_trophy():
    room = trophy_room()
    player = Player(name="Hero", hp=20)
    player.inventory.add(QuestItem(name="Horn", description="", article="the"))
    assert place_trophies("horn", room, player) == "The Horn doesn't belong here."
    assert room.placed_trophies == set()

def test_place_trophies_refuses_a_trophy_with_no_plinth_here():
    room = trophy_room()
    player = hunter("Crown")
    assert place_trophies("crown", room, player) == "The Crown doesn't belong here."
    assert [item.name for item in player.inventory.items] == ["Crown"]

# ---- place_trophies: all ----

def test_place_trophies_all_places_every_trophy_carried():
    room = trophy_room()
    player = hunter("Horn", "Heart")
    message = place_trophies("all", room, player)
    assert message == "You set the Horn on its plinth.\nYou set the Heart on its plinth.\n(Trophies placed: 2 of 3.)"
    assert room.placed_trophies == {"Horn", "Heart"}
    assert player.inventory.items == []

def test_place_trophies_all_leaves_everything_else_in_the_inventory():
    room = trophy_room()
    player = hunter("Horn", "Crown")
    sword = Weapon(name="Sword", description="", damage=3)
    player.inventory.add(sword)
    place_trophies("all", room, player)
    assert [item.name for item in player.inventory.items] == ["Crown", "Sword"]

def test_place_trophies_all_with_no_trophies_to_place():
    room = trophy_room()
    assert place_trophies("all", room, hunter()) == "You have no trophies to place."

# ---- milestones ----

def _milestones(log):
    return {
        1: lambda player: log.append(1) or "First.",
        3: lambda player: log.append(3) or "All of them.",
    }

def test_reaching_a_milestone_runs_its_reward_and_shows_its_message():
    log = []
    room = trophy_room(_milestones(log))
    message = place_trophies("horn", room, hunter("Horn"))
    assert log == [1]
    assert message == "You set the Horn on its plinth.\nFirst.\n(Trophies placed: 1 of 3.)"

def test_a_milestone_is_only_ever_rewarded_once():
    log = []
    room = trophy_room(_milestones(log))
    player = hunter("Horn", "Nail")
    place_trophies("horn", room, player)
    place_trophies("nail", room, player)
    assert log == [1]

def test_a_reached_milestone_is_recorded_in_the_rooms_flags():
    """Flags are saved with the room, so a reload can't pay a milestone out again."""
    room = trophy_room(_milestones([]))
    place_trophies("horn", room, hunter("Horn"))
    assert room.flags == {"trophy_milestone:1"}

def test_a_milestone_already_in_the_rooms_flags_is_not_rewarded_again():
    log = []
    room = trophy_room(_milestones(log))
    room.flags.add("trophy_milestone:1")
    place_trophies("horn", room, hunter("Horn"))
    assert log == []

def test_placing_everything_at_once_reaches_every_milestone_in_order():
    log = []
    room = trophy_room(_milestones(log))
    message = place_trophies("all", room, hunter("Heart", "Nail", "Horn"))
    assert log == [1, 3]
    assert message.splitlines()[-3:] == ["First.", "All of them.", "(Trophies placed: 3 of 3.)"]

def test_a_milestone_reward_is_given_the_player():
    def reward(player):
        player.gold += 10
        return "Paid."
    room = trophy_room({1: reward})
    player = hunter("Horn")
    place_trophies("horn", room, player)
    assert player.gold == 10
