from types import SimpleNamespace
from typing import Union
from pathlib import Path
from pygame.color import Color

# Colors
WHITE: Color = Color(255, 255, 255, 255)
BETTER_WHITE: Color = Color(215, 215, 215, 255)
BLACK: Color = Color(0, 0, 0, 255)
RED: Color = Color(255, 0, 0, 255)
TRANSPARENT: Color = Color(0, 0, 0, 0)

# Title Bar
TITLEBAR_OPTIONS_PATH: str = 'application/titlebar_options.png'
TITLEBAR_OPTIONS_DIMENSIONS: tuple[int, int] = (2, 1)  # width, height

TITLEBAR_1PX_PATH: str = 'application/titlebar_1px.png'
TITLEBAR_1PX_DIMENSIONS: tuple[int, int] = (1, 4)  # width, height

TITLEBAR_DEFAULT_HEIGHT: int = 30

# General
RESOLUTION: tuple[int, int] = (1366, 768) 

APPLICATION_MIN_WIDTH = 100
APPLICATION_MIN_HEIGHT = 100

# Formatting

CODE_FORMATTING: SimpleNamespace = SimpleNamespace(
    COLOR_CHANGE = lambda color: f'⸸[c:{color.r},{color.g},{color.b},{color.a}]',
    COLOR_RESET = lambda: '⸸[c:reset}',

    SIZE_CHANGE = lambda size: f'⸸[s:{size}]', 
    SIZE_DIFF = lambda delta: f'⸸[sd:{delta}]', 
    SIZE_RESET = lambda: '⸸[s:reset]',
    
    FONT_CHANGE = lambda font: f'⸸[f:{font}]',
    FONT_RESET = lambda: '⸸[f:reset]',

    RESET= lambda: '⸸[c:reset] ⸸[f:reset] ⸸[s:reset]'
)

TEXT_ESCAPE_CHAR: str = '⸸'


# Assets
ASSETS_PATH: Path = Path('./assets')
IMAGE_PATH: Path = ASSETS_PATH / 'images'
AUDIOS_PATH: Path = ASSETS_PATH / 'audios'
FONTS_PATH: Path = ASSETS_PATH / 'fonts'

# Font Variations
FONT_VARIATIONS: list[str] = ['Light.ttf', 'LightItalic.ttf',
                              'Regular.ttf', 'RegularItalic.ttf', 
                              'Medium.ttf', 'MediumItalic.ttf',
                              'SemiBold.ttf', 'SemiBoldItalic.ttf',
                              'Bold.ttf', 'BoldItalic.ttf', 
                              'Black.ttf', 'BlackItalic.ttf']

# Applications
WINDOW_OUTLINE_COLOR: tuple[int, int, int, int] = (65, 65, 65, 255)

SCROLLBAR_WIDTH: int = 15

# Message Box
MESSAGE_BOX_DIMENSIONS: tuple[int, int] = (320, 160)
MESSAGE_BOX_PADDING: tuple[int, int] = (10, 10)
MESSAGE_BOX_FONT_SIZE: int = 20
MESSAGE_BOX_TEXT_COLOR: tuple[int, int, int, int] = (255, 46, 99, 255)
MESSAGE_BOX_BGCOLOR: tuple[int, int, int, int] = (30, 30, 30, 250)
MESSAGE_BOX_OUTLINE_COLOR: tuple[int, int, int, int] = (65, 65, 65, 255)
MESSAGE_BOX_TIME: int = 3

# TTY
TTY_FONT_SIZE: int = 20
TTY_TEXT_PADDING: tuple[int, int] = (3, 3)

GAME_WIDTH = 1280
GAME_HEIGHT = 720

FPS = 30