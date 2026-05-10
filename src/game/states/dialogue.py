from pygame import Event

from dialogue.flow import DialogueFlow
from game.states.base import State
from loguru_config import get_subsystem_logger

logger = get_subsystem_logger('game.states.main_menu')


class DialogueState(State):
    def __init__(self, flow: DialogueFlow):
        self.flow: DialogueFlow = flow
        super().__init__(should_draw_bg=True)

    def graphics_handler(self):
        super().graphics_handler()

    def events_handler(self, events: list[Event]):
        super().events_handler(events)