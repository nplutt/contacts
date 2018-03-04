import json

from pytest import mark
from unittest import TestCase

from chalice.config import Config
from chalice.local import LocalGateway

from app import app


@mark.usefixtures('migrations', 'users', 'user_data')
class TestCreateUser(TestCase):
    def setUp(self):
        self.lg = LocalGateway(app, Config())

    def test_create_user_returns_code_and_header(self):
        body = dict(emailAddress='nplutt@gmail.com',
                    firstName='Joe',
                    lastName='Schmo',
                    metaData=[
                        dict(dataType='favorite food',
                             data='tacos')
                    ])
        response = self.lg.handle_request(method='POST',
                                          path='/users',
                                          headers={
                                              'Content-Type': 'application/json'
                                          },
                                          body=json.dumps(body))
        assert response['statusCode'] == 201
        assert response['headers']['Location'].index('users')

    def test_create_user_fails_on_conflict(self):
        body = dict(emailAddress='nplutt@gmail.com',
                    firstName='Nick',
                    lastName='Plutt',
                    metaData=[
                        dict(dataType='favorite food',
                             data='tacos')
                    ])
        response = self.lg.handle_request(method='POST',
                                          path='/users',
                                          headers={
                                              'Content-Type': 'application/json'
                                          },
                                          body=json.dumps(body))
        assert response['statusCode'] == 409
