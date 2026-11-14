from datetime import datetime, timedelta
import unittest

from services.monitor import Monitor
from services.simulator import generate_measurements

class SimulatorTests(unittest.TestCase):
    def setUp(self):
        self.start = datetime(2026, 11, 13, 8)

    def test_generates_requested_count_interval_and_temperature_range(self):
        measurements = generate_measurements(
            self.start,
            4,
            interval=timedelta(minutes=5),
            minimum_temperature=20,
            maximum_temperature=30,
            seed=42,
        )
        self.assertEqual(
            [timestamp for timestamp, _ in measurements],
            [self.start + timedelta(minutes=5 * index) for index in range(4)],
        )
        self.assertTrue(all(20 <= temperature <= 30 for _, temperature in measurements))

    def test_seed_makes_generation_reproducible(self):
        first = generate_measurements(self.start, 5, seed=21)
        second = generate_measurements(self.start, 5, seed=21)
        self.assertEqual(first, second)

    def test_generated_measurements_can_be_added_to_monitor(self):
        monitor = Monitor()
        readings = monitor.add_readings(generate_measurements(self.start, 10, seed=21))
        self.assertEqual(len(readings), 10)
        self.assertEqual(len(monitor), 10)
        self.assertEqual([reading.reading_id for reading in readings], list(range(1, 11)))

    def test_rejects_invalid_parameters(self):
        invalid_arguments = (
            {"count": -1},
            {"count": True},
            {"count": 1, "interval": timedelta(0)},
            {"count": 1, "minimum_temperature": 30, "maximum_temperature": 20},
            {"count": 1, "minimum_temperature": float("nan")},
        )
        for arguments in invalid_arguments:
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                generate_measurements(self.start, **arguments)
