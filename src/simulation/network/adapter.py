from dataclasses import dataclass

from simulation.network.base import IPv4Addr, Packet, Port
from simulation.network.consumer_routers import ConsumerRouter


@dataclass(frozen=True, eq=True)
class Binding:
    port: Port
    service_fn: callable[[Packet], bytes | None]
    

class ComputerNetworkAdapter(object):

    def __init__(self, parent: ConsumerRouter, listeners: list[Binding]) -> None:
        self.parent: ConsumerRouter = parent
        self.ip_address: IPv4Addr | None = self.parent.hand_ip() if self.enabled else None
        self.listeners: list[Binding] = listeners or []
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

    def enable(self) -> None:
        pass

    def disable(self) -> None:
        self.disconnect()
    
    def handle_request(self, packet: Packet) -> None:
        if self.ip_address != packet.dest.addr:
            self.parent.send_packet(packet)
        for listener in self.listeners:
            if self.ip_address == packet.dest.addr and listener.port == packet.dest.port:
                msg = listener.service_fn(packet)
                if msg: self.parent.send_packet(Packet(packet.dest, packet.source, msg, response=True))

    def handle_response(self, packet: Packet) -> None:
        if self.ip_address == packet.dest.addr:
            self.buffer.append(packet)
    
    def send_packet(self, packet: Packet) -> None:
        if not packet.response:
            self.handle_request(packet)

        elif packet.response:
            self.handle_response(packet)