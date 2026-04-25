from __future__ import annotations

import pygame
import pytest

pygame.display.init()


@pytest.fixture(scope='module', autouse=True)
def _display():
    pygame.display.set_mode((1, 1))
    yield
    pygame.display.quit()


from game.states.main_menu import MainMenuState, new_game
from game.states.rl import RLState
from graphics.components.ui import Button, Label
from graphics.constants import GAME_WIDTH, GAME_HEIGHT


# ─── MainMenuState ───────────────────────────────────────────────────────────


class TestMainMenuState:
    def test_constructs_without_error(self):
        MainMenuState()

    def test_main_surface_sized_to_game(self):
        s = MainMenuState()
        assert s.main_surface.get_size() == (GAME_WIDTH, GAME_HEIGHT)

    def test_has_heading_label_and_four_buttons(self):
        s = MainMenuState()
        labels = [c for c in s.components if isinstance(c, Label)]
        buttons = [c for c in s.components if isinstance(c, Button)]
        assert len(labels) == 1
        assert len(buttons) == 4

    def test_heading_label_text(self):
        s = MainMenuState()
        labels = [c for c in s.components if isinstance(c, Label)]
        assert labels[0].text == "HACKNET"

    def test_button_labels_in_expected_order(self):
        s = MainMenuState()
        buttons = [c for c in s.components if isinstance(c, Button)]
        assert [b.text for b in buttons] == ["New Game", "Continue", "Options", "Quit"]

    def test_new_game_button_wires_real_callback(self):
        """Buttons 1..3 are no-op lambdas; button 0 is the module-level
        `new_game` function that pops main menu and pushes RLState."""
        s = MainMenuState()
        buttons = [c for c in s.components if isinstance(c, Button)]
        assert buttons[0].on_click is new_game
        assert buttons[1].on_click is not new_game

    def test_events_handler_runs_without_error(self, monkeypatch):
        s = MainMenuState()
        # Mouse outside every component so no callback fires.
        monkeypatch.setattr(pygame.mouse, 'get_pos', lambda: (-1, -1))
        s.events_handler([])


# ─── RLState ─────────────────────────────────────────────────────────────────


class TestRLState:
    def test_constructs_without_error(self):
        RLState()

    def test_loads_idle_sprite_frame(self):
        s = RLState()
        assert isinstance(s.img, pygame.Surface)

    def test_main_surface_sized_to_game(self):
        s = RLState()
        assert s.main_surface.get_size() == (GAME_WIDTH, GAME_HEIGHT)

    def test_graphics_handler_blits_sprite(self):
        s = RLState()
        s.main_surface.fill((0, 0, 0, 0))
        s.graphics_handler()
        # Sprite is blitted at (GAME_WIDTH * 0.5, GAME_HEIGHT * 0.5).  Sample
        # a pixel just inside that origin and verify the alpha changed.
        sx = int(GAME_WIDTH * 0.5) + 32
        sy = int(GAME_HEIGHT * 0.5) + 32
        assert s.main_surface.get_at((sx, sy)).a != 0

    def test_events_handler_runs_without_error(self):
        s = RLState()
        s.events_handler([])
