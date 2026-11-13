from datetime import datetime, timedelta, timezone
from math import ceil, log2
from random import Random
import unittest
from unittest.mock import patch

from models.reading import Reading, temperature_key, time_key
from services.monitor import Monitor
from tests.test_avl import assert_avl
from trees.avl import AVLTree

class MonitorTests(unittest.TestCase):
    def setUp(self):
        self.monitor = Monitor()
        self.now = datetime(2026, 11, 12, 10, 30)

    def test_same_objects_are_stored_in_independent_indices(self):
        first = self.monitor.add_reading(self.now, 31.5)
        second = self.monitor.add_reading(self.now - timedelta(hours=1), 35)
        chronological = self.monitor.chronological_readings()
        thermal = self.monitor.temperature_readings()
        self.assertEqual(chronological, [second, first])
        self.assertEqual(thermal, [first, second])
        self.assertIs(chronological[1], thermal[0])
        self.assertIsNot(self.monitor._time_index._root, self.monitor._temperature_index._root)

    def test_identical_timestamps_and_temperatures_are_preserved(self):
        readings = [self.monitor.add_reading(self.now, 30) for _ in range(10)]
        self.assertEqual([r.reading_id for r in readings], list(range(1, 11)))
        self.assertEqual(self.monitor.chronological_readings(), readings)
        self.assertEqual(self.monitor.temperature_readings(), readings)
        self.assertEqual(self.monitor.readings_between(self.now, self.now), readings)
        self.assertEqual(self.monitor.readings_above(30), [])
        self.assertEqual(self.monitor.readings_above(29), readings)

    def test_date_interval_includes_both_boundaries_across_days(self):
        readings = self.monitor.add_readings(
            (self.now + timedelta(days=day), 25 + day) for day in range(4)
        )
        self.assertEqual(
            self.monitor.readings_between(readings[1].timestamp, readings[2].timestamp),
            readings[1:3],
        )
        self.assertEqual(self.monitor.readings_between(datetime.min, self.now - timedelta(seconds=1)), [])
        with self.assertRaises(ValueError):
            self.monitor.readings_between(readings[2].timestamp, readings[1].timestamp)

    def test_temperature_threshold_is_strict_and_sorted(self):
        readings = self.monitor.add_readings(
            [(self.now, 31), (self.now, 30), (self.now, -5), (datetime.max, 30)]
        )
        self.assertEqual(self.monitor.readings_above(30), [readings[0]])
        self.assertEqual(self.monitor.readings_above(-10), sorted(readings, key=temperature_key))
        self.assertEqual(self.monitor.readings_above(100), [])

    def test_empty_monitor(self):
        self.assertEqual(len(self.monitor), 0)
        self.assertEqual(self.monitor.time_height, 0)
        self.assertEqual(self.monitor.temperature_height, 0)
        self.assertEqual(self.monitor.readings_above(30), [])
        self.assertEqual(self.monitor.readings_between(datetime.min, datetime.max), [])
        self.assertEqual(self.monitor.add_readings([]), [])

    def test_invalid_readings_are_rejected_before_changing_indices(self):
        for timestamp, temperature in (
            (self.now, float("nan")), (self.now, float("inf")),
            (self.now, -float("inf")), (self.now, True), (self.now, "30"),
            (self.now, 10 ** 1000), ("2026-11-12", 30),
            (self.now.replace(tzinfo=timezone.utc), 30),
        ):
            with self.subTest(timestamp=timestamp, temperature=temperature):
                with self.assertRaises(ValueError):
                    self.monitor.add_reading(timestamp, temperature)
                self.assertEqual(len(self.monitor), 0)
                self.assertEqual(self.monitor.temperature_readings(), [])
        self.assertEqual(self.monitor.add_reading(self.now, 30).reading_id, 1)

    def test_invalid_query_bounds(self):
        for limit in (float("nan"), float("inf"), True, "30"):
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                self.monitor.readings_above(limit)
        with self.assertRaises(ValueError):
            self.monitor.readings_between(self.now, self.now.replace(tzinfo=timezone.utc))

    def test_batch_is_atomic_when_a_later_reading_is_invalid(self):
        previous = self.monitor.add_reading(self.now, 25)
        with self.assertRaises(ValueError):
            self.monitor.add_readings([(self.now, 31), (self.now, float("nan"))])
        self.assertEqual(self.monitor.chronological_readings(), [previous])
        self.assertEqual(self.monitor.temperature_readings(), [previous])
        self.assertEqual(self.monitor.add_reading(self.now, 35).reading_id, 2)

    def test_second_index_failure_does_not_commit_first_index(self):
        previous = self.monitor.add_reading(self.now, 25)
        original_insert = AVLTree.insert

        def fail_temperature_index(tree, value):
            if tree._key is temperature_key:
                raise RuntimeError("Falha simulada no segundo índice")
            original_insert(tree, value)

        with patch.object(AVLTree, "insert", fail_temperature_index):
            with self.assertRaises(RuntimeError):
                self.monitor.add_reading(self.now, 35)
        self.assertEqual(self.monitor.chronological_readings(), [previous])
        self.assertEqual(self.monitor.temperature_readings(), [previous])
        self.assertEqual(self.monitor.add_reading(self.now, 35).reading_id, 2)

    def test_volume_and_queries_match_a_reference_list(self):
        random = Random(42)
        readings = self.monitor.add_readings(
            (self.now + timedelta(minutes=random.randrange(100)), random.randrange(-5, 45))
            for _ in range(1000)
        )
        self.assertEqual(self.monitor.chronological_readings(), sorted(readings, key=time_key))
        self.assertEqual(self.monitor.temperature_readings(), sorted(readings, key=temperature_key))
        start, end = self.now + timedelta(minutes=20), self.now + timedelta(minutes=40)
        expected = sorted([r for r in readings if start <= r.timestamp <= end], key=time_key)
        self.assertEqual(self.monitor.readings_between(start, end), expected)
        expected = sorted([r for r in readings if r.temperature > 30], key=temperature_key)
        self.assertEqual(self.monitor.readings_above(30), expected)
        self.assertEqual(len(self.monitor), 1000)
        for tree in (self.monitor._time_index, self.monitor._temperature_index):
            assert_avl(self, tree)
            self.assertLessEqual(tree.height, ceil(1.45 * log2(1002)))

    def test_reading_rejects_invalid_identifiers(self):
        for reading_id in (0, -1, True, 1.5):
            with self.subTest(reading_id=reading_id), self.assertRaises(ValueError):
                Reading(reading_id, self.now, 30)
