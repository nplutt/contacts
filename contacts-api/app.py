import logging

from chalice import Chalice

from chalicelib.methods.user import create_user, get_user_info

app = Chalice(app_name='contacts-api')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@app.route('/')
def index():
    return {'hello': 'world'}


@app.route('/users', methods=['POST'], cors=True)
def path_user():
    logger.info("Received request at /user...")
    if app.current_request.method == 'POST':
        return create_user(app.current_request.json_body)


@app.route('/users/{user_id}', methods=['GET'], cors=True)
def path_user_user_id(user_id):
    logger.info("Received request at /user/{userid}...")
    if app.current_request.method == 'GET':
        return get_user_info(user_id)
