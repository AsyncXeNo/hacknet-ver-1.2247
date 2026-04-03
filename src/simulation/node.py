from __future__ import annotations
import time
from itertools import chain
from simulation.network.adapter import ComputerNetworkAdapter
from simulation.application import Application
import random
from enum import Enum
from copy import deepcopy
from better_exceptions import LoggingException
from loguru_config import get_subsystem_logger
from simulation.network.base import Port, Packet, SocketAddr
from simulation.network.adapter import Binding
from game_timer import game_timer
from abc import ABC
from typing import TypeAlias
from threading import Thread
from collections import defaultdict
from utils import FunctionGroup


class OSException(LoggingException):
    def __init__(self, message, *args):
        super().__init__(logger=get_subsystem_logger('os'), message=message, *args)

class PortInUseException(OSException):
    def __init__(self, message, *args):
        super().__init__(message=message, *args)

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


class OperatingSystem(ABC):
    def __init__(self, apps: list[Application] | None = None) -> None:
        self.owner: Computer | None = None
        apps = apps or []
        for app in apps:
            self.install(app)
            
        self.port_mapping: dict[Application, list[Port]] = defaultdict(list)
        self.temp_port_blocks: dict[Application, list[Port]] = defaultdict(list)

        self.buffer: dict[Application, list[Packet]] = defaultdict(list)
        
        self.syscall = FunctionGroup(self, 'syscall')

    @property
    def ports_in_use(self) -> list[Port]:
        return sum(self.port_mapping.values(), []) + sum(self.temp_port_blocks.values(), [])

    def get_unassigned_port(self, app: Application | None = None):
        while True:
            num = random.randint(0, 65535)
            if num not in self.ports_in_use:
                break
        if app:
            self.temp_port_blocks[app].append(num)
        return num

    def free_temp_port_block(self, app: Application, port: Port):
        assert port in self.temp_port_blocks[app]
        self.temp_port_blocks[app].remove(port)

    def own(self, computer: Computer):
        self.owner = computer

    # syscall.bind
    def syscall_bind(self, app: Application, port: Port, service_fn: callable[[Packet], bytes | None]):
        assert self.owner, 'OS has no computer owner.'
        net_adap: NetworkAdapterAccess = self.owner.get_resource(HardwareResource.NETWORK_ADAPTER)

        if port in self.ports_in_use: raise PortInUseException(f"Port {port} is in use")
        self.port_mapping[app].append(port)

        net_adap.bind(port, service_fn)

    # syscall.unbind
    def syscall_unbind(self, app: Application, port: Port | None=None):
        assert self.owner, 'OS has no computer owner.'
        net_adap: NetworkAdapterAccess = self.owner.get_resource(HardwareResource.NETWORK_ADAPTER)
        
        ports = self.port_mapping[app]

        if len(ports) == 0:
            raise OSException(f'No ports mapped for application {app.name}')
        elif len(ports) == 1 and (port is None or port == ports[0]):
            del self.port_mapping[app]
            net_adap.unbind(ports[0])
        elif port is not None and port in ports:
            self.port_mapping[app].remove(port)
            net_adap.unbind(port)
        elif port is not None and port not in ports:
            raise OSException(f'Port {port} is not mapped, but attempted to unbind it.')
        elif port is None and len(ports) > 1:
            raise OSException(f'Multiple ports mapped for application {app.name}, but no specific port provided to unbind.')
    
    def create_packet(self, app: Application, dest: SocketAddr, message: bytes) -> Packet:
        assert self.owner, 'OS has no computer owner.'
        net_adap: NetworkAdapterAccess = self.owner.get_resource(HardwareResource.NETWORK_ADAPTER)
        port = self.get_unassigned_port()
        return Packet(source=SocketAddr(addr=net_adap.ip_address, port=port), dest=dest, message=message, response=False)

    # syscall.request_blocking
    def syscall_request_blocking(self, app: Application, packet: Packet, timeout_secs: int) -> Packet | None:
        assert self.owner, 'OS has no computer owner.'
        net_adap: NetworkAdapterAccess = self.owner.get_resource(HardwareResource.NETWORK_ADAPTER)
        return net_adap.request(packet=packet, timeout_secs=timeout_secs)

    # syscall.request_async
    def syscall_request_async(self, app: Application, packet: Packet, timeout_secs: int):
        assert self.owner, 'OS has no computer owner.'
        
        def wrapper_with_callback(app: Application, packet: Packet, timeout_secs: int):
            response_packet = self.syscall.request_blocking(app, packet, timeout_secs)
            if response_packet:
                self.buffer[app].append(response_packet)

        Thread(target=wrapper_with_callback, kwargs={"app": app, "packet": packet, "timeout_secs": timeout_secs}).start()

    # syscall.poll
    def syscall_poll(self, app: Application) -> list[Packet] | None:
        assert self.owner, 'OS has no computer owner'
        if app in self.buffer:
            packets = self.buffer.pop(app)
            return packets
        return None

    def install(self, app: Application):
        pass


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