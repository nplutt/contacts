import logging

from chalice import Chalice

from chalicelib.methods.user import create_user, get_users, get_user, delete_user

app = Chalice(app_name='contacts-api')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@app.route('/xping')
def index():
    return {'hello': 'world'}


@app.route('/users', methods=['POST', 'GET'], cors=True)
def path_user():
    logger.info("Received request at /user...")
    if app.current_request.method == 'POST':
        return create_user(app.current_request.json_body)
    elif app.current_request.method == 'GET':
        return get_users(app.current_request.query_params)


@app.route('/users/{user_id}', methods=['GET', 'DELETE'], cors=True)
def path_user_user_id(user_id):
    logger.info("Received request at /user/{userid}...")
    if app.current_request.method == 'GET':
        return get_user(user_id)
    elif app.current_request.method == 'DELETE':
        return delete_user(user_id)
