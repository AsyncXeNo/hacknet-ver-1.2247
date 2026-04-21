from copy import copy

import pygame

from graphics.conn_pygame_graphics import conn_pygame_graphics
from game.states.base import State
from game.states.main_menu import MainMenuState


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
        self.push_state(MainMenuState())

    def push_state(self, state: State):
        assert not any(map(lambda x: isinstance(x, state.__class__), self.state_stack)), "Cannot push two states of the same kind"
        conn_pygame_graphics.push_surface(state.surface_layer)
        self.state_stack.append(state)

    def pop_state(self) -> State:
        state = self.state_stack.pop()
        conn_pygame_graphics.remove_surface(state.surface_layer)
        return state

    def main_loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            
            states_copy = copy(self.state_stack)
            draw_table: list[State] = []

            current = states_copy.pop()
            current.event_handler()

            draw_table.append(current)
            while current.should_draw_bg:
                try:
                    current = states_copy.pop()
                    draw_table.append(current)
                except IndexError as e:
                    break

            draw_table.reverse()

            for draw in draw_table:
                draw.graphics_handler()

            conn_pygame_graphics.main()