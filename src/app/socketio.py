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
    :param data: dict
    :return: None
    """
    room = data.get("room")
    user = User.query.filter(User.email == session["user"], Chat.id == room).first()
    if user and "msg" in data:
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
