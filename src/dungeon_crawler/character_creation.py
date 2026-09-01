"""Character creation - ancestry selection and Player construction, called once at the start of main()."""

from dungeon_crawler.characters import Player
from dungeon_crawler.content import ANCESTRIES

def choose_ancestry() -> str:
    print("\nBefore your descent begins, tell me - whose blood runs in you?\n")
    for key, data in ANCESTRIES.items():
        print(f"    {key} - {data['label']} (ATK {data['attack']} / DEF {data['armour']} / HP {data['hp']})")

    while True:
        choice = input("\n> ").strip().lower()
        if choice in ANCESTRIES:
            return choice
        print("That name means nothing to me. Choose from the list above.")

def create_player(name: str, ancestry_key: str) -> Player:
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