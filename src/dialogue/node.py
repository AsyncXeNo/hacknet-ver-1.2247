from collections.abc import Callable
from dataclasses import dataclass

from dialogue.base import DialogueTreeObject
from game.states.base import State
from graphics.components.base import Component


@dataclass
class Speaker(object):
    ref: Component


class DialogueNode(DialogueTreeObject):
    def __init__(self, speaker: Speaker, text: str, trigger: Callable[[], None] | None):
        self.speaker: Speaker = speaker
        self.text: str = text
        super().__init__(trigger)