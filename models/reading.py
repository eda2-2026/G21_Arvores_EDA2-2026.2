from dataclasses import dataclass
from datetime import datetime
from math import isfinite

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

def validate_timestamp(timestamp: datetime) -> None:
    if not isinstance(timestamp, datetime):
        raise ValueError("A data/hora deve ser um datetime")
    if timestamp.utcoffset() is not None:
        raise ValueError("Use data/hora local, sem fuso horário")

def validate_temperature(temperature: float) -> None:
    if isinstance(temperature, bool) or not isinstance(temperature, (int, float)):
        raise ValueError("A temperatura deve ser numérica e finita")
    try:
        finite = isfinite(temperature)
    except OverflowError:
        finite = False
    if not finite:
        raise ValueError("A temperatura deve ser numérica e finita")

@dataclass(frozen=True)
class Reading:
    reading_id: int
    timestamp: datetime
    temperature: float

    def __post_init__(self) -> None:
        if type(self.reading_id) is not int or self.reading_id <= 0:
            raise ValueError("O identificador deve ser um inteiro positivo")
        validate_timestamp(self.timestamp)
        validate_temperature(self.temperature)
        object.__setattr__(self, "temperature", float(self.temperature))

def time_key(reading: Reading) -> tuple[datetime, int]:
    return reading.timestamp, reading.reading_id

def temperature_key(reading: Reading) -> tuple[float, datetime, int]:
    return reading.temperature, reading.timestamp, reading.reading_id
