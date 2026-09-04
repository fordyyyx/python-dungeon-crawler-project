"""Character classes - Character, Player, Enemy, Ally - and the skill tree system (Skill, SkillPath, SkillTree) that lets a Player unlock permanent stat/ability upgrades."""

from dungeon_crawler.items import Inventory, Item, Weapon, Armour, QuestItem
from dungeon_crawler.world import Room
from textwrap import dedent
import random

class Character:
    """Shared base for anything that can fight - HP, attack, armour, and the ability flags (Double Strike, Thorns, Last Stand) that Skills can turn on."""

    def __init__(self, name: str, hp: int, attack_damage: int, armour: int = 0):
        """Set up base combat stats; ability flags default off until a Skill enables them."""
        self.name = name
        self.hp = hp
        self.attack_damage = attack_damage
        self.armour = armour
        self.max_hp = hp
        self.equipped_weapon: "Weapon | None" = None
        self.equipped_helmet: "Armour | None" = None
        self.equipped_body: "Armour | None" = None
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
        """Chance (0.0-1.0) to avoid an incoming attack entirely. set by DodgeSkill. Lives on Character, not Player, same precedent
        as has_thorns/brace_amount - Enemy/Companion could plausibly use it too later."""

    def attack(self, target: "Character") -> str:
        """Attack target once, then a second time at half damage if Double Strike is unlocked. Returns the combined message; does not print."""
        incoming = self.attack_damage
        damage_dealt, death_message = target.take_damage(incoming, attacker=self)
        deflected = incoming - damage_dealt

        message = f"{self.name} attacks {target.name} for {damage_dealt} damage."
        if deflected > 0:
            message += f" ({deflected} deflected by armour)"
        if death_message:
            message += f"\n{death_message}"
            return message

        if getattr(self, "has_double_strike", False):
            # second strike deals half damage - a guaranteed extra hit, not a full second attack
            second_damage, second_death = target.take_damage(self.attack_damage // 2, attacker=self)
            message += f"\n{self.name} strikes again for {second_damage} damage."
            if second_death:
                message += f"\n{second_death}"

        return message


    def take_damage(self, amount: int, attacker: "Character | None" = None) -> tuple[int, str]:
        """Apply any pending Defend/Brace reduction, then armour-reduced damage, handling Last Stand and Thorns along the way. Returns
        (actual damage dealt, message) - message is empty if the target survived with nothing noteworthy to report. pending_damage_reduction
        is consumed (reset to 0) here regardless of whether it changed anything, since a brace only ever protects against the next hit taken."""
        if random.random() < self.dodge_chance:
            return 0, f"{self.name} dodges the attack!"

        braced_amount = max(0, amount - self.pending_damage_reduction)
        self.pending_damage_reduction = 0
        reduced = max(0, braced_amount - self.armour)

        for piece in (self.equipped_helmet, self.equipped_body):
            if piece is not None and piece.durability > 0:
                piece.durability -= 1
                if piece.durability == 0:
                    self.armour -= piece.defence

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
        self.experience_to_next_level = 50
        self.gold = 0
        """currency earned from defeating enemies. Displayed in the inventory listing, not stats - it isn't a character stat, it's a resource"""
        self.inventory = Inventory()
        self.skill_tree = SkillTree()
        self.ancestry_label = ancestry_label
        self.auto_talk = False
        self.intellect = 0
        self.companion: "Companion | None" = None

    def on_death(self) -> str:
        """Player-specific defeat message, shown when HP reaches zero."""
        return f"{self.name} has fallen. Game Over."

    def get_stats(self) -> str:
        """Format the player's core stats and unlocked skills for display, e.g. via the 'stats' command."""
        heritage = f"{self.ancestry_label}" if self.ancestry_label else ""
        unlocked_lines = []
        for path in self.skill_tree.paths.values():
            for skill in path.skills[:path.unlocked_count]:
                unlocked_lines.append(f"  - {skill.name}")
        unlocked_section = "\nUnlocked Skills:\n" + "\n".join(unlocked_lines) if unlocked_lines else ""

        stat_string = f"""
        {self.name} ({heritage}):
        LVL {self.level} --- {self.experience} XP
        {self.hp} HP
        {self.attack_damage} ATK
        {self.armour} DEF
        {self.intellect} INT
        {unlocked_section}
        """
        return dedent(stat_string).strip()

    def get_inventory_display(self) -> str:
        """Format inventory contents for display - regular items grouped with counts, quest items and gold listed separately."""
        if not self.inventory.items and self.gold == 0:
            return "Your inventory is empty."

        regular_items = [item for item in self.inventory.items if not isinstance(item, QuestItem)]
        quest_items = [item for item in self.inventory.items if isinstance(item, QuestItem)]

        counts: dict[str, int] = {}
        for item in regular_items:
            counts[item.name] = counts.get(item.name, 0) + 1

        equipped_names = {
            item.name for item in regular_items if item.equipped
        }

        lines =[]
        for name, count in counts.items():
            line = f"{name} x{count}" if count > 1 else name
            if name in equipped_names:
                line += " (equipped)"
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
        """Raise level, roll the XP threshold forward, grant one skill point."""
        self.level += 1
        self.experience -= self.experience_to_next_level
        self.skill_tree.skill_points += 1
        self.experience_to_next_level = int(self.experience_to_next_level * 1.5)
        self.intellect += 1
        return f"{self.name} reaches level {self.level}! A skill point is available."

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

    def __init__(self, name: str, hp: int, description: str ="", attack_damage: int = 5, loot: list[Item] | None = None, armour: int = 0, next_phase_factory = None, experience_reward=0, gold_reward=0, aggression_weight: float = 1.0, caution_weight: float = 1.0, randomness_weight: float = 0.3, brace_amount: int = 0, heal_amount: int = 0):
        """experience_reward and gold_reward are granted to the player on this enemy's defeat, via handle_enemy_defeat() - see engine.py
        aggression_weight/caution_weight/randomness_weight feed choose_enemy_action()'s utility scoring (combat.py) - a balanced
        default (1.0/1.0/0.3) suits most enemies; named/boss enemies should get bespoke values tied to their lore.
        brace_amount is the flat damage reduction this enemy applies to itself when it chooses Defend; heal_amount is the flat HP
        it restores when it chooses Heal - heal_amount = 0 excludes Heal from the candidate list entirely (see _score_candidate_actions()),
        not scored at zero."""
        super().__init__(name, hp, attack_damage, armour)
        self.loot = loot or []
        self.description = description
        self.next_phase_factory = next_phase_factory
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

    def on_death(self) -> str:
        """Enemy-specific defeat message, listing any dropped loot."""
        message = f"{self.name} has been defeated."
        if self.loot:
            item_names = ", ".join(item.name for item in self.loot)
            message += f"\nIt dropped: {item_names}"
        return message


class Ally():
    """A non-combat NPC that can be talked to and traded with, per its required_items/reward data - never branched on by name, see CLAUDE.md."""

    def __init__(self, name: str, description: str ='', hint: str ='', hint_complete: str='', required_items: list[str] | None = None, items: list[Item] | None = None, reward: Item | None = None, post_trade_message: str = ""):
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


    def talk(self, player) -> str:
        """Return this ally's dialogue - the completed-trade line takes priority, then the completed-hint if the player already holds every required item, otherwise the regular hint."""
        if self.trade_completed:
            return self.hint_complete or self.hint
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

    def __init__(self, name: str, hp: int, home_room: Room, description: str = "", attack_damage: int = 5, armour: int = 0, required_items: list[str] | None = None, aggression_weight: float = 1.0, caution_weight: float = 1.0, randomness_weight: float = 0.3, brace_amount: int = 0, heal_amount: int =0):
        """required_items are what the player must hold to recruit this companion (see recruit_companion()) - mirrors Ally.required_items.
        aggression_weight/caution_weight/randomness_weight/brace_amount/heal_amount feed choose_companion_action()'s utility scoring (combat.py)
        - same shape and same defaults as Enemy's equivalent fields."""
        super().__init__(name, hp, attack_damage, armour)
        self.description = description
        self.home_room = home_room
        self.required_items = required_items or []
        self.aggression_weight = aggression_weight
        self.caution_weight = caution_weight
        self.randomness_weight = randomness_weight
        self.brace_amount = brace_amount
        self.heal_amount = heal_amount

    def on_death(self) -> str:
        """Companion-specific 'downed' message - distinct from a permanent death. Fires via the same take_damage()/on_death() mechanism
        as Player/Enemy, but a Companion reaching 0 HP means downed-and-recoverable, not game-ending or gone for good."""
        return f"{self.name} is downed and can no longer fight - a Reviver can bring them back."

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
                AttackBoostSkill("Iron Grip", "Steadier strikes.", bonus=2),
                AttackBoostSkill("Warrior's Fury", "A hero's strength awakens.", bonus=4),
                AttackBoostSkill("Blessing of Ares", "The war god lends his might.", bonus=6),
            ]),
            "defence": SkillPath("Defence", [
                DefenceBoostSkill("Hardened Skin", "Blows land softer.", bonus=2),
                DefenceBoostSkill("Aegis Ward", "A sliver of divine protection.", bonus=4),
                DefenceBoostSkill("Bronze Resolve", "Nearly unbreakable.", bonus=6),
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