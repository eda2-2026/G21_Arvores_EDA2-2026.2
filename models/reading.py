from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Reading:
    reading_id: int
    timestamp: datetime
    temperature: float

def time_key(reading: Reading) -> tuple[datetime, int]:
    return reading.timestamp, reading.reading_id

def temperature_key(reading: Reading) -> tuple[float, datetime, int]:
    return reading.temperature, reading.timestamp, reading.reading_id
