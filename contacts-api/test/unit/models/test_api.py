from unittest import TestCase
from uuid import UUID

from mock import MagicMock

from chalicelib.models.api import User


class TestUserModel(TestCase):
    def test_unpack_meta_data_works_no_meta_data(self):
        data = {'emailAddress': 'nplutt@gmail.com',
                'firstName': 'Nick',
                'lastName': 'Plutt'}

        result = User().unpack_meta_data(data=data)

        assert result == {'emailAddress': 'nplutt@gmail.com',
                          'firstName': 'nick',
                          'lastName': 'plutt',
                          'metaData': [{'fieldData': 'Plutt', 'fieldType': 'lastName'},
                                       {'fieldData': 'nplutt@gmail.com', 'fieldType': 'emailAddress'},
                                       {'fieldData': 'Nick', 'fieldType': 'firstName'}]}

    def test_unpack_meta_data_works_with_meta_data(self):
        data = {'emailAddress': 'nplutt@gmail.com',
                'firstName': 'Nick',
                'lastName': 'Plutt',
                'metaData': [
                    {'fieldData': 'tacos',
                     'fieldType': 'favorite food'}
                ]}

        result = User().unpack_meta_data(data=data)

        assert result == {'emailAddress': 'nplutt@gmail.com',
                          'firstName': 'nick',
                          'lastName': 'plutt',
                          'metaData': [{'fieldData': 'tacos', 'fieldType': 'favorite food'},
                                       {'fieldData': 'Plutt', 'fieldType': 'lastName'},
                                       {'fieldData': 'nplutt@gmail.com', 'fieldType': 'emailAddress'},
                                       {'fieldData': 'Nick', 'fieldType': 'firstName'}]}

    def test_split_model_works(self):
        data = {'user_id': UUID('befed934-3f35-4b81-ac41-d1ca8039daeb'),
                'email_address': 'nplutt@gmail.com',
                'first_name': 'nick',
                'last_name': 'plutt',
                'meta_data': [
                    {'field_data': 'tacos', 'field_type': 'favorite food'},
                    {'field_data': 'Plutt', 'field_type': 'lastName'},
                    {'field_data': 'nplutt@gmail.com', 'field_type': 'emailAddress'},
                    {'field_data': 'Nick', 'field_type': 'firstName'}
                ]
                }

        data_result, meta_data_result = User().split_model(data=data)

        assert data_result == {'email_address': 'nplutt@gmail.com',
                               'first_name': 'nick',
                               'last_name': 'plutt',
                               'user_id': UUID('befed934-3f35-4b81-ac41-d1ca8039daeb')}

        assert meta_data_result == [{'field_data': 'tacos',
                                     'field_type': 'favorite food',
                                     'user_id': UUID('befed934-3f35-4b81-ac41-d1ca8039daeb')},
                                    {'field_data': 'Plutt',
                                     'field_type': 'lastName',
                                     'user_id': UUID('befed934-3f35-4b81-ac41-d1ca8039daeb')},
                                    {'field_data': 'nplutt@gmail.com',
                                     'field_type': 'emailAddress',
                                     'user_id': UUID('befed934-3f35-4b81-ac41-d1ca8039daeb')},
                                    {'field_data': 'Nick',
                                     'field_type': 'firstName',
                                     'user_id': UUID('befed934-3f35-4b81-ac41-d1ca8039daeb')}]

    def test_map_meta_data_to_model_many_works(self):
        data = [{'field_data': 'nplutt@gmail.com',
                 'field_type': 'emailAddress',
                 'user_id': UUID('9f1b15e8-dca7-427d-816d-44f519010c6b')},
                {'field_data': 'Nick',
                 'field_type': 'firstName',
                 'user_id': UUID('9f1b15e8-dca7-427d-816d-44f519010c6b')},
                {'field_data': 'Plutt',
                 'field_type': 'lastName',
                 'user_id': UUID('9f1b15e8-dca7-427d-816d-44f519010c6b')},
                {'field_data': '200 Grand Avenue',
                 'field_type': 'address',
                 'user_id': UUID('9f1b15e8-dca7-427d-816d-44f519010c6b')},
                {'field_data': 'nohn@gmail.com',
                 'field_type': 'emailAddress',
                 'user_id': UUID('161e71f0-085c-4607-9631-b8a964f63fc4')},
                {'field_data': 'John',
                 'field_type': 'firstName',
                 'user_id': UUID('161e71f0-085c-4607-9631-b8a964f63fc4')},
                {'field_data': 'Bones',
                 'field_type': 'lastName',
                 'user_id': UUID('161e71f0-085c-4607-9631-b8a964f63fc4')},
                {'field_data': '612-584-9642',
                 'field_type': 'phone number',
                 'user_id': UUID('161e71f0-085c-4607-9631-b8a964f63fc4')}]

        input_data = []

        for d in data:
            record = MagicMock()
            record._asdict = MagicMock()
            record._asdict.return_value = d
            input_data.append(record)

        result = User().map_meta_data_to_model(data=input_data, pass_many=True)

        assert result == [{'user_id': '9f1b15e8-dca7-427d-816d-44f519010c6b',
                           'email_address': 'nplutt@gmail.com',
                           'first_name': 'Nick',
                           'last_name': 'Plutt',
                           'meta_data': [{'field_data': '200 Grand Avenue',
                                          'field_type': 'address'}]
                           },
                          {'user_id': '161e71f0-085c-4607-9631-b8a964f63fc4',
                           'email_address': 'nohn@gmail.com',
                           'first_name': 'John',
                           'last_name': 'Bones',
                           'meta_data': [{'field_data': '612-584-9642',
                                          'field_type': 'phone number'}]
                           }]

    def test_map_meta_data_to_model_one_works(self):
        data = [{'field_data': 'nplutt@gmail.com',
                 'field_type': 'emailAddress',
                 'user_id': UUID('9f1b15e8-dca7-427d-816d-44f519010c6b')},
                {'field_data': 'Nick',
                 'field_type': 'firstName',
                 'user_id': UUID('9f1b15e8-dca7-427d-816d-44f519010c6b')},
                {'field_data': 'Plutt',
                 'field_type': 'lastName',
                 'user_id': UUID('9f1b15e8-dca7-427d-816d-44f519010c6b')},
                {'field_data': '200 Grand Avenue',
                 'field_type': 'address',
                 'user_id': UUID('9f1b15e8-dca7-427d-816d-44f519010c6b')}]

        input_data = []

        for d in data:
            record = MagicMock()
            record._asdict = MagicMock()
            record._asdict.return_value = d
            input_data.append(record)

        result = User().map_meta_data_to_model(data=input_data, pass_many=False)

        assert result == {'user_id': '9f1b15e8-dca7-427d-816d-44f519010c6b',
                          'email_address': 'nplutt@gmail.com',
                          'first_name': 'Nick',
                          'last_name': 'Plutt',
                          'meta_data': [{'field_data': '200 Grand Avenue',
                                         'field_type': 'address'}]
                          }
