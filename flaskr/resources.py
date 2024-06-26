from flask import Flask, request
from flask_restful import Resource, Api
from flaskr.backend import login, logout, create_user, delete_user, modify_user, list_users, list_onlineusers
from time import gmtime, strftime
import logging

def get_current_datetime_string():
    return strftime("%Y-%m-%dT%H:%M:%S", gmtime())


class Login(Resource):
    def post(self):
        logging.info(f'POST /login: {request.form}')

        result = login(dict(request.form) | {
            'ip': request.remote_addr
        })

        logging.info(f'Responding with the token: {result}')
        return result, 200


class Logout(Resource):
    def post(self):
        logging.info(f'POST /logout: {request.form}')

        result = logout(dict(request.form))

        return '', 204


class UserList(Resource):
    def get(self):
        logging.info(f'GET /user/list: {request.form}')

        return list_users(), 200


class UserCreate(Resource):
    def post(self):
        logging.info(f'POST /user/create: {request.form}')

        create_user(dict(request.form))

        return '', 204


class UserDelete(Resource):
    def post(self, id):
        logging.info(f'POST /user/delete: {request.form}')

        delete_user(dict(request.form) | {
            'id': id
        })

        return '', 204


class UserUpdate(Resource):
    def post(self, id):
        logging.info(f'POST /user/update: {request.form}')

        modify_user(dict(request.form) | {
            'id': id
        })

        return '', 204


class OnlineUsers(Resource):
    def get(self):
        logging.info(f'GET /onlineusers: {request.form}')

        result = list_onlineusers()

        return result, 200
