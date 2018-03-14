import sys

from os import environ, getcwd, getenv
from time import sleep

from alembic import command
from alembic.config import Config
from docker import from_env
from psycopg2 import OperationalError, connect
from pytest import fixture

try:
    from chalicelib.models.db import Users, UserData
    from chalicelib.singletons import Base
    from chalicelib.utils import get_database_url, db_session
    from test.integration.constants import (user_id_1, user_id_2, user_id_3, user_id_4, user_id_5,
                                            user_id_6)
except ImportError:
    sys.path.append(getcwd())
    from test.integration.constants import (user_id_1, user_id_2, user_id_3, user_id_4, user_id_5,
                                            user_id_6)
    from chalicelib.models.db import Users, UserData
    from chalicelib.singletons import Base
    from chalicelib.utils import get_database_url, db_session

environ['DB_HOST'] = '127.0.0.1'
environ['MASTER_DB_USER'] = 'master_local_docker_user'
environ['MASTER_DB_PASSWORD'] = 'master_local_docker_password'
environ['DB_USER'] = 'local_docker_user'
environ['DB_PASSWORD'] = 'local_docker_password'
environ['DB_NAME'] = 'postgres'

docker_client = from_env()


@fixture(scope='session', autouse=True)
def postgres(request):
    print('Pulling postgres image...\n')
    docker_client.api.pull('postgres:latest')
    print('Starting postgres...\n')
    container = docker_client.containers.run('postgres:latest',
                                             detach=True,
                                             ports={'5432/tcp': ('127.0.0.1', 0)},
                                             environment={'POSTGRES_PASSWORD': getenv('MASTER_DB_PASSWORD'),
                                                          'POSTGRES_USER': getenv('MASTER_DB_USER')})
    environ['DB_PORT'] = docker_client.api.port(container.id, '5432')[0]['HostPort']

    for i in range(0, 20):
        try:
            connect(host=getenv('DB_HOST'),
                    user=getenv('MASTER_DB_USER'),
                    password=getenv('MASTER_DB_PASSWORD'),
                    database=getenv('DB_NAME'),
                    port=getenv('DB_PORT'))
            print('Database is running on port {}\n\n'.format(getenv('DB_PORT')))
            break
        except OperationalError:
            print('.')
            sleep(3)
    else:
        print('Database failed to start\n')

    def teardown():
        print('Killing and removing docker container\n')
        container.kill()
        container.remove(force=True)

    request.addfinalizer(teardown)


@fixture(scope='session')
def migrations(request):
    print('Running alembic migrations...\n')
    alembic_config = Config('alembic.ini')

    def teardown():
        print('Downgrading alembic migrations...\n')
        command.downgrade(alembic_config, 'base')

    request.addfinalizer(teardown)
    command.upgrade(alembic_config, 'head')


@fixture(scope='function')
def users(request):
    data = [
        Users(user_id=user_id_1,
              email_address='nplutt@gmail.com',
              first_name='nick',
              last_name='plutt'),
        Users(user_id=user_id_2,
              email_address='john@gmail.com',
              first_name='john',
              last_name='bones'),
        Users(user_id=user_id_3,
              email_address='tim@gmail.com',
              first_name='tim',
              last_name='allen'),
        Users(user_id=user_id_4,
              email_address='chew@gmail.com',
              first_name='chew',
              last_name='bacca'),
        Users(user_id=user_id_5,
              email_address='luke@gmail.com',
              first_name='luke',
              last_name='skywalker'),
        Users(user_id=user_id_6,
              email_address='mace@gmail.com',
              first_name='mace',
              last_name='weindu')
    ]

    with db_session() as session:
        session.add_all(data)
        session.commit()

    def teardown():
        with db_session() as session:
            session.query(Users).delete()
            session.commit()

    request.addfinalizer(teardown)


@fixture(scope='function')
def user_data(request):
    data = [
        UserData(field_type='emailAddress',
                 field_data='nplutt@gmail.com',
                 user_id=user_id_1),
        UserData(field_type='firstName',
                 field_data='Nick',
                 user_id=user_id_1),
        UserData(field_type='lastName',
                 field_data='Plutt',
                 user_id=user_id_1),
        UserData(field_type='address',
                 field_data='200 Grand Avenue',
                 user_id=user_id_1),
        UserData(field_type='emailAddress',
                 field_data='nohn@gmail.com',
                 user_id=user_id_2),
        UserData(field_type='firstName',
                 field_data='John',
                 user_id=user_id_2),
        UserData(field_type='lastName',
                 field_data='Bones',
                 user_id=user_id_2),
        UserData(field_type='phone number',
                 field_data='612-584-9642',
                 user_id=user_id_2),
        UserData(field_type='emailAddress',
                 field_data='tim@gmail.com',
                 user_id=user_id_3),
        UserData(field_type='firstName',
                 field_data='Tim',
                 user_id=user_id_3),
        UserData(field_type='lastName',
                 field_data='Allen',
                 user_id=user_id_3),
        UserData(field_type='emailAddress',
                 field_data='chew@gmail.com',
                 user_id=user_id_4),
        UserData(field_type='firstName',
                 field_data='Chew',
                 user_id=user_id_4),
        UserData(field_type='lastName',
                 field_data='Bacca',
                 user_id=user_id_4),
        UserData(field_type='phone number',
                 field_data='612-584-5496',
                 user_id=user_id_4),
        UserData(field_type='emailAddress',
                 field_data='luke@gmail.com',
                 user_id=user_id_5),
        UserData(field_type='firstName',
                 field_data='Luke',
                 user_id=user_id_5),
        UserData(field_type='lastName',
                 field_data='Skywalker',
                 user_id=user_id_5),
        UserData(field_type='emailAddress',
                 field_data='mace@gmail.com',
                 user_id=user_id_6),
        UserData(field_type='firstName',
                 field_data='Mace',
                 user_id=user_id_6),
        UserData(field_type='lastName',
                 field_data='Windu',
                 user_id=user_id_6)
    ]

    with db_session() as session:
        session.add_all(data)
        session.commit()

    def teardown():
        with db_session() as session:
            session.query(UserData).delete()
            session.commit()

    request.addfinalizer(teardown)
