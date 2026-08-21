from dungeon_crawler.items import Item, Weapon, Armour, Consumable, Inventory
from dungeon_crawler.characters import Character, Player
from dungeon_crawler.world import Room
from dungeon_crawler.engine import pick_up

def test_item_initialises_as_unequipped():
    sword = Weapon(name="Iron Sword", description="", damage=5)
    assert sword.equipped is False

def test_weapon_use_increases_attack_power():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    sword = Weapon(name="Iron Sword", description="", damage=5)
    sword.use(hero)
    assert hero.attack_damage == 15

def test_weapon_use_returns_equip_message():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    sword = Weapon(name="Iron Sword", description="", damage=5)
    message = sword.use(hero)
    assert message == "Hero equips Iron Sword, (+5 attack)."

def test_weapon_use_sets_equipped_flag():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    sword = Weapon(name="Iron Sword", description="", damage=5)
    sword.use(hero)
    assert sword.equipped is True

def test_weapon_use_when_already_equipped_does_not_increase_attack_again():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    sword = Weapon(name="Iron Sword", description="", damage=5)
    sword.use(hero)
    sword.use(hero)
    assert hero.attack_damage == 15

def test_weapon_use_when_already_equipped_returns_already_equipped_message():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    sword = Weapon(name="Iron Sword", description="", damage=5)
    sword.use(hero)
    message = sword.use(hero)
    assert message == "Iron Sword already equipped."

def test_armour_use_increases_armour():
    hero = Character(name="hero", hp=100, attack_damage=10)
    armour = Armour(name="helmet", description="", defence=3)
    armour.use(hero)
    assert hero.armour == 3

def test_armour_use_returns_equip_message():
    hero = Character(name="hero", hp=100, attack_damage=10)
    armour = Armour(name="helmet", description="", defence=3)
    message = armour.use(hero)
    assert message == "hero equips helmet, (+3 armour)."

def test_armour_use_sets_equipped_flag():
    hero = Character(name="hero", hp=100, attack_damage=10)
    armour = Armour(name="helmet", description="", defence=3)
    armour.use(hero)
    assert armour.equipped is True

def test_armour_use_when_already_equipped_does_not_increase_armour_again():
    hero = Character(name="hero", hp=100, attack_damage=10)
    armour = Armour(name="helmet", description="", defence=3)
    armour.use(hero)
    armour.use(hero)
    assert hero.armour == 3

def test_armour_use_when_already_equipped_returns_already_equipped_message():
    hero = Character(name="hero", hp=100, attack_damage=10)
    armour = Armour(name="helmet", description="", defence=3)
    armour.use(hero)
    message = armour.use(hero)
    assert message == "helmet already equipped"

def test_consumable_use_heals_character():
    hero = Character(name="hero", hp=100, attack_damage=10)
    potion = Consumable(name="potion", heal_amount=3)
    hero.take_damage(10)
    potion.use(hero)
    assert hero.hp == 93

def test_consumable_use_does_not_exceed_max_hp():
    hero = Character(name="hero", hp=100, attack_damage=10)
    potion = Consumable(name="potion", heal_amount=3)
    hero.take_damage(2)
    potion.use(hero)
    assert hero.hp == 100

def test_consumable_use_returns_heal_message():
    hero = Character(name="hero", hp=100, attack_damage=10)
    potion = Consumable(name="potion", heal_amount=3)
    hero.take_damage(10)
    message = potion.use(hero)
    assert message == "hero uses potion, healing 3 HP."

def test_item_repr_includes_class_name_and_name(capsys):
    potion = Consumable(name="potion", heal_amount=3)
    print(potion)
    captured = capsys.readouterr()
    assert "Consumable(name='potion')" in captured.out

def test_inventory_add_adds_item():
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="Sword", damage=5)
    player.inventory.add(sword)
    assert sword in player.inventory.items


def test_inventory_items_property_returns_copy():
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="Sword", damage=5)
    shield = Armour(name="Shield", description="Shield", defence=3)
    player.inventory.add(sword)
    player.inventory.items.append(shield)
    assert player.inventory.items == [sword]

def test_inventory_use_item_removes_consumable_after_use():
    player = Player(name="hero", hp=100)
    potion = Consumable(name="potion", heal_amount=10)
    player.inventory.add(potion)
    assert player.inventory.items == [potion]
    player.inventory.use_item("potion", player)
    assert player.inventory.items == []

def test_inventory_use_item_keeps_weapon_after_use():
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="Sword", damage=5)
    player.inventory.add(sword)
    assert player.inventory.items == [sword]
    player.inventory.use_item("Bronze Xiphos", player)
    assert player.inventory.items == [sword]

def test_use_item_raises_error_when_item_not_found():
    player = Player(name="hero", hp=100)

    try:
        player.inventory.use_item("Bronze Xiphos", player)
        assert False, "Expected a ValueError but none was raised"
    except ValueError:
        pass

def test_inventory_drop_item_removes_item_from_inventory():
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    player.inventory.add(sword)
    player.inventory.drop_item("Bronze Xiphos")
    assert player.inventory.items == []

def test_inventory_drop_item_returns_dropped_item():
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    player.inventory.add(sword)
    dropped = player.inventory.drop_item("Bronze Xiphos")
    assert dropped is sword

def test_inventory_drop_item_raises_error_when_equipped():
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    player.inventory.add(sword)
    player.inventory.use_item("Bronze Xiphos", player)

    try:
        player.inventory.drop_item("Bronze Xiphos")
        assert False, "Expected a ValueError but none was raised"
    except ValueError:
        pass

def test_inventory_drop_item_when_equipped_does_not_remove_it():
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    player.inventory.add(sword)
    player.inventory.use_item("Bronze Xiphos", player)

    try:
        player.inventory.drop_item("Bronze Xiphos")
    except ValueError:
        pass
    assert player.inventory.items == [sword]

def test_inventory_drop_item_raises_error_when_item_not_found():
    player = Player(name="hero", hp=100)

    try:
        player.inventory.drop_item("Bronze Xiphos")
        assert False, "Expected a ValueError but none was raised"
    except ValueError:
        pass

def test_inventory_len_returns_item_count():
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    player.inventory.add(sword)
    assert len(player.inventory) == 1


