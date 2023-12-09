import logging


class Log:



    def __init__(self, path_to_log_file: str = 'logs/logs.log') -> None:
        logging.basicConfig(level=logging.INFO,
                            filename=path_to_log_file,
                            filemode='a',
                            # format='%(asctime)s %(levelname)s %(message)s',
                            format='%(asctime)s %(levelname)s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            encoding='utf-8')

    def save_logs(self, message: str, logs_level: str = 'info') -> None:
        if logs_level == 'info':
            logging.info(message)
        elif logs_level == 'warning':
            logging.warning(message)
        elif logs_level == 'error':
            logging.error(message)




# logging.warning(f'Ошибка')
#
# logging.debug("A DEBUG Message")
# logging.info("An INFO")
# logging.warning("A WARNING")
# logging.error("An ERROR")
# logging.critical("A message of CRITICAL severity")

logs = Log(path_to_log_file='logs.log')
logs.save_logs(message='kek', logs_level='info')
