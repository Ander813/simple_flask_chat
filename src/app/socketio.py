from app import socketio, redis_client
from flask import request
from flask_login import current_user
from flask_socketio import emit

from app.database import db
from app.models import Chat, User, Message


socketio_prefix = "socketio"


@socketio.on("pm")
def chat_event_handler(data):
    if "msg" not in data:
        return
    id = data.get("id")
    sender = User.query.filter_by(email=current_user.email).first()

    if not id:
        try:
            receiver = User.query.filter_by(email=data["receiver"]).first()
        except KeyError:
            return

    try:
        chat = Chat.query.filter_by(id=data["id"], chat_type="pm").first()
        emails_query = (
            Chat.query.join(User, Chat.users)
            .with_entities(User.email)
            .filter(Chat.id == data["id"])
            .all()
        )
        emails = [email.email for email in emails_query]
        chat.messages.append(Message(sender.id, data["msg"]))
    except KeyError:
        chat = Chat(chat_type="pm")
        chat.users.append(sender, receiver)
        emails = [sender.email.receiver.email]
        chat.messages.append(Message(sender.id, data["msg"]))
    else:
        db.session.add(chat)
        db.session.commit()

    for email in emails:
        sid = redis_client.get(f"{socketio_prefix}:{email}")
        if sid:
            sid = sid.decode("utf-8")
            emit("response", data, to=sid)


@socketio.on("disc")
def chat_event_handler(data):
    if "msg" not in data or "room" not in data:
        return

    room = data["room"]
    emails_query = (
        Chat.query.join(User, Chat.users)
        .with_entities(User.email)
        .filter(Chat.id == room)
        .all()
    )
    if emails_query:
        message = Message(current_user.id, data["msg"], room)
        db.session.add(message)
        db.session.commit()
        for email_obj in emails_query:
            sid = redis_client.get(f"{socketio_prefix}:{email_obj.email}")
            if sid:
                sid = sid.decode("utf-8")
                emit("response", data, to=sid)


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
    print("disc")
    del redis_client[f"{socketio_prefix}:{current_user.email}"]
    emit("disconnect", current_user.email, broadcast=True)
