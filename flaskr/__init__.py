from flask import Flask
from flask_restful import Api
from flaskr.resources import Login, Logout, UserList, UserCreate, UserDelete, UserUpdate, OnlineUsers
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import logging

logging.basicConfig(level=logging.DEBUG)

logging.info('Initializing app...')

app = Flask(import_name=__name__)
api = Api(app)

logging.info('Initializing database connection...')

username='postgres'
password='labris123!'

# Define the PostgreSQL URL
postgresql_url = 'postgresql://{username}:{password}@localhost:5432/mydatabase'

app.config['SQLALCHEMY_DATABASE_URI'] = postgresql_url

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

db.init(app)

logging.info('Connecting API routes...')

api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(UserList, '/user/list')
api.add_resource(UserCreate, '/user/create')
api.add_resource(UserDelete, '/user/delete/<int:id>')
api.add_resource(UserUpdate, '/user/update/<int:id>')
api.add_resource(OnlineUsers, '/onlineusers')

logging.info('Server ready!')
