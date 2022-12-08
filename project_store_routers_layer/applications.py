import os
import sys
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from project_store_business_logic_layer import business_logic
from project_store_entity_layer import entity as models
from project_store_data_access_layer.data_access import prepare_db
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from starlette.responses import RedirectResponse
from starlette import status

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from project_store_business_logic_layer.business_logic import BusinessLogic
from project_store_routers_layer.auth import get_current_user
from project_store_config_layer.configuration import Configuration
from project_store_exception_layer.exception import CustomException as ApplicationException
from project_store_logging_layer.logger.log_request import LogRequest
from project_store_logging_layer.logger.log_exception import LogExceptionDetail


router = APIRouter(prefix="/application", tags=["application"], responses= {"404": {"description": "Not Found"}})
engine , _, _ = prepare_db()
models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory=Configuration().TEMPLATE_DIR)
business_logic = BusinessLogic()

@router.get("/", response_class=HTMLResponse)
async def read_all_by_user(request: Request, db: Session = Depends(business_logic.get_db)):
    try:
        execution_id=str(uuid.uuid4())
        log_writer = LogRequest(execution_id= execution_id)
        log_writer.log_start(request, db, True)
        user = await get_current_user(request)
        if user is None:
            log_writer.log_stop(request, db, False)
            return RedirectResponse(url="/auth", status_code= status.HTTP_302_FOUND)
        todos = db.query(models.Application).all()
        log_writer.log_stop(request, db, True)
        return templates.TemplateResponse("index.html", {"request": request, "applications": todos, "user": user})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        exception_type = e.__repr__()
        exception_detail = {'exception_type': exception_type,
                    'file_name': file_name, 'line_number': exc_tb.tb_lineno,
                    'detail': sys.exc_info().__str__()}

        log_exception=LogExceptionDetail(execution_id= execution_id)
        log_exception.log(db, str(exception_detail))

        
        log_writer.log_stop(request, db, False)
        raise Exception(e) from e

@router.get("/add-app", response_class=HTMLResponse)
async def add_new_app(request: Request):
    try:
        user = await get_current_user(request)
        if user is None:
            return RedirectResponse(url="/auth", status_code= status.HTTP_302_FOUND)
        return templates.TemplateResponse("add-app.html", {"request": request, "user": user})
    except Exception as e:
        add_new_app_exception = ApplicationException(
        "Failed during Adding New Application in method [{0}]"
            .format(add_new_app.__name__))
        raise Exception(add_new_app_exception.error_message_detail(str(e), sys))\
                from e

@router.post("/add-app", response_class=HTMLResponse)
async def create_app(request: Request, title: str = Form(...),description: str = Form(...),
                                github_url: str = Form(...), technology: str= Form(...), db: Session = Depends(business_logic.get_db)):
    try:
        execution_id=str(uuid.uuid4())
        log_writer = LogRequest(execution_id= execution_id)
        log_writer.log_start(request, db, True)
        user = await get_current_user(request)
        if user is None:
            log_writer.log_stop(request, db, False)
            return RedirectResponse(url="/auth", status_code= status.HTTP_302_FOUND)
        todo_model = models.Application()
        todo_model.title = title
        todo_model.description = description
        todo_model.github_url = github_url
        todo_model.technology = technology
        # todo_model.owner_username = user.get("id")
        todo_model.owner_id = user.get("id")


        db.add(todo_model)
        db.commit()
        log_writer.log_stop(request, db, True)
        return RedirectResponse(url = '/application', status_code= status.HTTP_302_FOUND)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        exception_type = e.__repr__()
        exception_detail = {'exception_type': exception_type,
                    'file_name': file_name, 'line_number': exc_tb.tb_lineno,
                    'detail': sys.exc_info().__str__()}

        log_exception=LogExceptionDetail(execution_id= execution_id)
        log_exception.log(db, str(exception_detail))

        
        log_writer.log_stop(request, db, False)
        raise Exception(e) from e

@router.get("/view-app/{todo_id}", response_class=HTMLResponse)
async def view_app(request: Request, todo_id: int, db: Session = Depends(business_logic.get_db)):
    try:
        execution_id=str(uuid.uuid4())
        log_writer = LogRequest(execution_id=execution_id)
        log_writer.log_start(request, db, True)

        users = await get_current_user(request)
        if users is None:
            log_writer.log_stop(request, db, False)
            return RedirectResponse(url="/auth", status_code= status.HTTP_302_FOUND)
        todo = db.query(models.Application).filter(models.Application.id == todo_id).first()
        log_writer.log_stop(request, db, True)
        return templates.TemplateResponse("view-app.html", {"request": request, "applications": todo, "user": users})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        exception_type = e.__repr__()
        exception_detail = {'exception_type': exception_type,
                    'file_name': file_name, 'line_number': exc_tb.tb_lineno,
                    'detail': sys.exc_info().__str__()}

        log_exception=LogExceptionDetail(execution_id= execution_id)
        log_exception.log(db, str(exception_detail))

        
        log_writer.log_stop(request, db, False)
        raise Exception(e) from e

@router.post("/view-app/{todo_id}", response_class=HTMLResponse)
async def view_app_comit(request: Request, todo_id: int, title: str = Form(...),description: str = Form(...),
                                github_url: str = Form(...), technology: str= Form(...),\
                                db: Session = Depends(business_logic.get_db)):
    try:
        execution_id=str(uuid.uuid4())
        log_writer = LogRequest(execution_id= execution_id)
        log_writer.log_start(request, db, True)
        user = await get_current_user(request)
        if user is None:
            log_writer.log_stop(request, db, False)
            return RedirectResponse(url="/auth", status_code= status.HTTP_302_FOUND)
        
        todo = db.query(models.Application).filter(models.Application.id == todo_id).first()
        log_writer.log_stop(request, db, True)
        return RedirectResponse(url = '/application', status_code= status.HTTP_302_FOUND)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        exception_type = e.__repr__()
        exception_detail = {'exception_type': exception_type,
                    'file_name': file_name, 'line_number': exc_tb.tb_lineno,
                    'detail': sys.exc_info().__str__()}

        log_exception=LogExceptionDetail(execution_id= execution_id)
        log_exception.log(db, str(exception_detail))

        
        log_writer.log_stop(request, db, False)
        raise Exception(e) from e

@router.get("/delete/{todo_id}", response_class=HTMLResponse)
async def delete_app(request: Request, todo_id: int, db: Session = Depends(business_logic.get_db)):
    try:
        execution_id=str(uuid.uuid4())
        log_writer = LogRequest(execution_id=execution_id)
        log_writer.log_start(request, db, True)

        user = await get_current_user(request)
        if user is None:
            log_writer.log_stop(request, db, False)
            return RedirectResponse(url="/auth", status_code= status.HTTP_302_FOUND)
        todo = db.query(models.Application).filter(models.Application.id == todo_id).first()
        if todo is None:
            return RedirectResponse(url = '/application', status_code= status.HTTP_302_FOUND)
        db.query(models.Application).filter(models.Application.id == todo_id).delete()
        db.commit()
        log_writer.log_stop(request, db, True)
        return RedirectResponse(url = '/application', status_code= status.HTTP_302_FOUND)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        exception_type = e.__repr__()
        exception_detail = {'exception_type': exception_type,
                    'file_name': file_name, 'line_number': exc_tb.tb_lineno,
                    'detail': sys.exc_info().__str__()}

        log_exception=LogExceptionDetail(execution_id= execution_id)
        log_exception.log(db, str(exception_detail))

        
        log_writer.log_stop(request, db, False)
        raise Exception(e) from e

@router.get("/search")
async def search_jobs(request: Request, query: Optional[str],query1: Optional[str], db: Session = Depends(business_logic.get_db)):
    try:
        execution_id=str(uuid.uuid4())
        log_writer = LogRequest(execution_id=execution_id)
        log_writer.log_start(request, db, True)

        user = await get_current_user(request)
        if user is None:
            log_writer.log_stop(request, db, False)
            return RedirectResponse(url="/auth", status_code= status.HTTP_302_FOUND)
        items = db.query(models.Application).filter(models.Application.title.contains(query))\
                                .filter(models.Application.technology.contains(query1)).all()
        log_writer.log_stop(request, db, True)
        
        return templates.TemplateResponse(
            "index.html", {"request": request, "applications": items, "user": user}
        )
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        exception_type = e.__repr__()
        exception_detail = {'exception_type': exception_type,
                    'file_name': file_name, 'line_number': exc_tb.tb_lineno,
                    'detail': sys.exc_info().__str__()}

        log_exception=LogExceptionDetail(execution_id= execution_id)
        log_exception.log(db, str(exception_detail))

        
        log_writer.log_stop(request, db, False)
        raise Exception(e) from e