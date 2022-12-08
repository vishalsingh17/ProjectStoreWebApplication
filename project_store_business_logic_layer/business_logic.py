import sys
import os
from passlib.context import CryptContext
from typing import Optional
from datetime import datetime, timedelta
from jose import jwt, JWTError
from dotenv import dotenv_values


# from fastapi import FastAPI, Depends, HTTPException, status, APIRouter, Request, Response, Form

from project_store_entity_layer import entity as models
from project_store_data_access_layer.data_access import prepare_db
from project_store_config_layer.configuration import Configuration
from project_store_exception_layer.exception import CustomException as BusinessLogicException

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class BusinessLogic:

    def get_db(self):
        try:
            _ , SessionLocal, _ = prepare_db()
            db = SessionLocal()
            yield db
        except Exception as e:    
            load_db_exception = BusinessLogicException(
            "Failed during loading Database file in module [{0}] class [{1}] method [{2}]"
                .format(self.__module__, BusinessLogic.__name__,
                        self.get_db.__name__))
            raise Exception(load_db_exception.error_message_detail(str(e), sys))\
                 from e
        finally:
            db.close()


    def get_password_hash(self, password):
        try:
            return bcrypt_context.hash(password)
        except Exception as e:    
            get_password_hash_exception = BusinessLogicException(
            "Failed during Generating Hash password Verifying Passwprd file in module [{0}] class [{1}] method [{2}]"
                .format(self.__module__, BusinessLogic.__name__,
                        self.get_password_hash.__name__))
            raise Exception(get_password_hash_exception.error_message_detail(str(e), sys))\
                 from e 

    def verify_password(self, plain_password, hashed_password):
        try:
            return bcrypt_context.verify(plain_password, hashed_password)
        except Exception as e:    
            verify_password_exception = BusinessLogicException(
            "Failed during Verifying Passwprd file in module [{0}] class [{1}] method [{2}]"
                .format(self.__module__, BusinessLogic.__name__,
                        self.verify_password.__name__))
            raise Exception(verify_password_exception.error_message_detail(str(e), sys))\
                 from e


    def authenticate_user(self, username: str, password: str, db):
        try:
            user = db.query(models.Users)\
                .filter(models.Users.username == username)\
                .first()
            if not user:
                return False
            if not self.verify_password(password, user.hashed_password):
                return False
            return user
        except Exception as e:    
            authenticate_user_exception = BusinessLogicException(
            "Failed during Authenticating User in module [{0}] class [{1}] method [{2}]"
                .format(self.__module__, BusinessLogic.__name__,
                        self.authenticate_user.__name__))
            raise Exception(authenticate_user_exception.error_message_detail(str(e), sys))\
                 from e


    def create_access_token(self, username: str, user_id: int,
                            expires_delta: Optional[timedelta] = None):
        try:
            
            if os.environ.get('SECRET_KEY') is None and os.environ.get('ALGORITHM') is None:
                enironment_variable= dotenv_values('.env')
                secrete_key = enironment_variable['SECRET_KEY']
                algorithm = enironment_variable['ALGORITHM']
            else:
                secrete_key = os.environ.get('SECRET_KEY')
                algorithm = os.environ.get('ALGORITHM')

            encode = {"sub": username, "id": user_id}
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(minutes=15)
            encode.update({"exp": expire})
            # return jwt.encode(encode, Configuration().SECRET_KEY, algorithm=Configuration().ALGORITHM)
            return jwt.encode(encode,secrete_key, algorithm=algorithm)

        except Exception as e:    
            load_token_exception = BusinessLogicException(
            "Failed during loading Token in module [{0}] class [{1}] method [{2}]"
                .format(self.__module__, BusinessLogic.__name__,
                        self.create_access_token.__name__))
            raise Exception(load_token_exception.error_message_detail(str(e), sys))\
                 from e

