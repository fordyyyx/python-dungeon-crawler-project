from dungeon_crawler.items import Item, Weapon, Armour, Consumable, Reviver, QuestItem, Inventory, SkillPointReward
from dungeon_crawler.characters import Character, Player, Companion
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
    assert message == "Hero equips Iron Sword (+5 ATK)."

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

def test_weapon_unequip_when_not_equipped_returns_not_equipped_message():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    sword = Weapon(name="Iron Sword", description="", damage=5)
    message = sword.unequip(hero)
    assert message == "Iron Sword is not equipped."

def test_weapon_unequip_when_equipped_decreases_attack_power():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    sword = Weapon(name="Iron Sword", description="", damage=5)
    sword.use(hero)
    sword.unequip(hero)
    assert hero.attack_damage == 10

def test_weapon_unequip_when_equipped_clears_equipped_flag():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    sword = Weapon(name="Iron Sword", description="", damage=5)
    sword.use(hero)
    sword.unequip(hero)
    assert sword.equipped is False

def test_weapon_unequip_when_equipped_returns_unequip_message():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    sword = Weapon(name="Iron Sword", description="", damage=5)
    sword.use(hero)
    message = sword.unequip(hero)
    assert message == "Hero unequips Iron Sword (-5 ATK)"

def test_weapon_use_sets_character_equipped_weapon():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    sword = Weapon(name="Iron Sword", description="", damage=5)
    sword.use(hero)
    assert hero.equipped_weapon is sword

def test_weapon_unequip_clears_character_equipped_weapon():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    sword = Weapon(name="Iron Sword", description="", damage=5)
    sword.use(hero)
    sword.unequip(hero)
    assert hero.equipped_weapon is None

def test_weapon_use_replacing_equipped_weapon_unequips_old_weapon():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    old_sword = Weapon(name="Iron Sword", description="", damage=5)
    new_sword = Weapon(name="Steel Sword", description="", damage=8)
    old_sword.use(hero)
    new_sword.use(hero)
    assert old_sword.equipped is False

def test_weapon_use_replacing_equipped_weapon_updates_character_equipped_weapon():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    old_sword = Weapon(name="Iron Sword", description="", damage=5)
    new_sword = Weapon(name="Steel Sword", description="", damage=8)
    old_sword.use(hero)
    new_sword.use(hero)
    assert hero.equipped_weapon is new_sword

def test_weapon_use_replacing_equipped_weapon_updates_attack_damage():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    old_sword = Weapon(name="Iron Sword", description="", damage=5)
    new_sword = Weapon(name="Steel Sword", description="", damage=8)
    old_sword.use(hero)
    new_sword.use(hero)
    assert hero.attack_damage == 18

def test_weapon_use_replacing_equipped_weapon_returns_combined_message():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    old_sword = Weapon(name="Iron Sword", description="", damage=5)
    new_sword = Weapon(name="Steel Sword", description="", damage=8)
    old_sword.use(hero)
    message = new_sword.use(hero)
    assert message == "Hero unequips Iron Sword (-5 ATK)\nHero equips Steel Sword (+8 ATK)."

def test_armour_use_increases_armour():
    hero = Character(name="hero", hp=100, attack_damage=10)
    armour = Armour(name="helmet", description="", defence=3)
    armour.use(hero)
    assert hero.armour == 3

def test_armour_use_returns_equip_message():
    hero = Character(name="hero", hp=100, attack_damage=10)
    armour = Armour(name="helmet", description="", defence=3)
    message = armour.use(hero)
    assert message == "hero equips helmet, (+3 DEF)."

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

def test_armour_unequip_when_not_equipped_returns_not_equipped_message():
    hero = Character(name="hero", hp=100, attack_damage=10)
    armour = Armour(name="helmet", description="", defence=3)
    message = armour.unequip(hero)
    assert message == "helmet is not equipped."

def test_armour_unequip_when_equipped_decreases_armour():
    hero = Character(name="hero", hp=100, attack_damage=10)
    armour = Armour(name="helmet", description="", defence=3)
    armour.use(hero)
    armour.unequip(hero)
    assert hero.armour == 0

def test_armour_unequip_when_equipped_clears_equipped_flag():
    hero = Character(name="hero", hp=100, attack_damage=10)
    armour = Armour(name="helmet", description="", defence=3)
    armour.use(hero)
    armour.unequip(hero)
    assert armour.equipped is False

def test_armour_unequip_when_equipped_returns_unequip_message():
    hero = Character(name="hero", hp=100, attack_damage=10)
    armour = Armour(name="helmet", description="", defence=3)
    armour.use(hero)
    message = armour.unequip(hero)
    assert message == "hero unequips helmet (-3 DEF)"

def test_armour_use_sets_character_equipped_armour():
    hero = Character(name="hero", hp=100, attack_damage=10)
    armour = Armour(name="helmet", description="", defence=3)
    armour.use(hero)
    assert hero.equipped_armour is armour

def test_armour_unequip_clears_character_equipped_armour():
    hero = Character(name="hero", hp=100, attack_damage=10)
    armour = Armour(name="helmet", description="", defence=3)
    armour.use(hero)
    armour.unequip(hero)
    assert hero.equipped_armour is None

def test_armour_use_replacing_equipped_armour_unequips_old_armour():
    hero = Character(name="hero", hp=100, attack_damage=10)
    old_armour = Armour(name="helmet", description="", defence=3)
    new_armour = Armour(name="Iron Helm", description="", defence=5)
    old_armour.use(hero)
    new_armour.use(hero)
    assert old_armour.equipped is False

def test_armour_use_replacing_equipped_armour_updates_character_equipped_armour():
    hero = Character(name="hero", hp=100, attack_damage=10)
    old_armour = Armour(name="helmet", description="", defence=3)
    new_armour = Armour(name="Iron Helm", description="", defence=5)
    old_armour.use(hero)
    new_armour.use(hero)
    assert hero.equipped_armour is new_armour

def test_armour_use_replacing_equipped_armour_updates_defence():
    hero = Character(name="hero", hp=100, attack_damage=10)
    old_armour = Armour(name="helmet", description="", defence=3)
    new_armour = Armour(name="Iron Helm", description="", defence=5)
    old_armour.use(hero)
    new_armour.use(hero)
    assert hero.armour == 5

def test_armour_use_replacing_equipped_armour_returns_combined_message():
    hero = Character(name="hero", hp=100, attack_damage=10)
    old_armour = Armour(name="helmet", description="", defence=3)
    new_armour = Armour(name="Iron Helm", description="", defence=5)
    old_armour.use(hero)
    message = new_armour.use(hero)
    assert message == "hero unequips helmet (-3 DEF)\nhero equips Iron Helm, (+5 DEF)."

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

def test_reviver_use_with_no_companion_attribute_returns_message():
    """getattr(character, "companion", None) - a plain Character has no .companion attribute at all,
    distinct from a Player whose companion is explicitly None."""
    hero = Character(name="hero", hp=100, attack_damage=10)
    reviver = Reviver(name="Ambrosia", heal_amount=10)
    message = reviver.use(hero)
    assert message == "Ambrosia has nothing to revive."

def test_reviver_use_with_player_and_no_companion_returns_message():
    hero = Player(name="hero", hp=100)
    reviver = Reviver(name="Ambrosia", heal_amount=10)
    message = reviver.use(hero)
    assert message == "Ambrosia has nothing to revive."

def test_reviver_use_with_living_companion_returns_message_without_reviving():
    hero = Player(name="hero", hp=100)
    home = Room("Camp")
    hero.companion = Companion(name="Imp", hp=10, home_room=home)
    reviver = Reviver(name="Ambrosia", heal_amount=10)
    message = reviver.use(hero)
    assert message == "Imp doesn't need reviving."

def test_reviver_use_with_living_companion_does_not_change_hp():
    hero = Player(name="hero", hp=100)
    home = Room("Camp")
    companion = Companion(name="Imp", hp=10, home_room=home)
    hero.companion = companion
    reviver = Reviver(name="Ambrosia", heal_amount=10)
    reviver.use(hero)
    assert companion.hp == 10

def test_reviver_use_with_downed_companion_revives_with_heal_amount():
    hero = Player(name="hero", hp=100)
    home = Room("Camp")
    companion = Companion(name="Imp", hp=10, home_room=home)
    companion.hp = 0
    hero.companion = companion
    reviver = Reviver(name="Ambrosia", heal_amount=6)
    reviver.use(hero)
    assert companion.hp == 6

def test_reviver_use_with_downed_companion_caps_revive_at_max_hp():
    hero = Player(name="hero", hp=100)
    home = Room("Camp")
    companion = Companion(name="Imp", hp=10, home_room=home)
    companion.hp = 0
    hero.companion = companion
    reviver = Reviver(name="Ambrosia", heal_amount=100) # far exceeds the companion's max_hp
    reviver.use(hero)
    assert companion.hp == 10

def test_reviver_use_with_downed_companion_returns_revive_message():
    hero = Player(name="hero", hp=100)
    home = Room("Camp")
    companion = Companion(name="Imp", hp=10, home_room=home)
    companion.hp = 0
    hero.companion = companion
    reviver = Reviver(name="Ambrosia", heal_amount=6)
    message = reviver.use(hero)
    assert message == "Imp is revived with 6 HP, thanks to Ambrosia."

def test_reviver_is_a_consumable():
    reviver = Reviver(name="Ambrosia", heal_amount=6)
    assert isinstance(reviver, Consumable)

def test_reviver_used_via_inventory_is_removed_after_use():
    """Reviver inherits Consumable's auto-remove-after-use behaviour in Inventory.use_item() - confirms
    the integration actually holds, not just the isinstance relationship."""
    hero = Player(name="hero", hp=100)
    home = Room("Camp")
    companion = Companion(name="Imp", hp=10, home_room=home)
    companion.hp = 0
    hero.companion = companion
    reviver = Reviver(name="Ambrosia", heal_amount=6)
    hero.inventory.add(reviver)

    hero.inventory.use_item("Ambrosia", hero)

    assert reviver not in hero.inventory.items

def test_quest_item_use_returns_message():
    key = QuestItem(name="Bronze Key", description="")
    message = key.use(Character(name="hero", hp=100, attack_damage=10))
    assert message == "Bronze Key doesn't do anything on its own - it is meant for someone else."

def test_quest_item_use_does_not_change_character_stats():
    hero = Character(name="hero", hp=100, attack_damage=10)
    key = QuestItem(name="Bronze Key", description="")
    key.use(hero)
    assert hero.attack_damage == 10
    assert hero.armour == 0
    assert hero.hp == 100

def test_quest_item_unequip_returns_cannot_be_unequipped_message():
    hero = Character(name="hero", hp=100, attack_damage=10)
    key = QuestItem(name="Bronze Key", description="")
    message = key.unequip(hero)
    assert message == "Bronze Key cannot be unequipped."

def test_skill_point_reward_defaults_to_one_point():
    reward = SkillPointReward(name="Ancient Blessing", description="")
    assert reward.points == 1

def test_skill_point_reward_use_increases_skill_points():
    player = Player(name="hero", hp=100)
    reward = SkillPointReward(name="Ancient Blessing", description="", points=2)
    reward.use(player)
    assert player.skill_tree.skill_points == 2

def test_skill_point_reward_use_returns_message():
    player = Player(name="hero", hp=100)
    reward = SkillPointReward(name="Ancient Blessing", description="", points=2)
    message = reward.use(player)
    assert message == "hero gains 2 skill point(s) from Ancient Blessing."

def test_inventory_use_item_keeps_skill_point_reward_after_use():
    player = Player(name="hero", hp=100)
    reward = SkillPointReward(name="Ancient Blessing", description="", points=1)
    player.inventory.add(reward)
    player.inventory.use_item("Ancient Blessing", player)
    assert player.inventory.items == [reward]

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

def test_inventory_drop_item_raises_error_when_item_is_quest_item():
    player = Player(name="hero", hp=100)
    key = QuestItem(name="Bronze Key", description="")
    player.inventory.add(key)

    try:
        player.inventory.drop_item("Bronze Key")
        assert False, "Expected a ValueError but none was raised"
    except ValueError:
        pass

def test_inventory_drop_item_does_not_remove_quest_item_when_blocked():
    player = Player(name="hero", hp=100)
    key = QuestItem(name="Bronze Key", description="")
    player.inventory.add(key)

    try:
        player.inventory.drop_item("Bronze Key")
    except ValueError:
        pass
    assert player.inventory.items == [key]

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

def test_inventory_remove_removes_item():
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    player.inventory.add(sword)
    player.inventory.remove(sword)
    assert player.inventory.items == []

def test_inventory_repr_includes_item_names(capsys):
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    player.inventory.add(sword)
    print(player.inventory)
    captured = capsys.readouterr()
    assert "Inventory(['Bronze Xiphos'])" in captured.out

def test_inventory_use_item_matches_item_name_case_insensitively():
    player = Player(name="hero", hp=100)
    potion = Consumable(name="Potion", heal_amount=10)
    player.inventory.add(potion)
    player.inventory.use_item("potion", player)
    assert player.inventory.items == []

def test_inventory_drop_item_matches_item_name_case_insensitively():
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    player.inventory.add(sword)
    dropped = player.inventory.drop_item("bronze xiphos")
    assert dropped is sword

def test_inventory_unequip_item_returns_items_unequip_message():
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    player.inventory.add(sword)
    player.inventory.use_item("Bronze Xiphos", player)
    message = player.inventory.unequip_item("Bronze Xiphos", player)
    assert message == "hero unequips Bronze Xiphos (-3 ATK)"

def test_inventory_unequip_item_raises_error_when_item_not_found():
    player = Player(name="hero", hp=100)

    try:
        player.inventory.unequip_item("Bronze Xiphos", player)
        assert False, "Expected a ValueError but none was raised"
    except ValueError:
        pass

def test_inventory_unequip_item_matches_item_name_case_insensitively():
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    player.inventory.add(sword)
    player.inventory.use_item("Bronze Xiphos", player)
    message = player.inventory.unequip_item("bronze xiphos", player)
    assert message == "hero unequips Bronze Xiphos (-3 ATK)"

def test_inventory_remove_raises_error_when_item_not_in_inventory():
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)

    try:
        player.inventory.remove(sword)
        assert False, "Expected a ValueError but none was raised"
    except ValueError:
        pass


