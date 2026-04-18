from copy import copy

from game.states.base import State
from game.states.main_menu import MainMenuState
from lib.graphics.conn_pygame_graphics import ConnPygameGraphics

import pygame


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
        self.state_stack: list[State] = [
            MainMenuState()
        ]

        self.conn_pygame_graphics: ConnPygameGraphics = ConnPygameGraphics(1280, 720, 'Hacknet')

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

            self.conn_pygame_graphics.main()