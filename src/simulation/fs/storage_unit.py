from __future__ import annotations
from typing import TYPE_CHECKING, Any
from simulation.fs.constants import INVALID_CHARACTERS
from better_exceptions import LoggingException
from loguru_config import get_subsystem_logger

if TYPE_CHECKING:
    from fs.directory import Directory


class StorageUnitError(LoggingException):
    def __init__(self, message, *args):
        super().__init__(logger=get_subsystem_logger('fs'), message=message, *args)


class StorageUnit(object):
    """Class representing a storage unit in the virtual file system"""

    def __init__(self, parent: Directory, name: str, contents: str | bytes | list[StorageUnit]) -> None:

        self._validate_parent(parent)
        self.parent: Directory = parent

        self.set_name(name)

        self._validate_contents(contents)
        self.contents: str | bytes | list[StorageUnit] = contents

        self.metadata: dict[str, Any] = {}

    def __setattr__(self, name, value):
        match(name):
            case "parent":
                self._validate_parent(value)
            case "name":
                self._validate_name(value)
            case "contents":
                self._validate_contents(value)
        
        super().__setattr__(name, value)

    # Validation

    def _validate_parent(self, parent: Directory) -> None:
        """Checks if the parent is valid"""

        from fs.directory import Directory

        if not isinstance(parent, Directory):
            raise StorageUnitError('Storage unit\'s parent needs to be of type Directory.')
    
    def _validate_name(self, name: str) -> None:
        """Checks if the name is valid"""

        if not isinstance(name, str):
            raise StorageUnitError('Storage unit\'s name needs to be of type str.')

        if len(name) < 1:
            raise StorageUnitError('Storage unit\'s name needs to be atleast 1 character long.')

        if len(name) > 50:
            raise StorageUnitError('Storage unit\'s name can only be atmost 50 character long.')

        for letter in name:
            if letter in INVALID_CHARACTERS:
                raise StorageUnitError(f'Storage unit\'s name cannot have any of the following characters -> {INVALID_CHARACTERS}')

    def _validate_contents(self, contents: str | bytes | list[StorageUnit]) -> None:
        """Checks if the contents are valid"""

        if not (isinstance(contents, str) or isinstance(contents, bytes) or isinstance(contents, list)):
            raise StorageUnitError('Storage unit\'s contents need to be of one of the following types -> str, bytes, list[StorageUnit]')

    # Magic functions

    def __str__(self) -> str:
        
        return self.get_path()


