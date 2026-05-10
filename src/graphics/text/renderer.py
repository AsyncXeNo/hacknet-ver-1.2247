from __future__ import annotations
import dataclasses
from pathlib import Path
import re
from types import SimpleNamespace
from typing import NamedTuple
from pygame import Rect
from pygame.color import Color

from better_exceptions import LoggingException
from graphics.components.style import AlignHor
from graphics.constants import TEXT_ESCAPE_CHAR
from graphics.surfaces import Surface
from graphics.text.span import Span

from assets_manager import assets_manager
from game.manager import game_manager
from loguru_config import get_subsystem_logger
from copy import deepcopy

logger = get_subsystem_logger('graphics.text')


class TextOverflowException(LoggingException):
    def __init__(self, message, *args):
        super().__init__(logger, message, *args)


class InvalidVariable(LoggingException):
    def __init__(self, message, *args):
        super().__init__(logger, message, *args)


def constantize(raw_text: str, context_dict: SimpleNamespace) -> str:
    regex_pattern = re.compile(r'\{\{[^\ ]+?\}\}')

    matches: list[str] = regex_pattern.findall(raw_text)
    for var in matches:
        var_name = var.removeprefix('{{').removesuffix('}}')
        cur = context_dict
        for attr in var_name.split('.'):
            try:
                cur = getattr(cur, attr)
            except Exception as e:
                raise InvalidVariable(f'{var_name} is not a valid variable') from e

        raw_text = raw_text.replace(var, str(cur))
    
    return raw_text


def make_spans(raw_text: str, def_color: Color, def_size: int, def_font: Path, context_dict: SimpleNamespace | None) -> list[Span]:
    """
    Make spans from raw text
    Args:
        raw_text(str): There always has to be a space around \\n
    """
    if context_dict is None:
        context_dict = game_manager.states

    raw_text = constantize(raw_text, context_dict)
    if raw_text.startswith('\n'):
        raw_text = ' ' + raw_text
    while '\n\n' in raw_text:
        raw_text = raw_text.replace('\n\n', '\n  \n')

    words = [(x if x != '' else ' ') for x in raw_text.split(' ')]
    for word in words:
        assert '\n' not in word or word == '\n', 'Combination of \\n and normal text found. Illegal!'
    spans: list[Span] = []
    
    cur_color: Color = def_color
    cur_size: int = def_size
    cur_font: Path = def_font
    
    for word in words:
        if word.startswith(TEXT_ESCAPE_CHAR):
            code, val = word.removeprefix(TEXT_ESCAPE_CHAR + '[').removesuffix(']').split(':')
            match code:
                case 'f':
                    cur_font = def_font if val == 'reset' else Path(val)
                case 's':
                    cur_size = def_size if val == 'reset' else int(val)
                case 'sd':
                    cur_size = cur_size + int(val)
                case 'c':
                    cur_color = def_color if val == 'reset' else Color(*map(int, val.split(',')))
        else:
            spans.append(Span(word, cur_color, cur_size, cur_font))

    return spans


class PreRenderRes(NamedTuple):
    lines: list[list[Surface]]
    max_heights: list[int]


def pre_render(spans: list[Span], max_w: int) -> PreRenderRes:
    cur_x = 0

    lines = []
    current_line = []

    for idx, span in enumerate(spans):

        if span.text == '\n':
            if not current_line: continue
            lines.append(current_line.copy())
            current_line = []
            cur_x = 0
            continue
        
        # span
        raw_surface = assets_manager.get_font(span.font, span.font_size).render(span.text)
        span_surface = Surface.from_pygame_surface(raw_surface, [cur_x,0])
        span_width = span_surface.width
        
        if cur_x + span_width <= max_w:
            current_line.append(span_surface)
            cur_x += span_width

        elif len(current_line) == 0:
            raise TextOverflowException('Text overflows')

        else:
            lines.append(current_line.copy())
            current_line = []
            span_surface.pos = [0, 0]
            current_line.append(span_surface)
            cur_x = span_width

        # space
        if span.text == ' ' or idx == len(spans) - 1:
            continue

        raw_space_surface = assets_manager.get_font(span.font, span.font_size).render(' ')
        space_surface = Surface.from_pygame_surface(raw_space_surface, [cur_x, 0])
        space_width = space_surface.width
        if cur_x + space_width <= max_w:
            current_line.append(space_surface)
            cur_x += space_width
        else:
            lines.append(current_line.copy())
            current_line = []
            cur_x = 0

    if current_line: lines.append(current_line)
            
    max_heights = [max(map(lambda surface: surface.height, line)) for line in lines]
    
    return PreRenderRes(lines, max_heights)


def render_rich_text(spans: list[Span] | PreRenderRes, max_size: Rect | int, align_x: AlignHor, gap_y: int) -> Surface:
    max_w, max_h = (max_size.w, max_size.h) if isinstance(max_size, Rect) else (max_size, None)

    spans: PreRenderRes = pre_render(spans, max_w) if not isinstance(spans, PreRenderRes) else spans
    assert isinstance(spans, PreRenderRes), 'What the hell is spans then?!'

    surf_height = sum(spans.max_heights) + gap_y * max(len(spans.max_heights) - 1, 0) 
    
    if max_h is not None and surf_height > max_h:
        raise TextOverflowException('Text overflows')

    text_surface = Surface((max_w, surf_height), [0, 0])

    line_surfaces: list[Surface] = []
    cur_y = 0
    for line, height in zip(spans.lines, spans.max_heights):
        total_width = sum(map(lambda surface: surface.width, line), 0)
        line_surf = Surface((total_width, height), [0, cur_y])
        for surf in line:
            line_surf.blit(surf, (surf.pos[0], line_surf.height - surf.height))
        line_surfaces.append(line_surf)
        cur_y += height + gap_y

    for line in line_surfaces:
        leftover = text_surface.width - line.width
        match align_x:
            case AlignHor.LEFT:
                text_surface.blit(line, line.pos)
            case AlignHor.CENTER:
                text_surface.blit(line, (leftover / 2, line.pos[1]))
            case AlignHor.RIGHT:
                text_surface.blit(line, (leftover, line.pos[1]))

    return text_surface