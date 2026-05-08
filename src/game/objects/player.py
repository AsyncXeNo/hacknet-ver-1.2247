from __future__ import annotations
from enum import Enum
from types import SimpleNamespace

from pygame import Event
import pygame
from graphics.components.base import Component
from graphics.components.sprite import AnimFunc, Sprite, AnimStateMachine, AnimState, Transition
from graphics.constants import GAME_WIDTH, GAME_HEIGHT
from graphics.surfaces import Surface
from utils.properties import Transform
from utils.conditions import RelationalCondition, RelOp
from utils.properties import Transform, Translation
from assets_manager import assets_manager
from game.timer import game_timer
from copy import deepcopy

class Direction(Enum):
    UP=0
    LEFT=1
    DOWN=2
    RIGHT=3

    @property
    def low_name(self):
        return self.name.lower()


sprites = assets_manager.img.spritesheets

sprites = SimpleNamespace(
    idle={ direction.low_name : deepcopy(sprites.mc.idle[direction.value*2:(direction.value+1)*2]) for direction in Direction },
    walk={ direction.low_name : deepcopy(sprites.mc.walk[direction.value*8:(direction.value+1)*8]) for direction in Direction },
    run={ direction.low_name : deepcopy(sprites.mc.run[direction.value*8:(direction.value+1)*8]) for direction in Direction })

states = SimpleNamespace(
    idle={ direction.low_name: AnimState(sprites.idle[direction.low_name], 500, AnimFunc.BACK_AND_FORTH) for direction in Direction },
    walk={ direction.low_name: AnimState(sprites.walk[direction.low_name], 1000, AnimFunc.LOOP) for direction in Direction },
    run={ direction.low_name: AnimState(sprites.run[direction.low_name], 1000, AnimFunc.LOOP) for direction in Direction }
)

ZERO = lambda: 0.0


class Player(Component):
    def __init__(self, parent_surface: Surface):
        self.transform = Transform(Translation(GAME_WIDTH / 2, GAME_HEIGHT / 2), 0, 1)
        self.vel: Translation = Translation(0, 0)
        self.speed: float = 100.0
        
        relational_conds = [
            RelationalCondition(lambda: self.vel.y, RelOp.LT, ZERO),
            RelationalCondition(lambda: self.vel.x, RelOp.LT, ZERO),
            RelationalCondition(lambda: self.vel.y, RelOp.GT, ZERO),
            RelationalCondition(lambda: self.vel.x, RelOp.GT, ZERO),
        ]

        to_walk = sum([
            [Transition(states.idle[direction.low_name], 
                        states.walk[upper_dir.low_name], 
                        relational_conds[upper_dir.value]) for direction in Direction] for upper_dir in Direction
        ], start=[])

        stop_walk = RelationalCondition(lambda: self.vel.x, RelOp.EQ, ZERO).with_and(RelationalCondition(lambda: self.vel.y, RelOp.EQ, ZERO))
        
        to_idle = [Transition(states.walk[direction.low_name], 
                              states.idle[direction.low_name], 
                              stop_walk) for direction in Direction]
        
        self.state_machine = AnimStateMachine(states.idle[Direction.DOWN.low_name], to_walk + to_idle)
        self.sprite: Sprite = Sprite(parent_surface, self.state_machine, lambda: self.transform)

        super().__init__(parent_surface, self.sprite.rect)
        
        self.add_component(self.sprite)

    def events_handler(self, events: list[Event], mouse_offset: tuple[int, int]) -> None:
        new_time = game_timer.time_ms
        dx = new_time - self.last_update
        self.last_update = new_time
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                match event.key:
                    case pygame.K_w:
                        if self.vel.is_zero:
                            self.vel.y = -self.speed
                    case pygame.K_a:
                        if self.vel.is_zero:
                            self.vel.x = -self.speed
                    case pygame.K_s:
                        if self.vel.is_zero:
                            self.vel.y = self.speed
                    case pygame.K_d:
                        if self.vel.is_zero:
                            self.vel.x = self.speed
            elif event.type == pygame.KEYUP:
                match event.key:
                    case pygame.K_w:
                        if self.vel.y < 0:
                            self.vel.y = 0
                    case pygame.K_a:
                        if self.vel.x < 0 :
                            self.vel.x = 0
                    case pygame.K_s:
                        if self.vel.y > 0:
                            self.vel.y = 0
                    case pygame.K_d:
                        if self.vel.x > 0:
                            self.vel.x = 0

        self.transform.translation.x += self.vel.x * dx / 1000
        self.transform.translation.y += self.vel.y * dx / 1000
        
        super().events_handler(events, mouse_offset)

    def graphics_handler(self) -> None:
        super().graphics_handler()