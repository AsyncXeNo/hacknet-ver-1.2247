from __future__ import annotations
from typing import TYPE_CHECKING
from .base import Router, is_ip_in_domain, SocketAddr, CIDR, Packet, Domain

if TYPE_CHECKING:
    from typing import List, Optional
    from network.base import CIDR, IPv4Addr
    from network.consumer_routers import ConsumerRouters

import random

class InternetRouter(Router):
    def __init__(self, children: List[ISPRouter] = None):
        children = children or []
        super().__init__(None, children, True)

    def request_subrange(self) -> CIDR:
        assert len(self.children) < 252, "Too many ISPs..."
        while True:
            current_subrange = random.randint(1, 255)
            if current_subrange in (10, 192, 127): continue
            for child in self.children:
                if child.subrange and child.subrange.domain[0] == current_subrange:
                    break
            else:
                return CIDR((current_subrange, 0, 0, 0), 8)
    
    def assign_ip(self) -> IPv4Addr:
        return (0,1,1,0)

    def domain_range(self) -> Optional[CIDR]:
        return (self.ip_address,0) if self.enabled else None
    
    def enable(self) -> None:
        assert False, 'Internet Router cannot be enabled.'

    def disable(self) -> None:
        assert False, 'Internet Router cannot be disabled.'

    def send_packet(self, packet: Packet):
        is_loopback = is_ip_in_domain(packet.dest.addr, self.LOOPBACK)
        assert not is_loopback, "How the fuck"
        
        for child in self.children:
            child_is_right = (child.ip_address == packet.dest.addr)
            dest_in_child = child.domain_range() and is_ip_in_domain(packet.dest.addr, child.domain_range())
            if child_is_right or dest_in_child:
                child.send_packet(packet)
                break
        else:
            not_found_packet = Packet(SocketAddr(self.ip_address, 
                                       self.get_unassigned_port()),
                                       packet.source, 
                                       b'MAGICDestination not found',
                                       True)
            self.send_packet(not_found_packet)


class ISPRouter(Router):

    def __init__(self, parent: InternetRouter, children: List[ConsumerRouters] = None, enabled: bool = True):
        assert parent or not enabled, "ISP routers cannot be turned on without a connection to the internet"
        self.blacklist: List[IPv4Addr] = [(0,1,1,0)]
        children = children or []
        self.subrange: Optional[CIDR] = parent.request_subrange() if enabled else None
        super().__init__(parent, children, enabled)

    def assign_ip(self) -> IPv4Addr:
        assert self.enabled, "Router should be enabled"
        b = random.randint(0,255)
        c = random.randint(0,255)
        d = random.randint(0,255)
        return (self.subrange.domain[0], b, c, d)

    def hand_ip(self) -> IPv4Addr:
        assert self.enabled, "Inactive ISP assigning address"
        assert len(self.children) < 2**20, "Too many nodes"
        while True:
            current_ip = (self.subrange.domain[0], random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            if current_ip == self.ip_address: continue
            for child in self.children:
                if child.ip_address and child.ip_address == current_ip:
                    break
            else:
                return current_ip

    def add_to_blacklist(self, address: IPv4Addr):
        is_loopback = is_ip_in_domain(address, self.LOOPBACK)
        assert not is_loopback, "How the fuck"
        self.blacklist.append(address)

    def domain_range(self) -> Optional[CIDR]:
        return self.subrange if self.enabled else None
    
    def enable(self) -> None:
        if self.enabled: return
        self.subrange = self.parent.request_subrange()
        super().enable()

    def disable(self) -> None:
        super().disable()
        self.subrange = None

    def send_packet(self, packet: Packet):
        is_loopback = is_ip_in_domain(packet.dest.addr, self.LOOPBACK)
        assert not is_loopback, "How the fuck"

        if packet.dest.addr in self.blacklist:
            SA = SocketAddr
            return_packet = Packet(SA(self.ip_address, 
                                      self.get_unassigned_port()), 
                                      packet.source, 
                                      b"MAGICBanned", 
                                      True)
            self.send_packet(return_packet)
            return
        
        if (is_ip_in_domain(packet.dest.addr, self.domain_range())):
            if packet.dest.addr == self.ip_address:
                self.send_packet(self.process_packet(packet))
                return
            for child in self.children:
                child_is_right = (child.ip_address == packet.dest.addr)
                if child_is_right:
                    child.send_packet(packet)
                    break
            else:
                not_found_packet = Packet(SocketAddr(self.ip_address, self.get_unassigned_port()), 
                                          packet.source, 
                                          b'MAGICDestination not found',
                                          True)
                self.send_packet(not_found_packet)
        else:
            self.parent.send_packet(packet)
