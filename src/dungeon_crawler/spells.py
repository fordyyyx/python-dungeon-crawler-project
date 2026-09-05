"""Spells - The one place that holds all things to do with spellcasting."""

from dungeon_crawler.status_effects import StatusEffect

class Spell:
    """A known, castable spell - damage/heal_amount/effect are each optional (default 0/0/None), so a spell can be pure damage, pure heal
    pure status, or a combination, without needing separate subclasses. effect, if set, is a template - cast() builds a fresh StatusEffect
    from it each time, same reasoning as StatusEffectItem."""

    def __init__(self, name: str, description: str, mana_cost: int, damage: int = 0, heal_amount: int = 0, effect_name: str | None = None,
                 effect_amount: int = 0, effect_duration: int = 0):
        self.name = name
        self.description = description
        self.mana_cost = mana_cost
        self.damage = damage
        self.heal_amount = heal_amount
        self.effect_name = effect_name
        self.effect_amount = effect_amount
        self.effect_duration = effect_duration

    def cast(self, caster, target) -> str:
        """Apply this spell's effects. target is only used for damage/offensive-status (self.damage > 0 or a negative effect_amount) -
        a pure heal spell ignores target entirely and always affects caster."""
        messages = []
        if self.heal_amount > 0:
            healed = min(self.heal_amount, caster.max_hp - caster.hp)
            caster.hp += healed
            messages.append(f"{caster.name} recovers {healed} HP.")
        if self.damage > 0:
            if target is None:
                raise ValueError(f"You need a target for {self.name} - try 'target <enemy>' first.")
            dealt, death_message = target.take_damage(self.damage, attacker=caster)
            messages.append(f"{caster.name} casts {self.name} at {target.name} for {dealt} damage.")
            if death_message:
                messages.append(death_message)
        if self.effect_name is not None:
            recipient = caster if self.effect_amount >= 0 else target
            if recipient is None:
                raise ValueError(f"You need a target for {self.name} - try 'target <enemy>' first.")
            if recipient.is_alive():
                effect = StatusEffect(self.effect_name, self.effect_amount, self.effect_duration)
                messages.append(recipient.apply_status_effect(effect))
        return "\n".join(messages)

    def would_fail(self, caster, target) -> str | None:
        """Whether cast(caster, target) would raise instead of succeeding. None means it would succeed."""
        if self.damage > 0 and (target is None or not target.is_alive()):
            return f"You need a target for {self.name} - try 'target <enemy>' first."
        if self.effect_name is not None and self.effect_amount < 0 and (target is None or not target.is_alive()):
            return f"You need a target for {self.name} - try 'target <enemy>' first."
        return None