from unittest import TestCase

from chalice.config import Config
from chalice.local import LocalGateway
from pytest import mark

from app import app
from test.integration.constants import user_id_1


@mark.usefixtures('migrations', 'users', 'user_data')
class TestDeleteUser(TestCase):
    def setUp(self):
        self.lg = LocalGateway(app, Config())

    def test_delete_user(self):
        response_1 = self.lg.handle_request(method='DELETE',
                                            path='/users/{user_id}'
                                            .format(user_id=user_id_1),
                                            headers=dict(),
                                            body='')

        assert response_1['statusCode'] == 204

        response_2 = self.lg.handle_request(method='GET',
                                            path='/users/{user_id}'
                                            .format(user_id=user_id_1),
                                            headers=dict(),
                                            body='')

        assert response_2['statusCode'] == 404

    def test_delete_non_existent_user(self):
        response_1 = self.lg.handle_request(method='DELETE',
                                            path='/users/{user_id}'
                                            .format(user_id='7c098790-fe62-4903-8699-0ea958e18602'),
                                            headers=dict(),
                                            body='')

        assert response_1['statusCode'] == 404
