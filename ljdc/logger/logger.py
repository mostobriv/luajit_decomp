import logging
import os
import os.path
import coloredlogs
# import traffic.utils as utils



class Logger:
    LOGS_DIRECTORY = 'logs'

    def __init__(self, name, sub_directory=''):
        # self._ensure_logs_directory_exists(os.path.join(self.LOGS_DIRECTORY, sub_directory))

        if type(name) is not str:
            name = name.__class__.__name__

        self._logger = logging.getLogger(name)
        if len(self._logger.handlers) > 0:
            return

        self._logger.setLevel(logging.DEBUG)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(coloredlogs.ColoredFormatter('[%(name)s] [%(levelname)s] %(message)s'))
        self._logger.addHandler(stream_handler)

        # file_name = utils.camel_case_to_underscore(name) + '.log'
        # file_path = os.path.join(self.LOGS_DIRECTORY, sub_directory, file_name)
        # file_handler = logging.FileHandler(file_path)
        # file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        # self._logger.addHandler(file_handler)

    def debug(self, message):
        self._logger.debug(message)

    def info(self, message):
        self._logger.info(message)

    def warning(self, message):
        self._logger.warning(message)

    def error(self, message, exception: Exception=None):
        self._logger.error(message)
        if exception is not None:
            self._logger.exception(exception)

    @staticmethod
    def _ensure_logs_directory_exists(directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

        if os.path.isfile(directory):
            raise ValueError(f'Can not write logs into directory {directory}, because it\'s file')