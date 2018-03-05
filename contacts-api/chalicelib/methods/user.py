import logging
from urllib import unquote
from uuid import UUID

from chalice import Response, BadRequestError, ConflictError, ChaliceViewError, NotFoundError
from marshmallow.exceptions import ValidationError
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy_searchable import search

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


def get_users(query_params):
    """
    Retrieves data for all user's who have an attribute that matches the
    searchText
    Args:
        query_params (dict): a dictionary containing all of the query params
    Returns:
        list: list of dicts containing users information
    Raises:
        None
    """
    query_params = query_params if query_params else dict()
    logger.info("Retrieving user information with query params of {}..."
                .format(query_params))

    limit = query_params.get('limit', 25)
    offset = query_params.get('offset', 0)
    search_text = query_params.get('searchText')
    search_field = query_params.get('searchField')

    with db_session() as session:
        logger.info("Constructing text search sub query...")
        search_sub_query = session.query(UserData.user_id)

        if search_text:
            logger.info("Searching fields for text...")
            search_text = unquote(search_text)
            search_sub_query = search(search_sub_query, search_text, sort=True)
        if search_field:
            logger.info("Filtering results by searched field...")
            search_field = unquote(search_field)
            search_sub_query = search_sub_query.filter_by(data_type=search_field)

        logger.info("Applying offset and limit on subquery...")
        search_sub_query = search_sub_query.distinct().offset(offset).limit(limit).subquery()

        logger.info("Retrieving users info from database...")
        result = session.query(
            UserData.data_type,
            UserData.data,
            UserData.user_id
        ).filter(UserData.user_id == search_sub_query.c.user_id)

        logger.info("Users data retrieved")
        users_data = User(strict=True).dump(result, many=True).data

        return dict(
            meta=dict(
                limit=limit,
                offset=offset,
                count=len(users_data)
            ),
            data=users_data
        )


def get_user(user_id):
    """
    Retrieves all of a given users data
    Args:
        user_id (str): a users uuid
    Returns:
        dict: a dictionary containing all of a users information
    Raises:
        BadRequestError: if the user_id isn't a valid uuid
        NotFoundError: if no record can be found for the given user id
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
            UserData.data,
            UserData.user_id
        ).filter_by(user_id=user_id)

        if not result.count():
            logger.warning("User {} was not found in the database".format(user_id))
            raise NotFoundError

        logger.info("User data retrieved")
        user_data = User(strict=True).dump(result).data

        return dict(
            meta=dict(
                limit=1,
                offset=0,
                count=1
            ),
            data=user_data
        )


def delete_user(user_id):
    """
    Deletes user's records from the database
    Args:
        user_id (str): a users uuid
    Returns:
        None
    Raises:
        BadRequestError: if the user_id isn't a valid uuid
        NotFoundError: if no record can be found for the given user id
    """
    try:
        UUID(user_id)
    except ValueError as e:
        logger.warning("Invalid uuid, received error: {}".format(e))
        raise BadRequestError(e)

    with db_session() as session:
        logger.info("Deleting user data from users and user_data...")
        count = session.query(Users).filter_by(user_id=user_id).delete()

        if not count:
            logger.warning("User {} was not found in the database".format(user_id))
            raise NotFoundError

        return Response(body=None,
                        status_code=204,
                        headers=dict())
