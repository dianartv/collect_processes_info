import psutil
from psutil import NoSuchProcess
from psutil import Process as PsutilProcess
from multiprocessing import Process, Manager
from datetime import datetime


class ProcessesList:
    """Содержит объекты процессы."""

    processes_cpu_stats = []

    def __init__(self, processes: list) -> None:

        self.processes = [
            self._find_procs_by_name(p['process_name'], p['cores']) for p in
            processes
        ]
        self.processes_watch_list = []
        for p in self.processes:
            if p:
                self.processes_watch_list += [
                    ProcessStats(i.pid, cpu_cores=i.cores) for i in p
                ]

    @classmethod
    def _cpu_stats(cls, pid, interval, return_dict, cores):
        """Сбор статистики CPU для процесса."""

        def _cpu_format(cpu: list) -> list:
            return 0.0 if len(cpu) == 1 else sum(cpu[1:]) / len(cpu[1:])

        def _result_format(pid, cpu_data, counter):
            return {'pid': pid,
                    'cpu': cpu_data,
                    'interval': counter}

        try:
            p = PsutilProcess(pid=pid)

            cpu = [0.0]
            counter = 1

            try:
                while counter < interval:
                    cpu.append(p.cpu_percent(interval=2) / cores)
                    counter += 2

                return_dict[pid] = _result_format(p.pid, _cpu_format(cpu),
                                                  counter)
            except NoSuchProcess:
                # logging
                return_dict[pid] = _result_format(p.pid, _cpu_format(cpu),
                                                  counter)

        except NoSuchProcess:
            # logging
            return_dict[pid] = _result_format(pid,
                                              None,
                                              0)

    def create_stats(self, interval):
        """Сбор статистики CPU в мультипотоке."""

        manager = Manager()
        return_dict = manager.dict()
        processes = []
        pid_lst = [(i.pid, i.cpu_cores) for i in self.processes_watch_list]

        # Запуск дополнительных процессов
        for pid in pid_lst:
            p = Process(target=self._cpu_stats,
                        kwargs={'pid': pid[0],
                                'interval': interval,
                                'return_dict': return_dict,
                                'cores': pid[1]},
                        daemon=True)
            processes.append(p)
            p.start()

        [p.join() for p in processes]

        for cpu_process_data in return_dict.values():
            obj = list(
                filter(lambda p: p.pid == cpu_process_data['pid'],
                       self.processes_watch_list))[
                0]
            obj.cpu = cpu_process_data['cpu'], cpu_process_data['interval']

    def save_stats_to_file(self, path: str = 'stats/stats.txt') -> None:
        """Сохранение результатов CPU за период в текстовый файл."""

        now = datetime.now().strftime('%d/%m/%Y %H:%M')
        data = ''
        for p in self.processes_watch_list:
            if p.cpu[0] is None:
                data += f'Процесс: {p.name} [PID:{p.pid}]\n' \
                        f'Перестал существовать в момент ' \
                        f'сбора информации.\n---\n'
            else:
                data += f'Процесс: {p.name} [PID:{p.pid}]\n' \
                        f'Cores: {p.cpu_cores}\n' \
                        f'CPU: {round(p.cpu[0], 2)}% в течении ' \
                        f'{p.cpu[1]} сек.\n---\n'

        with open(path, 'a', encoding='utf-8') as f:
            f.write(f'{now}\n{data}\n')

    @staticmethod
    def _find_procs_by_name(name: str, cores=None) -> list | bool:
        # name передалть
        """Возвращает список процессов, соответствующих 'name'."""

        result = [
            p for p in psutil.process_iter(['name']) if p.info['name'] == name
        ]
        if result:
            for _ in result:
                _.cores = cores
            return result
        else:
            return False


class ProcessStats:
    def __init__(self, pid: int, cpu_cores=None) -> None:
        self.pid = pid
        self._process = self._isprocess(pid)
        self.name = self._process.name()
        if cpu_cores is None:
            self.cpu_cores = psutil.cpu_count(logical=False)
        else:
            self.cpu_cores = cpu_cores

    def __str__(self):
        return f'Процесс: {self.name}, pid:{self.pid}'

    @staticmethod
    def _isprocess(pid: int):
        try:
            return PsutilProcess(pid=pid)
        except NoSuchProcess:
            # logging
            print(f'Процесс с pid:{pid} не существует.')

    def get_cpu_percent(self, interval: float) -> float:
        cores = psutil.cpu_count(logical=True)
        return self._process.cpu_percent(interval=interval) / cores
