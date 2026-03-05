from loguru import logger
from loguru_config import remove_default_logger, configure_master_logger

if __name__ == "__main__":
    remove_default_logger()
    configure_master_logger()

    logger.debug('Hi')
    logger.warning('Hello')
