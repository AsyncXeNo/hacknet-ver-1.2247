from __future__ import annotations

import pygame

from graphics.utils import generate_id
from graphics.constants import TRANSPARENT, TITLEBAR_DEFAULT_HEIGHT, GAME_WIDTH, GAME_HEIGHT
from loguru_config import get_subsystem_logger

logger = get_subsystem_logger('graphics.surfaces')


class Surface(pygame.Surface):
    """Adds ID and pos attributes to the pygame Surface class"""

    def __init__(self, size: tuple[int, int], pos: list[int]) -> None:

        super().__init__(size, pygame.SRCALPHA)

        self.ID: str = f'SURFACE-{generate_id()}'
        self.pos: list[int] = pos

    @staticmethod
    def from_pygame_surface(source: pygame.Surface, pos: list[int]) -> Surface:
        inst = Surface(source.get_size(), pos)
        inst.blit(source, (0, 0))
        return inst

    def get_surface_range(self, include_titlebar: bool = True) -> tuple[list[int], list[int]]:
        """Returns the surface range from top-left to bottom-right"""

        if not include_titlebar:
            return ([self.pos[0], self.pos[1] + TITLEBAR_DEFAULT_HEIGHT], [self.pos[0] + self.get_width(), self.pos[1] + self.get_height() - TITLEBAR_DEFAULT_HEIGHT])

        return (self.pos, [self.pos[0] + self.get_width(), self.pos[1] + self.get_height()])