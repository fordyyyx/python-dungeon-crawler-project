from dungeon_crawler.world import Room, Map, RoomInteraction, StoryGate
from dungeon_crawler.characters import Player
from dungeon_crawler.characters import Enemy, Ally, Companion
from dungeon_crawler.content import create_hades, create_minotaur, create_chiron
from dungeon_crawler.items import Weapon

def test_room_connects_to_another_room():
    a = Room("A")
    b = Room("B")
    a.connect("north", b)
    assert a.get_exit("north") is b

def test_room_with_no_exit_returns_none():
    a = Room("A")
    assert a.get_exit("east") is None

def test_room_lock_exit_records_required_item():
    a = Room("A")
    a.lock_exit("north", "Bronze Key")
    assert a.locked_exits["north"] == "Bronze Key"

def test_room_initialises_with_no_locked_exits():
    a = Room("A")
    assert a.locked_exits == {}

def test_room_add_item_adds_to_room():
    a = Room("A")
    sword = Weapon(name="sword", description="", damage=3)
    a.add_item(sword)
    assert a.items == [sword]

def test_room_remove_item_removes_from_room():
    a = Room("A")
    sword = Weapon(name="sword", description="", damage=3)
    a.add_item(sword)
    a.remove_item(sword)
    assert a.items == []

def test_room_items_property_returns_copy():
    room = Room("Armoury")
    room.add_item("sword")
    room.items.append("shield")
    assert room.items == ["sword"]

def test_room_add_enemy_adds_to_room():
    room = Room("Armoury")
    hades = create_hades()
    room.add_enemy(hades)
    assert hades in room.enemies

def test_room_remove_enemy_removes_from_room():
    room = Room("Armoury")
    hades = create_hades()
    room.add_enemy(hades)
    room.remove_enemy(hades)
    assert room.enemies == []

def test_room_enemies_property_returns_copy():
    room = Room("Armoury")
    hades = create_hades()
    minotaur = create_minotaur()
    room.add_enemy(hades)
    room.enemies.append(minotaur)
    assert room.enemies == [hades]

def test_room_add_ally_adds_to_room():
    room = Room("Chamber of Chiron")
    chiron = create_chiron()
    room.add_ally(chiron)
    assert chiron in room.allies

def test_room_remove_ally_removes_from_room():
    room = Room("Chamber of Chiron")
    chiron = create_chiron()
    room.add_ally(chiron)
    room.remove_ally(chiron)
    assert room.allies == []

def test_room_allies_property_returns_copy():
    room = Room("Chamber of Chiron")
    chiron = create_chiron()
    other_ally = Ally(name="Nestor", description="", hint="")
    room.add_ally(chiron)
    room.allies.append(other_ally)
    assert room.allies == [chiron]

def test_room_initialises_with_empty_companions():
    room = Room("Camp")
    assert room.companions == []

def test_room_add_companion_adds_to_room():
    room = Room("Camp")
    companion = Companion(name="Imp", hp=10, home_room=room)
    room.add_companion(companion)
    assert companion in room.companions

def test_room_remove_companion_removes_from_room():
    room = Room("Camp")
    companion = Companion(name="Imp", hp=10, home_room=room)
    room.add_companion(companion)
    room.remove_companion(companion)
    assert room.companions == []

def test_room_companions_property_returns_copy():
    room = Room("Camp")
    companion = Companion(name="Imp", hp=10, home_room=room)
    other_companion = Companion(name="Harpy", hp=10, home_room=room)
    room.add_companion(companion)
    room.companions.append(other_companion)
    assert room.companions == [companion]

def test_room_remove_companion_raises_error_when_companion_not_in_room():
    room = Room("Camp")
    companion = Companion(name="Imp", hp=10, home_room=room)

    try:
        room.remove_companion(companion)
        assert False, "Expected a ValueError but none was raised"
    except ValueError:
        pass

def test_map_stores_and_retrieves_rooms():
    dungeon = Map()
    room = Room("Entrance")
    dungeon.add_room(room)
    assert dungeon.get_room("Entrance") is room
    assert len(dungeon) == 1

def test_map_len_returns_room_count():
    a = Room("A")
    b = Room("B")

    dungeon = Map()
    dungeon.add_room(a)
    dungeon.add_room(b)
    assert len(dungeon) == 2

def test_map_get_room_returns_none_for_missing_room():
    dungeon = Map()
    assert dungeon.get_room("Nowhere") is None

def test_room_repr_includes_name(capsys):
    room = Room("Armoury")
    print(room)
    captured = capsys.readouterr()
    assert "Room('Armoury')" in captured.out

def test_room_initialises_with_no_exits():
    room = Room("A")
    assert room.exits == {}

def test_room_initialises_with_no_items():
    room = Room("A")
    assert room.items == []

def test_room_initialises_with_no_enemies():
    room = Room("A")
    assert room.enemies == []

def test_room_initialises_with_no_allies():
    room = Room("A")
    assert room.allies == []

def test_map_add_room_overwrites_room_with_same_name():
    dungeon = Map()
    original = Room("Entrance")
    replacement = Room("Entrance")
    dungeon.add_room(original)
    dungeon.add_room(replacement)
    assert dungeon.get_room("Entrance") is replacement
    assert len(dungeon) == 1

def test_room_initialises_with_description():
    room = Room("A", description="A dusty stone chamber.")
    assert room.description == "A dusty stone chamber."

def test_room_initialises_with_empty_description_by_default():
    room = Room("A")
    assert room.description == ""

def test_room_remove_item_raises_error_when_item_not_in_room():
    room = Room("A")
    sword = Weapon(name="sword", description="", damage=3)

    try:
        room.remove_item(sword)
        assert False, "Expected a ValueError but none was raised"
    except ValueError:
        pass

def test_room_remove_enemy_raises_error_when_enemy_not_in_room():
    room = Room("A")
    hades = create_hades()

    try:
        room.remove_enemy(hades)
        assert False, "Expected a ValueError but none was raised"
    except ValueError:
        pass

def test_room_remove_ally_raises_error_when_ally_not_in_room():
    room = Room("A")
    chiron = create_chiron()

    try:
        room.remove_ally(chiron)
        assert False, "Expected a ValueError but none was raised"
    except ValueError:
        pass

def test_room_initialises_with_examine_text():
    room = Room("A", examine_text="A faint draft comes from somewhere below.")
    assert room.examine_text == "A faint draft comes from somewhere below."

def test_room_initialises_with_empty_examine_text_by_default():
    room = Room("A")
    assert room.examine_text == ""

def test_room_initialises_with_required_intellect():
    room = Room("A", required_intellect=3)
    assert room.required_intellect == 3

def test_room_initialises_with_zero_required_intellect_by_default():
    room = Room("A")
    assert room.required_intellect == 0

def test_room_initialises_with_is_forge_false_by_default():
    room = Room("A")
    assert room.is_forge is False

def test_room_initialises_with_is_forge_true():
    room = Room("A", is_forge=True)
    assert room.is_forge is True

def test_room_initialises_with_is_practice_chamber_false_by_default():
    room = Room("A")
    assert room.is_practice_chamber is False

def test_room_initialises_with_is_practice_chamber_true():
    room = Room("A", is_practice_chamber=True)
    assert room.is_practice_chamber is True

def test_room_initialises_with_no_hidden_exits():
    room = Room("A")
    assert room.hidden_exits == {}

def test_room_add_hidden_exit_records_room_without_affecting_exits():
    a = Room("A")
    b = Room("B")
    a.add_hidden_exit("down", b)
    assert a.hidden_exits["down"] is b
    assert a.exits == {}

def test_room_add_hidden_exit_does_not_appear_via_get_exit():
    a = Room("A")
    b = Room("B")
    a.add_hidden_exit("down", b)
    assert a.get_exit("down") is None

def test_room_reveal_hidden_exit_does_not_affect_existing_normal_exits():
    a = Room("A")
    b = Room("B")
    c = Room("C")
    a.connect("north", b)
    a.add_hidden_exit("down", c)
    a.reveal_hidden_exit("down")
    assert a.get_exit("north") is b
    assert a.get_exit("down") is c

def test_room_initialises_with_no_fast_travel_locks():
    room = Room("A")
    assert room.fast_travel_locks == set()

def test_room_lock_fast_travel_exit_adds_direction_to_locks():
    room = Room("A")
    room.lock_fast_travel_exit("prayer room")
    assert "prayer room" in room.fast_travel_locks

def test_room_lock_fast_travel_exit_does_not_affect_exits():
    room = Room("A")
    other = Room("B")
    room.connect("prayer room", other)
    room.lock_fast_travel_exit("prayer room")
    assert room.get_exit("prayer room") is other

def test_room_initialises_with_no_exit_activations():
    room = Room("A")
    assert room.exit_activations == {}

def test_room_register_fast_travel_activation_records_pairing():
    a = Room("A")
    b = Room("B")
    a.register_fast_travel_activation("forge", b, "prayer room")
    assert a.exit_activations["forge"] == (b, "prayer room")

def test_room_initialises_with_no_guarded_exits():
    room = Room("A")
    assert room.guarded_exits == set()

def test_room_guard_exit_adds_direction_to_guarded_exits():
    room = Room("A")
    other = Room("B")
    room.connect("south", other)
    room.guard_exit("south")
    assert "south" in room.guarded_exits

def test_room_guard_exit_does_not_remove_the_exit():
    room = Room("A")
    other = Room("B")
    room.connect("south", other)
    room.guard_exit("south")
    assert room.get_exit("south") is other

def test_room_unlock_exit_removes_the_item_lock():
    room = Room("Chamber")
    room.lock_exit("east", "Wooden Sword")
    room.unlock_exit("east")
    assert "east" not in room.locked_exits

def test_room_unlock_exit_keeps_the_exit_itself():
    room = Room("Chamber")
    yard = Room("Yard")
    room.connect("east", yard)
    room.lock_exit("east", "Wooden Sword")
    room.unlock_exit("east")
    assert room.get_exit("east") is yard

def test_room_unlock_exit_on_an_unlocked_direction_does_nothing():
    room = Room("Chamber")
    room.lock_exit("east", "Wooden Sword")
    room.unlock_exit("west")
    assert room.locked_exits == {"east": "Wooden Sword"}

def test_room_add_interaction_registers_the_verb():
    room = Room("Shore")
    room.add_interaction("listen", lambda player, room: "You listen.")
    assert "listen" in room.interactions

def test_room_interaction_handler_receives_the_player_and_room():
    room = Room("Shore")
    player = Player(name="Hero", hp=20)
    seen = []
    room.add_interaction("listen", lambda p, r: seen.append((p, r)) or "ok")
    result = room.interactions["listen"].handler(player, room)
    assert result == "ok"
    assert seen[0][0] is player
    assert seen[0][1] is room

def test_room_add_interaction_without_is_available_is_always_available():
    room = Room("Shore")
    room.add_interaction("listen", lambda player, room: "")
    assert room.interactions["listen"].is_available(Player(name="Hero", hp=20), room) is True

def test_room_add_interaction_default_unavailable_message():
    room = Room("Shore")
    room.add_interaction("listen", lambda player, room: "")
    assert room.interactions["listen"].unavailable_message == "Nothing happens."

def test_room_add_interaction_keeps_a_custom_unavailable_message():
    room = Room("Shore")
    room.add_interaction("listen", lambda player, room: "", lambda player, room: False, "Silence.")
    assert room.interactions["listen"].unavailable_message == "Silence."

def test_room_available_interactions_lists_verbs_in_the_order_added():
    room = Room("Shore")
    room.add_interaction("listen", lambda player, room: "")
    room.add_interaction("resist", lambda player, room: "")
    assert room.available_interactions(Player(name="Hero", hp=20)) == ["listen", "resist"]

def test_room_available_interactions_skips_an_unavailable_verb():
    room = Room("Shore")
    room.add_interaction("listen", lambda player, room: "", lambda player, room: False)
    room.add_interaction("resist", lambda player, room: "")
    assert room.available_interactions(Player(name="Hero", hp=20)) == ["resist"]

def test_room_available_interactions_is_empty_with_no_interactions():
    assert Room("Shore").available_interactions(Player(name="Hero", hp=20)) == []

def test_room_available_interactions_checks_availability_against_this_room():
    room = Room("Shore")
    room.add_interaction("listen", lambda player, room: "", lambda player, room: "quiet" not in room.flags)
    room.flags.add("quiet")
    assert room.available_interactions(Player(name="Hero", hp=20)) == []

def test_room_flags_start_empty():
    assert Room("Shore").flags == set()

def test_room_flags_are_not_shared_between_rooms():
    a = Room("A")
    b = Room("B")
    a.flags.add("done")
    assert b.flags == set()

def test_room_interactions_are_not_shared_between_rooms():
    a = Room("A")
    b = Room("B")
    a.add_interaction("listen", lambda player, room: "")
    assert b.interactions == {}

def test_room_interaction_defaults_to_always_available():
    interaction = RoomInteraction(handler=lambda player, room: "")
    assert interaction.is_available(Player(name="Hero", hp=20), Room("Shore")) is True
    assert interaction.unavailable_message == "Nothing happens."

def test_room_transient_state_starts_empty():
    assert Room("River").transient_state == {}

def test_room_transient_state_is_not_shared_between_rooms():
    a = Room("A")
    b = Room("B")
    a.transient_state["puzzle"] = 1
    assert b.transient_state == {}

def test_room_advice_starts_empty():
    assert Room("River").advice == ""

def test_room_cleared_story_flag_defaults_to_none():
    room = Room("Hall")
    assert room.cleared_story_flag is None
    assert room.cleared_message == ""

def test_room_is_not_concealed_by_default():
    assert Room("Hall").concealed_until is None

def test_room_on_leave_clears_transient_state():
    room = Room("Bedchamber")
    room.transient_state["dialogue"] = ("Persephone", "start")
    room.on_leave()
    assert room.transient_state == {}

def test_room_has_no_story_gates_by_default():
    assert Room("Hall").story_gates == {}

def test_room_gate_exit_stores_a_story_gate_for_that_direction():
    room = Room("Bedchamber")
    room.gate_exit("descend", ("promised", "refused"), blocked_message="Not yet.", map_label="waiting")
    gate = room.story_gates["descend"]
    assert isinstance(gate, StoryGate)
    assert gate.required_flags == ("promised", "refused")
    assert gate.blocked_message == "Not yet."
    assert gate.map_label == "waiting"

def test_room_reveal_hidden_exit_moves_it_into_exits():
    a, b = Room("Styx"), Room("Vault")
    a.add_hidden_exit("down", b)
    a.reveal_hidden_exit("down")
    assert a.get_exit("down") is b
    assert "down" not in a.hidden_exits

def test_room_reveal_hidden_exit_leaves_other_hidden_exits_hidden():
    a, b, c = Room("Styx"), Room("Vault"), Room("Cellar")
    a.add_hidden_exit("down", b)
    a.add_hidden_exit("north", c)
    a.reveal_hidden_exit("down")
    assert a.hidden_exits == {"north": c}
    assert "north" not in a.exits

def test_room_reveal_hidden_exit_with_no_such_exit_does_nothing():
    a, b = Room("Styx"), Room("Hall")
    a.connect("east", b)
    a.reveal_hidden_exit("down")
    assert a.exits == {"east": b}
    assert a.hidden_exits == {}

def test_room_initialises_with_is_workshop_false_by_default():
    assert Room("A").is_workshop is False

def test_room_initialises_with_is_workshop_true():
    assert Room("A", is_workshop=True).is_workshop is True

def test_room_is_not_a_trophy_room_by_default():
    room = Room("A")
    assert room.is_trophy_room is False
    assert (room.placed_trophies, room.trophy_plinths, room.trophy_milestones) == (set(), [], {})

def test_room_initialises_with_is_trophy_room_true():
    assert Room("A", is_trophy_room=True).is_trophy_room is True

def test_rooms_do_not_share_their_trophy_state():
    first, second = Room("A"), Room("B")
    first.placed_trophies.add("Horn")
    first.trophy_plinths.append(("Horn", "A notch."))
    assert (second.placed_trophies, second.trophy_plinths) == (set(), [])
