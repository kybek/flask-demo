import re
import logging

def optional(check):
    logging.info(f'Checking optional field with: {check}')
    
    def wrapper(*args):
        assert(args.count == 1)

        data = args[0]

        if data != None:
            check(data)

    return wrapper


def check_username(username):
    # Alphanumeric string that may include _ and – having a length of 3 to 16 characters
    assert re.match(r"^[a-z0-9_-]{3,16}$", username), "Username must be alphanumeric, lowercase, between 3 to 16 characters   "


def check_password(password):
    # Alphanumeric without space
    assert re.match(r"^[a-zA-Z0-9]*$", password), "Password must be alphanumeric"


def check_ip(ip):
    # IPv4 address
    assert re.match(r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$", ip), "Only IPv4 is supported"


def check_datetime(datetime):
    # ISO 8601 datetime string no seconds
    assert re.match(r"\d{4}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d", datetime), f"Invalid datetime: ({datetime})"


def check_email(email):
    # Common email Ids
    assert re.match(r"^([a-zA-Z0-9._%-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6})*$", email), 'Invalid email'


def check_name(name):
    assert re.match(r"^[a-zA-Z]*$", name), "Invalid name"


def check_date(date):
    assert re.match("\d{4}-[01]\d-[0-3]\d", date), "Invalid date"


def check_id(id):
    # A positive integer
    assert type(id) == int and id > 0


class SessionDataSchema():
    def validate(data):
        try:
            check_username(data.get('username'))
            check_password(data.get('password'))
            check_ip(data.get('ip'))
        except Exception as e:
            return repr(e)
        
        return None

    def prune(data):
        if SessionDataSchema.validate(data) != None:
            return None
        
        return {
            'username': data.get('username'),
            'password': data.get('password'),
            'ip': data.get('ip')
        }


class UserSchema():
    def validate(data):
        try:
            check_username(data.get('username'))
            optional(check_name)(data.get('firstname'))
            optional(check_name)(data.get('middlename'))
            optional(check_name)(data.get('lastname'))
            optional(check_date)(data.get('birthdate'))
            check_email(data.get('email'))
            check_password(data.get('password'))
            optional(check_id)(data.get('id'))
        except Exception as e:
            return repr(e)
        
        return None
    
    def prune(data):
        if UserSchema.validate(data) != None:
            return None
        
        return {
            'username': data.get('username'),
            'firstname': data.get('firstname'),
            'middlename': data.get('middlename'),
            'lastname': data.get('lastname'),
            'birthdate': data.get('birthdate'),
            'email': data.get('email'),
            'password': data.get('password'),
            'id': data.get('id')
        }


class UserDeletionSchema():
    def validate(data):
        try:
            check_id(data.get('id'))

        except Exception as e:
            return repr(e)
        
        return None
    
    def prune(data):
        if UserDeletionSchema.validate(data) != None:
            return None
        
        return {
            'id': data.get('id')
        }


class UserModificationSchema():
    def validate(data):
        try:
            optional(check_username)(data.get('username'))
            optional(check_name)(data.get('firstname'))
            optional(check_name)(data.get('middlename'))
            optional(check_name)(data.get('lastname'))
            optional(check_date)(data.get('birthdate'))
            optional(check_email)(data.get('email'))
            optional(check_password)(data.get('password'))
            check_id(data.get('id'))
        except Exception as e:
            return repr(e)
        
        return None
    
    def prune(data):
        if UserSchema.validate(data) != None:
            return None
        
        return {
            'username': data.get('username'),
            'firstname': data.get('firstname'),
            'middlename': data.get('middlename'),
            'lastname': data.get('lastname'),
            'birthdate': data.get('birthdate'),
            'email': data.get('email'),
            'password': data.get('password'),
            'id': data.get('id')
        }
