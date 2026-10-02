import random

from dungeon_crawler.characters import Player, Enemy
from dungeon_crawler.world import Room
from dungeon_crawler.items import Consumable, Weapon
from dungeon_crawler.exploration import CHEST_OPENED
from dungeon_crawler.chests import LootTable, chest_rng, roll_loot, add_fixed_chest, add_random_chest

def create_tonic() -> Consumable:
    return Consumable(name="Tonic", description="", heal_amount=5)

def create_dagger() -> Weapon:
    return Weapon(name="Dagger", description="", damage=2)

def seeded_player(seed: int = 7) -> Player:
    player = Player(name="Hero", hp=20)
    player.run_seed = seed
    return player

def open_chest(room, player) -> str:
    return room.interactions["open chest"].handler(player, room)

TABLE = LootTable(gold=(10, 25), items=[(3, create_tonic), (1, create_dagger)])

# ---- LootTable ----

def test_loot_table_defaults_to_no_items_and_two_rolls():
    table = LootTable(gold=(1, 2))
    assert table.items == []
    assert table.rolls == 2

# ---- chest_rng ----

def test_chest_rng_gives_the_same_numbers_for_the_same_run_and_room():
    first = chest_rng(seeded_player(), Room("Vault"))
    second = chest_rng(seeded_player(), Room("Vault"))
    assert [first.random() for _ in range(5)] == [second.random() for _ in range(5)]

def test_chest_rng_differs_between_rooms():
    player = seeded_player()
    assert chest_rng(player, Room("Vault")).random() != chest_rng(player, Room("Cellar")).random()

def test_chest_rng_differs_between_runs():
    room = Room("Vault")
    assert chest_rng(seeded_player(1), room).random() != chest_rng(seeded_player(2), room).random()

def test_chest_rng_leaves_the_games_own_random_numbers_alone():
    """A chest must never change, or be changed by, any other roll - it has its own generator."""
    player = seeded_player()
    state = random.getstate()
    roll_loot(TABLE, player, Room("Vault"))
    assert random.getstate() == state

# ---- roll_loot ----

def test_roll_loot_is_the_same_every_time_for_one_run_and_room():
    player, room = seeded_player(), Room("Vault")
    first_items, first_gold = roll_loot(TABLE, player, room)
    second_items, second_gold = roll_loot(TABLE, player, room)
    assert [item.name for item in first_items] == [item.name for item in second_items]
    assert first_gold == second_gold

def test_roll_loot_gold_stays_within_the_tables_range():
    room = Room("Vault")
    golds = [roll_loot(TABLE, seeded_player(seed), room)[1] for seed in range(200)]
    assert min(golds) >= 10
    assert max(golds) <= 25

def test_roll_loot_gives_one_item_per_roll():
    table = LootTable(gold=(0, 0), items=[(1, create_tonic)], rolls=3)
    items, _ = roll_loot(table, seeded_player(), Room("Vault"))
    assert [item.name for item in items] == ["Tonic", "Tonic", "Tonic"]

def test_roll_loot_builds_a_fresh_item_for_every_roll():
    table = LootTable(gold=(0, 0), items=[(1, create_tonic)], rolls=2)
    items, _ = roll_loot(table, seeded_player(), Room("Vault"))
    assert items[0] is not items[1]

def test_roll_loot_never_picks_an_item_with_no_weight():
    table = LootTable(gold=(0, 0), items=[(1, create_tonic), (0, create_dagger)], rolls=4)
    for seed in range(50):
        items, _ = roll_loot(table, seeded_player(seed), Room("Vault"))
        assert all(item.name == "Tonic" for item in items)

def test_roll_loot_can_give_every_item_in_the_table():
    room = Room("Vault")
    names = {item.name for seed in range(100) for item in roll_loot(TABLE, seeded_player(seed), room)[0]}
    assert names == {"Tonic", "Dagger"}

def test_roll_loot_with_no_items_in_the_table_gives_only_gold():
    items, gold = roll_loot(LootTable(gold=(5, 5)), seeded_player(), Room("Vault"))
    assert items == []
    assert gold == 5

# ---- fixed chests ----

def test_add_fixed_chest_adds_the_open_chest_verb():
    room = Room("Vault")
    add_fixed_chest(room, [create_tonic])
    assert room.available_interactions(seeded_player()) == ["open chest"]

def test_open_chest_puts_the_items_in_the_room_and_gives_the_gold():
    room = Room("Vault")
    add_fixed_chest(room, [create_tonic, create_dagger], gold=15)
    player = seeded_player()
    message = open_chest(room, player)
    assert [item.name for item in room.items] == ["Tonic", "Dagger"]
    assert player.gold == 15
    assert player.inventory.items == []
    assert message == "You force the lid open. Inside: a Tonic, a Dagger, 15 gold. (The items are on the floor - 'take all' to pick them up.)"

def test_open_chest_records_the_chest_as_opened():
    room = Room("Vault")
    add_fixed_chest(room, [create_tonic])
    open_chest(room, seeded_player())
    assert CHEST_OPENED in room.flags

def test_open_chest_can_only_be_opened_once():
    room = Room("Vault")
    add_fixed_chest(room, [create_tonic], gold=15)
    player = seeded_player()
    open_chest(room, player)
    assert room.available_interactions(player) == []
    assert room.interactions["open chest"].unavailable_message == "The chest is empty."

def test_open_chest_with_only_gold_does_not_mention_the_floor():
    room = Room("Vault")
    add_fixed_chest(room, [], gold=15)
    assert open_chest(room, seeded_player()) == "You force the lid open. Inside: 15 gold."

def test_open_chest_with_only_items_does_not_mention_gold():
    room = Room("Vault")
    add_fixed_chest(room, [create_tonic])
    assert open_chest(room, seeded_player()) == "You force the lid open. Inside: a Tonic. (The items are on the floor - 'take all' to pick them up.)"

def test_open_chest_with_nothing_inside_says_so_and_is_still_used_up():
    room = Room("Vault")
    add_fixed_chest(room, [])
    assert open_chest(room, seeded_player()) == "You force the lid open. It's empty."
    assert CHEST_OPENED in room.flags

def test_open_chest_is_refused_while_an_enemy_lives():
    room = Room("Vault")
    add_fixed_chest(room, [create_tonic], gold=15)
    room.add_enemy(Enemy(name="Goblin", hp=10))
    player = seeded_player()
    message = open_chest(room, player)
    assert message == "The Goblin won't let you anywhere near the chest."
    assert (room.items, player.gold, CHEST_OPENED in room.flags) == ([], 0, False)

def test_open_chest_names_a_proper_named_enemy_without_an_article():
    room = Room("Vault")
    add_fixed_chest(room, [create_tonic])
    room.add_enemy(Enemy(name="Talos", hp=10, article=""))
    assert open_chest(room, seeded_player()) == "Talos won't let you anywhere near the chest."

def test_open_chest_works_once_the_enemy_is_dead():
    room = Room("Vault")
    add_fixed_chest(room, [create_tonic])
    goblin = Enemy(name="Goblin", hp=10)
    room.add_enemy(goblin)
    goblin.hp = 0
    open_chest(room, seeded_player())
    assert [item.name for item in room.items] == ["Tonic"]

def test_open_chest_is_not_blocked_by_a_respawning_enemy():
    room = Room("Vault")
    add_fixed_chest(room, [create_tonic])
    dummy = Enemy(name="Dummy", hp=10)
    dummy.respawns = True
    room.add_enemy(dummy)
    open_chest(room, seeded_player())
    assert CHEST_OPENED in room.flags

def test_open_chest_is_blocked_by_an_unsolved_puzzle():
    """An invulnerable enemy still counts as living, so a puzzle room's chest waits for the puzzle."""
    room = Room("River")
    add_fixed_chest(room, [create_tonic])
    room.add_enemy(Enemy(name="Charybdis", hp=1, article="", invulnerable=True))
    assert open_chest(room, seeded_player()) == "Charybdis won't let you anywhere near the chest."

def test_fixed_chest_builds_fresh_items_for_every_room():
    first, second = Room("Vault"), Room("Vault")
    add_fixed_chest(first, [create_tonic])
    add_fixed_chest(second, [create_tonic])
    open_chest(first, seeded_player())
    open_chest(second, seeded_player())
    assert first.items[0] is not second.items[0]

# ---- random chests ----

def test_add_random_chest_adds_the_open_chest_verb():
    room = Room("Vault")
    add_random_chest(room, TABLE)
    assert room.available_interactions(seeded_player()) == ["open chest"]

def test_random_chest_holds_what_the_table_rolls_for_this_run_and_room():
    room = Room("Vault")
    add_random_chest(room, TABLE)
    player = seeded_player()
    expected_items, expected_gold = roll_loot(TABLE, player, room)
    open_chest(room, player)
    assert [item.name for item in room.items] == [item.name for item in expected_items]
    assert player.gold == expected_gold

def test_random_chest_gives_the_same_contents_in_a_rebuilt_world():
    """What a reload does: the world is built again, but the run seed and the room's name are the same - so the chest holds the same things."""
    results = []
    for _ in range(2):
        room = Room("Vault")
        add_random_chest(room, TABLE)
        player = seeded_player(1234)
        open_chest(room, player)
        results.append(([item.name for item in room.items], player.gold))
    assert results[0] == results[1]

def test_random_chest_can_only_be_opened_once():
    room = Room("Vault")
    add_random_chest(room, TABLE)
    player = seeded_player()
    open_chest(room, player)
    assert room.available_interactions(player) == []
