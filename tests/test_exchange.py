from dungeon_crawler.characters import Player, Ally
from dungeon_crawler.world import Room
from dungeon_crawler.items import Item, Consumable, Weapon, Armour, QuestItem, Trophy, LoyaltyToken, EscapeItem, IntellectReward, SkillPointReward, SpellBook, StatusEffectItem
from dungeon_crawler.spells import Spell
from dungeon_crawler.exploration import REPAIR_COST_PER_POINT
from dungeon_crawler.exchange import Offer, get_merchant, list_offers, make_exchange, available_offers, item_value, sale_price, get_buyer, sell_item, shop_offer
from dungeon_crawler.exchange import (VALUE_PER_DAMAGE, VALUE_PER_PIERCE, VALUE_PER_SIGNATURE, VALUE_PER_DEFENCE, ARMOUR_WEIGHT_VALUE, VALUE_PER_HEAL,
                                      FULL_HEAL_VALUE, VALUE_PER_INTELLECT, VALUE_PER_SKILL_POINT, ESCAPE_ITEM_VALUE, SALE_FRACTION, SHOP_MARKUP)

def create_tonic() -> Consumable:
    return Consumable(name="Tonic", description="", heal_amount=5)

def old_sword():
    return Weapon(name="Old Sword", description="", damage=2)

def merchant_room(*offers, exchange_line=""):
    room = Room("Stall")
    merchant = Ally(name="Trader", offers=list(offers), exchange_line=exchange_line)
    room.add_ally(merchant)
    return room, merchant

def test_offer_input_factory_defaults_to_none():
    offer = Offer(gold_cost=5, output_factory=create_tonic)
    assert offer.input_factory is None
    assert offer.input_name is None

def test_offer_input_name_is_the_name_of_what_it_takes():
    assert Offer(gold_cost=5, output_factory=create_tonic, input_factory=old_sword).input_name == "Old Sword"

def test_offer_output_name_is_the_name_of_what_it_makes():
    assert Offer(gold_cost=5, output_factory=create_tonic).output_name == "Tonic"

def test_offer_describe_a_gold_only_offer():
    assert Offer(gold_cost=5, output_factory=create_tonic).describe() == "5 gold -> Tonic"

def test_offer_describe_an_offer_with_an_item_to_hand_over():
    assert Offer(gold_cost=20, output_factory=create_tonic, input_factory=old_sword).describe() == "Old Sword + 20 gold -> Tonic"

def test_get_merchant_returns_the_first_ally_with_offers():
    room = Room("Stall")
    room.add_ally(Ally(name="Idler"))
    trader = Ally(name="Trader", offers=[Offer(gold_cost=5, output_factory=create_tonic)])
    room.add_ally(trader)
    assert get_merchant(room) is trader

def test_get_merchant_with_no_merchant_returns_none():
    room = Room("Stall")
    room.add_ally(Ally(name="Idler"))
    assert get_merchant(room) is None

def test_list_offers_with_no_merchant():
    assert list_offers(Room("Stall"), Player(name="Hero", hp=20)) == "There's no one here to exchange with."

def test_list_offers_numbers_every_offer_and_shows_the_players_gold():
    room, _ = merchant_room(Offer(gold_cost=5, output_factory=create_tonic), Offer(gold_cost=20, output_factory=create_tonic, input_factory=old_sword))
    player = Player(name="Hero", hp=20)
    player.gold = 12
    assert list_offers(room, player) == (
        "Trader's offers (you have 12 gold):\n"
        "    1. 5 gold -> Tonic\n"
        "    2. Old Sword + 20 gold -> Tonic\n"
        "Say 'exchange <number>' to accept one."
    )

def test_make_exchange_with_no_merchant():
    assert make_exchange("1", Room("Stall"), Player(name="Hero", hp=20)) == "There's no one here to exchange with."

def test_make_exchange_refuses_a_number_out_of_range():
    room, _ = merchant_room(Offer(gold_cost=5, output_factory=create_tonic))
    player = Player(name="Hero", hp=20)
    player.gold = 50
    message = make_exchange("2", room, player)
    assert "from 1 to 1" in message
    assert player.gold == 50
    assert player.inventory.items == []

def test_make_exchange_refuses_something_that_is_not_a_number():
    room, _ = merchant_room(Offer(gold_cost=5, output_factory=create_tonic))
    assert "from 1 to 1" in make_exchange("tonic", room, Player(name="Hero", hp=20))

def test_make_exchange_refuses_without_enough_gold():
    room, _ = merchant_room(Offer(gold_cost=5, output_factory=create_tonic))
    player = Player(name="Hero", hp=20)
    player.gold = 3
    assert make_exchange("1", room, player) == "That costs 5 gold - you have 3."
    assert player.gold == 3
    assert player.inventory.items == []

def test_make_exchange_a_gold_only_offer_takes_the_gold_and_gives_the_item():
    room, _ = merchant_room(Offer(gold_cost=5, output_factory=create_tonic))
    player = Player(name="Hero", hp=20)
    player.gold = 12
    message = make_exchange("1", room, player)
    assert player.gold == 7
    assert [item.name for item in player.inventory.items] == ["Tonic"]
    assert message == "Trader takes 5 gold.\nYou receive: a Tonic."

def test_make_exchange_gives_a_fresh_item_every_time():
    room, _ = merchant_room(Offer(gold_cost=1, output_factory=create_tonic))
    player = Player(name="Hero", hp=20)
    player.gold = 5
    make_exchange("1", room, player)
    make_exchange("1", room, player)
    first, second = player.inventory.items
    assert first is not second

def test_make_exchange_shows_the_merchants_exchange_line():
    room, _ = merchant_room(Offer(gold_cost=1, output_factory=create_tonic), exchange_line="She hums.")
    player = Player(name="Hero", hp=20)
    player.gold = 5
    assert make_exchange("1", room, player) == "Trader takes 1 gold.\nShe hums.\nYou receive: a Tonic."

def test_make_exchange_offers_never_run_out():
    room, merchant = merchant_room(Offer(gold_cost=1, output_factory=create_tonic))
    player = Player(name="Hero", hp=20)
    player.gold = 5
    make_exchange("1", room, player)
    assert len(merchant.offers) == 1

def test_make_exchange_hands_over_the_item_and_the_gold():
    room, _ = merchant_room(Offer(gold_cost=20, output_factory=create_tonic, input_factory=old_sword))
    player = Player(name="Hero", hp=20)
    player.gold = 25
    player.inventory.add(old_sword())
    message = make_exchange("1", room, player)
    assert player.gold == 5
    assert [item.name for item in player.inventory.items] == ["Tonic"]
    assert message == "Trader takes the Old Sword and 20 gold.\nYou receive: a Tonic."

def test_make_exchange_refuses_without_the_item():
    """Regression: the lookup read offer.input_name, which doesn't exist - any item offer crashed the game for anyone carrying anything."""
    room, _ = merchant_room(Offer(gold_cost=20, output_factory=create_tonic, input_factory=old_sword))
    player = Player(name="Hero", hp=20)
    player.gold = 25
    player.inventory.add(create_tonic())
    assert make_exchange("1", room, player).startswith("You don't have")
    assert player.gold == 25

def test_make_exchange_refuses_an_item_that_is_only_held_equipped():
    room, _ = merchant_room(Offer(gold_cost=20, output_factory=create_tonic, input_factory=old_sword))
    player = Player(name="Hero", hp=20)
    player.gold = 25
    sword = old_sword()
    player.inventory.add(sword)
    sword.use(player)
    assert make_exchange("1", room, player) == "You'll need to unequip the Old Sword first."
    assert sword in player.inventory.items
    assert player.gold == 25

def test_make_exchange_uses_an_unequipped_copy_when_another_is_equipped():
    room, _ = merchant_room(Offer(gold_cost=0, output_factory=create_tonic, input_factory=old_sword))
    player = Player(name="Hero", hp=20)
    worn, spare = old_sword(), old_sword()
    player.inventory.add(worn)
    player.inventory.add(spare)
    worn.use(player)
    make_exchange("1", room, player)
    assert worn in player.inventory.items
    assert spare not in player.inventory.items

def test_make_exchange_checks_the_item_before_the_gold():
    room, _ = merchant_room(Offer(gold_cost=20, output_factory=create_tonic, input_factory=old_sword))
    player = Player(name="Hero", hp=20)
    assert make_exchange("1", room, player).startswith("You don't have")

def test_make_exchange_with_the_item_but_not_enough_gold_keeps_the_item():
    room, _ = merchant_room(Offer(gold_cost=20, output_factory=create_tonic, input_factory=old_sword))
    player = Player(name="Hero", hp=20)
    player.gold = 5
    sword = old_sword()
    player.inventory.add(sword)
    assert make_exchange("1", room, player) == "That costs 20 gold - you have 5."
    assert sword in player.inventory.items

def test_make_exchange_without_the_item_names_it_with_its_article():
    room, _ = merchant_room(Offer(gold_cost=20, output_factory=create_tonic, input_factory=old_sword))
    assert make_exchange("1", room, Player(name="Hero", hp=20)) == "You don't have an Old Sword."

def test_make_exchange_with_no_number_asks_for_one():
    """main() routes a bare 'exchange' here with an empty choice."""
    room, _ = merchant_room(Offer(gold_cost=5, output_factory=create_tonic))
    assert make_exchange("", room, Player(name="Hero", hp=20)) == "Choose an offer from 1 to 1 - say 'offers' to see them."

def test_make_exchange_names_a_proper_named_item_without_an_article():
    def fang():
        return Weapon(name="Lamia's Fang", description="", damage=4, article="")
    room, _ = merchant_room(Offer(gold_cost=0, output_factory=fang))
    assert make_exchange("1", room, Player(name="Hero", hp=20)).endswith("You receive: Lamia's Fang.")

# ---- offers with no gold cost ----

def test_offer_describe_an_item_only_offer_leaves_the_gold_out():
    assert Offer(gold_cost=0, output_factory=create_tonic, input_factory=old_sword).describe() == "Old Sword -> Tonic"

def test_offer_describe_a_free_gold_only_offer_still_names_a_price():
    assert Offer(gold_cost=0, output_factory=create_tonic).describe() == "0 gold -> Tonic"

def test_make_exchange_an_item_only_offer_mentions_no_gold():
    room, _ = merchant_room(Offer(gold_cost=0, output_factory=create_tonic, input_factory=old_sword))
    player = Player(name="Hero", hp=20)
    player.inventory.add(old_sword())
    message = make_exchange("1", room, player)
    assert message.splitlines()[0] == "Trader takes the Old Sword."
    assert player.gold == 0

# ---- stock that unlocks by floor ----

def _floor_stock():
    return merchant_room(Offer(gold_cost=5, output_factory=create_tonic), Offer(gold_cost=9, output_factory=old_sword, min_floor=3))

def test_offer_min_floor_defaults_to_zero():
    assert Offer(gold_cost=5, output_factory=create_tonic).min_floor == 0

def test_available_offers_hides_stock_from_floors_not_yet_reached():
    room, merchant = _floor_stock()
    player = Player(name="Hero", hp=20)
    player.visited_floors = {"floor_1", "floor_2"}
    assert [offer.output_name for offer in available_offers(merchant, player)] == ["Tonic"]

def test_available_offers_keeps_older_stock_once_deeper_stock_unlocks():
    room, merchant = _floor_stock()
    player = Player(name="Hero", hp=20)
    player.visited_floors = {"floor_3"}
    assert [offer.output_name for offer in available_offers(merchant, player)] == ["Tonic", "Old Sword"]

def test_list_offers_only_lists_what_is_unlocked():
    room, _ = _floor_stock()
    listing = list_offers(room, Player(name="Hero", hp=20))
    assert "1. 5 gold -> Tonic" in listing
    assert "Old Sword" not in listing

def test_list_offers_with_nothing_unlocked_yet():
    room, _ = merchant_room(Offer(gold_cost=9, output_factory=old_sword, min_floor=3))
    assert list_offers(room, Player(name="Hero", hp=20)) == "Trader has nothing to offer you yet."

def test_make_exchange_with_nothing_unlocked_yet():
    room, _ = merchant_room(Offer(gold_cost=9, output_factory=old_sword, min_floor=3))
    player = Player(name="Hero", hp=20)
    player.gold = 50
    assert make_exchange("1", room, player) == "Trader has nothing to offer you yet."
    assert player.gold == 50

def test_make_exchange_numbers_only_count_unlocked_offers():
    room, _ = merchant_room(Offer(gold_cost=9, output_factory=old_sword, min_floor=3), Offer(gold_cost=5, output_factory=create_tonic))
    player = Player(name="Hero", hp=20)
    player.gold = 50
    make_exchange("1", room, player)
    assert [item.name for item in player.inventory.items] == ["Tonic"]
    assert make_exchange("2", room, player) == "Choose an offer from 1 to 1 - say 'offers' to see them."

# ---- item_value ----

class Oddity(Item):
    """An item of no kind item_value() knows."""

    def use(self, character) -> str:
        return ""

def test_item_value_of_a_quest_item_is_none():
    assert item_value(QuestItem(name="Key", description="")) is None

def test_item_value_of_a_trophy_or_keepsake_is_none():
    assert item_value(Trophy(name="Heart", description="")) is None
    assert item_value(LoyaltyToken(name="Thread", description="")) is None

def test_item_value_of_an_unknown_kind_of_item_is_none():
    assert item_value(Oddity(name="Thing")) is None

def test_item_value_of_a_weapon_counts_damage_and_pierce():
    spear = Weapon(name="Spear", description="", damage=6, weapon_class="piercing", armour_pierce=2)
    assert item_value(spear) == 6 * VALUE_PER_DAMAGE + 2 * VALUE_PER_PIERCE

def test_item_value_of_a_weapon_adds_a_premium_per_signature_property():
    plain = Weapon(name="Axe", description="", damage=7, weapon_class="heavy")
    fancy = Weapon(name="Axe", description="", damage=7, weapon_class="heavy", cleave=True, lifesteal=True)
    assert item_value(fancy) == item_value(plain) + 2 * VALUE_PER_SIGNATURE

def test_item_value_of_armour_is_worth_more_per_point_when_light():
    light = Armour(name="Vest", description="", defence=4, weight="light")
    heavy = Armour(name="Plate", description="", defence=4, weight="heavy")
    assert item_value(light) == round(4 * VALUE_PER_DEFENCE * ARMOUR_WEIGHT_VALUE["light"])
    assert item_value(heavy) == round(4 * VALUE_PER_DEFENCE * ARMOUR_WEIGHT_VALUE["heavy"])
    assert item_value(light) > item_value(heavy)

def test_item_value_of_a_healing_item_follows_how_much_it_heals():
    assert item_value(Consumable(name="Tonic", description="", heal_amount=12)) == 12 * VALUE_PER_HEAL

def test_item_value_of_a_full_heal_is_fixed():
    assert item_value(Consumable(name="Pomegranate", description="", heal_amount=999)) == FULL_HEAL_VALUE

def test_item_value_of_a_status_effect_item_counts_every_tick():
    regen = StatusEffectItem(name="Cup", description="", effect_name="Regen", amount=4, duration=4)
    poison = StatusEffectItem(name="Vial", description="", effect_name="Poison", amount=-3, duration=3)
    assert item_value(regen) == 4 * 4 * VALUE_PER_HEAL
    assert item_value(poison) == 3 * 3 * VALUE_PER_HEAL

def test_item_value_of_an_intellect_item_follows_its_amount():
    assert item_value(IntellectReward(name="Ledger", description="", amount=2)) == 2 * VALUE_PER_INTELLECT

def test_item_value_of_a_skill_point_item_follows_its_points():
    assert item_value(SkillPointReward(name="Favour", description="", points=1)) == VALUE_PER_SKILL_POINT

def test_item_value_of_an_escape_item():
    assert item_value(EscapeItem(name="Feather", description="")) == ESCAPE_ITEM_VALUE

def test_item_value_of_a_spellbook_follows_its_spells_damage():
    book = SpellBook(name="Tome", description="", spell=Spell(name="Bolt", description="", mana_cost=6, damage=8))
    assert item_value(book) == 8 * VALUE_PER_DAMAGE * 2

def test_item_value_of_a_spellbook_counts_a_healing_spell():
    """Regression: only damage was counted, so a book teaching a pure heal was worth 1 gold."""
    book = SpellBook(name="Tome", description="", spell=Spell(name="Mend", description="", mana_cost=4, heal_amount=5))
    assert item_value(book) == 5 * VALUE_PER_HEAL * 2

def test_item_value_of_a_spellbook_counts_a_status_effect():
    spell = Spell(name="Blight", description="", mana_cost=4, effect_name="Poison", effect_amount=-3, effect_duration=3)
    assert item_value(SpellBook(name="Tome", description="", spell=spell)) == 3 * 3 * VALUE_PER_HEAL * 2

def test_item_value_is_never_below_one_for_something_sellable():
    assert item_value(Weapon(name="Fangs", description="", damage=0)) == 1
    assert item_value(SpellBook(name="Tome", description="", spell=Spell(name="Nothing", description="", mana_cost=4))) == 1

def test_item_value_override_wins_over_the_formula():
    sword = Weapon(name="Sword", description="", damage=5)
    sword.value_override = 7
    assert item_value(sword) == 7

def test_item_value_override_never_makes_a_quest_item_sellable():
    key = QuestItem(name="Key", description="")
    key.value_override = 50
    assert item_value(key) is None

# ---- sale_price ----

def test_sale_price_is_a_fraction_of_the_value():
    sword = Weapon(name="Sword", description="", damage=5)
    assert sale_price(sword) == int(item_value(sword) * SALE_FRACTION)

def test_sale_price_of_something_unsellable_is_none():
    assert sale_price(QuestItem(name="Key", description="")) is None

def test_sale_price_of_damaged_armour_is_lower_by_the_cost_of_repairing_it():
    plate = Armour(name="Plate", description="", defence=5, max_durability=10)
    full = sale_price(plate)
    plate.durability = 6
    assert sale_price(plate) == full - 4 * REPAIR_COST_PER_POINT

def test_sale_price_of_armour_never_drops_below_one():
    rag = Armour(name="Rag", description="", defence=1, max_durability=10)
    rag.durability = 0
    assert sale_price(rag) == 1

def test_repairing_armour_before_selling_it_never_pays_for_itself():
    """Regression: the price first fell in proportion to durability, so a point of the Laestrygonian Hide was worth more than the 2 gold it cost
    to repair. Checked for every real piece of armour, at every level of wear."""
    from dungeon_crawler.dev_tools import ITEM_REGISTRY
    for factory in ITEM_REGISTRY.values():
        piece = factory()
        if not isinstance(piece, Armour):
            continue
        full = sale_price(piece)
        for durability in range(piece.max_durability):
            piece.durability = durability
            repair_bill = (piece.max_durability - durability) * REPAIR_COST_PER_POINT
            assert full - sale_price(piece) <= repair_bill, (piece.name, durability)

# ---- get_buyer / sell_item ----

def buyer_room():
    room = Room("Landing")
    buyer = Ally(name="Ferryman", buys_items=True)
    room.add_ally(buyer)
    return room, buyer

def test_get_buyer_returns_the_first_ally_who_buys():
    room = Room("Landing")
    room.add_ally(Ally(name="Idler"))
    ferryman = Ally(name="Ferryman", buys_items=True)
    room.add_ally(ferryman)
    assert get_buyer(room) is ferryman

def test_get_buyer_with_no_buyer_returns_none():
    room = Room("Landing")
    room.add_ally(Ally(name="Idler"))
    assert get_buyer(room) is None

def test_sell_item_with_no_buyer():
    player = Player(name="Hero", hp=20)
    player.inventory.add(old_sword())
    assert sell_item("old sword", Room("Empty"), player) == "There's no one here to sell to."
    assert len(player.inventory.items) == 1

def test_sell_item_with_no_name_asks_for_one():
    room, _ = buyer_room()
    player = Player(name="Hero", hp=20)
    player.inventory.add(old_sword())
    assert sell_item("", room, player) == "Sell what? Say 'sell' followed by the item's name."
    assert len(player.inventory.items) == 1

def test_sell_item_the_player_does_not_have():
    room, _ = buyer_room()
    assert sell_item("old sword", room, Player(name="Hero", hp=20)) == "No item named 'old sword' in inventory."

def test_sell_item_pays_the_sale_price_and_takes_the_item():
    room, _ = buyer_room()
    player = Player(name="Hero", hp=20)
    sword = old_sword()
    player.inventory.add(sword)
    message = sell_item("old sword", room, player)
    assert message == "Ferryman takes the Old Sword and counts out 10 gold."
    assert player.gold == 10
    assert sword not in player.inventory.items

def test_sell_item_refuses_an_item_that_is_only_held_equipped():
    room, _ = buyer_room()
    player = Player(name="Hero", hp=20)
    sword = old_sword()
    player.inventory.add(sword)
    sword.use(player)
    assert sell_item("old sword", room, player) == "You'll need to unequip the Old Sword first."
    assert (player.gold, sword in player.inventory.items) == (0, True)

def test_sell_item_sells_the_unequipped_copy_when_another_is_equipped():
    room, _ = buyer_room()
    player = Player(name="Hero", hp=20)
    worn, spare = old_sword(), old_sword()
    player.inventory.add(worn); player.inventory.add(spare)
    worn.use(player)
    sell_item("old sword", room, player)
    assert worn in player.inventory.items
    assert spare not in player.inventory.items

def test_sell_item_refuses_a_quest_item():
    room, _ = buyer_room()
    player = Player(name="Hero", hp=20)
    key = QuestItem(name="Bronze Key", description="")
    player.inventory.add(key)
    assert sell_item("bronze key", room, player) == "Ferryman won't take the Bronze Key."
    assert key in player.inventory.items

# ---- shop_offer ----

def test_shop_offer_prices_stock_at_the_markup_on_its_value():
    offer = shop_offer(old_sword)
    assert offer.gold_cost == item_value(old_sword()) * SHOP_MARKUP
    assert offer.input_factory is None

def test_shop_offer_takes_a_hand_set_price_and_a_floor():
    offer = shop_offer(create_tonic, min_floor=3, price=15)
    assert (offer.gold_cost, offer.min_floor) == (15, 3)

def test_shop_offer_for_something_with_no_value_raises_value_error():
    try:
        shop_offer(lambda: QuestItem(name="Key", description=""))
        assert False, "Expected a ValueError but none was raised"
    except ValueError:
        pass

def test_sell_item_names_an_upgraded_item_with_its_level_and_pays_for_it():
    room, _ = buyer_room()
    player = Player(name="Hero", hp=20)
    sword = old_sword()
    sword.upgrade_level = 2
    player.inventory.add(sword)
    assert sell_item("old sword", room, player) == "Ferryman takes the Old Sword +2 and counts out 20 gold."
