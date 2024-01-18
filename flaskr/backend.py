from flask import Flask, request
from flask_restful import Resource, Api, abort
from flaskr.schemas import SessionDataSchema, UserSchema, UserDeletionSchema, UserModificationSchema
import flaskr.database as database
import logging
import sqlalchemy
import psycopg2


def user_exists(username):
    result = database.get_user_by_username(username=username)

    if result == None:
        return False
    
    return True


def abort_if_cant_authenticate_user(username, password):
    logging.info(f'Trying to authenticate with username={username} and password={password}...')

    if user_exists(username=username) == False:
        abort(401, message='Wrong username')
    
    result = database.get_user_by_credentials(username=username, password=password)

    if result == None:
        abort(401, message=f'Wrong credentials: {username} | {password}')
    
    logging.info('Authentication successful!')


def modify_user(user_modification):
    try:
        database.modify_user(user_modification)
    except Exception as e:
        abort(500, message=repr(e))


def abort_if_cant_validate(data, schema):
    logging.info(f'Trying to validate {data} with {schema.__name__}...')

    validation_result = schema.validate(data)

    if validation_result != None:
        abort(404, message=str(validation_result))
    
    logging.info('Valid!')


def login(session_data):
    abort_if_cant_validate(session_data, SessionDataSchema)

    session_data = SessionDataSchema.prune(session_data)

    abort_if_cant_authenticate_user(
        username=session_data.get('username'),
        password=session_data.get('password')
    )

    try:
        database.insert_onlineuser(SessionDataSchema.prune(session_data))
    except Exception as e:
        abort(500, message=repr(e))


def logout(session_data):
    abort_if_cant_validate(session_data, SessionDataSchema)

    session_data = SessionDataSchema.prune(session_data)

    abort_if_cant_authenticate_user(
        username=session_data.get('username'),
        password=session_data.get('password')
    )

    try:
        database.delete_onlineuser(SessionDataSchema.prune(session_data))
    except Exception as e:
        abort(500, message=repr(e))


def create_user(user):
    user = user

    abort_if_cant_validate(user, UserSchema)

    user = UserSchema.prune(user)

    try:
        database.insert_user(user)
    except Exception as e:
        abort(500, message=repr(e))


def delete_user(user_deletion):
    abort_if_cant_validate(user_deletion, UserDeletionSchema)

    user_deletion = UserDeletionSchema.prune(user_deletion)
    
    try:
        database.delete_user(user_deletion)
    except Exception as e:
        abort(500, message=repr(e))


def update_user(user_modification):
    abort_if_cant_validate(user_modification, UserModificationSchema)

    user_modification = UserModificationSchema.prune(user_modification)

    try:
        database.modify_user(user_modification)
    except Exception as e:
        abort(500, message=repr(e))


def list_users():
    try:
        result = database.list_users()
    except Exception as e:
        abort(500, message=repr(e))

    return result


def list_onlineusers():
    try:
        result = database.list_onlineusers()
    except Exception as e:
        abort(500, message=repr(e))
    
    return result
