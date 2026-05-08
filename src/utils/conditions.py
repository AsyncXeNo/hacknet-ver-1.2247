from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, TypeAlias

from utils.types import Pointer

Leaf: TypeAlias = 'Pointer[Any] | Condition'


class LogicalOp(Enum):
    AND=0
    OR=1


class RelOp(Enum):
    EQ=0
    NEQ=1
    LT=2
    LEQ=3
    GT=4
    GEQ=5


class Condition(ABC):
    @abstractmethod
    def resolve(self) -> bool:
        pass


class LogicalCondition(Condition):
    def __init__(self, cond1: Condition, op: LogicalOp, cond2: Condition):
        self.cond1: Condition = cond1
        self.op: LogicalOp = op
        self.cond2: Condition = cond2

    def with_op(self, op: RelOp, var_cond: Leaf) -> RelationalCondition:
        return RelationalCondition(self, op, var_cond)

    def with_and(self, cond: Condition) -> LogicalCondition:
        return LogicalCondition(self, LogicalOp.AND, cond)
    
    def with_or(self, cond: Condition) -> LogicalCondition:
        return LogicalCondition(self, LogicalOp.OR, cond)

    def resolve(self) -> bool:
        match(self.op):
            case LogicalOp.AND:
                return self.cond1.resolve() and self.cond2.resolve()
            case LogicalOp.OR:
                return self.cond1.resolve() or self.cond2.resolve()


class RelationalCondition(Condition):
    def __init__(self, var1: Leaf, op: RelOp, var2: Leaf):
        self.var1: Leaf = var1
        self.op: RelOp = op
        self.var2: Leaf = var2

    def with_and(self, cond: Condition) -> LogicalCondition:
        return LogicalCondition(self, LogicalOp.AND, cond)
    
    def with_or(self, cond: Condition) -> LogicalCondition:
        return LogicalCondition(self, LogicalOp.OR, cond)

    def resolve(self) -> bool:
        val1 = (self.var1.resolve() 
            if isinstance(self.var1, Condition) 
            else self.var1()
        )
        val2 = (self.var2.resolve() 
            if isinstance(self.var2, Condition) 
            else self.var2()
        )

        match(self.op):
            case RelOp.EQ:
                return val1 == val2
            case RelOp.NEQ:
                return val1 != val2
            case RelOp.LT:
                return val1 < val2
            case RelOp.LEQ:
                return val1 <= val2
            case RelOp.GT:
                return val1 > val2
            case RelOp.GEQ:
                return val1 >= val2