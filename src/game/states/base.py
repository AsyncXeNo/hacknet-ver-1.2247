from abc import ABC

from graphics.surfaces import Surface, SurfaceLayer
from graphics.constants import GAME_WIDTH, GAME_HEIGHT


class State(ABC):

    def __init__(self, *, should_draw_bg: bool = False, surface_count: int = 1):
        self.should_draw_bg: bool = should_draw_bg
        self.surface_layer: SurfaceLayer = SurfaceLayer()
        # for _ in range(surface_count):
        #     self.surface_layer = Surface((GAME_WIDTH, GAME_HEIGHT), [0,0])

    def event_handler(self):
        pass

    def graphics_handler(self):
        pass
