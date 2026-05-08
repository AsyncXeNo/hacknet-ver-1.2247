# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "pillow>=12.2.0",
#     "pydantic-settings>=2.13.1",
# ]
# ///

import os
from PIL import Image, PngImagePlugin, UnidentifiedImageError

from pydantic import DirectoryPath
from pydantic_settings import BaseSettings, SettingsConfigDict


IMAGES_DIR = ""

class Settings(BaseSettings):
    input_dir: DirectoryPath

    model_config = SettingsConfigDict(
        cli_parse_args=True,
        cli_kebab_case=True
    )


def main() -> None:
    settings = Settings()
    
    for su_name in os.listdir(settings.input_dir):
        current_su = settings.input_dir / su_name

        if os.path.isdir(current_su):
            continue

        try:
            image = Image.open(current_su)
        except UnidentifiedImageError:
            print(f'{current_su} is not a valid image. Skipping.')
            continue

        if (width:=image.info.get('sprite_width')) and (height:=image.info.get('sprite_height')):
            print(f'Sprite metadata already set for {current_su}: {width}x{height}')
            continue
        
        while True:
            size = input(f'Sprite size ({current_su}): ').lower()
            try:
                width, height = map(int, size.split('x'))
                if not image.width % width == 0:
                    print('Image width doesnt divide evenly with provided width. Try again.')
                    continue
                if not image.height % height == 0:
                    print('Image height doesnt divide evenly with provided height. Try again.')
                    continue
                    
            except:
                print('Invalid input. Try again.')
            else:
                break

        meta = PngImagePlugin.PngInfo()

        for k, v in image.info.items():
            if isinstance(v, str):
                meta.add_text(k, v)
        
        meta.add_text('sprite_width', str(width))
        meta.add_text('sprite_height', str(height))

        image.save(current_su, pnginfo=meta)

        
if __name__ == "__main__":
    main()