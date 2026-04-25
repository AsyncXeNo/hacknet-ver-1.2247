
class GameTimer(object):
    def __init__(self):
        # In seconds
        self._time: float = 0

    def delta_time(self, dt_ms: float):
        self._time += dt_ms / 1000

    def update_time(self, time: float):
        self._time = time

    def get_time(self) -> float:
        return self._time
    
    @property
    def time(self) -> float:
        return self._time
    
    @property
    def time_ms(self) -> float:
        return self._time * 1000

    @classmethod
    def calc_deltatime(cls, seconds: int=0, minutes: int=0, hours: int=0) -> float:
        return seconds + minutes * 60 + hours * 3600


game_timer: GameTimer = GameTimer()