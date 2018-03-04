from pytest import mark
from unittest import TestCase


@mark.usefixtures('migrations', 'users', 'user_data')
class TestDatabase(TestCase):

    def test_data(self):
        assert 1 == 1
