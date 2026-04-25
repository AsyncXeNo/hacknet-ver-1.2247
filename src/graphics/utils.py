import random
import string
from threading import Lock

from loguru_config import get_subsystem_logger

lock = Lock()

GENERATED_IDS: list[str] = []

logger = get_subsystem_logger('graphics.utils')


def generate_id(length: int = 4) -> str:
    """Generates, stores and returns a random ID with the given length (default 4)"""

    with lock:
        while True:
            new_id = "".join(random.choices(string.ascii_uppercase, k=length))
            if new_id in GENERATED_IDS:
                continue
            GENERATED_IDS.append(new_id)
            break

        return new_id
