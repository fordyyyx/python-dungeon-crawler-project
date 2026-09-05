from dungeon_crawler.items import Item, Weapon, Armour, Consumable, Reviver, StatusEffectItem, SpellBook, QuestItem, Inventory, SkillPointReward
from dungeon_crawler.characters import Character, Player, Enemy, Companion
from dungeon_crawler.spells import Spell
from dungeon_crawler.world import Room

def test_item_initialises_as_unequipped():
    sword = Weapon(name="Iron Sword", description="", damage=5)
    assert sword.equipped is False

def test_weapon_use_returns_equip_message():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    sword = Weapon(name="Iron Sword", description="", damage=5)
    message = sword.use(hero)
    assert message == "Hero equips Iron Sword (melee, +5 DMG)."

def test_weapon_use_sets_equipped_flag():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    sword = Weapon(name="Iron Sword", description="", damage=5)
    sword.use(hero)
    assert sword.equipped is True

def test_weapon_use_does_not_change_attack_damage():
    """Weapon damage is read directly off the equipped slot during Character.attack(), never added into
    attack_damage itself - see Weapon's class docstring."""
    hero = Character(name="Hero", hp=100, attack_damage=10)
    sword = Weapon(name="Iron Sword", description="", damage=5)
    sword.use(hero)
    assert hero.attack_damage == 10

def test_weapon_use_when_already_equipped_returns_already_equipped_message():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    sword = Weapon(name="Iron Sword", description="", damage=5)
    sword.use(hero)
    message = sword.use(hero)
    assert message == "Iron Sword already equipped."

def test_weapon_unequip_when_not_equipped_returns_not_equipped_message():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    sword = Weapon(name="Iron Sword", description="", damage=5)
    message = sword.unequip(hero)
    assert message == "Iron Sword is not equipped."

def test_weapon_unequip_when_equipped_does_not_change_attack_damage():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    sword = Weapon(name="Iron Sword", description="", damage=5)
    sword.use(hero)
    sword.unequip(hero)
    assert hero.attack_damage == 10

def test_weapon_unequip_when_equipped_clears_equipped_flag():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    sword = Weapon(name="Iron Sword", description="", damage=5)
    sword.use(hero)
    sword.unequip(hero)
    assert sword.equipped is False

def test_weapon_unequip_when_equipped_returns_unequip_message():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    sword = Weapon(name="Iron Sword", description="", damage=5)
    sword.use(hero)
    message = sword.unequip(hero)
    assert message == "Hero unequips Iron Sword (-5 DMG)"

def test_weapon_defaults_to_melee_slot():
    sword = Weapon(name="Iron Sword", description="", damage=5)
    assert sword.slot == "melee"

def test_weapon_use_sets_character_equipped_melee_weapon_by_default():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    sword = Weapon(name="Iron Sword", description="", damage=5)
    sword.use(hero)
    assert hero.equipped_melee_weapon is sword

def test_weapon_use_with_ranged_slot_sets_character_equipped_ranged_weapon():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    bow = Weapon(name="Short Bow", description="", damage=4, slot="ranged")
    bow.use(hero)
    assert hero.equipped_ranged_weapon is bow

def test_weapon_use_with_ranged_slot_returns_equip_message():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    bow = Weapon(name="Short Bow", description="", damage=4, slot="ranged")
    message = bow.use(hero)
    assert message == "Hero equips Short Bow (ranged, +4 DMG)."

def test_weapon_unequip_clears_character_equipped_melee_weapon():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    sword = Weapon(name="Iron Sword", description="", damage=5)
    sword.use(hero)
    sword.unequip(hero)
    assert hero.equipped_melee_weapon is None

def test_weapon_unequip_clears_character_equipped_ranged_weapon():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    bow = Weapon(name="Short Bow", description="", damage=4, slot="ranged")
    bow.use(hero)
    bow.unequip(hero)
    assert hero.equipped_ranged_weapon is None

def test_weapon_use_replacing_same_slot_unequips_old_weapon():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    old_sword = Weapon(name="Iron Sword", description="", damage=5)
    new_sword = Weapon(name="Steel Sword", description="", damage=8)
    old_sword.use(hero)
    new_sword.use(hero)
    assert old_sword.equipped is False

def test_weapon_use_replacing_same_slot_updates_character_equipped_melee_weapon():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    old_sword = Weapon(name="Iron Sword", description="", damage=5)
    new_sword = Weapon(name="Steel Sword", description="", damage=8)
    old_sword.use(hero)
    new_sword.use(hero)
    assert hero.equipped_melee_weapon is new_sword

def test_weapon_use_replacing_same_slot_returns_combined_message():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    old_sword = Weapon(name="Iron Sword", description="", damage=5)
    new_sword = Weapon(name="Steel Sword", description="", damage=8)
    old_sword.use(hero)
    message = new_sword.use(hero)
    assert message == "Hero unequips Iron Sword (-5 DMG)\nHero equips Steel Sword (melee, +8 DMG)."

def test_weapon_use_melee_and_ranged_can_be_equipped_simultaneously():
    """The whole point of the slot split - a melee weapon and a ranged weapon occupy different slots, so
    equipping one must not unequip the other, mirroring Armour's helmet/body split."""
    hero = Character(name="Hero", hp=100, attack_damage=10)
    sword = Weapon(name="Iron Sword", description="", damage=5)
    bow = Weapon(name="Short Bow", description="", damage=4, slot="ranged")
    sword.use(hero)
    bow.use(hero)
    assert sword.equipped is True
    assert bow.equipped is True

def test_weapon_use_different_slots_do_not_unequip_each_other():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    sword = Weapon(name="Iron Sword", description="", damage=5)
    bow = Weapon(name="Short Bow", description="", damage=4, slot="ranged")
    sword.use(hero)
    bow.use(hero)
    assert hero.equipped_melee_weapon is sword
    assert hero.equipped_ranged_weapon is bow

def test_weapon_use_same_slot_swap_does_not_affect_a_different_slot():
    hero = Character(name="Hero", hp=100, attack_damage=10)
    old_sword = Weapon(name="Iron Sword", description="", damage=5)
    new_sword = Weapon(name="Steel Sword", description="", damage=8)
    bow = Weapon(name="Short Bow", description="", damage=4, slot="ranged")
    old_sword.use(hero)
    bow.use(hero)
    new_sword.use(hero)
    assert old_sword.equipped is False
    assert hero.equipped_melee_weapon is new_sword
    assert bow.equipped is True
    assert hero.equipped_ranged_weapon is bow

def test_armour_use_increases_armour():
    hero = Character(name="hero", hp=100, attack_damage=10)
    armour = Armour(name="helmet", description="", defence=3)
    armour.use(hero)
    assert hero.armour == 3

def test_armour_use_returns_equip_message():
    hero = Character(name="hero", hp=100, attack_damage=10)
    armour = Armour(name="helmet", description="", defence=3)
    message = armour.use(hero)
    assert message == "hero equips helmet (body, +3 DEF)."

def test_armour_use_sets_equipped_flag():
    hero = Character(name="hero", hp=100, attack_damage=10)
    armour = Armour(name="helmet", description="", defence=3)
    armour.use(hero)
    assert armour.equipped is True

def test_armour_use_when_already_equipped_does_not_increase_armour_again():
    hero = Character(name="hero", hp=100, attack_damage=10)
    armour = Armour(name="helmet", description="", defence=3)
    armour.use(hero)
    armour.use(hero)
    assert hero.armour == 3

def test_armour_use_when_already_equipped_returns_already_equipped_message():
    hero = Character(name="hero", hp=100, attack_damage=10)
    armour = Armour(name="helmet", description="", defence=3)
    armour.use(hero)
    message = armour.use(hero)
    assert message == "helmet already equipped"

def test_armour_unequip_when_not_equipped_returns_not_equipped_message():
    hero = Character(name="hero", hp=100, attack_damage=10)
    armour = Armour(name="helmet", description="", defence=3)
    message = armour.unequip(hero)
    assert message == "helmet is not equipped."

def test_armour_unequip_when_equipped_decreases_armour():
    hero = Character(name="hero", hp=100, attack_damage=10)
    armour = Armour(name="helmet", description="", defence=3)
    armour.use(hero)
    armour.unequip(hero)
    assert hero.armour == 0

def test_armour_unequip_when_equipped_clears_equipped_flag():
    hero = Character(name="hero", hp=100, attack_damage=10)
    armour = Armour(name="helmet", description="", defence=3)
    armour.use(hero)
    armour.unequip(hero)
    assert armour.equipped is False

def test_armour_unequip_when_equipped_returns_unequip_message():
    hero = Character(name="hero", hp=100, attack_damage=10)
    armour = Armour(name="helmet", description="", defence=3)
    armour.use(hero)
    message = armour.unequip(hero)
    assert message == "hero unequips helmet (-3 DEF)"

def test_armour_use_defaults_to_body_slot():
    armour = Armour(name="helmet", description="", defence=3)
    assert armour.slot == "body"

def test_armour_initialises_with_default_max_durability():
    armour = Armour(name="helmet", description="", defence=3)
    assert armour.max_durability == 10

def test_armour_initialises_with_custom_max_durability():
    armour = Armour(name="helmet", description="", defence=3, max_durability=5)
    assert armour.max_durability == 5

def test_armour_initialises_with_durability_starting_at_max():
    armour = Armour(name="helmet", description="", defence=3, max_durability=5)
    assert armour.durability == 5

def test_armour_use_sets_character_equipped_body_by_default():
    hero = Character(name="hero", hp=100, attack_damage=10)
    armour = Armour(name="helmet", description="", defence=3)
    armour.use(hero)
    assert hero.equipped_body is armour

def test_armour_use_with_helmet_slot_sets_character_equipped_helmet():
    hero = Character(name="hero", hp=100, attack_damage=10)
    armour = Armour(name="Bronze Helm", description="", defence=2, slot="helmet")
    armour.use(hero)
    assert hero.equipped_helmet is armour

def test_armour_unequip_clears_character_equipped_body():
    hero = Character(name="hero", hp=100, attack_damage=10)
    armour = Armour(name="helmet", description="", defence=3)
    armour.use(hero)
    armour.unequip(hero)
    assert hero.equipped_body is None

def test_armour_use_replacing_same_slot_unequips_old_armour():
    hero = Character(name="hero", hp=100, attack_damage=10)
    old_armour = Armour(name="helmet", description="", defence=3)
    new_armour = Armour(name="Iron Helm", description="", defence=5)
    old_armour.use(hero)
    new_armour.use(hero)
    assert old_armour.equipped is False

def test_armour_use_replacing_same_slot_updates_character_equipped_body():
    hero = Character(name="hero", hp=100, attack_damage=10)
    old_armour = Armour(name="helmet", description="", defence=3)
    new_armour = Armour(name="Iron Helm", description="", defence=5)
    old_armour.use(hero)
    new_armour.use(hero)
    assert hero.equipped_body is new_armour

def test_armour_use_replacing_same_slot_updates_defence():
    hero = Character(name="hero", hp=100, attack_damage=10)
    old_armour = Armour(name="helmet", description="", defence=3)
    new_armour = Armour(name="Iron Helm", description="", defence=5)
    old_armour.use(hero)
    new_armour.use(hero)
    assert hero.armour == 5

def test_armour_use_replacing_same_slot_returns_combined_message():
    hero = Character(name="hero", hp=100, attack_damage=10)
    old_armour = Armour(name="helmet", description="", defence=3)
    new_armour = Armour(name="Iron Helm", description="", defence=5)
    old_armour.use(hero)
    message = new_armour.use(hero)
    assert message == "hero unequips helmet (-3 DEF)\nhero equips Iron Helm (body, +5 DEF)."

def test_armour_use_helmet_and_body_can_be_equipped_simultaneously():
    """The whole point of the slot rework - a helmet and a body piece occupy different slots, so equipping
    one must not unequip the other, unlike Weapon's single slot."""
    hero = Character(name="hero", hp=100, attack_damage=10)
    helmet = Armour(name="Bronze Helm", description="", defence=2, slot="helmet")
    body = Armour(name="Breastplate", description="", defence=3, slot="body")
    helmet.use(hero)
    body.use(hero)
    assert helmet.equipped is True
    assert body.equipped is True
    assert hero.armour == 5

def test_armour_use_different_slots_do_not_unequip_each_other():
    hero = Character(name="hero", hp=100, attack_damage=10)
    helmet = Armour(name="Bronze Helm", description="", defence=2, slot="helmet")
    body = Armour(name="Breastplate", description="", defence=3, slot="body")
    helmet.use(hero)
    body.use(hero)
    assert hero.equipped_helmet is helmet
    assert hero.equipped_body is body

def test_armour_use_same_slot_swap_does_not_affect_a_different_slot():
    hero = Character(name="hero", hp=100, attack_damage=10)
    old_helmet = Armour(name="Bronze Helm", description="", defence=2, slot="helmet")
    new_helmet = Armour(name="Iron Helm", description="", defence=4, slot="helmet")
    body = Armour(name="Breastplate", description="", defence=3, slot="body")
    old_helmet.use(hero)
    body.use(hero)
    new_helmet.use(hero)
    assert old_helmet.equipped is False
    assert hero.equipped_helmet is new_helmet
    assert body.equipped is True
    assert hero.equipped_body is body

def test_consumable_use_heals_character():
    hero = Character(name="hero", hp=100, attack_damage=10)
    potion = Consumable(name="potion", heal_amount=3)
    hero.take_damage(10)
    potion.use(hero)
    assert hero.hp == 93

def test_consumable_use_does_not_exceed_max_hp():
    hero = Character(name="hero", hp=100, attack_damage=10)
    potion = Consumable(name="potion", heal_amount=3)
    hero.take_damage(2)
    potion.use(hero)
    assert hero.hp == 100

def test_consumable_use_returns_heal_message():
    hero = Character(name="hero", hp=100, attack_damage=10)
    potion = Consumable(name="potion", heal_amount=3)
    hero.take_damage(10)
    message = potion.use(hero)
    assert message == "hero uses potion, healing 3 HP."

def test_consumable_defaults_to_zero_heal_amount():
    consumable = Consumable(name="Empty Vial", description="")
    assert consumable.heal_amount == 0

def test_consumable_ends_turn_returns_true_when_heal_amount_is_zero():
    hero = Player(name="hero", hp=100)
    consumable = Consumable(name="Empty Vial", description="")
    assert consumable.ends_turn(hero) is True

def test_consumable_ends_turn_returns_false_when_heal_amount_is_positive():
    """A genuine heal is a free action mid-combat - it must not end the player's turn (and so must not
    trigger the enemy's counterattack), unlike every other use() call."""
    hero = Player(name="hero", hp=100)
    potion = Consumable(name="potion", heal_amount=3)
    assert potion.ends_turn(hero) is False

def test_reviver_use_with_no_companion_attribute_returns_message():
    """getattr(character, "companion", None) - a plain Character has no .companion attribute at all,
    distinct from a Player whose companion is explicitly None."""
    hero = Character(name="hero", hp=100, attack_damage=10)
    reviver = Reviver(name="Ambrosia", heal_amount=10)
    message = reviver.use(hero)
    assert message == "Ambrosia has nothing to revive."

def test_reviver_use_with_player_and_no_companion_returns_message():
    hero = Player(name="hero", hp=100)
    reviver = Reviver(name="Ambrosia", heal_amount=10)
    message = reviver.use(hero)
    assert message == "Ambrosia has nothing to revive."

def test_reviver_use_with_living_companion_returns_message_without_reviving():
    hero = Player(name="hero", hp=100)
    home = Room("Camp")
    hero.companion = Companion(name="Imp", hp=10, home_room=home)
    reviver = Reviver(name="Ambrosia", heal_amount=10)
    message = reviver.use(hero)
    assert message == "Imp doesn't need reviving."

def test_reviver_use_with_living_companion_does_not_change_hp():
    hero = Player(name="hero", hp=100)
    home = Room("Camp")
    companion = Companion(name="Imp", hp=10, home_room=home)
    hero.companion = companion
    reviver = Reviver(name="Ambrosia", heal_amount=10)
    reviver.use(hero)
    assert companion.hp == 10

def test_reviver_use_with_downed_companion_revives_with_heal_amount():
    hero = Player(name="hero", hp=100)
    home = Room("Camp")
    companion = Companion(name="Imp", hp=10, home_room=home)
    companion.hp = 0
    hero.companion = companion
    reviver = Reviver(name="Ambrosia", heal_amount=6)
    reviver.use(hero)
    assert companion.hp == 6

def test_reviver_use_with_downed_companion_caps_revive_at_max_hp():
    hero = Player(name="hero", hp=100)
    home = Room("Camp")
    companion = Companion(name="Imp", hp=10, home_room=home)
    companion.hp = 0
    hero.companion = companion
    reviver = Reviver(name="Ambrosia", heal_amount=100) # far exceeds the companion's max_hp
    reviver.use(hero)
    assert companion.hp == 10

def test_reviver_use_with_downed_companion_returns_revive_message():
    hero = Player(name="hero", hp=100)
    home = Room("Camp")
    companion = Companion(name="Imp", hp=10, home_room=home)
    companion.hp = 0
    hero.companion = companion
    reviver = Reviver(name="Ambrosia", heal_amount=6)
    message = reviver.use(hero)
    assert message == "Imp is revived with 6 HP, thanks to Ambrosia."

def test_reviver_is_a_consumable():
    reviver = Reviver(name="Ambrosia", heal_amount=6)
    assert isinstance(reviver, Consumable)

def test_reviver_used_via_inventory_is_removed_after_use():
    """Reviver inherits Consumable's auto-remove-after-use behaviour in Inventory.use_item() - confirms
    the integration actually holds, not just the isinstance relationship."""
    hero = Player(name="hero", hp=100)
    home = Room("Camp")
    companion = Companion(name="Imp", hp=10, home_room=home)
    companion.hp = 0
    hero.companion = companion
    reviver = Reviver(name="Ambrosia", heal_amount=6)
    hero.inventory.add(reviver)

    hero.inventory.use_item("Ambrosia", hero)

    assert reviver not in hero.inventory.items

def test_status_effect_item_initialises_with_effect_attributes():
    item = StatusEffectItem(name="Tonic of Regeneration", description="", effect_name="Regen", amount=3, duration=4)
    assert item.effect_name == "Regen"
    assert item.amount == 3
    assert item.duration == 4

def test_status_effect_item_is_a_consumable():
    item = StatusEffectItem(name="Tonic of Regeneration", description="", effect_name="Regen", amount=3, duration=4)
    assert isinstance(item, Consumable)

def test_status_effect_item_use_with_positive_amount_applies_effect_to_self():
    player = Player(name="Hero", hp=20)
    item = StatusEffectItem(name="Tonic of Regeneration", description="", effect_name="Regen", amount=3, duration=4)
    item.use(player)
    assert len(player.active_effects) == 1
    assert player.active_effects[0].name == "Regen"

def test_status_effect_item_use_with_positive_amount_returns_confirmation_message():
    player = Player(name="Hero", hp=20)
    item = StatusEffectItem(name="Tonic of Regeneration", description="", effect_name="Regen", amount=3, duration=4)
    message = item.use(player)
    assert message == "Hero is afflicted with Regen."

def test_status_effect_item_use_builds_a_fresh_effect_object_each_time():
    """Each use() must build its own StatusEffect - two characters affected by the same item must not
    secretly share one mutable effect object."""
    item = StatusEffectItem(name="Tonic of Regeneration", description="", effect_name="Regen", amount=3, duration=4)
    hero = Player(name="Hero", hp=20)
    ally = Player(name="Ally", hp=20)
    item.use(hero)
    item.use(ally)
    assert hero.active_effects[0] is not ally.active_effects[0]

def test_status_effect_item_use_with_negative_amount_applies_to_current_target():
    player = Player(name="Hero", hp=20)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    player.current_target = enemy
    item = StatusEffectItem(name="Vial of Poison", description="", effect_name="Poison", amount=-3, duration=4)

    item.use(player)

    assert len(enemy.active_effects) == 1
    assert player.active_effects == []

def test_status_effect_item_use_with_negative_amount_and_no_target_raises_error():
    player = Player(name="Hero", hp=20)
    item = StatusEffectItem(name="Vial of Poison", description="", effect_name="Poison", amount=-3, duration=4)

    try:
        item.use(player)
        assert False, "Expected a ValueError but none was raised"
    except ValueError:
        pass

def test_status_effect_item_use_with_negative_amount_and_dead_target_raises_error():
    player = Player(name="Hero", hp=20)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    enemy.hp = 0
    player.current_target = enemy
    item = StatusEffectItem(name="Vial of Poison", description="", effect_name="Poison", amount=-3, duration=4)

    try:
        item.use(player)
        assert False, "Expected a ValueError but none was raised"
    except ValueError:
        pass

def test_item_would_fail_defaults_to_none():
    weapon = Weapon(name="Iron Sword", description="", damage=5)
    player = Player(name="Hero", hp=20)
    assert weapon.would_fail(player) is None

def test_item_ends_turn_defaults_to_true():
    weapon = Weapon(name="Iron Sword", description="", damage=5)
    player = Player(name="Hero", hp=20)
    assert weapon.ends_turn(player) is True

def test_status_effect_item_ends_turn_returns_true_when_amount_is_negative():
    player = Player(name="Hero", hp=20)
    item = StatusEffectItem(name="Vial of Poison", description="", effect_name="Poison", amount=-3, duration=4)
    assert item.ends_turn(player) is True

def test_status_effect_item_ends_turn_returns_false_when_amount_is_non_negative():
    """A self-targeted heal-over-time is a free action, matching Consumable's own rule - only the
    offensive (negative-amount) case still ends the turn."""
    player = Player(name="Hero", hp=20)
    item = StatusEffectItem(name="Tonic of Regeneration", description="", effect_name="Regen", amount=3, duration=4)
    assert item.ends_turn(player) is False

def test_status_effect_item_would_fail_returns_none_with_positive_amount_regardless_of_target():
    player = Player(name="Hero", hp=20)
    item = StatusEffectItem(name="Tonic of Regeneration", description="", effect_name="Regen", amount=3, duration=4)
    assert item.would_fail(player) is None

def test_status_effect_item_would_fail_returns_none_when_negative_amount_has_a_living_target():
    player = Player(name="Hero", hp=20)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    player.current_target = enemy
    item = StatusEffectItem(name="Vial of Poison", description="", effect_name="Poison", amount=-3, duration=4)
    assert item.would_fail(player) is None

def test_status_effect_item_would_fail_returns_message_when_negative_amount_has_no_target():
    player = Player(name="Hero", hp=20)
    item = StatusEffectItem(name="Vial of Poison", description="", effect_name="Poison", amount=-3, duration=4)
    assert item.would_fail(player) == "You need a target for Vial of Poison - try 'target <enemy>' first."

def test_status_effect_item_would_fail_returns_message_when_negative_amount_target_is_dead():
    player = Player(name="Hero", hp=20)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    enemy.hp = 0
    player.current_target = enemy
    item = StatusEffectItem(name="Vial of Poison", description="", effect_name="Poison", amount=-3, duration=4)
    assert item.would_fail(player) == "You need a target for Vial of Poison - try 'target <enemy>' first."

def test_status_effect_item_use_with_no_target_error_message():
    player = Player(name="Hero", hp=20)
    item = StatusEffectItem(name="Vial of Poison", description="", effect_name="Poison", amount=-3, duration=4)

    try:
        item.use(player)
        assert False, "Expected a ValueError but none was raised"
    except ValueError as e:
        assert str(e) == "You need a target for Vial of Poison - try 'target <enemy>' first."

def test_status_effect_item_used_via_inventory_is_removed_after_use():
    player = Player(name="Hero", hp=20)
    item = StatusEffectItem(name="Tonic of Regeneration", description="", effect_name="Regen", amount=3, duration=4)
    player.inventory.add(item)

    player.inventory.use_item("Tonic of Regeneration", player)

    assert item not in player.inventory.items

def test_spell_book_initialises_with_spell():
    spell = Spell(name="Firebolt", description="", mana_cost=5, damage=10)
    book = SpellBook(name="Tome of Fire", description="", spell=spell)
    assert book.spell is spell

def test_spell_book_is_a_consumable():
    spell = Spell(name="Firebolt", description="", mana_cost=5, damage=10)
    book = SpellBook(name="Tome of Fire", description="", spell=spell)
    assert isinstance(book, Consumable)

def test_spell_book_use_adds_spell_to_known_spells():
    player = Player(name="Hero", hp=20)
    spell = Spell(name="Firebolt", description="", mana_cost=5, damage=10)
    book = SpellBook(name="Tome of Fire", description="", spell=spell)
    book.use(player)
    assert spell in player.known_spells

def test_spell_book_use_returns_confirmation_message():
    player = Player(name="Hero", hp=20)
    spell = Spell(name="Firebolt", description="", mana_cost=5, damage=10)
    book = SpellBook(name="Tome of Fire", description="", spell=spell)
    message = book.use(player)
    assert message == "Hero learns Firebolt!"

def test_spell_book_use_when_already_known_raises_error():
    player = Player(name="Hero", hp=20)
    spell = Spell(name="Firebolt", description="", mana_cost=5, damage=10)
    player.known_spells.append(spell)
    book = SpellBook(name="Tome of Fire", description="", spell=spell)

    try:
        book.use(player)
        assert False, "Expected a ValueError but none was raised"
    except ValueError as e:
        assert str(e) == "Hero already knows Firebolt."

def test_spell_book_use_when_already_known_does_not_add_duplicate():
    player = Player(name="Hero", hp=20)
    spell = Spell(name="Firebolt", description="", mana_cost=5, damage=10)
    player.known_spells.append(spell)
    book = SpellBook(name="Tome of Fire", description="", spell=spell)

    try:
        book.use(player)
    except ValueError:
        pass

    assert len(player.known_spells) == 1

def test_spell_book_use_matches_already_known_by_name_not_object_identity():
    player = Player(name="Hero", hp=20)
    player.known_spells.append(Spell(name="Firebolt", description="a different copy", mana_cost=99))
    new_spell = Spell(name="Firebolt", description="", mana_cost=5, damage=10)
    book = SpellBook(name="Tome of Fire", description="", spell=new_spell)

    try:
        book.use(player)
        assert False, "Expected a ValueError but none was raised"
    except ValueError:
        pass

def test_spell_book_would_fail_returns_none_when_not_known():
    player = Player(name="Hero", hp=20)
    spell = Spell(name="Firebolt", description="", mana_cost=5, damage=10)
    book = SpellBook(name="Tome of Fire", description="", spell=spell)
    assert book.would_fail(player) is None

def test_spell_book_would_fail_returns_message_when_already_known():
    player = Player(name="Hero", hp=20)
    spell = Spell(name="Firebolt", description="", mana_cost=5, damage=10)
    player.known_spells.append(spell)
    book = SpellBook(name="Tome of Fire", description="", spell=spell)
    assert book.would_fail(player) == "Hero already knows Firebolt."

def test_spell_book_used_via_inventory_is_removed_after_use():
    player = Player(name="Hero", hp=20)
    spell = Spell(name="Firebolt", description="", mana_cost=5, damage=10)
    book = SpellBook(name="Tome of Fire", description="", spell=spell)
    player.inventory.add(book)

    player.inventory.use_item("Tome of Fire", player)

    assert book not in player.inventory.items

def test_spell_book_used_via_inventory_when_already_known_is_not_removed():
    """use() raises rather than returning when already known, so Inventory.use_item()'s removal line is
    never reached - the book stays in inventory instead of being wasted."""
    player = Player(name="Hero", hp=20)
    spell = Spell(name="Firebolt", description="", mana_cost=5, damage=10)
    player.known_spells.append(spell)
    book = SpellBook(name="Tome of Fire", description="", spell=spell)
    player.inventory.add(book)

    try:
        player.inventory.use_item("Tome of Fire", player)
    except ValueError:
        pass

    assert book in player.inventory.items

def test_quest_item_use_returns_message():
    key = QuestItem(name="Bronze Key", description="")
    message = key.use(Character(name="hero", hp=100, attack_damage=10))
    assert message == "Bronze Key doesn't do anything on its own - it is meant for someone else."

def test_quest_item_use_does_not_change_character_stats():
    hero = Character(name="hero", hp=100, attack_damage=10)
    key = QuestItem(name="Bronze Key", description="")
    key.use(hero)
    assert hero.attack_damage == 10
    assert hero.armour == 0
    assert hero.hp == 100

def test_quest_item_unequip_returns_cannot_be_unequipped_message():
    hero = Character(name="hero", hp=100, attack_damage=10)
    key = QuestItem(name="Bronze Key", description="")
    message = key.unequip(hero)
    assert message == "Bronze Key cannot be unequipped."

def test_skill_point_reward_defaults_to_one_point():
    reward = SkillPointReward(name="Ancient Blessing", description="")
    assert reward.points == 1

def test_skill_point_reward_use_increases_skill_points():
    player = Player(name="hero", hp=100)
    reward = SkillPointReward(name="Ancient Blessing", description="", points=2)
    reward.use(player)
    assert player.skill_tree.skill_points == 2

def test_skill_point_reward_use_returns_message():
    player = Player(name="hero", hp=100)
    reward = SkillPointReward(name="Ancient Blessing", description="", points=2)
    message = reward.use(player)
    assert message == "hero gains 2 skill point(s) from Ancient Blessing."

def test_inventory_use_item_keeps_skill_point_reward_after_use():
    player = Player(name="hero", hp=100)
    reward = SkillPointReward(name="Ancient Blessing", description="", points=1)
    player.inventory.add(reward)
    player.inventory.use_item("Ancient Blessing", player)
    assert player.inventory.items == [reward]

def test_item_repr_includes_class_name_and_name(capsys):
    potion = Consumable(name="potion", heal_amount=3)
    print(potion)
    captured = capsys.readouterr()
    assert "Consumable(name='potion')" in captured.out

def test_inventory_add_adds_item():
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="Sword", damage=5)
    player.inventory.add(sword)
    assert sword in player.inventory.items


def test_inventory_items_property_returns_copy():
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="Sword", damage=5)
    shield = Armour(name="Shield", description="Shield", defence=3)
    player.inventory.add(sword)
    player.inventory.items.append(shield)
    assert player.inventory.items == [sword]

def test_inventory_use_item_removes_consumable_after_use():
    player = Player(name="hero", hp=100)
    potion = Consumable(name="potion", heal_amount=10)
    player.inventory.add(potion)
    assert player.inventory.items == [potion]
    player.inventory.use_item("potion", player)
    assert player.inventory.items == []

def test_inventory_use_item_keeps_weapon_after_use():
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="Sword", damage=5)
    player.inventory.add(sword)
    assert player.inventory.items == [sword]
    player.inventory.use_item("Bronze Xiphos", player)
    assert player.inventory.items == [sword]

def test_use_item_raises_error_when_item_not_found():
    player = Player(name="hero", hp=100)

    try:
        player.inventory.use_item("Bronze Xiphos", player)
        assert False, "Expected a ValueError but none was raised"
    except ValueError:
        pass

def test_inventory_drop_item_removes_item_from_inventory():
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    player.inventory.add(sword)
    player.inventory.drop_item("Bronze Xiphos")
    assert player.inventory.items == []

def test_inventory_drop_item_returns_dropped_item():
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    player.inventory.add(sword)
    dropped = player.inventory.drop_item("Bronze Xiphos")
    assert dropped is sword

def test_inventory_drop_item_raises_error_when_equipped():
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    player.inventory.add(sword)
    player.inventory.use_item("Bronze Xiphos", player)

    try:
        player.inventory.drop_item("Bronze Xiphos")
        assert False, "Expected a ValueError but none was raised"
    except ValueError:
        pass

def test_inventory_drop_item_when_equipped_does_not_remove_it():
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    player.inventory.add(sword)
    player.inventory.use_item("Bronze Xiphos", player)

    try:
        player.inventory.drop_item("Bronze Xiphos")
    except ValueError:
        pass
    assert player.inventory.items == [sword]

def test_inventory_drop_item_raises_error_when_item_is_quest_item():
    player = Player(name="hero", hp=100)
    key = QuestItem(name="Bronze Key", description="")
    player.inventory.add(key)

    try:
        player.inventory.drop_item("Bronze Key")
        assert False, "Expected a ValueError but none was raised"
    except ValueError:
        pass

def test_inventory_drop_item_does_not_remove_quest_item_when_blocked():
    player = Player(name="hero", hp=100)
    key = QuestItem(name="Bronze Key", description="")
    player.inventory.add(key)

    try:
        player.inventory.drop_item("Bronze Key")
    except ValueError:
        pass
    assert player.inventory.items == [key]

def test_inventory_drop_item_raises_error_when_item_not_found():
    player = Player(name="hero", hp=100)

    try:
        player.inventory.drop_item("Bronze Xiphos")
        assert False, "Expected a ValueError but none was raised"
    except ValueError:
        pass

def test_inventory_len_returns_item_count():
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    player.inventory.add(sword)
    assert len(player.inventory) == 1

def test_inventory_remove_removes_item():
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    player.inventory.add(sword)
    player.inventory.remove(sword)
    assert player.inventory.items == []

def test_inventory_repr_includes_item_names(capsys):
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    player.inventory.add(sword)
    print(player.inventory)
    captured = capsys.readouterr()
    assert "Inventory(['Bronze Xiphos'])" in captured.out

def test_inventory_use_item_matches_item_name_case_insensitively():
    player = Player(name="hero", hp=100)
    potion = Consumable(name="Potion", heal_amount=10)
    player.inventory.add(potion)
    player.inventory.use_item("potion", player)
    assert player.inventory.items == []

def test_inventory_drop_item_matches_item_name_case_insensitively():
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    player.inventory.add(sword)
    dropped = player.inventory.drop_item("bronze xiphos")
    assert dropped is sword

def test_inventory_unequip_item_returns_items_unequip_message():
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    player.inventory.add(sword)
    player.inventory.use_item("Bronze Xiphos", player)
    message = player.inventory.unequip_item("Bronze Xiphos", player)
    assert message == "hero unequips Bronze Xiphos (-3 DMG)"

def test_inventory_unequip_item_raises_error_when_item_not_found():
    player = Player(name="hero", hp=100)

    try:
        player.inventory.unequip_item("Bronze Xiphos", player)
        assert False, "Expected a ValueError but none was raised"
    except ValueError:
        pass

def test_inventory_unequip_item_matches_item_name_case_insensitively():
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    player.inventory.add(sword)
    player.inventory.use_item("Bronze Xiphos", player)
    message = player.inventory.unequip_item("bronze xiphos", player)
    assert message == "hero unequips Bronze Xiphos (-3 DMG)"

def test_inventory_remove_raises_error_when_item_not_in_inventory():
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)

    try:
        player.inventory.remove(sword)
        assert False, "Expected a ValueError but none was raised"
    except ValueError:
        pass


