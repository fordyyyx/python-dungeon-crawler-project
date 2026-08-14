from dungeon_crawler.characters import Player, Enemy
from dungeon_crawler.items import Weapon
from dungeon_crawler.world import Room, Map
from dungeon_crawler.content import build_world

def pick_up(room: Room, item_name: str, player: Player) -> str:
    for item in room.items:
        if item.name == item_name:
            player.inventory.add(item)
            room.items.remove(item)
            return f"You take the {item.name}. {item.description}"
    return "That's not here."

def main() -> None:
    dungeon, current_room = build_world()
    player = Player(name="Hero", hp=100)
    while player.is_alive():
        print(f"\n{current_room.name}: {current_room.description}")
        if current_room.enemies:
            enemy = current_room.enemies[0]
            print(f"A {enemy.name} blocks your path!")

        command = input("> ").strip().lower()

        if command.startwith("take "):
            item_name = command.removeprefix("take ").strip()
            print(pick_up(current_room, item_name, player))
        elif command in ("quit", "exit"):
            break
        elif command in current_room.exits:
            current_room = current_room.get_exit(command)
        else:
            print("Nothing happens.")

if __name__ == "__main__":
    main()