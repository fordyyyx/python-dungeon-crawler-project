# Greek Mythology Dungeon Crawler
## A text-based dungeon crawler RPG set in Greek mythology, built in pure Python to demonstrate OOP design

This game follows a hero (you) on the descent into the Underworld, facing monsters and mortals from legend on your path to defeat Hades. Train under Chiron, gather relics blessed by the Gods, and take on creatures from across Greek mythology.

It is built purely in Python to demonstrate my skills in object-oriented programming, as well as brush up on things I hadn't used for a while.

## Features
* A guided training prologue that teaches every core mechanic in-fiction, before the main descent begins
* Explore a connected map of rooms
* Turn-based combat
* Item pickup, inventory, use, and unequip
* Friendly NPCs who offer hints, dialogue, and items to trade
* A trading system with equip-state restrictions
* Enemies with loot drops
* Win/lose conditions

## Design Highlights
* **Abstract base class + inheritance** — `Character` → `Player`/`Enemy`; `Item` → `Weapon`/`Armour`/`Consumable`
* **Composition over inheritance** — `Player` *has an* `Inventory`, rather than inheriting one; `Ally` similarly holds its own `Inventory` for items it can give away
* **Encapsulation** — private attributes with controlled access via methods/`@property`, e.g. `Room._items`, `Inventory._items`
* **Polymorphism** — `on_death()` behaves differently per subclass; `use()`/`unequip()` behave differently per `Item` subclass
* **A standalone `Ally` class** (not inheriting `Character`) — friendly NPCs don't carry unused combat stats they'd never use, a deliberate design choice over blanket inheritance

## Installation
* Clone the repo
* Create and activate a virtual environment
* Run:
pip install -e ".[dev]"

## Playing the game
python -m dungeon_crawler

## Running tests
pytest --cov=src/dungeon_crawler


## Controls
* `look` — display room name and description
* `north` / `east` / `south` / `west` — move in that direction
* `talk` — talk to an ally in the room
* `attack` — attack an enemy in the room
* `take <item>` — pick up an item from the room
* `use <item>` — use or equip an item from your inventory
* `unequip <item>` — unequip an item
* `drop <item>` — drop an item into the room
* `take <item> from <ally>` — take an item from an ally's inventory
* `trade` — trade required items with an ally
* `inventory` — display your inventory
* `stats` - display your stats
* `map` - display the unlocked map of the floor
* `quit` / `exit` — quit the game

## Project structure
* `characters.py` — `Character`, `Player`, `Enemy`, `Ally`
* `items.py` — `Item`, `Weapon`, `Armour`, `Consumable`, `Inventory`
* `world.py` — `Room`, `Map`
* `content.py` — the actual game content: specific rooms, enemies, allies, and items
* `engine.py` — the game loop and command-handling logic

## Roadmap
The current release covers a training prologue and the foundational systems (combat, inventory, trading, allies). Planned expansion includes further floors drawing on the Iliad and Odyssey, a skill tree, and additional bosses.

## License
MIT — https://github.com/fordyyyx/python-dungeon-crawler-project/blob/main/LICENSE