from dungeon_crawler.items import Item, Weapon, Armour, Consumable, Inventory
from dungeon_crawler.characters import Character, Player
from dungeon_crawler.world import Room
from dungeon_crawler.engine import pick_up

def test_weapon_use_increases_attack_power():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    sword = Weapon(name="Iron Sword", description="", damage=5)
    sword.use(hero)
    assert hero.attack_damage == 15

def test_pick_up_adds_item_to_inventory():
    room = Room("Armoury")
    sword = Weapon(name="Bronze Xiphos", damage=3, description="...")
    room.add_item(sword)
    player = Player(name="hero", hp=100)

    result = pick_up(room, "Bronze Xiphos", player)

    assert sword in player.inventory._items
    assert sword not in room.items
    assert "Bronze Xiphos" in result


