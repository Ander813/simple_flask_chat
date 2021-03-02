from app import socketio
from flask import session, request
from flask_socketio import emit, join_room, leave_room

from .database import db
from app.models import Chat, User


@socketio.on("event")
def chat_event_handler(json):
    """
    :param json: json
    :return: None
    """
    room = json.get("room")
    user = User.query.filter(User.email == session["user"], Chat.id == room)
    if user and "msg" in json:
        emit("response", json, room=room)


@socketio.on("join")
def on_join(json):
    room = json.get("room")
    user = session.get("user")
    if room and user:
        join_room(room, sid=user)


@socketio.on("leave")
def on_leave(json):
    room = json.get("room")
    user = session.get("user")
    if room and user:
        leave_room(room)
