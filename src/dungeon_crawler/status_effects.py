"""Status Effects - healing, damaging and miss-chance effects on a Character. Most tick at the start of each combat round; a pure miss-chance
effect (Blinded) counts down once per attack instead - see StatusEffect.counts_down_on_attack."""

class StatusEffect:
    """A single ongoing effect. amount changes HP each tick - negative damages (poison, flame), positive heals (regen), zero does neither.
    miss_chance adds that much to the affected character's miss chance on every attack while it lasts (see Character.get_miss_chance()) -
    Blinded is the first effect to use it. Lives in Character.active_effects."""

    def __init__(self, name: str, amount: int, duration: int, miss_chance: float = 0.0):
        """Store this effect's identity, its per-tick amount, how many ticks (or, for an attack-counted effect, attacks) remain, and its
        miss_chance."""
        self.name = name
        self.amount = amount
        self.duration = duration
        self.miss_chance = miss_chance

    @property
    def counts_down_on_attack(self) -> bool:
        """An effect that only adds a miss chance (Blinded) lasts a number of the character's *attacks* rather than turns, so it always affects
        exactly as many attacks as its duration - regardless of whether it was applied before or after the character's own tick. Counted down
        in Character.attack(), never in tick()."""
        return self.amount == 0 and self.miss_chance > 0

    def tick(self, character) -> str:
        """Apply one tick and count down - except for effects that count down on attack instead, which tick silently without changing.
        Returns the message to show, or '' for an effect with no HP change."""
        if self.counts_down_on_attack:
            return ""
        if self.amount < 0:
            damage = min(-self.amount, character.hp)
            character.hp -= damage
            message = f"{character.name} takes {damage} damage from {self.name}."
        elif self.amount > 0:
            healed = min(self.amount, character.max_hp - character.hp)
            character.hp += healed
            message = f"{character.name} recovers {healed} HP from {self.name}."
        else:
            message = ""
        self.duration -= 1
        return message