
from pygame import Event

from game.states.base import State
from graphics.constants import GAME_HEIGHT, GAME_WIDTH
from graphics.surfaces import Surface
from assets_manager import assets_manager


class RLState(State):
    def __init__(self):
        super().__init__()
        self.img = assets_manager.img.spritesheets.mc.idle[4]

    def graphics_handler(self):
        self.main_surface.blit(self.img, (GAME_WIDTH * 0.5, GAME_HEIGHT * 0.5))
        super().graphics_handler()

    def events_handler(self, events: list[Event]):
        super().events_handler(events)