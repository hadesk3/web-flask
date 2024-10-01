from flask_socketio import emit
from flask import Blueprint,render_template
from . import socketio
chat = Blueprint('chat',__name__)
@chat.route('/chat')
def index():
    return render_template('chat.html')

from flask_socketio import emit
from . import socketio

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('send_message')
def handle_message(data):
    emit('receive_message', data, broadcast=True)
