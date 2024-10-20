from flask import Blueprint, render_template, request,redirect
from flask_socketio import join_room, leave_room, send
from flask_login import current_user
from .models import Customer, Role
from . import socketio
chat = Blueprint("chat",__name__)

customer_rooms = {}
@chat.route('/chat',methods = ['GET','POST'])
def handle_chat():
    if request.method == 'GET':
        customer = Customer.query.get(current_user.id)
        name = customer.gmail
        roles = []
        for role in customer.roles:
            roles.append(role.name)
        if 'ADMIN' in roles:
            role = 'ADMIN'
        else:
            role = 'CUSTOMER'
        return render_template('chat.html',name = name, role = role)
    else:
        return redirect(request.referrer)
@socketio.on('join')
def handle_join(data):
    name = data['name']
    role = data['role']
    if role == 'CUSTOMER':
        room = name
        customer_rooms['name'] = room 
    else:
        room = data['room']
    join_room(room)
    send(f"{name} has joined the room {room}.", to=room)

@socketio.on('message')
def handle_mess(data):
    room = data['room']
    msg = data['msg']
    send(msg,to=room)

@socketio.on('leave')
def handle_leave(data):
    room = data['room']
    username = data['name']
    leave_room(room)
    send(f"{username} has left the room {room}.", to=room)
