from flask import jsonify
from flaskr.schemas import UserSchema, SessionDataSchema
from dataclasses import dataclass
import datetime as dt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
import logging


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
class OnlineUser(db.Model):
    id: int
    created_at: dt.datetime
    ip: str
    user_id: int

    # https://stackoverflow.com/a/18854791

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime)
    ip = db.Column(db.String(255))
    user_id = db.Column(db.Integer, ForeignKey(User.id), unique=True)

    # user = relationship('User', foreign_keys='OnlineUser.user_id')
    # onlineuser = relationship('User', foreign_keys='OnlineUser.id')

    def serialize(self):
       """Return object data in easily serializable format"""
       return {
            'id': self.id,
            'created_at': self.created_at,
            'ip': self.ip,
            'user_id': self.user_id
       }


def get_user_by_credentials(username, password):
    return User.query.filter_by(username=username, password=password).first()


def get_user_by_id(id):
    return db.get_or_404(User, id)


def get_onlineuser_by_credentials(username, password):
    user = get_user_by_credentials(
        username=session_data_schema.get('username'),
        password=session_data_schema.get('password')
    )

    return OnlineUser.query.filter_by(user_id=user.id).first()


def get_user_model_object_from_schema(user_schema):
    return User(
        id=user_schema.get('id'),
        username=user_schema.get('username'),
        firstname=user_schema.get('firstname'),
        middlename=user_schema.get('middlename'),
        lastname=user_schema.get('lastname'),
        birthdate=user_schema.get('birthdate'),
        email=user_schema.get('email'),
        password=user_schema.get('password')
    )


def get_onlineuser_model_object_from_schema(session_data_schema):
    user = get_user_by_credentials(
        username=session_data_schema.get('username'),
        password=session_data_schema.get('password')
    )

    return OnlineUser(
        id=session_data_schema.get('id'),
        created_at=None,
        ip=session_data_schema.get('ip'),
        user_id=user.id
    )


def insert_onlineuser(session_data_schema):
    onlineuser = get_onlineuser_model_object_from_schema(session_data_schema=session_data_schema)

    db.session.add(onlineuser)
    db.session.commit()


def delete_onlineuser(session_data_schema):
    onlineuser = get_onlineuser_by_credentials(
        username=session_data_schema.get('username'),
        password=session_data_schema.get('password')
    )

    db.session.delete(onlineuser)
    db.session.commit()


def insert_user(user_schema):
    user = get_user_model_object_from_schema(user_schema)

    db.session.add(user)
    db.session.commit()


def delete_user(user_schema):
    user = get_user_by_id(user_schema.get('id'))

    db.session.delete(user)
    db.session.commit()


def modify_user(user_schema):
    user = get_user_by_id(user_schema.get('id'))

    db.session.query(User).\
        filter(User.id == user_schema.get('id')).\
        update(user_schema)


def list_users():
    users = User.query.all()
    return [x.serialize() for x in users]


def list_onlineusers():
    onlineusers = OnlineUser.query.all()
    return [x.serialize() for x in onlineusers]
