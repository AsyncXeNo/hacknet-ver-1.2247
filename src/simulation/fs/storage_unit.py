from __future__ import annotations
from typing import TYPE_CHECKING, Any
from simulation.fs.constants import INVALID_CHARACTERS
from better_exceptions import LoggingException
from loguru_config import get_subsystem_logger
from simulation.fs.permissions import Permissions, PermTriplet
from enum import Enum
import inspect

if TYPE_CHECKING:
    from fs.directory import Directory


class Action(Enum):
    READ=0
    WRITE=1
    EXECUTE=2


class StorageUnitError(LoggingException):
    def __init__(self, message, *args):
        super().__init__(logger=get_subsystem_logger('fs'), message=message, *args)

        
class FSPermissionError(StorageUnitError):
    def __init__(self, message, *args):
        super().__init__(message=message, *args)



class StorageUnit(object):
    """Class representing a storage unit in the virtual file system"""

    def __init__(self, parent: Directory, name: str, contents: str | bytes | list[StorageUnit], owner_uid: int) -> None:

        self.owner_uid: int = owner_uid
        self.permissions: Permissions = Permissions(PermTriplet(True, True, True),
                                                    PermTriplet(False, True, False))
        self.parent: Directory = parent
        self.name: str = name
        self.contents: str | bytes | list[StorageUnit] = contents

    def __setattr__(self, name, value):

        frame = inspect.currentframe().f_back
        caller_self = frame.f_locals.get("self")

        assert caller_self is self, "Use the functions"

        match(name):
            case "parent":
                self._validate_parent(value)
            case "name":
                self._validate_name(value)
            case "contents":
                self._validate_contents(value)
        
        super().__setattr__(name, value)

    def __getattribute__(self, name):
        
        if name == "contents":
            frame = inspect.currentframe().f_back
            caller_self = frame.f_locals.get("self")

            assert caller_self is self, "Use the function"

        return super().__getattribute__(name)

    def get_contents(self, user_uid: int) -> str | bytes | list[StorageUnit]:
        if not self.has_permission(user_uid, Action.READ):
            raise FSPermissionError(f"user {user_uid} doesn't have permission to read contents")
        return self.contents

    def set_parent(self, parent: Directory, user_uid: int) -> None:
        if not self.has_permission(user_uid, Action.WRITE):
            raise FSPermissionError(f"user {user_uid} doesn't have permission to change this su's parent")
        if not parent.has_permission(user_uid, Action.WRITE):
            raise FSPermissionError(f"user {user_uid} doesn't have write permissions for the new parent directory")
        self.parent = parent

    def set_name(self, name: str, user_uid: int) -> None:
        if not self.has_permission(user_uid, Action.WRITE):
            raise FSPermissionError(f"user {user_uid} doesn't have permission to change name")
        self.name = name
        
    def set_contents(self, contents: str | bytes | list[StorageUnit], user_uid: int) -> None:
        if not self.has_permission(user_uid, Action.WRITE):
            raise FSPermissionError(f"user {user_uid} doesn't have permission to set contents")
        self.contents = contents

    def set_owner(self, new_owner_uid: int, user_uid: int) -> None:
        if user_uid != 1:
            raise FSPermissionError(f"user {user_uid} doesn't have permission to set owner")
        self.owner_uid = new_owner_uid

    def set_permissions(self, new_permissions: Permissions, user_uid: int) -> None:
        if user_uid not in [1, self.owner_uid]:
            raise FSPermissionError(f"user {user_uid} doesn't have permissions to change permissions")
        self.permissions = new_permissions

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

    # Helper functions

    def has_permission(self, user_id: int, action: Action) -> bool:
        if user_id == 1: return True
        perms = self.permissions[self.owner_uid != user_id]
        return perms[action.value]

    # Magic functions

    def __str__(self) -> str:
        return self.path