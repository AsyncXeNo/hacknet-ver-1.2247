from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from loguru import Logger
    
import traceback


class LoggingException(Exception):
    def __init__(self, logger: Logger, message: str) -> None:
        self.logger: Logger = logger
        self.message: str = message
        self.logger.error(f'{self.__class__}: {message}\n{traceback.format_exc()}')