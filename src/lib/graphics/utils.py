from loguru import logger


def get_dimensions(width: int | None = None, height: int | None = None, ratio: tuple[int, int] = (1, 1)) -> tuple[int, int] | None:
    """Returns the other dimension of a surface given one dimension and the width-to-height ratio"""

    if height is None and width is None:
        logger.warning('None of the dimensions provided in get_dimensions function. This might break the application')
        return 1, 1

    elif height is not None and width is not None:
        return width, height

    elif height is not None:
        return (height // ratio[1]) * ratio[0], height

    elif width is not None:
        return width, (width // ratio[0]) * ratio[1]
