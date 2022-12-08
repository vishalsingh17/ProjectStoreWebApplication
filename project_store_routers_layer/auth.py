import os
import sys
from urllib import response
from wsgiref import validate
import uuid
from starlette.responses import RedirectResponse
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter, Request, Response, Form
from pydantic import BaseModel
from typing import Optional
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import dotenv_values

from project_store_entity_layer import entity as models
from project_store_data_access_layer.data_access import prepare_db

from project_store_business_logic_layer.business_logic import BusinessLogic
from project_store_config_layer.configuration import Configuration
from project_store_exception_layer.exception import CustomException as AuthenticationException
from project_store_logging_layer.logger.log_exception import LogExceptionDetail
from project_store_logging_layer.logger.log_request import LogRequest

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
engine , _, _ = prepare_db()
models.Base.metadata.create_all(bind=engine)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

templates = Jinja2Templates(directory=Configuration().TEMPLATE_DIR)

router = APIRouter(prefix="/auth", tags=["auth"], responses= {"401": {"description": "Not Authorized!!!"}}) 

business_logic = BusinessLogic()
class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None
    
    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get("email")
        self.password = form.get("password")



async def get_current_user(request: Request):
    try:
        if os.environ.get('SECRET_KEY') is None or os.environ.get('ALGORITHM') is None:
            enironment_variable= dotenv_values('.env')
            secret_key = enironment_variable['SECRET_KEY']
            algorithm = enironment_variable['ALGORITHM']
        else:
            secret_key = os.environ.get('SECRET_KEY')
            algorithm = os.environ.get('ALGORITHM')
        token=request.cookies.get("access_token")
        if token is None:
            return None
        # payload = jwt.decode(token, Configuration().SECRET_KEY, algorithms=[Configuration().ALGORITHM])
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        
        if username is None or user_id is None:
            return logout(request)
        return {"username": username, "id": user_id}
    except JWTError:
        raise HTTPException(status_code=404, detail="Detail Not Found")
    except Exception as e:
            load_get_current_user_exception = AuthenticationException(
            "Failed during Getting current user in method [{0}]"
                .format(get_current_user.__name__))
            raise Exception(load_get_current_user_exception.error_message_detail(str(e), sys))\
                 from e

@router.post("/token")
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(business_logic.get_db)):
    try:

        user = business_logic.authenticate_user(form_data.username, form_data.password, db)
        if not user:
            # log_writer.log_stop(response, db, False)
            return False
        token_expires = timedelta(minutes=60)
        token = business_logic.create_access_token(user.username,
                                    user.id,
                                    expires_delta=token_expires)

        response.set_cookie(key="access_token", value=token, httponly=True)
  
        return True
    except Exception as e:
        load_login_for_access_token_exception = AuthenticationException(
            "Failed during Login for access token in method [{0}]"
                .format(login_for_access_token.__name__))
        raise Exception(load_login_for_access_token_exception.error_message_detail(str(e), sys))\
                 from e


@router.get("/", response_class=HTMLResponse)
async def authentication_page(request: Request):
    try:
        return templates.TemplateResponse("login.html", {"request": request})
    except Exception as e:
        authentication_page_exception = AuthenticationException(
        "Failed during Authenticating in method [{0}]"
            .format(authentication_page.__name__))
        raise Exception(authentication_page_exception.error_message_detail(str(e), sys))\
                from e  

@router.post("/", response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(business_logic.get_db)):
    try:
        execution_id=str(uuid.uuid4())
        log_writer = LogRequest(execution_id = execution_id)
        log_writer.log_start(request, db, True)
        form = LoginForm(request)

        await form.create_oauth_form()
        response = RedirectResponse(url="/application", status_code=status.HTTP_302_FOUND)
        validate_user_cookie = await login_for_access_token(response= response, form_data=form, db=db)

        if not validate_user_cookie:
            log_writer.log_stop(request, db, False)
            msg = "Incorrect Username and password"
            return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
        log_writer.log_stop(request, db, True)
        return response

    except HTTPException:
        msg = "UnKnown Error"
        return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        exception_type = e.__repr__()
        exception_detail = {'exception_type': exception_type,
                    'file_name': file_name, 'line_number': exc_tb.tb_lineno,
                    'detail': sys.exc_info().__str__()}

        log_exception=LogExceptionDetail(execution_id= execution_id)
        log_exception.log(db, str(exception_detail))

        
        log_writer.log_stop(response, db, False)
        raise Exception(e) from e


@router.get("/logout")
async def logout(request: Request,db: Session = Depends(business_logic.get_db)):
    try:
        execution_id = str(uuid.uuid4())
        log_writer = LogRequest(execution_id= execution_id)
        log_writer.log_start(request, db, True)
        msg = "You have been logged out"
        response =  templates.TemplateResponse("login.html", {"request": request, "msg": msg})
        response.delete_cookie(key="access_token")
        log_writer.log_stop(request, db, True)
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        exception_type = e.__repr__()
        exception_detail = {'exception_type': exception_type,
                    'file_name': file_name, 'line_number': exc_tb.tb_lineno,
                    'detail': sys.exc_info().__str__()}

        log_exception=LogExceptionDetail(execution_id= execution_id)
        log_exception.log(db, str(exception_detail))
        
        log_writer.log_stop(response, db, False)
        raise Exception(e) from e

@router.get("/register", response_class=HTMLResponse)
async def authentication_page(request: Request):
    try:
        return templates.TemplateResponse("register.html", {"request": request})
    except Exception as e:
        authentication_page_exception = AuthenticationException(
        "Failed during Authenticating user in method [{0}]"
            .format(authentication_page.__name__))
        raise Exception(authentication_page_exception.error_message_detail(str(e), sys))\
                from e

@router.post("/register", response_class=HTMLResponse)
async def register_user(request: Request,
                        email: str = Form(...),
                        username: str= Form(...),
                        firstname: str= Form(...),
                        lastname: str= Form(...),
                        password: str= Form(...),
                        password2: str= Form(...),
                        db: Session = Depends(business_logic.get_db)):
    try:
        execution_id=str(uuid.uuid4())
        log_writer = LogRequest(execution_id= execution_id)
        log_writer.log_start(request, db, True)
        validation1 = db.query(models.Users).filter(models.Users.username == username).first()
        validation2 = db.query(models.Users).filter(models.Users.email == email).first()

        if password != password2 or validation1 is not None or validation2 is not None:
            msg = "Invalid Registration Request"
            return templates.TemplateResponse("register.html", {"request": request, "msg": msg})
        
        user_model = models.Users()
        user_model.username = username
        user_model.email = email
        user_model.first_name = firstname
        user_model.last_name = lastname
        user_model.hashed_password = business_logic.get_password_hash(password)
        user_model.is_active = True

        db.add(user_model)
        db.commit()
        log_writer.log_stop(request, db, True)
        msg = "Registration Successful...Please Login to continue"
        return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        exception_type = e.__repr__()
        exception_detail = {'exception_type': exception_type,
                    'file_name': file_name, 'line_number': exc_tb.tb_lineno,
                    'detail': sys.exc_info().__str__()}

        log_exception=LogExceptionDetail(execution_id= execution_id)
        log_exception.log(db, str(exception_detail))
        
        log_writer.log_stop(response, db, False)
        raise Exception(e) from e