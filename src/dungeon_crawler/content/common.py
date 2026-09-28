"""Factories genuinely reused by more than one floor. Standing convention (see CLAUDE.md): a factory starts life in its own floor's
module; the moment a second floor uses it, it moves here. Narrative/unique content (used by exactly one floor) always stays in that
floor's own file, even if it's thematically similar to something here."""

from dungeon_crawler.items import Consumable, Weapon, Armour, StatusEffectItem

def create_small_healing_potion() -> Consumable:
    """Create the Small Healing Potion consumable."""
    return Consumable(
        name="Small Healing Potion",
        heal_amount=5,
        description="A cloudy vial, more herb than magic - enough to steady a shaking hand, not much more."
    )

def create_cup_of_kykeon() -> StatusEffectItem:
    """Create the Cup of Kykeon - a strong heal-over-time (Regen 4 for 4 turns, 16 HP in total). As a positive StatusEffectItem it's a free
    action in combat. Given by Nestor in Shadow of Pylos, ahead of the descent to floor 6."""
    return StatusEffectItem(
        name="Cup of Kykeon",
        description="Wine, barley, and grated goat's cheese - an odd mixture, but it warms you from the inside out.",
        effect_name="Regen",
        amount=4,
        duration=4,
    )