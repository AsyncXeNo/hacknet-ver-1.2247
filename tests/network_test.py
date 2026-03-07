from __future__ import annotations
import pytest
from types import SimpleNamespace
from typing import TYPE_CHECKING
from simulation.network import InternetRouter, ISPRouter, BusinessRouter, HomeRouter, Packet, SocketAddr
from loguru_config import configure_master_logger, remove_default_logger

from loguru import logger

if TYPE_CHECKING:
    from simulation.network import IPv4Addr, ConsumerRouter


class PacketSink:
    def __init__(self, parent_router: ConsumerRouter):
        self.received: list[Packet] = []
        self.parent: ConsumerRouter = parent_router
        self.ip_address: IPv4Addr = parent_router.hand_ip()
        self.parent.children.append(self)

    def send_packet(self, packet):
        self.received.append(packet)


@pytest.fixture
def network():
    internet_router = InternetRouter()

    isp1 = ISPRouter(internet_router)
    business1 = BusinessRouter(isp1)
    user1 = PacketSink(business1)
    home1 = HomeRouter(isp1)
    user2 = PacketSink(home1)
    user3 = PacketSink(home1)

    isp2 = ISPRouter(internet_router)
    business2 = BusinessRouter(isp2)
    user4 = PacketSink(business2)
    user5 = PacketSink(business2)
    home2 = HomeRouter(isp2)
    user6 = PacketSink(home2)
    home3 = HomeRouter(isp2)
    user7 = PacketSink(home3)
    user8 = PacketSink(home3)
    home4 = HomeRouter(isp2)
    user9 = PacketSink(home4)

    isp3 = ISPRouter(internet_router)
    business3 = BusinessRouter(isp3)
    user10 = PacketSink(business3)
    home5 = HomeRouter(isp3)
    user11 = PacketSink(home5)
    user12 = PacketSink(home5)
    home6 = HomeRouter(isp3)
    user13 = PacketSink(home6)
    home7 = HomeRouter(isp3)
    user14 = PacketSink(home7)
    user15 = PacketSink(home7)

    isp4 = ISPRouter(internet_router)
    business4 = BusinessRouter(isp4)
    user16 = PacketSink(business4)
    user17 = PacketSink(business4)
    business5 = BusinessRouter(isp4)
    user18 = PacketSink(business5)
    home8 = HomeRouter(isp4)
    user19 = PacketSink(home8)
    home9 = HomeRouter(isp4)
    user20 = PacketSink(home9)
    user21 = PacketSink(home9)
    home10 = HomeRouter(isp4)
    user22 = PacketSink(home10)
    home11 = HomeRouter(isp4)
    user23 = PacketSink(home11)
    home12 = HomeRouter(isp4)
    user24 = PacketSink(home12)
    user25 = PacketSink(home12)
    home13 = HomeRouter(isp4)
    user26 = PacketSink(home13)

    return SimpleNamespace(
        internet_router=internet_router,
        isp1=isp1,
        business1=business1,
        home1=home1,
        user1=user1,
        user2=user2,
        user3=user3,
        isp2=isp2,
        business2=business2,
        user4=user4,
        user5=user5,
        home2=home2,
        user6=user6,
        home3=home3,
        user7=user7,
        user8=user8,
        home4=home4,
        user9=user9,
        isp3=isp3,
        business3=business3,
        user10=user10,
        home5=home5,
        user11=user11,
        user12=user12,
        home6=home6,
        user13=user13,
        home7=home7,
        user14=user14,
        user15=user15,
        isp4=isp4,
        business4=business4,
        user16=user16,
        user17=user17,
        business5=business5,
        user18=user18,
        home8=home8,
        user19=user19,
        home9=home9,
        user20=user20,
        user21=user21,
        home10=home10,
        user22=user22,
        home11=home11,
        user23=user23,
        home12=home12,
        user24=user24,
        user25=user25,
        home13=home13,
        user26=user26,
    )


def test_packet_send_same_router_sibling(network):
    """Send a packet between two users on the same home router (user2 -> user3, both on home1)."""
    packet = Packet(
        source=SocketAddr(network.user2.ip_address, 5000),
        dest=SocketAddr(network.user3.ip_address, 8080),
        message=b"ICMPPing",
        response=False,
    )
    network.home1.send_packet(packet)
    assert len(network.user3.received) == 1
    assert network.user3.received[0].message == b"ICMPPing"


def test_packet_send_across_isps(network):
    """Send a packet between users on different ISPs (user2 on isp1 -> user6 on isp2)."""
    network.home2.forward(1000, SocketAddr(network.user6.ip_address,9000))
    packet = Packet(
        source=SocketAddr(network.user2.ip_address, 5000),
        dest=SocketAddr(network.home2.ip_address, 1000),
        message=b"ICMPPing",
        response=False,
    )
    network.home1.send_packet(packet)
    assert len(network.user6.received) == 1
    assert network.user6.received[0].message == b"ICMPPing"


def test_packet_send_home_to_business(network):
    """Send a packet from a home user to a business user across ISPs."""
    network.business1.forward(7000, SocketAddr(network.user1.ip_address, 7000))
    packet = Packet(
        source=SocketAddr(network.user2.ip_address, 5000),
        dest=SocketAddr(network.business1.ip_address, 7000),
        message=b"ICMPPing",
        response=False,
    )
    network.home1.send_packet(packet)
    assert len(network.user1.received) == 1
    assert network.user1.received[0].message == b"ICMPPing"


def test_packet_send_business_to_home(network):
    """Send a packet from a business user to a home user on a different ISP."""
    network.home1.forward(3000, SocketAddr(network.user2.ip_address, 3000))
    packet = Packet(
        source=SocketAddr(network.user4.ip_address, 5000),
        dest=SocketAddr(network.home1.ip_address, 3000),
        message=b"ICMPPing",
        response=False,
    )
    network.business2.send_packet(packet)
    assert len(network.user2.received) == 1
    assert network.user2.received[0].message == b"ICMPPing"


def test_ping_router_gets_pong(network):
    """Ping a router directly and expect an ICMPPong response via NAT."""
    packet = Packet(
        source=SocketAddr(network.user2.ip_address, 5000),
        dest=SocketAddr(network.isp1.ip_address, 80),
        message=b"ICMPPing",
        response=False,
    )
    network.home1.send_packet(packet)
    assert len(network.user2.received) == 1
    assert network.user2.received[0].message == b"ICMPPong"


def test_ping_across_many_hops(network):
    """Send a packet from isp1/home1 user to isp4/home13 user (max hops)."""
    network.home13.forward(4000, SocketAddr(network.user26.ip_address, 4000))
    packet = Packet(
        source=SocketAddr(network.user2.ip_address, 5000),
        dest=SocketAddr(network.home13.ip_address, 4000),
        message=b"ICMPPing",
        response=False,
    )
    network.home1.send_packet(packet)
    assert len(network.user26.received) == 1
    assert network.user26.received[0].message == b"ICMPPing"


def test_send_multiple_packets_to_same_dest(network):
    """Send multiple packets to the same destination."""
    network.home2.forward(9000, SocketAddr(network.user6.ip_address, 9000))
    for i in range(5):
        packet = Packet(
            source=SocketAddr(network.user2.ip_address, 5000 + i),
            dest=SocketAddr(network.home2.ip_address, 9000),
            message=f"ICMPPing{i}".encode(),
            response=False,
        )
        network.home1.send_packet(packet)
    assert len(network.user6.received) == 5
    for i in range(5):
        assert network.user6.received[i].message == f"ICMPPing{i}".encode()


def test_send_packet_nonexistent_dest(network):
    """Send a packet to an IP that doesn't exist - should get error back."""
    fake_ip = (-1, -1, -1, -1)
    packet = Packet(
        source=SocketAddr(network.user2.ip_address, 5000),
        dest=SocketAddr(fake_ip, 9000),
        message=b"ICMPPing",
        response=False,
    )
    network.home1.send_packet(packet)
    assert len(network.user2.received) == 1
    assert network.user2.received[0].message == b"MAGICDestination not found"


def test_business_to_business_same_isp(network):
    """Send between two business users on the same ISP (isp4)."""
    network.business5.forward(9000, SocketAddr(network.user18.ip_address, 9000))
    packet = Packet(
        source=SocketAddr(network.user16.ip_address, 5000),
        dest=SocketAddr(network.business5.ip_address, 9000),
        message=b"ICMPPing",
        response=False,
    )
    network.business4.send_packet(packet)
    assert len(network.user18.received) == 1
    assert network.user18.received[0].message == b"ICMPPing"


def test_bidirectional_ping(network):
    """Send a ping in both directions between two users."""
    network.home2.forward(9000, SocketAddr(network.user6.ip_address, 9000))
    network.home1.forward(5000, SocketAddr(network.user2.ip_address, 5000))
    packet1 = Packet(
        source=SocketAddr(network.user2.ip_address, 5000),
        dest=SocketAddr(network.home2.ip_address, 9000),
        message=b"ICMPPing",
        response=False,
    )
    network.home1.send_packet(packet1)

    packet2 = Packet(
        source=SocketAddr(network.user6.ip_address, 9000),
        dest=SocketAddr(network.home1.ip_address, 5000),
        message=b"ICMPPing",
        response=False,
    )
    network.home2.send_packet(packet2)

    assert len(network.user6.received) == 1
    assert network.user6.received[0].message == b"ICMPPing"
    assert len(network.user2.received) == 1
    assert network.user2.received[0].message == b"ICMPPing"