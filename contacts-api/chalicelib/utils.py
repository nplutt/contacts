import logging

from contextlib import contextmanager
from os import getenv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, configure_mappers
from sqlalchemy.engine.url import URL

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

engines = {}


def get_database_url(username='DB_USER', password='DB_PASSWORD'):
    """
    Generates the postgres connection url.
    Args:
        username (str): Allows for configuring what username to use,
                        defaults to DB_USER
        password (str): Allows for configuring what password to use,
                        defaults to DB_PASSWORD
    Returns:
        sqlalchemy.engine.url.URL: The connection url
    """
    return URL(drivername='postgres',
               username=getenv(username),
               password=getenv(password),
               host=getenv('DB_HOST'),
               port=getenv('DB_PORT'),
               database=getenv('DB_NAME'))


@contextmanager
def db_session():
    """
    Builds and provides a scoped SqlAlchemy session.
    Args:
        None
    Returns:
        None
    """
    try:
        engine = engines[get_database_url()]
    except KeyError:
        engine = create_engine(get_database_url(),
                               pool_recycle=1,
                               pool_size=1,
                               max_overflow=50)
        engines[get_database_url()] = engine
    configure_mappers()
    session = scoped_session(sessionmaker(bind=engine))

    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.remove()
        session.close()


def database_username():
    return getenv('DB_USER')
