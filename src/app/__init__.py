from flask import Flask
from flask_login import LoginManager
from flask_socketio import SocketIO


app = Flask(__name__)
app.config.from_object("conf.conf.Config")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


manager = LoginManager(app)
from app import models


socketio = SocketIO(app)


from . import views

app.register_blueprint(views.chat)


@manager.user_loader
def load_user(user_id):
    return models.User.query.get(user_id)
