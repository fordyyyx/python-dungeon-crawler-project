from dungeon_crawler.characters import Character, Player, Enemy, Ally
from dungeon_crawler.items import Weapon, Inventory

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

def test_character_on_death_prints_default_message(capsys):
    character = Character(name="Hero", hp=0, attack_damage=5)
    character.on_death()
    captured = capsys.readouterr()
    assert "Hero has died" in captured.out

def test_attack_reduces_target_hp():
    attacker = Character(name="Hero", hp=30, attack_damage=10)
    target = Character(name="Goblin", hp=20, attack_damage=5)
    attacker.attack(target)
    assert target.hp == 10

def test_attack_returns_message_naming_attacker_and_target():
    attacker = Character(name="Hero", hp=30, attack_damage=10)
    target = Character(name="Goblin", hp=20, attack_damage=5)
    message = attacker.attack(target)
    assert message == "Hero attacks Goblin"

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


def test_player_on_death_prints_game_over(capsys):
    player = Player(name="Hero", hp=10)
    player.on_death()
    captured = capsys.readouterr()
    assert "Hero has fallen. Game Over." in captured.out

def test_enemy_initialises_with_correct_stats():
    enemy = Enemy(name="Goblin", hp=15, attack_damage=4, armour=1)
    assert enemy.name == "Goblin"
    assert enemy.hp == 15
    assert enemy.attack_damage == 4
    assert enemy.armour == 1

def test_enemy_initialises_with_empty_loot_by_default():
    enemy = Enemy(name="Goblin", hp=15, attack_damage=4)
    assert enemy.loot == []

def test_enemy_on_death_prints_defeated_message(capsys):
    enemy = Enemy(name="Hades", hp=60, attack_damage=20)
    enemy.on_death()
    captured = capsys.readouterr()
    assert "Hades has been defeated." in captured.out

def test_enemy_on_death_drops_loot(capsys):
    sword = Weapon(name="Iron Sword", description="", damage=5)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5, loot=[sword])
    enemy.take_damage(10)
    captured = capsys.readouterr()
    assert "Iron Sword" in captured.out

def test_enemy_on_death_with_no_loot_does_not_print_drop_message(capsys):
    enemy = Enemy("Hades", hp=60, attack_damage=20)
    enemy.on_death()
    captured = capsys.readouterr()
    assert "dropped: " not in captured.out

def test_player_get_stats(capsys):
    player = Player(name="hero", hp=100)
    print(player.get_stats())
    captured = capsys.readouterr()
    assert "hero:" in captured.out

def test_ally_initialises_with_empty_inventory():
    ally = Ally(name="Chiron")
    assert isinstance(ally.inventory, Inventory)
    assert len(ally.inventory) == 0

def test_ally_talk_returns_hint_when_set():
    ally = Ally(name="Chiron", hint="Beware the minotaur.")
    assert ally.talk() == "Beware the minotaur."

def test_ally_talk_returns_default_message_when_no_hint():
    ally = Ally(name="Chiron")
    assert ally.talk() == "Chiron has nothing to say."

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