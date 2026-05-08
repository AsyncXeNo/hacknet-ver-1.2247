from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from math import acos, cos, pi

from pygame import Event
import pygame
from pygame import Rect
from graphics.components.ui import Component
from graphics.surfaces import Surface
from game.timer import game_timer
from utils.types import Pointer
from utils.conditions import Condition
from utils.properties import Transform
from loguru_config import get_subsystem_logger

logger = get_subsystem_logger('graphics.sprite')


class Sprite(Component):
    def __init__(self, parent_surface: Surface, state_machine: AnimStateMachine, transform_ptr: Pointer[Transform]):
        self.state_machine = state_machine
        self.transform_ptr = transform_ptr
        self.img_rect: Rect
        self.final

        super().__init__(parent_surface, lambda: self.img_rect)

    @property
    def transform(self):
        return self.transform_ptr()

    @property
    def final(self):
        final_img = pygame.transform.rotozoom(self.state_machine.current, self.transform.rotation, self.transform.scale)
        self.img_rect = Rect(self.transform.translation.x, self.transform.translation.y, final_img.width, final_img.height)
        return final_img

    def events_handler(self, events: list[Event], mouse_offset: tuple[int, int]):
        new_time = game_timer.time_ms
        dx = new_time - self.last_update
        self.last_update = new_time

        self.state_machine.cur_state.delta(dx)
        self.state_machine.check_transition()

        return super().events_handler(events, mouse_offset)

    def graphics_handler(self):
        self.parent_surface.blit(self.final, (self.transform.translation.x, self.transform.translation.y))
        super().graphics_handler()        


class AnimStateMachine(object):
    def __init__(self, start_state: AnimState, trans: list[Transition]):
        self.start_state: AnimState = start_state
        self.cur_state: AnimState = start_state
        self.trans: list[Transition] = trans

    def check_transition(self):
        for tran in self.trans:
            if tran.from_state == self.cur_state and tran:
                self.cur_state = tran.to_state
                self.cur_state.cur_time = 0

    @property
    def current(self) -> Surface:
        return self.cur_state.current


class Transition(object):
    def __init__(self, from_state: AnimState, to_state: AnimState, cond: Condition):
        self.from_state = from_state
        self.to_state = to_state
        self.cond = cond

    def __bool__(self):
        return self.cond.resolve()


class AnimFunc(Enum):
    LOOP = lambda x, frames: int(round(x % frames))
    BACK_AND_FORTH = lambda x, frames: int(round(((frames-1) / pi) * acos(cos((pi/(frames-1))*x))))


class AnimState(object):
    def __init__(self, sprites: list[Surface], duration_ms: int, func: AnimFunc):
        self.sprites = sprites
        self.frames = len(sprites)
        self.cur_time = 0
        self.duration_ms = duration_ms
        self.func = func

    def delta(self, dx):        
        self.cur_time += dx

    @property
    def current(self) -> Surface:
        function = self.func
        cur_frame = self.cur_time // (self.duration_ms / self.frames)
        logger.debug(f'cur_frame: {cur_frame}')
        idx = function(cur_frame, self.frames)
        logger.debug(idx)
        return self.sprites[idx]