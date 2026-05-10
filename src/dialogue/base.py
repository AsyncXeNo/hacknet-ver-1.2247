from __future__ import annotations
from abc import ABC
from collections.abc import Callable

from game.states.base import State


class DialogueTreeObject(ABC):
    def __init__(self, trigger: Callable[[], None]):
        self.after: DialogueTreeObject | None = None
        self.trigger: Callable[[], None] = trigger