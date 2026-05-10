from __future__ import annotations

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


from game.objects.player import Direction, Player, states
from game.timer import game_timer
from graphics.constants import GAME_WIDTH, GAME_HEIGHT
from graphics.surfaces import Surface
from utils.properties import Translation


@pytest.fixture(autouse=True)
def _reset_game_timer():
    game_timer.update_time(0)
    yield
    game_timer.update_time(0)


@pytest.fixture
def parent():
    return Surface((GAME_WIDTH, GAME_HEIGHT), [0, 0])


def _key_event(kind: int, key: int) -> pygame.event.Event:
    return pygame.event.Event(kind, {'key': key, 'mod': 0, 'unicode': '', 'scancode': 0})


# ─── Direction enum ──────────────────────────────────────────────────────────


class TestDirection:
    def test_low_name_lowercases(self):
        assert Direction.UP.low_name == 'up'
        assert Direction.LEFT.low_name == 'left'
        assert Direction.DOWN.low_name == 'down'
        assert Direction.RIGHT.low_name == 'right'

    def test_values_are_zero_through_three(self):
        assert {d.value for d in Direction} == {0, 1, 2, 3}


# ─── Player construction ────────────────────────────────────────────────────


class TestPlayerConstruction:
    def test_constructs_without_error(self, parent):
        Player(parent)

    def test_initial_position_is_screen_center(self, parent):
        p = Player(parent)
        assert p.transform.translation.x == GAME_WIDTH / 2
        assert p.transform.translation.y == GAME_HEIGHT / 2

    def test_initial_velocity_is_zero(self, parent):
        p = Player(parent)
        assert isinstance(p.vel, Translation)
        assert p.vel.is_zero

    def test_default_speed(self, parent):
        p = Player(parent)
        assert p.speed == 100.0

    def test_initial_state_is_idle_down(self, parent):
        p = Player(parent)
        assert p.state_machine.cur_state is states.idle[Direction.DOWN.low_name]

    def test_sprite_is_registered_as_subcomponent(self, parent):
        p = Player(parent)
        # Component.add_component stores by name on a SimpleNamespace.
        assert p.sprite in vars(p.components).values()


# ─── Movement on key events ──────────────────────────────────────────────────


class TestPlayerKeyboardInput:
    def test_w_sets_negative_y_velocity(self, parent):
        p = Player(parent)
        p.events_handler([_key_event(pygame.KEYDOWN, pygame.K_w)], (0, 0))
        assert p.vel.y == -p.speed
        assert p.vel.x == 0

    def test_a_sets_negative_x_velocity(self, parent):
        p = Player(parent)
        p.events_handler([_key_event(pygame.KEYDOWN, pygame.K_a)], (0, 0))
        assert p.vel.x == -p.speed
        assert p.vel.y == 0

    def test_s_sets_positive_y_velocity(self, parent):
        p = Player(parent)
        p.events_handler([_key_event(pygame.KEYDOWN, pygame.K_s)], (0, 0))
        assert p.vel.y == p.speed

    def test_d_sets_positive_x_velocity(self, parent):
        p = Player(parent)
        p.events_handler([_key_event(pygame.KEYDOWN, pygame.K_d)], (0, 0))
        assert p.vel.x == p.speed

    def test_diagonal_keydown_blocked_while_already_moving(self, parent):
        """The player only accepts a new direction while velocity is zero —
        intentional one-axis-at-a-time movement."""
        p = Player(parent)
        p.events_handler([_key_event(pygame.KEYDOWN, pygame.K_w)], (0, 0))
        p.events_handler([_key_event(pygame.KEYDOWN, pygame.K_d)], (0, 0))
        assert p.vel.x == 0  # second keydown was ignored
        assert p.vel.y == -p.speed

    def test_keyup_zeros_matching_axis(self, parent):
        p = Player(parent)
        p.events_handler([_key_event(pygame.KEYDOWN, pygame.K_w)], (0, 0))
        p.events_handler([_key_event(pygame.KEYUP, pygame.K_w)], (0, 0))
        assert p.vel.is_zero

    def test_keyup_for_unrelated_key_is_noop(self, parent):
        p = Player(parent)
        p.events_handler([_key_event(pygame.KEYDOWN, pygame.K_w)], (0, 0))
        # KEYUP for K_d while only K_w was held should not affect velocity.
        p.events_handler([_key_event(pygame.KEYUP, pygame.K_d)], (0, 0))
        assert p.vel.y == -p.speed


# ─── Movement integration ────────────────────────────────────────────────────


class TestPlayerMovementIntegration:
    def test_position_advances_with_velocity_over_time(self, parent):
        p = Player(parent)
        start_x = p.transform.translation.x

        # Initialize last_update at t=0 by syncing the per-component clock.
        p.last_update = game_timer.time_ms

        p.vel.x = p.speed  # bypass keydown gate to set vel directly
        # Advance the timer by 1s. dx = 1000ms; dx_meters = 100 * 1000/1000 = 100.
        game_timer.update_time(1.0)
        p.events_handler([], (0, 0))

        assert p.transform.translation.x == pytest.approx(start_x + 100.0)

    def test_zero_velocity_does_not_move(self, parent):
        p = Player(parent)
        p.last_update = game_timer.time_ms
        start = (p.transform.translation.x, p.transform.translation.y)

        game_timer.update_time(1.0)
        p.events_handler([], (0, 0))
        assert (p.transform.translation.x, p.transform.translation.y) == start
