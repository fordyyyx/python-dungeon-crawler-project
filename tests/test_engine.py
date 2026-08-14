from dungeon_crawler.characters import Player
from dungeon_crawler.world import Room
from dungeon_crawler.items import Armour
from dungeon_crawler.engine import pick_up

def test_pick_up_adds_item_to_inventory():
    pass

def test_pick_up_removes_item_from_room():
    pass

def test_pick_up_returns_message_with_description():
    pass

def test_pick_up_returns_not_here_message_when_item_missing():
    pass

def test_pick_up_is_case_insensitive():
    room = Room("Library of Athena")
    shield = Armour(name="Shield of Aegis (fragment)", defence=2, description="...")
    room.add_item(shield)
    player = Player(name="hero", hp=100)

    result = pick_up(room, "shield of aegis (fragment)", player)

    assert shield in player.inventory.items