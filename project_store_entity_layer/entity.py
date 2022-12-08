from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, VARCHAR
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime
from project_store_data_access_layer.data_access import prepare_db

_, _, Base = prepare_db()

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=True)
    username = Column(String(45), unique=True, index=True, nullable=True)
    first_name = Column(String(45), nullable=True)
    last_name = Column(String(45), nullable=True)
    hashed_password = Column(String(200), nullable=True)
    is_active = Column(Integer, default=True, nullable=True)

    todos = relationship("Application", back_populates="owner")

class Application(Base):
    __tablename__ = "application"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    title = Column(String(200), nullable=True)
    description = Column(String(200), nullable=True)
    github_url = Column(String(200), nullable=True)
    technology = Column(String(200), nullable=True)
    # owner_username = Column(Integer, ForeignKey("users.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("Users", back_populates="todos")

class LogUser(Base):
    __tablename__ = "log_user"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    execution_id = Column(String(45), nullable=True)
    log_writer_id = Column(String(45), nullable=True)
    status = Column(Boolean, nullable=True)
    log_start_date = Column(String(60), nullable=True)
    log_start_time = Column(String(200), nullable=True)
    log_update_time = Column(String(50), nullable=True)
    log_stop_date = Column(String(45), nullable=True)
    log_stop_time = Column(String(45), nullable=True)
    execution_time_milisecond = Column(Integer, nullable=True)
    request = Column(String(200), nullable=True)

class LogException(Base):
    __tablename__ = "log_exception"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    execution_id = Column(String(45), nullable=True)
    log_update_date = Column(String(50), nullable=True)
    log_update_time = Column(String(50), nullable=True)
    message = Column(String(400), nullable=True)
    log_writer_id = Column(String(45), nullable=True)
