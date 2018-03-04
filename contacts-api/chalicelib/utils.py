from contextlib import contextmanager
from os import getenv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.engine.url import URL


def get_database_url():
    """
    Generates the postgres connection url.
    Args:
        None
    Returns:
        sqlalchemy.engine.url.URL: The connection url
    """
    return URL(drivername='postgres',
               username=getenv('DB_USER'),
               password=getenv('DB_PASSWORD'),
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
    engine = create_engine(get_database_url(),
                           pool_recycle=1,
                           pool_size=1,
                           max_overflow=50)
    session = scoped_session(sessionmaker(bind=engine))

    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.remove()
