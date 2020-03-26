import datetime
from Singleton import Singleton
import logging.config
from JSONConfig import JSONConfig


class LoggingConfig(object,metaclass=Singleton):

    #json_loggers =['TaskWrapper','PublishServiceHelper','Decorator','GISFeature','DatabaseHelper']
    #TODO: Move log level to config

    def __init__(self):
        self._config = JSONConfig(class_name=self.__class__.__name__)
        self._some_filename = f'_ags_create_feature_class_log.json'#{datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f")}.json'
        self._logging_dic = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'simpleformatter': {'format': '%(asctime)s %(name)s - %(levelname)s:%(message)s'},
                'json': {
                    'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                    'format': '%(asctime)s %(levelname)s %(message)s'
                }
            },
            'handlers': {
                'consolehandler': {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',
                    'formatter': 'simpleformatter',
                    'stream': 'ext://sys.stdout'
                },
                'filehandler': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': 'DEBUG',
                    'formatter': 'json',
                    'filename': f"logs/{self._some_filename}",
                    'maxBytes': 102400, #10485760,
                    'backupCount':5,
                    'mode':'a'
                }
            },

            'loggers': {
                'root': {'handlers': ['consolehandler'], 'level': 'DEBUG'},
                'json': {'handlers': ['filehandler'], 'level': 'DEBUG'}}
        }
        logging.config.dictConfig(self._logging_dic)

    def get_logger(self,class_name):
        if class_name in self._config.jsonloggers:
             return logging.getLogger('json')
        else:
            return logging.getLogger('root')





