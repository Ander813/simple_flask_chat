from app import socketio, redis_client
from flask import session, request
from flask_login import current_user
from flask_socketio import emit, join_room, leave_room

from src.app.database import db
from src.app.models import Chat, User, Message


socketio_prefix = "socketio"


@socketio.on("event")
def chat_event_handler(data):
    """
    If room is not given in data, creates new chat with sender and receiver.
    If room id is given, checks if user in chat and sends
    :param data: dict
    :return: None
    """
    if "msg" not in data:
        return

    room = data.get("room")
    if not room:
        message_to = data.get("receiver")
        if message_to:
            receiver = User.query.filter_by(email=message_to)
            sender = User.query.filter_by(email=current_user.email)
            message = Message(sender.id, data["msg"], room)
            chat = Chat()

            db.session.add(chat)
            chat.users.append(receiver, sender)
            chat.messages.append(message)

            db.session.commit()

            emit("response", data["msg"], room=redis_client[receiver.email])
            return

    user = User.query.filter(User.email == session["user"], Chat.id == room).first()
    if user:
        message = Message(user.id, data["msg"], room)
        db.session.add(message)
        db.session.commit()
        emit("response", data, room=room)


@socketio.on("join")
def on_join(json):
    room = json.get("room")
    user = session.get("user")
    if room and user:
        join_room(room)


@socketio.on("leave")
def on_leave(json):
    room = json.get("room")
    user = session.get("user")
    if room and user:
        leave_room(room)


@socketio.on("connect")
def on_connect():
    """
    Add user to online list on connect and emit that user connected

    :return: None
    """
    redis_client[f"{socketio_prefix}:{current_user.email}"] = request.sid
    emit("connected", current_user.email)


@socketio.on("disconnect")
def on_disconnect():
    """
    Remove user from online list and emit that user disconnected

    :return: None
    """
    del redis_client[f"{socketio_prefix}:{current_user.email}"]
    emit("disconnect", current_user.email)
