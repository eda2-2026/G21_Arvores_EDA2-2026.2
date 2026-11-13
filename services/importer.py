import csv
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

from models.reading import DATETIME_FORMAT, validate_temperature
from services.monitor import Monitor


def import_csv(path: str | Path, monitor: Monitor) -> int:
    """Importa CSV UTF-8 com cabeçalho data_hora,temperatura, sem carga parcial."""
    with open(path, encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, strict=True)
        try:
            fieldnames = reader.fieldnames
        except csv.Error as error:
            raise ValueError(f"Cabeçalho CSV inválido: {error}") from error
        if fieldnames != ["data_hora", "temperatura"]:
            raise ValueError("O cabeçalho do CSV deve ser data_hora,temperatura")

        def values() -> Iterator[tuple[datetime, float]]:
            try:
                for row in reader:
                    line = reader.line_num
                    if None in row or any(value is None for value in row.values()):
                        raise ValueError(f"Linha {line}: esperado data_hora,temperatura")
                    try:
                        timestamp = datetime.strptime(
                            row["data_hora"].strip(), DATETIME_FORMAT
                        )
                        temperature = float(row["temperatura"].strip())
                        validate_temperature(temperature)
                    except ValueError as error:
                        raise ValueError(f"Linha {line}: {error}") from error
                    yield timestamp, temperature
            except csv.Error as error:
                raise ValueError(f"Linha {reader.line_num}: CSV inválido ({error})") from error

        return len(monitor.add_readings(values()))
