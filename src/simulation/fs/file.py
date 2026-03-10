from __future__ import annotations
from typing import TYPE_CHECKING
from fs.storage_unit import StorageUnit
from better_exceptions import LoggingException
from loguru_config import get_subsystem_logger
import inspect

if TYPE_CHECKING:
    from fs.directory import Directory


class FileError(LoggingException):
    def __init__(self, message, *args):
        logger = get_subsystem_logger('fs')
        super().__init__(logger, message, *args)


class File(StorageUnit):
    """Class representing a file in the virtual file system"""

    def __init__(self, parent: Directory, name: str, contents: str | bytes, owner_uid: int) -> None:

        self.filename: str
        self.extension: str | None

        super().__init__(parent, name, contents, owner_uid)

    @property
    def name(self) -> str:
        ext = f".{self.extension}" if self.extension else ""
        return self.filename + ext

    @property
    def path(self) -> str:
        return f'{self.parent.path}{self.name}'

    def __setattr__(self, name, value):

        frame = inspect.currentframe().f_back
        caller_self = frame.f_locals.get("self")

        assert caller_self is self, "Use the function"

        if name == 'name':
            self._validate_name(name)

            namesplit = value.split('.')
            
            if len(namesplit) < 2:
                self.filename = namesplit[0]
                self.extension = None

            else:
                self.filename = '.'.join(namesplit[:-1])
                self.extension = namesplit[-1]

            return
        
        super().__setattr__(name, value)


    # Validation

    def _validate_contents(self, contents: str | bytes) -> None:
        """Checks if the contents are valid"""
        
        super()._validate_contents(contents)

        if isinstance(contents, list):
            raise FileError('File\'s contents need to be of one of the following types -> str, bytes')