import uuid
import sys
from datetime import datetime

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import update
from project_store_entity_layer import entity as models
from project_store_utils_layer.utils import CommonUtils
# from desktop_data_access_layer.mongo_db.mongo_db_atlas import MongoDBOperation
from project_store_exception_layer.exception import CustomException as LogRequestException
from project_store_config_layer.configuration import Configuration
from project_store_business_logic_layer.business_logic import BusinessLogic

class LogRequest:
    def __init__(self,execution_id=None):
        self.configs = Configuration()
        self.utils = CommonUtils()
        self.business_logic = BusinessLogic()
        # self.log_database=self.configs.DB_NAME
        self.log_collection_name=models
        self.execution_id=execution_id
        # self.mongo_db_object = MongoDBOperation()
        self.log_start_date=self.utils.get_date()
        self.log_start_time=self.utils.get_time()


    def get_log_data(self, request_data):
        try:
            log_data = request_data
            return log_data
        except Exception as e:
            log_exception = LogRequestException(
                "Failed during getting log data in module [{0}] class [{1}] method [{2}] -->log detail[{3}]"
                    .format(LogRequest.__module__.__str__(), LogRequest.__name__,
                            self.get_log_data.__name__, request_data))
            raise Exception(log_exception.error_message_detail(str(e), sys)) from e 
      

    def log_start(self, request, db, status=True):
        try:
            self.log_writer_id=str(uuid.uuid4())
            self.now = datetime.now()
            self.date = self.now.date()
            self.current_time = self.now.strftime("%H:%M:%S")


            log_model = models.LogUser()
            log_model.execution_id = self.execution_id
            log_model.status = status
            log_model.log_writer_id = self.log_writer_id
            log_model.log_start_date = self.log_start_date
            log_model.log_start_time = self.log_start_time
            log_model.log_update_time = datetime.now()
            log_model.request = str(request.url)

            db.add(log_model)
            db.commit()
            
        except Exception as e:
            log_exception = LogRequestException(
                "Failed during starting log in module [{0}] class [{1}] method [{2}]"
                    .format(LogRequest.__module__.__str__(), LogRequest.__name__,
                            self.log_start.__name__))
            raise Exception(log_exception.error_message_detail(str(e), sys)) from e


    def log_stop(self,request, db, status=True):
        try:
            self.now = datetime.now()
            self.date = self.now.date()
            self.current_time = self.now.strftime("%H:%M:%S")

            log_stop_date= self.utils.get_date()
            log_stop_time= self.utils.get_time()
            future_date="{} {}".format(log_stop_date,log_stop_time)
            past_date="{} {}".format(self.log_start_date,self.log_start_time)

            log_model = db.query(models.LogUser).filter(models.LogUser.execution_id == self.execution_id).one_or_none()
            log_model.status = status
            log_model.log_stop_date = log_stop_date
            log_model.log_stop_time = log_stop_time
            log_model.log_writer_id = self.log_writer_id
            log_model.execution_time_milisecond = self.utils.get_difference_in_milisecond(\
                                                    future_date,past_date)
            db.add(log_model)
            db.commit()
        except Exception as e:
            log_exception = LogRequestException(
                "Failed during stopping log in module [{0}] class [{1}] method [{2}]"
                    .format(LogRequest.__module__.__str__(), LogRequest.__name__,
                            self.log_stop.__name__))
            raise Exception(log_exception.error_message_detail(str(e), sys)) from e