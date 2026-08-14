from dungeon_crawler.characters import Player, Enemy
from dungeon_crawler.items import Weapon
from dungeon_crawler.world import Room, Map
from dungeon_crawler.content import build_world

def main() -> None:
    dungeon, current_room = build_world()
    player = Player(name="Hero", hp=100)
    while player.is_alive():
        print(f"\n{current_room.name}: {current_room.description}")
        if current_room.enemies:
            enemy = current_room.enemies[0]
            print(f"A {enemy.name} blocks your path!")

        command = input("> ").strip().lower()

        if command in ("quite", "exit"):
            break
        elif command in current_room.exits:
            current_room = current_room.get_exit(command)
        else:
            print("Nothing happens.")

if __name__ == "__main___":
    main()