from __future__ import annotations

import pygame
import pytest
from pygame import Rect, Color
from pygame.event import Event

pygame.display.init()


@pytest.fixture(scope='module', autouse=True)
def _display():
    pygame.display.set_mode((1, 1))
    yield
    pygame.display.quit()


from graphics.components.ui import (
    AnimType,
    Box, Button, ButtonStyle, BoxStyle,
    Component, Label, LabelStyle,
)
from graphics.components.style import (
    AlignHor, AlignVer, BorderConfig, Gap, TextConfig,
)
from graphics.surfaces import Surface
from game.timer import game_timer


@pytest.fixture(autouse=True)
def _reset_game_timer():
    game_timer.update_time(0)
    yield
    game_timer.update_time(0)


# ─── AnimType ────────────────────────────────────────────────────────────────


class TestAnimType:
    def test_initial_val_is_a(self):
        anim = AnimType(0, 100, ms=200)
        assert anim.val == 0
        assert anim.t == 0.0

    def test_delta_advances_t(self):
        anim = AnimType(0, 100, ms=200)
        anim.delta(100)
        assert anim.t == pytest.approx(0.5)

    def test_delta_lerps_value(self):
        anim = AnimType(0, 100, ms=200)
        anim.delta(100)
        assert anim.val == 50

    def test_delta_clamps_at_one(self):
        anim = AnimType(0, 100, ms=200)
        anim.delta(10_000)
        assert anim.t == 1.0
        assert anim.val == 100

    def test_negative_delta_clamps_at_zero(self):
        anim = AnimType(0, 100, ms=200)
        anim.delta(100)
        anim.delta(-10_000)
        assert anim.t == 0.0
        assert anim.val == 0

    def test_color_animation(self):
        anim = AnimType(Color(0, 0, 0), Color(200, 200, 200), ms=200)
        anim.delta(100)
        assert anim.val.r == 100


# ─── AnimComponentProperty (via ButtonStyle) ─────────────────────────────────


class TestButtonStyleAccess:
    def _make(self, fill=Color(0, 0, 0)):
        return ButtonStyle(
            Rect(0, 0, 50, 20),
            AnimType(fill, Color(255, 255, 255), ms=200),
            TextConfig(AlignHor.CENTER, AlignVer.CENTER, Color(255, 255, 255), 0, None, 10),
            BorderConfig(False, 0, None, None),
            Gap(0, 0, 0, 0),
        )

    def test_public_attribute_returns_anim_val(self):
        s = self._make(fill=Color(10, 20, 30))
        assert s.fill_color.r == 10

    def test_public_rect_returns_underlying_rect(self):
        s = self._make()
        assert s.rect == Rect(0, 0, 50, 20)

    def test_delta_propagates_to_anim_fields(self):
        s = self._make(fill=Color(0, 0, 0))
        s.delta(200)
        assert s.fill_color.r == 255  # animation fully advanced

    def test_static_field_is_returned_as_is(self):
        s = self._make()
        assert isinstance(s.border_config, BorderConfig)


# ─── Component base ──────────────────────────────────────────────────────────


class _NullComponent(Component):
    def __init__(self, parent_surface, rect):
        super().__init__(parent_surface, rect)
        self.events_seen = []
        self.draws = 0

    def events_handler(self, events, mouse_offset):
        self.events_seen.append((list(events), mouse_offset))
        return super().events_handler(events, mouse_offset)

    def graphics_handler(self):
        self.draws += 1
        return super().graphics_handler()


class TestComponentBase:
    @pytest.fixture
    def parent(self):
        return Surface((200, 200), [0, 0])

    def test_initial_hovered_is_false(self, parent):
        c = _NullComponent(parent, lambda: Rect(0, 0, 10, 10))
        assert c.hovered is False

    def test_add_component_appends(self, parent):
        c = _NullComponent(parent, lambda: Rect(0, 0, 10, 10))
        child = _NullComponent(parent, lambda: Rect(0, 0, 5, 5))
        c.add_component('child', child)
        assert c.components.child is child

    def test_events_dispatch_to_children_with_offset(self, parent):
        c = _NullComponent(parent, lambda: Rect(0, 0, 100, 100))
        child = _NullComponent(parent, lambda: Rect(15, 25, 10, 10))
        c.add_component('child', child)
        c.events_handler([], (0, 0))
        assert child.events_seen[-1][1] == (15, 25)

    def test_graphics_dispatch_to_children(self, parent):
        c = _NullComponent(parent, lambda: Rect(0, 0, 10, 10))
        child = _NullComponent(parent, lambda: Rect(0, 0, 5, 5))
        c.add_component('child', child)
        c.graphics_handler()
        assert child.draws == 1


# ─── Box ─────────────────────────────────────────────────────────────────────


class TestBox:
    def test_construction(self):
        """BoxStyle is currently a stub; Box.__init__ stores the style and a
        deferred lambda over style.rect, so construction should succeed even
        without any concrete fields."""
        parent = Surface((50, 50), [0, 0])
        b = Box(parent, BoxStyle())
        assert b.parent_surface is parent
        assert b.style.__class__ is BoxStyle


# ─── Button ──────────────────────────────────────────────────────────────────


def _button(parent, on_click=lambda b: None, on_hover=lambda b: None,
            rect=Rect(10, 10, 50, 20)):
    style = ButtonStyle(
        rect,
        AnimType(Color(0, 0, 0), Color(255, 255, 255), ms=200),
        TextConfig(AlignHor.CENTER, AlignVer.CENTER, Color(255, 255, 255), 0, None, 10),
        BorderConfig(False, 0, None, None),
        Gap(0, 0, 0, 0),
    )
    return Button(parent, "Hi", style, on_click, on_hover)


class TestButtonInteraction:
    @pytest.fixture
    def parent(self):
        return Surface((200, 200), [0, 0])

    def test_initial_hovered_false(self, parent):
        b = _button(parent)
        assert b.hovered is False

    def test_hover_callback_fires_once(self, parent, monkeypatch):
        calls = []
        b = _button(parent, on_hover=lambda btn: calls.append(btn))
        # mouse_offset is the rect's position; mouse local coords inside rect
        # require raw_mouse - rect.pos to be in (0, rect.w) x (0, rect.h).
        rect = b.style.rect
        monkeypatch.setattr(pygame.mouse, 'get_pos', lambda: (rect.x + 1, rect.y + 1))

        b.events_handler([], (rect.x, rect.y))
        b.events_handler([], (rect.x, rect.y))
        assert len(calls) == 1
        assert b.hovered is True

    def test_hover_resets_when_mouse_leaves(self, parent, monkeypatch):
        b = _button(parent)
        rect = b.style.rect
        monkeypatch.setattr(pygame.mouse, 'get_pos', lambda: (rect.x + 1, rect.y + 1))
        b.events_handler([], (rect.x, rect.y))
        assert b.hovered

        monkeypatch.setattr(pygame.mouse, 'get_pos', lambda: (10_000, 10_000))
        b.events_handler([], (rect.x, rect.y))
        assert b.hovered is False

    def test_click_inside_fires_callback(self, parent, monkeypatch):
        clicks = []
        b = _button(parent, on_click=lambda btn: clicks.append(btn))
        rect = b.style.rect
        monkeypatch.setattr(pygame.mouse, 'get_pos', lambda: (rect.x + 1, rect.y + 1))

        click = Event(pygame.MOUSEBUTTONUP, {'button': 1, 'pos': (rect.x + 1, rect.y + 1)})
        b.events_handler([click], (rect.x, rect.y))
        assert len(clicks) == 1

    def test_click_outside_does_not_fire(self, parent, monkeypatch):
        clicks = []
        b = _button(parent, on_click=lambda btn: clicks.append(btn))
        rect = b.style.rect
        monkeypatch.setattr(pygame.mouse, 'get_pos', lambda: (10_000, 10_000))

        click = Event(pygame.MOUSEBUTTONUP, {'button': 1, 'pos': (10_000, 10_000)})
        b.events_handler([click], (rect.x, rect.y))
        assert clicks == []

    def test_hover_advances_animation(self, parent, monkeypatch):
        b = _button(parent)
        rect = b.style.rect
        monkeypatch.setattr(pygame.mouse, 'get_pos', lambda: (rect.x + 1, rect.y + 1))

        # Component's last_update was set to game_timer.time_ms (0) at construction.
        # Advancing the timer by 0.2s gives time_ms=200, so dx=200 fully
        # advances the AnimType (ms=200).
        game_timer.update_time(0.2)
        b.events_handler([], (rect.x, rect.y))
        assert b.style.fill_color.r == 255


# ─── Label ───────────────────────────────────────────────────────────────────


def _label(parent, rect=Rect(10, 10, 50, 20)):
    style = LabelStyle(
        rect,
        TextConfig(AlignHor.CENTER, AlignVer.CENTER, Color(255, 255, 255), 0, None, 10),
        Gap(0, 0, 0, 0),
    )
    return Label(parent, "hi", style)


class TestLabel:
    @pytest.fixture
    def parent(self):
        return Surface((200, 200), [0, 0])

    def test_construction(self, parent):
        lab = _label(parent)
        assert lab.text == "hi"
        assert isinstance(lab.style, LabelStyle)

    def test_events_handler_runs_without_error(self, parent, monkeypatch):
        lab = _label(parent)
        monkeypatch.setattr(pygame.mouse, 'get_pos', lambda: (0, 0))
        lab.events_handler([], (0, 0))
