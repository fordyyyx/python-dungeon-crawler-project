"""The exchange system - offers a character can make: a price in gold, optionally an item handed over, for a new item. Circe's transformations
(floor 6) use both inputs; Charon's shop (roadmap) will reuse this with gold alone. Offers never run out so nothing here needs saving - if a
later merchant needs limited stock, it will also need adding to the save format."""

from dataclasses import dataclass
from typing import Callable

from dungeon_crawler.items import Item

@dataclass
class Offer:
    """One exchange: gold_cost gold, plus input_item (an item name) if set, for a fresh item from output_factory. A factory rather than an item,
    so every exchange gives a new instance - the same reason next_phase_factory is a factory."""

    gold_cost: int
    output_factory: Callable[[], Item]
    input_factory: Callable[[], Item] | None = None

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
        price = f"{self.gold_cost} gold"
        given = f"{self.input_name} + {price}" if self.input_name else price
        return f"{given} -> {self.output_name}"

def get_merchant(room):
    """The first ally in room with any offers, or None."""
    return next((ally for ally in room.allies if ally.offers), None)

def list_offers(room, player) -> str:
    """Every offer made by the merchant in room, numbered, with the player's current gold."""
    merchant = get_merchant(room)
    if merchant is None:
        return "There's no one here to exchange with."
    lines = [f"{merchant.name}'s offers (you have {player.gold} gold):"]
    for number, offer in enumerate(merchant.offers, start=1):
        lines.append(f"    {number}. {offer.describe()}")
    lines.append("Say 'exchange <number>' to accept one.")
    return "\n".join(lines)

def make_exchange(choice: str, room, player) -> str:
    """Accept the numbered offer. Refuses without changing anything if the number is invalid, the required item isn't held (or is only held equipped -
    the same rule as trade_with_ally()), or there isn't enough gold. Otherwise takes the item and gold, and gives a fresh output."""
    merchant = get_merchant(room)
    if merchant is None:
        return "There's no one here to exchange with."
    if not choice.isdigit() or not 1 <= int(choice) <= len(merchant.offers):
        return f"Choose an offer from 1 to {len(merchant.offers)} - say 'offers' to see them."
    offer = merchant.offers[int(choice) - 1]

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

    given = f"{handed_over.with_article(definite=True)} and {offer.gold_cost} gold" if handed_over else f"{offer.gold_cost} gold"
    lines = [f"{merchant.name} takes {given}."]
    if merchant.exchange_line:
        lines.append(merchant.exchange_line)
    lines.append(f"You receive: {output.with_article()}.")
    return "\n".join(lines)