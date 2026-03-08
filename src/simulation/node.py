from __future__ import annotations
from typing import TYPE_CHECKING

from simulation.network.base import IPv4Addr, Packet

if TYPE_CHECKING:
    from simulation.network.consumer_routers import ConsumerRouter


class OperatingSystem(object):
    def __init__(self) -> None:
        pass


class Computer(object): 
    def __init__(self, os: OperatingSystem, network_id, mac_id, apps) -> None:
        self.os: OperatingSystem = os
        self.network_id = network_id
        self.apps = apps
        self.mac_id = mac_id
        pass

class ComputerNetworkAdapter(object):

    def __init__(self, parent: ConsumerRouter, enabled: bool = True) -> None:
        self.enabled: bool = enabled
        self.parent: ConsumerRouter = parent
        self.ip_address: IPv4Addr | None = self.parent.hand_ip() if self.enabled else None

    def enable(self) -> None:
        pass

    def disable(self) -> None:
        pass

    def send_packet(self, packet: Packet) -> None:
        raise NotImplemented("Not implemented")