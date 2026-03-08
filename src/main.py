from loguru import logger
from loguru_config import remove_default_logger, configure_master_logger, get_subsystem_logger

if __name__ == "__main__":
    remove_default_logger()
    configure_master_logger()

    logger = get_subsystem_logger('test')

    logger.debug('Hi')
    logger.warning('Hello')