from __future__ import annotations

from dataclasses import dataclass

from simulation.network.base import IPv4Addr, Packet, Port
from simulation.network.consumer_routers import ConsumerRouter


@dataclass(frozen=True, eq=True)
class Binding:
    port: Port
    service_fn: callable[[Packet], bytes | None]
    

class ComputerNetworkAdapter(object):

    def __init__(self) -> None:
        self.parent: ConsumerRouter | None = None
        self.ip_address: IPv4Addr | None = None
        self.listeners: dict[Port, callable[[Packet], bytes | None]] = dict()
        self.buffer: list[Packet] = []

    def disconnect(self) -> None:
        if self.parent:
            self.parent.children.remove(self)
            self.parent = None
            self.ip_address = None

    def connect(self, router: ConsumerRouter, password: str | None) -> None:
        self.disconnect()
        if router.password == password:
            self.parent = router
            self.parent.children.append(self)
            self.ip_address = self.parent.hand_ip()

    def handle_request(self, packet: Packet) -> None:
        assert self.parent, 'Not connected to WiFi'
        
        if self.ip_address != packet.dest.addr:
            self.parent.send_packet(packet)
        
        elif packet.dest.port in self.listeners:
            msg = self.listeners[packet.dest.port](packet)
            if msg: self.parent.send_packet(Packet(packet.dest, packet.source, msg, response=True))

    def handle_response(self, packet: Packet) -> None:
        if self.ip_address == packet.dest.addr:
            self.buffer.append(packet)
    
    def send_packet(self, packet: Packet) -> None:
        if not packet.response:
            self.handle_request(packet)

        elif packet.response:
            self.handle_response(packet)