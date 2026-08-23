from dungeon_crawler.characters import Player, Enemy, Ally
from dungeon_crawler.world import Room
from dungeon_crawler.items import Armour, QuestItem, Weapon
from dungeon_crawler.engine import pick_up, resolve_combat_round, handle_enemy_defeat, is_exit_locked, trade_with_ally

def test_pick_up_adds_item_to_inventory():
    room = Room("Armoury")
    sword = Weapon("Bronze Xiphos", "", damage=3)
    room.add_item(sword)
    player = Player(name="hero", hp=100)

    pick_up(room, "bronze xiphos", player)

    assert sword in player.inventory.items

def test_pick_up_removes_item_from_room():
    room = Room("Armoury")
    sword = Weapon("Bronze Xiphos", "", damage=3)
    room.add_item(sword)
    player = Player(name="hero", hp=100)
    assert sword in room.items
    
    pick_up(room, "bronze xiphos", player)
    assert sword not in room.items

def test_pick_up_returns_message_with_description(capsys):
    room = Room("Armoury")
    sword = Weapon("Bronze xiphos", "", damage=3)
    room.add_item(sword)
    player = Player(name="hero", hp=100)

    print(pick_up(room, "bronze xiphos", player))
    captured = capsys.readouterr()
    assert "You take the Bronze xiphos." in captured.out


def test_pick_up_returns_not_here_message_when_item_missing(capsys):
    room = Room("Armoury")
    player = Player(name="hero", hp=100)

    print(pick_up(room, "bronze xiphos", player))
    captured = capsys.readouterr()
    assert "That's not here." in captured.out

def test_pick_up_is_case_insensitive():
    room = Room("Library of Athena")
    shield = Armour(name="Shield of Aegis (fragment)", defence=2, description="...")
    room.add_item(shield)
    player = Player(name="hero", hp=100)

    result = pick_up(room, "shield of aegis (fragment)", player)

    assert shield in player.inventory.items

def test_resolve_combat_round_reduces_enemy_hp():
    player = Player(name="Hero", hp=100, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)

    resolve_combat_round(player, enemy)

    assert enemy.hp == 10

def test_resolve_combat_round_reduces_player_hp_when_enemy_survives():
    player = Player(name="Hero", hp=100, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)

    resolve_combat_round(player, enemy)

    assert player.hp == 95

def test_resolve_combat_round_returns_both_attack_messages_when_both_survive():
    player = Player(name="Hero", hp=100, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)

    result = resolve_combat_round(player, enemy)

    assert "Hero attacks Goblin" in result
    assert "Goblin attacks Hero" in result

def test_resolve_combat_round_enemy_defeated_does_not_counter_attack():
    player = Player(name="Hero", hp=100, attack_damage=20)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)

    resolve_combat_round(player, enemy)

    assert player.hp == 100

def test_resolve_combat_round_returns_fallen_message_when_enemy_defeated():
    player = Player(name="Hero", hp=100, attack_damage=20)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)

    result = resolve_combat_round(player, enemy)

    assert "Goblin has been defeated." in result

def test_resolve_combat_round_returns_fallen_message_when_player_defeated():
    player = Player(name="Hero", hp=5, attack_damage=1)
    enemy = Enemy(name="Goblin", hp=100, attack_damage=20)

    result = resolve_combat_round(player, enemy)

    assert "Hero has fallen." in result

def test_handle_enemy_defeat_removes_enemy_from_room():
    room = Room("Armoury")
    enemy = Enemy(name="Goblin", hp=0, attack_damage=5)
    room.add_enemy(enemy)

    handle_enemy_defeat(room, enemy)

    assert enemy not in room.enemies

def test_handle_enemy_defeat_adds_loot_to_room():
    room = Room("Armoury")
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    enemy = Enemy(name="Goblin", hp=0, attack_damage=5, loot=[sword])
    room.add_enemy(enemy)

    handle_enemy_defeat(room, enemy)

    assert sword in room.items

def test_handle_enemy_defeat_with_no_loot_adds_nothing_to_room():
    room = Room("Armoury")
    enemy = Enemy(name="Goblin", hp=0, attack_damage=5)
    room.add_enemy(enemy)

    handle_enemy_defeat(room, enemy)

    assert room.items == []

def test_is_exit_locked_returns_false_when_direction_not_locked():
    room = Room("Armoury")
    player = Player(name="hero", hp=100)

    assert is_exit_locked(room, "north", player) is False

def test_is_exit_locked_returns_true_when_player_missing_required_item():
    room = Room("Armoury")
    room.lock_exit("north", "Bronze Key")
    player = Player(name="hero", hp=100)

    assert is_exit_locked(room, "north", player) is True

def test_is_exit_locked_returns_false_when_player_has_required_item():
    room = Room("Armoury")
    room.lock_exit("north", "Bronze Key")
    key = Weapon(name="Bronze Key", description="", damage=0)
    player = Player(name="hero", hp=100)
    player.inventory.add(key)

    assert is_exit_locked(room, "north", player) is False

def test_trade_with_ally_returns_missing_message_when_player_lacks_required_items():
    ally = Ally(name="Chiron")
    player = Player(name="hero", hp=100)
    coin = QuestItem(name="Charon's Coin", description="")

    message = trade_with_ally(ally, player, ["Wooden Sword", "Wooden Shield"], coin)

    assert message == "Chiron shakes their head. \"You're still missing: Wooden Sword, Wooden Shield.\""

def test_trade_with_ally_does_not_add_reward_when_items_missing():
    ally = Ally(name="Chiron")
    player = Player(name="hero", hp=100)
    coin = QuestItem(name="Charon's Coin", description="")

    trade_with_ally(ally, player, ["Wooden Sword"], coin)

    assert coin not in player.inventory.items

def test_trade_with_ally_removes_required_items_from_player_inventory_when_complete():
    ally = Ally(name="Chiron")
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Wooden Sword", description="", damage=1)
    player.inventory.add(sword)
    coin = QuestItem(name="Charon's Coin", description="")

    trade_with_ally(ally, player, ["Wooden Sword"], coin)

    assert sword not in player.inventory.items

def test_trade_with_ally_adds_reward_to_player_inventory_when_complete():
    ally = Ally(name="Chiron")
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Wooden Sword", description="", damage=1)
    player.inventory.add(sword)
    coin = QuestItem(name="Charon's Coin", description="")

    trade_with_ally(ally, player, ["Wooden Sword"], coin)

    assert coin in player.inventory.items

def test_trade_with_ally_returns_confirmation_message_when_complete():
    ally = Ally(name="Chiron")
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Wooden Sword", description="", damage=1)
    player.inventory.add(sword)
    coin = QuestItem(name="Charon's Coin", description="")

    message = trade_with_ally(ally, player, ["Wooden Sword"], coin)

    assert message == "Chiron nods, accepting each item in turn. \"You've done well.\" They hand you the Charon's Coin."

def test_trade_with_ally_returns_unequip_message_when_required_item_is_equipped():
    ally = Ally(name="Chiron")
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Wooden Sword", description="", damage=1)
    player.inventory.add(sword)
    player.inventory.use_item("Wooden Sword", player)
    coin = QuestItem(name="Charon's Coin", description="")

    message = trade_with_ally(ally, player, ["Wooden Sword"], coin)

    assert message == "Chiron shakes their head. \"You'll need to unequip: Wooden Sword.\""

def test_trade_with_ally_does_not_add_reward_when_required_item_is_equipped():
    ally = Ally(name="Chiron")
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Wooden Sword", description="", damage=1)
    player.inventory.add(sword)
    player.inventory.use_item("Wooden Sword", player)
    coin = QuestItem(name="Charon's Coin", description="")

    trade_with_ally(ally, player, ["Wooden Sword"], coin)

    assert coin not in player.inventory.items

def test_trade_with_ally_does_not_remove_equipped_item_when_blocked():
    ally = Ally(name="Chiron")
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Wooden Sword", description="", damage=1)
    player.inventory.add(sword)
    player.inventory.use_item("Wooden Sword", player)
    coin = QuestItem(name="Charon's Coin", description="")

    trade_with_ally(ally, player, ["Wooden Sword"], coin)

    assert sword in player.inventory.items