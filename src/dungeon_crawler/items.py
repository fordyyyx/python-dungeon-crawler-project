from abc import ABC, abstractmethod

class Item(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.equipped = False

    @abstractmethod
    def use(self, character) -> str:
        """Apply this item's effect to a character. Returns a message describing what happened."""
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"

    def unequip(self, character) -> str:
        return f"{self.name} cannot be unequipped."
class Weapon(Item):
    def __init__(self, name: str, description: str, damage: int):
        super().__init__(name, description)
        self.damage = damage

    def use(self, character) -> str:
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
        if not self.equipped:
            return f"{self.name} is not equipped."
        character.attack_damage -= self.damage
        self.equipped = False
        if character.equipped_weapon is self:
            character.equipped_weapon = None
        return f"{character.name} unequips {self.name} (-{self.damage} ATK)"

class Armour(Item):
    def __init__(self, name: str, description: str, defence: int):
        super().__init__(name, description)
        self.defence = defence

    def use(self, character) -> str:
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
        if not self.equipped:
            return f"{self.name} is not equipped."
        character.armour -= self.defence
        self.equipped = False
        if character.equipped_armour is self:
            character.equipped_armour = None
        return f"{character.name} unequips {self.name} (-{self.defence} DEF)"
    
class Consumable(Item):
    def __init__(self, name: str, heal_amount: int, description: str = ""):
        super().__init__(name, description)
        self.heal_amount = heal_amount

    def use(self, character) -> str:
        character.hp = min(character.hp + self.heal_amount, character.max_hp)
        return f"{character.name} uses {self.name}, healing {self.heal_amount} HP."

class QuestItem(Item):
    def use(self, character) -> str:
        return f"{self.name} doesn't do anything on its own - it is meant for someone else."

class SkillPointReward(Item):
    def __init__(self, name: str, description: str, points: int = 1):
        super().__init__(name, description)
        self.points = points

    def use(self, character) -> str:
        character.skill_tree.skill_points += self.points
        return f"{character.name} gains {self.points} skill point(s) from {self.name}."

class Inventory:
    def __init__(self):
        self._items: list[Item] = []

    def add(self, item: Item) -> None:
        self._items.append(item)

    def remove(self, item: Item) -> None:
        self._items.remove(item)

    def use_item(self, item_name: str, character) -> str:
        for item in self._items:
            if item.name.lower() == item_name.lower():
                message = item.use(character)
                if isinstance(item, Consumable):
                    self._items.remove(item)
                return message
        raise ValueError(f"No item named '{item_name}' in inventory.")
    
    def drop_item(self, item_name: str):
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
        for item in self.items:
            if item.name.lower() == item_name.lower():
                return item.unequip(character)
        raise ValueError(f"No item named {item_name} in inventory.")

    @property
    def items(self) -> list[Item]:
        return list(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __repr__(self) -> str:
        return f"Inventory({[item.name for item in self._items]})"
    