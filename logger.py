import logging


class Logger:
    def __init__(self):
        logging.basicConfig(filename='./logs/info.log',
                            format='[%(asctime)s] - %(levelname)s. %(message)s',
                            datefmt='%d/%m/%Y %H:%M:%S',
                            level=logging.DEBUG,
                            filemode='a')
        self.logger = logging.getLogger(__name__)

    def log_info(self, message):
        self.logger.info(f"{message}")


logger = Logger()
