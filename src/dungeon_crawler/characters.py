from dungeon_crawler.items import Inventory, Item

class Character:
    def __init__(self, name: str, hp: int, attack_damage: int, armour: int = 0):
        self.name = name
        self.hp = hp
        self.attack_damage = attack_damage
        self.armour = armour
        self.max_hp = hp

    def attack(self, target):
        target.take_damage(self.attack_damage)
        return f"{self.name} attacks {target.name}"

    def take_damage(self, amount: int) -> None:
        reduced = max(0, amount - self.armour)
        self.hp -= reduced
        if self.hp < 0:
            self.hp = 0
        if not self.is_alive():
            self.on_death()


    def is_alive(self) -> bool:
        return self.hp > 0

    def on_death(self) -> None:
        print(f"{self.name} has died.")

class Player(Character):
    def __init__(self, name: str, hp: int, attack_damage: int = 5, armour: int = 0):
        super().__init__(name, hp, attack_damage, armour)
        self.level = 1
        self.experience = 0
        self.inventory = Inventory()

    def on_death(self) -> None:
        print(f"{self.name} has fallen. Game Over.")

    def get_stats(self) -> str:
        inv_string = ", ".join(item.name for item in self.inventory.items)
        stat_string = f"""
        {self.name}:
        LVL {self.level} --- {self.experience} XP
        {self.hp} HP
        {self.attack_damage} ATK
        {self.armour} DEF
        Inventory: {inv_string}
        """
        return stat_string

class Enemy(Character):
    def __init__(self, name: str, hp: int, description: str ="", attack_damage: int = 5, loot: list[Item] | None = None, armour: int = 0):
        super().__init__(name, hp, attack_damage, armour)
        self.loot = loot or []
        self.description = description

    def on_death(self) -> None:
        print(f"{self.name} has been defeated.")
        if self.loot:
            print(f"{self.name} dropped: {', '.join(item.name for item in self.loot)}")

    def choose_action(self, player):
        pass


class Ally():
    def __init__(self, name: str, description: str ='', hint: str =''):
        self.name = name
        self.description = description
        self.hint = hint
        self.inventory = Inventory()

    def talk(self) -> str:
        return self.hint if self.hint else f"{self.name} has nothing to say."

    def give_item(self, item_name : str, player) -> str:
        for item in self.inventory.items:
            if item_name.lower() == item.name.lower():
                self.inventory.remove(item)
                player.inventory.add(item)
                return f"{self.name} gives you the {item.name}."
        return f"{self.name} does not have that item."
