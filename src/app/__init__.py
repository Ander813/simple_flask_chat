from flask import Flask
from flask_login import LoginManager

from . import views


app = Flask(__name__)
app.config.from_object("conf.conf.Config")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.register_blueprint(views.chat)

manager = LoginManager(app)
from app import models


@manager.user_loader
def load_user(user_id):
    return models.User.query.get(user_id)
