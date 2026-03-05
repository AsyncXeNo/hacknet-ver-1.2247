import json
import random
import string
from typing import Optional

from loguru import logger

GENERATED_IDS_PATH: str = "data/generated_ids.json"


def generate_id(length: int = 4) -> Optional[str]:
    """Generates, stores and returns a random ID with the given length (default 4)"""

    # Trying to read the file
    try:
        with open(GENERATED_IDS_PATH, "r") as f:
            generated = json.load(f)

        if not isinstance(generated, list):
            raise TypeError

    # File probably has some issues. Creating a new empty file
    except (FileNotFoundError, json.decoder.JSONDecodeError, TypeError) as e:
        logger.warning(f"Encountered an error while generating ID [{e}]. Trying to fix")

        try:
            open(GENERATED_IDS_PATH, "w")

            # Generating ID and setting it as the only generated ID
            new_id = "".join(random.choices(string.ascii_uppercase, k=length))
            generated = [new_id]

        # Directory not found
        except FileNotFoundError:
            logger.error(
                f"Directory <{'/'.join(GENERATED_IDS_PATH.split('/')[:-1])}> not found. The application will continue to run but no ID will be returned"
            )
            return None

    # Generating ID
    else:
        while True:
            new_id = "".join(random.choices(string.ascii_uppercase, k=length))

            if new_id not in generated:
                generated.append(new_id)
                break

    # Storing ID
    with open(GENERATED_IDS_PATH, "w") as f:
        json.dump(generated, f, indent=2)

    return new_id
