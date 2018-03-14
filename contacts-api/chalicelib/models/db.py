from uuid import uuid4

from sqlalchemy import Column, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import DateTime, String
from sqlalchemy_utils.types import TSVectorType

from chalicelib.singletons import Base
from chalicelib.utils import database_username


class Users(Base):
    __tablename__ = 'users'

    user_id = Column(UUID(as_uuid=True), unique=True, default=uuid4, nullable=False)
    email_address = Column(String, primary_key=True)
    first_name = Column(String, primary_key=True)
    last_name = Column(String, primary_key=True)
    add_name = Column(String, default=database_username)
    add_date = Column(DateTime, server_default=func.now())
    last_maintenance_name = Column(String, default=database_username, onupdate=database_username)
    last_maintenance_date = Column(DateTime, server_default=func.now(), onupdate=func.now())


class UserData(Base):
    __tablename__ = 'user_data'

    data_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    field_type = Column(String, nullable=False)
    field_data = Column(String, nullable=False)
    search_vector = Column(TSVectorType(), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    add_name = Column(String, default=database_username)
    add_date = Column(DateTime, server_default=func.now())
    last_maintenance_name = Column(String, default=database_username, onupdate=database_username)
    last_maintenance_date = Column(DateTime, server_default=func.now(), onupdate=func.now())

    users = relationship(Users, backref=backref('user_data', cascade='delete'))
