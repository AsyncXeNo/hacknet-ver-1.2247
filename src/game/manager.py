from copy import copy

import pygame

from game.timer import game_timer
from graphics.conn_pygame_graphics import conn_pygame_graphics
from graphics.constants import FPS
from game.states.base import State


# class RLState(State):
#     def __init__(self):
#         super().__init__()


# class ComputerState(State):
#     def __init__(self):
#         super().__init__()


# class PauseMenuState(State):
#     def __init__(self):
#         super().__init__(should_draw_bg=True)



class GameManager(object):
    def __init__(self):
        self.state_stack: list[State] = []
        self.clock = pygame.Clock()

    def push_state(self, state: State):
        assert not any(map(lambda x: isinstance(x, state.__class__), self.state_stack)), "Cannot push two states of the same kind"
        conn_pygame_graphics.push_state(state)
        self.state_stack.append(state)

    def pop_state(self) -> State:
        state = self.state_stack.pop()
        conn_pygame_graphics.remove_state(state)
        return state

    def main_loop(self):
        while True:

            ms = self.clock.tick(FPS)
            game_timer.delta_time(ms)
            
            events = pygame.event.get()
            if any(map(lambda event: event.type == pygame.QUIT, events)):
                pygame.quit()
                return
            
            current = self.state_stack[-1]
            current.events_handler(events)

            conn_pygame_graphics.main()


game_manager = GameManager()