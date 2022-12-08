import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import dotenv_values

from project_store_config_layer.configuration import Configuration
from project_store_exception_layer.exception import CustomException as DatabaseException


def prepare_db():
    try:
        db_config = Configuration()
        enironment_variable= dotenv_values('.env')
        db_name = db_config.DB_NAME
        user = db_config.USER
        host = db_config.HOST
        port = db_config.PORT
        password = enironment_variable['MYSQL_ROOT_PASSWORD']
        database = enironment_variable['MYSQL_DATABASE']
        # password = db_config.PASSWORD

        # password = 'test123'
        # database = db_config.DATABASE
        # This engine just used to query for list of databases
        engine = create_engine(f"{db_name}://{user}:{password}@{host}:{port}")
        # Query for existing databases
        engine.execute(f"CREATE DATABASE IF NOT EXISTS {database}")

        # This engine will be used for the rest of the application
        SQLALCHEMY_DATABASE_URI = f"{db_name}://{user}:{password}@{host}:{port}/{database}"
        db_engine = create_engine(SQLALCHEMY_DATABASE_URI)

        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
        Base = declarative_base()
        return db_engine, SessionLocal, Base

    except Exception as e:
        load_db_exception = DatabaseException(
        "Failed during loading Database file in module")
        raise Exception(load_db_exception.error_message_detail(str(e), sys))\
                from e