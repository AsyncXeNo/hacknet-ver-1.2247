from __future__ import annotations
import time
import pytest
from types import SimpleNamespace
from typing import TYPE_CHECKING
from threading import Thread
from simulation.network import InternetRouter, ISPRouter, BusinessRouter, HomeRouter, Packet, SocketAddr, IPv4Addr
from simulation.network.adapter import ComputerNetworkAdapter
from simulation.node import OperatingSystem, Computer, NetworkAdapterAccess, HardwareResource, ComputerSwitchedOff, PortInUseException
from simulation.application import Application
from game_timer import game_timer

if TYPE_CHECKING:
    from simulation.network import ConsumerRouter


# class PacketSink:
#     def __init__(self, parent_router: ConsumerRouter):
#         self.received: list[Packet] = []
#         self.parent: ConsumerRouter = parent_router
#         self.ip_address: IPv4Addr = parent_router.hand_ip()
#         self.parent.children.append(self)
#
#     def send_packet(self, packet):
#         self.received.append(packet)
#
#
# @pytest.fixture
# def network():
#     internet_router = InternetRouter()
#
#     isp1 = ISPRouter(internet_router)
#     business1 = BusinessRouter('biz1', 'pass1', isp1)
#     user1 = PacketSink(business1)
#     home1 = HomeRouter('home1', 'pass1', isp1)
#     user2 = PacketSink(home1)
#     user3 = PacketSink(home1)
#
#     isp2 = ISPRouter(internet_router)
#     business2 = BusinessRouter('biz2', 'pass2', isp2)
#     user4 = PacketSink(business2)
#     user5 = PacketSink(business2)
#     home2 = HomeRouter('home2', 'pass2', isp2)
#     user6 = PacketSink(home2)
#     home3 = HomeRouter('home3', 'pass3', isp2)
#     user7 = PacketSink(home3)
#     user8 = PacketSink(home3)
#     home4 = HomeRouter('home4', 'pass4', isp2)
#     user9 = PacketSink(home4)
#
#     isp3 = ISPRouter(internet_router)
#     business3 = BusinessRouter('biz3', 'pass3', isp3)
#     user10 = PacketSink(business3)
#     home5 = HomeRouter('home5', 'pass5', isp3)
#     user11 = PacketSink(home5)
#     user12 = PacketSink(home5)
#     home6 = HomeRouter('home6', 'pass6', isp3)
#     user13 = PacketSink(home6)
#     home7 = HomeRouter('home7', 'pass7', isp3)
#     user14 = PacketSink(home7)
#     user15 = PacketSink(home7)
#
#     isp4 = ISPRouter(internet_router)
#     business4 = BusinessRouter('biz4', 'pass4', isp4)
#     user16 = PacketSink(business4)
#     user17 = PacketSink(business4)
#     business5 = BusinessRouter('biz5', 'pass5', isp4)
#     user18 = PacketSink(business5)
#     home8 = HomeRouter('home8', 'pass8', isp4)
#     user19 = PacketSink(home8)
#     home9 = HomeRouter('home9', 'pass9', isp4)
#     user20 = PacketSink(home9)
#     user21 = PacketSink(home9)
#     home10 = HomeRouter('home10', 'pass10', isp4)
#     user22 = PacketSink(home10)
#     home11 = HomeRouter('home11', 'pass11', isp4)
#     user23 = PacketSink(home11)
#     home12 = HomeRouter('home12', 'pass12', isp4)
#     user24 = PacketSink(home12)
#     user25 = PacketSink(home12)
#     home13 = HomeRouter('home13', 'pass13', isp4)
#     user26 = PacketSink(home13)
#
#     return SimpleNamespace(
#         internet_router=internet_router,
#         isp1=isp1,
#         business1=business1,
#         home1=home1,
#         user1=user1,
#         user2=user2,
#         user3=user3,
#         isp2=isp2,
#         business2=business2,
#         user4=user4,
#         user5=user5,
#         home2=home2,
#         user6=user6,
#         home3=home3,
#         user7=user7,
#         user8=user8,
#         home4=home4,
#         user9=user9,
#         isp3=isp3,
#         business3=business3,
#         user10=user10,
#         home5=home5,
#         user11=user11,
#         user12=user12,
#         home6=home6,
#         user13=user13,
#         home7=home7,
#         user14=user14,
#         user15=user15,
#         isp4=isp4,
#         business4=business4,
#         user16=user16,
#         user17=user17,
#         business5=business5,
#         user18=user18,
#         home8=home8,
#         user19=user19,
#         home9=home9,
#         user20=user20,
#         user21=user21,
#         home10=home10,
#         user22=user22,
#         home11=home11,
#         user23=user23,
#         home12=home12,
#         user24=user24,
#         user25=user25,
#         home13=home13,
#         user26=user26,
#     )
#
#
# def test_same_router_sibling_delivery(network):
#     """Packet between two users on the same home router is delivered internally."""
#     packet = Packet(
#         source=SocketAddr(network.user2.ip_address, 5000),
#         dest=SocketAddr(network.user3.ip_address, 8080),
#         message=b"ICMPPing",
#         response=False,
#     )
#     network.home1.send_packet(packet)
#     assert len(network.user3.received) == 1
#     assert network.user3.received[0].message == b"ICMPPing"
#     assert network.user3.received[0].source == SocketAddr(network.user2.ip_address, 5000)
#     assert network.user3.received[0].dest == SocketAddr(network.user3.ip_address, 8080)
#     assert network.user3.received[0].response is False
#
#
# def test_cross_isp_with_port_forward(network):
#     """Packet from isp1 user to isp2 user via port forwarding."""
#     network.home2.forward(1000, SocketAddr(network.user6.ip_address, 9000))
#     packet = Packet(
#         source=SocketAddr(network.user2.ip_address, 5000),
#         dest=SocketAddr(network.home2.ip_address, 1000),
#         message=b"ICMPPing",
#         response=False,
#     )
#     network.home1.send_packet(packet)
#     assert len(network.user6.received) == 1
#     assert network.user6.received[0].message == b"ICMPPing"
#     assert network.user6.received[0].source.addr == network.home1.ip_address
#     assert network.user6.received[0].dest == SocketAddr(network.user6.ip_address, 9000)
#     assert network.user6.received[0].response is False
#
#
# def test_home_to_business_cross_isp(network):
#     """Home user sends to a business user on a different ISP."""
#     network.business1.forward(7000, SocketAddr(network.user1.ip_address, 7000))
#     packet = Packet(
#         source=SocketAddr(network.user2.ip_address, 5000),
#         dest=SocketAddr(network.business1.ip_address, 7000),
#         message=b"ICMPPing",
#         response=False,
#     )
#     network.home1.send_packet(packet)
#     assert len(network.user1.received) == 1
#     assert network.user1.received[0].message == b"ICMPPing"
#     assert network.user1.received[0].source.addr == network.home1.ip_address
#     assert network.user1.received[0].dest == SocketAddr(network.user1.ip_address, 7000)
#     assert network.user1.received[0].response is False
#
#
# def test_business_to_home_cross_isp(network):
#     """Business user sends to a home user on a different ISP."""
#     network.home1.forward(3000, SocketAddr(network.user2.ip_address, 3000))
#     packet = Packet(
#         source=SocketAddr(network.user4.ip_address, 5000),
#         dest=SocketAddr(network.home1.ip_address, 3000),
#         message=b"ICMPPing",
#         response=False,
#     )
#     network.business2.send_packet(packet)
#     assert len(network.user2.received) == 1
#     assert network.user2.received[0].message == b"ICMPPing"
#     assert network.user2.received[0].source.addr == network.business2.ip_address
#     assert network.user2.received[0].dest == SocketAddr(network.user2.ip_address, 3000)
#     assert network.user2.received[0].response is False
#
#
# def test_ping_isp_router_gets_pong(network):
#     """Pinging an ISP router directly returns ICMPPong via NAT."""
#     packet = Packet(
#         source=SocketAddr(network.user2.ip_address, 5000),
#         dest=SocketAddr(network.isp1.ip_address, 80),
#         message=b"ICMPPing",
#         response=False,
#     )
#     network.home1.send_packet(packet)
#     assert len(network.user2.received) == 1
#     assert network.user2.received[0].message == b"ICMPPong"
#     assert network.user2.received[0].source.addr == network.isp1.ip_address
#     assert network.user2.received[0].dest == SocketAddr(network.user2.ip_address, 5000)
#     assert network.user2.received[0].response is True
#
#
# def test_max_hops_isp1_to_isp4(network):
#     """Packet traverses from isp1/home1 to isp4/home13 (maximum hop count)."""
#     network.home13.forward(4000, SocketAddr(network.user26.ip_address, 4000))
#     packet = Packet(
#         source=SocketAddr(network.user2.ip_address, 5000),
#         dest=SocketAddr(network.home13.ip_address, 4000),
#         message=b"ICMPPing",
#         response=False,
#     )
#     network.home1.send_packet(packet)
#     assert len(network.user26.received) == 1
#     assert network.user26.received[0].message == b"ICMPPing"
#     assert network.user26.received[0].source.addr == network.home1.ip_address
#     assert network.user26.received[0].dest == SocketAddr(network.user26.ip_address, 4000)
#     assert network.user26.received[0].response is False
#
#
# def test_multiple_packets_same_destination(network):
#     """Five packets to the same forwarded port all arrive in order."""
#     network.home2.forward(9000, SocketAddr(network.user6.ip_address, 9000))
#     for i in range(5):
#         packet = Packet(
#             source=SocketAddr(network.user2.ip_address, 5000 + i),
#             dest=SocketAddr(network.home2.ip_address, 9000),
#             message=f"ICMPPing{i}".encode(),
#             response=False,
#         )
#         network.home1.send_packet(packet)
#     assert len(network.user6.received) == 5
#     for i in range(5):
#         assert network.user6.received[i].message == f"ICMPPing{i}".encode()
#         assert network.user6.received[i].source.addr == network.home1.ip_address
#         assert network.user6.received[i].dest == SocketAddr(network.user6.ip_address, 9000)
#         assert network.user6.received[i].response is False
#
#
# def test_nonexistent_destination_returns_error(network):
#     """Packet to a bogus IP gets a 'Destination not found' error back."""
#     fake_ip = (200, 200, 200, 200)
#     packet = Packet(
#         source=SocketAddr(network.user2.ip_address, 5000),
#         dest=SocketAddr(fake_ip, 9000),
#         message=b"ICMPPing",
#         response=False,
#     )
#     network.home1.send_packet(packet)
#     assert len(network.user2.received) == 1
#     assert network.user2.received[0].message == b"MAGICDestination not found"
#     assert network.user2.received[0].source.addr == network.internet_router.ip_address
#     assert network.user2.received[0].dest.addr == network.user2.ip_address
#     assert network.user2.received[0].dest.port == 5000
#     assert network.user2.received[0].response is True
#
#
# def test_business_to_business_same_isp(network):
#     """Two business routers on the same ISP can exchange packets."""
#     network.business5.forward(9000, SocketAddr(network.user18.ip_address, 9000))
#     packet = Packet(
#         source=SocketAddr(network.user16.ip_address, 5000),
#         dest=SocketAddr(network.business5.ip_address, 9000),
#         message=b"ICMPPing",
#         response=False,
#     )
#     network.business4.send_packet(packet)
#     assert len(network.user18.received) == 1
#     assert network.user18.received[0].message == b"ICMPPing"
#     assert network.user18.received[0].source.addr == network.business4.ip_address
#     assert network.user18.received[0].dest == SocketAddr(network.user18.ip_address, 9000)
#     assert network.user18.received[0].response is False
#
#
# def test_bidirectional_exchange(network):
#     """Two users send packets to each other via port forwarding."""
#     network.home2.forward(9000, SocketAddr(network.user6.ip_address, 9000))
#     network.home1.forward(5000, SocketAddr(network.user2.ip_address, 5000))
#
#     p1 = Packet(
#         source=SocketAddr(network.user2.ip_address, 5000),
#         dest=SocketAddr(network.home2.ip_address, 9000),
#         message=b"ICMPPing",
#         response=False,
#     )
#     network.home1.send_packet(p1)
#
#     p2 = Packet(
#         source=SocketAddr(network.user6.ip_address, 9000),
#         dest=SocketAddr(network.home1.ip_address, 5000),
#         message=b"ICMPPing",
#         response=False,
#     )
#     network.home2.send_packet(p2)
#
#     assert len(network.user6.received) == 1
#     assert network.user6.received[0].message == b"ICMPPing"
#     assert network.user6.received[0].source.addr == network.home1.ip_address
#     assert network.user6.received[0].dest == SocketAddr(network.user6.ip_address, 9000)
#     assert network.user6.received[0].response is False
#     assert len(network.user2.received) == 1
#     assert network.user2.received[0].message == b"ICMPPing"
#     assert network.user2.received[0].source.addr == network.home2.ip_address
#     assert network.user2.received[0].dest == SocketAddr(network.user2.ip_address, 5000)
#     assert network.user2.received[0].response is False
#
#
# def test_dns_resolve_and_route(network):
#     """DNS lookup resolves a domain, then the resolved IP is used to route a packet."""
#     network.home6.forward(5000, SocketAddr(network.user13.ip_address, 5000))
#     network.internet_router.map_domain("google.com", network.home6.ip_address)
#     network.internet_router.flood_dns()
#
#     dns_packet = Packet(
#         source=SocketAddr(network.user2.ip_address, 9000),
#         dest=SocketAddr(network.home1.ip_address, 90),
#         message=b"DNSgoogle.com",
#         response=False,
#     )
#     network.home1.send_packet(dns_packet)
#     assert len(network.user2.received) == 1
#     assert network.user2.received[0].source.addr == network.home1.ip_address
#     assert network.user2.received[0].dest == SocketAddr(network.user2.ip_address, 9000)
#     assert network.user2.received[0].response is True
#     ip_addr = tuple(map(int, network.user2.received[0].message.decode()[3:].split('.')))
#
#     packet = Packet(
#         source=SocketAddr(network.user2.ip_address, 9000),
#         dest=SocketAddr(ip_addr, 5000),
#         message=b"ICMPPing",
#         response=False,
#     )
#     network.home1.send_packet(packet)
#     assert len(network.user13.received) == 1
#     assert network.user13.received[0].message == b"ICMPPing"
#     assert network.user13.received[0].source.addr == network.home1.ip_address
#     assert network.user13.received[0].dest == SocketAddr(network.user13.ip_address, 5000)
#     assert network.user13.received[0].response is False
#
#
# def test_blacklist_blocks_and_returns_banned(network):
#     """ISP blacklist prevents delivery and sends MAGICBanned back."""
#     network.home2.forward(1000, SocketAddr(network.user6.ip_address, 9000))
#     target_ip = network.home2.ip_address
#     network.isp1.add_to_blacklist(target_ip)
#
#     packet = Packet(
#         source=SocketAddr(network.user2.ip_address, 5000),
#         dest=SocketAddr(target_ip, 1000),
#         message=b"ICMPPing",
#         response=False,
#     )
#     network.home1.send_packet(packet)
#     assert len(network.user6.received) == 0
#     assert len(network.user2.received) == 1
#     assert network.user2.received[0].message == b"MAGICBanned"
#     assert network.user2.received[0].source.addr == network.isp1.ip_address
#     assert network.user2.received[0].dest.addr == network.user2.ip_address
#     assert network.user2.received[0].dest.port == 5000
#     assert network.user2.received[0].response is True
#
#
# def test_forbidden_range_home_to_business(network):
#     """HomeRouter rejects packets destined for the 10.x.x.x (business) range."""
#     business_internal_ip = (10, 50, 50, 50)
#     packet = Packet(
#         source=SocketAddr(network.user2.ip_address, 5000),
#         dest=SocketAddr(business_internal_ip, 8080),
#         message=b"ICMPPing",
#         response=False,
#     )
#     network.home1.send_packet(packet)
#     assert len(network.user2.received) == 1
#     assert b"MAGICWrong Configuration" in network.user2.received[0].message
#     assert network.user2.received[0].source.addr == network.home1.ip_address
#     assert network.user2.received[0].dest == SocketAddr(network.user2.ip_address, 5000)
#     assert network.user2.received[0].response is True
#
#
# def test_forbidden_range_business_to_home(network):
#     """BusinessRouter rejects packets destined for the 192.168.x.x (home) range."""
#     home_internal_ip = (192, 168, 50, 50)
#     packet = Packet(
#         source=SocketAddr(network.user1.ip_address, 5000),
#         dest=SocketAddr(home_internal_ip, 8080),
#         message=b"ICMPPing",
#         response=False,
#     )
#     network.business1.send_packet(packet)
#     assert len(network.user1.received) == 1
#     assert b"MAGICWrong Configuration" in network.user1.received[0].message
#     assert network.user1.received[0].source.addr == network.business1.ip_address
#     assert network.user1.received[0].dest == SocketAddr(network.user1.ip_address, 5000)
#     assert network.user1.received[0].response is True
#
#
# def test_ping_own_router_private_ip(network):
#     """Pinging the router's own private IP returns ICMPPong."""
#     packet = Packet(
#         source=SocketAddr(network.user2.ip_address, 5000),
#         dest=SocketAddr(network.home1.PRIVATE_IP, 80),
#         message=b"ICMPPing",
#         response=False,
#     )
#     network.home1.send_packet(packet)
#     assert len(network.user2.received) == 1
#     assert network.user2.received[0].message == b"ICMPPong"
#     assert network.user2.received[0].source.addr == network.home1.ip_address
#     assert network.user2.received[0].dest == SocketAddr(network.user2.ip_address, 5000)
#     assert network.user2.received[0].response is True
#
#
# ### New tests for edge cases and special functionalities
#
#
# def test_stop_forwarding_blocks_delivery(network):
#     """After stop_forwarding, packets to that port are processed by the router instead."""
#     network.home2.forward(1000, SocketAddr(network.user6.ip_address, 9000))
#     network.home2.stop_forwarding(1000)
#     packet = Packet(
#         source=SocketAddr(network.user2.ip_address, 5000),
#         dest=SocketAddr(network.home2.ip_address, 1000),
#         message=b"ICMPPing",
#         response=False,
#     )
#     network.home1.send_packet(packet)
#     assert len(network.user6.received) == 0
#     assert len(network.user2.received) == 1
#     assert network.user2.received[0].message == b"ICMPPong"
#     assert network.user2.received[0].source.addr == network.home2.ip_address
#     assert network.user2.received[0].dest.addr == network.user2.ip_address
#     assert network.user2.received[0].dest.port == 5000
#     assert network.user2.received[0].response is True
#
#
# def test_dns_not_found(network):
#     """DNS query for an unmapped domain returns an error."""
#     dns_packet = Packet(
#         source=SocketAddr(network.user2.ip_address, 9000),
#         dest=SocketAddr(network.home1.ip_address, 90),
#         message=b"DNSnotreal.xyz",
#         response=False,
#     )
#     network.home1.send_packet(dns_packet)
#     assert len(network.user2.received) == 1
#     assert network.user2.received[0].message == b"MAGICDNS not found"
#     assert network.user2.received[0].source.addr == network.home1.ip_address
#     assert network.user2.received[0].dest == SocketAddr(network.user2.ip_address, 9000)
#     assert network.user2.received[0].response is True
#
#
# def test_dns_with_www_prefix(network):
#     """DNS query with www. prefix still resolves the base domain."""
#     network.home6.forward(5000, SocketAddr(network.user13.ip_address, 5000))
#     network.internet_router.map_domain("example.com", network.home6.ip_address)
#     network.internet_router.flood_dns()
#
#     dns_packet = Packet(
#         source=SocketAddr(network.user2.ip_address, 9000),
#         dest=SocketAddr(network.home1.ip_address, 90),
#         message=b"DNSwww.example.com",
#         response=False,
#     )
#     network.home1.send_packet(dns_packet)
#     assert len(network.user2.received) == 1
#     assert network.user2.received[0].message.startswith(b"DNS")
#     assert network.user2.received[0].source.addr == network.home1.ip_address
#     assert network.user2.received[0].dest == SocketAddr(network.user2.ip_address, 9000)
#     assert network.user2.received[0].response is True
#
#
# def test_unrecognized_protocol_returns_cannot_process(network):
#     """A message with no known protocol prefix gets 'Cannot process'."""
#     packet = Packet(
#         source=SocketAddr(network.user2.ip_address, 5000),
#         dest=SocketAddr(network.home1.PRIVATE_IP, 80),
#         message=b"GARBAGEfoobar",
#         response=False,
#     )
#     network.home1.send_packet(packet)
#     assert len(network.user2.received) == 1
#     assert network.user2.received[0].message == b"MAGICCannot process"
#     assert network.user2.received[0].source.addr == network.home1.ip_address
#     assert network.user2.received[0].dest == SocketAddr(network.user2.ip_address, 5000)
#     assert network.user2.received[0].response is True
#
#
# def test_business_router_sibling_delivery(network):
#     """Two users on the same business router can exchange packets internally."""
#     packet = Packet(
#         source=SocketAddr(network.user4.ip_address, 5000),
#         dest=SocketAddr(network.user5.ip_address, 8080),
#         message=b"ICMPPing",
#         response=False,
#     )
#     network.business2.send_packet(packet)
#     assert len(network.user5.received) == 1
#     assert network.user5.received[0].message == b"ICMPPing"
#     assert network.user5.received[0].source == SocketAddr(network.user4.ip_address, 5000)
#     assert network.user5.received[0].dest == SocketAddr(network.user5.ip_address, 8080)
#     assert network.user5.received[0].response is False
#
#
# def test_internet_router_ip_is_blacklisted_by_default(network):
#     """ISPs blacklist the internet router IP (0,1,1,0) by default."""
#     packet = Packet(
#         source=SocketAddr(network.user2.ip_address, 5000),
#         dest=SocketAddr((0, 1, 1, 0), 80),
#         message=b"ICMPPing",
#         response=False,
#     )
#     network.home1.send_packet(packet)
#     assert len(network.user2.received) == 1
#     assert network.user2.received[0].message == b"MAGICBanned"
#     assert network.user2.received[0].source.addr == network.isp1.ip_address
#     assert network.user2.received[0].dest.addr == network.user2.ip_address
#     assert network.user2.received[0].dest.port == 5000
#     assert network.user2.received[0].response is True
#
#
# def test_packet_to_public_ip_no_forward_processes_locally(network):
#     """Packet to a consumer router's public IP with no port forward is processed by the router."""
#     packet = Packet(
#         source=SocketAddr(network.user2.ip_address, 5000),
#         dest=SocketAddr(network.home2.ip_address, 9999),
#         message=b"ICMPPing",
#         response=False,
#     )
#     network.home1.send_packet(packet)
#     assert len(network.user2.received) == 1
#     assert network.user2.received[0].message == b"ICMPPong"
#     assert network.user2.received[0].source.addr == network.home2.ip_address
#     assert network.user2.received[0].dest.addr == network.user2.ip_address
#     assert network.user2.received[0].dest.port == 5000
#     assert network.user2.received[0].response is True
#
#
# def test_multiple_port_forwards_on_same_router(network):
#     """Multiple port forwards on one router each deliver to the correct user."""
#     network.home3.forward(1000, SocketAddr(network.user7.ip_address, 1000))
#     network.home3.forward(2000, SocketAddr(network.user8.ip_address, 2000))
#
#     p1 = Packet(
#         source=SocketAddr(network.user2.ip_address, 5000),
#         dest=SocketAddr(network.home3.ip_address, 1000),
#         message=b"ICMPPing",
#         response=False,
#     )
#     p2 = Packet(
#         source=SocketAddr(network.user2.ip_address, 5001),
#         dest=SocketAddr(network.home3.ip_address, 2000),
#         message=b"ICMPPing",
#         response=False,
#     )
#     network.home1.send_packet(p1)
#     network.home1.send_packet(p2)
#
#     assert len(network.user7.received) == 1
#     assert network.user7.received[0].source.addr == network.home1.ip_address
#     assert network.user7.received[0].dest == SocketAddr(network.user7.ip_address, 1000)
#     assert network.user7.received[0].response is False
#     assert len(network.user8.received) == 1
#     assert network.user8.received[0].source.addr == network.home1.ip_address
#     assert network.user8.received[0].dest == SocketAddr(network.user8.ip_address, 2000)
#     assert network.user8.received[0].response is False
#
#
# def test_same_isp_different_routers(network):
#     """Packet between two home routers on the same ISP (home3 -> home4, both on isp2)."""
#     network.home4.forward(6000, SocketAddr(network.user9.ip_address, 6000))
#     packet = Packet(
#         source=SocketAddr(network.user7.ip_address, 5000),
#         dest=SocketAddr(network.home4.ip_address, 6000),
#         message=b"ICMPPing",
#         response=False,
#     )
#     network.home3.send_packet(packet)
#     assert len(network.user9.received) == 1
#     assert network.user9.received[0].message == b"ICMPPing"
#     assert network.user9.received[0].source.addr == network.home3.ip_address
#     assert network.user9.received[0].dest == SocketAddr(network.user9.ip_address, 6000)
#     assert network.user9.received[0].response is False
#
#
# def test_del_domain_removes_dns(network):
#     """Deleting a domain mapping makes subsequent DNS lookups fail."""
#     network.internet_router.map_domain("ephemeral.io", network.home1.ip_address)
#     network.internet_router.flood_dns()
#     network.home1.del_domain("ephemeral.io")
#
#     dns_packet = Packet(
#         source=SocketAddr(network.user2.ip_address, 9000),
#         dest=SocketAddr(network.home1.ip_address, 90),
#         message=b"DNSephemeral.io",
#         response=False,
#     )
#     network.home1.send_packet(dns_packet)
#     assert len(network.user2.received) == 1
#     assert network.user2.received[0].message == b"MAGICDNS not found"
#     assert network.user2.received[0].source.addr == network.home1.ip_address
#     assert network.user2.received[0].dest == SocketAddr(network.user2.ip_address, 9000)
#     assert network.user2.received[0].response is True
#
#
# def test_blacklist_multiple_ips(network):
#     """Blacklisting multiple IPs blocks all of them."""
#     ip_a = network.home2.ip_address
#     ip_b = network.home3.ip_address
#     network.isp1.add_to_blacklist(ip_a)
#     network.isp1.add_to_blacklist(ip_b)
#
#     p1 = Packet(
#         source=SocketAddr(network.user2.ip_address, 5000),
#         dest=SocketAddr(ip_a, 80),
#         message=b"ICMPPing",
#         response=False,
#     )
#     p2 = Packet(
#         source=SocketAddr(network.user3.ip_address, 5000),
#         dest=SocketAddr(ip_b, 80),
#         message=b"ICMPPing",
#         response=False,
#     )
#     network.home1.send_packet(p1)
#     network.home1.send_packet(p2)
#
#     assert len(network.user2.received) == 1
#     assert network.user2.received[0].message == b"MAGICBanned"
#     assert network.user2.received[0].source.addr == network.isp1.ip_address
#     assert network.user2.received[0].dest.addr == network.user2.ip_address
#     assert network.user2.received[0].dest.port == 5000
#     assert network.user2.received[0].response is True
#     assert len(network.user3.received) == 1
#     assert network.user3.received[0].message == b"MAGICBanned"
#     assert network.user3.received[0].source.addr == network.isp1.ip_address
#     assert network.user3.received[0].dest.addr == network.user3.ip_address
#     assert network.user3.received[0].dest.port == 5000
#     assert network.user3.received[0].response is True
#
#
# def test_forward_then_stop_then_forward_again(network):
#     """Port forward can be re-established after being stopped."""
#     network.home2.forward(1000, SocketAddr(network.user6.ip_address, 9000))
#     network.home2.stop_forwarding(1000)
#     network.home2.forward(1000, SocketAddr(network.user6.ip_address, 9000))
#
#     packet = Packet(
#         source=SocketAddr(network.user2.ip_address, 5000),
#         dest=SocketAddr(network.home2.ip_address, 1000),
#         message=b"ICMPPing",
#         response=False,
#     )
#     network.home1.send_packet(packet)
#     assert len(network.user6.received) == 1
#     assert network.user6.received[0].message == b"ICMPPing"
#     assert network.user6.received[0].source.addr == network.home1.ip_address
#     assert network.user6.received[0].dest == SocketAddr(network.user6.ip_address, 9000)
#     assert network.user6.received[0].response is False
#
#
# def test_ping_business_router_private_ip(network):
#     """Pinging a business router's private IP (10.0.0.1) returns ICMPPong."""
#     packet = Packet(
#         source=SocketAddr(network.user1.ip_address, 5000),
#         dest=SocketAddr(network.business1.PRIVATE_IP, 80),
#         message=b"ICMPPing",
#         response=False,
#     )
#     network.business1.send_packet(packet)
#     assert len(network.user1.received) == 1
#     assert network.user1.received[0].message == b"ICMPPong"
#     assert network.user1.received[0].source.addr == network.business1.ip_address
#     assert network.user1.received[0].dest == SocketAddr(network.user1.ip_address, 5000)
#     assert network.user1.received[0].response is True
#
#
# def test_dns_flood_propagates_to_nested_routers(network):
#     """DNS flood from internet router reaches ISP and consumer routers."""
#     network.internet_router.map_domain("deep.net", network.home5.ip_address)
#     network.internet_router.flood_dns()
#
#     assert "deep.net" in network.isp1.dns_record
#     assert "deep.net" in network.home1.dns_record
#     assert "deep.net" in network.isp3.dns_record
#     assert "deep.net" in network.business3.dns_record
#
#
# ### NAT Timeout
#
# def test_nat_timeout_pass(network):
#     from game_timer import game_timer
#
#     network.home6.forward(8900, SocketAddr(network.user13.ip_address, 8900))
#
#     packet_front = Packet(SocketAddr(network.user2.ip_address, 9000),
#                           SocketAddr(network.home6.ip_address, 8900),
#                           b'yo',
#                           False)
#
#     network.home1.send_packet(packet_front)
#
#     assert len(network.user13.received) == 1
#     nat_sock = network.user13.received[0].source
#
#     print(nat_sock)
#
#     game_timer.delta_time(10)
#
#     packet_back = Packet(SocketAddr(network.user13.ip_address, 8900), nat_sock, b'wazzup', True)
#
#     network.home6.send_packet(packet_back)
#
#     assert len(network.user2.received) == 1
#     assert network.user2.received[0].message == b'wazzup'
#
#
# def test_nat_timeout_fail(network):
#     from game_timer import game_timer
#
#     network.home6.forward(8900, SocketAddr(network.user13.ip_address, 8900))
#
#     packet_front = Packet(SocketAddr(network.user2.ip_address, 9000),
#                           SocketAddr(network.home6.ip_address, 8900),
#                           b'yo',
#                           False)
#
#     network.home1.send_packet(packet_front)
#
#     assert len(network.user13.received) == 1
#     nat_sock = network.user13.received[0].source
#
#     print(nat_sock)
#
#     game_timer.delta_time(300 * 1000)
#
#     packet_back = Packet(SocketAddr(network.user13.ip_address, 8900), nat_sock, b'wazzup', True)
#
#     network.home6.send_packet(packet_back)
#
#     assert len(network.user2.received) == 0
#
#
# ### Disconnect and Connect to different ConsumerRouter
#
# def test_switch_routers(network):
#     first_ip = network.user2.parent.ip_address
#     assert network.user2 in network.home1.children
#     network.home1.children.remove(network.user2)
#
#     network.user2.parent = network.home3
#     network.home3.children.append(network.user2)
#     network.user2.ip_address = network.user2.parent.hand_ip()
#
#     assert first_ip != network.user2.parent.ip_address
#
#     network.home3.forward(8900, SocketAddr(network.user2.ip_address, 8900))
#
#     packet = Packet(SocketAddr(network.user3.ip_address, 9000), SocketAddr(network.home3.ip_address, 8900), b'ICMPPing', False)
#
#     network.home1.send_packet(packet)
#
#     assert len(network.user2.received) == 1
#     assert network.user2.received[0].message == b'ICMPPing'


###############################################################################
# End-to-end tests: Computer -> OS -> NetworkAdapterAccess -> Adapter -> Router
###############################################################################


class StubOS(OperatingSystem):
    pass


class StubApp(Application):
    def __init__(self, name: str = "test_app"):
        super().__init__()
        self.name = name


def make_computer(router: ConsumerRouter, password: str | None) -> Computer:
    """Create a Computer, switch it on, and connect its adapter to the router."""
    os = StubOS()
    comp = Computer(os, total_ram=1024)
    comp.switch_on()
    comp.network_adaptor_base.connect(router, password)
    return comp


def advance_timer_in_background(delay_real: float, game_secs: float):
    """After a real-time delay, advance the game timer so check_buffer can time out."""
    def _advance():
        time.sleep(delay_real)
        game_timer.delta_time(game_secs * 1000)
    Thread(target=_advance, daemon=True).start()


@pytest.fixture(autouse=True)
def reset_game_timer():
    """Reset game timer to 0 before every test."""
    game_timer.update_time(0)
    yield


@pytest.fixture
def e2e():
    """End-to-end fixture: two home routers on different ISPs, each with a computer."""
    internet = InternetRouter()

    isp_a = ISPRouter(internet)
    home_a = HomeRouter('home_a', 'alpha', isp_a)

    isp_b = ISPRouter(internet)
    home_b = HomeRouter('home_b', 'beta', isp_b)

    comp_a = make_computer(home_a, 'alpha')
    comp_b = make_computer(home_b, 'beta')

    return SimpleNamespace(
        internet=internet,
        isp_a=isp_a, home_a=home_a, comp_a=comp_a,
        isp_b=isp_b, home_b=home_b, comp_b=comp_b,
    )


@pytest.fixture
def local():
    """Two computers on the same home router."""
    internet = InternetRouter()
    isp = ISPRouter(internet)
    home = HomeRouter('home', 'pass', isp)

    comp_a = make_computer(home, 'pass')
    comp_b = make_computer(home, 'pass')

    return SimpleNamespace(
        internet=internet, isp=isp, home=home,
        comp_a=comp_a, comp_b=comp_b,
    )


@pytest.fixture
def biz():
    """Business router setup with a computer."""
    internet = InternetRouter()
    isp = ISPRouter(internet)
    business = BusinessRouter('biz', 'bizpass', isp)

    comp = make_computer(business, 'bizpass')

    return SimpleNamespace(
        internet=internet, isp=isp, business=business, comp=comp,
    )


# ---------------------------------------------------------------------------
# Adapter: connect / disconnect
# ---------------------------------------------------------------------------

class TestAdapterConnectDisconnect:
    def test_connect_assigns_ip(self, e2e):
        """Computer gets an IP in the router's private range after connecting."""
        adapter = e2e.comp_a.network_adaptor_base
        assert adapter.ip_address is not None
        assert adapter.ip_address[0] == 192 and adapter.ip_address[1] == 168

    def test_connect_adds_to_router_children(self, e2e):
        """Adapter appears in the router's children list after connecting."""
        adapter = e2e.comp_a.network_adaptor_base
        assert adapter in e2e.home_a.children

    def test_disconnect_clears_ip(self, e2e):
        """Disconnecting removes the IP address."""
        adapter = e2e.comp_a.network_adaptor_base
        adapter.disconnect()
        assert adapter.ip_address is None

    def test_disconnect_removes_from_children(self, e2e):
        """Disconnecting removes adapter from router's children."""
        adapter = e2e.comp_a.network_adaptor_base
        adapter.disconnect()
        assert adapter not in e2e.home_a.children

    def test_wrong_password_does_not_connect(self):
        """Wrong WiFi password leaves adapter unconnected."""
        internet = InternetRouter()
        isp = ISPRouter(internet)
        home = HomeRouter('secure', 'correct_pass', isp)

        os = StubOS()
        comp = Computer(os, total_ram=1024)
        comp.switch_on()
        comp.network_adaptor_base.connect(home, 'wrong_pass')

        assert comp.network_adaptor_base.ip_address is None
        assert comp.network_adaptor_base not in home.children

    def test_reconnect_to_different_router(self, e2e):
        """Adapter can disconnect from one router and connect to another."""
        adapter = e2e.comp_a.network_adaptor_base
        old_ip = adapter.ip_address

        adapter.disconnect()
        adapter.connect(e2e.home_b, 'beta')

        assert adapter.ip_address is not None
        assert adapter.ip_address != old_ip
        assert adapter in e2e.home_b.children
        assert adapter not in e2e.home_a.children


# ---------------------------------------------------------------------------
# Computer: power state
# ---------------------------------------------------------------------------

class TestComputerPower:
    def test_get_resource_when_off_raises(self):
        """Accessing hardware on a powered-off computer raises ComputerSwitchedOff."""
        os = StubOS()
        comp = Computer(os, total_ram=1024)
        with pytest.raises(ComputerSwitchedOff):
            comp.get_resource(HardwareResource.NETWORK_ADAPTER)

    def test_get_resource_when_on_returns_adapter(self):
        """Accessing NETWORK_ADAPTER on a powered-on computer returns NetworkAdapterAccess."""
        os = StubOS()
        comp = Computer(os, total_ram=1024)
        comp.switch_on()
        res = comp.get_resource(HardwareResource.NETWORK_ADAPTER)
        assert isinstance(res, NetworkAdapterAccess)


# ---------------------------------------------------------------------------
# OS: bind / unbind
# ---------------------------------------------------------------------------

class TestOSBindUnbind:
    def test_bind_registers_listener(self, local):
        """syscall.bind registers a listener on the adapter."""
        app = StubApp()
        service_fn = lambda pkt: b"ICMPPong"
        local.comp_a.os.syscall.bind(app, 8080, service_fn)

        adapter = local.comp_a.network_adaptor_base
        assert 8080 in adapter.listeners

    def test_bind_duplicate_port_raises(self, local):
        """Binding a port that's already in use raises PortInUseException."""
        app_a = StubApp("app_a")
        app_b = StubApp("app_b")
        local.comp_a.os.syscall.bind(app_a, 8080, lambda pkt: None)

        with pytest.raises(PortInUseException):
            local.comp_a.os.syscall.bind(app_b, 8080, lambda pkt: None)

    def test_unbind_removes_listener(self, local):
        """syscall.unbind removes the listener from the adapter."""
        app = StubApp()
        local.comp_a.os.syscall.bind(app, 8080, lambda pkt: None)
        local.comp_a.os.syscall.unbind(app, 8080)

        adapter = local.comp_a.network_adaptor_base
        assert 8080 not in adapter.listeners

    def test_rebind_after_unbind(self, local):
        """A port can be rebound after unbinding."""
        app = StubApp()
        local.comp_a.os.syscall.bind(app, 8080, lambda pkt: None)
        local.comp_a.os.syscall.unbind(app, 8080)
        local.comp_a.os.syscall.bind(app, 8080, lambda pkt: b"hello")

        adapter = local.comp_a.network_adaptor_base
        assert 8080 in adapter.listeners


# ---------------------------------------------------------------------------
# OS: create_packet
# ---------------------------------------------------------------------------

class TestOSCreatePacket:
    def test_create_packet_has_correct_source_ip(self, local):
        """create_packet uses the adapter's IP as source address."""
        app = StubApp()
        dest = SocketAddr(IPv4Addr(8, 8, 8, 8), 80)
        pkt = local.comp_a.os.create_packet(app, dest, b"ICMPPing")

        adapter = local.comp_a.network_adaptor_base
        assert pkt.source.addr == adapter.ip_address

    def test_create_packet_has_correct_dest(self, local):
        """create_packet sets the destination as provided."""
        app = StubApp()
        dest = SocketAddr(IPv4Addr(8, 8, 8, 8), 80)
        pkt = local.comp_a.os.create_packet(app, dest, b"ICMPPing")

        assert pkt.dest == dest

    def test_create_packet_is_request(self, local):
        """create_packet sets response=False."""
        app = StubApp()
        dest = SocketAddr(IPv4Addr(8, 8, 8, 8), 80)
        pkt = local.comp_a.os.create_packet(app, dest, b"ICMPPing")

        assert pkt.response is False


# ---------------------------------------------------------------------------
# E2E: listener-based service on adapter (no OS request, direct adapter flow)
# ---------------------------------------------------------------------------

class TestAdapterListenerService:
    def test_listener_receives_request_and_sends_response(self, local):
        """A bound listener on comp_b receives a request routed from comp_a and responds."""
        received = []

        def echo_service(pkt: Packet) -> bytes | None:
            received.append(pkt)
            return b"ICMPPong"

        adapter_b = local.comp_b.network_adaptor_base
        adapter_b.listeners[9000] = echo_service

        adapter_a = local.comp_a.network_adaptor_base
        pkt = Packet(
            source=SocketAddr(adapter_a.ip_address, 5000),
            dest=SocketAddr(adapter_b.ip_address, 9000),
            message=b"ICMPPing",
            response=False,
        )
        local.home.send_packet(pkt)

        assert len(received) == 1
        assert received[0].message == b"ICMPPing"
        # Response should land in comp_a's adapter buffer
        assert len(adapter_a.buffer) == 1
        assert adapter_a.buffer[0].message == b"ICMPPong"

    def test_listener_returning_none_sends_no_response(self, local):
        """A listener that returns None does not generate a response packet."""
        def silent_service(pkt: Packet) -> bytes | None:
            return None

        adapter_b = local.comp_b.network_adaptor_base
        adapter_b.listeners[9000] = silent_service

        adapter_a = local.comp_a.network_adaptor_base
        pkt = Packet(
            source=SocketAddr(adapter_a.ip_address, 5000),
            dest=SocketAddr(adapter_b.ip_address, 9000),
            message=b"ICMPPing",
            response=False,
        )
        local.home.send_packet(pkt)

        assert len(adapter_a.buffer) == 0


# ---------------------------------------------------------------------------
# E2E: blocking request through OS syscall
# ---------------------------------------------------------------------------

class TestBlockingRequest:
    def test_ping_router_private_ip_blocking(self, local):
        """OS blocking request to router's private IP gets ICMPPong."""
        app = StubApp()
        dest = SocketAddr(local.home.PRIVATE_IP, 80)
        pkt = local.comp_a.os.create_packet(app, dest, b"ICMPPing")

        # The packet delivery is synchronous through routers, but check_buffer
        # polls with time.sleep(0.1). The send thread delivers instantly, so
        # the response should be in the buffer before the first poll.
        response = local.comp_a.os.syscall.request_blocking(app, pkt, timeout_secs=5)

        assert response is not None
        assert response.message == b"ICMPPong"

    def test_ping_isp_via_os_blocking(self, e2e):
        """OS blocking request to ISP router gets ICMPPong (goes through NAT)."""
        app = StubApp()
        dest = SocketAddr(e2e.isp_a.ip_address, 80)
        pkt = e2e.comp_a.os.create_packet(app, dest, b"ICMPPing")

        response = e2e.comp_a.os.syscall.request_blocking(app, pkt, timeout_secs=5)

        assert response is not None
        assert response.message == b"ICMPPong"

    def test_blocking_request_to_listener_cross_isp(self, e2e):
        """Blocking request from comp_a to comp_b's listener across ISPs."""
        server_app = StubApp("server")
        e2e.comp_b.os.syscall.bind(server_app, 9000, lambda pkt: b"ICMPPong")

        # Port-forward on home_b so external traffic reaches comp_b
        adapter_b = e2e.comp_b.network_adaptor_base
        e2e.home_b.forward(9000, SocketAddr(adapter_b.ip_address, 9000))

        client_app = StubApp("client")
        dest = SocketAddr(e2e.home_b.ip_address, 9000)
        pkt = e2e.comp_a.os.create_packet(client_app, dest, b"ICMPPing")

        response = e2e.comp_a.os.syscall.request_blocking(client_app, pkt, timeout_secs=5)

        assert response is not None
        assert response.message == b"ICMPPong"

    def test_blocking_request_timeout_no_listener(self, e2e):
        """Blocking request to a port with no listener on remote computer times out (no response from adapter)."""
        # home_b port-forwards to comp_b, but comp_b has no listener on that port
        adapter_b = e2e.comp_b.network_adaptor_base
        e2e.home_b.forward(7777, SocketAddr(adapter_b.ip_address, 7777))

        client_app = StubApp("client")
        dest = SocketAddr(e2e.home_b.ip_address, 7777)
        pkt = e2e.comp_a.os.create_packet(client_app, dest, b"ICMPPing")

        # Need to advance game_timer so the timeout fires
        advance_timer_in_background(delay_real=0.3, game_secs=10)
        response = e2e.comp_a.os.syscall.request_blocking(client_app, pkt, timeout_secs=5)

        assert response is None

    def test_blocking_request_bogus_destination(self, e2e):
        """Blocking request to a nonexistent IP returns MAGICDestination not found."""
        app = StubApp()
        dest = SocketAddr(IPv4Addr(200, 200, 200, 200), 80)
        pkt = e2e.comp_a.os.create_packet(app, dest, b"ICMPPing")

        response = e2e.comp_a.os.syscall.request_blocking(app, pkt, timeout_secs=5)

        assert response is not None
        assert response.message == b"MAGICDestination not found"

    def test_blocking_request_blacklisted_ip(self, e2e):
        """Blocking request to a blacklisted IP returns MAGICBanned."""
        e2e.isp_a.add_to_blacklist(e2e.home_b.ip_address)

        app = StubApp()
        dest = SocketAddr(e2e.home_b.ip_address, 80)
        pkt = e2e.comp_a.os.create_packet(app, dest, b"ICMPPing")

        response = e2e.comp_a.os.syscall.request_blocking(app, pkt, timeout_secs=5)

        assert response is not None
        assert response.message == b"MAGICBanned"


# ---------------------------------------------------------------------------
# E2E: async request + poll through OS syscall
# ---------------------------------------------------------------------------

class TestAsyncRequestPoll:
    def test_async_ping_router_then_poll(self, local):
        """Async request to router private IP, then poll retrieves the response."""
        app = StubApp()
        dest = SocketAddr(local.home.PRIVATE_IP, 80)
        pkt = local.comp_a.os.create_packet(app, dest, b"ICMPPing")

        local.comp_a.os.syscall.request_async(app, pkt, timeout_secs=5)
        # Give the background thread time to deliver + buffer
        time.sleep(0.5)

        packets = local.comp_a.os.syscall.poll(app)
        assert packets is not None
        assert len(packets) == 1
        assert packets[0].message == b"ICMPPong"

    def test_poll_returns_none_when_no_response(self, local):
        """Polling before any async request returns None."""
        app = StubApp()
        result = local.comp_a.os.syscall.poll(app)
        assert result is None

    def test_async_cross_isp_with_listener(self, e2e):
        """Async request to a service across ISPs, then poll to get the response."""
        server_app = StubApp("server")
        e2e.comp_b.os.syscall.bind(server_app, 9000, lambda pkt: b"ICMPPong")
        adapter_b = e2e.comp_b.network_adaptor_base
        e2e.home_b.forward(9000, SocketAddr(adapter_b.ip_address, 9000))

        client_app = StubApp("client")
        dest = SocketAddr(e2e.home_b.ip_address, 9000)
        pkt = e2e.comp_a.os.create_packet(client_app, dest, b"ICMPPing")

        e2e.comp_a.os.syscall.request_async(client_app, pkt, timeout_secs=5)
        time.sleep(0.5)

        packets = e2e.comp_a.os.syscall.poll(client_app)
        assert packets is not None
        assert len(packets) == 1
        assert packets[0].message == b"ICMPPong"

    def test_poll_consumes_buffer(self, local):
        """Polling drains the buffer — second poll returns None."""
        app = StubApp()
        dest = SocketAddr(local.home.PRIVATE_IP, 80)
        pkt = local.comp_a.os.create_packet(app, dest, b"ICMPPing")

        local.comp_a.os.syscall.request_async(app, pkt, timeout_secs=5)
        time.sleep(0.5)

        first = local.comp_a.os.syscall.poll(app)
        assert first is not None

        second = local.comp_a.os.syscall.poll(app)
        assert second is None


# ---------------------------------------------------------------------------
# E2E: DNS resolution through OS
# ---------------------------------------------------------------------------

class TestDNSEndToEnd:
    def test_dns_resolve_blocking(self, e2e):
        """Blocking DNS query to local router resolves a mapped domain."""
        e2e.internet.map_domain("test.com", e2e.home_b.ip_address)
        e2e.internet.flood_dns()

        app = StubApp()
        dest = SocketAddr(e2e.home_a.PRIVATE_IP, 53)
        pkt = e2e.comp_a.os.create_packet(app, dest, b"DNStest.com")

        response = e2e.comp_a.os.syscall.request_blocking(app, pkt, timeout_secs=5)

        assert response is not None
        assert response.message.startswith(b"DNS")
        resolved_ip = tuple(map(int, response.message.decode()[3:].split('.')))
        assert resolved_ip == tuple(e2e.home_b.ip_address)

    def test_dns_then_ping_resolved_ip_blocking(self, e2e):
        """Resolve a domain via DNS, then ping the resolved IP end-to-end."""
        e2e.internet.map_domain("server.io", e2e.home_b.ip_address)
        e2e.internet.flood_dns()

        app = StubApp()

        # Step 1: DNS resolve
        dns_dest = SocketAddr(e2e.home_a.PRIVATE_IP, 53)
        dns_pkt = e2e.comp_a.os.create_packet(app, dns_dest, b"DNSserver.io")
        dns_resp = e2e.comp_a.os.syscall.request_blocking(app, dns_pkt, timeout_secs=5)
        assert dns_resp is not None
        resolved_ip = IPv4Addr(*map(int, dns_resp.message.decode()[3:].split('.')))

        # Step 2: Ping the resolved public IP (router processes it)
        ping_dest = SocketAddr(resolved_ip, 80)
        ping_pkt = e2e.comp_a.os.create_packet(app, ping_dest, b"ICMPPing")
        ping_resp = e2e.comp_a.os.syscall.request_blocking(app, ping_pkt, timeout_secs=5)

        assert ping_resp is not None
        assert ping_resp.message == b"ICMPPong"


# ---------------------------------------------------------------------------
# E2E: bidirectional communication with application listeners
# ---------------------------------------------------------------------------

class TestBidirectionalE2E:
    def test_two_computers_exchange_messages(self, e2e):
        """comp_a sends to comp_b's service, comp_b sends to comp_a's service."""
        app_a = StubApp("app_a")
        app_b = StubApp("app_b")

        e2e.comp_a.os.syscall.bind(app_a, 8000, lambda pkt: b"ICMPPong")
        e2e.comp_b.os.syscall.bind(app_b, 9000, lambda pkt: b"ICMPPong")

        adapter_a = e2e.comp_a.network_adaptor_base
        adapter_b = e2e.comp_b.network_adaptor_base
        e2e.home_a.forward(8000, SocketAddr(adapter_a.ip_address, 8000))
        e2e.home_b.forward(9000, SocketAddr(adapter_b.ip_address, 9000))

        # comp_a -> comp_b
        dest_b = SocketAddr(e2e.home_b.ip_address, 9000)
        pkt_to_b = e2e.comp_a.os.create_packet(app_a, dest_b, b"ICMPPing")
        resp_from_b = e2e.comp_a.os.syscall.request_blocking(app_a, pkt_to_b, timeout_secs=5)

        assert resp_from_b is not None
        assert resp_from_b.message == b"ICMPPong"

        # comp_b -> comp_a
        dest_a = SocketAddr(e2e.home_a.ip_address, 8000)
        pkt_to_a = e2e.comp_b.os.create_packet(app_b, dest_a, b"ICMPPing")
        resp_from_a = e2e.comp_b.os.syscall.request_blocking(app_b, pkt_to_a, timeout_secs=5)

        assert resp_from_a is not None
        assert resp_from_a.message == b"ICMPPong"


# ---------------------------------------------------------------------------
# E2E: service with custom application logic
# ---------------------------------------------------------------------------

class TestApplicationService:
    def test_echo_service_returns_payload(self, local):
        """A service that echoes back the received message body."""
        server_app = StubApp("echo_server")

        def echo_handler(pkt: Packet) -> bytes | None:
            return pkt.message

        local.comp_b.os.syscall.bind(server_app, 7000, echo_handler)

        client_app = StubApp("client")
        adapter_b = local.comp_b.network_adaptor_base
        dest = SocketAddr(adapter_b.ip_address, 7000)
        pkt = local.comp_a.os.create_packet(client_app, dest, b"hello world")

        response = local.comp_a.os.syscall.request_blocking(client_app, pkt, timeout_secs=5)

        assert response is not None
        assert response.message == b"hello world"

    def test_counter_service_tracks_state(self, local):
        """A stateful service that counts how many requests it has handled."""
        server_app = StubApp("counter")
        counter = [0]

        def counter_handler(pkt: Packet) -> bytes | None:
            counter[0] += 1
            return str(counter[0]).encode()

        local.comp_b.os.syscall.bind(server_app, 7000, counter_handler)

        client_app = StubApp("client")
        adapter_b = local.comp_b.network_adaptor_base
        dest = SocketAddr(adapter_b.ip_address, 7000)

        for expected in range(1, 4):
            pkt = local.comp_a.os.create_packet(client_app, dest, b"increment")
            response = local.comp_a.os.syscall.request_blocking(client_app, pkt, timeout_secs=5)
            assert response is not None
            assert response.message == str(expected).encode()

    def test_key_value_store_service(self, local):
        """A service that acts as a simple key-value store over the network."""
        server_app = StubApp("kv_store")
        store = {}

        def kv_handler(pkt: Packet) -> bytes | None:
            msg = pkt.message.decode()
            if msg.startswith("SET:"):
                # SET:key:value
                _, key, value = msg.split(":", 2)
                store[key] = value
                return b"OK"
            elif msg.startswith("GET:"):
                key = msg.split(":", 1)[1]
                return store.get(key, "NOT_FOUND").encode()
            return None

        local.comp_b.os.syscall.bind(server_app, 7000, kv_handler)

        client_app = StubApp("client")
        adapter_b = local.comp_b.network_adaptor_base
        dest = SocketAddr(adapter_b.ip_address, 7000)

        # SET
        set_pkt = local.comp_a.os.create_packet(client_app, dest, b"SET:name:hacknet")
        set_resp = local.comp_a.os.syscall.request_blocking(client_app, set_pkt, timeout_secs=5)
        assert set_resp is not None
        assert set_resp.message == b"OK"

        # GET
        get_pkt = local.comp_a.os.create_packet(client_app, dest, b"GET:name")
        get_resp = local.comp_a.os.syscall.request_blocking(client_app, get_pkt, timeout_secs=5)
        assert get_resp is not None
        assert get_resp.message == b"hacknet"

        # GET missing key
        miss_pkt = local.comp_a.os.create_packet(client_app, dest, b"GET:missing")
        miss_resp = local.comp_a.os.syscall.request_blocking(client_app, miss_pkt, timeout_secs=5)
        assert miss_resp is not None
        assert miss_resp.message == b"NOT_FOUND"


# ---------------------------------------------------------------------------
# E2E: NAT timeout through OS layer
# ---------------------------------------------------------------------------

class TestNATTimeoutE2E:
    def test_response_within_nat_window(self, e2e):
        """Response arriving before NAT expires is delivered to the OS."""
        server_app = StubApp("server")
        e2e.comp_b.os.syscall.bind(server_app, 9000, lambda pkt: b"ICMPPong")
        adapter_b = e2e.comp_b.network_adaptor_base
        e2e.home_b.forward(9000, SocketAddr(adapter_b.ip_address, 9000))

        # Small time advance, well within 5-minute NAT window
        game_timer.delta_time(10)

        client_app = StubApp("client")
        dest = SocketAddr(e2e.home_b.ip_address, 9000)
        pkt = e2e.comp_a.os.create_packet(client_app, dest, b"ICMPPing")
        response = e2e.comp_a.os.syscall.request_blocking(client_app, pkt, timeout_secs=5)

        assert response is not None
        assert response.message == b"ICMPPong"


# ---------------------------------------------------------------------------
# E2E: forbidden range through OS
# ---------------------------------------------------------------------------

class TestForbiddenRangeE2E:
    def test_home_computer_to_business_range_blocked(self, e2e):
        """A home computer sending to a 10.x.x.x address gets MAGICWrong Configuration."""
        app = StubApp()
        dest = SocketAddr(IPv4Addr(10, 50, 50, 50), 80)
        pkt = e2e.comp_a.os.create_packet(app, dest, b"ICMPPing")

        response = e2e.comp_a.os.syscall.request_blocking(app, pkt, timeout_secs=5)

        assert response is not None
        assert b"MAGICWrong Configuration" in response.message

    def test_business_computer_to_home_range_blocked(self, biz):
        """A business computer sending to a 192.168.x.x address gets MAGICWrong Configuration."""
        app = StubApp()
        dest = SocketAddr(IPv4Addr(192, 168, 50, 50), 80)
        pkt = biz.comp.os.create_packet(app, dest, b"ICMPPing")

        response = biz.comp.os.syscall.request_blocking(app, pkt, timeout_secs=5)

        assert response is not None
        assert b"MAGICWrong Configuration" in response.message


# ---------------------------------------------------------------------------
# E2E: reconnect computer to different router mid-session
# ---------------------------------------------------------------------------

class TestReconnectE2E:
    def test_computer_works_after_switching_routers(self, e2e):
        """Computer can send packets after disconnecting and reconnecting to a new router."""
        adapter = e2e.comp_a.network_adaptor_base

        adapter.disconnect()
        adapter.connect(e2e.home_b, 'beta')

        app = StubApp()
        dest = SocketAddr(e2e.home_b.PRIVATE_IP, 80)
        pkt = e2e.comp_a.os.create_packet(app, dest, b"ICMPPing")

        response = e2e.comp_a.os.syscall.request_blocking(app, pkt, timeout_secs=5)

        assert response is not None
        assert response.message == b"ICMPPong"

    def test_service_survives_reconnect_same_router(self, local):
        """Listener persists on adapter after disconnect/reconnect to same router."""
        server_app = StubApp("server")
        local.comp_b.os.syscall.bind(server_app, 9000, lambda pkt: b"ICMPPong")

        adapter_b = local.comp_b.network_adaptor_base
        adapter_b.disconnect()
        adapter_b.connect(local.home, 'pass')

        # Listener is still registered on adapter.listeners
        assert 9000 in adapter_b.listeners

        client_app = StubApp("client")
        dest = SocketAddr(adapter_b.ip_address, 9000)
        pkt = local.comp_a.os.create_packet(client_app, dest, b"ICMPPing")

        response = local.comp_a.os.syscall.request_blocking(client_app, pkt, timeout_secs=5)

        assert response is not None
        assert response.message == b"ICMPPong"


# ---------------------------------------------------------------------------
# E2E: multiple services on one computer
# ---------------------------------------------------------------------------

class TestMultipleServices:
    def test_two_services_on_different_ports(self, local):
        """Two services on the same computer respond independently."""
        app_echo = StubApp("echo")
        app_upper = StubApp("upper")

        local.comp_b.os.syscall.bind(app_echo, 7000, lambda pkt: pkt.message)
        local.comp_b.os.syscall.bind(app_upper, 7001, lambda pkt: pkt.message.upper())

        client = StubApp("client")
        adapter_b = local.comp_b.network_adaptor_base

        echo_dest = SocketAddr(adapter_b.ip_address, 7000)
        echo_pkt = local.comp_a.os.create_packet(client, echo_dest, b"hello")
        echo_resp = local.comp_a.os.syscall.request_blocking(client, echo_pkt, timeout_secs=5)
        assert echo_resp is not None
        assert echo_resp.message == b"hello"

        upper_dest = SocketAddr(adapter_b.ip_address, 7001)
        upper_pkt = local.comp_a.os.create_packet(client, upper_dest, b"hello")
        upper_resp = local.comp_a.os.syscall.request_blocking(client, upper_pkt, timeout_secs=5)
        assert upper_resp is not None
        assert upper_resp.message == b"HELLO"


# ---------------------------------------------------------------------------
# E2E: NAT timeout expiry — response dropped after window
# ---------------------------------------------------------------------------

class TestNATTimeoutExpiry:
    def test_nat_expired_response_dropped(self, e2e):
        """Response arriving after NAT expires never reaches the sender."""
        # Bind a listener on comp_b but DON'T use blocking request —
        # we need manual control over timing between send and response.
        received_by_b = []

        def capture_handler(pkt: Packet) -> bytes | None:
            received_by_b.append(pkt)
            # Don't respond immediately — we'll send the response manually
            return None

        adapter_b = e2e.comp_b.network_adaptor_base
        adapter_b.listeners[9000] = capture_handler
        e2e.home_b.forward(9000, SocketAddr(adapter_b.ip_address, 9000))

        # Send a request from comp_a (directly through adapter, not OS blocking)
        adapter_a = e2e.comp_a.network_adaptor_base
        pkt = Packet(
            source=SocketAddr(adapter_a.ip_address, 5000),
            dest=SocketAddr(e2e.home_b.ip_address, 9000),
            message=b"ICMPPing",
            response=False,
        )
        e2e.home_a.send_packet(pkt)

        assert len(received_by_b) == 1
        # The source was rewritten by NAT — capture it for the response
        nat_source = received_by_b[0].source

        # Advance game time past the 5-minute NAT window
        game_timer.delta_time(300 * 1000)

        # Now send response back using the NAT address
        response_pkt = Packet(
            source=SocketAddr(adapter_b.ip_address, 9000),
            dest=nat_source,
            message=b"ICMPPong",
            response=True,
        )
        e2e.home_b.send_packet(response_pkt)

        # Response should NOT reach comp_a — NAT entry expired
        assert len(adapter_a.buffer) == 0


# ---------------------------------------------------------------------------
# E2E: multiple async requests in flight
# ---------------------------------------------------------------------------

class TestMultipleAsyncInFlight:
    def test_three_async_requests_all_polled(self, local):
        """Three async requests to different services, all responses collected via poll."""
        server_app_a = StubApp("svc_a")
        server_app_b = StubApp("svc_b")
        server_app_c = StubApp("svc_c")

        local.comp_b.os.syscall.bind(server_app_a, 7000, lambda pkt: b"resp_a")
        local.comp_b.os.syscall.bind(server_app_b, 7001, lambda pkt: b"resp_b")
        local.comp_b.os.syscall.bind(server_app_c, 7002, lambda pkt: b"resp_c")

        client = StubApp("client")
        adapter_b = local.comp_b.network_adaptor_base

        for port in (7000, 7001, 7002):
            dest = SocketAddr(adapter_b.ip_address, port)
            pkt = local.comp_a.os.create_packet(client, dest, b"ICMPPing")
            local.comp_a.os.syscall.request_async(client, pkt, timeout_secs=5)

        # Wait for all three background threads to complete
        time.sleep(1.0)

        packets = local.comp_a.os.syscall.poll(client)
        assert packets is not None
        assert len(packets) == 3
        messages = {p.message for p in packets}
        assert messages == {b"resp_a", b"resp_b", b"resp_c"}


# ---------------------------------------------------------------------------
# E2E: disconnected adapter
# ---------------------------------------------------------------------------

class TestDisconnectedAdapter:
    def test_send_on_disconnected_adapter_asserts(self, local):
        """Sending a packet through a disconnected adapter raises AssertionError."""
        adapter = local.comp_a.network_adaptor_base
        ip_before = adapter.ip_address
        adapter.disconnect()

        pkt = Packet(
            source=SocketAddr(ip_before, 5000),
            dest=SocketAddr(IPv4Addr(8, 8, 8, 8), 80),
            message=b"ICMPPing",
            response=False,
        )
        with pytest.raises(AssertionError):
            adapter.send_packet(pkt)


# ---------------------------------------------------------------------------
# E2E: OS syscalls on powered-off computer
# ---------------------------------------------------------------------------

class TestSyscallsWhenOff:
    def test_create_packet_when_off_raises(self, local):
        """create_packet on a powered-off computer raises ComputerSwitchedOff."""
        local.comp_a.switch_off()
        app = StubApp()
        dest = SocketAddr(IPv4Addr(8, 8, 8, 8), 80)

        with pytest.raises(ComputerSwitchedOff):
            local.comp_a.os.create_packet(app, dest, b"ICMPPing")

    def test_bind_when_off_raises(self, local):
        """syscall.bind on a powered-off computer raises ComputerSwitchedOff."""
        local.comp_a.switch_off()
        app = StubApp()

        with pytest.raises(ComputerSwitchedOff):
            local.comp_a.os.syscall.bind(app, 8080, lambda pkt: None)

    def test_blocking_request_when_off_raises(self, local):
        """syscall.request_blocking on a powered-off computer raises ComputerSwitchedOff."""
        app = StubApp()
        dest = SocketAddr(local.home.PRIVATE_IP, 80)
        # Create packet while on
        pkt = local.comp_a.os.create_packet(app, dest, b"ICMPPing")

        local.comp_a.switch_off()

        with pytest.raises(ComputerSwitchedOff):
            local.comp_a.os.syscall.request_blocking(app, pkt, timeout_secs=5)


# ---------------------------------------------------------------------------
# E2E: port forward exists but service was unbound
# ---------------------------------------------------------------------------

class TestPortForwardWithoutListener:
    def test_request_to_forwarded_port_after_unbind(self, e2e):
        """Port forward routes to comp_b, but listener was unbound — no response from adapter."""
        server_app = StubApp("server")
        e2e.comp_b.os.syscall.bind(server_app, 9000, lambda pkt: b"ICMPPong")

        adapter_b = e2e.comp_b.network_adaptor_base
        e2e.home_b.forward(9000, SocketAddr(adapter_b.ip_address, 9000))

        # Unbind the service
        e2e.comp_b.os.syscall.unbind(server_app, 9000)

        client_app = StubApp("client")
        dest = SocketAddr(e2e.home_b.ip_address, 9000)
        pkt = e2e.comp_a.os.create_packet(client_app, dest, b"ICMPPing")

        # Packet reaches adapter but no listener — no response generated.
        # Blocking request should time out.
        advance_timer_in_background(delay_real=0.3, game_secs=10)
        response = e2e.comp_a.os.syscall.request_blocking(client_app, pkt, timeout_secs=5)

        assert response is None
