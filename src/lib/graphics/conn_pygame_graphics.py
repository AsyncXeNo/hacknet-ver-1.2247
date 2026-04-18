from __future__ import annotations
import sys

import pygame

from typing import Optional
from lib.graphics.surfaces import Surface, SurfaceLayer
from lib.graphics.constants import IMAGE_PATH, DEFAULT_BOLD_FONT, DEFAULT_BOLDITALIC_FONT, DEFAULT_ITALIC_FONT, DEFAULT_REGULAR_FONT, BLACK
from loguru_config import get_subsystem_logger

logger = get_subsystem_logger('graphics.ConnPygameGraphics')


class ConnPygameGraphics(object):
    """Graphics handler at the outermost level"""

    def __init__(self, width: int, height: int, caption: str, fullscreen: bool = False) -> None:

        logger.info('Hello from ConnPygameGraphics!')

        pygame.init()

        # info: pygame.display._VidInfo = pygame.display.Info()

        self.width: int = width
        self.height: int = height
        self.caption: str = caption 

        logger.debug("Available Modes: {}", pygame.display.list_modes(32))

        self.window = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN if fullscreen else 0) 

        pygame.display.set_caption(self.caption)

        self.fonts: dict[str, str] = {
            'regular': DEFAULT_REGULAR_FONT,
            'italic': DEFAULT_ITALIC_FONT,
            'bold': DEFAULT_BOLD_FONT,
            'bolditalic': DEFAULT_BOLDITALIC_FONT,
        }
        self.render_queue: list[SurfaceLayer] = []

        self.image_path: str = IMAGE_PATH

    # Helpers

    def get_surface_by_id(self, surface_id: str) -> Surface:
        """Returns a surface with given id"""

        try:
            return list(filter(lambda surface: surface.ID == surface_id, self.render_queue))[0]
        except IndexError:
            logger.warning(f'Surface with ID {surface_id} not found. Ignoring request')

    def get_index(self, surface: Surface) -> int:
        """Returns the index of a passed in surface"""

        return self.render_queue.index(self.get_surface_by_id(surface.ID))

    def get_selected(self) -> Surface | None:
        """Returns the surface at the end of the render queue"""

        return self.render_queue[-1] if self.render_queue else None

    # Main

    def main(self) -> None:
        """Called on every iteration of the Game Loop"""

        self.window.fill(BLACK)

        for surface_layer in self.render_queue:
            frame = Surface((self.width, self.height), [0, 0])
            pygame.transform.scale(surface_layer.__surface, (self.width, self.height), frame)
            #TODO: LETTERBOX
            self.window.blit(frame, [0,0])

        pygame.display.update()

    # Queue Operations

    def push_surface(self, surface: Surface) -> None:
        """Pushes a surface to the render queue"""

        # rendered_surface =
        self.render_queue.append(surface.copy())

    def pop_surface(self) -> Surface:
        """Pops a surface from the render queue"""

        return self.render_queue.pop(0)

    def remove_surface(self, surface: Surface) -> None:
        """Removes a specific surface from the render queue"""

        for a in range(len(self.render_queue)):
            if self.render_queue[a].ID == surface.ID:
                self.render_queue.pop(a)

    def select_surface(self, surface: Surface) -> None:
        """Puts a render surface at the end of the queue"""

        surface = self.get_surface_by_id(surface.ID)
        self.render_queue.remove(surface)
        self.render_queue.append(surface)

    # Shapes

    def draw_line(self, color: tuple[int, int, int, int], start: tuple[int, int], end: tuple[int, int], width: int = 1, surface: Optional[Surface] = None) -> pygame.Rect:
        """Draws a line of given width (default 1) on a surface (default main window surface)"""

        if not surface:
            surface = self.window

        return pygame.draw.line(surface, color, start, end, width)

    def draw_lines(self, color: tuple[int, int, int, int], points: list[tuple[int, int]], width: int = 1, closed: bool = False, surface: Optional[Surface] = None) -> pygame.Rect:
        """Draws multiple lines on the screen with given width (default 1) connecting all the points in the given sequence on a surface (default main window surface)"""

        if not surface:
            surface = self.window

        return pygame.draw.lines(surface, color, closed, points, width)

    def draw_circle(self, color: tuple[int, int, int, int], center: tuple[int, int], radius: int, quadrants: int = 0b1111, width: int = 0, surface: Optional[Surface] = None) -> pygame.Rect:
        """Draws the specified quadrants of the circle (default 0b1111) on a surface (default main window surface)"""

        if not surface:
            surface = self.window

        quadrants = [bool(quadrants & 0b1000), bool(quadrants & 0b100), bool(quadrants & 0b10), bool(quadrants & 0b1)]

        return pygame.draw.circle(surface, color, center, radius, width, *quadrants)

    def draw_rect(self, color: tuple[int, int, int, int], rect_x: int, rect_y: int, rect_width: int, rect_height: int, width: int = 0, surface: Optional[Surface] = None) -> pygame.Rect:
        """Draws a rectangle with given dimensions on a surface (default main window surface)"""

        if not surface:
            surface = self.window

        return pygame.draw.rect(surface, color, pygame.Rect(rect_x, rect_y, rect_width, rect_height), width)

    def draw_polygon(self, color: tuple[int, int, int, int], points: list[tuple[int, int]], width: int = 0, surface: Optional[Surface] = None) -> pygame.Rect:
        """Draws a polygon using the given points on a surface (defualt main window surface)"""

        if not surface:
            surface = self.window

        return pygame.draw.polygon(surface, color, points, width)

    # Images

    def convert_to_pygame_image(self, name: str) -> Optional[pygame.Surface]:
        """Loads and returns a pygame image with given name"""

        try:
            image = pygame.image.load(f'{self.image_path}{name}')
        except FileNotFoundError:
            logger.error(f'Invalid image file path {self.image_path}{name}. Ignoring load request')
            return

        return image

    def blit_image(self, pos: tuple[int, int], image_name: str, width: int = 0, height: int = 0, surface: Optional[Surface] = None) -> Optional[pygame.Rect]:
        """Blits an image to a surface (default main window surface)"""

        if not surface:
            surface = self.window

        image = self.convert_to_pygame_image(image_name)

        if not image:
            logger.error('No image file found. Ignoring blit request')
            return

        image_size = (
            width if width > 0 else int(image.get_width()),
            height if height > 0 else int(image.get_height())
        )

        image = pygame.transform.scale(image, image_size)

        return surface.blit(image, pos)

    # Text

    def render_text(self, font_type: str, size: int, text: str, color: tuple[int, int, int, int], pos: tuple[int, int], background: Optional[tuple[int, int, int, int]] = None, surface: Optional[Surface] = None) -> Optional[pygame.Rect]:
        """Renders text on a surface (default main window surface)"""

        if not surface:
            surface = self.window

        try:
            font = pygame.font.Font(self.fonts[font_type], size)
        except KeyError:
            logger.error(f'Invalid font type {font_type}. Ignoring render request')
            return

        text = font.render(text, True, color, background)

        return surface.blit(text, pos)
