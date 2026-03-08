
class GameTimer(object):
    def __init__(self):
        self.time: float = 0

    def delta_time(self, dt: float):
        self.time += dt

    def update_time(self, time: float):
        self.time = time

    def get_time(self) -> float:
        return self.time

    @classmethod
    def calc_deltatime(cls, seconds: int=0, minutes: int=0, hours: int=0) -> float:
        return seconds + minutes * 60 + hours * 3600


game_timer: GameTimer = GameTimer()