from __future__ import annotations
from typing import TYPE_CHECKING
from enum import Enum
from abc import ABC, abstractmethod
from bidict import bidict
from typing import Tuple, Optional, List
from dataclasses import dataclass

if TYPE_CHECKING:
    from typing import TypeAlias, Tuple, Optional, List, Dict
    from node import ComputerNetworkAdapter

import random

Node: TypeAlias = 'Router | ComputerNetworkAdapter'

IPv4Addr: TypeAlias = Tuple[int, int, int, int]
Port: TypeAlias = int
Bidict: TypeAlias = bidict
Domain: TypeAlias = str


@dataclass(eq=True, frozen=True)
class CIDR(object):
    domain: IPv4Addr
    fixed: int


@dataclass(eq=True, frozen=True)
class SocketAddr(object):
    addr: IPv4Addr
    port: Port


def is_ip_in_domain(ip: IPv4Addr, domain: CIDR):
    fixed = domain.fixed
    if fixed >= 8 and ip[0] != domain.domain[0]:
        return False
    if fixed >= 16 and ip[1] != domain.domain[1]:
        return False
    if fixed >= 24 and ip[2] != domain.domain[2]:
        return False
    if fixed >= 32 and ip[3] != domain.domain[3]:
        return False

    return True


class RouterPacketProcessor(object):

    class Protocol(Enum):
        ICMP = "ICMP"
        HTTP = "HTTP"
        MAGIC = "MAGIC"
        DNS = "DNS"

    @classmethod
    def process_packet(cls, router: Router, packet: Packet) -> Packet:
        Prot = RouterPacketProcessor.Protocol
        decoded_message = ""
        try:
            decoded_message = packet.message.decode("utf-8")
        except UnicodeDecodeError:
            return Packet(SocketAddr(router.ip_address, router.get_unassigned_port()), 
                          packet.source,
                          b"MAGICCannot process", 
                          True)

        return_message = None
        if decoded_message.startswith(Prot.MAGIC.value):
            raw_message = decoded_message.removeprefix(Prot.MAGIC.value)
            return_message = str.encode(f"{Prot.MAGIC.value}Cannot process")

        
        elif decoded_message.startswith(Prot.ICMP.value):
            raw_message = decoded_message.removeprefix(Prot.ICMP.value)
            if raw_message == "Ping":
                return_message = str.encode(f"{Prot.ICMP.value}Pong")

        elif decoded_message.startswith(Prot.HTTP.value):
            raw_message = decoded_message.removeprefix(Prot.HTTP.value)
            if raw_message.upper() == "GET":
                raise NotImplementedError("HTTP not implemented")
        
        elif decoded_message.startswith(Prot.DNS.value):
            raw_message = decoded_message.removeprefix(Prot.DNS.value)
            raw_message = raw_message.strip().strip(' ').strip('/')
            if raw_message.count('.') > 1 and raw_message.startswith('www.'):
                raw_message = raw_message.strip('www.')
            if raw_message in router.dns_record:
                address = '.'.join(map(str, router.dns_record[raw_message]))
                return_message = str.encode(f"{Prot.DNS.value}{address}")
            else:
                return_message = str.encode(f"{Prot.MAGIC.value}DNS not found")

        return_message = return_message or b"MAGICCannot process"
            
        return Packet(SocketAddr(router.ip_address, router.get_unassigned_port()), 
                      packet.source, 
                      return_message, 
                      True)
        

class Router(ABC):
    LOOPBACK: CIDR = CIDR((127,0,0,0), 8)
    def __init__(self, parent: Optional[Router], children: List[Node] = None, enabled: bool = True) -> None:
        self.dns_record: Dict[Domain, IPv4Addr] = dict()
        self.parent: Router | None = parent
        self.children = children or []
        self.enabled: bool = enabled
        self.ip_address: Optional[IPv4Addr] = self.assign_ip() if self.enabled else None

        if self.parent:
            self.parent.children.append(self)

        for child in self.children:
            child.parent = self
            child.disable()
            child.enable()

    def get_unassigned_port(self):
        while True:
            num = random.randint(0, 65535)
            if num not in [80]:
                break
        return num

    @abstractmethod
    def assign_ip(self) -> IPv4Addr:
        pass

    @abstractmethod
    def domain_range(self) -> Optional[CIDR]:
        pass

    def enable(self) -> None:
        if self.enabled: return
        self.enabled = True
        self.ip_address = self.assign_ip()
        for child in self.children:
            child.enable()

    def disable(self) -> None:
        if not self.enabled: return
        self.enabled = False
        self.ip_address = None
        for child in self.children:
            child.disable()

    @abstractmethod
    def send_packet(self, packet: Packet):
        pass

    def process_packet(self, packet: Packet) -> Packet:
        return RouterPacketProcessor.process_packet(self, packet)
    
    def map_domain(self, domain: Domain, address: IPv4Addr):
        self.dns_record[domain] = address

    def del_domain(self, domain: Domain):
        if domain not in self.dns_record: return
        del self.dns_record[domain]

    def flood_dns(self):
        for child in self.children:
            if isinstance(child, Router):
                child.dns_record = self.dns_record | child.dns_record
                child.flood_dns()


class Packet(object):
    def __init__(self, source: SocketAddr, dest: SocketAddr, message: bytes, response: bool):
        self.source: SocketAddr = source
        self.dest: SocketAddr = dest
        self.message: bytes = message
        self.response: bool = response