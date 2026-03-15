from __future__ import annotations
from typing import TYPE_CHECKING

from simulation.network.adapter import ComputerNetworkAdapter
from simulation.network.base import IPv4Addr, Packet, Port
from application import Application
from dataclasses import dataclass

if TYPE_CHECKING:
    from simulation.network.consumer_routers import ConsumerRouter


class OperatingSystem(object):
    def __init__(self) -> None:
        pass

    def install(self, app: Application):
        pass


class Computer(object): 
    def __init__(self, os: OperatingSystem, network_adapter: ComputerNetworkAdapter, apps: list[Application] | None = None, peripherals: list[Peripheral] | None = None) -> None:
        self.os: OperatingSystem = os
        apps = apps or []
        for app in apps:
            self.os.install(app)
        self.peripherals = peripherals or []
        self.network_adapter = network_adapter
        pass