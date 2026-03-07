from __future__ import annotations
from typing import TYPE_CHECKING, TypeAlias
from .base import Router, Packet, is_ip_in_domain
from simulation.network.fixed_routers import ISPRouter
from simulation.network.base import CIDR, SocketAddr
from bidict import bidict
from itertools import chain
from loguru import logger

if TYPE_CHECKING:
    from network.fixed_routers import ISPRouter
    from network.base import Bidict, Port
    from typing import List, Dict, Optional
    from node import ComputerNetworkAdapter

import random


class ConsumerRouter(Router):
    FORBIDDEN_RANGE: CIDR
    PRIVATE_RANGE: CIDR

    def assign_ip(self):
        return self.parent.hand_ip()

    def wrong_range_packet(self, packet: Packet):
        incorrect_packet = Packet(SocketAddr(self.ip_address, self.get_unassigned_port()),
                                    packet.source,
                                    b'MAGICWrong Configuration: Business Router',
                                    True)
        self.send_packet(incorrect_packet)


    def internal_response_packet(self, packet: Packet):
        socket_addr = packet.dest
        if packet.dest.addr == self.ip_address:
            socket_addr = self.remove_from_NAT(packet.dest.port)
            logger.debug(f"Got {socket_addr} from NAT")
            if not socket_addr:
                self.send_packet(self.process_packet(packet))
                return
        correct_child = None
        for child in self.children:
            if child.ip_address == socket_addr.addr:
                correct_child = child
                break
        else:
            return
        if correct_child:
            packet.dest = socket_addr
            correct_child.send_packet(packet)

    def internal_request_packet(self, packet: Packet):
        socket_addr = packet.dest
        if packet.dest.addr == self.ip_address:
            socket_addr = self.port_forwarding.get(packet.dest.port)
            if not socket_addr:
                self.send_packet(self.process_packet(packet))
                return

        correct_child =  None
        for child in self.children:
            if child.ip_address == socket_addr.addr:
                correct_child = child
                break
        else: 
            not_found_packet = Packet(SocketAddr(self.ip_address, self.get_unassigned_port()), 
                                        packet.source,
                                        b'MAGICDestination not found',
                                        True)
            self.send_packet(not_found_packet)
            return
        if correct_child:
            packet.dest = socket_addr
            correct_child.send_packet(packet)

    def external_request_packet(self, packet: Packet):
        port = self.add_to_NAT(packet.source)
        packet.source = SocketAddr(self.ip_address, port)
        self.parent.send_packet(packet)

    def external_response_packet(self, packet: Packet):
        port = self.port_forwarding.inv.get(packet.dest)
        packet.source = SocketAddr(self.ip_address, port)
        self.parent.send_packet(packet)


    def send_packet(self, packet):
        is_loopback = is_ip_in_domain(packet.dest.addr, self.LOOPBACK)
        assert not is_loopback, "How the fuck"

        if is_ip_in_domain(packet.dest.addr, self.FORBIDDEN_RANGE):
            self.wrong_range_packet(packet)
            return

        is_public_ip = packet.dest.addr == self.ip_address
        is_private_domain = is_ip_in_domain(packet.dest.addr, self.PRIVATE_RANGE)

        # To internal
        if is_public_ip or is_private_domain:
            if packet.dest.addr == self.PRIVATE_IP:
                self.send_packet(self.process_packet(packet))
            elif not packet.response:
                self.internal_request_packet(packet)
            elif packet.response:
                self.internal_response_packet(packet)

        # To external
        else:
            if not packet.response:
                self.external_request_packet(packet)
            if packet.response:
                self.external_response_packet(packet)


    def domain_range(self) -> Optional[CIDR]:
        return self.PRIVATE_RANGE if self.enabled else None

    def get_unassigned_port(self):
        while True:
            num = random.randint(0, 65535)
            if num not in chain(self.nat_table.keys(), self.port_forwarding.keys(), [80]):
                break
        return num

    def add_to_NAT(self, socket_addr: SocketAddr) -> Port:
        port = self.get_unassigned_port()
        logger.info(f"Added port {port} to NAT for address {socket_addr}")
        self.nat_table[port] = socket_addr
        return port

    def forward(self, port: Port, socket_addr: SocketAddr) -> None:
        self.port_forwarding[port] = socket_addr

    def stop_forwarding(self, port: Port) -> None:
        del self.port_forwarding[port]

    def remove_from_NAT(self, port: Port) -> SocketAddr:
        if port not in self.nat_table: return
        
        logger.info(f"Removing port {port} to NAT for address {self.nat_table[port]}")
        
        socket_addr = self.nat_table[port]
        del self.nat_table[port]
        return socket_addr


class BusinessRouter(ConsumerRouter):
    PRIVATE_IP = (10, 0, 0, 1)
    FORBIDDEN_RANGE = CIDR((192,168,0,0), 16)
    PRIVATE_RANGE = CIDR((10,0,0,0), 8)

    def __init__(self, parent: ISPRouter, children : List[ComputerNetworkAdapter | HomeRouter] = None, enabled: bool = True):
        assert parent or not enabled, "Consumers routers cannot be enabled without connection to an ISP"
        self.nat_table: Dict[Port, SocketAddr] = dict()
        self.port_forwarding: Bidict[Port, SocketAddr] = bidict()
        children = children or []
        super().__init__(parent, children, enabled)

    def hand_ip(self):
        assert self.enabled, "Inactive ISP assigning address"
        assert len(self.children) < 2**20, "Too many nodes"
        while True:
            current_ip = (10, random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            if current_ip == (10,0,0,1): continue
            for child in self.children:
                if child.ip_address and child.ip_address == current_ip:
                    break
            else:
                return current_ip



class HomeRouter(ConsumerRouter):
    PRIVATE_IP = (192, 168, 1, 1)
    FORBIDDEN_RANGE = CIDR((10,0,0,0), 8)
    PRIVATE_RANGE = CIDR((192,168,0,0), 16)

    def __init__(self, parent: ISPRouter | BusinessRouter, children : List[ComputerNetworkAdapter] = None, enabled: bool = True):
        assert parent or not enabled, "Consumers routers cannot be enabled without connection to an ISP"
        self.nat_table: Dict[Port, SocketAddr] = dict()
        self.port_forwarding: Bidict[Port, SocketAddr] = bidict()
        children = children or []
        super().__init__(parent, children, enabled)


    def hand_ip(self):
        assert self.enabled, "Inactive ISP assigning address"
        assert len(self.children) < 2**15, "Too many nodes"
        while True:
            current_ip = (192, 168, random.randint(0, 255), random.randint(0, 255))
            if current_ip == (192,168,1,1): continue
            for child in self.children:
                if child.ip_address and child.ip_address == current_ip:
                    break
            else:
                return current_ip
