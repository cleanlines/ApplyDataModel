from JSONConfig import JSONConfig
from LoggingConfig import LoggingConfig

class Task(object): pass


class BaseObject(object):

    def __init__(self):
        
        self._class_name = self.__class__.__name__
        self._logger = LoggingConfig().get_logger(self.__class__.__name__)
        self.log = lambda x: self.__do_message(x)
        self.errorlog = lambda x: self.__do_message(x, "error")
        self.log(f"Class:{self._class_name}")
        self._config = JSONConfig(class_name=self._class_name)
        self.log(f"loaded config for {self._class_name} from {str(self._config)}")


    def __do_message(self, message_string, level="debug"):
        """
        Write to log method (file or memory)
        params: level: level to write (default info) - one of:
                       critical,error,warn,info,debug
        """
        #DEBUG print(f"DEBUG:{message_string},{level}")
        message_string = f"{self._class_name} :{message_string}"
        if level == "critical":
            self._logger.critical(message_string)
        elif level == "error" or level == "err":
            self._logger.error(message_string)
            self._logger.exception("Traceback as follows:")
        elif level == "warn":
            self._logger.warning(message_string)
        elif level == "info":
            self._logger.info(message_string)
        elif level == "debug":
            self._logger.debug(message_string)
        else:
            print(message_string)