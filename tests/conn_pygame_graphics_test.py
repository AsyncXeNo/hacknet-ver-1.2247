from __future__ import annotations

import pygame
import pytest


pygame.display.init()


@pytest.fixture(scope='module', autouse=True)
def _display():
    pygame.display.set_mode((1, 1))
    yield
    pygame.display.quit()


from graphics.conn_pygame_graphics import ConnPygameGraphics
from graphics.surfaces import Surface


class _FakeState:
    def __init__(self, *, should_draw_bg: bool = False, size=(40, 30)):
        self.should_draw_bg = should_draw_bg
        self.main_surface = Surface(size, [0, 0])
        self.draw_calls = 0

    def graphics_handler(self):
        self.draw_calls += 1


@pytest.fixture
def cpg():
    return ConnPygameGraphics(64, 48, 'test-window')


# ─── Render queue plumbing ───────────────────────────────────────────────────


class TestRenderQueue:
    def test_push_appends(self, cpg):
        s1, s2 = _FakeState(), _FakeState()
        cpg.push_state(s1)
        cpg.push_state(s2)
        assert cpg.render_queue == [s1, s2]

    def test_pop_removes_first(self, cpg):
        s1, s2 = _FakeState(), _FakeState()
        cpg.push_state(s1)
        cpg.push_state(s2)
        assert cpg.pop_state() is s1
        assert cpg.render_queue == [s2]

    def test_remove_state_targets_specific(self, cpg):
        s1, s2, s3 = _FakeState(), _FakeState(), _FakeState()
        for s in (s1, s2, s3): cpg.push_state(s)
        cpg.remove_state(s2)
        assert cpg.render_queue == [s1, s3]

    def test_select_moves_to_end(self, cpg):
        s1, s2, s3 = _FakeState(), _FakeState(), _FakeState()
        for s in (s1, s2, s3): cpg.push_state(s)
        cpg.select_state(s1)
        assert cpg.render_queue == [s2, s3, s1]

    def test_remove_state_missing_raises(self, cpg):
        with pytest.raises(ValueError):
            cpg.remove_state(_FakeState())


# ─── main() rendering ────────────────────────────────────────────────────────


class TestMainRender:
    def test_renders_top_state_when_only_one_pushed(self, cpg):
        s = _FakeState()
        cpg.push_state(s)
        cpg.main()
        assert s.draw_calls == 1

    def test_layered_rendering_includes_background_states(self, cpg):
        base = _FakeState(should_draw_bg=False)
        overlay = _FakeState(should_draw_bg=True)
        cpg.push_state(base)
        cpg.push_state(overlay)
        cpg.main()
        # Both render: top has should_draw_bg=True so the walk pulls in `base`.
        assert base.draw_calls == 1
        assert overlay.draw_calls == 1

    def test_bottom_state_not_drawn_under_opaque_top(self, cpg):
        bottom = _FakeState()
        top = _FakeState(should_draw_bg=False)
        cpg.push_state(bottom)
        cpg.push_state(top)
        cpg.main()
        assert top.draw_calls == 1
        assert bottom.draw_calls == 0

    def test_all_should_draw_bg_walks_to_root(self, cpg):
        a = _FakeState(should_draw_bg=True)
        b = _FakeState(should_draw_bg=True)
        c = _FakeState(should_draw_bg=True)
        for s in (a, b, c): cpg.push_state(s)
        cpg.main()
        assert a.draw_calls == 1
        assert b.draw_calls == 1
        assert c.draw_calls == 1
