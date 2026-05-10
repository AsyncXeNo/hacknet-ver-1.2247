from __future__ import annotations

from abc import ABC
from collections.abc import Callable
from types import SimpleNamespace

from pygame import Event, Rect

from graphics.surfaces import Surface
from game.timer import game_timer


class Component(ABC):
    def __init__(self, parent_surface: Surface, rect: Callable[[], Rect]):
        self.parent_surface: Surface = parent_surface
        self.rect = rect
        self.components: SimpleNamespace = SimpleNamespace()
        self.last_update: int = game_timer.time_ms
        self.hovered: bool = False
        super().__init__()

    def events_handler(self, events: list[Event], mouse_offset: tuple[int, int]):
        for component in vars(self.components).values():
            component.events_handler(events, (mouse_offset[0] + component.rect().x, mouse_offset[1] + component.rect().y))

    def add_component(self, name: str, component: Component):
        assert name not in vars(self.components), f'Cannot have multiple components with same name: {name}'
        self.components.__setattr__(name, component)

    def graphics_handler(self):
        for component in vars(self.components).values():
            component.graphics_handler()
