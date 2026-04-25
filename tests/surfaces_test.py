from __future__ import annotations

import pygame
import pytest

from graphics.surfaces import Surface
from graphics.constants import TITLEBAR_DEFAULT_HEIGHT


pygame.display.init()


@pytest.fixture(scope='module', autouse=True)
def _display():
    pygame.display.set_mode((1, 1))
    yield
    pygame.display.quit()


class TestSurfaceConstruction:
    def test_inherits_from_pygame_surface(self):
        s = Surface((100, 50), [10, 20])
        assert isinstance(s, pygame.Surface)

    def test_size_propagated(self):
        s = Surface((100, 50), [0, 0])
        assert s.get_size() == (100, 50)

    def test_pos_stored(self):
        s = Surface((20, 20), [3, 7])
        assert s.pos == [3, 7]

    def test_id_is_prefixed_string(self):
        s = Surface((10, 10), [0, 0])
        assert s.ID.startswith('SURFACE-')
        assert len(s.ID) > len('SURFACE-')

    def test_two_surfaces_have_different_ids(self):
        a = Surface((10, 10), [0, 0])
        b = Surface((10, 10), [0, 0])
        assert a.ID != b.ID

    def test_uses_srcalpha(self):
        s = Surface((10, 10), [0, 0])
        assert s.get_flags() & pygame.SRCALPHA

    def test_pixels_writable(self):
        s = Surface((4, 4), [0, 0])
        s.fill((10, 20, 30, 255))
        assert s.get_at((0, 0))[:3] == (10, 20, 30)


class TestSurfaceRange:
    def test_range_with_titlebar(self):
        s = Surface((100, 50), [10, 20])
        top_left, bottom_right = s.get_surface_range(include_titlebar=True)
        assert top_left == [10, 20]
        assert bottom_right == [110, 70]

    def test_range_default_includes_titlebar(self):
        s = Surface((100, 50), [10, 20])
        assert s.get_surface_range() == s.get_surface_range(include_titlebar=True)

    def test_range_without_titlebar(self):
        s = Surface((100, 50), [10, 20])
        top_left, bottom_right = s.get_surface_range(include_titlebar=False)
        assert top_left == [10, 20 + TITLEBAR_DEFAULT_HEIGHT]
        assert bottom_right == [110, 20 + 50 - TITLEBAR_DEFAULT_HEIGHT]
