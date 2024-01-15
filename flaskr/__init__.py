import os

from flask import Flask, current_app

def create_app():
    app = Flask(import_name=__name__)
    
    @app.route('/')
    def main():
        return 'MAIN'

    @app.route('/login')
    def login():
        return ''
    
    @app.route('/logout')
    def logout():
        return ''
    
    @app.route('/user/list')
    def user_list():
        return ''
    
    @app.route('/user/create')
    def user_create():
        return ''
    
    @app.route('/user/delete/<int:id>')
    def user_delete(id):
        return ''
    
    @app.route('/user/update/<int:id>')
    def user_update(id):
        return ''

    @app.route('/onlineusers')
    def onlineusers():
        return ''

    return app

"""
/login
/logout
/user/list
/user/create
/user/delete/{id}
/user/update/{id}
/onlineusers
"""