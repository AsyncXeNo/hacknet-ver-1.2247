from collections.abc import Callable
from dialogue.base import DialogueTreeObject
from game.states.base import State


class Option(DialogueTreeObject):
    def __init__(self, text: str, requirement: Callable[[], bool], trigger: Callable[[], bool]):
        self.text: str = text
        self.requirement: Callable[[], bool] = requirement
        super().__init__(trigger=trigger)


class DialogueChoice(object):
    def __init__(self, options: list[Option]):
        self.options: list[Option] = options
        assert self.options, 'Need options'