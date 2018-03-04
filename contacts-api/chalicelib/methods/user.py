import logging

from chalice import Response, BadRequestError, ConflictError, ChaliceViewError, NotFoundError
from marshmallow.exceptions import ValidationError
from psycopg2 import IntegrityError
from sqlalchemy.dialects.postgresql import insert
from uuid import UUID

from chalicelib.models.api import User
from chalicelib.models.db import Users, UserData
from chalicelib.utils import db_session

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def create_user(json_body):
    """
    Inserts user into the users table and insert's the user's meta data
    into the meta_data table.
    Args:
        json_body (dict): a dict representing the json body
    Returns:
        chalice.Response: response object with status code and headers
    Raises:
        BadRequestError: if the provided data is malformed or invalid
        ConflictError: if the user already exists or if the user data is malformed
        ChaliceViewError: if something goes wrong when inserting the records
    """
    try:
        logger.info("Validating json body...")
        user_info, user_meta_data = User(strict=True).load(json_body).data
    except ValidationError as e:
        logger.warning("Invalid json body, received error: {}".format(e))
        raise BadRequestError(e)

    with db_session() as session:
        try:
            user_insert = insert(Users)
            user_data_insert = insert(UserData)

            logger.info("Inserting data into the user table...")
            session.execute(user_insert, user_info)

            logger.info("Inserting data into the user_data table...")
            session.execute(user_data_insert, user_meta_data)

            session.commit()
        except IntegrityError as e:
            logger.warning("User or user data already exists, received error: {}".format(e))
            raise ConflictError(e)
        except Exception as e:
            logger.critical("Something went wrong when retrieving user data, "
                            "received error: {}".format(e))
            raise ChaliceViewError(e)

        logger.info("Data successfully inserted")

    return Response(body=None,
                    status_code=201,
                    headers=dict(Location='/users/{}'.format(str(user_info['user_id']))))


def get_user_info(user_id):
    """
    
    """
    try:
        UUID(user_id)
    except ValueError as e:
        logger.warning("Invalid uuid, received error: {}".format(e))
        raise BadRequestError(e)

    with db_session() as session:
        logger.info("Retrieving user information...")
        result = session.query(
            UserData.data_type,
            UserData.data
        ).filter_by(user_id=user_id)

        if not result:
            logger.warning("User {} was not found in the database".format(user_id))
            raise NotFoundError

        logger.info("User data retrieved")

        return User(strict=True).dump(result).data

