from __future__ import annotations
from typing import TYPE_CHECKING
from enum import Enum
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from typing import TypeAlias, List, Optional, Tuple
    from node import Computer

import random

Node: TypeAlias = 'Router' | 'Computer'
ConsumerRouters: TypeAlias = 'HomeRouter' | 'BusinessRouter'

IPv4Addr: TypeAlias = Tuple[int, int, int, int]
CIDR: TypeAlias = Tuple[IPv4Addr, int]


class Router(ABC):
    def __init__(self, parent: Optional[Router], children: List[Node] = None, enabled: bool = True) -> None:
        self.parent: Router | None = parent

        if self.parent:
            self.parent.children.append(self)

        self.children = children or []
        
        for child in self.children:
            child.parent = self
            child.disable()
            child.enable()

        self.enabled: bool = enabled

        self.ip_address: Optional[IPv4Addr] = self.assign_ip() if self.enabled else None

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
                if child.subrange and child.subrange[0][0] == current_subrange:
                    break
            else:
                return ((current_subrange, 0, 0, 0), 8)
    
    def assign_ip(self) -> IPv4Addr:
        return (0,1,1,0)

    def domain_range(self) -> Optional[CIDR]:
        return (self.ip_address,0) if self.enabled else None
    
    def enable(self) -> None:
        assert False, 'Internet Router cannot be enabled.'

    def disable(self) -> None:
        assert False, 'Internet Router cannot be disabled.'


class ISPRouter(Router):
    def __init__(self, parent: InternetRouter, children: List[ConsumerRouters] = None, enabled: bool = True):
        assert parent or not enabled, "ISP routers cannot be turned on without a connection to the internet"
        children = children or []
        self.subrange: Optional[CIDR] = parent.request_subrange() if enabled else None
        super().__init__(parent, children, enabled)

    def assign_ip(self) -> IPv4Addr:
        assert self.enabled, "Router should be enabled"
        b = random.randint(0,255)
        c = random.randint(0,255)
        d = random.randint(0,255)
        return (self.subrange[0][0], b, c, d)

    def hand_ip(self) -> IPv4Addr:
        assert self.enabled, "Inactive ISP assigning address"
        assert len(self.children) < 2**20, "Too many nodes"
        while True:
            current_ip = (self.subrange[0][0], random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            if current_ip == self.ip_address: continue
            for child in self.children:
                if child.ip_address and child.ip_address == current_ip:
                    break
            else:
                return current_ip

    def domain_range(self) -> Optional[CIDR]:
        return self.subrange if self.enabled else None
    
    def enable(self) -> None:
        if self.enabled: return
        self.subrange = self.parent.request_subrange()
        super().enable()

    def disable(self) -> None:
        super().disable()
        self.subrange = None


class BusinessRouter(Router):
    PRIVATE_IP = (10, 0, 0, 1)
    def __init__(self, parent: ISPRouter, children : List[Computer | HomeRouter] = None, enabled: bool = True):
        assert parent or not enabled, "Consumers routers cannot be enabled without connection to an ISP"
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

    def assign_ip(self):
        return self.parent.hand_ip()

    def domain_range(self) -> Optional[CIDR]:
        return ((10,0,0,0), 8) if self.enabled else None


class HomeRouter(Router):
    PRIVATE_IP = (192, 168, 1, 1)
    def __init__(self, parent: ISPRouter | BusinessRouter, children : List[Computer] = None, enabled: bool = True):
        assert parent or not enabled, "Consumers routers cannot be enabled without connection to an ISP"
        children = children or []
        super().__init__(parent, children, enabled)

    def assign_ip(self):
        return self.parent.hand_ip()

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

    def domain_range(self) -> Optional[CIDR]:
        return ((192,168,0,0), 16) if self.enabled else None
