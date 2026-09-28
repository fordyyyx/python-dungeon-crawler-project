from dungeon_crawler.characters import Player, Ally
from dungeon_crawler.world import Room
from dungeon_crawler.items import Consumable, Weapon
from dungeon_crawler.exchange import Offer, get_merchant, list_offers, make_exchange

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
