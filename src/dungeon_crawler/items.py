from abc import ABC, abstractmethod

class Item(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def use(self, character) -> str:
        """Apply this item's effect to a character. Returns a message describing what happened."""
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"
class Weapon(Item):
    def __init__(self, name: str, description: str, damage: int):
        super().__init__(name, description)
        self.damage = damage

    def use(self, character) -> str:
        character.attack_damage += self.damage
        return f"{character.name} equips {self.name}, (+{self.damage} attack)."

class Armour(Item):
    def __init__(self, name: str, description: str, defence: int):
        super().__init__(name, description)
        self.defence = defence

    def use(self, character) -> str:
        character.armour += self.defence
        return f"{character.name} equips {self.name}, (+{self.defence} armour)."
    
class Consumable(Item):
    def __init__(self, name: str, heal_amount: int, description: str = ""):
        super().__init__(name, description)
        self.heal_amount = heal_amount

    def use(self, character) -> str:
        character.hp += self.heal_amount
        return f"{character.name} uses {self.name}, healing {self.heal_amount} HP."

class Inventory:
    def __init__(self):
        self._items: list[Item] = []

    def add(self, item: Item) -> None:
        self._items.append(item)

    def remove(self, item: Item) -> None:
        self._items.remove(item)

    def use_item(self, item_name: str, character) -> str:
        for item in self._items:
            if item.name == item_name:
                message = item.use(character)
                if isinstance(item, Consumable):
                    self._items.remove(item)
                return message
        raise ValueError(f"No item named'{item_name}' in inventory.")

    @property
    def items(self) -> list[Item]:
        return list(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __repr__(self) -> str:
        return f"Inventory({[item.name for item in self._items]})"
    