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
        if meta_data:
            meta_data = [dict(data_type=str(d),
                              data=str(meta_data[d])) for d in meta_data]
        data['meta_data'] = meta_data
        return data

    @post_load
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
        import pdb; pdb.set_trace()
        meta_data = data.pop('meta_data', None)
        for d in meta_data:
            d['user_id'] = user_id
        return data, meta_data

    @pre_dump
    def map_meta_data_to_model(self, data):
        model = dict()
        for d in data:
            if d in ['email_address', 'first_name', 'last_name']:
                model[d] = data.pop(d)
        model['meta_data'] = data
        import pdb; pdb.set_trace()

        return model

    @post_dump
    def map_meta_data_array_to_json(self, data):
        meta_data = data.pop('metaData')
        data['metaData'] = dict()
        for d in meta_data:
            data['metaData'][d['dataType']] = d['data']
        import pdb; pdb.set_trace()
        return data
