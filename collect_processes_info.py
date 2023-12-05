from scripts.processes import ProcessesList
from config import PROCESSES, INTERVAL


def main():
    # Поздание коллекции из процессов
    processes = ProcessesList(processes=PROCESSES)

    # Сборка статистики
    processes.create_stats(interval=INTERVAL)

    # Сохранение статистики
    processes.save_stats_to_file(path='stats/stats.txt')


if __name__ == '__main__':
    main()
