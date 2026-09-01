"""Item classes - Item and its subclasses (Weapon, Armour, Consumable, QuestItem, SkillPointReward) - plus Inventory, which holds and manages a character's items."""

from abc import ABC, abstractmethod

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
class Weapon(Item):
    """An equippable item that raises attack_damage while equipped."""

    def __init__(self, name: str, description: str, damage: int):
        """Store the attack bonus this weapon grants when equipped."""
        super().__init__(name, description)
        self.damage = damage

    def use(self, character) -> str:
        """Equip this weapon, unequipping character's current weapon first if one is equipped (single-slot per CLAUDE.md - equipping never stacks)."""
        if self.equipped:
            return f"{self.name} already equipped."

        messages = []
        if character.equipped_weapon is not None:
            messages.append(character.equipped_weapon.unequip(character))

        character.attack_damage += self.damage
        self.equipped = True
        character.equipped_weapon = self
        messages.append(f"{character.name} equips {self.name} (+{self.damage} ATK).")
        return "\n".join(messages)

    def unequip(self, character) -> str:
        """Remove this weapon's attack bonus and clear it from character.equipped_weapon."""
        if not self.equipped:
            return f"{self.name} is not equipped."
        character.attack_damage -= self.damage
        self.equipped = False
        if character.equipped_weapon is self:
            character.equipped_weapon = None
        return f"{character.name} unequips {self.name} (-{self.damage} ATK)"

class Armour(Item):
    """An equippable item that raises armour while equipped."""

    def __init__(self, name: str, description: str, defence: int):
        """Store the armour bonus this item grants when equipped."""
        super().__init__(name, description)
        self.defence = defence

    def use(self, character) -> str:
        """Equip this armour, unequipping character's current armour first if any is equipped (single-slot per CLAUDE.md - equipping never stacks)."""
        if self.equipped:
            return f"{self.name} already equipped"

        messages = []
        if character.equipped_armour is not None:
            messages.append(character.equipped_armour.unequip(character))
        character.armour += self.defence
        self.equipped = True
        character.equipped_armour = self
        messages.append(f"{character.name} equips {self.name}, (+{self.defence} DEF).")
        return "\n".join(messages)

    def unequip(self, character) -> str:
        """Remove this armour's defence bonus and clear it from character.equipped_armour."""
        if not self.equipped:
            return f"{self.name} is not equipped."
        character.armour -= self.defence
        self.equipped = False
        if character.equipped_armour is self:
            character.equipped_armour = None
        return f"{character.name} unequips {self.name} (-{self.defence} DEF)"

class Consumable(Item):
    """A single-use item that heals HP on use; Inventory.use_item() removes it from the inventory afterwards."""

    def __init__(self, name: str, heal_amount: int, description: str = ""):
        """Store how much HP this consumable heals."""
        super().__init__(name, description)
        self.heal_amount = heal_amount

    def use(self, character) -> str:
        """Heal character by heal_amount, capped at max_hp."""
        character.hp = min(character.hp + self.heal_amount, character.max_hp)
        return f"{character.name} uses {self.name}, healing {self.heal_amount} HP."

class QuestItem(Item):
    """A story item that can't be dropped (see Inventory.drop_item()) and does nothing when used - it exists to be given or traded, not consumed."""

    def use(self, character) -> str:
        """Quest items have no effect of their own when used."""
        return f"{self.name} doesn't do anything on its own - it is meant for someone else."

class SkillPointReward(Item):
    """An item that grants skill points on use."""

    def __init__(self, name: str, description: str, points: int = 1):
        """Store how many skill points this item grants."""
        super().__init__(name, description)
        self.points = points

    def use(self, character) -> str:
        """Grant character's skill tree points skill points."""
        character.skill_tree.skill_points += self.points
        return f"{character.name} gains {self.points} skill point(s) from {self.name}."

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
    