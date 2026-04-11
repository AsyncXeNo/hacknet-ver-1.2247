from dataclasses import dataclass
import random
import hashlib
import base64
import secrets

@dataclass(eq=True, frozen=True)
class User:
    uid: int
    username: str
    display_name: str | None
    hashed_password: str

    @classmethod
    def with_password(
        cls,
        uid: int,
        username: str,
        password: str,
        display_name: str | None = None,
    ):
        return cls(
            uid,
            username,
            display_name,
            cls.hash_passwd(password),
        )

    @classmethod
    def with_hashed_password(
        cls,
        uid: int,
        username: str,
        hashed_password: str,
        display_name: str | None = None,
    ):
        return cls(
            uid,
            username,
            display_name,
            hashed_password,
        )

    @staticmethod
    def hash_passwd(password: str) -> str:
        salt = base64.b64encode(
            secrets.token_bytes(16),
            altchars=b'./'
        ).decode()

        hashed = base64.b64encode(
            hashlib.sha512((password + salt).encode()).digest(),
            altchars=b'./'
        ).decode()

        return f"$6${salt}${hashed}"

    @property
    def passwd_line(self):
        return ':'.join([self.username, 'x', str(self.uid), str(self.uid), self.display_name, '/root' if self.uid == 0 else '/home/' + self.username, '/bin/bash'])
    
    @property
    def shadow_line(self):
        return f"{self.username}:{self.hashed_password}:::::::"

    @staticmethod
    def verify_passwd(password: str, hashed: str) -> bool:
        _, _, salt, stored = hashed.split("$")

        new = base64.b64encode(
            hashlib.sha512((password + salt).encode()).digest(),
            altchars=b'./'
        ).decode()

        return secrets.compare_digest(stored, new)