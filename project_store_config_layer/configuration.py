import os
import sys
from project_store_utils_layer.utils import CommonUtils
from project_store_exception_layer.exception import CustomException as ConfigurationException


class Configuration:
    def __init__(self):
        try:
            config = CommonUtils().read_yaml("config.yaml")

            FRONTEND_DIR = config['FRONTEND_DIR']
            # KEY_TOKEN = config['KEY_TOKEN']
            DATABASE = config['DATABASE']
            
            self.TEMPLATE_DIR = FRONTEND_DIR['TEMPLATE_DIR']
            self.STATIC_DIR = FRONTEND_DIR['STATIC_DIR']

            # self.SECRET_KEY = KEY_TOKEN['SECRET_KEY']
            # self.ALGORITHM = KEY_TOKEN['ALGORITHM']

            self.DB_NAME = DATABASE['DB_NAME']
            self.USER = DATABASE['USER']
            self.HOST = DATABASE['HOST']
            self.PORT = DATABASE['PORT']
            self.PASSWORD = DATABASE['PASSWORD']
            self.DATABASE = DATABASE['DATABASE']

        except Exception as e:
            configuration_exception = ConfigurationException(
                "Failed during loading configuration file in module [{0}] class [{1}] method [{2}]"
                    .format(self.__module__, Configuration.__name__,
                            self.__init__.__name__))
            raise Exception(configuration_exception.error_message_detail(str(e), sys))\
                                             from e