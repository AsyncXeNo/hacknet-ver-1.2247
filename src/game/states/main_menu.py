import dataclasses
from pygame import FONT_CENTER, Event
import pygame
from pygame.color import Color
from pygame import Rect

from game.states.base import State
from game.states.rl import RLState
from graphics.constants import GAME_WIDTH, GAME_HEIGHT
from graphics.surfaces import Surface
from graphics.components.primitives import draw_box, draw_text, draw_text_in_box
from graphics.components.style import Style, BorderConfig, TextConfig, Gap, AlignHor, AlignVer
from graphics.components.ui import Button, Label, ButtonStyle, LabelStyle, AnimType
from game.manager import game_manager

from assets_manager import FONTS
from loguru_config import get_subsystem_logger

logger = get_subsystem_logger('game.states.main_menu')


def new_game(_):
    game_manager.pop_state()
    game_manager.push_state(RLState())


class MainMenuState(State):
    def __init__(self):
        super().__init__()
        
        w,h = GAME_WIDTH, GAME_HEIGHT

        default_text_config = TextConfig(AlignHor.CENTER, AlignVer.CENTER, Color("white"), pygame.FONT_CENTER, FONTS.Krypton.Regular, 16)

        heading_text_config = dataclasses.replace(default_text_config, font_path= FONTS.Krypton.Bold, font_size=36, color=Color('red'))
        label_style = LabelStyle(Rect(0, 0, w, h*0.4), heading_text_config, Gap(0,0,0,0))
        self.add_component('title', Label(self.main_surface, "HACKNET", label_style))

        texts = ["New Game", "Continue", "Options", "Quit"]
        incr = h * 0.10
        curr = h * 0.40
        size_y = h * 0.05
        x = w * (0.5 - 0.05)
        size_x = w * 0.10
        
        for i, text in enumerate(texts):
            border_config = BorderConfig(True, 20, 2, Color(100, 0, 0, 255))
            text_config = AnimType(default_text_config, dataclasses.replace(default_text_config, color=Color("black")), 100)
            button_style = ButtonStyle(Rect(x, curr, size_x, size_y),
                                       AnimType(Color(15, 15, 15, 255), Color(240, 240, 255), 100),
                                       text_config,
                                       border_config,
                                       Gap(0, 0, 0, 0))
            curr += incr
            self.add_component(text.lower().replace(' ', '_') + "_button", Button(self.main_surface, 
                                      text, 
                                      button_style, 
                                      new_game if i == 0 else lambda button: None, 
                                      lambda button: None))

    def graphics_handler(self):
        super().graphics_handler()

    def events_handler(self, events: list[Event]):
        super().events_handler(events)