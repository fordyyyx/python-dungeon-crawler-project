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

def create_bronze_xiphos() -> Weapon:
    """Create the Bronze Xiphos weapon."""
    return Weapon(
        name="Bronze Xiphos",
        description="A short, leaf-bladed sword - favoured by soldiers who valued speed over reach.",
        damage=3,
    )

def create_aegis_fragment() -> Armour:
    """Create the Shield of Aegis (fragment) armour."""
    return Armour(
        name="Shield of Aegis (fragment)",
        defence=2,
        description="A shard of bronze etched with a single unblinking eye.",
    )