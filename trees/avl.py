from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")
K = TypeVar("K")

@dataclass
class _Node(Generic[T]):
    value: T
    left: _Node[T] | None = None
    right: _Node[T] | None = None
    height: int = 1

class AVLTree(Generic[T, K]):
    def __init__(self, key: Callable[[T], K]) -> None:
        self._key = key
        self._root: _Node[T] | None = None

    @staticmethod
    def _node_height(node: _Node[T] | None) -> int:
        return node.height if node is not None else 0

    def _update_height(self, node: _Node[T]) -> None:
        node.height = 1 + max(
            self._node_height(node.left),
            self._node_height(node.right),
        )

    def _balance_factor(self, node: _Node[T]) -> int:
        return self._node_height(node.left) - self._node_height(node.right)

    @property
    def height(self) -> int:
        return self._node_height(self._root)

    def insert(self, value: T) -> None:
        raise NotImplementedError

    def search(self, key: K) -> T | None:
        raise NotImplementedError

    def range_search(self, start: K | None = None, end: K | None = None) -> list[T]:
        raise NotImplementedError

    def in_order(self) -> list[T]:
        raise NotImplementedError
