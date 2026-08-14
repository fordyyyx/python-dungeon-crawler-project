from dungeon_crawler.world import Room, Map
from dungeon_crawler.characters import Enemy
from dungeon_crawler.content import create_hades

def test_room_connects_to_another_room():
    a = Room("A")
    b = Room("B")
    a.connect("north", b)
    assert a.get_exit("north") is b

def test_room_with_no_exit_returns_none():
    a = Room("A")
    assert a.get_exit("east") is None

def test_map_stores_and_retrieves_rooms():
    dungeon = Map()
    room = Room("Entrance")
    dungeon.add_room(room)
    assert dungeon.get_room("Entrance") is room
    assert len(dungeon) == 1

def test_room_items_property_returns_copy():
    room = Room("Armoury")
    room.add_item("sword")
    room.items.append("shield")
    assert room.items == ["sword"]

def test_enemies_add_to_room():
    room = Room("Armoury")
    hades = create_hades()
    room.add_enemy(hades)
    assert hades in room.enemies
    