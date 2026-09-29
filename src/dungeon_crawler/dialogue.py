"""Branching dialogue - an ally's conversation as a set of nodes, each with numbered options the player answers with 'say <number>'. Where the
player is in a conversation lives in the room's transient_state, so leaving resets it. What they chose is recorded by options' effects as story
flags, which are saved - so choices are final. Built for Persephone; reusable for Hades, the ending and the Trophy Room."""

from dataclasses import dataclass, field
from typing import Callable

@dataclass
class DialogueOption:
    """One answer. next_node is where it leads, or None to end the conversation. effect runs when it's chosen and returns a message (or '').
    available decides whether it's offered at all - e.g. a choice that disappears once it's been made."""

    label: str
    next_node: str | None
    effect: Callable | None = None
    available: Callable | None = None

@dataclass
class DialogueNode:
    """What the speaker says, and the options offered. on_enter runs each time the node is reached, returning a message (or '') - e.g. handing
    over a gift for the first time."""

    text: str
    options: list[DialogueOption] = field(default_factory=list)
    on_enter: Callable | None = None

def _offered(node: DialogueNode, player) -> list[DialogueOption]:
    return [option for option in node.options if option.available is None or option.available(player)]

def _show_node(speaker, node_id: str, room, player) -> str:
    """Enter a node: run its on_enter, record the position, and describe it with its numbered options."""
    node = speaker.dialogue[node_id]
    lines = []
    if node.on_enter is not None:
        entered = node.on_enter(player)
        if entered:
            lines.append(entered)
    lines.append(node.text)
    room.transient_state["dialogue"] = (speaker.name, node_id)
    offered = _offered(node, player)
    for number, option in enumerate(offered, start=1):
        lines.append(f"    {number}. {option.label}")
    if offered:
        lines.append("(Answer with 'say <number>'.)")
    return "\n".join(lines)

def start_dialogue(speaker, room, player) -> str:
    """Begin speaker's conversation at its 'start' node."""
    return _show_node(speaker, "start", room, player)

def continue_dialogue(choice: str, room, player) -> str:
    """Answer the current conversation with option number 'choice'. Ends the conversation when an option leads nowhere."""
    position = room.transient_state.get("dialogue")
    if position is None:
        return "You're not in a conversation."
    speaker_name, node_id = position
    speaker = next((ally for ally in room.allies if ally.name == speaker_name), None)
    if speaker is None:
        room.transient_state.pop("dialogue", None)
        return "You're not in a conversation."
    options = _offered(speaker.dialogue[node_id], player)
    if not choice.isdigit() or not 1 <= int(choice) <= len(options):
        return f"Choose an option from 1 to {len(options)}."
    option = options[int(choice) - 1]

    lines = []
    if option.effect is not None:
        result = option.effect(player)
        if result:
            lines.append(result)
    if option.next_node is None:
        room.transient_state.pop("dialogue", None)
    else:
        lines.append(_show_node(speaker, option.next_node, room, player))
    return "\n".join(lines)