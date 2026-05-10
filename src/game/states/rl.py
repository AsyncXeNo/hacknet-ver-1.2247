
from pygame import Event

from game.objects.player import Player
from game.states.base import State
from graphics.constants import GAME_HEIGHT, GAME_WIDTH


class RLState(State):
    def __init__(self):
        super().__init__()
        self.add_component('player', Player(self.main_surface))

    def graphics_handler(self):
        super().graphics_handler()

    def events_handler(self, events: list[Event]):
        super().events_handler(events)