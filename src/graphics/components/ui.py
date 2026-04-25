from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
import dataclasses
from dataclasses import dataclass
from typing import Generic, TypeVar

import pygame

from graphics.components import primitives
from graphics.components.style import AlignHor, AlignVer, TextConfig, BorderConfig, Gap, lerp
from pygame import Rect, Color
from pygame.event import Event
from graphics.surfaces import Surface
from game.timer import game_timer
from loguru_config import get_subsystem_logger

logger = get_subsystem_logger('graphics.components')

T = TypeVar('T')

class AnimType(Generic[T]):
    def __init__(self, a: T, b: T, ms: int):
        self.val = a
        self.a: T = a
        self.b: T = b
        self.ms: int = ms
        self._t: float = 0.0
        super().__init__()

    @property
    def t(self):
        return self._t

    @t.setter
    def t(self, new_t):
        self._t = new_t
        self.val = lerp(self.a, self.b, self._t)

    def delta(self, dx: int):
        self.t = max(min(self._t + dx / self.ms, 1.0), 0.0)


class AnimComponentProperty(ABC):
    def __getattribute__(self, name):
        if name.startswith('_') or name == 'delta':
            value = super().__getattribute__(name)
            return value
        private_name = f'_{name}'
        
        raw = super().__getattribute__(private_name)
        return raw.val if isinstance(raw, AnimType) else raw

    def delta(self, dx):
        for f in dataclasses.fields(self):
            value = getattr(self, f.name)
            if isinstance(value, AnimType):
                value.delta(dx)


@dataclass(frozen=False)
class ButtonStyle(AnimComponentProperty):
    _rect: Rect | AnimType[Rect]
    _fill_color: Color | AnimType[Color]
    _text_config: TextConfig | AnimType[TextConfig]
    _border_config: BorderConfig | AnimType[BorderConfig]
    _padding: Gap | AnimType[Gap]


@dataclass(frozen=False)
class BoxStyle():
    pass


@dataclass(frozen=False)
class LabelStyle(AnimComponentProperty):
    _rect: Rect | AnimType[Rect]
    _text_config: TextConfig | AnimType[TextConfig]
    _padding: Gap | AnimType[Gap]
    

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


class Box(Component):
    def __init__(self, parent_surface: Surface, style: BoxStyle):
        self.style: BoxStyle = style
        super().__init__(parent_surface, lambda: self.style.rect)


class Label(Component):
    def __init__(self, parent_surface: Surface, text: str, style: LabelStyle):
        self.style: LabelStyle = style
        self.text: str = text

        super().__init__(parent_surface, lambda: self.style.rect)

    def graphics_handler(self):
        primitives.draw_text(self.parent_surface, 
                             self.style.rect, 
                             self.text, 
                             self.style.text_config, 
                             self.style.padding)
        return super().graphics_handler()
    
    def events_handler(self, events, mouse_offset):
        new_time = game_timer.time_ms
        dx = new_time - self.last_update
        self.last_update = new_time

        mouse_dx, mouse_dy = mouse_offset
        raw_mouse = pygame.mouse.get_pos()
        mouse_x, mouse_y = raw_mouse[0] - mouse_dx, raw_mouse[1] - mouse_dy
        
        for event in events:
            if event.type not in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN):
                continue
        
        if 0 < mouse_x < self.style.rect.w and 0 < mouse_y < self.style.rect.h:
            self.hovered = True
            self.style.delta(dx)
        else:
            self.hovered = False
            self.style.delta(-dx)

        return super().events_handler(events, mouse_offset)


class Button(Component):
    def __init__(self, parent_surface: Surface, text: str, style: ButtonStyle, on_click: Callable[[Button], None], on_hover: Callable[[Button], None]):
        self.style: ButtonStyle = style
        self.text: str = text
        self.on_click: Callable[[Button], None] = on_click
        self.on_hover: Callable[[Button], None] = on_hover
        self.hovered: bool = False
        super().__init__(parent_surface, lambda: self.style.rect)

    def graphics_handler(self):
        primitives.draw_text_in_box(self.parent_surface, 
                                    self.style.rect, 
                                    self.text, 
                                    self.style.text_config, 
                                    self.style.border_config, 
                                    self.style.fill_color, 
                                    self.style.padding)
        
        return super().graphics_handler()

    def events_handler(self, events: list[Event], mouse_offset: tuple[int, int]):
        new_time = game_timer.time_ms
        dx = new_time - self.last_update
        self.last_update = new_time
        
        mouse_dx, mouse_dy = mouse_offset
        raw_mouse = pygame.mouse.get_pos()
        mouse_x, mouse_y = raw_mouse[0] - mouse_dx, raw_mouse[1] - mouse_dy

        for event in events:
            if event.type not in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN):
                continue

            if event.type == pygame.MOUSEBUTTONUP:
                if 0 < mouse_x < self.style.rect.w and 0 < mouse_y < self.style.rect.h:
                    self.on_click(self)

        if 0 < mouse_x < self.style.rect.w and 0 < mouse_y < self.style.rect.h:
            if not self.hovered:
                self.on_hover(self)
            self.hovered = True
            self.style.delta(dx)
        else:
            self.hovered = False
            self.style.delta(-dx)

        return super().events_handler(events, mouse_offset)