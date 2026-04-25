from loguru_config import remove_default_logger, configure_master_logger, get_subsystem_logger

remove_default_logger()
configure_master_logger()

from game.manager import game_manager
from game.states.main_menu import MainMenuState


if __name__ == "__main__":
    

    game_manager.push_state(MainMenuState())
    game_manager.main_loop()