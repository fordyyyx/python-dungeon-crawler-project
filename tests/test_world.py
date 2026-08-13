from dungeon_crawler.world import Room, Map

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