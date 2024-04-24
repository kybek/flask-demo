import re
import logging
from flask_restful import abort


def required(check):
    logging.info(f'Checking required field {str(check.__name__).removeprefix("check_")} with: {check.__name__}')

    def wrapper(*args):
        assert len(args) >= 1, f'Internal error: The resulting function of the decorator {__name__} takes at least one argument'

        data = args[0]

        assert data != None, f'The {str(check.__name__).removeprefix("check_")} field can\'t be null.'

        logging.info(f'Data isn\'t empty, sending to {check.__name__}...')
        check(data)
        logging.info('Passed the check!')

    return wrapper


def optional(check):
    logging.info(f'Checking optional field {str(check.__name__).removeprefix("check_")} with: {check.__name__}')

    def wrapper(*args):
        assert len(args) >= 1, f'Internal error: The resulting function of the decorator {__name__} takes at least one argument'

        data = args[0]

        if data == None:
            logging.info('Data is empty, skipping the check!')
        else:
            logging.info(f'Data isn\'t empty, sending to {check.__name__}...')
            check(data)
            logging.info('Passed the check!')

    return wrapper


def validator(func):
    def wrapper(*args):
        assert len(args) == 1, f'Internal error: The resulting function of the decorator {__name__} takes exactly one argument'

        data = args[0]

        try:
            func(data)
        except AssertionError as e:
            abort(500, message=str(e))
        except Exception as e:
            abort(500, message=repr(e))
        
        logging.info('Validated!')

        return None

    return wrapper


def check_username(username):
    logging.info('Validating username')
    # Alphanumeric string that may include _ and – having a length of 3 to 16 characters
    assert re.match(r"^[a-z0-9_-]{3,16}$", username), "Username must be alphanumeric, lowercase, between 3 to 16 characters   "


def check_password(password):
    logging.info('Validating password')
    # Alphanumeric without space
    assert re.match(r"^[a-zA-Z0-9]*$", password), "Password must be alphanumeric"


def check_ip(ip):
    logging.info('Validating ip')
    # IPv4 address
    assert re.match(r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$", ip), "Only IPv4 is supported"


def check_datetime(datetime):
    logging.info('Validating datetime')
    # ISO 8601 datetime string no seconds
    assert re.match(r"\d{4}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d", datetime), f"Invalid datetime: ({datetime})"


def check_email(email):
    logging.info('Validating email')
    # Common email Ids
    assert re.match(r"^([a-zA-Z0-9._%-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6})*$", email), 'Invalid email'


def check_name(name):
    logging.info('Validating name')
    assert re.match(r"^[a-zA-Z]*$", name), "Invalid name"


def check_date(date):
    logging.info('Validating date')
    assert re.match("\d{4}-[01]\d-[0-3]\d", date), "Invalid date"


def check_id(id):
    logging.info('Validating id')
    # A positive integer
    assert type(id) == int and id > 0


def check_token(token):
    logging.info('Validating token')
    # Alphanumeric without space
    assert re.match(r"^[a-zA-Z0-9_-]*$", token), "Token must be alphanumeric"


class LoginFormSchema():
    @validator
    def validate(data):
        required(check_username)(data.get('username'))
        required(check_password)(data.get('password'))
        required(check_ip)(data.get('ip'))

    def serialize(data):
        logging.info(f'Serializing the data: {data}')

        if LoginFormSchema.validate(data) != None:
            return None
        
        return {
            'username': data.get('username'),
            'password': data.get('password'),
            'ip': data.get('ip')
        }


class SessionDataSchema():
    @validator
    def validate(data):
        required(check_datetime)(data.get('created_at'))
        required(check_ip)(data.get('ip'))
        required(check_id)(data.get('user_id'))
        required(check_token)(data.get('token'))

    def serialize(data):
        logging.info(f'Serializing the data: {data}')

        if SessionDataSchema.validate(data) != None:
            return None
        
        return {
            'created_at': data.get('created_at'),
            'ip': data.get('ip'),
            'user_id': data.get('user_id'),
            'token': data.get('token')
        }


class TokenDataSchema():
    @validator
    def validate(data):
        required(check_token)(data.get('token'))

    def serialize(data):
        logging.info(f'Serializing the data: {data}')

        if TokenDataSchema.validate(data) != None:
            return None
        
        return {
            'token': data.get('token')
        }


class NewUserDataSchema():
    @validator
    def validate(data):
        required(check_username)(data.get('username'))
        required(check_email)(data.get('email'))
        required(check_password)(data.get('password'))
        optional(check_name)(data.get('firstname'))
        optional(check_name)(data.get('middlename'))
        optional(check_name)(data.get('lastname'))
        optional(check_date)(data.get('birthdate'))
        optional(check_id)(data.get('id'))
    
    def serialize(data):
        logging.info(f'Serializing the data: {data}')

        if NewUserDataSchema.validate(data) != None:
            return None
        
        return {
            'username': data.get('username'),
            'email': data.get('email'),
            'password': data.get('password'),
            'firstname': data.get('firstname'),
            'middlename': data.get('middlename'),
            'lastname': data.get('lastname'),
            'birthdate': data.get('birthdate'),
            'id': data.get('id')
        }


class UserDataSchema():
    @validator
    def validate(data):
        optional(check_username)(data.get('username'))
        optional(check_email)(data.get('email'))
        optional(check_password)(data.get('password'))
        optional(check_name)(data.get('firstname'))
        optional(check_name)(data.get('middlename'))
        optional(check_name)(data.get('lastname'))
        optional(check_date)(data.get('birthdate'))
        optional(check_id)(data.get('id'))
    
    def serialize(data):
        logging.info(f'Serializing the data: {data}')

        if UserDataSchema.validate(data) != None:
            return None
        
        return {
            'username': data.get('username'),
            'email': data.get('email'),
            'password': data.get('password'),
            'firstname': data.get('firstname'),
            'middlename': data.get('middlename'),
            'lastname': data.get('lastname'),
            'birthdate': data.get('birthdate'),
            'id': data.get('id')
        }


class UserDeletionSchema():
    @validator
    def validate(data):
        required(check_token)(data.get('token'))
        required(check_id)(data.get('id'))
    
    def serialize(data):
        logging.info(f'Serializing the data: {data}')

        if UserDeletionSchema.validate(data) != None:
            return None
        
        return {
            'token': data.get('token'),
            'id': data.get('id')
        }


class UserModificationSchema():
    @validator
    def validate(data):
        required(check_token)(data.get('token'))
        optional(check_name)(data.get('firstname'))
        optional(check_name)(data.get('middlename'))
        optional(check_name)(data.get('lastname'))
        optional(check_date)(data.get('birthdate'))
        optional(check_email)(data.get('email'))
        required(check_id)(data.get('id'))
    
    def serialize(data):
        logging.info(f'Serializing the data: {data}')

        if UserModificationSchema.validate(data) != None:
            return None
        
        return {
            'token': data.get('token'),
            'firstname': data.get('firstname'),
            'middlename': data.get('middlename'),
            'lastname': data.get('lastname'),
            'birthdate': data.get('birthdate'),
            'email': data.get('email'),
            'id': data.get('id')
        }
