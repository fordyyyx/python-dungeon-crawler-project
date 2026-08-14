from dungeon_crawler.items import Inventory, Item

class Character:
    def __init__(self, name: str, hp: int, attack_damage: int, armour: int = 0):
        self.name = name
        self.hp = hp
        self.attack_damage = attack_damage
        self.armour = armour

    def attack(self, target):
        pass

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
    def __init__(self, name: str, hp: int, attack_damage: int, armour: int = 0):
        super().__init__(name, hp, attack_damage, armour)
        self.level = 1
        self.experience = 0
        self.inventory = Inventory()

    def on_death(self) -> None:
        print(f"{self.name} has fallen. Game Over.")

    def attack(self, target):
        damage = self.attack_damage
        target.take_damage(damage)

class Enemy(Character):
    def __init__(self, name: str, hp: int, attack_damage: int = 5, loot: list[Item] | None = None, armour: int = 0):
        super().__init__(name, hp, attack_damage, armour)
        self.loot = loot or []

    def attack(self, target):
        damage = self.attack_damage
        target.take_damage(damage)

    def on_death(self) -> None:
        print(f"{self.name} has been defeated.")
        if self.loot:
            print(f"{self.name} dropped: {', '.join(item.name for item in self.loot)}")

    def choose_action(self, player):
        pass