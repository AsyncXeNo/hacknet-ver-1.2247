from __future__ import annotations

import math

import pygame
import pytest

# `assets_manager` calls `Surface.convert_alpha()` at import time, which
# requires an active video mode — so set the mode before the asset-loading
# imports run.
pygame.display.init()
pygame.display.set_mode((1, 1))


@pytest.fixture(scope='module', autouse=True)
def _display():
    yield
    pygame.display.quit()


from graphics.components.sprite import (
    AnimFunc,
    AnimState,
    AnimStateMachine,
    Sprite,
    Transition,
)
from graphics.surfaces import Surface
from utils.conditions import RelationalCondition, RelOp
from utils.properties import Transform, Translation


def _frames(n: int, size: tuple[int, int] = (4, 4)) -> list[Surface]:
    """n distinct surfaces tagged by a unique pixel so equality is by identity
    and frame switches are observable in tests."""
    return [Surface(size, [0, 0]) for _ in range(n)]


# ─── AnimFunc ────────────────────────────────────────────────────────────────


class TestAnimFunc:
    def test_loop_wraps_back_to_zero(self):
        # AnimFunc.LOOP is a lambda stored on the Enum class. It is callable
        # directly; semantics: idx = round(x % frames).
        loop = AnimFunc.LOOP
        assert loop(0, 4) == 0
        assert loop(1, 4) == 1
        assert loop(3, 4) == 3
        assert loop(4, 4) == 0
        assert loop(5, 4) == 1

    def test_back_and_forth_endpoints(self):
        baf = AnimFunc.BACK_AND_FORTH
        # At x=0 -> idx=0; at x=frames-1 -> idx=frames-1.
        assert baf(0, 4) == 0
        assert baf(3, 4) == 3

    def test_back_and_forth_returns_at_double_extent(self):
        """The acos/cos formulation gives a triangle wave with period
        2*(frames-1).  After advancing past the end, the index winds back."""
        baf = AnimFunc.BACK_AND_FORTH
        assert baf(2 * (4 - 1), 4) == 0  # full cycle returns to start

    def test_back_and_forth_midpoint(self):
        baf = AnimFunc.BACK_AND_FORTH
        # midpoint of the forward sweep (x = (frames-1)/2) -> half-frame index
        assert baf(1.5, 4) == round(1.5)


# ─── AnimState ───────────────────────────────────────────────────────────────


class TestAnimState:
    def test_initial_frame_is_zero(self):
        frames = _frames(4)
        st = AnimState(frames, duration_ms=1000, func=AnimFunc.LOOP)
        assert st.current is frames[0]

    def test_delta_accumulates(self):
        st = AnimState(_frames(4), duration_ms=1000, func=AnimFunc.LOOP)
        st.delta(250)
        st.delta(250)
        assert st.cur_time == 500

    def test_loop_advances_per_frame_slot(self):
        frames = _frames(4)
        st = AnimState(frames, duration_ms=1000, func=AnimFunc.LOOP)
        # 250ms per frame at 4 frames over 1000ms.
        st.delta(250)
        assert st.current is frames[1]
        st.delta(250)
        assert st.current is frames[2]
        st.delta(500)
        # At t=1000, cur_frame == 4 -> index 0 again (loop).
        assert st.current is frames[0]

    def test_frames_count_matches_input_list(self):
        st = AnimState(_frames(7), duration_ms=100, func=AnimFunc.LOOP)
        assert st.frames == 7


# ─── Transition ──────────────────────────────────────────────────────────────


class TestTransition:
    def test_truthiness_resolves_condition(self):
        a, b = AnimState(_frames(1), 100, AnimFunc.LOOP), AnimState(_frames(1), 100, AnimFunc.LOOP)
        true_cond = RelationalCondition(lambda: 1, RelOp.EQ, lambda: 1)
        false_cond = RelationalCondition(lambda: 1, RelOp.EQ, lambda: 2)
        assert bool(Transition(a, b, true_cond)) is True
        assert bool(Transition(a, b, false_cond)) is False

    def test_stores_states(self):
        a, b = AnimState(_frames(1), 100, AnimFunc.LOOP), AnimState(_frames(1), 100, AnimFunc.LOOP)
        t = Transition(a, b, RelationalCondition(lambda: 0, RelOp.EQ, lambda: 0))
        assert t.from_state is a
        assert t.to_state is b


# ─── AnimStateMachine ────────────────────────────────────────────────────────


class TestAnimStateMachine:
    def test_starts_at_start_state(self):
        a = AnimState(_frames(1), 100, AnimFunc.LOOP)
        sm = AnimStateMachine(a, [])
        assert sm.cur_state is a

    def test_check_transition_advances_when_cond_true(self):
        a = AnimState(_frames(1), 100, AnimFunc.LOOP)
        b = AnimState(_frames(1), 100, AnimFunc.LOOP)
        sm = AnimStateMachine(a, [
            Transition(a, b, RelationalCondition(lambda: 1, RelOp.EQ, lambda: 1)),
        ])
        sm.check_transition()
        assert sm.cur_state is b

    def test_check_transition_no_op_when_cond_false(self):
        a = AnimState(_frames(1), 100, AnimFunc.LOOP)
        b = AnimState(_frames(1), 100, AnimFunc.LOOP)
        sm = AnimStateMachine(a, [
            Transition(a, b, RelationalCondition(lambda: 1, RelOp.EQ, lambda: 2)),
        ])
        sm.check_transition()
        assert sm.cur_state is a

    def test_transition_resets_cur_time_on_new_state(self):
        a = AnimState(_frames(2), 100, AnimFunc.LOOP)
        b = AnimState(_frames(2), 100, AnimFunc.LOOP)
        b.cur_time = 500  # pre-existing state
        sm = AnimStateMachine(a, [
            Transition(a, b, RelationalCondition(lambda: 1, RelOp.EQ, lambda: 1)),
        ])
        sm.check_transition()
        assert sm.cur_state is b
        assert sm.cur_state.cur_time == 0

    def test_check_transition_only_fires_for_matching_from_state(self):
        a = AnimState(_frames(1), 100, AnimFunc.LOOP)
        b = AnimState(_frames(1), 100, AnimFunc.LOOP)
        c = AnimState(_frames(1), 100, AnimFunc.LOOP)
        sm = AnimStateMachine(a, [
            Transition(b, c, RelationalCondition(lambda: 1, RelOp.EQ, lambda: 1)),
        ])
        sm.check_transition()
        assert sm.cur_state is a

    def test_current_returns_cur_state_current_frame(self):
        frames = _frames(2)
        a = AnimState(frames, 100, AnimFunc.LOOP)
        sm = AnimStateMachine(a, [])
        assert sm.current is frames[0]


# ─── Sprite ──────────────────────────────────────────────────────────────────


class TestSprite:
    @pytest.fixture
    def parent(self):
        return Surface((200, 200), [0, 0])

    def _make(self, parent):
        frames = _frames(2, size=(8, 8))
        state = AnimState(frames, duration_ms=1000, func=AnimFunc.LOOP)
        sm = AnimStateMachine(state, [])
        transform = Transform(Translation(10, 20), rotation=0, scale=1)
        return Sprite(parent, sm, lambda: transform), transform, sm

    def test_construction_sets_img_rect(self, parent):
        sprite, transform, _ = self._make(parent)
        # `final` was accessed during init to seed img_rect.
        assert sprite.img_rect.x == 10
        assert sprite.img_rect.y == 20
        # rotozoom of an 8x8 surface at scale=1 yields 8x8.
        assert sprite.img_rect.width == 8
        assert sprite.img_rect.height == 8

    def test_rect_callable_returns_img_rect(self, parent):
        sprite, _, _ = self._make(parent)
        assert sprite.rect() is sprite.img_rect

    def test_transform_property_dereferences_pointer(self, parent):
        sprite, transform, _ = self._make(parent)
        transform.translation.x = 99
        assert sprite.transform.translation.x == 99

    def test_graphics_handler_blits_without_error(self, parent):
        sprite, _, _ = self._make(parent)
        sprite.graphics_handler()  # should not raise
