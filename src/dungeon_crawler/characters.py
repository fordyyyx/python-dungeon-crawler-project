from dungeon_crawler.items import Inventory, Item, Weapon, Armour, QuestItem
from textwrap import dedent

class Character:
    def __init__(self, name: str, hp: int, attack_damage: int, armour: int = 0):
        self.name = name
        self.hp = hp
        self.attack_damage = attack_damage
        self.armour = armour
        self.max_hp = hp
        self.equipped_weapon: "Weapon | None" = None
        self.equipped_armour: "Armour | None" = None
        self.has_double_strike = False
        self.has_last_stand = False
        self.has_thorns = False
        self.in_combat = False
        self.current_target: "Enemy | None" = None

    def attack(self, target: "Character") -> str:
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
            second_damage, second_death = target.take_damage(self.attack_damage // 2, attacker=self)
            message += f"\n{self.name} strikes again for {second_damage} damage."
            if second_death:
                message += f"\n{second_death}"

        return message


    def take_damage(self, amount: int, attacker: "Character | None" = None) -> tuple[int, str]:
        reduced = max(0, amount - self.armour)
        would_be_lethal = (self.hp - reduced) <= 0

        if would_be_lethal and getattr(self, "has_last_stand", False) and self.hp > 1:
            self.hp = 1
            return reduced, f"{self.name} refuses to fall, clinging to life at 1 HP."

        self.hp -= reduced
        if self.hp < 0:
            self.hp = 0

        message = ""
        if self.has_thorns and attacker is not None and reduced > 0:
            thorns_damage = max(1, reduced // 4)
            attacker.hp -= thorns_damage
            if attacker.hp < 0:
                attacker.hp = 0
            message += f"\n{attacker.name} takes {thorns_damage} damage from the counter-strike."
        
        if not self.is_alive():
            death_message = self.on_death()
            return reduced, (message + f"\n{death_message}").strip()
        return reduced, message.strip()


    def is_alive(self) -> bool:
        return self.hp > 0

    def on_death(self) -> str:
        return (f"{self.name} has died.")

class Player(Character):
    def __init__(self, name: str, hp: int, attack_damage: int = 5, armour: int = 0, ancestry_label: str = ""):
        super().__init__(name, hp, attack_damage, armour)
        self.level = 1
        self.experience = 0
        self.experience_to_next_level = 50
        self.gold = 0
        """currency earned from defeating enemies. Displayed in the inventory listing, not stats - it isn't a character stat, it's a resource"""
        self.inventory = Inventory()
        self.skill_tree = SkillTree()
        self.equipped_weapon = None
        self.equipped_armour = None
        self.ancestry_label = ancestry_label
        self.auto_talk = False
        self.intellect = 0

    def on_death(self) -> str:
        return f"{self.name} has fallen. Game Over."

    def get_stats(self) -> str:
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


class Enemy(Character):
    def __init__(self, name: str, hp: int, description: str ="", attack_damage: int = 5, loot: list[Item] | None = None, armour: int = 0, next_phase_factory = None, experience_reward=0, gold_reward=0):
        """experience_reward and gold_reward are granted to the player on this enemy's defeat, via handle_enemy_defeat() - see engine.py"""
        super().__init__(name, hp, attack_damage, armour)
        self.loot = loot or []
        self.description = description
        self.next_phase_factory = next_phase_factory
        self.has_been_fled_from = False
        """Set to True the first time the player succesfully flees from this enemy;
            used to vary the room-entry message on a second encounter."""
        self.experience_reward = experience_reward
        self.gold_reward = gold_reward

    def on_death(self) -> str:
        message = f"{self.name} has been defeated."
        if self.loot:
            item_names = ", ".join(item.name for item in self.loot)
            message += f"\nIt dropped: {item_names}"
        return message

    def choose_action(self, player):
        pass


class Ally():
    def __init__(self, name: str, description: str ='', hint: str ='', hint_complete: str='', required_items: list[str] | None = None, items: list[Item] | None = None, reward: Item | None = None, post_trade_message: str = ""):
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
        if self.trade_completed:
            return self.hint_complete or self.hint
        if self.required_items:
            player_item_names = [item.name for item in player.inventory.items]
            if all(name in player_item_names for name in self.required_items):
                return self.hint_complete or self.hint
        return self.hint if self.hint else f"{self.name} has nothing to say."

    def give_item(self, item_name : str, player) -> str:
        for item in self.inventory.items:
            if item_name.lower() == item.name.lower():
                self.inventory.remove(item)
                player.inventory.add(item)
                return f"{self.name} gives you the {item.name}."
        return f"{self.name} does not have that item."

class Skill:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def apply(self, character) -> str:
        raise NotImplementedError

class AttackBoostSkill(Skill):
    def __init__(self, name: str, description: str, bonus: int):
        super().__init__(name, description)
        self.bonus = bonus

    def apply(self, character) -> str:
        character.attack_damage += self.bonus
        return f"{character.name} gains +{self.bonus} attack from {self.name}."

class DefenceBoostSkill(Skill):
    def __init__(self, name: str, description: str, bonus: int):
        super().__init__(name, description)
        self.bonus = bonus

    def apply(self, character):
        character.armour += self.bonus
        return f"{character.name} gains +{self.bonus} armour from {self.name}."

class SkillPath:
    def __init__(self, name: str, skills: list[Skill]):
        self.name = name
        self._skills = skills
        self.unlocked_count = 0

    def unlock_next(self, character) -> str:
        if self.unlocked_count >= len(self._skills):
            raise ValueError(f"{self.name} path is fully unlocked")
        skill = self._skills[self.unlocked_count]
        self.unlocked_count += 1
        return skill.apply(character)

    @property
    def next_skill(self) -> "Skill | None":
        if self.unlocked_count >= len(self._skills):
            return None
        return self._skills[self.unlocked_count]

    @property
    def skills(self) -> list[Skill]:
        return list(self._skills)

class SkillTree:
    def __init__(self):
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
                LastStandSkill("Last Stand", "Even death hesitates before one so stubborn"),
            ])
        }

    def invest(self, path_name: str, character) -> str:
        if self.skill_points <= 0:
            raise ValueError("No skill points available")
        path = self.paths.get(path_name)
        if path is None:
            raise ValueError(f"No such path: {path_name}")
        message = path.unlock_next(character)
        self.skill_points -= 1
        return message

class DoubleStrikeSkill(Skill):
    def apply(self, character) -> str:
        character.has_double_strike = True
        return f"{character.name} learns to strike twice in quick succession."

class LastStandSkill(Skill):
    def apply(self, character) -> str:
        character.has_last_stand = True
        return f"{character.name} will not fall easily - death itself will have to try twice."

class ThornsSkill(Skill):
    def apply(self, character) -> str:
        character.has_thorns = True
        return f"{character.name} learns to turn an enemy's own strength against them."