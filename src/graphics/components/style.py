from __future__ import annotations
from typing import TYPE_CHECKING
from contextlib import ContextDecorator
from enum import Enum
from functools import wraps
from dataclasses import dataclass

if TYPE_CHECKING:
    from pathlib import Path
    from pygame.color import Color

from assets_manager import assets_manager


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