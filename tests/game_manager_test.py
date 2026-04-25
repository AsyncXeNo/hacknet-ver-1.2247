from __future__ import annotations

import pygame
import pytest

pygame.display.init()


@pytest.fixture(scope='module', autouse=True)
def _display():
    pygame.display.set_mode((1, 1))
    yield
    pygame.display.quit()


from game.manager import GameManager, game_manager
from game.states.base import State
from graphics.constants import GAME_WIDTH, GAME_HEIGHT
from graphics.conn_pygame_graphics import conn_pygame_graphics


# ─── State base ──────────────────────────────────────────────────────────────


class _ConcreteState(State):
    pass


class _OtherState(State):
    pass


class TestStateBase:
    def test_main_surface_is_game_sized(self):
        s = _ConcreteState()
        assert s.main_surface.get_size() == (GAME_WIDTH, GAME_HEIGHT)

    def test_should_draw_bg_default_false(self):
        s = _ConcreteState()
        assert s.should_draw_bg is False

    def test_should_draw_bg_kwarg(self):
        s = _ConcreteState(should_draw_bg=True)
        assert s.should_draw_bg is True

    def test_components_starts_empty(self):
        s = _ConcreteState()
        assert s.components == []

    def test_add_component_appends(self):
        s = _ConcreteState()
        marker = object()
        s.add_component(marker)
        assert marker in s.components


# ─── GameManager ─────────────────────────────────────────────────────────────


@pytest.fixture
def gm():
    """A fresh GameManager that doesn't leak state into the global one."""
    mgr = GameManager()
    yield mgr
    while mgr.state_stack:
        mgr.pop_state()


class TestGameManagerStack:
    def test_push_appends(self, gm):
        s = _ConcreteState()
        gm.push_state(s)
        assert gm.state_stack[-1] is s

    def test_push_syncs_to_graphics(self, gm):
        s = _ConcreteState()
        gm.push_state(s)
        assert s in conn_pygame_graphics.render_queue

    def test_push_duplicate_class_asserts(self, gm):
        gm.push_state(_ConcreteState())
        with pytest.raises(AssertionError):
            gm.push_state(_ConcreteState())

    def test_push_different_class_ok(self, gm):
        gm.push_state(_ConcreteState())
        gm.push_state(_OtherState())
        assert len(gm.state_stack) == 2

    def test_pop_returns_top(self, gm):
        a = _ConcreteState()
        b = _OtherState()
        gm.push_state(a)
        gm.push_state(b)
        assert gm.pop_state() is b
        assert gm.state_stack == [a]

    def test_pop_removes_from_graphics(self, gm):
        s = _ConcreteState()
        gm.push_state(s)
        gm.pop_state()
        assert s not in conn_pygame_graphics.render_queue


class TestGameManagerSingleton:
    def test_module_singleton_is_a_game_manager(self):
        assert isinstance(game_manager, GameManager)


# ─── main_loop ───────────────────────────────────────────────────────────────


class _RecordingState(State):
    """State that counts how many event-frames it processed."""
    def __init__(self):
        super().__init__()
        self.tick_count = 0

    def events_handler(self, events):
        self.tick_count += 1
        return super().events_handler(events)


class TestMainLoopExit:
    def test_quit_event_terminates_loop(self, gm, monkeypatch):
        """A QUIT event in the second frame should cause main_loop to return."""
        s = _RecordingState()
        gm.push_state(s)

        # First frame: nothing (state ticks).  Second frame: QUIT (loop exits).
        frames = iter([
            [],
            [pygame.event.Event(pygame.QUIT)],
        ])

        def _fake_event_get():
            try:
                return next(frames)
            except StopIteration:
                pytest.fail("main_loop ran more frames than expected")

        monkeypatch.setattr(pygame.event, 'get', _fake_event_get)
        # Don't render and don't tear down the display in this unit test.
        monkeypatch.setattr(conn_pygame_graphics, 'main', lambda: None)
        monkeypatch.setattr(pygame, 'quit', lambda: None)

        gm.main_loop()
        assert s.tick_count == 1
