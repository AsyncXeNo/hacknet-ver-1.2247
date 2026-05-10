from game.states.base import State


class VirtualState(State):
    def __init__(self):
        raise NotImplementedError('No virtual states')