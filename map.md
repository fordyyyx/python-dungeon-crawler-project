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

Styx Crossing {Charon - Friendly} [NOTE: built - the ferryman's shop: 'offers' / 'exchange <number>' for healing and plain gear that unlocks by the deepest floor reached, and 'sell <item>' - he buys anything with a value at half price]
* east -> Fields of Asphodel
* down -> Sunken Vault
* descend -> Library of Athena
* ascend -> Cave Entrance
Fields of Asphodel {Shade - Enemy}
* west -> Styx Crossing
* south -> Banks of the Lethe [NOTE: hidden exit, revealed by 'examine' - the examine text hints at a river to the south]
Banks of the Lethe {the river - room interaction} [NOTE: built - no enemy; 'drink' (the price, changes nothing) / 'drink deeply' (forget every skill, every point refunded, for 25 gold per floor of the deepest floor reached)]
* north -> Fields of Asphodel
Sunken Vault {Skeleton Warrior - Enemy} [NOTE: chest - 'open chest' once the room is clear: fixed, two Small Healing Potions and 15 gold]
* up -> Styx Crossing

Library of Athena {Athena - Friendly}
* west -> Armoury of Ares
* south -> Hall of Hermes
* ascend -> Styx Crossing
Armoury of Ares {Ares - Friendly}
* east -> Library of Athena
* north -> Trophy Room of Zeus [NOTE: hidden exit in actual code, add_hidden_exit(), required_intellect=3 — this plain-text notation has no way to mark that]
Trophy Room of Zeus {Zeus - Companion} [NOTE: built - is_trophy_room=True: thirteen plinths, 'place <trophy>' / 'place all'; rewards at 5 (+5 max HP), 10 (a skill point) and 13 trophies; a chest that opens only when every plinth is filled (the Thunderbolt of Zeus, two Vials of Ambrosia); Zeus joins as a companion once the room is complete]
* south -> Armoury of Ares
Hall of Hermes {Hermes - Friendly}
* north -> Library of Athena
* south -> Forge of Prometheus
Forge of Prometheus {Prometheus - Friendly} [NOTE: built - a one-time hardcore offer (permadeath, for a full armour repair); no trade]
* north -> Hall of Hermes
* east -> Practice Chamber
* descend -> Bony Crypt
* prayer room -> Prayer Room [NOTE: reciprocal fast-travel shortcut, locked (Room.fast_travel_locks) until 'forge' is used from Prayer Room first, see CLAUDE.md's "Fast-travel locks"]
* stony lair -> Stony Lair [NOTE: same fast-travel-lock mechanism as above, keyed to Stony Lair's own 'forge' exit]
* maze of pillars -> Maze of Pillars [NOTE: same fast-travel-lock mechanism as above, keyed to Maze of Pillars' own 'forge' exit]
* shadow of pylos -> Shadow of Pylos [NOTE: same fast-travel-lock mechanism, keyed to Shadow of Pylos' own 'forge' exit]
* shadow of ithaca -> Shadow of Ithaca [NOTE: same fast-travel-lock mechanism, keyed to Shadow of Ithaca's own 'forge' exit]
* bedchamber of persephone -> Bedchamber of Persephone [NOTE: same fast-travel-lock mechanism, keyed to the Bedchamber's own 'forge' exit]
* gate of cerberus -> Gate of Cerberus [NOTE: same fast-travel-lock mechanism, keyed to the Gate's own 'forge' exit]
* tartarus -> Tartarus [NOTE: same fast-travel-lock mechanism, keyed to Tartarus' own 'forge' exit - and not listed at all until 'hades_defeated', since Tartarus is concealed]
Practice Chamber {Practice Enemy - Enemy} [NOTE: is_practice_chamber=True; the enemy has respawns=True and resets on defeat instead of being removed]
* west -> Forge of Prometheus

Bony Crypt {Crypt Keeper - Enemy}
* ascend -> Forge of Prometheus
* south -> Cave of Harpies
* down -> Ossuary [NOTE: hidden exit, revealed by 'examine']
Ossuary [NOTE: built - no enemy or ally; the Ledger of the Unjudged (+2 intellect, an IntellectReward) on the lectern]
* up -> Bony Crypt
Cave of Harpies {Harpy - Enemy} [NOTE: chest - 'open chest' once the room is clear: random, early loot table]
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
Stony Lair {Petrified Guardian - Enemy} [NOTE: chest - 'open chest' once the room is clear: random, middle loot table]
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
* east -> Daedalus' Workshop [NOTE: hidden exit, revealed by 'examine', required_intellect=5]
Daedalus' Workshop [NOTE: built - no enemy or ally; is_workshop=True, so 'upgrade' works here (weapons and armour, up to +5, limited by intellect); the Clockwork Crossbow (ranged, 5, pierce 1) and Daedalus' Notes (+1 intellect)]
* west -> Maze of Pillars
* up -> Icarus' Shaft
Icarus' Shaft {Icarus - Friendly} [NOTE: built - lore, no trade; gives away the Feather of Icarus, a one-use guaranteed escape (EscapeItem)]
* down -> Daedalus' Workshop
Lair of Medusa {Medusa - Enemy}
* north -> Maze of Pillars
* descend -> Shadow of Army Camp [NOTE: guarded - blocked until the whole Medusa chain (Phase 1, both Gorgons, Awakened) is defeated]

Shadow of Army Camp {Shade of Achilles - Companion} [NOTE: built - recruitable after beating him in a duel ('challenge shade of achilles')]
* ascend -> Lair of Medusa
* south -> Shadow of Troy (North)
* in -> Belly of the Wooden Horse [NOTE: hidden exit, revealed by 'examine' - the examine text points at the horse]
Belly of the Wooden Horse [NOTE: built - no enemy or ally; the Spear of Pelion (piercing, 8, pierce 2)]
* out -> Shadow of Army Camp
Shadow of Troy (North) {Shade of Hector - Enemy} [NOTE: built - 39 HP / 11 ATK / 5 armour / pierce 3, drops Hector's Helm; guards 'south']
* north -> Shadow of Army Camp
* south -> Shadow of Troy (Central)
Shadow of Troy (Central) {Shade of Ajax - Enemy} [NOTE: built - 56 HP / 13 ATK / 1 armour / pierce 3, drops the Tower Shield of Ajax; guards 'west'] [NOTE: chest - 'open chest' once the room is clear: random, middle loot table]
* north -> Shadow of Troy (North)
* west -> Shadow of Troy (Alleyway)
Shadow of Troy (Alleyway) {Myrmidon Soldier ×2 - Enemy} [NOTE: built - a pair, 10 ATK / pierce 3, each dropping a Field Dressing; 'south' deliberately unguarded - skipping them costs the dressings]
* east -> Shadow of Troy (Central)
* south -> Shadow of Troy (South)
Shadow of Troy (South) {Shade of Paris - Enemy} [NOTE: built - evasive archer: 50% melee dodge, natural 9 armour pierce; drops the Bow of Paris; guards 'east']
* north -> Shadow of Troy (Alleyway)
* east -> Shadow of Pylos
Shadow of Pylos {Nestor - Friendly} [NOTE: built - advice, no trade; gives away a Cup of Kykeon]
* west -> Shadow of Troy (South)
* descend -> Bright Cave
* forge -> Forge of Prometheus [NOTE: one-way shortcut, no lock]

Bright Cave {Antiphates, Laestrygonian - Enemy} [NOTE: built - two boulder-throwing giants with pierce 2; Antiphates drops his Club (heavy, 8), the Laestrygonian the Laestrygonian Hide (medium, 5 DEF); exit not guarded] [NOTE: chest - 'open chest' once the room is clear: random, late loot table]
* ascend -> Shadow of Pylos
* south -> Calm Waters
Calm Waters {Sirens - room interaction} [NOTE: built - no enemy; 'listen' / 'give in' / 'resist', the Sirens' bargain: +2 skill points for -5 max HP, permanently. Also the fork - west (Scylla) and south (Charybdis) are two parallel routes to Poseidon's Depths; only one has to be passed, as Nestor's advice says]
* north -> Bright Cave
* east -> Cavern of Polyphemus
* west -> Rocky Shore
* south -> Narrow River
Cavern of Polyphemus {Polyphemus - Enemy} [NOTE: built - optional two-phase fight; Polyphemus (Blinded) starts at a 35% miss chance and drops the Olive-wood Stake; two Wheels of Cheese on the floor]
* west -> Calm Waters
Rocky Shore {Head of Scylla ×6 - Enemy} [NOTE: built - six weak heads, each striking blindly (30% miss), guarding 'south'; the Boar's-Tusk Helm lies on the rocks]
* east -> Calm Waters
* south -> Poseidon's Depths
Narrow River {Charybdis - Enemy (invulnerable)} [NOTE: built - a puzzle, not a fight: 'watch' / 'climb' / 'let go' / 'row' against the whirlpool's cycle; a mistake costs 12 HP. Guards 'west' until solved; drops the Hoplon of the Drowned]
* north -> Calm Waters
* west -> Poseidon's Depths
Poseidon's Depths {Poseidon - Enemy} [NOTE: built - floor 6's boss: Poseidon, then two Hippocampi (Kelp Poultices), then Poseidon (Earth-Shaker), who drops the Trident of the Depths; guards 'south'. Both routes rejoin here, so the other monster stays reachable afterwards]
* north -> Rocky Shore
* east -> Narrow River
* south -> Shadow of Ithaca
Shadow of Ithaca {Odysseus - Companion} [NOTE: built - a ranged companion who gives advice; joins once the Suitors are cleared ('suitors_cleared')]
* north -> Poseidon's Depths
* east -> Muddy Pigsty
* south -> Throne Room of Odysseus
* forge -> Forge of Prometheus [NOTE: one-way shortcut, no lock]
* west -> Cave of the Nymphs [NOTE: hidden exit, revealed by 'examine', required_intellect=6]
Cave of the Nymphs {the Phaeacians' gifts - room interaction} [NOTE: built - no enemy or ally; 'gather the gifts' gives 200 gold once (saved in Room.flags); Nymphs' Honey (25 HP heal) on the floor; Odysseus has an advice line for it]
* east -> Shadow of Ithaca
Muddy Pigsty {Circe - Friendly} [NOTE: built - six exchanges ('offers' / 'exchange <number>'): outgrown gear into Kelp Poultices and Cups of Kykeon for no gold, and weak consumables into the same for 5-10]
* west -> Shadow of Ithaca
Throne Room of Odysseus {Antinous, Eurymachus, Suitor x2 - Enemy} [NOTE: built - the floor's last fight; guards 'west'; clearing it sets 'suitors_cleared', which lets Odysseus join] [NOTE: chest - 'open chest' once the room is clear: fixed, a Cup of Kykeon, a Kelp Poultice and 40 gold]
* north -> Shadow of Ithaca
* west -> Bedchamber of Odysseus
Bedchamber of Odysseus {Penelope - Friendly} [NOTE: built - no trade; gives away Penelope's Thread, the first LoyaltyToken; has lines for Odysseus and Achilles]
* east -> Throne Room of Odysseus
* descend -> Chamber of the Oracle

Chamber of the Oracle {Oracle of Delphi - Friendly} [NOTE: built - the twist prophecy once, then three prophecies: 'ask ahead' (the next floor's traits) / 'ask secrets' (a hidden exit on a floor already reached)]
* ascend -> Bedchamber of Odysseus
* south -> Shadow of Thebes
Shadow of Thebes {Tiresias - Friendly} [NOTE: built - free, unlimited readings of what the player isn't ready for on the floor below]
* north -> Chamber of the Oracle
* south -> Bedchamber of Persephone
Bedchamber of Persephone {Persephone - Friendly} [NOTE: built - the first branching dialogue ('say <number>'); gives a Pomegranate (full heal) once, and asks the player to spare Hades - 'promised_mercy' or 'refused_mercy'; 'promised_mercy' makes Hades yield on floor 8]
* north -> Shadow of Thebes
* descend -> Gate of Cerberus [NOTE: story-gated - shut until the player answers Persephone either way]
* forge -> Forge of Prometheus [NOTE: one-way shortcut, no lock]

Gate of Cerberus {Cerberus - Enemy} [NOTE: built - three phases (Cerberus, Two Heads, Last Head); the last head poisons, fully restores the player on defeat and drops the Hide of Cerberus; guards 'south']
* ascend -> Bedchamber of Persephone
* south -> Hall of Hades
* forge -> Forge of Prometheus [NOTE: one-way shortcut, no lock]
Hall of Hades {Hades - Enemy} [NOTE: built - Hades, three Restless Shades (Vials of Ambrosia), then Hades (Helm of Darkness), who drops the Bident of Hades; with 'promised_mercy' he yields and stays as a recruitable companion. Clearing the Hall sets 'hades_defeated' and shows the ending]
* north -> Gate of Cerberus
* descend -> Tartarus [NOTE: concealed until 'hades_defeated', and guarded by the Hades chain]

Tartarus {Typhon - Enemy} [NOTE: built - concealed until 'hades_defeated'. Typhon, four Serpents of Typhon (poison, Vials of Ambrosia), then Typhon (Storm Unleashed), who blinds and drops the Heart of Typhon (a Trophy). Clearing it sets 'typhon_defeated' and shows the true ending]
* ascend -> Hall of Hades
* forge -> Forge of Prometheus [NOTE: one-way shortcut, no lock]

---
FLOOR ASSIGNMENTS (confirmed):
Floor 0 (Chiron's Training Grounds): Chamber of Chiron + 4 variants
Floor 1 (The Underworld Gateway): Cave Entrance, Styx Crossing, Fields of Asphodel, Banks of the Lethe, Sunken Vault
Floor 2 (Domains of the Gods): Library of Athena, Armoury of Ares, Trophy Room of Zeus, Hall of Hermes, Forge of Prometheus, Practice Chamber
Floor 3 (Low Dungeon): Bony Crypt, Ossuary, Cave of Harpies, Prayer Room, Dim Corridor, Overgrown Forest
Floor 4 (Labyrinth and Greater Monsters): Labyrinth of the Minotaur, Stony Lair, Cavern of the Cyclops, Mossy Grove, Shadowy Corner, Sandy Expanse, Maze of Pillars, Daedalus' Workshop, Icarus' Shaft, Lair of Medusa
Floor 5 (Shadow of Troy): Shadow of Army Camp, Belly of the Wooden Horse, Shadow of Troy (North/Central/Alleyway/South), Shadow of Pylos
Floor 6 (Odyssey and the Open Sea): Bright Cave, Calm Waters, Cavern of Polyphemus, Rocky Shore, Narrow River, Poseidon's Depths, Shadow of Ithaca, Cave of the Nymphs, Muddy Pigsty, Throne Room of Odysseus, Bedchamber of Odysseus
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
item's source). Prometheus has
no trade (`trade` replies that he has nothing to trade) - his role is the
one-time hardcore offer instead. Trophy Room of Zeus is built
too (see the end of this section). The sixth floor-2 room, Practice Chamber, is real, populated content
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

Floor 5 is fully populated: the Shade of Achilles (a recruitable Companion,
duel first) in Shadow of Army Camp, then one encounter per room down the
Shadow of Troy - Hector, Ajax, a pair of Myrmidons, and Paris - with Nestor
in Shadow of Pylos before the descent. Hector, Ajax and Paris guard the way on;
the Myrmidons' exit is deliberately left open.
Floor 6's layout was reworked so Scylla (Rocky Shore) and Charybdis (Narrow
River) are two parallel branches off Calm Waters, both leading to Poseidon's
Depths, rather than one corridor through both - the player picks one, and the
Depths link back to the other. Nestor's dialogue on floor 5 now describes
this choice.
Floor 6 is fully populated: Antiphates and a Laestrygonian in Bright
Cave, the Sirens' bargain in Calm Waters (a room interaction, not an enemy),
Polyphemus in his cavern, six Heads of Scylla guarding Rocky Shore's
'south', Charybdis' puzzle guarding Narrow River's 'west', Poseidon's chain
guarding the Depths' 'south', Odysseus (a companion) in Shadow of Ithaca, and
Circe (the first merchant) in the Muddy Pigsty, the Suitors guarding the Throne
Room's 'west', and Penelope in the Bedchamber. Shadow of Pylos and Shadow of Ithaca have 'forge' shortcuts, as do
Persephone's Bedchamber, the Gate of Cerberus and Tartarus - so the Forge has
eight reciprocal exits.
Floor 7 is populated, with no enemies: the Oracle in the Chamber of the Oracle,
Tiresias in Shadow of Thebes, and Persephone in her Bedchamber, whose 'descend'
stays shut until the player answers her request (a story gate).
Floor 8 is populated: Cerberus in the Gate of Cerberus, guarding 'south', and
Hades' chain in the Hall of Hades - the story's end.
Floor 9 is populated: Tartarus, concealed until the 'hades_defeated' story
flag (which clearing the Hall sets), holds Typhon - the post-game and the true
ending. Every floor now has its content (roadmap.md's "Populate all floors" is
complete), and Floor 2's Trophy Room of Zeus has been built since.
Optional hidden rooms, each revealed by 'examine' and each with a plain way back:
the Banks of the Lethe (floor 1, forgetting skills), the Ossuary (floor 3, the
Ledger of the Unjudged), Daedalus' Workshop and Icarus' Shaft (floor 4, intellect
5 - the Clockwork Crossbow, Daedalus' Notes, and Icarus with the Feather of
Icarus), the Belly of the Wooden Horse (floor 5, the Spear of Pelion) and the Cave
of the Nymphs (floor 6, intellect 6 - Nymphs' Honey and 200 gold) - alongside the
older Sunken Vault (floor 1) and Trophy Room of Zeus (floor 2, intellect 3).
Charon (Styx Crossing, floor 1) is a shop now: he sells eight items - potions and
dressings, a Kelp Poultice and Cup of Kykeon, the Bronze Buckler, Bronze Greataxe and
Hoplite Sword, and the Obol of Return (the first real Reviver) - unlocking between
floors 0 and 6, and buys anything sellable. Every forge shortcut is three rooms from him.
Six rooms hold a chest, opened with 'open chest' once the room is clear: Sunken Vault
(floor 1) and the Throne Room of Odysseus (floor 6) have fixed contents; Cave of Harpies
(floor 3), Stony Lair (floor 4), Shadow of Troy (Central) (floor 5) and Bright Cave
(floor 6) roll theirs from a loot table, once per playthrough. A seventh, in the Trophy
Room, opens only when every trophy is placed.
The Trophy Room of Zeus (floor 2, hidden north of the Armoury, intellect 3) holds Zeus
and thirteen plinths. Eight trophies are boss drops - Horn of the Minotaur, Bronze Nail
of Talos, Head of Medusa (floor 4), Fleece of the Ram (Polyphemus), Conch of Poseidon
(floor 6), Collar of Cerberus, Helm of Darkness (floor 8) and Heart of Typhon (floor 9) -
and five lie in hidden rooms: Phial of the Lethe (Banks of the Lethe), Keeper's Lantern
(Ossuary), Daedalus' Compass (Workshop), Bridle of the Wooden Horse (Belly of the Wooden
Horse) and Phaeacian Tripod (Cave of the Nymphs).
Daedalus' Workshop (floor 4, hidden) is where gear is upgraded: 'upgrade' lists what
can be improved, 'upgrade <item>' adds +1 damage or defence for gold, up to +5.