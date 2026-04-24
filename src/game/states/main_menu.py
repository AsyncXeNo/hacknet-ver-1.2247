import dataclasses
from pygame import FONT_CENTER
from pygame.color import Color
from pygame import Rect

from game.states.base import State
from graphics.constants import GAME_WIDTH, GAME_HEIGHT
from graphics.surfaces import Surface
from graphics.components.ui import draw_box, draw_text, draw_text_in_box
from graphics.components.style import Style, BorderConfig, TextConfig, Gap, AlignHor, AlignVer
from graphics.conn_pygame_graphics import conn_pygame_graphics
from assets_manager import FONTS
from loguru_config import get_subsystem_logger

logger = get_subsystem_logger('game.states.main_menu')


class MainMenuState(State):
    def __init__(self):
        super().__init__()
        self.surface_layer.surface.fill((0,0,0,255))
        
        self.main_rect = Surface((GAME_WIDTH * 0.8, GAME_HEIGHT * 0.8), (GAME_WIDTH * 0.1, GAME_HEIGHT * 0.1))
        self.surface_layer.push_surface(self.main_rect)

    def graphics_handler(self):
        default_text_config = TextConfig(align_x = AlignHor.CENTER,
                                         align_y = AlignVer.CENTER, 
                                         color = Color("white"), 
                                         font_align=FONT_CENTER, 
                                         font_path = FONTS.Krypton.Regular, 
                                         font_size = 22)
        with Style(
            text_config = default_text_config,
            border_config = BorderConfig(True, 20, 2, Color("white")),
            padding=Gap(0,0,0,0)
        ):
            w,h = self.main_rect.width, self.main_rect.height
            heading_text_config = dataclasses.replace(default_text_config, font_path= FONTS.Krypton.Bold, font_size=36, color=Color('red'))
            draw_box(surface=self.main_rect, rect=Rect(0, 0, w, h), fill_color=Color(15, 15, 15, 255))
            draw_text(surface=self.main_rect, rect=Rect(0, 0, w, h*0.4), text="HACKNET", text_config=heading_text_config)

            texts = ["New Game", "Continue", "Options", "Quit"]
            incr = h*0.15
            curr = h*0.35
            size_y = h*0.1
            x = w*(0.5-0.075)
            size_x = w*0.15
            
            for text in texts:
                draw_text_in_box(surface=self.main_rect, rect=Rect(x, curr, size_x, size_y), text=text, fill_color=Color("black"))
                curr += incr

        logger.debug('We just drew the main menu')
        return super().graphics_handler()

    def event_handler(self):
        return super().event_handler()