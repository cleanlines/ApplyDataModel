import inspect
import os
import json


class JSONConfig(object):

    def __init__(self, class_name=None):
        super()

        try:
            if class_name is not None:
                a_file = inspect.getframeinfo(inspect.currentframe())[0]
                self._common_config = os.path.join(os.path.split(a_file)[0], 'commonconfig.json')
                self._file = os.path.join(os.path.split(a_file)[0], class_name + '.json')

                if os.path.exists(self._common_config):
                    self.__mixin_config(self._common_config)

                if os.path.exists(self._file):
                    self.__mixin_config(self._file)

        except Exception:
            # no config file found - may or may not be an error depending on the module.
            raise RuntimeError("Cannot load module configuration")

    def add_config(self,a_file):
        self.__mixin_config(a_file)

    def __mixin_config(self, a_file):
        try:
            json_data = open(a_file)
            config = json.load(json_data)
            json_data.close()
            [setattr(self, k, v) for k, v in config.items()]
        except Exception:
            raise RuntimeError("Cannot load application configuration")

    def __str__(self):
        return self._file
