from dungeon_crawler.world import Room, Map
from dungeon_crawler.characters import Enemy
from dungeon_crawler.content import create_hades, create_minotaur
from dungeon_crawler.items import Weapon

def test_room_connects_to_another_room():
    a = Room("A")
    b = Room("B")
    a.connect("north", b)
    assert a.get_exit("north") is b

def test_room_with_no_exit_returns_none():
    a = Room("A")
    assert a.get_exit("east") is None

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
