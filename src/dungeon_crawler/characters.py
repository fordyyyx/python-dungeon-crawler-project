class Character:
    def __init__(self, name: str, hp: int):
        self.name = name
        self.hp = hp

    def attack(self, target):
        pass

    def take_damage(self, amount: int) -> None:
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0


    def is_alive(self) -> bool:
        return self.hp > 0

class Player(Character):
    def __init__(self, name: str, hp: int, level: int, attack_damage: int, inventory: list):
        super().__init__(name, hp)
        self.level = level
        self.attack_damage = attack_damage
        self.inventory = inventory

    def attack(self, target):
        damage = self.attack_damage
        target.take_damage(damage)

class Enemy(Character):
    def __init__(self, name: str, hp: int, attack_damage: int):
        super().__init__(name, hp)
        self.attack_damage = attack_damage

    def attack(self, target):
        damage = self.attack_damage
        target.take_damage(damage)