from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from main import main, run_menu
from services.monitor import Monitor

class CLITests(unittest.TestCase):
    def run_session(self, inputs):
        monitor = Monitor()
        output = StringIO()
        with patch("builtins.input", side_effect=inputs), redirect_stdout(output):
            run_menu(monitor)
        return monitor, output.getvalue()

    def test_individual_insertion_queries_statistics_and_lists(self):
        monitor, output = self.run_session([
            "1", "2026-11-12 10:30:00", "31.5", "5", "6", "7",
            "3", "2026-11-12 10:30:00", "2026-11-12 10:30:00",
            "4", "30", "0",
        ])
        self.assertEqual(len(monitor), 1)
        self.assertIn("Leitura 1 inserida nos dois índices.", output)
        self.assertIn("Total de leituras: 1", output)
        self.assertIn("Altura da AVL por horário: 1", output)
        self.assertIn("Altura da AVL por temperatura: 1", output)
        self.assertIn("Rotações da AVL por horário: 0", output)
        self.assertIn("Rotações da AVL por temperatura: 0", output)
        self.assertEqual(output.count("Total: 1 leitura(s)."), 4)

    def test_csv_import_from_menu(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "leituras com espaços.csv"
            path.write_text("data_hora,temperatura\n2026-11-12 10:30:00,31.5\n", encoding="utf-8")
            monitor, output = self.run_session(["2", f'"{path}"', "0"])
        self.assertEqual(len(monitor), 1)
        self.assertIn("1 leitura(s) importada(s)", output)

    def test_simulated_measurements_from_menu(self):
        monitor, output = self.run_session([
            "8", "3", "2026-11-13 08:00:00", "5", "20", "30", "0",
        ])
        readings = monitor.chronological_readings()
        self.assertEqual(len(readings), 3)
        self.assertEqual(
            [reading.timestamp.strftime("%H:%M:%S") for reading in readings],
            ["08:00:00", "08:05:00", "08:10:00"],
        )
        self.assertTrue(all(20 <= reading.temperature <= 30 for reading in readings))
        self.assertIn("3 leitura(s) simulada(s) inserida(s) nos dois índices.", output)

    def test_invalid_inputs_do_not_exit_menu(self):
        monitor, output = self.run_session([
            "99", "1", "data inválida", "1", "2026-11-12 10:30:00", "nan",
            "4", "abc", "6", "0",
        ])
        self.assertEqual(len(monitor), 0)
        self.assertIn("Opção inválida", output)
        self.assertEqual(output.count("Erro:"), 3)
        self.assertIn("Nenhuma leitura encontrada.", output)

    def test_missing_csv_does_not_exit_menu(self):
        with TemporaryDirectory() as directory:
            monitor, output = self.run_session(["2", str(Path(directory) / "ausente.csv"), "0"])
        self.assertEqual(len(monitor), 0)
        self.assertIn("Erro:", output)
        self.assertIn("Encerrando monitoramento.", output)

    def test_eof_and_keyboard_interrupt_exit_cleanly(self):
        for interruption in (EOFError, KeyboardInterrupt):
            with self.subTest(interruption=interruption):
                output = StringIO()
                with patch("builtins.input", side_effect=interruption), redirect_stdout(output):
                    main()
                self.assertIn("Encerrando monitoramento.", output.getvalue())
