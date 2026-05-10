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
from game.objects.player import Player
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
        components = vars(s.components).values()
        labels = [c for c in components if isinstance(c, Label)]
        buttons = [c for c in components if isinstance(c, Button)]
        assert len(labels) == 1
        assert len(buttons) == 4

    def test_heading_label_text(self):
        s = MainMenuState()
        assert s.components.title.text == "HACKNET"

    def test_button_labels_in_expected_order(self):
        s = MainMenuState()
        actual = [
            s.components.new_game_button.text,
            s.components.continue_button.text,
            s.components.options_button.text,
            s.components.quit_button.text,
        ]
        assert actual == ["New Game", "Continue", "Options", "Quit"]

    def test_new_game_button_wires_real_callback(self):
        """`new_game_button` is wired to the module-level `new_game` function
        (pops main menu and pushes RLState); other buttons are no-op lambdas."""
        s = MainMenuState()
        assert s.components.new_game_button.on_click is new_game
        assert s.components.continue_button.on_click is not new_game

    def test_events_handler_runs_without_error(self, monkeypatch):
        s = MainMenuState()
        # Mouse outside every component so no callback fires.
        monkeypatch.setattr(pygame.mouse, 'get_pos', lambda: (-1, -1))
        s.events_handler([])


# ─── RLState ─────────────────────────────────────────────────────────────────


class TestRLState:
    def test_constructs_without_error(self):
        RLState()

    def test_has_player_component(self):
        s = RLState()
        assert isinstance(s.components.player, Player)

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
