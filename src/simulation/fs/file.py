from __future__ import annotations
from typing import TYPE_CHECKING
from fs.storage_unit import StorageUnit
from better_exceptions import LoggingException
from loguru_config import get_subsystem_logger

if TYPE_CHECKING:
    from fs.directory import Directory

class FileError(LoggingException):
    def __init__(self, message, *args):
        logger = get_subsystem_logger('fs')
        super().__init__(logger, message, *args)

class File(StorageUnit):
    """Class representing a file in the virtual file system"""

    def __init__(self, parent: Directory, name: str, contents: str | bytes) -> None:

        self.filename: str
        self.extension: str | None

        super().__init__(parent, name, contents)

    @property
    def name(self) -> str:
        ext = f".{self.extension}" if self.extension else ""
        return self.filename + ext

    @property
    def path(self) -> str:
        return f'{self.parent.get_path()}{self.get_name()}'

    def __setattr__(self, name, value): 
        match(name):
            case "name":
                self._validate_name(name)

                namesplit = value.split('.')
                
                if len(namesplit) < 2:
                    self.filename = namesplit[0]
                    self.extension = None

                else:
                    self.filename = '.'.join(namesplit[:-1])
                    self.extension = namesplit[-1]
                return

        super(object).__setattr__(name, value)

    # Validation

    def _validate_contents(self, contents: str | bytes) -> None:
        """Checks if the contents are valid"""
        
        super()._validate_contents(contents)

        if isinstance(contents, list):
            raise FileError('File\'s contents need to be of one of the following types -> str, bytes')

