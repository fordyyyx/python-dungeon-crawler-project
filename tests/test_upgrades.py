from dungeon_crawler.characters import Player
from dungeon_crawler.world import Room
from dungeon_crawler.items import Weapon, Armour, Consumable, QuestItem
from dungeon_crawler.exchange import item_value, sale_price
from dungeon_crawler.upgrades import (
    MAX_UPGRADE_LEVEL, UPGRADE_COST_FACTOR, UPGRADE_MIN_COST, upgrade_cap, is_upgradeable, base_value, upgrade_cost, list_upgrades, upgrade_item,
)

def workshop() -> Room:
    return Room("Workshop", is_workshop=True)

def smith(gold: int = 1000, intellect: int = 12) -> Player:
    """A player with plenty of gold and enough intellect for every level, unless told otherwise."""
    player = Player(name="Hero", hp=20)
    player.gold = gold
    player.intellect = intellect
    return player

def axe() -> Weapon:
    """Worth 70, so each level costs 70 times the level."""
    return Weapon(name="Axe", description="", damage=7, weapon_class="heavy")

def knife() -> Weapon:
    """Worth 20 - below the minimum cost."""
    return Weapon(name="Knife", description="", damage=2)

def plate() -> Armour:
    return Armour(name="Plate", description="", defence=5, weight="medium", max_durability=10)

# ---- constants ----

def test_upgrade_constants():
    assert (MAX_UPGRADE_LEVEL, UPGRADE_COST_FACTOR, UPGRADE_MIN_COST) == (5, 1.0, 40)

# ---- upgrade_cap ----

def test_upgrade_cap_is_never_below_one():
    assert upgrade_cap(smith(intellect=0)) == 1

def test_upgrade_cap_rises_by_one_for_every_three_intellect():
    assert [upgrade_cap(smith(intellect=i)) for i in (2, 3, 5, 6, 9)] == [1, 2, 2, 3, 4]

def test_upgrade_cap_never_exceeds_the_maximum_level():
    assert upgrade_cap(smith(intellect=12)) == MAX_UPGRADE_LEVEL
    assert upgrade_cap(smith(intellect=40)) == MAX_UPGRADE_LEVEL

# ---- is_upgradeable ----

def test_is_upgradeable_for_weapons_and_armour():
    assert is_upgradeable(axe()) is True
    assert is_upgradeable(plate()) is True

def test_is_upgradeable_is_false_for_anything_else():
    assert is_upgradeable(Consumable(name="Tonic", description="", heal_amount=5)) is False
    assert is_upgradeable(QuestItem(name="Key", description="")) is False

# ---- base_value / upgrade_cost ----

def test_base_value_ignores_upgrades():
    weapon = axe()
    weapon.upgrade_level = 3
    assert base_value(weapon) == 70
    assert item_value(weapon) == 100

def test_base_value_leaves_the_upgrade_level_as_it_was():
    weapon = axe()
    weapon.upgrade_level = 3
    base_value(weapon)
    assert weapon.upgrade_level == 3

def test_upgrade_cost_of_the_first_level_is_the_items_value():
    assert upgrade_cost(axe()) == 70

def test_upgrade_cost_rises_with_the_level_being_bought():
    weapon = axe()
    costs = []
    for level in range(MAX_UPGRADE_LEVEL):
        weapon.upgrade_level = level
        costs.append(upgrade_cost(weapon))
    assert costs == [70, 140, 210, 280, 350]

def test_upgrade_cost_of_a_cheap_item_uses_the_minimum():
    assert upgrade_cost(knife()) == UPGRADE_MIN_COST

def test_upgrade_cost_of_armour_follows_its_value():
    assert upgrade_cost(plate()) == item_value(plate()) == 60

# ---- list_upgrades ----

def test_list_upgrades_outside_the_workshop():
    player = smith()
    player.inventory.add(axe())
    assert list_upgrades(Room("Hall"), player) == "You'd need proper tools for that."

def test_list_upgrades_with_nothing_to_upgrade():
    player = smith()
    player.inventory.add(Consumable(name="Tonic", description="", heal_amount=5))
    assert list_upgrades(workshop(), player) == "You have nothing that Daedalus' tools could improve."

def test_list_upgrades_shows_the_cap_the_gold_and_each_items_next_level():
    player = smith(gold=300, intellect=6)
    player.inventory.add(axe())
    player.inventory.add(plate())
    assert list_upgrades(workshop(), player) == (
        "You understand his tools well enough to upgrade an item to +3. You have 300 gold.\n"
        "    Axe - +1 for 70 gold\n"
        "    Plate - +1 for 60 gold\n"
        "Say 'upgrade' followed by an item's name to improve it."
    )

def test_list_upgrades_leaves_out_things_that_cannot_be_upgraded():
    player = smith()
    player.inventory.add(axe())
    player.inventory.add(Consumable(name="Tonic", description="", heal_amount=5))
    assert "Tonic" not in list_upgrades(workshop(), player)

def test_list_upgrades_names_an_upgraded_item_with_its_level():
    player = smith()
    weapon = axe()
    weapon.upgrade_level = 2
    player.inventory.add(weapon)
    assert "    Axe +2 - +3 for 210 gold" in list_upgrades(workshop(), player)

def test_list_upgrades_marks_an_item_at_the_players_cap():
    player = smith(intellect=0)
    weapon = axe()
    weapon.upgrade_level = 1
    player.inventory.add(weapon)
    assert "    Axe +1 - beyond what you understand, for now" in list_upgrades(workshop(), player)

def test_list_upgrades_marks_an_item_at_the_maximum_level():
    player = smith()
    weapon = axe()
    weapon.upgrade_level = MAX_UPGRADE_LEVEL
    player.inventory.add(weapon)
    assert "    Axe +5 - as good as it can ever be" in list_upgrades(workshop(), player)

# ---- upgrade_item ----

def test_upgrade_item_outside_the_workshop_changes_nothing():
    player = smith()
    weapon = axe()
    player.inventory.add(weapon)
    assert upgrade_item("axe", Room("Hall"), player) == "You'd need proper tools for that."
    assert (weapon.upgrade_level, player.gold) == (0, 1000)

def test_upgrade_item_the_player_does_not_have():
    assert upgrade_item("axe", workshop(), smith()) == "You have no weapon or armour called 'axe'."

def test_upgrade_item_refuses_something_that_is_not_gear():
    player = smith()
    player.inventory.add(Consumable(name="Tonic", description="", heal_amount=5))
    assert upgrade_item("tonic", workshop(), player) == "You have no weapon or armour called 'tonic'."
    assert player.gold == 1000

def test_upgrade_item_raises_a_weapons_damage_and_takes_the_gold():
    player = smith()
    weapon = axe()
    player.inventory.add(weapon)
    message = upgrade_item("axe", workshop(), player)
    assert (weapon.upgrade_level, weapon.damage, player.gold) == (1, 8, 930)
    assert message == "You work at the bench until the light starts to fail. Axe +1 - heavy, two-handed, 8 DMG. (Paid 70 gold.)"

def test_upgrade_item_raises_armours_defence():
    player = smith()
    armour = plate()
    player.inventory.add(armour)
    upgrade_item("plate", workshop(), player)
    assert (armour.upgrade_level, armour.defence, player.gold) == (1, 6, 940)

def test_upgrade_item_on_worn_armour_raises_the_wearers_armour_at_once():
    player = smith()
    armour = plate()
    player.inventory.add(armour)
    armour.use(player)
    before = player.armour
    upgrade_item("plate", workshop(), player)
    assert player.armour == before + 1

def test_upgrade_item_matches_the_name_whatever_its_case():
    player = smith()
    weapon = axe()
    player.inventory.add(weapon)
    upgrade_item("AXE", workshop(), player)
    assert weapon.upgrade_level == 1

def test_upgrade_item_without_enough_gold_changes_nothing():
    player = smith(gold=69)
    weapon = axe()
    player.inventory.add(weapon)
    assert upgrade_item("axe", workshop(), player) == "Upgrading it to +1 costs 70 gold - you have 69."
    assert (weapon.upgrade_level, player.gold) == (0, 69)

def test_upgrade_item_at_the_players_cap_is_refused():
    player = smith(intellect=0)
    weapon = axe()
    weapon.upgrade_level = 1
    player.inventory.add(weapon)
    assert upgrade_item("axe", workshop(), player) == "You don't understand Daedalus' tools well enough to improve the Axe +1 any further."
    assert (weapon.upgrade_level, player.gold) == (1, 1000)

def test_upgrade_item_at_the_maximum_level_is_refused():
    player = smith()
    weapon = axe()
    weapon.upgrade_level = MAX_UPGRADE_LEVEL
    player.inventory.add(weapon)
    assert upgrade_item("axe", workshop(), player) == "Axe +5 is as good as it can ever be."
    assert player.gold == 1000

def test_upgrade_item_can_be_taken_all_the_way_to_the_maximum():
    player = smith(gold=1050)
    weapon = axe()
    player.inventory.add(weapon)
    for _ in range(MAX_UPGRADE_LEVEL):
        upgrade_item("axe", workshop(), player)
    assert (weapon.upgrade_level, weapon.damage, player.gold) == (5, 12, 0)

def test_upgrade_item_prefers_the_equipped_copy():
    player = smith()
    spare, worn = axe(), axe()
    player.inventory.add(spare)
    player.inventory.add(worn)
    worn.use(player)
    upgrade_item("axe", workshop(), player)
    assert (spare.upgrade_level, worn.upgrade_level) == (0, 1)

def test_upgrade_item_takes_the_first_copy_when_none_is_equipped():
    player = smith()
    first, second = axe(), axe()
    player.inventory.add(first)
    player.inventory.add(second)
    upgrade_item("axe", workshop(), player)
    assert (first.upgrade_level, second.upgrade_level) == (1, 0)

def test_an_item_above_the_players_cap_keeps_its_level():
    """The cap only limits further upgrades - losing intellect, or loading into a lower cap, never takes a level away."""
    player = smith(intellect=0)
    weapon = axe()
    weapon.upgrade_level = 4
    player.inventory.add(weapon)
    upgrade_item("axe", workshop(), player)
    assert (weapon.upgrade_level, weapon.damage) == (4, 11)

# ---- upgrades and selling ----

def test_an_upgraded_item_sells_for_more_but_never_for_what_the_upgrades_cost():
    """No profit loop: every level adds to the sale price, but far less than it cost."""
    weapon = axe()
    plain_price = sale_price(weapon)
    spent = 0
    for level in range(MAX_UPGRADE_LEVEL):
        weapon.upgrade_level = level
        spent += upgrade_cost(weapon)
    weapon.upgrade_level = MAX_UPGRADE_LEVEL
    assert sale_price(weapon) > plain_price
    assert sale_price(weapon) - plain_price < spent

# ---- an upgraded item is still found by its plain name ----

def test_upgrade_item_finds_an_already_upgraded_item_by_its_plain_name():
    """The level is only ever shown beside the name - commands still match the name itself."""
    player = smith()
    weapon = axe()
    weapon.upgrade_level = 1
    player.inventory.add(weapon)
    upgrade_item("axe", workshop(), player)
    assert weapon.upgrade_level == 2

def test_upgrade_item_does_not_match_the_name_with_its_level():
    player = smith()
    weapon = axe()
    weapon.upgrade_level = 1
    player.inventory.add(weapon)
    assert upgrade_item("axe +1", workshop(), player) == "You have no weapon or armour called 'axe +1'."
