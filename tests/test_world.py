from dungeon_crawler.world import Room, Map
from dungeon_crawler.characters import Enemy, Ally
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
