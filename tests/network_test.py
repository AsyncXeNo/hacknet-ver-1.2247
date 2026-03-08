from __future__ import annotations
import pytest
from types import SimpleNamespace
from typing import TYPE_CHECKING
from simulation.network import InternetRouter, ISPRouter, BusinessRouter, HomeRouter, Packet, SocketAddr, IPv4Addr

if TYPE_CHECKING:
    from simulation.network import ConsumerRouter


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


def test_same_router_sibling_delivery(network):
    """Packet between two users on the same home router is delivered internally."""
    packet = Packet(
        source=SocketAddr(network.user2.ip_address, 5000),
        dest=SocketAddr(network.user3.ip_address, 8080),
        message=b"ICMPPing",
        response=False,
    )
    network.home1.send_packet(packet)
    assert len(network.user3.received) == 1
    assert network.user3.received[0].message == b"ICMPPing"
    assert network.user3.received[0].source == SocketAddr(network.user2.ip_address, 5000)
    assert network.user3.received[0].dest == SocketAddr(network.user3.ip_address, 8080)
    assert network.user3.received[0].response is False


def test_cross_isp_with_port_forward(network):
    """Packet from isp1 user to isp2 user via port forwarding."""
    network.home2.forward(1000, SocketAddr(network.user6.ip_address, 9000))
    packet = Packet(
        source=SocketAddr(network.user2.ip_address, 5000),
        dest=SocketAddr(network.home2.ip_address, 1000),
        message=b"ICMPPing",
        response=False,
    )
    network.home1.send_packet(packet)
    assert len(network.user6.received) == 1
    assert network.user6.received[0].message == b"ICMPPing"
    assert network.user6.received[0].source.addr == network.home1.ip_address
    assert network.user6.received[0].dest == SocketAddr(network.user6.ip_address, 9000)
    assert network.user6.received[0].response is False


def test_home_to_business_cross_isp(network):
    """Home user sends to a business user on a different ISP."""
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
    assert network.user1.received[0].source.addr == network.home1.ip_address
    assert network.user1.received[0].dest == SocketAddr(network.user1.ip_address, 7000)
    assert network.user1.received[0].response is False


def test_business_to_home_cross_isp(network):
    """Business user sends to a home user on a different ISP."""
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
    assert network.user2.received[0].source.addr == network.business2.ip_address
    assert network.user2.received[0].dest == SocketAddr(network.user2.ip_address, 3000)
    assert network.user2.received[0].response is False


def test_ping_isp_router_gets_pong(network):
    """Pinging an ISP router directly returns ICMPPong via NAT."""
    packet = Packet(
        source=SocketAddr(network.user2.ip_address, 5000),
        dest=SocketAddr(network.isp1.ip_address, 80),
        message=b"ICMPPing",
        response=False,
    )
    network.home1.send_packet(packet)
    assert len(network.user2.received) == 1
    assert network.user2.received[0].message == b"ICMPPong"
    assert network.user2.received[0].source.addr == network.isp1.ip_address
    assert network.user2.received[0].dest == SocketAddr(network.user2.ip_address, 5000)
    assert network.user2.received[0].response is True


def test_max_hops_isp1_to_isp4(network):
    """Packet traverses from isp1/home1 to isp4/home13 (maximum hop count)."""
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
    assert network.user26.received[0].source.addr == network.home1.ip_address
    assert network.user26.received[0].dest == SocketAddr(network.user26.ip_address, 4000)
    assert network.user26.received[0].response is False


def test_multiple_packets_same_destination(network):
    """Five packets to the same forwarded port all arrive in order."""
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
        assert network.user6.received[i].source.addr == network.home1.ip_address
        assert network.user6.received[i].dest == SocketAddr(network.user6.ip_address, 9000)
        assert network.user6.received[i].response is False


def test_nonexistent_destination_returns_error(network):
    """Packet to a bogus IP gets a 'Destination not found' error back."""
    fake_ip = (200, 200, 200, 200)
    packet = Packet(
        source=SocketAddr(network.user2.ip_address, 5000),
        dest=SocketAddr(fake_ip, 9000),
        message=b"ICMPPing",
        response=False,
    )
    network.home1.send_packet(packet)
    assert len(network.user2.received) == 1
    assert network.user2.received[0].message == b"MAGICDestination not found"
    assert network.user2.received[0].source.addr == network.internet_router.ip_address
    assert network.user2.received[0].dest.addr == network.user2.ip_address
    assert network.user2.received[0].dest.port == 5000
    assert network.user2.received[0].response is True


def test_business_to_business_same_isp(network):
    """Two business routers on the same ISP can exchange packets."""
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
    assert network.user18.received[0].source.addr == network.business4.ip_address
    assert network.user18.received[0].dest == SocketAddr(network.user18.ip_address, 9000)
    assert network.user18.received[0].response is False


def test_bidirectional_exchange(network):
    """Two users send packets to each other via port forwarding."""
    network.home2.forward(9000, SocketAddr(network.user6.ip_address, 9000))
    network.home1.forward(5000, SocketAddr(network.user2.ip_address, 5000))

    p1 = Packet(
        source=SocketAddr(network.user2.ip_address, 5000),
        dest=SocketAddr(network.home2.ip_address, 9000),
        message=b"ICMPPing",
        response=False,
    )
    network.home1.send_packet(p1)

    p2 = Packet(
        source=SocketAddr(network.user6.ip_address, 9000),
        dest=SocketAddr(network.home1.ip_address, 5000),
        message=b"ICMPPing",
        response=False,
    )
    network.home2.send_packet(p2)

    assert len(network.user6.received) == 1
    assert network.user6.received[0].message == b"ICMPPing"
    assert network.user6.received[0].source.addr == network.home1.ip_address
    assert network.user6.received[0].dest == SocketAddr(network.user6.ip_address, 9000)
    assert network.user6.received[0].response is False
    assert len(network.user2.received) == 1
    assert network.user2.received[0].message == b"ICMPPing"
    assert network.user2.received[0].source.addr == network.home2.ip_address
    assert network.user2.received[0].dest == SocketAddr(network.user2.ip_address, 5000)
    assert network.user2.received[0].response is False


def test_dns_resolve_and_route(network):
    """DNS lookup resolves a domain, then the resolved IP is used to route a packet."""
    network.home6.forward(5000, SocketAddr(network.user13.ip_address, 5000))
    network.internet_router.map_domain("google.com", network.home6.ip_address)
    network.internet_router.flood_dns()

    dns_packet = Packet(
        source=SocketAddr(network.user2.ip_address, 9000),
        dest=SocketAddr(network.home1.ip_address, 90),
        message=b"DNSgoogle.com",
        response=False,
    )
    network.home1.send_packet(dns_packet)
    assert len(network.user2.received) == 1
    assert network.user2.received[0].source.addr == network.home1.ip_address
    assert network.user2.received[0].dest == SocketAddr(network.user2.ip_address, 9000)
    assert network.user2.received[0].response is True
    ip_addr = tuple(map(int, network.user2.received[0].message.decode()[3:].split('.')))

    packet = Packet(
        source=SocketAddr(network.user2.ip_address, 9000),
        dest=SocketAddr(ip_addr, 5000),
        message=b"ICMPPing",
        response=False,
    )
    network.home1.send_packet(packet)
    assert len(network.user13.received) == 1
    assert network.user13.received[0].message == b"ICMPPing"
    assert network.user13.received[0].source.addr == network.home1.ip_address
    assert network.user13.received[0].dest == SocketAddr(network.user13.ip_address, 5000)
    assert network.user13.received[0].response is False


def test_blacklist_blocks_and_returns_banned(network):
    """ISP blacklist prevents delivery and sends MAGICBanned back."""
    network.home2.forward(1000, SocketAddr(network.user6.ip_address, 9000))
    target_ip = network.home2.ip_address
    network.isp1.add_to_blacklist(target_ip)

    packet = Packet(
        source=SocketAddr(network.user2.ip_address, 5000),
        dest=SocketAddr(target_ip, 1000),
        message=b"ICMPPing",
        response=False,
    )
    network.home1.send_packet(packet)
    assert len(network.user6.received) == 0
    assert len(network.user2.received) == 1
    assert network.user2.received[0].message == b"MAGICBanned"
    assert network.user2.received[0].source.addr == network.isp1.ip_address
    assert network.user2.received[0].dest.addr == network.user2.ip_address
    assert network.user2.received[0].dest.port == 5000
    assert network.user2.received[0].response is True


def test_forbidden_range_home_to_business(network):
    """HomeRouter rejects packets destined for the 10.x.x.x (business) range."""
    business_internal_ip = (10, 50, 50, 50)
    packet = Packet(
        source=SocketAddr(network.user2.ip_address, 5000),
        dest=SocketAddr(business_internal_ip, 8080),
        message=b"ICMPPing",
        response=False,
    )
    network.home1.send_packet(packet)
    assert len(network.user2.received) == 1
    assert b"MAGICWrong Configuration" in network.user2.received[0].message
    assert network.user2.received[0].source.addr == network.home1.ip_address
    assert network.user2.received[0].dest == SocketAddr(network.user2.ip_address, 5000)
    assert network.user2.received[0].response is True


def test_forbidden_range_business_to_home(network):
    """BusinessRouter rejects packets destined for the 192.168.x.x (home) range."""
    home_internal_ip = (192, 168, 50, 50)
    packet = Packet(
        source=SocketAddr(network.user1.ip_address, 5000),
        dest=SocketAddr(home_internal_ip, 8080),
        message=b"ICMPPing",
        response=False,
    )
    network.business1.send_packet(packet)
    assert len(network.user1.received) == 1
    assert b"MAGICWrong Configuration" in network.user1.received[0].message
    assert network.user1.received[0].source.addr == network.business1.ip_address
    assert network.user1.received[0].dest == SocketAddr(network.user1.ip_address, 5000)
    assert network.user1.received[0].response is True


def test_ping_own_router_private_ip(network):
    """Pinging the router's own private IP returns ICMPPong."""
    packet = Packet(
        source=SocketAddr(network.user2.ip_address, 5000),
        dest=SocketAddr(network.home1.PRIVATE_IP, 80),
        message=b"ICMPPing",
        response=False,
    )
    network.home1.send_packet(packet)
    assert len(network.user2.received) == 1
    assert network.user2.received[0].message == b"ICMPPong"
    assert network.user2.received[0].source.addr == network.home1.ip_address
    assert network.user2.received[0].dest == SocketAddr(network.user2.ip_address, 5000)
    assert network.user2.received[0].response is True


### New tests for edge cases and special functionalities


def test_stop_forwarding_blocks_delivery(network):
    """After stop_forwarding, packets to that port are processed by the router instead."""
    network.home2.forward(1000, SocketAddr(network.user6.ip_address, 9000))
    network.home2.stop_forwarding(1000)
    packet = Packet(
        source=SocketAddr(network.user2.ip_address, 5000),
        dest=SocketAddr(network.home2.ip_address, 1000),
        message=b"ICMPPing",
        response=False,
    )
    network.home1.send_packet(packet)
    assert len(network.user6.received) == 0
    assert len(network.user2.received) == 1
    assert network.user2.received[0].message == b"ICMPPong"
    assert network.user2.received[0].source.addr == network.home2.ip_address
    assert network.user2.received[0].dest.addr == network.user2.ip_address
    assert network.user2.received[0].dest.port == 5000
    assert network.user2.received[0].response is True


def test_dns_not_found(network):
    """DNS query for an unmapped domain returns an error."""
    dns_packet = Packet(
        source=SocketAddr(network.user2.ip_address, 9000),
        dest=SocketAddr(network.home1.ip_address, 90),
        message=b"DNSnotreal.xyz",
        response=False,
    )
    network.home1.send_packet(dns_packet)
    assert len(network.user2.received) == 1
    assert network.user2.received[0].message == b"MAGICDNS not found"
    assert network.user2.received[0].source.addr == network.home1.ip_address
    assert network.user2.received[0].dest == SocketAddr(network.user2.ip_address, 9000)
    assert network.user2.received[0].response is True


def test_dns_with_www_prefix(network):
    """DNS query with www. prefix still resolves the base domain."""
    network.home6.forward(5000, SocketAddr(network.user13.ip_address, 5000))
    network.internet_router.map_domain("example.com", network.home6.ip_address)
    network.internet_router.flood_dns()

    dns_packet = Packet(
        source=SocketAddr(network.user2.ip_address, 9000),
        dest=SocketAddr(network.home1.ip_address, 90),
        message=b"DNSwww.example.com",
        response=False,
    )
    network.home1.send_packet(dns_packet)
    assert len(network.user2.received) == 1
    assert network.user2.received[0].message.startswith(b"DNS")
    assert network.user2.received[0].source.addr == network.home1.ip_address
    assert network.user2.received[0].dest == SocketAddr(network.user2.ip_address, 9000)
    assert network.user2.received[0].response is True


def test_unrecognized_protocol_returns_cannot_process(network):
    """A message with no known protocol prefix gets 'Cannot process'."""
    packet = Packet(
        source=SocketAddr(network.user2.ip_address, 5000),
        dest=SocketAddr(network.home1.PRIVATE_IP, 80),
        message=b"GARBAGEfoobar",
        response=False,
    )
    network.home1.send_packet(packet)
    assert len(network.user2.received) == 1
    assert network.user2.received[0].message == b"MAGICCannot process"
    assert network.user2.received[0].source.addr == network.home1.ip_address
    assert network.user2.received[0].dest == SocketAddr(network.user2.ip_address, 5000)
    assert network.user2.received[0].response is True


def test_business_router_sibling_delivery(network):
    """Two users on the same business router can exchange packets internally."""
    packet = Packet(
        source=SocketAddr(network.user4.ip_address, 5000),
        dest=SocketAddr(network.user5.ip_address, 8080),
        message=b"ICMPPing",
        response=False,
    )
    network.business2.send_packet(packet)
    assert len(network.user5.received) == 1
    assert network.user5.received[0].message == b"ICMPPing"
    assert network.user5.received[0].source == SocketAddr(network.user4.ip_address, 5000)
    assert network.user5.received[0].dest == SocketAddr(network.user5.ip_address, 8080)
    assert network.user5.received[0].response is False


def test_internet_router_ip_is_blacklisted_by_default(network):
    """ISPs blacklist the internet router IP (0,1,1,0) by default."""
    packet = Packet(
        source=SocketAddr(network.user2.ip_address, 5000),
        dest=SocketAddr((0, 1, 1, 0), 80),
        message=b"ICMPPing",
        response=False,
    )
    network.home1.send_packet(packet)
    assert len(network.user2.received) == 1
    assert network.user2.received[0].message == b"MAGICBanned"
    assert network.user2.received[0].source.addr == network.isp1.ip_address
    assert network.user2.received[0].dest.addr == network.user2.ip_address
    assert network.user2.received[0].dest.port == 5000
    assert network.user2.received[0].response is True


def test_packet_to_public_ip_no_forward_processes_locally(network):
    """Packet to a consumer router's public IP with no port forward is processed by the router."""
    packet = Packet(
        source=SocketAddr(network.user2.ip_address, 5000),
        dest=SocketAddr(network.home2.ip_address, 9999),
        message=b"ICMPPing",
        response=False,
    )
    network.home1.send_packet(packet)
    assert len(network.user2.received) == 1
    assert network.user2.received[0].message == b"ICMPPong"
    assert network.user2.received[0].source.addr == network.home2.ip_address
    assert network.user2.received[0].dest.addr == network.user2.ip_address
    assert network.user2.received[0].dest.port == 5000
    assert network.user2.received[0].response is True


def test_multiple_port_forwards_on_same_router(network):
    """Multiple port forwards on one router each deliver to the correct user."""
    network.home3.forward(1000, SocketAddr(network.user7.ip_address, 1000))
    network.home3.forward(2000, SocketAddr(network.user8.ip_address, 2000))

    p1 = Packet(
        source=SocketAddr(network.user2.ip_address, 5000),
        dest=SocketAddr(network.home3.ip_address, 1000),
        message=b"ICMPPing",
        response=False,
    )
    p2 = Packet(
        source=SocketAddr(network.user2.ip_address, 5001),
        dest=SocketAddr(network.home3.ip_address, 2000),
        message=b"ICMPPing",
        response=False,
    )
    network.home1.send_packet(p1)
    network.home1.send_packet(p2)

    assert len(network.user7.received) == 1
    assert network.user7.received[0].source.addr == network.home1.ip_address
    assert network.user7.received[0].dest == SocketAddr(network.user7.ip_address, 1000)
    assert network.user7.received[0].response is False
    assert len(network.user8.received) == 1
    assert network.user8.received[0].source.addr == network.home1.ip_address
    assert network.user8.received[0].dest == SocketAddr(network.user8.ip_address, 2000)
    assert network.user8.received[0].response is False


def test_same_isp_different_routers(network):
    """Packet between two home routers on the same ISP (home3 -> home4, both on isp2)."""
    network.home4.forward(6000, SocketAddr(network.user9.ip_address, 6000))
    packet = Packet(
        source=SocketAddr(network.user7.ip_address, 5000),
        dest=SocketAddr(network.home4.ip_address, 6000),
        message=b"ICMPPing",
        response=False,
    )
    network.home3.send_packet(packet)
    assert len(network.user9.received) == 1
    assert network.user9.received[0].message == b"ICMPPing"
    assert network.user9.received[0].source.addr == network.home3.ip_address
    assert network.user9.received[0].dest == SocketAddr(network.user9.ip_address, 6000)
    assert network.user9.received[0].response is False


def test_del_domain_removes_dns(network):
    """Deleting a domain mapping makes subsequent DNS lookups fail."""
    network.internet_router.map_domain("ephemeral.io", network.home1.ip_address)
    network.internet_router.flood_dns()
    network.home1.del_domain("ephemeral.io")

    dns_packet = Packet(
        source=SocketAddr(network.user2.ip_address, 9000),
        dest=SocketAddr(network.home1.ip_address, 90),
        message=b"DNSephemeral.io",
        response=False,
    )
    network.home1.send_packet(dns_packet)
    assert len(network.user2.received) == 1
    assert network.user2.received[0].message == b"MAGICDNS not found"
    assert network.user2.received[0].source.addr == network.home1.ip_address
    assert network.user2.received[0].dest == SocketAddr(network.user2.ip_address, 9000)
    assert network.user2.received[0].response is True


def test_blacklist_multiple_ips(network):
    """Blacklisting multiple IPs blocks all of them."""
    ip_a = network.home2.ip_address
    ip_b = network.home3.ip_address
    network.isp1.add_to_blacklist(ip_a)
    network.isp1.add_to_blacklist(ip_b)

    p1 = Packet(
        source=SocketAddr(network.user2.ip_address, 5000),
        dest=SocketAddr(ip_a, 80),
        message=b"ICMPPing",
        response=False,
    )
    p2 = Packet(
        source=SocketAddr(network.user3.ip_address, 5000),
        dest=SocketAddr(ip_b, 80),
        message=b"ICMPPing",
        response=False,
    )
    network.home1.send_packet(p1)
    network.home1.send_packet(p2)

    assert len(network.user2.received) == 1
    assert network.user2.received[0].message == b"MAGICBanned"
    assert network.user2.received[0].source.addr == network.isp1.ip_address
    assert network.user2.received[0].dest.addr == network.user2.ip_address
    assert network.user2.received[0].dest.port == 5000
    assert network.user2.received[0].response is True
    assert len(network.user3.received) == 1
    assert network.user3.received[0].message == b"MAGICBanned"
    assert network.user3.received[0].source.addr == network.isp1.ip_address
    assert network.user3.received[0].dest.addr == network.user3.ip_address
    assert network.user3.received[0].dest.port == 5000
    assert network.user3.received[0].response is True


def test_forward_then_stop_then_forward_again(network):
    """Port forward can be re-established after being stopped."""
    network.home2.forward(1000, SocketAddr(network.user6.ip_address, 9000))
    network.home2.stop_forwarding(1000)
    network.home2.forward(1000, SocketAddr(network.user6.ip_address, 9000))

    packet = Packet(
        source=SocketAddr(network.user2.ip_address, 5000),
        dest=SocketAddr(network.home2.ip_address, 1000),
        message=b"ICMPPing",
        response=False,
    )
    network.home1.send_packet(packet)
    assert len(network.user6.received) == 1
    assert network.user6.received[0].message == b"ICMPPing"
    assert network.user6.received[0].source.addr == network.home1.ip_address
    assert network.user6.received[0].dest == SocketAddr(network.user6.ip_address, 9000)
    assert network.user6.received[0].response is False


def test_ping_business_router_private_ip(network):
    """Pinging a business router's private IP (10.0.0.1) returns ICMPPong."""
    packet = Packet(
        source=SocketAddr(network.user1.ip_address, 5000),
        dest=SocketAddr(network.business1.PRIVATE_IP, 80),
        message=b"ICMPPing",
        response=False,
    )
    network.business1.send_packet(packet)
    assert len(network.user1.received) == 1
    assert network.user1.received[0].message == b"ICMPPong"
    assert network.user1.received[0].source.addr == network.business1.ip_address
    assert network.user1.received[0].dest == SocketAddr(network.user1.ip_address, 5000)
    assert network.user1.received[0].response is True


def test_dns_flood_propagates_to_nested_routers(network):
    """DNS flood from internet router reaches ISP and consumer routers."""
    network.internet_router.map_domain("deep.net", network.home5.ip_address)
    network.internet_router.flood_dns()

    assert "deep.net" in network.isp1.dns_record
    assert "deep.net" in network.home1.dns_record
    assert "deep.net" in network.isp3.dns_record
    assert "deep.net" in network.business3.dns_record


### NAT Timeout

def test_nat_timeout_pass(network):
    from game_timer import game_timer
    
    network.home6.forward(8900, SocketAddr(network.user13.ip_address, 8900))

    packet_front = Packet(SocketAddr(network.user2.ip_address, 9000), 
                          SocketAddr(network.home6.ip_address, 8900),
                          b'yo',
                          False)

    network.home1.send_packet(packet_front)

    assert len(network.user13.received) == 1
    nat_sock = network.user13.received[0].source

    print(nat_sock)

    game_timer.delta_time(10)

    packet_back = Packet(SocketAddr(network.user13.ip_address, 8900), nat_sock, b'wazzup', True)

    network.home6.send_packet(packet_back)

    assert len(network.user2.received) == 1
    assert network.user2.received[0].message == b'wazzup'


def test_nat_timeout_fail(network):
    from game_timer import game_timer
    
    network.home6.forward(8900, SocketAddr(network.user13.ip_address, 8900))

    packet_front = Packet(SocketAddr(network.user2.ip_address, 9000), 
                          SocketAddr(network.home6.ip_address, 8900),
                          b'yo',
                          False)

    network.home1.send_packet(packet_front)

    assert len(network.user13.received) == 1
    nat_sock = network.user13.received[0].source

    print(nat_sock)

    game_timer.delta_time(400)

    packet_back = Packet(SocketAddr(network.user13.ip_address, 8900), nat_sock, b'wazzup', True)

    network.home6.send_packet(packet_back)

    assert len(network.user2.received) == 0


### Disconnect and Connect to different ConsumerRouter

def test_switch_routers(network):
    first_ip = network.user2.parent.ip_address
    assert network.user2 in network.home1.children
    network.home1.children.remove(network.user2)

    network.user2.parent = network.home3
    network.home3.children.append(network.user2)
    network.user2.ip_address = network.user2.parent.hand_ip()
    
    assert first_ip != network.user2.parent.ip_address

    network.home3.forward(8900, SocketAddr(network.user2.ip_address, 8900))

    packet = Packet(SocketAddr(network.user3.ip_address, 9000), SocketAddr(network.home3.ip_address, 8900), b'ICMPPing', False)

    network.home1.send_packet(packet)

    assert len(network.user2.received) == 1
    assert network.user2.received[0].message == b'ICMPPing'