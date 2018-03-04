from uuid import uuid4

from inflection import underscore
from marshmallow import Schema, fields, post_load, pre_load, pre_dump


class MetaData(Schema):
    data = fields.String(required=True)
    data_type = fields.String(required=True,
                              load_from='dataType',
                              dump_to='dataType')
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
            data (dict): validated json request body
        Returns:
            (dict): user model with all meta data
        """
        if not data.get('metaData'):
            data['metaData'] = []

        for key, value in data.iteritems():
            if key in ['emailAddress', 'firstName', 'lastName']:
                data[key] = value.lower()
            if key is not 'metaData':
                data['metaData'].append(dict(data_type=str(key),
                                             data=str(value)))
        return data

    @post_load(pass_original=False)
    def split_model(self, data):
        """
        Splits model up into user and metadata.  Also sets user id field for the meta data.
        Args:
            data (dict): validated json request body
        Returns:
            (tuple): a tuple containing:
                (dict): user info
                (list of dict): a list of user meta data
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
            data (dict): dictionary containing the results of the query
        Returns:
            dict: valid data that can be mapped to the User model
        """
        user_data = dict()
        results = [d._asdict() for d in data]

        for index, r in enumerate(results):
            user_id = str(r.pop('user_id'))

            if not user_data.get(user_id):
                user_data[user_id] = dict()
            if not user_data[user_id].get('meta_data'):
                user_data[user_id]['meta_data'] = []

            if r['data_type'] in ['emailAddress', 'firstName', 'lastName']:
                user_data[user_id][underscore(r['data_type'])] = r['data']
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


