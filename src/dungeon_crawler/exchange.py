"""The exchange system - offers a character can make: a price in gold, optionally an item handed over, for a new item. Circe's transformations
(floor 6) mostly take an item; Charon's shop (floor 1) takes gold alone, with stock that unlocks by the deepest floor reached (shop_offer(),
available_offers()). Also item values and selling: item_value() is the one number both a shop's price and a sale are based on, and sell_item()
sells to any ally who buys. Offers never run out so nothing here needs saving - if a later merchant needs limited stock, it will also need
adding to the save format."""

from dataclasses import dataclass
from typing import Callable

from dungeon_crawler.items import Item, Armour, Consumable, EscapeItem, IntellectReward, QuestItem, SkillPointReward, SpellBook, StatusEffectItem, Weapon
from dungeon_crawler.exploration import deepest_floor_reached, REPAIR_COST_PER_POINT

VALUE_PER_DAMAGE = 10
VALUE_PER_PIERCE = 8
VALUE_PER_SIGNATURE = 0
VALUE_PER_DEFENCE = 12
ARMOUR_WEIGHT_VALUE = {"light": 1.25, "medium": 1.0, "heavy": 0.85}
VALUE_PER_HEAL = 2
FULL_HEAL_THRESHOLD = 999
FULL_HEAL_VALUE = 120
VALUE_PER_INTELLECT = 60
VALUE_PER_SKILL_POINT = 80
ESCAPE_ITEM_VALUE = 60
SALE_FRACTION = 0.5
SHOP_MARKUP = 4

@dataclass
class Offer:
    """One exchange: gold_cost gold, plus the item input_factory builds if set (matched by name - see input_name), for a fresh item from
    output_factory. Factories rather than items or names, so every exchange gives a new instance - the same reason next_phase_factory is a
    factory - and the item asked for can never be misspelt."""

    gold_cost: int
    output_factory: Callable[[], Item]
    input_factory: Callable[[], Item] | None = None
    min_floor: int = 0

    @property
    def output_name(self) -> str:
        """The name of what this offer produces."""
        return self.output_factory().name

    @property
    def input_name(self) -> str | None:
        """The name of the item this offer takes, or None for gold alone."""
        return self.input_factory().name if self.input_factory is not None else None

    def describe(self) -> str:
        """A one-line summary, e.g. 'Bronze Xiphos + 20 gold -> Kelp Poultice'."""
        given = []
        if self.input_name:
            given.append(self.input_name)
        if self.gold_cost > 0 or not self.input_name:
            given.append(f"{self.gold_cost} gold")
        return f"{' + '.join(given)} -> {self.output_name}"

def get_merchant(room):
    """The first ally in room with any offers, or None."""
    return next((ally for ally in room.allies if ally.offers), None)

def list_offers(room, player) -> str:
    """Every offer made by the merchant in room, numbered, with the player's current gold."""
    merchant = get_merchant(room)
    if merchant is None:
        return "There's no one here to exchange with."
    offers = available_offers(merchant, player)
    if not offers:
        return f"{merchant.name} has nothing to offer you yet."
    lines = [f"{merchant.name}'s offers (you have {player.gold} gold):"]
    for number, offer in enumerate(offers, start=1):
        lines.append(f"    {number}. {offer.describe()}")
    lines.append("Say 'exchange <number>' to accept one.")
    return "\n".join(lines)

def make_exchange(choice: str, room, player) -> str:
    """Accept the numbered offer. Refuses without changing anything if the number is invalid, the required item isn't held (or is only held equipped -
    the same rule as trade_with_ally()), or there isn't enough gold. Otherwise takes the item and gold, and gives a fresh output."""
    merchant = get_merchant(room)
    if merchant is None:
        return "There's no one here to exchange with."
    offers = available_offers(merchant, player)
    if not offers:
        return f"{merchant.name} has nothing to offer you yet."
    if not choice.isdigit() or not 1 <= int(choice) <= len(offers):
        return f"Choose an offer from 1 to {len(offers)} - say 'offers' to see them."
    offer = offers[int(choice) - 1]

    handed_over = None
    if offer.input_factory is not None:
        wanted = offer.input_factory()
        handed_over = next((i for i in player.inventory.items if i.name == wanted.name and not i.equipped), None)
        if handed_over is None:
            equipped_copy = next((i for i in player.inventory.items if i.name == wanted.name), None)
            if equipped_copy is not None:
                return f"You'll need to unequip {equipped_copy.with_article(definite=True)} first."
            return f"You don't have {wanted.with_article()}."
    if player.gold < offer.gold_cost:
        return f"That costs {offer.gold_cost} gold - you have {player.gold}."

    if handed_over is not None:
        player.inventory.remove(handed_over)
    player.gold -= offer.gold_cost
    output = offer.output_factory()
    player.inventory.add(output)

    given = [handed_over.with_article(definite=True)] if handed_over else []
    if offer.gold_cost > 0:
        given.append(f"{offer.gold_cost} gold")
    lines = [f"{merchant.name} takes {' and '.join(given)}."]
    if merchant.exchange_line:
        lines.append(merchant.exchange_line)
    lines.append(f"You receive: {output.with_article()}.")
    return "\n".join(lines)

def item_value(item: Item) -> int | None:
    """What an item is worth - the single number that both buying from and selling to a merchant are based on. None means it can never be sold:
    quest items, and everything built on them (trophies, keepsakes). A hand-set value_override wins over the formula, for items whose worth
    isn't in their numbers. Never below 1 for anything sellable."""
    if isinstance(item, QuestItem):
        return None
    if item.value_override is not None:
        return item.value_override

    if isinstance(item, Weapon):
        signatures = sum(1 for present in (item.cleave, item.lifesteal, item.poison_chance, item.blind_chance) if present)
        value = item.damage * VALUE_PER_DAMAGE + item.armour_pierce * VALUE_PER_PIERCE + signatures * VALUE_PER_SIGNATURE
    elif isinstance(item, Armour):
        value = round(item.defence * VALUE_PER_DEFENCE * ARMOUR_WEIGHT_VALUE[item.weight])
    elif isinstance(item, EscapeItem):
        value = ESCAPE_ITEM_VALUE
    elif isinstance(item, IntellectReward):
        value = item.amount * VALUE_PER_INTELLECT
    elif isinstance(item, SkillPointReward):
        value = item.points * VALUE_PER_SKILL_POINT
    elif isinstance(item, SpellBook):
        spell = item.spell
        effect = abs(getattr(spell, "effect_amount", 0) or 0) * (getattr(spell, "effect_duration", 0) or 0)
        value = (
            (spell.damage or 0) * VALUE_PER_DAMAGE
            + (getattr(spell, "heal_amount", 0) or 0) * VALUE_PER_HEAL
            + effect * VALUE_PER_HEAL
        ) * 2
    elif isinstance(item, StatusEffectItem):
        value = abs(item.amount) * item.duration * VALUE_PER_HEAL
    elif isinstance(item, Consumable):
        value = FULL_HEAL_VALUE if item.heal_amount >= FULL_HEAL_THRESHOLD else item.heal_amount * VALUE_PER_HEAL
    else:
        return None
    return max(1, value)

def sale_price(item: Item) -> int | None:
    """What a merchant pays for item - SALE_FRACTION of its value, and for armour, less exactly what it would cost to repair
    (REPAIR_COST_PER_POINT for each missing point of durability), so repairing a piece before selling it never turns a profit. None if it can't
    be sold. Never below 1 for anything sellable."""
    value = item_value(item)
    if value is None:
        return None
    price = int(value * SALE_FRACTION)
    if isinstance(item, Armour):
        price -= (item.max_durability - item.durability) * REPAIR_COST_PER_POINT
    return max(1, price)

def available_offers(merchant, player) -> list[Offer]:
    """The offers this merchant shows the player right now - every offer whose min_floor they've reached. The numbers 'exchange' uses come from
    this list, so they only ever count offers the player can actually see."""
    deepest = deepest_floor_reached(player)
    return [offer for offer in merchant.offers if deepest >= offer.min_floor]

def get_buyer(room):
    """The first ally in room who buys items, or None."""
    return next((ally for ally in room.allies if ally.buys_items), None)

def sell_item(item_name: str, room, player) -> str:
    """Sell the named item to the buyer in room for its sale_price(). Refused if no item is named, there's no buyer, the player doesn't have it,
    the only copy is equipped (the same rule as trading), or it can't be sold - quest items, trophies, and keepsakes. If the player has two of the same item and
    one is equipped, the unequipped one is sold."""
    if not item_name:
        return "Sell what? Say 'sell' followed by the item's name."
    buyer = get_buyer(room)
    if buyer is None:
        return "There's no one here to sell to."
    copies = [i for i in player.inventory.items if i.name.lower() == item_name.lower()]
    if not copies:
        return f"No item named '{item_name}' in inventory."
    item = next((i for i in copies if not i.equipped), None)
    if item is None:
        return f"You'll need to unequip {copies[0].with_article(definite=True)} first."
    price = sale_price(item)
    if price is None:
        return f"{buyer.name} won't take {item.with_article(definite=True)}."

    player.inventory.remove(item)
    player.gold += price
    return f"{buyer.name} takes {item.with_article(definite=True)} and counts out {price} gold."

def shop_offer(factory, min_floor: int = 0, price: int | None = None) -> Offer:
    """An offer for a merchant's stock: priced at SHOP_MARKUP times the item's value, unless price sets it by hand. Raises ValueError for an item
    with no value - a programmer mistake, since such an item can never be sold."""
    if price is None:
        value = item_value(factory())
        if value is None:
            raise ValueError(f"{factory().name} has no value, so it can't be stocked by a merchant.")
        price = value * SHOP_MARKUP
    return Offer(gold_cost=price, output_factory=factory, min_floor=min_floor)
