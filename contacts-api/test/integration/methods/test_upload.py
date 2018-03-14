# import json
#
# from mock import patch
# from pytest import mark
# from unittest import TestCase
#
# from chalice.config import Config
# from chalice.local import LocalGateway
#
# from app import app
#
#
# @mark.usefixtures('migrations', 'users', 'user_data')
# class TestCreateUser(TestCase):
#     def setUp(self):
#         self.lg = LocalGateway(app, Config())
#
#     @patch('chalicelib.methods.upload.boto3.upload_file')
#     def test_upload_file_uploads_to_s3(self):
#
#     def test_create_user_returns_code_and_header(self):
#         body = dict(emailAddress='nplutt@gmail.com',
#                     firstName='Joe',
#                     lastName='Schmo',
#                     metaData=[
#                         dict(fieldType='favorite food',
#                              data='tacos')
#                     ])
#         response_1 = self.lg.handle_request(method='POST',
#                                             path='/users',
#                                             headers={
#                                                 'Content-Type': 'application/json'
#                                             },
#                                             body=json.dumps(body))
#         assert response_1['statusCode'] == 201
#         assert response_1['headers']['Location'].index('users')
#
#         response_2 = self.lg.handle_request(method='GET',
#                                             path=response_1['headers']['Location'],
#                                             headers=dict(),
#                                             body='')
#
#         assert response_2['statusCode'] == 200
#
#         body['userId'] = ANY
#         assert json.loads(response_2['body'])['data'] == body
