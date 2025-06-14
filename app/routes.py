from flask import Blueprint, render_template
from flask_socketio import SocketIO, emit
import threading
import random
import time
# from .extensions import socketio


main = Blueprint('main', __name__)



@main.route('/')
def index():
    return render_template('index.html')


@main.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@main.route('/servers')
def servers():
    return render_template('servers.html')




    
# @main.route('/')
# def home():
#     return "Hello, Factory Pattern!"


# @main.route('/home')
# def index():
#     users = User.query.all()
#     if not users:
#         return 'No users found'

#     result = ''
#     for user in users:
#         result += f'Username: {user.username} <br> Email: {user.email}<br><br>'
#     return result