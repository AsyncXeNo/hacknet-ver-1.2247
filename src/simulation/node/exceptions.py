
from better_exceptions import LoggingException
from loguru_config import get_subsystem_logger


class OSException(LoggingException):
    def __init__(self, message, *args):
        super().__init__(logger=get_subsystem_logger('os'), message=message, *args)

class PortInUseException(OSException):
    def __init__(self, message, *args):
        super().__init__(message=message, *args)

class InvalidUserException(OSException):
    def __init__(self, message, *args):
        super().__init__(message=message, *args)

class NotAFileException(OSException):
    def __init__(self, message, *args):
        super().__init__(message=message, *args)

class NotADirectoryException(OSException):
    def __init__(self, message, *args):
        super().__init__(message=message, *args)

class TooManyUsersException(OSException):
    def __init__(self, message, *args):
        super().__init__(message=message, *args)

class UserNotFoundException(OSException):
    def __init__(self, message, *args):
        super().__init__(message=message, *args)

class InvalidPermissionException(OSException):
    def __init__(self, message, *args):
        super().__init__(message=message, *args)

class UsernameAlreadyExistsException(OSException):
    def __init__(self, message, *args):
        super().__init__(message=message, *args)

class InvalidPasswordException(OSException):
    def __init__(self, message, *args):
        super().__init__(message=message, *args)

class InvalidPathException(OSException):
    def __init__(self, message, *args):
        super().__init__(message=message, *args)