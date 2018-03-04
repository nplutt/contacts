from copy import deepcopy
from inflection import underscore
from uuid import uuid4
from marshmallow import Schema, fields, post_load, pre_load, post_dump, pre_dump


class MetaData(Schema):
    data = fields.String(required=True)
    data_type = fields.String(required=True,
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
    # meta_data = fields.Raw()
    meta_data = fields.Nested(MetaData,
                              many=True,
                              dump_to='metaData')

    @pre_load
    def unpack_meta_data(self, data):
        """
        Unpacks the dictionary of meta data fields for a given user and formats
        it for the database.
        Args:
            data (dict): validated json request body
        Returns:
            (dict): user model with structured
        """
        meta_data = data.pop('metaData', None)
        flat_data = deepcopy(data)
        flat_data.update(meta_data)
        meta_data = [dict(data_type=str(d), data=str(flat_data[d])) for d in flat_data]
        data['meta_data'] = meta_data
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
        meta_data = data.pop('meta_data', None)
        for d in meta_data:
            d['user_id'] = user_id
        return data, meta_data

    @pre_dump
    def map_meta_data_to_model(self, data):
        model = dict()
        removed_indexes = []
        results = [d._asdict() for d in data.all()]

        for index, r in enumerate(results):
            if r['data_type'] in ['emailAddress', 'firstName', 'lastName']:
                model[underscore(r['data_type'])] = r['data']
                removed_indexes.append(index)

        model['meta_data'] = results

        for count, i in enumerate(removed_indexes):
            model['meta_data'].pop(i - count)

        return model

    @post_dump
    def map_meta_data_array_to_json(self, data):
        meta_data = data.pop('metaData')
        data['metaData'] = dict()
        for d in meta_data:
            data['metaData'][d['dataType']] = d['data']
        return data
