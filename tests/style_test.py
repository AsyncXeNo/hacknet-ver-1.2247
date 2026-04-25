from __future__ import annotations

import pytest
from pygame import Rect
from pygame.color import Color

from graphics.components.style import (
    AlignHor, AlignVer,
    BorderConfig, Gap, TextConfig,
    Style, lerp, styled, _style_stack,
)


@pytest.fixture(autouse=True)
def _isolated_style_stack():
    """Each test starts with an empty style stack."""
    snapshot = list(_style_stack)
    _style_stack.clear()
    yield
    _style_stack.clear()
    _style_stack.extend(snapshot)


# ─── lerp ────────────────────────────────────────────────────────────────────


class TestLerpNumeric:
    def test_int_at_t_zero_returns_a(self):
        assert lerp(0, 100, 0.0) == 0

    def test_int_at_t_one_returns_b(self):
        assert lerp(0, 100, 1.0) == 100

    def test_int_at_midpoint(self):
        assert lerp(0, 100, 0.5) == 50

    def test_float_at_midpoint(self):
        assert lerp(2.0, 4.0, 0.5) == pytest.approx(3.0)

    def test_preserves_input_numeric_type(self):
        assert isinstance(lerp(0, 10, 0.5), int)
        assert isinstance(lerp(0.0, 10.0, 0.5), float)

    def test_t_out_of_bounds_low_asserts(self):
        with pytest.raises(AssertionError):
            lerp(0, 100, -0.1)

    def test_t_out_of_bounds_high_asserts(self):
        with pytest.raises(AssertionError):
            lerp(0, 100, 1.1)

    def test_type_mismatch_asserts(self):
        with pytest.raises(AssertionError):
            lerp(1, 2.0, 0.5)


class TestLerpColor:
    def test_color_endpoints(self):
        a, b = Color(0, 0, 0, 255), Color(255, 255, 255, 255)
        assert tuple(lerp(a, b, 0.0)) == (0, 0, 0, 255)
        assert tuple(lerp(a, b, 1.0)) == (255, 255, 255, 255)

    def test_color_midpoint(self):
        a, b = Color(0, 0, 0), Color(200, 200, 200)
        mid = lerp(a, b, 0.5)
        assert mid.r == 100 and mid.g == 100 and mid.b == 100


class TestLerpComposite:
    def test_gap_lerps_each_field(self):
        a = Gap(0, 0, 0, 0)
        b = Gap(10, 20, 30, 40)
        mid = lerp(a, b, 0.5)
        assert (mid.l, mid.r, mid.t, mid.b) == (5, 10, 15, 20)

    def test_rect_lerps_each_field(self):
        a = Rect(0, 0, 0, 0)
        b = Rect(10, 20, 30, 40)
        mid = lerp(a, b, 0.5)
        assert (mid.x, mid.y, mid.width, mid.height) == (5, 10, 15, 20)

    def test_border_config_lerps_when_border_matches(self):
        a = BorderConfig(True, 0, 1, Color(0, 0, 0))
        b = BorderConfig(True, 10, 5, Color(100, 100, 100))
        mid = lerp(a, b, 0.5)
        assert mid.radius == 5
        assert mid.width == 3

    def test_border_config_assert_on_mismatch(self):
        a = BorderConfig(False, 0, None, None)
        b = BorderConfig(True, 0, 1, Color(0, 0, 0))
        with pytest.raises(AssertionError):
            lerp(a, b, 0.5)

    def test_text_config_lerps_color_and_size(self):
        a = TextConfig(AlignHor.CENTER, AlignVer.CENTER, Color(0, 0, 0), 0, None, 10)
        b = TextConfig(AlignHor.CENTER, AlignVer.CENTER, Color(200, 200, 200), 0, None, 30)
        mid = lerp(a, b, 0.5)
        assert mid.font_size == 20
        assert mid.color.r == 100

    def test_text_config_align_mismatch_asserts(self):
        a = TextConfig(AlignHor.LEFT, AlignVer.TOP, Color(0, 0, 0), 0, None, 10)
        b = TextConfig(AlignHor.RIGHT, AlignVer.TOP, Color(0, 0, 0), 0, None, 10)
        with pytest.raises(AssertionError):
            lerp(a, b, 0.5)


# ─── Gap ─────────────────────────────────────────────────────────────────────


class TestGap:
    def test_x_sums_horizontal(self):
        assert Gap(2, 3, 0, 0).x == 5

    def test_y_sums_vertical(self):
        assert Gap(0, 0, 4, 5).y == 9

    def test_none_post_init_defaults(self):
        g = Gap(None, None, None, None)
        assert (g.l, g.r, g.t, g.b) == (0, 0, 0, 0)


# ─── BorderConfig ────────────────────────────────────────────────────────────


class TestBorderConfig:
    def test_no_border_with_no_width_or_color_ok(self):
        BorderConfig(False, 5, None, None)

    def test_border_with_width_and_color_ok(self):
        BorderConfig(True, 5, 2, Color(0, 0, 0))

    def test_border_true_without_width_asserts(self):
        with pytest.raises(AssertionError):
            BorderConfig(True, 5, None, Color(0, 0, 0))

    def test_border_true_without_color_asserts(self):
        with pytest.raises(AssertionError):
            BorderConfig(True, 5, 1, None)

    def test_border_false_with_width_asserts(self):
        with pytest.raises(AssertionError):
            BorderConfig(False, 5, 1, None)


# ─── Style / styled ──────────────────────────────────────────────────────────


class TestStyle:
    def test_context_manager_pushes_and_pops(self):
        assert _style_stack == []
        with Style(color='red'):
            assert _style_stack == [{'color': 'red'}]
        assert _style_stack == []

    def test_nested_styles_stack(self):
        with Style(color='red'):
            with Style(font_size=12):
                assert _style_stack == [{'color': 'red'}, {'font_size': 12}]


class TestStyled:
    def test_passes_args_through_when_no_active_style(self):
        @styled
        def f(**kwargs):
            return kwargs
        assert f(color='blue') == {'color': 'blue'}

    def test_active_style_merged_into_kwargs(self):
        @styled
        def f(**kwargs):
            return kwargs
        with Style(color='red', font_size=12):
            assert f() == {'color': 'red', 'font_size': 12}

    def test_explicit_kwargs_win(self):
        @styled
        def f(**kwargs):
            return kwargs
        with Style(color='red'):
            assert f(color='green') == {'color': 'green'}

    def test_outer_style_overridden_by_inner(self):
        @styled
        def f(**kwargs):
            return kwargs
        with Style(color='red'):
            with Style(color='green'):
                assert f()['color'] == 'green'
