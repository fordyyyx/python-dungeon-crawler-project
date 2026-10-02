"""Factories genuinely reused by more than one place. Standing convention (see CLAUDE.md): a factory starts life in its own floor's
module; the moment a second user needs it - another floor, Charon's stock, or a loot table (loot_tables.py) - it moves here. Narrative/unique
content (used by exactly one floor) always stays in that floor's own file, even if it's thematically similar to something here."""

from dungeon_crawler.items import Consumable, StatusEffectItem, Reviver, Armour, Weapon

def create_small_healing_potion() -> Consumable:
    """Create the Small Healing Potion - a 5 HP heal: dropped on several floors, sold by Charon from the start, and in the early loot table."""
    return Consumable(
        name="Small Healing Potion",
        heal_amount=5,
        description="A cloudy vial, more herb than magic - enough to steady a shaking hand, not much more."
    )

def create_bronze_xiphos() -> Weapon:
    """Create the Bronze Xiphos - the first real blade, given by the Wounded Soldier (floor 1). Also in the early loot table, and one of the
    things Circe will take."""
    return Weapon(
        name="Bronze Xiphos",
        description="A short, leaf-bladed sword - favoured by soldiers who valued speed over reach.",
        damage=3,
        weapon_class="blade",
    )

def create_cup_of_kykeon() -> StatusEffectItem:
    """Create the Cup of Kykeon - a strong heal-over-time (Regen 4 for 4 turns, 16 HP in total). As a positive StatusEffectItem it's a free
    action in combat. Given by Nestor in Shadow of Pylos (floor 5), made by Circe, sold by Charon from floor 6, and in the late loot table and
    the Throne Room's chest."""
    return StatusEffectItem(
        name="Cup of Kykeon",
        description="Wine, barley, and grated goat's cheese - an odd mixture, but it warms you from the inside out.",
        effect_name="Regen",
        amount=4,
        duration=4,
    )

def create_field_dressing() -> Consumable:
    """Create a Field Dressing - a 10 HP heal, the first step up from the Small Healing Potion's 5. Dropped by each Myrmidon Soldier (floor 5), sold by Charon
    from floor 3, and in the early and middle loot tables."""
    return Consumable(
        name="Field Dressing",
        heal_amount=10,
        description="Clean linen and a salve that smells of honey and pine - soldier's way of staying on their feet.",
    )

def create_kelp_poultice() -> Consumable:
    """Create a Kelp Poultice - a 12 HP heal, dropped by each Hippocampus in Poseidon's fight (floor 6), made by Circe, sold by Charon
    from floor 4, and in the middle and late loot tables."""
    return Consumable(
        name="Kelp Poultice",
        heal_amount=12,
        description="A wad of cold, salty kelp that draws the sting out of a wound faster than it has any right to."
    )

def create_obol_of_return() -> Reviver:
    """Create an Obol of Return - a Reviver, bringing a downed companion back with 20 HP. Sold by Charon: the ferryman who carries souls across is
    the one who can carry one back. The first real Reviver in the game; also in the late loot table. Value set by hand, since its worth is in
    what it does, not its numbers."""
    obol = Reviver(
        name="Obol of Return",
        description="A single coin, cold as river water. Pressed into a fallen companion's hand, it pays for a crossing back the other way.",
        heal_amount=20,
    )
    obol.value_override = 25
    return obol

def create_bronze_buckler() -> Armour:
    """Create a Bronze Buckler - a plain medium shield with 2 defence, filling the gap between Wooden Shield (light, 1) and the Chipped Stone
    Aegis (heavy, 3). Sold by Charon from floor 4, and in the middle loot table."""
    return Armour(
        name="Bronze Buckler",
        description="Small, round, and plain, but the bronze is thick where it matters.",
        defence=2,
        slot="shield",
        weight="medium",
        max_durability=12,
    )

def create_bronze_greataxe() -> Weapon:
    """Create a Bronze Greataxe - a plain heavy weapon with 6 damage, below the Labrys (7, cleave). For players who want a heavy weapon without
    beating the Minotaur - so it has to be on sale before him. Sold by Charon from floor 3, and in the middle loot table."""
    return Weapon(
        name="Bronze Greataxe",
        description="A heavy, honest axe - no story behind it, just a lot of bronze on the end of a long handle.",
        damage=6,
        weapon_class="heavy",
    )

def create_hoplite_sword() -> Weapon:
    """Create a Hoplite Sword - a plain blade with 5 damage, between the Bronze Xiphos and Serpent's Kiss (6, poison), for a player who missed the
    optional Sun-scorched Dagger. Sold by Charon from floor 4, and in the late loot table."""
    return Weapon(
        name="Hoplite Sword",
        description="A soldier's sword, well balanced and well kept. Thousands like it were carried to Troy.",
        damage=5,
    )

def create_ambrosia() -> Consumable:
    """Create the Vial of Ambrosia consumable."""
    return Consumable(
        name="Vial of Ambrosia",
        heal_amount=20,
        description="Golden and faintly humming - mortal hands were never meant to hold this.",
    )