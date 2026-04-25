from __future__ import annotations

import pytest

from game.timer import GameTimer, game_timer


@pytest.fixture
def t():
    return GameTimer()


class TestGameTimer:
    def test_initial_time_is_zero(self, t):
        assert t.get_time() == 0
        assert t.time == 0
        assert t.time_ms == 0

    def test_delta_time_converts_ms_to_seconds(self, t):
        t.delta_time(1000)
        assert t.time == pytest.approx(1.0)
        assert t.time_ms == pytest.approx(1000.0)

    def test_delta_time_accumulates(self, t):
        t.delta_time(250)
        t.delta_time(250)
        t.delta_time(500)
        assert t.time == pytest.approx(1.0)

    def test_fractional_milliseconds(self, t):
        t.delta_time(16.6667)
        assert t.time == pytest.approx(0.0166667, rel=1e-3)

    def test_update_time_sets_absolute(self, t):
        t.delta_time(500)
        t.update_time(7.5)
        assert t.time == 7.5
        assert t.time_ms == 7500

    def test_get_time_and_property_agree(self, t):
        t.delta_time(123)
        assert t.get_time() == t.time

    def test_module_singleton_exists(self):
        assert isinstance(game_timer, GameTimer)


class TestCalcDeltatime:
    def test_seconds_only(self):
        assert GameTimer.calc_deltatime(seconds=42) == 42

    def test_minutes_to_seconds(self):
        assert GameTimer.calc_deltatime(minutes=2) == 120

    def test_hours_to_seconds(self):
        assert GameTimer.calc_deltatime(hours=1) == 3600

    def test_combined(self):
        assert GameTimer.calc_deltatime(seconds=30, minutes=2, hours=1) == 3750

    def test_zero_default(self):
        assert GameTimer.calc_deltatime() == 0
