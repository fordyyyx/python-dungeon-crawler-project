from dungeon_crawler.dialogue import DialogueNode, DialogueOption, start_dialogue, continue_dialogue
from dungeon_crawler.characters import Player, Ally
from dungeon_crawler.world import Room

def _conversation(dialogue):
    """A room holding one ally with the given dialogue, and a player to talk to them."""
    room = Room("Bedchamber")
    queen = Ally(name="Queen", dialogue=dialogue)
    room.add_ally(queen)
    return room, queen, Player(name="Hero", hp=20)

def _two_node_dialogue():
    return {
        "start": DialogueNode(text="Well?", options=[DialogueOption("Ask about the king", "king"), DialogueOption("Leave", None)]),
        "king": DialogueNode(text="He is busy.", options=[DialogueOption("Go back", "start")]),
    }

# ---- DialogueOption / DialogueNode ----

def test_dialogue_option_has_no_effect_or_availability_check_by_default():
    option = DialogueOption("Leave", None)
    assert option.effect is None
    assert option.available is None

def test_dialogue_node_starts_with_no_options_and_no_on_enter():
    node = DialogueNode(text="Hello.")
    assert node.options == []
    assert node.on_enter is None

def test_dialogue_nodes_do_not_share_an_options_list():
    first = DialogueNode(text="A")
    second = DialogueNode(text="B")
    first.options.append(DialogueOption("Leave", None))
    assert second.options == []

# ---- start_dialogue ----

def test_start_dialogue_shows_the_start_node_with_numbered_options():
    room, queen, player = _conversation(_two_node_dialogue())
    message = start_dialogue(queen, room, player)
    assert message == "Well?\n    1. Ask about the king\n    2. Leave\n(Answer with 'say <number>'.)"

def test_start_dialogue_records_the_position_in_the_room():
    room, queen, player = _conversation(_two_node_dialogue())
    start_dialogue(queen, room, player)
    assert room.transient_state["dialogue"] == ("Queen", "start")

def test_start_dialogue_runs_on_enter_before_the_text():
    dialogue = {"start": DialogueNode(text="Well?", on_enter=lambda p: "She hands you a gift.")}
    room, queen, player = _conversation(dialogue)
    assert start_dialogue(queen, room, player) == "She hands you a gift.\nWell?"

def test_start_dialogue_leaves_out_an_empty_on_enter_message():
    dialogue = {"start": DialogueNode(text="Well?", on_enter=lambda p: "")}
    room, queen, player = _conversation(dialogue)
    assert start_dialogue(queen, room, player) == "Well?"

def test_start_dialogue_passes_the_player_to_on_enter():
    received = []
    dialogue = {"start": DialogueNode(text="Well?", on_enter=lambda p: received.append(p) or "")}
    room, queen, player = _conversation(dialogue)
    start_dialogue(queen, room, player)
    assert received[0] is player

def test_start_dialogue_hides_unavailable_options_and_renumbers():
    dialogue = {"start": DialogueNode(text="Well?", options=[
        DialogueOption("Secret", None, available=lambda p: False),
        DialogueOption("Leave", None),
    ])}
    room, queen, player = _conversation(dialogue)
    assert start_dialogue(queen, room, player) == "Well?\n    1. Leave\n(Answer with 'say <number>'.)"

# ---- continue_dialogue ----

def test_continue_dialogue_outside_a_conversation_says_so():
    room, queen, player = _conversation(_two_node_dialogue())
    assert continue_dialogue("1", room, player) == "You're not in a conversation."

def test_continue_dialogue_after_the_speaker_has_gone_ends_the_conversation():
    room, queen, player = _conversation(_two_node_dialogue())
    start_dialogue(queen, room, player)
    room.remove_ally(queen)
    message = continue_dialogue("1", room, player)
    assert message == "You're not in a conversation."
    assert "dialogue" not in room.transient_state

def test_continue_dialogue_moves_to_the_chosen_node():
    room, queen, player = _conversation(_two_node_dialogue())
    start_dialogue(queen, room, player)
    message = continue_dialogue("1", room, player)
    assert message == "He is busy.\n    1. Go back\n(Answer with 'say <number>'.)"
    assert room.transient_state["dialogue"] == ("Queen", "king")

def test_continue_dialogue_can_return_to_an_earlier_node():
    room, queen, player = _conversation(_two_node_dialogue())
    start_dialogue(queen, room, player)
    continue_dialogue("1", room, player)
    message = continue_dialogue("1", room, player)
    assert message.startswith("Well?")
    assert room.transient_state["dialogue"] == ("Queen", "start")

def test_continue_dialogue_with_a_non_number_asks_for_a_valid_option():
    room, queen, player = _conversation(_two_node_dialogue())
    start_dialogue(queen, room, player)
    assert continue_dialogue("king", room, player) == "Choose an option from 1 to 2."

def test_continue_dialogue_with_no_choice_asks_for_a_valid_option():
    room, queen, player = _conversation(_two_node_dialogue())
    start_dialogue(queen, room, player)
    assert continue_dialogue("", room, player) == "Choose an option from 1 to 2."

def test_continue_dialogue_with_zero_asks_for_a_valid_option():
    room, queen, player = _conversation(_two_node_dialogue())
    start_dialogue(queen, room, player)
    assert continue_dialogue("0", room, player) == "Choose an option from 1 to 2."

def test_continue_dialogue_with_too_high_a_number_keeps_the_position():
    room, queen, player = _conversation(_two_node_dialogue())
    start_dialogue(queen, room, player)
    message = continue_dialogue("3", room, player)
    assert message == "Choose an option from 1 to 2."
    assert room.transient_state["dialogue"] == ("Queen", "start")

def test_continue_dialogue_option_leading_nowhere_ends_the_conversation():
    room, queen, player = _conversation(_two_node_dialogue())
    start_dialogue(queen, room, player)
    message = continue_dialogue("2", room, player)
    assert message == ""
    assert "dialogue" not in room.transient_state

def test_continue_dialogue_runs_the_options_effect_on_the_player():
    dialogue = {"start": DialogueNode(text="Well?", options=[DialogueOption("Promise", None, effect=lambda p: p.story_flags.add("promised") or "")])}
    room, queen, player = _conversation(dialogue)
    start_dialogue(queen, room, player)
    continue_dialogue("1", room, player)
    assert player.story_flags == {"promised"}

def test_continue_dialogue_shows_the_effects_message_before_the_next_node():
    dialogue = {
        "start": DialogueNode(text="Well?", options=[DialogueOption("Bow", "after", effect=lambda p: "You bow.")]),
        "after": DialogueNode(text="Rise.", options=[DialogueOption("Leave", None)]),
    }
    room, queen, player = _conversation(dialogue)
    start_dialogue(queen, room, player)
    assert continue_dialogue("1", room, player) == "You bow.\nRise.\n    1. Leave\n(Answer with 'say <number>'.)"

def test_continue_dialogue_ending_option_returns_its_effects_message():
    dialogue = {"start": DialogueNode(text="Well?", options=[DialogueOption("Go", None, effect=lambda p: "You walk away.")])}
    room, queen, player = _conversation(dialogue)
    start_dialogue(queen, room, player)
    assert continue_dialogue("1", room, player) == "You walk away."

def test_continue_dialogue_numbers_follow_the_offered_options():
    """With the first option hidden, '1' picks the first option actually shown, not the first one defined."""
    dialogue = {
        "start": DialogueNode(text="Well?", options=[
            DialogueOption("Secret", "secret", available=lambda p: False),
            DialogueOption("Ask about the king", "king"),
        ]),
        "secret": DialogueNode(text="Hush."),
        "king": DialogueNode(text="He is busy."),
    }
    room, queen, player = _conversation(dialogue)
    start_dialogue(queen, room, player)
    assert continue_dialogue("1", room, player) == "He is busy."

def test_continue_dialogue_runs_on_enter_again_each_time_a_node_is_reached():
    entries = []
    dialogue = {
        "start": DialogueNode(text="Well?", on_enter=lambda p: entries.append("start") or "", options=[DialogueOption("Again", "start")]),
    }
    room, queen, player = _conversation(dialogue)
    start_dialogue(queen, room, player)
    continue_dialogue("1", room, player)
    assert entries == ["start", "start"]

def test_leaving_the_room_ends_the_conversation():
    room, queen, player = _conversation(_two_node_dialogue())
    start_dialogue(queen, room, player)
    room.on_leave()
    assert continue_dialogue("1", room, player) == "You're not in a conversation."

def test_a_node_with_no_options_shows_no_say_prompt():
    dialogue = {"start": DialogueNode(text="She says nothing more.")}
    room, queen, player = _conversation(dialogue)
    assert start_dialogue(queen, room, player) == "She says nothing more."
