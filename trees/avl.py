from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")
K = TypeVar("K")


@dataclass(frozen=True)
class _Node(Generic[T]):
    value: T
    left: _Node[T] | None = None
    right: _Node[T] | None = None
    height: int = 1


class AVLTree(Generic[T, K]):
    """AVL genérica com chaves únicas e consultas por intervalo inclusivo.

    Os nós são imutáveis: uma inserção recria apenas o caminho até a folha.
    Assim, copy.copy(tree) compartilha os nós com segurança até novas inserções,
    permitindo preparar atualizações de dois índices antes de publicá-las.
    """

    def __init__(self, key: Callable[[T], K]) -> None:
        self._key = key
        self._root: _Node[T] | None = None
        self._size = 0

    @staticmethod
    def _node_height(node: _Node[T] | None) -> int:
        return node.height if node is not None else 0

    def _make_node(
        self, value: T, left: _Node[T] | None, right: _Node[T] | None
    ) -> _Node[T]:
        return _Node(
            value, left, right,
            1 + max(self._node_height(left), self._node_height(right)),
        )

    def _balance_factor(self, node: _Node[T]) -> int:
        return self._node_height(node.left) - self._node_height(node.right)

    def _rotate_left(self, node: _Node[T]) -> _Node[T]:
        pivot = node.right
        assert pivot is not None
        left = self._make_node(node.value, node.left, pivot.left)
        return self._make_node(pivot.value, left, pivot.right)

    def _rotate_right(self, node: _Node[T]) -> _Node[T]:
        pivot = node.left
        assert pivot is not None
        right = self._make_node(node.value, pivot.right, node.right)
        return self._make_node(pivot.value, pivot.left, right)

    def _rebalance(self, node: _Node[T]) -> _Node[T]:
        balance = self._balance_factor(node)
        if balance > 1:
            assert node.left is not None
            if self._balance_factor(node.left) < 0:  # LR
                node = self._make_node(
                    node.value, self._rotate_left(node.left), node.right
                )
            return self._rotate_right(node)  # LL
        if balance < -1:
            assert node.right is not None
            if self._balance_factor(node.right) > 0:  # RL
                node = self._make_node(
                    node.value, node.left, self._rotate_right(node.right)
                )
            return self._rotate_left(node)  # RR
        return node

    def _insert(self, node: _Node[T] | None, value: T) -> _Node[T]:
        if node is None:
            return _Node(value)
        value_key = self._key(value)
        node_key = self._key(node.value)
        if value_key < node_key:
            node = self._make_node(
                node.value, self._insert(node.left, value), node.right
            )
        elif value_key > node_key:
            node = self._make_node(
                node.value, node.left, self._insert(node.right, value)
            )
        else:
            raise ValueError("Duplicate keys are not allowed")
        return self._rebalance(node)

    def __len__(self) -> int:
        return self._size

    @property
    def height(self) -> int:
        return self._node_height(self._root)

    def insert(self, value: T) -> None:
        self._root = self._insert(self._root, value)
        self._size += 1

    def search(self, key: K) -> T | None:
        node = self._root
        while node is not None:
            node_key = self._key(node.value)
            if key < node_key:
                node = node.left
            elif key > node_key:
                node = node.right
            else:
                return node.value
        return None

    def range_search(self, start: K | None = None, end: K | None = None) -> list[T]:
        """Retorna valores ordenados em [start, end], em O(log n + k)."""
        if start is not None and end is not None and start > end:
            raise ValueError("O início do intervalo deve ser menor ou igual ao fim")
        result: list[T] = []

        def visit(node: _Node[T] | None) -> None:
            if node is None:
                return
            key = self._key(node.value)
            if start is None or key > start:
                visit(node.left)
            if (start is None or key >= start) and (end is None or key <= end):
                result.append(node.value)
            if end is None or key < end:
                visit(node.right)

        visit(self._root)
        return result

    def in_order(self) -> list[T]:
        return self.range_search()
