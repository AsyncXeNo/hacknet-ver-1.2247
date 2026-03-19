from __future__ import annotations
from simulation.network.adapter import ComputerNetworkAdapter
from application import Application
from enum import Enum
from better_exceptions import LoggingException
from loguru_config import get_subsystem_logger
from simulation.network.base import Port, Packet, SocketAddr
from simulation.network.adapter import Binding
from abc import ABC
from typing import TypeAlias


class ComputerException(LoggingException):
    def __init__(self, message, *args):
        super().__init__(logger=get_subsystem_logger('computer'), message=message, *args)


class NotEnoughRAMException(ComputerException):
    def __init__(self, message, *args):
        super().__init__(message=message, *args)

class UnboundException(ComputerException):
    def __init__(self, message, *args):
        super().__init__(message=message, *args)


class OperatingSystem(ABC):
    def __init__(self, apps: list[Application] | None = None) -> None:
        apps = apps or []
        for app in apps:
            self.install(app)

    def install(self, app: Application):
        pass


class HardwareResource(Enum):
    NETWORK_ADAPTER=0
    RAM=1


HardwareAccess: TypeAlias = 'RamAccess | Peripheral | ComputerNetworkAdapter'

class Computer(object): 
    def __init__(self, os: OperatingSystem, total_ram: int, network_adapter: ComputerNetworkAdapter, peripherals: list[Peripheral] | None = None,) -> None:
        self.os: OperatingSystem = os
        self.ram: RamAccess = RamAccess(self, total_ram, 0)
        self.peripherals: list[Peripheral] = peripherals or []
        self.network_adapter = network_adapter

    def get_resource(self, res: HardwareResource) -> HardwareAccess:
        match(res):
            case HardwareResource.NETWORK_ADAPTER:
                return self.network_adapter
            case HardwareResource.RAM:
                return self.ram_access


class RamAccess(object):
    
    def __init__(self, owner: Computer, total_ram: int, current_ram: int):
        self.owner = owner
        self.total_ram = total_ram
        self.current_ram = current_ram
        self.usage: dict[Application, int]

    def assign_ram(self, app: Application, ram: int):
        if ram + self.current_ram > self.total_ram:
            raise NotEnoughRAMException()
        self.usage[app] = ram
        self.current_ram += ram

    def free_ram(self, app: Application):
        ram = self.usage[app]
        del self.usage[app]
        self.current_ram -= ram


class NetworkAdapterAccess(object):

    def __init__(self, owner: Computer, net_adap: ComputerNetworkAdapter):
        self.net_adap = net_adap
        self.app_bindings: dict[Application, Binding] = []

    def bind(self, app: Application, port: Port, service_fn: callable[[Packet], bytes | None]):
        binding = Binding(port, service_fn)
        self.app_bindings[app] = binding
        self.net_adap.listeners.append(binding)

    def unbind(self, app: Application):
        try:
            binding = self.app_bindings.pop(app)
            self.net_adap.listeners.remove(binding)
        except (ValueError, KeyError):
            raise UnboundException(f'Application {app} is not bound but unbound anway')

    def request(self, addr: SocketAddr, timeout_ms: int):
        #TODO: Multithreading, spawn a thread to handle request routing
        pass
        

class Peripheral(object):
    pass