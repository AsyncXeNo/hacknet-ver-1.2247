
from game.states.base import State
from lib.graphics.surfaces import Surface


class MainMenuState(State):
    def __init__(self):
        super().__init__()

    def graphics_handler(self):
        # main_surf = Surface()
        return super().graphics_handler()

    def event_handler(self):
        return super().event_handler()
