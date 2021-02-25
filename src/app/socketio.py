from app import socketio
from flask_socketio import emit


@socketio.on("event")
def chat_event_handler(json):
    """
    :param json: json
    :return: None
    """
    print(json)
    emit("response", json)
