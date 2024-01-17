from flask import Flask, request
from flask_restful import Resource, Api, abort
from flaskr.schemas import SessionDataSchema, UserSchema, UserDeletionSchema, UserModificationSchema
import flaskr.db as db
import logging


def create_new_id():
    return 1


def user_exists(username):
    result = db.select_user(username)

    if result == None:
        return False
    
    return True


def abort_if_cant_authenticate_user(username, password):
    if user_exists(username=username) == False:
        abort(401, message='Wrong username')
    
    result = db.select_user_pass(username, password)

    if result == None:
        abort(401, message='Wrong password')


def modify_user(user_modification):
    db.modify_user(user_modification)


def abort_if_cant_validate(data, schema):
    validation_result = schema.validate(data)

    if validation_result != None:
        abort(404, message=str(validation_result))


def login(session_data):
    abort_if_cant_validate(session_data, SessionDataSchema)

    abort_if_cant_authenticate_user(username=username, password=password)

    db.insert_onlineuser(SessionDataSchema.prune(session_data))


def logout(session_data):
    abort_if_cant_validate(session_data, SessionDataSchema)

    abort_if_cant_authenticate_user(SessionDataSchema.prune(session_data))

    db.delete_onlineuser(username=username)


def create_user(user):
    user = user | {'id': create_new_id()}

    abort_if_cant_validate(user, UserSchema)
    
    db.insert_user(UserSchema.prune(user))


def delete_user(user_deletion):
    abort_if_cant_validate(user_deletion, UserDeletionSchema)
    
    db.delete_user(UserDeletionSchema.prune(user_deletion))


def update_user(user_modification):
    abort_if_cant_validate(user_modification, UserModificationSchema)

    db.modify_user(UserModificationSchema.prune(user_modification))


def list_users():
    return db.list_users()


def list_onlineusers():
    return db.list_onlineusers()
