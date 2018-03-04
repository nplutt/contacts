from uuid import uuid4

from sqlalchemy import Column, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import DateTime, String
from sqlalchemy_searchable import make_searchable
from sqlalchemy_utils.types import TSVectorType

from chalicelib.singletons import Base
from chalicelib.utils import database_username

# make_searchable()


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
    data_type = Column(String, nullable=False)
    meta_data = Column(String, nullable=False)
    search_vector = Column(TSVectorType('meta_data'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    add_name = Column(String, default=database_username)
    add_date = Column(DateTime, server_default=func.now())
    last_maintenance_name = Column(String, default=database_username, onupdate=database_username)
    last_maintenance_date = Column(DateTime, server_default=func.now(), onupdate=func.now())
