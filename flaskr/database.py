from flask import jsonify
from flaskr.schemas import UserDataSchema, SessionDataSchema, NewUserDataSchema
from dataclasses import dataclass
import datetime as dt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, TIMESTAMP
from sqlalchemy.sql import text
import logging
import datetime as dt

logging.info('Creating db instance...')

db = SQLAlchemy()

logging.info('Finished creating db instance!')

@dataclass
class User(db.Model):
    id: int
    username: str
    firstname: str
    middlename: str
    lastname: str
    birthdate: str
    email: str
    password: str

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    firstname = db.Column(db.String(255))
    middlename = db.Column(db.String(255))
    lastname = db.Column(db.String(255))
    birthdate = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))

    def serialize(self):
       """Return object data in easily serializable format"""
       return {
            'id': self.id,
            'username': self.username,
            'firstname': self.firstname,
            'middlename': self.middlename,
            'lastname': self.lastname,
            'birthdate': self.birthdate,
            'email': self.email,
            'password': self.password
       }


@dataclass
class Session(db.Model):
    id: int
    created_at: dt.datetime
    ip: str
    user_id: int
    token: str

    # https://stackoverflow.com/a/18854791

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(TIMESTAMP)
    ip = db.Column(db.String(255))
    user_id = db.Column(db.Integer, ForeignKey(User.id), unique=True)
    token = db.Column(db.String(255))


    def serialize(self):
       """Return object data in easily serializable format"""
       logging.info(f'Serializing {type(self).__name__} object: {self.__dict__}')

       return {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'ip': self.ip,
            'user_id': self.user_id,
            'token': self.token
       }
    
    def join_and_serialize(self):
        logging.info(f'Joining {type(self).__name__} with {User.__name__} using {self.user_id}')
        result = get_user_by_id(self.user_id)

        if result == None:
            return None
        else:
            user = result.serialize()

            return self.serialize() | {
                'username': user.get('username')
            }


def delete_empty_fields(data):
    return {k: v for k, v in data.items() if v}


def get_user_by_credentials(username, password):
    logging.info(f'Database select user with username={username}, password={password}...')
    result = User.query.filter_by(username=username, password=password).first()
    logging.info(f'Result: {str(result)}')

    return result


def get_user_by_id(id):
    logging.info(f'Database select user with id={id}')
    result = User.query.filter_by(id=id).first()
    logging.info(f'Result: {str(result)}')

    return result


def get_user_by_username(username):
    return User.query.filter_by(username=username).first()


def get_session_by_credentials(username, password):
    user = get_user_by_credentials(
        username=username,
        password=password
    )

    return Session.query.filter_by(user_id=user.id).first()


def get_session_by_token(token):
    return Session.query.filter_by(token=token).first()


def get_user_model_object_from_schema(user_data):
    return User(
        id=user_data.get('id'),
        username=user_data.get('username'),
        firstname=user_data.get('firstname'),
        middlename=user_data.get('middlename'),
        lastname=user_data.get('lastname'),
        birthdate=user_data.get('birthdate'),
        email=user_data.get('email'),
        password=user_data.get('password')
    )


def get_session_model_object_from_schema(session_data):
    return Session(
        id=session_data.get('id'),
        created_at=session_data.get('created_at'),
        ip=session_data.get('ip'),
        user_id=session_data.get('user_id'),
        token=session_data.get('token')
    )


def insert_session(session_data):
    logging.info(f'Inserting session data to database: {session_data}')
    session = get_session_model_object_from_schema(session_data=session_data)

    db.session.add(session)
    db.session.commit()


def delete_session(token):
    session = get_session_by_token(
        token=token
    )

    db.session.delete(session)
    db.session.commit()


def insert_user(user_data):
    user = get_user_model_object_from_schema(user_data)

    db.session.add(user)
    db.session.commit()


def delete_user(id):
    user = get_user_by_id(id)

    db.session.delete(user)
    db.session.commit()


def modify_user(user_data):
    user = get_user_by_id(user_data.get('id'))

    user_data = delete_empty_fields(user_data)

    db.session.query(User).\
        filter(User.id == user_data.get('id')).\
        update(user_data)

    db.session.commit()


def list_users():
    users = User.query.all()
    return [x.serialize() for x in users]


def list_sessions():
    sessions = Session.query.\
        all()
    
    result = [x.join_and_serialize() for x in sessions]

    
    if result != None and None in result:
        logging.info('Removing nulls from result...')
        result.remove(None)

    return result


def select_user_with_username(username):
    return db.session.query(User).\
        filter(User.username == username).\
        first().\
        serialize()
