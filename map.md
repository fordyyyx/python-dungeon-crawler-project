Chamber of Chiron {Chiron - Friendly}
* north -> Chamber of Chiron (North)
* east -> Chamber of Chiron (East) [NOTE: locked - needs the Wooden Sword; unlocks for good once walked through, see CLAUDE.md's "Locked exits open for good"]
* south -> Chamber of Chiron (South) [NOTE: locked - needs the Wooden Shield; same permanent unlock]
* west -> Chamber of Chiron (West) [NOTE: locked - needs the Dummy Head; same permanent unlock]
* descend -> Cave Entrance [NOTE: locked - needs Charon's Coin, Chiron's trade reward; one-way by design]
Chamber of Chiron (North)
* south -> Chamber of Chiron
Chamber of Chiron (East)
* west -> Chamber of Chiron
Chamber of Chiron (South) {Training Dummy - Enemy}
* north -> Chamber of Chiron
Chamber of Chiron (West) {Mentor - Friendly}
* east -> Chamber of Chiron

Cave Entrance {Wounded Soldier - Friendly}
* descend -> Styx Crossing

Styx Crossing {Charon - Friendly}
* east -> Fields of Asphodel
* down -> Sunken Vault
* descend -> Library of Athena
* ascend -> Cave Entrance
Fields of Asphodel {Shade - Enemy}
* west -> Styx Crossing
Sunken Vault {Skeleton Warrior - Enemy}
* up -> Styx Crossing

Library of Athena {Athena - Friendly}
* west -> Armoury of Ares
* south -> Hall of Hermes
* ascend -> Styx Crossing
Armoury of Ares {Ares - Friendly}
* east -> Library of Athena
* south -> Trophy Room of Zeus [NOTE: hidden exit in actual code, add_hidden_exit(), required_intellect=3 — this plain-text notation has no way to mark that]
Trophy Room of Zeus {Zeus - Friendly}
* north -> Armoury of Ares
Hall of Hermes {Hermes - Friendly}
* north -> Library of Athena
* south -> Forge of Prometheus
Forge of Prometheus {Prometheus - Friendly}
* north -> Hall of Hermes
* east -> Practice Chamber
* descend -> Bony Crypt
* prayer room -> Prayer Room [NOTE: reciprocal fast-travel shortcut, locked (Room.fast_travel_locks) until 'forge' is used from Prayer Room first, see CLAUDE.md's "Fast-travel locks"]
* stony lair -> Stony Lair [NOTE: same fast-travel-lock mechanism as above, keyed to Stony Lair's own 'forge' exit]
* maze of pillars -> Maze of Pillars [NOTE: same fast-travel-lock mechanism as above, keyed to Maze of Pillars' own 'forge' exit]
Practice Chamber {Practice Enemy - Enemy} [NOTE: is_practice_chamber=True; the enemy has respawns=True and resets on defeat instead of being removed]
* west -> Forge of Prometheus

Bony Crypt {Crypt Keeper - Enemy}
* ascend -> Forge of Prometheus
* south -> Cave of Harpies
Cave of Harpies {Harpy - Enemy}
* north -> Bony Crypt
* east -> Prayer Room
* south -> Dim Corridor
Prayer Room {Fanatic - Enemy}
* west -> Cave of Harpies
* forge -> Forge of Prometheus [NOTE: one-way shortcut, no lock]
Dim Corridor {Lurker - Enemy}
* north -> Cave of Harpies
* south -> Overgrown Forest
Overgrown Forest {Centaur - Enemy}
* north -> Dim Corridor
* descend -> Labyrinth of the Minotaur [NOTE: guarded (Room.guarded_exits) - blocked while the Centaur lives, see CLAUDE.md's "Guarded exits"]

Labyrinth of the Minotaur {Minotaur - Enemy}
* ascend -> Overgrown Forest
* east -> Cavern of the Cyclops
* west -> Stony Lair
* south -> Mossy Grove [NOTE: guarded - blocked while the Minotaur lives; west/east/ascend stay open]
Cavern of the Cyclops {Cyclops - Enemy}
* west -> Labyrinth of the Minotaur
Stony Lair {Petrified Guardian - Enemy}
* east -> Labyrinth of the Minotaur
* forge -> Forge of Prometheus [NOTE: one-way shortcut, no lock]
Mossy Grove {Satyr - Enemy}
* north -> Labyrinth of the Minotaur
* west -> Shadowy Corner
* south -> Sandy Expanse
Shadowy Corner {Lamia - Enemy}
* east -> Mossy Grove
Sandy Expanse {Ember Wraith - Enemy}
* north -> Mossy Grove
* east -> Maze of Pillars
Maze of Pillars {Talos - Enemy}
* west -> Sandy Expanse
* south -> Lair of Medusa [NOTE: guarded - blocked while Talos lives]
* forge -> Forge of Prometheus [NOTE: one-way shortcut, no lock]
Lair of Medusa {Medusa - Enemy}
* north -> Maze of Pillars
* descend -> Shadow of Army Camp [NOTE: guarded - blocked until the whole Medusa chain (Phase 1, both Gorgons, Awakened) is defeated]

Shadow of Army Camp {Shade of Achilles - Companion} [NOTE: built - recruitable after beating him in a duel ('challenge shade of achilles'); the only built content on floors 5-9 so far]
* ascend -> Lair of Medusa
* south -> Shadow of Troy (North)
Shadow of Troy (North) {Shade of Hector - Enemy} [NOTE: built - 32 HP / 9 ATK / 5 armour, drops Hector's Helm; exit not guarded]
* north -> Shadow of Army Camp
* south -> Shadow of Troy (Central)
Shadow of Troy (Central) {Shade of Ajax - Enemy}
* north -> Shadow of Troy (North)
* west -> Shadow of Troy (Alleyway)
Shadow of Troy (Alleyway) {Myrmidon Soldier - Enemy}
* east -> Shadow of Troy (Central)
* south -> Shadow of Troy (South)
Shadow of Troy (South) {Shade of Paris - Enemy}
* north -> Shadow of Troy (Alleyway)
* east -> Shadow of Pylos
Shadow of Pylos {Nestor - Friendly}
* west -> Shadow of Troy (South)
* descend -> Bright Cave

Bright Cave {Laestrygonian - Enemy}
* ascend -> Shadow of Pylos
* south -> Calm Waters
Calm Waters {Sirens - Enemy}
* north -> Bright Cave
* east -> Cavern of Polyphemus
* west -> Rocky Shore
Cavern of Polyphemus {Polyphemus - Enemy}
* west -> Calm Waters
Rocky Shore {Scylla - Enemy}
* east -> Calm Waters
* south -> Narrow River
Narrow River {Charybdis - Enemy}
* north -> Rocky Shore
* south -> Poseidon's Depths
Poseidon's Depths {Poseidon - Enemy}
* north -> Narrow River
* east -> Shadow of Ithaca
Shadow of Ithaca {Odysseus - Friendly}
* west -> Poseidon's Depths
* east -> Muddy Pigsty
* south -> Throne Room of Odysseus
Muddy Pigsty {Circe - Friendly}
* west -> Shadow of Ithaca
Throne Room of Odysseus {Suitors of Ithaca - Enemy}
* north -> Shadow of Ithaca
* west -> Bedchamber of Odysseus
Bedchamber of Odysseus {Penelope - Friendly}
* east -> Throne Room of Odysseus
* descend -> Chamber of the Oracle

Chamber of the Oracle {Oracle of Delphi - Friendly}
* ascend -> Bedchamber of Odysseus
* south -> Shadow of Thebes
Shadow of Thebes {Tiresias - Friendly}
* north -> Chamber of the Oracle
* south -> Bedchamber of Persephone
Bedchamber of Persephone {Persephone - Friendly}
* north -> Shadow of Thebes
* descend -> Gate of Cerberus

Gate of Cerberus {Cerberus - Enemy}
* ascend -> Bedchamber of Persephone
* south -> Hall of Hades
Hall of Hades {Hades - Enemy}
* north -> Gate of Cerberus
* descend -> Tartarus

Tartarus {Typhon - Enemy}
* ascend -> Hall of Hades

---
FLOOR ASSIGNMENTS (confirmed):
Floor 0 (Chiron's Training Grounds): Chamber of Chiron + 4 variants
Floor 1 (The Underworld Gateway): Cave Entrance, Styx Crossing, Fields of Asphodel, Sunken Vault
Floor 2 (Domains of the Gods): Library of Athena, Armoury of Ares, Trophy Room of Zeus, Hall of Hermes, Forge of Prometheus, Practice Chamber
Floor 3 (Low Dungeon): Bony Crypt, Cave of Harpies, Prayer Room, Dim Corridor, Overgrown Forest
Floor 4 (Labyrinth and Greater Monsters): Labyrinth of the Minotaur, Stony Lair, Cavern of the Cyclops, Mossy Grove, Shadowy Corner, Sandy Expanse, Maze of Pillars, Lair of Medusa
Floor 5 (Shadow of Troy): Shadow of Army Camp, Shadow of Troy (North/Central/Alleyway/South), Shadow of Pylos
Floor 6 (Odyssey and the Open Sea): Bright Cave, Calm Waters, Cavern of Polyphemus, Rocky Shore, Narrow River, Poseidon's Depths, Shadow of Ithaca, Muddy Pigsty, Throne Room of Odysseus, Bedchamber of Odysseus
Floor 7 (Prophecy and the Elder Dead): Chamber of the Oracle, Shadow of Thebes, Bedchamber of Persephone
Floor 8 (The Final Descent): Gate of Cerberus, Hall of Hades
Floor 9 (Tartarus): Tartarus

STATUS: Full shell built and playtested (all rooms reachable, correctly connected).
Population (enemies/allies/items/trades) is COMPLETE for Floor 0 and Floor 1
(Wounded Soldier, Charon, a Skeleton Warrior that also drops the Skeleton
Bone needed for Hermes' trade below, and a Shade in Fields of Asphodel
dropping the Weathered Helm - the game's first real `slot="helmet"` item).
Floor 2's four god rooms (Library of Athena, Armoury of
Ares, Hall of Hermes, Forge of Prometheus) now hold their allies - the
Athena/Ares/Hermes/Prometheus `create_*()` calls are wired into
`build_floor_2()`. Three of the four gods' trades are now genuinely
completable through normal play: Hermes' required Skeleton Bone drops in
Sunken Vault (floor 1); Athena's required Centaur's Broken Bow now drops
from the new Centaur enemy in Overgrown Forest (floor 3); Ares' required
Cyclops' Eye now drops from the new Cyclops enemy in Cavern of the Cyclops
(floor 4). All four gods now have real dialogue (Athena delivers the story
premise, and Athena's, Ares' and Hermes' hints each point at their trade
item's source). Only
Prometheus' trade remains incomplete - he has no required items *or* reward,
so `trade` just replies that he has nothing to trade and never completes;
that's unwritten content, not a placement gap. Trophy Room of Zeus remains
fully unpopulated - no Zeus content (ally or otherwise) has been written
yet. The sixth floor-2 room, Practice Chamber, is real, populated content
(a respawning practice dummy, `create_practice_dummy()`), same as before.

Floors 3 and 4 have each gained their first real enemy content, placed as
part of wiring up Athena's and Ares' trade items: the Minotaur is now in
its own Labyrinth of the Minotaur (floor 4), alongside the new Centaur
(Overgrown Forest, floor 3) and Cyclops (Cavern of the Cyclops, floor 4).
Floor 3 is now fully populated with enemies: Bony Crypt holds a Crypt Keeper
(drops the Vial of Grave Rot, the game's first real StatusEffectItem, an
offensive poison), Cave of Harpies a Harpy (drops the Harpy-fletched Bow, the
first real ranged weapon), Prayer Room a Fanatic (drops the Tome of Old
Prayers, the first real SpellBook, teaching Prayer Bolt), Dim Corridor a
Lurker (drops a Small Healing Potion), and Overgrown Forest the Centaur.

Floor 4 is now fully populated with enemies too: Stony Lair holds a
Petrified Guardian (drops the Chipped Stone Aegis, a heavy shield), Mossy Grove a Satyr
(drops the Wineskin of Dionysus, the game's first real heal-over-time
StatusEffectItem), Shadowy Corner a Lamia (the game's first enemy with
Character.has_lifesteal, drops Lamia's Fang, a piercing lifesteal weapon), Sandy Expanse an Ember Wraith
(drops the Sun-scorched Dagger), Maze of Pillars a Talos (drops Talos'
Bronze Plating, the best body armour in the game so far), and Lair of
Medusa the floor's climactic fight: Medusa (Phase 1) falls to a wave of two
Gorgons, then Medusa (Awakened) - the game's first real, named multi-stage
boss, see `CLAUDE.md`'s "Multi-stage boss fights" - who drops Serpent's
Kiss, a poisoned blade. Alongside the Minotaur and Cyclops, that's every room on floor 4
holding a real enemy now. The Minotaur drops the Labrys (a 7-damage, two-handed
heavy axe with cleave), replacing the Bronze Xiphos he used to share with the Wounded Soldier.

Four critical-path exits are now guarded (`Room.guarded_exits`) and can't be
used while their room's enemy lives: Overgrown Forest's `descend` (Centaur),
Labyrinth of the Minotaur's `south` (Minotaur), Maze of Pillars' `south`
(Talos), and Lair of Medusa's `descend` (the whole Medusa chain). Every other
fight on floors 0-4 is still optional to walk past.

Floor 5 has its first real content: the Shade of Achilles, a recruitable
Companion in Shadow of Army Camp, who must be beaten in a duel first, and
the Shade of Hector in Shadow of Troy (North), an armour-5 enemy who drops
Hector's Helm. Every other room on floors 5-9 remains an unpopulated shell - the per-room
enemies/allies listed above for those floors are the planned design, not
built content. Finishing Floor 2's population (Prometheus' trade and Trophy
Room of Zeus) and the rest of floors 5-9's population are all deferred to the "Populate all floors" roadmap item.