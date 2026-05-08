from typing import Callable, TypeAlias


type Pointer[T] = Callable[[], T]