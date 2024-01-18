from flask import Flask, request
from flask_restful import Resource, Api, abort
from flaskr.schemas import SessionDataSchema, UserSchema, UserDeletionSchema, UserModificationSchema
import flaskr.database as database
import logging
import sqlalchemy
import psycopg2
import hashlib


def use_schema(schema, need_plaintext_password=False):
    def decorator(func):
        def wrapper(*args):
            assert len(args) == 1, f'Internal error: The resulting function of the decorator {__name__} takes exactly one argument'

            data = args[0]

            abort_if_cant_validate(data=data, schema=schema)

            if need_plaintext_password == False:
                data = hide_plaintext_password(data=data)

            data = schema.prune(data)

            func(data)
        return wrapper
    return decorator


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


def abort_if_cant_validate(data, schema):
    logging.info(f'Trying to validate {data} with {schema.__name__}...')

    validation_result = schema.validate(data)

    if validation_result != None:
        abort(404, message=str(validation_result))
    
    logging.info('Valid!')


def abort_if_password_isnt_complex(password):
    return True # TODO: implement password complexity check


def get_salted_password(password, unqiue_salt_source):
    part1 = str.encode(password)
    part2 = str.encode(hashlib.sha256(str.encode(unqiue_salt_source)).hexdigest())
    return part1 + part2


def get_salted_hash(password, unqiue_salt_source):
    return hashlib.sha256(get_salted_password(password=password, unqiue_salt_source=unqiue_salt_source)).hexdigest()


def hide_plaintext_password(data):
    if data.get('password') is None:
        return data
    
    data.update(
        password=get_salted_hash(
            password=data.get('password'),
            unqiue_salt_source=data.get('username')
        )
    )

    return data

@use_schema(SessionDataSchema)
def login(session_data):
    abort_if_cant_authenticate_user(
        username=session_data.get('username'),
        password=session_data.get('password')
    )

    try:
        database.insert_onlineuser(SessionDataSchema.prune(session_data))
    except Exception as e:
        abort(500, message=repr(e))


@use_schema(SessionDataSchema)
def logout(session_data):
    abort_if_cant_authenticate_user(
        username=session_data.get('username'),
        password=session_data.get('password')
    )

    try:
        database.delete_onlineuser(SessionDataSchema.prune(session_data))
    except Exception as e:
        abort(500, message=repr(e))


@use_schema(UserSchema, need_plaintext_password=True)
def create_user(user):
    abort_if_password_isnt_complex(password=user.get('password'))

    user = hide_plaintext_password(data=user)

    try:
        database.insert_user(user)
    except Exception as e:
        abort(500, message=repr(e))


@use_schema(UserDeletionSchema)
def delete_user(user_deletion):
    abort_if_cant_authenticate_user(
        username=user_deletion.get('username'),
        password=user_deletion.get('password')
    )

    try:
        try:
            database.delete_onlineuser(user_deletion)
        except Exception:
            pass
        
        database.delete_user(user_deletion)
    except Exception as e:
        abort(500, message=repr(e))


@use_schema(UserModificationSchema)
def modify_user(user_modification):
    abort_if_cant_authenticate_user(
        username=user_modification.get('username'),
        password=user_modification.get('password')
    )

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
