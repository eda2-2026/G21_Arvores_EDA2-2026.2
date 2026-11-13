import csv
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from services.importer import import_csv
from services.monitor import Monitor
from tests.test_avl import assert_avl

class CSVTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "leituras.csv"
        self.monitor = Monitor()
        self.now = datetime(2026, 11, 12, 10, 30)

    def write_csv(self, text):
        self.path.write_text(text, encoding="utf-8")

    def test_import_preserves_duplicates_and_accepts_utf8_bom(self):
        self.write_csv(
            "\ufeffdata_hora,temperatura\n"
            "2026-11-12 10:30:00,31.5\n"
            "2026-11-12 10:30:00,31.5\n"
        )
        self.assertEqual(import_csv(self.path, self.monitor), 2)
        self.assertEqual(len(self.monitor), 2)
        self.assertEqual(len(self.monitor.readings_above(30)), 2)
        self.assertEqual(self.monitor.chronological_readings(), self.monitor.temperature_readings())

    def test_bad_headers(self):
        for header in ("", "timestamp,temperature", "temperatura,data_hora", "data_hora,temperatura,id"):
            with self.subTest(header=header):
                self.write_csv(header + "\n")
                with self.assertRaisesRegex(ValueError, "cabeçalho"):
                    import_csv(self.path, self.monitor)

    def test_header_without_readings(self):
        self.write_csv("data_hora,temperatura\n")
        self.assertEqual(import_csv(self.path, self.monitor), 0)
        self.assertEqual(len(self.monitor), 0)

    def test_malformed_quoted_header_is_reported_as_validation_error(self):
        self.write_csv('"data_hora,temperatura\n')
        with self.assertRaisesRegex(ValueError, "Cabeçalho CSV inválido"):
            import_csv(self.path, self.monitor)
        self.assertEqual(len(self.monitor), 0)

    def test_invalid_later_row_preserves_existing_data_and_ids(self):
        previous = self.monitor.add_reading(self.now, 20)
        for row in (
            "data-inválida,25", "2026-11-12 10:30:00,abc",
            "2026-11-12 10:30:00,nan", "2026-11-12 10:30:00,inf",
            "2026-11-12 10:30:00", "2026-11-12 10:30:00,25,extra",
            '"2026-11-12 10:30:00,25',
        ):
            with self.subTest(row=row):
                self.write_csv("data_hora,temperatura\n2026-11-12 11:00:00,31\n" + row + "\n")
                with self.assertRaisesRegex(ValueError, "Linha"):
                    import_csv(self.path, self.monitor)
                self.assertEqual(self.monitor.chronological_readings(), [previous])
                self.assertEqual(self.monitor.temperature_readings(), [previous])
        self.assertEqual(self.monitor.add_reading(self.now, 30).reading_id, 2)

    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            import_csv(self.path, self.monitor)
        self.assertEqual(len(self.monitor), 0)

    def test_invalid_encoding_does_not_commit_partial_import(self):
        self.path.write_bytes(b"data_hora,temperatura\n2026-11-12 10:30:00,25\n\xff")
        with self.assertRaises(UnicodeError):
            import_csv(self.path, self.monitor)
        self.assertEqual(len(self.monitor), 0)

    def test_csv_files_with_100_and_1000_readings(self):
        for size in (100, 1000):
            with self.subTest(size=size):
                monitor = Monitor()
                with self.path.open("w", encoding="utf-8", newline="") as output:
                    writer = csv.writer(output)
                    writer.writerow(["data_hora", "temperatura"])
                    for index in range(size):
                        writer.writerow([self.now + timedelta(minutes=index), 20 + index % 20])
                self.assertEqual(import_csv(self.path, monitor), size)
                self.assertEqual(len(monitor), size)
                self.assertEqual(len(monitor.readings_above(30)), size // 20 * 9)
                assert_avl(self, monitor._time_index)
                assert_avl(self, monitor._temperature_index)
