from dungeon_crawler.items import Item, Weapon, Armour, Consumable, Inventory
from dungeon_crawler.characters import Character, Player
from dungeon_crawler.world import Room
from dungeon_crawler.engine import pick_up

def test_weapon_use_increases_attack_power():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    sword = Weapon(name="Iron Sword", description="", damage=5)
    sword.use(hero)
    assert hero.attack_damage == 15

def test_armour_use_increases_armour():
    pass

def test_consumable_use_heals_character():
    pass

def test_consumable_use_does_not_exceed_max_hp():
    pass

def test_item_repr_includes_class_name_and_name():
    pass

def test_inventory_add_adds_item():
    pass

def test_inventory_items_property_returns_copy():
    pass

def test_inventory_use_item_removes_consumable_after_use():
    pass

def test_inventory_use_item_keeps_weapon_after_use():
    pass

def test_use_item_raises_error_when_item_not_found():
    pass

def test_inventory_len_returns_item_count():
    pass


