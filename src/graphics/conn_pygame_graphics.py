from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game.states.base import State
import sys

import pygame

from typing import Optional

from graphics.surfaces import Surface
from graphics.constants import BLACK, TRANSPARENT
from loguru_config import get_subsystem_logger

logger = get_subsystem_logger('graphics.ConnPygameGraphics')


class ConnPygameGraphics(object):
    def __init__(self, width: int, height: int, caption: str, fullscreen: bool = False) -> None:
        logger.info('Initializing ConnPygameGraphics.')

        pygame.init()

        # info: pygame.display._VidInfo = pygame.display.Info()

        self.width: int = width
        self.height: int = height
        self.caption: str = caption 

        logger.debug("Available Modes: {}", pygame.display.list_modes(32))

        self.window = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN if fullscreen else 0) 
        pygame.display.set_caption(self.caption)

        self.render_queue: list[State] = []

    # Main

    def main(self) -> None:
        self.window.fill(BLACK)
        
        render_queue = self.render_queue.copy()
        draw_set = set()
        current = render_queue.pop()
        draw_set.add(current)
        while current.should_draw_bg:
            try:
                current = render_queue.pop()
                draw_set.add(current)
            except IndexError as e:
                break
                
        for state in self.render_queue:
            if state not in draw_set:
                continue
            state.main_surface.fill(TRANSPARENT)
            state.graphics_handler()
            frame = Surface((self.width, self.height), [0, 0])
            pygame.transform.scale(state.main_surface, (self.width, self.height), frame)
            #TODO: LETTERBOX
            self.window.blit(frame, [0,0])

        pygame.display.update()

    # Queue Operations

    def push_state(self, state: State) -> None:
        self.render_queue.append(state)

    def pop_state(self) -> State:
        return self.render_queue.pop(0)

    def remove_state(self, state: State) -> None:
        self.render_queue.remove(state)

    def select_state(self, state: State) -> None:
        self.render_queue.remove(state)
        self.render_queue.append(state)


conn_pygame_graphics: ConnPygameGraphics = ConnPygameGraphics(1280, 720, 'Hacknet')