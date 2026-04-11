from __future__ import annotations
import random
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from simulation.fs.directory import RootDir
    from simulation.fs.file_su import File, Directory
    from simulation.fs.storage_unit import StorageUnit
    from simulation.fs.user import User
    from simulation.node.op_sys import OperatingSystem, InvalidUserException, NotAFileException, NotADirectoryException, TooManyUsersException, UserNotFoundException, InvalidPermissionException, UsernameAlreadyExistsException, InvalidPasswordException, InvalidPathException


class FileSystemAccess(object):
    def __init__(self, os: OperatingSystem, fs: RootDir):
        self.os: OperatingSystem = os
        self.fs: RootDir = fs
        self.user: User | None = None

    @staticmethod
    def user_update_propogate(f):
        def wrapped(self, *args, **kwargs):
            res = f(self, *args, **kwargs)
            self.os.user_update_propogate()
            return res
        return wrapped

    @staticmethod
    def user_required(user_id: int | None = None):
        def decorator(f):
            def wrapped(self, *args, **kwargs):
                if user_id:
                    assert self.user.uid == user_id, "Invalid user. Transaction invalidated."
                else:
                    assert self.user is not None, "Invalid user. Transaction invalidated."

                return f(self, *args, **kwargs)
            return wrapped
        return decorator

    def validate_user(self, raw_user: User) -> bool:
        passwd_file = self.fs['etc']['passwd'].get_contents(0).decode()
        user_ids = set(map( lambda line: int(line.split(':')[2]), passwd_file.splitlines()))        
        return raw_user.uid in user_ids

    def get_su_at_path(self, path: str, base: str='/') -> StorageUnit:
        path = path.rstrip('/')
        if path[0] != '/':
            joiner = '/' if base[-1] != '/' else '' 
            path = base + joiner + path
        units = path.split('/')[1:]
        units = list(filter(lambda x: x != '.', units))
        current: StorageUnit = self.fs
        while len(units) != 0:
            to_traverse = units.pop(0)
            if isinstance(current, RootDir) and to_traverse == '..':
                raise InvalidPathException('Path is invalid.')
            current = current.parent if to_traverse == '..' else current[to_traverse]
        return current
    
    @user_required(0)
    @user_update_propogate
    def create_user(self, username: str, display_name: str, password: str) -> User:
        passwd_file = self.read_file('/etc/passwd').decode()
        user_ids = set(map(lambda line: int(line.split(':')[2]), passwd_file.splitlines()))
        usernames = list(map(lambda line: line.split(':')[0], passwd_file.splitlines()))
        if username in usernames:
            raise UsernameAlreadyExistsException(f'User with username {username} already exists.')
        if len(user_ids) >= 1000:
            raise TooManyUsersException("Too many users. Cannot create any more")
        new_userid = random.randint(1, 999)
        while new_userid in user_ids:
            new_userid = random.randint(1, 999)
        user = User.with_password(new_userid, username, password, display_name)
        self.append_to_file('/etc/passwd', f"{user.passwd_line}\n".encode('utf-8'))
        self.append_to_file('/etc/shadow', f"{user.shadow_line}\n".encode('utf-8'))

    @user_required(0)
    @user_update_propogate
    def delete_user(self, user: User):
        passwd_file = self.read_file('/etc/passwd').decode()
        shadow_file = self.read_file('/etc/shadow').decode()
        passwd_lines = passwd_file.splitlines()
        shadow_lines = shadow_file.splitlines()
        passwd_user_ids = list(map( lambda line: int(line.split(':')[2]), passwd_lines))
        shadow_user_ids = list(map( lambda line: int(line.split(':')[2]), shadow_lines))
        try:
            passwd_index = passwd_user_ids.index(user.uid)
            shadow_index = shadow_user_ids.index(user.uid)
            del passwd_lines[passwd_index]
            del shadow_lines[shadow_index]
            passwd_contents = '\n'.join(passwd_lines).encode('utf-8')
            shadow_contents = '\n'.join(shadow_lines).encode('utf-8')
            self.write_to_file('/etc/passwd', passwd_contents)
            self.write_to_file('/etc/shadow', shadow_contents)
            
        except ValueError:
            raise UserNotFoundException(f"user {user.display_name} not found.")

    @user_required()
    @user_update_propogate 
    def update_user(self, user_uid: int, username: str | None=None, display_name: str | None = None, password: str | None = None):
        
        new_user = (
            User.with_password(user_uid, 
                               username = username or self.user.username, 
                               password = password, 
                               display_name = display_name or self.user.display_name) 
            if password else 
            User.with_hashed_password(user_uid,
                                      username = username or self.user.username,
                                      password = self.user.hashed_password,
                                      display_name = display_name or self.user.display_name)
        )

        passwd_file = self.read_file('/etc/passwd').decode()
        shadow_file = self.read_file('/etc/shadow').decode()
        passwd_lines = passwd_file.splitlines()
        shadow_lines = shadow_file.splitlines()

        if new_user.uid != self.user.uid and self.user.uid != 0:
            items = list(map(lambda line: line.split(':'), passwd_lines))
            old_display_name = next(filter(lambda line: line[2] == str(new_user.uid) , items))[4]
            
            raise InvalidPermissionException(f"User {self.user.display_name} does not have permission to change {old_display_name}'s permissions")
        
        passwd_user_ids = list(map( lambda line: int(line.split(':')[2]), passwd_lines))
        shadow_user_ids = list(map( lambda line: int(line.split(':')[2]), shadow_lines))
        try:
            passwd_index = passwd_user_ids.index(new_user.uid)
            shadow_index = shadow_user_ids.index(new_user.uid)
            passwd_lines[passwd_index] = new_user.passwd_line
            shadow_lines[shadow_index] = new_user.shadow_line
            passwd_contents = '\n'.join(passwd_lines).encode('utf-8')
            shadow_contents = '\n'.join(shadow_lines).encode('utf-8')
            self.write_to_file('/etc/passwd', passwd_contents)
            self.write_to_file('/etc/shadow', shadow_contents)
            
        except ValueError:
            raise UserNotFoundException(f"user {new_user.display_name} not found.")

    def login_helper(self, username: str, password: str) -> User:
        passwd_lines = self.read_file('/etc/passwd').decode().splitlines()
        shadow_lines = self.read_file('/etc/shadow').decode().splitlines()
        try:
            passwd_line = next(filter(lambda line: line.partition(":")[0] == username, passwd_lines))
            shadow_line = next(filter(lambda line: line.partition(":")[0] == username, shadow_lines))
        except StopIteration:
            raise UserNotFoundException(f"user {username} not found.")

        real_password = shadow_line.split(':')[1]
        if User.verify_passwd(password, real_password):
            return User.from_files(passwd_line, shadow_line)
        else:
            raise InvalidPasswordException(f"Invalid Password")

    """
    CRUD FS
    """

    @user_required()
    def read_file(self, path: str, base='/') -> bytes:
        file: StorageUnit = self.get_su_at_path(path, base)
        if not isinstance(file, File):
            raise NotAFileException(f"{file.path} is not a file")
        return file.get_contents(self.user.uid)

    @user_required()
    def create_file(self, path: str, base='/') -> None:
        parent_path, file_name = path.rsplit('/', 1)
        parent: StorageUnit = self.get_su_at_path(parent_path, base)
        if not isinstance(parent, Directory):
            raise NotADirectoryException(f"{parent.path} is not a directory")
        parent.add(File(file_name, b'', self.user.uid), self.user.uid)

    @user_required()
    def write_to_file(self, path: str, contents: bytes, base='/'):
        file: StorageUnit = self.get_su_at_path(path, base)
        if not isinstance(file, File):
            raise NotAFileException(f"{file.path} is not a file")
        file.set_contents(contents, self.user.uid)

    @user_required()
    def append_to_file(self, path: str, contents: bytes, base='/'):
        file_contents = self.read_file(path, base)
        new_contents = file_contents + contents
        self.write_to_file(path, new_contents, base)

    @user_required()
    def delete_file(self, path: str, base='/') -> None:
        file : StorageUnit = self.get_su_at_path(path, base)
        if not isinstance(file, File):
            raise NotAFileException(f"{file.path} is not a file")
        file.parent.delete(file, self.user.uid)

    @user_required()
    def read_dir(self, path: str, base='/') -> list[File | Directory]:
        directory: StorageUnit = self.get_su_at_path(path, base)
        if not isinstance(directory, Directory):
            raise NotADirectoryException(f"{directory.path} is not a directory")
        return directory.get_contents(self.user.uid)

    @user_required()
    def create_dir(self, path: str, base='/') -> None:
        parent_path, dir_name = path.rsplit('/', 1)
        parent: StorageUnit = self.get_su_at_path(parent_path, base)
        if not isinstance(parent, Directory):
            raise NotADirectoryException(f"{parent.path} is not a directory")
        parent.add(Directory(dir_name, [], self.user.uid), self.user.uid)

    @user_required()
    def delete_dir(self, path: str, base='/') -> None:
        direc : StorageUnit = self.get_su_at_path(path, base)
        if not isinstance(direc, Directory):
            raise NotADirectoryException(f"{direc.path} is not a directory")
        direc.parent.delete(direc, self.user.uid)


class Transaction(object):
    def __init__(self, fs_access: FileSystemAccess, user: User):
        self.fs_access: FileSystemAccess = fs_access
        self.user: User = user

    def __enter__(self, *args):
        if not self.fs_access.validate_user(self.user):
            raise InvalidUserException(f"user {self.user.display_name} does not exist.")
        self.fs_access.user = self.user
        return self
    
    def __exit__(self, *args):
        self.fs_access.user = None
