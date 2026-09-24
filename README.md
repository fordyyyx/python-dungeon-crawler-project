# Greek Mythology Dungeon Crawler
## A text-based dungeon crawler RPG set in Greek mythology, built in pure Python to demonstrate OOP design

This game follows a hero (you) on the descent into the Underworld, facing monsters and mortals from legend on your path to defeat Hades. Choose your ancestry, train under Chiron, gather relics blessed by the Gods, trade with the friendly and the fallen alike, recruit a companion to fight at your side, and grow stronger through a branching skill tree and a spellbook as you push deeper.

It is built purely in Python to demonstrate my skills in object-oriented programming, as well as brush up on things I hadn't used for a while.

## Features
* Character creation — name your hero, choose a primary ancestry (gods, heroes, and monstrous bloodlines each with their own starting stats and trade-offs), then a second, different figure for a passive secondary gift — a distinct ability rather than more stats (heavy attacks that miss half as often, spells that never go on cooldown, a guaranteed clean escape, and more)
* A guided training prologue that teaches every core mechanic in-fiction, before the main descent begins
* One-off hints that explain a mechanic the first time it matters (your first fight, the forge, a guarded way forward, an unspent skill point) and then never repeat, even across saves
* Explore a connected, multi-floor map of rooms, gated by locked exits and item requirements (a door stays open once you've opened it) — some passages are hidden entirely until you stop and `examine` your surroundings, and the way forward past a floor's toughest foes stays barred until you've defeated them
* An Intellect stat, set by ancestry and grown through levelling, that unlocks additional flavour text and lore when examining — never anything required to progress
* Turn-based, team-vs-team combat that locks you into an encounter — attack a chosen target, cast a spell, use an item, check your stats/skills, or flee (fleeing always succeeds, but a healthier enemy has a higher chance of landing a parting hit as you disengage)
* Multiple enemies at once, each deciding for itself whether to attack, defend, or heal via a utility-based AI (with a little randomness baked in, so it doesn't always play perfectly) — target a specific enemy by name, disambiguating with a number when more than one shares it
* Recruitable companions who fight alongside you with the same AI-driven decision-making as enemies, and level up as you fight together — a downed companion isn't gone for good, and can be revived or simply dismissed home to recover
* Duels — some companions won't follow you until you've beaten them in a fight of their own; losing a duel isn't a death, and your wounds fade once it's over
* Your lineage is noticed — gods, monsters, and heroes of legend recognise their own descendants (and a companion has things to say about old rivals)
* An optional toggleable auto-talk setting, so allies speak automatically on room entry rather than needing `talk` every time — and an auto-map setting that lists each room's exits the same way
* An `uncleared` command that remembers every room you've visited and lists the ones you haven't finished with yet, plus any new rooms one step away that you haven't explored — without ever spoiling anything further out
* Item pickup, inventory, use, and unequip — weapons occupy two slots (melee and ranged) and armour three (helmet, body, and shield), so a piece in each can be worn at once, only swapping within the same slot — though a two-handed weapon and a shield can't be used together
* Weapon classes that play differently — blades make heavy attacks more reliable, two-handed heavy weapons hit hardest, and piercing weapons cut through armour — plus unique boss drops with their own tricks (a cleave that carries into a second enemy, a fang that drains life, a poisoned blade)
* Armour weight — heavier armour protects more but makes every attack more likely to miss, with your exact miss chances shown in `stats`
* Attack variety — light, heavy (bigger hit, a chance to miss entirely), and ranged (requires an equipped ranged weapon) attacks, chosen per turn
* Armour durability that wears down as you take hits (shown in your inventory) and can be repaired for gold at the Forge of Prometheus — armour softens every blow, but never blocks one completely
* Status effects — poison, flame, and heal-over-time tonics that tick each round, stacking by prolonging duration rather than piling up separate instances
* Spellcasting — a learnable spellbook, a mana pool, and per-spell cooldowns; rest to recover mana between fights
* Friendly NPCs with hints, conditional dialogue that changes before, during, and after a trade, and items to trade
* A trading system that checks for both missing and still-equipped items
* Quest items — untradeable, undroppable, and displayed separately from regular gear
* A branching skill tree (Attack and Defence paths of five escalating tiers each, plus an Abilities path) unlocked via skill points earned through trades — or through levelling up, gained by defeating enemies for experience, which also raises your max HP
* Gold, earned from defeating enemies, tracked separately from your core stats
* Special combat abilities — Double Strike, Thorns, Last Stand, and Dodge
* Enemies with loot drops
* Multi-stage boss fights — a defeated phase can transition seamlessly into the next, or first summon a wave of lesser foes that must all be cleared before the boss reveals what comes after them
* A Practice Chamber (floor 2, by the Forge of Prometheus) with an infinitely-respawning, customisable dummy — freely test weapons/spells/potions with no mana cost or cooldowns while inside
* A full save/load system — 3 profiles, 5 slots each, with a New Game / Load Game / Delete Save title screen, manual save/load commands mid-game, and autosave the first time you reach a new floor
* Win/lose conditions — dying offers a reload from your last save rather than always ending the game outright

## Design Highlights
* **Abstract base class + inheritance** — `Character` -> `Player`/`Enemy`/`Companion`; `Item` -> `Weapon`/`Armour`/`Consumable`/`QuestItem`, and `Consumable` -> `Reviver`/`StatusEffectItem`/`SpellBook`/`SkillPointReward`
* **Composition over inheritance** — `Player` *has an* `Inventory` and a `SkillTree`, rather than inheriting either; `Ally` similarly holds its own `Inventory` for items it can give away
* **Encapsulation** — private attributes with controlled access via methods/`@property`, e.g. `Room._items`, `Inventory._items`
* **Polymorphism** — `on_death()` behaves differently per subclass; `use()`/`unequip()`/`would_fail()` behave differently per `Item` subclass; each `Skill` subclass applies its own effect via `apply()`
* **A standalone `Ally` class** (not inheriting `Character`) — friendly NPCs don't carry unused combat stats they'd never use, a deliberate design choice over blanket inheritance. `Companion` deliberately breaks from that pattern instead: it genuinely *is* a `Character`, since it needs real combat stats to fight alongside the player
* **Data-driven NPC behaviour** — trade requirements, rewards, and conditional dialogue live as attributes on each `Ally` object, rather than name-based branching in the game loop. The same principle extends to combat AI — an enemy or companion's personality (aggression, caution, randomness) is data on the object, not a chain of `if` statements
* **Data-driven character creation** — ancestry options, their stat trade-offs, and each one's secondary passive ability are all defined as data (`ANCESTRIES`), not a chain of conditionals — applying a secondary gift is one shared function call, not a branch per ancestry
* **Utility-based AI** — every enemy and companion scores its candidate actions (attack, defend, heal) each turn based on real combat state (kill potential, incoming threat, missing HP), adds a little randomness, and acts on whichever scores highest — occasionally "wrong," by design, rather than always optimal
* **Validate-then-commit action handling** — spells and certain items expose a `would_fail()` dry-run check alongside their real `cast()`/`use()`, so combat can fully confirm an action will succeed *before* any of the turn's other state (status effect ticks, spell cooldowns) is touched — a failed action never costs the player anything

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
* `toggle auto map` - list the exits automatically every time you enter a room
* `uncleared` - list the rooms you've visited that aren't cleared yet (enemies, items left behind, an unfinished trade, or a hidden passage worth a closer look), plus reachable rooms you haven't discovered yet
* `talk` - talk to an ally or companion in the room
* `toggle auto talk` - allies speak automatically on room entry, without needing `talk` each time
* `attack` / `attack light` / `attack heavy` / `attack ranged` - attack an enemy in the room; this locks you into combat until every enemy is defeated or you flee. Heavy hits harder but can miss entirely; ranged requires an equipped ranged weapon
* `target <name>` - set your attack target, persisting across rounds; if two or more enemies share a name, add a number (e.g. `target harpies 2`)
* `cast <spell>` - cast a known spell (mid-combat only); costs mana and may set the spell on a one-turn cooldown
* `flee` - disengage from combat (mid-combat only)
* `take <item>` - pick up an item from the room (also works mid-combat, without using your turn)
* `take all` - pick up everything in the room at once (also works mid-combat, without using your turn)
* `use <item>` / `equip <item>` - use or equip an item from your inventory; `equip` only ever equips gear, so it can't accidentally drink a potion (mid-combat, a genuine heal is a free action that doesn't use your turn; anything else — an offensive item, a non-healing use — still uses your turn, and the enemy still acts)
* `unequip <item>` - unequip an item
* `drop <item>` - drop an item into the room (quest items can't be dropped)
* `take <item> from <ally>` - take an item from an ally's inventory
* `take all from <ally>` - take everything an ally is holding at once
* `trade` - trade required items with an ally for their reward
* `recruit <name>` - recruit a companion who joins your team in combat (requires specific items)
* `challenge <name>` - duel a companion who won't join until you've beaten them; losing isn't a death, and your HP is restored afterwards
* `dismiss` - release your current companion, who returns home
* `repair <item>` - repair an item to full durability at a Forge (requires gold)
* `dummy set <stat> <value>` - customise the practice dummy's stats (Practice Chamber only)
* `rest` / `wait` - recover mana outside of combat
* `save` / `save <profile> <slot>` - save your progress outside of combat; bare `save` targets your active slot, `save <profile> <slot>` targets a specific one (confirms first if it's already occupied)
* `load <profile> <slot>` - load a different save outside of combat; always confirms, since it discards any unsaved progress
* `skills` - view your skill tree progress and available points (also available mid-combat)
* `learn <path>` - spend a skill point on the next skill in a path (`attack`, `defence`, or `abilities`) (also available mid-combat)
* `inventory` - display carried items, with equipped gear, quest items, and gold marked separately (also available mid-combat)
* `stats` - display your core stats (including Intellect), ancestry, level, and experience (also available mid-combat)
* `controls` - show the full list of available commands (always available, regardless of state)
* `quit` / `exit` - quit the game

## Project structure
* `characters.py` - `Character`, `Player`, `Enemy`, `Ally`, `Companion`, `Skill`, `SkillPath`, `SkillTree`
* `items.py` - `Item`, `Weapon`, `Armour`, `Consumable`, `QuestItem`, `Inventory`, plus `Consumable`'s own subclasses `Reviver`, `StatusEffectItem`, `SpellBook`, `SkillPointReward`
* `status_effects.py` - `StatusEffect` - the poison/flame/heal-over-time engine, ticked once per combat turn
* `spells.py` - `Spell` - offensive/defensive/utility spellcasting
* `hints.py` - the text of every one-off contextual hint, and the logic that shows each one only once per save
* `world.py` - `Room`, `Map`
* `content/` - the actual game content: specific rooms, enemies, allies, and items, one module per floor, plus the ancestry options for character creation, dev-only test content, and `build_world()`
* `combat.py` - combat resolution: team-vs-team turns, targeting, status-effect ticking, spellcasting, defeat handling, and fleeing
* `exploration.py` - everything outside combat: picking up items, trading, recruiting/dismissing companions, repairing armour, examining, and the map
* `character_creation.py` - ancestry selection and building the player character, plus the title screen and every save/load prompt
* `save_system.py` - the save/load system: profile and slot management, JSON persistence for player state and a full per-room snapshot of the world
* `dev_tools.py` - the developer command set (not part of the standard game)
* `engine.py` - the game loop and top-level command routing

## Roadmap
The current release covers character creation with primary and secondary ancestries, a training prologue, the foundational systems (combat, inventory, trading, allies, skill tree), companions, armour with durability and repair, status effects, spellcasting, attack variety (light/heavy/ranged), a practice chamber for testing loadouts risk-free, weapon classes and armour weight, a full save/load system with profiles/slots and autosave, multi-stage boss fight mechanics (phase transitions and wave-gated adds) with Medusa as the first named boss built on them, floors 0–4 fully populated, from Chiron's training grounds down to Medusa's lair, and the first of floor 5 - the Shade of Achilles, the first companion you can recruit, once you've beaten him in a duel, and the Shade of Hector. Planned additions include further floors drawing on the Iliad and Odyssey, with more named multi-stage bosses among them.

## License
MIT - https://github.com/fordyyyx/python-dungeon-crawler-project/blob/main/LICENSE
