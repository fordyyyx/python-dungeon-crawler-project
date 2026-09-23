"""Factories genuinely reused by more than one floor. Standing convention (see CLAUDE.md): a factory starts life in its own floor's
module; the moment a second floor uses it, it moves here. Narrative/unique content (used by exactly one floor) always stays in that
floor's own file, even if it's thematically similar to something here."""

from dungeon_crawler.items import Consumable, Weapon, Armour

def create_small_healing_potion() -> Consumable:
    """Create the Small Healing Potion consumable."""
    return Consumable(
        name="Small Healing Potion",
        heal_amount=5,
        description="A cloudy vial, more herb than magic - enough to steady a shaking hand, not much more."
    )
