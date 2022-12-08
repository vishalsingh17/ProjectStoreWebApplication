import uuid
import sys
from datetime import datetime
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import update
from project_store_entity_layer import entity as models
from project_store_utils_layer.utils import CommonUtils
# from desktop_data_access_layer.mongo_db.mongo_db_atlas import MongoDBOperation
from project_store_exception_layer.exception import CustomException as ExRequestException
from project_store_config_layer.configuration import Configuration
from project_store_data_access_layer.data_access import prepare_db
from project_store_business_logic_layer.business_logic import BusinessLogic

engine ,_,_ = prepare_db()
class LogExceptionDetail:
    def __init__(self, execution_id=None):
        self.configs = Configuration()
        self.utils = CommonUtils()
        self.business_logic = BusinessLogic()

        self.log_collection_name=models
        self.execution_id=execution_id
        # self.mongo_db_object = MongoDBOperation()
        self.log_start_date=self.utils.get_date()
        self.log_start_time=self.utils.get_time()

    def log(self,db,log_message):
        try:
            log_writer_id=str(uuid.uuid4())

            self.now = datetime.now()
            self.date = self.now.date()
            self.current_time = self.now.strftime("%H:%M:%S")


            log_model = models.LogException()
            log_model.execution_id = self.execution_id
            log_model.log_update_date = self.utils.get_date()
            log_model.log_update_time = datetime.now()
            log_model.message = log_message
            log_model.log_writer_id = log_writer_id

            db.add(log_model)
            db.commit()
        except Exception as e:
            log_exception = ExRequestException(
                "Failed during getting log data in module [{0}] class [{1}] method [{2}]"
                    .format(LogExceptionDetail.__module__.__str__(), LogExceptionDetail.__name__,
                            self.log.__name__))
            raise Exception(log_exception.error_message_detail(str(e), sys)) from e 