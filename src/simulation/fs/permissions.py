from dataclasses import dataclass


@dataclass(eq=True, frozen=True)
class PermTriplet(object):
    write: bool
    read: bool
    execute: bool


class Permission(object):
    def __init__(self, user: PermTriplet, others: PermTriplet):
        self.user: PermTriplet = user
        self.others: PermTriplet = others