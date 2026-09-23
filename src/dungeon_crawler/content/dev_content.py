"""Dev-only test content - generic, lore-free instances that exist purely to exercise a system end-to-end via dev tools
(dev spawn/dev add/ dev grant spell/dev teleport). None of this is placed in any real room. See dev_guide.md."""

from dungeon_crawler.world import Room
from dungeon_crawler.spells import Spell
from dungeon_crawler.items import SpellBook, StatusEffectItem
from dungeon_crawler.characters import Enemy, Companion

def build_companion_test_camp() -> Room:
    """A dedicated, unconnected home room for the test Companion below - same reasoning as build_blank_test_room():
    a disposable room that exists purely so dev-test content has somewhere to live, not tied to any real floor."""
    return Room(
        "Companion Test Camp",
        "A quiet clearing set aside for testing recruitment and dismissal - not part of any real floor."
    )

def create_test_companion() -> Companion:
    """Generic dev-test Companion - no lore, no required_items (so 'recruit' succeeds immediately after 'dev spawn'), with attack/defend/heal
    all non-zero so every AI branch is genuinely exercised. Not yet placed in any room; reachable only via 'dev spawn test companion' until a 
    real recruitable Companion (Zeus, tamed enemies, etc.) gets its design finished."""
    return Companion(
        name="Test Companion",
        description="A dev-only stand-in companion, here purely to exercise the recruit/fight/dismiss loop.",
        hp=20,
        home_room=build_companion_test_camp(),
        attack_damage=6,
        armour=1,
        heal_amount=4,
        brace_amount=2,
    )

def create_test_spell() -> Spell:
    """Generic dev-test Spell combining damage and an offensive status effect in one cast, so both branches of Spell.cast()/would_fail()
    get exercised through a real SpellBook rather than only via 'dev grant spell'. Not tied to any lore - a real elemental/ability-tied
    spell roster is still pending design."""
    return Spell(
        name="Test Bolt",
        description="A cracking dev-only bolt, useful for exercising damage and poison in a single cast.",
        mana_cost=5,
        damage=6,
        effect_name="Poison",
        effect_amount=-2,
        effect_duration=3,
    )

def create_test_spellbook() -> SpellBook:
    """SpellBook teaching Test Bolt - lets 'dev add' place a real learnable item, rather than only 'dev grant spell'."""
    return SpellBook(
        name="Test Spellbook",
        description="A dev-only spellbook. Reading it teaches Test Bolt.",
        spell=create_test_spell(),
    )

def create_test_healing_tonic() -> StatusEffectItem:
    """Generic dev-test StatusEffectItem, positive amount - self-targeted heal-over-time, exercising the 'amount >= 0' branch of
    StatusEffectItem.use()."""
    return StatusEffectItem(
        name="Test Healing Tonic",
        description="A dev-only tonic that mends the drinker over time.",
        effect_name="Regen",
        amount=3,
        duration=3,
    )

def create_test_venom_vial() -> StatusEffectItem:
    """Generic dev-test StatusEffectItem, negative amount - offensive, applied to current_target, exercising the 'amount < 0' branch of
    StatusEffectItem.use() (and its would_fail() target check) through real inventory content rather than only 'dev afflict'."""
    return StatusEffectItem(
        name="Test Venom Vial",
        description="A dev-only vial of poison, thrown at whatever you're currently targeting.",
        effect_name="Poison",
        amount=-3,
        duration=3
    )

def create_test_boss() -> Enemy:
    """Generic dev-test boss - two phases, the first gated behind a two-add wave purely to exercise next_wave_factories/wave_gate_factory/
    next_phase_factory end-to-end via 'dev spawn test boss'. Not tied to any lore - a real named boss with this same shape now exists too
    (Medusa, floor 4, see content/floor_4.py), but this dev-only version stays for isolated testing without a full room/fight setup."""
    return Enemy(
        name="Test Boss",
        hp=1,
        attack_damage=1,
        next_wave_factories=[
            lambda: Enemy(name="Test Add", hp=1, attack_damage=1, experience_reward=1, gold_reward=1),
            lambda: Enemy(name="Test Add", hp=1, attack_damage=1, experience_reward=1, gold_reward=1),
        ],
        next_phase_factory=lambda: Enemy(name="Test Boss (Phase 2)", hp=1, attack_damage=1, experience_reward=5, gold_reward=5)
    )

def build_blank_test_room() -> Room:
    """A single, deliberately empty room for dev testing - not connected to anything via exits, only ever reached by 
    'dev teleport dev test room'. Nothing pre-populated; use dev spawn / dev add once inside. """
    return Room(
        "Dev Test Room",
        "A featureless void, useful for exactly nothing except testing things in isolation."
    )