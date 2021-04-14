from app import socketio, redis_client
from flask import request
from flask_login import current_user
from flask_socketio import emit

from app.database import db
from app.models import Chat, User, Message


socketio_prefix = "socketio"
prevent_disconnect = set()


@socketio.on("pm")
def chat_event_handler(data):
    if "text" not in data:
        return

    sender = User.query.filter_by(email=current_user.email).first()

    try:
        chat = Chat.query.filter_by(id=data["id"], chat_type="pm").first()
        emails_query = (
            Chat.query.join(User, Chat.users)
            .with_entities(User.email)
            .filter(Chat.id == data["id"])
            .all()
        )
        emails = [email.email for email in emails_query]
        message = Message(sender.id, data["text"])
        chat.messages.append(message)
    except KeyError:
        receiver = User.query.filter_by(email=data["receiver"]).first()
        chat = Chat(chat_type="pm")
        chat.users.append(sender, receiver)
        emails = [sender.email, receiver.email]
        message = Message(sender.id, data["text"])
        chat.messages.append(message)
    else:
        db.session.add(chat)
        db.session.commit()

    data.update({"sent": str(message.sent)})
    for email in emails:
        sid = redis_client.get(f"{socketio_prefix}:{email}")
        if sid:
            sid = sid.decode("utf-8")
            emit("response", data, to=sid)


@socketio.on("disc")
def chat_event_handler(data):
    if "text" not in data or "room" not in data:
        return

    room = data["room"]
    emails_query = (
        Chat.query.join(User, Chat.users)
        .with_entities(User.email)
        .filter(Chat.id == room)
        .all()
    )
    if emails_query:
        message = Message(current_user.id, data["text"], room)
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
    if redis_client.get(f"{socketio_prefix}:{current_user.email}") is not None:
        prevent_disconnect.add(current_user.email)

    redis_client[f"{socketio_prefix}:{current_user.email}"] = request.sid
    emit("connected", current_user.email, broadcast=True)


@socketio.on("disconnect")
def on_disconnect():
    """
    Remove user from online list and emit that user disconnected

    :return: None
    """
    if current_user.email not in prevent_disconnect:
        del redis_client[f"{socketio_prefix}:{current_user.email}"]
        emit("disconnected", current_user.email, broadcast=True)
    else:
        prevent_disconnect.remove(current_user.email)
