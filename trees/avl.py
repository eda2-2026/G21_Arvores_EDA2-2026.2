from collections.abc import Callable
from typing import Generic, TypeVar

T = TypeVar("T")
K = TypeVar("K")

class AVLTree(Generic[T, K]):
    def __init__(self, key: Callable[[T], K]) -> None:
        self._key = key

    def insert(self, value: T) -> None:
        raise NotImplementedError

    def search(self, key: K) -> T | None:
        raise NotImplementedError

    def range_search(self, start: K | None = None, end: K | None = None) -> list[T]:
        raise NotImplementedError

    def in_order(self) -> list[T]:
        raise NotImplementedError
