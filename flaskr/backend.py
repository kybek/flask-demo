from flask import Flask, request
from flask_restful import Resource, Api, abort
from flaskr.schemas import LoginFormSchema, SessionDataSchema, UserDataSchema, UserDeletionSchema, UserModificationSchema, TokenDataSchema, NewUserDataSchema
import flaskr.database as database
import logging
import sqlalchemy
import psycopg2
import hashlib
import datetime as dt
import re
import secrets


def use_schema(schema, need_plaintext_password=False):
    def decorator(func):
        def wrapper(*args):
            assert len(args) == 1, f'Internal error: The resulting function of the decorator {__name__} takes exactly one argument'

            data = args[0]

            logging.info(f'Using schema {schema.__name__} on data {str(data)}')

            abort_if_cant_validate(data=data, schema=schema)

            if need_plaintext_password == False:
                data = hide_plaintext_password(data=data)
                logging.info(f'Hided the plaintext password in data: {data}')


            data = schema.serialize(data)

            logging.info('Finished validating & cleaning data!')
            logging.info(f'Calling {str(func.__name__)} with {data}')

            return func(data)
        return wrapper
    return decorator


def user_exists(username):
    result = database.get_user_by_username(username=username)

    if result == None:
        return False
    
    return True


def session_exists(token):
    result = database.get_session_by_token(token=token)

    if result == None:
        return False
    
    return True


def abort_if_cant_login_with_credentials(username, password):
    logging.info(f'Trying to authenticate with username={username} and password={password}...')

    if user_exists(username=username) == False:
        abort(401, message='Wrong username')
    
    result = database.get_user_by_credentials(username=username, password=password)

    if result == None:
        abort(401, message=f'Wrong credentials: {username} | {password}')
    
    logging.info('Authentication successful!')


def abort_if_cant_login_with_token(token):
    logging.info(f'Trying to authenticate with token={token}...')

    if session_exists(token=token) == False:
        abort(401, message=f'Invalid token: {token}')
    
    logging.info('Authentication successful!')


def abort_if_cant_validate(data, schema):
    logging.info(f'Trying to validate {data} with {schema.__name__}...')

    validation_result = schema.validate(data)

    if validation_result != None:
        abort(404, message=str(validation_result))
    
    logging.info('Valid!')


def abort_if_password_isnt_complex(password):
    if re.match(r"^[a-zA-Z0-9]{8,}$", password):
        return True
    
    abort(401, message='Password is too weak (At least 8 characters, [a-zA-Z0-9])')


def get_salted_password(password, unqiue_salt_source):
    part1 = str.encode(password)
    part2 = str.encode(hashlib.sha256(str.encode(unqiue_salt_source)).hexdigest())
    return part1 + part2


def get_salted_hash(password, unqiue_salt_source):
    return hashlib.sha256(get_salted_password(password=password, unqiue_salt_source=unqiue_salt_source)).hexdigest()


def hide_plaintext_password(data):
    if data.get('password') is None or data.get('username') is None:
        return data
    
    data.update(
        password=get_salted_hash(
            password=data.get('password'),
            unqiue_salt_source=data.get('username')
        )
    )

    return data


def generate_token():
    return secrets.token_urlsafe(16)


@use_schema(LoginFormSchema)
def login(login_form):
    abort_if_cant_login_with_credentials(
        username=login_form.get('username'),
        password=login_form.get('password')
    )

    user = database.get_user_by_credentials(
        username=login_form.get('username'),
        password=login_form.get('password')
    )

    if user == None:
        return abort(500, message='No such user.')

    if database.get_session_by_credentials(
        username=login_form.get('username'),
        password=login_form.get('password')
    ) != None:
        return abort(500, message='The user is already logged in.')

    session_data = SessionDataSchema.serialize({
        'created_at': dt.datetime.now().isoformat(),
        'ip': login_form.get('ip'),
        'user_id': user.id,
        'token': generate_token()
    })

    try:
        database.insert_session(session_data)
    except Exception as e:
        abort(500, message=repr(e))
    
    logging.debug(session_data)

    return session_data.get('token')


@use_schema(TokenDataSchema)
def logout(token_data):
    abort_if_cant_login_with_token(
        token=token_data.get('token')
    )

    try:
        database.delete_session(token_data.get('token'))
    except Exception as e:
        abort(500, message=repr(e))


@use_schema(NewUserDataSchema, need_plaintext_password=True)
def create_user(user):
    abort_if_password_isnt_complex(password=user.get('password'))

    user = hide_plaintext_password(data=user)

    try:
        database.insert_user(user)
    except Exception as e:
        abort(500, message=repr(e))


@use_schema(UserDeletionSchema)
def delete_user(user_deletion):
    abort_if_cant_login_with_token(
        token=user_deletion.get('token')
    )

    try:
        try:
            database.delete_session(token=user_deletion.get('token'))
        except Exception:
            pass
        
        session = database.get_session_by_token(user_deletion.get('token'))
        database.delete_user(user_deletion.get('id'))
    except Exception as e:
        abort(500, message=repr(e))


@use_schema(UserModificationSchema)
def modify_user(user_modification):
    abort_if_cant_login_with_token(
        token=user_modification.get('token')
    )

    try:
        database.modify_user(UserDataSchema.serialize(user_modification))
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
        result = database.list_sessions()
    except Exception as e:
        abort(500, message=repr(e))
    
    return result
