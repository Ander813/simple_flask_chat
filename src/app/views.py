import json

from flask import (
    Blueprint,
    render_template,
    Response,
    redirect,
    url_for,
    session,
    make_response,
)
from flask_login import login_user, current_user
from sqlalchemy.exc import IntegrityError

from app import socketio_prefix
from app.database import db
from app.decorators import logged_in_redirect, unauthorized_redirect
from app.forms import RegisterForm, LoginForm
from app.models import User, Chat
from app import redis_client


chat = Blueprint("chat", __name__, template_folder="templates")


@chat.route("/", methods=["GET"])
@unauthorized_redirect("chat.login_page")
def index():
    # chat = Chat.query.join(User).filter(User.email.contains(current_user.email)).first()
    return render_template("index.html", current_user=current_user.email)


@chat.route("/chat", methods=["GET"])
@unauthorized_redirect("chat.login_page")
def chat_page():
    chats = Chat.query.filter(User.email == current_user.email).all()
    if chats:
        for chat in chats:
            for i in range(len(chat.users)):
                if chat.users[i].email == current_user.email:
                    del chat.users[i]
                    break

    return render_template(
        "chat.html",
        chats=chats,
        current_user=current_user.email,
    )


@chat.route("/chat/<int:id>", methods=["GET"])
def get_chat(id):
    chat = (
        Chat.query.filter(Chat.id == id, User.email == current_user.email)
        .order_by("id")
        .first()
    )
    message_list = []
    if chat:
        for message in chat.messages:
            message_list.append(message.as_dict())
        return json.dumps(message_list)


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
            resp = make_response(redirect(url_for("chat.index")))
            resp.set_cookie("user", current_user.email)
            return resp
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
            return redirect(url_for("chat.index"))
        except IntegrityError as e:
            return Response("User with such email already exists", 400)
    return render_template("register.html", form=form)
