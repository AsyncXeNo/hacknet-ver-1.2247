from __future__ import annotations
import pytest
from simulation.fs.directory import RootDir, Directory, DirectoryError, RootDirError
from simulation.fs.file_su import File, FileError
from simulation.fs.storage_unit import StorageUnit, StorageUnitError, FSPermissionError, Action
from simulation.fs.permissions import Permissions, PermTriplet
from simulation.fs.user import User

ROOT_UID = 0
USER_UID = 100
OTHER_UID = 999


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def fs():
    """Basic filesystem: / -> home/ -> alice/ -> readme.txt"""
    root = RootDir()

    home = Directory('home', [], ROOT_UID, root)
    root.add(home, ROOT_UID)

    user_dir = Directory('alice', [], USER_UID, home)
    home.add(user_dir, ROOT_UID)

    readme = File('readme.txt', 'hello world', USER_UID, user_dir)
    user_dir.add(readme, USER_UID)

    return root


@pytest.fixture
def root():
    return RootDir()


# ─── StorageUnit Validation ──────────────────────────────────────────────────


class TestStorageUnitValidation:
    def test_name_empty_string_rejected(self, root):
        with pytest.raises(StorageUnitError):
            Directory('', [], ROOT_UID, root)

    def test_name_too_long_rejected(self, root):
        with pytest.raises(StorageUnitError):
            Directory('a' * 51, [], ROOT_UID, root)

    def test_name_boundary_values(self, root):
        """Exactly 1 and 50 chars should pass; 0 and 51 should fail."""
        assert Directory('x', [], ROOT_UID, root).name == 'x'
        assert Directory('a' * 50, [], ROOT_UID, root).name == 'a' * 50

    def test_name_with_slash_rejected(self, root):
        with pytest.raises(StorageUnitError):
            Directory('foo/bar', [], ROOT_UID, root)

    def test_name_with_null_rejected(self, root):
        with pytest.raises(StorageUnitError):
            Directory('foo\0bar', [], ROOT_UID, root)

    def test_name_not_string_rejected(self, root):
        with pytest.raises(StorageUnitError):
            Directory(123, [], ROOT_UID, root)

    def test_parent_not_directory_rejected(self, root):
        f = File('dummy.txt', 'x', ROOT_UID, root)
        with pytest.raises(StorageUnitError):
            Directory('child', [], ROOT_UID, f)

    def test_contents_invalid_type_rejected(self, root):
        with pytest.raises(StorageUnitError):
            StorageUnit('bad', 12345, ROOT_UID, root)

    def test_external_attr_set_blocked(self, root):
        """__setattr__ guard: setting attrs from outside the object should assert."""
        f = File('test.txt', 'data', ROOT_UID, root)
        with pytest.raises(AssertionError):
            f.contents = 'hacked'

    def test_external_contents_read_blocked(self, root):
        """__getattribute__ guard: reading .contents from outside should assert."""
        f = File('test.txt', 'data', ROOT_UID, root)
        with pytest.raises(AssertionError):
            _ = f.contents


# ─── StorageUnit Permissions ─────────────────────────────────────────────────


class TestStorageUnitPermissions:
    def test_default_perms_owner_rwx_others_write_only(self, root):
        """Default: owner=rwx, others=-w-. Verify the actual dispatch logic."""
        f = File('test.txt', 'data', USER_UID, root)
        assert f.has_permission(USER_UID, Action.READ) is True
        assert f.has_permission(USER_UID, Action.EXECUTE) is True
        assert f.has_permission(OTHER_UID, Action.READ) is False
        assert f.has_permission(OTHER_UID, Action.WRITE) is True
        assert f.has_permission(OTHER_UID, Action.EXECUTE) is False

    def test_root_bypasses_all_zero_permissions(self, root):
        """Root (uid=1) should bypass even fully zeroed-out permissions."""
        f = File('test.txt', 'data', USER_UID, root)
        f.set_permissions(
            Permissions(PermTriplet(False, False, False), PermTriplet(False, False, False)),
            USER_UID,
        )
        assert f.has_permission(ROOT_UID, Action.READ) is True
        assert f.has_permission(ROOT_UID, Action.WRITE) is True
        assert f.has_permission(ROOT_UID, Action.EXECUTE) is True

    def test_every_setter_enforces_write_permission(self, root):
        """set_contents and set_name both require WRITE; lock owner out and verify."""
        f = File('test.txt', 'data', USER_UID, root)
        f.set_permissions(
            Permissions(PermTriplet(True, False, True), PermTriplet(False, False, False)),
            USER_UID,
        )
        with pytest.raises(FSPermissionError):
            f.set_contents('new', USER_UID)
        with pytest.raises(FSPermissionError):
            f.set_name('new.txt', USER_UID)

    def test_get_contents_enforces_read_permission(self, root):
        f = File('test.txt', 'data', USER_UID, root)
        with pytest.raises(FSPermissionError):
            f.get_contents(OTHER_UID)  # others lack read by default

    def test_set_owner_only_root_can_do_it(self, root):
        f = File('test.txt', 'data', USER_UID, root)
        with pytest.raises(FSPermissionError):
            f.set_owner(OTHER_UID, USER_UID)
        f.set_owner(OTHER_UID, ROOT_UID)
        assert f.owner_uid == OTHER_UID

    def test_set_permissions_owner_or_root_only(self, root):
        f = File('test.txt', 'data', USER_UID, root)
        # Non-owner, non-root -> fail
        with pytest.raises(FSPermissionError):
            f.set_permissions(
                Permissions(PermTriplet(True, True, True), PermTriplet(True, True, True)),
                OTHER_UID,
            )
        # Owner -> ok
        new_perms = Permissions(PermTriplet(True, False, False), PermTriplet(True, False, False))
        f.set_permissions(new_perms, USER_UID)
        assert f.permissions.user == PermTriplet(True, False, False)
        # Root -> ok
        f.set_permissions(
            Permissions(PermTriplet(False, False, False), PermTriplet(False, False, False)),
            ROOT_UID,
        )
        assert f.permissions.user == PermTriplet(False, False, False)

    def test_owner_change_flips_permission_lookup(self, root):
        """After chown, old owner should be treated as 'others'."""
        f = File('test.txt', 'data', USER_UID, root)
        f.set_permissions(
            Permissions(PermTriplet(True, True, True), PermTriplet(False, False, False)),
            USER_UID,
        )
        f.set_owner(OTHER_UID, ROOT_UID)
        assert f.has_permission(USER_UID, Action.READ) is False
        assert f.has_permission(OTHER_UID, Action.READ) is True

    def test_owner_can_lock_themselves_out_of_chmod(self, root):
        """If owner removes their own write, they can still chmod (set_permissions
        only checks uid match, not write perm). Verify this behavior."""
        f = File('test.txt', 'data', USER_UID, root)
        f.set_permissions(
            Permissions(PermTriplet(True, False, False), PermTriplet(False, False, False)),
            USER_UID,
        )
        # Owner can still set_permissions even without write
        f.set_permissions(
            Permissions(PermTriplet(True, True, True), PermTriplet(False, False, False)),
            USER_UID,
        )
        assert f.has_permission(USER_UID, Action.WRITE) is True


# ─── File ────────────────────────────────────────────────────────────────────


class TestFile:
    def test_name_with_extension(self, root):
        f = File('readme.txt', '', ROOT_UID, root)
        assert f.name == 'readme.txt'
        assert f.filename == 'readme'
        assert f.extension == 'txt'

    def test_name_without_extension(self, root):
        f = File('Makefile', '', ROOT_UID, root)
        assert f.name == 'Makefile'
        assert f.filename == 'Makefile'
        assert f.extension is None

    def test_name_with_multiple_dots(self, root):
        f = File('archive.tar.gz', '', ROOT_UID, root)
        assert f.filename == 'archive.tar'
        assert f.extension == 'gz'
        assert f.name == 'archive.tar.gz'

    def test_name_dotfile(self, root):
        f = File('.bashrc', '', ROOT_UID, root)
        assert f.filename == ''
        assert f.extension == 'bashrc'
        assert f.name == '.bashrc'

    def test_path_resolution(self, fs):
        home = fs['home']
        alice = home['alice']
        readme = alice['readme.txt']
        assert readme.path == '/home/alice/readme.txt'

    def test_set_name_changes_filename_and_extension(self, root):
        f = File('old.txt', '', ROOT_UID, root)
        f.set_name('new.md', ROOT_UID)
        assert f.filename == 'new'
        assert f.extension == 'md'
        assert f.name == 'new.md'

    def test_set_name_removes_extension(self, root):
        f = File('old.txt', '', ROOT_UID, root)
        f.set_name('noext', ROOT_UID)
        assert f.filename == 'noext'
        assert f.extension is None

    def test_binary_contents_accepted(self, root):
        data = b'\x89PNG\r\n\x1a\n'
        f = File('image.png', data, ROOT_UID, root)
        assert f.get_contents(ROOT_UID) == data

    def test_list_contents_rejected_on_create_and_set(self, root):
        with pytest.raises(FileError):
            File('bad.txt', [], ROOT_UID, root)
        f = File('ok.txt', 'ok', ROOT_UID, root)
        with pytest.raises(FileError):
            f.set_contents([], ROOT_UID)

    def test_switch_str_to_bytes_contents(self, root):
        f = File('test.txt', 'text', ROOT_UID, root)
        f.set_contents(b'binary', ROOT_UID)
        assert f.get_contents(ROOT_UID) == b'binary'

    def test_str_representation_is_path(self, root):
        f = File('test.txt', '', ROOT_UID, root)
        root.add(f, ROOT_UID)
        assert str(f) == '/test.txt'


# ─── Directory ───────────────────────────────────────────────────────────────


class TestDirectory:
    def test_path_resolution(self, fs):
        home = fs['home']
        assert home.path == '/home/'
        alice = home['alice']
        assert alice.path == '/home/alice/'

    def test_add_and_lookup(self, root):
        d = Directory('dir', [], ROOT_UID, root)
        root.add(d, ROOT_UID)
        assert root['dir'] is d

    def test_add_file_to_directory(self, root):
        d = Directory('dir', [], ROOT_UID, root)
        root.add(d, ROOT_UID)
        f = File('hello.txt', 'world', ROOT_UID, d)
        d.add(f, ROOT_UID)
        assert d['hello.txt'] is f

    def test_contains_by_name(self, root):
        d = Directory('dir', [], ROOT_UID, root)
        root.add(d, ROOT_UID)
        f = File('a.txt', '', ROOT_UID, d)
        d.add(f, ROOT_UID)
        assert 'a.txt' in d
        assert 'b.txt' not in d

    def test_contains_by_object(self, root):
        d = Directory('dir', [], ROOT_UID, root)
        root.add(d, ROOT_UID)
        f = File('a.txt', '', ROOT_UID, d)
        d.add(f, ROOT_UID)
        assert f in d

    def test_getitem_nonexistent_raises(self, root):
        d = Directory('dir', [], ROOT_UID, root)
        root.add(d, ROOT_UID)
        with pytest.raises(DirectoryError):
            d['nope']

    def test_duplicate_name_rejected(self, root):
        d = Directory('dir', [], ROOT_UID, root)
        root.add(d, ROOT_UID)
        f1 = File('same.txt', 'a', ROOT_UID, d)
        d.add(f1, ROOT_UID)
        f2 = File('same.txt', 'b', ROOT_UID, d)
        with pytest.raises(DirectoryError):
            d.add(f2, ROOT_UID)

    def test_delete_removes_child(self, root):
        d = Directory('dir', [], ROOT_UID, root)
        root.add(d, ROOT_UID)
        f = File('a.txt', '', ROOT_UID, d)
        d.add(f, ROOT_UID)
        d.delete(f, ROOT_UID)
        assert 'a.txt' not in d

    def test_add_requires_write_permission(self, root):
        d = Directory('dir', [], USER_UID, root)
        root.add(d, ROOT_UID)
        d.set_permissions(
            Permissions(PermTriplet(True, False, True), PermTriplet(False, False, False)),
            USER_UID,
        )
        f = File('x.txt', '', USER_UID, d)
        with pytest.raises(FSPermissionError):
            d.add(f, USER_UID)

    def test_delete_requires_write_permission(self, root):
        d = Directory('dir', [], USER_UID, root)
        root.add(d, ROOT_UID)
        f = File('x.txt', '', USER_UID, d)
        d.add(f, USER_UID)
        d.set_permissions(
            Permissions(PermTriplet(True, False, True), PermTriplet(False, False, False)),
            USER_UID,
        )
        with pytest.raises(FSPermissionError):
            d.delete(f, USER_UID)

    def test_nested_directories_path(self, root):
        a = Directory('a', [], ROOT_UID, root)
        root.add(a, ROOT_UID)
        b = Directory('b', [], ROOT_UID, a)
        a.add(b, ROOT_UID)
        c = Directory('c', [], ROOT_UID, b)
        b.add(c, ROOT_UID)
        assert c.path == '/a/b/c/'

    def test_get_contents_sorted(self, root):
        d = Directory('mixed', [], ROOT_UID, root)
        root.add(d, ROOT_UID)
        f = File('file.txt', '', ROOT_UID, d)
        d.add(f, ROOT_UID)
        sub = Directory('subdir', [], ROOT_UID, d)
        d.add(sub, ROOT_UID)
        sorted_contents = d.get_contents_sorted()
        # Directory class name < File class name alphabetically
        assert sorted_contents[0].__class__.__name__ == 'Directory'
        assert sorted_contents[1].__class__.__name__ == 'File'

    def test_contents_must_be_list(self, root):
        with pytest.raises(DirectoryError):
            Directory('bad', 'string_contents', ROOT_UID, root)

    def test_contents_elements_must_be_storage_units(self, root):
        with pytest.raises(DirectoryError):
            d = Directory('bad', [], ROOT_UID, root)
            d.add("not a storage unit", ROOT_UID)

    def test_non_owner_with_write_can_add(self, root):
        """Others have write by default, so non-owners should be able to add."""
        d = Directory('shared', [], USER_UID, root)
        root.add(d, ROOT_UID)
        f = File('contrib.txt', 'data', OTHER_UID, d)
        d.add(f, OTHER_UID)  # others have write=True by default
        assert 'contrib.txt' in d

    def test_multiple_children(self, root):
        d = Directory('multi', [], ROOT_UID, root)
        root.add(d, ROOT_UID)
        for i in range(10):
            f = File(f'file{i}.txt', f'content{i}', ROOT_UID, d)
            d.add(f, ROOT_UID)
        assert len(d.get_contents(ROOT_UID)) == 10
        for i in range(10):
            assert f'file{i}.txt' in d


# ─── RootDir ─────────────────────────────────────────────────────────────────


class TestRootDir:
    def test_rootdir_defaults(self):
        r = RootDir()
        assert r.path == '/'
        assert r.owner_uid == ROOT_UID
        assert r.name == ''
        assert r.get_contents(ROOT_UID) == []
        assert str(r) == '/'

    def test_set_name_on_rootdir_fails(self):
        r = RootDir()
        with pytest.raises(RootDirError):
            r.set_name('bad', ROOT_UID)

    def test_cannot_set_parent(self):
        r = RootDir()
        d = Directory('tmp', [], ROOT_UID, r)
        r.add(d, ROOT_UID)
        with pytest.raises(RootDirError):
            r.set_parent(d, ROOT_UID)


# ─── User ────────────────────────────────────────────────────────────────────


class TestUser:
    def test_with_password_roundtrip(self):
        u = User.with_password(100, 'alice', 'secret', display_name='Alice')
        assert u.uid == 100
        assert u.username == 'alice'
        assert u.display_name == 'Alice'
        assert u.hashed_password.startswith('$6$')
        assert User.verify_passwd('secret', u.hashed_password) is True
        assert User.verify_passwd('wrong', u.hashed_password) is False

    def test_salting_produces_unique_hashes(self):
        u1 = User.with_password(1, 'a', 'same')
        u2 = User.with_password(2, 'b', 'same')
        assert u1.hashed_password != u2.hashed_password

    def test_with_hashed_password_passthrough(self):
        hashed = '$6$salt$hash'
        u = User.with_hashed_password(100, 'bob', hashed)
        assert u.hashed_password == hashed

    def test_hash_format_parts(self):
        u = User.with_password(100, 'alice', 'test')
        parts = u.hashed_password.split('$')
        # format: $6$salt$hash -> ['', '6', salt, hash]
        assert len(parts) == 4
        assert parts[1] == '6'


# ─── Cross-Component / Integration ──────────────────────────────────────────


class TestIntegration:
    def test_full_hierarchy_traversal_and_permissions(self, fs):
        """Walk / -> home/ -> alice/ -> readme.txt, verify paths, owner read, other blocked."""
        readme = fs['home']['alice']['readme.txt']
        assert readme.path == '/home/alice/readme.txt'
        assert readme.get_contents(USER_UID) == 'hello world'
        # root reads regardless of ownership
        assert readme.get_contents(ROOT_UID) == 'hello world'
        # non-owner without read -> blocked
        with pytest.raises(FSPermissionError):
            readme.get_contents(OTHER_UID)

    def test_restrict_then_restore_permissions(self, root):
        """Owner locks themselves out, root restores access."""
        f = File('test.txt', 'data', USER_UID, root)
        root.add(f, ROOT_UID)
        f.set_permissions(
            Permissions(PermTriplet(False, False, False), PermTriplet(False, False, False)),
            USER_UID,
        )
        with pytest.raises(FSPermissionError):
            f.get_contents(USER_UID)
        f.set_permissions(
            Permissions(PermTriplet(True, True, True), PermTriplet(True, True, True)),
            ROOT_UID,
        )
        assert f.get_contents(USER_UID) == 'data'

    def test_ownership_transfer_flips_access(self, root):
        """chown from USER to OTHER: old owner loses access, new owner gains it."""
        f = File('secret.txt', 'classified', USER_UID, root)
        root.add(f, ROOT_UID)
        f.set_permissions(
            Permissions(PermTriplet(True, True, True), PermTriplet(False, False, False)),
            USER_UID,
        )
        assert f.get_contents(USER_UID) == 'classified'
        f.set_owner(OTHER_UID, ROOT_UID)
        assert f.get_contents(OTHER_UID) == 'classified'
        with pytest.raises(FSPermissionError):
            f.get_contents(USER_UID)

    def test_mixed_ownership_tree(self, root):
        """Root-owned /etc/passwd unreadable by alice; alice-owned file readable by alice."""
        etc = Directory('etc', [], ROOT_UID, root)
        root.add(etc, ROOT_UID)
        passwd = File('passwd', 'root:x:0:0', ROOT_UID, etc)
        etc.add(passwd, ROOT_UID)

        home = Directory('home', [], ROOT_UID, root)
        root.add(home, ROOT_UID)
        alice_dir = Directory('alice', [], USER_UID, home)
        home.add(alice_dir, ROOT_UID)
        notes = File('notes.txt', 'my notes', USER_UID, alice_dir)
        alice_dir.add(notes, USER_UID)

        assert notes.get_contents(USER_UID) == 'my notes'
        with pytest.raises(FSPermissionError):
            passwd.get_contents(USER_UID)  # others have no read

    def test_deep_nesting_path_resolution(self, root):
        current = root
        for name in ['a', 'b', 'c', 'd', 'e']:
            d = Directory(name, [], ROOT_UID, current)
            current.add(d, ROOT_UID)
            current = d
        f = File('deep.txt', 'found me', ROOT_UID, current)
        current.add(f, ROOT_UID)
        assert f.path == '/a/b/c/d/e/deep.txt'

    def test_file_rename_updates_path_and_extension(self, fs):
        readme = fs['home']['alice']['readme.txt']
        readme.set_name('notes.md', USER_UID)
        assert readme.path == '/home/alice/notes.md'
        assert readme.filename == 'notes'
        assert readme.extension == 'md'

    def test_set_parent_checks_write_on_target_directory(self, root):
        """set_parent needs write on both the SU and the new parent."""
        d1 = Directory('d1', [], USER_UID, root)
        root.add(d1, ROOT_UID)
        d2 = Directory('d2', [], USER_UID, root)
        root.add(d2, ROOT_UID)
        f = File('f.txt', '', USER_UID, d1)
        d1.add(f, USER_UID)

        d2.set_permissions(
            Permissions(PermTriplet(True, False, True), PermTriplet(False, False, False)),
            USER_UID,
        )
        with pytest.raises(FSPermissionError):
            f.set_parent(d2, USER_UID)

    def test_add_delete_add_cycle(self, root):
        """Add 3 files, delete the middle one, verify state."""
        d = Directory('workspace', [], ROOT_UID, root)
        root.add(d, ROOT_UID)
        files = [File(f'{c}.txt', c, ROOT_UID, d) for c in 'abc']
        for f in files:
            d.add(f, ROOT_UID)
        d.delete(files[1], ROOT_UID)
        assert len(d.get_contents(ROOT_UID)) == 2
        assert 'b.txt' not in d
        assert 'a.txt' in d and 'c.txt' in d

    def test_delete_then_readd_same_name(self, root):
        """After deleting a file, adding a new one with the same name should work."""
        d = Directory('dir', [], ROOT_UID, root)
        root.add(d, ROOT_UID)
        f1 = File('x.txt', 'v1', ROOT_UID, d)
        d.add(f1, ROOT_UID)
        d.delete(f1, ROOT_UID)
        f2 = File('x.txt', 'v2', ROOT_UID, d)
        d.add(f2, ROOT_UID)
        assert d['x.txt'] is f2
        assert f2.get_contents(ROOT_UID) == 'v2'

    def test_root_writes_to_fully_locked_file(self, root):
        """Root bypasses even 000 permissions on all operations."""
        f = File('locked.txt', 'original', USER_UID, root)
        root.add(f, ROOT_UID)
        f.set_permissions(
            Permissions(PermTriplet(False, False, False), PermTriplet(False, False, False)),
            USER_UID,
        )
        # Root can still read, write, and rename
        assert f.get_contents(ROOT_UID) == 'original'
        f.set_contents('changed', ROOT_UID)
        assert f.get_contents(ROOT_UID) == 'changed'
        f.set_name('unlocked.txt', ROOT_UID)
        assert f.name == 'unlocked.txt'
