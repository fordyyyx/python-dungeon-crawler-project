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
