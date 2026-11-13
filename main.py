from datetime import datetime

from models.reading import DATETIME_FORMAT, Reading
from services.importer import import_csv
from services.monitor import Monitor


MENU = """
Monitoramento de temperatura de estufa
1 - Inserir leitura
2 - Importar CSV
3 - Consultar intervalo de datas/horários
4 - Consultar temperaturas acima de um limite
5 - Exibir estatísticas
6 - Listar leituras por horário
7 - Listar leituras por temperatura
0 - Sair
"""


def read_datetime(prompt: str) -> datetime:
    return datetime.strptime(input(prompt).strip(), DATETIME_FORMAT)


def show_readings(readings: list[Reading]) -> None:
    if not readings:
        print("Nenhuma leitura encontrada.")
        return
    print(f"{'ID':>6}  {'Data/hora':19}  Temperatura (°C)")
    for reading in readings:
        timestamp = reading.timestamp.strftime(DATETIME_FORMAT)
        print(f"{reading.reading_id:>6}  {timestamp}  {reading.temperature:g}")
    print(f"Total: {len(readings)} leitura(s).")


def run_menu(monitor: Monitor) -> None:
    while True:
        print(MENU)
        option = input("Escolha uma opção: ").strip()
        try:
            if option == "0":
                print("Encerrando monitoramento.")
                return
            if option == "1":
                timestamp = read_datetime("Data/hora (AAAA-MM-DD HH:MM:SS): ")
                temperature = float(input("Temperatura em °C (use ponto decimal): "))
                reading = monitor.add_reading(timestamp, temperature)
                print(f"Leitura {reading.reading_id} inserida nos dois índices.")
            elif option == "2":
                path = input("Caminho do CSV: ").strip().strip('"')
                count = import_csv(path, monitor)
                print(f"{count} leitura(s) importada(s) nos dois índices.")
            elif option == "3":
                start = read_datetime("Início (AAAA-MM-DD HH:MM:SS): ")
                end = read_datetime("Fim (AAAA-MM-DD HH:MM:SS): ")
                show_readings(monitor.readings_between(start, end))
            elif option == "4":
                limit = float(input("Limite em °C (use ponto decimal): "))
                show_readings(monitor.readings_above(limit))
            elif option == "5":
                print(f"Total de leituras: {len(monitor)}")
                print(f"Altura da AVL por horário: {monitor.time_height}")
                print(f"Altura da AVL por temperatura: {monitor.temperature_height}")
            elif option == "6":
                show_readings(monitor.chronological_readings())
            elif option == "7":
                show_readings(monitor.temperature_readings())
            else:
                print("Opção inválida. Escolha um número de 0 a 7.")
        except (ValueError, OSError) as error:
            print(f"Erro: {error}")


def main() -> None:
    try:
        run_menu(Monitor())
    except (EOFError, KeyboardInterrupt):
        print("\nEncerrando monitoramento.")


if __name__ == "__main__":
    main()
