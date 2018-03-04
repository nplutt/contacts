import json

from pytest import mark
from unittest import TestCase

from chalice.config import Config
from chalice.local import LocalGateway

from test.integration.constants import user_id_1

from app import app


@mark.usefixtures('migrations', 'users', 'user_data')
class TestGetUser(TestCase):
    def setUp(self):
        self.lg = LocalGateway(app, Config())

    def test_get_user_basic_works(self):
        response = self.lg.handle_request(method='GET',
                                          path='/users/{user_id}'.format(user_id=user_id_1),
                                          headers=dict(),
                                          body='')
        assert response['statusCode'] == 200
        assert json.loads(response['body'])['data'] == {
            'emailAddress': 'nplutt@gmail.com',
            'firstName': 'Nick',
            'lastName': 'Plutt',
            'metaData': [{'data': '200 Grand Avenue', 'dataType': 'address'}],
            'userId': '9f1b15e8-dca7-427d-816d-44f519010c6b'}

    def test_get_user_raises_not_found(self):
        response = self.lg.handle_request(method='GET',
                                          path='/users/{user_id}'
                                          .format(user_id='7c098790-fe62-4903-8699-0ea958e18602'),
                                          headers=dict(),
                                          body='')
        assert response['statusCode'] == 404
