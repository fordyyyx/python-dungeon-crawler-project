"""Status Effects - Healing and Damaging effects applied at the start of each combat round."""

class StatusEffect:
    """A single ongoing effect - poison/flame/regen are all this same shape, distinguished only by name and the sign of amount
    (negative = damage each tick, positive = healing each tick). Lives in Character.active_effects."""

    def __init__(self, name: str, amount: int, duration: int):
        """Store this effect's identity, its per-tick amount, and how many ticks remain."""
        self.name = name
        self.amount = amount
        self.duration = duration

    def tick(self, character) -> str:
        if self.amount < 0:
            damage = min(-self.amount, character.hp)
            character.hp -= damage
            message = f"{character.name} takes {damage} damage from {self.name}."
        else:
            healed = min(self.amount, character.max_hp - character.hp)
            character.hp += healed
            message = f"{character.name} recovers {healed} HP from {self.name}."
        self.duration -= 1
        return message