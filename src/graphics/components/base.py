from __future__ import annotations

from abc import ABC
from collections.abc import Callable

from pygame import Event, Rect

from graphics.surfaces import Surface
from game.timer import game_timer


class Component(ABC):
    def __init__(self, parent_surface: Surface, rect: Callable[[], Rect]):
        self.parent_surface: Surface = parent_surface
        self.rect = rect
        self.sub_components: list[Component] = []
        self.last_update: int = game_timer.time_ms
        self.hovered: bool = False
        super().__init__()

    def events_handler(self, events: list[Event], mouse_offset: tuple[int, int]):
        for sub_component in self.sub_components:
            sub_component.events_handler(events, (mouse_offset[0] + sub_component.rect().x, mouse_offset[1] + sub_component.rect().y))

    def add_component(self, component: Component):
        self.sub_components.append(component)

    def graphics_handler(self):
        for sub_component in self.sub_components:
            sub_component.graphics_handler()