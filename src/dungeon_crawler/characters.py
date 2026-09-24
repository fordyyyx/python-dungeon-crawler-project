"""Character classes - Character, Player, Enemy, Ally - and the skill tree system (Skill, SkillPath, SkillTree) that lets a Player unlock permanent stat/ability upgrades."""

from dungeon_crawler.items import Inventory, Item, Weapon, Armour, QuestItem
from dungeon_crawler.status_effects import StatusEffect
from dungeon_crawler.spells import Spell
from dungeon_crawler.world import Room
from textwrap import dedent
from typing import Sequence, Callable
import random

HEAVY_ATTACK_MULTIPLIER: float = 1.75
HEAVY_WEAPON_MULTIPLIER: float = 2.0
HEAVY_ATTACK_MISS_CHANCE: float = 0.4
BLADE_HEAVY_MISS_MODIFIER: float = -0.1
ARMOUR_WEIGHT_MISS_PENALTY: dict[str, float] = {"light": 0.0, "medium": 0.05, "heavy": 0.10}
MAX_MISS_CHANCE: float = 0.95
WEAPON_LIFESTEAL_CAP: int = 3
WEAPON_POISON_AMOUNT: int = -3
WEAPON_POISON_DURATION: int = 3
MINIMUM_DAMAGE: int = 1
HP_PER_LEVEL: int = 2
COMPANION_HP_PER_LEVEL: int = 2
COMPANION_ATTACK_PER_LEVEL: int = 1
STARTING_EXPERIENCE_TO_NEXT_LEVEL: int = 50

class Character:
    """Shared base for anything that can fight - HP, attack, armour, and the ability flags (Double Strike, Thorns, Last Stand) that Skills can turn on."""

    def __init__(self, name: str, hp: int, attack_damage: int, armour: int = 0):
        """Set up base combat stats; ability flags default off until a Skill enables them."""
        self.name = name
        self.hp: int = hp
        self.attack_damage: int = attack_damage
        self.base_armour = armour
        """Armour that doesn't come from worn gear - an enemy's natural armour, ancestry, Defence skills, dev/dummy set. Worn pieces are never added
        into this; see the armour property."""
        self.max_hp: int = hp
        self.equipped_melee_weapon: "Weapon | None" = None
        self.equipped_ranged_weapon: "Weapon | None" = None
        self.equipped_helmet: "Armour | None" = None
        self.equipped_body: "Armour | None" = None
        self.equipped_shield: "Armour | None" = None
        self.has_double_strike = False
        self.has_last_stand = False
        self.has_thorns = False
        self.in_combat = False
        self.current_target: "Enemy | None" = None
        self.pending_damage_reduction = 0
        """Flat damage reduction applied to (and consumed by) the next hit this character takes - set when an Enemy chooses the Defend/Brace
        action (see combat.py's choose_enemy_action()/_score_candidate_actions()). Lives on Character, not Enemy, since take_damage() (the
        only thing that reads it) doesn't know which subclass self is."""
        self.dodge_chance = 0.0
        """Chance (0.0-1.0) to avoid an incoming attack entirely. Set by DodgeSkill. Lives on Character, not Player, same precedent
        as has_thorns/brace_amount - Enemy/Companion use it too (the Shade of Achilles' duel form has 0.15). See also melee_dodge_chance."""
        self.active_effects: list[StatusEffect] = []
        self.turn_started = False
        """Guards start-of-turn ticking (status effects/spell cooldowns) so a free action (a healing item) followed by a turn-ending one in the
        same round only ticks once. Reset to False by resolve_companion_and_enemy_turns() whenever a round actually concludes - see combat.py."""
        self.has_reckless_strength = False
        self.has_measured_casting = False
        self.has_swift_feet = False
        self.has_unyielding_tide = False
        self.has_berserking = False
        self.has_silver_tongue = False
        self.can_ranged_without_weapon = False
        self.has_petrifying_gaze = False
        self.has_bull_rush = False
        self.has_iron_hide = False
        """These ten flags are all secondary-ancestor abilities (see ANCESTRIES['secondary_effect'] in content/ancestries.py) - same shape as
        has_thorns/dodge_chance, but granted once at character creation, never by the skill tree. Deliberately zero overlap with the skill
        tree's four ability flags (has_double_strike, has_last_stand, has_thorns, dodge_chance) - see roadmap.md"""
        self.has_lifesteal = False
        """Heals the attacker for half of damage_dealt (capped at max_hp) on every successful hit - see Character.attack(). Set via Enemy's
        constructor (Lamia is the first use). A lifesteal weapon (Weapon.lifesteal) never touches this flag - attack() reads the weapon directly,
        so unequipping it can't wipe a flag granted by something else."""
        self.melee_dodge_chance: float = 0.0
        """Extra dodge chance against melee attacks only (light and heavy) - added on top of dodge_chance, never applied to ranged attacks or
        spells. How a ranged enemy 'keeps its distance' without the game having any positioning: closing in is hard, so the answer is a bow,
        a spell, or accepting a lot of misses. See take_damage()."""
        self.armour_pierce: int = 0
        """Armour this character's own attacks ignore when they have no weapon doing it - an archer's natural piercing. If a weapon is equipped,
        the higher of the two applies. See attack()."""

    def equipment_defence(self) -> int:
        """Total defence from worn armour pieces (helmet, body, and shield). A broken piece (durability 0) contributes nothing, unless Unyielding
        Tide keeps its defence working."""
        pieces = (self.equipped_helmet, self.equipped_body, self.equipped_shield)
        return sum(
            piece.defence for piece in pieces
            if piece is not None and (piece.durability > 0 or self.has_unyielding_tide)
        )

    @property
    def armour(self) -> int:
        """Total armour - base_armour plus the defence of every worn, unbroken piece. Calculated fresh every time rather than kept as a running
        total, so equipping, unequipping, breaking, repairing, and loading can never disagree about it."""
        return self.base_armour + self.equipment_defence()

    @armour.setter
    def armour(self, value: int) -> None:
        """Setting total armour adjusts base_armour so the total comes out at value. That keeps 'armour += bonus' (DefenceBoostSkill) and 'dev set
        def' / 'dummy set def' working unchanged - both change the base, never a worn piece."""
        self.base_armour = value - self.equipment_defence()

    def armour_weight_penalty(self) -> float:
        """The total miss chance added by the weight of every equipped armour piece (helmet, body, and shield). Broken pieces still count -
        they're still being worn."""
        pieces = (self.equipped_helmet, self.equipped_body, self.equipped_shield)
        return sum(ARMOUR_WEIGHT_MISS_PENALTY[piece.weight] for piece in pieces if piece is not None)

    def get_miss_chance(self, attack_type: str) -> float:
        """The chance an attack of this type misses. Light and ranged attacks only miss through armour weight. Heavy attacks start at
        HEAVY_ATTACK_MISS_CHANCE, are made more reliable by a blade (BLADE_HEAVY_MISS_MODIFIER), add the armour weight penalty, and are then halved
        by Reckless Strength. Always clamped to 0 - MAX_MISS_CHANCE. Spells never call this - armour weight doesn't affect them."""
        chance = self.armour_weight_penalty()
        if attack_type == "heavy":
            chance += HEAVY_ATTACK_MISS_CHANCE
            weapon = self.equipped_melee_weapon
            if weapon is not None and weapon.weapon_class == "blade":
                chance += BLADE_HEAVY_MISS_MODIFIER
            if self.has_reckless_strength:
                chance /= 2
        return min(MAX_MISS_CHANCE, max(0.0, chance))

    def attack(self, target: "Character", attack_type: str = "light", others: "Sequence[Character] | None" = None) -> str:
        """Attack target once, then apply any follow-ups. attack_type picks the weapon slot: 'light' and 'heavy' use equipped_melee_weapon, 'ranged'
        uses equipped_ranged_weapon.

        Miss: rolled first, against get_miss_chance(attack_type). A light/ranged attack only rolls at all if armour weight gives it a chance to miss,
        so an unarmoured attacker never makes a random roll for it.
        Damage: attack_damage + weapon damage, +2 with Berserking at or below half HP. Heavy attacks multiply that by HEAVY_ATTACK_MULTIPLIER, or
        HEAVY_WEAPON_MULTIPLIER with a heavy-class weapon. Bull Rush adds a flat +3 after multiplier against a full HP target. The higher of the
        weapon's armour_pierce and this character's own natural armour_pierce is ignored from the target's armour. Light and heavy attacks
        (and their cleave and Double Strike follow-ups) are melee, so a target's melee_dodge_chance can evade them; ranged attacks never are.
        Follow-ups, in order: lifesteal (Character.has_lifesteal or the weapon's) heals half the damage dealt - a weapon's heal is capped at
        WEAPON_LIFESTEAL_CAP, innate lifesteal never is, and the two never stack (innate wins); cleave (a heavy weapon's signature,
        heavy attacks only) hits the first other living, non-respawning combatant in 'others' for half the swing's damage, whether or not the target
        died. Then, only if the target survived: Petrifying Gaze (15%) and the weapon's own poison_chance each roll separately to poison it, and
        Double Strike hits again for base_damage // 2, ignoring armour.

        Enemy/Companion always calls this with the default ('light', no 'others') and never equip weapons or armour, so they never miss and never cleave."""
        weapon = self.equipped_ranged_weapon if attack_type == "ranged" else self.equipped_melee_weapon

        is_melee = attack_type != "ranged"

        miss_chance = self.get_miss_chance(attack_type)
        if miss_chance > 0 and random.random() < miss_chance:
            if attack_type == "heavy":
                return f"{self.name} swings a heavy blow at {target.name} - but misses!"
            return f"{self.name} attacks {target.name} - but misses!"

        weapon_bonus = weapon.damage if weapon is not None else 0
        base_damage = self.attack_damage + weapon_bonus
        if self.has_berserking and self.hp <= self.max_hp / 2:
            base_damage += 2

        if attack_type == "heavy":
            multiplier = HEAVY_WEAPON_MULTIPLIER if weapon is not None and weapon.weapon_class == "heavy" else  HEAVY_ATTACK_MULTIPLIER
            swing_damage = round(base_damage * multiplier)
        else:
            swing_damage = base_damage

        incoming = swing_damage
        if self.has_bull_rush and target.hp == target.max_hp:
            incoming += 3

        weapon_pierce = weapon.armour_pierce if weapon is not None else 0
        armour_pierce = max(weapon_pierce, self.armour_pierce)
        damage_dealt, death_message = target.take_damage(incoming, attacker=self, armour_pierce=armour_pierce, melee=is_melee)
        deflected = incoming - damage_dealt

        message = f"{self.name} attacks {target.name} for {damage_dealt} damage."
        if deflected > 0:
            message += f" ({deflected} deflected by armour)"

        has_lifesteal = self.has_lifesteal or (weapon is not None and weapon.lifesteal)
        if has_lifesteal and damage_dealt > 0:
            heal = damage_dealt // 2
            if not self.has_lifesteal:
                heal = min(heal, WEAPON_LIFESTEAL_CAP)
            healed = min(heal, self.max_hp - self.hp)
            if healed > 0:
                self.hp += healed
                message += f"\n{self.name} drains {healed} HP from the wound."

        if death_message:
            message += f"\n{death_message}"

        if attack_type == "heavy" and weapon is not None and weapon.cleave:
            message += self._cleave(target, swing_damage // 2, armour_pierce, others)

        if not target.is_alive():
            return message

        if self.has_petrifying_gaze and random.random() < 0.15:
            message += f"\n{target.apply_status_effect(StatusEffect('Poison', -3, 3))}"

        if weapon is not None and weapon.poison_chance > 0 and random.random() < weapon.poison_chance:
            message += f"\n{target.apply_status_effect(StatusEffect('Poison', WEAPON_POISON_AMOUNT, WEAPON_POISON_DURATION))}"

        if getattr(self, "has_double_strike", False):
            # second strike deals half of base_damage (weapon- and Berserking-inclusive, but before the heavy multiplier/Bull Rush), ignoring armour
            second_damage, second_death = target.take_damage(base_damage // 2, attacker=self, ignore_armour=True, melee=is_melee)
            message += f"\n{self.name} strikes again for {second_damage} damage."
            if second_death:
                message += f"\n{second_death}"

        return message

    def _cleave(self, primary: "Character", damage: int, armour_pierce: int, others: "Sequence[Character] | None") -> str:
        """Hit the first other living, non-respawning combatant in others (if any) for damage. Returns the message lines to append, or '' if there
        was nobody else to hit. Any defeat this causes is processed afterwards by resolve_pending_defeats() (combat.py), like any other."""
        second = next(
            (c for c in (others or []) if c is not primary and c.is_alive() and not getattr(c, "respawns", False)),
            None,
        )
        if second is None:
            return ""
        second_damage, second_death = second.take_damage(damage, attacker=self, armour_pierce=armour_pierce, melee=True)
        message = f"\nThe swing carries on into {second.name} for {second_damage} damage."
        if second_death:
            message += f"\n{second_death}"
        return message

    def take_damage(self, amount: int, attacker: "Character | None" = None, ignore_armour: bool = False, armour_pierce: int = 0, melee: bool = False) -> tuple[int, str]:
        """Apply any pending Defend/Brace reduction, then armour-reduced damage, handling Last Stand and Thorns along the way. Returns
        (actual damage dealt, message) - message is empty if the target survived with nothing noteworthy to report. pending_damage_reduction
        is consumed (reset to 0) here regardless of whether it changed anything, since a brace only ever protects against the next hit taken.
        ignore_armour skips the armour subtraction (used by Double Strike's second hit); armour_pierce lowers the armour applied, never below 0
        (a piercing weapon, or the attacker's natural pierce). melee=True - passed by attack() for light/heavy attacks and cleave - also lets
        melee_dodge_chance evade the hit, on the same roll as dodge_chance: below dodge_chance is an ordinary dodge, below the two combined is
        'stays just out of reach'. Spells and ranged attacks leave melee False. Every worn piece loses 1 durability per hit that isn't dodged. Any hit with amount > 0 that isn't dodged deals at
        least MINIMUM_DAMAGE, however much brace/armour/Iron Hide would otherwise absorb - a 0-damage attacker still deals 0."""
        roll = random.random()
        if roll < self.dodge_chance:
            return 0, f"{self.name} dodges the attack!"
        if melee and roll < self.dodge_chance + self.melee_dodge_chance:
            return 0, f"{self.name} stays just out of reach!"

        braced_amount = max(0, amount - self.pending_damage_reduction)
        self.pending_damage_reduction = 0
        armour_applied = 0 if ignore_armour else max(0, self.armour - armour_pierce)
        reduced = max(0, braced_amount - armour_applied)
        if self.has_iron_hide:
            reduced = max(0, reduced - 1)
        if amount > 0:
            reduced = max(MINIMUM_DAMAGE, reduced)

        for piece in (self.equipped_helmet, self.equipped_body, self.equipped_shield):
            if piece is not None and piece.durability > 0:
                piece.durability -= 1

        would_be_lethal = (self.hp - reduced) <= 0

        if would_be_lethal and getattr(self, "has_last_stand", False) and self.hp > 1:
            # only saves from above 1 HP - already at 1 HP means Last Stand already spent, so this hit is allowed to finish the job
            self.hp = 1
            return reduced, f"{self.name} refuses to fall, clinging to life at 1 HP."

        self.hp -= reduced
        if self.hp < 0:
            self.hp = 0

        message = ""
        if self.has_thorns and attacker is not None and reduced > 0:
            thorns_damage = max(1, reduced // 4)  # guarantee at least 1 reflected even on small hits
            attacker.hp -= thorns_damage
            if attacker.hp < 0:
                attacker.hp = 0
            message += f"\n{attacker.name} takes {thorns_damage} damage from the counter-strike."

        if not self.is_alive():
            death_message = self.on_death()
            return reduced, (message + f"\n{death_message}").strip()
        return reduced, message.strip()

    def apply_status_effect(self, effect: StatusEffect) -> str:
        """Apply a new status effect, or - if one with the same name is already active - prolong its duration by adding the new duration
        on top (decided stacking rule, shared with Spells - see roadmap.md). Reapplication never changes amount, only duration."""
        existing = next((e for e in self.active_effects if e.name == effect.name), None)
        if existing is not None:
            existing.duration += effect.duration
            return f"{self.name}'s {effect.name} is prolonged."
        self.active_effects.append(effect)
        return f"{self.name} is afflicted with {effect.name}."

    def tick_status_effects(self) -> list[str]:
        """Apply one tick of every active effect, removing any that expire after this tick. Stops the moment a tick kills this character
        - same 'stop once dead' precedent as resolve_combat_round() - appending on_death()'s message when that happens."""
        messages = []
        for effect in list(self.active_effects):
            if not self.is_alive():
                break
            messages.append(effect.tick(self))
            if effect.duration <= 0:
                self.active_effects.remove(effect)
        if not self.is_alive():
            messages.append(self.on_death())
        return messages

    def is_alive(self) -> bool:
        """Whether this character's HP is still above zero."""
        return self.hp > 0

    def on_death(self) -> str:
        """Default defeat message; Player and Enemy override this with their own. Does not print - see CLAUDE.md."""
        return (f"{self.name} has died.")

class Player(Character):
    """The player-controlled character - adds levelling, gold, inventory, and the skill tree on top of the shared Character stats."""

    def __init__(self, name: str, hp: int, attack_damage: int = 5, armour: int = 0, ancestry_label: str = ""):
        """Build a fresh level-1 player from the stats chosen at character creation."""
        super().__init__(name, hp, attack_damage, armour)
        self.level = 1
        self.experience = 0
        self.experience_to_next_level = STARTING_EXPERIENCE_TO_NEXT_LEVEL
        self.gold = 0
        """currency earned from defeating enemies. Displayed in the inventory listing, not stats - it isn't a character stat, it's a resource"""
        self.inventory = Inventory()
        self.skill_tree = SkillTree()
        self.ancestry_label = ancestry_label
        self.auto_talk = False
        self.intellect = 0
        self.companion: "Companion | None" = None
        self.known_spells: list[Spell] = []
        self.mana = 20
        self.max_mana = 20
        self.spell_cooldowns: dict[str, int] = {}
        self.secondary_ancestry_label = ""
        self.ancestry_key: str | None = None
        self.secondary_ancestry_key: str | None = None
        """ANCESTRIES keys (content/ancestries.py) - the canonical form of the player's lineage, used to match ancestry_lines. Kept alongside
        ancestry_label/secondary_ancestry_label because labels are display text and may be reworded; keys shouldn't be."""
        self.seen_lines: set[str] = set()
        """Keys for one-off dialogue already shown this save - ancestry lines ('ancestry:<speaker>:<key>') and rival lines
        ('rival:<companion>:<enemy>'). Separate from seen_hints, which is only for hints.HINTs. Saved."""
        self.visited_floors: set[str] = set()
        """Which floors this run has reached, keyed by build_world()'s floor names (e.g. 'floor_0') - populated by main()'s
        autosave on first crossing into a new floor, checked via find_floor_for_room() so re-crossing an already-visited
        floor boundary doesn't re-trigger it."""
        self.visited_rooms: set[str] = set()
        """Names of every room this run has entered - used by the 'uncleared' command, which only reports rooms the player has actually seen,
        so it never reveals the map."""
        self.dev_mode = False
        """Whether developer commands are available for this save - moved off a dev_tools.py module global (see CLAUDE.md's note on why)
        so it's per-save state, not per process. Set once via the 'developer mode' name-trick or the mid-game 'developer mode' toggle,
        persisted through save/load like any other Player field."""
        self.auto_map = False
        """Whether print_room() lists the room's exits automatically on entry - toggled via 'toggle auto map', mirroring auto_talk."""
        self.seen_hints: set[str] = set()
        """Keys from hints.HINTS already shown in this save - see show_hint(). Saved, so a reload doesn't repeat hints."""

    def on_death(self) -> str:
        """Player-specific defeat message, shown when HP reaches zero."""
        return f"{self.name} has fallen. Game Over."

    def get_stats(self) -> str:
        """Format the player's core stats and unlocked skills for display, e.g. via the 'stats' command."""
        heritage = f"{self.ancestry_label}" if self.ancestry_label else ""
        secondary_line = f"\nSecondary gift: {self.secondary_ancestry_label}" if self.secondary_ancestry_label else ""
        weapon_parts = []
        if self.equipped_melee_weapon is not None:
            weapon_parts.append(f"+{self.equipped_melee_weapon.damage} melee")
        if self.equipped_ranged_weapon is not None:
            weapon_parts.append(f"+{self.equipped_ranged_weapon.damage} ranged")
        weapon_summary = f" ({', '.join(weapon_parts)})" if weapon_parts else ""

        unlocked_lines = []
        for path in self.skill_tree.paths.values():
            for skill in path.skills[:path.unlocked_count]:
                unlocked_lines.append(f"  - {skill.name}")
        unlocked_section = "\nUnlocked Skills:\n" + "\n".join(unlocked_lines) if unlocked_lines else ""

        light_miss, heavy_miss, ranged_miss = (round(self.get_miss_chance(t) * 100) for t in ("light", "heavy", "ranged"))

        stat_string = f"""
        {self.name} ({heritage}):
        LVL {self.level} --- {self.experience} XP
        {self.hp} HP
        {self.attack_damage} ATK{weapon_summary}
        {self.armour} DEF
        Miss chance: {light_miss}% light / {heavy_miss}% heavy / {ranged_miss}% ranged
        {self.intellect} INT{secondary_line}
        {unlocked_section}
        """
        return dedent(stat_string).strip()

    def get_inventory_display(self) -> str:
        """Format inventory contents for display, in inventory order - regular items grouped with counts and their details() (e.g. 'blade,
        3 DMG'), except Armour, which is listed one piece per line with its details() including durability (two same-named pieces can differ
        in wear); quest items and gold listed separately."""
        if not self.inventory.items and self.gold == 0:
            return "Your inventory is empty."

        regular_items = [item for item in self.inventory.items if not isinstance(item, QuestItem)]
        quest_items = [item for item in self.inventory.items if isinstance(item, QuestItem)]

        counts: dict[str, int] = {}
        for item in regular_items:
            if not isinstance(item, Armour):
                counts[item.name] = counts.get(item.name, 0) + 1

        equipped_names = {
            item.name for item in regular_items if item.equipped and not isinstance(item, Armour)
        }

        lines =[]
        listed: set[str] = set()
        for item in regular_items:
            if isinstance(item, Armour):
                line = item.name + (" (equipped)" if item.equipped else "") + f" - {item.details()}"
                lines.append(line)
            elif item.name not in listed:
                listed.add(item.name)
                count = counts[item.name]
                line = f"{item.name} x{count}" if count > 1 else item.name
                if item.name in equipped_names:
                    line += " (equipped)"
                details = item.details()
                if details:
                    line += f" - {details}"
                lines.append(line)

        if quest_items:
            quest_names = ", ".join(item.name for item in quest_items)
            lines.append(f"\nQuest Items: {quest_names}")

        if self.gold > 0:
            lines.append(f"\nGold: {self.gold}")

        return "\n".join(lines)

    def get_skills_display(self) -> str:
        """Format skill tree progress - next unlock per path, points available."""
        lines = []
        for path in self.skill_tree.paths.values():
            next_skill = path.next_skill
            if next_skill is not None:
                lines.append(f"{path.name}: next unlock is {next_skill.name} - {next_skill.description}")
            else:
                lines.append(f"{path.name}: fully unlocked.")
        lines.append(f"Skill Points available: {self.skill_tree.skill_points}")
        return "\n".join(lines)

    def gain_experience(self, amount: int) -> str:
        """Add XP; automatically levels up if the threshold is reached. Returns a message describing what happened, doesn't print."""
        self.experience += amount
        message = f"{self.name} gains {amount} experience."
        if self.experience >= self.experience_to_next_level:
            message += f"\n{self.level_up()}"
        return message

    def level_up(self) -> str:
        """Raise level, roll the XP threshold forward, grant one skill point, +1 intellect, and +HP_PER_LEVEL max HP. Current HP rises by the same
        amount rather than fully healing, so levelling up mid-fight doesn't hand out a free full restore."""
        self.level += 1
        self.experience -= self.experience_to_next_level
        self.skill_tree.skill_points += 1
        self.experience_to_next_level = int(self.experience_to_next_level * 1.5)
        self.intellect += 1
        self.max_hp += HP_PER_LEVEL
        self.hp += HP_PER_LEVEL
        return f"{self.name} reaches level {self.level}! +{HP_PER_LEVEL} max HP, and a skill point is available."

    def tick_spell_cooldowns(self) -> None:
        """Decrement every active spell cooldown by one turn, dropping any that reach 0. Call once per player turn, same insertion
        point as tick_status_effects()."""
        expired = [name for name, remaining in self.spell_cooldowns.items() if remaining <= 1]
        for name in expired:
            del self.spell_cooldowns[name]
        for name in self.spell_cooldowns:
            self.spell_cooldowns[name] -= 1

    @property
    def team(self) -> list[Character]:
        """The player's active combat team - Player.self, plus Player.companion if one exists and is currently alive. A downed
        companion (hp == 0) is excluded automatically until revived - see Reviver."""
        team: list["Character"] = [self]
        if self.companion is not None and self.companion.is_alive():
            team.append(self.companion)
        return team


class Enemy(Character):
    """A hostile Character with loot, and optionally a boss phase transition via next_phase_factory."""

    def __init__(self, name: str, hp: int, description: str ="", attack_damage: int = 5, loot: list[Item] | None = None, armour: int = 0, next_phase_factory = None, next_wave_factories: list | None = None, wave_gate_factory = None, experience_reward=0, gold_reward=0, aggression_weight: float = 1.0, caution_weight: float = 1.0, randomness_weight: float = 0.3, brace_amount: int = 0, heal_amount: int = 0, respawns: bool = False, has_lifesteal: bool = False, has_petrifying_gaze: bool = False, defeat_effect: "Callable[[Player], str] | None" = None, ancestry_lines: dict[str, str] | None = None, melee_dodge_chance: float = 0.0, armour_pierce: int = 0):
        """experience_reward and gold_reward are granted to the player (and the same experience to their companion) on this enemy's defeat,
        via handle_enemy_defeat() - see combat.py. defeat_effect runs on that same final defeat. melee_dodge_chance and armour_pierce are the
        Character fields of the same name (see there) - the Shade of Paris is the first enemy to set either.
        aggression_weight/caution_weight/randomness_weight feed choose_enemy_action()'s utility scoring (combat.py) - a balanced
        default (1.0/1.0/0.3) suits most enemies; named/boss enemies should get bespoke values tied to their lore.
        brace_amount is the flat damage reduction this enemy applies to itself when it chooses Defend; heal_amount is the flat HP
        it restores when it chooses Heal - heal_amount = 0 excludes Heal from the candidate list entirely (see _score_candidate_actions()),
        not scored at zero. next_wave_factories spawns a set of ordinary adds on a defeat instead of going straight to next_phase_factory
        - each add gets wave_gate_factory set to this phase's own next_phase_factory (the deferred transition), carried on the adds
        themselves rather than tracked on Room/Player. See handle_enemy_defeat()."""
        super().__init__(name, hp, attack_damage, armour)
        self.loot = loot or []
        self.description = description
        self.next_phase_factory = next_phase_factory
        self.next_wave_factories = next_wave_factories
        self.wave_gate_factory = wave_gate_factory
        self.has_been_fled_from = False
        """Set to True the first time the player succesfully flees from this enemy;
            used to vary the room-entry message on a second encounter."""
        self.experience_reward = experience_reward
        self.gold_reward = gold_reward
        self.aggression_weight = aggression_weight
        self.caution_weight = caution_weight
        self.randomness_weight = randomness_weight
        self.brace_amount = brace_amount
        self.heal_amount = heal_amount
        self.respawns = respawns
        self.has_lifesteal = has_lifesteal
        self.has_petrifying_gaze = has_petrifying_gaze
        self.defeat_effect = defeat_effect
        """Optional function run once when this enemy is finally defeated (not on an intermediate boss phase), returning a message line. A generic
        hook, never a name check: Achilles' duel form uses it to grant a skill point, and Hades will use it for the reveal."""
        self.duel_companion: "Companion | None" = None
        """Set by start_duel() (exploration.py) on the combat form of a companion who's being duelled - the companion to put back in the room when
        the duel ends, whichever way it goes. None for every ordinary enemy."""
        self.duel_return_hp: int | None = None
        """The player's HP when this duel began - set by start_duel(), restored whenever the duel ends (win, loss, or flee), so a friendly fight
        never leaves the player worse off. None for every ordinary enemy."""
        self.ancestry_lines = ancestry_lines or {}
        """ANCESTRIES key -> a line shown once, the first time a player of that lineage sees this enemy - see get_enemy_ancestry_lines() (exploration.py).
        Same shape as Ally/Companion.ancestry_lines, but triggered on sight rather than by 'talk', since enemies can't be talked to."""
        self.melee_dodge_chance = melee_dodge_chance
        self.armour_pierce = armour_pierce

    def on_death(self) -> str:
        """Enemy-specific defeat message, listing any dropped loot."""
        message = f"{self.name} has been defeated."
        if self.loot:
            item_names = ", ".join(item.name for item in self.loot)
            message += f"\nIt dropped: {item_names}"
        return message


class Ally():
    """A non-combat NPC that can be talked to and traded with, per its required_items/reward data - never branched on by name, see CLAUDE.md."""

    def __init__(self, name: str, description: str ='', hint: str ='', hint_complete: str='', required_items: list[str] | None = None, items: list[Item] | None = None, reward: Item | None = None, post_trade_message: str = "", hint_traded: str="", ancestry_lines: dict[str, str] | None = None):
        """Set up an ally's dialogue and starting inventory."""
        self.name = name
        self.description = description
        self.hint = hint
        self.hint_complete = hint_complete
        self.inventory = Inventory()
        self.items = items
        self.required_items = required_items or []
        self.reward = reward
        self.post_trade_message = post_trade_message
        self.trade_completed = False
        for item in self.items or []:
            self.inventory.add(item)
        self.hint_traded = hint_traded
        self.ancestry_lines = ancestry_lines or {}
        """ANCESTRIES key -> a line said once to a player of that lineage, before their usual dialogue - see talk_to() (exploration.py)."""


    def talk(self, player) -> str:
        """Return this ally's dialogue - the completed-trade line takes priority, then the completed-hint if the player already holds every required item, otherwise the regular hint."""
        if self.trade_completed:
            return self.hint_traded or self.hint_complete or self.hint
        if self.required_items:
            player_item_names = [item.name for item in player.inventory.items]
            if all(name in player_item_names for name in self.required_items):
                return self.hint_complete or self.hint
        return self.hint if self.hint else f"{self.name} has nothing to say."

    def give_item(self, item_name : str, player) -> str:
        """Move a named item from this ally's inventory to the player's, if the ally has it."""
        for item in self.inventory.items:
            if item_name.lower() == item.name.lower():
                self.inventory.remove(item)
                player.inventory.add(item)
                return f"{self.name} gives you the {item.name}."
        return f"{self.name} does not have that item."

class Companion(Character):
    """A recruitable ally who fights alongside the player, once recruited via recruit_companion() (see exploration.py). Unlike Ally,
    Companion IS a Character - it needs real combat stats to sit in Player.team and act via choose_companion_action() (combat.py),
    home_room is where a dismissed Companion reappears - see dismiss_companion()."""

    def __init__(self, name: str, hp: int, home_room: Room, description: str = "", attack_damage: int = 5, armour: int = 0, required_items: list[str] | None = None, aggression_weight: float = 1.0, caution_weight: float = 1.0, randomness_weight: float = 0.3, brace_amount: int = 0, heal_amount: int =0, hint: str = "", hint_recruitable: str = "", duel_enemy_factory: "Callable[[], Enemy] | None" = None, duel_won_message: str = "", duel_lost_message: str = "", ancestry_lines: dict[str, str] | None = None, rival_lines: dict[str, str] | None = None):
        """required_items are what the player must hold to recruit this companion (see recruit_companion()) - mirrors Ally.required_items.
        aggression_weight/caution_weight/randomness_weight/brace_amount/heal_amount feed choose_companion_action()'s utility scoring (combat.py)
        - same shape and same defaults as Enemy's equivalent fields. hint/hint_recruitable are this companion's talk() lines, and
        duel_enemy_factory/duel_won_message/duel_lost_message set up a duel they insist on before joining (see start_duel(), exploration.py)."""
        super().__init__(name, hp, attack_damage, armour)
        self.description = description
        self.home_room = home_room
        self.required_items = required_items or []
        self.aggression_weight = aggression_weight
        self.caution_weight = caution_weight
        self.randomness_weight = randomness_weight
        self.brace_amount = brace_amount
        self.heal_amount = heal_amount
        self.hint = hint
        self.hint_recruitable = hint_recruitable
        self.duel_enemy_factory = duel_enemy_factory
        """If set, this companion must be beaten in a duel before they'll join - 'challenge <name>' swaps them for the Enemy this builds
        (see start_duel()). None means they can be recruited straight away, as before."""
        self.duel_won = False
        self.duel_won_message = duel_won_message
        self.duel_lost_message = duel_lost_message
        self.level = 1
        self.experience = 0
        self.experience_to_next_level = STARTING_EXPERIENCE_TO_NEXT_LEVEL
        self.ancestry_lines = ancestry_lines or {}
        self.rival_lines = rival_lines or {}
        """Enemy name -> a line this companion says once, the first time they meet that enemy while in the player's party - see get_rival_lines()
        (exploration.py). Keyed by enemy name as content data; no code ever branches on a particular name."""

    def on_death(self) -> str:
        """Companion-specific 'downed' message - distinct from a permanent death. Fires via the same take_damage()/on_death() mechanism
        as Player/Enemy, but a Companion reaching 0 HP means downed-and-recoverable, not game-ending or gone for good."""
        return f"{self.name} is downed and can no longer fight - a Reviver can bring them back."

    @property
    def requires_duel(self) -> bool:
        """Whether this companion still has to be beaten in a duel before they can be recruited."""
        return self.duel_enemy_factory is not None and not self.duel_won

    def talk(self, player) -> str:
        """This companion's dialogue - the recruitable line once nothing stands in the way of recruiting them, otherwise the regular hint. Mirrors
        Ally.talk()'s shape."""
        if not self.requires_duel and self.hint_recruitable:
            return self.hint_recruitable
        return self.hint if self.hint else f"{self.name} has nothing to say."

    def gain_experience(self, amount: int) -> str:
        """Add experience, levelling up as many times as it covers. Companions follow the same curve as the player - see
        STARTING_EXPERIENCE_TO_NEXT_LEVEL."""
        self.experience += amount
        messages = [f"{self.name} gains {amount} experience."]
        while self.experience >= self.experience_to_next_level:
            self.experience -= self.experience_to_next_level
            messages.append(self._level_up())
        return "\n".join(messages)

    def _level_up(self) -> str:
        """Raise level, roll the threshold forward, and add COMPANION_HP_PER_LEVEL max HP and COMPANION_ATTACK_PER_LEVEL attack. Current HP only
        rises if the companion is still standing, so levelling up can never revive a downed companion - only a Reviver or dismissal does that."""
        self.level += 1
        self.experience_to_next_level = int(self.experience_to_next_level * 1.5)
        self.max_hp += COMPANION_HP_PER_LEVEL
        if self.is_alive():
            self.hp += COMPANION_HP_PER_LEVEL
        self.attack_damage += COMPANION_ATTACK_PER_LEVEL
        return f"{self.name} reaches level {self.level}! (+{COMPANION_HP_PER_LEVEL} max HP, +{COMPANION_ATTACK_PER_LEVEL} ATK)"

    def restore_level(self, level: int, experience: int) -> None:
        """Rebuild level state on a freshly created (level 1) companion when loading a save, replaying each level-up. Stats are recalculated
        rather than saved, so they can never drift from what the levels say - the same lesson as the armour double-counting bug. Callers
        set hp afterwards."""
        for _ in range(level - 1):
            self._level_up()
        self.experience = experience

class Skill:
    """Base class for a single skill-tree unlock; subclasses implement apply() to grant its effect."""

    def __init__(self, name: str, description: str):
        """Store this skill's display name and description."""
        self.name = name
        self.description = description

    def apply(self, character) -> str:
        """Grant this skill's effect to character. Must be implemented by subclasses."""
        raise NotImplementedError

class AttackBoostSkill(Skill):
    """A skill that permanently raises attack_damage by a fixed bonus."""

    def __init__(self, name: str, description: str, bonus: int):
        """Store the attack bonus this skill grants."""
        super().__init__(name, description)
        self.bonus = bonus

    def apply(self, character) -> str:
        """Add this skill's bonus to character's attack_damage."""
        character.attack_damage += self.bonus
        return f"{character.name} gains +{self.bonus} attack from {self.name}."

class DefenceBoostSkill(Skill):
    """A skill that permanently raises armour by a fixed bonus."""

    def __init__(self, name: str, description: str, bonus: int):
        """Store the armour bonus this skill grants."""
        super().__init__(name, description)
        self.bonus = bonus

    def apply(self, character):
        """Add this skill's bonus to character's armour."""
        character.armour += self.bonus
        return f"{character.name} gains +{self.bonus} armour from {self.name}."

class SkillPath:
    """One branch of the skill tree (e.g. Attack, Defence, Abilities) - an ordered list of skills unlocked one at a time."""

    def __init__(self, name: str, skills: list[Skill]):
        """Store this path's name and its skills in unlock order."""
        self.name = name
        self._skills = skills
        self.unlocked_count = 0

    def unlock_next(self, character) -> str:
        """Apply and unlock this path's next skill in order. Raises ValueError if every skill in the path is already unlocked."""
        if self.unlocked_count >= len(self._skills):
            raise ValueError(f"{self.name} path is fully unlocked")
        skill = self._skills[self.unlocked_count]
        self.unlocked_count += 1
        return skill.apply(character)

    @property
    def next_skill(self) -> "Skill | None":
        """The next skill this path would unlock, or None if the path is fully unlocked."""
        if self.unlocked_count >= len(self._skills):
            return None
        return self._skills[self.unlocked_count]

    @property
    def skills(self) -> list[Skill]:
        """A copy of this path's skills, in unlock order."""
        return list(self._skills)

class SkillTree:
    """A player's full set of skill paths, plus the skill_points available to spend on them."""

    def __init__(self):
        """Build the tree with its three fixed paths (Attack, Defence, Abilities) and their skills."""
        self.skill_points = 0
        self.paths: dict[str, SkillPath] = {
            "attack": SkillPath("Attack", [
                AttackBoostSkill("Iron Grip", "Steadier strikes. (+2 ATK)", bonus=2),
                AttackBoostSkill("Honed Instinct", "Every swing finds its mark a little easier. (+3 ATK)", bonus=3),
                AttackBoostSkill("Warrior's Fury", "A hero's strength awakens. (+4 ATK)", bonus=4),
                AttackBoostSkill("Spartan Discipline", "Years of drilling, spent in a single moment. (+5 ATK)", bonus=5),
                AttackBoostSkill("Blessing of Ares", "The war god lends his might. (+6 ATK)", bonus=6),
            ]),
            "defence": SkillPath("Defence", [
                DefenceBoostSkill("Hardened Skin", "Blows land softer. (+2 DEF)", bonus=2),
                DefenceBoostSkill("Steady Stance", "Harder to knock off your feet. (+3 DEF)", bonus=3),
                DefenceBoostSkill("Aegis Ward", "A sliver of divine protection. (+4 DEF)", bonus=4),
                DefenceBoostSkill("Tempered Bronze", "Hammered, heated, and hammered again. (+5 DEF)", bonus=5),
                DefenceBoostSkill("Bronze Resolve", "Nearly unbreakable. (+6 DEF)", bonus=6),
            ]),
            "abilities": SkillPath("Abilities", [
                DoubleStrikeSkill("Twin Strike", "A second blow follows the first, fast and true."),
                ThornsSkill("Retribution", "Every blow against you leaves a mark of its own."),
                LastStandSkill("Last Stand", "Even death hesitates before one so stubborn."),
                DodgeSkill("Nimble Grace", "A hero's step, quick enough to slip past death's reach.", chance=0.35)
            ])
        }

    def invest(self, path_name: str, character) -> str:
        """Spend one skill point unlocking the next skill on path_name. Raises ValueError if no points are available or the path name doesn't exist."""
        if self.skill_points <= 0:
            raise ValueError("No skill points available")
        path = self.paths.get(path_name)
        if path is None:
            raise ValueError(f"No such path: {path_name}")
        message = path.unlock_next(character)
        self.skill_points -= 1
        return message

class DoubleStrikeSkill(Skill):
    """Unlocks Double Strike - see Character.attack() for the second-hit behaviour this flag enables."""

    def apply(self, character) -> str:
        """Turn on character.has_double_strike."""
        character.has_double_strike = True
        return f"{character.name} learns to strike twice in quick succession."

class LastStandSkill(Skill):
    """Unlocks Last Stand - see Character.take_damage() for the survive-at-1-HP behaviour this flag enables."""

    def apply(self, character) -> str:
        """Turn on character.has_last_stand."""
        character.has_last_stand = True
        return f"{character.name} will not fall easily - death itself will have to try twice."

class ThornsSkill(Skill):
    """Unlocks Thorns - see Character.take_damage() for the damage-reflection behaviour this flag enables."""

    def apply(self, character) -> str:
        """Turn on character.has_thorns."""
        character.has_thorns = True
        return f"{character.name} learns to turn an enemy's own strength against them."

class DodgeSkill(Skill):
    """Unlocks a permanent chance to dodge - see Character.take_damage() for the avoid-the-hit-entirely behaviour this grants."""

    def __init__(self, name: str, description: str, chance: float):
        """Store the dodge chance this skill grants."""
        super().__init__(name, description)
        self.chance = chance

    def apply(self, character) -> str:
        """Add this skill's chance to character's dodge_chance."""
        character.dodge_chance += self.chance
        return f"{character.name} learns to slip aside from incoming blows."