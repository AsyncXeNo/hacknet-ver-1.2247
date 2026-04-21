from __future__ import annotations
import time
from simulation.network.adapter import ComputerNetworkAdapter
from simulation.node.application import Application
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from simulation.node.op_sys import OperatingSystem
from enum import Enum
from copy import deepcopy
from better_exceptions import LoggingException
from loguru_config import get_subsystem_logger
from simulation.network.base import Port, Packet
from game.timer import game_timer
from typing import TypeAlias
from threading import Thread


class ComputerException(LoggingException):
    def __init__(self, message, *args):
        super().__init__(logger=get_subsystem_logger('computer'), message=message, *args)

class ComputerSwitchedOff(ComputerException):
    def __init__(self, message, *args):
        super().__init__(message=message, *args)

class NotEnoughRAMException(ComputerException):
    def __init__(self, message, *args):
        super().__init__(message=message, *args)

class UnboundException(ComputerException):
    def __init__(self, message, *args):
        super().__init__(message=message, *args)


class HardwareResource(Enum):
    NETWORK_ADAPTER=0
    RAM=1


HardwareAccess: TypeAlias = 'RamAccess | Peripheral | ComputerNetworkAdapter'

class Computer(object): 
    def __init__(self, os: OperatingSystem, total_ram: int, peripherals: list[Peripheral] | None = None,) -> None:
        self.os: OperatingSystem = os
        self.ram: RamAccess = RamAccess(self, total_ram, 0)
        self.peripherals: list[Peripheral] = peripherals or []
        self.network_adapter_access: NetworkAdapterAccess = NetworkAdapterAccess(ComputerNetworkAdapter())

        self.on: bool = False

        self.os.own(self)

    @property
    def network_adaptor_base(self):
        return self.network_adapter_access.net_adap

    def switch_on(self) -> None:
        self.on = True

    def switch_off(self) -> None:
        self.on = False

    def get_resource(self, res: HardwareResource) -> HardwareAccess:
        if not self.on: raise ComputerSwitchedOff('Cannot get resource when computer is switched off.')
        match(res):
            case HardwareResource.NETWORK_ADAPTER:
                return self.network_adapter_access
            case HardwareResource.RAM:
                return self.ram


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

    def __init__(self, net_adap: ComputerNetworkAdapter):
        self.net_adap = net_adap
        self.bindings: dict[Port, callable[[Packet], bytes | None]] = dict()

    @property
    def ip_address(self):
        return self.net_adap.ip_address

    def bind(self, port: Port, service_fn: callable[[Packet], bytes | None]):
        self.bindings[port] = service_fn
        self.net_adap.listeners[port] = service_fn

    def unbind(self, port: Port):
        if self.bindings.get(port) is not None:
            del self.bindings[port]
            del self.net_adap.listeners[port]
        else:
            raise UnboundException(f'Port {port} is not bound but attempted to unbind')

    def request(self, packet: Packet, timeout_secs: int):
        Thread(target=self.send_request_thread, args=(deepcopy(packet),)).start()
        return self.check_buffer(packet, timeout_secs)

    def check_buffer(self, sent_packet: Packet, timeout_secs: int):
        start = game_timer.get_time()
        
        def is_right_packet(packet: Packet):
            return packet.dest == sent_packet.source
                
        while True:
            if game_timer.get_time() - start > timeout_secs:
                break
            if (packet:=next(filter(is_right_packet, self.net_adap.buffer), None)) is not None:
                self.net_adap.buffer.remove(packet)
                return packet
            time.sleep(0.1)

        return None

    def send_request_thread(self, packet: Packet):
        self.net_adap.send_packet(packet)
        

class Peripheral(object):
    pass