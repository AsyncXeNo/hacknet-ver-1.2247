
class OperatingSystem(object):
    def __init__(self) -> None:
        pass


class Computer(object): 
    def __init__(self, os: OperatingSystem, network_id, mac_id, apps) -> None:
        self.os = os
        self.network_id = network_id
        self.apps = apps
        self.mac_id = mac_id
        pass