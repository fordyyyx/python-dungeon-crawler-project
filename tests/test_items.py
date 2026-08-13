from dungeon_crawler.items import Item, Weapon, Armor, Consumable, Inventory
from dungeon_crawler.characters import Character

def test_weapon_use_increases_attack_power():
    hero = Character(name="Hero", hp=100)
    hero.attack_damage = 10
    sword = Weapon(name="Iron Sword", description="", damage=5)
    sword.use(hero)
    assert hero.attack_damage == 15


