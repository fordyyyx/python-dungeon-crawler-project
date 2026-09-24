"""Item classes - Item and its subclasses (Weapon, Armour, Consumable (and its own subclasses Reviver, StatusEffectItem, SpellBook, SkillPointReward), QuestItem) - plus Inventory, which holds and manages a character's items."""

from abc import ABC, abstractmethod
from dungeon_crawler.status_effects import StatusEffect
from dungeon_crawler.spells import Spell

WEAPON_CLASSES = ("blade", "heavy", "piercing", "ranged")
ARMOUR_SLOTS = ("helmet", "body", "shield")
ARMOUR_WEIGHTS = ("light", "medium", "heavy")

class Item(ABC):
    """Base class for anything that can sit in an Inventory; subclasses implement use() for what actually happens when it's used."""

    def __init__(self, name: str, description: str):
        """Store this item's name and description; starts unequipped."""
        self.name = name
        self.description = description
        self.equipped = False

    @abstractmethod
    def use(self, character) -> str:
        """Apply this item's effect to a character. Returns a message describing what happened."""
        raise NotImplementedError

    def __repr__(self) -> str:
        """Debug representation showing the class name and item name."""
        return f"{self.__class__.__name__}(name={self.name!r})"

    def unequip(self, character) -> str:
        """Default no-op for items that can't be equipped; Weapon and Armour override this."""
        return f"{self.name} cannot be unequipped."

    def would_fail(self, character) -> str | None:
        """Default: never fails."""
        return None

    def ends_turn(self, character) -> bool:
        """Whether using this item consumes the player's turn (triggering the enemy's turn) or is a free action. Default True;
        Consumable and StatusEffectItem override this for genuinely healing effects."""
        return True

    def details(self) -> str:
        """A short stat summary for the inventory display (e.g. 'blade, 3 DMG'). Empty by default; Weapon and Armour override it."""
        return ""

class Weapon(Item):
    """An equippable item that deals extra damage while equipped, in one of two slots ('melee' or 'ranged'). A weapon's damage is NOT added into
    Character.attack_damage - it's read directly off whichever slot matches the attack type at the moment of attacking (see Character.attack()),
    so a melee and a ranged weapon worn together never stack.

    weapon_class decides how it fights: 'blade' lowers the heavy-attack miss chance, 'heavy' raises the heavy-attack multiplier but is two-handed
    (can't be used with a shield), 'piercing' ignores armour_pierce points of the target's armour, and 'ranged' is for the ranged slot. lifesteal,
    poison_chance, and cleave are signature properties for unique boss drops. All of these are read from the equipped weapon during attack() -
    never copied onto the character as ability flags, so unequipping can never wipe an ability granted by something else (e.g. an ancestry)."""

    def __init__(self, name: str, description: str, damage: int, slot: str = "melee", weapon_class: str = "blade", armour_pierce: int = 0, lifesteal: bool = False, poison_chance: float = 0.0, cleave: bool = False):
        """Store the weapon's damage, slot, class, and any signature properties. Raises ValueError for an unknown weapon_class."""
        super().__init__(name, description)
        if weapon_class not in WEAPON_CLASSES:
            raise ValueError(f"Unknown weapon_class '{weapon_class}' - must be one of {WEAPON_CLASSES}.")
        self.damage = damage
        self.slot = slot
        self.weapon_class = weapon_class
        self.armour_pierce = armour_pierce
        self.lifesteal = lifesteal
        self.poison_chance = poison_chance
        self.cleave = cleave

    @property
    def two_handed(self) -> bool:
        """Heavy weapons are two-handed - equipping one unequips any shield, and vice-versa."""
        return self.weapon_class == "heavy"

    def details(self) -> str:
        """Class, handedness, piercing, signature properties, then damage - e.g. 'heavy, two-handed, cleave, 7 DMG'."""
        parts = [self.weapon_class]
        if self.two_handed:
            parts.append("two-handed")
        if self.armour_pierce:
            parts.append(f"pierces {self.armour_pierce}")
        if self.lifesteal:
            parts.append("lifesteal")
        if self.poison_chance:
            parts.append(f"{round(self.poison_chance * 100)}% poison")
        if self.cleave:
            parts.append("cleave")
        parts.append(f"{self.damage} DMG")
        return ", ".join(parts)

    def use(self, character) -> str:
        """Equip this weapon into its slot, unequipping whatever currently occupies that same slot first. A two-handed weapon also unequips any
        shield, matching how every other slot swaps rather than refusing."""
        if self.equipped:
            return f"{self.name} already equipped."

        slot_attr = f"equipped_{self.slot}_weapon"
        messages = []
        current = getattr(character, slot_attr)
        if current is not None:
            messages.append(current.unequip(character))

        shield = getattr(character, "equipped_shield", None)
        if self.two_handed and shield is not None:
            messages.append(shield.unequip(character))

        self.equipped = True
        setattr(character, slot_attr, self)
        messages.append(f"{character.name} equips {self.name} ({self.slot}, +{self.damage} DMG).")
        return "\n".join(messages)

    def unequip(self, character) -> str:
        """Clear this weapon from its slot. No longer touches attack_damage - see class docstring."""
        if not self.equipped:
            return f"{self.name} is not equipped."
        self.equipped = False
        slot_attr = f"equipped_{self.slot}_weapon"
        if getattr(character, slot_attr) is self:
            setattr(character, slot_attr, None)
        return f"{character.name} unequips {self.name} (-{self.damage} DMG)"

class Armour(Item):
    """An equippable item that raises armour while equipped, in one of three slots ('helmet', 'body', or shield) - all three can be worn at once.
    A worn, unbroken piece's defence counts towards Character.armour, which is calculated fresh from base_armour plus worn gear - equipping
    and unequipping never add to or subtract from a running total.

    weight ('light', 'medium', or 'heavy') adds a miss chance to every attack the wearer makes - see Character.get_miss_chance(). A shield can't
    be used with a two-handed weapon: equipping one unequips the other, whichever way around."""

    def __init__(self, name: str, description: str, defence: int, slot: str = "body", max_durability: int = 10, weight: str = "light"):
        """Store the armour bonus, slot, durability, and weight. Raises ValueError for an unknown slot or weight."""
        super().__init__(name, description)
        if slot not in ARMOUR_SLOTS:
            raise ValueError(f"Unknown armour slot '{slot}' - must be one of {ARMOUR_SLOTS}.")
        if weight not in ARMOUR_WEIGHTS:
            raise ValueError(f"Unknown armour weight '{weight}' - must be one of {ARMOUR_WEIGHTS}.")
        self.defence = defence
        self.slot = slot
        self.weight = weight
        self.max_durability = max_durability
        self.durability = max_durability
        """Starts full. Reaches 0 via Character.take_damage() (see there) - the item stays equipped but its defence stops counting towards
        Character.armour until repaired at the Forge (see repair_item(), exploration.py)."""

    def details(self) -> str:
        """Slot, weight, defence, and durability - e.g. 'body, heavy, 6 DEF, 18/18 durability'."""
        return f"{self.slot}, {self.weight}, {self.defence} DEF, {self.durability}/{self.max_durability} durability"

    def use(self, character) -> str:
        """Equip this armour into its slot, unequipping whatever currently occupies that same slot first. Equipping a shield also unequips a
        two-handed weapon."""
        if self.equipped:
            return f"{self.name} already equipped"

        slot_attr = f"equipped_{self.slot}"
        messages = []
        current = getattr(character, slot_attr)
        if current is not None:
            messages.append(current.unequip(character))

        weapon = getattr(character, "equipped_melee_weapon", None)
        if self.slot == "shield" and weapon is not None and weapon.two_handed:
            messages.append(weapon.unequip(character))

        self.equipped = True
        setattr(character, slot_attr, self)
        messages.append(f"{character.name} equips {self.name} ({self.slot}, +{self.defence} DEF).")
        return "\n".join(messages)

    def unequip(self, character) -> str:
        """Clear this armour from its slot - its defence stops counting towards Character.armour."""
        if not self.equipped:
            return f"{self.name} is not equipped."
        self.equipped = False
        slot_attr = f"equipped_{self.slot}"
        if getattr(character, slot_attr) is self:
            setattr(character, slot_attr, None)
        return f"{character.name} unequips {self.name} (-{self.defence} DEF)"

class Consumable(Item):
    """A single-use item that heals HP on use; Inventory.use_item() removes it from the inventory afterwards."""

    def __init__(self, name: str, description: str = "", heal_amount: int = 0):
        """Store how much HP this consumable heals."""
        super().__init__(name, description)
        self.heal_amount = heal_amount

    def use(self, character) -> str:
        """Heal character by heal_amount, capped at max_hp - the message reports the HP actually restored, not heal_amount, so a potion used
        near full health doesn't overstate what it did."""
        healed = min(self.heal_amount, character.max_hp - character.hp)
        character.hp += healed
        return f"{character.name} uses {self.name}, healing {healed} HP."

    def ends_turn(self, character) -> bool:
        """A genuine heal (heal_amount > 0) is a free action; anything else (including in the base Consumable's default 0) still ends the turn."""
        return self.heal_amount <= 0

    def would_fail(self, character) -> str | None:
        """Block a genuine heal (heal_amount > 0) at full HP rather than wasting the item. The heal_amount > 0 guard matters: SkillPointReward
        inherits this method and has heal_amount = 0, so it must never be blocked at full HP. Reviver, StatusEffectItem and SpellBook
        all override would_fail() with their own rules, so this doesn't reach them."""
        if self.heal_amount > 0 and character.hp >= character.max_hp:
            return f"{character.name} is already at full health - {self.name} would be wasted."
        return None

class Reviver(Consumable):
    """A single-use item that revives character.companion (a downed Companion, hp == 0), restoring heal_amount HP capped at the companion's
    max_hp - unlike a normal Consumable, this targets the companion, not character itself. Inherits Consumable's auto-remove-after-use
    behaviour in Inventory.use_item() for free. Always ends the turn - overrides Consumable.ends_turn(), since bringing a downed companion back
    is a significant combat action, not a quick self-heal, despite heal_amount always being positive."""

    def use(self, character) -> str:
        """Revive character.companion if one exists and is downed; otherwise explain why nothing happened, since 'no companion to revive'
        isn't a lookup failure the way a missing item name is."""
        companion = getattr(character, "companion", None)
        if companion is None:
            return f"{self.name} has nothing to revive."
        if companion.is_alive():
            return f"{companion.name} doesn't need reviving."
        companion.hp = min(self.heal_amount, companion.max_hp)
        return f"{companion.name} is revived with {companion.hp} HP, thanks to {self.name}."

    def ends_turn(self, character) -> bool:
        """Reviving always costs the turn - see class docstring."""
        return True

    def would_fail(self, character) -> str | None:
        """Mirrors use()'s two no-op cases, so handle_combat_command() rejects them before the Reviver is consumed or a turn is spent."""
        companion = getattr(character, "companion", None)
        if companion is None:
            return f"{self.name} has nothing to revive."
        if companion.is_alive():
            return f"{companion.name} doesn't need reviving."
        return None
class QuestItem(Item):
    """A story item that can't be dropped (see Inventory.drop_item()) and does nothing when used - it exists to be given or traded, not consumed."""

    def use(self, character) -> str:
        """Quest items have no effect of their own when used."""
        return f"{self.name} doesn't do anything on its own - it is meant for someone else."

class SkillPointReward(Consumable):
    """An item that grants skill points on use. Inherits Consumable's auto-remove-after-use behaviour in Inventory.use_item() for free - consumed
    every time, same pattern as Reviver/StatusEffectItem/SpellBook. Not just Favour of Hermes - this is a real bug fix at the class level,
    so it applied to every SkillPointReward that exists of gets created."""

    def __init__(self, name: str, description: str, points: int = 1):
        """Store how many skill points this item grants."""
        super().__init__(name, description)
        self.points = points

    def use(self, character) -> str:
        """Grant character's skill tree points skill points."""
        character.skill_tree.skill_points += self.points
        return f"{character.name} gains {self.points} skill point(s) from {self.name}."

class StatusEffectItem(Consumable):
    """Applies a StatudEffect to the player (if amount is positive, a heal-over-time tonic) or to player.current_target (if negative,
    poison/flame) - reuses the existing target command as the way to aim an offensive one, per roadmap.md's decision, rather than a new
    'use <item> on <target> syntax."""
    def __init__(self, name: str, description: str, effect_name: str, amount: int, duration: int):
        """Store what effect this item applies, and how strong/long it lasts."""
        super().__init__(name, description)
        self.effect_name = effect_name
        self.amount = amount
        self.duration = duration

    def use(self, character) -> str:
        """Build a fresh StatusEffect on each use (so two uses aren't secretly sharing one mutable object) and apply it to self (healing)
        or current_target (offensive - raises ValueError with no target set or a dead one, caught by handle_combat_command()'s existing
        except ValueError, same as every other failed-action case)."""
        effect = StatusEffect(self.effect_name, self.amount, self.duration)
        if self.amount >= 0:
            return character.apply_status_effect(effect)
        if character.current_target is None or not character.current_target.is_alive():
            raise ValueError(f"You need a target for {self.name} - try 'target <enemy>' first.")
        return character.current_target.apply_status_effect(effect)

    def would_fail(self, character) -> str | None:
        if self.amount < 0 and (character.current_target is None or not character.current_target.is_alive()):
            return f"You need a target for {self.name} - try 'target <enemy>' first."
        return None

    def ends_turn(self, character) -> bool:
        """Heal-over-time (amount >= 0) is free, matching Consumable's own rule; offensive (amount < 0) still ends the turn."""
        return self.amount < 0

class SpellBook(Consumable):
    """A single-use item that permanently teaches its spell. Already known - use() returns without consuming."""
    def __init__(self, name: str, description: str, spell: Spell):
        """Store the spell this book teaches."""
        super().__init__(name, description)
        self.spell = spell

    def use(self, character) -> str:
        """Add self.spell to character.known_spells, unless already known."""
        if any(known.name == self.spell.name for known in character.known_spells):
            raise ValueError(f"{character.name} already knows {self.spell.name}.")
        character.known_spells.append(self.spell)
        return f"{character.name} learns {self.spell.name}!"

    def would_fail(self, character) -> str | None:
        if any(known.name == self.spell.name for known in character.known_spells):
            return f"{character.name} already knows {self.spell.name}."
        return None

class Inventory:
    """Holds a character's items - used by both Player and Ally - with add/remove/use/drop/unequip operations and a read-only items property over the private list (see CLAUDE.md)."""

    def __init__(self):
        """Start with an empty item list."""
        self._items: list[Item] = []

    def add(self, item: Item) -> None:
        """Add item to this inventory."""
        self._items.append(item)

    def remove(self, item: Item) -> None:
        """Remove item from this inventory."""
        self._items.remove(item)

    def use_item(self, item_name: str, character) -> str:
        """Use the named item on character, removing it from the inventory afterwards if it's a Consumable. Raises ValueError if no item with that name is present."""
        for item in self._items:
            if item.name.lower() == item_name.lower():
                failure = item.would_fail(character)
                if failure is not None:
                    raise ValueError(failure)
                message = item.use(character)
                if isinstance(item, Consumable):
                    self._items.remove(item)
                return message
        raise ValueError(f"No item named '{item_name}' in inventory.")

    def drop_item(self, item_name: str):
        """Remove and return the named item, for dropping into a Room. Raises ValueError if the item is a QuestItem, is currently equipped, or isn't present."""
        for item in self._items:
            if item.name.lower() == item_name.lower():
                if isinstance(item, QuestItem):
                    raise ValueError(f"{item.name} is too important to drop.")
                if item.equipped:
                    raise ValueError(f"Cannot drop {item.name} while it is equipped.")
                self._items.remove(item)
                return item
        raise ValueError(f"No item named {item_name} in inventory.")

    def unequip_item(self, item_name: str, character) -> str:
        """Unequip the named item from character. Raises ValueError if no item with that name is present."""
        for item in self.items:
            if item.name.lower() == item_name.lower():
                return item.unequip(character)
        raise ValueError(f"No item named {item_name} in inventory.")

    @property
    def items(self) -> list[Item]:
        """A copy of this inventory's items, safe to iterate without exposing the private list."""
        return list(self._items)

    def __len__(self) -> int:
        """Number of items currently in this inventory."""
        return len(self._items)

    def __repr__(self) -> str:
        """Debug representation listing item names."""
        return f"Inventory({[item.name for item in self._items]})"
