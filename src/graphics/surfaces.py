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
        self.pos: list[int, int] = pos

    def copy(self) -> Surface:
        """Returns a copy of the surface"""

        new = Surface(self.get_size(), self.pos)
        new.ID = self.ID
        new.blit(self, (0, 0))

        return new

    def get_surface_range(self, include_titlebar: bool = True) -> tuple[list[int], list[int]]:
        """Returns the surface range from top-left to bottom-right"""

        if not include_titlebar:
            return ([self.pos[0], self.pos[1] + TITLEBAR_DEFAULT_HEIGHT], [self.pos[0] + self.get_width(), self.pos[1] + self.get_height() - TITLEBAR_DEFAULT_HEIGHT])

        return (self.pos, [self.pos[0] + self.get_width(), self.pos[1] + self.get_height()])


class SurfaceLayer(object):
    
    def __init__(self):
        self.__surface: Surface = Surface((GAME_WIDTH, GAME_HEIGHT), [0,0])
        self.render_queue: list[Surface] = []

    @property
    def surface(self):
        return self.__surface

    def main(self):
        self.__surface.fill(TRANSPARENT)

        for surface in self.render_queue:
            self.__surface.blit(surface, surface.pos)

    def push_surface(self, surface: Surface) -> None:
        """Pushes a surface to the render queue"""

        self.render_queue.append(surface)

    def pop_surface(self) -> Surface:
        """Pops a surface from the render queue"""

        return self.render_queue.pop(0)

    def remove_surface(self, surface: Surface) -> None:
        """Removes a specific surface from the render queue"""

        for a in range(len(self.render_queue)):
            if self.render_queue[a].ID == surface.ID:
                self.render_queue.pop(a)
        
    def get_surface_by_id(self, surface_id: str) -> Surface | None:
        """Returns a surface with given id"""

        try:
            return list(filter(lambda surface: surface.ID == surface_id, self.render_queue))[0]
        except IndexError:
            logger.warning(f'Surface with ID {surface_id} not found. Ignoring request')
        

    def select_surface(self, surface: Surface) -> None:
        """Puts a render surface at the end of the queue"""

        surface = self.get_surface_by_id(surface.ID)
        self.render_queue.remove(surface)
        self.render_queue.append(surface)