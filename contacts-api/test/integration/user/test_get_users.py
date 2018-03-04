import json

from pytest import mark
from unittest import TestCase

from chalice.config import Config
from chalice.local import LocalGateway

from app import app


@mark.usefixtures('migrations', 'users', 'user_data')
class TestGetUsersInfo(TestCase):
    def setUp(self):
        self.lg = LocalGateway(app, Config())

    def test_get_users_basic_works(self):
        response = self.lg.handle_request(method='GET',
                                          path='/users?searchText=n',
                                          headers=dict(),
                                          body='')
        assert response['statusCode'] == 200
        assert json.loads(response['body'])['data'] == [
            {'emailAddress': 'nplutt@gmail.com',
             'firstName': 'Nick',
             'lastName': 'Plutt',
             'metaData': [{'data': '200 Grand Avenue', 'dataType': 'address'}],
             'userId': '9f1b15e8-dca7-427d-816d-44f519010c6b'},
            {'emailAddress': 'nohn@gmail.com',
             'firstName': 'John',
             'lastName': 'Bones',
             'metaData': [{'data': '612-584-9642', 'dataType': 'phone number'}],
             'userId': '161e71f0-085c-4607-9631-b8a964f63fc4'}]

    def test_get_users_search_with_spaces(self):
        response = self.lg.handle_request(method='GET',
                                          path='/users?searchText=grand%20avenue',
                                          headers=dict(),
                                          body='')
        assert response['statusCode'] == 200
        assert json.loads(response['body'])['data'] == [
            {'emailAddress': 'nplutt@gmail.com',
             'firstName': 'Nick',
             'lastName': 'Plutt',
             'metaData': [{'data': '200 Grand Avenue', 'dataType': 'address'}],
             'userId': '9f1b15e8-dca7-427d-816d-44f519010c6b'}]

    def test_get_users_search_with_dashes(self):
        response = self.lg.handle_request(method='GET',
                                          path='/users?searchText=612-584',
                                          headers=dict(),
                                          body='')
        assert response['statusCode'] == 200
        assert json.loads(response['body'])['data'] == [
            {'emailAddress': 'chew@gmail.com',
             'firstName': 'Chew',
             'lastName': 'Bacca',
             'metaData': [{'data': '612-584-5496', 'dataType': 'phone number'}],
             'userId': '00042aa2-2575-4746-bf1d-35b9579f05ad'},
            {'emailAddress': 'nohn@gmail.com',
             'firstName': 'John',
             'lastName': 'Bones',
             'metaData': [{'data': '612-584-9642', 'dataType': 'phone number'}],
             'userId': '161e71f0-085c-4607-9631-b8a964f63fc4'}]

    def test_get_users_limit_works(self):
        response = self.lg.handle_request(method='GET',
                                          path='/users?searchText=n&limit=1',
                                          headers=dict(),
                                          body='')
        assert response['statusCode'] == 200
        assert json.loads(response['body'])['data'] == [
            {'emailAddress': 'nohn@gmail.com',
             'firstName': 'John',
             'lastName': 'Bones',
             'metaData': [{'data': '612-584-9642', 'dataType': 'phone number'}],
             'userId': '161e71f0-085c-4607-9631-b8a964f63fc4'}]

    def test_get_users_offset_works(self):
        response = self.lg.handle_request(method='GET',
                                          path='/users?searchText=n&offset=1',
                                          headers=dict(),
                                          body='')
        assert response['statusCode'] == 200
        assert json.loads(response['body'])['data'] == [
            {'emailAddress': 'nplutt@gmail.com',
             'firstName': 'Nick',
             'lastName': 'Plutt',
             'metaData': [{'data': '200 Grand Avenue', 'dataType': 'address'}],
             'userId': '9f1b15e8-dca7-427d-816d-44f519010c6b'}]

    def test_get_users_search_field_filter_works(self):
        response = self.lg.handle_request(method='GET',
                                          path='/users?searchText=n&searchField=address',
                                          headers=dict(),
                                          body='')
        assert response['statusCode'] == 200
        assert len(json.loads(response['body'])['data']) == 0

    def test_get_users_order_works(self):
        response = self.lg.handle_request(method='GET',
                                          path='/users?searchText=nick',
                                          headers=dict(),
                                          body='')
        assert response['statusCode'] == 200
        assert json.loads(response['body'])['data'] == [
            {'emailAddress': 'nplutt@gmail.com',
             'firstName': 'Nick',
             'lastName': 'Plutt',
             'metaData': [{'data': '200 Grand Avenue', 'dataType': 'address'}],
             'userId': '9f1b15e8-dca7-427d-816d-44f519010c6b'}]

    def test_get_users_no_query_params_works(self):
        response = self.lg.handle_request(method='GET',
                                          path='/users',
                                          headers=dict(),
                                          body='')
        assert response['statusCode'] == 200
        assert len(json.loads(response['body'])['data']) == 6
