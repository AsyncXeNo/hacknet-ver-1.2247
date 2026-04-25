from __future__ import annotations
import math
from typing import TypeVar
from typing import TYPE_CHECKING
from contextlib import ContextDecorator
from enum import Enum
from functools import wraps
import dataclasses
from dataclasses import dataclass

from pygame import Rect

from loguru_config import get_subsystem_logger

if TYPE_CHECKING:
    from pathlib import Path

from pygame.color import Color


logger = get_subsystem_logger('graphics.components')


T = TypeVar('T')


class AlignHor(Enum):
    LEFT=0
    CENTER=1
    RIGHT=2

class AlignVer(Enum):
    TOP=0
    CENTER=1
    BOTTOM=2


@dataclass
class TextConfig():
    align_x: AlignHor | None
    align_y: AlignVer | None
    color: Color | None
    font_align: int
    font_path: Path | None
    font_size: int | None


@dataclass
class Gap():
    l: int
    r: int
    t: int
    b: int

    @property
    def x(self):
        return self.l + self.r
    
    @property
    def y(self):
        return self.t + self.b

    def __post_init__(self):
        self.l = self.l or 0
        self.r = self.r or 0
        self.t = self.t or 0
        self.b = self.b or 0


@dataclass
class BorderConfig():
    border: bool
    radius: int
    width: int | None
    color: Color | None

    def __post_init__(self):
        first_case = self.border and self.width is not None and self.color is not None
        second_case = not self.border and (self.width is None and self.color is None)
        assert first_case or second_case, "Drawing of border doesn't correspond with values"


def lerp(a: T, b: T, t: float):
    assert 0.0 <= t <= 1.0, 't should be between 0 and 1'
    assert type(a) == type(b), 'a and b should be same type when lerping'
    if isinstance(a, (int, float)):
        return type(a)((1 - t) * a + t * b)
    if isinstance(a, Color):
        return a.lerp(b, t)
    if isinstance(a, Gap):
        return Gap(lerp(a.l, b.l, t), 
                   lerp(a.r, b.r, t),
                   lerp(a.t, b.t, t),
                   lerp(a.b, b.b, t))
    if isinstance(a, BorderConfig):
        assert a.border == b.border
        return BorderConfig(a.border, 
                            lerp(a.radius, b.radius, t), 
                            lerp(a.width, b.width, t), 
                            lerp(a.color, b.color, t))

    if isinstance(a, TextConfig):
        assert a.align_x == b.align_x, "align_x is not the same"
        assert a.align_y == b.align_y, "align_y is not the same"
        assert a.font_align == b.font_align, "font_align is not the same"
        assert a.font_path == b.font_path, "font_path is not the same"

        res = dataclasses.replace(a, color=lerp(a.color, b.color, t), font_size=lerp(a.font_size, b.font_size, t))
        return res

    if isinstance(a, Rect):
        return Rect(lerp(a.x, b.x, t), 
                    lerp(a.y, b.y, t), 
                    lerp(a.w, b.w, t), 
                    lerp(a.h, b.h, t))

_style_stack: list[dict] = []


class Style(ContextDecorator):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __enter__(self):
        _style_stack.append(self.kwargs)

    def __exit__(self, exc_type, exc, tb):
        _style_stack.pop()


def styled(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        merged = {}

        # earlier styles should be overridden by later ones
        for layer in _style_stack:
            merged.update(layer)

        # explicit call arguments win
        merged.update(kwargs)

        return fn(*args, **merged)

    return wrapper