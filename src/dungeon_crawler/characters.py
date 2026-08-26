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

    def attack(self, target: "Character") -> str:
        damage_dealt, death_message = target.take_damage(self.attack_damage)
        message = f"{self.name} attacks {target.name} for {damage_dealt} damage."
        if death_message:
            message += f"\n{death_message}"
            return message

        if getattr(self, "has_double_strike", False):
            second_damage, second_death = target.take_damage(self.attack_damage // 2)
            message += f"\n{self.name} strikes again for {second_damage} damage."
            if second_death:
                message += f"\n{second_death}"

        return message


    def take_damage(self, amount: int) -> tuple[int, str]:
        reduced = max(0, amount - self.armour)
        would_be_lethal = (self.hp - reduced) <= 0

        if would_be_lethal and getattr(self, "has_last_stand", False) and self.hp > 1:
            self.hp = 1
            return reduced, f"{self.name} refuses to fall, clinging to life at 1 HP."

        self.hp -= reduced
        if self.hp < 0:
            self.hp = 0
        if not self.is_alive():
            return reduced, self.on_death()
        return reduced, ""


    def is_alive(self) -> bool:
        return self.hp > 0

    def on_death(self) -> str:
        return (f"{self.name} has died.")

class Player(Character):
    def __init__(self, name: str, hp: int, attack_damage: int = 5, armour: int = 0):
        super().__init__(name, hp, attack_damage, armour)
        self.level = 1
        self.experience = 0
        self.inventory = Inventory()
        self.skill_tree = SkillTree()
        self.equipped_weapon = None
        self.equipped_armour = None

    def on_death(self) -> str:
        return f"{self.name} has fallen. Game Over."

    def get_stats(self) -> str:
        stat_string = f"""
        {self.name}:
        LVL {self.level} --- {self.experience} XP
        {self.hp} HP
        {self.attack_damage} ATK
        {self.armour} DEF
        """
        return dedent(stat_string).strip()

    def get_inventory_display(self) -> str:
        if not self.inventory.items:
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

        return "\n".join(lines)

class Enemy(Character):
    def __init__(self, name: str, hp: int, description: str ="", attack_damage: int = 5, loot: list[Item] | None = None, armour: int = 0):
        super().__init__(name, hp, attack_damage, armour)
        self.loot = loot or []
        self.description = description

    def on_death(self) -> str:
        message = f"{self.name} has been defeated."
        if self.loot:
            item_names = ", ".join(item.name for item in self.loot)
            message += f"\nIt dropped: {item_names}"
        return message

    def choose_action(self, player):
        pass


class Ally():
    def __init__(self, name: str, description: str ='', hint: str ='', hint_complete: str='', required_items: list[str] | None = None, items: list[Item] | None = None, reward: Item | None = None):
        self.name = name
        self.description = description
        self.hint = hint
        self.hint_complete = hint_complete
        self.inventory = Inventory()
        self.items = items
        self.required_items = required_items or []
        self.reward = reward
        for item in self.items or []:
            self.inventory.add(item)


    def talk(self, player) -> str:
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