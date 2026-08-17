from dungeon_crawler.characters import Player, Enemy
from dungeon_crawler.items import Weapon
from dungeon_crawler.world import Room, Map
from dungeon_crawler.content import build_world

def pick_up(room: Room, item_name: str, player: Player) -> str:
    for item in room.items:
        if item.name.lower() == item_name.lower():
            player.inventory.add(item)
            room.remove_item(item)
            return f"You take the {item.name}. {item.description}"
    return "That's not here."

def resolve_combat_round(player: Player, enemy: Enemy):
    messages = [player.attack(enemy)]

    if not enemy.is_alive():
        messages.append(f"The {enemy.name} has fallen.")
        return "\n".join(messages)

    messages.append(enemy.attack(player))

    if not player.is_alive():
        messages.append(f"{player.name} has fallen.")

    return "\n".join(messages)

def main() -> None:
    dungeon, current_room = build_world()
    player = Player(name="Hero", hp=100)
    while player.is_alive():
        print(f"\n{current_room.name}: {current_room.description}")
        if current_room.enemies:
            enemy = current_room.enemies[0]
            print(f"A {enemy.name} blocks your path!")

        command = input("> ").strip().lower()

        if command.startswith("take "):
            item_name = command.removeprefix("take ").strip()
            print(pick_up(current_room, item_name, player))

        elif command in ("quit", "exit"):
            break

        elif command in current_room.exits:
            current_room = current_room.exits[command]

        elif command == "attack":
            if current_room.enemies:
                enemy = current_room.enemies[0]
                print(resolve_combat_round(player, enemy))
                if not enemy.is_alive():
                    current_room.remove_enemy(enemy)
            else:
                print("There's nothing here to attack.")

        else:
            print("Nothing happens.")

    if not player.is_alive():
        print(f"\n{player.name} has died. Game over.")

if __name__ == "__main__":
    main()