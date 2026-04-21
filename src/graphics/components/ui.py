from __future__ import annotations

from typing import TYPE_CHECKING

from loguru_config import get_subsystem_logger

if TYPE_CHECKING:
    from pygame import Rect
    from graphics.surfaces import Surface

from graphics.components.style import TextConfig, BorderConfig, Gap, AlignHor, AlignVer

from dataclasses import asdict, dataclass
from enum import Enum
from pygame import draw
from pygame.color import Color

from graphics.components.style import styled
from assets_manager import assets_manager


logger = get_subsystem_logger('graphics.components.ui')


def _draw_box(surface: Surface, 
             rect: Rect, 
             border_config: BorderConfig, 
             fill_color: Color, **kwargs):

    draw.rect(surface, fill_color, rect, width=0, border_radius=border_config.radius)
    
    if border_config.border:
        draw.rect(surface, border_config.color, rect, width=border_config.width, border_radius=border_config.radius)


def _draw_text(surface: Surface, 
              rect: Rect,
              text: str, 
              text_config: TextConfig, 
              padding: Gap, **kwargs):

    assert text, 'Text is needed'
    assert all(map(lambda x: x is not None, asdict(text_config).values())), "Need all text config values if text is present"

    logger.debug(f"{text_config.font_path}")
    font = assets_manager.get_font(text_config.font_path, text_config.font_size)
    font.align = text_config.font_align

    available_width = rect.width - padding.x
    available_height = rect.height - padding.y

    logger.debug(f"{font} - {text} - {text_config.color}")
    text_surf = font.render(text, True, text_config.color, None, available_width).convert_alpha()
    logger.debug(f"font color is {text_config.color}")
    text_rect = text_surf.get_rect()

    assert text_rect.width <= available_width and text_rect.height <= available_height, 'Text doesnt fit inside the button.'

    left = rect.x + padding.l
    right = rect.x + rect.w - padding.r

    top = rect.y + padding.t
    bottom = rect.y + rect.h - padding.b
    
    center_x = rect.x + rect.w / 2
    center_y = rect.y + rect.h / 2

    match (text_config.align_x, text_config.align_y):
        case (AlignHor.LEFT, AlignVer.TOP):
            text_rect.topleft = (left, top)
        case (AlignHor.LEFT, AlignVer.CENTER):
            text_rect.midleft = (left, center_y)
        case (AlignHor.LEFT, AlignVer.BOTTOM):
            text_rect.bottomleft = (left, bottom)
        case (AlignHor.CENTER, AlignVer.TOP):
            text_rect.midtop = (center_x, top)
        case (AlignHor.CENTER, AlignVer.CENTER):
            text_rect.center = (center_x, center_y)
        case (AlignHor.CENTER, AlignVer.BOTTOM):
            text_rect.midbottom = (center_x, bottom)
        case (AlignHor.RIGHT, AlignVer.TOP):
            text_rect.topright = (right, top)
        case (AlignHor.RIGHT, AlignVer.CENTER):
            text_rect.midright = (right, center_y)
        case (AlignHor.RIGHT, AlignVer.BOTTOM):
            text_rect.bottomright = (right, bottom)

    surface.blit(text_surf, text_rect)


def _draw_text_in_box(surface: Surface, 
                     rect: Rect, 
                     text: str,
                     text_config: TextConfig,
                     border_config: BorderConfig, 
                     fill_color: Color,
                     padding: Gap, **kwargs) -> None:

    _draw_box(surface, rect, border_config, fill_color)
    
    if text:
        _draw_text(surface, rect, text, text_config, padding)


draw_box = styled(_draw_box)
draw_text = styled(_draw_text)
draw_text_in_box = styled(_draw_text_in_box)