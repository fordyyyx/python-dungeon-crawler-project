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

def choose_secondary_ancestry(primary_key: str) -> str:
    """Prompt for a secondary ancestro, granting a passive ability rather than stats. Can't match primary_key - 'basic' is the natural
    'skip entirely' option, since it has no secondary_effect."""
    print("\nAnd whose gift, beyond blood, do you also carry>\n")
    for key, data in ANCESTRIES.items():
        if key == primary_key:
            continue
        print(f"    {key} - {data['secondary_ability_label']}")

    while True:
        choice = input("\n> ").strip().lower()
        if choice == primary_key:
            print("You've already claimed that blood - choose a different one, or 'basic' for none.")
            continue
        if choice in ANCESTRIES:
            return choice
        print("That name means nothing to me. Choose from the list above.")

def create_player(name: str, ancestry_key: str, secondary_ancestry_key: str) -> Player:
    """Build a Player from ancestry_key's stats - hp/attack/armour are set outright, replacing Player's defaults rather than adding to them.
    Also sets intellect and grants a bonus skill point if the ancestry includes one. secondary_ancestry_key applies that entry's
    secondary_effect (a passive ability, never stats) - silently does nothing if it matches ancestry_key or has no secondary_effect (e.g. basic')."""
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

    secondary_data = ANCESTRIES.get(secondary_ancestry_key)
    if secondary_data is not None and secondary_ancestry_key != ancestry_key and secondary_data["secondary_effect"] is not None:
        secondary_data["secondary_effect"](player)
        player.secondary_ancestry_label = secondary_data["secondary_ability_label"]
    
    return player