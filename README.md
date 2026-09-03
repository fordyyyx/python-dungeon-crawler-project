# Greek Mythology Dungeon Crawler
## A text-based dungeon crawler RPG set in Greek mythology, built in pure Python to demonstrate OOP design

This game follows a hero (you) on the descent into the Underworld, facing monsters and mortals from legend on your path to defeat Hades. Choose your ancestry, train under Chiron, gather relics blessed by the Gods, trade with the friendly and the fallen alike, and grow stronger through a branching skill tree as you push deeper.

It is built purely in Python to demonstrate my skills in object-oriented programming, as well as brush up on things I hadn't used for a while.

## Features
* Character creation — name your hero and choose an ancestry (gods, heroes, and monstrous bloodlines each with their own starting stats and trade-offs)
* A guided training prologue that teaches every core mechanic in-fiction, before the main descent begins
* Explore a connected, multi-floor map of rooms, gated by locked exits and item requirements — some passages are hidden entirely until you stop and `examine` your surroundings
* An Intellect stat, set by ancestry and grown through levelling, that unlocks additional flavour text and lore when examining — never anything required to progress
* Turn-based combat that locks you into an encounter — attack, use an item, check your stats/skills, or flee (fleeing always succeeds, but a healthier enemy has a higher chance of landing a parting hit as you disengage)
* An optional toggleable auto-talk setting, so allies speak automatically on room entry rather than needing `talk` every time
* Item pickup, inventory, use, and unequip — equipping a new weapon or armour piece correctly replaces the old one rather than stacking
* Friendly NPCs with hints, conditional dialogue, and items to trade
* A trading system that checks for both missing and still-equipped items
* Quest items — untradeable, undroppable, and displayed separately from regular gear
* A branching skill tree (Attack, Defence, and Abilities paths) unlocked via skill points earned through trades — or through levelling up, gained by defeating enemies for experience
* Gold, earned from defeating enemies, tracked separately from your core stats
* Special combat abilities — Double Strike, Thorns, and Last Stand
* Enemies with loot drops
* Win/lose conditions

## Design Highlights
* **Abstract base class + inheritance** — `Character` -> `Player`/`Enemy`; `Item` -> `Weapon`/`Armour`/`Consumable`/`QuestItem`
* **Composition over inheritance** — `Player` *has an* `Inventory` and a `SkillTree`, rather than inheriting either; `Ally` similarly holds its own `Inventory` for items it can give away
* **Encapsulation** — private attributes with controlled access via methods/`@property`, e.g. `Room._items`, `Inventory._items`
* **Polymorphism** — `on_death()` behaves differently per subclass; `use()`/`unequip()` behave differently per `Item` subclass; each `Skill` subclass applies its own effect via `apply()`
* **A standalone `Ally` class** (not inheriting `Character`) — friendly NPCs don't carry unused combat stats they'd never use, a deliberate design choice over blanket inheritance
* **Data-driven NPC behaviour** — trade requirements, rewards, and conditional dialogue live as attributes on each `Ally` object, rather than name-based branching in the game loop
* **Data-driven character creation** — ancestry options and their stat trade-offs are defined as data (`ANCESTRIES`), not a chain of conditionals

## Installation
* Clone the repo
* Create and activate a virtual environment
* Run:
```
pip install -e ".[dev]"
```

## Playing the game
```
python -m dungeon_crawler
```
or, once installed:
```
dungeon-crawler
```

## Running tests
```
pytest --cov=src/dungeon_crawler
```

## Controls
* `look` - display room name and description
* `examine` - look closer at your surroundings; may reveal hidden passages
* `examine <item>` - view an item's description
* `north` / `east` / `south` / `west` / `descend` / etc. - move in that direction
* `map` - show the exits available from your current room
* `fullmap` / `world` - show every reachable room on the current floor
* `talk` - talk to an ally in the room
* `toggle auto talk` - allies speak automatically on room entry, without needing `talk` each time
* `attack` - attack an enemy in the room; this locks you into combat until the enemy is defeated or you flee
* `target <name> - set your attack target, persisting across rounds; if two or more enemies share a name, add a number (e.g. `target harpies 2`)
* `flee` - disengage from combat (mid-combat only)
* `take <item>` - pick up an item from the room
* `use <item>` - use or equip an item from your inventory (mid-combat, this uses your turn, and the enemy still acts)
* `unequip <item>` - unequip an item
* `drop <item>` - drop an item into the room (quest items can't be dropped)
* `take <item> from <ally>` - take an item from an ally's inventory
* `trade` - trade required items with an ally for their reward
* `recruit <name>` - recruit a companion who joins your team in combat (requires specific items)
* `dismiss` - release your current companion, who returns home
* `skills` - view your skill tree progress and available points (also available mid-combat)
* `learn <path>` - spend a skill point on the next skill in a path (`attack`, `defence`, or `abilities`) (also available mid-combat)
* `inventory` - display carried items, with equipped gear, quest items, and gold marked separately (also available mid-combat)
* `stats` - display your core stats (including Intellect), ancestry, level, and experience (also available mid-combat)
* `controls` - show the full list of available commands (always available, regardless of state)
* `quit` / `exit` - quit the game

## Project structure
* `characters.py` - `Character`, `Player`, `Enemy`, `Ally`, `Skill`, `SkillPath`, `SkillTree`
* `items.py` - `Item`, `Weapon`, `Armour`, `Consumable`, `QuestItem`, `Inventory`
* `world.py` - `Room`, `Map`
* `content.py` - the actual game content: specific rooms, enemies, allies, and items, organized by floor, plus the ancestry options for character creation
* `combat.py` - combat resolution: attacking, defeat handling, and fleeing
* `exploration.py` - everything outside combat: picking up items, trading, examining, and the map
* `character_creation.py` - ancestry selection and building the player character
* `dev_tools.py` - the developer command set (not part of the standard game)
* `engine.py` - the game loop and top-level command routing

## Roadmap
The current release covers character creation, a training prologue, the foundational systems (combat, inventory, trading, allies, skill tree), and the first main floor. Planned additions include further floors drawing on the Iliad and Odyssey, and additional bosses.

## License
MIT - https://github.com/fordyyyx/python-dungeon-crawler-project/blob/main/LICENSE