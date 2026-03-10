from dataclasses import dataclass
import random
import hashlib
import base64


@dataclass(eq=True, frozen=True, init=False)
class User(object):
    uid: int
    username: str
    display_name: str | None
    hashed_password: str | None

    def __init__(self, uid: int, username: str, display_name: str | None=None, *, password: str| None = None, hashed_password: str | None = None):
        assert not (password and hashed_password)
        self.uid = uid
        self.username = username
        self.display_name = display_name
        self.hashed_password = self.hash_passwd(password) if password else hashed_password

    @classmethod
    def hash_passwd(cls, password: str) -> str:
        salt = base64.b64encode(random.randint(1, 64**3), altchars='./').decode('utf-8')
        hashed = base64.b64encode(hashlib.sha512(( password + salt ).encode("utf-8")).digest(), altchars='./').decode('utf-8')
        return f"$6${salt}${hashed}"

    @classmethod
    def verify_passwd(cls, password: str, hashed: str) -> bool:
        salt = hashed.split('$')[2]
        new_hashed = base64.b64encode(hashlib.sha512((password + salt).encode("utf-8")).digest(), altchars='./').decode('utf-8')
        return hashed.split('$')[3] == new_hashed