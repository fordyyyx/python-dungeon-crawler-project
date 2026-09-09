"""Character creation - ancestry selection and Player construction, called once at the start of main()."""

from dungeon_crawler.characters import Player
from dungeon_crawler.content import ANCESTRIES
from dungeon_crawler import save_system

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

def choose_title_screen_action() -> str:
    """Prompt New Game / Load Game / Delete Save / Quit, looping until a valid choice. Returns 'new', 'load', 'delete', or 'quit'."""
    print("\n1. New Game\n2. Load Game\n3. Delete Save\n4. Quit\n")
    choices = {"1": "new", "2": "load", "3": "delete", "4": "quit"}
    while True:
        choice = input("> ").strip()
        if choice in choices:
            return choices[choice]
        print("Choose 1, 2, 3, or 4.")

def choose_profile() -> int:
    """Prompt for a profile number (1-PROFILE_LIMIT), looping until valid."""
    print(f"\nWhich profile? (1-{save_system.PROFILE_LIMIT})")
    while True:
        choice = input("> ").strip()
        if choice.isdigit() and 1 <= int(choice) <= save_system.PROFILE_LIMIT:
            return int(choice)
        print(f"Choose a number from 1 to {save_system.PROFILE_LIMIT}.")

def choose_slot(profile_num: int) -> int:
    """Prompt for a slot number (1-SAVE_SLOTS_PER_PROFILE) within profile_num, showing each slot's occupancy/summary. Looping until valid."""
    print(f"\nProfile {profile_num}:")
    for slot_num in range(1, save_system.SAVE_SLOTS_PER_PROFILE + 1):
        summary = save_system.slot_summary(profile_num, slot_num)
        print(f"    {slot_num}. {summary if summary else 'empty'}")
    while True:
        choice = input("> ").strip()
        if choice.isdigit() and 1 <= int(choice) <= save_system.SAVE_SLOTS_PER_PROFILE:
            return int(choice)
        print(f"Choose a number from 1 to {save_system.SAVE_SLOTS_PER_PROFILE}.")

def choose_occupied_slot(profile_num: int) -> int | None:
    """Same as choose_slot(), but only occupied slots are selectable - used by Load Game. Returns None if the profile has no saves at all."""
    occupied = [n for n in range(1, save_system.SAVE_SLOTS_PER_PROFILE + 1) if save_system.slot_exists(profile_num, n)]
    if not occupied:
        print(f"\nProfile {profile_num} has no saves.")
        return None
    print(f"\nProfile {profile_num}:")
    for slot_num in occupied:
        print(f"    {slot_num}. {save_system.slot_summary(profile_num, slot_num)}")
    while True:
        choice = input("> ").strip()
        if choice.isdigit() and int(choice) in occupied:
            return int(choice)
        print("Choose one of the numbers listed above.")

def confirm(prompt: str) -> bool:
    """A yes/no prompt, looping until answered clearly. Shared by every overwrite/delete/reload confirmation."""
    while True:
        choice = input(f"{prompt} (yes/no)\n> ").strip().lower()
        if choice in ("yes", "y"):
            return True
        if choice in ("no", "n"):
            return False
        print("Please answer yes or no.")