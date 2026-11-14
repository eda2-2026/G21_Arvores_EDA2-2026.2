from datetime import datetime, timedelta
from random import Random

from models.reading import validate_temperature, validate_timestamp

def generate_measurements(
    start: datetime,
    count: int,
    interval: timedelta = timedelta(minutes=1),
    minimum_temperature: float = 15.0,
    maximum_temperature: float = 40.0,
    seed: int | None = None,
) -> list[tuple[datetime, float]]:
    validate_timestamp(start)
    if type(count) is not int or count < 0:
        raise ValueError("A quantidade deve ser um inteiro não negativo")
    if not isinstance(interval, timedelta) or interval <= timedelta(0):
        raise ValueError("O intervalo deve ser maior que zero")
    validate_temperature(minimum_temperature)
    validate_temperature(maximum_temperature)
    if minimum_temperature > maximum_temperature:
        raise ValueError("A temperatura mínima deve ser menor ou igual à máxima")
    random = Random(seed)
    return [
        (
            start + index * interval,
            random.uniform(minimum_temperature, maximum_temperature),
        )
        for index in range(count)
    ]
