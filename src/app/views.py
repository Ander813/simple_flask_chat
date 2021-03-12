from flask import (
    Blueprint,
    render_template,
    Response,
    redirect,
    url_for,
    session,
)
from flask_login import login_user, current_user
from sqlalchemy.exc import IntegrityError

from src.app import socketio_prefix
from src.app.database import db
from src.app.decorators import logged_in_redirect, unauthorized_redirect
from src.app.forms import RegisterForm, LoginForm
from src.app.models import User, Chat
from app import redis_client


chat = Blueprint("chat", __name__, template_folder="templates")


@chat.route("/", methods=["GET"])
@unauthorized_redirect("chat.login_page")
def index():
    return render_template("index.html")


@chat.route("/<int:room>", methods=["GET"])
@unauthorized_redirect("chat.login_page")
def chat_page(room):
    chat = Chat.query.filter(Chat.id == room, User.email == current_user.email).first()
    if Chat.query.filter(Chat.id == room, User.email == current_user.email).first():
        return render_template("chat.html", messages=chat.messages, users=chat.users)
    return redirect(url_for("chat.index"))


@chat.route("/online", methods=["GET"])
def get_online_users():
    users_online = []
    for key in redis_client.scan_iter(f"{socketio_prefix}:*"):
        users_online.append(key.decode().split(":")[-1])
    return {"online": users_online}


@chat.route("/login", methods=["GET", "POST"])
@logged_in_redirect("chat.index")
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        try:
            assert user.check_password(form.password.data)
            login_user(user)
            session["user"] = user.email
            return redirect(url_for("chat.index"))
        except (AttributeError, AssertionError):
            return Response("Invalid credentials", status=401)
    return render_template("login.html", form=form)


@chat.route("/register", methods=["GET", "POST"])
@logged_in_redirect("chat.index")
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            db.session.add(User(email=form.email.data, password=form.password1.data))
            db.session.commit()
        except IntegrityError as e:
            return Response("User with such email already exists", 400)
    return render_template("register.html", form=form)
