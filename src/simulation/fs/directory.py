from __future__ import annotations
from fs.storage_unit import StorageUnit
from better_exceptions import LoggingException
from loguru_config import get_subsystem_logger

class DirectoryError(LoggingException):
    def __init__(self, message, *args):
        logger = get_subsystem_logger('fs')
        super().__init__(logger, message, *args)

class RootDirError(LoggingException):
    def __init__(self, message, *args):
        logger = get_subsystem_logger('fs')
        super().__init__(logger, message, *args)


class Directory(StorageUnit):
    """Class representing a directory in the virtual file system"""

    @property
    def path(self) -> str:
        """Returns the directory's absolute path"""
        return f'{self.parent.path}{"/" if not isinstance(self.parent, RootDir) else ""}{self.get_name()}'

    def __contains__(self, item):
        if isinstance(item, str):
            return item in list(map(lambda su: su.name, self.contents))
        else:
            return item in self.contents

    def __getitem__(self, key) -> StorageUnit:
        try:
            pred = lambda su: su.name == key
            element = next(filter(pred, self.contents))
            return element
        except StopIteration:
            raise DirectoryError(f"Directory does not have storage unit {key}")


    # Getters
    def get_contents_sorted(self) -> str |  bytes | list[StorageUnit]:
        return sorted(self.contents, key=lambda su: su.__class__.__name__)


    # Operations
    def add(self, su: StorageUnit) -> None:
        """Adds a storage unit to the contents (handles parent)"""

        self._validate_directory_element(su)

        if self.get_su_by_name(su.get_name()) is not None:
            raise DirectoryError('Directory cannot have more than 1 storage units with the same name')

        if su.parent != self:
            if su.parent:
                su.parent.delete(su)
            su.set_parent(self)
        self.contents.append(su)


    def delete(self, su: StorageUnit) -> None:
        """Deletes a storage unit from the contents"""

        try:
            self.contents.remove(su)
        except ValueError:
            self.logger.warning('Given storage unit is not a child. Ignoring delete request')


    # Validation

    def _validate_contents(self, contents: list[StorageUnit]) -> None:
        "Checks if the contents are valid"

        if not isinstance(contents, list):
            raise DirectoryError("Directory contents need to be of type list")

        for element in contents:
            self._validate_directory_element(element)

        for element in contents:
            if len(list(filter(lambda su, element = element: su.get_name() == element.get_name(), contents))) > 1:
                raise DirectoryError('Directory cannot have more than 1 storage units with the same name')

    def _validate_directory_element(self, element: StorageUnit) -> None:
        """Checks if the directory element is valid"""

        if not isinstance(element, StorageUnit):
            raise DirectoryError("Units in the directory need to be of type StorageUnit")


class RootDir(Directory):
    """Class representing the root directory in the virtual file system"""

    def __init__(self, contents: list[StorageUnit] = []) -> None:
        super().__init__(None, '', contents)

    @property
    def path(self) -> str:
        """Returns the path of the root directory"""
        return '/'

    # Validation
    def _validate_name(self, name: str) -> None:
        """Checks if the name is valid"""

        if name != "":
            raise RootDirError('Root directory cannot have a name')

    def _validate_parent(self, parent: None) -> None:
        """Checks if the parent is valid"""

        if parent is not None:
            raise RootDirError('Root directory cannot have a parent')