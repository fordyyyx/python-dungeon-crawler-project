from dungeon_crawler.world import Room, Map
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

def test_room_reveal_hidden_exits_promotes_exit_into_exits():
    a = Room("A")
    b = Room("B")
    a.add_hidden_exit("down", b)
    a.reveal_hidden_exits()
    assert a.get_exit("down") is b

def test_room_reveal_hidden_exits_clears_hidden_exits():
    a = Room("A")
    b = Room("B")
    a.add_hidden_exit("down", b)
    a.reveal_hidden_exits()
    assert a.hidden_exits == {}

def test_room_reveal_hidden_exits_returns_revealed_directions():
    a = Room("A")
    b = Room("B")
    c = Room("C")
    a.add_hidden_exit("down", b)
    a.add_hidden_exit("up", c)
    revealed = a.reveal_hidden_exits()
    assert revealed == ["down", "up"]

def test_room_reveal_hidden_exits_with_none_hidden_returns_empty_list():
    room = Room("A")
    assert room.reveal_hidden_exits() == []

def test_room_reveal_hidden_exits_does_not_affect_existing_normal_exits():
    a = Room("A")
    b = Room("B")
    c = Room("C")
    a.connect("north", b)
    a.add_hidden_exit("down", c)
    a.reveal_hidden_exits()
    assert a.get_exit("north") is b
    assert a.get_exit("down") is c
