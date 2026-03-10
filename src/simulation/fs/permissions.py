from dataclasses import dataclass
from typing import NamedTuple


class PermTriplet(NamedTuple):
    read: bool
    write: bool
    execute: bool


class Permissions(object):
    def __init__(self, user: PermTriplet, others: PermTriplet):
        self.user: PermTriplet = user
        self.others: PermTriplet = others

    def __getitem__(self, key):
        if key:
            return self.others
        else:
            return self.user

