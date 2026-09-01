"""Character creation - ancestry selection and Player construction, called once at the start of main()."""

from dungeon_crawler.characters import Player
from dungeon_crawler.content import ANCESTRIES

def choose_ancestry() -> str:
    """Prompt the player to pick an ancestry, looping until a valid key is entered. Returns the ancestry's dict key (e.g. 'athena'), not its display label."""
    print("\nBefore your descent begins, tell me - whose blood runs in you?\n")
    for key, data in ANCESTRIES.items():
        print(f"    {key} - {data['label']} (ATK {data['attack']} / DEF {data['armour']} / HP {data['hp']})")

    while True:
        choice = input("\n> ").strip().lower()
        if choice in ANCESTRIES:
            return choice
        print("That name means nothing to me. Choose from the list above.")

def create_player(name: str, ancestry_key: str) -> Player:
    """Build a Player from ancestry_key's stats - hp/attack/armour are set outright, replacing Player's defaults rather than adding to them.
    Also sets intellect and grants a bonus skill point if the ancestry includes one."""
    data = ANCESTRIES[ancestry_key]
    player = Player(
        name=name,
        hp=data['hp'],
        attack_damage=data["attack"],
        armour=data["armour"],
        ancestry_label=data["label"]
    )
    player.intellect = data["intellect"]
    if data["bonus_skill_point"]:
        player.skill_tree.skill_points += 1
    return player