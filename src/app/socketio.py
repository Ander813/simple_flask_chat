from app import socketio
from flask import session, request
from flask_socketio import emit, join_room, leave_room


@socketio.on("event")
def chat_event_handler(json):
    """
    :param json: json
    :return: None
    """
    room = request.args.get("room", None)
    if room and "msg" in json:
        print(json, session["user"])
        emit("response", json)


@socketio.on("join")
def on_join(json):
    room = request.args.get("room", None)
    join_room(room)


@socketio.on("leave")
def on_leave(json):
    room = request.args.get("room", None)
    leave_room(room)
