from abc import ABC
from types import SimpleNamespace

from pygame import Event

from graphics.components.ui import Component
from graphics.surfaces import Surface
from graphics.constants import GAME_WIDTH, GAME_HEIGHT


class State(ABC):

    def __init__(self, *, should_draw_bg: bool = False):
        self.should_draw_bg: bool = should_draw_bg
        self.main_surface: Surface = Surface((GAME_WIDTH, GAME_HEIGHT), [0,0])
        self.components: SimpleNamespace = SimpleNamespace()

    def add_component(self, name: str, component: Component):
        assert name not in vars(self.components), f'Cannot have multiple components with same name: {name}'
        self.components.__setattr__(name, component)

    def events_handler(self, events: list[Event]):
        for component in vars(self.components).values():
            component.events_handler(events, (component.rect().x, component.rect().y))

    def graphics_handler(self):
        for component in vars(self.components).values():
            component.graphics_handler()
