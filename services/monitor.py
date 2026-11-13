from collections.abc import Iterable
from copy import copy
from datetime import datetime

from models.reading import (
    Reading,
    temperature_key,
    time_key,
    validate_temperature,
    validate_timestamp,
)
from trees.avl import AVLTree

class Monitor:
    """Mantém duas AVL independentes apontando para as mesmas leituras."""

    def __init__(self) -> None:
        self._time_index = AVLTree(key=time_key)
        self._temperature_index = AVLTree(key=temperature_key)
        self._next_id = 1

    def __len__(self) -> int:
        return len(self._time_index)

    @property
    def time_height(self) -> int:
        return self._time_index.height

    @property
    def temperature_height(self) -> int:
        return self._temperature_index.height

    def add_reading(self, timestamp: datetime, temperature: float) -> Reading:
        return self.add_readings([(timestamp, temperature)])[0]

    def add_readings(self, values: Iterable[tuple[datetime, float]]) -> list[Reading]:
        """Insere um lote inteiro ou mantém ambos os índices inalterados.

        Cópias rasas são seguras porque os nós da AVL são imutáveis. Cada
        inserção ainda custa O(log n); somente os caminhos alterados são copiados.
        """
        time_index = copy(self._time_index)
        temperature_index = copy(self._temperature_index)
        next_id = self._next_id
        readings: list[Reading] = []
        for timestamp, temperature in values:
            reading = Reading(next_id, timestamp, temperature)
            time_index.insert(reading)
            temperature_index.insert(reading)
            readings.append(reading)
            next_id += 1
        self._time_index = time_index
        self._temperature_index = temperature_index
        self._next_id = next_id
        return readings

    def readings_between(self, start: datetime, end: datetime) -> list[Reading]:
        """Consulta inclusiva por data/hora, inclusive quando há repetições."""
        validate_timestamp(start)
        validate_timestamp(end)
        if start > end:
            raise ValueError("A data inicial deve ser menor ou igual à data final")
        # Todos os IDs são positivos e menores que o próximo ID.
        return self._time_index.range_search((start, 0), (end, self._next_id))

    def readings_above(self, limit: float) -> list[Reading]:
        """Retorna temperaturas estritamente maiores que o limite, em ordem."""
        validate_temperature(limit)
        # A chave fica depois de todas as leituras com temperatura igual ao limite.
        start = (limit, datetime.max, self._next_id)
        return self._temperature_index.range_search(start=start)

    def chronological_readings(self) -> list[Reading]:
        return self._time_index.in_order()

    def temperature_readings(self) -> list[Reading]:
        return self._temperature_index.in_order()
