from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from simulation.node.hardware import Computer, NetworkAdapterAccess
from simulation.node.hardware import HardwareResource
from simulation.node.application import Application
import random
from better_exceptions import LoggingException
from loguru_config import get_subsystem_logger
from simulation.network.base import Port, Packet, SocketAddr
from abc import ABC
from threading import Thread
from collections import defaultdict
from utils import FunctionGroup


class OSException(LoggingException):
    def __init__(self, message, *args):
        super().__init__(logger=get_subsystem_logger('os'), message=message, *args)

class PortInUseException(OSException):
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