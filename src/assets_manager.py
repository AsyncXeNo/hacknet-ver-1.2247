import os
from typing import Any
from pathlib import Path

import pygame
from pygame.font import Font
from PIL import Image, UnidentifiedImageError
from types import SimpleNamespace
from functools import cache

from graphics.constants import FONT_VARIATIONS, IMAGE_PATH, AUDIOS_PATH, FONTS_PATH
from loguru_config import get_subsystem_logger

logger = get_subsystem_logger('graphics.assets_manager')

FONTS = None


class AssetsManager(object):

    @property
    def img(self):
        return self.processed_images

    def __init__(self):
        self.processed_images = SimpleNamespace()
        
        self.process_spritesheets()
        self.get_available_fonts()

    @cache
    def get_font(self, path: Path, size: int) -> Font:
        return Font(path, size)
    
    def get_available_fonts(self):
        global FONTS
        temp = dict()
        logger.info("Loading fonts...")
        for dir_name in os.listdir(FONTS_PATH):
            current_dir = FONTS_PATH / dir_name
            assert os.path.isdir(current_dir), f'{current_dir} is not a folder'
            font_dir = dict()
            for font_file in os.listdir(current_dir):
                current_font = current_dir / font_file
                assert os.path.isfile(current_font) and font_file in FONT_VARIATIONS, f"{current_font} is not a proper font file"
                proc_font = font_file.removesuffix(".ttf")
                font_dir[proc_font] = current_font.resolve()
                logger.info(f"Loaded {dir_name}/{proc_font}!")
            temp[dir_name] = SimpleNamespace(**font_dir)
        logger.info(f"Done loading fonts!")
        FONTS = SimpleNamespace(**temp)
        
    def process_spritesheets(self):
        path = IMAGE_PATH / 'spritesheets'
        temp = dict()
        for folder in os.listdir(path):
            current_folder = path / folder
            assert os.path.isdir(current_folder), f'{current_folder} is not a folder'

            temp[folder] = self.process_spritesheet_directory(Path(current_folder))
        self.processed_images.spritesheets = SimpleNamespace(**temp)

    def process_spritesheet_directory(self, path: Path) -> SimpleNamespace:
        temp = dict()
        for su_name in os.listdir(path):
            current_su = path / su_name
            if os.path.isdir(current_su):
                temp[su_name] = self.process_spritesheet_directory(current_su)
            else:
                assert su_name.endswith('.png'), f'{current_su} is not a valid image'
                try:
                    image = Image.open(current_su)
                except UnidentifiedImageError:
                    logger.error(f'{current_su} could not be loaded. Skipping...')
                    continue

                image_surf = pygame.image.load(current_su).convert_alpha()

                image_width = image.width
                image_height = image.height
                
                sprite_width = int(image.info.get('sprite_width', 0))
                sprite_height = int(image.info.get('sprite_height', 0))

                assert sprite_width and sprite_height, f'Sprite metadata not set for {current_su}'
                
                assert image_width % sprite_width == 0 and image_height % sprite_height == 0, f"The sprite size of {current_su} doesn't divide evenly with image size" 

                num_cols = image_width // sprite_width
                num_rows = image_height // sprite_height
                
                sprites = []
                for i in range(num_rows):
                    for j in range(num_cols):
                        sprite = image_surf.subsurface((sprite_width * j, 
                                                        sprite_height * i, 
                                                        sprite_width,
                                                        sprite_height))
                        sprites.append(sprite)
                        
                temp[su_name.removesuffix('.png')] = sprites

        return SimpleNamespace(**temp)


assets_manager: AssetsManager = AssetsManager()