from __future__ import annotations

import string
from threading import Thread

import pytest

from graphics.utils import generate_id, GENERATED_IDS


@pytest.fixture(autouse=True)
def _clear_generated_ids():
    """Each test gets a fresh registry so we don't fight the singleton."""
    snapshot = list(GENERATED_IDS)
    GENERATED_IDS.clear()
    yield
    GENERATED_IDS.clear()
    GENERATED_IDS.extend(snapshot)


class TestGenerateId:
    def test_default_length_is_four(self):
        assert len(generate_id()) == 4

    def test_custom_length(self):
        assert len(generate_id(length=8)) == 8

    def test_uppercase_only(self):
        for _ in range(50):
            new_id = generate_id()
            assert all(c in string.ascii_uppercase for c in new_id)

    def test_uniqueness(self):
        ids = {generate_id(length=6) for _ in range(200)}
        assert len(ids) == 200

    def test_registered_in_generated_ids(self):
        new_id = generate_id()
        assert new_id in GENERATED_IDS

    def test_thread_safety(self):
        results = []

        def _spam():
            for _ in range(50):
                results.append(generate_id(length=6))

        threads = [Thread(target=_spam) for _ in range(4)]
        for thr in threads: thr.start()
        for thr in threads: thr.join()

        assert len(results) == len(set(results)) == 200
