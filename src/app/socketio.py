from app import socketio, redis_client
from flask import session, request
from flask_login import current_user
from flask_socketio import emit, join_room, leave_room

from app.database import db
from app.models import Chat, User, Message


socketio_prefix = "socketio"


@socketio.on("pm")
def chat_event_handler(data):
    id = data.get("id")
    sender = User.query.get(email=current_user.email)
    receiver = User.query.get(email=data.get("receiver"))

    if "msg" not in data or not receiver:
        return

    if not id:
        try:
            chat = Chat(chat_type="pm")
            chat.users.append(sender, receiver)
            chat.messages.append(Message(sender.id, data["msg"]))
        except Exception as e:
            return
    else:
        try:
            chat = Chat.query.get(id=data["id"], chat_type="pm")
            chat.messages.append(Message(sender.id, data["msg"]))
        except Exception as e:
            return
    db.session.add(chat)
    db.session.commit()

    sid = redis_client.get(f"{socketio_prefix}:{receiver}")
    emit("response", data["msg"], room=sid)


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
    emails = (
        Chat.query.join(User, Chat.users)
        .with_entities(User.email)
        .filter(Chat.id == room)
        .all()
    )
    if emails:
        message = Message(current_user.id, data["msg"], room)
        db.session.add(message)
        db.session.commit()
        for email in emails:
            sid = redis_client.get(f"{socketio_prefix}:{email.email}")
            if sid:
                sid = sid.decode("utf-8")
                emit("response", data, room=sid)


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
    emit("connected", current_user.email, broadcast=True)


@socketio.on("disconnect")
def on_disconnect():
    """
    Remove user from online list and emit that user disconnected

    :return: None
    """
    del redis_client[f"{socketio_prefix}:{current_user.email}"]
    emit("disconnect", current_user.email, broadcast=True)
