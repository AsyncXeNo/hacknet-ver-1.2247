from __future__ import annotations

from utils.properties import Transform, Translation


class TestTranslation:
    def test_construction(self):
        t = Translation(1.0, -2.5)
        assert t.x == 1.0
        assert t.y == -2.5

    def test_is_zero_when_both_zero(self):
        assert Translation(0, 0).is_zero is True

    def test_is_zero_false_when_x_nonzero(self):
        assert Translation(0.0001, 0).is_zero is False

    def test_is_zero_false_when_y_nonzero(self):
        assert Translation(0, -0.0001).is_zero is False

    def test_mutable(self):
        t = Translation(0, 0)
        t.x = 5
        t.y = 7
        assert (t.x, t.y) == (5, 7)
        assert t.is_zero is False


class TestTransform:
    def test_construction(self):
        tr = Transform(Translation(10, 20), rotation=90, scale=2.0)
        assert tr.translation.x == 10
        assert tr.translation.y == 20
        assert tr.rotation == 90
        assert tr.scale == 2.0

    def test_mutable_fields(self):
        tr = Transform(Translation(0, 0), 0, 1)
        tr.rotation = 45
        tr.scale = 0.5
        tr.translation.x = 100
        assert tr.rotation == 45
        assert tr.scale == 0.5
        assert tr.translation.x == 100
