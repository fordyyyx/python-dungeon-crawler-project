class Character:
    def __init__(self, name: str, hp: int, armour: int = 0):
        self.name = name
        self.hp = hp
        self.armour = armour

    def attack(self, target):
        pass

    def take_damage(self, amount: int) -> None:
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0


    def is_alive(self) -> bool:
        return self.hp > 0

class Player(Character):
    def __init__(self, name: str, hp: int, level: int, attack_damage: int, inventory: list, armour: int = 0):
        super().__init__(name, hp, armour)
        self.level = level
        self.attack_damage = attack_damage
        self.inventory = inventory

    def attack(self, target):
        damage = self.attack_damage
        target.take_damage(damage)

class Enemy(Character):
    def __init__(self, name: str, hp: int, attack_damage: int, armour: int = 0):
        super().__init__(name, hp, armour)
        self.attack_damage = attack_damage

    def attack(self, target):
        damage = self.attack_damage
        target.take_damage(damage)