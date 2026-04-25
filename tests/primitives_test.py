from __future__ import annotations

from pathlib import Path

import pygame
import pytest
from pygame import Rect
from pygame.color import Color

pygame.display.init()


@pytest.fixture(scope='module', autouse=True)
def _display():
    pygame.display.set_mode((1, 1))
    yield
    pygame.display.quit()


from graphics.components.primitives import (
    _draw_box, _draw_text, _draw_text_in_box,
    draw_box, draw_text, draw_text_in_box,
)
from graphics.components.style import (
    AlignHor, AlignVer, BorderConfig, Gap, Style, TextConfig,
)
from graphics.surfaces import Surface


REAL_FONT = Path(__file__).parent.parent / 'assets' / 'fonts' / 'Krypton' / 'Regular.ttf'


@pytest.fixture
def surface():
    return Surface((200, 200), [0, 0])


# ─── _draw_box ───────────────────────────────────────────────────────────────


class TestDrawBox:
    def test_fill_color_painted_inside(self, surface):
        rect = Rect(0, 0, 50, 50)
        _draw_box(surface, rect, BorderConfig(False, 0, None, None), Color(10, 20, 30, 255))
        assert surface.get_at((25, 25))[:3] == (10, 20, 30)

    def test_border_drawn_when_enabled(self, surface):
        rect = Rect(10, 10, 100, 100)
        _draw_box(surface, rect,
                  BorderConfig(True, 0, 2, Color(255, 0, 0, 255)),
                  Color(0, 0, 0, 255))
        # border edge sample - at the top edge of the rect
        assert surface.get_at((10, 10))[:3] == (255, 0, 0)
        # interior should still be the fill color
        assert surface.get_at((50, 50))[:3] == (0, 0, 0)


# ─── _draw_text ──────────────────────────────────────────────────────────────


class TestDrawText:
    def _config(self, **overrides):
        defaults = dict(
            align_x=AlignHor.LEFT, align_y=AlignVer.TOP,
            color=Color(255, 255, 255), font_align=0,
            font_path=REAL_FONT, font_size=14,
        )
        defaults.update(overrides)
        return TextConfig(**defaults)

    def test_renders_visible_pixels(self, surface):
        rect = Rect(0, 0, 100, 30)
        _draw_text(surface, rect, "Hi", self._config(), Gap(0, 0, 0, 0))
        # Some pixels in the rect should now be non-zero
        any_white = any(
            surface.get_at((x, y))[:3] == (255, 255, 255)
            for x in range(rect.width) for y in range(rect.height)
        )
        assert any_white

    def test_empty_text_asserts(self, surface):
        with pytest.raises(AssertionError):
            _draw_text(surface, Rect(0, 0, 100, 30), "",
                       self._config(), Gap(0, 0, 0, 0))

    def test_missing_text_config_value_asserts(self, surface):
        bad = self._config(color=None)
        with pytest.raises(AssertionError):
            _draw_text(surface, Rect(0, 0, 100, 30), "Hi", bad, Gap(0, 0, 0, 0))


# ─── _draw_text_in_box ───────────────────────────────────────────────────────


class TestDrawTextInBox:
    def _config(self):
        return TextConfig(
            AlignHor.CENTER, AlignVer.CENTER,
            Color(255, 255, 255), 0,
            REAL_FONT, 14,
        )

    def test_box_then_text(self, surface):
        rect = Rect(20, 20, 80, 40)
        _draw_text_in_box(
            surface, rect, "OK",
            self._config(),
            BorderConfig(False, 0, None, None),
            Color(0, 0, 0, 255),
            Gap(0, 0, 0, 0),
        )
        # background filled
        assert surface.get_at((25, 25))[:3] == (0, 0, 0)
        # has at least one text pixel inside
        text_pixels = sum(
            1 for x in range(rect.left, rect.right)
            for y in range(rect.top, rect.bottom)
            if surface.get_at((x, y))[:3] == (255, 255, 255)
        )
        assert text_pixels > 0

    def test_empty_text_skipped_no_assert(self, surface):
        """Composite skips text drawing on empty string."""
        _draw_text_in_box(
            surface, Rect(0, 0, 50, 30), "",
            self._config(),
            BorderConfig(False, 0, None, None),
            Color(5, 5, 5, 255),
            Gap(0, 0, 0, 0),
        )


# ─── styled wrappers ─────────────────────────────────────────────────────────


class TestStyledWiring:
    def test_styled_pulls_kwargs_from_active_style(self, surface):
        rect = Rect(0, 0, 30, 30)
        with Style(border_config=BorderConfig(False, 0, None, None),
                   fill_color=Color(50, 100, 150, 255)):
            draw_box(surface, rect)
        assert surface.get_at((10, 10))[:3] == (50, 100, 150)
