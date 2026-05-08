from dataclasses import dataclass


@dataclass(frozen=False)
class Translation():
    x: float
    y: float

    @property
    def is_zero(self):
        return self.x == 0 and self.y == 0


@dataclass(frozen=False)
class Transform():
    translation: Translation
    rotation: float
    scale: float