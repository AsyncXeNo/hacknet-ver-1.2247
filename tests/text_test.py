from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

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


from graphics.text import renderer as renderer_mod
from graphics.text.renderer import (
    InvalidVariable,
    PreRenderRes,
    TextOverflowException,
    constantize,
    make_spans,
    pre_render,
    render_rich_text,
)
from graphics.text.span import Span
from graphics.components.style import AlignHor


# ─── fakes ───────────────────────────────────────────────────────────────────


class _FakeFont:
    """Render text → pygame.Surface w/ deterministic size.

    width  = len(text) * size (size==0 → 0 for empty text)
    height = size
    """

    def __init__(self, size: int):
        self.size = size

    def render(self, text: str) -> pygame.Surface:
        w = max(len(text) * self.size, 1)
        h = max(self.size, 1)
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        return surf


class _FakeAssetsManager:
    def get_font(self, path, size):
        return _FakeFont(size)


@pytest.fixture
def fake_assets(monkeypatch):
    am = _FakeAssetsManager()
    monkeypatch.setattr(renderer_mod, 'assets_manager', am)
    return am


@pytest.fixture
def fake_game_manager(monkeypatch):
    gm = SimpleNamespace(states=SimpleNamespace())
    monkeypatch.setattr(renderer_mod, 'game_manager', gm)
    return gm


DEF_COLOR = Color(255, 255, 255, 255)
DEF_SIZE = 10
DEF_FONT = Path('Regular.ttf')


# ─── Span ────────────────────────────────────────────────────────────────────


class TestSpan:
    def test_fields_stored(self):
        s = Span('hi', DEF_COLOR, 12, DEF_FONT)
        assert s.text == 'hi'
        assert s.color == DEF_COLOR
        assert s.font_size == 12
        assert s.font == DEF_FONT

    def test_frozen_immutable(self):
        s = Span('hi', DEF_COLOR, 12, DEF_FONT)
        with pytest.raises(Exception):
            s.text = 'bye'  # type: ignore

    def test_equality(self):
        a = Span('x', DEF_COLOR, 10, DEF_FONT)
        b = Span('x', DEF_COLOR, 10, DEF_FONT)
        assert a == b

    def test_inequality(self):
        a = Span('x', DEF_COLOR, 10, DEF_FONT)
        b = Span('y', DEF_COLOR, 10, DEF_FONT)
        assert a != b

# ─── constantize ─────────────────────────────────────────────────────────────


class TestConstantize:
    def test_passthrough_no_vars(self):
        assert constantize('hello world', SimpleNamespace()) == 'hello world'

    def test_empty_string(self):
        assert constantize('', SimpleNamespace()) == ''

    def test_single_var(self):
        ctx = SimpleNamespace(name='Alice')
        assert constantize('hi {{name}}', ctx) == 'hi Alice'

    def test_nested_attr(self):
        ctx = SimpleNamespace(player=SimpleNamespace(name='Bob'))
        assert constantize('{{player.name}}', ctx) == 'Bob'

    def test_deeply_nested_attr(self):
        ctx = SimpleNamespace(a=SimpleNamespace(b=SimpleNamespace(c=42)))
        assert constantize('{{a.b.c}}', ctx) == '42'

    def test_multiple_vars(self):
        ctx = SimpleNamespace(a='X', b='Y')
        assert constantize('{{a}}-{{b}}', ctx) == 'X-Y'

    def test_repeated_same_var_replaced(self):
        ctx = SimpleNamespace(x='Z')
        assert constantize('{{x}} {{x}}', ctx) == 'Z Z'

    def test_non_str_value_coerced(self):
        ctx = SimpleNamespace(n=7)
        assert constantize('{{n}}', ctx) == '7'

    def test_path_value_coerced(self):
        ctx = SimpleNamespace(p=Path('a/b'))
        assert constantize('{{p}}', ctx) == str(Path('a/b'))

    def test_missing_attr_raises(self):
        with pytest.raises(InvalidVariable):
            constantize('{{missing}}', SimpleNamespace())

    def test_missing_nested_attr_raises(self):
        ctx = SimpleNamespace(a=SimpleNamespace())
        with pytest.raises(InvalidVariable):
            constantize('{{a.b}}', ctx)

    def test_var_with_internal_space_not_matched(self):
        # regex requires no spaces inside braces
        ctx = SimpleNamespace(x='Y')
        out = constantize('{{ x }}', ctx)
        assert out == '{{ x }}'


# ─── make_spans ──────────────────────────────────────────────────────────────


class TestMakeSpans:
    def test_plain_two_words(self):
        spans = make_spans('hello world', DEF_COLOR, DEF_SIZE, DEF_FONT, SimpleNamespace())
        assert [s.text for s in spans] == ['hello', 'world']
        for s in spans:
            assert s.color == DEF_COLOR
            assert s.font_size == DEF_SIZE
            assert s.font == DEF_FONT

    def test_empty_string_yields_one_space(self):
        spans = make_spans('', DEF_COLOR, DEF_SIZE, DEF_FONT, SimpleNamespace())
        assert [s.text for s in spans] == [' ']

    def test_leading_newline_prepended_with_space(self):
        spans = make_spans('\n hi', DEF_COLOR, DEF_SIZE, DEF_FONT, SimpleNamespace())
        assert [s.text for s in spans] == [' ', '\n', 'hi']

    def test_double_newline_expands_to_paragraph_break(self):
        spans = make_spans(' \n\n ', DEF_COLOR, DEF_SIZE, DEF_FONT, SimpleNamespace())
        assert [s.text for s in spans] == [' ', '\n', ' ', '\n', ' ']

    def test_triple_newline_loops_until_done(self):
        spans = make_spans(' \n\n\n ', DEF_COLOR, DEF_SIZE, DEF_FONT, SimpleNamespace())
        # no '\n\n' substrings remain
        joined = ''.join(s.text for s in spans)
        assert '\n\n' not in joined

    def test_newline_inside_word_asserts(self):
        with pytest.raises(AssertionError):
            make_spans('foo\nbar', DEF_COLOR, DEF_SIZE, DEF_FONT, SimpleNamespace())

    def test_color_change_and_reset(self):
        text = 'a ⸸[c:10,20,30,40] b ⸸[c:reset] c'
        spans = make_spans(text, DEF_COLOR, DEF_SIZE, DEF_FONT, SimpleNamespace())
        words = [s for s in spans if s.text not in (' ',)]
        assert words[0].text == 'a' and words[0].color == DEF_COLOR
        assert words[1].text == 'b' and tuple(words[1].color) == (10, 20, 30, 40)
        assert words[2].text == 'c' and words[2].color == DEF_COLOR

    def test_size_change_and_reset(self):
        text = 'a ⸸[s:30] b ⸸[s:reset] c'
        spans = [s for s in make_spans(text, DEF_COLOR, DEF_SIZE, DEF_FONT, SimpleNamespace()) if s.text not in (' ',)]
        assert spans[0].font_size == DEF_SIZE
        assert spans[1].font_size == 30
        assert spans[2].font_size == DEF_SIZE

    def test_size_delta_increments_current(self):
        text = 'a ⸸[sd:5] b ⸸[sd:-3] c'
        spans = [s for s in make_spans(text, DEF_COLOR, DEF_SIZE, DEF_FONT, SimpleNamespace()) if s.text not in (' ',)]
        assert spans[0].font_size == DEF_SIZE
        assert spans[1].font_size == DEF_SIZE + 5
        assert spans[2].font_size == DEF_SIZE + 5 - 3

    def test_font_change_and_reset(self):
        text = 'a ⸸[f:Bold.ttf] b ⸸[f:reset] c'
        spans = [s for s in make_spans(text, DEF_COLOR, DEF_SIZE, DEF_FONT, SimpleNamespace()) if s.text not in (' ',)]
        assert spans[0].font == DEF_FONT
        assert spans[1].font == Path('Bold.ttf')
        assert spans[2].font == DEF_FONT

    def test_escape_token_emits_no_span(self):
        text = '⸸[c:1,2,3,4]'
        spans = make_spans(text, DEF_COLOR, DEF_SIZE, DEF_FONT, SimpleNamespace())
        assert spans == []

    def test_var_substituted_before_tokenize(self):
        ctx = SimpleNamespace(name='Alice')
        spans = make_spans('hi {{name}}', DEF_COLOR, DEF_SIZE, DEF_FONT, ctx)
        assert [s.text for s in spans] == ['hi', 'Alice']

    def test_none_ctx_uses_game_manager_states(self, fake_game_manager):
        fake_game_manager.states = SimpleNamespace(name='Z')
        spans = make_spans('{{name}}', DEF_COLOR, DEF_SIZE, DEF_FONT, None)
        assert [s.text for s in spans] == ['Z']


# ─── pre_render ──────────────────────────────────────────────────────────────


def _spans(*texts: str, size: int = DEF_SIZE, color: Color = DEF_COLOR, font: Path = DEF_FONT) -> list[Span]:
    return [Span(t, color, size, font) for t in texts]


class TestPreRender:
    def test_single_word_one_line(self, fake_assets):
        out = pre_render(_spans('hi'), max_w=1000)
        assert len(out.lines) == 1
        # 1 surface (word) — no trailing space because last span
        assert len(out.lines[0]) == 1

    def test_two_words_same_line_with_space(self, fake_assets):
        out = pre_render(_spans('a', 'b'), max_w=1000)
        assert len(out.lines) == 1
        # word, space, word — last has no trailing space
        assert len(out.lines[0]) == 3

    def test_word_overflow_wraps_to_next_line(self, fake_assets):
        # each char = DEF_SIZE wide. 'aaaa' = 40, ' ' = 10, 'bbbb' = 40 → 90 fits.
        # set max_w=50 — only 'aaaa' fits, then ' '/'bbbb' wrap.
        out = pre_render(_spans('aaaa', 'bbbb'), max_w=50)
        assert len(out.lines) == 2
        # second-line first surface pos reset to 0
        assert out.lines[1][0].pos == [0, 0]

    def test_single_word_wider_than_max_raises(self, fake_assets):
        with pytest.raises(TextOverflowException):
            pre_render(_spans('toolong'), max_w=5)

    def test_explicit_newline_breaks_line(self, fake_assets):
        out = pre_render(_spans('a', '\n', 'b'), max_w=1000)
        assert len(out.lines) == 2

    def test_newline_with_empty_current_line_skipped(self, fake_assets):
        out = pre_render(_spans('\n', 'a'), max_w=1000)
        # leading \n drops; only one line w/ 'a'
        assert len(out.lines) == 1

    def test_max_heights_per_line(self, fake_assets):
        big = Span('B', DEF_COLOR, 30, DEF_FONT)
        small = Span('s', DEF_COLOR, 10, DEF_FONT)
        nl = Span('\n', DEF_COLOR, DEF_SIZE, DEF_FONT)
        out = pre_render([big, nl, small], max_w=1000)
        assert out.max_heights[0] == 30
        assert out.max_heights[1] == 10

    def test_empty_spans_yields_empty(self, fake_assets):
        out = pre_render([], max_w=100)
        assert out.lines == []
        assert out.max_heights == []

    def test_returns_pre_render_res(self, fake_assets):
        out = pre_render(_spans('a'), max_w=100)
        assert isinstance(out, PreRenderRes)


# ─── render_rich_text ────────────────────────────────────────────────────────


class TestRenderRichText:
    def test_accepts_spans_list(self, fake_assets):
        surf = render_rich_text(_spans('hi'), Rect(0, 0, 200, 200), AlignHor.LEFT, 0)
        assert surf.get_width() == 200

    def test_accepts_pre_render_res(self, fake_assets):
        pre = pre_render(_spans('hi'), max_w=200)
        surf = render_rich_text(pre, Rect(0, 0, 200, 200), AlignHor.LEFT, 0)
        assert surf.get_width() == 200

    def test_max_size_int_no_height_check(self, fake_assets):
        # int max → max_h=None → no overflow exception even on long content
        surf = render_rich_text(_spans('hi'), 200, AlignHor.LEFT, 0)
        assert surf.get_width() == 200

    def test_height_overflow_raises(self, fake_assets):
        # one line of size 30 → height 30; max_h=5 → overflow
        big = _spans('B', size=30)
        with pytest.raises(TextOverflowException):
            render_rich_text(big, Rect(0, 0, 200, 5), AlignHor.LEFT, 0)

    def test_gap_y_adds_to_total_height(self, fake_assets):
        spans = [
            Span('a', DEF_COLOR, 10, DEF_FONT),
            Span('\n', DEF_COLOR, 10, DEF_FONT),
            Span('b', DEF_COLOR, 10, DEF_FONT),
        ]
        no_gap = render_rich_text(spans, Rect(0, 0, 200, 1000), AlignHor.LEFT, 0)
        with_gap = render_rich_text(spans, Rect(0, 0, 200, 1000), AlignHor.LEFT, 7)
        assert with_gap.get_height() == no_gap.get_height() + 7

    def test_single_line_no_gap_added(self, fake_assets):
        spans = _spans('a')
        s_a = render_rich_text(spans, Rect(0, 0, 200, 1000), AlignHor.LEFT, 0)
        s_b = render_rich_text(spans, Rect(0, 0, 200, 1000), AlignHor.LEFT, 50)
        assert s_a.get_height() == s_b.get_height()

    def test_align_left(self, fake_assets):
        # smoke: produces surface; line.pos.x stays 0
        surf = render_rich_text(_spans('a'), Rect(0, 0, 200, 1000), AlignHor.LEFT, 0)
        assert isinstance(surf, pygame.Surface)

    def test_align_center(self, fake_assets):
        surf = render_rich_text(_spans('a'), Rect(0, 0, 200, 1000), AlignHor.CENTER, 0)
        assert isinstance(surf, pygame.Surface)

    def test_align_right(self, fake_assets):
        surf = render_rich_text(_spans('a'), Rect(0, 0, 200, 1000), AlignHor.RIGHT, 0)
        assert isinstance(surf, pygame.Surface)


# ─── exceptions ──────────────────────────────────────────────────────────────


class TestExceptions:
    def test_text_overflow_is_exception(self):
        assert issubclass(TextOverflowException, Exception)

    def test_invalid_variable_is_exception(self):
        assert issubclass(InvalidVariable, Exception)
