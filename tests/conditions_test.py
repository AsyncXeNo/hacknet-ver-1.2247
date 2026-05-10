from __future__ import annotations

import pytest

from utils.conditions import (
    Condition,
    LogicalCondition,
    LogicalOp,
    RelationalCondition,
    RelOp,
)


# ─── helpers ─────────────────────────────────────────────────────────────────


def _ptr(value):
    """Wrap a literal in a zero-arg callable to satisfy the Leaf protocol."""
    return lambda: value


# ─── RelationalCondition ─────────────────────────────────────────────────────


class TestRelationalConditionWithPointers:
    @pytest.mark.parametrize("a, op, b, expected", [
        (1, RelOp.EQ, 1, True),
        (1, RelOp.EQ, 2, False),
        (1, RelOp.NEQ, 2, True),
        (1, RelOp.NEQ, 1, False),
        (1, RelOp.LT, 2, True),
        (2, RelOp.LT, 1, False),
        (1, RelOp.LT, 1, False),
        (1, RelOp.LEQ, 1, True),
        (1, RelOp.LEQ, 2, True),
        (3, RelOp.LEQ, 2, False),
        (2, RelOp.GT, 1, True),
        (1, RelOp.GT, 2, False),
        (1, RelOp.GT, 1, False),
        (2, RelOp.GEQ, 2, True),
        (3, RelOp.GEQ, 2, True),
        (1, RelOp.GEQ, 2, False),
    ])
    def test_resolves_each_op(self, a, op, b, expected):
        cond = RelationalCondition(_ptr(a), op, _ptr(b))
        assert cond.resolve() is expected

    def test_pointer_is_evaluated_each_resolve(self):
        """Resolve must call the pointer every time so that mutating the
        underlying value is reflected in the next resolve call."""
        store = {'v': 0}
        cond = RelationalCondition(lambda: store['v'], RelOp.GT, _ptr(0))
        assert cond.resolve() is False
        store['v'] = 5
        assert cond.resolve() is True

    def test_works_with_floats(self):
        cond = RelationalCondition(_ptr(1.5), RelOp.LT, _ptr(2.0))
        assert cond.resolve() is True


# ─── RelationalCondition with nested Conditions ──────────────────────────────


class TestRelationalConditionWithNestedCondition:
    def test_nested_condition_resolved_first(self):
        """A RelationalCondition leaf may itself be another Condition, in
        which case its boolean resolution is the value compared."""
        inner = RelationalCondition(_ptr(1), RelOp.EQ, _ptr(1))  # True
        outer = RelationalCondition(inner, RelOp.EQ, _ptr(True))
        assert outer.resolve() is True


# ─── LogicalCondition ────────────────────────────────────────────────────────


class TestLogicalConditionAnd:
    def test_both_true(self):
        a = RelationalCondition(_ptr(1), RelOp.EQ, _ptr(1))
        b = RelationalCondition(_ptr(2), RelOp.EQ, _ptr(2))
        assert LogicalCondition(a, LogicalOp.AND, b).resolve() is True

    def test_one_false(self):
        a = RelationalCondition(_ptr(1), RelOp.EQ, _ptr(1))
        b = RelationalCondition(_ptr(2), RelOp.EQ, _ptr(3))
        assert LogicalCondition(a, LogicalOp.AND, b).resolve() is False


class TestLogicalConditionOr:
    def test_either_true(self):
        a = RelationalCondition(_ptr(1), RelOp.EQ, _ptr(1))
        b = RelationalCondition(_ptr(2), RelOp.EQ, _ptr(3))
        assert LogicalCondition(a, LogicalOp.OR, b).resolve() is True

    def test_both_false(self):
        a = RelationalCondition(_ptr(1), RelOp.EQ, _ptr(2))
        b = RelationalCondition(_ptr(3), RelOp.EQ, _ptr(4))
        assert LogicalCondition(a, LogicalOp.OR, b).resolve() is False


# ─── fluent helpers (with_and / with_or) ─────────────────────────────────────


class TestFluentChaining:
    def test_relational_with_and_returns_logical(self):
        a = RelationalCondition(_ptr(1), RelOp.EQ, _ptr(1))
        b = RelationalCondition(_ptr(2), RelOp.EQ, _ptr(2))
        chained = a.with_and(b)
        assert isinstance(chained, LogicalCondition)
        assert chained.resolve() is True

    def test_relational_with_or_returns_logical(self):
        a = RelationalCondition(_ptr(1), RelOp.EQ, _ptr(2))
        b = RelationalCondition(_ptr(3), RelOp.EQ, _ptr(3))
        chained = a.with_or(b)
        assert isinstance(chained, LogicalCondition)
        assert chained.resolve() is True

    def test_logical_with_and_chains(self):
        a = RelationalCondition(_ptr(1), RelOp.EQ, _ptr(1))
        b = RelationalCondition(_ptr(2), RelOp.EQ, _ptr(2))
        c = RelationalCondition(_ptr(3), RelOp.EQ, _ptr(3))
        chained = LogicalCondition(a, LogicalOp.AND, b).with_and(c)
        assert chained.resolve() is True

    def test_logical_with_or_chains(self):
        a = RelationalCondition(_ptr(1), RelOp.EQ, _ptr(2))  # False
        b = RelationalCondition(_ptr(3), RelOp.EQ, _ptr(4))  # False
        c = RelationalCondition(_ptr(5), RelOp.EQ, _ptr(5))  # True
        chained = LogicalCondition(a, LogicalOp.OR, b).with_or(c)
        assert chained.resolve() is True


# ─── Condition is abstract ───────────────────────────────────────────────────


class TestConditionAbstract:
    def test_cannot_instantiate(self):
        with pytest.raises(TypeError):
            Condition()
