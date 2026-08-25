from dungeon_crawler.characters import Character, Player, Enemy, Ally
from dungeon_crawler.items import Weapon, Inventory, QuestItem

def test_character_initialises_with_correct_stats():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.hp == 30
    assert character.attack_damage == 5

def test_character_initialises_with_default_armour_of_zero():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.armour == 0

def test_take_damage_reduces_hp():
    character = Character(name="Hero", hp=100, attack_damage=10)
    character.take_damage(30)
    assert character.hp == 70

def test_take_damage_cannot_go_below_zero():
    character = Character(name="Hero", hp=10, attack_damage=5)
    character.take_damage(50)
    assert character.hp == 0

def test_take_damage_applies_armour_reduction():
    character = Character(name="Hero", hp=30, attack_damage=5, armour=3)
    character.take_damage(5)
    assert character.hp == 28

def test_take_damage_with_armour_exceeding_damage_deals_no_damage():
    character = Character(name="Hero", hp=30, attack_damage=5, armour=10)
    character.take_damage(4)
    assert character.hp == 30

def test_take_damage_kills_character():
    character = Character(name="Hero", hp=10, attack_damage=5)
    character.take_damage(10)
    assert character.is_alive() is False

def test_is_alive_true_when_hp_above_zero():
    character = Character(name="Hero", hp=10, attack_damage=5)
    assert character.is_alive() == True

def test_is_alive_false_when_hp_zero():
    character = Character(name="Hero", hp=0, attack_damage=5)
    assert character.is_alive() == False

def test_character_on_death_returns_default_message():
    character = Character(name="Hero", hp=0, attack_damage=5)
    message = character.on_death()
    assert "Hero has died" in message

def test_take_damage_lethal_damage_returns_death_message():
    character = Character(name="Hero", hp=10, attack_damage=5)
    damage_dealt, message = character.take_damage(10)
    assert "Hero has died" in message

def test_take_damage_non_lethal_damage_returns_empty_string():
    character = Character(name="Hero", hp=10, attack_damage=5)
    damage_dealt, message = character.take_damage(5)
    assert message == ""

def test_take_damage_returns_damage_dealt():
    character = Character(name="Hero", hp=30, attack_damage=5, armour=3)
    damage_dealt, message = character.take_damage(10)
    assert damage_dealt == 7

def test_attack_reduces_target_hp():
    attacker = Character(name="Hero", hp=30, attack_damage=10)
    target = Character(name="Goblin", hp=20, attack_damage=5)
    attacker.attack(target)
    assert target.hp == 10

def test_attack_returns_message_naming_attacker_and_target():
    attacker = Character(name="Hero", hp=30, attack_damage=10)
    target = Character(name="Goblin", hp=20, attack_damage=5)
    message = attacker.attack(target)
    assert message == "Hero attacks Goblin for 10 damage."

def test_attack_appends_death_message_when_target_dies():
    attacker = Character(name="Hero", hp=30, attack_damage=100)
    target = Character(name="Goblin", hp=20, attack_damage=5)
    message = attacker.attack(target)
    assert message == "Hero attacks Goblin for 100 damage.\nGoblin has died."

def test_attack_message_shows_armour_reduced_damage():
    attacker = Character(name="Hero", hp=30, attack_damage=10)
    target = Character(name="Goblin", hp=20, attack_damage=5, armour=4)
    message = attacker.attack(target)
    assert message == "Hero attacks Goblin for 6 damage."

def test_player_initialises_with_inventory():
    player = Player(name="Hero", hp=10)
    assert isinstance(player.inventory, Inventory)
    assert len(player.inventory) == 0

def test_player_initialises_with_correct_stats():
    player = Player(name="Hero", hp=50, attack_damage=7, armour=2)
    assert player.name == "Hero"
    assert player.hp == 50
    assert player.attack_damage == 7
    assert player.armour == 2

def test_player_initialises_at_level_one_with_no_experience():
    player = Player(name="Hero", hp=10)
    assert player.level == 1
    assert player.experience == 0


def test_player_initialises_with_default_attack_damage():
    player = Player(name="Hero", hp=10)
    assert player.attack_damage == 5

def test_player_on_death_returns_game_over_message():
    player = Player(name="Hero", hp=10)
    message = player.on_death()
    assert message == "Hero has fallen. Game Over."

def test_enemy_initialises_with_correct_stats():
    enemy = Enemy(name="Goblin", hp=15, attack_damage=4, armour=1)
    assert enemy.name == "Goblin"
    assert enemy.hp == 15
    assert enemy.attack_damage == 4
    assert enemy.armour == 1

def test_enemy_initialises_with_empty_loot_by_default():
    enemy = Enemy(name="Goblin", hp=15, attack_damage=4)
    assert enemy.loot == []

def test_enemy_initialises_with_description():
    enemy = Enemy(name="Goblin", hp=15, attack_damage=4, description="A grumbling goblin, unhappy to be disturbed.")
    assert enemy.description == "A grumbling goblin, unhappy to be disturbed."

def test_enemy_on_death_returns_defeated_message():
    enemy = Enemy(name="Hades", hp=60, attack_damage=20)
    message = enemy.on_death()
    assert "Hades has been defeated." in message

def test_enemy_on_death_drops_loot():
    sword = Weapon(name="Iron Sword", description="", damage=5)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5, loot=[sword])
    damage_dealt, message = enemy.take_damage(10)
    assert "Iron Sword" in message

def test_enemy_on_death_with_no_loot_does_not_include_drop_message():
    enemy = Enemy("Hades", hp=60, attack_damage=20)
    message = enemy.on_death()
    assert "dropped" not in message.lower()

def test_player_get_stats(capsys):
    player = Player(name="hero", hp=100)
    print(player.get_stats())
    captured = capsys.readouterr()
    assert "hero:" in captured.out

def test_player_get_stats_has_no_leading_whitespace():
    player = Player(name="hero", hp=100)
    stats = player.get_stats()
    assert stats.startswith("hero:")

def test_ally_initialises_with_empty_inventory():
    ally = Ally(name="Chiron")
    assert isinstance(ally.inventory, Inventory)
    assert len(ally.inventory) == 0

def test_ally_initialises_with_description():
    ally = Ally(name="Chiron", description="Half man, half horse, entirely patient.")
    assert ally.description == "Half man, half horse, entirely patient."

def test_ally_talk_returns_hint_when_set():
    player = Player(name="hero", hp=10)
    ally = Ally(name="Chiron", hint="Beware the minotaur.")
    assert ally.talk(player) == "Beware the minotaur."

def test_ally_talk_returns_default_message_when_no_hint():
    player = Player(name="hero", hp=10)
    ally = Ally(name="Chiron")
    assert ally.talk(player) == "Chiron has nothing to say."

def test_ally_initialises_with_items_adds_them_to_inventory():
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    ally = Ally(name="Chiron", items=[sword])
    assert sword in ally.inventory.items

def test_ally_initialises_with_default_required_items_as_empty_list():
    ally = Ally(name="Chiron")
    assert ally.required_items == []

def test_ally_talk_returns_hint_when_player_missing_required_items():
    player = Player(name="hero", hp=10)
    ally = Ally(name="Chiron", hint="Learn to move first.", hint_complete="Well done.", required_items=["Wooden Sword"])
    assert ally.talk(player) == "Learn to move first."

def test_ally_talk_returns_hint_complete_when_player_has_required_items():
    player = Player(name="hero", hp=10)
    sword = Weapon(name="Wooden Sword", description="", damage=1)
    player.inventory.add(sword)
    ally = Ally(name="Chiron", hint="Learn to move first.", hint_complete="Well done.", required_items=["Wooden Sword"])
    assert ally.talk(player) == "Well done."

def test_ally_talk_falls_back_to_hint_when_required_items_met_but_no_hint_complete_set():
    player = Player(name="hero", hp=10)
    sword = Weapon(name="Wooden Sword", description="", damage=1)
    player.inventory.add(sword)
    ally = Ally(name="Chiron", hint="Learn to move first.", required_items=["Wooden Sword"])
    assert ally.talk(player) == "Learn to move first."

def test_ally_give_item_adds_item_to_player_inventory():
    ally = Ally(name="Chiron")
    player = Player(name="Hero", hp=50)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    ally.inventory.add(sword)
    ally.give_item("Bronze Xiphos", player)
    assert sword in player.inventory.items

def test_ally_give_item_removes_item_from_ally_inventory():
    ally = Ally(name="Chiron")
    player = Player(name="Hero", hp=50)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    ally.inventory.add(sword)
    ally.give_item("Bronze Xiphos", player)
    assert sword not in ally.inventory.items

def test_ally_give_item_returns_confirmation_message():
    ally = Ally(name="Chiron")
    player = Player(name="Hero", hp=50)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    ally.inventory.add(sword)
    message = ally.give_item("Bronze Xiphos", player)
    assert message == "Chiron gives you the Bronze Xiphos."

def test_ally_give_item_returns_message_when_item_not_found():
    ally = Ally(name="Chiron")
    player = Player(name="Hero", hp=50)
    message = ally.give_item("Bronze Xiphos", player)
    assert message == "Chiron does not have that item."

def test_ally_give_item_matches_item_name_case_insensitively():
    ally = Ally(name="Chiron")
    player = Player(name="Hero", hp=50)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    ally.inventory.add(sword)
    ally.give_item("bronze xiphos", player)
    assert sword in player.inventory.items

def test_character_initialises_with_max_hp_equal_to_hp():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.max_hp == 30

def test_enemy_on_death_drops_multiple_loot_items_lists_all_names():
    sword = Weapon(name="Iron Sword", description="", damage=5)
    shield = Weapon(name="Bronze Shield", description="", damage=0)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5, loot=[sword, shield])
    message = enemy.on_death()
    assert "Iron Sword, Bronze Shield" in message

def test_ally_initialises_with_empty_description_by_default():
    ally = Ally(name="Chiron")
    assert ally.description == ""

def test_character_initialises_with_no_equipped_weapon():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.equipped_weapon is None

def test_character_initialises_with_no_equipped_armour():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.equipped_armour is None

def test_get_inventory_display_returns_empty_message_when_no_items():
    player = Player(name="hero", hp=100)
    assert player.get_inventory_display() == "Your inventory is empty."

def test_get_inventory_display_lists_single_item():
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    player.inventory.add(sword)
    assert player.get_inventory_display() == "Bronze Xiphos"

def test_get_inventory_display_shows_count_for_duplicate_items():
    player = Player(name="hero", hp=100)
    player.inventory.add(Weapon(name="Bronze Xiphos", description="", damage=3))
    player.inventory.add(Weapon(name="Bronze Xiphos", description="", damage=3))
    assert player.get_inventory_display() == "Bronze Xiphos x2"

def test_get_inventory_display_lists_multiple_items_on_separate_lines():
    player = Player(name="hero", hp=100)
    player.inventory.add(Weapon(name="Bronze Xiphos", description="", damage=3))
    player.inventory.add(Weapon(name="Shield", description="", damage=1))
    assert player.get_inventory_display() == "Bronze Xiphos\nShield"

def test_get_inventory_display_marks_equipped_item():
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    player.inventory.add(sword)
    sword.use(player)
    assert player.get_inventory_display() == "Bronze Xiphos (equipped)"

def test_get_inventory_display_marks_duplicate_group_equipped_if_any_instance_equipped():
    player = Player(name="hero", hp=100)
    equipped_sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    spare_sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    player.inventory.add(equipped_sword)
    player.inventory.add(spare_sword)
    equipped_sword.use(player)
    assert player.get_inventory_display() == "Bronze Xiphos x2 (equipped)"

def test_get_inventory_display_lists_quest_item_in_separate_section():
    player = Player(name="hero", hp=100)
    player.inventory.add(Weapon(name="Bronze Xiphos", description="", damage=3))
    player.inventory.add(QuestItem(name="Dummy Head", description=""))
    assert player.get_inventory_display() == "Bronze Xiphos\n\nQuest Items: Dummy Head"

def test_get_inventory_display_with_only_quest_items():
    player = Player(name="hero", hp=100)
    player.inventory.add(QuestItem(name="Dummy Head", description=""))
    assert player.get_inventory_display() == "\nQuest Items: Dummy Head"

def test_get_inventory_display_lists_multiple_quest_items_together():
    player = Player(name="hero", hp=100)
    player.inventory.add(QuestItem(name="Dummy Head", description=""))
    player.inventory.add(QuestItem(name="Mentor's Token", description=""))
    assert player.get_inventory_display() == "\nQuest Items: Dummy Head, Mentor's Token"