class FunctionGroup(object):
    def __init__(self, parent, prefix):
        self._parent = parent
        self._prefix = prefix

    def __getattr__(self, name):
        return getattr(self._parent, f"{self._prefix}_{name}")