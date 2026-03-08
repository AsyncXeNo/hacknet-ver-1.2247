from dataclasses import dataclass

class User(object):
    
    def __init__(self, username: str, display_name: str | None = None, password: str | None = None):
        self.username: str = username
        self.display_name: str | None = display_name
        self.password: str | None = password