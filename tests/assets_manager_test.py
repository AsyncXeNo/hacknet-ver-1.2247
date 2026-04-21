from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import SimpleNamespace

import pygame
import pytest
from PIL import Image, PngImagePlugin

pygame.font.init()
pygame.display.init()


@pytest.fixture(scope='session', autouse=True)
def _pygame_display():
    pygame.display.set_mode((1, 1))
    yield
    pygame.display.quit()


REAL_FONT = (
    Path(__file__).parent.parent
    / 'assets' / 'fonts' / 'Krypton' / 'Regular.ttf'
)


def _write_sheet(path: Path, cols: int, rows: int, sw: int, sh: int) -> None:
    img = Image.new('RGBA', (sw * cols, sh * rows), (10, 20, 30, 255))
    meta = PngImagePlugin.PngInfo()
    meta.add_text('sprite_width', str(sw))
    meta.add_text('sprite_height', str(sh))
    img.save(path, pnginfo=meta)


@pytest.fixture
def asset_tree(tmp_path):
    """Layout AssetsManager expects:

    tmp_path/
      images/spritesheets/mc/idle.png       (4x2 grid of 16x24)
      images/spritesheets/mc/walk.png       (8x1 grid of 16x24)
      fonts/Krypton/Regular.ttf
      fonts/Krypton/Bold.ttf
    """
    images = tmp_path / 'images'
    mc = images / 'spritesheets' / 'mc'
    mc.mkdir(parents=True)
    _write_sheet(mc / 'idle.png', cols=4, rows=2, sw=16, sh=24)
    _write_sheet(mc / 'walk.png', cols=8, rows=1, sw=16, sh=24)

    fonts = tmp_path / 'fonts'
    family = fonts / 'Krypton'
    family.mkdir(parents=True)
    font_bytes = REAL_FONT.read_bytes()
    (family / 'Regular.ttf').write_bytes(font_bytes)
    (family / 'Bold.ttf').write_bytes(font_bytes)

    return SimpleNamespace(root=tmp_path, images=images, fonts=fonts)


@pytest.fixture
def am_module(asset_tree, monkeypatch):
    """Point constants at the synthetic asset tree and re-import the module
    so its top-level AssetsManager() runs against the patched paths."""
    import graphics.constants as consts
    monkeypatch.setattr(consts, 'IMAGE_PATH', asset_tree.images)
    monkeypatch.setattr(consts, 'FONTS_PATH', asset_tree.fonts)
    # FONT_VARIATIONS has a missing-comma bug in graphics.constants; patch a
    # sane list here so the rest of the tests exercise AssetsManager itself.
    # TestConstants::test_font_variations_has_no_implicit_concatenation
    # asserts on the real constant.
    monkeypatch.setattr(
        consts, 'FONT_VARIATIONS',
        ['Regular.ttf', 'Bold.ttf', 'Italic.ttf', 'BoldItalic.ttf'],
    )
    sys.modules.pop('graphics.assets_manager', None)
    return importlib.import_module('graphics.assets_manager')


@pytest.fixture
def am(am_module):
    return am_module.AssetsManager()


# ─── Spritesheet processing ──────────────────────────────────────────────────


class TestSpritesheets:
    def test_img_property_returns_processed_images(self, am):
        assert am.img is am.processed_images

    def test_spritesheets_grouped_by_folder(self, am):
        assert hasattr(am.img.spritesheets, 'mc')

    def test_frame_count_matches_grid(self, am):
        assert len(am.img.spritesheets.mc.idle) == 8   # 4 cols * 2 rows
        assert len(am.img.spritesheets.mc.walk) == 8   # 8 cols * 1 row

    def test_frames_are_pygame_surfaces(self, am):
        assert all(
            isinstance(s, pygame.Surface)
            for s in am.img.spritesheets.mc.idle
        )

    def test_frames_have_sprite_dimensions(self, am):
        for s in am.img.spritesheets.mc.idle:
            assert s.get_size() == (16, 24)

    def test_missing_sprite_metadata_raises(self, asset_tree, am_module):
        bad = asset_tree.images / 'spritesheets' / 'bad'
        bad.mkdir()
        Image.new('RGBA', (32, 32)).save(bad / 'nometa.png')
        with pytest.raises(AssertionError):
            am_module.AssetsManager()

    def test_non_divisible_sprite_size_raises(self, asset_tree, am_module):
        odd = asset_tree.images / 'spritesheets' / 'odd'
        odd.mkdir()
        img = Image.new('RGBA', (33, 24))
        meta = PngImagePlugin.PngInfo()
        meta.add_text('sprite_width', '16')
        meta.add_text('sprite_height', '24')
        img.save(odd / 'odd.png', pnginfo=meta)
        with pytest.raises(AssertionError):
            am_module.AssetsManager()

    def test_non_png_file_in_sheet_dir_raises(self, asset_tree, am_module):
        (asset_tree.images / 'spritesheets' / 'mc' / 'notes.txt').write_text('x')
        with pytest.raises(AssertionError):
            am_module.AssetsManager()


# ─── Fonts ───────────────────────────────────────────────────────────────────


class TestFonts:
    def test_fonts_grouped_by_family(self, am, am_module):
        assert am_module.FONTS is not None
        assert hasattr(am_module.FONTS, 'Krypton')

    def test_font_variations_strip_ttf_suffix(self, am, am_module):
        krypton = am_module.FONTS.Krypton
        assert hasattr(krypton, 'Regular')
        assert hasattr(krypton, 'Bold')

    def test_font_paths_point_at_real_files(self, am, am_module):
        assert Path(am_module.FONTS.Krypton.Regular).is_file()

    def test_unknown_font_filename_raises(self, asset_tree, am_module):
        (asset_tree.fonts / 'Krypton' / 'Weird.ttf').write_bytes(b'x')
        with pytest.raises(AssertionError):
            am_module.AssetsManager()

    def test_non_directory_in_fonts_raises(self, asset_tree, am_module):
        (asset_tree.fonts / 'loose.ttf').write_bytes(b'x')
        with pytest.raises(AssertionError):
            am_module.AssetsManager()


# ─── get_font ────────────────────────────────────────────────────────────────


class TestGetFont:
    def test_returns_font_instance(self, am):
        """Annotated `-> Font` but currently has no return statement — this
        test fails until the return is added."""
        f = am.get_font(REAL_FONT, 16)
        assert isinstance(f, pygame.font.Font)

    def test_caches_by_path_and_size(self, am):
        f1 = am.get_font(REAL_FONT, 16)
        f2 = am.get_font(REAL_FONT, 16)
        assert f1 is f2

    def test_different_sizes_are_not_shared(self, am):
        assert am.get_font(REAL_FONT, 12) is not am.get_font(REAL_FONT, 24)


# ─── Constants regressions ───────────────────────────────────────────────────


class TestConstants:
    def test_font_variations_has_no_implicit_concatenation(self):
        """Regression for missing comma between 'LightItalic.ttf' and
        'Regular.ttf' in graphics.constants.FONT_VARIATIONS — Python
        concatenates them into 'LightItalic.ttfRegular.ttf'."""
        from graphics.constants import FONT_VARIATIONS
        assert 'Regular.ttf' in FONT_VARIATIONS
        assert 'LightItalic.ttf' in FONT_VARIATIONS
