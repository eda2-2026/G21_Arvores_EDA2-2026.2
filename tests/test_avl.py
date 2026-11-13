from copy import copy
from math import ceil, log2
from random import Random
import unittest

from trees.avl import AVLTree


def assert_avl(test: unittest.TestCase, tree: AVLTree) -> None:
    """Verifica ordenação, alturas armazenadas e balanceamento de todos os nós."""
    def visit(node, lower=None, upper=None):
        if node is None:
            return 0, 0
        key = tree._key(node.value)
        if lower is not None:
            test.assertGreater(key, lower)
        if upper is not None:
            test.assertLess(key, upper)
        left_height, left_size = visit(node.left, lower, key)
        right_height, right_size = visit(node.right, key, upper)
        test.assertLessEqual(abs(left_height - right_height), 1)
        height = 1 + max(left_height, right_height)
        test.assertEqual(node.height, height)
        return height, 1 + left_size + right_size

    height, size = visit(tree._root)
    test.assertEqual(tree.height, height)
    test.assertEqual(len(tree), size)


class AVLTests(unittest.TestCase):
    def test_four_rotation_cases(self):
        cases = (
            ([30, 20, 10], 1),
            ([10, 20, 30], 1),
            ([30, 10, 20], 2),
            ([10, 30, 20], 2),
        )
        for values, expected_rotations in cases:
            with self.subTest(values=values):
                tree = AVLTree(key=lambda value: value)
                for value in values:
                    tree.insert(value)
                    assert_avl(self, tree)
                self.assertEqual(tree._root.value, 20)
                self.assertEqual(tree.in_order(), [10, 20, 30])
                self.assertEqual(tree.height, 2)
                self.assertEqual(tree.rotation_count, expected_rotations)

    def test_ordered_reverse_and_random_insertions_at_volume(self):
        for size in (100, 1000):
            random_values = list(range(size))
            Random(42).shuffle(random_values)
            for values in (list(range(size)), list(reversed(range(size))), random_values):
                with self.subTest(size=size, first=values[:3]):
                    tree = AVLTree(key=lambda value: value)
                    for value in values:
                        tree.insert(value)
                    assert_avl(self, tree)
                    self.assertEqual(tree.in_order(), list(range(size)))
                    self.assertLessEqual(tree.height, ceil(1.45 * log2(size + 2)))
                    self.assertEqual(tree.search(size // 2), size // 2)

    def test_empty_tree(self):
        tree = AVLTree(key=lambda value: value)
        self.assertEqual(len(tree), 0)
        self.assertEqual(tree.height, 0)
        self.assertEqual(tree.rotation_count, 0)
        self.assertIsNone(tree.search(1))
        self.assertEqual(tree.in_order(), [])
        self.assertEqual(tree.range_search(1, 2), [])

    def test_duplicate_key_does_not_change_tree(self):
        tree = AVLTree(key=lambda value: value)
        for value in (3, 1, 2, 4):
            tree.insert(value)
        root = tree._root
        with self.assertRaises(ValueError):
            tree.insert(2)
        self.assertIs(tree._root, root)
        self.assertEqual(tree.in_order(), [1, 2, 3, 4])
        assert_avl(self, tree)

    def test_search_returns_value_not_key(self):
        tree = AVLTree(key=lambda value: value[0])
        for value in ((2, "dois"), (1, "um"), (3, "três")):
            tree.insert(value)
        self.assertEqual(tree.search(2), (2, "dois"))
        self.assertIsNone(tree.search(99))

    def test_inclusive_and_open_ranges(self):
        tree = AVLTree(key=lambda value: value)
        for value in (5, 1, 9, 3, 7):
            tree.insert(value)
        for start, end, expected in (
            (3, 7, [3, 5, 7]), (5, 5, [5]), (None, 3, [1, 3]),
            (7, None, [7, 9]), (10, 20, []), (4, 4, []),
            (None, None, [1, 3, 5, 7, 9]),
        ):
            with self.subTest(start=start, end=end):
                self.assertEqual(tree.range_search(start, end), expected)
        with self.assertRaises(ValueError):
            tree.range_search(7, 3)

    def test_queries_prune_irrelevant_subtrees(self):
        calls = 0

        def key(value):
            nonlocal calls
            calls += 1
            return value

        tree = AVLTree(key=key)
        for value in range(4095):
            tree.insert(value)
        calls = 0
        self.assertEqual(tree.range_search(4000, 4002), [4000, 4001, 4002])
        self.assertLess(calls, 50)
        calls = 0
        self.assertEqual(tree.search(4000), 4000)
        self.assertLessEqual(calls, tree.height)

    def test_shallow_copies_can_be_updated_independently(self):
        tree = AVLTree(key=lambda value: value)
        for value in range(20):
            tree.insert(value)
        other = copy(tree)
        other.insert(20)
        tree.insert(-1)
        self.assertEqual(tree.in_order(), list(range(-1, 20)))
        self.assertEqual(other.in_order(), list(range(21)))
        assert_avl(self, tree)
        assert_avl(self, other)
