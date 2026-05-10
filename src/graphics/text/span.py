from pathlib import Path

from pygame import Color
from dataclasses import dataclass


@dataclass(frozen=True)
class Span(object):
    '''Represents one word or a space or \\n'''
    text: str
    color: Color
    font_size: int
    font: Path