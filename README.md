# Greek Mythology Dungeon Crawler
## A text-based dungeon crawler RPG set in Greek mythology, built in pure Python to demonstrate OOP design

This game follows a hero (you) on the descent into a cave, facing various monsters on your path to defeat Hades. Find items from the Gods and take on monsters from legend.
It is built purely in Python to demonstrate my skills in object oriented programming as well as brush up on things I have not used for a while.

## Features
* Explore a connected map of rooms
* Turn-based combat
* Item pickup, inventory, and usage
* Enemies with loot drops
* Win/lose conditions

## Highlights
* Abstract base class + inheritance (Character -> Player/Enemy; Item -> Weapon/Armour/Consumable)
* Composition over inheritance (Player has an Inventory, rather than inheriting one)
* Encapsulation (Private attributes with controlled access via methods/ @property e.g. Room._items)
* Polymorphism (on_death() behaving differently per subclass)

## Installation
* Clone the repo
* Create and activate a virtual environment
* run ``` pip install -e ".[dev]" ```

## Playing the game
run ```python -m dungeon_crawler```

## Controls
* north - move north
* east - move east
* south - move south
* west - move west
* attack - attack enemy
* take *item* - pick up item from room
* use *item* - use item from inventory
* quit/exit - quit game

## License
MIT - https://github.com/fordyyyx/python-dungeon-crawler-project/blob/main/LICENSE
