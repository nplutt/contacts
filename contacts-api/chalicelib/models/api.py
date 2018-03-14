from uuid import uuid4

from inflection import underscore
from marshmallow import Schema, fields, post_load, pre_load, pre_dump


class MetaData(Schema):
    field_data = fields.String(required=True,
                               load_from='fieldData',
                               dump_to='fieldData')
    field_type = fields.String(required=True,
                               load_from='fieldType',
                               dump_to='fieldType')
    user_id = fields.UUID(required=False,
                          load_from='userId',
                          dump_to='userId')


class User(Schema):
    user_id = fields.UUID(required=False,
                          load_from='userId',
                          dump_to='userId',
                          missing=uuid4)
    email_address = fields.String(required=True,
                                  load_from='emailAddress',
                                  dump_to='emailAddress')
    first_name = fields.String(required=True,
                               load_from='firstName',
                               dump_to='firstName')
    last_name = fields.String(required=True,
                              load_from='lastName',
                              dump_to='lastName')
    meta_data = fields.Nested(MetaData,
                              many=True,
                              load_from='metaData',
                              dump_to='metaData')

    @pre_load
    def unpack_meta_data(self, data):
        """
        Unpacks the the firstName, lastName, and emailAddress fields and
        adds them to the metaData list.
        Args:
            data (dict): {'emailAddress': 'nplutt@gmail.com',
                          'firstName': 'Nick',
                          'lastName': 'Plutt',
                          'metaData': [
                              {'fieldData': 'tacos',
                              'fieldType': 'favorite food'}
                              ]
                          }

        Returns:
            (dict): {'emailAddress': 'nplutt@gmail.com',
                     'firstName': 'nick',
                     'lastName': 'plutt',
                     'metaData': [
                         {'fieldData': 'tacos', 'fieldType': 'favorite food'},
                         {'fieldData': 'Plutt', 'fieldType': 'lastName'},
                         {'fieldData': 'nplutt@gmail.com', 'fieldType': 'emailAddress'},
                         {'fieldData': 'Nick', 'fieldType': 'firstName'}
                         ]
                     }
        """
        if not data.get('metaData'):
            data['metaData'] = []

        for key, value in data.iteritems():
            if key in ['emailAddress', 'firstName', 'lastName']:
                data[key] = value.lower()
            if key != 'metaData':
                data['metaData'].append(dict(fieldType=str(key),
                                             fieldData=str(value)))

        return data

    @post_load(pass_original=False)
    def split_model(self, data):
        """
        Splits model up into user and metadata and sets user id field for the meta data.
        Args:
            data (dict): {'user_id': UUID('d18203ab-3311-4e44-aedf-2a9170188266'),
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

        Returns:
            (tuple): a tuple containing:

                (dict): {'email_address': 'nplutt@gmail.com',
                         'first_name': 'nick',
                         'last_name': 'plutt',
                         'user_id': UUID('befed934-3f35-4b81-ac41-d1ca8039daeb')}

                (list of dict): [{'field_data': 'tacos',
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
        """
        user_id = data.get('user_id')
        meta_data = data.pop('meta_data')
        for d in meta_data:
            d['user_id'] = user_id

        return data, meta_data

    @pre_dump(pass_many=True)
    def map_meta_data_to_model(self, data, pass_many):
        """
        Maps a user's meta data to the return model with email address,
        first name, and last name
        Args:
            data (dict): [{'field_data': 'nplutt@gmail.com',
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
        Returns:
            dict: [{'user_id': '9f1b15e8-dca7-427d-816d-44f519010c6b',
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
        """
        user_data = dict()
        results = [d._asdict() for d in data]

        for index, r in enumerate(results):
            user_id = str(r.pop('user_id'))

            if not user_data.get(user_id):
                user_data[user_id] = dict()
            if not user_data[user_id].get('meta_data'):
                user_data[user_id]['meta_data'] = []

            if r['field_type'] in ['emailAddress', 'firstName', 'lastName']:
                user_data[user_id][underscore(r['field_type'])] = r['field_data']
            else:
                user_data[user_id]['meta_data'].append(r)

        user_data_list = []
        for key, value in user_data.iteritems():
            value['user_id'] = key
            user_data_list.append(value)

        if pass_many:
            return user_data_list
        else:
            return user_data_list[0]


